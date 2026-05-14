# Backend-Konfiguration: Bright Data + Apify (Hybrid)

Konkrete API-Aufrufe und Schemas fuer die beiden Backends. Lies den passenden Abschnitt vor dem ersten Backend-Aufruf, sonst raetselst du an Endpoints und Output-Formaten.

## Zugriffs-Wege: MCP-Connector vs. HTTP-API

Pro Backend gibt es zwei Wege, mit denen Claude die Daten holen kann:

1. **MCP-Connector** (bevorzugt, falls verbunden): Tools werden als native Claude-Tools angeboten, Auth laeuft ueber OAuth. Anbieter wie Apify und Bright Data haben offizielle MCP-Server.
2. **Direkte HTTP-API** (Fallback): Claude ruft `requests.post(...)` ueber Bash-Tool mit Token aus Env Vars.

**Vor jedem ersten Backend-Aufruf:** Discovery durchfuehren - schauen, welche Tools mit Prefix `mcp__Apify__*` oder `mcp__BrightData__*` (Naming variiert je Installation) im Inventar liegen.

**Entscheidungs-Logik pro Backend:**

```
1. Connector verfuegbar (Tool im Inventar) -> Connector nutzen
2. Sonst Env-Token gesetzt -> HTTP-API (siehe Sektionen weiter unten)
3. Sonst -> User-Hinweis, was eingerichtet werden muss
```

## Apify-Connector (Tool-Pattern)

Der offizielle Apify-MCP-Server exponiert typischerweise Tools wie:

- `call-actor` / `mcp__Apify__call-actor` - startet einen Actor mit gegebenem Input
- `get-actor-output` / `get-dataset-items` - holt das Resultat
- `search-actors` - findet passende Actors per Keyword

**Aufruf-Pattern fuer Schritt 6 (Mitarbeiter-Listing):**

```
1. (optional) search-actors mit "linkedin company employees" - Actor-ID finden
2. call-actor mit:
   - actor_id: "harvestapi/linkedin-profile-search" (oder gefundene ID)
   - run_input: {
       "currentCompanies": ["https://www.linkedin.com/company/example/"],
       "maxItems": 200,
       "profileScraperMode": "Short"
     }
3. get-actor-output mit der zurueckgegebenen run_id / dataset_id
```

Die genauen Tool-Namen koennen je nach Connector-Version variieren - nutze die Namen aus dem aktuellen Tool-Inventar, nicht hardcoded.

## Bright Data Connector (Tool-Pattern)

Der Bright Data MCP-Server exponiert typischerweise Tools wie:

- `web-data-linkedin-company-profile` - Company-Daten zu URL
- `web-data-linkedin-people-profile` - Profil-Daten zu URL
- `web-data-linkedin-posts` - Posts zu Company-URL oder Profil-URL
- `scrape-as-markdown` / `scrape-as-html` - Web Unlocker Fallback

Das exakte Set haengt vom Connector ab - beim ersten Lauf schauen, was angeboten wird.

**Aufruf-Pattern Schritt 5 (Company):**

```
web-data-linkedin-company-profile mit url: "https://www.linkedin.com/company/example/"
```

**Aufruf-Pattern Schritt 9 (Deep-Profile):**

```
web-data-linkedin-people-profile mit url: "https://www.linkedin.com/in/profile-slug/"
```

**Aufruf-Pattern Schritt 10/11 (Posts):**

```
web-data-linkedin-posts mit url: COMPANY_URL oder PROFILE_URL,
optional start_date / end_date
```

## Wann der Connector NICHT genuegt

Falls der Connector ein Tool nicht exponiert, das du fuer deinen Workflow brauchst (z. B. ein spezifischer Actor, der nur per direkter API aufrufbar ist): Fallback auf HTTP-API fuer diesen einen Schritt. Beide Wege liefern in das gleiche Internal Schema.

---

## Backend-Auswahl pro Workflow-Schritt

Der Skill nutzt ein **Hybrid-Modell** - nicht ein Backend wins-it-all, sondern jeder Schritt geht zu dem Backend, das ihn am besten loest.

