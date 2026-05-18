---
name: 03-13-social-reddit-fit-check
description: Prueft den Reddit-Marketing-Fit als Kanal fuer eine MTA - keine klassische Wettbewerbsanalyse, weil Marken auf Reddit selten eigene Profile mit Reach haben. Baut ein Subreddit-Inventar zur Branche (Mitglieder, Posts/Tag, Sprache, Moderations-Strenge), erhebt Marken-Erwaehnungen fuer Kunde und Top-3-WBs mit Sentiment, analysiert Themen-Tiefe in Top-Subreddits und berechnet einen Fit-Score 0-100 ueber vier Achsen (Community-Aktivitaet, Brand-Reception, Kommerz-Toleranz, Format-Tauglichkeit). Output ist audits/reddit-fit.md plus reddit-subreddits.csv plus reddit-erwaehnungen.csv plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Reddit als Kanal bewerten will - auch bei "Reddit-Check", "Reddit-Marketing-Fit", "Ist Reddit ein Kanal fuer uns", "Subreddits fuer die Branche", "Reddit-Erwaehnungen", "Reddit-Audit", "Community-Recherche Reddit". Setzt 01-01-mta-projekt-init voraus; Branchen-Fit-Gate skippt B2B-Industrie/Versicherung/Hausverwaltung.
---

# Reddit-Marketing-Fit-Check

Stufe-3-Social-Audit. **Wichtige Besonderheit:** Reddit ist keine Standard-Wettbewerber-Analyse wie Instagram, TikTok oder Pinterest. Marken haben dort selten eigene Profile mit Reach — Reddit ist Community-driven, die Diskussion findet in Subreddits statt. Daher prueft dieser Skill den **Marketing-Fit fuer Reddit als Kanal**, nicht die Wettbewerber-Aktivitaet.

Der Skill liefert vier Bausteine:

1. **Subreddit-Inventar** fuer die Branche (Mitglieder, Posts/Tag, Sprache, Moderations-Strenge)
2. **Marken-Erwaehnungen** fuer Kunde + Top-3-Wettbewerber (letzte 6 Monate, Sentiment-Klassifikation, Top-5-Threads)
3. **Themen-Diskussions-Tiefe** in den Top-Subreddits (Pain-Points der Community, Tonalitaet)
4. **Reddit-Marketing-Fit-Score** (0-100) ueber vier Achsen + Strategie-Empfehlung `aktiv_empfohlen | beobachtung_empfohlen | nicht_empfohlen`

Drei Output-Ebenen:

1. **Aggregat-Markdown** `audits/reddit-fit.md` — Subreddit-Inventar, Marken-Erwaehnungen, Themen, Fit-Score, Empfehlung
2. **Subreddits-CSV** `audits/reddit-subreddits.csv` — eine Zeile pro Top-Subreddit mit Metriken
3. **Erwaehnungen-CSV** `audits/reddit-erwaehnungen.csv` — eine Zeile pro Erwaehnung × Akteur × Thread
4. **HTML-Report** `reports/X-reddit-fit.html` — Fit-Score-Visualisierung, Top-Subreddits-Karten, Erwaehnungen-Tabelle

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

## Branchen-Fit-Gate — wichtiger Vorab-Hinweis

Reddit ist nicht fuer jede Branche relevant. Stark Reddit-affine Branchen: Tech, Gaming, B2B-SaaS, E-Commerce mit Produkt-Bewertungen, Finanzen/Krypto, Hobby-Communities. Schwach Reddit-affine Branchen: Hausverwaltung, Versicherungen, regionale Handwerker, B2B-Industrie-Maschinenbau, Steuerberatung, Recht, lokale Dienstleister.

**Verhalten dieses Skills:**

- Wenn die initiale Branchen-Recherche (Schritt 3) **0 relevante Subreddits** mit >1000 Mitgliedern und >0.5 Posts/Tag findet → automatischer Skip mit Hinweis-Output, `branchen_fit_reddit: gering` und Empfehlung "Reddit als Kanal ueberspringen". Kein voller Erwaehnungs-Scrape, kein Themen-Scrape.
- Wenn **1-3 relevante Subreddits** existieren → kompakter Lauf mit voller Erwaehnungs- und Themen-Analyse, Fit-Score kann trotzdem niedrig ausfallen.
- Bei **>=4 relevanten Subreddits** → voller Audit-Lauf.

