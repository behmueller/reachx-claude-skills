---
name: 04-07-segment-potenzial-matrix
description: Ergänzende Zweitsynthese zur kanal-zentrierten MTA-Synthese. Mappt das vorhandene Markt-Potenzial auf 2-4 Kunden-Segmente (Leistungsart, Zielgruppe oder Region) und macht pro Segment einen ehrlichen Erreichbarkeits- und Engpass-Check. Schema-vor-Lauf - Phase A schlägt die Segment-Definition und das Bewertungs-Raster vor, Stratege bestätigt, Phase B rechnet pro Segment fünf Auswertungs-Blöcke (Marktpotenzial bottom-up, Ist-Position, Erreichbarkeits-Prüfung, Hebel plus Kanal-Mix, Aufwands-Hochrechnung) und verdichtet zu einer Gesamt-Matrix über Potenzial mal Aufwand mal Erreichbarkeit mal Time-to-Impact. Häufiger Befund - nicht das Marketing, sondern die Liefer-/Personal-Kapazität des Kunden ist der Engpass. Bandbreiten konservativ/realistisch/ambitioniert, niemals Punktschätzungen. Outputs synthese/segment-potenzial-matrix.md plus synthese/segment-potenzial-matrix.csv plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext das Potenzial nach Kunden-Segmenten aufschlüsseln will - auch bei Phrasen wie "Segment-Potenzial-Matrix", "Segment-Analyse", "nach Segmenten aufschlüsseln", "welches Kundensegment lohnt sich", "Segment-Priorisierung", "Leistungssegmente bewerten", "Zielgruppen-Segmente vergleichen", "wo ist der Engpass", "Kapazitäts-Engpass-Check". Setzt voraus, dass 04-04-forecast-modell gelaufen ist - bricht sonst ab.
---

# Segment-Potenzial-Matrix

**Ergänzende Zweitsynthese** in Stufe 4. Läuft **nach** `04-04-forecast-modell` und nutzt dessen Bandbreiten als Input.

Dieser Skill **ersetzt die kanal-zentrierte Synthese nicht** — er ergänzt sie. Die Standard-MTA-Synthese (`04-02-kanal-chancen-analyse`, `04-03-ziele-aus-potenzialen`, `04-04-forecast-modell`) denkt in Marketing-**Kanälen** (SEO / SEA / Meta / …). Viele Kunden haben aber mehrere unterschiedliche Leistungs- oder Zielgruppen-**Segmente**, jedes mit eigener Markt-, Erreichbarkeits- und Aufwands-Logik. Ein Forecast, der nur nach Kanal aufschlüsselt, verdeckt, dass das Wachstum in Segment A kapazitäts-gedeckelt und in Segment B kanal-gedeckelt ist.

Dieser Skill liefert die **Segment-Sicht**: Er mappt das in der Kanal-Synthese ermittelte Potenzial auf die Kunden-Segmente und macht einen ehrlichen Erreichbarkeits- und Engpass-Check pro Segment. Output ist eine optionale, ergänzende Sicht für die MTA-Slides — sie verdrängt `kanal-chancen.md` und `forecast.md` nicht, sie kontextualisiert sie.

**Position im Workflow** (verbindlich so im Output und in den Slides einordnen):

```text
04-04-forecast-modell   ──┬──>  04-05-90-tage-plan  ──>  04-06-retainer-kalkulator
                          └──>  04-07-segment-potenzial-matrix   (Zweitsynthese, ergänzend)
```

`04-07` ist kein Glied der Pflicht-Kette `04-01 → 04-06`. Es ist ein optionaler Seitenstrang, der nach `04-04` läuft. `04-05` und `04-06` setzen `04-07` **nicht** voraus — die Pflicht-Kette läuft auch ohne diesen Skill durch.

## Drei Output-Ebenen

1. **Aggregat-Markdown** `synthese/segment-potenzial-matrix.md` — pro Segment fünf Auswertungs-Blöcke, die Gesamt-Matrix über vier Achsen, Engpass-Analyse, Priorisierung (Mengen-Logik), strategische Story. Frontmatter mit `basis_inputs` + `generiert_am`, `status: vorgeschlagen` bis zum Stratege-Review.
2. **Segment-CSV** `synthese/segment-potenzial-matrix.csv` — eine Zeile pro Segment × Auswertungs-Block für schnelle Sortierung/Filter.
3. **HTML-Report** `reports/<freie-nummer>-segment-potenzial.html` — Matrix-Heatmap (Segment × Achse), Engpass-Karten, Priorisierungs-Liste.

**Report-Nummer:** Es gibt keine feste Nummer — `04-07` ist eine späte Zweitsynthese, ihr Report hängt hinten an. Vorschlag: `21-segment-potenzial.html` (die Audit-/Synthese-Reports sind bis ca. `20` belegt). **Beim Lauf gegen `reports/index.html` prüfen**, ob die Nummer frei ist, und die nächste freie Zahl wählen, falls nicht.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschlag bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Synthese-Outputs zur Segment-Sicht.

