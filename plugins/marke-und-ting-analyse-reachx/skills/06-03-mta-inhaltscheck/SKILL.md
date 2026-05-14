---
name: 06-03-mta-inhaltscheck
description: Prüft den Inhalt einer MARKE&TING-Analyse (MTA) in Google Slides — Markenanalyse, Online-Marketing-Potenzialanalyse, Forecast-Hochrechnungen, Investitions-Folien, ROI-Argumentation, Retainer-Hinleitung. Bewertet, ob der Kunde aus dem Deck klar ablesen kann, welche Aufwände auf ihn zukommen und warum sich das Invest lohnt. Output ist ein gestyltes HTML-Dokument im REACHX-Branding plus Kurzfassung im Chat. Nutze diesen Skill, sobald der Nutzer eine Google-Slides-URL oder Presentation-ID nennt und nach MTA-Review, MARKE&TING-Analyse-Check, Inhaltscheck, Potenzialanalyse, Forecast-Prüfung, Investitions-Folien-Review, ROI-Story oder Retainer-Hinleitung fragt — auch bei "MTA prüfen", "ist die Analyse vollständig?", "Investitionsfolien checken", "Forecast nachvollziehbar?", "wird der Retainer klar?". Komplementär zu /06-01-action-titles-check (Mikro-Ebene Titel) und /06-02-pyramid-structure-check (Makro-Ebene Storyline). Setzt gws-CLI voraus. NICHT für PPTX-Dateien.
---

# MTA-Inhaltscheck (MARKE&TING-Analyse)

Reviewt den *Inhalt* einer MARKE&TING-Analyse — also nicht Titel oder Storyline, sondern ob die für den Kunden entscheidenden Inhalte vorhanden, quantifiziert und argumentativ verzahnt sind. Zielfrage: **Versteht der Kunde nach dem Deck, was möglich ist, was es kostet — und warum die Setup-Investition + Retainer keine Kosten, sondern eine Investition sind?**

Output ist eine HTML-Datei im REACHX-Styling (Schrift Red Hat Display/Text, Sunrise-Red als Akzent) mit Executive Summary, Bewertungstabelle, klappbaren Detail-Reviews pro Dimension und Top-3-Hebeln. Im Chat zusätzlich eine Kurzfassung mit Bewertungstabelle und Pfad zur HTML-Datei.

Methodik und Bewertungskriterien stehen ausführlich in `reference/methodology.md` — lies diese Datei *vor* der Inhaltsanalyse in Schritt 6. Das HTML-Template steht in `reference/report-template.html` — dieses wird in Schritt 8 mit Inhalten gefüllt.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Verhältnis zu den anderen Skills

- **06-01-action-titles-check**: bewertet einzelne Folientitel (Mikro).
- **06-02-pyramid-structure-check**: bewertet die Argumentations-Architektur des Decks (Makro).
- **06-03-mta-inhaltscheck** (dieser Skill): bewertet die *inhaltliche Vollständigkeit und Schlagkraft* einer MTA — sind die Pflicht-Inhalte (Diagnose, Forecast, Invest, ROI, Retainer-Brücke) da und tragen sie?

Sinnvolle Reihenfolge: erst Inhalt (dieser Skill), dann Struktur, dann Titel.

## Voraussetzungen

- `gws` ist installiert und authentifiziert. Schlägt ein Aufruf mit Auth-Fehler (Exit-Code 2) fehl, weise den Nutzer auf einmaliges `gws auth login` hin.

## Schritt 0 — MTA-Kontext laden (optional, Dual-Mode)

Dieser Skill kann in zwei Modi laufen:

