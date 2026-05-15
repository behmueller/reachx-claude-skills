---
name: 04-03-ziele-aus-potenzialen
description: Leitet im MTA-Kontext realistische Ziel-Bandbreiten aus Markt-Potenzialen ab, wenn der Kunde keine bezifferten KPIs nennt (Standard-Fall). Schema-vor-Lauf-Pattern - Phase A schlägt das Annahmen-Set vor (Branchen-CR pro Kanal, AOV/LTV, Lead-zu-Kunde-Konversion, Ramp-up, Quelle pro Annahme), Phase B leitet pro Top-Kanal aus kanal-chancen.md drei Szenario-Bandbreiten ab (konservativ, realistisch, ambitioniert) plus Gesamt-Aggregat. Output ist synthese/ziele.md plus synthese/ziele-aufschluesselung.csv. Pflicht-Bandbreite, niemals Punktschaetzungen. Quelle pro Zahl explizit verlinkt. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Ziele aus Potenzialen ableiten will - auch bei Phrasen wie "Ziele ableiten", "Ziel-Bandbreiten", "Potenzial-Ziele", "konservativ realistisch ambitioniert", "Marketing-Beitrag schaetzen", "Umsatz-Bandbreite ableiten", "Bottom-up-Forecast", "Ziele aus Audits". Setzt voraus, dass 04-02-kanal-chancen-analyse gelaufen ist - bricht sonst ab.
---

# Ziele aus Potenzialen ableiten

Dritter Skill in Stufe 4 (Synthese). **Schema-vor-Lauf-Skill** (siehe `contracts.md` Abschnitt 8). Bottom-up-Brücke zwischen `04-02-kanal-chancen-analyse` und `04-04-forecast-modell`. Wird automatisch relevant, wenn der Kunde im Briefing keine bezifferten KPIs genannt hat (Standard-Fall, siehe Architektur-Entscheidung 14 im Plan) — kann aber auch als Plausibilitäts-Check über Briefing-Zielen laufen.

**Kernregel: Pflicht-Bandbreite, niemals Punktschätzungen** (siehe Architektur-Entscheidung 10 im Plan). Jede Zahl im Output hat eine verlinkte Annahmen-Quelle, damit der Stratege im Kunden-Gespräch jede Zahl bis zur Annahme zurückverfolgen kann.

**Drei Output-Ebenen:**

1. **Annahmen-Schema (Phase A)** `synthese/ziel-annahmen-schema.md` — Konversionsraten-Bandbreiten pro Kanal, AOV/LTV-Annahme, Lead-zu-Kunde-Stufen für B2B, Ramp-up-Phasen, Quelle pro Annahme
2. **Aggregat-Markdown (Phase B)** `synthese/ziele.md` — pro Top-Kanal drei Szenario-Bandbreiten plus Gesamt-Aggregat, Annahmen-Tabelle, optionaler Plausibilitäts-Check gegen Briefing
3. **Roh-CSV (Phase B)** `synthese/ziele-aufschluesselung.csv` — Kanal × Szenario × Metrik als flache Tabelle für `04-04-forecast-modell`
4. **HTML-Report** `reports/X-ziele.html` — Szenario-Karten plus Annahmen-Übersicht

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

