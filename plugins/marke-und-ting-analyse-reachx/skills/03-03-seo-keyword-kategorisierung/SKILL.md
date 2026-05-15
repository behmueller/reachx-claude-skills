---
name: 03-03-seo-keyword-kategorisierung
description: Kategorisiert den in 03-02-seo-keyword-recherche erstellten Keyword-Pool in branchenspezifische Cluster (z.B. Branded, Produkt-Themen, Anwendungsfälle, Long-Tail), Intent-Typen (informational, commercial, transactional, branded, navigational) und Funnel-Stufen (TOFU, MOFU, BOFU). Nutzt das Schema-vor-Lauf-Pattern - Phase A schlägt ein Cluster-Schema vor, Stratege reviewt und bestätigt, Phase B wendet das Schema auf den Pool an und schreibt seo-keyword-cluster.csv plus seo-cluster-zusammenfassung.md. Output ist der Input für 04-02-kanal-chancen-analyse und 04-05-90-tage-plan. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Keywords clustern, Themen-Cluster bilden, Intent-Typen vergeben oder Funnel-Stufen zuweisen will - auch bei Phrasen wie "Keywords clustern", "Keyword-Kategorisierung", "Themen-Cluster bilden", "Intent-Typen vergeben", "Funnel-Mapping", "TOFU MOFU BOFU", "SEO-Cluster", "Keyword-Pool kategorisieren". Setzt voraus, dass 03-02-seo-keyword-recherche gelaufen ist - bricht sonst ab.
---

# SEO-Keyword-Kategorisierung

Dritter und letzter SEO-Skill in Stufe 3. **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8). Wandelt den in `03-02-seo-keyword-recherche` erstellten flachen Keyword-Pool in eine **strategisch nutzbare Cluster-Struktur** um — branchenspezifisch, vom Strategen kuratiert.

**Drei Kategorisierungs-Dimensionen** pro Keyword:

1. **Cluster** — thematische Bündelung (z. B. "Aufmaß-Workflow", "Smart-Home-Integration", "Branded-Begriffe"). Die Cluster sind branchenspezifisch und werden im Schema vom Strategen festgelegt.
2. **Intent-Typ** — `informational | commercial | transactional | branded | navigational`. Verfeinert die heuristische Intent-Hypothese aus `03-02-seo-keyword-recherche`.
3. **Funnel-Stufe** — `TOFU | MOFU | BOFU` (Top/Middle/Bottom of Funnel). Ergänzend zum Intent-Typ, mit etwas anderer Brille (Funnel beschreibt Kunden-Reise-Stufe, Intent die konkrete Such-Absicht).

Der Output ist die Brücke zwischen Roh-Keyword-Daten und Strategie-Output:

- `audits/seo-keyword-cluster.csv` — vollständig kategorisierter Pool (für `04-02-kanal-chancen-analyse`, `04-04-forecast-modell`, `04-05-90-tage-plan`)
- `audits/seo-cluster-zusammenfassung.md` — Aggregat pro Cluster mit Volumen, Difficulty-Verteilung, Kunden-Abdeckung, strategischer Handlungs-Empfehlung
- `reports/08-seo-cluster.html` — visueller Cluster-Report für die MTA-Präsentation

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
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

- "Keywords clustern"
- "Keyword-Kategorisierung"
- "Themen-Cluster bilden"
- "Intent-Typen vergeben"
- "Funnel-Mapping"
- "TOFU MOFU BOFU"
- "SEO-Cluster"
- "Keyword-Pool kategorisieren"
- "SEO-Themen-Struktur"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen
- `03-02-seo-keyword-recherche` gelaufen → `audits/seo-keyword-pool.csv` und `audits/seo-keyword-pool.md` vorhanden
- Empfohlen: `data/kunde.md` (für Portfolio-Kategorien als Cluster-Inspiration)
- Empfohlen: `wettbewerber/identifikation-schema.md` (für Branchen-Kontext)
- Empfohlen: `data/briefing.md` (für Themen-Schwerpunkte des Strategen)

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `audits/keyword-kategorisierung-schema.md` existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B läuft.

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Inputs aus Drive, Outputs nach Drive — siehe `contracts.md` Abschnitt 4. Helper: `01-01-mta-projekt-init/scripts/drive.py`.

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug-aus-aufruf>")
[ -z "$MTA_JSON" ] || [ "$MTA_JSON" = "null" ] && { echo "✗ MTA nicht im Cache. Bitte 01-01-mta-projekt-init aufrufen."; exit 1; }
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

