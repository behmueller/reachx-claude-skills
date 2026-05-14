---
name: 03-15-web-content-inventur
description: Gestufte Content-Inventur pro Akteur (Kunde + bestätigte Wettbewerber). Drei Stufen pro Akteur - sitemap_only (Sitemap zählen, Pattern-Cluster), light (Top-30-Crawl mit Title/Meta/Headings) oder full (Vollcrawl mit Word-Count und Themen-Heuristik). Schema-vor-Lauf-Pattern - Phase A schlägt Stufe pro Akteur plus Filter-Patterns vor, Stratege bestätigt, Phase B schreibt audits/content-inventur.md plus CSV. Nutze diesen Skill IMMER im MTA-Kontext, wenn der Nutzer Content auditieren, Sitemaps prüfen, Seitenstrukturen vergleichen oder Content-Lücken finden will - auch bei Phrasen wie "Content-Inventur", "Sitemap auswerten", "Content-Audit Kunde vs Wettbewerber", "Themen-Verteilung der Website", "Page-Typ-Verteilung", "Content-Lücken finden", "Blog-Inventur", "Wie viele Seiten hat die Seite". Setzt 01-01-mta-projekt-init voraus, idealerweise 02-02-wettbewerber-identifikation - bricht sonst mit Hinweis ab.
---

# Content-Inventur

Fünfter Audit-Skill in Stufe 3 (Audits, Website-Familie). **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8) mit **gestuftem Tiefenmodell**: pro Akteur entscheidet der Stratege im Schema, wie tief die Content-Inventur greift.

Drei Stufen, von günstig zu teuer:

1. **`sitemap_only`** — nur `sitemap.xml` (inklusive `sitemap_index.xml`-Auflösung) laden, URLs zählen, nach URL-Pfad-Heuristik clustern. Keine Page-Crawls. Günstig, schnell, Page-Typ-Verteilung als Endergebnis.
2. **`light`** — Sitemap plus Crawl der Top-30 Seiten pro Cluster: Title, Meta-Description, H1/H2-Struktur. Mittlere Tiefe, gut für 80% der Wettbewerber.
3. **`full`** — wie `light` plus Vollcrawl des definierten Content-Bereichs (z. B. `/blog/`, `/ratgeber/`) mit Word-Count und Themen-Heuristik per Token-Frequenz. Teuer, sinnvoll für Best-Practice-Vorbilder und den Kunden.

Output ist die Brücke vom Roh-Sitemap-Bestand zum Strategie-Output:

- `audits/content-inventur.md` — Aggregat mit Page-Typ-Verteilung pro Akteur, Top-Themen, Content-Lücken Kunde vs. Wettbewerb, Auffälligkeiten
- `audits/content-inventur.csv` — Page-Liste pro Akteur (URL, Page-Typ, Title, Word-Count falls `light`/`full`)
- `audits/raw/sitemap-SLUG.xml` und `audits/raw/content-crawl-SLUG.json` pro Akteur
- `reports/13-03-15-web-content-inventur.html` — Visueller Vergleichs-Report

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "Content-Inventur"
- "Sitemap auswerten"
- "Content-Audit Kunde vs Wettbewerber"
- "Themen-Verteilung der Website"
- "Welche Seiten hat Wettbewerber X"
- "Page-Typ-Verteilung"
- "Content-Lücken finden"
- "Blog-Inventur"
- "Wie viele Seiten hat die Seite"
- "Website-Content prüfen"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- **Stark empfohlen:** `02-02-wettbewerber-identifikation` mit `wettbewerber/liste.md` (`status: bestaetigt`) — sonst läuft der Skill im Kunden-only-Modus mit Hinweis
- Apify-Zugang verfügbar (für `apify/website-content-crawler`)
- Optional: `FIRECRAWL_API_KEY` als Alternative für strukturierte Page-Daten
- Empfohlen: `data/kunde.md` (für Portfolio-Kategorien als Cluster-Inspiration)

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `audits/content-inventur-schema.md` existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B läuft.

### Phase-Entscheidungs-Logik (Schritt 1 bei jedem Aufruf)

