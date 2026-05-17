---
name: 03-17-sea-first-party-google-ads
description: Erhebt für den Kunden den First-Party-Google-Ads-Status-Quo direkt aus dessen echtem Google-Ads-Konto - über den CLI-Wrapper google-ads.py (Befehle list-accounts, account-overview, campaign-performance, search-terms, keyword-performance, conversion-actions, run-gaql), der die offizielle google-ads-Python-Library wrappt und gegen den REACHX-MCC authentifiziert. Liefert die echten Spend-, Klick-, Conversion- und Quality-Score-Daten des Kundenkontos - im Gegensatz zu 03-05-sea-google-ads-check, das via Transparency Center nur die öffentlich sichtbaren Anzeigen der WETTBEWERBER sieht. Default-Zeitraum 12 Monate plus letzte 30 Tage. Kern-Analysen: Account- und Kampagnen-Performance (Spend, Impressionen, Klicks, CTR, CPC, Conversions, Conversion-Value, ROAS, Kampagnentyp-Mix), Search-Terms-Analyse mit Streuverlust-Hinweisen und Brand-vs-Non-Brand-Split, Quality-Score-Verteilung als Optimierungs-Hebel, und ein leichter Conversion-Plausibilitäts-Check (welche Conversion-Actions, Status, Typ, Kategorie, mögliche GA4-Doppelzählung). Output ist audits/sea-first-party.md mit Aggregat plus audits/sea-kampagnen.csv und audits/sea-suchbegriffe.csv als Roh-Datenbasis plus HTML-Report reports/05c-sea-first-party.html. Die Suchbegriffe-CSV ist zusätzlich Roh-Keyword-Quelle für 03-02-seo-keyword-recherche und 03-03-seo-keyword-kategorisierung. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext das echte Google-Ads-Konto des Kunden auswerten will - auch bei Phrasen wie "Google Ads First-Party", "echtes Ads-Konto auswerten", "Kampagnen-Performance des Kunden", "wie performt das Kundenkonto", "Search-Terms-Report", "Suchbegriffe-Analyse", "Quality Score prüfen", "Ads-Conversion-Setup", "SEA First-Party", "Streuverlust im Konto", "ROAS der Kampagnen", "Google-Ads-Audit des eigenen Kontos". Setzt 01-01-mta-projekt-init voraus; bei fehlender google-credentials.yaml oder keinem Konto-Match freundlicher Skip mit Anleitung, KEIN Abbruch des MTA-Workflows.
---

# SEA-First-Party-Google-Ads

**First-Party-SEA-Skill in Stufe 3** (Kanal-Audits). Erhebt aus dem **echten Google-Ads-Konto des Kunden** über den CLI-Wrapper `${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py` den First-Party-SEA-Status-Quo: Spend, Impressionen, Klicks, CTR, CPC, Conversions, Conversion-Value, ROAS, Quality Score und die echten Suchanfragen, die Anzeigen ausgelöst haben.

Dieser Skill ist Teil des **First-Party-Blocks** der MTA — gemeinsam mit `03-04-seo-first-party-gsc` (Search Console) und `03-18-web-analytics-ga4` (GA4). Der Block legt die **Realitäts-Basis** aus den echten Konten des Kunden, *bevor* Third-Party-Tools (Sistrix, Ahrefs) und die Wettbewerbs-Audits laufen. Keine harte Abhängigkeit zu den anderen beiden First-Party-Skills — sie ergänzen sich, blockieren sich aber nicht.

Klare Abgrenzung zu `03-05-sea-google-ads-check`:

- **`03-05-sea-google-ads-check`** sieht via Google Ads Transparency Center nur die **öffentlich sichtbaren Anzeigen der Wettbewerber** — keine Spends, keine Klicks, keine Conversions. Wettbewerbs-Sicht von außen.
- **Dieser Skill (`03-17`)** sieht das **echte eigene Konto des Kunden** mit allen internen Performance-Daten: was kostet die Kampagne wirklich, was konvertiert, wo geht Streuverlust verloren, wie stehen die Quality Scores. First-Party-Realität von innen.

Warum First-Party-SEA wertvoll ist:

- **Transparency Center** zeigt nur, *dass* jemand Anzeigen schaltet — nie *wie gut* sie laufen.
- **Das echte Konto** zeigt die Wahrheit: Ein Kunde mit 8.000 EUR Spend und ROAS 0,9 hat ein anderes Problem als einer mit 800 EUR Spend und ROAS 6,0 — und genau diese Lesart braucht die MTA-Story.
- Die `sea-suchbegriffe.csv` ist die wertvollste Roh-Keyword-Quelle der ganzen MTA: echte Suchanfragen *mit echten Conversion-Daten*. Wo SEO-Keyword-Tools modellieren, zeigt der Search-Terms-Report, was tatsächlich konvertiert.

