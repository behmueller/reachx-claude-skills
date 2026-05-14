# Output-Schema: Ziele aus Potenzialen ableiten (Phase B)

Definiert die drei Pflicht-Outputs der Phase B:

- `synthese/ziele.md` — Aggregat-Markdown mit Szenario-Tabellen und Annahmen-Verweisen
- `synthese/ziele-aufschluesselung.csv` — Roh-Tabelle (Kanal × Szenario × Metrik)
- `reports/X-abgeleitete-ziele.html` — HTML-Report mit Szenario-Karten

## CSV-Schema (`synthese/ziele-aufschluesselung.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma.

### Spalten (in fester Reihenfolge)

```
kanal_slug,kanal_anzeigename,szenario,metrik,wert_min,wert_realistisch,wert_max,einheit,
annahme_cr_quelle,annahme_aov_quelle,annahme_volumen_quelle,konfidenz,
ramp_up_monate_min,ramp_up_monate_max,
zugehoerige_auffaelligkeiten,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `kanal_slug` | string (kebab-case) | ja | `seo`, `sea`, `meta-ads`, `linkedin-ads`, `local-seo`, `content`, `social-organisch`, `newsletter`, `website-cro`, `aggregat` |
| `kanal_anzeigename` | string | ja | Anzeigename für Excel-Lesbarkeit |
| `szenario` | enum | ja | `konservativ` \| `realistisch` \| `ambitioniert` \| `aggregat` |
| `metrik` | enum | ja | `traffic` \| `klicks` \| `anfragen` \| `qualifiziert_leads` \| `angebote` \| `orders` \| `umsatz` \| `conversion_rate` \| `aov` |
| `wert_min` | float | ja | unterer Wert der Bandbreite |
| `wert_realistisch` | float | ja | mittlerer Wert |
| `wert_max` | float | ja | oberer Wert |
| `einheit` | string | ja | `EUR` \| `besuche_pro_monat` \| `leads_pro_monat` \| `prozent` \| `eur_pro_order` |
| `annahme_cr_quelle` | string | nein | Quelle der CR-Annahme |
| `annahme_aov_quelle` | string | nein | Quelle der AOV-Annahme |
| `annahme_volumen_quelle` | string | nein | Quelle der Volumen-Annahme |
| `konfidenz` | enum | ja | `hoch` \| `mittel` \| `niedrig` |
| `ramp_up_monate_min` | int | nein | leer bei `kanal_slug: aggregat` |
| `ramp_up_monate_max` | int | nein | leer bei `kanal_slug: aggregat` |
| `zugehoerige_auffaelligkeiten` | string | nein | Pipe-Liste der Auffälligkeits-Typen, die diese Zeile triggern |
| `datenstand_iso` | ISO-8601 | ja | Datum des Skill-Laufs |

### Sortierung

1. `kanal_slug` (alphabetisch, `aggregat`-Zeilen ans Ende)
2. `szenario`: `konservativ` → `realistisch` → `ambitioniert` → `aggregat`
3. `metrik` in fester Reihenfolge: `traffic` → `klicks` → `anfragen` → `qualifiziert_leads` → `angebote` → `orders` → `umsatz` → `conversion_rate` → `aov`

## Markdown-Schema (`synthese/ziele.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 04-03-ziele-aus-potenzialen
phase: B
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  ziel_annahmen_schema: synthese/ziel-annahmen-schema.md
  kanal_chancen_md: synthese/kanal-chancen.md
  briefing: data/briefing.md       # null wenn nicht vorhanden
  kunde: data/kunde.md             # null wenn nicht vorhanden
  audits_genutzt:
    - audits/seo-cluster-zusammenfassung.md
    - audits/google-ads.md
    # ... alle die für die Volumen-Basis gelesen wurden

# === Lauf-Kontext ===
branchen_typ: BRANCHEN_SLUG
lauf_modus: abgeleitet_pur | plausibilitaets_check | hybrid

