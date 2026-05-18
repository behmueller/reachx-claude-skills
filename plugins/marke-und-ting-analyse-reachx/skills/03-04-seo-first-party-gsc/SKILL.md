---
name: 03-04-seo-first-party-gsc
description: Erhebt für den Kunden den first-party-SEO-Status-Quo direkt aus der Google Search Console über den dedizierten search-console-MCP (saurabhsharma2u/search-console-mcp, OAuth gegen einen zentralen Agentur-Account) - 16-Monats-Performance-Verlauf, Top-Queries mit Klicks/Impressionen/CTR/Position, Top-Pages, Device- und Country-Splits, CTR-by-Position-Benchmark. Liefert die echten Klick-Daten des Kunden VOR allen third-party-Sichtbarkeits-Tools (Sistrix/Ahrefs-Index) und detektiert Gewinner/Verlierer, Cannibalization, Hidden-Content, CTR-Gaps und Position-zu-Klick-Quick-Wins - viele davon über eingebaute SEO-Analyse-Tools des MCP (`seo_quick_wins`, `seo_cannibalization`, `seo_low_ctr_opportunities`, `seo_lost_queries`, `seo_brand_vs_nonbrand`). Fällt auf den Ahrefs-MCP-GSC-Pfad zurück, wenn der dedizierte MCP nicht installiert ist (Reduced-Modus mit Hinweis). Output ist audits/gsc-first-party.md mit Aggregat, audits/gsc-performance.csv und audits/gsc-pages.csv als Roh-Basis, plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext GSC-Daten, Search-Console-Performance, first-party-SEO-Daten oder echte Klick-Daten des Kunden ziehen will - auch bei Phrasen wie "GSC-Daten", "Search Console auswerten", "echte SEO-Klicks", "first-party-SEO", "Gewinner Verlierer SEO", "CTR-Gap", "Cannibalization-Check", "GSC-Quick-Wins", "Position 4-10 Hebel", "Search Console Performance". Setzt 01-01-mta-projekt-init voraus; bei nicht verbundenem MCP und nicht verbundener GSC-Property freundlicher Skip mit Anleitung, KEIN Abbruch des MTA-Workflows.
---

# SEO-First-Party-GSC

**Erster SEO-Skill in Stufe 3** (Kanal-Audits), läuft VOR `03-01-seo-sichtbarkeit-und-rankings`. Erhebt aus der **echten Google-Search-Console-Property des Kunden** über den dedizierten **search-console-MCP** (saurabhsharma2u/search-console-mcp, OAuth gegen einen zentralen Agentur-Account, kostenlos, keine Ahrefs-Units) den first-party-SEO-Status-Quo: Klicks, Impressionen, CTR, Position — die einzigen echten Performance-Daten, die der Kunde tatsächlich aus Google bekommt.

Dieser Skill ist Teil des **First-Party-Blocks** der MTA (GSC + GA4 + Google Ads — `03-04`, `03-18`, `03-17`), der gemeinsam die Realitäts-Basis legt, **bevor** Third-Party-Tools (Sistrix/Ahrefs-Index) und die Wettbewerbs-Audits laufen. Keine harte Abhängigkeit zu den beiden anderen First-Party-Skills — der Block wird aber bewusst zusammen und früh abgearbeitet.

Warum first-party VOR third-party-Tools (Sistrix, Ahrefs-Index)?

- **Sistrix/Ahrefs-Index** = modellierte Sichtbarkeit, basierend auf gecrawlten Top-N-Keywords. Gut für Wettbewerbs-Vergleich, aber filtert Long-Tail und Brand-Traffic.
- **GSC** = echte Google-Realität für den Kunden. Zeigt was tatsächlich rankt, wer wirklich klickt, wo CTR-Hebel liegen. Long-Tail- und Brand-Queries, die in Sistrix/Ahrefs fehlen, sind hier vollständig sichtbar (im Avadent-Live-Test: GSC zeigte ~10× mehr Keywords als der Ahrefs-Index, plus personenbezogene Suchen wie "Dr. Hanke Bad Homburg", die kein Index-Crawler kennt).