| Schritt | Backend | Begruendung |
|---|---|---|
| 5. Company Page | **Bright Data** | Stabiler, einheitliches Schema |
| 6. Mitarbeiter-Listing aus Company URL | **Apify** (zwingend) | Bright Data hat dafuer keinen Standard-Endpoint |
| 9. Deep-Profile-Scrape (per URL) | **Bright Data** | Sauberes Karriere-Historie-Schema |
| 10. Company-Posts | **Bright Data** | "Discover by company url" verfuegbar |
| 11. Personen-Posts | **Bright Data** | "Discover by profile url" verfuegbar |

**Schritt 6 ist der einzige, der zwingend Apify braucht.** Wenn nur Bright Data verfuegbar ist, kann der Skill nur eingeschraenkt laufen (kein Mitarbeiter-Listing -> keine Department-/Tenure-Statistik -> kein Smart-Sampling fuer Schritt 9).

## Voller Apify-Fallback

Wenn `BRIGHTDATA_*` nicht gesetzt sind, kann der Skill alternativ den **gesamten Workflow ueber Apify** fahren. Das ist aber Backup, nicht Default.

Erkennen ueber Environment Variables:

```
1. BRIGHTDATA_API_TOKEN + 3 Dataset-IDs gesetzt + APIFY_TOKEN gesetzt -> Hybrid (Default)
2. nur APIFY_TOKEN gesetzt -> voller Apify-Fallback (mit Hinweis an User)
3. nur BRIGHTDATA_* gesetzt -> Skill kann starten, ABER Schritt 6 wird uebersprungen
   und User wird gewarnt: keine Department-/Tenure-Statistik moeglich
4. weder noch -> User-Setup-Hinweis, kein Scrape starten
```

Bei jedem Backend-Fehler (nicht: leeres Ergebnis - das ist OK) einmal Retry nach 30 Sekunden, bei zweitem Fehler User informieren.

---

# Bright Data - HTTP-API (Fallback ohne Connector)

Wenn der Bright Data MCP-Connector NICHT verbunden ist, nutze direkte HTTP-API. Bright Data arbeitet mit einem **asynchronen Snapshot-Modell**:

1. Du triggerst einen Job per POST -> bekommst eine `snapshot_id` zurueck
2. Du pollst den Status, bis er auf `ready` steht (typisch 30 Sek. - wenige Minuten)
3. Du holst die Ergebnisse per GET ab

## Auth und Endpoints

Alle Calls nutzen den API-Token im Authorization-Header:

```
Authorization: Bearer BRIGHTDATA_API_TOKEN
Content-Type: application/json
```

Endpoints (Stand 2026, pruefe ggf. Bright Data Doku bei 404):

```
POST   https://api.brightdata.com/datasets/v3/trigger?dataset_id=DATASET_ID
GET    https://api.brightdata.com/datasets/v3/progress/SNAPSHOT_ID
GET    https://api.brightdata.com/datasets/v3/snapshot/SNAPSHOT_ID?format=json
```

## Workflow-Pattern (Pseudo-Code)

```python
import requests, time, os

API = "https://api.brightdata.com/datasets/v3"
HEADERS = {"Authorization": f"Bearer {os.environ['BRIGHTDATA_API_TOKEN']}",
           "Content-Type": "application/json"}

def trigger_and_wait(dataset_id, payload, max_wait_seconds=600):
    # 1) Trigger
    r = requests.post(f"{API}/trigger?dataset_id={dataset_id}",
                      json=payload, headers=HEADERS)
    r.raise_for_status()
    snapshot_id = r.json()["snapshot_id"]

    # 2) Poll
    elapsed = 0
    while elapsed < max_wait_seconds:
        time.sleep(20)
        elapsed += 20
        s = requests.get(f"{API}/progress/{snapshot_id}", headers=HEADERS).json()
        if s.get("status") == "ready":
            break
        if s.get("status") == "failed":
            raise RuntimeError(f"Snapshot failed: {s}")
    else:
        raise TimeoutError(f"Snapshot {snapshot_id} not ready after {max_wait_seconds}s")

    # 3) Fetch
    r = requests.get(f"{API}/snapshot/{snapshot_id}?format=json", headers=HEADERS)
    r.raise_for_status()
    return r.json()
```

## Bright Data - Company API (Schritt 5)

**Dataset:** `BRIGHTDATA_DATASET_COMPANY` (Dataset "LinkedIn Company Information")

**Trigger-Payload:**

```json
[
  {"url": "https://www.linkedin.com/company/example-company/"}
]
```

**Erwartete Output-Felder (typisch):**

