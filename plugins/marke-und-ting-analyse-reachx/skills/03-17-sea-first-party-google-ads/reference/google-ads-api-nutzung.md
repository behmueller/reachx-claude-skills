# Google-Ads-API-Nutzung

Wie der Skill First-Party-Google-Ads-Daten beschafft. Eine einzige Datenquelle:

- **`google-ads.py`-CLI-Wrapper** (`${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py`) — wrappt die offizielle `google-ads`-Python-Library in eine zustandslose CLI mit JSON-Output, analog zu `drive.py`. Jeder Aufruf lädt die Credentials, führt eine GAQL-Query aus, schreibt JSON nach stdout.

Kein MCP, kein Fallback-Pfad. Wenn der Wrapper nicht einsatzbereit ist → freundlicher Skip (siehe `SKILL.md` Schritt 1), KEIN Abbruch des MTA-Workflows.

**Abgrenzung:** Dieser Wrapper liefert das **echte eigene Kundenkonto** unter dem REACHX-MCC. `03-05-sea-google-ads-check` nutzt stattdessen das öffentliche Google Ads Transparency Center und sieht nur die Anzeigen der Wettbewerber von außen — ohne Spend, Klicks, Conversions.

## Zugangs-Reihenfolge

1. **Wrapper-Datei prüfen** — `${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py` existiert.
2. **Library prüfen** — `google-ads`-Python-Library installiert (`pip3 install -r ${CLAUDE_PLUGIN_ROOT}/scripts/requirements-google.txt`). Der Wrapper meldet eine fehlende Library selbst mit klarer Anleitung.
3. **Credentials prüfen** — `~/.config/reachx-mta/google-credentials.yaml` existiert (oder der via `REACHX_GOOGLE_CREDENTIALS` gesetzte Pfad).
4. **Probe-Call** — `python3 google-ads.py list-accounts`. Liefert er eine Konto-Liste → einsatzbereit. Schlägt er fehl → Skip mit der jeweiligen Fehlermeldung.

## Auth-Setup (einmalig pro Mac)

Der Wrapper liest seine Zugangsdaten aus einer YAML-Datei. Pflichtfelder:

```yaml
# ~/.config/reachx-mta/google-credentials.yaml  (chmod 600 — NIEMALS ins Repo committen)
developer_token: "<Google-Ads-API-Developer-Token>"
client_id: "<OAuth-Client-ID>"
client_secret: "<OAuth-Client-Secret>"
refresh_token: "<langlebiges-Refresh-Token>"
login_customer_id: "<REACHX-MCC-ID, 10-stellig, ohne Bindestriche>"
```

