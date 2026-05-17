# Chancen-Score-Formel: Fünf Achsen pro Kanal

Diese Datei definiert exakt, wie der `chancen_score` pro Kanal berechnet wird. Sie ist die Methodik-Referenz für den Skill und gleichzeitig die transparente Methodik-Beilage, die der Stratege dem Kunden im MTA-Gespräch erklären kann.

## Grundprinzip

Pro Kanal werden fünf Achsen auf einer **0-100-Skala** bewertet. Aus den fünf Achsen-Scores wird per gewichtetem Mittelwert der `chancen_score` berechnet. Jede Achse hat eine **Konfidenz** (`hoch | mittel | niedrig`) — wenn mehr als 2 von 5 Achsen niedrig sind, wird auch der Gesamt-Score als `niedrig` markiert.

## Achse 1: `potenzial_score`

**Frage**: Wie groß ist der Markt-Hebel in diesem Kanal für diesen Kunden?

**Skala**: 0 = kein Potenzial, 100 = sehr großes Potenzial.

### First-Party-Daten als bevorzugte Quelle

Bevor die unten stehenden Third-Party-/Branchen-Quellen herangezogen werden, prüft der Skill, ob First-Party-Ist-Daten des Kunden vorliegen — sie sind die **bevorzugte Quelle** für das Potenzial, weil sie messbar statt geschätzt sind:

- **`ga4-first-party.md` Block `kanal_wertigkeit`** (plus `ga4-channels.csv`, Filter `periode=zwoelf_monate`) — für jeden Kanal mit GA4-Beitrag: Session-Anteil, Conversion-Rate, Umsatz-Anteil, `wert_einordnung`. Ein Kanal, der laut GA4 schon echte Sessions plus eine ordentliche CR/Umsatz liefert, belegt ein reales Potenzial; ein Kanal mit kaum GA4-Beitrag, der branchen-typisch aber stark ist, behält den hohen Branchen-Default als ungehobenes Aufholpotenzial (GA4 widerlegt das Potenzial nicht, sondern zeigt nur, dass es noch nicht gehoben ist).
- **`sea-first-party.md`** (plus `sea-kampagnen.csv`) — für SEA / Google-Ads: die echte Konto-Performance (Spend-Größenordnung, ROAS, Conversions) ersetzt die geschätzte Branchen-Dichte aus `google-ads.md` als Markt-Signal.

**`belastbarkeit`-Gate (verbindlich):** Das Frontmatter-Feld `belastbarkeit` aus `ga4-first-party.md` steuert die Konfidenz, mit der die GA4-Zahlen einfließen — `gruen` → Konfidenz `hoch`, GA4-Werte voll nutzbar; `gelb` → Konfidenz `mittel`, nutzbar mit Vorsicht; `rot` → Konfidenz `niedrig`, GA4-Conversion-Zahlen nur als grobe Orientierung, keine harte Score-Ableitung daraus (dann fällt der Score transparent auf die Third-Party-/Branchen-Logik unten zurück).

Fehlen `ga4-first-party.md` und `sea-first-party.md`, gilt die folgende Quellen- und Fallback-Logik unverändert.

### Quellen pro Kanal

