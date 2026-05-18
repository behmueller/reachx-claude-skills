---
name: 03-02-seo-keyword-recherche
description: Erweitert die in 03-01-seo-sichtbarkeit-und-rankings erfasste CSV-Basis um Long-Tail-Variationen (Ahrefs matching-/related-/suggestions, primär), Wettbewerbs-Gap-Keywords (auf denen ein Wettbewerber rankt aber der Kunde nicht), Branchen-Seed-Keywords aus dem identifikation-schema und reichert den Pool mit Ahrefs-Keyword-Difficulty, Volumen, CPC, Intent-Flags und Parent-Topic an. Sistrix dient optional zur DACH-Long-Tail-Ergänzung und Volumen-Cross-Validierung. Output ist audits/seo-keyword-pool.csv als erweiterte Roh-Datenbasis plus audits/seo-keyword-pool.md als Stratege-Aggregat mit Top-Gaps, Difficulty-Verteilung, Intent-Verteilung und Cluster-Vorbereitung. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext die Keyword-Basis erweitern oder Wettbewerbs-Gaps finden will - auch bei Phrasen wie "Keyword-Recherche", "Keyword-Pool aufbauen", "Long-Tail finden", "Wettbewerbs-Gaps", "Keyword-Gaps", "auf welchen Keywords rankt Wettbewerber X aber Kunde nicht", "Keyword-Universe", "SEO-Keyword-Erweiterung", "Difficulty-Werte ergänzen", "Ahrefs-Anreicherung". Setzt voraus, dass 03-01-seo-sichtbarkeit-und-rankings gelaufen ist und audits/seo-keywords.csv vorhanden ist - bricht sonst mit Hinweis ab. Ahrefs-MCP ist Pflicht (Skill bricht ab, wenn nicht verbunden); Sistrix ist optional.
---

# SEO-Keyword-Recherche

Zweiter Skill in Stufe 3. Baut auf der CSV-Roh-Datenbasis aus `03-01-seo-sichtbarkeit-und-rankings` auf und erweitert sie zu einem **strategisch nutzbaren Keyword-Pool** mit:

1. **Long-Tail-Variationen** der wichtigsten Keywords des Kunden — **primär via Ahrefs** (`keywords-explorer-matching-terms`, `-related-terms`, `-search-suggestions`), optional über Sistrix als DACH-Ergänzung
2. **Wettbewerbs-Gap-Keywords** — Keywords, auf denen ein oder mehrere Wettbewerber stark ranken, der Kunde aber nicht (oder schlecht). Die wertvollste Output-Kategorie für die MTA-Story.
3. **Branchen-Seed-Keywords** aus `wettbewerber/identifikation-schema.md` plus daraus abgeleitete generische Branchen-Keywords als Cross-Check
4. **Ahrefs-Vollanreicherung** — Keyword-Difficulty, Ahrefs-Volumen, CPC, Intent-Flags (`is_branded`, `is_transactional`, `is_commercial`, `is_informational`) und `parent_topic` für die Top-Kandidaten (gebatcht bis 1000 Keywords/Request)

Output: erweiterte CSV plus Stratege-Aggregat-Markdown. Diese Outputs sind die Eingabe für `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf, baut Cluster und Intent-Typen).

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

- "Keyword-Recherche"
- "Keyword-Pool aufbauen"
- "Long-Tail finden"
- "Wettbewerbs-Gaps"
- "Keyword-Gaps"
- "auf welchen Keywords rankt Wettbewerber X aber Kunde nicht"
- "Keyword-Universe für [Kunde]"
- "SEO-Keyword-Erweiterung"
- "Difficulty-Werte ergänzen"
- "Ahrefs-Anreicherung"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen
- `03-01-seo-sichtbarkeit-und-rankings` gelaufen → `audits/seo-keywords.csv` und `audits/seo-sichtbarkeit.md` vorhanden
- **Ahrefs-MCP-Zugang Pflicht** — alle Tools mit Prefix `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-*` müssen verfügbar sein. Skill bricht ab, wenn nicht verbunden (siehe Schritt 1). Begründung: Ahrefs ist seit Tool-Anbindung Primary-Quelle für Long-Tail, Difficulty, Intent und Volumen.
- **Sistrix-Zugang optional** — wenn vorhanden, wird Sistrix-Long-Tail als DACH-Ergänzung mitgezogen und Sistrix-Volumen zur Cross-Validierung gegen Ahrefs verglichen. Wenn nicht vorhanden: Skill läuft im **Reduced-Modus ohne Sistrix** (keine `sistrix_*`-Spalten gefüllt, kein Cross-Check), Hinweis im Schluss-Format.
- Empfohlen: `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` — für Branchen-Seed-Keywords. Wenn nicht vorhanden: Skill läuft trotzdem, nutzt nur CSV-Basis + Ahrefs-Expansion

## Geo-vs-generisch-Klassifikation (Standard-Schritt, nicht optional)

Pro Seed-Keyword aus den Top-30-Kunden-Keywords und Top-20-Gap-Keywords muss der Skill feststellen, welchen Such-Typ das Keyword bedient. Das bestimmt, welche SEO-Taktik zieht:

- **Lokal aussteuerbar** — Keyword löst bei SERP-Check einen Local Pack aus (Google Maps-Box oberhalb der organischen Ergebnisse). Beispiele: „Zahnarzt Frankfurt", „Umzugsunternehmen Berlin". Diese Keywords sind über GMB und lokale Landingpages angreifbar, nicht primär über Content-Marketing.
- **Bundesweit / intent-getrieben** — kein Local Pack sichtbar, rein organische Ergebnisse oder Shopping. Klassische SEO-Content-Taktik.

**Durchführung**: für die Top-Seed-Keywords einen stichprobenartigen SERP-Check via Ahrefs `keywords-explorer-overview` (Feld `local_pack` oder `serp_features`) oder via manuellem Hinweis in der Schema-Datei. Bei unklarer Datenlage: im Pool-Markdown als „Local-Pack-Status ungeprüft" markieren.

**Lokale Service-Keywords mit Orts-Zusatz** (z. B. „[Leistung] [Stadt]", „[Leistung] in der Nähe") werden als eigene Achse im Pool erfasst — Spalte `keyword_geo_typ: lokal | ueberregional | unklar`.

**Optionaler Ausland-Intent-Block**: Wenn die Branche oder das Briefing auf internationale Konkurrenz hindeutet (z. B. medizinische Leistungen mit Patienten aus Nachbarländern, Anbieter in einer Grenzregion), ergänzt der Skill einen separaten Cluster mit Keywords, die Orts-Namen oder Sprachen-Bezüge aus den relevanten Herkunftsländern enthalten (z. B. türkisch- oder polnischsprachige Suchbegriffe, Keywords mit Orts-Zusatz für diese Länder). Dieses Block wird nur aufgebaut, wenn das Briefing oder `data/kunde.md` einen entsprechenden Hinweis enthält — nicht standardmäßig.

## Ablauf

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
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/` für Pool-Zwischenergebnisse und Ahrefs-Roh-Caches.

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Lies `audits/seo-keywords.csv` aus Drive:

