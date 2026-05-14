# Tools-API-Nutzung

Wie der Skill die drei Tooling-Achsen anspricht — BuiltWith fuer den Tech-Stack-Primaer, Wappalyzer (via Apify) als Fallback, PageSpeed Insights v5 fuer Performance + Core Web Vitals. Plus URL-Normalisierung, Tracking-Signaturen und Fehler-Behandlung.

## Zugangs-Reihenfolge (Skill-Logik)

Vor dem ersten Akteurs-Lookup ein kleiner Healthcheck pro Achse.

### Tech-Stack-Achse

1. **MCP-Tools pruefen** — falls eine BuiltWith-MCP-Integration verbunden ist (Tool-Praefix `mcp__builtwith__*`), diese bevorzugen.
2. **HTTP-API mit Key** — sonst `BUILTWITH_API_KEY` aus dem Environment lesen, gegen `https://api.builtwith.com/` requesten.
3. **Wappalyzer-Apify-Fallback** — wenn BuiltWith fehlt oder eine Domain nicht abdeckt: Apify-MCP nutzen, einen Wappalyzer-Actor aufrufen (z. B. `apify/wappalyzer` oder Community-Actor mit aktueller Maintenance).
4. **Alles drei fehlt** → Tech-Achse markieren als `tech_audit_lief: false`, Skill laeuft mit den anderen Achsen weiter.

### Performance-Achse

1. **PageSpeed Insights v5** — Endpoint `https://www.googleapis.com/pagespeedonline/v5/runPagespeed` ist oeffentlich und ohne Key nutzbar (niedriges Rate-Limit). Wenn `PAGESPEED_API_KEY` im Environment vorhanden ist → mit Key (25.000 Queries/Tag).
2. Bei Netzwerk- oder 429-Fehler: Retry-Logik (siehe Abschnitt "PageSpeed-Quotas") oder ggf. zwei Achsen-Modus mit `performance_audit_lief: false`.

## URL-Normalisierung

Vor allen API-Aufrufen die Akteurs-URL normalisieren — sonst gibt es Duplikate, falsche Hits oder gar keine Antworten:

1. URL parsen, Schema (http/https) erhalten, fehlend → `https://` vorhaengen
2. Trailing-Slash und Path verwerfen (Default Audit auf Root); falls Akteur explizit eine Unterseite als "Haupt-Einstieg" hat (z. B. Microsite), die Unterseite verwenden — Stratege-Override
3. Lowercase Host
4. Subdomain-Erhaltung: wenn der Akteur explizit auf einer Subdomain operiert (`shop.beispiel.de`), Subdomain behalten
5. Punycode bleibt Punycode (BuiltWith, PageSpeed kommen damit klar)

Beispiele:

| Input | Audit-URL |
|---|---|
| `beispiel.de` | `https://beispiel.de` |
| `https://www.beispiel.de/` | `https://www.beispiel.de` |
| `https://shop.beispiel.de/produkte` | `https://shop.beispiel.de` |
| `https://Beispiel.DE/Startseite` | `https://beispiel.de` |
| `xn--mller-kva.de` (Punycode) | `https://xn--mller-kva.de` |

**Redirect-Check**: Vor dem ersten API-Aufruf einen HEAD-Request schicken. Wenn 301/302 auf eine andere Domain redirected wird, die Ziel-URL fuer alle drei Achsen verwenden. In den Roh-JSONs beide URLs dokumentieren (`audit_url_original` + `audit_url_effektiv`).

## BuiltWith-API

BuiltWith ist die Primaer-Quelle fuer den Tech-Stack-Lookup. Liefert eine kategorisierte Technologie-Liste mit hoher Coverage gerade fuer Marketing- und Analytics-Tools.

### Endpoint `domain.json`

```
GET https://api.builtwith.com/v21/api.json
?KEY=BUILTWITH_API_KEY
&LOOKUP=beispiel.de
&liveOnly=yes
```

Wichtige Parameter:

