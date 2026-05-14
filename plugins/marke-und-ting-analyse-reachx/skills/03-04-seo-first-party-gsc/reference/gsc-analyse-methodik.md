# Analyse-Methodik

Konkrete Schwellwerte, Heuristiken und Berechnungs-Formeln für die fünf Kern-Analysen des Skills:

1. Gewinner/Verlierer-Detection
2. Cannibalization-Detection
3. Hidden-Content-Discovery
4. CTR-Gap-Analyse
5. Position-zu-Klick-Hebel (Quick-Win-Pool)

Alle Schwellwerte sind als **Default** zu verstehen — bei wiederkehrenden False-Positives in echten MTAs nachjustieren und hier dokumentieren.

## 1. Gewinner/Verlierer-Detection

**Eingangs-Daten:** `gsc-performance.csv` mit Zeilen `periode=current` und `periode=comparison_qoq`. Join über `query`.

**Berechnung pro Query:**

```
delta_klicks_absolut = clicks_current - clicks_comparison
delta_klicks_prozent = (delta_klicks_absolut / max(clicks_comparison, 1)) * 100
```

**Klassifikation:**

| Klasse | Bedingung |
|---|---|
| `gewinner` | `delta_klicks_prozent >= +20` UND `delta_klicks_absolut >= +5` |
| `verlierer` | `delta_klicks_prozent <= -20` UND `delta_klicks_absolut <= -5` |
| `neu` | `clicks_comparison == 0` UND `clicks_current >= 5` |
| `verloren` | `clicks_comparison >= 5` UND `clicks_current == 0` |
| `none` | sonst |

**Begründung der Schwellwerte:**

- **20%-Hürde** filtert normales Rauschen (Saisonalität, Update-Schwankungen)
- **5-Klick-Minimum** filtert sehr kleine Queries (von 1 auf 2 Klicks = +100%, aber bedeutungslos)
- **Neu/Verloren** als eigene Klassen, weil Prozent-Delta bei 0-Basis nicht definiert ist

**Output-Reihenfolge:**

- Gewinner-Tabelle: sortiert nach `delta_klicks_absolut` absteigend
- Verlierer-Tabelle: sortiert nach `delta_klicks_absolut` aufsteigend (größter Verlust zuerst)

**Edge Cases:**

- Query erscheint nur in einer Periode → in der jeweils anderen Periode mit clicks=0 ergänzen
- Anonymous Queries (`ist_anonymous=true`) → aus Gewinner/Verlierer ausgeschlossen, sie sind aggregierte Pools
- Brand-Queries (top_ranking_url ist Homepage UND Query enthält Kunden-Namen-Token aus `meta.json.kunde`) → markieren als `kategorie_analyse: brand` aber TROTZDEM in Gewinner/Verlierer aufnehmen, mit "(Brand)"-Marker in der HTML-Tabelle. Brand-Trends sind strategisch relevant (Brand-Search-Lift durch Kampagnen, etc.)

## 2. Cannibalization-Detection

**Voraussetzung:** API liefert pro Query ≥ 2 ranking_urls (siehe `gsc-api-nutzung.md` Abschnitt "Cannibalization-Konstruktion"). Wenn nicht möglich → Analyse fällt aus mit Hinweis.

**Kandidaten-Identifikation pro Query:**

```
urls_top_50 = ranking_urls mit position <= 50 für diese Query in 90T
```

**Klassifikation als Cannibalization:**

| Bedingung | Schwellwert |
|---|---|
| Anzahl konkurrierender URLs | `len(urls_top_50) >= 2` |
| Beide unter Top-10 | `alle position > 10` (keine URL ist klar Lead) |
| Genug Volumen | `summe(impressions) >= 100` in 90T |
| Brand-Filter | Query ist kein Brand-Term (sonst sind Mehrfach-Rankings normal: Homepage + About + Kontakt-Page) |

**Empfehlungs-Logik:**

- Wenn alle URLs auf gleicher Page-Kategorie (z. B. drei Blog-Posts) → **Consolidation** empfehlen (Inhalte zusammenführen, 301-Redirect der schwächeren auf stärkere)
- Wenn URLs auf verschiedenen Kategorien (z. B. Service-Page + Blog) → **Internes Linking** empfehlen (Blog soll Service-Page boosten, nicht konkurrieren)
- Wenn eine URL deutlich höhere Impressions hat (≥ 5× andere) → **Canonical** empfehlen (schwache URL canonicalisiert auf starke)

