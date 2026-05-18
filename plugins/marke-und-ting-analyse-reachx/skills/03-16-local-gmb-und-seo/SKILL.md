---
name: 03-16-local-gmb-und-seo
description: Local-SEO-Audit für lokale Akteure einer MTA - prüft pro Akteur (Kunde plus regionale Wettbewerber) das Google-My-Business-Profil (Vollständigkeit, Rating, Review-Sentiment, Antwort-Quote, Post-Aktivität, Kategorie), die Local-Pack-Rankings pro Standort mal Service-Keyword und die NAP-Konsistenz (Name, Adresse, Telefon) zwischen GMB, Website-Impressum und Branchenportalen. Nutzt Schema-vor-Lauf - Phase A schlägt Standorte, Suchradius, Local-Pack-Keywords und Review-Themen vor, Stratege bestätigt, Phase B scrapt via Apify Google-Maps-Scraper. Skip in Phase A wenn Kunde national/online ist (kein Local-Bezug), Override "trotzdem laufen" möglich. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext lokale Sichtbarkeit, Google My Business, Maps-Rankings oder NAP-Konsistenz prüfen will - auch bei "GMB-Audit", "Local-SEO-Check", "Google-My-Business-Profil prüfen", "Local-Pack-Rankings", "NAP-Konsistenz", "lokale Sichtbarkeit", "Maps-Rankings", "GMB-Reviews analysieren", "lokale Wettbewerbs-Analyse".
---

# GMB- und Local-SEO-Audit

Local-SEO-Audit-Skill in Stufe 3. **Schema-vor-Lauf-Pattern** (siehe `contracts.md` Abschnitt 8). Prüft pro Akteur die lokale Online-Präsenz auf drei Achsen:

1. **GMB-Profil-Qualität** — Vollständigkeit, Rating, Anzahl Reviews, Review-Sentiment entlang branchen-typischer Themen, Antwort-Quote, Post-Aktivität, Kategorie-Korrektheit
2. **Local-Pack-Rankings** — pro Standort × Service-Keyword (mit Stadtteil-/Stadt-Modifier) die Position im Google Maps Local Pack
3. **NAP-Konsistenz** — Name/Address/Phone Cross-Check zwischen GMB, Website-Impressum, und (falls vorhanden) Branchenportalen aus `wettbewerber/portale.md`

Der Skill ist **gestaffelt-optional**: läuft nur sinnvoll für Kunden mit Local-Bezug (lokale Dienstleister, regionale B2B-Mittelständler mit Filialen, lokal-organisierte Handwerks- oder Hospitality-Marken). Bei rein nationalen oder Online-Akteuren bricht der Skill in Phase A mit Hinweis ab — der Stratege kann mit Override-Argument `trotzdem laufen` zwingen.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf MCPs/APIs, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Transkript-Pfad, Wettbewerber-Liste)
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

## Wann triggern

- "GMB-Audit"
- "Local-SEO-Check"
- "Google-My-Business-Profil prüfen"
- "Local-Pack-Rankings ziehen"
- "NAP-Konsistenz prüfen"
- "Lokale Sichtbarkeit auditieren"
- "Maps-Rankings vergleichen"
- "GMB-Reviews analysieren"
- "Lokale Wettbewerbs-Analyse"
- Nutzer fragt im MTA-Kontext nach Local-SEO

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden (`region` ist Pflichtfeld)
- **Stark empfohlen**: `02-02-wettbewerber-identifikation` mit `status: bestaetigt` → `wettbewerber/liste.md` enthält Kategorie `regional`
- **Empfohlen**: `02-01-kunden-marken-profil` → `data/kunde.md` mit `touchpoints_gefunden` (GMB-Link, Filialen)
- **Optional**: `02-04-branchenportal-recherche` → `wettbewerber/portale.md` für NAP-Cross-Check
- **Optional**: `data/briefing.md` für vom Kunden genannte Standorte
- **Apify-Zugang (Pflicht für Phase B)** — Actor-Auswahl in `reference/local-tools-mapping.md` (mit `zuletzt_getestet`-Datum und `status`). Credential-Prüfung: ausschließlich `[ -n "$APIFY_TOKEN" ]` — kein Scannen von `~/.zshrc` o. ä. (contracts.md Abschnitt 11). Vor dem ersten echten Scrape Apify-Health-Check via `mcp__apify__fetch-actor-details` für den verwendeten Actor: bei `Session ID not found` sofort abbrechen und Reconnect-Hinweis ausgeben, statt alle Akteure einzeln scheitern zu lassen.

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf prüft der Skill, ob `audits/local-gmb-schema.md` existiert und welchen Status sie hat.

