# Phase-B-Output-Schema: `synthese/retainer.md`, `synthese/retainer.xlsx`, `reports/X-retainer.html`

Strukturelle Vorlage und Validierungs-Regeln fuer die Phase-B-Outputs des `04-06-retainer-kalkulator`. Vier Abschnitte: Markdown-Aggregat, Excel-Struktur, ROI-Bewertungs-Schwellen, HTML-Report-Sektionen.

---

## 1. `synthese/retainer.md` — Markdown-Aggregat

### Frontmatter

```yaml
---
skill: 04-06-retainer-kalkulator
phase: B
generiert_am: 2026-05-14T14:00:00Z
basis_zentral:
  stundensaetze_version: "2026.05"
  aufwands_bandbreiten_version: "2026.05"
basiert_auf:
  konfiguration: synthese/retainer-konfiguration.md
  forecast: synthese/forecast.md
  plan_90_tage: synthese/90-tage-plan.md
  kanal_chancen: synthese/kanal-chancen.md
  briefing: data/briefing.md     # null wenn nicht vorhanden

# Kunden-Konfiguration (Spiegel aus retainer-konfiguration.md)
service_level_konfiguriert: wachstum
vertragslaufzeit_monate: 12
reporting_frequenz: monatlich
strategie_workshop_frequenz: quartal

# Empfehlung des Skills (kann von der Konfiguration abweichen, mit Begruendung)
empfohlenes_service_level: wachstum
empfehlung_konfidenz: hoch   # hoch | mittel | niedrig
empfehlung_begruendung: "Briefing-Signal plus Kunden-Reife-Signal plus Forecast-ROI uebereinstimmend wachstum."

# Drei Service-Level x Drei Szenarien Matrix (3x3 = 9 Werte-Sets)
matrix:
  basis:
    konservativ:
      monat_min_eur: 2900
      monat_max_eur: 4200
      setup_min_eur: 4200
      setup_max_eur: 7800
      gesamt_12m_min_eur: 39000
      gesamt_12m_max_eur: 58200
      roi_faktor: 4.2
      break_even_monat: 5
    realistisch:
      monat_min_eur: 3500
      monat_max_eur: 5500
      setup_min_eur: 5500
      setup_max_eur: 9500
      gesamt_12m_min_eur: 47500
      gesamt_12m_max_eur: 75500
      roi_faktor: 5.1
      break_even_monat: 4
    ambitioniert:
      monat_min_eur: 4200
      monat_max_eur: 6500
      setup_min_eur: 7000
      setup_max_eur: 12000
      gesamt_12m_min_eur: 57400
      gesamt_12m_max_eur: 90000
      roi_faktor: 6.3
      break_even_monat: 3
  wachstum:
    konservativ:
      monat_min_eur: 5500
      monat_max_eur: 8000
      # ...
    realistisch:
      # ...
    ambitioniert:
      # ...
  vollservice:
    konservativ:
      # ...
    realistisch:
      # ...
    ambitioniert:
      # ...

# Aggregat-Statistiken
top_3_kostenposten:
  - rolle: SEA_MANAGER
    anteil_prozent: 35
  - rolle: SEO_MANAGER
    anteil_prozent: 28
  - rolle: STRATEGIE_MANAGER
    anteil_prozent: 18

kosten_pro_kanal:   # Anteil pro Kanal am Jahres-Retainer im empfohlenen Service-Level
  seo: 32
  sea: 28
  meta_ads: 18
  content: 12
  strategie_reporting: 10

# Auffaelligkeiten
auffaelligkeiten:
  - typ: vertragslaufzeit_zu_kurz_fuer_ramp_up
    relevanz: hoch
    details: "Vertragslaufzeit 6 Monate, SEO 32% Stunden-Anteil — SEO braucht 9 Monate Ramp-up"
  - typ: kosten_dominanz_einzelner_kanal
    relevanz: mittel
    details: "SEA macht 35% des Retainers — Klumpenrisiko wenn SEA underperformt"
  # mindestens 5 echte Auffaelligkeiten

schema_version: "1.0"
---
```

### Body-Sektionen (Pflicht)

