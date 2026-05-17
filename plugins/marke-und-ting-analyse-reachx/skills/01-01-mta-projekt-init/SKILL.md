---
name: 01-01-mta-projekt-init
description: Legt einen neuen MARKE&TING®-Analyse-Projektordner in Google Drive an oder setzt einen bestehenden MTA-Ordner fort — inklusive Sub-Ordnerstruktur, Meta-Daten, Status-Datei und HTML-Report-Dashboard. Der Projektleiter gibt die Drive-URL des MTA-Ordners im REACHX Shared Drive an (innerhalb des Kunden-Ordners vom Projektleiter vorab angelegt). Nutze diesen Skill IMMER, wenn der Nutzer eine neue MTA für einen Kunden starten will oder eine bestehende MTA fortsetzen möchte — auch bei Phrasen wie "neuer MTA für [Kunde]", "starte MTA für [Kunde]", "lege MTA an für [Kunde]", "neues MTA-Projekt", "MARKE&TING-Analyse für [Kunde]", "MTA-Projekt initialisieren", "MTA fortsetzen", "weiter mit MTA". Dieser Skill ist die Voraussetzung für alle weiteren MTA-Skills — die brechen ab, wenn der MTA-Folder nicht initialisiert (meta.json fehlt) oder nicht im lokalen Cache registriert ist.
---

# 01-01-MTA-Projekt-Init

Legt für einen neuen MARKE&TING®-Analyse-Lauf die saubere Projektstruktur **direkt im REACHX Shared Drive** an, schreibt die Stammdaten in `meta.json`, initialisiert die Fortschritts-Datei `status.md` und erzeugt das leere HTML-Report-Dashboard im REACHX-Branding. Erkennt automatisch, ob bereits eine MTA im Ziel-Folder existiert, und setzt sie in dem Fall fort (Resume-Modus).

Dieser Skill ist der **Pflicht-Einstieg** in jeden MTA-Lauf. Alle Folge-Skills setzen voraus, dass dieser Skill gelaufen ist — sie prüfen auf das Vorhandensein der MTA im lokalen Active-MTA-Cache (`~/.cache/reachx-mta/active-mtas.json`) und brechen sonst mit klarer Fehlermeldung ab.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "Neuer MTA für [Kunde]"
- "Starte MTA-Projekt für [Kunde]"
- "Lege MTA an für [Kunde]"
- "MARKE&TING-Analyse für [Kunde]"
- "MTA-Projekt initialisieren"
- "MTA fortsetzen für [Kunde]" / "weiter mit MTA [Kunde]" (Resume)
- Nutzer will erkennbar einen neuen MTA-Lauf starten oder eine bestehende MTA fortsetzen

## Was der Skill liefert

Eine vollständige MTA-Struktur im REACHX Shared Drive unter dem vom Projektleiter angegebenen MTA-Folder:

```
[Drive] <Kunde>/<MTA-Folder>/
├── meta.json                    # Stammdaten + Drive-Folder-IDs (Schema 2.1)
├── status.md                    # Fortschritts-Tracker für alle Folge-Skills
├── input/                       # vom Strategen bereitgestellte Quell-Files (Input für Skills)
│   └── transkripte/             # Kickoff-/Folge-Meeting-Transkripte (.md, .docx, .txt, .vtt)
├── data/                        # für Skill-Outputs (briefing.md, kunde.md, etc.)
├── wettbewerber/                # für Wettbewerber-Profile
├── audits/                      # für Kanal-Audit-Outputs
├── synthese/                    # für Synthese-Skills (Stufe 4)
├── reports/
│   ├── index.html               # Dashboard mit Status-Übersicht
│   └── _shell.html              # Template für andere Skills (HTML-Reports)
└── assets/                      # Screenshots, Logos, Rohdaten
```

Der `input/`-Sub-Folder ist der **einzige Ort, in den der Stratege selbst Files ablegt** (per Drive-Web-UI, Drag&Drop oder gws). Alles andere wird ausschließlich von Skills geschrieben. Aktuell genutzt von `01-02-kickoff-transcript-parser` (liest aus `input/transkripte/`); zukünftige Skills können weitere Sub-Sub-Folder unter `input/` ergänzen (z.B. `input/screenshots/`, `input/dokumente/`).