- "Ziele ableiten"
- "Ziel-Bandbreiten"
- "Potenzial-Ziele"
- "konservativ realistisch ambitioniert"
- "Marketing-Beitrag schätzen"
- "Umsatz-Bandbreite ableiten"
- "Bottom-up-Forecast"
- "Ziele aus Audits"
- "wieviel Umsatz kann der Kunde erwarten"
- "Plausibilitäts-Check über die Kunden-Ziele"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`, `status.md`
- **`04-02-kanal-chancen-analyse` gelaufen** → `synthese/kanal-chancen.md` plus `synthese/kanal-chancen.csv` vorhanden — sonst Abbruch mit Hinweis
- Empfohlen: mindestens 2-3 Audit-Skills aus Stufe 3 mit Volumen-Daten (SEO-Cluster, GMB, Ads-Spend-Schätzungen) — sonst Annahmen-Schema fast komplett aus Branchen-Defaults
- Empfohlen: `data/briefing.md` (für Plausibilitäts-Check und ggf. Kunden-AOV)
- Empfohlen: `data/kunde.md` (für Portfolio + AOV-Hinweise + B2B/B2C-Einordnung)

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `synthese/ziel-annahmen-schema.md` existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B läuft.

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

Schema und Outputs liegen im `synthese/`-Sub-Folder auf Drive:

```
1. Existiert synthese/ziel-annahmen-schema.md auf Drive?
   - Nein → Phase A (Schema generieren)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt → Phase B (Ziel-Ableitung)
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert synthese/ziele.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen (überschreiben / Backup-und-neu / abbrechen)
```

---

## Phase A — Annahmen-Schema

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Lies `status.md` aus Drive (`find_by_name(FOLDER_ID, "status.md")` → `read_text`).

**Hartes Voraussetzungs-Gate:** `synthese/kanal-chancen.md` muss auf Drive existieren (`find_by_name(SYNTHESE_ID, "kanal-chancen.md")`). Wenn nicht:

```
✗ synthese/kanal-chancen.md nicht gefunden.
Bitte zuerst 04-02-kanal-chancen-analyse laufen lassen — der Skill identifiziert die Top-Kanäle, aus denen wir Ziele ableiten.
```

Lies `synthese/kanal-chancen.md` aus Drive (Frontmatter), insbesondere:

- `top_3_empfehlungen[]` — für welche Kanäle wir Ziele ableiten
- `kanal_ranking[i].potenzial_score` plus `audit_inputs_verfuegbar` — Volumen-Basis
- `branchen_typ` — für Default-Konversionsraten
- `audit_coverage.modus` — voll | reduced | duenn

Lies optional aus Drive (jeweils `find_by_name` + `read_text` im passenden Sub-Folder):

- `data/briefing.md` — Frontmatter (KPIs vom Kunden? bezifferte Ziele? Felder `unklar_aus_transkript: true`?), Body (Ziel-Aussagen, Timeline-Aussagen)
- `data/kunde.md` — Portfolio (AOV-Hinweise: Preis-Range, Subscription-Modell, Order-Größe), B2B/B2C-Hypothese
- `audits/seo-cluster-zusammenfassung.md`, `audits/seo-keyword-cluster.csv` — kumuliertes Volumen pro Cluster (für SEO-Ziel-Berechnung)
- `audits/google-ads.md`, `audits/meta-ads.md`, `audits/linkedin-ads.md` — Branchen-Spend-Range
- `audits/local-gmb.md`, `audits/local-rankings.csv` — lokales Volumen
- `wettbewerber/identifikation-schema.md` — Branchen-Kontext (B2B-Stufen, typische Order-Größen)

### Schritt A.2: Briefing-KPI-Inventur

Prüfe `data/briefing.md` auf bezifferte Ziele:

- **Hat der Kunde bezifferte Ziele genannt?** (z. B. "wir wollen 50 Leads/Monat", "Umsatz +20% in 12 Monaten")
- **Timeline genannt?** (z. B. "in 6 Monaten Ergebnisse")
- **AOV / Auftragsgröße erwähnt?**

Daraus ergibt sich der **Lauf-Modus**:

- **`abgeleitet_pur`** — keine Kunden-KPIs, Ziele werden komplett aus Potenzialen abgeleitet (Standard-Fall)
- **`plausibilitaets_check`** — Kunden-KPIs vorhanden, Skill leitet trotzdem ab und vergleicht
- **`hybrid`** — manche KPIs vom Kunden (z. B. AOV), andere abzuleiten

Modus wird im Schema-Frontmatter dokumentiert.

### Schritt A.3: Branchen-Typ und Konversionsraten-Defaults

Aus `kanal-chancen.md.branchen_typ` den Branchen-Typ übernehmen. Lade die Branchen-Default-Bandbreiten aus `reference/ziel-annahmen-schema-template.md` (5+ Branchen-Typen mit CR-Bandbreiten pro Kanal, AOV-Range, Ramp-up).

Default-Bandbreiten pro Kanal als **Bandbreiten, nicht Punktwerte**:

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up (Monate) |
|---|---|---|---|---|
| SEO | 0,8% | 1,5% | 3,0% | 6-12 |
| SEA / Google-Ads | 2,5% | 4,5% | 7,0% | 1-2 |
| Local-Pack / GMB | 4,0% | 8,0% | 12,0% | 1-3 |
| LinkedIn-Ads | 0,4% | 1,0% | 2,0% | 2-4 |
| Meta-Ads | 1,0% | 2,5% | 5,0% | 1-3 |
| Social-organisch | 0,2% | 0,5% | 1,0% | 3-6 |
| Newsletter | 1,5% | 4,0% | 8,0% | 2-4 |
| Content / Blog | 0,5% | 1,2% | 2,5% | 6-12 |
| Website-CRO | n/a Hebel-Faktor | +10-15% | +25-40% | 1-3 |

Bandbreiten werden **branchen-spezifisch im Schema verfeinert** (z. B. B2B-SaaS hat höhere Demo-Lead-CR; B2C-E-Commerce hat höhere Transaction-CR). Pro Branchen-Typ liegen kuratierte Overrides in `reference/ziel-annahmen-schema-template.md`.

### Schritt A.4: AOV / LTV-Annahmen ableiten

Aus `data/kunde.md` Portfolio extrahieren:

- Preis-Range pro Produkt / Service
- Subscription / One-time
- Typische Order-Größe (B2C) oder Vertragswert (B2B)

Wenn klare Hinweise: **AOV-Bandbreite mit Konfidenz `hoch`** ableiten.
Wenn nur Indizien: Branchen-Benchmark als Fallback (z. B. B2B-SaaS-AOV 80-300 € MRR, B2C-Werkzeuge 60-200 € Order, Lokal-Dienstleister 250-2.000 € Auftrag).
Wenn Briefing eine Zahl nennt: nutze sie als realistischen Punkt der Bandbreite, konservativ/ambitioniert als ±25%.

Konfidenz: `hoch | mittel | niedrig` pro Annahme, im Schema explizit.

### Schritt A.5: Lead-zu-Kunde-Konversion (B2B-Spezifikum)

Nur wenn `branchen_typ` einer der B2B-Varianten ist (`b2b_saas`, `b2b_industrie`, `b2b_mittelstand_dienstleister`).

Default-Funnel:

```
Traffic → Anfrage (Form-Submit, Demo-Buchung)  : Form-Conversion-Rate (CR)
Anfrage → qualifizierter Lead                   : 50-80% (Branchen-Default)
qualifizierter Lead → Angebot                   : 40-70%
Angebot → Auftrag                               : 20-40% (B2B-Standard)
```

Stratege passt im Schema-Review die Stufen branchen-spezifisch an (z. B. bei sehr beratungsintensivem B2B die Angebot-zu-Auftrag-Konversion senken).

Bei B2C wird dieser Block übersprungen (Traffic → Order direkt via CR).

### Schritt A.6: Ramp-up-Phasen

Pro Kanal die Zeit bis zum "Steady State" als Bandbreite:

- SEO: 6-12 Monate (Content-Hub + Indexierung + Ranking-Konsolidierung)
- SEA: 1-2 Monate (Kampagnen-Setup + Qualitätsfaktor-Aufbau)
- Local: 1-3 Monate (GMB-Optimierung + Review-Aufbau)
- LinkedIn-Ads: 2-4 Monate (Lookalike-Audiences + Lead-Form-Tuning)
- Meta-Ads: 1-3 Monate (Pixel-Daten-Reife + Creative-Test)
- Social-organisch: 3-6 Monate (Profil-Wachstum + Algorithmen-Vertrauen)
- Content / Blog: 6-12 Monate (analog SEO)
- Newsletter: 2-4 Monate (List-Building + Engagement-Rate)

Ramp-up wird im Schema dokumentiert — wenn das Briefing eine kürzere Timeline nennt, wird das als Diskrepanz markiert (`ramp_up_diskrepanz_zu_briefing_timeline`).

### Schritt A.7: Quelle pro Annahme

Jede Annahme im Schema hat ein `quelle`-Feld mit einem der folgenden Werte:

- `sistrix_daten` — aus SEO-Sichtbarkeits-Audit
- `ahrefs_daten` — aus Keyword-Recherche
- `gmb_daten` — aus Local-Audit
- `ads_audit` — aus Google/Meta/LinkedIn-Ads-Check
- `branchen_benchmark` — aus `reference/herleitungs-methodik.md`
- `briefing_aussage` — vom Kunden im Briefing genannt
- `kunde_md_portfolio` — aus Portfolio in `data/kunde.md`
- `schaetzung_skill` — explizite Schätzung mit niedriger Konfidenz

Quelle pro Annahme im Schema-Frontmatter — **Pflicht für die Quellen-Transparenz**.

### Schritt A.8: `synthese/ziel-annahmen-schema.md` nach Drive schreiben

Erzeuge das Schema lokal nach dem Format in `reference/ziel-annahmen-schema-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "ziel-annahmen-schema.md" \
  /tmp/ziel-annahmen-schema.md "text/markdown"
