---
name: 04-01-positionierungs-analyse
description: Aggregiert die Marken-Profile von Kunde und Wettbewerbern zu einem 2D-Positionierungs-Mapping mit Markt-Cluster-Erkennung, White-Space-Analyse und Bewegungs-Empfehlung. Strategisches Herz der MTA - zeigt, wo der Kunde im Wettbewerbsumfeld steht und welche Differenzierungs-Lücken offen sind. Nutzt Schema-vor-Lauf - Phase A schlägt Achsen-Kombinationen vor (Default Tonalitäts-Achsen plus Alternativen wie USP-Differenzierung, Funnel-Fokus), Stratege bestätigt, Phase B baut das 2D-Mapping mit SVG-Visualisierung. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext eine Positionierungs-Analyse, ein Marken-Mapping oder eine Differenzierungs-Analyse will - auch bei Phrasen wie "Positionierungs-Mapping", "Marken-Mapping bauen", "Wo steht der Kunde im Wettbewerb", "Differenzierungs-Lücken finden", "White-Space-Analyse", "Markt-Cluster erkennen", "Brand-Positioning". Setzt voraus, dass 02-01-kunden-marken-profil und 02-03-wettbewerber-marken-profil gelaufen sind - bricht sonst ab.
---

# Positionierungs-Analyse

Erster Skill in Stufe 4 (Synthese) der MTA. **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8). Aggregiert die in `02-01-kunden-marken-profil` und `02-03-wettbewerber-marken-profil` erstellten Profile zu einem **2D-Positionierungs-Mapping** — der visuellen Story-Achse der MTA.

**Drei strategische Outputs:**

1. **2D-Mapping** — Akteure (Kunde + WBs) als Punkte auf zwei vom Strategen gewählten Achsen
2. **Markt-Cluster** — Gruppen von Akteuren, die auf ähnlichen Positionen landen (Sub-Segmente in der Branche)
3. **White-Space + Bewegungs-Empfehlung** — leere Quadranten als strategische Freiräume plus konkrete Richtung, in die sich der Kunde bewegen könnte, um sich abzusetzen

Der Skill ist die Brücke zwischen den deskriptiven Stufe-2-Marken-Profilen und der präskriptiven Stufe-4-Strategie. Er beantwortet die Frage: **"Wo ist im Markt noch Luft, und wohin sollte sich der Kunde bewegen?"**

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

- "Positionierungs-Analyse erstellen"
- "Positionierungs-Mapping bauen"
- "Marken-Mapping"
- "Brand-Positioning"
- "Wo steht der Kunde im Wettbewerb"
- "Differenzierungs-Lücken finden"
- "White-Space-Analyse"
- "Markt-Cluster erkennen"
- "Welche Positionierungs-Räume sind frei"
- "2D-Positionierungs-Karte"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen
- `02-01-kunden-marken-profil` gelaufen → `data/kunde.md` vorhanden
- `02-03-wettbewerber-marken-profil` gelaufen → mindestens 2 `wettbewerber/SLUG.md`-Dateien vorhanden
- `wettbewerber/liste.md` mit `status: bestaetigt`
- Empfohlen: `audits/seo-keyword-cluster.csv` (wenn Achsen-Vorschlag auf Keyword-Cluster zurückgreifen soll, z. B. Funnel-Fokus-Achse)
- Empfohlen: `data/briefing.md` (für Differenzierungs-Hypothese aus Strategen-Brille)
- Empfohlen: `data/abweichungen.md` (für Auffälligkeit `kunde_position_widerspruechlich`)

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `synthese/positionierung-schema.md` existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B läuft.

### Phase-Entscheidungs-Logik (Schritt 1 bei jedem Aufruf)

Zuerst die Drive-Bootstrap (siehe `contracts.md` Abschnitt 1):

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Schema und Outputs liegen auf Drive im `synthese/`-Sub-Folder:

```
1. Existiert synthese/positionierung-schema.md auf Drive? (drive.py find_by_name "$SYNTHESE_ID" "positionierung-schema.md")
   - Nein → Phase A (Schema generieren)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt → Phase B (eigentliches Mapping)
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert synthese/positionierung.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen: überschreiben / Backup-und-neu / abbrechen
```

---

## Phase A — Achsen-Schema generieren

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Prüfe via `drive.py list-children`:

- `data/kunde.md` vorhanden in `DATA_ID`? Sonst Abbruch mit Hinweis auf `02-01-kunden-marken-profil`
- Mindestens 2 Marken-Profil-Dateien in `WB_ID` (außer `liste.md`)? Sonst Abbruch mit Hinweis auf `02-03-wettbewerber-marken-profil`
- `wettbewerber/liste.md` mit `status: bestaetigt`? Sonst Abbruch