Zuerst die Drive-Bootstrap (siehe `contracts.md` Abschnitt 1):

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
```

Phasen-Logik (Schema und Output liegen auf Drive im `audits/`-Sub-Folder):

```
1. Existiert audits/content-inventur-schema.md auf Drive? (drive.py find_by_name "$AUDITS_ID" "content-inventur-schema.md")
   - Nein → Phase A (Schema generieren)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt → Phase B (eigentliche Inventur)
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert audits/content-inventur.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen: überschreiben / Backup-und-neu / abbrechen
```

---

## Phase A — Inventur-Schema generieren

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Lies `wettbewerber/liste.md` aus Drive (`find_by_name(WB_ID, "liste.md")` → `read_text`):

- Wenn vorhanden und `status: bestaetigt` → alle Akteure (Kunde + alle Wettbewerber mit `empfehlung_profilieren` in {ja, optional}) aufnehmen
- Wenn vorhanden, aber `status: vorgeschlagen` → freundlicher Abbruch mit Hinweis "wettbewerber/liste.md bestätigen oder Kunden-only-Modus explizit anfordern"
- Wenn nicht vorhanden → Kunden-only-Modus mit Hinweis im Body

Lies optionale Inputs aus Drive:

- `data/kunde.md` via `find_by_name(DATA_ID, "kunde.md")` (für `portfolio_wie_kommuniziert[].kategorie` — die Produkt-Kategorien sind häufig gute Cluster-Anker und beeinflussen die Stufen-Empfehlung)
- `wettbewerber/identifikation-schema.md` via `find_by_name(WB_ID, "identifikation-schema.md")` (für Branchen-Typ und Region — bei lokalen B2C-Branchen ist `sitemap_only` meist ausreichend, bei B2B-SaaS lohnt sich `light`)
- `data/briefing.md` via `find_by_name(DATA_ID, "briefing.md")` (für vom Strategen genannte Themen-Schwerpunkte)

### Schritt A.2: Akteurs-Liste mit Default-Stufen aufbauen

Pro Akteur eine Stufen-Empfehlung nach folgender Logik:

| Akteurs-Kategorie | Default-Stufe | Begründung |
|---|---|---|
| Kunde | `light` | Wir wollen genug Tiefe für Cluster-Erkennung und Themen-Lücken, aber nicht jede einzelne Seite |
| Wettbewerber `bedrohungsgrad: direkt` (Top-3 nach Strategen-Markierung) | `light` | Vergleichbar mit dem Kunden auf gleicher Tiefe |
| Restliche regional/direkt-WB | `sitemap_only` | Reine Bestands-Vergleichsbasis reicht |
| Wettbewerber `best_practice_ueberregional` | `full` | Diese sind die lernfähigste Quelle - Themen-Tiefe und Schreibstil sind wertvolle Inspiration |

Override-Möglichkeit: Stratege kann pro Akteur die Stufe im Schema anpassen.

### Schritt A.3: Filter-Patterns pro Akteur ableiten

Pro Akteur eine Liste von **Exclude-Patterns** (URL-Pfade, die aus der Inventur ausgeschlossen werden) und **Include-Patterns** (optional — wenn nur ein Sub-Bereich relevant ist).

**Standard-Excludes** für alle Akteure (Defaults):

- `/wp-admin/`, `/wp-content/uploads/`, `/wp-json/` (Wordpress-Backend)
- `/cart/`, `/checkout/`, `/warenkorb/`, `/kasse/` (Shop-Transaktional)
- `/tag/`, `/category/`, `/page/[0-9]+/`, `/archive/` (Pagination und Tag-Archive — Duplicate Content)
- `/feed/`, `/?p=`, `/?s=` (RSS und Query-Parameter)
- `/login/`, `/register/`, `/mein-konto/`, `/my-account/` (User-Bereiche)
- `/datei/`, `*.pdf`, `*.jpg`, `*.png`, `*.xml` (Asset-Files, außer es ist explizit Content)

**Branchen-spezifische Excludes** (Standard-Vorschläge je Branche, vom Strategen kuratierbar) — siehe `reference/stufen-methodik.md`.

**Include-Patterns** für `full`-Stufe: pro Akteur den Content-Bereich definieren, der vollständig gecrawlt wird (z. B. `include: ["/blog/", "/ratgeber/", "/magazin/"]`). Wenn leer: ganzer Bereich nach Exclude-Filter.

### Schritt A.4: Page-Typ-Heuristik definieren

Standard-Heuristik (Default-Vorschlag, vom Strategen erweiterbar) — siehe `reference/stufen-methodik.md` für die volle Mapping-Tabelle. Sechs Page-Typen:

- `produkt_seite` — `/produkte/`, `/shop/`, `/products/`
- `blog_oder_ratgeber` — `/blog/`, `/ratgeber/`, `/magazin/`, `/news/`, `/journal/`
- `lp_oder_kampagne` — URL ohne erkennbares Sub-Verzeichnis aber mit utm-Hinweisen oder `/lp/`, `/landingpage/`
- `service_oder_branche` — `/leistungen/`, `/branchen/`, `/services/`, `/loesungen/`
- `unternehmens_seite` — `/unternehmen/`, `/ueber-uns/`, `/karriere/`, `/kontakt/`, `/impressum/`
- `sonstige` — alles, was nicht matched

Im Schema kann der Stratege das Mapping pro Akteur überschreiben (manche Domains haben eigene Pfad-Konventionen wie `/wissen/` statt `/blog/`).

### Schritt A.5: Tool-Auswahl

Default-Tool-Reihenfolge pro Stufe:

| Stufe | Sitemap-Loader | Page-Crawler |
|---|---|---|
| `sitemap_only` | HTTP-GET `/sitemap.xml` plus `/sitemap_index.xml`-Discovery | nicht nötig |
| `light` | wie oben | `apify/website-content-crawler` mit `maxCrawlPages` pro Cluster |
| `full` | wie oben | `apify/website-content-crawler` mit erweitertem Limit auf Include-Pattern, optional Firecrawl-Alternative |

Wenn `FIRECRAWL_API_KEY` gesetzt: Firecrawl als Alternative für die `light`/`full`-Stufen anbieten (saubere Markdown-Outputs, weniger Konfigurations-Aufwand).

### Schritt A.6: Budget-Schätzung

Aus den vorgeschlagenen Stufen ein grobes Crawl-Budget ableiten (für den Strategen-Review):

- `sitemap_only`: 0 Crawl-Credits (nur HTTP-GETs)
- `light`: ca. 30 Crawl-Credits pro Cluster, ca. 5-8 Cluster pro Akteur → ca. 150-240 Crawl-Credits pro Akteur
- `full`: ca. 200-1000 Crawl-Credits pro Akteur (je nach Größe des Content-Bereichs)

Summe pro Akteur und Gesamt im Schema-Body ausweisen.

### Schritt A.7: `audits/content-inventur-schema.md` nach Drive schreiben

Erzeuge das vollständige Schema lokal in `~/.cache/reachx-mta/<slug>/content-inventur-schema.md` nach `reference/inventur-schema-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "content-inventur-schema.md" \
  ~/.cache/reachx-mta/<slug>/content-inventur-schema.md "text/markdown"
