# Marken-Profil-Schema (`data/kunde.md` und `wettbewerber/<slug>.md`)

Dieses Schema gilt **identisch** für Kunde und Wettbewerber. So können Synthese-Skills (z. B. `04-01-positionierungs-analyse`) später strukturell vergleichen.

Liegt im Projekt-Root unter `data/kunde.md` für den Kunden, oder unter `wettbewerber/<slug>.md` für jeden Wettbewerber. Format: Markdown mit YAML-Frontmatter.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 02-01-kunden-marken-profil       # oder 02-03-wettbewerber-marken-profil
generiert_am: <ISO-8601>
schema_version: "1.0"
quelle:
  website_url: <vollständige URL inkl. Protokoll>
  crawl_actor: <z.B. apify/website-content-crawler>
  crawl_durchgefuehrt_am: <ISO-8601>
  seiten_gecrawlt: <int>
  hauptsprache_detektiert: <de | en | … >
  crawl_hinweise: [<liste etwaiger Probleme: Cookie-Wall, SPA-Rendering-Issues, …>]

# === Marken-Identität ===
marke:
  name: <Markenname>
  synonyme: [<liste alternativer Schreibweisen, Kürzel, etc.>]
  claim: <Haupt-Claim auf der Startseite, falls erkennbar>
  logo_pfad: <relativer Pfad zu assets/<slug>-logo.png falls extrahiert>

# === Portfolio (wie auf der Website kommuniziert) ===
portfolio_wie_kommuniziert:
  - name: <Produktname / Dienstleistung>
    beschreibung: <wie die Website es beschreibt>
    kategorie: <Hauptkategorie aus Sicht der Website>
    quelle_url: <relative URL auf der Website>

# === USPs wie auf der Website kommuniziert ===
usps_wie_kommuniziert:
  - usp: <Kerndifferenzierung>
    beleg: <Zitat von der Website, unter 25 Wörter>
    quelle_url: <relative URL>

# === Zielgruppen-Hypothese aus der Website ===
zielgruppen_hypothese_aus_website:
  - persona: <Persona-Beschreibung>
    segment: <B2B | B2C | beide>
    begruendung: <warum diese Persona aus Website-Inhalten abgeleitet>
    belege: [<liste mit zitierten Indikatoren>]

# === Tonalität ===
tonalitaet:
  formell_vs_informell:
    achse_wert: <-2 | -1 | 0 | 1 | 2>   # negativ = formell, positiv = informell
    achse_label: <Kurzbeschreibung der konkreten Position auf der Achse>
    belege: [<liste 2–3 kurzer Zitate>]
  expertise_vs_partnerschaftlich:
    achse_wert: <-2 .. 2>   # negativ = expertise-zentriert, positiv = partnerschaftlich
    achse_label: <…>
    belege: [<…>]
  sachlich_vs_emotional:
    achse_wert: <-2 .. 2>   # negativ = sachlich, positiv = emotional
    achse_label: <…>
    belege: [<…>]
  modern_vs_traditionell:
    achse_wert: <-2 .. 2>   # negativ = modern, positiv = traditionell
    achse_label: <…>
    belege: [<…>]

# === Hero-Test (Donald-Miller-Methodik) ===
hero_test:
  was_wird_angeboten:
    score: <1 .. 5>    # 5 = sofort klar, 1 = nicht erkennbar
    begruendung: <kurz, warum dieser Score>
    sichtbar_in_sekunden: <int>
  fuer_wen:
    score: <1 .. 5>
    begruendung: <…>
    sichtbar_in_sekunden: <int>
  was_ist_anders:
    score: <1 .. 5>
    begruendung: <…>
    sichtbar_in_sekunden: <int>
  wie_weiter_cta:
    score: <1 .. 5>
    begruendung: <…>
    sichtbar_in_sekunden: <int>
  gesamt_score: <1 .. 5>   # Mittelwert oder gewichteter Wert
  screenshot_pfad: <relativer Pfad zu assets/<slug>-startseite.png>

# === Verständlichkeit der Startseite ===
verstaendlichkeit_startseite:
  score: <1 .. 5>
  schwachstellen: [<liste konkreter Schwachstellen>]
  staerken: [<liste konkreter Stärken>]

