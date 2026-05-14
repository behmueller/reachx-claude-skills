# Portale-Output-Schema (`wettbewerber/portale.md`)

Format der Output-Datei von `02-04-branchenportal-recherche`. Die Datei dokumentiert die Portal-mal-Akteur-Recherche und ist Input für die Synthese-Skills.

Liegt im Projekt unter `wettbewerber/portale.md`. Format: Markdown mit YAML-Frontmatter.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 02-04-branchenportal-recherche
generiert_am: <ISO-8601>
schema_version: "1.0"

# === Recherche-Provenienz ===
basiert_auf:
  identifikations_schema: wettbewerber/identifikation-schema.md
  identifikations_schema_bestaetigt_am: <ISO-8601>
  liste: wettbewerber/liste.md
  liste_bestaetigt_am: <ISO-8601>
  kunde_md_vorhanden: <true | false>

recherche_durchgefuehrt:
  methoden_mix:
    - methode: A
      portale_count: 3
    - methode: B
      portale_count: 4
    - methode: C
      portale_count: 1
    - methode: D
      portale_count: 0
  tasks_total: <int>     # Akteure × Portale
  tasks_erfolgreich: <int>
  tasks_fehlgeschlagen: <int>

# === Portal-Stammdaten ===
# Übernommen aus identifikation-schema.md, plus konkrete Recherche-Methode aus portal-scraper-mapping.md
portale:
  - portal_slug: <kebab-case-slug, z.B. "jameda" oder "proven-expert">
    portal_name: <Portal-Anzeigename, z.B. "jameda.de">
    portal_url: <Haupt-URL>
    typ: <Bewertungsportal | Verzeichnis | Marktplatz | Termin-Plattform | OTA | sonstige>
    relevanz_im_schema: <hoch | mittel | niedrig>
    reach: <lokal | regional | national | dach | international>
    touchpoint_charakter: <reputation | lead | reputation_und_lead | branding>
    recherche_methode: <A | B | C | D | B_fallback>
    recherche_quelle: <Apify-Actor-Name | Web-Search | Puppeteer-Custom | manuell>
    skala_score: <z.B. "1-5 Sterne" oder "1.0-6.0 Note" oder "0-10 Score">

# === Akteurs-Stammdaten ===
# Aus meta.json (Kunde) und liste.md (Wettbewerber)
akteure:
  - akteurs_slug: <kebab-case-slug>
    name: <Anzeigename>
    typ: <kunde | wettbewerber>
    website: <URL oder null>
    kategorie_wenn_wettbewerber: <kunde_genannt | regional | best_practice_ueberregional | null>

# === Recherche-Matrix ===
# Pro (Portal, Akteur) ein Eintrag
matrix:
  - portal_slug: <slug>
    akteurs_slug: <slug>
    status: <aktiv | gelistet_ruhend | nicht_gelistet | unklar | recherche_fehlgeschlagen>
    profil_url: <vollständige URL oder null>
    score:
      wert: <float oder null>
      skala: <z.B. "1-5" oder "1.0-6.0 (1 ist beste)" oder "0-10">
    reviews_count: <int oder null>
    letzte_aktivitaet:
      datum: <ISO-8601 oder null>
      typ: <letzte_review | letzte_inhaber_antwort | letztes_inserat | profil_update | unbekannt>
    portal_spezifische_felder:
      # z.B. für ProvenExpert: premium_status, empfehlungen_aggregat
      # z.B. für TripAdvisor: ranking_in_stadt, auszeichnungen
      # z.B. für G2: g2_grid_position, awards
      <key>: <value>
    recherche_methode_angewendet: <A | B | C | B_fallback>
    fehler_typ: <null | login_wall | portal_unreachable | name_konflikt | timeout | unbekanntes_portal>
    notiz: <freier Text, z.B. bei name_konflikt welche Kandidaten geprüft wurden>

# === Aggregat-Statistiken (für Dashboard) ===
statistiken:
  coverage_total_prozent: <float>   # % aller (Portal, Akteur)-Kombinationen mit Status aktiv ODER gelistet_ruhend
  coverage_kunde_prozent: <float>   # nur die Kunden-Zeile
  coverage_wettbewerber_durchschnitt_prozent: <float>
  portal_mit_hoechster_coverage: <portal_slug>
  portal_mit_niedrigster_coverage: <portal_slug>

