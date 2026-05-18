---
name: 02-01-kunden-marken-profil
description: Erstellt aus der Kunden-Website das strukturierte Marken-Profil mit Portfolio, USPs, Zielgruppen-Hypothese, Tonalität (4 Achsen), Hero-Test (Donald-Miller-Methodik), Verständlichkeits-Bewertung und Touchpoint-Inventur. Wenn ein Briefing vorliegt, wird zusätzlich data/abweichungen.md mit den Diskrepanzen zwischen Briefing und Website erzeugt. Nutze diesen Skill IMMER, wenn der Nutzer im Kontext einer laufenden MTA die Kunden-Marke analysieren will - auch bei Phrasen wie "Kunden-Marken-Profil erstellen", "Analysiere die Website von [Kunde]", "Mach das Markenprofil für unseren Kunden", "Brand-Audit der Kunden-Website", "Werte die Website von [Kunde] aus", "Erstelle das Marken-Profil aus aufmaster.de". Auch dann nutzen, wenn der Nutzer nach Hero-Test oder Tonalitäts-Analyse für die laufende MTA fragt. Setzt voraus, dass 01-01-mta-projekt-init bereits gelaufen ist - bricht sonst mit Hinweis ab.
---

# Kunden-Marken-Profil

Erstellt aus der Kunden-Website ein strukturiertes Marken-Profil mit identischer Struktur zu `02-03-wettbewerber-marken-profil` — damit die Synthese-Skills später Side-by-Side vergleichen können.

Sieben Dimensionen werden erfasst: Marken-Identität (Name, Synonyme, Claim), Portfolio (wie kommuniziert), USPs (wie kommuniziert), Zielgruppen-Hypothese aus Website-Inhalten, Tonalität (4 Achsen), Hero-Test nach Donald Miller, Verständlichkeit der Startseite, Touchpoint-Inventur.

Wenn `data/briefing.md` vorliegt, wird zusätzlich `data/abweichungen.md` erzeugt — die Diskrepanzen zwischen Eigenwahrnehmung im Kickoff und tatsächlicher Website-Kommunikation. Das ist oft der wertvollste Output dieses Skills.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="<name-dieses-skills>"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Report-Render zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Wann triggern

- "Kunden-Marken-Profil erstellen"
- "Analysiere die Website von [Kunde]"
- "Brand-Audit der Kunden-Website"
- "Erstelle das Marken-Profil aus [URL]"
- "Mach den Hero-Test für die Kunden-Website"
- Nutzer fragt nach Tonalitäts-Analyse oder Hero-Test im MTA-Kontext

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden, mit `website` befüllt
- Optional, aber stark empfohlen: `01-02-kickoff-transcript-parser` gelaufen → `data/briefing.md` vorhanden (für Abweichungs-Analyse)
- **Pflicht-MCP:** Apify (für Website-Crawl und Screenshot). Vor dem ersten Crawl-Aufruf Health-Check durchführen (contracts.md Abschnitt 11):
  ```bash
  # Credential-Check — nur diese eine Variable, keine breite Suche
  [ -n "$APIFY_TOKEN" ] || { echo "✗ APIFY_TOKEN nicht gesetzt."; exit 1; }
  ```
  Schlägt der Check fehl: sauberer Abbruch mit Hinweis — kein Fallback auf eigenes Crawling.

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

Ermittle den Drive-Folder der aktiven MTA über den Active-MTA-Cache und lies `meta.json`:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  python3 "$DRIVE_PY" list-mtas
  echo "✗ MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

