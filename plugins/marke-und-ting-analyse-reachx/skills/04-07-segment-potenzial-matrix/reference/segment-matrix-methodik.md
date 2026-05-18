# Segment-Matrix-Methodik: fünf Auswertungs-Blöcke, vier Matrix-Achsen, Engpass-Typologie

Diese Datei definiert exakt, wie Phase B pro Segment rechnet. Sie ist die Methodik-Referenz für den Skill und gleichzeitig die transparente Methodik-Beilage, die der Stratege dem Kunden im MTA-Gespräch erklären kann.

## Grundprinzipien

- **Bandbreiten, niemals Punktschätzungen.** Jeder quantitative Wert hat drei Szenarien: `konservativ`, `realistisch`, `ambitioniert`.
- **Quelle pro Zahl.** Jeder Wert trägt einen Quellen-Typ aus der kanonischen Vierer-Liste (`contracts.md` Abschnitt 13): `erhoben` (aus Tool/Kunden-Datendatei gemessen), `briefing` (Kundenangabe, unverifiziert), `benchmark` (Branchen-Referenz aus `segment-raster-defaults.md`), `schaetzung_skill` (heuristisch abgeleitet).
- **Load-bearing Heuristiken markieren.** Eine `schaetzung_skill`, die die Priorisierung oder eine Engpass-Aussage trägt, wird zusätzlich als explizite Auffälligkeit ausgewiesen.
- **Forecast bleibt die Leit-Zahl.** Die Segment-Matrix verteilt das Forecast-Potenzial — sie ersetzt es nicht. Bei Abweichung > 20 % gibt es eine Auffälligkeit, keine stille Korrektur.

---

## Die fünf Auswertungs-Blöcke pro Segment

### Block 1: Marktpotenzial (bottom-up)

Ziel: die adressierbare Markt-Größe des Segments **bottom-up** beziffern — nicht top-down aus einer Marktstudie, sondern aus den Bausteinen Nachfrage × Reichweite × Conversion × Wert.

**Berechnung pro Szenario:**

```text
segment_potenzial_umsatz[szenario] =
    relevante_nachfrage[szenario]          # Such-Volumen / adressierbare Kunden im Einzugsgebiet / adressierbare Accounts
  * erreichbare_marketing_reichweite[szenario]   # realistischer Anteil, der über Marketing erreichbar ist (0..1)
  * conversion_bandbreite[szenario]        # aus Forecast-Annahmen-Schema bzw. segment-raster-defaults.md
  * segment_wert[szenario]                 # AOV bzw. Deckungsbeitrag des Segments
```

**Quellen je nach Segmentierungs-Achse:**

| Achse | `relevante_nachfrage`-Quelle |
|---|---|
| Leistungsart | Such-Volumen der leistungs-spezifischen Keyword-Cluster (aus `kanal-chancen.md` / SEO-Audits); adressierbare Account-Zahl bei B2B |
| Zielgruppe | Größe der Zielgruppe im Markt — aus Briefing, Branchen-Benchmark, ggf. Kunden-CRM-Daten |
| Region | Einwohner-/Haushalts-/Betriebs-Zahl im Einzugsgebiet × Bedarfsquote — aus Kunden-Datendateien (`erhoben`) oder als `schaetzung_skill` |

**Geteilte Parameter:** `conversion_bandbreite`, `segment_wert`/AOV und der Doppelzählungs-Faktor werden aus `synthese/forecast.md` bzw. dem bestätigten Forecast-Annahmen-Schema gezogen — nicht pro Segment neu erfunden. So bleibt die Segment-Summe mit dem Forecast vergleichbar.

**Pflicht-Cross-Check:** Summe aller `segment_potenzial_umsatz[realistisch]` gegen `forecast.md` `aggregat_12_monate.real.umsatz_eur`. Abweichung > 20 % → Auffälligkeit `segment_summe_vs_forecast_diskrepanz`. Der Forecast bleibt führend; die Segment-Matrix erklärt nur die Verteilung darunter.

### Block 2: Ist-Position des Kunden

Ziel: wie stark steht der Kunde im Segment **heute**? Liefert den Abstand zwischen Ist und Potenzial — die eigentliche Hebel-Größe.

- Wenn Kunden-Datendateien vorliegen: Umsatzanteil heute, Auftragszahlen, Kundenzahl im Segment → `erhoben`.
- Sonst: aus Briefing/Kunden-Profil geschätzt → `briefing` oder `schaetzung_skill`.

