# Pinterest-Output-Schema

Vollständiges Schema für die Output-Dateien des `03-10-social-pinterest`-Skills:

- `audits/pinterest-wettbewerb.md` - Aggregat (Markdown mit YAML-Frontmatter)
- `audits/pinterest-profile.csv` - Profil-Matrix (CSV)
- `audits/pinterest-pins.csv` - Pin-Sample (CSV)
- `assets/raw/pinterest-profile-AKTEURSSLUG.json.gz` (Drive) - Roh-Cache, lokal `~/.cache/reachx-mta/<slug>/raw/pinterest-profile-AKTEURSSLUG.json`
- `assets/raw/pinterest-pins-AKTEURSSLUG.json.gz` (Drive) - Roh-Cache, lokal `~/.cache/reachx-mta/<slug>/raw/pinterest-pins-AKTEURSSLUG.json`

## 1. `audits/pinterest-wettbewerb.md`

### Frontmatter

```yaml
---
# === Skill-Metadaten ===
skill: 03-10-social-pinterest
generiert_am: 2026-05-13T11:00:00Z
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  meta_json: meta.json
  liste_md: wettbewerber/liste.md
  liste_bestaetigt_am: 2026-05-08T14:00:00Z
  kunde_md_vorhanden: true
modus: voll                  # voll | kunden_only
apify_actor_primaer: apify/pinterest-scraper
apify_actor_fallback: apify/puppeteer-scraper
datenstand: 2026-05-13

# === Branchen-Fit-Bewertung ===
branchen_fit_pinterest: niedrig          # hoch | mittel | niedrig
pinterest_branchen_relevant: false       # bool - true wenn mind. 1 Akteur aktiv
branchen_fit_begruendung: "B2B-Industrie, Maschinenbau - Pinterest erfahrungsgemäß keine zentrale Plattform"

# === Akteurs-Matrix ===
akteure:
  - akteurs_slug: musterkunde-gmbh
    akteurs_typ: kunde
    akteurs_name: Musterkunde GmbH
    pinterest_username: musterkundegmbh
    pinterest_url: https://www.pinterest.com/musterkundegmbh/
    match_methode: touchpoint            # touchpoint | briefing | apify_search | nicht_gefunden
    match_konfidenz: hoch                # hoch | mittel | niedrig | nicht_gefunden
    follower_count: 1240
    following_count: 18
    boards_count: 12
    pins_count_gesamt: 348
    verifiziert: false
    business_account: true
    account_typ: business
    pins_im_zeitfenster_12m: 28
    pins_pro_woche_median: 0.5
    wochen_seit_letztem_pin: 3
    aktivitaets_status: gering_aktiv     # aktiv | gering_aktiv | inaktiv | kein_profil
    pin_typen_verteilung:
      standard: 0.71
      video: 0.18
      idea: 0.07
      product: 0.04
      unbekannt: 0.0
    engagement_pro_pin_median: 7.5
    engagement_rate_proxy: 0.6           # Engagement / Follower * 100
    top_boards:
      - name: Inspiration
        pin_anzahl: 87
        follower_anzahl: 412
      - name: Anwendungsbeispiele
        pin_anzahl: 54
        follower_anzahl: 198
    content_pillars:
      - Inspiration
      - Anwendungsbeispiele
      - Saison-Highlights
    scrape_unvollstaendig: false
    idea_pins_erfassbar: true
    engagement_proxy_unzuverlaessig: false
  # ... weitere Akteure analog

# === Branchen-Aggregat ===
branchen_aggregat:
  akteure_mit_profil: 4
  akteure_total: 7
  aktive_akteure: 2
  pins_volumen_12m_branchenweit: 167
  follower_summe: 12400
  follower_top_akteur:
    akteur: best-practice-akteur
    follower: 8400
  engagement_pro_pin_median_branche: 9.2
  pin_typen_branchenweit:
    standard: 0.68
    video: 0.20
    idea: 0.08
    product: 0.04
    unbekannt: 0.0
  content_pillars_branchenweit:
    - pillar: Saisonale Inspirationen
      akteure_count: 3
      pin_anteil: 0.22
    - pillar: DIY-Anleitungen
      akteure_count: 2
      pin_anteil: 0.14

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: kunde_engagement_unter_branchen_median
    titel: "Kunden-Engagement 35% unter Branchen-Median"
    beschreibung: "Engagement-pro-Pin des Kunden liegt bei 7.5, Branchen-Median bei 11.5 - Pin-Qualität oder Tags-Optimierung prüfen"
    relevanz: mittel                     # hoch | mittel | niedrig
    handlungs_empfehlung: "Pin-Titel und -Beschreibungen mit Suchbegriffen anreichern, Cover-Bilder neu testen"
    betroffene_akteure:
      - musterkunde-gmbh
  - typ: wettbewerber_idea_pins_strategie
    titel: "Zwei Wettbewerber setzen stark auf Idea-Pins"
    beschreibung: "best-practice-akteur und wettbewerber-zwei haben Idea-Pin-Anteil >25%, Kunde nutzt Idea-Pins selten"
    relevanz: mittel
    handlungs_empfehlung: "Idea-Pin-Format testen - Pinterest pusht Story-Format aktuell organisch"
    betroffene_akteure:
      - best-practice-akteur
      - wettbewerber-zwei

# === Coverage-Hinweise ===
coverage:
  akteure_ohne_pinterest_username: 3
  akteure_mit_scrape_problem: 0
  manueller_check_erforderlich: false
---
```