SLUG=$(jq -r '.projekt_slug' /tmp/meta.json)
WEBSITE=$(jq -r '.website' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

### Schritt 1: Voraussetzungs-Check

Wenn `META_ID` leer ist:

```
✗ Kein gültiger MTA-Folder.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Prüfe in `data/` auf eine bereits existierende `kunde.md`:

```bash
EXISTING_KUNDE=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "kunde.md") | .id')
```

Wenn vorhanden: frage **überschreiben / Backup-und-neu / abbrechen**.

Prüfe, ob `data/briefing.md` auf Drive existiert — merke dir den Status für Schritt 10:

```bash
BRIEFING_ID=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "briefing.md") | .id')
```

### Schritt 2: Website crawlen

Nutze Apify zum Crawlen. **Erste Wahl: `apify/website-content-crawler`** mit folgenden Parametern:

- `startUrls`: nur die `website`-URL aus `meta.json`
- `maxCrawlPages`: 40 (Default — genug für ein gutes Marken-Profil, ohne übertrieben)
- `maxCrawlDepth`: 3
- `crawlerType`: `playwright:chrome` (deckt SPAs ab, ist nur unwesentlich langsamer)
- `saveMarkdown`: true
- `saveHtml`: true (für Link-Extraktion)
- `removeCookieWarnings`: true

Bei Apify-MCP-Zugang über die verfügbaren Tools, sonst direkter API-Aufruf mit `APIFY_TOKEN`.

Ergebnis: Liste der gecrawlten Seiten mit Titel, Markdown-Inhalt, URL, ggf. HTML. Speichere die Roh-Daten lokal in `~/.cache/reachx-mta/<slug>/website-crawl.json` und lade sie am Ende des Skill-Laufs als `website-crawl-<kunden-slug>.json` in den `assets/`-Sub-Folder auf Drive hoch (idealerweise per `gzip` komprimiert, weil Apify-JSONs groß werden können).

### Schritt 3: Startseite-Screenshot

Für den Hero-Test brauchen wir den visuellen Eindruck der Startseite. Nutze entweder:

- **`apify/puppeteer-scraper`** mit Page-Function für `page.screenshot()` (Standard: Viewport 1440×900, kein Vollseiten-Shot — wir wollen nur den Above-the-Fold-Bereich)
- Oder fallback: aus dem website-content-crawler-Output, falls dieser Screenshot-Funktion hat

Speichere lokal in `~/.cache/reachx-mta/<slug>/<kunden-slug>-startseite.png` und lade am Skill-Ende per `drive.py upsert-text` (MIME `image/png`) in den `assets/`-Sub-Folder auf Drive hoch. Bei Cookie-Wall: erst Cookie-Banner akzeptieren oder ausblenden (Apify-Optionen nutzen), dann Screenshot.

```bash
python3 "$DRIVE_PY" upsert-text "$ASSETS_ID" "<kunden-slug>-startseite.png" \
  ~/.cache/reachx-mta/"$SLUG"/<kunden-slug>-startseite.png "image/png"
