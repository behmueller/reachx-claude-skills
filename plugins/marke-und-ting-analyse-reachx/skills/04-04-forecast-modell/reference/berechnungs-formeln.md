# Berechnungs-Formeln und Defaults

Dieses Dokument hält die Mathematik des `04-04-forecast-modell` zentral. Das Python-Skript `scripts/forecast-berechnung.py` implementiert genau diese Formeln. Wenn du die Mathematik anpasst, beide Stellen synchron halten.

## 1. Pro-Kanal-Funnel

### B2C-Standard (Lead-Funnel inaktiv)

```
sessions[k, m, s]  = volumen_basis[k, s]
                     * ramp_up_faktor(k, m, s)
                     * saisonalitaet[k, m]
                     * klick_anteil[k, s]
leads[k, m, s]     = sessions[k, m, s] * cr[k, s]
orders[k, m, s]    = leads[k, m, s]                       # B2C: leads = orders
umsatz[k, m, s]    = orders[k, m, s] * aov[s]
spend[k, m, s]     = spend_basis[k, s] * (ramp_up_faktor wenn aligned, sonst 1)
```

### B2B-Standard (Lead-Funnel aktiv)

```
sessions[k, m, s]  = (wie B2C)
leads[k, m, s]     = sessions[k, m, s] * cr[k, s]
qualifiziert[k, m, s] = leads[k, m, s] * cr_anfrage_qualifiziert[s]
angebote[k, m, s]  = qualifiziert[k, m, s] * cr_qualifiziert_zu_angebot[s]
orders[k, m, s]    = angebote[k, m, s] * cr_angebot_zu_auftrag[s]
umsatz[k, m, s]    = orders[k, m, s] * aov[s]
```

### Website-CRO als Hebel-Kanal

CRO ist kein eigener Volumen-Kanal sondern ein **Conversion-Rate-Uplift** auf andere Kanäle. Wenn `kanal_typ: hebel` im Schema:

```
fuer alle k in andere_kanaele:
    cr[k, s] = cr[k, s] * (1 + cro_uplift[s])     # uplift nur ab Monat cro_wirkungs_monat (Default Monat 4)
```

Default-Uplift-Bandbreite: worst 0,05 (5%), real 0,15 (15%), best 0,30 (30%) — im Schema überschreibbar.

## 2. Ramp-up-Funktionen

Der `ramp_up_faktor(k, m, s)` gibt einen Wert in [0, 1] zurück, der den Steady-State-Anteil in Monat `m` beschreibt.

### Linear

```
fuer monat m in [1, T]:
    f = start_anteil + (1 - start_anteil) * (m - 1) / (T - 1)
    return min(f, 1.0)
fuer m > T:
    return 1.0
```

Beispiel `start_anteil 0.10`, `T = 5`: M1 = 0.10, M2 = 0.325, M3 = 0.55, M4 = 0.775, M5 = 1.0.

### S-Kurve (Logistisch)

```
# Logistische Funktion: f(m) = L / (1 + exp(-k * (m - m0)))
# mit L = 1.0, m0 = T/2 (Wendepunkt), k = 4/T (Steilheit)
# normalisiert, sodass f(1) = start_anteil

import math
def s_curve(m, T, start_anteil):
    m0 = T / 2.0
    k = 4.0 / T
    raw = 1.0 / (1.0 + math.exp(-k * (m - m0)))
    raw1 = 1.0 / (1.0 + math.exp(-k * (1 - m0)))     # Wert bei m=1
    rawT = 1.0 / (1.0 + math.exp(-k * (T - m0)))     # Wert bei m=T
    # normalisiert auf [start_anteil, 1.0]
    normalized = start_anteil + (1 - start_anteil) * (raw - raw1) / (rawT - raw1)
    return min(max(normalized, start_anteil), 1.0) if m <= T else 1.0
```

