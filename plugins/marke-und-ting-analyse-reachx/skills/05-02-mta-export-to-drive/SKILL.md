---
name: 05-02-mta-export-to-drive
description: Erstellt am Ende einer abgeschlossenen MTA ein finales ZIP-Archiv aller MTA-Outputs und legt es als versionierte Final-Version im Kunden-Folder ab (eine Ebene über dem MTA-Folder im REACHX Shared Drive). Optional auch: PDF-Renderings der HTML-Reports. Nutze diesen Skill IMMER, wenn der Nutzer eine MTA abschließen und einen kompletten Export für Archiv oder Strategen-Übergabe erstellen will - auch bei Phrasen wie "MTA abschließen", "Final-Export bauen", "ZIP-Archiv erzeugen", "Strategen-Paket bauen", "MTA fertig", "Export für Übergabe", "MTA archivieren", "MTA-Snapshot erstellen". Letzter Skill in der MTA-Pipeline.
---

# MTA-Export-to-Drive (Final-ZIP)

Letzter Skill in der MTA-Pipeline. Da seit Schema 2.0 (2026-05-14) alle MTA-Outputs bereits live auf Google Drive liegen, ist der ursprüngliche Sinn dieses Skills (lokale Files → Drive hochladen) entfallen. Stattdessen hat der Skill jetzt eine neue, sinnvolle Rolle: er bündelt die fertige MTA als **versioniertes ZIP-Archiv** und legt es **eine Ebene über dem MTA-Folder** ab — also direkt im Kunden-Folder, damit der Stratege ein klares "MTA finalisiert am DATUM"-Artefakt hat.

> **Hinweis:** Dieser Skill wurde im Schema-2.0-Wechsel umgewidmet. Die alte Implementierung (MCP-Routing, gws-Fallback, Drive-API, Reduced-Modus) ist obsolet — alle Outputs werden über `drive.py` (gws CLI) abgewickelt. Die `reference/`-Files (`drive-mapping.md`, `drive-tools-mapping.md`, `export-output-schema.md`) sind teilweise veraltet — die neue Logik unten ist die Quelle der Wahrheit.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-techniker`**-Subagent (Haiku 4.5). Reine Mechanik (Drive-Listing, ZIP-Packen, Upload), keine inhaltliche Bewertung. Der Hauptthread orchestriert (Bestätigungs-Stopp vor Final-Export), der Subagent macht die Mechanik schnell und günstig.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-techniker"`
- Übergabe: MTA-Slug
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

- "MTA abschließen"
- "Final-Export für KUNDE"
- "ZIP-Archiv der MTA erzeugen"
- "MTA archivieren"
- "Strategen-Paket bauen"
- "MTA-Snapshot erstellen"
- "MTA fertig — was jetzt"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA im lokalen Active-MTA-Cache registriert, `meta.json` im Drive-MTA-Folder vorhanden
- `gws` CLI installiert und authentifiziert
- Empfohlen: möglichst viele Stufe-1/2/3/4-Skills durchgelaufen — Skill exportiert allerdings auch lückenhafte MTAs (warnt deutlich)

## Ablauf

### Schritt 0: MTA-Kontext laden

Standard-Pattern (siehe `01-01-mta-projekt-init/reference/contracts.md` Abschnitt 1):

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  echo "✗ MTA nicht registriert. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
SLUG=$(jq -r '.projekt_slug' /tmp/meta.json)
KUNDE=$(jq -r '.kunde' /tmp/meta.json)
```

Lies auch `status.md` aus dem MTA-Root (`find_by_name` → `read`) und extrahiere `schritte_done` und `schritte_offen` aus dem Frontmatter — wird in Schritt 5 für den Schluss-Report genutzt.

### Schritt 1: Alle Files im MTA-Folder rekursiv listen

Walk durch alle Sub-Folders auf Drive und sammle die kompletten Datei-Metadaten (Name, ID, MIME-Type, Größe, Pfad innerhalb der MTA). Pseudo-Logik:

```bash
# Root-Level Files (meta.json, status.md, reports/, etc.)
python3 "$DRIVE_PY" list-children "$FOLDER_ID" > /tmp/mta-root.json

# Pro Sub-Folder rekursiv listen
for sub in data wettbewerber audits synthese reports assets; do
  SUB_ID=$(jq -r ".drive.subfolders.$sub" /tmp/meta.json)
  python3 "$DRIVE_PY" list-children "$SUB_ID" > "/tmp/mta-$sub.json"
  # für reports/slides/ ggf. weiter rekursiv
