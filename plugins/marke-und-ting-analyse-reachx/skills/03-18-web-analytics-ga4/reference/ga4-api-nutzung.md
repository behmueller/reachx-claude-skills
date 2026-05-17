# GA4-API-Nutzung

Wie der Skill Google-Analytics-4-Daten beschafft. Eine einzige Quelle: der Helper `${CLAUDE_PLUGIN_ROOT}/scripts/google-analytics.py`, der die GA4 Data API (Reporting) und die GA4 Admin API (Property-Liste) in eine zustandslose CLI mit JSON-Output wrappt — analog zu `google-ads.py` und `drive.py`.

Es gibt **keinen Fallback-Pfad** (anders als bei `03-04`, das einen Ahrefs-GSC-Fallback hat). Ohne `google-credentials.yaml` oder ohne zugängliche Property skippt der Skill freundlich.

## Auth und Setup

`google-analytics.py` liest OAuth-User-Credentials aus `~/.config/reachx-mta/google-credentials.yaml` (chmod 600) — **dieselbe Datei wie `google-ads.py`**. Der Helper braucht daraus nur drei Felder: `client_id`, `client_secret`, `refresh_token`. Der refresh_token deckt beide Google-APIs ab (Ads und Analytics), weil der OAuth-Scope beim Erzeugen breit genug gewählt wurde.

- Pfad überschreibbar via Env-Var `REACHX_GOOGLE_CREDENTIALS`.
- Wenn `03-17-sea-first-party-google-ads` (Schwester-Skill) bereits lief, ist die Datei schon da — beide Skills teilen sie.
- Fehlt die Datei: einmalig `google-oauth.py` ausführen (OAuth-Browser-Login mit dem zentralen Agentur-Account). Der genaue Setup-Schritt liegt außerhalb dieses Skills.
- Verwendeter Scope: `https://www.googleapis.com/auth/analytics.readonly` (nur Lesezugriff).

**Python-Libraries:** Der Helper braucht `google-analytics-data`, `google-analytics-admin`, `google-auth`, `pyyaml`. Installation: `pip3 install -r ${CLAUDE_PLUGIN_ROOT}/scripts/requirements-google.txt`. Fehlt eine Library, gibt der Helper eine klare Fehlermeldung mit dem `pip3`-Befehl aus.

## Befehls-Inventar

Alle Befehle geben JSON nach stdout aus. Bei Konfig-/Auth-/API-Fehlern: Meldung nach stderr, Exit-Code 2.

| Befehl | Zweck | Wichtigste Felder im Output |
|---|---|---|
| `list-properties` | Alle GA4-Properties, auf die der OAuth-Account Zugriff hat (Admin API) | `count`, `rows[].property_id`, `rows[].display_name`, `rows[].account` |
| `overview <pid>` | Account-Aggregat ohne Dimension — die Kern-Kennzahlen | `metrics.{sessions, totalUsers, newUsers, screenPageViews, engagementRate, averageSessionDuration, keyEvents}` |
| `channels <pid>` | Traffic nach Default Channel Group | `rows[].{sessionDefaultChannelGroup, sessions, totalUsers, newUsers, keyEvents, engagementRate}` |
| `top-pages <pid>` | Meistbesuchte Seiten nach Aufrufen | `rows[].{pagePath, screenPageViews, sessions, totalUsers, averageSessionDuration}` |
| `conversions <pid>` | Events nach Key-Event-Zahl — Key Events (Conversions) oben | `rows[].{eventName, keyEvents, eventCount, eventValue}` |
| `run-report <pid>` | Frei konfigurierbarer Report (Dimensionen + Metriken) | `rows[]` mit den angeforderten Dimensionen/Metriken, `row_count` |

Gemeinsame Optionen:

