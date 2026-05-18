# Tools-Mapping für Local-SEO-Audit

Übersicht über die in Phase B genutzten Recherche-Tools mit Stärken, Schwächen und Fallback-Kaskade.

## Getestete Actor-IDs

Vor dem Lauf immer den Health-Check (Limit-1-Aufruf mit Kunden-GMB-URL) durchführen; bei Fehler Alternativen aus der Liste probieren.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `compass/google-maps-scraper` | Google Maps Scraper (Compass) | noch nicht getestet | unbekannt | Erste Wahl GMB-Profil |
| `apify/google-maps-extractor` | Google Maps Extractor (official) | noch nicht getestet | unbekannt | Fallback GMB-Profil |
| `apify/google-maps-local-pack-scraper` | Local Pack Scraper | noch nicht getestet | unbekannt | Erste Wahl Local-Pack-Rankings |
| `apify/puppeteer-scraper` | Custom Puppeteer | — | fallback | Nur wenn kein spezialisierter Actor verfügbar |

**Login-Wall:** Google Maps ist öffentlich ohne Login zugänglich. Keine Auth notwendig. Apify-Session-Fehler sind Session-Probleme, kein Maps-Problem → Reconnect, dann Retry.

## 1. GMB-Profil-Scrape

### Bevorzugt: Apify `compass/google-maps-scraper`

- Liefert: Profil-Daten (Name, Adresse, Telefon, Website, Kategorien, Öffnungszeiten, Beschreibung), Medien-Count, Reviews-Sample, Posts
- Input-Optionen: Google-Maps-URL ODER Suchbegriff + Standort
- Pro Akteur: 1 Call mit `placeIds` (wenn GMB-URL aus `data/kunde.md` extrahierbar) sonst 1 Call mit `searchStringsArray: [name + stadt]`
- Reviews: Parameter `maxReviews: 50`, `reviewsSort: newest`
- Stärken: robust, regelmäßig aktualisiert, viele Felder
- Schwächen: bei Rate-Limit oder Bot-Erkennung können Reviews unvollständig sein

### Alternative: Apify `apify/google-maps-extractor`

- Funktional ähnlich, andere Default-Felder
- Fallback wenn `compass/google-maps-scraper` Probleme macht

### Letzter Fallback: Manuelle Profil-Erfassung

Web-Search nach `<name> google my business` → manuelle Erfassung der zentralen Felder, keine Reviews. Reduced-Modus, im Output explizit markiert.

### Cache-Strategie

Pro Akteur und Standort einen Cache `audits/raw/gmb-<slug>.json` mit:

```json
{
  "akteur_slug": "muster-zahnarzt-mitte",
  "standort_id": "hauptsitz",
  "scrape_datum": "2026-05-13T11:00:00Z",
  "apify_actor": "compass/google-maps-scraper",
  "raw": { ... vollständiges Apify-Result ... }
}
```

Bei Re-Run prüft der Skill, ob der Cache jünger als 14 Tage ist — wenn ja, kein erneuter Apify-Call.

## 2. Local-Pack-Rankings

### Option A (bevorzugt): Apify `apify/google-maps-local-pack-scraper` oder Äquivalent

- Input: Lat/Lng des Standorts + Keyword (= eine Local-Pack-Query)
- Output: Top-3-Local-Pack plus Top-10-Maps-Ergebnisse mit Position, Name, Adresse, Rating, Rezensions-Anzahl
- Pro Local-Pack-Query: 1 Call
- Bei 12 Keywords × 3 Standorten = 36 Calls (typischer Lauf)

### Option B (präziser, kostenpflichtig): Local Falcon API

- Grid-basiertes Ranking-Tool — pro Standort wird ein NxN-Grid in der Stadt aufgespannt, pro Grid-Punkt das Ranking ermittelt
- Liefert räumliche Sichtbarkeits-Karte (in welchen Stadtteilen ist der Akteur stark, wo nicht)
- API-Key nötig
- Stärken: präziser als Apify-Einzel-Calls, gut für Multi-Filial-Akteure
- Schwächen: Credits/Kosten, nicht im REACHX-Standard-Stack

Wenn Stratege Local-Falcon-Credentials konfiguriert hat (`LOCAL_FALCON_API_KEY` Env-Variable), bevorzuge Falcon vor Apify.

### Option C (Web-Search-Fallback): SerpAPI oder Web-Search-Tool

- Bei fehlenden Apify-Credits oder Local-Falcon: per Web-Search die Local-Pack-Snippets ziehen
- Nur Top-3 zuverlässig erfassbar (Local Pack im klassischen SERP)
- Reduced-Modus, im Output mit `quelle: web_search` markiert, `tiefe: top_3_nur`

### Tool-Wahl-Kaskade

```text
1. Local Falcon (wenn API-Key gesetzt)
2. Apify Local-Pack-Scraper
3. SerpAPI / Web-Search (Reduced-Modus)
```

### Pro-Query-Output (in CSV)

```csv
standort_id, keyword, position, akteur_slug, name, adresse, rating, rezensions_anzahl, quelle, scrape_datum
```

Wenn ein Akteur in der Top-10 nicht in der Akteurs-Liste matched: `akteur_slug = unbekannt`, Auffälligkeit `local_wb_nicht_in_liste` aggregieren.

## 3. NAP-Konsistenz

### Quelle GMB

Direkt aus dem GMB-Scrape (siehe oben).

### Quelle Website-Impressum

Apify `apify/website-content-crawler` auf die Akteur-Domain mit:

```yaml
startUrls:
  - https://<domain>/impressum
  - https://<domain>/kontakt
  - https://<domain>/datenschutz   # manchmal NAP-Daten am Footer
crawlerType: cheerio
maxCrawlPages: 5
saveMarkdown: true
```

