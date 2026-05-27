# Audit-Methodik — Schwellwerte, Auffälligkeiten, Ampel-Logik

Kanonische Referenz für die Bewertung. Alle Schwellwerte sind **Heuristiken** für
einen schnellen Onboarding-Check — sie ersetzen keine vertiefte Analyse, sondern
machen Auffälligkeiten sichtbar. Im Zweifel die Beobachtung beschreiben statt sie
hart als „Fehler" zu deklarieren.

---

## 1. Die sechs Audit-Module

| Modul | Frage | Primäre Tools |
|---|---|---|
| **M1 — Account-Health** | Wie ist der Gesamtzustand? | `ads_get_opportunity_score`, `ads_get_errors`, `ads_get_ad_accounts` |
| **M2 — Performance-Verlauf** | Wie hat sich Leistung über 12 Monate entwickelt? | `ads_get_ad_entities` (monthly), `ads_insights_performance_trend`, `ads_insights_industry_benchmark` |
| **M3 — Struktur & Setup** | Ist das Kampagnen-Setup verbesserbar? | `ads_get_ad_entities` (campaign/adset/ad), `ads_insights_auction_ranking_benchmarks`, `ads_get_ad_account_custom_audiences` |
| **M4 — Tracking & Datenqualität** | Misst das Konto sauber? | `ads_get_datasets`, `ads_get_dataset_quality`, `ads_get_dataset_stats` |
| **M5 — Creatives** | Sind die Creatives frisch und vielfältig? | `ads_get_ad_entities` (ad, `frequency`), `ads_get_creatives` |
| **M6 — Synthese** | Was sind die priorisierten Findings? | `ads_insights_anomaly_signal` + Aggregat aus M1–M5 |

---

## 2. Ampel-Logik je Modul

Jedes Modul bekommt ein Ampel-Urteil: **grün** (solide) / **gelb** (verbesserbar) /
**rot** (struktureller Handlungsbedarf). Die Ampel ist das, was im Report oben steht.

### M1 — Account-Health
- **rot:** Konto gesperrt/eingeschränkt · Opportunity Score < 40 · ≥ 1 delivery-blockierender Fehler auf einer Kampagne mit Budget.
- **gelb:** Opportunity Score 40–69 · Delivery-Fehler nur auf pausierten/budgetlosen Entitäten.
- **grün:** Opportunity Score ≥ 70 · keine Delivery-Fehler.

### M2 — Performance-Verlauf
- **rot:** ROAS-Trend klar fallend bei steigendem Spend · Cost-per-Result > 1,5× Branchen-Benchmark · Performance-Bruch im 12-Monats-Verlauf ohne erkennbaren Grund.
- **gelb:** Effizienz seitwärts/leicht fallend · Cost-per-Result 1,0–1,5× Benchmark · ausgeprägte Saisonalität ohne Budget-Anpassung.
- **grün:** Effizienz stabil/steigend · Cost-per-Result ≤ Benchmark.

### M3 — Struktur & Setup
- **rot:** Mehrheit der Ad Sets dauerhaft in der Lernphase (zu wenig Conversions) · hoher Auction-Overlap zwischen eigenen Kampagnen · Budget zu ≥ 60 % auf einer Kampagne.
- **gelb:** Audience-Fragmentierung (viele kleine, überlappende Ad Sets) · Advantage+-Hebel ungenutzt · Placements ohne Grund stark eingeschränkt · Objective passt nicht zum erkennbaren Geschäftsziel.
- **grün:** Klare Struktur, gesunde Ad-Set-Größen, kein nennenswerter Overlap.

### M4 — Tracking & Datenqualität
- **rot:** kein Dataset / kein Pixel · Conversions-API (CAPI) fehlt · EMQ-Score schwach (siehe §4) · Daten veraltet (kein Upload in den letzten Tagen).
- **gelb:** Pixel vorhanden, aber CAPI fehlt oder EMQ mittelmäßig · Match-Key-Coverage lückenhaft.
- **grün:** Pixel + CAPI aktiv, EMQ gut, Daten frisch.

