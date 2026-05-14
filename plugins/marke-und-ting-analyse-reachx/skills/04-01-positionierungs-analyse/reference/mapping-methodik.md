# Mapping-Methodik

Berechnungs-Logik für die Achsen-Werte pro Akteur und für die Cluster-Erkennung. Phase B des `04-01-positionierungs-analyse`-Skills nutzt dieses Dokument als Single-Source-of-Truth.

Grundprinzip: **Reproduzierbarkeit**. Bei gleichem Input und gleichem Schema muss der gleiche (x, y)-Wert pro Akteur entstehen. Keine Zufallselemente, keine LLM-Bewertung in Phase B (das ist Aufgabe der Marken-Profile in Stufe 2).

## 1. Direkte Tonalitäts-Achsen

Vier Achsen aus den Marken-Profilen (`tonalitaet.*.achse_wert`), Skala -2 bis +2:

| Achse | Marken-Profil-Feld | Pol negativ | Pol positiv |
|---|---|---|---|
| formell-informell | `tonalitaet.formell_vs_informell.achse_wert` | formell | informell |
| expertise-partnerschaftlich | `tonalitaet.expertise_vs_partnerschaftlich.achse_wert` | expertise-zentriert | partnerschaftlich |
| sachlich-emotional | `tonalitaet.sachlich_vs_emotional.achse_wert` | sachlich | emotional |
| modern-traditionell | `tonalitaet.modern_vs_traditionell.achse_wert` | modern | traditionell |

### Werte-Abbildung

```
wert_im_marken_profil  →  achsen_wert_im_mapping
-2                     →  -2.0
-1                     →  -1.0
 0                     →   0.0
+1                     →  +1.0
+2                     →  +2.0
null                   →  Fallback (siehe Konfidenz-Logik)
```

### Konfidenz-Logik

- `achse_wert` numerisch (-2, -1, 0, +1, +2): Konfidenz `hoch`
- `achse_wert: null` UND akteur ist Reduced-Mode (kein Crawl möglich): Konfidenz `niedrig`, Wert `0.0` als Fallback
- `achse_wert: null` UND Profil ist Standard-Mode: Konfidenz `mittel`, Wert `0.0` als Fallback (oft fehlen einfach Belege)

Im Output-CSV wird die Konfidenz pro Achse separat geführt (`konfidenz_x`, `konfidenz_y`).

## 2. USP-Differenzierungs-Achse (Preis-Fokus ↔ Premium-Fokus)

Aus `usps_wie_kommuniziert` pro Akteur berechnet.

### Token-Listen

**Preis-Token** (Treffer reduzieren Wert):

```
preis, günstig, sparen, sparsam, niedrig, low-cost, budget, erschwinglich,
preiswert, fair, transparent, transparente preise, ohne aufpreis, kostenlos,
gratis, rabatt, deal, angebot, schnäppchen, bezahlbar
```

**Premium-Token** (Treffer erhöhen Wert):

```
premium, exzellenz, exklusiv, hochwertig, qualität, qualitativ, luxus,
luxuriös, edel, manufaktur, handgefertigt, meister, perfektion, präzision,
top, spitzen, beste, besten, profi, professionell, individuell, maßgeschneidert
```

### Berechnungs-Formel

```
fuer jeden USP in usps_wie_kommuniziert:
    text = usp.usp + " " + usp.beleg
    preis_hits += anzahl Token aus Preis-Liste in text (case-insensitive, Token-Boundary)
    premium_hits += anzahl Token aus Premium-Liste in text

gesamt_hits = preis_hits + premium_hits

wenn gesamt_hits == 0:
    achsen_wert = 0.0
    konfidenz = niedrig
sonst:
    rohscore = (premium_hits - preis_hits) / gesamt_hits
    achsen_wert = rohscore * 2.0  # auf [-2, +2] skalieren
    achsen_wert = max(-2.0, min(2.0, achsen_wert))
    konfidenz = hoch wenn gesamt_hits >= 3 sonst mittel
```

### Edge Cases

- Wenn USPs leer (Profil hatte keine extrahiert): `achsen_wert = 0.0`, `konfidenz = niedrig`
- Token-Match ist Substring-basiert mit Wort-Grenzen (z. B. "Premium" matched, "premiumpreis" matched auch — das ist gewollt)

## 3. Zielgruppen-Breiten-Achse (Spezialist ↔ Generalist)

Aus `zielgruppen_hypothese_aus_website` und `portfolio_wie_kommuniziert` pro Akteur.

### Eingangs-Werte

```
persona_anzahl = len(zielgruppen_hypothese_aus_website)
kategorie_anzahl = len(set([item.kategorie for item in portfolio_wie_kommuniziert]))
```

### Mapping-Tabelle

