---
name: 04-05-90-tage-plan
description: Generiert eine konkrete 90-Tage-Roadmap in drei Monats-Phasen (Monat 1 Setup, Monat 2 Skalierung, Monat 3 Optimierung). Liest synthese/forecast.md, synthese/kanal-chancen.md, audits/seo-cluster-zusammenfassung.md (Sweet-Spot-Cluster), audits/web-tech-tracking.md und data/briefing.md und leitet pro Top-Kanal konkrete Massnahmen mit Verantwortlichkeit (REACHX / Kunde / Hybrid), Stunden-Range, Voraussetzungen, Meilenstein und Priorisierung (Quick-Win / Foundation / Long-Term) ab. Outputs sind synthese/90-tage-plan.md, synthese/90-tage-plan.csv und reports/X-90-tage.html mit Gantt-aehnlicher Inline-SVG. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext eine 90-Tage-Roadmap, Massnahmen-Plan oder Action-Plan braucht - auch bei Phrasen wie "90-Tage-Plan", "Roadmap erstellen", "Massnahmen-Plan", "Action-Plan", "Quick-Wins planen", "was machen wir in den naechsten 3 Monaten", "Channel-Setup-Plan", "Meilensteine festlegen". Setzt 04-04-forecast-modell und 04-02-kanal-chancen-analyse voraus.
---

# 90-Tage-Plan-Generator

Vierter Synthese-Skill in Stufe 4 — der **Uebergang von der Analyse in die Umsetzung**. Verdichtet die Top-Kanaele aus `04-02-kanal-chancen-analyse`, die Spend-/Ramp-up-Annahmen aus `04-04-forecast-modell` und die Sweet-Spot-Cluster aus `03-03-seo-keyword-kategorisierung` zu einer **konkreten 90-Tage-Roadmap** in drei Monats-Phasen mit Verantwortlichkeiten, Aufwand-Bandbreiten und Meilenstein-Indikatoren.

**Kein Schema-vor-Lauf**: Massnahmen-Inhalte sind aus den Audit-Daten ableitbar und folgen den festen REACHX-Standard-Templates in `reference/massnahmen-bibliothek.md`. Kein kundenspezifisches Schema noetig.

Drei Output-Ebenen:

1. **Markdown-Roadmap** `synthese/90-tage-plan.md` — strukturierte Massnahmen-Tabelle pro Monat plus Aggregat (Gesamt-Aufwand, Verantwortlichkeits-Verteilung, Prio-Verteilung), strategische Story
2. **Massnahmen-CSV** `synthese/90-tage-plan.csv` — eine Zeile pro Massnahme mit allen Feldern (Roh-Tabelle fuer CSV-Konsumenten wie Asana, Trello, Notion)
3. **HTML-Report** `reports/X-90-tage.html` — Gantt-aehnliche Inline-SVG-Visualisierung mit drei Monats-Spalten, Massnahmen-Zeilen, Farbcodierung nach Prioritaet

Die Nummer im Report-Dateinamen (`X`) ergibt sich aus der Workflow-Reihenfolge im jeweiligen Projekt (typisch `12` oder `13` direkt nach `04-04-forecast-modell`).

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Wann triggern