Schema-vor-Lauf-Pattern: **Phase A** schreibt das Segment-Schema nach Drive und bricht ab. Der Stratege bestätigt im Hauptthread. **Phase B** läuft im Subagent erneut und führt die eigentliche Rechnung aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="04-07-segment-potenzial-matrix"
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

- "Segment-Potenzial-Matrix"
- "Segment-Analyse"
- "nach Segmenten aufschlüsseln"
- "welches Kundensegment lohnt sich"
- "Segment-Priorisierung"
- "Leistungssegmente bewerten"
- "Zielgruppen-Segmente vergleichen"
- "Region-Segmente bewerten"
- "wo ist der Engpass"
- "Kapazitäts-Engpass-Check"
- "ist das Marketing der Engpass oder die Lieferkapazität"
- "Potenzial pro Segment"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`, `status.md`
- **`04-04-forecast-modell` gelaufen** → `synthese/forecast.md` plus `synthese/forecast.csv` vorhanden (Pflicht-Input — liefert die Bandbreiten, die pro Segment aufgeteilt werden). **Hinweis zum Dateinamen:** `04-04-forecast-modell` schreibt sein Aggregat als `synthese/forecast.md` (nicht `forecast-modell.md`) — dieser Skill liest `synthese/forecast.md`.
- **`synthese/kanal-chancen.md`** vorhanden (Pflicht-Input — die Kanal-Sicht, die dieser Skill um die Segment-Sicht ergänzt; liefert Top-Kanäle pro Segment-Hebel)
- **`data/briefing.md`** vorhanden (Pflicht-Input — Quelle für die Segment-Definition: Leistungsarten, Zielgruppen, Regionen, genannte Kapazitäts-Aussagen)
- Empfohlen: `data/kunde.md` und `synthese/positionierung.md` (für die Segment-Definition in Phase A)
- Empfohlen: Kunden-Datendateien — Umsatz-/Kundenzahlen-/Auftragsexporte, falls vom Strategen bereitgestellt. Gesucht wird in `data/` und in `input/` (beliebige `.csv`/`.xlsx`/`.md` mit Umsatz-, Auftrags- oder Kundenzahlen). Liegen solche Dateien vor, werden Segmentgrößen und Einzugsgebiet daraus belegt (`erhoben`/`briefing`); fehlen sie, werden sie als `schaetzung_skill` klar markiert.

Fehlt ein **Pflicht-Input** → harter Abbruch nach `contracts.md` Abschnitt 12 mit klarer Meldung, welcher Skill vorher laufen muss. **Kein Silent-Fallback** — der Skill rechnet niemals ohne Forecast-Bandbreiten-Basis.

### Pflicht-MCPs

Keine. Dieser Skill ist ein reiner Synthese-Skill — er liest nur vorhandene Drive-Outputs und rechnet. Keine externen MCPs nötig, kein Health-Check.

## Ablauf

Schema-vor-Lauf-Pattern (siehe `contracts.md` Abschnitt 8). Bei jedem Aufruf prüft der Skill, ob `synthese/segment-potenzial-matrix-schema.md` existiert und welchen Status sie hat.

### Phase-Entscheidungs-Logik (Schritt 0 bei jedem Aufruf)

Zuerst die Drive-Bootstrap (siehe `contracts.md` Abschnitt 1):

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
INPUT_ID=$(jq -r '.drive.subfolders.input' /tmp/meta.json)
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Phase-Entscheidung:

```text
1. Existiert synthese/segment-potenzial-matrix-schema.md auf Drive?
   - Nein                       -> Phase A (Schema generieren)
   - Ja, status: vorgeschlagen  -> freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt     -> Phase B (Matrix-Berechnung)
   - Ja, anderer Status         -> Abbruch mit Hinweis auf erlaubte Werte

2. Existiert synthese/segment-potenzial-matrix.md auf Drive bereits?
   - Nein -> weiter mit Phase B
   - Ja   -> fragen (überschreiben / Backup-und-neu / abbrechen)