| Kanal | Primäre Quelle | Sekundäre Quelle |
|---|---|---|
| SEO | `seo-cluster-zusammenfassung.md` `statistiken.kumuliertes_volumen` (gesamt) plus `cluster_aggregat` Top-Score-Cluster | `seo-sichtbarkeit.md` `statistiken.luecke_kunde_zu_top_relativ` |
| SEA / Google-Ads | First-Party `sea-first-party.md` (echte Spend-/ROAS-/Conversion-Daten) — bevorzugt; sonst `google-ads.md` `statistiken.branchen_sea_dichte` + `top_werber.anzahl_anzeigen` als Indikator für Marktsignal | SpyFu-Spend-Ranges aus `akteure[i].spyfu_anreicherung` wenn vorhanden |
| Meta-Ads | `meta-ads.md` `statistiken` (analog Google) | Anzahl aktiver WBs |
| LinkedIn-Ads | `linkedin-ads.md` `statistiken` | Branchen-typische LinkedIn-Eignung |
| Local-SEO / GMB | `local-gmb.md` mit Such-Volumen lokaler Keywords | `local-rankings.csv` Wettbewerbs-Dichte |
| Content / Blog | `seo-cluster-zusammenfassung.md` Cluster mit `intent_dominanz: informational` und `funnel_dominanz: TOFU` | `content-inventur.md` Lücken vs. Wettbewerb |
| Instagram-organisch | `instagram-wettbewerb.md` Reichweite-Range der WBs | branchen-typisch |
| TikTok-organisch | `tiktok-wettbewerb.md` Reichweite-Range | branchen-typisch |
| LinkedIn-organisch | `linkedin-wettbewerb.md` oder `03-11-social-linkedin`-Output, Engagement-Median der WBs | branchen-typisch |
| Pinterest-organisch | `pinterest-wettbewerb.md` | branchen-typisch |
| YouTube-organisch | `youtube-wettbewerb.md` (falls vorhanden) | branchen-typisch |
| Website-CRO | `web-tech-tracking.md` PageSpeed-Lücke + `pagespeed.csv` LCP/CLS | Tracking-Lücken |

### Score-Logik

**First-Party-Mapping (bevorzugt — wenn `ga4-first-party.md` / `sea-first-party.md` vorhanden):**

- GA4-getragene Kanäle (Organic Search → SEO, Paid Search → SEA, organische Social-Kanäle, Direct/Referral als CRO-Indikator): Der echte GA4-Session-Anteil plus die `wert_einordnung` aus `kanal_wertigkeit` belegen das Ist-Potenzial. Ein Kanal mit substanziellem Session-Anteil und `wert_einordnung: hoch` rechtfertigt einen hohen `potenzial_score`. Ein Kanal mit 0 GA4-Beitrag wird **nicht** automatisch auf 0 gesetzt — er behält den Branchen-Default als ungehobenes Aufholpotenzial; GA4 belegt hier nur die Reife-Lücke (siehe Achse 4), nicht das Fehlen von Markt.
- SEA: aus `sea-first-party.md` die Spend-Größenordnung und ROAS — ein Konto mit relevantem Spend und tragfähigem ROAS belegt einen funktionierenden, ausbaubaren Markt.
- Bei `belastbarkeit: rot` werden die GA4-Zahlen nur als grobe Orientierung gelesen; der Score wird dann primär aus dem quantitativen Mapping unten gebildet.

**Quantitatives Mapping** (Default — wenn keine First-Party-Daten, aber Third-Party-Daten vorhanden):

- Volumen-basierte Kanäle (SEO, SEA, Content, Local): Mapping über kumuliertes Volumen relativ zum Branchen-Median
  - Volumen < 1.000 → Score 10-25
  - Volumen 1.000-10.000 → Score 25-50
  - Volumen 10.000-50.000 → Score 50-75
  - Volumen > 50.000 → Score 75-95
- Spend-basierte Kanäle (alle Ads): Mapping über Branchen-Spend-Median (aus SpyFu o. Ä.)
  - Wenn SpyFu fehlt: Hilfsmetrik Anzahl aktiver Anzeigen × 5 (gedeckelt auf 80)
- Reichweite-basierte Kanäle (Social-organisch): Median-Followers der Top-WBs als Proxy
  - Median < 1.000 → 10, < 10.000 → 30, < 100.000 → 60, > 100.000 → 85
- CRO: Inverse PageSpeed-Lücke (schlechte Performance = höheres Potenzial)
  - LCP > 4s → 80, 2.5-4s → 60, < 2.5s → 30