Ausgegeben wird `ist_position_umsatz_heute` (Punktwert genügt, weil Ist-Zahl) und der `hebel_abstand` = `segment_potenzial_umsatz[realistisch] − ist_position_umsatz_heute`. Ein großer Abstand bei guter Erreichbarkeit ist ein Kandidat für `segment_unterbespielt`.

### Block 3: Kritische Erreichbarkeits-Prüfung

Der ehrliche Kern. Frage: **Ist dieses Segment mit Marketing überhaupt real adressierbar?** Ein großes Marktpotenzial nützt nichts, wenn die Käufer nicht über Marketing-Touchpoints zu gewinnen sind.

Geprüft werden:

- **Such-/Awareness-Verhalten:** Sucht die Zielgruppe aktiv (SEO/SEA adressierbar) oder nicht (dann nur Push/Awareness oder gar nicht digital)?
- **Kauf-Modus:** Ist der Kauf marketing-getrieben (Anzeige/Content → Anfrage) oder beziehungs-/ausschreibungs-/empfehlungs-getrieben (Marketing spielt höchstens eine Nebenrolle)?
- **Digitale Touchpoints:** Ist die Zielgruppe über digitale Kanäle erreichbar (Alters-/Branchen-/Beschaffungs-Muster)?
- **Entscheidungs-Komplexität:** Lange Buying-Center-Prozesse (Gewerbe-/Public) sind marketing nur eingeschränkt steuerbar.

Ergebnis:

- `erreichbarkeit`-Score 0–100 (geht in die Matrix)
- `marketing_adressierbar: ja | eingeschraenkt | nein` — eine klare qualitative Aussage

Score-Leitplanken:

| Befund | `erreichbarkeit` | `marketing_adressierbar` |
|---|---|---|
| Aktive Suche, marketing-getriebener Kauf, digital erreichbar | 75–95 | ja |
| Teilweise Suche, gemischter Kauf-Modus | 45–70 | eingeschraenkt |
| Kaum Suche, beziehungs-/ausschreibungs-getrieben, schwer digital erreichbar | 10–40 | nein |

Ein Segment mit `marketing_adressierbar: nein` triggert die Auffälligkeit `segment_marketing_nicht_adressierbar` — die ehrliche Botschaft an den Kunden ist dann, dass Marketing nicht der Hebel ist.

### Block 4: Hebel + Kanal-Mix

Ziel: die Segment-Sicht mit der Kanal-Sicht verbinden. Welche Kanäle aus `kanal-chancen.md` tragen genau dieses Segment?

- Pro Segment ein **priorisierter Kanal-Mix** (2–4 Kanäle) mit `chancen_score`-Bezug aus `kanal-chancen.md`.
- Begründung pro Kanal: warum trägt er gerade dieses Segment (z. B. "SEA trägt Privat-Sanierung, weil aktive lokale Suche; LinkedIn-Ads trägt Gewerbe-Neubau, weil Buying-Center auf LinkedIn").
- Wenn ein Top-Kanal aus der Kanal-Synthese **kein** Segment klar trägt, ist das ein Hinweis (Auffälligkeit-Kandidat) — die Kanal-Sicht und die Segment-Sicht passen dann nicht sauber zusammen.

### Block 5: Aufwands-Hochrechnung

Ziel: was kostet die Erschließung des Segments? Als Bandbreite.

- **Setup-Aufwand:** einmalig — Kampagnen-Aufbau, Content-Hub, Landingpages, Tracking je Segment. EUR + Stunden-Range.
- **Laufender Aufwand:** monatlich — Paid-Spend (EUR-Bandbreite) für Paid-Anteile, Stunden-Range für organische/Service-Anteile. Die Paid-Spend-Bandbreiten werden mit den Forecast-Spend-Annahmen abgeglichen.
- **Time-to-Impact:** Monate bis zur spürbaren Wirkung — aus `segment-raster-defaults.md` plus Kanal-Mix (Paid-lastige Segmente schneller, SEO-/Content-lastige langsamer).

Liefert die Roh-Werte für die Matrix-Achsen `aufwand` und `time_to_impact`.

---

## Die vier Matrix-Achsen (0–100)

Aus den fünf Blöcken werden vier Achsen verdichtet.

### `potenzial`

Aus Block 1. Das größte Segment-Marktpotenzial (`realistisch`) wird auf 100 normiert, die übrigen Segmente relativ dazu skaliert. Untergrenze 5 (kein Segment auf 0, weil bewertbar).

