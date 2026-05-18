# Keyword-Pool-Output-Schema

Definiert die Output-Formate des Skills für die beiden Pflicht-Dateien:

- `audits/seo-keyword-pool.csv` — der vollständige Keyword-Pool als CSV (für Folge-Skill `03-03-seo-keyword-kategorisierung`)
- `audits/seo-keyword-pool.md` — Stratege-Aggregat (Top-Gaps, Auffälligkeiten, Difficulty-Verteilung)

Beide Dateien sind verbindlich für die Folge-Skills.

## CSV-Schema (`audits/seo-keyword-pool.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
keyword,keyword_normalisiert,sistrix_volumen,ahrefs_volumen,volumen_diskrepanz,difficulty,ahrefs_cpc,ahrefs_parent_topic,ahrefs_is_branded,ahrefs_is_transactional,ahrefs_is_commercial,ahrefs_is_informational,quellen,seed_keyword,intent_hypothese,intent_quelle,keyword_geo_typ,gap_zu_kunde,gap_typ,gap_score,branchen_basis_luecke,ranking_kunde_position,ranking_kunde_url,ranking_top_wb_slug,ranking_top_wb_position,ranking_top_wb_url,branded_filter_grund,branded_unscharf,aggregator_filter_grund,lookup_fehlgeschlagen,datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `keyword` | string | ja | ursprünglicher Keyword-Text (Schreibweise wie geliefert) |
| `keyword_normalisiert` | string | ja | lowercase, getrimmt, Mehrfach-Whitespace zusammengezogen |
| `sistrix_volumen` | integer oder leer | nein | Sistrix-Suchvolumen — leer wenn `sistrix_modus: aus` oder Keyword nicht in Sistrix |
| `ahrefs_volumen` | integer oder leer | nein | Ahrefs-Suchvolumen (aus `keywords-explorer-overview.volume`) — gefüllt für alle Keywords aus Schritt 8 |
| `volumen_diskrepanz` | true / false / leer | nein | true, wenn Sistrix und Ahrefs >50% abweichen. Leer, wenn nicht beide Volumen vorhanden. |
| `difficulty` | integer 0-100 oder leer | nein | Ahrefs Keyword-Difficulty (aus `keyword_difficulty`) — gefüllt für alle Keywords aus Schritt 8 |
| `ahrefs_cpc` | float oder leer | nein | durchschnittlicher CPC laut Ahrefs |
| `ahrefs_parent_topic` | string oder leer | nein | Ahrefs-Parent-Topic-Cluster (aus `parent_keyword`) — jetzt vollflächig für alle Ahrefs-angereicherten Keywords gefüllt. Wichtiger Input für `03-03-seo-keyword-kategorisierung`. |
| `ahrefs_is_branded` | true / false / leer | nein | Ahrefs-Flag, **Primary für Intent-Klassifikation** |
| `ahrefs_is_transactional` | true / false / leer | nein | Ahrefs-Flag |
| `ahrefs_is_commercial` | true / false / leer | nein | Ahrefs-Flag |
| `ahrefs_is_informational` | true / false / leer | nein | Ahrefs-Flag |
| `quellen` | string | ja | Pipe-getrennte Liste: `sistrix_csv | sistrix_longtail | sistrix_suggestions | branchen_seed | ahrefs_matching | ahrefs_related | ahrefs_suggestions | ahrefs_overview` |
| `seed_keyword` | string oder leer | nein | bei Long-Tail-Variationen: aus welchem Seed-Keyword expandiert |
| `intent_hypothese` | enum | ja | `branded | transactional | commercial | informational | navigational | unklar` |
| `intent_quelle` | enum | ja | **`ahrefs_flags`** (primary, aus Ahrefs `is_*`-Flags) oder **`heuristik`** (fallback, wenn Ahrefs-Daten fehlen) oder **`manuelle_kuration`** (reserviert für Folge-Skill `03-03-seo-keyword-kategorisierung`) |
| `keyword_geo_typ` | enum | ja | `lokal` (Keyword löst Local Pack aus oder enthält Orts-Zusatz), `ueberregional` (kein Local Pack, rein organisch), `unklar` (kein SERP-Check durchgeführt oder Datenlage eindeutig) |
| `gap_zu_kunde` | true / false | ja | hat der Kunde eine starke Position (≤ 30) auf diesem Keyword? false = Gap |
| `gap_typ` | enum oder leer | nein | `hart` (Kunde nicht in Top-100), `weich` (Kunde > 30, WB ≤ 10), leer wenn kein Gap |
| `gap_score` | float oder leer | nein | Score-Wert für Gap-Priorisierung — Berechnung siehe `wettbewerbs-gap-logik.md` |
| `branchen_basis_luecke` | true / false | ja | Branchen-Seed-Keyword, das der Kunde nicht abdeckt |
| `ranking_kunde_position` | integer oder leer | nein | Position des Kunden für dieses Keyword (aus Basis-CSV) |
| `ranking_kunde_url` | URL oder leer | nein | URL des Kunden für dieses Keyword |
| `ranking_top_wb_slug` | string oder leer | nein | Slug des am besten rankenden WBs |
| `ranking_top_wb_position` | integer oder leer | nein | Position des Top-WBs |
| `ranking_top_wb_url` | URL oder leer | nein | URL des Top-WBs |
| `branded_filter_grund` | string oder leer | nein | wenn das Keyword durch den Branded-Filter ausgeschlossen wurde: welche Marke wurde erkannt. Quelle kann Token-Match oder Ahrefs `is_branded` sein — Quelle im Wert mit notieren (z. B. `"alpha-tech (ahrefs)"`). |
| `branded_unscharf` | true / false / leer | nein | true, wenn Heuristik branded sagt aber Ahrefs `is_branded: false` (oder umgekehrt). Hinweis für Strategen-Kuration. |
| `aggregator_filter_grund` | string oder leer | nein | wenn das Keyword durch den Aggregator-Filter ausgeschlossen wurde: welcher Aggregator |
| `lookup_fehlgeschlagen` | true / false | ja | true, wenn beim Lookup ein Fehler auftrat (z. B. Ahrefs-Rate-Limit) |
| `datenstand_iso` | ISO-8601 | ja | Datenstand für diese Zeile |

