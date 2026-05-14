# GSC-API-Nutzung

Wie der Skill Google-Search-Console-Daten beschafft. Zwei Pfade:

1. **Primary — dedizierter search-console-MCP** (saurabhsharma2u/search-console-mcp). Direkter Zugriff auf die kostenlose GSC-API über OAuth mit einem zentralen Agentur-Account. Empfohlen, tiefere Daten, keine Ahrefs-Units.
2. **Fallback — Ahrefs-MCP-GSC-Tools** (`mcp__1d9710a6-f270-4555-88f8-e4367948d936__gsc-*`). Verfügbar wenn der dedizierte MCP nicht installiert ist. Reduced-Modus mit Hinweis im Schluss-Format.

## Zugangs-Reihenfolge

1. **search-console-MCP prüfen** — Tools mit Prefix `mcp__search-console__*` müssen verfügbar sein (insbesondere `sites_list`, `analytics_top_queries`, `analytics_top_pages`, `analytics_time_series`, `analytics_compare_periods`, `seo_quick_wins`, `seo_cannibalization`, `seo_low_ctr_opportunities`).
2. **GSC-Property im Account verfügbar prüfen** — über `mcp__search-console__sites_list({engine: "google"})`. Match gegen Kunden-Domain (siehe "Domain-Matching" unten).
3. **Wenn nicht da: Ahrefs-MCP-Fallback prüfen** — Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__`. Plus `management-projects` für Property-Auffindung.
4. **Beides nicht da** → Skill skippt freundlich (siehe SKILL.md Schritt 1). Direkter OAuth-Setup im Skip-Hinweis erklärt.

## OAuth-Setup search-console-MCP (einmalig pro Mac)

```bash
# 1. OAuth-Browser-Flow starten (Token wird in macOS Keychain gespeichert)
npx -y search-console-mcp@1.13.5 setup

# 2. Verifizieren, dass Properties zugänglich sind
npx -y search-console-mcp@1.13.5 accounts list

# 3. In Claude Code registrieren (user-scoped, gepinnte Version)
claude mcp add search-console --scope user -- npx -y search-console-mcp@1.13.5