```bash
KEYWORDS_CSV_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "seo-keywords.csv") | .id')
if [ -z "$KEYWORDS_CSV_ID" ] || [ "$KEYWORDS_CSV_ID" = "null" ]; then
  echo "✗ audits/seo-keywords.csv nicht gefunden. Bitte zuerst 03-01-seo-sichtbarkeit-und-rankings laufen lassen."
  exit 1
fi
python3 "$DRIVE_PY" read "$KEYWORDS_CSV_ID" > ~/.cache/reachx-mta/<slug>/seo-keywords.csv
```

Wenn die CSV fehlt:

```
✗ audits/seo-keywords.csv nicht gefunden.
Bitte zuerst 03-01-seo-sichtbarkeit-und-rankings laufen lassen — der baut die Roh-Datenbasis auf, auf der dieser Skill aufsetzt.
```

Lies `audits/seo-sichtbarkeit.md` aus Drive für die Frontmatter (Akteurs-Liste, statistiken, schema_version). Validiere, dass `schema_version` kompatibel ist.

```bash
SICHTBARKEIT_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "seo-sichtbarkeit.md") | .id')
python3 "$DRIVE_PY" read "$SICHTBARKEIT_ID" > /tmp/seo-sichtbarkeit.md
```

Prüfe optionale Inputs (alle via `drive.py read <id>` aus den jeweiligen Sub-Foldern):

- `wettbewerber/identifikation-schema.md` (aus `$WB_ID`) → für `branchen_seed_keywords` und `branchenportale_relevant`
- `data/kunde.md` (aus `$DATA_ID`) → für `portfolio_wie_kommuniziert.kategorie` als Cross-Check für Intent-Hypothesen
- `data/briefing.md` (aus `$DATA_ID`) → für `wettbewerber_genannt` und ggf. erwähnte Keyword-Themen

**Ahrefs-Healthcheck (Pflicht):**

- Prüfe Verfügbarkeit der MCP-Tools `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-overview`, `-matching-terms`, `-related-terms`, `-search-suggestions`
- Ein Probelauf via `mcp__1d9710a6-f270-4555-88f8-e4367948d936__subscription-info-limits-and-usage` (oder ein 1-Keyword `keywords-explorer-overview`-Aufruf) zeigt, ob Auth funktioniert
- Wenn nicht verbunden oder Auth fehlschlägt:

```
✗ Ahrefs-MCP nicht verbunden oder Healthcheck fehlgeschlagen.
Dieser Skill setzt Ahrefs als Primärquelle voraus (Long-Tail, Difficulty, Intent, Volumen).
Bitte Ahrefs-MCP verbinden und Skill erneut aufrufen.
```

**Sistrix-Check (optional):** Prüfe Sistrix-Zugang wie in `03-01-seo-sichtbarkeit-und-rankings/reference/sistrix-api-nutzung.md`. Setze `sistrix_modus: voll`, `partiell` (Auth ok, aber bestimmte Endpoints ausgefallen) oder `aus` (kein Zugang). **Kein Abbruch bei fehlendem Sistrix.**

### Schritt 2: Existenz-Check Output-Dateien

Prüfe via `drive.py list-children "$AUDITS_ID"`, ob `seo-keyword-pool.csv` oder `seo-keyword-pool.md` schon im Audits-Folder liegen. Wenn ja, frage:

