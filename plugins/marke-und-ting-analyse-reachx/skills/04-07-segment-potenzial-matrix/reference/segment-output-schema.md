# Output-Schema: Segment-Potenzial-Matrix (Phase B)

Definiert die drei Pflicht-Outputs:

- `synthese/segment-potenzial-matrix.md` — Aggregat-Markdown mit den fünf Auswertungs-Blöcken pro Segment, Gesamt-Matrix, Engpass-Analyse, Priorisierung
- `synthese/segment-potenzial-matrix.csv` — eine Zeile pro Segment × Auswertungs-Block
- `reports/<nummer>-segment-potenzial.html` — HTML-Report mit Matrix-Heatmap

---

## CSV-Schema (`synthese/segment-potenzial-matrix.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma.

Die CSV hat **eine Zeile pro Segment × Auswertungs-Block** — fünf inhaltliche Blöcke pro Segment plus eine Pflicht-`gesamt`-Zeile pro Segment mit den verdichteten Matrix-Achsen. Bei 3 Segmenten also 3 × 6 = 18 Zeilen.

### Spalten (in fester Reihenfolge)

```
segment_slug,segment_anzeigename,segmentierungs_achse,
block,
wert_konservativ,wert_realistisch,wert_ambitioniert,wert_einheit,
quelle_typ,
potenzial_score,aufwand_score,erreichbarkeit_score,time_to_impact_score,
prioritaet_score_roh,prioritaet_score_mengen,
engpass_typ,engpass_quelle,marketing_adressierbar,
rang_mengen,rang_umsetzung,
konfidenz,
zugehoerige_auffaelligkeiten,
datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `segment_slug` | string (kebab-case) | ja | z. B. `privat-sanierung` |
| `segment_anzeigename` | string | ja | Anzeigename für Excel-Lesbarkeit |
| `segmentierungs_achse` | enum | ja | `leistungsart` \| `zielgruppe` \| `region` |
| `block` | enum | ja | `marktpotenzial` \| `ist_position` \| `erreichbarkeit` \| `hebel_kanalmix` \| `aufwand` \| `gesamt` |
| `wert_konservativ` | float / leer | ja* | Block-Wert konservativ — leer bei rein qualitativen Blöcken (`hebel_kanalmix`) |
| `wert_realistisch` | float / leer | ja* | Block-Wert realistisch |
| `wert_ambitioniert` | float / leer | ja* | Block-Wert ambitioniert |
| `wert_einheit` | string | ja | z. B. `EUR_jahr`, `auftraege_jahr`, `monate`, `eur_setup`, `eur_monat`, `stunden_monat` |
| `quelle_typ` | enum | ja | `erhoben` \| `briefing` \| `benchmark` \| `schaetzung_skill` |
| `potenzial_score` | int 0-100 | ja (in `gesamt`-Zeile) | Matrix-Achse — sonst leer |
| `aufwand_score` | int 0-100 | ja (in `gesamt`-Zeile) | invertiert: hoch = niedriger Aufwand |
| `erreichbarkeit_score` | int 0-100 | ja (in `gesamt`-Zeile) | |
| `time_to_impact_score` | int 0-100 | ja (in `gesamt`-Zeile) | invertiert: hoch = schnelle Wirkung |
| `prioritaet_score_roh` | int 0-100 | ja (in `gesamt`-Zeile) | ungedeckelt |
| `prioritaet_score_mengen` | int 0-100 | ja (in `gesamt`-Zeile) | engpass-gedeckelt — steuert das Mengen-Ranking |
| `engpass_typ` | enum | ja (in `gesamt`-Zeile) | `marketing_potenzial` \| `liefer_kapazitaet` \| `personal_kapazitaet` \| `vertriebs_kapazitaet` \| `onboarding_service` \| `kein_klarer_engpass` |
| `engpass_quelle` | enum | ja (in `gesamt`-Zeile) | `erhoben` \| `briefing` \| `schaetzung_skill` |
| `marketing_adressierbar` | enum | ja (in `gesamt`-Zeile) | `ja` \| `eingeschraenkt` \| `nein` |
| `rang_mengen` | int | ja (in `gesamt`-Zeile) | Position in der Mengen-Logik (1 = höchste Priorität) |
| `rang_umsetzung` | int | ja (in `gesamt`-Zeile) | Position in der Umsetzungs-Reihenfolge |
| `konfidenz` | enum | ja | `hoch` \| `mittel` \| `niedrig` |
| `zugehoerige_auffaelligkeiten` | string | nein | Pipe-Liste der Auffälligkeits-Typen |
| `datenstand_iso` | ISO-8601 | ja | Datum des Skill-Laufs |

\* In den Block-Zeilen `marktpotenzial`, `ist_position`, `erreichbarkeit`, `aufwand` sind die `wert_*`-Spalten gefüllt; in der `hebel_kanalmix`-Zeile leer (qualitativ); in der `gesamt`-Zeile sind die Score-Spalten gefüllt.

### Sortierung

1. `segment_slug` (alphabetisch)
2. `block` in fester Reihenfolge: `marktpotenzial` → `ist_position` → `erreichbarkeit` → `hebel_kanalmix` → `aufwand` → `gesamt`

---

## Markdown-Schema (`synthese/segment-potenzial-matrix.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 04-07-segment-potenzial-matrix
phase: B
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"
status: vorgeschlagen   # vorgeschlagen bis Stratege-Review, dann bestaetigt

