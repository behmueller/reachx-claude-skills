# Output-Schema fuer `03-08-social-instagram`

Definiert die drei Pflicht-Outputs:

- `audits/instagram-profile.csv` - Profil-Kennzahlen pro Akteur (eine Zeile)
- `audits/instagram-posts.csv` - Posts-Sample pro Akteur (eine Zeile pro Post)
- `audits/instagram-wettbewerb.md` - Aggregat-Markdown mit Profil-Snapshot, Posts-Statistik, Content-Pillars, Auffaelligkeiten

Plus die Pattern-Sprache fuer die Folge-Social-Skills (`03-09-social-tiktok`, `03-10-social-pinterest`) - die nutzen analoges Schema mit Plattform-spezifischen Feldern.

## Profile-CSV (`audits/instagram-profile.csv`)

UTF-8, mit Header, Komma-getrennt, doppelte Anfuehrungszeichen fuer Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,ig_handle,ig_profil_url,
followers_count,follows_count,posts_count_total,
is_verified,account_typ,business_category,
bio_text,bio_laenge,link_in_bio,
posts_letzte_12mo_count,posting_frequenz_pro_woche,
engagement_rate_median,engagement_rate_p25,engagement_rate_p75,
post_typ_mix_image_pct,post_typ_mix_carousel_pct,post_typ_mix_reel_pct,post_typ_mix_igtv_pct,
hashtag_durchschnitt_pro_post,content_pillars_count,
stories_aktiv,stories_hinweis,
profil_existiert,privat_account,account_inaktiv,scrape_blockiert,
datenstand_iso
```

### Spalten-Definitionen

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string (kebab-case) | ja | aus `liste.md` / `meta.json` |
| `akteurs_typ` | enum | ja | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Anzeigename aus Marken-Profil |
| `ig_handle` | string | ja | Instagram-Handle ohne `@` |
| `ig_profil_url` | URL | ja | normalisierte Profil-URL |
| `followers_count` | int | ja | aus Apify, 0 wenn nicht ermittelbar |
| `follows_count` | int | ja | aus Apify |
| `posts_count_total` | int | ja | Gesamt-Posts laut Profil (nicht 12mo-Filter!) |
| `is_verified` | bool | ja | Verifizierungs-Status |
| `account_typ` | enum | ja | `personal | business | creator | unbekannt` |
| `business_category` | string / leer | nein | nur wenn Business-Account |
| `bio_text` | string | ja | voller Bio-Text |
| `bio_laenge` | int | ja | Zeichen-Anzahl |
| `link_in_bio` | URL / leer | nein | External-URL aus Bio |
| `posts_letzte_12mo_count` | int | ja | Anzahl gescrapter Posts in Zeitraum |
| `posting_frequenz_pro_woche` | float (2 NK) | ja | aus 12mo-Posts, 0 bei Inaktivitaet |
| `engagement_rate_median` | float (4 NK) | ja | Median ER ueber Posts |
| `engagement_rate_p25` | float (4 NK) | ja | 25-Perzentil |
| `engagement_rate_p75` | float (4 NK) | ja | 75-Perzentil |
| `post_typ_mix_image_pct` | float (1 NK) | ja | Prozent-Anteil |
| `post_typ_mix_carousel_pct` | float (1 NK) | ja | Prozent-Anteil |
| `post_typ_mix_reel_pct` | float (1 NK) | ja | Prozent-Anteil |
| `post_typ_mix_igtv_pct` | float (1 NK) | ja | Prozent-Anteil (oft 0) |
| `hashtag_durchschnitt_pro_post` | float (1 NK) | ja | Durchschnitt |
| `content_pillars_count` | int | ja | Anzahl erkannter Pillars |
| `stories_aktiv` | bool / leer | nein | aus Actor-Output, leer wenn nicht ermittelbar |
| `stories_hinweis` | string / leer | nein | Frei-Text (z. B. "stories_count_24h: 4") |
| `profil_existiert` | bool | ja | false bei geloeschtem/falschem Handle |
| `privat_account` | bool | ja | true wenn `private: true` von Apify |
| `account_inaktiv` | bool | ja | true wenn 0 Posts in 12mo |
| `scrape_blockiert` | bool | ja | true bei Rate-Limit / Login-Wall |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch

## Posts-CSV (`audits/instagram-posts.csv`)

UTF-8, mit Header, Komma-getrennt, doppelte Anfuehrungszeichen.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,post_id,post_url,post_typ,
taken_at_iso,caption_auszug,caption_laenge,
hashtag_count,mention_count,hashtags_top5,
likes_count,comments_count,video_views_count,
engagement_rate,content_pillar,datenstand_iso
```

