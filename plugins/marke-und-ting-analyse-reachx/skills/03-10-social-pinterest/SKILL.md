---
name: 03-10-social-pinterest
description: Vollständige Pinterest-Wettbewerbsanalyse für Kunde + alle bestätigten Wettbewerber. Pro Akteur Profil-Daten (Follower, Following, Boards, Pins gesamt, Bio, verifiziert, Business-Account), Top-10-Boards-Übersicht mit Pin-Anzahl und Follower pro Board, Pin-Sample der letzten 12 Monate mit Hard-Cap 40 Pins (Typ, Title, Beschreibung, Saves, Comments, Board-Zugehörigkeit, Tags), plus Content-Pillars über Board-Themen und Pin-Tokens. Output ist audits/pinterest-wettbewerb.md plus audits/pinterest-profile.csv plus audits/pinterest-pins.csv plus HTML-Report. Branchenrelevanz-Hinweis bei B2B / Recht / Finanzen prominent. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Pinterest-Aktivität von Kunde und Wettbewerbern prüfen will - auch bei Phrasen wie "Pinterest Check", "Pinterest Wettbewerber", "wer ist auf Pinterest", "Pinterest Pins prüfen", "Boards der Konkurrenz", "Pinterest Idea Pins", "Pinterest Strategie". Setzt 01-01-mta-projekt-init voraus; ohne wettbewerber/liste.md läuft der Skill im Kunden-only-Modus.
---

# Pinterest-Competitor-Research

Stufe-3-Social-Audit, analog zu `03-08-social-instagram` und `03-11-social-linkedin`. Prüft für Kunde + alle bestätigten Wettbewerber die Pinterest-Aktivität - Profil-Größe, Boards-Struktur, Pin-Sample der letzten 12 Monate, Engagement und thematische Content-Pillars.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/pinterest-wettbewerb.md` - Profil-Matrix, Boards-Themen pro Akteur, Pin-Typen-Verteilung, Engagement-Vergleich, Content-Pillars, Auffälligkeiten
2. **Profile-CSV** `audits/pinterest-profile.csv` - eine Zeile pro Akteur mit Profil-Kennzahlen + Boards-Übersicht
3. **Pins-CSV** `audits/pinterest-pins.csv` - eine Zeile pro Pin im Sample mit Engagement-Daten
4. **HTML-Report** `reports/17-pinterest-wettbewerb.html` - Stat-Strip, Heatmap, Akteurs-Karten, Content-Pillars

**Wichtige Begrenzungen von Pinterest-Scraping:**

- Pinterest API ist für Drittanbieter eingeschränkt - Apify-Actors arbeiten Web-basiert
- Login meist nicht nötig für öffentliche Profile, aber bei sehr großen Profilen kann Pinterest die Auslieferung drosseln
- Reine Saves-Counts werden teils geschätzt angezeigt (Apify nimmt den angezeigten Wert)
- Idea-Pins sind ein Pinterest-spezifisches Story-Format; Erfassbarkeit variiert je nach Actor
- Pinterest-Branchen-Fit: stark für Lifestyle, Home and Garden, Mode, DIY, Wedding, Food, Reise; schwach für B2B-Industrie, Recht, Finanzen - Skill markiert das explizit

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

- "Pinterest Check"
- "Pinterest Wettbewerber"
- "Wer ist auf Pinterest"
- "Pinterest Pins prüfen"
- "Boards der Konkurrenz"
- "Pinterest Idea Pins"
- "Pinterest Strategie"
- "Pinterest-Aktivität analysieren"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA registriert, `meta.json` im Drive-MTA-Root
- Apify-Zugang verfügbar (für Pinterest-Scraping - die zentralen Apify-Actors sind in `reference/pinterest-tools-mapping.md` dokumentiert)
- Empfohlen: `wettbewerber/liste.md` (Drive) mit `status: bestaetigt` - sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` und `wettbewerber/AKTEURSSLUG.md` (Drive) mit `touchpoints`-Inventur - daraus kommen die Pinterest-Usernames. Wenn nicht vorhanden, versucht der Skill die Auflösung via Pinterest-Search.

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

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