- `KEY` — API-Key aus dem REACHX-BuiltWith-Account
- `LOOKUP` — Domain (ohne Schema, ohne Trailing-Slash). BuiltWith erkennt Schema selbst.
- `liveOnly=yes` — nur aktuell aktive Technologien (sonst werden alle jemals gesehenen ausgegeben)
- `noMetaData=yes` — optional, reduziert Antwort-Groesse

Antwort-Struktur (vereinfacht):

```json
{
  "Results": [{
    "Result": {
      "Paths": [{
        "Technologies": [{
          "Name": "WordPress",
          "Tag": "cms",
          "FirstDetected": 1640995200000,
          "LastDetected": 1715000000000,
          "Categories": ["CMS"]
        }, ...]
      }]
    }
  }]
}
```

Pro Technologie hat BuiltWith einen `Tag` und `Categories`. Der Skill normalisiert das in die festen Kategorien (siehe `tech-output-schema.md` Abschnitt "Tech-Kategorien"):

| BuiltWith-Tag/Kategorie | Skill-Kategorie |
|---|---|
| `cms`, "CMS" | `cms` |
| `framework`, "JavaScript Frameworks", "Web Frameworks" | `frontend_framework` |
| "Ecommerce" | `ecommerce_plattform` |
| "Web Servers", "Hosting" | `server_hosting` |
| "Content Delivery Network" | `cdn` |
| "Marketing Automation", "Email Hosting Providers" | `marketing_automation` |
| "Analytics and Tracking" | `analytics_tools` (in Tracking-Achse vertieft) |
| `paas`, "Programming Languages" | `programming_language` |

### Credits

BuiltWith arbeitet auf Credit-Basis (genaues Modell je nach REACHX-Vertrag). Pro Domain-Lookup ein Credit. Bei 10 Akteuren → 10 Credits. Bei MCP-Modus uebernimmt die MCP das Credit-Tracking.

### Fehler-Behandlung

- **403** — Key ungueltig → Skill-Abbruch, klare Fehlermeldung
- **429** — Rate-Limit → 60 s warten, ein Retry, dann Wappalyzer-Fallback fuer die restlichen Domains
- **Domain nicht gefunden** → BuiltWith liefert `Result.Errors` mit `Code: NXDOMAIN` oder leere `Paths` → Akteur als `tech_audit_lief: partiell` markieren, Wappalyzer-Fallback versuchen

## Wappalyzer-Fallback (via Apify)

Wenn BuiltWith fehlt oder eine Domain leer zurueckkommt, einen Apify-Actor mit Wappalyzer-Funktionalitaet aufrufen.

### Empfohlene Actors

Mehrere Apify-Actors stellen Wappalyzer-Funktionalitaet bereit. Bei einem Lauf den Actor identifizieren, der zum Zeitpunkt der Audit-Erstellung aktuell maintained ist. Beispiele:

- `apify/wappalyzer` — offizieller Apify-Actor (wenn verfuegbar)
- `infigon-labs/wappalyzer-scraper` oder vergleichbare Community-Actors

Suche per Apify-MCP-Tool `mcp__Apify__search-actors` mit Query "wappalyzer", waehle den Actor mit hoechstem `runCount` und niedrigstem `lastRunAt`-Alter.

### Input-Schema (typisch)

```json
{
  "urls": [
    {"url": "https://beispiel.de"},
    {"url": "https://anderer-akteur.com"}
  ]
}
```

### Output-Mapping

Wappalyzer-Output ist kompatibel mit BuiltWith-Output, hat aber weniger Marketing-Stack-Coverage. Pro Technologie:

```json
{
  "name": "WordPress",
  "categories": [{"id": 1, "name": "CMS"}],
  "version": "6.4",
  "confidence": 100
}
```

Wie bei BuiltWith in die festen Skill-Kategorien normalisieren. **Im Output `tech_audit_quelle: wappalyzer`** markieren, damit der Stratege die Tiefe-Differenz versteht (Wappalyzer findet typischerweise CMS und Frontend-Framework zuverlaessig, aber weniger Marketing-Tools).