Beispiel `start_anteil 0.10`, `T = 9`: M1=0.10, M2=0.12, M3=0.18, M4=0.30, M5=0.50, M6=0.70, M7=0.85, M8=0.94, M9=1.0.

### Sofort

```
fuer monat m == 1:
    return start_anteil          # Default 0.70
fuer m in [2, T]:
    return start_anteil + (1 - start_anteil) * (m - 1) / (T - 1)
fuer m > T:
    return 1.0
```

Beispiel `start_anteil 0.70`, `T = 2`: M1 = 0.70, M2 = 1.0, ab M3 = 1.0.

### Welches `T` gilt?

Pro Szenario das passende `monate_bis_steady_state_*`:

- `worst`-Szenario → `monate_bis_steady_state_max` (langsamer)
- `real`-Szenario → `monate_bis_steady_state_real`
- `best`-Szenario → `monate_bis_steady_state_min` (schneller)

## 3. Saisonalitäts-Defaults pro Branchen-Typ

Multiplikatoren pro Kalendermonat (Default = 1,0 neutral). Quelle: Branchen-Benchmarks REACHX-intern.

### b2c_ecommerce (Standard-Schwankungen mit Q4-Peak)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.85 | 0.80 | 0.95 | 1.00 | 1.05 | 1.00 | 0.90 | 0.90 | 1.05 | 1.10 | 1.30 | 1.40 |

### b2c_lokal_dienstleister (Sommer-Loch, Frühjahrs-Peak)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.85 | 0.95 | 1.10 | 1.15 | 1.10 | 0.95 | 0.80 | 0.80 | 1.05 | 1.10 | 1.05 | 0.85 |

### b2b_saas (relativ flach, Q1 Setup-Peak, Sommer-Loch, Q4 Budget-Peak)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.10 | 1.15 | 1.10 | 1.00 | 0.95 | 0.90 | 0.80 | 0.85 | 1.05 | 1.15 | 1.20 | 0.90 |

### b2b_industrie (Messe-Peaks Q1 und Q3, Sommer-Loch)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.10 | 1.15 | 1.20 | 1.10 | 1.00 | 0.85 | 0.75 | 0.85 | 1.10 | 1.15 | 1.05 | 0.80 |

### b2b_mittelstand_dienstleister (flach, leichter Sommer-Knick)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.00 | 1.05 | 1.05 | 1.00 | 0.95 | 0.95 | 0.85 | 0.90 | 1.05 | 1.10 | 1.05 | 0.95 |

### content_publisher (Schul-/Studium-Rhythmus)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.10 | 1.05 | 1.05 | 1.00 | 0.95 | 0.85 | 0.75 | 0.80 | 1.15 | 1.20 | 1.10 | 1.00 |

### marktplatz_plattform (Q4-Peak wie B2C plus Januar-Tief)

| Jan | Feb | Mar | Apr | Mai | Jun | Jul | Aug | Sep | Okt | Nov | Dez |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.80 | 0.85 | 1.00 | 1.00 | 1.05 | 1.00 | 0.95 | 0.95 | 1.05 | 1.10 | 1.25 | 1.40 |

### sonstige / unbekannt

Alle Multiplikatoren = 1.0 → flacher Verlauf. Im Phase-B-Output wird Auffälligkeit `konfidenz_niedrig_basis` gesetzt.

## 4. Aggregat-Berechnung

```
fuer monat m, szenario s:
    aggregat_roh[m, s] = sum(umsatz[k, m, s] fuer alle k)
    aggregat_korr[m, s] = aggregat_roh[m, s] * doppelzaehlung_faktor

    aggregat_leads_roh[m, s] = sum(leads[k, m, s] fuer alle k)
    aggregat_leads_korr[m, s] = aggregat_leads_roh[m, s] * doppelzaehlung_faktor

    aggregat_orders_roh[m, s] = sum(orders[k, m, s] fuer alle k)
    aggregat_orders_korr[m, s] = aggregat_orders_roh[m, s] * doppelzaehlung_faktor

    aggregat_spend[m, s] = sum(spend[k, m, s] fuer alle k)   # Spend wird NICHT doppelt gezaehlt
```

