---
name: 03-09-social-tiktok
description: Vollständige TikTok-Wettbewerbsanalyse für Kunde und bestätigte Wettbewerber. Pro Akteur Profil-Daten (Follower, Following, Likes-Gesamt, Bio, Verifizierung) plus ein Video-Sample der letzten 6-12 Monate (Hard-Cap 30 Videos pro Akteur) mit Views, Likes, Comments, Shares, Engagement-Rate, Caption, Hashtags, Music-Track, Video-Länge, Top-3-Videos und Content-Pillars-Heuristik. Erfasst TikTok-Spezifika wie Trend-Sound-Nutzung, Duet/Stitch-Aktivität und Hashtag-Challenge-Teilnahme. Output ist audits/tiktok-wettbewerb.md plus Profil- und Video-CSVs und reports/16-tiktok-wettbewerb.html. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext die TikTok-Präsenz vergleichen will - auch bei Phrasen wie "TikTok-Wettbewerbsanalyse", "TikTok-Audit", "wer ist auf TikTok aktiv", "TikTok-Profile vergleichen", "TikTok-Engagement", "Trend-Sounds Wettbewerber", "ist TikTok ein Kanal für uns". Skip bei 0 erkennbaren TikTok-Profilen mit Branchen-Fit-Hinweis. Setzt 02-02-wettbewerber-identifikation voraus.
---

# TikTok Competitor Research

Stufe-3-Audit-Skill für die TikTok-Präsenz. Analog zu `03-08-social-instagram`, aber zugeschnitten auf TikTok-Spezifika (Trend-Sounds, Hashtag-Challenges, Duet/Stitch, sehr volatile Engagement-Verteilung).

Pro Akteur (Kunde + alle bestätigten Wettbewerber) erhebt der Skill:

- **Profil-Daten**: Follower-Count, Following-Count, Likes-Gesamt, Bio-Text, Verifizierungs-Status
- **Video-Sample der letzten 6-12 Monate** (max. 30 Videos pro Akteur): Views, Likes, Comments, Shares, Engagement-Rate, Caption, Hashtags, Music-Track, Video-Länge
- **TikTok-Spezifika**: Trend-Sound-Nutzung, Duet/Stitch-Aktivität, Hashtag-Challenge-Teilnahme
- **Heuristiken**: Top-3-Videos nach Views, Content-Pillars-Heuristik

Output (auf Drive): `audits/tiktok-wettbewerb.md`, `audits/tiktok-profile.csv`, `audits/tiktok-videos.csv`, `assets/raw/tiktok-*-SLUG.json.gz` (gzip-komprimiert), `reports/16-tiktok-wettbewerb.html`.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="<name-dieses-skills>"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Report-Render zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Branchenrelevanz — wichtiger Vorab-Hinweis

TikTok ist stark B2C-, Lifestyle-, Gen-Z- und Entertainment-lastig. Bei klassischen B2B-Industrien, Recht, Steuerberatung, Hausverwaltung, Versicherungen, Anlagenbau, technischen Dienstleistungen ist die TikTok-Aktivität oft 0 — sowohl beim Kunden als auch bei allen Wettbewerbern.

**Verhalten dieses Skills:**

- Wenn **0 Akteure** ein erkennbares TikTok-Profil haben → automatischer Skip mit Hinweis-Output und `branchen_fit: gering` im Frontmatter. Kein voller Lauf, kein Video-Scrape.
- Wenn **nur 1-2 Akteure** ein Profil haben → kompakter Lauf, im Output prominent dokumentiert: "TikTok-Branchen-Fit gering — strategisches Nicht-Thema, wenn keine Akteure aktiv".
- Bei **>=3 aktiven Akteuren** → voller Audit-Lauf.

Diese Schwelle ist im Schluss-Format explizit dokumentiert, damit der Stratege weiß, warum der Audit klein ausfällt.

## Wann triggern

- "TikTok-Wettbewerbsanalyse"
- "TikTok-Audit für [Kunde]"
- "Wer von den Wettbewerbern ist auf TikTok aktiv"
- "TikTok-Profile vergleichen"
- "TikTok-Engagement-Rate Branche"
- "Trend-Sounds Wettbewerber"
- "Hashtag-Challenges in unserer Branche"
- "Ist TikTok ein Kanal für uns"
- "TikTok-Content-Audit"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA registriert, `meta.json` im Drive-MTA-Root
- `02-02-wettbewerber-identifikation` Phase A + B abgeschlossen:
  - `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` (Drive)
  - `wettbewerber/liste.md` mit `status: bestaetigt` (Drive)
