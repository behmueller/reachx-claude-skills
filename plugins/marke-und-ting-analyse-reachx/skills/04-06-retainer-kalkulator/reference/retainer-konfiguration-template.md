# Phase-A-Output-Template: `synthese/retainer-konfiguration.md`

Strukturelle Vorlage fuer das Phase-A-Output des `04-06-retainer-kalkulator`. Enthaelt Service-Level-Definitionen, Default-Kanal-Verantwortlichkeit pro Service-Level, Reporting- und Workshop-Frequenz-Defaults sowie Begruendungs-Templates.

---

## 1. Frontmatter-Struktur (Pflicht)

```yaml
---
skill: 04-06-retainer-kalkulator
status: vorgeschlagen   # vorgeschlagen | bestaetigt
basis_zentral:
  stundensaetze: reference/reachx-stundensaetze.md
  stundensaetze_version: "2026.05"
  aufwands_bandbreiten: reference/aufwands-bandbreiten.md
  aufwands_bandbreiten_version: "2026.05"
basiert_auf:
  briefing: data/briefing.md     # null wenn nicht vorhanden
  kanal_chancen: synthese/kanal-chancen.md
  forecast: synthese/forecast.md
  plan_90_tage: synthese/90-tage-plan.md
generiert_am: 2026-05-14T12:30:00Z
schema_version: "1.0"

# Kunden-spezifische Konfiguration
service_level: wachstum             # basis | wachstum | vollservice
vertragslaufzeit_monate: 12         # 6 | 12 | 24

kanal_verantwortlichkeit:
  # Map pro Top-Kanal aus kanal-chancen Top-3 plus alle weiteren mit chancen_score >= 50
  seo:
    reachx_anteil_prozent: 70
    kunde_anteil_prozent: 30
    skills: [SEO_MANAGER, CONTENT_MANAGER, STRATEGIE_MANAGER]
  sea:
    reachx_anteil_prozent: 100
    kunde_anteil_prozent: 0
    skills: [SEA_MANAGER, CONTENT_MANAGER, DESIGNER, STRATEGIE_MANAGER]
  meta_ads:
    reachx_anteil_prozent: 80
    kunde_anteil_prozent: 20
    skills: [SEA_MANAGER, DESIGNER, STRATEGIE_MANAGER]

reporting_frequenz: monatlich       # monatlich | quartal | woechentlich_stand_up (mehrere moeglich als Liste)
strategie_workshop_frequenz: quartal  # quartal | halbjaehrlich

# Optionale Stundensatz-Overrides
stundensatz_override: null
  # Alternativ z. B.:
  # stundensatz_override:
  #   neukunden_rabatt_prozent: 10
  #   mengen_rabatt_prozent: 8

# Begruendung pro Feld (vom Skill generiert, Stratege kann editieren)
begruendung:
  service_level: "Briefing nennt 1-FTE-Inhouse-Marketing-Team, REACHX uebernimmt Strategie plus 2-3 Top-Kanaele operativ — wachstum passt."
  vertragslaufzeit: "12 Monate Standard, SEO braucht 9 Monate Ramp-up (siehe forecast.md Annahmen)."
  kanal_verantwortlichkeit: "SEO und SEA als Top-2 aus kanal-chancen.md, REACHX uebernimmt operativ; Content gemeinsam mit Kunde."
  reporting_frequenz: "Monatliches Reporting plus Strategie-Call ist Mittelstand-Standard."
  strategie_workshop_frequenz: "Quartal-Workshops fuer wachstum-Service-Level, mehr Strategie-Tiefe als basis."
  stundensatz_override: "Kein Override — Standard-Saetze aus zentralem Stundensatz-Dokument."

# Hinweise des Skills an den Strategen
strategen_hinweise:
  - "Wenn Kunde im Gespraech SEA als Prio 1 vor SEO nannte, Kanal-Verantwortlichkeit anpassen."
  - "Wenn Kunde mit kleinem Budget pruefen will, Service-Level basis pruefen."
  - "Wenn Forecast Best-Szenario sehr ambitioniert ist, 24 Monate Vertragslaufzeit pruefen."

# Validierung
inputs_gefunden:
  - synthese/kanal-chancen.md
  - synthese/forecast.md
  - synthese/90-tage-plan.md
inputs_fehlen: []   # Liste fehlender empfohlener Inputs
---
```

