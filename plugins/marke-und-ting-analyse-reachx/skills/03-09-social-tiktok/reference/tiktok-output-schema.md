# TikTok-Output-Schema

Format der Output-Dateien von `03-09-social-tiktok`. Die Aggregat-Datei `audits/tiktok-wettbewerb.md` ist Input für die Synthese-Skills `04-02-kanal-chancen-analyse` und `04-01-positionierungs-analyse`. Die CSVs sind Daten-Backbone für tiefer-gehende Analysen.

## 1. `audits/tiktok-wettbewerb.md` — Voller Lauf

### Frontmatter-Schema

```yaml
---
# === Skill-Metadaten ===
skill: 03-09-social-tiktok
generiert_am: <ISO-8601>
schema_version: "1.0"
lauf_typ: voll                       # voll | skip
branchen_fit: <hoch | mittel | gering>

# === Recherche-Provenienz ===
basiert_auf:
  liste: wettbewerber/liste.md
  liste_bestaetigt_am: <ISO-8601>
  kunde_md_vorhanden: <true | false>
  marken_profile_vorhanden: <true | false>

erhebung:
  zeitraum_video_sample_monate: <int>  # 6 oder 12
  hard_cap_videos_pro_akteur: 30
  apify_actor_primaer: <Actor-Name>
  apify_actor_fallback: <Actor-Name oder null>
  durchgefuehrt_am: <ISO-8601>

# === Akteurs-Liste ===
akteure:
  - akteurs_slug: <kebab-case>
    name: <Anzeigename>
    typ: <kunde | wettbewerber>
    kategorie_wenn_wettbewerber: <kunde_genannt | regional | best_practice_ueberregional | null>
    profil_status: <gefunden | nicht_gefunden | profil_privat | profil_geloescht | kein_eindeutiger_match>
    tiktok_username: <username ohne @ oder null>
    profil_url: <URL oder null>
    match_quelle: <touchpoint | website | search | web_search | nicht_gefunden>
    match_konfidenz: <hoch | mittel | niedrig | null>

# === Profil-Snapshots ===
profile:
  - akteurs_slug: <slug>
    follower_count: <int oder null>
    following_count: <int oder null>
    likes_gesamt: <int oder null>
    videos_gesamt: <int oder null>
    verifiziert: <bool oder null>
    bio_text: <string oder null>
    externer_link: <URL oder null>

# === Video-Sample-Aggregate pro Akteur ===
video_aggregate:
  - akteurs_slug: <slug>
    videos_im_sample: <int>
    zeitraum_von: <ISO-8601-Datum>
    zeitraum_bis: <ISO-8601-Datum>
    posting_frequenz_pro_woche: <float>
    aktivitaet_status: <aktiv | inaktiv_seit_X_wochen>
    inaktiv_seit_wochen: <int oder null>
    views_median: <int>
    engagement_rate_median: <float>           # z.B. 0.057
    engagement_rate_min: <float>
    engagement_rate_max: <float>
    trend_sound_nutzung_prozent: <float>      # Anteil Videos mit nicht-eigenem Sound
    duet_stitch_anteil_prozent: <float>
    top_3_videos:
      - video_id: <string>
        video_url: <URL>
        views: <int>
        engagement_rate: <float>
        caption_kurz: <string, gekürzt auf 120 Zeichen>
    top_hashtags:
      - tag: <string ohne #>
        haeufigkeit: <int>
    top_music_tracks:
      - titel: <string>
        kuenstler: <string oder null>
        ist_original_sound: <bool>
        haeufigkeit: <int>
    content_pillars_heuristik:
      - pillar_name: <string>
        anteil_prozent: <float>
        beleg_beispiele: [<video_id>, <video_id>]

# === Branchen-Aggregate ===
branchen_aggregate:
  median_engagement_rate: <float>
  akteure_mit_profil: <int>
  akteure_ohne_profil: <int>
  branchen_relevante_hashtags:        # Hashtags, die bei >=2 Akteuren im Top-10 sind
    - tag: <string>
      anzahl_akteure: <int>
  branchen_relevante_sounds:          # Music-Tracks bei >=2 Akteuren
    - titel: <string>
      kuenstler: <string oder null>
      anzahl_akteure: <int>
  branchen_relevante_challenges:      # Hashtags mit Challenge-Form bei >=2 Akteuren
    - tag: <string>
      anzahl_akteure: <int>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <kunde_kein_tiktok_profil | kunde_inaktiv_seit_X_wochen | kunde_engagement_unter_branchen_median | wettbewerber_viraler_hit | trend_sound_nutzung_diskrepanz | hashtag_challenge_teilnahme | content_pillar_luecke_kunde>
    schwere: <hoch | mittel | niedrig>
    betroffene_akteure: [<slug>, <slug>]
    daten_beleg: <string mit konkreten Zahlen>
    handlungsvorschlag: <string in einem Satz>

# === Lücken ===
luecken:
  - akteurs_slug: <slug>
    grund: <kein_eindeutiger_match | apify_fehler | profil_privat | profil_geloescht | sonstiges>
    detail: <Freitext>
---
```

