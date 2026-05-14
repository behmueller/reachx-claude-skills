# LinkedIn-Ads-Besonderheiten — Was bei LinkedIn anders ist als bei Google und Meta

Diese Reference erklärt die Eigenheiten der LinkedIn Ad Library, die den Skill-Workflow von `03-05-sea-google-ads-check` und `03-06-sea-meta-ads-library-check` unterscheiden. Wer den Skill nutzt oder anpasst, sollte diese Punkte präsent haben.

## 1. Company-Page-Konzept statt Domain-Match

**Bei Google**: Match über Werbetreibenden-Domain (`adstransparency.google.com/?domain=mustermann.de`).

**Bei Meta**: Match über Facebook-Page (`facebook.com/ads/library/?search_type=page&q=Mustermann`).

**Bei LinkedIn**: Match über LinkedIn **Company Page**, identifiziert durch:

- Company Page Slug (z. B. `mustermann-gmbh` in `linkedin.com/company/mustermann-gmbh/`)
- Company ID (LinkedIn-interner Numerischer Identifier)

Konsequenz für den Skill: vor jedem Scrape muss die Company-Page identifiziert werden. Reihenfolge:

1. Aus `data/kunde.md` / `wettbewerber/SLUG.md` `touchpoints` mit `typ: linkedin`
2. Aus `data/briefing.md`
3. Web-Search `"COMPANYNAME" site:linkedin.com/company`
4. Manuell-Fallback mit Strategen-Hinweis

**Implikation für die Akteurs-Liste**: Akteure ohne LinkedIn Company Page (häufig bei kleinen lokalen B2C-Unternehmen) können nicht analysiert werden. Sie tauchen im Output unter `linkedin_company_page_unbekannt: true` auf und sind selbst ein Daten-Punkt: "Akteur ist auf LinkedIn nicht präsent."

## 2. B2B-Fokus der Plattform

LinkedIn ist primär eine B2B-Plattform. Ads-Investments folgen dem Plattform-Charakter:

| Branchen-Typ | Erwartete LinkedIn-Ads-Aktivität |
|---|---|
| B2B SaaS / Enterprise-Software | hoch — Decision-Maker-Reach, Demand-Gen |
| B2B Industrie / Maschinenbau | mittel — vor allem für Recruiting, Trade-Shows |
| B2B Beratung / Agentur | mittel-hoch — Thought-Leadership, Lead-Gen |
| B2C E-Commerce | sehr gering — falscher Plattform-Fit |
| Lokales Handwerk | sehr gering |
| Lokale Gastronomie / Mode-Einzelhandel | quasi null |
| Healthcare / Pharma | mittel — Awareness bei medizinischem Fachpersonal |
| Recruiting-fokussierte Akteure | hoch — unabhängig von Branche |

Konsequenz für den Skill: bei B2C-Kontext (`b2c_kontext: true`) ist ein Null-Ergebnis erwartet. Das Skill-Output dokumentiert das als datenbasierte Annahme-Bestätigung, nicht als Skill-Fehler. Der B2C-Hinweis-Block im Output erklärt das dem Strategen.

**Architektur-Entscheidung**: `03-07-sea-linkedin-ads-library-check` läuft auch bei B2C-Branchen durch — die strategische Aussage "LinkedIn Ads spielt in dieser Branche keine Rolle" ist genauso wertvoll wie eine detaillierte Aktivitäts-Analyse.

## 3. Login-Wall — variable Coverage

LinkedIn versteckt einen Teil der Ad-Library-Inhalte hinter einem Login-Dialog. Was ohne Login sichtbar ist:

- Anzeigen-Liste mit Werbetext, CTA, Creative
- Erst-Schalt-Datum, Regionen
- Anzeigentyp

Was teilweise oder gar nicht sichtbar ist ohne Login:

- Targeting-Daten (Job-Title, Industry, Geography) — variiert pro Anzeige
- Reichweiten-Schätzungen
- Detail-Targeting-Achsen (Skills, Groups)

Konsequenz für den Skill: Coverage-Lücken sind erwartet. Der Skill markiert pro Akteur `targeting_verfuegbar: true | false` und im Top-Level Frontmatter `coverage_einschraenkung: keine | login_wall_leicht | login_wall_stark`.

**Stratege-Hinweis im Output**: bei `login_wall_stark` (das heißt: bei mehr als 50% der Akteure fehlen die Targeting-Daten) wird empfohlen, dass der Stratege bei kritischen Akteuren manuell mit eingeloggter LinkedIn-Session nachprüft. Der Skill kann das nicht automatisieren (würde LinkedIn-Login-Credentials brauchen, was für ein Marketing-Audit-Skill nicht im Scope ist).

## 4. EU-DSA-Pflicht — gute Datenbasis für EU-Akteure

Seit 2023 ist LinkedIn durch den Digital Services Act (DSA) verpflichtet, alle in der EU geschalteten Anzeigen in der Ad Library zu listen. Das hat zwei Implikationen:

**Positiv:**

- Vollständige Coverage für alle EU-aktiven Werbetreibenden (auch nicht-verifizierte, was ein Unterschied zu Google's Transparency Center ist)
- Targeting-Daten sind nach DSA-Vorgaben oft sichtbarer als auf anderen Plattformen
- 12-Monats-Historie (länger als bei Google) — der Skill kann auch kürzlich pausierte Anzeigen sehen und das Schalt-Verhalten über die Zeit besser einschätzen

**Negativ / Einschränkung:**

- Anzeigen, die nur außerhalb der EU geschaltet wurden, sind nicht in der EU-Library — bei internationalen WBs kann das eine Coverage-Lücke sein
- DSA-Targeting-Hinweise sind oft sehr grob (`Senior, Manager, Leader` als Job-Title statt detaillierter Rollen)

Konsequenz für den Skill: für DACH-MTAs ist die Library eine sehr gute Datenbasis. Internationale Akteure müssen ggf. separat geprüft werden.

## 5. Anzeigentypen — andere Familie als Google/Meta

LinkedIn hat ein eigenes Anzeigentypen-Vokabular:

| Anzeigentyp | Beschreibung | Häufigkeit in MTAs |
|---|---|---|
| `sponsored_content` | beworbener Post im Feed, häufigster Typ | hoch |
| `sponsored_messaging` | InMail-/Conversation-Ads, persönlich zugestellt | mittel, Vertriebs-fokussiert |
| `text_ads` | klassische Sidebar-Text-Anzeigen (Desktop) | selten, oft kleinere Budgets |
| `dynamic_ads` | personalisierte Anzeigen mit Profilfoto des Empfängers | selten, fortgeschritten |
| `video_ads` | Video im Feed | mittel-hoch, B2B-Storytelling |
| `document_ads` | PDF/Whitepaper als Anzeige, lead-gen-orientiert | mittel, Lead-Gen-Standard |
| `event_ads` | Event-Promotion (Webinar, Konferenz) | mittel, eventgetrieben |

Konsequenz: Im Output-Schema sind die LinkedIn-Anzeigentypen direkt benannt, nicht zu Google-Typen gemapt. Der Skill kategorisiert pro Anzeige eindeutig.

## 6. LinkedIn-spezifische Themen-Cluster

Während bei Google die dominanten Cluster meist `branded`, `produkt`, `generic` und ggf. `conquest` sind, hat LinkedIn-Ads ein eigenes Cluster-Vokabular:

- **Recruiting** — Stellenanzeigen, Employer-Branding-Posts. Bei vielen B2B-Akteuren der dominante Cluster (kann >50% der LinkedIn-Ads ausmachen). Wichtig: in der `04-02-kanal-chancen-analyse` macht es einen großen Unterschied, ob die WBs auf LinkedIn primär Recruiting machen oder Demand-Gen — ersteres heißt: Demand-Gen-Wettbewerb gering.
- **Lead-Gen** — Whitepaper, Webinar, Demo-Buchungen, Trial-Promotion
- **Event** — Konferenz-Promotion, Webinar-Einladungen
- **Thought-Leadership** — beworbene Inhalte von Executives, Studien-Promotion, Branchen-Reports
- **Branded** — Brand-Awareness ohne konkrete Conversion-Aufforderung
- **Conquest** — gegen WB-Markennamen (selten auf LinkedIn, aber strategie-relevant)
- **Thema_TOKEN** — produkt-/themenspezifische Cluster
- **Generic** — Sammelbecken

Der Skill nutzt Werbetext-Token-Matching für die Cluster-Zuweisung (siehe SKILL.md Schritt 6).

## 7. Targeting-Transparenz als strategischer Datenpunkt

Wenn LinkedIn Targeting-Daten anzeigt (DSA-getrieben), sind sie ein **wichtiger strategischer Datenpunkt für die MTA**:

- **Top-Job-Titles über alle WBs** → zeigt, welche Decision-Maker-Rollen die Branche anspricht. Wenn alle WBs auf "CTO, Head of IT" zielen und der Kunde will sich differenzieren, kann das Targeting auf andere Rollen (z. B. Operations-Lead) eine Differenzierungs-Strategie sein.
- **Top-Industries** → zeigt, welche Branchen die WBs als Kundenzielgruppe sehen. Wenn die WBs auf "Industrial Manufacturing" zielen und der Kunde eigentlich "Healthcare" als Zielgruppe hat, kann das eine USP-Bestätigung sein.
- **Top-Geographies** → zeigt Märkte, die die WBs bedienen.

Der Skill aggregiert diese drei Achsen pool-weit (über alle WBs) und legt sie im Targeting-Aggregat ab. Die `04-02-kanal-chancen-analyse` kann daraus Differenzierungs-Argumente bauen.

## 8. Sponsored Messaging und InMail — Sonderfall

Sponsored Messaging (formerly InMail) ist eine eigene Anzeigen-Familie, die persönlich zugestellt wird. In der Ad Library tauchen diese Anzeigen oft nur als Stub auf (mit Werbetext, aber ohne Targeting-Daten oder Creative).

Der Skill markiert solche Stubs als `format: text` mit `anzeige_typ: sponsored_messaging`, zählt sie aber mit. Im Output-Body kann ein Hinweis stehen, dass Sponsored Messaging in der Library nur teilweise abgebildet wird.

## 9. Kein Spend-Tracking

Anders als bei Google (wo SpyFu Spend-Schätzungen liefert), gibt es für LinkedIn-Ads **kein verlässliches Drittanbieter-Spend-Tracking**. Tools wie Pathmatics, SimilarWeb oder LinkedIn Sales Navigator geben grobe Schätzungen, sind aber:

- selten in REACHX-Lizenzen verfügbar
- meist nicht für DACH-Markt brauchbar
- mit zu großen Unschärfen behaftet

**Architektur-Entscheidung**: Der Skill verzichtet auf Spend-Schätzungen. Stattdessen wird die Aktivitäts-Intensität (Anzahl Anzeigen × Anzeigentypen-Mix × Schalt-Dauer) als Proxy verwendet.

## 10. Reproduzierbarkeit und UI-Wechsel

Die LinkedIn-Ad-Library-UI ändert sich periodisch (ungefähr alle 3-6 Monate substanziell). Konsequenzen:

- **Selektoren altern**: bei jedem Skill-Lauf wird mitgeloggt, welche Felder erfolgreich extrahiert wurden vs. welche fehlen. Bei einer Häufung von Fehlern: Selektoren prüfen.
- **Roh-Daten immer speichern**: in `audits/raw/linkedin-ads-AKTEURSSLUG.json` liegt die Apify-Roh-Antwort. Bei UI-Bruch kann die Extraktions-Logik nachgezogen werden, ohne neu zu scrapen.
- **Apify-Actor-Wahl**: bei UI-Bruch oft schneller, einen anderen Apify-Actor zu probieren als einen Custom-Puppeteer-Workflow zu pflegen. Im SKILL.md Schritt 4 ist die Fallback-Kaskade dokumentiert.

## 11. Pattern-Konsistenz mit Google-Ads-Check und Meta-Ads-Library-Check

Trotz aller LinkedIn-Eigenheiten ist die Output-Struktur **strikt parallel** zu `03-05-sea-google-ads-check` und `03-06-sea-meta-ads-library-check`:

- Pfad-Pattern: `audits/PLATTFORM-ads.md` + `audits/PLATTFORM-ads-anzeigen.csv` + `audits/raw/PLATTFORM-ads-SLUG.json` + `reports/NN-PLATTFORM-ads.html`
- CSV-Spalten: gleiche Basis-Spalten (akteurs_slug, anzeige_id, anzeige_typ, etc.) plus plattform-spezifische Erweiterungen
- Markdown-Frontmatter: gleiche Top-Level-Struktur (Provenienz, akteure, themen_cluster, statistiken, auffaelligkeiten)
- Auffälligkeits-Familien: identische Basis (kunde_inaktiv_wb_aktiv, conquest_aktivitaet etc.) plus plattform-spezifische (linkedin_ads_kein_branchen_thema, linkedin_login_wall_coverage_luecke)

Das stellt sicher, dass `04-02-kanal-chancen-analyse` und `04-04-forecast-modell` die Outputs der drei Ads-Skills mit einer einheitlichen Logik konsumieren können — pro Plattform identische Pattern-Verarbeitung.

## 12. Was NICHT in diesen Skill gehört

- **LinkedIn-Organic-Content-Analyse** — gehört zu `03-11-social-linkedin`. Der vorhandene Skill macht die Posts-Analyse und Mitarbeiter-Auswertung — `03-07-sea-linkedin-ads-library-check` fokussiert ausschließlich auf bezahlte Anzeigen.
- **LinkedIn-Account-Audit** (Profil-Qualität, Connections, Sales Navigator Lists) — out of scope, gehört in einen separaten Audit-Skill, falls je benötigt.
- **LinkedIn-Post-Quality-Rating** — separater Skill `03-12-social-linkedin-post-quality`, bewertet Organic-Posts entlang 5 Dimensionen.
- **Spend-Schätzungen** — siehe Punkt 9, bewusst weggelassen.
- **Targeting-Detail-Recherche** über die Ad-Library hinaus — out of scope. Wenn der Stratege detailliertes Targeting der WBs sehen will, muss er manuell in LinkedIn Campaign Manager rein.
- **A/B-Test-Erkennung** — heuristisch unsicher, manueller Stratege-Job.
- **Eigene Konkurrenz-Beobachtung über Zeit** — wäre ein laufender Monitoring-Skill, nicht Teil der MTA.