---

## 2. Body-Struktur (Pflicht-Sektionen)

```markdown
# Retainer-Konfiguration fuer KUNDENNAME

## Uebersicht

Dieses Schema enthaelt die projektspezifischen Konfigurations-Entscheidungen fuer den
Retainer-Kalkulator. Stundensaetze und Aufwands-Bandbreiten kommen aus den zentralen
Reference-Dateien (Version `2026.05`).

Bitte folgende Felder pruefen, anpassen und dann `status: bestaetigt` setzen:

- `service_level` — basis / wachstum / vollservice
- `vertragslaufzeit_monate` — 6 / 12 / 24
- `kanal_verantwortlichkeit` — Map pro Top-Kanal mit REACHX-/Kunde-Anteil
- `reporting_frequenz` — monatlich / quartal / woechentlich_stand_up
- `strategie_workshop_frequenz` — quartal / halbjaehrlich
- `stundensatz_override` — null oder konkrete Override-Map

Pflicht-Review durch den Strategen — diese Konfiguration steuert die Preis-Empfehlung
am Ende der MTA und damit das verkaufs-relevante Dokument.

## Service-Level — was bedeuten basis / wachstum / vollservice?

(Wird vom Skill aus `retainer-konfiguration-template.md` Abschnitt 3 kopiert)

## Begruendung der Vorschlaege

(Detail-Begruendung pro Feld aus Frontmatter rendered)

## Strategen-Hinweise

(Liste aus Frontmatter rendered)

## Was kommt aus den zentralen Reference-Dateien

Alle Felder, die NICHT in dieser Konfiguration genannt sind, kommen aus
`reference/reachx-stundensaetze.md` und `reference/aufwands-bandbreiten.md`. Dazu
zaehlen:

- Stundensaetze pro Rolle (STRATEGIE_LEAD, SEO_MANAGER, SEA_MANAGER, ...)
- Aufwands-Bandbreiten pro Massnahmen-Typ (Setup, Laufend, Reporting, Workshops)
- Branchen-typische Retainer-Vergleichs-Ranges

Wenn diese Werte agentur-weit aktualisiert werden sollen, die zentralen Dateien
editieren — NICHT diese Konfiguration. Bei Aenderungen wird der Skill versioniert.
```

---

## 3. Service-Level-Definitionen (Referenz)

Drei Service-Level mit klarer Abgrenzung:

### `basis` — Beratung plus Strategie plus Reporting

- **Charakter**: REACHX als strategischer Sparringspartner, Operatives beim Kunden
- **Typische Kunden-Reife**: Inhouse-Team mit 2+ FTE Marketing, eigenes Tracking, eigene Content-Produktion
- **REACHX-Anteil pro Kanal**: 30-50% (Strategie, Reporting, Review)
- **Inhalt**: Strategie-Workshops, monatliches Reporting, Beratungs-Stunden, Kanal-Reviews, kein operatives Hands-on
- **Preis-Hausnummer (Realistisch)**: 3.000-7.000 EUR/Monat (branchen-abhaengig)

### `wachstum` — Hybrid

- **Charakter**: REACHX uebernimmt 2-3 Top-Kanaele operativ, Rest gemeinsam mit Kunde
- **Typische Kunden-Reife**: Inhouse-Team 1 FTE oder Junior-Marketer / Werkstudent
- **REACHX-Anteil pro Top-Kanal**: 60-80%
- **Inhalt**: Strategie plus operatives Hands-on in 2-3 Kanaelen, monatliches Reporting plus Strategie-Call, Quartal-Workshops
- **Preis-Hausnummer (Realistisch)**: 6.000-13.000 EUR/Monat (branchen-abhaengig)

### `vollservice` — REACHX uebernimmt alles im Top-Kanal-Mix

