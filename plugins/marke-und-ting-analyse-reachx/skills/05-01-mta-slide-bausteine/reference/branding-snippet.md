# REACHX-Branding-Snippet fuer Slide-Bausteine

Slide-spezifisches CSS, das in jede einzelne Slide-HTML-Datei inline eingefuegt wird. Basiert auf der Shell-CSS aus `01-01-mta-projekt-init/reference/report-shell.html`, aber slide-optimiert: 16:9-Format, groessere Schriften, weniger Container-Margins.

Jede Slide-Datei ist **self-contained** — keine externen Stylesheets, kein gemeinsames JS. Damit kann der Stratege eine einzelne Slide als File verschicken oder per Druck-Funktion als PDF exportieren.

## Pflicht-CSS-Block (pro Slide)

```html
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>NN — Sektion · KUNDE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@400;500;700;800;900&family=Red+Hat+Text:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --font-display: "Red Hat Display", sans-serif;
    --font-text: "Red Hat Text", sans-serif;
    --fw-regular: 400;
    --fw-medium: 500;
    --fw-semibold: 600;
    --fw-bold: 700;
    --fw-extrabold: 800;
    --fw-black: 900;

    --white: #fff;
    --night-sky-grey: #f2f3f3;
    --night-sky-dark-blue: #000a14;
    --sunrise-red: #ec644a;
    --sunrise-red-light: #ff8d6d;
    --sunrise-orange: #feae77;
    --sunrise-yellow: #fcd299;
    --sunrise-sand: #f5e1cc;
    --day-break-blue: #4a7ded;
    --day-break-blue-light: #e6edfc;
    --gray-medium: #999da1;
    --gray-light: #d5d5d8;
    --gray-divider: #d9d9d9;

    /* Slide-spezifische Token */
    --slide-w: 1920px;
    --slide-h: 1080px;
    --slide-padding: 96px 128px;
    --action-title-size: 56px;
    --body-size: 28px;
    --small-size: 22px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 100%;
    height: 100%;
    background: var(--night-sky-grey);
    font-family: var(--font-text);
    color: var(--night-sky-dark-blue);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

  /* Slide-Container — Print-Format 1920x1080 */
  .slide {
    width: var(--slide-w);
    height: var(--slide-h);
    background: var(--white);
    padding: var(--slide-padding);
    position: relative;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 0 auto;
  }

  /* Bildschirm-Anpassung — Slide skaliert proportional in das Browser-Viewport */
  @media screen and (max-width: 1920px) {
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .slide {
      transform-origin: top left;
      transform: scale(calc(100vw / 1920));
      margin: 0;
    }
    body::after {
      content: "";
      display: block;
      width: 100vw;
      height: calc(100vw * 1080 / 1920);
    }
  }

  /* Slide-Nummer + Kunde in Footer */
  .slide-meta {
    position: absolute;
    bottom: 48px;
    left: 128px;
    right: 128px;
    display: flex;
    justify-content: space-between;
    font-family: var(--font-text);
    font-size: var(--small-size);
    font-weight: var(--fw-medium);
    color: var(--gray-medium);
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .slide-meta .num { color: var(--sunrise-red); font-weight: var(--fw-bold); }

  /* Eyebrow ueber Action-Title (z. B. Sektions-Label) */
  .eyebrow {
    font-family: var(--font-text);
    font-size: var(--small-size);
    font-weight: var(--fw-bold);
    color: var(--sunrise-red);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 24px;
  }

  /* Action-Title — die zentrale Aussage der Slide */
  .action-title {
    font-family: var(--font-display);
    font-weight: var(--fw-black);
    font-size: var(--action-title-size);
    line-height: 1.18;
    color: var(--night-sky-dark-blue);
    margin-bottom: 48px;
    max-width: 1600px;
  }
  .action-title .accent { color: var(--sunrise-red); }

  /* Stuetzpunkte (Body unter Action-Title) */
  .body-stack {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 32px;
    font-size: var(--body-size);
    line-height: 1.4;
  }

  /* Drei-Block-Layout */
  .three-blocks {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
    flex: 1;
  }
  .three-blocks .block {
    background: var(--night-sky-grey);
    padding: 40px 36px;
    border-left: 8px solid var(--sunrise-red);
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .three-blocks .block .num {
    font-family: var(--font-display);
    font-weight: var(--fw-black);
    font-size: 36px;
    color: var(--sunrise-red);
    line-height: 1;
  }
  .three-blocks .block .label {
    font-family: var(--font-text);
    font-size: var(--small-size);
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--night-sky-dark-blue);
  }
  .three-blocks .block .title {
    font-family: var(--font-display);
    font-weight: var(--fw-extrabold);
    font-size: 32px;
    line-height: 1.2;
    color: var(--night-sky-dark-blue);
  }
  .three-blocks .block .desc {
    font-size: 22px;
    line-height: 1.4;
    color: var(--night-sky-dark-blue);
  }

  /* Tabelle */
  table.slide-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 24px;
    background: var(--white);
    box-shadow: 0 0 24px 0 #0003;
  }
  table.slide-table th, table.slide-table td {
    padding: 20px 24px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid var(--gray-divider);
  }
  table.slide-table th {
    background: var(--night-sky-dark-blue);
    color: var(--white);
    font-family: var(--font-text);
    font-weight: var(--fw-bold);
    font-size: var(--small-size);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  table.slide-table tr:last-child td { border-bottom: none; }
  table.slide-table .highlight { color: var(--sunrise-red); font-weight: var(--fw-bold); }

  /* Grafik-Container */
  .graphic {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
  }
  .graphic svg { max-width: 100%; max-height: 100%; }

  /* Quote-Slide */
  .quote {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    font-family: var(--font-display);
    font-weight: var(--fw-bold);
    font-size: 48px;
    line-height: 1.3;
    color: var(--night-sky-dark-blue);
    padding-right: 200px;
  }
  .quote::before {
    content: "„";
    font-family: var(--font-display);
    font-weight: var(--fw-black);
    font-size: 200px;
    line-height: 0.5;
    color: var(--sunrise-red);
    margin-bottom: 16px;
  }
  .quote .attribution {
    margin-top: 32px;
    font-family: var(--font-text);
    font-weight: var(--fw-semibold);
    font-size: 24px;
    color: var(--gray-medium);
    text-transform: none;
  }

  /* Cover- und Closing-Layouts */
  .cover {
    background: var(--night-sky-dark-blue);
    color: var(--white);
  }
  .cover .eyebrow { color: var(--sunrise-red); }
  .cover .display {
    font-family: var(--font-display);
    font-weight: var(--fw-black);
    font-size: 96px;
    line-height: 1.1;
    margin-bottom: 32px;
  }
  .cover .display .accent { color: var(--sunrise-red); }
  .cover .meta { font-size: 28px; color: var(--gray-light); }
  .cover::before {
    content: "";
    position: absolute;
    top: 0;
    right: 0;
    width: 400px;
    height: 100%;
    background-image: repeating-linear-gradient(-48deg,
      transparent 0,
      transparent 30px,
      rgba(236, 100, 74, 0.15) 30px,
      rgba(236, 100, 74, 0.15) 60px);
    pointer-events: none;
  }

  /* Transition-Slide */
  .transition {
    background: var(--night-sky-grey);
  }
  .transition .agenda-list {
    list-style: none;
    counter-reset: agenda;
    display: flex;
    flex-direction: column;
    gap: 24px;
    font-size: 36px;
  }
  .transition .agenda-list li {
    counter-increment: agenda;
    display: flex;
    align-items: center;
    gap: 32px;
  }
  .transition .agenda-list li::before {
    content: counter(agenda, decimal-leading-zero);
    font-family: var(--font-display);
    font-weight: var(--fw-black);
    font-size: 48px;
    color: var(--sunrise-red);
    min-width: 80px;
  }

  /* Badges fuer Status-Anzeige (z. B. Sweet-Spot, Gap, etc.) */
  .badge {
    display: inline-flex;
    align-items: center;
    font-family: var(--font-text);
    font-size: 18px;
    font-weight: var(--fw-bold);
    padding: 6px 14px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-radius: 2px;
  }
  .badge.stark { background: #66ae77; color: var(--white); }
  .badge.mittel { background: var(--sunrise-orange); color: var(--night-sky-dark-blue); }
  .badge.schwach { background: var(--sunrise-red); color: var(--white); }
  .badge.platzhalter { background: var(--gray-divider); color: var(--night-sky-dark-blue); }

  /* Platzhalter-Slide (wenn Daten fehlen) */
  .placeholder-note {
    background: var(--sunrise-sand);
    border-left: 8px solid var(--sunrise-red);
    padding: 40px 48px;
    margin-top: 32px;
    font-size: var(--body-size);
    line-height: 1.4;
  }
  .placeholder-note .label {
    font-family: var(--font-text);
    font-size: var(--small-size);
    font-weight: var(--fw-bold);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--sunrise-red);
    margin-bottom: 12px;
  }

  /* Print-Optimierung — PDF-Export */
  @page {
    size: 1920px 1080px;
    margin: 0;
  }
  @media print {
    body { background: var(--white); display: block; min-height: auto; }
    body::after { display: none; }
    .slide { transform: none; margin: 0; box-shadow: none; }
  }
</style>
</head>
<body>

<div class="slide">
  <!-- Slide-Inhalt hier — siehe slide-layouts.md fuer die einzelnen Layouts -->

  <div class="slide-meta">
    <span><span class="num">NN</span> · SEKTIONS-NAME</span>
    <span>MARKE&TING-Analyse · KUNDE</span>
  </div>
</div>

</body>
</html>
```

