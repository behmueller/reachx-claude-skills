---
name: 03-18-web-analytics-ga4
description: Erhebt für den Kunden den first-party-Web-Analytics-Status-Quo direkt aus dessen echter GA4-Property über den dedizierten Helper google-analytics.py (OAuth-User-Credentials gegen einen zentralen Agentur-Account, dieselbe Datei wie google-ads.py) - 12-Monats-Sitzungsverlauf, Kanal-Performance UND Kanal-Wertigkeit (Sessions, Conversion-Rate, Umsatz, Engagement pro Channel), source/medium-Analyse inklusive unüblicher Kanäle (Preisvergleich, Bewertungsportale), Conversion-Baseline, Top-Pages, Device- und Geo-Splits. Liefert die echten Nutzungsdaten des Kunden als Forecast-Anker. Läuft zweiphasig - Phase A ist ein Datenqualitäts-Gate, das Conversion-Tracking, Direct-Last-Attribution, GA4↔GSC-Abweichung und Datenhistorie prüft, BEVOR irgendwelche Zahlen weitergegeben werden, und stoppt mit beschreibenden Strategen-Fragen; Phase B führt nach Bestätigung die volle Erhebung durch und leitet ein belastbarkeit-Urteil (grün/gelb/rot) ab. Output ist audits/ga4-datenqualitaet.md (Gate), audits/ga4-first-party.md mit Aggregat plus Conversion-Baseline, audits/ga4-channels.csv und audits/ga4-pages.csv als Roh-Basis, plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext GA4-Daten, Web-Analytics, echte Nutzungsdaten oder die Conversion-Realität des Kunden ziehen will - auch bei Phrasen wie "GA4-Daten", "Web-Analytics auswerten", "Google Analytics ziehen", "Analytics-Datenqualität prüfen", "Conversion-Tracking checken", "Conversion-Rate des Kunden", "Kanal-Performance GA4", "Kanal-Wertigkeit", "first-party-Analytics", "echte Sessions", "Forecast-Baseline aus Analytics", "Direct-Traffic-Anomalie", "Consent-Verlust prüfen". Setzt 01-01-mta-projekt-init voraus; empfiehlt 03-14-web-tech-und-tracking und 03-04-seo-first-party-gsc vorab, aber keine harte Abhängigkeit. Bei fehlenden google-credentials.yaml oder nicht zugänglicher Property freundlicher Skip mit Anleitung, KEIN Abbruch des MTA-Workflows.
---

# Web-Analytics-First-Party (GA4)

**First-Party-Web-Analytics-Skill in Stufe 3** (Kanal-Audits), Schwester-Skill zu `03-04-seo-first-party-gsc` (GSC) und `03-17-sea-first-party-google-ads` (Google Ads). Erhebt aus der **echten GA4-Property des Kunden** über den Helper `${CLAUDE_PLUGIN_ROOT}/scripts/google-analytics.py` (OAuth-User-Credentials gegen einen zentralen Agentur-Account) den first-party-Nutzungs-Status-Quo: Sessions, Nutzer, Kanäle, Conversions, Top-Pages — die einzigen echten Verhaltensdaten, die zeigen, was auf der Kunden-Website tatsächlich passiert.

Dieser Skill ist Teil des **First-Party-Blocks** der MTA (`03-04-seo-first-party-gsc` für GSC, `03-18-web-analytics-ga4` für GA4, `03-17-sea-first-party-google-ads` für Google Ads). Der Block legt die Realitäts-Basis aus den echten Konten des Kunden — und läuft bewusst früh, **bevor** Third-Party-Tools (Sistrix, Ahrefs) und die Wettbewerbs-Audits ihre modellierten Außensichten beisteuern. Keine harte Abhängigkeit zwischen den drei Skills; sie ergänzen sich, jeder läuft auch allein.

Warum first-party-GA4 im MTA-Workflow?

- **Third-Party-Tools** (Sistrix, Ahrefs, Ad-Libraries) modellieren von außen — Sichtbarkeit, Anzeigen-Aktivität, geschätzten Traffic. Sie sehen nie, ob ein Besucher konvertiert.
- **GA4** = die Verhaltens-Realität. Zeigt, welche Kanäle Sessions liefern, welche Sessions in Conversions münden, wie wertvoll SEO- vs. Paid- vs. anderer Traffic wirklich ist.

Die GA4-Daten verankern die Synthese-Skills:
- `04-04-forecast-modell` bekommt die echte Conversion-Baseline (CR pro Kanal, Sessions/Monat, AOV) statt reiner Branchen-Benchmarks
- `04-02-kanal-chancen-analyse` kann Kanal-Volumen gegen Kanal-Wertigkeit stellen ("viel Traffic, aber 0,3 % CR")
- `04-03-ziele-aus-potenzialen` startet von der echten Ist-Conversion-Rate

**Kern-Besonderheit: Datenqualitäts-Gate.** Kunden haben GA4 oft fehlerhaft aufgesetzt — Pageviews fälschlich als Conversion getaggt, Consent-Verluste durch Cookie-Banner, fehlendes UTM-Tagging. Würde der Skill diese Zahlen ungeprüft weitergeben, zöge der Forecast falsche Schlüsse. Deshalb läuft der Skill **zweiphasig**: Phase A prüft die Datenqualität und stoppt mit Strategen-Fragen, Phase B erhebt erst nach Bestätigung die volle Datenbasis und führt überall ein `belastbarkeit`-Urteil (grün/gelb/rot) mit.

Vier Output-Ebenen:

1. **Gate-Datei** `audits/ga4-datenqualitaet.md` — Phase A schreibt sie mit Auto-Befunden und Strategen-Fragen; Phase B liest sie nach Bestätigung.
2. **Aggregat-Markdown** `audits/ga4-first-party.md` — Performance-Übersicht, Kanal-Wertigkeit, Conversion-Baseline, GA4↔GSC-Abgleich, source/medium-Analyse, Auffälligkeiten — mit `belastbarkeit` im Frontmatter.
3. **Roh-CSVs** `audits/ga4-channels.csv` (Channel-Ebene, je Zeitraum — die maschinenlesbare Synthese-Baseline) + `audits/ga4-pages.csv` (Page-Ebene).
4. **HTML-Report** `reports/05b-ga4-first-party.html` — Datenqualitäts-Ampel, Kanal-Wertigkeit, GSC-Abgleich, Auffälligkeiten prominent oben; CSV ist die Maschinen-Schicht, HTML die Interpretations-Schicht.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Property-Bestätigung, Gate-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (CLI-Calls auf `google-analytics.py`, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z. B. bestätigte `property_id`, Phase-Hinweis)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="03-18-web-analytics-ga4"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Die Marker werden in **beiden Phasen** gesetzt — Phase A (Gate) zählt genauso wie Phase B (Vollauf). Beim HTML-Report-Render (nur Phase B) zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Wann triggern

- "GA4-Daten ziehen"
- "Web-Analytics auswerten"
- "Google Analytics des Kunden"
- "Analytics-Datenqualität prüfen"
- "Conversion-Tracking checken"
- "Conversion-Rate des Kunden ermitteln"
- "Kanal-Performance in GA4"
- "Kanal-Wertigkeit — welcher Traffic konvertiert"
- "First-party-Analytics-Status-Quo"
- "Echte Sessions und Nutzer"
- "Forecast-Baseline aus Analytics"
- "Direct-Traffic-Anomalie prüfen"
- "Consent-Verlust / Tracking-Lücke prüfen"
- "GA4 gegen GSC abgleichen"

## Voraussetzungen

