# MTA-Sektions-Katalog

Vollstaendige Story-Struktur einer REACHX-MARKE&TING-Analyse mit Input-Mapping und Layout-Empfehlung pro Sektion. Pro Sektion ein eigenes HTML-Slide-File `synthese/slide-bausteine/NN-slug.html`.

Die Reihenfolge ist die Praesentations-Reihenfolge. Skip-Logik pro Sektion ist in der Spalte `Skip-Regel` dokumentiert.

## Sektions-Liste

### 00 — Cover

- **Slug:** `cover`
- **Pflicht-Inputs:** `meta.json` (kunde, kunden_slug, projekt_slug, kickoff_datum)
- **Optionale Inputs:** Kunden-Logo in `assets/`
- **Layout:** `cover`
- **Action-Title-Vorlage:** keine — Cover hat reinen Titel "MARKE&TING-Analyse" plus Kundenname und Datum
- **Pflicht-Elemente:** REACHX-Logo unten rechts, Kunden-Logo zentriert (oder Kunden-Schriftzug, wenn kein Logo), Datum, Stratege-Name (aus `meta.json` wenn vorhanden, sonst "REACHX Strategie")
- **Skip-Regel:** niemals — Cover ist immer dabei
- **Status `voll`:** `meta.json` vorhanden mit gefuellten Pflichtfeldern

### 01 — Agenda

- **Slug:** `agenda`
- **Pflicht-Inputs:** (keine — strukturell aus dem Sektions-Katalog selbst)
- **Layout:** `transition-slide` mit numerierter Liste
- **Action-Title-Vorlage:** "So fuehrt diese Analyse zu einer klaren Investitionsentscheidung."
- **Pflicht-Elemente:** numerierte Liste der MTA-Hauptkapitel (Markenanalyse, Online-Marketing-Status, Kanal-Chancen, Forecast, Investition, Retainer)
- **Skip-Regel:** niemals

### 02 — Briefing-Rekapitulation

- **Slug:** `briefing-rekap`
- **Pflicht-Inputs:** `data/briefing.md`
- **Layout:** `quote-slide` (wenn Kunden-Zitate aus Briefing extrahierbar) oder `action-title-mit-3-blocks` (Ziele/Pain/Erwartung)
- **Action-Title-Vorlage:** "Drei Kern-Aussagen aus dem Briefing pruefen wir hier auf Tragfaehigkeit."
- **Pflicht-Elemente:** Drei Bloecke: "Geschaeftsziele", "Pain Points", "Erwartung an REACHX" — jeweils 2-3 Bullets aus dem Briefing
- **Skip-Regel:** niemals — auch ohne Briefing wird Sektion als Platzhalter erzeugt mit Hinweis "Briefing-Datei fehlt, 01-02-kickoff-transcript-parser zuerst laufen lassen"

### 03 — Marken-Profil (Kunde)

- **Slug:** `marken-profil`
- **Pflicht-Inputs:** `data/kunde.md`
- **Optionale Inputs:** Screenshot der Kunden-Website in `assets/`
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** auf Basis Hero-Test-Score
  - Score >= 7: "Die Markenkommunikation ist klar — das Fundament fuer Wachstum steht."
  - Score 4-6: "Die Markenkommunikation hat klare Staerken, aber an drei Punkten fehlt Schaerfe."
  - Score < 4: "Die Markenkommunikation ist die erste Stellschraube — Hero-Test scheitert an drei Punkten."
- **Pflicht-Elemente:** Tabelle mit Tonalitaets-Achsen (4 Achsen mit Bewertungs-Skala) + Hero-Test-Score
- **Skip-Regel:** niemals

### 04 — Abweichungs-Analyse

- **Slug:** `abweichungen`
- **Pflicht-Inputs:** `data/abweichungen.md`
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** "Briefing und Website-Realitaet zeigen drei Diskrepanzen, die wir loesen muessen."
- **Pflicht-Elemente:** Tabelle mit Spalten "Aussage Briefing", "Realitaet Website", "Diskrepanz-Typ", "Handlungs-Empfehlung"
- **Skip-Regel:** Wenn `data/abweichungen.md` nicht existiert → `skip` (kann passieren wenn kein Briefing da war)

