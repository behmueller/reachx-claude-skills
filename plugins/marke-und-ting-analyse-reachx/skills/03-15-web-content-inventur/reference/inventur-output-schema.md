# Inventur-Output-Schema (Phase-B-Outputs)

Format-Definition für die Phase-B-Outputs des `03-15-web-content-inventur`-Skills.

## CSV-Output: `audits/content-inventur.csv`

### Spalten (Single-Source-of-Truth)

```
akteur_slug,akteur_name,url,page_typ,cluster,title,meta_description,h1,word_count,crawl_stufe,datenstand_iso
```

| Spalte | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `akteur_slug` | string (kebab-case) | ja | Slug aus dem Schema |
| `akteur_name` | string | ja | Anzeige-Name aus dem Schema |
| `url` | string (URL absolut) | ja | Vollständige URL der Page |
| `page_typ` | enum | ja | produkt_seite, blog_oder_ratgeber, lp_oder_kampagne, service_oder_branche, unternehmens_seite, sonstige |
| `cluster` | string | ja | Default = page_typ; bei akteurs-spezifischem Mapping kann Cluster feiner sein |
| `title` | string | optional | leer bei sitemap_only |
| `meta_description` | string | optional | leer bei sitemap_only |
| `h1` | string | optional | leer bei sitemap_only |
| `word_count` | int | optional | leer bei sitemap_only und meist auch light (außer Crawler liefert es) |
| `crawl_stufe` | enum | ja | sitemap_only / light / full |
| `datenstand_iso` | string ISO-8601 | ja | Zeitpunkt des Crawls für diesen Akteur |

### Validierungs-Regeln

- Eine Zeile pro Page (URL).
- Pro Akteur sortiert nach `page_typ`, dann nach `url`.
- Felder mit Kommata oder Anführungszeichen werden doppelt gequotet.
- Bei Stufe `sitemap_only`: `title`, `meta_description`, `h1`, `word_count` sind leer.
- Bei Stufe `light`: `title`, `meta_description`, `h1` gefüllt für die Top-30-pro-Cluster-Sample; für die restlichen Pages des Akteurs leer.
- Bei Stufe `full`: zusätzlich `word_count` gefüllt im `include_patterns`-Bereich.

## Markdown-Aggregat: `audits/content-inventur.md`

### Frontmatter

```yaml
---
skill: 03-15-web-content-inventur
status: abgeschlossen
schema_version: 1.0
generiert_am: 2026-05-13T15:30:00Z
basis:
  - audits/content-inventur-schema.md
  - audits/raw/sitemap-*.xml
  - audits/raw/content-crawl-*.json

projekt_slug: PROJEKT_SLUG
kunde: KUNDEN_NAME

statistik:
  akteure_gesamt: 5
  pages_gesamt: 4823
  stufen_verteilung:
    sitemap_only: 2
    light: 2
    full: 1
  groesster_cluster:
    name: blog_oder_ratgeber
    pages: 1842
  content_luecken_kunde: 4
  auffaelligkeiten_gesamt: 8

akteurs_zusammenfassung:
  - slug: kunde
    pages_gesamt: 312
    stufe: light
    top_cluster: produkt_seite
  - slug: alpha-tech
    pages_gesamt: 1284
    stufe: light
    top_cluster: blog_oder_ratgeber
  # ...
---
```

### Body-Struktur

