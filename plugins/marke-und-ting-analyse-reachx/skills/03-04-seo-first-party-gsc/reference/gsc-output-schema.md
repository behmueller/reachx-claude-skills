# Output-Schema

Definiert die Output-Formate des Skills für die drei Pflicht-Dateien:

- `audits/gsc-first-party.md` — Aggregat-Markdown mit YAML-Frontmatter
- `audits/gsc-performance.csv` — Query-Ebene als Roh-Datenbasis
- `audits/gsc-pages.csv` — Page-Ebene als Roh-Datenbasis

Alle Dateien sind verbindlich für die Folge-Skills — Schema-Änderungen brauchen Versions-Bump (siehe `contracts.md`).

## Markdown-Schema (`audits/gsc-first-party.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-04-seo-first-party-gsc
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
quelle:
  tool: ahrefs_mcp_gsc
  ahrefs_projekt_id: <id>
  gsc_property_url: <z. B. sc-domain:kunde.de oder https://www.kunde.de/>
  gsc_property_typ: <domain | url_prefix>
  gsc_verbunden_seit: <ISO oder null wenn unbekannt>
  abgefragt_am: <ISO-8601>

# === Zeiträume ===
zeitraeume:
  aktuell:
    von: <ISO>
    bis: <ISO>
    tage: 90
  vergleich_qoq:
    von: <ISO>
    bis: <ISO>
    tage: 90
  vergleich_yoy:
    von: <ISO>          # null wenn Historie < 365 Tage
    bis: <ISO>
    tage: 90
  verlauf_lang:
    von: <ISO>
    bis: <ISO>
    tage: <int>          # tatsächlich verfügbar, max 480

historie_verfuegbar_tage: <int>
daten_qualitaet: <hoch | mittel | niedrig | keine>

# === Performance-Stand (90 Tage aktuell) ===
statistiken_90_tage:
  clicks_total: <int>
  impressions_total: <int>
  ctr_avg: <float>           # 0..1 (0.034 = 3,4%)
  position_avg: <float>
  anteil_brand_klicks: <float oder null>               # 0..1, primär aus seo_brand_vs_nonbrand (Modus direkt)
  anteil_non_brand_klicks: <float oder null>           # 0..1, Komplement zu anteil_brand_klicks
  anteil_anonymous_queries_klicks: <float oder null>   # 0..1, nur im Fallback-Modus (Ahrefs-MCP) populiert
  top_country_code: <z. B. de>
  top_country_klick_anteil: <float>
  top_device: <mobile | desktop | tablet>
  top_device_klick_anteil: <float>

# === QoQ-Trend ===
statistiken_trend_qoq:
  clicks_delta_absolut: <int>
  clicks_delta_prozent: <float>     # positiv = Anstieg
  impressions_delta_prozent: <float>
  ctr_delta_punkte: <float>          # CTR-Differenz in Prozentpunkten
  position_delta: <float>            # negative Zahl = Verbesserung (höhere Position)

# === Analyse-Zähler ===
analyse_zaehler:
  anzahl_gewinner: <int>
  anzahl_verlierer: <int>
  anzahl_neu: <int>
  anzahl_verloren: <int>
  anzahl_cannibalization: <int>
  anzahl_hidden_content: <int>
  anzahl_ctr_gap: <int>
  anzahl_quick_win: <int>
  quick_win_geschaetztes_potenzial_klicks_pro_monat: <int>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <traffic_trend_negativ | traffic_trend_positiv | brand_dominant | anonymous_dominant | cannibalization_haeufig | cannibalization_keine_funde | hidden_content_relevant | ctr_gap_systematisch | quick_win_cluster | mobile_underperformance | non_dach_traffic_signifikant | sistrix_gsc_divergenz | sonstige>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion für die MTA-Slide>
    betroffene_queries: [<liste, optional>]
    betroffene_pages: [<liste, optional>]

# === CSV-Verknüpfung ===
csv_dateien:
  performance: audits/gsc-performance.csv
  pages: audits/gsc-pages.csv
  zeilen_performance: <int>
  zeilen_pages: <int>

# === Roh-Daten ===
raw_dateien:
  # Im Modus direkt (search-console-MCP):
  - audits/raw/gsc-performance-history.json
  - audits/raw/gsc-top-queries-current.json
  - audits/raw/gsc-top-queries-comparison.json
  - audits/raw/gsc-top-pages.json
  - audits/raw/gsc-brand-split.json
  # Im Modus fallback (Ahrefs-MCP) zusätzlich:
  - audits/raw/gsc-anonymous-queries.json
  # ... pro abgefragtem Tool eine Datei
mcp_pfad: <direkt | fallback>  # welcher MCP-Pfad wurde genutzt
---

