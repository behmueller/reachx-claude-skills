# Report-Bausteine — kanonische Markup-Bibliothek für MTA-HTML-Reports

**Dies ist die einzige Quelle für Report-Markup.** Jeder Skill, der einen HTML-Report
in den `reports/`-Ordner schreibt, baut `{{MAIN_CONTENT}}` **ausschließlich** aus den
Bausteinen dieser Datei zusammen — Markup 1:1 kopieren, nur die Inhalte ersetzen.

**Niemals** eigene CSS-Klassen erfinden, eigene `<style>`-Blöcke ergänzen oder
inline-`style="…"`-Attribute setzen. Alle hier verwendeten Klassen sind im CSS von
`report-shell.html` definiert — eine Klasse, die hier nicht vorkommt, existiert im
Shell-CSS nicht und rendert ungestylt.

Nach dem Rendern ist der Report mit `scripts/validate-report.py` zu prüfen (siehe
`contracts.md` Abschnitt 7) — der Validator schlägt an, sobald eine nicht-definierte
Klasse oder ein offener Platzhalter im Report steht.

---

## Shell-Platzhalter

Die Shell (`reports/_shell.html` auf Drive) hat exakt diese acht Platzhalter. Alle
müssen ersetzt werden — ein verbleibendes `{{…}}` ist ein Fehler.

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | Browser-Tab-Titel: `<Skill-Titel> · <Kunde>` |
| `{{EYEBROW}}` | Kleiner Label-Text im Hero: z. B. `MTA-Audit · SEO` |
| `{{DISPLAY_NAME}}` | Große Hero-Überschrift: der Report-Titel |
| `{{META_LINE}}` | Meta-Zeile unter dem Titel: Quelle, Datenstand, Akteur-Anzahl |
| `{{MAIN_CONTENT}}` | Der Report-Inhalt — ausschließlich aus den Bausteinen unten |
| `{{TOKEN_BREAKDOWN}}` | Nur Dashboard: voller Token-Breakdown. Sonst leer lassen. |
| `{{TOKEN_FOOTER}}` | Footer-Counter via `token-tracker.py render-skill-counter` |
| `{{FOOTER_TEXT}}` | Footer-Zeile: `MTA · <Kunde> · <Report-Typ>` |

`{{MAIN_CONTENT}}` steht zwischen `<main><div class="container">` und `</div></main>` —
also **nur** der Inhalt, kein `<main>`, kein `<body>`, kein `<html>` mit hineinschreiben.

---

## 1. Sektion mit Section-Heading

Jede thematische Einheit des Reports ist eine `<section>` mit `id` (für die TOC) und
einem `.section-heading`. Das `.label` ist der Eyebrow, das `<h2>` der Titel.

**Wann:** Immer — die oberste Gliederungsebene jedes Reports.

```html
<section id="sichtbarkeit">
  <div class="section-heading">
    <p class="label">01 — Sistrix-Sicht</p>
    <h2>Organische Sichtbarkeit im Vergleich</h2>
  </div>
  <p class="section-intro">Optionaler Einleitungssatz, max. ~820px breit.</p>

  <!-- Inhalt der Sektion: Tabellen, Karten, Suggestion-Blöcke … -->
</section>
```

---

## 2. Sticky-TOC (Schnellzugriff)

Steht **einmal ganz oben** in `{{MAIN_CONTENT}}`, vor der ersten `<section>`. Die
`href`-Anker zeigen auf die `id` der jeweiligen Sektion.

**Wann:** Sobald der Report mehr als zwei Sektionen hat.

```html
<nav class="toc" aria-label="Schnellzugriff">
  <strong>Schnellzugriff</strong>
  <a href="#sichtbarkeit">Sistrix-Sicht</a>
  <a href="#ahrefs">Ahrefs-Sicht</a>
  <a href="#auffaelligkeiten">Auffälligkeiten</a>
</nav>
```

---

## 3. Summary-Card

Weiße Karte für die hervorgehobene Zusammenfassung. `.note` ist der optionale,
ausgegraute Hinweis-Block am Fuß der Karte.

**Wann:** Executive Summary, Kernaussage am Anfang einer Sektion.

```html
<div class="summary-card">
  <h3>Kernbefund</h3>
  <p>Verdichteter Fließtext mit den wichtigsten Beobachtungen.</p>
  <p class="note">Datenstand: 2026-05-17 · Quelle: Sistrix + Ahrefs</p>
</div>
```