```

---

## Phase A — Segment-Schema vorschlagen

### Schritt A.1: Projekt-Auffindung und Pflicht-Input-Gate

Drive-Bootstrap wie oben. Lies `status.md` aus Drive.

**Hartes Voraussetzungs-Gate** (jeweils `drive.py find_by_name`, nach `contracts.md` Abschnitt 12):

- `synthese/forecast.md` muss auf Drive existieren — sonst Abbruch mit Hinweis auf `04-04-forecast-modell`
- `synthese/kanal-chancen.md` muss auf Drive existieren — sonst Abbruch mit Hinweis auf `04-02-kanal-chancen-analyse`
- `data/briefing.md` muss auf Drive existieren — sonst Abbruch mit Hinweis auf `01-02-kickoff-transcript-parser`

Abbruch-Format bei fehlendem Pflicht-Input:

```text
✗ 04-07-segment-potenzial-matrix kann nicht laufen: <pflicht-input> fehlt.
Bitte zuerst <vorgänger-skill> ausführen.
```

### Schritt A.2: Inputs einlesen

Lade aus Drive in den lokalen Cache (`~/.cache/reachx-mta/<slug>/`):

- `synthese/forecast.md` — Frontmatter: `aggregat_12_monate.*` (worst/real/best für Umsatz, Leads, Orders), `kanaele[]`, `branchen_typ`, `aggregat_pro_quartal`, `forecast_outputs_fuer_folge_skills`
- `synthese/kanal-chancen.md` — Frontmatter: `top_3_empfehlungen[]`, `kanal_ranking[]`, `branchen_typ`, `strategische_story`
- `data/briefing.md` — Body und Frontmatter: Leistungsarten/Portfolio, Zielgruppen, Regionen, **genannte Kapazitäts-Aussagen** (Personal, Liefer-/Produktions-Kapazität, Auslastung, Wachstums-Grenzen)
- `data/kunde.md` (falls vorhanden) — Portfolio-Struktur, USPs, Zielgruppen-Hypothese
- `synthese/positionierung.md` (falls vorhanden) — Differenzierungs-Achsen

**Kunden-Datendateien suchen:** Liste `data/` und `input/` (`drive.py list-children`). Suche nach Dateien mit Umsatz-, Auftrags- oder Kundenzahlen (Dateinamen-Heuristik: `umsatz`, `kunden`, `auftraege`, `orders`, `revenue`, `export`, `zahlen` o. ä.; Endungen `.csv`, `.xlsx`, `.md`). Gefundene Dateien laden und im Schema unter `kunden_datenquellen` vermerken. Liegt nichts vor: Segmentgrößen und Einzugsgebiet in Phase B als `schaetzung_skill` markieren.

### Schritt A.3: Segment-Definition ableiten (Kern von Phase A)

Schlage **2 bis 4 Segmente** vor. Ein Segment ist eine in sich kohärente Teil-Einheit des Kunden-Geschäfts mit eigener Markt-, Erreichbarkeits- und Aufwands-Logik. Die Segmentierungs-Achse wird aus den Inputs abgeleitet — genau **eine** Achse pro MTA wählen (Segmente dürfen nicht über mehrere Achsen gemischt werden, sonst überlappen sie):

| Segmentierungs-Achse | Wann wählen | Beispiel-Segmente |
|---|---|---|
| **Leistungsart** | Kunde bietet klar abgrenzbare Leistungs-/Produktlinien mit eigenem Markt | "Privatkunden-Sanierung", "Gewerbe-Neubau", "Wartungsverträge" |
| **Zielgruppe** | Eine Leistung, aber mehrere Käufer-Typen mit eigener Ansprache | "Endverbraucher B2C", "Architekten als Multiplikatoren", "Wohnungsbau-Gesellschaften" |
| **Region** | Gleiche Leistung, mehrere Einzugsgebiete mit eigener Wettbewerbs-/Nachfrage-Lage | "Kern-Region (50 km)", "erweiterte Region", "überregional / online" |

**Auswahl-Heuristik:** Nimm die Achse, entlang derer das Briefing/Kunden-Profil die deutlichsten Unterschiede in Marge, Nachfrage oder Erreichbarkeit zeigt. Im Zweifel: Leistungsart, weil sie am direktesten auf Kapazität und Marge mappt. Die gewählte Achse und die Begründung kommen ins Schema.

Pro Segment im Schema festhalten: `segment_slug`, `anzeigename`, `kurzbeschreibung`, `abgrenzung` (was gehört rein/raus), `briefing_belege` (Zeilen-Verweise), `geschaetzter_umsatzanteil_heute` (falls aus Kunden-Datendateien belegbar `erhoben`, sonst `schaetzung_skill`).

### Schritt A.4: Bewertungs-Raster vorschlagen

Pro Segment werden in Phase B **fünf Auswertungs-Blöcke** gerechnet und vier **Matrix-Achsen** bewertet. In Phase A werden die Achsen-Skalen, die Bandbreiten-Logik und die Engpass-Faktoren als Raster vorgeschlagen — der Stratege bestätigt oder korrigiert sie. Details siehe `reference/segment-matrix-methodik.md`.

Das Raster im Schema umfasst:

- **Matrix-Achsen** (0–100): `potenzial`, `aufwand` (invertiert: hoch = niedriger Aufwand), `erreichbarkeit`, `time_to_impact` (invertiert: hoch = schnelle Wirkung) — plus die Gewichtung für die `prioritaet_score`-Aggregation
- **Bandbreiten-Set:** für jeden quantitativen Wert die drei Szenarien `konservativ`, `realistisch`, `ambitioniert` — niemals Punktschätzungen
- **Engpass-Kandidaten:** Liste der zu prüfenden limitierenden Faktoren pro Segment (Marketing-Potenzial vs. Liefer-/Produktions-Kapazität vs. Personal vs. Vertriebs-Kapazität vs. Onboarding/Service)
- **Branchen-Defaults:** Conversion-/Marge-/Time-to-Impact-Referenzwerte aus `reference/segment-raster-defaults.md`

### Schritt A.5: Schema nach Drive schreiben

Erzeuge `synthese/segment-potenzial-matrix-schema.md` lokal nach dem Format in `reference/segment-schema-template.md`, `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "segment-potenzial-matrix-schema.md" \
  /tmp/segment-schema.md "text/markdown"