```markdown
# Retainer-Empfehlung fuer KUNDENNAME

## Uebersicht

(3-5 Saetze: Service-Level-Empfehlung, Monats-Preis-Range Realistisch, Setup-Range, ROI-Faktor Realistisch, Break-Even-Monat Realistisch)

## 3x3-Matrix: Service-Level x Szenario

| Service-Level | Konservativ | Realistisch | Ambitioniert |
|---|---|---|---|
| basis | 2900-4200 EUR/Mo, ROI 4.2x, Break-Even M5 | 3500-5500 EUR/Mo, ROI 5.1x, Break-Even M4 | 4200-6500 EUR/Mo, ROI 6.3x, Break-Even M3 |
| **wachstum (empfohlen)** | ... | ... | ... |
| vollservice | ... | ... | ... |

## Service-Level-Empfehlung: WACHSTUM

(Begruendung in 5-10 Saetzen, mit Verweis auf Briefing-Signale, Kanal-Verantwortlichkeit, Forecast-ROI)

### Aufwand pro Kanal (im empfohlenen Service-Level)

(Tabelle pro Kanal: REACHX-Stunden/Monat, Kunde-Stunden/Monat, Kosten/Monat)

### Aufwand pro Monat M1-M12

(Tabelle Monat x Kanal mit Stunden plus EUR, Setup-Anteil M1-M3 separat ausgewiesen, laufender Aufwand M4-M12 mit Skalierungs-Hinweis)

### Strategie- und Reporting-Aufwand

(Stunden pro Monat fuer Strategie-Call, Reporting, plus Workshop-Aufwand pro Quartal/Halbjahr)

## ROI-Argumentation

Pro Service-Level x Szenario:

- Gesamtkosten 12 Monate (min-max) vs. erwarteter Forecast-Umsatz-Beitrag 12 Monate (entsprechendes Szenario)
- ROI-Faktor: erwarteter_umsatz / gesamtkosten
- Bewertung: stark / solide / grenzwertig / schwach (siehe Abschnitt 3 unten)

### Break-Even pro Szenario (empfohlenes Service-Level)

| Szenario | Break-Even-Monat | Kumulierte Kosten | Kumulierter erwarteter Umsatz |
|---|---|---|---|
| Konservativ | M7 | 45.500 EUR | 47.200 EUR |
| Realistisch | M4 | 29.500 EUR | 33.800 EUR |
| Ambitioniert | M3 | 22.100 EUR | 28.500 EUR |

## Auffaelligkeiten

(Sortiert nach Relevanz, mit Handlungs-Empfehlung pro Auffaelligkeit)

## Datenbasis-Footer

- Stundensaetze-Version: 2026.05 (Stand 2026-05-14)
- Aufwands-Bandbreiten-Version: 2026.05 (Stand 2026-05-14)
- Forecast-Stand: 2026-05-12
- 90-Tage-Plan-Stand: 2026-05-13
- Konfigurations-Bestaetigung: 2026-05-14 durch Stratege

```

---

## 2. `synthese/retainer.xlsx` — Excel-Struktur

Fuenf Sheets:

### Sheet 1: `Uebersicht`

3x3-Matrix (Service-Level x Szenario) plus empfohlene Markierung.

- Zeilen: basis / wachstum / vollservice
- Spalten-Gruppen (je Szenario): Monat-Preis-min, Monat-Preis-max, Setup-min, Setup-max, Gesamt-12M-min, Gesamt-12M-max, ROI-Faktor, Break-Even-Monat
- **Empfohlenes Service-Level** mit Hintergrund-Fill (`#FFF2CC` gelb)
- Header in REACHX-Blau (`#004C7E`), weisse Schrift, fett

### Sheet 2: `Aufwands-Pivot`

Strategisches Haupt-Artefakt — Massnahme x Monat x Stunden x Kostenposition.

- Zeilen: Massnahmen aus 90-Tage-Plan plus laufende Posten M4-M12
- Spalten: M1, M2, M3, M4, M5, ..., M12, **Summe**
- Pro Zelle zwei Zeilen-Eintraege: Stunden (oben), EUR (unten)
- Gruppierung nach Kanal (mit Kanal-Header-Zeilen)
- Letzte Zeile: Summe pro Monat plus Jahressumme
- Color-Scale fuer Stunden-Verteilung (Hellblau zu Dunkelblau) zur Erkennung von Kosten-Dominanzen

### Sheet 3: `Aufschluesselung`

Pro Skill-Rolle aus `reachx-stundensaetze.md` ein Block.

