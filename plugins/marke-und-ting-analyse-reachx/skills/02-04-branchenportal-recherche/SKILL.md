---
name: 02-04-branchenportal-recherche
description: Recherchiert die Präsenz von Kunde und Wettbewerbern auf den im 02-02-wettbewerber-identifikation-Schema kuratierten Branchenportalen (Jameda, ProvenExpert, G2, Capterra, OMR Reviews, Trustpilot, MyHammer, ImmoScout24, wlw.de, etc.). Pro Portal mal Akteur wird Profil-URL, Bewertung, Anzahl Reviews, Aktivitätsstatus und Letzte-Aktivität extrahiert. Output ist wettbewerber/portale.md mit einer Portal-mal-Akteur-Matrix plus Auffälligkeiten-Block, plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext die Portal-Präsenz oder Reputation von Kunde und Wettbewerbern prüfen will - auch bei Phrasen wie "Branchenportal-Recherche", "Wer ist auf welchem Portal", "Sind die Wettbewerber auf Jameda / ProvenExpert / G2", "Portal-Recherche", "Reputations-Analyse Portale", "Bewertungs-Check auf den Branchenportalen", "wlw-Check", "Trustpilot-Vergleich". Setzt voraus, dass 02-02-wettbewerber-identifikation gelaufen ist und wettbewerber/liste.md den Status bestaetigt hat.
---

# Branchenportal-Recherche

Recherchiert für jeden Akteur (Kunde + alle bestätigten Wettbewerber) die Präsenz auf den in `wettbewerber/identifikation-schema.md` kuratierten Branchenportalen. Das Ergebnis ist eine **Portal-mal-Akteur-Matrix**, die zeigt:

- Wo ist welcher Akteur überhaupt vertreten?
- Wer hat wie viele Bewertungen?
- Wer hat die beste Reputation?
- Welcher Akteur ist auf welchem Portal stark / schwach / gar nicht vorhanden?

Damit ergänzt der Skill die Marken-Analyse um die **externe Sicht** — wie der Markt den Akteur über die Portale wahrnimmt, unabhängig von der eigenen Website.

Dieser Skill ist der **dritte und letzte Skill in Stufe 2** (Wettbewerber). Danach ist Stufe 2 abgeschlossen und die Audit-Skills von Stufe 3 können beginnen.

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

- "Branchenportal-Recherche"
- "Wer ist auf welchem Portal"
- "Sind die Wettbewerber auf Jameda / ProvenExpert / G2 / Capterra / MyHammer / [Portal]"
- "Portal-Recherche für [Kunde]"
- "Reputations-Analyse auf den Branchenportalen"
- "Bewertungs-Check auf den Branchenportalen"
- "wlw-Check", "Trustpilot-Vergleich", "G2-Matrix"
- Nutzer fragt nach Bewertungs-Anzahl, Review-Score oder Portal-Aktivität im MTA-Kontext

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden
- `02-02-wettbewerber-identifikation` Phase A + B abgeschlossen:
  - `wettbewerber/identifikation-schema.md` mit `status: bestaetigt` (für die Portal-Liste)
  - `wettbewerber/liste.md` mit `status: bestaetigt` (für die Akteure)
- Apify-Zugang verfügbar (für Portal-spezifische Scraper)
- Web-Search-Zugang (für Profil-URL-Auflösung, wo direkter Scrape nicht praktikabel ist)

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
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

### Schritt 1: Voraussetzungs-Check (Drive)

Wenn `META_ID` leer ist:

```
✗ Kein gültiger MTA-Folder.
Bitte zuerst 01-01-mta-projekt-init aufrufen.
```

Lies `wettbewerber/identifikation-schema.md` aus Drive:

```bash
SCHEMA_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "identifikation-schema.md") | .id')
if [ -z "$SCHEMA_ID" ]; then
  echo "✗ wettbewerber/identifikation-schema.md fehlt auf Drive."
  echo "Bitte erst 02-02-wettbewerber-identifikation Phase A laufen lassen, Schema reviewen und auf status: bestaetigt setzen."
  exit 1
fi
python3 "$DRIVE_PY" read "$SCHEMA_ID" > /tmp/identifikation-schema.md
```

