---
name: 05-03-html-report-aus-analyse
description: Rendert einen beliebigen, in Claude Code erstellten Report (Markdown-Datei ODER Analyse-Inhalt aus dem Chatverlauf) zu einer self-contained HTML-Datei im REACHX-MTA-Design — Red Hat Display/Text, Sunrise-Red, Night-Sky, dieselben Bausteine wie alle MTA-Reports. Anders als die übrigen 05er-Skills ist dieser Skill NICHT MTA-projektgebunden: er braucht keine meta.json, kein Drive, kein Dashboard und läuft in jedem Claude-Code-Projekt. Erzeugt eine einzelne, im Browser öffenbare .html-Datei mit eingebettetem CSS. Nutze diesen Skill IMMER, wenn der Nutzer aus einer fertigen Analyse einen gestylten HTML-Report im MTA-Look will — auch bei Phrasen wie "mach mir daraus einen HTML-Report", "Report im MTA-Design", "HTML-Report aus dieser Analyse", "render das als HTML", "gestylter Report", "Analyse als HTML-Report", "REACHX-Report aus Markdown", "HTML-Report bauen". Setzt KEINEN MTA-Projektkontext voraus; funktioniert mit jeder Markdown-/Text-Quelle.
---

# HTML-Report aus beliebiger Analyse

Verwandelt einen beliebigen Report — eine Markdown-Datei oder eine Analyse, die nur im
Chatverlauf steht — in eine **self-contained HTML-Datei** im REACHX-MTA-Design.

**Abgrenzung zu den anderen 05er-Skills:** `05-01` und `05-02` sind MTA-pipeline-gebunden
(brauchen `meta.json`, Drive, Synthese-Outputs). Dieser Skill ist bewusst **kontextfrei** —
er nimmt irgendeinen Report und gibt eine einzelne `.html`-Datei zurück. Kein Drive-Upload,
kein `index.html`-Dashboard, kein Token-Footer.

**Architektur-Entscheidung — kein eigenes Design.** Der Skill erfindet kein CSS und keine
Bausteine. Er nutzt **dieselben drei kanonischen Plugin-Dateien** wie jeder MTA-Report:

| Datei | Rolle |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-shell.html` | Äußerer Rahmen + komplettes CSS — **unverändert** übernehmen |
| `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` | Einzige Markup-Quelle — die 12 Bausteine, 1:1 kopieren |
| `${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py` | Qualitäts-Gate vor dem Schreiben |

Dadurch sieht der Output garantiert MTA-konform aus und bleibt es auch, wenn sich die Shell
ändert. Die einzige skill-eigene Datei ist `reference/markdown-mapping.md` — die fehlende
Zutat: **welche Markdown-Struktur auf welchen Baustein abgebildet wird.**

## Ausführungs-Modus

Dieser Skill läuft im **Hauptthread**, nicht auf einem Subagent. Grund: liegt die Quelle nur
im Chatverlauf, hat ein Subagent diesen Kontext nicht. Die Markdown→Baustein-Zuordnung ist
zudem interpretierende Arbeit, kein reines Templating.

---

## Phase A — Struktur-Plan (Stopp vor dem Rendern)

Folgt dem Schema-vor-Lauf-Pattern des Plugins: erst Gliederung vorschlagen, bestätigen
lassen, dann rendern.

### A1 — Quelle bestimmen

Zwei Eingabe-Wege, beide zulässig:

- **Datei:** Der Nutzer nennt einen Pfad zu einer `.md`/`.txt`-Datei → mit `Read` einlesen.
- **Chat:** Die Analyse steht im laufenden Gespräch → den relevanten Inhalt aus dem
  Verlauf nehmen.

Ist unklar, was die Quelle ist, **einmal kurz nachfragen** — nie raten.

### A2 — Quelle analysieren

Den Quell-Report gegen `reference/markdown-mapping.md` lesen: Welche Überschriften-Ebenen,
welche Tabellen, welche Listen, welche Callouts, welche Kennzahlen, welche Zahlenreihen
gibt es? Daraus die Sektions-Gliederung ableiten.

### A3 — Hero-Metadaten festlegen

Die Shell hat acht Platzhalter (siehe `report-bausteine.md` → "Shell-Platzhalter"). Für
diesen Skill:

| Platzhalter | Quelle |
|---|---|
| `{{TITLE}}` | Browser-Tab: `<Report-Titel>` |
| `{{EYEBROW}}` | Kleiner Label-Text im Hero, z. B. `REACHX · Analyse` oder Report-Kategorie |
| `{{DISPLAY_NAME}}` | Große Hero-Überschrift = der Report-Titel |
| `{{META_LINE}}` | Meta-Zeile: Datenstand, Quelle, Verfasser — was zutrifft |
| `{{MAIN_CONTENT}}` | Der Report-Inhalt (Phase B) |
| `{{TOKEN_BREAKDOWN}}` | **leer lassen** — kein MTA-Dashboard |
| `{{TOKEN_FOOTER}}` | **leer lassen** — kein Token-Tracking |
| `{{FOOTER_TEXT}}` | Footer-Zeile, z. B. `REACHX · <Report-Titel> · <Datum>` |

So viel wie möglich aus dem Quell-Report ableiten. Fehlt Titel oder Eyebrow und ist nicht
ableitbar → in **einer gebündelten Frage** klären (Titel, Eyebrow, Output-Pfad).

### A4 — Gliederung vorschlagen und stoppen

Dem Nutzer eine **kompakte** Vorschau geben: pro Sektion die Überschrift und welche
Bausteine sie füllen. Beispiel:

```
1. Ausgangslage      → summary-card + stat-strip
2. Befunde           → table.ratings (mit Badges) + suggestion-Block
3. Empfehlungen      → ol.top3
Hero: "Marktanalyse Q2 2026" · Eyebrow "REACHX · Analyse" · Output: ./marktanalyse-q2.html
```

Bei freiem Fließtext ohne klare Überschriften: vorschlagen, **wie** der Text in Sektionen
geschnitten wird. **Stopp** — Bestätigung oder Korrektur des Nutzers abwarten.

---

## Phase B — Rendern, validieren, schreiben

### B1 — Shell laden

`report-shell.html` mit `Read` einlesen. Der `<style>`-Block wird **byte-genau unverändert**
übernommen — niemals CSS umbauen, ergänzen oder aus dem Gedächtnis rekonstruieren.

### B2 — `{{MAIN_CONTENT}}` aus Bausteinen bauen

Den Report-Inhalt **ausschließlich** aus den Bausteinen in `report-bausteine.md`
zusammensetzen. Die Zuordnung Markdown → Baustein steht in `reference/markdown-mapping.md` —
diese Datei jetzt lesen und anwenden. Regeln (aus `contracts.md` Abschnitt 7):

- **Markup kopieren, nicht erfinden** — das Markup kommt 1:1 aus `report-bausteine.md`.
- **Keine eigenen CSS-Klassen**, **kein inline-`style="…"`**, **kein eigener `<style>`-Block**.
- Ab drei Sektionen: Sticky-TOC oben einsetzen.

### B3 — Platzhalter füllen

Alle acht Platzhalter ersetzen (A3). Zusätzlich:

- **`<body>` bekommt die Klasse `is-dashboard`** — also `<body class="is-dashboard">`. Das
  blendet den Back-Link aus, den die Shell sonst im Hero rendert. Ein self-contained Report
  hat kein `index.html`, auf das der Back-Link zeigen könnte; `is-dashboard` ist der vom
  Shell-CSS unterstützte Weg, ihn sauber zu unterdrücken.
- `{{TOKEN_BREAKDOWN}}` und `{{TOKEN_FOOTER}}` durch leeren String ersetzen.

### B4 — Output schreiben

Die fertige HTML-Datei an den in A3/A4 vereinbarten Pfad schreiben (Default: `./<slug>.html`
im aktuellen Verzeichnis, `<slug>` aus dem Report-Titel). Eine einzelne, self-contained
Datei — CSS ist im `<style>`-Block eingebettet, die einzige externe Abhängigkeit ist der
Google-Fonts-CDN-Link aus der Shell (mit `sans-serif`-Fallback, identisch zu allen
MTA-Reports).

### B5 — Validieren (Pflicht vor dem Abschluss)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <output.html> --shell
```

Der Validator prüft drei Regeln: (1) jede verwendete CSS-Klasse ist im `<style>`-Block
definiert, (2) keine offenen `{{Platzhalter}}`, (3) der `<style>`-Block ist byte-identisch
mit der kanonischen Shell.

- **Exit-Code 0** → fertig, Pfad an den Nutzer melden, Öffnen im Browser anbieten.
- **Exit-Code 1** → **nicht abschließen.** Markup gegen `report-bausteine.md` korrigieren
  (meist eine erfundene Klasse oder ein offener Platzhalter) und erneut validieren.

---

## Was dieser Skill NICHT tut

- Kein Drive-Upload, kein `index.html`-Dashboard, kein Token-Tracking.
- Keine inhaltliche Recherche — er rendert nur, was im Quell-Report steht. Fehlende Daten
  werden nicht erfunden; eine dünne Quelle ergibt einen kurzen Report.
- Keine neuen Bausteine oder Farben — bei einer Struktur, die kein Baustein abbildet, wird
  auf den nächstpassenden Baustein zurückgegriffen (siehe `markdown-mapping.md`), nicht
  improvisiert.
