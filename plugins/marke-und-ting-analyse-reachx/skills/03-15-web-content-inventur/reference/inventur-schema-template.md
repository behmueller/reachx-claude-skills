# Inventur-Schema-Template (Phase-A-Output)

Format-Vorlage für `audits/content-inventur-schema.md`. Der Skill generiert diese Datei in Phase A; der Stratege editiert sie; danach setzt er `status: bestaetigt` und Phase B läuft.

## Datei-Aufbau

```markdown
---
skill: 03-15-web-content-inventur
status: vorgeschlagen   # vorgeschlagen | bestaetigt
basis:
  - meta.json
  - wettbewerber/liste.md
  - data/kunde.md            # optional
  - data/briefing.md         # optional
generiert_am: 2026-05-13T14:00:00Z
schema_version: 1.0

projekt_slug: PROJEKT_SLUG
kunde: KUNDEN_NAME

akteure:
  - slug: kunde
    name: KUNDEN_NAME
    domain: kunde-domain.de
    kategorie: kunde
    stufe: light
    include_patterns: []
    exclude_patterns: []
    light_top_n_pro_cluster: 30
    full_max_pages: 500
    notiz: "Mittlere Tiefe - genug für Cluster und Themen-Lücken"

  - slug: alpha-tech
    name: Alpha Tech GmbH
    domain: alpha-tech.de
    kategorie: kunde_genannt
    bedrohungsgrad: direkt
    stufe: light
    include_patterns: []
    exclude_patterns: []
    light_top_n_pro_cluster: 30
    notiz: "Top-3-Wettbewerber - vergleichbar mit Kunde"

  - slug: beta-solutions
    name: Beta Solutions
    domain: beta-solutions.com
    kategorie: best_practice_ueberregional
    stufe: full
    include_patterns:
      - /blog/
      - /ratgeber/
    exclude_patterns: []
    full_max_pages: 500
    notiz: "Best-Practice - lernfähigste Quelle, voller Content-Crawl"

  - slug: gamma-services
    name: Gamma Services
    domain: gamma-services.de
    kategorie: regional
    stufe: sitemap_only
    include_patterns: []
    exclude_patterns: []
    notiz: "Regionaler WB - Bestand reicht zum Vergleich"

filter_patterns_global:
  exclude_default:
    - /wp-admin/
    - /wp-content/uploads/
    - /wp-json/
    - /cart/
    - /checkout/
    - /warenkorb/
    - /kasse/
    - /tag/
    - /category/
    - /page/[0-9]+/
    - /archive/
    - /feed/
    - /login/
    - /register/
    - /mein-konto/
    - /my-account/
    - "*.pdf"
    - "*.jpg"
    - "*.png"
    - "*.xml"

page_typ_heuristik:
  produkt_seite:
    - /produkte/
    - /shop/
    - /products/
  blog_oder_ratgeber:
    - /blog/
    - /ratgeber/
    - /magazin/
    - /news/
    - /journal/
  lp_oder_kampagne:
    - /lp/
    - /landingpage/
    - "?utm_"
  service_oder_branche:
    - /leistungen/
    - /branchen/
    - /services/
    - /loesungen/
  unternehmens_seite:
    - /unternehmen/
    - /ueber-uns/
    - /karriere/
    - /kontakt/
    - /impressum/
  # alles andere -> sonstige

tool_auswahl:
  sitemap_loader: http_get
  light_crawler: apify/website-content-crawler
  full_crawler: apify/website-content-crawler
  firecrawl_verfuegbar: false   # wenn FIRECRAWL_API_KEY gesetzt -> true

budget_schaetzung:
  sitemap_only_credits: 0
  light_credits_pro_akteur: 240
  full_credits_pro_akteur: 800
  gesamt_credits_geschaetzt: 1240
---

# Content-Inventur-Schema: KUNDEN_NAME

## Akteurs-Liste

Folgende Akteure werden inventarisiert, mit Begründung der vorgeschlagenen Stufe:

### Kunde (1)

- **KUNDEN_NAME** (kunde-domain.de) — Stufe `light`. Begründung: Wir wollen genug Tiefe für Cluster-Erkennung und Themen-Lücken, aber nicht jede einzelne Seite.

### Direkte Wettbewerber (N)

- **Alpha Tech GmbH** (alpha-tech.de) — Stufe `light`. Begründung: Top-3-WB, vergleichbar mit Kunde auf gleicher Tiefe.

### Best-Practice-Wettbewerber (M)

- **Beta Solutions** (beta-solutions.com) — Stufe `full`. Begründung: Best-Practice — lernfähigste Quelle, voller Content-Crawl im Blog-Bereich.

### Regionale Wettbewerber (K)

- **Gamma Services** (gamma-services.de) — Stufe `sitemap_only`. Begründung: Reine Bestands-Vergleichsbasis reicht.

## Filter-Patterns

Globale Excludes (Defaults oben im Frontmatter) decken Wordpress-Backend, Shop-Transaktional, Pagination/Tag-Archive, RSS, User-Bereiche und Asset-Files ab.

Pro Akteur können `include_patterns` und `exclude_patterns` ergänzt werden — z. B. wenn ein Akteur einen eigenen Shop-Bereich unter `/store/` hat, der ausgeschlossen werden soll.

## Page-Typ-Heuristik

Standard-Mapping (oben im Frontmatter): sechs Page-Typen plus `sonstige` als Fallback.

Anpassungs-Hinweise pro Akteur:

- Wenn ein Akteur eine domain-eigene Convention hat (z. B. `/wissen/` statt `/blog/`), Mapping pro Akteur ergänzen.
- Bei B2B-SaaS taucht oft `/docs/` als Page-Typ auf — manuell ergänzen falls relevant.

## Tool-Auswahl

- Sitemap-Loader: einfacher HTTP-GET auf `/sitemap.xml`, Discovery über `/sitemap_index.xml`, `/robots.txt`, `/wp-sitemap.xml`.
- Light/Full-Crawl: Apify `apify/website-content-crawler` (cheerio für statisches HTML, Playwright als Fallback bei JS).
- Optional Firecrawl als Alternative, wenn `FIRECRAWL_API_KEY` gesetzt ist.

## Budget-Übersicht

| Stufe | Akteure | Credits pro Akteur | Summe |
|---|---|---|---|
| sitemap_only | K | 0 | 0 |
| light | X | ca. 240 | ca. X*240 |
| full | M | ca. 800 | ca. M*800 |
| **Gesamt** | N | | ca. SUMME |

Bei knappem Apify-Budget: Stratege kann Stufen runterstufen (z. B. `light` → `sitemap_only` für regional-WB).

## Pflicht-Review durch den Strategen

Bitte folgende Punkte prüfen:

1. **Stufe pro Akteur** — besonders die `best_practice`-WB (Default `full`), die das meiste Budget brauchen. Bei knappem Budget runterstufen.
2. **Filter-Patterns** — wenn ein Akteur eine eigenwillige URL-Struktur hat, akteurs-spezifische Excludes/Includes ergänzen.
3. **Page-Typ-Heuristik** — wenn die Standard-Pfade nicht passen, pro Akteur das Mapping erweitern.
4. **Budget** — wenn die Summe das verfügbare Apify-Budget übersteigt, Stufen runterstufen oder Akteure ausschließen.

Nach Review: `status: bestaetigt` im Frontmatter setzen, Skill erneut aufrufen.

## Anmerkungen vom Skill (Stand der Generierung)

- Akteurs-Liste basiert auf `wettbewerber/liste.md` mit `status: bestaetigt`.
- Wenn Liste fehlt: Kunden-only-Modus, Skill weist in der Konsolen-Ausgabe darauf hin.
- Crawl-Budget ist eine Schätzung — tatsächliche Apify-Credits können je nach Site-Komplexität abweichen.
```