- **(a) überschreiben** — `drive.py upsert-text` überschreibt sauber
- **(b) Backup-und-neu** — alte Versionen werden zuerst nach `audits/_backup/seo-keyword-pool-ISO.{csv,md}` umkopiert (find-or-create `_backup`-Sub-Folder via `find-or-create-folder`)
- **(c) abbrechen**

### Schritt 3: Basis-Keyword-Pool aus der CSV laden

Lies `audits/seo-keywords.csv`. Lege eine interne Datenstruktur an:

```
keyword_pool = {
  "<keyword-normalisiert>": {
    keyword_original: <ursprünglicher Text>,
    rankings_pro_akteur: {
      <akteurs_slug>: {position, suchvolumen, ranking_url, sistrix_competition}
    },
    erfasst_im_basislauf: true,
    quellen: ["sistrix_csv"]
  }
}
```

**Keyword-Normalisierung**: lowercase, mehrfache Leerzeichen zu einem, führende/schließende Whitespaces entfernen. Umlaute bleiben (sowohl Sistrix als auch Ahrefs indexieren Umlaute separat). Sonderzeichen bleiben.

Statistik: Anzahl unique Keywords im Basis-Pool zählen.

### Schritt 4: Wettbewerbs-Gap-Berechnung

**Die wertvollste Kategorie für die MTA-Story.** Siehe `reference/wettbewerbs-gap-logik.md` für die genaue Regelung.

Kurzgefasst:

1. Für jedes Keyword im Pool: prüfe, ob der **Kunde** unter den `rankings_pro_akteur` vorkommt.
2. Wenn nein → Gap-Kandidat
3. Wenn ja, aber Position des Kunden > 30 UND mindestens ein WB ist auf Position ≤ 10 → "weicher Gap"
4. Filtere Gap-Kandidaten nach:
   - **Suchvolumen-Mindesthöhe**: 200/Monat (konfigurierbar via Override im Aufruf). Quelle: `sistrix_volumen` aus CSV; wenn leer, später in Schritt 8 via Ahrefs ergänzt und Gap-Filter nachgezogen.
   - **Branded-Filter**: Keywords, die einen Wettbewerber-Markennamen enthalten, werden ausgeschlossen (außer der Kunde rankt für die WB-Marke — dann eine eigene Auffälligkeit). In Schritt 8 wird das `is_branded`-Flag aus Ahrefs als zusätzliche Validierung herangezogen — siehe `reference/wettbewerbs-gap-logik.md`.
   - **Aggregator-Filter**: Keywords, deren Ranking-URLs primär Aggregatoren sind (Wikipedia, Foren, große Vergleichsportale), werden ausgeschlossen
5. Sortiere die verbleibenden Gaps nach (Suchvolumen × Anzahl WBs-im-Top-10)

In die Pool-Datenstruktur ergänzen: `gap_zu_kunde: true | false`, `gap_typ: hart | weich | null`, `gap_score: <float>`.

### Schritt 5: Long-Tail-Expansion — primär Ahrefs, optional Sistrix-DACH-Ergänzung

Für die **Top-Kunden-Keywords** (Top 30 nach Suchvolumen × Position-Gewicht, aus dem Basis-Pool) und für die **Top-Gap-Keywords** (Top 20 nach Gap-Score):

**5a) Ahrefs-Expansion (primär, immer ausgeführt):**

Pro Seed-Keyword drei parallele Ahrefs-Calls:

1. `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-matching-terms` — Phrase-Match-Variationen mit `volume_from: 50`, `limit: 50`, Country aus `meta.json.region` (Default `de`)
2. `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-related-terms` — thematisch verwandte Keywords, `limit: 30`
3. `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-search-suggestions` — Auto-Suggest-/W-Fragen-Variationen, `limit: 30`

Rohdaten cachen: `~/.cache/reachx-mta/<slug>/audits/raw/ahrefs-<endpoint>-<seed-slug>.json` (lokal, später komprimiert nach Drive `assets/raw/`). Bei Spalten-Fehler die Spalten aus der Fehlermeldung übernehmen (siehe `reference/ahrefs-api-nutzung.md`).

**5b) Sistrix-Expansion (optional, nur wenn `sistrix_modus != aus`):**

Pro Seed-Keyword `keyword.related` (Limit 100) plus bei Bedarf `keyword.suggestions` als DACH-Ergänzung — vor allem für deutschsprachige Long-Tail-Phrasen, die Ahrefs nicht kennt.

**5c) Mergen in den Pool:**

Pro neu gefundenes Keyword:

- Bereits im Pool? → nicht erneut aufnehmen, aber `quellen` um den entsprechenden Tag ergänzen (`ahrefs_matching`, `ahrefs_related`, `ahrefs_suggestions`, `sistrix_longtail`, `sistrix_suggestions`)
- Filter:
  - **Min-Suchvolumen 50/Monat** (Long-Tail darf kleiner sein als der Gap-Filter)
  - Branded-Filter wie in Schritt 4
- Neue Keywords mit:
  - `erfasst_im_basislauf: false`
  - `quellen: ["ahrefs_matching", ...]`
  - `seed_keyword: <ursprung>`
  - `rankings_pro_akteur: {}` (initial leer, optional in Schritt 6 angereichert)
  - Wenn aus Ahrefs gekommen: `ahrefs_volumen`, `ahrefs_cpc`, `ahrefs_parent_topic` und Intent-Flags direkt mitnehmen (sparen Roundtrip)

