---
name: 03-01-seo-sichtbarkeit-und-rankings
description: Erhebt für Kunde und alle bestätigten Wettbewerber primär via Sistrix die organische SEO-Sichtbarkeit (Sichtbarkeitsindex aktuell + 12-Monats-Verlauf), Top-Keywords mit Position und Suchvolumen, sowie die Sistrix-eigene Wettbewerbs-Liste pro Domain - und ergänzt parallel via Ahrefs Domain Rating (DR), klickbasierte Traffic-Schätzung, Intent-geflaggte Top-Keywords und eine zweite Wettbewerber-Liste. Sistrix bleibt Leit-Datenquelle für Sichtbarkeitsindex und DACH-Long-Tail; Ahrefs liefert Backlink-Stärke, Traffic-Lesart und Cross-Check-Wettbewerber. Output ist audits/seo-sichtbarkeit.md mit Vergleich plus audits/seo-keywords.csv als Sistrix-Roh-Datenbasis plus audits/seo-rankings-ahrefs.csv als Ahrefs-Parallel-Datenbasis, dazu ein HTML-Report mit zwei Stat-Strips (Sistrix-Sicht + Ahrefs-Sicht), Sichtbarkeits-Kurven, DR-Verlauf und Wettbewerbs-Schnittmenge. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext SEO-Daten, Rankings, Sichtbarkeits-Vergleiche oder Keyword-Basis aufbauen will - auch bei Phrasen wie "SEO-Sichtbarkeit", "Rankings vergleichen", "Sistrix-Daten ziehen", "Sichtbarkeitsindex für Wettbewerber", "Wo rankt der Kunde", "SEO-Status-Quo", "Keyword-Roh-Daten", "organische Sichtbarkeit", "Domain Rating prüfen", "Backlink-Stärke", "Ahrefs-Traffic-Schätzung". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist und Sistrix-Zugang verfügbar; ohne wettbewerber/liste.md kann der Skill als Kunden-only-Lauf starten; ohne Ahrefs-MCP läuft der Skill im reduzierten Modus ohne Ahrefs-Sektion.
---

# SEO-Sichtbarkeit-und-Rankings

Erster Skill in Stufe 3 (Kanal-Audits). Erhebt für **Kunde + alle bestätigten Wettbewerber** die organische SEO-Sichtbarkeit — **primär via Sistrix** (Sichtbarkeitsindex, DACH-Long-Tail-Keywords, Sistrix-Wettbewerber-Vorschläge) und **parallel via Ahrefs** (Domain Rating, klickbasierte Traffic-Schätzung, Intent-geflaggte Keywords, Ahrefs-Wettbewerber). Legt damit die **Datenbasis für alle SEO-Folge-Skills** (`03-02-seo-keyword-recherche`, `03-03-seo-keyword-kategorisierung`, später `03-15-web-content-inventur`).

**Hybrid-Prinzip**: Sistrix bleibt Leit-Datenquelle (Sichtbarkeitsindex ist Strategen- und Kunden-Sprache, DACH-Long-Tail-Tiefe besser). Ahrefs ergänzt mit Daten, die Sistrix nicht hat — DR, Traffic-Schätzung, Intent-Flags, zweite Wettbewerber-Liste. Beide Datenquellen werden im Report **nebeneinander** gezeigt, **nicht ineinander umgerechnet** (siehe Hinweis "Sistrix-Volumen vs. Ahrefs-Volumen" und "SI vs. DR" weiter unten).

Vier Output-Ebenen:

1. **Aggregat-Markdown** `audits/seo-sichtbarkeit.md` — Sistrix-Visibility-Vergleich + Ahrefs-DR/Traffic-Sektion, Top-Keywords pro Akteur, Wettbewerbs-Schnittmenge Sistrix∩Ahrefs, Auffälligkeiten
2. **Sistrix-Roh-CSV** `audits/seo-keywords.csv` — alle Sistrix-Keywords mit Domain, Position, Suchvolumen + Ahrefs-Anreicherung (`ahrefs_volume`, `ahrefs_kd`, Intent-Flags), für die Folge-Skills
3. **Ahrefs-Parallel-CSV** `audits/seo-rankings-ahrefs.csv` — Ahrefs-Top-Keywords pro Akteur (Ahrefs liefert eigene Keyword-Liste, die teilweise nicht in der Sistrix-Top-200 vorkommt)
4. **HTML-Report** `reports/06-seo-sichtbarkeit.html` — zwei Stat-Strips (Sistrix-Sicht + Ahrefs-Sicht), Sichtbarkeits-Kurven, DR-Verlauf-Sparkline, Master-Tabelle, Top-10 pro Akteur, Wettbewerbs-Schnittmenge

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wichtige Werte-Diskrepanzen — was der Skill kommuniziert

- **Sistrix-Volumen vs. Ahrefs-Volumen**: für DACH-Keywords typischerweise 1,5–3× Abweichung (Sistrix in der Regel höher). Der Skill schreibt beide Werte in die CSV und markiert in den Auffälligkeiten Keywords mit >50% Diskrepanz.
- **Sichtbarkeitsindex (SI, Sistrix) vs. Domain Rating (DR, Ahrefs)**: **NICHT vergleichbar** — andere Skalen, andere Inputs. SI misst Ranking-Footprint, DR misst Backlink-Stärke. Im Report nebeneinander, **niemals umrechnen oder zu einem "Mischwert" verdichten**.
- **Sistrix-Wettbewerber vs. Ahrefs-Wettbewerber**: können überlappen oder divergieren. Beide Listen werden erfasst, die **Schnittmenge** ist ein starkes Signal (Auffälligkeit `wettbewerber_schnittmenge_stark`).

## Wann triggern

