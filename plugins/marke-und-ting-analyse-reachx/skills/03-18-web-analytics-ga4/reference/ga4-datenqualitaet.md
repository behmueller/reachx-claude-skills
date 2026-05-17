# GA4-Datenqualitäts-Gate

Das Herzstück des Skills. GA4-Properties beim Kunden sind häufig fehlerhaft aufgesetzt — Pageviews als Conversion getaggt, Consent-Verluste, fehlendes UTM-Tagging. Würde der Skill diese Zahlen ungeprüft in die Synthese geben, zöge `04-04-forecast-modell` falsche Schlüsse. Deshalb läuft `03-18` zweiphasig: **Phase A prüft, bevor Phase B Zahlen weitergibt.**

Dieses Dokument definiert:

1. Die automatischen Checks (Phase A rechnet sie selbst) — mit Schwellwerten und Begründungen.
2. Die fünf beschreibenden Strategen-Fragen — mit Begründungstexten.
3. Die `belastbarkeit`-Ableitungslogik (grün/gelb/rot).
4. Das Format der `audits/ga4-datenqualitaet.md`-Gate-Datei.

Alle Schwellwerte sind **Defaults** — bei wiederkehrenden Fehlurteilen in echten MTAs nachjustieren und hier dokumentieren.

---

## 1. Automatische Checks (Phase A)

Phase A zieht nur den Kurz-Pull (`conversions` + `overview` 12M/30T + `channels` 12M + `channels` 90T für den GA4↔GSC-Abgleich + ein source/medium-`run-report` + die Historie-Heuristik) und rechnet daraus die folgenden sechs Checks. Jeder Check liefert einen `befund` (Klartext für den Strategen) und einen `ampel`-Vorschlag (`gruen`/`gelb`/`rot`), der in die `belastbarkeit`-Ableitung einfließt.

### Check 1 — Conversion-Plausibilität

**Eingangs-Daten:** `conversions`-Antwort (Events mit `keyEvents`, `eventCount`), `overview`-Antwort (`sessions`, `keyEvents`), 12-Monats-Zeitraum.

**Schritt 1 — Key-Event-Namen scannen.** Liste der Events mit `keyEvents > 0`. Verdächtig (typische Fehl-Taggings — das sind GA4-Automatik- oder Engagement-Events, die fast nie eine echte Conversion sind):

```
page_view, scroll, session_start, user_engagement, first_visit,
view_item, view_item_list, view_search_results, view_promotion,
view_cart, click, file_download
```

Steht eines davon in der Key-Event-Liste → Auto-Befund: "Verdächtiges Key-Event getaggt: `<name>`".

**Schritt 2 — Conversion-Rate berechnen.**

```
conversion_rate_12m = keyEvents_gesamt / sessions_gesamt
```

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| `conversion_rate_12m > 0.15` | CR über Plausibilitäts-Schwellwert — fast sicher ein Pageview-/Engagement-Event als Key-Event getaggt | `rot` |
| `conversion_rate_12m == 0` ODER keine Key-Events | Kunde misst gar keine Conversions | `rot` |
| `0.001 <= conversion_rate_12m <= 0.15` UND kein verdächtiges Event | CR plausibel | `gruen` |
| CR plausibel, aber ein verdächtiges Event in der Liste | CR-Wert ok, aber Tagging unsauber — Stratege muss in Frage 2 einordnen | `gelb` |

**Begründung der 15-%-Hürde:** Echte Website-Conversion-Raten liegen branchenübergreifend meist bei 0,5–8 % (E-Commerce 1–3 %, Lead-Gen B2B oft unter 5 %). Eine CR über 15 % entsteht praktisch nur, wenn ein hochfrequentes Event (Pageview, Scroll, Engagement) fälschlich als Key-Event markiert ist — dann wird quasi jede Sitzung "konvertiert".

### Check 2 — Direct-Last (Attributions-Verlässlichkeit)

**Eingangs-Daten:** `channels`-Antwort (12 Monate).