### Body-Struktur

```markdown
# Pinterest-Wettbewerbsanalyse: KUNDENNAME

> ℹ **Branchen-Fit-Hinweis** (bei niedrig: prominenter als Banner)
> Pinterest-Branchen-Fit gering - strategisches Nicht-Thema empfohlen.
> [Begründung aus Frontmatter]

## Übersicht

- Akteure mit Pinterest-Profil: 4 von 7
- Aktive Accounts: 2
- Top-Account: best-practice-akteur mit 8.400 Followern
- Pin-Volumen 12M branchenweit: 167 Pins
- Engagement-Median pro Pin: 9.2

## Akteurs-Vergleichs-Tabelle

| Akteur | Typ | Follower | Boards | Pins 12M | Engagement | Status |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## Pro Akteur

### Musterkunde GmbH (Kunde)

**Profil-Snapshot:** 1.240 Follower, 12 Boards, 348 Pins gesamt, Business-Account, nicht verifiziert.

**Bio:** ...

**Top-Boards:**

| Board | Pins | Follower |
|---|---|---|
| Inspiration | 87 | 412 |
| Anwendungsbeispiele | 54 | 198 |
| ... | ... | ... |

**Pin-Typen-Verteilung:** Standard 71%, Video 18%, Idea 7%, Product 4%

**Top-Pins nach Saves:**

1. "Pin-Titel" (Board: Inspiration) - 124 Saves, 3 Comments
2. ...

**Content-Pillars:** Inspiration, Anwendungsbeispiele, Saison-Highlights

### (weitere Akteure analog)

## Branchen-Content-Pillars

| Pillar | Akteure | Pin-Anteil |
|---|---|---|
| Saisonale Inspirationen | 3 | 22% |
| DIY-Anleitungen | 2 | 14% |

## Auffälligkeiten

### Kunden-Engagement 35% unter Branchen-Median (mittel)

[Beschreibung, Handlungs-Empfehlung, betroffene Akteure]

### (weitere Auffälligkeiten)
```

## 2. `audits/pinterest-profile.csv`

Eine Zeile pro Akteur. Trennzeichen: Komma. Strings mit Anführungszeichen falls sie Komma enthalten.

### Spalten

```
akteurs_slug
akteurs_typ                          # kunde | wettbewerber
akteurs_name
pinterest_username
pinterest_url
match_methode                        # touchpoint | briefing | apify_search | nicht_gefunden
match_konfidenz                      # hoch | mittel | niedrig | nicht_gefunden
follower_count
following_count
boards_count
pins_count_gesamt
verifiziert                          # 1 | 0
business_account                     # 1 | 0
account_typ                          # personal | business | unbekannt
pins_im_zeitfenster_12m
pins_pro_woche_median
wochen_seit_letztem_pin
aktivitaets_status                   # aktiv | gering_aktiv | inaktiv | kein_profil
engagement_pro_pin_median
engagement_rate_proxy
top_boards                           # Pipe-getrennt: "name:pin_anzahl:follower_anzahl|name2:...", max 10
content_pillars                      # Pipe-getrennt, max 5
scrape_unvollstaendig                # 1 | 0
idea_pins_erfassbar                  # 1 | 0
engagement_proxy_unzuverlaessig      # 1 | 0
datenstand_iso
```

