# Output-Schema für `03-05-sea-google-ads-check`

Definiert die beiden Pflicht-Outputs:

- `audits/google-ads-anzeigen.csv` — Roh-Anzeigen pro Akteur (für Folge-Analysen und ggf. spätere Synthese)
- `audits/google-ads.md` — Aggregat-Markdown mit Aktivitäts-Matrix, Themen-Clustern, Auffälligkeiten

Plus dieselbe Pattern-Sprache für die zwei Folge-Skills `03-06-sea-meta-ads-library-check` und `03-07-sea-linkedin-ads-library-check` — die nutzen analoges Schema, nur mit anderen Plattform-spezifischen Feldern.

## CSV-Schema (`audits/google-ads-anzeigen.csv`)

UTF-8, mit Header, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,werbender_name,werbender_verifiziert,
anzeige_id,anzeige_typ,format,erst_schalt_datum,letzte_anzeige_datum,
aktive_in_regionen,in_zielregion,
werbetext_headline,werbetext_beschreibung,
landingpage_url,landingpage_tiefe,creative_url,
cluster,datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string (kebab-case) | ja | aus `liste.md` / `meta.json` |
| `akteurs_typ` | enum | ja | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Anzeigename |
| `werbender_name` | string | ja | TC-Display-Name (kann von akteurs_name abweichen) |
| `werbender_verifiziert` | bool | ja | TC-Verifizierungsstatus |
| `anzeige_id` | string | ja | TC-ID oder generierter Hash |
| `anzeige_typ` | enum | ja | `search | display | video | shopping | demand_gen | unbekannt` |
| `format` | enum | ja | `text | image | video | responsive_search | responsive_display | unbekannt` |
| `erst_schalt_datum` | ISO-8601 | ja | Datum oder Monatserster bei Monats-Granularität |
| `letzte_anzeige_datum` | ISO-8601 / leer | nein | nur bei pausierten Anzeigen |
| `aktive_in_regionen` | string | ja | Komma-getrennte ISO-Country-Codes |
| `in_zielregion` | bool | ja | true wenn Region matched `meta.json.region` |
| `werbetext_headline` | string / leer | nein | Search-Ads-Headline (bei Display/Video oft leer) |
| `werbetext_beschreibung` | string / leer | nein | Search-Ads-Body |
| `landingpage_url` | URL | ja | Ziel-URL der Anzeige inkl. UTM-Params |
| `landingpage_tiefe` | int | ja | Pfad-Tiefe (0 = Homepage, 1+ = Sub-Pages) |
| `creative_url` | URL / leer | nein | nur bei Display/Video |
| `cluster` | string | ja | aus Schritt 6: `branded | conquest_<wb> | thema_<token> | generic` |
| `datenstand_iso` | ISO-8601 | ja | Datum des Scrapes |

### Sortierung

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` alphabetisch
3. `in_zielregion` true zuerst
4. `erst_schalt_datum` absteigend (jüngste zuerst)
5. `anzeige_id` als Tiebreaker für Stabilität

### Größen-Grenze

Pro Akteur Hard-Cap 100 Anzeigen. Bei 10 Akteuren = max 1000 Zeilen.

## Markdown-Schema (`audits/google-ads.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-05-sea-google-ads-check
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only
  liste_bestaetigt_am: <ISO-8601 oder null>

quelle:
  tool: google_ads_transparency_center
  scraper: <z.B. apify/google-ads-transparency-center-scraper>
  datenstand: <ISO-8601>

spyfu_modus: voll | reduced | aus
spyfu_wechselkurs_usd_eur: <float wenn voll/reduced>

# === Aktivitäts-Matrix pro Akteur ===
akteure:
  - akteurs_slug: <slug>
    name: <Anzeigename>
    typ: kunde | wettbewerber
    kategorie_wenn_wb: <kunde_genannt | regional | best_practice_ueberregional | null>
    domain: <normalisierte Domain>
    aktiv_im_transparency_center: true | false
    anzahl_aktive_anzeigen: <int>
    anzahl_in_zielregion: <int>
    anzeigentypen_verteilung:
      search: <int>
      display: <int>
      video: <int>
      shopping: <int>
      demand_gen: <int>
      unbekannt: <int>
    aelteste_schalt_datum: <ISO-8601 oder null>
    juengste_schalt_datum: <ISO-8601 oder null>
    cluster_anzahl: <int>
    cluster_top_3: [<liste der 3 größten Cluster im Akteurs-Portfolio>]
    landingpage_tiefe_durchschnitt: <float>
    spyfu_anreicherung:
      verfuegbar: <true | false>
      monatliche_paid_clicks_estimate: <int oder null>
      monatlicher_spend_eur_min: <int oder null>
      monatlicher_spend_eur_max: <int oder null>
      paid_keywords_count: <int oder null>
      hinweise: <string>
    raw_pfad: <relativer Pfad zu audits/raw/google-ads-<slug>.json>