### Phase-Entscheidungs-Logik (Schritt 1 bei jedem Aufruf)

Zuerst die Drive-Bootstrap (siehe `contracts.md` Abschnitt 1):

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
```

Schema und Outputs liegen auf Drive im `audits/`-Sub-Folder:

```
1. Existiert audits/local-gmb-schema.md auf Drive? (drive.py find_by_name "$AUDITS_ID" "local-gmb-schema.md")
   - Nein → Phase A (Schema generieren)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Review
   - Ja, status: bestaetigt → Phase B (eigentliches Audit)
   - Ja, status: skip_national_online → Skill ist bewusst geskippt, kein Lauf, Hinweis "Override mit trotzdem laufen möglich"
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert audits/local-gmb.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen: überschreiben / Backup-und-neu / abbrechen
```

### Skip-Logik (vor Phase A)

Aus `meta.json.branche`, `meta.json.region`, optional `data/kunde.md` und `wettbewerber/identifikation-schema.md.region_definition` ableiten:

- **Skip-Kandidat**: wenn `region_definition.ausdehnung` in {national, dach, international} UND keine GMB-Touchpoints in `data/kunde.md.touchpoints_gefunden` UND `wettbewerber/liste.md` enthält keine Kategorie `regional` (oder ist leer)
- **Override**: Wenn Nutzer-Argument `trotzdem laufen` (oder `force`) gesetzt ist, überspringe Skip-Logik

Bei Skip-Kandidat: schreibe `audits/local-gmb-schema.md` (lokal generieren, dann `drive.py upsert-text "$AUDITS_ID" "local-gmb-schema.md" /tmp/schema.md "text/markdown"`) mit `status: skip_national_online` und einer kurzen Begründung, lasse den Skill auf `schritte_done` setzen mit Vermerk "geskippt — kein Local-Bezug", aktualisiere `status.md` auf Drive, gib im Chat aus:

```
✗ 03-16-local-gmb-und-seo geskippt — kein Local-Bezug erkannt.

Begründung:
- Region-Definition: national/online
- Keine GMB-Touchpoints in data/kunde.md
- Keine regionalen Wettbewerber in wettbewerber/liste.md

Wenn das falsch ist (Kunde hat doch lokale Filialen oder lokales Service-Gebiet), Skill mit Argument "trotzdem laufen" erneut aufrufen.

Nächste Schritte:
1. <nächster relevanter Audit-Skill>

