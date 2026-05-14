# Phase-B-Output-Schema

Format-Definition der drei Output-Dateien plus Roh-Caches, die Phase B erzeugt.

## 1. `audits/local-gmb.md` — Aggregat pro Akteur

### Frontmatter

```yaml
---
skill: 03-16-local-gmb-und-seo
phase: B
status: abgeschlossen
generiert_am: 2026-05-13T11:30:00Z
schema_version: 1.0

basis:
  - audits/local-gmb-schema.md
  - wettbewerber/liste.md
  - data/kunde.md

akteure_gesamt: 6
akteure_kunde: 1
akteure_wettbewerber: 5
standorte_gesamt: 4

statistik_kunde:
  profil_vollstaendigkeit_prozent: 78
  rating: 4.3
  reviews_anzahl: 127
  antwort_quote_prozent: 22
  letzte_post_alter_tage: 145
  top_3_quote_local_pack_prozent: 35
  top_10_quote_local_pack_prozent: 70

statistik_pool_durchschnitt:
  profil_vollstaendigkeit_prozent: 65
  rating: 4.4
  reviews_anzahl: 89
  antwort_quote_prozent: 45

auffaelligkeiten:
  - typ: kunde_keine_review_antworten
    severity: hoch
    text: Kunde hat 22% Antwort-Quote, Pool-Median 45%, Top-WB hat 80%.
  - typ: wettbewerber_dominiert_local_pack
    severity: hoch
    wettbewerber_slug: alpha-zahnarzt
    quote_top_3_prozent: 75
    text: alpha-zahnarzt ist in 9 von 12 Local-Pack-Queries in Top-3, Kunde nur in 3 von 12.
  - typ: kunde_keine_gmb_posts_seit_90_tagen
    severity: mittel
    letzte_post_alter_tage: 145
    text: Kunde hat seit 145 Tagen keinen GMB-Post veröffentlicht.
  - typ: negativer_review_cluster
    severity: mittel
    thema: wartezeit
    anzahl_reviews: 8
    durchschnitt_sterne: 2.6
    text: 8 Reviews mit Schnitt 2.6 Sterne erwähnen 'Wartezeit' als Problem.
  - typ: nap_inkonsistenz
    severity: niedrig
    akteur_slug: muster-zahnarzt-mitte
    feld: telefon
    text: Telefonnummer in GMB weicht von Website-Impressum ab.

reduced_modi:
  - branchenportale_nicht_geprueft   # falls portale.md fehlt
---
```

### Body-Struktur

