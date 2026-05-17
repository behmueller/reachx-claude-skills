# Analyse-Methodik

Konkrete Berechnungs-Formeln, Heuristiken und Schwellwerte für die Kern-Analysen von Phase B:

1. Kanal-Wertigkeits-Berechnung
2. source/medium-Cluster-Regeln (unübliche Kanäle)
3. GA4↔GSC-Abgleichs-Methodik
4. Conversion-Baseline-Bildung
5. Top-Pages, Geo, Device
6. Auffälligkeiten-Schwellwerte

Die Datenqualitäts-Checks von Phase A sind separat in `ga4-datenqualitaet.md` dokumentiert. Alle Schwellwerte hier sind **Defaults** — bei wiederkehrenden Fehlurteilen in echten MTAs nachjustieren und hier dokumentieren.

## 1. Kanal-Wertigkeits-Berechnung

Der Kern-Mehrwert des Skills: nicht nur **wie viel** Traffic ein Channel bringt (Volumen), sondern **wie wertvoll** dieser Traffic ist. Ein Channel mit 50 % der Sessions, aber 0,3 % Conversion-Rate ist strategisch weniger wert als einer mit 12 % der Sessions und 5 % CR.

**Eingangs-Daten:** `ga4-channels.csv` (Periode `zwoelf_monate`), plus die Account-Gesamt-CR aus `overview`.

**Pro Channel berechnen:**

```
session_anteil      = channel.sessions / sessions_gesamt
conversion_rate     = channel.conversions / channel.sessions       # bereits in der CSV
cr_relativ          = channel.conversion_rate / account_gesamt_cr  # >1 = überdurchschnittlich
umsatz_anteil       = channel.umsatz / umsatz_gesamt               # nur E-Commerce, sonst null
engagement_rate     = channel.engagement_rate                      # bereits in der CSV
```

**Wert-Einordnung** (Feld `wert_einordnung` in `kanal_wertigkeit`):

| Einordnung | Bedingung |
|---|---|
| `hoch` | `cr_relativ >= 1.3` — der Channel konvertiert deutlich über dem Account-Schnitt |
| `mittel` | `0.7 <= cr_relativ < 1.3` — etwa Account-Durchschnitt |
| `niedrig` | `cr_relativ < 0.7` — der Channel konvertiert deutlich unter dem Schnitt |

**Kanal-Wert-Divergenz** (löst die Auffälligkeit `kanal_wert_divergenz` aus):

```
ist_divergenz = (session_anteil >= 0.20) AND (wert_einordnung == "niedrig")
```

Ein Channel, der ≥ 20 % der Sessions liefert, aber unterdurchschnittlich konvertiert — das ist die strategisch wichtigste Beobachtung: viel Traffic, der "verpufft". Typische Fälle: Direct mit vielen ungetaggten, aber kalten Besuchern; Organic Social mit Reichweite ohne Kaufabsicht.

**Cross-Reference mit anderen First-Party-Skills:**

- Wenn `audits/gsc-first-party.md` existiert: GA4-`Organic Search`-Sessions gegen GSC-Klickvolumen stellen — siehe Abschnitt 3.
- Wenn Ads-Daten vorliegen (`03-17-sea-first-party-google-ads` oder `03-05-sea-google-ads-check`): GA4-`Paid Search`-Channel gegen Ads-Spend stellen — gibt einen groben "Kosten pro Conversion über GA4 gesehen"-Wert. Nur als Orientierung, nicht als harte Zahl (GA4-Paid und Ads-Reporting zählen unterschiedlich).

**Output:** Der `kanal_wertigkeit`-Block im Frontmatter von `ga4-first-party.md` und die Kanal-Wertigkeits-Tabelle im Markdown/HTML — die zentrale Erkenntnis-Tabelle des Reports.

## 2. source/medium-Cluster-Regeln (unübliche Kanäle)

GA4s Default Channel Group kennt keinen "Preisvergleich"- oder "Bewertungsportal"-Bucket — solche Quellen landen pauschal in `Referral`. Für die Kanal-Strategie ist das eine versteckte Realität: ein Shop, der einen relevanten Umsatzanteil über idealo macht, hat dort einen eigenständigen Marketing-Hebel, der im `Referral`-Sammelbucket unsichtbar bleibt.

**Eingangs-Daten:** der source/medium-`run-report` (`sessionSourceMedium`-Dimension).

**Cluster-Definition** — Token-Match auf `sessionSource` (case-insensitive, Teilstring):

| Cluster | Such-Token |
|---|---|
| Preisvergleich | `idealo`, `billiger.de`, `guenstiger`, `geizhals`, `preisvergleich`, `ladenzeile`, `shopping.google`, `kelkoo` |
| Bewertungs-/Branchenportal | `provenexpert`, `trustpilot`, `jameda`, `wlw`, `capterra`, `getapp`, `g2.com`, `g2crowd`, `omr`, `kununu`, `ekomi`, `ausgezeichnet.org` |