```

Optional zusätzlich Mobile-Variante (375×812) als `<kunden-slug>-startseite-mobile.png` im `assets/`-Sub-Folder — wenn die Branche typisch hohen Mobile-Anteil hat (Local Services, B2C, Retail).

### Schritt 4: Marken-Identität extrahieren

Aus den gecrawlten Inhalten (vor allem Startseite + About/Impressum):

- `marke.name` → wie heißt sich die Firma selbst (oft nicht identisch mit Domain)
- `marke.synonyme` → alternative Schreibweisen, Kürzel, ggf. Marken-Versionen (z. B. "REACHX" / "Reach X" / "ReachX")
- `marke.claim` → Haupt-Claim, falls auf Startseite prominent platziert

Wenn ein Logo extrahierbar ist (`<img>`-Tag mit "logo" im Alt oder Pfad), als `<kunden-slug>-logo.png` in den `assets/`-Sub-Folder auf Drive hochladen (via `drive.py upsert-text` mit MIME `image/png`).

### Schritt 5: Portfolio, USPs, Zielgruppen-Hypothese

Aus den Inhalten der gecrawlten Seiten:

**Portfolio:** Welche Produkte/Dienstleistungen werden auf welchen Seiten beworben? Pro Produkt: Name, kurze Beschreibung, Kategorie, Quell-URL. Quelle ist die *Website*, nicht das Briefing.

**USPs wie kommuniziert:** Welche Differenzierungs-Aussagen finden sich auf der Website? Pro USP: kurzer Beleg (Zitat unter 25 Wörter), Quell-URL. **Nicht** Marketing-Floskeln ("Wir sind die Besten") aufnehmen, sondern konkrete Differenzierungs-Aussagen.

**Zielgruppen-Hypothese:** Aus Sprache, Bildwelt, beworbenen Anwendungsfällen — wer ist die Zielgruppe laut Website? Mit konkreten Belegen aus dem Crawl.

### Schritt 6: Tonalitäts-Analyse (4 Achsen)

Lies `reference/methodik.md` Abschnitt 2 für die genaue Methodik. Für jede der vier Achsen:

1. **Formell ↔ Informell**
2. **Expertise-zentriert ↔ Partnerschaftlich**
3. **Sachlich ↔ Emotional**
4. **Modern ↔ Traditionell**

Setze einen Wert von -2 bis +2, dazu ein knappes Label (was bedeutet die Position konkret), plus 2–3 Zitat-Belege aus dem Crawl (jeder unter 25 Wörter).

Wenn eine Achse mangels Material nicht bewertbar ist: `achse_wert: null`, Hinweis in `crawl_luecken`.

### Schritt 7: Hero-Test und Verständlichkeit

Lies `reference/methodik.md` Abschnitt 1 und 3 für die genauen Kriterien.

**Hero-Test:** Vier Fragen einzeln bewerten (Score 1–5, Begründung, geschätzte Sichtbarkeitszeit in Sekunden), basierend auf dem Startseite-Screenshot aus Schritt 3 und dem Markdown-Inhalt der Startseite. Vision-Modell-Aufruf empfohlen — das Modell sieht den Screenshot direkt.

- Was wird angeboten?
- Für wen?
- Was ist anders / besser?
- Wie weiter (CTA)?

`gesamt_score` als Mittelwert plus im Body **explizit benennen, welche Frage am schwächsten ist**.

**Verständlichkeit:** Eigene Bewertung 1–5, getrennt vom Hero-Test. Mit `schwachstellen`- und `staerken`-Liste (konkrete Findings mit Belegen).

### Schritt 8: Touchpoint-Inventur

Durchsuche das gecrawlte HTML (Footer, Header, Kontakt-Seiten) nach Links zu:

| Typ | Erkennungs-Patterns |
|---|---|
| LinkedIn | `linkedin.com/company/`, `linkedin.com/in/` |
| Instagram | `instagram.com/` |
| TikTok | `tiktok.com/@` |
| YouTube | `youtube.com/@`, `youtube.com/c/`, `youtube.com/channel/` |
| Facebook | `facebook.com/`, `fb.com/` |
| Pinterest | `pinterest.com/`, `pinterest.de/` |
| GMB | `g.page/`, `goo.gl/maps`, Google-Maps-Einbettungen |
| Branchenportale | Jameda, Doctolib, ProvenExpert, Trustpilot, MyHammer, etc. — je nach Branche |
| Newsletter | Anmeldeformulare (mit `mailto:`-Aktion oder Subscribe-Pattern) |
| App | App-Store-Links (apps.apple.com, play.google.com) |
| Subdomain | gleiche Domain, anderer Subdomain-Teil — nur erfassen, wenn verlinkt |

Pro Touchpoint: Typ, vollständige URL, Bezeichnung (z.B. Profil-Name), und ein einfacher Aktivitäts-Indikator: `aktiv` wenn der Link funktioniert und in Footer/Header prominent platziert, `ruhend` wenn versteckt oder offensichtlich veraltet, `unklar` wenn nicht eindeutig zu beurteilen.

### Schritt 9: `data/kunde.md` schreiben

Baue das Marken-Profil lokal im Cache zusammen (Schema in `reference/kunde-schema.md`) und lade es nach Drive in den `data/`-Sub-Folder hoch:

```bash
# kunde.md lokal aufbauen (Frontmatter + Body)
# ... Inhalt rendern ...
python3 "$DRIVE_PY" upsert-text "$DATA_ID" "kunde.md" \
  ~/.cache/reachx-mta/"$SLUG"/kunde.md "text/markdown"
