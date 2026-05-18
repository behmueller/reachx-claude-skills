---
name: 02-02-wettbewerber-identifikation
description: Identifiziert Wettbewerber für eine laufende MTA aus drei Quellen - vom Kunden genannte (aus dem Briefing), regionale Wettbewerber (via Apify Google Maps), überregionale Best-Practice-Vorbilder (via Sistrix Toplist). Nutzt First-Party-Signale (echte GSC-Top-Queries als Seed-Keywords, GA4-Referral-Domains als Akteurs-Kandidaten), wenn die First-Party-Skills schon gelaufen sind - sonst läuft der Skill unverändert mit aus Briefing/Branche abgeleiteten Seed-Keywords. Nutzt das Schema-vor-Lauf-Pattern - in Phase A wird ein Recherche-Schema generiert und vom Strategen bestätigt, in Phase B läuft die eigentliche Recherche. Nutze diesen Skill IMMER, wenn der Nutzer im Kontext einer laufenden MTA Wettbewerber finden will - auch bei Phrasen wie "Wettbewerber identifizieren", "Wettbewerber-Recherche starten für [Kunde]", "Wer sind die Konkurrenten von [Kunde]", "Finde Wettbewerber", "Konkurrenz-Recherche", "Identifiziere Best Practices im Markt von [Kunde]". Setzt voraus, dass 01-01-mta-projekt-init bereits gelaufen ist und idealerweise auch 02-01-kunden-marken-profil und 01-02-kickoff-transcript-parser - bricht bei fehlender meta.json mit Hinweis ab.
---

# Wettbewerber-Identifikation

Findet Wettbewerber für eine laufende MTA in drei Kategorien:

1. **Vom Kunden genannt** — aus `briefing.md.wettbewerber_genannt` übernommen (immer dabei, auch ohne Online-Marketing-Signale)
2. **Regional direkt** — aus Google-Maps-Recherche im definierten geographischen Radius
3. **Best-Practice überregional** — aus Sistrix-Toplist zu Branchen-Seed-Keywords, ohne Geo-Filter, max 3-5

Der Skill nutzt das **Schema-vor-Lauf-Pattern**: in Phase A generiert er ein Recherche-Schema, das der Stratege reviewt und bestätigt, bevor in Phase B die eigentliche Recherche läuft. Das schützt vor verschwendetem Aufwand bei falschen Seed-Keywords oder Region-Definitionen.

Die Wettbewerber-Liste ist **der wichtigste Eingriffspunkt im MTA**, weil sie alle Folge-Skills steuert — falsche oder unvollständige Wettbewerber-Auswahl wirkt sich auf jede einzelne Audit-Analyse aus.

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

- "Wettbewerber identifizieren für [Kunde]"
- "Wettbewerber-Recherche starten"
- "Finde die Konkurrenz von [Kunde]"
- "Wer sind die Wettbewerber"
- "Best Practices im Markt von [Kunde] finden"
- Nutzer nennt im MTA-Kontext explizit Wettbewerber-Suche

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- **Stark empfohlen:** `01-02-kickoff-transcript-parser` gelaufen → `briefing.md` vorhanden (für vom Kunden genannte Wettbewerber)
- **Stark empfohlen:** `02-01-kunden-marken-profil` gelaufen → `kunde.md` vorhanden (für fundierte Seed-Keyword-Generierung)
- **Idealerweise vorab gelaufen (weiche Anreicherung, KEINE harte Voraussetzung):** der First-Party-Block — `03-04-seo-first-party-gsc` und `03-18-web-analytics-ga4`. Wenn deren Outputs (`audits/gsc-first-party.md` + `audits/gsc-performance.csv`, `audits/ga4-first-party.md` + `audits/ga4-channels.csv`) vorliegen, nutzt 02-02 sie, um Seed-Keywords und Wettbewerber-Kandidaten **datenbasiert statt geraten** abzuleiten — echte GSC-Top-Queries als Seed-Keywords, GA4-Referral-Domains als Akteurs-Kandidaten. Liegen sie nicht vor, läuft 02-02 exakt wie bisher.
- **Optionaler MCP: Sistrix** (für Best-Practice-Toplist via `mcp__sistrix__domain_kwcount_seo` / `mcp__sistrix__keyword_domain_seo`). Health-Check vor Phase B:
  ```bash
  [ -n "$SISTRIX_API_KEY" ] || echo "⚠ SISTRIX_API_KEY nicht gesetzt — Sistrix nicht verfügbar."
  ```
  Wenn Sistrix nicht erreichbar: Skill läuft im **Reduced-Modus** — Best-Practice-Kategorie entfällt oder wird über `WebSearch`/`rag-web-browser` mit manuellen Toplist-Recherchen befüllt. Im Output `konfidenz: niedrig` und Hinweis im Schluss-Format vermerken.