Sag mir, welcher als nächster.
```

---

## Phase A — Local-SEO-Schema generieren

### Schritt A.1: Projekt-Auffindung und Voraussetzungs-Check

Drive-Bootstrap wie oben. Lies aus Drive (`find_by_name` + `read_text`):

- `meta.json` (Pflicht — `region`, `branche`) — bereits in /tmp/meta.json
- `wettbewerber/liste.md` via `find_by_name(WB_ID, "liste.md")` (empfohlen — `status: bestaetigt`, Kategorie `regional`)
- `data/kunde.md` via `find_by_name(DATA_ID, "kunde.md")` (empfohlen — `touchpoints_gefunden` mit GMB-Link und Filialen)
- `data/briefing.md` via `find_by_name(DATA_ID, "briefing.md")` (empfohlen — vom Kunden genannte Standorte oder Service-Gebiet)

Wenn `meta.json` fehlt: Abbruch mit Hinweis "01-01-mta-projekt-init zuerst aufrufen".

Wenn `wettbewerber/liste.md` fehlt oder nicht bestätigt: Hinweis im Schema-Body, dass der Skill auf reduzierter Wettbewerbs-Basis läuft, aber weitermachen. Empfehlung im Body: erst `02-02-wettbewerber-identifikation` bestätigen, dann nochmal aufrufen.

### Schritt A.2: Skip-Bedingung prüfen

Wende die oben beschriebene Skip-Logik an. Bei Skip-Kandidat ohne Override: Schema mit `status: skip_national_online` schreiben, Skip-Schluss-Format ausgeben, kein Phase-A-Vollformat.

### Schritt A.3: Standorte des Kunden bestimmen

Quellen in Reihenfolge:

1. `data/kunde.md.touchpoints_gefunden` — GMB-Link extrahieren, daraus Hauptsitz-Adresse ziehen (sofern verlinkt)
2. Filialen aus `data/kunde.md.portfolio_wie_kommuniziert` oder `data/briefing.md.standorte` (falls dort genannt)
3. Branchen-Default: bei lokalen Dienstleistern (Arzt, Anwalt, Hausverwaltung, Handwerk) ein Hauptsitz; bei Filialisten (Restaurant-Ketten, Werkstätten, Studios) alle benannten Standorte
4. Manueller Ergänzungs-Vorschlag im Schema-Body: "Wenn weitere Filialen existieren, hier ergänzen"

Pro Standort: `name`, `adresse`, `plz`, `stadt`, optional `stadtteil`, optional `gmb_url` (falls bekannt).

### Schritt A.4: Suchradius festlegen

Default nach Branchen-Typ (siehe `reference/local-seo-schema-template.md`):

- Urbane Branchen mit hoher Dichte (Arzt, Anwalt, Restaurant, Café): `suchradius_km: 15`
- Ländliche oder spezialisierte Branchen (Hausverwaltung, Handwerk, Werkstatt): `suchradius_km: 25`
- Sehr spezialisierte Dienstleister (Kardiologe, Steuerberater für Branche X): `suchradius_km: 50`

Der Stratege kann im Review anpassen.

### Schritt A.5: Local-Pack-Keywords kuratieren

Aus den Quellen:

- `audits/seo-keywords.csv` oder `audits/seo-keyword-pool.csv` (falls SEO-Skills schon gelaufen sind) — Service-Keywords mit hoher kommerzieller Relevanz
- `wettbewerber/identifikation-schema.md.branchen_seed_keywords` — branchen-spezifische Service-Begriffe
- `data/kunde.md.portfolio_wie_kommuniziert` — Hauptservice-Kategorien

Kombiniere mit Stadt-/Stadtteil-Modifier:

```
local_pack_keywords:
  - basis: "zahnarzt"
    modifier_typen: [stadt, stadtteil, "in der nähe"]
    expansion:
      - "zahnarzt berlin"
      - "zahnarzt mitte"
      - "zahnarzt prenzlauer berg"
      - "zahnarzt in der nähe"
```

Faustregel: 5-10 Basis-Keywords × 2-3 Modifier-Typen = 10-30 Local-Pack-Queries pro Standort. Hard-Cap: 30 Queries pro Standort.

### Schritt A.6: Lokale Wettbewerber-Definition

Aus `wettbewerber/liste.md`:

- Alle Wettbewerber mit Kategorie `regional` direkt übernehmen
- Plus: in Phase B liefert Apify Google Maps Scraper automatisch lokale Wettbewerber pro Local-Pack-Query — die werden als "Sistrix-Local-Vorschläge" markiert und gegen die Strategen-Liste abgeglichen

Im Schema dokumentieren:

```
lokale_wettbewerber:
  aus_liste_md:
    - slug: muster-zahnarzt-mitte
      website: muster-zahnarzt.de
    - slug: ...
  ergaenzungen_aus_local_pack: in_phase_b