### Sortierung

1. `gap_zu_kunde` (true zuerst — Gaps sind wertvollstes Material)
2. `gap_score` absteigend (höchstes Score zuerst, leer am Ende)
3. `ahrefs_volumen` absteigend (Primary), bei Gleichstand `sistrix_volumen` absteigend
4. `keyword_normalisiert` (alphabetisch zur Stabilität bei Re-Runs)

### Größen-Grenze

Soft-Cap: 1500 Keywords pro Pool. Hard-Cap: 3000. Bei sehr großen Pools im Aggregat-Markdown auf Top-200 begrenzt rendern.

### Volumen-Diskrepanz-Logik

- Wenn `sistrix_modus: aus` → `volumen_diskrepanz` bleibt leer, weil kein Vergleichswert vorliegt
- Wenn beide Werte vorhanden:
  - `abweichung = abs(sistrix_volumen - ahrefs_volumen) / max(sistrix_volumen, ahrefs_volumen)`
  - `volumen_diskrepanz: true` wenn `abweichung > 0.5`
- Beide Spalten bleiben unverändert erhalten — keine Spalte wird priorisiert, beide Werte sind Primärquellen ihres Tools

### Intent-Quelle-Logik

Pro Keyword genau ein `intent_quelle`-Wert:

- `ahrefs_flags`: für alle Keywords, die in Schritt 8 mit Ahrefs angereichert wurden und mindestens ein `is_*`-Flag auf `true` hatten
- `heuristik`: für Keywords ohne Ahrefs-Match (Cap überschritten, 404, Ahrefs liefert alle Flags `false` führt zu `unklar` mit `intent_quelle: heuristik` als Fallback-Lauf)
- `manuelle_kuration`: wird von diesem Skill nie geschrieben; reserviert für `03-03-seo-keyword-kategorisierung`