Die GSC-Daten verankern alle SEO-Folge-Skills:
- `03-01-seo-sichtbarkeit-und-rankings` bekommt Realitäts-Korrektur (Kunde rankt laut Sistrix auf Position 4, aber GSC zeigt: bringt 0 Klicks — Hebel woanders)
- `03-02-seo-keyword-recherche` startet vom echten Klick-Pool, nicht vom modellierten
- `03-15-web-content-inventur` weiß, welche Pages echten Traffic ziehen vs. Karteileichen

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/gsc-first-party.md` — Performance-Übersicht, Gewinner/Verlierer, Cannibalization, Hidden-Content, CTR-Gaps, Quick-Win-Pool, Auffälligkeiten
2. **Roh-CSVs** `audits/gsc-performance.csv` (Query-Ebene) + `audits/gsc-pages.csv` (Page-Ebene) — Datenbasis für die SEO-Folge-Skills
3. **HTML-Report** `reports/05a-gsc-first-party.html` — Performance-Stat-Strip, 16M-Verlauf, Gewinner/Verlierer-Tabellen, Quick-Win-Liste

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

- "GSC-Daten ziehen"
- "Search Console auswerten"
- "Echte SEO-Klicks des Kunden"
- "First-party-SEO-Status-Quo"
- "Gewinner/Verlierer im SEO"
- "CTR-Gap finden"
- "Cannibalization-Check"
- "Anonymous Queries auswerten"
- "GSC-Quick-Wins finden"
- "Position 4-10 Hebel"
- "Search Console Performance des Kunden"
- "Hidden-Content-Discovery"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` mit `website` und `kunden_slug` vorhanden
- **Primärer Pfad: search-console-MCP** verbunden — Tools mit Prefix `mcp__search-console__*` verfügbar. Installation einmalig: `npx -y search-console-mcp@1.13.5 setup` (OAuth-Browser-Login, Token in macOS Keychain), dann `claude mcp add search-console --scope user -- npx -y search-console-mcp@1.13.5`.
- **Fallback: Ahrefs-MCP** mit GSC-Anbindung — Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__gsc-*`. Nur genutzt wenn der dedizierte MCP nicht installiert ist.
- **GSC-Property des Kunden ist dem OAuth-Account zugänglich** (entweder direkt freigegeben, oder der zentrale Agentur-Account hat als `siteFullUser`/`siteRestrictedUser`/`siteOwner` Zugriff). Skill prüft das automatisch über `sites_list`.

**Wichtig:** Wenn weder MCP noch GSC-Zugang da ist → **freundlicher Skip mit Anleitung, KEIN Abbruch.** Der MTA-Workflow läuft mit `03-01-seo-sichtbarkeit-und-rankings` (Sistrix-basiert) und weiteren SEO-Skills nahtlos weiter. GSC ist ein **Bonus**, kein Blocker.

**Reihenfolge:** Dieser Skill läuft bewusst **früh** — nach den Setup-Skills (`01-01`, `01-02`, `02-01`) und idealerweise **vor `02-02-wettbewerber-identifikation`**. Grund: Die First-Party-Outputs sind der Realitäts-Anker — die Top-Queries aus `gsc-performance.csv` schärfen die Wettbewerber-Identifikation mit echten Seed-Keywords statt mit geratenen Branchen-Begriffen. Harte Voraussetzung bleibt allein `01-01-mta-projekt-init`; alles andere ist Empfehlung, kein Blocker.

## Ablauf

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Inputs aus Drive, Outputs nach Drive — siehe `contracts.md` Abschnitt 4. Helper: `01-01-mta-projekt-init/scripts/drive.py`.

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug-aus-aufruf>")
[ -z "$MTA_JSON" ] || [ "$MTA_JSON" = "null" ] && { echo "✗ MTA nicht im Cache. Bitte 01-01-mta-projekt-init aufrufen."; exit 1; }
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lokaler Arbeits-Cache für GSC-Roh-JSONs und CSV-Generierung: `~/.cache/reachx-mta/<slug>/`.

**Wichtig:** Der GSC-MCP-Zugang ist **unabhängig von Drive/gws** — der search-console-MCP nutzt einen eigenen OAuth-Token (macOS Keychain), und der Status-Quo-Text zu MCP-Installation und Property-Auflösung bleibt unverändert. Die Drive-Anpassung betrifft nur die Speicher-Stellen der Outputs.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Wenn `meta.json` aus Schritt 0 fehlt oder nicht lesbar:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Prüfe in dieser Reihenfolge, welcher MCP-Pfad verfügbar ist:

1. **Primärpfad — dedizierter search-console-MCP:** Sind Tools mit Prefix `mcp__search-console__*` verfügbar (insbesondere `sites_list`, `analytics_top_queries`, `analytics_top_pages`, `analytics_time_series`, `analytics_compare_periods`, `seo_quick_wins`, `seo_cannibalization`, `seo_low_ctr_opportunities`)? Wenn ja → Modus **direkt**.

2. **Fallback-Pfad — Ahrefs-MCP-GSC-Tools:** Sind Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__gsc-*` und `...__management-projects` verfügbar? Wenn ja → Modus **fallback** mit Hinweis im Schluss-Format "Reduced-Modus über Ahrefs-MCP — empfehle Installation des dedizierten search-console-MCP für tiefere Daten und kostenlose API-Calls".

3. **Keiner verfügbar:** freundlicher Skip, kein Abbruch:

```
ℹ 03-04-seo-first-party-gsc geskippt — Kein GSC-MCP installiert.

So beheben (einmalig, ~3 Minuten):
1. `npx -y search-console-mcp@1.13.5 setup` im Terminal — startet OAuth-Browser-Login mit dem zentralen Agentur-Account (Token landet in macOS Keychain, hardware-gebunden)
2. `claude mcp add search-console --scope user -- npx -y search-console-mcp@1.13.5` — registriert den MCP user-weit
3. Claude Code neu starten
4. Diesen Skill erneut aufrufen

Bis dahin läuft der MTA-Workflow mit Sistrix-basierter Third-Party-Sicht weiter — kein Blocker.

Nächste Schritte:
1. 03-01-seo-sichtbarkeit-und-rankings — Sistrix-basierte Sichtbarkeit als Hauptdatenquelle

Sag mir, welcher als nächster.
```

### Schritt 2: GSC-Property-Auffindung

**Im Modus direkt** — Rufe `mcp__search-console__sites_list({engine: "google"})` auf. Das Ergebnis ist eine Liste aller GSC-Properties, auf die der OAuth-Account Zugriff hat (pro Property: `siteUrl`, `permissionLevel`).

**Domain-Matching** gegen die Kunden-Domain aus `meta.json.website`. Beide GSC-Property-Typen behandeln (Details in `reference/gsc-api-nutzung.md` Abschnitt "Domain-Matching"):

- **URL-Property**: `siteUrl` ist eine vollständige URL wie `https://avadent.de/`. Match wenn Host-Teil mit Kunden-Domain übereinstimmt.
- **Domain-Property**: `siteUrl` hat das Präfix `sc-domain:`, z. B. `sc-domain:avadent.de`. Match wenn das Suffix mit der Kunden-Domain übereinstimmt.

Wenn mehrere Properties passen (z. B. `https://www.avadent.de/` UND `sc-domain:avadent.de`): bevorzuge die Domain-Property (umfasst alle Subdomains und Protokolle), Fallback URL-Property. Stratege-Override über Argument `property=<siteUrl>` möglich.

**Permission-Level beachten:**
- `siteOwner`, `siteFullUser`, `siteRestrictedUser` → ausreichend für read-only Pulls, weiter mit Schritt 3
- `siteUnverifiedUser` → Property ist im Account gelistet, aber Verifikation steht aus. Kein Daten-Zugriff möglich → Skip wie unten.

**Im Modus fallback** — Rufe `mcp__1d9710a6-f270-4555-88f8-e4367948d936__management-projects` auf. Suche das Ahrefs-Projekt, dessen URL/Domain zur Kunden-Domain passt. Bei Treffer mit GSC-Anbindung weiter, sonst Skip wie unten.

