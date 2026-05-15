---
name: 03-11-social-linkedin
description: Erhebt fuer Kunde und Wettbewerber den LinkedIn-Status via Bright-Data plus Apify - Company-Page-Daten (Follower, Industry, Size, HQ), Mitarbeiter-Listing mit Department- und Tenure-Verteilung, Smart-Sample Deep-Profile-Scrape sowie Posts der Company und ausgewaehlter Personen der letzten 12 Monate mit Engagement-Rate, Format-Mix, Themen-Cluster und Post-Qualitaets-Rating. Output ist audits/linkedin-wettbewerb.md plus CSVs plus reports/18-linkedin-wettbewerb.html. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext LinkedIn-Aktivitaet, B2B-Kanal-Fit oder Mitarbeiter-Struktur pruefen will - auch bei Phrasen wie "LinkedIn Audit", "LinkedIn-Wettbewerbsanalyse", "Wer ist auf LinkedIn aktiv", "LinkedIn organic Kanal-Fit", "Mitarbeiter auf LinkedIn", "Posting-Frequenz LinkedIn", "Thought-Leadership-Strategie", "LinkedIn Content-Pillars". Laeuft im MTA-Modus wenn meta.json existiert, sonst Standalone mit output/-Ordner. Ohne wettbewerber/liste.md Kunden-only-Modus.
---

# LinkedIn-Competitor-Research

Stufe-3-Social-Audit fuer LinkedIn organic. Liefert pro Akteur (Kunde plus bestaetigte Wettbewerber) ein vollstaendiges Profil-Bild: Company-Page-Snapshot, Mitarbeiter-Struktur (Department-/Tenure-Verteilung), Posts der Company plus eines Smart-Samples von Personen-Profilen, Engagement-Rate, Format-Mix, Themen-Cluster und Post-Qualitaets-Rating.

Anders als die anderen Social-Audits (Instagram, TikTok, Pinterest) hat LinkedIn drei Daten-Ebenen, die zusammen ausgewertet werden: **Company**, **Mitarbeiter (Listing plus Deep-Sample)** und **Posts (Company plus Personen)**. Daraus laesst sich die fuer B2B-Kunden zentrale Frage beantworten - lohnt LinkedIn organic als Marketing-Kanal?

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

## Zwei Lauf-Modi

Der Skill erkennt automatisch, ob er **innerhalb einer MTA** oder **standalone** laeuft:

### Modus A - MTA (Default wenn `meta.json` gefunden wird)

- Output unter `audits/`, `reports/` im Projekt-Ordner
- Vergleich gegen `wettbewerber/liste.md`
- `status.md` und `reports/index.html` werden aktualisiert
- Branchen-Median und Auffaelligkeiten werden berechnet
- Schlussformat nach `contracts.md` Abschnitt 6

### Modus B - Standalone (Fallback wenn keine `meta.json`)

- Output unter `output/{competitor_slug}/` im aktuellen Working-Directory
- Pro Wettbewerber ein Einzel-Report (`report.md`)
- Bei mehreren Wettbewerbern zusaetzlich `aggregate_comparison.md`
- Kein `status.md`-Update, kein Dashboard
- Schlussformat als kurzer Kommentar im Chat

Der Modus wird **nicht vom Nutzer gewaehlt**, sondern aus der Umgebung erkannt - `meta.json` da: MTA. `meta.json` nicht da: Standalone.

## Output-Ebenen im MTA-Modus

1. **Aggregat-Markdown** `audits/linkedin-wettbewerb.md` - Profil-Matrix, Mitarbeiter-Aggregat, Posts-Statistik, Content-Pillars, Auffaelligkeiten pro Akteur
2. **Company-CSV** `audits/linkedin-companies.csv` - eine Zeile pro Akteur mit Company-Kennzahlen
3. **Employees-CSV** `audits/linkedin-employees.csv` - alle gelisteten Mitarbeiter pro Akteur
4. **Posts-CSV** `audits/linkedin-posts.csv` - Posts-Sample mit Rating
5. **Roh-Daten** (gzip-komprimiert auf Drive) `assets/raw/linkedin-company-SLUG.json.gz`, `assets/raw/linkedin-employees-SLUG.json.gz`, `assets/raw/linkedin-posts-SLUG.json.gz`
6. **HTML-Report** `reports/18-linkedin-wettbewerb.html` - Strategen-Report aus `reports/_shell.html`