### Validierungs-Regeln

- `akteurs_slug` ist nicht leer
- `akteurs_typ` ist `kunde` oder `wettbewerber`
- Counts sind int oder leer (bei `nicht_gefunden`)
- `pins_pro_woche_median` und `engagement_pro_pin_median` sind float auf 2 Nachkommastellen
- Wenn `match_methode == nicht_gefunden`: alle profilbezogenen Counts leer
- Aktivitäts-Buckets:
  - `aktiv`: `pins_pro_woche_median >= 1.0` und `wochen_seit_letztem_pin < 4`
  - `gering_aktiv`: `0.2 <= pins_pro_woche_median < 1.0` und `wochen_seit_letztem_pin < 8`
  - `inaktiv`: alles andere mit Profil
  - `kein_profil`: kein auflösbarer Username

## 3. `audits/pinterest-pins.csv`

Eine Zeile pro Pin × Akteur. Trennzeichen: Komma. Mehrzeilige Texte (Beschreibung) sauber in Anführungszeichen mit Escapes.

### Spalten

```
akteurs_slug
akteurs_typ
akteurs_name
pin_id
pin_url
pin_title
pin_beschreibung
pin_typ                              # standard | video | idea | product | unbekannt
created_at                           # ISO-8601
saves_count                          # int oder leer
comments_count                       # int oder leer
domain_link                          # Quelldomain oder leer
landingpage_url
board_slug
board_name
tags                                 # Komma-getrennt, in Anführungszeichen wegen Mehrwert-Kommas
creative_url
datenstand_iso
```

### Validierungs-Regeln

- `pin_id` ist nicht leer
- `created_at` ist ISO-8601 und liegt im Fenster `datenstand_iso - 12 Monate` bis `datenstand_iso`
- `pin_typ` ist genau einer der erlaubten Werte
- `saves_count` und `comments_count` sind int oder leer
- Hard-Cap: Maximal 40 Pins pro `akteurs_slug` in der gesamten Datei
- Sortierung: pro Akteur chronologisch absteigend (jüngste zuerst), Akteure alphabetisch nach `akteurs_slug` mit Kunde zuerst

## 4. Roh-Daten-Caches

### `assets/raw/pinterest-profile-AKTEURSSLUG.json.gz` (Drive) — lokal `~/.cache/reachx-mta/<slug>/raw/pinterest-profile-AKTEURSSLUG.json`

Direkte Apify-Actor-Antwort für das Profil + Boards. JSON. Wird unverändert lokal abgelegt, am Skill-Ende gzip-komprimiert nach Drive hochgeladen. Dient als Audit-Trail bei späteren Diskussionen ("Wo kam die Zahl her?").

### `assets/raw/pinterest-pins-AKTEURSSLUG.json.gz` (Drive) — lokal `~/.cache/reachx-mta/<slug>/raw/pinterest-pins-AKTEURSSLUG.json`

Direkte Apify-Actor-Antwort für die Pin-Liste. JSON.

## 5. Pflicht-Konsistenz zwischen den Dateien

- Jeder Akteur in `pinterest-profile.csv` ist auch in der `akteure`-Sektion des Frontmatters von `pinterest-wettbewerb.md` aufgeführt - identische Slugs und Counts
- `pins_im_zeitfenster_12m` in der Profil-CSV entspricht der Anzahl Zeilen in `pinterest-pins.csv` für den gleichen Akteur (mit Hard-Cap 40)
- `top_boards` in der Profil-CSV entspricht den Top-Boards aus dem Frontmatter
- `content_pillars` in der Profil-CSV entspricht den Pillars aus dem Frontmatter

Wenn ein Akteur als `nicht_gefunden` markiert ist:

- Profil-CSV-Zeile vorhanden mit `akteurs_slug`, `akteurs_typ`, `akteurs_name`, `match_methode: nicht_gefunden`, alle anderen Felder leer
- Pin-CSV: keine Zeile
- Frontmatter `akteure`: vorhanden mit den genannten Feldern und `aktivitaets_status: kein_profil`
