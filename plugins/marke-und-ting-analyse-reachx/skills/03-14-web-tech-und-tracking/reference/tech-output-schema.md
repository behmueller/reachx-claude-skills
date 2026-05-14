# Tech-Output-Schema

Definiert die Output-Formate des Skills fuer die drei Pflicht-Dateien:

- `audits/web-tech-tracking.md` — Aggregat-Markdown mit YAML-Frontmatter (fuer die MTA-Story)
- `audits/tech-stack.csv` — Tech-Inventar pro Akteur (eine Zeile pro Akteur, breit)
- `audits/pagespeed.csv` — Performance-Werte (zwei Zeilen pro Akteur, Mobile + Desktop)

Alle drei sind verbindlich fuer Folge-Skills — Schema-Aenderungen brauchen Versions-Bump (siehe `contracts.md`).

## Tech-Kategorien

Feste Skill-Kategorien (BuiltWith und Wappalyzer werden hierauf normalisiert):

| Skill-Kategorie | Beispiele |
|---|---|
| `cms` | WordPress, TYPO3, Drupal, Joomla, Webflow, Contentful, Shopware (auch CMS-faehig), Adobe Experience Manager, Sitecore, Storyblok, Strapi, Ghost, Squarespace, Wix |
| `frontend_framework` | React, Vue, Angular, Next.js, Nuxt.js, Astro, Svelte, SvelteKit, Remix, Gatsby, Ember |
| `ecommerce_plattform` | Shopify, Shopware, WooCommerce, Magento, BigCommerce, OXID eShop, JTL-Shop, plentymarkets, Wix Stores, Squarespace Commerce |
| `server_hosting` | Vercel, Netlify, AWS (CloudFront, EC2, S3-Hosting), Cloudflare Pages, Heroku, Hetzner, 1&1 IONOS, Strato, all-inkl, GitHub Pages, Render, Fly.io |
| `cdn` | Cloudflare, Fastly, Akamai, Amazon CloudFront, KeyCDN, BunnyCDN, jsDelivr (fuer Assets) |
| `marketing_automation` | HubSpot, Mailchimp, Salesforce/Pardot, ActiveCampaign, Klaviyo, Brevo/SendinBlue, CleverReach, GetResponse, Marketo |
| `analytics_tools` | Google Analytics 4, Universal Analytics, Adobe Analytics, Matomo, Plausible, Fathom, Piwik PRO, Mixpanel, Amplitude (in Tracking-Achse vertieft) |
| `programming_language` | PHP, Python, Ruby, Node.js, .NET, Java, Go (soweit aus dem Tech-Profil erkennbar) |

Bei Mehrfach-Erkennung pro Kategorie (z. B. WP + Shopify-Sub-Shop) Liste in Primaer-zuerst-Reihenfolge — Primaer ist der, der die meiste Site abdeckt. Im CSV nur den Primaer-Eintrag, im Markdown-Body die volle Liste.

## Markdown-Schema (`audits/web-tech-tracking.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-14-web-tech-und-tracking
generiert_am: 2026-05-13T10:30:00Z
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only-Modus
  liste_bestaetigt_am: 2026-05-12T14:00:00Z
quelle:
  tech_tool: builtwith            # builtwith | wappalyzer | gemischt
  tech_audit_lief: true           # false im Reduced-Modus
  tech_zugang: mcp                # mcp | http_api | apify-actor
  performance_tool: pagespeed-insights-v5
  performance_audit_lief: true    # false im Reduced-Modus
  performance_key_gesetzt: true   # ob PAGESPEED_API_KEY genutzt wurde
  datenstand: 2026-05-13T10:30:00Z

