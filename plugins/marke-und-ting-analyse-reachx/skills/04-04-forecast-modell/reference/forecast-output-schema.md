# Output-Schema: Forecast-Modell (Phase B)

Definiert die vier Pflicht-Outputs:

- `synthese/forecast.md` — Aggregat-Markdown mit Szenarien-Tabelle und Annahmen-Transparenz
- `synthese/forecast.csv` — Roh-Tabelle (Kanal × Monat × Szenario × KPI)
- `synthese/forecast.xlsx` — Excel mit drei Sheets (roh, pivot, annahmen)
- `reports/X-forecast.html` — HTML-Report mit Sparklines und SVG-Aggregat-Chart

## CSV-Schema (`synthese/forecast.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma.

### Spalten (in fester Reihenfolge)

```
kanal_slug,kanal_anzeigename,monat_index,monat_label,szenario,
sessions,leads,qualifizierte_leads,orders,umsatz_eur,spend_eur,
cr_angewandt,aov_angewandt,ramp_up_faktor,saisonalitaet_multiplikator,
quelle_volumen,quelle_cr,quelle_aov,quelle_spend,quelle_ziel_overlay,
konfidenz,zugehoerige_auffaelligkeiten,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `kanal_slug` | string (kebab-case) | ja | z. B. `seo`, `sea`, `meta-ads`, `linkedin-ads`, `aggregat` |
| `kanal_anzeigename` | string | ja | Anzeigename für Excel-Lesbarkeit |
| `monat_index` | int 1-12 | ja | sequenziell |
| `monat_label` | string | ja | z. B. `2026-07` oder `M3` |
| `szenario` | enum | ja | `worst` \| `real` \| `best` \| `aggregat` |
| `sessions` | float | ja | Klicks bzw. Sessions vom Kanal pro Monat |
| `leads` | float | ja | Top-Funnel-Conversion (Form-Submit, Anfrage) |
| `qualifizierte_leads` | float | nein | leer bei B2C, Pflicht bei B2B |
| `orders` | float | ja | finale Conversion (Auftrag oder Order) |
| `umsatz_eur` | float | ja | orders × AOV |
| `spend_eur` | float | ja | 0 bei organischen Kanälen |
| `cr_angewandt` | float | ja | effektive Conversion-Rate (sessions → orders), inkl. Funnel-Stufen |
| `aov_angewandt` | float | ja | AOV in EUR |
| `ramp_up_faktor` | float [0,1] | ja | Anteil am Steady State in dem Monat |
| `saisonalitaet_multiplikator` | float | ja | Default 1,0 |
| `quelle_volumen` | string | ja | z. B. `audits/seo-cluster-zusammenfassung.md` |
| `quelle_cr` | string | ja | z. B. `abgeleitete_ziele` |
| `quelle_aov` | string | ja | z. B. `data/kunde.md` |
| `quelle_spend` | string | ja | z. B. `branchen_benchmark` oder `briefing_aussage` |
| `quelle_ziel_overlay` | string | ja | `abgeleitete_ziele` (Default) oder `briefing_aussage` falls Vorrang im Schema gesetzt |
| `konfidenz` | enum | ja | `hoch` \| `mittel` \| `niedrig` |
| `zugehoerige_auffaelligkeiten` | string | nein | Pipe-Liste der Auffälligkeits-Typen |
| `datenstand_iso` | ISO-8601 | ja | Datum des Skill-Laufs |

### Sortierung

1. `kanal_slug` (alphabetisch, `aggregat`-Zeilen ans Ende)
2. `monat_index` aufsteigend
3. `szenario`: `worst` → `real` → `best` → `aggregat`

### Größen-Erwartung

`Anzahl Kanaele × 12 Monate × 3 Szenarien + 12 × 3 Aggregat-Zeilen` = z. B. bei 5 Kanälen: 5 × 12 × 3 + 36 = 216 Zeilen.

## Excel-Schema (`synthese/forecast.xlsx`)

Drei Sheets:

### Sheet `roh`

Identisch mit CSV. Header-Zeile bold. Spaltenbreiten autofit. Zahlen mit Tausender-Separator wo > 1000.

### Sheet `pivot`

Erzeugt via `pandas.pivot_table`:

```python
pd.pivot_table(
    df_roh,
    index=["kanal_slug", "kanal_anzeigename"],
    columns=["monat_index", "szenario"],
    values=["umsatz_eur", "leads", "orders", "spend_eur"],
    aggfunc="sum"
)
```

Plus eine Aggregat-Zeile pro Monat (Summe über alle Kanäle).

### Sheet `annahmen`

Annahmen-Transparenz als flache Tabelle:

| achse | kanal_slug | szenario | wert | einheit | quelle | konfidenz |
|---|---|---|---|---|---|---|
| aov | (alle) | worst | 120 | EUR | kunde_md_portfolio | hoch |
| aov | (alle) | real | 150 | EUR | kunde_md_portfolio | hoch |
| aov | (alle) | best | 200 | EUR | kunde_md_portfolio | hoch |
| cr | seo | worst | 0.008 | prozent | abgeleitete_ziele | hoch |
| cr | seo | real | 0.015 | prozent | abgeleitete_ziele | hoch |
| cr | seo | best | 0.030 | prozent | abgeleitete_ziele | hoch |
| volumen_basis | seo | worst | 8000 | suchanfragen | audits/seo-cluster-zusammenfassung.md | hoch |
| ramp_up_monate | seo | (alle) | 9 | monate | abgeleitete_ziele | hoch |
| spend_monat | sea | real | 4000 | EUR | branchen_benchmark | mittel |
| saisonalitaet | (alle) | jan | 0.85 | multiplikator | branchen_benchmark | mittel |

## Markdown-Schema (`synthese/forecast.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 04-04-forecast-modell
phase: B
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  forecast_annahmen_schema: synthese/forecast-schema.md
  abgeleitete_ziele: synthese/ziele.md
  ziel_annahmen_schema: synthese/ziel-annahmen-schema.md
  kanal_chancen: synthese/kanal-chancen.md
  briefing: data/briefing.md       # null wenn nicht vorhanden