Plus lokal beim Kollegen, der die MTA leitet: ein Eintrag in `~/.cache/reachx-mta/active-mtas.json` mit `<slug> → {folder_id, kunde, zuletzt_aktiv}`, damit Folge-Skills den Drive-Folder ohne erneute URL-Eingabe wiederfinden.

## Voraussetzungen

Der Skill nutzt das Helper-Modul `scripts/drive.py`, das wiederum die **`gws` CLI** (Google Workspace CLI) für alle Drive-Operationen nutzt. Voraussetzung:

- `gws` installiert und mit dem persönlichen Google-Account des Projektleiters authentifiziert (`which gws` muss einen Pfad zurückgeben).
- Schreibrechte im REACHX Shared Drive auf den Kunden-Folder.
- Python 3.9+ verfügbar (Standard auf macOS).

Wenn `gws` nicht installiert ist: **abbrechen** mit Setup-Anleitung statt zu raten.

## Ablauf

### Schritt 1: Stammdaten erfassen

Frage den Nutzer nach den folgenden fünf Pflicht-Stammdaten. Falls Angaben in der Konversation bereits vorhanden sind, übernimm sie und bestätige sie nur — frage nicht doppelt:

1. **Kundenname** (Pflicht) — z. B. "Müller Hausverwaltung GmbH"
2. **Branche** (Pflicht, Freitext) — z. B. "Hausverwaltung", "Orthopädie-Praxis"
3. **Region** (Pflicht) — z. B. "Frankfurt am Main", "DACH-weit", "Hessen"
4. **Website-URL** (Pflicht) — vollständige URL inklusive Protokoll
5. **Drive-MTA-Ordner-URL** (Pflicht) — Der Projektleiter hat im REACHX Shared Drive bereits einen Kunden-Ordner und darin einen leeren MTA-Ordner angelegt. Wir brauchen die URL **dieses MTA-Ordners**, nicht die des Kunden-Ordners. Akzeptiert werden:
   - Drive-Web-URL: `https://drive.google.com/drive/folders/<ID>` (auch mit `?usp=sharing` etc.)
   - Drive-Open-URL: `https://drive.google.com/open?id=<ID>`
   - Direkt die Folder-ID (20+ Zeichen, `[a-zA-Z0-9_-]`)

Optional:
- **Kickoff-Datum** (YYYY-MM-DD)
- **MTA-Deadline** (YYYY-MM-DD)

### Schritt 2: Drive-Folder validieren

Bevor irgendetwas geschrieben wird:

```bash
python3 scripts/drive.py extract-folder-id "<eingegebene-url-oder-id>"
python3 scripts/drive.py validate-folder "<folder-id>"
```

`validate-folder` prüft drei Dinge und bricht bei jedem Fehler ab:
- Folder existiert und ist mit dem aktuellen Google-Account erreichbar
- Der Drive-Eintrag ist wirklich ein Folder (kein File, kein Google Doc)
- Der Account hat `canAddChildren` (Schreibrecht)

Bei Fehlern: gib die `gws`-Fehlermeldung im Klartext aus und schlage den nächsten Schritt vor (z.B. "Bitte den Drive-Admin um Schreibrechte fragen" oder "URL prüfen — vielleicht ist es der Kunden-Ordner statt des MTA-Ordners?").

### Schritt 3: Slug ableiten

Berechne den Slug nach dieser Regel:

- Kundenname lowercase, Umlaute ersetzen (ä→ae, ö→oe, ü→ue, ß→ss), alles außer `[a-z0-9-]` zu Bindestrich, doppelte Bindestriche kollabieren, führende/abschließende Bindestriche entfernen
- Format: `mta-<kunden-slug>-<YYYY-MM>` mit dem aktuellen Monat
- Beispiel: "Müller Hausverwaltung GmbH" + Mai 2026 → `mta-mueller-hausverwaltung-gmbh-2026-05`

Nutze das `scripts/slugify.py`-Skript für die Slug-Erzeugung — verhindert Inkonsistenzen.

### Schritt 4: Resume-Check

