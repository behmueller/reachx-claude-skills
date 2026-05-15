---
name: 04-06-retainer-kalkulator
description: Berechnet am Ende der MTA die REACHX-Retainer-Empfehlung aus forecast.md und 90-tage-plan.md. Drei Service-Level (basis, wachstum, vollservice) mit Preis-Range in drei Szenarien (konservativ, realistisch, ambitioniert), Setup, laufender Aufwand Monate 4-12, ROI-Argumentation und Break-Even-Monat pro Szenario. Schema-vor-Lauf - Phase A schlaegt Service-Level, Kanal-Verantwortlichkeit REACHX vs Kunden-Inhouse, Reporting-Frequenz und Vertragslaufzeit vor, Stratege bestaetigt, Phase B berechnet mit Pandas plus openpyxl und schreibt retainer.md, retainer.xlsx und einen HTML-Report mit drei Service-Level-Karten plus ROI-Chart. Stundensaetze und Aufwands-Bandbreiten liegen zentral im Skill-reference/. Nutze IMMER bei Phrasen wie Retainer berechnen, Service-Level-Vorschlag, Stunden hochrechnen, Verkaufs-Preis, Break-Even Marketing-Budget, ROI Retainer, monatlicher Aufwand REACHX. Setzt 04-04-forecast-modell und 04-05-90-tage-plan voraus - bricht sonst ab.
---

# Retainer-Kalkulator

Letzter rein rechnerischer Skill in Stufe 4 (Synthese). **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8). Erzeugt das **verkaufs-relevante Dokument am Ende der MTA**: drei Service-Level (basis, wachstum, vollservice) mit Preis-Bandbreite pro Monat, Setup-Bandbreite, laufendem Aufwand Monate 4-12, ROI-Argument gegen den Forecast und Break-Even-Monat pro Szenario.

**Architektur-Spezifikum:** Stundensaetze und Aufwands-Bandbreiten liegen **zentral im Skill-`reference/`-Ordner**, NICHT projektspezifisch. Begruendung: REACHX-Stundensaetze und Aufwands-Bandbreiten sind agentur-weit gleich, nicht pro MTA neu kuratiert. Bei Stundensatz- oder Bandbreiten-Aenderungen wird der zentrale Skill aktualisiert (Versionierung in `reachx-stundensaetze.md`), nicht das einzelne Projekt.

Phase A erzeugt eine **projektspezifische Konfiguration** in `synthese/retainer-konfiguration.md` mit Service-Level-Auswahl, Kanal-Verantwortlichkeit (REACHX vs Kunden-Inhouse), Reporting-Frequenz, Workshop-Frequenz und Vertragslaufzeit. Alle Stundensaetze und Aufwands-Bandbreiten kommen aus dem zentralen Reference-Schema.

Alle Outputs verwenden **Pflicht-Bandbreiten** (min/max) — niemals Punktwerte. Drei Szenarien-Logik analog zu `04-04-forecast-modell`: konservativ, realistisch, ambitioniert.

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

- "Retainer berechnen"
- "Retainer-Empfehlung erstellen"
- "Service-Level-Vorschlag fuer den Kunden"
- "Basis Wachstum Vollservice"
- "Stunden hochrechnen"
- "Verkaufs-Preis kalkulieren"
- "Break-Even Marketing-Budget"
- "ROI-Argumentation Retainer"
- "Monatlicher Aufwand REACHX"
- "MTA-Retainer-Folie vorbereiten"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen
- `04-04-forecast-modell` gelaufen → `synthese/forecast.md` mit Real-Szenario-Umsatz-12-Monate vorhanden, plus Worst/Best fuer Konservativ/Ambitioniert-Mapping
- `04-05-90-tage-plan` gelaufen → `synthese/90-tage-plan.md` mit Massnahmen-Liste und Aufwands-Hinweisen
- `04-02-kanal-chancen-analyse` gelaufen → `synthese/kanal-chancen.md` mit Top-Kanaelen
- Empfohlen: `data/briefing.md` (fuer Budget-Indikationen, Inhouse-Team-Reife, Vertragslaufzeit-Wunsch)
- Zentrale Reference: `reference/reachx-stundensaetze.md` und `reference/aufwands-bandbreiten.md` sind Pflicht und werden IMMER gelesen (auch in Phase A)

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prueft der Skill, ob `synthese/retainer-konfiguration.md` existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B laeuft.

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
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

**Wichtig (Architektur-Spezifikum):** Die zentralen `reference/reachx-stundensaetze.md` und `reference/aufwands-bandbreiten.md` bleiben im Skill-Ordner (im Plugin), NICHT auf Drive. Diese werden weiterhin als lokale Skill-Reference-Files gelesen. Nur die projektspezifischen Outputs (`synthese/retainer-*`, `synthese/retainer.md`, `synthese/retainer.xlsx`) wandern nach Drive.

Schema und Outputs liegen im `synthese/`-Sub-Folder auf Drive:

