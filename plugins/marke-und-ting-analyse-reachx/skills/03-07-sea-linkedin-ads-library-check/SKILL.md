---
name: 03-07-sea-linkedin-ads-library-check
description: Erhebt für Kunde und alle bestätigten Wettbewerber den aktuellen Status der LinkedIn-Ads-Aktivität via LinkedIn Ad Library (öffentliche Datenquelle, teilweise hinter Login-Wall) - aktive Anzeigen, Anzeigentypen (Sponsored Content, Sponsored Messaging, Text Ads, Dynamic Ads), Schalt-Zeiträume, Werbetexte, ggf. Job-Title- und Industry-Targeting. Output ist audits/linkedin-ads.md (pro Akteur Aktivitäts-Status + Themen-Cluster + Targeting-Hinweise) plus audits/linkedin-ads-anzeigen.csv (Roh-Anzeigen) plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext LinkedIn-Ads-Aktivität prüfen will - auch bei Phrasen wie "LinkedIn Ads Check", "wer schaltet LinkedIn-Ads", "aktive LinkedIn-Anzeigen", "LinkedIn Ad Library prüfen", "B2B Ads Aktivität", "LinkedIn-Werbung der Wettbewerber", "Sponsored Content Wettbewerb". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist; ohne wettbewerber/liste.md läuft der Skill im Kunden-only-Modus. B2C-Branchen oft mit geringer Coverage.
---

# LinkedIn-Ads-Library-Check

