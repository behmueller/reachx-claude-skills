# Markdown → Baustein-Mapping

Diese Datei ist die fehlende Zutat des Skills: **welche Struktur im Quell-Report auf
welchen Baustein abgebildet wird.** Die Bausteine selbst (das fertige Markup) stehen in
`01-01-mta-projekt-init/reference/report-bausteine.md` — diese Datei sagt nur, *wann*
welcher Baustein dran ist.

Grundregel: Der Quell-Report bestimmt den Inhalt, das Mapping bestimmt die Form. Niemals
Daten erfinden, um einen Baustein zu füllen — passt kein Baustein gut, lieber den
schlichteren wählen (`table.data` statt `table.ratings`, Fließtext statt `stat-strip`).

---

## 1. Mapping-Tabelle

| Struktur im Quell-Report | Ziel-Baustein | Regel |
|---|---|---|
| Erste `#`-Überschrift / Dokumenttitel | Hero `{{DISPLAY_NAME}}` | Wird **nicht** zur Section — wandert in den Hero. |
| `##`-Überschrift | `<section>` + `.section-heading` (Baustein 1) | `id` = Slug der Überschrift. `.label` = optionaler Eyebrow (eine führende Nummer wie „01 — …" oder eine Kategorie), `<h2>` = Überschriftstext. |
| Erster Absatz direkt nach einer `##`-Überschrift, kurz (≲300 Zeichen) | `.section-intro` | Längerer Einleitungstext → normaler `<p>` oder `summary-card`. |
| Absatz/Abschnitt „Zusammenfassung", „Kernbefund", „Fazit", „Executive Summary", „TL;DR", „Management Summary" | `summary-card` (Baustein 3) | `<h3>` = Überschrift, Datenstand/Quelle → `.note`. |
| `###`-Überschriften, **mehrfach gleichartig** (ein Block je Akteur/Kanal/Cluster/Item) | `details.dim`-Karten (Baustein 8) | `data-rating` aus einem Bewertungs-Wort im Block ableiten (siehe §2). Die ersten 1–3 Karten `open`, der Rest zu. |
| `###`-Überschrift, **einmalig** | `<h3>` innerhalb der Section | Direkt, kein Karten-Baustein. |
| `####`-Überschrift | `<h4>` | Direkt — `<h4>` rendert als Label (uppercase) im Shell-CSS. |
| Markdown-Tabelle, generische Zeilen-Spalten-Daten | `table.data` (Baustein 5) | Eine Summen-/Median-/Gesamt-Zeile → `<tr class="total">`. |
| Markdown-Tabelle, erste Spalte = Dimension/Kriterium/Achse, weitere Spalten = Bewertung | `table.ratings` (Baustein 6) | Erste Spalte rendert dann groß und fett. |
| Bewertungs-/Status-Wort in einer Tabellenzelle oder am Zeilenanfang | `<span class="badge …">` (Baustein 7) | Wort → Modifier siehe §2. Das Wort durch das Badge **ersetzen**, nicht doppeln. |
| Blockquote (`>`) oder Absatz mit Präfix „Empfehlung:", „Auffälligkeit:", „Hinweis:", „Achtung:", „Lücke:", „Risiko:", „Chance:" | `suggestion`-Block (Baustein 9) | Präfix → `.label`, Rest → `<p>`. |
| Nummerierte Liste, die als **Ranking/Priorisierung** lesbar ist (Top-N Hebel, Empfehlungen, Prioritäten) | `ol.top3` (Baustein 11) | Erstes **fettes** Element je Eintrag = Titel, Rest = Erläuterung. Funktioniert für beliebig viele Einträge, nicht nur drei. |
| Nummerierte Liste, die **Prozess-Schritte/Phasen** beschreibt (3–5 Schritte) | `workflow-card` + `workflow-steps` (Baustein 10) | `.num` = `01`…, `.ttl` = Schritt-Titel, `.desc` = Beschreibung. Bei mehr als ~5 Schritten → `ol.top3` oder `table.data`. |
| Kennzahlen-Block: Liste/Tabelle aus Wert + Label, oder Sätze wie „**3,8** Sichtbarkeitsindex" | `stat-strip` (Baustein 4) | `.num` = Wert, `.lbl` = Label. 3–6 Stats pro Strip; gehört an den Anfang einer Section oder direkt unter den Hero. |
| Zahlenreihe mit ≥6 Werten, erkennbar ein Zeitverlauf (Monate, Quartale) | Inline-SVG-Sparkline (Baustein 12) | Y-Formel und gemeinsame `min`/`max`-Skala strikt aus Baustein 12 übernehmen. |
| Report hat mehr als zwei `##`-Sektionen | Sticky-TOC (Baustein 2) | Einmal ganz oben in `{{MAIN_CONTENT}}`, `href`-Anker = Section-`id`s. |
| Aufzählung mit `-`/`*` ohne der obigen Sonderfälle | siehe §3 | — |
| Inline-Code, Links | `<code>`, `<a>` | Direkt übernehmen — beide sind im Shell-CSS gestylt. |
| Bild / eingebettete Grafik | weglassen | Der Skill bettet keine Bilder ein. Im Bestätigungsschritt erwähnen. |

---

## 2. Bewertungs-Wort → Badge-Modifier

Es gibt **exakt sieben** Badge-Modifier — keinen weiteren. Zwei Familien:

**Rating-Familie** (Qualitäts-/Stärke-Urteil):

| Wörter im Quell-Report | Modifier | Render |
|---|---|---|
| stark, gut, hoch, top, exzellent, erfüllt | `badge stark` | grün |
| mittel, ok, teilweise, durchschnittlich, ausbaufähig | `badge mittel` | orange |
| schwach, schlecht, niedrig, gering, fehlt, kritisch | `badge schwach` | rot |

**Status-Familie** (Zustand/Fortschritt):

| Wörter im Quell-Report | Modifier | Render |
|---|---|---|
| vorhanden, aktiv, live, umgesetzt, ja | `badge vorhanden` | grün-hell |
| in arbeit, in bearbeitung, läuft, WIP | `badge in-arbeit` | sand |
| geplant, offen, vorgesehen, todo | `badge geplant` | blau-hell |
| neutral, k. A., unklar, n/a, — | `badge neutral` | grau |

Das `data-rating`-Attribut der `details.dim`-Karte kennt nur `stark` / `mittel` / `schwach`
(färbt den linken Rand). Status-Wörter mappen dort auf das nächstliegende Rating oder das
Attribut bleibt weg (Rand grau).

Steht im Quell-Report ein Urteil, das in keine Familie passt, → `badge neutral` und das
Original-Wort als Badge-Text.

---

## 3. Aufzählungslisten — Sonderfall

Das Shell-CSS stylt **kein generisches `<ul>`** (nur `ol.top3`). Eine schlichte
`<ul>`-Liste rendert daher mit Browser-Default — validator-konform und akzeptabel, aber
nicht „gestaltet". Daher:

- **Kurze Stichpunkt-Liste innerhalb** einer `summary-card` oder eines `details.dim`-`.body`
  → als `<ul>` belassen. Im Kontext der Karte sieht das sauber aus.
- **Liste, die eigentlich Zeilen-Daten ist** (jeder Punkt hat dieselbe Struktur, z. B.
  „Name — Wert — Kommentar") → in `table.data` umbauen.
- **Liste, die eine Priorisierung ist** → `ol.top3`.
- **Liste pro Akteur/Item mit jeweils mehreren Unterpunkten** → `details.dim`-Karten, die
  Unterpunkte als `<h4>` + `<p>` im `.body`.

Freistehende `<ul>`-Listen direkt im `{{MAIN_CONTENT}}` (außerhalb einer Karte) möglichst
vermeiden — lieber in einen der obigen Bausteine überführen.

---

## 4. Umgang mit unstrukturiertem Quell-Text

Liegt die Analyse als freier Fließtext ohne Überschriften vor:

1. Den Text in thematische Blöcke lesen — jeder Block wird eine `##`-Section.
2. Den eröffnenden Absatz / die Kernaussage → `summary-card`.
3. Genannte Zahlen, die zusammengehören → `stat-strip`.
4. Klare Empfehlungen / Warnungen → `suggestion`-Block.
5. Diese vorgeschlagene Gliederung in **Phase A4** dem Nutzer zur Bestätigung zeigen,
   bevor gerendert wird.

Lässt sich ein Block keinem Baustein sinnvoll zuordnen → schlichter `<p>`-Fließtext
innerhalb der Section. Das ist immer zulässig und besser als ein erzwungener Baustein.

---

## 5. Reihenfolge innerhalb einer Section

Bewährte Abfolge, wenn die Elemente vorhanden sind:

1. `.section-heading` (Pflicht)
2. `.section-intro` (optional, ein Satz)
3. `stat-strip` (wenn Kennzahlen vorhanden)
4. `summary-card` (wenn ein Kernbefund vorhanden)
5. Tabellen / `details.dim`-Karten / Fließtext — der Hauptteil
6. `suggestion`-Block (Auffälligkeit/Empfehlung am Ende der Section)

`ol.top3` und `workflow-card` stehen meist in einer eigenen, eigenen Section („Empfehlungen",
„Vorgehen").

---

## 6. Kurzbeispiel

**Quell-Markdown:**

```markdown
## Sichtbarkeit
Der Kunde liegt im Mittelfeld.

| Akteur | SI | Bewertung |
|---|---|---|
| Kunde GmbH | 3,8 | mittel |
| Wettbewerber A | 5,1 | stark |

Empfehlung: Content-Offensive auf BOFU-Cluster.
```

**Ziel-`{{MAIN_CONTENT}}`-Fragment:**

```html
<section id="sichtbarkeit">
  <div class="section-heading">
    <p class="label">Analyse</p>
    <h2>Sichtbarkeit</h2>
  </div>
  <p class="section-intro">Der Kunde liegt im Mittelfeld.</p>
  <table class="data">
    <thead><tr><th>Akteur</th><th>SI</th><th>Bewertung</th></tr></thead>
    <tbody>
      <tr><td>Kunde GmbH</td><td>3,8</td><td><span class="badge mittel">Mittel</span></td></tr>
      <tr><td>Wettbewerber A</td><td>5,1</td><td><span class="badge stark">Stark</span></td></tr>
    </tbody>
  </table>
  <div class="suggestion">
    <p class="label">Empfehlung</p>
    <p>Content-Offensive auf BOFU-Cluster.</p>
  </div>
</section>
```