```

Der Stratege kann das Schema direkt in der Drive-Web-UI editieren (Markdown ist editierbar) und `status: bestaetigt` setzen.

Sektionen:

- **Frontmatter**: Skill-Metadaten, Akteurs-Liste mit Default-Stufen, Crawl-Budget gesamt
- **Body**:
  - Übersicht der Akteurs-Liste mit empfohlener Stufe und Begründung pro Akteur
  - Filter-Patterns (globale Defaults plus akteurs-spezifische Anpassungen)
  - Page-Typ-Heuristik (Standard-Mapping plus Override-Hinweise)
  - Tool-Auswahl pro Stufe
  - Budget-Übersicht
  - Pflicht-Review-Sektion für den Strategen mit konkreten Eingriffspunkten (Stufen anpassen, Include/Exclude-Patterns ergänzen, Page-Typ-Mapping erweitern)

### Schritt A.8: Schluss-Format Phase A

```
✓ 03-15-web-content-inventur Phase A abgeschlossen.

Outputs (auf Drive):
- audits/content-inventur-schema.md — Inventur-Schema (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Akteure gesamt:         N (Kunde + M Wettbewerber)
- Stufe sitemap_only:     X Akteure
- Stufe light:            Y Akteure
- Stufe full:             Z Akteure
- Crawl-Budget gesamt:    ca. B Credits

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Stufe pro Akteur (besonders die best_practice-Wettbewerber, die per Default auf full gehen), Filter-Patterns (Exclude-Liste), Page-Typ-Mapping.
Nach Review (direkt in Drive editierbar): status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, via `drive.py upsert-text "$FOLDER_ID" "status.md" ...` zurückschreiben):

