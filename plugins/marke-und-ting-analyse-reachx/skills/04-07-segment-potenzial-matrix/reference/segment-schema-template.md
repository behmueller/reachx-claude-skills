# Schema-Template für `synthese/segment-potenzial-matrix-schema.md`

Format des Phase-A-Outputs. Der Skill schreibt diese Datei mit `status: vorgeschlagen`, der Stratege reviewt die Segment-Definition und das Bewertungs-Raster und setzt `status: bestaetigt`, dann läuft Phase B.

Phase A ist der **Kern des Schema-vor-Lauf-Patterns** für diesen Skill: Die Segmentierung ist kundenspezifisch und lässt sich nicht generisch raten. Der Stratege muss bestätigen, dass die Segmente trennscharf, vollständig und entlang der richtigen Achse geschnitten sind, bevor gerechnet wird.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 04-07-segment-potenzial-matrix
phase: A
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"
status: vorgeschlagen   # vorgeschlagen | bestaetigt

# === Basis (was wurde gelesen) ===
basis_inputs:
  - datei: synthese/forecast.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: synthese/kanal-chancen.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: data/briefing.md
    generiert_am: ISO_8601_TIMESTAMP
  - datei: data/kunde.md            # null wenn nicht vorhanden
    generiert_am: ISO_8601_TIMESTAMP
  - datei: synthese/positionierung.md   # null wenn nicht vorhanden
    generiert_am: ISO_8601_TIMESTAMP

# === Kunden-Datendateien (Umsatz-/Auftrags-/Kundenzahlen) ===
# Aus data/ und input/ gesucht. Leere Liste, wenn keine vorliegt.
kunden_datenquellen:
  - datei: input/umsatz-2025.csv
    inhalt: "Umsatz pro Leistungslinie 2025"
    nutzbar_fuer: [segmentgroesse, ist_position]
  # leer => Segmentgroessen und Einzugsgebiet in Phase B als schaetzung_skill

# === Branchen-Kontext (aus forecast.md / kanal-chancen.md) ===
branchen_typ: BRANCHEN_SLUG
branchen_typ_konfidenz: hoch

# === Forecast-Anker (Leit-Zahlen, gegen die die Segment-Summe geprueft wird) ===
forecast_anker:
  aggregat_12_monate_umsatz_real_eur: 320000
  aggregat_12_monate_umsatz_worst_eur: 180000
  aggregat_12_monate_umsatz_best_eur: 580000
  doppelzaehlung_faktor: 0.85
  quelle: synthese/forecast.md

# === Segmentierungs-Achse ===
segmentierungs_achse: leistungsart   # leistungsart | zielgruppe | region
segmentierungs_achse_begruendung: >
  Der Kunde bietet drei klar abgrenzbare Leistungslinien mit deutlich
  unterschiedlicher Marge und Liefer-Kapazitaet — die Leistungsart ist die
  Achse mit den groessten Unterschieden in Erreichbarkeit und Engpass-Lage.
einzelsegment_warnung: false   # true, wenn nur ein kohaerentes Segment erkennbar

# === Segment-Definition (2-4 Segmente) ===
segmente:
  - segment_slug: privat-sanierung
    anzeigename: Privatkunden-Sanierung
    kurzbeschreibung: "Sanierungs- und Modernisierungsauftraege fuer Privathaushalte"
    abgrenzung: >
      Enthaelt: Einzelauftraege Privathaushalte bis ~50k Auftragswert.
      Nicht enthalten: Gewerbe-Neubau, Wartungsvertraege.
    briefing_belege:
      - "Briefing-Body Z. 14 — 'Kerngeschaeft sind private Sanierungen'"
    geschaetzter_umsatzanteil_heute:
      wert_prozent: 60
      quelle: schaetzung_skill   # erhoben wenn aus kunden_datenquellen belegt
    kapazitaets_hinweise_briefing:
      - "Briefing-Body Z. 31 — 'Monteure sind ausgelastet, Wartezeit 6 Wochen'"

  - segment_slug: gewerbe-neubau
    anzeigename: Gewerbe-Neubau
    kurzbeschreibung: "Projektgeschaeft fuer gewerbliche Neubauten"
    abgrenzung: "Enthaelt: Ausschreibungs-/Projektgeschaeft Gewerbe. Nicht: Privat."
    briefing_belege:
      - "Briefing-Body Z. 18"
    geschaetzter_umsatzanteil_heute:
      wert_prozent: 30
      quelle: schaetzung_skill
    kapazitaets_hinweise_briefing: []

  - segment_slug: wartungsvertraege
    anzeigename: Wartungsvertraege
    kurzbeschreibung: "Wiederkehrende Wartungs- und Service-Vertraege"
    abgrenzung: "Enthaelt: laufende Vertraege. Nicht: Einzelauftraege."
    briefing_belege:
      - "Briefing-Body Z. 22"
    geschaetzter_umsatzanteil_heute:
      wert_prozent: 10
      quelle: schaetzung_skill
    kapazitaets_hinweise_briefing: []