Die First-Party-SEA-Daten verankern mehrere Folge-Skills:
- `03-02-seo-keyword-recherche` bekommt die `sea-suchbegriffe.csv` als Seed-Pool mit echten Conversion-Signalen — Keywords, die in Ads konvertieren, sind starke SEO-Kandidaten
- `03-03-seo-keyword-kategorisierung` kann die Suchbegriffe mit kategorisieren
- `04-02-kanal-chancen-analyse` bekommt die echte SEA-Performance als Hebel-Score für den Paid-Search-Kanal
- `04-04-forecast-modell` kann mit echten CR- und CPC-Werten statt Branchen-Annahmen rechnen

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/sea-first-party.md` — Account-Kennzahlen, Kampagnen-Performance, Search-Terms-Analyse, Quality-Score-Verteilung, Conversion-Setup-Urteil, Auffälligkeiten
2. **Roh-CSVs** `audits/sea-kampagnen.csv` (Kampagnen-Ebene) + `audits/sea-suchbegriffe.csv` (Search-Terms-Ebene) — Datenbasis für die SEO- und Synthese-Folge-Skills
3. **HTML-Report** `reports/05c-sea-first-party.html` — Account-Stat-Strip, Conversion-Setup-Urteil, Top-Kampagnen, Quality-Score-Verteilung, Auffälligkeiten — die Erkenntnis-Schicht, nicht nur Tabellen-Dumps

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Konto-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Wrapper-Aufrufe, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z. B. eine vom Strategen bestätigte `customer_id`)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

**Konto-Bestätigung läuft über den Hauptthread:** Die `customer_id` steht *nicht* in `meta.json`. Der Subagent schlägt sie aus dem Kontonamen-Match vor, der Hauptthread holt die Bestätigung beim Strategen ein (siehe Schritt 2). Erst mit bestätigter `customer_id` läuft die Datenerhebung.

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

- "Google Ads First-Party"
- "Echtes Ads-Konto des Kunden auswerten"
- "Kampagnen-Performance des Kunden"
- "Wie performt das Kundenkonto"
- "Search-Terms-Report" / "Suchbegriffe-Analyse"
- "Quality Score prüfen"
- "Ads-Conversion-Setup prüfen"
- "SEA First-Party"
- "Streuverlust im Konto finden"
- "ROAS der Kampagnen"
- "Google-Ads-Audit des eigenen Kontos"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` mit `kunde`, `website`, `kunden_slug`, `region` vorhanden
- **Google-Ads-Wrapper installierbar**: `${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py` mit der `google-ads`-Python-Library (`pip3 install -r ${CLAUDE_PLUGIN_ROOT}/scripts/requirements-google.txt`)
- **Auth-Credentials**: `~/.config/reachx-mta/google-credentials.yaml` (chmod 600) mit `developer_token`, `client_id`, `client_secret`, `refresh_token`, `login_customer_id` (REACHX-MCC). Pfad überschreibbar via `REACHX_GOOGLE_CREDENTIALS`. Wird einmalig pro Mac angelegt — siehe `reference/google-ads-api-nutzung.md` Abschnitt "Auth-Setup".
- **Kunde hat ein Google-Ads-Konto unter dem REACHX-MCC** — der Wrapper sieht ~70 Konten unter dem MCC, der Skill matcht den Kundennamen aus `meta.json` gegen die Kontonamen.

**Wichtig:** Wenn die `google-credentials.yaml` fehlt, die Library nicht installiert ist oder kein Konto zur Kunden-Domain matcht → **freundlicher Skip mit Anleitung, KEIN Abbruch.** Der MTA-Workflow läuft mit `03-05-sea-google-ads-check` (Wettbewerber-Transparency-Sicht) und den übrigen Audit-Skills nahtlos weiter. First-Party-SEA ist ein **Bonus**, kein Blocker — analog zur GSC-Skip-Logik in `03-04-seo-first-party-gsc`.

**Reihenfolge — bewusst früh:** Der Skill läuft als Teil des First-Party-Blocks bewusst **früh** im MTA-Ablauf: nach den Setup-Skills (`01-01`, `01-02`, `02-01`) und idealerweise **vor `02-02-wettbewerber-identifikation`** sowie vor den Third-Party- und Wettbewerbs-Audits. Grund: Die First-Party-Outputs (echte Suchbegriffe, Kampagnen-Themen, was tatsächlich konvertiert) **schärfen die Wettbewerber-Identifikation** und verankern alle Folge-Audits an der Realität. Die einzige *harte* Voraussetzung bleibt `01-01-mta-projekt-init` — `02-02` ist ausdrücklich keine Vorbedingung, sondern profitiert umgekehrt von diesem Skill.

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

Lokaler Arbeits-Cache für Wrapper-Roh-JSONs und CSV-Generierung: `~/.cache/reachx-mta/<slug>/`.

**Wichtig:** Der Google-Ads-Wrapper-Zugang ist **unabhängig von Drive/gws** — `google-ads.py` nutzt eigene OAuth-Credentials in `~/.config/reachx-mta/google-credentials.yaml`. Die Drive-Anpassung betrifft nur die Speicher-Stellen der Outputs.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Wenn `meta.json` aus Schritt 0 fehlt oder nicht lesbar:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Prüfe in dieser Reihenfolge, ob der Wrapper einsatzbereit ist:

1. **Wrapper-Datei vorhanden** — `${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py` existiert.
2. **Credentials vorhanden** — `~/.config/reachx-mta/google-credentials.yaml` existiert (oder der via `REACHX_GOOGLE_CREDENTIALS` gesetzte Pfad).
3. **Library + Auth funktionieren** — Probe-Call `python3 google-ads.py list-accounts`. Liefert er eine Konto-Liste → Modus **direkt**.

Wenn ein Schritt scheitert → **freundlicher Skip, kein Abbruch:**

```
ℹ 03-17-sea-first-party-google-ads geskippt — Google-Ads-Zugang nicht eingerichtet.

So beheben (einmalig pro Mac):
1. Python-Library installieren:
   pip3 install -r ${CLAUDE_PLUGIN_ROOT}/scripts/requirements-google.txt
2. Credential-Datei anlegen: ~/.config/reachx-mta/google-credentials.yaml (chmod 600)
   mit developer_token, client_id, client_secret, refresh_token, login_customer_id
   (REACHX-MCC). refresh_token einmalig via google-oauth.py erzeugen.
3. Test: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/google-ads.py list-accounts
4. Diesen Skill erneut aufrufen.

Bis dahin läuft der MTA-Workflow weiter — kein Blocker. Die Wettbewerber-SEA-Sicht
liefert 03-05-sea-google-ads-check unabhängig davon.

Nächste Schritte:
1. 03-05-sea-google-ads-check — Wettbewerber-Anzeigen via Transparency Center

Sag mir, welcher als nächster.
```

Schreibe `status.md` mit Vermerk `geskippt — google_ads_zugang_fehlt` und führe einen Mini-Eintrag im "✓ Erledigt"-Block (mit Status "geskippt"). Setup-Details in `reference/google-ads-api-nutzung.md` Abschnitt "Auth-Setup".

### Schritt 2: Konto-Auffindung und Bestätigung

`meta.json` ist read-only und enthält **keine `customer_id`**. Der Skill ermittelt sie selbst.

**2.1 Re-Run-Erkennung** — Prüfe via `drive.py list-children "$AUDITS_ID"`, ob `sea-first-party.md` schon existiert. Wenn ja: lies die Datei, extrahiere `quelle.customer_id` aus dem YAML-Frontmatter und nutze sie direkt (Re-Run mit bekanntem Konto). Springe zu Schritt 3 — keine erneute Bestätigung nötig, sofern der Stratege nicht explizit ein anderes Konto wünscht.

**2.2 Konto-Liste ziehen** — `python3 google-ads.py list-accounts`. Liefert pro Konto unter dem REACHX-MCC: `customer_id`, `name`, `currency`, `is_manager`, `status` (`ENABLED` / `CANCELED` / `SUSPENDED`), `level`.

