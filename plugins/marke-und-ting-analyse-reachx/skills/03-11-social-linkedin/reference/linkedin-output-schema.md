# Output-Schema fuer `03-11-social-linkedin` (MTA-Modus)

Definiert die Pflicht-Outputs im MTA-Modus:

- `audits/linkedin-companies.csv` - Company-Kennzahlen pro Akteur (eine Zeile)
- `audits/linkedin-employees.csv` - Mitarbeiter-Listing aggregiert ueber alle Akteure (eine Zeile pro Mitarbeiter)
- `audits/linkedin-posts.csv` - Posts-Sample (eine Zeile pro Post, Company-Posts plus Personen-Posts)
- `audits/linkedin-wettbewerb.md` - Aggregat-Markdown mit Provenienz, Pro-Akteur-Matrix, Auffaelligkeiten

Im Standalone-Modus gilt das Schema aus `assets/report_template.md` plus `assets/aggregate_template.md`.

## Companies-CSV (`audits/linkedin-companies.csv`)

UTF-8, mit Header, Komma-getrennt, doppelte Anfuehrungszeichen fuer Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,linkedin_handle,company_url,
industry,company_size,headquarters,founded,
followers_count,employees_in_linkedin,
description_auszug,specialties_top5,website,
posts_letzte_12mo_count_company,
posts_letzte_12mo_count_personen,
posting_frequenz_pro_woche_company,
posting_frequenz_pro_woche_personen,
engagement_rate_median_company,engagement_rate_p25_company,engagement_rate_p75_company,
engagement_rate_median_personen,engagement_rate_p25_personen,engagement_rate_p75_personen,
format_mix_text_pct,format_mix_image_pct,format_mix_carousel_pct,
format_mix_video_pct,format_mix_document_pct,format_mix_article_pct,format_mix_poll_pct,
content_pillars_count,
mitarbeiter_listing_count,top_department,top_department_pct,
median_tenure_jahre,tenure_coverage_pct,
aktive_poster_count,aktive_poster_pct,
profil_existiert,scrape_blockiert,coverage_hinweis,
datenstand_iso
```

### Spalten-Definitionen (Auszug)

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string (kebab-case) | ja | aus `liste.md` / `meta.json` |
| `akteurs_typ` | enum | ja | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Anzeigename aus Marken-Profil |
| `linkedin_handle` | string | ja | Company-Handle ohne URL-Prefix |
| `company_url` | URL | ja | normalisierte Company-URL |
| `industry` | string | ja | LinkedIn-Industry-Feld |
| `company_size` | string | ja | z. B. "11-50 employees" |
| `headquarters` | string | nein | HQ-Stadt/Land |
| `founded` | int | nein | Gruendungsjahr |
| `followers_count` | int | ja | Company-Page-Follower, 0 wenn nicht ermittelbar |
| `employees_in_linkedin` | int | nein | LinkedIn-Schaetzung (oft ungenau) |
| `description_auszug` | string | ja | erste 200 Zeichen |
| `specialties_top5` | string | nein | Komma-getrennt, max 5 |
| `website` | URL | nein | aus Company-Page |
| `posts_letzte_12mo_count_company` | int | ja | Anzahl gescrapter Company-Posts |
| `posts_letzte_12mo_count_personen` | int | ja | Anzahl gescrapter Personen-Posts (Sample) |
| `posting_frequenz_pro_woche_company` | float (2 NK) | ja | aus Company-Posts |
| `posting_frequenz_pro_woche_personen` | float (2 NK) | ja | aus Personen-Posts, summiert ueber Sample |
| `engagement_rate_median_company` | float (4 NK) | ja | Median ER ueber Company-Posts |
| `engagement_rate_p25_company` | float (4 NK) | ja | 25-Perzentil |
| `engagement_rate_p75_company` | float (4 NK) | ja | 75-Perzentil |
| `engagement_rate_median_personen` | float (4 NK) | ja | Median ER ueber Personen-Posts |
| `engagement_rate_p25_personen` | float (4 NK) | ja | 25-Perzentil |
| `engagement_rate_p75_personen` | float (4 NK) | ja | 75-Perzentil |
| `format_mix_*_pct` | float (1 NK) | ja | Prozent-Anteil pro Format ueber Company-Posts |
| `content_pillars_count` | int | ja | Anzahl erkannter Pillars |
| `mitarbeiter_listing_count` | int | ja | Anzahl gelisteter Mitarbeiter |
| `top_department` | string | ja | Bucket-Name mit hoechstem Anteil |
| `top_department_pct` | float (1 NK) | ja | Anteil des Top-Departments |
| `median_tenure_jahre` | float (1 NK) / leer | nein | nur wenn Tenure-Coverage >= 30% |
| `tenure_coverage_pct` | float (1 NK) | ja | Anteil der Deep-Scrapes mit Tenure-Daten |
| `aktive_poster_count` | int | ja | Personen im Sample mit >=1 Post/Monat |
| `aktive_poster_pct` | float (1 NK) | ja | Anteil aktiver Poster im Sample |
| `profil_existiert` | bool | ja | false bei nicht erreichbarer Page |
| `scrape_blockiert` | bool | ja | true bei Backend-Fehler/Rate-Limit |
| `coverage_hinweis` | string / leer | nein | Frei-Text fuer Caveats |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch

## Employees-CSV (`audits/linkedin-employees.csv`)

UTF-8, mit Header. Eine Zeile pro Mitarbeiter (alle Akteure aggregiert).

### Spalten

```
akteurs_slug,akteurs_typ,name,profile_url,headline,
current_position,current_company,location,
department_inferred,position_level,
years_at_company,tenure_bucket,
is_deep_scraped,is_sample_post_author,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string | ja | wie Companies-CSV |
| `name` | string | ja | Voller Name |
| `profile_url` | URL | ja | `https://www.linkedin.com/in/...` |
| `headline` | string | nein | aus Apify Listing |
| `current_position` | string | nein | Job-Titel |
| `current_company` | string | nein | Aktueller Arbeitgeber (sollte mit Akteur matchen) |
| `location` | string | nein | Stadt/Land |
| `department_inferred` | enum | ja | siehe `sampling.md` |
| `position_level` | enum | nein | `c_level | director | head | lead | senior | manager | ic | unknown` |
| `years_at_company` | float (1 NK) / leer | nein | nur bei Deep-Scrape oder Listing-Hinweis |
| `tenure_bucket` | enum / leer | nein | `<1 Jahr | 1-3 Jahre | 3-5 Jahre | 5-10 Jahre | >10 Jahre` |
| `is_deep_scraped` | bool | ja | true wenn Profil in Schritt 9 deep-gescraped wurde |
| `is_sample_post_author` | bool | ja | true wenn Person in Schritt 11 fuer Posts gezogen wurde |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch
3. `is_deep_scraped` desc (Deep-gescrapte oben), dann `name` alphabetisch