```

Stratege kann die Datei direkt in Drive editieren.

Sektionen:

- **Frontmatter**: Skill-Metadaten, Branchen-Typ, Lauf-Modus, AOV-Bandbreite, Lead-Funnel (falls B2B), CR-Bandbreiten pro Kanal mit Ramp-up und Quelle
- **Body**: Übersicht des Annahmen-Sets, Begründungs-Texte pro Achse, Pflicht-Review-Sektion für den Strategen

### Schritt A.9: Schluss-Format Phase A

```
✓ 04-03-ziele-aus-potenzialen Phase A abgeschlossen.

Outputs (auf Drive):
- synthese/ziel-annahmen-schema.md — Annahmen-Set (status: vorgeschlagen)

Annahmen-Übersicht:
- Branchen-Typ:    BRANCHEN_SLUG
- Lauf-Modus:      MODUS (abgeleitet_pur | plausibilitaets_check | hybrid)
- AOV-Bandbreite:  X-Y EUR (Konfidenz K)
- Kanäle im Set:   N (Top-3 aus kanal-chancen.md plus weitere relevante)

Pflicht-Review durch den Strategen
Bitte prüfen: CR-Bandbreiten pro Kanal (branchen-realistisch?), AOV-Annahme (passt zum Portfolio?), Lead-Funnel-Stufen bei B2B (realistische Quoten?), Ramp-up-Phasen (Kunden-Timeline-Erwartung im Briefing?).
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text "$FOLDER_ID" "status.md"`):

```yaml
blockiert:
  - skill: 04-03-ziele-aus-potenzialen (Phase B)
    wartet_auf: "Strategen-Review von synthese/ziel-annahmen-schema.md (auf Drive)"