**Output:**

- Cannibalization-Tabelle in Markdown: Query, URLs (als Liste), Positionen, Impressions-Summe, Empfehlung
- Jede gefundene Cannibalization landet als `kategorie_analyse: cannibalization` Tag in `gsc-performance.csv` für die Query

## 3. Hidden-Content-Discovery

Versehentlich rankende Pages mit Klick-Potenzial — Content, der ungeplant rankt aber kein systematischer Hebel im aktuellen Content-Plan ist.

**Eingangs-Daten:** Top-50-Queries aus `current`-Periode mit `position <= 5`. Plus zugehörige `top_ranking_url`.

**Heuristik:**

```
ist_hidden_content_kandidat = (
    position <= 5
    AND clicks >= 20  in 90T
    AND kategorie_seite IN {blog, news, presse}
    AND NOT query ist brand
)
```

**Begründung:**

- **Position ≤ 5** → die Page rankt schon gut, Klick-Potenzial ist da
- **Klicks ≥ 20** → die Query hat reales Volumen
- **kategorie_seite ∈ {blog, news, presse}** → das ist KEINE typische Service-/Produkt-Treffer-Page, also "versehentlich". Ein Blog-Artikel aus 2018, der für eine kommerzielle Query auf Position 3 rankt = Hidden-Content-Kandidat
- **Nicht Brand** → Brand-Queries auf Blog-Pages sind normal (z. B. Pressemitteilungen ranken für Brand)

**Empfehlungs-Logik:**

- **Default-Empfehlung**: Inhalt aktualisieren (Datum, Beispiele), zur passenden Service-/Produkt-Page intern verlinken, ggf. neue Service-Page erstellen falls keine existiert
- Bei sehr alten Pages (URL enthält Jahreszahl ≤ aktuelles Jahr - 3): zusätzlich "Refresh oder Migration zu permanenter URL" empfehlen

**Schwellwert "≥ 3 relevante Treffer mit zusammen ≥ 50 Klicks"** löst Auffälligkeit `hidden_content_relevant` aus.

## 4. CTR-Gap-Analyse

Pro Top-200-Query vergleichen: ist die CTR der Query unter dem, was bei dieser durchschnittlichen Position normalerweise zu erwarten wäre?

**Eingangs-Daten:**

- `gsc-ctr-by-position`-Antwort (Domain-spezifische CTR-Kurve)
- ODER (Fallback) Branchen-generische CTR-Benchmarks (siehe unten)

**Berechnung pro Query:**

```
position_bucket = floor(query.position)         # 1.4 → 1, 6.8 → 6
benchmark_ctr = ctr_by_position[position_bucket]
ctr_gap_punkte = (query.ctr - benchmark_ctr) * 100   # in Prozentpunkten
ctr_gap_relativ = query.ctr / benchmark_ctr           # 0..1+
```

**Klassifikation als CTR-Gap-Kandidat:**

| Bedingung | Schwellwert |
|---|---|
| Negative Lücke | `ctr_gap_punkte <= -2.0` (mindestens 2 Prozentpunkte unter Benchmark) |
| Genug Impressions | `impressions >= 500` in 90T |
| Position nicht ganz unten | `position <= 20` (bei Position 30+ ist CTR-Berechnung instabil) |
| Nicht Anonymous | `ist_anonymous == false` |

**Geschätztes Zusatz-Klick-Potenzial:**

```
zusatz_klicks_pro_monat = (benchmark_ctr - query.ctr) * impressions * (30/90)
```

**Output-Reihenfolge:**

- CTR-Gap-Tabelle sortiert nach `zusatz_klicks_pro_monat` absteigend (Top-Klick-Hebel zuerst)

**Schwellwert "≥ 10 Queries mit Gap ≤ -2 pp"** löst Auffälligkeit `ctr_gap_systematisch` aus → Title/Snippet-Optimierung als Cluster-Hebel.

## 5. Position-zu-Klick-Hebel (Quick-Win-Pool)

Der klassische "Position 4-10"-Quick-Win-Ansatz. Queries, die sichtbar in der SERP sind (Top-10), aber nicht auf Position 1-3 (wo die meisten Klicks passieren). Push auf Top-3 = großer Klick-Lift.

**Eingangs-Daten:** Top-200-Queries aus `current`-Periode mit `ist_anonymous=false`.

**Klassifikation als Quick-Win:**