---

## 4. Stat-Strip

Reihe von Kennzahlen. `.num` ist der Wert (rendert groß und in Sunrise-Red), `.lbl`
das Label darunter.

**Wann:** Kennzahlen-Überblick am Anfang einer Sektion oder eines Reports.

```html
<div class="stat-strip">
  <div class="stat"><span class="num">3,8</span><span class="lbl">Sichtbarkeitsindex</span></div>
  <div class="stat"><span class="num">Platz 3</span><span class="lbl">von 9 Akteuren</span></div>
  <div class="stat"><span class="num">+12 %</span><span class="lbl">Trend 12 Monate</span></div>
  <div class="stat"><span class="num">247</span><span class="lbl">Top-100-Keywords</span></div>
</div>
```

---

## 5. Daten-Tabelle

`table.data` für normale tabellarische Daten. `tr.total` für eine optionale
Summen-/Abschlusszeile.

**Wann:** Master-Tabellen, Keyword-Listen, jede Zeilen-Spalten-Daten.

```html
<table class="data">
  <thead>
    <tr><th>Akteur</th><th>Typ</th><th>SI aktuell</th><th>Trend</th></tr>
  </thead>
  <tbody>
    <tr><td>Kunde GmbH</td><td>Kunde</td><td>3,8</td><td>+12 %</td></tr>
    <tr><td>Wettbewerber A</td><td>regional</td><td>5,1</td><td>−3 %</td></tr>
    <tr class="total"><td>Median</td><td>—</td><td>4,2</td><td>+2 %</td></tr>
  </tbody>
</table>
```

---

## 6. Ratings-Tabelle

`table.ratings` — wie `table.data`, aber die erste Spalte rendert fett und groß
(für Bewertungs-Achsen, Dimensionen, Kriterien).

**Wann:** Bewertungs-Tabellen, bei denen die erste Spalte die Achse benennt.

```html
<table class="ratings">
  <thead>
    <tr><th>Dimension</th><th>Bewertung</th><th>Begründung</th></tr>
  </thead>
  <tbody>
    <tr><td>Tonalität</td><td><span class="badge stark">Stark</span></td><td>Konsistent über alle Touchpoints.</td></tr>
    <tr><td>Hero-Test</td><td><span class="badge mittel">Mittel</span></td><td>Nutzen erkennbar, CTA schwach.</td></tr>
  </tbody>
</table>
```

---

## 7. Badges

Inline-Label. Zwei Familien: **Audit-Ratings** und **Status**. Nur diese acht
Modifier existieren — kein weiterer.

**Wann:** Rating-/Status-Markierung in Tabellen, Karten-Summaries, Listen.

```html
<!-- Audit-Ratings -->
<span class="badge stark">Stark</span>
<span class="badge mittel">Mittel</span>
<span class="badge schwach">Schwach</span>

<!-- Status -->
<span class="badge vorhanden">Vorhanden</span>
<span class="badge in-arbeit">In Arbeit</span>
<span class="badge geplant">Geplant</span>
<span class="badge neutral">Neutral</span>
```

---

## 8. Expandable-Karte (`details.dim`)

Aufklappbare Karte — ein Block pro Akteur, Cluster, Kanal o. ä. Das `data-rating`
färbt den linken Rand (`stark` grün, `mittel` orange, `schwach` rot). `data-rating`
ist optional — ohne Attribut bleibt der Rand grau.

`open` als Attribut auf `<details>` setzt die Karte aufgeklappt (Konvention: Kunde
und Top-2 aufgeklappt, der Rest zugeklappt).

**Wann:** Detail-Block pro Akteur/Cluster/Kanal — der häufigste Audit-Baustein.

```html
<details class="dim" data-rating="stark" open>
  <summary>
    <strong>Kunde GmbH</strong>
    <span class="badge stark">SI 3,8</span>
  </summary>
  <div class="body">
    <h4>SI-Verlauf</h4>
    <p>Inhalt der Karte — Tabellen, Listen, Sparklines.</p>
  </div>
</details>

<details class="dim" data-rating="mittel">
  <summary>
    <strong>Wettbewerber A</strong>
    <span class="badge mittel">SI 5,1</span>
  </summary>
  <div class="body">
    <p>Zugeklappte Karte ohne <code>open</code>.</p>
  </div>
</details>
```

---

## 9. Suggestion-Block

Hervorgehobener Empfehlungs-/Auffälligkeiten-Block mit rotem linken Rand.