```

YAML-Frontmatter mit allen strukturierten Feldern, Markdown-Body mit den acht Sektionen (Übersicht, Portfolio, USPs, Zielgruppen, Tonalität, Hero-Test, Touchpoints, Lücken).

### Schritt 10: Abweichungs-Analyse (falls Briefing vorhanden)

Wenn `BRIEFING_ID` (siehe Schritt 1) nicht leer ist: lade `data/briefing.md` aus Drive lokal nach `~/.cache/reachx-mta/<slug>/briefing.md` runter, parse das Frontmatter und vergleiche mit dem gerade erstellten `kunde.md` nach den vier Typen aus `reference/abweichungen-leitfaden.md`:

```bash
python3 "$DRIVE_PY" read "$BRIEFING_ID" > ~/.cache/reachx-mta/"$SLUG"/briefing.md
```

- Typ A — USP-Lücken
- Typ B — USP-Inkonsistenzen
- Typ C — Portfolio-Diskrepanzen
- Typ D — Zielgruppen-Mismatch

Schreibe `abweichungen.md` lokal in den Cache und lade in den `data/`-Sub-Folder auf Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$DATA_ID" "abweichungen.md" \
  ~/.cache/reachx-mta/"$SLUG"/abweichungen.md "text/markdown"
```

Wenn kein Briefing vorhanden: Abweichungs-Analyse überspringen, Hinweis im Schluss-Format.

### Schritt 11: HTML-Report erzeugen

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `reports/_shell.html` aus Drive und erzeuge daraus `02-kunde.html` mit:

- `{{TITLE}}` → `Marken-Profil · <Kunde>`
- `{{EYEBROW}}` → `MTA-Marken-Profil`
- `{{DISPLAY_NAME}}` → `Marken-Profil: <Kunde>`
- `{{META_LINE}}` → `Quelle: <Anzahl> Seiten gecrawlt · <Crawl-Datum> · Generiert: <heute>`
- `{{MAIN_CONTENT}}` → Render der Profil-Inhalte mit der bekannten CSS-Klassen-Sprache:
  - Stat-Strip oben mit Hero-Test-Gesamt-Score, Verständlichkeit, Anzahl Touchpoints, Anzahl Abweichungen
  - Sticky-TOC zu allen Sektionen
  - Tonalitäts-Sektion mit visueller Achsen-Darstellung (z. B. einfache Balken oder Text-Slider)
  - Hero-Test mit eingebettetem Screenshot
  - Touchpoints als kompakte Tabelle mit Status-Badges
  - Bei niedriger Hero-Test-Score oder hoher Abweichungs-Dichte: `.suggestion`-Block mit Strategen-Empfehlung
- `{{FOOTER_TEXT}}` → `MTA · <Kunde> · Marken-Profil aus Website-Crawl`

Den fertigen Report lokal in `~/.cache/reachx-mta/<slug>/02-kunde.html` zusammenbauen und nach Drive hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "02-kunde.html" \
  ~/.cache/reachx-mta/"$SLUG"/02-kunde.html "text/html"
```

Wenn `abweichungen.md` erstellt wurde: zusätzlich `02b-abweichungen.html` mit dem gleichen Pattern erzeugen und nach `reports/` auf Drive hochladen.

### Schritt 12: Dashboard-Update

Aktualisiere `reports/index.html` auf Drive (lesen, modifizieren, zurückschreiben — Pattern wie in `contracts.md` Abschnitt 7):

- Stat-Strip aktualisieren
- "Erledigt"-Sektion erweitern
- Reports-Liste um `02-kunde.html` (und ggf. `02b-abweichungen.html`) erweitern
- Nächste Empfehlung aktualisieren

### Schritt 13: `status.md` aktualisieren

`status.md` liegt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe per `upsert-text` zurück (`STATUS_ID` via `list-children` auf `$FOLDER_ID`):

Nach Regeln aus `contracts.md` Abschnitt 3:

- `02-01-kunden-marken-profil` in `schritte_done`
- Eigene Sektion in "✓ Erledigt"
- `naechster_empfohlen`: der First-Party-Block — `03-04-seo-first-party-gsc`, `03-18-web-analytics-ga4`, `03-17-sea-first-party-google-ads` — und **danach** `02-02-wettbewerber-identifikation` (das die First-Party-Outputs nutzt, um Seed-Keywords und Wettbewerber-Kandidaten datenbasiert statt geraten abzuleiten)
- Wenn Abweichungen mit Priorität "hoch" gefunden wurden: zusätzlicher Hinweis im Body, dass das Thema Strategie-relevant ist

### Schritt 14: Standard-Schlussformat im Chat

```
✓ 02-01-kunden-marken-profil abgeschlossen.

