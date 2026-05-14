# Meta Ad Library — Zugriff und Mapping

Operative Vorgaben für den Zugriff auf die Meta Ad Library — welche Apify-Actors, welche URL-Patterns, welche Datenfelder, welche Limitierungen. Erweitert das gemeinsame Output-Pattern aus `03-05-sea-google-ads-check/reference/ads-output-schema.md` um Meta-spezifische Felder.

## Was ist die Meta Ad Library?

Metas öffentliches Werbetreibenden-Verzeichnis: `https://www.facebook.com/ads/library/`. Seit 2019 (USA, politische Anzeigen) und seit 2023 (EU, durch DSA-Pflicht für alle Anzeigen ausgeweitet) zeigt Meta dort:

**Was gezeigt wird:**

- Alle aktiven Anzeigen jeder Facebook-Page (auch kleinere Werbetreibende, anders als Googles Verifizierungs-Hürde)
- Anzeigentypen (Single-Image, Video, Carousel, Collection, Dynamic Product Ads)
- Aktivierungs- und Stopp-Datum
- Plattform-Verteilung (Facebook, Instagram, Messenger, Audience Network)
- Werbetexte und Creatives
- Bei politischen oder gesellschaftlichen Anzeigen (EU-DSA-Bereich): Reach-Range, Spend-Range, Demographics-Aufschlüsselung

**Was NICHT gezeigt wird:**

- Spend-Daten bei normalen (nicht-politischen) Anzeigen
- Klick- und Impressions-Zahlen bei normalen Anzeigen
- Conversion-Raten
- Targeting-Details bei normalen Anzeigen (Interests, Custom Audiences, Lookalikes)
- Historische Performance-Trends

**Wichtige Unterschiede gegenüber Google Ads Transparency Center:**

| Aspekt | Google TC | Meta Ad Library |
|---|---|---|
| Auth | keine | keine |
| Hürde für Werbetreibende | Verifizierungs-Pflicht (kleinere Konten fehlen) | keine — jede Page mit Anzeigen ist sichtbar |
| Identifikations-Schlüssel | Domain | Facebook-Page-ID oder Page-Name |
| Plattform-Daten | nur Google-Surfaces | mehrere Surfaces pro Anzeige (FB/IG/Messenger/AN) |
| Spend-Daten | nein | nur bei politischen Anzeigen (EU-DSA) |
| Demographics | nein | nur bei politischen Anzeigen (EU-DSA) |
| Creative-Formate | Search/Display/Video/Shopping | Image/Video/Carousel/Collection/DPA |

## URL-Patterns

### Suche per Page-ID (Standard im Skill)

```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&view_all_page_id=PAGE_ID
```

Parameter:

- `active_status=active` — nur aktive Anzeigen
- `active_status=all` — auch gestoppte
- `ad_type=all` — alle Anzeigentypen
- `ad_type=political_and_issue_ads` — nur DSA-politische Anzeigen
- `country=DE` — Land-Filter
- `view_all_page_id=PAGE_ID` — numerische Page-ID

### Suche per Page-Name (Fallback wenn Page-ID nicht aufgelöst)

```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&q=PAGE_NAME&search_type=page
```

### EU-DSA-Bereich (politische Anzeigen, Sonder-URL)

```
https://www.facebook.com/ads/library/?active_status=active&ad_type=political_and_issue_ads&country=DE&view_all_page_id=PAGE_ID
```

## Page-Resolution (Schritt 2 im Skill)

Pro Akteur muss eine **Facebook-Page-ID** aufgelöst werden — das ist Voraussetzung für ad library-Lookup. Drei Stufen:

### Stufe 1: Direkt aus Marken-Profil

Lies `data/kunde.md` (für Kunde) oder `wettbewerber/AKTEUR-SLUG.md` (für Wettbewerber). Suche unter `touchpoints` nach `typ: facebook`. Die URL kann zwei Formen haben:

- `https://www.facebook.com/PAGE_HANDLE/` — Handle, muss zu ID aufgelöst werden
- `https://www.facebook.com/pages/NAME/PAGE_ID/` — ID direkt enthalten

Handle-zu-ID-Auflösung: über Apify-Actor `apify/facebook-page-scraper` oder direkt eine HEAD-Request mit Body-Parsing nach `"pageID":"..."` im HTML.

`page_match_konfidenz: hoch` — Quelle ist explizit dokumentiert.

