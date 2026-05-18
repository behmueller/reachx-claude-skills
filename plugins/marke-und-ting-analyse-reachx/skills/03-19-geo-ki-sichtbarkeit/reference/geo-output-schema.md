# GEO-Output-Schema

Vollständiges Schema für die Dateien des `03-19-geo-ki-sichtbarkeit`-Skills:

- `audits/geo-sichtbarkeit-schema.md` — Phase-A-Schema-Datei (Schema-vor-Lauf)
- `audits/geo-sichtbarkeit.md` — Aggregat (Markdown mit YAML-Frontmatter)
- `audits/geo-sichtbarkeit-prompts.csv` — Prompt × Engine × Akteur (CSV)
- `audits/geo-sichtbarkeit-quellen.csv` — zitierte Domains (CSV)
- `assets/raw/geo-*.json.gz` (Drive) — gzip-komprimierte Roh-Caches; lokal `~/.cache/reachx-mta/<slug>/raw/geo-*.json`

---

## 1. Schema-Datei `audits/geo-sichtbarkeit-schema.md` (Phase A)

Wird vom Skill in Phase A generiert, vom Strategen reviewt, dann mit `status: bestaetigt` für Phase B freigegeben.

```markdown
---
# === Skill-Metadaten ===
skill: 03-19-geo-ki-sichtbarkeit
phase: A
generiert_am: <ISO-8601>
schema_version: "1.0"
status: vorgeschlagen          # Stratege ändert nach Review zu: bestaetigt
basis: <welche Dateien gelesen wurden — z.B. meta.json, data/kunde.md, audits/seo-keywords.csv>

# === Methodik-Konfiguration ===
brand_radar: nicht_verfuegbar  # verfuegbar | nicht_verfuegbar — aus dem Tool-Health-Check
probe_wiederholungen: 1        # 1 = eine Probe pro Prompt×Engine; 2-3 = mehrfach proben, Mehrheits-Befund

# === Engine-Set ===
engines:
  - chatgpt
  - gemini
  - perplexity
  # - claude                   # optional — analog Perplexity behandelt

# === Prompt-Inventar (~10 Prompts, gemischt) ===
prompt_inventar:
  - prompt_id: p01
    text: "Wie funktioniert <Branchen-Thema>?"
    typ: informational         # informational | kommerziell | lokal
    funnel_stufe: TOFU         # TOFU | MOFU | BOFU
    begruendung: "<warum dieser Prompt — Bezug zu Portfolio / GSC-Query / Briefing-Pain-Point>"
  - prompt_id: p02
    text: "Bester Anbieter für <Leistung>"
    typ: kommerziell
    funnel_stufe: BOFU
    begruendung: "..."
  - prompt_id: p03
    text: "Bester <Leistung>-Anbieter in <Stadt>"
    typ: lokal
    funnel_stufe: BOFU
    begruendung: "lokale Variante — Kunde ist regional tätig"
  # ... bis ~10

# === Akteur-Set ===
akteur_set:
  - akteurs_slug: kunde-gmbh
    akteurs_name: "Kunde GmbH"
    akteurs_typ: kunde
    domain: kunde.de
    synonyme: ["Kunde GmbH", "Kunde", "kunde.de"]
  - akteurs_slug: wettbewerber-alpha
    akteurs_name: "Wettbewerber Alpha"
    akteurs_typ: wettbewerber_kunde_genannt
    domain: alpha.de
    synonyme: ["Wettbewerber Alpha", "Alpha AG", "alpha.de"]
  # ... relevante WBs aus wettbewerber/liste.md
---

# Schema für 03-19-geo-ki-sichtbarkeit: <Kundenname>

## Methodik-Hinweis

Brand Radar: **<verfuegbar | nicht_verfuegbar>**.
<Bei nicht_verfuegbar: "Kein Brand-Radar-Abo erkannt — der Lauf wird rein qualitativ.
Die Befunde sind Prompt-Stichproben mit Konfidenz niedrig.">

## Begründung des Prompt-Inventars

<Warum diese ~10 Prompts? Mix aus informational / kommerziell / lokal erklären,
Bezug zu Portfolio, echten Keywords und Branche.>

## Begründung des Akteur-Sets

<Welche Wettbewerber wurden aufgenommen und warum — nicht zwingend alle aus
liste.md, nur die strategisch relevanten.>

## Pflicht-Review durch den Strategen

- [ ] **Prompt-Inventar**: decken die Prompts die relevanten Such-Situationen ab?
      Fehlt ein Cluster? Sind die lokalen Varianten passend (oder Kunde rein national)?
- [ ] **Akteur-Set**: sind die richtigen Wettbewerber dabei? Synonyme/Schreibvarianten vollständig?
- [ ] **Engines**: ist das Default-Set passend? Claude ergänzen?
- [ ] **probe_wiederholungen**: bei 1 belassen oder auf 2-3 erhöhen für stabilere Stichprobe?

**Nach dem Review:** Setze `status: bestaetigt` im Frontmatter, dann läuft Phase B.
```