```

### Schritt A.6: Schluss-Format Phase A

```text
✓ 04-07-segment-potenzial-matrix Phase A abgeschlossen.

Outputs (auf Drive):
- synthese/segment-potenzial-matrix-schema.md — Segment-Definition + Bewertungs-Raster (status: vorgeschlagen)

Segment-Vorschlag:
- Segmentierungs-Achse: <leistungsart | zielgruppe | region>
- Segmente: <N> — <kurze Aufzählung der Anzeigenamen>
- Kunden-Datendateien: <gefunden: Liste | keine — Segmentgrößen als schaetzung_skill>

Pflicht-Review durch den Strategen:
Bitte prüfen: Sind die Segmente trennscharf und vollständig? Stimmt die Segmentierungs-Achse?
Sind die Engpass-Kandidaten pro Segment realistisch? Bandbreiten-Logik bestätigt?
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text`):

```yaml
blockiert:
  - skill: 04-07-segment-potenzial-matrix (Phase B)
    wartet_auf: "Strategen-Review von synthese/segment-potenzial-matrix-schema.md (auf Drive)"
```

---

## Phase B — Segment-Matrix berechnen

### Schritt B.1: Schema-Validierung

Lies `synthese/segment-potenzial-matrix-schema.md` aus Drive. Prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis auf Phase A.
2. 2–4 Segmente definiert, jedes mit `segment_slug`, `anzeigename`, `abgrenzung`.
3. Genau eine Segmentierungs-Achse gewählt.
4. Bewertungs-Raster vollständig: vier Matrix-Achsen mit Gewichtung, Engpass-Kandidaten pro Segment, Bandbreiten-Set.

Bei Fehler: konkreter Hinweis, welches Feld zu korrigieren ist.

### Schritt B.2: Existenz-Check Output

Wenn `synthese/segment-potenzial-matrix.md` oder `.csv` auf Drive bereits existieren: fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Pro Segment fünf Auswertungs-Blöcke rechnen

Für **jedes** Segment werden fünf Blöcke ausgewertet. Methodik-Details und Formeln in `reference/segment-matrix-methodik.md`. Kurzfassung:

1. **Marktpotenzial (bottom-up)** — Segment-Marktgröße bottom-up: relevante Nachfrage (Such-Volumen / Ziel-Kundenzahl im Einzugsgebiet / adressierbare Accounts) × erwartbare Marketing-Reichweite × Conversion-Bandbreite × Marge bzw. AOV des Segments. Drei Szenarien. Quelle pro Faktor explizit (`erhoben` / `briefing` / `benchmark` / `schaetzung_skill`).
2. **Ist-Position des Kunden** — wie stark ist der Kunde im Segment heute aufgestellt? Aus Kunden-Datendateien (Umsatzanteil heute, Auftragszahlen) wenn vorhanden, sonst aus Briefing/Kunden-Profil. Liefert den Abstand zwischen Ist und Potenzial.
3. **Kritische Erreichbarkeits-Prüfung** — der ehrliche Kern: Ist das Segment mit Marketing real adressierbar? Prüfe Such-/Awareness-Verhalten der Zielgruppe, ob der Kauf marketing-getrieben oder beziehungs-/ausschreibungs-getrieben ist, ob digitale Touchpoints überhaupt erreichbar sind. Ergebnis ist der `erreichbarkeit`-Score plus eine klare Aussage `marketing_adressierbar: ja | eingeschraenkt | nein`.
4. **Hebel + Kanal-Mix** — welche Kanäle (aus `kanal-chancen.md`) tragen dieses Segment? Pro Segment ein priorisierter Kanal-Mix mit Begründung. Hier wird die Kanal-Sicht und die Segment-Sicht verbunden.
5. **Aufwands-Hochrechnung** — was kostet die Erschließung des Segments? Setup-Aufwand plus laufender Aufwand als Bandbreite (EUR-Spend für Paid-Anteile, Stunden-Range für organische/Service-Anteile). Time-to-Impact-Schätzung pro Segment.

Alle Werte als **Bandbreite** (`konservativ` / `realistisch` / `ambitioniert`) — niemals Punktschätzungen. Jede Zahl trägt einen Quellen-Typ (`erhoben` / `briefing` / `benchmark` / `schaetzung_skill`, siehe `contracts.md` Abschnitt 13). **Load-bearing Heuristiken** — Annahmen, die die Priorisierung oder eine Engpass-Aussage tragen — werden zusätzlich als explizite Auffälligkeit markiert.

**Konsistenz mit dem Forecast (Pflicht-Cross-Check, `contracts.md` Abschnitt 12):** Die Summe der Segment-Marktpotenziale (realistisch) wird gegen `forecast.md` `aggregat_12_monate.real.umsatz_eur` gestellt. Weicht die Segment-Summe **> 20 %** vom Forecast-Aggregat ab, wird das als explizite Auffälligkeit `segment_summe_vs_forecast_diskrepanz` ausgewiesen — der Forecast bleibt die Leit-Zahl, die Segment-Matrix erklärt die Verteilung darunter. Geteilte Parameter (AOV, Conversion-Bandbreiten, Doppelzählungs-Faktor) werden aus dem Forecast bzw. dem bestätigten Annahmen-Schema gezogen, nicht pro Segment neu angenommen.

### Schritt B.4: Engpass- / Kapazitäts-Analyse pro Segment

Für jedes Segment den **limitierenden Faktor** benennen — das ist der inhaltliche Kern dieses Skills. Geprüft wird, ob das Wachstum des Segments durch das **Marketing-Potenzial** gedeckelt ist oder durch die **reale Kapazität des Kunden** (Liefer-/Produktions-Kapazität, Personal, Vertriebs-Durchsatz, Onboarding/Service).

Pro Segment ein `engpass_typ` aus:

| `engpass_typ` | Bedeutung |
|---|---|
| `marketing_potenzial` | Der Markt bzw. die erreichbare Nachfrage limitiert — mehr Marketing-Budget bringt mehr |
| `liefer_kapazitaet` | Produktions-/Liefer-/Material-Kapazität des Kunden limitiert — mehr Leads helfen nicht |
| `personal_kapazitaet` | Fachkräfte / Team-Größe limitiert die Leistungserbringung |
| `vertriebs_kapazitaet` | Lead-Verarbeitung / Angebots-Durchsatz limitiert |
| `onboarding_service` | Service-/Onboarding-Kapazität limitiert (typisch SaaS, Beratung) |
| `kein_klarer_engpass` | beide Seiten skalieren mit — kein dominanter Engpass erkennbar |

**Häufiger und wichtiger Befund:** In der Praxis ist oft **nicht das Marketing**, sondern die **Kunden-Kapazität** der Engpass. Wenn ein Segment ein hohes Marketing-Potenzial hat, aber die Liefer-/Personal-Kapazität des Kunden begrenzt ist, ist die ehrliche Empfehlung **nicht** "mehr Budget in das Segment", sondern z. B. "Marge-Optimierung statt Mengen-Wachstum", "Kapazität zuerst aufbauen" oder "Budget in ein anderes Segment lenken". Diese Befunde gehören prominent in die Engpass-Analyse, die strategische Story und — wenn load-bearing — in die Auffälligkeiten.

Die Engpass-Aussage stützt sich auf Briefing-Kapazitäts-Aussagen (`briefing`) und, wo vorhanden, auf Kunden-Datendateien. Liegt keine belastbare Kapazitäts-Info vor, wird der Engpass-Befund als `schaetzung_skill` markiert und als Auffälligkeit (`engpass_unbestaetigt`) ausgewiesen, mit der Empfehlung, ihn im Kunden-Gespräch zu verifizieren — Kunden-Aussagen zur Kapazität sind Hypothesen, keine Fakten (`contracts.md` Abschnitt 13).

### Schritt B.5: Gesamt-Matrix und Priorisierung

Für jedes Segment werden die vier Matrix-Achsen (0–100) gesetzt:

- `potenzial` — aus Block 1 (Marktpotenzial realistisch, gemappt auf 0–100 relativ zum größten Segment)
- `aufwand` — aus Block 5, **invertiert** (hoch = niedriger Aufwand)
- `erreichbarkeit` — aus Block 3 (kritische Erreichbarkeits-Prüfung)
- `time_to_impact` — aus Block 5, **invertiert** (hoch = schnelle Wirkung)

Daraus der `prioritaet_score` (gewichtetes Mittel, Default-Gewichte und Branchen-Overrides in `reference/segment-matrix-methodik.md`):

```text
prioritaet_score = (
    0.35 * potenzial
  + 0.20 * aufwand
  + 0.30 * erreichbarkeit
  + 0.15 * time_to_impact
)
```

`erreichbarkeit` ist bewusst hoch gewichtet — ein Segment mit großem Potenzial, das marketing nicht adressierbar ist, darf nicht oben landen.

**Engpass-Deckelung:** Ist der `engpass_typ` eines Segments **nicht** `marketing_potenzial` und **nicht** `kein_klarer_engpass`, wird der `prioritaet_score` für die *Mengen-Logik* gedeckelt (Detail-Regel in der Methodik-Datei) — ein kapazitäts-gedeckeltes Segment ist kein guter Kandidat für ein Mengen-Wachstums-Budget, auch wenn das Marketing-Potenzial hoch ist.

**Priorisierung — zwei klar getrennte Sichten** (Pflicht, nicht vermischen):

1. **Mengen-Logik** — Reihung der Segmente nach `prioritaet_score`: Wo lohnt sich zusätzliches Mengen-/Wachstums-Budget am meisten?
2. **Umsetzungs-Reihenfolge** — eine *separate*, qualitative Reihenfolge: Welches Segment zuerst angehen (Quick-Win-/Foundation-/Long-Term-Logik, Abhängigkeiten, Kapazitäts-Vorlauf)? Diese Reihenfolge kann von der Mengen-Logik abweichen — z. B. ein kleines Segment zuerst, weil es Cashflow für den Kapazitäts-Aufbau eines größeren Segments liefert.

Beide Sichten werden im Output **getrennt benannt und begründet**.

### Schritt B.6: Auffälligkeiten

Mindestens **6 Auffälligkeiten**. Wenn weniger als 6 echte aus den Daten ableitbar sind: um methodische Hinweise ergänzen (z. B. dünne Datenbasis für ein Segment).

| Typ | Auslöser |
|---|---|
| `kapazitaet_ist_engpass` | Segment mit hohem Marketing-Potenzial, aber `engpass_typ` ≠ `marketing_potenzial` — Budget-Empfehlung umkehren |
| `segment_marketing_nicht_adressierbar` | Segment mit `marketing_adressierbar: nein` — Marketing ist nicht der Hebel, im Kunden-Gespräch erden |
| `segment_unterbespielt` | Segment mit hohem Potenzial + hoher Erreichbarkeit, aber niedrige Ist-Position |
| `segment_zu_klein` | Segment-Potenzial zu klein für relevanten Eigen-Fokus — ggf. mit anderem Segment bündeln |
| `mengen_vs_umsetzung_divergenz` | Mengen-Logik und Umsetzungs-Reihenfolge weichen deutlich ab — Stratege muss die Reihenfolge bewusst begründen |
| `segment_summe_vs_forecast_diskrepanz` | Summe der Segment-Potenziale weicht > 20 % vom `forecast.md`-Aggregat ab |
| `engpass_unbestaetigt` | Engpass-Befund nur als `schaetzung_skill` — im Kunden-Gespräch verifizieren |
| `segment_datenbasis_duenn` | Für ein Segment fehlen Kunden-Datendateien — Werte überwiegend `schaetzung_skill` |
| `marge_statt_menge` | Segment kapazitäts-gedeckelt mit guter Marge — Empfehlung Marge-/Preis-Optimierung statt Mengen-Wachstum |

### Schritt B.7: Strategische Story

Im Body der `segment-potenzial-matrix.md` ein narrativer Abschnitt (4–6 Sätze): Welches Segment trägt das Wachstum? Wo ist die Kapazität der Engpass, nicht das Marketing? Wie verhalten sich Mengen-Logik und Umsetzungs-Reihenfolge zueinander? **Ausdrücklich einordnen, dass diese Segment-Sicht die Kanal-Sicht aus `kanal-chancen.md` / `forecast.md` ergänzt, nicht ersetzt** — beide Sichten zusammen ergeben das vollständige Bild für die MTA.

### Schritt B.8: Output schreiben — Markdown + CSV nach Drive

Erzeuge `synthese/segment-potenzial-matrix.md` und `synthese/segment-potenzial-matrix.csv` lokal nach dem Schema in `reference/segment-output-schema.md` und lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "segment-potenzial-matrix.md" /tmp/segment-matrix.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "segment-potenzial-matrix.csv" /tmp/segment-matrix.csv "text/csv"
```