Bevor du neu anlegst, prüfe ob im Ziel-Folder schon eine `meta.json` existiert:

```bash
python3 scripts/drive.py list-children "<folder-id>"
```

Wenn `meta.json` in der Liste auftaucht:
1. Lies sie: `python3 scripts/drive.py read "<meta-json-file-id>"`
2. Lies `status.md` analog
3. Registriere die MTA im lokalen Cache: `python3 scripts/drive.py register-mta "<slug-aus-meta>" "<folder-id>" "<kunde-aus-meta>"`
4. Gib dem Nutzer den aktuellen Stand aus: "MTA für [Kunde] wird fortgesetzt. Stand laut `status.md`: Schritt X erledigt, nächster empfohlener Schritt: Y." Schluss-Format wie in Schritt 11, aber ohne "neu angelegt".

Wenn `meta.json` fehlt, weiter zu Schritt 5.

### Schritt 5: Pflicht-Bestätigung vor Anlage

**STOPP** — gib alle Stammdaten plus den Drive-Folder-Namen zusammengefasst aus und warte auf ausdrückliche Bestätigung des Nutzers ("ja", "passt", "leg an" o. ä.). Wenn der Nutzer korrigiert, übernimm die Korrektur und bestätige erneut.

Beispiel-Output für den Bestätigungs-Stop:

```
Stammdaten geprüft:
- Kunde:    Müller Hausverwaltung GmbH
- Branche:  Hausverwaltung
- Region:   Frankfurt am Main
- Website:  https://www.mueller-hausverwaltung.de
- Slug:     mta-mueller-hausverwaltung-gmbh-2026-05
- Drive:    [REACHX Shared Drive] Müller Hausverwaltung > MTA 2026-05 (leer)
            https://drive.google.com/drive/folders/1abc...

OK so?
```

### Schritt 6: Sub-Ordner anlegen

Lege die sieben Sub-Folders unter dem MTA-Folder an, plus die definierten Sub-Sub-Folder unter `input/`. Idempotent (existierende werden wiederverwendet, nicht überschrieben):

```bash
# Top-Level Sub-Folder
for sub in input data wettbewerber audits synthese reports assets; do
  python3 scripts/drive.py find-or-create-folder "<folder-id>" "$sub"
done

# Sub-Sub-Folder unter input/
# Die input-Folder-ID kommt aus dem find-or-create-folder-Lauf oben
python3 scripts/drive.py find-or-create-folder "<input-folder-id>" "transkripte"
```

Sammle alle zurückgegebenen Folder-IDs für `meta.json` — sowohl die Top-Level-Sub-Folder als auch die Sub-Sub-Folder unter `input/`.

**Resume-Fall (Schritt 4 hatte schon eine `meta.json` gefunden):** Auch im Resume-Lauf rufst du `find-or-create-folder` für **alle** Top-Level-Sub-Folder und `input/transkripte` auf — das ist idempotent. Damit werden fehlende Sub-Folder (z.B. weil das Projekt mit einem älteren Schema initialisiert wurde) automatisch ergänzt. Anschließend aktualisierst du die `drive.subfolders`-Map in der bestehenden `meta.json` und hebst die `schema_version` ggf. auf den aktuellen Stand.

### Schritt 7: `meta.json` schreiben

Erstelle die `meta.json` (Schema-Version 2.1 — enthält Drive-IDs inklusive `input`-Sub-Folder und dessen Sub-Sub-Folder):

```json
{
  "kunde": "Müller Hausverwaltung GmbH",
  "kunden_slug": "mueller-hausverwaltung-gmbh",
  "branche": "Hausverwaltung",
  "region": "Frankfurt am Main",
  "website": "https://www.mueller-hausverwaltung.de",
  "projekt_slug": "mta-mueller-hausverwaltung-gmbh-2026-05",
  "drive": {
    "folder_id": "<root-mta-folder-id>",
    "folder_url": "https://drive.google.com/drive/folders/<id>",
    "subfolders": {
      "input": "<id>",
      "data": "<id>",
      "wettbewerber": "<id>",
      "audits": "<id>",
      "synthese": "<id>",
      "reports": "<id>",
      "assets": "<id>"
    },
    "input_subfolders": {
      "transkripte": "<id>"
    }
  },
  "kickoff_datum": null,
  "mta_deadline": null,
  "erstellt_am": "2026-05-14T14:30:00Z",
  "schema_version": "2.1"
}
```