### Groessen-Grenze

Hard-Cap 200 Mitarbeiter pro Akteur (siehe Schritt 6 im Skill). Bei 8 Akteuren = max 1.600 Zeilen.

## Posts-CSV (`audits/linkedin-posts.csv`)

UTF-8, mit Header. Eine Zeile pro Post (Company-Posts plus Personen-Posts gemischt, durch `author_type` getrennt).

### Spalten

```
akteurs_slug,akteurs_typ,author_type,author_name,author_url,
post_id,post_url,format,
date_posted_iso,text_auszug,text_laenge,
hashtag_count,hashtags_top5,mention_count,
likes_count,reposts_count,comments_count,
engagement_rate,
rating_hook,rating_substance,rating_format_fit,
rating_engagement_mechanic,rating_performance_ratio,rating_total,
theme_cluster,tonality,
is_repost,datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string | ja | wie Companies-CSV |
| `akteurs_typ` | enum | ja | `kunde | wettbewerber` |
| `author_type` | enum | ja | `company | person` |
| `author_name` | string | ja | Company-Name oder Personen-Name |
| `author_url` | URL | ja | Company-URL oder Profile-URL |
| `post_id` | string | ja | LinkedIn-Post-ID oder normalisierte URL-Hash |
| `post_url` | URL | ja | Public-Post-URL |
| `format` | enum | ja | `text | image | carousel | video | document | article | poll | repost` |
| `date_posted_iso` | ISO-8601 | ja | YYYY-MM-DD |
| `text_auszug` | string | ja | erste 200 Zeichen des Post-Bodys |
| `text_laenge` | int | ja | Zeichen-Anzahl des vollen Posts |
| `hashtag_count` | int | ja | Anzahl Hashtags |
| `hashtags_top5` | string | nein | Komma-getrennt, max 5 |
| `mention_count` | int | ja | Anzahl Mentions |
| `likes_count` | int | ja | aus Backend |
| `reposts_count` | int | ja | aus Backend |
| `comments_count` | int | ja | aus Backend |
| `engagement_rate` | float (4 NK) | ja | `(likes + reposts + comments) / followers` |
| `rating_hook` | int (1-5) / leer | nein | aus `03-12-social-linkedin-post-quality` Skill |
| `rating_substance` | int (1-5) / leer | nein | dito |
| `rating_format_fit` | int (1-5) / leer | nein | dito |
| `rating_engagement_mechanic` | int (1-5) / leer | nein | dito |
| `rating_performance_ratio` | float / leer | nein | Post-ER / Account-Median-ER |
| `rating_total` | float (1 NK) / leer | nein | gewichtete Summe |
| `theme_cluster` | string / leer | nein | z. B. `thought_leadership`, `product_news`, `recruiting` |
| `tonality` | enum / leer | nein | `informativ | inspirierend | provokativ | locker | formell | unklar` |
| `is_repost` | bool | ja | true wenn Repost ohne eigenen Kommentar |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch
3. `author_type` (`company` vor `person`)
4. `date_posted_iso` absteigend (juengste zuerst)

### Groessen-Grenze

Pro Akteur Company-Posts Hard-Cap 50, plus pro Akteur 10 Personen × 30 Posts Hard-Cap = max 350 Zeilen pro Akteur. Bei 8 Akteuren max 2.800 Zeilen.

## Markdown-Schema (`audits/linkedin-wettbewerb.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-11-social-linkedin
generiert_am: 2026-05-14T14:00:00Z
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only
  liste_bestaetigt_am: 2026-05-12T09:00:00Z