```yaml
blockiert:
  - skill: 03-15-web-content-inventur (Phase B)
    wartet_auf: "Strategen-Review von audits/content-inventur-schema.md (auf Drive)"
```

Eigenen Skill noch NICHT in `schritte_done` — erst nach Phase B.

---

## Phase B — Eigentliche Inventur

### Schritt B.1: Schema-Validierung

Lies `audits/content-inventur-schema.md` aus Drive (`find_by_name(AUDITS_ID, "content-inventur-schema.md")` → `read_text`). Prüfe:

1. `status: bestaetigt`? Sonst Abbruch
2. Mindestens 1 Akteur definiert?
3. Jeder Akteur hat: `name`, `domain`, `stufe` in {sitemap_only, light, full}, `include_patterns` (Liste, kann leer sein), `exclude_patterns` (Liste, kann leer sein)?
4. Page-Typ-Heuristik-Tabelle vorhanden?

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Existenz-Check Output

Wenn `audits/content-inventur.md` oder `audits/content-inventur.csv` auf Drive bereits existieren (`drive.py find_by_name`): fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Pro Akteur die Sitemap laden

Sequenziell pro Akteur (Apify-Rate-Limits beachten):

1. HTTP-GET `https://DOMAIN/sitemap.xml`
2. Wenn 404 oder leer → Discovery: `https://DOMAIN/sitemap_index.xml`, `/robots.txt` (auf `Sitemap:`-Zeilen parsen), `/sitemap-1.xml`, `/wp-sitemap.xml`
3. Wenn es ein Sitemap-Index ist (`<sitemapindex>`): rekursiv alle referenzierten Sitemaps laden
4. Alle URLs sammeln, Roh-Sitemap lokal cachen und am Ende des Laufs nach Drive `assets/raw/sitemap-SLUG.xml` hochladen
5. Wenn keine Sitemap findbar → Akteur als `sitemap_fehlt` markieren, Inventur für diesen Akteur degradiert auf "Domain-Größe unbekannt", Hinweis im Output

### Schritt B.4: Sitemap-Filterung und Page-Typ-Klassifikation

Pro URL:

1. **Exclude-Filter** anwenden (globale plus akteurs-spezifische Patterns)
2. **Include-Filter** anwenden (wenn vorhanden, sonst alles durchlassen)
3. **Page-Typ-Klassifikation** nach Heuristik aus dem Schema
4. **Cluster-Zuordnung**: Page-Typ ist gleichzeitig der Cluster

Output dieser Stufe: Liste aller URLs pro Akteur mit `url`, `page_typ`. Bei Stufe `sitemap_only` ist das das Endergebnis pro Akteur.

### Schritt B.5: Light-Crawl (nur für Akteure mit Stufe `light` oder `full`)

Pro Cluster die Top-30 Seiten crawlen (Auswahl: erste 30 in Sitemap-Reihenfolge — Sitemaps sind meist sinnvoll sortiert; bei großen Sites Stratege im Schema priorisieren lassen).

Crawl via Apify `apify/website-content-crawler`:

- `startUrls`: die ausgewählten URLs (max 30 pro Cluster)
- `maxCrawlPages`: identisch zur URL-Anzahl
- `crawlerType`: `cheerio` (schnell für statisches HTML) oder `playwright` (fallback für JS-Sites)
- Output-Felder: `title`, `metaDescription`, `h1`, `h2[]`, `wordCount` (falls verfügbar)

Alternative bei `FIRECRAWL_API_KEY`: Firecrawl `/scrape` mit `extract` für strukturierte Page-Daten.