`drive.input_subfolders` ist als eigener Block angelegt (statt verschachtelt unter `subfolders.input`), damit Folge-Skills ohne Sonderfall-Logik darauf zugreifen können: `meta["drive"]["input_subfolders"]["transkripte"]`. Spätere Erweiterungen (z.B. `input_subfolders.screenshots`) bleiben rückwärtskompatibel.

Hochladen via:

```bash
python3 scripts/drive.py upsert-text "<folder-id>" "meta.json" /tmp/meta-content.json "application/json"
```

(Tipp: schreibe den JSON-String erst in eine lokale temp-Datei und übergib den Pfad dann an `upsert-text`. Das vermeidet Quoting-Probleme.)

### Schritt 8: `status.md` initialisieren

Initial-Status:

```markdown
---
projekt: mta-mueller-hausverwaltung-gmbh-2026-05
kunde: Müller Hausverwaltung GmbH
gestartet: 2026-05-14T14:30:00Z
schritte_done:
  - 01-01-mta-projekt-init
schritte_offen:
  - 01-02-kickoff-transcript-parser
  - 02-01-kunden-marken-profil
naechster_empfohlen: 01-02-kickoff-transcript-parser
blockiert: []
---

# MTA-Status: Müller Hausverwaltung GmbH

## ✓ Erledigt

### 01-01-mta-projekt-init
- Erledigt: 2026-05-14 14:30
- Output: Drive-Folder strukturiert, meta.json, status.md, leeres Dashboard

## ⏭ Nächster empfohlener Schritt

**01-02-kickoff-transcript-parser** — Briefing aus dem Kickoff-Meeting-Transkript extrahieren.
```

Hochladen via `upsert-text` mit MIME `text/markdown`.

Lies das vollständige `status.md`-Schema aus `reference/contracts.md`.

### Schritt 9: HTML-Dashboard und Shell hochladen

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

1. **`_shell.html` hochladen:** Lade `reference/report-shell.html` als `_shell.html` in den `reports/`-Sub-Folder. Diese Datei ist das Template, das alle Folge-Skills für ihre eigenen HTML-Reports nutzen.

   ```bash
   python3 scripts/drive.py upsert-text "<reports-folder-id>" "_shell.html" \
     "reference/report-shell.html" "text/html"
   ```

2. **`index.html` rendern und hochladen:** Erzeuge das Dashboard durch Kopieren der Shell und Füllen der Platzhalter:
   - `{{TITLE}}` → "MTA · [Kundenname]"
   - `{{EYEBROW}}` → "MARKE&TING® Analyse"
   - `{{DISPLAY_NAME}}` → Kundenname
   - `{{META_LINE}}` → "Branche: [Branche] · Region: [Region] · Gestartet: [Datum]"
   - `{{MAIN_CONTENT}}` → Status-Übersicht aus `status.md` als HTML (siehe `reference/contracts.md`, Abschnitt "Dashboard-Rendering"). **Im Dashboard-Modus zusätzlich** den Stat-Strip-Counter einbauen — Stat-Strip kommt aus `python3 scripts/token-tracker.py render-counter <slug> --style stat-strip`.
   - `{{TOKEN_BREAKDOWN}}` → Output von `python3 scripts/token-tracker.py render-counter <slug> --style breakdown` (im Dashboard prominent, in Skill-Reports leer lassen)
   - `{{TOKEN_FOOTER}}` → Im Dashboard leer (Breakdown-Sektion ist da schon ausführlich), bei Skill-Reports: Output von `python3 scripts/token-tracker.py render-skill-counter <slug> <skill-name>`
   - `{{FOOTER_TEXT}}` → "MTA · [Kunde] · [Projekt-Slug]"
   - **Zusätzlich:** ersetze `<body>` durch `<body class="is-dashboard">` — blendet den Back-Link im Hero aus, weil das Dashboard sonst auf sich selbst verlinkt.

   Schreibe das Resultat in eine temp-Datei und lade hoch:

   ```bash
   python3 scripts/drive.py upsert-text "<reports-folder-id>" "index.html" \
     /tmp/dashboard-content.html "text/html"
   ```

