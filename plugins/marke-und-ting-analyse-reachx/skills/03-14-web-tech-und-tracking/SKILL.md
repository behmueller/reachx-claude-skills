---
name: 03-14-web-tech-und-tracking
description: Erhebt für Kunde und Wettbewerber den Tech-Stack (CMS, Frontend, Hosting, Marketing-Tools) via BuiltWith bzw. Wappalyzer, das Tracking-Setup (GA4, GTM, Consent-Tool, Conversion-Pixel, Heatmaps, A/B-Tests) und Core Web Vitals (LCP/INP/CLS plus Performance-Score) via PageSpeed Insights für Mobile und Desktop. Output ist audits/web-tech-tracking.md mit Tech-Matrix, Tracking-Lücken und Performance-Vergleich, plus audits/tech-stack.csv und audits/pagespeed.csv als Roh-Datenbasis, plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Tech-Stack, Tracking oder Web-Performance prüfen will - auch bei "Tech-Stack prüfen", "BuiltWith-Check", "Wappalyzer-Audit", "welches CMS nutzt", "Tracking-Audit", "Tracking-Lücken", "Consent-Check", "PageSpeed-Check", "Core Web Vitals", "Lighthouse-Vergleich", "Performance-Audit", "GA4-Erkennung", "GTM-Check", "Conversion-Pixel-Check". Setzt 01-01-mta-projekt-init voraus; ohne wettbewerber/liste.md läuft der Kunden-only-Modus.
---

# Website-Tech-und-Tracking-Audit

Stufe-3-Audit-Skill (Website-Familie). Erhebt fuer Kunde + alle bestaetigten Wettbewerber drei verzahnte Audit-Achsen in einem Lauf:

1. **Tech-Stack** via BuiltWith (Primaer) oder Wappalyzer (Fallback) — CMS, Frontend-Frameworks, E-Commerce-Plattform, Server/Hosting/CDN, Marketing-Tools, Analytics-Tools
2. **Tracking-Setup** — Google Analytics (GA4), Google Tag Manager (Container-ID), Consent-Tool (Usercentrics, Cookiebot, OneTrust, etc.), Conversion-Pixel (Meta, LinkedIn, Google Ads, TikTok), Heatmap-Tools (Hotjar, Microsoft Clarity, FullStory), A/B-Testing-Tools
3. **Performance** via PageSpeed Insights API — Core Web Vitals (LCP, INP, CLS) fuer Mobile + Desktop, Performance-Score 0-100, Top-3 Optimierungs-Empfehlungen, CrUX-Real-User-Daten vs. Lighthouse-Lab-Daten

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/web-tech-tracking.md` — Tech-Matrix, Tracking-Luecken-Tabelle, Performance-Vergleich, Auffaelligkeiten
2. **Tech-CSV** `audits/tech-stack.csv` und **Performance-CSV** `audits/pagespeed.csv` — Roh-Datenbasis fuer Folge-Skills und Excel-Auswertung
3. **HTML-Report** `reports/12-website-tech.html` — Master-Matrix, Tracking-Luecken-Heatmap, CWV-Vergleichsbalken

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

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

- "Tech-Stack pruefen"
- "BuiltWith-Check"
- "Wappalyzer-Audit"
- "Welches CMS nutzt [Akteur]"
- "Tracking-Audit"
- "Tracking-Luecken finden"
- "Consent-Check"
- "PageSpeed-Check"
- "Core Web Vitals fuer Kunde und Wettbewerber"
- "Lighthouse-Vergleich"
- "Performance-Audit Website"
- "GA4-Erkennung"
- "GTM-Check"
- "Conversion-Pixel-Check"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- Tooling-Zugang fuer mindestens **einen** der drei Achsen:
  - **BuiltWith** via API-Key `BUILTWITH_API_KEY` ODER MCP-Tool `mcp__builtwith__*` ODER Wappalyzer-Fallback via Apify-Actor (`apify/wappalyzer` oder vergleichbar). Apify-Credential-Prüfung: ausschließlich `[ -n "$APIFY_TOKEN" ]` — kein Scannen von `~/.zshrc` o. ä. (contracts.md Abschnitt 11). Vor Apify-Actor-Nutzung Health-Check via `mcp__apify__fetch-actor-details`: bei `Session ID not found` sofort abbrechen.
  - **PageSpeed Insights** via Google-API (Endpoint kostenfrei, `PAGESPEED_API_KEY` optional fuer hoehere Rate-Limits). **Pflicht-Check zu Beginn:** `[ -n "$PAGESPEED_API_KEY" ]` — wenn gesetzt, PSI mit Key nutzen (höheres Quota, ca. 400 Anfragen/100 Sekunden). Wenn **nicht** gesetzt: anonymer Zugang (ca. 25 Anfragen/100 Sekunden) — bei HTTP 429 PSI-Calls auf die **Kunden-Domain begrenzen** (Wettbewerber-Calls überspringen) und im Output `performance_audit_nur_kunde: true` markieren. **Hinweis:** Für CrUX-Real-User-Daten (Origin-Level) gibt es eine eigene CrUX-API (`https://chromeuxreport.googleapis.com/v1/records:queryRecord`) mit separatem `CRUX_API_KEY` — wenn vorhanden, für detailliertere Real-User-Daten nutzen; ansonsten verlässt der Skill sich auf die CrUX-Daten, die PageSpeed Insights mitliefert.