```markdown
# Content-Inventur: KUNDEN_NAME

## Übersicht

- **Akteure inventarisiert**: 5
- **Pages gesamt**: 4.823
- **Stufen-Verteilung**: 2× sitemap_only, 2× light, 1× full
- **Größter Cluster**: blog_oder_ratgeber mit 1.842 Pages
- **Content-Lücken Kunde**: 4 identifiziert

## Page-Typ-Verteilung

Tabelle Akteur × Page-Typ mit Page-Counts und %-Anteilen:

| Akteur | produkt | blog | lp | service | unternehmen | sonstige | Gesamt |
|---|---|---|---|---|---|---|---|
| Kunde | 80 (26%) | 12 (4%) | 4 (1%) | 38 (12%) | 22 (7%) | 156 (50%) | 312 |
| Alpha Tech | 124 (10%) | 842 (66%) | 18 (1%) | 96 (7%) | 28 (2%) | 176 (14%) | 1.284 |
| Beta Solutions | 0 | 1.842 (88%) | 12 (1%) | 84 (4%) | 32 (2%) | 124 (5%) | 2.094 |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Pro Akteur

### Kunde (KUNDEN_NAME) — Stufe `light`

- **Pages gesamt**: 312
- **Page-Typ-Verteilung**: 26% produkt, 12% service, 7% unternehmen, 4% blog, 50% sonstige
- **Top-5-Cluster nach Page-Count**:
  1. sonstige (156)
  2. produkt_seite (80)
  3. service_oder_branche (38)
  4. unternehmens_seite (22)
  5. blog_oder_ratgeber (12)
- **Auffälligkeiten für Kunde**:
  - `cluster_zu_breit` — sonstige hat 50% Anteil, Page-Typ-Heuristik passt nicht ideal
  - `kunde_cluster_luecke` — nur 12 Blog-Pages, im Vergleich zu Alpha Tech (842) und Beta Solutions (1.842) ein klarer Content-Hub-Vorsprung der WB

### Alpha Tech GmbH — Stufe `light`

- **Pages gesamt**: 1.284
- **Page-Typ-Verteilung**: 66% blog, 10% produkt, 7% service, 2% unternehmen, 14% sonstige
- **Top-5-Cluster nach Page-Count**: ...
- **Auffälligkeiten für Alpha Tech**: ...

### Beta Solutions — Stufe `full`

- **Pages gesamt**: 2.094
- **Page-Typ-Verteilung**: 88% blog, 4% service, 2% unternehmen, 1% lp, 5% sonstige
- **Top-Themen (aus Token-Frequenz im Blog-Bereich)**:
  1. smart-home-integration (138 Erwähnungen)
  2. nachhaltigkeit (96)
  3. workflow-automatisierung (84)
  4. ...
- **Auffälligkeiten für Beta Solutions**: ...

## Content-Lücken Kunde vs. Wettbewerb

Die strategisch wichtigsten Beobachtungen:

1. **Blog-Lücke** — Kunde hat 12 Blog-Pages, Alpha Tech 842, Beta Solutions 1.842. Klarer Content-Hub-Rückstand. Empfehlung: Blog-Strategie als Kern-Initiative im 90-Tage-Plan.
2. **Themen-Lücke Smart-Home-Integration** — Top-Thema bei Beta Solutions (138 Erwähnungen), beim Kunden nicht erkennbar im Content. Potenzieller Quick-Win, weil Such-Volumen vorhanden ist (siehe SEO-Audit).
3. ...

## Pool-weite Auffälligkeiten

Sortiert nach Relevanz:

- `kunde_cluster_luecke` (blog_oder_ratgeber) — Kunde 0 vs. 842/1.842 bei WB
- `themen_luecke_kunde` (smart-home-integration) — Top-Thema bei Beta, fehlt beim Kunden
- `pagination_dominanz` (Gamma Services) — 42% Pagination-URLs, Content-Bestand kleiner als rohe Sitemap suggeriert
- `sitemap_fehlt` (Delta Shop) — keine Sitemap findbar, Inventur degradiert
- ...

## Vorbereitung für Folge-Skills

- **`04-02-kanal-chancen-analyse`**: Die Content-Lücken Kunde vs. WB sind primärer Input für die Argumentation "SEO+Content als Kanal-Chance". Themen-Lücken (`themen_luecke_kunde`) sind konkrete Themen-Hinweise.
- **`04-05-90-tage-plan`**: Top-3 Content-Lücken als Maßnahmen-Kandidaten. Best-Practice-Beobachtungen (Beta Solutions: 88% Blog-Anteil mit Themen-Tiefe) als Inspiration für die Content-Strategie.
- **`04-01-positionierungs-analyse`**: Page-Typ-Verteilung gibt Hinweise auf die strategische Ausrichtung des WB (Service-fokussiert vs. Content-fokussiert vs. Produkt-fokussiert).
```

## HTML-Report: `reports/13-03-15-web-content-inventur.html`

### Aufbau

Aus `reports/_shell.html` mit folgenden Sektionen:

1. **Stat-Strip oben** (4 Stats):
   - Akteure inventarisiert (Anzahl)
   - Pages gesamt
   - Größter Cluster (Name + Page-Count)
   - Content-Lücken Kunde (Anzahl)

2. **Sticky-TOC** (`nav.toc`):
   - Übersicht
   - Page-Typ-Heatmap
   - Pro-Akteur-Sektionen
   - Content-Lücken
   - Auffälligkeiten