- `--range R` — Zeitraum. Entweder `<N>daysAgo` (z. B. `365daysAgo`, `30daysAgo`; Ende = `today`) oder ein expliziter Bereich `YYYY-MM-DD:YYYY-MM-DD`. Auch `today`/`yesterday` erlaubt. Default: `30daysAgo`.
- `--limit N` — Zeilen-Limit (Default 100). Greift bei `top-pages` und `run-report`.
- `--dimensions d1,d2` und `--metrics m1,m2` — nur bei `run-report`, CSV-Listen von GA4-API-Namen.

`<pid>` (property_id) wird intern zu `properties/<ziffern>` normalisiert — Bindestriche/Buchstaben sind egal, der Helper zieht die Ziffern.

## Property-Matching (`list-properties` → Kunde)

`meta.json` ist read-only und hat **keine `property_id`**. Der Skill muss die Property selbst finden:

1. **Domain aus `meta.json.website` normalisieren:** URL parsen, Host extrahieren, `www.` entfernen, lowercase. Beispiel: `https://www.aufmaster.de/leistungen` → `aufmaster.de`.
2. **Kundennamen-Token aus `meta.json.kunde`:** tokenisieren, lowercase. Beispiel: `"Aufmaster GmbH"` → `["aufmaster", "gmbh"]`.
3. **Gegen `list-properties`-Antwort matchen.** GA4-Property-`display_name`s tragen üblicherweise die Domain (`aufmaster.de - GA4`), den Markennamen (`Aufmaster Web`) oder eine Mischung. Auch das `account`-Feld prüfen — es trägt oft den Firmennamen.
   - Match-Kriterium: Domain-Stamm (ohne TLD) ODER ein Kundennamen-Token (länger als 3 Zeichen, kein generisches Wort wie `gmbh`, `ag`, `web`) kommt im `display_name` oder `account` vor.
4. **Genau ein Treffer** → `property_id` als Vorschlag an den Hauptthread.
5. **Mehrere Treffer** → alle Kandidaten dem Hauptthread vorlegen. Häufiger Fall: eine Live-Property und eine alte/Test-Property mit ähnlichem Namen. Strategen-Frage 3 im Gate (Property-Wahl) deckt das zusätzlich ab.
6. **Kein Treffer** → freundlicher Skip (SKILL.md Schritt 2 Fall 1).

**Der Hauptthread bestätigt die `property_id` immer** — der Skill rät nie. Bei Re-Run wird die bestätigte ID aus dem Frontmatter der vorhandenen `ga4-datenqualitaet.md` (bzw. `ga4-first-party.md`) gelesen, dann ist keine erneute Bestätigung nötig.

## Zeitraum-Defaults

Der Skill arbeitet mit zwei Pflicht-Zeiträumen, beide als `<N>daysAgo` an `--range` übergeben:

| Periode | `--range`-Wert | Zweck |
|---|---|---|
| 12 Monate | `365daysAgo` | Saisonalität, Jahres-Trend, stabile Conversion-Baseline |
| 30 Tage | `30daysAgo` | Aktueller Stand |

Für den Monats-Verlauf: `run-report` mit `--dimensions yearMonth` und `--range 365daysAgo`.

**Datenhistorie ermitteln:** Die GA4 Data API liefert keinen direkten "Property-Start"-Wert. Heuristik:

```bash
python3 "$GA" run-report <pid> --dimensions yearMonth --metrics sessions --range 730daysAgo
```

Die früheste `yearMonth`-Zeile mit `sessions > 0` markiert den faktischen Property-Start. Liegt sie weniger als 12 Monate zurück → Frontmatter `historie_verfuegbar_tage` setzen, 12-Monats-Range auf den verfügbaren Bereich kürzen, kein YoY-Vergleich.

## GA4-Metrik- und Dimensions-Namen

`run-report` braucht die exakten GA4-API-Namen. Die wichtigsten für diesen Skill:

### Metriken

