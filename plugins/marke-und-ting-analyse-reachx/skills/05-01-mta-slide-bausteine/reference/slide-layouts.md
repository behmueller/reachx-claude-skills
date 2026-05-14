# Slide-Layout-Templates

Sieben wiederverwendbare Layouts fuer die MTA-Slide-Bausteine. Jedes Layout hat einen festen HTML-Aufbau und nutzt die CSS-Klassen aus `branding-snippet.md`. Bei der Generierung waehlt der Skill pro Sektion eines dieser Layouts (siehe `sektions-katalog.md`).

Jede Slide ist 1920x1080 (16:9). Slide-Container ist `<div class="slide">`, gefolgt von Sektions-spezifischen Bloecken plus `<div class="slide-meta">` als Footer.

---

## 1. cover

Erste Slide der MTA. Night-Sky-Hintergrund, grosser Kunden-Name in Display-Schrift, Sub-Zeile mit Datum und Stratege.

```
+--------------------------------------------------------------------+
| .slide.cover (Night-Sky-Background, Diagonal-Streifen oben rechts) |
|                                                                    |
|   .eyebrow ........... "MARKE&TING-Analyse"                        |
|                                                                    |
|   .display ........... KUNDEN-NAME                                 |
|                       <span class="accent">Status & Potenzial</span>|
|                                                                    |
|   .meta .............. 12. Mai 2026 · Strategie REACHX             |
|                                                                    |
|   [REACHX-Logo unten rechts]                                       |
+--------------------------------------------------------------------+
```

```html
<div class="slide cover">
  <p class="eyebrow">MARKE&amp;TING-Analyse</p>
  <h1 class="display">KUNDEN-NAME<br><span class="accent">Status &amp; Potenzial</span></h1>
  <p class="meta">12. Mai 2026 · Strategie REACHX</p>
  <div class="slide-meta">
    <span><span class="num">00</span> · Cover</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## 2. action-title-mit-tabelle

Action-Title oben, darunter eine Tabelle als Visualisierungs-Element. Gut fuer Sichtbarkeits-Vergleich, Wettbewerbs-Side-by-Side, Forecast-Tabelle, Abweichungs-Matrix.

```
+--------------------------------------------------------------------+
| .eyebrow  Sektion · NN                                             |
|                                                                    |
| .action-title                                                      |
| Drei Wettbewerber profilieren sich klar — der Kunde                |
| kann sich gezielt absetzen.                                        |
|                                                                    |
| [.body-stack mit Tabelle]                                          |
| +----------+--------+---------+-----------------+--------------+  |
| | Kriterium | Kunde | WB-1    | WB-2            | WB-3         |  |
| +----------+--------+---------+-----------------+--------------+  |
| | USP      | ...    | ...     | ...             | ...          |  |
| +----------+--------+---------+-----------------+--------------+  |
| ...                                                                |
+--------------------------------------------------------------------+
```

```html
<div class="slide">
  <p class="eyebrow">06 · Wettbewerber-Highlights</p>
  <h1 class="action-title">Drei Wettbewerber profilieren sich klar — der Kunde kann sich gezielt absetzen.</h1>

  <div class="body-stack">
    <table class="slide-table">
      <thead>
        <tr>
          <th>Kriterium</th>
          <th>Kunde</th>
          <th>WB-1</th>
          <th>WB-2</th>
          <th>WB-3</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>USP</strong></td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
        <tr>
          <td><strong>Tonalitaet</strong></td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
          <td>...</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="slide-meta">
    <span><span class="num">06</span> · Wettbewerber-Highlights</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## 3. action-title-mit-grafik

Action-Title oben, darunter eine SVG-Grafik (Linien-Chart, 2D-Positionierungs-Mapping, Timeline, etc.) als Hauptelement. Gut fuer Positionierung, Forecast, 90-Tage-Plan.

```
+--------------------------------------------------------------------+
| .eyebrow                                                           |
| .action-title                                                      |
|                                                                    |
| .graphic                                                           |
|   <svg>...</svg>                                                   |
|                                                                    |
+--------------------------------------------------------------------+
```