1. **MTA-Modus**: Wenn der Nutzer den Skill im Kontext einer laufenden MTA aufruft und die MTA im lokalen Active-MTA-Cache registriert ist, wird der HTML-Report nach Drive in den `reports/`-Sub-Folder der aktiven MTA hochgeladen und `status.md` aktualisiert. Briefing-Kontext (Schritt 2) wird aus `data/briefing.md` auf Drive gelesen statt aus dem lokalen Working Directory.
2. **Standalone-Modus**: Wenn keine MTA aktiv ist, schreibt der Skill den Bericht lokal ins Working Directory — wie bisher. Briefing-Kontext wird im lokalen Working Directory gesucht.

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
    DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
    REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
  fi
fi
```

Wenn kein MTA-Slug genannt wird und keiner im Cache ist: Standalone-Modus, kein Hard-Abbruch — der Skill funktioniert dann wie ein generisches Deck-Inhalts-QA-Tool.

## Schritt 1 — Presentation-ID bestimmen

Akzeptiere als Input eine vollständige Slides-URL oder eine reine ID. Aus einer URL wie `https://docs.google.com/presentation/d/<ID>/edit#...` extrahiere `<ID>` zwischen `/d/` und dem nächsten `/`. Wurde nichts mitgegeben, frage explizit nach URL oder ID, bevor Du fortfährst.

## Schritt 2 — Briefing-Kontext laden (optional, aber empfohlen)

Vor dem Inhaltscheck prüfe, ob im Projektordner Briefing-Material liegt — typische Quellen sind Fireflies-Transkripte, Kickoff-Notizen, oder ein vom Nutzer gepflegtes Briefing-Dokument. Diese geben oft preis, *welche* Umsatz-/Lead-/KPI-Ziele der Kunde im Briefing genannt hat. Diese Ziele sollten in der Analyse referenziert werden — wenn nicht, ist das ein Befund für Dimension 1 (Zielklarheit) und Dimension 5 (ROI-Argumentation).

**MTA-Modus**: Suche im `data/`-Sub-Folder auf Drive nach Briefing-Files:

```bash
BRIEFING_ID=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "briefing.md") | .id')
if [ -n "$BRIEFING_ID" ]; then
  python3 "$DRIVE_PY" read "$BRIEFING_ID" > /tmp/briefing.md
fi
```

Wenn `data/briefing.md` auf Drive vorhanden ist, lies sie als Briefing-Quelle.

**Standalone-Modus**: Suche im aktuellen Working Directory und in einem ggf. namentlich passenden Unterordner (z. B. nach Kunden-Name aus Folie 1 des Decks) nach Dateien, deren Name eines der folgenden Muster trifft (case-insensitive):

```
*briefing*
*kickoff*
*transcript*
*fireflies*
*meeting*
*kunde-call*
*onboarding*
```

Mit Endung `.md`, `.txt`, `.json`, `.docx`, `.pdf`. Lies gefundene Dateien (bei `.docx`/`.pdf` über die entsprechenden Skills, falls verfügbar). Extrahiere:

- **Genannte Geschäftsziele**: Umsatzziel, Leadziel, Conversion-Ziel, Wachstums-Vorgaben.
- **Genannte Pain Points**: was funktioniert aktuell nicht, wo will der Kunde hin?
- **Bestehende Marketing-Aktivitäten**: bereits laufende Kanäle, vergangene Maßnahmen, vorhandene Infrastruktur (Shop-System, CRM, etc.).
- **Implizite Erwartungen**: was hat der Kunde als nächsten Schritt erwartet (Strategie, Konzept, Operatives, etc.)?

Wurden keine Dateien gefunden, frage den Nutzer einmal explizit:

> "Liegen Briefing-Notizen, Fireflies-Transkripte oder Kickoff-Protokolle vor, die ich einlesen soll? Damit kann ich abgleichen, ob die im Briefing genannten Ziele in der Analyse referenziert werden. Wenn nein, fahre ich ohne fort — die Bewertung wird dann ohne Briefing-Cross-Check durchgeführt."

Bei "ohne fort": Hinweis im Bericht hinzufügen, dass die Briefing-Verzahnung nicht geprüft werden konnte.