```
1. Existiert synthese/retainer-konfiguration.md auf Drive?
   - Nein → Phase A (Projekt-Konfiguration generieren)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt → Phase B (eigentliche Berechnung)
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert synthese/retainer.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen: ueberschreiben / Backup-und-neu / abbrechen
```

---

## Phase A — Projekt-Konfigurations-Schema

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Pruefe via `drive.py find_by_name "$SYNTHESE_ID" "..."`:

- `synthese/forecast.md` auf Drive vorhanden? Sonst Abbruch mit Hinweis auf `04-04-forecast-modell`
- `synthese/90-tage-plan.md` auf Drive vorhanden? Sonst Abbruch mit Hinweis auf `04-05-90-tage-plan`
- `synthese/kanal-chancen.md` auf Drive vorhanden? Sonst Abbruch mit Hinweis auf `04-02-kanal-chancen-analyse`

Bei fehlenden Voraussetzungen:

```
✗ Voraussetzungen fuer 04-06-retainer-kalkulator fehlen.
Bitte zuerst die folgenden Skills laufen lassen: KONKRETE LISTE
Aktuell fehlt: KONKRETE LISTE
```

**Pflicht-Lese-Reihenfolge:**

1. `reference/reachx-stundensaetze.md` (zentrale Stundensaetze — IMMER zuerst, niemals Caches verwenden; lokal aus dem Skill-Ordner gelesen, NICHT von Drive)
2. `reference/aufwands-bandbreiten.md` (zentrale Aufwands-Bandbreiten pro Massnahmen-Typ; ebenfalls lokal aus dem Skill-Ordner)
3. `synthese/kanal-chancen.md` Frontmatter aus Drive (Top-Kanaele, chancen_score, Branchen-Typ)
4. `synthese/forecast.md` Frontmatter aus Drive (Worst/Real/Best-Szenario-Umsatz-12-Monate)
5. `synthese/90-tage-plan.md` aus Drive (Massnahmen-Liste mit Verantwortlichkeiten-Hinweisen, ggf. Aufwands-Schaetzungen)
6. `data/briefing.md` aus Drive (optional, Budget-Indikation, Inhouse-Team-Hinweise, Vertragslaufzeit-Wunsch)

### Schritt A.2: Service-Level-Vorschlag ableiten

Drei Service-Level laut `reference/retainer-konfiguration-template.md`:

| Service-Level | Charakter | Typische Kunden-Reife | Typische Kanal-Verantwortung |
|---|---|---|---|
| `basis` | Beratungs-dominiert, Strategie plus Reporting, Operatives beim Kunden | Inhouse-Team mit 2 plus FTE Marketing | REACHX nur Strategie, Reporting, Reviews; Kunde macht Content + Paid-Setup + Tracking |
| `wachstum` | Hybrid, REACHX uebernimmt 2-3 Top-Kanaele operativ, Rest gemeinsam | Inhouse-Team 1 FTE oder Junior | REACHX Top-Kanaele plus Strategie; Kunde unterstuetzt operativ |
| `vollservice` | REACHX uebernimmt alle Top-Kanaele plus Strategie plus Reporting | Kein oder sehr junges Inhouse-Team | REACHX macht alles im Top-3-Kanal-Mix; Kunde nur Freigaben |

Default-Heuristik (Branchen-Heuristik plus Briefing-Signale):

- Briefing nennt "internes Team" oder "Inhouse-Marketer" mit FTE ≥ 2 → Vorschlag `basis`
- Briefing nennt FTE 1, "Junior-Marketer" oder "Werkstudent" → Vorschlag `wachstum`
- Briefing nennt "kein internes Team", "wir haben niemanden", "ihr macht alles" → Vorschlag `vollservice`
- Briefing fehlt: Default `wachstum` (haeufigster Fall im REACHX-Mittelstand-Segment)
- Touchpoint-Inventur in `data/kunde.md` zeigt sehr inaktive Social-Profile / kein Tracking → Hinweis dass Kunde wahrscheinlich keine starke Inhouse-Kapazitaet hat, Vorschlag eher `vollservice` oder `wachstum`

Markiere Auffaelligkeit `service_level_passt_nicht_zu_kunden_reife`, wenn Briefing-Signal und Reife-Signal widerspruechlich sind (z. B. Briefing sagt Vollservice, Touchpoint-Inventur zeigt starkes Inhouse-Team — oder umgekehrt).

### Schritt A.3: Kanal-Verantwortlichkeit pro Kanal

Aus `synthese/90-tage-plan.md` und `synthese/kanal-chancen.md` Top-Kanaele extrahieren. Pro Kanal vorschlagen:

```yaml
kanal_verantwortlichkeit:
  seo:
    reachx_anteil_prozent: 80   # Default je nach Service-Level
    kunde_anteil_prozent: 20
    skills: [strategie, content-briefing, technik-pflege, reporting]
  sea:
    reachx_anteil_prozent: 100
    kunde_anteil_prozent: 0
    skills: [kampagnen-management, anzeigentexte, reporting]
  content:
    reachx_anteil_prozent: 50
    kunde_anteil_prozent: 50   # Kunde liefert Themen, REACHX redigiert
    skills: [redaktion, briefing-uebernahme]
  ...
```