```html
<div class="slide">
  <p class="eyebrow">07 · Positionierung</p>
  <h1 class="action-title">Im Wettbewerbsumfeld bleibt der Quadrant <span class="accent">Premium-Persoenlich</span> frei.</h1>

  <div class="graphic">
    <svg viewBox="0 0 1200 700" width="1200" height="700">
      <!-- Achsen -->
      <line x1="100" y1="350" x2="1100" y2="350" stroke="var(--gray-divider)" stroke-width="2"/>
      <line x1="600" y1="50" x2="600" y2="650" stroke="var(--gray-divider)" stroke-width="2"/>

      <!-- Akteure als Punkte -->
      <circle cx="400" cy="200" r="20" fill="var(--sunrise-red)"/>
      <text x="430" y="205" font-family="Red Hat Display" font-weight="800" font-size="22">KUNDE</text>

      <circle cx="800" cy="500" r="16" fill="var(--day-break-blue)"/>
      <text x="825" y="505" font-family="Red Hat Text" font-weight="600" font-size="20">WB-1</text>

      <!-- Achsen-Labels -->
      <text x="100" y="380" font-family="Red Hat Text" font-weight="700" font-size="20" fill="var(--gray-medium)">formell</text>
      <text x="1050" y="380" font-family="Red Hat Text" font-weight="700" font-size="20" fill="var(--gray-medium)" text-anchor="end">informell</text>
    </svg>
  </div>

  <div class="slide-meta">
    <span><span class="num">07</span> · Positionierung</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

Wenn `synthese/positionierung.md` bereits ein vollstaendiges `<svg>...</svg>` enthaelt, dieses direkt einbetten — nicht neu rendern.

---

## 4. action-title-mit-3-blocks

Action-Title oben, darunter drei nummerierte Bloecke. Gut fuer Top-3-Empfehlungen (Kanal-Chancen, Retainer-Varianten), Drei-Kategorien-Splits (Wettbewerber-Uebersicht, Briefing-Rekap).

```
+--------------------------------------------------------------------+
| .eyebrow                                                           |
| .action-title                                                      |
|                                                                    |
| .three-blocks                                                      |
| +------------------+  +------------------+  +------------------+   |
| | 01               |  | 02               |  | 03               |   |
| | LABEL            |  | LABEL            |  | LABEL            |   |
| | Block-Titel      |  | Block-Titel      |  | Block-Titel      |   |
| | Beschreibung     |  | Beschreibung     |  | Beschreibung     |   |
| +------------------+  +------------------+  +------------------+   |
+--------------------------------------------------------------------+
```

```html
<div class="slide">
  <p class="eyebrow">13 · Kanal-Chancen</p>
  <h1 class="action-title">Drei Kanaele bringen 70 Prozent der erwarteten Wirkung in den ersten 12 Monaten.</h1>

  <div class="three-blocks">
    <div class="block">
      <span class="num">01</span>
      <span class="label">Score 9,2</span>
      <h3 class="title">SEO &amp; Content</h3>
      <p class="desc">14 Sweet-Spot-Cluster mit niedrigem Wettbewerb, 4.200 Suchvolumen, Kunde rankt fuer 15 Prozent.</p>
    </div>
    <div class="block">
      <span class="num">02</span>
      <span class="label">Score 7,8</span>
      <h3 class="title">Google Ads</h3>
      <p class="desc">Drei Wettbewerber kaufen sich Brand-Terms — defensiver Schutz-Layer + offensive Akquise-Kampagne.</p>
    </div>
    <div class="block">
      <span class="num">03</span>
      <span class="label">Score 6,5</span>
      <h3 class="title">LinkedIn Organic</h3>
      <p class="desc">B2B-Zielgruppe ist ueberwiegend auf LinkedIn, Posting-Frequenz der WBs &lt; 1/Woche — wenig Wettbewerb.</p>
    </div>
  </div>

  <div class="slide-meta">
    <span><span class="num">13</span> · Kanal-Chancen</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## 5. quote-slide