- Apify-Zugang verfügbar (für TikTok-Scraper-Actors)
- Empfohlen, aber nicht zwingend: `02-01-kunden-marken-profil` und `02-03-wettbewerber-marken-profil` (für die Touchpoint-Inventur mit eventuell schon erfassten TikTok-Usernames)

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

Folge `contracts.md` Abschnitt 1. Ermittle Drive-Folder-IDs:

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

### Schritt 1: Voraussetzungs-Check

Lies `wettbewerber/liste.md` aus Drive (`WETTBEWERBER_ID` → `find_by_name` + `read_text`). Wenn fehlt oder `status` nicht `bestaetigt`:

```
✗ wettbewerber/liste.md fehlt oder hat status: vorgeschlagen.
Bitte erst 02-02-wettbewerber-identifikation abschließen und die Liste bestätigen.
```

Lies optional `data/kunde.md` (Drive `DATA_ID`) und `wettbewerber/<slug>.md` (Drive `WETTBEWERBER_ID`), um TikTok-Usernames aus der Touchpoint-Inventur zu ziehen.

### Schritt 2: Akteurs-Liste und Profil-Match

Akteurs-Liste zusammensetzen:

1. **Kunde** aus `meta.json` (`kunde`, `website`, optional `kunden_slug`)
2. **Wettbewerber** aus `wettbewerber/liste.md`, alle drei Kategorien (kunde_genannt, regional, best_practice_ueberregional)

Pro Akteur den TikTok-Username ermitteln:

**Quellen-Priorisierung:**

1. **Touchpoint-Inventur**: Wenn `data/kunde.md` oder `wettbewerber/profile/<slug>.md` einen TikTok-Touchpoint enthält → direkt nutzen.
2. **Website-Scan**: Webseite des Akteurs prüfen (Footer, Social-Icons, Impressum) — TikTok-Link kann dort verlinkt sein.
3. **TikTok-Search via Apify**: `apify/tiktok-scraper` mit Such-Modus oder Profil-Such-Endpoint nutzen, Markenname als Query, Top-Treffer prüfen auf Namens-Match (siehe `reference/tiktok-tools-mapping.md`).
4. **Skip mit Hinweis**: Wenn nach allen drei Quellen **kein eindeutiger Match** vorliegt → diesen Akteur mit Status `kein_profil_gefunden` markieren, NICHT erraten.

Wichtig: TikTok-Usernames sind eindeutig und beginnen mit `@`. Speichere sie ohne `@` als Slug.

### Schritt 3: Branchen-Fit-Gate

Nach Schritt 2 zählt der Skill, wie viele Akteure ein erkennbares TikTok-Profil haben:

- **0 Akteure mit Profil** → Skill bricht ab mit kompakter Skip-Datei (`audits/tiktok-wettbewerb.md` mit `branchen_fit: gering` und 0 Datenpunkten), HTML-Report wird als Skip-Variante angelegt. Status-Update und Dashboard-Update trotzdem laufen lassen — der Stratege sieht, dass der Skill gelaufen ist und TikTok kein Thema ist.
- **1-2 Akteure mit Profil** → kompakter Lauf weiter, Branchen-Fit-Hinweis prominent.
- **>=3 Akteure mit Profil** → voller Audit-Lauf weiter.

Die Skip-Variante ist im Output-Schema klar abgegrenzt (siehe `reference/tiktok-output-schema.md`).

### Schritt 4: Profil-Daten erheben

Pro Akteur mit erkanntem TikTok-Profil:

- Apify-Actor: `clockworks/free-tiktok-scraper` oder `apify/tiktok-profile-scraper` (siehe `reference/tiktok-tools-mapping.md` für aktuelle Empfehlung und Fallback-Reihenfolge)
- Erhebung: Follower-Count, Following-Count, Likes-Gesamt, Bio-Text, Verifizierungs-Status, Anzahl Videos gesamt, Region/Sprache (falls vom Actor zurückgegeben), Profil-Bild-URL, externer Link aus Bio

