# Output-Schema

Definiert die Output-Formate des Skills. Vier Pflicht-Dateien:

- `audits/ga4-datenqualitaet.md` — das Gate (Format in `ga4-datenqualitaet.md` Abschnitt 4)
- `audits/ga4-first-party.md` — Aggregat-Markdown mit YAML-Frontmatter (hier definiert)
- `audits/ga4-channels.csv` — Channel-Ebene, die maschinenlesbare Synthese-Baseline (hier definiert)
- `audits/ga4-pages.csv` — Page-Ebene als Roh-Datenbasis (hier definiert)

Alle Dateien sind verbindlich für die Folge-Skills — Schema-Änderungen brauchen Versions-Bump (siehe `contracts.md`).

## Markdown-Schema (`audits/ga4-first-party.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-18-web-analytics-ga4
phase: B
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
  gate_datei: audits/ga4-datenqualitaet.md
  gsc_datei: audits/gsc-first-party.md          # oder null, wenn 03-04 nicht lief
  web_tech_datei: audits/web-tech-tracking.md   # oder null, wenn 03-14 nicht lief
quelle:
  tool: ga4_data_api
  helper: google-analytics.py
  property_id: <id>
  property_display_name: <name>
  abgefragt_am: <ISO-8601>

# === Zeiträume ===
zeitraeume:
  zwoelf_monate:
    von: <ISO>
    bis: <ISO>
    tage: <int>          # 365, oder weniger bei junger Property
  dreissig_tage:
    von: <ISO>
    bis: <ISO>
    tage: 30
historie_verfuegbar_tage: <int>

# === Belastbarkeit (das zentrale Qualitäts-Urteil) ===
belastbarkeit: <gruen | gelb | rot>
belastbarkeit_begruendung: <ein bis zwei Sätze>
forecast_hinweis: <was 04-04-forecast-modell mit den Zahlen tun darf/nicht darf>

# === Performance-Stand 12 Monate ===
statistiken_12_monate:
  sessions: <int>
  users: <int>
  new_users: <int>
  page_views: <int>
  key_events: <int>
  conversion_rate: <float>          # 0..1, NUR Macro-Conversions
  engagement_rate: <float>          # 0..1
  avg_session_duration_sek: <float>
  top_channel: <z. B. Organic Search>
  top_channel_session_anteil: <float>
  top_country_code: <z. B. de>
  top_country_session_anteil: <float>
  top_device: <desktop | mobile | tablet>
  top_device_session_anteil: <float>

# === Performance-Stand 30 Tage ===
statistiken_30_tage:
  sessions: <int>
  users: <int>
  key_events: <int>
  conversion_rate: <float>
  engagement_rate: <float>

# === Conversion-Baseline (das Forecast-Aggregat für 04-04) ===
conversion_baseline:
  gesamt_cr: <float>                     # 0..1, nur Macro-Conversions, 12-Monats-Basis
  sessions_pro_monat: <int>              # 12-Monats-Schnitt
  conversions_pro_monat: <int>           # Macro-Conversions, 12-Monats-Schnitt
  macro_conversion_events: [<liste>]     # aus Strategen-Antwort Frage 2
  micro_conversion_events: [<liste>]     # bewusst NICHT in der Baseline
  cr_pro_channel:
    - channel: <name>
      conversion_rate: <float>
      sessions_pro_monat: <int>
  ist_ecommerce: <true | false>
  aov: <float oder null>                 # Average Order Value, nur E-Commerce
  umsatz_pro_monat: <float oder null>
  consent_korrektur_hinweis: <text oder null>   # die Consent-Nuance, siehe ga4-datenqualitaet.md

# === Kanal-Wertigkeit ===
kanal_wertigkeit:
  - channel: <name>
    session_anteil: <float>
    conversion_rate: <float>
    umsatz_anteil: <float oder null>
    engagement_rate: <float>
    wert_einordnung: <hoch | mittel | niedrig>   # siehe ga4-analyse-methodik.md

# === GA4↔GSC-Abgleich ===
gsc_abgleich:                            # oder null, wenn gsc-first-party.md fehlt
  ga4_organic_sessions: <int>
  gsc_klicks: <int>
  verhaeltnis: <float>
  interpretation: <text>

# === Analyse-Zähler ===
analyse_zaehler:
  anzahl_channels: <int>
  anzahl_unuebliche_kanaele: <int>
  anzahl_auffaelligkeiten: <int>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <conversion_tracking_fehlt | conversion_ueberzaehlt | consent_luecke_vermutet | direct_anomalie | kanal_wert_divergenz | unueblicher_kanal_relevant | historie_zu_kurz | nicht_dach_traffic_signifikant | tracking_luecke_bekannt | sonstige>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion für die MTA-Slide>
    betroffene_channels: [<liste, optional>]

