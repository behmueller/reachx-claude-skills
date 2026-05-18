# MTA-Skill-Konventionen (`contracts.md`)

Dieses Dokument legt die gemeinsamen Regeln fest, an die sich **alle Skills im MTA-Workflow** halten müssen. Wenn du einen neuen MTA-Skill baust oder einen bestehenden anpasst, ist das hier die Pflichtlektüre.

**Stand 2026-05-17:** Schema-Version 2.2. Alle MTA-Outputs leben in Google Drive (über die `gws` CLI), nicht mehr lokal. Neu in 2.2: die Querschnitts-Abschnitte 11–13 (MCP-Health-Checks & Credential-Disziplin, Synthese-Sequenz & Input-Staleness, kritische Haltung & Daten-Disziplin) — die `meta.json`-Struktur ist gegenüber 2.1 unverändert, Projekte auf 2.1 brauchen keine Migration. Schema 2.1 führte den dedizierten `input/`-Sub-Folder für vom Strategen bereitgestellte Quell-Files ein (z.B. Meeting-Transkripte in `input/transkripte/`). Schema 2.0-Projekte (ohne `input/`) werden beim nächsten `01-01-mta-projekt-init`-Resume-Lauf automatisch ergänzt. Schema 1.0-Projekte (lokaler Filesystem-Pfad) sind gleichbedeutend mit Vorgänger-Status — neue Skills sollten die unterstützen oder zumindest sauber abbrechen.

Inhaltsverzeichnis:

1. [Projekt-Auffindung — wie ein Skill weiß, in welcher MTA er läuft](#1-projekt-auffindung)
2. [`meta.json`-Schema (Version 2.0)](#2-metajson-schema)
3. [`status.md`-Schema und -Update-Regeln](#3-statusmd-schema)
4. [Drive-Operationen — wie Skills Files schreiben und lesen](#4-drive-operationen)
5. [Datei-Konventionen — Naming, Sub-Folder, Output-Format](#5-datei-konventionen)
6. [Standard-Schlussformat im Chat](#6-standard-schlussformat)
7. [HTML-Reports — Shell-Nutzung und Dashboard-Update](#7-html-reports)
8. [Schema-vor-Lauf — für Skills mit kundenspezifischer Logik](#8-schema-vor-lauf)
9. [Audit-Trail, Konflikte, parallele Kollegen](#9-audit-trail)
10. [Token-Tracking pro MTA](#10-token-tracking-pro-mta)
11. [MCP-Abhängigkeiten, Health-Checks und Credential-Disziplin](#11-mcp-abhängigkeiten)
12. [Synthese-Sequenz und Input-Staleness](#12-synthese-sequenz)
13. [Kritische Haltung und Daten-Disziplin](#13-kritische-haltung)

---

## 1. Projekt-Auffindung

Jeder Folge-Skill braucht die Drive-Folder-ID der aktiven MTA. Suchreihenfolge:

1. **Expliziter Parameter:** Nutzer nennt den Slug ("für mta-mueller-…") oder gibt eine Drive-URL direkt mit.
2. **Active-MTA-Cache** (`~/.cache/reachx-mta/active-mtas.json`): Dort hat `01-01-mta-projekt-init` die zuletzt aktive MTA mit `slug → folder_id` registriert. Skills lesen den Cache mit:

   ```bash
   python3 <pfad>/01-01-mta-projekt-init/scripts/drive.py get-mta <slug>
   # oder
   python3 <pfad>/01-01-mta-projekt-init/scripts/drive.py list-mtas
   ```

3. **Mehrere aktive MTAs ohne expliziten Slug:** Frage den Nutzer, welche er meint — niemals raten.

Pflicht: **Jeder Folge-Skill prüft zuerst, ob `meta.json` im Drive-Folder existiert.** Wenn nicht (z.B. weil der Cache stale ist und der Folder gelöscht wurde), Abbruch mit:

```
✗ Kein gültiger MTA-Folder für '<slug>'.
Bitte 01-01-mta-projekt-init mit der Drive-URL des MTA-Ordners aufrufen.
```

---

## 2. `meta.json`-Schema

Liegt direkt im Drive-MTA-Root. Pflichtfelder (Schema 2.1):

```json
{
  "kunde": "string",
  "kunden_slug": "string",
  "branche": "string",
  "region": "string",
  "website": "string (URL)",
  "projekt_slug": "string",
  "drive": {
    "folder_id": "string (Drive-Folder-ID des MTA-Roots)",
    "folder_url": "string (https://drive.google.com/drive/folders/...)",
    "subfolders": {
      "input": "string (Drive-Folder-ID)",
      "data": "string",
      "wettbewerber": "string",
      "audits": "string",
      "synthese": "string",
      "reports": "string",
      "assets": "string"
    },
    "input_subfolders": {
      "transkripte": "string (Drive-Folder-ID)"
    }
  },
  "kickoff_datum": "string (YYYY-MM-DD) | null",
  "mta_deadline": "string (YYYY-MM-DD) | null",
  "erstellt_am": "string (ISO-8601)",
  "schema_version": "2.1"
}
```

- `meta.json` ist **read-only** für alle Folge-Skills. Nur `01-01-mta-projekt-init` schreibt diese Datei.
- Die `drive.subfolders`-Map ist die Single Source of Truth für die Folder-IDs, in die Folge-Skills ihre Outputs schreiben.
- `drive.input_subfolders` enthält die Sub-Sub-Folder unter `input/`, in denen der **Stratege selbst Files ablegt** (kein Skill schreibt dort hinein, Skills lesen nur). Aktuell: `transkripte`. Weitere Einträge können in späteren Schema-Versionen ergänzt werden.
- Bei Schema-Änderungen in zukünftigen Versionen: `schema_version` hochzählen.

### Migration von Schema 2.0

Schema-2.0-Projekte (ohne `input/`-Sub-Folder und ohne `drive.input_subfolders`) können einfach migriert werden: Beim nächsten Resume-Lauf von `01-01-mta-projekt-init` legt der Skill die fehlenden Folder per `find-or-create-folder` an (idempotent), aktualisiert die `drive`-Map in der `meta.json` und hebt `schema_version` auf `2.1`. Folge-Skills, die auf Schema-2.0-Projekte stoßen und neue Felder brauchen (`input_subfolders.transkripte`), brechen mit Hinweis ab: "Projekt auf Schema 2.0. Bitte 01-01-mta-projekt-init im Resume-Modus erneut aufrufen, dann diesen Skill wiederholen."

### Migration von Schema 1.0

Alte Projekte (Schema 1.0 mit lokalem `projekt_pfad`) werden nicht automatisch migriert. Wenn ein Folge-Skill ein Schema-1.0-Projekt findet, gibt er eine klare Meldung aus: "Dieses Projekt läuft noch auf Schema 1.0 (lokal). Migration auf Drive: `01-01-mta-projekt-init` mit `--migrate` aufrufen." (Die Migrations-Logik ist optional und kann später ergänzt werden.)

---

## 3. `status.md`-Schema

Liegt im Drive-MTA-Root. Wird von `01-01-mta-projekt-init` initialisiert und von **jedem Folge-Skill** am Ende seiner Ausführung aktualisiert. Updates passieren über `drive.py upsert-text` — das nutzt `gws files update` und überschreibt die Datei sauber (kein Datei-Müll, keine Duplikate).

### YAML-Frontmatter

```yaml
---
projekt: <projekt-slug>
kunde: <kundenname>
gestartet: <ISO-8601>
schritte_done:
  - <skill-name-1>
  - <skill-name-2>
schritte_offen:
  - <skill-name-3>
  - <skill-name-4>
naechster_empfohlen: <skill-name>
blockiert:
  - skill: <skill-name>
    wartet_auf: <was fehlt, warum blockiert>
---
```

### Markdown-Body

Strukturiert nach drei festen Sektionen:

```markdown
# MTA-Status: <kundenname>

## ✓ Erledigt

### <skill-name>
- Erledigt: <YYYY-MM-DD HH:MM>
- Output: <relative pfade der erzeugten dateien>
- Hinweise: <optional, wichtige Anmerkungen aus dem Lauf>

## ⏭ Nächster empfohlener Schritt

**<skill-name>** — <kurze Begründung in einem Satz>

## ⊙ Auch jetzt möglich (parallel)

- **<skill-name>** — <Begründung>

## ✗ Blockiert

- **<skill-name>** wartet auf <was fehlt>
```

### Update-Regeln für Folge-Skills

**Output-Reihenfolge:** Ein Skill schreibt zuerst alle inhaltlichen Outputs nach Drive (Markdown, CSV, dann der HTML-Report), und **erst danach** `status.md`. So hinterlässt auch ein Lauf, der vorzeitig endet (Subagent gekillt, Timeout), vollständige, nutzbare Outputs — und `status.md` meldet einen Skill nie als fertig, dessen Outputs fehlen.

Am Ende **jedes** Skill-Laufs:

1. Aktuelle `status.md` aus Drive lesen (`drive.py read <file-id>`). Die File-ID wird einmal pro Skill-Lauf via `find_by_name(meta.drive.folder_id, "status.md")` ermittelt.
2. Frontmatter parsen, eigenen Skill in `schritte_done` eintragen, aus `schritte_offen` entfernen.
3. Eigene Sektion unter "✓ Erledigt" im Body hinzufügen (mit Datum, Outputs, ggf. Hinweisen).
4. `naechster_empfohlen` setzen — der Skill, der jetzt den größten Mehrwert bringt.
5. Wenn parallele Skills möglich sind, in "⊙ Auch jetzt möglich" listen.
6. Wenn dieser Skill etwas blockiert (z. B. weil ein Schema noch zu bestätigen ist), entsprechenden Eintrag in `blockiert` (Frontmatter) und unter "✗ Blockiert" (Body).
7. Aktualisierte `status.md` zurückschreiben (`drive.py upsert-text`).

---

## 4. Drive-Operationen

**Alle persistenten Outputs leben in Google Drive**, nicht im lokalen Filesystem. Skills nutzen dafür das Helper-Modul `01-01-mta-projekt-init/scripts/drive.py` — entweder als Subprocess-CLI oder als Python-Import.

### Helper-Aufruf als Subprocess (häufigster Fall)

```bash
DRIVE="<plugin-pfad>/01-01-mta-projekt-init/scripts/drive.py"

# meta.json lesen
META_ID=$(python3 "$DRIVE" list-children "<mta-folder-id>" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE" read "$META_ID" > /tmp/meta.json

# Output schreiben (idempotent — überschreibt wenn schon vorhanden)
echo "<inhalt>" > /tmp/output.md
python3 "$DRIVE" upsert-text "<audits-folder-id>" "seo-sichtbarkeit.md" /tmp/output.md "text/markdown"
```

### Helper-Aufruf als Python-Modul

```python
import sys
sys.path.insert(0, "<plugin-pfad>/01-01-mta-projekt-init/scripts")
import drive

mta = drive.get_active_mta("mta-mueller-hausverwaltung-gmbh-2026-05")
meta_id = drive.find_by_name(mta["folder_id"], "meta.json")["id"]
meta = json.loads(drive.read_text(meta_id))

# Output schreiben
audits_id = meta["drive"]["subfolders"]["audits"]
drive.upsert_text(audits_id, "seo-sichtbarkeit.md", inhalt, mime_type="text/markdown")
```

### Lokaler Arbeits-Cache

Für temporäre Zwischenergebnisse (Apify-Roh-JSONs, CSV-Generierung, HTML-Templating) nutzt jeder Skill `~/.cache/reachx-mta/<slug>/`. Dieser Cache wird **nicht** mit Drive synchronisiert — Skills laden am Ende des Laufs nur die finalen Outputs nach Drive hoch.

### Fehlerbehandlung

- `gws` nicht installiert → Skill bricht ab mit Setup-Hinweis (kein Fallback auf MCP — wir haben uns auf gws committed).
- Drive-Quota überschritten (HTTP 429/403) → Skill bricht ab mit Original-Fehlermeldung und Retry-Hinweis.
- File nicht gefunden bei Read (HTTP 404) → Skill bricht ab und schlägt vor, `meta.json` zu prüfen oder MTA neu zu initialisieren.

---

## 5. Datei-Konventionen

### Output-Sub-Folder pro Skill-Familie

| Skill-Familie | Drive-Sub-Folder (`meta.drive.subfolders.*`) |
|---|---|
| Briefing & Setup (Stufe 1) | `data` (Ausnahme: `meta.json` und `status.md` liegen direkt im MTA-Root) |
| Marken-Profile + Wettbewerber (Stufe 2) | `wettbewerber` und `data` |
| Kanal-Audits (Stufe 3) | `audits` |
| Synthese (Stufe 4) | `synthese` |
| HTML-Reports (alle) | `reports` |
| Screenshots, Logos, Rohdaten-Caches | `assets` |

### Input-Sub-Folder (vom Strategen befüllt)

| Sub-Sub-Folder | Pfad (`meta.drive.input_subfolders.*`) | Wer befüllt | Wer liest |
|---|---|---|---|
| `input/transkripte/` | `transkripte` | Stratege (Drive-Web-UI / gws / Drag&Drop) | `01-02-kickoff-transcript-parser` |

**Konvention für `input/`-Inhalte:**

- Skills schreiben **niemals** in `input/`-Sub-Folder — sie sind reine Lese-Quelle.
- Der Stratege lädt Files direkt in den passenden Sub-Sub-Folder hoch, bevor er den verarbeitenden Skill aufruft.
- Erlaubte Datei-Endungen pro Sub-Sub-Folder regelt der verarbeitende Skill (z.B. `transkripte/`: `.md` Fireflies, `.docx` Plaud, `.txt`, `.vtt`).
- Mehrere Files pro Sub-Sub-Folder sind erlaubt (z.B. mehrere Meeting-Transkripte) — der verarbeitende Skill listet die Files und fragt den Strategen, wenn unklar welches er meint.
- Dateinamens-Empfehlung für Transkripte: `<typ>-<YYYY-MM-DD>.<ext>`, z.B. `kickoff-2026-05-15.md`, `folgetermin-2026-06-02.docx`, `verkaufsgespraech-2026-04-10.txt`. Wird nicht erzwungen, aber das jüngste File wird per `modifiedTime` ermittelt — sprechende Namen helfen.

### Dateinamen für inhaltliche Outputs

Klare, kurze Namen ohne Stufen-Präfix (das steckt im Skill, nicht im Output):

- `data/briefing.md`, `data/kunde.md`
- `wettbewerber/liste.md`, `wettbewerber/<wb-slug>.md`
- `audits/seo-sichtbarkeit.md`, `audits/seo-keywords.csv`, `audits/meta-ads.md`, etc.
- `synthese/positionierung.md`, `synthese/kanal-chancen.md`

### Dateinamen für HTML-Reports

Numerisches Präfix nach Workflow-Reihenfolge — bleibt unverändert zu Schema 1.0:

- `reports/01-briefing.html`
- `reports/02-kunde.html`
- `reports/03-wettbewerber-liste.html`
- `reports/04-wettbewerber-profile.html`
- `reports/05-audits-*.html` (pro Audit-Skill eine Datei) — Audit-Skills mit feiner Reihenfolge-Anforderung dürfen einen Buchstaben-Suffix vergeben, um sich gezielt vor anderen Audit-Reports einzusortieren: `reports/05a-gsc-first-party.html`, `reports/05b-ga4-first-party.html`, `reports/05c-sea-first-party.html` (der First-Party-Block läuft vor den Third-Party-Audit-Reports)
- `reports/06-synthese-*.html`
- `reports/index.html` ist immer das Dashboard.

### Output-Format: Hybrid (Markdown + YAML-Frontmatter)

Standard für inhaltliche Outputs:

```markdown
---
generiert_am: 2026-05-14T11:00:00Z
skill: 02-01-kunden-marken-profil
schema_version: 2.0
hero_test_score: 4
verstaendlichkeit_score: 3
touchpoints:
  - typ: website
    url: https://www.beispiel.de
  - typ: linkedin
    url: https://linkedin.com/company/beispiel
---

# Kunden-Marken-Profil: Beispiel GmbH

## Portfolio
Beispiel positioniert sich als ...

## Tonalität
- Achse formell ↔ informell: eher formell
- Beleg: "Sehr geehrte Damen und Herren, wir bieten Ihnen ..."
```

- **Frontmatter:** numerische Scores, IDs, kurze strukturierte Listen, Skill-Metadaten
- **Body:** narrative Inhalte, längere Analysen, Belege als Zitate

### Reine JSON nur wo sinnvoll

- `meta.json` — rein technische Metadaten
- `raw/`-Caches von API-Returns (Sistrix, Apify, etc.) — kommen ohnehin als JSON; gehören in `assets/raw/` als ZIP oder direkt
- Sehr lange flache Listen besser als CSV (z. B. `seo-keywords.csv` mit 2000 Keywords)

---

## 6. Standard-Schlussformat

Jeder Skill schließt im Chat **strikt** mit dieser Struktur:

```
✓ <skill-name> abgeschlossen.

Outputs (auf Drive):
- <relative pfad 1> — <kurze Beschreibung>
- <relative pfad 2> — <kurze Beschreibung>
Status aktualisiert in: status.md

Nächste Schritte:
1. <empfohlener-skill-name> — <Begründung in einem Satz>
2. (optional parallel) <alternativer-skill-name> — <Begründung>

Sag mir, welcher als nächster.
```

Variationen:

- Bei **mehreren empfohlenen Folge-Skills**: Liste mit kurzer Begründung pro Eintrag.
- Bei **blockierten Folge-Skills**: Zusätzliche Sektion "Blockiert:" mit Begründung.
- Bei **offenen Punkten** (z. B. unklare Briefing-Felder): "Offene Punkte:" als zusätzliche Sektion vor "Nächste Schritte".

Niemals weglassen. Auch nicht bei Skills, die "offensichtliche" Folge-Skills haben. Der Stratege sieht im Chat sofort, wo er steht.

---

## 7. HTML-Reports

**Zwei kanonische Dateien — bei HTML-Reports immer beide heranziehen:**

| Datei (im Plugin) | Rolle |
|---|---|
| `01-01-mta-projekt-init/reference/report-shell.html` | Der äußere Rahmen + das **gesamte CSS**. Pro Projekt als `reports/_shell.html` auf Drive. |
| `01-01-mta-projekt-init/reference/report-bausteine.md` | Die **einzige Quelle für Report-Markup** — fertiges Copy-Paste-Markup je Komponente. |

Diese beiden Dateien sind die einzige Wahrheit für Report-Aussehen. `contracts.md` dupliziert die CSS-Klassen-Liste **nicht** — sie steht in `report-bausteine.md`.

### Shell-Nutzung

Jedes Projekt hat im Anlage-Schritt eine `reports/_shell.html` auf Drive bekommen — die geteilte HTML-Vorlage im REACHX-Branding.

Wenn dein Skill einen HTML-Report schreibt:

1. Lies `reports/_shell.html` aus Drive (per `drive.py read <id>`). Übernimm den `<style>`-Block **unverändert** — niemals CSS umbauen, ergänzen oder aus dem Gedächtnis rekonstruieren.
2. Ersetze die acht Platzhalter:
   - `{{TITLE}}` — Browser-Tab-Titel: "<Skill-Titel> · <Kunde>"
   - `{{EYEBROW}}` — kleiner Label-Text oben: z. B. "MTA-Audit · SEO"
   - `{{DISPLAY_NAME}}` — große Überschrift: der eigentliche Report-Titel
   - `{{META_LINE}}` — Meta-Zeile unter dem Titel (Quelle, Datenstand, Akteur-Anzahl)
   - `{{MAIN_CONTENT}}` — der inhaltliche Teil zwischen `<main>` und `</main>`
   - `{{TOKEN_BREAKDOWN}}` — nur Dashboard, sonst leer lassen
   - `{{TOKEN_FOOTER}}` — Footer-Counter (siehe Abschnitt 10)
   - `{{FOOTER_TEXT}}` — Footer-Zeile
3. **Validiere** den fertigen Report vor dem Upload (siehe unten).
4. Lade das Resultat als `reports/<nummer>-<slug>.html` per `drive.py upsert-text` hoch (MIME `text/html`).

### Content-Sektionen — nur kanonische Bausteine

`{{MAIN_CONTENT}}` wird **ausschließlich** aus den Bausteinen in `report-bausteine.md` zusammengesetzt. Diese Datei enthält für jede Komponente — Sektion, Sticky-TOC, `table.data`, `table.ratings`, Stat-Strip, `details.dim`-Karten, Badges, Suggestion-Block, Top-N-Liste, SVG-Sparkline — das fertige Markup zum 1:1-Kopieren.

Vier Regeln:

- **Markup kopieren, nicht erfinden.** Die SKILL.md beschreibt *welche* Bausteine mit *welchen* Daten zu füllen sind — das Markup selbst kommt unverändert aus `report-bausteine.md`.
- **Keine eigenen CSS-Klassen.** Jede Klasse, die nicht in `report-bausteine.md` vorkommt, existiert im Shell-CSS nicht und rendert ungestylt.
- **Kein inline-`style="…"`.** Styling lebt im Shell-CSS, nicht im Report-Inhalt.
- **Kein eigener `<style>`-Block.** Das CSS kommt komplett aus der Shell.

### Pflicht: Report vor dem Upload validieren

Jeder Skill, der einen HTML-Report rendert, prüft ihn **vor dem Drive-Upload**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" \
  ~/.cache/reachx-mta/<slug>/<nummer>-<slug>.html --shell
```

Der Validator prüft drei Regeln: (1) jede verwendete CSS-Klasse ist im `<style>`-Block definiert, (2) keine offenen `{{Platzhalter}}`, (3) der `<style>`-Block ist byte-identisch mit der kanonischen Shell. **Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen**, Markup gegen `report-bausteine.md` korrigieren und erneut validieren.

### Dashboard-Update (`reports/index.html`)

Am Ende jedes Skill-Laufs aktualisiert der Skill **zusätzlich** das Dashboard:

1. Lies aktuellen `index.html` aus Drive.
2. Aktualisiere die Status-Sektion (Erledigt-Liste, Nächste Schritte) — gleiche Inhalte wie `status.md`, aber als HTML.
3. Ergänze einen Eintrag in der "Reports"-Sektion mit Link auf den neuen Report.
4. **Pflicht:** stelle sicher, dass das `<body>`-Tag die Klasse `is-dashboard` trägt (`<body class="is-dashboard">`). Diese Klasse blendet den Back-Link aus, der in der Shell standardmäßig im Hero rendert.
5. Schreibe `index.html` zurück per `drive.py upsert-text` (sauberes Update, keine Duplikat-Datei).

Dadurch hat der Stratege immer eine aktuelle Einstiegs-Seite, von der er zu allen bisher erzeugten Reports navigieren kann.

### Back-Link im Hero (alle Reports außer Dashboard)

Die Shell rendert im Hero standardmäßig einen `<a class="back-link" href="index.html">Dashboard</a>` oberhalb des Eyebrow. Dies funktioniert für alle Skill-Reports, die im selben `reports/`-Ordner liegen. Konventionen:

- **Normale Skill-Reports** (`01-briefing.html`, `02-kunde.html`, `04-wettbewerber-profile.html`, alle `audits/`- und `synthese/`-Reports): `<body>` ohne Klasse → Back-Link sichtbar.
- **Dashboard** (`reports/index.html`): `<body class="is-dashboard">` → Back-Link via CSS ausgeblendet.
- **Print-Layout:** Back-Link wird im Druck automatisch ausgeblendet (siehe Shell-CSS).
- **HREF:** bleibt immer `index.html` (relativer Pfad im selben Ordner), nicht `./index.html` oder absolut. Auf Drive funktioniert das, weil die HTML-Files im selben Folder liegen.

---

## 8. Schema-vor-Lauf

Skills mit **kundenspezifischer Bewertungs- oder Klassifikations-Logik** müssen in zwei Phasen laufen:

### Phase A: Schema-Vorschlag

1. Skill liest `data/briefing.md`, `data/kunde.md` (und ggf. weitere relevante Inputs) — alle aus Drive.
2. Generiert eine `<output-ordner>/<skill-slug>-schema.md`-Datei mit Vorschlag-Status, **schreibt sie nach Drive**.
3. Bricht ab, gibt im Chat aus:

```
Schema für <skill-name> vorgeschlagen.
Datei: <relativer pfad zur schema-datei> (auf Drive)
Bitte reviewen, anpassen, dann Status auf `bestaetigt` setzen und Skill erneut aufrufen.
```

Der Stratege kann das Schema dann direkt in der Drive-Web-UI editieren — Markdown-Files sind in Drive editierbar — oder lokal runterladen, editieren, hochladen.

### Phase B: Eigentliche Ausführung

Beim zweiten Aufruf:

1. Skill liest die Schema-Datei aus Drive.
2. Prüft `status: bestaetigt` im Frontmatter.
3. Wenn nicht bestätigt → Hinweis auf Phase A, kein Lauf.
4. Wenn bestätigt → führe die eigentliche Klassifikation/Bewertung durch.

### Schema-Datei-Format

```markdown
---
skill: <skill-slug>
status: vorgeschlagen   # vorgeschlagen | bestaetigt
basis: <welche dateien zur generierung gelesen wurden>
generiert_am: <ISO-8601>
# danach skill-spezifische Felder
---

# Schema für <skill-name>

## <Achse 1>
- ...
```

### Skills, die Schema-vor-Lauf verwenden

- `02-02-wettbewerber-identifikation` (Branchen-Seed-Keywords, Branchenportale, Region)
- `03-03-seo-keyword-kategorisierung` (Funnel- und Produkt-Cluster)
- `03-15-web-content-inventur` (Tiefe pro Akteur: Sitemap-only / Light / Full)
- `03-16-local-gmb-und-seo` (GMB-Kategorien, branchen-typische Review-Themen)
- Sämtliche Social-Channel-Audits (Profil-Zuordnung, Themen-Cluster)
- `04-01-positionierungs-analyse` (Differenzierungs-Achsen)
- `04-04-forecast-modell` (Annahmen-Set)
- `04-06-retainer-kalkulator` (Achtung: Schema liegt zentral im Skill-`reference/`, nicht projektspezifisch)

---

## 9. Audit-Trail, Konflikte, parallele Kollegen

### Audit-Trail

Drive zeigt für jeden File "Geändert von: [Kollege]", weil jeder mit seinem eigenen Google-Account schreibt (über die `gws`-CLI-Auth). Kein Setup nötig — passiert automatisch.

### Parallele Bearbeitung

Drive lässt mehrere Kollegen gleichzeitig in **einen Folder** schreiben, aber **nicht in dieselbe Datei**. Wenn zwei Kollegen gleichzeitig `status.md` updaten wollen, erzeugt Drive eine Konflikt-Kopie (`status (1).md`). Das ist meistens das richtige Verhalten — der zweite Kollege merkt es, sieht beide Versionen und kann mergen.

Konvention: **Pro MTA arbeitet zur gleichen Zeit nur ein Kollege.** Parallele Kollegen-Arbeit ist in der Praxis selten (eine MTA hat einen verantwortlichen Strategen). Wenn doch nötig: über Slack/Chat absprechen, wer gerade dran ist.

### Sync-Latenz

Da Skills direkt über die Drive-API schreiben (nicht über Drive Desktop), sind Änderungen für andere Kollegen praktisch sofort sichtbar — keine Sync-Verzögerung wie bei Drive Desktop. In der Web-UI kann die Anzeige des aktuellen Files trotzdem 5–10 Sekunden brauchen (Drive-Caching).

### Datei-Konflikt-Detektion

Skills können vor einem Update prüfen, ob die Datei seit dem letzten Lesen verändert wurde (`modifiedTime`-Feld). Wenn ja, brechen sie mit einer Warnung ab statt zu überschreiben. Pattern (optional, noch nicht in allen Skills):

```python
file_meta = drive.get_file_metadata(file_id)
if file_meta["modifiedTime"] > my_last_read_time:
    raise ConflictError("Datei wurde inzwischen von einem anderen Kollegen geändert.")
```

---

## 10. Token-Tracking pro MTA

**Zweck:** Live-Tracking des Token-Verbrauchs pro Modell und pro Skill, mit EUR-Cost-Schätzung. Sichtbar auf dem Dashboard und im Footer jedes Skill-Reports.

### Architektur

- **Datenquelle:** Claude Code logged pro Message in `~/.claude/projects/<cwd-encoded>/*.jsonl` (mit `usage`-Block: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens` und Modell-Name).
- **Helper:** `01-01-mta-projekt-init/scripts/token-tracker.py` aggregiert die Daten inkrementell (Cursor in lokalem State), rechnet EUR-Cost auf Basis Anthropic-Pricing (Stand Mai 2026, FX `REACHX_USD_TO_EUR` Env, Default 0.92).
- **Speicherort:** Lokaler Cache `~/.cache/reachx-mta/<slug>/token-usage.json` (Live nach jedem Prompt), Drive `meta/token-usage.json` (gedrosselt alle ~5 Min via Stop-Hook).
- **Stop-Hook:** `${CLAUDE_PLUGIN_ROOT}/scripts/post-stop-token-sync.sh` läuft nach jeder Claude-Antwort, non-blocking, silent-fail.

### Render-Punkte

- **Dashboard (`reports/index.html`):** Voller Breakdown via `token-tracker.py render-counter <slug> --style breakdown` als `{{TOKEN_BREAKDOWN}}`-Slot. Plus kompakter Stat-Strip via `--style stat-strip` im `{{MAIN_CONTENT}}`-Stat-Bereich. Wird beim Dashboard-Re-Render durch Folge-Skills aktualisiert.
- **Skill-Reports (`reports/<nummer>-<slug>.html`):** Skill-spezifischer Footer-Counter via `token-tracker.py render-skill-counter <slug> <skill-name>` als `{{TOKEN_FOOTER}}`-Slot in der Shell. Wenn der Skill den Slot nicht befüllt: leer.

### Skill-Pflicht: Mark-Start / Mark-End

Damit `pro_skill`-Aufschlüsselung korrekt zugeordnet wird, muss jeder Folge-Skill am Anfang und Ende seines Laufs Events absetzen:

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
python3 "$TRACKER" mark-skill-start "<slug>" "<skill-name>"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "<slug>" "<skill-name>"
```

Die Events landen in `~/.cache/reachx-mta/<slug>/skill-log.jsonl`. Beim nächsten Aggregate werden alle Messages, deren Timestamp zwischen `start` und `end` liegen, dem Skill zugeordnet. Messages ohne aktiven Skill (z.B. freie User-Interaktion zwischen Skill-Läufen) landen unter `_kein_skill_aktiv`.

### Pricing-Tabelle aktualisieren

Wenn Anthropic die Preise ändert, bearbeite `PRICING_USD_PER_MTOK` in `token-tracker.py`. Aktuelle Werte (Mai 2026, pro 1M Tokens, USD):

| Modell | Input | Output | Cache-Read | Cache-Write 5m | Cache-Write 1h |
|---|---:|---:|---:|---:|---:|
| Opus 4.7 | $15 | $75 | $1.50 | $18.75 | $30 |
| Sonnet 4.6 | $3 | $15 | $0.30 | $3.75 | $6 |
| Haiku 4.5 | $0.80 | $4 | $0.08 | $1.00 | $1.60 |

### Was NICHT getrackt wird

- Token aus Drittanbieter-APIs (Apify, Sistrix, Ahrefs, gws): Claude Code-Tokens only.
- Sehr alte Sessions vor dem ersten `aggregate`-Lauf: Cursor-based, also nur Messages seit Skill-Installation werden mitgezählt. Für Bestandsprojekte: einmaliger Full-Re-Aggregate möglich via `rm ~/.cache/reachx-mta/<slug>/token-tracker-cursor.json && python3 token-tracker.py aggregate <slug>`.

---

## 11. MCP-Abhängigkeiten, Health-Checks und Credential-Disziplin

Viele MTA-Skills hängen an externen MCP-Servern (Sistrix, Ahrefs, GSC/Search-Console, Apify). Diese Verbindungen sind **nicht zuverlässig** — sie sind bei Session-Start nicht immer verbunden, und Apify-Sessions brechen im Betrieb ab. Jeder MCP-abhängige Skill folgt diesen Regeln.

### Pflicht-MCPs deklarieren

Jede `SKILL.md` listet unter `## Voraussetzungen` ihre MCPs getrennt nach:

- **Pflicht-MCP** — ohne diesen MCP ist der Skill nicht sinnvoll lauffähig → bei Fehlen sauberer Abbruch.
- **Optionaler MCP** — erweitert den Skill, ist aber ersetzbar → bei Fehlen läuft der Skill im **Reduced-Modus** und dokumentiert die Lücke im Output (`konfidenz: niedrig`, Hinweis im Schluss-Format).

### Health-Check vor dem Lauf

Bevor ein Skill teure Logik startet, prüft er die Pflicht-MCPs mit **einem billigen Test-Call** (z.B. Sistrix `credits`, Ahrefs `subscription-info`, Apify `search-actors` mit Limit 1). Schlägt er fehl:

```
✗ Pflicht-MCP '<name>' nicht erreichbar.
Bitte in /mcp verbinden (ggf. neu authentifizieren) und Skill erneut aufrufen.
Optional fehlend: <liste> → Skill liefe im Reduced-Modus.
```

Kein blindes Lossscrapen — sonst scheitern erst nach vielen Calls einzelne Schritte, und der Output ist halb-leer.

### Apify-Spezifika

- Apify-MCP-Sessions **überleben PC-Standby / lange Pausen nicht** — typischer Fehler: `Session ID not found`. Der Health-Check direkt vor dem ersten echten Scrape (nicht nur am Skill-Start) fängt das ab.
- **Parallel-Clients** (Codex, eine zweite Claude-Session) auf demselben Apify-Account-Token invalidieren die Session gegenseitig. Bei wiederholtem Session-Bruch im Schluss-Format darauf hinweisen.
- Skills mit vielen Apify-Runs (Social, GMB, Ads): bei `Session ID not found` **abbrechen mit Reconnect-Hinweis** statt jeden weiteren Akteur einzeln scheitern zu lassen. Bereits geschriebene Teil-Outputs erwähnen.
- Getestete Actor-IDs gehören **datiert** in die `reference/`-Datei des Skills (`actor`, `zuletzt_getestet: YYYY-MM-DD`, `status`). Login-Wall-blockierte Quellen (Facebook-Posts, LinkedIn Ad Library, teils Jameda) explizit als „nicht erhebbar ohne authentifizierten Scraper" markieren — kein endloses Actor-Durchprobieren.

### Credential-Disziplin (Pflicht)

Token werden über **genau eine definierte Umgebungsvariable pro Dienst** erkannt — `APIFY_TOKEN`, `SISTRIX_API_KEY`, `PAGESPEED_API_KEY` etc. Erlaubt ist ausschließlich der Test **dieser einen Variable**:

```bash
[ -n "$APIFY_TOKEN" ] || { echo "✗ APIFY_TOKEN nicht gesetzt."; exit 1; }
```

**Verboten:** breite Credential-Suche — kein `env | grep -iE 'token|key|secret'`, kein Durchsuchen von `~/.zshrc`, `~/.zprofile`, `~/.netrc`, `~/.claude/settings.json` o.ä. nach Schlüsseln. Das löst zu Recht einen Security-Block des Harness aus. Fehlt die definierte Variable → sofortiger sauberer Abbruch mit Angabe des erwarteten Variablennamens, **keine** Exploration.

---

## 12. Synthese-Sequenz und Input-Staleness

Die Stufe-4-Synthese ist eine **Kette** — jeder Skill liest den Output des Vorgängers als Pflicht-Input. Wird sie parallel oder in falscher Reihenfolge gefahren, bauen Skills auf veralteten Zahlen auf, und die divergierenden Werte fallen erst im fertigen Deck auf.

### Verbindliche Reihenfolge

```
04-01-positionierungs-analyse
04-02-kanal-chancen-analyse
  → 04-03-ziele-aus-potenzialen
    → 04-04-forecast-modell
      → 04-05-90-tage-plan
        → 04-06-retainer-kalkulator
```

Jeder dieser Skills **darf erst starten, wenn der Vorgänger fertig ist** — kein Parallel-Start. Der Hauptthread orchestriert sequenziell.

### Pflicht-Input-Check statt Silent-Fallback

Jeder Synthese-Skill prüft zu Beginn, ob seine Pflicht-Inputs existieren — und bei Schema-Inputs zusätzlich `status: bestaetigt`. Fehlt ein Pflicht-Input → **Abbruch mit klarer Meldung**:

```
✗ <skill> kann nicht laufen: <pflicht-input> fehlt (oder status ≠ bestaetigt).
Bitte zuerst <vorgänger-skill> ausführen.
```

**Kein „hybrid"-, „Bottom-up-aus-Briefing"- oder ähnlicher Silent-Fallback**, der den fehlenden Vorgänger still kompensiert — das erzeugt zwei MTA-Outputs mit unvereinbaren Zahlen (in der Praxis gesehen: Forecast und Ziele wichen um ~50 % ab).

### Input-Staleness

Jeder Synthese-Output trägt im Frontmatter, worauf er beruht:

```yaml
basis_inputs:
  - datei: synthese/kanal-chancen.md
    generiert_am: 2026-05-17T19:30:00Z
  - datei: audits/seo-keyword-cluster.csv
    generiert_am: 2026-05-16T14:00:00Z
```

Beim Lauf vergleicht der Skill die `generiert_am`-Stempel seiner Inputs mit dem eigenen letzten Output. Ist ein Input **neuer** als der bestehende Output → Staleness-Hinweis im Schluss-Format: „`<input>` wurde nach diesem Output aktualisiert — Re-Run empfohlen."

### Re-Run-Disziplin

Wird ein **Audit re-gerunnt**, nachdem die Synthese schon lief: Der Audit-Skill markiert in `status.md` (Frontmatter `blockiert` oder ein Hinweis in der eigenen Sektion), dass die nachgelagerten Synthese-Skills auf veralteter Basis stehen. Pauschale Regel: Ändert sich Stufe 3, ist die Stufe-4-Kette potenziell stale.

### Konsistenz-Check zwischen Synthese-Outputs

Leiten zwei Skills dieselbe Größe unterschiedlich ab (klassisch: `ziele.md` vs. `forecast-modell.md` für NPat/Umsatz Jahr 1), führt der spätere Skill einen **Cross-Check** durch und weist eine Abweichung **> 20 %** als explizite Auffälligkeit aus. Geteilte Parameter (z.B. Doppelzählungs-Faktor, AOV, CR-Bandbreiten) werden aus **einer** Quelle gezogen — dem bestätigten Annahmen-Schema — nicht pro Skill neu angenommen.

---

## 13. Kritische Haltung und Daten-Disziplin

Die MTA ist ein **prüfendes** Instrument, kein Protokoll der Kundenselbsteinschätzung. Diese Haltung ist für alle Skills verbindlich — besonders für Wettbewerber- und Synthese-Skills.

### Kunden-Aussagen sind Hypothesen

Angaben aus Briefing / Kickoff (Ziele, genannte Wettbewerber, Kapazitäts- und Budget-Einschätzungen, Selbstbild) sind **Hypothesen, keine Fakten**. Sie werden mit erhobenen Daten verifiziert, bevor sie in Bewertung oder Forecast einfließen:

- Vom Kunden genannte Wettbewerber → gegen reale Datenlage prüfen (Sichtbarkeit, Local-Pack, GMB, Paid). Ein genannter „Hauptkonkurrent" kann sich als nachrangig erweisen — und umgekehrt.
- Kunden-Ziele → gegen Markt-Potenzial plausibilisieren, bevor sie als Zielwert gelten.
- Zusätzlich immer die **Latente-Bedrohung-Frage** stellen: Wer ist heute schwach, würde aber stark, sobald der Kunde aufdreht?

### Quellen-Kennzeichnung pro Zahl (Pflicht)

Jede Zahl im Output trägt einen erkennbaren Quellen-Typ — im Frontmatter, in Tabellenspalten oder inline:

| Typ | Bedeutung |
|---|---|
| `erhoben` | direkt aus Tool/MCP gemessen (Sistrix, Ahrefs, Apify, GSC, PageSpeed) |
| `briefing` | Kundenangabe aus Briefing/Kickoff — unverifiziert |
| `benchmark` | Branchen-Referenzwert aus einer Reference-Datei |
| `schaetzung_skill` | heuristisch vom Skill abgeleitet |

Eine heuristische Schätzung wird **niemals** als erhobener Wert dargestellt. **Load-bearing Heuristiken** — Annahmen, die Forecast, ROI oder eine Top-3-Empfehlung tragen — werden zusätzlich als explizite Auffälligkeit ausgewiesen, damit der Stratege sie im Kundengespräch kennt.

### Aggregat- und Volatilitäts-Disziplin

- **Plattform-Trennung:** Kennzahlen pro Quelle getrennt halten. Eine GMB-Review-Zahl ist nicht die Multi-Plattform-Summe (GMB + Jameda + …). Im Frontmatter Quelle/Plattform pro Wert benennen.
- **Volatile Kleinwerte:** Metriken, die bei kleinen absoluten Werten stark schwanken, taugen dort nicht als Primär-Signal. Konkret: der Sistrix-Sichtbarkeitsindex bei `SI < 0,05` — ein einzelnes kurz rankendes Keyword verdoppelt den Wert. Für lokale Akteure dort Local-Pack-Quoten / GMB-Metriken als Leitsignal nehmen, den VI nur sekundär.
- **Trend-Ehrlichkeit:** Prozent-Trends gegen einen sinnvollen Basiszeitpunkt rechnen, nicht Peak-gegen-Tal. Einen „+70 %"-Befund auf Artefakt prüfen, bevor er in den Output geht.

---

## Versionierung dieses Dokuments

Wenn sich Konventionen ändern, `schema_version` in `meta.json` und in betroffenen Schemas hochzählen. Alte Projekte bleiben auf ihrer Version — Skills sollten Versions-Check machen, bevor sie auf alte Schemas zugreifen.

Aktuelle Version: **2.2** (Abschnitte 11–13 ergänzt: MCP-Health-Checks/Credential-Disziplin, Synthese-Sequenz/Staleness, kritische Haltung — seit 2026-05-17. Keine `meta.json`-Strukturänderung gegenüber 2.1; Projekte auf 2.1 bleiben kompatibel.)
Vorgänger: 2.1 (Drive-basiert mit `input/`-Sub-Folder für Stratege-Quell-Files, 2026-05-15), 2.0 (Drive-basiert, 2026-05-14 — automatische Migration via 01-01-Resume), 1.0 (lokal-Filesystem-basiert, bis 2026-05-13)
