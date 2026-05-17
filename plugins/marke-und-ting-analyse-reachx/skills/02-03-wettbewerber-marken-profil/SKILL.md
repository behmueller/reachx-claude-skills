---
name: 02-03-wettbewerber-marken-profil
description: Erstellt strukturierte Marken-Profile für alle in wettbewerber/liste.md markierten Wettbewerber - identisches Schema wie 02-01-kunden-marken-profil, damit Synthese-Skills wie 04-01-positionierungs-analyse Kunde und Wettbewerber strukturell vergleichen können. Pro Wettbewerber ein eigenes Profil mit Marken-Identität, Portfolio, USPs, Zielgruppen-Hypothese, Tonalität auf vier Achsen, Hero-Test nach Donald Miller, Verständlichkeit, Touchpoint-Inventur - plus ein Bundle-HTML-Report mit allen Profilen Side-by-Side. Nutze diesen Skill IMMER, wenn der Nutzer im Kontext einer MTA Marken-Profile für die Wettbewerber erstellen will - auch bei Phrasen wie "Marken-Profile für Wettbewerber erstellen", "Profile die Wettbewerber", "Wettbewerber-Marken-Profile bauen", "Brand-Audit der Wettbewerber", "Analysiere die Wettbewerber-Websites", "Hero-Test für Wettbewerber". Setzt voraus, dass 02-02-wettbewerber-identifikation gelaufen ist und wettbewerber/liste.md den Status bestaetigt hat - bricht sonst ab.
---

# Wettbewerber-Marken-Profil

Erstellt pro Wettbewerber aus `wettbewerber/liste.md` ein strukturiertes Marken-Profil mit **identischer Struktur zu `02-01-kunden-marken-profil`** — damit Synthese-Skills (z. B. `04-01-positionierungs-analyse`) Kunde und Wettbewerber strukturell Side-by-Side vergleichen können.

**Wichtige Design-Regel:** Dieser Skill verwendet das Schema, die Methodik und die Crawl-Vorgaben **direkt aus `02-01-kunden-marken-profil`** — keine Duplizierung. Wenn du dir unsicher bist, was wie zu erfassen ist, lies:

- `02-01-kunden-marken-profil/reference/kunde-schema.md` — vollständiges Schema für ein Marken-Profil (gilt 1:1 für Wettbewerber)
- `02-01-kunden-marken-profil/reference/methodik.md` — Hero-Test, Tonalitäts-Achsen, Verständlichkeits-Bewertung

Den `02-01-kunden-marken-profil`-Skill-Pfad tolerant auflösen — typischerweise im selben Skills-Root wie dieser Skill.

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

- "Marken-Profile für Wettbewerber erstellen"
- "Profile die Wettbewerber"
- "Wettbewerber-Marken-Profile bauen"
- "Brand-Audit der Wettbewerber"
- "Analysiere die Websites der Wettbewerber"
- "Mach die Wettbewerber-Profile für [Kunde]"
- "Hero-Test für die Wettbewerber"
- Nutzer fragt nach Tonalitäts-Analyse oder USP-Vergleich der Wettbewerber im MTA-Kontext

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- `02-02-wettbewerber-identifikation` Phase B abgeschlossen → `wettbewerber/liste.md` vorhanden
- `wettbewerber/liste.md` hat `status: bestaetigt` im Frontmatter — sonst Abbruch mit Hinweis
- Apify-Zugang verfügbar (über MCP oder API-Token im Environment)
- Empfohlen: `02-01-kunden-marken-profil` ist bereits gelaufen (für Vergleichbarkeit) — kein harter Block, aber Hinweis im Schluss-Format

## Ablauf

### Schritt 0: MTA-Kontext ermitteln

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
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

### Schritt 1: Voraussetzungs-Check (Drive)

Wenn `META_ID` leer ist:

```
✗ Kein gültiger MTA-Folder.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Lies `wettbewerber/liste.md` aus Drive:

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -z "$LISTE_ID" ]; then
  echo "✗ wettbewerber/liste.md nicht gefunden auf Drive."
  echo "Bitte zuerst 02-02-wettbewerber-identifikation laufen lassen (Phase A + Phase B)."
  exit 1
fi
python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/liste.md
```