## Markdown-Schema (`audits/seo-keyword-pool.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-02-seo-keyword-recherche
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  basis_csv: audits/seo-keywords.csv
  sichtbarkeit_md: audits/seo-sichtbarkeit.md
  identifikation_schema: wettbewerber/identifikation-schema.md   # null wenn nicht vorhanden
  briefing: data/briefing.md   # null wenn nicht vorhanden
  kunde_md: data/kunde.md   # null wenn nicht vorhanden

quellen_genutzt:
  - sistrix_csv
  - ahrefs_matching
  - ahrefs_related
  - ahrefs_suggestions
  - ahrefs_overview
  - sistrix_longtail   # null wenn sistrix_modus: aus
  - branchen_seed

# Ahrefs ist Primary — Skill bricht ab, wenn ahrefs_modus nicht "voll"
ahrefs_modus: voll | partiell   # "partiell" wenn Rate-Limit mitten im Lauf — keine "aus"-Option mehr
sistrix_modus: voll | partiell | aus

# === Aggregat-Statistik ===
statistiken:
  pool_keywords_gesamt: <int>
  pro_quelle:
    sistrix_csv: <int>
    ahrefs_matching: <int>
    ahrefs_related: <int>
    ahrefs_suggestions: <int>
    sistrix_longtail: <int>
    branchen_seed: <int>
  intent_verteilung:
    branded: <int>
    transactional: <int>
    commercial: <int>
    informational: <int>
    navigational: <int>
    unklar: <int>
  intent_quelle_verteilung:
    ahrefs_flags: <int>
    heuristik: <int>
    manuelle_kuration: 0   # in diesem Skill immer 0
  gap_zu_kunde_total: <int>
  gap_hart: <int>
  gap_weich: <int>
  sweet_spot_gaps: <int>   # gap + difficulty <= 30 + volumen >= 300
  branchen_basis_luecken: <int>
  ahrefs_angereichert: <int>   # zuvor: difficulty_angereichert — umbenannt, weil jetzt mehr als Difficulty
  volumen_diskrepanz_count: <int>
  intent_hypothese_korrigiert_count: <int>   # NEU
  top_parent_topics:
    - topic: <string>
      anzahl: <int>
    # Top 10

difficulty_histogramm:
  - bucket: "0-10"
    count: <int>
  # ... 10er-Buckets bis 90-100

# === Top-50-Gap-Keywords ===
top_gap_keywords:
  - keyword: <string>
    sistrix_volumen: <int oder null>
    ahrefs_volumen: <int oder null>
    difficulty: <int oder null>
    gap_typ: <hart | weich>
    gap_score: <float>
    top_wb_slug: <string>
    top_wb_position: <int>
    intent_hypothese: <enum>
    intent_quelle: <enum>
    parent_topic: <string oder null>

# === Long-Tail-Cluster (Token-basiert) ===
longtail_cluster:
  - seed_keyword: <string>
    anzahl_variationen: <int>
    kumuliertes_volumen: <int>
    quellen_mix: { ahrefs_matching: <int>, ahrefs_related: <int>, sistrix_longtail: <int> }
    beispiel_variationen: [<liste 3-5 Beispiele>]

# === Parent-Topic-Cluster (NEU, Ahrefs-basiert) ===
parent_topic_cluster:
  - parent_topic: <string>
    anzahl_keywords: <int>
    kumuliertes_volumen: <int>
    durchschnitts_difficulty: <int>
    beispiel_keywords: [<liste>]

# === Branchen-Seed-Status ===
branchen_seed_status:
  - seed: <keyword aus identifikation-schema>
    im_pool: <true | false>
    kunde_position: <int oder null>
    kunde_status: <abgedeckt_top10 | abgedeckt_top30 | luecke_top100 | gar_nicht>
    top_wb_position: <int oder null>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <enum aus den 11 Typen in SKILL.md Schritt 10>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion>
    betroffene_keywords: [<liste der Keywords>]
---

# SEO-Keyword-Pool und Wettbewerbs-Gaps: <Kundenname>

## Übersicht

3-5 Sätze: wie groß ist der Pool, was war die Hauptquelle (Ahrefs primär plus ggf. Sistrix-DACH-Ergänzung), was sind die Top-1-2-Auffälligkeiten.

