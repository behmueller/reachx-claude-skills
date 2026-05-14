# Massnahmen-Bibliothek

Zentrale Sammlung der Standard-Massnahmen pro Kanal-Typ. Diese Bibliothek wird vom `04-05-90-tage-plan` als Vorlage genutzt — pro Kunden-Plan werden die passenden Massnahmen ausgewaehlt, mit Audit-Daten angereichert und ggf. um kundenspezifische Massnahmen ergaenzt.

**Struktur pro Massnahme**:

- `slug` — eindeutiger Bibliotheks-Slug (kebab-case)
- `titel` — kurz, aktivisch
- `beschreibung` — 1-2 Saetze
- `zielsetzung` — was die Massnahme erreichen soll
- `kanal_slug` — Bezug zum Kanal
- `verantwortlich_default` — `REACHX | Kunde | Hybrid`
- `verantwortlich_details` — bei Hybrid die Rollen-Aufteilung
- `aufwand_range_stunden` — Bandbreite (Min-Max), niemals Punktwert
- `voraussetzungen_typ` — Tech-Voraussetzungen (z. B. "Tracking muss live sein") oder andere Massnahmen-Slugs
- `meilenstein_indikator` — woran man Erfolg messen kann
- `prioritaet_default` — `Quick-Win | Foundation | Long-Term`
- `typische_monat` — `1 | 2 | 3` (Default-Zuordnung, kann ueberschrieben werden)
- `bemerkung` — optionale Hinweise

---

## Cross-Channel Foundation (Tracking, Setup, Reporting)

### tracking-ga4-setup

- **titel**: GA4-Tracking auf Hauptdomain einrichten und verifizieren
- **beschreibung**: GA4-Property konfigurieren, Tag-Manager-Container aufsetzen, Events fuer Conversions definieren, Consent-Mode integrieren.
- **zielsetzung**: Saubere Daten-Basis fuer alle Channel-Auswertungen.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde Umsetzung im CMS)
- **aufwand_range_stunden**: 12-24
- **voraussetzungen_typ**: Zugriff auf Tag-Manager und CMS, Datenschutz-Freigabe
- **meilenstein_indikator**: GA4 zeigt mindestens 7 Tage saubere Daten fuer Top-10-Landingpages, Conversion-Events firen wie erwartet
- **prioritaet_default**: Foundation
- **typische_monat**: 1
- **bemerkung**: Critical-Path-Kandidat — blockiert haeufig andere Channel-Optimierungen

### server-side-tagging

- **titel**: Server-Side-Tracking ueber Tag-Manager-Server aufsetzen
- **beschreibung**: GTM-Server-Container in Cloud-Umgebung (GCP oder Stape) deployen, Client-Server-Routing fuer kritische Events einrichten.
- **zielsetzung**: Bessere Daten-Qualitaet, weniger Ad-Blocker-Verluste, robustere Conversion-Messung.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 16-32
- **voraussetzungen_typ**: `tracking-ga4-setup` muss live sein, Hosting-Budget freigegeben
- **meilenstein_indikator**: 95%+ der GA4-Events kommen ueber den Server-Container
- **prioritaet_default**: Foundation
- **typische_monat**: 2
- **bemerkung**: Nur bei Kunden mit relevantem Trackingsignal-Verlust (z. B. Safari + iOS-dominiertem Traffic)

### consent-audit

- **titel**: Cookie-Consent-Audit und CMP-Konfiguration
- **beschreibung**: Pruefung der aktuellen Consent-Loesung, Anpassung der Kategorien-Trennung (technisch / Marketing / Statistik), Consent-Mode-Integration mit GA4 und Ads.
- **zielsetzung**: DSGVO-Konformitaet plus maximale Datenerfassung im erlaubten Rahmen.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde / Datenschutz-Verantwortlicher Freigabe)
- **aufwand_range_stunden**: 6-12
- **voraussetzungen_typ**: Aktuelle Datenschutzerklaerung verfuegbar
- **meilenstein_indikator**: CMP zeigt korrekte Trennung, Consent-Mode wird an alle Tags weitergegeben
- **prioritaet_default**: Foundation
- **typische_monat**: 1

