---
name: 03-05-sea-google-ads-check
description: Erhebt für Kunde und alle bestätigten Wettbewerber den aktuellen Status der Google-Ads-Aktivität via Google Ads Transparency Center (öffentliche Datenquelle, ohne Auth) - aktive Anzeigen, Anzeigentypen (Search/Display/Video/Shopping), Schalt-Zeiträume, Werbetexte, Regionen. Optional ergänzt durch SpyFu-Daten für Spend-Schätzungen wenn Account vorhanden. Output ist audits/google-ads.md (pro Akteur Aktivitäts-Status + Themen-Cluster der Anzeigen) plus audits/google-ads-anzeigen.csv (Roh-Anzeigen) plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Google-Ads-Aktivität prüfen will - auch bei Phrasen wie "Google Ads Check", "wer schaltet Ads", "aktive Google-Anzeigen", "Transparency Center prüfen", "Paid Search Aktivität", "Google Ads Aktivität der Wettbewerber", "SEA Aktivität", "Werbetexte der Konkurrenz". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist; ohne wettbewerber/liste.md läuft der Skill im Kunden-only-Modus.
---

# Google-Ads-Check

Vierter Skill in Stufe 3, erster Ads-Skill. Prüft via **Google Ads Transparency Center** (öffentliche, kostenfreie Datenquelle ohne Auth-Bedarf) für Kunde + alle bestätigten Wettbewerber die aktuelle Google-Ads-Aktivität.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/google-ads.md` — Aktivitäts-Status pro Akteur, Anzeigen-Cluster nach Thema/Produkt, geschätzte Spend-Ranges (wenn SpyFu)
2. **Anzeigen-CSV** `audits/google-ads-anzeigen.csv` — alle erfassten Anzeigen mit Akteur, Anzeigentyp, Schalt-Datum, Werbetexten
3. **HTML-Report** `reports/09-google-ads.html` — Aktivitäts-Matrix, Anzeigen-Galerie pro Akteur, Themen-Cluster-Hinweise

**Wichtige Begrenzung:** Das Transparency Center zeigt **aktive Anzeigen**, **keine historischen Daten** (außer Erst-Schalt-Datum). Spend-Schätzungen sind nur über Drittanbieter (SpyFu, SEMrush) möglich — sind optional, nicht Pflicht.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "Google Ads Check"
- "Wer schaltet Ads"
- "Aktive Google-Anzeigen"
- "Transparency Center prüfen"
- "Paid Search Aktivität"
- "Google Ads Aktivität der Wettbewerber"
- "SEA Aktivität"
- "Werbetexte der Konkurrenz"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`
- Apify-Zugang verfügbar (für Transparency-Center-Scraping — der zentrale Apify-Actor wird in `reference/transparency-center-mapping.md` dokumentiert)
- Empfohlen: `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` und `wettbewerber/liste.md` mit `status: bestaetigt` — sonst Kunden-only-Modus
- Empfohlen: `audits/seo-keyword-cluster.csv` falls schon vorhanden — für Cluster-Cross-Analyse (welche Anzeigen-Themen entsprechen welchem SEO-Cluster?)
- Optional: SpyFu-API-Zugang (`SPYFU_API_KEY` im Environment) für Spend-Schätzungen — wenn nicht vorhanden: Reduced-Modus ohne Spends

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
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/` für Apify-Roh-JSONs.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Lies `wettbewerber/liste.md` aus Drive:

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WB_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -n "$LISTE_ID" ] && [ "$LISTE_ID" != "null" ]; then
  python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/wb-liste.md
fi
```

Wenn vorhanden mit `status: bestaetigt` → Modus **Voll**; sonst → Modus **Kunden-only** mit Hinweis.

Prüfe Apify-Zugang (analog zu anderen Apify-nutzenden Skills). Bei fehlendem Zugang: Abbruch mit Hinweis.

Prüfe SpyFu:

- MCP-Tools mit Prefix `mcp__spyfu__*`? → MCP-Modus
- `SPYFU_API_KEY`? → HTTP-Modus
- Sonst → **SpyFu-Reduced**: keine Spend-Schätzungen, alles andere bleibt

### Schritt 2: Akteurs-Liste zusammenstellen