Wenn `get-mta` nichts liefert: Abbruch mit Hinweis "01-01-mta-projekt-init zuerst aufrufen".

### Schritt 1: Voraussetzungs-Check

Lies `wettbewerber/liste.md` aus Drive (`WETTBEWERBER_ID` via `find_by_name` + `read_text`). Wenn vorhanden mit `status: bestaetigt` → Modus **Voll**; sonst → Modus **Kunden-only** mit Hinweis.

Prüfe Apify-Zugang (analog zu anderen Apify-nutzenden Skills). Bei fehlendem Zugang: Abbruch mit Hinweis.

**Branchen-Fit-Vorab-Check**: Wenn `meta.json.branche` oder `data/kunde.md` (Drive) auf eine Pinterest-unfreundliche Branche hinweist (B2B-Industrie, Recht, Steuerberatung, Finanzen, klassisches SaaS), setze internen Flag `branchen_fit_pinterest: niedrig` und gebe später im Output einen Branchen-Hinweis-Block aus. Skill läuft trotzdem durch - Null-Ergebnisse sind wertvoll, weil sie eine strategische Annahme datenbasiert untermauern.

Bei Pinterest-starken Branchen (Lifestyle, Home and Garden, Mode, DIY, Wedding, Food, Reise, Beauty, Kinder, Hochzeit, Interior, Garten): Flag `branchen_fit_pinterest: hoch`. Bei neutralen Branchen: `branchen_fit_pinterest: mittel`.

### Schritt 2: Akteurs-Liste mit Pinterest-Username-Match zusammenstellen

Pinterest-spezifische Logik: der Match erfolgt über den **Pinterest-Username** (URL-Form `https://www.pinterest.com/USERNAME/`).

Reihenfolge der Quellen pro Akteur (alle Files aus Drive lesen):

1. **Aus Marken-Profil**: in `data/kunde.md` (Drive `DATA_ID`) bzw. `wettbewerber/AKTEURSSLUG.md` (Drive `WETTBEWERBER_ID`) unter `touchpoints` nach `typ: pinterest` suchen
2. **Aus Briefing**: in `data/briefing.md` (Drive `DATA_ID`) nach erwähnten Pinterest-Profilen
3. **Pinterest-Search via Apify**: wenn nichts gefunden, Apify-Search-Actor mit dem Akteurs-Namen, Top-Treffer als Kandidat - nur übernehmen wenn der gefundene Account-Name oder die Website mit dem Akteur eindeutig matcht
4. **Skip-Fallback**: wenn auch das nicht eindeutig ist, Akteur als `pinterest_username_unbekannt: true` markieren und im Output zur Strategen-Review aufführen. Kein automatisches Raten.

Pro Akteur dokumentieren:

- `pinterest_username` (sobald aufgelöst)
- `pinterest_url` (kanonische URL)
- `match_methode`: `touchpoint | briefing | apify_search | nicht_gefunden`
- `match_konfidenz`: `hoch | mittel | niedrig | nicht_gefunden`

### Schritt 3: Existenz-Check Output

Via `list-children` auf `AUDITS_ID` prüfen, ob `pinterest-wettbewerb.md`, `pinterest-profile.csv` oder `pinterest-pins.csv` bereits im Drive `audits/`-Folder existieren: fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt 4: Profil-Scrape pro Akteur

Pro Akteur mit aufgelöstem Username (siehe `reference/pinterest-tools-mapping.md`):

1. **Apify-Actor aufrufen** - Standard: `apify/pinterest-scraper` oder `epctex/pinterest-scraper`, Fallback: `apify/puppeteer-scraper` mit Custom-Page-Function
2. **Profil-Daten extrahieren**:
   - `username`
   - `display_name`
   - `bio_text`
   - `follower_count`
   - `following_count`
   - `boards_count`
   - `pins_count_gesamt`
   - `verifiziert`: bool
   - `business_account`: bool
   - `website_verifiziert` (im Profil hinterlegte und von Pinterest verifizierte Domain, wenn sichtbar)
   - `account_typ`: `personal | business | unbekannt`
   - `region` (falls Pinterest das in den Profil-Metadaten ausgibt)