- "SEO-Sichtbarkeit"
- "Rankings vergleichen"
- "Sistrix-Daten ziehen für [Kunde]"
- "Sichtbarkeitsindex für Wettbewerber"
- "Wo rankt der Kunde"
- "SEO-Status-Quo"
- "Keyword-Roh-Daten erfassen"
- "Organische Sichtbarkeit für die MTA"
- "Domain Rating prüfen"
- "Backlink-Stärke der Wettbewerber"
- "Ahrefs-Traffic-Schätzung"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- **Sistrix-Zugang verfügbar (Pflicht)** — über MCP, falls vorhanden, oder direkter API-Token. Wenn Sistrix komplett fehlt → Abbruch (Sistrix ist Leit-Datenquelle, der Sichtbarkeitsindex ist nicht durch Ahrefs ersetzbar).
- **Ahrefs-MCP verfügbar (optional, empfohlen)** — wenn Ahrefs-MCP-Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__site-explorer-*` erkannt werden → **Hybrid-Modus** (Sistrix + Ahrefs). Wenn Ahrefs fehlt → **Reduced-Modus** (nur Sistrix, Ahrefs-Sektion entfällt, Hinweis im Schluss-Format).
- Empfohlen: `02-02-wettbewerber-identifikation` mit `status: bestaetigt` in `wettbewerber/liste.md` → Vergleich gegen Wettbewerber möglich
- **Ohne `liste.md`**: Skill läuft trotzdem im **Kunden-only-Modus** (nur Kunden-Domain), mit Hinweis im Schluss-Format, dass der Vergleich erst nach `02-02-wettbewerber-identifikation` aussagekräftig ist

### Modi-Übersicht

| Sistrix | Ahrefs | Wettbewerber-Liste | Skill-Modus |
|---|---|---|---|
| ✓ | ✓ | bestätigt | **Voll-Hybrid** (Sistrix + Ahrefs, Kunde + WBs) |
| ✓ | ✓ | fehlt / nicht bestätigt | **Hybrid-Kunden-only** (Sistrix + Ahrefs, nur Kunde) |
| ✓ | ✗ | bestätigt | **Reduced** (nur Sistrix, Kunde + WBs) |
| ✓ | ✗ | fehlt / nicht bestätigt | **Reduced-Kunden-only** (nur Sistrix, nur Kunde) |
| ✗ | — | — | **Abbruch** |

## Ablauf

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Alle Inputs werden aus Google Drive gelesen, alle Outputs nach Drive geschrieben — siehe `contracts.md` Abschnitt 4 für das Pattern. Helper-Modul: `01-01-mta-projekt-init/scripts/drive.py`.

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

# Aktive MTA aus dem lokalen Cache holen
MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug-aus-aufruf-oder-resolve-from-context>")
if [ -z "$MTA_JSON" ] || [ "$MTA_JSON" = "null" ]; then
  echo "✗ MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

# meta.json aus Drive lesen
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

# Sub-Folder-IDs extrahieren
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lokaler Arbeits-Cache für Zwischenergebnisse (Sistrix-/Ahrefs-Roh-JSONs, CSV-Generierung, HTML-Templating): `~/.cache/reachx-mta/<slug>/`. Wird **nicht** mit Drive synchronisiert — am Ende des Laufs werden nur die finalen Outputs hochgeladen.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Wenn `meta.json` aus Schritt 0 fehlt oder nicht lesbar:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Lies `wettbewerber/liste.md` aus Drive:

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WB_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -n "$LISTE_ID" ] && [ "$LISTE_ID" != "null" ]; then
  python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/wb-liste.md
fi
```

Wenn vorhanden mit `status: bestaetigt` → Modus **Voll** (Kunde + alle WBs). Wenn vorhanden mit `status: vorgeschlagen` → Warnung:

```
⏸ wettbewerber/liste.md hat status: vorgeschlagen.
Empfehlung: erst Liste bestätigen, dann diesen Skill laufen lassen, damit der Vergleich korrekt ist.

Soll ich trotzdem im Kunden-only-Modus laufen, oder warten?
```

Wenn `liste.md` fehlt: Modus **Kunden-only**, Hinweis im Schluss-Format.

Prüfe Sistrix-Zugang (Pflicht):

- Bei MCP: prüfe verfügbare Tools (z. B. `mcp__sistrix__*`-Tools)
- Bei API-Token: prüfe `SISTRIX_API_KEY` im Environment
- Wenn beides fehlt: Abbruch mit Hinweis "Sistrix-Zugang nicht verfügbar. Bitte MCP verbinden oder SISTRIX_API_KEY setzen."

Prüfe Ahrefs-MCP-Zugang (optional):