Bei fehlenden Voraussetzungen:

```
✗ Voraussetzungen für 04-01-positionierungs-analyse fehlen.
Bitte zuerst 02-01-kunden-marken-profil und 02-03-wettbewerber-marken-profil laufen lassen.
Aktuell fehlt: [konkrete Liste]
```

Lies optionale Inputs aus Drive (`find_by_name` + `read_text`):

- `audits/seo-keyword-cluster.csv` via `find_by_name(AUDITS_ID, "seo-keyword-cluster.csv")` (für Funnel-Fokus-Achse, falls SEO-Cluster vorhanden)
- `data/briefing.md` via `find_by_name(DATA_ID, "briefing.md")` (für Strategen-Intention und Differenzierungs-Hypothese)
- `data/abweichungen.md` via `find_by_name(DATA_ID, "abweichungen.md")` (für Auffälligkeit `kunde_position_widerspruechlich`)

### Schritt A.2: Akteurs-Inventur

Sammle alle Akteure für das Mapping:

1. **Kunde**: immer dabei, aus `data/kunde.md`
2. **Wettbewerber mit `empfehlung_profilieren: ja`**: aus `wettbewerber/liste.md` Frontmatter — diese sind die strategisch relevanten WBs
3. **Best-Practice-WBs**: alle mit `kategorie: best_practice_ueberregional` (auch wenn aus anderer Region — sie sind orientierend, nicht direkt konkurrierend)

Pro Akteur die Marken-Profil-Datei aus Drive lesen (`find_by_name(WB_ID, "<slug>.md")` bzw. `find_by_name(DATA_ID, "kunde.md")` → `read_text`) und die für die Achsen-Berechnung relevanten Felder extrahieren:

- `tonalitaet.*.achse_wert` (4 Tonalitäts-Achsen, Skala -2 bis +2)
- `usps_wie_kommuniziert` (Liste der USPs für USP-Differenzierungs-Achse)
- `portfolio_wie_kommuniziert` (für Portfolio-Breite und Preis-Wahrnehmung)
- `zielgruppen_hypothese_aus_website` (für Zielgruppen-Breite)
- `hero_test.gesamt_score` (für Kommunikations-Klarheits-Achse)
- `verstaendlichkeit_startseite.score` (analog)

Akteure ohne ausreichende Daten (z. B. Reduced-Mode-WBs ohne Tonalitäts-Bewertung) werden mit Konfidenz-Markierung mitgeführt — Stratege entscheidet in Phase A, ob sie ins Mapping rein dürfen.

### Schritt A.3: Achsen-Vorschläge ableiten

Default-Achsen-Kombinationen sind in `reference/achsen-template.md` pro Branchen-Typ vorgegeben. Standard-Vorschlag:

**Achsen-Default (immer als ersten Vorschlag):**

- **X-Achse**: `formell ↔ informell` (Tonalitäts-Achse 1)
- **Y-Achse**: `expertise-zentriert ↔ partnerschaftlich` (Tonalitäts-Achse 2)

Begründung im Schema: Diese zwei Achsen sind aus dem Marken-Profil direkt verfügbar (Skala -2 bis +2), haben in fast jeder Branche differenzierungs-relevanten Spread und sind für den Kunden im Strategie-Gespräch sofort verständlich.

**Alternative Achsen-Vorschläge (in dieser Reihenfolge, je nach Branchen-Typ und Datenlage):**

| Achse | Skala-Definition | Wann sinnvoll |
|---|---|---|
| `sachlich ↔ emotional` | Tonalitäts-Achse 3, -2 bis +2 | Wenn Branche emotional aufgeladen ist (Lifestyle, B2C) |
| `modern ↔ traditionell` | Tonalitäts-Achse 4, -2 bis +2 | Wenn Branche im Generationen-Wechsel ist (Handwerk, Bank, Versicherung) |
| `USP-Differenzierung: Preis-Fokus ↔ Premium-Fokus` | abgeleitet aus USPs und Portfolio, -2 bis +2 (-2 = stark Preis-Argument, +2 = stark Premium-/Qualitäts-Argument) | Wenn Preis im Briefing als Hebel genannt ist |
| `Zielgruppen-Breite: spezialist ↔ generalist` | aus Persona-Anzahl und Portfolio-Breite | Wenn Strategie-Frage "fokussieren oder breitern?" ansteht |
| `Funnel-Fokus: Awareness ↔ Decision` | aus SEO-Cluster-Funnel-Verteilung (TOFU/BOFU-Anteil) | Wenn SEO-Cluster vorhanden ist und Funnel-Differenzierung im Fokus steht |
| `Kommunikations-Klarheit: unklar ↔ klar` | aus Hero-Test-Gesamt-Score + Verständlichkeits-Score | Wenn Branche viele intransparente Anbieter hat |

