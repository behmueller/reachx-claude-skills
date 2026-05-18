# Output-Schema: Kanal-Chancen-Analyse

Definiert die drei Pflicht-Outputs:

- `synthese/kanal-chancen.md` — Aggregat-Markdown mit Top-3-Empfehlungen + strategischer Story
- `synthese/kanal-chancen.csv` — Eine Zeile pro Kanal mit allen Achsen-Scores
- `reports/10-kanal-chancen.html` — HTML-Report mit Score-Heatmap

## CSV-Schema (`synthese/kanal-chancen.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma.

### Spalten (in fester Reihenfolge)

```
kanal_slug,kanal_anzeigename,
potenzial_score,potenzial_konfidenz,
aufwand_score,aufwand_konfidenz,
briefing_fit_score,briefing_fit_konfidenz,
kunden_reife_score,kunden_reife_roh,kunden_reife_konfidenz,
branchen_fit_score,branchen_fit_konfidenz,branchen_fit_overrides,
chancen_score,chancen_score_konfidenz,
rang,
auffaelligkeiten_typen,
audit_inputs_verfuegbar,audit_inputs_fehlt,
empfohlene_naechste_aktion,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `kanal_slug` | string (kebab-case) | ja | z. B. `seo`, `sea`, `meta-ads`, `linkedin-ads`, `local-seo`, `content`, `instagram-organisch`, `tiktok-organisch`, `linkedin-organisch`, `pinterest-organisch`, `youtube-organisch`, `website-cro` |
| `kanal_anzeigename` | string | ja | Anzeigename für Excel-Lesbarkeit |
| `potenzial_score` | int 0-100 / `skip` | ja | `skip` wenn Kanal ausgeschlossen (z. B. Local-SEO bei nicht-lokal-relevantem Kunden) |
| `potenzial_konfidenz` | enum | ja | `hoch | mittel | niedrig | skip` |
| `aufwand_score` | int 0-100 / `skip` | ja | invertiert: hoch = niedriger Aufwand |
| `aufwand_konfidenz` | enum | ja | analog |
| `briefing_fit_score` | int 0-100 / `skip` | ja | |
| `briefing_fit_konfidenz` | enum | ja | analog |
| `kunden_reife_score` | int 0-100 / `skip` | ja | nicht-monoton — siehe Formel-Datei |
| `kunden_reife_roh` | int 0-100 / leer | nein | Hilfsgröße für Transparenz |
| `kunden_reife_konfidenz` | enum | ja | |
| `branchen_fit_score` | int 0-100 / `skip` | ja | |
| `branchen_fit_konfidenz` | enum | ja | |
| `branchen_fit_overrides` | string | nein | Komma-Liste der angewandten Override-Regeln, z. B. `aktivitaets_override|saettigungs_override` |
| `chancen_score` | int 0-100 / `skip` | ja | finaler Score |
| `chancen_score_konfidenz` | enum | ja | |
| `rang` | int / `skip` | ja | Position im Ranking (1 = höchster Score) |
| `auffaelligkeiten_typen` | string | nein | Pipe-getrennte Liste der Auffälligkeits-Typen, die diesen Kanal betreffen |
| `audit_inputs_verfuegbar` | string | ja | Pipe-Liste der Audit-Dateien, die für diesen Kanal gelesen wurden |
| `audit_inputs_fehlt` | string | nein | Pipe-Liste der erwarteten Audit-Dateien, die fehlten |
| `empfohlene_naechste_aktion` | string | ja | 1 Satz, konkrete nächste Aktion für den Strategen |
| `datenstand_iso` | ISO-8601 | ja | Datum des Skill-Laufs |

### Sortierung

1. `rang` aufsteigend (Top-Kanal zuerst)
2. `skip`-Einträge ans Ende
3. Tiebreaker: alphabetisch nach `kanal_slug`

### Größen-Grenze

Eine Zeile pro konfiguriertem Kanal (Basis-Set 12 Kanäle; mit GEO, Reddit und Facebook-organisch bis zu 15 Kanäle) plus ggf. Skip-Zeilen. Kein Hard-Cap nötig.

### Quellen- und Konfidenz-Vermerk (First-Party)

Die Konfidenz-Spalten `potenzial_konfidenz` und `kunden_reife_konfidenz` spiegeln verbindlich die Datenherkunft wider:

- Sind `potenzial_score` bzw. `kunden_reife_score` aus First-Party-Ist-Daten (`ga4-first-party.md` Block `kanal_wertigkeit`, `sea-first-party.md`) abgeleitet, folgt die Konfidenz dem `belastbarkeit`-Gate von GA4 — `gruen` → `hoch`, `gelb` → `mittel`, `rot` → `niedrig` (Zahlen nur Orientierung).
- Ohne First-Party-Daten gilt die bisherige Konfidenz-Logik aus Branchen-Defaults/Third-Party-Audits (siehe `chancen-score-formel.md`).
- Die genutzte First-Party-Quelle wird pro Kanal in `audit_inputs_verfuegbar` mitgeführt (z. B. `audits/ga4-first-party.md`, `audits/sea-first-party.md`), sodass im CSV nachvollziehbar bleibt, welche Achse messbar statt geschätzt ist.

## Markdown-Schema (`synthese/kanal-chancen.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 04-02-kanal-chancen-analyse
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  briefing: data/briefing.md            # null wenn nicht vorhanden
  kunde: data/kunde.md                  # null wenn nicht vorhanden
  positionierung: synthese/positionierung.md   # null wenn nicht vorhanden
  audits_verfuegbar:
    - audits/seo-cluster-zusammenfassung.md
    - audits/google-ads.md
    - audits/web-tech-tracking.md
    # ... (alle gefundenen)
  audits_fehlt:
    - audits/meta-ads.md
    - audits/local-gmb.md
    # ... (alle erwarteten aber nicht vorhandenen)