Parse das YAML-Frontmatter:

- `status: bestaetigt` → weiter
- `status: vorgeschlagen` → Abbruch:
  ```
  ⏸ wettbewerber/liste.md hat status: vorgeschlagen.
  Bitte erst die Liste reviewen und auf status: bestaetigt setzen, dann diesen Skill erneut aufrufen.
  Das ist der wichtigste Eingriffspunkt im MTA — alle Folge-Skills hängen an dieser Liste.
  ```
- Anderer Status → Abbruch mit Hinweis auf erlaubte Werte

Prüfe optional, ob `data/kunde.md` auf Drive existiert (via `list-children` auf `$DATA_ID`) — wenn ja, merke dir, dass am Ende ein Hinweis auf `04-01-positionierungs-analyse` möglich ist; wenn nein, im Schluss-Format `02-01-kunden-marken-profil` als Empfehlung listen.

### Schritt 2: Wettbewerber-Auswahl

Aus `wettbewerber/liste.md` Frontmatter alle Einträge aus den drei Kategorien (`kunde_genannt`, `regional`, `best_practice_ueberregional`) sammeln.

**Filter-Regeln:**

1. **Default-Filter**: nur Einträge mit `empfehlung_profilieren: ja` werden profiliert
2. **Optional vom Nutzer überschrieben**: Wenn der Nutzer im Aufruf explizit nennt "auch die optionalen", "alle profilieren" oder einzelne Wettbewerber nennt, anwenden
3. **Ohne Website**: Einträge mit `website: null` oder offline-Domain werden auf den Reduced-Mode geschickt (siehe Schritt 5d) und am Ende mit Empfehlung `empfehlung_profilieren: nein` markiert (Hinweis im Schluss-Format, damit Stratege die Liste anpasst)

**Anzahl-Limit:**

- Standard: max 7 Wettbewerber pro Lauf (siehe `reference/profil-prozess.md`)
- Wenn die gefilterte Liste mehr als 7 Einträge hat:
  ```
  ⚠ N Wettbewerber haben empfehlung_profilieren: ja — empfohlen sind max 7 pro Lauf.
  
  Vorschlag: Liste auf die wichtigsten 7 kuratieren (Priorität: kunde_genannt direkt > best_practice > regional top-3 nach Reviews).
  Soll ich mit den Top 7 nach dieser Priorität weitermachen, oder möchtest du die Auswahl manuell anpassen?
  ```
  Im Autonomie-Modus (oder bei expliziter Bestätigung): Auto-Kuration nach der Priorität anwenden, **welche Wettbewerber rausgefallen sind** im Schluss-Format ausweisen.

### Schritt 3: Existenz-Check pro Wettbewerber (Drive)

Liste die Inhalte des `wettbewerber/`-Sub-Folders auf Drive einmal und cache das Ergebnis:

```bash
python3 "$DRIVE_PY" list-children "$WETT_ID" > /tmp/wett-children.json
```

Für jeden zu profilierenden Wettbewerber:

1. Slug ermitteln (siehe `reference/profil-prozess.md` Abschnitt 1)
2. Prüfen, ob `<SLUG>.md` in `/tmp/wett-children.json` enthalten ist (SLUG = der generierte Slug-Wert)
3. Bei Existenz: pro existierender Datei einmal fragen:
   - **(a) überschreiben** — alte Version geht verloren (Drive zeigt die alte Version automatisch in der Versions-Historie)
   - **(b) Backup-und-neu** — alte Version als `SLUG.backup-<ISO>.md` per `upsert-text` in den `wettbewerber/`-Sub-Folder ablegen, dann neu erstellen
   - **(c) skippen** — diesen Wettbewerber nicht erneut profilieren
   - **(d) abbrechen** — gesamter Skill-Lauf abbrechen

Im Standard-Workflow (alle Wettbewerber neu): Bei mehreren existierenden Profilen Sammel-Frage stellen, eine Antwort für alle.

### Schritt 4: Crawl-Plan und Reihenfolge

