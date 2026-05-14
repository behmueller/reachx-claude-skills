# Phase-A-Output-Template: `audits/local-gmb-schema.md`

Dieses Template definiert das Format der Schema-Datei, die in Phase A des `03-16-local-gmb-und-seo`-Skills geschrieben wird. Das Schema steuert in Phase B die konkrete Recherche.

## Datei-Format

```markdown
---
skill: 03-16-local-gmb-und-seo
status: vorgeschlagen   # vorgeschlagen | bestaetigt | skip_national_online
basis:
  - meta.json
  - data/kunde.md
  - wettbewerber/liste.md
  - data/briefing.md
  - audits/seo-keywords.csv (falls vorhanden)
generiert_am: 2026-05-13T10:00:00Z
schema_version: 1.0

# strukturierte Kern-Felder
standorte_kunde:
  - id: hauptsitz
    name: Beispielname GmbH
    adresse: Beispielstraße 1
    plz: "10115"
    stadt: Berlin
    stadtteil: Mitte
    gmb_url: https://maps.google.com/?cid=...
    service_area: false
    haupt: true

suchradius_km: 15

local_pack_keywords:
  - basis: zahnarzt
    modifier_typen: [stadt, stadtteil, in_der_naehe]
    expansion:
      - zahnarzt berlin
      - zahnarzt mitte
      - zahnarzt prenzlauer berg
      - zahnarzt in der nähe

lokale_wettbewerber:
  aus_liste_md:
    - slug: muster-zahnarzt-mitte
      website: muster-zahnarzt.de
  ergaenzungen_aus_local_pack: in_phase_b

gmb_review_themen:
  - wartezeit
  - beratung
  - freundlichkeit
  - schmerzen
  - preise
  - erreichbarkeit

nap_cross_check_quellen:
  - gmb
  - website_impressum
  - branchenportale_aus_portale_md

# Statistiken (vom Skill berechnet, vom Strategen NICHT manuell zu ändern)
statistik:
  anzahl_standorte: 1
  anzahl_local_pack_keywords_gesamt: 12
  anzahl_regionale_wettbewerber: 5
  anzahl_review_themen: 6
---

# Local-SEO-Schema · KUNDE

[Body mit Begründungen und Pflicht-Review-Sektion — siehe unten]
```

## Body-Sektionen (Pflicht)

### 1. Übersicht

Kurzer Block: was hat der Skill gesehen (Anzahl Standorte, Branche aus meta.json, Region-Definition aus wettbewerber-Schema falls vorhanden), warum nicht geskippt (Begründung für Local-Bezug).

### 2. Standorte des Kunden

Liste mit Begründung pro Standort. Beispiel:

> **Hauptsitz**: Beispielstraße 1, 10115 Berlin-Mitte. Quelle: GMB-Touchpoint aus `data/kunde.md.touchpoints_gefunden`, Adresse aus GMB-Profil verifiziert.
>
> **Filiale Charlottenburg**: Kantstraße 100, 10623 Berlin. Quelle: aus `data/briefing.md.standorte` übernommen, GMB-Profil-URL unbekannt — wird in Phase B per Maps-Suche nachgezogen.

Hinweis-Block am Ende: "Wenn weitere Filialen existieren, bitte hier ergänzen."

### 3. Suchradius-Begründung

Ein Satz mit Branchen-Default-Begründung. Beispiel:

> Suchradius: **15 km** — urbane Branche (Zahnarzt) mit hoher Dichte in Berlin-Mitte, Patienten suchen typischerweise innerhalb des eigenen Stadtteils plus 1-2 Nachbar-Bezirke.

### 4. Local-Pack-Keywords

Pro Basis-Keyword eine Begründung der Modifier-Wahl. Beispiel:

> **Basis "zahnarzt"** — aus `audits/seo-keywords.csv` als Top-Service-Keyword identifiziert (Volumen 12.000/Monat). Modifier `stadt` (Berlin), `stadtteil` (Mitte, Prenzlauer Berg — die zwei direkten Einzugs-Bezirke), `in_der_naehe` (zunehmend wichtig durch mobile Suche).

Faustregel-Box:

> Hard-Cap: max 30 Local-Pack-Queries pro Standort, max 10 Basis-Keywords. Bei vielen Filialen ggf. Standorte oder Keywords priorisieren.

### 5. Lokale Wettbewerber

Liste der WBs aus `wettbewerber/liste.md` mit Kategorie `regional`. Hinweis, dass in Phase B per Apify-Maps-Scrape automatisch weitere lokale Akteure identifiziert werden — bei Häufung Auffälligkeit `local_wb_nicht_in_liste`.

### 6. Branchen-typische Review-Themen

Liste der Themen mit kurzer Begründung pro Thema. Beispiel:

> - **Wartezeit** — in Zahnarzt-Reviews häufig, oft Friktions-Punkt
> - **Beratung** — Differenzierungs-Achse für Premium-Praxen
> - **Schmerzen** — emotionaler Trigger, taucht in negativen wie positiven Reviews auf

Hinweis: "Stratege kann ergänzen/streichen — die Themen steuern die Sentiment-Cluster in Phase B."

### 7. NAP-Cross-Check-Quellen

Liste der Quellen, die der Skill in Phase B abfragt. Bei fehlender `wettbewerber/portale.md` Hinweis, dass Branchenportal-NAP weggelassen wird.

### 8. Pflicht-Review-Sektion

Konkrete Eingriffspunkte für den Strategen:

- [ ] Standorte vollständig? Filialen ergänzen oder streichen?
- [ ] Suchradius passend? (5–100 km plausibel)
- [ ] Local-Pack-Keywords sinnvoll? Modifier-Mischung okay?
- [ ] Lokale Wettbewerber: jemand vergessen?
- [ ] Review-Themen branchen-relevant? Ergänzungen?
- [ ] NAP-Quellen: Branchenportale relevant für diesen Kunden?