# === Aggregat (Steady State, Jahres-Beitrag) ===
aggregat:
  konservativ:
    traffic: 0
    leads: 0
    orders: 0
    umsatz_eur: 0
  realistisch:
    traffic: 0
    leads: 0
    orders: 0
    umsatz_eur: 0
  ambitioniert:
    traffic: 0
    leads: 0
    orders: 0
    umsatz_eur: 0
  doppelzaehlung_faktor_angewandt: 0.85
  aggregat_roh_umsatz_realistisch: 0   # vor Doppelzählungs-Korrektur, zur Transparenz
  top_kanal_anteil_realistisch_prozent: 0.0
  konfidenz_gesamt: hoch | mittel | niedrig

# === Pro Kanal die drei Szenarien ===
kanaele:
  - kanal_slug: seo
    kanal_anzeigename: SEO
    rang_aus_kanal_chancen: 1
    konservativ:
      traffic: 0
      anfragen: 0
      orders: 0
      umsatz_eur: 0
    realistisch:
      traffic: 0
      anfragen: 0
      orders: 0
      umsatz_eur: 0
    ambitioniert:
      traffic: 0
      anfragen: 0
      orders: 0
      umsatz_eur: 0
    annahmen_verweis:
      cr_quelle: branchen_benchmark
      aov_quelle: kunde_md_portfolio
      volumen_quelle: audits/seo-cluster-zusammenfassung.md
    ramp_up_monate_min: 6
    ramp_up_monate_max: 12
    konfidenz: hoch
    zugehoerige_auffaelligkeiten: []
  
  # ... weitere Kanäle

# === Plausibilitäts-Check (nur bei plausibilitaets_check / hybrid) ===
plausibilitaets_check:
  aktiv: true | false
  vergleiche:
    - kunden_kpi_typ: leads_pro_monat
      kunden_kpi_wert: 50
      kunden_kpi_quelle_zeile: "Briefing-Body Z. 24"
      bandbreite_konservativ: 25
      bandbreite_realistisch: 60
      bandbreite_ambitioniert: 110
      ergebnis: passt | unrealistisch_hoch | unrealistisch_niedrig
      kommentar: "Kunden-Wert liegt im realistisch-Bereich"

# === Auffälligkeiten (min. 6) ===
auffaelligkeiten:
  - typ: enum    # kunde_ziel_unrealistisch_hoch | kunde_ziel_unrealistisch_niedrig | kanal_dominiert_ergebnis | aov_unklar | ramp_up_diskrepanz_zu_briefing_timeline | lead_zu_kunde_unklar_b2b | quelle_branchen_benchmark_unsicher | briefing_kpi_passt | sonstige
    titel: string
    beschreibung: "1-2 Sätze"
    relevanz: hoch | mittel | niedrig
    handlungs_empfehlung: "konkrete Aktion"
    betroffene_kanaele: [seo, sea]

# === Quellen-Inventur (für Reproduzierbarkeit) ===
quellen_inventur:
  hoch_konfidenz_annahmen: 0
  mittel_konfidenz_annahmen: 0
  niedrig_konfidenz_annahmen: 0
  branchen_benchmark_anteil_prozent: 0.0
  audit_daten_anteil_prozent: 0.0
  briefing_aussage_anteil_prozent: 0.0

# === Vorbereitung für 04-04-forecast-modell ===
forecast_vorbereitung:
  uebernahme_in_forecast_schema: [aov, cr_bandbreiten, lead_funnel, ramp_up]
  verfeinerung_im_forecast: [saisonalitaet, monats_kurve]
---

# Abgeleitete Ziele: KUNDENNAME

## Übersicht

3-5 Sätze: Lauf-Modus, Branchen-Typ, Anzahl Kanäle, Aggregat-Bandbreite (konservativ-ambitioniert EUR pro Jahr), Top-Kanal-Beitrag, Konfidenz-Verteilung.

## Aggregat — Drei Szenarien

| Metrik | Konservativ | Realistisch | Ambitioniert |
|---|---|---|---|
| Traffic / Reichweite | X | X | X |
| Anfragen / Leads | X | X | X |
| Orders / Aufträge | X | X | X |
| Umsatz-Beitrag | X EUR | X EUR | X EUR |

