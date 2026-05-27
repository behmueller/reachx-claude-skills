---
name: meta-ads-account-check
description: Read-only Audit eines Meta-Ads-Werbekontos für den Start einer Agentur-Zusammenarbeit. Greift First-Party über den Meta-Ads-MCP auf das echte Werbekonto des Kunden zu und prüft in sechs Modulen den Account-Gesundheitszustand (Opportunity Score, Delivery-Fehler), die Performance-Entwicklung über 12 Monate (Trend je KPI, Branchen-Benchmark), die Kampagnen-Struktur (Budget-Verteilung, Auction-Overlap, Audience-Setup), die Tracking- und Datenqualität (Pixel, Conversions-API, EMQ-Score), die Creative-Lage (Frequency, Format-Mix) und synthetisiert daraus priorisierte Findings mit Quick-Wins und Top-3-Hebeln. Erzeugt ein Markdown-Aggregat, eine Kampagnen-CSV und einen REACHX-gebrandeten HTML-Report fürs Kundengespräch. Der Skill nimmt UNTER KEINEN UMSTÄNDEN Änderungen am Werbekonto vor — keine Kampagnen, keine Budgets, keine Status-Wechsel. Nutze diesen Skill, wenn der Nutzer ein Meta-Ads-Konto, Facebook-Ads-Konto oder Instagram-Ads-Konto prüfen, auditieren oder bewerten will — auch bei Phrasen wie "Meta-Ads-Konto checken", "Werbekonto-Audit", "neues Werbekonto prüfen", "wie performt das Meta-Konto", "Facebook-Ads-Account auditieren", "Onboarding-Check Werbekonto", "Account-Health Meta", "Meta-Ads-Quick-Check", "ist das Kampagnen-Setup gut", "Performance-Probleme im Werbekonto finden", "Tracking-Setup prüfen Meta". Setzt voraus, dass der Meta-Ads-MCP-Server verbunden ist und der Nutzer First-Party-Zugriff auf das Konto hat.
---

# Meta-Ads-Werbekonto-Audit

Ein **read-only Onboarding-Audit** für Meta-Ads-Werbekonten. Wenn REACHX als Agentur
erstmals Zugriff auf das Werbekonto eines Kunden bekommt, liefert dieser Skill in
einem Lauf ein belastbares Gesamtbild: Wie hat sich die Performance entwickelt, ist
das Kampagnen-Setup verbesserbar, gibt es strukturelle Probleme, und gab es in den
letzten 12 Monaten unentdeckte Performance-Einbrüche?

Das Ergebnis ist bewusst **vorzeigbar** — ein REACHX-gebrandeter HTML-Report, der dem
Kunden direkten Mehrwert zeigt und die Kompetenz der Agentur darstellt, bevor
überhaupt eine Optimierung beginnt.

## Read-only — die zentrale Regel

**Dieser Skill verändert NIEMALS etwas am Werbekonto.** Er zeigt auf, er greift nicht
ein. Keine Kampagne wird angelegt, kein Budget geändert, kein Status umgeschaltet,
keine Zielgruppe geschrieben.

Die verändernden Meta-Ads-MCP-Tools (`ads_create_*`, `ads_update_*`,
`ads_activate_entity`, `ads_update_custom_audience_users`, `ads_catalog_create*`)
sind **gesperrt** — vollständige Liste in `reference/meta-ads-mcp-nutzung.md`
Abschnitt 0. Bittet der Nutzer mitten im Lauf um eine Änderung, wird das freundlich
abgelehnt und als Empfehlung in den Report aufgenommen — die Umsetzung ist ein
bewusst getrennter, späterer Schritt.

## Ausführungs-Modus

Der Skill läuft **im Hauptthread**, ohne Subagent — der Audit ist interaktiv (Konto-
Bestätigung, ggf. Rückfragen) und überschaubar im Token-Verbrauch. Er hat keine
Abhängigkeit zum `marke-und-ting-analyse-reachx`-Plugin: kein Drive, kein `meta.json`,
kein Projektkontext. Outputs landen lokal im Dateisystem.

> **Hinweis:** Für den Einsatz innerhalb einer laufenden MARKE&TING-Analyse existiert
> der Schwester-Skill `03-21-sea-first-party-meta-ads` im MTA-Plugin — gleiche Audit-
> Methodik, aber in den MTA-Kontext (Drive, `meta.json`, `contracts.md`) eingehängt.

## Voraussetzungen