**Fallback ohne Daten**: Branchen-Default aus `branchen-fit-defaults.md` Spalte `potenzial_default`, Konfidenz `niedrig`.

### Konfidenz

- `hoch`: First-Party-Ist-Daten (`ga4-first-party.md` mit `belastbarkeit: gruen`, `sea-first-party.md`) ODER konkrete Audit-Daten mit mehr als einem Akteur als Referenz
- `mittel`: GA4 mit `belastbarkeit: gelb` ODER ein Third-Party-Audit verfügbar, aber dünne Daten oder nur ein Akteur
- `niedrig`: GA4 mit `belastbarkeit: rot` (Zahlen nur Orientierung) ODER nur Branchen-Default, kein Audit gelaufen

## Achse 2: `aufwand_score` (invertiert)

**Frage**: Wie niedrig ist die Reibung im Kanal? Wie schnell kommt Wirkung?

**Skala**: 0 = sehr hoher Aufwand / lange Ramp-up / hohe Tech-Voraussetzungen, 100 = niedriger Aufwand / schneller Start.

**Wichtig**: invertierte Skala — hoher Score = niedriger Aufwand.

### Bewertungs-Faktoren pro Kanal

| Kanal | Aufwands-Signale | Score-Logik |
|---|---|---|
| SEO | Median-Difficulty aller Cluster, Anzahl benötigter Content-Pieces | Difficulty 0-20 → 80-95, 20-40 → 60-80, 40-60 → 30-60, > 60 → 10-30 |
| SEA | Spend-Anforderung pro Conversion (geschätzt) | Hoher CPC oder hohe SpyFu-Spends bei WBs → niedriger Score |
| Meta-Ads | Creative-Frequenz-Anforderung, Pixel-Setup | Default 60; -20 wenn Tracking fehlt; -10 wenn FB-Page nicht vorhanden |
| LinkedIn-Ads | Sehr hohe CPCs sind branchenbekannt | Default 35; +15 wenn Branche LinkedIn-affin |
| Local-SEO | GMB-Setup, lokale Reviews-Pflege | Default 70 wenn GMB existiert, 40 wenn fehlt |
| Content | Content-Frequenz × Themen-Tiefe | Default 50; +20 bei Sweet-Spot-Cluster (niedrige Difficulty); -20 wenn Content-Hub neu aufgebaut werden muss |
| Instagram-organisch | Content-Frequenz, Creative-Qualität | Default 40; -20 wenn Branche eher textlastig; +10 wenn Kunde schon Bild-Asset-Pool hat |
| TikTok-organisch | Video-Produktion, hohe Frequenz | Default 25; +15 wenn Kunde schon Video-Content hat |
| LinkedIn-organisch | Persönlicher Content-Aufwand | Default 45; +15 wenn Kunde-Person aktiv |
| Pinterest-organisch | Visuelle Content-Anforderung | Default 35 |
| YouTube-organisch | Produktions-Aufwand sehr hoch | Default 20 |
| Website-CRO | Dev-Aufwand, A/B-Test-Setup | Default 45; -15 wenn Tracking fehlt; +20 wenn Quick-Win-Pattern aus PageSpeed (z. B. Lazy-Loading-Lücke) |

### Konfidenz

Analog zu Achse 1 — Konfidenz hoch wenn konkrete Audit-Daten, sonst mittel/niedrig.

## Achse 3: `briefing_fit_score`

**Frage**: Passt der Kanal zu den Zielen aus dem Briefing?

**Skala**: 0 = klarer Widerspruch zu Briefing-Zielen, 100 = direkt im Briefing genannt oder klare Implikation.

### Mapping-Logik

Aus `data/briefing.md` Frontmatter und Body extrahieren:

- `ziele[]` (strategische Ziele)
- `kanaele_genannt[]` (vom Kunden explizit erwähnt)
- `wachstums_richtung` (Neukunden / Bestandskunden / D2C / B2B / etc.)
- `zielgruppe[]`