### Body-Struktur

```markdown
# TikTok-Wettbewerbsanalyse: <Kundenname>

## Übersicht

- Akteure gesamt: N (1 Kunde + N-1 Wettbewerber)
- Akteure mit TikTok-Profil: P
- Akteure ohne TikTok-Profil: Q
- Video-Sample gesamt: V (über alle Akteure)
- Erhebungs-Zeitraum: VON bis BIS
- Branchen-Fit: hoch | mittel | gering
- Branchen-Median-Engagement-Rate: X %

[Branchen-Fit-Hinweis-Block, wenn `gering` oder `mittel`]

## Profil-Matrix

Tabelle: Akteure (Zeilen) × Follower, Likes-Gesamt, Videos im Sample, Posting-Frequenz/Woche, ER-Median (Spalten).

## Akteurs-Sektionen

### <Kundenname> (kunde)
- Profil-Daten
- Video-Sample-Aggregat
- TikTok-Spezifika (Trend-Sound-Anteil, Duet/Stitch, Hashtag-Challenges)
- Top-3-Videos (mit URL)
- Content-Pillars-Heuristik

### <Wettbewerber 1> (wettbewerber)
[gleiche Struktur]

## Branchen-Aggregate

- Branchen-Median-Engagement-Rate
- Branchen-relevante Hashtags
- Branchen-relevante Sounds
- Branchen-relevante Challenges

## Auffälligkeiten

Eine Sektion pro Auffälligkeit mit:
- Typ und Schwere
- Betroffene Akteure
- Daten-Beleg
- Handlungs-Empfehlung

## Lücken

- Akteure ohne Match
- Scrape-Fehler
- Hinweise für manuelle Strategen-Recherche
```

## 2. `audits/tiktok-wettbewerb.md` — Skip-Variante

Wenn `lauf_typ: skip`, ist das Frontmatter reduziert:

```yaml
---
skill: 03-09-social-tiktok
generiert_am: <ISO-8601>
schema_version: "1.0"
lauf_typ: skip
branchen_fit: gering

basiert_auf:
  liste: wettbewerber/liste.md
  liste_bestaetigt_am: <ISO-8601>

akteure_geprueft: <int>
akteure_mit_profil: 0
skip_grund: kein_akteur_mit_tiktok_profil_gefunden

geprüfte_akteure:
  - akteurs_slug: <slug>
    name: <name>
    typ: <kunde | wettbewerber>
    profil_status: <nicht_gefunden | kein_eindeutiger_match>
    match_versuche: [touchpoint, website, search]
---
```

### Body Skip-Variante