**2.3 Namens-Matching** — Matche `meta.json.kunde` (und ggf. den Host aus `meta.json.website`) gegen die `name`-Felder der Konten. Matching-Logik in `reference/google-ads-api-nutzung.md` Abschnitt "Konto-Matching":
- Token-Overlap zwischen Kundenname und Kontoname (case-insensitiv, ohne Rechtsform-Suffixe wie "GmbH", "AG")
- `is_manager: true`-Konten (Unter-MCCs) als Treffer ausschließen — gesucht ist ein operatives Werbekonto
- Bei mehreren Treffern: `status: ENABLED` priorisieren vor `CANCELED` / `SUSPENDED`

**2.4 Vorschlag und Bestätigung** — Der Subagent gibt den Hauptthread-Vorschlag zurück, der Hauptthread holt die Strategen-Bestätigung ein. Die Frage **muss erklären, warum** sie gestellt wird (beschreibende Frage):

- **Genau ein ENABLED-Treffer** → Vorschlag mit Bestätigungs-Bitte:

  ```
  Konto-Treffer für <Kunde>: "<Kontoname>" (ID <customer_id>, Status ENABLED, Währung EUR).
  Bitte bestätigen — dann ziehe ich die First-Party-Daten dieses Kontos.
  ```

- **Mehrere Treffer** → alle listen, beschreibende Rückfrage:

  ```
  Unter dem REACHX-MCC gibt es mehrere Konten, die zum Kunden <Kunde> passen:
  1. "<Name A>" (ID <id>, Status ENABLED)
  2. "<Name B>" (ID <id>, Status CANCELED)

  Welches ist das aktive Konto des Kunden? Wichtig, weil sonst die Daten eines
  gekündigten Alt-Kontos ausgewertet würden — das verfälscht die ganze SEA-Lesart.
  ```

- **Kein Treffer** → freundlicher Skip:

  ```
  ℹ 03-17-sea-first-party-google-ads geskippt — kein Google-Ads-Konto für <Kunde> gefunden.

  Unter dem REACHX-MCC sind N Konten sichtbar, aber keines matcht den Kundennamen.
  Mögliche Gründe:
  - Der Kunde betreibt (noch) kein Google-Ads-Konto
  - Das Konto liegt nicht unter dem REACHX-MCC (eigenständig oder bei anderer Agentur)
  - Der Kontoname weicht stark vom Firmennamen ab

  Wenn das Konto existiert, aber anders heißt: Skill mit Argument
  `customer_id=<10-stellige-ID>` erneut aufrufen, dann nutze ich diese direkt.

  Bis dahin läuft der MTA-Workflow weiter — kein Blocker.

  Nächste Schritte:
  1. 03-05-sea-google-ads-check — Wettbewerber-Anzeigen via Transparency Center

  Sag mir, welcher als nächster.
  ```

  Schreibe `status.md` mit Vermerk `geskippt — kein_konto_match`.

**Override:** Wenn der Stratege mit Argument `customer_id=<ID>` aufruft, überspringt der Skill das Matching und nutzt die ID direkt. Schlägt der erste Wrapper-Call mit Permission-Error fehl (Konto liegt nicht unter dem MCC), sauberer Skip wie oben.

**Hinweis CANCELED-Konten:** `list-accounts` liefert auch gekündigte Konten (`status: CANCELED`). Diese können noch historische Daten enthalten, gehören aber selten zur aktiven MTA-Story. Bei einem CANCELED-Konto als einzigem Treffer trotzdem nachfragen — der Stratege entscheidet, ob die Alt-Daten relevant sind.

### Schritt 3: Zeiträume festlegen

Der Wrapper akzeptiert `--range` als GAQL-Datums-Literal oder als expliziten Bereich `YYYY-MM-DD:YYYY-MM-DD`.

Zwei Standard-Zeiträume pro Lauf — **beide mit demselben Enddatum**, damit die Trend-Aussage "30T vs. anteiliger 12M-Schnitt" nicht durch uneinheitliche Enddaten verzerrt wird:

- **12-Monats-Range** (`zeitraum_lang`) — expliziter Bereich `<heute-365>:<heute>`. Basis für Account-Overview, Kampagnen-Performance, Search-Terms, Keyword-Performance. Zeigt das volle Jahr inkl. Saisonalität.
- **Letzte 30 Tage** (`zeitraum_kurz`) — expliziter Bereich `<heute-30>:<heute>`. Aktueller Snapshot für den Trend-Vergleich "läuft das Konto gerade?". **Bewusst NICHT das GAQL-Literal `LAST_30_DAYS`** — das endet bei `gestern`, der 12-Monats-Range aber bei `heute`. Uneinheitliche Enddaten verfälschen den Trend-Vergleich; beide Ranges nutzen darum explizite Bereiche mit identischem Enddatum.

Der Skill ruft die Performance-Befehle für beide Ranges auf und stellt im Output die 30-Tage-Werte den 12-Monats-Werten gegenüber (anteilige Hochrechnung für die Trend-Aussage).

**Daten-Latenz:** Google-Ads-Daten sind im Tagesverlauf noch nicht final (Conversions werden teils mit Verzögerung attribuiert). Beide Ranges enden bei `heute` — die letzten 1-3 Tage können sich noch leicht ändern, das ist für eine MTA-Status-Aufnahme unkritisch und betrifft beide Ranges gleich. Im Output `abgefragt_am` vermerken.

### Schritt 4: Datenerhebung

Pro Konto die Wrapper-Befehle aufrufen. Genaue Parameter und JSON-Strukturen in `reference/google-ads-api-nutzung.md`. **Geld kommt vom Wrapper bereits normalisiert** — die `google-ads.py`-CLI rechnet Micros in Währungs-Einheiten um (`_eur()`) und liefert das `currency`-Feld pro Antwort mit. **Werte unverändert übernehmen**, keine eigene Micros-Umrechnung.

**4.1 Account-Overview** (beide Ranges)

```bash
python3 google-ads.py account-overview <customer_id> --range <heute-365>:<heute>
python3 google-ads.py account-overview <customer_id> --range <heute-30>:<heute>
```

Liefert ein Aggregat: `cost`, `impressions`, `clicks`, `conversions`, `conversions_value`, `ctr`, `avg_cpc`, `currency`. ROAS lokal berechnen: `conversions_value / cost` — das Feld bleibt **leer** (nicht 0), wenn `cost = 0` (Division durch Null), konsistent zu `reference/sea-analyse-methodik.md`.