### M5 — Creatives
- **rot:** Frequency dauerhaft sehr hoch bei wenigen Creatives (Creative-Burnout) · Ad Sets mit nur 1 aktivem Creative.
- **gelb:** geringe Format-Vielfalt (nur ein Format) · Creatives alle alt (kein neues Creative in 90 Tagen) · 2 Creatives je Ad Set.
- **grün:** mehrere frische Creatives je Ad Set, Format-Mix, Frequency im grünen Bereich.

### Gesamt-Ampel
Die schlechteste Modul-Ampel bestimmt nicht automatisch das Gesamturteil — aber:
**ein rotes M4 (Tracking) macht das Gesamturteil mindestens gelb**, weil alle
Performance-Zahlen darüber dann unter Vorbehalt stehen. Das im Report-Kopf als
**Datenqualitäts-Vorbehalt** explizit ausweisen.

---

## 3. Kennzahlen-Formeln

Alle Werte aus dem MCP unverändert übernehmen — Meta liefert Geld in Konto-Währung.
Liefert das MCP eine Metrik als `Not available` (häufig `clicks`/`ctr`/`cpc`/
`purchase_roas`), gilt sie als **nicht erhoben** — nicht als `0`; die darauf
aufbauende Kennzahl entfällt und wird als Datenlücke vermerkt (Details in
`meta-ads-mcp-nutzung.md` Abschnitt 9). Abgeleitete Kennzahlen lokal berechnen:

- **ROAS** = `purchase_value / spend` — leer lassen (nicht 0), wenn `spend = 0`.
- **CTR** = `clicks / impressions` — Meta liefert i. d. R. `ctr` direkt; wenn ja, übernehmen.
- **CPC** = `spend / clicks` · **CPM** = `spend / impressions × 1000`.
- **CVR / Conversion-Rate** = `results / clicks` (bzw. `/ link_clicks`, je nach verfügbarem Feld).
- **CPA / Cost-per-Result (CPR)** = `spend / results`.
- **Frequency** = `impressions / reach` — Meta liefert `frequency` meist direkt.

**30-Tage- vs. 12-Monats-Vergleich:** beide Zeiträume mit **identischem Enddatum**
abfragen (heute). Den 30-Tage-Wert dem auf 30 Tage anteilig hochgerechneten
12-Monats-Schnitt gegenüberstellen — sonst verzerrt ungleiche Periodenlänge den Trend.

---

## 4. EMQ-Score-Lesart (Modul 4)