- Empfohlen: `wettbewerber/liste.md` mit `status: bestaetigt` → voller Vergleich. Sonst Kunden-only-Modus mit Hinweis.
- Reduced-Modus moeglich: Wenn nur BuiltWith ODER nur PageSpeed verfuegbar ist, laeuft der Skill nur mit der verfuegbaren Achse durch — entsprechende Felder werden im Output als `tech_audit_lief: false` bzw. `performance_audit_lief: false` markiert.

## Ablauf

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Ermittle MTA-Folder via `drive.py` und lies `meta.json` aus Drive:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Wenn die MTA nicht im Cache ist oder `meta.json` fehlt:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Lies `wettbewerber/liste.md` aus Drive (`find_by_name(WB_ID, "liste.md")` → `read_text`). Bei `status: bestaetigt` → Modus **Voll** (Kunde + alle WBs). Bei `status: vorgeschlagen` → Warnung mit Option, im Kunden-only-Modus weiterzumachen. Bei fehlender Datei → Kunden-only-Modus mit Hinweis im Schluss-Format.

Pruefe Tooling-Zugang (Details in `reference/tools-api-nutzung.md` Abschnitt "Zugangs-Reihenfolge"):

- **Tech-Stack-Achse**:
  - MCP-Tools `mcp__builtwith__*` vorhanden? → BuiltWith-MCP-Modus
  - `BUILTWITH_API_KEY` im Environment? → BuiltWith-HTTP-Modus
  - Apify verbunden und Wappalyzer-Actor verfuegbar? → Wappalyzer-Fallback-Modus
  - Alles drei fehlt → `tech_audit_lief: false`, Skill laeuft mit den anderen Achsen weiter

- **Tracking-Achse**:
  - Tracking-Erkennung lebt entweder im BuiltWith-Result (BuiltWith liefert Analytics + Marketing-Tools) oder wird im Wappalyzer-Fallback eingelesen.
  - Wenn beides nicht verfuegbar ist, hilft eine leichtgewichtige HTML-Inspektion (Apify `apify/puppeteer-scraper` oder `apify/website-content-crawler` mit Render-Mode), die nach den bekannten Tracking-Signaturen sucht — Details in `reference/tools-api-nutzung.md` Abschnitt "Tracking-Signaturen".

- **Performance-Achse**:
  - PageSpeed Insights v5 ist eine oeffentliche kostenfreie Google-API. `PAGESPEED_API_KEY` ist optional (hoeheres Rate-Limit), sonst auch ohne Key nutzbar — Endpoint funktioniert.
  - Bei Netzwerk-Fehler oder Quota-Ueberschreitung: Retry-Logik in `reference/tools-api-nutzung.md` Abschnitt "PageSpeed-Quotas".

Wenn **alle drei Achsen** fehlen: Abbruch mit klarem Hinweis.

### Schritt 2: Akteurs-Liste und URL-Liste zusammenstellen

Pro Akteur (mit `akteurs_slug`, `akteurs_typ` kunde/wettbewerber, `akteurs_name`):

1. **Kunde** — URL aus `meta.json.website`. URL normalisieren (siehe `reference/tools-api-nutzung.md` Abschnitt "URL-Normalisierung").
2. **Wettbewerber** — pro Eintrag in `wettbewerber/liste.md` mit gueltiger `website`-URL. Alle drei Kategorien (`kunde_genannt`, `regional`, `best_practice_ueberregional`) werden uebernommen, Filter wie bei `03-01-seo-sichtbarkeit-und-rankings` — auch `empfehlung_profilieren: nein` werden erfasst, weil Tech-Daten guenstig sind. Eintraege mit `website: null` ausschliessen.