- Prüfe, ob Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__site-explorer-*` verfügbar sind. Mindestens erwartet:
  - `site-explorer-metrics`
  - `site-explorer-metrics-history`
  - `site-explorer-domain-rating`
  - `site-explorer-domain-rating-history`
  - `site-explorer-organic-keywords`
  - `site-explorer-organic-competitors`
- Optional-Healthcheck via `subscription-info-limits-and-usage`, um Restbudget zu sehen (Skill arbeitet auf 400.000 Units/Monat). Bei Restbudget < 5.000 Units: Warnung im Schluss-Format, dass aktueller Lauf möglicherweise unvollständig bleibt.
- Wenn Ahrefs-MCP fehlt: **Reduced-Modus** — Hinweis im Chat, dass Ahrefs-Sektion entfällt, Skill läuft weiter. Im Frontmatter `quelle.ahrefs.zugang: null` setzen.
- Details zu Ahrefs-Aufrufen siehe `reference/ahrefs-api-nutzung.md`.

### Schritt 2: Domain-Liste zusammenstellen

**Domains** (jeweils mit Akteurs-Slug + Akteurs-Typ kunde/wettbewerber):

1. **Kunde** — Domain aus `meta.json.website`, normalisiert (siehe `reference/sistrix-api-nutzung.md` Abschnitt "Domain-Normalisierung")
2. **Wettbewerber** — pro Eintrag in `wettbewerber/liste.md`:
   - Aus den drei Kategorien (`kunde_genannt`, `regional`, `best_practice_ueberregional`) alle Einträge mit gültiger `website`-URL übernehmen
   - **Filter**: nicht nur `empfehlung_profilieren: ja` — auch `optional` und `nein` werden hier mit erfasst, weil SEO-Daten günstig zu erheben sind und für `04-02-kanal-chancen-analyse` später wertvoll sind
   - **Ausschluss**: Einträge mit `website: null` (kein Domain, kein Sistrix-Lookup möglich)

Notiere die Anzahl der zu prüfenden Domains. Bei mehr als 15 Domains: Hinweis im Schluss-Format, dass der Lauf länger dauern wird.

### Schritt 3: Sistrix-Domain-Overview pro Domain

Pro Domain Sistrix-Aufrufe (siehe `reference/sistrix-api-nutzung.md` für API-Details und MCP-Tool-Namen):

1. **Visibility-Index aktuell** (Sistrix-Endpoint `domain.overview` oder MCP-Equivalent):
   - Aktueller VI-Wert (Float)
   - Land/Region (Default `de`)
   - Mobile vs. Desktop (Default Desktop, optional Mobile zusätzlich)

2. **Visibility-Verlauf 12 Monate** (`domain.sichtbarkeitsindex.verlauf` oder `domain.history`):
   - Mindestens monatliche Werte, idealerweise wöchentlich
   - Speichern als Liste `[{datum: ISO-8601, wert: float}, …]`

3. **Sistrix-eigene Wettbewerber** (`domain.competitors`):
   - Top-10 Sistrix-vorgeschlagene Wettbewerber-Domains
   - Pro Wettbewerber: Domain, Visibility, Overlap-Score
   - **Wichtig**: diese Liste kann der `02-02-wettbewerber-identifikation`-Liste vom Strategen abweichen — beides erfassen, später in Auffälligkeiten ausweisen

4. **Top-Keywords der Domain** (`domain.keywords` oder `domain.urls.keywords`):
   - Default: Top 100 Keywords nach Suchvolumen × Position (gewichtet)
   - Pro Keyword: Keyword-Text, Position, Suchvolumen, URL der rankenden Seite, ggf. Wettbewerb (CPC-Bid / Konkurrenz-Score), ggf. Difficulty (falls Sistrix-Endpoint das hat — sonst aus späterem Ahrefs-Lauf)
   - Bei sehr großen Domains: Limit auf Top 200 (sonst werden CSV und Token-Budget zu groß)

**Roh-Daten zwischenspeichern** unter `~/.cache/reachx-mta/<slug>/audits/raw/sistrix-<akteurs-slug>.json` (lokaler Cache, für Reproduzierbarkeit und Folge-Skills). Am Ende des Laufs als ZIP komprimiert nach Drive in `assets/raw/` hochladen (siehe `contracts.md` Abschnitt 4 zu Apify-/API-Caches).

### Schritt 3b: Ahrefs-Domain-Overview pro Domain (nur Hybrid-Modus)

**Nur ausführen, wenn Ahrefs-MCP verfügbar.** Im Reduced-Modus überspringen.

Pro Domain Ahrefs-MCP-Aufrufe (siehe `reference/ahrefs-api-nutzung.md` für Tool-Details, Kosten und Spalten-Auswahl). **Wichtig: Domain-Mode immer `mode=subdomains`** verwenden (laut MCP-Doc-Hinweis), nicht `mode=domain` — sonst werden Subdomains nicht mitgezählt.

1. **Domain-Metrics** (`site-explorer-metrics`):
   - Liefert `org_keywords`, `org_traffic`, `paid_keywords`, `paid_traffic` als Snapshot
   - Im internen Schema: `ahrefs_org_keywords`, `ahrefs_org_traffic`, `ahrefs_paid_keywords`

2. **Domain Rating aktuell** (`site-explorer-domain-rating`):
   - Liefert `domain_rating` (0-100, Backlink-Stärke) und `ahrefs_rank` (Positionsrang)
   - DR ist **die zentrale Ahrefs-Backlink-Metrik** — geht später als eigene Spalte in die Master-Tabelle

3. **DR-Verlauf 12 Monate** (`site-explorer-domain-rating-history`):
   - Liefert Liste `[{date, domain_rating}, …]` (mind. monatlich)
   - Sistrix sieht Backlink-Trends nicht — diese Serie ist ein Ahrefs-Alleinstellungsmerkmal
   - Speichern als Liste `[{datum: ISO-8601, wert: float}, …]`

4. **Traffic-Verlauf 12 Monate** (`site-explorer-metrics-history`):
   - Select: `org_traffic, org_cost, paid_traffic, paid_cost`
   - Klickbasierte Schätzung als **zweite Lesart** neben Sistrix-Sichtbarkeitsindex (NICHT in SI umrechnen, nur nebeneinanderstellen)

5. **Ahrefs-Top-Keywords** (`site-explorer-organic-keywords`):
   - Select: `keyword, volume, keyword_difficulty, best_position, best_position_url, sum_traffic, is_branded, is_transactional, is_commercial, is_informational`
   - Default Top 100 nach `sum_traffic` (entspricht ungefähr Ahrefs-eigener Wichtigkeits-Sortierung)
   - **Wichtig**: Ahrefs liefert hier **eigene Keywords**, die teilweise in der Sistrix-Top-200 nicht vorkommen — diese gehen in die parallele CSV `audits/seo-rankings-ahrefs.csv`, nicht in `audits/seo-keywords.csv`
   - Intent-Flags (`is_branded`, `is_transactional`, `is_commercial`, `is_informational`) sind boolesch — der nachgelagerte `03-03-seo-keyword-kategorisierung`-Skill nutzt sie als Hypothese für seinen Intent-Cluster-Vorschlag

6. **Ahrefs-Organic-Competitors** (`site-explorer-organic-competitors`):
   - Select: `competitor_domain, keywords_common, keywords_competitor, domain_rating, traffic`
   - Liefert Ahrefs-eigene Wettbewerber-Vorschläge (basierend auf gemeinsamen Keywords)
   - Wird in Schritt 6 mit der Sistrix-Wettbewerber-Liste pro Akteur abgeglichen — Schnittmenge ist **starkes Signal**, Differenzen sind **Strategen-Review-Hinweise**

7. **Optional: Ahrefs-Top-Pages** (`site-explorer-top-pages`):
   - Nur wenn Budget reicht und Folge-Skills es brauchen (`03-15-web-content-inventur`).
   - In `raw/`-Cache ablegen, in dieser MTA-Stufe **nicht zwingend** auswerten.

**Cross-Domain-Anreicherung der Sistrix-CSV**: Für jedes Sistrix-Keyword in `audits/seo-keywords.csv` versucht der Skill ein Match in der Ahrefs-Organic-Keywords-Liste **derselben Domain** (per `keyword`-String, lowercase, Whitespace-getrimmt). Wenn Match gefunden → Ahrefs-Volumen, KD und Intent-Flags ergänzen. Wenn nicht → Spalten leer lassen.

**Roh-Daten zwischenspeichern** unter `~/.cache/reachx-mta/<slug>/audits/raw/ahrefs-<endpoint>-<akteurs-slug>.json` (lokaler Cache, ein File pro Endpoint pro Akteur). Am Ende komprimiert nach Drive `assets/raw/`. Struktur und TTL siehe `reference/ahrefs-api-nutzung.md`.

### Schritt 4: Domain nicht in Sistrix indexiert

Wenn eine Domain in Sistrix nicht vorkommt (oft bei sehr kleinen oder sehr neuen Websites, oder bei internationalen Domains außerhalb DACH):

- Visibility-Index auf `null` setzen
- Keyword-Liste leer
- Im Output deutlich markieren: `sistrix_indexiert: false`
- Im Schluss-Format als Hinweis ausweisen

Bei mehreren nicht-indexierten Domains: möglicher Hinweis, dass die Branche oder Geografie nicht Sistrix-stark ist (z. B. internationale B2B-SaaS — wenn Ahrefs im Hybrid-Modus läuft, kann der Ahrefs-Traffic-Wert hier eine zweite Lesart liefern, wenn Sistrix die Domain nicht kennt).

**Wichtig**: Wenn eine Domain bei Sistrix nicht indexiert ist, aber Ahrefs-Daten hat → trotzdem in beide CSVs (sofern Hybrid-Modus). Die Sistrix-CSV-Zeile bleibt leer (keine Keywords), die Ahrefs-CSV trägt die Top-Keywords. Im Frontmatter `sistrix_indexiert: false`, aber `ahrefs_indexiert: true` setzen. Auffälligkeit `nur_ahrefs_indexiert` vergeben.

### Schritt 5: CSV-Output `audits/seo-keywords.csv` (Sistrix-primär, Ahrefs-angereichert)

Schreibe alle Sistrix-erfassten Keywords aller Akteure in eine flache CSV. Sistrix bleibt **die Leit-Datenquelle** — die Datei heißt weiterhin `seo-keywords.csv` und ist Pflicht-Input für die Folge-Skills. Die Ahrefs-Spalten werden per Keyword-Match angereichert (Schritt 3b), sind aber **optional pro Zeile** — wenn kein Match → leer.

Spalten (siehe `reference/ausgabe-schema.md` Abschnitt "CSV-Schema"):

```
akteurs_slug, akteurs_typ, akteurs_name, domain, keyword, position, suchvolumen, ranking_url, sistrix_competition, kwid, datenstand_iso, ahrefs_volume, ahrefs_kd, ahrefs_sum_traffic, intent_branded, intent_transactional, intent_commercial, intent_informational
```

Die Spalten 1–11 sind unverändert zu Schema-Version 1.0 (Sistrix-Daten). Die Spalten 12–18 sind neu (Ahrefs-Anreicherung):

- `ahrefs_volume` — Ahrefs-Suchvolumen für dasselbe Keyword (typischerweise 1,5–3× niedriger als Sistrix bei DACH)
- `ahrefs_kd` — Keyword Difficulty (0-100, Ahrefs-eigene Skala)
- `ahrefs_sum_traffic` — Ahrefs-Traffic-Beitrag dieses Keywords für die Domain
- `intent_branded`, `intent_transactional`, `intent_commercial`, `intent_informational` — boolesche Flags (0/1) von Ahrefs

Eine Zeile pro (Akteur, Keyword)-Kombination. Bei 10 Akteuren × 100 Keywords ergibt das 1000 Zeilen — handhabbar in Excel und für die Folge-Skills.

CSV ist **die Roh-Datenbasis** — die Folge-Skills (`03-02-seo-keyword-recherche`, `03-03-seo-keyword-kategorisierung`) lesen primär aus dieser Datei, nicht aus dem Aggregat-Markdown.

### Schritt 5b: CSV-Output `audits/seo-rankings-ahrefs.csv` (nur Hybrid-Modus)

**Nur ausführen, wenn Ahrefs-MCP verfügbar.** Im Reduced-Modus überspringen.

Parallel-CSV mit Ahrefs-eigenen Top-Keywords pro Akteur. Begründung für separate Datei: Ahrefs liefert eigene Keyword-Liste mit eigener Sortierung — viele Keywords erscheinen, die in der Sistrix-Top-200 nicht vorkommen. Würde man sie in `seo-keywords.csv` mischen, wäre die Sortierung und die "Anzahl pro Akteur"-Logik kaputt.

Spalten (siehe `reference/ausgabe-schema.md` Abschnitt "Ahrefs-CSV-Schema"):

```
akteurs_slug, akteurs_typ, akteurs_name, domain, keyword, ahrefs_volume, ahrefs_kd, best_position, best_position_url, ahrefs_sum_traffic, intent_branded, intent_transactional, intent_commercial, intent_informational, datenstand_iso
```

Eine Zeile pro (Akteur, Ahrefs-Keyword)-Kombination. Default Top 100 pro Akteur. Die Folge-Skills nutzen diese Datei **ergänzend** zu `seo-keywords.csv`, primär für Intent-Cluster-Hypothesen und für Keywords, die Sistrix nicht sieht.

### Schritt 6: Aggregat-Markdown `audits/seo-sichtbarkeit.md`

Format nach `reference/ausgabe-schema.md` Abschnitt "Markdown-Schema". YAML-Frontmatter mit:

- Skill-Metadaten, Recherche-Provenienz (welche Sistrix-Endpoints, welche Ahrefs-Tools, wann gelaufen, Datenstand) — `quelle.sistrix` und `quelle.ahrefs` als getrennte Blöcke
- Akteurs-Liste mit Sistrix-Feldern (`visibility_aktuell`, `visibility_12m_min`, …) und parallel Ahrefs-Feldern (`ahrefs_dr_aktuell`, `ahrefs_dr_vor_12m`, `ahrefs_org_traffic`, `ahrefs_org_keywords`) — Ahrefs-Felder sind `null`, wenn Reduced-Modus oder Domain nicht in Ahrefs
- Vergleich (Kunden-Position im Ranking nach SI, Lücke zu Spitzenreiter, Lücke zum Median) — **bleibt Sistrix-primär**
- Sistrix-eigene Wettbewerber-Vorschläge (pro Akteur die Top-5)
- **Neu**: Ahrefs-eigene Wettbewerber-Vorschläge (pro Akteur die Top-5)
- **Neu**: Wettbewerber-Schnittmenge Sistrix∩Ahrefs (Domains, die in **beiden** Tools als WB auftauchen → starkes Signal)
- Auffälligkeiten (siehe Schritt 7, erweitert)

Body strukturiert nach:

- Übersicht (Kunde-SI, Top-SI im Vergleich, Anzahl indizierter Akteure in Sistrix bzw. Ahrefs)
- **Sistrix-Sicht** (Leit-Datenquelle):
  - Ranking-Tabelle nach SI sortiert mit Trend-Pfeil und Top-3-Keywords
  - Pro Akteur Mini-Sektion mit SI-Verlauf-Beschreibung, Top-10 Sistrix-Keywords
  - Sistrix-eigene Wettbewerbs-Cluster
- **Ahrefs-Sicht** (parallel, nur Hybrid-Modus):
  - DR-Tabelle pro Akteur (DR aktuell, DR vor 12M, DR-Trend)
  - Traffic-Schätzung pro Akteur (klickbasiert) als zweite Lesart neben SI
  - Pro Akteur die Top-10 Ahrefs-Keywords mit Intent-Flags
  - Ahrefs-eigene Wettbewerbs-Cluster
- **Wettbewerber-Schnittmenge Sistrix∩Ahrefs**: Tabelle mit allen Domains, die in beiden Tools als WB-Vorschlag auftauchen, getrennt von der Strategen-`liste.md` → starkes Signal für "übersehene relevante WBs"
- **Wichtige Werte-Diskrepanzen**: Tabelle mit Sistrix- vs. Ahrefs-Volumen für die Top-Keywords des Kunden (zur Kalibrierung für den Strategen — er soll wissen, dass die Zahlen pro Tool unterschiedlich sind)
- Auffälligkeiten als eigene Sektion

### Schritt 7: Auffälligkeiten

Aus den erhobenen Daten die strategisch relevanten Beobachtungen extrahieren:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_unter_median` | Kunden-SI unter Median der WB-Gruppe | "Kunde liegt mit SI 0.08 unter dem WB-Median von 0.21" |
| `kunde_top` | Kunden-SI in den Top 3 der erhobenen Akteure | "Kunde rankt im SI auf Platz 2 von 9" |
| `wettbewerber_dominant` | Ein WB hat SI mehr als 3× über dem Median | "Wettbewerber X dominiert die organische Sichtbarkeit (SI 0.84, nächstbester 0.21)" |
| `trend_kunde_negativ` | Kunden-SI in 12 Monaten um >25% gefallen | "Kunden-SI ist in 12 Monaten von 0.18 auf 0.08 gefallen — möglicher Penalty oder Tech-Issue" |
| `trend_kunde_positiv` | Kunden-SI in 12 Monaten um >50% gestiegen | "Kunden-SI hat sich verdoppelt — laufende SEO-Aktivität sichtbar" |
| `sistrix_wb_nicht_in_liste` | Mindestens 2 Sistrix-vorgeschlagene WBs sind nicht in `liste.md` | "Sistrix schlägt X und Y als Wettbewerber vor, beide nicht in liste.md — Strategen-Review empfohlen" |
| `keyword_cluster_dominant` | Top-3-Keywords der WBs sind häufig gleich oder ähnlich | "Wettbewerb konzentriert sich auf 'Hauptkeyword X' — Differenzierungs-Chance über Long-Tail" |
| `nicht_indiziert_haeufig` | Mehr als 30% der Akteure sind nicht in Sistrix | "Branche nicht stark in Sistrix-Index — Ahrefs-Sicht als Cross-Check nutzen" |
| **`volumen_diskrepanz_sistrix_ahrefs`** | Sistrix-Volumen und Ahrefs-Volumen weichen für ein Keyword um >50% ab | "'aufmaß werkzeug' — Sistrix 720 vs. Ahrefs 290 — bei Volumen-Argumentation in der MTA-Slide auf Quellen-Mix hinweisen" |
| **`wettbewerber_schnittmenge_stark`** | Ein WB taucht in BEIDEN Tool-Listen (Sistrix-WBs UND Ahrefs-WBs) für mindestens einen Akteur auf | "Domain Z erscheint sowohl bei Sistrix als auch bei Ahrefs als Wettbewerber — belastbares Signal, prüfen ob in liste.md" |
| **`wettbewerber_nur_ahrefs`** | Domain ist Ahrefs-WB, aber nicht in Sistrix-WBs und nicht in `liste.md` | "Ahrefs schlägt Domain X als WB vor, Sistrix nicht — meist Backlink-Profil-WB, der inhaltlich weniger relevant ist; Strategen-Review" |
| **`wettbewerber_nur_sistrix`** | Domain ist Sistrix-WB, aber nicht in Ahrefs-WBs und nicht in `liste.md` | "Sistrix schlägt Domain Y als WB vor, Ahrefs nicht — Ranking-Overlap ohne Backlink-Overlap, oft DACH-Long-Tail-spezifisch; Strategen-Review" |
| **`traffic_dr_diskrepanz`** | DR hoch (>50) aber Ahrefs-Traffic niedrig (im untersten Quartil) — oder umgekehrt | "Akteur hat DR 62 (starkes Backlink-Profil), aber nur 1.200 org. Klicks/Monat — ungenutzte Autorität, möglicherweise Content-Lücke" |
| **`nur_ahrefs_indexiert`** | Domain ist in Ahrefs, aber nicht in Sistrix | "Akteur X ist in Sistrix nicht indexiert, in Ahrefs aber mit DR 38 und 3.400 Klicks — internationaler Footprint dominiert" |

Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung.