# 4. Claude Code neu starten
```

**Berechtigungs-Scope** beim OAuth-Dialog: erwarte `webmasters.readonly` (nur Lesezugriff). Wenn `webmasters` ohne `.readonly` angefordert wird, abbrechen — zu weiter Scope.

**Token-Storage**: macOS Keychain (hardware-gebunden), Fallback `~/.search-console-mcp-config.enc` mit AES-256-GCM, Schlüssel aus Machine-ID abgeleitet. Token ist NICHT zwischen Geräten portabel.

**Property-Freigabe pro Kunde**: Der Kunde muss den OAuth-Account (E-Mail aus `accounts_list` ablesbar) als Nutzer in seiner GSC-Property hinzufügen. Permission-Level `siteRestrictedUser` reicht für read-only Pulls.

## Tool-Mapping search-console-MCP ↔ Ahrefs-MCP-Fallback

Im **Modus direkt** primär nutzen, im **Modus fallback** auf den Ahrefs-Pfad ausweichen. Spalten-Namen und Parameter-Details in der jeweiligen Tool-Doku.

| Funktion | Primary (search-console-MCP) | Fallback (Ahrefs-MCP) |
|---|---|---|
| Property-Auflistung | `sites_list({engine: "google"})` | `management-projects` |
| Account-Status | `accounts_list` | (in management-projects integriert) |
| Domain-weiter Trend | `analytics_time_series({metrics, granularity})` | `gsc-performance-history` |
| Performance-Snapshot | `analytics_performance_summary` | (aus `gsc-performance-history` ableiten) |
| Top-Queries | `analytics_top_queries({limit, sortBy})` | `gsc-keywords` |
| Query-History | `analytics_time_series({dimensions: ["date","query"]})` mit Filter | `gsc-keyword-history` |
| Top-Pages | `analytics_top_pages({limit, sortBy})` | `gsc-pages` |
| Page-History | `analytics_time_series({dimensions: ["date","page"]})` mit Filter | `gsc-page-history` |
| Aggregierter Page-Trend | `analytics_time_series` | `gsc-pages-history` |
| (Query, Page)-Drill-down | `analytics_query({dimensions: ["query","page"]})` | (Ahrefs-Pfad muss konstruieren) |
| Performance by Device | `analytics_query({dimensions: ["device"]})` | `gsc-performance-by-device` |
| Position-Bucketing | `seo_primitive_ranking_bucket` oder `analytics_query` mit Position-Bins | `gsc-performance-by-position` |
| Position-Trend | `analytics_time_series({metrics: ["position"]})` | `gsc-positions-history` |
| Performance by Country | `analytics_by_country({limit})` | `gsc-metrics-by-country` |
| CTR-by-Position-Kurve | aus `analytics_query` lokal aggregieren (oder `seo_primitive_ranking_bucket`) | `gsc-ctr-by-position` |
| Anonymous-Queries-Anteil | ❌ nicht direkt — nutze stattdessen `seo_brand_vs_nonbrand` für Brand-Anteil-Analyse | `gsc-anonymous-queries` |
| Period-Vergleich | `analytics_compare_periods` | (zwei Aufrufe diffen) |
| Anomalie-Erkennung | `analytics_anomalies` | (kein Äquivalent) |

## Eingebaute SEO-Analyse-Tools (Modus direkt)

Ein zentraler Vorteil des dedizierten MCP: viele Analysen sind als direkte Tool-Calls verfügbar, statt aus Rohdaten konstruiert werden zu müssen.

| Analyse | Direkter Tool-Call |
|---|---|
| Quick-Wins Pos 11-20 | `seo_quick_wins({siteUrl, days, minImpressions, limit})` — liefert query, page, position, impressions, `potentialClicks` |
| Quick-Wins Pos 4-10 (Striking Distance) | `seo_striking_distance({siteUrl, days})` |
| Cannibalization | `seo_cannibalization({siteUrl, days})` — direkt, ohne (Query, Page)-Konstruktion |
| CTR-Gap | `seo_low_ctr_opportunities({siteUrl, days, minImpressions})` |
| Verlorene Queries | `seo_lost_queries({siteUrl, days})` |
| Brand vs. Non-Brand | `seo_brand_vs_nonbrand({siteUrl, days, brandTerms})` |
| SEO-Recommendations (allgemein) | `seo_recommendations({siteUrl})` |
| Traffic-Drop-Attribution | `analytics_drop_attribution({siteUrl})` |
| URL-Indexing-Check | `inspection_inspect({siteUrl, url})` und `inspection_batch` |

**Empfehlung im Skill:** Bei jeder Sub-Analyse zuerst das passende Built-in-Tool versuchen. Nur bei leerer/fehlerhafter Antwort auf die manuelle Berechnung aus Rohdaten fallen.

## Domain-Matching (`sites_list` → Kunde)

Aus `meta.json.website` die Kunden-Domain extrahieren, normalisieren (siehe `03-01-seo-sichtbarkeit-und-rankings/reference/sistrix-api-nutzung.md` Abschnitt "Domain-Normalisierung" — gleiche Logik):

1. URL parsen, Host extrahieren
2. `www.` entfernen
3. Lowercase

Dann in der `sites_list`-Antwort prüfen. GSC kennt zwei Property-Typen:

**URL-Prefix Property** — `siteUrl` ist eine vollständige URL, z. B. `https://avadent.de/`, `http://www.gearparts24.de/`, `https://www.primomedico.com/de/`. Match wenn der Host-Teil dem Kunden entspricht.

**Domain Property** — `siteUrl` hat das Präfix `sc-domain:`, z. B. `sc-domain:avadent.de`. Match wenn das Suffix dem Kunden entspricht. Deckt alle Subdomains und Protokolle ab.

**Match-Stufen:**

1. **Domain-Property-Match** — bevorzugen, weil sie umfassender ist (alle Subdomains, alle Protokolle)
2. **URL-Property-Match** — wenn keine Domain-Property existiert
3. **Mehrfach-Match URL-Property** — z. B. `http://kunde.de/` und `https://www.kunde.de/`. Bevorzuge HTTPS, dann `www`. Markiere die Wahl im Frontmatter (`property_gewaehlt`).

Wenn kein Match → freundlicher Skip-Pfad (siehe SKILL.md Schritt 2 Fall 2). Im Skip-Hinweis explizit die E-Mail-Adresse aus `accounts_list` nennen, damit der Kunde weiß, welches Konto er einladen muss.