## Branding-Regeln

1. **Schriften** — `Red Hat Display` (Headlines, Action-Titles, Display-Elemente) und `Red Hat Text` (Body, Stuetzpunkte, Tabellen, Footer). Geladen ueber Google Fonts mit Preconnect-Optimierung.

2. **Farben** — Verbindlich:
   - `--night-sky-dark-blue: #000a14` — Primaer-Text, Cover-Hintergrund
   - `--sunrise-red: #ec644a` — Akzente, Hervorhebungen, Cover-Highlight, Action-Title-Spans
   - `--night-sky-grey: #f2f3f3` — Body-Hintergrund, Block-Hintergrund
   - `--white: #fff` — Slide-Hintergrund (Standard)
   - `--gray-medium: #999da1` — Sekundaer-Text, Footer

3. **Hierarchie** — Pro Slide nur EIN Action-Title (groesste Schriftgroesse). Stuetzpunkte sind 50% so gross wie der Action-Title. Sekundaer-Infos (Footer, Slide-Nummer, Eyebrow) sind 30% so gross.

4. **Spacing** — Slide-Padding `96px 128px` (oben/unten 96px, links/rechts 128px). Block-Abstand 32px. Action-Title-Bottom-Margin 48px.

5. **Slide-Footer** — IMMER unten links die Slide-Nummer in Sunrise-Red plus Sektions-Name, unten rechts "MARKE&TING-Analyse · KUNDE".