**Drei Möglichkeiten:**

1. **Property gefunden mit Lese-Zugriff** → siteUrl notieren, weiter mit Schritt 3.

2. **Keine passende Property im Account** → **freundlicher Skip:**

```
ℹ 03-04-seo-first-party-gsc geskippt — GSC-Property nicht zugänglich.

Für die Kunden-Domain <domain> ist keine GSC-Property im verbundenen OAuth-Account verfügbar. Der search-console-MCP sieht aktuell N andere Properties, aber nicht diese.

So beheben:
1. Kunde bittet, den zentralen Agentur-Account (<account-email aus accounts_list>) als "Eingeschränkter Nutzer" oder höher in seiner GSC-Property hinzuzufügen
   ODER
2. Stratege erhält direkten Zugang zu einer anderen GSC-Property des Kunden und fügt sie dem zentralen Account hinzu

Nach Freigabe diesen Skill erneut aufrufen.

Bis dahin läuft der MTA-Workflow mit Sistrix-basierter Third-Party-Sicht weiter — kein Blocker.

Nächste Schritte:
1. 03-01-seo-sichtbarkeit-und-rankings — Sistrix-basierte Sichtbarkeit als Hauptdatenquelle

Sag mir, welcher als nächster.
```

Schreibe `status.md` mit Vermerk `geskippt — gsc_property_nicht_zugaenglich` und führe einen Mini-Eintrag im "✓ Erledigt"-Block (mit Status "geskippt").

3. **Property gefunden, aber `siteUnverifiedUser`** → analoger Skip, Vermerk `geskippt — property_unverified`.

**Override:** Wenn Stratege mit Argument `force` oder `trotzdem versuchen` erneut aufruft, versucht der Skill, die Tools direkt mit der gewünschten siteUrl aufzurufen. Wenn der erste API-Call mit Permission-Error fehlschlägt, sauber abbrechen wie oben.

### Schritt 3: Zeitraum festlegen

Default: **16 Monate** rückwärts ab heute (GSC-Max-Zeitraum). Bei jüngeren Properties (Anbindung jünger als 16M) wird der Zeitraum automatisch auf den verfügbaren Bereich reduziert.

**Wichtig — GSC-Daten-Latenz:** GSC-Daten sind typischerweise 2-3 Tage verzögert. Der Skill setzt das Enddatum aller Calls deshalb auf `today - 3 days`, nicht `today`. Das verhindert "leere Tage"-Artefakte am Range-Ende.

Zusätzliche Vergleichs-Zeitfenster für Trend-Analyse (jeweils mit dem 3-Tage-Versatz):

- **Aktuelle Periode**: letzte 90 Tage (heute-3 minus 90 bis heute-3)
- **Vergleichs-Periode 1**: 91-180 Tage davor (Quartals-Vergleich)
- **Vergleichs-Periode 2**: 365 Tage zurück versetzte 90-Tage-Periode (Jahres-Vergleich, sofern verfügbar)

### Schritt 4: Performance-Pull

Pro Zeitraum die relevanten search-console-MCP-Tools aufrufen. Details und genaue Tool-Parameter in `reference/gsc-api-nutzung.md`. Im **Modus fallback** (Ahrefs-MCP) verweisen die Hinweise in Klammern auf das jeweilige Fallback-Tool — siehe Tool-Mapping-Tabelle in `gsc-api-nutzung.md`.

**4.1 Domain-weiter Performance-Verlauf (16M)**

Tool: `mcp__search-console__analytics_time_series({siteUrl, startDate, endDate, granularity: "weekly", metrics: ["clicks", "impressions", "ctr", "position"]})`

Liefert pro Tag oder Woche (je nach `granularity`): clicks, impressions, ctr, position. Speichere als Liste in `~/.cache/reachx-mta/<slug>/audits/raw/gsc-performance-history.json (lokal, später komprimiert nach Drive assets/raw/)`.

*(Fallback Ahrefs: `gsc-performance-history`)*

**4.2 Top-200 Queries — aktuelle Performance + Vergleich**

Primär: `mcp__search-console__analytics_top_queries({siteUrl, days: 90, limit: 200, sortBy: "clicks"})`. Liefert pro Query: query-Text, clicks, impressions, ctr, position.

Für Top-Ranking-URL pro Query (wird für Cannibalization und Hidden-Content gebraucht): `mcp__search-console__analytics_query({siteUrl, dimensions: ["query", "page"], rowLimit: 1000})` — pro (Query, Page)-Paar die Metriken.

**Vergleich für Gewinner/Verlierer-Detection:** Nutze `mcp__search-console__analytics_compare_periods({siteUrl, period1Start, period1End, period2Start, period2End})` für domain-aggregierte Deltas. Für Query-Ebene-Deltas zwei `analytics_top_queries`-Calls mit unterschiedlichen `days`-Werten und diff lokal rechnen, ODER `seo_lost_queries({siteUrl})` für verlorene Queries direkt.

Für Top-100 zusätzlich Query-History: `mcp__search-console__analytics_time_series` mit `dimensions: ["date", "query"]` und Query-Filter — gibt Trend-Sparkline-Daten.

Roh-Daten in `~/.cache/reachx-mta/<slug>/audits/raw/gsc-queries.json` (lokaler Cache).

*(Fallback Ahrefs: `gsc-keywords` + `gsc-keyword-history`)*

**4.3 Top-100 Pages — Performance**

Tool: `mcp__search-console__analytics_top_pages({siteUrl, days: 90, limit: 100, sortBy: "clicks"})`

Pro Page: URL, clicks, impressions, ctr, position. Für Anzahl rankender Queries pro Page: `analytics_query({dimensions: ["page", "query"]})` mit page-Gruppierung lokal.

Optional für Top-30-Pages: `mcp__search-console__analytics_time_series` mit `dimensions: ["date", "page"]` und Page-Filter für Trend-Sparklines.

Roh-Daten in `~/.cache/reachx-mta/<slug>/audits/raw/gsc-pages.json` (lokaler Cache).