3. **Roh-Daten ablegen** im lokalen Arbeits-Cache unter `~/.cache/reachx-mta/<slug>/raw/pinterest-profile-AKTEURSSLUG.json` - Upload gzip-komprimiert nach Drive `assets/raw/` am Skill-Ende (siehe Schritt 13)

### Schritt 5: Boards-Übersicht pro Akteur

Pro Akteur die Liste aller Boards holen, daraus die Top-10 nach Follower-Anzahl bzw. Pin-Anzahl (Sortierung dokumentieren, Default: Follower-Anzahl).

Pro Board:

- `board_slug` (aus URL)
- `board_name`
- `board_beschreibung` (falls verfügbar)
- `pin_anzahl`
- `follower_anzahl`
- `letzter_pin_datum` (falls verfügbar)
- `board_thema_inferiert` (heuristisch aus Title + Beschreibung)

Wenn ein Akteur weniger als 10 Boards hat: alle Boards in die Übersicht aufnehmen.

### Schritt 6: Pins-Scrape pro Akteur

Pro Akteur die letzten Pins über alle Boards einsammeln. **Hard-Cap 40 Pins** pro Akteur (chronologisch absteigend, jüngste zuerst). Zeitfenster: letzte 12 Monate.

Pro Pin:

- `pin_id` (Pinterest-eigene ID)
- `pin_url`
- `pin_title`
- `pin_beschreibung`
- `pin_typ`: `standard | video | idea | product | unbekannt`
- `created_at` (ISO-8601)
- `saves_count`
- `comments_count`
- `domain_link` (Domain der hinterlegten Quelle - eigene Domain, Drittanbieter, oder leer)
- `landingpage_url` (falls vorhanden)
- `board_slug` (Board-Zugehörigkeit)
- `board_name`
- `tags` (Liste, soweit Pinterest sie öffentlich ausgibt)
- `creative_url` (Pin-Bild / Video-Thumbnail)

Wenn ein Akteur weniger als 40 Pins in 12 Monaten hat: alle Pins. Wenn ein Akteur 0 Pins in 12 Monaten hat: `letzte_pin_datum_vor_12m: true` markieren.

Roh-Daten ablegen im lokalen Arbeits-Cache unter `~/.cache/reachx-mta/<slug>/raw/pinterest-pins-AKTEURSSLUG.json` - Upload gzip-komprimiert nach Drive `assets/raw/` am Skill-Ende (siehe Schritt 13).

### Schritt 7: Aktivitäts-Berechnung pro Akteur

Pro Akteur aus dem Pin-Sample:

- `pins_im_zeitfenster_12m`: int
- `pins_pro_woche_median`: float (Median über die Wochen mit mindestens einem Pin)
- `wochen_seit_letztem_pin`: int
- `aktivitaets_status`: `aktiv | gering_aktiv | inaktiv | kein_profil`
  - aktiv: mindestens 1 Pin pro Woche im Median
  - gering_aktiv: 0,2 bis 1 Pin pro Woche im Median
  - inaktiv: weniger als 0,2 oder letzte Pin älter als 8 Wochen
  - kein_profil: kein auflösbarer Username
- `pin_typen_verteilung`: dict mit Prozent-Anteilen pro Typ
- `engagement_pro_pin_median`: float (Saves + Comments durch Anzahl Pins im Sample)
- `engagement_rate_proxy`: float (Engagement-pro-Pin geteilt durch Follower-Count, mal 100 - als grober Proxy)

### Schritt 8: Content-Pillars und Themen-Cluster

Pro Akteur aus den Board-Themen + Pin-Token-Heuristik die dominanten Content-Pillars extrahieren:

1. **Board-Themen-Cluster** - Boards mit ähnlichen Tokens im Title und in der Beschreibung gruppieren
2. **Pin-Tags-Cluster** - Top-Tags über alle Pins
3. **Pin-Title-Token-Cluster** - häufige Substantive aus Pin-Titles (Stopwords filtern)

