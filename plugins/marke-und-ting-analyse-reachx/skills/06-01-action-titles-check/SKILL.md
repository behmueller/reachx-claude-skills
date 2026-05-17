---
name: 06-01-action-titles-check
description: Bewertet und verbessert Action Titles in Google Slides nach dem Pyramidalprinzip (Minto). Output ist ein gestyltes HTML-Dokument im REACHX-Branding plus optionale Slides-Kommentare. Nutze diesen Skill, sobald der Nutzer eine Google-Slides-URL oder Presentation-ID nennt und nach Action Titles, Folientiteln, Headlines, Pyramid Principle, MECE oder Minto fragt — auch wenn nur "Titel prüfen", "Headlines bewerten", "Folien-Überschriften optimieren", "Deck-Review", oder "sind die Titel gut?" gesagt wird. Auch dann nutzen, wenn der Nutzer ein Strategie-Deck-Review wünscht und sich auf die Titel konzentriert. Setzt eine installierte und authentifizierte gws-CLI voraus (Google Workspace CLI). NICHT nutzen für PPTX-Dateien (dort den eingebauten PPTX-Skill verwenden) oder für allgemeines Folien-Review jenseits der Titel.
---

# Action Titles Check (Pyramidalprinzip)

Reviewt die Action Titles eines Google-Slides-Decks und pflegt freigegebene Vorschläge als verankerte Kommentare ein. Originale Titel bleiben unverändert — die Vorschläge erscheinen im Slides-Kommentar-Panel und können dort vom Empfänger selektiv übernommen werden.

Output ist eine HTML-Datei im REACHX-Styling (Schrift Red Hat Display/Text, Sunrise-Red als Akzent) mit Executive Summary, sortierter Bewertungstabelle pro Folie, klappbaren Detail-Reviews und Standalone-Test-Verdikt. Im Chat zusätzlich eine Kurzfassung mit Pfad zur HTML-Datei.

Methodik und Bewertungskriterien stehen ausführlich in `reference/methodology.md` — lies diese Datei *vor* dem Schreiben des Berichts in Schritt 5. Das HTML-Template steht in `reference/report-template.html` — dieses wird in Schritt 6 mit Inhalten gefüllt.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="<name-dieses-skills>"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Report-Render zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Voraussetzungen

- `gws` ist installiert und authentifiziert. Schlägt ein Aufruf mit Auth-Fehler (Exit-Code 2) fehl, weise den Nutzer auf einmaliges `gws auth login` hin.
- Für das Einpflegen von Kommentaren braucht der Nutzer Kommentar-Rechte am Deck (kommt mit Edit- oder Kommentator-Rolle).

## Schritt 0 — MTA-Kontext laden (optional, Dual-Mode)

Dieser Skill kann in zwei Modi laufen:

1. **MTA-Modus**: Wenn der Nutzer den Skill im Kontext einer laufenden MTA aufruft und die MTA im lokalen Active-MTA-Cache registriert ist, wird der HTML-Report nach Drive in den `reports/`-Sub-Folder der aktiven MTA hochgeladen und `status.md` aktualisiert.
2. **Standalone-Modus**: Wenn keine MTA aktiv ist (oder der Skill bewusst standalone aufgerufen wird), schreibt der Skill den HTML-Report lokal ins Working Directory — wie bisher.

Erkennungs-Logik am Skill-Anfang:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_MODE=false
if [ -n "<slug>" ] && [ -f "$DRIVE_PY" ]; then
  MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>" 2>/dev/null)
  if [ -n "$MTA_JSON" ]; then
    MTA_MODE=true
    FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
    META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
    python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
    REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
  fi
