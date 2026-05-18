# Segment-Raster-Defaults: Branchen-Referenzwerte pro Segmentierungs-Achse

Diese Datei liefert die Branchen-Default-Referenzwerte, die Phase B als `benchmark`-Quelle nutzt, wenn keine Kunden-Datendateien (`erhoben`) und keine konkreten Audit-Daten vorliegen. Alle Defaults sind als **Bandbreite** angegeben (`konservativ` / `realistisch` / `ambitioniert`) — der Skill übernimmt nie eine Punktschätzung.

**Quellen-Disziplin:** Jeder hier übernommene Wert wird im Output mit Quelle `benchmark` markiert. Trägt ein Wert die Priorisierung oder eine Engpass-Aussage, wird er zusätzlich als load-bearing Auffälligkeit ausgewiesen (`contracts.md` Abschnitt 13).

Die acht Branchen-Typen sind identisch zu `04-02-kanal-chancen-analyse/reference/branchen-fit-defaults.md`: `b2b_saas`, `b2c_ecommerce`, `lokal_dienstleister`, `b2b_industrie`, `b2b_mittelstand_dienstleister`, `content_publisher`, `marktplatz_plattform`, `sonstige`.

---

## 1. Conversion-Bandbreiten pro Branche

Conversion von Marketing-Session/Kontakt zu Anfrage/Lead. Genutzt in Block 1 (Marktpotenzial), wenn das bestätigte Forecast-Annahmen-Schema keinen segment-spezifischen Wert liefert. **Vorrang hat immer die CR aus `forecast.md` bzw. dem Forecast-Annahmen-Schema** — diese Tabelle ist nur der Fallback.

| Branche | konservativ | realistisch | ambitioniert |
|---|---:|---:|---:|
| `b2b_saas` | 0,8 % | 1,8 % | 3,5 % |
| `b2c_ecommerce` | 1,0 % | 2,2 % | 4,5 % |
| `lokal_dienstleister` | 1,5 % | 3,0 % | 6,0 % |
| `b2b_industrie` | 0,5 % | 1,2 % | 2,5 % |
| `b2b_mittelstand_dienstleister` | 0,8 % | 1,8 % | 3,5 % |
| `content_publisher` | 0,3 % | 0,8 % | 1,8 % |
| `marktplatz_plattform` | 1,0 % | 2,0 % | 4,0 % |
| `sonstige` | 0,8 % | 1,8 % | 3,5 % |

> Bei B2B mit mehrstufigem Lead-Funnel ist dies die Top-Funnel-CR (Session → Lead). Die nachgelagerten Funnel-Stufen (Lead → qualifiziert → Angebot → Auftrag) werden aus dem Forecast-Annahmen-Schema übernommen, nicht hier neu angesetzt.

---

## 2. Time-to-Impact-Defaults (Monate bis spürbare Wirkung)

Monate, bis ein Marketing-Invest im Segment messbar wirkt. Hängt stark vom Kanal-Mix des Segments ab — die Tabelle gibt den branchen-typischen Mittel-Mix; Phase B verschiebt nach Kanal-Mix aus Block 4 (Paid-lastig → schneller, SEO/Content-lastig → langsamer).

| Branche | konservativ | realistisch | ambitioniert |
|---|---:|---:|---:|
| `b2b_saas` | 10 | 7 | 4 |
| `b2c_ecommerce` | 6 | 4 | 2 |
| `lokal_dienstleister` | 7 | 4 | 2 |
| `b2b_industrie` | 12 | 9 | 6 |
| `b2b_mittelstand_dienstleister` | 10 | 7 | 4 |
| `content_publisher` | 12 | 9 | 6 |
| `marktplatz_plattform` | 8 | 5 | 3 |
| `sonstige` | 10 | 7 | 4 |

**Kanal-Mix-Verschiebung** (auf den realistischen Wert angewandt):

- Segment-Kanal-Mix überwiegend Paid (SEA / Meta-Ads / LinkedIn-Ads): −2 bis −3 Monate
- Segment-Kanal-Mix überwiegend SEO / Content: +2 bis +3 Monate
- Local-SEO / GMB als Haupthebel: neutral bis −1 Monat

---

## 3. Erreichbarkeits-Defaults pro Segmentierungs-Achse

Startwert für den `erreichbarkeit`-Score (Block 3), bevor die konkrete kritische Prüfung ihn anpasst. Der Default ist bewusst konservativ — die Prüfung in Block 3 hebt oder senkt ihn anhand des tatsächlichen Such-/Kauf-Verhaltens.

### Achse Leistungsart

| Leistungs-Charakter | Erreichbarkeits-Default | Begründung |
|---|---:|---|
| Standardisierte, planbar nachgefragte Leistung | 70 | aktive Suche, marketing-getrieben |
| Erklärungsbedürftige, beratungsintensive Leistung | 50 | gemischter Kauf-Modus |
| Projekt-/Ausschreibungs-Geschäft | 30 | beziehungs-/ausschreibungs-getrieben |
| Wiederkehrende Verträge / Bestandsgeschäft | 40 | wenig Neu-Akquise über Marketing, eher Cross-/Up-Sell |

### Achse Zielgruppe

| Zielgruppen-Typ | Erreichbarkeits-Default | Begründung |
|---|---:|---|
| Endverbraucher B2C, breit | 70 | digital gut erreichbar, aktive Suche |
| Fach-Multiplikatoren (Architekten, Planer, Makler) | 55 | erreichbar, aber kein direkter Kauf — Multiplikator-Effekt |
| KMU-Entscheider | 55 | erreichbar über LinkedIn/SEA, mittlere Komplexität |
| Großkunden / Konzern-Buying-Center | 30 | lange Prozesse, marketing nur unterstützend |
| Öffentliche Hand / Ausschreibungen | 20 | formalisierte Vergabe, marketing kaum steuernd |