### Spalten-Definitionen

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string | ja | wie Profile-CSV |
| `akteurs_typ` | enum | ja | `kunde | wettbewerber` |
| `post_id` | string | ja | Instagram-Shortcode |
| `post_url` | URL | ja | `https://www.instagram.com/p/SHORTCODE/` oder `/reel/...` |
| `post_typ` | enum | ja | `image | carousel | reel | igtv | unbekannt` |
| `taken_at_iso` | ISO-8601 | ja | Post-Datum |
| `caption_auszug` | string | ja | erste 200 Zeichen, voller Text in `raw/` |
| `caption_laenge` | int | ja | Zeichen-Anzahl des vollen Captions |
| `hashtag_count` | int | ja | Anzahl Hashtags im Post |
| `mention_count` | int | ja | Anzahl Mentions |
| `hashtags_top5` | string | ja | Komma-getrennt, max 5 Hashtags |
| `likes_count` | int | ja | aus Apify |
| `comments_count` | int | ja | aus Apify |
| `video_views_count` | int / leer | nein | nur bei Reels/IGTV |
| `engagement_rate` | float (4 NK) | ja | `(likes + comments) / followers` |
| `content_pillar` | string | ja | aus Schritt 7, z. B. `produkt_neuheit` |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch
3. `taken_at_iso` absteigend (juengste zuerst)

### Groessen-Grenze

Pro Akteur Hard-Cap 50 Posts. Bei 8 Akteuren = max 400 Zeilen.

## Markdown-Schema (`audits/instagram-wettbewerb.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-08-social-instagram
generiert_am: 2026-05-13T15:00:00Z
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only
  liste_bestaetigt_am: 2026-05-12T09:00:00Z

quelle:
  tool: apify
  profil_actor: apify/instagram-profile-scraper
  posts_actor: apify/instagram-post-scraper
  cookies_modus: anonym | session   # session = Apify-Cookies aktiv
  datenstand: 2026-05-13T15:00:00Z

# === Branchen-Aggregat ===
branchen_aggregat:
  akteure_mit_profil: 5
  akteure_aktiv_12mo: 4
  median_engagement_rate: 0.0182
  median_posting_frequenz_pro_woche: 2.5
  reel_anteil_branche_pct: 38.2
  branche_ig_relevanz: stark | mittel | schwach

# === Pro-Akteur-Matrix ===
akteure:
  - slug: kunde-mueller
    typ: kunde
    profil_existiert: true
    followers_count: 1240
    posts_letzte_12mo: 8
    posting_frequenz_pro_woche: 0.17
    engagement_rate_median: 0.0041
    post_typ_mix:
      image_pct: 62.5
      carousel_pct: 25.0
      reel_pct: 12.5
      igtv_pct: 0.0
    content_pillars_count: 2
  - slug: alpha-tech
    typ: wettbewerber
    ...

# === Auffaelligkeiten ===
auffaelligkeiten:
  - typ: kunde_engagement_unter_branchen_median
    titel: "Kunde liegt deutlich unter Branchen-Median"
    beschreibung: "Kunde 0.4%, Branchen-Median 1.8%"
    relevanz: hoch
    handlung: "Content-Qualitaet und Posting-Zeiten pruefen"
    betroffene: [kunde-mueller]
  - typ: wettbewerber_reel_strategie
    ...
---

# Instagram-Wettbewerb: KUNDE_NAME

## Uebersicht

(Anzahl Akteure mit Profil, aktive Akteure, Top-Engagement, Branchen-Relevanz)

## Branchen-Relevanz

(Bei `branche_ig_relevanz: schwach` prominent oben mit Hinweis fuer `04-02-kanal-chancen-analyse`)

## Vergleichs-Tabelle

| Akteur | Follower | Posts/Wo | ER Median | Reel-Anteil | Pillars |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Pro Akteur

### KUNDE-MUELLER (Kunde)