Roh-JSON pro Akteur lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/tiktok-profile-<akteurs-slug>.json` — am Skill-Ende gzip-komprimiert nach Drive `assets/raw/` hochladen (siehe Schritt 12).

### Schritt 5: Video-Sample erheben (max. 30 pro Akteur)

Pro Akteur ein Video-Sample erheben. **Hard-Cap 30 Videos pro Akteur** — TikTok-Engagement ist so volatil (virale Hits mischen sich mit 200-View-Videos), dass ein größeres Sample diminishing returns hat und Apify-Compute teuer wird.

**Auswahl-Kriterien:**

- Zeitraum: letzte 6-12 Monate (Default 12 Monate, fällt auf 6 zurück wenn der Actor nicht mehr liefert)
- Wenn der Actor mehr als 30 Videos in dem Zeitraum zurückgibt: nimm die **neuesten 30**, nicht eine zufällige Stichprobe — Recency ist für TikTok-Strategie-Aussagen wichtiger als historische Tiefe
- Wenn weniger als 30 Videos im Zeitraum → alle nehmen, Coverage-Quote im Output ausweisen

**Pro Video erfasst:**

- Video-ID, Video-URL, Posting-Datum
- Video-Länge in Sekunden
- Views, Likes, Comments, Shares, Saves (falls verfügbar)
- Engagement-Rate = (Likes + Comments + Shares) / Views, gerundet auf zwei Nachkommastellen
- Caption-Text (full text, nicht gekürzt)
- Hashtags (extrahiert aus Caption)
- Music-Track: Titel, Künstler/Original-Sound-Owner, ist `original_sound` ja/nein, Music-ID falls verfügbar
- Duet/Stitch-Indikator: Ist das Video selbst ein Duet/Stitch von einem anderen Video?

Roh-JSON pro Akteur lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/tiktok-videos-<akteurs-slug>.json` — am Skill-Ende gzip-komprimiert nach Drive `assets/raw/` (siehe Schritt 12).

### Schritt 6: TikTok-Spezifika ableiten

Aus dem Video-Sample pro Akteur folgende TikTok-spezifische Aggregate berechnen:

**a) Trend-Sound-Nutzung**

- Anzahl der Videos im Sample, die einen nicht-eigenen Music-Track verwenden (d.h. `original_sound = false`)
- Anteil in Prozent
- Top-3 verwendete Tracks mit Häufigkeit
- Heuristik "Trend-Sound": Wenn ein Track in mehreren Wettbewerber-Samples auftaucht → starkes Trend-Sound-Signal; im Auffälligkeiten-Block ausweisen

**b) Duet/Stitch-Aktivität**

- Anzahl Videos im Sample, die als Duet oder Stitch markiert sind
- Anteil in Prozent
- Strategische Aussage: Akteure, die aktiv mit Duet/Stitch arbeiten, integrieren Community-Content — ist im Brand-Building-Kontext relevant

**c) Hashtag-Challenge-Teilnahme**

- Alle Hashtags aus dem Sample aggregieren
- Top-10 verwendete Hashtags pro Akteur
- Cross-Akteurs-Aggregat: Welche Hashtags tauchen bei mehreren Akteuren auf? → Branchen-relevante Hashtags / Challenges
- Bei Hashtags, die deutlich "Challenge-Form" haben (z.B. `#xyzchallenge`, `#xyztrend`) → in der Auffälligkeiten-Sektion explizit benennen

**d) Content-Pillars-Heuristik**

- Pro Akteur Cluster aus Caption-Schlüsselwörtern bilden (einfacher Ansatz: Top-Hashtags + häufigste Caption-Bigramme)
- 3-5 Cluster pro Akteur ableiten und benennen (z.B. "Produkt-Demo", "Behind-the-Scenes", "Educational", "User-Generated", "Trend-Aufgreifer")
- Diese sind Heuristik, nicht definitiv — im Output als `pillars_heuristik` kennzeichnen

**e) Top-3-Videos**

- Pro Akteur die drei Videos mit den höchsten Views
- Plus Engagement-Rate dieser Videos zur Einordnung (hohe Views + hohe ER vs. hohe Views + niedrige ER = nur viral, kein Engagement)

### Schritt 7: Aggregat-Analyse

Über alle Akteure hinweg:

- **Branchen-Median-Engagement-Rate**: Median über alle Video-ER-Werte (alle Akteure, alle Videos) als Benchmark
- **Posting-Frequenz**: Pro Akteur Videos pro Woche im erfassten Zeitraum
- **Aktivität-Status pro Akteur**: `aktiv` wenn >=1 Video in letzten 4 Wochen, `inaktiv_seit_X_wochen` sonst (X = Anzahl Wochen seit letztem Video)
- **Branchen-relevante Hashtags / Challenges**: Hashtags, die bei >=2 Akteuren im Top-10 auftauchen
- **Branchen-relevante Trend-Sounds**: Music-Tracks, die bei >=2 Akteuren auftauchen