> Werte sind Jahres-Beiträge im Steady State (nach Ramp-up von 6-12 Monaten je nach Kanal-Mix). Doppelzählungs-Faktor: 0,XX angewandt (Roh-Summe ohne Korrektur: X EUR).

**Top-Kanal-Beitrag** (realistisches Szenario): KANAL — XX% am Aggregat

## Pro Kanal

### SEO · Rang 1 in kanal-chancen.md

| Metrik | Konservativ | Realistisch | Ambitioniert |
|---|---|---|---|
| Traffic / Monat | X | X | X |
| Orders / Monat | X | X | X |
| Umsatz / Jahr | X EUR | X EUR | X EUR |

- **Annahmen-Verweis**: CR aus `branchen_benchmark`, AOV aus `data/kunde.md` Portfolio (150 EUR realistisch), Volumen aus `audits/seo-cluster-zusammenfassung.md` (kumuliertes Volumen Top-3-Cluster: 11.400 / Monat)
- **Ramp-up**: 6-12 Monate
- **Konfidenz**: hoch
- **Auffälligkeiten**: kanal_dominiert_ergebnis (siehe unten)

(... weitere Kanäle in gleicher Struktur)

## Annahmen-Tabelle

| Annahme | Wert | Quelle | Konfidenz |
|---|---|---|---|
| AOV (realistisch) | 150 EUR | data/kunde.md Portfolio | hoch |
| SEO-CR konservativ | 0,8% | branchen_benchmark | mittel |
| ... | ... | ... | ... |

> Quellen-Inventur: X% aus Audit-Daten, X% aus Branchen-Benchmark, X% aus Briefing-Aussagen, X% aus Skill-Schätzung.

## Plausibilitäts-Check gegen Briefing-KPIs

(Nur wenn Lauf-Modus `plausibilitaets_check` oder `hybrid`)

| Kunden-KPI | Briefing-Wert | Konservativ | Realistisch | Ambitioniert | Ergebnis |
|---|---|---|---|---|---|
| Leads/Monat | 50 | 25 | 60 | 110 | passt |
| Umsatz/Jahr | 250.000 EUR | 180.000 | 320.000 | 580.000 | passt |

Kommentar pro Vergleich.

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### Auffälligkeit 1 — Titel

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: konkret

**Betroffene Kanäle**: liste

(weitere Auffälligkeiten, mind. 6 insgesamt)

## Datenbasis

**Audits zur Verfügung** (X von Y):

- gelesen `audits/seo-cluster-zusammenfassung.md`
- gelesen `audits/google-ads.md`
- nicht gelesen `audits/local-gmb.md` — Local-Pack-Annahmen aus Branchen-Benchmark

**Audit-Coverage** (aus `kanal-chancen.md`): XX% → Modus `voll | reduced | duenn`

## Vorbereitung für 04-04-forecast-modell

Empfohlene Übernahme ins Forecast-Schema:

- AOV-Bandbreite (1:1)
- CR-Bandbreiten pro Kanal (1:1)
- Lead-Funnel-Stufen (B2B, 1:1)
- Ramp-up-Phasen (1:1)

Verfeinerung im Forecast nötig:

- Saisonalität pro Kanal (Monats-Kurve)
- Wachstums-Funktion innerhalb des Ramp-up (linear / s-curve)
- Optional: pessimistische / optimistische Wachstums-Pfade

## Folge-Skills

- **`04-04-forecast-modell`** (Schema-vor-Lauf) — verfeinert die Annahmen und rechnet das 12-Monats-Modell mit Ramp-up
- **`04-05-90-tage-plan`** — leitet konkrete Maßnahmen für die Top-3-Kanäle ab
```

## HTML-Report-Struktur

Im `{{MAIN_CONTENT}}`-Bereich:

### 1. Stat-Strip

```html
<section class="stat-strip">
  <div class="stat"><span class="label">Aggregat realistisch (EUR/Jahr)</span><span class="value">320.000</span></div>
  <div class="stat"><span class="label">Bandbreite (konservativ-ambitioniert)</span><span class="value">180k-580k</span></div>
  <div class="stat"><span class="label">Top-Kanal-Anteil</span><span class="value">SEO 42%</span></div>
  <div class="stat"><span class="label">Konfidenz</span><span class="value">hoch</span></div>
