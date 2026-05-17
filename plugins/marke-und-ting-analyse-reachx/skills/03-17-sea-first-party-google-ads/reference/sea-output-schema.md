# Output-Schema

Definiert die Output-Formate des Skills für die drei Pflicht-Dateien:

- `audits/sea-first-party.md` — Aggregat-Markdown mit YAML-Frontmatter
- `audits/sea-kampagnen.csv` — Kampagnen-Ebene als Roh-Datenbasis
- `audits/sea-suchbegriffe.csv` — Search-Terms-Ebene als Roh-Datenbasis (auch Roh-Keyword-Quelle für die SEO-Skills)

Alle Dateien sind verbindlich für die Folge-Skills — Schema-Änderungen brauchen Versions-Bump (siehe `contracts.md`).

## Markdown-Schema (`audits/sea-first-party.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-17-sea-first-party-google-ads
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
quelle:
  tool: google_ads_api
  wrapper: scripts/google-ads.py
  customer_id: <10-stellige-ID>
  konto_name: <descriptive_name des Kontos>
  konto_status: <ENABLED | CANCELED | SUSPENDED | CLOSED>
  currency: <z. B. EUR>
  abgefragt_am: <ISO-8601>

# === Zeiträume ===
zeitraeume:
  zeitraum_lang:
    von: <ISO>
    bis: <ISO>
    tage: 365
  zeitraum_kurz:
    label: LAST_30_DAYS
    von: <ISO>
    bis: <ISO>
    tage: 30

daten_qualitaet: <hoch | mittel | niedrig | keine>

# === Account-Performance 12 Monate ===
statistiken_12_monate:
  cost: <float>                  # in Konto-Waehrung, unveraendert vom Wrapper
  impressions: <int>
  clicks: <int>
  ctr: <float>                   # 0..1
  avg_cpc: <float>
  conversions: <float>
  conversions_value: <float>
  roas: <float oder null>        # conversions_value / cost; null wenn cost = 0
  cpa: <float oder null>         # cost / conversions; null wenn conversions = 0
  cr: <float oder null>          # conversions / clicks; null wenn clicks = 0

# === Account-Performance 30 Tage ===
statistiken_30_tage:
  cost: <float>
  impressions: <int>
  clicks: <int>
  ctr: <float>
  avg_cpc: <float>
  conversions: <float>
  conversions_value: <float>
  roas: <float oder null>
  cpa: <float oder null>
  cr: <float oder null>

# === Trend 30 Tage vs. 12-Monats-Schnitt ===
trend:
  spend_30t_vs_schnitt_prozent: <float>   # 30T-Spend ggü. anteiligem 12M-Schnitt (12M/12)
  konto_aktiv: <true | false>             # false wenn Spend 30T = 0 bei 12M-Spend > 0

# === Conversion-Setup ===
conversion_setup_urteil: <sauber | mit_einschraenkung | kein_tracking>
conversion_actions_anzahl: <int>
conversion_actions_enabled: <int>
conversion_ga4_importiert: <true | false>
conversion_macro_micro_gemischt: <true | false>
conversion_offene_frage: <string oder null>   # beschreibende Strategen-Frage, falls Unklarheit bleibt

# === Kampagnentyp-Mix (Spend-Anteil je channel_type, 12 Monate) ===
kampagnentyp_mix:
  - channel_type: <SEARCH | DISPLAY | VIDEO | SHOPPING | DEMAND_GEN | PERFORMANCE_MAX | ...>
    spend_anteil: <float>        # 0..1
    cost: <float>

# === Quality-Score-Verteilung (spend-gewichtet, 12 Monate) ===
quality_score_verteilung:
  anteil_schwach: <float oder null>    # QS 1-4
  anteil_mittel: <float oder null>     # QS 5-7
  anteil_stark: <float oder null>      # QS 8-10
  keywords_ohne_qs: <int>              # quality_score = null
  hinweis: <string oder null>          # z. B. "QS fuer Mehrheit nicht vergeben"

# === Search-Terms-Kennzahlen ===
search_terms_kennzahlen:
  anzahl_suchbegriffe: <int>
  brand_anteil_spend: <float>          # 0..1
  brand_anteil_conversions: <float>    # 0..1
  streuverlust_anteil_spend: <float>   # 0..1, Anteil Spend in streuverlust-geflaggten Suchbegriffen
  anzahl_streuverlust: <int>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <conversion_tracking_fehlt | conversion_aus_ga4_importiert | conversion_macro_micro_gemischt | hoher_streuverlust_suchbegriffe | quality_score_schwach | kampagne_ohne_conversions | budget_konzentration | brand_anteil_hoch | roas_unter_eins | konto_inaktiv | sonstige>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion für die MTA-Slide>
    betroffene_kampagnen: [<liste, optional>]
    betroffene_suchbegriffe: [<liste, optional>]