Jeder Vorschlag mit:

- Klarer Achsen-Definition (Pole + Skala)
- Berechnungs-Logik aus den Marken-Profil-Feldern
- Branchen-Eignungs-Begründung
- Erwartetem Spread (wie breit der Cluster der Akteure voraussichtlich liegt)

Der Default-Vorschlag wird empfohlen — der Stratege kann frei tauschen.

### Schritt A.4: Cluster-Definition (Markt-Cluster-Erkennungs-Schwellwerte)

Markt-Cluster im 2D-Raum werden über euklidische Distanz erkannt. Default-Schwelle: **Cluster-Radius 1.0** auf der jeweiligen Achsen-Skala (das entspricht bei der Standard -2-bis-+2-Skala einem Viertel der Gesamtbreite — eng genug für strategisch relevante Ähnlichkeit, breit genug für 2-3-Akteur-Cluster).

Im Schema werden vorgeschlagen:

- `cluster_radius`: Default 1.0 (anpassbar 0.5 bis 2.0)
- `mindestgroesse_cluster`: Default 2 Akteure (ab 2 WBs auf ähnlicher Position = Markt-Cluster, allein-stehender Akteur ist kein Cluster)
- `kunde_immer_eigenstaendig`: Default `false` (Kunde wird wie jeder andere Akteur geclustert; auf `true` setzen, wenn der Stratege den Kunden bewusst als Solitär anzeigen will)

### Schritt A.5: Differenzierungs-Achse-Hypothese

Wichtigster strategischer Input für die spätere Bewegungs-Empfehlung. Der Skill schlägt eine **Differenzierungs-Richtung** vor, basierend auf:

1. **Wo ist im aktuellen Mapping White-Space?** Vorab-Berechnung mit Default-Achsen.
2. **Was sagt das Briefing zur Differenzierung?** `data/briefing.md` Frontmatter-Felder zu Strategie-Intention.
3. **Wo sind die Abweichungen zwischen Briefing und Website?** Aus `data/abweichungen.md` — wenn der Kunde sich anders sieht als seine Website kommuniziert, ist das oft ein Hinweis auf die gewünschte Bewegungs-Richtung.

Format der Hypothese im Schema:

```
differenzierungs_hypothese:
  richtung: "z.B. weg von expertise-zentriert hin zu partnerschaftlich + emotional"
  begruendung: "Briefing nennt 'auf Augenhöhe mit Kunden' als Selbstbild,
                 Website kommuniziert aber stark Awards und Top-Listen-Plätze.
                 Im Mapping ist der Quadrant 'partnerschaftlich + emotional' leer."
  konfidenz: hoch | mittel | niedrig
```

Stratege bestätigt oder überschreibt im Schema-Review.

### Schritt A.6: `synthese/positionierung-schema.md` nach Drive schreiben

Erzeuge das vollständige Schema lokal nach `reference/achsen-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "positionierung-schema.md" \
  /tmp/positionierung-schema.md "text/markdown"
```

Stratege kann die Datei direkt in Drive editieren.

Sektionen:

- **Frontmatter**: Skill-Metadaten, Anzahl Akteure für Mapping, Default-X-Achse, Default-Y-Achse, Liste Alternative-Achsen, Cluster-Radius, Differenzierungs-Hypothese
- **Body**:
  - Übersicht der Akteurs-Inventur (wer ist drin, wer ist optional drin, wer fehlt)
  - Standard-Achsen-Vorschlag mit Begründung
  - Alternative Achsen-Vorschläge in Reihenfolge
  - Cluster-Schwellwerte
  - Differenzierungs-Hypothese (mit Begründung)
  - Pflicht-Review-Sektion für den Strategen mit konkreten Eingriffspunkten

### Schritt A.7: Schluss-Format Phase A

```
✓ 04-01-positionierungs-analyse Phase A abgeschlossen.

Outputs (auf Drive):
- synthese/positionierung-schema.md — Achsen-Schema (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Akteure im Mapping: N (davon Kunde, M zu profilierende WBs, K Best-Practice)
- X-Achse Default:    formell ↔ informell
- Y-Achse Default:    expertise ↔ partnerschaftlich
- Alternativen:       4-6 Achsen vorgeschlagen
- Cluster-Radius:     1.0 (auf -2 bis +2 Skala)
- Differenzierungs-Hypothese: HYPOTHESE_RICHTUNG

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Achsen-Kombination (Default oder Alternative auswählen), Akteurs-Auswahl (WBs reduzieren oder ergänzen), Cluster-Radius, Differenzierungs-Hypothese.
Achsen-Wahl prägt die ganze MTA-Story - bitte bewusst entscheiden.
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text "$FOLDER_ID" "status.md"`):