- **Meta-Ads-MCP verbunden** — der MCP-Server `Meta_Ads_MCP` muss in Claude Code
  aktiv sein (Tools mit Präfix `ads_*`). Fehlt er, bricht der Skill mit Hinweis ab.
- **First-Party-Zugriff** — der mit dem MCP verbundene Meta-Account hat Zugriff auf
  das zu prüfende Werbekonto (eigenes Konto oder geteilter Agentur-Zugriff).

Fehlt der MCP:

```
✗ Meta-Ads-Account-Audit nicht möglich — Meta-Ads-MCP nicht verbunden.

So beheben:
1. In Claude Code den Meta-Ads-MCP-Server verbinden (Meta_Ads_MCP).
2. Diesen Skill erneut aufrufen.
```

## Optionale Permission-Härtung

Zusätzlich zur Prompt-Disziplin kann eine Deny-Regel die Write-Tools hart blockieren.
In `~/.claude/settings.json` unter `permissions.deny`:

```json
"mcp__claude_ai_Meta_Ads_MCP__ads_create_campaign",
"mcp__claude_ai_Meta_Ads_MCP__ads_create_ad_set",
"mcp__claude_ai_Meta_Ads_MCP__ads_create_ad",
"mcp__claude_ai_Meta_Ads_MCP__ads_create_creative",
"mcp__claude_ai_Meta_Ads_MCP__ads_create_custom_audience",
"mcp__claude_ai_Meta_Ads_MCP__ads_update_entity",
"mcp__claude_ai_Meta_Ads_MCP__ads_update_custom_audience_users",
"mcp__claude_ai_Meta_Ads_MCP__ads_activate_entity",
"mcp__claude_ai_Meta_Ads_MCP__ads_catalog_create",
"mcp__claude_ai_Meta_Ads_MCP__ads_catalog_create_product_set"
```

Empfohlen für Strategen, die den Skill regelmäßig nutzen — dann ist der Schreibschutz
nicht nur Konvention, sondern erzwungen. Der genaue Tool-Präfix kann je nach MCP-
Installation abweichen; im Zweifel den tatsächlichen Namen aus einem Tool-Aufruf
übernehmen.

## Ablauf

### Schritt 0: Konto-Discovery und Bestätigung

**0.1** `ads_get_ad_accounts` aufrufen. Bei gesetztem `next_cursor` weiter paginieren,
bis alle Konten erfasst sind.

**0.2** Pro Konto prüfen: `is_ads_mcp_enabled` und `is_queryable`. Konten mit
`is_ads_mcp_enabled: false` aus der Auswahl nehmen.

**0.3 Konto wählen:**
- Hat der Nutzer beim Aufruf einen Kontonamen / eine Account-ID genannt → dagegen matchen.
- **Genau ein nutzbares Konto** → vorschlagen und bestätigen lassen.
- **Mehrere Konten** → alle mit `ad_account_name`, `ad_account_id`, `business_name`
  auflisten und fragen, welches geprüft werden soll. **Niemals raten** — das falsche
  Konto zu auditieren verfälscht den ganzen Report.
- **Kein nutzbares Konto** → Hinweis ausgeben, dass der verbundene Meta-Account keinen
  First-Party-Zugriff auf ein querybares Werbekonto hat, und sauber stoppen.

Die Bestätigungsfrage erklärt, **warum** sie gestellt wird:

```
Ich habe Zugriff auf dieses Werbekonto:
  "Musterkunde GmbH" (ID 123456789, Business: Musterkunde GmbH, Währung EUR)

Soll ich den read-only Audit für dieses Konto starten? Ich bestätige lieber vorab —
ein Audit des falschen Kontos würde den ganzen Report unbrauchbar machen.
```

**0.4** Erst nach Bestätigung weiter. Konto-Stammdaten (`ad_account_id`, Name,
`business_name`, Währung) für Frontmatter und Report merken.

### Schritt 1: Voraussetzungs- und Queryability-Check

- Ist das gewählte Konto `is_queryable: false` → `not_queryable_reason` an den Nutzer
  ausgeben. Die `ads_insights_*`-Tools und `ads_get_opportunity_score` funktionieren
  oft trotzdem; `ads_get_ad_entities` nicht. In diesem Fall den Audit im reduzierten
  Modus fahren (ohne Entitäts-Ebene) und das im Report als Datenlücke vermerken.
- Konto-Status prüfen (gesperrt / eingeschränkt). Ein eingeschränktes Konto ist selbst
  schon Finding `konto_eingeschraenkt`.

### Schritt 2: Zeiträume festlegen

Zwei Zeiträume mit **identischem Enddatum** (heute):

