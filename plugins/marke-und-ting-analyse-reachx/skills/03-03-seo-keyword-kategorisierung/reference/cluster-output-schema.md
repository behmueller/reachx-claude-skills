# Output-Schema für Phase B

Definiert die Outputs nach erfolgreicher Phase-B-Ausführung:

- `audits/seo-keyword-cluster.csv` — vollständig kategorisierter Keyword-Pool (für Synthese-Skills)
- `audits/seo-cluster-zusammenfassung.md` — Aggregat pro Cluster für den Strategen

## CSV-Schema (`audits/seo-keyword-cluster.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Pipe.

### Spalten (in fester Reihenfolge)

```
keyword,keyword_normalisiert,sistrix_volumen,ahrefs_volumen,difficulty,ahrefs_cpc,
primaer_cluster,sekundaer_cluster,cluster_typ,intent_typ,funnel_stufe,
kategorisierung_quelle,kategorisierungs_konfidenz,
gap_zu_kunde,gap_typ,gap_score,
ranking_kunde_position,ranking_kunde_url,ranking_top_wb_slug,ranking_top_wb_position,
quellen_pool,seed_keyword,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `keyword` | string | ja | aus Pool-CSV übernommen |
| `keyword_normalisiert` | string | ja | aus Pool-CSV übernommen |
| `sistrix_volumen` | int / leer | nein | aus Pool-CSV |
| `ahrefs_volumen` | int / leer | nein | aus Pool-CSV |
| `difficulty` | int / leer | nein | aus Pool-CSV |
| `ahrefs_cpc` | float / leer | nein | aus Pool-CSV |
| `primaer_cluster` | string | ja | Pflicht-Zuordnung — Cluster-Name aus Schema |
| `sekundaer_cluster` | string / leer | nein | Pipe-getrennte Liste weiterer Cluster |
| `cluster_typ` | enum | ja | `branded | produkt | anwendung | gap_cluster | longtail | generic | fallback` |
| `intent_typ` | enum | ja | `branded | transactional | commercial | informational | navigational | unklar` |
| `funnel_stufe` | enum | ja | `TOFU | MOFU | BOFU` |
| `kategorisierung_quelle` | enum | ja | `branded_match | anker_token_match | ahrefs_parent_topic | manual_override | fallback_generic` |
| `kategorisierungs_konfidenz` | enum | ja | `hoch | mittel | niedrig` |
| `gap_zu_kunde` | bool | ja | aus Pool-CSV |
| `gap_typ` | enum / leer | nein | aus Pool-CSV |
| `gap_score` | float / leer | nein | aus Pool-CSV |
| `ranking_kunde_position` | int / leer | nein | aus Pool-CSV |
| `ranking_kunde_url` | URL / leer | nein | aus Pool-CSV |
| `ranking_top_wb_slug` | string / leer | nein | aus Pool-CSV |
| `ranking_top_wb_position` | int / leer | nein | aus Pool-CSV |
| `quellen_pool` | string | ja | aus Pool-CSV (Pipe-Liste der Quellen) |
| `seed_keyword` | string / leer | nein | aus Pool-CSV |
| `datenstand_iso` | ISO-8601 | ja | Datenstand der Kategorisierung (= Phase-B-Lauf) |

### Sortierung

1. `primaer_cluster` (alphabetisch, oder nach Cluster-Score-Reihenfolge wenn Score-Sortierung im Schema gesetzt)
2. Innerhalb des Clusters: `gap_zu_kunde` true zuerst
3. Dann `gap_score` absteigend, leere ans Ende
4. Dann `sistrix_volumen` absteigend
5. Dann `keyword_normalisiert` alphabetisch (Tiebreaker für Reproduzierbarkeit)

### Größen-Grenze

Soft-Cap: 1500 Keywords (wie Pool-CSV). Hard-Cap: 3000.

## Markdown-Schema (`audits/seo-cluster-zusammenfassung.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-03-seo-keyword-kategorisierung
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  pool_csv: audits/seo-keyword-pool.csv
  pool_md: audits/seo-keyword-pool.md
  schema: audits/keyword-kategorisierung-schema.md
  schema_bestaetigt_am: <ISO-8601 aus Schema-Frontmatter>