- Zeilen: STRATEGIE_LEAD, STRATEGIE_MANAGER, SEO_MANAGER, SEA_MANAGER, CONTENT_MANAGER, SOCIAL_MEDIA_MANAGER, DESIGNER, DEVELOPER, JUNIOR_HANDS
- Spalten: Stunden/Monat (Empfohlenes Service-Level, Realistisch), Stundensatz EUR, Kosten/Monat EUR, Kosten/Jahr EUR
- Letzte Zeile: Summe

### Sheet 4: `Setup-Phase`

Setup-Massnahmen einmalig.

- Zeilen: Setup-Bloecke aus `aufwands-bandbreiten.md` Abschnitt 1
- Spalten: Stunden-min, Stunden-max, Rolle, Stundensatz, Kosten-min, Kosten-max
- Gruppierung nach Bereich (Strategie-Setup / Tracking-Setup / Kanal-Setup)
- Aggregat unten: Setup-Gesamt-min, Setup-Gesamt-max

### Sheet 5: `ROI-Vergleich`

Retainer-Kosten vs. Forecast-Beitrag pro Monat.

- Spalten: M1, M2, M3, ..., M12, Aggregat
- Zeilen-Gruppen pro Szenario:
  - Kumulierte Retainer-Kosten
  - Kumulierter erwarteter Umsatz aus Forecast
  - Differenz (Umsatz minus Kosten)
  - Break-Even-Marker (Spaltenzelle mit gruenem Border in dem Monat, in dem Break-Even erreicht wird)
- Conditional Formatting: Differenz-Zellen rot wenn negativ, gruen wenn positiv

### Excel-Styling

```python
# Default-Formate
HEADER_FILL = PatternFill(start_color="004C7E", end_color="004C7E", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
EMPFOHLEN_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
NUM_FORMAT_EUR = '#,##0" EUR";[Red]-#,##0" EUR"'
NUM_FORMAT_STUNDEN = '0.0" h"'
```

### CSV-Fallback

Wenn `openpyxl` und `xlsxwriter` beide nicht verfuegbar, schreibt der Skill 5 CSV-Files:

- `synthese/retainer-uebersicht.csv`
- `synthese/retainer-aufwands-pivot.csv`
- `synthese/retainer-aufschluesselung.csv`
- `synthese/retainer-setup-phase.csv`
- `synthese/retainer-roi-vergleich.csv`

Im Output-Markdown wird das transparent dokumentiert (Sektion "Datenbasis-Footer").

---

## 3. ROI-Bewertungs-Schwellen

```
ROI-Faktor = erwarteter_umsatz_12_monate / gesamtkosten_12_monate
```

| ROI-Faktor | Bewertung | Handlungs-Hinweis |
|---|---|---|
| > 5x | stark | Retainer-Empfehlung klar argumentierbar, Verkaufsgespraech offensiv |
| 3-5x | solide | Standard-Empfehlungs-Bereich, ROI-Argument als Stuetze |
| 2-3x | grenzwertig | Service-Level pruefen — kleinere Stufe oder weniger Kanaele eventuell besser |
| < 2x | schwach | Auffaelligkeit `roi_negativ_im_worst_case` wenn das das Worst/Konservativ-Szenario ist; sonst Hinweis im Output dass die Empfehlung im Verkaufsgespraech vorsichtig kommuniziert werden muss |

ROI-Anteil-Prozent (umgekehrte Sicht: Kosten als % vom Umsatz):

| ROI-Anteil | Bewertung |
|---|---|
| < 10% | stark |
| 10-20% | solide |
| 20-30% | grenzwertig |
| > 30% | schwach |

---

## 4. HTML-Report `reports/X-retainer.html` — Sektionen

Aus `reports/_shell.html`. Pflicht-Platzhalter ersetzen (siehe `contracts.md` Abschnitt 7). Body-Sektionen in dieser Reihenfolge:

### 4.1 Stat-Strip (oben)

Vier Stat-Karten:

- **Empfohlenes Service-Level**: z. B. `WACHSTUM` mit Konfidenz-Badge
- **Monats-Preis-Range (Realistisch)**: z. B. `5.500 bis 9.000 EUR`
- **ROI-Faktor (Realistisch)**: z. B. `5.1x` mit Bewertung-Badge (`stark/solide/grenzwertig/schwach`)
- **Break-Even (Realistisch)**: z. B. `Monat 4`

