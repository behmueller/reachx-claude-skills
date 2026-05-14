# Positionierungs-Output-Schema (Phase-B-Outputs)

Definiert das Format der drei Phase-B-Outputs: `synthese/positionierung.md`, `synthese/positionierung-mapping.csv` und `reports/X-positionierung.html` (SVG-Konstruktion).

## 1. `synthese/positionierung.md` — Aggregat-Markdown

### Frontmatter

```yaml
---
skill: 04-01-positionierungs-analyse
generiert_am: ISO-8601
schema_version: "1.0"
basis_schema: synthese/positionierung-schema.md

# Achsen-Definition
x_achse:
  label: "formell ↔ informell"
  pol_negativ: formell
  pol_positiv: informell
  quelle_feld: tonalitaet.formell_vs_informell.achse_wert
y_achse:
  label: "expertise ↔ partnerschaftlich"
  pol_negativ: expertise-zentriert
  pol_positiv: partnerschaftlich
  quelle_feld: tonalitaet.expertise_vs_partnerschaftlich.achse_wert

# Akteurs-Statistik
akteure_im_mapping: 7
akteure_typ_verteilung:
  kunde: 1
  wb_zu_profilieren: 4
  wb_best_practice: 2

# Kunden-Position
kunde_position:
  x: -1.5
  y: -1.0
  konfidenz_x: hoch
  konfidenz_y: hoch
  quadrant: Q3
  quadrant_label: "formell + expertise"

# Cluster
markt_cluster_anzahl: 2
markt_cluster:
  - id: cluster_1
    label: "B2B-Expertise-Cluster"
    akteure: [WB_1_SLUG, WB_2_SLUG, KUNDE_SLUG]
    mittelpunkt: [-1.3, -0.8]
    enthaelt_kunde: true
  - id: cluster_2
    label: "Best-Practice-Cluster"
    akteure: [BP_1_SLUG, BP_2_SLUG]
    mittelpunkt: [1.2, 1.5]
    enthaelt_kunde: false

# White-Space
whitespace_quadranten:
  - quadrant: Q2
    label: "formell + partnerschaftlich"
    akteure_anzahl: 0
    strategische_relevanz: niedrig
  - quadrant: Q1
    label: "informell + partnerschaftlich"
    akteure_anzahl: 1
    enthaelt_nur: BP_2_SLUG
    strategische_relevanz: hoch
    empfohlen: true

# Bewegungs-Empfehlung
bewegungs_empfehlung:
  ist_position: [-1.5, -1.0]
  ziel_position: [0.5, 1.0]
  bewegungs_distanz: 2.83
  bewegungs_richtung: "nach rechts oben - hin zu partnerschaftlich + informell"
  aufwand_grob: mittel

# Auffälligkeiten
auffaelligkeiten_anzahl: 6
auffaelligkeiten_typen:
  - kunde_in_dichtem_cluster
  - markt_cluster_dominant
  - whitespace_strategie_relevant
  - tonale_homogenitaet_branche
  - kunde_position_widerspruechlich
  - keine_wb_im_premium_segment

# Konfidenz-Summary
konfidenz_summary:
  akteure_hoch_konfidenz: 5
  akteure_mittel_konfidenz: 1
  akteure_niedrig_konfidenz: 1
  niedrig_konfidenz_pflicht_hinweis: false
---
```

### Body-Struktur