```
direct_anteil = sessions[Channel == "Direct"] / sessions_gesamt
```

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| `direct_anteil > 0.40` | Direct-Anteil auffällig hoch — Attribution unzuverlässig | `gelb` |
| `direct_anteil > 0.60` | Direct-Anteil sehr hoch — Attribution stark gestört | `rot` |
| `direct_anteil <= 0.40` | Direct-Anteil unauffällig | `gruen` |

**Begründung:** "Direct" ist in GA4 der Auffangbucket für Sessions ohne erkennbare Quelle — Lesezeichen, direkt eingetippte URLs, aber auch **falsch oder gar nicht getaggte** Quellen: E-Mail-Klicks ohne UTM, App-Verweise, eigene Kampagnen ohne UTM-Parameter, Dark Traffic. Ein Direct-Anteil über 40 % heißt fast immer: ein relevanter Teil des Traffics wird dem falschen Kanal zugeordnet. Für die Kanal-Wertigkeits-Analyse ist das gravierend — SEO- oder Paid-Traffic, der als Direct verbucht wird, lässt den jeweiligen Kanal zu schwach aussehen.

### Check 3 — GA4↔GSC-Abgleich (Consent-/Tracking-Indikator)

**Voraussetzung:** `audits/gsc-first-party.md` (Output von `03-04-seo-first-party-gsc`) existiert. Fehlt sie → Check übersprungen, Auto-Befund: "GSC-Daten nicht verfügbar — Consent-Abgleich entfällt, Empfehlung `03-04` nachholen".

**Eingangs-Daten:**
- GA4: `sessions[Channel == "Organic Search"]` aus dem **90-Tage-`channels`-Pull** (`--range 90daysAgo`, Schritt 3.3 im SKILL.md). Phase A zieht `channels` bewusst zusätzlich mit 90-Tage-Range, damit dieser Vergleich sauber funktioniert.
- GSC: `statistiken_90_tage.clicks_total` aus `gsc-first-party.md` (90-Tage-Wert).

Beide Seiten decken damit **denselben 90-Tage-Zeitraum** ab — der Vergleich ist ein sauberer Direktvergleich. **Keine ×4-Hochrechnung** auf 12 Monate: Die wäre ungenau (Saisonalität, Trend) und ist nicht nötig, weil GA4 ebenfalls auf 90 Tage gezogen wird.

```
abgleich_verhaeltnis = ga4_organic_sessions / gsc_klicks
```

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| `abgleich_verhaeltnis < 0.70` | GA4-Organic deutlich unter GSC-Klicks — starker Consent-Verlust- / Tracking-Lücken-Verdacht | `gelb` (bzw. `rot` bei `< 0.40`) |
| `0.70 <= abgleich_verhaeltnis <= 1.30` | GA4 und GSC plausibel im Einklang | `gruen` |
| `abgleich_verhaeltnis > 1.30` | GA4-Organic über GSC-Klicks — meist Bucket-Definitions-Unterschied (GA4 zählt z. B. Google-Maps-/News-Traffic mit), seltener Bot-Traffic | `gelb` |

**Begründung:** GSC zählt **Klicks in der Google-Suche** — das passiert vor dem Cookie-Banner. GA4 zählt **getrackte Sessions** — das passiert erst nach Consent. Klickt ein Nutzer in Google, landet auf der Seite und lehnt das Banner ab, erscheint er in GSC, aber nicht (oder nur über Consent-Mode-Modellierung) in GA4. Eine GA4-Organic-Zahl deutlich unter den GSC-Klicks ist deshalb der **stärkste einzelne Indikator für Consent-Verlust** — stärker als die bloße Existenz eines Cookie-Banners, weil er die tatsächliche Lücke quantifiziert.

Die 70-%-Grenze ist konservativ: ein gewisser Schwund ist normal (GSC-Klick ≠ GA4-Session bei sofortigem Zurück-Klick, unterschiedliche Mess-Logik). Erst unter 70 % wird es zum Befund.

