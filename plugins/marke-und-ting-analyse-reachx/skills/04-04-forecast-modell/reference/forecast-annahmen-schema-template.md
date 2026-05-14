# Schema-Template für `synthese/forecast-schema.md`

Format des Phase-A-Outputs. Der Skill schreibt diese Datei mit `status: vorgeschlagen`, der Stratege reviewt und setzt `status: bestaetigt`, dann läuft Phase B.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 04-04-forecast-modell
phase: A
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"
status: vorgeschlagen   # vorgeschlagen | bestaetigt

# === Basis (was wurde gelesen) ===
basiert_auf:
  meta_json: meta.json
  kanal_chancen_md: synthese/kanal-chancen.md
  kanal_chancen_csv: synthese/kanal-chancen.csv
  abgeleitete_ziele_md: synthese/ziele.md
  ziele_aufschluesselung_csv: synthese/ziele-aufschluesselung.csv
  ziel_annahmen_schema_md: synthese/ziel-annahmen-schema.md
  briefing: data/briefing.md       # null wenn nicht vorhanden
  kunde: data/kunde.md             # null wenn nicht vorhanden

# === Branchen-Typ und Lauf-Modus ===
branchen_typ: BRANCHEN_SLUG
branchen_typ_konfidenz: hoch
lauf_modus: abgeleitet_pur   # abgeleitet_pur | plausibilitaets_check | hybrid
lauf_modus_begruendung: "Briefing nennt keine bezifferten KPIs, Vorrang abgeleitete Ziele"

# === Kickoff-Anker fuer Monats-Labels ===
kickoff_datum: 2026-06-01    # aus meta.json, oder null
monats_label_modus: kalendermonat   # kalendermonat | sequenziell (M1..M12)

# === Dual-Quellen-KPI-Inventur ===
ziel_inventur:
  briefing_kpis_vorhanden: true
  abgeleitete_ziele_vorhanden: true
  ziel_quellen:
    - kpi: leads_pro_monat
      briefing_wert: 50
      briefing_quelle_zeile: "Briefing-Body Z. 24"
      abgeleitet_worst: 25
      abgeleitet_real: 60
      abgeleitet_best: 110
      diskrepanz_typ: passt          # passt | briefing_hoeher | briefing_niedriger
      vorrang_im_forecast: abgeleitete_ziele   # abgeleitete_ziele | briefing
    - kpi: umsatz_pro_jahr
      briefing_wert: 250000
      briefing_quelle_zeile: "Briefing-Body Z. 28"
      abgeleitet_worst: 180000
      abgeleitet_real: 320000
      abgeleitet_best: 580000
      diskrepanz_typ: passt
      vorrang_im_forecast: abgeleitete_ziele

# === AOV / LTV-Annahme ===
aov:
  worst: 120
  real: 150
  best: 200
  einheit: EUR
  typ: order   # order | mrr | arr | auftragswert
  konfidenz: hoch
  quelle: kunde_md_portfolio
  begruendung: "Portfolio-Range 80-300 EUR Mid-Tier, realistisch 150 EUR"
  uebernommen_aus: synthese/ziel-annahmen-schema.md

# === Lead-Funnel (nur bei B2B) ===
lead_funnel:
  aktiv: true
  stufen:
    - name: anfrage_qualifiziert
      cr_worst: 0.50
      cr_real: 0.65
      cr_best: 0.80
      konfidenz: mittel
      quelle: branchen_benchmark
    - name: qualifiziert_zu_angebot
      cr_worst: 0.40
      cr_real: 0.55
      cr_best: 0.70
      konfidenz: mittel
      quelle: branchen_benchmark
    - name: angebot_zu_auftrag
      cr_worst: 0.20
      cr_real: 0.30
      cr_best: 0.40
      konfidenz: mittel
      quelle: branchen_benchmark

# === Doppelzaehlungs-Korrektur ===
doppelzaehlung_faktor: 0.85
doppelzaehlung_quelle: aggregat_default
doppelzaehlung_begruendung: "Default fuer 2-Kanal-Overlap, Stratege passt im Review an"