Default-Verteilung pro Service-Level:

- `basis`: REACHX im Schnitt 30-50% pro Kanal (Beratung plus Strategie plus Reporting), Kunde 50-70% (operativ)
- `wachstum`: REACHX 60-80% pro Top-Kanal, Kunde 20-40% (unterstuetzend)
- `vollservice`: REACHX 90-100% pro Top-Kanal, Kunde 0-10% (Freigaben, Asset-Lieferung)

Uebernahme aus `90-tage-plan.md`: wenn dort eine Massnahme explizit "Kunde uebernimmt" oder "REACHX uebernimmt" markiert ist, wird das hier gespiegelt.

### Schritt A.4: Reporting-Frequenz

Default-Heuristik:

- Service-Level `basis` → `monatlich` (Strategie-Call) plus `quartal` (Reporting-Workshop)
- Service-Level `wachstum` → `monatlich` (Reporting plus Strategie-Call) plus optional `woechentlich_stand_up` (15 Minuten Calls)
- Service-Level `vollservice` → `monatlich` plus `woechentlich_stand_up` plus `quartal` (Strategie-Workshop)

Strategen-Override moeglich, z. B. wenn Kunde im Briefing explizit "kein woechentliches Call-Format" gewuenscht hat.

### Schritt A.5: Strategie-Workshop-Frequenz

Default:

- Service-Level `basis` → `quartal` (4 Workshops pro Jahr)
- Service-Level `wachstum` → `quartal` (4 Workshops pro Jahr)
- Service-Level `vollservice` → `halbjaehrlich` (2 grosse Workshops plus monatliche Strategie-Calls; bei Vollservice braucht es weniger formelle Workshops, weil REACHX laufend strategisch aktiv ist)

### Schritt A.6: Vertragslaufzeit-Vorschlag

Default-Heuristik:

- Standard: 12 Monate
- Wenn Briefing 6 Monate / "kurzer Vertrag" / "Probelauf" → 6 Monate vorschlagen, ABER pruefen: wenn SEO im Top-3-Kanal-Mix oder Content > 30% Anteil → Auffaelligkeit `vertragslaufzeit_zu_kurz_fuer_ramp_up` markieren (SEO braucht 9+ Monate Ramp-up — siehe `synthese/forecast.md` Ramp-up-Annahmen)
- Wenn Forecast Best-Szenario sehr ambitioniert (Forecast-12-Monate-Aggregat > 3x heutige Marketing-Performance) und Setup-Phase gross → 24 Monate als Alternative vorschlagen (laengerer Investitions-Schutz fuer den Kunden)

### Schritt A.7: `synthese/retainer-konfiguration.md` nach Drive schreiben

Erzeuge das Phase-A-Schema lokal nach `reference/retainer-konfiguration-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "retainer-konfiguration.md" \
  /tmp/retainer-konfiguration.md "text/markdown"
```

Stratege editiert die Konfiguration direkt in der Drive-Web-UI und setzt `status: bestaetigt`.

Frontmatter:

```yaml
---
skill: 04-06-retainer-kalkulator
status: vorgeschlagen
basis_zentral:
  stundensaetze: reference/reachx-stundensaetze.md
  aufwands_bandbreiten: reference/aufwands-bandbreiten.md
basiert_auf:
  briefing: data/briefing.md
  kanal_chancen: synthese/kanal-chancen.md
  forecast: synthese/forecast.md
  plan_90_tage: synthese/90-tage-plan.md
generiert_am: ISO-8601
schema_version: "1.0"

service_level: wachstum
vertragslaufzeit_monate: 12

kanal_verantwortlichkeit:
  seo:
    reachx_anteil_prozent: 70
    kunde_anteil_prozent: 30
    skills: [strategie, content-briefing, reporting]
  sea:
    reachx_anteil_prozent: 100
    kunde_anteil_prozent: 0
    skills: [kampagnen-management, anzeigentexte, reporting]

reporting_frequenz: monatlich
strategie_workshop_frequenz: quartal

begruendung:
  service_level: "Briefing nennt 1-FTE-Inhouse-Marketing-Team, REACHX uebernimmt Strategie plus 2-3 Top-Kanaele operativ — wachstum passt."
  vertragslaufzeit: "12 Monate Standard, SEO braucht 9 Monate Ramp-up (siehe Forecast)."
  reporting_frequenz: "Monatliches Reporting plus Strategie-Call ist Mittelstand-Standard."

strategen_hinweise:
  - "Wenn Kunde im Gespraech SEA als Prio 1 nannte, Kanal-Verantwortlichkeit anpassen."
  - "Wenn Kunde kleines Budget pruefen will, service_level basis pruefen."

inputs_gefunden:
  - synthese/kanal-chancen.md
  - synthese/forecast.md
  - synthese/90-tage-plan.md
inputs_fehlen: []
---
```