### reporting-dashboard

- **titel**: KPI-Dashboard aufbauen (Looker Studio oder vergleichbar)
- **beschreibung**: Dashboard mit allen Top-Kanaelen, KPIs (Traffic, Leads, Umsatz), Forecast-Vergleich, Drilldown auf Kampagnen-Ebene.
- **zielsetzung**: Stratege und Kunde sehen jederzeit den Plan-Fortschritt.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 8-16
- **voraussetzungen_typ**: `tracking-ga4-setup`, Ads-Konten verbunden
- **meilenstein_indikator**: Kunde hat Zugang, Dashboard wird in Monatsreview genutzt
- **prioritaet_default**: Foundation
- **typische_monat**: 3

### briefing-luecken-workshop

- **titel**: Briefing-Workshop zur USP- und Zielgruppen-Schaerfung
- **beschreibung**: 90-Minuten-Workshop mit Kunden-Stakeholdern, USP und Zielgruppe konkretisieren, in Briefing-Dokument zurueckschreiben.
- **zielsetzung**: Saubere Briefing-Basis fuer alle Content- und Ads-Briefings.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: Hybrid (REACHX Moderation + Kunde Input)
- **aufwand_range_stunden**: 6-10
- **voraussetzungen_typ**: keine
- **meilenstein_indikator**: Aktualisiertes Briefing-Dokument liegt vor und ist von Kunde freigegeben
- **prioritaet_default**: Foundation
- **typische_monat**: 1
- **bemerkung**: Wird nur eingeplant, wenn `briefing_fit_konfidenz` in `kanal-chancen.md` auf `niedrig` steht

---

## SEO

### sitemap-und-indexierung

- **titel**: XML-Sitemap einreichen und Indexierung verifizieren
- **beschreibung**: Sitemap aktualisieren, in Search Console einreichen, alle Top-Landingpages auf Indexierungs-Status pruefen, blockierende Robots-Eintraege loesen.
- **zielsetzung**: Saubere Crawl- und Index-Basis als Voraussetzung fuer SEO-Wirkung.
- **kanal_slug**: `seo`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 4-8
- **voraussetzungen_typ**: Search-Console-Zugang
- **meilenstein_indikator**: 95%+ der Top-50-URLs sind indexiert, keine kritischen Crawl-Fehler in Search Console
- **prioritaet_default**: Quick-Win
- **typische_monat**: 1

### sweet-spot-cluster-content-hub

- **titel**: Content-Hub fuer Top-Sweet-Spot-Cluster aufbauen
- **beschreibung**: Fuer das Sweet-Spot-Cluster aus `seo-cluster-zusammenfassung.md` einen strukturierten Content-Hub konzipieren (Pillar-Page plus 4-6 Cluster-Artikel mit interner Verlinkung).
- **zielsetzung**: Top-10-Rankings fuer das Sweet-Spot-Cluster innerhalb von 6 Monaten.
- **kanal_slug**: `seo`
- **verantwortlich_default**: Hybrid (REACHX Briefing + Konzept, Kunde Fach-Input)
- **aufwand_range_stunden**: 24-48 (Konzept-Phase plus erste 2 Stuecke)
- **voraussetzungen_typ**: `briefing-luecken-workshop` falls noetig, Sweet-Spot-Cluster identifiziert
- **meilenstein_indikator**: Pillar-Page plus 2 Cluster-Artikel live, erste Impressions in Search Console fuer Cluster-Keywords
- **prioritaet_default**: Quick-Win (wenn Cluster Median-Difficulty unter 30)
- **typische_monat**: 1-2 (Konzept Monat 1, erste Stuecke Monat 2)
- **bemerkung**: Pro Sweet-Spot-Cluster eine eigene Massnahme, ID-Suffix nach Cluster

### schema-markup-einbauen