**4.2 Kampagnen-Performance** (beide Ranges)

```bash
python3 google-ads.py campaign-performance <customer_id> --range <heute-365>:<heute>
python3 google-ads.py campaign-performance <customer_id> --range <heute-30>:<heute>
```

Liefert pro Kampagne: `campaign_id`, `campaign`, `status`, `channel_type` (`SEARCH` / `DISPLAY` / `VIDEO` / `SHOPPING` / `DEMAND_GEN` / `PERFORMANCE_MAX` / ...), `cost`, `impressions`, `clicks`, `conversions`, `conversions_value`, `ctr`, `avg_cpc`. Bereits nach Kosten absteigend sortiert. Roh-JSON nach `~/.cache/reachx-mta/<slug>/audits/raw/sea-campaign-performance-<range>.json`.

**4.3 Search-Terms** (12-Monats-Range)

```bash
python3 google-ads.py search-terms <customer_id> --range <heute-365>:<heute> --limit 300
```

Liefert die echten Suchanfragen, die Anzeigen ausgelöst haben: `search_term`, `status` (`ADDED` / `EXCLUDED` / `NONE` / `ADDED_EXCLUDED`), `campaign`, `impressions`, `clicks`, `conversions`, `cost`, `ctr`. Default-Limit 300, bei sehr großen Konten bis 1.000 hochsetzen. Roh-JSON nach `audits/raw/sea-search-terms.json`.

**4.4 Keyword-Performance inkl. Quality Score** (12-Monats-Range)

```bash
python3 google-ads.py keyword-performance <customer_id> --range <heute-365>:<heute> --limit 300
```

Liefert pro Keyword: `keyword`, `match_type` (`EXACT` / `PHRASE` / `BROAD`), `quality_score` (1-10 oder `null` wenn nicht vergeben), `campaign`, `impressions`, `clicks`, `conversions`, `cost`, `avg_cpc`. Roh-JSON nach `audits/raw/sea-keyword-performance.json`.

**4.5 Conversion-Actions**

```bash
python3 google-ads.py conversion-actions <customer_id>
```

Liefert alle definierten Conversion-Actions: `id`, `name`, `status` (`ENABLED` / `REMOVED` / `HIDDEN`), `type` (`WEBPAGE`, `GOOGLE_ANALYTICS_4_*`, `UPLOAD_CLICKS`, `WEBSITE_CALL`, ...), `category` (`PURCHASE`, `LEAD`, `SUBMIT_LEAD_FORM`, `PAGE_VIEW`, `CONTACT`, ...), `counting_type`, `primary_for_goal`. Roh-JSON nach `audits/raw/sea-conversion-actions.json`. Basis für den Conversion-Plausibilitäts-Check in Schritt 5.

**API-Budget:** Der Wrapper nutzt die kostenlose Google-Ads-API. Pro Skill-Lauf typisch 8-12 Wrapper-Calls (je 1 GAQL-Query). Das Standard-Developer-Token-Limit (Basic Access: 15.000 Operationen/Tag) wird weit unterschritten. Details in `reference/google-ads-api-nutzung.md` Abschnitt "API-Budget".

### Schritt 5: Conversion-Plausibilitäts-Check

Ein **leichter Inline-Check** — das schlanke Pendant zum vollen GA4-Datenqualitäts-Gate, das `03-18-web-analytics-ga4` zweiphasig führt. Hier KEIN eigenes Schema-vor-Lauf, sondern eine Inline-Bewertung, deren Ergebnis als kurzer Abschnitt im Output und als Auffälligkeit landet.

Aus den `conversion-actions`-Daten prüfen (Regeln in `reference/sea-analyse-methodik.md` Abschnitt "Conversion-Plausibilitäts-Check"):

1. **Gibt es überhaupt eine ENABLED-Conversion?** — Wenn keine einzige `status: ENABLED`-Conversion existiert, misst das Konto nichts. Conversion-Zahlen aus `account-overview` sind dann nicht vertrauenswürdig → Auffälligkeit `conversion_tracking_fehlt`, Urteil `kein_tracking`.

2. **GA4-importierte Conversions** — Conversion-Actions mit `type` aus der `GOOGLE_ANALYTICS_4_*`-Familie sind aus GA4 importiert. Wenn das Konto sowohl GA4-importierte als auch native (`WEBPAGE`) Conversion-Actions für dieselbe Aktion zählt, droht **Doppelzählung** — Conversion-Zahlen können überzeichnet sein. → Auffälligkeit `conversion_aus_ga4_importiert`, Hinweis für `03-18-web-analytics-ga4`-Cross-Check.

3. **Macro-/Micro-Mix** — Wenn `primary_for_goal: true` sowohl für eine harte Conversion (`category: PURCHASE` / `LEAD`) als auch für eine weiche (`category: PAGE_VIEW`) gesetzt ist, mischt das Konto Macro- und Micro-Conversions in der Haupt-Zielmessung. Das verzerrt ROAS und CR. → Auffälligkeit `conversion_macro_micro_gemischt`.

4. **Verwaiste REMOVED-Actions** — Viele `status: REMOVED`-Actions sind unkritisch (normaler Lifecycle), aber wenn die *einzige* je definierte Conversion REMOVED ist, deckt sich das mit Punkt 1.

**Conversion-Setup-Urteil** als ein Wert: `sauber` / `mit_einschraenkung` / `kein_tracking`. Geht ins Frontmatter (`conversion_setup_urteil`), als kurzer Abschnitt in den Body und prominent in den HTML-Report.

**Wenn nach dem Check eine inhaltliche Unklarheit bleibt** (z. B. unklar, ob eine GA4-importierte Conversion bewusst die native ersetzt oder additiv läuft), formuliert der Skill **eine** beschreibende Strategen-Frage — sie muss erklären, warum sie wichtig ist:

```
Das Konto zählt sowohl eine native Webseiten-Conversion ("Kontaktformular") als auch
eine GA4-importierte Conversion ("Lead GA4"). Werden beide additiv in der Zielmessung
gezählt? Wichtig, weil sonst die Conversion-Zahl und damit der ROAS doppelt so hoch
erscheinen wie real — das würde die ganze SEA-Wirtschaftlichkeits-Aussage verzerren.
```

Die Frage geht über den Subagent-Rückgabe-Status an den Hauptthread. Der Skill schreibt die Outputs trotzdem (mit der Annahme als Default), markiert die Annahme aber als offenen Punkt.