Schwelle ist im Output und im Schluss-Format explizit dokumentiert.

## Wann triggern

- "Reddit-Check"
- "Reddit-Marketing-Fit"
- "Ist Reddit ein Kanal fuer uns"
- "Subreddits fuer die Branche [BRANCHE]"
- "Reddit-Erwaehnungen pruefen"
- "Reddit-Audit"
- "Community-Recherche Reddit"
- "Pruefe Reddit"
- "Brand-Mentions auf Reddit"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA registriert, `meta.json` im Drive-MTA-Root
- **Apify-Zugang (Pflicht)** — Actor-Auswahl in `reference/reddit-tools-mapping.md` (mit `zuletzt_getestet`-Datum und `status`). Credential-Prüfung: ausschließlich `[ -n "$APIFY_TOKEN" ]` — kein Scannen von `~/.zshrc` o. ä. (contracts.md Abschnitt 11). Vor dem ersten echten Scrape Apify-Health-Check via `mcp__apify__fetch-actor-details` für den verwendeten Actor: bei `Session ID not found` sofort abbrechen und Reconnect-Hinweis ausgeben, statt alle Akteure einzeln scheitern zu lassen.
- **Reddit als GEO-/Discovery-Hebel:** Reddit ist nicht nur ein Leadgen-Kanal — relevante Subreddits sind zunehmend Quellen, auf die LLMs (ChatGPT, Perplexity, Gemini) in ihren Antworten verweisen. Bei der Auswertung der Subreddit-Inventur daher ergänzend prüfen: Werden in den Top-Subreddits Markennamen, Ratgeber-Themen oder Produkt-Kategorien diskutiert, auf die LLMs typischerweise verweisen? Wenn ja: `geo_hebel_relevant: true` im Frontmatter und gesonderte "GEO-Kopplung"-Sektion im Fit-Score-Output (als optionale fünfte Bewertungsachse, nur wenn ein positiver Befund vorliegt).
- Empfohlen: `wettbewerber/liste.md` (Drive) mit `status: bestaetigt` — sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` (Drive) mit Portfolio und USP-Beschreibungen — daraus zieht der Skill Subreddit-Such-Keywords
- Hinweis: Reddit-API direkt ist rate-limit-anfaellig — Skill nutzt Apify-Actors (siehe `reference/reddit-tools-mapping.md`)

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

Folge `contracts.md` Abschnitt 1. Ermittle Drive-Folder-IDs aus `meta.json`:

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

Wenn `get-mta` nichts liefert:

```
✗ Kein MTA-Projekt gefunden.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

### Schritt 1: Voraussetzungs-Check

Lies `wettbewerber/liste.md` aus Drive (`WETTBEWERBER_ID` via `find_by_name` + `read_text`). Wenn vorhanden mit `status: bestaetigt` → Modus **Voll**; sonst → Modus **Kunden-only** mit Hinweis.

Pruefe Apify-Zugang. Bei fehlendem Zugang: Abbruch mit Hinweis.

### Schritt 2: Such-Keyword-Set zusammenstellen

Aus den vorhandenen Inputs Such-Keywords fuer Subreddit-Recherche ableiten:

1. **Branche** aus `meta.json` (`branche`-Feld) — z. B. "B2B-SaaS", "Maschinenbau", "Bauhandwerk"
2. **Portfolio-Begriffe** aus `data/kunde.md` (Drive `DATA_ID`, wenn vorhanden) — Produktkategorien, Service-Begriffe
3. **Marken-Namen** Kunde + Top-3-Wettbewerber (aus `liste.md` im Drive `WETTBEWERBER_ID`, Kategorie `kunde_genannt` priorisiert)
4. **Synonyme/Alternativ-Bezeichnungen** der Branche (deutsch + englisch) — wichtig, weil viele Subreddits englischsprachig sind

Beispiel-Set fuer einen Maler-Betrieb:
- Branchen-Keywords: "Maler", "Malerei", "Streichen", "painters", "painting", "DIY paint"
- Portfolio-Keywords: "Fassade", "Innenraum", "Tapezieren"
- Subreddit-Kandidaten daraus: `r/Malerei`, `r/painting`, `r/DIY`, `r/HomeImprovement`, `r/Heimwerken`, `r/de_IAmA` etc.