done
```

Sammle Inventur-Tabelle: pro File `lokaler_zielpfad_im_zip`, `drive_id`, `mime_type`, `size_bytes`.

**Lücken-Check**: vergleiche gegen Pflicht-Files aus `contracts.md` Abschnitt 5 (z.B. `data/briefing.md`, `data/kunde.md`, etc.) — wenn Schlüssel-Files fehlen, sammle Auffälligkeit `pflicht_outputs_fehlen` für den Schluss-Report.

### Schritt 1a: De-Duplication-Pass — Re-Run-Artefakte entfernen

Bevor exportiert wird, den MTA-Folder-Baum auf **Duplikat-Dateien gleichen Namens** prüfen. Bei wiederholten Skill-Läufen und paralleler Bearbeitung entstehen auf Drive Konflikt-Kopien (`status (1).md`, `kanal-chancen (1).md`, `forecast (2).xlsx`) — diese würden sonst doppelt ins ZIP wandern und den Export verwässern.

Pro Sub-Folder aus der Inventur (Schritt 1) die `name`-Felder auf Kollisionen prüfen — sowohl exakte Namensgleichheit als auch das Drive-Konflikt-Muster `<basisname> (N).<ext>`:

```bash
# Pro Sub-Folder: Dateien gruppieren, Konflikt-Kopien identifizieren
python3 "$DRIVE_PY" list-children "$SUB_ID" | jq -r '.[] | "\(.name)\t\(.id)\t\(.modifiedTime)"'
```

Pro erkannter Duplikat-Gruppe (z. B. `status.md` + `status (1).md`):

- Die **aktuellste** Version behalten — die mit dem jüngsten `modifiedTime`. Bei der `(N)`-Variante ist es meist die Konflikt-Kopie; verlässlicher ist `modifiedTime`.
- Die veraltete(n) Datei(en) entfernen: `python3 "$DRIVE_PY" delete "<file-id-der-alten-version>"`.
- Jede Löschung im Schluss-Report unter Auffälligkeit `re_run_duplikat_entfernt` festhalten (Dateiname, behaltene vs. gelöschte Version-ID).

**Vorsicht:** Nur eindeutige Re-Run-Artefakte löschen — Dateien, die sich nur durch den Drive-`(N)`-Suffix oder exakt gleichen Namen unterscheiden. Inhaltlich verschiedene Dateien (z. B. `wettbewerber/alpha.md` und `wettbewerber/beta.md`) sind keine Duplikate. Im Zweifel die Datei behalten und im Schluss-Report als `dedup_unklar` melden, statt blind zu löschen.

Auch den **Kunden-Folder** (Parent des MTA-Folders, siehe Schritt 5) auf alte `mta-<slug>-final-*.zip`-Snapshots prüfen — die werden **nicht** automatisch gelöscht (Versionierung über Timestamp ist gewollt), aber im Schluss-Report wird die Anzahl vorhandener Alt-Snapshots gemeldet, damit der Stratege bei Bedarf aufräumt.

Nach dem De-Duplication-Pass die Inventur aus Schritt 1 mit dem bereinigten Stand neu aufbauen.

### Schritt 2: Bestätigungs-Stopp

Bevor irgendetwas heruntergeladen oder gezippt wird:

```
Final-Export für MTA "<KUNDE>" vorbereiten:
- Drive-Folder:    <Folder-URL>
- Slug:            <slug>
- Files insgesamt: NN
- Größe geschätzt: XX MB
- Erledigt:        <Liste aus status.md schritte_done>
- Offen:           <Liste aus status.md schritte_offen — falls vorhanden, betone, dass Export trotzdem läuft>

ZIP-Archiv landet im Kunden-Folder (eine Ebene über der MTA) als:
  mta-<slug>-final-<YYYY-MM-DDTHHMM>.zip

OK so?
```

Bei "ja"/"passt"/"leg an": weiter. Bei "nein": Skill abbrechen, kein Side-Effect.

### Schritt 3: Files lokal herunterladen

Lege das lokale Zielverzeichnis an:

```bash
EXPORT_DIR="$HOME/.cache/reachx-mta/$SLUG/export"
mkdir -p "$EXPORT_DIR"
```

Pro File aus der Inventur (Schritt 1):

```bash
python3 "$DRIVE_PY" read "<file-id>" > "$EXPORT_DIR/<zielpfad-im-zip>"
# Für Sub-Folders: mkdir -p vor dem Read
```

Erhalte die MTA-Struktur exakt im lokalen Spiegel (`meta.json`, `status.md` im Root; `data/`, `wettbewerber/`, `audits/`, `synthese/`, `reports/`, `assets/` als Sub-Folders inkl. ggf. `reports/slides/`).

**Edge Case**: Bei großen Files (>50 MB pro File, z.B. Apify-Roh-Caches) — direkt Streamen via `drive.py read`. Wenn Total-Größe > 2 GB → Auffälligkeit `rohdaten_zu_gross`, im Schluss-Report erwähnen.

Falls `drive.py` keinen `read` für Binärdaten kann, nutze ergänzend `gws drive files download` direkt.

### Schritt 4: ZIP-Archiv erstellen

```bash
TIMESTAMP=$(date -u +%Y-%m-%dT%H%M)
ZIP_NAME="mta-${SLUG}-final-${TIMESTAMP}.zip"
ZIP_PATH="$HOME/.cache/reachx-mta/$SLUG/$ZIP_NAME"

