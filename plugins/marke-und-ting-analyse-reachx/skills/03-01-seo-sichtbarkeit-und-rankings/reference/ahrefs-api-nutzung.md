# Ahrefs-MCP-Nutzung

Wie der Skill Ahrefs anspricht — ausschließlich über die Ahrefs-MCP-Verbindung (kein direkter HTTP-Fallback in diesem Skill). Plus die Liste der relevanten MCP-Tools, Spalten-Auswahl, Unit-Kosten und Fehler-Behandlung.

REACHX-Account hat ein Monatsbudget von **400.000 Units**. Eine durchschnittliche MTA mit 10 Akteuren verbraucht ca. 4.000–8.000 Units — also gut planbar, aber Re-Runs ohne Cache können das Budget schnell aufessen.

## Zugangs-Reihenfolge (Skill-Logik)

1. **MCP-Tools prüfen** — der Skill scannt verfügbare Tools auf Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__site-explorer-*` und `mcp__1d9710a6-f270-4555-88f8-e4367948d936__subscription-info-*`. Mindestens erwartet:
   - `site-explorer-metrics`
   - `site-explorer-metrics-history`
   - `site-explorer-domain-rating`
   - `site-explorer-domain-rating-history`
   - `site-explorer-organic-keywords`
   - `site-explorer-organic-competitors`
2. **Optional**: `site-explorer-top-pages` für `03-15-web-content-inventur`-Vorbereitung.
3. **Healthcheck**: `subscription-info-limits-and-usage` aufrufen, Restbudget lesen. Bei < 5.000 Units Warnung im Schluss-Format.
4. **MCP fehlt** → Reduced-Modus aktivieren, Ahrefs-Sektion komplett überspringen. **Kein HTTP-API-Fallback** in diesem Skill (Ahrefs-HTTP-API hat eigenes Auth-Modell, lohnt sich für die ergänzende Rolle nicht).

## Domain-Mode

**Pflicht: `mode=subdomains`** für alle Ahrefs-Tools verwenden. Begründung (laut MCP-Tool-Doku): `mode=domain` schließt Subdomains aus, was für DACH-Kunden mit `shop.*`, `blog.*` etc. zu unvollständigen Ergebnissen führt. `mode=exact_url` ist für Page-Level-Analysen, hier nicht relevant.

Bei explizit subdomain-spezifischen Akteuren (z. B. `shop.beispiel.de` als eigene Marke) trotzdem `mode=subdomains` — Ahrefs erkennt die genaue Subdomain im `target`-Parameter und scopiert intern korrekt.

## Domain-Normalisierung

Identisch zu Sistrix (siehe `sistrix-api-nutzung.md`). Eine einzige normalisierte Domain pro Akteur, beide Tools sprechen damit dieselbe Domain an — sonst werden Matches in Schritt 3b unmöglich.

## Relevante Tools

Pro Tool: was es liefert, welche Parameter wichtig sind, welche `select`-Spalten gesetzt werden, ungefähre Unit-Kosten.

### `site-explorer-metrics`

Snapshot der Kern-Metriken einer Domain.

Wichtige Parameter:
- `target` — die normalisierte Domain
- `mode` — `subdomains` (Pflicht)
- `country` — `de` Default, sonst nach `meta.json.region`
- `protocol` — `both` (Default)
- `date` — heute oder leer (Snapshot)

Liefert: `org_keywords`, `org_traffic`, `paid_keywords`, `paid_traffic`, ggf. weitere Aggregate.

**Unit-Kosten**: ca. **50 Units** pauschal pro Aufruf.

### `site-explorer-metrics-history`

Verlauf der Metriken über Zeit.

Wichtige Parameter:
- `target`, `mode`, `country`, `protocol` wie oben
- `date_from` — heute minus 365 Tage
- `date_to` — heute
- `history_grouping` — `monthly` Default (wöchentlich verbraucht deutlich mehr Units)
- `select` — `org_traffic, org_cost, paid_traffic, paid_cost`

Liefert Zeitreihe für jede ausgewählte Spalte.

**Unit-Kosten**: ca. **20 Units pro Datenpunkt** in der Zeitreihe. Bei monatlich = 12 Punkte = ca. 240 Units.

### `site-explorer-domain-rating`

Aktuelles DR plus Ahrefs-Rank.

Wichtige Parameter:
- `target`, `mode`, `protocol` wie oben
- `date` — heute oder leer

Liefert: `domain_rating` (0-100), `ahrefs_rank` (Positionsrang weltweit).

**Unit-Kosten**: ca. **50 Units** pauschal.

### `site-explorer-domain-rating-history`

DR-Verlauf 12 Monate.

Wichtige Parameter:
- `target`, `mode`, `protocol` wie oben
- `date_from` — heute minus 365 Tage
- `date_to` — heute
- `history_grouping` — `monthly`

Liefert Liste `[{date, domain_rating}, …]`.

**Unit-Kosten**: ca. **20 Units pro Datenpunkt** ≈ 240 Units bei monatlicher Auflösung.

### `site-explorer-organic-keywords`

Top-Keywords der Domain mit Intent-Flags.

Wichtige Parameter:
- `target`, `mode`, `country`, `protocol`
- `select` — **immer setzen**: `keyword, volume, keyword_difficulty, best_position, best_position_url, sum_traffic, is_branded, is_transactional, is_commercial, is_informational`
- `order_by` — `sum_traffic:desc` (entspricht Ahrefs-Wichtigkeits-Sortierung)
- `limit` — 100 Default (Skill-Konvention), 200 maximal sinnvoll
- `where` — optional Filter, in diesem Skill **kein Filter** (auch Long-Tail-KWs sind relevant)

Liefert eine Liste Keyword-Datensätze. Intent-Flags sind boolesch (0/1), mehrere Flags pro Keyword sind möglich (z. B. `is_commercial=1` und `is_informational=1` gleichzeitig).

**Unit-Kosten**: ca. **37 Units pro Zeile**. Bei 100 Keywords = 3.700 Units pro Akteur. **Das ist der teuerste Endpoint** — der Skill akzeptiert das, weil Intent-Flags und Volume/KD-Werte den Folge-Skills viel sparen.

### `site-explorer-organic-competitors`

Ahrefs-eigene Wettbewerber-Liste.

Wichtige Parameter:
- `target`, `mode`, `country`, `protocol`
- `select` — **immer setzen**: `competitor_domain, keywords_common, keywords_competitor, domain_rating, traffic`
- `order_by` — `keywords_common:desc` (Wettbewerber mit größtem Keyword-Überlapp zuerst)
- `limit` — 10 Default (analog zu Sistrix `domain.competitors`)

Liefert Top-10 Wettbewerber-Domains pro Akteur mit Overlap-Metrik (`keywords_common`), eigener Domain-Stärke (`keywords_competitor`, `domain_rating`) und Traffic-Schätzung.

**Unit-Kosten**: ca. **14 Units pro Zeile**. Bei 10 = 140 Units pro Akteur.

### `site-explorer-top-pages` (optional)

Top-Pages nach organischem Traffic. Nur abrufen, wenn Restbudget komfortabel ist und `03-15-web-content-inventur` schon eingeplant ist.

Wichtige Parameter:
- `target`, `mode`, `country`, `protocol`
- `select` — `url, sum_traffic, keywords, top_keyword, top_keyword_volume`
- `limit` — 50

**Unit-Kosten**: ca. **25 Units pro Zeile**.

### `subscription-info-limits-and-usage`

Healthcheck — keine Domain nötig.

Liefert: Monats-Budget, verbrauchte Units, Restbudget, Reset-Datum.

**Unit-Kosten**: 0 (Meta-Tool).

## Unit-Verbrauch und Budget-Strategie

Pro Akteur im Voll-Hybrid-Modus (alle Tools, Default-Limits):

| Tool | Units |
|---|---|
| `site-explorer-metrics` | 50 |
| `site-explorer-metrics-history` (12 Monatspunkte × 4 Spalten) | ~240 |
| `site-explorer-domain-rating` | 50 |
| `site-explorer-domain-rating-history` (12 Punkte) | ~240 |
| `site-explorer-organic-keywords` (100 Zeilen) | ~3.700 |
| `site-explorer-organic-competitors` (10 Zeilen) | ~140 |
| **Summe pro Akteur** | **~4.400 Units** |

Bei 10 Akteuren: ca. **44.000 Units pro MTA**. Bei 400.000 Units/Monat passt das für 8-9 vollständige MTAs/Monat ohne Cache-Nutzung.

**Strategie:**

- Vor dem ersten Lauf: `subscription-info-limits-and-usage` aufrufen. Wenn Rest-Budget < geschätzter Verbrauch → Warnung im Schluss-Format, Option zum Abbruch.
- Pro Akteur sequenziell aufrufen (nicht parallel) — MCP-Server-freundlicher und einfacher zu debuggen.
- **14-Tage-Cache** (siehe unten) reduziert Re-Run-Kosten drastisch.
- Bei sehr großen Akteurs-Listen (>15): vorher prüfen, ob `limit` für `organic-keywords` auf 50 reduziert werden sollte.

## Fehler-Behandlung

| MCP-Fehler | Reaktion |
|---|---|
| 401 / 403 | MCP-Auth ungültig — Reduced-Modus aktivieren, Hinweis im Schluss-Format "Ahrefs-MCP-Verbindung prüfen" |
| 429 (Rate-Limit oder Subscription-Limit) | 60s warten, einmal retry. Bei zweitem 429: Skill schreibt bisher erhobene Ahrefs-Daten, markiert Rest als `ahrefs_indexiert: unbekannt`, läuft mit Sistrix-only-Sektion weiter |
| Tool-Fehler "domain not found" / leere Antwort bei `site-explorer-metrics` | `ahrefs_indexiert: false` setzen, weitere Ahrefs-Calls für diesen Akteur überspringen |
| Tool-Fehler bei einzelnem Sub-Endpoint (z. B. `organic-competitors`) | Nur diesen Endpoint als `unbekannt` markieren, andere Daten behalten |
| Netzwerk-Fehler / MCP-Verbindung weg | Reduced-Modus aktivieren, in Frontmatter `quelle.ahrefs.zugang: unterbrochen`, Hinweis im Schluss-Format |
| Leere Antwort / unerwartetes Format | Roh-Antwort in `raw/`-Cache ablegen für Debug, Akteur als `ahrefs_recherche_fehlgeschlagen` markieren |

## Caching-Strategie

Pro Akteur und Endpoint eine JSON-Datei in `audits/raw/`:

```
audits/raw/ahrefs-metrics-<akteurs-slug>.json
audits/raw/ahrefs-metrics-history-<akteurs-slug>.json
audits/raw/ahrefs-domain-rating-<akteurs-slug>.json
audits/raw/ahrefs-domain-rating-history-<akteurs-slug>.json
audits/raw/ahrefs-organic-keywords-<akteurs-slug>.json
audits/raw/ahrefs-organic-competitors-<akteurs-slug>.json
audits/raw/ahrefs-top-pages-<akteurs-slug>.json   # optional
```

Struktur einer einzelnen Datei:

```json
{
  "akteurs_slug": "mustermann",
  "domain": "mustermann.de",
  "endpoint": "organic-keywords",
  "mode": "subdomains",
  "country": "de",
  "abgefragt_am": "2026-05-14T08:00:00Z",
  "ttl_bis": "2026-05-28T08:00:00Z",
  "units_verbraucht_geschaetzt": 3700,
  "response": { ... Ahrefs-Roh-Antwort ... }
}
```

### TTL-Logik (14 Tage)

Vor jedem Tool-Aufruf:

1. Prüfe, ob die entsprechende Cache-Datei existiert
2. Wenn ja: lies `ttl_bis` und vergleiche mit jetzt
3. Wenn Cache noch frisch → nutze gecachte Antwort, **kein** MCP-Call (Unit-Spar)
4. Wenn abgelaufen → MCP-Call, Cache überschreiben mit neuem `ttl_bis = jetzt + 14 Tage`

Begründung 14 Tage: Ahrefs aktualisiert Backlink- und Keyword-Daten typischerweise 1-2× pro Woche. 14 Tage TTL ist ein Kompromiss zwischen Aktualität und Unit-Verbrauch bei Re-Runs.

**Forced Re-Fetch**: wenn der Stratege ausdrücklich frische Daten will, kann der Skill mit `--no-cache` (zukünftige Flag) gestartet werden. Default: Cache nutzen.

## Antwort-Normalisierung auf internes Schema

Folge-Skills (`03-02-seo-keyword-recherche`, `03-03-seo-keyword-kategorisierung`) lesen primär aus den CSVs, nicht aus den raw-JSONs. Damit das funktioniert, normalisiert der Skill die Ahrefs-Spalten beim Übertrag in die CSV:

| Ahrefs-Spalte | CSV-Spalte in `seo-keywords.csv` | CSV-Spalte in `seo-rankings-ahrefs.csv` |
|---|---|---|
| `keyword` | (Match-Key, nicht eigene Spalte) | `keyword` |
| `volume` | `ahrefs_volume` | `ahrefs_volume` |
| `keyword_difficulty` | `ahrefs_kd` | `ahrefs_kd` |
| `best_position` | — | `best_position` |
| `best_position_url` | — | `best_position_url` |
| `sum_traffic` | `ahrefs_sum_traffic` | `ahrefs_sum_traffic` |
| `is_branded` | `intent_branded` (0/1) | `intent_branded` (0/1) |
| `is_transactional` | `intent_transactional` (0/1) | `intent_transactional` (0/1) |
| `is_commercial` | `intent_commercial` (0/1) | `intent_commercial` (0/1) |
| `is_informational` | `intent_informational` (0/1) | `intent_informational` (0/1) |

## Was NICHT in diesen Skill gehört

- **Backlink-Listen** (`site-explorer-all-backlinks`, `site-explorer-referring-domains`) — gehört in einen separaten Backlink-Skill, falls gebaut. Hier nur DR als Aggregat-Metrik.
- **SERP-Overview** (`serp-overview`) — gehört in `03-02-seo-keyword-recherche`.
- **Site Audit** (`site-audit-*`) — gehört in `03-14-web-tech-und-tracking`.
- **Brand Radar** (`brand-radar-*`) — gehört in einen separaten Brand-Tracking-Skill, falls gebaut.
- **Paid Pages** (`site-explorer-paid-pages`) — gehört in `03-05-sea-google-ads-check`.

## Verhältnis zu Sistrix

- Beide Tools werden **nebeneinander** verwendet, nicht statt einander.
- Sistrix bleibt Leit-Datenquelle für den Sichtbarkeitsindex und für DACH-Long-Tail-Keywords (kleine deutsche Domains).
- Ahrefs ergänzt mit DR (Backlink-Stärke), Traffic-Schätzung, Intent-Flags und einer zweiten WB-Liste.
- Bei Daten-Konflikten (Volumen-Diskrepanz, abweichende WB-Listen) generiert der Skill Auffälligkeiten — er entscheidet nicht, welche Quelle "richtig" ist.