# === Lauf-Kontext ===
branchen_typ: BRANCHEN_SLUG
lauf_modus: abgeleitet_pur | plausibilitaets_check | hybrid
kickoff_datum: 2026-06-01
monats_labels:
  - "2026-07"
  - "2026-08"
  # ... 12 Eintraege

# === 12-Monats-Aggregat ===
aggregat_12_monate:
  worst:
    umsatz_eur: 180000
    leads: 240
    orders: 720
    spend_eur: 30000
  real:
    umsatz_eur: 320000
    leads: 480
    orders: 1280
    spend_eur: 48000
  best:
    umsatz_eur: 580000
    leads: 800
    orders: 2320
    spend_eur: 78000
  doppelzaehlung_faktor_angewandt: 0.85
  steady_state_monat_real: 6
  top_kanal_anteil_real_prozent: 42.0
  top_kanal_slug: seo
  konfidenz_gesamt: hoch | mittel | niedrig

# === Quartal-Aggregat (zur Konvenienz) ===
aggregat_pro_quartal:
  q1:
    real_umsatz_eur: 35000
    real_leads: 60
  q2:
    real_umsatz_eur: 70000
    real_leads: 110
  q3:
    real_umsatz_eur: 90000
    real_leads: 150
  q4:
    real_umsatz_eur: 125000
    real_leads: 160

# === Pro Kanal Aggregat ===
kanaele:
  - kanal_slug: seo
    kanal_anzeigename: SEO
    jahr_umsatz_worst: 60000
    jahr_umsatz_real: 134000
    jahr_umsatz_best: 280000
    anteil_real_prozent: 42.0
    steady_state_monat: 9
    konfidenz: hoch
    auffaelligkeiten: []
  # ... weitere Kanaele

# === Plausibilitaets-Check ===
plausibilitaets_check:
  aktiv: true
  vergleiche:
    - kpi: leads_pro_monat
      briefing_wert: 50
      real_min_im_jahr: 28
      real_max_im_jahr: 62
      real_durchschnitt: 45
      ergebnis: passt | unrealistisch_hoch | unrealistisch_niedrig
      kommentar: "Briefing-Wert liegt im Real-Korridor"

# === Auffaelligkeiten (min. 6) ===
auffaelligkeiten:
  - typ: enum
    titel: string
    beschreibung: "1-2 Saetze"
    relevanz: hoch | mittel | niedrig
    handlungs_empfehlung: "konkrete Aktion"
    betroffene_kanaele: [seo, sea]

# === Vorbereitung fuer Folge-Skills ===
forecast_outputs_fuer_folge_skills:
  fuer_90_tage_plan:
    top_kanal_slug: seo
    top_kanal_steady_state_monat: 9
    empfehlung: "30/60/90-Tage-Meilensteine an SEO-Ramp-up koppeln"
  fuer_retainer_kalkulator:
    durchschnittlicher_spend_real_pro_monat: 4000
    geschaetzter_aufwand_organisch_stunden_pro_monat: 30
---