Body erklaert pro Feld die Heuristik in Klartext und nennt konkret die Eingriffspunkte fuer den Strategen.

### Schritt A.8: Schluss-Format Phase A

```
✓ 04-06-retainer-kalkulator Phase A abgeschlossen.

Outputs (auf Drive):
- synthese/retainer-konfiguration.md — Projekt-Konfiguration (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Service-Level:             wachstum
- Vertragslaufzeit:          12 Monate
- Reporting-Frequenz:        monatlich
- Workshop-Frequenz:         quartal
- Kanal-Verantwortlichkeit:  REACHX-Anteil 60-80% bei Top-Kanaelen

⏸ Pflicht-Review durch den Strategen
Bitte pruefen: Service-Level (passt zur Kunden-Reife?), Vertragslaufzeit (passt zum Ramp-up des Top-Kanal-Mix?), Kanal-Verantwortlichkeit (passt zu dem, was der Kunde im Gespraech wollte?), Reporting- und Workshop-Frequenz.
Stundensaetze und Aufwands-Bandbreiten kommen aus den zentralen Reference-Dateien — bei agentur-weiten Aenderungen dort pflegen, nicht hier.
Nach Review: status: bestaetigt im Frontmatter setzen, dann laeuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text "$FOLDER_ID" "status.md"`):

```yaml
blockiert:
  - skill: 04-06-retainer-kalkulator (Phase B)
    wartet_auf: "Strategen-Review von synthese/retainer-konfiguration.md (auf Drive)"
```

---

## Phase B — Berechnung

### Schritt B.1: Schema-Validierung

Lies `synthese/retainer-konfiguration.md` aus Drive (`find_by_name(SYNTHESE_ID, "retainer-konfiguration.md")` → `read_text`). Pruefe:

1. `status: bestaetigt`? Sonst Abbruch
2. `service_level` ist `basis | wachstum | vollservice`?
3. `vertragslaufzeit_monate` ist 6 / 12 / 24?
4. `kanal_verantwortlichkeit` enthaelt mindestens die Top-3-Kanaele aus `kanal-chancen.md`?
5. Pro Kanal: `reachx_anteil_prozent + kunde_anteil_prozent = 100` (Toleranz +/- 2)?
6. `reporting_frequenz` und `strategie_workshop_frequenz` aus zulaessiger Wertemenge?

Bei Verletzung: konkrete Fehlermeldung mit Hinweis auf das fehlerhafte Feld.

### Schritt B.2: Existenz-Check Output