# === CSV-Verknüpfung ===
csv_dateien:
  kampagnen: audits/sea-kampagnen.csv
  suchbegriffe: audits/sea-suchbegriffe.csv
  zeilen_kampagnen: <int>
  zeilen_suchbegriffe: <int>

# === Roh-Daten ===
raw_dateien:
  - audits/raw/sea-account-overview-12m.json
  - audits/raw/sea-account-overview-30d.json
  - audits/raw/sea-campaign-performance-12m.json
  - audits/raw/sea-campaign-performance-30d.json
  - audits/raw/sea-search-terms.json
  - audits/raw/sea-keyword-performance.json
  - audits/raw/sea-conversion-actions.json
---

# SEA-First-Party-Daten aus dem Google-Ads-Konto: <Kundenname>

## Übersicht

3-5 Sätze: welches Konto (Name, ID, Status), Spend-Größenordnung über 12 Monate,
ROAS-Lesart, wo die größten Hebel liegen. Conversion-Setup-Urteil als
Vertrauens-Disclaimer für alle ROAS-Zahlen: "Conversion-Tracking <Urteil> —
die ROAS/CPA-Werte sind <belastbar / mit Vorsicht zu lesen / nicht belastbar>."

## Account-Performance

| Metrik | 12 Monate | Letzte 30 Tage |
|---|---|---|
| Spend | <X EUR> | <X EUR> |
| Impressionen | <int> | <int> |
| Klicks | <int> | <int> |
| Avg-CTR | <X,X%> | <X,X%> |
| Avg-CPC | <X,XX EUR> | <X,XX EUR> |
| Conversions | <X> | <X> |
| Conversion-Value | <X EUR> | <X EUR> |
| ROAS | <X,X> | <X,X> |
| CPA | <X,XX EUR> | <X,XX EUR> |
| CR | <X,X%> | <X,X%> |

Ein bis zwei Sätze zum Trend (läuft das Konto gerade stärker/schwächer als im
12-Monats-Schnitt? Pausiert?).

## Kampagnen-Performance

(Tabelle je Kampagne, 12-Monats-Range, sortiert nach Spend absteigend)

| Kampagne | Typ | Status | Spend | Klicks | CTR | Conv. | ROAS | CPA | CR |
|---|---|---|---|---|---|---|---|---|---|
| Search - Brand DE | SEARCH | ENABLED | … | … | … | … | … | … | … |

## Kampagnentyp-Mix

Spend-Verteilung über die channel_types (12 Monate):

| Typ | Spend | Anteil |
|---|---|---|
| SEARCH | … | … % |
| PERFORMANCE_MAX | … | … % |

Ein Satz: wo liegt das Budget strukturell.

## Search-Terms-Analyse

Top-Suchbegriffe nach Spend (12 Monate):

| Suchbegriff | Kampagne | Impr. | Klicks | Kosten | Conv. | Brand | Streuverlust |
|---|---|---|---|---|---|---|---|
| … | … | … | … | … | … | ja/nein | ja/nein |

**Brand vs. Non-Brand:**

- Brand-Anteil am Spend: <X%>
- Brand-Anteil an den Conversions: <X%>
- Non-Brand-Anteil am Spend: <Y%>

Ein bis zwei Sätze: erntet das Konto vor allem bestehende Brand-Nachfrage oder
erschließt es neue?

**Streuverlust:**

- Spend in streuverlust-geflaggten Suchbegriffen: <X EUR> (<X%> des Gesamt-Spends)
- Beispiel-Suchbegriffe: …

(Hinweis: Die `sea-suchbegriffe.csv` ist auch Roh-Keyword-Quelle für
`03-02-seo-keyword-recherche` und `03-03-seo-keyword-kategorisierung` — echte
Suchanfragen mit echten Conversion-Daten.)

## Quality-Score-Verteilung

Spend-gewichtete Verteilung über die Keywords (12 Monate):

| Bin | Spend-Anteil |
|---|---|
| schwach (QS 1-4) | <X%> |
| mittel (QS 5-7) | <X%> |
| stark (QS 8-10) | <X%> |

Schwächste Keywords nach Spend:

| Keyword | QS | Match-Type | Kampagne | Spend | CPC |
|---|---|---|---|---|---|
| … | … | … | … | … | … |

(Wenn QS für die Mehrheit der Keywords nicht vergeben ist: Hinweis statt Tabelle.)

## Conversion-Setup

Ergebnis des Plausibilitäts-Checks:

- **Urteil:** <sauber | mit Einschränkung | kein Tracking>
- **Conversion-Actions:** <N gesamt, M ENABLED>
- **Begründung:** <1-3 Sätze — gibt es ENABLED-Conversions, GA4-Import,
  Macro-/Micro-Mix?>