```yaml
blockiert:
  - skill: 04-01-positionierungs-analyse (Phase B)
    wartet_auf: "Strategen-Review von synthese/positionierung-schema.md (auf Drive)"
```

---

## Phase B — 2D-Mapping erzeugen

### Schritt B.1: Schema-Validierung

Lies `synthese/positionierung-schema.md` aus Drive (`find_by_name(SYNTHESE_ID, "positionierung-schema.md")` → `read_text`). Prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis auf Phase A
2. X-Achse und Y-Achse definiert? Mit Pole und Skala?
3. Mindestens 3 Akteure für das Mapping (Kunde + 2 WBs minimum)?
4. Cluster-Schwellwerte numerisch?
5. Differenzierungs-Hypothese ausgefüllt?

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Existenz-Check Output

Wenn `synthese/positionierung.md`, `synthese/positionierung-mapping.csv` oder der HTML-Report auf Drive bereits existieren (`drive.py find_by_name`): fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Achsen-Werte pro Akteur berechnen

Logik pro Achse aus `reference/mapping-methodik.md`:

**Bei direkten Tonalitäts-Achsen** (formell-informell, expertise-partnerschaftlich, sachlich-emotional, modern-traditionell):

- Wert direkt aus `tonalitaet.<achse>.achse_wert` (-2 bis +2)
- Wenn `null` (keine Belege im Profil) → Konfidenz `niedrig`, Wert `0` (neutral) als Fallback, im Output explizit markiert

**Bei abgeleiteten Achsen:**

- `USP-Differenzierung: Preis ↔ Premium`: USPs nach Schlüsselwörtern klassifizieren (preis, günstig, sparen, vs. premium, qualität, exzellenz). Score = (Premium-Hits - Preis-Hits) / max(1, Gesamt-Hits) × 2, gekappt auf [-2, +2]
- `Zielgruppen-Breite: spezialist ↔ generalist`: Anzahl der Personas in `zielgruppen_hypothese_aus_website` plus Portfolio-Breite. Score-Mapping: 1 Persona+1 Kategorie = -2 (spezialist), 4+ Personas oder 5+ Kategorien = +2 (generalist), Rest linear interpoliert
- `Funnel-Fokus: Awareness ↔ Decision`: aus SEO-Cluster-CSV — TOFU-Anteil des Akteurs minus BOFU-Anteil, × 2, gekappt auf [-2, +2]. Nur für Kunde und WBs mit Ranking-Daten verfügbar
- `Kommunikations-Klarheit: unklar ↔ klar`: (Hero-Test-Gesamt + Verständlichkeit) / 2, lineare Skalierung von [1,5] auf [-2,+2]

Pro Akteur das Tupel `(x_wert, y_wert, konfidenz_x, konfidenz_y)` speichern.

### Schritt B.4: 2D-Mapping erzeugen — als eigene SVG-Datei

Visualisierung als **SVG** (keine externen JS-Libs):

- SVG-Größe: 800×800 px (Quadrat — Achsen sind gleichberechtigt)
- Quadranten-Grid (4 Quadranten, sichtbare Mittelachsen, Skala -2 bis +2)
- Akteure als Punkte (Kreise) mit Label
- **Punkt-Größe = Marken-Stärke-Indikator**: Kombination aus Hero-Test-Gesamt-Score (Größe) und Verständlichkeits-Score
- **Punkt-Farbe**: Kunde in `#ec644a` (REACHX-Sunrise-Red), WBs in `#000a14` (Night-Sky), Best-Practice-WBs in Grau `#7a8a99`
- Cluster-Markierung: gestricheltes Polygon um Akteure, die im selben Cluster sind, mit Cluster-Label

**Wichtig — SVG in eine eigene Datei auslagern:** Das 2D-Mapping wird **nicht** inline in den HTML-Report gerendert, sondern als eigenständige Datei `synthese/positionierungs-mapping.svg` geschrieben (siehe Schritt B.10a) und vom HTML-Report nur **referenziert** (`<img src="../synthese/positionierungs-mapping.svg">`) bzw. der SVG-Quelltext aus der Datei eingebettet. Grund: Das rechenintensive Inline-Rendern des Quadranten-Grids mit Punkten, Labels und Cluster-Polygonen direkt im Report-Render-Schritt hat in der Praxis den Subagenten zum Stillstand gebracht (beobachteter 600-Sekunden-Stall). Die SVG-Datei wird **zuerst** erzeugt — vor dem HTML-Report.

