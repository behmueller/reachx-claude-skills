# LinkedIn Ad Library — Zugriff und Mapping

Operative Vorgaben für den Zugriff auf die LinkedIn Ad Library — welche Apify-Actors, welche URL-Patterns, welche Datenfelder, welche Limitierungen. Plus CSV- und Markdown-Schema für die Outputs.

## Was ist die LinkedIn Ad Library?

LinkedIns öffentliches Werbetreibenden-Verzeichnis: `https://www.linkedin.com/ad-library/`. Seit 2023 (verpflichtend für die EU durch den Digital Services Act, DSA) zeigt LinkedIn dort alle Anzeigen, die in der EU geschaltet wurden, mit Schalt-Zeitraum, Anzeigentyp, Werbetext und teilweise Targeting-Daten.

**Was es zeigt:**

- Anzeigen aller Werbetreibenden, die in der EU geschaltet haben (DSA-Pflicht)
- Aktive plus kürzlich pausierte Anzeigen, in der Regel der letzten 12 Monate
- Erst-Schalt-Datum
- Aktive Regionen (Country-Level)
- Werbetext und Creatives (Bilder/Videos/Carousels)
- Anzeigentyp (Sponsored Content, Sponsored Messaging, Text Ads, Dynamic Ads, Video Ads, Document Ads, Event Ads)
- CTA-Text
- Teilweise (vor allem nach Login): Job-Title-, Industry-, Geography-Targeting

**Was es NICHT zeigt:**

- Anzeigen von Werbetreibenden außerhalb der EU, die nicht in der EU geschaltet haben (Coverage-Lücke außerhalb EU-Pflicht)
- Spend-Daten (keine Spend-Schätzungen wie bei Google über SpyFu in vergleichbarer Qualität)
- Klick-/Impression-Zahlen
- CPM/CPC-Werte
- Detail-Targeting (Skills, Groups) — nur die groben Achsen Job-Title, Industry, Geography

**Wichtigste Einschränkung: Login-Wall**

Manche Detail-Felder, vor allem Targeting-Daten, sind erst nach LinkedIn-Login vollständig sichtbar. Ohne Login zeigt LinkedIn nur einen reduzierten Datensatz. Der Skill arbeitet ohne Login (Apify scraped ohne Auth), das heißt:

- Werbetext, CTA, Creative-URL, Landingpage, Erst-Schalt-Datum, Regionen → sichtbar
- Job-Title-Targeting, Industry-Targeting → teilweise sichtbar (variiert pro Anzeige)
- Reichweiten-Schätzungen → meistens nicht sichtbar

Im Output Coverage-Lücke explizit dokumentieren — der Stratege kann bei kritischen Akteuren manuell eingeloggt nachprüfen.

## URL-Patterns

Pro Akteur drei mögliche Such-Modi:

| Suche nach | URL-Pattern | Wann |
|---|---|---|
| Company ID | `https://www.linkedin.com/ad-library/search?companyIds=COMPANYID` | **Standard im Skill** — wenn ID bekannt |
| Company Page Slug | `https://www.linkedin.com/ad-library/search?accountOwner=COMPANYSLUG` | wenn ID nicht bekannt, Slug aus Touchpoint-Inventur |
| Keyword | `https://www.linkedin.com/ad-library/search?keyword=NAME` | Fallback wenn ID + Slug nicht eindeutig |

**Company-ID-Lookup**: LinkedIn-interne IDs sind nicht immer in der URL sichtbar. Wenn die Company Page besucht wird, ist die ID im DOM oder in der URL einer Werbe-Seite einsehbar. Der Skill nutzt primär den Slug, fragt die ID bei Apify als zusätzliches Feld ab.

**Region-Override-Pattern**: `&dateOption=last-30-days&countries=DE` als zusätzliche Query-Parameter, um direkt den Region-Filter zu setzen. Default für REACHX-MTAs: `countries=DE`, bei DACH-Kunden `countries=DE,AT,CH`.

## Apify-Actor-Optionen — getestete Actor-IDs

