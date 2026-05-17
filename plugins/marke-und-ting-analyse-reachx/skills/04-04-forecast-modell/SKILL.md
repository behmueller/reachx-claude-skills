---
name: 04-04-forecast-modell
description: Baut im MTA-Kontext ein quantitatives 12-Monats-Forecast-Modell mit Best/Real/Worst-Szenarien pro Kanal. Schema-vor-Lauf - Phase A schlägt Annahmen vor (CR-Bandbreiten aus ziele.md, Saisonalität, Ramp-up pro Kanal, Spend, AOV, Lead-Funnel), Phase B rechnet die 12-Monats-Kurve via pandas mit Excel-Pivot. Liest ZWEI Ziel-Quellen (Briefing und synthese/ziele.md) und markiert pro Zahl die Quelle. Outputs forecast-schema.md, forecast.md, forecast.xlsx, forecast.csv plus HTML mit SVG-Sparklines. Pflicht-Bandbreite, niemals Punktschätzungen. Nutze diesen Skill IMMER bei Forecast-Aufgaben in einer MTA - auch bei Phrasen wie "Forecast bauen", "12-Monats-Modell", "Best-Real-Worst", "Szenario-Rechnung", "Monats-Kurve", "Excel-Forecast", "Ramp-up-Modell", "Umsatz-Prognose", "Lead-Forecast", "Marketing-Forecast". Setzt voraus, dass 04-02-kanal-chancen-analyse und 04-03-ziele-aus-potenzialen gelaufen sind - bricht sonst ab.
---

# Forecast-Modell

Vierter Skill in Stufe 4 (Synthese). **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8). Baut auf `04-03-ziele-aus-potenzialen` (Steady-State-Bandbreiten) und `04-02-kanal-chancen-analyse` (Kanal-Priorisierung) auf — verfeinert die Annahmen um Saisonalität, Ramp-up-Kurven, Spend-Pfade und rechnet das **12-Monats-Modell pro Kanal × Szenario**.

**Kernregel: Pflicht-Bandbreite, niemals Punktschätzungen** (siehe Architektur-Entscheidung 10 im Plan). Jede Zelle im Forecast hat eine verlinkte Annahmen-Quelle. Wenn das Briefing eine bezifferte Zahl nennt, wird sie im Output explizit als `quelle: briefing_aussage` markiert — sonst `quelle: abgeleitete_ziele` oder `quelle: branchen_benchmark`.

**Dual-Quellen-Logik:** Der Skill liest ZWEI Quellen für Ziele:

1. `data/briefing.md` — was der Kunde explizit will (KPI-Inventur aus Frontmatter)
2. `synthese/ziele.md` — was aus den Markt-Potenzialen abgeleitet wurde

Im Output wird pro Zahl ausgewiesen, woher sie stammt. Diskrepanzen werden als Auffälligkeit `ziele_briefing_vs_abgeleitet_diskrepanz` markiert.

**Output-Ebenen:**

1. **Annahmen-Schema (Phase A)** `synthese/forecast-schema.md` — Verfeinerung der Annahmen aus `ziel-annahmen-schema.md` um Saisonalitäts-Kurve, Ramp-up-Funktion, Spend-Pfad pro Monat
2. **Aggregat-Markdown (Phase B)** `synthese/forecast.md` — 12-Monats-Szenarien-Tabelle plus Kanal-Verteilung plus Annahmen-Transparenz plus Plausibilitäts-Check gegen Briefing
3. **Roh-CSV (Phase B)** `synthese/forecast.csv` — Kanal × Monat × Szenario × KPI als flache Tabelle
4. **Excel-Pivot (Phase B)** `synthese/forecast.xlsx` — Pivot-fähige Tabelle mit mehreren Sheets (Roh, Pivot, Annahmen)
5. **HTML-Report** `reports/X-forecast.html` — Sparkline-Verlauf pro Kanal plus Aggregat-Chart (SVG inline)

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