**Reduced-Modus**: Die fünf Ahrefs-abhängigen Typen (`volumen_diskrepanz_sistrix_ahrefs`, `wettbewerber_schnittmenge_stark`, `wettbewerber_nur_ahrefs`, `wettbewerber_nur_sistrix`, `traffic_dr_diskrepanz`, `nur_ahrefs_indexiert`) werden im Reduced-Modus nicht generiert.

### Schritt 8: HTML-Report `reports/06-seo-sichtbarkeit.html`

Aus `reports/_shell.html` einen Audit-Report bauen:

- `{{TITLE}}` → `SEO-Sichtbarkeit · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · SEO`
- `{{DISPLAY_NAME}}` → `SEO-Sichtbarkeit und Rankings: KUNDE`
- `{{META_LINE}}` → `Sistrix + Ahrefs · Datenstand DATUM · N Akteure · Generiert: heute` (im Reduced-Modus nur `Sistrix · …`)
- `{{MAIN_CONTENT}}` →
  - **Zwei Stat-Strips oben** (im Hybrid-Modus, sonst nur Strip 1):
    - **Strip 1 — Sistrix-Sicht**: Kunden-SI, Rang im SI-Vergleich (z. B. "Platz 3 von 9"), Trend SI 12 Monate (Pfeil + Prozent), Anzahl Auffälligkeiten, Anzahl nicht-Sistrix-indizierter Akteure
    - **Strip 2 — Ahrefs-Sicht**: Kunden-DR, Ahrefs-Traffic-Schätzung (Klicks/Monat), DR-Trend 12 Monate, Anzahl Ahrefs-Keywords der Kunden-Domain. **Hinweis-Text unter dem Strip**: "DR und SI sind nicht direkt vergleichbar — DR misst Backlink-Stärke, SI misst Ranking-Footprint."
  - **Sticky-TOC**: Sistrix-Sicht (Master, Verlauf, pro Akteur), Ahrefs-Sicht (DR/Traffic, pro Akteur), Wettbewerber-Schnittmenge, Volumen-Diskrepanzen, Auffälligkeiten
  - **Sistrix-Master-Tabelle**: alle Akteure nach SI sortiert; Spalten: Akteur, Typ (Kunde / WB-Kategorie), SI aktuell, SI vor 12M, Trend-Badge, Top-3-Keywords (komma-separiert)
  - **SI-Verlauf-Visualisierung**: einfache SVG-Sparklines pro Akteur (12-Monats-Verlauf, gleicher Y-Achsen-Maßstab über alle Akteure)
  - **Ahrefs-Master-Tabelle** (nur Hybrid): Akteur, DR aktuell, DR vor 12M, DR-Trend-Badge, org_traffic, org_keywords. **Eigene Tabelle**, nicht mit der Sistrix-Tabelle vermischt — damit beide Skalen nebeneinander lesbar bleiben.
  - **DR-Verlauf-Sparkline**: pro Akteur, parallel zur SI-Sparkline (klar als "Ahrefs DR-Verlauf" labeln)
  - **Pro Akteur ein `details class="skill"`-Block** (default zugeklappt außer Kunde + Top-2-WBs nach SI):
    - SI-Verlauf
    - Top-10 Sistrix-Keywords als Tabelle (Keyword, Position, Suchvolumen, ranking-URL)
    - Sistrix-vorgeschlagene WBs als kleine Liste
    - **Im Hybrid-Modus zusätzlich**: DR-Wert + DR-Verlauf, Ahrefs-Traffic, Top-10 Ahrefs-Keywords mit Intent-Badges (`B` = branded, `T` = transactional, `C` = commercial, `I` = informational), Ahrefs-WBs als kleine Liste
  - **Ahrefs-Wettbewerber-Liste-Block** (eigener Block, nur Hybrid): Top-Ahrefs-WBs aggregiert über alle Akteure, mit `bereits_in_liste`-Flag und `auch_sistrix_wb`-Flag (Schnittmenge-Marker)
  - **Wettbewerber-Schnittmenge-Block** (nur Hybrid): Domains, die in beiden Tools als WB-Vorschlag auftauchen → starkes Signal, `.suggestion`-Stil
  - **Volumen-Diskrepanz-Tabelle** (nur Hybrid): Top-Keywords des Kunden mit Sistrix-Volumen, Ahrefs-Volumen, Abweichung in %
  - **Sistrix-Wettbewerbs-Cluster**: Hinweis-Block wie bisher
  - **Auffälligkeiten-Block** als `.suggestion`-Block: Top 3-5 strategische Beobachtungen, sortiert nach Relevanz
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · SEO-Sichtbarkeit-Audit`

### Schritt 8b: Outputs nach Drive hochladen

Alle finalen Outputs werden via `drive.py upsert-text` nach Drive geschrieben (idempotent — überschreibt bestehende Datei sauber):

```bash
# Markdown-Aggregat
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-sichtbarkeit.md" \
  ~/.cache/reachx-mta/<slug>/seo-sichtbarkeit.md "text/markdown"