### Check 4 — Datenhistorie

**Eingangs-Daten:** Historie-Heuristik (`run-report --dimensions yearMonth --metrics sessions --range 730daysAgo`, früheste `yearMonth` mit `sessions > 0`).

```
historie_verfuegbar_tage = (heute - property_start)
```

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| `historie_verfuegbar_tage < 365` | Datenhistorie unter 12 Monaten — keine Saisonalität, kein YoY-Vergleich | `gelb` |
| `historie_verfuegbar_tage < 90` | Datenhistorie sehr kurz — auch der 12-Monats-Trend ist nicht aussagekräftig | `rot` |
| `historie_verfuegbar_tage >= 365` | Volle Historie verfügbar | `gruen` |

**Begründung:** Der Forecast (`04-04`) braucht Saisonalität — ein Lead-Geschäft mit Sommer-Loch oder ein Shop mit Q4-Peak ist ohne 12-Monats-Sicht nicht modellierbar. Eine kurze Historie macht die Conversion-Baseline nicht falsch, aber die Saisonalitäts-Annahmen müssen dann aus dem Branchen-Benchmark kommen.

### Check 5 — Unzugeordneter Traffic

**Eingangs-Daten:** `channels`-Antwort und source/medium-`run-report`.

```
unzugeordnet_anteil = sessions[Channel in {"Unassigned", "(not set)"}] / sessions_gesamt
```

Zusätzlich im source/medium-Report den Anteil von `(not set) / (not set)` und `(not set) / (none)` prüfen.

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| `unzugeordnet_anteil > 0.10` | Über 10 % nicht zugeordneter Traffic — Tagging-Qualität schlecht | `gelb` |
| `unzugeordnet_anteil <= 0.10` | Unzugeordneter Traffic im Normalbereich | `gruen` |

**Begründung:** `Unassigned`/`(not set)` entsteht, wenn GA4 eine Sitzung keiner Channel-Definition zuordnen kann — meist wegen kaputter UTM-Parameter (Tippfehler im `utm_medium`, nicht-standardkonforme Werte) oder Mess-Lücken. Ein hoher Anteil verzerrt die Kanal-Wertigkeits-Analyse, weil echte Kanäle Volumen "verlieren".

### Check 6 — source/medium-Scan (unübliche relevante Kanäle)

**Eingangs-Daten:** source/medium-`run-report`.

Den Report auf Quellen scannen, die GA4 pauschal als `Referral` (oder `(not set)`) verbucht, die aber strategisch einen **eigenen Kanal-Bucket** verdienen, weil sie ein eigenständiger Marketing-Hebel sind:

**Preisvergleichs-Portale** (Token im `sessionSource`):
```
idealo, billiger.de, guenstiger, geizhals, preisvergleich, ladenzeile, shopping.google
```

**Branchen- und Bewertungsportale:**
```
provenexpert, trustpilot, jameda, wlw, capterra, g2, getapp, omr, kununu, ekomi
```

Für jeden Treffer mit relevantem Volumen (`sessions`-Anteil ≥ ~2 % ODER `keyEvents > 0`):

| Bedingung | Befund | Ampel-Vorschlag |
|---|---|---|
| Treffer gefunden | "Unüblicher relevanter Kanal entdeckt: `<quelle>` (X % Sessions, als Referral verbucht) — verdient eigenen Bucket" | `gelb` (nur Informations-Befund, kein Tracking-Defekt) |
| Kein Treffer | Keine unüblichen Kanäle — Standard-Channel-Gruppierung ausreichend | `gruen` |