- "Forecast bauen"
- "12-Monats-Modell"
- "Best-Real-Worst-Szenarien"
- "Forecast-Modell"
- "Monats-Kurve berechnen"
- "Excel-Forecast"
- "Ramp-up-Modell"
- "Quartals-Forecast"
- "Marketing-Forecast"
- "Wie entwickelt sich der Umsatz über 12 Monate"
- "Forecast für die MTA"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`, `status.md`
- **`04-02-kanal-chancen-analyse` gelaufen** → `synthese/kanal-chancen.md` plus `synthese/kanal-chancen.csv` vorhanden
- **`04-03-ziele-aus-potenzialen` gelaufen** → `synthese/ziele.md`, `synthese/ziele-aufschluesselung.csv`, `synthese/ziel-annahmen-schema.md` mit `status: bestaetigt`

Wenn eine Voraussetzung fehlt: harter Abbruch mit Hinweis, welcher Skill vorher laufen muss.

- Empfohlen: `data/briefing.md` (für KPI-Inventur und Plausibilitäts-Check gegen Briefing-Ziele)
- Branchen-Saisonalitäts-Defaults aus `reference/berechnungs-formeln.md` werden geladen

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `synthese/forecast-schema.md` existiert und welchen Status sie hat.

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
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Schema und Outputs liegen im `synthese/`-Sub-Folder auf Drive:

```
1. Existiert synthese/forecast-schema.md auf Drive?
   - Nein -> Phase A (Schema generieren)
   - Ja, status: vorgeschlagen -> freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt -> Phase B (Forecast-Berechnung)
   - Ja, anderer Status -> Abbruch mit Hinweis auf erlaubte Werte

2. Existiert synthese/forecast.md auf Drive bereits?
   - Nein -> weiter mit Phase B
   - Ja -> fragen (ueberschreiben / Backup-und-neu / abbrechen)
```

---

## Phase A — Annahmen-Schema

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Lies `status.md` aus Drive.

**Hartes Voraussetzungs-Gate** (jeweils `drive.py find_by_name`):

- `synthese/kanal-chancen.md` muss auf Drive existieren — sonst Abbruch mit Hinweis auf `04-02-kanal-chancen-analyse`
- `synthese/ziele.md` muss auf Drive existieren — sonst Abbruch mit Hinweis auf `04-03-ziele-aus-potenzialen`
- `synthese/ziel-annahmen-schema.md` mit `status: bestaetigt` muss auf Drive existieren — sonst Abbruch

Lies aus diesen Dateien aus Drive (siehe `reference/forecast-annahmen-schema-template.md` für die genauen Felder):

- Aus `synthese/ziele.md` Frontmatter: `aggregat.*`, `kanaele[].konservativ/realistisch/ambitioniert`, `kanaele[].ramp_up_monate_min/max`, `forecast_vorbereitung.uebernahme_in_forecast_schema`
- Aus `synthese/ziel-annahmen-schema.md` Frontmatter: AOV-Bandbreite, CR-Bandbreiten pro Kanal, Lead-Funnel-Stufen, Ramp-up-Bandbreiten, branchen_typ, lauf_modus
- Aus `synthese/kanal-chancen.md` Frontmatter: `top_3_empfehlungen[]`, `branchen_typ`, `strategische_story.primaer_hebel`
- Aus `data/briefing.md` Frontmatter und Body: bezifferte KPIs (Leads/Monat, Umsatz, Timeline, Spend-Budget falls genannt)

### Schritt A.2: Dual-Quellen-KPI-Inventur

Pro Briefing-KPI prüfen: Liegt die Zahl auch in `ziele.md`? Wenn ja, beide Werte im Schema festhalten und Diskrepanz dokumentieren:

```yaml
ziel_inventur:
  briefing_kpis_vorhanden: true
  abgeleitete_ziele_vorhanden: true
  ziel_quellen:
    - kpi: leads_pro_monat
      briefing_wert: 50           # null wenn nicht im Briefing
      briefing_quelle_zeile: "Briefing-Body Z. 24"
      abgeleitet_konservativ: 25
      abgeleitet_realistisch: 60
      abgeleitet_ambitioniert: 110
      diskrepanz_typ: passt | briefing_hoeher | briefing_niedriger
      vorrang_im_forecast: abgeleitete_ziele