Liste der zu crawlenden Wettbewerber zusammenstellen, sortiert nach:

1. `kunde_genannt` mit `bedrohungsgrad: direkt` zuerst (höchste Relevanz)
2. `best_practice_ueberregional` (für strategischen Vergleich)
3. `regional` Top nach Google-Maps-Reviews

Verarbeitungs-Modus: **sequenziell** (siehe `reference/profil-prozess.md` Abschnitt 2 — Begründung: Apify-Rate-Limits, Vision-Modell-Auslastung, leichter zu debuggen). Bei größeren Listen (5+) kurze Pausen zwischen den Apify-Crawls einbauen.

### Schritt 5: Pro Wettbewerber das Marken-Profil erstellen

Für jeden Wettbewerber die acht Sub-Schritte ausführen, **identisch zur Logik in `02-01-kunden-marken-profil` Schritte 2 bis 9** (siehe dort und in `02-01-kunden-marken-profil/reference/methodik.md` für Details — hier nur kurze Erinnerung):

#### 5a. Website crawlen

Apify `apify/website-content-crawler` mit Parametern:

- `startUrls`: nur die `website`-URL des Wettbewerbers aus `liste.md`
- `maxCrawlPages`: **20** (für Wettbewerber bewusst niedriger als beim Kunden — wir brauchen nur Marken-Substanz, keine Tiefen-Inventur)
- `maxCrawlDepth`: 2
- `crawlerType`: `playwright:chrome`
- `saveMarkdown`: true
- `saveHtml`: true
- `removeCookieWarnings`: true

Roh-Daten lokal speichern in `~/.cache/reachx-mta/<slug>/website-crawl/<SLUG>.json` und am Skill-Ende komprimiert (`.json.gz`) in den `assets/`-Sub-Folder auf Drive hochladen.

#### 5b. Startseite-Screenshot

Apify `apify/puppeteer-scraper` (Viewport 1440×900, kein Vollseiten-Shot). Lokal als `~/.cache/reachx-mta/<slug>/<SLUG>-startseite.png` speichern und nach Drive in den `assets/`-Sub-Folder hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$ASSETS_ID" "<SLUG>-startseite.png" \
  ~/.cache/reachx-mta/"$SLUG"/<SLUG>-startseite.png "image/png"
```

Mobile-Variante (375×812) nur, wenn die Wettbewerber-Branche typisch hohen Mobile-Anteil hat (Local Services, B2C, Retail) — gleiche Logik wie beim Kunden.

#### 5c. Marken-Identität, Portfolio, USPs, Zielgruppen-Hypothese

Aus den gecrawlten Inhalten extrahieren — exakt nach den Vorgaben in `02-01-kunden-marken-profil` Schritte 4 und 5. Quelle ist die **Wettbewerber-Website**, nicht das Briefing des Kunden.

#### 5d. Reduced-Mode bei fehlender / sehr dünner Website

Wenn der Wettbewerber keine erreichbare Website hat (z. B. nur Google-Maps-Eintrag, oder Website offline / 404):

- Marken-Identität nur aus dem `liste.md`-Eintrag (Name, evtl. Google-Maps-Beschreibung)
- Portfolio, USPs, Zielgruppen-Hypothese, Tonalität, Hero-Test, Verständlichkeit: **leer lassen** mit `crawl_luecken`-Eintrag "Website nicht erreichbar"
- Touchpoint-Inventur: nur die aus dem `liste.md`-Eintrag bekannten (z. B. Google Maps, Telefonnummer)
- Im Schluss-Format ausweisen, dass dieser Wettbewerber im Reduced-Mode profiliert wurde
- Empfehlung an den Strategen: `empfehlung_profilieren: nein` in `liste.md` setzen, damit künftige Re-Runs den Wettbewerber überspringen

#### 5e. Tonalitäts-Analyse (4 Achsen)

Genau nach `02-01-kunden-marken-profil/reference/methodik.md` Abschnitt 2. Vier Achsen, Wert -2 bis +2, je 2–3 Zitat-Belege.

#### 5f. Hero-Test und Verständlichkeit

Genau nach `02-01-kunden-marken-profil/reference/methodik.md` Abschnitt 1 und 3. Vier Donald-Miller-Fragen, plus separater Verständlichkeits-Score 1–5. Vision-Modell auf den Startseiten-Screenshot aus 5b aufrufen.

#### 5g. Touchpoint-Inventur

Nach den Patterns aus `02-01-kunden-marken-profil` Schritt 8. Wichtig für später: hier finden wir die LinkedIn-/Instagram-/TikTok-Handles der Wettbewerber, die `03-11-social-linkedin`, `03-08-social-instagram` etc. später brauchen.

#### 5h. `wettbewerber/SLUG.md` nach Drive schreiben

Baue das Marken-Profil lokal im Cache zusammen (Schema in `02-01-kunden-marken-profil/reference/kunde-schema.md` — identisch) und lade nach Drive in den `wettbewerber/`-Sub-Folder hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "<SLUG>.md" \
  ~/.cache/reachx-mta/"$SLUG"/<SLUG>.md "text/markdown"
```