```markdown
# Positionierungs-Analyse: KUNDE_NAME

## Übersicht

3-5 Sätze: wo steht der Kunde, was differenziert ihn, wo ist Bewegungs-Spielraum.

## 2D-Mapping

Achsen:
- X-Achse: formell ↔ informell
- Y-Achse: expertise ↔ partnerschaftlich

| Akteur | Typ | X | Y | Quadrant | Cluster |
|---|---|---|---|---|---|
| KUNDE | Kunde | -1.5 | -1.0 | Q3 | cluster_1 |
| WB_1 | WB zu profilieren | -1.0 | -0.5 | Q3 | cluster_1 |
| WB_2 | WB zu profilieren | -1.5 | -0.5 | Q3 | cluster_1 |
| WB_3 | WB zu profilieren | -0.5 | -1.5 | Q3 | - |
| WB_4 | WB zu profilieren | -1.0 | 1.0 | Q2 | - |
| BP_1 | Best-Practice | 1.0 | 1.5 | Q1 | cluster_2 |
| BP_2 | Best-Practice | 1.5 | 1.0 | Q1 | cluster_2 |

## Markt-Cluster

### Cluster 1: B2B-Expertise-Cluster

- Akteure: KUNDE, WB_1, WB_2
- Mittelpunkt: (-1.3, -0.8)
- Charakter: Tradition-zentrierter B2B-Auftritt, formelle Anrede, Awards und Top-Listen prominent

### Cluster 2: Best-Practice-Cluster

- Akteure: BP_1, BP_2
- Mittelpunkt: (1.2, 1.5)
- Charakter: Branchen-Best-Practice mit informeller Tonalität und kunden-zentrierter Story

## White-Space-Analyse

| Quadrant | Akteure | Strategische Relevanz |
|---|---|---|
| Q1 (informell + partnerschaftlich) | 2 (Best-Practice) | Hoch - empfohlene Bewegungs-Richtung |
| Q2 (formell + partnerschaftlich) | 1 (WB_4) | Mittel - alternativer White-Space |
| Q3 (formell + expertise) | 4 (Kunde + 3 WBs) | Niedrig - Markt-Default |
| Q4 (informell + expertise) | 0 | Niedrig - wenig relevant fuer Branche |

## Bewegungs-Empfehlung

Ist-Position: (-1.5, -1.0) im Quadrant Q3 (formell + expertise)
Ziel-Position: (0.5, 1.0) im Quadrant Q1 (informell + partnerschaftlich)
Bewegungs-Distanz: 2.83 (Aufwand mittel)

Konkrete Hebel:
1. HEBEL_1 (z. B. Tonalitäts-Shift in Hero-Headline)
2. HEBEL_2
3. HEBEL_3

## Auffälligkeiten

### kunde_in_dichtem_cluster (hoch-relevant)

Kunde teilt Position mit WB_1 und WB_2 im Quadrant Q3 - drei Akteure auf nahezu identischer Position.

### markt_cluster_dominant (hoch-relevant)

(siehe Methodik)

### whitespace_strategie_relevant (hoch-relevant)

Quadrant Q1 enthält nur Best-Practice-WBs aus anderen Regionen - im Wettbewerbsumfeld leer.

### tonale_homogenitaet_branche (mittel-relevant)

5 von 7 Akteuren in Quadranten Q3 und Q4 (rechts-unten und links-unten).

### kunde_position_widerspruechlich (mittel-relevant)

Briefing beschreibt Kunde als 'partnerschaftlich', Website rangiert mit Y=-1.0 stark expertise-zentriert.

### keine_wb_im_premium_segment (informativ)

Nur relevant wenn USP-Differenzierungs-Achse aktiv.

## Vorbereitung für Folge-Skills

- `04-02-kanal-chancen-analyse`: White-Space Q1 + Bewegungs-Hebel = Argumente für Content/Social-Kanäle die partnerschaftliche Tonalität tragen
- `05-01-mta-slide-bausteine`: Mapping-SVG ist Schlüssel-Visualisierung der Strategie-Sektion
- `04-05-90-tage-plan`: Hebel-Liste als Roh-Material für Maßnahmen-Plan
```

## 2. `synthese/positionierung-mapping.csv`

### Spalten