```markdown
# GMB- und Local-SEO-Audit · KUNDE

## Übersicht

[Stat-Block: Akteure, Standorte, Queries, Reduced-Modi falls aktiv]

## Pool-weite Auffälligkeiten

[Liste nach Severity sortiert, mit Handlungs-Empfehlung pro Auffälligkeit]

## Pro Akteur

### Kunde · KUNDENNAME

#### Standort: Hauptsitz (Adresse)

**GMB-Profil**:
- Vollständigkeit: 78% (Telefonnummer ja, Öffnungszeiten ja, Beschreibung 142 Zeichen, 12 Fotos)
- Rating: 4.3 (127 Reviews)
- Antwort-Quote: 22%
- Letzter Post: vor 145 Tagen
- Hauptkategorie: Zahnarzt (passt)
- Sub-Kategorien: 0 (Empfehlung: mindestens 3 ergänzen)

**Reviews-Sentiment** (Top-3-Themen):
- Beratung: 23 Reviews, Schnitt 4.6 (positiv)
- Wartezeit: 8 Reviews, Schnitt 2.6 (negativ — Cluster)
- Freundlichkeit: 18 Reviews, Schnitt 4.7 (positiv)

**Local-Pack-Sichtbarkeit**:
- Top-3-Quote: 25% (3 von 12 Keywords)
- Top-10-Quote: 67% (8 von 12)
- Beste Position: 2 für "zahnarzt mitte"
- Schlechteste Position: nicht gefunden für "zahnarzt prenzlauer berg"

**NAP-Konsistenz**:
- GMB-Telefon: 030-12345678
- Website-Telefon: 030-1234-5678 (gleiche Nummer, andere Formatierung — OK)
- Branchenportal-Telefon: 030-12345679 (abweichend — Auffälligkeit!)

**Auffälligkeiten Kunde-spezifisch**:
- ⚠ kunde_keine_review_antworten (severity: hoch)
- ⚠ kunde_keine_gmb_posts_seit_90_tagen (severity: mittel)
- ⚠ negativer_review_cluster (Wartezeit)
- ℹ nap_inkonsistenz (Telefon-Diff, mutmaßlich Tippfehler)

#### Standort: Filiale Charlottenburg (falls vorhanden)

[gleiches Schema]

### Wettbewerber · ALPHA-ZAHNARZT

[gleiche Sub-Struktur, aber komprimierter — Pro-WB-Block kann kürzer sein, Fokus auf Vergleich mit Kunde]

## Cross-Akteurs-Vergleich

### Local-Pack-Heatmap

|                            | Kunde | alpha-zahnarzt | beta-praxis | gamma-zahnaerzte |
|----------------------------|-------|----------------|-------------|------------------|
| zahnarzt berlin            | 5     | 1              | 3           | 7                |
| zahnarzt mitte             | 2     | 1              | 4           | -                |
| zahnarzt prenzlauer berg   | -     | 2              | 1           | 4                |
| zahnarzt in der nähe       | 8     | 1              | 2           | 5                |

(Tabelle ist Vorschau; vollständige Daten in `audits/local-rankings.csv`)

### Profil-Vergleich

| Akteur          | Vollständig. | Rating | Reviews | Antwort-Quote |
|-----------------|--------------|--------|---------|---------------|
| Kunde           | 78%          | 4.3    | 127     | 22%           |
| alpha-zahnarzt  | 92%          | 4.7    | 320     | 80%           |
| beta-praxis     | 65%          | 4.5    | 78      | 50%           |

## Vorbereitung für Folge-Skills

Hinweis für `04-02-kanal-chancen-analyse`: Local-SEO ist [stark|mittel|schwach] als Kanal, Begründung aus den Top-Auffälligkeiten.

Hinweis für `04-05-90-tage-plan`: konkrete Action-Items aus den Auffälligkeiten (z. B. "Antwort-Quote von 22% auf 60% in 90 Tagen", "GMB-Posts wieder aufnehmen, monatlich").
```

## 2. `audits/local-rankings.csv`

Spalten:

```
standort_id,standort_stadt,keyword_basis,keyword_modifier,keyword_full,position,akteur_slug,akteur_name,akteur_adresse,akteur_rating,akteur_reviews,quelle,scrape_datum,pack_eingeblendet
```

Pro Local-Pack-Query und gefundenem Akteur eine Zeile (also bei 12 Queries × Top-10 pro Query × N Akteure: bis zu 120 Zeilen pro Standort).

Validierung:

- `position`: integer 1-10 oder `null` (= nicht in Top-10 gefunden)
- `akteur_slug`: matched gegen Akteurs-Liste, sonst `unbekannt-<index>`
- `quelle`: `local_falcon | apify_pack_scraper | web_search_fallback`
- `pack_eingeblendet`: `true | false` — false wenn Google für diese Query kein Local Pack zeigt

Sortierung: nach `standort_id`, dann `keyword_full`, dann `position`.

## 3. `audits/gmb-reviews.csv`

Spalten:

```
akteur_slug,akteur_name,standort_id,review_id,datum,sterne,text,antwort_vorhanden,antwort_datum,themen_match
```

- Max 50 Reviews pro Akteur und Standort, nach Datum absteigend
- `themen_match`: Pipe-getrennte Liste der Themen aus `gmb_review_themen`, die im Review-Text erkannt wurden (z. B. `wartezeit|beratung`)
- `text`: trimmed auf max 500 Zeichen, längere Reviews abgeschnitten mit `...` (vollständig im Roh-Cache)
- `antwort_vorhanden`: `true | false`
- `antwort_datum`: nur gesetzt wenn `antwort_vorhanden: true`

Sortierung: nach `akteur_slug`, dann `datum` absteigend.

## 4. Roh-Caches

### `audits/raw/gmb-<slug>.json`

```json
{
  "akteur_slug": "muster-zahnarzt-mitte",
  "standort_id": "hauptsitz",
  "scrape_datum": "2026-05-13T11:00:00Z",
  "apify_actor": "compass/google-maps-scraper",
  "raw": { /* vollständiges Apify-Result */ }
}
```