Event Match Quality bewertet, wie gut Events einem Meta-Konto zugeordnet werden
können. Meta skaliert i. d. R. 1–10 (bzw. „good/great"-Label). Heuristik:
- **schwach:** EMQ ≤ 5 bzw. „okay"/„poor" → rot.
- **mittel:** EMQ 6–7 → gelb.
- **gut:** EMQ ≥ 8 bzw. „good"/„great" → grün.

Tatsächliche Skala dem Tool-Output entnehmen und im Report die Roh-Werte nennen —
nicht nur das Ampel-Label. Schwache Match-Key-Coverage (wenige Match-Keys wie E-Mail,
Telefon, externe ID) ist unabhängig vom EMQ ein Gelb-/Rot-Signal.

---

## 5. Auffälligkeiten-Katalog

Jede Auffälligkeit hat: `typ`, `titel`, `beschreibung`, `relevanz` (hoch/mittel/niedrig),
`empfehlung`. Sie fließen in Modul 6 (Synthese) und in den Report-Findings-Block.

| Typ | Auslöser | Relevanz |
|---|---|---|
| `kein_conversion_tracking` | Kein Dataset / Pixel feuert keine Conversion-Events | hoch |
| `capi_fehlt` | Pixel vorhanden, aber keine Conversions-API-Quelle | hoch |
| `emq_schwach` | EMQ-Score im schwachen Bereich (§4) | hoch |
| `daten_veraltet` | Dataset ohne frischen Event-Upload | hoch |
| `delivery_fehler` | `ads_get_errors` meldet harten Blocker auf aktiver Entität | hoch |
| `konto_eingeschraenkt` | Konto-Status nicht normal / `is_queryable=false` | hoch |
| `roas_erosion` | ROAS fällt über 12 Monate bei steigendem/gleichem Spend | hoch |
| `unter_benchmark` | Cost-per-Result deutlich über Branchen-Benchmark | hoch |
| `performance_bruch` | Klarer Knick im 12-Monats-Verlauf (Anomalie-Signal) | mittel–hoch |
| `budget_konzentration` | Eine Kampagne bindet ≥ 60 % des Spends | mittel |
| `zombie_kampagne` | Aktive Kampagne mit Spend, 0 Results über ≥ 90 Tage | hoch |
| `auction_overlap` | Hoher Overlap zwischen eigenen Kampagnen/Ad Sets | mittel |
| `lernphase_dauerhaft` | Ad Sets verlassen die Lernphase nicht (zu wenig Conversions) | mittel |
| `audience_fragmentierung` | Viele kleine, überlappende Ad Sets / Audiences | mittel |
| `advantage_ungenutzt` | Keine Advantage+-Hebel trotz passendem Konto-Profil | niedrig–mittel |
| `placement_eingeschraenkt` | Placements ohne Grund manuell stark beschnitten | niedrig–mittel |
| `objective_mismatch` | Kampagnen-Objective passt nicht zum erkennbaren Geschäftsziel | mittel |
| `creative_burnout` | Hohe Frequency bei wenigen/alten Creatives | mittel |
| `creative_mono` | Ad Sets mit nur 1 Creative / nur einem Format | niedrig–mittel |
| `audience_veraltet` | Custom Audiences alt / sehr klein / ohne Delivery | niedrig |
| `konto_inaktiv` | Spend letzte 30 Tage = 0, aber 12-Monats-Spend > 0 | mittel |
| `kein_spend_historie` | Konto existiert, hat aber nie nennenswert Budget verbraucht | — (nur Hinweis) |

**Relevanz-Stufung:** Die im Katalog genannte Relevanz ist der Standard. Sie steigt,
wenn die Auffälligkeit eine Kampagne mit hohem Spend betrifft, und sinkt bei
pausierten / budgetlosen Entitäten.

---

## 6. Synthese-Regeln (Modul 6)

1. **Anomalie-Signale einordnen:** `ads_insights_anomaly_signal`-Treffer sind
   Beobachtungen — im Report als „prüfenswert" kennzeichnen, nicht als feststehende
   Ursache. Wo Metas `opportunity_score` eine kausal verknüpfte Empfehlung liefert,
   diese bevorzugen (höhere Konfidenz).
2. **Findings sortieren:** nach `relevanz` (hoch → niedrig), bei Gleichstand nach
   betroffenem Spend-Anteil.
3. **Quick-Wins vs. strukturell trennen:** Quick-Win = in < 1 Woche ohne Budget-Risiko
   umsetzbar (z. B. Negativ-Placement entfernen, Zombie-Kampagne pausieren). Strukturell
   = braucht Konzept/Abstimmung (Tracking-Neuaufbau, Kontostruktur, Audience-Strategie).
4. **Datenqualitäts-Vorbehalt zuerst:** Steht M4 auf rot, beginnt die Synthese mit
   dem Satz, dass alle ROAS-/CPA-Zahlen darüber unter Vorbehalt stehen.
5. **Top-3-Hebel:** die drei wirkungsstärksten Findings als nummerierte Liste —
   das ist der Mehrwert-Kern für das Kundengespräch.

---

## 7. Ton der Findings (intern-schonungslos, kundentauglich)

Findings werden **offen und konkret** benannt — auch unbequeme („Das Conversion-Tracking
misst nichts Belastbares"). Aber: sachlich, ohne Schuldzuweisung an Vorgänger-Agentur
oder Kunde, und jede Schwäche mit einem konkreten nächsten Schritt. So ist der Report
nach kurzer Sichtung direkt mit dem Kunden teilbar. Keine Weichzeichnung von Fakten,
aber auch kein Alarmismus — Relevanz ehrlich stufen.
