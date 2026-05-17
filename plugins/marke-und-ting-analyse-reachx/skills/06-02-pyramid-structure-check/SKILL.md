---
name: 06-02-pyramid-structure-check
description: Bewertet die Gesamtstruktur einer Google-Slides-Präsentation nach dem Pyramidalprinzip (Minto)&#58; Governing Thought, SCQA-Intro, MECE-Sektionen, Standalone-Test über Section Divider hinweg. Schlägt konkrete Restrukturierungen (Folien verschieben, zusammenlegen, streichen, einfügen) vor und pflegt Beobachtungen als Kommentare auf Section-Divider-Folien ein. Nutze diesen Skill, sobald der Nutzer eine Google-Slides-URL oder Presentation-ID nennt und nach Storyline, Argumentationsbogen, Deck-Aufbau, Pyramid Principle, MECE, SCQA oder Storyflow fragt — auch bei "Struktur prüfen", "Storyline review", "ist die Argumentation logisch?", "Deck-Architektur", "hängt das Deck zusammen?". Komplementär zu /06-01-action-titles-check (für einzelne Titel). Setzt gws-CLI voraus. NICHT für PPTX-Dateien (dort PPTX-Skill).
---

# Pyramid Structure Check (Pyramidalprinzip auf Deck-Ebene)

Reviewt den Argumentationsbogen einer Google-Slides-Präsentation als Ganzes — nicht die einzelnen Titel, sondern die Architektur dahinter: Hat das Deck eine klare zentrale These? Führt das Intro sauber dorthin? Sind die Hauptsektionen MECE und stützen die These? Ergibt das Querlesen der Strukturelemente einen kohärenten Argumentationsbogen?

Das Ergebnis sind ein strukturierter Diagnose-Bericht, konkrete Restrukturierungs-Vorschläge (welche Folie wohin, was streichen, was zusammenlegen) und — auf Wunsch — verankerte Kommentare auf den Section-Divider-Folien, die jeweils die Beobachtungen zur betreffenden Sektion festhalten.

Methodik und Bewertungskriterien stehen ausführlich in `reference/methodology.md` — lies diese Datei *vor* der Strukturanalyse in Schritt 5.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="<name-dieses-skills>"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Report-Render zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Verhältnis zu /06-01-action-titles-check

Beide Skills nutzen denselben theoretischen Hintergrund (Pyramidalprinzip nach Minto), aber unterschiedliche Bewertungsebenen:

- **06-01-action-titles-check**: bewertet jeden einzelnen Folientitel auf Aussagekraft (Mikro-Ebene).
- **06-02-pyramid-structure-check** (dieser Skill): bewertet die Architektur des Decks — Hauptaussage, Intro-Logik, Sektionierung, Argumentationsfluss (Makro-Ebene).

Beide Reviews ergänzen sich. Wenn der Nutzer beides möchte, ist die natürliche Reihenfolge: erst Struktur, dann Titel — denn der Strukturreview kann Folien streichen oder verschieben, was Titel-Reviews überflüssig macht.

## Voraussetzungen

- `gws` ist installiert und authentifiziert. Schlägt ein Aufruf mit Auth-Fehler (Exit-Code 2) fehl, weise den Nutzer auf einmaliges `gws auth login` hin.
- Für das Einpflegen von Kommentaren braucht der Nutzer Kommentar-Rechte am Deck (kommt mit Edit- oder Kommentator-Rolle).

## Schritt 0 — MTA-Kontext laden (optional, Dual-Mode)

Dieser Skill kann in zwei Modi laufen:

1. **MTA-Modus**: Wenn der Nutzer den Skill im Kontext einer laufenden MTA aufruft und die MTA im lokalen Active-MTA-Cache registriert ist, wird der Diagnose-Bericht nach Drive in den `reports/`-Sub-Folder der aktiven MTA hochgeladen und `status.md` aktualisiert.
2. **Standalone-Modus**: Wenn keine MTA aktiv ist, schreibt der Skill den Bericht lokal — wie bisher. Slides-Lesen und Strukturanalyse sind identisch in beiden Modi.