SVG-Konstruktions-Details in `reference/positionierung-output-schema.md`.

### Schritt B.5: Markt-Cluster-Erkennung

Algorithmus (einfache Distanz-basierte Clusterung, deterministisch reproduzierbar):

```
1. Berechne euklidische Distanz für jedes Akteurs-Paar
2. Wenn distanz <= cluster_radius (aus Schema): Paar gilt als "nah"
3. Transitive Hülle bilden: A-nah-B und B-nah-C → A,B,C im selben Cluster
4. Cluster mit Größe >= mindestgroesse_cluster aus Schema werden ausgewiesen
5. Kunde im Cluster mit WBs: starke Auffälligkeit (kunde_in_dichtem_cluster)
6. Kunde allein: Auffälligkeit kunde_alleinstellung_existiert
```

Pro Cluster: Mittelpunkt berechnen (Schwerpunkt der Akteurs-Punkte) als Cluster-Label-Position im SVG.

### Schritt B.6: White-Space-Analyse

Vier Quadranten des 2D-Raums:

- Q1: oben-rechts (X positiv, Y positiv)
- Q2: oben-links (X negativ, Y positiv)
- Q3: unten-links (X negativ, Y negativ)
- Q4: unten-rechts (X positiv, Y negativ)

Pro Quadrant:

- Anzahl Akteure (Kunde mitgezählt)
- Wenn 0 Akteure: White-Space (Auffälligkeit `whitespace_strategie_relevant`)
- Wenn 1 Akteur (insbesondere wenn der Akteur Kunde ist): potenzielle Alleinstellung
- Wenn alle Akteure in 1-2 Quadranten: `tonale_homogenitaet_branche` (Branche ist auf den Achsen homogen — Differenzierungs-Chance)

Strategische Relevanz der White-Spaces wird mit der Differenzierungs-Hypothese aus dem Schema abgeglichen — der Quadrant, der die Hypothese am besten erfüllt, wird als `whitespace_empfohlen` markiert.

### Schritt B.7: Bewegungs-Empfehlung für den Kunden

Aus der Differenzierungs-Hypothese (Schema) plus White-Space-Analyse (Schritt B.6) plus Cluster-Position des Kunden (Schritt B.5) wird die Bewegungs-Empfehlung abgeleitet:

```
bewegungs_empfehlung:
  ist_position: (x, y)
  ziel_position: (x', y')
  bewegungs_richtung: "z.B. nach rechts oben - hin zu partnerschaftlich + informell"
  begruendung: "Im Quadrant rechts-oben gibt es keinen WB, Differenzierungs-Hypothese
                 aus Schema deckt sich damit, Briefing nennt 'auf Augenhöhe' als Selbstbild."
  hebel_konkret:
    - "Tonalitäts-Shift in Hero-Headline von Awards-Statement zu Kunden-Story"
    - "Du-Anrede einführen (aktuell Sie)"
    - "Awards-Sektion weiter unten platzieren statt Hero-Sektion"
  aufwand_grob: niedrig | mittel | hoch
```

Empfehlung ist **nicht final** — der Stratege validiert im Kunden-Gespräch. Aber sie ist das **Roh-Material für die MTA-Strategie-Slides**.

### Schritt B.8: Auffälligkeiten ableiten