### Stufe 2: Aus Briefing

Wenn `data/briefing.md` Facebook-URLs im Frontmatter unter `touchpoints` oder im Body nennt, gleiche Resolution wie Stufe 1.

`page_match_konfidenz: hoch`.

### Stufe 3: Auto-Resolution via Ad-Library-Suche

Wenn keine Page-URL in den Marken-Profilen, dann:

1. Akteurs-Name (aus `meta.json.kunde` oder `wettbewerber/liste.md`) in Ad-Library-Search:
   `https://www.facebook.com/ads/library/?q=AKTEUR_NAME&search_type=page&country=DE`
2. Treffer-Liste extrahieren
3. Bei mehreren Treffern: Heuristik
   - Verifiziertes Häkchen → bevorzugen
   - Sprache passend zur Region → bevorzugen
   - Domain im Page-About entspricht Akteurs-Domain → bevorzugen
   - Höchste Follower-Zahl als Tie-Breaker
4. Best-Match nehmen, `page_match_konfidenz: mittel` (bei Top-1-Treffer mit allen Signalen) oder `niedrig` (bei mehreren plausiblen Kandidaten)

Wenn gar kein plausibler Treffer: `facebook_page_id: null`, `page_match_konfidenz: nicht_gefunden`. Im Output unter "Lücken und Hinweise" alle gefundenen Kandidaten listen (Stratege kann override geben).

## Apify-Actor-Optionen

### Erste Wahl: `apify/facebook-ads-library-scraper`

Speziell für die Ad Library entwickelt, robust gegen UI-Änderungen.

**Input-Parameter:**

```json
{
  "urls": [
    "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DE&view_all_page_id=PAGE_ID"
  ],
  "maxAds": 100,
  "language": "de",
  "country": "DE"
}
```

**Output pro Anzeige (vereinfacht):**

```json
{
  "ad_archive_id": "1234567890123456",
  "page_id": "987654321",
  "page_name": "Beta Solutions",
  "page_verified": true,
  "ad_creation_time": "2025-09-15T08:00:00Z",
  "ad_delivery_start_time": "2025-09-15T08:00:00Z",
  "ad_delivery_stop_time": null,
  "publisher_platforms": ["FACEBOOK", "INSTAGRAM", "MESSENGER"],
  "ad_creative_body": "Werbetext primary...",
  "ad_creative_link_title": "Headline...",
  "ad_creative_link_description": "Description...",
  "ad_creative_link_caption": "beta-solutions.com",
  "cta_text": "Mehr erfahren",
  "ad_snapshot_url": "https://www.facebook.com/ads/library/?id=...",
  "image_url": "https://...",
  "video_preview_url": null,
  "card_count": null,
  "is_active": true,
  "is_political": false,
  "eu_political_metadata": null
}
```

Bei politischen Anzeigen ist `eu_political_metadata` gefüllt:

```json
{
  "estimated_audience_size": {"lower": 50000, "upper": 100000},
  "spend": {"lower": 500, "upper": 999, "currency": "EUR"},
  "impressions": {"lower": 100000, "upper": 200000},
  "demographics_by_age_gender": [...],
  "demographics_by_region": [...]
}
```

### Fallback-Actor: `curious_coder/facebook-ads-library-scraper` oder Community-Varianten

Wenn der Standard-Actor nicht verfügbar oder veraltet ist: Apify-Store nach Alternativen mit aktivem Maintenance-Status suchen. Pro Actor vor produktivem Lauf einen Healthcheck mit der Kunden-Page-ID, um Datenformat zu verifizieren.

### Hard-Fallback: Custom Puppeteer-Skript

`apify/puppeteer-scraper` mit Custom-Page-Function — wenn alle spezialisierten Actors scheitern.

**Wichtige Page-Function-Schritte:**

1. Navigiere zur Ad-Library-URL mit Page-ID
2. Warte auf `[role="article"]` (Anzeigen-Karte) oder Equivalent
3. Cookie-Banner akzeptieren wenn nötig
4. Scroll-Trigger für Infinite-Scroll: Page-Down bis Anzeigen-Anzahl stabil oder Cap erreicht
5. Pro Anzeigen-Karte:
   - Klick auf "Anzeigendetails ansehen" für vollständigen Werbetext
   - Plattform-Icons auslesen (FB/IG/Messenger/AN)
   - Erst-Schalt-Datum aus Karten-Header
   - Bei politischen Anzeigen: DSA-Block aus "Anzeigentransparenz"-Sektion extrahieren