(Wenn eine offene Strategen-Frage besteht: hier wörtlich ausweisen, mit dem
Hinweis, dass die Outputs mit einer Default-Annahme geschrieben wurden.)

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach `relevanz: hoch` → `mittel` → `niedrig`)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: …

**Betroffen**: <kampagnen/suchbegriffe>

(weitere Auffälligkeiten …)

## Lücken und Hinweise

- Datenbasis dünn? (`daten_qualitaet: niedrig` → Warnung hier)
- Konto neu / wenig Historie? → Hinweis hier
- Conversion-Tracking fehlt → ROAS/CPA/CR nicht belastbar
- Offene Strategen-Frage aus dem Conversion-Check → hier wiederholen
- Konto in Konto-Währung ≠ EUR → Hinweis, dass Synthese-Skills umrechnen
```

## CSV-Schema (`audits/sea-kampagnen.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
campaign_id,campaign,status,channel_type,zeitraum,datum_von,datum_bis,cost,currency,impressions,clicks,ctr,avg_cpc,conversions,conversions_value,roas,cpa,cr
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `campaign_id` | string | ja | Kampagnen-ID aus der API |
| `campaign` | string | ja | Kampagnen-Name (unverändert) |
| `status` | string | ja | `ENABLED` / `PAUSED` / `REMOVED` |
| `channel_type` | string | ja | `SEARCH` / `DISPLAY` / `VIDEO` / `SHOPPING` / `DEMAND_GEN` / `PERFORMANCE_MAX` / ... |
| `zeitraum` | string | ja | `12m` (12-Monats-Range) oder `30d` (LAST_30_DAYS) |
| `datum_von` | ISO-8601 | ja | Periode-Start |
| `datum_bis` | ISO-8601 | ja | Periode-Ende |
| `cost` | float | ja | Spend in Konto-Währung (unverändert vom Wrapper) |
| `currency` | string | ja | Konto-Währung (`EUR`, `USD`, ...) |
| `impressions` | integer | ja | Impressionen in der Periode |
| `clicks` | integer | ja | Klicks in der Periode |
| `ctr` | float | ja | Click-Through-Rate als Dezimalwert 0..1 |
| `avg_cpc` | float | ja | Durchschnittlicher CPC in Konto-Währung |
| `conversions` | float | ja | Conversions in der Periode (kann gebrochen sein) |
| `conversions_value` | float | ja | Conversion-Wert in Konto-Währung |
| `roas` | float oder leer | nein | `conversions_value / cost`; leer wenn `cost = 0` |
| `cpa` | float oder leer | nein | `cost / conversions`; leer wenn `conversions = 0` |
| `cr` | float oder leer | nein | `conversions / clicks`; leer wenn `clicks = 0` |

### Sortierung

1. `zeitraum` (`12m` zuerst, dann `30d`)
2. `cost` absteigend
3. `campaign` alphabetisch (Tiebreaker)

### Beispiel

```csv
campaign_id,campaign,status,channel_type,zeitraum,datum_von,datum_bis,cost,currency,impressions,clicks,ctr,avg_cpc,conversions,conversions_value,roas,cpa,cr
987654321,Search - Brand DE,ENABLED,SEARCH,12m,2025-05-17,2026-05-17,12400.30,EUR,210400,9800,0.0466,1.27,240.0,96200.0,7.76,51.67,0.0245
987654322,Search - Generic Produkte,ENABLED,SEARCH,12m,2025-05-17,2026-05-17,21800.10,EUR,980200,22400,0.0229,0.97,310.0,68400.0,3.14,70.32,0.0138
987654321,Search - Brand DE,ENABLED,SEARCH,30d,2026-04-17,2026-05-17,1010.40,EUR,17800,840,0.0472,1.20,21.0,8200.0,8.12,48.11,0.0250
```

## CSV-Schema (`audits/sea-suchbegriffe.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt. Eine Zeile je Suchbegriff (12-Monats-Range).

**Diese CSV ist die Übergabe-Schnittstelle an die SEO-Keyword-Skills.** `03-02-seo-keyword-recherche` liest sie als Seed-Pool mit echten Conversion-Daten, `03-03-seo-keyword-kategorisierung` als zusätzliche Keyword-Quelle. Header und Semantik nicht ohne Versions-Bump ändern.

### Spalten

