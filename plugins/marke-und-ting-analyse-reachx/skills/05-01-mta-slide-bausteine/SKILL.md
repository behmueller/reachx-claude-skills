---
name: 05-01-mta-slide-bausteine
description: Generiert pro MTA-Sektion eine eigene HTML-Slide-Datei im REACHX-Branding (16:9, Red Hat Display/Text, Sunrise-Red, Night-Sky) plus Index mit Vorschau-Thumbnails. Stratege kopiert HTML-Bausteine in Google Slides oder nutzt sie als visuelle Vorlage. Pro Sektion Action-Title nach Pyramid-Principle plus Visualisierung und Stuetzpunkte. Skill prueft pro Sektion, ob Synthese- und Audit-Outputs vorhanden sind, und erzeugt Platzhalter-Slides wenn ein Vor-Skill fehlt. Nutze diesen Skill IMMER, wenn im MTA-Kontext Slide-Bausteine, HTML-Folien oder eine Slide-Vorlage erzeugt werden sollen - auch bei Phrasen wie "Slide-Bausteine bauen", "MTA-Slides generieren", "HTML-Folien fuer MTA", "Slide-Vorlagen erstellen", "Folien-Bausteine", "MTA-Praesentation aufbauen", "Slides aus MTA-Daten", "Drive-Slides vorbereiten". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist und mindestens ein Synthese-Output (positionierung, ziele, forecast, kanal-chancen, 90-tage-plan oder retainer) vorhanden ist.
---

# MTA-Slide-Bausteine

Finaler Synthese-Skill in Stufe 4 — vor Drive-Export. Generiert **pro MTA-Sektion eine eigene HTML-Slide** im REACHX-Branding (16:9-Verhältnis, Red Hat Display/Text, Sunrise-Red Akzente). Der Stratege kann die Slides direkt visuell prüfen, in Google Slides kopieren oder als Vorlage für die finale Präsentation nutzen.

**Architektur-Entscheidung:** HTML statt nur Markdown. Slides sind visuell — der Stratege sieht sofort Layout, Farben, Hierarchie. Pro Slide eine eigene Datei, damit der Stratege einzelne Bausteine in Google Slides kopieren kann ohne Manuell-Split.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-techniker`**-Subagent (Haiku 4.5). Reine Mechanik (Templating, HTML-Rendering, Drive-Uploads), keine inhaltliche Bewertung. Der Hauptthread orchestriert (welche Sektionen sollen gerendert werden?), der Subagent macht die Mechanik schnell und günstig.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-techniker"`
- Übergabe: MTA-Slug + Templating-Parameter
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "Slide-Bausteine bauen"
- "MTA-Slides generieren"
- "HTML-Folien fuer MTA"
- "Slide-Vorlagen erstellen"
- "Folien-Bausteine"
- "MTA-Praesentation aufbauen"
- "Slides aus MTA-Daten"
- "Drive-Slides vorbereiten"
- "Praesentations-Bausteine"
- "MTA-Story als Slides"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA im lokalen Active-MTA-Cache (`~/.cache/reachx-mta/active-mtas.json`) registriert
- `meta.json` im Drive-MTA-Folder vorhanden (Schema 2.0)
- `gws` CLI installiert und authentifiziert
- Mindestens EINER der folgenden Synthese-Outputs (im `synthese/`-Sub-Folder auf Drive):
  - `synthese/positionierung.md`
  - `synthese/ziele.md`
  - `synthese/forecast.md`
  - `synthese/kanal-chancen.md`
  - `synthese/90-tage-plan.md`
  - `synthese/retainer.md`
- Empfohlen: `data/briefing.md`, `data/kunde.md`, `wettbewerber/liste.md`, Audit-Outputs

Wenn weniger als ein Synthese-Output vorhanden ist:

```
✗ Mindestens ein Synthese-Output erforderlich.
Bitte zuerst mindestens einen Synthese-Skill laufen lassen (04-01-positionierungs-analyse, 04-03-ziele-aus-potenzialen, 04-04-forecast-modell, 04-02-kanal-chancen-analyse, 04-05-90-tage-plan oder 04-06-retainer-kalkulator).
```