fi
```

Wenn der Nutzer keinen MTA-Slug nennt und auch keiner aktiv im Cache ist: Standalone-Modus, kein Hard-Abbruch — der Skill funktioniert dann wie ein generisches Deck-QA-Tool.

Das Slides-Lesen (Schritte 1-4) und die Bewertung (Schritte 5-7) sind in beiden Modi identisch — die Slides-API ist unabhängig von der MTA-Migration.

## Schritt 1 — Presentation-ID bestimmen

Akzeptiere als Input eine vollständige Slides-URL oder eine reine ID. Aus einer URL wie `https://docs.google.com/presentation/d/<ID>/edit#...` extrahiere `<ID>` zwischen `/d/` und dem nächsten `/`. Wurde nichts mitgegeben, frage explizit nach URL oder ID, bevor Du fortfährst.

## Schritt 2 — Deck einlesen

Fordere nur die für das Review notwendigen Felder an:

```bash
gws slides presentations get --params '{
  "presentationId": "<ID>",
  "fields": "slides(objectId,pageElements(objectId,shape(placeholder,text)),slideProperties(notesPage(pageElements(shape(placeholder,text)))))"
}' > /tmp/atc-deck.json 2>&1
```

**Wichtig**: Die `gws`-CLI druckt vor der eigentlichen JSON-Antwort die Zeile `Using keyring backend: keyring` auf stdout. Bevor Du die Datei mit einem JSON-Parser einliest, strippe die erste Zeile, falls sie nicht mit `{` beginnt:

```bash
head -1 /tmp/atc-deck.json | grep -qv "^{" && sed -i '' '1d' /tmp/atc-deck.json
```

Schlägt der Aufruf mit `accessNotConfigured` fehl, ist die Slides-API im GCP-Projekt nicht aktiviert — gib den Aktivierungs-Hinweis aus der gws-Stderr unverändert an den Nutzer weiter.

## Schritt 3 — Pro Folie extrahieren

Sammle aus der JSON-Antwort für jede Folie folgende Felder:

- **Folien-Index** — beginnend bei 1, in der Reihenfolge des `slides`-Arrays.
- **Folien-ObjectId** — `slide.objectId`. Wird für den Kommentar-Anchor in Schritt 9 benötigt.
- **Titel-Text** — Text aus dem `pageElement` mit `shape.placeholder.type === "TITLE"` oder `"CENTERED_TITLE"`. Der Text liegt in `shape.text.textElements[*].textRun.content` (zusammenhängen, Whitespace trimmen).
- **Body-Text** — alle anderen Text-tragenden Shapes (`placeholder.type` `BODY`, `SUBTITLE` oder Shapes ohne Placeholder). Konkateniere zu einem String pro Folie.
- **Speaker Notes** — aus `slide.slideProperties.notesPage.pageElements[*]` das Shape mit `placeholder.type === "BODY"`. Notes geben oft die intendierte Aussage preis und sind essenziell für gute Vorschläge.

**Statement-Folien erkennen**: Folien ohne TITLE-Placeholder, deren gesamter Folientext eine zusammenhängende Aussage trägt (typisch: ein bis drei Sätze als kompletter Folieninhalt, kein zusätzlicher Body-Block). Diese werden mitbewertet — Methodik-Sonderregel siehe `reference/methodology.md`.

## Schritt 4 — Sonderfolien erkennen und überspringen

Nur folgende drei Folientypen NICHT bewerten, sondern markieren:

- **Cover-Folie** (typischerweise erste Folie mit Deck-Titel + Untertitel + Datum): überspringen.
- **Agenda-/Inhalt-Folien** (Titel ist "Agenda", "Inhalt", "Inhaltsverzeichnis", "Übersicht"): überspringen.
- **Section Divider** (Folie mit nur Sektions-Nummer und -Name, z. B. "01. Markenanalyse", oder reine Zwischenüberschrift ohne Body): überspringen.

**Anhang-Folien** mit numerischer Strukturlogik (z. B. "1.1 Markenname", "1.6 Visuelle Markenidentität — Bildwelt") werden *strikt mitbewertet*. Die Methodik gilt dort unverändert.

## Schritt 5 — Methodik laden

