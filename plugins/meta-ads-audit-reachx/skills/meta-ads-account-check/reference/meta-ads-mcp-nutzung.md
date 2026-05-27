# Meta-Ads-MCP — Tool-Nutzung & Schreibschutz

Diese Datei ist die kanonische Referenz dafür, **welche** MCP-Tools der Skill aufruft,
**mit welchen Parametern** — und welche Tools **niemals** angefasst werden dürfen.

---

## 0. Schreibschutz — die wichtigste Regel

**Dieser Skill verändert NIEMALS etwas am Werbekonto.** Er ist ein reiner Lese-Audit.

### Verbotene Tools — niemals aufrufen

Die folgenden Meta-Ads-MCP-Tools sind für diesen Skill **gesperrt**. Sie werden
unter keinen Umständen aufgerufen — auch dann nicht, wenn der Nutzer mitten im
Lauf darum bittet, „direkt eine Kleinigkeit zu fixen":

| Gesperrtes Tool | Was es täte |
|---|---|
| `ads_create_campaign` | Kampagne anlegen |
| `ads_create_ad_set` | Ad Set anlegen |
| `ads_create_ad` | Anzeige anlegen |
| `ads_create_creative` | Creative anlegen |
| `ads_create_custom_audience` | Zielgruppe anlegen |
| `ads_update_entity` | Kampagne/Ad Set/Ad ändern (Budget, Status, Targeting …) |
| `ads_update_custom_audience_users` | Nutzer in eine Custom Audience schreiben |
| `ads_activate_entity` | Pausierte Entität aktivieren |
| `ads_catalog_create` | Produktkatalog anlegen |
| `ads_catalog_create_product_set` | Produkt-Set anlegen |

**Wenn der Nutzer eine Änderung wünscht:** freundlich erklären, dass dieser Skill
bewusst read-only ist (Onboarding-Audit — erst aufzeigen, nicht eingreifen), und
die gewünschte Änderung als Empfehlung in den Report aufnehmen. Die Umsetzung ist
ein bewusst getrennter, späterer Schritt außerhalb dieses Skills.

### Erlaubte Tools — ausschließlich diese

Nur abfragende Tools: alle `ads_get_*`, alle `ads_insights_*` und die lesenden
`ads_catalog_get_*`. Diese ändern per Definition nichts.

### Optionale Härtung über `settings.json`

Zusätzlich zur Prompt-Disziplin kann eine Deny-Regel in `~/.claude/settings.json`
die Write-Tools hart blockieren — siehe `SKILL.md` Abschnitt „Optionale
Permission-Härtung". Empfohlen, aber nicht zwingend.

---

## 1. Konto-Discovery

### `ads_get_ad_accounts`

Liefert alle zugänglichen Werbekonten, paginiert in 50er-Blöcken. Pro Konto:
`ad_account_id` (numerisch), `ad_account_name`, `business_id`, `business_name`,
`is_ads_mcp_enabled`, `is_queryable`, ggf. `not_queryable_reason`.

- **`is_ads_mcp_enabled: false`** → dieses Konto und seine Objekte NICHT in weiteren
  Tool-Calls verwenden.
- **`is_queryable: false`** → `ads_get_ad_entities` für dieses Konto nicht aufrufen;
  stattdessen `not_queryable_reason` an den Nutzer ausgeben.
- Bei gesetztem `next_cursor`: erneut mit `cursor` aufrufen, bis alle Konten da sind.

Die Business-Felder zeigen nur den **besitzenden** Business — mit Agenturen geteilte
Konten können weitere Zugriffe haben, die hier nicht erscheinen.

---

## 2. Performance-Daten — das Arbeitspferd

### `ads_get_ad_entities`

Das flexibelste Tool. Holt Entitäten auf `account` / `campaign` / `adset` / `ad`-Ebene
mit Metriken, Attributen, Breakdowns, Filtern und Sortierung.

