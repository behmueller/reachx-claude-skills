---
name: 02-05-wettbewerber-realitaets-check
description: Verifiziert die in 02-02-wettbewerber-identifikation gesammelten Akteure (kundengenannte + regionale + Best-Practice) gegen erhobene Daten und klassifiziert sie nach realer Bedrohungslage. Vom Kunden genannte Wettbewerber sind Hypothesen, keine Fakten - dieser Skill prueft pro Akteur mehrere Realitaets-Signale (organische Sichtbarkeit via Sistrix-VI / Ahrefs-DR, lokale Relevanz und GMB-Proximity, Paid-Aktivitaet, Website-/Marken-Staerke) und teilt jeden Akteur regelbasiert in drei Klassen ein - aktuell_stark, latente_bedrohung, nachrangig. Pro Akteur ein Soll-Ist-Abgleich zwischen Kunden-Einschaetzung und Datenlage; Abweichungen werden explizit als Befund ausgewiesen. Outputs sind wettbewerber/realitaets-check.md, wettbewerber/realitaets-check.csv und ein HTML-Report - ab diesem Skill die massgebliche Wettbewerbs-Datenbasis fuer alle Folge-Skills. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext die genannten Wettbewerber verifizieren oder priorisieren will - auch bei Phrasen wie "Wettbewerber-Realitaets-Check", "sind die genannten Konkurrenten wirklich gefaehrlich", "latente Bedrohung", "Konkurrenz verifizieren", "Wettbewerber-Bedrohungslage", "stimmt die Wettbewerber-Einschaetzung des Kunden", "Soll-Ist-Abgleich Wettbewerber", "welche Konkurrenten sind real relevant". Setzt voraus, dass 02-02-wettbewerber-identifikation gelaufen ist und wettbewerber/liste.md den Status bestaetigt hat - bricht sonst ab. Laeuft zwischen 02-02-wettbewerber-identifikation und 02-03-wettbewerber-marken-profil.
---

# Wettbewerber-Realitäts-Check

Vom Kunden genannte Wettbewerber sind **Hypothesen, keine Fakten** (`contracts.md` Abschnitt 13). Dieser Skill nimmt die in `02-02-wettbewerber-identifikation` gesammelten Akteure — kundengenannt, regional, Best-Practice — und verifiziert sie gegen erhobene Daten. Er verhindert zwei typische MTA-Fehler:

1. Ein im Kickoff genannter „Hauptkonkurrent" wird ungeprüft als Top-Bedrohung in die Analyse übernommen, obwohl die Datenlage ihn als nachrangig ausweist.
2. Ein datenseitig real gefährlicher Akteur wird übersehen, weil der Kunde ihn nicht auf dem Schirm hatte.

Das Ergebnis ist eine **regelbasierte Klassifikation** jedes Akteurs in drei Bedrohungs-Klassen plus ein **Soll-Ist-Abgleich** zwischen Kunden-Einschätzung und Datenlage. Die Outputs dieses Skills (`wettbewerber/realitaets-check.md` + `.csv`) sind **ab hier die maßgebliche Wettbewerbs-Datenbasis** für alle Folge-Skills — `02-03-wettbewerber-marken-profil`, `02-04-branchenportal-recherche` und die Synthese-Stufe lesen die Klassifikation, um Profilier-Tiefe und Bedrohungs-Gewichtung zu steuern.

**Position im Workflow:** zwischen `02-02-wettbewerber-identifikation` (liefert die Akteur-Liste) und `02-03-wettbewerber-marken-profil` (profiliert die als relevant verifizierten Akteure).

**Kein Schema-vor-Lauf nötig** — die Akteure kommen aus der bereits vom Strategen bestätigten `wettbewerber/liste.md`, die Klassifikations-Schwellen sind fest in `reference/klassifikations-schema.md` dokumentiert. Der Skill prüft beim Start, ob `02-02` gelaufen ist; sonst Abbruch.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, MTA-Auswahl), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs, Drive-Operationen via `drive.py`, regelbasierte Klassifikation, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="02-05-wettbewerber-realitaets-check"
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

