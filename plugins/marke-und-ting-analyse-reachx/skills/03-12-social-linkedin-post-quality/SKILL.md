---
name: 03-12-social-linkedin-post-quality
description: Bewertet LinkedIn-Posts entlang eines 5-Dimensionen-Frameworks (Hook, inhaltlicher Mehrwert, Format-Fit, Engagement-Mechanik, Performance-Ratio) und liefert Score plus Begründung plus Optimierungs-Hinweise. Funktioniert in zwei Modi - Standalone (Nutzer übergibt Posts direkt oder ruft den Skill außerhalb eines MTA-Projekts auf) und Sub-Skill von 03-11-social-linkedin (automatischer Aufruf mit fertiger Posts-CSV, Output als JSON-Cache im MTA-Projekt). Nutze diesen Skill IMMER, wenn der Nutzer LinkedIn-Posts bewerten, vergleichen, benchmarken oder optimieren will - auch bei Phrasen wie "ist das ein guter Post", "rate meinen LinkedIn-Post", "bewerte diese Beiträge", "Post-Quality-Check", "LinkedIn-Content-Audit", "vergleich die LinkedIn-Posts von X und Y", "rate this LinkedIn post". Auch wenn der Nutzer Posts mit Engagement-Daten teilt und nach Einschätzung fragt, auch ohne explizites "bewerten".
---

# LinkedIn Post Quality Rating

Strukturiertes Framework zur Bewertung von LinkedIn-Posts. Kombiniert qualitative Inhaltsanalyse mit quantitativen Performance-Daten. Designt so, dass die Bewertung über verschiedene Branchen, Tonalitäten und Account-Größen hinweg fair bleibt.

Dieser Skill ist ein **Sub-Skill** im MTA-Workflow (siehe `MTA-SKILLS-PLAN.md`): er kann standalone laufen oder von `03-11-social-linkedin` als Helper aufgerufen werden. Die Doppel-Modus-Architektur ist die wichtigste Konvention, die hier zu beachten ist - siehe Abschnitt "Modus-Erkennung".

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

## Wann triggern

- Einzelner Post wird zur Bewertung vorgelegt (Text plus ggf. Engagement-Daten)
- Mehrere Posts sollen verglichen oder gebenchmarkt werden
- Optimierungs-/Verbesserungsvorschläge für eigene Posts
- Aufruf als Sub-Schritt aus `03-11-social-linkedin`
- "Bewerte diesen Post", "Post-Quality-Check", "LinkedIn-Content-Audit", "rate meine Posts"

## Modus-Erkennung (Pflicht vor jeder Ausführung)

Skill prüft am Start, in welchem Modus er läuft. Drei mögliche Modi:

### Modus 1 — Sub-Skill-Modus (von 03-11-social-linkedin aufgerufen)

Erkennungs-Indikatoren (mindestens einer trifft zu):

- Aufruf-Kontext nennt explizit `03-11-social-linkedin` als Caller
- Eingangsparameter ist ein Pfad zu einer Posts-CSV (typisch lokaler Arbeits-Cache `~/.cache/reachx-mta/<slug>/raw/linkedin-posts-AKTEURSSLUG.csv` oder Drive `audits/linkedin-posts.csv`) plus Akteurs-Slug
- Eingangsparameter `mode: sub-skill` wird mitgegeben

Verhalten in diesem Modus:

- Liest Posts aus der übergebenen CSV (Pflicht-Spalten siehe `references/mta-integration.md`)
- Bewertet jeden Post nach dem 5-Dimensionen-Framework
- Schreibt das Ergebnis **rein technisch** als JSON-Cache in den lokalen Arbeits-Cache `~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json` (Caller bündelt das später beim Upload nach Drive `assets/raw/`)
- **KEIN** Markdown-Aggregat, **KEIN** HTML-Report, **KEIN** `status.md`-Update, **KEIN** Standard-Schluss-Format - das alles macht der aufrufende Caller
- Output an den Caller ist ein schlanker JSON-Block mit dem Cache-Pfad plus Summary-Statistik (Anzahl bewerteter Posts, Durchschnitts-Score, Top/Bottom-3)

### Modus 2 — MTA-Standalone-Modus (Aufruf innerhalb eines MTA-Projekts)

Erkennungs-Indikatoren:

- MTA ist im Active-MTA-Cache registriert (`drive.py get-mta <slug>` liefert eine `folder_id`)
- Nutzer ruft den Skill direkt auf, nicht über `03-11-social-linkedin`
- Nutzer liefert Posts ad hoc (z. B. paste in den Chat) oder verweist auf eine vorhandene `audits/linkedin-posts.csv` im Drive-Folder