Hard-Cap: maximal **500 neue Long-Tail-Keywords** insgesamt (zuvor 300). Begründung: Ahrefs-Batching-Effizienz bei der späteren Anreicherung erlaubt deutlich mehr Volumen. Konfigurierbar via Override `longtail_cap: <N>`.

### Schritt 6: Optional — Rankings für Long-Tail-Keywords

**Optionaler Schritt** (Default: nicht ausführen, weil Credit-intensiv). Aktiviert via Nutzer-Override "auch Rankings für Long-Tail".

Wenn aktiviert: pro neuem Long-Tail-Keyword Sistrix-Lookup für die Top-3 wichtigsten Akteure (Kunde + Top-2-WBs nach VI aus `seo-sichtbarkeit.md` Frontmatter). Ergänze die `rankings_pro_akteur`-Daten.

Wenn nicht aktiviert: Long-Tail-Keywords bleiben ohne Ranking-Daten, im Pool-Markdown als "Recherche-Stand: Long-Tail" markiert.

### Schritt 7: Branchen-Seed-Cross-Check

Wenn `wettbewerber/identifikation-schema.md` vorhanden und bestätigt:

1. Lies `branchen_seed_keywords` aus dem Frontmatter
2. Pro Seed-Keyword: prüfe, ob es bereits im Pool ist
3. Wenn nicht: Validierungs-Lookup — **primär via Ahrefs** `keywords-explorer-overview` (liefert in einem Call Volumen + Difficulty + Intent + Parent-Topic). Optional Sistrix `keyword.overview` als DACH-Cross-Check, wenn Sistrix verfügbar.
   - Wenn Ahrefs-`volume` ≥ 100/Monat: in den Pool aufnehmen mit `quellen: ["branchen_seed"]`, `seed_keyword: null`
4. Cross-Check: Seed-Keywords, die der Kunde **nicht** abdeckt (Position > 30 oder gar nicht rankend) → markieren als `branchen_basis_luecke: true`

Wenn das Schema-File nicht vorhanden: dieser Schritt übersprungen, Hinweis im Schluss-Format.

### Schritt 8: Ahrefs-Vollanreicherung (Difficulty, Volumen, CPC, Intent-Flags, Parent-Topic)

**Pflicht-Schritt** (Ahrefs ist seit Schritt 1 verfügbar). Ersetzt die bisherige reine Difficulty-Anreicherung.

Strategie zur Credit-Schonung — nicht für alle Keywords anreichern, sondern für die **strategisch relevanten**, aber durch Batching deutlich mehr als zuvor:

| Priorität | Auswahl | Erwartete Anzahl |
|---|---|---|
| 1 | Alle Gap-Keywords (komplett, nicht nur Top-50) | bis zu 300 |
| 2 | Alle Kunden-Top-50-Keywords (aus Basis-Pool, nach Volumen × Position-Gewicht) | bis zu 50 |
| 3 | Alle Branchen-Seeds | bis zu 30 |
| 4 | Alle Long-Tail-Keywords mit Suchvolumen ≥ 200/Monat (Sistrix oder Ahrefs) | variabel, max 200 |
| 5 | Long-Tail-Keywords < 200 Volumen, soweit Budget reicht | Rest bis Cap |

Gesamt-Cap: **500–1000 Anreicherungen** pro Lauf, abhängig von Pool-Größe (zuvor 150). Default `anreicherung_cap: 800`, konfigurierbar via Override. Begründung: bei 1000 Keywords/Batch und 400.000 Units/Monat ist die alte Grenze überholt — typischer MTA-Lauf reizt unter 1% des Budgets aus.

**Pro Batch (bis 1000 Keywords):**

- `mcp__1d9710a6-f270-4555-88f8-e4367948d936__keywords-explorer-overview`
- `select`-Felder: `keyword, volume, keyword_difficulty, cpc, traffic_potential, is_branded, is_transactional, is_commercial, is_informational, parent_keyword, intents, country`
- Country aus `meta.json.region` (Default `de`)
- Bei Spalten-Fehler: Spalten aus der Fehlermeldung übernehmen und Request wiederholen
- Cache: `~/.cache/reachx-mta/<slug>/audits/raw/ahrefs-overview-batch-<n>.json` (lokal, später komprimiert nach Drive `assets/raw/`)

**In den Pool ergänzen pro Keyword:**

- `difficulty: <int>` (aus `keyword_difficulty`)
- `ahrefs_volumen: <int>` (aus `volume`)
- `ahrefs_cpc: <float>` (aus `cpc`)
- `ahrefs_parent_topic: <string>` (aus `parent_keyword`)
- `ahrefs_intent_flags: { is_branded, is_transactional, is_commercial, is_informational }` (für Schritt 9)
- Wenn Sistrix-Volumen und Ahrefs-Volumen stark abweichen (>50% Unterschied): `volumen_diskrepanz: true`. Beide Werte bleiben in der CSV erhalten.

### Schritt 9: Intent-Hypothese pro Keyword — Ahrefs-Flags primär, Heuristik als Fallback

Pro Keyword im Pool eine Intent-Hypothese ableiten. **Ahrefs-Intent-Flags sind die Primary-Quelle**, die heuristischen Regeln aus dem alten Skill werden zum Fallback für Keywords ohne Ahrefs-Match (z. B. weil das Anreicherungs-Cap überschritten ist oder Ahrefs das Keyword nicht kennt).