Lies *jetzt* `reference/methodology.md` vollständig. Die Datei enthält die fünf Bewertungskriterien, die Bewertungsskala, die Sonderregel für Statement-Folien und Beispielbewertungen, die als Kalibrierung dienen.

## Schritt 6 — HTML-Bericht generieren

**Validierung — Pflicht:** Den fertigen Report vor dem Upload prüfen: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad>` (ohne `--shell`, da dieser Skill ein eigenes Template `reference/report-template.html` nutzt). Exit-Code 0 → ausliefern. Exit-Code 1 → nicht ausliefern, korrigieren, erneut validieren. Keine CSS-Klassen verwenden, die nicht im `<style>`-Block des Templates definiert sind.

Lies `reference/report-template.html`. Das Template enthält Platzhalter in der Form `{{TOKEN}}`, die Du durch die Inhalte aus den vorherigen Schritten ersetzt.

### Bewertungen sammeln

Für jede bewertete Folie (Sonderfolien aus Schritt 4 ausgenommen) sammle:

- **Folien-Index**, **Folien-ObjectId**
- **Aktueller Titel** (oder "Kein Titel" wenn leer)
- **Bewertung**: Stark / Verbesserungswürdig / Schwach
- **Vorschlag**: vollständiger Satz, max. ~120 Zeichen (bei Stark: leer)
- **Begründung**: 2–3 Sätze, welche Kriterien erfüllt/verfehlt sind, mit Bezug auf Body und Notes (bei Stark: ein Satz, was die Folie gut macht)
- **Body-Snippet** (1–2 Sätze, falls für Kontext relevant)
- **Notes-Snippet** (1–2 Sätze, falls die Speaker Notes die Aussage präzisieren)

Wichtig: Nutze die Speaker Notes aktiv. Oft steht dort die intendierte Aussage, die der sichtbare Titel nicht trifft. Dann ist der Vorschlag häufig eine Verdichtung der Speaker Notes.

### Output-Pfad bestimmen

- **Kunden-Slug**: aus dem Cover-Folientitel (Folie 1) extrahieren — Kleinbuchstaben, Sonderzeichen entfernen, Leerzeichen durch `-` ersetzen. Im MTA-Modus alternativ aus `meta.json.kunden_slug`.
- **Datum**: heutiges Datum im Format `YYYY-MM-DD`.
- **Dateiname**: `deck-qa-action-titles-{kunden-slug}-{datum}.html`
- **Speicherort**:
  - **MTA-Modus**: Datei wird lokal nach `/tmp/<filename>` gerendert und dann via `python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "<filename>" "/tmp/<filename>" "text/html"` nach Drive in den `reports/`-Sub-Folder der aktiven MTA hochgeladen.
  - **Standalone-Modus**: Datei wird ins aktuelle Working Directory geschrieben (Fallback `/tmp/` wenn nicht beschreibbar) — wie bisher.

### Platzhalter ersetzen

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | `Action-Titles-Check — {Kundenname}-Deck` |
| `{{EYEBROW}}` | `Action-Titles-Check · Pyramidalprinzip (Minto)` |
| `{{DISPLAY_NAME}}` | `{Kundenname}-Deck` |
| `{{REPORT_DATE}}` | Heutiges Datum, Format `YYYY-MM-DD` |
| `{{DECK_DATE_SUFFIX}}` | Wenn Deck-Datum erkennbar: ` · Deck-Datum: {Datum}`, sonst leer |
| `{{DECK_URL}}` | `https://docs.google.com/presentation/d/{ID}/edit` |
| `{{EXEC_SUMMARY}}` | Ein oder mehrere `<p>`-Elemente: 3–5 Sätze. Verteilung der Bewertungen, wiederkehrende Muster, knappes Verdikt zum Standalone-Test. |
| `{{COUNT_TOTAL}}` | Anzahl bewerteter Folien (ohne Sonderfolien) |
| `{{COUNT_STARK}}` / `{{COUNT_MITTEL}}` / `{{COUNT_SCHWACH}}` | Zählungen pro Bewertung |
| `{{COUNT_SKIPPED}}` | Anzahl übersprungener Sonderfolien (Cover, Agenda, Section Divider) |
| `{{RATINGS_ROWS}}` | Eine `<tr>`-Zeile pro Folie. Format siehe unten. |
| `{{SLIDE_DETAILS}}` | Ein `<details class="slide">`-Block pro Folie. Format siehe unten. |
| `{{STANDALONE_TEST}}` | HTML-Block mit Standalone-Test (siehe unten) |
| `{{FOOTER_TEXT}}` | `Action-Titles-Check Skill v1.0 · Bericht erstellt automatisiert auf Basis von <a href="{DECK_URL}" target="_blank" rel="noopener">Original-Deck</a>. Die Originale-Titel bleiben unverändert.` |