| Bedingung | Schwellwert |
|---|---|
| Position-Bereich | `4 <= position <= 10` |
| Genug Impressions | `impressions >= 300` in 90T |
| Niedriges aktuelles Klick-Volumen | `clicks <= 30` in 90T (sonst kein Quick-Win mehr) |
| Nicht Brand | nicht Brand-Query |

**Geschätztes Zusatz-Klick-Potenzial bei Sprung auf Position 3:**

```
ctr_pos_3_benchmark = ctr_by_position[3]           # aus Domain-Kurve oder Generic-Benchmark
geschaetzte_klicks_pos_3 = ctr_pos_3_benchmark * impressions
zusatz_klicks_pro_monat = (geschaetzte_klicks_pos_3 - clicks) * (30/90)
```

**Output:**

- Quick-Win-Tabelle sortiert nach `zusatz_klicks_pro_monat` absteigend
- Top-20 in der Markdown-Tabelle, alle als `kategorie_analyse: quick_win` in CSV

**Summen-Statistik:**

- `quick_win_geschaetztes_potenzial_klicks_pro_monat` = Summe aller `zusatz_klicks_pro_monat` aus dem Quick-Win-Pool
- Bei ≥ 20 Quick-Wins UND Summe ≥ 300 Klicks/Monat → Auffälligkeit `quick_win_cluster` (hoher strategischer Wert)

## CTR-Benchmarks pro Position

Wenn `gsc-ctr-by-position`-Tool keine ausreichenden Daten liefert (zu wenig Datenpunkte für eine bestimmte Position), nutzt der Skill diese **branchen-generischen Fallback-Werte**. Quelle: aggregierte Daten aus mehreren publizierten Studien (Advanced Web Ranking, Sistrix, Backlinko), gemittelt für deutsche SERP.

| Position | Avg CTR (Desktop+Mobile) | Hinweis |
|---|---|---|
| 1 | 28% | Stark abhängig von SERP-Features (Featured Snippet kann auf 35-40% pushen) |
| 2 | 15% | |
| 3 | 11% | |
| 4 | 8% | |
| 5 | 6% | |
| 6 | 4,5% | |
| 7 | 3,5% | |
| 8 | 2,8% | |
| 9 | 2,3% | |
| 10 | 2,0% | |
| 11-15 | 1,2% | Zweite SERP-Seite |
| 16-20 | 0,8% | |
| 21-30 | 0,4% | |
| 31+ | 0,2% | |

**Wichtig:** Diese Werte sind **konservative Annahmen**. Echte Domain-CTR weicht stark ab je nach:

- Branche (B2B oft niedrigere CTR-Kurve, B2C oft höher)
- SERP-Feature-Häufigkeit (Featured Snippet, People-Also-Ask, Local Pack drücken Organic-CTR)
- Query-Intent (Brand-Queries hohe CTR, Generic-Queries niedrigere)

Wo Domain-spezifische Kurve aus `gsc-ctr-by-position` verfügbar ist, **diese bevorzugen** — sie bildet die echte Realität ab. Generic-Benchmarks nur als Fallback.

## Brand-Detection

Eine Query gilt als Brand-Query, wenn:

```
brand_tokens = tokenize(meta.json.kunde)   # z. B. ["mustermann", "gmbh"]
query_tokens = tokenize(query.lowercase())
ueberlap = brand_tokens ∩ query_tokens
ist_brand = (len(ueberlap) > 0 AND len(ueberlap) >= len(brand_tokens) - 1)
```

Beispiel: Kunde "Mustermann GmbH" → Brand-Queries sind "mustermann", "mustermann gmbh", "mustermann shop". Nicht "muster gmbh" (anderes Token).

Heuristik ist bewusst etwas unscharf. Stratege kann im Output-Markdown manuelle Korrekturen vornehmen.

**Brand-Klick-Anteil:** Summe Klicks aller Brand-Queries / Gesamt-Klicks. Bei ≥ 50% → Auffälligkeit `brand_dominant`.

## Mobile-Underperformance

**Eingangs-Daten:** `gsc-performance-by-device`-Antwort.

```
mobile_ctr = device['mobile'].ctr
desktop_ctr = device['desktop'].ctr
mobile_position = device['mobile'].position
desktop_position = device['desktop'].position
```

**Klassifikation als Mobile-Underperformance:**

- `mobile_ctr < desktop_ctr * 0.7` (Mobile-CTR weniger als 70% der Desktop-CTR)
- UND Position-Differenz < 2 (also nicht erklärbar durch deutlich schlechtere Mobile-Positionen)

