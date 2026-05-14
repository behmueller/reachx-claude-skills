# Methodik: Hero-Test, Tonalität, Verständlichkeit

Drei Dimensionen, die der Skill für jede Marken-Analyse anwendet. Die Methodik ist **identisch für Kunde und Wettbewerber** — damit `04-01-positionierungs-analyse` später Side-by-Side vergleichen kann.

## 1. Hero-Test (Donald-Miller-Methodik)

Der 5-Sekunden-Test: Was erkennt ein Erstbesucher auf der Startseite in den ersten 5 Sekunden? Vier Fragen, jeweils 1–5 bewertet.

### Die vier Fragen

**1. Was wird angeboten?**

Erkennt der Besucher klar, *was* die Marke verkauft / anbietet? Konkret: Produkt-Kategorie, Service-Typ, Branche.

| Score | Bedeutung |
|---|---|
| 5 | Sofort klar — Hero-Headline benennt das Angebot direkt |
| 4 | Klar nach 1–2 Sekunden — leichte Interpretation nötig |
| 3 | Erkennbar, aber unscharf — "irgendwas mit Handwerk"-Niveau |
| 2 | Nur durch Lesen mehrerer Sektionen erkennbar |
| 1 | Nicht erkennbar — Hero zeigt nur Bilder, abstrakte Statements |

**2. Für wen?**

Erkennt der Besucher, ob er zur Zielgruppe gehört? Konkret: B2B vs. B2C, Branche, Rolle, Anwendungsfall.

| Score | Bedeutung |
|---|---|
| 5 | Sehr klar — direkte Ansprache der Zielgruppe ("Für Hausverwalter, die …") |
| 4 | Klar aus Kontext, Branche genannt |
| 3 | Aus den Beispielen / Bildern erkennbar |
| 2 | Nur indirekt aus den Inhalten erschließbar |
| 1 | Unklar — könnte jeder sein |

**3. Was ist anders / besser?**

Erkennt der Besucher die Differenzierung zur Konkurrenz?

| Score | Bedeutung |
|---|---|
| 5 | Eindeutige Differenzierung mit Beleg ("Einzige Lösung, die …") |
| 4 | Klares USP-Statement ohne Beleg ("Schneller, günstiger, besser") |
| 3 | Allgemeine Qualitätsversprechen ("Hochwertig", "Persönlich") |
| 2 | Nur Selbst-Lob ohne Substanz |
| 1 | Keine erkennbare Differenzierung |

**4. Wie weiter? (Call-to-Action)**

Ist ein klarer, hervorgehobener nächster Schritt erkennbar?

| Score | Bedeutung |
|---|---|
| 5 | Primärer CTA prominent, beschriftet mit der konkreten Aktion ("Jetzt Termin buchen") |
| 4 | CTA klar, aber generisch beschriftet ("Mehr erfahren") |
| 3 | CTA vorhanden, aber visuell nicht hervorgehoben |
| 2 | Mehrere Optionen, keine klare Hierarchie |
| 1 | Kein CTA erkennbar |

### Bewertungs-Ablauf

1. **Screenshot der Startseite** in Standard-Desktop-Größe (1440×900) erzeugen — via Apify-Actor oder anderem Headless-Tool
2. **Vision-Modell befragen** mit den vier Fragen einzeln, jeweils Score + Begründung + geschätzter Sichtbarkeitszeit anfordern
3. **Mobile-Variante optional** (375×812): wenn Mobile-Anteil bei der Zielgruppe wahrscheinlich hoch ist (B2C, Local Services), zusätzlich bewerten

### `gesamt_score`

Mittelwert der vier Einzel-Scores. Im Body **immer benennen, welche Frage durchgefallen ist** — der Mittelwert allein ist für den Strategen wenig wertvoll. Beispiel:

> Gesamt 3,25 / 5 — solide, aber **"Was ist anders?" fällt mit 1 durch**: keine Differenzierung erkennbar. Die anderen drei Dimensionen sind ok bis gut.

## 2. Tonalitäts-Analyse (Vier Achsen)

Auf jeder Achse Skala von -2 bis +2 setzen, jeweils mit 2–3 Zitat-Belegen aus dem Crawl.

### Achse 1: Formell ↔ Informell

Indikatoren:

- **Sie/Du**: dominiert eine Form, oder Mischung?
- **Sprachregister**: Schriftdeutsch vs. Umgangssprache
- **Fachjargon-Dichte**: hohe Dichte = formell; niedrige Dichte = informell
- **Satzbau**: lange Sätze mit Nominalisierungen = formell; kurze Sätze = informell