Such-Keyword-Set lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/reddit-such-keywords.json` fuer Reproduzierbarkeit — am Skill-Ende gzip-komprimiert nach Drive `assets/raw/` (siehe Schritt 13).

### Schritt 3: Subreddit-Inventar aufbauen

Pro Keyword via Apify (`apify/reddit-scraper` im Such-Modus oder dedizierter Subreddit-Search-Endpoint, siehe `reference/reddit-tools-mapping.md`) Subreddit-Kandidaten suchen:

1. **Such-Anfrage** pro Keyword: Top-20-Subreddits nach Relevanz
2. **Pro Kandidat extrahieren**:
   - `subreddit_name` (mit `r/`-Prefix)
   - `subreddit_url`
   - `mitglieder_anzahl` (subscribers)
   - `posts_pro_tag` (avg der letzten 30 Tage)
   - `sprache_dominant`: `de | en | mixed | unbekannt` (Heuristik: aus Sidebar-Description + sample der Top-10-Posts)
   - `nsfw`: bool
   - `moderations_strenge`: `streng | mittel | locker | unbekannt` (Heuristik: aus Sidebar-Regeln — viele Regeln + explizite Anti-Werbung-Regel = `streng`; siehe `reference/reddit-tools-mapping.md`)
   - `sidebar_description` (gekuerzt auf 300 Zeichen)
   - `relevanz_score` 0-1 (Skill-Heuristik: Keyword-Match × Mitglieder-Skalierung × Aktivitaets-Faktor)
3. **Deduplizieren** ueber `subreddit_name`
4. **Filtern**: nur Subreddits mit >=1000 Mitgliedern UND >=0.5 Posts/Tag UND nicht NSFW

**Branchen-Fit-Gate (Skip-Logik):**

Nach dem Filtern zaehlen, wie viele Subreddits uebrig bleiben:

- **0 Subreddits** → Skip-Variante (siehe Schritt 11): kompakter Output, Fit-Score 0, Empfehlung `nicht_empfohlen`, kein Erwaehnungs- und Themen-Scrape. Status-Update und Dashboard-Update trotzdem.
- **1-3 Subreddits** → Kompakt-Lauf weiter (alle Schritte, aber Themen-Tiefe nur fuer diese 1-3).
- **>=4 Subreddits** → Voll-Lauf, Top-10 nach `relevanz_score` fuer Themen-Tiefe.

Roh-Daten lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/reddit-subreddits.json` — Upload nach Drive am Skill-Ende (Schritt 13).

### Schritt 4: Existenz-Check Output

Via `list-children` auf `AUDITS_ID` pruefen, ob `reddit-fit.md`, `reddit-subreddits.csv` oder `reddit-erwaehnungen.csv` bereits im Drive `audits/`-Folder existieren: fragen (ueberschreiben / Backup-und-neu / abbrechen).

### Schritt 5: Marken-Erwaehnungen erheben

Fuer **Kunde + Top-3 Wettbewerber** (sortiert: zuerst kunde_genannt, dann regional, dann ueberregional, alle aus `liste.md`).

Pro Akteur via Apify (`apify/reddit-search-scraper`):

1. **Such-Anfrage**: Markenname + Synonyme/Schreibvarianten (z. B. "Aufmaster", "auf-master", "aufmaster.de")
2. **Zeitfilter**: letzte 6 Monate
3. **Sortierung**: Relevanz + neu
4. **Hard-Cap**: max 50 Erwaehnungen pro Akteur (sonst Apify-Compute teuer)
5. **Pro Treffer extrahieren**:
   - `thread_id`, `thread_url`, `thread_title`
   - `subreddit` (in welchem Subreddit?)
   - `erwaehnung_typ`: `post | comment`
   - `erwaehnung_text` (Original-Auszug, max 500 Zeichen)
   - `autor_username` (oder `[deleted]`)
   - `erstellt_iso`
   - `score` (Upvotes minus Downvotes)
   - `kommentare_count` (nur bei Posts)
   - `sentiment` (siehe Schritt 6)