Sechster Skill in Stufe 3, dritter Ads-Skill nach `03-05-sea-google-ads-check` und `03-06-sea-meta-ads-library-check`. Prüft via **LinkedIn Ad Library** (https://www.linkedin.com/ad-library/) für Kunde + alle bestätigten Wettbewerber die aktuelle LinkedIn-Ads-Aktivität.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/linkedin-ads.md` — Aktivitäts-Status pro Akteur, Anzeigen-Cluster nach Thema/Produkt, Targeting-Hinweise wenn sichtbar (Job Titles, Industries)
2. **Anzeigen-CSV** `audits/linkedin-ads-anzeigen.csv` — alle erfassten Anzeigen mit Akteur, Anzeigentyp, Schalt-Datum, Werbetexten, Targeting-Hinweisen
3. **HTML-Report** `reports/11-linkedin-ads.html` — Aktivitäts-Matrix, Anzeigen-Galerie pro Akteur, Themen-Cluster, B2B-Eignungs-Hinweis

**Wichtige Begrenzung:** Die LinkedIn Ad Library zeigt **aktive plus kürzlich pausierte Anzeigen** der letzten 12 Monate. **Login-Wall**: manche Anzeigen sind ohne LinkedIn-Login nicht oder nur eingeschränkt sichtbar — Coverage ist deshalb variabel und im Output dokumentiert. **B2C-Branchen**: LinkedIn ist B2B-fokussiert, in reinen B2C-Branchen ist die Aktivität oft gering — kann strategisches Nicht-Thema sein.

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

- "LinkedIn Ads Check"
- "Wer schaltet LinkedIn-Ads"
- "Aktive LinkedIn-Anzeigen"
- "LinkedIn Ad Library prüfen"
- "B2B Ads Aktivität"
- "LinkedIn-Werbung der Wettbewerber"
- "Sponsored Content Wettbewerb"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`
- **Apify-Zugang (Pflicht)** — der zentrale Apify-Actor wird in `reference/linkedin-ad-library-mapping.md` dokumentiert (mit `zuletzt_getestet`-Datum und `status`). Credential-Prüfung: ausschließlich `[ -n "$APIFY_TOKEN" ]` — kein Scannen von `~/.zshrc` o. ä. (contracts.md Abschnitt 11). Vor dem ersten echten Scrape Apify-Health-Check via `mcp__apify__fetch-actor-details` für den verwendeten Actor: bei `Session ID not found` sofort abbrechen und Reconnect-Hinweis ausgeben, statt alle Akteure einzeln scheitern zu lassen.
- **Login-Wall-Hinweis:** Die LinkedIn Ad Library ist öffentlich zugänglich, liefert aber ohne Login einen reduzierten Datensatz. Targeting-Details (Job-Title, Industry) sind oft nur eingeloggt vollständig sichtbar — diese Felder als `null` markieren und im Output Coverage-Lücke dokumentieren. Organische LinkedIn-Posts (Company-Feed) sind hingegen hinter Login und **nicht erhebbar ohne authentifizierten Scraper**.
- Empfohlen: `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` und `wettbewerber/liste.md` mit `status: bestaetigt` — sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` und `wettbewerber/*.md` mit `touchpoints`-Inventur — daraus kommen die LinkedIn-Company-Page-URLs der Akteure (wichtig, weil der Match in der LinkedIn Ad Library über die Company Page erfolgt, nicht über die Domain)

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

**B2C-Vorab-Check**: Wenn `meta.json.branche` oder `data/kunde.md` (aus `$DATA_ID`) auf eine reine B2C-Branche hinweist (z. B. lokales Handwerk, Gastronomie, Mode-Einzelhandel, Beauty, Fitness-Studio), setze internen Flag `b2c_kontext: true` und gebe später im Output einen B2C-Hinweis-Block aus. Skill läuft trotzdem durch — Ergebnis ist wertvoll, auch wenn es zeigt "in dieser Branche spielt LinkedIn Ads keine Rolle".

### Schritt 2: Akteurs-Liste mit Company-Page-Match zusammenstellen

LinkedIn-spezifische Logik: der Match in der LinkedIn Ad Library erfolgt nicht über die Domain, sondern über die **LinkedIn Company Page**. Pro Akteur muss die Company-Page-URL identifiziert werden.

Reihenfolge der Quellen pro Akteur — alle Inputs via `drive.py read <id>` aus den jeweiligen Sub-Foldern:

1. **Aus Marken-Profil**: in `data/kunde.md` (aus `$DATA_ID`) bzw. `wettbewerber/AKTEURSSLUG.md` (aus `$WB_ID`) unter `touchpoints` nach `typ: linkedin` suchen — URL hat Form `https://www.linkedin.com/company/COMPANYSLUG/`
2. **Aus Briefing**: in `data/briefing.md` (aus `$DATA_ID`) nach erwähnten LinkedIn-Profilen
3. **Direkter Lookup**: wenn nichts gefunden, Web-Search nach `"COMPANYNAME" site:linkedin.com/company`
4. **Manuell-Fallback**: wenn auch das nicht eindeutig ist, Akteur als `linkedin_company_page_unbekannt: true` markieren und im Output zur Strategen-Review aufführen

Akteure mit gefundener Company-Page (Akteurs-Slug + Typ kunde/wettbewerber + LinkedIn-Slug):

1. **Kunde** — Company-Page-Slug
2. **Wettbewerber** — pro Eintrag aus `liste.md` mit gefundener Company-Page. Wie bei `03-05-sea-google-ads-check`: **keine Filterung auf `empfehlung_profilieren: ja`** — LinkedIn-Ad-Library-Lookup ist günstig genug für alle WBs.

### Schritt 3: Existenz-Check Output

Prüfe via `drive.py list-children "$AUDITS_ID"`, ob `linkedin-ads.md` oder `linkedin-ads-anzeigen.csv` schon im Audits-Folder liegen. Wenn ja: fragen (überschreiben / Backup-und-neu nach `audits/_backup/` / abbrechen).

### Schritt 4: Ad-Library-Scrape pro Akteur

Pro Akteur (siehe `reference/linkedin-ad-library-mapping.md`):

1. **URL aufbauen**: `https://www.linkedin.com/ad-library/search?companyIds=COMPANYID` oder `https://www.linkedin.com/ad-library/search?accountOwner=COMPANYSLUG` (siehe Mapping-Reference für aktuelle URL-Struktur)
2. **Apify-Actor aufrufen** — Standard: `apify/linkedin-ad-library-scraper` (falls vorhanden), Fallback: `apify/puppeteer-scraper` mit Custom-Page-Function und Login-Wall-Workaround
3. **Daten extrahieren pro Anzeige**:
   - `werbender_name` (LinkedIn Company Page Name — sollte mit Akteur matchen)
   - `werbender_company_id` (LinkedIn-interne ID)
   - `anzeige_id` (Library-eigene Ad-ID, sonst Hash)
   - `anzeige_typ`: `sponsored_content | sponsored_messaging | text_ads | dynamic_ads | video_ads | document_ads | event_ads | unbekannt`
   - `format`: `single_image | video | carousel | document | event | text | unbekannt`
   - `erst_schalt_datum` (ISO-8601)
   - `letzte_anzeige_datum` (falls verfügbar)
   - `aktive_in_regionen`: Liste der Länder (LinkedIn liefert Country-Level)
   - `werbetext_intro` (Sponsored-Content-Intro-Text)
   - `werbetext_headline` (Headline / CTA-Block)
   - `werbetext_beschreibung` (Body-Text)
   - `creative_url` (für Image/Video/Carousel — URL zum Asset)
   - `landingpage_url` (Ziel-URL inkl. UTM)
   - `cta_text` (z. B. "Mehr erfahren", "Demo buchen", "Registrieren")
   - `job_title_targeting` (wenn sichtbar — LinkedIn zeigt teilweise grobes Targeting öffentlich, vor allem in der EU wegen DSA)
   - `industry_targeting` (wenn sichtbar)
   - `geography_targeting` (wenn sichtbar)

4. **Roh-Daten ablegen** unter `~/.cache/reachx-mta/<slug>/audits/raw/linkedin-ads-AKTEURSSLUG.json` (lokaler Cache, am Ende komprimiert nach Drive `assets/raw/`)

5. **Region-Filter** anwenden: nur Anzeigen, die in `meta.json.region` aktiv sind (Default: Deutschland; bei DACH-Kunden auch AT, CH einbeziehen). Anzeigen außerhalb der Zielregion in `regional_irrelevante_anzeigen`-Liste separat ablegen.

### Schritt 5: Akteur nicht in der Ad Library oder Login-Wall-Effekt

LinkedIn zeigt nur Anzeigen, die die Plattform öffentlich gelistet hat. Ohne Login ist die Sichtbarkeit teilweise eingeschränkt — manche Detail-Felder (Targeting) sind erst nach Login sichtbar. Wenn ein Akteur ohne Treffer durchläuft, gibt es drei Möglichkeiten:

- **Keine LinkedIn-Ads-Aktivität**: der Akteur schaltet keine Ads (häufig bei B2C-Branchen)
- **Login-Wall-Effekt**: Anzeigen sind vorhanden, aber nur mit Login sichtbar — Skill kann sie nicht sehen
- **Company-Page-Match-Problem**: der Akteur ist auf LinkedIn aktiv, aber unter anderem Company-Page-Namen registriert

Pro Akteur ohne Treffer:

- `aktiv_in_ad_library: false`
- `match_methode: company_page_slug | company_id | suche_name | nicht_gefunden`
- Hinweis im Output, dass das mehrere Gründe haben kann

Bei mehr als 50% der WBs ohne Treffer **und** `b2c_kontext: true`: Auffälligkeit `linkedin_ads_kein_branchen_thema` mit Hinweis, dass LinkedIn-Ads in dieser Branche möglicherweise irrelevant ist (strategisches Nicht-Thema).

Bei mehr als 50% der WBs ohne Treffer **und** `b2c_kontext: false`: Auffälligkeit `linkedin_login_wall_coverage_luecke` mit Hinweis, dass die LinkedIn-Coverage ohne Login limitiert ist und der Stratege ggf. mit eingeloggter LinkedIn-Session prüfen sollte.

### Schritt 6: Anzeigen-Cluster pro Akteur

Pro Akteur die Anzeigen in Themen-Cluster gruppieren (heuristisch, identisch zu `03-05-sea-google-ads-check`):

1. **Branded** — Werbetext enthält Eigen-Markennamen → `cluster: branded`
2. **Conquest** — Werbetext oder Landingpage zielt auf WB-Markennamen → `cluster: conquest_WBSLUG`
3. **Recruiting** — LinkedIn-spezifisch: viele Anzeigen sind Personalmarketing. Werbetext-Token wie "Karriere", "Stelle", "Job", "Wir suchen", "Recruiting" → `cluster: recruiting`
4. **Lead-Gen** — Werbetexte mit Whitepaper, Webinar, Demo, Testversion, Trial → `cluster: lead_gen`
5. **Event** — Konferenz, Webinar, Messe-Auftritt → `cluster: event`
6. **Thought-Leadership** — Content-Promotion, Studien, Blogposts → `cluster: thought_leadership`
7. **Produkt-/Themen-Cluster** — Heuristik über Werbetext-Token: gruppiere Anzeigen mit ähnlichem Token-Set → `cluster: thema_TOKEN`
8. **Generic** — Sammelbecken für unklare Anzeigen

Pro Cluster Statistik: Anzahl Anzeigen, Anzeigentypen-Mix, Erst-Schalt-Datum-Range, Beispiel-Werbetext.

### Schritt 7: Targeting-Aggregation

LinkedIn ist eine der wenigen Plattformen, die teilweise Targeting-Daten öffentlich zeigt (vor allem in der EU wegen DSA). Wo verfügbar, aggregiere pro Akteur:

- `job_title_targeting_top`: Top-5 beworbene Job-Titles über alle Anzeigen des Akteurs
- `industry_targeting_top`: Top-5 beworbene Industries
- `geography_targeting_top`: Top-5 Regionen

Wenn keine Targeting-Daten verfügbar (häufig wenn nicht eingeloggt): `targeting_verfuegbar: false`.

Pool-weit aggregieren: welche Job-Titles werden branchenweit beworben? Hilft dem Strategen zu verstehen, welche Decision-Maker-Typen die WBs ansprechen.

### Schritt 8: Auffälligkeiten

Aus den erhobenen Daten:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_inaktiv_wb_aktiv` | Kunde hat 0 aktive Anzeigen, mindestens 2 WBs sind aktiv | "Kunde schaltet keine LinkedIn Ads, beta-solutions hat 8 aktive Sponsored-Content-Anzeigen — Decision-Maker-Reach entgeht" |
| `kunde_aktiv_wb_inaktiv` | Kunde hat Anzeigen, alle WBs sind inaktiv | "Kunde dominiert LinkedIn-Ads in der Wettbewerbsgruppe — Position halten" |
| `conquest_aktivitaet` | Mindestens 1 WB bewirbt Kunden-Markennamen | "Wettbewerber alpha-tech bewirbt aktiv den Markennamen des Kunden auf LinkedIn — Conquest-Brand-Protection prüfen" |
| `kunde_macht_conquest` | Kunde bewirbt WB-Markennamen | "Kunde betreibt Conquest-Marketing gegen beta-solutions — strategisch beabsichtigt?" |
| `linkedin_ads_kein_branchen_thema` | B2C + >50% WBs ohne Treffer | "Geringe LinkedIn-Ads-Dichte in B2C-Branche — möglicherweise kein strategisches Thema für den Kunden" |
| `linkedin_login_wall_coverage_luecke` | B2B + >50% WBs ohne Treffer | "Coverage-Lücke wegen Login-Wall — manueller Check mit eingeloggter Session empfohlen" |
| `recruiting_dominiert` | >60% der WB-Anzeigen sind Recruiting-Cluster | "Wettbewerber nutzen LinkedIn primär für Recruiting, nicht für Demand-Gen — Differenzierungs-Chance mit Lead-Gen-Kampagnen" |
| `thought_leadership_konkurrenz` | Mindestens 3 WBs aktiv im Thought-Leadership-Cluster | "Branche stark auf Thought-Leadership-Promotion — Content-Tiefe wird in der Story wichtig" |
| `decision_maker_targeting_dominant` | Wenn Targeting-Daten verfügbar und Top-Job-Title bei >5 WBs identisch | "WBs zielen identische Decision-Maker-Rollen an (z. B. CTO, Head of IT) — Targeting-Differenzierung oder Tonalitäts-Differenzierung empfehlen" |

Pro Auffälligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure.

### Schritt 9: CSV-Output `audits/linkedin-ads-anzeigen.csv`

Eine Zeile pro Anzeige × Akteur. Schema in `reference/linkedin-ad-library-mapping.md` Abschnitt "Anzeigen-CSV".

Spalten (analog `03-05-sea-google-ads-check` mit LinkedIn-Erweiterungen):

```
akteurs_slug, akteurs_typ, akteurs_name, werbender_name, werbender_company_id,
anzeige_id, anzeige_typ, format, erst_schalt_datum, letzte_anzeige_datum,
aktive_in_regionen, in_zielregion,
werbetext_intro, werbetext_headline, werbetext_beschreibung, cta_text,
landingpage_url, landingpage_tiefe, creative_url,
job_title_targeting, industry_targeting, geography_targeting,
cluster, datenstand_iso
```

### Schritt 10: Aggregat-Markdown `audits/linkedin-ads.md`

Frontmatter mit:

- Skill-Metadaten, Quellen-Provenienz (Apify-Actor + Datum + Anzahl Akteure)
- `b2c_kontext: true | false` — wenn true, zusätzlicher Hinweis-Block im Body
- Aktivitäts-Matrix pro Akteur:
  - `aktiv_in_ad_library: true | false`
  - `linkedin_company_page_url`
  - `linkedin_company_id`
  - `match_methode`
  - `anzahl_aktive_anzeigen`
  - `anzahl_in_zielregion`
  - `anzeigentypen_verteilung` (sponsored_content/sponsored_messaging/text_ads/dynamic_ads/video_ads/document_ads/event_ads)
  - `aelteste_schalt_datum`
  - `juengste_schalt_datum`
  - `cluster_anzahl`
  - `targeting_verfuegbar: true | false`
  - `job_title_targeting_top`, `industry_targeting_top`, `geography_targeting_top` (wenn verfügbar)
- Branchenweite Aggregat-Statistik
- Auffälligkeiten

Body:

- B2C-Hinweis-Block oben (wenn `b2c_kontext: true`): "LinkedIn-Ads-Aktivität in B2C-Branchen oft gering — kann strategisches Nicht-Thema sein. Trotzdem hier dokumentiert, um die Annahme datenbasiert zu untermauern."
- Coverage-Hinweis (Login-Wall): "LinkedIn Ad Library liefert ohne Login eingeschränkte Sichtbarkeit. Skill-Coverage variabel — bei kritischen Akteuren manueller Stratege-Check empfohlen."
- Übersicht (Anzahl aktive Akteure, Top-Werber, Branchen-LinkedIn-Ads-Dichte)
- Akteurs-Vergleichs-Tabelle
- Pro Akteur ein Sub-Block mit:
  - Aktivitätsstatus + Company-Page-Link
  - Anzeigentypen-Verteilung
  - Top-Anzeigen (mit Werbetext-Auszug, max 5)
  - Themen-Cluster im Akteurs-Portfolio
  - Targeting-Profil (wenn verfügbar)
- Themen-Cluster-Übersicht über alle WBs
- Targeting-Aggregat über alle WBs (Top-Job-Titles, Top-Industries der Branche)
- Auffälligkeiten

### Schritt 11: HTML-Report `reports/11-linkedin-ads.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html`:

- **Stat-Strip oben**: Akteure aktiv in Ad Library, Anzahl Anzeigen gesamt, Top-Werber, Anzahl Themen-Cluster, Anzahl Auffälligkeiten
- **B2C-Hinweis-Banner** (wenn `b2c_kontext: true`) als `.summary-card`
- **Coverage-Hinweis-Banner** zur Login-Wall als kleiner Info-Block
- **Sticky-TOC** zu allen Sektionen
- **Aktivitäts-Heatmap** (Akteur × Anzeigentyp)
- **Pro Akteur** ein `details.skill`-Block mit:
  - Aktivitätsstatus + Volumen + Company-Page-Link
  - Anzeigentypen-Verteilung (kleine ASCII-Balken)
  - Top-5-Anzeigen-Karten mit Werbetext-Auszug und Landingpage-Link
  - Targeting-Profil (wenn verfügbar)
- **Themen-Cluster-Übersicht**: für jeden Cluster eine Karte mit Akteurs-Verteilung
- **Targeting-Aggregat**: Top-Job-Titles und Top-Industries als Tag-Wolke
- **Auffälligkeiten** als `.suggestion`-Block
- Footer

### Schritt 11b: Outputs nach Drive hochladen

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "linkedin-ads.md" \
  ~/.cache/reachx-mta/<slug>/linkedin-ads.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "linkedin-ads-anzeigen.csv" \
  ~/.cache/reachx-mta/<slug>/linkedin-ads-anzeigen.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "11-linkedin-ads.html" \
  ~/.cache/reachx-mta/<slug>/11-linkedin-ads.html "text/html"
```

### Schritt 12: Dashboard-Update und status.md

Standard-Pattern: `reports/index.html` und `status.md` aus Drive lesen, anpassen, zurückschreiben — siehe `contracts.md` Abschnitt 3 und 7.

- `03-07-sea-linkedin-ads-library-check` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z. B. "6 von 9 Akteuren aktiv, B2C-Hinweis aktiv")
- Reports-Liste um `11-linkedin-ads.html`
- Stat-Strip aktualisieren
- `naechster_empfohlen`: `03-14-web-tech-und-tracking` (nächster Audit-Skill in der natürlichen Reihenfolge — Ads-Triple abgeschlossen)

