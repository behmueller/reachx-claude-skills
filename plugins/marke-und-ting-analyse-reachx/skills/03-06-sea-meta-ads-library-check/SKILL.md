---
name: 03-06-sea-meta-ads-library-check
description: Erhebt für Kunde und Wettbewerber den Status der Meta-Anzeigen-Aktivität via Meta Ad Library (öffentlich, ohne Auth) - aktive Anzeigen auf Facebook, Instagram, Audience Network, Formate (Image/Video/Carousel/Collection), Schalt-Zeiträume, Werbetexte, Plattform-Mix, EU-DSA-Daten bei politischen Anzeigen. Output ist audits/meta-ads.md plus audits/meta-ads-anzeigen.csv plus HTML-Report - identisches Pattern wie 03-05-sea-google-ads-check, damit 04-02-kanal-chancen-analyse plattformweit vergleichen kann. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Meta-Ads, Facebook-Anzeigen, Instagram-Anzeigen oder die Ad Library prüfen will - auch bei Phrasen wie "Meta Ads Check", "Facebook Ads prüfen", "Instagram Ads Wettbewerber", "Ad Library Recherche", "wer schaltet Meta-Anzeigen", "Social Paid Aktivität", "FB-Ads Konkurrenz", "Werbetexte Meta". Setzt 01-01-mta-projekt-init voraus; ohne wettbewerber/liste.md läuft der Skill im Kunden-only-Modus.
---

# Meta-Ads-Library-Check

Fünfter Skill in Stufe 3, zweiter Ads-Skill. Prüft via **Meta Ad Library** (`https://www.facebook.com/ads/library/`, öffentliche, kostenfreie Datenquelle ohne Auth-Bedarf) für Kunde + alle bestätigten Wettbewerber die aktuelle Meta-Ads-Aktivität auf Facebook, Instagram, Messenger und Audience Network.

Pattern-Wiederverwendung: Output-Schema folgt strikt dem Pattern aus `03-05-sea-google-ads-check` (gleiche CSV-Struktur, gleiche Markdown-Struktur, gleiche Auffälligkeits-Familie), nur erweitert um Meta-spezifische Felder. Dadurch ist die spätere Synthese in `04-02-kanal-chancen-analyse` plattformweit einheitlich.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/meta-ads.md` — Aktivitäts-Status pro Akteur, Anzeigen-Cluster nach Thema/Produkt, Plattform-Mix (FB/IG/Messenger/Audience Network), EU-DSA-Hinweise bei politischen Anzeigen
2. **Anzeigen-CSV** `audits/meta-ads-anzeigen.csv` — alle erfassten Anzeigen mit Akteur, Anzeigentyp, Plattform, Schalt-Datum, Werbetexten, Demografie wenn verfügbar
3. **HTML-Report** `reports/10-meta-ads.html` — Aktivitäts-Matrix, Anzeigen-Galerie pro Akteur, Plattform-Heatmap, Themen-Cluster

**Wichtige Begrenzungen der Meta Ad Library:**

- Page-zentrierter Zugriff: Suche läuft über Facebook-Page-IDs oder Page-Namen, nicht über Domain wie bei Google (Page-Match-Problem siehe Edge Cases)
- Targeting-Daten (Demographics, Interests) nur für politische Anzeigen im EU-DSA-Bereich vollständig sichtbar
- Keine Spend-Daten ausser bei politischen Anzeigen (EU-DSA-Pflicht)
- Reach-Schätzungen nur bei politischen Anzeigen
- Snapshot-Charakter: aktuell aktive plus kürzlich gestoppte Anzeigen, keine vollständige Historie

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

- "Meta Ads Check"
- "Facebook Ads prüfen"
- "Instagram Ads Wettbewerber"
- "Ad Library Recherche"
- "Wer schaltet Meta-Anzeigen"
- "Social Paid Aktivität"
- "FB-Ads Konkurrenz"
- "Werbetexte Meta"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`
- Apify-Zugang verfügbar (für Ad-Library-Scraping — der zentrale Apify-Actor wird in `reference/ad-library-mapping.md` dokumentiert)
- Empfohlen: `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` und `wettbewerber/liste.md` mit `status: bestaetigt` — sonst Kunden-only-Modus
- Empfohlen: `audits/google-ads.md` falls schon vorhanden — für Cross-Plattform-Vergleich (Akteur SEA-only, Social-only oder beides?)