- "90-Tage-Plan erstellen"
- "Roadmap ableiten"
- "Massnahmen-Plan generieren"
- "Action-Plan fuer den Kunden"
- "Quick-Wins planen"
- "Was machen wir in den naechsten 3 Monaten"
- "Channel-Setup-Plan ableiten"
- "Meilensteine festlegen"
- "Umsetzungs-Roadmap bauen"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`, `status.md` vorhanden
- **`04-04-forecast-modell` gelaufen** → `synthese/forecast.md` fuer Spend-/Ramp-up-/Ziel-Annahmen. Pflicht-Input. Ohne diesen Skill bricht der Lauf ab.
- **`04-02-kanal-chancen-analyse` gelaufen** → `synthese/kanal-chancen.md` fuer die Top-Kanaele und Auffaelligkeiten. Pflicht-Input.
- Empfohlen: `audits/seo-cluster-zusammenfassung.md` — Sweet-Spot-Cluster werden direkt zu Quick-Wins
- Empfohlen: `audits/web-tech-tracking.md` — fuer Tech-Voraussetzungen (Tracking, Pixel, Schema-Markup, Pagespeed)
- Empfohlen: `data/briefing.md` — fuer Kunden-Ziele, Team-Setup und Verantwortlichkeits-Defaults

## Ablauf

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Drive-Bootstrap:

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

Lies `status.md` aus Drive.

**Pflicht-Input-Check** (via `drive.py find_by_name`): Existieren `synthese/forecast.md` und `synthese/kanal-chancen.md` auf Drive?

Wenn `kanal-chancen.md` fehlt:

```
✗ 04-02-kanal-chancen-analyse muss zuerst laufen.
Datei synthese/kanal-chancen.md fehlt.
```

Wenn `forecast.md` fehlt:

```
✗ 04-04-forecast-modell muss zuerst laufen.
Datei synthese/forecast.md fehlt.
```

### Schritt 2: Inputs lesen aus Drive

Lies und parse (jeweils `find_by_name` + `read_text` im passenden Sub-Folder):

- **`synthese/kanal-chancen.md`** Frontmatter:
  - `top_3_empfehlungen[]` → die Treiber-Kanaele mit `kanal_slug`, `kanal_anzeigename`, `chancen_score`, `naechste_aktion`, `konkrete_argumente`
  - `kanal_ranking[]` → Rang 4-6 als sekundaere Kanaele (fuer Monat-3-Long-Term-Massnahmen)
  - `auffaelligkeiten[]` mit `typ: quick_win_kanal` → direkte Quick-Win-Kandidaten
  - `auffaelligkeiten[]` mit `typ: kunden_reife_engpass` → Foundation-Massnahmen
- **`synthese/forecast.md`** Frontmatter:
  - Ramp-up-Annahmen pro Kanal (z. B. SEO 6 Monate, SEA 4 Wochen, Meta-Ads 6 Wochen)
  - Spend-Annahmen pro Kanal pro Monat (fuer Aufwands-Plausibilisierung)
  - Real-Szenario-Ziele (Ergebnis-Bezug fuer Meilensteine)
- **`audits/seo-cluster-zusammenfassung.md`** (optional, empfohlen) Frontmatter:
  - `auffaelligkeiten[]` mit `typ: sweet_spot_cluster` → SEO-Quick-Win-Kandidaten (Content-Hub fuer Monat 1)
  - `cluster_aggregat[]` Top-10 nach `cluster_score` → Long-Term-Content-Themen
- **`audits/web-tech-tracking.md`** (optional) Frontmatter:
  - `auffaelligkeiten[]` mit `typ: tracking_luecke | pixel_fehlt | cwv_kritisch | schema_markup_fehlt` → Foundation-Massnahmen fuer Monat 1
  - `tech_stack` → welche Tools vorhanden vs. fehlend
- **`data/briefing.md`** (optional) Frontmatter:
  - `team_setup` → Verantwortlichkeits-Defaults (z. B. "Kunde hat eigenes Inhouse-Team" → mehr Massnahmen Hybrid)
  - `kunden_ziele` → fuer Meilenstein-Formulierung

### Schritt 3: Verantwortlichkeits-Default-Logik anwenden

Aus dem **REACHX-Service-Modell** (siehe `reference/massnahmen-bibliothek.md`) ergeben sich Default-Verantwortlichkeiten pro Massnahmen-Typ:

- **REACHX**: Strategie, Briefing-Erstellung, Konzept-Phasen, Reporting-Auswertung, Channel-Spezialist-Arbeit (SEA-Konto-Optimierung, SEO-Onpage, Ads-Creatives)
- **Kunde**: Asset-Bereitstellung (Logos, Bilder, Markenrichtlinien), Inhaltliche Freigaben, Tracking-Implementierung auf der Website (wenn Inhouse-Dev), Login-Zugaenge, Texte-Recherche fuer Fachthemen
- **Hybrid**: Content-Produktion (REACHX Briefing + Kunde Fach-Input), Performance-Reviews (REACHX Auswertung + Kunde Entscheidung), Tracking-Setup (REACHX Konzept + Kunde Umsetzung)

Diese Defaults werden in `reference/massnahmen-bibliothek.md` pro Standard-Massnahme festgehalten. Override aus `data/briefing.md`-Team-Setup: bei "Kunde hat kein Inhouse-Marketing-Team" → mehr Massnahmen verschieben zu REACHX, bei "Kunde hat starkes Inhouse-Team" → mehr Hybrid.

### Schritt 4: Massnahmen pro Monat ableiten

**Monat 1 — Setup-Phase** (typisch 8-15 Massnahmen):

Quellen-Heuristik:

1. **Tech-Voraussetzungen aus `audits/web-tech-tracking.md`** (Tracking-Setup, Pixel-Installation, Consent-Verifikation, Schema-Markup) → Foundation-Massnahmen, blockieren oft andere Massnahmen
2. **Auffaelligkeiten mit `typ: kunden_reife_engpass`** → Foundation
3. **Sweet-Spot-Cluster aus `seo-cluster-zusammenfassung.md`** → erste Content-Briefings (Quick-Win)
4. **Briefing-Luecken** (wenn `briefing_fit_konfidenz: niedrig` in `kanal-chancen.md`) → Klarungs-Workshop mit Kunde (Hybrid)
5. **Konto-/Account-Einrichtungen** fuer Top-3-Kanaele (z. B. Google Ads-Konto, Meta-Business-Manager, LinkedIn-Campaign-Manager) → Foundation
6. **Content-Inventur-Ergebnisse umsetzen** (Stale-Content-Liste aus `audits/content-inventur.md` falls vorhanden)

**Monat 2 — Skalierung** (typisch 6-12 Massnahmen):

Quellen-Heuristik:

1. **`naechste_aktion` aus Top-3 in `kanal-chancen.md`** → erste Kampagnen live
2. **SEO-Content-Hubs aus Sweet-Spot-Cluster** → erste Veroeffentlichungen
3. **Ads-Kampagnen-Launches** (basierend auf Forecast-Spend-Annahmen)
4. **Audience-Tests** (zwei bis drei Audience-Varianten pro Paid-Kanal)
5. **Erste Performance-Review** Ende Monat 2 (Hybrid: REACHX Auswertung + Kunde Entscheidung)

**Monat 3 — Optimierung** (typisch 5-10 Massnahmen):

Quellen-Heuristik:

1. **Daten-Auswertung der Monat-2-Tests** → Skalierung der Gewinner
2. **Erweiterung auf zweite Cluster-Themen** (Long-Term aus `cluster_aggregat`)
3. **Reporting-Aufbau** (Dashboard, KPI-Set fuer Retainer-Phase)
4. **Quartals-Strategie-Review** (Hybrid, Stratege + Kunde) → Vorbereitung fuer Retainer-Phase
5. **Langfristige Initiativen anstossen** (z. B. Email-Marketing-Aufbau, CRO-Test-Pipeline, Video-Strategie)

### Schritt 5: Pro Massnahme die Pflicht-Felder fuellen

Siehe `reference/plan-output-schema.md` fuer das vollstaendige Schema. Kurz:

- `massnahme_id` — `m001`, `m002`, ... (durchnummeriert ueber alle Monate)
- `monat` — `1 | 2 | 3`
- `titel` — kurz, aktivisch (z. B. "GA4-Tracking auf der Hauptdomain einrichten")
- `beschreibung` — 1-2 Saetze
- `zielsetzung` — 1 Satz, was die Massnahme erreichen soll
- `kanal_slug` — Bezug zum Kanal aus `kanal-chancen.md` (`seo`, `sea`, `meta-ads`, `linkedin-ads`, `local-seo`, `content`, `instagram-organisch`, `tiktok-organisch`, `linkedin-organisch`, `pinterest-organisch`, `youtube-organisch`, `website-cro`, `tracking-cross` fuer kanal-uebergreifend)
- `verantwortlich` — `REACHX | Kunde | Hybrid` (bei Hybrid: `verantwortlich_details` mit Rollen-Aufteilung)
- `aufwand_range_stunden` — Bandbreite mit Bindestrich (z. B. `8-16`). **Niemals Punktschaetzung**
- `voraussetzungen` — Liste der `massnahme_id`s oder Tech-Voraussetzungen (z. B. "GA4 muss vorher live sein", `[m001]`)
- `meilenstein_indikator` — woran man erkennt, dass die Massnahme erfolgreich ist (z. B. "GA4 zeigt mindestens 7 Tage saubere Daten fuer Top-10-Landingpages")
- `prioritaet` — `Quick-Win | Foundation | Long-Term`
- `quelle` — woher die Massnahme stammt (`auffaelligkeit:typ`, `top3_aktion`, `bibliothek:slug`, `sweet_spot_cluster:name`, `tech_voraussetzung`, `best_practice`)

### Schritt 6: Prioritaets-Logik

- **Quick-Win**: Aufwand 4-16 Stunden, sichtbar innerhalb von 30 Tagen, klarer Effekt — typisch SEO-Sweet-Spot-Cluster mit niedriger Difficulty, SEA-Conquest-Kampagne fuer Brand-Begriffe, Pagespeed-Quick-Fixes, GMB-Profil-Optimierung
- **Foundation**: Aufwand 8-40 Stunden, blockiert oft andere Massnahmen, kein sofortiger Effekt — typisch Tracking-Setup, Account-Einrichtungen, Briefing-Workshops, Schema-Markup
- **Long-Term**: Aufwand 12-60+ Stunden, Effekt erst nach mehreren Monaten — typisch Content-Hub-Aufbau fuer schwierige Cluster, Email-Marketing-Funnel, CRO-Test-Pipeline, Video-Strategie

Die Aufwands-Bandbreiten pro Standard-Massnahme sind in `reference/massnahmen-bibliothek.md` festgehalten.

### Schritt 7: Aggregat-Berechnung

Berechne fuer das Aggregat im Output:

- **Gesamt-Aufwand-Range**: Summe aller Min-Werte bis Summe aller Max-Werte (z. B. `180-340 Stunden`)
- **Aufwand pro Monat**: Min/Max pro Monat
- **Verantwortlichkeits-Verteilung**: Prozent-Anteile (z. B. `60% REACHX, 25% Hybrid, 15% Kunde`)
- **Prioritaets-Verteilung**: Prozent-Anteile (z. B. `35% Quick-Win, 40% Foundation, 25% Long-Term`)
- **Kanal-Verteilung**: Anzahl Massnahmen pro Kanal
- **Plan-Team-Kapazitaets-Schaetzung**: aus `data/briefing.md` Team-Setup ableiten (falls vorhanden) — z. B. "Kunde mit 1 Marketing-Verantwortlicher → typisch 40-60 Std/Monat verfuegbar fuer MTA-Umsetzung". Wenn Gesamt-Aufwand-Range Min > 3×Team-Kapazitaet: Auffaelligkeit `aufwand_uebersteigt_team_kapazitaet`.

### Schritt 8: Auffaelligkeiten identifizieren

Mindestens **6 Auffaelligkeiten** ueber den Plan ableiten:

- `aufwand_uebersteigt_team_kapazitaet` — Gesamt-Stunden-Range-Min > 3× geschaetzte Team-Kapazitaet aus Briefing (oder ohne Briefing: Gesamt-Min > 240 Std als pragmatische Schwelle)
- `kunden_verantwortung_dominiert` — mehr als 60% der Massnahmen liegen beim Kunden — Risiko, dass die Agentur zu wenig Hands-on wird, Plan-Wirkung haengt zu stark am Kunden-Zeitbudget
- `setup_phase_zu_lang` — Monat-1-Setup-Aufwand-Mitte > 50% der 90-Tage-Gesamt-Aufwand-Mitte — zu viel Foundation, zu wenig Ergebnis im Quartal
- `keine_quick_wins_in_monat_1` — alle Massnahmen in Monat 1 sind Foundation oder Long-Term — Erwartungs-Management mit Kunden noetig, weil 30 Tage kein sichtbarer Effekt
- `tech_voraussetzungen_fehlen` — Massnahme braucht Tracking-/Tool-Setup, das laut `web-tech-tracking.md` nicht vorhanden ist — eine zusaetzliche Foundation-Massnahme als Voraussetzung im Plan eingeplant
- `kanal_im_plan_nicht_im_chancen_top5` — Massnahme(n) fuer Kanal mit `rang > 5` in `kanal-chancen.md` — Plausibilitaets-Check: warum bekommt ein niedrig-bewerteter Kanal Massnahmen? (kann legitim sein, muss aber begruendet werden)

Optional weitere:

- `kein_reporting_setup` — keine Reporting-Massnahme im Plan, obwohl Plan auf Daten-Auswertung in Monat 3 setzt
- `forecast_widerspruch` — Plan-Wirkung (Meilensteine) und Forecast-Annahmen widersprechen sich (z. B. Plan rechnet mit Effekt Monat 2 fuer Kanal mit Ramp-up 6 Monate)
- `quick_wins_dominant` — ueber 60% der Massnahmen sind Quick-Win, langfristiger Aufbau fehlt — strategische Luecke

Wenn weniger als 6 echte Auffaelligkeiten ableitbar: mit methodischen Hinweisen ergaenzen (z. B. "Datenbasis duenn — Plan ist Best-Guess auf vorhandenem Stand").

### Schritt 9: Strategische Story formulieren

Im Body der `90-tage-plan.md` ein narrativer Abschnitt (3-5 Saetze): Was sind die **groessten Hebel im 90-Tage-Fenster**? Was muss der Kunde freigeben, damit der Plan traegt? Wo sind die Risiken? Was ist die erwartete Tortenstueck-Verteilung zwischen REACHX und Kunde?

Diese Story ist die Vorbereitung fuer die MTA-Slides (Roadmap-Slide vor der Retainer-Empfehlung).

### Schritt 10: Output schreiben — Markdown plus CSV nach Drive

Erzeuge `synthese/90-tage-plan.md` und `synthese/90-tage-plan.csv` lokal nach dem Schema in `reference/plan-output-schema.md`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "90-tage-plan.md" /tmp/90-tage-plan.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "90-tage-plan.csv" /tmp/90-tage-plan.csv "text/csv"
```