Hinweis: Aktuell existiert kein nativer Fireflies-MCP-Connector. Der Nutzer kann Transkripte als `.md`/`.txt` exportieren und im Projektordner ablegen.

## Schritt 3 — Deck einlesen

```bash
gws slides presentations get --params '{
  "presentationId": "<ID>",
  "fields": "slides(objectId,slideProperties(notesPage(pageElements(shape(placeholder,text)))),pageElements(objectId,shape(placeholder,text)))"
}' > /tmp/mta-deck.json 2>&1
```

**Wichtig**: Die `gws`-CLI druckt vor der eigentlichen JSON-Antwort die Zeile `Using keyring backend: keyring` auf stdout. Bevor Du die Datei mit einem JSON-Parser einliest, strippe die erste Zeile, falls sie nicht mit `{` beginnt:

```bash
head -1 /tmp/mta-deck.json | grep -qv "^{" && sed -i '' '1d' /tmp/mta-deck.json
```

Oder beim Parsen die Datei ab dem ersten `{` lesen.

Schlägt der Aufruf mit `accessNotConfigured` fehl, ist die Slides-API im GCP-Projekt nicht aktiviert — gib den Aktivierungs-Hinweis aus der gws-Stderr unverändert an den Nutzer weiter.

Bei sehr großen Decks (200+ Folien — bei MTAs typisch wegen Anhang) ist die JSON-Antwort über mehrere MB groß. Schreibe sie in `/tmp/mta-deck.json` und lies sie strukturiert weiter, statt alles inline zu halten.

## Schritt 4 — Sektionen klassifizieren und Skelett bilden

Eine MTA hat einen typischen Aufbau, an dem sich der Inhaltscheck orientiert. Die genauen Sektions-Titel variieren, aber die *Rollen* sind konstant:

```
[Intro]                  Cover, Ausgangslage, "Heute präsentieren wir..."-Folie, Inhalt
[Section A1]             "01. | Summary Markenanalyse" (Diagnose)
[Section A2]             "02. | Optimierungspotential Marke" (Maßnahmen)
[Section A3, optional]   "03. | Ausblick Branding" (Brand-Manifesto)
[Section B1]             "04. | Summary Online-Marketing-Analyse" (Diagnose pro Kanal)
[Section B2]             "05. | Optimierungspotentiale Online-Marketing" (Maßnahmen + Forecasts)
[Section C]              "Investition | Kalkulation & Angebot" (Setup-Kosten + Retainer-Brücke)
[Closing]                "Das machen wir | Zeit für Fragen"
[Anhang]                 1. Markenidentität, 2. Markenpositionierung, 3. Zielgruppe,
                         4. Markenkommunikation, 5. User-Experience,
                         SEO-Detail, Content-Detail, Social-Detail, Google-Ads-Detail, Inbound-Detail
```

Mache Folgendes:

1. Identifiziere alle Section-Divider (Folien mit numerierter Sektion z. B. "01. | …", "02. | …" oder mit "Investition | …" als Titel-Element).
2. Ordne jede Section-Divider einer der oben genannten Rollen zu.
3. Notiere Folien-Range pro Sektion (z. B. "Section A1: Folien 5–10", "Section B2: Folien 27–35").
4. **Forecast-Folien identifizieren**: durchsuche das *gesamte* Deck (nicht nur Section B2) nach Folien, deren Titel eines der folgenden Muster trifft (case-insensitive):
   - "Forecast", "Hochrechnung", "Forecast-Hochrechnung"
   - "Potenzial-Hochrechnung", "möglichen monatlichen Umsatz"

   Forecast-Folien können *innerhalb* der Maßnahmen-Sektion (B2) erscheinen, *direkt vor* der Investitions-Sektion, oder *zwischen* Maßnahmen-Folien einzelner Kanäle. Notiere für jede Forecast-Folie: Kanal (SEO/SEA/Paid Social/Inbound/Content), Folien-Index, vollständiger Body-Text mit den Annahmen.