*(Fallback Ahrefs: `gsc-pages` + `gsc-page-history`)*

**4.4 Brand vs. Non-Brand-Split**

Tool: `mcp__search-console__seo_brand_vs_nonbrand({siteUrl, days: 90, brandTerms: [<aus meta.json.marke.synonyme>]})`

Liefert die Aufteilung der Klicks/Impressions/CTR in Brand-Anteil vs. Non-Brand-Anteil. Ersetzt die frühere Anonymous-Queries-Analyse als "wo kommt der Traffic strukturell her"-Signal. Bei sehr Brand-lastigen Domains (>50% Brand-Klicks → siehe `brand_dominant`-Auffälligkeit) ist der echte SEO-Hebel die Non-Brand-Performance.

Roh-Daten in `~/.cache/reachx-mta/<slug>/audits/raw/gsc-brand-split.json` (lokaler Cache).

*(Fallback Ahrefs: `gsc-anonymous-queries` — liefert ähnlichen Insight, aber andere Achse: Brand-vs-Non-Brand kann der direkte MCP, Anonymous-Cluster aggregiert nur der Ahrefs-Pfad)*

**4.5 Performance by Device**

Tool: `mcp__search-console__analytics_query({siteUrl, dimensions: ["device"], days: 90})`

Liefert clicks/impressions/ctr/position split nach `mobile`, `desktop`, `tablet`. Schlüssel-Signal für Branchen mit starkem Mobile-Bias (B2C, Local) oder schwachem Mobile (B2B).

*(Fallback Ahrefs: `gsc-performance-by-device`)*

**4.6 Performance by Country**

Tool: `mcp__search-console__analytics_by_country({siteUrl, days: 90, limit: 10})`

Top-10 Länder nach Klicks. Wichtig für internationale Akteure oder zur Validierung "Kunde glaubt DACH-only, GSC zeigt 30% US-Traffic".

*(Fallback Ahrefs: `gsc-metrics-by-country`)*

**4.7 CTR-by-Position-Benchmark**

Tool: `mcp__search-console__analytics_query({siteUrl, dimensions: ["query"], days: 90})` — daraus die Position-Bins lokal aggregieren (Pos 1, 2-3, 4-5, 6-10, 11-20, 21+) und domain-eigene CTR-Kurve berechnen.

Alternativ: `mcp__search-console__seo_primitive_ranking_bucket` falls verfügbar — liefert die Bucket-Aggregation direkt.

Vergleich mit Branchen-Benchmarks (siehe `reference/gsc-analyse-methodik.md` "CTR-Benchmarks") gibt den CTR-Gap-Indikator pro Query — der zentrale Hebel für `seo_low_ctr_opportunities` in Schritt 5.

*(Fallback Ahrefs: `gsc-ctr-by-position`)*

**API-Budget:** Gesamtlauf nutzt ausschließlich die kostenlose GSC-API (Quota: 1.200 Requests/Minute, 30k pro Property/Tag). Pro Skill-Lauf typisch 20-40 API-Calls, weit unter dem Limit. Im Fallback-Modus über Ahrefs: ca. 1.500-3.000 Ahrefs-Units. Details in `reference/gsc-api-nutzung.md` Abschnitt "API-Budget".

### Schritt 5: Analyse

Im **Modus direkt** bietet der search-console-MCP fünf eingebaute SEO-Analyse-Tools, die genau diese Kern-Analysen abdecken. Nutze sie als Primary, fall auf eigene Berechnung aus Rohdaten nur zurück wenn ein Tool fehlschlägt oder leere Antwort liefert. Methodik-Details (Schwellwerte, Berechnungs-Logik) in `reference/gsc-analyse-methodik.md`.

**5.1 Gewinner/Verlierer-Detection**

Primary-Tool: `mcp__search-console__seo_lost_queries({siteUrl, days: 90})` — liefert Queries, die im Vergleichszeitraum Klicks verloren haben. Plus `mcp__search-console__analytics_compare_periods` für die Domain-aggregierten Trend-Zahlen.

Wenn das Tool keine direkten "Gewinner"-Daten liefert: aus zwei `analytics_top_queries`-Calls (aktuelle 90T vs. 91-180T) lokal diffen. Schwellwerte:

- **Gewinner**: Klick-Anstieg ≥ +20% UND absolute Klick-Differenz ≥ 5 (kleine Queries filtern)
- **Verlierer**: Klick-Rückgang ≤ -20% UND absolute Klick-Differenz ≥ 5
- **Neu**: Queries, die in der Vergleichs-Periode 0 Klicks hatten und jetzt ≥ 5
- **Verloren**: Queries, die früher ≥ 5 Klicks hatten und jetzt 0

Bonus: `mcp__search-console__analytics_anomalies({siteUrl, days: 90})` für statistische Ausreißer-Detection (Drops/Spikes außerhalb der normalen Varianz).

Output: Top-10-Gewinner-Tabelle + Top-10-Verlierer-Tabelle.

**5.2 Cannibalization-Detection**

Primary-Tool: `mcp__search-console__seo_cannibalization({siteUrl, days: 90})` — direkter Tool-Call, liefert Queries mit mehreren konkurrierenden URLs out-of-the-box. Spart die eigene Konstruktion aus (Query, Page)-Paaren.

Fallback wenn das Tool leer liefert oder nicht verfügbar: Aus den `analytics_query`-Daten mit `dimensions: ["query", "page"]` selbst rechnen — pro Query ≥ 2 URLs mit Position ≤ 30 und Impressions-Summe ≥ 100 in 90 Tagen.

Output: Cannibalization-Tabelle mit Query, konkurrierenden URLs, jeweiligen Positionen, Empfehlung (Consolidation/Canonical/internes Linking).

**5.3 Hidden-Content-Discovery**

Kein direktes Tool — bleibt eigene Heuristik auf Rohdaten. Pro Top-50-Query mit Position ≤ 5: Prüfe, ob die ranking_url eine "offensichtliche Treffer-Page" ist (Produktseite, Service-Page) oder eine "versehentlich rankende Page" (alter Blog-Eintrag, About-Page, Pressemitteilung).

