# Ahrefs als Primary-Quelle (plus Sistrix als optionale DACH-Ergänzung)

Seit der vollen Anbindung des Ahrefs-MCP (400.000 Units/Monat) ist **Ahrefs die Primärquelle** für diesen Skill — für Long-Tail-Expansion, Keyword-Difficulty, Volumen, CPC, Intent-Klassifikation und Parent-Topic-Cluster. Sistrix ist optional und liefert eine **DACH-Long-Tail-Ergänzung** plus **Volumen-Cross-Validierung**.

Die alte "Sistrix-First-Strategy" ist damit umgekehrt.

## Zugangs-Reihenfolge

### Ahrefs (Pflicht)

1. **MCP-Tools prüfen** — alle relevanten Tools haben den Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__`. Tool-Discovery via Verfügbarkeits-Check vor dem ersten Lookup.
2. **Healthcheck** vor dem ersten Bulk-Aufruf: `mcp__1d9710a6-f270-4555-88f8-e4367948d936__subscription-info-limits-and-usage` (zeigt verbleibendes Unit-Budget) **oder** ein minimaler 1-Keyword-`keywords-explorer-overview`-Call.
3. **Wenn nicht verbunden oder Healthcheck fehlschlägt → Skill-Abbruch.** Anders als früher kein "Reduced-Modus ohne Ahrefs" — Ahrefs ist seit der MCP-Anbindung Pflicht.

Über das MCP gibt es keinen API-Key-Hinweis im Skill-Code. Authentifizierung läuft transparent über die MCP-Verbindung.

### Sistrix (optional)

1. Prüfen wie in `03-01-seo-sichtbarkeit-und-rankings/reference/sistrix-api-nutzung.md`
2. Wenn verfügbar: `sistrix_modus: voll`, alle Sistrix-Endpoints nutzbar
3. Wenn nicht verfügbar: `sistrix_modus: aus`, Skill läuft trotzdem voll — nur ohne DACH-Long-Tail-Ergänzung und ohne Volumen-Cross-Check

## Ahrefs-Tool-Mapping

Alle Tool-Namen mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__`.

### 1. `keywords-explorer-overview` (zentraler Anreicherungs-Endpoint)

Liefert pro Keyword alle relevanten Metriken in einem Call.

**Wichtige `select`-Felder:**

- `keyword`
- `volume` — Suchvolumen
- `keyword_difficulty` (0–100)
- `cpc` — durchschnittlicher CPC
- `traffic_potential`
- `is_branded` — Boolean, Ahrefs-Erkennung Markenbezug
- `is_transactional` — Boolean
- `is_commercial` — Boolean
- `is_informational` — Boolean
- `parent_keyword` — Ahrefs-Parent-Topic-Cluster
- `intents` — strukturierte Intent-Auflistung
- `country`

**Bei Spalten-Drift** (Ahrefs ändert Feldnamen): Skill übernimmt die Namen aus der Fehlermeldung und wiederholt den Request einmal. Bei zweitem Fehlschlag → Batch als fehlgeschlagen markieren, Lauf weiter.

**Batching:**

- **Bis 1000 Keywords pro Request** möglich (anders als früher angenommen 50-100)
- Country aus `meta.json.region` ableiten, Default `de`
- Pro Batch eine Cache-Datei: `audits/raw/ahrefs-overview-batch-<n>.json`

**Verwendung:**

- Vollanreicherung in SKILL.md Schritt 8 (Difficulty + Volumen + Intent-Flags + Parent-Topic)
- Branchen-Seed-Validierung in Schritt 7 (statt früher Sistrix `keyword.overview`)

### 2. `keywords-explorer-matching-terms`

Long-Tail-Variationen, die das Seed-Keyword als Phrase enthalten. **Primary für Phrase-Match-Long-Tail.**

Wichtige Parameter:

- `keywords: <seed>`
- `country: <code>` (aus `meta.json.region`)
- `volume_from: 50` (Min-Volumen-Filter)
- `match_mode: phrase_match`
- `limit: 50` (Default für diesen Skill)

Cache: `audits/raw/ahrefs-matching-terms-<seed-slug>.json`

### 3. `keywords-explorer-related-terms`

Thematisch verwandte Keywords (eigene Cluster-Achse, breiter als matching-terms). **Primary für thematische Expansion.**

- `keywords: <seed>`
- `country: <code>`
- `volume_from: 50`
- `limit: 30`

Cache: `audits/raw/ahrefs-related-terms-<seed-slug>.json`

### 4. `keywords-explorer-search-suggestions`

Auto-Suggest-Variationen (Google-Suggest-basiert, W-Fragen, natürliche Long-Tail-Phrasen). **Primary für W-Fragen.**