5. **Investitions-Detailfolien identifizieren** (Titel oder Body enthält):
   - "Investition", "Kalkulation", "Angebot"
   - "Brand Optimierung", "Marketing-Setup", "Strategiephase", "Setup-Phase"
   - "Webdesign" (wenn als Setup-Modul positioniert)

6. **Timeline-Folie identifizieren** (Titel enthält "Projektmodell", "Timeline", "Roadmap" oder Body listet "Monat 1, Monat 2, …" auf).

7. **ROI-/Rechenbeispiel-Folien** (Titel enthält "ROI", "Rechenbeispiel", "Amortisation" oder Body enthält explizite Gegenüberstellung Forecast vs. Investition).

8. **Retainer-Inhalt-Folien identifizieren** — Folien, die *im Hauptteil* (nicht im Anhang) zeigen, was der Retainer monatlich umfasst. Erkennbar an: Titel oder Untertitel enthält "Retainer", "Laufender Betrieb", oder Body ist eine Tabelle mit Monaten als Spalten und Leistungen als Zeilen (SEO, Content, Google Ads, etc.). Diese Folien gehören zur Investitions-Sektion (Rolle: Retainer-Inhalt) und sind zentral für Dimension 6 (Roter Faden zum Retainer).

9. **Förderungs-Folien** (Titel enthält "RKW", "Förder", "Zuschuss", "Digital Jetzt") — optional, Bonus.

10. **Hauptteil-/Anhang-Trennung**: Anhang beginnt typischerweise nach der Closing-Folie ("Das machen wir | Zeit für Fragen") oder direkt nach der Investitions-Sektion. Folien ab dort werden im Inhaltscheck *unterstützend* einbezogen, aber nicht primär bewertet (der Anhang ist Backup, kein Kern-Argument).

Notiere die Skelett-Klassifikation als kompakte Liste — sie ist Grundlage für die Inhaltsbewertung.

## Schritt 5 — Pro Folie extrahieren

Sammle aus der JSON-Antwort für jede Folie:

- **Folien-Index** (1-basiert).
- **Folien-ObjectId** (`slide.objectId`).
- **Titel** — alle TITLE/CENTERED_TITLE-Placeholder zusammenkonkateniert.
- **Body** — alle anderen Text-tragenden Shapes.
- **Notes** — `notesPage` BODY-Placeholder.

## Schritt 6 — Methodik laden

Lies *jetzt* `reference/methodology.md` vollständig. Die Datei enthält:

- Theoretischen Hintergrund: Was eine MTA leisten muss
- Die sechs Bewertungsdimensionen mit Detail-Kriterien
- Bewertungsskala (Stark / Verbesserungswürdig / Schwach)
- Häufige Antipatterns
- Beispielbewertungen als Kalibrierung
- Templates für Verbesserungsvorschläge

## Schritt 7 — Inhaltscheck durchführen

Bewerte das Deck systematisch entlang der sechs Dimensionen aus `reference/methodology.md`. Bewertungsskala pro Dimension: **Stark | Verbesserungswürdig | Schwach**.

Die sechs Dimensionen sind:

1. **Zielklarheit** — Versteht der Kunde nach dem Intro, was die Analyse leisten soll und worauf sie hinausläuft (Setup → Retainer)?
2. **Markenanalyse-Diagnose** — Klare Stärken/Schwächen-Aussage + zugeordnete Optimierungs-Maßnahmen mit REACHX-Empfehlung?
3. **Online-Marketing-Potenzialanalyse** — Pro Kanal: Diagnose + Maßnahmen + quantifizierter Forecast (Suchvolumen/Klicks/CTR/AOV/CLV → Umsatz)?
4. **Investitions-Klarheit** — Setup-Phase mit Modulen und Einzelkosten + Timeline + Retainer als nächste Phase + Gesamthöhe erkennbar?
5. **ROI-Argumentation** — Werden Forecast-Umsätze gegen Setup + Retainer + Mediabudget gespiegelt? Wird "Investition statt Kosten"-Framing genutzt?
6. **Roter Faden zum Retainer** — Führt das Deck logisch von Diagnose über Maßnahmen über Setup zur expliziten Retainer-Empfehlung?