### Schritt 13: Standard-Schlussformat im Chat

```
✓ 03-07-sea-linkedin-ads-library-check abgeschlossen.

Outputs:
- audits/linkedin-ads.md — Aggregat mit Aktivitäts-Matrix, Themen-Clustern, Targeting-Hinweisen
- audits/linkedin-ads-anzeigen.csv — Roh-Anzeigen (N Zeilen)
- reports/11-linkedin-ads.html — Strategen-Report
Status aktualisiert in: status.md

LinkedIn-Ads-Lage:
- Akteure aktiv in Ad Library:  M von N
- Anzeigen in Zielregion:       A
- Top-Werber:                   AKTEUR mit N Anzeigen
- Themen-Cluster:               T
- Targeting-Daten verfügbar:    X von N Akteuren

[Wenn b2c_kontext aktiv:]
ℹ B2C-Kontext erkannt
- LinkedIn-Ads-Aktivität in B2C-Branchen oft gering — kann strategisches Nicht-Thema sein.

[Wenn Coverage-Lücke:]
ℹ Coverage-Lücke
- LinkedIn Ad Library liefert ohne Login eingeschränkte Sichtbarkeit. Bei kritischen Akteuren manueller Check empfohlen.

[Wenn Auffälligkeiten:]
⚠ LinkedIn-Ads-Insights:
- (1-3 Top-Auffälligkeiten)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestätigt — LinkedIn-Ads-Lage nur für den Kunden, kein Branchen-Benchmark.

Nächste Schritte:
1. 03-14-web-tech-und-tracking — Tech-Stack + Tracking + PageSpeed
2. (parallel möglich) 03-15-web-content-inventur — Sitemap-basierte Inhalts-Analyse
3. (parallel möglich) 03-11-social-linkedin — vertiefte LinkedIn-Organic-Analyse (kein Ads, sondern Content + Mitarbeiter)

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/linkedin-ad-library-mapping.md` — Apify-Actor-Optionen, URL-Patterns, Datenfelder, Login-Wall-Workaround, CSV-Schema, Markdown-Schema, Validierungs-Regeln
- `reference/linkedin-ads-besonderheiten.md` — Was bei LinkedIn anders ist als bei Google/Meta: Company-Page-Konzept, B2B-Fokus, Login-Wall, DSA-Targeting-Transparenz, EU-spezifische Daten