### `aufwand` (invertiert)

Aus Block 5. **Hoch = niedriger Aufwand.** Mapping über den kombinierten Setup- + 12-Monats-Aufwand (`realistisch`):

- niedrigster Aufwand der Segmente → 85–95
- mittlerer Aufwand → 45–70
- höchster Aufwand → 15–35

### `erreichbarkeit`

Aus Block 3, direkt der dort ermittelte `erreichbarkeit`-Score.

### `time_to_impact` (invertiert)

Aus Block 5. **Hoch = schnelle Wirkung.** Mapping über `time_to_impact_monate` (`realistisch`):

- ≤ 3 Monate → 80–95
- 4–6 Monate → 55–75
- 7–9 Monate → 35–50
- > 9 Monate → 15–30

---

## `prioritaet_score` — Aggregation

```text
prioritaet_score = (
    0.35 * potenzial
  + 0.20 * aufwand
  + 0.30 * erreichbarkeit
  + 0.15 * time_to_impact
)
```

Ergebnis auf eine ganze Zahl gerundet (0–100). `erreichbarkeit` ist bewusst mit 0,30 hoch gewichtet — ein Segment mit großem Potenzial, das marketing nicht adressierbar ist, darf nicht oben im Ranking landen.

### Branchen-Gewichtungs-Overrides

- **Beziehungs-/Ausschreibungs-getriebene Branchen** (B2B-Industrie, öffentliche Hand, große Gewerbeprojekte): `erreichbarkeit` auf 0,35, `potenzial` auf 0,30 — die Adressierbarkeit filtert hier härter.
- **B2C-E-Commerce / hohe Marktdynamik**: `potenzial` auf 0,40, `time_to_impact` auf 0,20, `erreichbarkeit` auf 0,25 — Markt-Größe und Geschwindigkeit dominieren, Adressierbarkeit ist meist gegeben.
- **Lokal-Dienstleister**: Default-Gewichte, aber bei mehreren Regions-Segmenten `time_to_impact` auf 0,20 hoch (Local-SEO/GMB unterschiedlich schnell pro Region).

Der gewählte Gewichtungs-Satz wird im Schema (`bewertungs_raster.gewichtung` + `gewichtung_quelle`) festgehalten und im Output transparent gemacht.

---

## Engpass-Deckelung

Die Mengen-Priorisierung darf ein Segment **nicht** nach oben spülen, dessen Wachstum von der Kunden-Kapazität gedeckelt ist — mehr Marketing-Budget bringt dort nichts.

Regel: Ist der `engpass_typ` eines Segments **nicht** `marketing_potenzial` und **nicht** `kein_klarer_engpass`, wird der `prioritaet_score` für die **Mengen-Logik** wie folgt gedeckelt:

```text
prioritaet_score_mengen = min(prioritaet_score, kapazitaets_deckel)
```

- `kapazitaets_deckel = 55` bei klar belegtem Kapazitäts-Engpass (Quelle `erhoben` oder `briefing`)
- `kapazitaets_deckel = 65` bei vermutetem Engpass (`schaetzung_skill`) — schwächere Deckelung, weil unverifiziert

Der **ungedeckelte** `prioritaet_score` bleibt im CSV/Frontmatter erhalten (Spalte `prioritaet_score_roh`), der gedeckelte Wert (`prioritaet_score_mengen`) steuert das Mengen-Ranking. So bleibt für den Strategen sichtbar: "Dieses Segment hätte ohne den Kapazitäts-Engpass Priorität X — mit Engpass nur Y."

---

## Engpass-Typologie

Pro Segment genau ein `engpass_typ`:

| `engpass_typ` | Bedeutung | Empfehlungs-Richtung |
|---|---|---|
| `marketing_potenzial` | Markt / erreichbare Nachfrage limitiert | Mehr Marketing-Budget bringt mehr Wachstum |
| `liefer_kapazitaet` | Produktions-/Liefer-/Material-Kapazität limitiert | Erst Kapazität aufbauen, oder Marge statt Menge |
| `personal_kapazitaet` | Fachkräfte / Team-Größe limitiert | Recruiting parallel; Marketing dosiert |
| `vertriebs_kapazitaet` | Lead-Verarbeitung / Angebots-Durchsatz limitiert | Vertriebs-Prozess/CRM vor Lead-Skalierung |
| `onboarding_service` | Service-/Onboarding-Kapazität limitiert (SaaS, Beratung) | Onboarding skalierbar machen vor Akquise-Push |
| `kein_klarer_engpass` | beide Seiten skalieren mit | Marketing-getriebenes Wachstum tragfähig |