- `keywords: <seed>`
- `country: <code>`
- `limit: 30`

Cache: `audits/raw/ahrefs-search-suggestions-<seed-slug>.json`

### 5. `keywords-explorer-volume-by-country` (optional)

Für internationale Domains, wenn der Kunde mehrere Länder bedient. Default: nicht aufrufen.

### 6. `keywords-explorer-volume-history` (optional)

Volumen-Trend, saisonale Schwankungen. Default: nicht aufrufen — für die MTA reicht der aktuelle Stand, Trend-Analyse ist Strategen-Special-Auftrag.

### 7. `subscription-info-limits-and-usage` (Healthcheck)

Vor Bulk-Läufen einmal aufrufen, um das verbleibende Unit-Budget zu kennen.

### Nicht in diesem Skill

- `site-explorer-organic-keywords` — wird schon im vorherigen Skill `03-01-seo-sichtbarkeit-und-rankings` genutzt. Hier nicht erneut aufrufen, sondern aus `audits/seo-keywords.csv` lesen.

## Credit-/Unit-Strategie

Bei **400.000 Units/Monat** und typischer MTA-Größe (1 Hauptkunde + 3-7 Wettbewerber, 1-2 Läufe pro Monat) ist das Budget großzügig dimensioniert.

### Grobe Unit-Kosten

| Endpoint | Units pro Request | Anmerkung |
|---|---|---|
| `keywords-explorer-overview` (1 Keyword) | ~1 | sehr günstig |
| `keywords-explorer-overview` (1000 Keywords gebatcht) | ~1 Request mit 1000 Rows | maximale Effizienz |
| `keywords-explorer-matching-terms` (Limit 50) | ~10-30 | pro Seed |
| `keywords-explorer-related-terms` (Limit 30) | ~10-30 | pro Seed |
| `keywords-explorer-search-suggestions` (Limit 30) | ~10-30 | pro Seed |
| `subscription-info-limits-and-usage` | 0 | kostenfrei |

### Beispielrechnung für einen MTA-Lauf

- Long-Tail-Expansion: ~50 Seeds × 3 Endpoints × ~20 Units = ~3.000 Units
- Vollanreicherung: 800 Keywords / 1000 pro Batch = 1 Request mit ~800 Rows ≈ 800 Units
- Branchen-Seed-Validierung: gebatcht in einem `overview`-Call mit den restlichen Anreicherungs-Keywords → marginale Mehrkosten
- **Gesamt pro MTA-Lauf: ~4.000 Units** (unter 1% des Monatsbudgets)

→ Caps können großzügig sein: SKILL.md setzt `longtail_cap: 500` und `anreicherung_cap: 800` als Defaults, beide via Override anpassbar.

### Strategie für Bulk-Anreicherung (Schritt 8)

1. Pre-Filter nach Priorität (siehe SKILL.md Schritt 8 Tabelle)
2. Sortierte Keyword-Liste in Batches von 1000 zerlegen
3. Pro Batch ein `keywords-explorer-overview`-Call mit allen relevanten `select`-Feldern
4. Roh-JSON in `audits/raw/ahrefs-overview-batch-<n>.json` cachen
5. Bei Re-Runs mit Override `nur Ahrefs nachziehen`: Cache-Dateien lesen, älter als 14 Tage → neu ziehen, sonst Cache nutzen
6. Bei 429: 30s warten, einmal retry. Bei zweitem 429: bisher gezogene Daten schreiben, Schluss-Format mit Hinweis.

## Fehler-Behandlung

| Fehler | Reaktion |
|---|---|
| Ahrefs-MCP nicht verbunden | **Skill-Abbruch** vor Schritt 2 — Ahrefs ist Pflicht |
| Ahrefs Auth-Fehler im Healthcheck | **Skill-Abbruch** |
| Ahrefs 429 (Rate-Limit) während Bulk | 30s warten, einmal retry. Bei zweitem 429: bisher gezogene Daten behalten, Lauf abschließen, Hinweis im Schluss-Format |
| Ahrefs 5xx | 30s warten, einmal retry, dann Batch als fehlgeschlagen markieren und mit nächstem weitermachen |
| Ahrefs Spalten-Drift (Feld umbenannt) | Spalten aus Fehlermeldung übernehmen, einmal retry. Bei zweitem Fehler: Batch markieren |
| Ahrefs leere Antwort für ein Keyword | Im Pool `ahrefs_volumen: null`, `difficulty: null` etc. lassen — kein Fehler |
| Sistrix 401 / 403 | `sistrix_modus: aus`, Skill läuft weiter ohne Cross-Validierung |
| Sistrix 429 | 30-60s warten, einmal retry, dann Sistrix-Schritt als partiell markieren |
| Sistrix 404 (Keyword unbekannt) | `sistrix_volumen: null` für die Zeile |