# === Akteurs-Liste mit Kerndaten ===
akteure:
  - akteurs_slug: kunde-beispiel
    name: Beispiel GmbH
    typ: kunde
    kategorie_wenn_wettbewerber: null
    domain: beispiel.de
    audit_url_effektiv: https://www.beispiel.de
    # Tech-Stack-Kerndaten
    tech_audit_quelle: builtwith     # builtwith | wappalyzer | partiell | leer
    cms: WordPress
    cms_version: "6.4"
    frontend_framework: null
    ecommerce_plattform: null
    server_hosting: Hetzner
    cdn: Cloudflare
    marketing_automation: Mailchimp
    programming_language: PHP
    # Tracking-Setup
    ga4_vorhanden: true
    ga4_id: "G-XXXXXXXXXX"
    universal_analytics_vorhanden: false
    gtm_vorhanden: true
    gtm_id: "GTM-XXXXXXX"
    consent_tool: Borlabs
    consent_tool_strikt: true
    meta_pixel_vorhanden: false
    meta_pixel_id: null
    linkedin_insight_vorhanden: false
    linkedin_partner_id: null
    google_ads_conversion_vorhanden: false
    tiktok_pixel_vorhanden: false
    heatmap_tool: null
    ab_testing_tool: null
    tracking_ids_extrahiert: vollstaendig   # vollstaendig | partiell | nicht
    # Performance
    performance_audit_lief: true
    performance_mobile:
      score: 62
      lcp_lab_ms: 3400
      fcp_lab_ms: 1800
      tbt_lab_ms: 350
      cls_lab: 0.08
      speed_index_lab_ms: 4200
      crux_daten: true
      lcp_crux_p75_ms: 2800
      inp_crux_p75_ms: 280
      cls_crux_p75: 0.05
      top_empfehlungen:
        - id: unused-javascript
          title: "Nicht verwendetes JavaScript reduzieren"
          savings_ms: 1200
    performance_desktop:
      score: 85
      # ... analog
    raw_pfade:
      builtwith: audits/raw/builtwith-kunde-beispiel.json
      wappalyzer: null
      pagespeed_mobile: audits/raw/pagespeed-kunde-beispiel-mobile.json
      pagespeed_desktop: audits/raw/pagespeed-kunde-beispiel-desktop.json

# === Aggregat-Statistiken ===
statistiken:
  akteure_total: 8
  akteure_tech_erfasst: 8
  akteure_performance_erfasst: 8
  cms_verteilung:
    WordPress: 4
    Webflow: 2
    Shopify: 1
    TYPO3: 1
  ga4_coverage: 7              # von akteure_total
  gtm_coverage: 6
  consent_coverage: 5
  meta_pixel_coverage: 3
  performance_mobile_score_kunde: 62
  performance_mobile_score_median: 71
  performance_mobile_score_top: 92
  performance_desktop_score_kunde: 85
  performance_desktop_score_median: 88
  cwv_bestanden_mobile: 4       # Akteure mit allen drei CrUX-Metriken im "Good"-Bereich
  cwv_bestanden_desktop: 6

# === Auffaelligkeiten ===
auffaelligkeiten:
  - typ: tracking_luecke_kunde
    titel: "Kunden-Tracking unvollstaendig"
    beschreibung: "Kunde hat GA4, aber kein Meta-Pixel und kein LinkedIn-Insight-Tag — kein Conversion-Tracking auf Paid-Social moeglich."
    relevanz: hoch
    handlungs_empfehlung: "Vor Paid-Social-Start Pixel implementieren (Aufwand ~2h)."
    betroffene_akteure: [kunde-beispiel]
  - typ: consent_unkonform
    titel: "Wettbewerber A laedt Meta-Pixel ohne Consent"
    beschreibung: "WB-A hat Meta-Pixel aber kein Consent-Tool — DSGVO-Risiko fuer den Wettbewerber, nicht fuer Kunde."
    relevanz: niedrig
    handlungs_empfehlung: "Nicht im MTA, intern Notiz fuer eventuelle Kontakt-Aufnahme."
    betroffene_akteure: [wb-a-slug]
  - typ: kunde_core_web_vitals_schwach
    titel: "Kunden-LCP Mobile bei 3.4 s (Schwellwert 2.5 s)"
    beschreibung: "Mobile-LCP des Kunden ist deutlich ueber dem Google-Schwellwert — Auswirkung auf SEO-Ranking und Conversion."
    relevanz: hoch
    handlungs_empfehlung: "PageSpeed-Empfehlungen umsetzen: unused-javascript reduzieren (Einsparung ~1.2 s)."
    betroffene_akteure: [kunde-beispiel]
