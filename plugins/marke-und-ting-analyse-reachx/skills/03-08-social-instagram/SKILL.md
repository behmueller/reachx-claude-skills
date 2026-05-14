---
name: 03-08-social-instagram
description: Erhebt für Kunde und alle bestätigten Wettbewerber den Instagram-Status via Apify-Scraper - Profil-Daten (Follower, Following, Posts, Bio, Link-in-Bio, Verifizierung, Account-Typ) plus Posts der letzten 12 Monate (Hard-Cap 50 pro Akteur) mit Engagement-Rate, Post-Typ-Mix (Image/Carousel/Reel/IGTV), Posting-Frequenz, Caption-Pattern, Content-Pillars-Heuristik und Stories-Aktivitaet wenn der Actor sie liefert. Output ist audits/instagram-wettbewerb.md plus audits/instagram-profile.csv plus audits/instagram-posts.csv plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Instagram-Aktivitaet pruefen will - auch bei Phrasen wie "Instagram Check", "Instagram-Wettbewerbsanalyse", "wer ist auf Instagram aktiv", "Instagram-Audit", "IG-Profile vergleichen", "Reels-Strategie der Wettbewerber", "Instagram Engagement", "Content-Pillars auf Instagram". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist; ohne wettbewerber/liste.md laeuft der Skill im Kunden-only-Modus.
---

# Instagram-Competitor-Research

Stufe-3-Social-Audit, analog zu `03-11-social-linkedin`. Erhebt fuer Kunde + alle bestaetigten Wettbewerber via Apify den aktuellen Instagram-Status - Profil-Snapshot plus Posts-Sample der letzten 12 Monate mit Engagement-Statistik und Content-Pillars-Heuristik.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/instagram-wettbewerb.md` - Profil-Snapshot, Posts-Statistik, Content-Pillars, Auffaelligkeiten pro Akteur
2. **Profile-CSV** `audits/instagram-profile.csv` - eine Zeile pro Akteur mit Profil-Kennzahlen
3. **Posts-CSV** `audits/instagram-posts.csv` - eine Zeile pro Post mit Engagement-Daten
4. **HTML-Report** `reports/15-instagram-wettbewerb.html` - Strategen-Bericht mit Profil-Matrix, Posts-Galerie, Content-Pillars

**Wichtige Begrenzung:** Instagram erlaubt anonymen Zugriff nur eingeschraenkt. Bei Login-Wall nutzt der Skill Apify-Cookies-Option (siehe `reference/instagram-tools-mapping.md`). Posts-Coverage ist nie 100% - das wird im Output transparent gemacht. Stories sind ueber den Standard-Profile-Scraper nicht zuverlaessig erfassbar - nur Hinweis "stories_aktiv ja/nein" wenn der Actor das Feld liefert.

**Branchen-Relevanz-Hinweis:** Bei reinen B2B-Branchen (B2B-SaaS, Industrie, Spezialdienstleistung) ist Instagram oft Nebenkanal. Der Skill laeuft trotzdem - die Auffaelligkeit `branche_ig_unueblich` markiert das fuer die Synthese, damit `04-02-kanal-chancen-analyse` Instagram nicht ueberbewertet.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "Instagram Check"
- "Instagram-Wettbewerbsanalyse"
- "Wer ist auf Instagram aktiv"
- "Instagram-Audit"
- "IG-Profile vergleichen"
- "Reels-Strategie der Wettbewerber"
- "Instagram Engagement"
- "Content-Pillars auf Instagram"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA in `~/.cache/reachx-mta/active-mtas.json` registriert, `meta.json` im Drive-MTA-Root
- Apify-Zugang verfuegbar (siehe `reference/instagram-tools-mapping.md` fuer Actor-Auswahl)
- Empfohlen: `wettbewerber/liste.md` (Drive) mit `status: bestaetigt` - sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` und `wettbewerber/SLUG.md` (Drive) mit Touchpoint-Inventur (`typ: instagram`) - daraus zieht der Skill die Profil-URLs
- Optional: Apify-Cookies (Instagram-Login-Session) - bei aggressiver Rate-Limitierung oder Login-Wall noetig

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