## Edge Cases

- **Akteur hat keine LinkedIn Company Page** → Standard-Fall in B2C / sehr kleinen Unternehmen. Skill markiert `linkedin_company_page_unbekannt: true`, listet zur Strategen-Review, läuft trotzdem durch.

- **Company-Page-Name weicht stark vom Akteurs-Namen ab** (z. B. lokale Tochter mit eigener Seite) → Skill nutzt Company-Page-URL aus Marken-Profil als Quelle der Wahrheit. Wenn Stratege Multi-Page-Match möchte: Override "auch ZUSATZURL abfragen".

- **Sehr viele aktive Anzeigen (>200 pro Akteur)** → Hard-Cap bei Top-100 nach Erst-Schalt-Datum absteigend (jüngste zuerst). Im Body Hinweis "Akteur hat >200 aktive Anzeigen, Top-100 ausgewertet."

- **Werbetexte sind in EN, Akteur sitzt aber in DE** → wird häufig bei internationalen WBs. Werbetexte roh übernehmen, im Frontmatter `werbetext_sprache: en` markieren, im Body Hinweis.

- **Sponsored Messaging und InMail-Anzeigen sind selten in der Ad Library sichtbar** → in der Library tauchen Sponsored-Messaging-Anzeigen oft nur als Stub auf. Skill markiert das im Output, zählt sie aber mit.