Heuristik: ranking_url enthält Pfad-Komponenten wie `/blog/`, `/news/`, `/presse/`, `/archiv/` UND clicks ≥ 20 in 90 Tagen → **Hidden-Content-Kandidat**.

Bonus: `mcp__search-console__analytics_organic_landing_pages({siteUrl})` liefert pro Landing-Page die Performance-Daten — gut für die Page-Kategorisierung (Blog/News vs. Service/Product).

Output: Hidden-Content-Liste mit Query, ranking_url, Klicks, Empfehlung.

**5.4 CTR-Gap**

Primary-Tool: `mcp__search-console__seo_low_ctr_opportunities({siteUrl, days: 90, minImpressions: 500})` — liefert Queries mit Position+Impression-Daten, deren CTR unter dem domain-internen Benchmark liegt. Direkter Drop-in für die CTR-Gap-Logik.

Methodik (auch für Fallback-Berechnung):
- CTR-Gap = `query_ctr - benchmark_ctr_bei_position`
- **CTR-Gap-Kandidat**: Gap ≤ -2 Prozentpunkte UND Impressions ≥ 500 in 90 Tagen
- Empfehlung: Title und Snippet überarbeiten

Output: CTR-Gap-Tabelle, sortiert nach Klick-Potenzial (Gap × Impressions).

**5.5 Position-zu-Klick-Hebel (Quick-Win-Pool)**

Primary-Tool: `mcp__search-console__seo_quick_wins({siteUrl, days: 90, minImpressions: 300})` — liefert Pos-11-20-Queries mit Impressions-Potenzial direkt, inklusive `potentialClicks`-Schätzung. Wenn der Skill auch Pos-4-10-Wins braucht (klassische Quick-Wins): zusätzlich `mcp__search-console__seo_striking_distance({siteUrl, days: 90})` für die Pos-4-10-Klasse.

Methodik:
- **Quick-Win Pos 4-10**: Position zwischen 4 und 10 UND Impressions ≥ 300 in 90 Tagen UND Klicks ≤ 30
- **Quick-Win Pos 11-20**: Position zwischen 11 und 20 UND Impressions ≥ 300 in 90 Tagen (Page-2-Push auf Page-1)
- Geschätztes Klick-Potenzial bei Sprung auf Position 3 = `impressions × ctr_benchmark_pos3` (siehe Methodik)

Output: Quick-Win-Tabelle mit Query, aktueller Position, Impressions, aktuellen Klicks, geschätztem Potenzial. Aufgeteilt in zwei Sub-Tabellen (Pos 4-10 und Pos 11-20).

**Übersicht — direkte SEO-Tools des search-console-MCP:**

| Analyse | Primary-Tool (Modus direkt) | Fallback |
|---|---|---|
| Gewinner/Verlierer | `seo_lost_queries` + `analytics_compare_periods` | aus 2 `analytics_top_queries`-Calls diffen |
| Cannibalization | `seo_cannibalization` | (Query, Page)-Aggregation aus `analytics_query` |
| Hidden-Content | (keine direkte Funktion) + `analytics_organic_landing_pages` für Page-Kategorie | Eigene Heuristik aus Rohdaten |
| CTR-Gap | `seo_low_ctr_opportunities` | Pos-Bucket × Domain-CTR-Kurve |
| Quick-Wins | `seo_quick_wins` (Pos 11-20) + `seo_striking_distance` (Pos 4-10) | Filter auf `analytics_top_queries` |
| Brand-Dominanz | `seo_brand_vs_nonbrand` | Token-Match auf `analytics_top_queries` |
| Anomalie-Erkennung | `analytics_anomalies` | (kein Fallback) |

### Schritt 6: CSV-Outputs

**`audits/gsc-performance.csv`** — Query-Ebene. Eine Zeile pro (Query, Periode)-Paar, damit Folge-Skills sowohl aktuelle als auch Vergleichs-Periode lesen können.

Spalten (siehe `reference/gsc-output-schema.md` für vollständiges Schema):

```
query, periode, datum_von, datum_bis, clicks, impressions, ctr, position, top_ranking_url, ist_anonymous, kategorie_analyse
```

`kategorie_analyse` ist ein Tag aus `{gewinner, verlierer, neu, verloren, cannibalization, hidden_content, ctr_gap, quick_win, none}`.

**`audits/gsc-pages.csv`** — Page-Ebene. Eine Zeile pro Page für die aktuelle 90-Tage-Periode.

Spalten:

```
page_url, clicks, impressions, ctr, position, anzahl_queries, kategorie_seite
```

`kategorie_seite` ist ein heuristischer Tag aus `{produkt, service, blog, news, presse, ueber_uns, kontakt, homepage, sonstige}` basierend auf URL-Pfad — wird auch für Hidden-Content-Discovery genutzt.

### Schritt 7: Aggregat-Markdown `audits/gsc-first-party.md`

Format mit YAML-Frontmatter nach `reference/gsc-output-schema.md` Abschnitt "Markdown-Schema". Frontmatter enthält:

- Skill-Metadaten, Recherche-Provenienz (Ahrefs-Projekt-ID, GSC-Verbindungsstatus, Zeiträume)
- `statistiken_90_tage` (clicks_total, impressions_total, ctr_avg, position_avg, anteil_brand_klicks, anteil_non_brand_klicks, top_country, top_device)
- `statistiken_trend_qoq` (clicks_delta_prozent, impressions_delta_prozent, top_3_gewinner_summe_klicks, top_3_verlierer_summe_klicks)
- `analyse_zaehler` (anzahl_gewinner, anzahl_verlierer, anzahl_cannibalization, anzahl_hidden_content, anzahl_ctr_gap, anzahl_quick_win)
- `auffaelligkeiten` (Liste der strategischen Beobachtungen, siehe Schritt 8)

Body strukturiert nach:

1. **Übersicht** (3-5 Sätze: was zeigt GSC im Vergleich zur Sistrix-Erwartung, wo sind die größten Hebel)
2. **Performance-Stand 90 Tage** (Klicks/Impressionen/CTR/Position aggregiert, plus QoQ-Veränderung)
3. **Performance-Verlauf 16 Monate** (Beschreibung der Hauptbewegungen, Saisonalität, Knickpunkte)
4. **Top-Queries** (Tabelle Top-30 nach Klicks, mit Periode-Vergleich)
5. **Top-Pages** (Tabelle Top-20 nach Klicks)
6. **Brand vs. Non-Brand** (Klick-Anteil, CTR pro Segment — aus `seo_brand_vs_nonbrand`. Im Fallback-Modus stattdessen Anonymous-Queries-Cluster aus Ahrefs)
7. **Device- und Country-Splits**
8. **Gewinner und Verlierer** (zwei Tabellen, Top-10 jeweils)
9. **Cannibalization** (Tabelle, sofern Fälle gefunden)
10. **Hidden-Content-Discovery** (Liste mit Empfehlungen)
11. **CTR-Gap-Quick-Wins** (Tabelle sortiert nach Klick-Potenzial)
12. **Position-zu-Klick-Quick-Wins** (Tabelle sortiert nach Klick-Potenzial)
13. **Auffälligkeiten** (aus Frontmatter, sortiert nach Relevanz)

### Schritt 8: Auffälligkeiten

Strategische Beobachtungen extrahieren, ähnlich wie in `03-01-seo-sichtbarkeit-und-rankings`:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `traffic_trend_negativ` | Klicks 90-Tage vs. 91-180-Tage um ≥ 25% gefallen | "GSC-Klicks sind in 90 Tagen um -32% gefallen — möglicher Penalty, Migration-Issue oder Wettbewerber-Aktivität." |
| `traffic_trend_positiv` | Klicks um ≥ 25% gestiegen | "Klicks um +47% gestiegen — laufende SEO-Aktivität sichtbar, in der Story als Beleg nutzen." |
| `brand_dominant` | Brand-Anteil ≥ 50% der Klicks (aus `seo_brand_vs_nonbrand`) | "60% der GSC-Klicks kommen aus Brand-Suchen — der echte SEO-Hebel liegt im Non-Brand-Bereich. In Quick-Win-Berechnung Brand-Anteil herausnehmen." |
| `cannibalization_haeufig` | ≥ 5 Cannibalization-Fälle | "5+ Queries mit konkurrierenden URLs — IA-Review notwendig." |
| `hidden_content_relevant` | ≥ 3 Hidden-Content-Treffer mit ≥ 50 Klicks zusammen | "3 versehentlich rankende Blog-Pages bringen 200+ Klicks — Content-Ausbau-Opportunität." |
| `ctr_gap_systematisch` | ≥ 10 Queries mit Gap ≤ -2 Prozentpunkten | "Domain-CTR liegt systematisch unter Benchmark — Title/Snippet-Optimierung als Cluster-Hebel." |
| `quick_win_cluster` | ≥ 20 Quick-Wins mit Gesamt-Potenzial ≥ 300 Klicks/Monat | "20+ Position-4-10-Queries mit zusammen ~350 Klick-Potenzial — strukturierter Inhalts-Refresh-Plan empfohlen." |
| `mobile_underperformance` | Mobile-CTR < 70% der Desktop-CTR bei gleicher Position | "Mobile-Klick-Performance deutlich unter Desktop — Mobile-Snippets / Mobile-UX prüfen." |
| `non_dach_traffic_signifikant` | Nicht-DACH-Land hat ≥ 15% Klick-Anteil | "15%+ Traffic aus [Land] — internationaler Markt unterschätzt? Stratege prüfen." |
| `sistrix_gsc_divergenz` | Sistrix-VI hoch, aber GSC-Klicks niedrig (nur prüfbar wenn 03-01-seo-sichtbarkeit-und-rankings schon lief) | "Sistrix zeigt VI 0.45, GSC zeigt nur 200 Klicks/Monat — Modell-vs-Realität-Diskrepanz, Story-relevant." |

Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung.

### Schritt 9: HTML-Report `reports/05a-gsc-first-party.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html` bauen. Nummer `05a` (vor `06-seo-sichtbarkeit.html`, damit GSC im Dashboard sichtbar vor Sistrix steht — `05a` statt `05` damit nicht mit anderen Stufe-3-Audits kollidiert).

Platzhalter:

- `{{TITLE}}` → `SEO First-Party (GSC) · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · SEO First-Party`
- `{{DISPLAY_NAME}}` → `SEO First-Party-Daten aus Google Search Console: KUNDE`
- `{{META_LINE}}` → `Quelle: GSC via search-console-MCP · Datenstand: <ISO> · Zeitraum: 16 Monate · Generiert: <heute>` (im Fallback-Modus: `GSC via Ahrefs-MCP (Reduced)`)
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip oben**: Klicks/90T, Impressionen/90T, Avg-CTR, Avg-Position, QoQ-Klick-Trend (Prozent + Pfeil), Non-Brand-Anteil-Prozent, Anzahl Quick-Wins
  - **Sticky-TOC**: Verlauf, Top-Queries, Top-Pages, Brand-Split, Device/Country, Gewinner/Verlierer, Cannibalization, Hidden-Content, CTR-Gap, Quick-Wins, Auffälligkeiten
  - **16M-Verlauf**: SVG-Linechart (Klicks und Impressions parallel auf Doppel-Y-Achse), oder Fallback-Text-Tabelle wenn SVG zu komplex
  - **Top-Queries** als `table.data` mit Trend-Badge pro Zeile (↑/↓/→)
  - **Top-Pages** analog
  - **Brand vs. Non-Brand** als Hinweis-Card mit Anteil-Prozenten (Brand-Klicks vs. Non-Brand-Klicks, jeweils mit CTR-Vergleich)
  - **Device-Split** als kleine 3-Balken-Visualisierung
  - **Country-Split** als Tabelle
  - **Gewinner/Verlierer** je als `details.skill[data-status="..."]` Block
  - **Cannibalization** als Tabelle mit Empfehlungen pro Zeile
  - **Hidden-Content-Discovery** als `.suggestion`-Block-Liste
  - **CTR-Gap** als Tabelle, sortiert nach Klick-Potenzial absteigend, oben markiert
  - **Quick-Wins** als prominente Tabelle (Position-zu-Klick-Hebel), Top 20 mit geschätztem Klick-Potenzial
  - **Auffälligkeiten-Block** als `.suggestion`-Block mit Top 3-5 strategischen Beobachtungen
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · SEO-First-Party-GSC-Audit`

`<body>` ohne Klasse → Back-Link zum Dashboard sichtbar (siehe `contracts.md` Abschnitt 7).

### Schritt 9b: Outputs nach Drive hochladen

Finale Outputs via `drive.py upsert-text` nach Drive (idempotent):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "gsc-first-party.md" \
  ~/.cache/reachx-mta/<slug>/gsc-first-party.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "gsc-performance.csv" \
  ~/.cache/reachx-mta/<slug>/gsc-performance.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "gsc-pages.csv" \
  ~/.cache/reachx-mta/<slug>/gsc-pages.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "05a-gsc-first-party.html" \
  ~/.cache/reachx-mta/<slug>/05a-gsc-first-party.html "text/html"
```