Folge `contracts.md` Abschnitt 1. Ermittle die Drive-Folder-IDs aus `meta.json`:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WETTBEWERBER_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Wenn `get-mta` nichts liefert: Abbruch mit Hinweis "01-01-mta-projekt-init zuerst aufrufen".

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Lies `wettbewerber/liste.md` aus dem Drive-Sub-Folder `WETTBEWERBER_ID` via `find_by_name` + `read_text`. Wenn vorhanden mit `status: bestaetigt` → Modus **Voll**; sonst → Modus **Kunden-only** mit Hinweis.

Pruefe Apify-Zugang (MCP-Tools mit Prefix `mcp__Apify__*` oder `APIFY_TOKEN` im Environment). Bei fehlendem Zugang: Abbruch mit Hinweis.

### Schritt 2: Profil-URL-Match pro Akteur

Pro Akteur die Instagram-Profil-URL aus den Marken-Profilen ziehen (alle Files aus Drive lesen):

1. **Kunde**: aus `data/kunde.md` (Drive `DATA_ID`) Frontmatter-Feld `touchpoints` einen Eintrag mit `typ: instagram` suchen
2. **Wettbewerber**: pro Eintrag aus `liste.md` mit gueltiger `slug` aus `wettbewerber/SLUG.md` (Drive `WETTBEWERBER_ID`) Touchpoint-Inventur ziehen

URL-Normalisierung:

- `instagram.com/handle` → `https://www.instagram.com/handle/`
- Trailing-Slash standardisieren
- Query-Params entfernen
- Wenn nur Handle ohne URL: `https://www.instagram.com/HANDLE/`

**Akteure ohne IG-Profil:**

- Skip mit Hinweis `kein_ig_profil_identifiziert`
- Wenn der Kunde keine IG-Profil hat: separate Auffaelligkeit `kunde_kein_ig_profil` (siehe Schritt 9)
- Empfehlung im Output: "Eventuell `02-01-kunden-marken-profil` / `02-03-wettbewerber-marken-profil` erneut laufen lassen, wenn ein IG-Profil im Web auffindbar ist aber nicht in der Touchpoint-Inventur steht"

### Schritt 3: Existenz-Check Output

Pruefe via `list-children` auf `AUDITS_ID`, ob `instagram-wettbewerb.md`, `instagram-profile.csv` oder `instagram-posts.csv` bereits im Drive `audits/`-Folder existieren: fragen (ueberschreiben / Backup-und-neu / abbrechen).

### Schritt 4: Profil-Scrape pro Akteur

Pro Akteur sequenziell (Rate-Limits ernst nehmen) mit `apify/instagram-profile-scraper` (siehe `reference/instagram-tools-mapping.md` fuer Actor-Optionen und Cookies-Handling):

1. **Input bauen**: `{ "usernames": ["HANDLE"] }` oder `{ "directUrls": ["URL"] }` je nach Actor-Variante
2. **Run starten und auf Fertig warten** - bei Cookies-Option Apify-Storage-Key fuer Cookies hinterlegen
3. **Daten extrahieren**:
   - `username`, `full_name`, `biography`, `external_url` (Link-in-Bio)
   - `followers_count`, `follows_count`, `posts_count`
   - `is_verified` (bool), `is_business_account` (bool), `business_category_name`
   - `account_typ`: `personal | business | creator | unbekannt` (aus is_business_account + Hinweisen)
   - `profile_pic_url` (fuer HTML-Report)
   - `stories_aktiv` (bool, falls Actor das liefert) und `stories_anzahl_24h` (falls verfuegbar)
4. **Roh-Daten ablegen** im lokalen Arbeits-Cache unter `~/.cache/reachx-mta/<slug>/raw/instagram-profile-SLUG.json` - am Skill-Ende werden alle Roh-JSONs gzip-komprimiert nach Drive in den `assets/raw/`-Sub-Folder hochgeladen (siehe Schritt 14)