Status auf `bestaetigt` setzen, dann Skill erneut aufrufen für Phase B.

---

## Branchen-Defaults

### Suchradius pro Branchen-Typ

| Branchen-Typ | Beispiele | Default `suchradius_km` |
|---|---|---|
| Urbane Dienstleister, hohe Dichte | Zahnarzt, Allgemeinarzt, Friseur, Café | 15 |
| Spezialisierte Dienstleister, mittlere Dichte | Anwalt, Steuerberater, Heilpraktiker | 25 |
| Sehr spezialisierte Dienstleister | Kardiologe, Branchen-Berater, Orthopäde | 50 |
| Lokales Handwerk, Service-Area-Business | Klempner, Elektriker, Maler | 25 |
| Lokale Hospitality | Restaurant, Hotel, Eventlocation | 15 |
| Werkstatt, KFZ | Auto-Werkstatt, Fahrradladen | 25 |
| Hausverwaltung, Immobilien | Hausverwaltung, Makler | 25 |
| Filialisten (regional) | Bäckerei-Kette, Fitness-Studio, Tankstelle | 15 (pro Filiale) |
| B2B-Mittelstand mit Standort-Bezug | Druckerei, Werbeagentur regional | 50 |

### Review-Themen pro Branche

#### Arzt / Zahnarzt / Heilpraktiker

```yaml
gmb_review_themen:
  - wartezeit
  - beratung
  - freundlichkeit
  - schmerzen
  - preise
  - sprechstundenhilfe
  - erreichbarkeit
  - termin_verfuegbarkeit
```

#### Restaurant / Café

```yaml
gmb_review_themen:
  - essen_qualitaet
  - service
  - atmosphaere
  - preise
  - wartezeit
  - reservierung
  - sauberkeit
  - getraenke
```

#### Handwerker / Klempner / Elektriker

```yaml
gmb_review_themen:
  - puenktlichkeit
  - qualitaet
  - preis_leistung
  - sauberkeit
  - kommunikation
  - rueckrufe
  - termin_treue
```

#### Anwalt / Steuerberater

```yaml
gmb_review_themen:
  - beratung
  - erfolg
  - verstaendlichkeit
  - honorar
  - erreichbarkeit
  - empathie
  - kompetenz
```

#### Hausverwaltung

```yaml
gmb_review_themen:
  - erreichbarkeit
  - reaktionszeit
  - transparenz
  - abrechnung
  - hausmeister
  - reparaturen
  - kommunikation
```

#### Werkstatt / KFZ

```yaml
gmb_review_themen:
  - reparatur_qualitaet
  - preis_transparenz
  - termin_treue
  - kommunikation
  - sauberkeit
  - ersatzteile
  - wartezeit
```

#### Hotel / Hospitality

```yaml
gmb_review_themen:
  - sauberkeit
  - service
  - zimmer
  - fruehstueck
  - lage
  - preis_leistung
  - personal
  - lautstaerke
```

#### Friseur / Beauty

```yaml
gmb_review_themen:
  - beratung
  - qualitaet
  - preise
  - wartezeit
  - sauberkeit
  - freundlichkeit
  - terminverfuegbarkeit
```

#### Fitness / Studio

```yaml
gmb_review_themen:
  - geraete
  - sauberkeit
  - trainer
  - kurse
  - oeffnungszeiten
  - preise
  - parkplatz
```

#### Fallback (Branche nicht in Default-Liste)

```yaml
gmb_review_themen:
  - service
  - qualitaet
  - preis_leistung
  - erreichbarkeit
  - freundlichkeit
  - termin_treue
```

Mit Hinweis im Schema-Body: "Branche `XYZ` ist nicht in den Default-Themen — generischer Themen-Set genutzt, bitte branchen-spezifisch ergänzen."

---

## Skip-Logik-Status

Wenn der Skill in Phase A Skip-Kandidat erkennt UND kein Override gesetzt ist, wird das Schema mit folgendem Mini-Format geschrieben:

```yaml
---
skill: 03-16-local-gmb-und-seo
status: skip_national_online
generiert_am: ...
basis: [meta.json, data/kunde.md, wettbewerber/identifikation-schema.md]
begruendung:
  region_definition: national
  gmb_touchpoint_kunde: nicht_vorhanden
  regionale_wettbewerber_in_liste: 0
override_argument: trotzdem laufen
---

# Local-SEO-Audit · KUNDE — geskippt

Kein Local-Bezug erkannt. Begründung:
- Region-Definition aus wettbewerber/identifikation-schema.md: national
- data/kunde.md.touchpoints_gefunden enthält keinen GMB-Link
- wettbewerber/liste.md enthält keine Kategorie regional

Wenn das falsch ist (Kunde hat doch Filialen oder lokales Service-Gebiet), Skill mit Argument "trotzdem laufen" erneut aufrufen. Der Skip-Status wird dann ignoriert, Phase A läuft normal.
```

---

## Validierung in Phase B

Beim Phase-B-Start prüft der Skill:

1. `status: bestaetigt`? Sonst Abbruch.
2. `standorte_kunde` mindestens 1 Eintrag, jeder mit `stadt` und entweder `adresse` oder `service_area: true`
3. `suchradius_km` numerisch, 5 ≤ x ≤ 100
4. `local_pack_keywords` mindestens 3 Basis-Keywords mit jeweils mindestens 1 Modifier-Typ
5. `gmb_review_themen` mindestens 3 Einträge
6. `nap_cross_check_quellen` mindestens `gmb` enthalten

Bei Fehler: konkreter Hinweis, welches Feld fehlt oder falsch ist.