```
akteur_slug         (string, eindeutig)
akteur_typ          (kunde | wb_zu_profilieren | wb_best_practice)
akteur_name         (string, Display-Name)
x_wert              (float, -2.0 bis +2.0)
y_wert              (float, -2.0 bis +2.0)
konfidenz_x         (hoch | mittel | niedrig)
konfidenz_y         (hoch | mittel | niedrig)
quadrant            (Q1 | Q2 | Q3 | Q4)
quadrant_label      (string, z. B. "informell + partnerschaftlich")
cluster_id          (string oder leer)
cluster_groesse     (int oder leer)
hero_test_score     (float, aus Marken-Profil)
verstaendlichkeit_score (float, aus Marken-Profil)
quelle_x_feld       (string, welches Marken-Profil-Feld die X-Achse speist)
quelle_y_feld       (string, welches Marken-Profil-Feld die Y-Achse speist)
datenstand_iso      (ISO-8601)
```

### Validierungs-Regeln

- `x_wert` und `y_wert` zwingend im Bereich [-2.0, +2.0]
- `konfidenz_x` und `konfidenz_y` sind Pflichtfelder
- `akteur_slug` muss eindeutig sein (kein Akteur doppelt im Mapping)
- Kunde ist genau einmal in der CSV vorhanden

## 3. HTML-Report — SVG-Konstruktion

### Grundlayout des Reports

Aus `reports/_shell.html` mit folgenden Sektionen:

1. Stat-Strip oben: 4 Stats (Akteure, Cluster, White-Space-Quadranten, Auffälligkeiten)
2. Sticky-TOC: Mapping, Markt-Cluster, White-Space, Bewegungs-Empfehlung, Auffälligkeiten
3. Mapping-Sektion mit Inline-SVG (Hauptsektion)
4. Cluster-Sektion mit `details.skill`-Karten
5. White-Space-Sektion als 2×2-Grid
6. Bewegungs-Empfehlung als `.suggestion`-Block prominent
7. Auffälligkeiten-Block mit Badges

### Inline-SVG Spezifikation

