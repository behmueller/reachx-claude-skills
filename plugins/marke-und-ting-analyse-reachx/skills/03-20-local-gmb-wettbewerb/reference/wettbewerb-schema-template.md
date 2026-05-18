# Phase-A-Output-Template: `audits/local-gmb-wettbewerb-schema.md`

Dieses Template definiert das Format der Schema-Datei, die in Phase A des `03-20-local-gmb-wettbewerb`-Skills geschrieben wird. Das Schema steuert in Phase B den Wettbewerbsvergleich.

## Zwei Schema-Varianten

Welche Variante der Skill schreibt, hängt davon ab, ob `03-16-local-gmb-und-seo` bereits ein bestätigtes Schema hinterlassen hat (siehe SKILL.md Schritt 2):

- **Variante „Aufsatz"** — ein bestätigtes `audits/local-gmb-schema.md` existiert. Standorte, Suchradius und Local-Pack-Keywords werden **geerbt** und nur referenziert. Der Stratege prüft im Review **nur LVS-Gewichtung und Akteur-Set**.
- **Variante „eigenständig"** — kein `03-16`-Schema (oder nur `vorgeschlagen`). Das Schema ist vollständig: Standorte, Suchradius und Local-Pack-Keywords werden hier definiert und voll reviewed.

Beide Varianten nutzen dasselbe Datei-Format unten — bei „Aufsatz" sind die geerbten Felder mit `geerbt_aus: local-gmb-schema.md` markiert.

## Datei-Format

```markdown
---
skill: 03-20-local-gmb-wettbewerb
status: vorgeschlagen   # vorgeschlagen | bestaetigt | skip_national_online
variante: aufsatz       # aufsatz | eigenstaendig
basis:
  - meta.json
  - wettbewerber/liste.md
  - data/kunde.md
  - audits/local-gmb-schema.md (falls vorhanden)
basis_schema: local-gmb-schema.md   # nur bei variante: aufsatz, sonst weglassen
generiert_am: 2026-05-17T10:00:00Z
schema_version: 1.0

# Akteur-Set
akteur_set:
  kunde:
    slug: beispiel-zahnarzt
    name: Beispiel Zahnarztpraxis
  wettbewerber:
    - slug: alpha-zahnarzt
      name: Alpha Zahnarzt MVZ
      kategorie: regional
    - slug: beta-praxis
      name: Beta Praxis am Markt
      kategorie: regional
  auto_ergaenzung_in_phase_b: true   # lokale WB aus Local-Pack-Scan ergänzen

# Standorte (geerbt bei variante: aufsatz, sonst hier definiert)
standorte_kunde:
  - id: hauptsitz
    name: Beispiel Zahnarztpraxis
    adresse: Beispielstraße 1
    plz: "10115"
    stadt: Berlin
    stadtteil: Mitte
    gmb_url: https://maps.google.com/?cid=...
    service_area: false
    haupt: true
geerbt_aus: local-gmb-schema.md   # nur wenn standorte geerbt

suchradius_km: 15
geerbt_aus_suchradius: local-gmb-schema.md   # nur wenn geerbt

# Local-Pack-Keywords (geerbt oder definiert)
local_pack_keywords:
  - basis: zahnarzt
    modifier_typen: [stadt, stadtteil, in_der_naehe]
    expansion:
      - zahnarzt berlin
      - zahnarzt mitte
      - zahnarzt in der nähe
geerbt_aus_keywords: local-gmb-schema.md   # nur wenn geerbt

# LVS-Block-Gewichtung (Summe muss exakt 100 ergeben)
lvs_gewichtung:
  block_a_local_pack: 45
  block_b_review_substanz: 30
  block_c_profil_reife: 25
lvs_gewichtung_begruendung: >
  Such-getriebene Branche (Zahnarzt) — Local-Pack-Position höher gewichtet,
  weil sie fast direkt Anfragen bedeutet.

# Review-Velocity-Buckets (fix, nicht konfigurierbar)
review_velocity_buckets:
  - letzte_1_monat
  - letzte_3_monate
  - letzte_6_monate
  - letzte_12_monate

# Statistiken (vom Skill berechnet, vom Strategen NICHT manuell zu ändern)
statistik:
  anzahl_akteure: 6
  anzahl_kunden_standorte: 1
  anzahl_wettbewerber: 5
  anzahl_local_pack_keywords_gesamt: 12
  lvs_gewichtung_summe: 100
---

# Local-GMB-Wettbewerbs-Schema · KUNDE

[Body mit Begründungen und Pflicht-Review-Sektion — siehe unten]
```

## Body-Sektionen (Pflicht)

### 1. Übersicht

Welche Variante (`aufsatz` / `eigenstaendig`) und warum. Bei `aufsatz`: klarer Satz "Standorte, Suchradius und Local-Pack-Keywords aus dem bereits bestätigten 03-16-Schema übernommen — bitte nur LVS-Gewichtung und Akteur-Set prüfen." Bei `eigenstaendig`: Hinweis, dass `03-16` zuerst zu laufen die Doppel-Bestätigung erspart hätte.