</section>
```

### 2. Drei Szenario-Karten nebeneinander

Drei `.summary-card`s mit den Szenario-Aggregaten:

```html
<div class="suggestion">
  <h3>Konservativ</h3>
  <p>Umsatz/Jahr: 180.000 EUR</p>
  <ul>
    <li>Traffic: X</li>
    <li>Leads: X</li>
    <li>Orders: X</li>
  </ul>
</div>
<div class="suggestion">
  <h3>Realistisch</h3>
  <p>Umsatz/Jahr: 320.000 EUR</p>
  ...
</div>
<div class="suggestion">
  <h3>Ambitioniert</h3>
  <p>Umsatz/Jahr: 580.000 EUR</p>
  ...
</div>
```

### 3. Pro-Kanal-Details

`<details class="skill" data-status="...">` pro Kanal mit Szenario-Tabelle und Annahmen-Verweis.

### 4. Annahmen-Tabelle

`<table class="data">` mit allen Annahmen, Quellen, Konfidenzen.

### 5. Plausibilitäts-Check

Nur wenn aktiv: prominente `.summary-card` (grün bei `passt`, gelb bei `unrealistisch_niedrig`, rot bei `unrealistisch_hoch`).

### 6. Auffälligkeiten

`<details>`-Blöcke, gruppiert nach Relevanz.

### 7. Datenbasis-Footer

Welche Audits da waren, welche fehlten — als kleine Tabelle. Wenn Modus `duenn`, prominent oben als Warnung in `.summary-card` mit roter Border.

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jeder Kanal hat genau drei Szenarien (konservativ, realistisch, ambitioniert)
2. Pro Szenario gilt: `konservativ_wert <= realistisch_wert <= ambitioniert_wert` für alle Metriken
3. Aggregat-Werte sind konsistent mit Kanal-Summen (innerhalb Doppelzählungs-Faktor Toleranz ±2%)
4. Jede Annahme im Output hat ein `quelle`-Feld
5. `auffaelligkeiten` hat **mindestens 6 Einträge**
6. Jede Auffälligkeit hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`, `betroffene_kanaele`
7. Wenn `lauf_modus: plausibilitaets_check` oder `hybrid` und Briefing-KPIs vorhanden: `plausibilitaets_check.vergleiche` ist nicht leer
8. `quellen_inventur` summiert über die Konfidenz-Felder zur Gesamt-Anzahl Annahmen

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `04-04-forecast-modell`

Liest aus `ziele.md` Frontmatter:

- `aggregat.realistisch.*` als Steady-State-Werte
- `kanaele[].konservativ/realistisch/ambitioniert` als Szenario-Basis
- `kanaele[].ramp_up_monate_*` als Monats-Kurven-Endpunkt
- `forecast_vorbereitung.uebernahme_in_forecast_schema` als Hinweis-Liste

Liest aus `ziel-annahmen-schema.md` Frontmatter:

- AOV-Bandbreite, CR-Bandbreiten, Lead-Funnel-Stufen → werden im Forecast-Annahmen-Schema verfeinert

### `04-05-90-tage-plan`

Liest aus `ziele.md`:

- Top-Kanal aus `aggregat.top_kanal_anteil_realistisch_prozent` → erster 90-Tage-Block
- Auffälligkeiten mit `typ: ramp_up_diskrepanz_zu_briefing_timeline` → Hybrid-Strategie-Block

### `05-01-mta-slide-bausteine`

- Drei Szenario-Karten direkt als Forecast-Slide-Baustein
- Annahmen-Tabelle als Anhangs-Slide
- Plausibilitäts-Check als Story-Slide (Kunden-Erwartung vs. Daten)