**Wichtige Begrenzung:** Cookie-frei zugaengliche LinkedIn-Daten sind eingeschraenkt. Posts-Historie umfasst typischerweise nur 4-8 Wochen, nicht 12 Monate. Mitarbeiter-Listing zeigt ~80-90% der LinkedIn-sichtbaren Mitarbeiter. Tenure-Daten sind nur fuer ~50-70% der Deep-Scrapes verwertbar. Coverage-Quoten werden im Output transparent ausgewiesen.

**Branchen-Relevanz-Hinweis:** Bei reinen B2C-Branchen (Lifestyle, lokale Dienstleistung, Endkunden-Handel) ist LinkedIn organic oft Nebenkanal. Der Skill laeuft trotzdem - die Auffaelligkeit `branche_linkedin_unueblich` markiert das fuer die Synthese, damit `04-02-kanal-chancen-analyse` LinkedIn nicht ueberbewertet.

## Wann triggern

- "LinkedIn Audit"
- "LinkedIn-Wettbewerbsanalyse"
- "Wer ist auf LinkedIn aktiv"
- "LinkedIn organic Kanal-Fit"
- "Department-Verteilung Wettbewerber"
- "Mitarbeiter auf LinkedIn"
- "Posting-Frequenz LinkedIn"
- "Thought-Leadership-Strategie"
- "LinkedIn Content-Pillars"
- "ist LinkedIn ein Kanal fuer uns"

## Voraussetzungen

- **MTA-Modus:** `01-01-mta-projekt-init` gelaufen → MTA registriert, `meta.json` im Drive-MTA-Root
- Bright-Data-Zugang (MCP-Connector ODER `BRIGHTDATA_API_TOKEN` plus 3 Dataset-IDs) - siehe `reference/backends.md`
- Apify-Zugang (MCP-Connector ODER `APIFY_TOKEN`) - zwingend fuer Mitarbeiter-Listing
- Empfohlen: `wettbewerber/liste.md` (Drive) mit `status: bestaetigt` - sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` und `wettbewerber/SLUG.md` (Drive) mit Touchpoint-Inventur (`typ: linkedin`) - daraus zieht der Skill die Company-URLs
- Optional: Schwester-Skill `03-12-social-linkedin-post-quality` fuer die Post-Bewertung (Fallback eingebaut wenn nicht verfuegbar)

## Ablauf

### Schritt 0: MTA-Kontext ermitteln (nur MTA-Modus)

Folge `contracts.md` Abschnitt 1. Ermittle Drive-Folder-IDs:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WETTBEWERBER_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Wenn `get-mta` nichts liefert → Modus **Standalone**.

### Schritt 1: Modus-Erkennung und Projekt-Auffindung

- **MTA gefunden** (Schritt 0 lieferte `FOLDER_ID`) → Modus **MTA**. Lies `wettbewerber/liste.md` aus Drive (`WETTBEWERBER_ID` via `find_by_name` + `read_text`). Wenn `status: bestaetigt` → Modus **MTA-Voll**; sonst → Modus **MTA-Kunden-only** mit Hinweis.
- **Nicht gefunden** → Modus **Standalone**. Erfrage Company-URL(s) vom Nutzer. Kein `status.md`-Update am Ende. Standalone-Outputs bleiben im lokalen `output/`-Ordner (kein Drive).

### Schritt 2: Backend-Discovery

Pruefe **pro Backend** in dieser Reihenfolge:

1. **MCP-Connector** verfuegbar (Tools mit Prefix `mcp__Apify__*` oder `mcp__BrightData__*`)? → nutzen
2. **HTTP-API** mit Env-Var-Token (`BRIGHTDATA_API_TOKEN` plus Dataset-IDs, `APIFY_TOKEN`)? → nutzen
3. **Nichts** → User-Setup-Hinweis, kein Scrape starten

Setup-Status zusammenfassen ("Bright Data ueber Connector, Apify ueber HTTP-API"). Details in `reference/backends.md`.

**Wichtig:** Bright Data hat in der Standard-Konfiguration **keinen** Endpoint fuer "alle Mitarbeiter zu Company URL". Mitarbeiter-Listing **zwingend** ueber Apify. Alle anderen Schritte koennen ueber Bright Data laufen.

### Schritt 3: Company-URL-Match pro Akteur

Pro Akteur die LinkedIn-Company-URL ziehen:

- **MTA-Modus / Kunde:** aus `data/kunde.md` (Drive `DATA_ID`) Frontmatter-Feld `touchpoints` einen Eintrag mit `typ: linkedin` suchen
- **MTA-Modus / Wettbewerber:** pro Eintrag aus `liste.md` mit gueltiger `slug` aus `wettbewerber/SLUG.md` (Drive `WETTBEWERBER_ID`) Touchpoint-Inventur ziehen
- **Standalone-Modus:** Company-URL(s) vom Nutzer im Prompt

URL-Normalisierung:

- `linkedin.com/company/handle` → `https://www.linkedin.com/company/handle/`
- Trailing-Slash standardisieren
- Query-Params entfernen
- Sales-Navigator-Formate (`linkedin.com/sales/...`) auf Public-Page-Form normalisieren