Verhalten in diesem Modus:

- Ermittle Drive-Folder-IDs aus `meta.json` (siehe Schritt 0 unten)
- Bewertet Posts nach Framework
- Schreibt vollwertigen Aggregat-Output gemäß `contracts.md` nach Drive:
  - `audits/post-quality-bewertungen.md` (Markdown mit YAML-Frontmatter)
  - `audits/post-quality-bewertungen.csv` (eine Zeile pro Post)
  - `reports/19-post-quality.html` (Strategen-Report aus `reports/_shell.html` aus Drive)
- Aktualisiert `status.md` und `reports/index.html` (Dashboard) auf Drive gemäß `contracts.md`
- Beendet im Chat mit Standard-Schluss-Format aus `contracts.md` Abschnitt 6

### Modus 3 — Plain-Standalone-Modus (kein MTA-Projekt)

Erkennungs-Indikatoren:

- Kein MTA im Active-MTA-Cache registriert
- Nutzer hat keinen MTA-Kontext genannt
- Typischer Use-Case: Nutzer wirft 1-3 Posts in den Chat und fragt "ist das gut?"

Verhalten in diesem Modus:

- Bewertet Posts nach Framework
- Output direkt im Chat als gerendertes Markdown (siehe "Output-Format" unten)
- Optional: wenn Nutzer das wünscht, schreibe das Markdown in eine Datei im aktuellen Arbeits-Verzeichnis (nicht hardcoded, sondern explizit erfragen)
- **KEIN** `status.md`-Update, **KEIN** HTML-Report, **KEIN** MTA-Strukturen anlegen, **KEIN** Drive-Schreibvorgang
- Schluss-Format im Chat: schlicht und ohne MTA-Schluss-Block

## Schritt 0: MTA-Kontext ermitteln (nur Modus 2)

Im MTA-Standalone-Modus ermittle die Drive-Folder-IDs aus `meta.json`:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Im Sub-Skill-Modus (Modus 1) bekommt der Skill `FOLDER_ID` und Cache-Pfade vom Caller. Im Plain-Standalone (Modus 3) entfaellt dieser Schritt.

## Voraussetzungen pro Modus

| Voraussetzung | Sub-Skill | MTA-Standalone | Plain-Standalone |
|---|---|---|---|
| `meta.json` | erwartet (vom Caller) | Pflicht | nicht erforderlich |
| Posts-CSV vom Caller | Pflicht | optional | nicht erforderlich |
| Detail-Rubrik `references/rubric.md` | Pflicht lesen | Pflicht lesen | Pflicht lesen |
| Engagement-Daten | optional | optional | optional |

## Was du als Input pro Post brauchst

Pro Post mindestens:

- **Post-Text** (Pflicht)

Idealerweise zusätzlich:

- **Format-Typ** (Text-only, Bild, Karussell, Video, Document/PDF, Poll, Event, Repost, Article)
- **Engagement-Daten**: Likes, Reactions-Breakdown, Reposts/Shares, Kommentar-Anzahl
- **Posting-Zeitpunkt** (Datum, idealerweise Uhrzeit plus Wochentag)
- **Account-Kontext**: Followerzahl des postenden Accounts (kritisch für Performance-Ratio)
- **Median-Engagement-Rate des Accounts** (für faire Vergleichbarkeit)

Wenn Daten fehlen, bewerte die verfügbaren Dimensionen und vermerke explizit, welche nicht beurteilt werden konnten. **Erfinde keine Daten** - das verfälscht den Report und untergräbt das Framework. Lieber "nicht bewertbar" angeben, als zu raten.

## Das Framework auf einen Blick

5 Dimensionen, jeweils 1-5 Punkte. Plus 2 kategorische Meta-Felder. Plus eine Gesamtnote (gewichteter Durchschnitt).

| Dimension | Was wird bewertet | Gewichtung |
|---|---|---|
| **A) Hook-Qualität** | Erste 1-2 Zeilen / Vorschau-Bereich | 20% |
| **B) Inhaltlicher Mehrwert** | Substanz, Originalität, konkretes Insight | 25% |
| **C) Format-Fit** | Passt das Format zum Inhalt? | 15% |
| **D) Engagement-Mechanik** | CTA, Frage, Diskussionsanlass | 15% |
| **E) Performance-Ratio** | Daten-getriebener Vergleich mit Account-Median | 25% |

