# Google Ads Transparency Center — Zugriff und Mapping

Operative Vorgaben für den Zugriff auf das Google Ads Transparency Center (TC) — welche Apify-Actors, welche URL-Patterns, welche Datenfelder, welche Limitierungen.

## Was ist das Transparency Center?

Google's öffentliches Werbetreibenden-Verzeichnis: `https://adstransparency.google.com/`. Seit 2023 zeigt Google dort **alle Anzeigen verifizierter Werbetreibender** (verifiziert nach Googles Advertiser-Identity-Program), inklusive Schalt-Zeitraum, Regionen, Anzeigenformate und Werbetexte. **Kein Login nötig, keine API-Auth.**

**Was es zeigt:**

- Anzeigen verifizierter Werbetreibender
- Aktuelle und kürzlich pausierte Anzeigen
- Erst-Schalt-Datum
- Aktive Regionen
- Werbetext und Creatives (Bilder/Videos)
- Anzeigentyp (Search, Display, Video, Shopping)

**Was es NICHT zeigt:**

- Anzeigen nicht-verifizierter Werbetreibender (kleinere Konten)
- Historische Spend-Daten
- Klick-/Impression-Zahlen
- CPC-Werte
- Keyword-Targeting

Für **Spend-Schätzungen** brauchen wir Drittanbieter (SpyFu, SEMrush, iSpionage) — siehe unten Abschnitt "Spend-Schätzungen".

## URL-Patterns

Pro Akteur drei mögliche Such-Modi:

| Suche nach | URL-Pattern | Wann |
|---|---|---|
| Domain | `https://adstransparency.google.com/?domain=<domain>` | **Standard im Skill** — direkter Akteurs-Match |
| Werbetreibenden-Name | `https://adstransparency.google.com/?creative-format=&region=anywhere&start-date=&end-date=&searchTerm=<name>` | Fallback wenn Domain-Suche leer |
| Werbetreibenden-ID | `https://adstransparency.google.com/advertiser/<id>` | nur wenn ID bereits bekannt aus früherer Recherche |

**Domain-Match-Heuristik**: das TC erlaubt manchmal nur exakte Domain-Treffer. Vor dem Scrape die normalisierte Domain prüfen — falls keine Treffer, mit Hauptmarken-Name als Fallback suchen.

## Apify-Actor-Optionen — getestete Actor-IDs

Getestete Actors (Stand des Projekteinsatzes). Vor dem Lauf immer den Health-Check (Limit-1-Aufruf mit Kunden-Domain) durchführen; bei Fehler Alternativen aus der Liste probieren. Login-Wall-Quellen werden explizit markiert.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `apify/google-ads-transparency-center-scraper` | Google Ads TC Scraper (official) | noch nicht getestet | unbekannt | Als Erste Wahl probieren |
| `igolaizola/google-ads-transparency-scraper` | Community TC Scraper | noch nicht getestet | unbekannt | Erster Fallback |
| `compass/google-ads-transparency-center` | TC Compass | noch nicht getestet | unbekannt | Zweiter Fallback |

**Login-Wall:** Das Transparency Center ist öffentlich ohne Login zugänglich — kein authentifizierter Scraper nötig. Sollte ein Actor dennoch Login-Fehler zurückgeben, ist das ein Apify-Sessions-Problem, kein TC-Problem → Session-Reconnect, dann Retry.

### Erste Wahl: `apify/google-ads-transparency-center-scraper` (falls vorhanden im Store)

**Vorteile:**

- Speziell für TC entwickelt — kennt die UI-Quirks
- Liefert strukturierte JSON-Daten
- Pagination-Handling eingebaut

**Input-Parameter:**

```json
{
  "domains": ["mustermann.de", "beta-solutions.com"],
  "region": "DE",
  "maxAdsPerDomain": 100,
  "includeInactive": false,
  "language": "de"
}
```

Wenn der Standard-Actor nicht verfügbar ist, im Apify-Store nach Alternativen suchen:

- `igolaizola/google-ads-transparency-scraper`
- `compass/google-ads-transparency-center`
- Generische Community-Actors

Pro Actor: vor dem Lauf einen kleinen Healthcheck mit der Kunden-Domain, um Datenformat zu prüfen.

### Fallback: Custom Puppeteer-Skript

Wenn kein spezialisierter Actor verfügbar oder verlässlich ist: `apify/puppeteer-scraper` mit Custom-Page-Function.

**Wichtige Page-Function-Schritte:**

1. Navigiere zur Domain-URL
2. Warte auf `.advertiser-header` oder vergleichbares Element
3. Wenn Cookie-Banner: akzeptieren (selektor `[aria-label*="alle akzeptieren" i]`)
4. Scroll-Trigger für Lazy-Loading: Page-Down mehrmals, bis Anzeigen-Anzahl stabil
5. Pro Anzeige-Karte: `querySelector('.ad-card')` und extrahiere Felder
6. Optional: Klick auf "Anzeigen-Details" für vollständigen Werbetext

**Wichtig:** TC-UI ändert sich periodisch. Bei Änderungen müssen Selektoren angepasst werden. Im `audits/raw/<akteurs-slug>.json` immer die Roh-Antwort speichern, damit bei UI-Bruch nur die Extraktions-Logik anzupassen ist.

### Hard-Fallback: Manueller Check

Wenn alle Apify-Optionen scheitern: Skill produziert eine Liste der TC-URLs aller Akteure und bittet den Strategen um manuellen Check. Im Output-Markdown unter `manueller_check_erforderlich` listen.

## Datenfelder (Mapping zu Output-CSV-Spalten)

Was der Actor / das Scrape liefern muss, mit Mapping auf die CSV-Spalten:

| TC-Feld | CSV-Spalte | Typ | Hinweis |
|---|---|---|---|
| Advertiser Display Name | `werbender_name` | string | manchmal abweichend von Domain ("Mustermann GmbH" statt "mustermann") |
| Verified Advertiser | `werbender_verifiziert` | bool | true wenn Google-Checkmark sichtbar |
| Ad ID / Creative ID | `anzeige_id` | string | wenn fehlt: Hash aus headline+datum+advertiser |
| Ad Format | `anzeige_typ` | enum | search/display/video/shopping/demand_gen/unbekannt |
| Creative Format | `format` | string | text/image/video/responsive_search/responsive_display |
| First Shown Date | `erst_schalt_datum` | ISO-8601 | beim TC manchmal nur Monat — dann auf Monatsersten setzen |
| Last Shown Date | `letzte_anzeige_datum` | ISO-8601 oder leer | nur wenn nicht mehr aktiv |
| Active Countries | `aktive_in_regionen` | string (kommagetrennt) | ISO-Country-Codes |
| Headline (Search) | `werbetext_headline` | string | bis 90 Zeichen typisch |
| Description (Search) | `werbetext_beschreibung` | string | bis 180 Zeichen typisch |
| Final URL | `landingpage_url` | URL | inklusive Query-Params |
| Image/Video URL | `creative_url` | URL oder leer | nur bei Display/Video |

**`landingpage_tiefe`** wird im Skill berechnet aus der URL-Path-Tiefe:

- `/` → 0 (Homepage)
- `/produkte/` → 1
- `/produkte/aufmasswerkzeuge/` → 2
- `/produkte/aufmasswerkzeuge/details/` → 3

Wichtig für Auffälligkeit `landingpage_qualitaet_inkonsistent`.

## Region-Filter

Aus `meta.json.region` (siehe `contracts.md` Abschnitt 2):

- `Deutschland` → Filter auf `DE`
- `DACH` → `DE`, `AT`, `CH`
- `Europa` → erweiterte Liste
- Bei Override im Skill-Aufruf "auch internationale Anzeigen": kein Filter

Pro Anzeige `in_zielregion: true | false` setzen. Anzeigen außerhalb der Zielregion bleiben in der CSV, im Aggregat aber separat ausgewiesen (`internationale_aktivitaet`-Sektion).