# === Themen-Cluster über alle Akteure ===
themen_cluster:
  - cluster_name: <string>
    typ: branded | conquest_<wb> | thema | generic
    anzeigen_anzahl: <int>
    aktive_akteure: [<liste>]
    beispiel_werbetext: <auszug>

# === Aggregat-Statistik ===
statistiken:
  akteure_total: <int>
  akteure_aktiv_im_tc: <int>
  akteure_inaktiv_im_tc: <int>
  anzeigen_total: <int>
  anzeigen_in_zielregion: <int>
  top_werber:
    akteurs_slug: <slug>
    anzahl_anzeigen: <int>
  branchen_sea_dichte: <gering | mittel | hoch>   # heuristisch: < 30% aktive = gering, 30-70% = mittel, > 70% = hoch
  conquest_aktivitaeten: <int>   # Anzahl WBs, die Kunden-Brand bewerben
  kunde_betreibt_conquest_gegen: [<liste der wb_slugs>]

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <enum: kunde_inaktiv_wb_aktiv | kunde_aktiv_wb_inaktiv | conquest_aktivitaet | kunde_macht_conquest | geringe_ads_dichte_branche | hohe_ads_dichte_branche | werbetext_cluster_dominant | landingpage_qualitaet_inkonsistent>
    titel: <string>
    beschreibung: <1-2 Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion>
    betroffene_akteure: [<slugs>]
---

# Google-Ads-Aktivität: <Kundenname>

## Übersicht

3-5 Sätze: wie viele Akteure aktiv, Top-Werber, SEA-Dichte der Branche, Top-1-2-Auffälligkeiten.

## Akteurs-Vergleichs-Tabelle

| Akteur | Typ | TC-aktiv | Anzeigen (DE) | Search | Display | Video | Shopping | Spend (EUR/Mo) | Cluster |
|---|---|---|---|---|---|---|---|---|---|
| Mustermann GmbH | Kunde | ✓ | 12 | 8 | 3 | 1 | 0 | 4.000-8.000 | 3 |
| Beta Solutions | WB | ✓ | 47 | 32 | 8 | 5 | 2 | 25.000-50.000 | 7 |
| Alpha Tech | WB | ✗ | 0 | – | – | – | – | – | – |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

Spend nur wenn SpyFu verfügbar. "TC-aktiv: ✗" heißt: keine Anzeigen im TC gefunden — kann "kein SEA" oder "nicht verifiziert" bedeuten.

## Pro Akteur

### <Akteur 1>

**Aktivitäts-Status**: aktiv mit X Anzeigen (Y in Zielregion).

**Anzeigentypen-Verteilung**:

```
Search    ▓▓▓▓▓▓▓ 8
Display   ▓▓▓ 3
Video     ▓ 1
Shopping  0
```

**Top-Anzeigen** (max 5):

- "Aufmaß-Werkzeuge — Profi-Qualität ab 49 €" · Search · seit 2025-09 · DE
  - LP: /produkte/aufmasswerkzeuge/
- ...

**Themen-Cluster im Portfolio**:

- `thema_aufmass` (5 Anzeigen) — Hauptthema
- `branded` (4 Anzeigen) — Brand-Defense
- `thema_kabel` (3 Anzeigen)

**SpyFu-Daten** (falls verfügbar):

- Geschätzte monatliche Klicks: 1.200
- Geschätzte monatliche Spend: 4.000 € – 8.000 €
- Paid-Keywords gesamt: 87

(... weitere Akteure ...)

## Themen-Cluster über alle Akteure

Welche Themen werden im Branchen-Werbe-Markt am häufigsten bespielt? Hilft zu sehen, welche Themen umkämpft sind und welche frei.

| Cluster | Aktive Akteure | Anzeigen | Beispiel-Werbetext |
|---|---|---|---|
| thema_aufmass | 6 von 9 | 47 | "Schnelles Aufmaß-Werkzeug — sofort lieferbar" |
| thema_kabel | 4 von 9 | 28 | "Profi-Kabel für jeden Einsatz" |
| branded | 8 von 9 | 32 | (eigene Markennamen) |
| conquest | 2 von 9 | 6 | "Suchen Sie Alternative zu Mustermann?" |
| generic | 5 von 9 | 21 | "Handwerker-Werkzeuge online kaufen" |