- **Targeting-Daten fehlen komplett ohne Login** → in vielen Fällen sind die DSA-Targeting-Hinweise nur mit LinkedIn-Login sichtbar. Skill markiert `targeting_verfuegbar: false` und beschränkt das Targeting-Aggregat auf die wenigen Akteure mit Daten.

- **Apify-Actor liefert keine Anzeige-IDs** → Skill generiert Hash-basierte ID aus `werbender_name + erst_schalt_datum + werbetext_headline`. Dadurch sind Re-Runs stabil.

- **Apify-Actor scheitert (Library-UI-Änderung oder Login-Wall verschärft)** → Fallback auf manuellen Mini-Workflow: dem Strategen die Ad-Library-URLs aller Akteure ausgeben, mit Bitte, manuell zu prüfen (idealerweise eingeloggt). Im Output ein `manueller_check_erforderlich`-Block mit Akteurs-Liste.

- **Internationale Akteure** (Ad Library zeigt auch andere Regionen) → Region-Filter (Schritt 4.5) anwenden. Anzeigen außerhalb der Zielregion in eigener Sektion `internationale_aktivitaet` listen.

- **Recruiting-Dominanz** → wenn der allergrößte Teil aller WB-Anzeigen Recruiting ist, ist Demand-Gen-Wettbewerb gering. Wird als Auffälligkeit `recruiting_dominiert` ausgegeben und ist für die spätere `04-02-kanal-chancen-analyse` ein wichtiges Signal.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/linkedin-ads.md`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Anzeigen (via `drive.py upsert-text`)
- Standard-Schlussformat
- `status.md` und Dashboard werden aktualisiert (`drive.py upsert-text`)
- HTML-Report aus `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **Library-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/linkedin-ads-AKTEURSSLUG.json`, am Ende komprimiert nach Drive `assets/raw/`
- **Werbetexte unverändert** lassen — Originaltexte sind die Datenbasis, keine Übersetzungen oder Umformulierungen
- **Coverage-Limitierungen explizit dokumentieren** — der Stratege darf beim Kunden-Gespräch nicht überziehen, wenn die Login-Wall die Sichtbarkeit eingeschränkt hat
- **B2C-Kontext nicht als Skill-Abbruch behandeln** — auch ein Null-Ergebnis ist wertvoll, weil es eine strategische Annahme datenbasiert untermauert
