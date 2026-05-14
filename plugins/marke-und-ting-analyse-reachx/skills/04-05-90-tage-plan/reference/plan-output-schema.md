# Output-Schema: 90-Tage-Plan-Generator

Definiert die drei Pflicht-Outputs:

- `synthese/90-tage-plan.md` — Markdown-Roadmap mit Massnahmen-Tabelle pro Monat plus Aggregat plus strategischer Story
- `synthese/90-tage-plan.csv` — Roh-Tabelle (eine Zeile pro Massnahme) fuer CSV-Konsumenten wie Asana, Trello, Notion
- `reports/X-90-tage.html` — HTML-Report mit Gantt-aehnlicher Inline-SVG-Visualisierung

## CSV-Schema (`synthese/90-tage-plan.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anfuehrungszeichen fuer Werte mit Komma oder Pipe.

### Spalten (in fester Reihenfolge)

```
massnahme_id,monat,titel,beschreibung,zielsetzung,
kanal_slug,kanal_anzeigename,
verantwortlich,verantwortlich_details,
aufwand_min_stunden,aufwand_max_stunden,
voraussetzungen,
meilenstein_indikator,
prioritaet,
quelle,
bibliothek_slug,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `massnahme_id` | string | ja | Format `m001`, `m002`, ... durchnummeriert ueber alle Monate |
| `monat` | int 1-3 | ja | Monats-Zuordnung |
| `titel` | string | ja | kurz, aktivisch |
| `beschreibung` | string | ja | 1-2 Saetze |
| `zielsetzung` | string | ja | 1 Satz, was die Massnahme erreichen soll |
| `kanal_slug` | string | ja | aus `kanal-chancen.md` Kanal-Set plus `tracking-cross` fuer kanal-uebergreifend |
| `kanal_anzeigename` | string | ja | Anzeigename fuer Lesbarkeit |
| `verantwortlich` | enum | ja | `REACHX | Kunde | Hybrid` |
| `verantwortlich_details` | string | nein | bei Hybrid: Rollen-Aufteilung in 1 Satz |
| `aufwand_min_stunden` | int | ja | Untergrenze der Bandbreite, min >= 1 |
| `aufwand_max_stunden` | int | ja | Obergrenze, max >= min |
| `voraussetzungen` | string | nein | Pipe-Liste der `massnahme_id`s oder Text-Hinweise (z. B. `m001|m003|Tracking muss live sein`) |
| `meilenstein_indikator` | string | ja | woran man Erfolg messen kann, 1 Satz |
| `prioritaet` | enum | ja | `Quick-Win | Foundation | Long-Term` |
| `quelle` | string | ja | `auffaelligkeit:typ`, `top3_aktion`, `bibliothek:slug`, `sweet_spot_cluster:name`, `tech_voraussetzung`, `best_practice` |
| `bibliothek_slug` | string | nein | Bibliotheks-Slug aus `massnahmen-bibliothek.md` falls Massnahme aus Bibliothek stammt |
| `datenstand_iso` | ISO-8601 | ja | Datum des Skill-Laufs |

### Sortierung

1. `monat` aufsteigend
2. Innerhalb des Monats: `prioritaet` in Reihenfolge `Foundation` → `Quick-Win` → `Long-Term`
3. Tiebreaker: alphabetisch nach `kanal_slug`, dann `massnahme_id` aufsteigend

### Groessen-Grenze

Soft-Cap: 35 Massnahmen. Hard-Cap: 50. Wenn Plan groesser wird: Warnung im Output, einige Massnahmen in 91-180-Tage-Backlog verschoben (Backlog wird nicht geschrieben, nur erwaehnt).

## Markdown-Schema (`synthese/90-tage-plan.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 04-05-90-tage-plan
generiert_am: ISO-8601
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  forecast: synthese/forecast.md
  kanal_chancen: synthese/kanal-chancen.md
  seo_cluster: audits/seo-cluster-zusammenfassung.md   # null wenn nicht vorhanden
  website_tech: audits/web-tech-tracking.md                 # null wenn nicht vorhanden
  briefing: data/briefing.md                           # null wenn nicht vorhanden
  zusaetzliche_audits_genutzt:
    - audits/content-inventur.md
    - audits/google-ads.md
    # ... (alle gefundenen)