Das Frontmatter trägt `status: vorgeschlagen` (bis Stratege-Review), `generiert_am` und den `basis_inputs`-Block mit `generiert_am`-Stempeln der gelesenen Inputs (Staleness-Check nach `contracts.md` Abschnitt 12).

**Staleness-Check:** Vergleiche die `generiert_am`-Stempel von `forecast.md` und `kanal-chancen.md` mit einem ggf. bestehenden früheren `segment-potenzial-matrix.md`. Ist ein Input neuer → Staleness-Hinweis im Schluss-Format.

### Schritt B.9: HTML-Report

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschließlich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

**Report-Nummer bestimmen:** `reports/index.html` aus Drive lesen, prüfen welche Nummern belegt sind. Vorschlag `21-segment-potenzial.html`; ist `21` belegt, die nächste freie Zahl wählen. Die gewählte Nummer im Schluss-Format und im Dashboard-Eintrag verwenden.

Lies `_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`). Ersetze die acht Platzhalter (siehe `contracts.md` Abschnitt 7). Inhalt für `{{MAIN_CONTENT}}` — exakte Bausteine in `reference/segment-output-schema.md`:

- **Sticky-TOC** zu den Sektionen
- **Stat-Strip**: Anzahl Segmente, Segmentierungs-Achse, Top-Prioritäts-Segment, Anzahl kapazitäts-gedeckelter Segmente
- **Summary-Card**: Einordnung als ergänzende Zweitsynthese zur Kanal-Sicht
- **Matrix-Heatmap**: `table.data` Segment × Achse (`potenzial`, `aufwand`, `erreichbarkeit`, `time_to_impact`, `prioritaet_score`) — Zellen mit Rating-Badges (`stark`/`mittel`/`schwach`)
- **Pro Segment** ein `details.dim`-Block mit `data-rating` — die fünf Auswertungs-Blöcke, Bandbreiten-Tabelle, Engpass-Befund mit Badge
- **Engpass-Übersicht**: `table.ratings` Segment × `engpass_typ` + limitierender Faktor
- **Priorisierung**: zwei `top3`-Listen — Mengen-Logik und Umsetzungs-Reihenfolge, klar getrennt
- **Strategische Story**: `summary-card` am Ende
- **Auffälligkeiten**: `suggestion`-Blöcke, sortiert nach Relevanz
- **Datenbasis-Hinweis**: welche Inputs/Kunden-Datendateien vorlagen, welche Werte `schaetzung_skill` sind