# === Auffälligkeiten ===
auffaelligkeiten:
  - typ: <kunde_luecke | kunde_ruhend | kunde_stark | portal_sattigung | premium_verteilung | sonstige>
    titel: <kurzer Titel>
    beschreibung: <ein bis zwei Sätze>
    relevanz: <hoch | mittel | niedrig>
    handlungs_empfehlung: <konkrete Aktion für die MTA-Slide>
    betroffene_portale: [<liste der portal_slugs>]
    betroffene_akteure: [<liste der akteurs_slugs>]
---

# Branchenportal-Recherche: <Kundenname>

## Übersicht

Kompakte Zusammenfassung der Recherche-Statistiken — Methoden-Mix, Coverage-Indikatoren, größte Auffälligkeiten in 2-3 Sätzen.

## Methodisches Vorgehen

Pro Portal eine kurze Notiz: welche Methode angewendet wurde, ggf. Fallback-Begründung. Damit kann der Stratege bei Rückfragen oder Wiederholbarkeit nachvollziehen, wie die Daten zustande kamen.

## Portal A — <Portal-Name>

(Pro Portal eine eigene Sektion)

Kurz-Charakterisierung des Portals (1 Satz, aus den Stammdaten).

| Akteur | Status | Score | Reviews | Letzte Aktivität | Profil-URL |
|---|---|---|---|---|---|
| Kunde | aktiv | 4.3/5 | 87 | 2026-04-12 | … |
| Wettbewerber 1 | aktiv | 4.5/5 | 142 | 2026-05-01 | … |
| Wettbewerber 2 | gelistet_ruhend | 4.1/5 | 23 | 2024-11-08 | … |
| Wettbewerber 3 | nicht_gelistet | — | — | — | — |

**Beobachtung**: kurze 1-2-Satz-Analyse über dieses Portal (z. B. "Marktführer hat hier eine sehr starke Reputation, Kunde liegt im Mittelfeld, ein WB hat das Portal verschlafen.")

## (weitere Portale …)

## Auffälligkeiten

Strategisch relevante Beobachtungen über alle Portale hinweg. Aus dem Frontmatter `auffaelligkeiten` als Markdown gerendert.

### <Auffälligkeit 1 — Titel>

Beschreibung. Konkrete Handlungs-Empfehlung für die MTA-Slide.

Betroffene Portale: …
Betroffene Akteure: …

## Recherche-Lücken

Tasks, die nicht erfolgreich abgeschlossen werden konnten — als To-Do für den Strategen, ggf. manuell nachprüfen.

| Portal | Akteur | Fehler-Typ | Hinweis |
|---|---|---|---|
| Portal-X | WB-3 | login_wall | manuelle Recherche durch Strategen empfohlen |
| Portal-Y | WB-1 | name_konflikt | drei Kandidaten gefunden — Stratege wählt |
```

## Feld-Erläuterungen

### `status` (Matrix-Eintrag)

Fünf Werte, eindeutig:

- **`aktiv`** — Profil existiert UND mindestens eine Aktivität in den letzten 6 Monaten (neue Review, Antwort des Akteurs, Profil-Update, neue Inserate, Termin-Verfügbarkeit)
- **`gelistet_ruhend`** — Profil existiert, aber keine Aktivität in den letzten 6 Monaten
- **`nicht_gelistet`** — Akteur auf diesem Portal nicht gefunden
- **`unklar`** — Profil teilweise gefunden, aber Aktivitäts-Datum nicht eindeutig extrahierbar
- **`recherche_fehlgeschlagen`** — Recherche selbst ist gescheitert (Login-Wall, Timeout, Portal offline). Unterscheidet sich von `nicht_gelistet`: bei `nicht_gelistet` wurde die Suche erfolgreich durchgeführt und kam ohne Treffer zurück, bei `recherche_fehlgeschlagen` konnte die Suche nicht zuverlässig ausgeführt werden.

### `score.skala`

**Wichtig**: Portal-Score-Skalen werden NICHT normalisiert. Die rohe Portal-Skala bleibt erhalten, damit der Stratege Vergleichbarkeit innerhalb eines Portals direkt ablesen kann. Beispiele:

- Jameda: `1.0-6.0 (1 ist beste)` — Schul-Notensystem
- ProvenExpert: `1.0-5.0` — höher ist besser
- TripAdvisor: `1-5 Punkte`
- Trustpilot: `0-5 TrustScore`
- Booking.com: `1-10` — höher ist besser
- G2: `1-5 Sterne`

Normalisierung über Portale hinweg ist Aufgabe der Synthese-Skills (z. B. `04-02-kanal-chancen-analyse`).

### `portal_spezifische_felder`

Frei-strukturiertes Feld pro Portal-Typ. Beispiele:

**ProvenExpert:**
```yaml
portal_spezifische_felder:
  premium_status: gold
  empfehlungen_aggregat: 247
  aggregierte_portale: ["google", "facebook"]