| API-Name | Bedeutung |
|---|---|
| `sessions` | Sitzungen |
| `totalUsers` | Gesamt-Nutzer |
| `newUsers` | Neue Nutzer |
| `activeUsers` | Aktive Nutzer |
| `screenPageViews` | Seitenaufrufe |
| `engagementRate` | Engagement-Rate (0..1) |
| `averageSessionDuration` | Durchschnittliche Sitzungsdauer (Sekunden) |
| `keyEvents` | Key Events (= Conversions in GA4-Terminologie) |
| `eventCount` | Event-Anzahl gesamt |
| `eventValue` | Summierter Event-Wert |
| `totalRevenue` | Gesamt-Umsatz (E-Commerce + sonstige) |
| `purchaseRevenue` | Kauf-Umsatz |
| `transactions` | Anzahl Transaktionen |
| `bounceRate` | Absprungrate (0..1) |

### Dimensionen

| API-Name | Bedeutung |
|---|---|
| `sessionDefaultChannelGroup` | Default Channel Group der Sitzung (Organic Search, Paid Search, Direct, Referral, Organic Social, ...) |
| `sessionSourceMedium` | Quelle/Medium der Sitzung (`google / organic`, `idealo.de / referral`, `(direct) / (none)`, ...) |
| `sessionSource` | Nur die Quelle |
| `sessionMedium` | Nur das Medium |
| `firstUserDefaultChannelGroup` | Channel der allerersten Sitzung des Nutzers (Akquise-Sicht) |
| `pagePath` | Seitenpfad (ohne Host) |
| `landingPage` | Einstiegsseite der Sitzung |
| `eventName` | Event-Name |
| `country` | Land |
| `deviceCategory` | `desktop` / `mobile` / `tablet` |
| `date` | Tag (`YYYYMMDD`) |
| `yearMonth` | Monat (`YYYYMM`) — gut für 12-Monats-Verlauf |
| `sessionCampaignName` | Kampagnen-Name der Sitzung (UTM) |

**Wichtig — GA4-Channel-Namen sind englisch:** `sessionDefaultChannelGroup` liefert `Organic Search`, `Paid Search`, `Direct`, `Referral`, `Organic Social`, `Paid Social`, `Email`, `Display`, `Affiliates`, `Unassigned`, `(not set)`. Der Skill behält die englischen Bucket-Namen in der CSV bei (`channel`-Spalte), darf sie aber im Markdown/HTML deutsch beschreiben.

**`(not set)` und `Unassigned`** sind GA4-eigene Sammelbuckets für nicht zuordenbaren Traffic — sie zählen beim Check "unzugeordneter Traffic" (siehe `ga4-datenqualitaet.md`).

## run-report — die zentralen Aufrufe

Der Skill nutzt `run-report` für alles, was über die vier Komfort-Befehle hinausgeht.

### source/medium-Report (Phase A Kurz-Pull und Phase B)

```bash
# Phase A — Kurz-Scan auf unübliche Kanäle
python3 "$GA" run-report <pid> --dimensions sessionSourceMedium \
  --metrics sessions,keyEvents --range 365daysAgo --limit 100

# Phase B — voller source/medium-Report
python3 "$GA" run-report <pid> --dimensions sessionSourceMedium \
  --metrics sessions,totalUsers,keyEvents,engagementRate --range 365daysAgo --limit 200
```

`run-report` sortiert standardmäßig nicht — die Zeilen kommen in API-Reihenfolge. Der Skill sortiert lokal nach `sessions` absteigend. (Die Komfort-Befehle `channels`, `top-pages`, `conversions` sortieren intern via `order_by_metric`.)

### Monats-Verlauf

```bash
python3 "$GA" run-report <pid> --dimensions yearMonth \
  --metrics sessions,totalUsers,keyEvents --range 365daysAgo
```

### Geo- und Device-Split

```bash
python3 "$GA" run-report <pid> --dimensions country \
  --metrics sessions,keyEvents,engagementRate --range 365daysAgo --limit 15

python3 "$GA" run-report <pid> --dimensions deviceCategory \
  --metrics sessions,keyEvents,engagementRate --range 365daysAgo
```