### Schema-Validierung (Phase B, vor dem Lauf)

1. `status: bestaetigt` im Frontmatter — sonst Abbruch mit Hinweis auf Phase A
2. `engines` enthält mindestens 1 Engine
3. `prompt_inventar` enthält mindestens 5 Prompts
4. jeder Prompt hat `prompt_id`, `text`, `typ`, `funnel_stufe`
5. `akteur_set` enthält den Kunden (`akteurs_typ: kunde`); WBs optional (Kunden-only erlaubt)
6. jeder Akteur hat mindestens den Marken-Namen in `synonyme`

Bei Fehler **konkret benennen, welches Feld** korrigiert werden muss.

---

## 2. `audits/geo-sichtbarkeit.md` (Aggregat)

### Frontmatter (Phase B)

```yaml
---
# === Skill-Metadaten ===
skill: 03-19-geo-ki-sichtbarkeit
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  schema_datei: audits/geo-sichtbarkeit-schema.md
  schema_bestaetigt_am: <ISO-8601>
  liste_md: wettbewerber/liste.md
  liste_bestaetigt_am: <ISO-8601 oder null>
basis_inputs:
  - datei: audits/geo-sichtbarkeit-schema.md
    generiert_am: <ISO-8601>
modus: voll_qualitativ          # voll_quantitativ | voll_qualitativ | kunden_only
brand_radar: nicht_verfuegbar   # verfuegbar | nicht_verfuegbar
methode:
  - qualitative_probe           # immer
  # - brand_radar               # nur bei voll_quantitativ
konfidenz: niedrig              # Probe-Werte sind Stichproben — Pflicht-Kennzeichnung
datenstand: <YYYY-MM-DD>

# === Konfiguration ===
engines: [chatgpt, gemini, perplexity]
prompts_gesamt: 10
probe_wiederholungen: 1

# === Akteurs-Sichtbarkeit ===
akteure:
  - akteurs_slug: kunde-gmbh
    akteurs_typ: kunde
    prompts_sichtbar: 4
    prompts_gesamt: 10
    sichtbarkeits_quote: 0.40   # Indikator, Konfidenz niedrig — keine belastbare Quote
    engine_abdeckung: 2         # in 2 von 3 Engines mindestens 1× sichtbar
    nennungs_verteilung:
      genannt: 2
      zitiert: 1
      genannt_und_zitiert: 1
      nicht_sichtbar: 6
    brand_radar_mentions: null  # int bei voll_quantitativ, sonst null
    brand_radar_sov: null       # float 0-1 bei voll_quantitativ
  - akteurs_slug: wettbewerber-alpha
    akteurs_typ: wettbewerber_kunde_genannt
    prompts_sichtbar: 8
    prompts_gesamt: 10
    sichtbarkeits_quote: 0.80
    engine_abdeckung: 3
    nennungs_verteilung:
      genannt: 3
      zitiert: 2
      genannt_und_zitiert: 3
      nicht_sichtbar: 2
    brand_radar_mentions: null
    brand_radar_sov: null

# === Quellen-Ökosystem (Top-Domains) ===
quellen_oekosystem:
  - domain: reddit.com
    quellen_typ: community
    zitations_anzahl: 14
    gehoert_akteur: null
  - domain: einbranchenportal.de
    quellen_typ: branchenportal
    zitations_anzahl: 9
    gehoert_akteur: null
  - domain: alpha.de
    quellen_typ: eigene_site
    zitations_anzahl: 5
    gehoert_akteur: wettbewerber-alpha

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: kunde_unsichtbar
    titel: "Kunde in der Mehrheit der KI-Antworten nicht präsent"
    relevanz: hoch
    betroffene_akteure: [kunde-gmbh]
    betroffene_engines: [chatgpt, gemini]
    handlung: "FAQ-/Entity-Schema und Long-Form-Content aufbauen, Quell-Präsenz auf zitierten Plattformen"
---
```

