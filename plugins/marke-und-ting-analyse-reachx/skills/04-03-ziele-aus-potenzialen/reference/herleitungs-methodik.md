# Herleitungs-Methodik

Definiert die Formeln, Quellen-Hierarchie und Bandbreiten-Logik für `04-03-ziele-aus-potenzialen`.

## 1. Kern-Prinzipien

1. **Pflicht-Bandbreite** — niemals Punktschätzungen. Jede Zahl im Output hat einen Min/Realistisch/Max-Tripel.
2. **Quellen-Transparenz** — jede Annahme hat ein `quelle`-Feld mit verlinkbarem Ursprung.
3. **Konfidenz pro Annahme** — `hoch | mittel | niedrig` wird mitgeschrieben; bei `niedrig` warnt der Output.
4. **Steady-State-Bezug** — die ausgegebenen Bandbreiten gelten für den Steady State nach Ramp-up, nicht für Monat 1. Der Forecast-Skill rechnet die Ramp-up-Kurve.
5. **Kein Zurückschreiben ins Briefing** — Briefing bleibt "was der Kunde gesagt hat", abgeleitete Ziele sind eigene Quelle.

## 2. Quellen-Hierarchie

Wenn mehrere Quellen für dieselbe Annahme verfügbar sind, gilt diese Reihenfolge:

1. **Kunden-Daten aus Audit** (höchste Priorität) — z. B. SEO-Volumen aus Sistrix-Audit, Local-Volumen aus GMB-Audit
2. **Briefing-Aussage des Kunden** — z. B. AOV "wir haben durchschnittlich 150 EUR pro Auftrag"
3. **Portfolio-Ableitung aus `data/kunde.md`** — z. B. AOV aus Preis-Range der Produkte
4. **Branchen-Benchmark** aus diesem Referenz-Dokument
5. **Schätzung Skill** (niedrigste Priorität) — wird im Output mit Konfidenz `niedrig` und Auffälligkeit `quelle_branchen_benchmark_unsicher` flagged

Wenn ein Wert aus Quelle 1-3 abweicht von Quelle 4-5, **immer Quelle 1-3 bevorzugen** und im Schema dokumentieren.

## 3. Bandbreiten-Logik

### 3.1 Punkt-zu-Bandbreite-Konversion

Wenn eine Quelle nur einen Punktwert liefert (z. B. Briefing nennt "150 EUR AOV"):

- konservativ = Punktwert × 0,75
- realistisch = Punktwert
- ambitioniert = Punktwert × 1,25

Diese Konversion gilt für AOV, Volumen-Werte, CR aus Punkt-Aussagen.

### 3.2 Branchen-Default-Spreads

Branchen-Benchmark-Bandbreiten haben standardmäßig einen Faktor **2-4** zwischen konservativ und ambitioniert (siehe `ziel-annahmen-schema-template.md`).

Wenn der Spread im Schema kleiner ist (< Faktor 1,8): Hinweis im Phase-A-Schluss, dass die Annahmen ggf. zu optimistisch sind.

### 3.3 Konfidenz-Propagation

Pro Kanal-Berechnung wird die niedrigste Konfidenz der eingesetzten Annahmen ermittelt:

```
kanal_konfidenz = min(volumen_konfidenz, cr_konfidenz, aov_konfidenz, lead_funnel_konfidenz)
```

Aggregat-Konfidenz = niedrigste Kanal-Konfidenz über die im Aggregat enthaltenen Kanäle.

## 4. Kern-Formeln pro Kanal

### 4.1 SEO

```
traffic_szenario = volumen_basis × klick_anteil_szenario
orders_szenario  = traffic_szenario × cr_szenario × lead_funnel_gesamt_szenario (falls B2B)
umsatz_szenario  = orders_szenario × aov_szenario
```

Wobei:

- `volumen_basis` aus `audits/seo-cluster-zusammenfassung.md` (kumuliertes Suchvolumen der Top-3-Cluster) oder Top-50-Keywords als Fallback
- `klick_anteil` typisch 20-40% (siehe `ziel-annahmen-schema-template.md`)
- `lead_funnel_gesamt_szenario` (B2B) = produkt aller Lead-Funnel-Stufen für das jeweilige Szenario
- B2C: `lead_funnel_gesamt = 1.0` (Direct-Conversion)

### 4.2 SEA / Google-Ads

Zwei Modi je nach Spend-Annahme:

**Modus A — Spend-getrieben** (Default wenn Spend-Annahme vorhanden):

```
klicks_szenario  = spend_szenario / durchschnittlicher_cpc
orders_szenario  = klicks_szenario × cr_szenario × lead_funnel_gesamt_szenario
umsatz_szenario  = orders_szenario × aov_szenario
```

**Modus B — Volumen-getrieben** (wenn Spend-Annahme fehlt):

```
klicks_szenario  = volumen_basis × ads_impression_share_szenario × ads_ctr_szenario
```