```

---

## Phase B — Ziel-Ableitung

### Schritt B.1: Schema-Validierung

Lies `synthese/ziel-annahmen-schema.md` aus Drive (`find_by_name(SYNTHESE_ID, "ziel-annahmen-schema.md")` → `read_text`). Prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis auf Phase A
2. Mindestens 3 Kanäle im Schema (sonst zu wenig Basis)
3. Jeder Kanal hat: CR-Bandbreite (konservativ/realistisch/ambitioniert), Ramp-up-Bandbreite, Quelle
4. AOV-Bandbreite gesetzt (min/realistisch/max) mit Konfidenz
5. Falls B2B: Lead-Funnel-Stufen komplett

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Existenz-Check Output

Wenn `synthese/ziele.md` oder `synthese/ziele-aufschluesselung.csv` bereits auf Drive existieren (`drive.py find_by_name`): fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt B.3: Volumen-Basis pro Kanal extrahieren

Pro Kanal aus dem Schema das **adressierbare Volumen** extrahieren (alle Audit-Inputs aus Drive `AUDITS_ID` lesen, Basis für CR-Anwendung):

- **SEO**: kumuliertes Suchvolumen der Top-3-Cluster aus `audits/seo-cluster-zusammenfassung.md` (oder Top-50 Keywords falls Cluster nicht vorhanden) — Annahme: realistischer Traffic-Anteil 20-40% (Position-1-Erwartung × Klick-Verteilung)
- **SEA**: kumuliertes Suchvolumen relevanter Keywords × Klick-Anteil bei Ads-Position (Annahme 5-15% Impression-Share zu Beginn, ramp-up gegen 25-40%)
- **Local / GMB**: lokales Suchvolumen aus `audits/local-gmb.md` oder Schätzung aus regionalem Marktvolumen × Local-Pack-Klick-Rate (Annahme 20-30%)
- **LinkedIn-Ads**: Spend-Annahme (aus Schema oder Branchen-Benchmark) × CR-Bandbreite → Leads
- **Meta-Ads**: analog LinkedIn
- **Content / Blog**: analog SEO mit niedrigeren Klick-Quoten (Mid-Funnel)
- **Website-CRO**: kein Volumen-Multiplikator, sondern Hebel-Faktor auf bestehenden Traffic

**Bandbreiten überall** — nie ein einzelner Volumen-Wert. Falls Quelle eine Punkt-Zahl liefert: ±25% als konservativ/ambitioniert.

### Schritt B.4: Drei Szenarien pro Kanal berechnen

Pro Kanal werden drei Szenarien berechnet:

```
konservativ  = Volumen_unten × CR_konservativ × AOV_unten × Lead_funnel_unten
realistisch  = Volumen_mitte × CR_realistisch × AOV_mitte × Lead_funnel_mitte
ambitioniert = Volumen_oben × CR_ambitioniert × AOV_oben × Lead_funnel_oben
```

Bei B2B mit Lead-Funnel: zusätzlich die Anfrage→Auftrag-Stufen multipliziert.

Bei Website-CRO als Hebel: Conversion-Uplift auf bestehende Conversions angewandt (statt eigene Volumen-Basis).

Pro Szenario werden ausgewiesen:

- **Traffic / Reichweite** (oben in der Kette)
- **Leads / Anfragen** (mittlere Stufe, bei B2B)
- **Aufträge / Orders** (untere Stufe)
- **Umsatz-Beitrag** (Orders × AOV)
- **Annahmen-Liste** (welche Werte aus dem Schema mit welcher Quelle)

### Schritt B.5: Aggregat über alle Kanäle

Aggregat-Berechnung berücksichtigt:

- **Pro Szenario die Summe** über alle Kanäle für Traffic, Leads, Orders, Umsatz
- **Achtung Doppelzählung**: Wenn ein User über mehrere Kanäle kommt (z. B. Brand-Search nach Ads-Impression), wird ein Korrektur-Faktor angewendet (Default 0,85 für 2-Kanal-Overlap, 0,75 für 3+-Kanal-Overlap) — im Schema dokumentiert
- **Ramp-up-gewichtet**: Steady-State-Werte plus Hinweis "Erreicht in 6-12 Monaten" — der Forecast-Skill rechnet die Monats-Kurve

Aggregat-Output:

| Szenario | Traffic | Leads | Orders | Umsatz |
|---|---|---|---|---|
| konservativ | X | Y | Z | W EUR |
| realistisch | X | Y | Z | W EUR |
| ambitioniert | X | Y | Z | W EUR |

### Schritt B.6: Plausibilitäts-Check gegen Briefing-KPIs

Wenn Lauf-Modus `plausibilitaets_check` oder `hybrid`:

Für jede Kunden-KPI aus dem Briefing:

- Liegt der Kunden-Wert **über dem ambitionierten Szenario**? → Auffälligkeit `kunde_ziel_unrealistisch_hoch`
- Liegt der Kunden-Wert **unter dem konservativen Szenario**? → Auffälligkeit `kunde_ziel_unrealistisch_niedrig` (Marken-Potenzial wird nicht ausgeschöpft)
- Liegt der Kunden-Wert **in der Bandbreite**? → ist in Ordnung, im Output als bestätigt markieren

### Schritt B.7: Auffälligkeiten extrahieren

Mindestens **6 Auffälligkeiten** (siehe Liste). Wenn weniger als 6 echte Auffälligkeiten aus den Daten ableitbar sind: ergänze um methodische Hinweise (z. B. "Annahmen mit niedriger Konfidenz — Folge-Recherche empfohlen").

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_ziel_unrealistisch_hoch` | Kunden-KPI > ambitioniertes Szenario | "Kunde will 200 Leads/Monat, ambitioniertes Szenario rechnet mit max 110" |
| `kunde_ziel_unrealistisch_niedrig` | Kunden-KPI < konservatives Szenario | "Kunde will 10 Leads/Monat, konservativ rechnen wir mit 25 — Potenzial wird nicht ausgeschöpft" |
| `kanal_dominiert_ergebnis` | Ein Kanal trägt >60% des Gesamt-Aggregats | "SEO macht 72% des realistischen Umsatzes — Klumpenrisiko, wenn ein Cluster wegbricht" |
| `aov_unklar` | AOV-Konfidenz `niedrig` (kein klarer Portfolio-Hinweis) | "AOV-Bandbreite 40-400 EUR sehr breit — Kunden-Gespräch zur Auftragsgröße empfohlen" |
| `ramp_up_diskrepanz_zu_briefing_timeline` | Briefing-Timeline kürzer als Top-Kanal-Ramp-up | "Kunde will Ergebnisse in 3 Monaten, SEO als Top-Kanal braucht 6-12 — Hybrid mit SEA als Sofort-Hebel empfehlen" |
| `lead_zu_kunde_unklar_b2b` | B2B-Funnel-Konfidenz `niedrig` über mehrere Stufen | "Anfrage→Auftrag-Quote 20-40% sehr breit — historische Daten vom Kunden würden die Bandbreite halbieren" |
| `quelle_branchen_benchmark_unsicher` | >50% der Annahmen aus `branchen_benchmark`-Quelle | "Großteil der Annahmen aus Branchen-Benchmarks (nicht aus Kunden-Daten) — Schema-Verfeinerung mit Kunden-Daten würde Genauigkeit deutlich erhöhen" |
| `briefing_kpi_passt` | Plausibilitäts-Check positiv | "Kunden-Ziel 50 Leads/Monat liegt in realistischer Bandbreite — bestätigt" |