Erkennungs-Logik am Skill-Anfang:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_MODE=false
if [ -n "<slug>" ] && [ -f "$DRIVE_PY" ]; then
  MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>" 2>/dev/null)
  if [ -n "$MTA_JSON" ]; then
    MTA_MODE=true
    FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
    META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
    python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
    REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
  fi
fi
```

Wenn kein MTA-Slug genannt wird und keiner im Cache ist: Standalone-Modus, kein Hard-Abbruch.

## Schritt 1 — Presentation-ID bestimmen

Akzeptiere als Input eine vollständige Slides-URL oder eine reine ID. Aus einer URL wie `https://docs.google.com/presentation/d/<ID>/edit#...` extrahiere `<ID>` zwischen `/d/` und dem nächsten `/`. Wurde nichts mitgegeben, frage explizit nach URL oder ID, bevor Du fortfährst.

## Schritt 2 — Deck einlesen

Strukturreview braucht mehr Felder als ein reiner Titel-Review — auch Body, Notes und Layout-Informationen, weil daraus erkennbar wird, welche Rolle eine Folie im Argumentationsbogen spielt.

```bash
gws slides presentations get --params '{
  "presentationId": "<ID>",
  "fields": "slides(objectId,slideProperties(notesPage(pageElements(shape(placeholder,text)))),pageElements(objectId,shape(placeholder,text)))"
}'
```

Schlägt der Aufruf mit `accessNotConfigured` fehl, ist die Slides-API im GCP-Projekt nicht aktiviert — gib den Aktivierungs-Hinweis aus der gws-Stderr unverändert an den Nutzer weiter.

**Sanity-Check direkt nach dem Einlesen** (Schutz gegen Halluzinationen): Logge sofort nach dem gws-Aufruf zwei Werte und gib sie auch im Output am Ende mit aus, damit jederzeit verifizierbar ist, welches Deck tatsächlich analysiert wurde:

1. **Folienzahl** — `len(slides)` aus der JSON-Antwort.
2. **Cover-Titel** — Titel-Text der ersten Folie (Cover).

Beide Werte gehören in den fertigen Bericht (z. B. als kompakter Header: "Deck: <Cover-Titel> · 88 Folien"). Wenn Du im weiteren Verlauf eine andere Folienzahl oder einen anderen Cover-Titel erwähnst, hast Du das falsche Deck im Kopf — stoppe und lies das Deck erneut ein. Diese Verifikation hat sich in Real-Tests als wertvoll erwiesen, weil bei der parallelen Analyse mehrerer Decks Verwechslungen sonst stille Halluzinationen erzeugen.

## Schritt 3 — Pro Folie extrahieren und Folientyp klassifizieren

Sammle aus der JSON-Antwort für jede Folie:

- **Folien-Index** — beginnend bei 1, in der Reihenfolge des `slides`-Arrays.
- **Folien-ObjectId** — `slide.objectId`. Wird für den Kommentar-Anchor in Schritt 8 benötigt.
- **Titel-Text** — Text aus *allen* `pageElement` mit `shape.placeholder.type === "TITLE"` oder `"CENTERED_TITLE"`. Eine Folie kann mehrere TITLE-Placeholder haben — typisches Beispiel sind Section-Divider mit zwei TITLE-Elementen: einem für die Sektions-Nummerierung ("01.", "02.") und einem für den Sektions-Namen ("Summary Markenanalyse"). Sammle in solchen Fällen alle TITLE-Texte in der Reihenfolge, in der sie im `pageElements`-Array stehen, und konkateniere sie mit Leerzeichen oder Trennzeichen — das Ergebnis ist der "vollständige Titel" der Folie (z. B. "01. Summary Markenanalyse"). Diese Information ist essenziell für Detection-Schritt 4 in Schritt 4 (Sektions-Nummerierungs-Lücke).
- **Body-Text** — alle anderen Text-tragenden Shapes.
- **Speaker Notes** — aus `slide.slideProperties.notesPage.pageElements[*]` das Shape mit `placeholder.type === "BODY"`.