## Spend-Schätzungen (SpyFu)

Das TC liefert **keine Spend-Daten**. Wenn der Stratege Spend-Schätzungen will, kommt SpyFu zum Einsatz.

### SpyFu-Endpoints

Pro Akteur ein Lookup:

```text
GET https://api.spyfu.com/v1/domain/<domain>/overview
?api_key=<KEY>
&country=de
```

Liefert (vereinfacht):

- `monthly_paid_clicks_estimate`
- `monthly_paid_spend_estimate_usd_low`
- `monthly_paid_spend_estimate_usd_high`
- `paid_keywords_count`

**Konvertierung zu EUR**: aktueller Wechselkurs (heuristisch, eine Tageskurs-Schätzung reicht) oder fix als 1 USD ≈ 0.92 EUR (Stand 2026-05). Im Frontmatter den verwendeten Kurs dokumentieren.

### Rate-Limits und Credits

SpyFu zählt pro Domain-Lookup einen Credit. Bei 10 Akteuren = 10 Credits. Bei Standard-Accounts unproblematisch, bei Trial-Accounts ggf. enger — Skill prüft Quota vorab.

Bei Quota-Überschreitung: nur Kunde + Top-3-WB nach Anzeigen-Anzahl mit Spend, Rest ohne. Im Output Hinweis.

### Alternative: SEMrush oder iSpionage

Wenn SpyFu nicht da ist, andere Drittanbieter:

- **SEMrush**: über `mcp__semrush__*` (falls verbunden) oder API mit `SEMRUSH_API_KEY`
- **iSpionage**: derzeit nicht im REACHX-Stack, daher kein Default-Support

Im Skill aktuell nur SpyFu implementiert — andere können später ergänzt werden.

## Caching und Re-Runs

Pro Lauf werden alle Roh-Antworten in `audits/raw/` abgelegt:

- `google-ads-<akteurs-slug>.json` — TC-Roh-Antwort
- `google-ads-spyfu-<akteurs-slug>.json` — SpyFu-Roh-Antwort

Bei Re-Run: Skill prüft, ob die Roh-Daten älter als 7 Tage sind:

- < 7 Tage → Cache nutzen, kein Re-Scrape
- ≥ 7 Tage → neu ziehen

Override `force_refresh` umgeht den Cache.

## Limitierungen des Transparency Centers (für die MTA-Story zu kommunizieren)

1. **Nur verifizierte Werbetreibende sichtbar** — kleinere Konten fehlen. Wenn ein Akteur nicht im TC ist, heißt das nicht zwangsläufig "schaltet keine Ads".
2. **Keine Spend-Daten** — Spend-Schätzungen kommen aus Drittanbietern und sind Ranges, keine harten Werte.
3. **Keine Targeting-Details** — wir sehen die Anzeige, nicht für welche Keywords sie ausgespielt wird. Keyword-Schätzungen kommen aus SEO-Recherche oder SpyFu.
4. **Snapshot-Charakter** — TC zeigt aktuell aktive plus kürzlich pausierte Anzeigen. Langfristige Strategie-Trends nicht ableitbar ohne Drittanbieter-Historie.
5. **Region-Granularität ist Country-Level** — nicht Stadt/PLZ. Lokal-Targeting innerhalb DE ist nicht sichtbar.

Diese Limitierungen werden in `audits/google-ads.md` "Lücken und Hinweise" am Ende explizit dokumentiert, damit der Stratege beim Kunden-Gespräch nicht überzieht.

## Was NICHT in diesen Skill gehört

- **Detaillierte Keyword-Targeting-Analyse** — gehört nicht zur MTA, würde Sistrix-/Ahrefs-Daten brauchen
- **Anzeigen-Qualitäts-Bewertung** (Quality Score) — Google liefert das nicht öffentlich
- **A/B-Test-Erkennung** — heuristisch unsicher, manueller Stratege-Job
- **Eigene Konkurrenz-Beobachtung über Zeit** — wäre ein separater laufender Monitoring-Skill, nicht Teil der MTA