# SEO-First-Party-Daten aus Google Search Console: <Kundenname>

## Übersicht

3-5 Sätze: Datenstand und Datenbasis (welcher MCP-Pfad, welche Property), Performance-Stand-Snapshot (Klicks/90T, QoQ-Trend), wo die größten Hebel liegen, Brand/Non-Brand-Split als Realitäts-Check (im Fallback-Modus stattdessen Anonymous-Anteil).

## Performance-Stand 90 Tage

| Metrik | Wert | QoQ-Trend |
|---|---|---|
| Klicks gesamt | <int> | <+/- %> |
| Impressionen gesamt | <int> | <+/- %> |
| Avg-CTR | <X,X%> | <+/- pp> |
| Avg-Position | <X,X> | <+/- Position> |

## Performance-Verlauf (16 Monate)

Beschreibung der Hauptbewegungen, Saisonalität, Knickpunkte. Hinweise auf Google-Updates (wenn Klick-Trend zu bekannten Update-Daten passt).

## Top-Queries (Top 30 nach Klicks)

| # | Query | Klicks | Impressions | CTR | Position | Trend QoQ |
|---|---|---|---|---|---|---|
| 1 | … | … | … | … | … | ↑ +24% |
| … | … | … | … | … | … | … |

Bei Top-Query = Brand: Markierung "(Brand)" und Hinweis im Body.

## Top-Pages (Top 20 nach Klicks)

| # | Page | Klicks | Impressions | CTR | Position | Anz. Queries | Kategorie |
|---|---|---|---|---|---|---|---|
| 1 | … | … | … | … | … | … | produkt |
| … | … | … | … | … | … | … | … |

## Brand vs. Non-Brand

**Im Modus direkt (search-console-MCP):**

- Brand-Klick-Anteil: <X%>
- Non-Brand-Klick-Anteil: <Y%>
- Brand-CTR vs. Non-Brand-CTR: <Brand X,X% vs. Non-Brand Y,Y%>

(Ein bis zwei Sätze: was bedeutet das für die Story — z. B. "60% Brand-Klicks bedeuten: der echte SEO-Hebel liegt im Non-Brand-Bereich. Brand-Traffic wird nicht durch SEO-Maßnahmen vergrößert, sondern durch Brand-Building.")

**Im Modus fallback (Ahrefs-MCP):** stattdessen Anonymous-Queries-Block einfügen:

- Klick-Anteil: <X%>
- Impressions-Anteil: <X%>
- Themen-Hypothese: <falls aus Page-Verteilung ableitbar>

(Ein bis zwei Sätze: "40% Anonymous heißt: ein großer Teil der echten Suchanfragen ist nicht direkt sichtbar; Page-Ebene-Analyse priorisieren.")

## Device- und Country-Splits

**Device:**

| Device | Klicks | Klick-Anteil | CTR | Avg-Position |
|---|---|---|---|---|
| mobile | … | … | … | … |
| desktop | … | … | … | … |
| tablet | … | … | … | … |

**Country (Top 5):**

| Land | Klicks | Klick-Anteil | CTR | Position |
|---|---|---|---|---|
| DE | … | … | … | … |
| … | … | … | … | … |

## Gewinner

Top-10 Queries mit größtem positiven Klick-Delta QoQ:

| Query | Klicks aktuell | Klicks Vergleich | Delta absolut | Delta % | Top-Page |
|---|---|---|---|---|---|
| … | … | … | … | +X% | … |

## Verlierer

Top-10 Queries mit größtem negativen Klick-Delta QoQ:

| Query | Klicks aktuell | Klicks Vergleich | Delta absolut | Delta % | Top-Page |
|---|---|---|---|---|---|
| … | … | … | … | -X% | … |

## Cannibalization

(nur wenn Fälle gefunden, sonst Sektion auslassen oder "Keine Cannibalization erkannt." schreiben)

| Query | Konkurrierende URLs | Positionen | Impressions 90T | Empfehlung |
|---|---|---|---|---|
| … | url-a / url-b | 14 / 19 | 1.200 | Consolidation / Canonical / internes Linking |

## Hidden-Content-Discovery

Versehentlich rankende Pages mit Klick-Potenzial:

| Query | Page | Klicks | Position | Empfehlung |
|---|---|---|---|---|
| … | /blog/alter-eintrag | 42 | 4 | Inhalt aktualisieren, zur Service-Page verlinken |

## CTR-Gap-Quick-Wins

Queries mit CTR ≥ 2 Prozentpunkte unter dem Domain-Benchmark bei gleicher Position:

| Query | Position | Impressions | Aktuelle CTR | Benchmark-CTR | Gap | Geschätzte Zusatz-Klicks/Monat |
|---|---|---|---|---|---|---|
| … | 6 | 1.800 | 1,2% | 4,1% | -2,9 pp | ~50 |

## Position-zu-Klick-Quick-Wins

Queries auf Position 4-10 mit hohem Impressions-Volumen — klassischer Quick-Win-Pool:

| Query | Position | Impressions | Aktuelle Klicks | Geschätztes Potenzial Pos 3 | Top-Page |
|---|---|---|---|---|---|
| … | 7 | 2.400 | 18 | ~140 | … |

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach `relevanz: hoch` → `mittel` → `niedrig`)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: …

**Betroffen**: <queries/pages>

(weitere Auffälligkeiten …)

## Lücken und Hinweise

- Datenbasis dünn? (`daten_qualitaet: niedrig` → Warnung hier)
- Property-Anbindung zu jung für 16M? → Hinweis hier
- Cannibalization-Analyse ausgefallen wegen MCP-Limit? → Hinweis hier
- Fehlende Tool-Antworten (welche Tools haben leer geliefert)
```

## CSV-Schema (`audits/gsc-performance.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
query,periode,datum_von,datum_bis,clicks,impressions,ctr,position,top_ranking_url,ist_anonymous,kategorie_analyse
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `query` | string | ja | Query-Text. Bei zensierten Queries: `__ANONYMOUS__` |
| `periode` | string | ja | `current` (aktuelle 90T) oder `comparison_qoq` oder `comparison_yoy` |
| `datum_von` | ISO-8601 | ja | Periode-Start |
| `datum_bis` | ISO-8601 | ja | Periode-Ende |
| `clicks` | integer | ja | Klicks in der Periode |
| `impressions` | integer | ja | Impressionen in der Periode |
| `ctr` | float | ja | Click-Through-Rate als Dezimalwert 0..1 (0.034 = 3,4%) |
| `position` | float | ja | Durchschnittliche Position |
| `top_ranking_url` | string oder leer | nein | Top-1-rankende Page für diese Query (in der Periode); leer bei Anonymous oder wenn nicht verfügbar |
| `ist_anonymous` | boolean | ja | `true` wenn Query von GSC zensiert (Pool-Eintrag) |
| `kategorie_analyse` | string | ja | Eines aus `{gewinner, verlierer, neu, verloren, cannibalization, hidden_content, ctr_gap, quick_win, brand, none}` — nur für `periode=current` aussagekräftig; bei Vergleichs-Perioden `none` |

### Sortierung

Innerhalb der Datei nach:

1. `periode` (`current` zuerst, dann `comparison_qoq`, `comparison_yoy`)
2. `clicks` absteigend
3. `query` alphabetisch (Tiebreaker)

### Beispiel

```csv
query,periode,datum_von,datum_bis,clicks,impressions,ctr,position,top_ranking_url,ist_anonymous,kategorie_analyse
mustermann gmbh,current,2026-02-13,2026-05-11,1820,5400,0.337,1.4,https://mustermann.de/,false,brand
kabel messer kaufen,current,2026-02-13,2026-05-11,142,4800,0.0296,5.8,https://mustermann.de/produkte/kabel-messer,false,quick_win
__ANONYMOUS__,current,2026-02-13,2026-05-11,890,18200,0.0489,8.1,,true,none
kabel messer kaufen,comparison_qoq,2025-11-13,2026-02-12,68,3900,0.0174,7.9,https://mustermann.de/produkte/kabel-messer,false,none
```

### Größen-Grenze

- Top-200 Queries × bis zu 3 Perioden = bis zu 600 Zeilen pro Periode-Set
- Plus eine Zeile pro Periode für `__ANONYMOUS__`
- Realistische Datei: 500-700 Zeilen, gut handhabbar in Excel

## CSV-Schema (`audits/gsc-pages.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt.

### Spalten