Harte Voraussetzung ist nur `01-01-mta-projekt-init`. Der Skill läuft **bewusst früh** — idealerweise nach den Setup-Skills (01-01, 01-02, 02-01) und **vor `02-02-wettbewerber-identifikation`**: Seine Outputs (source/medium-Referral-Domains, Kanal-Wertigkeit) schärfen die Wettbewerber-Identifikation, weil GA4-Referral-Domains konkrete Akteurs-Hinweise liefern. First-Party-Daten sind der Realitäts-Anker, der die Wettbewerber-Auswahl und alle Folge-Audits verankert.

- `01-01-mta-projekt-init` gelaufen → `meta.json` mit `website` und `kunden_slug` vorhanden.
- **OAuth-Credentials** in `~/.config/reachx-mta/google-credentials.yaml` (chmod 600) — dieselbe Datei wie `google-ads.py`. `google-analytics.py` liest daraus `client_id`, `client_secret`, `refresh_token`; der refresh_token deckt beide Google-APIs ab. Pfad überschreibbar via `REACHX_GOOGLE_CREDENTIALS`.
- **GA4-Property des Kunden ist dem OAuth-Account zugänglich** (der zentrale Agentur-Account ist mit mindestens `Viewer` in der Property eingetragen). Der Skill prüft das automatisch über `list-properties`.
- **Python-Libraries** für `google-analytics.py` installiert: `pip3 install -r ${CLAUDE_PLUGIN_ROOT}/scripts/requirements-google.txt`.

**Empfohlen vorab (keine harte Abhängigkeit):**

- `03-14-web-tech-und-tracking` — wenn gelaufen, hat es das Consent-Tool (CMP) bereits erkannt. Phase A liest `audits/web-tech-tracking.md` und füllt die Consent-Frage damit vor, statt sie offen zu stellen. Spart dem Strategen einen Recherche-Schritt.
- `03-04-seo-first-party-gsc` — wenn gelaufen, liefert es `audits/gsc-first-party.md` mit echten Organic-Klicks. Phase A nutzt das für den GA4↔GSC-Abgleich — den besten Indikator für Consent-Verlust.

Beide Skills sind **Bonus**: ohne sie läuft `03-18` durch, stellt aber die Consent-Frage offen und überspringt die GSC-Abgleich-Sektion mit Hinweis.

**Wichtig:** Wenn keine `google-credentials.yaml` da ist oder keine passende Property gefunden wird → **freundlicher Skip mit Anleitung, KEIN Abbruch.** Der MTA-Workflow läuft mit den übrigen Audit-Skills nahtlos weiter. GA4 ist ein **Forecast-Verstärker**, kein Blocker — fehlt es, fällt der Forecast (`04-04`) transparent auf Branchen-Benchmarks zurück.

## Ablauf

Der Skill läuft **zweiphasig** (Datenqualitäts-Gate nach `contracts.md` Abschnitt 8, hier als Datenqualitäts-Gate statt Klassifikations-Schema):

- **Phase A — Datenqualitäts-Gate** (Schritte 0–6): Property finden, Kurz-Pull (nur `conversions` + `overview` + `channels` 12M und 90T + ein `run-report` für source/medium), automatische Checks rechnen, `audits/ga4-datenqualitaet.md` mit `status: vorgeschlagen` schreiben, stoppen.
- **Phase B — Vollauf** (Schritte 7–17): Gate-Datei mit `status: bestaetigt` einlesen, volle Erhebung, Aggregat + CSVs + HTML, `belastbarkeit`-Urteil ableiten.

Der Skill erkennt die Phase **automatisch** in Schritt 1: existiert `audits/ga4-datenqualitaet.md` noch nicht → Phase A. Existiert sie mit `status: bestaetigt` → Phase B. Existiert sie mit `status: vorgeschlagen` → Hinweis "Gate noch nicht bestätigt", kein Lauf.

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

Lokaler Arbeits-Cache für GA4-Roh-JSONs und CSV-Generierung: `~/.cache/reachx-mta/<slug>/`.

**Wichtig:** Die GA4-Auth (`google-credentials.yaml`) ist **unabhängig von Drive/gws** — `google-analytics.py` nutzt einen eigenen OAuth-Refresh-Token. Die Drive-Anpassung betrifft nur die Speicher-Stellen der Outputs.

### Schritt 1: Projekt-Auffindung, Voraussetzungs-Check, Phasen-Erkennung

Folge `contracts.md` Abschnitt 1. Wenn `meta.json` aus Schritt 0 fehlt oder nicht lesbar:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

**Voraussetzungs-Check:** Prüfe, ob `~/.config/reachx-mta/google-credentials.yaml` existiert (bzw. `REACHX_GOOGLE_CREDENTIALS`). Wenn nicht → freundlicher Skip, kein Abbruch:

```
ℹ 03-18-web-analytics-ga4 geskippt — keine Google-Credentials gefunden.

So beheben (einmalig):
1. Sicherstellen, dass ~/.config/reachx-mta/google-credentials.yaml existiert (chmod 600)
   mit den Feldern client_id, client_secret, refresh_token. Diese Datei wird von
   google-ads.py geteilt — wenn der SEA-First-Party-Skill (03-17) schon lief, ist
   sie bereits da.
2. Falls nicht: google-oauth.py einmalig ausführen (OAuth-Browser-Login mit dem
   zentralen Agentur-Account).
3. Diesen Skill erneut aufrufen.

Bis dahin läuft der MTA-Workflow ohne first-party-GA4-Daten weiter — kein Blocker.
Der Forecast (04-04) fällt dann transparent auf Branchen-Benchmark-Conversion-Raten zurück.

Nächste Schritte:
1. 03-04-seo-first-party-gsc — falls noch nicht gelaufen, first-party-SEO-Daten (First-Party-Block)
2. 03-17-sea-first-party-google-ads — falls noch nicht gelaufen, first-party-Paid-Daten (First-Party-Block)
3. 02-02-wettbewerber-identifikation — nutzt die First-Party-Outputs zur Schärfung
4. 03-14-web-tech-und-tracking — Tech/Tracking-Audit als weitere Achse

Sag mir, welcher als nächster.
```

Schreibe `status.md` mit Vermerk `geskippt — keine_google_credentials` (siehe Schritt 17).

**Phasen-Erkennung:** Lies das `audits/`-Verzeichnis aus Drive. Prüfe, ob `ga4-datenqualitaet.md` existiert:

- **Existiert nicht** → **Phase A**, weiter mit Schritt 2.
- **Existiert, Frontmatter `status: vorgeschlagen`** → Gate noch offen, kein Lauf:

  ```
  ℹ Datenqualitäts-Gate für 03-18-web-analytics-ga4 noch nicht bestätigt.
  Datei: audits/ga4-datenqualitaet.md (auf Drive)
  Bitte die Strategen-Fragen im Abschnitt "Offene Fragen" beantworten,
  status im Frontmatter auf `bestaetigt` setzen und Skill erneut aufrufen.
  ```

- **Existiert, Frontmatter `status: bestaetigt`** → **Phase B**, weiter mit Schritt 7.

---

## Phase A — Datenqualitäts-Gate

### Schritt 2: GA4-Property-Auffindung

Rufe den Helper auf:

```bash
GA="${CLAUDE_PLUGIN_ROOT}/scripts/google-analytics.py"
python3 "$GA" list-properties
```

Liefert `{"count": N, "rows": [{"property_id", "display_name", "account"}, ...]}` — alle GA4-Properties, auf die der OAuth-Account Zugriff hat.