```
id, name, slogan, description, website, country_code, industry,
company_size, organization_type, locations, founded,
followers, employees_in_linkedin, specialties
```

Speichere im MTA-Modus lokal als `~/.cache/reachx-mta/<slug>/raw/linkedin-company-SLUG.json` (am Skill-Ende gzip-komprimiert nach Drive `assets/raw/`), im Standalone-Modus als `output/SLUG/company.json` im lokalen Filesystem. Vermerke `followers` fuer die spaetere Engagement-Rate-Berechnung.

## Bright Data - People Profiles API (Schritt 9: Deep-Scrape)

**Dataset:** `BRIGHTDATA_DATASET_PEOPLE` (Dataset "LinkedIn People Profiles")

Im Endpoint-Picker als **"Collect by URL"** aufgelistet. Nimmt eine Liste von Profil-URLs und gibt vollstaendige Profile zurueck.

**Trigger-Payload:**

```json
[
  {"url": "https://www.linkedin.com/in/profile-slug-1/"},
  {"url": "https://www.linkedin.com/in/profile-slug-2/"}
]
```

**Erwartete Output-Felder (Deep-Tier):**

```
name, url, position, current_company, current_company_name,
city, country_code, about,
experience: [
  {title, company, start_date, end_date, duration, description, location}
],
education: [...], certifications: [...], languages: [...],
followers, connections
```

Speichere im MTA-Modus die Deep-Daten in der `linkedin-employees.csv` (Department-Bucket plus Tenure-Spalten, auf Drive) sowie Roh-JSON lokal in `~/.cache/reachx-mta/<slug>/raw/linkedin-employees-SLUG.json` (am Skill-Ende gzip-komprimiert nach Drive `assets/raw/`).

**Wichtig:** Diese API liefert KEINE Mitarbeiter-Listings aus einer Company-URL - nur Profile zu konkreten Profil-URLs. Fuer Schritt 6 (Listing) brauchst du Apify.

## Bright Data - Posts API (Schritt 10: Company-Posts)

**Dataset:** `BRIGHTDATA_DATASET_POSTS` (Dataset "LinkedIn Posts")

Im Endpoint-Picker als **"Discover by company url"** aufgelistet. Nimmt eine Company-URL und gibt deren Posts zurueck.

**Trigger-Payload (mit Datums-Filter fuer 12 Monate):**

```json
[
  {"url": "https://www.linkedin.com/company/example-company/",
   "start_date": "2025-05-09",
   "end_date": "2026-05-09"}
]
```

**Erwartete Output-Felder:**

```
post_id, url, post_text, date_posted, hashtags, embedded_links,
images, videos, post_type, account_type,
num_likes, num_comments, num_reposts (manchmal num_shares),
top_visible_comments
```

Speichere im MTA-Modus die Daten in `linkedin-posts.csv` (Author-Type `company`, auf Drive), Roh-JSON lokal in `~/.cache/reachx-mta/<slug>/raw/linkedin-posts-SLUG.json` (am Skill-Ende gzip-komprimiert nach Drive `assets/raw/`).

## Bright Data - Posts API (Schritt 11: Personen-Posts)

Gleicher Dataset, aber Endpoint **"Discover by profile url"**:

**Trigger-Payload:**

```json
[
  {"url": "https://www.linkedin.com/in/person-slug-1/",
   "start_date": "2025-05-09",
   "end_date": "2026-05-09"},
  {"url": "https://www.linkedin.com/in/person-slug-2/",
   "start_date": "2025-05-09",
   "end_date": "2026-05-09"}
]
```

Output-Format identisch zu Company-Posts. Im MTA-Modus in `linkedin-posts.csv` mit Author-Type `person`. Im Standalone-Modus als `output/SLUG/people_posts.csv`.

## Bright-Data-Eigenheiten