```

**Vorrang-Logik:**

- **Default**: `vorrang_im_forecast: abgeleitete_ziele` (drei Szenarien, breit, mit Quellen)
- Wenn das Briefing eine harte Vorgabe ist: Stratege setzt im Review `vorrang_im_forecast: briefing` und `abgeleitete_ziele` werden als Plausibilitäts-Check geführt

### Schritt A.3: Konversionsraten und Volumen pro Kanal übernehmen

Aus `synthese/ziel-annahmen-schema.md` werden die CR-Bandbreiten und Volumen-Basen 1:1 übernommen (siehe `forecast_vorbereitung.uebernahme_in_forecast_schema`). Bei Bedarf branchen-spezifisch verfeinert (Stratege im Review):

```yaml
kanaele:
  - kanal_slug: seo
    cr_bandbreite:
      worst: 0.008
      real: 0.015
      best: 0.030
    volumen_basis_monat:
      worst: 8000
      real: 11400
      best: 16000
      einheit: monatliche_suchanfragen
      quelle: audits/seo-cluster-zusammenfassung.md
```

### Schritt A.4: Saisonalitäts-Kurve pro Kanal

Branchen-typische Saisonalität als 12-Monats-Multiplikatoren (Default 1,0 = neutral). Defaults pro Branchen-Typ in `reference/berechnungs-formeln.md`. Beispiel für `b2c_ecommerce`:

```yaml
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
  kanal_overrides:
    sea: null
    seo: null
  konfidenz: mittel
```

Stratege kann pro Kanal Overrides setzen (z. B. SEA-Spend wird im Black Friday hochgedreht).

### Schritt A.5: Ramp-up-Funktion pro Kanal

Pro Kanal eine **Wachstums-Funktion** im Ramp-up-Fenster. Drei Typen verfügbar:

- `linear` — gleichmäßiger Anstieg von Start-Anteil auf Steady State über N Monate
- `s_curve` — langsamer Start, steile Mitte, Sättigung (typisch für SEO, Content)
- `sofort` — Monat 1 bereits 70-80%, Monat 2-3 bei 100% (typisch für SEA, Meta-Ads)

```yaml
kanaele:
  - kanal_slug: seo
    ramp_up:
      funktion: s_curve
      monate_bis_steady_state_min: 6
      monate_bis_steady_state_max: 12
      monate_bis_steady_state_real: 9
      start_anteil: 0.10
      quelle: abgeleitete_ziele
  - kanal_slug: sea
    ramp_up:
      funktion: sofort
      monate_bis_steady_state_min: 1
      monate_bis_steady_state_max: 2
      monate_bis_steady_state_real: 2
      start_anteil: 0.70
      quelle: abgeleitete_ziele
```

### Schritt A.6: Spend-Annahmen pro Kanal pro Monat

Pro Paid-Kanal (SEA, Meta-Ads, LinkedIn-Ads): Monats-Spend als Bandbreite. Quelle: Briefing falls genannt, sonst Branchen-Benchmark, sonst Skill-Schätzung. Für organische Kanäle (SEO, Content, Social-organisch): Aufwand in Mitarbeiter-Stunden pro Monat oder Retainer-Anteil — der `04-06-retainer-kalkulator` rechnet später daraus den Stunden-Preis.

```yaml
kanaele:
  - kanal_slug: sea
    spend_monat:
      worst: 2500
      real: 4000
      best: 6500
      einheit: EUR_pro_monat
      quelle: branchen_benchmark
      ramp_up_aligned: true
      konfidenz: mittel