Mindestens 7 Auffälligkeiten-Typen, in dieser Reihenfolge prüfen:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_alleinstellung_existiert` | Kunde allein in einem Quadrant, keine WBs in Radius 1.0 | "Kunde positioniert sich allein im Quadrant 'informell + partnerschaftlich' - das ist ein Differenzierungs-Asset, sollte in der Kommunikation geschärft werden" |
| `kunde_in_dichtem_cluster` | Kunde im Cluster mit 2+ WBs auf nahezu identischer Position | "Kunde teilt Position mit alpha-tech und beta-solutions im Quadrant 'formell + expertise' - drei Akteure auf nahezu identischer Position, Differenzierung dringend nötig" |
| `kunde_position_widerspruechlich` | abweichungen.md vorhanden und Briefing-Selbstbild weicht von Website-Position ab | "Briefing positioniert Kunde als 'partnerschaftlich', Website rangiert aber als 'expertise-zentriert' (Y = -1.5). Selbstbild und Außenwahrnehmung weichen ab" |
| `markt_cluster_dominant` | Ein Cluster mit 3+ WBs | "3 WBs (alpha-tech, beta-solutions, gamma-werk) bilden einen dominanten Cluster im Quadrant 'formell + expertise' - dieser Position ist der Markt-Default, jeder davon abweichende Akteur differenziert sich automatisch" |
| `whitespace_strategie_relevant` | Quadrant ohne WB-Präsenz, der die Differenzierungs-Hypothese erfüllt | "Quadrant 'informell + partnerschaftlich' ist leer - White-Space, deckt sich mit Differenzierungs-Hypothese aus Briefing. Empfohlene Bewegungs-Richtung" |
| `tonale_homogenitaet_branche` | Alle Akteure (oder >75%) in 1-2 Quadranten | "8 von 9 Akteuren in Quadrant 'formell + expertise' - Branche ist tonal sehr homogen. Differenzierung über Achsen-Wechsel wirkungsvoller als über Achsen-Position" |
| `keine_wb_im_premium_segment` | (nur wenn USP-Differenzierungs-Achse aktiv) Quadrant mit hoher Premium-Achse leer | "Keiner der WBs spielt im Premium-Quadranten - Premium-Positionierung ist eine offene Strategie-Option" |
| `keine_wb_im_unteren_funnel` | (nur wenn Funnel-Fokus-Achse aktiv) Decision-Quadrant leer | "Alle WBs sind awareness-fokussiert - im Decision-Funnel ist Platz für aktivierende Inhalte" |
| `kunde_low_confidence_position` | Konfidenz X oder Y `niedrig` für Kunde | "Kunden-Position teilweise unsicher (Y-Wert aus Fallback) - Marken-Profil hat zu wenige Belege auf Achse Y. Profil mit mehr Belegen anreichern oder andere Y-Achse wählen" |

### Schritt B.9: Output `synthese/positionierung.md` nach Drive

Lokal generieren, dann `drive.py upsert-text "$SYNTHESE_ID" "positionierung.md" /tmp/positionierung.md "text/markdown"`. Vollständiges Schema in `reference/positionierung-output-schema.md`. Frontmatter:

```yaml
---
skill: 04-01-positionierungs-analyse
generiert_am: ISO-8601
schema_version: "1.0"
basis_schema: synthese/positionierung-schema.md
akteure_im_mapping: N
x_achse: "z.B. formell ↔ informell"
y_achse: "z.B. expertise ↔ partnerschaftlich"
markt_cluster_anzahl: K
whitespace_quadranten: 1
kunde_position:
  x: 1.0
  y: -0.5
  konfidenz_x: hoch
  konfidenz_y: mittel
auffaelligkeiten_anzahl: 6
auffaelligkeiten_typen: [kunde_alleinstellung_existiert, markt_cluster_dominant, ...]
---
```

Body strukturiert nach:

- **Übersicht**: gewählte Achsen, Akteurs-Inventur, Kurz-Story (3-5 Sätze: wo steht der Kunde, was differenziert ihn, wo ist Bewegungs-Spielraum)
- **2D-Mapping**: ASCII-Tabelle mit allen Akteuren und ihren (x, y)-Werten, sortiert nach Quadrant
- **Markt-Cluster**: pro Cluster: Cluster-Name, Akteure, Mittelpunkt, Cluster-Charakter (1-2 Sätze: was eint die Cluster-Akteure tonal/strategisch)
- **White-Space-Analyse**: pro Quadrant Akteurs-Zahl + Bewertung
- **Bewegungs-Empfehlung**: Ist-Position → Ziel-Position + konkrete Hebel + Aufwands-Schätzung
- **Auffälligkeiten**: sortiert nach strategischer Relevanz
- **Vorbereitung für Folge-Skills**: Hinweis, welche Erkenntnisse als Argumente für `04-02-kanal-chancen-analyse` und `05-01-mta-slide-bausteine` taugen

### Schritt B.9a: SVG-Datei `synthese/positionierungs-mapping.svg` nach Drive

**Output-Reihenfolge (verbindlich, `contracts.md` Abschnitt 3):** Erst die inhaltlichen Datei-Outputs (Markdown, SVG, CSV), zuletzt der HTML-Report und `status.md`. So bleibt ein vorzeitig beendeter Lauf (Subagent gekillt, Timeout) mit vollständigen, nutzbaren Outputs zurück.

Erzeuge die 2D-Mapping-Grafik aus Schritt B.4 als eigenständige SVG-Datei lokal und lade sie nach Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "positionierungs-mapping.svg" \
  /tmp/positionierungs-mapping.svg "image/svg+xml"
```

Die Datei ist self-contained (alle Styles im `<svg>`-Element selbst, keine externen Referenzen). Der HTML-Report in Schritt B.11 referenziert bzw. bettet sie ein — er rendert das Grid **nicht** erneut. Damit hängt der teure Grid-/Punkt-/Cluster-Render nicht am Report-Render-Schritt.

