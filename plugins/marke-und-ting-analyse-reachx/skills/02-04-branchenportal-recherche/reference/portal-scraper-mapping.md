# Portal-Scraper-Mapping

Pro Branchenportal: welche Recherche-Methode ist die zuverlässigste, welcher Apify-Actor (falls vorhanden), welches URL-Pattern für die Profil-Auflösung via Web-Search, und welche portal-spezifischen Zusatz-Felder erfasst werden.

**Stand:** Mai 2026 — initial. Wächst mit jeder neuen Branche.

## Methoden-Glossar

| Methode | Wann nutzen |
|---|---|
| **A — Apify-Portal-Scraper** | Es existiert ein zuverlässiger, gepflegter Apify-Actor für dieses Portal. Erste Wahl, weil strukturierte Daten und niedrigste Fehlerquote. |
| **B — Web-Search + URL-Pattern** | Kein Apify-Actor verfügbar oder Portal akzeptiert direkte URL-Patterns. Skill nutzt Web-Search mit `site:<portal-domain>` plus den Akteurs-Namen, nimmt den Top-Treffer als Profil-URL und scraped die Seite (falls öffentlich zugänglich). |
| **C — Apify-Puppeteer mit Portal-interner Suche** | Portal hat keine direkten URL-Patterns ODER ist hinter JS-Wall / Cookie-Wall. `apify/puppeteer-scraper` mit Custom Page-Function, simuliert die Portal-eigene Suche. |
| **D — Manuelle Recherche** | Login-Wall oder Anti-Bot-Schutz, der keine der drei automatischen Methoden zulässt. Skill markiert die Task als `recherche_fehlgeschlagen` mit Empfehlung an den Strategen. |

## Portal-Übersicht

### Gesundheitswesen

#### jameda.de

| | |
|---|---|
| Methode | A (Apify Jameda-Scraper) ODER B (Web-Search) |
| Apify-Actor | `apify/jameda-scraper` (falls nicht vorhanden: Methode B) |
| URL-Pattern (B) | `<akteurs-name> site:jameda.de` |
| Zusatz-Felder | Note-Skala (1.0 = beste, 6.0 = schlechteste), Anzahl Patientenbewertungen, Fachrichtungen, Kassen-Privat, Sprechzeiten |
| Aktivitäts-Indikator | Datum der letzten Bewertung |

#### doctolib.de

| | |
|---|---|
| Methode | C (Puppeteer + portal-interne Suche) |
| Apify-Actor | `apify/puppeteer-scraper` mit Custom-Script |
| URL-Pattern (B) | `<akteurs-name> site:doctolib.de` (oft direkt funktionierend) |
| Zusatz-Felder | Anzahl Online-Termine verfügbar, Profil-Verifizierung, akzeptierte Versicherungen |
| Aktivitäts-Indikator | Aktuelle Termin-Verfügbarkeit als Aktivitäts-Beweis |

#### sanego.de / arzt-auskunft.de / weisse-liste.de

| | |
|---|---|
| Methode | B (Web-Search) |
| URL-Pattern | `<akteurs-name> site:<portal-domain>` |
| Zusatz-Felder | Standard-Score, Reviews-Count |

### Rechts- und Steuerberatung

#### anwalt.de

| | |
|---|---|
| Methode | A oder B |
| Apify-Actor | `apify/anwalt-de-scraper` (prüfen, ob aktuell) — sonst Methode B |
| URL-Pattern (B) | `<akteurs-name> site:anwalt.de` |
| Zusatz-Felder | Rechtsgebiete, Standort, Premium-Mitglied (ja/nein), Anzahl beantworteter Forum-Fragen |
| Aktivitäts-Indikator | Datum der letzten Bewertung oder Forum-Antwort |

#### ProvenExpert (branchenübergreifend, sehr häufig)

| | |
|---|---|
| Methode | B (Web-Search funktioniert in der Regel zuverlässig) |
| URL-Pattern | `<akteurs-name> site:provenexpert.com` |
| Zusatz-Felder | Empfehlungs-Note (1,0–5,0), Anzahl Empfehlungen gesamt, Anzahl Bewertungen (eigene + Portal-Aggregat), Premium-Status (Gold/Platin) |
| Aktivitäts-Indikator | Datum der letzten Bewertung |
| Besonderheit | ProvenExpert aggregiert oft Bewertungen aus anderen Portalen — Doppelzählung in der MTA-Auswertung vermeiden (im Auffälligkeiten-Block ausweisen) |

#### ageras.de / advocado.de

| | |
|---|---|
| Methode | B oder C |
| URL-Pattern | `<akteurs-name> site:ageras.de` / `site:advocado.de` |
| Zusatz-Felder | Vermittlungs-Profil-Vorhanden ja/nein, ggf. Tarif-Modell |
| Aktivitäts-Indikator | sehr schwer zu erfassen — typisch `unklar` |

### Handwerk

#### myhammer.de

