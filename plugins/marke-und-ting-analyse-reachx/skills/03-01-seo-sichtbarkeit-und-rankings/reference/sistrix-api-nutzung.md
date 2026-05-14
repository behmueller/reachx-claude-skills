# Sistrix-API-Nutzung

Wie der Skill Sistrix anspricht — über MCP wenn verfügbar, sonst über HTTP-API mit `SISTRIX_API_KEY`. Plus die Liste der relevanten Endpoints, Parameter-Defaults und Fehler-Behandlung.

## Zugangs-Reihenfolge (Skill-Logik)

1. **MCP-Tools prüfen** — falls eine Sistrix-MCP-Integration verbunden ist (z. B. `mcp__sistrix__*`), diese bevorzugen. Vorteile: strukturierte Ergebnisse, kein Token-Handling, kein eigenes Caching-Layer nötig.
2. **HTTP-API mit Token** — wenn kein MCP vorhanden: `SISTRIX_API_KEY` aus dem Environment lesen, gegen `https://api.sistrix.com/` requesten.
3. **Beides fehlt** → Skill-Abbruch mit konkreter Anleitung, wie der Zugang einzurichten ist (Verweis auf REACHX-Onboarding-Doku, falls vorhanden — sonst Generic-Hinweis).

In allen Fällen: vor dem ersten Domain-Lookup einen kleinen Healthcheck (z. B. Account-Info-Endpoint), um schnell zu sehen ob Auth funktioniert.

## Domain-Normalisierung

Vor jeder Sistrix-Abfrage die Domain normalisieren — sonst gibt es Duplikate und falsche Hits:

1. URL parsen, nur Host extrahieren
2. `www.`-Präfix entfernen
3. Trailing-Slash und Path verwerfen
4. Lowercase
5. Punycode bleibt Punycode (Sistrix erwartet das)
6. Subdomain-Erhaltung: wenn der Akteur explizit auf einer Subdomain operiert (`shop.beispiel.de`), die Subdomain behalten — sonst auf Apex-Domain reduzieren

Beispiele:

| Input | Sistrix-Domain |
|---|---|
| `https://www.beispiel.de/` | `beispiel.de` |
| `https://shop.beispiel.de/produkte` | `shop.beispiel.de` |
| `https://Beispiel.DE` | `beispiel.de` |
| `https://www.beispiel.co.uk/` | `beispiel.co.uk` |
| `xn--mller-kva.de` (Punycode für "müller.de") | `xn--mller-kva.de` |

Bei Mehrfach-Domain-Konflikt (z. B. Kunde hat `beispiel.de` und `beispiel.com` als gleichwertige Hauptdomains): nur die in `meta.json.website` genannte Domain abfragen. Stratege kann via expliziten Override mehrere abfragen lassen.

## Relevante Endpoints

Pro Endpoint: was er liefert, welche Parameter wichtig sind, ungefährer Credit-Verbrauch (Sistrix rechnet in Credits — relevant für Rate-Limit-Strategie).

### `domain.overview`

Visibility-Index der Domain, aktueller Wert plus Basis-Statistiken.

```
GET https://api.sistrix.com/domain.overview
?api_key=<KEY>
&domain=<domain>
&country=de
&format=json
&mobile=false
```

Wichtige Parameter:

- `country` — Standard `de`. Bei DACH-Kunden ggf. `at`, `ch`. Bei internationalen Kunden: `us`, `uk`, `fr`, `es`, `it`, `pl` (Sistrix-Coverage prüfen, manche Länder weniger gut)
- `mobile` — `false` (Default) für Desktop-VI. `true` für Mobile-VI. Standard im Skill: nur Desktop, Mobile optional bei B2C-Branchen.

Liefert mindestens: aktueller VI, geschätzte monatliche organische Besuche, Anzahl rankender Keywords gesamt.

### `domain.sichtbarkeitsindex.verlauf` (oder `domain.history` / `domain.visibilityindex.history` je nach Sistrix-API-Version)

12-Monats-Verlauf des VI.

```
GET https://api.sistrix.com/domain.sichtbarkeitsindex.verlauf
?api_key=<KEY>
&domain=<domain>
&country=de
&history_days=365
&format=json
```

Liefert Liste `[{date: ISO, sichtbarkeitsindex: float}, …]`. Bei Domains ohne Historie (z. B. zu jung): leere Liste, im Skill als `verlauf: []` ablegen, Auffälligkeit `domain_zu_jung` vergeben.

### `domain.kwcount` und `domain.kw`

Keyword-Anzahl plus die Keywords selbst.

```
GET https://api.sistrix.com/domain.kw
?api_key=<KEY>
&domain=<domain>
&country=de
&limit=200
&order_by=visibilityindex_desc
&format=json
```

Wichtige Parameter:

- `limit` — Skill nutzt 200 als Default-Top-N. Sistrix liefert bei diesem Endpoint die wichtigsten Keywords nach VI-Gewicht. Bei sehr großen Domains (10k+ rankende KWs) ist 200 ein vernünftiger Cap.
- `order_by` — `visibilityindex_desc` priorisiert nach VI-Gewicht (Suchvolumen × Position-Wert). Alternative: `searchvolume_desc` für Suchvolumen-Priorisierung — kann bei sehr großen Sites zu Generic-Keyword-Bias führen.
- `position_to` — Filter auf Top-30 oder Top-100 Position möglich. Default im Skill: kein Filter, weil auch Position 30-50 Insights bringen kann (Long-Tail-Chancen).

Pro Keyword im Result: `keyword`, `position`, `searchvolume`, `url` (ranking-URL), ggf. `competition` (CPC-basierte Konkurrenz), ggf. `kwid` (Sistrix-interne Keyword-ID).

