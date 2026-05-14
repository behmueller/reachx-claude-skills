# Extraktions-Leitfaden

Anleitung für die inhaltliche Extraktion aus dem geparsten Transkript in das Briefing-Schema. Basiert auf Mustern, die wir aus echten REACHX-Kickoff- und Verkaufsgesprächs-Transkripten gelernt haben.

## Reihenfolge der Extraktion

1. **Meeting-Typ klassifizieren** zuerst — bestimmt, welche Felder zu erwarten sind
2. **Speaker-Verlässlichkeit prüfen** — wenn unverlässlich, inhaltsbasiert arbeiten
3. **Inhaltsfelder extrahieren** in dieser Reihenfolge: Produkte → Zielgruppen → Ziele → USPs → Wettbewerber → Tools → Budget → No-Gos → Regionen → Stakeholder → Offene Punkte
4. **Qualitäts-Indikatoren** am Schluss setzen

Diese Reihenfolge entspricht dem natürlichen Informationsfluss in den Kickoff-Meetings: erst das *Was* (Produkt, Markt), dann das *Wofür* (Ziele), dann das *Wie* (USPs, Tools), dann die *Constraints* (Budget, No-Gos).

## Meeting-Typ-Klassifikation

Schlüssel-Signale:

**`kickoff_extern`**
- Im Titel/Header: "Kickoff", "Kick-Off", "Kick Off PA", Mischung aus Kunden- und Agentur-Sprechern
- Im Text: Vorstellungsrunde aller Beteiligten ("Mein Name ist X, ich bin bei Y …")
- Erwartungs-Klärung: "Was erwartet ihr von uns?", "Was wollt ihr am Ende haben?"
- Beide Seiten stellen Fragen
- Mehrere Stakeholder pro Seite

**`briefing_intern`**
- Im Titel: "Briefing", "Strategie-Meeting", "Kickoff-Aufbereitung", interne Codes/Kürzel
- Speaker-Statistik: 1 dominanter Sprecher (>70%), andere mit kurzen Bestätigungen oder Rückfragen
- Inhaltlich: Faktenmonolog mit Quereinwürfen
- Sprecher referenziert Kunde in dritter Person ("Der Kunde will …")
- **Aufmaster ist genau dieser Typ** — Bastian fasst nach dem externen Kickoff intern für die Strategen zusammen

**`verkaufsgespraech`**
- Im Titel: "erster Austausch", "Erstgespräch", "Vorstellung", "Pitch"
- Vor MTA-Beauftragung, daher: Agentur stellt *sich* vor (nicht das Vorgehen)
- Kunde beschreibt den Bedarf groß, ohne dass schon konkrete Ziele/KPIs gesetzt werden
- Häufig kein Zugriff auf interne Tools des Kunden ("Welche Tools nutzt ihr denn?")
- Sales-Phrasen der Agentur ("Wir können euch helfen mit X")

**Praktische Konsequenz**: bei `verkaufsgespraech` und `briefing_intern` sind die Felder `kpis`, `tools_des_kunden`, `regionen` oft unvollständig. Das ist kein Fehler des Skills, sondern Realität — markiere als `unklar_aus_transkript: true` und füge die Felder zur `offene_punkte`-Liste hinzu.

## Speaker-Verlässlichkeit

Beim Westend-Bank-Transkript bekommt Christiane Höfer von Fireflies ~89% Wortanteil zugewiesen, obwohl im Meeting nachweislich mehrere Stakeholder lange Wortbeiträge hatten (Tanja Breidenbenden, Bastian Hirsch online, Vorstand Thomas Rosenfeld als "Christiane Höfer" gelabelt, etc.).

**Erkennungsmerkmale für unverlässliche Speaker-Tags:**

1. Ein Sprecher hat >80% Wortanteil
2. Im Text springt das Thema mehrfach (jemand stellt sich vor, dann jemand anders, dann wieder jemand anders) — aber alles als ein Sprecher gelabelt
3. Kontextuelle Hinweise im Text: "Hallo, ich bin der/die …" mit verschiedenen Namen, alle einem Sprecher zugeordnet

**Vorgehen bei unverlässlichen Tags:**

- Setze `speaker_verlaesslich: false`
- Bei `stakeholder_kunde`: leite die Personen aus dem **Inhalt** ab (Vorstellungsrunden im Text), nicht aus den Speaker-Tags
- Bei einzelnen Aussagen: gib `quelle_turn` weg oder ergänze "(Sprecher unsicher)"
- Im Body unter "Offene Punkte" Notiz: *"Speaker-Erkennung im Transkript war unsauber. Zuordnungen zu Personen ggf. prüfen."*

## Feld-spezifische Extraktion

### Ziele

Suche nach Formulierungen wie:
- "Wir wollen …", "Unser Ziel ist …", "Wir möchten erreichen …"
- "Es geht uns darum …"
- "Die nächsten 12 Monate / 2 Jahre wollen wir …"

Im **Verkaufsgespräch** oft schwach ausgeprägt — der Kunde sagt eher *Schmerz* als *Ziel* ("Aktuell läuft das nicht gut, weil …"). Wandele Schmerz in Ziel um: "schlechte Online-Sichtbarkeit" → Ziel = "Sichtbarkeit erhöhen", Typ = `branding`, markiere als `unklar_aus_transkript: true` weil der Kunde es nicht explizit als Ziel formuliert hat.

### USPs (eigenwahrnehmung)

Nur was der **Kunde selbst** sagt, nicht was die Agentur paraphrasiert. Typische Formulierungen:

- "Wir sind die einzigen, die …"
- "Was uns von anderen unterscheidet ist …"
- "Unsere Stärke ist …"
- Indirekt: "Im Gegensatz zu denen, die …, machen wir …"

