# MTA-Integration und Doppel-Modus-Architektur

Dieses Dokument beschreibt, wie `03-12-social-linkedin-post-quality` in den MTA-Workflow eingebettet ist und wie der Doppel-Modus (Sub-Skill plus Standalone) technisch funktioniert.

## Drei Betriebs-Modi

### 1. Sub-Skill-Modus (primärer MTA-Use-Case)

Aufgerufen aus `03-11-social-linkedin` mit:

- Posts-CSV-Pfad (lokaler Arbeits-Cache, typisch `~/.cache/reachx-mta/<slug>/raw/linkedin-posts-AKTEURSSLUG.csv` - der Caller schreibt vor dem Sub-Skill-Aufruf eine Per-Akteur-CSV in den Cache)
- Akteurs-Slug
- Akteurs-Typ (`kunde` oder `wettbewerber`)
- Optional: Account-Median-ER aus dem Profil-Scrape

Output: JSON-Cache, kein Chat-Format, kein status.md-Update.

### 2. MTA-Standalone-Modus

Manueller Aufruf innerhalb eines MTA-Projekts. Z. B. wenn der Stratege gezielt LinkedIn-Posts für ein einzelnes Thema neu bewerten will.

Output: vollwertiger Aggregat-Lauf mit Markdown plus CSV plus HTML plus status.md plus Dashboard plus Standard-Schluss.

### 3. Plain-Standalone-Modus

Kein MTA-Kontext. Nutzer wirft 1-N Posts in den Chat, will eine Bewertung.

Output: gerendertes Markdown im Chat, optional Datei.

## Modus-Erkennungs-Algorithmus

```text
1. Wenn Aufruf-Parameter `mode=sub-skill` oder `caller=03-11-social-linkedin`:
   → Modus 1 (Sub-Skill)
2. Sonst, wenn Posts-CSV-Pfad als Eingabe übergeben wurde UND Pfad zeigt auf MTA-Projekt:
   → Modus 1 (Sub-Skill mit impliziter Caller-Annahme)
3. Sonst, wenn eine MTA im Active-MTA-Cache registriert ist (`drive.py get-mta <slug>` liefert eine `folder_id`) oder explizit per Slug-Parameter genannt wurde:
   → Modus 2 (MTA-Standalone)
4. Sonst:
   → Modus 3 (Plain-Standalone)
```

Im Zweifelsfall kurz beim Nutzer rückfragen, welcher Modus gemeint ist.

## Posts-CSV-Schema (Input vom Caller)

Erwartete Spalten, identisch zur CSV, die `03-11-social-linkedin` schreibt:

| Spalte | Pflicht | Beschreibung |
|---|---|---|
| `akteur_slug` | ja | Identifiziert den Account |
| `akteur_typ` | ja | `kunde` oder `wettbewerber` |
| `post_id` | ja | Stabile Post-ID (LinkedIn-URN oder Hash) |
| `post_url` | nein | Original-URL auf LinkedIn |
| `datum` | ja | ISO-8601 |
| `format` | ja | `text_only` / `bild` / `karussell` / `video` / `document` / `poll` / `event` / `repost` / `article` |
| `text` | ja | Voller Post-Text |
| `likes` | nein | Anzahl Reactions/Likes |
| `reposts` | nein | Anzahl Reposts/Shares |
| `kommentare` | nein | Anzahl Kommentare |
| `follower_zahl` | nein | Followerzahl des Akteurs zum Posting-Zeitpunkt (oder aktuell) |
| `account_median_er` | nein | Account-Median-Engagement-Rate (Prozent) für Performance-Ratio |
| `is_repost_ohne_kommentar` | nein | `true` / `false` |

Fehlende Spalten führen zu eingeschränkter Bewertung (insbesondere Performance-Ratio). Skill bricht nicht ab, sondern markiert die nicht bewertbaren Dimensionen explizit.

## JSON-Cache-Schema (Output an den Caller)

Dateiname: `~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json` (lokaler Arbeits-Cache, eine Datei pro Akteur). Der Caller `03-11-social-linkedin` bündelt diese Caches beim Upload nach Drive `assets/raw/` (gzip-komprimiert).

Top-Level-Felder:

```json
{
  "skill": "03-12-social-linkedin-post-quality",
  "mode": "sub-skill",
  "caller": "03-11-social-linkedin",
  "akteur_slug": "string",
  "akteur_typ": "kunde|wettbewerber",
  "generiert_am": "ISO-8601",
  "schema_version": "1.0",
  "anzahl_posts": 0,
  "durchschnitts_score": 0.0,
  "performance_ratio_bewertet": 0,
  "performance_ratio_nicht_bewertet": 0,
  "posts": [],
  "aggregat": {}
}
```

Pro Post in `posts[]`:

```json
{
  "post_id": "string",
  "auszug": "erste 80 Zeichen",
  "datum": "YYYY-MM-DD",
  "format": "...",
  "engagement": {"likes": 0, "reposts": 0, "kommentare": 0},
  "scores": {
    "hook": 1-5,
    "mehrwert": 1-5,
    "format_fit": 1-5,
    "engagement_mechanik": 1-5,
    "performance_ratio": "1-5 oder null"
  },
  "gesamtnote": 0.0,
  "performance_ratio_bewertet": true,
  "performance_ratio_basis": "account_median|branchen_benchmark|nicht_bewertbar",
  "themen_cluster": ["..."],
  "tonalitaet": "...",
  "begruendung": {
    "hook": "...",
    "mehrwert": "...",
    "format_fit": "...",
    "engagement_mechanik": "...",
    "performance_ratio": "..."
  },
  "optimierungs_hinweise": ["..."]
}
```

Aggregat-Block:

```json
{
  "top_3_posts": ["POST_ID_1", "POST_ID_2", "POST_ID_3"],
  "bottom_3_posts": ["POST_ID_X", "POST_ID_Y", "POST_ID_Z"],
  "format_verteilung": {"text_only": 0, "karussell": 0},
  "themen_cluster_verteilung": {"thought_leadership": 0, "recruiting": 0},
  "tonalitaets_verteilung": {"corporate": 0, "persoenlich": 0}
}
```

## Aufruf-Konvention durch 03-11-social-linkedin

Der Caller ruft den Skill iterativ pro Akteur auf:

```text
für jeden Akteur in [Kunde + bestätigte Wettbewerber]:
  posts_csv = ~/.cache/reachx-mta/<slug>/raw/linkedin-posts-AKTEURSSLUG.csv
  if posts_csv vorhanden und nicht leer:
    aufruf: 03-12-social-linkedin-post-quality
      mode: sub-skill
      caller: 03-11-social-linkedin
      posts_csv: <Cache-Pfad>
      akteur_slug: AKTEURSSLUG
      akteur_typ: kunde|wettbewerber
      account_median_er: <falls bekannt aus Profil-Scrape>
    erwartet: ~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json existiert nach Lauf
```

Nach allen Sub-Skill-Läufen aggregiert der Caller die Cache-Dateien zu seinem eigenen Markdown plus HTML plus status.md.

## Was im Sub-Skill-Modus NICHT passieren darf

- KEIN `audits/post-quality-bewertungen.md` schreiben (das ist Standalone-Output)
- KEIN HTML-Report schreiben
- KEIN `status.md` aktualisieren
- KEIN Dashboard aktualisieren
- KEIN Standard-Schluss-Format im Chat
- KEIN Pop-up-Nachfragen, die den Caller blockieren

Alles, was den Caller-Workflow stört, ist im Sub-Skill-Modus verboten. Der Skill liefert sauber den JSON-Cache und kehrt zurück.

## Cache-Verhalten

Bei wiederholtem Aufruf (Re-Run) für denselben Akteur:

1. Prüfen, ob `~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json` bereits existiert
2. Wenn ja: vergleiche `generiert_am` mit Modified-Date der Posts-CSV
3. Wenn Cache jünger als CSV: erneut bewerten ist OK, alten Cache überschreiben
4. Wenn Cache älter als CSV: gleiche Logik (Re-Eval), Caller hat Frische-Verantwortung
5. Im Zweifel: erneut bewerten - die Kosten sind moderat und Konsistenz ist wichtiger als Cache-Sparen

## Edge Cases

- **Posts-CSV leer**: Skill schreibt einen Stub-Cache mit `anzahl_posts: 0` und `posts: []`. Caller erkennt das und überspringt den Akteur.
- **Posts-CSV fehlt**: Skill bricht ab mit Fehler-JSON `{"error": "posts_csv_not_found", "path": "..."}`. Caller protokolliert das.
- **Keine Engagement-Daten in der CSV**: Skill bewertet die 4 Dimensionen ohne E, markiert `performance_ratio: null`. Caller kann darauf reagieren.
- **Account-Median nicht in CSV und nicht als Parameter**: Skill nutzt Branchen-Benchmark aus `references/benchmarks.md`, vermerkt `performance_ratio_basis: branchen_benchmark`.
- **Hard-Cap durch Caller**: 03-11-social-linkedin begrenzt CSV auf 50 Posts pro Akteur. Sub-Skill verarbeitet einfach, was er bekommt - keine eigene Begrenzungs-Logik.

## Konvention für den HTML-Report (nur MTA-Standalone-Modus)

Dateiname: `reports/19-post-quality.html` (Nummerierung passt zur erweiterten Reihenfolge in `MTA-SKILLS-PLAN.md`).

Aus `reports/_shell.html` kopieren und Platzhalter ersetzen gemäß `contracts.md` Abschnitt 7:

- `{{TITLE}}` — "Post-Quality-Bewertung · KUNDE"
- `{{EYEBROW}}` — "MTA-Audit"
- `{{DISPLAY_NAME}}` — "LinkedIn-Post-Quality-Bewertung"
- `{{META_LINE}}` — Erstellungs-Datum plus Anzahl Posts plus Akteure
- `{{MAIN_CONTENT}}` — Stat-Strip plus Bewertungs-Tabelle plus Pro-Post-Karten plus Aggregat
- `{{FOOTER_TEXT}}` — Standard-Footer

`<body>` ohne `is-dashboard`-Klasse (Back-Link sichtbar).