**Akteure ohne LinkedIn-Profil:**

- Skip mit Hinweis `kein_linkedin_profil_identifiziert`
- Wenn der Kunde keine Company-Page hat: separate Auffaelligkeit `kunde_kein_linkedin_profil`

### Schritt 4: Existenz-Check Output

**MTA-Modus:** via `list-children` auf `AUDITS_ID` prüfen, ob `linkedin-wettbewerb.md`, `linkedin-companies.csv`, `linkedin-employees.csv` oder `linkedin-posts.csv` bereits im Drive `audits/`-Folder existieren. **Standalone:** lokales `output/`-Verzeichnis prüfen. Bei Konflikt fragen (ueberschreiben / Backup-und-neu / abbrechen).

### Schritt 5: Company-Page-Scrape pro Akteur

Backend: **Bright Data** (Fallback Apify). Details: `reference/backends.md` Abschnitt "Company API".

Erwartete Felder: `name`, `linkedin_url`, `industry`, `company_size`, `headquarters`, `founded`, `follower_count` (kritisch fuer ER), `description`, `specialties`, `website`, `employees_count`.

Roh-Daten lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/linkedin-company-SLUG.json` (MTA) bzw. `output/SLUG/company.json` (Standalone). Im MTA-Modus am Skill-Ende gzip-komprimiert nach Drive `assets/raw/` (siehe Schritt 16).

### Schritt 6: Mitarbeiter-Listing pro Akteur

Backend: **Apify** (zwingend - Bright Data hat keinen Endpoint fuer Company → Employees).

Empfohlener Actor: `harvestapi/linkedin-profile-search`. Input-Schema: siehe `reference/backends.md` Abschnitt "Apify - Mitarbeiter-Listing".

**Volume-Limit:** Bei >500 Mitarbeitern auf der Page nur die ersten 200 scrapen (konfigurierbar). Mehr braucht das Aggregat nicht.

URL-Hygiene: `profile_url` muss im Format `https://www.linkedin.com/in/...` sein, nicht Sales-Navigator.

### Schritt 7: Department- und Tenure-Analyse aus Listing

Klassifiziere jeden Mitarbeiter nach Headline/Position in einen Bucket (Leadership, Marketing, Sales, Engineering, Product, HR, Finance, Operations, Customer Success, Legal, Other). Regeln in `reference/sampling.md`.

**C-Level schlaegt Funktion** ("CMO" → Leadership, nicht Marketing).

Tenure-Verteilung wenn aus dem Listing direkt verfuegbar - sonst erst nach Schritt 9 (Deep-Scrape) berechnen.

Optionales Helper-Script: `scripts/analyze_employees.py` (Department-Klassifizierung plus Tenure-Aggregation).

### Schritt 8: Smart Sampling - 10 Profile auswaehlen

Stratifizierte Auswahl nach Default-Verteilung:

- 1-2 Leadership / C-Level
- 3-4 Marketing / Sales / Comms
- 1-2 Product
- 1-2 HR / People
- 1-2 Andere

Auswahl-Regeln in `reference/sampling.md` (Sample-Strategie, Bevorzugung, Spezialfaelle). Override moeglich (z. B. "nur C-Level" oder "alle Marketing").

### Schritt 9: Deep-Profile-Scrape