**Score-Logik:**

| Bedingung | Score-Beitrag |
|---|---|
| Kanal explizit in `kanaele_genannt` | +40 (Start-Wert 60) |
| Briefing-Ziel "Neukunden-Akquise" + Performance-Kanal (SEA/Meta/LinkedIn-Ads) | +20 |
| Briefing-Ziel "Awareness / Reichweite" + Social/Content | +20 |
| Briefing-Ziel "Bestandskunden halten" + Newsletter/CRM (außerhalb dieses Skills) | nicht in dieser Achse, Hinweis im Body |
| Zielgruppe B2B + LinkedIn / SEA | +15 |
| Zielgruppe B2C + Meta-Ads / Instagram | +15 |
| Lokaler Bezug im Briefing + Local-SEO | +25 |
| Briefing schließt Kanal aus ("nicht TikTok", "nicht Print" etc.) | -50 (deutlich abwerten) |

Default bei vollständigem Briefing-Mismatch: 30.

**Bei fehlendem Briefing**: Score = 50 (neutral), Konfidenz `niedrig`, Hinweis im Output.

### Konfidenz

- `hoch`: `briefing.md` vorhanden, mehrere Briefing-Felder mappen klar
- `mittel`: Briefing vorhanden, aber Ziele/Kanäle unklar formuliert
- `niedrig`: kein Briefing oder Briefing mit vielen `unklar_aus_transkript: true` Feldern

## Achse 4: `kunden_reife_score` (kontext-abhängig)

**Frage**: Wie weit ist der Kunde bereits im Kanal aktiv? Und ist das Chance oder Engpass?

Die Achse ist **bewusst nicht-monoton**: niedrige Reife kann positiv sein (großes Aufholpotenzial), aber auch negativ (Tech-/Team-Engpass). Der Skill berechnet zwei Hilfsgrößen:

- `reife_roh` (0-100): wie aktiv ist der Kunde? 0 = inaktiv, 100 = sehr aktiv und professionell aufgesetzt
- `reife_kontext_score` (0-100): wie groß ist der Hebel daraus?

### First-Party-Daten als bevorzugte `reife_roh`-Quelle

Vor den unten stehenden Third-Party-Signalen prüft der Skill, ob First-Party-Ist-Daten vorliegen — sie sind die **bevorzugte Quelle** für `reife_roh`, weil sie die tatsächliche Kanal-Aktivität des Kunden messen statt sie zu schätzen:

- **`ga4-first-party.md` Block `kanal_wertigkeit`** (plus `ga4-channels.csv`) — für jeden GA4-getragenen Kanal: Liefert der Kanal laut GA4 echte Sessions plus Conversions, ist die Kunden-Reife belegt hoch (`reife_roh` aus dem Session-/Conversion-Beitrag abgeleitet, nicht aus Annahmen). Zeigt GA4 für einen branchen-typisch starken Kanal 0 oder kaum Beitrag, ist `reife_roh` belegt niedrig — das ist echtes, datenbelegtes Aufholpotenzial statt einer Vermutung.
- **`sea-first-party.md`** (plus `sea-kampagnen.csv`) — für SEA: aktive Kampagnen, Spend-Höhe und Konto-Aktivität sind die echte `reife_roh`. Ein Konto mit relevantem Spend → hohe Reife; ein inaktives/leeres Konto → niedrige Reife mit Engpass-Hinweis.

**`belastbarkeit`-Gate (verbindlich):** `gruen` → Konfidenz `hoch`; `gelb` → Konfidenz `mittel`; `rot` → Konfidenz `niedrig`, GA4-Zahlen nur als grobe Orientierung — dann fällt `reife_roh` auf die Third-Party-Signale unten zurück. Fehlen beide First-Party-Quellen, gilt die folgende Tabelle unverändert.

### `reife_roh` Quellen pro Kanal