### Frontmatter (Kunden-only)

Wie oben, aber `modus: kunden_only`, `akteure` enthält nur den Kunden, WB-bezogene Auffälligkeiten entfallen.

### Body-Struktur

```markdown
# GEO-KI-Sichtbarkeit: <Kundenname>

## Übersicht & Kernbefund

**Kunden-Sichtbarkeit: 4 von 10 Prompts (Quote 40 % — Stichprobe, Konfidenz niedrig)
— Position 3 von 4 Akteuren.**

<3-4 Sätze: wie sichtbar der Kunde in KI-Suche ist, wie er gegen die WBs steht.>

## Einordnung — GEO ist ein Multiplikator, kein Budgetposten

GEO-Sichtbarkeit entsteht nicht durch ein eigenes Budget, sondern als Folge starker
SEO-/Content-/Reputations-Arbeit. Die folgenden Befunde fließen als Verstärker in
die SEO- und Content-Empfehlungen ein — sie begründen keine eigene Investitionszeile.

## Sichtbarkeit pro Akteur

### Kunde GmbH (Kunde)
- 4 von 10 Prompts sichtbar, in 2 von 3 Engines
- Nennungs-Art: 2× genannt, 1× zitiert, 1× genannt_und_zitiert, 6× nicht sichtbar
<bei voll_quantitativ: Brand-Radar-Mentions und Share of Voice>

### Wettbewerber Alpha
- ...

## Engine-Vergleich

<Welche Engine zeigt welchen Akteur wie oft; Divergenzen — z.B. Kunde in Perplexity
sichtbar, in Google AI Overviews nicht.>

## Quellen-Ökosystem

<Top-zitierte Domains mit Typ. Was bedeutet das für die Quell-Strategie:
Wo muss der Kunde präsent sein, damit die Engines ihn zitieren?>

## Auffälligkeiten

<Liste der getriggerten Auffälligkeiten mit Titel, Relevanz, Handlung.>

## GEO-Hebel-Empfehlung

Konkrete, SEO-/Content-verankerte Hebel (siehe geo-analyse-methodik.md, Hebel-Katalog):
1. **FAQ-/Entity-Schema** — ...
2. **Long-Form-Content mit Preistransparenz** — ...
3. **Quell-Präsenz auf <zitierte Plattform>** — ...

Jeder Hebel ist als Multiplikator auf einen bestehenden Kanal (SEO, Content,
Branchenportale) formuliert, nicht als neuer Kanal.

## Methodik & Konfidenz

Die Sichtbarkeits-Werte beruhen auf qualitativen Prompt-Stichproben. KI-Antworten
sind nicht-deterministisch und personalisiert — die Quoten sind Indikatoren, keine
belastbaren Messwerte (`konfidenz: niedrig`).
<bei voll_quantitativ: "Brand Radar liefert die belastbarere Aggregat-Lesart —
getrennt ausgewiesen, nicht mit den Probe-Werten verrechnet.">
```

---

## 3. `audits/geo-sichtbarkeit-prompts.csv`

Eine Zeile pro Prompt × Engine × Akteur.

| Spalte | Typ | Beschreibung | Beispiel |
|---|---|---|---|
| `prompt_id` | string | aus dem Schema | `p02` |
| `prompt_text` | string | Prompt-Wortlaut | `Bester Anbieter für ...` |
| `prompt_typ` | enum | `informational \| kommerziell \| lokal` | `kommerziell` |
| `funnel_stufe` | enum | `TOFU \| MOFU \| BOFU` | `BOFU` |
| `engine` | enum | `chatgpt \| gemini \| perplexity \| claude` | `perplexity` |
| `akteurs_slug` | string | aus dem Akteur-Set | `kunde-gmbh` |
| `akteurs_typ` | enum | `kunde \| wettbewerber_kunde_genannt \| wettbewerber_regional \| wettbewerber_ueberregional` | `kunde` |
| `akteurs_name` | string | Marken-Name für Anzeige | `Kunde GmbH` |
| `sichtbar` | bool | `true` wenn genannt und/oder zitiert | `true` |
| `nennungs_art` | enum | `genannt \| zitiert \| genannt_und_zitiert \| nicht_sichtbar` | `zitiert` |
| `position_in_antwort` | enum | `prominent \| erwähnt \| randständig \| —` | `erwähnt` |
| `antwort_auszug` | string | erste 200 Zeichen der Antwort, Newlines durch Space ersetzt | `"Zu den Anbietern zählen ..."` |
| `methode` | enum | immer `qualitative_probe` | `qualitative_probe` |
| `konfidenz` | enum | immer `niedrig` für Probe-Zeilen | `niedrig` |
| `datenstand_iso` | ISO-Datum | wann erhoben | `2026-05-17` |