**Wichtig:** Ad-Library-UI ändert sich periodisch (DSA-Erweiterungen, Layout-Updates). Bei Änderungen Selektoren anpassen. Im `audits/raw/meta-ads-AKTEUR-SLUG.json` immer die Roh-Antwort speichern.

### Letzte Option: Manueller Check

Wenn alle Apify-Optionen scheitern: Skill produziert eine Liste der Ad-Library-URLs aller Akteure und bittet den Strategen um manuellen Check. Im Output unter `manueller_check_erforderlich` listen.

## Anzeigen-CSV-Mapping (Meta-Erweiterung des Google-Patterns)

Die CSV folgt dem Pattern aus `03-05-sea-google-ads-check/reference/ads-output-schema.md`, ergänzt um Meta-spezifische Felder. Spalten-Reihenfolge (fest):

```
akteurs_slug,akteurs_typ,akteurs_name,page_id,page_name,page_verified,
anzeige_id,anzeige_typ,plattformen,erst_schalt_datum,letzte_anzeige_datum,
aktive_in_regionen,in_zielregion,
werbetext_primary,werbetext_headline,werbetext_beschreibung,cta_button,
landingpage_url,landingpage_tiefe,creative_url,karussell_anzahl_karten,
ist_politisch,dsa_reach_geschaetzt,dsa_spend_eur_min,dsa_spend_eur_max,
cluster,datenstand_iso
```

### Mapping Meta-Feld zu CSV-Spalte

| Meta Ad Library | CSV-Spalte | Typ | Hinweis |
|---|---|---|---|
| `page_id` | `page_id` | string (numerisch) | Pflicht für Resolution |
| `page_name` | `page_name` | string | Display-Name |
| `page_verified` | `page_verified` | bool | true bei blauem Häkchen |
| `ad_archive_id` | `anzeige_id` | string | wenn fehlt: Hash aus body+datum+page_id |
| (abgeleitet aus Creative) | `anzeige_typ` | enum | image/video/carousel/collection/dpa/unbekannt |
| `publisher_platforms` | `plattformen` | string (kommagetrennt) | facebook,instagram,messenger,audience_network |
| `ad_delivery_start_time` | `erst_schalt_datum` | ISO-8601 | |
| `ad_delivery_stop_time` | `letzte_anzeige_datum` | ISO-8601 oder leer | nur wenn nicht aktiv |
| `target_locations` oder Region-Filter | `aktive_in_regionen` | string | ISO-Country-Codes |
| (berechnet) | `in_zielregion` | bool | match gegen `meta.json.region` |
| `ad_creative_body` | `werbetext_primary` | string | Haupt-Text |
| `ad_creative_link_title` | `werbetext_headline` | string | Headline |
| `ad_creative_link_description` | `werbetext_beschreibung` | string | |
| `cta_text` | `cta_button` | string | "Mehr erfahren" etc. |
| `ad_creative_link_caption` oder Final URL | `landingpage_url` | URL | |
| (berechnet) | `landingpage_tiefe` | int | Pfad-Tiefe |
| `image_url` oder `video_preview_url` | `creative_url` | URL oder leer | |
| `card_count` | `karussell_anzahl_karten` | int oder leer | nur bei carousel/collection |
| `is_political` | `ist_politisch` | bool | |
| `eu_political_metadata.impressions.upper` | `dsa_reach_geschaetzt` | int oder leer | obere Range |
| `eu_political_metadata.spend.lower` | `dsa_spend_eur_min` | int oder leer | |
| `eu_political_metadata.spend.upper` | `dsa_spend_eur_max` | int oder leer | |
| (aus Skill-Schritt 6) | `cluster` | string | branded/conquest_WB/thema_TOKEN/generic |
| (Lauf-Datum) | `datenstand_iso` | ISO-8601 | |

### Anzeigentyp-Detection-Heuristik

Da Meta die Anzeigentypen nicht immer explizit liefert, im Skript ableiten:

- `video_preview_url` ist gefüllt → `anzeige_typ: video`
- `card_count` ist gefüllt und mehr als 1 → `anzeige_typ: carousel` oder `collection` (collection meist mit speziellem CTA "Jetzt einkaufen")
- `image_url` ist gefüllt und Carousel-Indikator fehlt → `anzeige_typ: image`
- Werbetext enthält dynamische Platzhalter `{{product.name}}` etc. → `anzeige_typ: dpa`
- Sonst → `anzeige_typ: unbekannt`