Fehler-Handling:

- **Privat-Account**: `privat_account: true`, kein Posts-Scrape, Hinweis im Output
- **Account nicht gefunden** (Handle falsch oder geloescht): `profil_existiert: false`, Hinweis
- **Login-Wall trotz Cookies**: Skill bricht fuer diesen Akteur ab, weiter mit naechstem, Auffaelligkeit `ig_scrape_blockiert` sammelt die Faelle

### Schritt 5: Posts-Scrape pro Akteur

Pro Akteur mit `apify/instagram-post-scraper` (oder Bundle-Actor `apify/instagram-scraper`):

1. **Input bauen**: `{ "username": "HANDLE", "resultsLimit": 50, "onlyPostsNewerThan": "12 months" }` - exakte Parameter siehe Actor-Spezifikation in `reference/instagram-tools-mapping.md`
2. **Hard-Cap**: 50 Posts pro Akteur (auch wenn mehr verfuegbar)
3. **Zeitraum-Filter**: nur Posts juenger als 12 Monate (ab heute)
4. **Daten extrahieren pro Post**:
   - `post_id` (Instagram-Shortcode), `post_url`
   - `post_typ`: `image | carousel | reel | igtv | unbekannt`
   - `caption_text` (voll), `caption_laenge` (Zeichen), `hashtag_count`, `mention_count`
   - `hashtags` (Liste), `mentions` (Liste)
   - `likes_count`, `comments_count`
   - `video_views_count` (nur bei Reels/IGTV)
   - `taken_at_iso` (Post-Datum)
   - `media_url` (fuer HTML-Report)
   - `engagement_rate`: `(likes + comments) / followers` (auf 4 Nachkommastellen)
5. **Roh-Daten ablegen** im lokalen Arbeits-Cache unter `~/.cache/reachx-mta/<slug>/raw/instagram-posts-SLUG.json` - Upload nach Drive `assets/raw/` (gzip-komprimiert) am Skill-Ende (siehe Schritt 14)

Wenn weniger als 50 Posts in 12 Monaten verfuegbar: alle nehmen, im Output Anzahl ausweisen. Wenn 0 Posts in 12 Monaten: `account_inaktiv: true`, Posting-Frequenz wird zu 0, Auffaelligkeit `kunde_inaktiv_seit_X_wochen` oder `wb_inaktiv` (siehe Schritt 9).

### Schritt 6: Aggregat-Statistik pro Akteur

Aus den Posts berechnen:

- **Posting-Frequenz**: Posts/Woche, Median-Tage-Abstand zwischen Posts
- **Durchschnittliche Engagement-Rate**: Mittelwert ueber alle Posts
- **Engagement-Rate-Verteilung**: P25, Median, P75
- **Post-Typ-Mix**: Prozent-Verteilung (image / carousel / reel / igtv)
- **Top-3-Posts nach Engagement-Rate**: post_url, caption_auszug, engagement_rate, post_typ
- **Caption-Pattern**:
  - Durchschnittliche Caption-Laenge
  - Hashtag-Nutzung: Durchschnitt + Median Hashtags pro Post
  - Mention-Nutzung: Durchschnitt Mentions pro Post
- **Top-10-Hashtags** des Akteurs (Frequenz-Ranking)

### Schritt 7: Content-Pillars-Heuristik pro Akteur

Aus den Caption-Tokens Themen-Cluster bilden (heuristisch, nicht Schema-vor-Lauf):

1. **Tokenize**: Captions in Tokens splitten, Stopwords entfernen, Hashtags separat behandeln
2. **Cluster** nach Co-Occurrence: Gruppen von Tokens, die haeufig gemeinsam auftreten
3. **Benennen**: pro Cluster die Top-3-Tokens als Cluster-Label nehmen (z. B. `produkt_neuheit`, `team_einblick`, `kunden_referenz`)
4. **Pillar-Anzahl**: typischerweise 3-5 Pillars pro Akteur, Rest als `sonstiges`
5. **Statistik pro Pillar**: Anzahl Posts, durchschnittliche Engagement-Rate, dominante Post-Typen