## Permission-Level beachten

`sites_list` liefert pro Property auch das Permission-Level:

| Level | Bedeutung | Skill-Verhalten |
|---|---|---|
| `siteOwner` | volle Rechte (verifiziert) | ✓ Daten-Pull möglich |
| `siteFullUser` | Lese-/Schreib-Zugriff (außer User-Management) | ✓ Daten-Pull möglich |
| `siteRestrictedUser` | Lese-Zugriff | ✓ Daten-Pull möglich (für unseren Use-Case ausreichend) |
| `siteUnverifiedUser` | Account ist in Property gelistet, aber Verifikation ausstehend | ✗ kein Daten-Zugriff → Skip mit Hinweis |

## Zeitraum-Defaults

- **Aktuelle Periode**: heute - 90 Tage bis heute - 3 Tage (3-Tage-Puffer, weil GSC 1-3 Tage Verzögerung hat)
- **Vergleichs-Periode 1 (QoQ)**: heute - 180 Tage bis heute - 91 Tage
- **Jahres-Vergleich (YoY)**: heute - 455 Tage bis heute - 365 Tage (nur wenn Anbindung ≥ 16M alt)
- **16M-Verlauf**: heute - 480 Tage bis heute - 3 Tage

**Wenn Property jünger als 16M:** Verfügbarkeits-Check via erstem Datenpunkt in `analytics_time_series` (oder Fallback-Probe). Zeitraum-Defaults automatisch reduzieren auf den verfügbaren Bereich. Frontmatter-Feld `historie_verfuegbar_tage` setzen.

## API-Budget

**Modus direkt — kostenlose GSC-API:**

Quota: **1.200 Requests/Minute, 30.000 Requests/Property/Tag**. Pro Skill-Lauf typisch 20-40 API-Calls (Tool-Calls können mehrere API-Requests intern bündeln, aber bleiben weit unter dem Limit).

Strategie:
- Sequenzielle Calls, nicht parallel — vermeidet Bursts
- Bei 429: 60s warten, einmal retry, dann erhobene Daten schreiben und Rest als offen markieren
- Bei sehr großen Properties (Top-1k-Queries gewünscht): `analytics_query` mit `rowLimit` höher setzen statt mehrere paginierte Calls

**Modus fallback — Ahrefs-Units:**

| Tool | Units pro Call (geschätzt) |
|---|---|
| `management-projects` | 0-5 (Metadata) |
| `gsc-performance-history` | 10-30 |
| `gsc-keywords` (Limit 200) | 50-100 |
| `gsc-keyword-history` × 100 Queries | 500-1000 |
| `gsc-pages` (Limit 100) | 30-50 |
| `gsc-page-history` × 30 Pages | 150-300 |
| `gsc-anonymous-queries` | 10-30 |
| `gsc-performance-by-device` | 10-20 |
| `gsc-metrics-by-country` | 10-20 |
| `gsc-ctr-by-position` | 10-20 |

**Gesamt im Fallback-Modus:** geschätzt 1.500-3.000 Ahrefs-Units. Bei 400k/Monat-Budget unkritisch, aber unnötig wenn der direkte MCP verfügbar wäre.

## Cannibalization-Konstruktion

**Im Modus direkt:** `mcp__search-console__seo_cannibalization({siteUrl, days})` liefert die Daten direkt out-of-the-box. Pro Query: konkurrierende URLs mit Position + Impressions. Kein manueller Aufbau nötig.

Wenn das Tool leer liefert (sehr kleine Properties): Fallback auf manuelle Konstruktion über `analytics_query({dimensions: ["query", "page"]})` mit ausreichend hohem `rowLimit`. Lokale Aggregation: pro Query alle Pages sammeln, Cannibalization-Kandidat wenn ≥ 2 Pages mit Position ≤ 30 und gemeinsame Impressions-Summe ≥ 100 in 90 Tagen.

**Im Modus fallback:** Ahrefs-`gsc-keywords` liefert typischerweise nur die Top-1-ranking-URL pro Query. Drei-stufiger Fallback:

- **Option A**: Wenn `gsc-keywords` einen Parameter wie `group_by: query,page` oder `include_all_pages: true` unterstützt — nutzen.
- **Option B**: Top-100-Queries durchgehen, pro Query `gsc-keyword-history` mit Page-Drill-down. Teurer.
- **Option C**: Cannibalization-Analyse ausfallen lassen, Hinweis "MCP-Version unterstützt diese Drill-down nicht" im Output. Empfehlung: search-console-MCP installieren.