Wenn **E) Performance-Ratio** mangels Daten nicht berechenbar ist (keine Engagement-Zahlen oder kein Vergleichsmedian), wird die Gesamtnote aus den verbleibenden 4 Dimensionen ohne E gemittelt - mit klarem Vermerk im Output.

**Die kompakte Tabelle hier reicht NICHT für eine ernsthafte Bewertung.** Lies vor jeder Bewertung die ausführliche Rubrik in `references/rubric.md`. Sie enthält Score-Beispiele für jede Dimension und Anti-Patterns. Ohne diese Detail-Rubrik werden die Bewertungen inkonsistent und schwerer zu begründen.

Für Engagement-Benchmarks und Branchen-Median-Werte 2026: `references/benchmarks.md`.

## Meta-Felder (zusätzlich zu den 5 Dimensionen)

- **Themen-Cluster**: Welcher inhaltlichen Kategorie ordnest du den Post zu? Schlage 1-3 passende Tags vor (z. B. "Thought Leadership", "Recruiting", "Produkt-Launch", "Kultur-Einblick", "Daten/Studie", "Behind the Scenes", "Kunden-Story", "Industry News", "Personal Story"). Bei Wettbewerbsanalysen entstehen daraus Theme-Verteilungen.
- **Tonalität**: Wie klingt der Post? Eines aus: Corporate, Persönlich, Inspirierend, Provokativ, Sachlich-informativ, Humorvoll, Kontrovers, Kritisch.

Diese Felder fließen NICHT in die Note ein - sie helfen bei der Aggregation in einer Wettbewerbsanalyse, um Muster zu erkennen ("Wettbewerber X postet 60% Recruiting in Corporate-Tonalität").

## Ablauf einer Bewertung

1. **Modus erkennen** (siehe oben)
2. **Detail-Rubrik laden**: `references/rubric.md` lesen (vermeidet Inkonsistenz zwischen Posts)
3. **Bei Sub-Skill-Modus**: Posts-CSV laden, Spalten auf das Schema in `references/mta-integration.md` mappen
4. **Pro Post die 5 Dimensionen einzeln bewerten** mit kurzer Begründung (1-2 Sätze pro Dimension)
5. **Meta-Felder zuordnen** (Themen-Cluster, Tonalität)
6. **Gesamtnote berechnen** als gewichtetes Mittel
7. **1-3 konkrete Optimierungs-Hinweise** formulieren (nur wenn vom User gewünscht oder bei Noten unter 3,5)
8. **Output strukturieren** je nach Modus (siehe unten)

Wichtig: Die Bewertung ist **relativ**, nicht absolut. Ein Post mit 200 Likes auf einem Account mit 1.000 Followern ist anders zu bewerten als auf einem mit 100.000 Followern. Daher ist die Followerzahl für Dimension E so wichtig.

## Output-Format

### Modus 1 — Sub-Skill-Modus

JSON-Cache unter `~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json` (lokaler Arbeits-Cache - der Caller `03-11-social-linkedin` bündelt das später beim Upload nach Drive `assets/raw/`):

```json
{
  "skill": "03-12-social-linkedin-post-quality",
  "mode": "sub-skill",
  "caller": "03-11-social-linkedin",
  "akteur_slug": "AKTEURSSLUG",
  "akteur_typ": "kunde|wettbewerber",
  "generiert_am": "ISO-8601",
  "schema_version": "1.0",
  "anzahl_posts": 12,
  "durchschnitts_score": 3.4,
  "performance_ratio_bewertet": 10,
  "performance_ratio_nicht_bewertet": 2,
  "posts": [
    {
      "post_id": "POST_ID",
      "auszug": "...",
      "datum": "YYYY-MM-DD",
      "format": "...",
      "scores": {"hook": 4, "mehrwert": 5, "format_fit": 4, "engagement_mechanik": 3, "performance_ratio": 4},
      "gesamtnote": 4.1,
      "performance_ratio_bewertet": true,
      "themen_cluster": ["..."],
      "tonalitaet": "...",
      "begruendung": {"hook": "...", "mehrwert": "...", "format_fit": "...", "engagement_mechanik": "...", "performance_ratio": "..."},
      "optimierungs_hinweise": ["..."]
    }
  ],
  "aggregat": {
    "top_3_posts": ["POST_ID_1", "POST_ID_2", "POST_ID_3"],
    "bottom_3_posts": ["POST_ID_X", "POST_ID_Y", "POST_ID_Z"],
    "format_verteilung": {"text_only": 4, "karussell": 3, "video": 2, "bild": 3},
    "themen_cluster_verteilung": {"thought_leadership": 5, "recruiting": 3, "...": 4}
  }
}
```