**Akteure mit Domain** (jeweils Akteurs-Slug + Typ kunde/wettbewerber):

1. **Kunde** — Domain aus `meta.json.website`
2. **Wettbewerber** — pro Eintrag aus `liste.md` mit gültiger `website`-URL. Wie bei `03-01-seo-sichtbarkeit-und-rankings`: **keine Filterung auf `empfehlung_profilieren: ja`** — Transparency-Center-Lookup ist günstig genug für alle WBs.

Domain-Normalisierung wie in `03-01-seo-sichtbarkeit-und-rankings/reference/sistrix-api-nutzung.md` Abschnitt "Domain-Normalisierung" — entferne `www.`, Subdomains nur behalten wenn identitätsrelevant.

### Schritt 3: Existenz-Check Output

Prüfe via `drive.py list-children "$AUDITS_ID"`, ob `google-ads.md` oder `google-ads-anzeigen.csv` schon im Audits-Folder liegen. Wenn ja: fragen (überschreiben / Backup-und-neu nach `audits/_backup/` / abbrechen).

### Schritt 4: Transparency-Center-Scrape pro Akteur

Pro Akteur (siehe `reference/transparency-center-mapping.md`):

1. **URL aufbauen**: `https://adstransparency.google.com/?domain=<domain>` (oder MCP-Equivalent)
2. **Apify-Actor aufrufen** — Standard: `apify/google-ads-transparency-scraper` (falls vorhanden), Fallback: `apify/puppeteer-scraper` mit Custom-Page-Function
3. **Daten extrahieren pro Anzeige**:
   - `werbender_name` (Name des Inserenten — sollte mit Akteur matchen)
   - `werbender_verifiziert` (Google-Verifizierungsstatus)
   - `anzeige_id`
   - `anzeige_typ`: `search | display | video | shopping | demand_gen | unbekannt`
   - `format`: `text | image | video | responsive_search | responsive_display`
   - `erst_schalt_datum` (ISO-8601)
   - `letzte_anzeige_datum` (falls verfügbar)
   - `aktive_in_regionen`: Liste der Länder/Regionen
   - `werbetext_headline` (für Search-Ads die Hauptzeile)
   - `werbetext_beschreibung` (für Search-Ads der Body)
   - `creative_url` (für Display/Video — URL zum Asset)
   - `landingpage_url` (Ziel-URL der Anzeige)

4. **Roh-Daten ablegen** unter `~/.cache/reachx-mta/<slug>/audits/raw/google-ads-<akteurs-slug>.json` (lokaler Cache, am Ende komprimiert nach Drive `assets/raw/`)

5. **Region-Filter** anwenden: nur Anzeigen, die in `meta.json.region` aktiv sind (Default: Deutschland; bei DACH-Kunden auch AT, CH einbeziehen). Anzeigen außerhalb der Zielregion in `regional_irrelevante_anzeigen`-Liste separat ablegen.

### Schritt 5: Akteur nicht im Transparency Center

Google's Transparency Center zeigt **nur verifizierte Werbetreibende**. Wenn ein Akteur dort gar nicht auftaucht, gibt es zwei Möglichkeiten:

- **Keine Google-Ads-Aktivität**: der Akteur schaltet aktuell keine Ads (Standard-Fall)
- **Nicht verifiziert**: kleinere Werbetreibende oder solche, die noch nicht durch Googles Verifizierungs-Prozess sind

Pro Akteur ohne Transparency-Treffer:

- `aktiv_im_transparency_center: false`
- Hinweis im Output, dass das beides bedeuten kann

Bei mehr als 50% der WBs ohne Transparency-Treffer: Auffälligkeit `geringe_ads_dichte_branche` mit Hinweis, dass die Branche generell wenig SEA-aktiv ist (mögliche Differenzierungs-Chance für den Kunden).

### Schritt 6: Anzeigen-Cluster pro Akteur

Pro Akteur die Anzeigen in Themen-Cluster gruppieren (heuristisch — schemagesteuerte Kategorisierung wäre ein zukünftiger Erweiterungs-Skill):