**Property-Matching** gegen Kundennamen und Domain aus `meta.json` (`kunde`, `website`). `meta.json` hat **keine `property_id`** und ist read-only — der Skill muss die Property selbst finden. Matching-Logik in `reference/ga4-api-nutzung.md` Abschnitt "Property-Matching":

1. Domain aus `meta.json.website` normalisieren (Host, ohne `www.`, lowercase).
2. Property-`display_name` und `account` gegen Domain-Token und Kundennamen-Token matchen (GA4-Property-Namen tragen oft die Domain oder den Markennamen).
3. Bei genau einem Treffer → `property_id` als Vorschlag.
4. Bei mehreren Treffern → alle dem Hauptthread zur Auswahl vorlegen.

**Der Hauptthread bestätigt die `property_id`** — niemals raten. Vorschlag:

```
GA4-Property-Vorschlag für <Kunde> (<domain>):
  property_id: <id> — "<display_name>" (Konto: <account>)
Stimmt das? Falls nicht, die richtige property_id nennen.
```

Bei **Re-Run** (Phase B oder erneutes Phase A) wird die bestätigte `property_id` aus dem Frontmatter der vorhandenen `ga4-datenqualitaet.md` bzw. `ga4-first-party.md` gelesen — keine erneute Bestätigung nötig.

**Zwei Skip-Fälle:**

1. **Keine passende Property im Account** → freundlicher Skip:

```
ℹ 03-18-web-analytics-ga4 geskippt — GA4-Property nicht zugänglich.

Für die Kunden-Domain <domain> ist keine GA4-Property im verbundenen OAuth-Account
verfügbar. list-properties sieht aktuell N andere Properties, aber nicht diese.

So beheben:
1. Kunde bittet, den zentralen Agentur-Account als "Betrachter" (Viewer) oder höher
   in der Property-Zugriffsverwaltung seiner GA4-Property hinzuzufügen.
2. Nach Freigabe diesen Skill erneut aufrufen.

Bis dahin läuft der MTA-Workflow ohne first-party-GA4-Daten weiter — kein Blocker.

Nächste Schritte:
1. 03-04-seo-first-party-gsc — first-party-SEO-Daten (First-Party-Block)
2. 03-17-sea-first-party-google-ads — first-party-Paid-Daten (First-Party-Block)
3. 02-02-wettbewerber-identifikation — nutzt die First-Party-Outputs zur Schärfung
4. 03-14-web-tech-und-tracking — Tech/Tracking-Audit

Sag mir, welcher als nächster.
```

2. **`list-properties` schlägt mit Auth-Fehler fehl** → Hinweis "OAuth-Token-Problem — `google-oauth.py` erneut ausführen", sauberer Abbruch (kein MTA-Abbruch, nur dieser Skill). Vermerk `geskippt — auth_fehler` in `status.md`.

Bei jedem Skip: `status.md` aktualisieren mit Grund, Mini-Eintrag im "✓ Erledigt"-Block mit Status "geskippt".

### Schritt 3: Kurz-Pull (Gate-Datenbasis)

Phase A zieht **nur die für die Auto-Checks nötigen Daten** — nicht den vollen Datensatz. Zeitraum für den Kurz-Pull: `--range 365daysAgo` (12 Monate) für Conversions/Overview/Channels, plus ein paralleler `--range 30daysAgo`-Pull für den aktuellen Conversion-Snapshot.

**3.1 Key-Events / Conversions**

```bash
python3 "$GA" conversions <property_id> --range 365daysAgo
```

Liefert Events nach `keyEvents`, `eventCount`, `eventValue` — die Key-Events stehen oben. Das ist die Basis für den Conversion-Plausibilitäts-Check.

**3.2 Overview**

```bash
python3 "$GA" overview <property_id> --range 365daysAgo
python3 "$GA" overview <property_id> --range 30daysAgo
```

Liefert `sessions`, `totalUsers`, `newUsers`, `screenPageViews`, `engagementRate`, `averageSessionDuration`, `keyEvents` als Account-Aggregat. Die 12-Monats-Zahl bildet die Conversion-Rate, die 30-Tage-Zahl den aktuellen Stand.

**3.3 Channels**

```bash
python3 "$GA" channels <property_id> --range 365daysAgo
python3 "$GA" channels <property_id> --range 90daysAgo
```

Liefert Traffic nach `sessionDefaultChannelGroup` (Organic Search / Paid Search / Direct / Referral / Social / ...) mit Sessions, Nutzern, keyEvents, Engagement. Der 12-Monats-Pull ist Basis für den Direct-Last-Check und den unzugeordneten-Traffic-Check. Der **zusätzliche 90-Tage-Pull** liefert den GA4-"Organic Search"-Sessions-Wert für den GA4↔GSC-Abgleich (Check 4.3) — er wird gegen den GSC-90-Tage-Wert (`statistiken_90_tage.clicks_total`) gestellt, damit beide Seiten denselben Zeitraum abdecken (sauberer 90-Tage-Direktvergleich, keine ×4-Näherung).

**3.4 source/medium-Roh-Scan**

```bash
python3 "$GA" run-report <property_id> --dimensions sessionSourceMedium \
  --metrics sessions,keyEvents --range 365daysAgo --limit 100
```

Liefert den rohen source/medium-Report. Basis für den source/medium-Scan auf unübliche aber relevante Quellen.

**Datenhistorie:** Die GA4 Data API liefert keinen direkten "erstes Datum mit Daten"-Wert. Heuristik: ein `run-report` mit `--dimensions yearMonth --metrics sessions --range 730daysAgo` (24 Monate) — die früheste `yearMonth` mit `sessions > 0` ist der Property-Start. Liegt sie weniger als 12 Monate zurück → kein YoY-Vergleich möglich.

Roh-Antworten als JSON in `~/.cache/reachx-mta/<slug>/audits/raw/ga4-gate-*.json` (lokal, in Phase B nach Drive `assets/raw/` komprimiert).

**Data Filters:** Die GA4 Data API exponiert keine Data Filters (interner-Traffic-Filter, Developer-Traffic-Filter — das sind Admin-API-Property-Settings, die der Helper nicht liest). Der Skill nimmt deshalb **automatisch an: "ungefiltert (Standard)"** und stellt dazu **keine Strategen-Frage**. Vermerk im Gate-File als Auto-Annahme.

### Schritt 4: Automatische Checks rechnen

Der Skill rechnet die folgenden Checks selbst aus dem Kurz-Pull. Schwellwerte und Begründungen vollständig in `reference/ga4-datenqualitaet.md` Abschnitt "Automatische Checks".

**4.1 Conversion-Plausibilität.** Key-Events-Namen aus `conversions` prüfen. Verdächtig getaggte Events: `page_view`, `scroll`, `session_start`, `user_engagement`, `first_visit`, `view_*` (z. B. `view_item`, `view_search_results`). Conversion-Rate berechnen: `keyEvents / sessions` (12 Monate).
- CR > ~15 % → starker Verdacht: ein Pageview-/Engagement-Event ist fälschlich als Key-Event markiert.
- CR = 0 oder keine Key-Events → der Kunde misst keine Conversions.
- Beide Befunde gehen in die Auto-Befunde des Gate-Files.

**4.2 Direct-Last.** Direct-Anteil aus `channels`: `Direct-Sessions / Gesamt-Sessions`. > ~40 % → Attribution unzuverlässig (fehlendes UTM-Tagging auf eigenen Kampagnen, Dark Traffic, App-/E-Mail-Klicks ohne UTM).