### 05 — Wettbewerber-Uebersicht

- **Slug:** `wettbewerber-uebersicht`
- **Pflicht-Inputs:** `wettbewerber/liste.md` (Frontmatter `status: bestaetigt`)
- **Layout:** `action-title-mit-3-blocks`
- **Action-Title-Vorlage:** "Drei Wettbewerbs-Kategorien rahmen die Positionierung des Kunden."
- **Pflicht-Elemente:** drei Bloecke fuer "vom Kunden genannt", "regional", "Best-Practice ueberregional" — jeweils mit 3-5 Logos/Namen
- **Skip-Regel:** Wenn weniger als 2 WBs in `liste.md` mit `status: bestaetigt` → `platzhalter` mit Hinweis "02-02-wettbewerber-identifikation Status noch nicht bestaetigt"

### 06 — Wettbewerber-Highlights

- **Slug:** `wettbewerber-highlights`
- **Pflicht-Inputs:** mindestens 2 Marken-Profile in `wettbewerber/*.md` (ausgenommen `liste.md` und `identifikation-schema.md`)
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** "Drei Wettbewerber profilieren sich klar — der Kunde kann sich gezielt absetzen."
- **Pflicht-Elemente:** Side-by-Side-Tabelle (max 5 WBs) mit Zeilen "USP", "Tonalitaet", "Zielgruppen-Hypothese", "Hero-Test-Score"
- **Skip-Regel:** Wenn weniger als 2 WB-Profile vorhanden → `platzhalter`

### 07 — Positionierung

- **Slug:** `positionierung`
- **Pflicht-Inputs:** `synthese/positionierung.md`
- **Layout:** `action-title-mit-grafik`
- **Action-Title-Vorlage:** aus dem `kern_aussage`-Frontmatter-Feld der Positionierungs-Analyse
- **Pflicht-Elemente:** 2D-SVG-Mapping (wenn in `synthese/positionierung.md` Body als `<svg>...</svg>` enthalten, direkt einbetten — sonst Achsen-Skelett mit Punkten aus den Akteurs-Daten neu rendern)
- **Skip-Regel:** Wenn `synthese/positionierung.md` fehlt → `platzhalter` mit Hinweis "04-01-positionierungs-analyse zuerst laufen lassen"

### 08 — SEO-Status

- **Slug:** `seo-status`
- **Pflicht-Inputs:** `audits/seo-sichtbarkeit.md` oder `audits/seo-cluster-zusammenfassung.md`
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** auf Basis Sichtbarkeits-Verhaeltnis
  - Kunde < 0.5 × Median-Wettbewerber: "Im SEO laeuft der Kunde dem Wettbewerb um Faktor X hinterher — das ist der schnellste Hebel."
  - Kunde innerhalb Faktor 2: "Im SEO liegt der Kunde im Mittelfeld — drei Cluster oeffnen den Vorsprung."
  - Kunde >2 × Median: "Im SEO ist der Kunde Marktfuehrer — die Aufgabe ist Verteidigung, nicht Aufholjagd."
- **Pflicht-Elemente:** Tabelle mit Sichtbarkeits-Index Kunde vs. WB-Top-3, Top-5 Gap-Cluster, Median-Difficulty
- **Skip-Regel:** Wenn keine SEO-Audit-Outputs vorhanden → `platzhalter`

### 09 — Ads-Status

- **Slug:** `ads-status`
- **Pflicht-Inputs:** mindestens einer von `audits/google-ads-*.md`, `audits/meta-ads-*.md`, `audits/linkedin-ads-*.md`
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** auf Basis Aktivitaets-Muster
  - Kunde inaktiv, WBs aktiv: "Bezahlte Reichweite spielt der Kunde nicht — drei Wettbewerber holen sich darueber den ersten Termin."
  - Kunde aktiv: "Bezahlte Reichweite ist gesetzt, drei Stellschrauben heben die Effizienz."