**Relevanz-Schwelle** — eine Quelle wird nur dann als eigener Bucket ausgewiesen, wenn sie strategisch ins Gewicht fällt:

```
ist_relevant = (session_anteil >= 0.02) OR (conversions > 0)
```

Eine Preisvergleichs-Quelle mit 0,1 % Sessions und 0 Conversions bleibt im Referral-Bucket — sie würde den Report nur aufblähen.

**Verarbeitung in Phase B:**

1. Pro relevanter Treffer-Quelle eine eigene Zeile in `ga4-channels.csv` mit `channel = <quelle>` (z. B. `idealo.de`) und `ist_unueblicher_kanal = true`.
2. Diese Sessions/Conversions/Umsatz **aus der `Referral`-Zeile herausrechnen** — die `Referral`-Zeile zeigt danach nur den restlichen Referral-Traffic. So bleibt die Summe konsistent.
3. Im Markdown und HTML eine eigene Sub-Tabelle "Unübliche Kanäle" mit Einordnung pro Quelle (Preisvergleich = transaktionaler Hebel; Bewertungsportal = Vertrauens-/Reputations-Hebel).
4. Auffälligkeit `unueblicher_kanal_relevant`, wenn die Cluster-Summe ≥ 5 % der Gesamt-Sessions erreicht oder ein Cluster mehr Conversions liefert als ein Standard-Channel.

**Wichtig:** Diese Analyse ist eine Verfeinerung, kein Datenqualitäts-Mangel — das Tracking funktioniert ja. Sie verschlechtert die `belastbarkeit` nicht (siehe `ga4-datenqualitaet.md` Check 6).

## 3. GA4↔GSC-Abgleichs-Methodik

Der GA4↔GSC-Abgleich ist der **beste einzelne Indikator für Consent-Verlust** — er wird sowohl in Phase A (als Auto-Check, grob) als auch in Phase B (als eigene Report-Sektion, ausführlich) genutzt.

**Voraussetzung:** `audits/gsc-first-party.md` (Output von `03-04-seo-first-party-gsc`) existiert. Fehlt sie → Sektion `gsc_abgleich: null`, Hinweis im Body, Empfehlung `03-04` nachzuholen.

**Daten-Beschaffung:**

- **GA4-Seite:** `Organic Search`-Channel aus `channels`. Für einen sauberen Vergleich denselben Zeitraum wie GSC nutzen — GSC liefert in `gsc-first-party.md` einen 90-Tage-Wert (`statistiken_90_tage.clicks_total`). Der Skill zieht deshalb zusätzlich einen GA4-`channels`-Pull mit `--range 90daysAgo` und nimmt daraus die `Organic Search`-Sessions.
- **GSC-Seite:** `statistiken_90_tage.clicks_total` aus dem Frontmatter von `gsc-first-party.md`.

**Berechnung:**

```
verhaeltnis = ga4_organic_sessions_90d / gsc_klicks_90d
```

**Interpretation:**

| Verhältnis | Interpretation |
|---|---|
| `< 0.40` | Starker Consent-Verlust oder schwere Tracking-Lücke — über 60 % der Google-Sucher landen nicht messbar in GA4 |
| `0.40 – 0.70` | Deutlicher Consent-Verlust vermutet — ein relevanter Teil der echten Besucher fehlt in GA4 |
| `0.70 – 1.30` | Plausibel im Einklang — der normale Schwund (Sofort-Zurück-Klicks, unterschiedliche Mess-Logik) erklärt die Differenz |
| `> 1.30` | GA4 zählt mehr als GSC — meist Bucket-Definitions-Unterschied (GA4-`Organic Search` enthält auch organischen Maps-/News-/Bing-Traffic, GSC ist Google-Web-only), seltener Bot-Traffic |

**Warum das funktioniert:** GSC zählt Klicks **in der Suchergebnisseite** — das passiert, bevor der Nutzer die Website und damit das Cookie-Banner sieht. GA4 zählt Sessions **nach** dem Consent. Die Differenz zwischen beiden ist die Consent-/Tracking-Lücke (plus ein konstanter normaler Schwund). Deshalb ist dieser Abgleich aussagekräftiger als die bloße Feststellung "es gibt ein Cookie-Banner".

**Output:** Der `gsc_abgleich`-Block im Frontmatter und die eigene Body-Sektion "GA4↔GSC-Abgleich". Bei vermutetem Verlust fließt das in die Auffälligkeit `consent_luecke_vermutet` und in den `consent_korrektur_hinweis` der Conversion-Baseline.

## 4. Conversion-Baseline-Bildung