# === Modus ===
modus: voll | reduced | duenn
konfidenz_gesamt: hoch | mittel | niedrig

# === Top-Kanaele (aus kanal-chancen.md) ===
top_kanaele:
  - rang: 1
    kanal_slug: seo
    kanal_anzeigename: SEO
    chancen_score: 73
    massnahmen_anzahl: 6
  - rang: 2
    kanal_slug: sea
    kanal_anzeigename: SEA / Google-Ads
    chancen_score: 68
    massnahmen_anzahl: 4
  - rang: 3
    kanal_slug: meta-ads
    kanal_anzeigename: Meta-Ads
    chancen_score: 64
    massnahmen_anzahl: 3

# === Aggregat ===
aggregat:
  massnahmen_gesamt: 22
  massnahmen_monat_1: 9
  massnahmen_monat_2: 8
  massnahmen_monat_3: 5
  aufwand_min_stunden_gesamt: 184
  aufwand_max_stunden_gesamt: 348
  aufwand_min_monat_1: 78
  aufwand_max_monat_1: 142
  aufwand_min_monat_2: 64
  aufwand_max_monat_2: 124
  aufwand_min_monat_3: 42
  aufwand_max_monat_3: 82
  verantwortlichkeits_verteilung:
    REACHX: 0.55     # Anteil aller Massnahmen
    Hybrid: 0.32
    Kunde: 0.13
  prioritaets_verteilung:
    Quick-Win: 0.36
    Foundation: 0.41
    Long-Term: 0.23
  kanal_verteilung:
    seo: 6
    sea: 4
    meta-ads: 3
    tracking-cross: 5
    content: 2
    website-cro: 2
  geschaetzte_team_kapazitaet_kunde_std_pro_monat: 50   # null wenn unbekannt
  geschaetzte_team_kapazitaet_quelle: briefing | default

# === Massnahmen (alle) ===
massnahmen:
  - massnahme_id: m001
    monat: 1
    titel: GA4-Tracking auf Hauptdomain einrichten und verifizieren
    beschreibung: GA4-Property konfigurieren, GTM-Container aufsetzen, Events fuer Conversions definieren.
    zielsetzung: Saubere Daten-Basis fuer alle Channel-Auswertungen.
    kanal_slug: tracking-cross
    kanal_anzeigename: Tracking & Setup
    verantwortlich: Hybrid
    verantwortlich_details: REACHX Konzept und QA, Kunde Implementierung im CMS
    aufwand_min_stunden: 12
    aufwand_max_stunden: 24
    voraussetzungen: []
    voraussetzungen_text: Zugriff auf GTM und CMS noetig
    meilenstein_indikator: GA4 zeigt mind. 7 Tage saubere Daten fuer Top-10-Landingpages
    prioritaet: Foundation
    quelle: tech_voraussetzung
    bibliothek_slug: tracking-ga4-setup
  - massnahme_id: m002
    monat: 1
    # ... (weitere Massnahmen analog)

# === Meilensteine pro Monat ===
meilensteine:
  monat_1:
    titel: Setup-Phase abgeschlossen
    beschreibung: 1-2 Saetze, was am Ende Monat 1 steht
    messbare_indikatoren:
      - GA4 liefert saubere Daten fuer Top-10-Landingpages
      - Sweet-Spot-Cluster-Pillar-Page-Konzept freigegeben
      - SEA-Konto live mit Brand-Kampagne
  monat_2:
    titel: Erste Skalierungs-Welle live
    beschreibung: 1-2 Saetze
    messbare_indikatoren:
      - Erste 4 Content-Stuecke aus Sweet-Spot-Cluster live
      - Meta-Ads-Erstkampagne laeuft mit drei Audience-Tests
      - Performance-Review zu Monat 2 dokumentiert
  monat_3:
    titel: Optimierung und Q2-Vorbereitung
    beschreibung: 1-2 Saetze
    messbare_indikatoren:
      - Top-Cluster mit 6+ Stuecken live, erste Rankings sichtbar
      - SEA-Kampagnen mit positivem ROAS
      - Q2-Plan freigegeben, Retainer-Empfehlung dokumentiert

