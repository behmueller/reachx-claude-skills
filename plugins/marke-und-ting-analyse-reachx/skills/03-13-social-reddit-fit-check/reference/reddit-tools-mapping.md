# Reddit-Tools-Mapping

Welcher Apify-Actor fuer welchen Schritt, Subreddit-Such-Heuristik, Sprache-Erkennung, Moderations-Strenge-Heuristik, Sentiment-Klassifikations-Regeln, Tonalitaets-Klassifikation. Pflege diese Datei, wenn ein Actor abgekuendigt wird oder ein neuer dazu kommt.

**Stand:** Mai 2026

## Getestete Actor-IDs

Vor dem Lauf immer den Health-Check (Limit-1-Aufruf mit einem bekannten Subreddit) durchführen; bei Fehler Alternativen aus der Liste probieren.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `apify/reddit-scraper` | Reddit Scraper (official) | noch nicht getestet | unbekannt | Erste Wahl — Subreddit-Crawl, Posts, Kommentare |
| `apify/reddit-search-scraper` | Reddit Search Scraper | noch nicht getestet | unbekannt | Erste Wahl — Subreddit-Suche, Marken-Erwähnungen |
| `apify/reddit-comments-scraper` | Reddit Comments Scraper | noch nicht getestet | unbekannt | Optional — Thread-Tiefe |
| `apify/puppeteer-scraper` | Custom Puppeteer | — | fallback | Nur wenn kein spezialisierter Actor verfügbar |

**Login-Wall:** Reddit ist öffentlich ohne Login zugänglich. Keine Auth notwendig. Bei Session-Fehlern: Reconnect, dann Retry.

## Methoden-Glossar

| Methode | Wann nutzen |
|---|---|
| **A — Apify Reddit-Scraper** | Erste Wahl fuer Subreddit-Crawl, Post-Sample, Kommentare. Aktuell empfohlen: `apify/reddit-scraper` (Universal-Actor mit Subreddit-, Post- und Comment-Endpoints) |
| **B — Apify Reddit-Search-Scraper** | Spezialisiert auf Reddit-interne Suche (Subreddit-Suche per Keyword, Erwaehnungs-Suche per Markenname). Aktuell empfohlen: `apify/reddit-search-scraper` |
| **C — Apify Reddit-Comments-Scraper** | Optional fuer Thread-Tiefe, wenn ein einzelner Thread komplett gescraped werden soll (Top-Kommentare, verschachtelte Threads). Aktuell empfohlen: `apify/reddit-comments-scraper` (oder Funktion von Methode A) |
| **D — Reddit-API direkt** | **NICHT empfohlen.** Rate-limit-anfaellig, OAuth-Setup-Aufwand zu hoch fuer Skill-Reproduzierbarkeit. Apify-Actors abstrahieren das weg. Nur als allerletzter Notfall-Fallback. |

## Aufruf-Strategie pro Workflow-Schritt

### Schritt 3 — Subreddit-Inventar

Pro Keyword aus dem Such-Set (Schritt 2):

- **Primaer**: Methode B im Subreddit-Such-Modus
- **Input-Parameter**:
  - `searches`: `[KEYWORD]`
  - `searchType`: `subreddits` (oder vergleichbarer Modus-Selector je nach Actor-Version)
  - `maxItems`: 20 pro Keyword
  - `sortBy`: `relevance` (Default)
- **Output-Felder pro Subreddit**:
  - `name` (z. B. `Heimwerken`)
  - `url` (`https://www.reddit.com/r/Heimwerken/`)
  - `subscribers` oder `members` (Mitglieder-Anzahl)
  - `publicDescription` oder `description` (Sidebar-Text, gekuerzt 300 Zeichen)
  - `over18` (NSFW-Flag)
  - `lang` (wenn vom Actor geliefert)
  - `createdAt` / `created_utc`

**Posts-pro-Tag berechnen** (Actor liefert das nicht direkt):

- Subreddit-Stream-Abruf: Methode A mit `subredditUrl: URL`, `sort: new`, `maxItems: 100`
- Aus den 100 neuesten Posts: `taken_at_iso` extrahieren, Zeitspanne berechnen, `posts_pro_tag = 100 / (max_date - min_date in Tagen)`
- Wenn weniger als 100 Posts ueberhaupt: `posts_pro_tag = posts_anzahl / (heute - aeltester_post)`

**Subreddit-Filter (Skip-Bedingungen):**

- `subscribers < 1000` → raus
- `posts_pro_tag < 0.5` → raus (Subreddit zu inaktiv)
- `over18 == true` → raus (NSFW out-of-scope)