**Wichtig**: Wenn ein Stratege fragt "Wäre euer USP also X?" und der Kunde nur mit "Genau" oder "Ja" antwortet, kannst du das als USP aufnehmen, aber den `beleg` muss das **gesamte Frage-Antwort-Paar** enthalten, damit der Stratege später sieht, dass es eine bestätigte (nicht spontan genannte) Eigenwahrnehmung war.

Beispiel:
```yaml
usps_kunde_eigenwahrnehmung:
  - usp: "Premium-Qualität als Differenzierung gegen asiatische Billig-Anbieter"
    beleg: "Stratege: 'Eure Stärke ist also Premium-Qualität?' Kunde: 'Ja, genau, wir müssen uns über Premium-Qualität und Markenversprechen absetzen.'"
    quelle_turn: "11:33"
```

### Wettbewerber

Vier Kategorien zu unterscheiden:

1. **Direkter Wettbewerb** ("Schmidt Hausverwaltung hat uns letzten Monat einen Mandanten weggenommen") → `direkt`
2. **Indirekter Wettbewerb** ("Online-Hausverwaltungen wie X wachsen, das beobachten wir") → `indirekt`
3. **Inspiration** ("Schau dir Firma Y an, die machen ihr Online-Marketing wirklich gut") → `inspiration`
4. **Plattformen / Aggregatoren** (Amazon für Casafan, Booking für Hotels) — separat behandeln: nicht als Wettbewerber im klassischen Sinn, sondern als Vertriebskanal. Wenn Kunde sie als Bedrohung erwähnt ("Wir verlieren Margin an Amazon-Händler"), dann `indirekt` mit Kontext-Hinweis.

### Tools des Kunden

Häufig erwähnt, aber selten klar bestätigt. Achte auf:

- **CRM**: HubSpot, Salesforce, Pipedrive, "wir haben kein CRM", "wir benutzen Excel"
- **Analytics**: GA4, "Google Analytics", "Matomo", "haben wir nicht eingerichtet"
- **Ads**: Google Ads, Meta, "schalten gar keine"
- **CMS**: WordPress, Shopify, "haben eine neue Website mit Quokka", "eigene Lösung"
- **Sonstige**: Newsletter (Mailchimp, Brevo, Sendinblue), Tracking (GTM, Consent-Tools)

Wenn der Status unklar ist (Tool erwähnt, aber nicht klar, ob aktiv genutzt), setze `status: unklar` — das geht in die `offene_punkte`-Liste.

### Budget

Selten beziffert. Achte auf:

- Konkrete Zahlen ("ca. 5k im Monat", "20k im Jahr für Marketing")
- Relative Aussagen ("die aktuelle Pauschale ist mir zu hoch", "wir haben da Spielraum")
- Constraints ("kein Performance-Budget verfügbar", "Aufsichtsrat muss zustimmen")

Bei Verkaufsgesprächen oft komplett offen — dann leer lassen, nicht raten.

### Stakeholder (Kunde)

Aus dem Inhalt ableiten, nicht (nur) aus Speaker-Tags. Vorstellungsrunden sind die Goldquelle. Rollen-Klassifikation:

- "Geschäftsführer / CEO / Inhaber / Vorstand" → `Geschäftsführung`
- "Marketing-Manager / -Leitung / Werbeleitung" → `Marketing`
- "Vertriebsleiter / Sales / Vertrieb" → `Vertrieb`
- "IT-Leitung / CTO / Webmaster" → `IT`
- Andere (HR, Finanzen, Compliance, externe Berater) → `Sonstige`

**Aussagekraft** (`hoch | mittel | niedrig`):
- `hoch` → spricht substanziell über mehrere relevante Themen, trifft Entscheidungen
- `mittel` → trägt operativ bei, beantwortet Fachfragen
- `niedrig` → nur kurz dabei, hauptsächlich Beobachter-Rolle

## Off-Topic-Filter

Das, was du wegfiltern darfst (kein Briefing-Wert):

- Small Talk zu Beginn ("Wer ist alles da?", "Schaffen wir das mit dem WLAN?")
- Tool-Probleme ("Fireflies zulassen", "Kannst du mich hören?")
- Pausen-Diskussionen ("Soll ich mir Kaffee holen?")
- Off-Topic-Rückblicke auf andere Projekte, die nichts mit der aktuellen MTA zu tun haben
- Per-Sie-vs-Per-Du-Diskussionen

**Wichtig**: filtere *aus der Extraktion*, nicht aus dem Transkript selbst (das bleibt unverändert im Original-Pfad). Dein Output ist nur das `briefing.md`.

## Pflicht-Output bei niedriger Dichte

Wenn `inhaltliche_dichte: niedrig` oder >3 Felder als `unklar_aus_transkript: true`:

Schreibe **prominent unter "Offene Punkte"** im Markdown-Body eine Notiz wie:

```markdown
## Offene Punkte

⚠ **Empfehlung an den Strategen:** Das Briefing weist mehrere Lücken auf, die vor weiteren MTA-Schritten geklärt werden sollten:

- Konkrete KPIs / Zielwerte (im Transkript nur grobe Richtung)
- Aktuelles Marketing-Budget (nicht beziffert)
- Stand des CRM/Analytics-Setups beim Kunden (unklar)
- Wettbewerbs-Positionierung aus Kundensicht (nur Plattformen genannt, keine direkten Konkurrenten)

Vor dem nächsten Skill (`02-01-kunden-marken-profil` oder `02-02-wettbewerber-identifikation`) empfehlen wir eine kurze Rückfrage-Runde mit dem Kunden — gerne per E-Mail mit den oben genannten Punkten.
```

Diese Notiz wird auch im HTML-Report sichtbar als Suggestion-Block und im Chat-Schluss-Format als "Offene Punkte"-Sektion.