# === Auffaelligkeiten (min. 6) ===
auffaelligkeiten:
  - typ: enum (siehe Liste unten)
    titel: kurzer Titel
    beschreibung: 1-2 Saetze
    relevanz: hoch | mittel | niedrig
    handlungs_empfehlung: konkrete Aktion
    betroffene_massnahmen: [m001, m003]
    betroffene_kanaele: [seo, sea]

# === Strategische Story ===
strategische_story:
  groesste_hebel: 2-3 Hebel als kurze Strings
  hebel_beschreibung: 3-5 Saetze
  kunden_freigabe_critical: Liste was Kunde unbedingt liefern muss
  risiken: Liste
---

# 90-Tage-Plan: KUNDENNAME

## Uebersicht

3-5 Saetze: Top-Kanaele, Gesamt-Aufwand-Range, groesste Hebel, Verantwortlichkeits-Mix.

## Aggregat auf einen Blick

| Metrik | Wert |
|---|---|
| Massnahmen gesamt | 22 |
| Aufwand gesamt | 184-348 Stunden |
| Verantwortlich REACHX | 55% |
| Verantwortlich Hybrid | 32% |
| Verantwortlich Kunde | 13% |
| Quick-Wins | 36% |
| Foundation | 41% |
| Long-Term | 23% |
| Geschaetzte Kunden-Team-Kapazitaet | 50 Std/Monat |

## Monat 1 - Setup

**Meilenstein Ende Monat 1**: Setup-Phase abgeschlossen — alle Tracking-Voraussetzungen live, erste Sweet-Spot-Cluster-Briefings angestossen, SEA-Konto mit Brand-Kampagne aktiv.

**Massnahmen**:

| ID | Titel | Kanal | Verantwortlich | Aufwand | Prio | Voraussetzungen | Meilenstein |
|---|---|---|---|---|---|---|---|
| m001 | GA4-Tracking auf Hauptdomain einrichten | tracking-cross | Hybrid | 12-24 | Foundation | - | GA4 liefert saubere Daten fuer Top-10 |
| m002 | XML-Sitemap einreichen und Indexierung verifizieren | seo | REACHX | 4-8 | Quick-Win | - | 95%+ Top-50-URLs indexiert |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Monat 2 - Skalierung

**Meilenstein Ende Monat 2**: Erste Skalierungs-Welle live — Content-Stuecke veroeffentlicht, Ads-Kampagnen mit ersten Performance-Daten, Performance-Review dokumentiert.

**Massnahmen**:

(analoge Tabelle)

## Monat 3 - Optimierung

**Meilenstein Ende Monat 3**: Optimierung und Q2-Vorbereitung — Top-Cluster mit mehreren Stuecken live, SEA mit positivem ROAS, Q2-Plan freigegeben.

**Massnahmen**:

(analoge Tabelle)

## Critical-Path und Abhaengigkeiten

Massnahmen, die viele andere blockieren:

- **m001 GA4-Tracking** blockiert: m007 (Reporting-Dashboard), m012 (Meta-Pixel-Setup), m015 (LinkedIn-Insight-Tag) — Critical-Path-Massnahme
- **m003 Briefing-Workshop** blockiert: m008 (Content-Hub-Konzept), m013 (Meta-Ads-Briefing) — wenn Briefing-Luecken vorliegen

Wenn diese Massnahmen kippen, ruckt der gesamte Plan.

## Strategische Story

Aus Frontmatter `strategische_story`. 3-5 Saetze:

- Groesste Hebel im 90-Tage-Fenster
- Was Kunde unbedingt freigeben muss
- Risiken

## Auffaelligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### Auffaelligkeit 1 - Titel

Beschreibung in 1-2 Saetzen.

**Handlungs-Empfehlung**: konkret

**Betroffene Massnahmen**: m003, m008

**Betroffene Kanaele**: SEO, Meta-Ads

(weitere Auffaelligkeiten — mind. 6)

## Datenbasis

**Inputs zur Verfuegung** (X von Y):