```html
<svg viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg" class="positionierung-svg">
  <!-- Hintergrund / Quadranten-Tinting -->
  <rect x="0" y="0" width="400" height="400" fill="#f5f5f5" />              <!-- Q2 -->
  <rect x="400" y="0" width="400" height="400" fill="#fdf3ef" />            <!-- Q1 White-Space empfohlen: heller Sunrise-Tint -->
  <rect x="0" y="400" width="400" height="400" fill="#f5f5f5" />            <!-- Q3 -->
  <rect x="400" y="400" width="400" height="400" fill="#f5f5f5" />          <!-- Q4 -->

  <!-- Grid-Linien (jede Skala-Einheit) -->
  <g stroke="#e0e0e0" stroke-width="1">
    <!-- Vertikale Linien bei x = -2, -1, 0, +1, +2 (in SVG-Koordinaten: 0, 200, 400, 600, 800) -->
    <line x1="0" y1="0" x2="0" y2="800" />
    <line x1="200" y1="0" x2="200" y2="800" />
    <line x1="400" y1="0" x2="400" y2="800" stroke="#000a14" stroke-width="2"/>  <!-- Hauptachse Y -->
    <line x1="600" y1="0" x2="600" y2="800" />
    <line x1="800" y1="0" x2="800" y2="800" />
    <!-- Horizontale Linien analog -->
    <line x1="0" y1="0" x2="800" y2="0" />
    <line x1="0" y1="200" x2="800" y2="200" />
    <line x1="0" y1="400" x2="800" y2="400" stroke="#000a14" stroke-width="2"/>  <!-- Hauptachse X -->
    <line x1="0" y1="600" x2="800" y2="600" />
    <line x1="0" y1="800" x2="800" y2="800" />
  </g>

  <!-- Achsen-Beschriftung -->
  <text x="400" y="820" text-anchor="middle" font-family="Red Hat Text, sans-serif" font-size="14" fill="#000a14">X_ACHSE_LABEL</text>
  <text x="-20" y="400" text-anchor="middle" font-family="Red Hat Text, sans-serif" font-size="14" fill="#000a14" transform="rotate(-90 -20 400)">Y_ACHSE_LABEL</text>

  <!-- Pol-Labels (-2, +2 als Endpunkte) -->
  <text x="10" y="395" font-size="11" fill="#7a8a99">POL_NEG_X</text>
  <text x="790" y="395" text-anchor="end" font-size="11" fill="#7a8a99">POL_POS_X</text>
  <text x="405" y="15" font-size="11" fill="#7a8a99">POL_POS_Y</text>
  <text x="405" y="795" font-size="11" fill="#7a8a99">POL_NEG_Y</text>

  <!-- Cluster-Polygone (gestrichelt) -->
  <polygon points="..." fill="none" stroke="#7a8a99" stroke-width="2" stroke-dasharray="6,4" />
  <text x="..." y="..." font-size="12" fill="#7a8a99">CLUSTER_LABEL</text>

  <!-- Akteurs-Punkte -->
  <!-- Kunde: roter Punkt -->
  <circle cx="100" cy="500" r="14" fill="#ec644a" stroke="#000a14" stroke-width="2"/>
  <text x="120" y="505" font-family="Red Hat Display, sans-serif" font-size="13" font-weight="600" fill="#000a14">KUNDE_NAME</text>

  <!-- WB zu profilieren: dunkler Punkt -->
  <circle cx="200" cy="500" r="10" fill="#000a14" />
  <text x="215" y="505" font-size="12" fill="#000a14">WB_NAME</text>

  <!-- WB Best-Practice: grauer Punkt -->
  <circle cx="600" cy="200" r="10" fill="#7a8a99" />
  <text x="615" y="205" font-size="12" fill="#7a8a99">BP_NAME</text>

  <!-- Bewegungs-Pfeil (Kunde Ist-Position zu Ziel-Position) -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#ec644a" />
    </marker>
  </defs>
  <line x1="100" y1="500" x2="500" y2="200" stroke="#ec644a" stroke-width="2" stroke-dasharray="4,4" marker-end="url(#arrowhead)" opacity="0.7"/>
  <text x="300" y="340" font-size="11" fill="#ec644a" font-style="italic">Empfohlene Bewegung</text>
</svg>
```

### Koordinaten-Transformation

```
Mapping-Koordinaten (-2.0 bis +2.0) → SVG-Koordinaten (0 bis 800):
svg_x = (mapping_x + 2.0) * 200
svg_y = 800 - (mapping_y + 2.0) * 200    # Y invertiert weil SVG-Y nach unten zeigt

Beispiel:
mapping (0, 0) → svg (400, 400)  (Zentrum)
mapping (-2, -2) → svg (0, 800)  (links unten in SVG-Sicht = unten links im Mapping)
mapping (+2, +2) → svg (800, 0)  (rechts oben)
```

### Punkt-Größe pro Akteur

Basierend auf Marken-Stärke:

```
groesse = 10 + (hero_test_gesamt_score / 5) * 6
# hero_test 1 → Radius 11
# hero_test 5 → Radius 16
# Kunde: zusätzlich +2 (immer prominenter)
```

### Cluster-Polygon-Konstruktion

Pro Cluster: konvexe Hülle aller Cluster-Akteurs-Punkte mit Padding 20px. Bei nur 2 Akteuren: Linie mit 30px-Buffer als Ellipse.

```
fuer cluster mit >= 3 akteuren:
    polygon-punkte = konvexe huelle (graham scan) der akteurs-svg-koordinaten, mit padding 20px nach aussen

fuer cluster mit 2 akteuren:
    ellipse mit zentrum = mittelpunkt, achsen entlang verbindungslinie, padding 30px

cluster-label-position: zentrum oder oberhalb des polygons, Schriftfarbe #7a8a99
```

### REACHX-Farb-Konventionen