Roh-Output pro Akteur lokal in `~/.cache/reachx-mta/<slug>/`, am Ende des Laufs nach Drive `assets/raw/content-crawl-SLUG.json`.

### Schritt B.6: Full-Crawl (nur für Akteure mit Stufe `full`)

Wie Light-Crawl, aber:

- `startUrls`: nur die `include_patterns`-Bereiche aus dem Schema
- `maxCrawlPages`: hoch genug für den Bereich (Default 500, im Schema überschreibbar)
- `maxCrawlDepth`: 3 (folgt internen Links innerhalb der Include-Patterns)
- Word-Count immer extrahieren
- Themen-Heuristik per Token-Frequenz: pro Akteur die Top-30 inhaltlichen Tokens (Stopwords ausgeschlossen) sammeln, als `top_themen` in den Output

### Schritt B.7: Cross-Akteur-Analyse — Content-Lücken

Wenn mindestens Kunde plus 1 Wettbewerber auf Stufe `light` oder höher ist:

1. **Page-Typ-Verteilungs-Vergleich**: pro Page-Typ den Akteur mit dem niedrigsten Anteil identifizieren — wenn Kunde dort ist und Differenz zum Durchschnitt >50%, ist das ein Lücken-Hinweis
2. **Themen-Lücken** (nur wenn ≥1 Akteur auf Stufe `full`): Top-Themen-Tokens beim Best-Practice-WB, die beim Kunden komplett fehlen, werden als `themen_luecke_kunde` markiert
3. **Cluster-Größen-Auffälligkeiten**: Cluster, in denen der Kunde 0 Pages hat, mindestens 1 WB aber >10, werden als `kunde_cluster_luecke` markiert

### Schritt B.8: Auffälligkeiten extrahieren