Pro Akteur eine **Audit-URL**: in der Regel die in `meta.json` oder `liste.md` genannte Hauptdomain-URL (z. B. `https://www.kunde.de/`). Bei sub-domain-getrennten Akteuren die genannte Subdomain nutzen.

Bei mehr als 15 Akteuren: Hinweis im Schluss-Format, dass der Lauf laenger dauern wird (PageSpeed ~30-60s pro URL pro Strategy).

### Schritt 3: Tech-Stack-Audit pro Akteur

Pro Akteur Tech-Stack-Lookup (Details in `reference/tools-api-nutzung.md` Abschnitt "BuiltWith-API" und "Wappalyzer-Fallback"):

1. **Primaer: BuiltWith**
   - Endpoint `domain.json?KEY=...&LOOKUP=akteur-url` (HTTP) oder MCP-Tool-Aufruf
   - Liefert eine umfassende Technologie-Liste, kategorisiert (Analytics, Tag-Management, JS-Frameworks, CMS, E-Commerce, CDN, Hosting-Provider, Marketing-Automation, Consent-Tool, Conversion-Pixel etc.)
   - Roh-Antwort lokal cachen unter `~/.cache/reachx-mta/<slug>/audits/raw/builtwith-<akteurs-slug>.json` und am Ende des Laufs (zusammen mit allen Roh-JSONs) nach Drive in `assets/raw/` hochladen (per `drive.py upsert-text`)

2. **Fallback: Wappalyzer via Apify**
   - Wenn BuiltWith fehlt oder eine Domain nicht enthaelt: `apify/wappalyzer` (oder vergleichbarer Community-Actor) ueber die Apify-MCP aufrufen
   - Liefert vergleichbares Schema, aber weniger Detail-Tiefe und Marketing-Stack-Coverage
   - Roh-Antwort lokal cachen, am Ende nach Drive `assets/raw/wappalyzer-<akteurs-slug>.json`
   - Im Markdown-Frontmatter `tech_audit_quelle: wappalyzer` markieren, damit der Stratege die Tiefe-Differenz versteht

3. **Normalisierung** in feste Kategorien (siehe `reference/tech-output-schema.md` Abschnitt "Tech-Kategorien"):
   - `cms` (WordPress, TYPO3, Drupal, Webflow, Contentful, Shopware, Adobe Experience Manager, etc.)
   - `frontend_framework` (React, Vue, Angular, Next.js, Nuxt, Astro, Svelte etc.)
   - `ecommerce_plattform` (Shopify, Shopware, WooCommerce, Magento, BigCommerce — null wenn nicht E-Commerce)
   - `server_hosting` (Vercel, Netlify, AWS, Cloudflare-Pages, eigener Server, deutsche Hoster wie Hetzner / 1&1 IONOS)
   - `cdn` (Cloudflare, Fastly, Akamai, Amazon CloudFront)
   - `marketing_automation` (HubSpot, Mailchimp, Salesforce/Pardot, ActiveCampaign, Klaviyo, Brevo/SendinBlue)
   - `analytics_tools` (alle erkannten Analytics-Tools — wird in Schritt 4 vertieft)
   - `programming_language` (PHP, Python, Ruby, Node.js — soweit erkannt)

   Bei Mehrfach-Erkennung pro Kategorie (z. B. WP + Shopify-Sub-Shop) Liste in der Reihenfolge "Primaer zuerst" — Primaer ist der, der die meiste Site abdeckt.

### Schritt 4: Tracking-Setup-Audit pro Akteur

Aus den Tech-Stack-Daten oder via separate Signatur-Erkennung (siehe `reference/tools-api-nutzung.md` Abschnitt "Tracking-Signaturen") fuer jeden Akteur die folgenden Boolean-Felder + ggf. Detail-Felder bestimmen:

| Feld | Inhalt | Beispiele |
|---|---|---|
| `ga4_vorhanden` | bool | Google Analytics 4 erkannt (Measurement-ID `G-XXXX`) |
| `ga4_id` | string oder null | Falls aus HTML extrahierbar |
| `universal_analytics_vorhanden` | bool | Legacy UA (`UA-XXXX`) — sollte 2026 nicht mehr existieren, Auffaelligkeit wenn doch |
| `gtm_vorhanden` | bool | Google Tag Manager Container erkannt |
| `gtm_id` | string oder null | Container-ID `GTM-XXXX` |
| `consent_tool` | string oder null | Usercentrics / Cookiebot / OneTrust / Borlabs / CCM19 / klaro / sonstige Eigenloesung |
| `consent_tool_strikt` | bool oder null | Wird vor Tracking-Skripten geladen (Heuristik aus dem Script-Order) |
| `meta_pixel_vorhanden` | bool | Facebook/Meta Pixel erkannt |
| `meta_pixel_id` | string oder null | |
| `linkedin_insight_vorhanden` | bool | LinkedIn Insight Tag erkannt |
| `linkedin_partner_id` | string oder null | |
| `google_ads_conversion_vorhanden` | bool | Google Ads Conversion-Tag erkannt |
| `tiktok_pixel_vorhanden` | bool | |
| `heatmap_tool` | string oder null | Hotjar / Microsoft Clarity / FullStory / Mouseflow / Lucky Orange |
| `ab_testing_tool` | string oder null | Google Optimize (deprecated), VWO, Optimizely, AB-Tasty, Convertize |
| `marketing_automation_tool` | string oder null | siehe Schritt 3 — `marketing_automation`-Kategorie |

Wenn das Tooling Tracking-IDs nicht zuverlaessig extrahiert: Felder leer lassen (null) und im Frontmatter `tracking_ids_extrahiert: partiell` setzen, damit der Stratege nicht falsche Sicherheit hat.

**Tracking-Konformitaets-Check** (heuristisch):

- Wenn `ga4_vorhanden=true` und `consent_tool=null` → Auffaelligkeit `consent_unkonform`
- Wenn `meta_pixel_vorhanden=true` und `consent_tool=null` → Auffaelligkeit `consent_unkonform`
- Wenn `universal_analytics_vorhanden=true` → Auffaelligkeit `legacy_tracking`
- Wenn `consent_tool!=null` und `consent_tool_strikt=false` → Hinweis: Consent-Tool zwar vorhanden, Skripte werden aber moeglicherweise vor Einwilligung geladen — manuelle Pruefung empfohlen

### Schritt 5: Performance-Audit pro Akteur (PageSpeed Insights)

Pro Akteur **zwei** PageSpeed-Calls (Mobile + Desktop). Details in `reference/tools-api-nutzung.md` Abschnitt "PageSpeed-API":

```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
?url=https://akteur-url
&strategy=mobile
&category=performance
&key=PAGESPEED_API_KEY   (optional)
```

Pro Call extrahieren:

- **Performance-Score** 0-100 (aus `lighthouseResult.categories.performance.score` × 100)
- **Lighthouse-Lab-Werte** (controlled environment): LCP, FCP, TBT, CLS, Speed-Index — aus `lighthouseResult.audits.{metric}.numericValue`
- **CrUX-Real-User-Daten** (echte Nutzer der letzten 28 Tage, wenn Domain in CrUX-Datenbank): LCP-p75, INP-p75, CLS-p75 — aus `loadingExperience.metrics.*` und `originLoadingExperience.metrics.*`
- **Top-3 Lighthouse-Empfehlungen**: aus `lighthouseResult.audits` die Audits mit `score < 1.0` und hoechstem `details.overallSavingsMs` — als Titel + Savings-Estimate

Roh-Antwort lokal cachen und am Ende des Laufs nach Drive in `assets/raw/pagespeed-<akteurs-slug>-mobile.json` und `assets/raw/pagespeed-<akteurs-slug>-desktop.json` hochladen.

**CrUX vs. Lab dokumentieren**: Wenn CrUX-Daten fehlen (`loadingExperience` nicht in der Antwort) → im Output explizit `crux_daten: false` markieren. Das passiert oft bei kleinen Sites unterhalb der CrUX-Schwellwerte.

### Schritt 6: CSV-Outputs

**`audits/tech-stack.csv`** — eine Zeile pro Akteur, breite Spalten (siehe `reference/tech-output-schema.md` Abschnitt "tech-stack.csv-Schema"):