- **`zeitraum_lang`** — 12 Monate: `time_range` `{"since":"<heute-365>","until":"<heute>"}`.
- **`zeitraum_kurz`** — 30 Tage: `time_range` `{"since":"<heute-30>","until":"<heute>"}`.

Für `ads_insights_*`- und `ads_catalog_*`-Tools mit GROSSGESCHRIEBENEM `date_preset`:
`LAST_30D` bzw. — wo nötig — `date_from`/`date_to` explizit. Begründung für identische
Enddaten: `reference/audit-methodik.md` §3.

### Schritt 3: Modul 1 — Account-Health

- `ads_get_opportunity_score` (nur `ad_account_id`) → Score 0–100 + Empfehlungen,
  sortiert nach `opportunity_score_lift` (Punkte).
- `ads_get_errors` mit der Account-ID als `entity_ids` → harte Delivery-Blocker der
  Kind-Entitäten.
- Ampel nach `reference/audit-methodik.md` §2 (M1).

### Schritt 4: Modul 2 — Performance-Verlauf

- `ads_get_field_context` → Felder für `ads_get_ad_entities` verifizieren (Workflow:
  `reference/meta-ads-mcp-nutzung.md` §2).
- `ads_get_ad_entities` `level=account`, `time_increment="monthly"`, `time_range`
  = `zeitraum_lang` → die 12-Monats-Kurve (Spend, Impressions, Reach, Clicks, CTR,
  CPC, CPM, Results, Purchase-Value).
- `ads_get_ad_entities` `level=account`, `time_range` = `zeitraum_kurz` → 30-Tage-Snapshot.
- `ads_insights_performance_trend` (ohne `analysis_metric`) → Richtungs-Aussage je KPI.
- `ads_insights_industry_benchmark` `date_preset="LAST_90D"` → Cost-per-Result vs.
  Branche (auf Outcome-Metriken fokussieren, nicht CPM).
- Kennzahlen lokal ableiten (`reference/audit-methodik.md` §3). 30-T dem anteiligen
  12-M-Schnitt gegenüberstellen.
- Ampel nach §2 (M2).

### Schritt 5: Modul 3 — Struktur & Setup

- `ads_get_ad_entities` `level=campaign`, `time_range` = `zeitraum_lang`, sortiert
  nach `spend` absteigend → Kampagnen-Übersicht, Objective-Mix, Budget-Verteilung.
  Bei sehr vielen Kampagnen zusätzlich aufsteigend sortiert aufrufen, um Flops zu sehen.
- `ads_get_ad_entities` `level=adset`, `time_range` = `zeitraum_lang` → Ad-Set-Anzahl
  und -Größen (Lernphasen-Indiz: viele kleine Ad Sets mit wenig Conversions).
- `ads_get_ad_entities` `level=account`, `breakdowns=["publisher_platform"]` und ein
  zweiter Call mit `breakdowns=["platform_position"]` → Placement-Verteilung.
- `ads_insights_auction_ranking_benchmarks` `date_preset="LAST_30D"` → Auction-Overlap
  und -Wettbewerbsfähigkeit.
- `ads_get_ad_account_custom_audiences` → Audience-Strategie; bei auffälligen Audiences
  `ads_get_custom_audience` für Details.
- Auffälligkeiten prüfen: `budget_konzentration`, `zombie_kampagne`, `auction_overlap`,
  `lernphase_dauerhaft`, `audience_fragmentierung`, `placement_eingeschraenkt`,
  `objective_mismatch`, `advantage_ungenutzt`. Ampel nach §2 (M3).

### Schritt 6: Modul 4 — Tracking & Datenqualität

**Das ist der Vertrauens-Disclaimer für den ganzen Report.**

- `ads_get_datasets` → vorhandene Datasets (Pixel / App / CAPI-Quellen). Kein
  Dataset → Finding `kein_conversion_tracking`, Modul rot.
- Pro Dataset `ads_get_dataset_quality` → EMQ-Score, Match-Key-Coverage, Frische
  (nach Channel `web`/`offline`/`crm`). EMQ-Lesart: `reference/audit-methodik.md` §4.
- Pro Dataset `ads_get_dataset_stats` → Event-Volumen (feuert der Pixel plausibel?).
- Conversions-API-Status: gibt es eine Server-seitige / CAPI-Quelle? Wenn nur Browser-
  Pixel → Finding `capi_fehlt`.