Die Conversion-Baseline ist das Forecast-relevante Aggregat — `04-04-forecast-modell` und `04-03-ziele-aus-potenzialen` lesen sie direkt.

**Grundprinzip: nur Macro-Conversions.** Aus der Strategen-Antwort zu Frage 2 stehen fest, welche Key-Events Macro (Geschäftsabschluss) und welche Micro (Zwischenschritt) sind. Die Baseline wird **ausschließlich aus Macro-Events** gebildet.

**Berechnung:**

```
macro_keyevents_gesamt   = Summe der keyEvents der Macro-Events (12 Monate)
gesamt_cr                = macro_keyevents_gesamt / sessions_12m
sessions_pro_monat       = sessions_12m / 12
conversions_pro_monat    = macro_keyevents_gesamt / 12
```

**Pro Channel:** aus `ga4-channels.csv` die Macro-Conversions je Channel — falls der `channels`-Pull keyEvents nicht nach Event-Name aufschlüsselt, einen zusätzlichen `run-report --dimensions sessionDefaultChannelGroup,eventName --metrics keyEvents` ziehen und auf die Macro-Events filtern.

**E-Commerce-Fall:** Wenn die Property Umsatz misst (Schritt 9.7 im SKILL.md liefert `totalRevenue > 0`):

```
umsatz_pro_monat = totalRevenue_12m / 12
aov              = totalRevenue_12m / transactions_12m
```

**Lead-Geschäfts-Fall:** keine Transaktionen, `aov: null`, `umsatz_pro_monat: null`. Die Baseline arbeitet mit Lead-Conversions — das ist normal, kein Fehler. `04-04` rechnet dann mit einem Lead-zu-Kunde-Faktor und einem Deckungsbeitrag pro Kunde aus dem Briefing.

**Consent-Korrektur (Nuance):** Bei vermuteter Consent-Lücke (Abschnitt 3 oder Strategen-Antwort Frage 1) bleibt die `gesamt_cr` als **Rate** robust — getrackte Sessions und getrackte Conversions sind gleichermaßen betroffen. Aber die **Absolut-Werte** `sessions_pro_monat` und `conversions_pro_monat` sind zu niedrig. Der `consent_korrektur_hinweis` dokumentiert das und gibt den Hochrechnungs-Faktor:

```
# bei bekannter Akzeptanzrate a (z. B. 0.60):
faktor_ohne_consent_mode = 1 / a
# bei aktivem Consent Mode v2 (modellierte Conversions füllen die Lücke teilweise):
faktor_mit_consent_mode  = konservativ zwischen 1.0 und 1/a wählen, Default ~ (1 + (1/a - 1) * 0.5)
```

Der Skill rechnet die Absolut-Werte **nicht selbst hoch** — er liefert nur den Hinweis und den Faktor. Die Hochrechnung ist Aufgabe von `04-04` (Normalisierung gehört in die Synthese, siehe SKILL.md "Wichtige Konventionen").

## 5. Top-Pages, Geo, Device

**Top-Pages:** aus `top-pages` (12 Monate). Jede Page bekommt die `kategorie_seite`-Heuristik (siehe `ga4-output-schema.md`). Conversions pro Page, soweit über `landingPage`/Page-Dimension zuordenbar — wenn nicht sauber zuordenbar, Spalte leer lassen statt zu raten.

**Geo-Split:** aus dem `country`-`run-report`. DACH-Anteil = Summe `de` + `at` + `ch`. Nicht-DACH-Anteil = Rest.

```
nicht_dach_anteil = sessions[country NOT IN (de, at, ch)] / sessions_gesamt
```

Bei `nicht_dach_anteil >= 0.15` UND `meta.json.region` nicht international → Auffälligkeit `nicht_dach_traffic_signifikant`. Vor der Auffälligkeit prüfen, ob die Nicht-DACH-Länder plausibel sind (echter Markt) oder nach Spam/Bot aussehen (viele Sessions aus untypischen Ländern mit 0 Engagement).

**Device-Split:** aus dem `deviceCategory`-`run-report`. Pro Device Sessions, Session-Anteil, CR, Engagement. Auffällig: ein Device mit hohem Session-Anteil, aber deutlich niedrigerer CR — das ist ein UX-Signal (Mobile-Checkout-Problem o. Ä.), wird in der Body-Sektion erwähnt, aber nur dann als Auffälligkeit geführt, wenn es deutlich ist.

## 6. Auffälligkeiten-Schwellwerte

Strategische Beobachtungen — analog `03-04` Schritt 8. Jede Auffälligkeit mit Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung.