### Schritt 9b: Initiales `meta/token-usage.json` anlegen

Erstelle einen `meta/`-Sub-Folder im MTA-Drive (`find-or-create-folder "<folder-id>" "meta"`) und lade dort ein initiales `token-usage.json` mit Schema-Stub hoch — der Stop-Hook wird das von Stop-zu-Stop füllen:

```bash
META_FOLDER_ID=$(python3 scripts/drive.py find-or-create-folder "<folder-id>" "meta")
cat > /tmp/token-usage-init.json <<EOF
{"schema_version": "1.0", "slug": "<slug>", "letzte_aktualisierung": "<iso-now>", "gesamt": {"input_tokens": 0, "output_tokens": 0, "cache_creation_5m_tokens": 0, "cache_creation_1h_tokens": 0, "cache_read_tokens": 0, "message_count": 0, "cost_usd": 0.0, "cost_eur": 0.0}, "pro_modell": {}, "pro_skill": {}, "fx_usd_to_eur": 0.92}
EOF
python3 scripts/drive.py upsert-text "$META_FOLDER_ID" "token-usage.json" /tmp/token-usage-init.json "application/json"
```

Die laufende Befüllung passiert ab jetzt automatisch via Stop-Hook (`post-stop-token-sync.sh`) — lokal nach jedem Prompt, Drive-Push gedrosselt alle ~5 Minuten.

### Schritt 10: MTA im lokalen Cache registrieren

```bash
python3 scripts/drive.py register-mta "mta-mueller-hausverwaltung-gmbh-2026-05" \
  "<folder-id>" "Müller Hausverwaltung GmbH"
```

`working_dir` wird vom Skript automatisch als `os.getcwd()` mitgespeichert — wichtig für die robuste Token-Tracker-Auflösung. Folge-Skills (und der Stop-Hook) finden so die MTA-Folder-ID **und** das passende `~/.claude/projects/`-Verzeichnis ohne Heuristik.

### Schritt 11: Status-Pflichtschluss

Gib im Chat strikt diese Struktur aus (siehe `reference/contracts.md` für die exakte Konvention):

```
✓ 01-01-mta-projekt-init abgeschlossen.

MTA angelegt im REACHX Shared Drive:
- Kunde:      Müller Hausverwaltung GmbH
- Slug:       mta-mueller-hausverwaltung-gmbh-2026-05
- Drive:      https://drive.google.com/drive/folders/<id>
- Dashboard:  reports/index.html (auf Drive)
- Status:     status.md (auf Drive)

Lokal:
- Im Active-MTA-Cache registriert. Folge-Skills finden die MTA automatisch.

Nächste Schritte:
1. 01-02-kickoff-transcript-parser — Briefing aus dem Kickoff-Meeting-Transkript extrahieren
   (Hinweis: Lege das Transkript vorab in den Drive-Sub-Folder `input/transkripte/` —
   Drive-Web-UI → in den MTA-Folder → input/transkripte → Drag&Drop.)
2. 02-01-kunden-marken-profil — Markenprofil aus der Website erstellen (direkt möglich, auch ohne Transkript)

Sag mir, welcher als nächster — oder beide nacheinander.
```

Im Resume-Fall (Schritt 4 hatte schon eine `meta.json` gefunden):

```
✓ MTA fortgesetzt — kein Neuanlage notwendig.

MTA-Stand:
- Kunde:      Müller Hausverwaltung GmbH
- Slug:       mta-mueller-hausverwaltung-gmbh-2026-05
- Erledigt:   01-01, 01-02, 02-01 (siehe status.md)
- Nächster:   02-02-wettbewerber-identifikation

Drive:        https://drive.google.com/drive/folders/<id>
Lokal:        Im Active-MTA-Cache aktualisiert.

Soll ich mit 02-02 weitermachen?
```

## Wichtige Konventionen