# === Provenienz / Staleness ===
basis_inputs:
  - datei: synthese/forecast.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: synthese/kanal-chancen.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: data/briefing.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: synthese/segment-potenzial-matrix-schema.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: data/kunde.md                # null wenn nicht vorhanden
    generiert_am: ISO_8601_TIMESTAMP
kunden_datenquellen:                    # leere Liste, wenn keine vorlagen
  - input/umsatz-2025.csv
staleness_hinweis: null                 # string, wenn ein Input neuer als ein frueherer Output ist

# === Einordnung ===
einordnung: zweitsynthese_ergaenzend_zur_kanalsicht
ersetzt_nicht:
  - synthese/kanal-chancen.md
  - synthese/forecast.md

# === Lauf-Kontext ===
branchen_typ: BRANCHEN_SLUG
segmentierungs_achse: leistungsart      # leistungsart | zielgruppe | region
modus: voll                             # voll | reduced
konfidenz_gesamt: hoch                   # hoch | mittel | niedrig

# === Forecast-Cross-Check ===
forecast_cross_check:
  forecast_aggregat_real_eur: 320000
  segment_summe_real_eur: 305000
  abweichung_prozent: 4.7
  ergebnis: konsistent                   # konsistent | diskrepanz
  kommentar: "Segment-Summe liegt innerhalb 20% des Forecast-Aggregats"

# === Gewichtung ===
gewichtung:
  potenzial: 0.35
  aufwand: 0.20
  erreichbarkeit: 0.30
  time_to_impact: 0.15
  quelle: default                        # default | branchen_override | stratege_override

# === Segmente ===
segmente:
  - segment_slug: privat-sanierung
    anzeigename: Privatkunden-Sanierung
    # Block 1
    marktpotenzial_eur:
      konservativ: 120000
      realistisch: 185000
      ambitioniert: 290000
      quelle: schaetzung_skill
    # Block 2
    ist_position_umsatz_heute_eur: 95000
    ist_position_quelle: briefing
    hebel_abstand_eur: 90000
    # Block 3
    erreichbarkeit_score: 78
    marketing_adressierbar: ja
    erreichbarkeit_begruendung: "Aktive lokale Suche, marketing-getriebener Kauf"
    # Block 4
    kanal_mix:
      - kanal_slug: local-seo
        rolle: primaer
        begruendung: "Lokale Service-Suchen tragen das Segment"
      - kanal_slug: sea
        rolle: sekundaer
        begruendung: "Sofort-Hebel fuer Anfragen"
    # Block 5
    setup_aufwand_eur:
      konservativ: 4000
      realistisch: 6500
      ambitioniert: 9000
      quelle: benchmark
    laufender_aufwand_monat:
      spend_eur_real: 1800
      stunden_real: 12
      quelle: benchmark
    time_to_impact_monate:
      konservativ: 7
      realistisch: 4
      ambitioniert: 2
      quelle: benchmark
    # Matrix-Achsen
    potenzial_score: 100
    aufwand_score: 70
    erreichbarkeit_score: 78
    time_to_impact_score: 68
    prioritaet_score_roh: 82
    prioritaet_score_mengen: 82
    # Engpass
    engpass_typ: personal_kapazitaet
    engpass_quelle: briefing
    engpass_begruendung: >
      Briefing nennt 6 Wochen Wartezeit und ausgelastete Monteure — das Wachstum
      ist personal-, nicht marketing-gedeckelt.
    engpass_empfehlung_richtung: marge_statt_menge
    # Ranking
    rang_mengen: 1
    rang_umsetzung: 2
    konfidenz: mittel
    auffaelligkeiten: [kapazitaet_ist_engpass, marge_statt_menge]
  # ... weitere Segmente