Methodik in `reference/instagram-output-schema.md` Abschnitt "Content-Pillars-Heuristik" dokumentiert.

### Schritt 8: Branchen-Median-Berechnung

Aus allen Wettbewerbs-Akteuren (ohne Kunden) den Median der Engagement-Rate berechnen. Wenn weniger als 3 WBs Daten haben: Branchen-Benchmark-Default 1.5% nutzen, im Output mit Hinweis ausweisen.

Der Wert wird in Schritt 9 fuer die Auffaelligkeit `kunde_engagement_unter_branchen_median` genutzt.

### Schritt 9: Auffaelligkeiten

Aus den erhobenen Daten:

| Typ | Ausloeser | Beispiel |
|---|---|---|
| `kunde_kein_ig_profil` | Kunde hat kein IG-Profil in Touchpoint-Inventur | "Kunde hat kein Instagram-Profil identifiziert - bei B2C-Branche Vorsicht, eventuell uebersehen oder strategisch ausgelassen" |
| `kunde_inaktiv_seit_X_wochen` | Kunde hat 0 Posts in den letzten X Wochen (X >= 4) | "Kunde hat seit 12 Wochen nicht gepostet - Account wirkt verwaist" |
| `kunde_engagement_unter_branchen_median` | Kunden-Engagement-Rate < 0.7 × Branchen-Median | "Kunde liegt bei 0.4% Engagement-Rate, Branchen-Median 1.8% - Content-Qualitaet hinterfragen" |
| `wettbewerber_reel_strategie` | Mindestens 1 WB hat >40% Reels-Anteil, Kunde unter 10% | "Wettbewerber alpha-tech setzt 50% auf Reels - Kunde hat keine Reels, format-Luecke" |
| `content_pillar_luecke_kunde` | Pillar bei >2 WBs aktiv (>=5 Posts), bei Kunde fehlend | "WBs bespielen Pillar 'kunden_referenz' regelmaessig, Kunde nicht - Trust-Signal-Luecke" |
| `posting_frequenz_diskrepanz` | WB-Median >= 3× Kunden-Frequenz | "WBs posten im Median 4x/Woche, Kunde 1x/Monat - Sichtbarkeits-Luecke" |
| `hashtag_strategie_unterschied` | Hashtag-Set-Schnittmenge Kunde × Top-WB-Set < 20% | "Kunde nutzt komplett andere Hashtags als die aktivsten WBs - moeglicher Distribution-Verlust" |
| `branche_ig_unueblich` | >60% der WBs ohne IG-Profil ODER WB-Median < 0.5 Posts/Woche | "Branche ist auf Instagram strukturell schwach vertreten - Instagram in `04-02-kanal-chancen-analyse` als Nebenkanal markieren" |

Pro Auffaelligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure.

Mindest-Erwartung: 6 Auffaelligkeits-Typen im Schema (oben 8 definiert - alle koennen ausgeloest werden, sind nicht alle Pflicht pro Lauf).

### Schritt 10: Profile-CSV `audits/instagram-profile.csv`

Eine Zeile pro Akteur. Schema in `reference/instagram-output-schema.md` Abschnitt "Profile-CSV".

Spalten:

```
akteurs_slug, akteurs_typ, akteurs_name, ig_handle, ig_profil_url,
followers_count, follows_count, posts_count_total,
is_verified, account_typ, business_category,
bio_text, bio_laenge, link_in_bio,
posts_letzte_12mo_count, posting_frequenz_pro_woche,
engagement_rate_median, engagement_rate_p25, engagement_rate_p75,
post_typ_mix_image_pct, post_typ_mix_carousel_pct, post_typ_mix_reel_pct, post_typ_mix_igtv_pct,
hashtag_durchschnitt_pro_post, content_pillars_count,
stories_aktiv, stories_hinweis,
profil_existiert, privat_account, account_inaktiv, scrape_blockiert,
datenstand_iso
```

