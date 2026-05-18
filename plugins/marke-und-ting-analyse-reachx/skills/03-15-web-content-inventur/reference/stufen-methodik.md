# Stufen-Methodik: sitemap_only / light / full

Fachliche Grundlage für die Wahl der Inventur-Tiefe pro Akteur. Wird in Phase A als Default-Vorschlag genutzt; der Stratege kuratiert im Schema-Review.

## Getestete Actor-IDs

Vor dem Lauf immer den Health-Check (`mcp__apify__fetch-actor-details`) durchführen; bei `Session ID not found` sofort abbrechen. Für Stufe `sitemap_only` wird kein Actor benötigt.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `apify/website-content-crawler` | Website Content Crawler (official) | noch nicht getestet | unbekannt | Erste Wahl für Stufen `light` und `full` |
| `apify/cheerio-scraper` | Cheerio Scraper | noch nicht getestet | unbekannt | Leichtgewichtiger Fallback für statisches HTML |
| `apify/puppeteer-scraper` | Puppeteer Scraper | noch nicht getestet | fallback | Für JS-gerenderte Seiten wenn Cheerio unzureichend |

## Drei Stufen im Überblick

### `sitemap_only` (günstig)

**Ziel**: Bestands-Übersicht. Wie viele Seiten hat ein Akteur insgesamt, wie verteilt er sie über die Page-Typen?

**Methode**:

1. HTTP-GET `https://DOMAIN/sitemap.xml`
2. Fallback-Discovery falls 404:
   - `/sitemap_index.xml`
   - `/robots.txt` parsen auf `Sitemap:`-Zeilen
   - `/wp-sitemap.xml` (Wordpress-Default seit 5.5)
   - `/sitemap-1.xml`, `/page-sitemap.xml`, `/post-sitemap.xml`
3. Bei Sitemap-Index: rekursiv alle referenzierten Sitemaps laden
4. Alle URLs sammeln, in `audits/raw/sitemap-SLUG.xml` cachen
5. URL-Pfad-Pattern-Matching für Page-Typ-Klassifikation
6. Keine Crawl-Calls

**Kosten**: 0 Apify-Credits, nur einige HTTP-GETs.

**Stärken**: Schnell, robust, gibt Page-Typ-Verteilung. Reicht für `regional`-WB und für Sites, bei denen wir nur den Vergleichs-Bestand brauchen.

**Schwächen**: Keine Titles, keine Meta-Descriptions, keine Headings. Themen-Analyse nicht möglich. Keine Erkenntnis über die *Tiefe* eines Bereichs (z. B. Blog mit 100 Posts à 200 Wörtern vs. 100 Posts à 2.000 Wörter sieht gleich aus).

**Empfohlen für**:

- Regionale Wettbewerber, die nicht im Detail interessieren
- Akteure mit `bedrohungsgrad: inspiration` (vom Kunden genannt, aber nicht primärer Vergleichsmaßstab)
- Reduced-Modus bei knappem Apify-Budget

### `light` (mittel)

**Ziel**: Strukturelle Inventur mit Stichproben-Tiefe. Wir wissen, wie Pages aussehen (Title, Meta, H1), und können dadurch Themen-Cluster pro Page-Typ erkennen.

**Methode**:

1. Sitemap-Lauf wie `sitemap_only`
2. Pro Page-Typ-Cluster die Top-30 Seiten ausgewählt (Default; im Schema überschreibbar mit `light_top_n_pro_cluster`)
3. Apify `apify/website-content-crawler` mit `crawlerType: cheerio` (schnell für statisches HTML)
4. Extrahierte Felder: `title`, `metaDescription`, `h1`, `h2[]`, optional `wordCount`
5. Roh-Output in `audits/raw/content-crawl-SLUG.json`

**Top-30-Auswahl-Logik**: Sitemap-Reihenfolge wird als Default genommen — die ist bei den meisten CMS sinnvoll sortiert (z. B. Wordpress: chronologisch nach `lastmod`, Webflow: nach Collection-Reihenfolge). Stratege kann im Schema priorisieren (z. B. Top-30 nach `lastmod` oder nach manueller Liste).

**Kosten**: ca. 30 Crawl-Credits × ca. 5-8 Cluster pro Akteur = ca. 150-240 Credits pro Akteur.