```
akteurs_slug, akteurs_typ, akteurs_name, domain, tech_audit_quelle,
cms, cms_version, frontend_framework, ecommerce_plattform, server_hosting, cdn,
marketing_automation, programming_language,
ga4_vorhanden, ga4_id, universal_analytics_vorhanden, gtm_vorhanden, gtm_id,
consent_tool, consent_tool_strikt,
meta_pixel_vorhanden, meta_pixel_id, linkedin_insight_vorhanden, linkedin_partner_id,
google_ads_conversion_vorhanden, tiktok_pixel_vorhanden,
heatmap_tool, ab_testing_tool,
datenstand_iso
```

**`audits/pagespeed.csv`** — zwei Zeilen pro Akteur (Mobile + Desktop), schmale Spalten:

```
akteurs_slug, akteurs_typ, akteurs_name, domain, strategy,
performance_score, lcp_lab_ms, fcp_lab_ms, tbt_lab_ms, cls_lab, speed_index_lab_ms,
crux_daten, lcp_crux_p75_ms, inp_crux_p75_ms, cls_crux_p75,
top_empfehlung_1, top_empfehlung_2, top_empfehlung_3,
rerun_empfohlen, datenstand_iso
```

`rerun_empfohlen` (bool): `true` wenn der Lauf mit HTTP-429-Fehler abgebrochen wurde oder nur der anonyme Quota ausgeschöpft war. Signal für den Strategen: diese Zeile mit `PAGESPEED_API_KEY` nochmals ziehen.

Beide CSVs sind Roh-Datenbasis — Folge-Skills (`04-02-kanal-chancen-analyse`) lesen primaer aus den CSVs.

CSVs lokal in `~/.cache/reachx-mta/<slug>/` generieren, dann via `drive.py upsert-text "$AUDITS_ID" "tech-stack.csv" /tmp/tech-stack.csv "text/csv"` und analog `pagespeed.csv` nach Drive hochladen.

### Schritt 7: Aggregat-Markdown `audits/web-tech-tracking.md`

Schreibe nach Drive via `drive.py upsert-text "$AUDITS_ID" "web-tech-tracking.md" /tmp/web-tech-tracking.md "text/markdown"`.

Format nach `reference/tech-output-schema.md` Abschnitt "Markdown-Schema". YAML-Frontmatter enthaelt:

- Skill-Metadaten, Recherche-Provenienz (Tech-Tool: builtwith/wappalyzer, PageSpeed-Datenstand)
- Akteurs-Liste mit zentralen Stack-Feldern + Tracking-Booleans + Performance-Scores (Mobile/Desktop)
- Aggregat-Statistiken (CMS-Verteilung, GA4-Coverage, Consent-Coverage, CWV-Bestanden-Quote pro Strategy)
- Auffaelligkeiten (siehe Schritt 8)

Body strukturiert nach:

- **Uebersicht** (3-5 Saetze): Tech-Stack-Vielfalt in der Akteurs-Gruppe, Kunden-Position, Top-1-2-Auffaelligkeiten
- **Tech-Stack-Matrix** (Tabelle pro Akteur × Tech-Kategorie)
- **Tracking-Setup-Matrix** (Tabelle pro Akteur × Tracking-Tool-Familie, Symbole ✓ / – / ⚠ fuer "vorhanden / fehlt / unkonform")
- **Performance-Vergleich** (Tabelle pro Akteur Mobile vs. Desktop, mit Cell-Color-Hint stark/mittel/schwach gemaess CWV-Schwellwerten)
- **Pro Akteur** Mini-Sektion mit Tech-Detail, Tracking-Detail, Top-3 PageSpeed-Empfehlungen
- **Auffaelligkeiten** als eigene Sektion

CWV-Bestand-Schwellwerte (gemaess Google):

| Metrik | gut | verbesserungsbeduerftig | schwach |
|---|---|---|---|
| LCP | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

### Schritt 8: Auffaelligkeiten

Aus den erhobenen Daten die strategisch relevanten Beobachtungen extrahieren:

| Typ | Ausloeser | Beispiel |
|---|---|---|
| `tracking_luecke_kunde` | Kunde fehlt mindestens eines von GA4 / GTM / Consent-Tool | "Kunde hat kein GA4 und kein GTM — keine Daten-Basis fuer Optimierung" |
| `consent_unkonform` | Tracking laeuft ohne Consent-Tool | "Kunde laedt Meta-Pixel ohne Consent-Tool — DSGVO-Risiko" |
| `legacy_tracking` | Universal Analytics noch aktiv | "Universal Analytics (UA-Property) bei Kunde noch aktiv — wird nicht mehr von Google bedient" |
| `kunde_core_web_vitals_schwach` | Kunden-LCP > 2.5s oder CLS > 0.1 (Mobile) | "Kunden-LCP Mobile bei 4.2s (Schwellwert 2.5s) — SEO-Risiko und UX-Problem" |
| `wettbewerber_modern_tech` | >=2 WBs nutzen modernen Stack (React/Vue/Next/Nuxt + CDN), Kunde nicht | "3 von 5 Wettbewerbern bauen auf Next.js + Vercel; Kunden-WordPress wirkt im Vergleich behaebig" |
| `cms_branchen_outlier` | Kunde nutzt CMS, das niemand sonst in der Branchen-Gruppe nutzt | "Kunde nutzt TYPO3; alle 7 Wettbewerber nutzen WordPress oder Webflow — schwerere Skalierung" |
| `conversion_pixel_fehlt` | Kunde wirbt (Google Ads-Aktivitaet aus 03-05-sea-google-ads-check) aber hat keinen Conversion-Pixel | "Kunde schaltet Google Ads, aber Google-Ads-Conversion-Tag fehlt — Conversion-Tracking nicht moeglich" |
| `heatmap_tool_branche_dominant` | Mehrheit der WBs nutzt Heatmap-Tool, Kunde nicht | "5 von 7 Wettbewerbern nutzen Hotjar oder Microsoft Clarity — Kunde hat kein UX-Analytics" |
| `marketing_automation_luecke` | >=2 WBs haben Marketing-Automation, Kunde nicht | "Wettbewerber X (HubSpot) und Y (Pardot) haben Marketing-Automation; Kunde nicht — Lead-Nurturing-Luecke" |
| `kunde_performance_top` | Kunden-Performance-Score >=90 (Mobile) und Top-2 in der Gruppe | "Kunde fuehrt Performance-Vergleich mit Score 94 (Mobile) — Wettbewerbsvorteil halten" |

Jede Auffaelligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung. Mindestens 8 Auffaelligkeits-Typen sind aufgefuehrt — pro Lauf werden nur die zutreffenden ausgegeben.

Cross-Check mit anderen Audit-Outputs, wenn vorhanden (via `drive.py find_by_name(AUDITS_ID, "...")` → `read_text`):

- `audits/google-ads.md`: Wenn Kunde dort Aktivitaet zeigt, aber hier `google_ads_conversion_vorhanden=false` → Auffaelligkeit `conversion_pixel_fehlt` mit hoher Relevanz
- `audits/seo-sichtbarkeit.md`: Wenn Kunden-VI niedrig und LCP schwach → in der Auffaelligkeit den moeglichen Zusammenhang andeuten (Core-Web-Vitals sind Ranking-Signal)

### Schritt 9: HTML-Report `reports/12-website-tech.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lade `_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), fülle die Platzhalter, schreibe lokal in den Cache, lade hoch via `drive.py upsert-text "$REPORTS_ID" "12-website-tech.html" /tmp/report.html "text/html"`.

Aus `reports/_shell.html` einen Audit-Report bauen:

- `{{TITLE}}` → `Website-Tech und Tracking · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · Website`
- `{{DISPLAY_NAME}}` → `Website-Tech, Tracking und Performance: KUNDE`
- `{{META_LINE}}` → `BuiltWith/Wappalyzer + PageSpeed Insights · Datenstand DATUM · N Akteure · Generiert: heute`
- `{{MAIN_CONTENT}}`:
  - **Stat-Strip oben**: CMS-Diversitaet (z. B. "5 CMS-Familien"), Kunden-Performance Mobile, Kunden-Performance Desktop, Anzahl Tracking-Luecken-Auffaelligkeiten, Anzahl CWV-bestanden Akteure
  - **Sticky-TOC**: Tech-Matrix, Tracking-Matrix, Performance, Pro-Akteur-Sektionen, Auffaelligkeiten
  - **Tech-Stack-Matrix** als `table.data` (Akteure × Tech-Kategorien, Zellen mit Tool-Namen oder `–`)
  - **Tracking-Setup-Heatmap** als `table.data` (Akteure × Tracking-Familien, Zellen mit `.badge.stark/mittel/schwach` je nach Status)
  - **Performance-Vergleich** als zwei Tabellen (Mobile, Desktop) mit Performance-Score + LCP + INP + CLS, Zellen-Badge gemaess CWV-Schwellwerten
  - **Pro Akteur** `details.skill[data-status=...]`-Block (default: Kunde + Top-2-Performance aufgeklappt, Rest zugeklappt) mit: Tech-Detail, Tracking-Detail, PageSpeed-Top-3-Empfehlungen Mobile + Desktop
  - **Auffaelligkeiten-Block** als `.suggestion`-Block: Top 3-5 strategische Beobachtungen mit Handlungs-Empfehlungen
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · Website-Tech-und-Tracking-Audit`

### Schritt 10: Dashboard-Update

Lies `reports/index.html` aus Drive (`find_by_name(REPORTS_ID, "index.html")` → `read_text`), patche die Sektionen, lade zurück via `drive.py upsert-text "$REPORTS_ID" "index.html" ... "text/html"`. Aktualisiere `reports/index.html`:

- Stat-Strip um Kunden-Performance-Score Mobile + Tracking-Luecken-Indicator ergaenzen
- "Erledigt"-Sektion erweitern um `03-14-web-tech-und-tracking`
- Reports-Liste um `12-website-tech.html` erweitern
- "Naechster empfohlener Schritt": kontextabhaengig, in der Regel `03-15-web-content-inventur` oder ein weiterer Audit-Skill

### Schritt 11: `status.md` aktualisieren

Nach Regeln aus `contracts.md` Abschnitt 3. `status.md` aus dem MTA-Root lesen (`find_by_name(FOLDER_ID, "status.md")` → `read_text`), patchen, zurück per `drive.py upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"`:

- `03-14-web-tech-und-tracking` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen (z. B. "BuiltWith fehlte fuer 2 Akteure, Wappalyzer-Fallback genutzt" oder "PageSpeed-Reduced-Modus weil PAGESPEED_API_KEY fehlt — Rate-Limit moeglich")
- `naechster_empfohlen`: meist `03-15-web-content-inventur` (Schema-vor-Lauf), oder bei lokalen Akteuren `03-16-local-gmb-und-seo`
- Bei hoher Relevanz der `tracking_luecke_kunde` oder `consent_unkonform`: Hinweis im Body, dass das MTA-Story-relevant ist (sofort-handhabbare Massnahme)

### Schritt 12: Standard-Schlussformat im Chat

```
✓ 03-14-web-tech-und-tracking abgeschlossen.

Outputs (auf Drive):
- audits/web-tech-tracking.md — Aggregat mit Tech-Matrix, Tracking-Luecken, Performance-Vergleich
- audits/tech-stack.csv — Tech-Inventar pro Akteur (N Zeilen)
- audits/pagespeed.csv — Performance-Werte Mobile+Desktop pro Akteur (2*N Zeilen)
- reports/12-website-tech.html — visueller Audit-Report
Status aktualisiert in: status.md

Ergebnis:
- Akteure erfasst:           N (Kunde + (N-1) Wettbewerber)
- Tech-Stack erkannt:        M (BuiltWith: A, Wappalyzer-Fallback: B)
- PageSpeed gelaufen:        P von N (Mobile+Desktop)
- Kunden-Performance Mobile: X / 100 (LCP Y,Ys, INP Zms, CLS C)
- Kunden-Performance Desktop: X / 100 (LCP Y,Ys, INP Zms, CLS C)
- Tracking-Luecken Kunde:    GA4 [✓/✗], GTM [✓/✗], Consent [✓/✗], Conv.-Pixel [✓/✗]

[Wenn Auffaelligkeiten:]
⚠ Top-Auffaelligkeiten:
- (1-3 Punkte aus der Auffaelligkeiten-Liste, sortiert nach Relevanz)

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md fehlt oder nicht bestaetigt — Tech-Vergleich nur fuer Kunde.

[Wenn Reduced-Modus:]
ℹ Eingeschraenkter Lauf
- Tech-Audit gelaufen [ja/nein], Performance-Audit gelaufen [ja/nein] — andere Achse fehlt mangels Tooling.

Naechste Schritte:
1. 03-15-web-content-inventur — Sitemap- und Content-Analyse fuer Themen-Luecken
2. (parallel moeglich) 03-16-local-gmb-und-seo — bei lokalen Akteuren
3. (parallel moeglich) 03-06-sea-meta-ads-library-check oder 03-07-sea-linkedin-ads-library-check

Sag mir, welcher als naechster.
```

## Bundled Resources

