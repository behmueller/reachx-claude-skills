# Phase-B-Output-Schema

Format-Definition der Output-Dateien, die Phase B des `03-20-local-gmb-wettbewerb`-Skills erzeugt.

## 1. `audits/local-gmb-wettbewerb.md` — Aggregat

### Frontmatter

```yaml
---
skill: 03-20-local-gmb-wettbewerb
phase: B
status: abgeschlossen
generiert_am: 2026-05-17T11:30:00Z
schema_version: 1.0
plattform: gmb            # alle Review-Zahlen sind GMB-only, keine Multi-Plattform-Summe

basis_inputs:
  - datei: audits/local-gmb-wettbewerb-schema.md
    generiert_am: 2026-05-17T10:00:00Z
  - datei: wettbewerber/liste.md
    generiert_am: 2026-05-16T09:00:00Z
  - datei: audits/local-gmb-schema.md
    generiert_am: 2026-05-15T14:00:00Z   # nur bei variante: aufsatz

akteure_gesamt: 6
akteure_kunde: 1
akteure_wettbewerber: 5
standorte_gesamt: 6
local_pack_queries_durchgefuehrt: 12

lvs_gewichtung:
  block_a_local_pack: 45
  block_b_review_substanz: 30
  block_c_profil_reife: 25
lvs_quelle: schaetzung_skill    # der LVS ist abgeleitet; Eingangsgrößen sind erhoben

lvs_ranking:
  - rang: 1
    akteur_slug: alpha-zahnarzt
    lvs: 78.4
    block_a: 82.0
    block_b: 75.1
    block_c: 76.0
  - rang: 2
    akteur_slug: beta-praxis
    lvs: 61.2
    block_a: 58.0
    block_b: 64.0
    block_c: 64.5
  - rang: 4
    akteur_slug: beispiel-zahnarzt     # Kunde
    ist_kunde: true
    lvs: 44.7
    block_a: 38.0
    block_b: 49.0
    block_c: 50.5

statistik_kunde:
  lvs: 44.7
  rang: 4
  von_n: 6
  reviews_gesamt: 127
  velocity_1m: 2
  velocity_3m: 6
  velocity_6m: 9
  velocity_12m: 18
  velocity_trend: stabil
  top_3_quote_prozent: 25
  top_10_quote_prozent: 67
  antwort_quote_prozent: 22
  profil_reife_score: 50.5

statistik_pool:
  lvs_median: 53.0
  lvs_max: 78.4
  reviews_gesamt_max: 320
  velocity_3m_max: 22

auffaelligkeiten:
  - typ: kunde_lvs_unter_median
    severity: hoch
    text: "LVS Kunde 44,7 — Pool-Median 53,0. Kunde auf Rang 4 von 6."
  - typ: wettbewerber_review_momentum
    severity: hoch
    wettbewerber_slug: alpha-zahnarzt
    text: "alpha-zahnarzt 22 neue Reviews in 3 Monaten, Kunde nur 6 — 3,7-facher Wert."
  - typ: review_substanzverlust
    severity: mittel
    wettbewerber_slug: gamma-zahnaerzte
    text: "gamma-zahnaerzte 210 Reviews gesamt, aber 0 in den letzten 6 Monaten."
  - typ: latente_bedrohung_local
    severity: mittel
    wettbewerber_slug: delta-praxis
    text: "delta-praxis LVS nur 31, aber velocity_3m verdreifacht — würde stark, sobald GMB-Profil nachgezogen wird."

reduced_modi: []          # z.B. velocity_nicht_erhebbar, local_pack_web_search
lvs_konfidenz: hoch       # hoch | niedrig (niedrig bei aktiven Reduced-Modi)
---
```

### Body-Struktur