quelle:
  company_backend: bright_data | apify
  employees_backend: apify
  deep_profile_backend: bright_data | apify
  posts_backend: bright_data | apify
  rating_skill: 03-12-social-linkedin-post-quality | inline_fallback
  datenstand: 2026-05-14T14:00:00Z

# === Branchen-Aggregat ===
branchen_aggregat:
  akteure_mit_page: 6
  akteure_aktiv_12mo: 5
  median_engagement_rate_company: 0.0245
  median_engagement_rate_personen: 0.0387
  median_posting_frequenz_company_pro_woche: 1.8
  median_posting_frequenz_personen_pro_woche: 2.4
  top_format_branche: document
  top_format_anteil_pct: 31.2
  branche_linkedin_relevanz: stark | mittel | schwach

# === Pro-Akteur-Matrix ===
akteure:
  - slug: kunde-mueller
    typ: kunde
    profil_existiert: true
    followers_count: 1240
    mitarbeiter_listing_count: 38
    top_department: Engineering
    top_department_pct: 31.5
    median_tenure_jahre: 3.2
    posts_letzte_12mo_company: 8
    posts_letzte_12mo_personen: 14
    posting_frequenz_company_pro_woche: 0.17
    engagement_rate_median_company: 0.0041
    engagement_rate_median_personen: 0.0089
    format_mix:
      text_pct: 62.5
      image_pct: 25.0
      carousel_pct: 12.5
    content_pillars_count: 2
    aktive_poster_pct: 20.0
  - slug: alpha-tech
    typ: wettbewerber
    ...

# === Auffaelligkeiten ===
auffaelligkeiten:
  - typ: kunde_engagement_unter_branchen_median
    titel: "Kunde liegt deutlich unter Branchen-Median (Company)"
    beschreibung: "Kunde 0.41% ER, Branchen-Median 2.45%"
    relevanz: hoch
    handlung: "Content-Qualitaet, Posting-Zeiten und Format-Mix pruefen"
    betroffene: [kunde-mueller]
  - typ: wettbewerber_thought_leadership_strategie
    ...
