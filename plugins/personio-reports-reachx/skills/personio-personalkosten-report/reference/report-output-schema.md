# Output-Schema — XLSX, report-daten.json, HTML

Der Skill erzeugt vier Dateien im Verzeichnis
`~/personio-reports/personalkosten-<YYYY-MM-DD>/`:

| Datei | Erzeugt von | Zweck |
|---|---|---|
| `employees.json` | `personio.py` | Roh-Daten aus Personio |
| `personalkosten-report.xlsx` | `build-report.py` | Detail-Mappe für HR (4 Blätter) |
| `report-daten.json` | `build-report.py` | verdichtete Kennzahlen |
| `personalkosten-report.html` | Skill (aus Shell) | REACHX-Report (Management-Sicht) |

---

## 1. Excel-Mappe — `personalkosten-report.xlsx`

`build-report.py` schreibt die Mappe fertig formatiert; sie wird nicht
nachbearbeitet. Vier Blätter:

1. **Übersicht** — KPI-Block: Headcount, FTE, Mitarbeiter mit Gehalt,
   Bruttogehälter p.a., Arbeitgeberkosten p.a. und p.M., Durchschnitte je Kopf
   und je FTE, Ein-/Austritte, Fluktuationsrate, Ø Betriebszugehörigkeit.
2. **Mitarbeiter** — eine Zeile je Mitarbeiter: Name (oder Code), Abteilung,
   Position, Status, Eintritt, Austritt, Wochenstunden, FTE, Monatsbrutto,
   Jahresbrutto inkl. Bonus, Arbeitgeberkosten p.a.
3. **Abteilungen** — je Abteilung Headcount, FTE, Anzahl mit Gehalt,
   Bruttogehälter p.a., Arbeitgeberkosten p.a.; mit Summenzeile.
4. **Annahmen & Hinweise** — AG-Faktor, Vollzeit-Stunden, Gehalts-/Bonus-
   Attribut, Stichtag, Anonymisierung, der Schätzungs-Hinweis und alle
   Datenlücken-Warnungen.

---

## 2. `report-daten.json`

Maschinen-Schicht für den HTML-Report. Aufbau:

```json
{
  "success": true,
  "erstellt_am": "2026-05-22T16:40:00",
  "stichtag": "2026-05-22",
  "quelle": "Personio REST API v1 (First-Party, read-only)",
  "annahmen": {
    "ag_faktor": 1.20,
    "vollzeit_stunden": 40.0,
    "gehalt_attribut": "auto",
    "gehalt_intervall": "auto",
    "bonus_attribut": "bonus",
    "bonus_intervall": "jaehrlich",
    "anonymisiert": false
  },
  "kennzahlen": {
    "headcount": 142,
    "fte_summe": 128.5,
    "mit_gehalt": 138,
    "ohne_gehalt": 4,
    "kostendaten_verfuegbar": true,
    "personalkosten": {
      "brutto_jahr_summe": 7840000.0,
      "ag_kosten_jahr_summe": 9408000.0,
      "ag_kosten_monat_summe": 784000.0,
      "brutto_jahr_schnitt": 56811.59,
      "ag_kosten_jahr_schnitt_kopf": 68173.91,
      "ag_kosten_jahr_je_fte": 73210.0
    },
    "fluktuation": {
      "eintritte_12m": 18,
      "austritte_12m": 11,
      "fluktuationsrate": 0.0775,
      "betriebszugehoerigkeit_schnitt_jahre": 3.4
    },
    "status_verteilung": {"active": 138, "leave": 3, "onboarding": 1},
    "gehalt_basis_verteilung": {"fix_salary": 120, "hourly_salary": 18}
  },
  "abteilungen": [
    {"abteilung": "Entwicklung", "headcount": 40, "fte": 38.0,
     "mit_gehalt": 40, "brutto_jahr": 2600000.0, "ag_jahr": 3120000.0}
  ],
  "ohne_gehalt_namen": ["MA-099", "…"],
  "warnungen": ["4 von 142 Mitarbeitern ohne Gehaltsangabe — …"],
  "dateien": {"xlsx": "personalkosten-report.xlsx"}
}
```

Leere abgeleitete Werte sind `null`, nicht `0`.

---

## 3. HTML-Report — `personalkosten-report.html`

Aus `reference/report-shell.html` bauen: Shell lesen, sechs Platzhalter ersetzen,
Ergebnis schreiben. `{{MAIN_CONTENT}}` **ausschließlich** aus den Bausteinen
unten — keine eigenen CSS-Klassen, kein inline-`style` (Ausnahme: `bar-fill`-
Breite), der `<style>`-Block bleibt unverändert.

### Platzhalter

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | `Personalkosten-Report · <stichtag>` |
| `{{EYEBROW}}` | `REACHX · Personalreport` |
| `{{DISPLAY_NAME}}` | `Personalkosten-Report` |
| `{{META_LINE}}` | `Quelle: Personio (First-Party, read-only) · Stichtag: <stichtag> · Erstellt: <datum>` |
| `{{MAIN_CONTENT}}` | Report-Körper aus den Bausteinen |
| `{{FOOTER_TEXT}}` | `REACHX · Personalkosten-Report · vertraulich — enthält Gehaltsdaten` |

### Pflicht-Reihenfolge in `{{MAIN_CONTENT}}`

1. Sticky-TOC
2. Stat-Strip (Headcount, FTE, Arbeitgeberkosten p.a., Ø AG-Kosten/Kopf,
   Fluktuationsrate)
3. Datenlücken-Disclaimer — **nur** wenn `warnungen` nicht leer
4. Summary-Card „Kernbefund"
5. `<section id="headcount">` — Headcount & Struktur
6. `<section id="kosten">` — Personalkosten
7. `<section id="fluktuation">` — Fluktuation
8. `<section id="annahmen">` — Annahmen & Datenlücken