Grosses Kunden-Zitat aus dem Briefing als zentrales Element. Gut fuer Briefing-Rekapitulation und Eroeffnungs-Statements.

```
+--------------------------------------------------------------------+
| .eyebrow                                                           |
|                                                                    |
|   "                                                                |
|   Wir wollen in zwei Jahren                                        |
|   der Marktfuehrer in der DACH-Region sein.                        |
|                                                                    |
|   .attribution — Geschaeftsfuehrer, Kickoff-Meeting 12.05.2026     |
+--------------------------------------------------------------------+
```

```html
<div class="slide">
  <p class="eyebrow">02 · Briefing-Rekapitulation</p>

  <div class="quote">
    Wir wollen in zwei Jahren der Marktfuehrer in der DACH-Region sein.
    <p class="attribution">— Geschaeftsfuehrer, Kickoff-Meeting 12. Mai 2026</p>
  </div>

  <div class="slide-meta">
    <span><span class="num">02</span> · Briefing-Rekapitulation</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## 6. transition-slide

Sektions-Trenner mit Agenda-Liste oder Sektions-Vorschau. Hintergrund Night-Sky-Grey, grosse Nummern in Sunrise-Red. Gut fuer Agenda-Slide und Sektions-Eroeffnung.

```
+--------------------------------------------------------------------+
| .slide.transition (Night-Sky-Grey-Hintergrund)                     |
|                                                                    |
| .eyebrow ...... Agenda                                             |
|                                                                    |
| .action-title . So fuehrt diese Analyse zu einer klaren            |
|                 Investitionsentscheidung.                          |
|                                                                    |
| .agenda-list                                                       |
|   01 Markenanalyse                                                 |
|   02 Online-Marketing-Status                                       |
|   03 Kanal-Chancen                                                 |
|   04 Forecast                                                      |
|   05 Investition & Retainer                                        |
+--------------------------------------------------------------------+
```

```html
<div class="slide transition">
  <p class="eyebrow">Agenda</p>
  <h1 class="action-title">So fuehrt diese Analyse zu einer klaren Investitionsentscheidung.</h1>

  <ol class="agenda-list">
    <li>Markenanalyse</li>
    <li>Online-Marketing-Status</li>
    <li>Kanal-Chancen</li>
    <li>Forecast</li>
    <li>Investition &amp; Retainer</li>
  </ol>

  <div class="slide-meta">
    <span><span class="num">01</span> · Agenda</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## 7. closing

Letzte Slide(s) der MTA. Naechste-Schritte und Kontakt. Drei nummerierte Actions oder Kontakt-Block.

```
+--------------------------------------------------------------------+
| .eyebrow ...... Naechste Schritte                                  |
|                                                                    |
| .action-title . Drei Entscheidungen ermoeglichen den Start         |
|                 in den naechsten 14 Tagen.                         |
|                                                                    |
| .three-blocks                                                      |
| +------------------+  +------------------+  +------------------+   |
| | 01 To-Do         |  | 02 To-Do         |  | 03 To-Do         |   |
| +------------------+  +------------------+  +------------------+   |
|                                                                    |
| .contact (optional, fuer 19-naechste-schritte)                     |
|   STRATEGE-NAME · sascha@reachx.de · +49 ...                       |
+--------------------------------------------------------------------+
```