## Tracking-Signaturen

Tracking-Erkennung kommt primaer aus dem BuiltWith- bzw. Wappalyzer-Result. Beide listen die Tools auf, der Skill mappt sie auf die Boolean-Felder:

| Skill-Feld | BuiltWith/Wappalyzer-Namen (Beispiele) |
|---|---|
| `ga4_vorhanden` | "Google Analytics 4", "Google Analytics", "GTAG" (mit weiterer Pruefung) |
| `universal_analytics_vorhanden` | "Universal Analytics", "ga.js" |
| `gtm_vorhanden` | "Google Tag Manager" |
| `consent_tool` | "Usercentrics", "Cookiebot", "OneTrust", "Borlabs Cookie", "CCM19", "klaro", "Iubenda" |
| `meta_pixel_vorhanden` | "Facebook Pixel", "Meta Pixel" |
| `linkedin_insight_vorhanden` | "LinkedIn Insight Tag" |
| `google_ads_conversion_vorhanden` | "Google Ads Conversion Tracking" (manche Tools tagen das gemeinsam mit GTAG; bei reinem GTAG-Tag eine zweite Pruefung im HTML) |
| `tiktok_pixel_vorhanden` | "TikTok Pixel" |
| `heatmap_tool` | "Hotjar", "Microsoft Clarity", "FullStory", "Mouseflow", "Lucky Orange" |
| `ab_testing_tool` | "Optimizely", "VWO", "AB Tasty", "Convertize" (Google Optimize wurde Sept 2023 eingestellt — wenn erkannt: Auffaelligkeit `legacy_tracking`) |

### Fallback: HTML-Inspektion via Apify

Wenn BuiltWith und Wappalyzer beide fehlen, kann eine leichtgewichtige Signatur-Erkennung via Apify-Crawler erfolgen:

1. `apify/website-content-crawler` oder `apify/puppeteer-scraper` mit Render-Mode (JS-Execution noetig fuer Tag-Manager-Container)
2. Pro Akteur die initiale HTML-Antwort + die ausgefuehrten Scripts erfassen
3. Suche nach Signatur-Patterns:

| Tool | Signatur-Pattern |
|---|---|
| GA4 | `gtag/js?id=G-`, `gtag('config', 'G-`, `googletagmanager.com/gtag` |
| Universal Analytics | `google-analytics.com/analytics.js`, `gtag('config', 'UA-`, `ga('create',` |
| GTM | `googletagmanager.com/gtm.js?id=GTM-`, `<!-- Google Tag Manager -->`-Kommentare |
| Meta Pixel | `connect.facebook.net/en_US/fbevents.js`, `fbq('init',` |
| LinkedIn Insight | `snap.licdn.com/li.lms-analytics/insight.min.js`, `_linkedin_partner_id = ` |
| Google Ads Conversion | `googleadservices.com/pagead/conversion.js`, `gtag('event', 'conversion'` |
| Hotjar | `static.hotjar.com/c/hotjar-`, `(function(h,o,t,j,a,r)` Pattern |
| Microsoft Clarity | `clarity.ms/tag/`, `clarity("set"` |
| Usercentrics | `app.usercentrics.eu/browser-ui/`, `usercentrics-cmp` Element |
| Cookiebot | `consent.cookiebot.com/uc.js`, `<script id="Cookiebot"` |
| OneTrust | `cdn.cookielaw.org/scripttemplates/`, `<script src="https://cdn.cookielaw.org` |

Konfidenz dokumentieren: wenn Signatur-Pattern matched aber Tool-Name nicht in BuiltWith/Wappalyzer-Ergebnis, dann `tracking_ids_extrahiert: partiell` und Stratege-Hinweis.

### Tracking-ID-Extraktion

Wenn die HTML-Inspektion die IDs zugaenglich macht, im Skill mit Regex extrahieren:

