# Wettbewerbs-Gap-Logik

Die Gap-Berechnung ist der **wertvollste Output** dieses Skills für die MTA-Story. Hier die genaue Regelung — Schwellwerte, Filter, Scoring — damit das Ergebnis reproduzierbar und nachvollziehbar bleibt.

Seit der Umstellung auf Ahrefs als Primärquelle ist die Volumen-Basis für die Gap-Berechnung ebenfalls primär Ahrefs (`ahrefs_volumen`); Sistrix-Volumen wird nur dann genutzt, wenn Ahrefs für ein Keyword keinen Wert liefert.

## 1. Definition: Was ist ein Gap?

Ein "Gap" ist ein Keyword, auf dem mindestens ein Wettbewerber stark rankt, der Kunde aber schwach oder gar nicht. Drei Schärfegrade:

| Gap-Typ | Kunden-Position | WB-Position | Bedeutung |
|---|---|---|---|
| **hart** | nicht im Top-100 (oder nicht in Sistrix erfasst) | mindestens 1 WB auf Position ≤ 10 | Kunde ist auf diesem Keyword unsichtbar, WB dominiert |
| **weich** | Position 31-100 | mindestens 1 WB auf Position ≤ 10 | Kunde rankt, aber zu schlecht für relevanten Traffic |
| **kein Gap** | Position ≤ 30 | egal | Kunde ist in der relevanten Zone, ggf. nur Optimierungs-Potenzial |

**Hart > weich** in der Priorität — bei einem harten Gap ist die Strecke länger, aber das Argument für den Strategen klarer ("hier rankt der Kunde überhaupt nicht").

## 2. Schwellwerte

| Schwellwert | Default | Konfigurierbar via Override |
|---|---|---|
| Min-Suchvolumen für Gap-Kandidaten | 200/Monat | `gap_min_volumen: <N>` |
| Top-Position-Schwelle WB | 10 | `wb_top_position: <N>` |
| Kunden-Position-Schwelle "in der Zone" | 30 | `kunde_zone: <N>` |
| Max Gaps pro Lauf in der Pool-Datei | unbegrenzt (Sortierung steuert Relevanz) | — |
| Max Gaps in der MD-Top-Tabelle | 30 | — |

**Volumen-Quelle für den Gap-Filter** (Reihenfolge):

1. `ahrefs_volumen` (Primary, weil Ahrefs jetzt für alle Gap-Kandidaten in Schritt 8 angereichert wird)
2. `sistrix_volumen` (Fallback, wenn Ahrefs für das Keyword nichts liefert)
3. wenn beide leer → Keyword bleibt im Pool, fällt aber aus der Gap-Sortierung heraus (Score-Berechnung skippt es)

Begründung der Defaults:

- **200/Monat**: unter dieser Schwelle ist der absolute Traffic-Wert zu klein, um in der MTA-Story als Argument zu zählen. Stratege kann bei Nischen-Branchen runtersetzen.
- **WB-Top-10**: Position 1-10 = erste Seite. Wer weiter unten rankt, liefert kein starkes "wir verlieren gegen WB X"-Argument.
- **Kunden-Zone 30**: Position 30 ist die De-facto-Sichtbarkeits-Grenze (Sistrix-Konvention). Wer schlechter rankt, hat de facto null relevanten organischen Traffic.

## 3. Filter — was wird ausgeschlossen

### Branded-Filter

Keywords, die einen Markennamen eines **Wettbewerbers** enthalten, werden grundsätzlich **nicht** als Gap behandelt, weil:

- der Kunde nicht für die Marke des WBs ranken sollte
- WBs ranken trivial für die eigene Marke — das ist kein Differenzierungs-Signal

**Erkennung (zweistufig, Ahrefs als zusätzliche Validierung):**

**Stufe 1 — Token-Match (wie bisher):**

- Aus `wettbewerber/liste.md` alle WB-`name`-Felder und WB-Domain-Hauptnamen
- Aus `data/kunde.md` Wettbewerber-`marke.synonyme`-Felder (falls in Markenprofilen erfasst)
- Aus `data/briefing.md` `wettbewerber_genannt[].name`