---

# LinkedIn-Wettbewerb: KUNDE_NAME

## Uebersicht

(Anzahl Akteure mit Company-Page, aktive Akteure, Top-Engagement, Branchen-Relevanz)

## Branchen-Relevanz

(Bei `branche_linkedin_relevanz: schwach` prominent oben mit Hinweis fuer `04-02-kanal-chancen-analyse`)

## Vergleichs-Tabelle Company

| Akteur | Follower | Mitarb. | Posts/Wo (Co) | ER Median (Co) | ER Median (Pers) | Top-Format |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## Mitarbeiter-Aggregat

| Akteur | Listing | Top-Department | Median-Tenure | Aktive Poster |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## Pro Akteur

### KUNDE-MUELLER (Kunde)

- **Company-Page**: 1.240 Follower, "11-50 employees", HQ Muenchen
- **Branche**: B2B-SaaS
- **Mitarbeiter-Listing**: 38 Eintraege; Top-Department Engineering (31%), gefolgt von Sales (24%), Leadership (16%)
- **Tenure**: Median 3.2 Jahre (Coverage 70%)
- **Posting Company**: 8 Posts in 12 Monaten = 0.17/Woche
- **Posting Personen-Sample**: 14 Posts ueber 10 Profile = 1.4 Posts pro Person ueber 12 Monate
- **Engagement-Rate Company**: Median 0.4% (P25 0.2%, P75 0.7%)
- **Engagement-Rate Personen**: Median 0.9% (P25 0.4%, P75 1.4%)
- **Format-Mix Company**: 62% Text, 25% Image, 12% Carousel - kein Video, kein Document
- **Top-3-Posts** (nach ER):
  - [Post-URL] - 1.8% ER - "Carousel ueber Produkt-Launch ..."
  - ...
- **Content-Pillars**: produkt_neuheit (4 Posts), recruiting (3 Posts)

### ALPHA-TECH (Wettbewerber)

...

## Content-Pillars-Uebersicht (branchenweit)

- **product_news**: 5 von 6 WBs aktiv (Kunde 4 Posts)
- **thought_leadership**: 4 von 6 WBs aktiv, Kunde NICHT (Luecke)
- **recruiting**: 3 von 6 WBs aktiv (Kunde 3 Posts)

## Auffaelligkeiten

(detaillierte Liste mit Handlungs-Empfehlungen)
```

## Validierungs-Regeln

Vor Schreiben der CSVs:

1. **`akteurs_slug`** muss in allen Posts-Zeilen auch in der Companies-CSV existieren
2. **`engagement_rate`** muss berechenbar sein - bei `followers_count = 0` oder `null` setze `engagement_rate` auf leer und vermerke im Akteur-Eintrag `er_nicht_berechenbar: true`
3. **`format_mix_*_pct`** muss in Summe 100.0 ergeben (Rundungs-Toleranz +/- 0.5)
4. **`posts_letzte_12mo_count_company`** in Companies-CSV muss gleich der Anzahl der Posts-CSV-Zeilen mit `author_type=company` fuer den Akteur sein
5. **`mitarbeiter_listing_count`** muss gleich der Anzahl der Employees-CSV-Zeilen fuer den Akteur sein
6. **`date_posted_iso`** in Posts-CSV: alle Daten muessen >= heute - 12 Monate sein (Toleranz: 14 Tage)
7. **`current_company`** in Employees-CSV sollte zum Akteur passen - bei Mismatch (Person hat schon gekuendigt o. Ae.) als Hinweis im `coverage_hinweis` notieren

Bei Validierungs-Fehler: Skill bricht ab mit klarem Hinweis, schreibt nichts persistent.

## Konsistenz mit Standalone-Modus

Im Standalone-Modus (kein `meta.json`) werden die CSVs unter `output/SLUG/` mit aelteren Schemas (siehe `assets/report_template.md`) geschrieben. Wenn der Stratege spaeter in MTA-Modus wechselt: Daten muessen manuell migriert werden, kein automatischer Path.