```markdown
# TikTok-Wettbewerbsanalyse: <Kundenname> (Skip)

## Ergebnis

TikTok-Branchen-Fit gering. Es konnte für keinen der N geprüften Akteure (Kunde + N-1 Wettbewerber) ein erkennbares TikTok-Profil ermittelt werden.

**Strategische Einordnung:** TikTok ist für diese MTA ein strategisches Nicht-Thema. Kein voller Audit-Lauf durchgeführt.

## Geprüfte Akteure

Tabelle: Akteur, Profil-Status, geprüfte Quellen.

## Hinweis für den Strategen

Wenn der Stratege TikTok-Präsenz manuell verifizieren will: TikTok-App oder tiktok.com mit Markennamen prüfen. Bei Fund: Username in der Touchpoint-Inventur (`data/kunde.md` oder `wettbewerber/profile/<slug>.md`) ergänzen und Skill erneut laufen lassen.
```

## 3. `audits/tiktok-profile.csv`

Eine Zeile pro Akteur (auch ohne Profil — dann meiste Felder leer).

Spalten in dieser Reihenfolge:

| Spalte | Typ | Beschreibung |
|---|---|---|
| akteurs_slug | string | Kebab-case-Slug des Akteurs |
| akteurs_name | string | Anzeigename |
| typ | enum | kunde, wettbewerber |
| tiktok_username | string oder leer | ohne @ |
| profil_url | URL oder leer | vollständige TikTok-URL |
| profil_status | enum | gefunden, nicht_gefunden, profil_privat, profil_geloescht, kein_eindeutiger_match |
| follower_count | int oder leer | |
| following_count | int oder leer | |
| likes_gesamt | int oder leer | |
| videos_gesamt | int oder leer | |
| verifiziert | bool oder leer | |
| bio_text | string oder leer | CR/LF mit Leerzeichen ersetzen, CSV-escapen |
| externer_link | URL oder leer | |
| erhebungs_datum | ISO-8601 oder leer | |

## 4. `audits/tiktok-videos.csv`

Eine Zeile pro Video im Sample. Keine Zeilen für Akteure ohne Profil.

Spalten:

| Spalte | Typ | Beschreibung |
|---|---|---|
| akteurs_slug | string | |
| video_id | string | TikTok-Video-ID |
| video_url | URL | |
| posting_datum | ISO-8601 | |
| laenge_sekunden | int | |
| views | int | |
| likes | int | |
| comments | int | |
| shares | int | |
| saves | int oder leer | optional, je nach Actor |
| engagement_rate | float oder leer | (likes+comments+shares)/views, vier Nachkommastellen |
| caption | string | volltext, CSV-escapen |
| hashtags_csv | string | semikolon-separiert ohne # |
| music_titel | string oder leer | |
| music_kuenstler | string oder leer | |
| ist_original_sound | bool oder leer | |
| ist_duet | bool | |
| ist_stitch | bool | |

## 5. Roh-Cache `assets/raw/tiktok-profile-<slug>.json.gz` und `assets/raw/tiktok-videos-<slug>.json.gz` (Drive)

Direktes JSON aus dem Apify-Actor, **unverändert**. Diese Dateien sind Cache und Beleg-Quelle, damit Folge-Skills oder manuelle Nachprüfung den ursprünglichen Datenstand sehen. Lokal werden sie unter `~/.cache/reachx-mta/<slug>/raw/` zwischengespeichert, am Skill-Ende gzip-komprimiert nach Drive `assets/raw/` hochgeladen.

## 6. HTML-Report `reports/16-tiktok-wettbewerb.html`

Basiert auf `reports/_shell.html`. Pflicht-Sektionen siehe SKILL.md Schritt 11.

Bei Skip-Variante: stark reduziert, nur Branchen-Fit-Hinweis und Akteurs-Tabelle mit Profil-Status.

## 7. Versions-Hinweis

`schema_version: "1.0"` ist initial. Bei Field-Mapping-Änderungen (z.B. neue Apify-Actor-Felder) Version hochzählen und alte Reader-Logik in Synthese-Skills kompatibel halten.