```

### Schritt A.7: AOV / LTV / Lead-zu-Kunde-Raten übernehmen

1:1 aus `synthese/ziel-annahmen-schema.md`. Stratege kann im Review verfeinern.

### Schritt A.8: Auffälligkeits-Trigger im Schema vorab definieren

Im Schema-Frontmatter Schwellwerte für die Phase-B-Auffälligkeiten dokumentieren (transparent für den Strategen):

```yaml
auffaelligkeits_trigger:
  ziele_briefing_vs_abgeleitet_diskrepanz_prozent: 30
  kanal_dominanz_im_forecast_prozent: 60
  ramp_up_engpass_briefing_timeline_monate: 6
  spend_zu_hoch_faktor: 1.5
```

### Schritt A.9: `synthese/forecast-schema.md` nach Drive schreiben

Erzeuge das Schema lokal nach dem Format in `reference/forecast-annahmen-schema-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "forecast-schema.md" \
  /tmp/forecast-schema.md "text/markdown"
```

Stratege editiert das Schema direkt in der Drive-Web-UI.

Sektionen:

- **Frontmatter**: Skill-Metadaten, `basiert_auf`, Branchen-Typ, Lauf-Modus, KPI-Inventur, AOV, Lead-Funnel, Kanäle mit CR/Volumen/Ramp-up/Saisonalität/Spend, Auffälligkeits-Trigger
- **Body**: Übersicht der übernommenen Annahmen, Begründung pro Saisonalitäts-Kurve, Begründung pro Ramp-up-Funktion, Pflicht-Review-Sektion mit konkreten Eingriffspunkten

### Schritt A.10: Schluss-Format Phase A

```
✓ 04-04-forecast-modell Phase A abgeschlossen.

Outputs (auf Drive):
- synthese/forecast-schema.md — Annahmen-Set (status: vorgeschlagen)

Annahmen-Übersicht:
- Branchen-Typ:    BRANCHEN_SLUG
- Lauf-Modus:      MODUS
- Kanäle im Set:   N
- Saisonalität:    SAISON_TYP (Default oder Override pro Kanal)
- Ramp-up-Mix:     X linear / Y s_curve / Z sofort
- Spend gesamt:    Aggregat-Bandbreite EUR pro Jahr
- Ziel-Quellen:    abgeleitete Ziele plus Briefing-KPIs (N Diskrepanzen markiert)

Pflicht-Review durch den Strategen
Bitte prüfen: Saisonalitäts-Kurven (passen zur Branche?), Ramp-up-Funktionen pro Kanal (s_curve vs sofort), Spend-Bandbreiten (Branchen-realistisch oder Briefing-vorgegeben?), Vorrang im Forecast bei Briefing-vs-abgeleitet-Diskrepanzen.
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text "$FOLDER_ID" "status.md"`):

```yaml
blockiert:
  - skill: 04-04-forecast-modell (Phase B)
    wartet_auf: "Strategen-Review von synthese/forecast-schema.md (auf Drive)"