- **titel**: Schema-Markup auf Top-Templates einbauen
- **beschreibung**: Strukturierte Daten (Organization, Product/Service, Article, FAQ, LocalBusiness je nach Branche) auf den Top-Templates implementieren, in Rich-Results-Test verifizieren.
- **zielsetzung**: SERP-Visibility erhoehen, Rich-Snippets ermoeglichen.
- **kanal_slug**: `seo`
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde / Dev Umsetzung)
- **aufwand_range_stunden**: 8-16
- **voraussetzungen_typ**: Dev-Zugang oder CMS-Editor-Zugang
- **meilenstein_indikator**: Rich-Results-Test gruen fuer Top-20-URLs, erste Rich-Snippets in SERPs sichtbar
- **prioritaet_default**: Quick-Win
- **typische_monat**: 2

### seo-onpage-top10

- **titel**: SEO-Onpage-Optimierung der Top-10-Landingpages
- **beschreibung**: Title-Tags, Meta-Descriptions, H-Struktur, interne Verlinkung, Bild-Alt-Texte fuer die Top-10 umsatzrelevanten Landingpages ueberarbeiten.
- **zielsetzung**: Ranking-Hebel auf bestehenden Top-Seiten heben.
- **kanal_slug**: `seo`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 12-20
- **voraussetzungen_typ**: Search-Console-Daten verfuegbar
- **meilenstein_indikator**: 6-8 der 10 Seiten zeigen verbesserte CTR nach 4 Wochen
- **prioritaet_default**: Quick-Win
- **typische_monat**: 1

### core-web-vitals-fix

- **titel**: Core-Web-Vitals der Top-Templates verbessern
- **beschreibung**: LCP, INP und CLS auf den Top-Templates analysieren, kritische Bremsen entfernen (Bild-Komprimierung, kritisches CSS, Third-Party-Scripts).
- **zielsetzung**: Ranking-Signal CWV gruen, bessere UX.
- **kanal_slug**: `seo`
- **verantwortlich_default**: Hybrid (REACHX Audit + Kunde / Dev Umsetzung)
- **aufwand_range_stunden**: 12-32
- **voraussetzungen_typ**: PageSpeed-Insights-Daten aus `web-tech-tracking.md`
- **meilenstein_indikator**: CrUX-Daten der Top-Templates zeigen "gut" fuer alle drei Metriken
- **prioritaet_default**: Foundation
- **typische_monat**: 2

---

## SEA / Google-Ads

### sea-konto-setup

- **titel**: Google-Ads-Konto strukturiert aufsetzen
- **beschreibung**: Konto-Struktur, Conversion-Tracking, Audience-Listen, Negative-Keyword-Liste, Brand-Kampagne als Basis aufsetzen.
- **zielsetzung**: Belastbare SEA-Basis fuer alle weiteren Kampagnen.
- **kanal_slug**: `sea`
- **verantwortlich_default**: Hybrid (REACHX Setup + Kunde MCC-Freigabe)
- **aufwand_range_stunden**: 8-14
- **voraussetzungen_typ**: `tracking-ga4-setup`, MCC-Zugriff oder neues Konto
- **meilenstein_indikator**: Konto laeuft, Brand-Kampagne mit Conversions sichtbar
- **prioritaet_default**: Foundation
- **typische_monat**: 1

### sea-conquest-kampagne

- **titel**: Conquest-Kampagne auf Wettbewerber-Brands
- **beschreibung**: Kampagne auf Brand-Keywords der Top-3-Wettbewerber, mit eigenen USPs in Anzeigen und dedizierten Landingpages.
- **zielsetzung**: Wettbewerber-Suche-Volumen abgreifen, schnelle Sichtbarkeit fuer Brand-Niveau.
- **kanal_slug**: `sea`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 6-12
- **voraussetzungen_typ**: `sea-konto-setup`, Landingpages live
- **meilenstein_indikator**: Mindestens 50 Klicks und 3 Conversions innerhalb 14 Tagen
- **prioritaet_default**: Quick-Win
- **typische_monat**: 1-2

### sea-performance-max

- **titel**: Performance-Max-Kampagne fuer Top-Conversion-Ziel
- **beschreibung**: PMax-Kampagne mit allen Assets (Bild, Video, Text), Audience-Signals, Customer-Match-Listen.
- **zielsetzung**: Skalierung des Top-Ziels mit Google's Bidding-Algorithmus.
- **kanal_slug**: `sea`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 10-18
- **voraussetzungen_typ**: `sea-konto-setup`, Asset-Vorrat (Bilder, Video, Headlines)
- **meilenstein_indikator**: ROAS ueber 2.0 nach 4-6 Wochen
- **prioritaet_default**: Long-Term
- **typische_monat**: 2-3