### Schritt B.10: CSV `synthese/positionierung-mapping.csv` nach Drive

Lokal generieren, dann `drive.py upsert-text "$SYNTHESE_ID" "positionierung-mapping.csv" /tmp/mapping.csv "text/csv"`. Spalten:

```
akteur_slug, akteur_typ, akteur_name, x_wert, y_wert, konfidenz_x, konfidenz_y,
quadrant, cluster_id, cluster_groesse, hero_test_score, verstaendlichkeit_score,
datenstand_iso
```

Für reproduzierbare Visualisierung und spätere Skill-Re-Runs. `akteur_typ` ist `kunde | wb_zu_profilieren | wb_best_practice`.

### Schritt B.11: HTML-Report `reports/X-positionierung.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Numerisches Präfix aus `status.md` ableiten (nächste freie Nummer ab Reports-Liste). `_shell.html` aus Drive lesen (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), Platzhalter füllen, dann `drive.py upsert-text "$REPORTS_ID" "X-positionierung.html" ... "text/html"`. Aus `reports/_shell.html`:

- Stat-Strip oben: Anzahl Akteure, Anzahl Markt-Cluster, Anzahl White-Space-Quadranten, Anzahl Auffälligkeiten
- Sticky-TOC zu: Mapping, Markt-Cluster, White-Space, Bewegungs-Empfehlung, Auffälligkeiten
- **2D-Mapping** (Hauptsektion, oben prominent): die in Schritt B.9a erzeugte `synthese/positionierungs-mapping.svg` einbinden — **nicht** das Grid hier im Report-Render-Schritt neu zeichnen. Den SVG-Quelltext aus der lokalen Datei `/tmp/positionierungs-mapping.svg` 1:1 in den `{{MAIN_CONTENT}}` kopieren (das SVG ist self-contained, kein eigener `<style>`-Block, keine eigenen CSS-Klassen — Validator-konform). Quadranten-Grid mit Achsen-Beschriftung, Akteurs-Punkte mit Labels, Cluster-Polygone, White-Space-Quadranten leicht hervorgehoben. Legende: Kunde / WB / Best-Practice / Cluster
- **Markt-Cluster-Block**: pro Cluster eine `details.skill`-Karte mit Akteurs-Liste und Cluster-Charakter
- **White-Space-Block**: vier Quadranten als 2×2-Grid mit Akteurs-Listen und Strategie-Note pro Quadrant
- **Bewegungs-Empfehlung** als `.suggestion`-Block prominent: Ist-Position, Ziel-Position, Hebel-Liste
- **Auffälligkeiten-Block**: nach Relevanz sortiert, mit Badges (`.badge.stark` für hoch-relevante)
- Footer

SVG-Details in `reference/positionierung-output-schema.md` Abschnitt SVG-Konstruktion.

### Schritt B.12: Dashboard-Update und status.md

Beide (`reports/index.html`, `status.md`) aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben.

- `04-01-positionierungs-analyse` in `schritte_done` (Phase B abgeschlossen)
- Aus `blockiert` entfernen
- Reports-Liste um den neuen positionierung-Report ergänzen
- Stat-Strip aktualisieren
- `naechster_empfohlen`:
  - Wenn weitere Synthese-Skills offen: `04-02-kanal-chancen-analyse` (nutzt Positionierung als strategisches Fundament)
  - Wenn Forecast-Reihe als nächstes: `04-03-ziele-aus-potenzialen`

### Schritt B.13: Standard-Schlussformat im Chat