# === Priorisierung (zwei getrennte Sichten) ===
prioritaet_mengen_logik:
  - rang: 1
    segment_slug: privat-sanierung
    prioritaet_score_mengen: 82
    begruendung: "Groesstes Potenzial + hohe Erreichbarkeit"
  # ...
umsetzungs_reihenfolge:
  - rang: 1
    segment_slug: wartungsvertraege
    typ: quick_win                       # quick_win | foundation | long_term
    begruendung: >
      Schnellste Wirkung, finanziert den Kapazitaets-Aufbau fuer Privat-Sanierung.
  # ...
mengen_vs_umsetzung_divergenz: true

# === Engpass-Uebersicht ===
engpass_uebersicht:
  segmente_kapazitaets_gedeckelt: 2
  segmente_marketing_gedeckelt: 1
  haeufigster_engpass: personal_kapazitaet
  kernbefund: >
    Bei 2 von 3 Segmenten ist die Kunden-Kapazitaet der Engpass, nicht das
    Marketing — Mengen-Budget wuerde verpuffen.

# === Auffaelligkeiten (min. 6) ===
auffaelligkeiten:
  - typ: enum   # kapazitaet_ist_engpass | segment_marketing_nicht_adressierbar
                # | segment_unterbespielt | segment_zu_klein
                # | mengen_vs_umsetzung_divergenz | segment_summe_vs_forecast_diskrepanz
                # | engpass_unbestaetigt | segment_datenbasis_duenn | marge_statt_menge | sonstige
    titel: string
    beschreibung: "1-2 Saetze"
    relevanz: hoch | mittel | niedrig
    handlungs_empfehlung: "konkrete Aktion"
    betroffene_segmente: [privat-sanierung]

# === Strategische Story ===
strategische_story:
  wachstums_traeger_segment: <slug>
  engpass_kernaussage: <1-2 Saetze>
  beschreibung: <4-6 Saetze>
  einordnung_zur_kanalsicht: >
    Diese Segment-Sicht ergaenzt die Kanal-Sicht — beide zusammen ergeben das Bild.

# === Aggregat-Statistiken ===
statistiken:
  segmente_bewertet: 3
  top_prioritaet_mengen_score: 82
  segmente_niedrige_konfidenz: 1
  werte_aus_erhoben_prozent: 20.0
  werte_aus_schaetzung_skill_prozent: 45.0
---

# Segment-Potenzial-Matrix: KUNDENNAME

> **Einordnung.** Diese Analyse ist eine ergänzende Zweitsynthese zur
> kanal-zentrierten MTA-Synthese (`kanal-chancen.md`, `forecast.md`). Sie
> verteilt das Forecast-Potenzial auf die Kunden-Segmente und prüft pro Segment
> Erreichbarkeit und Engpass — sie ersetzt die Kanal-Sicht nicht.

## Übersicht

3-5 Sätze: Segmentierungs-Achse, Anzahl Segmente, Forecast-Cross-Check-Ergebnis,
Kernbefund der Engpass-Analyse.

## Gesamt-Matrix

Tabelle Segment × vier Achsen + `prioritaet_score`.

| Segment | Potenzial | Aufwand | Erreichbarkeit | Time-to-Impact | Prio (Menge) | Engpass |
|---|---|---|---|---|---|---|
| Privatkunden-Sanierung | 100 | 70 | 78 | 68 | 82 | personal_kapazitaet |
| ... | ... | ... | ... | ... | ... | ... |

## Pro Segment

### Privatkunden-Sanierung