# Sistrix-Keywords CSV
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-keywords.csv" \
  ~/.cache/reachx-mta/<slug>/seo-keywords.csv "text/csv"

# Ahrefs-Parallel-CSV (nur Hybrid-Modus)
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-rankings-ahrefs.csv" \
  ~/.cache/reachx-mta/<slug>/seo-rankings-ahrefs.csv "text/csv"

# HTML-Report
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "06-seo-sichtbarkeit.html" \
  ~/.cache/reachx-mta/<slug>/06-seo-sichtbarkeit.html "text/html"
```

Hinweis CSV: `drive.py upsert-text` setzt für CSV-Files `disableConversionToGoogleType: true` — die CSV bleibt also CSV und wird nicht automatisch in ein Google Sheet umgewandelt.

### Schritt 9: Dashboard-Update

Lies aktuelles `reports/index.html` aus Drive, aktualisiere, schreibe zurück:

```bash
INDEX_ID=$(python3 "$DRIVE_PY" list-children "$REPORTS_ID" | jq -r '.[] | select(.name == "index.html") | .id')
python3 "$DRIVE_PY" read "$INDEX_ID" > /tmp/index.html
# … HTML modifizieren (siehe contracts.md Abschnitt 7) …
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "index.html" /tmp/index.html "text/html"
```

Aktualisiere `reports/index.html`:

- Stat-Strip um Kunden-SI ergänzen; im Hybrid-Modus zusätzlich Kunden-DR
- "Erledigt"-Sektion erweitern um `03-01-seo-sichtbarkeit-und-rankings`
- Reports-Liste um `06-seo-sichtbarkeit.html` erweitern
- Stufe 3 als "in Arbeit" markieren (erster Audit-Skill durch)
- "Nächster empfohlener Schritt": `03-02-seo-keyword-recherche` (baut auf der CSV-Roh-Datenbasis auf)

### Schritt 10: `status.md` aktualisieren

Standard-Pattern (aus Drive lesen, anpassen, zurückschreiben):

```bash
STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > /tmp/status.md
# … Frontmatter parsen, eigenen Skill in schritte_done, aus schritte_offen, naechster_empfohlen setzen …
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"
```

Nach Regeln aus `contracts.md` Abschnitt 3:

- `03-01-seo-sichtbarkeit-und-rankings` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z. B. "3 von 9 Akteuren nicht in Sistrix indexiert")
- `naechster_empfohlen`: `03-02-seo-keyword-recherche`
- Wenn Auffälligkeit `trend_kunde_negativ`: Hinweis im Body, dass das Strategie-relevant ist und in MTA-Story einfließen sollte

### Schritt 11: Standard-Schlussformat im Chat

```
✓ 03-01-seo-sichtbarkeit-und-rankings abgeschlossen.
Modus: <Voll-Hybrid | Hybrid-Kunden-only | Reduced | Reduced-Kunden-only>