---

## Meta-Ads

### meta-business-manager-setup

- **titel**: Meta-Business-Manager und Pixel sauber aufsetzen
- **beschreibung**: Business-Manager-Struktur, Pixel-Implementierung (incl. CAPI), Custom-Conversions, Audience-Listen anlegen.
- **zielsetzung**: Saubere Meta-Daten-Basis.
- **kanal_slug**: `meta-ads`
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde Dev fuer Pixel/CAPI)
- **aufwand_range_stunden**: 10-18
- **voraussetzungen_typ**: `tracking-ga4-setup`, Page-Admin-Rechte
- **meilenstein_indikator**: Pixel + CAPI senden konsistente Events, Match-Rate ueber 60%
- **prioritaet_default**: Foundation
- **typische_monat**: 1

### meta-ads-erstkampagne

- **titel**: Erste Meta-Ads-Kampagne mit 3 Audience-Varianten
- **beschreibung**: Awareness- oder Conversion-Kampagne, 3 Audience-Sets (Interest, Lookalike, Custom), je 2-3 Creatives.
- **zielsetzung**: Erste Performance-Daten zur Audience-Auswahl fuer Skalierung.
- **kanal_slug**: `meta-ads`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 12-24
- **voraussetzungen_typ**: `meta-business-manager-setup`, Creatives verfuegbar
- **meilenstein_indikator**: Gewinner-Audience identifiziert, CPL unter Branchen-Median
- **prioritaet_default**: Long-Term
- **typische_monat**: 2

---

## LinkedIn-Ads (B2B)

### linkedin-campaign-manager-setup

- **titel**: LinkedIn Campaign Manager und Insight Tag aufsetzen
- **beschreibung**: Insight Tag installieren, Audience-Listen (Job-Title, Industry, Company-Size), Conversion-Tracking konfigurieren.
- **kanal_slug**: `linkedin-ads`
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 6-10
- **voraussetzungen_typ**: Page-Admin-Rechte, `tracking-ga4-setup`
- **meilenstein_indikator**: Insight Tag firt sauber, mindestens 3 Audience-Listen ueber 10k
- **prioritaet_default**: Foundation
- **typische_monat**: 1-2

### linkedin-sponsored-content

- **titel**: Erste Sponsored-Content-Kampagne (Thought-Leadership oder Lead-Gen)
- **beschreibung**: 2-3 Anzeigen-Varianten mit unterschiedlichen Hooks, Lead-Gen-Form oder Conversion-Ziel.
- **kanal_slug**: `linkedin-ads`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 10-18
- **voraussetzungen_typ**: `linkedin-campaign-manager-setup`
- **meilenstein_indikator**: 50+ qualifizierte Leads oder 5%+ CTR
- **prioritaet_default**: Long-Term
- **typische_monat**: 2-3

---

## Local-SEO / GMB

### gmb-profil-optimierung

- **titel**: Google-Business-Profile vollstaendig optimieren
- **beschreibung**: Kategorien, Beschreibungstexte, Services, Fotos, Q&A, Posts; Negative-Reviews-Antwort-Prozess aufsetzen.
- **kanal_slug**: `local-seo`
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde fuer Foto-/Text-Freigaben)
- **aufwand_range_stunden**: 6-12
- **voraussetzungen_typ**: GMB-Inhaber-Rechte
- **meilenstein_indikator**: 100% Profile-Vollstaendigkeit, alle Reviews beantwortet
- **prioritaet_default**: Quick-Win
- **typische_monat**: 1

### nap-konsistenz-fix

- **titel**: NAP-Konsistenz ueber Branchenportale herstellen
- **beschreibung**: Name, Adresse, Telefon auf GMB, Website-Impressum und Branchenportalen synchronisieren.
- **kanal_slug**: `local-seo`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 4-10
- **voraussetzungen_typ**: Portal-Logins
- **meilenstein_indikator**: Mindestens 8 von 10 Top-Portalen zeigen konsistente Daten
- **prioritaet_default**: Quick-Win
- **typische_monat**: 2

