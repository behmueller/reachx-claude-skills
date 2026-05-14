# Ausgabe-Schema

Definiert die Output-Formate des Skills für die Pflicht-Dateien:

- `audits/seo-sichtbarkeit.md` — Aggregat-Markdown mit YAML-Frontmatter (für die MTA-Story), inkl. Sistrix-Sicht + Ahrefs-Sicht
- `audits/seo-keywords.csv` — Sistrix-primäre Roh-Daten + Ahrefs-Anreicherung (für die SEO-Folge-Skills)
- `audits/seo-rankings-ahrefs.csv` — Ahrefs-Parallel-Roh-Daten (nur Hybrid-Modus, ergänzend)

Alle Dateien sind verbindlich für die Folge-Skills — Schema-Änderungen brauchen Versions-Bump (siehe `contracts.md`).

**Aktuelle Schema-Version: 1.1** (Bump gegenüber 1.0 wegen Ahrefs-Anreicherung in `seo-keywords.csv` und neuer Datei `seo-rankings-ahrefs.csv`).

## Markdown-Schema (`audits/seo-sichtbarkeit.md`)

```markdown
---
# === Skill-Metadaten ===
skill: 03-01-seo-sichtbarkeit-und-rankings
generiert_am: <ISO-8601>
schema_version: "1.1"
modus: <voll_hybrid | hybrid_kunden_only | reduced | reduced_kunden_only>

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste: wettbewerber/liste.md   # null wenn Kunden-only-Modus
  liste_bestaetigt_am: <ISO-8601 oder null>
quelle:
  sistrix:
    zugang: <mcp | http_api>
    country: de
    datenstand: <ISO-8601>
    mobile: <true | false>
  ahrefs:
    zugang: <mcp | null | unterbrochen>    # null im Reduced-Modus
    mode: subdomains
    country: de
    datenstand: <ISO-8601 oder null>
    units_verbraucht_geschaetzt: <int oder null>
    restbudget_units: <int oder null>     # aus subscription-info-limits-and-usage

# === Akteurs-Liste ===
akteure:
  - akteurs_slug: <kebab-case>
    name: <Anzeigename>
    typ: <kunde | wettbewerber>
    kategorie_wenn_wettbewerber: <kunde_genannt | regional | best_practice_ueberregional | null>
    domain: <normalisierte Domain ohne www>

    # --- Sistrix-Block ---
    sistrix_indexiert: <true | false>
    visibility_aktuell: <float oder null>
    visibility_vor_12m: <float oder null>
    visibility_12m_min: <float oder null>
    visibility_12m_max: <float oder null>
    trend_richtung: <steigend | fallend | stabil | unbekannt>
    trend_prozent_12m: <float oder null>
    keywords_indexiert_gesamt: <int oder null>
    keywords_erfasst_im_csv: <int>
    rang_im_vergleich: <int>                # 1 = höchster SI

    # --- Ahrefs-Block (null im Reduced-Modus) ---
    ahrefs_indexiert: <true | false | null>
    ahrefs_dr_aktuell: <float oder null>          # 0-100
    ahrefs_dr_vor_12m: <float oder null>
    ahrefs_dr_trend_prozent_12m: <float oder null>
    ahrefs_dr_trend_richtung: <steigend | fallend | stabil | unbekannt | null>
    ahrefs_org_keywords: <int oder null>
    ahrefs_org_traffic: <int oder null>           # geschaetzte Klicks pro Monat
    ahrefs_paid_keywords: <int oder null>
    ahrefs_keywords_erfasst_im_csv: <int oder null>   # wie viele in seo-rankings-ahrefs.csv
    ahrefs_rang_dr_im_vergleich: <int oder null>      # 1 = hoechstes DR

    # --- Raw-Pfade ---
    raw_pfad_sistrix: <relativer Pfad zu audits/raw/sistrix-<slug>.json>
    raw_pfade_ahrefs:                             # leer im Reduced-Modus
      - <relativer Pfad zu audits/raw/ahrefs-metrics-<slug>.json>
      - <relativer Pfad zu audits/raw/ahrefs-metrics-history-<slug>.json>
      - <relativer Pfad zu audits/raw/ahrefs-domain-rating-<slug>.json>
      - <relativer Pfad zu audits/raw/ahrefs-domain-rating-history-<slug>.json>
      - <relativer Pfad zu audits/raw/ahrefs-organic-keywords-<slug>.json>
      - <relativer Pfad zu audits/raw/ahrefs-organic-competitors-<slug>.json>

# === Sistrix-vorgeschlagene Wettbewerber pro Akteur ===
sistrix_vorgeschlagene_wettbewerber:
  - fuer_akteurs_slug: <slug>
    vorschlaege:
      - domain: <vorgeschlagene Domain>
        visibility: <float>
        overlap_score: <float oder null>
        bereits_in_liste: <true | false>
        auch_ahrefs_wb: <true | false>          # Schnittmenge-Marker, false im Reduced-Modus

# === Ahrefs-vorgeschlagene Wettbewerber pro Akteur (leer im Reduced-Modus) ===
ahrefs_vorgeschlagene_wettbewerber:
  - fuer_akteurs_slug: <slug>
    vorschlaege:
      - domain: <vorgeschlagene Domain>
        keywords_common: <int>
        keywords_competitor: <int>
        domain_rating: <float>
        traffic: <int>
        bereits_in_liste: <true | false>
        auch_sistrix_wb: <true | false>         # Schnittmenge-Marker

# === Wettbewerber-Schnittmenge Sistrix ∩ Ahrefs (aggregiert, leer im Reduced-Modus) ===
wettbewerber_schnittmenge:
  - domain: <vorgeschlagene Domain>
    haeufigkeit_sistrix: <int>            # bei wie vielen Akteuren als Sistrix-WB
    haeufigkeit_ahrefs: <int>             # bei wie vielen Akteuren als Ahrefs-WB
    bereits_in_liste: <true | false>
    handlungs_empfehlung: <z.B. "in liste.md aufnehmen">

# === Aggregat-Statistik ===
statistiken:
  akteure_total: <int>
  akteure_indexiert_sistrix: <int>
  akteure_nicht_indexiert_sistrix: <int>
  akteure_indexiert_ahrefs: <int oder null>          # null im Reduced-Modus
  akteure_nur_ahrefs_indexiert: <int oder null>      # Sistrix nein, Ahrefs ja
  kunde_visibility_aktuell: <float oder null>
  kunde_rang_sistrix: <int oder null>
  kunde_trend_si_12m_prozent: <float oder null>
  kunde_dr_aktuell: <float oder null>
  kunde_rang_dr: <int oder null>
  kunde_trend_dr_12m_prozent: <float oder null>
  kunde_ahrefs_org_traffic: <int oder null>
  top_visibility: <float>
  top_visibility_akteur: <slug>
  top_dr: <float oder null>
  top_dr_akteur: <slug oder null>
  median_visibility: <float>
  median_dr: <float oder null>
  luecke_kunde_zu_top_absolut_si: <float>
  luecke_kunde_zu_top_relativ_si: <float>           # Prozent
  luecke_kunde_zu_top_absolut_dr: <float oder null>
  csv_zeilen_gesamt_sistrix: <int>
  csv_zeilen_gesamt_ahrefs: <int oder null>
  ahrefs_match_rate_prozent: <float oder null>      # wie viel % der Sistrix-Keywords bekamen Ahrefs-Match

# === Volumen-Diskrepanzen (leer im Reduced-Modus) ===
volumen_diskrepanzen:
  - keyword: <string>
    domain: <string>
    sistrix_volumen: <int>
    ahrefs_volumen: <int>
    abweichung_prozent: <float>             # positiv = Sistrix höher

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <kunde_unter_median | kunde_top | wettbewerber_dominant | trend_kunde_negativ | trend_kunde_positiv | sistrix_wb_nicht_in_liste | keyword_cluster_dominant | nicht_indiziert_haeufig | volumen_diskrepanz_sistrix_ahrefs | wettbewerber_schnittmenge_stark | wettbewerber_nur_ahrefs | wettbewerber_nur_sistrix | traffic_dr_diskrepanz | nur_ahrefs_indexiert | sonstige>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    quelle: <sistrix | ahrefs | beide>     # welche Datenquelle den Befund erzeugt hat
    handlungs_empfehlung: <konkrete Aktion für die MTA-Slide>
    betroffene_akteure: [<liste der akteurs_slugs>]
    betroffene_domains: [<liste der Domains, falls Auffälligkeit Domain-spezifisch ist>]
---

# SEO-Sichtbarkeit und Rankings: <Kundenname>

## Übersicht

3-5 Sätze: was ist die Datenbasis (Anzahl Akteure, Datenstand, Modus: Voll-Hybrid / Reduced), wo steht der Kunde, was sind die Top-1-2-Auffälligkeiten. **Wichtig**: Sistrix-Sichtbarkeitsindex (SI) und Ahrefs-Domain-Rating (DR) sind verschiedene Skalen — nicht vermischen.

## Sistrix-Sicht (Leit-Datenquelle)

### Ranking nach Sichtbarkeitsindex

Tabelle aller Akteure, sortiert nach `visibility_aktuell` absteigend (nicht-indexierte unten):

| Rang | Akteur | Typ | Domain | SI aktuell | SI vor 12M | Trend | Top-3 Keywords |
|---|---|---|---|---|---|---|---|
| 1 | … | WB best_practice | … | 0.84 | 0.71 | ↑ +18% | … |
| 2 | … | Kunde | … | 0.21 | 0.17 | ↑ +24% | … |
| … | … | … | … | … | … | … | … |
| — | WB-X | WB regional | … | nicht indexiert | — | — | — |

Trend-Pfeile: `↑` für `steigend`, `↓` für `fallend`, `→` für `stabil`, `?` für `unbekannt`.

### Sichtbarkeitsindex-Verlauf (12 Monate)

Beschreibung der wichtigsten Verlauf-Pattern (welcher Akteur stärkster Gewinner/Verlierer, synchrone Bewegungen, Kunde vs. Branche).

### Pro Akteur (Sistrix)

#### <Akteur 1>

- SI-Verlauf 12M: Min X,XX → Max X,XX, aktuell X,XX
- Indexierte Keywords gesamt: N
- Top-Keywords erfasst (in CSV): M
- Top-10 Keywords (Auszug):

| Keyword | Position | Suchvolumen | Ranking-URL |
|---|---|---|---|
| … | 3 | 1.900 | … |

**Sistrix-vorgeschlagene Wettbewerber (Top 5)**:

- domain-a.de (SI 0.45) — bereits in liste.md
- domain-b.de (SI 0.32) — **nicht in liste.md** → Stratege prüfen, **auch Ahrefs-WB**: ja/nein

### Sistrix-eigene Wettbewerbs-Cluster

| Vorgeschlagene Domain | Häufigkeit | Avg-Overlap | Status |
|---|---|---|---|
| domain-x.de | 5 von 9 Akteuren | 0.42 | nicht in liste.md → Strategen-Review |

## Ahrefs-Sicht (parallele Lesart, nur Hybrid-Modus)

**Skala-Hinweis**: DR (0-100) misst Backlink-Stärke. `org_traffic` ist eine klickbasierte Schätzung. Beide Werte sind nicht in den Sistrix-Sichtbarkeitsindex umrechenbar.

### Domain Rating und Traffic-Schätzung

| Rang | Akteur | Typ | Domain | DR aktuell | DR vor 12M | DR-Trend | org. Traffic (Klicks/Monat) | org. Keywords |
|---|---|---|---|---|---|---|---|---|
| 1 | … | WB best_practice | … | 68 | 62 | ↑ +10% | 24.500 | 8.200 |
| 2 | … | Kunde | … | 42 | 38 | ↑ +11% | 3.800 | 1.150 |

### DR-Verlauf (12 Monate)

Beschreibung der DR-Trends. Sistrix sieht Backlink-Trends nicht — diese Sektion ist Ahrefs-spezifisch.

### Pro Akteur (Ahrefs)

#### <Akteur 1>

- DR-Verlauf 12M: Min XX → Max XX, aktuell XX
- org. Traffic-Schätzung: ca. NNN Klicks/Monat
- Top-10 Ahrefs-Keywords (sortiert nach `sum_traffic`):

| Keyword | Volume | KD | Position | Intent | Traffic |
|---|---|---|---|---|---|
| … | 720 | 28 | 4 | C, I | 180 |

Intent-Spalten-Kürzel: `B` = branded, `T` = transactional, `C` = commercial, `I` = informational. Mehrere Flags möglich.

**Ahrefs-vorgeschlagene Wettbewerber (Top 5)**:

- domain-a.de (DR 58, common 320 KW) — bereits in liste.md, **auch Sistrix-WB**: ja
- domain-c.de (DR 64, common 280 KW) — nicht in liste.md → Strategen-Review

### Ahrefs-eigene Wettbewerbs-Cluster

| Vorgeschlagene Domain | Häufigkeit Ahrefs | Avg DR | Status |
|---|---|---|---|

## Wettbewerber-Schnittmenge Sistrix ∩ Ahrefs (nur Hybrid-Modus)

Domains, die in **beiden** Tool-Listen als Wettbewerber auftauchen → starkes Signal:

| Domain | Bei Sistrix-WBs | Bei Ahrefs-WBs | bereits in liste.md | Empfehlung |
|---|---|---|---|---|
| domain-x.de | 5 von 9 | 4 von 9 | nein | in liste.md aufnehmen, neuen 02-02-wettbewerber-identifikation-Lauf erwägen |

## Wichtige Werte-Diskrepanzen (nur Hybrid-Modus)

Sistrix-Volumen und Ahrefs-Volumen weichen bei DACH-Keywords häufig 1,5–3× ab. Für die Top-Keywords des Kunden:

| Keyword | Domain | Sistrix-Vol | Ahrefs-Vol | Abweichung |
|---|---|---|---|---|
| kabel messen | mustermann.de | 1.900 | 720 | -62% |

→ In der MTA-Slide: auf Quellen-Mix hinweisen, nicht eine Zahl als Wahrheit verkaufen.

## Auffälligkeiten

(aus Frontmatter rendered, sortiert nach `relevanz: hoch` → `mittel` → `niedrig`)

### <Auffälligkeit 1 — Titel>

Beschreibung in 1-2 Sätzen.

**Quelle**: <sistrix | ahrefs | beide>
**Handlungs-Empfehlung**: …
**Betroffen**: Akteur A, Akteur B

## Lücken und Hinweise

- Liste der nicht-indexierten Domains (Sistrix und Ahrefs getrennt ausweisen)
- Domains mit `recherche_fehlgeschlagen` und Fehler-Typ
- Falls Mobile-SI-Lauf optional ausgelassen: Hinweis, dass Mobile-Differenz möglicherweise relevant ist
- Ahrefs-Match-Rate: X% der Sistrix-Keywords haben einen Ahrefs-Match bekommen (niedrige Werte = Sistrix sieht viele Keywords, die Ahrefs nicht hat — typisch für DACH-Long-Tail)
- Im Reduced-Modus: Hinweis "Ahrefs-Sicht entfällt, weil Ahrefs-MCP nicht verfügbar war"
```

