# TikTok-Tools-Mapping

Welcher Apify-Actor für welchen Schritt, Fallback-Reihenfolge, bekannte Eigenheiten der verfügbaren TikTok-Scraper. Pflege diese Datei, wenn ein Actor abgekündigt wird oder ein neuer dazu kommt.

**Stand:** Mai 2026

## Getestete Actor-IDs

Vor dem Lauf immer den Health-Check (Limit-1-Aufruf mit Kunden-Handle) durchführen; bei Fehler Alternativen aus der Liste probieren.

| Actor-ID | Alias / Store-Name | zuletzt_getestet | status | Anmerkung |
|---|---|---|---|---|
| `clockworks/free-tiktok-scraper` | Free TikTok Scraper | noch nicht getestet | unbekannt | Erste Wahl für kostengünstige Läufe |
| `apify/tiktok-scraper` | TikTok Scraper (official) | noch nicht getestet | unbekannt | Stabilere Datenqualität, höhere Kosten |
| `apify/tiktok-profile-scraper` | TikTok Profile Scraper | noch nicht getestet | unbekannt | Nur Profil-Stammdaten (schnell/billig) |
| `apify/tiktok-search-scraper` | TikTok Search Scraper | noch nicht getestet | unbekannt | Profil-Auflösung aus Markennamen |
| `apify/puppeteer-scraper` | Custom Puppeteer | — | fallback | Nur wenn kein spezialisierter Actor verfügbar |

**Login-Wall:** Öffentliche Profile und Videos sind anonym zugänglich. Private Accounts: `profil_privat: true` setzen und überspringen.

## Methoden-Glossar

| Methode | Wann nutzen |
|---|---|
| **A — Apify offizieller TikTok-Scraper** | Erste Wahl für Profil- und Video-Daten. Aktuell empfohlen: `clockworks/free-tiktok-scraper` für kostengünstige Läufe und `apify/tiktok-scraper` für stabilere Datenqualität. |
| **B — Apify TikTok-Profile-Scraper** | Spezialisiert auf Profil-Stamm-Daten (Follower, Bio, Verifizierung). Schnellster Pfad, wenn nur Profil-Snapshot ohne Video-Tiefe gebraucht wird. |
| **C — Apify TikTok-Search-Scraper** | Für Profil-Auflösung aus Markennamen — sucht TikTok intern nach Suchbegriff und gibt Profil-Treffer zurück. |
| **D — Web-Search Fallback** | Wenn alle Apify-Actors fehlschlagen: Web-Search nach `<Markenname> site:tiktok.com` oder `<Markenname> tiktok`, nimm den Top-Treffer als Username-Kandidat und prüfe mit Methode B, ob das Profil existiert. |

## Aufruf-Strategie pro Workflow-Schritt

### Schritt 2 — Profil-Match (Username ermitteln)

Prioritäts-Reihenfolge pro Akteur:

1. **Touchpoint-Inventur** lesen (`data/kunde.md`, `wettbewerber/profile/*.md`). Wenn `tiktok`-Touchpoint vorhanden → Username extrahieren, Methode B nur zur Verifizierung.
2. **Website-Footer / Impressum** scannen, falls Website-URL vorhanden. Suche nach `tiktok.com/@`-Pattern in HTML.
3. **Methode C — TikTok-Search** mit Markenname als Query. Filter: Profil-Verifizierung bevorzugt, gefolgt von Follower-Count > 100 und Bio-Inhalt mit Branchen-Bezug.
4. **Methode D — Web-Search** als letzter Fallback. Eindeutigkeit prüfen: bei mehreren plausiblen Treffern → `kein_eindeutiger_match`, NICHT raten.

Output dieses Schritts pro Akteur:

```
akteurs_slug, tiktok_username (oder null), match_quelle (touchpoint | website | search | web_search | nicht_gefunden), match_konfidenz (hoch | mittel | niedrig)
```

### Schritt 4 — Profil-Daten

- **Primär**: Methode B (`apify/tiktok-profile-scraper` oder Profil-Endpoint von `clockworks/free-tiktok-scraper`)
- **Fallback**: Methode A im Profil-Modus
- **Output-Felder**: `username`, `display_name`, `bio`, `follower_count`, `following_count`, `likes_total`, `videos_total`, `verified`, `region`, `external_link`, `avatar_url`

Roh-JSON im lokalen Arbeits-Cache `~/.cache/reachx-mta/<slug>/raw/tiktok-profile-<akteurs-slug>.json` speichern, **unverändert** vom Actor — kein Umstrukturieren auf dem Weg in den Cache. Am Skill-Ende wird der Cache gzip-komprimiert nach Drive `assets/raw/` hochgeladen.