```html
<div class="slide">
  <p class="eyebrow">18 · Abschluss</p>
  <h1 class="action-title">Drei Entscheidungen ermoeglichen den Start in den naechsten 14 Tagen.</h1>

  <div class="three-blocks">
    <div class="block">
      <span class="num">01</span>
      <span class="label">Heute</span>
      <h3 class="title">Retainer-Variante waehlen</h3>
      <p class="desc">Drei Pakete liegen vor — konservativ, realistisch, ambitioniert.</p>
    </div>
    <div class="block">
      <span class="num">02</span>
      <span class="label">Diese Woche</span>
      <h3 class="title">Setup-Termin buchen</h3>
      <p class="desc">Strategie-Workshop fuer 90-Tage-Plan-Detailierung.</p>
    </div>
    <div class="block">
      <span class="num">03</span>
      <span class="label">Naechste Woche</span>
      <h3 class="title">Tracking-Freigaben erteilen</h3>
      <p class="desc">Google Analytics, Search Console, Ads-Accounts.</p>
    </div>
  </div>

  <div class="slide-meta">
    <span><span class="num">18</span> · Abschluss</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## Platzhalter-Slide (Sonder-Fall)

Wenn die Pflicht-Inputs fuer eine Sektion fehlen, aber die Sektion strukturell wichtig ist (z. B. Forecast), wird ein Platzhalter-Slide erzeugt — gleicher Action-Title, aber statt Visualisierung ein `.placeholder-note`-Block.

```html
<div class="slide">
  <p class="eyebrow">15 · Forecast</p>
  <h1 class="action-title">Das 12-Monats-Modell zeigt, ab wann die Investition rechnet.</h1>

  <div class="placeholder-note">
    <p class="label">Daten fehlen</p>
    <p>Forecast-Daten noch nicht generiert. Bitte zuerst <code>04-04-forecast-modell</code> laufen lassen.</p>
    <p style="margin-top:16px;">Sobald <code>synthese/forecast.md</code> vorhanden ist, kann diese Slide neu erzeugt werden mit Override "neu generieren".</p>
  </div>

  <div class="slide-meta">
    <span><span class="num">15</span> · Forecast</span>
    <span>MARKE&amp;TING-Analyse · KUNDE</span>
  </div>
</div>
```

---

## Layout-Auswahl-Regeln

| Wenn die Sektion ... | Layout |
|---|---|
| ein 2D-Mapping, Linien-Chart oder Timeline braucht | `action-title-mit-grafik` |
| eine Vergleichs-Tabelle (Kunde vs. Wettbewerber, KPI-Tabelle, Forecast-Tabelle) braucht | `action-title-mit-tabelle` |
| drei diskrete Empfehlungen, Kategorien oder Phasen hat | `action-title-mit-3-blocks` |
| ein zentrales Kunden-Zitat als Anker hat | `quote-slide` |
| eine Sektions-Eroeffnung oder Agenda-Slide ist | `transition-slide` |
| die erste oder letzte Slide ist | `cover` / `closing` |

Wenn keine Visualisierung passt: Default-Fallback ist `action-title-mit-3-blocks` mit den drei Kern-Aussagen. Auffaelligkeit `kein_visualisierungs_element` melden.

## CSS-Klassen-Index

Pflicht-Klassen pro Slide aus `branding-snippet.md`:

- `.slide` (Container, 1920x1080)
- `.slide.cover` (Cover-Variante, Night-Sky-Hintergrund)
- `.slide.transition` (Sektions-Trenner, Night-Sky-Grey-Hintergrund)
- `.eyebrow` (kleiner Label-Text oben in Sunrise-Red)
- `.action-title` (zentrale Aussage in Red Hat Display Black)
- `.action-title .accent` (Sunrise-Red-Akzent im Action-Title)
- `.body-stack` (Container fuer Body unter Action-Title)
- `.three-blocks` mit `.block` (Drei-Block-Layout)
- `.block .num`, `.label`, `.title`, `.desc` (Block-Inhalte)
- `.slide-table` (Tabellen-Variante mit Night-Sky-Header)
- `.graphic` (Container fuer SVG)
- `.quote` mit `.attribution` (Zitat-Layout)
- `.agenda-list` (Agenda-Liste fuer Transition-Slide)
- `.badge.stark|mittel|schwach|platzhalter` (Status-Badges)
- `.placeholder-note` (Hinweis-Block fuer fehlende Daten)
- `.slide-meta` (Footer-Zeile mit Slide-Nummer und Sektions-Name)