6. **Roh-Daten** lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/reddit-erwaehnungen-AKTEURSSLUG.json` — Upload nach Drive am Skill-Ende (Schritt 13)

Wenn fuer einen Akteur **0 Erwaehnungen** → Auffaelligkeit `wettbewerber_aktiv_kunde_unsichtbar` (bei Kunde) bzw. `kein_signal_wb_SLUG` (bei WBs) in Schritt 8.

### Schritt 6: Sentiment-Klassifikation pro Erwaehnung

**Wichtig: reproduzierbare Kriterien, nicht reine LLM-Bauchgefuehl-Skala.** Definiert in `reference/reddit-tools-mapping.md` Abschnitt "Sentiment-Klassifikation". Hier die Kernregeln:

Fuer jede Erwaehnung wird `sentiment` aus drei Signalen abgeleitet:

1. **Lexikon-Signal**: Liste pos/neg Marker-Woerter (deutsch + englisch) — z. B. pos: "recommend", "empfehle", "love", "klasse", "Top"; neg: "scam", "ripoff", "uebel", "Finger weg", "Schrott"
2. **Score-Signal**: Reddit-Score der Erwaehnung — `score >= 10` mit positivem Lexikon = stark positiv; `score <= -3` = stark negativ
3. **Kontext-Signal**: LLM-Pass auf die 500-Zeichen-Erwaehnung mit definierten Kategorien (siehe unten), NICHT freie Bauchgefuehl-Klassifikation

Klassifikations-Stufen:

- `positiv` — pos Lexikon-Marker + Score >= 5, oder LLM-Klasse "Empfehlung/Lob" mit Konfidenz hoch
- `neutral` — Erwaehnung ohne Wertung (z. B. Vergleichs-Frage, Aufzaehlung)
- `negativ` — neg Lexikon-Marker + Score >= 0, oder LLM-Klasse "Beschwerde/Warnung" mit Konfidenz hoch
- `gemischt` — sowohl pos als auch neg Marker im Text
- `unklar` — kein klares Signal, LLM-Konfidenz niedrig

LLM-Pass-Prompt-Template fuer reproduzierbares Verhalten in `reference/reddit-tools-mapping.md`.

Pro Akteur dann Aggregate berechnen:

- Anzahl Erwaehnungen gesamt
- Verteilung pos / neutral / neg / gemischt / unklar (Prozent)
- Top-5-Threads nach Score (mit Sentiment-Label, Subreddit, Auszug)
- Beteiligte Subreddits (wo wird der Akteur diskutiert?)

### Schritt 7: Themen-Diskussions-Tiefe in Top-Subreddits

Fuer die **Top-N nach Relevanz** (N = 10 bei Voll-Lauf, 1-3 bei Kompakt-Lauf):

1. Pro Subreddit die **letzten 30 Top-Posts** scrapen via `apify/reddit-scraper` (Subreddit-Modus, `sort: top`, `time: month`)
2. **Pro Post extrahieren**: Titel, Score, Anzahl Kommentare, Auszug Body, Top-3-Kommentare (fuer Tiefe)
3. **Themen-Cluster heuristisch ableiten** (analog Content-Pillars bei Instagram/TikTok — Token-Co-Occurrence ueber Titel + Top-Body-Auszuege):
   - 3-5 Themen-Cluster pro Subreddit
   - Pro Cluster: Label (Top-3-Tokens), Anzahl Posts, typische Pain-Points (Frage-Pattern "How do I...", "Hat jemand schon mal...", "Warum funktioniert X nicht?")
4. **Tonalitaet-Klassifikation pro Subreddit** (4 Stufen, definiert in `reference/reddit-tools-mapping.md`):
   - `snarky` — viel Sarkasmus, viele Memes, Anti-Establishment
   - `ernsthaft` — Fach-Diskussion, ausfuehrliche Antworten, wenig Memes
   - `hilfsbereit` — viele Frage-Antwort-Threads, gute Engagement-Quote
   - `kommerz_allergisch` — explizite Anti-Werbung-Regeln, Hostile zu Markenkonten
5. **Pain-Point-Signale extrahieren**: 3-5 Top-Pain-Points pro Subreddit (Frage-Pattern-Aggregation), lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/reddit-themen-SUBREDDIT.json` — Upload nach Drive am Skill-Ende (Schritt 13)

### Schritt 8: Reddit-Marketing-Fit-Score berechnen

Vier-Achsen-Score 0-100, gewichtet. Formel in `reference/fit-score-formel.md` (Pflicht-Read fuer Skill — die Achsen-Gewichte koennen ueber Branchen-Defaults angepasst werden).

**Vier Achsen:**