```
search_term,status,campaign,impressions,clicks,ctr,cost,currency,conversions,ist_brand,streuverlust_flag
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `search_term` | string | ja | Echte Suchanfrage (unverändert) |
| `status` | string | ja | `ADDED` / `EXCLUDED` / `ADDED_EXCLUDED` / `NONE` / `UNKNOWN` |
| `campaign` | string | ja | Kampagne, in der der Suchbegriff aufgetreten ist |
| `impressions` | integer | ja | Impressionen 12 Monate |
| `clicks` | integer | ja | Klicks 12 Monate |
| `ctr` | float | ja | CTR als Dezimalwert 0..1 |
| `cost` | float | ja | Kosten in Konto-Währung (unverändert vom Wrapper) |
| `currency` | string | ja | Konto-Währung |
| `conversions` | float | ja | Conversions 12 Monate (kann gebrochen sein) |
| `ist_brand` | boolean | ja | `true` wenn Brand-Term (Token-Match gegen Kundennamen — Methodik-Datei) |
| `streuverlust_flag` | boolean | ja | `true` wenn streuverlust-Kandidat (Heuristik — Methodik-Datei) |

### Sortierung

Nach `cost` absteigend, dann `impressions` absteigend (Tiebreaker).

### Beispiel

```csv
search_term,status,campaign,impressions,clicks,ctr,cost,currency,conversions,ist_brand,streuverlust_flag
mustermann gmbh,ADDED,Search - Brand DE,18200,3100,0.1703,310.20,EUR,84.0,true,false
kabel messer kaufen,ADDED,Search - Generic Produkte,4800,142,0.0296,168.40,EUR,11.0,false,false
messer kostenlos,NONE,Search - Generic Produkte,2200,38,0.0173,52.80,EUR,0.0,false,true
```

### Größen-Grenze

- Default `--limit 300`, bei großen Konten bis 1.000. CSV bei sehr großen Konten auf Top-1.000 nach Impressionen kappen, Hinweis im Body.

## Wie Folge-Skills die Outputs lesen

### `03-02-seo-keyword-recherche`

Liest **primär** `sea-suchbegriffe.csv` als Seed-Keyword-Set: das sind echte Suchanfragen, für die der Kunde Geld ausgegeben hat — und mit `conversions` ein echtes Konversions-Signal. Keywords mit `conversions > 0` sind die stärksten SEO-Kandidaten. `streuverlust_flag = true` markiert Keywords, die als SEO-Ziel auch eher ungeeignet sind.

### `03-03-seo-keyword-kategorisierung`

Bekommt aus `sea-suchbegriffe.csv` zusätzliche Keywords mit `ist_brand`-Vorklassifikation. Die Funnel-/Intent-/Cluster-Kategorisierung kommt separat dazu (Schema-vor-Lauf).

### `04-02-kanal-chancen-analyse`

Liest aus `sea-first-party.md` Frontmatter:

- `statistiken_12_monate.roas` und `.cost` → Hebel-Score und Wirtschaftlichkeit für den Paid-Search-Kanal
- `conversion_setup_urteil` → Daten-Vertrauens-Faktor (bei `kein_tracking` ist die SEA-Performance-Aussage entwertet)
- `auffaelligkeiten` mit hoher Relevanz → strategische Story-Bausteine

### `04-04-forecast-modell`

Liest aus `sea-first-party.md` Frontmatter und aus `sea-kampagnen.csv`:

- echte CR-, CPC- und ROAS-Werte je Kampagne → ersetzen die Branchen-Annahmen für den SEA-Kanal im Forecast-Schema
- `kampagnentyp_mix` → Ramp-up-Annahmen je channel_type

### `03-18-web-analytics-ga4`

Liest die `conversion-actions`-Roh-Daten aus `audits/raw/sea-conversion-actions.json` für den GA4-vs-Ads-Conversion-Cross-Check (welche Conversions sind aus GA4 importiert, droht Doppelzählung).

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. `quelle.customer_id` ist eine 10-stellige Ziffernfolge
2. `statistiken_12_monate.cost` ≥ 0 (Plausibilitäts-Check)
3. Wenn `cost = 0` über 12 Monate → `daten_qualitaet: keine`, minimale Outputs mit Hinweis "Konto inaktiv"
4. `roas`/`cpa`/`cr` sind leer (nicht 0) bei Division durch 0 — niemals als 0 ausweisen
5. `conversion_setup_urteil` ist einer von `{sauber, mit_einschraenkung, kein_tracking}`
6. CSV: jede Zeile hat alle Pflicht-Spalten gefüllt
7. CSV `sea-kampagnen.csv`: `channel_type`, `status`, `zeitraum` sind gültige Werte
8. CSV `sea-suchbegriffe.csv`: `ist_brand` und `streuverlust_flag` sind `true`/`false`
9. `kampagnentyp_mix`-Spend-Anteile summieren sich (mit Rundungs-Toleranz) auf 1,0
10. Jede `auffaelligkeit` hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`
11. Wenn `conversion_setup_urteil: kein_tracking` → ROAS/CPA/CR im Body explizit als "nicht belastbar" markiert
12. `currency` ist in jeder CSV-Zeile und im Frontmatter konsistent

Wenn eine Regel verletzt wird: konkrete Fehlermeldung im Skill-Schluss-Format, welcher Eintrag korrigiert werden muss.