**9a) Primary — Ahrefs-Flags:**

Wenn `ahrefs_intent_flags` für das Keyword vorhanden ist, wird daraus die `intent_hypothese` abgeleitet. Mapping (in dieser Prioritäts-Reihenfolge bei mehrfach-true):

1. `is_branded == true` → `branded`
2. `is_transactional == true` → `transactional`
3. `is_commercial == true` → `commercial`
4. `is_informational == true` → `informational`
5. Keine Flag `true` → `unklar` (Fallback auf Heuristik nicht, weil Ahrefs hier explizit "nichts erkannt" sagt — Stratege entscheidet)

Ergänze: `intent_quelle: ahrefs_flags`.

**9b) Fallback — Heuristik:**

Nur wenn kein Ahrefs-Match vorliegt (z. B. Cap überschritten, 404 beim Lookup, Long-Tail mit Volumen unter Filter). Regel-Schicht in Reihenfolge:

1. **Branded** — enthält Markennamen des Kunden oder eines bekannten WBs (aus `data/kunde.md` `marke.synonyme` und `wettbewerber/liste.md` Namen) → `intent_hypothese: branded`
2. **Transactional** — enthält Kauf-Signale ("kaufen", "preis", "bestellen", "shop", "angebot", "rabatt", "günstig", "bestpreis", "online kaufen") → `transactional`
3. **Commercial** — Vergleich/Bewertung-Signale ("test", "vergleich", "vs", "erfahrungen", "bewertung", "beste", "ranking", "alternativen zu") → `commercial`
4. **Informational** — Wissens-Signale ("was ist", "wie funktioniert", "anleitung", "tipps", "guide", "tutorial", W-Fragen) → `informational`
5. **Navigational** — sehr kurz und/oder enthält Domain-Fragmente ohne Kauf-Signal → `navigational`
6. **Sonstige / unklar** → `intent_hypothese: unklar`

Ergänze: `intent_quelle: heuristik`.

**9c) Tracking-Hinweis:**

Wenn Ahrefs-Intent **abweicht** von dem, was die Heuristik gesagt hätte (für Keywords mit beiden Quellen), wird das in der Auffälligkeit `intent_hypothese_korrigiert` aggregiert — informativ für den Strategen, ob die Heuristik systematisch danebenliegt.

`intent_quelle`-Werte sind dokumentiert in `reference/keyword-pool-schema.md`: `ahrefs_flags` (primary), `heuristik` (fallback), `manuelle_kuration` (für spätere Skills wie `03-03-seo-keyword-kategorisierung` reserviert).

### Schritt 10: Auffälligkeiten

Aus der angereicherten Pool-Datenstruktur die strategisch relevanten Beobachtungen extrahieren:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `top_gap_hochvolumig` | Mindestens 1 Gap-Keyword mit Suchvolumen ≥ 2000/Monat | "Hochvolumiger Gap: 'kabel verlängerung' (3.600/Monat, WB X auf Position 2, Kunde nicht im Top-100)" |
| `gap_cluster` | Mehrere Gap-Keywords mit ähnlichem Wortstamm (Heuristik: gleicher Token >=2x) oder gleichem `ahrefs_parent_topic` | "Gap-Cluster um 'verlegung*': 8 Keywords, gesamt 11.400 Suchvolumen — Content-Lücke" |
| `wb_dominanz_in_thema` | Ein WB rankt für >40% der Gap-Keywords im Top-10 | "Wettbewerber X dominiert das Thema 'aufmaß' — rankt auf 14 von 23 Gap-Keywords im Top-10" |
| `branded_traffic_kunde_stark` | Kunden-Branded-Keywords haben hohes Suchvolumen ≥ 500 und Kunde rankt Top 3 | "Markenbekanntheit erkennbar: 1.200 monatliche Brand-Searches, Kunde stabil auf Position 1-2" |
| `branded_traffic_wb_uebernommen` | Kunde rankt im Top-10 für WB-Markennamen | "Kunde rankt für 'WB-Name X' auf Position 4 — möglicher Conquest-Effekt, prüfen ob beabsichtigt" |
| `branchen_basis_luecke` | Mehr als 50% der Branchen-Seed-Keywords sind nicht vom Kunden abgedeckt | "Branchen-Basis-Lücke: Kunde rankt für 5 von 12 Branchen-Seeds nicht im Top-30" |
| `volumen_diskrepanz_sistrix_ahrefs` | Mehr als 10 Keywords mit >50% Volumen-Unterschied (nur wenn Sistrix verfügbar) | "Sistrix und Ahrefs liefern für 14 Keywords stark unterschiedliche Volumina — manuelle Validierung empfohlen" |
| `volumen_diskrepanz_systematisch` | **NEU** — >30% **aller** Cross-validierten Keywords mit Volumen-Diskrepanz | "67% der Cross-validierten Keywords zeigen >50% Volumen-Differenz zwischen Sistrix und Ahrefs — methodische Inkonsistenz, Stratege sollte entscheiden, welche Quelle für die MTA-Story führt." |
| `intent_hypothese_korrigiert` | **NEU** — ≥ 20 Keywords, deren Ahrefs-Intent von der Heuristik abweicht | "Bei 34 Keywords liefert Ahrefs einen anderen Intent als die Heuristik (v. a. transactional → commercial). Heuristik allein ist hier nicht zuverlässig." |
| `parent_topic_dominanz` | **NEU** — ein einzelnes `ahrefs_parent_topic` deckt >30% des Pools ab | "Parent-Topic 'aufmaß' dominiert den Pool mit 142 von 420 Keywords — strategischer Cluster-Anker für `03-03-seo-keyword-kategorisierung`." |
| `difficulty_sweet_spot` | Mindestens 5 Gap-Keywords mit Difficulty ≤ 30 UND Suchvolumen ≥ 300 | "Sweet-Spot-Gaps: 8 Keywords mit niedriger Difficulty und relevantem Volumen — schnelle SEO-Wins möglich" |

Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz, Handlungs-Empfehlung, betroffene Keywords.

