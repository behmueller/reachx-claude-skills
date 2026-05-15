---
name: 01-02-kickoff-transcript-parser
description: Wandelt ein Kickoff-Meeting-Transkript (Fireflies-Markdown, Gemini-Export, Plaud-Zusammenfassung) in das strukturierte MTA-Briefing (data/briefing.md plus reports/01-briefing.html). Nutze diesen Skill IMMER, wenn der Nutzer im Kontext einer laufenden MTA ein Transkript verarbeiten will - auch bei Phrasen wie "Parse das Kickoff-Transkript", "Briefing aus dem Transkript ziehen", "Werte das Kickoff-Meeting aus", "lies das Meeting-Protokoll", "extrahiere das Briefing", "verarbeite das Transkript für [Kunde]". Auch dann nutzen, wenn der Nutzer einen Dateipfad zu einem .md/.txt/.docx mit Meeting-Inhalten nennt und sich auf eine MTA bezieht. Der Skill setzt voraus, dass 01-01-mta-projekt-init bereits gelaufen ist und meta.json im Projektordner existiert - bricht sonst mit Hinweis ab.
---

# Kickoff-Transcript-Parser

Extrahiert aus einem Kickoff-Meeting-Transkript das strukturierte Briefing für die laufende MTA. Schreibt `data/briefing.md` mit YAML-Frontmatter plus Narrativ, generiert einen HTML-Report im REACHX-Branding und aktualisiert den Projekt-Status.

Das ist der **größte Effizienz-Hebel im MTA-Prozess**: heute extrahiert der Stratege die Insights manuell aus 60–90-Minuten-Meetings. Dieser Skill macht das in einem Lauf — mit klaren Markierungen, wo Lücken bestehen.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
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

## Wann triggern

- "Parse das Kickoff-Transkript"
- "Briefing aus dem Transkript ziehen"
- "Verarbeite das Kickoff-Meeting für [Kunde]"
- "Extrahiere das Briefing aus [Datei]"
- "Werte das Kickoff aus"
- Nutzer nennt einen Dateipfad zu einem Meeting-Transkript (.md, .txt, .docx) im Kontext der laufenden MTA

## Eingang

| Parameter | Pflicht | Beschreibung |
|---|---|---|
| Transkript-File | ja | Liegt im Drive-Sub-Folder `input/transkripte/` (Fireflies-Markdown, Plaud-DOCX-Zusammenfassung, TXT oder VTT). Der Stratege legt es vor dem Skill-Aufruf dort ab. |
| MTA-Slug | nein | Auto-Detect aus dem Active-MTA-Cache, oder explizit übergeben |
| Transkript-Dateiname | nein | Wenn mehrere Files in `input/transkripte/` liegen: konkreter Dateiname, sonst nimmt der Skill das jüngste File und fragt bei Mehrdeutigkeit nach |

**Pre-Step beim Strategen (außerhalb des Skills):** Transkript-Datei in den MTA-Drive-Folder unter `input/transkripte/` hochladen — per Drive-Web-UI (Drag&Drop), gws CLI (`gws drive files create --upload ...`) oder Google-Drive-Desktop. Der Skill liest die Datei dann aus Drive, parst sie und schreibt das Briefing zurück nach `data/`.

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

Der Skill nutzt den Active-MTA-Cache von `01-01-mta-projekt-init`, um den Drive-Folder der aktiven MTA zu finden:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

# MTA-Slug aus User-Eingabe oder Active-Cache
MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  # Mehrere MTAs? Liste anzeigen und User fragen
  python3 "$DRIVE_PY" list-mtas
  echo "✗ MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen oder Slug angeben."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

# meta.json aus Drive lesen
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