Beziehe für jede Dimension die Briefing-Informationen aus Schritt 2 (falls vorhanden) als Cross-Check ein.

Pro Dimension sammle:

- **Bewertung** (Stark/Verbesserungswürdig/Schwach)
- **Beobachtung** (was findet sich tatsächlich im Deck, mit konkreten Folien-Referenzen)
- **Begründung** (warum diese Bewertung — welche Kriterien aus der Methodik treffen zu?)
- **Verbesserungsvorschläge** (konkrete Aktion, ggf. mit Text-Vorschlag für eine fehlende Folie)

Sammle außerdem:

- **Executive Summary** (4–6 Sätze, siehe Format unten)
- **Top-3-Verbesserungen** (Vorschläge mit dem höchsten Hebel für den Retainer-Verkauf)

## Schritt 8 — HTML-Bericht generieren

Lies `reference/report-template.html`. Das Template enthält Platzhalter in der Form `{{TOKEN}}`, die Du durch die Inhalte aus Schritt 7 ersetzt.

### Output-Pfad bestimmen

- **Kunden-Slug**: aus dem Cover-Folientitel (Folie 1) extrahieren — Kleinbuchstaben, Sonderzeichen entfernen, Leerzeichen durch `-` ersetzen. Beispiel: "CasaFan" → `casafan`. Im MTA-Modus alternativ aus `meta.json.kunden_slug`.
- **Datum**: heutiges Datum im Format `YYYY-MM-DD`.
- **Dateiname**: `deck-qa-mta-inhalt-{kunden-slug}-{datum}.html`
- **Speicherort**:
  - **MTA-Modus**: Datei wird lokal nach `/tmp/<filename>` gerendert und dann via `python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "<filename>" "/tmp/<filename>" "text/html"` nach Drive in den `reports/`-Sub-Folder der aktiven MTA hochgeladen.
  - **Standalone-Modus**: Datei wird ins aktuelle Working Directory geschrieben (Fallback `/tmp/` wenn nicht beschreibbar) — wie bisher.

### Platzhalter ersetzen

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | `MTA-Inhaltscheck — {Kundenname}-Deck` (HTML-`<title>`) |
| `{{EYEBROW}}` | `MARKE&TING-Analyse · Inhaltscheck` |
| `{{DISPLAY_NAME}}` | `{Kundenname}-Deck` (in Hero-Headline) |
| `{{REPORT_DATE}}` | Heutiges Datum, Format `YYYY-MM-DD` |
| `{{DECK_DATE_SUFFIX}}` | Wenn das Deck-Datum aus Folie 1 ablesbar ist: ` · Deck-Datum: {Datum}`, sonst leerer String |
| `{{DECK_URL}}` | `https://docs.google.com/presentation/d/{ID}/edit` |
| `{{EXEC_SUMMARY}}` | Ein oder mehrere `<p>`-Elemente mit dem Executive Summary aus Schritt 7. Verwende `<strong>` für die zentrale Schwäche und den Top-Hebel. |
| `{{BRIEFING_NOTE}}` | Wenn Briefing geladen: `<p class="note">Briefing-Cross-Check durchgeführt: …</p>`. Wenn nicht: `<p class="note">Briefing-Cross-Check nicht durchgeführt — keine Briefing-Datei im Projektordner gefunden.</p>` |
| `{{RATINGS_ROWS}}` | Sechs `<tr>`-Zeilen, eine pro Dimension. Format siehe unten. |
| `{{DIMENSION_DETAILS}}` | Sechs `<details class="dim">`-Blöcke, einer pro Dimension. Format siehe unten. |
| `{{TOP3_ITEMS}}` | Drei `<li>`-Elemente. Format siehe unten. |
| `{{FOOTER_TEXT}}` | `MTA-Inhaltscheck Skill v1.0 · Bericht erstellt automatisiert auf Basis von <a href="{DECK_URL}" target="_blank" rel="noopener">Original-Deck</a>. Dieser Bericht ändert keine Folien oder Kommentare im Deck.` |