| Wert | Position |
|---|---|
| -2 | sehr formell (Bank, Anwalt, Konzern) |
| -1 | eher formell (B2B-Mittelstand) |
| 0 | situativ gemischt |
| +1 | eher informell (Du-Anrede, lockerer Ton) |
| +2 | sehr informell (Slang, persönliche Anekdoten) |

### Achse 2: Expertise-zentriert ↔ Partnerschaftlich

Indikatoren:

- **Pronomen-Verwendung**: "Wir" mit Daten = expertise-zentriert; "Wir gemeinsam mit Ihnen" = partnerschaftlich
- **Ego-Statements**: "Wir sind führend, weil …" vs. "Lass uns zusammen herausfinden …"
- **Story-Position**: Marke als Held vs. Marke als Guide für den Kunden-Helden

| Wert | Position |
|---|---|
| -2 | stark expertise-zentriert (viele Awards, Zertifikate, Top-Liste-Listen prominent) |
| -1 | überwiegend Experten-Auftritt |
| 0 | gemischt |
| +1 | überwiegend partnerschaftlich |
| +2 | konsequent kunden-zentriert ("Sie sind der Held, wir helfen") |

### Achse 3: Sachlich ↔ Emotional

Indikatoren:

- **Bildsprache**: Funktional vs. emotional aufgeladen
- **Adjektive**: messbar vs. wertend
- **Story vs. Spezifikation**: Anwendungsgeschichten vs. Feature-Listen

| Wert | Position |
|---|---|
| -2 | rein sachlich (Tech, Industrie, B2B-Software) |
| -1 | eher sachlich |
| 0 | gemischt |
| +1 | eher emotional |
| +2 | stark emotional (Lifestyle, Storytelling dominiert) |

### Achse 4: Modern ↔ Traditionell

Indikatoren:

- **Sprachstil**: zeitgemäß / Buzz-Wörter vs. etabliertes Vokabular
- **Themen-Anbindung**: aktuelle Trends vs. zeitlose Themen
- **Visuelle Sprache**: minimalistisch vs. klassisch
- **Branchen-Konventionen**: Bricht die Marke mit Branchen-Konventionen oder erfüllt sie?

| Wert | Position |
|---|---|
| -2 | stark modern (Startup-Sprache, Trends-getrieben) |
| -1 | eher modern |
| 0 | zeitlos / gemischt |
| +1 | eher traditionell |
| +2 | stark traditionell (Erbe, Geschichte, Beständigkeit dominant) |

### Belege

Jede Achse braucht **2–3 konkrete Zitate** als Belege. Wenn keine Belege auffindbar (z. B. weil die Website sehr inhaltsarm ist), Achse mit `null` markieren und in `crawl_luecken` notieren.

## 3. Verständlichkeit der Startseite

Eigene Dimension, getrennt vom Hero-Test. Bewertung 1–5.

### Bewertungs-Kriterien

| Kriterium | Was geprüft wird |
|---|---|
| Informations-Hierarchie | Wichtigstes oben, Sekundäres unten? Klare Sektionierung? |
| Fachsprache | Angemessen für die Zielgruppe? Erklärungen wo nötig? |
| Text-Verständlichkeit | Kurze Sätze, klare Absätze, keine Wortmonster |
| Visuelle Klarheit | Genug Whitespace, ausreichende Schriftgröße, klare Kontraste |
| CTA-Erkennbarkeit | Sind Aktions-Buttons als solche erkennbar? Klare Hierarchie? |

### Score-Vergabe

| Score | Bedeutung |
|---|---|
| 5 | Sehr verständlich — Erstbesucher findet sich sofort zurecht |
| 4 | Gut verständlich — kleine Verbesserungen möglich |
| 3 | Verständlich, aber mit Reibung — z. B. Fachsprache zu hoch, oder unklare Hierarchie |
| 2 | Schwer verständlich — Erstbesucher braucht 30+ Sekunden zum Sortieren |
| 1 | Verwirrend — Erstbesucher steigt aus |

### Output

`schwachstellen`-Liste mit konkreten Findings und Quote-Belegen, `staerken`-Liste analog. Beispiel:

```yaml
verstaendlichkeit_startseite:
  score: 3
  schwachstellen:
    - "Hero-Text 'Wir gestalten Ihre digitale Transformation' ist abstrakt — keine konkrete Aktion erkennbar"
    - "Drei CTAs nebeneinander mit gleicher Optik — keine klare Hierarchie"
    - "Fachbegriffe wie 'omnichannel' ohne Erklärung in der ersten Sektion"
  staerken:
    - "Klare Sektionierung mit großem Whitespace"
    - "Lesbare Typografie, gut skalierbar auf Mobile"
```