## Roh-Daten-Caching

Pro Pool-Lauf:

- `audits/raw/ahrefs-overview-batch-<n>.json` — pro Ahrefs-Batch eine Datei (Hauptanreicherung)
- `audits/raw/ahrefs-matching-terms-<seed-slug>.json`
- `audits/raw/ahrefs-related-terms-<seed-slug>.json`
- `audits/raw/ahrefs-search-suggestions-<seed-slug>.json`
- `audits/raw/sistrix-keyword-related-<seed-slug>.json` (nur wenn `sistrix_modus != aus`)
- `audits/raw/sistrix-keyword-suggestions-<seed-slug>.json` (nur wenn Sistrix verfügbar)
- `audits/raw/sistrix-keyword-overview-<keyword-hash>.json` (nur bei Sistrix-Einzel-Lookups, optional)

Bei Re-Runs werden Cache-Dateien gelesen und auf Aktualität geprüft (älter als 14 Tage → neu ziehen, sonst Cache nutzen).

## MCP-Spezifikum

- Tool-Discovery: Skill prüft Verfügbarkeit von `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-*` und `mcp__1d9710a6-f270-4555-88f8-e4367948d936__subscription-info-limits-and-usage`
- Bei MCP-Tool-Versionsdrift (z. B. ein Endpoint fehlt): in `raw/`-Cache pro Eintrag dokumentieren, welcher Tool-Name genutzt wurde
- Kein API-Key-Hinweis nötig — MCP-Auth ist transparent

## Sistrix als optionale DACH-Ergänzung

Sistrix bleibt **wertvoll für DACH-spezifischen Long-Tail** und als **Cross-Validierungs-Quelle** für Volumen.

### Wann Sistrix mitziehen

1. **DACH-Long-Tail in Schritt 5b** — Sistrix `keyword.related` und `keyword.suggestions` als Ergänzung zu Ahrefs (deckt deutschsprachige Long-Tail-Phrasen ab, die Ahrefs nicht kennt)
2. **Volumen-Cross-Validierung** — wenn Sistrix-Volumen verfügbar ist, wird es in der CSV neben Ahrefs-Volumen geführt. Bei >50% Abweichung: `volumen_diskrepanz: true`.

### Sistrix-Endpoints (nur wenn `sistrix_modus != aus`)

#### `keyword.related`

```
GET https://api.sistrix.com/keyword.related
?api_key=<KEY>&kw=<keyword>&country=de&limit=100&format=json
```

Liefert verwandte Keywords mit Suchvolumen. DACH-Long-Tail-Ergänzung in Schritt 5b.

#### `keyword.suggestions`

```
GET https://api.sistrix.com/keyword.suggestions
?api_key=<KEY>&kw=<keyword>&country=de&format=json
```

Auto-Suggest-Variationen. Im Skill: aufrufen, wenn `keyword.related` weniger als 30 Treffer liefert.

#### `keyword.overview` (optional, nur bei Sistrix-Einzel-Lookups)

```
GET https://api.sistrix.com/keyword.overview
?api_key=<KEY>&kw=<keyword>&country=de&format=json
```

Wird im neuen Workflow seltener genutzt — die Branchen-Seed-Validierung (alter Schritt 7) läuft jetzt primär über Ahrefs `keywords-explorer-overview` (gebatcht, günstiger). Sistrix-`keyword.overview` nur als Cross-Check bei strittigen Branchen-Seeds.

### Sistrix-Credits

Sistrix-Keyword-Endpoints sind günstiger als die Domain-Endpoints. Pro Long-Tail-Seed:

- `keyword.related` (Limit 100): 2-3 Credits
- `keyword.suggestions`: 1-2 Credits
- `keyword.overview`: 1 Credit

Bei 20 Top-Kunden-Keywords + 20 Top-Gap-Keywords als Seeds → 40 Seeds × ca. 2 Credits = 80 Credits. Für die meisten REACHX-Accounts unproblematisch.

## Was NICHT in diesen Skill gehört

- **Manuelle Kuration und Cluster** — gehört in `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf)
- **Content-Tiefen-Analyse** — `03-15-web-content-inventur`
- **Ads-Keyword-Listen** (Google Ads / Meta Ads) — separater Bezug in den Ads-Skills, nicht hier
- **Volumen-Trend-Analyse** (saisonale Schwankungen) — für die MTA reicht der aktuelle Stand, Trend-Analyse ist Strategen-Special-Auftrag