# === Aggregat-Statistik ===
statistiken:
  pool_keywords_gesamt: <int>
  cluster_anzahl: <int>
  durchschnittliche_cluster_groesse: <float>
  groesster_cluster:
    name: <string>
    groesse: <int>
  kleinster_cluster:
    name: <string>
    groesse: <int>
  
  intent_verteilung:
    branded: <int>
    transactional: <int>
    commercial: <int>
    informational: <int>
    navigational: <int>
    unklar: <int>
  
  funnel_verteilung:
    TOFU: <int>
    MOFU: <int>
    BOFU: <int>
  
  konfidenz_verteilung:
    hoch: <int>
    mittel: <int>
    niedrig: <int>
  
  cluster_typen_verteilung:
    branded: <int>
    produkt: <int>
    anwendung: <int>
    gap_cluster: <int>
    longtail: <int>
    generic: <int>

# === Cluster-Aggregat ===
cluster_aggregat:
  - name: <cluster-name>
    typ: <cluster-typ>
    beschreibung: <aus schema>
    anzahl_keywords: <int>
    kumuliertes_volumen: <int>
    median_difficulty: <int oder null>
    durchschnitts_position_kunde: <float oder null>
    kunden_abdeckung_top10_prozent: <float 0..100>
    cluster_score: <float>
    intent_dominanz: <intent_typ mit höchstem Anteil im Cluster>
    funnel_dominanz: <funnel-stufe mit höchstem Anteil>
    top_3_keywords:
      - keyword: <string>
        volumen: <int>
        position_kunde: <int oder null>
      - ...
    handlungs_empfehlung: <1-2 Sätze, strategie-relevant>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <enum: kunde_gap_cluster | kunde_dominant_cluster | sweet_spot_cluster | cluster_dominiert_von_wb | cluster_zu_klein | bofu_unterversorgt | kategorisierung_unsicher | pool_schlecht_clusterbar>
    titel: <string>
    beschreibung: <1-2 Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion>
    betroffene_cluster: [<liste>]
    betroffene_keywords: [<liste — bei größeren Auffälligkeiten Auswahl der Top-10>]
---

# SEO-Keyword-Cluster-Zusammenfassung: <Kundenname>

## Übersicht

3-5 Sätze: Pool-Größe, Anzahl Cluster, Top-Cluster nach Score, Funnel-Verteilung im groben, Top-2-Auffälligkeiten.

## Top-Cluster-Tabelle (nach Score)

| Rang | Cluster | Typ | # KWs | Volumen | Median-Diff. | Kunden-Abd. | Score | Empfehlung |
|---|---|---|---|---|---|---|---|---|
| 1 | aufmass_workflow | anwendung | 23 | 11.400 | 28 | 8% | 18.2 | Sweet-Spot-Gap, Content-Hub |
| 2 | branded_kunde | branded | 14 | 4.800 | 14 | 95% | 12.7 | Brand-Position halten |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

> Hinweis: vollständige Cluster-Liste in `audits/seo-keyword-cluster.csv`.

## Pro Cluster

### 1. <cluster-name> · Score X,X

**Typ**: anwendung · **Größe**: 23 Keywords · **Kumuliertes Volumen**: 11.400 · **Median-Difficulty**: 28

**Anker-Tokens (aus Schema)**: aufmaß, vermessen, ausmessen

**Top-Keywords**:

| Keyword | Volumen | Difficulty | Kunden-Pos. | Top-WB | WB-Pos. |
|---|---|---|---|---|---|
| aufmaß werkzeug | 1.900 | 24 | nicht im Top-100 | beta-solutions | 2 |
| ... | ... | ... | ... | ... | ... |

**Intent-Verteilung im Cluster**: 60% informational, 25% commercial, 15% transactional

**Funnel-Verteilung im Cluster**: 55% TOFU, 30% MOFU, 15% BOFU

**Kunden-Status**: Sehr schwache Abdeckung (8% Top-10) — Wettbewerber `beta-solutions` dominiert mit 9 Top-10-Positionen.

**Handlungs-Empfehlung**: Klarer Content-Hub-Kandidat. Sweet-Spot wegen niedriger Median-Difficulty — schnelle SEO-Wins möglich, wenn ein dedizierter Themen-Bereich aufgebaut wird.

(... weitere Cluster, max 12-15 sichtbar — Rest als CSV-Verweis ...)

## Intent-Verteilung pool-weit

| Intent | Anzahl | Anteil |
|---|---|---|
| informational | 145 | 42% |
| commercial | 102 | 30% |
| transactional | 58 | 17% |
| branded | 28 | 8% |
| navigational | 8 | 2% |
| unklar | 4 | 1% |