- Ampel nach §2 (M4). **Steht M4 auf rot, wird die Gesamt-Ampel mindestens gelb** und
  der Datenqualitäts-Vorbehalt prominent in Report-Kopf und Synthese gesetzt.

### Schritt 7: Modul 5 — Creatives

- `ads_get_ad_entities` `level=ad`, `time_range` = `zeitraum_kurz`, Felder inkl.
  `frequency` → Creative-Anzahl je Ad Set, Frequency-Lesart (Burnout-Indiz).
- `ads_get_creatives` → Creative-Inventar und Format-Mix. Für Detailfelder ggf.
  zweiter Call mit `creative_ids` (Teilergebnis-Hinweis: `reference/meta-ads-mcp-nutzung.md` §5).
- Auffälligkeiten `creative_burnout`, `creative_mono`. Ampel nach §2 (M5).

### Schritt 7b: Katalog (nur bei E-Commerce)

Nutzt das Konto Katalog-/Advantage+-Shopping-Kampagnen → `ads_catalog_get_catalogs`,
dann `ads_catalog_get_diagnostics` für Feed-Fehler. Kein Katalog → Modul überspringen.

### Schritt 8: Modul 6 — Synthese

- `ads_insights_anomaly_signal` (`ad_account_id`) → Anomalien der letzten Zeit;
  als „prüfenswert" einordnen, nicht als feststehende Ursache.
- Alle Auffälligkeiten aus M1–M5 + Anomalien zusammenführen, nach Relevanz sortieren
  (`reference/audit-methodik.md` §5, §6).
- Quick-Wins von strukturellen Themen trennen.
- Top-3-Hebel bestimmen — der Mehrwert-Kern fürs Kundengespräch.
- Gesamt-Ampel ableiten (rotes M4 → mindestens gelb).

### Schritt 9: Output-Verzeichnis und CSV

Verzeichnis anlegen: `~/meta-ads-audits/<konto-slug>-<YYYY-MM-DD>/`
(`<konto-slug>` = Kontoname kleingeschrieben, nicht-alphanumerische Zeichen → `-`).

`meta-ads-kampagnen.csv` schreiben — Schema in `reference/audit-output-schema.md` §2.
Eine Zeile je Kampagne × Zeitraum (`12m`, `30t`).

### Schritt 10: Markdown-Aggregat

`meta-ads-audit.md` schreiben — YAML-Frontmatter + Body nach
`reference/audit-output-schema.md` §1.

### Schritt 11: HTML-Report

`reference/report-shell.html` lesen, die sechs Platzhalter ersetzen,
`meta-ads-audit.html` ins Output-Verzeichnis schreiben. `{{MAIN_CONTENT}}`
ausschließlich aus den Bausteinen in `reference/audit-output-schema.md` §3 —
keine eigenen CSS-Klassen, kein inline-`style` (Ausnahme: `bar-fill`-Breite),
der `<style>`-Block bleibt unverändert. Vor dem Speichern prüfen: keine offenen
`{{…}}`, nur definierte Klassen.

Der Report trägt **Erkenntnisse**, nicht nur Tabellen: Gesamt-Ampel, Datenqualitäts-
Vorbehalt, Top-3-Hebel und Findings stehen prominent; CSV ist die Maschinen-Schicht.

### Schritt 12: Abschluss im Chat

```
✓ Meta-Ads-Werbekonto-Audit abgeschlossen — read-only, keine Änderungen vorgenommen.

Konto: <Kontoname> (<ad_account_id>)

Outputs (lokal in ~/meta-ads-audits/<slug>-<datum>/):
- meta-ads-audit.html — REACHX-Report fürs Kundengespräch
- meta-ads-audit.md   — Aggregat mit allen Befunden
- meta-ads-kampagnen.csv — Kampagnen-Rohdaten

Gesamt-Ampel: <grün | gelb | rot>
<bei Datenqualitäts-Vorbehalt: ⚠ ROAS-Zahlen unter Vorbehalt — Tracking unvollständig.>

Modul-Ampeln:
- M1 Account-Health:   <Ampel>
- M2 Performance:      <Ampel>
- M3 Struktur:         <Ampel>
- M4 Tracking:         <Ampel>
- M5 Creatives:        <Ampel>

Kennzahlen 12 Monate:
- Spend:            XXX <Währung>
- ROAS:             X,X
- Cost per Result:  XXX <Währung>
- Opportunity Score: XX / 100
- Trend 30 Tage:    <Spend +/- Z% ggü. 12-M-Schnitt>

Top-3-Hebel:
1. <Hebel>
2. <Hebel>
3. <Hebel>

[Wenn offene Frage / Datenlücke:]
? Offen: <Punkt, der das Bild noch schärfen würde>
```