Heuristik: ein Keyword gilt als WB-branded, wenn es einen WB-Markennamen als ganzen Token enthält. Substring-Match nicht akzeptieren (z. B. "Beta" sollte nicht "betacarotin" mit einbeziehen).

**Stufe 2 — Ahrefs `is_branded`-Flag (NEU):**

- Wenn das Keyword in Schritt 8 mit Ahrefs angereichert wurde, wird `ahrefs_is_branded` als zusätzliche Signal-Quelle genutzt
- Übereinstimmung Token-Match + Ahrefs-Flag → Branded-Filter zieht, `branded_filter_grund` auf z. B. `"alpha-tech (token+ahrefs)"`
- Token-Match sagt branded, Ahrefs sagt `is_branded: false` → `branded_unscharf: true` setzen, Filter zieht trotzdem (Token-Match ist konservativer), Stratege wird im Pool-Markdown auf den Sonderfall hingewiesen
- Token-Match sagt nicht-branded, Ahrefs sagt `is_branded: true` → das Keyword wird **nicht** automatisch gefiltert (Ahrefs könnte ein anderes Marken-Keyword erkennen, z. B. einen Hersteller, der kein WB ist), aber im Pool als `branded_unscharf: true` markiert und im Auffälligkeiten-Block aufgegriffen

**Ausnahme:** Wenn der **Kunde** für die Marke eines WBs rankt, ist das eine eigene Auffälligkeit (`branded_traffic_wb_uebernommen`). Im Pool wird das Keyword mit `intent_hypothese: branded` + `gap_zu_kunde: false` markiert, aber im Auffälligkeiten-Block hervorgehoben.

**Kunden-Branded-Keywords** (Keywords, die einen Synonym des Kunden-Markennamens enthalten) werden **nicht** als Gap betrachtet — wenn der Kunde nicht für seinen eigenen Markennamen rankt, ist das ein separates technisches Problem (Indexierungs-/Penalty-Issue), das nicht in den Gap-Pool gehört.

### Aggregator-Filter

Keywords, deren **Top-rankende URLs primär Aggregatoren** sind, werden ausgeschlossen — weil ein Kunde dort nicht realistisch ranken kann.

Aggregator-Liste aus:

- `02-02-wettbewerber-identifikation/reference/aggregatoren-blocklist.md` (Standard-Liste)
- `wettbewerber/identifikation-schema.md` `aggregatoren_blocklist_zusatz` (projektspezifisch)

Erkennung: prüfe die Domain der `ranking_top_wb_url` und der Top-3 Sistrix-Ergebnisse für das Keyword. Wenn ≥ 2 von 3 Top-Domains in der Aggregator-Liste sind → Keyword filtern.

**Ausnahme:** Wenn `aggregator_filter_aus` als Override gesetzt ist — z. B. bei Branchen, in denen Aggregatoren legitime Wettbewerber sind (Reise, Versicherung, manche B2C-Vergleichsmärkte).

Aggregator-Filter ist **unverändert** gegenüber der alten Version — er nutzt URL-Domains und nicht Ahrefs-Flags.

### Sehr-Long-Tail-Filter (Soft-Filter)

Keywords mit Suchvolumen < `gap_min_volumen` (Default 200) werden aus dem Gap-Pool ausgeschlossen, bleiben aber im normalen Keyword-Pool — sind nur nicht "Gap-würdig" für die MTA-Story.

## 4. Gap-Score-Berechnung

Pro Gap-Keyword wird ein `gap_score` berechnet, der die Priorisierung steuert.

### Formel (Standard)

```
gap_score = log10(volumen) × wb_count_top10 × position_gewicht × difficulty_multiplikator
```

Wobei:

- `volumen` = `ahrefs_volumen` wenn vorhanden, sonst `sistrix_volumen`
- `wb_count_top10` = Anzahl WBs mit Position ≤ 10 auf diesem Keyword
- `position_gewicht`:
  - `1.5` für `hart` (Kunde nicht im Top-100)
  - `1.0` für `weich` (Kunde 31-100)
- `difficulty_multiplikator` — **jetzt immer aktiv** (zuvor optional), weil Ahrefs-Difficulty in Schritt 8 für alle Gap-Kandidaten verfügbar ist

### Difficulty-Multiplikator (Pflicht-Komponente)