### Schritt 5 — Marken-Erwaehnungen

- **Primaer**: Methode B im Erwaehnungs-Such-Modus
- **Input-Parameter pro Akteur**:
  - `searches`: `[MARKENNAME, MARKENNAME alternative, "domain.tld"]`
  - `searchType`: `posts_and_comments` (oder vergleichbar)
  - `sortBy`: `relevance` und parallel `new`
  - `time`: `month` (Apify-Default-Filter) — clientseitig auf 6 Monate filtern
  - `maxItems`: 50 pro Akteur
- **Output-Felder pro Treffer**:
  - `id` (thread- oder comment-ID)
  - `parsedId`, `parentId` (fuer Kommentar-zu-Post-Mapping)
  - `url` (Thread-URL)
  - `title` (nur bei Posts)
  - `body` oder `text` (Volltext)
  - `subreddit`
  - `author` oder `username`
  - `createdAt` / `created_utc`
  - `score` oder `ups`
  - `numberOfComments` (nur bei Posts)
  - `dataType`: `post | comment`

### Schritt 7 — Themen-Tiefe Top-Subreddits

- **Primaer**: Methode A im Subreddit-Modus
- **Input-Parameter**:
  - `subreddit_urls`: `[URL]`
  - `sort`: `top`
  - `time`: `month`
  - `maxItems`: 30
- **Optionaler Tiefen-Pass (nur bei Voll-Lauf)**: Methode C fuer die Top-5-Posts pro Subreddit, um die ersten 10 Kommentare zu erfassen → Pain-Point-Signal-Extraktion

### Mapping-Heuristik fuer Field-Namen

Beim Parsen des Actor-Outputs defensiv vorgehen — verschiedene Actor-Versionen verwenden unterschiedliche Feld-Namen:

```python
def get_subscribers(item):
    return (item.get("subscribers") 
            or item.get("members") 
            or item.get("subscriberCount") 
            or 0)

def get_score(item):
    return (item.get("score") 
            or item.get("ups") 
            or item.get("upvotes") 
            or 0)

def get_text(item):
    return (item.get("body") 
            or item.get("text") 
            or item.get("selftext") 
            or item.get("content") 
            or "")
```

## Subreddit-Such-Heuristik (Schritt 3 Erweiterung)

**Such-Keyword-Set erweitern** ueber die Branche hinaus:

1. **Branchenname direkt** (deutsch + englisch): "Maler", "painters"
2. **Portfolio-Hauptbegriffe** aus `data/kunde.md`: pro Begriff einzeln suchen
3. **Synonyme**: deutsche Branchen oft auch in englischen Subreddits diskutiert, z. B. `r/DIY` fuer Heimwerken
4. **Marken-Namen** als Such-Term (manche Marken haben eigene Subreddits, z. B. `r/Tesla`, `r/notion`)
5. **Adjacent-Themen**: B2B-Branche → `r/sysadmin` / `r/devops` / `r/cscareerquestions` etc. — `reference/branchen-adjacencies.md` ggf. erweitern

**Relevanz-Score-Berechnung** (0-1):

```
relevanz_score = (
    0.4 * keyword_match_quality        # exakt im Namen / Description?
    + 0.3 * log10(subscribers / 1000)   # Mitglieder-Skalierung
    + 0.2 * min(posts_pro_tag / 10, 1)  # Aktivitaets-Faktor
    + 0.1 * sprach_match                # passt zur Kundensprache?
)
```

Cap bei 1.0. Top-10 nach diesem Score in den Voll-Lauf.

## Sprache-Erkennung (Subreddit)

Heuristik pro Subreddit:

1. **Sidebar-Description**: erste 200 Zeichen tokenisieren, dominante Sprache via Stopword-Match (de-Stopwords vs. en-Stopwords). 
2. **Top-10-Post-Titel**: gleiches Vorgehen.
3. **Entscheidung**:
   - `de` wenn beide >70% deutsch
   - `en` wenn beide >70% englisch
   - `mixed` wenn beide in 30-70% Range
   - `unbekannt` wenn weniger als 5 Tokens insgesamt

Optional: kleines Sprache-ID-Lib wie `langdetect` falls verfuegbar (zuverlaessiger als Stopword-Heuristik).

## Moderations-Strenge-Heuristik

Aus Sidebar-Regeln + Description abgeleitet (3 Stufen, plus `unbekannt`):