### Phase-Entscheidungs-Logik (Schritt 1 bei jedem Aufruf)

Prüfung beider Bedingungen erfolgt gegen Drive (via `drive.py list-children "$AUDITS_ID"`):

```
1. Existiert audits/keyword-kategorisierung-schema.md im Drive-Audits-Folder?
   - Nein → Phase A (Schema generieren)
   - Ja: Schema-File lesen (drive.py read <id>), Frontmatter parsen
     - status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
     - status: bestaetigt → Phase B (eigentliche Kategorisierung)
     - anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert audits/seo-keyword-cluster.csv bereits in Drive?
   - Nein → weiter mit Phase B
   - Ja → fragen: überschreiben / Backup-und-neu / abbrechen
```

Hinweis Schema-vor-Lauf: Phase A schreibt `audits/keyword-kategorisierung-schema.md` nach Drive via `drive.py upsert-text "$AUDITS_ID" "keyword-kategorisierung-schema.md" /tmp/schema.md "text/markdown"`. Der Stratege kann das Schema entweder direkt im Drive-Web-Editor anpassen (Markdown ist editierbar) oder lokal runterladen, editieren, neu hochladen. Phase B liest es robust zurück und prüft `status: bestaetigt`.

---

## Phase A — Cluster-Schema generieren

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1 und Schritt 0. Lies `audits/seo-keyword-pool.csv` plus `audits/seo-keyword-pool.md` aus Drive:

```bash
POOL_CSV_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "seo-keyword-pool.csv") | .id')
POOL_MD_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "seo-keyword-pool.md") | .id')
[ -z "$POOL_CSV_ID" ] && { echo "✗ audits/seo-keyword-pool.csv nicht gefunden."; exit 1; }
python3 "$DRIVE_PY" read "$POOL_CSV_ID" > /tmp/seo-keyword-pool.csv
python3 "$DRIVE_PY" read "$POOL_MD_ID" > /tmp/seo-keyword-pool.md
```

Wenn `seo-keyword-pool.csv` fehlt:

```
✗ audits/seo-keyword-pool.csv nicht gefunden.
Bitte zuerst 03-02-seo-keyword-recherche laufen lassen — der baut den Pool, auf dem dieser Skill aufsetzt.
```

Lies optionale Inputs aus Drive (jeweils via `drive.py list-children` + `drive.py read`):

- `data/kunde.md` (aus `$DATA_ID`) — für `portfolio_wie_kommuniziert[].kategorie` als Cluster-Anker
- `wettbewerber/identifikation-schema.md` (aus `$WB_ID`) — für `branchen_seed_keywords` und Branchen-Typ
- `data/briefing.md` (aus `$DATA_ID`) — für `themen_schwerpunkte` und vom Kunden genannte Anwendungsfälle

### Schritt A.2: Vor-Analyse des Pools

Berechne (für die Schema-Generierung):

- **Pool-Größe** und Quellen-Verteilung
- **Token-Frequenz**: Welche Wörter kommen über die Pool-Keywords hinweg häufig vor? (Top-50 Tokens mit Vorkommen, Stopwords ausgeschlossen)
- **Heuristische Intent-Verteilung** (aus Pool-Frontmatter)
- **Top-Gaps und ihre Wortstämme** (Cluster-Kandidaten von höchster Strategischer Relevanz)
- **Branded-Cluster-Größe** (alle Keywords mit `intent_hypothese: branded`)
- **Ahrefs-Parent-Topics** (wenn vorhanden) — Ahrefs liefert eine eigene Cluster-Vorschlags-Ebene, die als Inspiration für unsere Cluster genutzt werden kann

### Schritt A.3: Cluster-Vorschläge ableiten

Cluster-Vorschläge folgen einer **gestaffelten Logik**:

