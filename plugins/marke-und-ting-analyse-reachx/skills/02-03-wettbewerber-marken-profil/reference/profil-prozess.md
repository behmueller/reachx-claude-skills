# Multi-Wettbewerber-Verarbeitung

Operationelle Vorgaben für `02-03-wettbewerber-marken-profil` — wie der Skill mehrere Wettbewerber zuverlässig profiliert, ohne in Rate-Limits, Inkonsistenzen oder Endlosläufe zu rennen.

## 1. Slug-Generierung

Pro Wettbewerber wird ein eindeutiger Slug für den Dateinamen `wettbewerber/SLUG.md` und für Asset-Pfade benötigt.

### Reihenfolge der Slug-Quellen

1. **Domain ohne TLD und ohne Subdomain `www`**:
   - `https://www.beispiel-firma.de/` → `beispiel-firma`
   - `https://shop.musterag.com/` → `shop-musterag` (Subdomain bleibt, weil sie identitäts-relevant ist)
   - Mehrteilige Domains beibehalten, Bindestriche akzeptieren

2. **Wenn keine Website (Reduced-Mode)**: Aus dem Wettbewerber-`name`-Feld in `liste.md`:
   - lowercase
   - Umlaute auflösen (ä → ae, ö → oe, ü → ue, ß → ss)
   - alle Nicht-`[a-z0-9-]`-Zeichen durch `-` ersetzen
   - mehrfache Bindestriche zu einem zusammenfassen
   - führende und schließende Bindestriche entfernen
   - Beispiel: "Müller & Söhne GmbH" → `mueller-soehne-gmbh`

3. **Konflikt-Auflösung**: Wenn zwei Wettbewerber denselben Slug erzeugen (selten, aber möglich bei Sub-Marken oder Tippfehlern in der Liste):
   - Sortierung in der `liste.md` zählt — der erste behält den Slug
   - Konfliktende Slugs bekommen Suffix `-2`, `-3`, …
   - Im Skill-Schluss-Format als "Slug-Konflikt aufgelöst" ausweisen, damit der Stratege prüfen kann

### Beispiele

| Listen-Eintrag | Website | Slug |
|---|---|---|
| Mustermann GmbH | https://www.mustermann.de | `mustermann` |
| Müller & Söhne | https://mueller-soehne.de | `mueller-soehne` |
| ACME Werke (kein Web) | null | `acme-werke` |
| Beta Solutions | https://www.beta-solutions.com | `beta-solutions` |
| Beta-Solutions Berlin | https://beta-solutions-berlin.de | `beta-solutions-berlin` |
| Wettbewerber Nr. 1 (Tippfehler) | https://wb1.de | `wb1` |

## 2. Verarbeitungs-Modus: Sequenziell

Wettbewerber werden **nacheinander** verarbeitet, nicht parallel. Begründungen:

- **Apify-Rate-Limits**: Der `apify/website-content-crawler` und `apify/puppeteer-scraper` teilen sich das Account-Compute-Budget. Parallelisierung über mehrere gleichzeitige Actor-Runs erhöht die Wahrscheinlichkeit von 429er-Fehlern.
- **Vision-Modell-Auslastung**: Hero-Test braucht das Vision-Modell — sequenzielle Aufrufe sind robuster und debuggbarer.
- **Fortschritts-Transparenz**: Bei sequenzieller Verarbeitung kann der Skill nach jedem Wettbewerber den Stand in `status.md` zwischenspeichern. Bei einem Abbruch (Rate-Limit, Token-Issue) ist klar, was schon erledigt ist.

### Pausen zwischen Wettbewerbern

- Bei 1–4 Wettbewerbern: keine Pause nötig
- Bei 5–7 Wettbewerbern: 10 Sekunden Pause nach jedem dritten Crawl-Lauf, damit Apify-Queue nicht überlastet wird
- Wenn ein Crawl-Lauf länger als 5 Minuten braucht (Hänger): nach Timeout abbrechen, Wettbewerber als Reduced-Mode markieren, weitermachen

### Reihenfolge der Verarbeitung

Sortierung **vor** dem ersten Crawl festlegen, basierend auf strategischer Relevanz:

1. `kunde_genannt` mit `bedrohungsgrad: direkt`
2. `best_practice_ueberregional` (alle)
3. `kunde_genannt` mit `bedrohungsgrad: indirekt` oder `inspiration`
4. `regional`, sortiert nach `google_maps_reviews_count` absteigend

So sind die strategisch wichtigsten Profile zuerst fertig — falls der Lauf abbricht, sind die wertvollsten Daten schon erfasst.

## 3. Fehler-Recovery pro Wettbewerber

Jeder einzelne Wettbewerber kann unabhängig scheitern, ohne den Gesamt-Lauf zu blockieren. Pro Fehler-Typ:

| Fehler | Reaktion |
|---|---|
| Apify-Actor liefert leeres Crawl-Ergebnis (Cookie-Wall, JS-Wall) | Reduced-Mode, weiter mit nächstem WB |
| Apify-Token-Fehler / Auth | **Skill-Abbruch** (Recovery nicht möglich), bisher erstellte Profile bleiben erhalten |
| Apify-Rate-Limit (429) | 60 Sekunden warten, **einmal** retry — wenn weiter 429, **Skill-Abbruch** mit Hinweis, dass beim erneuten Aufruf nur die fehlenden Profile bearbeitet werden |
| Vision-Modell-Fehler beim Hero-Test | Hero-Test mit `null`-Scores schreiben, Hinweis im `crawl_luecken`, weiter mit den anderen Sektionen |
| Screenshot-Actor scheitert (Cookie-Wall ohne Bypass) | Profil ohne Screenshot schreiben, Hero-Test versuchen nur auf Markdown-Basis — Hinweis im Body, dass Hero-Test ohne Screenshot weniger zuverlässig ist |
| Slug-Generierung scheitert (z. B. exotischer Name) | Slug = `wettbewerber-INDEX` mit Hinweis im Schluss-Format |
| `wettbewerber/SLUG.md` schreibfehler (z. B. Disk voll) | **Skill-Abbruch**, bisher erstellte Profile bleiben erhalten |