### Schritt 8: Auffälligkeiten

Aus den Aggregaten die strategisch relevanten Beobachtungen ableiten. Mindestens 6 Auffälligkeits-Typen sind unterstützt — der Skill prüft jede und nimmt nur die zutreffenden in den Output auf:

1. **`kunde_kein_tiktok_profil`** — Kunde hat kein Profil, aber >=2 Wettbewerber sind aktiv → Empfehlung: Profil prüfen
2. **`kunde_inaktiv_seit_X_wochen`** — Kunde hat Profil, letztes Video ist >=8 Wochen alt, während Wettbewerber regelmäßig posten → Empfehlung: Aktivierung oder Profil-Pause-Entscheidung
3. **`kunde_engagement_unter_branchen_median`** — Kunden-Median-ER liegt deutlich (>30%) unter dem Branchen-Median → Empfehlung: Content-Strategie-Review
4. **`wettbewerber_viraler_hit`** — Mindestens ein Wettbewerber hat ein Video mit >100k Views im Sample → Empfehlung: das Video analysieren, Format/Hook ableiten
5. **`trend_sound_nutzung_diskrepanz`** — Branchen-relevante Trend-Sounds werden von Wettbewerbern genutzt, vom Kunden nicht → Empfehlung: Sound-Trends regelmäßig prüfen
6. **`hashtag_challenge_teilnahme`** — Wettbewerber nehmen an Branchen-relevanten Hashtag-Challenges teil, Kunde nicht → Empfehlung: Challenge-Monitoring
7. **`content_pillar_luecke_kunde`** — Pillars, die bei mehreren Wettbewerbern vorkommen, fehlen beim Kunden → Empfehlung: Pillar-Erweiterung prüfen

Pro Auffälligkeit: Akteurs-Bezug (welche Akteure betroffen), Daten-Belege (Zahlen aus dem Sample), Handlungsvorschlag in einem Satz.

### Schritt 9: `audits/tiktok-wettbewerb.md` schreiben

Format strikt nach `reference/tiktok-output-schema.md`. Markdown mit YAML-Frontmatter:

- **Frontmatter**: Skill-Metadaten, Recherche-Provenienz, Akteurs-Liste mit Profil-Match-Status, Branchen-Fit-Indikator, Sample-Coverage-Werte, Aggregate (Branchen-Median-ER, Branchen-relevante Hashtags, etc.), Auffälligkeiten-Liste
- **Body**: 
  - Übersicht (Anzahl Akteure mit/ohne Profil, Sample-Größe gesamt, Erhebungs-Zeitraum)
  - Profil-Matrix (alle Akteure nebeneinander mit Follower, Likes-Gesamt, Engagement-Rate-Median)
  - Pro Akteur eine Sektion mit Profil-Details, Video-Sample-Aggregat, TikTok-Spezifika, Top-3-Videos, Content-Pillars
  - Aggregate-Sektion (Branchen-Median, Branchen-Hashtags, Branchen-Sounds)
  - Auffälligkeiten als eigene Sektion
  - Lücken-Sektion (welche Akteure nicht gescraped werden konnten, mit Begründung)

### Schritt 10: CSVs schreiben

**`audits/tiktok-profile.csv`** — eine Zeile pro Akteur:

```
akteurs_slug, akteurs_name, typ, tiktok_username, profil_url, profil_status,
follower_count, following_count, likes_gesamt, videos_gesamt, verifiziert,
bio_text, externer_link, erhebungs_datum
```

**`audits/tiktok-videos.csv`** — eine Zeile pro Video im Sample:

```
akteurs_slug, video_id, video_url, posting_datum, laenge_sekunden,
views, likes, comments, shares, saves, engagement_rate,
caption, hashtags_csv, music_titel, music_kuenstler, ist_original_sound,
ist_duet, ist_stitch
```

Detaillierte Spalten-Definition in `reference/tiktok-output-schema.md`.

### Schritt 11: HTML-Report `reports/16-tiktok-wettbewerb.html`

Aus `reports/_shell.html` einen Bundle-Report bauen:

- `{{TITLE}}` → `TikTok-Wettbewerb · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · Social`
- `{{DISPLAY_NAME}}` → `TikTok-Wettbewerbsanalyse: KUNDE`
- `{{META_LINE}}` → `N Akteure · M Videos im Sample · Erhebung DATUM · Branchen-Fit: hoch/mittel/gering`
- `{{MAIN_CONTENT}}` →
  - **Branchen-Fit-Hinweis** prominent oben (Stat-Strip oder Suggestion-Block): "Branchen-Fit gering — TikTok als strategisches Nicht-Thema" wenn 0 Akteure aktiv; sonst nur dezenter Hinweis-Block
  - **Stat-Strip**: Anzahl Akteure mit Profil, Anzahl Akteure ohne Profil, Gesamt-Video-Sample, Branchen-Median-Engagement-Rate
  - **Sticky-TOC**: Übersicht, pro Akteur, Aggregate, Auffälligkeiten, Lücken
  - **Profil-Matrix**: HTML-Tabelle mit Akteuren als Zeilen, Spalten: Follower, Likes-Gesamt, Videos im Sample, Posting-Frequenz/Woche, Engagement-Rate-Median
  - **Pro Akteur** ein `details class="skill"`-Block, default zugeklappt: Profil-Daten, Top-3-Videos (mit Embed-Link oder Thumbnail-Hinweis), Content-Pillars, TikTok-Spezifika
  - **Aggregate-Sektion**: Branchen-Hashtags, Branchen-Sounds, Median-ER als visuelle Balken
  - **Auffälligkeiten-Block** prominent als `.suggestion`-Block, eine Karte pro Auffälligkeit mit klarer Handlungs-Empfehlung
  - **Lücken-Block** unten: nicht-gefundene Profile, Scrape-Fehler
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · TikTok-Wettbewerb`

Bei Skip-Variante (0 Akteure mit Profil): nur Branchen-Fit-Block und kurzer Hinweis im Body, keine Matrix.

### Schritt 12: Outputs nach Drive hochladen und Dashboard-Update

**Output-Uploads nach Drive**:

1. Aggregat-Markdown + CSVs → `AUDITS_ID`:
   ```bash
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "tiktok-wettbewerb.md" /tmp/tiktok-wettbewerb.md "text/markdown"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "tiktok-profile.csv" /tmp/tiktok-profile.csv "text/csv"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "tiktok-videos.csv" /tmp/tiktok-videos.csv "text/csv"
   ```
2. Roh-JSONs gzip-komprimiert nach Drive `assets/raw/` (Apify-Outputs koennen mehrere MB sein):
   ```bash
   RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
   for f in ~/.cache/reachx-mta/<slug>/raw/tiktok-*.json; do
     gzip -k "$f"
     python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
   done
   ```
3. HTML-Report `16-tiktok-wettbewerb.html` → `REPORTS_ID`.

**Dashboard-Update**: lies aktuelles `reports/index.html` aus Drive und aktualisiere via `upsert-text`:

- "Erledigt"-Sektion erweitern um `03-09-social-tiktok`
- Reports-Liste um `16-tiktok-wettbewerb.html` erweitern (bei Skip-Variante mit Badge "Branchen-Fit gering")
- Stat-Strip um TikTok-Coverage erweitern, falls Schema dafür ein Feld hat

### Schritt 13: `status.md` aktualisieren

Nach Regeln aus `contracts.md` Abschnitt 3:

- `03-09-social-tiktok` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, ggf. Skip-Hinweis ("Branchen-Fit gering, Skip-Variante geschrieben")
- `naechster_empfohlen`: nächster Social-Audit-Skill in der Sequenz, oder erster Synthese-Skill wenn alle Audits durch

### Schritt 14: Standard-Schlussformat im Chat

**Voller Lauf:**

```
✓ 03-09-social-tiktok abgeschlossen.

Outputs (auf Drive):
- audits/tiktok-wettbewerb.md — Aggregat mit Profilen, Video-Sample, Auffälligkeiten
- audits/tiktok-profile.csv — Profil-Matrix pro Akteur
- audits/tiktok-videos.csv — Video-Sample mit Engagement
- assets/raw/tiktok-profile-*.json.gz, assets/raw/tiktok-videos-*.json.gz — komprimierte Roh-Daten
- reports/16-tiktok-wettbewerb.html — visueller Report
Status aktualisiert in: status.md

Erhebungs-Statistik:
- Akteure gesamt:          N
- mit TikTok-Profil:       P
- ohne TikTok-Profil:      Q
- Video-Sample gesamt:     V
- Branchen-Median-ER:      E %
- Branchen-Fit:            hoch | mittel | gering

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- Kunde hat kein TikTok-Profil, 3 Wettbewerber sind aktiv
- Wettbewerber X hat viralen Hit mit 240k Views — Format analysieren
- Trend-Sound "..." wird von 2 Wettbewerbern genutzt, Kunde nicht