| ID-Typ | Regex |
|---|---|
| GA4 Measurement-ID | `G-[A-Z0-9]{10}` |
| Universal Analytics Property | `UA-\d+-\d+` |
| GTM Container | `GTM-[A-Z0-9]{6,}` |
| Meta Pixel | `fbq\(['"]init['"],\s*['"](\d{15,16})['"]\)` |
| LinkedIn Partner | `_linkedin_partner_id\s*=\s*['"](\d+)['"]` |

Bei Unsicherheit IDs leer lassen — falsche IDs sind schlimmer als fehlende.

### Consent-Tool-Strict-Heuristik

Pruefen, ob das Consent-Tool-Script **vor** den Tracking-Skripten geladen wird:

- Ja → `consent_tool_strikt: true` (Tracking-Skripte werden vermutlich erst nach Einwilligung geladen)
- Nein (Tracking-Script schon im Head, Consent erst spaeter) → `consent_tool_strikt: false` + Hinweis

Das ist eine Heuristik — die finale rechtliche Bewertung kann der Skill nicht ersetzen.

## PageSpeed-Insights-API

PageSpeed Insights v5 liefert Lighthouse-Werte (Lab) und CrUX-Werte (Real-User-Daten) in einem Aufruf. Endpoint ist kostenfrei.

### Endpoint

```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
?url=https://beispiel.de
&strategy=mobile
&category=performance
&key=PAGESPEED_API_KEY
```

Wichtige Parameter:

- `url` — vollstaendige URL inkl. Schema
- `strategy` — `mobile` oder `desktop`. Pro Akteur **beides** abfragen.
- `category` — `performance` reicht fuer dieses Audit (andere Lighthouse-Kategorien wie `accessibility` koennten ergaenzt werden, sind aber nicht Teil dieses Audits)
- `key` — `PAGESPEED_API_KEY` aus Environment. Optional, ohne Key niedriger Rate-Limit.

Bei `strategy=mobile`: Lighthouse simuliert ein Mid-Tier-Android-Geraet auf 4G-Netz. Das ist der relevante Default, weil Mobile-Traffic in den meisten Branchen dominiert. Desktop laeuft trotzdem mit, weil B2B-Recherche und mehr formelle Branchen oft Desktop-getrieben sind.

### Antwort-Mapping

```json
{
  "lighthouseResult": {
    "categories": {
      "performance": {"score": 0.62}
    },
    "audits": {
      "largest-contentful-paint": {"numericValue": 3400, "score": 0.45, ...},
      "first-contentful-paint": {"numericValue": 1800, ...},
      "total-blocking-time": {"numericValue": 350, ...},
      "cumulative-layout-shift": {"numericValue": 0.08, ...},
      "speed-index": {"numericValue": 4200, ...},
      "interactive": {"numericValue": 5100, ...},
      "render-blocking-resources": {"score": 0.3, "details": {"overallSavingsMs": 1200, ...}},
      ...
    }
  },
  "loadingExperience": {
    "metrics": {
      "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2800, "category": "AVERAGE"},
      "INTERACTION_TO_NEXT_PAINT": {"percentile": 280, "category": "AVERAGE"},
      "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 0.05, "category": "GOOD"}
    },
    "overall_category": "AVERAGE"
  },
  "originLoadingExperience": {...}
}
```

Pro Akteur extrahieren:

- **Performance-Score** = `lighthouseResult.categories.performance.score * 100`, gerundet auf Integer
- **LCP-Lab** = `lighthouseResult.audits["largest-contentful-paint"].numericValue` (ms)
- **FCP-Lab** = `lighthouseResult.audits["first-contentful-paint"].numericValue`
- **TBT-Lab** = `lighthouseResult.audits["total-blocking-time"].numericValue`
- **CLS-Lab** = `lighthouseResult.audits["cumulative-layout-shift"].numericValue` (dimensionslos)
- **Speed-Index-Lab** = `lighthouseResult.audits["speed-index"].numericValue`
- **CrUX-Verfuegbar** = `"loadingExperience" in response and "metrics" in response.loadingExperience`
- **LCP-CrUX-p75** = `loadingExperience.metrics.LARGEST_CONTENTFUL_PAINT_MS.percentile`
- **INP-CrUX-p75** = `loadingExperience.metrics.INTERACTION_TO_NEXT_PAINT.percentile`
- **CLS-CrUX-p75** = `loadingExperience.metrics.CUMULATIVE_LAYOUT_SHIFT_SCORE.percentile / 100` (PageSpeed liefert × 100)