Outputs:
- audits/seo-sichtbarkeit.md — Aggregat mit Sistrix-Sicht + Ahrefs-Sicht, Trends, Auffälligkeiten
- audits/seo-keywords.csv — Sistrix-Keywords (N Zeilen) + Ahrefs-Anreicherung für die SEO-Folge-Skills
[Hybrid-Modus zusätzlich:]
- audits/seo-rankings-ahrefs.csv — Ahrefs-Top-Keywords (N Zeilen) mit Intent-Flags
- reports/06-seo-sichtbarkeit.html — visueller Audit-Report (zwei Stat-Strips: Sistrix + Ahrefs)
Status aktualisiert in: status.md

Sistrix-Sicht:
- Akteure erfasst:           N (Kunde + (N-1) Wettbewerber)
- In Sistrix indexiert:      M
- Nicht in Sistrix indexiert: NI
- Kunden-SI aktuell:         X,XX (Rang Y von M)
- Kunden-SI-Trend 12M:       +/- Z%
- Top-SI im Vergleich:       Wettbewerber A mit X,XX

[Im Hybrid-Modus:]
Ahrefs-Sicht (parallele Lesart, nicht in SI umrechnen):
- In Ahrefs indexiert:       MA
- Kunden-DR aktuell:         XX (Trend 12M +/- Z%)
- Kunden-Traffic (Ahrefs):   ca. NNN Klicks/Monat
- Top-DR im Vergleich:       Wettbewerber B mit XX
- Wettbewerber-Schnittmenge: K Domains in BEIDEN Tool-Listen (= belastbare WB-Signale)

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- (1-3 Punkte aus der Auffälligkeiten-Liste, sortiert nach Relevanz)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md fehlt oder nicht bestätigt — Vergleich nur gegen Tool-vorgeschlagene WBs.