Daraus pro Akteur 3-5 Content-Pillars (z. B. "Wohnen and Interior", "Saisonale Rezepte", "DIY-Anleitungen"). Pro Pillar dokumentieren: Anzahl beitragender Boards, Anzahl beitragender Pins, Beispiel-Pin-Titles.

Branchenweit über alle Akteure zusammenfassen: welche Pillars sind in der Wettbewerbsgruppe dominant? Wo hat der Kunde Lücken?

### Schritt 9: Auffälligkeiten

Mindestens 7 Auffälligkeits-Typen werden geprüft - jede Auffälligkeit nur ausgeben, wenn ihre Bedingung tatsächlich erfüllt ist:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_kein_pinterest_profil` | Kunde hat keinen auflösbaren Username | "Kunde hat kein identifizierbares Pinterest-Profil - in einer Pinterest-affinen Branche ist das eine strategische Lücke" |
| `kunde_inaktiv_seit_X_wochen` | Kunde hat seit X Wochen keinen Pin, X mindestens 8 | "Letzter Pin vor 14 Wochen - Account wirkt verwaist, Vertrauenseinbuße im Pinterest-Algorithmus" |
| `kunde_kein_business_account` | Kunde hat persönliches Profil statt Business-Account | "Business-Konto fehlt - Pinterest-Analytics, Rich Pins und Ads sind ohne Business-Account nicht verfügbar" |
| `kunde_engagement_unter_branchen_median` | Kunden-Engagement-pro-Pin liegt unter dem Median der aktiven Wettbewerber | "Engagement pro Pin liegt 60 Prozent unter dem Wettbewerbs-Median - Content-Qualität oder Pin-Frequenz prüfen" |
| `wettbewerber_idea_pins_strategie` | Mindestens 2 WBs nutzen Idea-Pins mit signifikantem Anteil, Kunde nicht | "Zwei Wettbewerber setzen stark auf Idea-Pins (Story-Format), Kunde nutzt ausschließlich Standard-Pins - Reichweiten-Format wird verpasst" |
| `board_themen_luecke_kunde` | Es gibt ein Content-Pillar, das bei mindestens 2 WBs prominent ist, beim Kunden gar nicht | "Pillar 'Saisonale Inspirationen' bei drei WBs zentral - Kunde hat dazu kein Board" |
| `product_pin_potenzial_ungenutzt` | E-Commerce-Kunde nutzt keine Product-Pins, mindestens 1 WB schon | "Kunde betreibt Onlineshop, nutzt aber keine Product-Pins - Pinterest-zu-Shop-Conversion-Pfad fehlt" |
| `pinterest_branchen_fit_gering` | 0 von N Akteuren sind aktiv und Branchen-Fit-Vorab-Flag war nicht hoch | "Keine Pinterest-Aktivität in der Wettbewerbsgruppe - Pinterest ist für diese Branche vermutlich strategisches Nicht-Thema" |
| `wettbewerber_dominiert_pinterest` | Ein WB hat 3-fache Follower und 3-fache Pin-Frequenz gegenüber dem Branchen-Median | "Wettbewerber AKTEUR dominiert Pinterest in der Branche - lohnt sich als Best-Practice-Vorbild für Content-Strategie" |

Pro Auffälligkeit: Typ, Titel, Beschreibung, Relevanz (hoch / mittel / niedrig), Handlungs-Empfehlung, betroffene Akteure.

**Automatischer Hinweis-Block** wenn 0 Akteure aktiv: "Pinterest-Branchen-Fit gering - strategisches Nicht-Thema empfohlen" wird prominent oben im Output und im HTML-Report angezeigt, unabhängig vom Vorab-Branchen-Flag.

### Schritt 10: CSV-Outputs

**`audits/pinterest-profile.csv`** - eine Zeile pro Akteur:

```
akteurs_slug, akteurs_typ, akteurs_name, pinterest_username, pinterest_url,
match_methode, match_konfidenz, follower_count, following_count, boards_count,
pins_count_gesamt, verifiziert, business_account, account_typ,
pins_im_zeitfenster_12m, pins_pro_woche_median, wochen_seit_letztem_pin,
aktivitaets_status, engagement_pro_pin_median, engagement_rate_proxy,
top_boards (Pipe-getrennt: name:pin_anzahl:follower_anzahl, max 10),
content_pillars (Pipe-getrennt, max 5), datenstand_iso
```

**`audits/pinterest-pins.csv`** - eine Zeile pro Pin × Akteur:

```
akteurs_slug, akteurs_typ, akteurs_name, pin_id, pin_url, pin_title,
pin_beschreibung, pin_typ, created_at, saves_count, comments_count,
domain_link, landingpage_url, board_slug, board_name,
tags (Komma-getrennt), creative_url, datenstand_iso
```

Schema-Details und Validierungs-Regeln stehen in `reference/pinterest-output-schema.md`.

### Schritt 11: Aggregat-Markdown `audits/pinterest-wettbewerb.md`

Frontmatter mit:

- Skill-Metadaten, Quellen-Provenienz (Apify-Actor + Datum + Anzahl Akteure)
- `branchen_fit_pinterest`: `hoch | mittel | niedrig`
- `pinterest_branchen_relevant`: bool (true wenn mindestens 1 Akteur aktiv)
- Profil-Matrix pro Akteur mit allen Profil-Kennzahlen und Boards-Übersicht (kompakt)
- Pin-Typen-Verteilung pro Akteur
- Engagement-Vergleich (Median, Top, Bottom)
- Content-Pillars pro Akteur und branchenweit
- Auffälligkeiten

Body:

- Branchen-Fit-Hinweis-Block oben (immer; bei `niedrig` prominenter)
- Übersicht (Akteure aktiv, Top-Account, Pin-Volumen branchenweit, Engagement-Median)
- Akteurs-Vergleichs-Tabelle (Follower, Boards, Pins-12M, Engagement, Aktivität)
- Pro Akteur ein Sub-Block mit:
  - Profil-Snapshot (Bio, Follower, Boards-Count, Business-Account-Status, Verifizierungs-Status)
  - Top-10-Boards mit Pin-Anzahl und Follower-Anzahl
  - Pin-Typen-Verteilung (Standard / Video / Idea / Product)
  - Top-5-Pins nach Saves
  - Content-Pillars
- Branchen-Content-Pillars-Übersicht (welche Pillars dominieren in der Wettbewerbsgruppe)
- Auffälligkeiten

### Schritt 12: HTML-Report `reports/17-pinterest-wettbewerb.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html`:

- **Stat-Strip oben**: Akteure aktiv, Pin-Volumen 12M, Top-Account, Engagement-Median, Anzahl Content-Pillars, Anzahl Auffälligkeiten
- **Branchen-Fit-Banner** prominent: bei `niedrig` mit deutlichem `.summary-card`-Hinweis "Pinterest-Branchen-Fit gering - strategisches Nicht-Thema empfohlen"
- **Sticky-TOC** zu allen Sektionen
- **Aktivitäts-Heatmap** (Akteur × Pin-Typ)
- **Pro Akteur** ein `details.skill[data-status]`-Block mit:
  - Profil-Snapshot
  - Boards-Karten (Top-10 mit Pin- und Follower-Counts)
  - Pin-Typen-Verteilung als kleine ASCII-Balken
  - Top-5-Pins als Karten mit Saves, Comments, Board, Domain-Link
  - Content-Pillars als Tag-Wolke
- **Branchen-Content-Pillars**: für jeden Pillar eine Karte mit Akteurs-Verteilung
- **Auffälligkeiten** als `.suggestion`-Block
- Footer

### Schritt 13: Outputs nach Drive hochladen, Dashboard-Update, status.md

**Output-Uploads nach Drive** (in dieser Reihenfolge):

1. Aggregat-Markdown + CSVs → `AUDITS_ID`:
   ```bash
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "pinterest-wettbewerb.md" /tmp/pinterest-wettbewerb.md "text/markdown"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "pinterest-profile.csv" /tmp/pinterest-profile.csv "text/csv"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "pinterest-pins.csv" /tmp/pinterest-pins.csv "text/csv"
   ```
2. Roh-JSONs gzip-komprimiert nach Drive `assets/raw/`:
   ```bash
   RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
   for f in ~/.cache/reachx-mta/<slug>/raw/pinterest-*.json; do
     gzip -k "$f"
     python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
   done
   ```
3. HTML-Report `17-pinterest-wettbewerb.html` → `REPORTS_ID`.

**status.md-Update** (siehe `contracts.md` Abschnitt 3):

- `03-10-social-pinterest` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z. B. "4 von 7 Akteuren aktiv, Branchen-Fit mittel")
- Reports-Liste um `17-pinterest-wettbewerb.html`
- Stat-Strip aktualisieren
- `naechster_empfohlen`: nächster passender Social-Skill oder `04-02-kanal-chancen-analyse` falls Social-Triple komplett

### Schritt 14: Standard-Schlussformat im Chat

```
✓ 03-10-social-pinterest abgeschlossen.