### Schritt 11: Posts-CSV `audits/instagram-posts.csv`

Eine Zeile pro Post × Akteur. Schema in `reference/instagram-output-schema.md` Abschnitt "Posts-CSV".

Spalten:

```
akteurs_slug, akteurs_typ, post_id, post_url, post_typ,
taken_at_iso, caption_auszug, caption_laenge,
hashtag_count, mention_count, hashtags_top5,
likes_count, comments_count, video_views_count,
engagement_rate, content_pillar, datenstand_iso
```

`caption_auszug`: erste 200 Zeichen der Caption. Originaltext nicht aendern - vollstaendige Caption liegt in `raw/instagram-posts-SLUG.json`.

### Schritt 12: Aggregat-Markdown `audits/instagram-wettbewerb.md`

Frontmatter mit:

- Skill-Metadaten, Quellen-Provenienz (Apify-Actor + Datum + Anzahl Akteure)
- Profil-Matrix pro Akteur (Follower, Posts/Woche, Engagement-Rate, Post-Typ-Mix, Pillar-Anzahl)
- Branchen-Aggregat (Median-Engagement-Rate, Median-Frequenz, Typ-Mix-Branche)
- Branchen-Relevanz-Hinweis: `branche_ig_relevanz: stark | mittel | schwach` (aus Daten abgeleitet)
- Auffaelligkeiten

Body:

- Uebersicht (Anzahl Akteure mit Profil, Anzahl aktiv, Top-Engagement, Top-Reach)
- Branchen-Relevanz-Block (wenn schwach: prominent oben)
- Akteurs-Vergleichs-Tabelle (Profil-Kennzahlen)
- Pro Akteur ein Sub-Block mit:
  - Profil-Snapshot (Follower, Posts gesamt, Account-Typ, Bio-Auszug, Link-in-Bio)
  - Posting-Aktivitaet (Frequenz, Posts letzte 12mo, Median-Tage-Abstand)
  - Engagement-Rate-Statistik
  - Post-Typ-Mix
  - Content-Pillars (Top-3 mit Beispiel-Post)
  - Top-3-Posts (mit Caption-Auszug, Engagement-Rate)
  - Stories-Hinweis falls verfuegbar
- Content-Pillars-Uebersicht ueber alle WBs (welche Themen werden branchenweit bespielt?)
- Auffaelligkeiten als Liste

### Schritt 13: HTML-Report `reports/15-instagram-wettbewerb.html`

Aus `reports/_shell.html`:

- **Stat-Strip oben**: Akteure mit IG-Profil, aktive Akteure, Branchen-Median-ER, Top-Werber, Top-Reach-Akteur
- **Sticky-TOC** zu allen Sektionen
- **Branchen-Relevanz-Banner** oben (wenn schwach: rote Hervorhebung mit Hinweis fuer `04-02-kanal-chancen-analyse`)
- **Profil-Matrix-Tabelle**: Akteur × Follower × Frequenz × ER × Pillar-Anzahl
- **Pro Akteur** ein `details class="skill"`-Block mit:
  - Profil-Header (Avatar wenn vorhanden, Bio, Follower-Counts)
  - Posts-Statistik als Mini-Stat-Strip
  - Post-Typ-Mix als kleine Balken
  - Top-3-Posts als Karten (mit Media-Thumbnail, Caption-Auszug, ER-Wert)
  - Content-Pillars als Tag-Liste
- **Content-Pillars-Branchen-Uebersicht**: Pillars die mehrere WBs bespielen, mit Akteurs-Verteilung
- **Auffaelligkeiten** als `.suggestion`-Block
- Footer mit Datenquellen-Hinweis und Apify-Actor-Name

