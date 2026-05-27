---
name: 03-21-sea-first-party-meta-ads
description: Erhebt für den Kunden den First-Party-Meta-Ads-Status-Quo direkt aus dessen echtem Werbekonto über den Meta-Ads-MCP - im Gegensatz zu 03-06-sea-meta-ads-library-check, das via öffentliche Meta Ad Library nur die sichtbaren Anzeigen der WETTBEWERBER sieht. Read-only Audit in sechs Modulen: Account-Health (Opportunity Score, Delivery-Fehler), Performance-Entwicklung über 12 Monate (Trend je KPI, Branchen-Benchmark, 30-Tage-Snapshot), Kampagnen-Struktur (Budget-Verteilung, Auction-Overlap, Audience-Setup), Tracking- und Datenqualität (Pixel, Conversions-API, EMQ-Score - der Vertrauens-Disclaimer), Creative-Lage (Frequency, Format-Mix) und eine Synthese mit priorisierten Findings und Top-3-Hebeln. Output ist audits/meta-ads-first-party.md mit Aggregat plus audits/meta-ads-first-party-kampagnen.csv als Roh-Datenbasis plus HTML-Report reports/05d-meta-ads-first-party.html. Der Skill nimmt NIEMALS Änderungen am Werbekonto vor. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext das echte Meta-Ads-Konto des Kunden auswerten will - auch bei Phrasen wie "Meta-Ads First-Party", "echtes Werbekonto des Kunden prüfen", "wie performt das Meta-Konto", "Facebook-Ads-Konto auditieren", "Kampagnen-Performance Meta", "Tracking-Setup Meta prüfen", "Werbekonto-Audit", "Account-Health Meta", "Conversions-API checken", "Paid-Social First-Party". Setzt 01-01-mta-projekt-init voraus; bei fehlendem Meta-Ads-MCP oder keinem Konto-Zugriff freundlicher Skip mit Anleitung, KEIN Abbruch des MTA-Workflows.
---

# SEA-First-Party-Meta-Ads

**First-Party-SEA-Skill in Stufe 3** (Kanal-Audits). Erhebt aus dem **echten Meta-Ads-
Werbekonto des Kunden** über den Meta-Ads-MCP den First-Party-Paid-Social-Status-Quo:
Spend, Reach, Klicks, CTR, CPC, CPM, Results, ROAS, Opportunity Score, Tracking-
Qualität und die Kampagnen-/Creative-Struktur.

Dieser Skill ist Teil des **First-Party-Blocks** der MTA — gemeinsam mit
`03-04-seo-first-party-gsc` (Search Console), `03-17-sea-first-party-google-ads`
(Google Ads) und `03-18-web-analytics-ga4` (GA4). Der Block legt die **Realitäts-Basis**
aus den echten Konten des Kunden, *bevor* Third-Party-Tools und Wettbewerbs-Audits
laufen. Keine harte Abhängigkeit zu den anderen First-Party-Skills.

Klare Abgrenzung zu `03-06-sea-meta-ads-library-check`:

- **`03-06-sea-meta-ads-library-check`** sieht via öffentliche Meta Ad Library nur die
  **sichtbaren Anzeigen der Wettbewerber** — keine Spends, keine Klicks, keine
  Conversions. Wettbewerbs-Sicht von außen.
- **Dieser Skill (`03-21`)** sieht das **echte eigene Konto des Kunden** mit allen
  internen Performance-Daten: was kostet die Kampagne, was konvertiert, wie sauber
  misst das Tracking. First-Party-Realität von innen.

Warum First-Party-Meta wertvoll ist: Die Ad Library zeigt nur, *dass* jemand Anzeigen
schaltet — nie *wie gut*. Das echte Konto zeigt die Wahrheit. Ein Kunde mit ROAS 0,9
bei kaputtem Conversion-Tracking hat ein anderes Problem als einer mit ROAS 6,0 und
sauberer Conversions-API — und genau diese Lesart braucht die MTA-Story.