Backend: **Bright Data** (People Profiles API).

Pro ausgewaehltes Profil vollstaendigen Scrape mit Karriere-Historie. Felder: `experience` (Liste), `education`, `skills`, `current_position` mit `start_date` (fuer exakte Tenure).

Coverage-Erwartung: ~50-70% liefern brauchbare Tenure-Daten. Coverage im Output transparent ausweisen.

### Schritt 10: Company-Posts-Scrape

Backend: **Bright Data** (Posts API, "Discover by company url").

Hard-Cap: 50 Posts pro Account, 12-Monats-Zeitraum als Filter (LinkedIn liefert cookie-frei oft nur 4-8 Wochen - das ist OK).

Felder: `post_id`, `post_url`, `post_text`, `date_posted`, `format` (text/image/carousel/video/document/article/poll/repost), `likes`, `reposts`, `comments`, `reactions_breakdown` falls verfuegbar.

### Schritt 11: Personen-Posts-Scrape

Pro Person aus dem Smart-Sample (Schritt 8) die letzten ~30 Posts. Backend wie Company-Posts.

Zusatz-Felder: `author_name`, `author_position`.

### Schritt 12: Post-Qualitaets-Rating

Wenn Schwester-Skill `03-12-social-linkedin-post-quality` verfuegbar: aufrufen, pro Post 5-Dimensionen-Rating plus Themen-Cluster plus Tonalitaet plus Gesamtnote.

**Fallback:** vereinfachte Inline-Bewertung, im Output vermerken ("vereinfachte Bewertung verwendet").

Account-Median fuer Performance-Ratio: bei <10 Posts pro Account Branchen-Benchmark nutzen (siehe `03-12-social-linkedin-post-quality/references/benchmarks.md`).

### Schritt 13: Aggregat-Statistik pro Akteur

Aus den Posts berechnen:

- **Posting-Frequenz** (Posts pro Woche, Company plus Personen separat plus gesamt)
- **Format-Mix** (Prozent-Verteilung der Formate)
- **Themen-Cluster-Verteilung** (was wird worueber gepostet, aus Rating-Skill oder Heuristik)
- **Tonalitaets-Mix**
- **Engagement-Rate** (Company und Personen separat, Median plus P25/P75)
- **Top-3- und Bottom-3-Posts** mit Begruendung
- **Best-performing Format** und **Best-performing Cluster**

Optionales Helper-Script: `scripts/calculate_engagement.py` (ER plus Format-/Cluster-Performance plus Top/Bottom-Posts).

### Schritt 14: Branchen-Median-Berechnung (nur MTA-Voll-Modus)

Aus allen Wettbewerbs-Akteuren (ohne Kunde) den Median der ER (Company plus Personen) berechnen. Bei <3 WBs mit Daten: Branchen-Benchmark-Default 2.5% (Company) bzw. 4.0% (Personen), im Output mit Hinweis ausweisen.

### Schritt 15: Auffaelligkeiten

Aus den erhobenen Daten (Mindest-Erwartung: 6 Typen):

| Typ | Ausloeser | Beispiel |
|---|---|---|
| `kunde_kein_linkedin_profil` | Kunde hat keine Company-Page in Touchpoint-Inventur | "Kunde ohne LinkedIn-Company-Page - bei B2B-Branche kritisch, eventuell uebersehen oder ueberhaupt nicht angelegt" |
| `kunde_inaktiv_seit_X_wochen` | Kunde hat 0 Posts in den letzten X Wochen (X >= 4) | "Kunde hat seit 14 Wochen nicht gepostet - Page wirkt verwaist, Vertrauens-Risiko" |
| `kunde_engagement_unter_branchen_median` | Kunden-ER < 0.7 × Branchen-Median | "Kunde 0.8% ER, Branchen-Median 3.1% - Content-Qualitaet oder Targeting hinterfragen" |
| `wettbewerber_thought_leadership_strategie` | Mindestens 1 WB mit hoher Personen-Posts-Aktivitaet (>=5 aktive Poster, ER Personen > Company × 1.5) | "alpha-tech setzt auf Personal-Branding der Fuehrungskraefte - 4 C-Level-Profile mit Ø 6 Posts/Monat, doppelte ER vs. Company-Page" |
| `content_pillar_luecke_kunde` | Pillar bei >2 WBs aktiv (>=5 Posts), bei Kunde fehlend | "WBs bespielen Pillar 'kunden_referenz' regelmaessig, Kunde nicht - Trust-Signal-Luecke" |
| `posting_frequenz_diskrepanz` | WB-Median >= 3× Kunden-Frequenz | "WBs posten im Median 3x/Woche, Kunde 0.5x/Woche - Sichtbarkeits-Luecke" |
| `format_strategie_unterschied` | WB-Top-Format dominiert (>40%), Kunde mit anderem Top-Format | "WBs setzen >50% auf Document-Posts mit Carousel-Format, Kunde fast nur Text-Posts - Reichweiten-Format ungenutzt" |
| `branche_linkedin_unueblich` | >60% WBs ohne Page ODER WB-Median Posts/Woche < 0.5 | "Branche ist auf LinkedIn strukturell schwach - LinkedIn in 04-02-kanal-chancen-analyse als Nebenkanal markieren" |