**4.3 GA4↔GSC-Abgleich.** Falls `audits/gsc-first-party.md` (Output von `03-04`) existiert: die GA4-"Organic Search"-Sessions aus dem **90-Tage-`channels`-Pull** (Schritt 3.3) gegen den GSC-90-Tage-Wert `statistiken_90_tage.clicks_total` stellen — beide Seiten decken damit denselben Zeitraum ab (sauberer 90-Tage-Direktvergleich, **nicht** die grobe ×4-Hochrechnung). Liegt GA4-Organic deutlich unter GSC-Klicks (Faustregel: < ~70 %) → **bester Indikator für Consent-Verlust / Tracking-Lücke** (Besucher klicken in der Google-Suche, lehnen dann das Cookie-Banner ab und erscheinen nie in GA4). Methodik in `reference/ga4-datenqualitaet.md` Check 3 und `reference/ga4-analyse-methodik.md`. Wenn `gsc-first-party.md` fehlt → Check übersprungen, Hinweis im Gate-File.

**4.4 Datenhistorie.** Erstes Datum mit Daten aus 3.4-Heuristik. < 12 Monate → keine Saisonalität, kein YoY-Vergleich möglich. Befund im Gate-File.

**4.5 Unzugeordneter Traffic.** Anteil `(not set)` / `Unassigned` an den `channels`- und `sessionSourceMedium`-Zeilen. Hoch (> ~10 %) → Tagging-Qualität schlecht.

**4.6 source/medium-Scan.** Den rohen source/medium-Report aus 3.4 auf **unübliche, aber relevante** Quellen scannen, die GA4 pauschal als `Referral` verbucht und die einen eigenen Kanal-Bucket verdienen:
- Preisvergleichs-Portale: `idealo`, `billiger.de`, `guenstiger.de`, `geizhals`, `preisvergleich`
- Branchen-/Bewertungsportale: `provenexpert`, `trustpilot`, `jameda`, `wlw`, `capterra`, `g2`, `omr`
Treffer landen als Auto-Befund "unüblicher relevanter Kanal entdeckt" — in Phase B bekommen sie einen eigenen CSV-Bucket. Cluster-Regeln in `reference/ga4-analyse-methodik.md`.

### Schritt 5: Gate-Datei `audits/ga4-datenqualitaet.md` schreiben

Schreibe die Datei mit Frontmatter `status: vorgeschlagen` nach dem Format in `reference/ga4-datenqualitaet.md` Abschnitt "Format der Gate-Datei". Sie enthält:

- **Frontmatter:** Skill-Metadaten, bestätigte `property_id`, Kurz-Pull-Kennzahlen, alle Auto-Check-Ergebnisse strukturiert (jeder Check mit `befund` und `ampel`-Vorschlag), `status: vorgeschlagen`.
- **Body — Auto-Befunde:** pro Check ein Absatz mit dem konkreten Zahlen-Befund (z. B. "Conversion-Rate 12 Monate: 23,4 % — über dem Plausibilitäts-Schwellwert von 15 %. Verdacht: ein Pageview-Event ist als Key-Event getaggt. Erkannte Key-Events: page_view, generate_lead.").
- **Body — Offene Fragen:** die fünf beschreibenden Strategen-Fragen (siehe Schritt 6). **Jede Frage erklärt, WARUM sie gestellt wird** — der Stratege muss den Zweck verstehen, um sinnvoll antworten zu können.

Dann **stoppen** mit:

```
Datenqualitäts-Gate für 03-18-web-analytics-ga4 vorgeschlagen.
Datei: audits/ga4-datenqualitaet.md (auf Drive)

Phase A hat den Kurz-Pull gezogen und die automatischen Checks gerechnet.
Bitte die Auto-Befunde prüfen, die Fragen im Abschnitt "Offene Fragen" beantworten,
status im Frontmatter auf `bestaetigt` setzen und Skill erneut aufrufen.

Phase B zieht dann die volle Datenbasis und leitet das Belastbarkeits-Urteil ab.
```

`status.md` aktualisieren (Schritt 17) — der Skill ist nach Phase A nicht "erledigt", sondern "blockiert: wartet auf Gate-Bestätigung".

### Schritt 6: Die fünf Strategen-Fragen (im Gate-File)

Diese Fragen stehen im Abschnitt "Offene Fragen" der Gate-Datei. Jede mit Begründungstext. Wortlaut und Begründungen vollständig in `reference/ga4-datenqualitaet.md`.

1. **Cookie-Weiche / Consent.** Hat die Website ein Consent-Banner? Welches CMP? Ist Consent Mode v2 aktiv? Akzeptanzrate bekannt? — *Wichtig, weil bei abgelehnten Cookies ein Teil des echten Traffics gar nicht in GA4 erscheint; die Absolut-Baseline wäre dann zu niedrig und der Forecast zu pessimistisch.*
   **ABER ZUERST `audits/web-tech-tracking.md` lesen:** Wenn `03-14-web-tech-und-tracking` gelaufen ist und das CMP-Tool erkannt hat (z. B. Cookiebot, Usercentrics, Borlabs), die Frage **vorausgefüllt** präsentieren ("03-14 hat `<CMP>` erkannt — bitte nur noch Consent Mode v2 und Akzeptanzrate ergänzen") bzw. den erledigten Teil überspringen.

2. **Conversion-Einordnung.** Der Skill zeigt die erkannte Key-Events-Liste — welche davon sind echte **Macro**-Conversions (Kauf, Lead, Anfrage, Termin), welche sind **Micro**-Conversions (Newsletter-Anmeldung, Datei-Download, Klick)? — *Wichtig, weil nur Macro-Conversions in die Forecast-Baseline gehören. Micro-Conversions im Conversion-Zähler blähen die CR auf.*

3. **Property-Wahl.** Bei mehreren passenden Properties: Welche ist die produktive Live-Property (nicht Test/Staging/eine alte Property)? — *Wichtig, weil eine Staging-Property realistische, aber für den Forecast wertlose Daten liefert.*

4. **Bekannte Tracking-Lücken.** Sind Teile der Customer Journey ungetrackt — Checkout auf einer externen Shop-Domain, eine Subdomain ohne GA4-Tag, eine App? — *Wichtig, weil ein ungetrackter Checkout die Conversions verschwinden lässt und die CR künstlich auf 0 drückt.*

5. **Brüche im Zeitraum.** Gab es im Messzeitraum ein GA4-Re-Setup, einen Domain-Umzug oder eine Tracking-Migration (z. B. Universal Analytics → GA4)? — *Wichtig, weil solche Brüche Knicke in der Sitzungs-Kurve erzeugen, die sonst als echte Trends fehlinterpretiert würden.*

**Keine Frage zu internem Traffic / Data Filters** — siehe Schritt 3, Auto-Annahme "ungefiltert".

---

## Phase B — Vollauf

### Schritt 7: Gate-Datei einlesen, Property-Bestätigung übernehmen

Lies `audits/ga4-datenqualitaet.md` aus Drive. Prüfe `status: bestaetigt` im Frontmatter — wenn `vorgeschlagen`, Hinweis aus Schritt 1, kein Lauf.

Aus dem Gate-File übernehmen:
- Bestätigte `property_id`.
- Die Strategen-Antworten aus dem Abschnitt "Offene Fragen" (der Stratege hat sie direkt unter den Fragen ergänzt).
- Die Auto-Check-Ergebnisse aus dem Frontmatter.

Diese drei Blöcke (Auto-Checks + Strategen-Antworten) fließen in Schritt 13 zum `belastbarkeit`-Urteil zusammen.

### Schritt 8: Zeiträume festlegen

Zwei Pflicht-Zeiträume:

- **12 Monate** — `--range 365daysAgo`. Saisonalität, Jahres-Trend, stabile Conversion-Baseline.
- **Letzte 30 Tage** — `--range 30daysAgo`. Aktueller Stand.

Wenn die Datenhistorie (aus Phase A) < 12 Monate ist: 12-Monats-Range automatisch auf den verfügbaren Bereich reduzieren, Frontmatter-Feld `historie_verfuegbar_tage` setzen, Hinweis im Body. Optional für den Verlauf: `--dimensions yearMonth` über den verfügbaren Bereich (siehe Schritt 9.5).

### Schritt 9: Voll-Pull

Pro Zeitraum die relevanten Helper-Befehle. Genaue Parameter, GA4-Metrik-/Dimensions-Namen und `run-report`-Nutzung in `reference/ga4-api-nutzung.md`.

**9.1 Overview** — `overview` für 12M und 30T (falls Phase A schon gezogen: aus Cache lesen, nicht erneut callen).

**9.2 Channels (Kanal-Performance UND Kanal-Wertigkeit)** — `channels` für 12M und 30T. Liefert pro Channel Sessions, totalUsers, newUsers, keyEvents, engagementRate. Daraus pro Channel die **Conversion-Rate** (`keyEvents / sessions`) berechnen — das ist die Kanal-Wertigkeit. Für Umsatz pro Channel (falls E-Commerce): zusätzlich `run-report --dimensions sessionDefaultChannelGroup --metrics totalRevenue,purchaseRevenue,sessions`.

**9.3 source/medium** — `run-report --dimensions sessionSourceMedium --metrics sessions,totalUsers,keyEvents,engagementRate --range 365daysAgo --limit 200`. Plus die in Phase A entdeckten unüblichen Quellen zu einem Cluster "unübliche Kanäle" zusammenfassen (Regeln in `reference/ga4-analyse-methodik.md`).

**9.4 Top-Pages** — `top-pages <property_id> --range 365daysAgo --limit 100`. Liefert pagePath, screenPageViews, sessions, totalUsers, averageSessionDuration.

**9.5 Verlauf (12 Monate)** — `run-report --dimensions yearMonth --metrics sessions,totalUsers,keyEvents --range 365daysAgo`. Liefert die Monats-Kurve für Saisonalität und Trend.

**9.6 Geo- und Device-Split** — `run-report --dimensions country --metrics sessions,keyEvents,engagementRate --range 365daysAgo --limit 15` und `run-report --dimensions deviceCategory --metrics sessions,keyEvents,engagementRate --range 365daysAgo`.

**9.7 E-Commerce-Check** — ein `run-report --dimensions sessionDefaultChannelGroup --metrics totalRevenue,transactions --range 365daysAgo`. Liefert das alles 0/leer → die Property misst keinen Umsatz (Lead-Geschäft); E-Commerce-Sektionen entfallen, AOV bleibt `null`.

**API-Budget:** Die GA4 Data API ist kostenlos. Quotas sind großzügig (Standard-Property: 200.000 Tokens/Tag, 40.000/Stunde — pro `run-report` wenige Tokens). Ein voller Skill-Lauf nutzt typisch 12–20 Calls, weit unter dem Limit. Details in `reference/ga4-api-nutzung.md` Abschnitt "API-Budget".

Roh-Antworten als JSON in `~/.cache/reachx-mta/<slug>/audits/raw/ga4-*.json`.

### Schritt 10: Kern-Analysen

Methodik-Details (Berechnungs-Formeln, Schwellwerte) in `reference/ga4-analyse-methodik.md`.

**10.1 Kanal-Performance und Kanal-Wertigkeit.** Pro Channel: nicht nur Sessions/Volumen, sondern Conversion-Rate, keyEvents, Umsatz (falls E-Commerce) und Engagement-Rate. Damit wird messbar, *wie wertvoll* welcher Traffic ist — ein Channel mit hohem Session-Volumen, aber CR 0,3 % ist strategisch weniger wert als einer mit weniger Sessions und 4 % CR. Wenn `03-04` lief, GA4-Organic-Sessions gegen GSC-Klickvolumen stellen; wenn Ads-Daten vorliegen (`03-17` oder `03-05`), Paid-Channel gegen Spend.

**10.2 source/medium-Analyse.** Vollständige source/medium-Tabelle plus der Cluster "unübliche Kanäle" aus Phase A — die Quellen, die GA4 als `Referral` verbucht, aber strategisch einen eigenen Bucket verdienen (Preisvergleich, Bewertungsportale).

**10.3 GA4↔GSC-Abgleich.** Eigene Sektion: GA4-Organic-Sessions vs. GSC-Klicks, das Verhältnis, die Interpretation (Consent-Lücke? Tracking-Lücke? oder plausibel?). Nur wenn `gsc-first-party.md` existiert.

**10.4 Conversion-Baseline.** Das Forecast-relevante Aggregat: Gesamt-CR (nur Macro-Conversions laut Strategen-Antwort Frage 2), CR pro Channel, AOV/Umsatz falls E-Commerce, Sessions/Monat. Strukturiert im Frontmatter, damit `04-04-forecast-modell` es direkt liest.

**10.5 Top-Pages, Geo/Device, Engagement.** Top-Pages mit Kategorie-Heuristik (analog `gsc-pages.csv`), Geo-Split (DACH vs. Rest), Device-Split, Engagement-Rate als Qualitäts-Signal.

### Schritt 11: Auffälligkeiten

Strategische Beobachtungen extrahieren — analog `03-04` Schritt 8. Typ-Tabelle mit Auslöser und Beispiel vollständig in `reference/ga4-analyse-methodik.md` Abschnitt "Auffälligkeiten":

| Typ | Auslöser (Kurzform) |
|---|---|
| `conversion_tracking_fehlt` | Keine Key-Events / CR = 0 |
| `conversion_ueberzaehlt` | CR > 15 % bzw. Pageview-Event als Key-Event getaggt |
| `consent_luecke_vermutet` | GA4-Organic deutlich < GSC-Klicks ODER Consent-Banner ohne Consent Mode v2 |
| `direct_anomalie` | Direct-Anteil > 40 % |
| `kanal_wert_divergenz` | Channel mit hohem Session-Anteil, aber CR deutlich unter Account-Schnitt |
| `unueblicher_kanal_relevant` | Preisvergleich/Bewertungsportal mit relevantem Session-Anteil als Referral verbucht |
| `historie_zu_kurz` | Datenhistorie < 12 Monate |
| `nicht_dach_traffic_signifikant` | Nicht-DACH-Land mit ≥ 15 % Session-Anteil |
| `tracking_luecke_bekannt` | Strategen-Antwort Frage 4 nennt eine ungetrackte Journey-Stufe |

Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung.

### Schritt 12: CSV-Outputs

Vollständiges Schema in `reference/ga4-output-schema.md`.

**`audits/ga4-channels.csv`** — Channel-Ebene, **die maschinenlesbare Synthese-Baseline**. Eine Zeile pro (Channel, Periode)-Paar:

```
channel,periode,datum_von,datum_bis,sessions,users,new_users,conversions,conversion_rate,umsatz,engagement_rate,ist_unueblicher_kanal
```

**`audits/ga4-pages.csv`** — Page-Ebene, eine Zeile pro Page (12-Monats-Periode):

```
page_path,sessions,users,page_views,avg_session_duration,conversions,kategorie_seite
```

`kategorie_seite` ist die pfad-basierte Heuristik (`{produkt, service, blog, news, presse, ueber_uns, kontakt, homepage, sonstige}`) — gleiche Logik wie `gsc-pages.csv`.

### Schritt 13: `belastbarkeit`-Urteil ableiten