Im Frontmatter:

- `skill: 02-03-wettbewerber-marken-profil` (nicht `02-01-kunden-marken-profil`)
- Zusätzliches Feld `wettbewerber_kategorie: kunde_genannt | regional | best_practice_ueberregional` aus `liste.md` übernehmen
- Zusätzliches Feld `wettbewerber_quelle_eintrag: SLUG-AUS-LISTE` als Rückverweis
- Alle übrigen Felder identisch wie beim Kunden

Body-Struktur ebenfalls identisch (Übersicht, Portfolio, USPs, Zielgruppen, Tonalität, Hero-Test, Touchpoints, Lücken).

### Schritt 6: Bundle-HTML-Report `reports/04-wettbewerber-profile.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `reports/_shell.html` aus Drive und baue daraus einen Bundle-Report, der alle erstellten Profile Side-by-Side darstellt:

- `{{TITLE}}` → `Wettbewerber-Profile · KUNDE`
- `{{EYEBROW}}` → `MTA-Wettbewerber-Marken-Profile`
- `{{DISPLAY_NAME}}` → `Wettbewerber-Profile: KUNDE`
- `{{META_LINE}}` → `N Profile erstellt · Crawl-Datum DATUM · Generiert: heute`
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip oben**: Anzahl Profile gesamt, Anzahl pro Kategorie (kunde_genannt / regional / best_practice), Durchschnittlicher Hero-Test-Score, Anzahl im Reduced-Mode
  - **Sticky-TOC** mit Sprung zu jedem Wettbewerber-Profil
  - **Wenn `data/kunde.md` existiert**: Vergleichs-Block direkt oben — Kunden-Hero-Test-Score vs. Wettbewerber-Durchschnitt, plus Hinweis "Detaillierter Vergleich folgt in `04-01-positionierungs-analyse`"
  - **Pro Wettbewerber** ein `details class="dim"`-Block (defaultmäßig aufgeklappt für die ersten 3, zugeklappt für weitere) mit:
    - Kategorie-Badge (kunde_genannt / regional / best_practice)
    - Marken-Identität (Name, Claim, Logo wenn vorhanden)
    - Hero-Test-Score als Stat-Mini (Gesamt + schwächste Frage)
    - Tonalitäts-Achsen als kompakte Visualisierung (z. B. einfache Balken)
    - Top-3 USPs (mit Zitat-Beleg)
    - Touchpoints als Inline-Badges
    - Bei Reduced-Mode: deutlicher Hinweis-Block "Website nicht erreichbar — Profil reduziert"
  - **Cluster-Hinweis**: Wenn zwei oder mehr Wettbewerber sehr ähnliche Tonalität, Zielgruppen oder USPs haben, `.suggestion`-Block mit Hinweis "Diese Wettbewerber clustern eng — möglicher Hinweis auf Marktlücke oder Sättigung"
  - **Auffälligkeiten-Block** unten: 2–3 strategie-relevante Beobachtungen über die Wettbewerber-Gruppe (z. B. "Alle regionalen WBs haben Hero-Test unter 3 → Differenzierungs-Chance über bessere Startseite")
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · Wettbewerber-Marken-Profile`

Lokal zusammenbauen und nach Drive hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "04-wettbewerber-profile.html" \
  ~/.cache/reachx-mta/"$SLUG"/04-wettbewerber-profile.html "text/html"
```