Parse das YAML-Frontmatter — wenn `status` nicht `bestaetigt` ist:

```
✗ wettbewerber/identifikation-schema.md ist nicht bestätigt.
Bitte das Schema reviewen und auf status: bestaetigt setzen.
```

Lies `wettbewerber/liste.md` aus Drive:

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WETT_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -z "$LISTE_ID" ]; then
  echo "⏸ wettbewerber/liste.md fehlt auf Drive."
  echo "Bitte erst 02-02-wettbewerber-identifikation Phase B laufen lassen und die Liste reviewen."
  exit 1
fi
python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/liste.md
```

Wenn `status` in `liste.md` nicht `bestaetigt` ist: Abbruch mit Hinweis.

Prüfe optional, ob `data/kunde.md` auf Drive existiert:

```bash
KUNDE_ID=$(python3 "$DRIVE_PY" list-children "$DATA_ID" | jq -r '.[] | select(.name == "kunde.md") | .id')
[ -n "$KUNDE_ID" ] && python3 "$DRIVE_PY" read "$KUNDE_ID" > /tmp/kunde.md
```

Wenn nicht vorhanden: Hinweis im Schluss-Format, dass die Kunden-Zeile in der Matrix nur aus `meta.json`-Stammdaten kommt, nicht aus dem reichen Kunden-Profil.

### Schritt 2: Portal-Liste und Akteurs-Liste aufbauen

**Portal-Liste** aus `wettbewerber/identifikation-schema.md`:

- Alle Einträge unter `relevante_branchenportale` (Phase-A-Output) übernehmen
- Sortierung: nach `relevanz` (hoch → mittel → niedrig)
- **Auch Portale mit `relevanz: niedrig`** mitnehmen, aber im Output kennzeichnen — der Stratege entscheidet später, ob er sie in der MTA-Slide zeigt

**Akteurs-Liste** zusammensetzen aus:

1. **Kunde** — aus `meta.json` (`kunde`, `website`)
2. **Alle Wettbewerber aus `wettbewerber/liste.md`** — Filter:
   - **Default**: alle drei Kategorien, alle Einträge (nicht nur die mit `empfehlung_profilieren: ja`)
   - **Begründung**: Portal-Präsenz ist günstiger zu erheben als ein volles Marken-Profil, lohnt sich auch für die "optional"-WBs
   - **Reduced-Mode-WBs** (kein Web) trotzdem prüfen — manche haben nur eine Branchenportal-Präsenz und keine eigene Website

**Ausschluss** vor dem ersten Scrape:

- Wettbewerber, die nur in `aggregatoren_blocklist_zusatz` stehen (das wären ohnehin nicht in `liste.md`)
- Wettbewerber ohne Website UND ohne `name` (Daten-Lücke — überspringen)

### Schritt 3: Portal-mal-Akteur-Plan

Pro Kombination (Portal, Akteur) eine Recherche-Task erzeugen. Das ist die **Recherche-Matrix**:

```
       Portal-A  Portal-B  Portal-C  ...