Bei `probe_wiederholungen > 1`: pro Prompt × Engine × Akteur **eine** Zeile mit dem aggregierten Mehrheits-Befund (nicht eine Zeile pro Wiederholung).

Bei `probe_fehlgeschlagen` (keine generative Antwort erreichbar): die betroffenen Zeilen mit `nennungs_art: nicht_sichtbar`, `sichtbar: false` und einem Body-Hinweis — UND der Prompt zählt nicht in den `prompts_gesamt`-Nenner der betroffenen Engine.

**Encoding:** UTF-8, Komma-Trenner, Anführungszeichen-Escape bei Text-Feldern.

---

## 4. `audits/geo-sichtbarkeit-quellen.csv`

Eine Zeile pro zitierter Domain × Engine.

| Spalte | Typ | Beschreibung | Beispiel |
|---|---|---|---|
| `domain` | string | normalisiert, ohne `www.`, lowercase | `reddit.com` |
| `quellen_typ` | enum | `branchenportal \| community \| fachmedium \| eigene_site \| wissensplattform \| sonstige` | `community` |
| `engine` | enum | welche Engine zitiert diese Domain | `perplexity` |
| `zitations_anzahl` | int | wie oft über alle Prompts dieser Engine zitiert | `14` |
| `prompts_die_zitieren` | string | Pipe-separierte `prompt_id`-Liste | `p01\|p04\|p07` |
| `gehoert_akteur` | string | Akteurs-Slug, wenn Domain einem Akteur gehört, sonst leer | `wettbewerber-alpha` |
| `datenstand_iso` | ISO-Datum | wann erhoben | `2026-05-17` |

Wenn Brand Radar verfügbar ist und `cited-domains` liefert: diese Domains in die CSV mergen, mit derselben Typ-Klassifikation. Engine-Wert dann der Brand-Radar-`data_source`.

---

## 5. Roh-Cache-Dateien

| Datei (lokal `~/.cache/reachx-mta/<slug>/raw/`) | Inhalt | Format |
|---|---|---|
| `geo-probe-<engine>-<prompt_id>.json` | Roh-Antwort einer Probe (Antwort-Text, Quellen, Timestamp) | JSON Object |
| `geo-brand-radar-<tool>.json` | Brand-Radar-Tool-Output, unverändert (nur voll_quantitativ) | JSON |
| `geo-prompt-inventar.json` | das bestätigte Prompt-Inventar als Snapshot | JSON |

Roh-Daten **nicht** vor dem Cache umstrukturieren. Am Skill-Ende gzip-komprimiert nach Drive `assets/raw/`.

---

## Validierungs-Regeln

Beim Schreiben der Outputs prüft der Skill:

1. **Frontmatter valides YAML** — pyyaml-Parse, bei Fehler abbrechen
2. **`konfidenz: niedrig`** ist im Frontmatter gesetzt (Pflicht-Kennzeichnung der Probe-Werte)
3. **`methode` enthält `qualitative_probe`** — und `brand_radar` genau dann, wenn `modus: voll_quantitativ`
4. **`modus` und `brand_radar` konsistent** — `voll_quantitativ` nur bei `brand_radar: verfuegbar`
5. **CSV-Header matchen exakt** die oben definierten Schemas
6. **`sichtbarkeits_quote`** liegt in `[0, 1]` und entspricht `prompts_sichtbar / prompts_gesamt`
7. **Auffälligkeiten-Block vorhanden** — der Block `auffaelligkeiten` existiert im Output; 0 Einträge sind valide (z. B. wenn GEO-Sichtbarkeit unauffällig ist). `kunde_unsichtbar` ist stets ein expliziter Befund, falls zutreffend.
8. **Einordnungs-Block vorhanden** — der Body enthält den „GEO ist ein Multiplikator, kein Budgetposten"-Block

## Versionierung

Wenn sich das Schema ändert: `schema_version` in den Outputs hochzählen, im Skill Versions-Check vor dem Lesen alter Outputs.

Aktuelle Version: **1.0**
