# Instagram-Tools-Mapping

Dokumentiert die Apify-Actor-Optionen fuer `03-08-social-instagram`, das Input-Schema pro Actor, Cookies-Handling bei Login-Wall sowie Rate-Limit-Empfehlungen.

## Apify-Actor-Optionen

Instagram-Scraping ueber Apify ist in drei Varianten moeglich. Default: 1+2 sequenziell. Fallback: 3 als Bundle.

### Variante 1: `apify/instagram-profile-scraper` (Default fuer Profile)

Zweck: pro Akteur nur das Profil. Schnell, billig, robust.

**Input-Schema (typisch):**

```json
{
  "usernames": ["HANDLE_1", "HANDLE_2"],
  "resultsLimit": 1,
  "addParentData": false
}
```

Alternative Input-Form mit direkten URLs:

```json
{
  "directUrls": ["https://www.instagram.com/HANDLE/"],
  "resultsLimit": 1
}
```

**Output-Felder (relevante Auswahl):**

- `username`, `fullName`, `biography`, `externalUrl`
- `followersCount`, `followsCount`, `postsCount`
- `verified`, `isBusinessAccount`, `businessCategoryName`
- `profilePicUrl`, `profilePicUrlHD`
- `private` (bool - Privat-Account)
- `hasChannel`, `igtvVideoCount` (deprecated felder, optional)

Stories liefert dieser Actor i. d. R. nicht direkt - nur indirekte Hinweise (`hasStories` bei einigen Versionen).

### Variante 2: `apify/instagram-post-scraper` (Default fuer Posts)

Zweck: pro Akteur die letzten N Posts.

**Input-Schema (typisch):**

```json
{
  "username": "HANDLE",
  "resultsLimit": 50,
  "onlyPostsNewerThan": "2025-05-13"
}
```

Alternative mit ISO-Cutoff-Datum statt relativer Angabe. Manche Versionen erwarten `directUrls` mit Profil-URL und filtern intern.

**Output-Felder pro Post:**

- `id`, `shortCode`, `url`
- `type` (`Image | Sidecar | Video`) - Sidecar = Carousel
- `productType` (bei Reels: `clips`), `isVideo`
- `caption`, `hashtags`, `mentions`
- `likesCount`, `commentsCount`, `videoViewCount`
- `timestamp` (ISO-8601)
- `displayUrl`, `videoUrl` (fuer Media-Preview)

**Post-Typ-Mapping:**

| Apify-Feld | MTA-`post_typ` |
|---|---|
| `Image` | `image` |
| `Sidecar` | `carousel` |
| `Video` + `productType=clips` | `reel` |
| `Video` ohne `clips` | `igtv` (legacy, faellt sonst auf `reel`) |
| sonst | `unbekannt` |

### Variante 3: `apify/instagram-scraper` (Bundle-Fallback)

Zweck: Profile + Posts in einem Run. Aufwendiger pro Akteur, aber robust wenn die einzelnen Actors nicht verfuegbar sind oder die Apify-Account-Quota begrenzt ist.

**Input-Schema:**

```json
{
  "directUrls": ["https://www.instagram.com/HANDLE/"],
  "resultsType": "details",
  "resultsLimit": 50,
  "addParentData": true
}
```

`resultsType: details` liefert Profil + Posts; `resultsType: posts` nur Posts.

Output enthaelt sowohl Profil-Block (im Top-Level) als auch eine Liste von Posts. Skill muss beide Teile auseinanderpicken.

## MCP-vs-HTTP-Erkennung

Wie bei den anderen Apify-nutzenden Skills:

1. **MCP-Modus**: pruefe vorhandene Tools mit Prefix `mcp__Apify__*` (z. B. `mcp__Apify__call-actor`, `mcp__Apify__get-actor-run`). Wenn vorhanden: nutze `mcp__Apify__call-actor` mit Actor-Slug.
2. **HTTP-Modus**: pruefe `APIFY_TOKEN`-Env-Var. Wenn vorhanden: `POST https://api.apify.com/v2/acts/<actor-slug>/runs?token=$APIFY_TOKEN` mit Input-Body, dann Polling auf Run-Status, dann `GET .../runs/<id>/dataset/items`.
3. **Sonst**: Abbruch mit Hinweis "Apify-Zugang nicht verfuegbar - bitte MCP-Connector verbinden oder APIFY_TOKEN setzen".

## Cookies-Handling bei Login-Wall