# === Saisonalitaet ===
saisonalitaet:
  defaults_branchen_typ: b2c_ecommerce
  multiplikatoren:
    jan: 0.85
    feb: 0.80
    mar: 0.95
    apr: 1.00
    mai: 1.05
    jun: 1.00
    jul: 0.90
    aug: 0.90
    sep: 1.05
    okt: 1.10
    nov: 1.30
    dez: 1.40
  quelle: branchen_benchmark
  konfidenz: mittel
  kanal_overrides: {}   # pro kanal_slug ein dict mit eigenen Multiplikatoren falls noetig

# === Kanaele mit Volumen, CR, Ramp-up, Spend ===
kanaele:
  - kanal_slug: seo
    kanal_anzeigename: SEO
    rang_aus_kanal_chancen: 1
    kanal_typ: organisch   # organisch | paid | hebel
    volumen_basis_monat:
      worst: 8000
      real: 11400
      best: 16000
      einheit: monatliche_suchanfragen
      quelle: audits/seo-cluster-zusammenfassung.md
      konfidenz: hoch
    klick_anteil:
      worst: 0.20
      real: 0.30
      best: 0.40
      begruendung: "Position-1-Erwartung plus Klick-Verteilung"
    cr_bandbreite:
      worst: 0.008
      real: 0.015
      best: 0.030
      konfidenz: hoch
      quelle: abgeleitete_ziele
    ramp_up:
      funktion: s_curve   # linear | s_curve | sofort
      monate_bis_steady_state_min: 6
      monate_bis_steady_state_real: 9
      monate_bis_steady_state_max: 12
      start_anteil: 0.10
      quelle: abgeleitete_ziele
    spend_monat:
      worst: 0
      real: 0
      best: 0
      einheit: EUR_pro_monat
      quelle: skill_default
      ramp_up_aligned: false
      konfidenz: hoch
      begruendung: "SEO ist organisch, Aufwand wird im 04-06-retainer-kalkulator als Stunden modelliert"
    saisonalitaet_override: null
    konfidenz_gesamt: hoch

  - kanal_slug: sea
    kanal_anzeigename: SEA / Google-Ads
    rang_aus_kanal_chancen: 2
    kanal_typ: paid
    volumen_basis_monat:
      worst: 12000
      real: 18000
      best: 25000
      einheit: monatliche_suchanfragen
      quelle: audits/google-ads.md
      konfidenz: mittel
    klick_anteil:
      worst: 0.05
      real: 0.10
      best: 0.20
      begruendung: "Impression-Share-Annahme paid, ramp-up gegen 25-40%"
    cr_bandbreite:
      worst: 0.025
      real: 0.045
      best: 0.070
      konfidenz: hoch
      quelle: abgeleitete_ziele
    ramp_up:
      funktion: sofort
      monate_bis_steady_state_min: 1
      monate_bis_steady_state_real: 2
      monate_bis_steady_state_max: 2
      start_anteil: 0.70
      quelle: branchen_benchmark
    spend_monat:
      worst: 2500
      real: 4000
      best: 6500
      einheit: EUR_pro_monat
      quelle: branchen_benchmark
      ramp_up_aligned: true
      konfidenz: mittel
      begruendung: "Branchen-typischer SEA-Spend Mittelstand B2C-E-Commerce"
    saisonalitaet_override: null
    konfidenz_gesamt: mittel

  - kanal_slug: meta-ads
    kanal_anzeigename: Meta-Ads
    rang_aus_kanal_chancen: 3
    kanal_typ: paid
    # ... analog zu sea, mit ramp_up funktion sofort und entsprechenden Bandbreiten

  # ... weitere Top-Kanaele aus kanal-chancen.md

# === Auffaelligkeits-Trigger (transparent fuer Strategen) ===
auffaelligkeits_trigger:
  ziele_briefing_vs_abgeleitet_diskrepanz_prozent: 30
  kanal_dominanz_im_forecast_prozent: 60
  ramp_up_engpass_briefing_timeline_monate: 6
  spend_zu_hoch_faktor: 1.5
  worst_case_break_even_schwelle_eur: 0
  saisonalitaet_kollision_multiplikator_schwelle: 0.85

# === Konfidenz-Inventur ===
konfidenz_inventur:
  hoch_konfidenz_annahmen: 0
  mittel_konfidenz_annahmen: 0
  niedrig_konfidenz_annahmen: 0
  branchen_benchmark_anteil_prozent: 0.0
  audit_daten_anteil_prozent: 0.0
  briefing_aussage_anteil_prozent: 0.0
  abgeleitete_ziele_anteil_prozent: 0.0