### `audits/raw/local-rankings-<slug>.json`

Pro Standort eine Datei mit allen Pack-Query-Results für diesen Standort.

```json
{
  "standort_id": "hauptsitz",
  "stadt": "Berlin",
  "scrape_datum": "2026-05-13T11:15:00Z",
  "quelle": "apify_pack_scraper",
  "queries": [
    {
      "keyword_full": "zahnarzt mitte",
      "pack_eingeblendet": true,
      "results_top_10": [
        {"position": 1, "name": "alpha-zahnarzt", "adresse": "...", "rating": 4.7, "reviews": 320},
        ...
      ]
    },
    ...
  ]
}
```

## 5. `reports/14-gmb-local-seo.html`

Aus `reports/_shell.html` kopiert, Platzhalter ersetzt:

- `{{TITLE}}`: `Local-SEO-Audit · KUNDE`
- `{{EYEBROW}}`: `MTA-Audit`
- `{{DISPLAY_NAME}}`: `GMB- und Local-SEO-Audit: KUNDE`
- `{{META_LINE}}`: `N Akteure · S Standorte · Q Local-Pack-Queries · Generiert: DATUM`
- `{{MAIN_CONTENT}}`:
  1. Stat-Strip mit den fünf wichtigsten KPIs (Vollständigkeit Kunde, Rating Kunde, Top-3-Quote Kunde, Antwort-Quote Kunde, Anzahl Auffälligkeiten)
  2. `.summary-card` mit den drei wichtigsten Auffälligkeiten und Handlungs-Empfehlungen
  3. Sticky-TOC (`nav.toc`): Übersicht | Auffälligkeiten | Pro Akteur (mit Akteurs-Slugs) | Cross-Vergleich | Heatmap
  4. **Pool-weite Auffälligkeiten** als `.suggestion`-Block
  5. **Pro Akteur ein `<details class="skill" data-rating="stark|mittel|schwach">`-Block** mit Profil-Karte, Sentiment-Visualisierung, Local-Pack-Mini-Tabelle
  6. **Local-Pack-Heatmap** als HTML-Tabelle: Zeilen = Keywords, Spalten = Akteure, Zellen mit Hintergrundfarbe (Grün ≤ 3, Gelb 4-7, Orange 8-10, Rot nicht gefunden) und Position als Zahl
  7. **NAP-Diff-Tabelle** (nur bei Inkonsistenzen)
- `{{FOOTER_TEXT}}`: `MTA · KUNDE · Local-SEO-Audit Phase B`

## 6. status.md Update

Frontmatter:

- `03-16-local-gmb-und-seo` aus `schritte_offen` in `schritte_done`
- Aus `blockiert` entfernen
- `naechster_empfohlen` auf nächsten sinnvollen Skill (typischerweise `04-02-kanal-chancen-analyse` wenn genug Audits da sind)

Body:

```markdown
### 03-16-local-gmb-und-seo
- Erledigt: 2026-05-13 11:30
- Output:
  - audits/local-gmb-schema.md (status: bestaetigt)
  - audits/local-gmb.md
  - audits/local-rankings.csv
  - audits/gmb-reviews.csv
  - audits/raw/gmb-*.json
  - audits/raw/local-rankings-*.json
  - reports/14-gmb-local-seo.html
- Hinweise: N Akteure, S Standorte, A Auffälligkeiten. Top-Auffälligkeit: ...
```

Bei Skip:

```markdown
### 03-16-local-gmb-und-seo (geskippt)
- Erledigt: 2026-05-13 10:00
- Output: audits/local-gmb-schema.md (status: skip_national_online)
- Hinweise: Kein Local-Bezug erkannt. Override mit "trotzdem laufen" möglich.
```

## 7. Dashboard-Update

`reports/index.html`:

- Stat-Strip um Local-SEO-KPIs ergänzen (Top-3-Quote Kunde, GMB-Vollständigkeit Kunde)
- "Erledigt"-Sektion: Eintrag mit Link auf `reports/14-gmb-local-seo.html`
- Bei Skip: Eintrag in "Erledigt" mit Hinweis "(geskippt — kein Local-Bezug)"