**Der zentrale Befund dieses Skills:** Häufig ist nicht das Marketing der Engpass, sondern die Kunden-Kapazität. Wenn ein Segment hohes `potenzial`, aber einen Kapazitäts-`engpass_typ` hat, ist die ehrliche Empfehlung **nicht** "mehr Budget in das Segment". Stattdessen — je nach Lage:

- **Marge statt Menge:** Preis-/Angebots-Optimierung im Segment, statt mehr Leads zu erzeugen, die nicht bedient werden können → Auffälligkeit `marge_statt_menge`.
- **Kapazität zuerst:** Kapazitäts-Aufbau (Recruiting, Produktion) als Voraussetzung in den 90-Tage-Plan, Marketing nachgelagert dosiert.
- **Budget umlenken:** Mengen-Budget in ein anderes Segment mit `engpass_typ: marketing_potenzial` lenken.

Diese Befunde gehören prominent in die Engpass-Analyse, die strategische Story und — wenn load-bearing — in die Auffälligkeiten.

**Verifizierung:** Engpass-Aussagen aus dem Briefing sind Hypothesen (`contracts.md` Abschnitt 13). Liegt eine Kapazitäts-Aussage nur als Briefing-Zitat vor, ist der `engpass_typ` mit Quelle `briefing` markiert; fehlt jede belastbare Info, mit `schaetzung_skill` plus Auffälligkeit `engpass_unbestaetigt` und der Empfehlung, die Engpass-Frage im Kunden-Gespräch zu klären.

---

## Priorisierung — zwei getrennte Sichten

Pflicht: Mengen-Logik und Umsetzungs-Reihenfolge werden **getrennt** ausgewiesen und begründet — niemals zu einer Liste vermischt.

### 1. Mengen-Logik

Reihung der Segmente nach `prioritaet_score_mengen` (engpass-gedeckelt) absteigend. Beantwortet: **Wo lohnt sich zusätzliches Mengen-/Wachstums-Budget am meisten?**

### 2. Umsetzungs-Reihenfolge

Eine separate, qualitative Reihenfolge. Beantwortet: **Welches Segment zuerst angehen?** Berücksichtigt:

- **Quick-Win vs. Foundation vs. Long-Term:** schnell wirksame Segmente (hoher `time_to_impact`-Score, niedriger Aufwand) zuerst, um früh Wirkung zu zeigen.
- **Abhängigkeiten:** ein Segment, dessen Cashflow den Kapazitäts-Aufbau eines größeren Segments finanziert, gehört nach vorne — auch wenn es in der Mengen-Logik nicht führt.
- **Kapazitäts-Vorlauf:** ein kapazitäts-gedeckeltes Segment startet erst, wenn der Kapazitäts-Aufbau angestoßen ist.

Weicht die Umsetzungs-Reihenfolge in mindestens einem Rang von der Mengen-Logik ab → Auffälligkeit `mengen_vs_umsetzung_divergenz`: Der Stratege muss die Reihenfolge bewusst gegen die reine Mengen-Logik begründen.

---

## Tiebreaker

Bei gleichem `prioritaet_score_mengen` wird in dieser Reihenfolge sortiert:

1. Höhere `erreichbarkeit` (adressierbare Segmente zuerst)
2. Höheres `potenzial`
3. Höherer `time_to_impact`-Score (schnellere Wirkung zuerst)
4. Alphabetisch nach `segment_slug` (Reproduzierbarkeit)

---

## Konfidenz

Pro Segment eine `konfidenz` (`hoch | mittel | niedrig`):

- `hoch`: Marktpotenzial und Ist-Position aus Kunden-Datendateien belegt (`erhoben`), Erreichbarkeit aus konkreten Audit-Daten
- `mittel`: teils `briefing`/`benchmark`, teils `erhoben`
- `niedrig`: überwiegend `schaetzung_skill` — triggert Auffälligkeit `segment_datenbasis_duenn`

Sind mehr als die Hälfte der Segmente auf `niedrig`, wird im Output-Frontmatter `konfidenz_gesamt: niedrig` gesetzt und der Modus als `reduced` ausgewiesen.