[Wenn Lücken:]
ℹ Lücken:
- Wettbewerber Y: kein eindeutiger TikTok-Match gefunden — manuell prüfen

Nächste Schritte:
1. [nächster Audit-Skill oder Synthese-Skill] — [Begründung]
2. (parallel möglich) [...] — [...]

Sag mir, welcher als nächster.
```

**Skip-Variante (0 Akteure mit Profil):**

```
✓ 03-09-social-tiktok abgeschlossen (Skip-Variante).

Ergebnis: Branchen-Fit gering — kein Akteur (weder Kunde noch Wettbewerber) hat ein erkennbares TikTok-Profil.
TikTok ist für diese MTA ein strategisches Nicht-Thema.

Outputs (auf Drive):
- audits/tiktok-wettbewerb.md — Skip-Dokumentation mit Begründung
- reports/16-tiktok-wettbewerb.html — Skip-Variante des Reports
Status aktualisiert in: status.md

Nächste Schritte:
1. [nächster Skill] — [Begründung]

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/tiktok-tools-mapping.md` — Apify-Actor-Empfehlungen, Fallback-Reihenfolge, Profil-Match-Methodik, bekannte Edge Cases der TikTok-Scraper
- `reference/tiktok-output-schema.md` — Output-Format für `audits/tiktok-wettbewerb.md` (Frontmatter-Schema + Body-Struktur), CSV-Spalten-Definitionen, Skip-Variante-Schema

## Edge Cases

- **Akteur hat mehrere TikTok-Profile** (z.B. Hauptmarke + Sub-Brand): Nimm das Profil mit dem klarsten Markennamen-Match. Falls beide gleich relevant: nur eines wählen und im Body als Hinweis "Akteur hat zusätzliches Profil @xyz" dokumentieren.

- **Profil ist privat oder gelöscht**: Status `profil_privat` oder `profil_geloescht`. Keine Daten erheben, im Lücken-Block dokumentieren.

- **Profil hat 0 Videos im Zeitraum**: Status `profil_inaktiv`, Profil-Daten trotzdem erfassen (Follower etc.), aber Video-Sample leer.

- **Apify-Actor liefert keine Engagement-Daten** (manche Actor-Versionen lassen Comments/Shares weg): Mit den verfügbaren Feldern arbeiten, ER nur berechnen wenn mindestens Likes und Views vorhanden. Coverage-Quote pro Feld im Frontmatter ausweisen.

- **Sehr großer Akteur** (z.B. Wettbewerber mit 10 Mio. Follower und 500+ Videos): Hard-Cap 30 Videos bleibt — größere Samples helfen nicht für Strategie-Aussagen und kosten unnötig Apify-Compute.

- **Music-Track-Daten unvollständig**: Wenn der Actor Music-IDs nicht liefert, mit Titel+Künstler arbeiten. Trend-Sound-Cross-Akteur-Vergleich basiert dann auf String-Match (case-insensitive, normalisierte Whitespace).

- **Hashtag-Challenge-Detection unsicher**: Wenn unklar ist, ob ein Hashtag eine offizielle Challenge oder nur ein populärer Tag ist → konservativ als "Trend-Hashtag" labeln, nicht als "Challenge". Strategen-Disambiguation im Body.

- **Apify-Token fehlt**: Klare Fehlermeldung, kein Fallback (TikTok ist ohne Apify praktisch nicht scrape-bar). Skill bricht ab mit Setup-Hinweis.

- **Skip-Variante während eines aktiven Laufs erkennen**: Wenn nach Schritt 2 plötzlich 0 Profile übrig bleiben (z.B. weil alle Match-Versuche fehlschlagen), trotzdem die Skip-Variante ordentlich zu Ende schreiben — nicht abbrechen ohne Output.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown + YAML-Frontmatter Hybrid-Format
- Standard-Schlussformat im Chat (zwei Varianten: voller Lauf / Skip)
- `status.md` und Dashboard werden in jedem Lauf aktualisiert, auch bei Skip
- HTML-Report basiert auf `reports/_shell.html` (aus Drive)
- Engagement-Rate-Skala: (Likes + Comments + Shares) / Views, als Dezimal (0.057 = 5,7 %) im CSV, als Prozent im Markdown-Body
- Roh-JSON-Caches gehören gzip-komprimiert in Drive `assets/raw/`, lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/`
- Branchen-Fit-Indikator (`hoch | mittel | gering`) ist Pflichtfeld im Frontmatter, auch bei vollem Lauf