# === Input-Staleness (contracts.md Abschnitt 12) ===
# Liste aller gelesenen Audit-/Synthese-Inputs mit ihrem generiert_am-Stempel.
# Nachgelagerte Synthese-Skills prüfen damit, ob kanal-chancen.md stale ist.
basis_inputs:
  - datei: audits/seo-cluster-zusammenfassung.md
    generiert_am: <ISO-8601>
  - datei: audits/google-ads.md
    generiert_am: <ISO-8601>
  # ... (jeder gelesene Input mit Stempel)

# === First-Party-Datenlage ===
# Vermerkt, ob die First-Party-Ist-Daten in die Achsen-Scores eingeflossen sind.
# Steuert die Konfidenz von potenzial_score und kunden_reife_score.
first_party:
  ga4_vorhanden: <true | false>
  ga4_belastbarkeit: <gruen | gelb | rot | null>   # null wenn ga4-first-party.md fehlt
  ga4_konfidenz_wirkung: <hoch | mittel | niedrig | null>  # gruen→hoch, gelb→mittel, rot→niedrig
  sea_first_party_vorhanden: <true | false>

# === Branche und Gewichtung ===
branchen_typ: <b2b_saas | b2c_ecommerce | lokal_dienstleister | b2b_industrie | b2b_mittelstand_dienstleister | content_publisher | marktplatz_plattform | sonstige>
branchen_typ_konfidenz: <hoch | mittel | niedrig>
gewichtungen:
  potenzial: <float>
  aufwand: <float>
  briefing_fit: <float>
  kunden_reife: <float>
  branchen_fit: <float>

# === Audit-Coverage ===
audit_coverage:
  audits_gelaufen: <int>           # Anzahl Audits aus status.md
  audits_erwartet: <int>           # max möglich
  coverage_prozent: <float>
  modus: <voll | reduced | duenn>   # > 5 = voll, 3-5 = reduced, < 3 = duenn