**Workflow (Pflicht-Reihenfolge):**
1. Kandidaten-Felder wählen.
2. Mit `ads_get_field_context` verifizieren (Feldnamen sind level-skopiert — ein
   Feld der Kampagnen-Ebene ist auf Ad-Ebene evtl. ungültig). Nicht-auflösbare Namen
   gibt `ads_get_field_context` in `unknown_fields` zurück — diese NIE an
   `ads_get_ad_entities` übergeben.
3. `ads_get_ad_entities` aufrufen.

**Verifizierte Feldnamen (Stand Testlauf 2026-05-22)** — die Meta-Marketing-API-Namen
weichen von der Umgangssprache ab. Bestätigt gültig:

| Zweck | Korrekter Feldname | Hinweis |
|---|---|---|
| Spend | `amount_spent` | **NICHT `spend`** — `spend` wird als `unknown_field` abgelehnt |
| Impressionen | `impressions` | account/campaign/adset/ad |
| Reichweite | `reach` | account/campaign/adset/ad |
| Frequenz | `frequency` | account/campaign/adset/ad |
| CPM | `cpm` | account/campaign/adset/ad |
| Ergebnisse | `results` | verschachteltes Objekt, siehe unten |
| Kosten/Ergebnis | `cost_per_result` | campaign/adset/ad — **nicht account-level** |
| ROAS | `purchase_roas` | account/campaign/adset/ad — oft `Not available` (s. Abschnitt 9) |
| Objective | `objective` | nur campaign/ad |
| Status | `status` | nur campaign/adset/ad |
| Delivery-Status | `delivery` | nur campaign/adset/ad — enum (`active`/`error`/`off`/`inactive`/…) |
| Name | `name` | **NICHT `campaign_name`/`adset_name`/`ad_name`** |

`id` und `name` immer mitführen. Nicht existierende Felder (im Testlauf abgelehnt):
`spend`, `link_clicks`, `quality_ranking`, `engagement_rate_ranking`,
`conversion_rate_ranking`, `purchases`, `account_currency`, `date_start`/`date_stop`
(Letztere liefert das Tool automatisch im Output, nicht als `fields` anfordern).

**`results` / `cost_per_result` sind verschachtelte Objekte**, kein Skalar:

```json
"results": {"value": [{"indicator": "actions:offsite_conversion.fb_pixel_purchase",
  "values": [{"value": 13825, "attribution_windows": ["default"]}]}]}
```

Der `indicator` nennt die gemessene Aktion (`actions:offsite_conversion.fb_pixel_purchase`,
`actions:purchase`, bei Awareness-Kampagnen `reach`). Beim Aggregieren über mehrere
Kampagnen nur gleichartige `indicator` zusammenzählen — eine Awareness-Kampagne mit
`indicator: reach` liefert keine Käufe.

**Zeitraum (Pflicht für Metriken):** Ohne `date_preset` ODER `time_range` liefert das
Tool nur Attribute, keine Metriken. Nie beide gleichzeitig setzen.
- `date_preset`: `last_30d`, `last_90d`, `last_year`, `maximum`, `this_month` …
- `time_range`: JSON-String `'{"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}'`

**`time_increment`** steuert die Aufschlüsselung innerhalb des Zeitraums: `"1"`–`"90"`
(Tagesfenster), `"monthly"`, `"all_days"`. Für die 12-Monats-Kurve: `time_increment="monthly"`.

**`level`** — immer explizit setzen: `account` fürs Gesamtbild, `campaign` / `adset` /
`ad` für die jeweilige Ebene.

**`breakdowns`** — z. B. `publisher_platform`, `platform_position`, `impression_device`,
`age`, `gender`, `country`, `region`. Für den Audit relevant: `publisher_platform`
(Facebook / Instagram / Audience Network / Messenger) und `platform_position`
(Feed / Stories / Reels …) zeigen die Placement-Verteilung.