1. **Community-Aktivitaet (Gewicht 30%)** — `min(100, log(median_mitglieder_top10) × 10 + median_posts_pro_tag × 5)`
2. **Brand-Reception (Gewicht 30%)** — `100 × (pos_anteil_kunde - 0.5 × neg_anteil_kunde) + (40 wenn erwaehnungen >= 10, sonst Skalierung)`. Wenn 0 Erwaehnungen → 30 (neutral, weil unbekannt)
3. **Kommerz-Toleranz (Gewicht 20%)** — `100 × (1 - anteil_kommerz_allergisch_top10) × moderations_locker_faktor`
4. **Format-Tauglichkeit (Gewicht 20%)** — `100 × (1 - sprache_kollision_faktor) × hilfsbereit_tonalitaet_faktor`. Reddit-Marketing funktioniert primaer organisch (AMA, Authentic Story, Helpful Content) — kaum Paid. Faktor straft, wenn Sprache nicht passt oder Subreddits snarky/kommerz_allergisch sind.

**Score-Bands (siehe `reference/fit-score-formel.md`):**

- `0-30` → Empfehlung `nicht_empfohlen`
- `31-55` → Empfehlung `beobachtung_empfohlen`
- `56-100` → Empfehlung `aktiv_empfohlen`

Zusammenfassung pro Achse mit konkretem Zahlenwert und Erlaeuterungs-Satz im Output.

### Schritt 9: Auffaelligkeiten

Mindestens 6 Typen, der Skill prueft jede und nimmt nur zutreffende in den Output:

| Typ | Ausloeser | Beispiel |
|---|---|---|
| `branchen_kein_reddit_kontext` | Schritt 3 findet 0 relevante Subreddits | "Branche [BRANCHE] hat keinen relevanten Reddit-Kontext — Reddit als Kanal ueberspringen" |
| `negativer_sentiment_haeufung` | Kunden-neg-Anteil >= 40% bei >=5 Erwaehnungen | "Kunde hat 60% negative Erwaehnungen — PR-Fall, kein Marketing-Hebel, vor Aktivierung Reputations-Management" |
| `wettbewerber_aktiv_kunde_unsichtbar` | Mind. 1 WB hat >=10 Erwaehnungen, Kunde hat 0 | "Wettbewerber [WB] hat 23 Erwaehnungen, Kunde 0 — Sichtbarkeits-Chance" |
| `subreddit_kommerz_allergisch` | Top-Subreddit hat Tonalitaet `kommerz_allergisch` UND `moderations_strenge: streng` | "Top-Subreddit r/[NAME] ist explizit anti-Marketing — nur AMA oder authentic Story, keine direkte Werbung" |
| `viraler_thread_chance` | Top-Subreddit hat in letzten 30 Tagen Post mit Score >=500 zum Branchen-Thema, kein Marken-Beitrag dabei | "Thread r/[NAME] mit 800 Upvotes diskutiert [PAIN-POINT] — offen fuer authentischen Marken-Beitrag" |
| `sprache_kollision` | Kunde ist deutsche Marke, aber >=70% der Top-Subreddits sind englischsprachig | "Top-Subreddits ueberwiegend englisch — Reichweite des deutschen Kunden begrenzt, ggf. eigenes deutschsprachiges Engagement-Feld pruefen" |
| `pain_point_signal` | Pain-Point aus Themen-Analyse matched Portfolio-USP des Kunden | "Pain-Point '[PAIN]' wird in r/[NAME] regelmaessig diskutiert — Portfolio-USP '[USP]' passt direkt → Content-Anker" |

Pro Auffaelligkeit: Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Akteure/Subreddits.

### Schritt 10: CSVs schreiben

**`audits/reddit-subreddits.csv`** — eine Zeile pro Top-Subreddit (alle, die das Filter aus Schritt 3 passieren).

Spalten:

```
subreddit_name, subreddit_url, mitglieder_anzahl, posts_pro_tag,
sprache_dominant, nsfw, moderations_strenge, tonalitaet,
relevanz_score, themen_cluster_top3, pain_points_top3,
in_top10, datenstand_iso
```

**`audits/reddit-erwaehnungen.csv`** — eine Zeile pro Erwaehnung × Akteur × Thread.

Spalten:

```
akteurs_slug, akteurs_typ, akteurs_name,
thread_id, thread_url, thread_title, subreddit,
erwaehnung_typ, erwaehnung_text_auszug, autor_username,
erstellt_iso, score, kommentare_count,
sentiment, sentiment_konfidenz, datenstand_iso
```

`erwaehnung_text_auszug`: erste 200 Zeichen. Volltext liegt im Roh-JSON.