Kunde   [task]   [task]   [task]
WB-1    [task]   [task]   [task]
WB-2    [task]   [task]   [task]
...
```

Bei 1 Kunde + 8 Wettbewerbern und 6 Portalen sind das 54 Tasks. Pragmatisch:

- **Pro Portal sequenziell** (nicht parallel): erst Portal-A für alle Akteure, dann Portal-B, etc. — verhindert, dass mehrere Apify-Actors gleichzeitig laufen
- **Innerhalb eines Portals parallel möglich**, wenn der Portal-Scraper batch-fähig ist (z. B. Apify-Actor akzeptiert mehrere Such-Inputs in einem Run)

Reihenfolge der Portale: nach `relevanz` absteigend (hoch → mittel → niedrig). So sind die wichtigsten Daten zuerst da, falls der Lauf abbricht.

### Schritt 4: Pro Portal die Akteurs-Präsenz erheben

Für jedes Portal die Recherche-Methode aus `reference/portal-scraper-mapping.md` ableiten:

- **Methode A — Apify-Portal-Scraper (dediziert)** (wenn ein portal-spezifischer Apify-Actor existiert): direkter Scraper-Aufruf mit Akteurs-Liste
- **Methode A2 — Apify Website Content Crawler (generisch, Bot-Protector-fähig)** (wenn kein dedizierter Actor existiert UND das Portal einen Bot-Protector hat — z.B. Jameda, Cloudflare-geschützte Portale): `apify/website-content-crawler` mit Playwright-Chrome + Residential-Proxy. Profil-URL vorab via Web-Search ermitteln, dann an den Crawler als `startUrls` übergeben. Standard-Config siehe `reference/portal-scraper-mapping.md` → Methoden-Glossar.
- **Methode B — Web-Search + URL-Pattern** (wenn Portal ohne Bot-Schutz öffentlich crawlbar): `<akteurs-name> site:<portal-domain>`, Top-Treffer als Profil-URL nehmen
- **Methode C — Portal-interne Suche via Apify-Browser-Actor** (wenn Portal hinter Login / JS-Wall ohne öffentliche URL-Pattern): `apify/puppeteer-scraper` mit Custom Page-Function, sucht im Portal nach dem Akteur

Pro (Portal, Akteur):

1. **Profil-Auffindung**: Methode A/A2/B/C versuchen — in der Reihenfolge, die im Mapping für dieses Portal explizit dokumentiert ist. **Niemals Methode B versuchen, wenn das Mapping A2 vorschreibt** (das Portal hat Bot-Schutz, B würde zu 403/429 führen).
2. **Bei Fund**:
   - Profil-URL extrahieren
   - Bewertung (Score, z. B. 4.3/5 oder 87/100 — Portal-Skala bewahren)
   - Anzahl Reviews
   - Letzte Aktivität (letzte Review-Datum, letzter Profil-Update, falls erkennbar)
   - Zusätzliche portal-spezifische Felder (siehe Tabelle in `reference/portal-scraper-mapping.md`, z. B. Sieger-/Top-Listen-Plakette, Verifizierungs-Status, Premium-Eintrag ja/nein)
3. **Bei keinem Fund**: Status `nicht_gelistet`, kurze Begründung (z. B. "Portal-Suche zu generisch" oder "Profil offline")
4. **Bei Fehler**: Status `recherche_fehlgeschlagen`, Fehler-Typ notieren. **Wenn der Fehler ein Bot-Protector-Signal ist** (403/429/Cloudflare-Challenge im Response-HTML) und die genutzte Methode war B oder ein direkter Crawl: dokumentiere im Mapping-File einen neuen Eintrag mit Methode A2 und führe den Lauf für dieses Portal mit A2 erneut aus. Skill setzt den `methode`-Eintrag in der Output-Datei auf `A2_after_bot_protector_fallback`.

**Wichtig**: das Schema in `reference/portale-output-schema.md` definiert das Output-Format pro Eintrag. Strikt einhalten — die Synthese-Skills lesen das.

### Schritt 5: Aktivitäts-Indikator pro Treffer setzen

Aus den erhobenen Daten einen einfachen Status ableiten (gleiche Skala wie in `02-01-kunden-marken-profil` Touchpoints):

| Status | Kriterium |
|---|---|
| `aktiv` | Profil vorhanden + mindestens eine Aktivität in den letzten 6 Monaten (neue Review, Profil-Update, Antwort auf Review) |
| `gelistet_ruhend` | Profil vorhanden, aber keine Aktivität in den letzten 6 Monaten |
| `nicht_gelistet` | Profil bei der Suche nicht gefunden |
| `unklar` | Recherche teilweise erfolgreich, aber nicht eindeutig (z. B. Profil gefunden, aber Aktivitäts-Datum nicht extrahierbar) |

### Schritt 6: Auffälligkeiten und Cluster

Aus der Gesamt-Matrix die strategisch interessanten Beobachtungen extrahieren:

- **Lücken beim Kunden**: Wo ist der Kunde nicht gelistet, aber zwei oder mehr Wettbewerber sind aktiv? → MTA-Empfehlung: Profil anlegen
- **Verschlafene Portale**: Wo ist der Kunde gelistet, aber `gelistet_ruhend`, während Wettbewerber aktiv sind? → MTA-Empfehlung: Profil reaktivieren
- **Stärke-Indikatoren**: Wo hat der Kunde signifikant mehr Reviews / höheren Score als alle Wettbewerber? → MTA-Story: "wir haben hier den Lead"
- **Portal-Sättigung**: Portale, wo praktisch alle Akteure mit ähnlichem Score und ähnlicher Review-Anzahl präsent sind → Hinweis "Marktplatz-typisch, keine Differenzierungs-Chance allein über Profil"
- **Premium-Plakette-Verbreitung**: Wer hat das Premium-Badge auf welchem Portal? → relevant für Reputation-Audit-Story

Diese Beobachtungen kommen in die Output-Datei in einen eigenen `auffaelligkeiten`-Abschnitt im Frontmatter plus im Body als `## Auffälligkeiten`-Sektion.