`ads_impression_share` typisch konservativ 5%, realistisch 15%, ambitioniert 30%.
`ads_ctr` typisch 3-8% (Brand-Keywords höher, generische niedriger).

### 4.3 Local-Pack / GMB

```
traffic_szenario = lokales_volumen × local_pack_klick_rate × map_share_szenario
orders_szenario  = traffic_szenario × cr_szenario × lead_funnel_gesamt_szenario
umsatz_szenario  = orders_szenario × aov_szenario
```

`local_pack_klick_rate` typisch 20-30% (User klickt auf eines der 3 Local-Pack-Ergebnisse).
`map_share_szenario` typisch konservativ 0,15, realistisch 0,33, ambitioniert 0,50 (Anteil unter 3 Local-Pack-Plätzen).

### 4.4 LinkedIn-Ads / Meta-Ads (Paid Social)

```
impressionen_szenario = spend_szenario / cpm_szenario × 1000
klicks_szenario       = impressionen_szenario × ctr_szenario
orders_szenario       = klicks_szenario × cr_szenario × lead_funnel_gesamt_szenario
umsatz_szenario       = orders_szenario × aov_szenario
```

CPM-Annahmen aus Branchen-Benchmark (LinkedIn typisch 80-200 EUR CPM, Meta typisch 8-25 EUR CPM).
CTR typisch LinkedIn 0,3-0,8%, Meta 0,8-2,5%.

### 4.5 Social-organisch

```
reichweite_szenario = follower_basis × engagement_rate_szenario
klicks_szenario     = reichweite_szenario × link_click_rate_szenario
orders_szenario     = klicks_szenario × cr_szenario × lead_funnel_gesamt_szenario
umsatz_szenario     = orders_szenario × aov_szenario
```

Engagement-Rate plattformspezifisch (Instagram 1-3%, TikTok 5-15%, LinkedIn 2-4%, Pinterest 0,5-2%).

### 4.6 Newsletter

```
oeffnungen_szenario = liste_groesse × open_rate_szenario
klicks_szenario     = oeffnungen_szenario × ctr_szenario
orders_szenario     = klicks_szenario × cr_szenario × lead_funnel_gesamt_szenario
umsatz_szenario     = orders_szenario × aov_szenario
```

Branchen-Benchmark Open-Rate 20-35%, CTR 2-8%.

### 4.7 Content / Blog

Analog SEO mit etwas niedrigeren CR (Mid-Funnel-Charakter): `cr_konservativ × 0,7` als Default-Adjustment, im Schema explizit dokumentiert.

### 4.8 Website-CRO als Hebel-Faktor

Website-CRO ist **kein eigener Traffic-Kanal**, sondern ein **Multiplikator auf die bestehenden Conversions** aus den anderen Kanälen.

```
orders_kanal_mit_cro_szenario = orders_kanal_szenario × (1 + cro_uplift_szenario)
```

Default CRO-Uplift: konservativ +10%, realistisch +15%, ambitioniert +30%.
Im Schema mit Quelle `cro_hebel` markiert, im Output als eigener Block mit klarer Hebel-Logik dargestellt.

## 5. Aggregat-Logik

### 5.1 Roh-Summe vs. korrigierte Summe

```
aggregat_roh_szenario = sum(kanal_szenario_orders) über alle Kanäle
aggregat_korrigiert_szenario = aggregat_roh_szenario × doppelzaehlung_faktor
```

`doppelzaehlung_faktor` aus Schema:
- 1,00 wenn nur 1 Kanal aktiv
- 0,85 wenn 2 Kanäle aktiv
- 0,75 wenn 3+ Kanäle aktiv

Im Output **beide Zahlen ausweisen** (Transparenz), Default für die Kommunikation ist die korrigierte Summe.

### 5.2 Klumpenrisiko-Detektion

Pro Szenario prüfen:

```
max_kanal_anteil = max(kanal_umsatz / aggregat_korrigiert_umsatz) über alle Kanäle
if max_kanal_anteil > 0.60:
    auffaelligkeit "kanal_dominiert_ergebnis"
```

## 6. Plausibilitäts-Check gegen Briefing-KPIs

Wenn `lauf_modus: plausibilitaets_check` oder `hybrid` und Briefing eine bezifferte KPI nennt:

```
if kunden_kpi > aggregat_ambitioniert × 1.10:
    auffaelligkeit "kunde_ziel_unrealistisch_hoch", relevanz hoch
elif kunden_kpi < aggregat_konservativ × 0.90:
    auffaelligkeit "kunde_ziel_unrealistisch_niedrig", relevanz mittel
else:
    auffaelligkeit "briefing_kpi_passt", relevanz niedrig (positive Bestätigung)
```

Toleranz-Faktor 10% wegen Rundung und Modell-Unsicherheit.

## 7. B2B-Lead-Funnel-Mechanik

Wenn `lead_funnel.aktiv: true`:

```
funnel_gesamt_szenario = stufe1_cr_szenario × stufe2_cr_szenario × stufe3_cr_szenario
```