# === CSV-Verknüpfung ===
csv_dateien:
  channels: audits/ga4-channels.csv
  pages: audits/ga4-pages.csv
  zeilen_channels: <int>
  zeilen_pages: <int>

# === Roh-Daten ===
raw_dateien:
  - assets/raw/ga4-channels-12m.json
  - assets/raw/ga4-sourcemedium-12m.json
  - assets/raw/ga4-top-pages-12m.json
  - assets/raw/ga4-verlauf-monate.json
  # ... pro abgefragtem Call eine Datei
---

# First-Party-Web-Analytics aus Google Analytics 4: <Kundenname>

## Übersicht

3-5 Sätze. ZUERST das Belastbarkeits-Urteil (grün/gelb/rot) und was es für die
weitere Verwendung bedeutet. Dann: Datenstand, Performance-Snapshot (Sessions/12M,
Gesamt-CR), wo die größten Hebel und Auffälligkeiten liegen.

## Datenqualität und Belastbarkeit

**Belastbarkeit: <🟢 grün | 🟡 gelb | 🔴 rot>**

<Begründung. Dann die Auto-Befunde aus dem Gate kompakt. Dann die Strategen-Antworten
kompakt. Dann der Forecast-Hinweis: was 04-04 mit den Zahlen tun darf. Bei vermuteter
Consent-Lücke: die Consent-Korrektur-Nuance (Absolut-Volumen verzerrt, Rate robust,
Hochrechnungs-Faktor).>

## Performance-Stand

| Metrik | 12 Monate | 30 Tage |
|---|---|---|
| Sessions | <int> | <int> |
| Nutzer | <int> | <int> |
| Conversions (Macro) | <int> | <int> |
| Conversion-Rate | <X,X%> | <X,X%> |
| Engagement-Rate | <XX%> | <XX%> |

## Performance-Verlauf (12 Monate)

Monats-Kurve: Hauptbewegungen, Saisonalität, Knickpunkte. Brüche aus Strategen-
Antwort Frage 5 (GA4-Re-Setup, Relaunch, Migration) hier explizit verorten.

## Kanal-Performance und Kanal-Wertigkeit

| Channel | Sessions | Session-Anteil | Conversion-Rate | Umsatz | Engagement | Wert |
|---|---|---|---|---|---|---|
| Organic Search | … | … | … | … | … | hoch |
| Direct | … | … | … | … | … | mittel |
| … | … | … | … | … | … | … |

(1-2 Sätze: welcher Kanal liefert Volumen, welcher liefert Wert, wo divergiert das.)

## source/medium-Analyse

| Quelle/Medium | Sessions | Conversions | CR | Engagement |
|---|---|---|---|---|
| google / organic | … | … | … | … |
| … | … | … | … | … |

### Unübliche Kanäle (als Referral verbucht, eigener Bucket)

| Quelle | Sessions | Session-Anteil | Conversions | Einordnung |
|---|---|---|---|---|
| idealo.de | … | … | … | Preisvergleich — eigener Marketing-Hebel |

(Oder: "Keine unüblichen Kanäle erkannt.")

## GA4↔GSC-Abgleich

(Nur wenn gsc-first-party.md existiert, sonst: "GSC-Daten nicht verfügbar — Abgleich
übersprungen. Empfehlung: 03-04-seo-first-party-gsc nachholen.")

- GA4 Organic Search Sessions: <int>
- GSC Klicks (gleicher Zeitraum): <int>
- Verhältnis GA4/GSC: <X,X>
- Interpretation: <Consent-Lücke vermutet / plausibel im Einklang / Bucket-Unterschied>

## Conversion-Baseline (für den Forecast)

Das Forecast-relevante Aggregat — von `04-04-forecast-modell` direkt gelesen:

- Gesamt-Conversion-Rate (nur Macro): <X,X%>
- Sessions/Monat (12-Monats-Schnitt): <int>
- Conversions/Monat: <int>
- Macro-Conversion-Events: <liste>
- E-Commerce: <ja/nein> — falls ja: AOV <X> EUR, Umsatz/Monat <X> EUR
- Consent-Korrektur: <Hinweis oder "nicht nötig">

### Conversion-Rate pro Channel

| Channel | CR | Sessions/Monat |
|---|---|---|
| … | … | … |

## Top-Pages (Top 20 nach Sessions)

| # | Page | Sessions | Seitenaufrufe | Ø Dauer | Conversions | Kategorie |
|---|---|---|---|---|---|---|
| 1 | … | … | … | … | … | produkt |

## Geo- und Device-Splits

**Country (Top 5):**

| Land | Sessions | Session-Anteil | CR |
|---|---|---|---|

**Device:**

| Device | Sessions | Session-Anteil | CR | Engagement |
|---|---|---|---|---|

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach relevanz: hoch → mittel → niedrig)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: …