### Schritt 6: Kern-Analysen

Methodik-Details, Schwellwerte und Heuristiken in `reference/sea-analyse-methodik.md`.

**6.1 Account- und Kampagnen-Performance**

- Account-Aggregat 12 Monate vs. letzte 30 Tage — Spend, Impressionen, Klicks, CTR, CPC, Conversions, Conversion-Value, ROAS.
- ROAS pro Kampagne: `conversions_value / cost`. CR pro Kampagne: `conversions / clicks`. CPA pro Kampagne: `cost / conversions`.
- **Kampagnentyp-Mix** — Spend-Anteil je `channel_type` (Search/Display/Video/Shopping/Demand Gen/Performance Max). Zeigt, wo das Budget liegt.
- **Budget-Konzentration** — Wenn eine einzelne Kampagne ≥ 60 % des Gesamt-Spends bindet → Auffälligkeit `budget_konzentration`.
- **Kampagnen ohne Conversions** — ENABLED-Kampagnen mit Spend > 0 und 0 Conversions über 12 Monate → Auffälligkeit `kampagne_ohne_conversions`.

**6.2 Search-Terms-Analyse**

Die echten Suchanfragen aus `search-terms`. Pro Suchbegriff bewerten:

- **Streuverlust-Hinweise** — Suchbegriffe mit Kosten, aber 0 Conversions und thematisch irrelevant (Heuristik in der Methodik-Datei). Hoher Streuverlust-Anteil → Auffälligkeit `hoher_streuverlust_suchbegriffe`.
- **Brand vs. Non-Brand** — Token-Match des Suchbegriffs gegen den Kundennamen (gleiche Brand-Detection wie in `03-04`-Methodik). Brand-Anteil am Spend und an den Conversions. Sehr hoher Brand-Anteil → Auffälligkeit `brand_anteil_hoch` (das Konto erntet vor allem bestehende Nachfrage, statt neue zu erschließen).
- **Status der Suchbegriffe** — `ADDED` (als Keyword übernommen), `EXCLUDED` (negativ ausgeschlossen), `NONE` (weder/noch — Kandidaten-Pool).

Die `sea-suchbegriffe.csv` wird in Schritt 7 geschrieben — sie ist **explizit auch Roh-Keyword-Quelle für `03-02-seo-keyword-recherche` und `03-03-seo-keyword-kategorisierung`**: echte Suchanfragen mit echten Conversion-Daten sind die hochwertigste Seed-Liste, die eine MTA bekommen kann. Im Output und im CSV-Schema entsprechend dokumentieren.

**6.3 Quality-Score-Verteilung**

Aus `keyword-performance`. Quality Score 1-10 (oder `null` wenn nicht vergeben — bei zu wenig Impressionen).

- Verteilung in Bins: schwach (1-4), mittel (5-7), stark (8-10).
- Schwellwerte und Spend-Gewichtung in `reference/sea-analyse-methodik.md` Abschnitt "Quality-Score-Schwellwerte".
- Wenn ein relevanter Spend-Anteil auf Keywords mit QS 1-4 entfällt → Auffälligkeit `quality_score_schwach` (Optimierungs-Hebel: schwacher QS treibt CPC hoch).

**6.4 Conversion-Setup**

Das Ergebnis des Plausibilitäts-Checks aus Schritt 5 — als Abschnitt mit dem Urteil und der Begründung.

### Schritt 7: CSV-Outputs

**`audits/sea-kampagnen.csv`** — Kampagnen-Ebene. Eine Zeile je Kampagne × Zeitraum, damit Folge-Skills sowohl 12-Monats- als auch 30-Tage-Werte lesen können.

Spalten (vollständiges Schema in `reference/sea-output-schema.md`):

```
campaign_id,campaign,status,channel_type,zeitraum,datum_von,datum_bis,cost,currency,impressions,clicks,ctr,avg_cpc,conversions,conversions_value,roas,cpa,cr
```

**`audits/sea-suchbegriffe.csv`** — Search-Terms-Roh-Daten. Eine Zeile je Suchbegriff (12-Monats-Range).

Spalten:

```
search_term,status,campaign,impressions,clicks,ctr,cost,currency,conversions,ist_brand,streuverlust_flag
```

`ist_brand` (boolean) und `streuverlust_flag` (boolean) werden vom Skill aus der Analyse in Schritt 6.2 gesetzt. Diese CSV ist die Übergabe-Schnittstelle an die SEO-Keyword-Skills — Header und Semantik nicht ohne Versions-Bump ändern.

### Schritt 8: Aggregat-Markdown `audits/sea-first-party.md`

Format mit YAML-Frontmatter nach `reference/sea-output-schema.md` Abschnitt "Markdown-Schema". Frontmatter enthält:

- Skill-Metadaten, Recherche-Provenienz (`customer_id`, Kontoname, Währung, Zeiträume, `abgefragt_am`)
- `statistiken_12_monate` (cost, impressions, clicks, ctr, avg_cpc, conversions, conversions_value, roas)
- `statistiken_30_tage` (gleiche Felder, aktueller Snapshot)
- `conversion_setup_urteil` (`sauber` / `mit_einschraenkung` / `kein_tracking`) plus `conversion_actions_anzahl`, `conversion_actions_enabled`
- `kampagnentyp_mix` (Spend-Anteil je channel_type)
- `quality_score_verteilung` (Anteil schwach/mittel/stark)
- `search_terms_kennzahlen` (anzahl_suchbegriffe, brand_anteil_spend, streuverlust_anteil_spend)
- `auffaelligkeiten` (Liste der strategischen Beobachtungen, siehe Schritt 9)

Body strukturiert nach:

1. **Übersicht** (3-5 Sätze: welches Konto, Spend-Größenordnung, ROAS-Lesart, wo die größten Hebel liegen, Conversion-Setup-Urteil als Vertrauens-Disclaimer)
2. **Account-Performance** (12-Monats-Aggregat vs. letzte 30 Tage, Tabelle)
3. **Kampagnen-Performance** (Tabelle je Kampagne, sortiert nach Spend, mit ROAS/CPA/CR)
4. **Kampagnentyp-Mix** (Spend-Verteilung je channel_type)
5. **Search-Terms-Analyse** (Top-Suchbegriffe nach Spend, Brand-vs-Non-Brand-Split, Streuverlust-Block)
6. **Quality-Score-Verteilung** (Bin-Verteilung, schwächste Keywords nach Spend)
7. **Conversion-Setup** (Plausibilitäts-Check-Ergebnis mit Urteil und Begründung)
8. **Auffälligkeiten** (aus Frontmatter, sortiert nach Relevanz)
9. **Lücken und Hinweise** (Datenbasis dünn? Konto neu? Offene Strategen-Frage aus Schritt 5?)