**Top-3 Empfehlungen** aus den Audits filtern: nur die mit `score < 1.0` und `details.overallSavingsMs > 0` (oder `details.overallSavingsBytes > 0`). Nach `overallSavingsMs` absteigend sortieren, Top-3 nehmen. Pro Empfehlung speichern: `id` (Audit-ID), `title`, `savings_ms`.

Typische Top-Empfehlungen:

- `unused-javascript` — "JavaScript ungenutzt"
- `render-blocking-resources` — "Render-blockierende Ressourcen"
- `unminified-javascript` / `unminified-css`
- `uses-optimized-images` — "Bilder im Next-Gen-Format"
- `server-response-time` — "Erstes Antwort-Zeit"
- `unused-css-rules`
- `legacy-javascript`

### CrUX vs. Lab unterscheiden

CrUX-Daten sind echte Nutzer-Messungen der letzten 28 Tage. Lab-Daten sind Lighthouse-Simulationen. Beides ist relevant:

- **Lab-Daten** zeigen Optimierungspotenzial unter standardisierten Bedingungen — gut fuer Vergleich zwischen Akteuren
- **CrUX-Daten** zeigen reale Nutzer-Erfahrung — die Werte, an denen Google das Ranking-Signal berechnet

Im Output **beide** ausweisen, nicht zusammenmischen. CrUX fehlt oft bei kleinen Sites — dann nur Lab-Daten, mit `crux_daten: false` markiert.

### PageSpeed-Quotas

- **Ohne Key**: 25.000 Queries pro Tag pro IP (lt. Google-Doku Stand 2026, kann variieren)
- **Mit Key**: 25.000 Queries pro Tag pro Key, 100 pro 100 Sekunden

Pro Akteur 2 Calls (Mobile + Desktop). Bei einer MTA mit 10 Akteuren → 20 Calls. Quota sollte locker reichen.

Bei 429:

1. 60 Sekunden warten, einmal retry
2. Wenn weiterhin 429: Skill schreibt bisher erhobene Performance-Daten in CSV, markiert restliche Akteure als `performance_audit_offen: true`, setzt beim naechsten Aufruf fort
3. Bei vollem Quota-Bann: Stratege-Hinweis, Key anpassen oder einen Tag warten

### Timeout-Handling

PageSpeed kann fuer sehr langsame Sites > 60s brauchen. Skill-seitig Timeout auf 90 s setzen. Wenn Timeout: `pagespeed_status: timeout`, Akteur markieren — selbst eine starke Performance-Auffaelligkeit.

## Reduced-Modus

Wenn nur eine der zwei Haupt-Achsen (Tech-Stack vs. Performance) verfuegbar ist, laeuft der Skill trotzdem durch. Folgen fuer die Outputs:

- **Tech-Achse fehlt**: `tech-stack.csv` wird nicht erzeugt (oder mit leeren Tech-Spalten). `web-tech-tracking.md`-Frontmatter `tech_audit_lief: false`. Tracking-Erkennung wird ggf. als Apify-HTML-Inspektion durchgefuehrt (siehe Tracking-Signaturen-Fallback), aber mit `tracking_ids_extrahiert: partiell`.
- **Performance-Achse fehlt**: `pagespeed.csv` wird nicht erzeugt. `web-tech-tracking.md`-Frontmatter `performance_audit_lief: false`. Auffaelligkeit `kunde_core_web_vitals_schwach` kann dann nicht erzeugt werden — Hinweis im Schluss-Format, dass PageSpeed-Daten nachgeholt werden sollten.
- **Beide Achsen fehlen** → Skill-Abbruch mit klarem Tooling-Hinweis.