## Ablauf

Kein Schema-vor-Lauf — der Skill arbeitet rein deterministisch auf Basis vorhandener Inputs. Ablauf in 6 Schritten.

### Schritt 0: MTA-Kontext laden (Standard-Pattern)

Folge `01-01-mta-projekt-init/reference/contracts.md` Abschnitt 1 für die Projekt-Auffindung. Standard-Snippet:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  echo "✗ MTA nicht registriert. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

# Sub-Folder-IDs extrahieren
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WETTBEWERBER_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
```

Wenn `meta.json` fehlt oder MTA nicht im Cache: Abbruch mit Standard-Hinweis aus `contracts.md`.

### Schritt 1: Voraussetzungs-Check auf Drive

Liste die existierenden Synthese-Outputs aus Drive — Skill bricht ab, wenn weniger als ein Synthese-Output vorhanden ist (siehe Voraussetzungen oben):

```bash
SYNTHESE_FILES=$(python3 "$DRIVE_PY" list-children "$SYNTHESE_ID" | jq -r '.[].name')
```

### Schritt 2: Sektions-Inventur

Lies `reference/sektions-katalog.md` — dort steht der vollstaendige MTA-Story-Sektionen-Katalog mit Input-Mapping pro Sektion.

Pro Sektion pruefe, ob die deklarierten Input-Files in den jeweiligen Drive-Sub-Folders vorhanden sind. Nutze `drive.py list-children "$DATA_ID"`, `list-children "$WETTBEWERBER_ID"`, `list-children "$AUDITS_ID"`, `list-children "$SYNTHESE_ID"` und matche die Dateinamen gegen die Pflicht-Inputs in der Tabelle unten:

| Sektion | Pflicht-Inputs | Optionale Inputs |
|---|---|---|
| 00-cover | `meta.json` | Logo in `assets/` |
| 01-agenda | (keine — strukturell) | — |
| 02-briefing-rekap | `data/briefing.md` | — |
| 03-marken-profil | `data/kunde.md` | `reports/02-kunde.html` (Screenshot) |
| 04-abweichungen | `data/abweichungen.md` | — |
| 05-wettbewerber-uebersicht | `wettbewerber/liste.md` (status: bestaetigt) | — |
| 06-wettbewerber-highlights | mind. 2 `wettbewerber/*.md` (nicht liste.md) | — |
| 07-positionierung | `synthese/positionierung.md` | SVG-Mapping aus dem Skill direkt einbinden |
| 08-seo-status | `audits/seo-sichtbarkeit.md` oder `seo-cluster-zusammenfassung.md` | — |
| 09-ads-status | `audits/google-ads-*.md`, `audits/meta-ads-*.md`, `audits/linkedin-ads-*.md` | — |
| 10-website-tech | `audits/website-tech-tracking.md` | — |
| 11-local-seo | `audits/gmb-local-seo.md` | (nur wenn relevant fuer Branche) |
| 12-social-status | `audits/<plattform>-*.md` (Instagram, LinkedIn, TikTok, Pinterest) | — |
| 13-kanal-chancen | `synthese/kanal-chancen.md` | — |
| 14-ziele | `synthese/ziele.md` | `data/briefing.md` fuer Briefing-Ziele |
| 15-forecast | `synthese/forecast.md` | — |
| 16-90-tage-plan | `synthese/90-tage-plan.md` | — |
| 17-retainer | `synthese/retainer.md` | — |
| 18-abschluss | (strukturell) | — |
| 19-naechste-schritte | (strukturell) | `meta.json` fuer Kontakt |

Pro Sektion das Ergebnis in einer internen Slide-Status-Liste festhalten:

- `voll` — alle Pflicht-Inputs vorhanden, Slide kann mit echten Daten gerendert werden
- `platzhalter` — Pflicht-Inputs fehlen, aber Sektion ist strukturell wichtig: Slide wird als Platzhalter mit Hinweis-Text erzeugt
- `skip` — Sektion ist branchen-irrelevant (z. B. Local-SEO ohne lokales Geschaeft) und wird im Index als ausgelassen markiert

### Schritt 3: Slides-Sub-Folder auf Drive anlegen

Auf Drive arbeiten wir nicht in `synthese/slide-bausteine/`, sondern in `reports/slides/` — alle HTML-Slide-Files landen dort als Geschwister der anderen HTML-Reports:

```bash
SLIDES_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$REPORTS_ID" "slides")
```

Wenn der Ordner schon Files enthält:

- Standardverhalten: jede Slide-HTML wird via `upsert-text` idempotent ueberschrieben (Drive macht Versionierung im Hintergrund, kein `_versions/`-Backup notwendig).
- Stratege kann explizit "neu generieren" verlangen, dann werden alle Slide-Files frisch geschrieben.

Lokal arbeiten wir in `~/.cache/reachx-mta/<slug>/slides/` (Templating-Cache), am Ende werden die fertigen HTMLs hochgeladen.

Erwartetes Layout auf Drive:

```
[Drive] reports/slides/
├── 00-cover.html
├── 01-agenda.html
├── ...
├── 19-naechste-schritte.html
└── index.html
```

Screenshots oder SVG-Visualisierungen, die in Slide-HTMLs eingebettet werden, kommen in den `assets/`-Sub-Folder oben — Slide-HTMLs referenzieren sie relativ (`../../assets/...`).

### Schritt 4: Pro Sektion eine HTML-Slide rendern

Lies `reference/slide-layouts.md` und `reference/branding-snippet.md`. Wende pro Sektion das passende Layout an:

| Sektion | Empfohlenes Layout |
|---|---|
| 00-cover, 18-abschluss, 19-naechste-schritte | `cover` / `closing` |
| 01-agenda | `transition-slide` mit numerierter Liste |
| 02-briefing-rekap | `quote-slide` (Kunden-Zitate) oder `action-title-mit-3-blocks` (Ziele/Pain/Erwartung) |
| 03-marken-profil | `action-title-mit-tabelle` (Tonalitaets-Achsen + Hero-Test) |
| 04-abweichungen | `action-title-mit-tabelle` (Briefing-Aussage vs. Website-Realitaet) |
| 05-wettbewerber-uebersicht | `action-title-mit-3-blocks` (3 Kategorien: vom Kunden genannt, regional, ueberregional) |
| 06-wettbewerber-highlights | `action-title-mit-tabelle` (Side-by-Side-Vergleich 3-5 WBs) |
| 07-positionierung | `action-title-mit-grafik` (2D-SVG-Mapping direkt aus `synthese/positionierung.md` Body kopieren) |
| 08-seo-status, 09-ads-status, 12-social-status | `action-title-mit-tabelle` (Sichtbarkeits-Vergleich) |
| 10-website-tech, 11-local-seo | `action-title-mit-3-blocks` (Top-3-Lueken/Befunde) |
| 13-kanal-chancen | `action-title-mit-3-blocks` (Top-3-Kanaele mit Score) |
| 14-ziele | `action-title-mit-tabelle` (KPI-Bandbreiten konservativ/realistisch/ambitioniert) |
| 15-forecast | `action-title-mit-grafik` (12-Monats-Linien oder Tabelle) |
| 16-90-tage-plan | `action-title-mit-grafik` (Timeline) |
| 17-retainer | `action-title-mit-3-blocks` (Paket-Varianten) |

Pro Slide:

1. **Action-Title** generieren — Aussage-Satz nach Pyramid-Principle. Beispiele:
   - GUT: "Drei Kanaele bringen 70 Prozent der erwarteten Wirkung in den ersten 12 Monaten."
   - SCHLECHT: "Kanal-Chancen-Analyse" (das ist nur ein Label, keine Aussage)
   - SCHLECHT: "Was sind die wichtigsten Kanaele?" (Fragen sind verboten)
   - Maximale Laenge: 80 Zeichen. Wenn laenger: Auffaelligkeit `slide_text_zu_lang`.

2. **Visualisierungs-Element** einbauen — Tabelle, SVG-Grafik, Drei-Block-Layout oder Quote-Block. Wenn die Sektion nur reinen Text hat: Auffaelligkeit `kein_visualisierungs_element` und Default-Layout `action-title-mit-3-blocks` mit den 3 Kernaussagen.

3. **Stuetzpunkte** — 2-4 Bullets oder kurze Saetze, die den Action-Title belegen. Aus den Input-Files extrahieren (Frontmatter-Felder bevorzugt, Body als Fallback).

4. **REACHX-Branding** strikt einhalten — Schriften, Farben, Spacing wie in `reference/branding-snippet.md` definiert.

5. **Slide-Format** — `width: 1920px; height: 1080px; aspect-ratio: 16/9;` plus `transform: scale(...)` per CSS Media Query fuer Viewport-Anpassung. Print-PDF-Friendly via `@page` und `@media print`.

Schreibe pro Sektion ein eigenes HTML-File lokal nach `~/.cache/reachx-mta/<slug>/slides/NN-slug.html` und lade es dann nach Drive hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SLIDES_ID" "NN-slug.html" "$HOME/.cache/reachx-mta/<slug>/slides/NN-slug.html" "text/html"
```

### Schritt 5: Index-File erzeugen

`reports/slides/index.html` als Uebersicht aller Slides mit Mini-Vorschauen (auf Drive im `slides/`-Sub-Folder).

Layout:

- Hero mit Titel "MTA-Slide-Bausteine — <Kunde>" und Stat-Strip (Slides voll / Slides Platzhalter / Slides Skip)
- Grid mit 4-5 Spalten, pro Slide ein Thumbnail
- Thumbnail = `<a href="NN-slug.html">` mit eingebettetem `<iframe>` (skaliert via CSS-Transform) oder mit statischem Screenshot-Placeholder
- Pro Thumbnail darunter: Slide-Nummer, Sektions-Titel, Status-Badge (`voll`, `platzhalter`, `skip`)
- Footer mit Hinweis: "In Google Slides einbetten: Datei oeffnen → Inhalt kopieren → in neue Slide einfuegen. Fuer PDF-Export: Browser-Druck-Funktion (16:9-Layout)."

REACHX-Branding (gleiche CSS-Variablen wie Slide-Bausteine).

Index hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$SLIDES_ID" "index.html" \
  "$HOME/.cache/reachx-mta/<slug>/slides/index.html" "text/html"
```

### Schritt 6: Skill-Report und Status-Update

#### 6.1: HTML-Report `reports/<nummer>-slide-bausteine-uebersicht.html`

Lies `reports/_shell.html` aus Drive (per `drive.py read <id>`). Nummer nach Workflow-Reihenfolge (vermutlich 14 bis 17, je nach welche Folge-Skills schon Reports geschrieben haben). Inhalte:

- Stat-Strip: Anzahl Slides total, davon voll/Platzhalter/Skip
- Tabelle mit allen Slides (Sektion, Pfad, Status, Action-Title, Layout)
- Auffaelligkeiten-Block (`.suggestion`) mit Hinweisen aus Schritt 4
- Link `<a href="slides/index.html">` zum Slide-Index (relativ, im selben `reports/`-Folder auf Drive)
- TOC mit Quick-Links zu den Sektionen

Hochladen via `drive.py upsert-text "$REPORTS_ID" "NN-slide-bausteine-uebersicht.html" /tmp/report.html "text/html"`.

#### 6.2: Dashboard-Update

Aktualisiere `reports/index.html` auf Drive (Read–Modify–Write via `drive.py`):

- `05-01-mta-slide-bausteine` in Erledigt-Liste
- Neuen Report-Eintrag mit Link
- Stat-Strip um "Slides: NN" ergaenzen
- Body bleibt `class="is-dashboard"`

#### 6.3: `status.md` aktualisieren

Folge `contracts.md` Abschnitt 3. Lese `status.md` aus dem MTA-Root via `drive.py` (`find_by_name(FOLDER_ID, "status.md")` → `read`), aktualisiere und schreibe via `upsert-text` zurück:

- `05-01-mta-slide-bausteine` in `schritte_done` (Frontmatter), aus `schritte_offen` entfernen
- Eigene Sektion unter "✓ Erledigt" mit Datum, Outputs, ggf. Auffaelligkeiten
- `naechster_empfohlen`: typischerweise `05-02-mta-export-to-drive` (Final-Export-ZIP) oder Stratege-Review-Schritt (manuell)

#### 6.4: Standard-Schlussformat im Chat

```
✓ 05-01-mta-slide-bausteine abgeschlossen.

Outputs (auf Drive):
- reports/slides/index.html — Slide-Uebersicht mit Vorschau
- reports/slides/00-cover.html bis 19-naechste-schritte.html — N Slide-Bausteine
- reports/NN-slide-bausteine-uebersicht.html — Skill-Report mit Statistik
Status aktualisiert in: status.md

Slide-Statistik:
- Slides total:     N
- davon voll:       V (echte Daten)
- davon Platzhalter: P (Daten fehlen, Sektion strukturell wichtig)
- davon Skip:       S (Sektion branchen-irrelevant)

[Bei Auffaelligkeiten:]
⚠ Auffaelligkeiten:
- <auffaelligkeit 1>
- <auffaelligkeit 2>

Naechste Schritte:
1. Stratege-Review der Slide-Bausteine — reports/slides/index.html im Drive-Browser-Viewer oeffnen
2. Inhalte in Google Slides uebernehmen (manueller Schritt — REACHX-Master-Slides nutzen, HTML-Inhalte einkopieren)
3. 05-02-mta-export-to-drive — Final-Export-ZIP im Kunden-Folder ablegen
4. (optional) Fehlende Synthese-Skills nachholen, dann 05-01-mta-slide-bausteine erneut laufen lassen mit Override "neu generieren"

Sag mir, welcher als naechster.
```

## Auffaelligkeiten

Der Skill prueft pro Slide folgende Bedingungen und meldet die Auffaelligkeiten im Report und im Chat-Schluss:

| Typ | Ausloeser | Bedeutung |
|---|---|---|
| `sektion_daten_fehlen` | Pflicht-Inputs fehlen, Slide wurde als Platzhalter erzeugt | Hinweis, welcher Vor-Skill laufen muss |
| `slide_text_zu_lang` | Action-Title >80 Zeichen oder Body-Bullet >120 Zeichen | Stratege muss kuerzen, sonst passt es nicht in eine Zeile |
| `kein_visualisierungs_element` | Slide hat nur Text-Bloecke, keine Tabelle/SVG/Drei-Block-Layout | Visuell schwach — Empfehlung, Visualisierung zu ergaenzen |
| `zu_viele_slides` | >25 Slides erzeugt | MTA-Praesentation wird zu lang — Stratege sollte Sektionen zusammenlegen |
| `zu_wenige_slides` | <15 Slides erzeugt | MTA wirkt duenn — viele Synthese-Skills fehlen |
| `action_title_keine_aussage` | Action-Title ist Frage oder reines Label (z. B. "Kanal-Chancen") | Title muss eine Aussage sein |
| `inputs_veraltet` | Pflicht-Input ist aelter als 30 Tage | Hinweis, dass Daten vor MTA-Praesentation aktualisiert werden sollten |

## Output-Konventionen

- **Pfade in HTML-Slides relativ** — keine absoluten Pfade, damit der Drive-Browser-Viewer die Querverweise korrekt aufloest (Index → einzelne Slides, Slides → Assets unter `../../assets/`).
- **CSS inline pro Slide** — keine externen Stylesheets; jede Slide ist self-contained und kann einzeln verschickt werden
- **REACHX-Branding strikt** — Red Hat Display fuer Headlines, Red Hat Text fuer Body, Sunrise-Red `#ec644a` fuer Akzente, Night-Sky `#000a14` fuer Text auf hellem Grund
- **16:9-Format** — `width: 1920px; height: 1080px` als Print-Format, `aspect-ratio: 16/9` fuer Bildschirm-Skalierung
- **Action-Titles im Praesens** — keine Beschreibungen, keine Fragen, sondern Aussage-Saetze nach Pyramid-Principle

## Bundled Resources

- `reference/sektions-katalog.md` — vollstaendiger MTA-Story-Sektionen-Katalog mit Input-Mapping pro Sektion und Layout-Empfehlung
- `reference/slide-layouts.md` — Layout-Templates mit HTML-Skeletten (cover, action-title-mit-tabelle, action-title-mit-grafik, action-title-mit-3-blocks, quote-slide, transition-slide, closing)
- `reference/branding-snippet.md` — CSS-Block mit REACHX-Branding fuer Slide-Bausteine (16:9-spezifisch, basiert auf Shell-CSS aber Slide-optimiert)

## Edge Cases

- **Nur 1-2 Synthese-Outputs vorhanden** — der Skill laeuft trotzdem, erzeugt aber viele Platzhalter-Slides. Im Schluss-Format wird betont, dass die MTA noch nicht praesentabel ist und welche Vor-Skills fehlen.

- **Positionierungs-SVG ist nicht in `synthese/positionierung.md` enthalten** — der Skill faellt auf eine Platzhalter-Grafik zurueck (leeres Koordinatensystem mit Achsen-Beschriftung aus dem Schema) und meldet die Auffaelligkeit.

- **Wettbewerber-Liste hat weniger als 3 bestaetigte WBs** — Sektion 06 (Highlights) wird trotzdem erzeugt, aber nur mit den verfuegbaren WBs. Auffaelligkeit, wenn unter 2.

- **Forecast oder Retainer fehlt komplett** — kritische Sektionen, daher immer Platzhalter mit explizitem Hinweis im Slide-Body ("Daten fehlen — 04-04-forecast-modell / 04-06-retainer-kalkulator zuerst laufen lassen").

- **Re-Run nach Update eines Synthese-Outputs** — Stratege kann den Skill mit Override "neu generieren" aufrufen, der Skill ueberschreibt nur die betroffenen Slide-Dateien (Diff anhand Drive-`modifiedTime` des Input-Files vs. des bestehenden Slide-Files).

- **Sehr lange Action-Titles** — wenn das Aggregat-File einen Action-Title liefert, der >80 Zeichen ist: der Skill kuerzt nicht automatisch (Inhalt waere semantisch verfaelscht), sondern uebernimmt den Title und meldet `slide_text_zu_lang`. Stratege editiert das Input-File.

- **Branche ohne lokale Komponente** — `11-local-seo` wird automatisch auf `skip` gesetzt, wenn `meta.json` keine konkrete `region` enthaelt oder wenn `audits/gmb-local-seo.md` fehlt.

- **Mehrsprachige Praesentation** — der Skill arbeitet aktuell nur in Deutsch. Eine englische Variante koennte in einer spaeteren Skill-Version ergaenzt werden.

## Wichtige Konventionen

Alle in `01-01-mta-projekt-init/reference/contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive — gelesen/geschrieben via `drive.py` (Schema 2.0)
- HTML-Reports aus `reports/_shell.html` (aus Drive)
- `status.md` und Dashboard werden in jedem Lauf aktualisiert
- Standard-Schlussformat im Chat
- REACHX-Branding strikt (Red Hat Display/Text, Sunrise-Red, Night-Sky)
- Pro Slide eine eigene HTML-Datei (nicht alle in einer Datei) — der Stratege kopiert einzeln in Google Slides
- Action-Titles nach Pyramid-Principle (Aussage-Saetze, keine Fragen, keine Beschreibungen)