Die First-Party-Meta-Daten verankern mehrere Folge-Skills:
- `04-02-kanal-chancen-analyse` bekommt die echte Paid-Social-Performance als Hebel-Score
- `04-04-forecast-modell` kann mit echten CR-/CPA-Werten statt Branchen-Annahmen rechnen

## Read-only — die zentrale Regel

**Dieser Skill verändert NIEMALS etwas am Werbekonto.** Keine Kampagne, kein Budget,
kein Status, keine Zielgruppe. Die verändernden Meta-Ads-MCP-Tools (`ads_create_*`,
`ads_update_*`, `ads_activate_entity`, `ads_update_custom_audience_users`,
`ads_catalog_create*`) sind **gesperrt** — vollständige Liste in
`reference/meta-ads-mcp-nutzung.md` Abschnitt 0. Bittet der Stratege mitten im Lauf
um eine Änderung, wird das abgelehnt und als Empfehlung in den Report aufgenommen.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread
orchestriert (User-Interaktion, Konto-Bestätigungs-Stopp), der Subagent führt die
Skill-Logik aus (MCP-Calls, Drive-Operationen via `drive.py`, Output-Generierung) und
gibt einen kompakten Status zurück.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + ggf. eine vom Strategen bestätigte `ad_account_id`
- Erwarteter Rückgabe-Status: Standard-Schlussformat (`contracts.md` Abschnitt 6)