6. **Cover-Slide ist Night-Sky-Hintergrund**, alle anderen Slides sind White-Hintergrund mit Sektions-Bloecken in Night-Sky-Grey.

7. **SVG-Grafiken** muessen die CSS-Variablen referenzieren (z. B. `fill="var(--sunrise-red)"`) und max. die Slide-Innenmasse einhalten.

## Schrift-Skalierung pro Slide-Element

| Element | Schriftgroesse | Schrift | Gewicht |
|---|---|---|---|
| Cover-Display | 96px | Red Hat Display | 900 (Black) |
| Action-Title | 56px | Red Hat Display | 900 (Black) |
| Block-Titel | 32px | Red Hat Display | 800 (Extra-Bold) |
| Block-Num | 36px | Red Hat Display | 900 (Black) |
| Body-Text | 28px | Red Hat Text | 400 (Regular) |
| Tabellen-Body | 24px | Red Hat Text | 400-700 |
| Block-Desc | 22px | Red Hat Text | 400 (Regular) |
| Small-Text / Eyebrow / Tabelle-Header | 22px | Red Hat Text | 700 (Bold) |
| Slide-Meta (Footer) | 22px | Red Hat Text | 500 (Medium) |
| Badge | 18px | Red Hat Text | 700 (Bold) |

Bei extrem langen Action-Titles (>72 Zeichen) reduzieren auf 48px und max. 2 Zeilen. Wenn das nicht passt: `slide_text_zu_lang` melden.