---

## Content / Blog

### 03-15-web-content-inventur-stale-cleanup

- **titel**: Stale-Content aus Inventur archivieren oder ueberarbeiten
- **beschreibung**: Top-20-Stale-Content-Liste aus `content-inventur.md` durchgehen: archivieren, 301-redirecten oder ueberarbeiten.
- **kanal_slug**: `content`
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 8-20
- **voraussetzungen_typ**: `content-inventur.md` vorhanden
- **meilenstein_indikator**: 20 URLs entschieden und umgesetzt
- **prioritaet_default**: Quick-Win
- **typische_monat**: 2

### redaktionsplan-aufsetzen

- **titel**: Redaktionsplan fuer Top-Cluster-Themen aufsetzen
- **beschreibung**: 12-Monats-Redaktionsplan basierend auf `cluster_aggregat`-Top-10, Themen, Verantwortliche, Veroeffentlichungs-Rhythmus.
- **kanal_slug**: `content`
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 6-12
- **voraussetzungen_typ**: SEO-Cluster-Daten vorhanden
- **meilenstein_indikator**: Plan freigegeben, erste 3 Briefings angestossen
- **prioritaet_default**: Foundation
- **typische_monat**: 3

---

## Social-Organic (Instagram, LinkedIn-organisch, TikTok, Pinterest)

### social-content-pillars-definieren

- **titel**: Content-Pillars und Posting-Rhythmus pro relevantem Social-Kanal definieren
- **beschreibung**: Auf Basis der Wettbewerber-Audits (Instagram/LinkedIn/TikTok/Pinterest) Content-Pillars (3-5) und Posting-Frequenz festlegen.
- **kanal_slug**: kanal-spezifisch
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 6-12
- **voraussetzungen_typ**: Entsprechendes Social-Audit vorhanden
- **meilenstein_indikator**: Pillars und Plan freigegeben, erste Posts produziert
- **prioritaet_default**: Foundation
- **typische_monat**: 1-2

### social-erste-postwelle

- **titel**: Erste Postwelle (12 Posts) live setzen
- **beschreibung**: 12 Posts entsprechend der Content-Pillars produzieren und veroeffentlichen.
- **kanal_slug**: kanal-spezifisch
- **verantwortlich_default**: Hybrid (REACHX Konzept + Kunde Visual-Asset-Bereitstellung)
- **aufwand_range_stunden**: 20-40
- **voraussetzungen_typ**: `social-content-pillars-definieren`
- **meilenstein_indikator**: 12 Posts live, Engagement ueber Wettbewerber-Median
- **prioritaet_default**: Long-Term
- **typische_monat**: 2-3

---

## Website / CRO

### cro-quickfix-top-conversion-page

- **titel**: CRO-Quickfixes auf Top-Conversion-Page
- **beschreibung**: Heuristisches CRO-Audit, 3-5 priorisierte Fixes (Headline, CTA, Trust-Elemente, Form-Friction) umsetzen.
- **kanal_slug**: `website-cro`
- **verantwortlich_default**: REACHX
- **aufwand_range_stunden**: 8-16
- **voraussetzungen_typ**: `tracking-ga4-setup`
- **meilenstein_indikator**: Conversion-Rate-Lift auf Top-Page mindestens 15% (gegen Vor-Monat)
- **prioritaet_default**: Quick-Win
- **typische_monat**: 2

### cro-test-pipeline-aufsetzen

- **titel**: A/B-Test-Pipeline aufsetzen
- **beschreibung**: Test-Tool (z. B. VWO, Convert, GA4-Native) einrichten, erste 2 Tests im Backlog priorisieren.
- **kanal_slug**: `website-cro`
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 12-24
- **voraussetzungen_typ**: Genuegend Traffic (10k+ Sessions/Monat auf Test-Page)
- **meilenstein_indikator**: Erster Test laeuft, Signifikanz erreicht
- **prioritaet_default**: Long-Term
- **typische_monat**: 3

---

## Reviews / Quartals-Strategie

### performance-review-monat-2