# Forecast: KUNDENNAME

## Übersicht

3-5 Sätze: Lauf-Modus, Branchen-Typ, 12-Monats-Aggregat-Bandbreite, Steady-State-Monat, Top-Kanal-Beitrag.

## 12-Monats-Aggregat — Drei Szenarien

### Umsatz pro Monat (EUR)

| Monat | Worst | Real | Best |
|---|---|---|---|
| 2026-07 | 1.200 | 3.500 | 7.800 |
| 2026-08 | 2.000 | 5.400 | 11.200 |
| ... | ... | ... | ... |
| 2027-06 | 28.500 | 48.000 | 78.000 |
| **Jahr gesamt** | **180.000** | **320.000** | **580.000** |

### Leads pro Monat

| Monat | Worst | Real | Best |
|---|---|---|---|
| ... | ... | ... | ... |

> Werte sind nach Doppelzählungs-Korrektur (Faktor 0,85). Roh-Summen siehe `forecast.csv` und Excel-Sheet `pivot`.

**Top-Kanal-Beitrag** (Real-Szenario, Jahr): KANAL — XX% am 12-Monats-Aggregat-Umsatz

## Pro Kanal

### SEO · Rang 1 aus kanal-chancen.md

| Monat | Worst | Real | Best |
|---|---|---|---|
| ... | ... | ... | ... |

- **Annahmen-Verweis**: Volumen aus `audits/seo-cluster-zusammenfassung.md` (11.400 real), CR aus `abgeleitete_ziele` (1,5% real), AOV aus `data/kunde.md` (150 EUR real)
- **Ramp-up**: s_curve über 9 Monate (real), Steady State ab M10
- **Saisonalität**: B2C-E-Commerce-Default mit Q4-Peak
- **Konfidenz**: hoch
- **Auffälligkeiten**: kanal_dominanz_im_forecast (siehe unten)

(... weitere Kanäle in gleicher Struktur)

## Annahmen-Transparenz

Tabelle mit allen Annahmen, deren Quellen und Konfidenzen. Identisch zum Excel-Sheet `annahmen`.

| Achse | Kanal | Worst | Real | Best | Quelle | Konfidenz |
|---|---|---|---|---|---|---|
| AOV (EUR) | — | 120 | 150 | 200 | data/kunde.md | hoch |
| SEO-CR | seo | 0,8% | 1,5% | 3,0% | abgeleitete_ziele | hoch |
| SEO-Volumen (Monat) | seo | 8.000 | 11.400 | 16.000 | audits/seo-cluster-zusammenfassung.md | hoch |
| ... | ... | ... | ... | ... | ... | ... |

## Plausibilitäts-Check gegen Briefing-KPIs

(Nur wenn Briefing bezifferte KPIs hat)

| Briefing-KPI | Briefing-Wert | Real (min/max im Jahr) | Real (Durchschnitt) | Ergebnis |
|---|---|---|---|---|
| Leads/Monat | 50 | 28 – 62 | 45 | passt |
| Umsatz/Jahr | 250.000 EUR | — | 320.000 | unrealistisch_niedrig (Kunde unterschätzt sein Potenzial) |

Kommentar pro Vergleich mit Handlungs-Empfehlung.

## Diskrepanz-Tabelle: Briefing vs. abgeleitete Ziele

| KPI | Briefing-Wert | Abgeleitet Worst | Abgeleitet Real | Abgeleitet Best | Diskrepanz-Typ | Vorrang im Forecast |
|---|---|---|---|---|---|---|
| leads_pro_monat | 50 | 25 | 60 | 110 | passt | abgeleitete_ziele |
| umsatz_pro_jahr | 250.000 | 180.000 | 320.000 | 580.000 | briefing_niedriger | abgeleitete_ziele |

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### Auffälligkeit 1 — Titel

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: konkret

**Betroffene Kanäle**: liste

(weitere Auffälligkeiten, mind. 6 insgesamt)

## Datenbasis

- forecast-annahmen-schema bestaetigt am: ISO
- Audit-Daten genutzt: liste
- Konfidenz-Verteilung: X% hoch / Y% mittel / Z% niedrig

## Vorbereitung für Folge-Skills

### Für `04-05-90-tage-plan`

- Top-Kanal `seo` erreicht Steady State in Monat 9 — 90-Tage-Plan koppelt Meilensteine an SEO-Ramp-up-Kurve
- Auffälligkeit `ramp_up_engpass` triggert Hybrid-Empfehlung mit SEA als Sofort-Hebel

### Für `04-06-retainer-kalkulator`