**Limitierung:** Das Tool gibt ggf. nur eine Teilmenge zurück. Für Top- UND Flop-Werte
zweimal aufrufen mit gegenläufigem `sort` (z. B. `spend_descending` / `spend_ascending`).
Nie denselben Call mit identischen Parametern wiederholen.

**Wichtig:** Nur Parameter aus dem Tool-Schema verwenden — keine erfundenen Felder.

### `ads_get_field_context`

Vor `ads_get_ad_entities` die geplanten Felder verifizieren. Liefert pro Feld, auf
welchen Levels es gültig, filter- und sortierbar ist.

---

## 3. Metas eigene Diagnose-Tools

Diese Tools liefern fertige Analytik — sie sind der Kern, der aus Rohdaten einen
echten Audit macht.

### `ads_get_opportunity_score`

Account-weiter Gesundheits-Score **0–100** plus nach `opportunity_score_lift`
(in **Punkten**) sortierte Empfehlungen. **Nur Account-Ebene** — niemals einer
einzelnen Kampagne zuschreiben. Parameter: nur `ad_account_id`.

### `ads_insights_performance_trend`

Zeitreihen-Analyse je KPI: `CPC`, `CPM`, `CPR`, `ROAS`, `CTR`, `CVR`, `SPEND`,
`CLICKS`, `IMPRESSIONS`, `REACH`, `RESULT`, `COST_PER_LEAD`. Liefert Richtungs-Aussagen
(„CPC steigt seit X").

Parameter: `ad_account_id` (Pflicht), optional `analysis_level` (`AD` / `ADSET`),
`analysis_metric` (nur wenn explizit eine Metrik gefragt ist), `conversation_intent`,
`conversation_topic`, `entity_ids`. Für den Audit ohne `analysis_metric` aufrufen →
liefert alle Kern-KPIs. Sinnvolle Kontext-Werte: `conversation_intent` =
`OPTIMIZE_COST_OUTCOMES`, `conversation_topic` = `AUCTION_AND_DELIVERY`.

### `ads_insights_anomaly_signal`

Erkennt ungewöhnliche Muster / Abweichungen. Parameter: `ad_account_id` (Pflicht),
optional `entity_ids`. **Anomalien sind Beobachtungen, keine Ursachen** — im Report
als „prüfenswert" einordnen, nicht als feststehende Diagnose. Für belastbare,
kausal verknüpfte Hebel auf `ads_get_opportunity_score` verweisen.

### `ads_insights_auction_ranking_benchmarks`

Diagnostiziert die Auktions-Wettbewerbsfähigkeit: welche Ads stärker performen,
welche Faktoren (Gebot, Anzeigenqualität) optimierbar sind. Erkennt **Audience-Overlap**
und Fragmentierung (hoher Overlap → Unter-Auslieferung, Budget-Zersplitterung).
Parameter: `ad_account_id` (Pflicht), `date_preset` ODER `date_from`+`date_to`,
optional `entity_ids`. `date_preset`-Werte sind GROSSGESCHRIEBEN: `LAST_30D`,
`LAST_90D`, `LIFETIME` …

### `ads_insights_industry_benchmark`

Vergleicht Ad-Set-Performance gegen aggregierte Benchmarks ähnlicher Advertiser
derselben Branche. **Auf Business-Outcome-Metriken fokussieren** (Cost-per-Result),
nicht auf Oberflächen-Metriken (CPM). Vergleiche nur zwischen Ad-Objekten mit
ähnlichem Optimierungsziel. Parameter wie bei `industry_benchmark`: `ad_account_id`,
`date_preset` (GROSS) oder `date_from`+`date_to`, optionale Kontext-Werte.

---

## 4. Struktur- & Tracking-Gesundheit

### `ads_get_errors`

Auslieferungs-blockierende **harte Fehler** für Kampagne / Ad Set / Ad. Parameter:
`entity_ids` (Pflicht — bei Übergabe der Account-ID werden die Fehler aller
Kind-Entitäten geliefert, nicht die des Kontos selbst), optional `limit` (default 50).

**Deckt NICHT ab:** Performance-/Pacing-Probleme, gesperrte Konten, Anzeigen-Ablehnungen.

### `ads_get_datasets`

Listet die Datasets (Pixel / App / Conversions-API-Quellen) des Kontos. Basis für
die folgenden Dataset-Tools.

### `ads_get_dataset_quality`

Signal-Qualität pro Dataset: **EMQ-Score** (Event Match Quality), Match-Key-Coverage,
Upload-Frische. Gruppiert nach Channel (`web`, `offline`, `crm`, `custom_attribution`).
Parameter: `dataset_id` (Pflicht), optional `query_type`. **Niedrige EMQ-Scores oder
schwache Match-Key-Coverage immer flaggen** — sie untergraben die Verlässlichkeit
aller Conversion- und ROAS-Zahlen.

### `ads_get_dataset_stats`

Event-**Volumen** pro Dataset (Counts). Ergänzt `dataset_quality` (das keine Counts
liefert). Zeigt, ob der Pixel plausibel feuert.

### `ads_get_dataset_details`

Stammdaten eines Datasets.

### `ads_catalog_get_catalogs` / `ads_catalog_get_diagnostics` / `ads_catalog_get_feed_rules`

Nur relevant bei E-Commerce / Advantage+ Shopping / Katalog-Kampagnen.
`ads_catalog_get_diagnostics` zeigt Katalog-/Feed-Fehler. Wenn das Konto keinen
Katalog nutzt, dieses Modul überspringen.

---

## 5. Creative-Inventar

### `ads_get_creatives`

Listet Creatives. **Achtung Teilergebnis:** Ohne `creative_ids` liefert das Tool nur
`id`, `name`, `account_id`, `status`. Für weitere Felder (`body`, `title`, `link_url`,
`call_to_action_type`, `child_attachments` …) erneut mit `creative_ids` oder `fields`
aufrufen — ein fehlendes Feld bedeutet NICHT, dass es leer ist.

### `ads_get_creative_ads` / `ads_get_ad_images` / `ads_get_ad_videos`

Creative↔Ad-Zuordnung bzw. Bild-/Video-Assets. Für den Standard-Audit optional —
die Creative-Fatigue-Lesart kommt primär aus `frequency` (über `ads_get_ad_entities`).

---

## 6. Custom Audiences

### `ads_get_ad_account_custom_audiences` / `ads_get_custom_audience`

Listet Custom Audiences bzw. Detail einer Audience: Typ (Website, CRM, Lookalike,
Engagement), `approximate_count`, `delivery_status`, `operation_status`, Alter.
Zeigt die Audience-Strategie und veraltete / zu kleine Listen. **Nur lesen** —
`ads_update_custom_audience_users` ist gesperrt (Abschnitt 0).

---

## 7. Konto-/Feld-Hilfen (optional)

- `ads_get_field_context` — Feld-Verifikation (siehe Abschnitt 2).
- `ads_get_help_article` — Meta-Hilfeartikel, falls eine Fehlermeldung unklar ist.
- `ads_insights_advertiser_context` — Advertiser-Kontext, optionaler Hintergrund.

---

## 8. Aufruf-Budget & Fehlerverhalten

- Ein vollständiger Audit-Lauf liegt typisch bei **20–35 Tool-Calls**. Bei sehr
  großen Konten (viele Kampagnen) kann die Entitäts-Erhebung mehr Calls brauchen.
- Calls nie mit identischen Parametern wiederholen.
- **Transienter Fehler / 5xx / Rate-Limit:** einmal 30–60 s warten, ein Retry. Bei
  erneutem Fehler: bisher erhobene Daten verwenden, die Lücke im Report als „nicht
  erhoben" markieren — kein Abbruch des gesamten Audits.
- **`is_queryable: false` / `is_ads_mcp_enabled: false`:** sauberer Stopp mit dem
  vom MCP gelieferten Grund, siehe `SKILL.md` Schritt 1.

---

## 9. Bekannte Verfügbarkeits-Einschränkungen — Reduced-Modus

Der Meta-Ads-MCP wird **schrittweise ausgerollt**. Einzelne Tools und einzelne
Metriken sind je nach Werbekonto unterschiedlich verfügbar. Der Skill behandelt das
**pro Tool / pro Metrik** als Datenlücke und läuft im Reduced-Modus weiter — niemals
Komplett-Abbruch, weil ein einzelnes Tool fehlt.

### Tools, die kontoabhängig fehlen können

Liefert ein Tool den Fehler *„This tool is new and is being gradually rolled out…
Please check back at a later date"*, ist es für dieses Konto **nicht freigeschaltet**.
Im Testlauf 2026-05-22 (Globetrotter, Konto 356312596796397) betraf das:

- `ads_get_datasets`, `ads_get_dataset_quality`, `ads_get_dataset_stats`,
  `ads_get_dataset_details` → **Modul 4** ohne direkten EMQ-/CAPI-Messwert. Ersatz:
  indirekte Signale aus `ads_get_opportunity_score` (z. B. eine
  `capi_event_coverage`-Empfehlung verrät ein vorhandenes Pixel mit lückenhafter
  CAPI-Abdeckung) und `ads_get_errors` (z. B. Offline-Dataset-Zugriffsfehler).
- `ads_get_creatives`, `ads_get_creative_ads` → **Modul 5** ohne Creative-Inventar.
  Ersatz: `frequency` aus `ads_get_ad_entities` als Burnout-Indiz, Creative-bezogene
  Empfehlungen aus dem Opportunity Score.
- `ads_get_ad_account_custom_audiences`, `ads_get_custom_audience` → **Modul 3** ohne
  Audience-Strategie-Sicht.

### `ads_insights_*`-Tools liefern oft keine Daten

`ads_insights_performance_trend`, `ads_insights_anomaly_signal`,
`ads_insights_auction_ranking_benchmarks` und `ads_insights_industry_benchmark`
antworten regelmäßig mit *„No … data available for the given criteria"* — auch bei
aktiven Konten mit hohem Spend. Das ist kein Fehler, sondern fehlende Datendeckung.
Folgen:
- **Modul 2** ohne Branchen-Benchmark und ohne Metas Trend-Aussage → die
  12-Monats-Kurve aus `ads_get_ad_entities` (`time_increment="monthly"`) selbst auswerten.
- **Modul 6** ohne Anomalie-Signal → Auffälligkeiten allein aus M1–M5 ableiten.

### Metriken, die `Not available` sein können

`ads_get_ad_entities` gibt einzelne Metriken pro Konto als String `"Not available"`
zurück — im Testlauf durchgängig `clicks`, `ctr`, `cpc`, `purchase_roas`, teilweise
`results`. Solche Werte:
- **nicht als `0` behandeln** — die Kennzahl ist *nicht erhoben*, nicht „null".
- abgeleitete Kennzahlen (CTR/CPC-Formeln) entfallen dann; im Output leer lassen.
- die Lücke explizit benennen — im `datenluecken`-Block des Aggregats und im
  HTML-Disclaimer.
- Ist `purchase_roas` nicht verfügbar, das Konto über `results` / `cost_per_result`
  (Cost-per-Purchase) bewerten und das fehlende ROAS im Datenqualitäts-Vorbehalt
  ausdrücklich nennen.

### Pflicht: Reduced-Modus dokumentieren

Sobald ein Modul wegen fehlender Tools/Metriken nur teilweise erhoben werden konnte,
trägt der Report einen **Datenlücken-Block** (Markdown-Frontmatter `datenluecken` +
HTML-`.disclaimer` bzw. `.suggestion niedrig`). Das Gesamturteil bleibt gültig — es
stützt sich dann ausdrücklich auf die belastbar erhobenen Module.
