# Pinterest-Tools-Mapping

Apify-Actor-Optionen, URL-Patterns, Datenfelder-Mapping und Fallback-Kaskade für `03-10-social-pinterest`.

**Stand:** Mai 2026 - initial. Bei Actor-Wechsel oder Pinterest-UI-Änderungen aktualisieren.

## Datenquellen-Übersicht

Pinterest bietet keine öffentliche API für die Drittanbieter-Nutzung in der hier benötigten Tiefe. Web-Scraping via Apify ist Standard. Login ist bei öffentlichen Profilen meist nicht nötig, kann aber bei großen Profilen oder häufigen Requests von Pinterest gedrosselt werden.

## Apify-Actors

### Primär-Actor

**`apify/pinterest-scraper`** (oder `epctex/pinterest-scraper`)

| Parameter | Wert |
|---|---|
| Input-Typ | Pinterest-Profil-URL oder Username |
| Output | Profil-Stamm, Boards-Liste, Pins-Liste |
| Geschwindigkeit | ca. 1-2 Minuten pro mittelgroßes Profil |
| Limit | Hard-Cap 40 Pins setzen, Boards-Cap 50 |

**Erwartete Roh-Felder vom Actor:**

```
profile:
  username
  display_name
  bio
  followers_count
  following_count
  pin_count
  board_count
  is_verified
  is_business
  website
  account_type
  region

boards:
  - id
    name
    slug
    description
    pin_count
    follower_count
    last_pin_at
    url

pins:
  - id
    title
    description
    url
    image_url
    type             # standard, video, idea, product, story
    created_at
    save_count       # bei Pinterest oft als "saves" oder "reactions"
    comment_count
    domain           # Quelldomain
    link             # Landingpage-URL
    board_id
    board_name
    hashtags         # falls vom Actor extrahiert
    tags
```

Mapping zu Skill-Schema:

| Actor-Feld | Skill-Feld | Hinweis |
|---|---|---|
| `profile.username` | `pinterest_username` | Lowercase, ohne `/` |
| `profile.followers_count` | `follower_count` | int |
| `profile.is_business` | `business_account` | bool |
| `boards[].pin_count` | `pin_anzahl` | int |
| `pins[].type` | `pin_typ` | mapping siehe unten |
| `pins[].save_count` | `saves_count` | int oder null |

**Pin-Typ-Mapping** (Actor liefert verschiedene Strings):

| Actor-Wert | Skill-Wert |
|---|---|
| `standard`, `regular`, `image` | `standard` |
| `video`, `video_pin` | `video` |
| `story`, `idea`, `idea_pin` | `idea` |
| `product`, `product_pin`, `shop` | `product` |
| Sonstige | `unbekannt` |

### Fallback-Actor

**`apify/puppeteer-scraper`** mit Custom-Page-Function

Wenn der primäre Pinterest-Scraper ausfällt oder UI-Änderungen die Felder verändert haben:

- Page-Function navigiert `https://www.pinterest.com/USERNAME/` und liest sichtbare Werte aus dem DOM
- Boards-Liste via `https://www.pinterest.com/USERNAME/_saved/` oder ähnlichem Pfad
- Pins via Infinite-Scroll-Simulation mit Limit

Custom-Page-Function-Skelett (zum Anpassen):

```js
async ({ page, request }) => {
  await page.waitForSelector('[data-test-id="profile-header"]');
  const profile = await page.evaluate(() => {
    return {
      username: document.querySelector('[data-test-id="username"]')?.textContent,
      followers: document.querySelector('[data-test-id="follower-count"]')?.textContent,
      // ... weitere Selektoren
    };
  });
  // Boards und Pins via Scroll und JSON-Inspector
  return { profile, boards: [], pins: [] };
};
```

Custom-Selektoren sind volatil - bei Pinterest-UI-Änderung Skript anpassen. Dieser Pfad ist nur Notfall-Fallback.