**Begründung:** GA4s Default Channel Group kennt keinen "Preisvergleich"- oder "Bewertungsportal"-Bucket — diese Quellen landen alle im Sammelbucket `Referral`. Für einen Shop, der einen relevanten Teil seines Umsatzes über idealo macht, ist das eine versteckte, falsch gerahmte Kanal-Realität. Der Befund ist **kein Tracking-Defekt** (das Tracking funktioniert), sondern eine Analyse-Verfeinerung: Phase B gibt diesen Quellen in `ga4-channels.csv` einen eigenen Bucket (`ist_unueblicher_kanal: true`). Der Ampel-Vorschlag ist `gelb`, weil er die `belastbarkeit` nicht verschlechtern soll — er fließt als `unueblicher_kanal_relevant`-Auffälligkeit ein, nicht ins Belastbarkeits-Urteil. Cluster-Regeln im Detail in `ga4-analyse-methodik.md`.

### Auto-Annahme — Data Filters (KEINE Strategen-Frage)

Die GA4 Data API exponiert **keine Data Filters** — interner-Traffic-Filter und Developer-Traffic-Filter sind Admin-API-Property-Settings, die `google-analytics.py` nicht liest. Der Skill nimmt deshalb **automatisch an: "ungefiltert (Standard)"** und stellt **keine Strategen-Frage zu internem Traffic**. Die Annahme wird im Gate-File als Auto-Annahme dokumentiert ("Data Filters nicht prüfbar — Annahme: Standard-Konfiguration"). Sie senkt die `belastbarkeit` nicht.

---

## 2. Die fünf Strategen-Fragen

Diese Fragen stehen im Abschnitt "Offene Fragen" der Gate-Datei. **Jede Frage erklärt, WARUM sie gestellt wird** — der Stratege ist nicht zwingend Analytics-Experte und muss den Zweck verstehen, um sinnvoll zu antworten. Der Stratege beantwortet sie direkt unter der jeweiligen Frage in der Datei und setzt dann `status: bestaetigt`.

### Frage 1 — Cookie-Weiche / Consent

> **Hat die Website ein Consent-Banner (Cookie-Banner)? Wenn ja: welches Tool (CMP) wird genutzt? Ist Google Consent Mode v2 aktiv? Ist die Akzeptanzrate bekannt (wie viel Prozent der Besucher klicken "Alle akzeptieren")?**
>
> *Warum diese Frage wichtig ist: Wenn Besucher das Cookie-Banner ablehnen, wird ihre Sitzung — je nach Setup — gar nicht oder nur modelliert in GA4 gezählt. Ein Teil des echten Traffics ist dann unsichtbar. Die GA4-Absolut-Zahlen (Sessions, Conversions) wären zu niedrig, und der Forecast würde zu pessimistisch rechnen. Die Conversion-RATE bleibt zwar relativ robust (getrackte Sessions und getrackte Conversions sind gleichermaßen betroffen), aber die Absolut-Baseline muss um den Consent-Faktor hochgerechnet werden. Mit der Akzeptanzrate können wir diesen Faktor schätzen.*

**Vorausfüll-Logik:** Wenn `03-14-web-tech-und-tracking` gelaufen ist, hat es `audits/web-tech-tracking.md` geschrieben — dort steht das erkannte CMP-Tool (Cookiebot, Usercentrics, Borlabs Cookie, Consentmanager, ...) und oft auch, ob Consent Mode erkennbar war. Der Skill liest diese Datei in Phase A und präsentiert die Frage **vorausgefüllt**:

> *Aus `03-14-web-tech-und-tracking` bekannt: CMP = `<Tool>`, Consent Mode = `<erkannt / nicht erkannt>`. Bitte nur noch ergänzen: Akzeptanzrate (falls bekannt) und ob Consent Mode v2 (nicht nur v1) aktiv ist.*

Wenn `03-14` nicht gelaufen ist, wird die Frage komplett offen gestellt, plus Hinweis: "Empfehlung: `03-14-web-tech-und-tracking` vorab laufen lassen — es erkennt das CMP-Tool automatisch."

### Frage 2 — Conversion-Einordnung (Macro vs. Micro)