### Schritt 7: Dashboard-Update

Lies `reports/index.html` aus Drive, modifiziere und schreibe per `upsert-text` zurück:

- Stat-Strip aktualisieren (Anzahl erstellte Profile zur Statistik hinzufügen)
- "Erledigt"-Sektion erweitern um `02-03-wettbewerber-marken-profil`
- Reports-Liste um `04-wettbewerber-profile.html` erweitern
- Nächste Empfehlung aktualisieren: `02-04-branchenportal-recherche` ODER ein Audit-Skill — je nachdem, was als nächster sinnvoll ist (siehe Schritt 9)

### Schritt 8: `status.md` aktualisieren

`status.md` liegt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe per `upsert-text` zurück.

Nach Regeln aus `contracts.md` Abschnitt 3:

- `02-03-wettbewerber-marken-profil` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Output-Liste, Hinweisen (z. B. "1 Wettbewerber im Reduced-Mode")
- Wenn ein vorher in `blockiert` gelisteter Skill (z. B. `02-03-wettbewerber-marken-profil` selbst) jetzt fertig ist, aus `blockiert` entfernen
- `naechster_empfohlen`:
  - Wenn `02-04-branchenportal-recherche` noch offen: dieser, weil er auch auf der bestätigten `liste.md` aufbaut
  - Sonst: erster Audit-Skill nach Branchen-Eignung (für lokale Akteure `03-16-local-gmb-und-seo`, sonst `03-01-seo-sichtbarkeit-und-rankings`)
- Hinweis im Body: wenn `data/kunde.md` existiert, ist `04-01-positionierungs-analyse` jetzt theoretisch möglich (aber sinnvoller nach den Audit-Skills, damit Positionierungs-Achsen datengetrieben gewählt werden können)

### Schritt 9: Standard-Schlussformat im Chat

```
✓ 02-03-wettbewerber-marken-profil abgeschlossen.

Outputs (auf Drive):
- wettbewerber/SLUG-1.md — Marken-Profil Wettbewerber-1
- wettbewerber/SLUG-2.md — Marken-Profil Wettbewerber-2
- … (alle profilierten WBs)
- reports/04-wettbewerber-profile.html — Bundle-Report Side-by-Side
Status aktualisiert in: status.md

Ergebnis:
- Vollständig profiliert:  N Wettbewerber
- Im Reduced-Mode:         M Wettbewerber (Website nicht erreichbar)
- Hero-Test-Durchschnitt:  X,Y/5 über alle WBs
- Schwächste Dimension:    was wird angeboten | für wen | was ist anders | CTA

[Wenn Cluster gefunden:]
⚠ Cluster-Beobachtung:
- Wettbewerber A und Wettbewerber B haben sehr ähnliche Tonalität / USPs → möglicher Hinweis auf Marktlücke

[Wenn Reduced-Mode:]
⚠ Reduced-Mode-Wettbewerber:
- Wettbewerber X — Website nicht erreichbar → Empfehlung in liste.md auf empfehlung_profilieren: nein setzen

[Wenn data/kunde.md fehlt:]
ℹ 02-01-kunden-marken-profil fehlt noch — Side-by-Side-Vergleich im Bundle-Report nur über Wettbewerber, nicht gegen Kunde.

Nächste Schritte:
1. 02-04-branchenportal-recherche — sammelt Erwähnungen aller Akteure auf den im 02-02-wettbewerber-identifikation-Schema definierten Portalen
2. (parallel möglich) 03-01-seo-sichtbarkeit-und-rankings — Sistrix-Vergleich über alle profilierten WBs

Bei lokalen Branchen zusätzlich:
- 03-16-local-gmb-und-seo — Local-SEO-Vergleich

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/profil-prozess.md` — Wie der Skill mehrere Wettbewerber verarbeitet (Slug-Generierung, Sequenz, Rate-Limits, Fehler-Recovery)