```

---

## Phase B — Forecast-Berechnung

### Schritt B.1: Schema-Validierung

Lies `synthese/forecast-schema.md` aus Drive (`find_by_name(SYNTHESE_ID, "forecast-schema.md")` → `read_text`). Prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis auf Phase A
2. Mindestens 3 Kanäle im Schema
3. Jeder Kanal hat: CR-Bandbreite, Volumen-Basis, Ramp-up-Funktion mit Monaten und Start-Anteil, Saisonalität (Default oder Override)
4. AOV-Bandbreite gesetzt
5. Falls B2B: Lead-Funnel-Stufen komplett
6. `ziel_inventur` mit mindestens einer Quelle vorhanden

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Existenz-Check Output

Wenn `synthese/forecast.md`, `synthese/forecast.csv` oder `synthese/forecast.xlsx` auf Drive bereits existieren (`drive.py find_by_name`): fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Berechnung ausführen

Rufe das mitgelieferte Python-Skript `scripts/forecast-berechnung.py` auf. Das Skript liest Schema-Inhalte aus einer lokalen Cache-Datei (das SKILL lädt Schema vorher per `drive.py read` nach `~/.cache/reachx-mta/<slug>/forecast-schema.md`) und schreibt Outputs in den lokalen Cache, die das SKILL danach per `drive.py upsert-text` nach Drive hochlädt. Das Skript:

1. Lädt das Schema (YAML-Frontmatter parsen)
2. Berechnet pro Kanal × Monat × Szenario die fünf Pflicht-KPIs:
   - **Sessions / Klicks** (Volumen-Basis × Ramp-up-Faktor × Saisonalitäts-Multiplikator × Klick-Anteil)
   - **Anfragen / Leads** (Sessions × Conversion-Rate)
   - **Qualifizierte Leads / Orders** (Leads × Lead-Funnel bei B2B, sonst direkt Orders bei B2C)
   - **Umsatz** (Orders × AOV)
   - **Spend** (aus Spend-Annahme × Ramp-up-Faktor)
3. Aggregiert über alle Kanäle pro Monat × Szenario, wendet Doppelzählungs-Faktor an (aus Schema oder Default 0,85)
4. Schreibt `forecast.csv` (flach) und `forecast.xlsx` (Pivot mit drei Sheets: roh, pivot, annahmen) in den lokalen Cache; das SKILL lädt sie nach `synthese/` auf Drive hoch
5. Berechnet Auffälligkeits-Trigger und gibt sie als JSON an den Skill zurück

Berechnungs-Details in `reference/berechnungs-formeln.md`. Konkret:

```
sessions[kanal, monat, szenario] =
    volumen_basis[szenario]
    * ramp_up_faktor(monat, ramp_up_funktion, monate_bis_steady_state[szenario], start_anteil)
    * saisonalitaet_multiplikator[monat]
    * klick_anteil[szenario]

leads[kanal, monat, szenario] = sessions x cr[szenario]

# B2C: orders direkt = leads (transactional CR)
# B2B: orders = leads x cr_anfrage_qualifiziert x cr_qualifiziert_zu_angebot x cr_angebot_zu_auftrag