### Search-Actor für Username-Auflösung

Wenn der Pinterest-Username nicht aus der Touchpoint-Inventur kommt:

**`apify/pinterest-search-scraper`** oder Web-Search

- Suchbegriff: vollständiger Akteurs-Name + ggf. Region
- Erwarteter Output: Top-Treffer aus Pinterest-Profil-Suche
- Match-Kriterien:
  - Display-Name matcht Akteurs-Name (fuzzy)
  - **ODER** im Profil hinterlegte Website matcht Akteurs-Website
  - **UND** Account ist nicht offensichtlich Fan-Account oder Re-Pinner

Wenn kein eindeutiger Treffer: nicht raten, `match_konfidenz: nicht_gefunden`.

## URL-Patterns

| Zweck | Pattern |
|---|---|
| Profil-Seite | `https://www.pinterest.com/USERNAME/` |
| Pinterest.de-Variante | `https://www.pinterest.de/USERNAME/` - oft Redirect auf `.com` |
| Board-Übersicht | `https://www.pinterest.com/USERNAME/_saved/` (Hilfs-URL, je nach Account) |
| Board-Detail | `https://www.pinterest.com/USERNAME/BOARDSLUG/` |
| Pin-Detail | `https://www.pinterest.com/pin/PIN_ID/` |
| Suche | `https://www.pinterest.com/search/users/?q=SUCHBEGRIFF` |

## Fallback-Kaskade

Pro Akteur wird in dieser Reihenfolge versucht:

1. Primär: `apify/pinterest-scraper` mit dem aus der Touchpoint-Inventur bekannten Username
2. Wenn der Actor fehlerhaft läuft oder leere Daten zurückgibt: erneut mit alternativer URL-Variante (`.de` statt `.com` oder umgekehrt)
3. Wenn weiterhin leer: `apify/puppeteer-scraper` mit Custom-Page-Function
4. Wenn auch das scheitert: `manueller_check_erforderlich: true` setzen, Akteur in der Strategen-Review-Liste

Username-Auflösung-Kaskade (siehe SKILL.md Schritt 2):

1. Touchpoints in `data/kunde.md` / `wettbewerber/AKTEURSSLUG.md`
2. Briefing
3. `apify/pinterest-search-scraper`
4. Skip mit `nicht_gefunden`

## Credit-Verbrauch (Apify)

Grobe Schätzung pro Akteur (Stand Mai 2026):

| Schritt | Compute-Units |
|---|---|
| Profil + Boards (Top-50) | ca. 0,1-0,3 CU |
| Pins (Hard-Cap 40) | ca. 0,2-0,5 CU |
| Search für Username-Auflösung | ca. 0,05-0,1 CU |
| Fallback Puppeteer-Custom | ca. 0,3-0,8 CU |

Für eine typische MTA mit Kunde + 5 Wettbewerbern: ca. 2-5 CU. Bei großen Profilen oder vielen Boards entsprechend mehr.

## Coverage-Erwartung

- Bei verifizierten Business-Accounts: sehr gute Coverage von Profil, Boards und Pin-Sample
- Bei Personal-Accounts: gut, Saves-Counts manchmal lückenhaft
- Bei sehr großen Accounts (>1 Mio Follower): Pinterest drosselt, Pin-Sample kann unvollständig sein - Skill markiert `scrape_unvollstaendig: true`
- Bei sehr kleinen oder neuen Accounts (<10 Pins): Daten meistens vollständig

## Datenfelder-Mapping zur Skill-Output-CSV

Spalten-Reihenfolge in `audits/pinterest-profile.csv` und `audits/pinterest-pins.csv` siehe `pinterest-output-schema.md`.

Wichtige Konvention: alle Counts als int, alle Quoten als float (Engagement-Rate auf zwei Nachkommastellen gerundet), `null` wird als leerer String in der CSV ausgegeben.
