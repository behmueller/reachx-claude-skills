# Briefing-Schema (`data/briefing.md`)

Das Output-Format, das `01-02-kickoff-transcript-parser` schreibt und das alle Folge-Skills lesen. Markdown mit YAML-Frontmatter — Frontmatter für maschinenlesbare Felder, Body für Narrative und Belege.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 01-02-kickoff-transcript-parser
generiert_am: <ISO-8601>
schema_version: "1.0"
transkript_quelle:
  pfad: <relativer Pfad zur Transkript-Datei>
  sha256: <Hash der Quell-Datei>
  meeting_titel: <aus Transkript-Header>
  meeting_datum: <ISO-8601, aus Transkript-Header>
  meeting_dauer: <HH:MM:SS oder MM:SS>
  anzahl_turns: <int>
  anzahl_woerter: <int>
  sprecher_erkannt: [<liste von Namen>]

# === Meeting-Typ-Klassifikation ===
meeting_typ: <kickoff_extern | briefing_intern | verkaufsgespraech | unklar>
meeting_typ_begruendung: <ein Satz, warum dieser Typ>
speaker_verlaesslich: <true | false>   # false wenn 1 Sprecher >80% Wortanteil hat

# === Inhaltliche Felder (alle Listen können leer sein) ===
ziele:
  - typ: <umsatz | leadgen | branding | retention | unklar>
    beschreibung: <Kunden-Ziel in eigenen Worten>
    quelle_turn: <timestamp, optional>
    unklar_aus_transkript: <true | false>

kpis:
  - metrik: <z.B. "Anzahl neuer WEG-Mandate">
    zielwert: <Zahl + Einheit, oder null>
    zeitraum: <z.B. "pro Quartal", "bis Q4 2026", oder null>
    quelle_turn: <timestamp, optional>
    unklar_aus_transkript: <true | false>

zielgruppen:
  - persona: <Kurzbeschreibung>
    segment: <B2B | B2C | beide>
    pain_points: [<liste>]
    quelle_turn: <timestamp, optional>

produkte_dienstleistungen:
  - name: <Produktname>
    beschreibung: <kurze Beschreibung>
    preis_modell: <einmalig | abo | projektbasiert | unklar>
    quelle_turn: <timestamp, optional>

usps_kunde_eigenwahrnehmung:
  - usp: <wie der Kunde es selbst formuliert>
    beleg: <kurzes Zitat oder Paraphrase aus dem Transkript>
    quelle_turn: <timestamp, optional>

wettbewerber_genannt:
  - name: <Name>
    kontext: <warum erwähnt, wie positioniert>
    bedrohungsgrad_aus_briefing: <direkt | indirekt | inspiration | unklar>
    quelle_turn: <timestamp, optional>

budget_hinweise:
  marketing_budget_aktuell: <z.B. "ca. 2k €/Monat" oder null>
  budget_bereitschaft: <Aussage zur Bereitschaft, oder null>
  constraints: [<liste von Beschränkungen>]
  quelle_turn: <timestamp, optional>

no_gos: [<Liste von Themen, die der Kunde explizit ausgeschlossen hat>]

tools_des_kunden:
  - kategorie: <CRM | Analytics | CMS | E-Mail | Ads | Social | Andere>
    name: <Tool-Name>
    status: <im_einsatz | unklar | abgelehnt | geplant>
    quelle_turn: <timestamp, optional>

regionen: [<Liste relevanter Märkte/Regionen>]

stakeholder_kunde:
  - name: <Name aus Transkript>
    rolle: <Geschäftsführung | Marketing | Vertrieb | IT | Sonstige>
    aussagekraft: <hoch | mittel | niedrig>  # wie oft sprechen sie, mit wie viel Substanz

offene_punkte: [<Fragen, die im Meeting nicht abschließend geklärt wurden>]

# === Übergreifende Qualitäts-Indikatoren ===
inhaltliche_dichte: <hoch | mittel | niedrig>  # Bewertung des Briefing-Werts
extraktion_vollstaendig: <true | false>
extraktion_lücken: [<liste konkret fehlender oder unklarer Felder>]
---

# Briefing: <Kundenname>

## Übersicht

Kompakte Zusammenfassung (3–5 Sätze): Wer ist der Kunde, was sind die Hauptziele, welche besonderen Herausforderungen oder Chancen wurden im Meeting deutlich.

## Ziele und KPIs

Strukturierte Darstellung der oben im Frontmatter aufgelisteten Ziele und KPIs, plus Kontext aus dem Meeting. Bei `unklar_aus_transkript: true` explizit markieren.

## Zielgruppen und Markt

Beschreibung der Zielgruppen, Regionen, Marktposition aus Kunden-Sicht.

## Produkte und USPs

Was bietet der Kunde an, wie positioniert er sich, welche USPs nennt er selbst.