### Schritt 11: CSV-Output `audits/seo-keyword-pool.csv`

Schreibe den vollständigen Pool als CSV. Siehe `reference/keyword-pool-schema.md` für das exakte Spalten-Schema.

Kernspalten (Erweiterung über die Basis-CSV hinaus):

```
keyword, keyword_normalisiert, sistrix_volumen, ahrefs_volumen, volumen_diskrepanz, difficulty, ahrefs_cpc, ahrefs_parent_topic,
ahrefs_is_branded, ahrefs_is_transactional, ahrefs_is_commercial, ahrefs_is_informational,
quellen, seed_keyword, intent_hypothese, intent_quelle, gap_zu_kunde, gap_typ, gap_score, branchen_basis_luecke,
ranking_kunde_position, ranking_kunde_url, ranking_top_wb_slug, ranking_top_wb_position, ranking_top_wb_url,
datenstand_iso
```

Pro Keyword eine Zeile (nicht mehr eine Zeile pro Akteur — Pool ist Keyword-zentriert, nicht Akteurs-zentriert). Akteurs-Detail-Rankings stehen in `audits/seo-keywords.csv` (Basis-CSV vom vorherigen Skill).

### Schritt 12: Aggregat-Markdown `audits/seo-keyword-pool.md`

YAML-Frontmatter mit:

- Skill-Metadaten, Provenienz (welche Quellen wurden genutzt, welche Schritte ausgeführt, `ahrefs_modus`, `sistrix_modus`)
- Aggregat-Statistiken (Anzahl Keywords gesamt, nach Quelle, nach Intent-Hypothese aufgesplittet nach `intent_quelle`, Difficulty-Verteilung als Histogramm, Top-3-Parent-Topics)
- Top-50-Gap-Keywords als strukturierte Liste (mit Score, Volumen, Top-WB)
- Auffälligkeiten

Body strukturiert nach:

- Übersicht (Größe des Pools, größte Datenquelle, Top-Erkenntnis)
- Wettbewerbs-Gaps (mit Auswahl-Tabelle Top-30 nach Score)
- Long-Tail-Erweiterung (Anzahl, größte Cluster nach Seed-Keyword **und** nach `ahrefs_parent_topic`)
- Branchen-Seed-Status (Was deckt der Kunde, was nicht?)
- Difficulty-Verteilung (Histogramm in ASCII / Tabellenform)
- Intent-Hypothesen-Verteilung — getrennt nach `intent_quelle: ahrefs_flags` und `heuristik`
- Auffälligkeiten als eigene Sektion (sortiert nach Relevanz)
- Vorbereitung für `03-03-seo-keyword-kategorisierung`: Hinweis, welche Cluster sich schon abzeichnen — **vor allem aus den Ahrefs-Parent-Topics**, die jetzt vollflächig vorliegen

### Schritt 13: HTML-Report `reports/07-seo-keyword-pool.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Aus `reports/_shell.html`:

- `{{TITLE}}` → SEO-Keyword-Pool · Kunde
- `{{EYEBROW}}` → MTA-Audit · SEO
- `{{DISPLAY_NAME}}` → SEO-Keyword-Pool und Wettbewerbs-Gaps: Kunde
- `{{META_LINE}}` → N Keywords im Pool · M Gaps · Ahrefs (primary) + Sistrix (DACH-Ergänzung) · Datenstand DATUM
- `{{MAIN_CONTENT}}` →
  - Stat-Strip: Pool-Größe, Anzahl Gaps, Anzahl Sweet-Spot-Gaps (niedrige Difficulty + relevantes Volumen), Anzahl Branchen-Basis-Lücken, Anzahl Parent-Topics
  - Sticky-TOC
  - **Top-Gaps-Tabelle** (prominent oben, max 30 Einträge): Keyword, Suchvolumen (Ahrefs + Sistrix wenn beide vorhanden), Difficulty, Top-WB + Position, Gap-Score-Bar
  - **Gap-Cluster-Hinweise** als `details`-Blöcke (sowohl Token-basiert als auch Parent-Topic-basiert)
  - **Long-Tail-Übersicht** als kompakte Tabelle: Seed-Keyword → Anzahl Variationen, kumuliertes Volumen, Quellen-Mix (Ahrefs vs. Sistrix)
  - **Difficulty-Histogramm** (SVG-Balken oder Text-Visualisierung) — Verteilung der Difficulty in 10er-Buckets
  - **Intent-Verteilung** als kleine Donut-Beschreibung in Text-Form, mit Hinweis "X Keywords über Ahrefs-Flags klassifiziert, Y über Heuristik"
  - **Parent-Topic-Top-10** als Tabelle (neu, sichtbar für Strategen vor `03-03-seo-keyword-kategorisierung`)
  - **Auffälligkeiten** als `.suggestion`-Block, sortiert nach Relevanz, mit Handlungs-Empfehlungen
  - **Vorbereitungs-Hinweis**: "Die Intent-Klassifikation aus Ahrefs-Flags und die Parent-Topic-Cluster werden in `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf) zu MTA-Cluster-Achsen kuratiert."