### Schritt 9: Auffälligkeiten

Strategische Beobachtungen extrahieren, analog `03-04-seo-first-party-gsc` Schritt 8:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `conversion_tracking_fehlt` | keine einzige ENABLED-Conversion-Action | "Das Konto misst keine Conversions — alle ROAS/CPA-Aussagen aus der API sind nicht belastbar. Tracking-Setup ist der erste Hebel." |
| `conversion_aus_ga4_importiert` | GA4-importierte und native Conversions parallel | "Conversions kommen teils aus GA4-Import — mögliche Doppelzählung mit nativem Tracking. Vor Forecast bereinigen, Cross-Check mit 03-18." |
| `conversion_macro_micro_gemischt` | Macro- und Micro-Conversion beide `primary_for_goal` | "Haupt-Zielmessung mischt Käufe und Seitenaufrufe — ROAS ist dadurch verzerrt. Zielmessung auf Macro-Conversion fokussieren." |
| `hoher_streuverlust_suchbegriffe` | Streuverlust-Spend-Anteil ≥ Schwelle (Methodik) | "Ein relevanter Spend-Anteil fließt in irrelevante Suchanfragen — Negativ-Keyword-Pflege als Quick-Win." |
| `quality_score_schwach` | relevanter Spend-Anteil auf QS-1-4-Keywords | "Schwache Quality Scores treiben den CPC hoch — Anzeigen-Relevanz und Landingpages als Optimierungs-Hebel." |
| `kampagne_ohne_conversions` | ENABLED-Kampagne mit Spend, 0 Conversions/12M | "Kampagne X verbrennt Budget ohne messbare Conversion — pausieren oder Tracking prüfen." |
| `budget_konzentration` | eine Kampagne bindet ≥ 60 % des Spends | "Über die Hälfte des Budgets liegt auf einer Kampagne — Klumpenrisiko, Diversifizierung prüfen." |
| `brand_anteil_hoch` | Brand-Spend-Anteil ≥ Schwelle (Methodik) | "Ein großer Teil des Spends erntet Brand-Suchen — das Konto sichert bestehende Nachfrage, erschließt aber wenig neue. Non-Brand-Ausbau prüfen." |
| `roas_unter_eins` | Account-ROAS 12M < 1,0 (bei vertrauenswürdigem Tracking) | "Der Account macht über 12 Monate weniger Umsatz als er kostet — grundsätzliche Wirtschaftlichkeits-Frage für die MTA-Story." |
| `konto_inaktiv` | Spend letzte 30 Tage = 0, aber 12M-Spend > 0 | "Das Konto läuft aktuell nicht — Kampagnen pausiert. Klären, ob bewusst oder vergessen." |

Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch` / `mittel` / `niedrig`), Handlungs-Empfehlung.

### Schritt 10: HTML-Report `reports/05c-sea-first-party.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html` bauen. Nummer `05c` — GSC-First-Party ist `05a`, GA4-First-Party (`03-18-web-analytics-ga4`) ist `05b`, dieser SEA-First-Party-Skill ist `05c`. Damit stehen die drei First-Party-Audits im Dashboard zusammen vor den Third-Party-Audits.

**Wichtig (User-Vorgabe):** Der HTML-Report trägt die wichtigsten **Erkenntnisse**, nicht nur Tabellen-Dumps. CSV = Maschinen-Schicht, HTML = Interpretations-Schicht. Conversion-Setup-Urteil, Top-Kampagnen, Quality-Score-Verteilung und Auffälligkeiten stehen prominent.

Platzhalter:

- `{{TITLE}}` → `SEA First-Party (Google Ads) · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · SEA First-Party`
- `{{DISPLAY_NAME}}` → `SEA First-Party-Daten aus dem Google-Ads-Konto: KUNDE`
- `{{META_LINE}}` → `Quelle: Google Ads API via google-ads.py · Konto: <Kontoname> (<customer_id>) · Zeitraum: 12 Monate · Generiert: <heute>`
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip oben**: Spend/12M, Klicks/12M, Conversions/12M, ROAS, Avg-CPC, Avg-CTR, 30-Tage-Trend (Spend-Pfeil)
  - **Conversion-Setup-Urteil** prominent als `.summary-card` direkt unter dem Stat-Strip — ein Badge (`stark` = sauber, `mittel` = mit Einschränkung, `schwach` = kein Tracking) plus ein bis zwei Sätze Begründung. Das ist der Vertrauens-Disclaimer für alle ROAS-Zahlen darunter.
  - **Sticky-TOC**: Account-Performance, Kampagnen, Kampagnentyp-Mix, Search-Terms, Quality Score, Conversion-Setup, Auffälligkeiten
  - **Account-Performance** als `table.data` (12 Monate vs. 30 Tage gegenübergestellt)
  - **Top-Kampagnen** als `table.data`, sortiert nach Spend, mit ROAS-Badge pro Zeile (`stark` ROAS ≥ 3, `mittel` 1-3, `schwach` < 1) — Top-Kampagnen prominent
  - **Kampagnentyp-Mix** als kleine Balken-Visualisierung (Spend-Anteil je channel_type)
  - **Search-Terms** als Tabelle der Top-Suchbegriffe nach Spend, plus Brand-vs-Non-Brand-Hinweis-Card und Streuverlust-Block. Hinweis-Card: die `sea-suchbegriffe.csv` ist Roh-Keyword-Quelle für die SEO-Skills.
  - **Quality-Score-Verteilung** als 3-Bin-Balken-Visualisierung (schwach/mittel/stark, spend-gewichtet)
  - **Auffälligkeiten** als `.suggestion`-Block mit den Top-Beobachtungen, sortiert nach Relevanz
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · SEA-First-Party-Audit`
- `{{TOKEN_FOOTER}}` → Skill-Counter (siehe Token-Tracking)

`<body>` ohne Klasse → Back-Link zum Dashboard sichtbar (siehe `contracts.md` Abschnitt 7).

### Schritt 11: Outputs nach Drive hochladen