---

# Website-Tech, Tracking und Performance: <Kundenname>

## Uebersicht

3-5 Saetze: Datenbasis (Akteurs-Anzahl, Tools, Datenstand), Tech-Stack-Vielfalt in der Akteurs-Gruppe, Kunden-Position bei Tracking-Coverage und Performance, Top-1-2-Auffaelligkeiten.

## Tech-Stack-Matrix

Tabelle pro Akteur × Tech-Kategorie:

| Akteur | Typ | CMS | Frontend | E-Commerce | Hosting | CDN | Marketing-Automation |
|---|---|---|---|---|---|---|---|
| Beispiel GmbH | Kunde | WordPress | – | – | Hetzner | Cloudflare | Mailchimp |
| WB-A | WB regional | WordPress | – | WooCommerce | Hetzner | – | HubSpot |
| WB-B | WB best practice | – | Next.js | – | Vercel | Vercel-Edge | HubSpot |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Tracking-Setup-Matrix

Tabelle pro Akteur × Tracking-Familie. Symbole `✓` (vorhanden), `–` (fehlt), `⚠` (vorhanden aber unkonform/legacy):

| Akteur | GA4 | GTM | Consent | Meta-Pixel | LinkedIn-IT | Google-Ads-Conv | Heatmap | A/B-Tool |
|---|---|---|---|---|---|---|---|---|
| Beispiel GmbH | ✓ | ✓ | ✓ Borlabs | – | – | – | – | – |
| WB-A | ✓ | ✓ | ✓ Usercentrics | ✓ | ✓ | ✓ | Hotjar | – |
| WB-B | ✓ | ✓ | ✓ Cookiebot | ✓ | ✓ | ✓ | Clarity | VWO |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Performance-Vergleich Mobile

| Akteur | Score | LCP (Lab) | LCP (CrUX p75) | INP (CrUX p75) | CLS (CrUX p75) | Bestand CWV |
|---|---|---|---|---|---|---|
| Beispiel GmbH | 62 | 3.4s | 2.8s | 280ms | 0.05 | – LCP |
| WB-B | 92 | 1.8s | 1.6s | 110ms | 0.02 | ✓ |
| ... | ... | ... | ... | ... | ... | ... |

## Performance-Vergleich Desktop

(analog)

## Pro Akteur Detail

### Beispiel GmbH (Kunde)

- **Tech-Stack**: WordPress 6.4, gehostet auf Hetzner mit Cloudflare-CDN. Mailchimp fuer Newsletter.
- **Tracking**: GA4 + GTM + Borlabs-Consent. Keine Conversion-Pixel — Lead-Tracking nur ueber GA4-Events moeglich.
- **Performance Mobile**: 62/100. LCP schwach bei 3.4 s Lab / 2.8 s CrUX-p75.
  - Top-Empfehlungen: 1) Nicht verwendetes JavaScript reduzieren (~1.2s), 2) Render-blockierende Ressourcen (~0.7s), 3) Bilder im Next-Gen-Format (~0.5s)
- **Performance Desktop**: 85/100. LCP ok bei 1.8 s Lab.

(je Akteur eine Mini-Sektion mit denselben Achsen)

## Auffaelligkeiten

Sortiert nach Relevanz, mit Handlungs-Empfehlung:

### 1. Kunden-Tracking unvollstaendig (hoch)

Kunde hat GA4, aber kein Meta-Pixel und kein LinkedIn-Insight-Tag — kein Conversion-Tracking auf Paid-Social moeglich.

**Empfehlung**: Vor Paid-Social-Start Pixel implementieren (Aufwand ~2h).

### 2. Kunden-LCP Mobile bei 3.4 s (hoch)

Mobile-LCP des Kunden ist deutlich ueber dem Google-Schwellwert (2.5 s) — Auswirkung auf SEO-Ranking und Conversion.

**Empfehlung**: PageSpeed-Empfehlungen umsetzen: unused-javascript reduzieren (Einsparung ~1.2 s).