## Wann triggern

- "Wettbewerber-Realitäts-Check für [Kunde]"
- "Sind die genannten Konkurrenten wirklich gefährlich?"
- "Konkurrenz verifizieren"
- "Welche Wettbewerber sind real relevant?"
- "Soll-Ist-Abgleich der Wettbewerber-Einschätzung"
- "Latente Bedrohungen finden"
- "Wettbewerber-Bedrohungslage bewerten"
- Nutzer will im MTA-Kontext die `liste.md` gegen Daten prüfen, bevor profiliert wird

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- `02-02-wettbewerber-identifikation` Phase B abgeschlossen → `wettbewerber/liste.md` vorhanden
- `wettbewerber/liste.md` hat `status: bestaetigt` im Frontmatter — sonst Abbruch mit Hinweis
- **Optionaler MCP: Sistrix** (für Sichtbarkeitsindex via `mcp__sistrix__domain_visindex` / `domain_visindex_overview`). Health-Check vor dem Lauf:
  ```bash
  [ -n "$SISTRIX_API_KEY" ] || echo "⚠ SISTRIX_API_KEY nicht gesetzt — Sistrix nicht verfügbar."
  ```
- **Optionaler MCP: Ahrefs** (für Domain Rating via `mcp__claude_ai_Ahrefs__site-explorer-domain-rating` / `site-explorer-metrics`). Health-Check vor dem Lauf via billigem Test-Call (`subscription-info-limits-and-usage`).
- **Optionaler MCP: Apify** (für GMB-/Maps-Proximity bei lokalen Akteuren via Google-Maps-Scraper). Credential-Check:
  ```bash
  [ -n "$APIFY_TOKEN" ] || echo "⚠ APIFY_TOKEN nicht gesetzt — Maps-Proximity nicht erhebbar."
  ```

**Reduced-Modus (`contracts.md` Abschnitt 11):** Alle drei MCPs sind **optional** — der Skill ist auch ohne sie sinnvoll lauffähig, weil er die Signale aus `wettbewerber/liste.md` (Sistrix-Visibility, GMB-Daten, Online-Marketing-Signale, die `02-02` bereits erhoben hat) und einen leichten Website-Check als Basis nutzen kann. Fehlt ein MCP, sinkt nur die Frische/Tiefe der Signale:

- **Kein Sistrix erreichbar** → der Skill nimmt den `sistrix_visibility_index` aus `liste.md` (Best-Practice-Einträge) bzw. die `online_marketing_signale`-Strings. Wenn dort kein VI-Wert steht, bleibt das Signal `sichtbarkeit` leer und das `konfidenz`-Feld des Akteurs sinkt.
- **Kein Ahrefs erreichbar** → das DR-Signal entfällt; Sichtbarkeit wird allein über VI bewertet.
- **Kein Apify erreichbar** → GMB-Proximity wird nur aus den in `liste.md` vorhandenen Koordinaten/Adressen berechnet (für `regional`-Einträge hat `02-02` Lat/Lng erhoben), nicht frisch re-gescraped.

In jedem Reduced-Fall: pro betroffenem Akteur `konfidenz: niedrig` im CSV/Frontmatter, und im Schluss-Format eine zusammenfassende Reduced-Notiz. **Kein Abbruch** wegen fehlender optionaler MCPs — nur ein klarer Hinweis.

Der Skill bricht **nur** ab, wenn `02-02` nicht gelaufen ist oder `liste.md` nicht `bestaetigt` ist — das sind harte Voraussetzungen.

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  python3 "$DRIVE_PY" list-mtas
  echo "✗ MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