Finale Outputs via `drive.py upsert-text` nach Drive (idempotent):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "sea-first-party.md" \
  ~/.cache/reachx-mta/<slug>/sea-first-party.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "sea-kampagnen.csv" \
  ~/.cache/reachx-mta/<slug>/sea-kampagnen.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "sea-suchbegriffe.csv" \
  ~/.cache/reachx-mta/<slug>/sea-suchbegriffe.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "05c-sea-first-party.html" \
  ~/.cache/reachx-mta/<slug>/05c-sea-first-party.html "text/html"
```

CSV bleibt CSV (kein Auto-Convert zu Google Sheet). Roh-JSONs aus `~/.cache/reachx-mta/<slug>/audits/raw/` am Ende komprimiert nach Drive `assets/raw/`.

### Schritt 12: Dashboard-Update

`reports/index.html` aus Drive lesen, anpassen, zurückschreiben:

```bash
INDEX_ID=$(python3 "$DRIVE_PY" list-children "$REPORTS_ID" | jq -r '.[] | select(.name == "index.html") | .id')
python3 "$DRIVE_PY" read "$INDEX_ID" > /tmp/index.html
# … HTML anpassen …
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "index.html" /tmp/index.html "text/html"
```

Aktualisiere `reports/index.html`:

- Stat-Strip um SEA-12M-Spend und ROAS ergänzen
- "Erledigt"-Sektion erweitern um `03-17-sea-first-party-google-ads`
- Reports-Liste um `05c-sea-first-party.html` erweitern
- Stufe 3 als "in Arbeit" markieren
- Token-Breakdown-Slots aktualisieren (siehe `contracts.md` Sektion 10)
- "Nächster empfohlener Schritt": `03-05-sea-google-ads-check` (ergänzt die First-Party-Sicht um den Wettbewerber-Benchmark)

### Schritt 13: `status.md` aktualisieren

Aus Drive lesen, anpassen, zurückschreiben:

```bash
STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > /tmp/status.md
# … Frontmatter+Body anpassen …
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"
```

Nach Regeln aus `contracts.md` Abschnitt 3:

- `03-17-sea-first-party-google-ads` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, kompakten Highlight-Numbers (Spend/12M, ROAS, Conversion-Setup-Urteil)
- `naechster_empfohlen`: zuerst die noch nicht gelaufenen First-Party-Skills — `03-04-seo-first-party-gsc`, dann `03-18-web-analytics-ga4`; danach `02-02-wettbewerber-identifikation` (nutzt die First-Party-Outputs zur Schärfung der Wettbewerber-Auswahl). Erst wenn der First-Party-Block und `02-02` durch sind: `03-05-sea-google-ads-check` und die übrigen Third-Party-Audits. Bereits gelaufene First-Party-Skills überspringen.
- Bei `conversion_tracking_fehlt` oder `roas_unter_eins`: explizit als Hinweis "in MTA-Story als Schwerpunkt einplanen"
- Bei offener Strategen-Frage aus Schritt 5: Eintrag unter "✗ Blockiert" ist NICHT nötig (der Skill läuft durch), aber ein Vermerk unter "Hinweise" der Erledigt-Sektion

### Schritt 14: Standard-Schlussformat im Chat

```
✓ 03-17-sea-first-party-google-ads abgeschlossen.

Outputs (auf Drive):
- audits/sea-first-party.md — Aggregat mit Kampagnen-Performance, Search-Terms, Conversion-Check
- audits/sea-kampagnen.csv — Kampagnen-Ebene (N Zeilen)
- audits/sea-suchbegriffe.csv — Search-Terms-Roh-Daten (M Zeilen), auch Roh-Keyword-Quelle für 03-02/03-03
- reports/05c-sea-first-party.html — visueller First-Party-SEA-Audit
Status aktualisiert in: status.md

Konto: <Kontoname> (<customer_id>)

SEA-Highlights (12 Monate):
- Spend:                XXX EUR
- Klicks:               XXX
- Conversions:          XXX
- ROAS:                 X,X
- Avg-CPC:              X,XX EUR
- Avg-CTR:              X,X%
- Trend 30 Tage:        <Spend +/- Z% ggü. 12M-Schnitt>

Conversion-Setup: <sauber | mit Einschränkung | kein Tracking>
- <ein Satz Begründung aus dem Plausibilitäts-Check>

Gefundene Hebel:
- Kampagnentyp-Mix:     <z. B. 70% Search, 20% PMax, 10% Display>
- Streuverlust:         <Anteil Spend in irrelevanten Suchbegriffen>
- Quality Score schwach: <Anteil Spend auf QS 1-4>
- Brand-Anteil:         <Brand-Spend-Anteil>

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- (1-3 Punkte aus der Auffälligkeiten-Liste, sortiert nach Relevanz)

[Wenn offene Strategen-Frage aus dem Conversion-Check:]
? Offene Frage:
- <die beschreibende Frage aus Schritt 5 — wirkt nur auf die Belastbarkeit der Conversion-Zahlen>