**Block 1 — Marktpotenzial (bottom-up)**: Tabelle konservativ/realistisch/ambitioniert mit Quellen-Typ.

**Block 2 — Ist-Position**: Umsatz heute, Hebel-Abstand zum Potenzial.

**Block 3 — Erreichbarkeits-Prüfung**: `marketing_adressierbar`-Aussage + Begründung.

**Block 4 — Hebel + Kanal-Mix**: priorisierter Kanal-Mix mit Begründung pro Kanal.

**Block 5 — Aufwands-Hochrechnung**: Setup + laufender Aufwand als Bandbreite, Time-to-Impact.

**Engpass**: `engpass_typ` + Begründung + Empfehlungs-Richtung.

(... weitere Segmente in gleicher Struktur)

## Engpass- / Kapazitäts-Analyse

Pro Segment der limitierende Faktor. Prominenter Kernbefund: Wo ist die
Kunden-Kapazität der Engpass, nicht das Marketing — und was heißt das für die
Budget-Empfehlung (Marge statt Menge / Kapazität zuerst / Budget umlenken)?

## Priorisierung

### Mengen-Logik — wo lohnt sich zusätzliches Wachstums-Budget?

`top3`-Liste nach `prioritaet_score_mengen`.

### Umsetzungs-Reihenfolge — welches Segment zuerst angehen?

Separate `top3`-Liste mit Quick-Win-/Foundation-/Long-Term-Typ und Begründung.
**Beide Sichten sind bewusst getrennt** — bei Divergenz wird sie begründet.

## Strategische Story

4-6 Sätze. Schließt mit der Einordnung, dass die Segment-Sicht die Kanal-Sicht ergänzt.

## Auffälligkeiten

(aus Frontmatter, sortiert nach Relevanz — mind. 6)

### Auffälligkeit 1 — Titel

Beschreibung, Handlungs-Empfehlung, betroffene Segmente.

## Datenbasis

- Pflicht-Inputs: forecast.md, kanal-chancen.md, briefing.md (mit generiert_am-Stempeln)
- Kunden-Datendateien: Liste oder "keine — Segmentgrößen als schaetzung_skill"
- Quellen-Verteilung: X% erhoben / Y% briefing / Z% benchmark / W% schaetzung_skill
- Forecast-Cross-Check: konsistent | diskrepanz (Abweichung P%)

## Folge-Skills

- `04-05-90-tage-plan` — die Umsetzungs-Reihenfolge fließt direkt in die Phasen ein
- `05-01-mta-slide-bausteine` — Segment-Matrix als ergänzende Slide neben der Kanal-Slide
```

---

## HTML-Report-Struktur

`{{MAIN_CONTENT}}` wird **ausschließlich** aus den Bausteinen in `01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt. Reihenfolge:

### 1. Sticky-TOC

`nav.toc` mit Ankern auf die Sektionen.

### 2. Stat-Strip

`div.stat-strip` mit vier `div.stat`:

- Segmente bewertet (`num` = Anzahl, `lbl` = "Segmente")
- Segmentierungs-Achse (`num` = Achse, `lbl` = "Achse")
- Top-Priorität Menge (`num` = Segment-Name, `lbl` = "Prio Mengen-Logik")
- Kapazitäts-gedeckelt (`num` = "N von M", `lbl` = "Segmente kapazitäts-gedeckelt")

### 3. Summary-Card — Einordnung

`div.summary-card` mit `h3` "Einordnung" und dem Hinweis, dass dies eine ergänzende Zweitsynthese zur Kanal-Sicht ist. `p.note` mit Datenstand und Forecast-Cross-Check-Ergebnis.

### 4. Matrix-Heatmap

`table.data` — eine Zeile pro Segment, Spalten: Segment, Potenzial, Aufwand, Erreichbarkeit, Time-to-Impact, Prio (Menge). Die Score-Werte werden mit `span.badge` versehen: `stark` (≥ 60), `mittel` (30–59), `schwach` (< 30). Eine `tr.total`-Zeile mit dem Median je Spalte.

### 5. Pro Segment — `details.dim`