**Folientyp klassifizieren** (wichtig für Strukturanalyse):

- **Cover**: typischerweise erste Folie, Deck-Titel + Datum + ggf. Untertitel, kein Argumentcharakter.
- **Agenda / Inhalt**: Titel "Agenda", "Inhalt", "Inhaltsverzeichnis", "Übersicht".
- **Section Divider**: Folie mit nur Sektions-Nummer und -Name (z. B. "01. Markenanalyse"), reine Zwischenüberschrift ohne substantiellen Body.
- **Statement-Folie**: kein TITLE-Placeholder, gesamter Folientext trägt eine zusammenhängende Aussage (ein bis drei Sätze, kein separater Body-Block).
- **Inhalts-Folie**: alles andere — der eigentliche Argument-Träger.
- **Closing / Q&A / Kontakt**: typischerweise letzte ein bis zwei Folien (z. B. "Zeit für Fragen", "Vielen Dank").
- **Anhang / Appendix / Backup**: Folien hinter dem Closing oder unter einem Section-Divider mit "Anhang"/"Appendix"/"Backup" im Titel. Nicht Teil der Hauptpyramide, aber im Strukturreview auf Vollständigkeit prüfen (siehe Schritt 6).

Der Folientyp bestimmt die Rolle in der Pyramide. Section Divider markieren die Hauptverästelung, Statement-Folien tragen oft die Hauptaussage des jeweiligen Astes, Inhalts-Folien stützen die Aussagen, Anhang-Folien stehen außerhalb der Pyramide.

## Schritt 4 — Deck-Skelett aufbauen

Bevor Du in die Bewertung gehst: Baue eine kompakte Repräsentation des Argumentationsbogens auf. Diese Skelett-Darstellung ist später Grundlage für die Strukturdiagnose und für die Restrukturierungs-Vorschläge.

Gehe das Deck linear durch und bilde Sektionen anhand der Section Divider. Eine Sektion umfasst alle Folien zwischen einem Section Divider und dem nächsten (bzw. dem Ende des Decks). Innerhalb einer Sektion gehören die Inhalts-Folien zur Argumentation dieser Sektion.

Gewünschte Skelett-Form (intern, nicht zwingend an den Nutzer ausgegeben):

```
Cover: "Marke Aufmaster — Strategie 2025"
Agenda: ["Marktanalyse", "Markenanalyse", "Empfehlung"]

Sektion 1: "01. Marktanalyse" (Folien 3–8)
  - Folie 3 (Inhalt): "Der DACH-Markt für Premiumkabel ..."
  - Folie 4 (Inhalt): "Drei Wettbewerber haben in 2024 ..."
  - Folie 5 (Statement): "Aufmaster ist im Premiumsegment ..."
  ...

Sektion 2: "02. Markenanalyse" (Folien 9–17)
  ...

Sektion 3: "03. Empfehlung" (Folien 18–22)
  ...

Closing: Q&A + Kontakt
```

Notiere für jede Folie kurz, welche Aussage sie zu tragen scheint (aus Titel, Body, Notes). Bei Inhalts-Folien ohne klare Aussage: das ist bereits ein Befund für den späteren Bericht.

**Vier strukturelle Detection-Schritte beim Skelett-Aufbau** — diese decken typische handwerkliche Antipatterns auf, die im Strukturreview auffallen müssen, bevor in die Bewertung der vier Dimensionen gegangen wird:

1. **Duplikat-Titel über aufeinanderfolgende Folien**: Identifiziere Folien, deren Titel exakt oder nahezu identisch zur jeweils vorhergehenden Folie ist. Typischer Fall: Eine Tabelle wurde aus Platzgründen über zwei Folien gesplittet, beide tragen denselben Titel ohne "(1/2)"/"(2/2)"-Kennzeichnung. Notiere die Folien-Indizes und behandle den Befund als handwerklichen Antipattern (siehe Methodik).
2. **Doppelte Section-Divider mit identischem Titel**: Identifiziere Section-Divider, deren Titel mehrfach im Deck vorkommt. Typischer Fall: Zwei Folien tragen beide "Investition" als Divider, dazwischen liegen Inhalts-Folien. Notiere Folien-Indizes und behandle als MECE-Verletzung (siehe Methodik).
3. **Unvollständige Anhang-Sektion**: Wenn das Deck einen Anhang hat, prüfe seine innere Logik. Beginnt der Anhang mit einer Nummerierung wie "1." oder "Punkt 1", die "2.", "3." erwarten lässt, aber keine Fortsetzung hat? Notiere als handwerklichen Antipattern.
4. **Sektions-Nummerierungs-Lücke**: Tragen Section-Divider eine durchgehende Nummerierung ("01.", "02.", "03." oder "Kapitel 1", "Kapitel 2", "Kapitel 3")? Wichtig: Die Nummerierung steht in vielen Decks als *separater* TITLE-Placeholder neben dem Sektions-Namen — Du musst alle TITLE-Texte einer Folie zusammen betrachten (siehe Schritt 3 zur Titel-Extraktion). Wenn eine durchgehende Nummerierung erkennbar ist, prüfe, ob die Reihe lückenlos ist. Sprung von "02." auf "04." ohne "03." ist ein verräterisches Symptom dafür, dass beim Bauen umstrukturiert wurde und eine Sektion verloren ging oder zusammengelegt wurde — meist ist genau diese fehlende Sektion die Brücke, die das Deck strukturell vermissen lässt. Notiere Folien-Indizes und Lücken-Position. Kommt in vielen Decks vor und wird oft übersehen, weil der erste TITLE-Placeholder ohne den zweiten geprüft wird.

Diese vier Detection-Schritte produzieren Beobachtungen, die später in Teil 3 (Restrukturierungs-Vorschläge) als eigene Vorschläge erscheinen — sie sind nicht Teil der vier Dimensionsbewertungen, aber sie gehören in einen sauberen Strukturreview.

## Schritt 5 — Methodik laden

Lies *jetzt* `reference/methodology.md` vollständig. Die Datei enthält:

- Theorie hinter dem Pyramidalprinzip auf Deck-Ebene
- Die vier Bewertungsdimensionen (Governing Thought, SCQA, MECE, Standalone-Test) im Detail
- Häufige Antipatterns (Bottom-up-Storyline, Themen-statt-These, MECE-Verletzungen, Loose Ends)
- Restrukturierungs-Patterns (Verschieben, Zusammenlegen, Streichen, Einfügen)
- Beispielbewertungen als Kalibrierung

## Schritt 6 — Strukturanalyse durchführen

Bewerte das Deck systematisch entlang der vier Dimensionen. Bewertungsskala pro Dimension: **Stark | Verbesserungswürdig | Schwach**.

### Dimension 1 — Governing Thought

Frage: Hat das Deck eine klare zentrale Aussage, und ist sie früh und prominent platziert?

Suche aktiv nach der Kandidaten-Hauptaussage. Sie steht typischerweise:
- am Ende des Intros (nach SCQA-Setup), oder
- als erste Folie nach der Agenda, oder
- prominent in der Empfehlungs-Sektion.

Wenn Du keine eindeutige Hauptaussage findest, ist das ein zentraler Befund. Häufiger Fall: Das Deck arbeitet sich linear durch Themen, ohne dass eine These das Ganze zusammenhält ("Bottom-up-Storyline").

Beziehe Speaker Notes ein — manchmal steckt die Hauptaussage dort und ist nicht in den Folien sichtbar.