umsatz[kanal, monat, szenario] = orders x aov[szenario]
spend[kanal, monat, szenario]  = spend_monat[szenario] x ramp_up_faktor (wenn ramp_up_aligned)
```

### Schritt B.4: Quellen-Verlinkung pro Zelle

Pro Roh-Zeile in der CSV werden die `*_quelle`-Felder gesetzt:

- `quelle_volumen` — woher kommt die Volumen-Basis (z. B. `audits/seo-cluster-zusammenfassung.md`)
- `quelle_cr` — woher die Conversion-Rate (z. B. `abgeleitete_ziele`)
- `quelle_aov` — woher der AOV (z. B. `data/kunde.md` Portfolio)
- `quelle_spend` — woher der Spend (z. B. `briefing_aussage` oder `branchen_benchmark`)
- `quelle_ziel_overlay` — falls Briefing-KPI als Vorrang im Schema gesetzt war: `briefing_aussage`, sonst `abgeleitete_ziele`

### Schritt B.5: Auffälligkeiten extrahieren

Mindestens **6 Auffälligkeiten**. Wenn weniger als 6 echte aus den Daten ableitbar sind: ergänze um methodische Hinweise (z. B. niedrige Konfidenz im Schema).

| Typ | Auslöser | Beispiel |
|---|---|---|
| `ziele_briefing_vs_abgeleitet_diskrepanz` | Briefing-KPI weicht > Schwellwert vom abgeleitet_real ab | "Briefing-Ziel 100 Leads/Monat, abgeleitet realistisch 60 — Erwartungs-Diskrepanz im Kunden-Gespräch erden" |
| `kanal_dominanz_im_forecast` | Ein Kanal trägt > 60% des Real-Szenarios | "SEO macht 72% des realistischen Umsatzes — Klumpenrisiko, wenn ein Cluster wegbricht" |
| `ramp_up_engpass` | Real-Szenario erreicht Briefing-Timeline-Ziel nicht | "Briefing erwartet Ergebnisse in 3 Monaten, Top-Kanal SEO erreicht Steady State erst Monat 9 — Hybrid mit SEA als Sofort-Hebel" |
| `worst_case_nicht_break_even` | Selbst Best-Szenario erreicht nicht Break-Even im 12-Monats-Horizont | "Best-Szenario kommt auf 280k Umsatz, Spend plus Retainer 320k — Break-Even erst ab Jahr 2" |
| `saisonalitaet_kollidiert_kampagnen_start` | Geplanter Start trifft Branchen-Tief | "Start Januar, B2C-E-Commerce hat Januar-Tief (Multiplikator 0,85) — Start zwei Monate vorziehen oder akzeptieren" |
| `spend_zu_hoch_fuer_geforderte_ziele` | Spend-Annahme deutlich über Branchen-Ranges | "SEA-Spend 8.000 EUR/Monat liegt 50% über Branchen-Range — Volumen-Annahme zu konservativ oder Spend reduzieren" |
| `briefing_kpi_passt` | Plausibilitäts-Check positiv | "Briefing-Ziel 50 Leads/Monat liegt in Real-Bandbreite — bestätigt" |
| `konfidenz_niedrig_basis` | Mehrheit der Annahmen aus `branchen_benchmark` ohne Audit-Bestätigung | "Großteil der Annahmen aus Branchen-Defaults — Verfeinerung mit Kunden-CRM-Daten würde Forecast deutlich präziser machen" |

Auffälligkeiten werden im Markdown und HTML-Report prominent gezeigt.

### Schritt B.6: CSV-Output `synthese/forecast.csv` nach Drive

Lokal generiert vom Script (Schritt B.3), dann `drive.py upsert-text "$SYNTHESE_ID" "forecast.csv" /tmp/forecast.csv "text/csv"`. Vollständiges Schema in `reference/forecast-output-schema.md`. Spalten:

```
kanal_slug,kanal_anzeigename,monat_index,monat_label,szenario,
sessions,leads,qualifizierte_leads,orders,umsatz_eur,spend_eur,
cr_angewandt,aov_angewandt,ramp_up_faktor,saisonalitaet_multiplikator,
quelle_volumen,quelle_cr,quelle_aov,quelle_spend,quelle_ziel_overlay,
konfidenz,zugehoerige_auffaelligkeiten,
datenstand_iso
```

- `monat_index`: 1-12
- `monat_label`: z. B. `2026-06` (aus `meta.json.kickoff_datum` + Index)
- `szenario` ∈ `worst | real | best | aggregat`
- `kanal_slug: aggregat` für die Aggregat-Zeilen über alle Kanäle

### Schritt B.7: Excel-Output `synthese/forecast.xlsx` nach Drive

Lokal generiert vom Script, dann `drive.py upsert-text "$SYNTHESE_ID" "forecast.xlsx" /tmp/forecast.xlsx "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"`. Drei Sheets via `openpyxl` (siehe Script):

1. **Sheet `roh`**: flache Tabelle wie CSV
2. **Sheet `pivot`**: Pivot via `pandas.pivot_table` mit Kanal × Monat × Szenario, KPIs als Spalten, plus Aggregat-Zeile pro Monat
3. **Sheet `annahmen`**: Annahmen-Transparenz (AOV-Bandbreite, CR pro Kanal, Saisonalitäts-Multiplikatoren, Spend-Bandbreiten, Ramp-up-Funktionen) mit Quellen-Spalte

Excel-Formatierung minimal: Header-Zeile bold, Spaltenbreiten autofit, Zahlen mit Tausender-Separator und EUR-Suffix wo passend.

### Schritt B.8: Aggregat-Markdown `synthese/forecast.md` nach Drive

Lokal generieren, dann `drive.py upsert-text "$SYNTHESE_ID" "forecast.md" /tmp/forecast.md "text/markdown"`. Body strukturiert nach (Schema in `reference/forecast-output-schema.md`):

- **Übersicht**: Lauf-Modus, Branchen-Typ, Anzahl Kanäle, 12-Monats-Aggregat-Bandbreite (worst-best EUR), Steady-State-Monat, Top-Kanal-Beitrag
- **12-Monats-Aggregat-Tabelle** (Szenario × Monat, Umsatz und Leads als zwei Tabellen)
- **Pro Kanal ein Sub-Block** mit Mini-Tabelle und Mini-Sparkline-Beschreibung (eigentliche SVG nur im HTML-Report)
- **Annahmen-Transparenz**: was wurde übernommen aus `ziel-annahmen-schema`, was wurde verfeinert
- **Plausibilitäts-Check gegen Briefing**: nur bei `lauf_modus: plausibilitaets_check | hybrid`
- **Diskrepanz-Tabelle Briefing vs. abgeleitete Ziele**
- **Auffälligkeiten** (sortiert nach Relevanz)
- **Vorbereitung für `04-05-90-tage-plan` und `04-06-retainer-kalkulator`**: welche Forecast-Werte direkt weiterverwendet werden

### Schritt B.9: HTML-Report `reports/X-forecast.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