---

# Forecast-Annahmen-Schema: KUNDENNAME

## Status

`status: vorgeschlagen` — Pflicht-Review durch den Strategen vor Phase B.

## Übersicht

3-5 Sätze: Lauf-Modus, Branchen-Typ, Anzahl Kanäle, Saisonalitäts-Anker, Ramp-up-Mix, gesamt-Spend-Bandbreite, Diskrepanzen Briefing-vs-abgeleitet.

## Übernommen aus `ziel-annahmen-schema.md`

Tabelle, was 1:1 übernommen wurde (AOV, CR-Bandbreiten, Lead-Funnel, Ramp-up-Bandbreiten).

## Verfeinert in diesem Schema

- Saisonalitäts-Kurve (12 Monats-Multiplikatoren)
- Ramp-up-Funktion pro Kanal (linear vs. s_curve vs. sofort)
- Spend-Pfad pro Monat (Bandbreite)
- Doppelzählungs-Faktor (Default 0,85, im Review anpassbar)

## Begründungen pro Saisonalitäts-Kurve

Pro Branchen-Typ kurze Erklärung, warum die Multiplikatoren so gewählt wurden (Quelle: `reference/berechnungs-formeln.md` Tabelle).

## Begründungen pro Ramp-up-Funktion

Pro Kanal: warum `linear`, `s_curve` oder `sofort` — und warum die Anzahl Monate.

## Diskrepanzen Briefing vs. abgeleitete Ziele

Tabelle mit allen ziel_quellen-Einträgen aus dem Frontmatter, sortiert nach Diskrepanz-Größe.

## Pflicht-Review-Sektion

**Bitte prüfen vor `status: bestaetigt`:**

1. **Saisonalität**: Passen die Multiplikatoren zur Kunden-Branche? Gibt es kanal-spezifische Ausnahmen (z. B. SEA-Push im Black Friday)?
2. **Ramp-up-Funktion pro Kanal**: Bei SEO `s_curve` realistisch oder eher pessimistisch? Bei SEA wirklich `sofort` oder gibt es einen Setup-Engpass beim Kunden?
3. **Spend-Bandbreiten**: Liegen die Branchen-Defaults im Budget-Rahmen des Kunden? Briefing-Aussage zum Budget berücksichtigt?
4. **Vorrang bei Diskrepanzen**: Briefing-vs-abgeleitete-Ziele — default `abgeleitete_ziele`, aber bei harten Kunden-Vorgaben auf `briefing` umstellen
5. **Doppelzählungs-Faktor**: 0,85 für 2-Kanal-Overlap default — bei mehr als 3 wichtigen Kanälen auf 0,75 senken
6. **Lead-Funnel** (nur B2B): Sind die CR-Stufen kunden-realistisch oder zu optimistisch?

Nach Review: `status: bestaetigt` im Frontmatter setzen, dann ruft Phase B den Forecast-Berechner.

## Folge-Aktion

```bash
# Stratege bestaetigt:
sed -i '' 's/status: vorgeschlagen/status: bestaetigt/' synthese/forecast-schema.md

# Dann erneut:
# 04-04-forecast-modell aufrufen (Phase B laeuft automatisch)
```
```

## Validierungs-Regeln für Phase B

Vor der Berechnung prüft der Skill:

1. `status: bestaetigt` im Frontmatter
2. Mindestens 3 Einträge in `kanaele[]`
3. Pro Kanal: `volumen_basis_monat`, `cr_bandbreite`, `ramp_up.funktion`, `ramp_up.monate_bis_steady_state_real`, `ramp_up.start_anteil`
4. `aov` vollständig
5. Bei B2B (siehe `branchen_typ`): `lead_funnel.aktiv: true` und drei Stufen mit CR-Bandbreite
6. `saisonalitaet.multiplikatoren` enthält genau 12 Monatsnamen
7. `ziel_inventur` enthält mindestens einen Eintrag

Bei Fehler: konkrete Fehlermeldung im Skill-Schluss-Format mit Hinweis, welches Feld korrigiert werden muss.