# === Kanal-Ranking ===
kanal_ranking:
  - rang: 1
    kanal_slug: <slug>
    kanal_anzeigename: <name>
    chancen_score: <int>
    chancen_score_konfidenz: <hoch | mittel | niedrig>
    potenzial_score: <int>
    potenzial_konfidenz: <hoch | mittel | niedrig>
    aufwand_score: <int>
    aufwand_konfidenz: <hoch | mittel | niedrig>
    briefing_fit_score: <int>
    briefing_fit_konfidenz: <hoch | mittel | niedrig>
    kunden_reife_score: <int>
    kunden_reife_roh: <int>
    kunden_reife_konfidenz: <hoch | mittel | niedrig>
    branchen_fit_score: <int>
    branchen_fit_konfidenz: <hoch | mittel | niedrig>
    branchen_fit_overrides: [<liste der angewandten Overrides>]
    apify_konfidenz_flag: <niedrig_ohne_apify | null>   # nur Paid-Kanäle (sea, meta-ads); gesetzt, wenn der Apify-Transparency-/Ad-Library-Scrape unvollständig war
    geo_multiplikator_strang: <true | false>            # true nur für den GEO-Kanal — markiert ihn als Hebel auf SEO/Content, kein eigener Budgetposten
    auffaelligkeiten_typen: [<liste>]
    empfohlene_naechste_aktion: <1 Satz>
    audit_inputs_verfuegbar: [<liste der gelesenen Dateien>]
  - rang: 2
    # ...
  # ... (alle konfigurierten Kanäle plus ggf. skip)

# === Top-3-Empfehlungen ===
top_3_empfehlungen:
  - rang: 1
    kanal_slug: <slug>
    kanal_anzeigename: <name>
    chancen_score: <int>
    warum_jetzt: <2-3 Sätze: Hebel, Datenlage, Briefing-Bezug>
    konkrete_argumente:
      - <Beleg-1 aus Audit X>
      - <Beleg-2 aus Audit Y>
    naechste_aktion: <1-2 Sätze, konkret und ausführbar>
  - rang: 2
    # ...
  - rang: 3
    # ...

# === Strategische Story ===
strategische_story:
  primaer_hebel: <slug oder slug-paar>
  hebel_beschreibung: <3-5 Sätze>
  sekundaere_hebel: [<liste optional>]
  warnungen:
    - <z. B. "Briefing nennt LinkedIn — aber Daten zeigen SEO als stärksten Hebel">

# === Auffälligkeiten (min. 7) ===
auffaelligkeiten:
  - typ: <enum: kanal_unterbespielt_kunde | kanal_branchen_chance | kanal_branchen_uebersaturiert | kanal_briefing_widerspruch | kunden_reife_engpass | quick_win_kanal | kanal_zu_klein | datenbasis_duenn | konfidenz_niedrig_kanal | sonstige>
    titel: <string>
    beschreibung: <1-2 Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion>
    betroffene_kanaele: [<slugs>]

# === Aggregat-Statistiken ===
statistiken:
  kanaele_bewertet: <int>
  kanaele_geskippt: <int>
  durchschnittlicher_chancen_score: <float>
  median_chancen_score: <float>
  top_chancen_score: <int>
  bottom_chancen_score: <int>
  kanaele_mit_niedriger_konfidenz: <int>
  audits_zur_basis: <int>
---

# Kanal-Chancen-Analyse: <Kundenname>

## Übersicht

3-5 Sätze: Branche, Datenbasis (welche Audits), Top-Kanal-Score, die 1-2 wichtigsten strategischen Ableitungen, Audit-Coverage-Quote.

## Top-3-Empfehlungen

### 1. <Kanal-Anzeigename> · chancen_score <int>

**Warum jetzt**: <3-4 Sätze aus Frontmatter>

**Konkrete Argumente aus den Audits**:

- <Beleg-1>
- <Beleg-2>
- <Beleg-3>

**Nächste Aktion**: <1-2 Sätze>

### 2. <Kanal-Anzeigename> · chancen_score <int>

(analog)

### 3. <Kanal-Anzeigename> · chancen_score <int>

(analog)

## Vollständiges Kanal-Ranking