| Stufe | Signal |
|---|---|
| `streng` | (a) >=5 explizite Regeln in der Sidebar, ODER (b) explizite Regel "No self-promotion / No advertising / No marketing", ODER (c) Wiki-Link zu detaillierter Moderation-Policy |
| `mittel` | 2-4 Regeln, keine explizite Anti-Werbung-Regel, aber generelle Quality-Guidelines |
| `locker` | 0-1 Regeln in der Sidebar, Description ohne Verhaltens-Codex |
| `unbekannt` | Sidebar-Description leer oder Apify konnte Regeln nicht extrahieren |

Apify-Output: manche Actors liefern `rules` als strukturiertes Array (`name`, `description`), manche nicht. Wenn nicht: aus Sidebar-Text per Regex Pattern wie `^\d+\.\s` extrahieren.

## Tonalitaets-Klassifikation (Subreddit, 4 Stufen)

Pro Top-Subreddit aus den 30 Top-Posts + ersten 30 Kommentaren in Top-3-Posts abgeleitet:

| Stufe | Indikatoren |
|---|---|
| `snarky` | Sarkasmus-Marker (lol, smh, /s, kek), Meme-Posts >30% Anteil, viel Anti-Establishment-Sprache, "shitpost"-Pattern |
| `ernsthaft` | Lange Posts (>500 Zeichen Body), Fach-Vokabular, kaum Memes, Top-Kommentare mit Quellen/Links, AMA-Pattern haeufig |
| `hilfsbereit` | Viele Frage-Antwort-Pattern ("How do I...", "Hat jemand schon mal..."), hohe Antwort-Quote, gute Top-Kommentar-Score-Verteilung |
| `kommerz_allergisch` | Sidebar enthaelt explizite Anti-Werbung-Regel, regelmaessig Posts vom Typ "PSA: don't fall for [BRAND]'s marketing", Marken-Mentions ueberwiegend negativ |

Mehrere Tonalitaeten koennen sich ueberlappen (z. B. snarky + kommerz_allergisch ist typisch). Im Output das dominante Pattern + ggf. Sekundaer-Pattern dokumentieren.

## Sentiment-Klassifikation

**Wichtig: reproduzierbare Kriterien, nicht reine LLM-Bauchgefuehl-Skala.**

Drei Signale werden kombiniert:

### Signal 1 — Lexikon

Positive Marker (deutsch + englisch):

```
recommend, recommended, empfehle, empfehlen, empfehlung,
love, great, klasse, top, super, perfect, perfekt,
best, beste, awesome, amazing, fantastic, excellent,
solved my problem, hat geholfen, hilfreich,
worth it, lohnt sich, gerne wieder
```

Negative Marker:

```
scam, ripoff, betrug, abzocke,
shit, schrott, garbage, muell, mist,
avoid, finger weg, vermeiden,
disappointed, enttaeuscht, schlecht, terrible, awful,
waste of money, rausgeworfenes geld,
broken, kaputt, doesnt work, funktioniert nicht,
worst, schlimmste, never again, nie wieder
```

**Match-Logik**: Token-Match mit Wort-Grenzen (case-insensitive), keine Substring-Matches (sonst matched "recommend" auf "recommended" doppelt).

### Signal 2 — Score

- `score >= 10` UND mind. 1 pos Marker → starkes pos Signal
- `score >= 5` UND mind. 1 pos Marker → mittleres pos Signal
- `score <= -3` UND mind. 1 neg Marker → starkes neg Signal
- `score <= 0` UND mind. 1 neg Marker → mittleres neg Signal
- `score` allein ohne Lexikon-Match → kein Signal

### Signal 3 — LLM-Kontext-Pass

Nur wenn Signal 1 + Signal 2 unklar oder widerspruechlich.

LLM-Prompt-Template (reproduzierbar, mit definierten Kategorien):

```
Klassifiziere den folgenden Reddit-Auszug zu der Marke "MARKENNAME" 
in genau EINE Kategorie:

A) Empfehlung/Lob — Autor empfiehlt aktiv, lobt explizit, positive Erfahrung
B) Beschwerde/Warnung — Autor warnt, schimpft, negative Erfahrung
C) Neutrale Nennung — sachliche Erwaehnung ohne Wertung (Vergleich, Aufzaehlung, Frage)
D) Gemischt — sowohl positive als auch negative Aspekte explizit benannt
E) Unklar — Auszug ist zu kurz/mehrdeutig, Wertung nicht erkennbar

Auszug:
"AUSZUG_TEXT"

Antwort nur als Buchstabe (A/B/C/D/E) plus Konfidenz hoch/mittel/niedrig.
Beispiel: "A hoch" oder "C niedrig"
```

### Aggregation zu finaler Klassifikation