- **Async-Latenz**: Snapshots brauchen 30 Sek bis mehrere Minuten. Bei grossen Payloads (z. B. 10 Profile gleichzeitig) eher Richtung Minuten.
- **Leere Ergebnisse**: Status `ready` mit leerem Array = kein Fehler, sondern LinkedIn hatte nichts. Vermerke im Report ("0 Posts gefunden fuer Account X"), nicht abbrechen.
- **Records werden nur fuer erfolgreiche Lieferungen berechnet**. Failed-Snapshots kosten nichts.
- **Datums-Format**: Bright Data liefert Datums oft als Unix-Timestamp ODER ISO-String, je nach Endpoint. Bei der CSV-Generation auf einheitliches Format normalisieren (`YYYY-MM-DD`).
- **Engagement-Felder**: heissen mal `num_likes`/`num_comments`, mal `likes_count`/`comments_count` - beim Mappen beide pruefen.
- **Datums-Filter ehrlich kommunizieren**: Auch wenn du `start_date: 2025-05-09` setzt, liefert LinkedIn cookie-frei selten 12 Monate Posts zurueck. Realistisch sind 4-8 Wochen plus die paar Posts, die LinkedIn auf der Public-Page noch zeigt. Das ist kein Bright-Data-Problem, sondern LinkedIn-Limit.

---

# Apify - HTTP-API (Fallback ohne Connector)

Wenn der Apify MCP-Connector NICHT verbunden ist, nutze direkte HTTP-API. Apify nutzt das **Actor-Modell**: jeder Actor ist ein eigener Scraper mit eigenem Input-Schema und Output-Format.

## Auth und Endpoints

```
Authorization: Bearer APIFY_TOKEN

POST https://api.apify.com/v2/acts/ACTOR_ID/runs?token=APIFY_TOKEN
GET  https://api.apify.com/v2/actor-runs/RUN_ID
GET  https://api.apify.com/v2/datasets/DATASET_ID/items
```

ACTOR_ID kann der Slug-Pfad sein (z. B. `harvestapi/linkedin-profile-search`) - Apify ersetzt den Slash mit `~` in URLs (`harvestapi~linkedin-profile-search`).

## Apify - Mitarbeiter-Listing aus Company URL (Schritt 6, der zwingende Apify-Schritt)

**Empfohlene Actors (Stand 2026, cookie-frei):**

| Actor | Vorteil | Caveat |
|---|---|---|
| `harvestapi/linkedin-profile-search` | Filterbar nach `currentCompany`, gute Erfolgsrate | URL-basiertes Input-Schema |
| `harvestapi/linkedin-company-employees` | Direkt-Endpoint fuer Company -> Employees | Verfuegbarkeit pruefen |
| `apimaestro/linkedin-employees-no-cookies` | No-Cookie, schnell | Felder-Tiefe variabel |

**Beim ersten Lauf:** Kurz checken, welcher Actor gerade verfuegbar ist. Schreibe den gewaehlten Actor-Slug in `APIFY_ACTOR_EMPLOYEES` als Environment Variable, statt ihn im Skill zu hardcoden.

**Beispiel-Trigger fuer `harvestapi/linkedin-profile-search`:**

```json
{
  "currentCompanies": ["https://www.linkedin.com/company/example-company/"],
  "maxItems": 200,
  "profileScraperMode": "Short"
}
```

Die genauen Input-Felder unterscheiden sich pro Actor - **lies das jeweilige README** auf der Actor-Seite, bevor du Payload-Annahmen triffst.

**Erwartete Output-Felder (typisch):**

```
firstName, lastName, fullName, publicIdentifier, profileUrl,
headline, location, currentPosition, currentCompany,
profileImageUrl
```

Bei Mapping in unser Internal-Schema:

```python
employee = {
    "name": item.get("fullName") or f"{item.get('firstName')} {item.get('lastName')}",
    "profile_url": item.get("profileUrl") or item.get("publicProfileUrl"),
    "headline": item.get("headline"),
    "current_position": item.get("currentPosition") or item.get("title"),
    "current_company": item.get("currentCompany") or item.get("companyName"),
    "location": item.get("location") or item.get("locationName"),
}
```

## Apify - Optionale Fallbacks fuer andere Schritte

Diese Actors brauchst du nur, wenn Bright Data ausfaellt oder du den vollen Apify-Modus faehrst:

| Aufgabe | Empfohlener Actor |
|---|---|
| Company Page (Fallback) | `harvestapi/linkedin-company-scraper` |
| Deep Profile (Fallback) | `data-slayer/linkedin-profile-scraper` |
| Posts (Fallback) | `apimaestro/linkedin-posts-search-scraper-no-cookies` |

Konfigurierbar ueber zusaetzliche Env Vars:

```
APIFY_ACTOR_COMPANY=...
APIFY_ACTOR_DEEP_PROFILE=...
APIFY_ACTOR_POSTS=...
```