> **Wir haben in GA4 folgende Key-Events (Conversions) erkannt: `<Liste der Key-Event-Namen aus dem conversions-Pull>`. Bitte ordne ein: Welche davon sind echte Macro-Conversions — also der eigentliche Geschäftsabschluss (Kauf, qualifizierte Anfrage, Lead-Formular, Terminbuchung)? Und welche sind Micro-Conversions — kleinere Zwischenschritte (Newsletter-Anmeldung, PDF-Download, Klick auf Telefonnummer)?**
>
> *Warum diese Frage wichtig ist: Nur Macro-Conversions gehören in die Forecast-Baseline — sie sind das, was am Ende Umsatz bringt. Wenn Micro-Conversions im Conversion-Zähler stecken, sieht die Conversion-Rate künstlich hoch aus, und der Forecast überschätzt das Geschäft. Wir bilden die Conversion-Baseline ausschließlich aus den von dir als Macro markierten Events.*

Wenn der Auto-Check 1 ein verdächtiges Event gefunden hat (`page_view` etc.), wird das hier explizit hervorgehoben: "Achtung: `page_view` ist als Key-Event getaggt — das ist mit hoher Wahrscheinlichkeit ein Konfigurationsfehler, keine echte Conversion. Bitte bestätige, ob es ignoriert werden soll."

### Frage 3 — Property-Wahl

> **Wir haben für den Kunden `<N>` GA4-Properties gefunden: `<Liste display_name + property_id>`. Welche ist die produktive Live-Property der aktuellen Website? Gibt es darunter Test-, Staging- oder alte (vor einem Relaunch angelegte) Properties, die wir ignorieren sollen?**
>
> *Warum diese Frage wichtig ist: Eine Test- oder Staging-Property liefert real aussehende, aber für den Forecast wertlose Daten. Und eine alte Property von vor einem Website-Relaunch hätte einen Knick in der Sitzungs-Kurve, der wie ein echter Trend aussieht. Wir wollen sicher die richtige Property auswerten.*

Diese Frage erscheint **nur, wenn das Property-Matching in Phase A mehr als einen Treffer hatte**. Bei genau einem Treffer entfällt sie (Vermerk: "nur eine Property gefunden — Property-Wahl eindeutig").

### Frage 4 — Bekannte Tracking-Lücken

> **Sind Teile der Customer Journey aus deiner Sicht ungetrackt? Beispiele: Der Checkout/Bestellprozess läuft auf einer anderen Domain (externes Shop-System, Buchungstool). Eine Subdomain (z. B. shop., blog., app.) hat kein GA4-Tag. Es gibt eine mobile App, die separat oder gar nicht gemessen wird.**
>
> *Warum diese Frage wichtig ist: Wenn der Checkout auf einer ungetrackten Domain liegt, "verschwinden" die Conversions — GA4 sieht den Kauf nie und zeigt eine Conversion-Rate nahe 0, obwohl das Geschäft funktioniert. Wir würden den Kanal dann fälschlich als wertlos einstufen. Solche Lücken müssen wir kennen, bevor wir die Zahlen interpretieren.*

### Frage 5 — Brüche im Messzeitraum

> **Gab es in den letzten 12 Monaten ein größeres Ereignis, das die GA4-Daten beeinflusst haben könnte? Beispiele: ein GA4-Neu-Setup oder Umzug auf eine neue Property, ein Website-Relaunch oder Domain-Wechsel, eine Tracking-Migration (etwa von Universal Analytics auf GA4, oder Wechsel des Tag-Management-Setups).**
>
> *Warum diese Frage wichtig ist: Solche Ereignisse erzeugen Knicke in der Sitzungs- und Conversion-Kurve — ein plötzlicher Einbruch oder Sprung. Ohne dieses Wissen würden wir den Knick als echten Marktbewegungs-Trend fehlinterpretieren und im Forecast falsch fortschreiben. Mit der Info können wir den betroffenen Zeitraum sauber einordnen oder ausklammern.*

---

## 3. belastbarkeit-Ableitung