| Signal-Kombination | Resultat |
|---|---|
| Lexikon stark pos + Score-Signal pos | `positiv`, Konfidenz hoch |
| Lexikon mittel pos + Score-Signal pos ODER LLM=A hoch | `positiv`, Konfidenz mittel |
| Lexikon stark neg + Score-Signal neg | `negativ`, Konfidenz hoch |
| Lexikon mittel neg + Score-Signal neg ODER LLM=B hoch | `negativ`, Konfidenz mittel |
| Beide Lexikon-Seiten ODER LLM=D | `gemischt` |
| Kein Lexikon-Match, Score neutral, LLM=C | `neutral` |
| LLM=E ODER alle Signale schwach | `unklar` |

`sentiment_konfidenz` pro Erwaehnung: `hoch | mittel | niedrig` — wird in `audits/reddit-erwaehnungen.csv` ausgewiesen, damit der Stratege die Verlaesslichkeit pro Eintrag pruefen kann.

## Bot-Detection (Edge Case)

Bot-Accounts markieren mit `vermutlich_bot: true`, nicht in Sentiment-Aggregate einbezogen:

- `author` in einer bekannten Bot-Liste (z. B. `AutoModerator`, `RemindMeBot`, `WikiTextBot`)
- `author_karma < 10` UND `author_alter_tage < 30` (neuer Low-Karma-Account)
- Erwaehnungs-Text matched bekanntes Bot-Template-Pattern (z. B. "Beep boop", "I am a bot", "Dieser Beitrag wurde automatisch generiert")

Bot-Liste pflegen in diesem File, Sektion oben erweitern.

## Aufruf-Reihenfolge & Caching

1. Schritt 2 (Keyword-Set) → klein, ohne API
2. Schritt 3 (Subreddit-Inventar) → Methode B pro Keyword, ggf. Methode A fuer Posts-pro-Tag
3. Schritt 5 (Erwaehnungen) → Methode B pro Akteur
4. Schritt 7 (Themen-Tiefe) → Methode A pro Top-Subreddit, optional Methode C fuer Top-Threads

**Caching-Konvention:**

- Alle Roh-Resultate im lokalen Arbeits-Cache `~/.cache/reachx-mta/<slug>/raw/` ablegen, **unveraendert** vom Actor (kein Re-Mapping vor dem Cache). Am Skill-Ende werden alle Files gzip-komprimiert nach Drive `assets/raw/` hochgeladen.
- Lokale Cache-Pfade:
  - `~/.cache/reachx-mta/<slug>/raw/reddit-such-keywords.json` (Schritt 2)
  - `~/.cache/reachx-mta/<slug>/raw/reddit-subreddits.json` (Schritt 3)
  - `~/.cache/reachx-mta/<slug>/raw/reddit-erwaehnungen-AKTEURSSLUG.json` (Schritt 5 pro Akteur)
  - `~/.cache/reachx-mta/<slug>/raw/reddit-themen-SUBREDDITSLUG.json` (Schritt 7 pro Subreddit)
- Bei erneutem Lauf: Cache nicht automatisch wiederverwenden (Reddit-Daten veralten), aber im Skill-Output Datenstand pro Achse dokumentieren.

## Fehler-Handling

| Fehler | Verhalten |
|---|---|
| Apify-Token fehlt | Skill bricht ab mit klarer Fehlermeldung "APIFY_TOKEN fehlt oder MCP-Apify-Server nicht verfuegbar" |
| Methode B liefert 0 Treffer pro Keyword | Such-Variante probieren (mit/ohne Bindestrich, mit Anfuehrungszeichen). Wenn nach 3 Varianten immer noch 0 → Keyword als `null_match` markieren, weiter |
| Rate-Limit (HTTP 429) | Single Retry nach 30s, dann Skip dieses Actors mit Hinweis, Auffaelligkeit `apify_rate_limit` |
| Subreddit privat | `subreddit_unzugaenglich: true`, im CSV ausweisen, keine Themen-Tiefe |
| Cross-Posts (gleicher Thread in mehreren Subreddits) | Als separate Erwaehnung pro Subreddit fuehren, fuer Top-5-Liste deduplizieren ueber `thread_id` |

## Zu pflegende Felder

Diese Datei muss aktualisiert werden, wenn:

- Ein Apify-Actor abgekuendigt wird oder ein besserer dazu kommt → Methoden-Glossar
- Lexikon-Marker erweitert werden (neue Slang-Begriffe etc.) → Sentiment-Klassifikation
- Neue Bot-Patterns auftauchen → Bot-Detection
- Sprache-Erkennung verbessert wird (z. B. echtes Lib statt Stopword) → Sprache-Erkennung