Pro Auffaelligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure.

### Schritt 16: Output-Files schreiben

**MTA-Modus** - Upload nach Drive in dieser Reihenfolge:

1. `audits/linkedin-companies.csv` → `AUDITS_ID` via `upsert-text`. Schema in `reference/linkedin-output-schema.md`
2. `audits/linkedin-employees.csv` → `AUDITS_ID`
3. `audits/linkedin-posts.csv` → `AUDITS_ID`
4. `audits/linkedin-wettbewerb.md` → `AUDITS_ID` (Aggregat-Markdown mit Frontmatter und Body)
5. Roh-JSONs aus `~/.cache/reachx-mta/<slug>/raw/linkedin-*.json` gzip-komprimieren und nach Drive `assets/raw/` hochladen (Apify- und Bright-Data-Outputs koennen mehrere MB sein, gzip Pflicht):
   ```bash
   RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
   for f in ~/.cache/reachx-mta/<slug>/raw/linkedin-*.json; do
     gzip -k "$f"
     python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
   done
   ```

**Standalone-Modus:** Output unter `output/{competitor_slug}/` im lokalen Filesystem (kein Drive):

- `report.md` (aus `assets/report_template.md`)
- `company.json`, `employees_listing.csv`, `employees_deep.csv`, `company_posts.csv`, `people_posts.csv`
- Bei >=2 Wettbewerbern zusaetzlich `output/aggregate_comparison.md` (aus `assets/aggregate_template.md`)

### Schritt 17: HTML-Report `reports/18-linkedin-wettbewerb.html` (nur MTA)

Aus `reports/_shell.html` (aus Drive `REPORTS_ID` lesen via `find_by_name` + `read_text`) mit den Standard-Platzhaltern:

- `{{TITLE}}` - "LinkedIn-Wettbewerb · KUNDE_NAME"
- `{{EYEBROW}}` - "MTA-Audit"
- `{{DISPLAY_NAME}}` - "LinkedIn-Wettbewerbsanalyse"
- `{{META_LINE}}` - "Erstellt: ISO-DATUM · Quelle: Bright Data + Apify · N Akteure"
- `{{MAIN_CONTENT}}` - Inhalt (siehe unten)
- `{{FOOTER_TEXT}}` - "MTA-Audit · Datenquelle Bright Data + Apify"

Content-Sektionen in `{{MAIN_CONTENT}}`:

- **Stat-Strip oben**: Akteure mit Page, aktive Akteure, Branchen-Median-ER, Top-Engagement-Akteur, Top-Reach
- **Sticky-TOC** zu allen Sektionen
- **Branchen-Relevanz-Banner** oben (wenn schwach: rote Hervorhebung mit Hinweis fuer `04-02-kanal-chancen-analyse`)
- **Company-Profil-Matrix-Tabelle**: Akteur × Follower × Posts/Woche × ER × Format-Top
- **Mitarbeiter-Aggregat-Tabelle**: Akteur × Listing-Size × Top-Department × Median-Tenure × Aktive-Poster
- **Pro Akteur** ein `details class="skill"`-Block mit:
  - Company-Header (Name, Industry, Size, HQ, Follower)
  - Mitarbeiter-Struktur (Department-Verteilung als Mini-Tabelle, Tenure-Buckets)
  - Posts-Statistik als Mini-Stat-Strip
  - Format-Mix als kleine Balken
  - Top-3-Posts als Karten (mit Text-Auszug, ER-Wert, Format-Badge)
  - Content-Pillars als Tag-Liste