### Schritt 7: `wettbewerber/portale.md` nach Drive schreiben

Baue die Output-Datei lokal im Cache zusammen (Format in `reference/portale-output-schema.md`) und lade sie nach Drive in den `wettbewerber/`-Sub-Folder hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$WETT_ID" "portale.md" \
  ~/.cache/reachx-mta/"$SLUG"/portale.md "text/markdown"
```

YAML-Frontmatter mit:

- Skill-Metadaten + Recherche-Provenienz (welche Methode pro Portal, wann gelaufen)
- Portal-Liste (mit Stamm-Infos aus `identifikation-schema.md`)
- Akteurs-Liste (mit Stamm-Infos aus `liste.md` und `meta.json`)
- **Matrix**: pro (Portal, Akteur)-Kombination ein Eintrag mit URL, Score, Reviews, Aktivität, Status, optionalen Zusatz-Feldern
- Auffälligkeiten (siehe Schritt 6)

Body strukturiert nach:

- Übersicht (Anzahl Portale, Akteure, Gesamt-Tasks, Methoden-Mix)
- Pro Portal eine Sektion mit eingebetteter Mini-Matrix (Portal-Spalte aus der großen Matrix)
- Auffälligkeiten als eigene Sektion am Ende
- Lücken-Sektion (welche Tasks `recherche_fehlgeschlagen` waren — damit der Stratege manuell nachprüfen kann)

### Schritt 8: HTML-Report `reports/05-branchenportale.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `reports/_shell.html` aus Drive und baue einen Bundle-Report:

- `{{TITLE}}` → `Branchenportal-Recherche · KUNDE`
- `{{EYEBROW}}` → `MTA-Wettbewerber · Portale`
- `{{DISPLAY_NAME}}` → `Branchenportal-Recherche: KUNDE`
- `{{META_LINE}}` → `N Akteure × M Portale · Recherche-Datum DATUM · Generiert: heute`
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip oben**: Anzahl Akteure, Anzahl Portale, Gesamt-Coverage in % (wieviele (Portal, Akteur)-Kombis mit Status `aktiv` oder `gelistet_ruhend`), Anzahl Auffälligkeiten gefunden
  - **Sticky-TOC**: Übersicht, eine TOC-Ankerung pro Portal, Auffälligkeiten, Lücken
  - **Master-Matrix**: HTML-Tabelle mit Akteuren als Zeilen und Portalen als Spalten, jede Zelle als kompakter Badge:
    - `aktiv` → grünes Badge mit Score + Review-Count
    - `gelistet_ruhend` → gelbes Badge mit Score + Review-Count
    - `nicht_gelistet` → graues Badge "—"
    - `unklar` → orangefarbenes Badge "?"
  - **Pro Portal** ein `details class="dim"`-Block, default zugeklappt, mit detaillierter Akteurs-Liste (Profil-URL, Score, Reviews, letzte Aktivität)
  - **Auffälligkeiten-Block** prominent als `.suggestion`-Block: Top 3-5 strategische Beobachtungen mit klarer Handlungs-Empfehlung
  - **Lücken-Block** unten: Tasks, die nicht erfolgreich abgeschlossen werden konnten — als To-Do für den Strategen
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · Branchenportal-Recherche`

Lokal zusammenbauen und nach Drive hochladen:

```bash
python3 "$DRIVE_PY" upsert-text "$REPORTS_ID" "05-branchenportale.html" \
  ~/.cache/reachx-mta/"$SLUG"/05-branchenportale.html "text/html"