## Ablauf

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Inputs aus Drive, Outputs nach Drive — siehe `contracts.md` Abschnitt 4. Helper: `01-01-mta-projekt-init/scripts/drive.py`.

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug-aus-aufruf>")
[ -z "$MTA_JSON" ] || [ "$MTA_JSON" = "null" ] && { echo "✗ MTA nicht im Cache. Bitte 01-01-mta-projekt-init aufrufen."; exit 1; }
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/` für Apify-Roh-JSONs.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Lies `wettbewerber/liste.md` aus Drive (via `drive.py list-children "$WB_ID"` + `drive.py read`). Wenn vorhanden mit `status: bestaetigt` → Modus **Voll**; sonst → Modus **Kunden-only** mit Hinweis.

Prüfe Apify-Zugang (analog zu anderen Apify-nutzenden Skills). Bei fehlendem Zugang: Abbruch mit Hinweis.

### Schritt 2: Akteurs-Liste zusammenstellen und Page-Resolution

**Pro Akteur muss eine Facebook-Page-Referenz gefunden werden** (nicht Domain wie bei Google). Drei Auflösungs-Stufen — alle Inputs via `drive.py read <id>` aus den jeweiligen Sub-Foldern:

1. **Direkt aus Marken-Profil**: Wenn `data/kunde.md` (aus `$DATA_ID`) oder `wettbewerber/AKTEUR-SLUG.md` (aus `$WB_ID`) einen `touchpoint: facebook` mit URL enthält → diese Page-URL nehmen
2. **Aus Briefing**: Wenn `data/briefing.md` (aus `$DATA_ID`) eine Facebook-URL für den Akteur nennt
3. **Auto-Resolution via Search**: Page-Name aus dem Akteurs-Namen ableiten und in der Ad Library suchen (Suchparameter `view_all_page_id` lookup über Search-API oder Apify-Actor)

Pro Akteur dokumentieren:

- `facebook_page_id` (numerische ID, sobald aufgelöst)
- `facebook_page_url` (kanonische URL)
- `page_match_konfidenz`: `hoch | mittel | niedrig | nicht_gefunden`

**Page-Match-Problem (Edge Case):** Manche Kunden (besonders B2B-Mittelstand, Handwerker) haben gar keine Facebook-Page. In diesem Fall:

- `facebook_page_id: null`
- `aktiv_in_ad_library: false`
- Hinweis im Output: "Akteur hat keine identifizierbare Facebook-Page — Meta-Ads-Aktivität nicht prüfbar"
- Auffälligkeit `keine_meta_praesenz` falls Kunde betroffen ist (kann strategische Lücke sein)

### Schritt 3: Existenz-Check Output

Prüfe via `drive.py list-children "$AUDITS_ID"`, ob `meta-ads.md` oder `meta-ads-anzeigen.csv` schon im Audits-Folder liegen. Wenn ja: fragen (überschreiben / Backup-und-neu nach `audits/_backup/` / abbrechen).

### Schritt 4: Ad-Library-Scrape pro Akteur

Pro Akteur mit aufgelöster Page (siehe `reference/ad-library-mapping.md`):

1. **URL aufbauen**: `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&view_all_page_id=PAGE_ID`
2. **Apify-Actor aufrufen** — Standard: `apify/facebook-ads-library-scraper`, Fallback: `apify/puppeteer-scraper` mit Custom-Page-Function
3. **Daten extrahieren pro Anzeige**:
   - `page_id` (Meta-Page-ID des Werbenden)
   - `page_name` (Display-Name der Page)
   - `page_verified` (Meta-Verifizierungsstatus)
   - `anzeige_id` (Ad-Library-ID, beginnt oft mit grosser Nummer)
   - `anzeige_typ`: `image | video | carousel | collection | dpa | unbekannt`
   - `plattformen`: Liste aus `facebook | instagram | messenger | audience_network`
   - `erst_schalt_datum` (ISO-8601)
   - `letzte_anzeige_datum` (falls verfügbar — Meta zeigt das bei gestoppten Anzeigen)
   - `aktive_in_regionen`: Liste der Länder
   - `werbetext_primary` (Haupt-Text der Anzeige, oben über dem Creative)
   - `werbetext_headline` (Headline-Element)
   - `werbetext_beschreibung` (Description, oft Link-Description)
   - `cta_button` (Call-to-Action, z.B. "Mehr erfahren", "Jetzt einkaufen")
   - `creative_url` (URL zum Bild oder Video-Thumbnail)
   - `landingpage_url` (Ziel-URL der Anzeige)
   - `karussell_anzahl_karten` (nur bei Carousel-Anzeigen)
   - `ist_politisch`: bool (wenn ja, EU-DSA-Block ist gefüllt)
   - `dsa_reach_geschaetzt` (nur bei politischen Anzeigen)
   - `dsa_spend_eur_min` (nur bei politischen Anzeigen)
   - `dsa_spend_eur_max` (nur bei politischen Anzeigen)
   - `dsa_demographics` (nur bei politischen Anzeigen — Alter, Geschlecht, Region falls verfügbar)

4. **Roh-Daten ablegen** unter `~/.cache/reachx-mta/<slug>/audits/raw/meta-ads-AKTEUR-SLUG.json` (lokaler Cache, am Ende komprimiert nach Drive `assets/raw/`)

5. **Region-Filter** anwenden: nur Anzeigen, die in `meta.json.region` aktiv sind (Default: Deutschland; bei DACH-Kunden auch AT, CH einbeziehen). Anzeigen ausserhalb der Zielregion in `regional_irrelevante_anzeigen`-Liste separat ablegen.

### Schritt 5: Akteur nicht in der Ad Library

Pro Akteur ohne Treffer (aber mit Page-ID):

- `aktiv_in_ad_library: false`
- Hinweis: "Page existiert, aber aktuell keine aktiven Anzeigen in der Ad Library"

Pro Akteur ohne auflösbare Page:

- `facebook_page_id: null`
- Hinweis: "Keine Facebook-Page gefunden — Meta-Ads-Aktivität nicht prüfbar"

Bei mehr als 50% der WBs ohne aktive Anzeigen (und mit Page): Auffälligkeit `geringe_meta_dichte_branche`. Bei mehr als 50% ohne Page überhaupt: Auffälligkeit `geringe_meta_praesenz_branche` (mögliche Differenzierungs-Chance).

### Schritt 6: Anzeigen-Cluster pro Akteur

Pro Akteur die Anzeigen in Themen-Cluster gruppieren (heuristisch, identisch zur Logik in `03-05-sea-google-ads-check`):

1. **Branded** — Werbetext oder Headline enthält Eigen-Markennamen → `cluster: branded`
2. **Conquest** — Werbetext zielt auf WB-Markennamen → `cluster: conquest_WB-SLUG`
3. **Produkt-/Themen-Cluster** — Heuristik über Werbetext-Token-Set → `cluster: thema_TOKEN`
4. **Generic** — Sammelbecken für unklare Anzeigen

Zusätzlich Meta-spezifisches Cluster-Attribut: **Creative-Format-Mix pro Cluster** (Video vs Image vs Carousel). Hilft, Format-Strategien sichtbar zu machen ("WB X setzt nur auf Video-Carousels").

Pro Cluster Statistik: Anzahl Anzeigen, Plattform-Mix, Creative-Format-Mix, Erst-Schalt-Datum-Range, Beispiel-Werbetext.

### Schritt 7: Plattform-Verteilungs-Analyse

Meta-spezifisch: pro Akteur die Plattform-Verteilung aggregieren (Facebook only, Instagram only, beide, plus Messenger/Audience Network).

Auffälligkeiten-Trigger:

- Akteur schaltet nur auf Instagram → modernerer Markenauftritt, jüngere Zielgruppe
- Akteur schaltet nur auf Facebook → klassischer, älterer Markenauftritt
- Akteur nutzt Audience Network → Performance-Marketing-Fokus

### Schritt 8: EU-DSA-Block für politische Anzeigen

Politische und gesellschaftliche Anzeigen werden im DSA-Bereich der Ad Library mit zusätzlichen Daten ausgewiesen (Reach-Range, Spend-Range, Demographics).

Pro Akteur: wenn `ist_politisch: true` für eine oder mehrere Anzeigen, einen `dsa_anzeigen`-Sub-Block im Frontmatter füllen mit:

- `anzahl_dsa_anzeigen`
- `dsa_spend_eur_min_summe`
- `dsa_spend_eur_max_summe`
- `dsa_reach_summe_geschaetzt`

Bei B2B- und Handwerks-Kunden in der Regel leer. Bei NGOs, Verbänden, Parteien, manchmal auch bei Unternehmen mit gesellschaftlicher Positionierung relevant.

### Schritt 9: Auffälligkeiten

Aus den erhobenen Daten:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_inaktiv_wb_aktiv` | Kunde hat 0 aktive Anzeigen, mindestens 2 WBs sind aktiv | "Kunde schaltet keine Meta-Ads, beta-solutions hat 23 aktive Anzeigen — Social-Paid-Chance entgeht" |
| `kunde_aktiv_wb_inaktiv` | Kunde hat Anzeigen, alle WBs inaktiv | "Kunde dominiert Meta-Paid in der Wettbewerbsgruppe — Position halten, ggf. SOV erhöhen" |
| `conquest_aktivitaet` | Mindestens 1 WB nutzt Kunden-Markennamen im Werbetext | "Wettbewerber alpha-tech bewirbt aktiv den Markennamen des Kunden auf Meta — Brand-Defense prüfen" |
| `kunde_macht_conquest` | Kunde bewirbt WB-Markennamen | "Kunde betreibt Conquest gegen beta-solutions — strategisch beabsichtigt?" |
| `keine_meta_praesenz` | Kunde hat keine identifizierbare Facebook-Page | "Kunde hat keine Facebook-Page — fundamentale Meta-Lücke, Aufbau-Prio prüfen" |
| `geringe_meta_dichte_branche` | mehr als 50% WBs mit Page haben keine aktiven Anzeigen | "Geringe Social-Paid-Dichte in der Branche — möglicher First-Mover-Vorteil" |
| `geringe_meta_praesenz_branche` | mehr als 50% WBs haben gar keine Facebook-Page | "Branche ist auf Meta unterversorgt — strategisches Whitespace" |
| `hohe_meta_dichte_branche` | alle WBs aktiv mit mehr als 10 Anzeigen | "Hohe Social-Paid-Konkurrenz — Spends werden teuer, Creative-Qualität wird entscheidend" |
| `format_einseitigkeit_branche` | mehr als 70% der WB-Anzeigen sind Single-Image | "Wettbewerber-Anzeigen sind 78% Single-Image — Video- oder Carousel-Differenzierung möglich" |
| `plattform_einseitigkeit_kunde` | Kunde schaltet nur auf einer Plattform, WBs auf mehreren | "Kunde nur auf Facebook aktiv, WBs nutzen auch Instagram — Multi-Plattform-Setup prüfen" |
| `instagram_dominanz` | mehr als 70% der WB-Anzeigen laufen Instagram-first | "Branche ist Instagram-getrieben — visuelle Markeninszenierung priorisieren" |
| `dsa_aktivitaet` | mindestens 1 Akteur hat politische Anzeigen mit DSA-Daten | "Wettbewerber X schaltet als politische Anzeigen klassifizierte Spots — relevant fuer Positionierungs-Story" |