Detaillierte Spalten-Definition in `reference/reddit-output-schema.md`.

### Schritt 11: Aggregat-Markdown `audits/reddit-fit.md`

Markdown mit YAML-Frontmatter. Vollstaendiges Format in `reference/reddit-output-schema.md`.

Frontmatter enthaelt:

- Skill-Metadaten, Quellen-Provenienz
- Modus: `voll | kompakt | skip`
- `branchen_fit_reddit: hoch | mittel | gering`
- `fit_score: 0-100`
- `empfehlung: aktiv_empfohlen | beobachtung_empfohlen | nicht_empfohlen`
- Achsen-Werte (4 Achsen mit Einzel-Score)
- Subreddits-Top-10-Snapshot
- Akteurs-Erwaehnungs-Aggregate
- Auffaelligkeiten

Body-Struktur:

1. **Uebersicht & Empfehlung** — Fit-Score, Empfehlung, Begruendung in 3-4 Saetzen
2. **Branchen-Fit-Block** (prominent bei `gering`)
3. **Subreddit-Inventar** — Top-10-Tabelle mit Mitgliedern, Posts/Tag, Sprache, Moderation, Tonalitaet
4. **Marken-Erwaehnungen** — pro Akteur: Anzahl, Sentiment-Verteilung, Top-5-Threads
5. **Themen & Pain-Points** — pro Top-Subreddit: 3-5 Themen-Cluster, dominante Pain-Points, Tonalitaet
6. **Fit-Score-Aufschluesselung** — vier Achsen mit Einzel-Wert und Erlaeuterung
7. **Auffaelligkeiten** als Liste
8. **Strategie-Empfehlung** — konkrete Handlungs-Pfade (z. B. "AMA in r/X, organischer Content in r/Y, kein Paid")

Bei Skip-Variante: nur Block 1, 2 und Auffaelligkeiten `branchen_kein_reddit_kontext`.

### Schritt 12: HTML-Report `reports/X-reddit-fit.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html` aus Drive (`REPORTS_ID` via `find_by_name` + `read_text`) — `X` = naechste freie Report-Nummer, siehe `reports/index.html` (aus Drive).

- `{{TITLE}}` → `Reddit-Marketing-Fit · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · Social`
- `{{DISPLAY_NAME}}` → `Reddit-Marketing-Fit-Check: KUNDE`
- `{{META_LINE}}` → `Fit-Score VALUE · Empfehlung EMPF · N Subreddits · M Erwaehnungen · Datenstand DATUM`
- `{{MAIN_CONTENT}}` →
  - **Fit-Score-Hero** prominent oben: grosser Score-Wert, Empfehlungs-Badge (`.badge.stark | .badge.mittel | .badge.schwach`)
  - **Branchen-Fit-Banner** (bei `gering` prominent)
  - **Stat-Strip**: Subreddits-Anzahl, Erwaehnungen-gesamt, Sentiment-Verteilung-Kunde, Top-Reach-Subreddit
  - **Sticky-TOC** zu allen Sektionen
  - **Fit-Score-Aufschluesselung** als 4-Achsen-Visualisierung (Balken pro Achse mit Gewicht)
  - **Subreddits-Top-10** als Karten-Grid mit Stats (Mitglieder, Posts/Tag, Moderation, Tonalitaet-Badge)
  - **Marken-Erwaehnungen-Tabelle**: Akteur × Anzahl × Sentiment-Verteilung × Top-Thread
  - **Themen & Pain-Points** als `details.skill`-Bloecke pro Subreddit
  - **Auffaelligkeiten** als `.suggestion`-Block, eine Karte pro Auffaelligkeit
  - **Strategie-Empfehlung** als Hervorhebungs-Block
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · Reddit-Fit-Check`

Bei Skip-Variante: nur Fit-Score-Hero (Score 0, Badge `schwach`), Branchen-Fit-Banner, Auffaelligkeits-Block `branchen_kein_reddit_kontext`, keine Subreddit-Karten.

### Schritt 13: Outputs nach Drive hochladen, Dashboard-Update, status.md

**Output-Uploads nach Drive** (in dieser Reihenfolge):

1. Aggregat-Markdown + CSVs → `AUDITS_ID`:
   ```bash
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "reddit-fit.md" /tmp/reddit-fit.md "text/markdown"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "reddit-subreddits.csv" /tmp/reddit-subreddits.csv "text/csv"
   python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "reddit-erwaehnungen.csv" /tmp/reddit-erwaehnungen.csv "text/csv"
   ```
2. Roh-JSONs (Apify-Outputs koennen sehr gross sein, daher gzip Pflicht) nach Drive `assets/raw/`:
   ```bash
   RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
   for f in ~/.cache/reachx-mta/<slug>/raw/reddit-*.json; do
     gzip -k "$f"
     python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
   done
   ```
3. HTML-Report `X-reddit-fit.html` → `REPORTS_ID`.

**status.md-Update** (aus Drive lesen, aktualisieren, via `upsert-text` zurueckschreiben):

- `03-13-social-reddit-fit-check` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Modus (`voll | kompakt | skip`), Fit-Score, Empfehlung
- Reports-Liste um `X-reddit-fit.html` erweitern (bei Skip-Variante mit Badge "Branchen-Fit gering")
- Stat-Strip aktualisieren
- `naechster_empfohlen`: passender naechster Skill (z. B. `04-02-kanal-chancen-analyse` wenn genug Audits durch, sonst naechster Social-Skill)

### Schritt 14: Standard-Schlussformat im Chat

**Voller Lauf:**

```
✓ 03-13-social-reddit-fit-check abgeschlossen.

