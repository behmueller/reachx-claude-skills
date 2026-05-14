# Abweichungen-Leitfaden: Briefing vs. Website

Wenn der Kunde im Kickoff etwas anderes erzählt als die Website kommuniziert, ist das **eine der wertvollsten Erkenntnisse der MTA**. Der Stratege kann später daraus konkrete Empfehlungen ableiten: "Eure Website sagt X, ihr meint Y — das müssen wir anpassen."

Dieser Skill schreibt diese Diskrepanzen in eine eigene Datei `data/abweichungen.md`, **getrennt** vom `kunde.md` — damit der Stratege das Thema gezielt als eigenständige Erkenntnis kommunizieren kann.

## Wann diese Datei erstellt wird

Nur wenn `data/briefing.md` im Projekt-Ordner existiert. Wenn der `01-02-kickoff-transcript-parser` noch nicht gelaufen ist, wird `abweichungen.md` übersprungen und im Skill-Schluss-Format ein Hinweis ausgegeben.

## Felder, die verglichen werden

| Feld in `briefing.md` | Feld in `kunde.md` | Was wir suchen |
|---|---|---|
| `produkte_dienstleistungen` | `portfolio_wie_kommuniziert` | Wird *alles*, was der Kunde verkauft, auch auf der Website klar sichtbar? Werden manche Produkte ausgelassen oder vergraben? |
| `usps_kunde_eigenwahrnehmung` | `usps_wie_kommuniziert` | Findet sich jeder USP, den der Kunde mündlich nennt, auf der Website wieder? Wenn nicht: warum? |
| `zielgruppen` | `zielgruppen_hypothese_aus_website` | Spricht die Website die im Briefing genannte Zielgruppe an, oder eine andere? |
| `tools_des_kunden` | `touchpoints_gefunden` | Hat der Kunde Tools/Profile erwähnt, die auf der Website verlinkt sein sollten, aber nicht sind (LinkedIn, GMB, etc.)? |
| (Tonalitäts-Wunsch falls im Briefing erwähnt) | `tonalitaet` | Wenn der Kunde sagt "wir wollen modern wirken", aber die Tonalität ist `+2 traditionell` — Lücke |

## Klassifikation der Abweichungen

Für jede gefundene Diskrepanz: einer von vier Typen.

### Typ A: USP-Lücke

Etwas, das der Kunde mündlich als USP nennt, ist auf der Website **nicht** kommuniziert.

**Beispiel:** Briefing sagt "Wir sind die einzigen mit einer Kabel-Datenbank von tausenden Kabeln" → auf der Aufmaster-Website findet sich kein Hinweis darauf. ➜ **Lücke** mit hoher Priorität, weil USP ungenutzt.

### Typ B: USP-Inkonsistenz

Etwas, das der Kunde als USP nennt, wird auf der Website **schwächer oder anders** kommuniziert.

**Beispiel:** Briefing: "Premium-Qualität als Differenzierung gegen asiatische Billig-Anbieter" → Website spricht stattdessen über "günstige Preise". ➜ **Inkonsistenz** mit Strategie-Implikation.

### Typ C: Portfolio-Diskrepanz

Etwas, das auf der Website prominent ist, kam im Briefing nicht vor — oder umgekehrt.

**Beispiel:** Website wirbt prominent mit "Versicherungen", Briefing erwähnt nur "Bank". ➜ **Klärung nötig**: ist das ein Nebengeschäft, oder eine strategische Säule?

### Typ D: Zielgruppen-Mismatch

Die Website spricht eine andere Zielgruppe an als die im Briefing benannte primäre.

**Beispiel:** Briefing: "Hauptzielgruppe sind kleine Handwerksbetriebe" → Website spricht in Sprache und Bildwelt Enterprise-Kunden an. ➜ **Strukturelles Problem** — Website-Re-Design auf der Roadmap.

## Output-Format

Datei: `data/abweichungen.md`

```markdown
---
skill: 02-01-kunden-marken-profil
generiert_am: <ISO-8601>
schema_version: "1.0"
basis:
  briefing: data/briefing.md
  kunde: data/kunde.md
anzahl_abweichungen: <int>
abweichungs_dichte: <hoch | mittel | niedrig | keine>
priorisierte_abweichungen:
  - typ: <A | B | C | D>
    titel: <kurze Beschreibung>
    prioritaet: <hoch | mittel | niedrig>
---

# Abweichungen: Briefing vs. Website

## Übersicht

Kurz-Zusammenfassung: wie viele Diskrepanzen gefunden, welche Typ-Verteilung, wo die wichtigsten Hebel liegen.

## Typ A — USP-Lücken (Briefing nennt, Website ignoriert)

### <USP-Titel>

- **Im Briefing:** <Aussage des Kunden, mit quelle_turn aus briefing.md>
- **Auf der Website:** Nicht oder nur schwach kommuniziert
- **Implikation:** <was das für die Strategie bedeutet>

(weitere Items …)

## Typ B — USP-Inkonsistenzen

(analog)

## Typ C — Portfolio-Diskrepanzen

(analog)

## Typ D — Zielgruppen-Mismatch

(analog)

## Empfehlungen für die MTA-Slides

Welche der Abweichungen würden wir dem Kunden in der MTA-Präsentation vorlegen? Welche sind so eindeutig, dass sie eine eigene Folie verdienen?
```

## Priorisierung

Priorität jeder Abweichung ergibt sich aus zwei Fragen:

1. **Wie zentral ist das Thema?** Ein vergessener Hauptservice ist wichtiger als eine unklare Tonalität.
2. **Wie schmerzhaft ist die Schließung der Lücke?** Eine einzelne neue Hero-Headline ist trivial; ein Website-Re-Design ist teuer.

| Hohe Priorität | Mittlere Priorität | Niedrige Priorität |
|---|---|---|
| Zentrale USPs fehlen | Sekundäre Inkonsistenzen | Tonalitäts-Feinheiten |
| Hauptzielgruppe nicht adressiert | Portfolio-Reihenfolge ungünstig | Kleinere Wording-Unterschiede |
| Falsches Vertriebs-Versprechen | Touchpoint-Lücken (z.B. Social fehlt) | Layout-Detail-Themen |

## Spezialfall: keine `briefing.md`

Wenn `briefing.md` fehlt (z. B. weil `01-02-kickoff-transcript-parser` noch nicht lief), wird:

1. Keine `abweichungen.md` erzeugt
2. Im Skill-Schluss-Format steht: *"Abweichungs-Analyse übersprungen — kein briefing.md vorhanden. Wenn vorhanden, 01-02-kickoff-transcript-parser zuerst laufen lassen."*
3. `kunde.md` wird trotzdem normal geschrieben

## Spezialfall: `inhaltliche_dichte` im Briefing ist `niedrig`

Wenn das Briefing selbst Lücken hat (z. B. Verkaufsgespräch-Charakter), ist der Vergleich schwierig — viele Felder fehlen einfach im Briefing.

Verhalten in diesem Fall:

- Abweichungs-Analyse läuft trotzdem, aber **nur über die Felder, die im Briefing belegt sind**
- Im Header der `abweichungen.md`: Hinweis-Block, dass Briefing dünn war, daher Vergleich unvollständig
- Hauptfokus auf USP-Lücken (Typ A) und Zielgruppen-Mismatch (Typ D) — die anderen Typen brauchen mehr Briefing-Substanz