### Format der Bewertungstabellen-Zeilen (`{{RATINGS_ROWS}}`)

Bei großen Decks (> 50 Folien) gruppiere die Tabelle nach Sektionen — füge vor jedem Sektions-Block eine `<tr class="section-row">`-Zeile ein:

```html
<tr class="section-row"><td colspan="4">{Sektions-Name oder Section-Divider-Titel}</td></tr>
```

Pro bewerteter Folie:

```html
<tr>
  <td class="col-folie">{N}</td>
  <td class="col-bewertung"><span class="badge {bewertungs-klasse}">{Bewertungs-Label}</span></td>
  <td class="col-titel">{aktueller Titel — bei Statement-Folien ggf. mit „…" gekürzt und Markierung „(Statement-Folie)"}</td>
  <td class="col-vorschlag">{Vorschlag oder „—" bei Stark}</td>
</tr>
```

Mapping Bewertung → CSS-Klasse:
- "Stark" → `badge stark`
- "Verbesserungswürdig" → `badge mittel`
- "Schwach" → `badge schwach`

Sonderfolien (Cover, Agenda, Section Divider) erscheinen NICHT in der Tabelle — sie tauchen nur im `{{COUNT_SKIPPED}}`-Counter auf.

### Format der Detail-Blöcke (`{{SLIDE_DETAILS}}`)

Pro bewerteter Folie ein Block:

```html
<details class="slide" data-rating="{rating-key}"{open_attr}>
  <summary>
    <span class="slide-num">Folie {N}</span>
    <span class="badge {bewertungs-klasse}">{Bewertungs-Label}</span>
    <span class="slide-title-current">"{aktueller Titel oder 'Kein Titel'}"</span>
  </summary>
  <div class="body">
    <h4>Bewertung &amp; Begründung</h4>
    <p>{2–4 Sätze. Welche der fünf Kriterien erfüllt oder verfehlt? Bezug auf Body / Notes wenn relevant.}</p>

    <h4>Folien-Kontext</h4>
    <div class="quote-block">
      <span class="quote-label">Body</span>
      {Body-Snippet, max. 200 Zeichen, mit „…" gekürzt}
    </div>
    <div class="quote-block">
      <span class="quote-label">Speaker Notes</span>
      {Notes-Snippet, max. 200 Zeichen, mit „…" gekürzt}
    </div>

    <h4>Vorschlag</h4>
    <div class="suggestion">
      <div class="label">Neuer Titel</div>
      <p class="new-title">"{Vorgeschlagener neuer Titel}"</p>
    </div>
    <p><strong>Warum:</strong> {Begründung 2–3 Sätze}</p>
  </div>
</details>
```

