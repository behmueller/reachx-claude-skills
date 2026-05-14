# Reddit-Output-Schema

Vollstaendiges Schema fuer die Output-Dateien des `03-13-social-reddit-fit-check`-Skills:

- `audits/reddit-fit.md` — Aggregat (Markdown mit YAML-Frontmatter)
- `audits/reddit-subreddits.csv` — Top-Subreddits-Inventar (CSV)
- `audits/reddit-erwaehnungen.csv` — Erwaehnungen pro Akteur × Thread (CSV)
- `assets/raw/reddit-*.json.gz` (Drive) — gzip-komprimierte Roh-Caches; lokal `~/.cache/reachx-mta/<slug>/raw/reddit-*.json`

## 1. `audits/reddit-fit.md`

### Frontmatter (Voll-Lauf)

```yaml
---
# === Skill-Metadaten ===
skill: 03-13-social-reddit-fit-check
generiert_am: 2026-05-14T10:00:00Z
schema_version: "1.0"
formel_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste_md: wettbewerber/liste.md
  liste_bestaetigt_am: 2026-05-08T14:00:00Z
  kunde_md_vorhanden: true
modus: voll                  # voll | kompakt | skip
apify_actor_subreddits: apify/reddit-search-scraper
apify_actor_erwaehnungen: apify/reddit-search-scraper
apify_actor_themen: apify/reddit-scraper
datenstand: 2026-05-14

# === Such-Konfiguration ===
such_keywords:
  branche: ["Maler", "painters", "DIY paint"]
  portfolio: ["Fassade", "Innenraum", "Tapezieren"]
  marken: ["Beispiel GmbH", "beispiel-gmbh.de"]

# === Branchen-Fit-Bewertung ===
branchen_fit_reddit: mittel              # hoch | mittel | gering
subreddits_gefunden: 8
subreddits_top10:
  - subreddit: r/Heimwerken
    mitglieder: 24500
    posts_pro_tag: 4.2
    sprache: de
    moderations_strenge: mittel
    tonalitaet: hilfsbereit
    relevanz_score: 0.87
  # ... 9 weitere

# === Fit-Score ===
fit_score: 62
empfehlung: aktiv_empfohlen              # aktiv_empfohlen | beobachtung_empfohlen | nicht_empfohlen
gewichte_override: null                  # null oder dict mit angepassten Gewichten
achsen:
  community_aktivitaet:
    score: 54
    gewicht: 0.30
    daten:
      median_mitglieder_top10: 18000
      median_posts_pro_tag: 3.5
      subreddit_anzahl: 8
  brand_reception:
    score: 65
    gewicht: 0.30
    daten:
      erwaehnungen_anzahl: 18
      pos_anteil: 0.39
      neg_anteil: 0.11
      neutral_anteil: 0.33
      gemischt_anteil: 0.11
      unklar_anteil: 0.06
    daten_verlaesslichkeit: mittel
  kommerz_toleranz:
    score: 72
    gewicht: 0.20
    daten:
      anteil_kommerz_allergisch_top10: 0.20
      anteil_streng_moderiert_top10: 0.30
      anteil_locker_moderiert_top10: 0.40
  format_tauglichkeit:
    score: 58
    gewicht: 0.20
    daten:
      sprache_kollision_faktor: 0.40
      anteil_hilfsbereit_top10: 0.50
      anteil_ernsthaft_top10: 0.30

# === Akteurs-Erwaehnungen ===
akteure:
  - akteurs_slug: beispiel-gmbh
    akteurs_typ: kunde
    erwaehnungen_anzahl: 18
    sentiment_verteilung:
      positiv: 7
      neutral: 6
      negativ: 2
      gemischt: 2
      unklar: 1
    top_subreddits: [r/Heimwerken, r/de_IAmA, r/Selbststaendig]
    top_thread_url: https://www.reddit.com/r/Heimwerken/comments/...
  - akteurs_slug: wettbewerber-alpha
    akteurs_typ: wettbewerber_regional
    erwaehnungen_anzahl: 24
    sentiment_verteilung:
      positiv: 14
      neutral: 5
      negativ: 3
      gemischt: 1
      unklar: 1
    top_subreddits: [r/Heimwerken, r/painting]
    top_thread_url: https://www.reddit.com/r/painting/comments/...
  # ... weitere

# === Themen & Pain-Points ===
themen_pro_subreddit:
  - subreddit: r/Heimwerken
    themen_cluster:
      - label: "Fassaden-Renovierung"
        post_anzahl: 8
      - label: "Materialwahl"
        post_anzahl: 6
      - label: "Kosten-Einschaetzung"
        post_anzahl: 5
    pain_points_top3:
      - "Wann lohnt sich Profi vs DIY"
      - "Welcher Anbieter ist serioes"
      - "Wie lange haelt Fassadenfarbe"
  # ... weitere

# === Auffaelligkeiten ===
auffaelligkeiten:
  - typ: wettbewerber_aktiv_kunde_unsichtbar
    titel: "Wettbewerber alpha hat 24 Erwaehnungen, Kunde 18 - aehnliche Lage"
    relevanz: mittel
    betroffene_akteure: [beispiel-gmbh, wettbewerber-alpha]
    handlung: "Weiter beobachten, Sichtbarkeit ist vergleichbar"
  - typ: pain_point_signal
    titel: "Pain-Point 'Kosten-Einschaetzung' matched USP 'Transparente Festpreise'"
    relevanz: hoch
    betroffene_akteure: [beispiel-gmbh]
    betroffene_subreddits: [r/Heimwerken]
    handlung: "Content-Anker fuer organische Beitraege - AMA oder Helpful-Content-Format"
---
```