## Fehler-Behandlung

| Fehler | Reaktion |
|---|---|
| Weder search-console-MCP noch Ahrefs-MCP verfügbar | Freundlicher Skip mit Setup-Anleitung (SKILL.md Schritt 1) |
| `sites_list` schlägt fehl (Auth/Token) | "OAuth-Token abgelaufen — bitte `npx -y search-console-mcp@1.13.5 setup` erneut ausführen", sauberer Abbruch |
| Kein passendes Property im Account | Freundlicher Skip mit E-Mail-Hinweis (SKILL.md Schritt 2 Fall 2) |
| Property `siteUnverifiedUser` | Freundlicher Skip mit Hinweis zur Verifikation |
| 429 (GSC Rate-Limit) | 60s warten, einmal retry, dann teil-schreiben |
| 429 (Ahrefs Rate-Limit im Fallback-Modus) | Analog 60s + Retry |
| 5xx | 30s warten, einmal retry, dann Tool als "fehlgeschlagen" markieren, weiter mit nächstem |
| Leere Antwort bei nicht-kritischen Tools (`seo_brand_vs_nonbrand`, `analytics_anomalies`) | Feld auf `null` setzen, kein Skill-Abbruch |
| Leere Antwort bei kritischen Tools (`analytics_top_queries`, `analytics_time_series`) | Hinweis "GSC liefert keine Daten — Property erst kürzlich verbunden? Datenstand prüfen", `daten_qualitaet: keine`, sauber abschließen |

## Roh-Daten-Caching

Pro Tool-Aufruf die Roh-Antwort in `audits/raw/gsc-<tool-slug>.json` ablegen. Struktur:

```json
{
  "tool": "analytics_top_queries",
  "mcp": "search-console" | "ahrefs-fallback",
  "siteUrl": "<url>",
  "params": { "days": 90, "limit": 200, "sortBy": "clicks" },
  "abgefragt_am": "<ISO>",
  "response": { ...komplette Antwort... }
}
```

Vorteil:
- Folge-Skills (`03-02-seo-keyword-recherche`, `03-15-web-content-inventur`) können daraus lesen ohne Re-Calls
- Reproduzierbarkeit
- Debug bei merkwürdigen Werten
- Im Fallback-Modus dokumentiert das `mcp`-Feld, dass die Daten aus Ahrefs statt direkt von GSC kommen — relevant für die Folge-Skill-Cross-Reads

Bei mehreren Periode-Aufrufen pro Tool: Dateiname-Suffix mit Periode, z. B. `gsc-top-queries-current.json`, `gsc-top-queries-comparison.json`.

## Was NICHT in diesen Skill gehört

- **Service-Account-Setup für GSC** — bewusst nicht. OAuth-Desktop-Flow ist sauber und ausreichend. Service Accounts würden Aufwand und Sicherheitsfläche erhöhen (JSON-Key auf Festplatte, manuelle Property-Einladung pro Kunde) und sind nur sinnvoll für CI/Server-Setups.
- **GA4-Daten** — der search-console-MCP kann das technisch (Tools `analytics_organic_landing_pages`, `analytics_user_behavior` etc. sind GSC-zentriert; `analytics_ecommerce`, `analytics_realtime` wären GA4), aber dieser Skill konsumiert sie nicht. GA4-Anbindung erfordert separates Service-Account-Setup und gehört in einen eigenen Skill, sobald gebaut.
- **Bing-Webmaster-Daten** — der MCP unterstützt auch Bing (`bing_*` Tools), Auth aber separat (API-Key statt OAuth). Nicht für die MTA-Pipeline aktiv, kann später ergänzt werden.
- **Wettbewerber-GSC-Daten** — gibt es nicht, GSC ist first-party-only. Wettbewerbs-Sicht kommt aus `03-01-seo-sichtbarkeit-und-rankings`.
- **Difficulty-Werte** — gehört in `03-02-seo-keyword-recherche`.
- **Inhaltliches Content-Audit pro Page** — gehört in `03-15-web-content-inventur`.
- **Cluster/Intent/Funnel-Tagging der Queries** — gehört in `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf).