```

### Schritt A.7: Branchen-typische Review-Themen

Aus `reference/local-seo-schema-template.md` Branchen-Defaults laden — z. B.:

- **Arzt/Zahnarzt**: Wartezeit, Beratung, Freundlichkeit, Schmerzen, Preise, Sprechstundenhilfe, Erreichbarkeit
- **Restaurant**: Essen-Qualität, Service, Atmosphäre, Preise, Wartezeit, Reservierung
- **Handwerker**: Pünktlichkeit, Qualität, Preis-Leistung, Sauberkeit, Kommunikation, Rückrufe
- **Anwalt**: Beratung, Erfolg, Verständlichkeit, Honorar, Erreichbarkeit, Empathie
- **Hausverwaltung**: Erreichbarkeit, Reaktionszeit, Transparenz, Abrechnung, Hausmeister, Reparaturen
- **Werkstatt**: Reparatur-Qualität, Preis-Transparenz, Termin-Treue, Kommunikation, Sauberkeit, Ersatzteile

Stratege kann im Review ergänzen/streichen — die Themen steuern die Sentiment-Auswertung in Phase B (Cluster-Bildung über die Review-Texte).

### Schritt A.8: NAP-Cross-Check-Quellen

Pro Akteur in Phase B prüfen:

1. GMB-Profil (aus Apify-Scrape) — `name`, `adresse`, `telefon`
2. Website-Impressum (Apify Website-Content-Crawler auf `/impressum`, `/kontakt`)
3. Branchenportale aus `wettbewerber/portale.md` (falls vorhanden) — pro Portal die Profil-URL → Apify-Scrape oder Web-Search-Snippet

Quellen werden im Schema gelistet, damit der Stratege weiß, wo der Skill nachgucken wird.

### Schritt A.9: `audits/local-gmb-schema.md` nach Drive schreiben

Erzeuge das vollständige Schema lokal nach `reference/local-seo-schema-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "local-gmb-schema.md" \
  /tmp/local-gmb-schema.md "text/markdown"
```

Stratege kann die Datei direkt in Drive editieren und `status: bestaetigt` setzen.

Sektionen:

- **Frontmatter**: Skill-Metadaten, Anzahl Standorte, Anzahl Local-Pack-Keywords (gesamt), Anzahl regionale Wettbewerber, Anzahl Review-Themen
- **Body**:
  - Standorte des Kunden (Liste mit Adressen, GMB-Status)
  - Suchradius-Begründung
  - Local-Pack-Keywords pro Standort (mit Modifier-Typen und Expansion)
  - Lokale Wettbewerber-Liste
  - Branchen-typische Review-Themen
  - NAP-Cross-Check-Quellen
  - Pflicht-Review-Sektion mit konkreten Eingriffspunkten

### Schritt A.10: Schluss-Format Phase A

```
✓ 03-16-local-gmb-und-seo Phase A abgeschlossen.