```

### Schritt 9: Dashboard-Update

Lies `reports/index.html` aus Drive, modifiziere und schreibe per `upsert-text` zurück:

- Stat-Strip um Portal-Coverage erweitern (wenn das Schema dafür ein Feld hat — sonst überspringen)
- "Erledigt"-Sektion erweitern um `02-04-branchenportal-recherche`
- Reports-Liste um `05-branchenportale.html` erweitern
- "Nächster empfohlener Schritt": jetzt erster Audit-Skill (siehe Schritt 11)
- Markiere Stufe 2 als abgeschlossen, wenn `02-01-kunden-marken-profil` + `02-02-wettbewerber-identifikation` + `02-03-wettbewerber-marken-profil` + `02-04-branchenportal-recherche` alle in `schritte_done`

### Schritt 10: `status.md` aktualisieren

`status.md` liegt im MTA-Root-Folder auf Drive. Lies, modifiziere und schreibe per `upsert-text` zurück.

Nach Regeln aus `contracts.md` Abschnitt 3:

- `02-04-branchenportal-recherche` in `schritte_done`
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Hinweisen
- Falls Recherche-Tasks fehlgeschlagen sind: Hinweis im Body, `unblockiert`-Eintrag NICHT setzen (das ist nur ein Hinweis, kein Block)
- `naechster_empfohlen`: erster Audit-Skill je nach Branchen-Typ:
  - Lokale Akteure → `03-16-local-gmb-und-seo`
  - Andere → `03-01-seo-sichtbarkeit-und-rankings`

### Schritt 11: Standard-Schlussformat im Chat

```
✓ 02-04-branchenportal-recherche abgeschlossen.

Outputs (auf Drive):
- wettbewerber/portale.md — Portal-mal-Akteur-Matrix
- reports/05-branchenportale.html — visueller Report mit Master-Matrix
Status aktualisiert in: status.md

Recherche-Statistik:
- Akteure:        N (Kunde + (N-1) Wettbewerber)
- Portale:        M
- Tasks gesamt:   N × M = T
- aktiv:          A
- gelistet_ruhend: R
- nicht_gelistet: NL
- recherche_fehlgeschlagen: F (manuell prüfen)

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- Kunde fehlt auf Portal-X, während Wettbewerber A und B dort aktiv sind
- Kunde hat auf Portal-Y die meisten Reviews und höchsten Score — Stärke-Story für MTA
- Portal-Z zeigt Sättigung (alle Akteure 4,5+/5) — keine Differenzierungs-Chance allein über Listing

[Wenn Lücken:]
ℹ Recherche-Lücken:
- Portal-X hat Login-Wall — manuelle Recherche durch Strategen empfohlen

✓ Stufe 2 (Wettbewerber) abgeschlossen.