### Frontmatter (Skip-Variante)

Reduziertes Frontmatter, wenn `modus: skip`:

```yaml
---
skill: 03-13-social-reddit-fit-check
generiert_am: 2026-05-14T10:00:00Z
schema_version: "1.0"
formel_version: "1.0"

basiert_auf:
  meta_json: meta.json
  liste_md: wettbewerber/liste.md
modus: skip
datenstand: 2026-05-14

such_keywords:
  branche: ["Hausverwaltung", "property management"]
  portfolio: ["WEG-Verwaltung", "Sondereigentum"]

branchen_fit_reddit: gering
subreddits_gefunden: 0
subreddits_kandidaten_geprueft: 47    # wie viele wurden initial gesucht, bevor gefiltert wurde

fit_score: 0
empfehlung: nicht_empfohlen
achsen: null                          # nicht berechnet bei Skip

auffaelligkeiten:
  - typ: branchen_kein_reddit_kontext
    titel: "Branche Hausverwaltung hat keinen relevanten Reddit-Kontext"
    relevanz: hoch
    handlung: "Reddit als Kanal ueberspringen - andere Channels priorisieren"
---
```

### Body-Struktur (Voll-Lauf)

```markdown
# Reddit-Marketing-Fit: Beispiel GmbH

## Uebersicht & Empfehlung

**Fit-Score: 62 / 100 — Empfehlung: aktiv_empfohlen**

Reddit ist fuer Beispiel GmbH ein aktiv bespielbarer Kanal. Die Branche
hat eine etablierte Community in r/Heimwerken (24.500 Mitglieder, 4.2
Posts/Tag), Marken-Reception ist netto positiv, und die dominante 
Tonalitaet "hilfsbereit" passt zu authentischen Beitraegen. Format-
Empfehlung: organische Helpful-Content-Beitraege, keine Paid-Kampagnen.

## Subreddit-Inventar (Top 10)

| Subreddit | Mitglieder | Posts/Tag | Sprache | Moderation | Tonalitaet |
|---|---|---|---|---|---|
| r/Heimwerken | 24.500 | 4.2 | de | mittel | hilfsbereit |
| r/DIY | 22.500.000 | 800 | en | mittel | hilfsbereit |
| ... | ... | ... | ... | ... | ... |

## Marken-Erwaehnungen

### Beispiel GmbH (Kunde)
- 18 Erwaehnungen in den letzten 6 Monaten
- Sentiment: 39% pos / 33% neutral / 11% neg / 11% gemischt / 6% unklar
- Top-5-Threads: ...

### Wettbewerber-Alpha
- 24 Erwaehnungen
- Sentiment: ...

## Themen & Pain-Points

### r/Heimwerken
- **Themen-Cluster**: Fassaden-Renovierung (8 Posts), Materialwahl (6), Kosten-Einschaetzung (5)
- **Pain-Points**:
  - "Wann lohnt sich Profi vs DIY"
  - "Welcher Anbieter ist serioes"
  - "Wie lange haelt Fassadenfarbe"

## Fit-Score-Aufschluesselung

- **Community-Aktivitaet: 54 / 100** (Gewicht 30%) — Median 18.000 Mitglieder, 3.5 Posts/Tag, 8 Subreddits
- **Brand-Reception: 65 / 100** (Gewicht 30%) — 18 Erwaehnungen, netto positiv
- **Kommerz-Toleranz: 72 / 100** (Gewicht 20%) — Mehrheit locker moderiert
- **Format-Tauglichkeit: 58 / 100** (Gewicht 20%) — Sprache teilkollision, Tonalitaet ueberwiegend hilfsbereit

## Auffaelligkeiten

(Liste der getriggerten Auffaelligkeiten mit Titel, Relevanz, Handlung)

## Strategie-Empfehlung

Konkrete Pfade:
1. **AMA in r/Heimwerken** mit Fokus "Kosten-Einschaetzung Fassaden-Renovierung"
2. **Helpful-Content** in r/DIY (englisch) zu Material-Vergleichen
3. **Beobachtung** der Wettbewerber-Erwaehnungen — Tonalitaet pruefen
4. **Kein Paid** — Reddit-Marketing funktioniert organisch
```