- `reference/tools-api-nutzung.md` — BuiltWith-API und MCP, Wappalyzer-Apify-Fallback, PageSpeed-Insights-API (kostenfrei, Key optional), URL-Normalisierung, Tracking-Signaturen, Rate-Limits und Retry-Logik
- `reference/tech-output-schema.md` — Output-Schemas fuer `audits/web-tech-tracking.md` (Markdown + Frontmatter), `audits/tech-stack.csv` (Spalten) und `audits/pagespeed.csv` (Spalten)

## Edge Cases

- **Alle drei Tooling-Achsen fehlen** → Abbruch mit klarem Hinweis und Anleitung, wie BuiltWith / Apify / PageSpeed-API einzurichten sind. Kein Hard-Coded-Fallback auf Web-Search — verfaelscht die Datenbasis.

- **Domain hinter Cloudflare Bot-Protection** → BuiltWith und Wappalyzer kommen ggf. nicht ran. Im Output `tech_audit_lief: partiell` und Domain markieren. PageSpeed nutzt Google-eigene Crawler und kommt in der Regel durch.

- **Domain hat Redirect-Chain** → URL-Normalisierung folgt einer Stufe Redirect (HEAD-Request), nutzt Ziel-URL fuer alle drei Achsen. In `raw/`-JSONs beide URLs dokumentieren.

- **Domain ist eine Single-Page-Application ohne SSR** → BuiltWith / Wappalyzer erkennen das Frontend-Framework moeglicherweise nicht aus dem initialen HTML. Fallback: `apify/puppeteer-scraper` mit JS-Render fuer 1-2 strategische Akteure (Stratege-Override).

- **PageSpeed-API-Quota erreicht** → Wenn ohne Key: 25.000 Queries/Tag (sollte fuer MTA reichen). Wenn Key gesetzt: 25.000/Tag pro Key. Bei 429: 60s warten, einmal retry. Bei weiterem 429: Skill schreibt bisher erhobene PageSpeed-Daten, markiert restliche Akteure als `performance_audit_offen: true`, setzt sich beim naechsten Aufruf an der unfertigen Position fort.

- **Sehr langsam ladende Domain** (PageSpeed-Timeout) → Im Output `pagespeed_status: timeout` markieren. Das ist selbst eine starke Auffaelligkeit (`kunde_core_web_vitals_schwach`).

- **PageSpeed-Insights gibt CrUX-Daten nicht zurueck** (Domain unterhalb der Schwellwerte fuer CrUX-Aufnahme) → Im Output `crux_daten: false` markieren. Lab-Daten allein sind weniger aussagekraeftig, aber besser als nichts.

- **Tracking-IDs koennen nicht zuverlaessig extrahiert werden** (z. B. Tag-Manager-Container laedt asynchron, IDs sind erst nach Script-Execution sichtbar) → IDs leer lassen, `tracking_ids_extrahiert: partiell` setzen, Stratege manuell pruefen lassen.

- **Kunde nutzt iFrame-Tracking** (Untypisch, kommt bei alten Shopsystemen vor) → Wird vom Standard-Crawler nicht erkannt, Auffaelligkeit `tracking_setup_atypisch`, Stratege manuell pruefen.

- **`audits/tech-stack.csv` oder `audits/pagespeed.csv` existieren bereits auf Drive** (Re-Run) → frage:
  - **(a) ueberschreiben** — `drive.py upsert-text` ersetzt sauber (gws files update)
  - **(b) Backup-und-neu** — alte Versionen nach `assets/_backup/<datei>-<ISO>.csv` kopieren bevor upsert
  - **(c) abbrechen**

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im jeweiligen Sub-Folder aus `meta.json.drive.subfolders`
- Markdown + YAML-Frontmatter fuer `web-tech-tracking.md`, CSV fuer beide CSV-Files (Architektur-Entscheidung 1)
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (via `drive.py upsert-text`)
- HTML-Report basiert auf `reports/_shell.html` (aus Drive geladen)
- **Roh-API-Antworten unter Drive `assets/raw/`** — lokal in `~/.cache/reachx-mta/<slug>/` zwischenspeichern, am Ende des Laufs hochladen
- **Performance-Werte unveraendert lassen** — Lighthouse-Skala bleibt erhalten, Normalisierung ist Aufgabe der Synthese-Skills
- **CrUX vs. Lab transparent dokumentieren** — beides ausweisen, nicht zusammenmischen