Nächste Schritte:
1. 03-01-seo-sichtbarkeit-und-rankings — Sistrix-Sichtbarkeit für Kunde + Wettbewerber (erster Audit-Skill in Stufe 3)
2. (parallel möglich) 03-16-local-gmb-und-seo — wenn Kunde lokal-bezogen ist
3. (später) 03-14-web-tech-und-tracking — Tech-Stack und Performance

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/portal-scraper-mapping.md` — pro Portal: welche Recherche-Methode (Apify-Actor, Web-Search, Custom-Scrape), URL-Pattern, portal-spezifische Zusatz-Felder
- `reference/portale-output-schema.md` — Output-Format für `wettbewerber/portale.md` (Frontmatter-Schema + Body-Struktur)

**Kein eigenes Akteurs-Schema-File** — Akteure (Kunde, Wettbewerber) werden aus den vorhandenen Datei-Strukturen (`meta.json`, `wettbewerber/liste.md`) gelesen.

## Edge Cases

- **identifikation-schema.md hat 0 Branchenportale** → seltenes Szenario, aber möglich (sehr nischige B2B-Branche). Skill bricht ab mit Hinweis: "Keine Branchenportale im Identifikations-Schema. Wenn doch welche relevant sind: Phase A erneut anpassen und unter `relevante_branchenportale` ergänzen."

- **Akteurs-Liste hat nur den Kunden (keine WBs)** → Recherche trotzdem durchführen — die Kunden-Zeile allein ist wertvoll. Im Schluss-Format ausweisen, dass kein WB-Vergleich möglich war.

- **Portal hat Login-Wall** (z. B. G2 für detaillierte Reviews) → Versuche Methode B (Web-Search nach Profil-URL), erfasse Basis-Daten (URL, sichtbarer Score, Reviews-Count vor Login). Im Body ausweisen, dass tiefer-gehende Daten nur mit manuellem Login zugänglich.

- **Akteur ist auf einem Portal unter abweichendem Namen gelistet** (z. B. "Beispiel GmbH" auf der Website, aber "Beispiel Solutions" auf G2) → Web-Search mit beiden Schreibweisen, plus `synonyme` aus `data/kunde.md` (falls vorhanden). Bei mehreren Treffern: Mensch-in-der-Schleife — Skill listet alle Kandidaten, fragt den Strategen welcher gemeint ist (oder im autonomen Modus: nimmt den ersten mit passender Branche).

- **Portal hat sich umbenannt / wurde abgeschaltet** → Status `recherche_fehlgeschlagen` mit Fehler-Typ `portal_unreachable`, Hinweis im Schluss-Format, dass `identifikation-schema.md` aktualisiert werden sollte, plus Pflege des `branchenportale-mapping.md` im `02-02-wettbewerber-identifikation`-Skill (TODO für Skill-Wartung).

- **Apify-Token fehlt** → klare Fehlermeldung, kein Fallback. Wenn `web-search` allein funktioniert, kann der Skill im "Basis-Modus" laufen (nur URL-Auffindung, keine Score-Daten) — aber explizit ausweisen.

- **Sehr großer Lauf (mehr als 10 Akteure × 8 Portale = 80+ Tasks)** → Im Vorfeld den Strategen informieren ("80 Recherche-Tasks geplant, ca. X Minuten + Y Apify-Compute-Units"). Bei sehr vielen Akteuren: Vorschlag, die Recherche-Reichweite auf die Top-WBs zu beschränken.

- **Doppelte Portal-Einträge** (z. B. wenn `Google Reviews` und `Google Business Profile` separat im Schema stehen, faktisch aber das gleiche sind) → Skill erkennt das Pattern und vereinigt sie zu einem Eintrag im Output, mit Hinweis im Body.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive (via `drive.py upsert-text`); Pfad-Angaben im Frontmatter bezeichnen die Sub-Folder relativ zum MTA-Drive-Root
- Markdown + YAML-Frontmatter Hybrid-Format
- Standard-Schlussformat im Chat
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (in-place auf Drive)
- HTML-Report basiert auf `reports/_shell.html` (aus Drive geladen)
- **Portal-Score-Skalen unverändert lassen** — niemals normalisieren (4,3/5 bleibt 4,3/5, 87/100 bleibt 87/100); die Normalisierung ist Aufgabe der Synthese-Skills, die Roh-Skalen sind die Wahrheit