1. **Branded-Cluster** (immer dabei): Cluster `branded_kunde` für Kunden-Markensynonyme, optional `branded_wettbewerber_X` für jeden WB, dessen Markennamen-Keywords im Pool sind
2. **Produkt-/Portfolio-Cluster**: Pro Portfolio-Kategorie aus `data/kunde.md` ein Cluster-Vorschlag (z. B. "kabel-werkzeuge", "messer-werkzeuge"). Mapping: Keywords werden Token-Match-basiert zugewiesen.
3. **Anwendungs-/Themen-Cluster** aus Token-Frequenz: Top-Tokens mit Vorkommen ≥ 5 im Pool werden als Cluster-Anker vorgeschlagen
4. **Gap-Cluster** aus den `gap_cluster`-Auffälligkeiten in `seo-keyword-pool.md` Frontmatter (direkt übernehmen)
5. **Long-Tail-Cluster** für Keywords mit `quellen` enthält `*_longtail` (separater "Long-Tail-Bucket" pro Themen-Stamm)
6. **Generic-Cluster** als Sammelbecken für Keywords, die zu keinem spezifischen Cluster passen

**Cluster sind nicht exklusiv** — ein Keyword kann mehreren Clustern angehören (z. B. ein Long-Tail-Keyword zu einem Produkt-Cluster UND zum "Long-Tail-Bucket"). Der Skill nutzt dafür eine `primaer_cluster` (Pflicht) und optional `sekundaer_cluster` (Liste).

### Schritt A.4: Intent-Typ-Definitionen anpassen

Default-Intent-Typen aus `03-02-seo-keyword-recherche/reference/wettbewerbs-gap-logik.md` Abschnitt 4: `branded | transactional | commercial | informational | navigational`. Plus `unklar` als Fallback.

Im Schema werden pro Intent-Typ:

- Default-Heuristik-Trigger gelistet (Schlüsselbegriffe)
- **Branchen-Anpassungen** vorgeschlagen — z. B. bei B2B-SaaS: "demo", "trial", "vergleich" sind oft commercial, bei E-Commerce sind sie eher transactional
- Edge-Case-Hinweise für die Strategen-Review

### Schritt A.5: Funnel-Stufen-Mapping

Funnel-Stufen sind ergänzend zum Intent-Typ:

| Funnel-Stufe | Bedeutung | Typischer Intent |
|---|---|---|
| **TOFU** (Top of Funnel) | Awareness, allgemeine Informations-Suche | informational, oft generisch |
| **MOFU** (Middle of Funnel) | Consideration, Vergleich, Lösungsbewertung | commercial, "vs", "vergleich", "alternativen zu" |
| **BOFU** (Bottom of Funnel) | Decision, Kauf-/Buchungs-Absicht | transactional, "kaufen", "preis", "demo buchen" |

Plus **branded** als orthogonale Dimension (kann auf jeder Funnel-Stufe vorkommen).

Default-Mapping-Regeln werden im Schema dokumentiert, branchen-spezifisch angepasst.

### Schritt A.6: `audits/keyword-kategorisierung-schema.md` schreiben

Schreibe das vollständige Schema nach `reference/kategorisierung-schema-template.md`. Setze `status: vorgeschlagen`. Hochladen nach Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "keyword-kategorisierung-schema.md" \
  ~/.cache/reachx-mta/<slug>/keyword-kategorisierung-schema.md "text/markdown"
```

Sektionen:

- **Frontmatter**: Skill-Metadaten, Pool-Größe, Anzahl vorgeschlagener Cluster, Anzahl Intent-Typen, Default-Funnel-Mapping
- **Body**:
  - Übersicht der Pool-Daten (was der Skill gesehen hat)
  - Cluster-Vorschläge (pro Cluster: Name, Beschreibung, Anker-Tokens, ungefähre Größe, Beispiel-Keywords)
  - Intent-Typ-Definitionen mit Branchen-Anpassung
  - Funnel-Stufen-Mapping mit Branchen-Beispielen
  - Pflicht-Review-Sektion für den Strategen mit konkreten Eingriffspunkten

### Schritt A.7: Schluss-Format Phase A

```
✓ 03-03-seo-keyword-kategorisierung Phase A abgeschlossen.