## Branchen-SEA-Lage

- **SEA-Dichte**: <gering | mittel | hoch> — N von M Akteure schalten aktiv
- **Spend-Bandbreite** (wenn SpyFu): von <min> bis <max> EUR/Monat in der Wettbewerbsgruppe
- **Format-Mix**: Search dominiert (X%), Display und Video selten

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach Relevanz)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Handlungs-Empfehlung**: ...

**Betroffene Akteure**: ...

(weitere Auffälligkeiten ...)

## Lücken und Hinweise

- Akteure ohne TC-Eintrag: <Liste> — "kein SEA" oder "nicht verifiziert"?
- SpyFu-Lücken (Quota überschritten / Domain nicht erfasst): <Liste>
- Internationale Anzeigen (außerhalb Zielregion): <Anzahl> — in `audits/google-ads-anzeigen.csv` mit `in_zielregion: false` markiert
- TC-Limitierungen: keine Spend-Daten ohne SpyFu, kein Keyword-Targeting sichtbar, kein Quality-Score
```

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jeder Akteur in `akteure`-Liste mit `aktiv_im_transparency_center: true` hat mindestens eine zugehörige Anzeige in der CSV
2. `anzahl_aktive_anzeigen` = Anzahl Zeilen in CSV für diesen Akteur
3. `anzahl_in_zielregion` = Anzahl Zeilen mit `in_zielregion: true`
4. Jede Anzeige in CSV hat einen `akteurs_slug`, der in `akteure`-Liste vorkommt
5. `werbetext_headline` darf leer sein (nicht-Search-Ads), aber bei `anzeige_typ: search` muss sie gefüllt sein
6. `cluster`-Wert ist konsistent mit `themen_cluster`-Liste im Frontmatter
7. `statistiken.akteure_aktiv_im_tc` + `statistiken.akteure_inaktiv_im_tc` = `akteure_total`
8. `landingpage_tiefe` ist int ≥ 0
9. `creative_url` nur gefüllt bei `anzeige_typ` in {display, video, shopping}
10. `spyfu_anreicherung.verfuegbar: false` → alle Spend-Felder müssen `null` sein

Bei Verletzung: konkrete Fehlermeldung im Skill-Schluss-Format.

## Wie Folge-Skills die Outputs lesen

### `04-02-kanal-chancen-analyse`

Liest aus `google-ads.md` Frontmatter:

- `statistiken.branchen_sea_dichte` → Channel-Empfehlung (gering = Wachstums-Chance, hoch = teure Mitspielen)
- `akteure[i].anzahl_aktive_anzeigen` und Kunden-Aktivität → ist SEA bereits Kanal des Kunden?
- `auffaelligkeiten` mit `typ: conquest_aktivitaet | kunde_inaktiv_wb_aktiv` → strategische Argumente

### `04-04-forecast-modell`

Liest:

- `akteure[i].spyfu_anreicherung.monatlicher_spend_eur_*` → Spend-Referenz für eigenen Forecast
- `akteure[i].anzahl_aktive_anzeigen` → Aktivitäts-Größenordnung

### `04-05-90-tage-plan`

Liest:

- `auffaelligkeiten` mit hoher Relevanz → konkrete 90-Tage-Maßnahmen (z. B. "Conquest-Schutz aktivieren")
- `themen_cluster` → wo der Kunde noch nicht spielt → Cluster-spezifische Kampagnen-Vorschläge

### `05-01-mta-slide-bausteine`

- Akteurs-Vergleichs-Tabelle direkt als Slide-Tabelle
- Top-Anzeigen-Beispiele für die "Wettbewerber-Werbung"-Slide
- Auffälligkeiten als "Insights"-Slides

## Hinweis zu den Folge-Ads-Skills

`03-06-sea-meta-ads-library-check` und `03-07-sea-linkedin-ads-library-check` folgen demselben Output-Pattern:

- Plattform-spezifische CSV mit ähnlichen Spalten (mit Plattform-Anpassungen wie Targeting-Daten bei Meta)
- Plattform-spezifischer Aggregat-Markdown
- Identische Auffälligkeits-Typen-Familie (kunde_inaktiv_wb_aktiv etc.)

Das vereinheitlicht die Folge-Skill-Auswertung in `04-02-kanal-chancen-analyse` — ein Synthese-Skill kann pro Plattform identische Pattern-Logik anwenden.