- **rating-key**: `stark` / `mittel` / `schwach`
- **open_attr**: ` open` für Folien mit Bewertung "Schwach". Sonst leer.
- Bei "Stark"-Bewertung: nur die `<h4>Bewertung &amp; Begründung</h4>`-Sektion mit einem positiven Satz, was die Folie gut macht. Keine Vorschlags- oder Folien-Kontext-Sektion.
- Bei fehlendem Body oder fehlenden Notes: `<div class="quote-block">` weglassen.
- Statement-Folien: gleiches Format, Markierung "(Statement-Folie)" im `slide-title-current`-Text.

### Format des Standalone-Tests (`{{STANDALONE_TEST}}`)

```html
<h3>Würde das Querlesen der vorgeschlagenen Titel die Argumentation tragen?</h3>
<p><strong>Verdikt:</strong> {Ja / Eingeschränkt / Nein}. {1–2 Sätze Begründung.}</p>

<h4>Querlesen der Section-Divider + vorgeschlagenen Action Titles</h4>
<ol>
  {Eine <li>-Zeile pro Section-Divider und pro Inhalts-Folie mit dem Vorschlag (oder Original-Titel bei „Stark")}
</ol>

<p>{Optional: Wo der Argumentationsbogen hakt — konkrete Folien-Referenzen.}</p>
```

### HTML schreiben

**Standalone-Modus**: Verwende den Write-Tool-Aufruf mit dem fertigen HTML-Inhalt am lokalen Output-Pfad.

**MTA-Modus**: Schreibe lokal nach `/tmp/<filename>`, dann lade via `drive.py upsert-text` in den `reports/`-Sub-Folder hoch.

Verifiziere kurz, dass alle Platzhalter ersetzt wurden (kein `{{...}}` mehr in der finalen Datei).

Bei sehr großen Decks (> 100 Folien) gruppiere die Detail-Review-Sektion `{{SLIDE_DETAILS}}` nach Sektionen mit `<h3>`-Sektion-Headern, damit der Bericht navigierbar bleibt.

### `status.md`-Update (nur MTA-Modus)

Wenn `MTA_MODE=true`, aktualisiere am Ende `status.md` und das Dashboard nach den Regeln aus `contracts.md` Abschnitt 3:

- `06-01-action-titles-check` in `schritte_done` (Frontmatter)
- Eigene Sektion in "✓ Erledigt" mit Datum und Output (Pfad relativ im MTA-Folder)
- Dashboard (`reports/index.html`) um Skill-Eintrag und Report-Link ergänzen

Im Standalone-Modus: kein status.md-Update.

## Schritt 7 — Chat-Output

Nachdem die HTML-Datei geschrieben ist, gib im Chat eine kompakte Zusammenfassung aus:

```
## Action-Titles-Check — {Kundenname}

**HTML-Bericht:** [{Pfad}]({Pfad})

**Verteilung:** {COUNT_TOTAL} Folien geprüft — {COUNT_STARK} Stark, {COUNT_MITTEL} Verbesserungswürdig, {COUNT_SCHWACH} Schwach ({COUNT_SKIPPED} Sonderfolien übersprungen).

**Standalone-Test:** {Verdikt — Ja / Eingeschränkt / Nein, in 1 Satz}.

**Top-Befund:** {Wichtigste Erkenntnis aus dem Review — z. B. „Sektion B2 hat durchgehend Themenlabels statt Aussagen" oder „Strategie-Teil ist stark, aber Investitions-Sektion verschenkt das Potenzial".}

**Deck:** {URL}
```

Der HTML-Bericht enthält die vollständige Bewertungstabelle, klappbare Detail-Reviews und das Standalone-Querlesen.

## Schritt 8 — Kommentare anbieten

Frage anschließend den Nutzer:

> "Möchtest Du Vorschläge als Kommentare ins Deck einpflegen? Die ursprünglichen Titel bleiben unverändert — Du oder der Empfänger seht jeden Vorschlag im Slides-Kommentar-Panel und könnt ihn dort selektiv übernehmen oder diskutieren. Ich gehe Folie für Folie durch und pflege nur das ein, was Du explizit bestätigst."