| Kanal | Reife-Signal (Fallback ohne First-Party) |
|---|---|
| SEO | First-Party: GA4 `kanal_wertigkeit` Organic Search (Sessions + CR) — bevorzugt; sonst `seo-sichtbarkeit.md` `akteure[kunde].visibility_aktuell` relativ zu `top_visibility` |
| SEA | First-Party: `sea-first-party.md` (aktive Kampagnen, Spend) — bevorzugt; sonst `google-ads.md` `akteure[kunde].anzahl_aktive_anzeigen` und SpyFu-Spend |
| Meta-Ads | `meta-ads.md` analog |
| LinkedIn-Ads | `linkedin-ads.md` analog |
| Local-SEO | `local-gmb.md` Kunde-GMB-Status, Review-Anzahl, Antwort-Quote |
| Content | First-Party: GA4 `kanal_wertigkeit` Organic Search plus `ga4-pages.csv` Blog-Kategorie-Beitrag — bevorzugt; sonst `content-inventur.md` Kunde-Content-Volumen und -Frequenz |
| Social-organisch | First-Party: GA4 `kanal_wertigkeit` Organic Social — bevorzugt; sonst jeweiliger Social-Audit, Kunde-Follower und -Frequenz |
| Website-CRO | `web-tech-tracking.md` Tracking-Setup-Score, A/B-Test-Tools vorhanden |

### `reife_kontext_score` Berechnung

Pro Kanal in dieser Reihenfolge prüfen:

1. Wenn `reife_roh > 70` (Kunde bereits sehr aktiv): `score = 40` (Kanal ist Status-Quo, kein großer Chance-Hebel — aber nicht null, weil Optimierung möglich)
2. Wenn `reife_roh 40-70`: `score = 60` (Kunde aktiv, aber Luft nach oben — guter Optimierungs-Kandidat)
3. Wenn `reife_roh < 40` UND `potenzial_score > 60` UND keine Tech-/Team-Lücke erkennbar: `score = 85` (großer Hebel)
4. Wenn `reife_roh < 40` UND (Tech-Lücke ODER Branchen-Fit < 30): `score = 30` (Engpass-Risiko)
5. Wenn `reife_roh < 40` UND `potenzial_score < 40`: `score = 25` (kein großer Hebel)

**Tech-Lücke-Indikatoren:**

- Kein Tracking-Setup (aus `web-tech-tracking.md`)
- Keine GMB-Verifizierung (für Local-SEO)
- Kein Pixel/Conversion-API (für Meta/LinkedIn-Ads)
- Sehr kleines Team (aus Briefing erkennbar)

### Konfidenz

- `hoch`: First-Party-Ist-Daten zum Kunden im Kanal (`ga4-first-party.md` mit `belastbarkeit: gruen`, `sea-first-party.md`) ODER konkrete Third-Party-Audit-Daten zum Kunden
- `mittel`: GA4 mit `belastbarkeit: gelb` ODER indirekte Daten (z. B. nur Wettbewerber-Daten + Annahme über Kunden)
- `niedrig`: GA4 mit `belastbarkeit: rot` (Zahlen nur Orientierung) ODER nur Annahmen

## Achse 5: `branchen_fit_score`

**Frage**: Passt der Kanal grundsätzlich zur Branche?

**Skala**: 0 = Kanal ist für diese Branche kein realistischer Hebel, 100 = Kanal ist Pflicht in dieser Branche.

### Default-Score aus `branchen-fit-defaults.md`

Pro Branchen-Typ × Kanal gibt es einen Default-Score zwischen 10 und 95. Siehe separates Reference-File.

### Override-Logik aus Audit-Daten

Der Default-Wert wird durch konkrete Audit-Daten angepasst:

- **Aktivitäts-Override**: Wenn mindestens 50% der WBs im Kanal aktiv sind → +15 zum Default
- **Sättigungs-Override**: Wenn alle WBs aktiv UND Spend-Range hoch UND Schwellwert-Difficulty hoch → +10 (Branche ist klarer Treiber)
- **Lücken-Override**: Wenn 0 WBs aktiv UND Default-Score hoch → -20 (möglicherweise hat die Branche den Kanal aus gutem Grund verworfen — Stratege soll prüfen)
- **Cap**: Score wird auf 95 max und 5 min gedeckelt

### Konfidenz

- `hoch`: konkretes Wettbewerber-Verhalten im Kanal beobachtet (mehr als 3 WBs)
- `mittel`: nur Branchen-Default mit indirekter Plausibilität
- `niedrig`: nur Branchen-Default, kein Wettbewerber-Signal

## Aggregations-Formel

**Default:**

```
chancen_score = (
    0.30 * potenzial_score
  + 0.20 * aufwand_score
  + 0.20 * briefing_fit_score
  + 0.10 * kunden_reife_score
  + 0.20 * branchen_fit_score
)
```

Ergebnis wird auf eine ganze Zahl gerundet (0-100).

### Branchen-spezifische Gewichtungs-Overrides

Manche Branchen rechtfertigen abweichende Gewichte. Definiert in `branchen-fit-defaults.md`:

- **Lokal-Dienstleister**: höhere Gewichtung Branchen-Fit (0.25) und niedrigere Potenzial (0.25), weil Branchen-Fit hier sehr stark filtert
- **B2B-SaaS**: höhere Gewichtung Briefing-Fit (0.25), niedrigere Branchen-Fit (0.15), weil B2B-SaaS-Kanal-Mix sehr unternehmens-spezifisch ist
- **B2C-E-Commerce**: höhere Gewichtung Potenzial (0.35), niedrigere Kunden-Reife (0.05), weil hier die Marktgröße alles dominiert

## Tiebreaker

Wenn zwei Kanäle den gleichen `chancen_score` haben, wird in dieser Reihenfolge sortiert:

1. Höherer `briefing_fit_score` (Kunden-Realität geht vor Methodik)
2. Höherer `potenzial_score` (großer Hebel geht vor kleinem)
3. Höherer `aufwand_score` (schneller Win geht vor langem Aufbau)
4. Alphabetisch nach Kanal-Name (für Reproduzierbarkeit)

## Konfidenz-Aggregation

Pro Kanal wird auch eine `chancen_score_konfidenz` ausgegeben:

- `hoch`: 4 oder 5 der Achsen haben Konfidenz `hoch`
- `mittel`: 2-3 Achsen `hoch`, Rest mittel
- `niedrig`: mehr als 2 Achsen `niedrig`, oder weniger als 2 Achsen `hoch`

## Beispiel-Berechnung

Kunde: B2C-E-Commerce, Aufmaß-Werkzeuge (Hypothese aus Plan-Beispiel).

| Achse | Score | Konfidenz | Begründung |
|---|---|---|---|
| `potenzial_score` SEO | 72 | hoch | kumuliertes Volumen 11.400 für Sweet-Spot-Cluster |
| `aufwand_score` SEO | 65 | hoch | Median-Difficulty 28 — moderat |
| `briefing_fit_score` SEO | 75 | hoch | Briefing nennt "Neukundenakquise" und "SEO ausbauen" |
| `kunden_reife_score` SEO | 85 | hoch | Kunde mit reife_roh 22, potenzial hoch, keine Tech-Lücke → großer Hebel |
| `branchen_fit_score` SEO | 80 | hoch | B2C-E-Commerce default 75, WBs aktiv +5 |

Aggregation (B2C-Override 0.35/0.20/0.20/0.05/0.20):

```
chancen_score = 0.35*72 + 0.20*65 + 0.20*75 + 0.05*85 + 0.20*80
              = 25.2 + 13.0 + 15.0 + 4.25 + 16.0
              = 73.45 → 73
```

`chancen_score_konfidenz`: hoch (5 von 5 Achsen `hoch`).