```
✓ 04-01-positionierungs-analyse Phase B abgeschlossen.

Outputs (auf Drive):
- synthese/positionierung.md — 2D-Mapping mit Markt-Cluster, White-Space, Bewegungs-Empfehlung
- synthese/positionierungs-mapping.svg — ausgelagerte 2D-Mapping-Grafik (vom Report referenziert)
- synthese/positionierung-mapping.csv — Akteur × Achsen-Werte (für reproduzierbare Visualisierung)
- reports/X-positionierung.html — SVG-2D-Mapping + Strategie-Empfehlungen
Status aktualisiert in: status.md

Positionierungs-Statistik:
- Akteure im Mapping:    N
- X-Achse:               ACHSE_BESCHRIFTUNG_X
- Y-Achse:               ACHSE_BESCHRIFTUNG_Y
- Markt-Cluster:         K
- White-Space-Quadranten: W
- Kunden-Position:       (x, y) im Quadrant Qn

[Top 3 strategische Beobachtungen:]
⚠ Positionierungs-Insights:
1. AUFFAELLIGKEIT_1
2. AUFFAELLIGKEIT_2
3. AUFFAELLIGKEIT_3

Bewegungs-Empfehlung:
- Ist: aktueller Quadrant
- Ziel: empfohlener Quadrant
- Hebel: 3 konkrete Maßnahmen

Nächste Schritte:
1. 04-02-kanal-chancen-analyse — synthetisiert Positionierung mit den Audit-Outputs zu Kanal-Empfehlungen
2. (parallel möglich) 04-03-ziele-aus-potenzialen — leitet Bandbreiten aus Markt-Potenzialen ab

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/achsen-template.md` — Phase-A-Output-Format mit Default-Achsen-Kombinationen pro Branchen-Typ
- `reference/mapping-methodik.md` — Berechnungs-Logik pro Achsen-Typ (Tonalität direkt, USP-Differenzierung aus Token-Match, Zielgruppen-Breite, Funnel-Fokus, Cluster-Erkennungs-Algorithmus)
- `reference/positionierung-output-schema.md` — Phase-B-Output-Schema (Markdown-Frontmatter, CSV-Spalten, SVG-Konstruktion)

## Edge Cases

- **Weniger als 3 Akteure** (Kunde + 1 WB) → Mapping ist nicht aussagekräftig. Skill bricht in Phase A ab mit Hinweis, mehr WB-Profile zu erstellen.

- **Alle Tonalitäts-Werte sind `null`** (Marken-Profile haben keine Belege) → Default-Achsen nicht nutzbar. Phase A schlägt automatisch abgeleitete Achsen vor (Hero-Test, USP-Diff, Zielgruppen-Breite). Hinweis im Schema, dass Marken-Profile nachgebessert werden sollten.

- **Kunde und WBs sind sehr ähnlich (alle in einem Cluster)** → Auffälligkeit `tonale_homogenitaet_branche`. Bewegungs-Empfehlung priorisiert Achsen-Wechsel über Achsen-Position-Verschiebung.

- **Stratege wünscht 3D-Mapping** → Skill unterstützt aktuell nur 2D. Hinweis im Schema, dass für 3D zwei 2D-Mappings empfohlen werden (z. B. Achsen 1+2 und Achsen 3+4).

- **Best-Practice-WBs verzerren das Mapping** (sie sind aus anderer Region/Branche und liegen weit ab) → Stratege kann in Phase A einzelne WBs aus dem Mapping entfernen. Default ist: alle empfohlenen + Best-Practice rein.

- **Stratege wünscht Re-Run mit anderen Achsen** → Override-Argument "Achsen wechseln" → Skill löscht (mit Backup) den existierenden Phase-B-Output, lässt das Schema auf `status: vorgeschlagen` zurückfallen und bricht ab. Stratege editiert Achsen-Wahl, bestätigt, Skill läuft Phase B neu.

- **Funnel-Fokus-Achse gewählt, aber SEO-Cluster-CSV fehlt** → Phase B bricht mit Hinweis ab. Stratege muss entweder `03-03-seo-keyword-kategorisierung` laufen lassen oder andere Y-Achse wählen.

- **Konfidenz-Verteilung schlecht** (>30% der Akteure mit `konfidenz_niedrig` auf einer Achse) → Auffälligkeit `konfidenz_unsicher` mit Hinweis, dass das Mapping nur grob ist und im Strategen-Gespräch entsprechend kommuniziert werden sollte.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B läuft niemals ohne `status: bestaetigt` in Phase-A-Output
- Outputs leben auf Google Drive in `synthese/` und `reports/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für reproduzierbare Roh-Daten
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (aus Drive lesen, patchen, upsert)
- HTML-Report aus `reports/_shell.html` (aus Drive geladen)
- **Output-Reihenfolge** (`contracts.md` Abschnitt 3): zuerst alle inhaltlichen Outputs (`positionierung.md`, `positionierungs-mapping.svg`, `positionierung-mapping.csv`), dann der HTML-Report, **zuletzt** `status.md` — ein vorzeitig beendeter Lauf hinterlässt so vollständige Outputs
- **2D-Mapping als eigene SVG-Datei** (`synthese/positionierungs-mapping.svg`) — der HTML-Report bindet sie ein, rendert das Grid nicht selbst neu (verhindert 600-s-Stall im Report-Render-Schritt)
- **SVG, keine externen JS-Libs** — SVG-Datei und Report müssen offline und in Google Drive Preview funktionieren
- **Achsen-Wahl ist Strategen-Entscheidung** — Skill schlägt vor und begründet, aber der Stratege wählt im Schema-Review (Drive-Web-Editor)