Auffälligkeiten werden im Markdown und HTML-Report prominent gezeigt.

### Schritt B.8: CSV-Output `synthese/ziele-aufschluesselung.csv` nach Drive

Lokal generieren, dann `drive.py upsert-text "$SYNTHESE_ID" "ziele-aufschluesselung.csv" /tmp/ziele.csv "text/csv"`. Vollständiges Schema in `reference/ziel-output-schema.md`. Spalten:

```
kanal_slug, kanal_anzeigename, szenario, metrik, wert_min, wert_realistisch, wert_max, einheit,
annahme_cr_quelle, annahme_aov_quelle, annahme_volumen_quelle, konfidenz, ramp_up_monate_min, ramp_up_monate_max,
datenstand_iso
```

Wichtig:

- `szenario` ∈ `konservativ | realistisch | ambitioniert | aggregat`
- `metrik` ∈ `traffic | leads | orders | umsatz | conversion_rate | aov`
- Aggregat-Zeilen über alle Kanäle haben `kanal_slug: aggregat`
- Jede Zeile hat eine eindeutige Quellen-Kette in den `*_quelle`-Feldern

### Schritt B.9: Aggregat-Markdown `synthese/ziele.md` nach Drive

Lokal generieren, dann `drive.py upsert-text "$SYNTHESE_ID" "ziele.md" /tmp/ziele.md "text/markdown"`. Body strukturiert nach (Schema in `reference/ziel-output-schema.md`):