## Workflow-Pattern (Pseudo-Code)

```python
import requests, time, os

APIFY_TOKEN = os.environ["APIFY_TOKEN"]

def run_actor(actor_id, run_input, max_wait_seconds=600):
    actor_id_url = actor_id.replace("/", "~")

    # 1) Start
    r = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id_url}/runs",
        params={"token": APIFY_TOKEN}, json=run_input)
    r.raise_for_status()
    run = r.json()["data"]
    run_id = run["id"]
    dataset_id = run["defaultDatasetId"]

    # 2) Poll
    elapsed = 0
    while elapsed < max_wait_seconds:
        time.sleep(15)
        elapsed += 15
        s = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            params={"token": APIFY_TOKEN}).json()["data"]
        if s["status"] == "SUCCEEDED":
            break
        if s["status"] in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run failed: {s['status']}")
    else:
        raise TimeoutError(f"Apify run not ready after {max_wait_seconds}s")

    # 3) Fetch
    r = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={"token": APIFY_TOKEN, "format": "json"})
    r.raise_for_status()
    return r.json()
```

## Apify-spezifische Caveats

- **Output-Schemas variieren je Actor**: Mapping ins Internal-Schema (siehe unten) muss pro Actor angepasst werden.
- **Manche Actors haben eigene Rate-Limits**: Beim parallelen Triggern fuer mehrere Wettbewerber sequentiell laufen.
- **Pay-per-result**: Failed Records werden bei den meisten Actors nicht berechnet, aber pruefe pro Actor (steht im README).

---

# Schema-Normalisierung

Egal welches Backend in welchem Schritt: **wir normalisieren auf ein einheitliches Internal-Schema**, bevor wir CSVs schreiben oder den Rating-Skill aufrufen. Das haelt den Rest des Workflows backend-agnostisch.

## Internal Schema - Person (Listing aus Schritt 6)

```python
{
    "name": str,
    "profile_url": str,                   # https://www.linkedin.com/in/...
    "headline": str,
    "current_position": str,
    "current_company": str,
    "location": str,
    "department_inferred": str,           # ergaenzt durch unsere Klassifizierung
    "years_at_company": float | None      # ergaenzt aus Deep-Scrape, falls vorhanden
}
```

## Internal Schema - Person (Deep aus Schritt 9)

```python
{
    # ... Listing-Felder ...
    "experience": [
        {"title": str, "company": str, "start_date": "YYYY-MM" | None,
         "end_date": "YYYY-MM" | None, "is_current": bool,
         "duration_months": int | None}
    ],
    "education": list,
    "skills": list,
    "current_position_start_date": "YYYY-MM" | None,
    "tenure_months": int | None           # berechnet
}
```

## Internal Schema - Post (Schritt 10/11)

```python
{
    "post_url": str,
    "post_date": "YYYY-MM-DD",            # normalisiert
    "format": str,                         # text|image|carousel|video|document|article|poll|repost
    "text": str,                           # voller Body, nicht nur Headline
    "likes": int,
    "reposts": int,
    "comments": int,
    "reactions_breakdown": dict | None,   # {love: 5, insightful: 3, ...}
    "author_name": str,
    "author_url": str,
    "author_type": str,                    # company|person
    "media_urls": list,
    "hashtags": list,
    "is_repost": bool,
    "raw_backend_data": dict               # fuer Debugging, nicht in CSV
}
```

Halte dich an diese Schemas, dann ist der Rest des Skills backend-agnostisch.

## Konfigurations-Beispiel (Env Vars)

```bash
# Bright Data
export BRIGHTDATA_API_TOKEN="dein_token_hier"
export BRIGHTDATA_DATASET_COMPANY="gd_..."
export BRIGHTDATA_DATASET_PEOPLE="gd_..."
export BRIGHTDATA_DATASET_POSTS="gd_..."

# Apify
export APIFY_TOKEN="apify_api_..."
export APIFY_ACTOR_EMPLOYEES="harvestapi/linkedin-profile-search"

# Optional Fallbacks
export APIFY_ACTOR_COMPANY="harvestapi/linkedin-company-scraper"
export APIFY_ACTOR_DEEP_PROFILE="data-slayer/linkedin-profile-scraper"
export APIFY_ACTOR_POSTS="apimaestro/linkedin-posts-search-scraper-no-cookies"
```