## Wettbewerb

Welche Wettbewerber wurden genannt, wie ordnet der Kunde sie ein.

## Tooling und Budget

Aktueller Stack, Budget-Indikationen, Constraints.

## Offene Punkte

Was wurde nicht geklärt — Liste mit Verweisen auf den Kontext.
```

## Feld-Erläuterungen

### `meeting_typ`

| Wert | Definition | Typische Signale |
|---|---|---|
| `kickoff_extern` | Kickoff mit Kundenseite + Agentur am Tisch | Beide Seiten sprechen, Vorstellungsrunde, Erwartungs-Klärung |
| `briefing_intern` | Stratege fasst Kickoff-Inhalte für Agentur-Crew zusammen | 1 dominanter Sprecher (>70%), wenig Dialog, viel Faktenmonolog |
| `verkaufsgespraech` | Erst-Gespräch zur Akquise, vor MTA-Beauftragung | Beide Seiten stellen sich vor, Sales-Pitch der Agentur, Bedarfsklärung |
| `unklar` | Aus dem Transkript nicht zuordenbar | Fehlende Header, abgebrochenes Meeting |

Bei `verkaufsgespraech` und `briefing_intern` sind Felder wie `kpis` oft leer — das ist ok, einfach als unklar markieren.

### `speaker_verlaesslich`

Setze auf `false`, wenn:

- Ein einzelner erkannter Sprecher >80% Wortanteil hat (typisches Fireflies-Merge-Problem)
- Die Sprecherzahl unrealistisch klein wirkt für ein Multi-Stakeholder-Meeting
- Wechsel-Frequenz extrem niedrig ist (lange Monologe von "Person A", obwohl im Text klar mehrere Stimmen sind)

In dem Fall: Zuordnungen `quelle_turn` weglassen oder mit `<unsicher>` markieren. **Verlasse dich auf den Inhalt, nicht auf den Speaker-Tag.**

### `unklar_aus_transkript`

Pflicht-Flag, wenn die Information aus dem Transkript hervorgeht, aber unvollständig ist. Beispiele:

- Ziel ist klar genannt ("mehr Neukundengeschäft"), aber kein konkreter Zielwert
- Budget wird erwähnt, aber Höhe ist nicht beziffert
- Wettbewerber genannt, aber nicht klar, wie sie positioniert sind

Nicht für Felder, die im Transkript überhaupt nicht vorkommen — die sind einfach leer.

### `ziele.typ`

- `umsatz` → direkter Umsatzbezug ("mehr verkaufen", "Online-Shop-Umsatz steigern")
- `leadgen` → Lead-Generierung ("mehr Anfragen", "mehr WEG-Mandate gewinnen")
- `branding` → Bekanntheit/Image ("Marke etablieren", "spitzer positionieren")
- `retention` → Bestandskunden-Bindung
- `unklar` → erkennbar Ziel, Typ nicht eindeutig

### `usps_kunde_eigenwahrnehmung`

**Wichtig: nur USPs, die der Kunde aus eigener Wahrnehmung formuliert.** Wenn der Stratege paraphrasiert ("Sie meinen also, eure Stärke ist X?") und der Kunde nur zustimmt ("Genau"), zählt das schon als USP — aber als `beleg` die Stratege-Frage *plus* die Zustimmung zitieren.

Wenn USPs nur von der Agentur erwähnt werden, ohne Kunden-Bestätigung, **nicht** als USP aufnehmen.

### `wettbewerber_genannt.bedrohungsgrad_aus_briefing`

- `direkt` → Kunde nennt den Wettbewerber als unmittelbare Konkurrenz im Tagesgeschäft
- `indirekt` → Verwandte Branche oder anderer Markt, aber relevant
- `inspiration` → Wettbewerber als Vorbild oder Best Practice genannt (z.B. "Schau dir Firma X an, die machen das gut")
- `unklar` → erwähnt, aber Einordnung fehlt

### `inhaltliche_dichte`

- `hoch` → klare Ziele, USPs, Wettbewerber, Budget-Indikationen alle vorhanden
- `mittel` → zentrale Felder vorhanden, einzelne Lücken
- `niedrig` → Verkaufsgespräch-Charakter, viele Lücken — der Stratege muss vor weiteren Skills nachhaken

## Pflicht-Verhalten bei Lücken

Wenn `inhaltliche_dichte: niedrig` oder mehr als 3 Felder als `unklar_aus_transkript: true` markiert sind, schreibt der Skill am Ende der Sektion **"Offene Punkte"** im Body eine prominente Notiz an den Strategen: welche Felder besonders kritisch sind und wo Nachfragen sinnvoll sind. Diese Notiz erscheint auch im HTML-Report und im Chat-Schluss-Format als "Offene Punkte"-Sektion.
