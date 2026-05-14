# Achsen-Template (Phase-A-Output-Format)

Dieses Template definiert das Format für `synthese/positionierung-schema.md` (Phase-A-Output). Default-Achsen-Kombinationen sind pro Branchen-Typ vorgegeben.

## Vollständiges Schema-Datei-Format

```markdown
---
skill: 04-01-positionierungs-analyse
status: vorgeschlagen
basis:
  - data/kunde.md
  - wettbewerber/liste.md
  - wettbewerber/SLUG.md (pro Wettbewerber)
  - data/briefing.md (optional)
  - data/abweichungen.md (optional)
  - audits/seo-keyword-cluster.csv (optional)
generiert_am: ISO-8601
schema_version: "1.0"

# === Akteurs-Inventur ===
akteure_inventur:
  kunde:
    slug: KUNDE_SLUG
    name: KUNDE_NAME
    quelle: data/kunde.md
    daten_vollstaendig: true
  wettbewerber_zu_profilieren:
    - slug: WB_SLUG_1
      name: WB_NAME_1
      quelle: wettbewerber/WB_SLUG_1.md
      daten_vollstaendig: true
  wettbewerber_best_practice:
    - slug: WB_SLUG_2
      name: WB_NAME_2
      quelle: wettbewerber/WB_SLUG_2.md
      daten_vollstaendig: true
  fehlende_daten:
    - akteur: WB_SLUG_3
      grund: "Tonalitäts-Achsen 1 und 2 sind null - Profil nur Reduced-Mode"
  akteure_im_mapping_gesamt: N

# === Achsen-Vorschlag ===
achsen_vorschlag:
  default:
    x_achse:
      label: "formell ↔ informell"
      pol_negativ: formell
      pol_positiv: informell
      skala: "[-2, +2]"
      quelle_feld: tonalitaet.formell_vs_informell.achse_wert
      begruendung: "Tonalitäts-Achse 1 direkt aus Marken-Profil verfügbar, in fast jeder Branche differenzierungs-relevant"
    y_achse:
      label: "expertise-zentriert ↔ partnerschaftlich"
      pol_negativ: expertise-zentriert
      pol_positiv: partnerschaftlich
      skala: "[-2, +2]"
      quelle_feld: tonalitaet.expertise_vs_partnerschaftlich.achse_wert
      begruendung: "Tonalitäts-Achse 2 - Story-Position der Marke (Held vs. Guide), strategisch besonders aussagekräftig"
  alternativen:
    - id: alt_1
      x_achse:
        label: "sachlich ↔ emotional"
        quelle_feld: tonalitaet.sachlich_vs_emotional.achse_wert
      y_achse:
        label: "modern ↔ traditionell"
        quelle_feld: tonalitaet.modern_vs_traditionell.achse_wert
      branche_eignung: "B2C, Lifestyle, Handel - wenn Emotion und Generations-Wechsel im Fokus stehen"
    - id: alt_2
      x_achse:
        label: "Preis-Fokus ↔ Premium-Fokus"
        quelle_feld: usps_wie_kommuniziert (Token-Klassifikation)
      y_achse:
        label: "Spezialist ↔ Generalist"
        quelle_feld: zielgruppen_hypothese + portfolio_breite
      branche_eignung: "B2B-Mittelstand, Services - wenn Marktposition und Fokus-Frage zentral sind"
    - id: alt_3
      x_achse:
        label: "Awareness ↔ Decision (Funnel-Fokus)"
        quelle_feld: audits/seo-keyword-cluster.csv (TOFU/BOFU-Anteil)
      y_achse:
        label: "Kommunikations-Klarheit unklar ↔ klar"
        quelle_feld: hero_test.gesamt_score + verstaendlichkeit_startseite.score
      branche_eignung: "Wenn SEO-Cluster vorhanden ist und Funnel-Differenzierung strategisch relevant"

# === Cluster-Erkennungs-Schwellwerte ===
cluster_schwellwerte:
  cluster_radius: 1.0
  mindestgroesse_cluster: 2
  kunde_immer_eigenstaendig: false

# === Differenzierungs-Hypothese ===
differenzierungs_hypothese:
  richtung: "z.B. weg von expertise-zentriert hin zu partnerschaftlich + informell"
  begruendung: "Briefing nennt 'auf Augenhöhe mit Kunden' als Selbstbild, Website kommuniziert aber stark Awards. Im Mapping wäre der Quadrant rechts oben leer."
  konfidenz: hoch
  quelle_inputs:
    - data/briefing.md (Strategie-Intention)
    - data/abweichungen.md (Selbstbild vs. Außenwahrnehmung)
---

# Schema für 04-01-positionierungs-analyse

## 1. Akteurs-Inventur

(Body-Sektion: Welche Akteure sind im Mapping drin, welche fehlen, welche Daten-Lücken bestehen)

## 2. Achsen-Vorschlag

### Standard-Vorschlag (empfohlen)

X-Achse: formell ↔ informell
Y-Achse: expertise-zentriert ↔ partnerschaftlich

Begründung: ...

### Alternativen

(siehe Frontmatter)

## 3. Cluster-Schwellwerte

cluster_radius: 1.0 (anpassbar)
mindestgroesse_cluster: 2

## 4. Differenzierungs-Hypothese

(Body-Text mit Begründung)

## 5. Strategen-Review

Bitte prüfen:

- [ ] Achsen-Kombination: Default belassen oder Alternative wählen?
- [ ] Akteurs-Auswahl: WBs reduzieren oder ergänzen?
- [ ] Cluster-Radius: 1.0 passend oder anpassen?
- [ ] Differenzierungs-Hypothese: bestätigt oder anders ausrichten?

Nach Review: `status: bestaetigt` setzen und Skill erneut aufrufen.
```