Chat-Output: knapp, ohne MTA-Schluss-Format. Beispiel:

```
✓ post-quality-bewertung für AKTEURSSLUG abgeschlossen.
Cache: ~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json (12 Posts, Ø 3.4)
```

Caller (`03-11-social-linkedin`) liest den Cache, baut sein Aggregat, schreibt status.md/HTML.

### Modus 2 — MTA-Standalone-Modus

**`audits/post-quality-bewertungen.md`** mit YAML-Frontmatter:

```yaml
---
skill: 03-12-social-linkedin-post-quality
mode: mta-standalone
generiert_am: ISO-8601
schema_version: "1.0"
anzahl_posts: N
durchschnitts_score: 3.4
akteure: [SLUG_1, SLUG_2]
---
```

Body strukturiert mit:

- Übersicht (Akteure, Anzahl Posts, Durchschnitts-Score, Best/Worst-Post)
- Bewertungs-Tabelle (eine Zeile pro Post)
- Pro Post ein Detail-Block (Auszug, Scores, Begründung, Optimierungs-Hinweise)
- Aggregat-Patterns (Format-Verteilung, Themen-Cluster-Verteilung, Top-/Bottom-Patterns)

**`audits/post-quality-bewertungen.csv`** Spalten:

```
akteur_slug, post_id, datum, format, likes, reposts, kommentare,
hook_score, mehrwert_score, format_fit_score, engagement_mechanik_score, performance_ratio_score,
gesamtnote, performance_ratio_bewertet,
themen_cluster, tonalitaet
```

**Upload-Reihenfolge nach Drive** (im MTA-Standalone-Modus):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "post-quality-bewertungen.md" /tmp/pq.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "post-quality-bewertungen.csv" /tmp/pq.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "19-post-quality.html" /tmp/pq.html "text/html"
```

**`reports/19-post-quality.html`** aus `reports/_shell.html` (aus Drive `REPORTS_ID` lesen) mit Platzhaltern (`{{TITLE}}`, `{{EYEBROW}}`, `{{DISPLAY_NAME}}`, `{{META_LINE}}`, `{{MAIN_CONTENT}}`, `{{FOOTER_TEXT}}`). Body ohne `is-dashboard`-Klasse, Back-Link bleibt sichtbar.

Inhalt: Stat-Strip oben, Tabelle, Pro-Post-Karten als `details.skill`-Blöcke, Aggregat-Patterns.

**`reports/index.html`** Dashboard-Update (aus Drive lesen, aktualisieren, via `upsert-text` zurueckschreiben): Eintrag für `19-post-quality.html` in Reports-Liste, Status-Sektion aktualisiert.

**`status.md`-Update** gemäß `contracts.md` Abschnitt 3 (aus Drive `FOLDER_ID` lesen, aktualisieren, zurueckschreiben):
- `03-12-social-linkedin-post-quality` in `schritte_done` (Frontmatter)
- Sektion in "✓ Erledigt" im Body mit Datum, Outputs (Drive-Pfade), Hinweisen
- `naechster_empfohlen` setzen (im Standalone-Lauf typischerweise `04-02-kanal-chancen-analyse`, falls noch offen)

**Chat-Schluss** strikt nach `contracts.md` Abschnitt 6:

```
✓ 03-12-social-linkedin-post-quality abgeschlossen.

Outputs (auf Drive):
- audits/post-quality-bewertungen.md — Aggregat mit Detail-Bewertungen
- audits/post-quality-bewertungen.csv — Roh-Bewertungen (N Zeilen)
- reports/19-post-quality.html — Strategen-Report
Status aktualisiert in: status.md

Bewertungs-Lage:
- Posts bewertet:           N
- Durchschnitts-Score:      X,X
- Top-Post:                 AKTEUR, POST-AUSZUG (X,X)
- Bottom-Post:              AKTEUR, POST-AUSZUG (X,X)

Nächste Schritte:
1. EMPFOHLENER-NAECHSTER-SKILL — Begründung
2. (optional parallel) ALTERNATIVER-SKILL — Begründung

Sag mir, welcher als nächster.
```

### Modus 3 — Plain-Standalone-Modus

#### Bei einzelnem Post (vollständiger Bewertungsbericht)

```markdown
## Post-Bewertung

**Auszug:** "ERSTE_80_ZEICHEN..."
**Datum:** DATUM
**Format:** FORMAT
**Engagement:** N Likes · N Reposts · N Kommentare

### Bewertung (Gesamtnote: X,X / 5,0)