```
page_url,clicks,impressions,ctr,position,anzahl_queries,kategorie_seite,clicks_vergleich_qoq,delta_klicks_prozent
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `page_url` | string (URL) | ja | Vollständige Page-URL |
| `clicks` | integer | ja | Klicks 90T aktuell |
| `impressions` | integer | ja | Impressionen 90T aktuell |
| `ctr` | float | ja | CTR 0..1 |
| `position` | float | ja | Avg-Position 90T aktuell |
| `anzahl_queries` | integer oder leer | nein | Anzahl Queries, für die diese Page rankt (falls von API geliefert) |
| `kategorie_seite` | string | ja | Heuristik aus URL-Pfad: `{produkt, service, blog, news, presse, ueber_uns, kontakt, homepage, sonstige}` |
| `clicks_vergleich_qoq` | integer oder leer | nein | Klicks in 91-180-Tage-Periode (sofern verfügbar) |
| `delta_klicks_prozent` | float oder leer | nein | Delta vs. Vergleich-Periode (sofern verfügbar) |

### Page-Kategorisierungs-Heuristik

Pfad-basiert, einfache Regex-Matches (Reihenfolge entscheidet bei Konflikt):

1. Path = `/` oder leer → `homepage`
2. Path enthält `/produkt`, `/product`, `/p/`, `/shop` → `produkt`
3. Path enthält `/leistung`, `/service`, `/loesung` → `service`
4. Path enthält `/blog`, `/magazin`, `/ratgeber`, `/wissen` → `blog`
5. Path enthält `/news`, `/aktuelles` → `news`
6. Path enthält `/presse`, `/press` → `presse`
7. Path enthält `/ueber`, `/about`, `/team`, `/karriere` → `ueber_uns`
8. Path enthält `/kontakt`, `/contact`, `/anfrage` → `kontakt`
9. Sonst → `sonstige`

Skill darf die Heuristik branchen-spezifisch erweitern, wenn auffällige Pfade vorkommen (z. B. `/standorte` bei lokalen Akteuren).

### Sortierung

Nach `clicks` absteigend.

## Wie Folge-Skills die Outputs lesen

### `03-01-seo-sichtbarkeit-und-rankings`

Liest aus `gsc-first-party.md` Frontmatter:

- `statistiken_90_tage.clicks_total` → Realitäts-Anker für Sistrix-Visibility-Story
- `auffaelligkeiten` mit `typ: sistrix_gsc_divergenz` (sofern vorhanden) — wenn GSC-Skill nach Sistrix lief, sonst bleibt diese Auffälligkeit leer

Liest aus `gsc-performance.csv`:

- Filtert `periode=current`, sortiert nach `clicks` → cross-check mit Sistrix-Keyword-Liste: welche Queries kennt nur GSC, welche nur Sistrix?

### `03-02-seo-keyword-recherche`

Liest **primär** `gsc-performance.csv` (Filter `periode=current`, `ist_anonymous=false`) als Seed-Keyword-Set: das sind die Queries, für die der Kunde echte Klicks bekommt. Plus `gsc-pages.csv` für Page→Query-Mapping.

Erweitert um:
- Long-Tail-Variationen, Wettbewerbs-Gaps (aus Sistrix/Ahrefs)
- Difficulty (Ahrefs)

### `03-03-seo-keyword-kategorisierung`

Bekommt aus dem GSC-CSV bereits einen `kategorie_analyse`-Tag (Quick-Win, CTR-Gap, etc.) — das ist Performance-Kategorie, nicht Funnel-Kategorie. Die Funnel-/Intent-/Cluster-Kategorisierung kommt separat dazu.

### `03-15-web-content-inventur`

Liest `gsc-pages.csv` als Performance-Layer auf die Seitenstruktur. Jede inventierte Page bekommt die GSC-Klick/Impressions-Werte beigemischt → "diese Page hat 4.000 Wörter, aber 3 Klicks/Monat" wird sichtbar.

### `04-02-kanal-chancen-analyse`

Liest aus `gsc-first-party.md` Frontmatter:

- `analyse_zaehler.quick_win_geschaetztes_potenzial_klicks_pro_monat` → Hebel-Score für SEO-Kanal
- `auffaelligkeiten` mit hohem Relevanz-Score → strategische Story-Bausteine
- `statistiken_trend_qoq.clicks_delta_prozent` → Trend-Indikator (laufende SEO-Aktivität sichtbar?)

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. `historie_verfuegbar_tage` ≥ 30 — wenn weniger, Skill setzt `daten_qualitaet: keine`, schreibt minimale Outputs mit Hinweis "Property zu jung für sinnvolle Analyse"
2. `statistiken_90_tage.clicks_total` ≥ 0 (Plausibilitäts-Check)
3. Bei `daten_qualitaet: hoch | mittel`: mindestens 5 Quick-Wins ODER 5 Gewinner/Verlierer (sonst Hinweis "Datenbasis dünn")
4. CSV: jede Zeile hat alle Pflicht-Spalten gefüllt
5. CSV: `kategorie_analyse` ist gültiger Wert
6. Page-CSV: `kategorie_seite` ist gültiger Wert
7. Jede `auffaelligkeit` hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`
8. `analyse_zaehler` ist konsistent mit Anzahl der Tags in `gsc-performance.csv`

Wenn eine Regel verletzt wird: konkrete Fehlermeldung im Skill-Schluss-Format, welcher Eintrag korrigiert werden muss.