**Difficulty** ist in der Standard-Sistrix-API nicht enthalten — der Folge-Skill `03-02-seo-keyword-recherche` zieht Difficulty bei Bedarf aus Ahrefs.

### `domain.competitors`

Sistrix-vorgeschlagene Wettbewerber-Domains basierend auf Keyword-Overlap.

```
GET https://api.sistrix.com/domain.competitors.seo
?api_key=<KEY>
&domain=<domain>
&country=de
&limit=10
&format=json
```

Liefert Top-N Domains mit größtem Keyword-Overlap. Pro Treffer: Domain, eigener VI, Overlap-Score (z. B. "wie viele Keywords gemeinsam"). Im Skill genutzt für die Auffälligkeit `sistrix_wb_nicht_in_liste`.

### `domain.url.top`

Optional — Top-rankende URLs der Domain. Hilfreich für die Content-Inventur-Vorbereitung. Im SEO-Sichtbarkeits-Skill nicht zwingend, aber wenn der Credit-Verbrauch okay ist, mitschicken und in `raw/`-Cache ablegen.

## Credit-Verbrauch und Rate-Limit-Strategie

Sistrix-API ist Credit-basiert. Grobe Schätzungen:

| Endpoint | Credits pro Aufruf |
|---|---|
| `domain.overview` | 1 |
| `domain.history` / `verlauf` | 1-2 |
| `domain.kw` (Limit 200) | 5-10 |
| `domain.competitors.seo` | 1 |

Pro Domain: ca. 8-15 Credits. Bei 10 Akteuren: ca. 100-150 Credits.

**Strategie:**

- Vor dem ersten Lauf: Account-Quota lesen (`credits.budget` oder ähnlich), prüfen ob ausreichend
- Pro Domain sequenziell aufrufen (nicht parallel) — vermeidet Bursts
- Zwischen Domains keine harten Pausen nötig (Sistrix hat Throttling, aber sehr großzügig)
- Bei 429: 60 Sekunden warten, einmal retry. Bei zweitem 429: Skill schreibt bisher erhobene Daten, markiert Rest als offen, Hinweis im Schluss-Format

## Fehler-Behandlung

| HTTP-Status / Fehler | Reaktion |
|---|---|
| 401 / 403 | Token ungültig — Skill-Abbruch mit Hinweis "SISTRIX_API_KEY prüfen" |
| 404 (Domain nicht gefunden) | Sistrix kennt die Domain nicht — `sistrix_indexiert: false`, weiter mit nächster Domain |
| 429 (Rate-Limit) | 60s warten, einmal retry, dann sauber abbrechen |
| 5xx | 30s warten, einmal retry, dann Domain als `recherche_fehlgeschlagen` markieren und weiter mit nächster |
| Netzwerk-Fehler | wie 5xx |
| Leere Antwort / unerwartetes Format | Domain als `recherche_fehlgeschlagen` markieren, Roh-Antwort in `raw/`-Ordner für Debug ablegen |

## Roh-Daten-Caching

Pro Domain die JSON-Antworten der Endpoints in `audits/raw/sistrix-<akteurs-slug>.json` ablegen. Struktur:

```json
{
  "akteurs_slug": "mustermann",
  "domain": "mustermann.de",
  "country": "de",
  "abgefragt_am": "2026-05-13T08:00:00Z",
  "overview": {...sistrix-roh-antwort...},
  "verlauf": [...],
  "competitors": [...],
  "keywords": [...]
}
```

Vorteil:

- Folge-Skills (`03-02-seo-keyword-recherche`) können daraus lesen ohne erneute API-Calls
- Reproduzierbarkeit: bei späterer Frage "wie war das damals?" lässt sich die Roh-Antwort prüfen
- Bei Re-Run mit aktivem Caching-Flag (zukünftige Erweiterung): API-Calls überspringen

**Wichtig:** Roh-Daten sind großzügig dimensioniert — 10 Akteure × Mehrere-MB-pro-JSON-möglich. Bei Disk-Knappheit Hinweis im Schluss-Format.

## MCP-Nutzung (falls verbunden)

Wenn Sistrix-MCP-Tools vorhanden sind, der Skill versucht:

1. **Tool-Inventur**: Welche `mcp__sistrix__*`-Tools sind verfügbar?
2. **Mapping** der API-Endpoints auf MCP-Tool-Namen:
   - `domain.overview` → meist `mcp__sistrix__domain_overview` oder ähnlich
   - `domain.kw` → `mcp__sistrix__domain_keywords`
   - `domain.competitors.seo` → `mcp__sistrix__domain_competitors`
   - (Namen variieren je nach MCP-Implementierung)
3. **Sequenzielle MCP-Aufrufe** statt HTTP-Calls
4. **Antwort-Normalisierung** auf dasselbe interne Schema wie bei HTTP — Folge-Skills müssen sich nicht um die Quelle kümmern

Wenn MCP nur einen Teil der Endpoints abdeckt: hybrid betreiben — fehlende Endpoints über HTTP-API, vorhandene über MCP. In `raw/<slug>.json` pro Endpoint die Quelle dokumentieren (`source: "mcp"` oder `source: "http"`).

## Was NICHT in diesen Skill gehört

- **Difficulty-Werte aus Drittanbieter-Tools** (Ahrefs, Semrush) — gehört in `03-02-seo-keyword-recherche`
- **Content-Tiefen-Analyse** — gehört in `03-15-web-content-inventur`
- **Backlink-Profile** — gehört in einen separaten Skill, wenn er gebaut wird (steht aktuell nicht im Plan)
- **Manuelles Keyword-Tagging / Cluster** — gehört in `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf)