Doppelzählungs-Faktor (Standard 0,85) wird auf Outcome-Metriken (Leads/Orders/Umsatz) angewandt, nicht auf Spend (Spend ist immer additiv).

## 5. Auffälligkeits-Trigger (Schwellwert-Logik)

### `ziele_briefing_vs_abgeleitet_diskrepanz`

```
fuer jede ziel_quelle in ziel_inventur:
    if briefing_wert is None: continue
    abweichung = abs(briefing_wert - abgeleitet_real) / abgeleitet_real
    if abweichung > auffaelligkeits_trigger.ziele_briefing_vs_abgeleitet_diskrepanz_prozent / 100:
        trigger -> ziele_briefing_vs_abgeleitet_diskrepanz
```

### `kanal_dominanz_im_forecast`

```
aggregat_jahr_real = sum(aggregat_korr[m, "real"] fuer m in 1..12)
fuer jeden kanal k:
    kanal_anteil = sum(umsatz[k, m, "real"] fuer m in 1..12) / aggregat_jahr_real
    if kanal_anteil > auffaelligkeits_trigger.kanal_dominanz_im_forecast_prozent / 100:
        trigger -> kanal_dominanz_im_forecast (kanal k)
```

### `ramp_up_engpass`

```
if briefing.timeline_monate is None: skip
ergebnis_monat_real = min(m for m in 1..12 if aggregat_korr[m, "real"] >= 0.5 * steady_state)
if ergebnis_monat_real > briefing.timeline_monate:
    trigger -> ramp_up_engpass
```

### `worst_case_nicht_break_even`

```
jahres_umsatz_best = sum(aggregat_korr[m, "best"] fuer m in 1..12)
jahres_spend_real  = sum(aggregat_spend[m, "real"] fuer m in 1..12)
retainer_geschaetzt = 60000   # default 60k EUR/Jahr REACHX-Mid-Tier, im Schema ueberschreibbar
break_even = jahres_spend_real + retainer_geschaetzt
if jahres_umsatz_best < break_even:
    trigger -> worst_case_nicht_break_even
```

### `saisonalitaet_kollidiert_kampagnen_start`

```
start_monat = 1   # Monat 1 ist der Forecast-Start
if saisonalitaet.multiplikatoren[start_monat] < auffaelligkeits_trigger.saisonalitaet_kollision_multiplikator_schwelle:
    trigger -> saisonalitaet_kollidiert_kampagnen_start
```

### `spend_zu_hoch_fuer_geforderte_ziele`

```
fuer jeden paid-kanal k:
    branchen_spend_max = lookup(kanal_slug, branchen_typ).spend_real_obergrenze
    if spend_monat[k, "real"] > auffaelligkeits_trigger.spend_zu_hoch_faktor * branchen_spend_max:
        trigger -> spend_zu_hoch_fuer_geforderte_ziele
```

Branchen-Spend-Obergrenzen werden im Skript als Konstanten geführt:

| Branche | SEA-Spend max EUR/Mo | Meta-Spend max EUR/Mo | LinkedIn-Spend max EUR/Mo |
|---|---|---|---|
| b2c_ecommerce | 8000 | 6000 | 2000 |
| b2c_lokal_dienstleister | 3000 | 2000 | 1000 |
| b2b_saas | 6000 | 4000 | 8000 |
| b2b_industrie | 5000 | 2500 | 7000 |
| b2b_mittelstand_dienstleister | 4000 | 3000 | 5000 |
| content_publisher | 5000 | 6000 | 1500 |
| marktplatz_plattform | 10000 | 8000 | 3000 |
| sonstige | 5000 | 4000 | 4000 |

### `forecast_basis_first_party`