**Stärken**: Strukturelle Themen-Erkennung möglich (über Titles und H1). Vergleichbar zwischen Akteuren auf gleicher Tiefe.

**Schwächen**: Vollständige Themen-Verteilung im Content-Hub nicht erfasst. Bei großen Blogs (>100 Posts) sieht man nur die 30 obersten.

**Empfohlen für**:

- Kunde (Standard)
- Direkte Wettbewerber (Top-3 nach `bedrohungsgrad: direkt`)
- Best-Practice-WB bei knappem Budget (statt `full`)

### `full` (teuer)

**Ziel**: Vollständige Themen-Inventur im definierten Content-Bereich. Wir wissen, was ein Akteur in seinem Content-Hub publiziert, welche Themen er priorisiert, wie tief er pro Thema geht.

**Methode**:

1. Sitemap-Lauf wie oben
2. Light-Crawl für die Cluster außerhalb der `include_patterns`-Bereiche (z. B. Produkt-Seiten, Unternehmens-Seiten)
3. **Vollcrawl** des `include_patterns`-Bereichs:
   - Apify `apify/website-content-crawler` mit `maxCrawlPages: 500` (Default; im Schema überschreibbar)
   - `maxCrawlDepth: 3` (folgt internen Links innerhalb der Include-Patterns)
   - Word-Count immer extrahieren
4. Themen-Heuristik per Token-Frequenz: Top-30 inhaltliche Tokens pro Akteur (Stopwords ausgeschlossen) als `top_themen`
5. Roh-Output in `audits/raw/content-crawl-SLUG.json`

**Kosten**: ca. 200-1.000 Crawl-Credits pro Akteur (je nach Content-Bereich-Größe). Bei Blogs >1.000 Posts wird `maxCrawlPages` der Begrenzer.

**Stärken**: Vollständiges Themen-Bild. Tiefen-Analyse möglich (Word-Count-Verteilung). Lehrwert für Best-Practice-Beobachtung.

**Schwächen**: Teuer. Nicht für viele Akteure parallel. Bei sehr großen Sites greift `maxCrawlPages`-Limit.

**Empfohlen für**:

- Best-Practice-WB (mindestens 1-2, max 5)
- Kunde selbst, wenn der Content-Hub strategisch relevant ist

**Optional Firecrawl-Alternative**:

Wenn `FIRECRAWL_API_KEY` gesetzt ist, kann Firecrawl `/scrape` mit `extract`-Schema oder `/crawl` für Bulk-Operationen alternativ genutzt werden. Vorteile: sauberere Markdown-Outputs, weniger Konfigurations-Aufwand. Nachteile: separate Account-Abrechnung, kleinere Limits in Free/Pro-Tiers.

## Stufen-Vergleichs-Matrix

| Aspekt | sitemap_only | light | full |
|---|---|---|---|
| Sitemap geladen | ja | ja | ja |
| Page-Typ-Verteilung | ja | ja | ja |
| Title pro Page | nein | top 30/cluster | im Content-Bereich |
| Meta-Description | nein | top 30/cluster | im Content-Bereich |
| H1/H2-Struktur | nein | top 30/cluster | im Content-Bereich |
| Word-Count | nein | optional | ja |
| Themen-Top-Tokens | nein | nein | ja |
| Themen-Lücken-Vergleich Kunde vs. WB | begrenzt | gut | optimal |
| Apify-Credits pro Akteur | 0 | ca. 240 | ca. 800 |
| Zeit pro Akteur | unter 30s | 5-15 min | 30 min - 2 h |

## Page-Typ-Heuristik (Mapping-Tabelle)

Standard-Mapping, das in jedem Schema vorgeschlagen wird. Pro Akteur kann der Stratege das im Schema überschreiben.

### `produkt_seite`

URL-Pfade die matchen (Substring im URL-Path):

- `/produkte/`, `/produkt/`
- `/shop/`
- `/products/`, `/product/`
- `/sortiment/`
- `/artikel/` (bei Shops)

### `blog_oder_ratgeber`

- `/blog/`
- `/ratgeber/`
- `/magazin/`
- `/news/`, `/neuigkeiten/`
- `/journal/`
- `/wissen/`
- `/insights/`
- `/artikel/` (bei Publishern, nicht bei Shops)
- `/post/`, `/posts/`

### `lp_oder_kampagne`

URL-Patterns:

- `/lp/`, `/landingpage/`, `/landing-page/`
- `/kampagne/`, `/campaign/`
- URL enthält `?utm_` (Tracking-Parameter)
- URL enthält `/aktion-`, `/promo-`

### `service_oder_branche`

- `/leistungen/`, `/leistung/`
- `/branchen/`, `/branche/`
- `/services/`, `/service/`
- `/loesungen/`, `/loesung/`, `/solutions/`
- `/anwendungen/`, `/use-cases/`
- `/fuer-`, `/for-` (z. B. `/fuer-handwerker/`)

### `unternehmens_seite`

- `/unternehmen/`
- `/ueber-uns/`, `/uber-uns/`, `/about/`, `/about-us/`
- `/karriere/`, `/jobs/`, `/careers/`
- `/kontakt/`, `/contact/`
- `/impressum/`, `/datenschutz/`, `/agb/`, `/legal/`, `/privacy/`
- `/team/`, `/mitarbeiter/`
- `/standorte/`, `/locations/`
- `/presse/`, `/press/`

### `sonstige` (Fallback)

Alle URLs, die zu keinem der obigen Patterns matchen. **Wenn `sonstige` >30% des Akteurs-Bestands hat → Auffälligkeit `cluster_zu_breit`**: Heuristik passt nicht zur Site-Struktur, der Stratege sollte das Mapping für diesen Akteur erweitern (z. B. eine Branchen-spezifische URL-Convention wie `/wissensbasis/`).

## Branchen-spezifische Excludes (Default-Vorschläge)

Pro Branche gibt es typische URL-Pfade, die fast immer auszuschließen sind. Wenn die Branche aus `meta.json` einer der folgenden zugeordnet werden kann, werden diese Patterns als Default in `exclude_patterns` der jeweiligen Akteure aufgenommen.

### E-Commerce / Shop

- `/cart/`, `/checkout/`, `/warenkorb/`, `/kasse/`
- `/account/`, `/mein-konto/`
- `/orders/`, `/bestellungen/`
- `?sort=`, `?filter=` (Filter-URLs sind Duplicate Content)

### Healthcare

- `/notdienst/`, `/anfahrt/` (falls reine Info-Seiten ohne Content)
- `/team/aerzte/` (separate Team-Pages — diskutabel, Stratege entscheidet)

### B2B-SaaS

- `/docs/`, `/documentation/` (eigener Page-Typ "Docs"; entweder ausschließen oder als eigener Cluster definieren)
- `/changelog/`, `/release-notes/`
- `/status/` (Status-Page)

### Local Service / Handwerk

- `/kontakt/`, `/anfahrt/` (oft mehrfach pro Standort)
- `/standort-XYZ/` (Standort-Seiten als eigener Cluster oder ausschließen)

### Publisher / Magazin

- `/autoren/`, `/redaktion/`
- `/archiv/[jahr]/[monat]/` (Datums-Archive)

## Auswahl-Logik pro Akteur (Default-Stufen-Vergabe in Phase A)

```
function default_stufe(akteur):
  if akteur.kategorie == "kunde":
    return "light"
  if akteur.kategorie == "best_practice_ueberregional":
    return "full"
  if akteur.kategorie == "kunde_genannt":
    if akteur.bedrohungsgrad == "direkt" and akteur ist unter top-3 markiert:
      return "light"
    if akteur.bedrohungsgrad == "inspiration":
      return "sitemap_only"
    return "sitemap_only"  # default fallback
  if akteur.kategorie == "regional":
    if akteur ist unter top-3 nach Reviews-Count:
      return "light"
    return "sitemap_only"
  return "sitemap_only"  # safest default
```

Wichtig: Der Skill schlägt nur Defaults vor — die finale Stufen-Vergabe ist Strategen-Entscheidung im Schema-Review.

## Reduced-Modus bei knappem Apify-Budget

Wenn der Stratege das Crawl-Budget einschränken muss:

1. Erst alle `full` → `light` herabstufen (spart pro Akteur ca. 600 Credits)
2. Dann alle `light` außer Kunde + Top-1-WB → `sitemap_only` (spart pro Akteur ca. 240 Credits)
3. Im Extremfall: alle Akteure auf `sitemap_only` — wir verlieren Themen-Tiefe, behalten aber Bestands-Vergleich

Der Skill weist im Schema-Body die mögliche Reduktions-Stufung aus, sodass der Stratege schnell entscheiden kann.