| Rang | Kanal | Score | Potenzial | Aufwand | Briefing-Fit | Kunden-Reife | Branchen-Fit | Konfidenz |
|---|---|---|---|---|---|---|---|---|
| 1 | SEO | 73 | 72 | 65 | 75 | 85 | 80 | hoch |
| 2 | SEA / Google-Ads | 68 | 70 | 55 | 80 | 60 | 75 | hoch |
| 3 | Meta-Ads | 64 | 75 | 60 | 65 | 50 | 70 | mittel |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| — | Local-SEO / GMB | skip | — | — | — | — | — | — |

> Skip-Zeilen: Kanal nicht relevant für diesen Kunden (z. B. Local-SEO bei rein nationalem Online-Shop).

## Score-Heatmap

(im HTML-Report farbcodiert dargestellt — im Markdown als Tabelle wie oben)

## Strategische Story

<3-5 Sätze: was sind die 1-2 größten Hebel? Wie hängen Top-3 zusammen? Gibt es einen klaren Primär-Kanal oder einen sinnvollen Mix?>

**Warnungen** (falls vorhanden):

- <z. B. "Briefing legt Fokus auf LinkedIn — aber die Daten zeigen SEO als deutlich stärkeren Hebel. Im Kunden-Gespräch klären.">

## Pro Kanal (Details)

### SEO

- **chancen_score**: 73 (Konfidenz hoch)
- **Achsen**: Potenzial 72 hoch · Aufwand 65 hoch · Briefing-Fit 75 hoch · Kunden-Reife 85 hoch · Branchen-Fit 80 hoch
- **Audit-Inputs**: `audits/seo-cluster-zusammenfassung.md`, `audits/seo-sichtbarkeit.md`
- **Begründung Potenzial**: Kumuliertes Volumen 11.400 für Sweet-Spot-Cluster (Aufmaß-Anwendung)
- **Begründung Aufwand**: Median-Difficulty 28 — moderat, Content-Hub aufbauen möglich
- **Begründung Briefing-Fit**: Briefing nennt "Neukundenakquise" und SEO explizit als Wachstums-Hebel
- **Begründung Kunden-Reife**: Kunde mit `reife_roh` 22 (8% Top-10-Abdeckung) → großer Aufholhebel ohne Tech-Lücke
- **Begründung Branchen-Fit**: B2C-E-Commerce Default 75, plus 5 weil 6 von 9 WBs auf SEO sichtbar
- **Auffälligkeiten**: `quick_win_kanal`
- **Nächste Aktion**: Content-Hub für `aufmass_workflow`-Cluster aufbauen (siehe SEO-Cluster Top-1)

(... weitere Kanäle in gleicher Struktur — alle konfigurierten Kanäle)

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: <konkret>

**Betroffene Kanäle**: <liste>

(weitere Auffälligkeiten, mind. 7 insgesamt)

## Datenbasis

**Audits zur Verfügung** (X von Y):

- ✓ `audits/seo-cluster-zusammenfassung.md`
- ✓ `audits/google-ads.md`
- ✓ `audits/web-tech-tracking.md`
- ✗ `audits/meta-ads.md` — empfohlen für robustere Meta-Bewertung
- ✗ `audits/local-gmb.md` — Local-SEO geskippt mangels Daten

**Audit-Coverage**: 35% (4 von 11) → Modus `reduced` → einige Achsen mit niedriger Konfidenz

## Folge-Skills

Empfohlene nächste Skills basierend auf den Erkenntnissen:

- **`04-03-ziele-aus-potenzialen`** — leitet aus den Top-3-Kanälen quantifizierbare Ziel-Bandbreiten ab
- **`04-04-forecast-modell`** — wenn KPIs bekannt: direkt in den Forecast
- **Folge-Audits**: <Liste der fehlenden Audits, die den Score am stärksten verbessern würden>
```

## HTML-Report-Struktur

Im `{{MAIN_CONTENT}}`-Bereich:

### 1. Stat-Strip

```html
<section class="stat-strip">
  <div class="stat"><span class="label">Kanäle bewertet</span><span class="value">11</span></div>
  <div class="stat"><span class="label">Top-Score</span><span class="value">73</span></div>
  <div class="stat"><span class="label">Top-Kanal</span><span class="value">SEO</span></div>
  <div class="stat"><span class="label">Audit-Coverage</span><span class="value">63%</span></div>