- `{{FOOTER_TEXT}}` → MTA · Kunde · SEO-Keyword-Pool und Gaps

### Schritt 13b: Outputs nach Drive hochladen

Finale Outputs via `drive.py upsert-text` nach Drive schreiben:

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-keyword-pool.csv" \
  ~/.cache/reachx-mta/<slug>/seo-keyword-pool.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "seo-keyword-pool.md" \
  ~/.cache/reachx-mta/<slug>/seo-keyword-pool.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "07-seo-keyword-pool.html" \
  ~/.cache/reachx-mta/<slug>/07-seo-keyword-pool.html "text/html"
```

CSV bleibt CSV (kein Auto-Convert zu Google Sheet — `drive.py` setzt das intern).

### Schritt 14: Dashboard-Update und status.md

Standard-Pattern: `reports/index.html` und `status.md` aus Drive lesen, anpassen, zurückschreiben (siehe `contracts.md` Abschnitt 3 und 7):

```bash
INDEX_ID=$(python3 "$DRIVE_PY" list-children "$REPORTS_ID" | jq -r '.[] | select(.name == "index.html") | .id')
python3 "$DRIVE_PY" read "$INDEX_ID" > /tmp/index.html
# … HTML anpassen …
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "index.html" /tmp/index.html "text/html"

STATUS_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "status.md") | .id')
python3 "$DRIVE_PY" read "$STATUS_ID" > /tmp/status.md
# … Frontmatter+Body anpassen …
python3 "$DRIVE_PY" upsert-text "$FOLDER_ID" "status.md" /tmp/status.md "text/markdown"
```

Updates:

- `03-02-seo-keyword-recherche` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen
- `naechster_empfohlen`: `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf, baut auf diesem Pool auf)
- Reports-Liste um `07-seo-keyword-pool.html`
- Stat-Strip aktualisieren (Pool-Größe + Anzahl Gaps)

### Schritt 15: Standard-Schlussformat im Chat

```
✓ 03-02-seo-keyword-recherche abgeschlossen.

Outputs:
- audits/seo-keyword-pool.csv — erweiterter Keyword-Pool (N Zeilen)
- audits/seo-keyword-pool.md — Aggregat mit Gaps, Difficulty-Verteilung, Intent-Verteilung, Parent-Topics
- reports/07-seo-keyword-pool.html — Strategen-Report
Status aktualisiert in: status.md

Pool-Statistik:
- Keywords gesamt:           N
- Davon Basis (CSV):         M
- Davon Long-Tail Ahrefs:    LA
- Davon Long-Tail Sistrix:   LS  (0 wenn sistrix_modus: aus)
- Davon Branchen-Seeds:      B
- Wettbewerbs-Gaps:          G (davon Sweet-Spot: S)
- Ahrefs-Anreicherungen:     A (Difficulty + Intent + Volumen + Parent-Topic)
- Intent aus Ahrefs-Flags:   IA
- Intent aus Heuristik:      IH
- Parent-Topics:             P (Top-3: ..., ..., ...)

[Wenn Top-Gap-Auffälligkeiten:]
⚠ Top-Gap-Beobachtungen:
- (1-3 Punkte, sortiert nach Relevanz)

[Wenn Sistrix nicht verfügbar:]
ℹ Sistrix-Cross-Validierung übersprungen
- Sistrix-Zugang nicht verfügbar — sistrix_volumen-Spalte leer, keine Volumen-Diskrepanz-Analyse. Skill lief im Reduced-Modus ohne Sistrix. Pool basiert vollständig auf Ahrefs.

[Wenn Branchen-Seeds nicht verfügbar:]
ℹ Branchen-Seeds übersprungen
- wettbewerber/identifikation-schema.md fehlt oder nicht bestätigt — Pool nutzt nur CSV + Ahrefs-Expansion.

Nächste Schritte:
1. 03-03-seo-keyword-kategorisierung — Cluster + Intent-Typen schemagesteuert (Schema-vor-Lauf, Parent-Topics als Vorlage)
2. (parallel möglich) 03-05-sea-google-ads-check — Paid-Search-Aktivität in derselben Branche
3. (parallel möglich) 03-14-web-tech-und-tracking — Performance + Tracking

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/ahrefs-api-nutzung.md` — Ahrefs als Primary-Quelle, MCP-Tools, Batching-Strategie, Credit-Budget bei 400.000 Units/Monat, Caching. Sistrix-Sektion am Ende als optionale DACH-Ergänzung.
- `reference/keyword-pool-schema.md` — CSV-Spalten (inklusive der neuen Ahrefs-Intent-Flag- und `intent_quelle`-Spalten) und Markdown-Frontmatter-Schema
- `reference/wettbewerbs-gap-logik.md` — exakte Gap-Berechnungsregeln (Schwellwerte, Branded-Filter mit Ahrefs `is_branded`, Aggregator-Filter, Scoring auf Basis Ahrefs-Volumen)