Aus dem Markdown per Regex / LLM-Extraktion:

- **Name**: Firmenname (Lookup nach "Anbieter:", "Verantwortlich:", "Inhaber:", oder erstes auffälliges Firmen-Pattern)
- **Adresse**: Straße + PLZ + Stadt (Regex `\d{5}\s+[A-ZÄÖÜ][\w-]+`)
- **Telefon**: Regex `(\+49|0)[\d\s\-/()]+` mit mindestens 8 Ziffern

### Quelle Branchenportale

Pro Akteur, der in `wettbewerber/portale.md` Profile hat, die Portal-URL nochmal abrufen (Apify oder Web-Search). Branchenportal-typische NAP-Felder:

- Jameda: Praxis-Adresse + Telefon im Profil-Header
- ProvenExpert: Anbieter-Block mit Adresse
- wlw.de: Firmen-Stammdaten
- ImmoScout24: Maklerprofil-Adresse

Optional — wenn `wettbewerber/portale.md` nicht existiert oder Akteur dort keinen Eintrag hat, wird die Quelle übersprungen.

### NAP-Normalisierung

```python
def normalize_phone(s):
    # alle Whitespaces, Bindestriche, Klammern, Slashes raus
    digits = re.sub(r'[\s\-/()]', '', s)
    # +49 zu 0 normalisieren
    if digits.startswith('+49'):
        digits = '0' + digits[3:]
    if digits.startswith('0049'):
        digits = '0' + digits[4:]
    return digits

def normalize_address(s):
    # Lowercase
    s = s.lower()
    # Umlaut-Mapping
    s = s.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    # Abkürzungs-Mapping
    s = re.sub(r'\bstr\.?\b', 'strasse', s)
    s = re.sub(r'\bweg\.?\b', 'weg', s)
    s = re.sub(r'\bpl\.?\b', 'platz', s)
    # Whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def normalize_name(s):
    s = s.lower().strip()
    # Rechtsform-Varianten lokal egalisieren
    s = re.sub(r'\bg\.?\s*m\.?\s*b\.?\s*h\.?\b', 'gmbh', s)
    s = re.sub(r'\bag\b', 'ag', s)
    # Whitespace normalisieren
    s = re.sub(r'\s+', ' ', s)
    return s
```

Vergleich pro Feld:

- **Match**: normalisierte Strings identisch
- **Soft-Diff**: > 90% Ähnlichkeit (Levenshtein), z. B. bei Tippfehlern
- **Hard-Diff**: < 90% Ähnlichkeit oder fehlend in einer Quelle

Auffälligkeit `nap_inkonsistenz` wenn ≥ 1 Hard-Diff zwischen ≥ 2 Quellen für denselben Akteur.

## 4. Apify-Credit-Strategie

Pro typischem Lauf (Kunde + 5 WBs, 1 Standort, 12 Local-Pack-Keywords):

| Tätigkeit | Calls | Apify-Compute-Units (CU) |
|---|---|---|
| GMB-Profil-Scrape × 6 Akteure | 6 | ~6 CU |
| GMB-Reviews × 6 Akteure (Sample 50) | 6 (in GMB-Call enthalten) | ~12 CU |
| Local-Pack-Queries 12 × 1 Standort | 12 | ~6 CU |
| Website-Impressum-Crawl × 6 Akteure | 6 (max 5 Pages each) | ~3 CU |
| **Summe pro Lauf** | ~30 | **~27 CU** |

Bei großen Läufen (10 WBs, 3 Standorte, 30 Keywords): linear hochrechnen, vorab-Warnung im Schema-Body wenn > 100 CU erwartet.

## 5. Reduced-Modi

| Bedingung | Reduced-Modus |
|---|---|
| Apify-Quota fast ausgeschöpft | Reviews nur Top-20, kein Sentiment-Sub-Themen-Match |
| Local-Falcon nicht verfügbar, Apify-Pack-Scraper nicht zuverlässig | Nur Top-3-Local-Pack per Web-Search (Reduced-Tiefe) |
| Branchenportale nicht vorhanden | NAP-Check nur GMB-vs-Website, Hinweis im Body |
| Wenige Reviews insgesamt (< 10 pro Akteur) | Sentiment-Sub-Themen-Match wird auf reines Vorkommens-Counting reduziert, keine Score-Aggregation |
| Service-Area-Business ohne Adresse | NAP-Check nur Name + Telefon, keine Adress-Validierung |

Jeder Reduced-Modus wird im Markdown- und HTML-Output explizit dokumentiert, damit der Stratege im Kunden-Gespräch korrekt einordnen kann.

## 6. Bekannte Limits

- **Apify GMB-Scraper liefert keine Insights**: Anzahl Profil-Aufrufe, Wegbeschreibungen-Klicks, Anrufe — diese Daten sind Inhaber-only und nicht öffentlich scrapbar. Wenn der Kunde GMB-Insights teilt: separater Skill oder manueller Block im Output.
- **Reviews-Sample ist nicht repräsentativ bei aktiver Reviews-Filterung**: GMB filtert Spam/Fake-Reviews automatisch — manche kritische Reviews fehlen. Hinweis im Body.
- **Local-Pack-Personalisierung**: Google personalisiert Local Pack nach Such-Historie und Location. Apify-Scraper liefert "unsearched" Local Pack — das ist der gleiche Ausgangspunkt, kann aber von realen Nutzern abweichen.
- **Branchenportal-Anti-Bot**: Jameda, ProvenExpert haben aktive Anti-Bot-Maßnahmen — Puppeteer-Custom-Scrape kann nötig werden. Bei wiederholtem Fehlschlag: manuelle NAP-Erfassung als Fallback.