### Dimension 2 — SCQA-Intro

Frage: Führt das Intro (Folien zwischen Cover und erster Inhaltssektion) sauber durch das SCQA-Schema?

- **Situation**: Was ist der Kontext, der unstrittig ist?
- **Complication**: Was hat sich verändert, was ist das Problem?
- **Question**: Welche Frage stellt sich daraus?
- **Answer**: Was ist die Antwort (= Governing Thought)?

Häufige Schwächen: Intro startet direkt mit Daten (kein Setup), Complication fehlt (Frage wirkt aus der Luft gegriffen), Answer wird nicht gegeben (Empfehlung erst am Ende — verletzt Top-down-Prinzip).

### Dimension 3 — MECE-Struktur der Sektionen

Frage: Sind die Hauptsektionen mutually exclusive und collectively exhaustive — und stützt jede Sektion die Governing Thought?

Prüfe:
- **Mutual Exclusivity**: Überschneiden sich Sektionen inhaltlich? (z. B. "Markt" und "Wettbewerb" als zwei Sektionen, obwohl sich der Inhalt überlappt.)
- **Collective Exhaustiveness**: Decken die Sektionen zusammen alles ab, was die Hauptaussage stützen muss? Fehlt eine Sektion, deren Inhalt für die Argumentation kritisch wäre?
- **Relevanz pro Sektion**: Stützt jede Sektion direkt die Governing Thought, oder gibt es Sektionen, die "interessant aber tangential" sind?
- **Hierarchie-Konsistenz**: Sind die Section-Divider auf demselben Abstraktionsniveau, oder mischt das Deck Top-Level-Themen mit Sub-Themen?

### Dimension 4 — Standalone-Test (Deck-Ebene)

Frage: Wenn jemand nur die Section-Divider-Titel + Action Titles der Folien hintereinander liest — versteht er den Argumentationsbogen?

Mache den Test explizit: Lies dir die Reihe der Section-Divider-Titel und der Folien-Action-Titles vor. Ist es eine zusammenhängende Argumentation, die die Governing Thought herleitet? Oder klingt es wie eine Themenliste?

Die Standalone-Lesbarkeit auf Deck-Ebene ist anspruchsvoller als auf Folien-Ebene — sie verlangt, dass die Action Titles aufeinander aufbauen und gemeinsam die Hauptaussage tragen.

Hinweis: Schwache einzelne Action Titles ziehen den Standalone-Test runter, sind aber Sache des `/06-01-action-titles-check`-Skills. Hier geht es um die *Reihenfolge* und das *Zusammenspiel*: Wenn alle Titel stark wären, würde der Argumentationsbogen funktionieren?

### Handwerkliche Zusatzchecks (nicht Teil der Dimensionsbewertung)

Vier strukturelle Antipatterns, die *außerhalb* der vier Dimensionen liegen, aber in einen vollständigen Review gehören. Sie wurden bereits in Schritt 4 detektiert — hier werden die Befunde zur Auswertung für den Bericht zusammengefasst:

- **Duplikat-Titel über aufeinanderfolgende Folien** (aus Detection-Schritt 1): handwerklicher Antipattern. Geht in Bericht-Teil 3 als Markierungs- oder Zusammenleg-Vorschlag.
- **Doppelte Section-Divider** (aus Detection-Schritt 2): MECE-Verletzung im weiteren Sinn — wirkt wie Versehen oder Stil-Bruch. Geht in Bericht-Teil 3 als Auflösungsvorschlag.
- **Unvollständiger Anhang** (aus Detection-Schritt 3): handwerklicher Antipattern. Geht in Bericht-Teil 3 als Vervollständigungs- oder Streichungsvorschlag.
- **Sektions-Nummerierungs-Lücke** (aus Detection-Schritt 4): besonderer Antipattern — meist nicht nur kosmetisch, sondern Hinweis auf eine fehlende Sektion, die ursprünglich existierte oder existieren sollte. Geht in Bericht-Teil 3 als Renumerierungs- oder Sektions-Ergänzungs-Vorschlag, mit der Hypothese, welche Sektion an der Lücken-Position fehlen könnte.