Outputs (auf Drive):
- audits/reddit-fit.md — Aggregat mit Subreddit-Inventar, Erwaehnungen, Fit-Score
- audits/reddit-subreddits.csv — Top-Subreddits mit Metriken (N Eintraege)
- audits/reddit-erwaehnungen.csv — Erwaehnungen-Datenbasis (M Eintraege)
- assets/raw/reddit-*.json.gz — komprimierter Roh-Cache
- reports/X-reddit-fit.html — Strategen-Report mit Fit-Score-Visualisierung
Status aktualisiert in: status.md

Reddit-Lage:
- Branchen-Fit:                hoch | mittel | gering
- Top-Subreddits identifiziert: N
- Erwaehnungen Kunde:          K (Sentiment: P pos / N neutral / Q neg)
- Erwaehnungen WBs gesamt:     W
- Fit-Score:                   SCORE / 100
- Empfehlung:                  aktiv_empfohlen | beobachtung_empfohlen | nicht_empfohlen

[Wenn Auffaelligkeiten:]
⚠ Reddit-Insights:
- (1-3 Top-Auffaelligkeiten)

[Wenn negativer_sentiment_haeufung:]
⚠ Reputations-Warnung
- N% negative Erwaehnungen — vor Aktivierung Reputations-Management.

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestaetigt — Erwaehnungs-Analyse nur fuer den Kunden.

Naechste Schritte:
1. 04-02-kanal-chancen-analyse — wenn 4-5 Audits durch sind, Reddit-Score fliesst in das Ranking
2. (parallel moeglich) [naechster Social-Skill] — wenn weitere Kanaele zu pruefen

Sag mir, welcher als naechster.
```

**Skip-Variante (Branchen-Fit gering, 0 relevante Subreddits):**

```
✓ 03-13-social-reddit-fit-check abgeschlossen (Skip-Variante).

Ergebnis: Branchen-Fit gering — fuer Branche BRANCHE wurden keine relevanten Subreddits identifiziert.
Reddit ist fuer diese MTA ein strategisches Nicht-Thema.

Outputs (auf Drive):
- audits/reddit-fit.md — Skip-Dokumentation mit Begruendung und Recherche-Trace
- reports/X-reddit-fit.html — Skip-Variante des Reports
Status aktualisiert in: status.md

Fit-Score: 0 / 100 · Empfehlung: nicht_empfohlen

Naechste Schritte:
1. [naechster Skill] — [Begruendung]