SLUG=$(jq -r '.projekt_slug' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WETT_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Wenn `META_ID` leer ist:

```
✗ Kein gültiger MTA-Folder.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

### Schritt 1: Voraussetzungs-Check — `wettbewerber/liste.md` lesen

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -z "$LISTE_ID" ]; then
  echo "✗ wettbewerber/liste.md nicht gefunden auf Drive."
  echo "Bitte zuerst 02-02-wettbewerber-identifikation laufen lassen (Phase A + Phase B)."
  exit 1
fi
python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/liste.md
```

Parse das YAML-Frontmatter von `/tmp/liste.md`:

- `status: bestaetigt` → weiter
- `status: vorgeschlagen` → Abbruch:
  ```
  ⏸ wettbewerber/liste.md hat status: vorgeschlagen.
  Bitte erst die Liste reviewen und auf status: bestaetigt setzen, dann diesen Skill erneut aufrufen.
  ```
- Anderer Status → Abbruch mit Hinweis auf erlaubte Werte

**Wiederholungs-Lauf:** Existiert `wettbewerber/realitaets-check.md` bereits auf Drive, einmal fragen, ob überschreiben (alte Version landet in der Drive-Versions-Historie) oder Backup-und-neu (`realitaets-check.backup-<ISO>.md` per `upsert-text` ablegen) oder Abbruch.

### Schritt 2: Akteur-Set zusammenstellen

Aus dem Frontmatter von `/tmp/liste.md` **alle** Akteure aus den drei Kategorien sammeln — `wettbewerber.kunde_genannt`, `wettbewerber.regional`, `wettbewerber.best_practice_ueberregional`. **Kein Akteur wird ausgelassen**, auch nicht solche mit `empfehlung_profilieren: nein` — gerade die kundengenannten, die `02-02` als schwach markiert hat, sind der Kern des Realitäts-Checks.

Pro Akteur die in `liste.md` bereits vorhandenen Felder übernehmen:

- `name`, `website`, `kategorie`
- bei `kunde_genannt`: `bedrohungsgrad` (= die **Kunden-Einschätzung** für den Soll-Ist-Abgleich), `kontext_aus_briefing`
- bei `regional`: `standort` (Adresse, PLZ, Stadt, Koordinaten), `google_maps_rating`, `google_maps_reviews_count`
- bei `best_practice_ueberregional`: `sistrix_visibility_index`, `sistrix_top_keywords`
- für alle: `online_marketing_signale`, `quelle_zusatz`

Außerdem den **Kunden-Standort** aus `meta.json` (`region`) und — wenn vorhanden — aus `data/kunde.md` (GMB-Standorte in den Touchpoints) ermitteln. Der Kunden-Standort ist der Bezugspunkt für die GMB-Proximity-Berechnung.

Lies optional `data/briefing.md` (für `wettbewerber_genannt` und den genannten Bedrohungsgrad, falls in `liste.md` knapper) und `data/kunde.md` (Kunden-Standort) aus dem `data/`-Sub-Folder — wenn nicht vorhanden, kein Fehler.

### Schritt 3: Realitäts-Signale pro Akteur erheben

Für **jeden** Akteur die vier Signal-Achsen erheben. Die genauen Schwellen und die Punkte-Logik stehen verbindlich in `reference/klassifikations-schema.md` — hier nur die Erhebungs-Logik.

#### 3a. Organische Sichtbarkeit

- **Sistrix-VI:** Wenn Sistrix erreichbar, `domain_visindex` (bzw. `domain_visindex_overview` für den Länder-Kontext) für die Akteurs-Domain abfragen. Sonst den `sistrix_visibility_index` aus `liste.md` nehmen (nur bei Best-Practice-Einträgen vorhanden) bzw. den VI-Wert aus den `online_marketing_signale`-Strings parsen.
- **Ahrefs-DR:** Wenn Ahrefs erreichbar, `site-explorer-domain-rating` für die Akteurs-Domain abfragen. DR ist robuster als VI, weil er die Backlink-Stärke misst und nicht von einzelnen kurz rankenden Keywords abhängt.
- **Volatilitäts-Disziplin (`contracts.md` Abschnitt 13 — Pflicht):** Der Sistrix-VI ist bei **Kleinstwerten unzuverlässig** — bei `VI < 0,05` verdoppelt ein einzelnes kurz rankendes Keyword den Wert. Für lokale Akteure mit VI in dieser Größenordnung wird die Sichtbarkeit **nicht primär über den VI** bewertet, sondern über DR und über die lokalen Signale (3b). Der VI bleibt dann nur **sekundäres** Signal und wird im Output entsprechend markiert (`sichtbarkeit_vi_konfidenz: niedrig`).
- Quellen-Kennzeichnung: VI/DR direkt aus dem MCP gemessen → `erhoben`; aus `liste.md` übernommen → `erhoben` (mit Datenstand-Hinweis aus `liste.md`).

#### 3b. Lokale Relevanz / GMB-Proximity

Nur sinnvoll, wenn der Kunde lokal/regional agiert (`meta.json.region` ist eine Stadt/Region, nicht „national"/„DACH"/„international"). Bei nationalem/Online-Kunden ist diese Achse für alle Akteure neutral — im Schema dokumentiert.

- **Distanz zum Kunden-Standort:** Für `regional`-Akteure hat `liste.md` bereits Koordinaten. Distanz Akteur ↔ Kunden-Standort per Haversine berechnen (km). Wenn Koordinaten fehlen und Apify erreichbar: Akteurs-Adresse via Google-Maps-Scraper geocoden.
- **Einzugsgebiet-Überlappung:** Liegt der Akteur innerhalb des Einzugsradius des Kunden (Default-Radius aus `reference/klassifikations-schema.md`, branchenabhängig), zählt er als „im Kernmarkt". Liegt er deutlich außerhalb, ist er lokal kein direkter Wettbewerber — kann aber `latente_bedrohung` sein, wenn er stark ist (siehe 3a + 3d).
- **GMB-Stärke:** `google_maps_rating` × `google_maps_reviews_count` aus `liste.md` als grobes lokales Reputations-Signal.

#### 3c. Paid-Aktivität

- Aus den `online_marketing_signale` in `liste.md` ableiten, ob aktive Google Ads / Meta Ads / LinkedIn-Ads erkannt wurden (`02-02` hat das bereits geprüft).
- Optionaler Frische-Check: Google Ads Transparency Center (`https://adstransparency.google.com/?domain=<domain>`) und Meta Ad Library kurz öffnen, falls die `liste.md`-Signale älter sind. Kein endloses Durchprobieren — ein Check pro Quelle.
- Signal-Wert: `aktiv` (mindestens eine bezahlte Quelle live), `inaktiv` (keine erkennbar), `unbekannt` (nicht prüfbar).

#### 3d. Website-/Marken-Stärke (grober Check)

- Kurzer Check der Akteurs-Startseite (HTTP-Status, ist es eine echte Marken-Website, professioneller Auftritt, erkennbares Online-Marketing-Setup wie Tracking/Newsletter/Blog).
- Bewertung grob in `stark` / `mittel` / `schwach` — ist die Marke ein ernstzunehmender, ausgebauter Online-Auftritt oder eine dünne Visitenkarten-Seite?
- Website offline / 404 → Signal `schwach`, Notiz „Website nicht erreichbar".

**Signal-Erhebung robust halten:** Schlägt ein einzelner Signal-Call fehl (MCP-Timeout, Domain offline), das Signal als `unbekannt` markieren und mit den verbleibenden Signalen weiterklassifizieren — **nicht** den ganzen Akteur überspringen. Bei `Session ID not found` auf Apify: GMB-Proximity-Achse für die restlichen Akteure auf Reduced (aus `liste.md`-Koordinaten) umstellen, im Schluss-Format Reconnect-Hinweis (`contracts.md` Abschnitt 11).

### Schritt 4: Regelbasierte Klassifikation

Jeder Akteur wird anhand der erhobenen Signale **regelbasiert** in genau eine von drei Klassen einsortiert. Die Schwellen und die vollständige Entscheidungs-Logik stehen verbindlich in `reference/klassifikations-schema.md` — der Skill wendet sie an, ohne sie pro Lauf neu zu erfinden.

Die drei Klassen (Kurzfassung — Details im Schema):

| Klasse | Bedeutung |
|---|---|
| `aktuell_stark` | Heute ein realer Wettbewerber im Kernmarkt des Kunden — starke Sichtbarkeit **und/oder** starke lokale Präsenz im Einzugsgebiet, ggf. plus Paid-Aktivität. |
| `latente_bedrohung` | Heute schwach im Kernmarkt oder in einem anderen Segment/einer anderen Region — aber mit Substanz (z. B. starker überregionaler Akteur, der lokal aufdrehen könnte; oder ein Akteur mit starker Marke aber noch ohne lokalen Fokus). Könnte schnell gefährlich werden, sobald der Kunde aufdreht oder der Akteur expandiert. |
| `nachrangig` | Datenseitig kein relevanter Wettbewerber — schwache Sichtbarkeit, keine lokale Überlappung, keine Paid-Aktivität, dünne Marke. Häufig ein kundengenannter Akteur, den der Kunde überschätzt. |

**Pflicht-Begründung:** Pro Akteur formuliert der Skill einen kurzen, datengestützten Begründungs-Satz, der die Klasse trägt — welche Signale ausschlaggebend waren. Eine Klasse ohne Beleg-Signale ist nicht zulässig.

**Latente-Bedrohung-Frage (`contracts.md` Abschnitt 13 — Pflicht):** Für jeden als `nachrangig` oder schwach eingestuften Akteur explizit prüfen: *Wer ist heute schwach, würde aber stark, sobald der Kunde aufdreht oder der Akteur lokal/überregional expandiert?* Best-Practice-überregionale Akteure mit hoher Sichtbarkeit, die heute nicht im Einzugsgebiet des Kunden aktiv sind, sind die klassischen `latente_bedrohung`-Kandidaten — nicht `nachrangig`.

### Schritt 5: Soll-Ist-Abgleich

Für jeden Akteur — besonders für die `kunde_genannt`-Kategorie — die **Kunden-Einschätzung** gegen die **Datenlage** stellen:

- **Soll (Kunde):** der `bedrohungsgrad` aus `liste.md` / `briefing.md` (`direkt`, `indirekt`, `inspiration`) bzw. bei nicht vom Kunden genannten Akteuren der implizite Status „vom Kunden nicht erwähnt".
- **Ist (Daten):** die in Schritt 4 vergebene Klasse.

Aus der Kombination ergibt sich der **Abgleich-Befund**. Die Mapping-Tabelle steht in `reference/klassifikations-schema.md`. Die wichtigsten Abweichungs-Fälle, die **explizit als Befund** ausgewiesen werden müssen:

- **Überschätzt:** Kunde nennt den Akteur als `direkt`-Konkurrenten, die Daten sagen `nachrangig` → Befund „Vom Kunden überschätzt — datenseitig nachrangig."
- **Unterschätzt / blinder Fleck:** Akteur ist `aktuell_stark`, wurde vom Kunden aber gar nicht oder nur als `inspiration` genannt → Befund „Vom Kunden unterschätzt / blinder Fleck."
- **Latente Bedrohung übersehen:** Akteur ist `latente_bedrohung`, vom Kunden nicht erwähnt → Befund „Latente Bedrohung, vom Kunden nicht auf dem Schirm."
- **Bestätigt:** Kunden-Einschätzung und Datenlage decken sich → Befund „Kunden-Einschätzung bestätigt."

Übereinstimmungen sind genauso ein gültiges Ergebnis wie Abweichungen — beide gehören in den Output. Nur die **Abweichungen** wandern zusätzlich in den Auffälligkeiten-Block.

### Schritt 6: `wettbewerber/realitaets-check.csv` nach Drive schreiben

Eine Zeile pro Akteur, eine Spalte pro Signal plus Klasse und Soll-Ist. Format und Spalten-Liste in `reference/realitaets-check-schema.md`. Baue die CSV lokal im Cache zusammen und lade sie nach Drive:

```bash
mkdir -p ~/.cache/reachx-mta/"$SLUG"
# ... realitaets-check.csv lokal aufbauen ...
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "realitaets-check.csv" \
  ~/.cache/reachx-mta/"$SLUG"/realitaets-check.csv "text/csv"
```

### Schritt 7: `wettbewerber/realitaets-check.md` nach Drive schreiben

Das Aggregat: pro Akteur Klassifikation + Begründung + Soll-Ist, plus ein Auffälligkeiten-Block. Format in `reference/realitaets-check-schema.md`. Baue es lokal zusammen (Markdown + YAML-Frontmatter Hybrid) und lade es nach Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "realitaets-check.md" \
  ~/.cache/reachx-mta/"$SLUG"/realitaets-check.md "text/markdown"
```

Pflicht im Frontmatter: pro Zahl/Signal die Quellen-Kennzeichnung (`erhoben` / `briefing` / `benchmark` / `schaetzung_skill`) nach `contracts.md` Abschnitt 13. Der Kunden-Bedrohungsgrad ist immer `briefing` (unverifiziert), die erhobenen Signale `erhoben`, die Einzugsradius-Defaults `benchmark`.

**Reihenfolge (`contracts.md` Abschnitt 3):** zuerst CSV (Schritt 6), dann `.md` (Schritt 7), dann HTML-Report (Schritt 8), dann Dashboard und `status.md` — so sind die inhaltlichen Outputs auch bei vorzeitigem Abbruch vollständig.

### Schritt 8: HTML-Report `reports/03b-wettbewerber-realitaets-check.html`

**Report-Nummer:** `03b` — der Report sortiert sich direkt hinter `03-wettbewerber-liste.html` (Output von `02-02`) und vor `04-wettbewerber-profile.html` (Output von `02-03`) ein. Das ist die Workflow-Reihenfolge. **Beim Lauf vor dem Schreiben gegen `reports/index.html` prüfen** — listet das Dashboard bereits einen `03b`-Report (z. B. weil ein anderer Skill die Nummer belegt hat), die nächste freie Buchstaben-Variante (`03c`) wählen und im Schluss-Format vermerken.

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschließlich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `reports/_shell.html` aus Drive und baue daraus den Report:

- `{{TITLE}}` → `Wettbewerber-Realitäts-Check · <Kunde>`
- `{{EYEBROW}}` → `MTA-Wettbewerber · Realitäts-Check`
- `{{DISPLAY_NAME}}` → `Wettbewerber-Realitäts-Check: <Kunde>`
- `{{META_LINE}}` → `<N> Akteure verifiziert · Datenstand <Datum> · Generiert: <heute>`
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip** oben: Akteure gesamt, Anzahl `aktuell_stark`, Anzahl `latente_bedrohung`, Anzahl `nachrangig`, Anzahl Soll-Ist-Abweichungen.
  - **Sticky-TOC** zu den Sektionen.
  - **Summary-Card** mit dem Kernbefund (z. B. „Von 4 kundengenannten Wettbewerbern sind datenseitig 2 nachrangig; 1 nicht genannter Akteur ist aktuell_stark.").
  - **Klassifikations-Tabelle** (`table.data` bzw. `table.ratings`): Zeile pro Akteur — Name, Kategorie, Klasse als Badge (`aktuell_stark` → `badge stark`, `latente_bedrohung` → `badge mittel`, `nachrangig` → `badge schwach`), Kurz-Begründung. Eine `tr.total`-Zeile mit der Verteilung.
  - **Pro Akteur** ein `details.dim`-Block mit `data-rating` passend zur Klasse (`stark`/`mittel`/`schwach`), aufgeklappt für `aktuell_stark` und `latente_bedrohung`, zugeklappt für `nachrangig`. Inhalt: die vier Signal-Achsen, der Soll-Ist-Abgleich (Kunden-Einschätzung vs. Datenlage), der Begründungs-Satz.
  - **Soll-Ist-Sektion** mit den Abweichungs-Befunden als `.suggestion`-Blöcke (überschätzt / unterschätzt / latente Bedrohung übersehen).
  - **Auffälligkeiten-Block** unten als `.suggestion` — 2–3 strategie-relevante Beobachtungen.
- `{{TOKEN_FOOTER}}` → Skill-Counter (siehe Token-Tracking)
- `{{FOOTER_TEXT}}` → `MTA · <Kunde> · Wettbewerber-Realitäts-Check`

Lokal zusammenbauen, validieren, dann hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "03b-wettbewerber-realitaets-check.html" \
  ~/.cache/reachx-mta/"$SLUG"/03b-wettbewerber-realitaets-check.html "text/html"
```

### Schritt 9: Dashboard-Update

Lies `reports/index.html` aus Drive, modifiziere und schreibe per `upsert-text` zurück (`contracts.md` Abschnitt 7):

- Stat-Strip aktualisieren (Klassen-Verteilung ergänzen).
- "Erledigt"-Sektion erweitern um `02-05-wettbewerber-realitaets-check`.
- Reports-Liste um `03b-wettbewerber-realitaets-check.html` erweitern.
- "Nächster empfohlener Schritt" auf `02-03-wettbewerber-marken-profil` setzen.
- Sicherstellen, dass das `<body>`-Tag die Klasse `is-dashboard` trägt.

### Schritt 10: `status.md` aktualisieren

`status.md` liegt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe per `upsert-text` zurück (`contracts.md` Abschnitt 3):

- `02-05-wettbewerber-realitaets-check` in `schritte_done`, aus `schritte_offen` entfernen.
- Eigene Sektion in "✓ Erledigt" mit Datum, Output-Liste, Hinweisen (z. B. „2 kundengenannte Akteure datenseitig als nachrangig eingestuft").
- `naechster_empfohlen` → `02-03-wettbewerber-marken-profil` (profiliert nun die verifizierten relevanten Akteure).
- In "⊙ Auch jetzt möglich": `02-04-branchenportal-recherche` (braucht nur die `liste.md`).

### Schritt 11: Standard-Schlussformat im Chat

```
✓ 02-05-wettbewerber-realitaets-check abgeschlossen.

Outputs (auf Drive):
- wettbewerber/realitaets-check.md — Klassifikation + Soll-Ist je Akteur (ab jetzt die maßgebliche Wettbewerbs-Datenbasis)
- wettbewerber/realitaets-check.csv — Signal-Tabelle, eine Zeile pro Akteur
- reports/03b-wettbewerber-realitaets-check.html — visueller Report
Status aktualisiert in: status.md

Ergebnis:
- Akteure verifiziert:      <N>
- aktuell_stark:            <X>
- latente_bedrohung:        <Y>
- nachrangig:               <Z>
- Soll-Ist-Abweichungen:    <A>

[Wenn Abweichungen gefunden:]
⚠ Soll-Ist-Abweichungen:
- <Akteur> — vom Kunden als <Soll> genannt, datenseitig <Klasse>
- <Akteur> — latente Bedrohung, vom Kunden nicht erwähnt

[Wenn Reduced-Modus:]
ℹ Reduced-Modus: <welche MCPs fehlten> — Konfidenz bei <N> Akteuren niedrig.

Nächste Schritte:
1. 02-03-wettbewerber-marken-profil — profiliert die als aktuell_stark / latente_bedrohung verifizierten Akteure
2. (parallel möglich) 02-04-branchenportal-recherche — Portal-Präsenz aller Akteure

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/klassifikations-schema.md` — die regelbasierten Schwellen für die drei Klassen, die Signal-Punkte-Logik, die Einzugsradius-Defaults pro Branchen-Typ und das Soll-Ist-Mapping. **Verbindliche Quelle** für die Klassifikation.
- `reference/realitaets-check-schema.md` — Output-Format für `wettbewerber/realitaets-check.md` und `wettbewerber/realitaets-check.csv` (Spalten-Liste, Frontmatter-Felder, Body-Struktur).

## Edge Cases

- **`liste.md` hat 0 Akteure** → Skill bricht ab mit Hinweis: „Keine Akteure in liste.md — der Realitäts-Check braucht mindestens einen Akteur. Bitte 02-02 prüfen." Kein leerer Lauf.
- **Kunde ist national / Online-only** (`meta.json.region` ist „national"/„DACH"/„Online") → die GMB-Proximity-Achse ist für alle Akteure neutral. Die Klassifikation läuft dann über Sichtbarkeit, Paid und Marken-Stärke. Im Output-Frontmatter `lokale_achse_aktiv: false` und Hinweis im Body.
- **Kein einziger MCP erreichbar** (Sistrix, Ahrefs, Apify alle aus) → Reduced-Modus über die in `liste.md` vorhandenen Signale. Der Skill läuft, klassifiziert auf reduzierter Basis und setzt für alle Akteure `konfidenz: niedrig`. Im Schluss-Format deutlicher Hinweis, dass eine frische Erhebung die Klassifikation belastbarer machen würde. Kein Abbruch.
- **Akteur-Domain offline / 404** → Signal `website_marken_staerke: schwach`, andere Achsen so weit erhebbar. Solche Akteure tendieren zu `nachrangig` — außer ein kundengenannter mit `direkt`-Bedrohungsgrad, dann Soll-Ist-Befund „überschätzt / Akteur möglicherweise nicht mehr aktiv".
- **Sistrix-VI sehr klein (`< 0,05`)** → VI nur sekundär werten (Volatilitäts-Disziplin, `contracts.md` Abschnitt 13). Klassifikation primär über DR und lokale Signale, `sichtbarkeit_vi_konfidenz: niedrig` im Output.
- **Best-Practice-Akteur weit außerhalb des Einzugsgebiets** → fast immer `latente_bedrohung`, nicht `nachrangig` — er ist überregional stark und könnte lokal aufdrehen. Die Latente-Bedrohung-Frage greift hier zwingend.
- **`02-05` wird erneut aufgerufen** → bei vorhandenem `realitaets-check.md` einmalige Überschreiben/Backup/Abbruch-Frage (Schritt 1).
- **`liste.md` wurde nach dem ersten Realitäts-Check um Akteure ergänzt** → der Skill verifiziert beim Re-Run das vollständige Akteur-Set neu (keine inkrementelle Logik — der Realitäts-Check ist günstig genug für einen Voll-Lauf, und so bleibt die Klassifikation konsistent).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive (via `drive.py upsert-text`); Pfad-Angaben im Frontmatter bezeichnen die Sub-Folder relativ zum MTA-Drive-Root.
- Markdown + YAML-Frontmatter Hybrid-Format; Quellen-Kennzeichnung pro Zahl (`contracts.md` Abschnitt 13).
- Kundenaussagen sind Hypothesen — der Kunden-Bedrohungsgrad ist immer `briefing` (unverifiziert), die erhobenen Signale `erhoben` (`contracts.md` Abschnitt 13).
- Volatilitäts-Disziplin: Sistrix-VI bei Kleinstwerten nur sekundär (`contracts.md` Abschnitt 13).
- MCP-Health-Checks vor dem Lauf, Reduced-Modus mit Konfidenz-Flag bei fehlenden optionalen MCPs (`contracts.md` Abschnitt 11).
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (in-place auf Drive).
- HTML-Reports basieren auf `reports/_shell.html` (aus Drive geladen), `{{MAIN_CONTENT}}` nur aus kanonischen Bausteinen, Pflicht-Validierung vor Upload.
- Standard-Schlussformat im Chat.
- Die Outputs dieses Skills sind ab hier die maßgebliche Wettbewerbs-Datenbasis — Folge-Skills lesen `realitaets-check.md` für die Bedrohungs-Klassifikation.