3. **Page-Typ-Heatmap** (eigenes `<section>`):
   - HTML-Tabelle mit Akteur als Zeilen, Page-Typ als Spalten
   - Zell-Farbintensität nach %-Anteil (CSS-Klassen `.heatmap-0` bis `.heatmap-5`)
   - Klick auf Zelle scrollt zum Akteurs-Detail

4. **Pro Akteur** als `<details class="skill">`-Block:
   - Header: Akteurs-Name, Stufe-Badge (`.badge.stark` für full, `.badge.mittel` für light, `.badge.schwach` für sitemap_only)
   - Page-Count + Stufen-Info
   - Cluster-Tabelle (`table.data`)
   - Top-Themen (nur bei `full`)
   - Auffälligkeiten als Mini-Liste

5. **Content-Lücken** prominent als `.summary-card`:
   - Top-3 Lücken mit Handlungs-Empfehlung
   - Vermerkt klar: was bedeutet die Lücke für die MTA-Story?

6. **Auffälligkeiten** als `.suggestion`-Block:
   - Sortiert nach Relevanz
   - Pro Auffälligkeit: Typ-Badge, Beschreibung, betroffener Akteur

7. **Footer**:
   - Generiert-Am, Stufen-Verteilung, Hinweis auf CSV als Roh-Daten

## Auffälligkeiten-Definitionen

| Typ | Auslöser-Logik | Handlungs-Empfehlung |
|---|---|---|
| `kunde_cluster_luecke` | Kunde 0 Pages in einem Cluster UND mindestens 1 WB hat >10 Pages dort | "Content-Hub-Lücke im Cluster CLUSTER_NAME — Empfehlung als Top-Initiative im 90-Tage-Plan" |
| `themen_luecke_kunde` | Best-Practice-WB hat ein Top-Thema (Token-Frequenz top-10), Kunde hat es nicht im Content | "Thema THEMA_NAME bei WB stark präsent, beim Kunden Lücke — Themen-Brief vorschlagen" |
| `kunde_content_dominant` | Kunde hat in einem Cluster >50% Anteil über alle Akteure | "Kunde dominiert in CLUSTER_NAME — gutes Bestands-Asset, in MTA als Stärke ausweisen" |
| `wb_duenn_aber_intensiv` | WB hat <100 Pages aber durchschnittlich >1500 Wörter pro Post (nur bei full) | "WB_NAME setzt auf Tiefe statt Breite — Inspiration für eigene Content-Strategie" |
| `sitemap_fehlt` | Sitemap-Discovery für Akteur fehlgeschlagen | "AKTEUR_NAME: keine Sitemap findbar — Crawl-Strategie unklar, manueller Check empfohlen" |
| `pagination_dominanz` | >40% der rohen Sitemap-URLs matchen Pagination-Pattern | "AKTEUR_NAME: Pagination dominiert, Content-Bestand kleiner als rohe Sitemap suggeriert" |
| `cluster_zu_breit` | Cluster `sonstige` >30% des Akteurs-Bestands | "Page-Typ-Heuristik passt nicht zu AKTEUR_NAME — Mapping für diesen Akteur erweitern" |
| `lp_oder_kampagne_signal` | Akteur hat ≥3 Pages mit utm-Parametern oder /lp/-Pfaden | "AKTEUR_NAME: aktive Landing-Page-Kampagnen identifiziert — Hinweis auf Paid-Aktivitäten" |

## Raw-Caches

- `audits/raw/sitemap-SLUG.xml` — pro Akteur die Roh-Sitemap (bei Sitemap-Index: konkateniert oder im Original-Format als ZIP)
- `audits/raw/content-crawl-SLUG.json` — pro Akteur der Apify-Crawler-Output (nur bei Stufe `light` oder `full`)

Diese Caches werden NICHT in den HTML-Report eingebunden, sondern dienen der Reproduzierbarkeit und ggf. späteren Re-Analysen.

## Wichtige Konventionen

- **CSV ist Single-Source-of-Truth**. Markdown und HTML sind Sichten auf die CSV.
- Pfad-Angaben in Markdown und HTML sind relativ zum Projektordner.
- Datenstand pro Akteur in `datenstand_iso` — bei späteren Re-Runs für Trendvergleich relevant.
- Sortier-Konvention im Markdown: Akteure in Reihenfolge `kunde` → `kunde_genannt` → `regional` → `best_practice_ueberregional`. Auffälligkeiten nach Relevanz (Kunden-Lücken vor WB-Beobachtungen).