Aus den Auto-Checks (Phase A) + Strategen-Antworten (Schritt 7) das Feld `belastbarkeit: gruen | gelb | rot` ableiten. Ableitungslogik vollständig in `reference/ga4-datenqualitaet.md` Abschnitt "belastbarkeit-Ableitung". Kurzform:

- **`gruen`** — Conversion-Tracking sauber (Macro-Conversions klar definiert, CR plausibel), Direct-Anteil unauffällig, GA4↔GSC im plausiblen Bereich, ≥ 12 Monate Historie, keine bekannte Tracking-Lücke.
- **`gelb`** — eine relevante Einschränkung (z. B. Consent-Lücke vermutet, aber Conversions sauber; oder kurze Historie; oder erhöhter Direct-Anteil). Zahlen nutzbar, aber mit dokumentierter Einschränkung.
- **`rot`** — Conversion-Tracking defekt (kein/falsches Tracking) ODER mehrere schwere Einschränkungen gleichzeitig. Die GA4-Conversion-Rate ist **nicht als harte Zahl verwendbar**.

Das Urteil wird in `ga4-first-party.md` (Frontmatter `belastbarkeit` + eigene Body-Sektion) und prominent als Ampel im HTML-Report mitgeführt.

**Konsequenz dokumentieren:** Bei `belastbarkeit: rot` darf `04-04-forecast-modell` die GA4-Conversion-Rate **nicht** als harte Zahl übernehmen, sondern fällt transparent auf den Branchen-Benchmark zurück. Das wird im Frontmatter (`forecast_hinweis`) und in der Body-Sektion explizit so geschrieben.

**Nuance dokumentieren:** Consent-Lücken verzerren die **Absolut-Volumina** nach unten (abgelehnte Cookies = unsichtbare Besucher), aber die **Conversion-RATE bleibt relativ robust** — sie wird aus getrackten Sessions und getrackten Conversions gebildet, beide gleichermaßen vom Consent betroffen. Konsequenz: Bei reiner Consent-Lücke (sonst sauberes Tracking) ist die GA4-CR weiter nutzbar, aber die **Absolut-Baseline** (Sessions/Monat, Conversions/Monat) muss um den geschätzten Consent-Faktor hochgerechnet werden. Dieser Hinweis steht im Frontmatter (`conversion_baseline.consent_korrektur_hinweis`) und in der Body-Sektion.

### Schritt 14: Aggregat-Markdown `audits/ga4-first-party.md`

Format mit YAML-Frontmatter nach `reference/ga4-output-schema.md` Abschnitt "Markdown-Schema". Frontmatter enthält u. a.:

- Skill-Metadaten, Recherche-Provenienz (`property_id`, Zeiträume, Gate-Referenz).
- `belastbarkeit` (`gruen`/`gelb`/`rot`) plus `belastbarkeit_begruendung`.
- `statistiken_12_monate` und `statistiken_30_tage` (sessions, users, new_users, key_events, conversion_rate, engagement_rate, avg_session_duration, top_channel, top_country, top_device).
- `conversion_baseline` (strukturiert für `04-04`: gesamt_cr, cr_pro_channel, sessions_pro_monat, aov, umsatz_pro_monat, macro_conversion_events, consent_korrektur_hinweis).
- `kanal_wertigkeit` (pro Channel: session_anteil, conversion_rate, wert_einordnung).
- `gsc_abgleich` (ga4_organic_sessions, gsc_klicks, verhaeltnis, interpretation — oder `null` wenn GSC fehlt).
- `forecast_hinweis` (was `04-04` mit den Zahlen tun darf/nicht darf).
- `auffaelligkeiten` (Liste, siehe Schritt 11).

Body strukturiert nach:

1. **Übersicht** (3–5 Sätze: Datenstand, Belastbarkeits-Urteil als Erstes, größte Hebel).
2. **Datenqualität und Belastbarkeit** (Ampel, Auto-Befunde, Strategen-Antworten, Forecast-Konsequenz, Consent-Korrektur-Nuance).
3. **Performance-Stand** (12M und 30T: Sessions, Nutzer, Engagement, Conversions).
4. **Performance-Verlauf 12 Monate** (Monats-Kurve, Saisonalität, Knickpunkte — Brüche aus Strategen-Antwort Frage 5 hier verorten).
5. **Kanal-Performance und Kanal-Wertigkeit** (Tabelle: Channel × Sessions × CR × Umsatz × Engagement, plus Wert-Einordnung).
6. **source/medium-Analyse** (Tabelle, plus Cluster "unübliche Kanäle").
7. **GA4↔GSC-Abgleich** (eigene Sektion — oder Hinweis "GSC-Daten fehlen, Abgleich übersprungen").
8. **Conversion-Baseline** (das Forecast-Aggregat — Gesamt-CR, CR pro Channel, AOV, Sessions/Monat).
9. **Top-Pages** (Tabelle Top-20).
10. **Geo- und Device-Splits**.
11. **Auffälligkeiten** (aus Frontmatter, sortiert nach Relevanz).
12. **Lücken und Hinweise**.

### Schritt 15: HTML-Report `reports/05b-ga4-first-party.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html` bauen. Nummer `05b` (GSC ist `05a`, der SEA-First-Party-Skill `03-17` wird `05c`).

**User-Vorgabe — der HTML-Report trägt die ERKENNTNISSE, nicht Tabellen-Dumps.** Datenqualitäts-Ampel, Strategen-Antworten, Kanal-Wertigkeit, GSC-Abgleich und Auffälligkeiten stehen **prominent oben**. CSV ist die Maschinen-Schicht, HTML die Interpretations-Schicht.

Platzhalter:

- `{{TITLE}}` → `Web-Analytics First-Party (GA4) · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · Web-Analytics First-Party`
- `{{DISPLAY_NAME}}` → `First-Party-Web-Analytics aus Google Analytics 4: KUNDE`
- `{{META_LINE}}` → `Quelle: GA4 Data API via google-analytics.py · Property: <id> · Zeitraum: 12 Monate · Datenqualität: <Ampel> · Generiert: <heute>`
- `{{MAIN_CONTENT}}` →
  - **Datenqualitäts-Ampel ganz oben** — große `.summary-card` mit `belastbarkeit` (grün/gelb/rot), Begründung in einem Satz, der Forecast-Konsequenz und der Consent-Korrektur-Nuance. Das ist die erste Sektion, vor dem Stat-Strip.
  - **Stat-Strip** — Sessions/12M, Nutzer/12M, Gesamt-CR, Conversions/12M, Engagement-Rate, Top-Channel, Anteil unüblicher Kanäle.
  - **Sticky-TOC**: Datenqualität, Verlauf, Kanal-Wertigkeit, source/medium, GSC-Abgleich, Conversion-Baseline, Top-Pages, Geo/Device, Auffälligkeiten.
  - **Strategen-Antworten** als `.suggestion`-Block — die fünf Gate-Antworten kompakt, damit der Leser die Datenqualität einordnen kann.
  - **12M-Verlauf** als SVG-Linechart (Sessions + Conversions parallel) oder Fallback-Text-Tabelle.
  - **Kanal-Wertigkeit** als `table.data` — pro Channel Sessions, Session-Anteil, CR (mit Badge `stark`/`mittel`/`schwach`), Umsatz, Engagement, Wert-Einordnung. Das ist die zentrale Erkenntnis-Tabelle.
  - **source/medium** als `table.data`, der Cluster "unübliche Kanäle" oben abgesetzt und markiert.
  - **GA4↔GSC-Abgleich** als Hinweis-Card mit dem Verhältnis und der Interpretation (oder Hinweis, dass GSC fehlt).
  - **Conversion-Baseline** als `.summary-card` — das Forecast-Aggregat klar lesbar (Gesamt-CR, CR pro Channel, AOV, Sessions/Monat), mit dem Hinweis, was `04-04` damit tun darf.
  - **Top-Pages** als `table.data`.
  - **Geo/Device** als kleine Balken-Visualisierung bzw. Tabelle.
  - **Auffälligkeiten-Block** als `.suggestion`-Block, Top 3–5 nach Relevanz.
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · Web-Analytics-First-Party-GA4-Audit`
- `{{TOKEN_FOOTER}}` → Skill-Counter (siehe Token-Tracking).

`<body>` ohne Klasse → Back-Link zum Dashboard sichtbar (siehe `contracts.md` Abschnitt 7).

### Schritt 16: Outputs nach Drive hochladen

Finale Outputs via `drive.py upsert-text` nach Drive (idempotent):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "ga4-datenqualitaet.md" \
  ~/.cache/reachx-mta/<slug>/ga4-datenqualitaet.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "ga4-first-party.md" \
  ~/.cache/reachx-mta/<slug>/ga4-first-party.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "ga4-channels.csv" \
  ~/.cache/reachx-mta/<slug>/ga4-channels.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "ga4-pages.csv" \
  ~/.cache/reachx-mta/<slug>/ga4-pages.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "05b-ga4-first-party.html" \
  ~/.cache/reachx-mta/<slug>/05b-ga4-first-party.html "text/html"
```