Dieser Skill ist der erste in der MTA-Skill-Kette und legt die Konventionen fest, an die sich alle weiteren Skills halten. Die vollständigen Vorgaben stehen in **`reference/contracts.md`** — lies sie, wenn du andere MTA-Skills baust oder anpasst.

Zusammengefasst:

- **Outputs leben in Google Drive**, nicht lokal. Alle Folge-Skills nutzen den Helper `01-01-mta-projekt-init/scripts/drive.py`, um Files zu schreiben/lesen/updaten.
- **`meta.json` ist die Single Source of Truth** für Drive-Folder-IDs — Folge-Skills lesen sie einmal beim Start und arbeiten dann mit den IDs.
- **Markdown + YAML-Frontmatter** als Hybrid-Format für inhaltliche Outputs, JSON für rein technische Metadaten.
- **Jeder Folge-Skill updatet `status.md`** (per `upsert_text`, das überschreibt sauber dank `gws files update`) und gibt am Ende eine Empfehlung im standardisierten Format aus.
- **Jeder Folge-Skill schreibt seinen HTML-Report** in den `reports/`-Sub-Folder auf Drive, basierend auf `reports/_shell.html`.
- **Audit-Trail kommt von Drive geschenkt:** Drive zeigt für jeden File "Geändert von: [Kollege]", weil jeder mit seinem eigenen Google-Account schreibt.

## Bundled Resources

- `scripts/drive.py` — **Helper-Modul** für alle Drive-Operationen über `gws` CLI. Hat CLI-Interface (`extract-folder-id`, `validate-folder`, `find-or-create-folder`, `upsert-text`, `read`, `delete`, `register-mta`, `get-mta`, `list-mtas`, `list-children`) und kann auch als Python-Modul importiert werden.
- `scripts/slugify.py` — Kleiner Helper für die konsistente Slug-Erzeugung aus Kundennamen.
- `reference/contracts.md` — Vollständige Konventionen für alle MTA-Skills (status.md-Schema, meta.json-Schema 2.0, Drive-Operations-Konventionen, Standard-Schlussformat, Dashboard-Rendering-Regeln).
- `reference/report-shell.html` — Geteiltes HTML-Template im REACHX-Branding für alle Reports im Projektordner.

## Edge Cases

- **`gws` nicht installiert** — Klare Setup-Anleitung ausgeben, Skill abbrechen. Beispiel-Hinweis: "Bitte einmalig `gws` installieren und mit deinem REACHX-Google-Account authentifizieren. Anleitung: [interner Wiki-Link]."
- **Drive-URL ist Kunden-Ordner statt MTA-Ordner** — Bei `validate-folder` ist das nicht automatisch erkennbar (beides sind Folders mit Schreibrecht). Schutzmechanismus: Wenn der Folder bereits Sub-Folders namens "MTA 2025-..." oder ähnlich enthält und nicht leer ist, frage explizit nach: "Der Folder enthält schon X Items. Bist du sicher, dass das der MTA-Ordner ist und nicht der Kunden-Ordner?"
- **Sonderzeichen im Kundennamen** (Umlaute, &, GmbH-Suffixe) — Slugify-Skript regelt das.
- **Mehrere MTAs für denselben Kunden im selben Monat** — Der Projektleiter legt für jede MTA einen eigenen Drive-Folder an, der Slug ist dadurch eindeutig. Wenn er versehentlich denselben Folder zweimal nutzt, fängt Resume-Check (Schritt 4) das auf.
- **Unvollständige Stammdaten** — niemals ohne Pflicht-Felder anlegen, immer nachfragen.
- **Nutzer wechselt mitten in Schritt 4 die Daten** — wieder bei Schritt 2 ansetzen, Drive-Folder neu validieren, Slug neu berechnen, erneut bestätigen lassen.
- **Drive-API hat Quota erreicht** — `gws` gibt eine 429- oder 403-Fehlermeldung zurück. Skill bricht mit der Original-Fehlermeldung ab und schlägt vor, in 60–120 Sekunden erneut zu versuchen.
- **Kollege ohne Schreibrechte versucht zu initialisieren** — `validate-folder` schlägt mit "Kein Schreibrecht" fehl. Klare Meldung statt zu raten.