cd "$EXPORT_DIR"
zip -r "$ZIP_PATH" .
```

Schreibe zusätzlich eine `FINAL-EXPORT-INFO.md` mit den wichtigsten Metadaten ans Root der ZIP (Kunde, Slug, Datum, Drive-Folder-URL, Erledigt-Liste, Offen-Liste, Größe, Anzahl Files) — ähnlich der Pflicht-README im Original-Skill, aber kompakter, weil die ZIP der Stratege ohnehin auspackt.

### Schritt 5: ZIP nach Drive hochladen — in den Kunden-Folder

Der Kunden-Folder ist **der Parent des MTA-Folders**. Den ermitteln:

```bash
KUNDE_FOLDER_ID=$(python3 "$DRIVE_PY" get-file-metadata "$FOLDER_ID" | jq -r '.parents[0]')
# Falls drive.py keinen get-file-metadata hat, direkt via gws:
# KUNDE_FOLDER_ID=$(gws drive files get --params "{\"fileId\": \"$FOLDER_ID\", \"fields\": \"parents\"}" | jq -r '.parents[0]')
```

ZIP hochladen via `gws drive files create` (resumable Upload für große Dateien) — die Datei ist binär, also nicht via `drive.py upsert-text`, sondern direkt:

```bash
gws drive files create \
  --params "{\"fields\": \"id,name,webViewLink\"}" \
  --media "$ZIP_PATH" \
  --json "{\"name\": \"$ZIP_NAME\", \"parents\": [\"$KUNDE_FOLDER_ID\"]}"
```

Drive-View-Link aus der Response für den Schluss-Report extrahieren.

**Versionierung**: ZIP-Name enthält ISO-Timestamp — beim erneuten Lauf wird kein Konflikt erzeugt, sondern eine neue Datei daneben. Stratege kann ältere Final-Exports nach Bedarf löschen.

### Schritt 6: Skill-Report, Dashboard und status.md aktualisieren

#### 6.1: HTML-Report (auf Drive, im MTA-Folder)

Generiere `reports/<NN>-final-export.html` (NN = nächste freie Nummer). Inhalte:

- Stat-Strip: Files-Total, ZIP-Größe, Erledigt-Quote (`schritte_done` / total Skills), Datum
- Großer Hero-CTA: "→ Final-ZIP im Kunden-Folder öffnen" (Drive-View-Link)
- Tabelle aller im ZIP enthaltenen Files (Pfad, Größe)
- Auffälligkeiten-Block, falls vorhanden (Lücken aus Schritt 1)

Lade hoch via `drive.py upsert-text "$REPORTS_ID" "NN-final-export.html" /tmp/report.html "text/html"`.

#### 6.2: Dashboard-Update

`reports/index.html` aus Drive lesen, aktualisieren, zurückschreiben:

- `05-02-mta-export-to-drive` in Erledigt-Liste
- Großer Hero-Banner: "MTA finalisiert — Final-ZIP im Kunden-Folder verfügbar" mit Link
- `naechster_empfohlen`: leer / "MTA abgeschlossen"

#### 6.3: `status.md` aktualisieren

Nach Regeln aus `contracts.md` Abschnitt 3:

- `05-02-mta-export-to-drive` in `schritte_done`
- Eigene Sektion "✓ Erledigt" mit Datum, ZIP-Name, Drive-Link
- `naechster_empfohlen`: `MTA abgeschlossen — Übergabe an Strategen`

### Schritt 7: Standard-Schlussformat im Chat

```
✓ 05-02-mta-export-to-drive abgeschlossen — MTA finalisiert.

Final-Export (im Kunden-Folder, eine Ebene über der MTA):
- ZIP-Name:     mta-<slug>-final-<timestamp>.zip
- Drive-Link:   <webViewLink>
- Größe:        XX,X MB
- Files:        NN

Outputs (im MTA-Folder auf Drive):
- reports/<NN>-final-export.html — Skill-Report
Status aktualisiert in: status.md