Ein `details class="dim"` pro Segment, `data-rating` nach `prioritaet_score_mengen` (`stark`/`mittel`/`schwach`). Kunde-Top-Segment mit `open`. `summary` mit `strong` Segment-Name + `span.badge` Prio-Score. Im `div.body` die fünf Auswertungs-Blöcke als `h4`-Abschnitte, Bandbreiten als `table.data`, der Engpass-Befund mit einem Status-Badge.

### 6. Engpass-Übersicht

`table.ratings` — erste Spalte Segment (rendert fett), Spalten: `engpass_typ` (als Badge), limitierender Faktor, Empfehlungs-Richtung.

### 7. Priorisierung — zwei `top3`-Listen

Zwei `ol.top3` in zwei `section`-Blöcken bzw. unter zwei `h4`:

- "Mengen-Logik" — Segmente nach `prioritaet_score_mengen`
- "Umsetzungs-Reihenfolge" — Segmente nach `rang_umsetzung`, mit Quick-Win-/Foundation-/Long-Term-Hinweis

Bei `mengen_vs_umsetzung_divergenz: true` ein `div.suggestion` davor, das die Divergenz erklärt.

### 8. Strategische Story

`div.summary-card` am Ende der Story-Sektion.

### 9. Auffälligkeiten

`div.suggestion`-Blöcke (`p.label` = "Auffälligkeit", `p` = Beschreibung), sortiert nach Relevanz.

### 10. Datenbasis-Hinweis

`table.data` — welche Inputs vorlagen, welche Kunden-Datendateien, Quellen-Verteilung. Bei Modus `reduced` zusätzlich ein `div.suggestion` oben mit dem Hinweis auf die dünne Datenbasis.

**Keine** Sparkline nötig (keine Zeitreihen). **Keine** eigenen CSS-Klassen, **kein** inline-`style`. Vor Upload mit `validate-report.py --shell` prüfen (Exit-Code 0 Pflicht).

---

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. 2-4 Segmente in `segmente[]`, jedes mit allen fünf Blöcken und allen vier Matrix-Achsen
2. Jeder quantitative Block-Wert hat drei Szenarien (`konservativ` ≤ `realistisch` ≤ `ambitioniert`, Toleranz ±1 %) und einen `quelle`-Typ
3. `prioritaet_score_roh` = gewichtete Summe der vier Achsen (Toleranz ±1 wegen Rundung)
4. `prioritaet_score_mengen` ≤ `prioritaet_score_roh` (Engpass-Deckelung nie nach oben)
5. Jedes Segment hat genau einen `engpass_typ` aus der erlaubten Liste und ein `marketing_adressierbar`
6. `prioritaet_mengen_logik` und `umsetzungs_reihenfolge` haben beide alle Segmente, jeweils eindeutige Ränge
7. `auffaelligkeiten` hat **mindestens 6 Einträge**, jede mit `typ`, `titel`, `relevanz`, `handlungs_empfehlung`, `betroffene_segmente`
8. `forecast_cross_check` ist gesetzt; bei Abweichung > 20 % ist die Auffälligkeit `segment_summe_vs_forecast_diskrepanz` vorhanden
9. CSV hat pro Segment sechs Block-Zeilen (`marktpotenzial`, `ist_position`, `erreichbarkeit`, `hebel_kanalmix`, `aufwand`, `gesamt`)
10. `segmentierungs_achse` ist einer der drei erlaubten Werte
11. `status: vorgeschlagen` im Output-Frontmatter (bis Stratege-Review)

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

---

## Wie Folge-Skills die Outputs lesen

### `04-05-90-tage-plan`

- `umsetzungs_reihenfolge[]` → die Reihenfolge der Segment-Erschließung fließt direkt in die Monats-Phasen ein
- `auffaelligkeiten` mit `typ: kapazitaet_ist_engpass` / `marge_statt_menge` → Kapazitäts-Aufbau als Voraussetzung bzw. Marge-Maßnahme im Plan
- `04-05` setzt `04-07` nicht voraus — die Segment-Sicht ist eine optionale Anreicherung

### `05-01-mta-slide-bausteine`

- Gesamt-Matrix als ergänzende Slide neben der Kanal-Chancen-Slide
- `engpass_uebersicht.kernbefund` als Story-Punkt — der ehrliche Engpass-Befund ist ein starkes MTA-Argument
- `strategische_story` als Segment-Story-Slide