1. **Branded** — Werbetext enthält Eigen-Markennamen → `cluster: branded`
2. **Conquest** — Werbetext oder Landingpage zielt auf WB-Markennamen (selten, aber strategie-relevant) → `cluster: conquest_<wb-slug>`
3. **Produkt-/Themen-Cluster** — Heuristik über Werbetext-Token: gruppiere Anzeigen mit ähnlichem Token-Set → `cluster: thema_<token>`
4. **Generic** — Sammelbecken für unklare Anzeigen

Pro Cluster Statistik: Anzahl Anzeigen, Anzeigentypen-Mix, Erst-Schalt-Datum-Range, Beispiel-Werbetext.

### Schritt 7: SpyFu-Anreicherung (optional)

Wenn SpyFu verfügbar: pro Akteur SpyFu-Domain-Overview ziehen.

Relevante Felder:

- `monatlicher_ads_spend_geschaetzt` (USD-Range, idealerweise konvertiert zu EUR)
- `anzahl_paid_keywords`
- `top_paid_keywords` (Top-10 — separater Datenpunkt, ergänzt das SEO-Picture)
- `historische_ads_aktivitaet` (z. B. "schaltet seit Q3/2023", "Pause Q1/2024")

Ergänze pro Akteur im Aggregat-Markdown unter `spyfu_anreicherung`.

Bei SpyFu-Fehler (Account-Limit, Domain nicht erfasst): Pro-Akteur-Status `spyfu_nicht_verfuegbar: true`, weiter mit nächstem Akteur.

### Schritt 8: Auffälligkeiten

Aus den erhobenen Daten:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_inaktiv_wb_aktiv` | Kunde hat 0 aktive Anzeigen, mindestens 2 WBs sind aktiv | "Kunde schaltet keine Google Ads, beta-solutions hat 14 aktive Anzeigen — Reaktive-Chance auf Search-Anfragen entgeht" |
| `kunde_aktiv_wb_inaktiv` | Kunde hat Anzeigen, alle WBs sind inaktiv | "Kunde dominiert SEA in der Wettbewerbsgruppe — Position halten" |
| `conquest_aktivitaet` | Mindestens 1 WB bewirbt Kunden-Markennamen | "Wettbewerber alpha-tech bewirbt aktiv den Markennamen des Kunden — Conquest-Brand-Protection prüfen" |
| `kunde_macht_conquest` | Kunde bewirbt WB-Markennamen | "Kunde betreibt Conquest-Marketing gegen beta-solutions — strategisch beabsichtigt?" |
| `geringe_ads_dichte_branche` | >50% WBs ohne Transparency-Treffer | "Geringe SEA-Dichte in der Branche — möglicher First-Mover-Vorteil für SEA-Kampagnen" |
| `hohe_ads_dichte_branche` | Alle WBs aktiv mit >10 Anzeigen | "Hohe SEA-Konkurrenz — Spends werden teuer, Differenzierung über Long-Tail oder spezifische Personas empfehlen" |
| `werbetext_cluster_dominant` | >70% der WB-Anzeigen nutzen identische Differenzierungs-Aussagen | "Wettbewerber-Werbetexte sind sehr homogen ('persönlich', 'individuell', 'erfahren') — Differenzierungs-Chance über andere Tonalität" |
| `landingpage_qualitaet_inkonsistent` | Anzeigen führen auf Homepage statt auf dediziertere Landingpages (heuristisch über URL-Tiefe) | "Wettbewerber X leitet alle Anzeigen auf die Homepage — schwache Landingpage-Strategie, möglicher Vorteil bei dedicated PPC-Landingpages" |

Pro Auffälligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure.

### Schritt 9: CSV-Output `audits/google-ads-anzeigen.csv`

Eine Zeile pro Anzeige × Akteur. Schema in `reference/ads-output-schema.md` Abschnitt "Anzeigen-CSV".

Spalten:

```
akteurs_slug, akteurs_typ, akteurs_name, werbender_name, werbender_verifiziert,
anzeige_id, anzeige_typ, format, erst_schalt_datum, letzte_anzeige_datum,
aktive_in_regionen, in_zielregion, werbetext_headline, werbetext_beschreibung,
landingpage_url, landingpage_tiefe, creative_url, cluster, datenstand_iso
```

### Schritt 10: Aggregat-Markdown `audits/google-ads.md`

Frontmatter mit:

- Skill-Metadaten, Quellen-Provenienz (Apify-Actor + Datum + Anzahl Akteure)
- Aktivitäts-Matrix pro Akteur:
  - `aktiv_im_transparency_center: true | false`
  - `anzahl_aktive_anzeigen: <int>`
  - `anzahl_in_zielregion: <int>`
  - `anzeigentypen_verteilung` (search/display/video/shopping)
  - `aelteste_schalt_datum`
  - `juengste_schalt_datum`
  - `cluster_anzahl: <int>`
  - `spend_geschaetzt_eur_min`, `spend_geschaetzt_eur_max` (wenn SpyFu)
- Branchenweite Aggregat-Statistik
- Auffälligkeiten

Body:

- Übersicht (Anzahl aktive Akteure, Top-Werber, Branchen-SEA-Dichte)
- Akteurs-Vergleichs-Tabelle
- Pro Akteur ein Sub-Block mit:
  - Aktivitätsstatus
  - Anzeigentypen-Verteilung
  - Top-Anzeigen (mit Werbetext-Auszug, max 5)
  - Themen-Cluster im Akteurs-Portfolio
  - SpyFu-Daten falls vorhanden
- Themen-Cluster-Übersicht über alle WBs (was wird beworben?)
- Auffälligkeiten

### Schritt 11: HTML-Report `reports/09-google-ads.html`

Aus `reports/_shell.html`:

- **Stat-Strip oben**: Akteure aktiv im TC, Anzahl Anzeigen gesamt, Top-Werber, Anzahl Themen-Cluster, Anzahl Auffälligkeiten
- **Sticky-TOC** zu allen Sektionen
- **Aktivitäts-Heatmap** (Akteur × Anzeigentyp): zeigt schnell, wer welche Format-Mischung nutzt
- **Pro Akteur** ein `details class="skill"`-Block mit:
  - Aktivitätsstatus + Volumen
  - Anzeigentypen-Verteilung (kleine ASCII-Balken)
  - Top-5-Anzeigen-Karten mit Werbetext-Auszug und Landingpage-Link
  - SpyFu-Spend-Schätzung (falls vorhanden) als Stat-Mini
- **Themen-Cluster-Übersicht**: für jeden Cluster eine Karte mit Akteurs-Verteilung
- **Auffälligkeiten** als `.suggestion`-Block
- Footer

### Schritt 11b: Outputs nach Drive hochladen

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "google-ads.md" \
  ~/.cache/reachx-mta/<slug>/google-ads.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "google-ads-anzeigen.csv" \
  ~/.cache/reachx-mta/<slug>/google-ads-anzeigen.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "09-google-ads.html" \
  ~/.cache/reachx-mta/<slug>/09-google-ads.html "text/html"
```