→ Auffälligkeit `mobile_underperformance`. Empfehlung: Mobile-Snippets prüfen (Title-Truncation), Mobile-UX (Page-Speed, Above-the-Fold).

## Non-DACH-Traffic-Detection

**Eingangs-Daten:** `gsc-metrics-by-country`-Antwort.

```
nicht_dach_anteil = sum(klicks für country NOT IN [de, at, ch]) / sum(alle klicks)
```

Bei `nicht_dach_anteil >= 0.15` UND `meta.json.region` nicht international → Auffälligkeit `non_dach_traffic_signifikant`. Empfehlung: Stratege prüfen, ob internationale Märkte unterschätzt sind oder ob es Spam-Traffic ist (Country-Liste anschauen).

## Sistrix-GSC-Divergenz (Cross-Reference)

Nur prüfbar, wenn `audits/seo-sichtbarkeit.md` (von `03-01-seo-sichtbarkeit-und-rankings`) bereits existiert.

**Lese aus `seo-sichtbarkeit.md` Frontmatter:** `statistiken.kunde_visibility_aktuell`.

**Berechne:** Erwartete Klicks aus Sistrix-VI (grobe Daumenregel: VI × 5000 = geschätzte monatliche organische Klicks für deutsche Markt, sehr ungenau aber als Richtwert ok).

**Klassifikation:**

- Wenn `sistrix_erwartete_klicks > 3 * gsc_tatsaechliche_klicks_pro_monat` → Sistrix überschätzt deutlich. Auffälligkeit `sistrix_gsc_divergenz` mit Hinweis "Sistrix-Modell überzeichnet, GSC zeigt deutlich weniger echten Traffic. Mögliche Gründe: Brand-Lastige Sistrix-Top-Keywords, viele Long-Tail-Rankings die wenig Klicks bringen, schwache CTR."
- Wenn `gsc_tatsaechliche_klicks_pro_monat > 3 * sistrix_erwartete_klicks` → Sistrix unterzeichnet. Auffälligkeit "GSC zeigt mehr Traffic als Sistrix erwarten würde — wahrscheinlich starker Anonymous/Long-Tail-Anteil oder Brand-Direct-Traffic, der Sistrix nicht sieht."

Wenn `seo-sichtbarkeit.md` nicht existiert: Auffälligkeit überspringen, keine Datenbasis.

## Daten-Qualitäts-Bewertung

Setze `daten_qualitaet` im Frontmatter basierend auf Datenbasis:

| Klasse | Bedingung |
|---|---|
| `hoch` | clicks_total/90T ≥ 1000 UND historie_verfuegbar_tage ≥ 365 |
| `mittel` | clicks_total/90T ≥ 200 UND historie_verfuegbar_tage ≥ 90 |
| `niedrig` | clicks_total/90T ≥ 50 UND historie_verfuegbar_tage ≥ 30 |
| `keine` | sonst |

Bei `niedrig` und `keine`: Hinweis im Body und im Schluss-Format, dass Quick-Win-Empfehlungen mit Vorsicht zu lesen sind.

## Re-Run-Konsistenz

Bei Re-Run mit `audits/_backup/`-Optionen:

- Backup-Dateinamen enthalten `<skill>-<typ>-<ISO>.csv` und `.md`
- Roh-Daten unter `audits/raw/` werden bei Re-Run komplett überschrieben (kein Backup, Roh-Daten sind ohnehin reproduzierbar via neue API-Calls)

## Offene Methodik-Fragen für spätere Iteration

(In zukünftigen MTAs prüfen und hier dokumentieren:)

- Sind die 20%/5-Klick-Schwellwerte für Gewinner/Verlierer in B2B-Nischen sinnvoll, wo absolute Klick-Volumina klein sind? Eventuell Skalierung mit Domain-Größe einbauen.
- Wie verhalten sich SERP-Features (Featured Snippet, People-Also-Ask) zur CTR-Kurve? Aktuell ignoriert.
- Soll Cannibalization-Erkennung zusätzliche Pages-on-Page-2 berücksichtigen (Position 11-20)? Aktuell harter Cutoff bei 10.
- Quick-Win-Potenzial-Schätzung nutzt CTR-Benchmark bei Position 3 — konservativ. Optional: zusätzlich Pos-1-Potenzial ausweisen für ambitionierte Story.