- **Übersicht**: Lauf-Modus, Branchen-Typ, Anzahl Kanäle, Top-Aggregat-Bandbreite (konservativ-ambitioniert EUR pro Jahr)
- **Aggregat-Tabelle** (drei Szenarien × vier Metriken)
- **Pro Kanal ein Sub-Block** mit Szenario-Tabelle plus Annahmen-Verweis
- **Annahmen-Tabelle**: was wurde mit welcher Quelle und Konfidenz hergeleitet
- **Plausibilitäts-Check gegen Briefing** (nur bei Modus `plausibilitaets_check` / `hybrid`)
- **Auffälligkeiten** (sortiert nach Relevanz)
- **Vorbereitung für `04-04-forecast-modell`**: welche Annahmen direkt weiterverwendet werden, welche im Forecast-Schema verfeinert werden müssen

### Schritt B.10: HTML-Report

Lade `_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), Platzhalter füllen, dann via `drive.py upsert-text "$REPORTS_ID" "X-ziele.html" /tmp/report.html "text/html"` nach Drive. Aus `reports/_shell.html`:

- Stat-Strip oben: Aggregat-Bandbreite (konservativ-ambitioniert EUR pro Jahr), Top-Kanal-Beitrag, Annahmen-Anzahl, Konfidenz-Quote
- Sticky-TOC zu Aggregat, Pro-Kanal-Blöcke, Annahmen, Auffälligkeiten
- **Szenario-Karten** (drei nebeneinander: konservativ / realistisch / ambitioniert) mit Umsatz-Beitrag, Traffic, Leads, Orders pro Szenario
- **Pro Kanal** ein `details class="skill"`-Block mit Szenario-Tabelle, Annahmen-Verweis
- **Annahmen-Tabelle** mit Quelle und Konfidenz pro Annahme
- **Plausibilitäts-Check** als prominente Karte (grün bei Übereinstimmung, gelb bei niedrig, rot bei unrealistisch hoch)
- **Auffälligkeiten** als `.suggestion`-Block

### Schritt B.11: Dashboard-Update und status.md

Beide aus Drive lesen, patchen, via `drive.py upsert-text` zurückschreiben.

- `04-03-ziele-aus-potenzialen` in `schritte_done` (Phase B abgeschlossen)
- Aus `blockiert` entfernen
- Reports-Liste um den HTML-Report
- `naechster_empfohlen`: `04-04-forecast-modell` (Phase A — Annahmen-Set wird im Forecast-Schema verfeinert)

### Schritt B.12: Standard-Schlussformat im Chat

```
✓ 04-03-ziele-aus-potenzialen Phase B abgeschlossen.