## CSV-Schema (`audits/seo-keywords.csv`) — Sistrix-primär + Ahrefs-angereichert

UTF-8, mit Header-Zeile, Komma-getrennt, doppelte Anführungszeichen für Werte mit Komma/Zeilenumbruch.

**Zentrale Designentscheidung**: Sistrix-Keywords sind die Basis (eine Zeile pro Sistrix-Keyword pro Akteur). Wo Ahrefs für dasselbe Keyword Daten liefert, werden die Ahrefs-Spalten angereichert. Wo nicht, bleiben sie leer. Im Reduced-Modus (kein Ahrefs) bleiben alle Ahrefs-Spalten leer, das Schema bleibt aber stabil — Folge-Skills lesen so oder so dieselben Spalten.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,domain,keyword,position,suchvolumen,ranking_url,sistrix_competition,kwid,datenstand_iso,ahrefs_volume,ahrefs_kd,ahrefs_sum_traffic,intent_branded,intent_transactional,intent_commercial,intent_informational
```

| Spalte | Datentyp | Pflicht | Quelle | Beschreibung |
|---|---|---|---|---|
| `akteurs_slug` | string (kebab-case) | ja | Skill | Akteurs-Slug aus Frontmatter |
| `akteurs_typ` | string | ja | Skill | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Skill | Anzeigename für Excel-Lesbarkeit |
| `domain` | string | ja | Skill | normalisierte Domain ohne www |
| `keyword` | string | ja | Sistrix | Keyword-Text (Sistrix-Schreibweise) |
| `position` | integer | ja | Sistrix | aktuelle Position 1–100 |
| `suchvolumen` | integer | ja | Sistrix | monatliches Suchvolumen laut Sistrix |
| `ranking_url` | string (URL) | ja | Sistrix | URL der Seite, die rankt |
| `sistrix_competition` | float oder leer | nein | Sistrix | CPC-basierter Konkurrenz-Score |
| `kwid` | integer oder leer | nein | Sistrix | Sistrix-Keyword-ID |
| `datenstand_iso` | ISO-8601 | ja | Sistrix | Sistrix-Datenstand |
| `ahrefs_volume` | integer oder leer | nein | Ahrefs | Suchvolumen laut Ahrefs für dasselbe Keyword (leer, wenn kein Match oder Reduced-Modus) |
| `ahrefs_kd` | integer oder leer | nein | Ahrefs | Keyword Difficulty 0-100 |
| `ahrefs_sum_traffic` | integer oder leer | nein | Ahrefs | Ahrefs-Traffic-Beitrag dieses Keywords für die Domain |
| `intent_branded` | 0/1 oder leer | nein | Ahrefs | Branded-Intent-Flag |
| `intent_transactional` | 0/1 oder leer | nein | Ahrefs | Transactional-Intent-Flag |
| `intent_commercial` | 0/1 oder leer | nein | Ahrefs | Commercial-Intent-Flag |
| `intent_informational` | 0/1 oder leer | nein | Ahrefs | Informational-Intent-Flag |

### Match-Strategie für die Ahrefs-Anreicherung

Pro Sistrix-Keyword-Zeile sucht der Skill in der Ahrefs-Organic-Keywords-Antwort **derselben Domain** nach einem Match. Match-Regel:

1. Beide Keywords lowercase
2. Whitespace-trim
3. Mehrfach-Spaces zu einem reduzieren
4. Bindestrich-Toleranz: "online-shop" matched "online shop"

Bei Match → Ahrefs-Spalten füllen. Ohne Match → Ahrefs-Spalten bleiben leer.

### Beispiel

```csv
akteurs_slug,akteurs_typ,akteurs_name,domain,keyword,position,suchvolumen,ranking_url,sistrix_competition,kwid,datenstand_iso,ahrefs_volume,ahrefs_kd,ahrefs_sum_traffic,intent_branded,intent_transactional,intent_commercial,intent_informational
mustermann,kunde,Mustermann GmbH,mustermann.de,kabel messen,4,1900,https://mustermann.de/produkte/kabel-messer,0.42,123456,2026-05-13,720,28,180,0,0,1,1
mustermann,kunde,Mustermann GmbH,mustermann.de,aufmaß werkzeug,7,720,https://mustermann.de/aufmass,0.31,123457,2026-05-13,290,15,42,0,1,1,0
mustermann,kunde,Mustermann GmbH,mustermann.de,reachx mta,1,40,https://mustermann.de/case,,123459,2026-05-13,,,,,,,
beta-solutions,wettbewerber,Beta Solutions,beta-solutions.com,kabel messen,2,1900,https://beta-solutions.com/produkt/messer,0.42,123456,2026-05-13,720,28,940,0,0,1,1
beta-solutions,wettbewerber,Beta Solutions,beta-solutions.com,handwerker werkzeug,12,4400,https://beta-solutions.com/werkzeuge,0.51,123458,2026-05-13,1800,42,120,0,1,1,0
```

Zeile 3 zeigt eine Keyword-Zeile ohne Ahrefs-Match (Ahrefs kennt das Keyword für diese Domain nicht oder nur unter anderer Schreibweise).

### Sortierung

Innerhalb der Datei nach:

1. `akteurs_typ` (Kunde zuerst, dann Wettbewerber)
2. `akteurs_slug` (alphabetisch)
3. `position` aufsteigend (Top-Positionen zuerst)

### Größen-Grenze

Hard-Cap: 200 Keywords pro Akteur (Sistrix-Seite). Bei 10 Akteuren maximal 2000 Zeilen.

## CSV-Schema (`audits/seo-rankings-ahrefs.csv`) — Ahrefs-Parallel-Datei (nur Hybrid-Modus)

**Wird nur geschrieben, wenn Ahrefs-MCP verfügbar war.** Im Reduced-Modus überspringt der Skill diese Datei komplett (keine leere Datei erzeugen, sondern gar nicht anlegen).

Begründung für eigene Datei: Ahrefs liefert eine **eigene Top-Keyword-Liste** pro Domain mit eigener Sortierung (nach `sum_traffic`). Viele dieser Keywords sind nicht in der Sistrix-Top-200 und würden in `seo-keywords.csv` keine Zeile haben. Die separate Datei macht beide Sichten sauber lesbar.

### Spalten (in fester Reihenfolge)

```
akteurs_slug,akteurs_typ,akteurs_name,domain,keyword,ahrefs_volume,ahrefs_kd,best_position,best_position_url,ahrefs_sum_traffic,intent_branded,intent_transactional,intent_commercial,intent_informational,datenstand_iso
```

| Spalte | Datentyp | Pflicht | Beschreibung |
|---|---|---|---|
| `akteurs_slug` | string | ja | Akteurs-Slug |
| `akteurs_typ` | string | ja | `kunde` oder `wettbewerber` |
| `akteurs_name` | string | ja | Anzeigename |
| `domain` | string | ja | normalisierte Domain |
| `keyword` | string | ja | Keyword-Text (Ahrefs-Schreibweise) |
| `ahrefs_volume` | integer | ja | Ahrefs-Suchvolumen |
| `ahrefs_kd` | integer | ja | Keyword Difficulty 0-100 |
| `best_position` | integer | ja | beste Position der Domain für dieses Keyword |
| `best_position_url` | string (URL) | ja | URL, die rankt |
| `ahrefs_sum_traffic` | integer | ja | geschätzter Traffic-Beitrag (Klicks/Monat) |
| `intent_branded` | 0/1 | ja | Branded-Intent |
| `intent_transactional` | 0/1 | ja | Transactional-Intent |
| `intent_commercial` | 0/1 | ja | Commercial-Intent |
| `intent_informational` | 0/1 | ja | Informational-Intent |
| `datenstand_iso` | ISO-8601 | ja | Ahrefs-Datenstand |

### Beispiel

```csv
akteurs_slug,akteurs_typ,akteurs_name,domain,keyword,ahrefs_volume,ahrefs_kd,best_position,best_position_url,ahrefs_sum_traffic,intent_branded,intent_transactional,intent_commercial,intent_informational,datenstand_iso
mustermann,kunde,Mustermann GmbH,mustermann.de,kabel messen,720,28,4,https://mustermann.de/produkte/kabel-messer,180,0,0,1,1,2026-05-14
mustermann,kunde,Mustermann GmbH,mustermann.de,handwerker zubehör online,540,32,8,https://mustermann.de/zubehoer,95,0,1,1,0,2026-05-14
beta-solutions,wettbewerber,Beta Solutions,beta-solutions.com,kabel messen,720,28,2,https://beta-solutions.com/produkt/messer,940,0,0,1,1,2026-05-14
```

### Sortierung

Innerhalb der Datei nach:

1. `akteurs_typ` (Kunde zuerst)
2. `akteurs_slug` (alphabetisch)
3. `ahrefs_sum_traffic` absteigend (Top-Traffic-Keywords zuerst)

### Größen-Grenze

Default 100 Keywords pro Akteur. Bei 10 Akteuren maximal 1000 Zeilen. Limit konfigurierbar in der Ahrefs-API-Konvention (`reference/ahrefs-api-nutzung.md`).

## Wie Folge-Skills die Outputs lesen

### `03-02-seo-keyword-recherche`

Liest **primär** `audits/seo-keywords.csv` als Basis-Keywords. Wenn `audits/seo-rankings-ahrefs.csv` existiert (Hybrid-Modus), liest sie zusätzlich für Keywords, die Sistrix nicht sieht. Ergänzt um:

- Long-Tail-Variationen (eigene Sistrix-Queries)
- Wettbewerbs-Gaps (Keywords, auf denen WB rankt, Kunde nicht — wird über beide CSVs ermittelt)
- Ahrefs-Difficulty für die Top-Kandidaten — wenn schon in der Anreicherung enthalten, **nicht erneut abfragen** (Unit-Spar)

Output: erweitertes `audits/seo-keyword-pool.csv` mit zusätzlichen Spalten (`difficulty`, `intent_hypothese`, `quelle: sistrix | ahrefs | seed`).

### `03-03-seo-keyword-kategorisierung`

Liest `audits/seo-keyword-pool.csv` (Output des vorherigen Skills). Die Intent-Flags aus `audits/seo-keywords.csv` / `audits/seo-rankings-ahrefs.csv` werden als **Hypothese** für den Schema-vor-Lauf genutzt — wenn Ahrefs `is_commercial=1` und `is_transactional=1` setzt, ist das ein starkes Signal für BOFU-Einordnung.

Ergänzt um:

- `cluster` (z. B. "Branded", "Generic-Mid-Tail", "Long-Tail-Anwendungsfall")
- `intent_typ` (informational / navigational / commercial / transactional)
- `funnel_stufe` (TOFU / MOFU / BOFU)

Liest **nicht** `audits/seo-sichtbarkeit.md` direkt — die Aggregat-Markdown ist primär für Strategen, nicht für Maschinen.

### `04-02-kanal-chancen-analyse`

Liest aus `audits/seo-sichtbarkeit.md` Frontmatter:

- `statistiken.kunde_rang_sistrix`, `luecke_kunde_zu_top_*_si` → Bewertung "wie viel Aufholbedarf hat der Kunde im organischen Ranking?"
- `statistiken.kunde_dr_aktuell`, `luecke_kunde_zu_top_absolut_dr` → Bewertung "wie viel Backlink-Autorität fehlt?"
- `auffaelligkeiten` mit `typ: trend_kunde_negativ`, `keyword_cluster_dominant`, `wettbewerber_schnittmenge_stark`, `traffic_dr_diskrepanz` → strategische Story

## Validierungs-Regeln

Vor dem Schreiben prüft der Skill:

1. Jeder Akteur in der Frontmatter-Liste hat entweder `sistrix_indexiert: false` oder `visibility_aktuell` als float
2. Bei `sistrix_indexiert: true`: `raw_pfad_sistrix` zeigt auf existierende Datei
3. Im Hybrid-Modus: Jeder Akteur hat `ahrefs_indexiert` als `true | false`, nie `null`
4. Im Hybrid-Modus bei `ahrefs_indexiert: true`: `raw_pfade_ahrefs` enthält mindestens den `metrics`- und den `organic-keywords`-Pfad und beide Dateien existieren
5. CSV `seo-keywords.csv`: jede Zeile hat alle Sistrix-Pflicht-Spalten gefüllt (Ahrefs-Spalten dürfen leer sein)
6. CSV `seo-keywords.csv`: `akteurs_slug` in jeder Zeile existiert auch in `akteure`-Liste der Markdown
7. Im Hybrid-Modus: `seo-rankings-ahrefs.csv` existiert und jede Zeile hat alle Pflicht-Spalten gefüllt
8. `statistiken.akteure_total` = `len(akteure)`
9. `statistiken.akteure_indexiert_sistrix` + `statistiken.akteure_nicht_indexiert_sistrix` = `akteure_total`
10. Jede `auffaelligkeit` hat `typ`, `titel`, `relevanz`, `quelle`, `handlungs_empfehlung`
11. `quelle: ahrefs` oder `quelle: beide` darf nur im Hybrid-Modus vorkommen
12. Im Reduced-Modus: `quelle.ahrefs` im Frontmatter ist `null`, alle Ahrefs-spezifischen Auffälligkeits-Typen sind nicht vorhanden

Wenn eine Regel verletzt wird: konkrete Fehlermeldung im Skill-Schluss-Format, welcher Eintrag korrigiert werden muss.