### Umsatz pro Channel (E-Commerce-Check)

```bash
python3 "$GA" run-report <pid> --dimensions sessionDefaultChannelGroup \
  --metrics totalRevenue,transactions,sessions --range 365daysAgo
```

Liefert das alles `0`/leer → die Property misst keinen Umsatz (Lead-Geschäft). E-Commerce-Sektionen entfallen, AOV bleibt `null`.

### Conversion-Rate pro Channel

Es gibt keine direkte `conversionRate`-Metrik, die der Helper exponiert. Der Skill berechnet sie lokal: pro Channel-Zeile `conversion_rate = keyEvents / sessions`. Die `channels`-Antwort liefert `keyEvents` und `sessions` direkt mit.

## API-Budget

Die GA4 Data API ist **kostenlos**. Die Quotas sind großzügig (Standard-Property):

- **Tokens pro Tag:** 200.000 (Analytics-360-Properties deutlich mehr).
- **Tokens pro Stunde:** 40.000.
- **Concurrent Requests:** 10.

Ein `run-report` kostet je nach Komplexität wenige bis einige Dutzend Tokens. Ein voller Skill-Lauf (Phase A: ~5 Calls, Phase B: ~12–20 Calls) bleibt weit unter dem Limit.

Strategie:
- Sequenzielle Calls, nicht parallel — vermeidet Concurrency-Limit-Treffer.
- Bei `429`/`RESOURCE_EXHAUSTED`: 60 s warten, einmal Retry, dann bisher erhobene Daten schreiben und Rest als offen markieren.
- Phase A und Phase B teilen sich den Roh-Cache: Daten, die Phase A schon gezogen hat (`overview`, `channels`, `conversions` für 12M), in Phase B aus `~/.cache/reachx-mta/<slug>/audits/raw/ga4-gate-*.json` lesen statt erneut callen.

## Fehler-Behandlung

| Fehler | Reaktion |
|---|---|
| `google-credentials.yaml` fehlt | Freundlicher Skip mit Setup-Anleitung (SKILL.md Schritt 1) |
| Python-Library fehlt | Helper gibt `pip3`-Befehl aus — Skill leitet das im Skip-Hinweis weiter |
| `list-properties` schlägt mit Auth-Fehler fehl | "OAuth-Token erneuern — `google-oauth.py` ausführen", sauberer Abbruch (nur dieser Skill) |
| Keine passende Property | Freundlicher Skip mit Viewer-Einladungs-Hinweis (SKILL.md Schritt 2 Fall 1) |
| `429` / `RESOURCE_EXHAUSTED` | 60 s warten, einmal Retry, dann teil-schreiben |
| `5xx` / transienter API-Fehler | 30 s warten, einmal Retry, dann den Call als "fehlgeschlagen" markieren, weiter mit nächstem |
| Leere Antwort bei nicht-kritischem Call (`run-report` Umsatz, Geo) | Feld auf `null`/leer, kein Skill-Abbruch |
| Leere Antwort bei kritischem Call (`overview`, `channels`) | Hinweis "GA4 liefert keine Daten — Property erst kürzlich verbunden? Datenstand prüfen", `historie_verfuegbar_tage` minimal, sauber abschließen |
| `PERMISSION_DENIED` beim Reporting (Property gelistet, aber kein Lese-Recht) | Wie "keine passende Property" — freundlicher Skip mit Hinweis, dass der Account mindestens Viewer braucht |

Alle Helper-Fehler kommen als `Analytics-Fehler: <text>` mit Exit-Code 2 — der Skill prüft den Exit-Code und reagiert nach obiger Tabelle.

## Roh-Daten-Caching

Pro Helper-Aufruf die Roh-Antwort als JSON in `~/.cache/reachx-mta/<slug>/audits/raw/` ablegen:

- Phase-A-Kurz-Pull: `ga4-gate-conversions-12m.json`, `ga4-gate-overview-12m.json`, `ga4-gate-overview-30d.json`, `ga4-gate-channels-12m.json`, `ga4-gate-sourcemedium.json`, `ga4-gate-historie.json`.
- Phase-B-Voll-Pull: `ga4-channels-12m.json`, `ga4-channels-30d.json`, `ga4-sourcemedium-12m.json`, `ga4-top-pages-12m.json`, `ga4-verlauf-monate.json`, `ga4-geo.json`, `ga4-device.json`, `ga4-umsatz.json`.

Struktur jeder Datei:

```json
{
  "befehl": "channels",
  "property_id": "<id>",
  "range": "365daysAgo",
  "abgefragt_am": "<ISO-8601>",
  "phase": "A" | "B",
  "response": { ...komplette Helper-Antwort... }
}
```

Vorteil: Phase B liest Phase-A-Daten ohne Re-Call; Folge-Skills (`04-02`, `04-04`) können bei Bedarf nachschauen; Reproduzierbarkeit. Am Ende von Phase B den `raw/`-Ordner komprimiert nach Drive `assets/raw/` hochladen.

## Edge-Cases (API-Ebene)

- **Property-ID-Format:** Der Hauptthread könnte die ID mit Präfix nennen (`properties/123456`) oder pur (`123456`). Der Helper normalisiert beides — egal, was übergeben wird.
- **`yearMonth` ohne Daten am Rand:** GA4 liefert für Monate mit 0 Sessions oft gar keine Zeile (statt einer Zeile mit 0). Der Skill darf fehlende Monate im Verlauf als 0 ergänzen, wenn sie innerhalb des Property-Lebenszeitraums liegen.
- **`screenPageViews` vs. `pageviews`:** GA4 nutzt `screenPageViews` (deckt Web-Seiten und App-Screens ab). Der alte UA-Name `pageviews` existiert nicht — bei `run-report` immer `screenPageViews` verwenden.
- **`keyEvents` vs. altes `conversions`:** GA4 hat die Metrik 2024 von `conversions` auf `keyEvents` umbenannt. Der Helper nutzt `keyEvents`. In der Skill-Dokumentation und in den Outputs wird umgangssprachlich weiter "Conversion(s)" geschrieben — gemeint sind immer Key Events.
- **Sehr große source/medium-Long-Tail:** `--limit 200` reicht praktisch immer; die strategisch relevanten Quellen stehen oben. Kein Paginieren nötig.

## Was NICHT in diesen Skill gehört

- **Wettbewerber-GA4-Daten** — gibt es nicht, GA4 ist first-party-only. Wettbewerbs-Sicht kommt aus den Third-Party-Audit-Skills.
- **Realtime-Daten** — die GA4 Data API kann Realtime, der Skill braucht es nicht (Status-Quo, keine Live-Überwachung).
- **GA4-Admin-Konfiguration ändern** — der Skill liest nur (`analytics.readonly`). Conversion-Events umtaggen, Data Filters setzen etc. ist Beratungs-Output für den Strategen, keine Skill-Aktion.
- **Google-Ads-Daten** — gehören in `03-17-sea-first-party-google-ads`. Auch wenn GA4 verknüpfte Ads-Kampagnen zeigt: die Paid-Performance-Tiefe (Spend, CPC, Quality Score) kommt aus dem Ads-Helper.
- **GSC-Daten** — gehören in `03-04-seo-first-party-gsc`. `03-18` liest `gsc-first-party.md` nur für den Abgleich, zieht aber selbst keine GSC-Daten.
- **Event-Detail-Analyse / Funnel-Exploration** — der Skill bleibt auf Kanal-, Page- und Conversion-Aggregat-Ebene. Tiefe Event-Funnels gehören in ein dediziertes CRO-Audit, das (noch) nicht Teil der MTA-Pipeline ist.