## Edge Cases

- **`audits/seo-keywords.csv` ist leer oder hat nur Kunden-Zeilen** → Skill läuft im "Kunden-only-Pool"-Modus. Long-Tail-Expansion via Ahrefs und Branchen-Seeds funktionieren, Gap-Berechnung wird übersprungen (keine WBs vorhanden), Hinweis im Schluss-Format.

- **Ahrefs-Rate-Limit oder Auth-Fehler mitten im Lauf** → bisher gezogene Daten bleiben erhalten, Schritt 8 bricht ab. Skill schreibt Pool mit teilweise gefüllten Ahrefs-Spalten, im Body Hinweis "X von Y Keywords mit Ahrefs angereichert, Rest leer — Override `nur Ahrefs nachziehen` beim nächsten Aufruf". Da Ahrefs Pflicht ist, wird der Skill **nicht** kommentarlos weiterlaufen, sondern die Lücke explizit ausweisen.

- **Branded-Keyword des Kunden ist gleichzeitig generisches Wort** (z. B. "Aufmaster" als Firmenname und Begriff) → der Skill prüft jetzt zusätzlich das Ahrefs `is_branded`-Flag. Wenn Ahrefs `is_branded: false` zurückgibt aber die Heuristik branded sagt, wird im Pool ein Hinweis-Flag `branded_unscharf: true` gesetzt und im Pool-Markdown im Body genannt.

- **Aggregator-Filter ist zu aggressiv** → unverändert: Stratege kann beim Aufruf "Aggregator-Filter aus" überschreiben.

- **Ahrefs liefert für ein Keyword keine Daten** (Keyword unbekannt, 0 Treffer) → `lookup_fehlgeschlagen: false` bleibt, aber `ahrefs_volumen`, `difficulty` etc. bleiben leer. Intent-Hypothese fällt auf Heuristik zurück.

- **Volumen-Diskrepanz Sistrix vs. Ahrefs für >30% der Keywords** → eigene Auffälligkeit `volumen_diskrepanz_systematisch` (siehe Schritt 10) mit Empfehlung, dass die Branche durch unterschiedliche Daten-Quellen unterschiedlich gesehen wird (Sistrix oft DACH-stärker, Ahrefs internationaler). Beide Werte in CSV erhalten.

- **Pool wird sehr groß (>1500 Keywords)** → Pool-Markdown rendert nur Top-200 als Tabellen, Rest steht in CSV. Hinweis im Body, dass die CSV die Quelle der Wahrheit ist. Hard-Cap bei 3000 Keywords (siehe `reference/keyword-pool-schema.md`).

- **Pool-Markdown soll für Strategen lesbar bleiben** → keine Tabelle länger als 30 Zeilen rendern, alles darüber als CSV-Verweis "siehe audits/seo-keyword-pool.csv".

- **Re-Run mit nur partieller Quelle** → Override-Argumente unterstützen:
  - `nur Ahrefs nachziehen` → Schritt 8 läuft (Difficulty + Volumen + Intent-Flags + Parent-Topic gebatcht), Schritte 3-7 aus existierender CSV gelesen
  - `nur Long-Tail nachziehen` → Schritt 5 läuft (Ahrefs-matching/related/suggestions, optional Sistrix), alle anderen aus existierender CSV
  - `nur Gap-Berechnung` → Schritt 4 läuft mit aktualisierter Basis-CSV
  - In jedem Fall: bisheriger Pool-Stand wird gelesen, ergänzt, geschrieben — keine Vollerneuerung.

- **Spalten-Schema-Drift bei `keywords-explorer-overview`** → wenn Ahrefs den Spalten-Namen ändert (z. B. `keyword_difficulty` → `kd`), übernimmt der Skill die Namen aus der Fehlermeldung und wiederholt den Request einmal. Bei zweitem Fehlschlag: Hinweis im Schluss-Format, Schritt 8 für den Batch als fehlgeschlagen markieren.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder; Pfade in der Doku sind Drive-relativ (z. B. `audits/seo-keyword-pool.csv`)
- Markdown + YAML-Frontmatter für Pool-Aggregat, CSV für Roh-Daten (via `drive.py upsert-text`)
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (`drive.py upsert-text`)
- HTML-Report aus `reports/_shell.html` (aus Drive lesen, Platzhalter ersetzen, zurückschreiben)
- Ahrefs-Roh-Caches lokal unter `~/.cache/reachx-mta/<slug>/audits/raw/`, am Ende komprimiert nach Drive `assets/raw/`
- **CSV ist die Single-Source-of-Truth** für die Folge-Skills — Markdown ist für Strategen
- **Intent-Hypothesen kommen primär aus Ahrefs-Flags**, fallback Heuristik — finale Kategorisierung erfolgt weiterhin in `03-03-seo-keyword-kategorisierung` (Schema-vor-Lauf)
- **Volumen-Werte unverändert lassen** — beide Werte (Sistrix + Ahrefs) bleiben original in eigenen Spalten, Normalisierung ist Synthese-Aufgabe