- **Content-Pillars-Branchen-Uebersicht**: Pillars die mehrere WBs bespielen, mit Akteurs-Verteilung
- **Auffaelligkeiten** als `.suggestion`-Block
- Footer mit Datenquellen-Hinweis und Backend-Namen

### Schritt 18: status.md plus Dashboard-Update (nur MTA)

Folge `contracts.md` Abschnitt 3 und 7. `status.md` und `reports/index.html` aus Drive (`FOLDER_ID` bzw. `REPORTS_ID`) lesen, aktualisieren, via `upsert-text` zurueckschreiben:

- `03-11-social-linkedin` in `schritte_done` (Frontmatter), aus `schritte_offen` entfernen
- Eigene Sektion unter "✓ Erledigt" mit Datum, Outputs (Drive-Pfade), Hinweisen ("4 von 7 Akteuren mit Company-Page, Branchen-Relevanz stark, Kunde-Frequenz unter Branchen-Median")
- `naechster_empfohlen` setzen: passender naechster Social-Skill (`03-08-social-instagram` / `03-09-social-tiktok`) oder `04-02-kanal-chancen-analyse` wenn genug Audits durch
- Dashboard `reports/index.html` ergaenzen um Link auf den neuen Report (Stat-Strip aktualisieren, Reports-Liste, `<body class="is-dashboard">` beibehalten)

### Schritt 19: Standard-Schlussformat im Chat

**MTA-Modus:**

```
✓ 03-11-social-linkedin abgeschlossen.

Outputs (auf Drive):
- audits/linkedin-wettbewerb.md - Aggregat mit Profil-Matrix und Mitarbeiter-Struktur
- audits/linkedin-companies.csv - Company-Daten (N Akteure)
- audits/linkedin-employees.csv - Mitarbeiter-Listing (E Mitarbeiter aggregiert)
- audits/linkedin-posts.csv - Posts-Sample mit Rating (P Posts)
- assets/raw/linkedin-*.json.gz - komprimierte Roh-Daten
- reports/18-linkedin-wettbewerb.html - Strategen-Report
Status aktualisiert in: status.md

LinkedIn-Lage:
- Akteure mit Company-Page:    M von N
- Aktiv (Posts in 12mo):       A
- Branchen-Median-ER Company:  X.X %
- Branchen-Median-ER Personen: Y.Y %
- Top-Engagement-Akteur:       AKTEUR mit Z.Z %
- Posting-Frequenz-Branche:    F Posts/Woche (Median)
- Content-Pillars erkannt:     P (branchenweit)

[Wenn Auffaelligkeiten:]
⚠ LinkedIn-Insights:
- (1-3 Top-Auffaelligkeiten)

[Wenn Branche LinkedIn-unueblich:]
ℹ Branchen-Relevanz schwach
- LinkedIn ist in dieser Branche strukturell schwach - in 04-02-kanal-chancen-analyse als Nebenkanal werten.

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestaetigt - LinkedIn-Lage nur fuer den Kunden, kein Branchen-Benchmark.

[Wenn Backend-Probleme:]
ℹ Coverage-Hinweise
- Posts-Historie cookie-frei auf X Wochen begrenzt, Tenure-Coverage Y %

Naechste Schritte:
1. 03-08-social-instagram - analoges Pattern fuer Instagram, falls B2C-Komponente
2. (parallel moeglich) 03-09-social-tiktok - bei videoaffinen Branchen
3. (parallel moeglich) 04-02-kanal-chancen-analyse - wenn 4-5 Audits durch sind

Sag mir, welcher als naechster.
```

**Standalone-Modus:** kuerzere 3-5-zeilige Zusammenfassung im Chat (wie viele Wettbewerber, wie viele Posts gescraped, wichtigster Befund), kein status.md-Block.

## Bundled Resources