Outputs (auf Drive):
- data/kunde.md — strukturiertes Marken-Profil mit YAML-Frontmatter
- data/abweichungen.md — Diskrepanzen zwischen Briefing und Website (X gefunden)
- reports/02-kunde.html — visueller Report für den Strategen
- reports/02b-abweichungen.html — Abweichungs-Report
Status aktualisiert in: status.md

Hero-Test:        X,Y/5 (schwächste Dimension: <Frage>)
Verständlichkeit: X/5
Touchpoints:      <Anzahl> gefunden
Abweichungen:     <X hoch, Y mittel, Z niedrig>

[Bei hoher Abweichungs-Dichte:]
⚠ Strategie-relevante Lücken:
- <Top-2-Abweichungen>

Nächste Schritte:
1. 03-04-seo-first-party-gsc — First-Party-Block starten: echte GSC-Klick-Daten des Kunden
2. 03-18-web-analytics-ga4 — First-Party-Block: echte GA4-Nutzungs- und Referral-Daten
3. 03-17-sea-first-party-google-ads — First-Party-Block: echte Google-Ads-Daten des Kunden
4. danach 02-02-wettbewerber-identifikation — Wettbewerber-Liste finden, dann profilieren; nutzt die First-Party-Outputs (GSC-Top-Queries als Seed-Keywords, GA4-Referral-Domains als Akteurs-Kandidaten) für datenbasierte statt geratene Recherche

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/kunde-schema.md` — vollständiges Output-Schema, identisch nutzbar für `02-03-wettbewerber-marken-profil`
- `reference/methodik.md` — Hero-Test (Donald Miller), Tonalitäts-Achsen, Verständlichkeits-Bewertung
- `reference/abweichungen-leitfaden.md` — vier Abweichungs-Typen mit Priorisierungs-Regeln

## Edge Cases

- **Cookie-Walls verhindern Crawl** → Apify-Optionen nutzen (`removeCookieWarnings: true`, ggf. Custom Cookie-Acceptance). Wenn das nicht reicht: in `crawl_hinweise` notieren, Manual-Screenshot des Strategen einplanen
- **Single-Page-Apps ohne Server-Side-Rendering** → `playwright:chrome` als Crawler-Typ erzwingen, sonst sieht der Crawler leere Seiten
- **Mehrsprachige Website** → bei Erst-Crawl die Default-Sprache nehmen (oft Deutsch), bei klarem Bedarf zweiten Crawl für andere Sprachversion separat
- **Login-geschützte Bereiche** → ignorieren, in `crawl_luecken` notieren
- **Sehr kleine Website (1–3 Seiten)** → trotzdem alle Sektionen ausfüllen, aber `crawl_vollstaendig: true` mit Hinweis auf dünne Quelle
- **Website ist eine reine Landingpage / Coming Soon** → minimaler Output, klare Markierung in `crawl_luecken`, kein Hero-Test (oder Score 1 mit Erklärung)
- **Briefing-Dichte war niedrig** → Abweichungs-Analyse läuft trotzdem, aber mit Hinweis-Block über die unvollständige Vergleichsbasis (siehe `abweichungen-leitfaden.md`)
- **Apify nicht verfügbar** → klare Fehlermeldung mit Hinweis, dass MCP-Verbindung oder API-Token nötig ist; kein Fallback auf eigenes Crawling, weil das Anti-Bot- und SPA-Themen nicht zuverlässig löst

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive (über `drive.py upsert-text`); Pfad-Angaben im Frontmatter bezeichnen die Sub-Folder relativ zum MTA-Drive-Root
- Markdown + YAML-Frontmatter Hybrid-Format
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (in-place Update auf Drive)
- HTML-Reports basieren auf `reports/_shell.html` mit den verfügbaren CSS-Klassen