```markdown
# Local-GMB-Wettbewerbsvergleich · KUNDE

## Übersicht

[Akteur-Anzahl, Standorte, Local-Pack-Queries, Schema-Variante (aufsatz/eigenständig),
aktive Reduced-Modi falls vorhanden, LVS-Konfidenz]

## LVS-Ranking

[Tabelle: alle Akteure nach LVS absteigend — Spalten: Rang, Akteur, Typ (Kunde/regional),
LVS, Block A, Block B, Block C. Median-Zeile am Fuß. Kunden-Zeile hervorgehoben.]

## Review-Velocity

[Tabelle: pro Akteur velocity_1m / 3m / 6m / 12m, Velocity-Trend, reviews_gesamt.
Zeigt, wer aktiv aufbaut und wer Substanz verliert.]

## GMB-Profil-Reife

[Tabelle: pro Akteur die Teil-Kriterien — Kategorien, Attribute, Fotos, Posts/Monat,
Antwort-Quote, Vollständigkeit — plus C_score.]

## Pro Akteur

### Kunde · KUNDENNAME — LVS 44,7 (Rang 4 von 6)

**LVS-Aufschlüsselung**: Block A 38,0 · Block B 49,0 · Block C 50,5
(Gewichtung 45/30/25 → LVS 44,7)

**Review-Velocity**: 1M: 2 · 3M: 6 · 6M: 9 · 12M: 18 — Trend: stabil
**GMB-Profil-Reife**: 1 Hauptkategorie, 0 Sub · 6 Attribute · 12 Fotos ·
0,3 Posts/Monat · 22 % Antwort-Quote · Vollständigkeit 75 %
**Local-Pack**: Top-3 in 25 %, Top-10 in 67 % der 12 Queries

**Auffälligkeiten Kunde**: kunde_lvs_unter_median (hoch), kunde_antwort_quote_schwach (mittel)

### Wettbewerber · ALPHA-ZAHNARZT — LVS 78,4 (Rang 1)

[gleiche Sub-Struktur, komprimiert — Fokus auf Vergleich zum Kunden]

## Pool-weite Auffälligkeiten

[Liste nach Severity sortiert, mit Handlungs-Empfehlung pro Auffälligkeit]

## Vorbereitung für Folge-Skills

Hinweis für `04-02-kanal-chancen-analyse`: Local-SEO ist [stark|mittel|schwach] als Kanal.
Begründung aus dem LVS-Abstand Kunde-zu-Pool-Median und der schwächsten Block-Achse.
Der LVS-Wert des Kunden ist der konkrete Local-SEO-Datenpunkt für die Kanal-Bewertung.
```

## 2. `audits/local-gmb-wettbewerb.csv` — eine Zeile pro Akteur

Bei Multi-Standort: eine Zeile pro Akteur × Standort plus eine Akteur-Aggregat-Zeile (`standort_id: _aggregat`).

Spalten:

```csv
akteur_slug,akteur_name,ist_kunde,kategorie,standort_id,standort_stadt,
lvs,lvs_rang,block_a_score,block_b_score,block_c_score,
top_3_quote_prozent,top_10_quote_prozent,
reviews_gesamt,avg_rating,velocity_1m,velocity_3m,velocity_6m,velocity_12m,
velocity_trend,velocity_12m_mind,
kategorien_anzahl,sub_kategorien_anzahl,attribute_anzahl,foto_anzahl,
posts_pro_monat,antwort_quote_prozent,profil_vollstaendigkeit_prozent,
plattform,quelle,lvs_konfidenz,scrape_datum
```

Validierung:

- `lvs`, `block_*_score`: float 0–100, eine Nachkommastelle.
- `ist_kunde`: `true | false`.
- `kategorie`: `kunde | regional | auto_ergaenzt`.
- `velocity_*`: integer ≥ 0, monoton (`1m ≤ 3m ≤ 6m ≤ 12m`).
- `velocity_trend`: `beschleunigung | stabil | verlangsamung | inaktiv`.
- `velocity_12m_mind`: `true | false` — true wenn Sample keine 12 Monate abdeckt.
- `plattform`: immer `gmb`.
- `quelle`: `apify_maps | apify_extractor | web_search`.
- `lvs_konfidenz`: `hoch | niedrig`.

Sortierung: nach `lvs` absteigend, Aggregat-Zeilen vor Standort-Zeilen je Akteur.

## 3. Roh-Caches

### `assets/raw/gmb-wettbewerb-<slug>.json`

Pro Akteur (bei Filialen `-<standort>` suffigiert) — siehe `apify-actors.md` Abschnitt 4 für das Format.

### `audits/local-gmb-wettbewerb-rankings.csv`

Roh-Rankings pro Local-Pack-Query. Spalten:

```csv
standort_id,standort_stadt,keyword_basis,keyword_modifier,keyword_full,
position,akteur_slug,akteur_name,akteur_rating,akteur_reviews,
quelle,scrape_datum,pack_eingeblendet
```

- `position`: integer 1–10 oder leer (CSV: leeres Feld, nicht der String `null`) wenn nicht in Top-10.
- `pack_eingeblendet`: `true | false` — false-Queries zählen nicht in den Block-A-Nenner.
- `akteur_slug`: matched gegen Akteur-Set, sonst `unbekannt-<index>` (löst `local_wb_nicht_in_liste` aus).

## 4. HTML-Report `reports/14b-local-gmb-wettbewerb.html`

**Report-Nummer:** `14b` — sortiert direkt hinter `14-gmb-local-seo.html`. Vor dem Render gegen `reports/index.html` auf Drive prüfen; bei Kollision nächste freie Nummer im 14er-Block (`14c`, …) und im Schluss-Format/`status.md` die tatsächliche Nummer nennen.

Aus `reports/_shell.html` kopiert, acht Platzhalter ersetzt. `{{MAIN_CONTENT}}` ausschließlich aus den Bausteinen in `01-01-mta-projekt-init/reference/report-bausteine.md`. Vor Upload mit `scripts/validate-report.py --shell` validieren.

Platzhalter:

- `{{TITLE}}` — `Local-GMB-Wettbewerb · KUNDE`
- `{{EYEBROW}}` — `MTA-Audit · Local-SEO`
- `{{DISPLAY_NAME}}` — `Local-GMB-Wettbewerbsvergleich: KUNDE`
- `{{META_LINE}}` — `N Akteure · S Standorte · Q Local-Pack-Queries · Generiert: DATUM`
- `{{TOKEN_FOOTER}}` — Skill-Counter via `token-tracker.py render-skill-counter`
- `{{FOOTER_TEXT}}` — `MTA · KUNDE · Local-GMB-Wettbewerb`
- `{{TOKEN_BREAKDOWN}}` — leer (nur Dashboard)

### `{{MAIN_CONTENT}}`-Aufbau — Baustein-Zuordnung

Alle Bausteine 1:1 aus `report-bausteine.md`:

1. **Sticky-TOC** (`nav.toc`) — Anker: `#lvs-ranking`, `#velocity`, `#profil-reife`, `#akteure`, `#auffaelligkeiten`.
2. **Stat-Strip** (`div.stat-strip`) — fünf Stats: LVS Kunde, Rang Kunde von N, Top-3-Quote Kunde, Review-Velocity Kunde (3M), Anzahl Auffälligkeiten.
3. **Summary-Card** (`div.summary-card`) — Kernbefund: LVS-Position des Kunden, stärkster Akteur, Kern-Lücke. `.note` mit Datenstand und `lvs_konfidenz`.
4. **Sektion „LVS-Ranking"** (`section` + `section-heading`) — `table.data` aller Akteure nach LVS absteigend, Spalten Rang/Akteur/Typ/LVS/Block A/B/C, `tr.total` mit Pool-Median. Akteur-Typ als `badge` (`vorhanden` Kunde, `neutral` Wettbewerber).
5. **Sektion „Review-Velocity"** — `table.data` mit den vier Bucket-Werten plus Trend (Trend als `badge`: `stark` = beschleunigung, `mittel` = stabil, `schwach` = verlangsamung/inaktiv). Pro Akteur der Velocity-Verlauf als **Inline-SVG-Sparkline** (Baustein 12) — gleicher `min`/`max` über alle Sparklines des Reports, Punkte = inkrementelle Bucket-Werte über die Zeit.
6. **Sektion „GMB-Profil-Reife"** — `table.ratings` mit den Teil-Kriterien je Akteur, `C_score`-Spalte mit `badge` (stark/mittel/schwach).
7. **Sektion „Pro Akteur"** — **expandierbare Akteur-Zeilen**: ein `details.dim`-Block pro Akteur, `data-rating` aus dem LVS (≥ 66 `stark`, 33–65 `mittel`, < 33 `schwach`). Kunde und Top-2-Wettbewerber mit `open`, Rest zugeklappt. `summary` mit Akteur-Name (`<strong>`) und LVS als `badge`. `.body`: LVS-Aufschlüsselung (A/B/C × Gewicht), Velocity-Buckets, Profil-Reife-Detail, Local-Pack-Quoten.
8. **Sektion „Auffälligkeiten"** — ein `div.suggestion` pro Auffälligkeit, `.label` = Typ-Name, Text mit Handlungs-Empfehlung. Nach Severity sortiert.

Keine Local-Pack-Heatmap in diesem Report — die ist Sache von `03-16`. `03-20` fokussiert das LVS-Ranking und die Velocity-Sicht.

## 5. `status.md`-Update

Frontmatter:

- `03-20-local-gmb-wettbewerb` aus `schritte_offen` in `schritte_done`, aus `blockiert` entfernen.
- `naechster_empfohlen` auf nächsten sinnvollen Skill (typischerweise `04-02-kanal-chancen-analyse`, wenn genug Audits durch sind).

Body — Sektion unter „✓ Erledigt":

```markdown
### 03-20-local-gmb-wettbewerb
- Erledigt: 2026-05-17 11:30
- Output:
  - audits/local-gmb-wettbewerb-schema.md (status: bestaetigt)
  - audits/local-gmb-wettbewerb.md
  - audits/local-gmb-wettbewerb.csv
  - audits/local-gmb-wettbewerb-rankings.csv
  - assets/raw/gmb-wettbewerb-*.json
  - reports/14b-local-gmb-wettbewerb.html
- Hinweise: N Akteure, LVS Kunde X (Rang R von N). Top-Auffälligkeit: ...
```

Bei Skip:

```markdown
### 03-20-local-gmb-wettbewerb (geskippt)
- Erledigt: 2026-05-17 10:00
- Output: audits/local-gmb-wettbewerb-schema.md (status: skip_national_online)
- Hinweise: Kein Local-Bezug erkannt. Override mit "trotzdem laufen" möglich.
```

## 6. Dashboard-Update (`reports/index.html`)

- Stat-Strip um LVS Kunde ergänzen.
- „Erledigt"-Sektion: Eintrag mit Link auf `reports/14b-local-gmb-wettbewerb.html` (tatsächliche Nummer).
- Bei Skip: Eintrag mit Hinweis „(geskippt — kein Local-Bezug)".
- `<body class="is-dashboard">` sicherstellen.