Diese vier Befunde fließen *nicht* in die Bewertung der vier Dimensionen ein (eine "Schwach"-Bewertung in MECE wegen eines doppelten Dividers wäre überzogen) — sie sind nebenstehende handwerkliche Beobachtungen, die das Deck spürbar polierter machen, wenn sie behoben werden. Eine Ausnahme: Eine **Sektions-Nummerierungs-Lücke** kann gleichzeitig auf eine *inhaltliche* MECE-Lücke hinweisen — wenn das fehlende Kapitel argumentativ wirklich gebraucht wird (typischer Fall: fehlendes Brücken-/Synthese-Kapitel). In diesem Fall darf die Lücke zusätzlich als Befund in Dimension 3 (MECE-Collective-Exhaustiveness) erscheinen.

## Schritt 7 — Combined Output schreiben

Der Output besteht aus vier Teilen, in dieser Reihenfolge:

### Teil 1 — Executive Summary (4–6 Sätze)

Eine knappe Synthese der Strukturdiagnose:

- Die Kandidaten-Hauptaussage des Decks (in eigenen Worten verdichtet, mit Folien-Referenz).
- Die Bewertungen der vier Dimensionen in einem Satz pro Dimension.
- Das wichtigste strukturelle Problem und die wichtigste konkrete Restrukturierung.
- Ob das Deck nach Restrukturierung tragfähig wäre, oder ob die Storyline grundlegend neu gedacht werden müsste.

### Teil 2 — Bewertung der vier Dimensionen

Pro Dimension ein Block in folgendem Format:

```
## Dimension {N}: {Name}

**Bewertung:** {Stark | Verbesserungswürdig | Schwach}

{3–5 Sätze Prosa-Bewertung. Konkret beobachten, mit Folien-Referenzen ("Folie 7", "Sektion 02"). Zitate aus Titeln/Body/Notes wenn hilfreich.}

**Kernbefund:** {Ein Satz, der die Diagnose zuspitzt.}
```

### Teil 3 — Restrukturierungs-Vorschläge

Konkrete, umsetzbare Empfehlungen. Ordne nach Hebel: Was am meisten bewirkt zuerst.

Für jeden Vorschlag dieses Format:

```
### Vorschlag {N}: {Kurzbeschreibung}

**Aktion:** {Verschieben | Zusammenlegen | Streichen | Einfügen | Umbauen}

**Konkret:** {Welche Folie/n? Wohin? Was ändert sich am Section-Header?}

**Warum:** {2–3 Sätze, welches Pyramidalprinzip dadurch erfüllt wird.}

**Aufwand:** {Klein | Mittel | Groß}
```

Achte darauf: Vorschläge müssen *konkret und ausführbar* sein. Nicht "Storyline schärfen", sondern "Folie 5 ans Ende von Sektion 2 verschieben und als Übergang zu Sektion 3 nutzen, weil sie den Schluss aus der Markenanalyse zieht und dieser Schluss die Empfehlung vorbereitet".

Wenn das Deck eine grundsätzlich neue Storyline braucht, sage das explizit und skizziere eine alternative Sektionierung — typischerweise drei bis fünf Sektionen, jede mit einem Satz, was sie beweisen müsste.

### Teil 4 — Per-Sektion-Beobachtungen

Pro Sektion ein kompakter Block — Grundlage für die Section-Divider-Kommentare in Schritt 8:

```
## Sektion {N}: "{Section-Divider-Titel}"

**Rolle in der Argumentation:** {1 Satz, was diese Sektion zur Governing Thought beiträgt — oder beitragen sollte.}

**Stärken:** {1–2 Sätze.}

**Schwächen:** {1–2 Sätze, mit Folien-Referenzen.}

**Empfehlung:** {1–2 Sätze, was konkret zu ändern wäre.}
```