### Achse Region

| Region-Typ | Erreichbarkeits-Default | Begründung |
|---|---:|---|
| Kern-Einzugsgebiet mit etablierter Marke | 70 | bekannte Marke + Local-SEO greift |
| Erweitertes Einzugsgebiet, geringe Markenbekanntheit | 50 | Marketing muss erst Bekanntheit aufbauen |
| Überregional / online ohne lokalen Anker | 45 | hoher Wettbewerb, kein Local-Vorteil |

---

## 4. Marge-/Wert-Hinweise (Block 1, `segment_wert`)

Der `segment_wert` (AOV bzw. Deckungsbeitrag pro Auftrag/Order) kommt **bevorzugt aus `data/kunde.md` / Kunden-Datendateien**. Liegt nichts vor, wird er als `schaetzung_skill` aus dem Portfolio abgeleitet und als load-bearing markiert. Diese Datei gibt nur grobe Plausibilitäts-Korridore zur Selbstkontrolle:

| Branche | typische Auftrags-/Order-Größenordnung | Hinweis |
|---|---|---|
| `b2b_saas` | MRR/ARR statt Auftragswert | Wert über LTV modellieren, nicht über Einzel-Order |
| `b2c_ecommerce` | zweistellig bis niedrig dreistellig EUR | Warenkorb-AOV, hohe Frequenz |
| `lokal_dienstleister` | stark streuend, je nach Leistung | Privat- vs. Gewerbe-Segment trennt sich oft hier am deutlichsten |
| `b2b_industrie` | hoch vier- bis sechsstellig EUR | wenige, große Aufträge — kleine Mengen-Änderung, große Umsatz-Wirkung |
| `b2b_mittelstand_dienstleister` | Projekt-/Retainer-Werte vierstellig+ | Projekt vs. Retainer als mögliche Segment-Achse |
| `content_publisher` | Reichweiten-/Abo-getrieben | Wert über Abo-LTV oder Werbe-CPM |
| `marktplatz_plattform` | Take-Rate pro Transaktion | Wert = Transaktionsvolumen × Take-Rate |

---

## 5. Engpass-Wahrscheinlichkeit pro Branche (Orientierung für Block 4/B.4)

Welcher Engpass-Typ ist branchen-typisch am wahrscheinlichsten? Nur Orientierung — der tatsächliche Engpass wird pro Segment aus Briefing-Kapazitäts-Aussagen und Kunden-Datendateien bestimmt, nicht aus dieser Tabelle.

| Branche | häufigster Kapazitäts-Engpass | Hinweis |
|---|---|---|
| `b2b_saas` | `onboarding_service` | Akquise skaliert schneller als Onboarding/Customer-Success |
| `b2c_ecommerce` | `marketing_potenzial` | meist marketing-getrieben, Logistik selten der Engpass |
| `lokal_dienstleister` | `personal_kapazitaet` / `liefer_kapazitaet` | Monteur-/Handwerker-Kapazität deckelt häufig — klassischer Fall |
| `b2b_industrie` | `liefer_kapazitaet` | Produktions-/Material-Kapazität deckelt |
| `b2b_mittelstand_dienstleister` | `personal_kapazitaet` / `vertriebs_kapazitaet` | Berater-Stunden bzw. Angebots-Durchsatz deckeln |
| `content_publisher` | `marketing_potenzial` | Reichweiten-getrieben |
| `marktplatz_plattform` | `marketing_potenzial` (Angebots-Seite ggf. Engpass) | bei 2-seitigen Märkten kann die schwache Marktseite limitieren |
| `sonstige` | unbestimmt | pro Segment einzeln prüfen |

**Praxis-Hinweis:** Bei `lokal_dienstleister` und `b2b_industrie` ist der Befund "die Kunden-Kapazität ist der Engpass, nicht das Marketing" überdurchschnittlich häufig. Der Skill prüft das hier nicht voreilig, aber Block B.4 schaut bei diesen Branchen besonders genau auf Briefing-Kapazitäts-Aussagen.

---

## 6. Aufwands-Größenordnungen (Block 5, Orientierung)

Setup- und laufender Aufwand pro Segment hängen vom Kanal-Mix ab. Grobe Orientierungs-Korridore (der konkrete Aufwand kommt aus dem Kanal-Mix in Block 4 plus den Forecast-Spend-Annahmen):

| Kanal-Mix-Charakter des Segments | Setup-Aufwand | Laufender Aufwand/Monat |
|---|---|---|
| Paid-lastig (SEA/Meta/LinkedIn-Ads) | mittel — Kampagnen-/Tracking-Setup | EUR-Spend dominiert, Stunden gering |
| SEO/Content-lastig | hoch — Content-Hub, Landingpages | Stunden dominieren, Spend gering |
| Local-SEO/GMB | niedrig-mittel — GMB-Optimierung je Standort | Stunden moderat, kaum Spend |
| Hybrid | mittel-hoch | gemischt EUR + Stunden |

Konkrete EUR-/Stunden-Bandbreiten werden nicht hier fixiert, sondern aus dem Forecast (Spend-Annahmen) und dem späteren `04-06-retainer-kalkulator`-Rahmen abgeleitet — diese Tabelle dient nur der Plausibilitäts-Selbstkontrolle.