Die CR-Bandbreiten kommen mit einem Quellen-Tag aus `synthese/ziel-annahmen-schema.md` (gesetzt von `04-03-ziele-aus-potenzialen`). `04-04` baut keine eigene GA4-CR-Logik — es reicht den Tag durch.

```
cr_quellen = {kanal.cr_bandbreite.quelle fuer kanal in kanaele}
if cr_quellen & {"ga4_first_party", "sea_first_party"}:
    trigger -> forecast_basis_first_party
```

Bedeutung: Mindestens eine CR-Annahme stammt aus echten GA4-/Ads-Kunden-Daten statt Branchen-Schätzung → höhere Forecast-Konfidenz, als Realitäts-Beleg in der MTA-Story nutzbar.

### `ga4_datenqualitaet_unsicher`

```
if existiert(audits/ga4-first-party.md):
    belastbarkeit = ga4_first_party_md.frontmatter.belastbarkeit   # gruen | gelb | rot
    if belastbarkeit in ("gelb", "rot"):
        trigger -> ga4_datenqualitaet_unsicher
```

Bedeutung: GA4-Daten lagen vor, waren aber nicht voll belastbar. `04-03` hat die GA4-CR deshalb nicht (voll) übernommen, der Forecast nutzt (teilweise) Branchen-Benchmark statt der Kunden-CR. Handlungs-Empfehlung: im Kunden-Gespräch erden, GA4-Setup-Fix empfehlen. Fehlt `ga4-first-party.md` ganz, wird der Trigger nicht ausgewertet.

## 5b. GA4-Ist-Baseline-Plausibilisierung

Zusätzlich zum Plausibilitäts-Check gegen das Briefing: Wenn `audits/ga4-first-party.md` vorliegt, wird der Forecast-Start gegen die echte GA4-Ist-Baseline gestellt.

```
if existiert(audits/ga4-first-party.md):
    baseline = ga4_first_party_md.frontmatter.conversion_baseline
    ga4_sessions_ist  = baseline.sessions_pro_monat
    ga4_conversions_ist = baseline.conversions_pro_monat   # Conversions/Monat (Macro)

    forecast_m1_sessions = aggregat_korr[1, "real"]_sessions
    forecast_m1_orders   = aggregat_korr[1, "real"]_orders

    # Regel: Forecast-Start soll nicht unter dem GA4-Ist liegen
    # (Forecast = Marketing-Aufbau ZUSAETZLICH zur bestehenden Baseline)
    if forecast_m1_orders < ga4_conversions_ist * 0.90:
        ergebnis -> forecast_start_unter_ist  # Volumen-Basen / Ramp-up-Start zu konservativ
    else:
        ergebnis -> forecast_start_ueber_ist
```

Bei `belastbarkeit: gelb` oder `rot` wird der Vergleich nur als grobe Orientierung geführt und im Output entsprechend gekennzeichnet — keine harte Korrektur.

## 6. Monats-Labels

Wenn `meta.json.kickoff_datum` gesetzt: erstes Forecast-Monat = Kickoff-Monat + 1, dann fortlaufend.

```
from datetime import date
from dateutil.relativedelta import relativedelta

kickoff = date.fromisoformat(meta_json["kickoff_datum"])
for i in range(1, 13):
    monat = kickoff + relativedelta(months=i)
    label = monat.strftime("%Y-%m")
```

Wenn Kickoff null: Labels sind `M1` bis `M12`.

## 7. Konfidenz-Aggregation

Pro Zelle wird die Konfidenz aus den drei Faktoren (Volumen, CR, AOV) gebildet:

```
def aggr_konfidenz(volumen_konf, cr_konf, aov_konf):
    werte = {"hoch": 3, "mittel": 2, "niedrig": 1}
    summe = werte[volumen_konf] + werte[cr_konf] + werte[aov_konf]
    if summe >= 8: return "hoch"
    if summe >= 5: return "mittel"
    return "niedrig"
```