Diese Per-Sektion-Beobachtungen werden in Schritt 8 als Kommentar-Inhalt verwendet.

## Schritt 8 — Section-Kommentare anbieten

Nach dem Combined Output frage den Nutzer:

> "Möchtest Du die Per-Sektion-Beobachtungen als Kommentare auf den jeweiligen Section-Divider-Folien einpflegen? Dann sieht der Empfänger pro Sektion direkt im Deck, welche strukturellen Anmerkungen es gibt — und kann sie selektiv übernehmen oder diskutieren. Ich gehe Sektion für Sektion durch und pflege nur das ein, was Du explizit bestätigst."

Wenn ja, gehe in der Reihenfolge des Decks durch alle Sektionen und zeige pro Sektion:

```
Sektion {N}: "{Section-Divider-Titel}" (Folie {Index})
  Geplanter Kommentar:
    Rolle: {Rolle in der Argumentation}
    Schwächen: {Schwächen}
    Empfehlung: {Empfehlung}
```

Warte auf eine explizite Antwort:

- "ja" / "übernehmen" → Kommentar in die Queue.
- "nein" / "skip" → überspringen, weiter zur nächsten Sektion.
- Eine Anpassung des Kommentartextes durch den Nutzer → diese Variante in die Queue.

Frage **eine Sektion pro Runde**, nicht mehrere gleichzeitig.

Gibt es Sektionen ohne erkennbaren Section Divider (lineares Deck ohne Sektionierung), biete an, stattdessen einen einzelnen zusammenfassenden Kommentar auf Folie 1 zu setzen — Inhalt: Executive Summary aus Teil 1.

## Schritt 9 — Kommentare einpflegen

Für jede bestätigte Sektion erstelle einen verankerten Kommentar via Drive-API auf der jeweiligen Section-Divider-Folie. Der Anchor referenziert die Folien-ObjectId des Section Dividers:

```bash
gws drive comments create \
  --params '{"fileId": "<PRESENTATION_ID>", "fields": "id,content,anchor"}' \
  --json '{
    "content": "<KOMMENTAR_TEXT>",
    "anchor": "{\"r\":\"head\",\"a\":[{\"matrix\":{\"a\":1,\"b\":0,\"c\":0,\"d\":1,\"e\":0,\"f\":0}},{\"page\":\"<SLIDE_OBJECT_ID>\"}]}"
  }'
```

`<KOMMENTAR_TEXT>` wird wie folgt aufgebaut:

```
[Struktur-Review — Pyramidalprinzip]
Sektion: <Section-Titel>

Rolle in der Argumentation:
<Rolle>

Stärken:
<Stärken>

Schwächen:
<Schwächen>

Empfehlung:
<Empfehlung>
```

Erstelle die Kommentare einzeln (ein API-Call pro Sektion) — die Drive-API hat keinen Batch-Endpoint für Kommentare. Bei einem Fehler mit dem Anchor (z. B. ungültiges Format): falle zurück auf einen Datei-übergreifenden Kommentar ohne Anchor, dessen Content mit "[Sektion: <Titel>]" beginnt.

```bash
gws drive comments create \
  --params '{"fileId": "<PRESENTATION_ID>"}' \
  --json '{"content": "[Sektion: <Titel>] [Struktur-Review — Pyramidalprinzip]\n..."}'
```

Wenn keine Bestätigungen vorliegen, überspringe Schritt 9 und gehe direkt zu Schritt 10.

## Schritt 10 — Abschluss

Fasse zusammen:

- Anzahl tatsächlich eingepflegter Section-Kommentare und Anzahl Fallback-Kommentare (falls vorhanden).
- Bewertungen der vier Dimensionen in Stichworten (z. B. "Governing Thought: Verbesserungswürdig, SCQA: Schwach, MECE: Stark, Standalone: Verbesserungswürdig").
- Die ein bis drei Restrukturierungs-Vorschläge mit dem höchsten Hebel als Top-Empfehlungen.
- Direkter Link zum Deck: `https://docs.google.com/presentation/d/<ID>/edit`.
- Hinweis: Die Folien-Reihenfolge bleibt unverändert. Der Empfänger sieht die Beobachtungen im Kommentar-Panel und kann sie selektiv umsetzen, mit Antworten diskutieren oder als gelöst markieren.
- Optional: Hinweis auf den komplementären Skill `/06-01-action-titles-check` für die Bewertung einzelner Folientitel — jetzt sinnvoll, nachdem die Struktur geklärt ist.

### HTML-Report speichern (Dual-Mode)

**Validierung — Pflicht:** Den fertigen Report vor dem Upload prüfen: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad>` (ohne `--shell`, da dieser Skill den im Skill beschriebenen HTML-Aufbau nutzt). Exit-Code 0 → ausliefern. Exit-Code 1 → nicht ausliefern, korrigieren, erneut validieren. Keine CSS-Klassen verwenden, die nicht im `<style>`-Block des Templates definiert sind.

Falls der Combined Output zusätzlich als HTML-Diagnose-Report archiviert werden soll:

- **Dateiname**: `deck-qa-pyramid-{kunden-slug}-{datum}.html`
- **MTA-Modus** (`MTA_MODE=true`): Schreibe HTML lokal nach `/tmp/<filename>`, lade via `python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "<filename>" "/tmp/<filename>" "text/html"` in den `reports/`-Sub-Folder. Aktualisiere `status.md` (siehe `contracts.md` Abschnitt 3): `06-02-pyramid-structure-check` in `schritte_done`, eigene Sektion in "✓ Erledigt" mit Datum, Outputs und Bewertungs-Zusammenfassung. Dashboard (`reports/index.html`) um Skill-Eintrag und Report-Link ergänzen.
- **Standalone-Modus**: HTML wird im Working Directory abgelegt (Fallback `/tmp/`). Kein status.md-Update.

## Edge Cases

- **Deck ohne Section Divider** (lineare Folge ohne erkennbare Sektionierung): Die MECE-Dimension wird stattdessen über den thematischen Fluss bewertet. Statt Section-Kommentaren biete einen Master-Kommentar auf Folie 1 an. Dieser Fall ist bereits ein zentraler Strukturbefund — benenne ihn explizit im Bericht.
- **Sehr kurzes Deck (< 8 Folien)**: SCQA und MECE-Strukturanalyse passen nur eingeschränkt. Konzentriere Dich auf Governing Thought und Standalone-Test, und sage explizit, dass die anderen Dimensionen für ein Deck dieser Länge weniger relevant sind.
- **Deck ohne erkennbare Hauptaussage**: Schreibe das im Bericht klar als Befund. Schlage in Teil 3 eine Hypothese für eine Hauptaussage vor (auf Basis von Body und Notes) und mache die Restrukturierung konditional ("Wenn die Hauptaussage X ist, dann …").
- **Deck mit mehreren parallel platzierten Hauptaussagen** (typisch bei Status-Updates): Erkennen, benennen, und klären, ob das eine bewusste Entscheidung war. Pyramidalprinzip verlangt eine Hauptaussage — Multi-Thesen-Decks sind ein Antipattern, außer das Format ist explizit ein Update mit mehreren Workstreams.
- **403 / `accessNotAuthorized` bei Kommentar-Erstellung**: Nutzer hat keine Kommentar-Rechte. Erkläre das, biete an, das Review als reinen Bericht zu nutzen.
- **Andere Sprache als Deutsch im Deck**: Erkenne die Sprache aus Body und Notes und schreibe Bericht und Kommentare in derselben Sprache.
- **Anchor-Format wird abgelehnt**: Fallback auf nicht-verankerten Kommentar mit "[Sektion: <Titel>]"-Präfix im Content.