### 4.2 Sticky-TOC

Quicklinks zu allen Haupt-Sektionen: Service-Level-Karten, ROI-Chart, Aufwands-Pivot, Setup, Vertragsgestaltung, Auffaelligkeiten.

### 4.3 Drei Service-Level-Karten

Nebeneinander als `<details class="skill">`-Bloecke (Empfohlene mit `.badge.stark` und visuell hervorgehoben):

- **basis** Karte: Charakter-Beschreibung, Monats-Preis-Range (Realistisch), Setup-Range, ROI-Faktor (Realistisch), Break-Even-Monat (Realistisch), 5-7 Leistungs-Bullet-Points
- **wachstum** Karte: analog
- **vollservice** Karte: analog

In jeder Karte Tabelle mit allen drei Szenarien (konservativ/realistisch/ambitioniert) klein darunter.

### 4.4 ROI-Chart (Inline-SVG)

**Linien-Chart**: Pro Service-Level x Szenario eine Linie ueber 12 Monate.

- X-Achse: Monat M1-M12
- Y-Achse: EUR
- Linien: Kumulierte Retainer-Kosten (gestrichelt) und kumulierter erwarteter Forecast-Umsatz (durchgezogen), je Szenario
- Break-Even-Marker als vertikale Linie + Punkt-Highlight an Schnittstelle
- Legende rechts
- 3 Service-Level x 3 Szenarien = 9 Linien-Paare; um nicht ueberladen zu werden: nur empfohlenes Service-Level mit allen drei Szenarien, andere Service-Level dimmed

### 4.5 Aufschluesselung-Tabelle pro Kanal

Pro Kanal: REACHX-Stunden/Monat, Kunde-Stunden/Monat, Stundensatz, Kosten/Monat (im empfohlenen Service-Level x Realistisch-Szenario).

### 4.6 Setup-Phase-Tabelle

Setup-Bloecke aus `aufwands-bandbreiten.md` Abschnitt 1, Bandbreite Stunden plus EUR-Kosten.

### 4.7 Aufwands-Pivot-Heatmap

Tabelle Massnahme (Zeilen) x Monat M1-M12 (Spalten) mit Color-Coded-Stunden — gleicher Inhalt wie Excel-Sheet 2, aber als HTML-Tabelle mit `.heatmap` CSS-Klasse fuer Background-Color-Gradient.

### 4.8 Vertragsgestaltung-Sektion

- Vertragslaufzeit
- Kuendigungsfristen (Standard: 3 Monate zum Quartal)
- Reporting-Rhythmus
- Workshop-Rhythmus
- Eskalations-Pfad (Strategie-Lead-Kontakt)

### 4.9 Auffaelligkeiten-Block

`.suggestion`-Bloecke mit Handlungs-Empfehlungen pro Auffaelligkeit (mindestens 5).

### 4.10 Datenbasis-Footer

Versions-Angaben:

- Stundensaetze: 2026.05
- Aufwands-Bandbreiten: 2026.05
- Forecast-Stand
- 90-Tage-Plan-Stand
- Konfigurations-Bestaetigung-Datum

---

## 5. Validierungs-Regeln fuer den Output

- **Pflicht-Bandbreite**: pro Service-Level x Szenario muessen `monat_min < monat_max` und `setup_min < setup_max` gelten. Punktwerte (`min == max`) sind verboten — Validierungs-Fehler.
- **Drei Szenarien Pflicht**: `konservativ`, `realistisch`, `ambitioniert` muessen alle drei pro Service-Level vorhanden sein.
- **Mindestens 5 Auffaelligkeiten** im Output (siehe Skill SKILL.md Schritt B.8).
- **ROI-Faktor positiv**: Wenn ROI-Faktor < 1 in mindestens 2 von 3 Szenarien im empfohlenen Service-Level → Auffaelligkeit `roi_negativ_im_worst_case` automatisch markieren.
- **Versions-Stamp**: Stundensaetze- und Aufwands-Bandbreiten-Versionen muessen im Frontmatter und im Datenbasis-Footer auftauchen.
- **Drei Service-Level Pflicht**: alle drei Service-Level werden berechnet und im Output gezeigt, auch wenn nur eines empfohlen ist (Stratege kann im Verkaufsgespraech Alternativen anbieten).