In Phase B die Gate-Datei `ga4-datenqualitaet.md` belassen (sie wurde in Phase A geschrieben) — nicht überschreiben, außer der Skill ergänzt das `belastbarkeit`-Urteil auch dort als Querverweis. CSV bleibt CSV (kein Auto-Convert zu Google Sheet).

In **Phase A** wird nur die Gate-Datei hochgeladen — keine CSVs, kein HTML.

### Schritt 17: Dashboard- und `status.md`-Update

**Dashboard `reports/index.html`** (nur Phase B): aus Drive lesen, anpassen, zurückschreiben.

- Stat-Strip um GA4-Sessions/12M und Gesamt-CR ergänzen.
- "Erledigt"-Sektion um `03-18-web-analytics-ga4` erweitern.
- Reports-Liste um `05b-ga4-first-party.html` erweitern.
- Token-Breakdown-Slots beim Dashboard-Re-Render aktualisieren — analog zum Schwester-Skill `03-17-sea-first-party-google-ads` (siehe `contracts.md` Sektion 10).
- "Nächster empfohlener Schritt": je nach Workflow-Stand zuerst die offenen First-Party-Skills (`03-04-seo-first-party-gsc`, `03-17-sea-first-party-google-ads`), dann `02-02-wettbewerber-identifikation` falls offen, sonst `04-02-kanal-chancen-analyse`.

**`status.md`** (in jeder Phase) — aus Drive lesen, anpassen, zurückschreiben, nach Regeln aus `contracts.md` Abschnitt 3:

- **Phase A:** `03-18-web-analytics-ga4` bleibt in `schritte_offen`, Eintrag in `blockiert` (Frontmatter) und unter "✗ Blockiert" im Body: "wartet auf Bestätigung des Datenqualitäts-Gates (`audits/ga4-datenqualitaet.md`)".
- **Phase B:** `03-18-web-analytics-ga4` in `schritte_done`, aus `blockiert` entfernen, eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Highlight-Numbers (Sessions/12M, Gesamt-CR, `belastbarkeit`-Ampel). `naechster_empfohlen` in dieser Reihenfolge setzen: zuerst die noch offenen First-Party-Skills (`03-04-seo-first-party-gsc`, `03-17-sea-first-party-google-ads`), dann `02-02-wettbewerber-identifikation` (nutzt die First-Party-Outputs), erst danach Third-Party-/Wettbewerbs-Audits bzw. `04-02-kanal-chancen-analyse`.
- **Skip:** Mini-Eintrag in "✓ Erledigt" mit Status "geskippt" und Grund.
- Bei `belastbarkeit: rot`: explizit als Hinweis "Forecast (04-04) muss auf Branchen-Benchmark-CR zurückfallen — GA4-CR nicht belastbar".

### Schritt 18: Standard-Schlussformat im Chat

**Nach Phase A** (Gate vorgeschlagen):

```
ℹ 03-18-web-analytics-ga4 — Phase A (Datenqualitäts-Gate) abgeschlossen.

Output (auf Drive):
- audits/ga4-datenqualitaet.md — Auto-Befunde + offene Strategen-Fragen
Status aktualisiert in: status.md (Skill als blockiert markiert)

Auto-Befunde (Kurz-Pull):
- Conversion-Rate 12M:   XX,X% (<plausibel | über Schwellwert>)
- Direct-Anteil:         XX% (<unauffällig | erhöht>)
- GA4↔GSC-Abgleich:      <Verhältnis oder "GSC-Daten fehlen">
- Datenhistorie:         XX Monate
- Unüblicher Kanal:      <gefunden: idealo, ... | keiner>

Nächster Schritt:
1. audits/ga4-datenqualitaet.md auf Drive öffnen, die 5 Fragen im Abschnitt
   "Offene Fragen" beantworten, status im Frontmatter auf `bestaetigt` setzen.
2. 03-18-web-analytics-ga4 erneut aufrufen — Phase B zieht dann die volle Datenbasis.

Sag mir Bescheid, wenn das Gate bestätigt ist.
```

**Nach Phase B** (Vollauf):

```
✓ 03-18-web-analytics-ga4 abgeschlossen.

Outputs (auf Drive):
- audits/ga4-datenqualitaet.md — Datenqualitäts-Gate (bestätigt)
- audits/ga4-first-party.md — Aggregat mit Kanal-Wertigkeit, Conversion-Baseline, GSC-Abgleich
- audits/ga4-channels.csv — Channel-Ebene (N Zeilen), Synthese-Baseline für 04-04
- audits/ga4-pages.csv — Page-Ebene (M Zeilen)
- reports/05b-ga4-first-party.html — visueller First-Party-Audit
Status aktualisiert in: status.md

Datenqualität: <🟢 grün | 🟡 gelb | 🔴 rot> — <Begründung in einem Satz>

GA4-Highlights (12 Monate):
- Sessions:              XXX
- Nutzer:                XXX
- Gesamt-Conversion-Rate: X,X% (nur Macro-Conversions)
- Conversions:           XXX
- Engagement-Rate:       XX%
- Top-Channel:           <Channel> (XX% der Sessions)

Kanal-Wertigkeit (Top 3 nach CR):
- <Channel>: XX% Session-Anteil, X,X% CR
- <Channel>: XX% Session-Anteil, X,X% CR
- <Channel>: XX% Session-Anteil, X,X% CR

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- (1–3 Punkte aus der Auffälligkeiten-Liste, sortiert nach Relevanz)

[Wenn belastbarkeit: rot:]
⚠ Forecast-Hinweis: GA4-Conversion-Rate ist NICHT belastbar — 04-04-forecast-modell
   muss auf Branchen-Benchmark-CR zurückfallen. Grund: <Befund>.

Nächste Schritte:
1. 03-04-seo-first-party-gsc — first-party-SEO-Daten, falls noch offen (First-Party-Block)
2. 03-17-sea-first-party-google-ads — first-party-Paid-Performance, falls noch offen (First-Party-Block)
3. 02-02-wettbewerber-identifikation — nutzt die First-Party-Outputs (source/medium-Referral-Domains, Kanal-Wertigkeit) zur Schärfung der Wettbewerber-Auswahl
4. (parallel möglich) 03-14-web-tech-und-tracking — Tracking-Setup vertiefen
5. 04-02-kanal-chancen-analyse — sobald die Audit-Achsen stehen

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/ga4-api-nutzung.md` — `google-analytics.py`-Befehle und Parameter, GA4-Metrik-/Dimensions-Namen, `run-report`-Nutzung für source/medium und Verlauf, Property-Matching, API-Budget, Edge-Cases
- `reference/ga4-datenqualitaet.md` — das komplette Gate: alle Auto-Checks mit Schwellwerten, alle fünf Strategen-Fragen mit Begründungstexten, die `belastbarkeit`-Ableitungslogik (grün/gelb/rot-Kriterien), das Format der `audits/ga4-datenqualitaet.md`-Datei
- `reference/ga4-output-schema.md` — CSV-Spalten + Markdown-Frontmatter-Schema, Validierungs-Regeln, wie Folge-Skills die Outputs lesen
- `reference/ga4-analyse-methodik.md` — Kanal-Wertigkeits-Berechnung, source/medium-Cluster-Regeln (unübliche Kanäle), GA4↔GSC-Abgleichs-Methodik, Auffälligkeiten-Schwellwerte