SLUG=$(jq -r '.projekt_slug' /tmp/meta.json)
SCHEMA_VERSION=$(jq -r '.schema_version' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
TRANSKRIPTE_ID=$(jq -r '.drive.input_subfolders.transkripte // empty' /tmp/meta.json)
```

**Schema-Version-Check:** Wenn `TRANSKRIPTE_ID` leer ist (Schema 2.0 ohne `input/transkripte/`), abbrechen mit:

```
✗ MTA-Projekt läuft auf Schema 2.0, dieser Skill benötigt 2.1.
Bitte 01-01-mta-projekt-init im Resume-Modus erneut aufrufen — er ergänzt
den Sub-Folder `input/transkripte/` automatisch und hebt das Schema.
Danach diesen Skill wiederholen.
```

### Schritt 1: Voraussetzungs-Check und Idempotenz

Wenn `META_ID` leer ist (keine `meta.json` im Drive-Folder gefunden):

```
✗ Kein gültiger MTA-Folder.
Bitte 01-01-mta-projekt-init mit der Drive-URL des MTA-Ordners aufrufen.
```

Prüfe, ob das Transkript bereits verarbeitet wurde — eine `briefing.md` im `data/`-Sub-Folder:

```bash
EXISTING=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "briefing.md") | .id')
```

Wenn vorhanden, frage:

- **Überschreiben** (vorherige `briefing.md` auf Drive überschreiben — wenn versionierte Backups gewünscht: vorher als `briefing.backup-<timestamp>.md` per `upsert-text` ablegen)
- **Append** (zweites Meeting an dasselbe Briefing anhängen — Felder werden ergänzt, nicht ersetzt)
- **Abbrechen**

### Schritt 2: Transkript-File aus Drive auswählen und runterladen

Liste die Files in `input/transkripte/` und wähle das richtige aus:

```bash
TRANSKRIPTE_FILES=$(python3 "$DRIVE_PY" list-children "$TRANSKRIPTE_ID")
ANZAHL=$(echo "$TRANSKRIPTE_FILES" | jq 'length')

if [ "$ANZAHL" = "0" ]; then
  cat <<MSG
✗ Keine Transkripte im Drive-Sub-Folder gefunden.
Bitte das Meeting-Transkript (Fireflies-MD, Plaud-DOCX, TXT oder VTT) in
   <MTA-Folder>/input/transkripte/
auf Drive ablegen und den Skill erneut aufrufen.
MSG
  exit 1