### Body-Struktur (Skip-Variante)

```markdown
# Reddit-Marketing-Fit: Beispiel Hausverwaltung GmbH

## Skip-Variante: Reddit ist kein Kanal fuer diese Branche

**Fit-Score: 0 / 100 — Empfehlung: nicht_empfohlen**

Fuer die Branche Hausverwaltung wurden in der Subreddit-Recherche
keine relevanten Communities mit ausreichender Aktivitaet gefunden.
47 Subreddit-Kandidaten wurden ueber die Such-Keywords gepruefst, 
keiner erfuellt die Mindest-Kriterien (>1.000 Mitglieder, >0.5 Posts/Tag).

## Recherche-Trace

Die folgenden Keywords wurden gegen die Reddit-Subreddit-Suche gestellt:
- Branche: "Hausverwaltung", "property management", "WEG-Verwaltung"
- Portfolio: "Sondereigentum", "Mietverwaltung"
- Marken-Namen: "Beispiel Hausverwaltung GmbH"

Keine der gefundenen Subreddits erfuellt die Schwellwerte.

## Auffaelligkeiten

- `branchen_kein_reddit_kontext` — Reddit ist fuer diese Branche kein 
  Kanal-Hebel. Andere Plattformen (LinkedIn, Branchenportale) priorisieren.

## Empfehlung

Reddit aus dem Kanal-Mix dieser MTA ausschliessen. Resources fuer 
andere Audits einsetzen.
```

## 2. `audits/reddit-subreddits.csv`

Eine Zeile pro Top-Subreddit (alle, die das Filter aus Schritt 3 passieren).

**Spalten-Definition:**

| Spalte | Typ | Beschreibung | Beispiel |
|---|---|---|---|
| `subreddit_name` | string | mit `r/`-Prefix | `r/Heimwerken` |
| `subreddit_url` | URL | volle URL | `https://www.reddit.com/r/Heimwerken/` |
| `mitglieder_anzahl` | int | Subscribers | `24500` |
| `posts_pro_tag` | float | Median letzte 30 Tage | `4.2` |
| `sprache_dominant` | enum | `de | en | mixed | unbekannt` | `de` |
| `nsfw` | bool | | `false` |
| `moderations_strenge` | enum | `streng | mittel | locker | unbekannt` | `mittel` |
| `tonalitaet` | enum | `snarky | ernsthaft | hilfsbereit | kommerz_allergisch | unbekannt` | `hilfsbereit` |
| `relevanz_score` | float | 0.0-1.0 | `0.87` |
| `themen_cluster_top3` | string | Pipe-separated | `Fassaden-Renovierung | Materialwahl | Kosten-Einschaetzung` |
| `pain_points_top3` | string | Pipe-separated | `Profi vs DIY | Anbieter-Wahl | Haltbarkeit` |
| `in_top10` | bool | Ist in den Top-10 nach Relevanz-Score | `true` |
| `datenstand_iso` | ISO-Datum | wann erhoben | `2026-05-14` |

**Bei Skip-Variante: CSV ist leer (nur Header), oder wird nicht geschrieben** — dokumentieren in `audits/reddit-fit.md` Body.

## 3. `audits/reddit-erwaehnungen.csv`

Eine Zeile pro Erwaehnung × Akteur × Thread.

**Spalten-Definition:**