### Schritt 12: Dashboard-Update und status.md

Standard-Pattern: `reports/index.html` und `status.md` aus Drive lesen, anpassen, zurückschreiben — siehe `contracts.md` Abschnitt 3 und 7.

- `03-05-sea-google-ads-check` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z. B. "5 von 9 Akteuren inaktiv im TC")
- Reports-Liste um `09-google-ads.html`
- Stat-Strip aktualisieren
- `naechster_empfohlen`: `03-06-sea-meta-ads-library-check` (analoge Mechanik, gleiche Apify-Pattern, kann direkt anschließen)

### Schritt 13: Standard-Schlussformat im Chat

```
✓ 03-05-sea-google-ads-check abgeschlossen.

Outputs:
- audits/google-ads.md — Aggregat mit Aktivitäts-Matrix und Themen-Clustern
- audits/google-ads-anzeigen.csv — Roh-Anzeigen (N Zeilen)
- reports/09-google-ads.html — Strategen-Report
Status aktualisiert in: status.md

SEA-Lage:
- Akteure aktiv im TC:        M von N
- Anzeigen in Zielregion:     A
- Top-Werber:                 <akteur> mit <N> Anzeigen
- Themen-Cluster:             T
- Spend-Schätzung Kunde:      <Range EUR> [wenn SpyFu]
- Spend-Schätzung Top-WB:     <Range EUR> [wenn SpyFu]

[Wenn Auffälligkeiten:]
⚠ SEA-Insights:
- (1-3 Top-Auffälligkeiten)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestätigt — SEA-Lage nur für den Kunden, kein Branchen-Benchmark.

[Wenn SpyFu nicht verfügbar:]
ℹ Keine Spend-Schätzungen
- SpyFu-Zugang nicht verfügbar — Aktivitäts-Status ist da, Spends fehlen.

Nächste Schritte:
1. 03-06-sea-meta-ads-library-check — Meta-Ads-Aktivität, gleiche Apify-Mechanik
2. (parallel möglich) 03-07-sea-linkedin-ads-library-check — LinkedIn-Ads
3. (parallel möglich) 03-14-web-tech-und-tracking — Tech-Stack + Tracking

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/transparency-center-mapping.md` — Apify-Actor-Optionen, URL-Patterns, Datenfelder, Limitierungen des Transparency Centers
- `reference/ads-output-schema.md` — Markdown- und CSV-Schema für die Outputs, Validierungs-Regeln