| | |
|---|---|
| Methode | C (Puppeteer + Portal-Suche, weil Profile nicht via Google indexiert) |
| Apify-Actor | `apify/puppeteer-scraper` mit Custom-Script auf MyHammer-Suche |
| URL-Pattern (B) | als Fallback `<akteurs-name> site:my-hammer.de` |
| Zusatz-Felder | Anzahl abgeschlossene Aufträge, Bewertungsschnitt, Gewerke-Kategorien |
| Aktivitäts-Indikator | Datum des letzten abgeschlossenen Auftrags |

#### houzz.de

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<akteurs-name> site:houzz.de` |
| Zusatz-Felder | Anzahl Projekte im Portfolio, Anzahl Followers, Best-of-Houzz-Plakette ja/nein |
| Aktivitäts-Indikator | Datum des letzten Projekt-Uploads |

### Hospitality

#### booking.com / HRS / expedia.de / trivago.de

| | |
|---|---|
| Methode | A bevorzugt (es gibt mehrere Apify-Actors), sonst B |
| Apify-Actor | `voyager/booking-scraper`, `voyager/hrs-scraper`, `voyager/expedia-scraper`, `voyager/trivago-scraper` (prüfen) |
| URL-Pattern (B) | `<hotel-name> <stadt> site:booking.com` etc. |
| Zusatz-Felder | Bewertungsschnitt (Skala-bewusst — Booking 1-10, Expedia 1-5), Anzahl Bewertungen, Sterne-Klassifizierung, Kategorie-Subscores (Sauberkeit, Lage, Service) |
| Aktivitäts-Indikator | Datum der letzten Bewertung |
| Besonderheit | OTAs sind Lead-Plattformen — Preisrate und Verfügbarkeits-Daten sind aus MTA-Sicht weniger relevant als Bewertungs-Profil |

#### TripAdvisor

| | |
|---|---|
| Methode | A (Apify TripAdvisor-Scraper) — sehr zuverlässig |
| Apify-Actor | `maxcopell/tripadvisor` oder `apify/tripadvisor-scraper` |
| URL-Pattern (B) | als Fallback `<name> <stadt> site:tripadvisor.com` |
| Zusatz-Felder | Bewertungsschnitt (1-5), Anzahl Reviews, Ranking innerhalb der Stadt, Auszeichnungen (Travelers Choice etc.) |
| Aktivitäts-Indikator | Datum der letzten Review |

#### holidaycheck.de / yelp.de

| | |
|---|---|
| Methode | B oder A |
| Apify-Actor | `apify/yelp-scraper` (für Yelp) — HolidayCheck typisch B |
| URL-Pattern | `<name> <stadt> site:holidaycheck.de` / `site:yelp.de` |
| Zusatz-Felder | Standard |

#### Reservierungs-Plattformen (OpenTable / Quandoo / The Fork)

| | |
|---|---|
| Methode | B oder C (Portal-Suche) |
| Zusatz-Felder | Aktuelle Reservierungs-Verfügbarkeit als Aktivitäts-Beweis, Bewertungsschnitt, Anzahl Reviews, Cuisine-Tags |

### Immobilien

#### ImmoScout24 / Immowelt / immonet.de

| | |
|---|---|
| Methode | A oder B |
| Apify-Actor | `apify/immoscout24-scraper`, `apify/immowelt-scraper` (für Maklerprofile, nicht Inserate) |
| URL-Pattern (B) | `<makler-name> site:immobilienscout24.de` etc. |
| Zusatz-Felder | Anzahl aktive Inserate, Makler-Bewertungsschnitt, Premium-Status, Tätigkeitsschwerpunkte |
| Aktivitäts-Indikator | Datum des letzten neuen Inserats |
| Besonderheit | Makler-Profile sind typisch versteckter als Inserate — Methode C kann nötig sein |

### B2B-Software / SaaS

#### G2

| | |
|---|---|
| Methode | C (G2 hat Login-Wall für tiefere Daten) ODER B (für Basis-Daten ohne Login) |
| Apify-Actor | `apify/g2-scraper` (oft eingeschränkt) — typisch zuerst B versuchen |
| URL-Pattern (B) | `<produkt-name> site:g2.com` |
| Zusatz-Felder | Star-Rating (1-5), Anzahl Reviews, G2-Grid-Position (Leader/High Performer/Contender), Awards-Plaketten |
| Aktivitäts-Indikator | Datum der letzten Review |
| Besonderheit | Detail-Daten oft hinter Login — Basis-URL + Star-Rating + Reviews-Count über Google-Snippet meistens extrahierbar |

#### Capterra

| | |
|---|---|
| Methode | B (Capterra hat öffentliche Profile) |
| URL-Pattern | `<produkt-name> site:capterra.com` (oder `.de`) |
| Zusatz-Felder | Standard plus Top-Listen-Plakette ("Top 20 in Kategorie"), Pricing-Indikation |
| Aktivitäts-Indikator | Datum der letzten Review |

#### OMR Reviews

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<produkt-name> site:omr.com/de/reviews` |
| Zusatz-Felder | Standard plus OMR-Vergleichs-Position (z. B. "Platz 3 in CRM-Software") |