Acht Auffälligkeiten-Typen:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_cluster_luecke` | Kunde 0 Pages in einem Cluster, ≥1 WB hat >10 | "Cluster blog_oder_ratgeber: Kunde 0 Seiten, alpha-tech 84 Seiten — klarer Content-Hub-Vorsprung des WB" |
| `themen_luecke_kunde` | Best-Practice-WB hat Top-Thema, Kunde hat es nicht im Content | "Thema 'Smart-Home-Integration' bei beta-solutions stark präsent, beim Kunden nicht erkennbar" |
| `kunde_content_dominant` | Kunde hat in einem Cluster >50% Anteil über alle Akteure | "Kunde dominiert im Cluster produkt_seite — gutes Bestands-Asset" |
| `wb_dünn_aber_intensiv` | WB hat wenige Pages, aber hohe Themen-Tiefe (nur bei `full`) | "alpha-tech hat nur 28 Blog-Posts, aber durchschnittlich 1.800 Wörter pro Post — hohe Tiefe statt Breite" |
| `sitemap_fehlt` | Akteur hat keine erreichbare Sitemap | "casafan: keine Sitemap findbar — Crawl-Strategie unklar, ggf. manueller Check" |
| `pagination_dominanz` | Akteur hat >40% Pagination-URLs vor Filterung | "delta-shop hat 2.300 von 5.000 URLs als /page/N/ — Pagination dominiert, Content-Volumen wahrscheinlich kleiner als rohe Sitemap suggeriert" |
| `cluster_zu_breit` | Cluster `sonstige` hat >30% des Page-Bestands eines Akteurs | "epsilon-services: 38% der Seiten in 'sonstige' — Page-Typ-Heuristik passt nicht zur Site-Struktur, Mapping erweitern" |
| `lp_oder_kampagne_signal` | Mehrere Pages mit utm-Parametern oder /lp/-Pfaden | "zeta-saas: 14 Landing-Pages identifiziert — Hinweis auf aktive Paid-Aktivitäten" |

### Schritt B.9: CSV-Output `audits/content-inventur.csv`

CSV lokal erzeugen, dann `drive.py upsert-text "$AUDITS_ID" "content-inventur.csv" /tmp/content-inventur.csv "text/csv"`. Vollständiges Schema in `reference/inventur-output-schema.md`. Spalten:

```
akteur_slug, akteur_name, url, page_typ, cluster, title, meta_description, h1, word_count, crawl_stufe, datenstand_iso
```

Pro Akteur eine Sektion (alle Pages des Akteurs zusammen, sortiert nach Page-Typ und URL). Felder `title`, `meta_description`, `h1`, `word_count` sind bei Stufe `sitemap_only` leer.

### Schritt B.10: Aggregat-Markdown `audits/content-inventur.md`

Lokal generieren, dann `drive.py upsert-text "$AUDITS_ID" "content-inventur.md" /tmp/content-inventur.md "text/markdown"`. Body strukturiert nach:

- **Übersicht**: Akteure gesamt, Pages gesamt, Stufen-Verteilung
- **Page-Typ-Verteilung**: Tabelle Akteur × Page-Typ mit Page-Counts und %-Anteilen
- **Pro Akteur ein Sub-Block** (max 8-10 Akteure):
  - Stufe der Inventur
  - Page-Count gesamt
  - Page-Typ-Verteilung
  - Top-5 Cluster nach Page-Count
  - Top-Themen (nur bei Stufe `full`)
  - Auffälligkeiten für diesen Akteur
- **Content-Lücken Kunde vs. Wettbewerb** (eigene Sektion, prominent)
- **Auffälligkeiten** pool-weit, sortiert nach Relevanz
- **Vorbereitung für Folge-Skills**: Hinweise welche Cluster und Lücken für `04-02-kanal-chancen-analyse` und `04-05-90-tage-plan` taugen

### Schritt B.11: HTML-Report `reports/13-content-inventur.html`

`_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`) als Basis nehmen, Platzhalter füllen, dann via `drive.py upsert-text "$REPORTS_ID" "13-content-inventur.html" /tmp/report.html "text/html"` hochladen. Aus `reports/_shell.html`:

- Stat-Strip oben: Akteure-Anzahl, Pages gesamt, größter Cluster, Anzahl Content-Lücken
- Sticky-TOC zu allen Akteurs-Sektionen plus Lücken-Sektion plus Auffälligkeiten
- **Page-Typ-Heatmap**: Akteur × Page-Typ als Tabelle mit Farb-Intensität nach %-Anteil
- **Pro Akteur** ein `<details class="skill">`-Block mit Page-Count, Cluster-Tabelle, Top-Themen (falls full)
- **Content-Lücken-Block** prominent als `.suggestion` — die strategisch wichtigsten Beobachtungen
- **Auffälligkeiten-Block** mit Handlungs-Empfehlungen
- Footer

### Schritt B.12: Dashboard-Update und status.md

Beide Dateien (`reports/index.html` und `status.md`) aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben.

- `03-15-web-content-inventur` in `schritte_done`
- Aus `blockiert` entfernen
- Reports-Liste um `13-content-inventur.html`
- Stat-Strip aktualisieren (Anzahl Akteure inventarisiert, größter Cluster, Anzahl Lücken)
- `naechster_empfohlen`:
  - Wenn Stufe 3 noch nicht voll: nächster Audit-Skill (üblicherweise `03-16-local-gmb-und-seo` oder ein Social-Audit, parallel möglich)
  - Wenn Stufe 3 weitgehend durch: `04-02-kanal-chancen-analyse` (Synthese-Stufe)

### Schritt B.13: Standard-Schlussformat im Chat

```
✓ 03-15-web-content-inventur Phase B abgeschlossen.

Outputs (auf Drive):
- audits/content-inventur.md — Aggregat mit Page-Typ-Verteilung und Lücken
- audits/content-inventur.csv — N Pages über M Akteure
- reports/13-content-inventur.html — Vergleichs-Report mit Heatmap
Status aktualisiert in: status.md

Inventur-Statistik:
- Akteure inventarisiert:    M
- Pages gesamt:              N
- Stufen-Verteilung:         sitemap_only=X, light=Y, full=Z
- Größter Cluster:           NAME (P Pages)
- Content-Lücken Kunde:      L identifiziert

[Top 3 strategische Beobachtungen:]
⚠ Content-Insights:
1. AUFFAELLIGKEIT_1
2. AUFFAELLIGKEIT_2
3. AUFFAELLIGKEIT_3

[Wenn sitemap_fehlt bei einem Akteur:]
ℹ Hinweis
- AKTEUR_NAME hatte keine erreichbare Sitemap — Inventur für diesen Akteur degradiert. Ggf. manueller Stichproben-Check.