- ✓ synthese/forecast.md
- ✓ synthese/kanal-chancen.md
- ✓ audits/seo-cluster-zusammenfassung.md
- ✓ audits/web-tech-tracking.md
- ✗ audits/content-inventur.md — empfohlen fuer fundierte Stale-Content-Massnahmen
- ✓ data/briefing.md

## Folge-Skills

- **04-06-retainer-kalkulator** — wenn Forecast plus Plan vorhanden, kann Retainer berechnet werden
- **05-01-mta-slide-bausteine** — Roadmap-Slide-Baustein direkt aus diesem Plan
```

## HTML-Report-Struktur

Im `{{MAIN_CONTENT}}`-Bereich:

### 1. Stat-Strip

```html
<section class="stat-strip">
  <div class="stat"><span class="label">Massnahmen</span><span class="value">22</span></div>
  <div class="stat"><span class="label">Aufwand</span><span class="value">184-348 Std</span></div>
  <div class="stat"><span class="label">REACHX-Anteil</span><span class="value">55%</span></div>
  <div class="stat"><span class="label">Quick-Wins</span><span class="value">36%</span></div>
</section>
```

### 2. Gantt-aehnliche SVG-Timeline

Inline-SVG, keine externen Libraries. Aufbau:

- ViewBox z. B. `0 0 1200 800` (Hoehe abhaengig von Massnahmen-Anzahl)
- Drei vertikale Spalten als hellgraue Boxen (Monat 1 / Monat 2 / Monat 3), Spalten-Breite ca. 380px, Abstand 20px
- Spalten-Header oben: "Monat 1 - Setup", "Monat 2 - Skalierung", "Monat 3 - Optimierung"
- Pro Massnahme eine horizontale Zeile mit Balken in der entsprechenden Monats-Spalte
- Balken-Hoehe: 22-26 px, Zeilen-Abstand 8 px
- Balken-Farbcodierung nach `prioritaet`:
  - Quick-Win: REACHX-Sunrise-Red `#ec644a`
  - Foundation: REACHX-Night-Sky `#000a14`
  - Long-Term: Mittel-Grau `#666f7a`
- Balken-Laenge proportional zur Aufwand-Range-Mitte ((min+max)/2), Skalierungs-Faktor so dass groesste Massnahme ca. 70% der Spalten-Breite einnimmt
- Auf Balken: kurzer Titel-Text (truncated bei ueberlauf), Aufwand-Range klein dahinter
- Voraussetzungs-Pfeile: duenne graue Linien zwischen abhaengigen Massnahmen (`<line>` plus `<polygon>`-Pfeilspitze), nur wenn Abhaengigkeiten ueber Monats-Grenzen gehen
- Verantwortlichkeits-Indikator: kleines farbiges Rechteck links neben dem Balken (REACHX = sunrise, Hybrid = gelb, Kunde = blau)
- Legende unten

### 3. Meilenstein-Banner

Drei prominente Banner (eines pro Monats-Ende):

```html
<div class="summary-card">
  <h3>Meilenstein Ende Monat 1 - Setup-Phase abgeschlossen</h3>
  <ul>
    <li>GA4 liefert saubere Daten fuer Top-10-Landingpages</li>
    <li>Sweet-Spot-Cluster-Pillar-Page-Konzept freigegeben</li>
    <li>SEA-Konto live mit Brand-Kampagne</li>
  </ul>
</div>
```

### 4. Aggregat-Visualisierungen

Drei kompakte SVG-Visualisierungen nebeneinander:

- **Donut**: Verantwortlichkeits-Verteilung (REACHX vs. Hybrid vs. Kunde)
- **Donut**: Prioritaets-Verteilung (Quick-Win vs. Foundation vs. Long-Term)
- **Bar-Chart**: Aufwand pro Monat (drei vertikale Bars mit Min-Max-Range-Visualisierung)

### 5. Massnahmen-Tabellen pro Monat

Drei `table.data` (eine pro Monat) mit allen Massnahmen des Monats. Spalten: ID, Titel, Kanal, Verantwortlich, Aufwand, Prio, Meilenstein-Kurzfassung.

### 6. Critical-Path-Liste

Prominente `.summary-card` mit den Critical-Path-Massnahmen und ihren Abhaengigkeitspfaden (Pfeile in Text-Form: `m001 → m007, m012, m015`).