Schreibe nach Drive via `drive.py upsert-text "$REPORTS_ID" "<nummer>-segment-potenzial.html" /tmp/report.html "text/html"`.

### Schritt B.10: Dashboard-Update und status.md

Beide Dateien aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben (siehe `contracts.md` Abschnitt 3 und 7).

**`status.md`:**

- `04-07-segment-potenzial-matrix` in `schritte_done`, aus `schritte_offen` und `blockiert` entfernen
- Body-Eintrag unter "✓ Erledigt" mit Outputs und Hinweis, dass die Matrix bis Stratege-Review `status: vorgeschlagen` trägt
- `naechster_empfohlen`: in der Regel `04-05-90-tage-plan` oder `05-01-mta-slide-bausteine` (je nachdem, was noch offen ist) — `04-07` blockiert keinen Folge-Skill

**Dashboard `reports/index.html`:**

- Reports-Liste um den Segment-Report ergänzen (Link mit Titel und Kurzbeschreibung)
- Status-Sektion aktualisieren
- Token-Breakdown-Slots aktualisieren (`{{TOKEN_BREAKDOWN}}` via `token-tracker.py render-counter --style breakdown`, Stat-Strip via `--style stat-strip`)
- `<body class="is-dashboard">` beibehalten

### Schritt B.11: Standard-Schlussformat im Chat