| Spalte | Typ | Beschreibung | Beispiel |
|---|---|---|---|
| `akteurs_slug` | string | aus `liste.md` | `beispiel-gmbh` |
| `akteurs_typ` | enum | `kunde | wettbewerber_kunde_genannt | wettbewerber_regional | wettbewerber_ueberregional` | `kunde` |
| `akteurs_name` | string | Marken-Name fuer Anzeige | `Beispiel GmbH` |
| `thread_id` | string | Reddit-Thread-ID | `abc123` |
| `thread_url` | URL | volle URL | `https://www.reddit.com/r/Heimwerken/comments/abc123/...` |
| `thread_title` | string | Post-Titel (auch fuer Kommentare: der Parent-Post-Titel) | `Fassade streichen lassen - Erfahrungen?` |
| `subreddit` | string | mit `r/`-Prefix | `r/Heimwerken` |
| `erwaehnung_typ` | enum | `post | comment` | `comment` |
| `erwaehnung_text_auszug` | string | erste 200 Zeichen, **unveraendert** | `"Ich habe vor 2 Jahren mit Beispiel GmbH..."` |
| `autor_username` | string | oder `[deleted]` | `user123` |
| `erstellt_iso` | ISO-Datum | | `2026-03-15T14:23:00Z` |
| `score` | int | Upvotes minus Downvotes | `12` |
| `kommentare_count` | int | nur bei Posts | `5` |
| `sentiment` | enum | `positiv | neutral | negativ | gemischt | unklar` | `positiv` |
| `sentiment_konfidenz` | enum | `hoch | mittel | niedrig` | `hoch` |
| `vermutlich_bot` | bool | aus Bot-Detection | `false` |
| `datenstand_iso` | ISO-Datum | wann erhoben | `2026-05-14` |

**Encoding:** UTF-8, CSV mit Komma als Trenner, Anfuehrungszeichen-Escape bei Text-Feldern. **Newlines im `erwaehnung_text_auszug`** durch Space ersetzen (nicht entfernen), damit CSV-Parser nicht kaputt geht.

**Auszug-Regel:** Erste 200 Zeichen nach Stripping fuehrender Whitespaces, kein Mid-Sentence-Cut: wenn Zeichen 200 mitten im Wort liegt, bis zum naechsten Wort-Boundary erweitern.

**Bei Skip-Variante: CSV wird nicht geschrieben.**

## 4. Roh-Cache-Dateien (lokal `~/.cache/reachx-mta/<slug>/raw/`, am Skill-Ende nach Drive `assets/raw/` gzip-komprimiert)

| Datei (lokal) | Inhalt | Format |
|---|---|---|
| `reddit-such-keywords.json` | Die zusammengestellten Keywords (Schritt 2) | JSON Object |
| `reddit-subreddits.json` | Apify-Output Schritt 3, unveraendert | JSON Array |
| `reddit-erwaehnungen-AKTEURSSLUG.json` | Apify-Output Schritt 5 pro Akteur, unveraendert | JSON Array |
| `reddit-themen-SUBREDDITSLUG.json` | Apify-Output Schritt 7 pro Top-Subreddit, unveraendert | JSON Array |

`AKTEURSSLUG` und `SUBREDDITSLUG` sind die slug-Form (kleinbuchstaben, keine Sonderzeichen). `r/Heimwerken` wird zu `heimwerken`.

**Konvention:** Roh-Daten werden **nicht** vor dem Cache umstrukturiert — exakt das, was der Actor liefert. Begruendung: bei Schema-Wechseln des Actors kann man zurueck-mappen, ohne erneut zu scrapen.

## Validierungs-Regeln

Beim Schreiben der Outputs der Skill diese Checks ausfuehren:

1. **Frontmatter valides YAML** — pyyaml-Parse, bei Fehler abbrechen
2. **`fit_score` ist int 0-100** — sonst Berechnungs-Fehler
3. **`empfehlung` und `fit_score` passen zusammen** (Bands aus `fit-score-formel.md`)
4. **Achsen-Gewichte summieren zu 1.0** (toleranz 0.01) — sonst normalisieren und Hinweis loggen
5. **CSV-Header matched exakt** das oben definierte Schema
6. **Mindestens 1 Auffaelligkeit** im Output (auch bei Skip-Variante: `branchen_kein_reddit_kontext`)
7. **Bei `modus: skip`** Frontmatter: `subreddits_gefunden == 0`, `fit_score == 0`, `achsen == null`
8. **Bei `modus: voll | kompakt`**: `achsen` nicht null, alle vier Achsen-Werte vorhanden

## Versionierung

Wenn sich Schema aendert: `schema_version` in den Outputs hochzaehlen, im Skill-Code Versions-Check vor dem Lesen alter Outputs.

Aktuelle Version: **1.0**