Pro Auffälligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure.

### Schritt 10: CSV-Output `audits/meta-ads-anzeigen.csv`

Eine Zeile pro Anzeige x Akteur. Schema in `reference/ad-library-mapping.md` Abschnitt "Anzeigen-CSV-Mapping".

Spalten (Meta-Erweiterung des Google-Ads-Patterns):

```
akteurs_slug,akteurs_typ,akteurs_name,page_id,page_name,page_verified,
anzeige_id,anzeige_typ,plattformen,erst_schalt_datum,letzte_anzeige_datum,
aktive_in_regionen,in_zielregion,
werbetext_primary,werbetext_headline,werbetext_beschreibung,cta_button,
landingpage_url,landingpage_tiefe,creative_url,karussell_anzahl_karten,
ist_politisch,dsa_reach_geschaetzt,dsa_spend_eur_min,dsa_spend_eur_max,
cluster,datenstand_iso
```

### Schritt 11: Aggregat-Markdown `audits/meta-ads.md`

Frontmatter mit:

- Skill-Metadaten, Quellen-Provenienz (Apify-Actor + Datum + Anzahl Akteure)
- Aktivitäts-Matrix pro Akteur:
  - `facebook_page_id`, `facebook_page_url`, `page_match_konfidenz`
  - `aktiv_in_ad_library: true | false`
  - `anzahl_aktive_anzeigen`, `anzahl_in_zielregion`
  - `anzeigentypen_verteilung` (image/video/carousel/collection/dpa)
  - `plattform_verteilung` (facebook/instagram/messenger/audience_network — Anzeigen koennen auf mehreren laufen)
  - `aelteste_schalt_datum`, `juengste_schalt_datum`
  - `cluster_anzahl`, `cluster_top_3`
  - `dsa_block` (siehe Schritt 8) wenn relevant