Getestete Actors (Stand des Projekteinsatzes). Vor dem Lauf immer den Health-Check (Limit-1-Aufruf mit Kunden-Company-Page) durchführen; bei Fehler Alternativen aus der Liste probieren. Login-Wall-Quellen werden explizit markiert.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `apify/linkedin-ad-library-scraper` | LinkedIn Ad Library Scraper (official) | noch nicht getestet | unbekannt | Als Erste Wahl probieren |
| `igolaizola/linkedin-ad-library-scraper` | Community LinkedIn Ad Library | noch nicht getestet | unbekannt | Erster Fallback |
| `compass/linkedin-ad-library` | LinkedIn Ad Library Compass | noch nicht getestet | unbekannt | Zweiter Fallback |
| `apify/puppeteer-scraper` | Custom Puppeteer | — | fallback | Nur wenn kein spezialisierter Actor verfügbar |

**Login-Wall:** Die Ad Library ist öffentlich zugänglich — kein Auth-Token nötig. Sollte ein Actor Login-Fehler zurückgeben, ist das ein Apify-Sessions-Problem → Session-Reconnect, dann Retry. **Organische LinkedIn-Posts (Company-Feed)** sind hinter Login und nicht erhebbar ohne authentifizierten Scraper — explizit im Output als nicht erhoben markieren.

### Erste Wahl: `apify/linkedin-ad-library-scraper` (falls vorhanden im Store)

**Vorteile:**

- Speziell für LinkedIn Ad Library entwickelt — kennt die UI-Quirks
- Liefert strukturierte JSON-Daten
- Pagination-Handling eingebaut
- Login-Wall-Workaround: scraped, was öffentlich sichtbar ist, markiert fehlende Felder als null

**Input-Parameter:**

```json
{
  "companySlugs": ["mustermann-gmbh", "beta-solutions-ag"],
  "companyIds": [],
  "countries": ["DE"],
  "maxAdsPerCompany": 100,
  "dateRange": "last-12-months",
  "language": "de"
}
```

Wenn der Standard-Actor nicht verfügbar ist, im Apify-Store nach Alternativen suchen:

- `igolaizola/linkedin-ad-library-scraper`
- `compass/linkedin-ad-library`
- Generische Community-Actors

Pro Actor: vor dem Lauf einen kleinen Healthcheck mit der Kunden-Company-Page, um Datenformat zu prüfen.

### Fallback: Custom Puppeteer-Skript

Wenn kein spezialisierter Actor verfügbar oder verlässlich ist: `apify/puppeteer-scraper` mit Custom-Page-Function.

**Wichtige Page-Function-Schritte:**

1. Navigiere zur Ad-Library-URL des Akteurs
2. Warte auf `[data-test-id="ad-library-search-results"]` oder vergleichbares Element
3. Wenn Cookie-Banner: akzeptieren (Selektor `[data-test-id="cookie-banner-accept"]` oder vergleichbar)
4. **Login-Wall-Workaround**: bei Login-Dialog (oft als Modal-Overlay) versuchen, mit Escape oder Klick auf "Weiter ohne Login" zu schließen. Wenn das nicht klappt, mit reduziertem Datensatz weitermachen
5. Scroll-Trigger für Lazy-Loading: Page-Down mehrmals, bis Anzeigen-Anzahl stabil
6. Pro Anzeige-Karte: `querySelector('[data-test-id="ad-card"]')` und extrahiere Felder
7. Optional: Klick auf "Details ansehen" / "Über diese Anzeige" für vollständige Targeting-Daten (nur möglich wenn nicht hinter Login)

**Wichtig:** Die Ad-Library-UI ändert sich periodisch. Bei Änderungen müssen Selektoren angepasst werden. Im `audits/raw/linkedin-ads-AKTEURSSLUG.json` immer die Roh-Antwort speichern, damit bei UI-Bruch nur die Extraktions-Logik anzupassen ist.

### Hard-Fallback: Manueller Check

Wenn alle Apify-Optionen scheitern oder die Login-Wall zu restriktiv ist: Skill produziert eine Liste der Ad-Library-URLs aller Akteure und bittet den Strategen um manuellen Check (idealerweise mit LinkedIn-Login). Im Output-Markdown unter `manueller_check_erforderlich` listen.

## Datenfelder (Mapping zu Output-CSV-Spalten)

Was der Actor / das Scrape liefern muss, mit Mapping auf die CSV-Spalten:

| Ad-Library-Feld | CSV-Spalte | Typ | Hinweis |
|---|---|---|---|
| Company Page Name | `werbender_name` | string | manchmal abweichend vom Akteurs-Namen |
| Company ID | `werbender_company_id` | string | LinkedIn-interne ID, falls verfügbar |
| Ad ID | `anzeige_id` | string | wenn fehlt: Hash aus headline+datum+advertiser |
| Ad Type | `anzeige_typ` | enum | sponsored_content/sponsored_messaging/text_ads/dynamic_ads/video_ads/document_ads/event_ads/unbekannt |
| Creative Format | `format` | enum | single_image/video/carousel/document/event/text/unbekannt |
| First Shown Date | `erst_schalt_datum` | ISO-8601 | bei Monats-Granularität auf Monatsersten setzen |
| Last Shown Date | `letzte_anzeige_datum` | ISO-8601 oder leer | nur wenn pausiert |
| Active Countries | `aktive_in_regionen` | string (kommagetrennt) | ISO-Country-Codes |
| Intro Text | `werbetext_intro` | string | der Text über dem Creative (Sponsored Content) |
| Headline | `werbetext_headline` | string | die Headline am Creative (bei Sponsored Content max 200 Zeichen) |
| Description | `werbetext_beschreibung` | string | Description-Text unter der Headline (selten gefüllt bei manchen Formaten) |
| CTA Text | `cta_text` | string | z. B. "Mehr erfahren", "Demo buchen", "Registrieren", "Jetzt bewerben" |
| Final URL | `landingpage_url` | URL | inklusive Query-Params |
| Image/Video URL | `creative_url` | URL oder leer | nur bei Image/Video/Carousel |
| Job Title Targeting | `job_title_targeting` | string (semicolon-getrennt) | wenn Targeting-Daten sichtbar |
| Industry Targeting | `industry_targeting` | string (semicolon-getrennt) | wenn sichtbar |
| Geography Targeting | `geography_targeting` | string (semicolon-getrennt) | wenn sichtbar |

**`landingpage_tiefe`** wird im Skill berechnet aus der URL-Path-Tiefe (identisch zu `03-05-sea-google-ads-check`):

- `/` → 0 (Homepage)
- `/produkte/` → 1
- `/produkte/aufmasswerkzeuge/` → 2

## Region-Filter

Aus `meta.json.region`:

- `Deutschland` → Filter auf `DE`
- `DACH` → `DE`, `AT`, `CH`
- `Europa` → erweiterte Liste
- Bei Override `auch internationale Anzeigen`: kein Filter

Pro Anzeige `in_zielregion: true | false` setzen.

## CSV-Schema (`audits/linkedin-ads-anzeigen.csv`)

UTF-8, mit Header, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,werbender_name,werbender_company_id,
anzeige_id,anzeige_typ,format,erst_schalt_datum,letzte_anzeige_datum,
aktive_in_regionen,in_zielregion,
werbetext_intro,werbetext_headline,werbetext_beschreibung,cta_text,
landingpage_url,landingpage_tiefe,creative_url,
job_title_targeting,industry_targeting,geography_targeting,
cluster,datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string (kebab-case) | ja | aus `liste.md` / `meta.json` |
| `akteurs_typ` | enum | ja | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Anzeigename des Akteurs |
| `werbender_name` | string | ja | Library-Display-Name (kann abweichen) |
| `werbender_company_id` | string / leer | nein | LinkedIn-interne ID |
| `anzeige_id` | string | ja | Library-ID oder Hash |
| `anzeige_typ` | enum | ja | sponsored_content/sponsored_messaging/text_ads/dynamic_ads/video_ads/document_ads/event_ads/unbekannt |
| `format` | enum | ja | single_image/video/carousel/document/event/text/unbekannt |
| `erst_schalt_datum` | ISO-8601 | ja | Datum oder Monatserster |
| `letzte_anzeige_datum` | ISO-8601 / leer | nein | nur bei pausierten Anzeigen |
| `aktive_in_regionen` | string | ja | Komma-getrennte ISO-Country-Codes |
| `in_zielregion` | bool | ja | true wenn Region matched `meta.json.region` |
| `werbetext_intro` | string / leer | nein | Intro-Text über Creative |
| `werbetext_headline` | string / leer | nein | Headline am Creative |
| `werbetext_beschreibung` | string / leer | nein | Description |
| `cta_text` | string / leer | nein | CTA-Button-Text |
| `landingpage_url` | URL | ja | Ziel-URL inkl. UTM |
| `landingpage_tiefe` | int | ja | Pfad-Tiefe (0 = Homepage) |
| `creative_url` | URL / leer | nein | nur bei Image/Video/Carousel |
| `job_title_targeting` | string / leer | nein | semicolon-getrennte Job-Titles |
| `industry_targeting` | string / leer | nein | semicolon-getrennte Industries |
| `geography_targeting` | string / leer | nein | semicolon-getrennte Regionen |
| `cluster` | string | ja | branded/conquest_WB/recruiting/lead_gen/event/thought_leadership/thema_TOKEN/generic |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch
3. `in_zielregion` true zuerst
4. `erst_schalt_datum` absteigend (jüngste zuerst)
5. `anzeige_id` als Tiebreaker