### 7. Auffaelligkeiten

Als `<details>`-Bloecke, gruppiert nach Relevanz (hoch zuerst, ueber 6 Eintraege).

### 8. Strategische Story

Prominente `.summary-card` am Ende mit groessten Hebeln und Risiken.

### 9. Datenbasis-Footer

Welche Inputs da waren, welche fehlten — als kleine Tabelle.

## Validierungs-Regeln

Vor dem Schreiben prueft der Skill:

1. Mindestens 4 Massnahmen pro Monat
2. Jede Massnahme hat alle Pflicht-Felder
3. `aufwand_min_stunden >= 1` und `aufwand_max_stunden >= aufwand_min_stunden`
4. `verantwortlich` ist einer der 3 erlaubten Werte (`REACHX | Kunde | Hybrid`)
5. Bei `verantwortlich: Hybrid` ist `verantwortlich_details` gesetzt (sonst Warnung, keine harte Verletzung)
6. `prioritaet` ist einer der 3 erlaubten Werte
7. `monat` ist 1, 2 oder 3
8. `quelle` matched einem der erlaubten Patterns
9. Mindestens 1 Foundation-Massnahme in Monat 1
10. Mindestens 1 Quick-Win-Massnahme insgesamt
11. Mindestens 6 Auffaelligkeiten im `auffaelligkeiten`-Block
12. `voraussetzungen`-Graph ist zyklenfrei (keine Massnahme haengt indirekt von sich selbst ab)
13. `aggregat.massnahmen_gesamt` = Anzahl Eintraege in `massnahmen`
14. Summen pro Monat in `aggregat` matchen die Filter auf `massnahmen[monat==i]` (Toleranz 0)
15. `verantwortlichkeits_verteilung`-Summe und `prioritaets_verteilung`-Summe ergeben jeweils 1.0 (Toleranz +/- 0.02 wegen Rundung)

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Erlaubte Werte fuer `auffaelligkeiten.typ`

Pflicht-Set (mindestens 6 Auffaelligkeiten, nicht alle Typen zwingend besetzt):

- `aufwand_uebersteigt_team_kapazitaet`
- `kunden_verantwortung_dominiert`
- `setup_phase_zu_lang`
- `keine_quick_wins_in_monat_1`
- `tech_voraussetzungen_fehlen`
- `kanal_im_plan_nicht_im_chancen_top5`

Optional weitere Typen:

- `kein_reporting_setup`
- `forecast_widerspruch`
- `quick_wins_dominant`
- `abhaengigkeitskette_lang` (Critical-Path mit ueber 4 Stufen)
- `kanal_nur_einzelmassnahme` (Top-3-Kanal hat nur 1 Massnahme)
- `datenbasis_duenn`
- `methodischer_hinweis`

## Wie Folge-Skills die Outputs lesen

### `04-06-retainer-kalkulator`

Liest aus `90-tage-plan.md` Frontmatter:

- `aggregat.aufwand_min_stunden_gesamt` und `aggregat.aufwand_max_stunden_gesamt` → Setup-Stunden-Range fuer Retainer-Kalkulation
- `aggregat.verantwortlichkeits_verteilung` → Anteil REACHX-Stunden vs. Hybrid-Stunden (Hybrid wird mit Faktor 0.6 als REACHX-Stunden gewertet, Kunde 0.0)
- `aggregat.prioritaets_verteilung` → Mix-Argument fuer Paket-Empfehlung
- `top_kanaele[]` → fuer Light-/Standard-/Vollservice-Paket-Differenzierung

### `05-01-mta-slide-bausteine`

- `meilensteine` direkt als 3 Slides ("Was bis Monat 1 / 2 / 3 steht")
- Gantt-SVG als Roadmap-Slide
- `strategische_story` als Story-Slide vor dem Retainer-Block
- `aggregat.verantwortlichkeits_verteilung` als Tortenstueck-Slide

### `05-02-mta-export-to-drive`

- `synthese/90-tage-plan.csv` direkt in Drive-Ordner uebernehmen — Stratege kann CSV in Asana / Trello / Notion importieren
- HTML-Report als zentrale Roadmap-Datei