#### GetApp / SoftwareAdvice / TrustRadius

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<produkt-name> site:getapp.com` / `site:softwareadvice.com` / `site:trustradius.com` |
| Zusatz-Felder | Standard |

### B2B-Industrie / Maschinenbau

#### wlw.de (Wer-liefert-was)

| | |
|---|---|
| Methode | B oder C |
| URL-Pattern | `<firma> site:wlw.de` |
| Zusatz-Felder | Mitarbeiter-Klassifizierung, Kategorien-Listen, Premium-Mitglied ja/nein, Anzahl Anfragen-Möglichkeiten |
| Aktivitäts-Indikator | Aktualität der Produkt-Listings (oft schwer zu erkennen) |

#### Europages

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<firma> site:europages.com` |
| Zusatz-Felder | Standard |

### E-Commerce / Online-Handel

#### Trustpilot

| | |
|---|---|
| Methode | A (Apify Trustpilot-Scraper sehr zuverlässig) |
| Apify-Actor | `apify/trustpilot-scraper` |
| URL-Pattern (B) | `<shop-name> site:trustpilot.com` |
| Zusatz-Felder | TrustScore (0-5), Anzahl Reviews, Verifizierungs-Status, Antwort-Rate des Akteurs auf Reviews |
| Aktivitäts-Indikator | Datum der letzten Review + Antwort-Aktivität des Akteurs |

#### Trusted Shops

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<shop-name> site:trustedshops.de` |
| Zusatz-Felder | Trusted-Shops-Score, Anzahl Bewertungen, Gütesiegel-Status (Basic/Premium) |

#### eKomi

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<shop-name> site:ekomi.de` |
| Zusatz-Felder | eKomi-Siegel-Stufe (Silver/Gold/Platinum), Score, Reviews-Count |

### Branchenübergreifend (immer prüfen)

#### Google Business Profile / Google Reviews

| | |
|---|---|
| Methode | A (über Google Maps Scraper) |
| Apify-Actor | `compass/google-maps-scraper` oder `apify/google-maps-extractor` (mit `searchString: <akteurs-name> <stadt>`) |
| Zusatz-Felder | Sterne-Score (1-5), Anzahl Reviews, Kategorien, Telefon, Adresse, Öffnungszeiten-Pflege-Aktualität, Foto-Anzahl |
| Aktivitäts-Indikator | Datum der letzten Review, Datum der letzten Inhaber-Antwort, Aktualität der Öffnungszeiten |
| Besonderheit | Für lokal-bezogene Akteure das **wichtigste** Portal — bei `03-16-local-gmb-und-seo` wird das vertieft, hier nur Stamm-Daten |

#### kununu

| | |
|---|---|
| Methode | B |
| URL-Pattern | `<firma> site:kununu.com` |
| Zusatz-Felder | Bewertungsschnitt Mitarbeiter (1-5), Bewertungsschnitt Bewerber, Anzahl Bewertungen, Top-Company-Plakette ja/nein |
| Aktivitäts-Indikator | Datum der letzten Mitarbeiter-Bewertung |
| Besonderheit | Indirekter Marketing-Touchpoint — beeinflusst B2B-Reputation via Recruiting-Visibility |

#### LinkedIn Company Page

| | |
|---|---|
| Methode | A (über LinkedIn-Scraper) ODER über Touchpoint aus `02-01-kunden-marken-profil` / `wettbewerber/SLUG.md` |
| Apify-Actor | `apify/linkedin-company-scraper` oder die Daten aus `03-11-social-linkedin` referenzieren, falls vorhanden |
| Zusatz-Felder | Follower-Count, Anzahl Mitarbeiter (laut Profil), Branche, Post-Frequenz |
| Aktivitäts-Indikator | Datum des letzten Posts |
| Besonderheit | Vertiefte Analyse macht `03-11-social-linkedin` — hier nur Stamm-Daten und Existenz-Check |

## Hinweise zur Pflege dieser Liste

- Bei neuen Branchen in `02-02-wettbewerber-identifikation/reference/branchenportale-mapping.md` ergänzen, dann **dieser Liste hier folgen** und die Recherche-Methode dokumentieren
- Apify-Actor-Namen können sich ändern — bei Skill-Lauf zuerst prüfen, ob der Actor existiert. Bei Fehlern auf Methode B oder C fallen
- Wenn ein Portal eine API hat (z. B. Google Places API für GMB), kann das langfristig sauberer sein als Scraping — aber API-Limits beachten

## Was passiert mit Daten, die hier nicht aufgelistet sind?

Wenn ein Portal in `identifikation-schema.md` steht, das hier nicht gemappt ist:

1. Skill versucht standardmäßig Methode B (Web-Search mit `site:<domain>`)
2. Wenn das funktioniert, läuft der Lauf durch und der Skill notiert in der Output-Datei `methode: B_fallback`
3. Wenn Methode B keine Treffer bringt: Status `recherche_fehlgeschlagen` mit Fehler-Typ `unbekanntes_portal`, Hinweis im Schluss-Format an den Strategen, dieses Mapping zu ergänzen