CSV bleibt CSV (kein Auto-Convert zu Google Sheet).

### Schritt 10: Dashboard-Update

`reports/index.html` aus Drive lesen, anpassen, zurückschreiben:

```bash
INDEX_ID=$(python3 "$DRIVE_PY" list-children "$REPORTS_ID" | jq -r '.[] | select(.name == "index.html") | .id')
python3 "$DRIVE_PY" read "$INDEX_ID" > /tmp/index.html
# … HTML anpassen …
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "index.html" /tmp/index.html "text/html"
```

Aktualisiere `reports/index.html`:

- Stat-Strip um GSC-90T-Klicks und QoQ-Trend ergänzen
- "Erledigt"-Sektion erweitern um `03-04-seo-first-party-gsc`
- Reports-Liste um `05a-gsc-first-party.html` erweitern
- Stufe 3 als "in Arbeit" markieren
- "Nächster empfohlener Schritt": die übrigen First-Party-Skills `03-18-web-analytics-ga4` und `03-17-sea-first-party-google-ads` (First-Party-Block zusammen abarbeiten), danach `02-02-wettbewerber-identifikation` (nutzt die First-Party-Outputs als Seed-Keywords)

### Schritt 11: `status.md` aktualisieren

Aus Drive lesen, anpassen, zurückschreiben:

```bash
STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > /tmp/status.md
# … Frontmatter+Body anpassen …
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"
```

Nach Regeln aus `contracts.md` Abschnitt 3:

- `03-04-seo-first-party-gsc` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, kompakten Highlight-Numbers (Klicks/90T, QoQ-Delta, Quick-Win-Anzahl)
- `naechster_empfohlen`: zuerst die noch nicht gelaufenen First-Party-Skills (`03-18-web-analytics-ga4`, dann `03-17-sea-first-party-google-ads` — der First-Party-Block wird zusammen abgearbeitet), danach `02-02-wettbewerber-identifikation` mit dem Hinweis, dass es die First-Party-Outputs (GSC-Top-Queries als Seed-Keywords) nutzt. `03-01-seo-sichtbarkeit-und-rankings` und die übrigen Audits nachgelagert, sobald die Wettbewerber stehen.
- Bei `traffic_trend_negativ` oder `cannibalization_haeufig`: explizit als Hinweis "in MTA-Story als Schwerpunkt einplanen"

### Schritt 12: Standard-Schlussformat im Chat

```
✓ 03-04-seo-first-party-gsc abgeschlossen.

Outputs:
- audits/gsc-first-party.md — Aggregat mit Trend-Analyse, Cannibalization, Hidden-Content, Quick-Wins
- audits/gsc-performance.csv — Query-Ebene (N Zeilen), Basis für SEO-Folge-Skills
- audits/gsc-pages.csv — Page-Ebene (M Zeilen)
- reports/05a-gsc-first-party.html — visueller First-Party-Audit
Status aktualisiert in: status.md

GSC-Highlights (90 Tage):
- Klicks:               XXX (QoQ +/- Z%)
- Impressionen:         XXX
- Avg-CTR:              X,X%
- Avg-Position:         X,X
- Non-Brand-Anteil:     XX% (im Fallback-Modus: Anonymous-Anteil aus Ahrefs)

Gefundene Hebel:
- Gewinner:             N (Top: <query> +X%)
- Verlierer:            N (Top: <query> -X%)
- Cannibalization:      N Fälle
- Hidden-Content:       N Kandidaten
- CTR-Gap:              N Queries unter Benchmark
- Quick-Wins (Pos 4-10): N mit ~Z geschätzten Zusatz-Klicks/Monat

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- (1-3 Punkte aus der Auffälligkeiten-Liste, sortiert nach Relevanz)

Nächste Schritte:
1. 03-18-web-analytics-ga4 — nächster First-Party-Skill, der Block wird zusammen abgearbeitet
2. 03-17-sea-first-party-google-ads — letzter First-Party-Skill, vervollständigt die Realitäts-Basis
3. danach 02-02-wettbewerber-identifikation — nutzt die First-Party-Outputs (GSC-Top-Queries als echte Seed-Keywords) zur Schärfung der Wettbewerber-Recherche
4. (danach / sobald die Wettbewerber stehen) 03-01-seo-sichtbarkeit-und-rankings — Sistrix-Sichtbarkeit ergänzt die first-party-Sicht um Wettbewerbs-Vergleich

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/gsc-api-nutzung.md` — search-console-MCP-Tool-Inventar als Primary, Ahrefs-MCP-GSC-Tools als Fallback, Tool-Mapping-Tabelle, Domain-Matching, OAuth-Setup, Rate-Limits, Edge-Cases
- `reference/gsc-output-schema.md` — CSV-Spalten + Markdown-Frontmatter-Schema, Validierungs-Regeln
- `reference/gsc-analyse-methodik.md` — Gewinner/Verlierer-Schwellwerte, Cannibalization-Regeln, Hidden-Content-Heuristik, CTR-Benchmarks pro Position, Quick-Win-Potenzial-Formel