fi
```

**File-Auswahl:**

- **Genau ein File:** automatisch nehmen, im Chat melden ("Transkript erkannt: `<name>`").
- **Mehrere Files & explizit übergebener Dateiname:** das angegebene File nehmen. Wenn nicht vorhanden: Liste ausgeben und nachfragen.
- **Mehrere Files & kein Name übergeben:** die Top-3 nach `modifiedTime desc` ausgeben und nachfragen, welches verarbeitet werden soll. Niemals raten.

Lade das gewählte File in den lokalen Cache:

```bash
mkdir -p ~/.cache/reachx-mta/"$SLUG"/transkripte
FILE_ID=$(echo "$TRANSKRIPTE_FILES" | jq -r '.[] | select(.name == "<gewaehlter-name>") | .id')
FILE_NAME=$(echo "$TRANSKRIPTE_FILES" | jq -r '.[] | select(.id == "'"$FILE_ID"'") | .name')
python3 "$DRIVE_PY" read "$FILE_ID" > ~/.cache/reachx-mta/"$SLUG"/transkripte/"$FILE_NAME"
TRANSKRIPT_LOCAL=~/.cache/reachx-mta/"$SLUG"/transkripte/"$FILE_NAME"
```

`TRANSKRIPT_LOCAL` ist der lokale Cache-Pfad für die Verarbeitung — das Drive-Original bleibt unverändert. Im Briefing-Frontmatter trägst du in `transkript_quelle` die **Drive-File-ID + Drive-URL** ein (nicht den Cache-Pfad — das wäre nicht reproduzierbar für andere Kollegen).

**Format erkennen** anhand des Dateinamens und/oder des ersten Inhalt-Blocks:

| Erkennungsmuster | Format | Parser |
|---|---|---|
| `**Name** *[MM:SS]*: Text` | Fireflies-Markdown / Gemini-via-Meet | `scripts/parse_fireflies_md.py` |
| `[HH:MM:SS] Name: Text` oder VTT-Cues | WebVTT / SRT | (zukünftig — derzeit Fallback auf Plaintext-Modus) |
| Strukturierter DOCX-Bericht (Plaud) | Plaud.ai-Zusammenfassung | Lies als reinen Text, behandle wie strukturierten Bericht (kein Speaker-Diarisation) |
| Reiner Fließtext | TXT / Copy-Paste | Plaintext-Modus, kein Speaker-Mapping |

Wenn das Format `Fireflies-Markdown` ist, rufe `python3 scripts/parse_fireflies_md.py "$TRANSKRIPT_LOCAL" --json` auf und nutze den strukturierten Output (`meta` + `turns`).

Für andere Formate: lies die Datei direkt und behandle den Inhalt als unstrukturierten Text — die Extraktion läuft dann ohne Speaker-Tags.

### Schritt 3: Meeting-Typ klassifizieren

Bestimme den Meeting-Typ anhand der Signale im **Extraktions-Leitfaden** (`reference/extraktions-leitfaden.md`):

- `kickoff_extern` — Kunde und Agentur am Tisch
- `briefing_intern` — Agentur-interne Zusammenfassung
- `verkaufsgespraech` — Erstkontakt vor MTA-Beauftragung
- `unklar`

Setze gleichzeitig `speaker_verlaesslich`: wenn ein einzelner Sprecher >80 % Wortanteil hat oder andere Hinweise auf Speaker-Merging vorliegen, dann `false` — dann arbeite **inhaltsbasiert**, nicht speaker-tag-basiert.

### Schritt 4: Inhaltliche Extraktion

Folge der Reihenfolge im Extraktions-Leitfaden:

1. Produkte und Dienstleistungen
2. Zielgruppen und Regionen
3. Ziele und KPIs
4. USPs (eigenwahrnehmung) — **nur was der Kunde selbst sagt**, mit Beleg
5. Wettbewerber (mit Bedrohungsgrad-Klassifikation)
6. Tools des Kunden
7. Budget-Hinweise
8. No-Gos
9. Stakeholder-Inventar (aus Vorstellungsrunden im Inhalt, nicht aus Speaker-Tags wenn unzuverlässig)
10. Offene Punkte

Lies das vollständige Schema und alle Feld-Erläuterungen aus:

- `reference/briefing-schema.md` — Output-Format
- `reference/extraktions-leitfaden.md` — Wie extrahiert wird, inkl. Off-Topic-Filter und Edge Cases

Markiere unsichere Werte mit `unklar_aus_transkript: true`. Erfinde nichts, was nicht im Transkript steht.

### Schritt 5: Qualitäts-Indikatoren setzen

- `inhaltliche_dichte`: hoch / mittel / niedrig
- `extraktion_vollstaendig`: true wenn alle Pflichtfelder belegt, false sonst
- `extraktion_lücken`: konkrete Liste fehlender oder unklarer Felder

Wenn `inhaltliche_dichte: niedrig` ist oder mehr als 3 Felder als `unklar_aus_transkript: true` markiert sind, schreibe die im Leitfaden definierte **Empfehlungs-Notiz** prominent unter "Offene Punkte" im Body.

### Schritt 6: `data/briefing.md` schreiben

Baue das Briefing lokal im Cache zusammen und lade es nach Drive in den `data/`-Sub-Folder hoch. YAML-Frontmatter mit allen strukturierten Feldern, Markdown-Body mit den Sektionen aus dem Schema (Übersicht, Ziele und KPIs, Zielgruppen und Markt, Produkte und USPs, Wettbewerb, Tooling und Budget, Offene Punkte).

```bash
mkdir -p ~/.cache/reachx-mta/"$SLUG"
# briefing.md lokal aufbauen
cat > ~/.cache/reachx-mta/"$SLUG"/briefing.md <<'EOF'
<frontmatter + body>
EOF
# Nach Drive
python3 "$DRIVE_PY" upsert-text "$DATA_ID" "briefing.md" \
  ~/.cache/reachx-mta/"$SLUG"/briefing.md "text/markdown"