## Default-Achsen-Kombinationen pro Branchen-Typ

Die Achsen-Vorschläge werden anhand des in `wettbewerber/identifikation-schema.md` definierten `branchen_typ` priorisiert.

### B2B-Mittelstand (Maschinenbau, Industrie-Dienstleister, Industrie-SaaS)

- **Default**: formell ↔ informell × expertise ↔ partnerschaftlich
- **Alternative 1**: Spezialist ↔ Generalist × Preis-Fokus ↔ Premium-Fokus
- **Alternative 2**: modern ↔ traditionell × Kommunikations-Klarheit
- Begründung: B2B-Mittelstand neigt zu formell + expertise, Differenzierung oft über Tonalitäts-Wechsel oder Fokus-Schärfung

### B2C-E-Commerce

- **Default**: sachlich ↔ emotional × modern ↔ traditionell
- **Alternative 1**: Preis-Fokus ↔ Premium-Fokus × Spezialist ↔ Generalist
- **Alternative 2**: formell ↔ informell × expertise ↔ partnerschaftlich
- Begründung: B2C lebt von Emotion und Zeitgeist; Preis/Premium ist die zweite Strategie-Achse

### Lokal-Dienstleister (Handwerk, Gastronomie, Praxis)

- **Default**: formell ↔ informell × expertise ↔ partnerschaftlich
- **Alternative 1**: modern ↔ traditionell × Spezialist ↔ Generalist
- **Alternative 2**: sachlich ↔ emotional × Kommunikations-Klarheit
- Begründung: Lokal-Anbieter differenzieren oft über Auftreten (Sie/Du, persönlich vs. professionell)

### B2B-SaaS

- **Default**: expertise ↔ partnerschaftlich × Funnel-Fokus (Awareness ↔ Decision)
- **Alternative 1**: formell ↔ informell × Spezialist ↔ Generalist
- **Alternative 2**: Preis ↔ Premium × Kommunikations-Klarheit
- Begründung: SaaS-Markt ist tonal homogen; Funnel-Fokus ist starke Differenzierungs-Achse (Content vs. Demo-Push)

### Content-Publisher (Medien, Verlag, Plattform)

- **Default**: sachlich ↔ emotional × Spezialist ↔ Generalist
- **Alternative 1**: formell ↔ informell × modern ↔ traditionell
- **Alternative 2**: expertise ↔ partnerschaftlich × Funnel-Fokus
- Begründung: Publisher leben von Themen-Fokus und Tonalitäts-Persona

### Fallback (Branche unklar / Mischform)

- **Default**: formell ↔ informell × expertise ↔ partnerschaftlich (sicherste, breit anwendbare Kombination)
- Alle anderen als Alternativen

## Achsen-Definitions-Pflichtfelder

Jede Achse (Default oder Alternative) muss im Schema enthalten:

1. `label`: Anzeige-Beschriftung (z. B. "formell ↔ informell")
2. `pol_negativ` und `pol_positiv`: Namen der beiden Pole
3. `skala`: numerischer Bereich (Standard: [-2, +2])
4. `quelle_feld`: aus welchem Marken-Profil-Feld oder Audit-Feld der Wert berechnet wird
5. `begruendung`: warum diese Achse für diesen Kunden relevant ist (1-2 Sätze)

Bei abgeleiteten Achsen zusätzlich:

- `berechnungs_logik`: Token-Listen, Score-Formeln, Mapping-Regeln (Verweis auf `mapping-methodik.md` Abschnitt)

## Pflicht-Hinweise im Schema-Body

- **Achsen-Wahl prägt die ganze MTA-Story** — Stratege muss bewusst entscheiden
- **Bei Branchen-Default ist der Vorschlag empfohlen, aber nicht zwingend** — Strategen-Bauchgefühl darf gewinnen
- **Achsen mit fehlenden Daten** (z. B. Tonalitäts-Wert `null` bei mehreren Akteuren) explizit markieren — diese Achsen können nicht ohne Workaround genutzt werden