- `reference/backends.md` - Bright-Data plus Apify API-Aufrufe, MCP-vs-HTTP-Erkennung, Datasets-IDs, Hybrid-Modell, Schema-Normalisierung
- `reference/sampling.md` - Department-Klassifizierung (Trigger-Listen DE/EN), Smart-Sampling-Strategie, Tenure-Berechnung
- `reference/linkedin-output-schema.md` - CSV-Schemas (Companies, Employees, Posts), Markdown-Frontmatter, Validierungs-Regeln
- `scripts/analyze_employees.py` - Helper fuer Department-/Tenure-Aggregation (optional, manuelle Berechnung als Fallback)
- `scripts/calculate_engagement.py` - Helper fuer ER plus Format-/Cluster-Performance (optional)
- `assets/report_template.md` - Markdown-Template fuer Standalone-Einzelreport
- `assets/aggregate_template.md` - Markdown-Template fuer Standalone-Vergleichsreport

## Edge Cases

- **Sehr kleines Unternehmen (< 10 Mitarbeiter auf LinkedIn):** Smart-Sampling scraped alle vorhandenen, im Report Hinweis "Sample-Groesse N statt 10".
- **Mega-Account (>100K Follower):** ER ist strukturell niedriger (Account-Groesse-Effekt). Skill weist das im Akteurs-Sub-Block aus, vergleicht nicht direkt mit kleinen Akteuren.
- **Konzern mit Tochterfirmen:** Skill scraped nur die in der Touchpoint-Inventur eingetragene Company-Page. Wenn Stratege mehrere will: Override "auch CHILD_PAGE_2 scrapen".
- **C-Level postet privat statt Company:** Personal-Posts-Sample faengt das auf, Auffaelligkeit `wettbewerber_thought_leadership_strategie` triggert.
- **Cookie-frei nur 4-8 Wochen Posts statt 12 Monate:** das ist LinkedIn-Limit, kein Backend-Problem. Skill kommuniziert das im Coverage-Block.
- **Mitarbeiter-Listing zeigt nur 80 von 200 Mitarbeitern:** das ist LinkedIn-Limit (Public-Profile-Sichtbarkeit). Skill weist das aus, rechnet Statistik trotzdem aus dem verfuegbaren Sample.
- **Apify-Actor liefert Sales-Navigator-URLs statt `/in/...`:** Skill normalisiert beim Mapping ins Internal-Schema. Sales-Navigator-URLs ohne Public-Slug werden ausgeschlossen.
- **Bright-Data-Snapshot dauert >5 Minuten:** Skill pollt bis 10 Minuten, dann Hinweis im Output "Snapshot timeout, eventuell spaeter erneut versuchen".
- **Personen ohne aktuelle Position (`Open to work`):** Tenure-Berechnung wird uebersprungen, Profil bleibt im Listing aber nicht im Sample-Pool (Schritt 8 Bevorzugung).
- **Backend-Fehler (Connector down):** ein Retry nach 30 Sek, dann User-Hinweis. Nicht stillschweigend wechseln.
- **Standalone-Modus ohne `meta.json` aber mehrere Company-URLs:** Skill faehrt alle sequenziell, schreibt `aggregate_comparison.md` mit Rangliste plus Format-Heatmap plus strategischer Empfehlung.

## Wichtige Konventionen

Im MTA-Modus sind alle in `contracts.md` definierten Konventionen verbindlich:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown plus YAML-Frontmatter fuer Aggregat, CSVs fuer Roh-Daten
- Standard-Schlussformat (Outputs-Block, Statistik, ggf. Auffaelligkeiten, Naechste-Schritte-Block, "Sag mir, welcher als naechster")
- `status.md` und `reports/index.html` werden aktualisiert
- HTML-Report aus `reports/_shell.html` mit Standard-Platzhaltern (aus Drive)
- **Roh-Daten** gzip-komprimiert in Drive `assets/raw/linkedin-*-SLUG.json.gz` als Cache (lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/raw/`)
- **Captions und Post-Texte unveraendert** lassen - Originaltexte sind die Datenbasis, keine Uebersetzungen oder Umformulierungen
- **Engagement-Rate auf 4 Nachkommastellen** in der CSV, im Markdown als Prozent mit 1 Nachkommastelle
- **Branchen-Relevanz-Hinweis ist Pflicht** im Output - bei B2C-Branchen explizit dokumentieren, dass LinkedIn Nebenkanal ist
- **Coverage-Quoten transparent ausweisen** - LinkedIn liefert nie 100%, das wird im Output nicht aufpoliert