### Format der Bewertungstabellen-Zeilen (`{{RATINGS_ROWS}}`)

```html
<tr>
  <td>1. Zielklarheit</td>
  <td><span class="badge {bewertungs-klasse}">{Bewertungs-Label}</span></td>
  <td>{Kernbefund — ein Satz mit Folien-Referenz wo sinnvoll}</td>
  <td>{Top-Verbesserung — ein Satz}</td>
</tr>
```

Mapping Bewertung → CSS-Klasse:
- "Stark" → `badge stark`
- "Verbesserungswürdig" → `badge mittel`
- "Schwach" → `badge schwach`

Bei "Stark"-Bewertung in der Top-Verbesserung-Spalte: `—` (Em-Dash).

### Format der Detail-Blöcke (`{{DIMENSION_DETAILS}}`)

Pro Dimension ein Block:

```html
<details class="dim" data-rating="{rating-key}"{open_attr}>
  <summary>
    <span class="badge {bewertungs-klasse}">{Bewertungs-Label}</span>
    Dimension {N}: {Name}
  </summary>
  <div class="body">
    <h4>Beobachtung</h4>
    <p>{3–5 Sätze. Was findet sich konkret im Deck? Folien-Referenzen.}</p>

    <h4>Begründung der Bewertung</h4>
    <p>{2–3 Sätze, welche Kriterien aus der Methodik erfüllt oder verfehlt werden.}</p>

    <h4>Verbesserungsvorschläge</h4>
    <div class="suggestion">
      <div class="label">{Nummer} — {Kurz-Aktion}</div>
      <p>{Beschreibung der Aktion}</p>
      <pre class="template">{Text-Vorschlag mit <strong>Titel:</strong>, <strong>Body:</strong> und <span class="placeholder">{...}</span> für offene Werte}</pre>
    </div>
    <!-- weitere .suggestion-Blöcke -->
  </div>
</details>
```

- **rating-key**: `stark` / `mittel` / `schwach`
- **open_attr**: ` open` für Dimensionen mit Bewertung "Schwach" (default geöffnet, damit der Empfänger die kritischsten Befunde sofort sieht). Sonst leer.
- Bei "Stark"-Bewertung: keine `<h4>Verbesserungsvorschläge</h4>`-Sektion, stattdessen `<h4>Was die Sektion gut macht</h4>` mit einem Absatz.
- In `<pre class="template">` HTML-Entities verwenden (`&amp;`, `&lt;` etc.) und Platzhalter mit `<span class="placeholder">{...}</span>` markieren.
- Wenn ein Vorschlag eine Tabelle enthält (Forecast, Investitions-Summe, ROI), nutze `<table class="data">` mit optionalen `<tr class="total">` für Summenzeilen.

### Format der Top-3-Items (`{{TOP3_ITEMS}}`)

```html
<li><strong>{Kurz-Aktion}</strong> ({Dimension}) — {Begründung in einem Satz}</li>
```

### HTML schreiben

**Standalone-Modus**: Verwende den Write-Tool-Aufruf mit dem fertigen HTML-Inhalt am lokalen Output-Pfad.

**MTA-Modus**: Schreibe lokal nach `/tmp/<filename>`, dann lade via `drive.py upsert-text` in den `reports/`-Sub-Folder hoch.

Verifiziere kurz, dass alle Platzhalter ersetzt wurden (kein `{{...}}` mehr in der finalen Datei).