- `developer_token` — aus dem Google-Ads-API-Center des MCC. Basic Access reicht für die MTA-Pulls.
- `client_id` / `client_secret` — aus einem OAuth-Desktop-Client in der Google Cloud Console.
- `refresh_token` — einmalig erzeugen via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/google-oauth.py` (OAuth-Browser-Flow, gibt den `refresh_token` aus). In die YAML eintragen.
- `login_customer_id` — die Manager-Account-ID (MCC), unter dem die ~70 Kundenkonten hängen. Ohne dieses Feld scheitert `list-accounts` mit klarer Meldung.

**Sicherheit:** Die YAML mit `chmod 600` schützen. Pfad überschreibbar via Environment-Variable `REACHX_GOOGLE_CREDENTIALS`. Die Datei darf nie ins Git-Repo gelangen.

**Token-Storage:** Es gibt keinen MCP und keine Keychain — die Credentials liegen als Datei. Das `refresh_token` ist langlebig; bei Revoke (Passwort-Wechsel, Account-Entzug) neu erzeugen.

## Wrapper-Befehle

Alle Befehle geben JSON nach stdout aus. Listen-Befehle liefern ein Wrapper-Objekt `{"customer_id", "currency", "range", "count", "rows": [...]}`.

| Befehl | Zweck | Range-Parameter |
|---|---|---|
| `list-accounts` | Alle Kundenkonten (Level ≤ 1) unter dem MCC | — |
| `account-overview <cid>` | Account-Aggregat (eine Zeile) für den Zeitraum | `--range` |
| `campaign-performance <cid>` | Performance je Kampagne, nach Kosten absteigend | `--range` |
| `search-terms <cid>` | Search-Terms-Report — echte Suchanfragen | `--range`, `--limit` |
| `keyword-performance <cid>` | Keyword-Performance inkl. Quality Score | `--range`, `--limit` |
| `conversion-actions <cid>` | Conversion-Tracking-Setup (alle definierten Actions) | — |
| `run-gaql <cid> "<GAQL>"` | Roh-GAQL für Sonderfälle, Rows als verschachteltes Dict | — |

`<cid>` = `customer_id`, 10-stellig. Bindestriche und Whitespace werden vom Wrapper toleriert (`_clean_cid()` zieht reine Ziffern).

### `list-accounts`

```bash
python3 google-ads.py list-accounts
```

Liefert eine flache Liste (kein Wrapper-Objekt). Pro Konto:

```json
{
  "customer_id": "1234567890",
  "name": "Mustermann GmbH - Search",
  "currency": "EUR",
  "is_manager": false,
  "status": "ENABLED",
  "level": 1
}
```

- `status` — `ENABLED`, `CANCELED`, `SUSPENDED`, `CLOSED`. Auch gekündigte Konten erscheinen hier.
- `is_manager` — `true` bei Unter-MCCs (Manager-Konten). Diese sind **keine** operativen Werbekonten und beim Matching auszuschließen.
- `level` — Hierarchie-Ebene unter dem MCC (0 = MCC selbst, 1 = direkt darunter).

### `account-overview`

```bash
python3 google-ads.py account-overview 1234567890 --range 2025-05-17:2026-05-17
python3 google-ads.py account-overview 1234567890 --range LAST_30_DAYS
```

```json
{
  "customer_id": "1234567890",
  "name": "Mustermann GmbH - Search",
  "currency": "EUR",
  "range": "2025-05-17:2026-05-17",
  "cost": 48210.55,
  "impressions": 1820400,
  "clicks": 41200,
  "conversions": 612.0,
  "conversions_value": 184300.0,
  "ctr": 0.0226,
  "avg_cpc": 1.17
}
```

Bei leerem Zeitraum: `{"customer_id": ..., "range": ..., "note": "Keine Daten fuer den Zeitraum."}`.

### `campaign-performance`

```bash
python3 google-ads.py campaign-performance 1234567890 --range 2025-05-17:2026-05-17
```

Wrapper-Objekt, `rows` je Kampagne (nach `cost` absteigend):

```json
{
  "campaign_id": "987654321",
  "campaign": "Search - Brand DE",
  "status": "ENABLED",
  "channel_type": "SEARCH",
  "cost": 12400.30,
  "impressions": 210400,
  "clicks": 9800,
  "conversions": 240.0,
  "conversions_value": 96200.0,
  "ctr": 0.0466,
  "avg_cpc": 1.27
}
```

- `channel_type` — `SEARCH`, `DISPLAY`, `VIDEO`, `SHOPPING`, `DEMAND_GEN`, `PERFORMANCE_MAX`, `MULTI_CHANNEL`, `LOCAL`, `SMART`, `UNKNOWN`.
- `status` — `ENABLED`, `PAUSED`, `REMOVED`.

### `search-terms`

```bash
python3 google-ads.py search-terms 1234567890 --range 2025-05-17:2026-05-17 --limit 300
```

Wrapper-Objekt, `rows` je Suchbegriff (nach `impressions` absteigend):

```json
{
  "search_term": "kabel messer kaufen",
  "status": "ADDED",
  "campaign": "Search - Generic Produkte",
  "impressions": 4800,
  "clicks": 142,
  "conversions": 11.0,
  "cost": 168.40,
  "ctr": 0.0296
}
```

- `status` — `ADDED` (Suchbegriff ist als Keyword übernommen), `EXCLUDED` (negativ ausgeschlossen), `ADDED_EXCLUDED`, `NONE` (weder/noch — Kandidaten-Pool), `UNKNOWN`.
- `--limit` — Default 200. Für die MTA 300 setzen, bei großen Konten bis 1.000.

### `keyword-performance`

```bash
python3 google-ads.py keyword-performance 1234567890 --range 2025-05-17:2026-05-17 --limit 300
```

Wrapper-Objekt, `rows` je Keyword (nach `impressions` absteigend):

```json
{
  "keyword": "kabel messer",
  "match_type": "PHRASE",
  "quality_score": 6,
  "campaign": "Search - Generic Produkte",
  "impressions": 5200,
  "clicks": 160,
  "conversions": 12.0,
  "cost": 188.20,
  "avg_cpc": 1.18
}
```

- `match_type` — `EXACT`, `PHRASE`, `BROAD`.
- `quality_score` — Integer 1-10 oder `null`, wenn Google für das Keyword keinen QS vergeben hat (zu wenig Impressionen). `null` beim Aggregieren nicht als 0 werten — aus der Verteilung ausnehmen.

### `conversion-actions`

```bash
python3 google-ads.py conversion-actions 1234567890
```

Objekt `{"customer_id", "count", "rows": [...]}`, `rows` je Conversion-Action:

```json
{
  "id": "445566",
  "name": "Kontaktformular abgeschickt",
  "status": "ENABLED",
  "type": "WEBPAGE",
  "category": "SUBMIT_LEAD_FORM",
  "counting_type": "ONE_PER_CLICK",
  "primary_for_goal": true
}
```

- `status` — `ENABLED`, `REMOVED`, `HIDDEN`.
- `type` — u. a. `WEBPAGE`, `WEBSITE_CALL`, `UPLOAD_CLICKS`, `UPLOAD_CALLS`, `GOOGLE_ANALYTICS_4_CUSTOM`, `GOOGLE_ANALYTICS_4_PURCHASE`, `STORE_VISITS`, `AD_CALL`. Die `GOOGLE_ANALYTICS_4_*`-Typen kennzeichnen aus GA4 importierte Conversions.
- `category` — u. a. `PURCHASE`, `LEAD`, `SUBMIT_LEAD_FORM`, `CONTACT`, `SIGNUP`, `PAGE_VIEW`, `DOWNLOAD`, `BOOK_APPOINTMENT`, `REQUEST_QUOTE`, `DEFAULT`.
- `counting_type` — `ONE_PER_CLICK` (Lead-Logik) oder `MANY_PER_CLICK` (E-Commerce-Logik).
- `primary_for_goal` — `true`, wenn die Action in die Haupt-Zielmessung (Gebotsstrategie) einfließt.

### `run-gaql`

```bash
python3 google-ads.py run-gaql 1234567890 "SELECT campaign.name, metrics.clicks FROM campaign WHERE segments.date DURING LAST_7_DAYS"
```

Liefert eine flache Liste der Rows als verschachtelte Dicts (`MessageToDict`, `preserving_proto_field_name`). Nur für Sonderfälle — etwa Datums-Segmentierung bei sehr großen Konten oder Felder, die die Standard-Befehle nicht abdecken (z. B. Ad-Group-Ebene, segmentierte Conversion-Werte je Action).

## `--range`-Format

`--range` baut die GAQL-`WHERE`-Datums-Bedingung. Zwei Formen:

1. **GAQL-Datums-Literal** — `segments.date DURING <literal>`. Unterstützt:
   `TODAY`, `YESTERDAY`, `LAST_7_DAYS`, `LAST_14_DAYS`, `LAST_30_DAYS`, `LAST_BUSINESS_WEEK`, `LAST_WEEK_MON_SUN`, `LAST_WEEK_SUN_SAT`, `THIS_MONTH`, `LAST_MONTH`, `ALL_TIME`, `THIS_WEEK_MON_TODAY`, `THIS_WEEK_SUN_TODAY`.
2. **Expliziter Bereich** — `YYYY-MM-DD:YYYY-MM-DD` → `segments.date BETWEEN '<start>' AND '<end>'`.

Default ohne `--range`: `LAST_30_DAYS`.

**Für die MTA:** Es gibt kein 12-Monats-Literal — der 12-Monats-Range muss als expliziter Bereich übergeben werden:

```bash
START=$(date -v-365d +%Y-%m-%d)   # macOS
END=$(date +%Y-%m-%d)
python3 google-ads.py account-overview "$CID" --range "$START:$END"
```

Der Skill nutzt zwei Standard-Ranges (siehe `SKILL.md` Schritt 3): den 12-Monats-Bereich (`<heute-365>:<heute>`) und `LAST_30_DAYS`.

## Micros und Währung

`cost_micros` und `average_cpc` kommen von der Google-Ads-API in **Micros** — 1 Währungs-Einheit = 1.000.000 Micros. **Der Wrapper teilt diese beiden Felder bereits durch 1.000.000** (`_eur()`): die `cost`- und `avg_cpc`-Felder im JSON-Output sind dadurch in Konto-Währungs-Einheiten (z. B. EUR), kaufmännisch gerundet auf 2 Nachkommastellen. `conversions_value` und `conversions` sind dagegen **keine Micros-Werte, sondern bereits Dezimalzahlen** — sie werden NICHT durch 1.000.000 geteilt und unverändert (nur auf 2 Nachkommastellen gerundet) übernommen.

**Konsequenz für den Skill:**

- **Geld-Werte unverändert übernehmen.** Keine eigene Micros-Division, keine Rundung mehr.
- Das `currency`-Feld pro Antwort gibt die Konto-Währung (`EUR`, `USD`, `CHF`, ...). Im Output überall mit ausweisen.
- Bei einem Nicht-EUR-Konto: Werte trotzdem unverändert lassen. Eine etwaige Umrechnung in EUR ist Aufgabe der Synthese-Skills (`04-04-forecast-modell`), nicht dieses Audit-Skills.

`ctr` ist ein Dezimalwert 0..1 (0.0226 = 2,26 %). `conversions` und `conversions_value` sind Dezimalzahlen (Conversions können gebrochen sein durch attributions-anteilige Zählung).

## Konto-Matching (`list-accounts` → Kunde)

`meta.json` enthält **keine `customer_id`** — der Skill muss das Konto selbst finden. Vorgehen:

1. **Kundenname normalisieren** — `meta.json.kunde` lowercase, Rechtsform-Suffixe entfernen (`GmbH`, `AG`, `KG`, `GmbH & Co. KG`, `e.K.`, `UG`, `mbH`, `SE`), in Tokens zerlegen. Optional zusätzlich den Host aus `meta.json.website` (ohne `www.`, ohne TLD) als Token-Quelle.
2. **Kontonamen normalisieren** — `name`-Feld jedes Kontos lowercase, in Tokens zerlegen. Suffixe wie `- Search`, `- Brand`, `- PMax` ignorieren.
3. **Token-Overlap** — ein Konto ist ein Treffer, wenn ein signifikanter Kunden-Token (kein generisches Wort) im Kontonamen vorkommt. Beispiel: Kunde "Mustermann GmbH" → Treffer bei `name` "Mustermann GmbH - Search", "mustermann ppc 2024".
4. **Manager-Konten ausschließen** — Treffer mit `is_manager: true` verwerfen (Unter-MCC, kein operatives Werbekonto).
5. **Status-Priorisierung** — bei mehreren Treffern `status: ENABLED` vor `CANCELED`/`SUSPENDED`/`CLOSED` priorisieren.

**Ergebnis-Fälle** (Verhalten in `SKILL.md` Schritt 2.4):

- **Genau ein ENABLED-Treffer** → vorschlagen, Strategen-Bestätigung über den Hauptthread einholen.
- **Mehrere Treffer** → alle listen, beschreibende Rückfrage (warum die Wahl wichtig ist — Alt-Konto verfälscht die Lesart).
- **Nur CANCELED/SUSPENDED-Treffer** → vorschlagen, aber Status klar nennen und nachfragen, ob die Alt-Daten relevant sind.
- **Kein Treffer** → freundlicher Skip, Override `customer_id=<ID>` anbieten.

**Override:** Argument `customer_id=<10-stellige-ID>` umgeht das Matching komplett. Schlägt der erste Datencall mit Permission-Error fehl (Konto nicht unter dem MCC), sauberer Skip.

**Re-Run:** Existiert `audits/sea-first-party.md` bereits, steht die `customer_id` im YAML-Frontmatter (`quelle.customer_id`) — direkt von dort lesen, keine erneute Bestätigung nötig.

## Zeitraum-Defaults

- **12-Monats-Range** (`zeitraum_lang`): `<heute-365>:<heute>` als expliziter Bereich. Basis für alle Performance-Befehle.
- **30-Tage-Snapshot** (`zeitraum_kurz`): `LAST_30_DAYS` als Literal. Aktueller Trend-Vergleich.

`conversion-actions` ist zeitraum-unabhängig (Setup-Abfrage, kein `--range`).

**Daten-Latenz:** Conversions werden teils mit Verzögerung attribuiert (Conversion-Window kann mehrere Tage bis Wochen betragen). Die letzten 1-3 Tage des 12-Monats-Range sind noch nicht final — für eine MTA-Status-Aufnahme unkritisch. `abgefragt_am` im Output vermerken.

## API-Budget

Der Wrapper nutzt die **kostenlose Google-Ads-API**.

- **Quota:** Mit einem Basic-Access-Developer-Token gilt ein Limit von 15.000 Operationen/Tag. Eine `search_stream`-Query zählt unabhängig von der Zeilenzahl als überschaubare Operationszahl.
- **Pro Skill-Lauf:** typisch 8-12 Wrapper-Calls — `list-accounts` (1), `account-overview` ×2, `campaign-performance` ×2, `search-terms` (1), `keyword-performance` (1), `conversion-actions` (1), plus ggf. 1-2 `run-gaql` bei großen Konten. Weit unter dem Tageslimit.
- **Strategie:** Calls sequenziell ausführen, nicht parallel. Bei einem transienten Fehler (5xx, Rate-Limit) 30-60 s warten und einmal retrien.

## Roh-Daten-Caching

Pro Wrapper-Aufruf die Roh-JSON-Antwort in `~/.cache/reachx-mta/<slug>/audits/raw/sea-<befehl>-<range>.json` ablegen:

```
audits/raw/sea-account-overview-12m.json
audits/raw/sea-account-overview-30d.json
audits/raw/sea-campaign-performance-12m.json
audits/raw/sea-campaign-performance-30d.json
audits/raw/sea-search-terms.json
audits/raw/sea-keyword-performance.json
audits/raw/sea-conversion-actions.json
```

Am Ende des Laufs komprimiert nach Drive `assets/raw/`.

Vorteil:
- `03-02-seo-keyword-recherche` und `03-03-seo-keyword-kategorisierung` können die Search-Terms-Roh-Daten lesen, ohne erneute API-Calls
- `03-18-web-analytics-ga4` kann die `conversion-actions`-Roh-Daten für den GA4-vs-Ads-Cross-Check heranziehen
- Reproduzierbarkeit und Debug bei merkwürdigen Werten

## Fehler-Behandlung

Der Wrapper gibt API-Fehler als lesbare Meldung aus (`_explain()` extrahiert die Message aus der `GoogleAdsException`).

| Fehler | Reaktion |
|---|---|
| Wrapper-Datei fehlt | Freundlicher Skip mit Setup-Anleitung (`SKILL.md` Schritt 1) |
| `google-ads`-Library nicht installiert | Wrapper meldet `pip3 install`-Hinweis selbst → Skip mit dieser Anleitung |
| `google-credentials.yaml` fehlt | Wrapper meldet den Pfad und die Pflichtfelder → Skip mit dieser Anleitung |
| `login_customer_id` fehlt in der YAML | `list-accounts` scheitert mit klarer Meldung → Skip |
| Kein passendes Konto unter dem MCC | Freundlicher Skip, Override `customer_id=<ID>` anbieten (`SKILL.md` Schritt 2.4) |
| Permission-Error bei `customer_id`-Override | Konto liegt nicht unter dem MCC → Skip |
| Auth-Fehler / Refresh-Token revoked | Hinweis "Refresh-Token erneuern via `google-oauth.py`", sauberer Skip, `status.md`-Vermerk `geskippt — auth_fehlgeschlagen` |
| Rate-Limit / 5xx (transient) | 30-60 s warten, einmal retry, dann teil-schreiben |
| Leerer Zeitraum (`note`-Feld in der Antwort) | Konto ohne Spend in der Periode → `daten_qualitaet: keine`, minimale Outputs |
| Quality Score überall `null` | QS-Verteilung auslassen, Hinweis im Body, keine `quality_score_schwach`-Auffälligkeit |

## Edge-Cases

- **Sehr großes Konto** (Search-Terms > 1.000 Zeilen) — `--limit` bis 1.000 hochsetzen. Bei noch mehr: `run-gaql` mit Datums-Segmentierung (z. B. quartalsweise `segments.date BETWEEN`-Bereiche) und lokal aggregieren. CSV auf Top-1.000 nach Impressionen kappen, Hinweis im Body.
- **Nicht-EUR-Konto** — `currency`-Feld auswerten, Werte unverändert lassen, Währung im ganzen Output ausweisen. Keine Umrechnung.
- **CANCELED/SUSPENDED-Konto** — der Wrapper liefert oft noch historische Daten. Skill kann auswerten, nennt den `status` im Frontmatter (`konto_status`) und im Konto-Vorschlag.
- **Konto ohne Conversion-Tracking** — `conversion-actions` liefert keine `ENABLED`-Action. `account-overview` zeigt dann 0 oder verzerrte Conversions. Performance-Daten trotzdem schreiben, ROAS/CPA/CR als "nicht belastbar" markieren.
- **GAQL-Sonderfelder** — braucht der Skill Felder, die die Standard-Befehle nicht liefern (Ad-Group-Ebene, Conversion-Wert je Action via `segments.conversion_action`), via `run-gaql` selbst abfragen. GAQL-Referenz: die offizielle Google-Ads-Query-Builder-Doku.

## Was NICHT in diesen Skill gehört

- **Wettbewerber-Ads** — gibt es im First-Party-Konto nicht. Wettbewerbs-SEA-Sicht kommt aus `03-05-sea-google-ads-check` (Transparency Center).
- **Schreibende Operationen** — der Skill ist reine read-only-Status-Aufnahme. Keine Kampagnen-Änderungen, keine Negativ-Keyword-Uploads. Optimierungs-Empfehlungen bleiben Text.
- **GA4-Daten** — das Conversion-Tracking-Setup wird hier nur geprüft (Plausibilitäts-Check). Die GA4-Daten selbst und das volle Datenqualitäts-Gate liefert `03-18-web-analytics-ga4` über `google-analytics.py`.
- **Keyword-Difficulty / Suchvolumen** — gehört in `03-02-seo-keyword-recherche` (Ahrefs). Dieser Skill liefert die echten Conversion-Daten zu den Suchbegriffen, nicht die SEO-Metriken.
- **Cluster-/Intent-/Funnel-Tagging der Suchbegriffe** — gehört in `03-03-seo-keyword-kategorisierung`.
- **Forecast / Budget-Empfehlung** — gehört in `04-04-forecast-modell` und `04-06-retainer-kalkulator`. Dieser Skill liefert nur den Status-Quo als deren Datenbasis.