| persona_anzahl + kategorie_anzahl | achsen_wert | Bedeutung |
|---|---|---|
| 1-2 | -2.0 | Stark spezialisiert |
| 3 | -1.0 | Eher spezialisiert |
| 4-5 | 0.0 | Mid-Bereich |
| 6-7 | +1.0 | Eher breit |
| ≥ 8 | +2.0 | Stark generalistisch |

### Konfidenz

- Beide Listen vorhanden mit Inhalten: `hoch`
- Eine Liste leer: `mittel`
- Beide Listen leer: `niedrig`, Wert `0.0`

## 4. Funnel-Fokus-Achse (Awareness ↔ Decision)

Aus `audits/seo-keyword-cluster.csv` pro Akteur (nur Kunde und WBs mit Ranking-Daten).

### Eingangs-Werte

Pro Akteur die in der CSV vorhandenen Ranking-Positionen lesen:

- `tofu_anteil` = (Anzahl Keywords mit `funnel_stufe: TOFU` und Akteur im Top-10) / (Anzahl Keywords mit Akteur im Top-10)
- `bofu_anteil` = (Anzahl Keywords mit `funnel_stufe: BOFU` und Akteur im Top-10) / (Anzahl Keywords mit Akteur im Top-10)

### Berechnungs-Formel

```
spread = bofu_anteil - tofu_anteil  # negativ = TOFU-lastig (Awareness), positiv = BOFU-lastig (Decision)
achsen_wert = spread * 4.0          # auf [-2, +2] skalieren (max möglicher Spread ist 1.0)
achsen_wert = max(-2.0, min(2.0, achsen_wert))
```

### Konfidenz

- Akteur hat ≥ 20 Keywords in der CSV mit Top-10-Ranking: `hoch`
- 5-19 Keywords: `mittel`
- < 5 oder keine Daten: `niedrig`, Wert `0.0`

### Hinweis

Diese Achse braucht `audits/seo-keyword-cluster.csv`. Wenn die nicht existiert: Skill bricht in Phase B mit Hinweis ab.

## 5. Kommunikations-Klarheits-Achse (unklar ↔ klar)

Aus `hero_test.gesamt_score` und `verstaendlichkeit_startseite.score` pro Akteur.

### Berechnungs-Formel

```
ist beide vorhanden:
    durchschnitt = (hero_test.gesamt_score + verstaendlichkeit_startseite.score) / 2
    # Mapping von [1, 5] auf [-2, +2]:
    achsen_wert = ((durchschnitt - 1) / 4) * 4 - 2
    achsen_wert = max(-2.0, min(2.0, achsen_wert))
    konfidenz = hoch

ist nur eine vorhanden:
    durchschnitt = der vorhandene Wert
    achsen_wert wie oben
    konfidenz = mittel

ist keine vorhanden:
    achsen_wert = 0.0
    konfidenz = niedrig
```

### Beispiel

- Hero-Test 4.0 + Verständlichkeit 3.0 = Durchschnitt 3.5 → `achsen_wert = ((3.5 - 1) / 4) * 4 - 2 = 0.5`
- Hero-Test 5.0 + Verständlichkeit 5.0 = Durchschnitt 5.0 → `achsen_wert = +2.0`
- Hero-Test 1.0 + Verständlichkeit 1.0 = Durchschnitt 1.0 → `achsen_wert = -2.0`

## 6. Cluster-Erkennungs-Algorithmus

Distanz-basierte Clusterung im 2D-Raum, deterministisch reproduzierbar.

### Schritt-für-Schritt

```
eingabe:
  akteure = Liste von (slug, x, y)
  cluster_radius = Schwelle aus Schema (Default 1.0)
  mindestgroesse_cluster = Schwelle aus Schema (Default 2)

algorithmus:
  1. Berechne paarweise euklidische Distanz:
     distanz(a, b) = sqrt((a.x - b.x)^2 + (a.y - b.y)^2)
  2. Baue Nachbarschafts-Graph:
     fuer jedes Paar (a, b): wenn distanz(a, b) <= cluster_radius: a und b sind verbunden
  3. Finde Zusammenhangs-Komponenten (transitive Hülle):
     fuer jeden Akteur: starte BFS/DFS ueber den Graphen, sammle alle erreichbaren Akteure
  4. Filtere Komponenten mit Groesse >= mindestgroesse_cluster - das sind die Markt-Cluster
  5. Akteure, die in keinem so gefilterten Cluster sind, sind Solitäre
  6. Pro Cluster: berechne Mittelpunkt als Schwerpunkt (arithmetisches Mittel der x- und y-Werte)
```

### Beispiel

3 Akteure: A(1.0, 1.0), B(1.5, 0.8), C(-1.0, -1.0)