```text
✓ 04-07-segment-potenzial-matrix Phase B abgeschlossen.

Outputs (auf Drive):
- synthese/segment-potenzial-matrix.md — Segment-Sicht (status: vorgeschlagen bis Review)
- synthese/segment-potenzial-matrix.csv — Roh-Tabelle (Segment x Auswertungs-Block)
- reports/<nummer>-segment-potenzial.html — Matrix-Heatmap, Engpass-Karten, Priorisierung
Status aktualisiert in: status.md

Segment-Matrix:
- Segmentierungs-Achse: <achse>
- Segmente bewertet:    <N>
- Top-Priorität (Menge): <segment> (prioritaet_score <X>)
- Umsetzungs-Reihenfolge: <segment-1> → <segment-2> → ...
- Kapazitäts-gedeckelte Segmente: <N von M>

Top strategische Beobachtungen:
1. <Auffälligkeit 1>
2. <Auffälligkeit 2>
3. <Auffälligkeit 3>

[Bei segment_summe_vs_forecast_diskrepanz oder Staleness:]
ℹ Hinweis: <Diskrepanz / Re-Run-Empfehlung>

Diese Segment-Sicht ergänzt die Kanal-Sicht (kanal-chancen.md / forecast.md) — sie ersetzt sie nicht.

Nächste Schritte:
1. Matrix reviewen, dann status: bestaetigt setzen
2. <04-05-90-tage-plan | 05-01-mta-slide-bausteine> — <Begründung>

Sag mir, welcher als nächster.
```