## Funnel-Verteilung pool-weit

| Funnel | Anzahl | Anteil |
|---|---|---|
| TOFU | 168 | 49% |
| MOFU | 112 | 32% |
| BOFU | 65 | 19% |

Vergleich zum branchen-typischen Erwartungswert (laut Schema-Branchen-Typ): leicht TOFU-lastiger als erwartet → möglicher Hinweis, dass Content-Strategie überwiegt, aber Conversion-Keywords ggf. fehlen.

## Konfidenz-Verteilung

| Konfidenz | Anzahl | Anteil |
|---|---|---|
| hoch | 248 | 72% |
| mittel | 78 | 23% |
| niedrig | 19 | 5% |

> Wenn `niedrig`-Anteil über 20%: Schema sollte überarbeitet werden.

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: ...

**Betroffene Cluster**: ...

(weitere Auffälligkeiten ...)

## Vorbereitung für Folge-Skills

Aus den Cluster-Aggregaten ergeben sich klare Argumente für:

- **`04-02-kanal-chancen-analyse`**: Top-Score-Cluster sind die SEO-Channel-Argumente. BOFU-Anteil unter 20% → Hinweis, dass Ads-Channel ergänzt werden sollte.
- **`04-04-forecast-modell`**: Cluster-Score-Top-10 als Forecast-Treiber. Annahme-Range pro Cluster sollte in das Forecast-Schema einfließen.
- **`04-05-90-tage-plan`**: Sweet-Spot-Cluster werden zu prioritären 90-Tage-Maßnahmen (Content-Briefings, Landingpage-Aufbau).

## Lücken und Hinweise

- Wenn `generic`-Cluster groß (>15% des Pools): Schema-Verfeinerung empfehlen
- Wenn `unklar`-Intent größer als 5%: Heuristik-Anpassung empfehlen
- Wenn Funnel-Verteilung stark von Erwartungswert abweicht: methodischen Hinweis für Strategen
```

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jede Zeile in der CSV hat alle Pflicht-Spalten gefüllt
2. `primaer_cluster` existiert in der Schema-Cluster-Liste
3. `sekundaer_cluster` (wenn gefüllt): alle Cluster existieren im Schema
4. `cluster_typ` matched mit dem `typ`-Feld des `primaer_cluster` im Schema
5. `intent_typ` ist einer der 6 erlaubten Werte
6. `funnel_stufe` ist einer der 3 erlaubten Werte
7. `kategorisierungs_konfidenz` passt zur `kategorisierung_quelle`:
   - `quelle: branded_match` → `konfidenz: hoch`
   - `quelle: fallback_generic` → `konfidenz: niedrig`
   - sonst: konsistente Logik aus dem Skill
8. Markdown-`statistiken.pool_keywords_gesamt` = Anzahl Zeilen in CSV
9. Markdown-`cluster_aggregat` enthält jeden Cluster aus dem Schema (auch leere Cluster werden gelistet, mit Hinweis im Body)
10. Jeder Cluster im Aggregat hat einen `cluster_score` als float

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `04-02-kanal-chancen-analyse`

**Primär** aus `seo-cluster-zusammenfassung.md` Frontmatter:

- `cluster_aggregat` → Top-Score-Cluster als SEO-Channel-Argumente
- `statistiken.funnel_verteilung` → Channel-Mix-Empfehlung
- `statistiken.intent_verteilung` → Channel-Vorschläge (z. B. viel transactional → Ads-Kandidat)
- `auffaelligkeiten` mit `typ: sweet_spot_cluster | kunde_gap_cluster` → strategische Argumente

### `04-04-forecast-modell`

- `cluster_aggregat` Top-10 nach Score → Forecast-Treiber-Liste
- Pro Cluster: Volumen + Median-Difficulty → Annahme für Ramp-up und Click-Through-Rate

### `04-05-90-tage-plan`

- `auffaelligkeiten` mit `typ: sweet_spot_cluster` → "Quick-Win"-Maßnahmen
- `cluster_aggregat` mit `kunden_abdeckung_top10_prozent < 20` → Content-Briefing-Kandidaten

### `05-01-mta-slide-bausteine`

- Cluster-Aggregat-Tabelle direkt als Slide-Tabelle
- Top-3-Auffälligkeiten als "Erkenntnis"-Slide-Inhalte