| Dimension | Score | Begründung |
|---|---|---|
| Hook-Qualität | X/5 | ... |
| Inhaltlicher Mehrwert | X/5 | ... |
| Format-Fit | X/5 | ... |
| Engagement-Mechanik | X/5 | ... |
| Performance-Ratio | X/5 oder n/v | ... |

**Themen-Cluster:** TAG1, TAG2
**Tonalität:** TONALITAET

### Optimierungs-Hinweise
1. konkreter Hinweis
2. konkreter Hinweis
```

#### Bei Batch-Bewertung (mehrere Posts in den Chat geworfen)

Tabellen-Format mit einer Zeile pro Post:

```markdown
| Datum | Format | Likes | Reposts | Komm. | Hook | Mehrwert | Format-Fit | Engage. | Perf. | Gesamt | Cluster | Tonalität |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
```

Plus eine kurze Aggregat-Analyse darunter:

- Durchschnitts-Note
- Bestperformer-Pattern (was zeichnet die Top-3-Posts aus)
- Underperformer-Pattern (was schwächt die Bottom-3-Posts)
- Format-Verteilung
- Themen-Cluster-Verteilung

Kein MTA-Schluss-Format, keine status.md-Updates - reines Chat-Output.

## Wichtige Prinzipien

**Nicht in Floskeln verfallen.** Bewertungs-Begründungen wie "guter Post" oder "schwacher Hook" sind nutzlos. Nenne, *was* den Hook stark/schwach macht ("Erste Zeile beginnt mit Frage an spezifische Zielgruppe - stoppt das Scrollen" vs. "Erste Zeile ist allgemeines Lebensweisheits-Zitat ohne Bezug").

**Kontext schlägt Pauschalurteil.** Ein 100-Wort-Post kann perfekt sein (knappe Reflexion) oder schwach (zu wenig Substanz für die These). Schau dir an, was der Post erreichen WILL, und bewerte daran.

**Branchen-Sensibilität.** B2B-Software-Posts ticken anders als HR-Recruiting-Posts. Lifestyle-Content anders als technische Deep-Dives. Wende die Rubrik mit Augenmaß an, nicht als starres Regelwerk. Im Zweifel: erwähne den Branchen-Kontext in der Begründung.

**Bei niedrigen Noten konstruktiv bleiben.** Wenn ein Post 2/5 bekommt, schreibe nicht "schlechter Post". Schreibe, *was* nicht funktioniert und *wie* es besser ginge. Niemand verbessert sich durch Pauschalkritik.

**Bei fehlenden Daten ehrlich sein.** Wenn keine Engagement-Daten vorliegen, kann Dimension E nicht bewertet werden - das ist OK. Vermerke es und bewerte die anderen 4 sauber.

**Im Sub-Skill-Modus keine Eigeninitiative.** Der Caller (03-11-social-linkedin) steuert Aggregation und status.md. Dieser Skill liefert nur den JSON-Cache, nichts darüber hinaus.

## Bundled Resources

- `references/rubric.md` — Detail-Rubrik mit Score-Ankern pro Dimension, Anti-Patterns, Reality-Check
- `references/benchmarks.md` — Engagement-Benchmarks 2026 nach Branche und Account-Größe plus Format-Multiplikatoren
- `references/mta-integration.md` — Doppel-Modus-Architektur, Posts-CSV-Schema vom Caller, JSON-Cache-Schema, Aufruf-Konvention

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich - aber **nur im MTA-Standalone-Modus**:

- Outputs leben auf Google Drive (Sub-Folder-IDs aus `meta.json`)
- Markdown plus YAML-Frontmatter für Aggregat, CSV für Roh-Bewertungen
- Standard-Schluss-Format im Chat
- `status.md` und Dashboard auf Drive werden aktualisiert
- HTML-Report aus `reports/_shell.html` (aus Drive)

Im **Sub-Skill-Modus** gilt: kein `status.md`, kein HTML, kein Standard-Schluss - das macht der Caller. Stattdessen JSON-Cache im lokalen Arbeits-Cache unter `~/.cache/reachx-mta/<slug>/raw/post-quality-AKTEURSSLUG.json` - der Caller (`03-11-social-linkedin`) bündelt den Cache beim Upload nach Drive `assets/raw/`.

Im **Plain-Standalone-Modus** gilt: kein MTA-Pfad-Schema, kein status.md, kein Dashboard, kein Drive - reines Chat-Output, optional Datei im aktuellen Arbeits-Verzeichnis (nur nach Rückfrage).