Steht der Report im Headcount-Modus (`kostendaten_verfuegbar: false`), entfällt
Sektion 6; der Disclaimer erklärt warum.

### Bausteine (Copy-Paste-Markup)

**Sticky-TOC**
```html
<nav class="toc" aria-label="Schnellzugriff">
  <strong>Schnellzugriff</strong>
  <a href="#headcount">Headcount</a>
  <a href="#kosten">Personalkosten</a>
  <a href="#fluktuation">Fluktuation</a>
  <a href="#annahmen">Annahmen</a>
</nav>
```

**Stat-Strip**
```html
<div class="stat-strip">
  <div class="stat"><span class="num">142</span><span class="lbl">Mitarbeiter</span></div>
  <div class="stat"><span class="num">128,5</span><span class="lbl">Vollzeitäquivalente</span></div>
  <div class="stat"><span class="num">9,41 Mio €</span><span class="lbl">Arbeitgeberkosten p.a.</span><span class="sub">geschätzt</span></div>
  <div class="stat"><span class="num">68.200 €</span><span class="lbl">Ø Kosten / Kopf</span><span class="sub">p.a., geschätzt</span></div>
  <div class="stat"><span class="num">7,8 %</span><span class="lbl">Fluktuation</span><span class="sub">12 Monate</span></div>
</div>
```

**Datenlücken-Disclaimer** (nur bei `warnungen`)
```html
<div class="disclaimer">
  <strong>Hinweis zur Datenlage:</strong> 4 von 142 Mitarbeitern haben keine
  Gehaltsangabe in den API-Daten und fehlen in den Kostensummen. Die
  Arbeitgeberkosten sind zudem eine Schätzung (Bruttogehalt × AG-Faktor 1,20),
  keine Ist-Abrechnungswerte.
</div>
```

**Summary-Card**
```html
<div class="summary-card">
  <h3>Kernbefund</h3>
  <p>Verdichteter Fließtext: Headcount und FTE, Höhe der Personalkosten, wo der
  Kostenschwerpunkt liegt, Auffälligkeiten bei Fluktuation oder Datenlage.</p>
  <p class="note">Stichtag 2026-05-22 · Quelle: Personio · read-only · vertraulich</p>
</div>
```

**Modul-Sektion**
```html
<section id="kosten">
  <div class="section-heading">
    <p class="label">Personalkosten</p>
    <h2>Was die Belegschaft als Arbeitgeber kostet</h2>
  </div>
  <p class="section-intro">Optionaler Einleitungssatz.</p>
  <!-- table.data, bar-row, ampel-grid … -->
</section>
```

**Kennzahl-Karten** (für KPI-Blöcke das Ampel-Grid ohne Wertung nutzen —
`data-ampel="gruen"` weglassen oder neutral lassen)
```html
<div class="ampel-grid">
  <div class="ampel-card">
    <p class="modul">Arbeitgeberkosten p.a.</p>
    <p class="urteil">9,41 Mio €</p>
    <p class="detail">Geschätzt, 138 Mitarbeiter mit Gehaltsangabe.</p>
  </div>
  <!-- weitere Karten -->
</div>
```

**Daten-Tabelle** (Abteilungs-Kostenverteilung)
```html
<table class="data">
  <thead><tr><th>Abteilung</th><th>Headcount</th><th>FTE</th><th>Arbeitgeberkosten p.a.</th></tr></thead>
  <tbody>
    <tr><td>Entwicklung</td><td>40</td><td>38,0</td><td>3.120.000 €</td></tr>
    <tr class="total"><td>Gesamt</td><td>142</td><td>128,5</td><td>9.408.000 €</td></tr>
  </tbody>
</table>
```

**Mini-Balken** (Kostenanteil je Abteilung, Status-Verteilung)
```html
<div class="bar-row">
  <span class="bar-label">Entwicklung</span>
  <span class="bar-track"><span class="bar-fill" style="width:33%"></span></span>
  <span class="bar-val">33 %</span>
</div>
```
> Beim `bar-fill` ist `style="width:NN%"` erlaubt — der einzige zulässige
> inline-`style` im Report, weil die Balkenbreite datengetrieben ist.

**Hinweis-Block** (für Datenlücken / Annahmen)
```html
<div class="suggestion mittel">
  <p class="label">Datenlücke</p>
  <p><strong>4 Mitarbeiter ohne Gehaltsangabe.</strong> Sie zählen in Headcount
  und FTE, fehlen aber in allen Kostensummen.</p>
</div>
```
Klasse ∈ {`suggestion hoch`, `suggestion mittel`, `suggestion niedrig`}.

### Inhaltliche Leitlinien

- **Geldwerte** im Report einheitlich deutsch formatieren (`9.408.000 €` oder
  `9,41 Mio €`); im Stat-Strip die kompakte Mio-Schreibweise, in Tabellen die
  volle Zahl.
- **Headcount vs. FTE** nie verwechseln — Headcount = Köpfe, FTE = Vollzeit-
  äquivalente.
- Die **Schätz-Natur** der Arbeitgeberkosten an mindestens einer prominenten
  Stelle ausschreiben (Disclaimer oder Summary-Card).
- **Keine Einzelgehälter** im HTML-Report — nur Summen, Schnitte, Abteilungs-
  Ebene. Einzelwerte stehen ausschließlich in der XLSX-Mappe.
- Den `gehalt_basis_verteilung`-Split (Festgehalt vs. Stundenlohn) erwähnen,
  wenn beide Gruppen relevant groß sind.

### Validierung vor dem Speichern

Keine offenen `{{…}}`-Platzhalter, nur Klassen aus `report-shell.html`, kein
inline-`style` außer `bar-fill`-Breite.