Outputs (auf Drive):
- audits/local-gmb-schema.md — Local-SEO-Schema (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Standorte:              N (Hauptsitz plus M Filialen)
- Suchradius:             X km (Branchen-Default für BRANCHE)
- Local-Pack-Keywords:    K (über alle Standorte)
- Regionale Wettbewerber: W aus liste.md plus Auto-Ergänzung in Phase B
- Review-Themen:          T (branchen-typisch)
- NAP-Quellen:            GMB, Website-Impressum, Branchenportale

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Standorte vollständig? Suchradius passend? Local-Pack-Keywords sinnvoll kombiniert? Review-Themen branchen-relevant?
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Schreibe `blockiert` in `status.md` (aus Drive lesen, patchen, zurück via `drive.py upsert-text "$FOLDER_ID" "status.md"`):

```yaml
blockiert:
  - skill: 03-16-local-gmb-und-seo (Phase B)
    wartet_auf: "Strategen-Review von audits/local-gmb-schema.md (auf Drive)"
```

---

## Phase B — Eigentliches Local-SEO-Audit

### Schritt B.1: Schema-Validierung

Lies `audits/local-gmb-schema.md` aus Drive (`find_by_name(AUDITS_ID, "local-gmb-schema.md")` → `read_text`). Prüfe:

1. `status: bestaetigt`? Sonst Abbruch
2. Mindestens 1 Standort definiert?
3. Mindestens 3 Local-Pack-Keywords pro Standort?
4. Mindestens 3 Review-Themen?
5. Suchradius-Wert plausibel (5-100 km)?

Bei jedem Fehler: konkreter Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Akteurs-Liste zusammenstellen

Akteure für den Lauf:

- Kunde (immer dabei, alle Standorte)
- Regionale Wettbewerber aus `wettbewerber/liste.md` (Kategorie `regional`, `empfehlung_profilieren: ja`)
- Optional: in Phase B per Apify-Scan zusätzlich identifizierte lokale Wettbewerber, die im Local Pack auftauchen aber nicht in `liste.md` stehen → markieren als `auto_ergaenzt`, Auffälligkeit `local_wb_nicht_in_liste` werfen

Hard-Cap: max 10 Wettbewerber im Lauf (sonst Apify-Credits explodieren).

### Schritt B.3: GMB-Profil-Scrape pro Akteur

Per Apify Google Maps Scraper (siehe `reference/local-tools-mapping.md` für konkrete Actor-Auswahl):

Pro Akteur und Standort extrahieren:

- **Profil-Daten**: Name, Adresse, Telefon, Website, Kategorie(n), Öffnungszeiten, Service-Bereich (falls Service-Area-Business), Beschreibung
- **Medien**: Anzahl Fotos, Datum letztes Foto
- **Reviews**: Gesamt-Rating, Anzahl Reviews, Reviews-Sample (max 50, nach Datum absteigend) mit Text, Datum, Sterne, Antwort-Status
- **Posts (Updates)**: Anzahl Posts in den letzten 12 Monaten, Datum letzter Post
- **Q&A**: Anzahl Fragen, Anzahl beantworteter Fragen
- **Profil-Vollständigkeits-Check**: Telefonnummer vorhanden? Öffnungszeiten vorhanden? Mindestens 5 Fotos? Beschreibung mit ≥ 100 Zeichen? Service-Bereich definiert (falls relevant)?

Lokal cachen in `~/.cache/reachx-mta/<slug>/`, am Ende des Laufs nach Drive `assets/raw/gmb-SLUG.json` hochladen (SLUG = Akteurs-Slug, bei Filialen mit `-STANDORT` suffigiert).

### Schritt B.4: Review-Sentiment-Analyse

Pro Akteur:

1. Lade Reviews-Sample
2. Pro Review-Thema aus `gmb_review_themen`: Token-basiert + LLM-leichte-Klassifikation → Anzahl Reviews, die das Thema erwähnen, plus durchschnittliches Sterne-Rating dieser Reviews
3. **Negativ-Cluster-Erkennung**: wenn ein Thema in ≥ 5 Reviews mit Schnitt ≤ 3 Sterne erwähnt wird → Auffälligkeit `negativer_review_cluster`
4. **Antwort-Quote**: Anteil Reviews mit Inhaber-Antwort über alle Reviews (nicht nur Sample, falls Gesamt-Antwort-Quote aus GMB-Profil ableitbar)

Schreibe Reviews-Sample nach Drive: lokal in `~/.cache/reachx-mta/<slug>/gmb-reviews.csv` aufbauen, dann `drive.py upsert-text "$AUDITS_ID" "gmb-reviews.csv" ... "text/csv"`. Spalten: `akteur_slug`, `standort`, `review_id`, `datum`, `sterne`, `text`, `antwort_vorhanden`, `antwort_datum`, `themen_match` (Pipe-Liste).

### Schritt B.5: Local-Pack-Rankings

Pro Standort × Local-Pack-Keyword die Top-3 (Local Pack) und Top-10 (Maps-Ergebnisse) Positionen ziehen:

**Tool-Optionen** (siehe `reference/local-tools-mapping.md`):

1. **Apify Google-Maps-Local-Pack-Scanner** (bevorzugt, mit Geo-Koordinaten) — Lat/Lng des Standorts setzen, Keyword als Query → Top-10-Liste mit Position, Name, Adresse, Rating
2. **Local-Falcon-API** (Alternative, falls Apify-Actor nicht verfügbar oder unzureichend) — Grid-basiertes Local-Pack-Ranking-Tool, kostenpflichtig, präziser
3. **Web-Search-Fallback** (Reduced-Modus, wenn keines der obigen verfügbar) — manuelle Such-Snippets, weniger zuverlässig, nur Top-3-Local-Pack erfassbar

Pro Result-Zeile: `standort`, `keyword`, `position`, `akteur_slug` (matched gegen Akteurs-Liste, sonst `unbekannt`), `name`, `adresse`, `rating`, `rezensions_anzahl`.

Aggregation:

- **Kunden-Sichtbarkeit pro Standort**: in wie vielen Local-Pack-Queries ist der Kunde in Top-3? In Top-10?
- **Wettbewerber-Dominanz**: pro Wettbewerber die Anzahl Top-3-Platzierungen
- **Auffälligkeit `wettbewerber_dominiert_local_pack`**: wenn ein WB in ≥ 60% der Local-Pack-Queries in Top-3 ist und Kunde nicht → markieren

Schreibe nach Drive `audits/local-rankings.csv` (`drive.py upsert-text "$AUDITS_ID" "local-rankings.csv" ...`) und Cache lokal, am Ende nach Drive `assets/raw/local-rankings-SLUG.json` pro Standort.

### Schritt B.6: NAP-Konsistenz-Check

Pro Akteur:

1. GMB-NAP (aus Schritt B.3): `name_gmb`, `adresse_gmb`, `telefon_gmb`
2. Website-Impressum: Apify Website-Content-Crawler auf Akteur-Domain `/impressum`, `/kontakt`, dann Regex/LLM-Extraktion → `name_website`, `adresse_website`, `telefon_website`
3. Branchenportale aus `wettbewerber/portale.md` (falls vorhanden, pro Portal die in Schritt 3 hinterlegte Profil-URL): NAP-Felder extrahieren

Normalisierung:

- Telefon: alle Whitespaces, Bindestriche, Klammern raus, führende `+49` mit `0` ersetzen — dann String-Vergleich
- Adresse: Straße + Hausnummer + PLZ + Stadt normalisiert (Umlaute, Whitespaces, Abkürzungen wie "Str." vs "Straße")
- Name: Lowercase, GmbH-Suffix-Varianten als ähnlich werten (GmbH = GmbH & Co. KG ist nicht gleich, aber GmbH = Ges.m.b.H. ja)

Auffälligkeit `nap_inkonsistenz` wenn ≥ 2 Quellen abweichen für einen Akteur. Im Output pro Akteur die exakte Diff-Tabelle.

### Schritt B.7: GMB-Kategorie-Plausibilität

Pro Akteur die GMB-Kategorie(n) gegen `meta.json.branche` und `data/kunde.md.portfolio_wie_kommuniziert.kategorie` (für Kunde) bzw. Wettbewerber-Profil prüfen:

- Wenn Hauptkategorie nicht zur Branche passt (z. B. Kunde ist Zahnarzt, GMB-Kategorie ist "Geschäft") → Auffälligkeit `gmb_kategorie_falsch`
- Sub-Kategorien fehlen häufig — Hinweis als Soft-Auffälligkeit, kein Hard-Flag

### Schritt B.8: Auffälligkeiten konsolidieren

Mindestens diese Typen werden erkannt:

| Typ | Auslöser |
|---|---|
| `kunde_gmb_unvollstaendig` | Profil-Vollständigkeits-Score < 70% (z. B. fehlende Öffnungszeiten, < 5 Fotos, keine Beschreibung) |
| `kunde_review_quote_schwach` | Rating < 4.0 ODER Anzahl Reviews < 20 ODER (Anzahl Reviews < halb so viele wie Top-WB) |
| `kunde_keine_review_antworten` | Antwort-Quote < 30% |
| `kunde_keine_gmb_posts_seit_90_tagen` | Letzter Post älter als 90 Tage (oder keine Posts) |
| `wettbewerber_dominiert_local_pack` | Ein WB in ≥ 60% der Local-Pack-Queries pro Standort in Top-3 |
| `nap_inkonsistenz` | ≥ 2 Quellen weichen für einen Akteur ab (Name, Adresse oder Telefon) |
| `negativer_review_cluster` | Ein Review-Thema mit ≥ 5 Reviews und Schnitt ≤ 3 Sterne |
| `gmb_kategorie_falsch` | GMB-Hauptkategorie passt nicht zur Branche |
| `local_wb_nicht_in_liste` | In Local-Pack-Auswertung taucht WB häufig auf, der nicht in `wettbewerber/liste.md` ist |

Auffälligkeiten werden im Markdown und HTML-Report prominent ausgewiesen — Roh-Material für die MTA-Story.

### Schritt B.9: Aggregat-Markdown `audits/local-gmb.md` schreiben

Lokal generieren, dann `drive.py upsert-text "$AUDITS_ID" "local-gmb.md" /tmp/local-gmb.md "text/markdown"`. Body strukturiert nach:

- **Übersicht**: Akteurs-Anzahl, Standorte gesamt, Local-Pack-Queries durchgeführt, NAP-Quellen geprüft
- **Pro Akteur ein Block** (mit Sub-Blöcken pro Standort, falls mehrere):
  - GMB-Profil-Status (Vollständigkeit, Rating, Reviews, Antwort-Quote, Post-Aktivität)
  - Top-3-Review-Themen (positiv und negativ)
  - Local-Pack-Sichtbarkeit (Top-3- und Top-10-Quote pro Standort)
  - NAP-Diff-Tabelle (falls Inkonsistenz)
  - Pro-Akteur-Auffälligkeiten
- **Cross-Akteurs-Vergleich**: Heatmap-Tabelle Akteure × Local-Pack-Keywords (Position pro Akteur pro Keyword)
- **Pool-weite Auffälligkeiten** sortiert nach Relevanz

Frontmatter siehe `reference/local-output-schema.md`.

### Schritt B.10: HTML-Report `reports/14-gmb-local-seo.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

`_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), Platzhalter füllen, `drive.py upsert-text "$REPORTS_ID" "14-gmb-local-seo.html" ... "text/html"`. Aus `reports/_shell.html`:

- Stat-Strip: Akteure, Standorte, GMB-Vollständigkeit-Schnitt Kunde, Top-3-Quote Kunde, Anzahl Auffälligkeiten
- Sticky-TOC zu Akteuren plus Auffälligkeiten plus Cross-Vergleich
- Pro Akteur ein `<details data-rating>`-Block mit GMB-Profil-Karte, Reviews-Sentiment-Visualisierung, Local-Pack-Position-Tabelle
- **Local-Pack-Heatmap** Akteur × Keyword (Farbe = Position; Grün ≤ 3, Gelb 4-10, Rot > 10 oder nicht gefunden)
- NAP-Diff-Block (falls Inkonsistenzen)
- Auffälligkeiten als `.suggestion`-Block mit Handlungs-Empfehlung pro Auffälligkeit
- Footer

### Schritt B.11: Dashboard und status.md

- `03-16-local-gmb-und-seo` in `schritte_done`
- Aus `blockiert` entfernen
- Reports-Liste um `14-gmb-local-seo.html`
- Stat-Strip im Dashboard aktualisieren
- `naechster_empfohlen`: bei genug abgeschlossenen Audits `04-02-kanal-chancen-analyse`, sonst nächster offener Audit-Skill

### Schritt B.12: Standard-Schlussformat im Chat

```
✓ 03-16-local-gmb-und-seo Phase B abgeschlossen.

Outputs (auf Drive):
- audits/local-gmb.md — Aggregat pro Akteur mit Profil-Status, Sentiment, Auffälligkeiten
- audits/local-rankings.csv — Roh-Rankings pro Standort × Keyword × Akteur
- audits/gmb-reviews.csv — Reviews-Sample (max 50 pro Akteur)
- assets/raw/gmb-SLUG.json, assets/raw/local-rankings-SLUG.json — Roh-Caches
- reports/14-gmb-local-seo.html — visueller Report mit Heatmap
Status aktualisiert in: status.md

Local-SEO-Statistik:
- Akteure auditiert:          N (1 Kunde, M Wettbewerber)
- Standorte:                  S (Kunden-Standorte)
- Local-Pack-Queries:         Q (pro Standort durchschnittlich K)
- GMB-Vollständigkeit Kunde:  X%
- Top-3-Quote Kunde:          Y% der Local-Pack-Queries
- Antwort-Quote Kunde:        Z%
- NAP-Inkonsistenzen:         I (Akteure betroffen)

[Top 3 strategische Beobachtungen:]
⚠ Local-SEO-Insights:
1. Auffälligkeit 1
2. Auffälligkeit 2
3. Auffälligkeit 3

Nächste Schritte:
1. 03-20-local-gmb-wettbewerb — vertieft den lokalen Wettbewerbsvergleich (Review-Velocity, GMB-Profil-Reife, Local-Visibility-Score) — empfohlen, wenn die Local-SEO-Konkurrenz genauer eingeordnet werden soll
2. 04-02-kanal-chancen-analyse — synthetisiert Local-SEO mit den anderen Audits (sobald genug Audits da sind)
3. (parallel möglich, falls noch nicht durch) weitere Audit-Skills

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/local-seo-schema-template.md` — Phase-A-Output-Format inklusive Branchen-Defaults für Suchradius und Review-Themen
- `reference/local-tools-mapping.md` — Apify-Actor-Optionen, Local-Falcon-Option, Web-Search-Fallback inklusive Stärken-/Schwächen-Vergleich
- `reference/local-output-schema.md` — Phase-B-CSV- und Markdown-Schema mit Validierungs-Regeln

## Edge Cases

- **Kunde hat kein GMB-Profil** → harter Befund: Auffälligkeit `kunde_gmb_unvollstaendig` mit maximaler Severity, Hinweis im Body, dass das die Grundlage für ALLE Local-Visibility-Maßnahmen ist. Phase B läuft trotzdem für die Wettbewerber.

- **Kunde ist Service-Area-Business** (kein physisches Ladengeschäft, sondern Service-Gebiet wie Handwerker) → Adresse im GMB-Profil ist versteckt, Service-Area-Polygone werden geprüft. Schema-Template hat dafür ein eigenes Standort-Format `service_area: true`.

- **Apify-Google-Maps-Scraper liefert keine Reviews** (Rate-Limit, Bot-Erkennung) → Reduced-Modus: nur Profil-Daten plus aggregiertes Rating, keine Sentiment-Analyse. Auffälligkeit `review_scrape_unvollstaendig` mit Hinweis im Body.

- **Local-Pack zeigt für ein Keyword keinen Local Pack** (Google entscheidet kontextabhängig, ob Local Pack eingeblendet wird) → Result-Zeile mit `position: null`, `pack_eingeblendet: false`. Im Aggregat als eigener Bucket "ohne Local Pack" ausweisen.

- **NAP-Quellen nicht erreichbar** (Impressum hat keine strukturierte Form, Branchenportal-Profil blockiert Bot) → Fallback: nur GMB-vs-Website-Vergleich, Branchenportale weglassen, Hinweis im Body.

- **Sehr viele Standorte** (> 5 Filialen) → in Phase A im Body Hinweis, dass das Audit teuer wird (Apify-Credits × Standorte × Keywords), Stratege sollte ggf. Standorte priorisieren oder Keywords reduzieren.

- **Wettbewerber-Filialen unbekannt** (WB hat Filialen, aber keine zentrale Liste) → in Phase B pro WB primär das GMB-Hauptprofil; auto-erkannte Filialen aus Maps-Scrape als Sekundär-Standorte markieren. Tiefere Multi-Standort-WB-Analyse ist Out-of-Scope (lieber als eigener Folge-Skill).

- **Re-Run nach Schema-Änderung** → Stratege ändert Schema in Drive, setzt `status: bestaetigt` erneut. Skill erkennt, dass `audits/local-gmb.md` auf Drive existiert, fragt überschreiben/Backup/abbrechen. Bei Backup → bestehende Outputs in den Drive-Sub-Folder `assets/_archive/<datum>/` kopieren bevor upsert.

- **Stratege erzwingt mit `trotzdem laufen` bei eigentlich Skip-Kandidat** → Skill läuft Phase A normal, aber im Schema-Body Warnung "Kein Local-Bezug erkannt — Audit-Ergebnisse können wenig aussagekräftig sein". Skip-Logik wird übersprungen.

- **Branche fehlt in den Review-Themen-Defaults** → Skill nutzt branchen-übergreifende Standard-Themen (Service, Qualität, Preis-Leistung, Erreichbarkeit, Freundlichkeit) plus Hinweis im Body, dass der Stratege branchen-spezifische Themen ergänzen sollte.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B läuft niemals ohne `status: bestaetigt` in Phase-A-Output
- Skip-Logik in Phase A ist ein eigener Pfad (`status: skip_national_online`), kein Fehler
- Outputs leben auf Google Drive in `audits/`, `reports/`, `assets/raw/` (über `drive.py upsert-text`)
- Markdown + YAML-Frontmatter für Aggregat, CSV für Roh-Daten
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (auch beim Skip)
- HTML-Report aus `reports/_shell.html` (aus Drive geladen)
- Apify-Roh-Daten werden lokal gecacht und am Ende des Laufs nach Drive `assets/raw/` hochgeladen
- NAP-Normalisierungs-Regeln sind in `reference/local-output-schema.md` dokumentiert