`_shell.html` aus Drive lesen, Platzhalter füllen, dann via `drive.py upsert-text "$REPORTS_ID" "X-forecast.html" /tmp/report.html "text/html"`. Aus `reports/_shell.html`:

- Stat-Strip oben: 12-Monats-Aggregat real (EUR), Bandbreite (worst-best), Top-Kanal-Beitrag, Steady-State-Monat
- Sticky-TOC zu Aggregat-Chart, Pro-Kanal-Blöcke, Annahmen, Auffälligkeiten
- **Aggregat-Chart** als inline-SVG: drei Szenarien-Linien (worst/real/best) über 12 Monate, Y-Achse Umsatz
- **Pro Kanal** ein `details class="dim"`-Block mit Mini-Sparkline (SVG inline, Höhe ~40px, alle drei Szenarien als dünne Linien)
- **Kanal-Verteilungs-Donut** (im Real-Szenario, Anteil am 12-Monats-Aggregat-Umsatz) — als SVG inline
- **Annahmen-Tabelle** mit Quellen-Spalte
- **Plausibilitäts-Check** als prominente Karte (grün/gelb/rot je nach Ergebnis)
- **Auffälligkeiten** als `.suggestion`-Block

### Schritt B.10: Dashboard-Update und status.md

Beide aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben.

- `04-04-forecast-modell` in `schritte_done` (Phase B abgeschlossen)
- Aus `blockiert` entfernen
- Reports-Liste um den HTML-Report
- `naechster_empfohlen`: `04-05-90-tage-plan`
- Parallel möglich: `04-06-retainer-kalkulator`

### Schritt B.11: Standard-Schlussformat im Chat

```
✓ 04-04-forecast-modell Phase B abgeschlossen.

Outputs (auf Drive):
- synthese/forecast.md — 12-Monats-Forecast mit Szenarien-Tabelle
- synthese/forecast.csv — Roh-Tabelle (Kanal x Monat x Szenario x KPI)
- synthese/forecast.xlsx — Pivot-faehig (Sheets: roh, pivot, annahmen)
- reports/X-forecast.html — Sparkline-Verlauf pro Kanal plus Aggregat-Chart
Status aktualisiert in: status.md

12-Monats-Aggregat (Umsatz):
- Worst:        X EUR
- Real:         Y EUR
- Best:         Z EUR
Top-Kanal-Beitrag: KANAL_NAME (Anteil P% am Real-Szenario)
Steady-State erreicht: Monat M (im Real-Szenario)

Top strategische Beobachtungen:
1. AUFFAELLIGKEIT_1
2. AUFFAELLIGKEIT_2
3. AUFFAELLIGKEIT_3

[Bei Diskrepanz Briefing vs. abgeleitet:]
ℹ Briefing-Vergleich
- Briefing-KPI liegt OBEN | UNTEN | INNERHALB der Real-Bandbreite — siehe Plausibilitäts-Block.

Nächste Schritte:
1. 04-05-90-tage-plan — operationalisiert die Top-Kanäle aus dem Forecast
2. (parallel möglich) 04-06-retainer-kalkulator — braucht Spend-Annahmen aus dem Forecast

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/forecast-annahmen-schema-template.md` — Phase-A-Output-Format mit Beispiel-Annahmen-Set
- `reference/berechnungs-formeln.md` — Funnel-Formeln, Saisonalität-Defaults pro Branche, Ramp-up-Kurven (linear, s_curve, sofort)
- `reference/forecast-output-schema.md` — Phase-B-CSV-, Markdown- und Excel-Schema mit Validierungs-Regeln
- `scripts/forecast-berechnung.py` — Python-Helper, voll lauffähig (pandas, openpyxl)