Sag mir, welcher als naechster.
```

## Bundled Resources

- `reference/reddit-tools-mapping.md` — Apify-Actor-Optionen (Reddit-Scraper, Reddit-Search-Scraper, Reddit-Comments-Scraper), Subreddit-Such-Heuristik, Sprache-Erkennung, Moderations-Strenge-Heuristik, **Sentiment-Klassifikations-Regeln** (Lexikon + Score + LLM-Pass mit definierten Kategorien), Tonalitaets-Klassifikation (snarky/ernsthaft/hilfsbereit/kommerz_allergisch)
- `reference/fit-score-formel.md` — vier Achsen mit Gewichten, exakte Formel pro Achse, Score-Bands, Branchen-Default-Anpassungen
- `reference/reddit-output-schema.md` — Markdown-Frontmatter-Schema, beide CSV-Schemas mit Spalten-Definition, Skip-Variante-Schema, Validierungs-Regeln

## Edge Cases

- **Marken-Name kollidiert mit Common-Word** (z. B. Kunde heisst "Strom" oder "Boost"): Such-Set wird mit Branchen-Disambiguator erweitert ("Strom Energie" statt nur "Strom"). Wenn nach Disambiguation immer noch >100 Treffer mit Mehrheit Off-Topic → Hinweis `marken_name_kollidiert` in Auffaelligkeiten, manuelle Pruefung empfohlen.

- **Kunde hat keinen offiziellen Reddit-Account, aber wird oft erwaehnt**: das ist der Standard-Fall fuer Reddit. Skill macht **keine Account-Suche** wie bei Instagram/TikTok — Erwaehnungs-Analyse ist der Kern.

- **Subreddit privat oder geschlossen** (`r/CommunityName` ist private): Apify liefert leeres Result. Skill markiert `subreddit_unzugaenglich: true`, im Output Hinweis.

- **Subreddit existiert nicht / falsche Schreibweise**: Apify-Search liefert keinen Treffer fuer den exakten Namen. Skill probiert Such-Variante (mit/ohne Bindestrich, Singular/Plural).

- **Massive Engagement-Verteilung (Power-Law)**: Ein paar Threads haben >1000 Score, die Mehrheit hat <5. Median-Wert wird im Output ausgewiesen, nicht Mittelwert.

- **Cross-Posts** (gleicher Thread in mehreren Subreddits): zaehlt als separate Erwaehnung pro Subreddit, im CSV mit gleicher `thread_id` aber unterschiedlichem `subreddit`. Aggregation deduplicates ueber `thread_id` fuer Top-5-Threads-Liste.

- **Bot-Accounts** (sehr alte Marken-Erwaehnung in Auto-Generierten Posts): Skill markiert Erwaehnungen mit `autor_username` aus bekannter Bot-Liste oder `karma < 10 UND autor_alter_tage < 30` als `vermutlich_bot: true`, nicht in Sentiment-Aggregate einbezogen.

- **Sehr alte Erwaehnung trotz 6-Monats-Filter** (Apify Filter-Fehler): clientseitig auf `erstellt_iso >= heute_minus_6_monate` filtern, alle aelteren verwerfen.

- **Stark englischsprachige Branche fuer deutschen Kunden** (z. B. Tech-SaaS): wenn `sprache_kollision`-Auffaelligkeit getriggert ist, Empfehlung im Strategie-Block: "Englisches Engagement-Profil aufbauen oder Niche-deutsche Subreddits priorisieren".

- **Apify-Actor scheitert komplett (Rate-Limit, UI-Aenderung)**: Fallback auf einen alternativen Reddit-Scraper-Actor (siehe `reference/reddit-tools-mapping.md`). Wenn beide scheitern: Skill bricht mit klarer Fehlermeldung ab, kein halbgares Result.

- **Reddit-API direkt nutzen**: ausdruecklich NICHT empfohlen — rate-limit-anfaellig, OAuth-Setup-Aufwand zu hoch fuer Skill-Reproduzierbarkeit. Apify-Actors abstrahieren das weg.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown + YAML-Frontmatter fuer Aggregat, CSV fuer Roh-Daten-Listen
- Standard-Schlussformat im Chat (zwei Varianten: voller / kompakter Lauf + Skip)
- `status.md` und Dashboard werden in jedem Lauf aktualisiert, auch bei Skip
- HTML-Report basiert auf `reports/_shell.html` (aus Drive)
- **Roh-Daten** gzip-komprimiert in Drive `assets/raw/reddit-*.json.gz` als Cache (lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/raw/`)
- **Erwaehnungs-Auszuege max 200 Zeichen im CSV, max 500 Zeichen im Markdown** — Volltexte bleiben im Roh-JSON
- **Sentiment-Klassifikation reproduzierbar** — Lexikon + Score + definierter LLM-Prompt, kein freies Bauchgefuehl
- **Fit-Score-Formel ist im Reference-File festgehalten** — Achsen-Gewichte koennen branchenabhaengig angepasst werden, das ist dokumentiert
- **Branchen-Fit-Gate (Schritt 3)** ist Pflicht-Schritt, kein optionaler Check