- **Pflicht-Elemente:** Tabelle Plattform x Akteur mit Aktivitaets-Status, Schaetz-Budget, Tonalitaet
- **Skip-Regel:** Wenn keine Ads-Audit-Outputs vorhanden → `platzhalter`

### 10 — Website-Tech & Tracking

- **Slug:** `website-tech`
- **Pflicht-Inputs:** `audits/website-tech-tracking.md`
- **Layout:** `action-title-mit-3-blocks`
- **Action-Title-Vorlage:** "Drei Tech-Hebel verhindern aktuell, dass Marketing-Investitionen messbar werden."
- **Pflicht-Elemente:** drei Bloecke "Technologie-Stack", "Tracking-Status", "Core Web Vitals" mit je 2-3 Befunden
- **Skip-Regel:** Wenn Audit fehlt → `platzhalter`

### 11 — Local-SEO

- **Slug:** `local-seo`
- **Pflicht-Inputs:** `audits/gmb-local-seo.md`
- **Layout:** `action-title-mit-3-blocks`
- **Action-Title-Vorlage:** "Local-SEO ist das Quick-Win-Fundament fuer den Region-X-Kunden."
- **Pflicht-Elemente:** drei Bloecke "GMB-Status", "Bewertungs-Lage", "Local-Keyword-Sichtbarkeit"
- **Skip-Regel:** wenn `meta.json.region` leer oder `audits/gmb-local-seo.md` fehlt → `skip` (Branchen-Irrelevanz signalisiert)

### 12 — Social-Status

- **Slug:** `social-status`
- **Pflicht-Inputs:** mindestens ein `audits/<plattform>-*.md` (Instagram, LinkedIn, TikTok, Pinterest)
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** "Eine Social-Plattform traegt heute schon — zwei weitere bieten ungenutztes Potenzial."
- **Pflicht-Elemente:** Tabelle Plattform x Akteur mit Follower, Posting-Frequenz, Post-Qualitaet, Letzte-Aktivitaet
- **Skip-Regel:** wenn kein Social-Audit vorhanden → `platzhalter`

### 13 — Kanal-Chancen

- **Slug:** `kanal-chancen`
- **Pflicht-Inputs:** `synthese/kanal-chancen.md`
- **Layout:** `action-title-mit-3-blocks`
- **Action-Title-Vorlage:** "Drei Kanaele bringen 70 Prozent der erwarteten Wirkung in den ersten 12 Monaten."
- **Pflicht-Elemente:** drei nummerierte Bloecke (Top-3-Kanaele) mit Kanal-Name, Score, Begruendung in 2 Saetzen
- **Skip-Regel:** Wenn Datei fehlt → `platzhalter`

### 14 — Ziele

- **Slug:** `ziele`
- **Pflicht-Inputs:** `synthese/ziele.md` oder `data/briefing.md` (Briefing-Ziele)
- **Layout:** `action-title-mit-tabelle`
- **Action-Title-Vorlage:** "Die abgeleiteten Ziel-Bandbreiten geben dem 12-Monats-Forecast Halt."
- **Pflicht-Elemente:** Tabelle mit KPI-Bandbreiten (konservativ / realistisch / ambitioniert) pro KPI (z. B. Sichtbarkeit, Leads, Umsatz)
- **Skip-Regel:** Wenn weder abgeleitete-ziele noch Briefing-Ziele vorhanden → `platzhalter`

### 15 — Forecast

- **Slug:** `forecast`
- **Pflicht-Inputs:** `synthese/forecast.md`
- **Layout:** `action-title-mit-grafik`
- **Action-Title-Vorlage:** "Das 12-Monats-Modell zeigt, ab wann die Investition rechnet."
- **Pflicht-Elemente:** Linien-Chart als inline SVG (3 Linien: konservativ, realistisch, ambitioniert) oder Tabelle mit 12 Monaten als Spalten und KPIs als Zeilen
- **Skip-Regel:** Wenn Datei fehlt → kritischer Platzhalter mit prominentem Hinweis (Forecast ist Kern der MTA)