**Validierungs-Regeln vor dem Schreiben**:

1. Mindestens 4 Massnahmen pro Monat
2. Jede Massnahme hat alle Pflicht-Felder (siehe Schema)
3. Jede Massnahme hat `aufwand_range_stunden` als Bandbreite mit Bindestrich (z. B. `8-16`), niemals nur eine Zahl
4. Mindestens 1 Foundation-Massnahme in Monat 1
5. Mindestens 1 Quick-Win-Massnahme insgesamt
6. Mindestens 6 Auffaelligkeiten
7. Voraussetzungs-Graph zyklenfrei (keine Massnahme haengt indirekt von sich selbst ab)
8. Aufwand-Range ist immer `min-max` mit `min <= max`, `min >= 1`
9. `verantwortlich` ist einer der 3 erlaubten Werte
10. `prioritaet` ist einer der 3 erlaubten Werte

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

### Schritt 11: HTML-Report mit Gantt-aehnlicher SVG-Visualisierung

Lies `_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`). Ersetze Platzhalter (siehe `contracts.md` Abschnitt 7). Inhalt fuer `{{MAIN_CONTENT}}`:

- **Stat-Strip**: Anzahl Massnahmen, Gesamt-Aufwand-Range, Verantwortlichkeits-Verteilung, Prio-Verteilung
- **Gantt-aehnliche SVG-Timeline** (Inline-SVG, keine externen JS-Libs):
  - Drei Monats-Spalten (Monat 1 / Monat 2 / Monat 3) als hellgraue Boxen
  - Pro Massnahme eine Zeile mit Balken in der entsprechenden Monats-Spalte
  - Farbcodierung Balken nach `prioritaet`: Quick-Win = REACHX-Sunrise-Red `#ec644a`, Foundation = REACHX-Night-Sky `#000a14`, Long-Term = Mittel-Grau
  - Balken-Laenge proportional zur Aufwand-Range-Mitte (visueller Hinweis)
  - Voraussetzungs-Pfeile zwischen abhaengigen Massnahmen (duenne Linien)