- Branchenweite Aggregat-Statistik (Meta-Dichte, Plattform-Mix der Branche, Format-Mix der Branche)
- Auffälligkeiten

Body:

- Übersicht (Anzahl aktive Akteure, Top-Werber, Branchen-Meta-Dichte, Plattform-Schwerpunkt)
- Akteurs-Vergleichs-Tabelle
- Pro Akteur ein Sub-Block mit Aktivitätsstatus, Plattform-Mix, Creative-Format-Verteilung, Top-Anzeigen mit Werbetext-Auszug (max 5), Themen-Clustern
- Themen-Cluster-Übersicht über alle WBs
- Plattform-Heatmap (Akteur x Plattform)
- DSA-Sektion falls relevant
- Auffälligkeiten

### Schritt 12: HTML-Report `reports/10-meta-ads.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html`:

- **Stat-Strip oben**: Akteure aktiv in Ad Library, Anzahl Anzeigen gesamt, Top-Werber, Plattform-Schwerpunkt, Anzahl Themen-Cluster, Anzahl Auffälligkeiten
- **Sticky-TOC**
- **Aktivitäts-Heatmap** (Akteur x Plattform — Meta-spezifische Erweiterung gegenüber Google)
- **Format-Mix-Diagramm** (Image/Video/Carousel/Collection pro Akteur)
- **Pro Akteur** ein `details class="dim"`-Block mit:
  - Page-Info und Match-Konfidenz
  - Aktivitätsstatus + Volumen
  - Plattform-Verteilung (kleine Balken)
  - Top-5-Anzeigen-Karten mit Creative-Thumbnail (falls verfügbar) und Werbetext-Auszug
  - Politische-Anzeigen-Block (DSA) falls relevant