## Bundled Resources

- `reference/meta-ads-mcp-nutzung.md` — welche MCP-Tools, mit welchen Parametern,
  **Schreibschutz und gesperrte Tools** (Abschnitt 0), Aufruf-Budget, Fehlerverhalten.
- `reference/audit-methodik.md` — sechs Module, Ampel-Logik, Kennzahlen-Formeln,
  EMQ-Lesart, Auffälligkeiten-Katalog, Synthese-Regeln, Ton der Findings.
- `reference/audit-output-schema.md` — Markdown-Frontmatter, CSV-Spalten, HTML-
  Platzhalter und Report-Bausteine.
- `reference/report-shell.html` — REACHX-gebrandete HTML-Shell (Red Hat, Sunrise-Red,
  Night-Sky) mit Platzhaltern.

## Edge Cases

- **Meta-Ads-MCP nicht verbunden** → sauberer Stopp mit Hinweis (siehe Voraussetzungen).
- **Kein nutzbares Werbekonto** (`is_ads_mcp_enabled: false` für alle) → Stopp mit
  Hinweis, dass der verbundene Account keinen First-Party-Zugriff hat.
- **Konto `is_queryable: false`** → reduzierter Modus ohne Entitäts-Ebene (M3/M5
  eingeschränkt), `not_queryable_reason` im Report, Datenlücke vermerken.
- **Einzelne Tools für das Konto nicht ausgerollt** (Fehler „gradually rolled out")
  oder **`ads_insights_*` liefert „No data available"** → reduzierter Modus pro Modul,
  kein Abbruch. Ersatz-Signale und Pflicht-Dokumentation in
  `reference/meta-ads-mcp-nutzung.md` Abschnitt 9.
- **Metriken `Not available`** (häufig `clicks`/`ctr`/`cpc`/`purchase_roas`) → nicht
  als `0` werten, abgeleitete Kennzahl entfällt, Datenlücke vermerken. Ist ROAS nicht
  verfügbar, wird das Konto über `results`/`cost_per_result` (Cost-per-Purchase)
  bewertet — der Datenqualitäts-Vorbehalt nennt das fehlende ROAS explizit.
- **Mehrere Werbekonten** → auflisten, vom Nutzer wählen lassen, nie raten.
- **Konto ohne Spend-Historie** (12-M-Spend ≈ 0) → minimaler Report,
  `kein_spend_historie`-Hinweis, Performance-Module entfallen mangels Daten.
- **Konto aktuell inaktiv** (30-T-Spend = 0, 12-M-Spend > 0) → Audit läuft durch,
  Finding `konto_inaktiv`.
- **Kein Conversion-Tracking** → M4 rot, Finding `kein_conversion_tracking`,
  Datenqualitäts-Vorbehalt; Performance-Zahlen werden trotzdem ausgewiesen, aber
  durchgängig als „unter Vorbehalt" markiert.
- **Kein Katalog** → Schritt 7b entfällt, kein Finding.
- **Nutzer wünscht eine Änderung am Konto** → freundlich ablehnen (read-only), die
  Änderung als Empfehlung in den Report aufnehmen. Niemals ein `ads_create_*`-,
  `ads_update_*`-, `ads_activate_entity`- oder `ads_catalog_create*`-Tool aufrufen.
- **Rate-Limit / 5xx** → einmal 30–60 s warten, ein Retry; dann mit Teil-Daten
  weiterarbeiten und die Lücke im Report markieren — kein Komplett-Abbruch.
- **Sehr großes Konto** (viele Kampagnen) → `ads_get_ad_entities` mit `limit` und
  gegenläufiger Sortierung zweimal aufrufen (Top + Flop nach Spend); CSV auf die
  Top-Kampagnen nach Spend kappen und das im Body vermerken.

## Wichtige Konventionen

- **Read-only ist nicht verhandelbar.** Im Zweifel: aufzeigen, nicht eingreifen.
- Geld-Werte aus dem MCP unverändert übernehmen (Konto-Währung), keine eigene
  Umrechnung. Währung überall mit ausweisen.
- Abgeleitete Kennzahlen bleiben leer (nicht `0`), wenn der Nenner 0 ist.
- Anomalie-Signale sind Beobachtungen, keine Diagnosen — im Report so kennzeichnen.
- Der HTML-Report ist die Interpretations-Schicht (Erkenntnisse, Ampeln, Top-3),
  die CSV die Maschinen-Schicht.
