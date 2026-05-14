# MTA-Skill-Konventionen (`contracts.md`)

Dieses Dokument legt die gemeinsamen Regeln fest, an die sich **alle Skills im MTA-Workflow** halten müssen. Wenn du einen neuen MTA-Skill baust oder einen bestehenden anpasst, ist das hier die Pflichtlektüre.

**Stand 2026-05-14:** Schema-Version 2.0. Alle MTA-Outputs leben jetzt in Google Drive (über die `gws` CLI), nicht mehr lokal. Schema 1.0-Projekte (lokaler Filesystem-Pfad) sind gleichbedeutend mit Vorgänger-Status — neue Skills sollten die unterstützen oder zumindest sauber abbrechen.

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

Liegt direkt im Drive-MTA-Root. Pflichtfelder (Schema 2.0):

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
      "data": "string (Drive-Folder-ID)",
      "wettbewerber": "string",
      "audits": "string",
      "synthese": "string",
      "reports": "string",
      "assets": "string"
    }
  },
  "kickoff_datum": "string (YYYY-MM-DD) | null",
  "mta_deadline": "string (YYYY-MM-DD) | null",
  "erstellt_am": "string (ISO-8601)",
  "schema_version": "2.0"
}
```

- `meta.json` ist **read-only** für alle Folge-Skills. Nur `01-01-mta-projekt-init` schreibt diese Datei.
- Die `drive.subfolders`-Map ist die Single Source of Truth für die Folder-IDs, in die Folge-Skills ihre Outputs schreiben.
- Bei Schema-Änderungen in zukünftigen Versionen: `schema_version` hochzählen.

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
- `reports/05-audits-*.html` (pro Audit-Skill eine Datei)
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

### Shell-Nutzung

Jedes Projekt hat im Anlage-Schritt eine `reports/_shell.html` auf Drive bekommen — das ist die geteilte HTML-Vorlage im REACHX-Branding.

Wenn dein Skill einen HTML-Report schreibt:

1. Lies `reports/_shell.html` aus Drive (per `drive.py read <id>`).
2. Ersetze die folgenden Platzhalter:
   - `{{TITLE}}` — Browser-Tab-Titel: "<Skill-Titel> · <Kunde>"
   - `{{EYEBROW}}` — kleiner Label-Text oben: z. B. "MTA-Audit", "Synthese", "Briefing"
   - `{{DISPLAY_NAME}}` — große Überschrift: der eigentliche Report-Titel
   - `{{META_LINE}}` — Meta-Zeile unter dem Titel (Erstellungs-Datum, ggf. Quelle)
   - `{{MAIN_CONTENT}}` — der inhaltliche Teil zwischen `<main>` und `</main>`
   - `{{FOOTER_TEXT}}` — Footer-Zeile
3. Lade das Resultat als `reports/<nummer>-<slug>.html` per `drive.py upsert-text` hoch (MIME `text/html`).

### Content-Sektionen

Innerhalb von `{{MAIN_CONTENT}}` strukturierst du den Inhalt mit den im Shell-CSS verfügbaren Klassen:

- `<section>` für jede Haupt-Sektion
- `.section-heading` mit `.label` (eyebrow) und `<h2>` (Section-Titel)
- `.summary-card` für hervorgehobene Zusammenfassungen
- `details.skill[data-status="..."]` für expandable Karten (siehe Skills-Overview-Beispiel)
- `table.data` für tabellarische Daten
- `.badge.stark`, `.badge.mittel`, `.badge.schwach` für Status-Badges
- `nav.toc` für Section-Quicklinks oben

Die vollständige CSS-Klassen-Übersicht steckt in `reports/_shell.html` selbst (auskommentiert).

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

## Versionierung dieses Dokuments

Wenn sich Konventionen ändern, `schema_version` in `meta.json` und in betroffenen Schemas hochzählen. Alte Projekte bleiben auf ihrer Version — Skills sollten Versions-Check machen, bevor sie auf alte Schemas zugreifen.

Aktuelle Version: **2.0** (Drive-basiert, seit 2026-05-14)
Vorgänger: 1.0 (lokal-Filesystem-basiert, bis 2026-05-13)
