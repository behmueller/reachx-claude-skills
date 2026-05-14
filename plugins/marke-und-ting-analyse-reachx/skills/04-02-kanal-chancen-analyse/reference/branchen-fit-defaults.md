# Branchen-Fit-Defaults: Branchen × Kanal-Matrix

Diese Datei definiert Default-Branchen-Fit-Scores für jeden Kanal in jedem der acht Branchen-Typen. Die Defaults greifen, wenn keine konkreten Wettbewerber-Audit-Daten den Branchen-Fit überschreiben.

## Branchen-Typen

Die acht Typen, auf die der Skill mappt:

| Slug | Beschreibung | Beispiele |
|---|---|---|
| `b2b_saas` | Software-as-a-Service, B2B-Tech | HubSpot, Sevdesk, Personio |
| `b2c_ecommerce` | Online-Shops, B2C-Produkte | About You, Westwing, MyHammer-Shop |
| `lokal_dienstleister` | Service mit lokalem Bezug, Walk-In | Zahnarzt, Anwalt, Friseur, Restaurant |
| `b2b_industrie` | Hersteller mit B2B-Vertriebszyklus | Maschinenbau, Großhandel, Industrie-Lieferanten |
| `b2b_mittelstand_dienstleister` | B2B-Service ohne Tech-Schwerpunkt | Agenturen, Beratungen, Steuerberater |
| `content_publisher` | Content/Medien als Geschäftsmodell | News-Sites, Blogs, Newsletter-Verlage |
| `marktplatz_plattform` | 2-Seiten-Marktplatz | ImmoScout, MyHammer, Etsy |
| `sonstige` | nicht klar zuzuordnen | Default mit ausgeglichenen Werten |

## Default-Branchen-Fit-Matrix

Score-Skala: 0 = Kanal nicht relevant, 100 = Pflicht-Kanal in dieser Branche.

| Kanal | b2b_saas | b2c_ecommerce | lokal_dienstleister | b2b_industrie | b2b_mittelstand_dienstleister | content_publisher | marktplatz_plattform | sonstige |
|---|---|---|---|---|---|---|---|---|
| **SEO** | 85 | 75 | 65 | 80 | 70 | 95 | 80 | 70 |
| **SEA / Google-Ads** | 85 | 90 | 70 | 65 | 60 | 30 | 75 | 65 |
| **Meta-Ads** | 25 | 90 | 55 | 25 | 35 | 40 | 60 | 50 |
| **LinkedIn-Ads** | 80 | 10 | 15 | 70 | 65 | 25 | 35 | 30 |
| **Local-SEO / GMB** | 10 | 30 | 95 | 40 | 50 | 10 | 30 | 30 |
| **Content / Blog** | 85 | 60 | 45 | 70 | 65 | 95 | 60 | 55 |
| **Instagram-organisch** | 25 | 80 | 60 | 20 | 40 | 50 | 60 | 50 |
| **TikTok-organisch** | 15 | 70 | 40 | 10 | 25 | 45 | 50 | 35 |
| **LinkedIn-organisch** | 90 | 15 | 25 | 70 | 75 | 30 | 40 | 40 |
| **Pinterest-organisch** | 5 | 65 | 25 | 10 | 15 | 40 | 50 | 25 |
| **YouTube-organisch** | 50 | 55 | 25 | 50 | 35 | 70 | 45 | 40 |
| **Website-CRO** | 80 | 90 | 60 | 70 | 65 | 70 | 85 | 70 |

## Begründungen pro Branche (Auszüge)

### `b2b_saas`

- LinkedIn-organisch (90) und LinkedIn-Ads (80) dominieren, weil die Zielgruppe (Decider, Tech-Leads) dort lebt
- SEA (85) wichtig wegen kompetitiver Begriffe wie "best crm software"
- SEO (85) für High-Intent-Vergleichs- und Lösungs-Suchen
- Meta-Ads (25), TikTok (15), Pinterest (5) — wenig B2B-SaaS-Eignung außer für sehr produkt-greifbare Tools
- Content / Blog (85) als Demand-Generation und Trust-Building

### `b2c_ecommerce`

- SEA (90) und Meta-Ads (90) dominieren — direkte Conversion-Kanäle
- Instagram (80) für Produkt-Visualität
- Pinterest (65) und TikTok (70) für Produkt-Discovery
- LinkedIn-Ads (10) praktisch irrelevant
- Website-CRO (90) entscheidend — Conversion-Rate-Optimization ist Standard-Disziplin

### `lokal_dienstleister`

- Local-SEO / GMB (95) ist der Hauptkanal
- SEA (70) für lokale Such-Anfragen
- Instagram (60) für visuelle Service-Darstellung (z. B. Friseur, Restaurant)
- LinkedIn und Pinterest schwach
- Branchen-Fit-Override im Skill stark anwenden — wenn nicht-lokal-relevant, wird Local-SEO ausgeschlossen

### `b2b_industrie`

- SEO (80) und Content (70) für Suche nach Spezial-Komponenten
- LinkedIn-Ads (70) und LinkedIn-organisch (70) für Decision-Maker
- Print/Trade-Shows historisch wichtig (außerhalb dieses Skills)
- Social-organisch (Instagram/TikTok) schwach
- Website-CRO (70) wegen langer Conversion-Pfade wichtig

### `b2b_mittelstand_dienstleister`

- LinkedIn-organisch (75) und LinkedIn-Ads (65) für persönliche Mandats-Akquise
- SEO (70) und Content (65) für Expertise-Demonstration
- Local-SEO (50) wenn regionaler Bezug
- Meta-Ads (35) schwach — meist nicht das richtige Touchpoint
- SEA (60) mittel — abhängig von Such-Volumen der Service-Begriffe