```

**TripAdvisor:**
```yaml
portal_spezifische_felder:
  ranking_in_stadt: 12
  ranking_gesamt: "12 von 87 Restaurants in Frankfurt"
  auszeichnungen: ["Travelers Choice 2025"]
```

**G2:**
```yaml
portal_spezifische_felder:
  g2_grid_position: "High Performer"
  awards: ["Best Support Spring 2026", "Easiest to Do Business With Spring 2026"]
```

**Google Business Profile:**
```yaml
portal_spezifische_felder:
  kategorien: ["Hausverwaltung", "Immobilienverwaltung"]
  foto_anzahl: 24
  oeffnungszeiten_aktuell: true
  inhaber_antwort_rate_prozent: 73
```

### `auffaelligkeiten[*].typ`

Vorgegebene Typen, damit der Bundle-Report sie kategorisieren kann:

- **`kunde_luecke`** — Kunde fehlt, mindestens 2 WBs sind aktiv → MTA-Empfehlung "Profil anlegen"
- **`kunde_ruhend`** — Kunde gelistet_ruhend, mindestens 1 WB aktiv → MTA-Empfehlung "Profil reaktivieren"
- **`kunde_stark`** — Kunde aktiv mit signifikant besseren Werten als WB-Durchschnitt → MTA-Story "wir haben hier den Lead"
- **`portal_sattigung`** — alle Akteure ähnlich gut auf einem Portal → kein Differenzierungs-Hebel über reines Listing
- **`premium_verteilung`** — Premium-/Gütesiegel-Verteilung ist auffällig (z. B. nur 1 WB hat Premium, oder alle, oder keiner) → Story für Reputation-Audit-Slide
- **`sonstige`** — alles andere; Skill formuliert Titel und Beschreibung selbst

### `auffaelligkeiten[*].relevanz`

Wichtig für den HTML-Report — nur `hoch` wird prominent angezeigt, `mittel` ist normal sichtbar, `niedrig` standardmäßig zugeklappt.

## Wie Synthese-Skills diese Datei lesen

- **`04-02-kanal-chancen-analyse`**: liest `auffaelligkeiten` für die Branchenportal-Kanal-Bewertung, plus die Coverage-Statistiken
- **`04-01-positionierungs-analyse`**: liest aktuell **nicht** aus dieser Datei (Marken-Profile sind die Basis), aber kann optional Premium-Status als Reputation-Signal aufnehmen
- **`04-05-90-tage-plan`**: liest die `auffaelligkeiten` mit `handlungs_empfehlung` als Quick-Wins (z. B. "ProvenExpert-Profil anlegen" als 1-Tages-Task)

## Validierungs-Regeln

Vor dem Schreiben der Datei prüft der Skill:

1. Jede (Portal, Akteur)-Kombination aus dem Schema hat genau einen Matrix-Eintrag
2. Jeder Matrix-Eintrag hat `status` gesetzt
3. Bei `status: aktiv` oder `gelistet_ruhend`: `profil_url` darf nicht `null` sein
4. Bei `status: recherche_fehlgeschlagen`: `fehler_typ` muss gesetzt sein
5. Jede `auffaelligkeit` hat `typ`, `titel`, `relevanz`, `handlungs_empfehlung`

Wenn eine Regel verletzt wird, korrigiert der Skill den Eintrag oder gibt im Schluss-Format konkret an, welcher Eintrag fehlerhaft ist.