### Zwischenspeicherung in `status.md`

Nach jedem **erfolgreich** abgeschlossenen Wettbewerber kann der Skill (optional, aber empfohlen) eine Mini-Aktualisierung in `status.md` vornehmen:

```yaml
in_arbeit:
  - skill: 02-03-wettbewerber-marken-profil
    fortschritt: "3 von 7 Wettbewerbern profiliert"
    profile_erstellt: [mustermann, beta-solutions, acme-werke]
```

Bei einem Abbruch sieht der nächste Lauf sofort, wo wieder anzusetzen ist. Beim erfolgreichen Komplettlauf wird `in_arbeit` entfernt und durch den normalen Eintrag in `schritte_done` ersetzt.

## 4. Cluster-Erkennung im Bundle-Report

Im Bundle-Report soll ein Hinweis-Block erscheinen, wenn Wettbewerber sich strukturell ähneln. Drei einfache Cluster-Indikatoren:

### a. Tonalitäts-Cluster

Zwei oder mehr Wettbewerber haben auf allen vier Tonalitäts-Achsen denselben Wert (±1). Hinweis-Text:

> "Wettbewerber X, Y, Z teilen eine sehr ähnliche Tonalität (formell-mittel, expertise-zentriert, sachlich, modern). Hinweis auf eine Marktnorm — Differenzierungs-Chance durch bewusst abweichende Markenstimme."

### b. USP-Cluster

Zwei oder mehr Wettbewerber haben sehr ähnliche USP-Formulierungen (manuelle Heuristik: gleiche Schlüsselbegriffe in zwei oder mehr USP-Sätzen). Beispiel: alle drei haben "individuelle Beratung" oder "30 Jahre Erfahrung" als Hauptdifferenzierung.

### c. Zielgruppen-Cluster

Zwei oder mehr Wettbewerber adressieren dieselbe Persona als primäre Zielgruppe.

### Schwellwert

Cluster nur ausweisen, wenn **mindestens 2 Wettbewerber** ähnlich sind UND die Ähnlichkeit nicht trivial ist (z. B. wenn alle "Qualität" als USP nennen, ist das kein Cluster — das ist Branchen-Standardphrase).

## 5. Vergleich mit `02-01-kunden-marken-profil` im Bundle-Report

Wenn `data/kunde.md` existiert, soll der Bundle-Report einen einfachen Side-by-Side-Block enthalten:

| Metrik | Kunde | Wettbewerber-Durchschnitt | Wettbewerber-Best |
|---|---|---|---|
| Hero-Test Gesamt | 3.5 | 2.8 | 4.0 (Wettbewerber X) |
| Verständlichkeit | 3 | 3.2 | 4 (Wettbewerber Y) |
| Touchpoint-Anzahl | 6 | 4.5 | 8 (Wettbewerber Z) |
| Tonalität formell-informell | -1 | -0.5 (mit Streuung -2 bis +1) | n/a |

**Wichtig:** das ist kein Ersatz für `04-01-positionierungs-analyse` — nur eine erste Orientierung. Im Block-Untertext explizit darauf verweisen:

> "Detaillierte Positionierungs-Analyse mit 2D-Mapping folgt in `04-01-positionierungs-analyse` (nach den Audit-Skills)."

## 6. Performance und Token-Budget

Realistische Schätzung pro Wettbewerber (für Strategen-Erwartungs-Management):

| Schritt | Dauer | Token-Verbrauch |
|---|---|---|
| Apify Website-Crawl | 1–3 Minuten | (außerhalb Token) |
| Screenshot | 20–40 Sekunden | (außerhalb Token) |
| Marken-Identität, Portfolio, USPs, Zielgruppen | LLM-Aufruf | ~3–6k Tokens |
| Tonalitäts-Analyse | LLM-Aufruf | ~2–4k Tokens |
| Hero-Test (Vision-Modell auf Screenshot) | Vision-Call | ~2–3k Tokens |
| Verständlichkeits-Bewertung | LLM-Aufruf | ~1–2k Tokens |
| Touchpoint-Extraktion | LLM-Aufruf | ~1–2k Tokens |
| Profil-Markdown schreiben | (Skill-intern) | minimal |

**Pro Wettbewerber: ~5–10 Minuten Echtzeit, ~10–17k Tokens.** Bei 7 Wettbewerbern: ca. 35–70 Minuten, ~70–120k Tokens.

Bei großen Läufen Stratege im Schluss-Format vorab informieren — oder klein anfangen (3 Wettbewerber) und nach Bestätigung erweitern.

## 7. Was NICHT in diesen Skill gehört

Damit der Skill seinen Scope behält:

- **Keine SEO-Analyse pro Wettbewerber** — das macht `03-01-seo-sichtbarkeit-und-rankings`
- **Keine Branchenportal-Recherche** — das macht `02-04-branchenportal-recherche`
- **Keine Social-Aktivitäts-Analyse** — das machen die plattformspezifischen Social-Audit-Skills
- **Keine Positionierungs-Achsen-Definition** — das macht `04-01-positionierungs-analyse` (Schema-vor-Lauf)
- **Keine Wettbewerber-Auswahl** — das macht `02-02-wettbewerber-identifikation`

Was gemacht wird: pro Wettbewerber dasselbe Marken-Profil wie für den Kunden, im selben Schema, damit später vergleichbar.