- **Massnahmen-Tabelle pro Monat**: drei `table.data` (eine pro Monat) mit `titel`, `verantwortlich`, `aufwand`, `prio`, `meilenstein`
- **Aggregat-Karten**: Gesamt-Aufwand, Verantwortlichkeits-Verteilung als Donut-SVG, Prio-Verteilung als Bar-SVG
- **Auffaelligkeiten**: aufklappbare `details`-Bloecke, gruppiert nach Relevanz
- **Strategische Story**: prominente `.summary-card` am Ende
- **Datenbasis-Footer**: welche Inputs zur Verfuegung standen

Schreibe nach Drive via `drive.py upsert-text "$REPORTS_ID" "X-90-tage.html" /tmp/report.html "text/html"`. Die Nummer `X` ergibt sich aus der Reihenfolge im Workflow (typisch `12` oder `13`). Pruefe vorhandene Reports auf Drive via `drive.py list-children "$REPORTS_ID"` und nimm die naechste freie Nummer.

Aktualisiere `reports/index.html` analog: aus Drive lesen, patchen, via `drive.py upsert-text "$REPORTS_ID" "index.html"` zurückschreiben (siehe `contracts.md` Abschnitt 7.3).

### Schritt 12: Status-Update

Folge `contracts.md` Abschnitt 3. `status.md` aus Drive lesen, patchen, via `drive.py upsert-text "$FOLDER_ID" "status.md" ... "text/markdown"` zurückschreiben:

- `04-05-90-tage-plan` in `schritte_done` aufnehmen, aus `schritte_offen` entfernen
- Body-Eintrag unter "✓ Erledigt" mit Output-Pfaden und Hinweis auf Massnahmen-Anzahl und Gesamt-Aufwand-Range
- `naechster_empfohlen`: `04-06-retainer-kalkulator` (wenn Forecast und Plan beide vorhanden) oder `05-01-mta-slide-bausteine` (wenn alle Synthese-Skills durch sind)

### Schritt 13: Schluss-Format im Chat

Standard-Schluss nach `contracts.md` Abschnitt 6. Bei Auffaelligkeit `aufwand_uebersteigt_team_kapazitaet` zusaetzlich:

```
HINWEIS: Plan-Aufwand uebersteigt geschaetzte Kunden-Team-Kapazitaet.
Empfohlen: Plan mit Kunde reviewen, Massnahmen priorisieren oder Retainer-Stunden hochrechnen.
```

## Modi

- **Voll**: forecast + kanal-chancen + alle Audits vorhanden — Default, alle Effekt-Schaetzungen mit hoher Konfidenz, vollstaendige Verantwortlichkeits-Verteilung
- **Reduced**: forecast + kanal-chancen vorhanden, aber Audits nur teilweise — Plan laeuft, aber einige Tech-Voraussetzungen werden generisch geschaetzt, Konfidenz mittel
- **Duenn**: kanal-chancen war im `duenn`-Modus — Plan dokumentiert duenne Basis, einige Massnahmen mit Konfidenz niedrig