- **Charakter**: REACHX als Full-Service-Marketing-Team
- **Typische Kunden-Reife**: Kein oder sehr junges Inhouse-Team, Kunde liefert nur Freigaben und Assets
- **REACHX-Anteil pro Top-Kanal**: 90-100%
- **Inhalt**: Vollumfaengliches Operatives plus Strategie plus Reporting plus Workshops, evtl. Hands-on-CMO-Vertretung
- **Preis-Hausnummer (Realistisch)**: 12.000-25.000 EUR/Monat (branchen-abhaengig)

---

## 4. Default-Kanal-Verantwortlichkeit pro Service-Level

Pro Service-Level Default-Verteilung — dient als Ausgangspunkt fuer Phase A. Der Stratege kann pro Kanal anpassen.

| Kanal | basis (REACHX-Anteil) | wachstum (REACHX-Anteil) | vollservice (REACHX-Anteil) |
|---|---|---|---|
| SEO | 40% (Strategie + Reporting) | 70% (operativ + Strategie) | 100% |
| SEA / Google Ads | 50% (Steuerung + Reporting) | 100% (komplett operativ) | 100% |
| Meta Ads | 30% (Strategie + Reporting) | 80% (operativ + Strategie) | 100% |
| LinkedIn Ads | 30% | 80% | 100% |
| Content / Blog | 30% (Briefings + Strategie) | 60% (Redaktion gemeinsam) | 100% |
| Newsletter | 20% (Strategie + Vorlagen) | 60% | 90% |
| Social-organisch | 20% (Konzept + Coaching) | 50% (gemeinsam) | 90% |
| Local-SEO / GMB | 30% | 70% | 100% |
| CRO / Website | 50% (Konzept + Review) | 80% | 100% |
| Tracking / Daten | 60% (Setup + Monitoring) | 90% | 100% |

Default-Werte sind als Ausgangspunkt zu verstehen. Phase A passt sie pro Kunde an Briefing-Signale und 90-Tage-Plan-Verteilung an.

---

## 5. Heuristik fuer Phase-A-Default-Auswahl

**Service-Level**:

1. Inhouse-FTE ≥ 2 (aus Briefing) → `basis`
2. Inhouse-FTE 1 oder Junior (aus Briefing) → `wachstum`
3. Inhouse-FTE 0 (aus Briefing) → `vollservice`
4. Touchpoint-Inventur zeigt inaktive Profile → Verschiebung Richtung `vollservice`
5. Briefing fehlt → `wachstum` als sicherer Default

**Vertragslaufzeit**:

1. Default 12 Monate
2. Briefing nennt 6 Monate / "Probelauf" → 6 Monate, ABER Auffaelligkeit `vertragslaufzeit_zu_kurz_fuer_ramp_up` falls SEO oder Content > 30% Stunden-Anteil
3. Briefing nennt 24 Monate / "langfristige Partnerschaft" → 24 Monate
4. Forecast Best-Szenario > 3x heutige Performance → 24 Monate als Alternative vorschlagen

**Reporting-Frequenz**:

| Service-Level | Default |
|---|---|
| basis | monatlich plus Quartal-Workshop |
| wachstum | monatlich plus optional woechentlich_stand_up |
| vollservice | monatlich plus woechentlich_stand_up |

**Strategie-Workshop-Frequenz**:

| Service-Level | Default |
|---|---|
| basis | quartal |
| wachstum | quartal |
| vollservice | halbjaehrlich (mehr Tagesgeschaeft macht weniger formelle Workshops noetig) |

---

## 6. Validierungs-Regeln fuer Phase B (Auszug)

- `service_level` ∈ {basis, wachstum, vollservice}
- `vertragslaufzeit_monate` ∈ {6, 12, 24}
- `kanal_verantwortlichkeit` enthaelt mindestens die Top-3-Kanaele aus `kanal-chancen.md`
- Pro Kanal: `reachx_anteil_prozent + kunde_anteil_prozent` = 100 (Toleranz +/- 2)
- `reporting_frequenz` ∈ {monatlich, quartal, woechentlich_stand_up}, kann als Liste angegeben werden
- `strategie_workshop_frequenz` ∈ {quartal, halbjaehrlich}
- `stundensatz_override` ist `null` oder enthaelt valide Rabatt-Konstanten aus `reachx-stundensaetze.md`