```

Im Body: nutze konkrete Belege/Zitate aus dem Transkript, wo es die Aussagekraft erhöht. Halte Zitate kurz (unter 25 Wörtern), markiere sie mit Anführungszeichen und Timestamp.

### Schritt 7: HTML-Report erzeugen

Erzeuge `01-briefing.html` und lade ihn in den `reports/`-Sub-Folder auf Drive:

1. Lies `reports/_shell.html` aus Drive (`drive.py read <id>` — die Shell-File-ID via `list-children` auf den reports-Folder ermitteln) als Ausgangspunkt
2. Fülle die Platzhalter:
   - `{{TITLE}}` → `Briefing · <Kunde>`
   - `{{EYEBROW}}` → `MTA-Briefing aus Kickoff`
   - `{{DISPLAY_NAME}}` → `Briefing: <Kunde>`
   - `{{META_LINE}}` → `Quelle: <Meeting-Titel> · <Meeting-Datum> · Generiert: <heute>`
   - `{{MAIN_CONTENT}}` → Render der Briefing-Inhalte als strukturiertes HTML (siehe unten)
   - `{{FOOTER_TEXT}}` → `MTA · <Kunde> · Briefing aus Kickoff-Transkript`

**Render-Regeln für `{{MAIN_CONTENT}}`:**

- Sticky-TOC mit Links zu allen Hauptsektionen
- Übersichts-Sektion mit `.summary-card` (Meeting-Typ, Meeting-Datum, Speaker-Anzahl, inhaltliche Dichte als Badge)
- Eine `<section>` pro Feldgruppe (Ziele, USPs, Wettbewerber, …)
- Bei jedem extrahierten Eintrag, wenn `unklar_aus_transkript: true`, ein `.badge.mittel` mit Text "unklar"
- "Offene Punkte"-Sektion zuletzt, bei niedriger Dichte als prominenter `.suggestion`-Block

Verfügbare CSS-Klassen siehe Kommentar oben im `_shell.html` oder `contracts.md` Abschnitt 7.

Den fertigen Report lokal in `~/.cache/reachx-mta/<slug>/01-briefing.html` zusammenbauen und dann nach Drive hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "01-briefing.html" \
  ~/.cache/reachx-mta/"$SLUG"/01-briefing.html "text/html"
```

### Schritt 8: Dashboard-Update

Aktualisiere `reports/index.html` auf Drive:

```bash
INDEX_ID=$(python3 "$DRIVE_PY" list-children "$REPORTS_ID" | jq -r '.[] | select(.name == "index.html") | .id')
python3 "$DRIVE_PY" read "$INDEX_ID" > ~/.cache/reachx-mta/"$SLUG"/index.html
# ... HTML modifizieren (Stat-Strip, Erledigt-Sektion, Reports-Liste, Nächster Schritt) ...
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "index.html" \
  ~/.cache/reachx-mta/"$SLUG"/index.html "text/html"
```

Inhaltliche Updates:
- Stat-Strip: "Erledigt"-Zähler hochsetzen
- "Erledigt"-Sektion: Eintrag für `01-02-kickoff-transcript-parser` ergänzen mit Link auf `01-briefing.html`
- "Nächster empfohlener Schritt": `02-01-kunden-marken-profil` setzen (oder `02-02-wettbewerber-identifikation`, je nach `inhaltliche_dichte`)
- "Reports"-Sektion: Link auf `01-briefing.html` hinzufügen

### Schritt 9: `status.md` aktualisieren

`status.md` liegt direkt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe zurück:

```bash
STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > ~/.cache/reachx-mta/"$SLUG"/status.md
# ... Frontmatter und Body anpassen ...
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" \
  ~/.cache/reachx-mta/"$SLUG"/status.md "text/markdown"
```

Nach den Regeln aus `contracts.md` (Abschnitt 3):

- `01-02-kickoff-transcript-parser` zu `schritte_done` (Frontmatter) und in "✓ Erledigt"-Sektion (Body)
- Aus `schritte_offen` entfernen
- `naechster_empfohlen` setzen
- Bei niedriger inhaltlicher Dichte: einen Eintrag in `blockiert` (Frontmatter) mit Begründung *"Briefing-Lücken — Stratege sollte mit Kunde nachhaken, bevor weitere Skills laufen"*