## Edge Cases

- **Domain hat sich umgezogen** → Transparency Center erkennt das oft nicht automatisch. Skill prüft via HEAD-Request, ob die Domain noch lebt und ob es eine Redirect-Chain gibt. Bei Redirect: beide Domains abfragen, im Output beide Ergebnisse dokumentieren.

- **Sehr viele aktive Anzeigen (>200 pro Akteur)** → Hard-Cap bei Top-100 nach Erst-Schalt-Datum absteigend (jüngste zuerst). Im Body Hinweis "Akteur hat >200 aktive Anzeigen, Top-100 ausgewertet."

- **Akteur betreibt Multi-Domain-Strategie** (z. B. eigene Shop-Domain + Marken-Domain): wird auf Standard-Domain abgefragt. Wenn Stratege Multi-Domain wünscht: Override "auch <weitere-domain> abfragen".

- **Werbetexte enthalten dynamische Platzhalter** ({Keyword}, {Location}) → werden roh übernommen, im Output mit Hinweis "Anzeige nutzt dynamische Insertion".

- **Transparency Center liefert keine Anzeige-IDs** (manchmal nur Snapshots) → Skill generiert Hash-basierte ID aus `werbender_name + erst_schalt_datum + werbetext_headline`. Dadurch sind Re-Runs stabil.

- **SpyFu-Account-Limit (z. B. 50 Lookups/Monat)** → Skill prüft vorab Quota (falls API liefert), bei Überschreitung: SpyFu-Anreicherung nur für Kunde + Top-3-WB nach Anzahl-Anzeigen, Rest ohne Spend.

- **Apify-Actor scheitert (TC-UI-Änderung)** → Fallback auf manuellen Mini-Workflow: dem Strategen die TC-URLs aller Akteure ausgeben, mit Bitte, manuell zu prüfen. Im Output ein "manueller_check_erforderlich"-Block, der die Akteure listet.

- **Konflikt-Domain** (Kunden- und WB-Domain führen auf denselben Konzern): wird selten, aber wichtig markiert. Skill aggregiert Anzeigen unter beiden Akteurs-Slugs, im Body Hinweis.

- **Internationale Akteure** (TC zeigt auch andere Regionen) → Region-Filter (Schritt 4.5) anwenden. Anzeigen außerhalb der Zielregion in eigener Sektion "internationale_aktivitaet" listen — kann für Strategen-Insight interessant sein (zeigt z. B. wo der WB schon Märkte angeht, die der Kunde noch nicht bedient).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/google-ads.md`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Anzeigen (via `drive.py upsert-text`)
- Standard-Schlussformat
- `status.md` und Dashboard werden aktualisiert (`drive.py upsert-text`)
- HTML-Report aus `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **TC-Roh-Daten** lokal im Arbeits-Cache `~/.cache/reachx-mta/<slug>/audits/raw/google-ads-<akteurs-slug>.json`, am Ende komprimiert nach Drive `assets/raw/`
- **Werbetexte unverändert** lassen — Originaltexte sind die Datenbasis, keine Übersetzungen oder Umformulierungen
- **Spend-Schätzungen sind Ranges**, niemals Punktschätzungen (siehe Architektur-Entscheidung 10 in `contracts.md`)