- **Profil**: 1.240 Follower, 380 Following, 87 Posts gesamt, Personal-Account, nicht verifiziert
- **Bio**: "..."
- **Link-in-Bio**: https://...
- **Posting**: 8 Posts in 12 Monaten = 0.17/Woche
- **Engagement-Rate**: Median 0.4% (P25 0.2%, P75 0.7%)
- **Post-Typ-Mix**: 62% Image, 25% Carousel, 12% Reel, 0% IGTV
- **Caption-Pattern**: Durchschnitt 180 Zeichen, 5 Hashtags pro Post
- **Content-Pillars**: produkt_neuheit (5 Posts), team_einblick (3 Posts)
- **Top-3-Posts**:
  - [Post-URL] - 4.1% ER - "Carousel ueber Produkt-Launch..."
  - ...
- **Stories**: keine Daten

### ALPHA-TECH (Wettbewerber)

...

## Content-Pillars-Uebersicht (branchenweit)

- **produkt_neuheit**: 4 von 5 WBs aktiv (Kunde 5 Posts)
- **kunden_referenz**: 3 von 5 WBs aktiv, Kunde NICHT (Luecke)
- **team_einblick**: 2 von 5 WBs aktiv (Kunde 3 Posts)

## Auffaelligkeiten

(detaillierte Liste mit Handlungs-Empfehlungen)
```

## Content-Pillars-Heuristik

Algorithmus fuer Schritt 7 des Skills:

### 1. Tokenize

Pro Post Caption:

- Lowercase
- Hashtags separat extrahieren (Liste plus aus Caption entfernen)
- Mentions separat extrahieren
- URLs entfernen
- Emoji entfernen
- Stopwords entfernen (Standard-DE-Stopwords plus IG-typische: `link`, `bio`, `mehr`, `swipe`, `tap`)
- Tokens auf laenge >= 4 Zeichen filtern

### 2. Token-Frequenz pro Akteur

Bag-of-Words pro Akteur: Token-Frequenz aufsummieren ueber alle Posts.

### 3. Co-Occurrence-Cluster

Tokens, die in mind. 3 Posts gemeinsam auftreten, bilden einen Cluster-Kandidaten. Cluster-Threshold:

- mind. 3 gemeinsame Posts
- mind. 2 zusammenhaengende Tokens

Heuristisch: Top-5 Cluster pro Akteur, Rest als `sonstiges`.

### 4. Cluster-Label

Pro Cluster die Top-3-Tokens als Label verwenden. Beispiele:

- `{produkt, neu, launch}` → `produkt_neuheit`
- `{team, mitarbeiter, einblick}` → `team_einblick`
- `{kunde, referenz, story}` → `kunden_referenz`
- `{event, messe, besuch}` → `event_messe`
- `{tipp, wissen, ratgeber}` → `wissen_tipps`

### 5. Pillar-Anzahl

Typischerweise 3-5 Pillars pro aktiven Akteur. Bei <3 Pillars: Akteur ist content-strategisch unfokussiert (Hinweis im Output). Bei >7 Pillars: Heuristik hat overfittet, Cluster zusammenlegen.

### 6. Statistik pro Pillar

Pro Pillar berechnen:

- Anzahl Posts
- Durchschnittliche Engagement-Rate
- Dominante Post-Typen
- Beispiel-Post-URL (Top-Engagement im Pillar)

## Validierungs-Regeln

Vor Schreiben der CSVs:

1. **`akteurs_slug`** muss in allen Posts-Zeilen auch in der Profile-CSV existieren
2. **`engagement_rate`** muss berechenbar sein - bei `followers_count = 0` oder `null` setze `engagement_rate` auf leer und vermerke im Profil-Eintrag `er_nicht_berechenbar: true`
3. **`post_typ_mix_*_pct`** muss in Summe 100.0 ergeben (Rundungs-Toleranz +/- 0.5)
4. **`posts_letzte_12mo_count`** in Profile-CSV muss gleich der Anzahl der Posts-CSV-Zeilen fuer den Akteur sein
5. **`taken_at_iso`** in Posts-CSV: alle Daten muessen >= heute - 12 Monate sein

Bei Validierungs-Fehler: Skill bricht ab mit klarem Hinweis, schreibt nichts persistent.