Nächste Schritte:
1. 04-02-kanal-chancen-analyse — synthetisiert Content mit den anderen Audits (sobald genug Audits da sind)
2. (parallel möglich) 03-16-local-gmb-und-seo / Social-Audits

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/inventur-schema-template.md` — Phase-A-Output-Format mit Default-Stufen pro Akteurs-Kategorie und Default-Filter-Patterns
- `reference/stufen-methodik.md` — Fachliche Grundlage zu sitemap_only / light / full, Page-Typ-Heuristik mit Mapping-Tabelle, Tool-Auswahl
- `reference/inventur-output-schema.md` — Phase-B-CSV-Schema, Markdown-Aggregat-Struktur, Auffälligkeiten-Definitionen

## Edge Cases

- **Akteur hat keine erreichbare Sitemap** → Skill versucht Discovery (`sitemap_index.xml`, `/robots.txt`, `/wp-sitemap.xml`). Wenn auch das fehlschlägt: Akteur als `sitemap_fehlt` markieren, Crawl optional via Apify mit Start-URL-Liste manuell ergänzbar (Stratege liefert URLs nach).

- **Sitemap-Index referenziert mehr als 50 Sub-Sitemaps** → großer Shop oder Publisher. Skill warnt vor dem Lauf, lädt aber alle (rekursiv) — bei `sitemap_only` ist das günstig. Bei `light`/`full` Hinweis im Schema-Body, dass Stratege ggf. die Stufe auf `sitemap_only` zurückstufen sollte.

- **Sehr große Sitemap (>10.000 URLs)** bei Stufe `light` → Top-30 pro Cluster ist die Default-Begrenzung. Stratege kann im Schema `light_top_n_pro_cluster` überschreiben.

- **Branchen-spezifische URL-Konventionen** (z. B. eine Healthcare-Site hat `/wissen/` statt `/blog/`) → Stratege passt im Schema die Page-Typ-Heuristik pro Akteur an.

- **Apify-Crawler scheitert auf JS-Heavy-Site** → Skill versucht `playwright`-Variante als Fallback. Wenn auch das fehlschlägt: Akteur als `crawl_fehlgeschlagen` markieren, Sitemap-only-Ergebnisse trotzdem ins Aggregat aufnehmen.

- **Stratege wünscht Re-Run mit verändertem Schema** → Override-Argument "Schema überarbeiten" → Skill löscht (mit Backup) den existierenden Phase-B-Output, lässt das Schema auf `status: vorgeschlagen` zurückfallen und bricht ab.

- **Re-Run mit identischem Schema** (z. B. Monate später für Trendvergleich) → Skill fragt: "Pages vorhanden, neu inventarisieren?" → bei Bestätigung neuer Lauf mit aktuellem Datenstand. Alter Output wird mit Datums-Suffix nach `assets/_backup/content-inventur-YYYYMMDD.md` auf Drive verschoben.

- **Cluster `sonstige` ist zu groß (>30%)** → Auffälligkeit `cluster_zu_breit` mit Empfehlung, das Page-Typ-Mapping für diesen Akteur zu erweitern.

- **Kein FIRECRAWL_API_KEY und Apify-Credits knapp** → Skill warnt vor dem Lauf, schlägt vor, alle Akteure auf `sitemap_only` zurückzustufen — Stratege entscheidet.

- **Internationaler Akteur mit hreflang-Sitemaps** → Skill bevorzugt die Sitemap der vom Schema definierten Region (Default: Region aus `meta.json`). Andere Sprachen werden im Body als "nicht inventarisiert" vermerkt.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B läuft niemals ohne `status: bestaetigt` in Phase-A-Output
- Outputs leben auf Google Drive in `audits/`, `reports/` und `assets/raw/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Daten
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert
- HTML-Report aus `reports/_shell.html` (aus Drive geladen)
- **CSV ist Single-Source-of-Truth** für die Folge-Skills (Synthese-Stufe)
- **Stufen-Entscheidung ist kuratiert** — der Stratege gestaltet im Schema-Review, der Skill schlägt nur Defaults vor