Outputs (auf Drive):
- audits/pinterest-wettbewerb.md - Aggregat mit Profil-Matrix, Boards, Pin-Typen, Content-Pillars
- audits/pinterest-profile.csv - Profil-Matrix (N Zeilen)
- audits/pinterest-pins.csv - Pin-Sample (M Zeilen)
- reports/17-pinterest-wettbewerb.html - Strategen-Report
- assets/raw/pinterest-*.json.gz - komprimierte Apify-Roh-JSONs
Status aktualisiert in: status.md

Pinterest-Lage:
- Akteure mit Pinterest-Profil:  M von N
- Aktive Accounts:                A
- Top-Account:                    AKTEUR mit F Followern
- Pin-Volumen 12M:                P Pins gesamt
- Engagement-Median pro Pin:      E
- Content-Pillars branchenweit:   C

[Wenn branchen_fit_pinterest = niedrig oder 0 aktive Akteure:]
ℹ Branchen-Fit-Hinweis
- Pinterest-Branchen-Fit gering - strategisches Nicht-Thema empfohlen.

[Wenn Auffälligkeiten:]
⚠ Pinterest-Insights:
- (1-3 Top-Auffälligkeiten)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestätigt - Pinterest-Lage nur für den Kunden, kein Branchen-Benchmark.