### Schritt 10: Standard-Schlussformat im Chat

```
✓ 01-02-kickoff-transcript-parser abgeschlossen.

Outputs (auf Drive):
- data/briefing.md — strukturiertes Briefing mit YAML-Frontmatter
- reports/01-briefing.html — visueller Report für den Strategen
Status aktualisiert in: status.md

Meeting-Typ:  <kickoff_extern | briefing_intern | verkaufsgespraech>
Dichte:       <hoch | mittel | niedrig>
Lücken:       <Anzahl Felder mit unklar_aus_transkript: true>

[Bei niedriger Dichte oder Lücken >3:]
Offene Punkte:
- <Liste der wichtigsten Lücken>

Empfehlung: vor weiteren Skills mit dem Kunden klären.

Nächste Schritte:
1. 02-01-kunden-marken-profil — Markenprofil aus der Website erstellen (empfohlen)
2. (parallel möglich) 02-02-wettbewerber-identifikation — Wettbewerber finden auf Basis der bisher genannten Konkurrenten

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/briefing-schema.md` — vollständiges Output-Schema mit Feld-Erläuterungen
- `reference/extraktions-leitfaden.md` — wie aus dem Transkript extrahiert wird, inkl. Meeting-Typ-Klassifikation, Off-Topic-Filter, USP-Regeln, Speaker-Verlässlichkeit
- `scripts/parse_fireflies_md.py` — Parser für Fireflies-Markdown-Transkripte (auch Gemini-Exports). Liefert strukturierte Meta + Turn-Liste als JSON.

## Edge Cases

- **Speaker-Erkennung unzuverlässig** (1 Sprecher >80%) → `speaker_verlaesslich: false`, inhaltsbasiert klassifizieren, im HTML-Report Hinweis-Block
- **Mehrere Meetings für dasselben Kunden** → Append-Modus in Schritt 1, Felder werden ergänzt nicht ersetzt; Quelle pro Eintrag im `quelle_turn`-Feld behalten
- **Verkaufsgespräch statt Kickoff** (siehe Casafan) → trotzdem extrahieren, Meeting-Typ entsprechend setzen, mit Hinweis auf reduzierte Briefing-Dichte
- **Plaud.ai-Zusammenfassung statt Transkript** → keine Speaker-Diarisation, Extraktion läuft auf Text-Inhalt; `transkript_quelle.anzahl_turns` auf 0, `sprecher_erkannt` leer lassen
- **Off-Topic-Anteil hoch** (Small Talk, Tool-Probleme) → wegfiltern bei Extraktion, Transkript selbst bleibt unverändert
- **Mehrere Sprache im Meeting** (Deutsch + Englisch, häufig bei Tech-Themen) → kein Problem, Extraktion sprachenagnostisch
- **Transkript erkennbar lückenhaft** (Audio-Aussetzer, "[unverständlich]"-Markierungen) → betroffene Bereiche bei Quelle markieren, im Notfall `extraktion_lücken` ergänzen

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich — insbesondere:

- Outputs leben in Google Drive (über `drive.py upsert-text`), nicht im lokalen Filesystem
- **Transkript-Quelle liegt auf Drive** in `input/transkripte/` — der Stratege legt das File vor dem Skill-Aufruf dort ab. In `transkript_quelle.drive_file_id` und `transkript_quelle.drive_url` werden die Drive-Referenzen festgehalten (kein lokaler Pfad — der lokale Cache ist nur Arbeits-Kopie, nicht reproduzierbar zwischen Kollegen)
- `input/`-Sub-Folder werden **nie** vom Skill geschrieben — sie sind reine Lese-Quelle
- Markdown + YAML-Frontmatter Hybrid-Format
- Standard-Schlussformat im Chat
- `status.md` und Dashboard `index.html` werden in jedem Lauf aktualisiert (in-place Update auf Drive via `upsert-text`)