Instagram zeigt anonymen Scrapern zunehmend Login-Walls oder degradierten Content. Die meisten Apify-Actors akzeptieren Session-Cookies als Input-Parameter, um sich als eingeloggte Session auszugeben.

### Wann Cookies-Option noetig

- Profil zeigt nur eingeschraenkten Bio-Text oder fehlende Posts-Counts
- Posts-Scrape liefert 0 Posts trotz aktivem Account
- Actor-Run schlaegt mit `LOGIN_REQUIRED`-Fehler fehl
- Rate-Limit-Fehler nach wenigen Akteuren (auch ohne Cookies fix - aber mit Cookies stabiler)

### Cookies bereitstellen

Apify-Actors akzeptieren typischerweise einen `sessionCookies`-Parameter:

```json
{
  "username": "HANDLE",
  "resultsLimit": 50,
  "sessionCookies": [
    { "name": "sessionid", "value": "...", "domain": ".instagram.com" },
    { "name": "ds_user_id", "value": "...", "domain": ".instagram.com" },
    { "name": "csrftoken", "value": "...", "domain": ".instagram.com" }
  ]
}
```

Cookies werden vom Strategen aus einem realen Browser exportiert (z. B. via Browser-Extension "EditThisCookie"). Empfehlung: **dedizierter Dummy-IG-Account** fuer Scraping, nicht der private Account.

### Cookies in Apify-Storage

Statt Cookies bei jedem Run mitzusenden, koennen sie in Apify-Key-Value-Storage hinterlegt und referenziert werden:

```json
{
  "username": "HANDLE",
  "sessionCookiesStorageKey": "instagram-session-cookies"
}
```

(Actor-Version-spezifisch - in der Actor-Doku pruefen.)

### Cookies-Ablauf

Instagram-Session-Cookies laufen typischerweise nach 30-90 Tagen ab. Skill prueft beim Profil-Scrape, ob das Profil erwartete Felder liefert. Bei `private: null` oder fehlenden `followersCount`: wahrscheinlich Cookie-Ablauf - Hinweis im Output, Cookies erneuern.

## Rate-Limit-Empfehlungen

Instagram ist aggressiv gegen Scraping. Empfehlungen:

- **Sequenziell**, niemals parallel - ein Akteur nach dem anderen
- **Pause zwischen Akteuren**: 30-60 Sekunden (von Apify intern oft automatisch)
- **Bei Rate-Limit-Fehler**: Skill markiert Akteur als `ig_scrape_blockiert: true`, wartet 5 Minuten, versucht naechsten Akteur
- **Maximale Akteure pro Lauf**: 10 (Hard-Cap, bei mehr Wettbewerbern Strategen-Bestaetigung einholen)
- **Hard-Cap Posts**: 50 pro Akteur (nicht hoeher - Engagement-Statistik wird durch Outlier verzerrt und Apify-Kosten steigen exponentiell)

## Kosten-Faustregel

Mit Standard-Apify-Pricing (Compute Units, Stand 2026):

- Profil-Scrape: ~0.02 USD pro Akteur
- Posts-Scrape (50 Posts): ~0.10 USD pro Akteur
- Bundle-Scrape (Variante 3): ~0.15 USD pro Akteur

Bei 8 Akteuren (Kunde + 7 WBs): ~0.96 USD pro Lauf. Bei kostenlosem Apify-Tier moeglich ohne extra Aufwand.

## Datenfelder-Mapping zur CSV

| Apify-Feld | CSV-Spalte |
|---|---|
| `username` | `ig_handle` |
| `fullName` | `akteurs_name` (Override moeglich) |
| `biography` | `bio_text` |
| `externalUrl` | `link_in_bio` |
| `followersCount` | `followers_count` |
| `followsCount` | `follows_count` |
| `postsCount` | `posts_count_total` |
| `verified` | `is_verified` |
| `isBusinessAccount` | abgeleitet zu `account_typ` |
| `businessCategoryName` | `business_category` |
| `private` | `privat_account` |
| `timestamp` | `taken_at_iso` |
| `likesCount` | `likes_count` |
| `commentsCount` | `comments_count` |
| `videoViewCount` | `video_views_count` |
| `caption` | `caption_text` (voll im JSON, `caption_auszug` in CSV) |
| `hashtags` | `hashtags` (Liste) plus `hashtag_count` |
| `mentions` | `mentions` (Liste) plus `mention_count` |