### 16 — 90-Tage-Plan

- **Slug:** `90-tage-plan`
- **Pflicht-Inputs:** `synthese/90-tage-plan.md`
- **Layout:** `action-title-mit-grafik`
- **Action-Title-Vorlage:** "Die ersten 90 Tage entscheiden, ob das Forecast-Modell tragfaehig ist."
- **Pflicht-Elemente:** Timeline-Grafik mit Phasen (Setup, Aktivierung, Skalierung) und Meilensteinen pro Monat
- **Skip-Regel:** Wenn Datei fehlt → `platzhalter`

### 17 — Retainer-Empfehlung

- **Slug:** `retainer`
- **Pflicht-Inputs:** `synthese/retainer.md`
- **Layout:** `action-title-mit-3-blocks`
- **Action-Title-Vorlage:** "Drei Retainer-Varianten bilden konservatives bis ambitioniertes Ambitionsniveau ab."
- **Pflicht-Elemente:** drei Bloecke mit Paket-Namen, Monats-Investition, enthaltene Leistungen, passend zu welchem Ziel-Szenario
- **Skip-Regel:** Wenn Datei fehlt → kritischer Platzhalter (Retainer ist die Conversion-Frage der MTA)

### 18 — Abschluss

- **Slug:** `abschluss`
- **Pflicht-Inputs:** keine
- **Layout:** `closing`
- **Action-Title-Vorlage:** "Drei Entscheidungen ermoeglichen den Start in den naechsten 14 Tagen."
- **Pflicht-Elemente:** drei To-Dos fuer den Kunden (Retainer-Variante waehlen, Setup-Termin buchen, Tracking-Freigaben erteilen)
- **Skip-Regel:** niemals

### 19 — Naechste Schritte / Q&A

- **Slug:** `naechste-schritte`
- **Pflicht-Inputs:** `meta.json` fuer Kontakt-Information
- **Layout:** `closing`
- **Action-Title-Vorlage:** "Wir freuen uns auf den naechsten Termin."
- **Pflicht-Elemente:** Kontakt-Block (Stratege-Name, REACHX-Adresse, E-Mail, Telefon), Termin-Vorschlag (placeholder), QR-Code-Placeholder fuer Kalender-Link
- **Skip-Regel:** niemals

## Slide-Status

Pro Sektion einer der drei Werte:

- `voll` — alle Pflicht-Inputs vorhanden, Slide mit echten Daten gerendert
- `platzhalter` — Pflicht-Inputs fehlen, Sektion strukturell wichtig: Slide mit Hinweis-Text "Daten fehlen, Skill X zuerst laufen lassen"
- `skip` — Sektion branchen-irrelevant (z. B. Local-SEO ohne lokales Geschaeft), im Index als ausgelassen markiert

Die Slide-Status-Liste wird vom Skill am Ende in das HTML-Dashboard und in den Skill-Report geschrieben.

## Naming-Konvention der HTML-Files

```
synthese/slide-bausteine/
├── 00-cover.html
├── 01-agenda.html
├── 02-briefing-rekap.html
├── 03-marken-profil.html
├── 04-abweichungen.html
├── 05-wettbewerber-uebersicht.html
├── 06-wettbewerber-highlights.html
├── 07-positionierung.html
├── 08-seo-status.html
├── 09-ads-status.html
├── 10-website-tech.html
├── 11-local-seo.html
├── 12-social-status.html
├── 13-kanal-chancen.html
├── 14-ziele.html
├── 15-forecast.html
├── 16-90-tage-plan.html
├── 17-retainer.html
├── 18-abschluss.html
├── 19-naechste-schritte.html
└── index.html
```

Skip-Sektionen werden weiterhin durch ein leeres Placeholder-HTML repraesentiert, damit die Index-Reihenfolge stabil bleibt — im Index als `skip` markiert und mit `display: none` ausgeblendet (Stratege kann via Index-Toggle aktivieren).