Outputs (auf Drive):
- synthese/ziele.md — Ziel-Bandbreiten pro Kanal plus Aggregat
- synthese/ziele-aufschluesselung.csv — Roh-Tabelle (Kanal × Szenario × Metrik)
- reports/X-ziele.html — Szenario-Karten plus Annahmen-Übersicht
Status aktualisiert in: status.md

Aggregat-Bandbreite (Steady State, Jahres-Beitrag):
- Konservativ:   X EUR
- Realistisch:   Y EUR
- Ambitioniert:  Z EUR
Top-Kanal-Beitrag: KANAL_NAME (Anteil P% am realistischen Szenario)

Top strategische Beobachtungen:
1. AUFFAELLIGKEIT_1
2. AUFFAELLIGKEIT_2
3. AUFFAELLIGKEIT_3

[Bei Plausibilitäts-Check mit Briefing-KPI:]
ℹ Briefing-Vergleich
- Kunden-Ziel KPI liegt OBEN | UNTEN | INNERHALB der abgeleiteten Bandbreite — siehe Plausibilitäts-Block.

Nächste Schritte:
1. 04-04-forecast-modell — verfeinert die Annahmen im Forecast-Schema und rechnet das 12-Monats-Modell mit Ramp-up
2. (parallel möglich) 04-05-90-tage-plan — leitet konkrete Maßnahmen für die Top-3-Kanäle ab

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/ziel-annahmen-schema-template.md` — Phase-A-Output-Format mit Branchen-Defaults für CR/AOV/Ramp-up pro 5+ Branchen-Typen
- `reference/herleitungs-methodik.md` — Formeln, Quellen-Hierarchie, Bandbreiten-Logik, Doppelzählungs-Korrektur, B2B-Lead-Funnel
- `reference/ziel-output-schema.md` — Phase-B-CSV- und Markdown-Schema mit Validierungs-Regeln

## Edge Cases

- **`kanal-chancen.md` fehlt** → harter Abbruch in Phase A mit Hinweis auf `04-02-kanal-chancen-analyse`. Skill leitet **niemals** ohne Kanal-Priorisierung ab.

- **Top-3-Kanäle sind alle mit niedriger Konfidenz** (audit_coverage `duenn`) → Warnung im Phase-A-Schluss. Skill läuft trotzdem, alle Annahmen mit `konfidenz: niedrig`, Auffälligkeit `quelle_branchen_benchmark_unsicher` wird gesetzt.

- **Briefing nennt komplette Ziel-Kette mit AOV, CR und Volumen** → Lauf-Modus `plausibilitaets_check`, Skill leitet trotzdem ab und vergleicht. Briefing-Werte werden im Output als "Kunden-Aussage" markiert.

- **Kunden-Ziel liegt 5x über ambitioniertem Szenario** → Auffälligkeit `kunde_ziel_unrealistisch_hoch` mit höchster Relevanz, prominente Empfehlung im HTML-Report ("Im Kunden-Gespräch erden — Erwartungshaltung kann sonst zu Vertrauensverlust führen").

- **B2C-Kunde aber Briefing nennt B2B-Lead-Funnel** → Lauf-Modus wird auf `hybrid` gesetzt, B2C-Direct-Conversion als Default plus optionaler B2B-Funnel-Block für die im Briefing genannten Premium-Services. Im Schema explizit dokumentiert.

- **Website-CRO als Top-Kanal aus `kanal-chancen.md`** → CRO wird als **Hebel-Faktor** auf die bestehenden Conversions aus anderen Kanälen modelliert, nicht als eigener Traffic-Kanal. Im Schema mit Quelle `cro_hebel` markiert.

- **Forecast-Modell-Skill ist bereits gelaufen und braucht Annahmen-Update** → Override-Argument "Schema überarbeiten" → Skill setzt Schema auf `vorgeschlagen` zurück (mit Backup), bricht ab. Stratege editiert, bestätigt, Skill läuft Phase B neu. Achtung: `04-04-forecast-modell` muss danach neu laufen.

- **Aggregat-Doppelzählung über Kanäle** → Default-Faktor 0,85 für 2-Kanal-Overlap, 0,75 für 3+-Kanal-Overlap (im Schema dokumentiert). Stratege kann im Review anpassen. Im Output explizit als "Roh-Summe vs. korrigierte Summe" ausgewiesen.

- **Kanal-Chancen-Top-3 hat `skip`-Kanäle (z. B. Local-SEO bei National-Online)** → werden in der Ableitung übersprungen, im Schema-Body Hinweis. Top-3 wird ggf. um Rang 4/5 ergänzt, wenn weniger als 3 nicht-skip-Kanäle.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt — Phase B läuft niemals ohne `status: bestaetigt`
- Outputs leben auf Google Drive in `synthese/` und `reports/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Daten
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (aus Drive lesen, patchen, upsert)
- HTML-Report aus `reports/_shell.html` (aus Drive geladen)
- **CSV ist Single-Source-of-Truth** für `04-04-forecast-modell`
- **Pflicht-Bandbreite, niemals Punktschätzungen** — strikt durchsetzen, auch bei "scheinbar klaren" Annahmen aus dem Briefing
- **Schreibt NICHT ins `briefing.md` zurück** — Briefing bleibt "was der Kunde gesagt hat", abgeleitete Ziele sind eigene Quelle
- **Quellen-Transparenz**: jede Zahl im Output hat ein verlinktes `quelle`-Feld