# === Bewertungs-Raster ===
bewertungs_raster:
  # Vier Matrix-Achsen, jeweils 0-100
  matrix_achsen:
    - achse: potenzial
      richtung: hoch_ist_gut
      beschreibung: "Marktpotenzial des Segments, gemappt relativ zum groessten Segment"
    - achse: aufwand
      richtung: invertiert     # hoch = niedriger Aufwand
      beschreibung: "Setup- + laufender Aufwand der Segment-Erschliessung"
    - achse: erreichbarkeit
      richtung: hoch_ist_gut
      beschreibung: "Ist das Segment mit Marketing real adressierbar?"
    - achse: time_to_impact
      richtung: invertiert     # hoch = schnelle Wirkung
      beschreibung: "Wie schnell wirkt Marketing-Invest im Segment?"
  # Gewichtung fuer prioritaet_score (Summe = 1.0)
  gewichtung:
    potenzial: 0.35
    aufwand: 0.20
    erreichbarkeit: 0.30
    time_to_impact: 0.15
  gewichtung_quelle: default   # default | branchen_override | stratege_override
  # Bandbreiten-Set: jeder quantitative Wert in drei Szenarien
  bandbreiten_set: [konservativ, realistisch, ambitioniert]
  # Engpass-Kandidaten, die pro Segment geprueft werden
  engpass_kandidaten:
    - marketing_potenzial
    - liefer_kapazitaet
    - personal_kapazitaet
    - vertriebs_kapazitaet
    - onboarding_service

# === Branchen-Default-Referenzwerte (aus segment-raster-defaults.md) ===
branchen_defaults:
  conversion_bandbreite:
    konservativ: 0.010
    realistisch: 0.020
    ambitioniert: 0.040
    quelle: branchen_benchmark
  time_to_impact_monate:
    konservativ: 9
    realistisch: 6
    ambitioniert: 3
    quelle: branchen_benchmark

# === Auffaelligkeits-Trigger (transparent fuer Strategen) ===
auffaelligkeits_trigger:
  segment_summe_vs_forecast_diskrepanz_prozent: 20
  segment_zu_klein_potenzialanteil_prozent: 8
  mengen_vs_umsetzung_divergenz_raenge: 1
---

# Segment-Potenzial-Matrix — Schema: KUNDENNAME

## Status

`status: vorgeschlagen` — Pflicht-Review durch den Strategen vor Phase B.

## Einordnung

Dieser Skill ist eine **ergänzende Zweitsynthese** zur kanal-zentrierten Synthese
(`kanal-chancen.md`, `forecast.md`). Er ersetzt sie nicht — er fügt die
Segment-Sicht hinzu. Phase B mappt das Forecast-Potenzial auf die unten
definierten Segmente und prüft pro Segment Erreichbarkeit und Engpass.

## Übersicht

3-5 Sätze: Segmentierungs-Achse und warum, Anzahl Segmente, ob Kunden-Datendateien
vorlagen, Forecast-Anker-Zahl.

## Segment-Definition

Pro Segment ein Block: Anzeigename, Kurzbeschreibung, Abgrenzung (was rein/raus),
Briefing-Belege, geschätzter Umsatzanteil heute mit Quellen-Typ.

## Bewertungs-Raster

Erklärung der vier Matrix-Achsen, der Gewichtung und der Engpass-Kandidaten.

## Pflicht-Review-Sektion

**Bitte prüfen vor `status: bestaetigt`:**

1. **Segmentierungs-Achse**: Ist `leistungsart` / `zielgruppe` / `region` die
   richtige Achse? Zeigt sie die größten Unterschiede in Marge/Nachfrage/Erreichbarkeit?
2. **Trennschärfe**: Überlappen die Segmente? Ist jeder Umsatz-Euro genau einem
   Segment zuordenbar?
3. **Vollständigkeit**: Decken die Segmente das gesamte Kunden-Geschäft ab, oder
   fehlt ein relevanter Teil?
4. **Anzahl**: 2-4 Segmente — bei mehr als 4 wurde gebündelt; passt die Bündelung?
5. **Engpass-Kandidaten**: Sind die zu prüfenden limitierenden Faktoren pro Segment
   realistisch? Fehlt ein kunden-spezifischer Engpass-Typ?
6. **Gewichtung**: Default 0,35 / 0,20 / 0,30 / 0,15 — `erreichbarkeit` bewusst
   hoch. Bei sehr beziehungs-getriebenem Geschäft `erreichbarkeit` weiter erhöhen.
7. **Umsatzanteile heute**: Wenn als `schaetzung_skill` markiert — kann der Stratege
   sie aus Kunden-Wissen korrigieren?

Nach Review: `status: bestaetigt` im Frontmatter setzen, dann läuft Phase B.

## Folge-Aktion

```bash
# Stratege bestaetigt:
sed -i '' 's/status: vorgeschlagen/status: bestaetigt/' synthese/segment-potenzial-matrix-schema.md
# Dann erneut 04-07-segment-potenzial-matrix aufrufen — Phase B laeuft automatisch.
```
```

## Validierungs-Regeln für Phase B

Vor der Berechnung prüft der Skill:

1. `status: bestaetigt` im Frontmatter
2. 2-4 Einträge in `segmente[]`, jeder mit `segment_slug`, `anzeigename`, `abgrenzung`
3. Genau ein Wert in `segmentierungs_achse` (`leistungsart` | `zielgruppe` | `region`)
4. `bewertungs_raster.matrix_achsen` enthält genau die vier Achsen `potenzial`, `aufwand`, `erreichbarkeit`, `time_to_impact`
5. `bewertungs_raster.gewichtung` summiert auf 1,0 (Toleranz ±0,01)
6. `bewertungs_raster.engpass_kandidaten` enthält mindestens `marketing_potenzial` und einen Kapazitäts-Typ
7. `forecast_anker.aggregat_12_monate_umsatz_real_eur` ist gesetzt (Leit-Zahl für den Cross-Check)
8. `branchen_defaults` mit `conversion_bandbreite` und `time_to_impact_monate` vorhanden

Bei Fehler: konkrete Fehlermeldung im Skill-Schluss-Format mit Hinweis, welches Feld zu korrigieren ist.