## Modi

- **Voll**: Forecast + Kanal-Chancen + Briefing + Kunden-Datendateien vorhanden — Segmentgrößen belegt, hohe Konfidenz
- **Reduced**: Pflicht-Inputs vorhanden, aber keine Kunden-Datendateien — Segmentgrößen als `schaetzung_skill`, Auffälligkeit `segment_datenbasis_duenn`
- **Abbruch**: ein Pflicht-Input fehlt — kein Lauf, Hinweis auf Vorgänger-Skill

## Edge Cases

- **Kunde hat nur ein erkennbares Segment** → Skill weist in Phase A darauf hin: bei einem einzigen kohärenten Geschäft bringt die Segment-Sicht keinen Mehrwert über die Kanal-Synthese hinaus. Empfehlung, `04-07` zu überspringen. Wenn der Stratege trotzdem laufen will (Override "trotzdem laufen"): Skill segmentiert nach Zielgruppe oder Funnel-Stufe als Ersatz-Achse und markiert die Segmente als schwach getrennt.
- **Mehr als 4 plausible Segmente** → Skill bündelt zu maximal 4 (kleinste/ähnlichste zusammenfassen) und vermerkt die Bündelung im Schema. Mehr als 4 Segmente überfrachten die Matrix.
- **Briefing nennt keine Kapazitäts-Aussagen** → alle Engpass-Befunde als `schaetzung_skill`, Auffälligkeit `engpass_unbestaetigt`, prominenter Hinweis, dass die Engpass-Frage im Kunden-Gespräch zu klären ist.
- **`forecast.md` als `forecast-modell.md` o. ä. nicht gefunden** → der Pflicht-Input ist `synthese/forecast.md` (der reale Output-Name von `04-04`). Findet der Skill ihn nicht, aber eine ähnlich benannte Datei (`forecast-modell.md`), Hinweis im Abbruch — kein automatisches Raten.
- **Stratege wünscht Re-Run mit veränderter Segment-Definition** → Override-Argument "Segmente überarbeiten" → Skill setzt das Schema auf `vorgeschlagen` zurück (mit Backup der Phase-B-Outputs), Stratege editiert, bestätigt, Phase B neu.
- **`reports/_shell.html` fehlt auf Drive** → Hinweis im Schluss-Format, HTML-Report wird als minimaler Plain-HTML-Stub geschrieben und hochgeladen.
- **Segment-Summe weicht stark vom Forecast ab** → keine stille Korrektur — Auffälligkeit `segment_summe_vs_forecast_diskrepanz`, der Forecast bleibt die Leit-Zahl.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt — Phase B läuft niemals ohne `status: bestaetigt`
- Outputs leben auf Google Drive in `synthese/` und `reports/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für das Aggregat, CSV als Single-Source-of-Truth
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (lesen, patchen, upsert)
- HTML-Report aus `reports/_shell.html`, ausschließlich kanonische Bausteine, Validierung vor Upload Pflicht
- **Pflicht-Bandbreite, niemals Punktschätzungen** — jede Zahl als konservativ/realistisch/ambitioniert
- **Quellen-Kennzeichnung pro Zahl** (`erhoben` / `briefing` / `benchmark` / `schaetzung_skill`); load-bearing Heuristiken zusätzlich als Auffälligkeit
- **Pflicht-Input-Check statt Silent-Fallback** — fehlt Forecast/Kanal-Chancen/Briefing, harter Abbruch
- **Kritische Haltung** — Kunden-Kapazitäts-Aussagen sind Hypothesen, gegen Daten prüfen; der Engpass-Befund ist der ehrliche Kern dieses Skills
- **Schreibt NICHT in `forecast.md`, `kanal-chancen.md` oder `briefing.md` zurück** — die Segment-Matrix ist eine eigene, ergänzende Quelle

## Reference-Dateien

- `reference/segment-schema-template.md` — Format des Phase-A-Outputs (`segment-potenzial-matrix-schema.md`) mit Beispiel-Segment-Set und Bewertungs-Raster
- `reference/segment-matrix-methodik.md` — die fünf Auswertungs-Blöcke, die vier Matrix-Achsen mit Score-Berechnung, Engpass-Typologie, `prioritaet_score`-Aggregation, Engpass-Deckelung, Mengen-Logik vs. Umsetzungs-Reihenfolge
- `reference/segment-raster-defaults.md` — Branchen-Defaults für Conversion-, Marge- und Time-to-Impact-Referenzwerte pro Segmentierungs-Achse
- `reference/segment-output-schema.md` — exakte Definition der Markdown-Frontmatter-Struktur, des CSV-Schemas und der HTML-Sektionen