## Wettbewerbs-Gaps (Top 30)

Tabelle:

| Rang | Keyword | Ahrefs-Vol | Sistrix-Vol | Difficulty | Gap-Typ | Top-WB | WB-Position | Intent | Intent-Quelle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | … | 3.600 | 4.200 | 24 | hart | beta-solutions | 2 | commercial | ahrefs_flags |
| … | … | … | … | … | … | … | … | … | … |

> Hinweis: weitere Gaps in `audits/seo-keyword-pool.csv` (Sortierung nach Gap-Score)

## Long-Tail-Expansion

Pro Seed-Keyword: Anzahl Variationen + kumuliertes Volumen + Quellen-Mix.

| Seed-Keyword | # Variationen | Ahrefs-Anteil | Sistrix-Anteil | Kumuliertes Volumen | Beispiele |
|---|---|---|---|---|---|
| kabel verlängerung | 22 | 17 | 5 | 8.400 | "kabel verlängerung außen", "kabel verlängerung 10m", … |
| … | … | … | … | … | … |

## Parent-Topic-Cluster (Ahrefs)

Top 10 Parent-Topics nach Pool-Abdeckung — wird in `03-03-seo-keyword-kategorisierung` als Cluster-Vorlage genutzt.

| Parent-Topic | # Keywords | Kumuliertes Volumen | Ø Difficulty | Beispiel-Keywords |
|---|---|---|---|---|
| aufmaß | 142 | 23.400 | 28 | "aufmaß werkzeug", "aufmaß app", … |
| … | … | … | … | … |

## Branchen-Seed-Status

Aus dem `identifikation-schema` — wie deckt der Kunde die Branchen-Basis ab?

| Seed-Keyword | Im Pool | Kunden-Position | Kunden-Status | Top-WB-Position |
|---|---|---|---|---|
| aufmaß werkzeug | ja | 5 | abgedeckt_top10 | 3 (beta-solutions) |
| handwerker-app | ja | nicht_im_top100 | luecke_top100 | 2 (alpha-tech) |
| … | … | … | … | … |

## Difficulty-Verteilung (Ahrefs)

ASCII-Histogramm oder Text-Tabelle für 10er-Buckets, mit Hinweis "X% des Pools liegt unter Difficulty 30 (Sweet-Spot-Zone)".

Beispiel:

```
 0-10  ▓▓▓▓▓▓ 32
10-20  ▓▓▓▓▓▓▓▓▓ 48
20-30  ▓▓▓▓▓▓▓▓ 41
30-40  ▓▓▓▓▓ 27
40-50  ▓▓▓ 18
50-60  ▓▓ 11
60-70  ▓ 6
70-80   3
80-90   1
90-100  0
```

## Intent-Hypothesen-Verteilung

| Intent | Anzahl | Anteil | aus Ahrefs-Flags | aus Heuristik |
|---|---|---|---|---|
| informational | 78 | 42% | 64 | 14 |
| commercial | 56 | 30% | 48 | 8 |
| transactional | 33 | 18% | 28 | 5 |
| branded | 14 | 7% | 14 | 0 |
| unklar | 5 | 3% | 2 | 3 |

> Hinweis: Ahrefs-Flags sind Primary-Quelle. Heuristik kommt nur zum Einsatz, wenn das Anreicherungs-Cap überschritten ist oder Ahrefs das Keyword nicht kennt. Die finale Kategorisierung erfolgt in `03-03-seo-keyword-kategorisierung`.

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach `relevanz: hoch` → `mittel` → `niedrig`)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: …

**Betroffene Keywords (Auswahl):** …

(weitere Auffälligkeiten …)

## Vorbereitung für `03-03-seo-keyword-kategorisierung`

Aus den Ahrefs-Parent-Topics und der Intent-Verteilung zeichnen sich folgende Cluster ab:

- **Branded-Cluster**: ca. 14 Keywords um Marken-Synonyme — sollte in `03-03-seo-keyword-kategorisierung` als eigener Cluster behandelt werden
- **Parent-Topic "Aufmaß"**: 142 Keywords (≈ 34% des Pools), davon 8 Gaps — strategischer Haupt-Cluster
- (weitere …)