Anzahl Akteure, Branche aus `meta.json`, warum nicht geskippt (Local-Bezug-Begründung).

### 2. Akteur-Set

Liste: Kunde (mit allen Standorten) plus regionale Wettbewerber aus `wettbewerber/liste.md`. Pro Wettbewerber Slug, Name, Quelle. Hinweis, dass Phase B per Local-Pack-Scan automatisch weitere lokale Akteure ergänzt (`local_wb_nicht_in_liste`-Auffälligkeit bei Häufung). Hard-Cap 10 Wettbewerber nennen.

### 3. Standorte und Local-Pack-Keywords

Bei `aufsatz`: kurz referenzieren ("aus bestätigtem 03-16-Schema, dort bereits geprüft"). Bei `eigenstaendig`: voll ausführen wie `03-16` Phase A — Standorte mit Begründung, Suchradius-Begründung, Local-Pack-Keywords mit Modifier-Wahl-Begründung, Hard-Cap-Box (30 Queries/Standort).

### 4. LVS-Block-Gewichtung

Die vorgeschlagenen Gewichte `gA / gB / gC` mit Begründung pro Block (warum diese Branche so gewichtet wird — siehe Branchen-Tabelle in `lvs-methodik.md`). Klarer Hinweis: **Summe muss exakt 100 ergeben**, Phase B validiert das.

Kurz erklären, was jeder Block misst:

> - **Block A — Local-Pack-Präsenz**: Anteil Top-3-/Top-10-Platzierungen über Standort × Keyword.
> - **Block B — Review-Substanz**: Volumen (log-skaliert) + Velocity (jüngere Reviews stärker) + Durchschnitts-Rating.
> - **Block C — GMB-Profil-Reife**: Kategorien, Attribute, Fotos, Posts-Frequenz, Antwort-Quote, Vollständigkeit.

### 5. Review-Velocity-Buckets

Kurzer Erklär-Block: die vier Buckets (1/3/6/12 Monate) sind fix für Vergleichbarkeit, jeder Bucket ist kumulativ ab heute rückwärts. In Phase B wird zusätzlich ein Velocity-Trend abgeleitet. Nicht konfigurierbar — der Stratege muss hier nichts prüfen.

### 6. Pflicht-Review-Sektion

Konkrete Eingriffspunkte:

Bei `aufsatz`:

- [ ] Akteur-Set vollständig? Wettbewerber vergessen oder zu viel?
- [ ] LVS-Gewichtung branchen-passend? (`gA + gB + gC = 100` zwingend)

Bei `eigenstaendig` zusätzlich:

- [ ] Standorte vollständig? Filialen ergänzen/streichen?
- [ ] Suchradius passend? (5–100 km plausibel)
- [ ] Local-Pack-Keywords sinnvoll kombiniert?

Abschluss: "Status auf `bestaetigt` setzen, dann Skill erneut aufrufen für Phase B."

## Skip-Status-Format

Bei Skip-Kandidat ohne Override (siehe SKILL.md Skip-Logik):

```yaml
---
skill: 03-20-local-gmb-wettbewerb
status: skip_national_online
generiert_am: ...
basis: [meta.json, data/kunde.md, audits/local-gmb-schema.md]
begruendung:
  ursache: "03-16-local-gmb-und-seo hat bereits skip_national_online gesetzt"
  # ODER bei eigenständiger Skip-Erkennung:
  region_definition: national
  gmb_touchpoint_kunde: nicht_vorhanden
  regionale_wettbewerber_in_liste: 0
override_argument: trotzdem laufen
---

# Local-GMB-Wettbewerbsvergleich · KUNDE — geskippt

Kein Local-Bezug erkannt. [Begründung]

Wenn das falsch ist, Skill mit Argument "trotzdem laufen" erneut aufrufen.
```

## Validierung in Phase B

Beim Phase-B-Start prüft der Skill:

1. `status: bestaetigt`? Sonst Abbruch.
2. `akteur_set.kunde` vorhanden, `standorte_kunde` mindestens 1 Eintrag mit `stadt` und entweder `adresse` oder `service_area: true`.
3. `lvs_gewichtung`: drei Blöcke vorhanden, Werte numerisch, **Summe exakt 100**.
4. `local_pack_keywords`: mindestens 3 Basis-Keywords mit jeweils mindestens 1 Modifier-Typ.
5. `review_velocity_buckets`: alle vier (1/3/6/12) vorhanden.
6. `suchradius_km`: numerisch, 5 ≤ x ≤ 100.

Bei Fehler: konkreter Hinweis, welches Feld fehlt oder falsch ist (besonders bei `lvs_gewichtung_summe ≠ 100`).