## Edge Cases

- **Kunde hat starke Tracking-Luecke laut `web-tech-tracking.md`**: Tracking-Setup wird automatisch zur einzigen Monat-1-Prioritaet, alle anderen Channel-Massnahmen warten auf Tracking. Auffaelligkeit `tech_voraussetzungen_fehlen`.
- **Briefing-Luecken markiert**: Wenn `briefing_fit_konfidenz: niedrig` in `kanal-chancen.md`, Briefing-Klaerungs-Workshop in Monat 1 mit `verantwortlich: Hybrid`.
- **Top-Kanal ist Meta-Ads, aber Werbekonto nicht vorhanden**: Werbekonto-Setup als Monat-1-Foundation mit `verantwortlich: Hybrid`, Voraussetzungs-Markierung fuer alle weiteren Meta-Massnahmen.
- **Plan hat ueber 35 Massnahmen**: Warnung im Output — entweder weniger Kanaele priorisieren oder einige Massnahmen ins 91-180-Tage-Backlog verschieben (separater Backlog wird nicht geschrieben, nur als Hinweis).
- **Forecast-Annahmen widersprechen dem Plan**: wenn z. B. Forecast einen Quick-Win-Kanal mit 6 Monaten Ramp-up annimmt, explizit als `forecast_widerspruch`-Auffaelligkeit markieren.
- **`audits/web-tech-tracking.md` fehlt auf Drive**: Default-Annahme "Tracking ist nicht verifiziert" → automatisch eine Tracking-Verifikations-Massnahme in Monat 1 einplanen, Hinweis in Datenbasis-Footer.
- **`reports/_shell.html` fehlt auf Drive**: Hinweis im Schluss-Format, HTML-Report wird trotzdem als minimaler Plain-HTML-Stub geschrieben und hochgeladen.

## Reference-Dateien

- `reference/massnahmen-bibliothek.md` — Standard-Massnahmen pro Kanal mit Default-Stunden-Range, Voraussetzungen, Meilenstein-Indikatoren, Default-Verantwortlichkeit (z. B. "SEO: Sitemap einreichen, Top-10-Sweet-Spot-Cluster mit Content-Hubs adressieren, Schema-Markup einbauen"). Diese Bibliothek ist die zentrale Quelle fuer alle Standard-Massnahmen — kunden-spezifische Anpassungen erfolgen in den Aufwands-Bandbreiten und der Kanal-Auswahl.
- `reference/plan-output-schema.md` — exakte Definition des Markdown-Frontmatter, des CSV-Schemas, der HTML-Sektionen, der SVG-Gantt-Struktur und der Validierungs-Regeln.