- Durchschnittlicher Real-Spend: 4.000 EUR/Monat über Paid-Kanäle
- Organische Kanäle: ca. 30-40 Mitarbeiter-Stunden/Monat (SEO/Content)

## Folge-Skills

- **`04-05-90-tage-plan`** — leitet die konkreten Maßnahmen aus den Top-Kanälen ab
- **`04-06-retainer-kalkulator`** (Schema-vor-Lauf) — berechnet Retainer-Empfehlung auf Basis des Forecast-Spends plus Aufwand
```

## HTML-Report-Struktur

Im `{{MAIN_CONTENT}}`-Bereich:

### 1. Stat-Strip

```html
<section class="stat-strip">
  <div class="stat"><span class="label">12-Monats-Aggregat Real (EUR)</span><span class="value">320.000</span></div>
  <div class="stat"><span class="label">Bandbreite (Worst-Best)</span><span class="value">180k-580k</span></div>
  <div class="stat"><span class="label">Top-Kanal-Anteil</span><span class="value">SEO 42%</span></div>
  <div class="stat"><span class="label">Steady-State erreicht</span><span class="value">Monat 9</span></div>
</section>
```

### 2. Aggregat-Chart (SVG inline)

Eine SVG-Grafik mit drei Linien (worst/real/best) über 12 Monate. Y-Achse Umsatz, X-Achse Monate. Höhe ca. 280px, Breite 100%. Achsen-Beschriftung, Legende, Y-Achsen-Marker bei den Quartalen.

### 3. Pro-Kanal-Details mit Sparkline

`<details class="skill" data-status="...">` pro Kanal. In der Summary die Mini-Sparkline (SVG inline, 40px Höhe, 200px Breite, drei dünne Linien). Beim Auf-Klappen: Monats-Tabelle plus Annahmen-Verweis.

### 4. Kanal-Verteilungs-Donut

SVG-Donut-Chart (Real-Szenario, Anteil am 12-Monats-Aggregat-Umsatz). Inline-SVG, Größe ca. 240px.

### 5. Annahmen-Tabelle

`<table class="data">` identisch zum Markdown.

### 6. Plausibilitäts-Check

`.summary-card` pro Vergleich. Grüne Border bei `passt`, gelbe bei `unrealistisch_niedrig`, rote bei `unrealistisch_hoch`.

### 7. Auffälligkeiten

Als `<details>`-Blöcke gruppiert nach Relevanz.

### 8. Datenbasis-Footer

Annahmen-Schema-Status, Quellen-Inventur als kleine Tabelle.

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jeder Kanal hat genau 12 Monate × 3 Szenarien Roh-Zeilen
2. Pro Zeile gilt `worst <= real <= best` für umsatz, leads, orders (Toleranz ±1% wegen Rundung)
3. Aggregat-Zeilen sind konsistent mit Kanal-Summen × Doppelzählungs-Faktor (Toleranz ±2%)
4. Jede Zeile hat alle fünf `*_quelle`-Felder
5. `auffaelligkeiten` hat **mindestens 6 Einträge**
6. Jede Auffälligkeit hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`, `betroffene_kanaele`
7. `aggregat_12_monate.steady_state_monat_real` ist in [1, 12]
8. `monats_labels` hat genau 12 Einträge
9. Excel-Sheet `roh`, `pivot`, `annahmen` alle vorhanden und nicht leer

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `04-05-90-tage-plan`

Liest aus `forecast.md` Frontmatter:

- `aggregat_12_monate.top_kanal_slug` → erster 90-Tage-Block
- `aggregat_12_monate.steady_state_monat_real` → Meilenstein-Setzung
- Auffälligkeiten mit `typ: ramp_up_engpass` → Hybrid-Strategie-Block
- `forecast_outputs_fuer_folge_skills.fuer_90_tage_plan` → direkt als Maßnahmen-Liste

### `04-06-retainer-kalkulator`

Liest aus `forecast.md` Frontmatter und CSV:

- Durchschnittlicher Real-Spend pro Monat über Paid-Kanäle → Spend-Komponente
- Organische Kanäle mit Ramp-up-Funktion → Aufwand-Schätzung in Stunden
- `forecast_outputs_fuer_folge_skills.fuer_retainer_kalkulator` → direkt als Input

### `05-01-mta-slide-bausteine`

- Aggregat-Chart als Slide-Bild (Export aus HTML-SVG)
- Top-3-Kanal-Tabelle als Slide-Tabelle
- Annahmen-Transparenz als Anhangs-Slide
- Plausibilitäts-Check als Story-Slide (Kunden-Erwartung vs. Forecast)