- **titel**: Performance-Review Ende Monat 2 mit Kunde
- **beschreibung**: 60-Minuten-Review der ersten Daten, Diskussion ueber Skalierung der Gewinner, Entscheidung zu Anpassungen fuer Monat 3.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: Hybrid (REACHX Auswertung + Kunde Entscheidung)
- **aufwand_range_stunden**: 4-8
- **voraussetzungen_typ**: Mindestens 4 Wochen Live-Daten
- **meilenstein_indikator**: Review-Doc liegt vor, Entscheidungen dokumentiert
- **prioritaet_default**: Foundation
- **typische_monat**: 2

### quartals-strategie-review

- **titel**: Quartals-Strategie-Review Ende Monat 3
- **beschreibung**: 90-Minuten-Review aller 90 Tage, Forecast-Abgleich, Retainer-Empfehlung fuer Q2, Roadmap-Update.
- **kanal_slug**: `tracking-cross`
- **verantwortlich_default**: Hybrid
- **aufwand_range_stunden**: 8-12
- **voraussetzungen_typ**: alle Live-Daten der 90 Tage
- **meilenstein_indikator**: Q2-Plan freigegeben
- **prioritaet_default**: Foundation
- **typische_monat**: 3

---

## Nutzungs-Hinweise fuer den Skill

Der Generator-Skill waehlt aus dieser Bibliothek pro Plan eine kuratierte Menge:

1. **Pflicht-Foundation** unabhaengig vom Kanal-Set: `tracking-ga4-setup`, `consent-audit`, `reporting-dashboard`, `quartals-strategie-review`, `performance-review-monat-2`. Diese gehen immer in den Plan, ausser die `web-tech-tracking.md` zeigt, dass Tracking bereits sauber laeuft (dann GA4-Setup nur als Verifikations-Massnahme).
2. **Pro Top-Kanal** aus `kanal-chancen.md`: 3-5 Massnahmen aus der entsprechenden Kanal-Sektion. Die `naechste_aktion` aus dem Top-3-Eintrag wird zu einer Massnahme verdichtet.
3. **Sweet-Spot-Cluster** aus `seo-cluster-zusammenfassung.md`: pro Sweet-Spot-Cluster eine Auspraegung von `sweet-spot-cluster-content-hub` (mit Cluster-Suffix).
4. **Tech-Voraussetzungen** aus `web-tech-tracking.md` Auffaelligkeiten: pro `relevanz: hoch`-Auffaelligkeit eine entsprechende Foundation-Massnahme (oft `core-web-vitals-fix`, `schema-markup-einbauen`, `server-side-tagging`).
5. **Kunden-spezifische Erweiterungen** aus `briefing.md`: z. B. wenn Kunde explizit Lead-Generierung will und LinkedIn-Ads im Top-5 ist → `linkedin-sponsored-content` direkt einplanen.

**Aufwand-Range-Anpassung pro Kunde**: Die Bandbreiten sind Defaults fuer einen typischen Mittelstands-Kunden. Bei sehr kleinen Kunden (Solo-Selbstaendige, kleine Agenturen) wird das Min-Ende genutzt, bei groesseren Kunden (mit Komplexitaet wie Multi-Site, Multi-Sprache) wird Max-Ende oder ein hoeherer Wert genutzt.

**Verantwortlichkeits-Override** aus `briefing.md`:

- Wenn `team_setup` zeigt "Kunde ohne Inhouse-Marketing-Team" → alle Default-`Hybrid` Massnahmen verschieben Richtung `REACHX`
- Wenn `team_setup` zeigt "Kunde mit starkem Inhouse-Marketing-Team" → mehr Default-`REACHX` Massnahmen werden zu `Hybrid` (oder reine Strategie-Massnahmen bei REACHX, Operatives beim Kunden)
- Wenn `team_setup` zeigt "Kunde hat Inhouse-Dev-Team" → Tech-Umsetzung beim Kunden, Konzept bei REACHX

**Voraussetzungs-Graph**: Die Bibliothek nutzt Slug-Verweise. Der Generator-Skill loest diese in `massnahme_id`s auf, wenn die entsprechende Massnahme im konkreten Plan vorkommt, sonst werden die Voraussetzungen als Text-Hinweis erfasst.
