# Aufwands-Bandbreiten pro Massnahmen-Typ (zentral, agentur-weit)

**Versionierung:** Aufwands-Bandbreiten in **Stunden pro Massnahme** bzw. **Stunden pro Monat**, jeweils Bandbreite min-max. Reflektiert Kunden-Komplexitaet (kleine Site / grosse Site, geringe / hohe Wettbewerbs-Intensitaet, Content-Reife). Wird zusammen mit `reachx-stundensaetze.md` versioniert.

```yaml
schema_version: "1.0"
version: "2026.05"
stand: 2026-05-14
```

---

## 1. Setup-Massnahmen (einmalig, Monat 1-3)

Setup-Massnahmen werden zu Vertragsbeginn einmalig durchgefuehrt. Bandbreite plus Rolle aus `reachx-stundensaetze.md`.

### Strategie-Setup

| Massnahmen-Typ | Stunden (min-max) | Rolle | Hinweis |
|---|---|---|---|
| Kick-off-Workshop (halber Tag) | 4-6 | STRATEGIE_LEAD | Plus 2-4h Vorbereitung |
| Strategie-Roadmap erstellen | 8-16 | STRATEGIE_MANAGER | Kanal-Roadmap fuer 12 Monate |
| Personas-Workshop (optional) | 4-8 | STRATEGIE_MANAGER | Nur bei fehlenden Personas im Briefing |
| 90-Tage-Plan-Uebergabe-Workshop | 2-4 | STRATEGIE_LEAD | Initialer Plan-Walkthrough mit Kunde |

### Tracking- und Technik-Setup

| Massnahmen-Typ | Stunden (min-max) | Rolle | Hinweis |
|---|---|---|---|
| GA4 plus GTM Setup | 8-16 | DEVELOPER | Inkl. Conversion-Goals, Cross-Domain falls noetig |
| Server-side Tracking-Setup | 12-24 | DEVELOPER | Wenn Cookie-less / DSGVO-Pflicht |
| GMB-Profil-Pflege initial | 3-6 | JUNIOR_HANDS | Nur bei lokalen Kunden, einmalige Aufraeumung |
| Schema-Markup-Implementierung | 4-10 | DEVELOPER | Pro Hauptseitentyp |

### Kanal-Setup

| Massnahmen-Typ | Stunden (min-max) | Rolle | Hinweis |
|---|---|---|---|
| SEA-Account-Struktur aufbauen | 8-16 | SEA_MANAGER | Konversionen, Kampagnen-Hierarchie, Audiences |
| Meta-Ads-Pixel plus Catalog-Setup | 6-12 | SEA_MANAGER | E-Commerce nur, sonst nur Pixel |
| LinkedIn-Ads-Insight-Tag plus Audiences | 4-8 | SEA_MANAGER | B2B-Kunden |
| Reporting-Dashboard bauen | 6-14 | STRATEGIE_MANAGER | Looker Studio oder Google Sheets, Kunde-spezifisch |
| Content-Style-Guide ableiten | 4-10 | CONTENT_MANAGER | Tonalitaet aus Marken-Profil uebernehmen |
| Landingpage-Konzept | 8-16 | STRATEGIE_MANAGER | Pro Top-Kanal eine optimierte LP |
| Newsletter-Template-Design | 4-8 | DESIGNER | Wenn Newsletter im Plan |

---

## 2. Laufende Massnahmen pro Monat (Monate 1-12, ggf. mit Service-Level-Skalierung)

Laufender Aufwand pro Monat. Service-Level-Skalierung (basis 0.3x / wachstum 0.7x / vollservice 1.0x) wird im Skill auf die operativen Posten angewendet — Strategie-, Reporting- und Workshop-Stunden bleiben unveraendert.

### Kanal: SEO

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| Content-Briefing erstellen | 2-4 (pro Artikel) | SEO_MANAGER | Pro Briefing |
| Content-Redaktion | 4-8 (pro Artikel) | CONTENT_MANAGER | Pro Artikel ca. 1500 Woerter |
| On-Page-Optimierung bestehende URLs | 4-10 | SEO_MANAGER | Laufende Pflege |
| Technische SEO-Pflege | 4-10 | DEVELOPER | Indexierung, Schema, Core-Web-Vitals |
| Monatlicher SEO-Report plus Strategie-Call | 3-5 | STRATEGIE_MANAGER | Pro Monat |
| Local-SEO (GMB-Pflege) | 2-6 | JUNIOR_HANDS | Posts, Q&A, Review-Antworten |

### Kanal: SEA / Google Ads

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| SEA-Kampagnen-Management | 8-18 | SEA_MANAGER | Bid-Management, Keyword-Pflege, Negative-KWs |
| SEA-Anzeigentexte plus RSA-Tests | 3-8 | CONTENT_MANAGER | Pro Monat 3-5 neue RSA-Varianten |
| SEA-Reporting plus Performance-Call | 3-5 | STRATEGIE_MANAGER | Pro Monat |
| Landingpage-Optimierung fuer SEA | 4-10 | DESIGNER + SEA_MANAGER | Conversion-Optimierung |

### Kanal: Meta Ads

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| Meta-Ads-Kampagnen-Management | 6-14 | SEA_MANAGER | Kampagnen, Audiences, Iteration |
| Meta-Ads-Creatives (statisch) | 4-10 | DESIGNER | Pro Monat 4-8 Creatives |
| Meta-Ads-Creatives (Video) | 6-16 | DESIGNER | Reels-Format, separat skaliert |
| Meta-Ads-Reporting | 2-4 | STRATEGIE_MANAGER | Pro Monat |