**Wann:** Auffälligkeiten-Block, strategische Empfehlung, Lücken-Hinweis.

```html
<div class="suggestion">
  <p class="label">Auffälligkeit</p>
  <p>Wettbewerber A rankt auf 40 transaktionalen Keywords, auf denen der Kunde
  nicht sichtbar ist — größter Gap im commercial-Intent.</p>
</div>
```

---

## 10. Workflow-/Step-Grid

Vier-Spalten-Grid aus nummerierten Schritten in einer `.workflow-card`.

**Wann:** Prozess-Darstellung, Phasen, nummerierte Vorgehensschritte.

```html
<div class="workflow-card">
  <h3>Vorgehen in vier Schritten</h3>
  <div class="workflow-steps">
    <div class="step">
      <span class="num">01</span>
      <div class="ttl">Setup</div>
      <div class="desc">Tracking und Konten aufsetzen.</div>
    </div>
    <div class="step">
      <span class="num">02</span>
      <div class="ttl">Kampagne</div>
      <div class="desc">Erste Kampagnen live schalten.</div>
    </div>
    <div class="step">
      <span class="num">03</span>
      <div class="ttl">Skalierung</div>
      <div class="desc">Budget auf Gewinner verschieben.</div>
    </div>
    <div class="step">
      <span class="num">04</span>
      <div class="ttl">Optimierung</div>
      <div class="desc">Conversion-Rate iterativ verbessern.</div>
    </div>
  </div>
</div>
```

---

## 11. Top-N-Liste

Nummerierte Liste mit großem Sunrise-Red-Kreis je Eintrag.

**Wann:** Top-3-Empfehlungen, priorisierte Hebel, Ranking-Aussagen.

```html
<ol class="top3">
  <li><strong>SEO-Content-Offensive</strong> — 12 BOFU-Cluster ohne Kunden-Ranking, hohes Volumen.</li>
  <li><strong>Google Ads auf Marken-Keywords</strong> — Wettbewerber bietet auf die Kunden-Marke.</li>
  <li><strong>Local-SEO an drei Standorten</strong> — GMB-Profile unvollständig, schnell zu heben.</li>
</ol>
```

---

## 12. Inline-SVG-Sparkline

Sparklines werden **nicht** improvisiert — dieser Baustein ist verbindlich. Eine
Sparkline ist ein `<svg>` mit `viewBox="0 0 100 28"`. Die Punkte sind eine
`points`-Liste; `x` läuft 0→100 gleichmäßig, `y` ist `28 − (wert − min) / (max − min) × 24 + 2`
(Y ist invertiert, oben = hoher Wert). Über **alle** Sparklines eines Reports den
**gleichen** `min`/`max` verwenden, damit die Kurven vergleichbar bleiben.

**Wann:** 12-Monats-Verläufe (SI, DR, Forecast-Kurven) pro Akteur/Kanal.

```html
<svg viewBox="0 0 100 28" preserveAspectRatio="none" width="120" height="34" role="img" aria-label="12-Monats-Verlauf">
  <polyline fill="none" stroke="#ec644a" stroke-width="2"
    stroke-linejoin="round" stroke-linecap="round"
    points="0,20 9,18 18,19 27,15 36,16 45,12 54,13 63,10 72,11 81,8 90,9 100,6" />
</svg>
```

Mehrere Linien (z. B. Forecast worst/real/best) — zusätzliche `<polyline>` mit
`stroke="#999da1"` (worst) bzw. `stroke="#66ae77"` (best), `stroke-width="1.5"`.

---

## Vollständige Klassen-Liste

Diese Klassen — und nur diese — sind im Shell-CSS definiert und im
`{{MAIN_CONTENT}}`-Bereich nutzbar:

`section-heading`, `label`, `section-intro`, `toc`, `summary-card`, `note`,
`stat-strip`, `stat`, `num`, `lbl`, `data`, `total`, `ratings`, `badge`, `stark`,
`mittel`, `schwach`, `vorhanden`, `in-arbeit`, `geplant`, `neutral`, `dim`, `body`,
`suggestion`, `workflow-card`, `workflow-steps`, `step`, `ttl`, `desc`, `top3`.

Vom Shell-Rahmen selbst belegt (nicht in `{{MAIN_CONTENT}}` neu setzen):
`container`, `hero`, `eyebrow`, `display`, `meta`, `back-link`, `is-dashboard`.