Nächste Schritte:
1. NAECHSTER_SOCIAL_SKILL - parallel möglich oder direkt anschließend
2. (parallel möglich) 04-02-kanal-chancen-analyse - falls genug Audit-Skills durchgelaufen

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/pinterest-tools-mapping.md` - Apify-Actor-Optionen, URL-Patterns, Datenfelder-Mapping, Fallback-Kaskade, Search-Methodik für Username-Auflösung
- `reference/pinterest-output-schema.md` - Vollständiges Schema für `audits/pinterest-wettbewerb.md`, `audits/pinterest-profile.csv`, `audits/pinterest-pins.csv` inkl. Validierungs-Regeln

## Edge Cases

- **Kunde hat keinen Pinterest-Account** → Standard-Fall in B2B-Industrie, Recht, Finanzen. Skill markiert `pinterest_username_unbekannt: true`, listet zur Strategen-Review, läuft trotzdem mit den WBs durch. Auffälligkeit `kunde_kein_pinterest_profil` nur bei `branchen_fit_pinterest: hoch` oder `mittel` ausgeben - bei niedrig ist das Erwartungswert.

- **Wettbewerber ist auf Pinterest unter anderem Namen** → Skill nutzt Username aus Marken-Profil als Quelle der Wahrheit. Wenn Apify-Search mehrere plausible Treffer liefert: nicht raten, sondern als `nicht_gefunden` markieren und Strategen-Review.

- **Sehr großes Profil mit über 200 Boards** → Skill holt alle Boards für die Übersicht, nimmt aber nur Top-10 in die Akteurs-Karte. Restliche Boards in der Profile-CSV nur als Gesamt-Count.

- **Pinterest-Drosselung bei großen Scrapes** → Apify-Actor liefert teils unvollständige Pin-Listen. Skill markiert das mit `scrape_unvollstaendig: true` und nutzt das gegebene Sample. Hard-Cap 40 Pins bleibt erhalten - eher Qualität als Vollständigkeit.

- **Pin-Typ unbekannt aus Actor-Output** → Skill setzt `pin_typ: unbekannt` und zählt diese Pins in der Verteilung separat. Wenn über 30 Prozent unbekannt: Hinweis im Output, dass die Pin-Typen-Verteilung mit Vorbehalt zu lesen ist.

- **Saves-Count fehlt komplett** → einige Apify-Actors liefern Saves nicht zuverlässig. Skill markiert `engagement_proxy_unzuverlaessig: true` und nutzt Comments allein als Proxy. Engagement-Vergleich mit entsprechendem Caveat im Output.

- **Idea-Pins werden nicht erfasst** → wenn der genutzte Apify-Actor Idea-Pins nicht ausgibt, dokumentiert der Skill `idea_pins_erfassbar: false` und gibt keinen Vergleich zur Idea-Pin-Nutzung aus. Auffälligkeit `wettbewerber_idea_pins_strategie` wird in dem Fall unterdrückt.

- **Internationale Akteure** → Pinterest ist global, aber Boards können lokalisiert sein. Skill markiert die Profil-Region wenn verfügbar, filtert aber nicht - Cross-Locale-Inspiration ist auf Pinterest normal.

- **Apify-Actor scheitert vollständig** → Fallback auf manuellen Mini-Workflow: dem Strategen die Pinterest-URLs aller Akteure ausgeben, mit Bitte, manuell zu prüfen. Im Output ein `manueller_check_erforderlich`-Block mit Akteurs-Liste.

- **Branche ist Pinterest-Nische (z. B. Hochzeit, Garten)** → Engagement-Werte können sehr hoch sein im Vergleich zu anderen Social-Plattformen. Im Output Pinterest-spezifisch werten, nicht 1:1 mit Instagram oder LinkedIn vergleichen.

## Branchenrelevanz

Pinterest ist stark in:

- Lifestyle, Home and Garden, Wohnen, Interior
- Mode, Beauty, Hair, Nails
- DIY, Handwerk, Selbermachen
- Wedding, Hochzeit, Events
- Food, Rezepte, Backen, Gastronomie
- Reise, Urlaub, Destinations
- Kinder, Familie, Erziehung
- Fitness, Yoga, Wellness

Pinterest ist schwach in:

- B2B-Industrie, Maschinenbau, Engineering-Dienstleistungen
- Recht, Steuerberatung, Wirtschaftsprüfung
- Finanzen, Banking, Versicherungen (außer Beratungs-B2C-Bereiche)
- Klassisches SaaS, IT-Infrastruktur
- Logistik, Großhandel

In den schwachen Branchen ist auch ein Null-Ergebnis ein wertvolles Audit-Resultat - der Skill dokumentiert das prominent und empfiehlt im Standard-Schlussformat, Pinterest ggf. als strategisches Nicht-Thema einzuordnen.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Profil- und Pin-Daten
- Standard-Schlussformat
- `status.md` und Dashboard werden aktualisiert
- HTML-Report aus `reports/_shell.html` (aus Drive)
- **Roh-Daten** gzip-komprimiert in Drive `assets/raw/pinterest-profile-AKTEURSSLUG.json.gz` und `pinterest-pins-AKTEURSSLUG.json.gz` als Cache (lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/raw/`)
- **Pin-Texte unverändert** lassen - Originaltexte sind Datenbasis, keine Übersetzungen
- **Hard-Cap 40 Pins** pro Akteur strikt einhalten - schützt vor exzessivem Apify-Verbrauch
- **Branchen-Fit-Hinweis prominent** - sowohl im Markdown als auch im HTML-Report; bei `branchen_fit_pinterest: niedrig` oder 0 aktiven Akteuren wird der Hinweis zum Top-Element der Story
- **Coverage-Limitierungen explizit dokumentieren** - der Stratege darf beim Kunden-Gespräch nicht überziehen, wenn der Actor unvollständig geliefert hat
- **Kein automatisches Raten beim Username-Match** - lieber `nicht_gefunden` markieren als falsche Daten ziehen