### Kanal: LinkedIn Ads

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| LinkedIn-Ads-Kampagnen-Management | 5-12 | SEA_MANAGER | B2B, hoeherer Spend-pro-Klick |
| LinkedIn-Ads-Creatives plus Sponsored Content | 3-8 | DESIGNER + CONTENT_MANAGER | Pro Monat 2-4 Stueck |
| LinkedIn-Ads-Reporting | 2-4 | STRATEGIE_MANAGER | Pro Monat |

### Kanal: Content / Blog

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| Redaktion (zusaetzlich zu SEO-Briefings) | 6-16 | CONTENT_MANAGER | Pro Monat 2-4 Artikel |
| Newsletter-Redaktion | 4-8 | CONTENT_MANAGER | Pro Monat 1-2 Newsletter |
| Content-Repurposing fuer Social | 2-6 | CONTENT_MANAGER | Aus Blog-Artikeln Social-Posts ableiten |

### Kanal: Social-organisch

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| Social-Redaktionsplan plus Posts | 6-14 | SOCIAL_MEDIA_MANAGER | Pro Plattform |
| Community-Management | 3-8 | SOCIAL_MEDIA_MANAGER | Comments, DMs, Reactions |
| Reels/Shorts-Konzepte | 4-10 | SOCIAL_MEDIA_MANAGER + DESIGNER | Pro Monat 4-8 Stueck |

### Cross-Kanal-Pflege

| Massnahmen-Typ | Stunden/Monat (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| Tracking-Monitoring plus Daten-QS | 2-5 | DEVELOPER | Datenpflege, Fehler-Behebung |
| Cross-Channel-Reporting | 3-6 | STRATEGIE_MANAGER | Aggregat-Dashboard |
| Monatlicher Strategie-Call (uebergreifend) | 1-2 | STRATEGIE_LEAD | Pro Monat |

---

## 3. Reporting- und Workshop-Frequenz

Reporting und Workshops haben eigene Aufwands-Logik basierend auf der Frequenz aus `synthese/retainer-konfiguration.md`.

### Reporting

| Frequenz | Stunden/Report (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| `monatlich` | 4-8 | STRATEGIE_MANAGER | 12 Reports/Jahr |
| `quartal` | 8-14 | STRATEGIE_MANAGER | 4 Reports/Jahr, tiefer aufgesetzt |
| `woechentlich_stand_up` | 0.5-1.0 | STRATEGIE_MANAGER | 50 Stand-ups/Jahr (z. B. 15 Minuten-Call) |

### Strategie-Workshops

| Frequenz | Stunden/Workshop (min-max) | Rolle | Anwendbar |
|---|---|---|---|
| `quartal` | 8-14 | STRATEGIE_LEAD | 4 Workshops/Jahr (halber bis ganzer Tag) |
| `halbjaehrlich` | 12-20 | STRATEGIE_LEAD | 2 Workshops/Jahr (ganzer Tag plus Vor-/Nachbereitung) |

---

## 4. Service-Level-Skalierung

Pro Service-Level wird auf **operative** Massnahmen ein Skalierungs-Faktor angewendet. Strategie-, Reporting- und Workshop-Stunden bleiben unveraendert.

| Service-Level | Faktor auf operative Stunden | Faktor auf Strategie-/Reporting-Stunden |
|---|---|---|
| `basis` | 0.3 | 1.0 |
| `wachstum` | 0.7 | 1.0 |
| `vollservice` | 1.0 | 1.0 |

Operative Massnahmen = alle Content-Produktion, Creative-Produktion, Kampagnen-Management, Community-Management. Strategie/Reporting = Strategie-Calls, Reports, Workshops, Roadmap-Pflege.

---

## 5. Branchen-typische Retainer-Vergleichs-Ranges (fuer Auffaelligkeit `retainer_uebersteigt_branchen_default`)

Erfahrungswerte aus REACHX-Bestand 2024-2026. Bandbreite in **EUR netto pro Monat** fuer den vollstaendigen Retainer (ohne Setup).

| Branchen-Typ | basis | wachstum | vollservice |
|---|---|---|---|
| `b2b_saas` | 3500-6500 | 6500-12500 | 12500-22000 |
| `b2c_ecommerce` | 3000-6000 | 6000-12000 | 12000-25000 |
| `lokal_dienstleister` | 1800-3500 | 3500-7000 | 7000-12000 |
| `b2b_industrie` | 4500-8500 | 8500-15000 | 15000-28000 |
| `b2b_mittelstand_dienstleister` | 3000-6000 | 6000-11000 | 11000-20000 |
| `content_publisher` | 2500-5000 | 5000-9500 | 9500-16000 |
| `marktplatz_plattform` | 5000-9000 | 9000-16000 | 16000-30000 |
| `sonstige` | 3000-6000 | 6000-11000 | 11000-20000 |

**Anwendung:** Wenn die berechnete Monats-Preis-Range > 1.5x die obere Branchen-Grenze, wird Auffaelligkeit `retainer_uebersteigt_branchen_default` markiert. Stratege prueft im Output, ob ein Custom-Premium-Service-Level kommuniziert werden sollte oder ob die Bandbreite zu eng gerechnet ist.

---

## 6. Aenderungs-Log

| Datum | Version | Aenderung |
|---|---|---|
| 2026-05-14 | 2026.05 | Initiale Erstellung zentrales Aufwands-Bandbreiten-Dokument mit Setup-, Lauf-, Reporting-, Workshop-Bloecken plus Branchen-Vergleichs-Ranges |