- **Pflicht-MCP: Apify** (für Google Maps Scraper). Credential-Check vor Phase B:
  ```bash
  [ -n "$APIFY_TOKEN" ] || { echo "✗ APIFY_TOKEN nicht gesetzt."; exit 1; }
  ```
  Schlägt der Check fehl: sauberer Abbruch. Kein blindes Starten ohne Health-Check (contracts.md Abschnitt 11).

## Ablauf

Der Skill läuft in zwei Phasen. Bei jedem Aufruf prüft er, ob `wettbewerber/identifikation-schema.md` **auf Drive** existiert und welchen Status sie hat — daraus ergibt sich, ob Phase A oder Phase B läuft.

### Schritt 0: MTA-Kontext ermitteln (bei jedem Aufruf)

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ]; then
  python3 "$DRIVE_PY" list-mtas
  echo "✗ MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

SLUG=$(jq -r '.projekt_slug' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WETT_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

### Phase-Entscheidungs-Logik (bei jedem Aufruf)

```bash
SCHEMA_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "identifikation-schema.md") | .id')
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
```

```
1. Existiert identifikation-schema.md auf Drive (SCHEMA_ID gesetzt)?
   - Nein → Phase A (Schema generieren)
   - Ja, status: vorgeschlagen → Stratege noch nicht reviewt → freundlicher Abbruch mit Hinweis
   - Ja, status: bestaetigt → Phase B (eigentliche Recherche)
   - Ja, status: irgendwas anderes → freundlicher Abbruch mit Hinweis auf Statuswerte

2. Existiert liste.md auf Drive (LISTE_ID gesetzt)?
   - Nein → weiter mit Phase B
   - Ja, status: vorgeschlagen → Stratege noch nicht reviewt — Hinweis, dass Folge-Skills warten
   - Ja, status: bestaetigt → der Skill ist bereits abgeschlossen. Bei explizitem "neu laufen lassen": fragen, ob Backup-und-überschreiben oder Abbruch
```

Zum Lesen des Status: Datei mit `drive.py read <id>` lokal nach `/tmp/...` ablegen und das YAML-Frontmatter parsen.

---

## Phase A — Recherche-Schema generieren

### Schritt A.1: Voraussetzungs-Check und Inputs aus Drive lesen

Wenn `META_ID` leer ist: Abbruch mit Hinweis "01-01-mta-projekt-init zuerst aufrufen".

Lies die optionalen Vorgänger-Outputs aus dem `data/`-Sub-Folder auf Drive (`briefing.md`, `kunde.md`):

```bash
BRIEFING_ID=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "briefing.md") | .id')
KUNDE_ID=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "kunde.md") | .id')

[ -n "$BRIEFING_ID" ] && python3 "$DRIVE_PY" read "$BRIEFING_ID" > /tmp/briefing.md
[ -n "$KUNDE_ID" ] && python3 "$DRIVE_PY" read "$KUNDE_ID" > /tmp/kunde.md
```

- `meta.json` (Pflicht — Branche, Region, Website)
- `data/briefing.md` (empfohlen — `wettbewerber_genannt`)
- `data/kunde.md` (empfohlen — `portfolio_wie_kommuniziert.kategorie`)

Wenn `briefing.md` oder `kunde.md` fehlen: Hinweis im Schema-Body, dass die Konfiguration auf reduzierter Datenbasis erstellt wurde, aber weitermachen.

**Optional: First-Party-Outputs aus dem `audits/`-Sub-Folder lesen.** Wenn der First-Party-Block (`03-04-seo-first-party-gsc`, `03-18-web-analytics-ga4`) schon gelaufen ist, liefert er echte Kunden-Daten, die Seed-Keywords und Wettbewerber-Kandidaten datenbasiert statt geraten machen. Lies sie, wenn vorhanden — wenn nicht, ohne Fehler weitermachen:

```bash
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)

GSC_MD_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "gsc-first-party.md") | .id')
GSC_CSV_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "gsc-performance.csv") | .id')
GA4_MD_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "ga4-first-party.md") | .id')
GA4_CSV_ID=$(python3 "$DRIVE_PY" list-children "$AUDITS_ID" | jq -r '.[] | select(.name == "ga4-channels.csv") | .id')

[ -n "$GSC_CSV_ID" ] && python3 "$DRIVE_PY" read "$GSC_CSV_ID" > /tmp/gsc-performance.csv
[ -n "$GSC_MD_ID" ]  && python3 "$DRIVE_PY" read "$GSC_MD_ID"  > /tmp/gsc-first-party.md
[ -n "$GA4_CSV_ID" ] && python3 "$DRIVE_PY" read "$GA4_CSV_ID" > /tmp/ga4-channels.csv
[ -n "$GA4_MD_ID" ]  && python3 "$DRIVE_PY" read "$GA4_MD_ID"  > /tmp/ga4-first-party.md
```

- `audits/gsc-performance.csv` + `audits/gsc-first-party.md` (optional — echte Top-Queries des Kunden, Quelle für Schritt A.2)
- `audits/ga4-channels.csv` + `audits/ga4-first-party.md` (optional — Kanal-Daten plus die source/medium-Analyse mit den Referral-Domains. **Hinweis:** die detaillierte source/medium-Tabelle mit den einzelnen Referral-Domains liegt im Body von `ga4-first-party.md` in der Sektion "source/medium-Analyse" — `ga4-channels.csv` enthält nur die aggregierte Kanal-Gruppe `Referral`. Beide Outputs werden für Schritt A.7 gelesen.)

Wenn keiner der First-Party-Outputs vorhanden ist: kein Fehler, der Skill läuft wie bisher mit aus Briefing/Branche abgeleiteten Seed-Keywords (siehe Edge Cases).

### Schritt A.2: Seed-Keywords ableiten

**Primärquelle, wenn `gsc-performance.csv` vorliegt — echte GSC-Top-Queries.** Liegt `/tmp/gsc-performance.csv` vor, sind die echten Non-Brand-Top-Queries des Kunden die **primäre** Seed-Keyword-Quelle — statt aus Briefing/Branche zu raten:

1. Aus `gsc-performance.csv` die Zeilen der aktuellen Periode nehmen, nach `clicks` (sekundär `impressions`) absteigend sortieren.
2. **Brand-Queries ausschließen** — alle Queries, die den Marken-Namen oder ein Synonym aus `meta.json.marke` / `data/kunde.md.marke.synonyme` enthalten. (Brand-Queries führen die Toplist-Recherche in die Irre, weil sie nur den Kunden selbst finden.)
3. Aus den verbleibenden Non-Brand-Queries 3-5 Seed-Keywords kuratieren — die stärksten Klick-/Impressionen-Treffer, aber generisch genug für eine Sistrix-Toplist (eine sehr lange Long-Tail-Query ggf. auf ihren Kern-Begriff verdichten).
4. Im Schema-Body dokumentieren, dass die Keywords aus **echten GSC-Daten** stammen (Qualitäts-Hinweis: höhere Treffsicherheit der Toplist-Recherche, weil der Markt aus den realen Suchanfragen des Kunden abgeleitet ist statt geraten), und im Frontmatter `seed_keywords_quelle: gsc` setzen.

**Fallback, wenn keine GSC-Daten vorliegen — wie bisher.** Aus den verfügbaren Quellen 3-5 Seed-Keywords ableiten, in Mischung aus:

- **Produktspezifisch** (1-2): Hauptprodukt-Kategorien aus Briefing/kunde.md
- **Branchengenerisch** (1-2): aus `meta.json.branche`, ggf. mit Anwendungs-Kontext
- **Pain-Point-Keywords** (optional, 1): wenn aus dem Briefing klar ein bestimmter Pain-Point hervortritt, kann ein zugehöriges Keyword sinnvoll sein

In diesem Fall im Frontmatter `seed_keywords_quelle: abgeleitet` setzen.

Wichtig (für beide Fälle): Keywords sollen **nicht** zu spezifisch sein (sonst leere Toplisten) und **nicht** zu generisch (sonst nur Aggregatoren). Faustregel: ein Keyword sollte in Sistrix mindestens 200 Suchvolumen pro Monat haben — wenn das beim Vorschlag unklar ist, im Body einen Hinweis setzen.

### Schritt A.3: Branchenportale-Vorschlag

Aus `reference/branchenportale-mapping.md` die zur Branche passenden Portale auswählen:

1. Branche aus `meta.json` mit den Sektionen in `branchenportale-mapping.md` matchen
2. Alle Portale mit Relevanz `hoch` und `mittel` für diese Branche aufnehmen
3. Plus branchenübergreifende Portale (Google Business Profile, kununu, LinkedIn) immer aufnehmen
4. Für jedes Portal die Felder `portal`, `url`, `relevanz`, `begruendung` setzen

Wenn die Branche nicht direkt in `branchenportale-mapping.md` enthalten ist: nächst-ähnliche Sektion + branchenübergreifende Liste + Hinweis im Body, dass Stratege die Liste prüfen sollte.

### Schritt A.4: Region-Definition ableiten

Aus:

- `meta.json.region` (Primär-Quelle)
- `data/briefing.md.regionen`
- `data/kunde.md.touchpoints_gefunden` (GMB-Standorte)

Faustregeln (siehe auch `reference/identifikation-schema-template.md`):

- Lokale Dienstleister-Branchen (Arzt, Anwalt, Restaurant, Handwerk, Hausverwaltung): `ausdehnung: lokal`, `radius_km: 15-30`
- Regionale B2B-Mittelständler: `ausdehnung: regional`
- Nationale / DACH-Produkt-Anbieter: `ausdehnung: national` / `dach`, `radius_km: 0`
- Globale B2B-SaaS / Online-Handel: `ausdehnung: international`

### Schritt A.5: Online-Marketing-Filter setzen

Default-Schwellwert nach Branchen-Typ (Tabelle in `reference/identifikation-schema-template.md`). Alternative Signale (Google Ads, Meta Ads, LinkedIn-Aktivität) als Liste mit "mindestens 1 von 3".

### Schritt A.6: Vom Briefing übernommene Wettbewerber sammeln

Aus `briefing.md.wettbewerber_genannt`: Liste mit `name`, `quelle_turn`, `bedrohungsgrad_aus_briefing` direkt übernehmen.

Wichtig: hier wird **nichts gefiltert** — auch wenn ein vom Kunden genannter Wettbewerber später keine Online-Marketing-Signale zeigt, gehört er in die Liste (Begründung: Kundenrelevanz schlägt Filter).

**Kritische Haltung (contracts.md Abschnitt 13):** Vom Kunden genannte Wettbewerber sind **Hypothesen**, keine verifizierten Fakten. Im Schema-Vorschlag (Phase A) und im Output (Phase B) als `briefing`-Quelle kennzeichnen. Phase B prüft jeden dieser Akteure gegen reale Datenlage (Sistrix-Sichtbarkeit, Local Pack, GMB, Paid-Ads). Ein im Briefing als „Hauptkonkurrent" genannter Akteur kann sich als nachrangig erweisen — und umgekehrt können Akteure mit starken Signalen auftauchen, die der Kunde nicht erwähnt hat. Auch die Bedrohungsgrad-Einstufung des Kunden ist ein erster Hinweis, kein Urteil.

### Schritt A.7: First-Party-Akteurs-Hinweise sammeln (GA4-Referral)

Wenn GA4-source/medium-/Referral-Daten vorliegen (`/tmp/ga4-first-party.md` aus Schritt A.1 — die source/medium-Tabelle im Body-Abschnitt "source/medium-Analyse"; `/tmp/ga4-channels.csv` liefert ergänzend den aggregierten `Referral`-Kanal), die Top-Referral-Domains scannen und potenzielle Akteurs-Kandidaten herausfiltern:

1. Aus der source/medium-Analyse die Referral-Quellen mit den meisten Sessions nehmen.
2. **Bekannte Nicht-Akteure herausfiltern** — Domains, die KEINE potenziellen Wettbewerber sind:
   - Such- und Aggregator-Domains aus `reference/aggregatoren-blocklist.md`
   - Bewertungs-/Branchenportale (ProvenExpert, Trustpilot, Jameda, wlw, Capterra, G2, OMR, Preisvergleiche) — die laufen über `02-04-branchenportal-recherche`, nicht als Wettbewerber
   - Social-Netze (LinkedIn, Instagram, Facebook, YouTube, TikTok, Pinterest, Reddit)
   - Suchmaschinen (Google, Bing, DuckDuckGo, Ecosia)
   - E-Mail-/Newsletter-Provider, URL-Shortener und offensichtliche technische Referrer
3. Was übrig bleibt, sind **echte Fremd-Domains, die Traffic an den Kunden schicken** — oft Branchen-Verzeichnisse, Partner, oder eben tatsächliche Wettbewerber, die den Kunden verlinken. Diese als Kandidaten in die neue Schema-Sektion `first_party_hinweise` aufnehmen, jeweils mit:
   - `domain` — die Referral-Domain
   - `referral_sessions` — Sessions aus GA4 (aktuelle Periode)
   - `begruendung` — kurzer Hinweis, warum die Domain als Akteurs-Kandidat aufgenommen wurde (z. B. "Fremd-Domain mit relevantem Referral-Traffic, kein bekanntes Portal/Social/Suchmaschine — Strategen-Prüfung, ob Wettbewerber")
4. Diese Sektion ist **explizit zur Strategen-Prüfung** — der Skill entscheidet nicht selbst, ob es Wettbewerber sind. Im Schema-Body einen Hinweis setzen, dass der Stratege die Liste durchgehen und unzutreffende Domains streichen soll.

Wenn keine GA4-Daten vorliegen: Schritt liefert eine **leere** `first_party_hinweise`-Sektion, kein Fehler. Im Schema-Body kurz vermerken, dass keine GA4-Referral-Daten zur Verfügung standen.

### Schritt A.8: `wettbewerber/identifikation-schema.md` nach Drive schreiben

Baue das vollständige Schema lokal im Cache zusammen (Format in `reference/identifikation-schema-template.md`) mit `status: vorgeschlagen` und lade es nach Drive in den `wettbewerber/`-Sub-Folder hoch:

```bash
mkdir -p ~/.cache/reachx-mta/"$SLUG"
# ... Schema lokal aufbauen ...
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "identifikation-schema.md" \
  ~/.cache/reachx-mta/"$SLUG"/identifikation-schema.md "text/markdown"
```

Im Body: pro Sektion eine Begründung, damit der Stratege schnell prüfen kann, warum diese Auswahl entstanden ist.

Der Stratege kann das Schema direkt in der Drive-Web-UI editieren (Markdown ist editierbar) oder lokal runterladen und neu hochladen — Phase B liest in beiden Fällen aus Drive.

### Schritt A.9: HTML-Report (optional)

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

In Phase A optional — der Schema-Markdown ist normalerweise ausreichend zum Review. Wenn der Stratege ihn lieber visuell sieht: HTML-Report mit Schema-Visualisierung erzeugen, aber nicht Pflicht.

### Schritt A.10: `status.md` aktualisieren und Schluss-Format Phase A

Lies, aktualisiere und schreibe `status.md` auf Drive (im MTA-Root-Folder) per `drive.py upsert-text` — setze `blockiert`-Eintrag wie unten.

```
✓ 02-02-wettbewerber-identifikation Phase A abgeschlossen.

Outputs (auf Drive):
- wettbewerber/identifikation-schema.md — Recherche-Schema (status: vorgeschlagen)

Konfigurations-Vorschlag:
- Seed-Keywords:      <Liste> (Quelle: <gsc | abgeleitet>)
- Region:             <ausdehnung + ggf. Radius>
- Branchenportale:    <Anzahl> identifiziert
- Filter-Schwelle:    Sistrix Visibility ≥ <Wert>
- Vom Briefing:       <Anzahl> Wettbewerber übernommen
- First-Party-Hinweise: <Anzahl> GA4-Referral-Domains als Kandidaten (0, wenn keine GA4-Daten)

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Seed-Keywords, Region, Branchenportale, Online-Marketing-Filter.
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

**Wichtig:** der Skill schreibt den Status `blockiert` in `status.md`, weil Phase B auf Strategen-Bestätigung wartet:

```yaml
blockiert:
  - skill: 02-02-wettbewerber-identifikation (Phase B)
    wartet_auf: "Strategen-Review von wettbewerber/identifikation-schema.md"
```

---

## Phase B — Eigentliche Wettbewerber-Recherche

### Schritt B.1: Schema aus Drive lesen und validieren

```bash
python3 "$DRIVE_PY" read "$SCHEMA_ID" > /tmp/identifikation-schema.md
```

Parse das YAML-Frontmatter, prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis
2. `branchen_seed_keywords` ≥ 2 Einträge?
3. `region_definition.ausdehnung` gesetzt?
4. `filter_online_marketing.sistrix_visibility_min` gesetzt?

Bei jedem Fehler: konkreten Hinweis, welches Feld korrigiert werden muss.

### Schritt B.2: Briefing-Wettbewerber übernehmen

Aus `vom_briefing_uebernommen` (im Schema): direkt in `wettbewerber.kunde_genannt` der Output-Liste übertragen.

Für jeden: Website ermitteln (entweder vom Kunden im Briefing genannt, oder via gezielte Web-Search `<name> site:de` / `<name> homepage`). Wenn keine Website findbar: trotzdem aufnehmen mit `website: null`, Hinweis in Notiz.

### Schritt B.3: Regionale Wettbewerber via Google Maps

Wenn `region_definition.ausdehnung` in {lokal, regional}:

1. Per Apify Google Maps Scraper (`compass/google-maps-scraper` oder `apify/google-maps-extractor`) suchen:
   - Suchbegriff: jedes Seed-Keyword × `region_definition.primaer`
   - Optional Radius via `searchPositions`
2. Pro Treffer extrahieren: Name, Adresse, PLZ, Stadt, Lat/Lng, Website, Google-Rating, Anzahl Reviews, Telefonnummer
3. Deduplizieren (gleiche Domain = gleicher Wettbewerber)
4. Filter:
   - **Aggregatoren-Blocklist** (`reference/aggregatoren-blocklist.md`) anwenden
   - **`aggregatoren_blocklist_zusatz`** aus dem Schema anwenden
   - Wettbewerber ohne Website: nur aufnehmen, wenn Reviews ≥ 5 (sonst zu wenig Online-Präsenz)
5. Max `ziel_anzahl.regional_max` (Default 10), sortiert nach Reviews-Count absteigend

### Schritt B.4: Überregionale Best-Practice via Sistrix

Wenn `region_definition.ausdehnung` ≠ international (für international ist eine andere Strategie nötig):

1. Sistrix-Toplist-API pro Seed-Keyword aufrufen, Top-50 ziehen
2. Pro Treffer extrahieren: Domain, Visibility-Index, Top-Keywords-Liste
3. Filter anwenden:
   - **Aggregatoren-Blocklist** anwenden
   - **`aggregatoren_blocklist_zusatz`** anwenden
   - **`filter_online_marketing.sistrix_visibility_min`** anwenden
   - Geo-Filter: wenn ein WB primär in derselben Region wie der Kunde arbeitet, fällt er aus der Best-Practice-Kategorie raus (er ist dann eher regional und wurde schon in Schritt B.3 gefunden)
4. Pro Domain Website-Check (kurzer Crawl der Startseite), um zu prüfen:
   - Ist es eine echte Marken-Website (kein Affiliate, kein Aggregator)?
   - Online-Marketing-Signale ableiten
5. Max `ziel_anzahl.best_practice_ueberregional_max` (Default 5), kuratiert nach Lehrwert (nicht nur nach Visibility):
   - Vielfalt der Branchen-Sub-Segmente bevorzugen
   - Mix aus Sichtbarkeits-Modellen (manche SEO-getrieben, manche Ads-getrieben, manche Content-getrieben)

### Schritt B.4b: First-Party-Hinweise prüfen (GA4-Referral-Kandidaten)

Wenn das Schema eine nicht-leere `first_party_hinweise`-Sektion enthält (vom Strategen in Phase A bestätigt — Domains, die er nicht gestrichen hat):

1. Jede bestätigte `first_party_hinweise`-Domain wie einen normalen Wettbewerber-Kandidaten behandeln — sie durchläuft denselben **Website-Check** (kurzer Crawl der Startseite: echte Marken-Website, kein Affiliate/Aggregator?) und denselben **Signal-Check** wie die Kandidaten aus B.3 und B.4.
2. Domains, die den Website-Check nicht bestehen (Portal, Affiliate, Verzeichnis, technischer Referrer) oder kein einziges Online-Marketing-Signal zeigen, werden verworfen — mit kurzer Notiz im Body.
3. Domains, die als **echte Wettbewerber** durchgehen, werden in die passende **bestehende** Kategorie einsortiert:
   - primär regional aktiv (in der Region des Kunden) → Kategorie `regional`
   - überregional aktiv → Kategorie `best_practice_ueberregional`
   - Dedupe: ist die Domain bereits über B.3 oder B.4 in der Liste, **nicht** doppelt aufnehmen — stattdessen am bestehenden Eintrag den Quellen-Vermerk ergänzen.
4. Jeder so aufgenommene Wettbewerber bekommt zusätzlich den Quellen-Vermerk `quelle_zusatz: first_party_signal` in seinem Listen-Eintrag — damit nachvollziehbar bleibt, dass der Akteur über ein First-Party-Signal (GA4-Referral) gefunden wurde.

**Wichtig:** Es entsteht **keine vierte Kategorie** in `liste.md` — die First-Party-Kandidaten landen in den drei bestehenden Kategorien, nur mit dem zusätzlichen `quelle_zusatz`-Feld. Wenn die `first_party_hinweise`-Sektion leer ist, wird dieser Schritt übersprungen.

### Schritt B.5: Online-Marketing-Signale anreichern

Für jeden Wettbewerber (alle drei Kategorien) den Signal-Check:

- **Sistrix Visibility** (wenn vorhanden) → direkt aus den Recherche-Daten
- **Google Ads** → Google Ads Transparency Center prüfen (`https://adstransparency.google.com/?domain=<domain>`)
- **Meta Ads** → Meta Ad Library prüfen (`https://www.facebook.com/ads/library/?q=<name>`)
- **LinkedIn Aktivität** → LinkedIn Company Page suchen, letzte 90 Tage Post-Aktivität

Für alle Signale: einfache Quantifizierung als String, z. B. `"aktive Google Ads (3 aktive Anzeigen)"`, `"keine LinkedIn-Page gefunden"`.

Jeder Wettbewerber muss **mindestens ein Signal** haben (aus dem Schema-Filter), sonst wird er verworfen — **außer** er stammt aus der Kategorie `kunde_genannt` (Ausnahme: vom Kunden genannte Wettbewerber bleiben immer in der Liste).

### Schritt B.6: `empfehlung_profilieren` setzen

Default-Logik (siehe `reference/liste-schema.md`):

- `kunde_genannt` + `bedrohungsgrad: direkt` → `ja`
- `kunde_genannt` + `bedrohungsgrad: inspiration` → `optional`
- `regional` top 3 nach Reviews → `ja`, Rest → `optional`
- `best_practice_ueberregional` → alle `ja`

Der Stratege kann das im Review anpassen.

### Schritt B.7: `wettbewerber/liste.md` nach Drive schreiben

Baue die Liste lokal im Cache zusammen (Format in `reference/liste-schema.md`) und lade sie nach Drive in den `wettbewerber/`-Sub-Folder hoch:

```bash
# ... liste.md lokal aufbauen mit status: vorgeschlagen ...
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "liste.md" \
  ~/.cache/reachx-mta/"$SLUG"/liste.md "text/markdown"
```

YAML-Frontmatter mit allen strukturierten Feldern, Markdown-Body mit den drei Kategorien-Sektionen und einer optionalen "Empfehlungen"-Sektion bei Auffälligkeiten.

Status: `vorgeschlagen`. Der Stratege bestätigt nach Review.

### Schritt B.8: HTML-Report erzeugen

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `reports/_shell.html` aus Drive und baue `03-wettbewerber-liste.html` daraus:

- `{{TITLE}}` → `Wettbewerber-Liste · <Kunde>`
- `{{EYEBROW}}` → `MTA-Wettbewerber-Identifikation`
- `{{DISPLAY_NAME}}` → `Wettbewerber: <Kunde>`
- `{{META_LINE}}` → `Aus 3 Quellen identifiziert · <Recherche-Datum> · Generiert: <heute>`
- `{{MAIN_CONTENT}}` →
  - Stat-Strip mit Gesamtanzahl, Anzahl pro Kategorie, Anzahl empfohlen-zu-profilieren
  - Sticky-TOC zu den drei Kategorien plus Empfehlungen
  - Pro Kategorie eine eigene Sektion
  - Wettbewerber als `<details>`-Blöcke mit `data-rating` je nach Online-Marketing-Stärke
  - Aggregierte Auffälligkeiten als `.suggestion`-Block
  - **Prominenter Status-Hinweis oben**: "Diese Liste wartet auf deine Bestätigung. Nach Review bitte `status: bestaetigt` setzen."
- `{{FOOTER_TEXT}}` → `MTA · <Kunde> · Wettbewerber-Identifikation Phase B`

Lokal zusammenbauen, dann nach Drive hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "03-wettbewerber-liste.html" \
  ~/.cache/reachx-mta/"$SLUG"/03-wettbewerber-liste.html "text/html"
```

### Schritt B.9: Dashboard-Update

Lies `reports/index.html` aus Drive, modifiziere und schreibe zurück per `upsert-text`:

- Stat-Strip aktualisieren
- "Erledigt"-Sektion erweitern um `02-02-wettbewerber-identifikation`
- Reports-Liste um `03-wettbewerber-liste.html` erweitern
- "Nächster empfohlener Schritt": auf `02-05-wettbewerber-realitaets-check` setzen, aber mit Hinweis "wartet auf Review der Liste"

### Schritt B.10: `status.md` aktualisieren

`status.md` liegt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe per `upsert-text` zurück.

- `02-02-wettbewerber-identifikation` in `schritte_done`
- Eigene Sektion in "✓ Erledigt"
- Eintrag in `blockiert`:
  ```yaml
  blockiert:
    - skill: 02-05-wettbewerber-realitaets-check
      wartet_auf: "Strategen-Review von wettbewerber/liste.md (status: bestaetigt setzen)"
  ```
- `naechster_empfohlen` auf einen unblockierten Skill setzen (z. B. `03-01-seo-sichtbarkeit-und-rankings`, der nur die Kunden-Website braucht, oder ein anderer Audit-Skill, der die Liste noch nicht zwingend braucht)

### Schritt B.11: Standard-Schlussformat im Chat

```
✓ 02-02-wettbewerber-identifikation Phase B abgeschlossen.

Outputs (auf Drive):
- wettbewerber/liste.md — Wettbewerber-Liste in 3 Kategorien (status: vorgeschlagen)
- reports/03-wettbewerber-liste.html — visueller Report
Status aktualisiert in: status.md

Ergebnis:
- Vom Kunden genannt:        <X> Wettbewerber
- Regional direkt:            <Y> Wettbewerber
- Best-Practice überregional: <Z> Wettbewerber (max 5)
- Empfohlen zu profilieren:   <N> Wettbewerber

[Falls Auffälligkeiten gefunden:]
⚠ Auffälligkeiten:
- <Top 2-3>

⏸ Pflicht-Review durch den Strategen
Bitte die Liste prüfen — der wichtigste Eingriffspunkt im MTA, weil alle Folge-Skills hieran hängen.
Nach Review: status: bestaetigt im wettbewerber/liste.md setzen.

Nächste Schritte (nach Listen-Bestätigung):
1. 02-05-wettbewerber-realitaets-check — verifiziert die Akteure gegen echte Daten, klassifiziert nach Bedrohungslage
2. 02-03-wettbewerber-marken-profil — Profile für die als relevant verifizierten Wettbewerber
3. 02-04-branchenportal-recherche — Erwähnungen auf den identifizierten Portalen

Parallel jetzt schon möglich:
- 03-01-seo-sichtbarkeit-und-rankings — braucht die Liste nicht zwingend

Sag mir, was du als nächstes willst.
```

## Bundled Resources

- `reference/identifikation-schema-template.md` — Format der Phase-A-Output-Datei mit Defaults pro Branchen-Typ
- `reference/branchenportale-mapping.md` — Branche → Portale-Mapping (wachsende Liste)
- `reference/aggregatoren-blocklist.md` — Standard-Domains, die rausgefiltert werden
- `reference/liste-schema.md` — Output-Format für `wettbewerber/liste.md`

## Edge Cases

- **Briefing nennt keine Wettbewerber** → Kategorie `kunde_genannt` bleibt leer, kein Fehler. Im Body Hinweis: "Kunde hat im Kickoff keine Wettbewerber genannt — Empfehlung, in einer Folge-Runde gezielt nach Konkurrenten zu fragen."
- **Sistrix-MCP nicht verfügbar** (kein API-Key oder MCP-Verbindung unterbrochen) → Reduced-Modus: Kategorie `best_practice_ueberregional` wird über manuelle `WebSearch`-Recherche (`<Seed-Keyword> beste Anbieter Deutschland`, `<Seed-Keyword> Marktführer`) und `rag-web-browser` mit Branchen-Toplisten-URLs befüllt. Im Output-Frontmatter `sistrix_toplist: false` setzen und im Schluss-Format `konfidenz: niedrig` für diese Kategorie vermerken. Kein endloses Durchprobieren von Fallback-Methoden — eine Alternative kurz dokumentieren und weitermachen.
- **Sistrix liefert keine relevanten Treffer für die Seed-Keywords** → Branchen-Nische, Stratege sollte spezifischere oder generischere Keywords vorschlagen. Skill gibt Hinweis und schlägt 1-2 alternative Keyword-Kombinationen vor.
- **Google Maps liefert nur Aggregatoren / Plattformen** → Wettbewerber sind nicht primär lokal organisiert (z. B. B2B-SaaS). Skip Schritt B.3 mit Notiz im Body.
- **Internationaler Markt** (`ausdehnung: international`) → Skill warnt: "Sistrix ist DACH-fokussiert, internationale Recherche unvollständig. Stratege sollte zusätzlich Ahrefs/SimilarWeb-Daten manuell prüfen."
- **Vom Kunden genannter Wettbewerber existiert nicht mehr / Domain ist offline** → Beim Website-Check Fehlerfall sauber abfangen, in der Liste mit `online_marketing_signale: ["Website nicht erreichbar"]` markieren, `empfehlung_profilieren: nein` setzen.
- **Mehr als 5 Best-Practice-Kandidaten mit ähnlich hoher Visibility** → Kuration nötig. Skill wählt nach Lehrwert-Vielfalt (Mix der Sichtbarkeits-Modelle), schreibt im Body, welche knapp aus der Top-5 rausgefallen sind, damit der Stratege ggf. tauschen kann.
- **First-Party-Skills noch nicht gelaufen** (`03-04-seo-first-party-gsc`, `03-18-web-analytics-ga4` haben keine Outputs in `audits/` hinterlegt) → 02-02 läuft wie bisher: Seed-Keywords werden aus Briefing/Branche abgeleitet (`seed_keywords_quelle: abgeleitet`), die `first_party_hinweise`-Sektion bleibt leer. Hinweis im Schema-Body, dass eine vorherige First-Party-Erhebung (GSC + GA4) die Keyword- und Kandidaten-Qualität deutlich verbessern würde — echte Top-Queries statt geratener Branchen-Begriffe, GA4-Referral-Domains als zusätzliche Akteurs-Quelle. Kein Fehler, kein Blocker.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt einhalten — Phase B läuft niemals ohne `status: bestaetigt` in Phase-A-Output (gelesen aus Drive!)
- Outputs leben in Google Drive (via `drive.py upsert-text`); Pfad-Angaben im Frontmatter bezeichnen die Sub-Folder relativ zum MTA-Drive-Root
- Markdown + YAML-Frontmatter Hybrid-Format
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (in-place auf Drive)
- HTML-Reports basieren auf `reports/_shell.html` (aus Drive geladen)
- Standard-Schlussformat im Chat