**Betroffen**: <channels>

## Lücken und Hinweise

- Belastbarkeit gelb/rot? → Konsequenz hier ausführen
- Property-Historie zu kurz? → Hinweis hier
- GSC-Abgleich übersprungen (03-04 fehlt)? → Hinweis hier
- Consent-Frage offen geblieben? → Hinweis hier
- Fehlgeschlagene API-Calls (welche Calls leer geliefert haben)
```

## CSV-Schema (`audits/ga4-channels.csv`)

Die **maschinenlesbare Synthese-Baseline** — `04-02-kanal-chancen-analyse` und `04-04-forecast-modell` lesen primär aus dieser Datei.

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma.

### Spalten (in fester Reihenfolge)

```
channel,periode,datum_von,datum_bis,sessions,users,new_users,conversions,conversion_rate,umsatz,engagement_rate,ist_unueblicher_kanal
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `channel` | string | ja | Channel-Name. Standard: GA4-Default-Channel-Group (englisch — `Organic Search`, `Direct`, ...). Für unübliche Kanäle: die Quelle (z. B. `idealo.de`) |
| `periode` | string | ja | `zwoelf_monate` oder `dreissig_tage` |
| `datum_von` | ISO-8601 | ja | Periode-Start |
| `datum_bis` | ISO-8601 | ja | Periode-Ende |
| `sessions` | integer | ja | Sitzungen in der Periode |
| `users` | integer | ja | Gesamt-Nutzer |
| `new_users` | integer | ja | Neue Nutzer |
| `conversions` | integer | ja | Key Events (Macro-Conversions, soweit der Channel-Report sie nach Macro filtern kann — sonst alle keyEvents, dann Hinweis im md) |
| `conversion_rate` | float | ja | `conversions / sessions`, Dezimalwert 0..1 (0.034 = 3,4%) |
| `umsatz` | float oder leer | nein | Umsatz des Channels in der Periode (EUR); leer bei Lead-Geschäft ohne E-Commerce |
| `engagement_rate` | float | ja | Engagement-Rate 0..1 |
| `ist_unueblicher_kanal` | boolean | ja | `true` für die in Phase A entdeckten Preisvergleichs-/Bewertungsportal-Quellen, die GA4 als Referral verbucht; `false` für Standard-Channels |

### Sortierung

1. `periode` (`zwoelf_monate` zuerst, dann `dreissig_tage`)
2. `sessions` absteigend
3. `channel` alphabetisch (Tiebreaker)

### Beispiel

```csv
channel,periode,datum_von,datum_bis,sessions,users,new_users,conversions,conversion_rate,umsatz,engagement_rate,ist_unueblicher_kanal
Organic Search,zwoelf_monate,2025-05-17,2026-05-16,48200,41100,33800,1640,0.034,,0.612,false
Direct,zwoelf_monate,2025-05-17,2026-05-16,21400,19800,12200,540,0.0252,,0.588,false
Paid Search,zwoelf_monate,2025-05-17,2026-05-16,12800,11900,10400,820,0.0641,,0.701,false
idealo.de,zwoelf_monate,2025-05-17,2026-05-16,3900,3700,3200,210,0.0538,,0.655,true
Organic Search,dreissig_tage,2026-04-17,2026-05-16,4200,3800,3100,150,0.0357,,0.620,false
```

### Konvention zu unüblichen Kanälen

Eine Quelle, die als `ist_unueblicher_kanal: true` einen eigenen Bucket bekommt, wird **zusätzlich** aus dem `Referral`-Bucket herausgerechnet, damit die Summe konsistent bleibt — d. h. die `Referral`-Zeile zeigt dann nur noch den restlichen Referral-Traffic. Im Markdown wird das transparent gemacht.

## CSV-Schema (`audits/ga4-pages.csv`)

UTF-8, mit Header-Zeile, Komma-getrennt.

### Spalten