- Kunde: `#ec644a` (Sunrise-Red)
- WB zu profilieren: `#000a14` (Night-Sky)
- WB Best-Practice: `#7a8a99` (Mid-Gray)
- Cluster-Polygon Stroke: `#7a8a99` mit `stroke-dasharray: 6,4`
- White-Space-empfohlen-Quadrant Hintergrund: `#fdf3ef` (heller Sunrise-Tint)
- Andere Quadranten Hintergrund: `#f5f5f5` (neutral hell)
- Bewegungs-Pfeil: `#ec644a` mit `stroke-dasharray: 4,4`

### Legende rechts neben dem SVG

```html
<div class="mapping-legende">
  <div><span class="dot kunde"></span>Kunde</div>
  <div><span class="dot wb"></span>Wettbewerber</div>
  <div><span class="dot bp"></span>Best-Practice</div>
  <div><span class="cluster-symbol"></span>Markt-Cluster</div>
  <div><span class="arrow-symbol"></span>Empfohlene Bewegung</div>
</div>
```

### Pflicht-Constraints für die SVG-Konstruktion

- **Keine externen Libs** — nur Inline-SVG, kein JS, kein externes CSS
- **Skalierbar** — `viewBox` setzen, damit der Report responsiv ist
- **Font-Fallback** — `Red Hat Display`/`Red Hat Text` referenzieren, aber generic Fallback `sans-serif` mitgeben
- **Druckfähig** — keine Animation, keine Hover-States (Report soll auch als PDF taugen)
- **Akteurs-Label-Kollisionen** — wenn zwei Punkte sehr nah sind, Labels mit Offset versetzen oder mit `text-anchor`-Wechsel arbeiten

## 4. Hebel-Mapping-Tabellen (für Bewegungs-Empfehlung)

Pro Achsen-Bewegung typische konkrete Hebel:

### Achsen-Bewegung "formell → informell" (X positiv)

- Sie-Anrede zu Du-Anrede wechseln (oder gemischt)
- Hero-Headline von Statement zu Frage oder Direkt-Anrede
- Längere Sätze auflösen in kürzere, prägnante
- Fachjargon reduzieren oder erklären
- Anekdoten/persönliche Beispiele in Content einbauen

### Achsen-Bewegung "expertise → partnerschaftlich" (Y positiv)

- Hero von "Wir sind führend" zu "Lass uns gemeinsam herausfinden"
- Awards-Sektion aus Hero-Bereich entfernen, weiter unten platzieren
- Marke als Guide für den Kunden-Helden positionieren (Story-Position-Shift)
- "Wir mit Daten"-Sprache zu "Sie mit unserem Support"-Sprache
- Case-Studies in den Vordergrund, in denen der Kunde der Held ist

### Achsen-Bewegung "sachlich → emotional" (X positiv, Achse 3)

- Funktionale Bilder durch emotionale ersetzen
- Adjektive von messbar zu wertend (in Maßen, Konsistenz wichtig)
- Anwendungsgeschichten statt Feature-Listen
- Stimmungsbilder im Hero, nicht Produkt-Renderings

### Achsen-Bewegung "modern → traditionell" oder umgekehrt (Achse 4)

- modern: Buzz-Wörter aktualisieren, Trends aufgreifen, visueller Minimalismus
- traditionell: Erbe und Geschichte prominent, Beständigkeits-Sprache, klassisches Visual

### Achsen-Bewegung "spezialist → generalist" oder umgekehrt

- spezialist: Portfolio reduzieren, Top-Nische schärfen, "Wir machen nur ..."-Statements
- generalist: Portfolio aufbreiten, mehr Personas adressieren, "Alles aus einer Hand"-Story

Diese Hebel-Listen werden je nach gewähltem Bewegungs-Vektor in der `bewegungs_empfehlung.hebel_konkret` ausgegeben. Stratege wählt die 2-4 stärksten Hebel im Kunden-Gespräch aus.