Wenn `synthese/retainer.md`, `synthese/retainer.xlsx` oder `reports/X-retainer.html` auf Drive bereits existieren (`drive.py find_by_name`): fragen (ueberschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Aufwand pro Kanal pro Monat — erste 3 Monate (Ramp-up plus 90-Tage-Plan-Massnahmen)

Pro Massnahme in `synthese/90-tage-plan.md`:

1. Mappe Massnahme → Massnahmen-Typ aus `reference/aufwands-bandbreiten.md` (z. B. "Content-Briefing", "Landingpage-Konzept", "Monatlicher SEO-Report")
2. Lies Aufwands-Bandbreite (Stunden min-max) aus zentraler Reference
3. Wende REACHX-Anteil aus `kanal_verantwortlichkeit` an: `reachx_stunden = stunden_aufwand * reachx_anteil_prozent / 100`
4. Mappe Massnahmen-Rolle (Strategie / SEO-Manager / SEA-Manager / Content-Manager / Designer / Developer) → Stundensatz aus `reference/reachx-stundensaetze.md`
5. Berechne `kosten_min` und `kosten_max` pro Massnahme

Pro Monat (M1, M2, M3) aggregieren:

- Verteile Massnahmen auf Monate gemaess `90-tage-plan.md` Timeline (Massnahmen ohne explizite Monat-Angabe gleichverteilen)
- Setup-Aufwand (initial-only Massnahmen wie Tracking-Setup, Kampagnen-Setup, Strategie-Workshop initial) **separat** ausweisen
- Laufender Aufwand M1-M3 = monatlich wiederkehrende Massnahmen (Reporting, laufende Kampagnen-Pflege)

### Schritt B.4: Laufender Aufwand Monate 4-12 (Skalierung plus Optimierung)

Aus dem zentralen `reference/aufwands-bandbreiten.md` Abschnitt 3 die **laufenden Aufwands-Bandbreiten** pro Kanal abrufen (z. B. "SEO laufend: 12-25h/Monat Content-Produktion plus 4-10h Technik-Pflege plus 3-6h Reporting"). Pro Kanal:

1. Wende `reachx_anteil_prozent` an
2. Wende Service-Level-Skalierung an:
   - `basis`: laufende operative Stunden mal 0.3 (Beratungs-Anteil)
   - `wachstum`: laufende operative Stunden mal 0.7
   - `vollservice`: laufende operative Stunden mal 1.0
3. Strategie-, Reporting- und Workshop-Stunden bleiben unveraendert (sind in jedem Service-Level Pflicht)
4. Reporting-Frequenz wirkt: `monatlich` = 12 Reports/Jahr, `quartal` = 4 Reports/Jahr (Stunden pro Report aus Reference)
5. Workshop-Frequenz wirkt: `quartal` = 4 Workshops, `halbjaehrlich` = 2

Pro Monat M4 bis M12 ein Aggregat in Stunden und EUR — analog zur Monats-Spalten-Logik im Forecast-Modell.

### Schritt B.5: Drei Retainer-Stufen mit Range pro Monat

Bilde drei Szenarien (analog zum Forecast):

- `konservativ` → nimmt die **untere Bandbreite** der Aufwands-Stunden plus moderate Effizienz-Annahmen (z. B. wenig Iterationen, schlanke Reports)
- `realistisch` → mittlere Bandbreite, branchen-typischer Aufwand
- `ambitioniert` → obere Bandbreite, hoher Optimierungs-Anspruch, mehr Tests, tiefere Reports

Pro Service-Level (basis, wachstum, vollservice) und pro Szenario (konservativ, realistisch, ambitioniert) eine **Monats-Preis-Range** und **Setup-Preis-Range** ausweisen. Ergebnis ist eine 3x3-Matrix.

**Pflicht-Bandbreite:** Im Output IMMER min/max ausweisen. Punktwerte sind verboten. Wenn konservativ = realistisch = ambitioniert: Validierungs-Fehler.

### Schritt B.6: ROI-Argumentation pro Service-Level pro Szenario

Pro Kombination (Service-Level x Szenario) berechnen:

```
gesamtkosten_12_monate = setup_kosten + monatlicher_aufwand * 12
                         (= setup_kosten + summe_monate_M1_bis_M12)

erwarteter_umsatz_12_monate = forecast_umsatz_aus_synthese_forecast.md (entsprechendes Szenario)
   wobei: konservativ → Worst-Szenario, realistisch → Real-Szenario, ambitioniert → Best-Szenario

roi_faktor = erwarteter_umsatz_12_monate / gesamtkosten_12_monate
roi_anteil_prozent = gesamtkosten_12_monate / erwarteter_umsatz_12_monate * 100
```

Bewertung (aus `reference/retainer-output-schema.md` Abschnitt 3):

- ROI-Faktor > 5x → stark
- ROI-Faktor 3-5x → solide
- ROI-Faktor 2-3x → grenzwertig
- ROI-Faktor < 2x → schwach (Auffaelligkeit moeglich, je nach Szenario)

### Schritt B.7: Break-Even-Monat pro Szenario

Pro Service-Level x Szenario den Monat ermitteln, ab dem der **kumulierte erwartete Umsatz-Beitrag** die **kumulierten Retainer-Kosten** uebersteigt.

```python
kumulierter_umsatz_m = sum(forecast_monatlich.umsatz[bis_monat_m])
kumulierte_kosten_m = setup_kosten + monatlicher_aufwand * m
break_even_monat = erster Monat m, wo kumulierter_umsatz_m >= kumulierte_kosten_m
```

Wenn Break-Even erst nach Monat 12: setze `break_even_monat = "nach M12"` und markiere Auffaelligkeit `roi_negativ_im_worst_case` falls das Worst-Szenario betroffen ist.

### Schritt B.8: Auffaelligkeiten (mindestens 5)

Pflicht-Pruefung aller Auffaelligkeits-Typen:

| Typ | Ausloeser |
|---|---|
| `retainer_uebersteigt_branchen_default` | Empfohlene Monats-Range deutlich (>1.5x) ueber branchen-typischen Retainer-Werten (Vergleichs-Range aus `reference/aufwands-bandbreiten.md` Abschnitt 5, branchen-Defaults) |
| `roi_negativ_im_worst_case` | Selbst das ambitionierte-Szenario-Best-Forecast-Mapping deckt den Retainer nicht im 12-Monats-Horizont (Break-Even nach M12 in mindestens 2 von 3 Szenarien) |
| `service_level_passt_nicht_zu_kunden_reife` | z. B. `vollservice` empfohlen, aber Kunde hat starkes Inhouse-Team (oder umgekehrt: `basis` empfohlen, aber Kunde hat kein Inhouse-Team) |
| `vertragslaufzeit_zu_kurz_fuer_ramp_up` | Vertragslaufzeit 6 Monate, aber SEO oder Content > 30% Stunden-Anteil (SEO braucht 9+ Monate Ramp-up gemaess Forecast-Annahmen) |
| `kosten_dominanz_einzelner_kanal` | Ein Kanal nimmt > 60% des Retainers ein (Klumpenrisiko in der Leistung — wenn dieser Kanal underperformt, kippt der ROI) |

Optional zusaetzlich (wenn anwendbar):

- `setup_aufwand_kritisch` — Setup > 50% des Jahres-Retainers
- `briefing_budget_indikation_ueberschritten` — Empfohlener Retainer-Preis-Min > Briefing-Budget-Indikation
- `briefing_budget_indikation_unterschritten` — Empfohlener Retainer-Preis-Max < Briefing-Budget-Indikation x 0.6
- `reporting_frequenz_passt_nicht` — Kunde hat woechentliche Calls gewuenscht, Service-Level basis sieht nur monatlich vor (Inkonsistenz)
- `stundensaetze_zentrale_version_alt` — `reachx-stundensaetze.md` aelter als 12 Monate (Pflege-Hinweis)

Mindest-Anzahl: 5 echte Auffaelligkeiten. Wenn weniger gegeben: methodische Hinweise ergaenzen (z. B. "Briefing fehlt — Budget-Realismus kann nicht geprueft werden, im Kunden-Gespraech klaeren").

### Schritt B.9: `synthese/retainer.md` und CSV nach Drive schreiben

Lokal generieren, dann nach Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "retainer.md" /tmp/retainer.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "retainer.csv" /tmp/retainer.csv "text/csv"
```

Folge `reference/retainer-output-schema.md` Abschnitt 1. Frontmatter komplett (Aggregat-Statistiken pro Service-Level pro Szenario, Empfehlungs-Konfidenz, Break-Even-Monate, ROI-Faktoren). Body strukturiert:

- Uebersicht (3-5 Saetze: Service-Level-Empfehlung, Preis-Range, ROI, Break-Even)
- 3x3-Matrix: Service-Level x Szenario mit Monats-Preis, Setup-Preis, Gesamtkosten-12-Monate, ROI-Faktor, Break-Even-Monat
- Pro Service-Level Detail-Sektion (Aufwand pro Kanal, Aufwand pro Monat M1-M12, Strategie-/Reporting-Stunden)
- ROI-Argumentation: Retainer-Kosten vs. Forecast-Umsatz-Beitrag pro Szenario
- Empfehlung des Skills (welches Service-Level fuer den Kunden) mit Begruendung und Konfidenz
- Auffaelligkeiten-Block (sortiert nach Relevanz)
- Datenbasis-Footer (Stundensaetze-Version, Bandbreiten-Version, Forecast-Stand, 90-Tage-Plan-Stand)

### Schritt B.10: `synthese/retainer.xlsx` lokal erzeugen, dann nach Drive hochladen

Generiere die Excel-Datei lokal (siehe Pseudocode), lade danach hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "retainer.xlsx" /tmp/retainer.xlsx \
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
```

Folge `reference/retainer-output-schema.md` Abschnitt 2. Pseudocode mit Pandas plus openpyxl (analog zum `04-04-forecast-modell`):

```python
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

wb = Workbook()

# Sheet 1: Uebersicht (3 Service-Level x 3 Szenarien Matrix)
ws_uebersicht = wb.active
ws_uebersicht.title = "Uebersicht"
# Zeilen: basis / wachstum / vollservice
# Spalten: konservativ-min, konservativ-max, realistisch-min, realistisch-max, ambitioniert-min, ambitioniert-max
# Plus: Setup-Range, Gesamtkosten-12M-Range, ROI-Faktor, Break-Even-Monat
# Empfohlenes Service-Level mit Highlight-Fill

# Sheet 2: Aufwands-Pivot (Massnahme x Monat x Stunden x Kostenposition)
ws_pivot = wb.create_sheet("Aufwands-Pivot")
# Zeilen: Massnahmen aus 90-Tage-Plan plus laufende M4-M12-Posten
# Spalten: M1, M2, M3, M4, ..., M12
# Pro Zelle: Stunden + EUR (zwei Zeilen pro Massnahme)
# Letzte Zeile: Summe pro Monat
# Letzte Spalte: Jahressumme

# Sheet 3: Aufschluesselung-Empfohlen (pro Skill-Typ)
ws_aufschluesselung = wb.create_sheet("Aufschluesselung")
# Pro Skill-Typ (Strategie, SEO-Manager, SEA-Manager, Content-Manager, Designer, Developer)
# Stunden monatlich, Stundensatz, Kosten/Monat, Kosten/Jahr

# Sheet 4: Setup-Phase
ws_setup = wb.create_sheet("Setup-Phase")
# Pro Setup-Block: Stunden, Stundensatz, Kosten — Aggregat unten

# Sheet 5: ROI-Vergleich (Retainer-Kosten vs Forecast-Beitrag pro Monat)
ws_roi = wb.create_sheet("ROI-Vergleich")
# Spalten: M1-M12, plus Aggregat
# Zeilen pro Szenario: kumulierte Kosten, kumulierter erwarteter Umsatz, Differenz, Break-Even-Marker

wb.save("synthese/retainer.xlsx")
```

**Conditional Formatting**:

- Empfohlenes Service-Level mit gelbem Hintergrund hervorheben
- ROI-Vergleich-Sheet: Differenz-Zellen rot wenn negativ, gruen wenn positiv
- Aufwands-Pivot: Color-Scale fuer Stunden-Verteilung (zur Erkennung von Kosten-Dominanzen)

**Fallback bei fehlenden Libraries:**

```python
try:
    from openpyxl import Workbook
    use_openpyxl = True
except ImportError:
    # CSV-Fallback: 5 CSVs schreiben statt Excel
    write_5_csv_files("synthese/")
    # Warnung im Output: "openpyxl nicht verfuegbar, CSV-Fallback geschrieben"
```

### Schritt B.11: HTML-Report `reports/X-retainer.html`

`_shell.html` aus Drive lesen (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), Platzhalter füllen, dann `drive.py upsert-text "$REPORTS_ID" "X-retainer.html" /tmp/report.html "text/html"`. Folge `reference/retainer-output-schema.md` Abschnitt 4. Sektionen:

- **Stat-Strip**: Empfohlenes Service-Level, Monats-Preis-Range (Realistisch), ROI-Faktor (Realistisch), Break-Even-Monat (Realistisch)
- **Drei Service-Level-Karten** nebeneinander:
  - `basis` / `wachstum` / `vollservice` als `details.skill`-Bloecke
  - Pro Karte: Monats-Preis-Range, Setup-Range, ROI-Faktor, Break-Even-Monat, Leistungs-Bullet-Points
  - Empfohlene Karte mit `.badge.stark` markiert
- **ROI-Chart** (inline-SVG): Pro Service-Level x Szenario eine Linie ueber 12 Monate, kumulierte Kosten vs. kumulierter Forecast-Beitrag, Break-Even-Marker als vertikale Linie
- **Aufschluesselung-Tabelle** pro Kanal (Stunden REACHX-Anteil, Stunden Kunde-Anteil, Kosten/Monat)
- **Setup-Phase-Tabelle**
- **Aufwands-Pivot-Visualisierung**: Heatmap-aehnliche Tabelle Massnahme x Monat mit Color-Coded-Stunden
- **Vertragsgestaltung-Sektion** (Laufzeit, Reporting, Workshops, Kuendigungsfristen)
- **Auffaelligkeiten-Block** als `.suggestion`-Bloecke mit Handlungs-Empfehlungen
- **Datenbasis-Footer** mit Versions-Angabe der zentralen Stundensaetze und Bandbreiten

Bestimme die Report-Nummer dynamisch aus den bereits existierenden Reports auf Drive (`drive.py list-children "$REPORTS_ID"`). Aktualisiere `reports/index.html` (aus Drive lesen, patchen, via `drive.py upsert-text "$REPORTS_ID" "index.html"` zurückschreiben).

### Schritt B.12: Dashboard-Update und status.md

Beide aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben.

- `04-06-retainer-kalkulator` in `schritte_done` (Phase B abgeschlossen)
- Aus `blockiert` entfernen
- Reports-Liste um den neuen Retainer-Report
- Stat-Strip aktualisieren (empfohlenes Service-Level, Monats-Preis-Range)
- `naechster_empfohlen`: `05-01-mta-slide-bausteine` (Synthese-Final-Skill)

### Schritt B.13: Standard-Schlussformat im Chat

```
✓ 04-06-retainer-kalkulator Phase B abgeschlossen.

Outputs (auf Drive):
- synthese/retainer.md — Drei Service-Level mit ROI und Break-Even
- synthese/retainer.csv — Flache Tabelle (Service-Level × Szenario × Monat × Kostenposition)
- synthese/retainer.xlsx — Aufwands-Pivot (Massnahme x Monat x Stunden x Kostenposition) plus Uebersicht plus ROI-Vergleich
- reports/X-retainer.html — Service-Level-Karten plus ROI-Chart
Status aktualisiert in: status.md

Retainer-Statistik:
- Empfohlenes Service-Level:    WACHSTUM (Konfidenz HOCH)
- Monats-Preis-Range (Real):    EUR X bis Y netto
- Setup-Range einmalig:         EUR X bis Y netto
- Gesamtkosten 12 Monate (Real): EUR X bis Y netto
- ROI-Faktor (Real):            FAKTOR x
- Break-Even-Monat (Real):      M

Auffaelligkeiten (sortiert nach Relevanz):
1. AUFFAELLIGKEIT-1
2. AUFFAELLIGKEIT-2
3. AUFFAELLIGKEIT-3

PFLICHT-BANDBREITE eingehalten — jede Zahl hat min/max-Range, drei Service-Level mal drei Szenarien.
Stundensaetze und Aufwands-Bandbreiten kommen aus zentralen Reference-Dateien (Version aus Frontmatter).

Naechste Schritte:
1. 05-01-mta-slide-bausteine — generiert die Slide-Bausteine fuer die Retainer-Folie aus diesem Output

Sag mir, welcher als naechster.
```

## Bundled Resources

- `reference/reachx-stundensaetze.md` — **Zentrale REACHX-Stundensaetze** pro Rolle (Strategie / SEO-Manager / SEA-Manager / Content-Manager / Designer / Developer) mit 2026-Default-Werten, Bandbreite und Override-Mechanik. Wird IMMER auch in Phase A gelesen.
- `reference/aufwands-bandbreiten.md` — **Zentrale Aufwands-Bandbreiten** pro Massnahmen-Typ (Setup-Massnahmen plus laufende Massnahmen plus Reporting plus Workshops). Plus branchen-typische Retainer-Vergleichs-Ranges fuer Auffaelligkeit `retainer_uebersteigt_branchen_default`.
- `reference/retainer-konfiguration-template.md` — Phase-A-Output-Format mit Service-Level-Definitionen, Default-Kanal-Verantwortlichkeit pro Service-Level und Begruendungs-Templates.
- `reference/retainer-output-schema.md` — Phase-B-Output-Format (Markdown-Frontmatter, Excel-Sheets-Struktur, HTML-Report-Sektionen, Validierungs-Regeln).

## Edge Cases

- **Forecast hat nur Real-Szenario** (Worst/Best fehlen) → Skill mappt konservativ = realistisch = ambitioniert auf Real und markiert Auffaelligkeit `forecast_szenarien_unvollstaendig`. Empfehlung: Forecast-Modell mit allen drei Szenarien neu laufen lassen, um den Retainer-ROI sauber zu berechnen.

- **90-Tage-Plan hat keine expliziten Aufwands-Stunden** → Skill mappt Massnahmen auf Massnahmen-Typen aus `aufwands-bandbreiten.md` und nimmt die mittlere Bandbreite. Auffaelligkeit `aufwand_aus_referenz_geschaetzt` mit Hinweis, dass exakter werden kann wenn 90-Tage-Plan Stunden ausweist.

- **Massnahme aus 90-Tage-Plan ohne klares Mapping** → Skill setzt konservative Default-Bandbreite (4-12 Stunden, STANDARD-Stundensatz), markiert mit Auffaelligkeit `massnahme_ohne_aufwand_mapping` und empfiehlt Schema-Aktualisierung in `aufwands-bandbreiten.md`.

- **Briefing fehlt komplett** → Skill arbeitet ohne Budget-Indikation. Auffaelligkeit `briefing_fehlt_budget_indikation_offen` plus Empfehlung in der Schluss-Sektion, dass die Empfehlung im Kunden-Gespraech auf Budget-Realismus geprueft werden muss.

- **Briefing nennt sehr hohes Budget (>20.000 EUR/Monat)** → Skill empfiehlt `vollservice` und schlaegt im Phase-A-Schema die obere Bandbreite an Aufwands-Werten vor. Auffaelligkeit `budget_oberhalb_standard_service_level` mit Empfehlung, ob ein Custom-Premium-Service-Level sinnvoller ist.

- **Briefing nennt sehr niedriges Budget (<2.500 EUR/Monat)** → Skill empfiehlt `basis`, weist im Output explizit aus, dass auch `basis` bei diesem Budget knapp wird, und schlaegt Schritt-fuer-Schritt-Modell vor (Beratungs-Stunden-Paket statt Retainer).

- **Stratege will Re-Run mit veraenderter Konfiguration** → Override-Argument "Konfiguration ueberarbeiten" → Skill loescht (mit Backup) den existierenden Phase-B-Output, laesst die Konfiguration auf `status: vorgeschlagen` zurueckfallen und bricht ab. Stratege editiert, bestaetigt, Skill laeuft Phase B neu.

- **openpyxl/pandas nicht verfuegbar** → Skill gibt Pip-Install-Anweisung im Chat aus und faellt auf 5 CSV-Files zurueck. Hinweis: in der MTA-Skill-Umgebung sind die Libraries Pflicht-Voraussetzung.

- **Zentrale Stundensaetze-Datei wurde aktualisiert nach Phase A** → Skill liest in Phase B die zentralen Reference-Dateien neu (kein Cache). Wenn Aenderung relevant: Auffaelligkeit `stundensaetze_zwischen_phasen_geaendert` mit Empfehlung Phase A erneut zu durchlaufen.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B laeuft niemals ohne `status: bestaetigt` in Phase A
- **Stundensaetze und Aufwands-Bandbreiten leben zentral** in `reference/reachx-stundensaetze.md` und `reference/aufwands-bandbreiten.md` im Skill-Ordner (NICHT auf Drive) — niemals projekt-spezifisch ueberschreiben (Aenderungen wirken agentur-weit per Skill-Versionierung)
- **Pflicht-Bandbreite** fuer alle Preise und Stunden — niemals Punktwert. Drei Szenarien (konservativ / realistisch / ambitioniert), niemals worst = real = best
- Projektspezifische Outputs leben auf Google Drive in `synthese/` und `reports/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter fuer Aggregat, Excel als zusaetzliches Verkaufs-Asset
- HTML-Report aus `reports/_shell.html` (aus Drive geladen) mit drei Service-Level-Karten plus ROI-Chart
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (aus Drive lesen, patchen, upsert)
- **Excel-Aufwands-Pivot ist das strategische Haupt-Artefakt** — Massnahme mal Monat mal Stunden mal Kostenposition, eine Tabelle fuer das Kunden-Gespraech
- **Versionierung der zentralen Reference-Dateien** im Frontmatter dokumentieren — pro Retainer-Output sichtbar, welche Stundensatz-Version verwendet wurde