## Edge Cases

- **`ziele.md` fehlt** → harter Abbruch in Phase A mit Hinweis auf `04-03-ziele-aus-potenzialen`. Skill rechnet niemals ohne Bandbreiten-Basis.

- **Briefing hat eine harte KPI-Vorgabe** → Stratege setzt im Schema-Review `ziel_inventur.ziel_quellen[i].vorrang_im_forecast: briefing`. Phase B führt den Forecast trotzdem mit drei Szenarien aus den abgeleiteten Annahmen, markiert aber die Briefing-Linie zusätzlich als Overlay im HTML-Chart.

- **Kickoff-Datum in `meta.json` ist null** → Monats-Labels starten mit `M1` / `M2` ... statt mit Kalendermonaten. Im Output Hinweis "Kickoff-Datum nicht gesetzt, Saisonalitäts-Multiplikatoren nutzen Default-Monat-Reihenfolge".

- **B2C-Kunde ohne Lead-Funnel** → `lead_funnel.aktiv: false` im Schema, Phase B rechnet direkt `sessions × cr = orders` und überspringt qualifizierte-Leads und Angebote.

- **Website-CRO als Hebel-Kanal** → CRO wird als Conversion-Rate-Uplift auf bestehende Kanäle modelliert, nicht als eigener Kanal. Im Schema mit `kanal_typ: hebel` markiert. Phase B addiert den Uplift in Monat M (Default Monat 4 nach Ramp-up) auf die Conversion-Raten der anderen Kanäle.

- **Stratege wünscht Re-Run mit verändertem Schema** → Override-Argument "Schema überarbeiten" → Skill löscht (mit Backup) Phase-B-Outputs, setzt Schema auf `vorgeschlagen` zurück. Stratege editiert, bestätigt, Phase B neu.

- **Mehr als 6 Auffälligkeiten greifen** → Skill listet alle, sortiert nach Relevanz. Im Chat-Schluss werden Top-3 nach Relevanz hervorgehoben.

- **Forecast Aggregat überschreitet das Briefing-Budget deutlich** → Auffälligkeit `spend_zu_hoch_fuer_geforderte_ziele` als prominente Warnung, im Kunden-Gespräch klären.

- **Saisonalitäts-Daten für die Branche nicht verfügbar** → Default-Multiplikatoren 1,0 für alle Monate plus Auffälligkeit `konfidenz_niedrig_basis`.

- **Python-Script schlägt fehl** → Skill fängt den Fehler ab, gibt im Chat die Fehler-Ursache aus (z. B. fehlende Pandas-Library), schreibt KEINE Output-Dateien.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt — Phase B läuft niemals ohne `status: bestaetigt`
- Outputs leben auf Google Drive in `synthese/` und `reports/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für Aggregat, CSV als Single-Source-of-Truth, Excel als Convenience-Layer
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (aus Drive lesen, patchen, upsert)
- HTML-Report aus `reports/_shell.html` (aus Drive geladen)
- **Pflicht-Bandbreite, niemals Punktschätzungen** — strikt durchsetzen, jede Zahl als worst/real/best
- **Quellen-Transparenz**: jede Zelle im Forecast hat eine verlinkte Quelle in der CSV
- **Dual-Quellen-Logik**: Briefing-KPIs und abgeleitete-ziele werden gleichberechtigt geführt, Vorrang im Schema explizit
- **Schreibt NICHT ins `briefing.md` oder `ziele.md` zurück** — Forecast ist eigene Quelle, baut auf den beiden auf