## Region-Filter

Aus `meta.json.region` (siehe `contracts.md` Abschnitt 2). Standard-Mapping identisch zu Google:

- `Deutschland` → `DE`
- `DACH` → `DE`, `AT`, `CH`
- `Europa` → erweiterte EU-Liste
- Bei Override "auch internationale Anzeigen": kein Filter

Meta liefert per `country` Parameter direkt nur Anzeigen für ein Land. Bei DACH separat pro Land scrapen und im Aggregat zusammenführen.

## Caching und Re-Runs

Pro Lauf werden alle Roh-Antworten in `audits/raw/` abgelegt:

- `meta-ads-AKTEUR-SLUG.json` — Ad-Library-Roh-Antwort

Bei Re-Run: Skill prüft, ob die Roh-Daten älter als 7 Tage sind:

- weniger als 7 Tage → Cache nutzen, kein Re-Scrape
- mehr oder gleich 7 Tage → neu ziehen

Override `force_refresh` umgeht den Cache.

## Markdown-Frontmatter-Erweiterungen (Delta zum Google-Pattern)

Pro Akteur im `akteure`-Block (siehe `03-05-sea-google-ads-check/reference/ads-output-schema.md`) zusätzliche Felder:

```yaml
akteure:
  - akteurs_slug: AKTEUR
    facebook_page_id: NUMMER oder null
    facebook_page_url: URL oder null
    page_match_konfidenz: hoch | mittel | niedrig | nicht_gefunden
    aktiv_in_ad_library: true | false
    anzahl_aktive_anzeigen: N
    anzahl_in_zielregion: N
    anzeigentypen_verteilung:
      image: N
      video: N
      carousel: N
      collection: N
      dpa: N
      unbekannt: N
    plattform_verteilung:
      facebook: N        # Anzeigen mit FB in plattformen-Liste
      instagram: N
      messenger: N
      audience_network: N
    dsa_block:
      anzahl_dsa_anzeigen: N
      dsa_spend_eur_min_summe: N oder null
      dsa_spend_eur_max_summe: N oder null
      dsa_reach_summe_geschaetzt: N oder null
    # ... restliche Felder identisch zu 03-05-sea-google-ads-check
```

Auf Aggregat-Ebene (`statistiken`) zusätzlich:

```yaml
statistiken:
  branchen_meta_dichte: gering | mittel | hoch
  plattform_schwerpunkt_branche: facebook | instagram | balanced
  format_schwerpunkt_branche: image | video | carousel | mixed
  akteure_ohne_page: N
  dsa_aktivitaet_in_branche: true | false
  # ... Rest identisch
```

## Validierungs-Regeln (Meta-spezifisch)

Zusätzlich zu den Validierungen aus `03-05-sea-google-ads-check/reference/ads-output-schema.md`:

1. Jeder Akteur mit `aktiv_in_ad_library: true` hat eine gültige `facebook_page_id`
2. `dsa_block.anzahl_dsa_anzeigen` entspricht der Anzahl Anzeigen mit `ist_politisch: true` in der CSV
3. `plattformen`-Liste pro Anzeige ist nicht leer (mindestens eine Plattform)
4. Bei `anzeige_typ: carousel` muss `karussell_anzahl_karten` mehr als 1 sein
5. Bei `ist_politisch: false` müssen alle `dsa_*`-Felder leer/null sein
6. `page_match_konfidenz: nicht_gefunden` → `facebook_page_id: null` und `aktiv_in_ad_library: false`

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Was NICHT in diesen Skill gehört

- **Targeting-Analyse für normale Anzeigen** — Meta liefert das nicht (nur DSA)
- **Click-Through-Rate oder Conversion-Schätzungen** — Meta liefert das nicht
- **Account-Insights** wie Custom Audiences oder Lookalikes — gehört nicht zur MTA, würde Werbe-Account-Zugriff brauchen
- **Anzeigen-Qualitäts-Score** — Meta liefert das nicht öffentlich
- **A/B-Test-Erkennung** — heuristisch unsicher, Stratege-Job
- **Vollständige Demographics auch für normale Anzeigen** — bleibt EU-DSA-exklusiv