### Schritt 14: Outputs nach Drive hochladen, Dashboard-Update, status.md

**Output-Uploads nach Drive** (in dieser Reihenfolge):

1. Aggregat-Markdown, Profile-CSV, Posts-CSV → `AUDITS_ID`:
   ```bash
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "instagram-wettbewerb.md" /tmp/instagram-wettbewerb.md "text/markdown"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "instagram-profile.csv" /tmp/instagram-profile.csv "text/csv"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "instagram-posts.csv" /tmp/instagram-posts.csv "text/csv"
   ```
2. Roh-JSONs gzip-komprimieren und nach Drive `assets/raw/` hochladen (Apify-Outputs koennen mehrere MB pro Akteur sein, daher gzip Pflicht):
   ```bash
   RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
   for f in ~/.cache/reachx-mta/<slug>/raw/instagram-*.json; do
     gzip -k "$f"
     python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
   done
   ```
3. HTML-Report `15-instagram-wettbewerb.html` → `REPORTS_ID` (siehe Schritt 13).

**`status.md`-Update** (siehe `contracts.md` Abschnitt 3):

- `03-08-social-instagram` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs (Drive-Pfade), Hinweisen (z. B. "3 von 7 Akteuren mit IG-Profil, Branchen-Relevanz schwach")
- Reports-Liste um `15-instagram-wettbewerb.html`
- Stat-Strip aktualisieren
- `naechster_empfohlen`: passender naechster Social-Skill (`03-09-social-tiktok` / `03-10-social-pinterest`) oder `04-02-kanal-chancen-analyse` wenn genug Audits durch

`status.md` und `reports/index.html` aus Drive lesen, aktualisieren, via `upsert-text` zurueckschreiben.

### Schritt 15: Standard-Schlussformat im Chat

```
✓ 03-08-social-instagram abgeschlossen.

Outputs (auf Drive):
- audits/instagram-wettbewerb.md - Aggregat mit Profil-Matrix und Content-Pillars
- audits/instagram-profile.csv - Profil-Daten-Matrix (N Akteure)
- audits/instagram-posts.csv - Posts-Sample (P Posts)
- reports/15-instagram-wettbewerb.html - Strategen-Report
- assets/raw/instagram-*.json.gz - komprimierte Apify-Roh-JSONs
Status aktualisiert in: status.md

IG-Lage:
- Akteure mit IG-Profil:       M von N
- Aktiv (Posts in 12mo):       A
- Branchen-Median-ER:          X.X %
- Top-Engagement-Akteur:       AKTEUR mit Y.Y %
- Reels-Anteil-Branche:        Z %
- Content-Pillars erkannt:     P (branchenweit)

[Wenn Auffaelligkeiten:]
⚠ IG-Insights:
- (1-3 Top-Auffaelligkeiten)

[Wenn Branche IG-unueblich:]
ℹ Branchen-Relevanz schwach
- Instagram ist in dieser Branche strukturell schwach - in `04-02-kanal-chancen-analyse` als Nebenkanal werten.

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestaetigt - IG-Lage nur fuer den Kunden, kein Branchen-Benchmark.

[Wenn Scrape-Probleme:]
ℹ Login-Wall / Rate-Limit
- N Akteure konnten nicht vollstaendig gescraped werden - eventuell Apify-Cookies-Option pruefen.

Naechste Schritte:
1. 03-09-social-tiktok - analoges Pattern fuer TikTok, wenn Branche videoaffin
2. (parallel moeglich) 03-10-social-pinterest - bei B2C-Visual-Branchen
3. (parallel moeglich) 04-02-kanal-chancen-analyse - wenn 4-5 Audits durch sind

Sag mir, welcher als naechster.
```

## Bundled Resources

- `reference/instagram-tools-mapping.md` - Apify-Actor-Optionen (Profile-Scraper, Post-Scraper, Bundle-Scraper), Input-Schema, Cookies-Handling bei Login-Wall, Rate-Limit-Empfehlungen
- `reference/instagram-output-schema.md` - Profile-CSV-Schema, Posts-CSV-Schema, Markdown-Frontmatter, Content-Pillars-Heuristik, Validierungs-Regeln