Wenn ja, gehe in der Reihenfolge des Decks durch alle Folien mit Bewertung "Verbesserungswürdig" oder "Schwach" und zeige pro Folie:

```
Folie {N}:
  Aktuell:   "{aktueller Titel oder '[Statement-Folie]'}"
  Vorschlag: "{vorgeschlagener Titel}"
```

Warte auf eine explizite Antwort:

- "ja" / "übernehmen" → Vorschlag in die Kommentar-Queue.
- "nein" / "skip" → überspringen, weiter zur nächsten Folie.
- Eine Alternativformulierung des Nutzers → diese Alternative in die Kommentar-Queue.

Frage **eine Folie pro Runde**, nicht mehrere gleichzeitig.

## Schritt 9 — Kommentare einpflegen

Für jede bestätigte Folie erstelle einen verankerten Kommentar via Drive-API. Der Anchor referenziert die Folien-ObjectId aus Schritt 3:

```bash
gws drive comments create \
  --params '{"fileId": "<PRESENTATION_ID>", "fields": "id,content,anchor"}' \
  --json '{
    "content": "<KOMMENTAR_TEXT>",
    "anchor": "{\"r\":\"head\",\"a\":[{\"matrix\":{\"a\":1,\"b\":0,\"c\":0,\"d\":1,\"e\":0,\"f\":0}},{\"page\":\"<SLIDE_OBJECT_ID>\"}]}"
  }'
```

`<KOMMENTAR_TEXT>` wird wie folgt aufgebaut:

```
[Action-Title-Vorschlag — Pyramidalprinzip]
Bewertung: <Stark | Verbesserungswürdig | Schwach>

Aktueller Titel: "<Originaltitel>"
Vorschlag: "<Vorschlag>"

Begründung: <Begründung-Text aus dem Detail-Review, 1–2 Sätze>
```

Erstelle die Kommentare einzeln (ein API-Call pro Folie) — die Drive-API hat keinen Batch-Endpoint für Kommentare. Bei einem Fehler mit dem Anchor (z. B. ungültiges Format): falle zurück auf einen Datei-übergreifenden Kommentar ohne Anchor, dessen Content mit "[Folie X]" beginnt, sodass der Bezug erhalten bleibt:

```bash
gws drive comments create \
  --params '{"fileId": "<PRESENTATION_ID>"}' \
  --json '{"content": "[Folie X] [Action-Title-Vorschlag — Pyramidalprinzip]\nBewertung: ...\n..."}'
```

Wenn keine Bestätigungen vorliegen, überspringe Schritt 9 und gehe direkt zu Schritt 10.

## Schritt 10 — Abschluss

Fasse im Chat zusammen:

- Pfad zur HTML-Datei (aus Schritt 6).
- Anzahl tatsächlich eingepflegter Kommentare und Anzahl Fallback-Kommentare (falls vorhanden, aus Schritt 9).
- Direkter Link zum Deck: `https://docs.google.com/presentation/d/<ID>/edit`.
- Hinweis: Die Original-Titel bleiben unverändert. Der Empfänger sieht alle Vorschläge im HTML-Bericht *und* — falls eingepflegt — im Kommentar-Panel des Decks.

## Edge Cases

- **Statement-Folien ohne TITLE-Placeholder**: werden mitbewertet (relaxierte Methodik). Der Kommentar verankert sich auf der Folien-ObjectId — funktioniert auch ohne Title-ObjectId.
- **403 / `accessNotAuthorized` bei Kommentar-Erstellung**: Nutzer hat keine Kommentar-Rechte am Deck. Erkläre das, biete an, das Review als reinen Bericht zu nutzen.
- **Andere Sprache als Deutsch im Deck**: Erkenne die Sprache aus Body und Notes und schreibe Vorschläge sowie Kommentare in derselben Sprache.
- **Anchor-Format wird abgelehnt**: Fallback auf nicht-verankerten Kommentar mit "[Folie X]"-Präfix im Content.