### `content_publisher`

- SEO (95) und Content (95) sind die Kanäle — der ganze Geschäftsmodell-Kern
- Newsletter (außerhalb dieses Skills) zentral
- YouTube (70) wichtig für Video-Content
- SEA (30) niedrig — paid vs. organic-Ökonomie verschiebt sich
- LinkedIn-Ads (25) niedrig

### `marktplatz_plattform`

- Beide Seiten bewerben: Anbieter UND Nachfrager
- SEO (80) für SEO-getriebenen Long-Tail-Traffic (Stadt+Kategorie-Kombinationen)
- Website-CRO (85) zentral für Conversion-Mechanik
- SEA (75) und Meta-Ads (60) für Customer-Acquisition
- LinkedIn (35) für Anbieter-Akquise wenn B2B-Marktplatz

### `sonstige`

Ausgeglichene Defaults zwischen 25 und 70. Stratege sollte über das Briefing-Fit nachjustieren.

## Override-Regeln

Der Default-Score wird durch konkrete Audit-Daten überschrieben:

### 1. Aktivitäts-Override

Wenn mehr als 50% der bestätigten Wettbewerber im Kanal aktiv sind:

- Branchen-Fit-Score: +15 (gedeckelt auf 95)
- Begründung: "WBs zeigen, dass der Kanal in dieser konkreten Marktnische funktioniert"

Quelle: jeweiliger Audit-Output `akteure[]` mit `aktiv: true` / Anzeigen-Anzahl > 0 / etc.

### 2. Sättigungs-Override

Wenn **alle** WBs aktiv UND Spend-Range hoch (z. B. SEA mit SpyFu-Median > 20k EUR/Monat):

- Branchen-Fit-Score: +10 (gedeckelt auf 95)
- Aber: `kanal_branchen_uebersaturiert`-Auffälligkeit setzen
- `aufwand_score` separat um -15 reduzieren (Markt ist teuer)

### 3. Lücken-Override

Wenn 0 WBs im Kanal aktiv UND Default-Branchen-Fit > 60:

- Branchen-Fit-Score: -20 (Floor 5)
- Begründung: "Möglicherweise hat die Branche den Kanal aus gutem Grund verworfen — Stratege soll prüfen, ob das Chance oder Sackgasse ist"
- Auffälligkeit `kanal_branchen_chance` ODER `kanal_zu_klein` setzen (Stratege entscheidet)

### 4. Zielgruppen-Override (aus Briefing)

Wenn Briefing klare Zielgruppe nennt, die nicht zum Branchen-Default passt (z. B. B2B-SaaS-Kunde mit Education-Zielgruppe → TikTok-Boost):

- Branchen-Fit-Score: +20 für betroffenen Kanal
- Konfidenz auf `mittel` setzen (weil Override-Annahme, nicht Daten)

## Branchen-spezifische Gewichtungs-Overrides für Aggregations-Formel

Im Default ist die Gewichtung 0.30/0.20/0.20/0.10/0.20 (siehe `chancen-score-formel.md`). Branchen-spezifisch:

| Branche | Gewichtungen (Pot/Auf/Brf/Reif/Bran) | Begründung |
|---|---|---|
| `lokal_dienstleister` | 0.25 / 0.20 / 0.15 / 0.15 / 0.25 | Branchen-Fit filtert hier sehr stark; Reife relevanter weil GMB-Setup binär ist |
| `b2b_saas` | 0.30 / 0.15 / 0.25 / 0.10 / 0.20 | Briefing-Fit höher, weil Kanal-Mix sehr unternehmens-spezifisch; Aufwand niedriger, weil Kanal-spezifischer Aufwand sehr variabel |
| `b2c_ecommerce` | 0.35 / 0.20 / 0.20 / 0.05 / 0.20 | Potenzial dominiert; Reife egal (Quick-Setup) |
| `b2b_industrie` | 0.25 / 0.25 / 0.20 / 0.15 / 0.15 | Aufwand wichtiger (lange Sales-Zyklen) |
| `b2b_mittelstand_dienstleister` | 0.25 / 0.20 / 0.25 / 0.15 / 0.15 | Briefing höher; persönliche Akquise-Logik |
| `content_publisher` | 0.35 / 0.20 / 0.15 / 0.10 / 0.20 | Potenzial dominiert (Volumen-Geschäftsmodell) |
| `marktplatz_plattform` | 0.30 / 0.20 / 0.20 / 0.10 / 0.20 | Default |
| `sonstige` | 0.30 / 0.20 / 0.20 / 0.10 / 0.20 | Default |

## Potenzial-Defaults (Fallback wenn keine Audit-Daten)

Wenn für einen Kanal noch kein Audit gelaufen ist, wird ein konservativer Potenzial-Default eingesetzt — abgeleitet vom Branchen-Fit-Score, aber 10 niedriger.

```
potenzial_default = max(10, branchen_fit_default - 10)
```

Konfidenz dann immer `niedrig`. Hinweis im Output: "Potenzial-Score basiert nur auf Branchen-Default — Audit für robusteren Score empfohlen."

## Aktualisierungs-Pflege dieser Datei

Die Branchen-Fit-Defaults sind **lebendige Werte**. Bei jedem MTA-Live-Test, der starke Abweichungen aufdeckt (z. B. lokaler Dienstleister mit TikTok-Erfolg), wird die Matrix angepasst. Schema-Version: 1.0.