```
page_path,sessions,users,page_views,avg_session_duration,conversions,kategorie_seite
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `page_path` | string | ja | Seitenpfad (ohne Host, wie GA4 ihn liefert) |
| `sessions` | integer | ja | Sitzungen 12M |
| `users` | integer | ja | Nutzer 12M |
| `page_views` | integer | ja | Seitenaufrufe 12M (`screenPageViews`) |
| `avg_session_duration` | float | ja | Durchschnittliche Sitzungsdauer in Sekunden |
| `conversions` | integer oder leer | nein | Key Events auf dieser Page (falls über `landingPage`/Page-Dimension zuordenbar) |
| `kategorie_seite` | string | ja | Pfad-Heuristik: `{produkt, service, blog, news, presse, ueber_uns, kontakt, homepage, sonstige}` |

### Page-Kategorisierungs-Heuristik

Identisch zu `gsc-pages.csv` (siehe `03-04-seo-first-party-gsc/reference/gsc-output-schema.md`) — Pfad-basierte Regex-Matches, Reihenfolge entscheidet bei Konflikt:

1. Path = `/` oder leer → `homepage`
2. Path enthält `/produkt`, `/product`, `/p/`, `/shop` → `produkt`
3. Path enthält `/leistung`, `/service`, `/loesung` → `service`
4. Path enthält `/blog`, `/magazin`, `/ratgeber`, `/wissen` → `blog`
5. Path enthält `/news`, `/aktuelles` → `news`
6. Path enthält `/presse`, `/press` → `presse`
7. Path enthält `/ueber`, `/about`, `/team`, `/karriere` → `ueber_uns`
8. Path enthält `/kontakt`, `/contact`, `/anfrage` → `kontakt`
9. Sonst → `sonstige`

Skill darf die Heuristik branchen-spezifisch erweitern, wenn auffällige Pfade vorkommen.

### Sortierung

Nach `sessions` absteigend.

## Wie Folge-Skills die Outputs lesen

### `04-02-kanal-chancen-analyse`

Liest **primär** `ga4-channels.csv` (Filter `periode=zwoelf_monate`):

- Pro Channel das Verhältnis Session-Volumen zu Conversion-Rate → Kanal-Wertigkeits-Input für den `chancen_score`.
- `ist_unueblicher_kanal=true`-Zeilen → potenzieller Bonus-Kanal, der bisher untergeht.

Liest aus `ga4-first-party.md` Frontmatter:

- `belastbarkeit` → wie stark die GA4-Signale gewichtet werden dürfen.
- `auffaelligkeiten` mit `relevanz: hoch` → strategische Story-Bausteine.
- `kanal_wertigkeit` → fertige Wert-Einordnung pro Channel.

### `04-04-forecast-modell`

Liest aus `ga4-first-party.md` Frontmatter den Block `conversion_baseline`:

- `gesamt_cr`, `cr_pro_channel`, `sessions_pro_monat`, `conversions_pro_monat`, `aov`, `umsatz_pro_monat` → die Real-Szenario-Anker.
- `consent_korrektur_hinweis` → ob die Absolut-Baseline hochgerechnet werden muss.
- `forecast_hinweis` + `belastbarkeit` → **entscheidet, ob die GA4-CR als harte Zahl genutzt werden darf.** Bei `belastbarkeit: rot` fällt der Forecast transparent auf den Branchen-Benchmark zurück.

### `04-03-ziele-aus-potenzialen`

Liest `conversion_baseline.gesamt_cr` als echte Ist-Conversion-Rate — Startpunkt für die Ziel-Bandbreiten statt reiner Branchen-Annahme.

### `03-17-sea-first-party-google-ads`

Cross-Read: vergleicht die GA4-`Paid Search`-Channel-Zeile (Sessions, CR) mit den echten Ads-Account-Daten. Divergenzen (GA4 zählt mehr/weniger Paid-Sessions als Ads Klicks meldet) sind ein Tracking-Befund.

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. `belastbarkeit` ist gesetzt und einer von `gruen`/`gelb`/`rot`.
2. `forecast_hinweis` ist gefüllt und passt zur `belastbarkeit`-Stufe (siehe `ga4-datenqualitaet.md` Abschnitt 3).
3. `conversion_baseline.macro_conversion_events` ist gefüllt — ODER bei `belastbarkeit: rot` mit leerer Liste plus explizitem Hinweis im Body, dass keine validen Macro-Events existieren.
4. `statistiken_12_monate.conversion_rate` wird **nur** aus Macro-Conversions gebildet (nicht aus allen keyEvents) — sonst inkonsistent mit `conversion_baseline.gesamt_cr`.
5. CSV: jede Zeile hat alle Pflicht-Spalten gefüllt.
6. CSV: `ist_unueblicher_kanal` ist ein Boolean, `kategorie_seite` ein gültiger Wert.
7. CSV `ga4-channels.csv`: pro `periode` summieren sich die Session-Zahlen plausibel zum `overview`-Gesamtwert (Toleranz für Rundung und herausgerechnete unübliche Kanäle).
8. Jede `auffaelligkeit` hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`.
9. `analyse_zaehler` ist konsistent mit den CSV-Inhalten.
10. Bei vorhandenem `gsc_abgleich`: `verhaeltnis = ga4_organic_sessions / gsc_klicks` ist nachrechenbar.

Wenn eine Regel verletzt wird: konkrete Fehlermeldung im Skill-Schluss-Format, welcher Eintrag korrigiert werden muss.