| Difficulty | Multiplikator | Begründung |
|---|---|---|
| ≤ 20 | × 1.4 | sehr leicht erreichbar, sofortiger SEO-Win |
| 21-30 | × 1.2 | gut erreichbar |
| 31-50 | × 1.0 | Standard |
| 51-70 | × 0.85 | eher schwer |
| > 70 | × 0.7 | sehr schwer, hoher Aufwand |
| Difficulty leer (Ahrefs konnte nicht anreichern) | × 1.0 | neutraler Wert, kein Bonus, kein Malus |

Begründung: ein Gap mit niedriger Difficulty ist sofortiger SEO-Win — strategisch wertvoller als ein Hochvolumen-Gap mit Difficulty 90.

### Beispiele

| Keyword | Ahrefs-Vol | WBs Top-10 | Gap-Typ | Difficulty | Score |
|---|---|---|---|---|---|
| kabel verlängerung | 3.600 | 2 | hart | 24 | log10(3600) × 2 × 1.5 × 1.2 = 12.8 |
| messer schleifen anleitung | 1.200 | 1 | weich | 18 | log10(1200) × 1 × 1.0 × 1.4 = 4.31 |
| profi werkzeug günstig | 720 | 3 | hart | 62 | log10(720) × 3 × 1.5 × 0.85 = 10.9 |
| nische long-tail xyz | 300 | 1 | hart | leer | log10(300) × 1 × 1.5 × 1.0 = 3.71 |

### Sortier-Regel

In der CSV: nach `gap_score` absteigend, leere Scores ans Ende.

In der Markdown-Top-Tabelle: nach `gap_score` absteigend, dabei aber **mindestens 2 unterschiedliche Top-WBs** in den Top-10 vertreten — wenn alle Top-10 vom selben WB dominiert sind, das im Auffälligkeiten-Block als `wb_dominanz_in_thema` hervorheben, damit es nicht wirkt wie ein Wettbewerber-spezifisches Problem.

## 5. Gap-Cluster-Erkennung

Mehrere Gaps mit ähnlichem Wortstamm bilden einen Cluster — das ist strategisch wertvoller als isolierte Einzelgaps.

### Heuristik (light) — unverändert

1. Pro Gap-Keyword: tokenize, alle Stopwords entfernen (de/en kurze Stoppwortliste)
2. Pro Token: zähle, in wie vielen Gap-Keywords er vorkommt
3. Tokens mit Vorkommen ≥ 3 und Token-Länge ≥ 4 → potenzielle Cluster-Anker
4. Bilde Cluster: alle Gap-Keywords, die einen Anker-Token teilen

### Parent-Topic-Cluster (NEU, Ahrefs-basiert)

Zusätzlich zum Token-basierten Clustering werden Gaps auch nach `ahrefs_parent_topic` gruppiert:

1. Pro Gap-Keyword: lies `ahrefs_parent_topic`
2. Gruppiere Gaps mit identischem Parent-Topic
3. Parent-Topic-Cluster mit ≥ 3 Gaps → eigener Cluster-Eintrag

Beide Cluster-Sichten werden im Pool-Markdown nebeneinander gerendert. Stratege wählt in `03-03-seo-keyword-kategorisierung`, welche der beiden Sichten besser zur MTA-Story passt.

### Cluster-Ausgabe

Pro Cluster (Token oder Parent-Topic):

- `anker_token` oder `parent_topic`: das gemeinsame Wort/Topic
- `anzahl_gaps`: wie viele Gaps im Cluster
- `kumuliertes_volumen`: Summe der Suchvolumina
- `top_wb`: welcher WB dominiert den Cluster
- `beispiel_keywords`: 3-5 Beispiele

Cluster mit `anzahl_gaps ≥ 3` UND `kumuliertes_volumen ≥ 1000` werden als Auffälligkeit `gap_cluster` ausgegeben — das ist eine **Content-Lücke**, die strategisch in der MTA als "Themen-Bereich" angegangen werden sollte.

## 6. Edge Cases

### Kunde ist gar nicht in Sistrix indexiert

Wenn `data/seo-sichtbarkeit.md` Frontmatter den Kunden mit `sistrix_indexiert: false` führt: **fast jedes Keyword ist potenziell ein Gap**. Der Skill berechnet trotzdem Gaps, aber im Pool-Markdown wird ein deutlicher Hinweis-Block oben eingefügt:

> "Hinweis: Kunde ist in Sistrix nicht indexiert. Alle gefundenen Gaps sind theoretisch — bevor die MTA-Story aufgebaut wird, sollte mit dem Strategen geklärt werden, warum der Kunde nicht erfasst ist (zu klein? Indexierungs-Issue? falsche Country-Einstellung?)."

### Kein Wettbewerber vorhanden

Wenn der Pool nur Kunden-Daten hat (Kunden-only-Modus oder leere WB-Liste): Gap-Berechnung wird übersprungen, im Pool-Markdown ein Hinweis, dass Gap-Analyse erst nach `02-02-wettbewerber-identifikation` sinnvoll ist.

### Sehr viele Gaps (>200)

Soft-Cap zur Übersicht: in der Markdown-Top-Tabelle nur 30 Einträge, Rest in CSV. Im Auffälligkeiten-Block ein eigener Eintrag `gap_pool_sehr_gross` mit Hinweis, dass die Wettbewerber dem Kunden weit voraus sind und die MTA-Story den Fokus auf wenige Cluster legen sollte, statt Einzelgaps aufzuzählen.

### Gap-Kandidat ist gleichzeitig ein Ranking-Keyword des Kunden auf einer anderen URL

Manchmal rankt der Kunde mit URL A auf Position 45, mit URL B auf Position 8 für dasselbe Keyword. Sistrix liefert in der Regel die beste Position. Wenn die Daten inkonsistent erscheinen: in `crawl_luecken` (im Pool-Markdown-Body) notieren und Stratege bitten, manuell zu prüfen.

### Branded-Filter erkennt einen WB-Namen falsch

Z. B. WB heißt "Bauen GmbH" — dann ist "bauen kostenrechner" trivial branded? Nein — der Branded-Filter braucht **Token-Match**, nicht Substring-Match. "Bauen" ist als generisches Wort zu häufig, um als WB-Marke zu zählen. Heuristik:

- WB-Markenname muss mindestens 4 Zeichen lang sein
- Im Keyword muss er als eigenständiges Token vorkommen (`bauen kostenrechner` enthält Token `bauen`, das eine WB-Marke wäre — würde gefiltert)

**Schutz-Heuristik:** Wenn ein WB-Markenname identisch zu einem hochfrequenten generischen Wort der Branche ist, im Skill-Pool-Markdown im Body Hinweis ausgeben und Stratege manuell entscheiden lassen (Override `branded_filter_ignore: ["bauen"]`). **Ergänzend:** Wenn Ahrefs `is_branded: false` liefert, ist das ein zusätzliches Signal, dass das Keyword nicht als branded gefiltert werden sollte — wird als `branded_unscharf: true` markiert für Strategen-Review.

### Ahrefs liefert für ein Gap-Kandidaten keine Daten

`ahrefs_volumen` und `difficulty` bleiben leer. Gap-Score wird trotzdem berechnet:

- Volumen-Fallback auf Sistrix-Volumen
- Difficulty-Multiplikator = 1.0 (neutral)
- Wenn auch Sistrix-Volumen leer → Keyword fällt aus der Gap-Sortierung, bleibt aber im Pool

## 7. Reproduzierbarkeit

Pro Lauf werden die Schwellwerte und Filter-Konfigurationen im Pool-Markdown Frontmatter dokumentiert:

```yaml
gap_konfiguration:
  gap_min_volumen: 200
  wb_top_position: 10
  kunde_zone: 30
  position_gewicht_hart: 1.5
  position_gewicht_weich: 1.0
  difficulty_multiplikator_aktiv: true   # jetzt immer true, weil Ahrefs Pflicht
  volumen_quelle_primary: ahrefs         # Ahrefs primär, Sistrix als Fallback
  aggregator_filter_aktiv: true
  branded_filter_aktiv: true
  branded_filter_ahrefs_validiert: true  # NEU — Ahrefs is_branded als Zusatz-Signal
  branded_filter_ignore: []
```

Damit ist bei Strategen-Rückfragen ("warum ist Keyword X nicht im Gap-Pool?") sofort nachvollziehbar, welche Regel angewendet wurde.