### Schritt 5 — Video-Sample

- **Primär**: Methode A (`clockworks/free-tiktok-scraper` oder `apify/tiktok-scraper`)
- **Input-Parameter**:
  - `profiles`: `[<username>]`
  - `resultsPerPage` / `maxItems`: 30
  - `sort`: `latest` (Recency!)
  - Zeitraum-Cutoff: Aktor-abhängig — wenn der Actor `older than X` filtern kann, auf 12 Monate begrenzen; sonst nach dem Scrape clientseitig auf Posting-Datum filtern
- **Output-Felder pro Video**: `id`, `webVideoUrl`, `createTimeISO`, `videoMeta.duration`, `playCount` (Views), `diggCount` (Likes), `commentCount`, `shareCount`, `collectCount` (Saves, optional), `text` (Caption), `hashtags[]`, `musicMeta.musicName`, `musicMeta.musicAuthor`, `musicMeta.musicOriginal` (Bool), `musicMeta.musicId`, `isAd`, `isDuet` / `duetInfo`, `isStitch` / `stitchInfo`

**Field-Mapping-Hinweise:**

- Verschiedene Actor-Versionen verwenden unterschiedliche Feld-Namen für Views (`playCount` vs. `viewCount` vs. `stats.playCount`). Beim Mapping defensiv lesen — siehe Mapping-Heuristik unten.
- Hashtags: Manche Actors geben sie als strukturiertes Array zurück, andere nur im Caption-Text. Wenn Array leer ist, fallback per Regex `#\w+` aus Caption parsen.

### Mapping-Heuristik für Field-Namen

Beim Parsen des Actor-Outputs defensiv vorgehen:

```
views   = item.playCount || item.viewCount || item.stats?.playCount || 0
likes   = item.diggCount || item.likeCount || item.stats?.diggCount || 0
comments = item.commentCount || item.stats?.commentCount || 0
shares  = item.shareCount || item.stats?.shareCount || 0
saves   = item.collectCount || item.stats?.collectCount || null
```

Engagement-Rate erst berechnen, wenn `views > 0`. Sonst `null` setzen und im CSV als leere Zelle ausweisen.

## Bekannte Edge Cases der Scraper

### `clockworks/free-tiktok-scraper`

- Kostengünstig, aber Engagement-Felder gelegentlich unvollständig
- Hard-Limit ~50 Videos pro Profil-Lauf in der Free-Tier-Konfiguration — für unseren Cap von 30 unproblematisch
- Bei sehr großen Profilen (>1 Mio. Follower) gelegentlich Timeouts → Retry mit `maxItems: 30` explizit

### `apify/tiktok-scraper`

- Stabilere Datenqualität, aber teurer pro Compute-Unit
- Liefert in der Regel vollständige Music-Meta-Daten inklusive Music-ID
- Unterstützt Search-Modus → kann auch für Methode C genutzt werden

### `apify/tiktok-profile-scraper`

- Schnellster Profil-Snapshot, aber keine Video-Daten
- Ideal für Schritt 4, wenn das volle Video-Sample über Methode A separat läuft
- Falls dieser Actor abgekündigt ist: `clockworks/free-tiktok-scraper` im Profil-Only-Modus

### Profil-Match-Fehlalarme

- Generische Markennamen ("Müller", "Schmidt-GmbH") → TikTok-Search liefert hunderte irrelevante Treffer. Lieber `kein_eindeutiger_match` setzen als raten.
- Markenname + Stadt als Query versuchen, falls der Akteur lokal ist (aus `meta.json.region` oder `wettbewerber/liste.md`).
- Bei Verdacht auf Fake-Profile (sehr alte Profile mit 0 Posts seit 2020): nicht als Match werten.

## Setup-Anforderungen

- **Apify-Token**: `APIFY_TOKEN` als Env-Var oder Apify-MCP-Connector verbunden
- **Login bei TikTok nicht erforderlich** für öffentliche Profile — Anti-Bot-Maßnahmen werden vom Apify-Actor gehandhabt
- **Rate-Limits**: Apify-Pay-as-you-go kostet typisch $0.10-0.50 pro Akteur (Profil + 30 Videos). Bei 1 Kunde + 8 Wettbewerbern liegen Gesamtkosten etwa bei $1-4.

## Mainenance-Hinweis

Wenn Apify einen Actor abkündigt oder ein neuer empfohlener Actor erscheint:

1. Diese Datei aktualisieren
2. In `SKILL.md` Schritt 4/5 die Actor-Namen anpassen
3. Skill-Version in `schema_version` (im Output-Schema) hochzählen, falls sich das Feld-Mapping signifikant ändert