Phase B verdichtet die sechs Auto-Check-Ampeln (aus dem Gate-Frontmatter) und die fünf Strategen-Antworten zu einem Gesamt-Urteil `belastbarkeit: gruen | gelb | rot`. Das Urteil steht im Frontmatter von `ga4-first-party.md` und prominent als Ampel im HTML-Report.

### Regel

Betrachtet werden die "Belastbarkeits-relevanten" Signale — Check 6 (unüblicher Kanal) zählt **nicht** mit, er ist eine Analyse-Verfeinerung, kein Qualitäts-Mangel.

**`rot`** — wenn **mindestens eines** zutrifft:
- Check 1 (Conversion-Plausibilität) ist `rot` UND der Stratege konnte in Frage 2 **keine** validen Macro-Conversion-Events benennen (Tracking ist faktisch unbrauchbar).
- Check 4 (Datenhistorie) ist `rot` (< 90 Tage).
- Frage 4 nennt eine Tracking-Lücke, die die **Conversion-Messung** betrifft (z. B. ungetrackter Checkout) UND es gibt keinen Workaround.
- Zwei oder mehr Auto-Checks sind `rot`.

**`gelb`** — wenn **nicht `rot`** und **mindestens eines** zutrifft:
- Ein einzelner Auto-Check ist `rot` oder `gelb`, der vom Strategen aber eingeordnet/abgemildert wurde (z. B. CR über 15 %, aber Frage 2 isoliert das falsch getaggte Event sauber — dann sind die Macro-Conversions verwertbar, aber das Tagging bleibt "unsauber").
- Consent-Lücke vermutet (Check 3 `gelb`/`rot` ODER Frage 1 nennt Banner ohne Consent Mode v2) — Absolut-Zahlen verzerrt, CR aber nutzbar.
- Datenhistorie `gelb` (< 12 Monate).
- Direct-Anteil erhöht (Check 2 `gelb`).
- Unzugeordneter Traffic erhöht (Check 5 `gelb`).

**`gruen`** — alle Belastbarkeits-relevanten Auto-Checks `gruen`, Conversion-Tracking sauber (Macro-Conversions klar definiert, CR plausibel, kein verdächtiges Event), keine Consent-Lücke vermutet, ≥ 12 Monate Historie, keine bekannte Tracking-Lücke.

### Konsequenzen pro Stufe (Pflicht zu dokumentieren)

**`rot`:** Im Frontmatter `forecast_hinweis` und in der Body-Sektion "Datenqualität und Belastbarkeit" explizit:

> Die GA4-Conversion-Rate ist NICHT belastbar. `04-04-forecast-modell` darf sie nicht als harte Zahl übernehmen und fällt transparent auf die Branchen-Benchmark-Conversion-Rate zurück. Grund: `<konkreter Befund>`. Sessions- und Kanal-Daten können — sofern nicht selbst betroffen — weiter als grobe Orientierung dienen.

**`gelb`:** Im `forecast_hinweis`:

> Die GA4-Conversion-Rate ist mit dokumentierter Einschränkung nutzbar: `<Einschränkung>`. `04-04` darf sie als Real-Szenario-Anker verwenden, soll aber die Best/Worst-Bandbreite entsprechend weiter ziehen.

**`gruen`:** Im `forecast_hinweis`:

> Die GA4-Conversion-Baseline ist belastbar und kann von `04-04` direkt als Real-Szenario-Anker übernommen werden.

### Consent-Nuance (Pflicht zu dokumentieren, unabhängig von der Ampel)

Wenn eine Consent-Lücke vermutet wird (Check 3 oder Frage 1), zusätzlich im Frontmatter `conversion_baseline.consent_korrektur_hinweis` und in der Body-Sektion:

> Consent-Lücken verzerren die **Absolut-Volumina** nach unten — abgelehnte Cookies bedeuten unsichtbare, aber real existierende Besucher. Die **Conversion-Rate** bleibt davon relativ unberührt: Sie wird aus getrackten Sessions und getrackten Conversions gebildet, beide sind gleichermaßen vom Consent betroffen, das Verhältnis bleibt stabil. Konsequenz für `04-04`: Die GA4-CR ist als Rate nutzbar, aber die **Absolut-Baseline** (Sessions/Monat, Conversions/Monat) muss um den geschätzten Consent-Faktor hochgerechnet werden. Faktor-Schätzung: bei bekannter Akzeptanzrate `a` ist der Hochrechnungs-Faktor grob `1/a` (Beispiel: 60 % Akzeptanz → Faktor ~1,67). Bei aktivem Consent Mode v2 ist der Verlust geringer (modellierte Conversions füllen die Lücke teilweise) — dann konservativer Faktor zwischen 1,0 und `1/a`.

---

## 4. Format der Gate-Datei `audits/ga4-datenqualitaet.md`

Phase A schreibt diese Datei. Sie ist gleichzeitig das Gate (Phase B liest `status`) und das strukturierte Protokoll der Datenqualitäts-Prüfung.

```markdown
---
# === Skill-Metadaten ===
skill: 03-18-web-analytics-ga4
phase: A
status: vorgeschlagen          # vorgeschlagen | bestaetigt — Stratege setzt auf bestaetigt
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Property ===
property_id: <id>              # vom Hauptthread bestätigt
property_display_name: <name>
property_mehrfach_treffer: <true | false>   # steuert, ob Frage 3 erscheint

# === Kurz-Pull-Kennzahlen ===
kurz_pull:
  zeitraum_12m_von: <ISO>
  zeitraum_12m_bis: <ISO>
  sessions_12m: <int>
  key_events_12m: <int>
  conversion_rate_12m: <float>          # 0..1
  sessions_30d: <int>
  historie_verfuegbar_tage: <int>

# === Automatische Checks ===
auto_checks:
  conversion_plausibilitaet:
    conversion_rate_12m: <float>
    verdaechtige_events: [<liste>]      # leer wenn keine
    key_events_erkannt: [<liste aller Key-Event-Namen>]
    befund: <klartext>
    ampel: <gruen | gelb | rot>
  direct_last:
    direct_anteil: <float>
    befund: <klartext>
    ampel: <gruen | gelb | rot>
  gsc_abgleich:
    gsc_datei_vorhanden: <true | false>
    ga4_organic_sessions: <int oder null>
    gsc_klicks: <int oder null>
    verhaeltnis: <float oder null>
    befund: <klartext>
    ampel: <gruen | gelb | rot | nicht_pruefbar>
  datenhistorie:
    historie_verfuegbar_tage: <int>
    befund: <klartext>
    ampel: <gruen | gelb | rot>
  unzugeordneter_traffic:
    unzugeordnet_anteil: <float>
    befund: <klartext>
    ampel: <gruen | gelb | rot>
  source_medium_scan:
    unuebliche_kanaele: [<liste {quelle, sessions, session_anteil}>]
    befund: <klartext>
    ampel: <gruen | gelb>

# === Auto-Annahmen ===
auto_annahmen:
  - "Data Filters nicht über die API prüfbar — Annahme: Standard-Konfiguration (ungefiltert)."

# === Strategen-Antworten (Stratege füllt aus) ===
strategen_antworten:
  consent: ""                  # Frei-Text — vom Strategen
  conversion_einordnung:
    macro_events: []           # vom Strategen markierte Macro-Conversion-Events
    micro_events: []
  property_wahl: ""
  tracking_luecken: ""
  brueche_im_zeitraum: ""
---

# Datenqualitäts-Gate — GA4 First-Party: <Kundenname>

## Was dieses Dokument ist

Phase A des Skills `03-18-web-analytics-ga4` hat einen Kurz-Pull aus der GA4-Property
gezogen und die automatischen Datenqualitäts-Checks gerechnet. Bevor Phase B die volle
Datenbasis erhebt und in die MTA-Synthese gibt, muss die Datenqualität geprüft sein —
sonst zieht der Forecast falsche Schlüsse.

**So geht es weiter:**
1. Die Auto-Befunde unten prüfen.
2. Die fünf Fragen im Abschnitt "Offene Fragen" beantworten (direkt darunter schreiben).
3. Im Frontmatter `status: vorgeschlagen` auf `status: bestaetigt` ändern.
4. Skill `03-18-web-analytics-ga4` erneut aufrufen — Phase B läuft dann durch.

## Automatische Befunde

### Conversion-Plausibilität
<Klartext-Absatz: CR-Wert, erkannte Key-Events, ob ein verdächtiges Event dabei ist,
was das bedeutet.>

### Direct-Last (Attribution)
<Klartext-Absatz: Direct-Anteil, Einordnung.>

### GA4↔GSC-Abgleich
<Klartext-Absatz: Verhältnis, Consent-Indikator — oder Hinweis, dass GSC-Daten fehlen.>

### Datenhistorie
<Klartext-Absatz: verfügbare Monate, Konsequenz für Saisonalität.>

### Unzugeordneter Traffic
<Klartext-Absatz: Anteil, Tagging-Qualität.>

### source/medium-Scan — unübliche Kanäle
<Klartext-Absatz: gefundene Preisvergleichs-/Bewertungsportal-Quellen, oder "keine".>

### Auto-Annahmen
- Data Filters nicht über die API prüfbar — Annahme: Standard-Konfiguration (ungefiltert).

## Offene Fragen

> Bitte direkt unter jeder Frage antworten. Jede Frage erklärt, warum sie wichtig ist.

### 1. Cookie-Weiche / Consent
<Frage-Text + Begründung aus Abschnitt 2, ggf. mit Vorausfüllung aus 03-14.>

**Antwort:**

### 2. Conversion-Einordnung (Macro vs. Micro)
<Frage-Text + Begründung + die erkannte Key-Event-Liste.>

**Antwort (Macro-Events):**
**Antwort (Micro-Events):**

### 3. Property-Wahl
<Nur wenn property_mehrfach_treffer = true. Frage-Text + Begründung + Property-Liste.>

**Antwort:**

### 4. Bekannte Tracking-Lücken
<Frage-Text + Begründung.>

**Antwort:**

### 5. Brüche im Messzeitraum
<Frage-Text + Begründung.>

**Antwort:**

## Vorläufige Belastbarkeits-Tendenz

Auf Basis nur der Auto-Checks zeichnet sich `<gruen | gelb | rot>` ab. Das endgültige
Urteil leitet Phase B aus Auto-Checks UND den Antworten oben ab — die Antworten können
das Bild verbessern (z. B. ein falsch getaggtes Event wird sauber isoliert) oder
verschärfen (z. B. ein ungetrackter Checkout wird bekannt).
```

### Validierungs-Regeln für die Gate-Datei

Phase A prüft vor dem Schreiben:

1. `property_id` ist gesetzt (vom Hauptthread bestätigt).
2. Jeder der sechs `auto_checks`-Blöcke hat `befund` und `ampel` gefüllt.
3. `auto_checks.conversion_plausibilitaet.key_events_erkannt` ist gefüllt (oder explizit leere Liste, wenn keine Key-Events existieren — das ist selbst ein Befund).
4. Frage 3 erscheint im Body genau dann, wenn `property_mehrfach_treffer: true`.
5. `status: vorgeschlagen` (Phase A setzt nie `bestaetigt`).

Phase B prüft vor dem Vollauf:

1. `status: bestaetigt` im Frontmatter — sonst kein Lauf.
2. `strategen_antworten.conversion_einordnung.macro_events` ist gefüllt ODER der Stratege hat im Frei-Text dokumentiert, dass es keine validen Macro-Events gibt (→ `belastbarkeit: rot`).
3. `consent`-Antwort ist nicht leer (sonst Hinweis: "Consent-Frage unbeantwortet — bitte ergänzen").