# === Touchpoints ===
touchpoints_gefunden:
  - typ: <website | subdomain | linkedin | instagram | tiktok | youtube | facebook | pinterest | gmb | branchenportal | newsletter | app | sonstige>
    url: <vollständige URL>
    bezeichnung: <z.B. Profil-Name auf Plattform>
    aktivitaets_indikator: <aktiv | ruhend | unklar>   # rein optische Einschätzung aus dem Link-Kontext

# === Übergreifende Qualitäts-Indikatoren ===
crawl_vollstaendig: <true | false>
crawl_luecken: [<liste was nicht erreichbar oder unklar war>]
```

## Body-Struktur (Markdown)

```markdown
# Marken-Profil: <Markenname>

## Übersicht

3–5 Sätze: wer ist die Marke, was bietet sie an, an wen, mit welcher Haltung. Spiegelung der Eigenwahrnehmung wie sie auf der Website rüberkommt.

## Portfolio

Strukturierte Darstellung der oben im Frontmatter aufgelisteten Produkte/Dienstleistungen.

## USPs (wie kommuniziert)

USPs aus der Website mit Belegen.

## Zielgruppen

Aus Website-Inhalten abgeleitete Zielgruppen-Hypothese, mit Belegen.

## Tonalität

Vier-Achsen-Bewertung mit Belegen.

## Hero-Test

Bewertung der Startseite nach den vier Donald-Miller-Fragen. Mit Screenshot-Verweis.

## Touchpoints

Liste der gefundenen Touchpoints.

## Lücken und Hinweise

Was beim Crawl nicht erreicht wurde, wo Datenlage dünn ist.
```

## Feld-Erläuterungen

### `marke.synonyme`

Wichtige Liste für später: Suchverhalten in Sistrix nutzt Marken-Synonyme. "REACHX" und "Reach X" und "ReachX" sind drei Varianten, die wir alle erfassen müssen für Brand-Search-Volumen.

### `portfolio_wie_kommuniziert` vs. Briefing

**Wichtig:** Hier steht nur, was die *Website* sagt — nicht, was der Kunde im Briefing erzählt hat. Abweichungen zwischen beiden landen in `data/abweichungen.md` (eigene Datei, eigener Skill-Output).

### `tonalitaet.achse_wert`

Skala -2 bis +2:

- `-2` = stark in Richtung linke Achse (z. B. sehr formell)
- `-1` = leicht in Richtung linke Achse
- `0` = neutral / ausgewogen
- `+1` = leicht in Richtung rechte Achse
- `+2` = stark in Richtung rechte Achse (z. B. sehr informell)

Jede Achse-Bewertung **muss 2–3 konkrete Belege** als Zitate haben (unter 25 Wörter pro Beleg). Ohne Belege ist die Achse nicht bewertbar — dann `achse_wert: null` und Hinweis in `crawl_luecken`.

### `hero_test`

Vier-Fragen-Methodik nach Donald Miller. Jede Frage einzeln bewertet (1 = nicht erkennbar, 5 = sofort klar), plus geschätzte Zeit in Sekunden, in der die Antwort sichtbar wird.

`gesamt_score`: Mittelwert der vier Einzel-Scores. Wenn eine Frage mit 1 bewertet ist und drei mit 4, ist das Mittel 3,25 — aber im Body sollte explizit benannt werden, **welche Frage** durchgefallen ist (das ist meist die wertvollere Information für den Strategen).

### `verstaendlichkeit_startseite`

Eigene Dimension, **getrennt vom Hero-Test**. Der Hero-Test prüft *was* erkennbar ist, die Verständlichkeit prüft *wie gut* es kommuniziert ist:

- Klare Hierarchie der Informationen?
- Fachsprache angemessen für Zielgruppe?
- Längere Texte verständlich gegliedert?
- Visuelle Klarheit (Whitespace, Lesbarkeit)?
- CTAs klar erkennbar als CTAs?

### `touchpoints_gefunden`

Wo werden Touchpoints gefunden?

- **Im Footer**: meist Social-Links, GMB-Verlinkung
- **Im Header**: Login-Bereiche, App-Stores
- **In Newsletter-Footer-Anker**: Newsletter-Anmeldungen
- **In Contact-Pages**: GMB-Verweise, Branchenportal-Links
- **In Press-/About-Pages**: Erwähnungen externer Plattformen

Subdomains nur einfangen, wenn sie in den gecrawlten Seiten verlinkt sind. Vollständige Subdomain-Inventur erst in einem späteren Audit (`03-14-web-tech-und-tracking` mit SimilarWeb).