→ Diese Hinweise werden in das Schema von `03-03-seo-keyword-kategorisierung` einfließen, das vor der eigentlichen Cluster-Bildung vom Strategen reviewt wird.

## Lücken und Hinweise

- Wenn Sistrix nicht verfügbar (`sistrix_modus: aus`): keine DACH-Long-Tail-Ergänzung, keine Volumen-Cross-Validierung
- Wenn Ahrefs `partiell` (Rate-Limit): X Keywords ohne Anreicherung
- Wenn Branchen-Seeds übersprungen: warum
- Wenn Volumen-Diskrepanz systematisch: methodischer Hinweis für Strategen
- Wenn Intent-Hypothese häufig korrigiert: Hinweis, dass die Heuristik allein nicht zuverlässig wäre
```

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jede Zeile in der CSV hat `keyword`, `keyword_normalisiert`, `quellen`, `intent_hypothese`, `intent_quelle`, `keyword_geo_typ`, `gap_zu_kunde`, `datenstand_iso`
2. `gap_zu_kunde: true` → `gap_typ` muss `hart` oder `weich` sein
3. `gap_zu_kunde: false` → `gap_typ` muss leer sein
4. `seed_keyword` darf nur gefüllt sein, wenn `quellen` ein `*_longtail`-, `*_suggestions`-, `ahrefs_matching`- oder `ahrefs_related`-Element enthält
5. `volumen_diskrepanz: true` → beide Volumen-Spalten müssen gefüllt sein
6. `difficulty` nur gefüllt, wenn Ahrefs-Modus `voll` oder `partiell` und Lookup für dieses Keyword nicht fehlgeschlagen
7. `intent_quelle: ahrefs_flags` → mindestens eines der `ahrefs_is_*`-Flags muss in der Zeile gesetzt (true oder false, nicht leer) sein
8. `intent_quelle: heuristik` → Keyword darf keine Ahrefs-Anreicherung haben (alle `ahrefs_is_*` leer) oder Anreicherung lieferte alle Flags `false` (Sonderfall: Heuristik-Fallback bei `unklar`)
9. Markdown-`statistiken.pool_keywords_gesamt` = Anzahl Zeilen in CSV
10. `branchen_seed_status` enthält jeden Seed aus `identifikation-schema.md` (falls vorhanden) — auch wenn der Seed nicht im Pool ist
11. `ahrefs_modus` darf nicht `aus` sein (Ahrefs ist Pflicht; wenn nicht verfügbar, ist der Skill schon in Schritt 1 abgebrochen)

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf)

Liest:

- **Primär** `audits/seo-keyword-pool.csv` (Roh-Daten, jetzt mit `ahrefs_parent_topic` und Ahrefs-Intent-Flags)
- Sekundär `audits/seo-keyword-pool.md` Frontmatter (`parent_topic_cluster`, `intent_verteilung`, `top_parent_topics`)

Generiert in Phase A ein Schema: welche Funnel-Cluster, welche Intent-Typen, Branchenkontext. **Die Ahrefs-Parent-Topics werden als Cluster-Vorlage genutzt** — der Stratege bestätigt, passt an, ergänzt. In Phase B kategorisiert er den Pool entlang des bestätigten Schemas und setzt dort `intent_quelle: manuelle_kuration`.

### `03-15-web-content-inventur` (Schema-vor-Lauf)

Kann optional `seo-keyword-pool.csv` lesen, um die wichtigsten Themen-Cluster vorab zu sehen — hilft bei der Crawl-Tiefen-Entscheidung pro Akteur.

### `04-02-kanal-chancen-analyse`

Liest `seo-keyword-pool.md` Frontmatter:

- `statistiken.sweet_spot_gaps` → "wie viele schnelle SEO-Wins"
- `statistiken.gap_zu_kunde_total` → "wie viel SEO-Potenzial insgesamt"
- `statistiken.top_parent_topics` → strategische Themen-Schwerpunkte
- `auffaelligkeiten` mit `typ: top_gap_hochvolumig`, `wb_dominanz_in_thema`, `parent_topic_dominanz` → strategische Argumente