...
```

## `tech-stack.csv`-Schema

Eine Zeile pro Akteur. Spalten in dieser Reihenfolge:

```
akteurs_slug,akteurs_typ,akteurs_name,domain,audit_url_effektiv,tech_audit_quelle,
cms,cms_version,frontend_framework,ecommerce_plattform,server_hosting,cdn,
marketing_automation,programming_language,
ga4_vorhanden,ga4_id,universal_analytics_vorhanden,gtm_vorhanden,gtm_id,
consent_tool,consent_tool_strikt,
meta_pixel_vorhanden,meta_pixel_id,linkedin_insight_vorhanden,linkedin_partner_id,
google_ads_conversion_vorhanden,tiktok_pixel_vorhanden,
heatmap_tool,ab_testing_tool,
tracking_ids_extrahiert,datenstand_iso
```

Beispiel-Zeile:

```
kunde-beispiel,kunde,Beispiel GmbH,beispiel.de,https://www.beispiel.de,builtwith,WordPress,6.4,,,,Hetzner,Cloudflare,Mailchimp,PHP,true,G-XXXXXXXXXX,false,true,GTM-XXXXXXX,Borlabs,true,false,,false,,false,false,,,vollstaendig,2026-05-13T10:30:00Z
```

Boolean-Felder als `true`/`false` (klein geschrieben). Leere String-Felder als leer (kein `null`-Literal). Kommas in Tool-Namen mit Quoting (`"AB Tasty, EU"`).

## `pagespeed.csv`-Schema

Zwei Zeilen pro Akteur. Spalten:

```
akteurs_slug,akteurs_typ,akteurs_name,domain,strategy,
performance_score,lcp_lab_ms,fcp_lab_ms,tbt_lab_ms,cls_lab,speed_index_lab_ms,
crux_daten,lcp_crux_p75_ms,inp_crux_p75_ms,cls_crux_p75,
top_empfehlung_1,top_empfehlung_2,top_empfehlung_3,top_empfehlung_1_savings_ms,
pagespeed_status,datenstand_iso
```

Beispiel-Zeile (Mobile):

```
kunde-beispiel,kunde,Beispiel GmbH,beispiel.de,mobile,62,3400,1800,350,0.08,4200,true,2800,280,0.05,Nicht verwendetes JavaScript reduzieren,Render-blockierende Ressourcen eliminieren,Bilder im Next-Gen-Format,1200,ok,2026-05-13T10:30:00Z
```

`pagespeed_status` kann `ok`, `timeout`, `error`, `crux_fehlt` sein. Bei `timeout`/`error` koennen Score und Lab-Werte leer sein, der Akteur wird im Output trotzdem gefuehrt.

## Validierungs-Regeln

Beim Schreiben pruefen:

1. **Markdown-Frontmatter** ist gueltiges YAML (z. B. via `yaml.safe_load` testen)
2. **CSVs** haben Header und N+1 Zeilen (Header + Daten)
3. **Performance-Score** ist 0-100 oder leer
4. **CWV-Werte** sind positiv oder leer
5. **Akteurs-Slugs** sind in tech-stack.csv und pagespeed.csv konsistent
6. **`raw_pfade`** zeigen auf existierende Dateien (oder sind `null`, falls die Achse nicht lief)

Bei Validierungs-Fehler im Skill: nicht ueberschreiben, sondern alte Files belassen + klaren Hinweis im Schluss-Format.

## Reduced-Modus-Markierungen

Wenn nur eine Achse lief:

- **Nur Tech**: `pagespeed.csv` wird nicht erzeugt. Frontmatter `performance_audit_lief: false`. Im Body wird die "Performance"-Sektion uebersprungen mit Hinweis.
- **Nur Performance**: `tech-stack.csv` wird nicht erzeugt (oder mit leeren Stack-Spalten, nur Akteurs-Daten). Frontmatter `tech_audit_lief: false`. Im Body wird die "Tech-Stack-Matrix" und "Tracking-Setup-Matrix" uebersprungen mit Hinweis.

In beiden Faellen wird die jeweils andere Achse weiterhin vollstaendig ausgegeben — die nicht-verfuegbare Achse soll der Stratege im naechsten Lauf nachholen, ohne den fertigen Teil verlieren zu muessen.