**Kein eigenes Schema-File.** Schema und Methodik werden direkt aus `02-01-kunden-marken-profil/reference/` gelesen — siehe Verweise oben.

## Edge Cases

- **Liste hat 0 Einträge mit `empfehlung_profilieren: ja`** → Skill bricht ab mit Hinweis: "Keine Wettbewerber zum Profilieren in liste.md markiert. Bitte erst Empfehlungen prüfen und mindestens 1 auf `ja` setzen." Kein leerer Lauf.

- **Liste hat mehr als 7 Einträge mit `empfehlung_profilieren: ja`** → Auto-Kuration nach Priorität (kunde_genannt direkt > best_practice > regional top-3 nach Reviews) mit Hinweis im Schluss-Format, welche WBs ausgewählt wurden.

- **Wettbewerber-Website ist offline / 404** → Reduced-Mode (Schritt 5d). Profil wird trotzdem geschrieben, aber mit klaren Lücken-Markierungen. Empfehlung an Strategen, `empfehlung_profilieren: nein` zu setzen.

- **Cookie-Wall verhindert Crawl** → analog zu `02-01-kunden-marken-profil`: Apify-Optionen nutzen, ggf. in `crawl_hinweise` notieren.

- **Mehrsprachige Wettbewerber-Website** → Default-Sprache crawlen (typischerweise die Sprache der Wettbewerber-Region). Im Frontmatter `hauptsprache_detektiert` setzen. Keine zweite Sprache crawlen — Aufwand-Nutzen-Verhältnis bei Wettbewerbern ungünstig.

- **Wettbewerber ist eine Konzern-Marke mit Untermarken** (z. B. großer Konzern mit Spezialprodukt für die Branche) → Die im `liste.md` genannte Website crawlen, **nicht** auf die Konzern-Haupt-Domain ausweichen. Im Body Hinweis, falls relevant.

- **Zwei Wettbewerber teilen sich ein Brand-Dach** (z. B. zwei Standorte eines Franchise-Verbunds als regionale WBs gelistet) → Beide trotzdem einzeln profilieren, im Bundle-Report Cluster-Hinweis "Franchise-Cluster".

- **Apify-Token fehlt oder Rate-Limit erreicht** → klare Fehlermeldung, schon erstellte Profile bleiben erhalten, Skill schreibt zwischengespeicherten Stand in `status.md` (z. B. "3 von 5 Profilen erstellt, Abbruch wegen Rate-Limit — bei erneutem Aufruf werden die verbleibenden 2 ergänzt").

- **Bundle-Report wird sehr lang (5+ Profile)** → Pro Profil nur die Top-Highlights im aufgeklappten Modus (Hero-Test, Top-3 USPs, Touchpoints), Vollständiges Profil immer als Link auf die einzelne `wettbewerber/SLUG.md`-Datei.

- **`02-03-wettbewerber-marken-profil` wird erneut aufgerufen mit unveränderter Liste** → Pro existierender SLUG.md einzeln fragen (siehe Schritt 3), keine stillschweigende Überschreibung.

- **`liste.md` wurde nach erstem Profil-Lauf um Wettbewerber ergänzt** → Skill erkennt am Existenz-Check, welche Slugs bereits abgedeckt sind, profiliert nur die neuen. Im Schluss-Format ausweisen "N neue WBs profiliert, M bereits vorhandene Profile unverändert gelassen".

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive (via `drive.py upsert-text`); Pfad-Angaben im Frontmatter bezeichnen die Sub-Folder relativ zum MTA-Drive-Root
- Markdown + YAML-Frontmatter Hybrid-Format
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (in-place auf Drive)
- HTML-Reports basieren auf `reports/_shell.html` (aus Drive geladen) mit den verfügbaren CSS-Klassen
- **Schema-Konsistenz zu `02-01-kunden-marken-profil` ist Pflicht** — niemals abweichende Feldnamen oder Strukturen einführen, weil sonst `04-01-positionierungs-analyse` und andere Synthese-Skills brechen