### Größen-Grenze

Pro Akteur Hard-Cap 100 Anzeigen. Bei 10 Akteuren = max 1000 Zeilen.

## Markdown-Schema (`audits/linkedin-ads.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-07-sea-linkedin-ads-library-check
generiert_am: ISO-8601
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only
  liste_bestaetigt_am: ISO-8601 oder null

quelle:
  tool: linkedin_ad_library
  scraper: apify/linkedin-ad-library-scraper
  datenstand: ISO-8601

b2c_kontext: true | false
coverage_einschraenkung: keine | login_wall_leicht | login_wall_stark

# === Aktivitäts-Matrix pro Akteur ===
akteure:
  - akteurs_slug: SLUG
    name: AKTEURSNAME
    typ: kunde | wettbewerber
    kategorie_wenn_wb: kunde_genannt | regional | best_practice_ueberregional | null
    linkedin_company_page_url: URL
    linkedin_company_id: ID oder null
    match_methode: company_id | company_page_slug | suche_name | nicht_gefunden
    aktiv_in_ad_library: true | false
    anzahl_aktive_anzeigen: INT
    anzahl_in_zielregion: INT
    anzeigentypen_verteilung:
      sponsored_content: INT
      sponsored_messaging: INT
      text_ads: INT
      dynamic_ads: INT
      video_ads: INT
      document_ads: INT
      event_ads: INT
      unbekannt: INT
    aelteste_schalt_datum: ISO-8601 oder null
    juengste_schalt_datum: ISO-8601 oder null
    cluster_anzahl: INT
    cluster_top_3: [liste der 3 größten Cluster]
    landingpage_tiefe_durchschnitt: FLOAT
    targeting_verfuegbar: true | false
    job_title_targeting_top: [liste]
    industry_targeting_top: [liste]
    geography_targeting_top: [liste]
    raw_pfad: audits/raw/linkedin-ads-SLUG.json

# === Themen-Cluster über alle Akteure ===
themen_cluster:
  - cluster_name: NAME
    typ: branded | conquest_WB | recruiting | lead_gen | event | thought_leadership | thema | generic
    anzeigen_anzahl: INT
    aktive_akteure: [liste]
    beispiel_werbetext: AUSZUG

# === Targeting-Aggregat (wenn verfügbar) ===
targeting_aggregat:
  top_job_titles_branche: [(job_title, anzahl_akteure)]
  top_industries_branche: [(industry, anzahl_akteure)]
  top_geographies_branche: [(geography, anzahl_akteure)]

# === Aggregat-Statistik ===
statistiken:
  akteure_total: INT
  akteure_aktiv_in_library: INT
  akteure_inaktiv_in_library: INT
  anzeigen_total: INT
  anzeigen_in_zielregion: INT
  top_werber:
    akteurs_slug: SLUG
    anzahl_anzeigen: INT
  branchen_linkedin_ads_dichte: gering | mittel | hoch
  conquest_aktivitaeten: INT
  kunde_betreibt_conquest_gegen: [liste wb_slugs]
  recruiting_anteil_branche: FLOAT  # Anteil der Recruiting-Cluster-Anzeigen
  thought_leadership_aktive_wbs: INT

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: kunde_inaktiv_wb_aktiv | kunde_aktiv_wb_inaktiv | conquest_aktivitaet | kunde_macht_conquest | linkedin_ads_kein_branchen_thema | linkedin_login_wall_coverage_luecke | recruiting_dominiert | thought_leadership_konkurrenz | decision_maker_targeting_dominant
    titel: STRING
    beschreibung: 1-2 Saetze
    relevanz: hoch | mittel | niedrig
    handlungs_empfehlung: AKTION
    betroffene_akteure: [slugs]
---

# LinkedIn-Ads-Aktivität: KUNDENNAME

[B2C-Hinweis-Block wenn b2c_kontext: true]
[Coverage-Hinweis-Block]