Outputs:
- audits/keyword-kategorisierung-schema.md — Cluster-Schema (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Pool-Größe:        N Keywords
- Cluster:           K vorgeschlagen (J davon aus Top-Gaps)
- Intent-Typen:      5 Standard + Branchen-Anpassung dokumentiert
- Funnel-Mapping:    TOFU/MOFU/BOFU pro Intent-Typ

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Cluster-Namen, -Beschreibungen und -Anker-Tokens. Cluster zusammenlegen, splitten, umbenennen oder löschen wie nötig. Intent-Typ-Heuristiken branchen-anpassen.
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Update `status.md` mit `blockiert`-Eintrag (aus Drive lesen, anpassen, zurückschreiben):

```bash
STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > /tmp/status.md
# blockiert-Eintrag im Frontmatter ergänzen
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"
```

Schreibe `blockiert` in `status.md`:

```yaml
blockiert:
  - skill: 03-03-seo-keyword-kategorisierung (Phase B)
    wartet_auf: "Strategen-Review von audits/keyword-kategorisierung-schema.md"
```

---

## Phase B — Eigentliche Kategorisierung

### Schritt B.1: Schema-Validierung

Lies `audits/keyword-kategorisierung-schema.md` aus Drive (über die in Schritt 0 ermittelte `$AUDITS_ID`):

```bash
SCHEMA_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "keyword-kategorisierung-schema.md") | .id')
python3 "$DRIVE_PY" read "$SCHEMA_ID" > /tmp/schema.md
```

Prüfe:

1. `status: bestaetigt`? Sonst Abbruch
2. Mindestens 3 Cluster definiert?
3. Jeder Cluster hat: Name, Beschreibung, Anker-Tokens (mindestens einer), Intent-Mapping-Hinweise
4. Intent-Typen-Liste vollständig? Funnel-Mapping definiert?

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Existenz-Check Output

Wenn `audits/seo-keyword-cluster.csv` oder `audits/seo-cluster-zusammenfassung.md` bereits existieren: fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Cluster-Zuweisung pro Keyword

Pro Keyword im Pool die Cluster-Zuweisung berechnen:

**Regel-Schicht (in Reihenfolge):**

1. **Branded**: wenn `intent_hypothese: branded` oder Keyword enthält Token aus Kunden-Synonymen → `primaer_cluster: branded_kunde`
2. **WB-Branded**: wenn Keyword Token aus WB-Markennamen enthält → `primaer_cluster: branded_wettbewerber_<wb-slug>`
3. **Anker-Token-Match**: pro Cluster aus dem Schema, prüfe ob mindestens ein `anker_token` im Keyword vorkommt (Token-Match, Substring kompatibel zur Schema-Definition):
   - Wenn genau ein Cluster matched → primärer Cluster
   - Wenn mehrere matchen → primärer Cluster ist der mit dem **spezifischsten Anker-Token** (längstes Token gewinnt), Rest als `sekundaer_cluster`
4. **Ahrefs-Parent-Topic-Fallback**: wenn das Schema mit Ahrefs-Parent-Topics arbeitet UND das Keyword einen Parent-Topic hat → entsprechender Cluster
5. **Fallback**: `primaer_cluster: generic`

Pro Keyword auch:

- **Intent-Typ**: aus Schema-Heuristik neu berechnet (Schema kann von der `intent_hypothese` aus `seo-keyword-pool.csv` abweichen — Schema gewinnt)
- **Funnel-Stufe**: aus Intent-Typ + Cluster-Mapping (z. B. ein "Vergleichs-Cluster" pusht eher zu MOFU, auch wenn das Keyword informational klingt)

### Schritt B.4: Cluster-Score pro Cluster berechnen

Pro Cluster aggregierte Metriken:

```
cluster_score = sum(volumen_pro_keyword) × abdeckung_kunde_faktor × difficulty_bonus
```

Wobei:

- `abdeckung_kunde_faktor`:
  - 0.5 wenn Kunde >50% der Cluster-Keywords im Top-10 abdeckt (Cluster ist schon stark, weniger Potenzial)
  - 1.0 wenn Kunde 0-50% abdeckt (Mid-Zone, Standard)
  - 1.5 wenn Kunde 0% abdeckt UND mindestens 1 WB stark abdeckt (Cluster ist ein klarer Gap-Cluster — höchster strategischer Wert)
- `difficulty_bonus`:
  - 1.4 wenn Median-Difficulty im Cluster ≤ 30 (Sweet-Spot)
  - 1.0 sonst

Dieser Score steuert die Sortierung im Output und die Priorisierung im Strategen-Report.

### Schritt B.5: Cluster-Auffälligkeiten

Pro Cluster und über alle Cluster hinweg die strategischen Beobachtungen extrahieren:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_gap_cluster` | Kunde 0%-Abdeckung in einem Cluster mit Volumen ≥ 1000 und WB-Top-10-Präsenz | "Cluster 'Aufmaß-Workflow' (4.200 Volumen, 14 Keywords) — Kunde rankt für keines davon im Top-100, beta-solutions auf 9 von 14 im Top-10" |
| `kunde_dominant_cluster` | Kunde >70%-Top-10-Abdeckung | "Cluster 'Branded' wird vom Kunden dominiert — solides Marken-Search-Fundament" |
| `sweet_spot_cluster` | Cluster mit Median-Difficulty ≤ 30 UND Volumen ≥ 1500 UND Kunden-Abdeckung < 50% | "Cluster 'Smart-Home-Integration' im Sweet-Spot: niedrige Difficulty (Median 22), 2.800 Volumen, Kunde rankt für 15% — schneller Win" |
| `cluster_dominiert_von_wb` | Ein WB hat >60% der Top-10-Positionen im Cluster | "Cluster 'Profi-Werkzeuge' wird von alpha-tech dominiert — Strategie: Differenzierung statt Konkurrenz auf alpha-tech-starken Keywords" |
| `cluster_zu_klein` | Cluster mit < 5 Keywords — möglicher Hinweis, dass Cluster-Definition zu eng war | "Cluster 'XYZ' nur 3 Keywords — eventuell mit anderem Cluster zusammenlegen oder löschen" |
| `bofu_unterversorgt` | < 10% des Pools im Funnel BOFU | "Pool ist stark Awareness-lastig — kommerzielle Keywords mit Kauf-Intent fehlen, eventuell durch gezielte Long-Tail-Recherche ergänzen" |

Cluster-Auffälligkeiten werden im Markdown und HTML-Report prominent gezeigt — sie sind das **Roh-Material für die MTA-Strategie-Slide**.

### Schritt B.6: CSV-Output `audits/seo-keyword-cluster.csv`

Vollständiges Schema in `reference/cluster-output-schema.md`. Spalten (Erweiterung über die Pool-CSV hinaus):

```
keyword, keyword_normalisiert, sistrix_volumen, ahrefs_volumen, difficulty, ahrefs_cpc, gap_zu_kunde, gap_typ, gap_score,
primaer_cluster, sekundaer_cluster, intent_typ, funnel_stufe, kategorisierung_quelle, kategorisierungs_konfidenz,
ranking_kunde_position, ranking_kunde_url, ranking_top_wb_slug, ranking_top_wb_position,
datenstand_iso
```

Wichtig:

- `sekundaer_cluster` ist Pipe-getrennte Liste (mehrere möglich)
- `kategorisierung_quelle`: welche Regel hat den Cluster zugewiesen (`branded_match | anker_token_match | ahrefs_parent_topic | manual_override | fallback_generic`)
- `kategorisierungs_konfidenz`: `hoch | mittel | niedrig` (heuristisch — bei mehreren Matches `mittel`, bei reinem Fallback `niedrig`, bei einzigem Match `hoch`)

### Schritt B.7: Aggregat-Markdown `audits/seo-cluster-zusammenfassung.md`

Body strukturiert nach:

- **Übersicht**: Pool-Größe, Anzahl Cluster, durchschnittliche Cluster-Größe, Top-Cluster nach Score
- **Top-Cluster-Tabelle** (sortiert nach Score):
  - Cluster-Name, Beschreibung, Anzahl Keywords, Kumuliertes Volumen, Median-Difficulty, Kunden-Abdeckung in %, Cluster-Score
- **Pro Cluster ein Sub-Block** (max 12-15 Cluster, Rest in CSV):
  - Definition + Anker-Tokens
  - Top-5 Keywords nach Volumen
  - Funnel-Verteilung im Cluster
  - Kunden-Stärke / -Schwäche
  - Strategische Handlungs-Empfehlung (1-2 Sätze)
- **Intent-Verteilung pool-weit** als Tabelle
- **Funnel-Verteilung pool-weit** als Tabelle
- **Auffälligkeiten** (sortiert nach Relevanz)
- **Vorbereitung für Folge-Skills**: Hinweis, welche Cluster-Score-Top-3 als Argumente für `04-02-kanal-chancen-analyse` und `04-05-90-tage-plan` taugen

### Schritt B.8: HTML-Report `reports/08-seo-cluster.html`

Aus `reports/_shell.html`:

- Stat-Strip oben: Anzahl Cluster, Top-Score-Cluster, Anzahl Sweet-Spot-Cluster, Anzahl Gap-Cluster
- Sticky-TOC zu allen Cluster-Sektionen plus Auffälligkeiten
- **Cluster-Heatmap** (Volumen × Difficulty als Bubble-Visualisierung — Bubble-Größe = Cluster-Volumen, Position = Median-Difficulty, Farbe = Kunden-Abdeckung)
- **Pro Cluster** ein `details class="skill"`-Block mit Cluster-Definition, Top-Keywords-Tabelle, Funnel-Mini-Verteilung
- **Intent/Funnel-Verteilungs-Block** mit ASCII- oder SVG-Visualisierung
- **Auffälligkeiten-Block** als `.suggestion`-Block — die strategisch wichtigsten Beobachtungen mit Handlungs-Empfehlungen
- Footer

### Schritt B.8b: Outputs nach Drive hochladen

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-keyword-cluster.csv" \
  ~/.cache/reachx-mta/<slug>/seo-keyword-cluster.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-cluster-zusammenfassung.md" \
  ~/.cache/reachx-mta/<slug>/seo-cluster-zusammenfassung.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "08-seo-cluster.html" \
  ~/.cache/reachx-mta/<slug>/08-seo-cluster.html "text/html"
```

### Schritt B.9: Dashboard-Update und status.md

Standard-Pattern (siehe `contracts.md` Abschnitt 3 und 7): `reports/index.html` und `status.md` aus Drive lesen, anpassen, zurückschreiben.

- `03-03-seo-keyword-kategorisierung` in `schritte_done` (Phase B abgeschlossen)
- Aus `blockiert` entfernen
- Reports-Liste um `08-seo-cluster.html`
- Stat-Strip aktualisieren (Anzahl Cluster, Top-Score-Cluster)
- `naechster_empfohlen`:
  - Wenn Stufe 3 noch nicht voll: nächster Audit-Skill (üblicherweise `03-05-sea-google-ads-check` oder `03-14-web-tech-und-tracking`, parallel möglich)
  - Wenn Stufe 3 weitgehend durch: `04-02-kanal-chancen-analyse` (Synthese-Stufe)

### Schritt B.10: Standard-Schlussformat im Chat

```
✓ 03-03-seo-keyword-kategorisierung Phase B abgeschlossen.

Outputs:
- audits/seo-keyword-cluster.csv — N Keywords in K Clustern (mit Intent + Funnel)
- audits/seo-cluster-zusammenfassung.md — Aggregat mit Top-Cluster, Auffälligkeiten
- reports/08-seo-cluster.html — Cluster-Heatmap + Strategie-Empfehlungen
Status aktualisiert in: status.md

Cluster-Statistik:
- Cluster gesamt:           K
- Sweet-Spot-Cluster:       S (niedrige Difficulty + relevantes Volumen)
- Gap-Cluster (Kunde 0%):   G
- Cluster vom Kunden dom.:  D
- Top-Score-Cluster:        <Name> (Score X,X)

[Top 3 strategische Beobachtungen:]
⚠ Cluster-Insights:
1. <Auffälligkeit 1>
2. <Auffälligkeit 2>
3. <Auffälligkeit 3>

[Wenn bofu_unterversorgt:]
ℹ Funnel-Hinweis
- Pool stark TOFU-lastig — kommerzielle Keywords fehlen, in der MTA-Story als Lücke ausweisen oder gezielt nachziehen.

Nächste Schritte:
1. 04-02-kanal-chancen-analyse — synthetisiert SEO mit den anderen Audits (sobald genug Audits da sind)
2. (parallel möglich, falls noch nicht durch) 03-05-sea-google-ads-check / 03-06-sea-meta-ads-library-check / 03-14-web-tech-und-tracking

Damit ist das SEO-Audit-Triple komplett. Vorschlag: Live-Test mit echtem Kunden, um die SEO-Pipeline (Sichtbarkeit → Pool → Cluster) im Verbund zu validieren.

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/kategorisierung-schema-template.md` — Phase-A-Output-Format mit Default-Cluster-Templates pro Branchen-Typ
- `reference/cluster-und-intent-methodik.md` — Definitionen der Intent-Typen und Funnel-Stufen mit Branchen-Anpassungs-Beispielen
- `reference/cluster-output-schema.md` — Phase-B-CSV- und Markdown-Schema mit Validierungs-Regeln

## Edge Cases

- **Pool ist klein (< 50 Keywords)** → Cluster-Bildung wird hart: heuristisch mindestens 3 Cluster (Branded, Hauptthema, Long-Tail/Sonstige). Im Schema-Vorschlag im Body Hinweis, dass mit kleinem Pool die Cluster eher grob bleiben.

- **Pool ist sehr groß (> 1500 Keywords)** → Cluster-Bildung hat Reibung: zu viele Token-Frequenz-Kandidaten. Skill nutzt in Phase A einen schärferen Token-Frequenz-Threshold (z. B. nur Tokens mit Vorkommen ≥ 10). Im Schema-Body Hinweis, dass Stratege ggf. Cluster zusammenlegen sollte.

- **Schema hat 30+ Cluster** → Hinweis im Phase-B-Schluss, dass das viel ist und im HTML-Report nur Top-15-Cluster ausgeklappt dargestellt werden, Rest in CSV.

- **Keyword passt zu keinem Cluster** → `primaer_cluster: generic`, `kategorisierungs_konfidenz: niedrig`. Wenn >20% des Pools im `generic`-Bucket landen: Auffälligkeit `pool_schlecht_clusterbar` mit Empfehlung, dass das Schema in einer zweiten Runde verfeinert werden sollte.

- **Branded-Cluster ist leer** → Hinweis im Body "Kunde scheint keine relevante Brand-Such-Aktivität zu haben (oder Brand-Synonyme im Pool fehlen) — manueller Cross-Check empfohlen".

- **Stratege wünscht Re-Run mit verändertem Schema** → Override-Argument "Schema überarbeiten" → Skill löscht (mit Backup) den existierenden Phase-B-Output, lässt das Schema auf `status: vorgeschlagen` zurückfallen und bricht ab. Stratege editiert, bestätigt, Skill läuft Phase B neu.

- **Re-Run mit identischem Schema bei neuem Pool-Stand** (z. B. nach `03-02-seo-keyword-recherche` mit Override "Long-Tail nachziehen") → Skill erkennt, dass der Pool jünger ist als das Cluster-CSV, fragt: "Pool wurde aktualisiert, Cluster neu berechnen?" → Re-Run der Phase B mit existierendem Schema.

- **Ahrefs-Parent-Topics sind unbalanciert** (Ahrefs gruppiert sehr aggressiv und das passt nicht zum branchen-spezifischen Cluster-Schema) → Schema-Template sieht `nutzung_ahrefs_parent_topics: optional` vor; Stratege entscheidet im Review, ob die Ahrefs-Cluster mitlaufen sollen oder nur die Token-Anker.

- **Konfidenz-Verteilung ist schlecht** (>50% niedrige Konfidenz) → Auffälligkeit `kategorisierung_unsicher` mit Empfehlung, das Schema zu erweitern (mehr Anker-Tokens pro Cluster, oder neue Cluster definieren).

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B läuft niemals ohne `status: bestaetigt` in Phase-A-Output (geprüft auf Drive)
- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/seo-keyword-cluster.csv`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Daten (via `drive.py upsert-text`)
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (`drive.py upsert-text`)
- HTML-Report aus `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- **CSV ist Single-Source-of-Truth** für die Folge-Skills (Synthese-Stufe)
- **Cluster-Definitionen sind kuratiert** — keine reine Token-Mechanik-Ausgabe, der Stratege gestaltet im Schema-Review