## Edge Cases

- **GSC-Property nicht verbunden** → freundlicher Skip mit Anleitung (siehe Schritt 2). KEIN Abbruch des MTA-Workflows. `status.md` markiert den Skill als geskippt mit Grund.

- **GSC-Property erst kürzlich verbunden** (weniger als 16M Historie) → Zeitraum wird automatisch auf verfügbaren Bereich reduziert. Hinweis im Frontmatter `historie_verfuegbar_tage` und im Body-Übersicht "GSC-Anbindung seit X Tagen, voller 16M-Vergleich nicht möglich".

- **Kunde hat mehrere GSC-Properties** (Hauptdomain + Subdomains, oder www + non-www, oder Domain-Property + URL-Prefix-Property) → Default: nehme die in `management-projects` zuerst gelistete passende Property. Wenn mehrere passen, im Schluss-Format Hinweis "X Properties gefunden, nutze <gewählte>. Stratege-Override möglich via Argument `property=<id>`".

- **Sehr kleine GSC-Daten** (Top-Query hat unter 10 Klicks/90T) → Skill läuft durch, markiert aber `daten_qualitaet: niedrig` im Frontmatter, Hinweis im Schluss-Format dass "Quick-Win-Empfehlungen mit Vorsicht zu lesen sind, Datenbasis dünn".

- **Brand-Query dominiert** (Top-Query ist Marken-Name mit >50% der Gesamtklicks) → Auffälligkeit `brand_dominant`, Empfehlung "Non-Brand-Performance gesondert betrachten, Brand-Anteil aus Quick-Win-Berechnung herausnehmen für realistische Hebel-Schätzung".

- **GSC-API Rate-Limit (selten)** → kostenlose GSC-API hat 1.200 Requests/Minute und 30k pro Property/Tag — bei normalem Skill-Lauf weit unterhalb. Falls doch erreicht: 60s warten, einmal retry. Bei wiederholtem Limit: bisher erhobene Daten schreiben, Rest als offen markieren, Hinweis im Schluss-Format. Im Fallback-Modus (Ahrefs) gilt dieselbe Recovery-Logik gegen Ahrefs-429.

- **OAuth-Token abgelaufen** → der `npx -y search-console-mcp@1.13.5` startet automatisch einen Refresh, wenn das Refresh-Token noch gültig ist. Wenn Refresh fehlschlägt (Token revoked, Account-Wechsel): freundlicher Hinweis "Bitte einmal `npx -y search-console-mcp@1.13.5 setup` erneut ausführen und Claude Code neu starten". Skill bricht sauber ab statt mit Auth-Errors abzustürzen.

- **CSV existiert bereits** (Re-Run) → frage analog `03-01-seo-sichtbarkeit-und-rankings`:
  - **(a) überschreiben**
  - **(b) Backup-und-neu** — alte Versionen nach `audits/_backup/gsc-*-<ISO>.csv`
  - **(c) abbrechen**

- **`seo_brand_vs_nonbrand` liefert leere oder unzuverlässige Antwort** (sehr kleine Domain, fehlende Brand-Terms in `meta.json.marke.synonyme`) → `anteil_brand_klicks: null`, kein Auffälligkeits-Eintrag. Token-Match-Fallback aus den Top-Queries möglich, wenn der Stratege Brand-Synonyme im Aufruf nachliefert.

- **CTR-Benchmark zu dünn** (zu wenig Position-Datenpunkte für domain-eigene Kurve) → Fallback auf branchen-generische CTR-Benchmarks aus `reference/gsc-analyse-methodik.md`. Hinweis im Body, dass CTR-Gap auf Benchmark-Basis berechnet ist statt Domain-eigener Kurve. `seo_low_ctr_opportunities` nutzt intern bereits domain-eigene Benchmarks, fällt aber bei sehr wenigen Queries auf Generic zurück.

- **`seo_cannibalization` liefert leere Antwort** → fällt der Skill auf eigene Konstruktion aus `analytics_query` mit `dimensions: ["query", "page"]` zurück (siehe `gsc-api-nutzung.md` "Cannibalization-Konstruktion"). Wenn auch das nichts liefert: Auffälligkeit `cannibalization_keine_funde` (statt `cannibalization_haeufig`).

- **Conflict mit `03-01-seo-sichtbarkeit-und-rankings`-Reihenfolge** → Wenn Sistrix-Skill schon lief und Strategin GSC nachschiebt: kein Problem, beide Skills arbeiten unabhängig. GSC-Skill kann zusätzliche Auffälligkeit `sistrix_gsc_divergenz` produzieren (wenn die Sistrix-Daten verfügbar sind).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/gsc-first-party.md`)
- Markdown + YAML-Frontmatter für `gsc-first-party.md`, CSV für `gsc-performance.csv` und `gsc-pages.csv` (via `drive.py upsert-text`)
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (auch bei Skip), via `drive.py upsert-text`
- HTML-Report basiert auf `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **GSC-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/gsc-*.json`, am Ende komprimiert nach Drive `assets/raw/`
- **GSC-MCP-Auth ist unabhängig von gws** — der search-console-MCP nutzt einen eigenen OAuth-Token, separat von der Drive-Authentifizierung
- **Klick-Werte unverändert lassen** — GSC-Daten sind Roh-Realität, Normalisierung ist Aufgabe der Synthese-Skills
- **First-party VOR third-party**: Skill ist absichtlich vor `03-01-seo-sichtbarkeit-und-rankings` positioniert. Wenn beide gelaufen sind, kann `04-02-kanal-chancen-analyse` beide Datenquellen kombinieren.
- **Credential-Disziplin (contracts.md Abschnitt 11)**: Dieser Skill nutzt keinen API-Key-basierten Zugang — der search-console-MCP nutzt OAuth via macOS Keychain. Kein Scanning von Environment-Variablen oder Shell-Config-Dateien nach Credentials. Fehlt die MCP-Verbindung: freundlicher Skip wie in Schritt 1 beschrieben.