## Edge Cases

- **Keine `google-credentials.yaml`** → freundlicher Skip mit Anleitung (Schritt 1). KEIN Abbruch des MTA-Workflows. `status.md` markiert geskippt.

- **GA4-Property nicht zugänglich** → freundlicher Skip (Schritt 2 Fall 1). Im Skip-Hinweis erklären, dass der zentrale Agentur-Account als Viewer in der Property eingetragen werden muss.

- **Gate-Datei mit `status: vorgeschlagen`** → Skill stoppt mit Hinweis auf die offenen Fragen (Schritt 1). Kein Vollauf.

- **Mehrere passende Properties** → alle dem Hauptthread zur Auswahl vorlegen, niemals raten. Die gewählte `property_id` landet im Gate-File-Frontmatter und wird bei Re-Run von dort gelesen. Strategen-Frage 3 (Property-Wahl) deckt zusätzlich Test-/Staging-Verwechslungen ab.

- **Conversion-Tracking defekt** (keine Key-Events oder CR = 0) → Skill läuft durch, setzt `belastbarkeit: rot`, Auffälligkeit `conversion_tracking_fehlt`, Frontmatter `forecast_hinweis` mit der Benchmark-Rückfall-Anweisung. Die übrigen Sektionen (Sessions, Kanäle, Pages) bleiben verwertbar.

- **Conversion überzählt** (CR > 15 %, Pageview als Key-Event) → Auffälligkeit `conversion_ueberzaehlt`. Die Conversion-Baseline wird **nur** aus den vom Strategen als Macro markierten Events gebildet (Frage 2). Falsch getaggte Events fließen nicht in die Baseline. Wenn der Stratege keine Macro-Events markieren konnte → `belastbarkeit: rot`.

- **Property jünger als 12 Monate** → 12-Monats-Range automatisch reduzieren, `historie_verfuegbar_tage` setzen, Auffälligkeit `historie_zu_kurz`, Hinweis im Body "keine Saisonalität/YoY möglich". `belastbarkeit` höchstens `gelb`.

- **E-Commerce-Property ohne Umsatz-Daten / Lead-Geschäft** → `run-report` für Umsatz liefert 0/leer. E-Commerce-Sektionen entfallen, `aov: null`, `umsatz_pro_monat: null`. Die Conversion-Baseline arbeitet dann mit Lead-Conversions statt Transaktionen — das ist normal und kein Fehler.

- **`gsc-first-party.md` fehlt** → GA4↔GSC-Abgleich wird übersprungen, `gsc_abgleich: null`, Hinweis im Body und im Schluss-Format. Empfehlung, `03-04` nachzuholen, damit der beste Consent-Indikator verfügbar wird. Das Consent-Urteil stützt sich dann nur auf die Strategen-Antwort (Frage 1).

- **`web-tech-tracking.md` fehlt** → Consent-Frage (Frage 1) wird offen gestellt statt vorausgefüllt. Empfehlung im Gate-File, `03-14` nachzuholen. Keine harte Abhängigkeit.

- **GA4-API Rate-Limit (selten)** → bei `429`/Quota-Fehler 60 s warten, einmal Retry. Bei wiederholtem Limit: bisher erhobene Daten schreiben, Rest als offen markieren, Hinweis im Schluss-Format.

- **OAuth-Token-Problem** → `google-analytics.py` gibt `Analytics-Fehler: ...` mit Exit-Code 2 zurück. Skill bricht sauber ab (nur dieser Skill, kein MTA-Abbruch) mit Hinweis "OAuth-Token erneuern — `google-oauth.py` ausführen". Vermerk `geskippt — auth_fehler` in `status.md`.

- **Outputs existieren bereits** (Re-Run Phase B) → analog `03-04`:
  - **(a) überschreiben**
  - **(b) Backup-und-neu** — alte Versionen nach `audits/_backup/ga4-*-<ISO>.{md,csv,html}`
  - **(c) abbrechen**
  Die Gate-Datei `ga4-datenqualitaet.md` wird bei einem reinen Phase-B-Re-Run **nicht** angefasst — sie bleibt die bestätigte Quelle.

- **Strategin will Gate neu aufrollen** → mit Argument `gate-neu` oder `phase-a erzwingen` aufgerufen, überschreibt der Skill `ga4-datenqualitaet.md` mit einem frischen Vorschlag (`status: vorgeschlagen`) und stoppt wieder. Sinnvoll, wenn sich nach dem ersten Lauf neue Erkenntnisse ergeben haben (z. B. `03-14` lief inzwischen).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/ga4-first-party.md`).
- Markdown + YAML-Frontmatter für `ga4-datenqualitaet.md` und `ga4-first-party.md`, CSV für `ga4-channels.csv` und `ga4-pages.csv` (via `drive.py upsert-text`).
- Standard-Schlussformat im Chat — eigene Variante je Phase (Schritt 18).
- `status.md` wird in jedem Lauf aktualisiert (auch in Phase A und bei Skip), via `drive.py upsert-text`; das Dashboard `reports/index.html` wird in Phase B aktualisiert (Schritt 17).
- HTML-Report basiert auf `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben) — nur Phase B.
- **GA4-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/ga4-*.json`, am Ende von Phase B komprimiert nach Drive `assets/raw/`.
- **GA4-Auth ist unabhängig von gws** — `google-analytics.py` nutzt einen eigenen OAuth-Refresh-Token aus `google-credentials.yaml`, separat von der Drive-Authentifizierung.
- **Session-/Conversion-Werte unverändert lassen** — GA4-Daten sind Roh-Realität; Normalisierung (z. B. Consent-Hochrechnung) ist Aufgabe der Synthese-Skills, der Skill liefert nur den `consent_korrektur_hinweis`.
- **Datenqualität VOR Datenweitergabe** — der zweiphasige Aufbau ist Pflicht. Der Skill gibt niemals GA4-Zahlen in die Synthese, ohne dass das Gate bestätigt und das `belastbarkeit`-Urteil abgeleitet ist.
- **Schwester-Skill-Konsistenz** — Schritt-Struktur, Output-Konventionen und Ton sind bewusst identisch zu `03-04-seo-first-party-gsc` und dem parallel gebauten `03-17-sea-first-party-google-ads` gehalten. HTML-Report-Nummern: GSC `05a`, GA4 `05b`, Google Ads `05c`.