[Wenn Auffälligkeiten:]
⚠ Hinweise:
- (z.B. pflicht_outputs_fehlen: data/briefing.md fehlt — Export trotzdem erstellt)
- (rohdaten_zu_gross: assets/ war > 2 GB, ausgelassen)

Nächste Schritte:
1. MTA-Pipeline abgeschlossen — Strategen-Übergabe via Drive-Link versenden.
2. (optional) PDFs aus den HTML-Reports rendern (separater manueller Schritt).

Sag mir, wenn du noch was anpassen willst.
```

## Optionale Erweiterung: PDF-Renderings

Optional kann der Skill am Ende alle HTML-Reports im MTA als PDFs rendern (via headless Chromium / Browser-Print-API) und zusätzlich ein `reports-pdf/`-Verzeichnis ins ZIP packen. Dieser Schritt ist nicht implementiert in der ersten Version — er kann später ergänzt werden, wenn der Stratege gedruckte Versionen will.

## Auffälligkeiten

| Typ | Auslöser | Bedeutung |
|---|---|---|
| `pflicht_outputs_fehlen` | Mind. 1 Stufe-3/4-Pflicht-Output fehlt im MTA-Folder | MTA inhaltlich lückenhaft — Hinweis im Final-Export |
| `rohdaten_zu_gross` | `assets/` insgesamt > 2 GB | Im ZIP nur Manifest, nicht die Raw-Files |
| `schema_vorlauf_nicht_bestaetigt` | Mind. 1 Schema-File mit `status: vorgeschlagen` | Stratege sollte vor Übergabe bestätigen |
| `re_run_duplikat_entfernt` | De-Duplication-Pass (Schritt 1a) hat eine Konflikt-Kopie / Re-Run-Artefakt gelöscht | Veraltete Version entfernt, nur die aktuelle bleibt im Export |
| `dedup_unklar` | Zwei Dateien mit kollidierendem Namen, Aktualität nicht eindeutig | Beide behalten, Stratege soll manuell prüfen |
| `upload_fehlgeschlagen` | ZIP-Upload nach Drive scheitert | Lokales ZIP unter `~/.cache/reachx-mta/<slug>/` für manuellen Upload |

## Bundled Resources

- `reference/drive-mapping.md` — historisch (Schema-1.0-Mapping lokal → Drive). Veraltet, nur als Referenz erhalten.
- `reference/drive-tools-mapping.md` — historisch (MCP/gws/API-Routing). Veraltet, der neue Skill nutzt ausschließlich `drive.py` (gws).
- `reference/export-output-schema.md` — historisch (Manifest-Schema). Veraltet — die neue Logik schreibt nur eine kompakte `FINAL-EXPORT-INFO.md` ins ZIP.

Bei späterem Refactoring können die `reference/`-Files konsolidiert oder gelöscht werden.

## Edge Cases

- **MTA-Folder hat keinen Parent (steht direkt im Drive-Root)**: dann ZIP im MTA-Folder selbst ablegen statt im Kunden-Folder, Hinweis im Schluss-Report.
- **ZIP-Größe > 2 GB**: resumable Upload via `gws drive files create` mit Streaming. Bei Timeout: lokales ZIP behalten, manueller Upload-Hinweis.
- **Drive-Quota erreicht**: 429/403-Fehler beim Upload — ZIP bleibt lokal, Hinweis im Chat: "Lokales ZIP: ~/.cache/reachx-mta/<slug>/<zip-name>. Bitte später manuell hochladen."
- **Re-Run**: Skill kann mehrfach laufen, jedes Mal wird eine neue Versions-ZIP mit aktuellem Timestamp angelegt. Stratege räumt veraltete Snapshots manuell auf.
- **Unvollständige MTA**: Skill bricht NICHT ab — exportiert was da ist, warnt im Final-Export und im Schluss-Format via `pflicht_outputs_fehlen`.
- **`drive.py` hat keinen `read` für Binärdaten**: ergänzend `gws drive files download --fileId <id> --media-path <path>` nutzen.

## Wichtige Konventionen

Alle in `01-01-mta-projekt-init/reference/contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive — gelesen/geschrieben via `drive.py` (Schema 2.0)
- HTML-Report aus `reports/_shell.html` (Back-Link sichtbar, kein `is-dashboard`)
- `status.md` und Dashboard werden in jedem Lauf aktualisiert
- Standard-Schlussformat im Chat
- **Final-ZIP landet im Kunden-Folder** (Parent des MTA-Folders) — der Stratege muss nicht in den MTA-Folder navigieren, um sie zu finden
- **Versionierung über Timestamp im Dateinamen** — kein hartes Überschreiben älterer Snapshots
- **Voraussetzungs-Check ist weich**: Skill warnt, fragt nicht hart ab — Stratege darf Teil-MTA finalisieren