[Wenn nicht-Sistrix-indizierte Akteure:]
ℹ Sistrix-Lücken:
- N Akteure nicht in Sistrix indexiert. [Wenn Hybrid: K davon in Ahrefs sichtbar — Ahrefs-Sicht im Report prüfen.]

[Wenn Reduced-Modus:]
ℹ Reduced-Modus
- Ahrefs-MCP nicht verfügbar — der Lauf basiert nur auf Sistrix. Für Backlink-Trend, Traffic-Schätzung und Intent-Flags den Skill nach Ahrefs-MCP-Verbindung erneut laufen lassen.

[Wenn Ahrefs-Budget knapp:]
ℹ Ahrefs-Budget niedrig
- Subscription zeigt Restbudget X.XXX Units — nächster Lauf in dieser MTA-Größe nicht garantiert. Re-Runs nutzen 14-Tage-Cache.

Nächste Schritte:
1. 03-02-seo-keyword-recherche — erweitert die Keyword-Basis mit Long-Tail, Wettbewerbs-Keywords (Sistrix + Ahrefs)
2. (parallel möglich) 03-05-sea-google-ads-check — Paid-Search-Aktivität in derselben Branche
3. (parallel möglich) 03-14-web-tech-und-tracking — Tech-Stack und Performance

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/sistrix-api-nutzung.md` — Sistrix-API/MCP-Nutzung, Endpoints, Domain-Normalisierung, Rate-Limits, Fehler-Recovery (unverändert)
- `reference/ahrefs-api-nutzung.md` — Ahrefs-MCP-Nutzung, Tool-Mapping, Spalten-Auswahl, Unit-Kosten, Caching-Strategie, Reduced-Modus
- `reference/ausgabe-schema.md` — Output-Schemas für `audits/seo-sichtbarkeit.md` (Markdown + Frontmatter), `audits/seo-keywords.csv` (Sistrix-primär + Ahrefs-angereichert) und `audits/seo-rankings-ahrefs.csv` (neue Ahrefs-Parallel-CSV)

## Edge Cases

- **Sistrix-Zugang fehlt komplett** → Skill-Abbruch mit klarem Hinweis. Kein Fallback auf alternative Tools (verfälscht die Datenbasis, weil der Sichtbarkeitsindex eine Sistrix-spezifische Metrik ist).

- **Ahrefs-MCP fehlt** → Reduced-Modus, kein Abbruch. Skill läuft nur mit Sistrix, lässt Ahrefs-Sektion im Markdown/HTML weg, Hinweis im Schluss-Format.

- **Sistrix-API-Rate-Limit erreicht** → 60 Sekunden warten, einmal retry. Bei weiterem 429: Skill schreibt bisher erhobene Daten in CSV und Markdown, markiert nicht-fertige Akteure im Body, setzt sich beim nächsten Aufruf an der unfertigen Position fort.

- **Ahrefs-Budget aufgebraucht (429 oder Subscription-Limit erreicht)** → Skill schreibt bisher erhobene Ahrefs-Daten in Cache und CSV, markiert nicht-fertige Akteure als `ahrefs_indexiert: unbekannt`, Skill bricht den Ahrefs-Teil ab und läuft mit Sistrix-only-Sektion weiter. Hinweis im Schluss-Format. Re-Run nach Budget-Reset nutzt 14-Tage-Cache aus `audits/raw/ahrefs-*.json` für die bereits abgefragten Akteure.

- **Sehr große Domain (10k+ Keywords)** → Hard-Cap bei Top 200 Keywords (Sistrix) und Top 100 Keywords (Ahrefs) pro Akteur. Im Body Hinweis "Domain hat sehr großen Keyword-Footprint, Auswahl begrenzt."

- **Internationale Domains** (`region: international` aus `identifikation-schema.md`) → Sistrix-Datenbank-Region auf `at`, `ch`, `us`, `uk`, `fr`, etc. je nach Bedarf einstellen. Ahrefs-Tools nehmen `country`-Parameter analog. Wenn ein Tool die Region nicht gut abdeckt: Hinweis und ggf. Skip-für-diese-Quelle.

- **Domain hat sich umgezogen / Redirect-Chain** → Sistrix erkennt das in der Regel automatisch. Bei Ahrefs in `mode=subdomains` wird die Redirect-Ziel-Domain abgefragt. In den `raw/*.json` beide Domains dokumentieren.

- **Kunde hat mehrere Domains** (Hauptmarke + Sub-Brands) → Skill prüft `meta.json.website` als Primär, kann via Stratege-Override zusätzlich Sub-Domains erfassen. Default: nur Primär.

- **`liste.md` enthält Domain, die identisch zur Kunden-Domain ist** → Dedup, Hinweis im Schluss-Format.

- **Sehr kleine SI-Werte (unter 0.01)** → werden trotzdem dargestellt, Sparkline mit Log-Skala oder gekennzeichnetem "kleinen-Werte-Bereich". Keine Filterung.

- **Ahrefs liefert für Kunden-Domain keine Treffer** (`org_keywords: 0`) → Im Frontmatter `ahrefs_indexiert: false`. Auffälligkeit nur, wenn das überraschend ist (Sistrix zeigt rankende Keywords, Ahrefs nicht — meist Ahrefs-Crawl-Lücke). Kein Abbruch.

- **Keyword-Match Sistrix↔Ahrefs scheitert wegen Schreibvarianten** (Bindestrich, Umlaute, Leerzeichen) → Match-Strategie: lowercase + Whitespace-Normalisierung + Bindestrich/Leerzeichen-Toleranz. Bei verbleibendem Mismatch: kein Match, Ahrefs-Spalten leer. Im Markdown-Body Hinweis-Statistik "X% der Sistrix-Keywords mit Ahrefs-Match".

- **DR-Verlauf hat Lücken** (Ahrefs liefert nicht jede Woche/Monat einen Wert) → Lücken im JSON als `null` ablegen, Sparkline interpoliert visuell nicht, sondern unterbricht die Linie.

- **`audits/seo-keywords.csv` oder `audits/seo-rankings-ahrefs.csv` existiert bereits** (Re-Run) → frage:
  - **(a) überschreiben** — neue Daten ersetzen alte
  - **(b) Backup-und-neu** — alte Version nach `audits/_backup/seo-keywords-<ISO>.csv` bzw. `audits/_backup/seo-rankings-ahrefs-<ISO>.csv`
  - **(c) abbrechen**

- **Sistrix-Volumen und Ahrefs-Volumen weichen für ein Keyword extrem ab** (>50%) → in CSV beide Werte stehen lassen, Auffälligkeit `volumen_diskrepanz_sistrix_ahrefs` generieren. Keine Quelle als "richtig" markieren — Stratege entscheidet.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder, Pfade in der Doku sind relativ zum Drive-MTA-Root (z. B. `audits/seo-sichtbarkeit.md`)
- Markdown + YAML-Frontmatter für `seo-sichtbarkeit.md`, CSV für `seo-keywords.csv` und `seo-rankings-ahrefs.csv`
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (via `drive.py upsert-text`)
- HTML-Report basiert auf `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **Sistrix-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/sistrix-<slug>.json`, am Ende komprimiert nach Drive `assets/raw/`
- **Ahrefs-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/ahrefs-<endpoint>-<slug>.json` mit 14-Tage-TTL, am Ende komprimiert nach Drive `assets/raw/`
- **Sichtbarkeitsindex-Werte unverändert lassen** — Sistrix-Skala bleibt erhalten, Normalisierung ist Aufgabe der Synthese-Skills
- **DR-Werte unverändert lassen** — Ahrefs-Skala (0-100) bleibt erhalten
- **SI und DR nicht mischen, nicht umrechnen, nicht zu einem gemeinsamen Score verdichten** — verschiedene Inputs, verschiedene Aussagen
- **Sistrix bleibt Leit-Datenquelle in der Strategen- und Kunden-Kommunikation** — Ahrefs ist Ergänzung, nicht Ersatz