## Default-Stufen pro Akteurs-Kategorie

| Kategorie | Default-Stufe | Begründung |
|---|---|---|
| `kunde` | `light` | Genug Tiefe für Cluster und Themen-Lücken |
| `kunde_genannt` mit `bedrohungsgrad: direkt` (Top-3) | `light` | Vergleichbar mit Kunde |
| `kunde_genannt` mit `bedrohungsgrad: inspiration` | `sitemap_only` | Bestands-Vergleich reicht |
| `regional` (Top-3 nach Reviews) | `light` | Direkte Konkurrenz, vergleichbare Tiefe |
| Restliche `regional` | `sitemap_only` | Reine Bestands-Sicht |
| `best_practice_ueberregional` | `full` | Lernfähigste Quelle |

## Pflicht-Felder pro Akteur

- `slug` (kebab-case, eindeutig)
- `name`
- `domain` (ohne Protokoll, ohne Pfad)
- `kategorie` (kunde / kunde_genannt / regional / best_practice_ueberregional)
- `stufe` (sitemap_only / light / full)
- `include_patterns` (Liste, leer = alle erlaubten URLs)
- `exclude_patterns` (Liste, leer = nur globale Defaults)

Optional:

- `light_top_n_pro_cluster` (Default 30, nur bei Stufe `light` oder `full`)
- `full_max_pages` (Default 500, nur bei Stufe `full`)
- `notiz` (Freitext für Strategen-Notizen)