- **Themen-Cluster-Übersicht** als Karten
- **Auffälligkeiten** als `.suggestion`-Block
- Footer

### Schritt 12b: Outputs nach Drive hochladen

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "meta-ads.md" \
  ~/.cache/reachx-mta/<slug>/meta-ads.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "meta-ads-anzeigen.csv" \
  ~/.cache/reachx-mta/<slug>/meta-ads-anzeigen.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "10-meta-ads.html" \
  ~/.cache/reachx-mta/<slug>/10-meta-ads.html "text/html"
```

### Schritt 13: Dashboard-Update und status.md

Standard-Pattern: `reports/index.html` und `status.md` aus Drive lesen, anpassen, zurückschreiben — siehe `contracts.md` Abschnitt 3 und 7.

- `03-06-sea-meta-ads-library-check` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z.B. "3 von 9 Akteuren haben keine Facebook-Page")
- Reports-Liste um `10-meta-ads.html`
- Stat-Strip aktualisieren
- `naechster_empfohlen`: `03-07-sea-linkedin-ads-library-check` (gleiche Mechanik, dritter und letzter Ads-Skill)

### Schritt 14: Standard-Schlussformat im Chat

```
✓ 03-06-sea-meta-ads-library-check abgeschlossen.

Outputs:
- audits/meta-ads.md — Aggregat mit Aktivitäts-Matrix, Plattform-Mix und Themen-Clustern
- audits/meta-ads-anzeigen.csv — Roh-Anzeigen (N Zeilen)
- reports/10-meta-ads.html — Strategen-Report
Status aktualisiert in: status.md