</section>
```

### 2. Top-3-Karten

Drei `.summary-card`s nebeneinander mit Score, Begründung und Aktions-Button:

```html
<div class="suggestion">
  <h3>1. SEO · 73</h3>
  <p>Warum jetzt: ...</p>
  <ul>
    <li>Beleg 1</li>
    <li>Beleg 2</li>
  </ul>
  <p><strong>Nächste Aktion:</strong> ...</p>
</div>
```

### 3. Score-Heatmap (Kanal × Achse)

`<table class="data">` mit Zellen, deren Hintergrund per Inline-Style farbcodiert ist:

- 0-29: rot (`background: #fee` oder Shell-Klasse)
- 30-59: gelb
- 60-100: grün

Spalten: Kanal, Potenzial, Aufwand, Briefing-Fit, Kunden-Reife, Branchen-Fit, Total
Zeilen: alle 12 Kanäle nach Score sortiert

### 4. Vollständige Tabelle

`table.data` mit allen Kanälen + Konfidenz-Badges (`.badge.stark/mittel/schwach`)

### 5. Pro-Kanal-Details

`<details class="skill" data-status="...">` mit Score-Achsen, Begründungen, Audit-Quellen.

### 6. Strategische Story

Prominente `.summary-card` am Ende.

### 7. Auffälligkeiten

Als `<details>`-Blöcke, gruppiert nach Relevanz.

### 8. Datenbasis-Footer

Welche Audits da waren, welche fehlten — als kleine Tabelle. Wenn Modus `duenn`, prominent oben als Warnung in `.summary-card` mit roter Border.

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Genau so viele Einträge in `kanal_ranking` wie das konfigurierte Kanal-Set enthält (Basis 12; mit GEO, Reddit und Facebook-organisch bis zu 15) — inklusive `skip`-Zeilen für ausgeschlossene Kanäle
2. Jeder Kanal hat alle fünf Achsen-Scores als int 0-100 oder `skip`
3. `chancen_score` = gewichtete Summe der fünf Achsen (Toleranz ±1 wegen Rundung)
4. `top_3_empfehlungen` hat genau 3 Einträge (oder weniger wenn nur 3 nicht-skip-Kanäle)
5. `auffaelligkeiten` hat **mindestens 7 Einträge**
6. Jede Auffälligkeit hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`, `betroffene_kanaele`
7. `statistiken.kanaele_bewertet` + `statistiken.kanaele_geskippt` ≤ 12
8. `audit_coverage.modus` ist konsistent mit `audits_gelaufen` (>5 = voll, 3-5 = reduced, <3 = duenn)
9. `branchen_typ` ist einer der 8 erlaubten Werte

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `04-03-ziele-aus-potenzialen`

Liest aus `kanal-chancen.md` Frontmatter:

- `top_3_empfehlungen[]` → für welche Kanäle Ziele abgeleitet werden
- `kanal_ranking[i].potenzial_score` + `audit_inputs_verfuegbar` → Volumen-Basis für Ziel-Bandbreiten

### `04-04-forecast-modell`

Liest:

- `top_3_empfehlungen[].kanal_slug` → Forecast-Treiber-Kanäle
- `kanal_ranking[i].potenzial_score` + `aufwand_score` → Ramp-up und Conversion-Annahmen
- `strategische_story.primaer_hebel` → Pivot-Kanal im Forecast

### `04-05-90-tage-plan`

Liest:

- `top_3_empfehlungen[].naechste_aktion` → direkt als 90-Tage-Maßnahme
- `auffaelligkeiten` mit `typ: quick_win_kanal` → 30-Tage-Tasks

### `05-01-mta-slide-bausteine`

- `top_3_empfehlungen` direkt als Empfehlungs-Slide
- Score-Heatmap als Slide-Tabelle
- `strategische_story` als Briefing-Story-Slide vor dem Forecast