| Typ | Auslöser | Relevanz | Beispiel-Beschreibung |
|---|---|---|---|
| `conversion_tracking_fehlt` | Keine Key-Events ODER `gesamt_cr == 0` | hoch | "GA4 misst keine Conversions — es sind keine Key-Events definiert. Forecast kann keine echte Conversion-Rate übernehmen und fällt auf den Branchen-Benchmark zurück." |
| `conversion_ueberzaehlt` | CR (alle keyEvents) > 15 % ODER verdächtiges Event als Key-Event getaggt | hoch | "Die Conversion-Rate liegt bei 23 % — `page_view` ist fälschlich als Key-Event getaggt. Die Baseline nutzt nur die als Macro bestätigten Events." |
| `consent_luecke_vermutet` | GA4↔GSC-Verhältnis < 0,70 ODER Consent-Banner ohne Consent Mode v2 | hoch | "GA4-Organic-Sessions liegen bei 55 % der GSC-Klicks — ein relevanter Teil der echten Besucher fehlt durch Consent-Ablehnung. Absolut-Baseline für den Forecast hochrechnen." |
| `direct_anomalie` | Direct-Anteil > 40 % | mittel (hoch bei > 60 %) | "44 % der Sessions sind Direct — wahrscheinlich fehlendes UTM-Tagging auf eigenen Kampagnen. Echte Kanal-Wertigkeit verzerrt." |
| `kanal_wert_divergenz` | Channel mit Session-Anteil ≥ 20 % UND `wert_einordnung: niedrig` | hoch | "Organic Social liefert 24 % der Sessions, konvertiert aber mit 0,4 % weit unter dem Account-Schnitt — viel Reichweite, wenig Geschäft." |
| `unueblicher_kanal_relevant` | Cluster-Summe unüblicher Kanäle ≥ 5 % der Sessions ODER mehr Conversions als ein Standard-Channel | mittel | "idealo und billiger.de bringen zusammen 8 % der Sessions, GA4 verbucht sie pauschal als Referral — Preisvergleich ist ein eigener, bisher unsichtbarer Hebel." |
| `historie_zu_kurz` | `historie_verfuegbar_tage < 365` | mittel | "GA4-Daten erst seit 7 Monaten verfügbar — keine Saisonalität, kein Jahresvergleich. Forecast-Saisonalität aus Branchen-Benchmark." |
| `nicht_dach_traffic_signifikant` | Nicht-DACH-Land(er) ≥ 15 % der Sessions, Kunde nicht international | niedrig (mittel wenn plausibler Markt) | "18 % der Sessions kommen aus [Land] — internationaler Markt unterschätzt, oder Spam-Traffic? Stratege prüfen." |
| `tracking_luecke_bekannt` | Strategen-Antwort Frage 4 nennt eine ungetrackte Journey-Stufe | hoch | "Der Checkout läuft laut Strategen auf einer ungetrackten Shop-Domain — GA4 sieht die Käufe nicht. Conversion-Rate aus GA4 ist nicht das echte Geschäft." |

**Reihenfolge im Output:** sortiert nach `relevanz` (hoch → mittel → niedrig), bei Gleichstand nach Auslöser-Stärke. Im HTML-Report die Top 3–5 prominent.

**Konsistenz mit der Belastbarkeit:** Auffälligkeiten und `belastbarkeit` hängen zusammen, sind aber nicht identisch — `belastbarkeit` ist das verdichtete Gesamt-Urteil (`ga4-datenqualitaet.md` Abschnitt 3), die Auffälligkeiten sind die einzelnen Beobachtungen. Eine `consent_luecke_vermutet`-Auffälligkeit mit Relevanz `hoch` führt typischerweise zu `belastbarkeit: gelb`; ein `conversion_tracking_fehlt` zu `belastbarkeit: rot`.

## Offene Methodik-Fragen für spätere Iteration

(In zukünftigen MTAs prüfen und hier dokumentieren:)

- Ist die 1,3-/0,7-cr_relativ-Schwelle für die Wert-Einordnung in allen Branchen sinnvoll? Bei sehr Brand-lastigen Accounts (hoher Direct/Organic-Brand-Anteil) verschiebt der Brand-Traffic den Account-Schnitt — eventuell Brand-bereinigten Schnitt nutzen.
- Der GA4↔GSC-Abgleich nimmt an, dass GA4-`Organic Search` ungefähr GSC-Scope abdeckt. Bei Properties mit viel Bing-/DuckDuckGo-Organic stimmt das nicht — dann das Verhältnis konservativer interpretieren.
- Consent-Mode-v2-Modellierung: Der Hochrechnungs-Faktor ist aktuell eine grobe Heuristik. Wenn echte MTAs Akzeptanzraten UND modellierte Conversions zeigen, einen empirischeren Faktor ableiten.
- Soll der Skill `firstUserDefaultChannelGroup` (Akquise-Channel) zusätzlich zur `sessionDefaultChannelGroup` (Session-Channel) ausweisen? Akquise-Sicht wäre für die Kanal-Wertigkeit ehrlicher, aber komplexer. Aktuell nur Session-Channel.