Meta-Paid-Lage:
- Akteure mit Page:            M von N
- Akteure aktiv in Ad Library: A von M
- Anzeigen in Zielregion:      X
- Top-Werber:                  AKTEUR mit N Anzeigen
- Plattform-Schwerpunkt:       facebook | instagram | beide
- Format-Schwerpunkt:          image | video | carousel | mixed
- Themen-Cluster:              T
- DSA-Anzeigen (politisch):    P (falls relevant)

[Wenn Auffälligkeiten:]
⚠ Meta-Insights:
- (1-3 Top-Auffälligkeiten)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestätigt — Meta-Paid-Lage nur für den Kunden, kein Branchen-Benchmark.

[Wenn Kunde keine Page:]
⚠ Kunde hat keine Facebook-Page
- Meta-Ads-Aktivität nicht prüfbar — strategische Lücke, Aufbau-Prio im 90-Tage-Plan diskutieren.

Nächste Schritte:
1. 03-07-sea-linkedin-ads-library-check — LinkedIn Ad Library, gleiche Apify-Mechanik
2. (parallel möglich) 03-14-web-tech-und-tracking — Tech-Stack + Tracking
3. (parallel möglich) 03-15-web-content-inventur — Sitemap und Inhalts-Inventur

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/ad-library-mapping.md` — Apify-Actor-Optionen, URL-Patterns, Page-Resolution-Heuristik, Datenfelder-Mapping
- `reference/meta-ads-besonderheiten.md` — Meta-spezifische Eigenheiten gegenüber Google: Page-Konzept, EU-DSA-Pflichten, Multi-Plattform-Logik, politische-Anzeigen-Sonderbehandlung

Das Output-Schema selbst ist in `03-05-sea-google-ads-check/reference/ads-output-schema.md` definiert — Meta-Erweiterungen werden in `reference/ad-library-mapping.md` als Delta dokumentiert, um Duplizierung zu vermeiden.

## Edge Cases

- **Kunde hat keine Facebook-Page**: Auffälligkeit `keine_meta_praesenz` setzen, im Schluss-Format Hinweis hervorheben. Akteurs-Eintrag mit `facebook_page_id: null` und `aktiv_in_ad_library: false`. Wettbewerber ohne Page werden gleich behandelt, aber ohne Sonderhinweis im Schluss-Format.

- **Page-Disambiguation (mehrere Pages mit ähnlichem Namen)**: Wenn die Such-Auflösung mehrere Kandidaten liefert, das mit der höchsten Follower-Zahl plus passender Sprache als Treffer nehmen. `page_match_konfidenz: mittel` setzen, im Output unter "Lücken und Hinweise" die anderen Kandidaten listen, damit Stratege bei Bedarf override geben kann.

- **Sehr viele aktive Anzeigen (mehr als 200 pro Page)**: Hard-Cap bei Top-100 nach Erst-Schalt-Datum absteigend (jüngste zuerst). Im Body Hinweis "Akteur hat mehr als 200 aktive Anzeigen, Top-100 ausgewertet."

- **Politische Anzeigen mit DSA-Datenfülle**: Werden separat im `dsa_block` aggregiert, kommen aber als normale Zeilen in die CSV. Reach- und Spend-Bandbreiten kommen direkt aus der Ad Library.

- **Instagram-only-Anzeigen**: kein Sonderfall — werden mit `plattformen: ["instagram"]` markiert. Im Plattform-Verteilungs-Block sichtbar.

- **Carousel- oder Collection-Anzeigen mit vielen Karten**: nur die Haupt-Werbetexte werden erfasst, nicht jede Karte einzeln. `karussell_anzahl_karten` dokumentiert das Format. Creative-URL zeigt die erste Karte.

- **Dynamic Product Ads (DPA) oder Catalog-Ads**: werden als `anzeige_typ: dpa` markiert. Werbetexte sind generisch (Platzhalter-Tokens), Landing-URLs zeigen aufs Katalog-Setup. In Cluster-Analyse oft als `generic` oder `branded` einsortiert.

- **Region nicht in Zielregion**: Anzeigen bleiben in CSV mit `in_zielregion: false`. Im Aggregat als `internationale_aktivitaet` separat ausgewiesen (kann strategisches Insight sein, wenn WB internationale Märkte angeht).

- **Apify-Actor scheitert (Ad-Library-UI-Änderung)**: Fallback auf manuellen Mini-Workflow — dem Strategen die Ad-Library-URLs aller Akteure ausgeben, mit Bitte um manuellen Check. Im Output `manueller_check_erforderlich`-Block mit URL-Liste.

- **Creative-Caching (Bilder, Videos)**: Pro Anzeige die `creative_url` in die CSV, kein Download per Default (Speicherplatz). Bei Override `download_creatives: true` Bilder nach `audits/assets/meta-ads/AKTEUR-SLUG/` herunterladen.

- **Page existiert, aber Werbe-Account ist privat oder deaktiviert**: in der Ad Library sichtbar als "Diese Seite hat aktuell keine Anzeigen". `aktiv_in_ad_library: false`, normaler Akteur-Eintrag.

- **Mehrere Pages eines Konzerns (Marken-, Shop-, Service-Page)**: Standard-Page wird aus dem Marken-Profil genommen. Wenn Stratege Multi-Page-Auswertung wünscht: Override `weitere_pages: [PAGE-URL-1, PAGE-URL-2]`. Im Output beide aggregiert.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/meta-ads.md`)
- Markdown plus YAML-Frontmatter für Aggregat, CSV für Roh-Anzeigen (via `drive.py upsert-text`)
- Standard-Schlussformat
- `status.md` und Dashboard werden aktualisiert (`drive.py upsert-text`)
- HTML-Report aus `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **Ad-Library-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/meta-ads-AKTEUR-SLUG.json`, am Ende komprimiert nach Drive `assets/raw/`
- **Werbetexte unverändert** lassen — Originaltexte sind die Datenbasis
- **DSA-Spend-Daten sind Ranges**, niemals Punktschätzungen (siehe Architektur-Entscheidung 10 in `contracts.md`)
- **Page-Match-Konfidenz transparent** machen — Stratege muss sehen, wie sicher die Akteurs-Identifikation ist