## Übersicht
3-5 Sätze: wie viele Akteure aktiv, Top-Werber, LinkedIn-Ads-Dichte, Top-1-2-Auffälligkeiten.

## Akteurs-Vergleichs-Tabelle

| Akteur | Typ | Library-aktiv | Anzeigen (DE) | SC | SM | Text | Dyn | Vid | Doc | Cluster |
|---|---|---|---|---|---|---|---|---|---|---|

(SC=Sponsored Content, SM=Sponsored Messaging, Dyn=Dynamic, Vid=Video, Doc=Document)

## Pro Akteur

### AKTEUR1
- Aktivitäts-Status
- Anzeigentypen-Verteilung (kleine ASCII-Balken)
- Top-Anzeigen (max 5)
- Themen-Cluster im Portfolio
- Targeting-Profil (wenn verfügbar)

## Themen-Cluster über alle Akteure
## Targeting-Aggregat (wenn verfügbar)
## Branchen-LinkedIn-Ads-Lage
## Auffälligkeiten
## Lücken und Hinweise
```

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jeder Akteur in `akteure`-Liste mit `aktiv_in_ad_library: true` hat mindestens eine zugehörige Anzeige in der CSV
2. `anzahl_aktive_anzeigen` = Anzahl Zeilen in CSV für diesen Akteur
3. `anzahl_in_zielregion` = Anzahl Zeilen mit `in_zielregion: true`
4. Jede Anzeige in CSV hat einen `akteurs_slug`, der in `akteure`-Liste vorkommt
5. `werbetext_headline` darf leer sein (bei Text Ads / Sponsored Messaging oft so)
6. `cluster`-Wert ist konsistent mit `themen_cluster`-Liste im Frontmatter
7. `statistiken.akteure_aktiv_in_library` + `statistiken.akteure_inaktiv_in_library` = `akteure_total`
8. `landingpage_tiefe` ist int ≥ 0
9. `creative_url` nur gefüllt bei `format` in {single_image, video, carousel, document}
10. `targeting_verfuegbar: false` → alle Targeting-Felder müssen leer sein
11. Bei `b2c_kontext: true` muss ein B2C-Hinweis-Block im Body stehen
12. Bei `coverage_einschraenkung: login_wall_stark` muss Coverage-Hinweis-Block im Body stehen

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Caching und Re-Runs

Pro Lauf werden alle Roh-Antworten in `audits/raw/` abgelegt:

- `linkedin-ads-AKTEURSSLUG.json` — Ad-Library-Roh-Antwort

Bei Re-Run: Skill prüft, ob die Roh-Daten älter als 7 Tage sind:

- < 7 Tage → Cache nutzen, kein Re-Scrape
- ≥ 7 Tage → neu ziehen

Override `force_refresh` umgeht den Cache.

## Wie Folge-Skills die Outputs lesen

### `04-02-kanal-chancen-analyse`

Liest aus `linkedin-ads.md` Frontmatter:

- `statistiken.branchen_linkedin_ads_dichte` → Channel-Empfehlung (gering = ggf. First-Mover, hoch = teure Mitspielen)
- `b2c_kontext` → wenn true und Dichte gering: LinkedIn Ads als Nicht-Kanal markieren
- `akteure[i].anzahl_aktive_anzeigen` → ist LinkedIn Ads bereits Kanal des Kunden?
- `auffaelligkeiten` → strategische Argumente

### `04-04-forecast-modell`

Liest:

- `akteure[i].anzahl_aktive_anzeigen` → Aktivitäts-Größenordnung
- `themen_cluster` → mögliche Kampagnen-Themen
- `targeting_aggregat` → Decision-Maker-Profil für die Audience-Annahme

### `04-05-90-tage-plan`

Liest:

- `auffaelligkeiten` mit hoher Relevanz → konkrete Maßnahmen
- `themen_cluster` → wo der Kunde noch nicht spielt → Kampagnen-Vorschläge
- `recruiting_anteil_branche` → wenn hoch, Hinweis für Demand-Gen-Differenzierung

### `05-01-mta-slide-bausteine`

- Akteurs-Vergleichs-Tabelle direkt als Slide-Tabelle
- Top-Anzeigen-Beispiele für die "Wettbewerber-Werbung-LinkedIn"-Slide
- Targeting-Aggregat als "Decision-Maker-Bild"-Slide
- Auffälligkeiten als Insights-Slides