**Konto-Bestätigung läuft über den Hauptthread:** Die `ad_account_id` steht *nicht* in
`meta.json`. Der Subagent schlägt sie aus dem Kontonamen-Match vor, der Hauptthread
holt die Bestätigung beim Strategen ein (Schritt 2). Erst mit bestätigter ID läuft
die Datenerhebung.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren (`contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="03-21-sea-first-party-meta-ads"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Render den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
```

## Wann triggern

- "Meta-Ads First-Party" / "Paid-Social First-Party"
- "Echtes Werbekonto des Kunden prüfen"
- "Wie performt das Meta-Konto" / "Facebook-Ads-Konto auswerten"
- "Kampagnen-Performance Meta" / "Werbekonto-Audit"
- "Tracking-Setup Meta prüfen" / "Conversions-API checken"
- "Account-Health Meta" / "Opportunity Score"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` mit `kunde`, `website`,
  `kunden_slug`, `region` vorhanden.
- **Meta-Ads-MCP verbunden** — der MCP-Server `Meta_Ads_MCP` (Tools mit Präfix
  `ads_*`) ist in Claude Code aktiv. **Pflicht-MCP** im Sinne von `contracts.md` §11.
- **First-Party-Zugriff** — der mit dem MCP verbundene Meta-Account hat Zugriff auf
  das Werbekonto des Kunden (eigenes Konto oder geteilter Agentur-Zugriff).

**Wichtig:** Fehlt der Meta-Ads-MCP oder ist kein Konto des Kunden zugänglich →
**freundlicher Skip mit Anleitung, KEIN Abbruch.** Der MTA-Workflow läuft mit
`03-06-sea-meta-ads-library-check` (Wettbewerber-Ad-Library-Sicht) und den übrigen
Audits nahtlos weiter. First-Party-Meta ist ein **Bonus**, kein Blocker — analog zur
Skip-Logik in `03-17-sea-first-party-google-ads`.

**Reihenfolge — bewusst früh:** Teil des First-Party-Blocks, läuft nach den Setup-
Skills und idealerweise **vor `02-02-wettbewerber-identifikation`** sowie vor den
Third-Party- und Wettbewerbs-Audits. Die einzige *harte* Voraussetzung ist
`01-01-mta-projekt-init`.

## Ablauf

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Inputs aus Drive, Outputs nach Drive — `contracts.md` Abschnitt 4. Helper:
`01-01-mta-projekt-init/scripts/drive.py`.

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

Lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/`.

### Schritt 1: Projekt-Auffindung und MCP-Health-Check

Folge `contracts.md` Abschnitt 1. Fehlt `meta.json`:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

**MCP-Health-Check** (`contracts.md` §11): mit einem billigen Call prüfen, ob der
Meta-Ads-MCP erreichbar ist — `ads_get_ad_accounts` (liefert ohnehin die Konto-Liste
für Schritt 2). Schlägt er fehl / ist der MCP nicht verbunden → **freundlicher Skip:**

```
ℹ 03-21-sea-first-party-meta-ads geskippt — Meta-Ads-MCP nicht verbunden.

So beheben:
1. In Claude Code den Meta-Ads-MCP-Server verbinden (Meta_Ads_MCP).
2. Diesen Skill erneut aufrufen.

Bis dahin läuft der MTA-Workflow weiter — kein Blocker. Die Wettbewerber-Meta-Sicht
liefert 03-06-sea-meta-ads-library-check unabhängig davon.

Nächste Schritte:
1. 03-06-sea-meta-ads-library-check — Wettbewerber-Anzeigen via Meta Ad Library

Sag mir, welcher als nächster.
```

`status.md` mit Vermerk `geskippt — meta_ads_mcp_fehlt`, Mini-Eintrag im
"✓ Erledigt"-Block mit Status "geskippt".

### Schritt 2: Konto-Auffindung und Bestätigung

`meta.json` ist read-only und enthält **keine `ad_account_id`**.

**2.1 Re-Run-Erkennung** — Prüfe via `drive.py list-children "$AUDITS_ID"`, ob
`meta-ads-first-party.md` existiert. Wenn ja: `quelle.ad_account_id` aus dem
Frontmatter lesen und direkt nutzen — Sprung zu Schritt 3.

**2.2 Konto-Liste** — `ads_get_ad_accounts` (paginieren bei `next_cursor`). Pro Konto:
`ad_account_id`, `ad_account_name`, `business_name`, `is_ads_mcp_enabled`,
`is_queryable`. Konten mit `is_ads_mcp_enabled: false` aussortieren.

**2.3 Namens-Matching** — `meta.json.kunde` (und Host aus `meta.json.website`) gegen
die `ad_account_name`- und `business_name`-Felder matchen (case-insensitiv, ohne
Rechtsform-Suffixe wie „GmbH", „AG").

**2.4 Vorschlag und Bestätigung** — Der Subagent gibt den Vorschlag an den Hauptthread,
der die Strategen-Bestätigung einholt. Die Frage erklärt, **warum**:

- **Genau ein Treffer:**
  ```
  Werbekonto-Treffer für <Kunde>: "<Kontoname>" (ID <ad_account_id>,
  Business <business_name>, Währung EUR).
  Bitte bestätigen — dann ziehe ich die First-Party-Daten dieses Kontos.
  ```
- **Mehrere Treffer:** alle listen, beschreibende Rückfrage, welches das aktive Konto
  des Kunden ist (sonst würde das falsche Konto die ganze Paid-Social-Lesart verzerren).
- **Kein Treffer:** freundlicher Skip, `status.md`-Vermerk `geskippt — kein_konto_match`,
  Override-Hinweis: Skill mit `ad_account_id=<ID>` erneut aufrufen.

**Override:** Aufruf mit `ad_account_id=<ID>` überspringt das Matching. Schlägt der
erste Call mit Permission-Error fehl → sauberer Skip.

### Schritt 3: Zeiträume festlegen

Zwei Zeiträume mit **identischem Enddatum** (heute), Begründung in
`reference/meta-ads-audit-methodik.md` §3:

- **`zeitraum_lang`** — 12 Monate: `time_range` `{"since":"<heute-365>","until":"<heute>"}`.
- **`zeitraum_kurz`** — 30 Tage: `time_range` `{"since":"<heute-30>","until":"<heute>"}`.

Für `ads_insights_*`-Tools mit GROSSGESCHRIEBENEM `date_preset` (`LAST_30D`,
`LAST_90D`) bzw. `date_from`/`date_to`.

### Schritt 4: Datenerhebung — sechs Module

Tool-Parameter in `reference/meta-ads-mcp-nutzung.md`, Methodik und Schwellwerte in
`reference/meta-ads-audit-methodik.md`. **Geld-Werte unverändert übernehmen**
(Konto-Währung), keine eigene Umrechnung.

- **M1 Account-Health** — `ads_get_opportunity_score`, `ads_get_errors` (Account-ID
  als `entity_ids`), Konto-Status.
- **M2 Performance** — `ads_get_field_context` → `ads_get_ad_entities`
  (`level=account`, `time_increment="monthly"`, `zeitraum_lang`) für die 12-Monats-
  Kurve; zweiter Call mit `zeitraum_kurz`; `ads_insights_performance_trend`;
  `ads_insights_industry_benchmark` (`date_preset="LAST_90D"`).
- **M3 Struktur** — `ads_get_ad_entities` `level=campaign` (sort `spend`, ggf. Top+Flop)
  und `level=adset`; Breakdown-Calls `publisher_platform` und `platform_position`;
  `ads_insights_auction_ranking_benchmarks` (`date_preset="LAST_30D"`);
  `ads_get_ad_account_custom_audiences`.
- **M4 Tracking** — `ads_get_datasets`, pro Dataset `ads_get_dataset_quality`
  (EMQ, Match-Keys, Frische) und `ads_get_dataset_stats` (Volumen); CAPI-Status.
  **Der Vertrauens-Disclaimer** — rotes M4 macht die Gesamt-Ampel mindestens gelb.
- **M5 Creatives** — `ads_get_ad_entities` `level=ad` (inkl. `frequency`),
  `ads_get_creatives`.
- **M6 Synthese** — `ads_insights_anomaly_signal`; Auffälligkeiten aus M1–M5 + Anomalien
  zusammenführen, nach Relevanz sortieren, Quick-Wins vs. strukturell trennen,
  Top-3-Hebel bestimmen, Gesamt-Ampel ableiten.

Bei E-Commerce-Konten optional `ads_catalog_get_catalogs` →
`ads_catalog_get_diagnostics` (Feed-Fehler). Kein Katalog → überspringen.

Ampel-Logik je Modul, EMQ-Lesart und Auffälligkeiten-Katalog: `meta-ads-audit-methodik.md`
§2, §4, §5. Das `conversion_setup_urteil` (`sauber` / `mit_einschraenkung` /
`kein_tracking`) aus dem M4-Befund ableiten — es ist der Vertrauens-Anker für
`04-02`/`04-04`.

### Schritt 5: CSV-Output

`audits/meta-ads-first-party-kampagnen.csv` schreiben — Schema in
`reference/meta-ads-output-schema.md` §2. Eine Zeile je Kampagne × Zeitraum.

### Schritt 6: Aggregat-Markdown

`audits/meta-ads-first-party.md` schreiben — YAML-Frontmatter + Body nach
`reference/meta-ads-output-schema.md` §1. Quellen-Kennzeichnung pro Zahl
(`contracts.md` §13): Performance-Kennzahlen `erhoben`, Branchen-Benchmark `benchmark`,
Ampel-Urteile `schaetzung_skill`.

### Schritt 7: HTML-Report

`reports/05d-meta-ads-first-party.html` aus `reports/_shell.html` (Drive) bauen.
`{{MAIN_CONTENT}}` **ausschließlich** aus den Bausteinen in
`01-01-mta-projekt-init/reference/report-bausteine.md` — `contracts.md` Abschnitt 7.
Platzhalter und Content-Aufbau in `reference/meta-ads-output-schema.md` §3.

Vor dem Upload validieren:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" \
  ~/.cache/reachx-mta/<slug>/05d-meta-ads-first-party.html --shell
```

Exit 0 → hochladen. Exit 1 → Markup gegen `report-bausteine.md` korrigieren.

### Schritt 8: Outputs nach Drive

Reihenfolge nach `contracts.md` §3 (erst Inhalt, dann `status.md`):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "meta-ads-first-party.md" \
  ~/.cache/reachx-mta/<slug>/meta-ads-first-party.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "meta-ads-first-party-kampagnen.csv" \
  ~/.cache/reachx-mta/<slug>/meta-ads-first-party-kampagnen.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "05d-meta-ads-first-party.html" \
  ~/.cache/reachx-mta/<slug>/05d-meta-ads-first-party.html "text/html"
```

### Schritt 9: Dashboard-Update

`reports/index.html` aus Drive lesen, anpassen, zurückschreiben (`contracts.md` §7):
Stat-Strip um Meta-Spend/12M und ROAS ergänzen, `03-21-sea-first-party-meta-ads` in
die Erledigt-Sektion, `05d`-Report verlinken, Token-Slots aktualisieren.
„Nächster empfohlener Schritt": die noch nicht gelaufenen First-Party-Skills.

### Schritt 10: status.md

Aus Drive lesen, anpassen, zurückschreiben (`contracts.md` §3):

- `03-21-sea-first-party-meta-ads` in `schritte_done`.
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Highlight-Numbers (Spend/12M,
  ROAS, Opportunity Score, `conversion_setup_urteil`, Gesamt-Ampel).
- `naechster_empfohlen`: zuerst noch nicht gelaufene First-Party-Skills
  (`03-04`, `03-17`, `03-18`), dann `02-02-wettbewerber-identifikation`; nachgelagert
  `03-06-sea-meta-ads-library-check`.
- Bei `kein_conversion_tracking` oder ROAS < 1: Hinweis „in MTA-Story als Schwerpunkt".

### Schritt 11: Standard-Schlussformat im Chat

```
✓ 03-21-sea-first-party-meta-ads abgeschlossen — read-only, keine Änderungen.

Outputs (auf Drive):
- audits/meta-ads-first-party.md — Aggregat mit Modul-Befunden und Findings
- audits/meta-ads-first-party-kampagnen.csv — Kampagnen-Ebene (N Zeilen)
- reports/05d-meta-ads-first-party.html — visueller First-Party-Meta-Audit
Status aktualisiert in: status.md

Konto: <Kontoname> (<ad_account_id>)

Meta-Ads-Highlights (12 Monate):
- Spend:            XXX EUR
- ROAS:             X,X
- Cost per Result:  XXX EUR
- Opportunity Score: XX / 100
- Trend 30 Tage:    <Spend +/- Z% ggü. 12-M-Schnitt>

Gesamt-Ampel: <grün | gelb | rot>
Conversion-Setup: <sauber | mit Einschränkung | kein Tracking>

Modul-Ampeln: M1 <…> · M2 <…> · M3 <…> · M4 <…> · M5 <…>

Top-3-Hebel:
1. <Hebel>
2. <Hebel>
3. <Hebel>

[Wenn Datenqualitäts-Vorbehalt:]
⚠ ROAS-Zahlen unter Vorbehalt — Conversion-Tracking unvollständig (Modul 4 rot).

Nächste Schritte:
1. 03-17-sea-first-party-google-ads — restlicher First-Party-Block (Google Ads)
2. 03-04-seo-first-party-gsc / 03-18-web-analytics-ga4 — restlicher First-Party-Block
3. 02-02-wettbewerber-identifikation — nutzt die First-Party-Outputs zur Schärfung
4. (nachgelagert) 03-06-sea-meta-ads-library-check — Wettbewerber-Ad-Library-Sicht

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/meta-ads-mcp-nutzung.md` — MCP-Tools, Parameter, **Schreibschutz und
  gesperrte Tools** (Abschnitt 0), Aufruf-Budget, Fehlerverhalten.
- `reference/meta-ads-audit-methodik.md` — sechs Module, Ampel-Logik, Kennzahlen-
  Formeln, EMQ-Lesart, Auffälligkeiten-Katalog, Synthese-Regeln.
- `reference/meta-ads-output-schema.md` — MTA-Einbettung: Drive-Pfade, Frontmatter,
  CSV, HTML-Platzhalter, Report-Nummer `05d`, Dashboard-/`status.md`-Update.

## Edge Cases

- **Meta-Ads-MCP nicht verbunden** → freundlicher Skip mit Anleitung (Schritt 1).
  KEIN Abbruch des MTA-Workflows. `status.md`-Vermerk `geskippt — meta_ads_mcp_fehlt`.
- **Kein Konto-Match** → freundlicher Skip (Schritt 2.4), Override `ad_account_id=<ID>`.
- **Mehrere Konto-Treffer** → beschreibende Rückfrage über den Hauptthread, nie raten.
- **Konto `is_queryable: false`** → reduzierter Modus ohne Entitäts-Ebene (M3/M5
  eingeschränkt), `not_queryable_reason` im Body, Datenlücke vermerken.
- **Einzelne Tools für das Konto nicht ausgerollt** (Fehler „gradually rolled out")
  oder **`ads_insights_*` liefert „No data available"** → reduzierter Modus pro Modul,
  kein Abbruch. Ersatz-Signale und Pflicht-Dokumentation in
  `reference/meta-ads-mcp-nutzung.md` Abschnitt 9. Im Frontmatter unter `datenluecken`
  führen; die `gesamt_ampel` bleibt gültig und stützt sich auf die belastbar
  erhobenen Module.
- **Metriken `Not available`** (häufig `clicks`/`ctr`/`cpc`/`purchase_roas`) → nicht
  als `0` werten, abgeleitete Kennzahl entfällt, Datenlücke vermerken. Fehlt ROAS, das
  Konto über `results`/`cost_per_result` (Cost-per-Purchase) bewerten; das
  `conversion_setup_urteil` und der Datenqualitäts-Vorbehalt nennen das fehlende ROAS
  explizit.
- **Konto ohne Spend-Historie** (12-M-Spend ≈ 0) → minimaler Output,
  `daten_qualitaet: keine`, Hinweis „Konto angelegt, aber inaktiv".
- **Konto aktuell inaktiv** (30-T-Spend = 0, 12-M > 0) → Skill läuft durch,
  Auffälligkeit `konto_inaktiv`.
- **Kein Conversion-Tracking** → M4 rot, `conversion_setup_urteil: kein_tracking`,
  Datenqualitäts-Vorbehalt; Performance-Daten trotzdem schreiben, ROAS/CPA als „nicht
  belastbar" markieren.
- **Nutzer wünscht eine Änderung am Konto** → ablehnen (read-only), als Empfehlung in
  den Report. Niemals ein `ads_create_*`/`ads_update_*`/`ads_activate_entity`/
  `ads_catalog_create*`-Tool aufrufen.
- **Rate-Limit / 5xx** → einmal 30–60 s warten, ein Retry; dann mit Teil-Daten weiter,
  Lücke im Report markieren — kein Komplett-Abbruch.
- **Sehr großes Konto** → `ads_get_ad_entities` mit `limit` und gegenläufiger
  Sortierung zweimal (Top + Flop nach Spend); CSV auf Top-Kampagnen kappen, im Body
  vermerken.
- **CSV/Markdown existiert bereits** (Re-Run) → `ad_account_id` aus dem vorhandenen
  Frontmatter lesen (Schritt 2.1), dann (a) überschreiben / (b) Backup-und-neu nach
  `audits/_backup/meta-ads-*-<ISO>` / (c) abbrechen.
- **Abgrenzung zu `03-06`** → kein Konflikt: `03-06` sieht Wettbewerber von außen
  (Ad Library), `03-21` das Kundenkonto von innen. `04-02-kanal-chancen-analyse`
  kombiniert beide. Verschiedene Dateinamen (`meta-ads.md` vs. `meta-ads-first-party.md`).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- **Read-only ist nicht verhandelbar** — aufzeigen, nicht eingreifen.
- Outputs leben in Google Drive; Pfade Drive-relativ.
- Markdown + YAML-Frontmatter für `meta-ads-first-party.md`, CSV für die Kampagnen-Datei.
- Standard-Schlussformat im Chat; `status.md` und Dashboard in jedem Lauf aktualisiert
  (auch bei Skip).
- HTML-Report aus `reports/_shell.html`, Validierung Pflicht (`contracts.md` §7).
- Geld-Werte unverändert (Konto-Währung), keine eigene Umrechnung.
- Quellen-Kennzeichnung pro Zahl (`contracts.md` §13).
- **First-Party vs. Third-Party**: Pendant zu `03-06-sea-meta-ads-library-check`.
  `03-06` = Wettbewerber öffentlich, `03-21` = eigenes Konto echt. Beide ergänzen
  sich in `04-02-kanal-chancen-analyse`.