### `status.md`-Update (nur MTA-Modus)

Wenn `MTA_MODE=true`, aktualisiere am Ende `status.md` und das Dashboard nach den Regeln aus `contracts.md` Abschnitt 3:

- `06-03-mta-inhaltscheck` in `schritte_done` (Frontmatter)
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs (HTML-Report-Name) und Bewertungs-Zusammenfassung der sechs Dimensionen
- Dashboard (`reports/index.html`) um Skill-Eintrag und Report-Link ergänzen

Im Standalone-Modus: kein status.md-Update.

## Schritt 9 — Chat-Output

Nachdem die HTML-Datei geschrieben ist, gib im Chat eine kompakte Zusammenfassung aus:

```
## MTA-Inhaltscheck — {Kundenname}

**HTML-Bericht:** [{Pfad}]({Pfad})

**Bewertungstabelle:**

| Dimension | Bewertung |
|---|---|
| 1. Zielklarheit | {Bewertung} |
| 2. Markenanalyse-Diagnose | {Bewertung} |
| 3. Online-Marketing-Potenzialanalyse | {Bewertung} |
| 4. Investitions-Klarheit | {Bewertung} |
| 5. ROI-Argumentation | {Bewertung} |
| 6. Roter Faden zum Retainer | {Bewertung} |

**Top-3-Hebel:**

1. {Top-Vorschlag 1}
2. {Top-Vorschlag 2}
3. {Top-Vorschlag 3}

**Deck:** {URL}
```

Der HTML-Bericht enthält die vollständigen Detail-Reviews und Text-Vorschläge mit kopierfähigen `<pre>`-Templates.

## Schritt 10 — Abschluss

Optional: Hinweis auf die komplementären Skills `/06-02-pyramid-structure-check` (Storyline) und `/06-01-action-titles-check` (Titel) — sinnvoll, nachdem die Inhalte stehen.

## Edge Cases

- **Deck ohne erkennbare MTA-Struktur**: Wenn weniger als drei der typischen Sektionen erkennbar sind, nenne das im Bericht explizit als zentralen Befund. Schlage in den Verbesserungsvorschlägen zu Dimension 1 vor, welche Sektionen ergänzt werden müssten.
- **Sehr kurzes Deck (< 30 Folien)**: Konzentriere Dich auf Dimension 1, 4, 5, 6 und sage explizit, dass die Analysetiefe verkürzt ist.
- **Decks ohne Forecast-Folien**: Dimension 3 wird mindestens "Verbesserungswürdig", oft "Schwach". Schlage vor, welche Forecast-Folien pro Kanal ergänzt werden sollten, mit Template-Annahmen aus der Methodik.
- **Deck ohne Investitions-Sektion**: Dimension 4 wird "Schwach". Sage explizit, dass das Deck keinen Retainer verkauft, sondern ein reiner Status-Bericht ist.
- **Zwei Forecasts mit widersprüchlichen Annahmen** (z. B. AOV 450 € und AOV 964 € in zwei Forecasts derselben Marke): Antipattern. Notiere als Befund in Dimension 3.
- **Andere Sprache als Deutsch im Deck**: Erkenne die Sprache aus Body und Notes und schreibe Bericht und Vorschläge in derselben Sprache. Die Eyebrow-Labels im HTML (`MARKE&TING-Analyse · Inhaltscheck`, `01 — Verdichtung`, etc.) bleiben deutsch (REACHX-Branding), Inhalte werden übersetzt.
- **Kein Schreibrecht im CWD (Standalone-Modus)**: Fallback auf `/tmp/deck-qa-mta-inhalt-{kunden-slug}-{datum}.html` und vermerke das im Chat-Output. Im MTA-Modus irrelevant — die Datei landet auf Drive.
- **Keine Briefing-Datei verfügbar und Nutzer überspringt**: Bewerte ohne Briefing-Cross-Check und vermerke die Einschränkung im Executive Summary.