Diese Quote wird im Kanal-Block zwischen `klicks` und `orders` zwischengeschaltet:

```
anfragen_szenario   = klicks_szenario × cr_szenario  (Form-CR auf Klicks)
qualifiziert        = anfragen × stufe1_cr
angebote            = qualifiziert × stufe2_cr
auftraege           = angebote × stufe3_cr
umsatz              = auftraege × aov
```

Im CSV-Output bekommt jede Stufe eine eigene Zeile mit `metrik`-Wert (`anfragen`, `qualifiziert_leads`, `angebote`, `orders`).

## 8. Volumen-Basis-Extraktion aus den Audits

### 8.1 SEO

Reihenfolge:

1. **`audits/seo-cluster-zusammenfassung.md`** Frontmatter: Top-3-Cluster nach `cluster_score`, ihre `kumuliertes_volumen` summieren. Konfidenz `hoch`.
2. **`audits/seo-keyword-cluster.csv`** (Fallback): Top-50 Keywords nach Volumen summieren. Konfidenz `mittel`.
3. **`audits/seo-keywords.csv`** (Fallback 2): wie 2., Konfidenz `mittel`.
4. Wenn keine Daten: Branchen-Benchmark aus `ziel-annahmen-schema-template.md`. Konfidenz `niedrig`. Auffälligkeit `quelle_branchen_benchmark_unsicher`.

### 8.2 SEA

Reihenfolge:

1. **`audits/google-ads.md`** Frontmatter: Branchen-Spend-Range, eigene aktive Spend-Schätzung. Konfidenz `mittel`.
2. **Briefing-Aussage**: wenn Kunde Spend-Budget genannt. Konfidenz `hoch`.
3. Branchen-Benchmark. Konfidenz `niedrig`.

### 8.3 Local-Pack / GMB

Reihenfolge:

1. **`audits/local-gmb.md`** Frontmatter: lokales Suchvolumen, GMB-Reviews-Stand. Konfidenz `hoch`.
2. **`audits/local-rankings.csv`**: aggregiertes Volumen über Top-Local-Keywords. Konfidenz `mittel`.
3. Branchen-Benchmark mit Region-Modifikator. Konfidenz `niedrig`.

### 8.4 LinkedIn-Ads / Meta-Ads

Reihenfolge:

1. **`audits/linkedin-ads.md` / `audits/meta-ads.md`**: aktuelle Spend-Hypothese, Targeting-Daten. Konfidenz `mittel`.
2. Branchen-Benchmark CPM × Spend-Annahme. Konfidenz `niedrig`.

### 8.5 Social-organisch

Reihenfolge:

1. **`audits/instagram-wettbewerb.md`, `tiktok-wettbewerb.md`, `linkedin-wettbewerb.md`, `pinterest-wettbewerb.md`**: aktuelle Follower-Basis des Kunden, durchschnittliche Engagement-Rate. Konfidenz `mittel`.
2. Branchen-Benchmark. Konfidenz `niedrig`.

## 9. Ramp-up-Bezug

Alle ausgegebenen Bandbreiten gelten für den **Steady State**. Der Ramp-up wird im Schema dokumentiert und an `04-04-forecast-modell` weitergereicht.

Wenn die Briefing-Timeline kürzer ist als der Top-Kanal-Ramp-up:

- Auffälligkeit `ramp_up_diskrepanz_zu_briefing_timeline`
- Empfehlung im Output: Hybrid-Strategie aus Sofort-Hebeln (SEA, Meta-Ads) plus mittelfristigen Hebeln (SEO, Content)

## 10. Validierung vor dem Schreiben

Vor dem Output prüft der Skill:

1. Jeder Kanal hat genau drei Szenario-Werte (konservativ < realistisch < ambitioniert)
2. konservativ ≤ realistisch ≤ ambitioniert (sonst Schema-Inkonsistenz)
3. Aggregat-Werte sind konsistent mit Kanal-Summen (innerhalb Doppelzählungs-Faktor)
4. Jede Zahl hat ein nicht-leeres `quelle`-Feld
5. CSV hat keine leeren Pflicht-Felder
6. Mindestens 6 Auffälligkeiten im Output (Pflicht-Mindestmenge)

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## 11. Skill-Reproduzierbarkeit

Jeder Lauf schreibt ins Output-Frontmatter:

- `datenstand_iso` — Zeitpunkt des Laufs
- `quellen_inventur.hoch_konfidenz`, `mittel_konfidenz`, `niedrig_konfidenz` — Anzahl Annahmen pro Konfidenz-Stufe
- `quellen_inventur.branchen_benchmark_anteil_prozent` — wie viel Prozent der Annahmen aus reinen Branchen-Benchmarks stammen (Reproduzierbarkeits-Marker)

Wenn `branchen_benchmark_anteil_prozent > 50`: Auffälligkeit `quelle_branchen_benchmark_unsicher` setzen.