## Edge Cases

- **Privat-Account**: Profil-Daten sind teilweise sichtbar (Bio, Follower-Count), Posts nicht. Profile-CSV-Zeile bleibt, Posts-CSV ohne Eintrag, im Output Hinweis "Privat-Account, Posts nicht zugaenglich".

- **Account geloescht oder Handle umbenannt**: Apify liefert leeres Resultat. Skill markiert `profil_existiert: false`, Hinweis im Output mit Empfehlung "Handle in Touchpoint-Inventur pruefen".

- **Verifizierter Account mit Mega-Reichweite (>1 Mio Follower)**: Engagement-Rate ist strukturell niedriger (Account-Groesse-Effekt). Skill weist das im Akteurs-Sub-Block aus, vergleicht nicht direkt mit kleineren Akteuren.

- **Account postet ausschliesslich Reels**: Post-Typ-Mix zeigt 100% Reels - Content-Pillars-Heuristik funktioniert weiter, Caption-Pattern bleibt valide. Im Output `reel_only_strategie: true`.

- **Sehr lange Captions (>2000 Zeichen)**: Caption-Auszug auf 200 Zeichen in CSV/Markdown, voller Text in `raw/`-JSON.

- **Hashtag-Spam (>30 Hashtags pro Post, alle generisch)**: Skill markiert in Auffaelligkeiten `hashtag_spam_pattern` als Sub-Variante von `hashtag_strategie_unterschied`.

- **Carousel-Posts mit mehreren Bildern**: zaehlen als 1 Post (nicht pro Slide), Engagement-Rate aggregiert ueber den Carousel.

- **IGTV ist deprecated** (Instagram hat IGTV in Reels integriert): Skill akzeptiert `igtv` als Post-Typ wenn der Actor das noch liefert, behandelt sonst als `video` unter `reel`.

- **Stories liefern nur Hinweis** (keine Inhalts-Analyse): wenn der Actor `stories_active: true` plus eventuell `stories_count_24h: <int>` liefert, uebernehmen wir das. Mehr nicht - Stories-Content ist nicht im Standard-Scope.

- **Apify-Actor scheitert komplett (UI-Aenderung)**: Fallback auf `apify/instagram-scraper` (Bundle-Actor mit Profile + Posts in einem Run) oder manuelle Pruefung (TC-Pattern wie bei `03-05-sea-google-ads-check`).

- **Brand-Multi-Account-Strategie** (Hauptaccount + Sub-Accounts wie `brand`, `brand_de`, `brand_jobs`): Skill scraped nur den in der Touchpoint-Inventur eingetragenen Account. Wenn Stratege mehrere will: Override "auch HANDLE_2 scrapen".

- **Wechselkurs Cookies (Login-Session laeuft ab)**: Skill prueft beim Profil-Scrape, ob das Cookie noch valide ist. Bei Fehler: Empfehlung im Output, Cookies in Apify-Storage zu erneuern.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown + YAML-Frontmatter fuer Aggregat, CSV fuer Roh-Daten
- Standard-Schlussformat
- `status.md` und Dashboard werden aktualisiert
- HTML-Report aus `reports/_shell.html`
- **Roh-Daten** unter Drive `assets/raw/instagram-profile-SLUG.json.gz` und `instagram-posts-SLUG.json.gz` als komprimierter Cache (lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/raw/`)
- **Captions unveraendert** lassen - Originaltexte sind die Datenbasis, keine Uebersetzungen oder Umformulierungen
- **Engagement-Rate auf 4 Nachkommastellen** in der CSV, im Markdown als Prozent mit 1 Nachkommastelle
- **Branchen-Relevanz-Hinweis ist Pflicht** im Output - bei B2B-Branchen explizit dokumentieren, dass IG Nebenkanal ist