Nächste Schritte:
1. 03-04-seo-first-party-gsc — restlicher First-Party-Block (Search Console), falls noch nicht gelaufen
2. 03-18-web-analytics-ga4 — restlicher First-Party-Block (GA4), schließt die Datenqualitäts-Lücke beim Conversion-Tracking
3. 02-02-wettbewerber-identifikation — danach: nutzt die First-Party-Outputs (echte Suchbegriffe, Kampagnen-Themen) zur Schärfung der Wettbewerber-Auswahl
4. (nachgelagert) 03-05-sea-google-ads-check — Wettbewerber-Anzeigen via Transparency Center, ergänzt die First-Party-Sicht um den Markt-Benchmark
5. (nachgelagert) 03-02-seo-keyword-recherche — nutzt sea-suchbegriffe.csv als Seed-Pool mit echten Conversion-Daten

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/google-ads-api-nutzung.md` — `google-ads.py`-Befehle, Parameter, `--range`-Format, Micros/Währungs-Hinweis, Auth-Setup, Konto-Matching, API-Budget, Edge-Cases
- `reference/sea-output-schema.md` — CSV-Spalten + Markdown-Frontmatter-Schema, Validierungs-Regeln, wie Folge-Skills die Outputs lesen
- `reference/sea-analyse-methodik.md` — Conversion-Plausibilitäts-Check-Regeln, Streuverlust-Heuristik, Quality-Score-Schwellwerte, ROAS/CPA/CR-Formeln, Auffälligkeiten-Schwellwerte

## Edge Cases

- **Google-Ads-Zugang nicht eingerichtet** (Wrapper/Library/Credentials fehlen) → freundlicher Skip mit Setup-Anleitung (Schritt 1). KEIN Abbruch des MTA-Workflows. `status.md` markiert den Skill als geskippt mit Grund.

- **Kein Konto-Match** → freundlicher Skip (Schritt 2.4). Skill nennt die Override-Option `customer_id=<ID>`. `status.md`-Vermerk `geskippt — kein_konto_match`.

- **Mehrere Konto-Treffer** → beschreibende Rückfrage über den Hauptthread (Schritt 2.4), die erklärt, warum ein gekündigtes Alt-Konto die Lesart verfälschen würde. Niemals raten.

- **Konto ist CANCELED/SUSPENDED** → der Skill kann es auswerten (historische Daten sind oft noch da), nennt den Status aber im Konto-Vorschlag und fragt nach. Im Output `konto_status` im Frontmatter.

- **Konto läuft aktuell nicht** (Spend letzte 30 Tage = 0, aber 12M-Spend > 0) → Skill läuft durch, Auffälligkeit `konto_inaktiv`, Hinweis im Schluss-Format.

- **Konto ganz ohne Spend** (12M-Spend = 0 bei einem ENABLED-Konto) → das Konto existiert, hat aber nie Budget verbraucht. Skill schreibt minimale Outputs, `daten_qualitaet: keine`, Hinweis "Konto angelegt, aber inaktiv — keine SEA-Historie auswertbar".

- **Kein Conversion-Tracking** → Auffälligkeit `conversion_tracking_fehlt`, Conversion-Setup-Urteil `kein_tracking`. Skill schreibt alle Performance-Daten trotzdem, markiert ROAS/CPA/CR aber als "nicht belastbar" — die Conversion-API liefert dann 0 oder verzerrte Werte.

- **GA4-importierte Conversions** → Conversion-Setup-Urteil mindestens `mit_einschraenkung`, Auffälligkeit `conversion_aus_ga4_importiert`, Cross-Check-Hinweis für `03-18-web-analytics-ga4`. Wenn Unklarheit bleibt: beschreibende Strategen-Frage (Schritt 5).

- **Sehr großes Konto** (Search-Terms-Report > 1.000 Zeilen) → `--limit` auf 1.000 hochsetzen; bei noch mehr in `reference/google-ads-api-nutzung.md` beschriebenes Paging via `run-gaql` mit Datums-Segmentierung. CSV bei sehr großen Konten auf Top-1.000 nach Impressionen kappen, Hinweis im Body.

- **Nicht-EUR-Konto** → der Wrapper liefert die Konto-Währung im `currency`-Feld. Werte unverändert übernehmen, Währung überall mit ausweisen. KEINE eigene Umrechnung — Synthese-Skills (`04-04-forecast-modell`) entscheiden über Normalisierung.

- **Währung uneinheitlich** (unwahrscheinlich unter einem MCC, aber möglich) → der Skill nimmt die `currency` aus `account-overview` als Konto-Währung; wenn ein Kampagnen-Call abweicht, Hinweis im Body.

- **Quality Score überall `null`** (Konto zu klein / zu wenig Impressionen pro Keyword) → Quality-Score-Verteilung wird ausgelassen, Hinweis "QS für die meisten Keywords nicht vergeben — Datenbasis zu dünn". Keine `quality_score_schwach`-Auffälligkeit.

- **CSV/Markdown existiert bereits** (Re-Run) → Skill liest die `customer_id` aus dem vorhandenen `sea-first-party.md`-Frontmatter (Schritt 2.1) und fragt analog `03-04`:
  - **(a) überschreiben**
  - **(b) Backup-und-neu** — alte Versionen nach `audits/_backup/sea-*-<ISO>.csv` / `.md`
  - **(c) abbrechen**

- **API-Rate-Limit / 5xx** → der Wrapper gibt den lesbaren API-Fehler aus (`_explain()`). Bei transientem Fehler 30-60s warten, einmal retry. Bei wiederholtem Limit: bisher erhobene Daten schreiben, Rest als offen markieren, Hinweis im Schluss-Format.

- **OAuth-Refresh-Token abgelaufen/revoked** → der Wrapper-Call schlägt mit Auth-Fehler fehl. Hinweis "Refresh-Token ungültig — bitte einmal `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/google-oauth.py` ausführen und `refresh_token` in der `google-credentials.yaml` aktualisieren". Skill bricht für diesen Lauf sauber ab (kein MTA-Abbruch), `status.md`-Vermerk `geskippt — auth_fehlgeschlagen`.

- **Abgrenzung zu `03-05`** → läuft `03-05-sea-google-ads-check` parallel, ist das kein Konflikt: `03-05` sieht die Wettbewerber von außen (Transparency Center), `03-17` sieht das Kundenkonto von innen. `04-02-kanal-chancen-analyse` kombiniert beide. Der Skill produziert KEINE Wettbewerber-Daten — First-Party ist konto-only.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/sea-first-party.md`)
- Markdown + YAML-Frontmatter für `sea-first-party.md`, CSV für `sea-kampagnen.csv` und `sea-suchbegriffe.csv` (via `drive.py upsert-text`)
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (auch bei Skip), via `drive.py upsert-text`
- HTML-Report basiert auf `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **Wrapper-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/sea-*.json`, am Ende komprimiert nach Drive `assets/raw/`
- **Google-Ads-Auth ist unabhängig von gws** — der `google-ads.py`-Wrapper nutzt eigene OAuth-Credentials in `~/.config/reachx-mta/google-credentials.yaml`, separat von der Drive-Authentifizierung
- **Geld-Werte unverändert lassen** — der Wrapper normalisiert Micros bereits in Konto-Währungs-Einheiten und liefert `currency` mit. Keine eigene Umrechnung, keine Währungs-Konvertierung — das ist Aufgabe der Synthese-Skills
- **First-Party vs. Third-Party**: Dieser Skill ist das First-Party-Pendant zu `03-05-sea-google-ads-check`. `03-05` = Wettbewerber öffentlich, `03-17` = eigenes Konto echt. Beide ergänzen sich in `04-02-kanal-chancen-analyse`
- **Conversion-Plausibilitäts-Check ist ein Inline-Check**, kein zweiphasiges Schema-vor-Lauf-Gate. Das volle Datenqualitäts-Gate führt der Schwester-Skill `03-18-web-analytics-ga4`