- distanz(A, B) = sqrt(0.5^2 + 0.2^2) = sqrt(0.29) ≈ 0.54
- distanz(A, C) = sqrt(2.0^2 + 2.0^2) ≈ 2.83
- distanz(B, C) = sqrt(2.5^2 + 1.8^2) ≈ 3.08

Mit cluster_radius = 1.0: A und B sind nah, C ist allein. Cluster {A, B} mit Mittelpunkt (1.25, 0.9), C ist Solitär.

### Sonderfall: Kunde immer eigenstaendig

Wenn `kunde_immer_eigenstaendig: true` im Schema: Kunde wird aus dem Graph entfernt vor Schritt 3, ist immer Solitär — auch wenn er räumlich nah an WBs liegt. Im Output entsprechend markiert.

## 7. Quadranten-Zuordnung

Pro Akteur Quadrant ermitteln:

```
wenn x >= 0 und y >= 0: Q1 (oben-rechts)
wenn x <  0 und y >= 0: Q2 (oben-links)
wenn x <  0 und y <  0: Q3 (unten-links)
wenn x >= 0 und y <  0: Q4 (unten-rechts)
```

Achsen-Beschriftungen aus dem Schema werden in die Quadranten-Namen übersetzt, z. B. bei X = formell↔informell und Y = expertise↔partnerschaftlich:

- Q1 = "informell + partnerschaftlich"
- Q2 = "formell + partnerschaftlich"
- Q3 = "formell + expertise"
- Q4 = "informell + expertise"

## 8. White-Space-Erkennung

Pro Quadrant:

```
akteure_im_quadrant = [akteur for akteur in alle_akteure if akteur.quadrant == Q]
wenn len(akteure_im_quadrant) == 0:
    quadrant ist White-Space
wenn len(akteure_im_quadrant) == 1 und akteur ist Kunde:
    kunde_alleinstellung
wenn len(akteure_im_quadrant) >= 4:
    quadrant ist Markt-Verdichtung
```

White-Space-Quadrant wird gegen die Differenzierungs-Hypothese aus dem Schema abgeglichen — der Quadrant, der die Hypothese am besten erfüllt, ist `whitespace_empfohlen`.

## 9. Tonale Homogenität der Branche

```
wenn >= 75% aller Akteure in 1 Quadrant ODER >= 90% in 2 Quadranten:
    auffaelligkeit: tonale_homogenitaet_branche
```

Branche ist auf den gewählten Achsen homogen — Differenzierung über Achsen-Wechsel sinnvoller als über Achsen-Position-Verschiebung.

## 10. Bewegungs-Empfehlung berechnen

Aus Differenzierungs-Hypothese (Schema) + Kunden-Position + White-Space-Analyse:

```
schritt 1: hypothese_richtung aus schema lesen (z. B. "weg von expertise, hin zu partnerschaftlich")
schritt 2: aus richtung die ziel-quadranten ableiten
schritt 3: pro ziel-quadrant pruefen:
    - ist quadrant white-space? (gut)
    - ist quadrant markt-cluster? (eher schlecht)
    - liegt quadrant in der hypothese-richtung? (pflicht)
schritt 4: ziel-position innerhalb des besten ziel-quadrants:
    - mittelpunkt des quadranten (1.0, 1.0) oder (-1.0, 1.0) etc.
    - oder spezifischer Punkt, der maximal weit weg vom dominantesten Markt-Cluster liegt
schritt 5: bewegungs-vektor: (ziel.x - kunde.x, ziel.y - kunde.y)
schritt 6: aufwand schaetzen:
    - distanz < 1.0: aufwand niedrig (kommunikative Anpassungen reichen)
    - distanz 1.0-2.0: aufwand mittel (umfassendere Re-Positionierung)
    - distanz > 2.0: aufwand hoch (Marken-Identität-Anpassung)
```

Hebel-Liste (konkrete Maßnahmen pro Achsen-Bewegung) wird aus Mapping-Tabellen in `reference/positionierung-output-schema.md` abgeleitet — pro Achse und Bewegungs-Richtung typische Hebel.

## 11. Datenqualitäts-Indikatoren

Pro Mapping-Lauf werden folgende Metriken berechnet und im Output dokumentiert:

```
konfidenz_summary:
  akteure_hoch_konfidenz: N    # beide Achsen-Werte hoch
  akteure_mittel_konfidenz: M
  akteure_niedrig_konfidenz: K
  niedrig_konfidenz_pflicht_hinweis: K > 0.3 * gesamt_akteure
```

Wenn mehr als 30% der Akteure niedrige Konfidenz haben: Auffälligkeit `konfidenz_unsicher` wird ausgegeben, Mapping wird im Output explizit als "Grob-Mapping" gekennzeichnet.
