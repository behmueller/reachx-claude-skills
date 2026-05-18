---
name: 03-20-local-gmb-wettbewerb
description: Systematischer Local-GMB-Wettbewerbsvergleich für eine MTA - liefert pro Akteur (Kunde mit allen Standorten plus bestätigte regionale Wettbewerber) die Review-Velocity in Buckets (neue Reviews der letzten 1/3/6/12 Monate), die GMB-Profil-Reife (Kategorien-Anzahl, Attribute, Foto-Anzahl, Posts-Frequenz, Antwort-Quote, Profil-Vollständigkeit) und einen robusten Local-Visibility-Score (LVS) 0-100 aus drei gewichteten Blöcken - A Local-Pack-Präsenz, B Review-Substanz, C GMB-Profil-Reife. Der LVS ist stabiler als der Sistrix-Sichtbarkeitsindex, der bei kleinen lokalen Akteuren zu volatil ist. Nutzt Schema-vor-Lauf - Phase A schlägt Akteur-Set, Standorte, Local-Pack-Keywords und LVS-Block-Gewichtung vor, Stratege bestätigt, Phase B scrapt via Apify Google-Maps- und Review-Scraper. Wenn 03-16-local-gmb-und-seo bereits ein bestätigtes Local-SEO-Schema hat, wird dieses als Basis übernommen statt ein zweites zu verlangen. Output ist audits/local-gmb-wettbewerb.md mit LVS-Ranking plus Auffälligkeiten, audits/local-gmb-wettbewerb.csv mit einer Zeile pro Akteur, plus HTML-Report mit expandierbaren Akteur-Zeilen. Daten-Lieferant für die Local-SEO-Bewertung in 04-02-kanal-chancen-analyse. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext den lokalen Wettbewerbsvergleich, Review-Velocity, GMB-Profil-Reife oder einen Local-Visibility-Score sehen will - auch bei "Local-Wettbewerbsvergleich", "GMB-Wettbewerb", "Review-Velocity", "wer baut Reviews auf", "Local-Visibility-Score", "LVS", "GMB-Profil-Reife vergleichen", "lokale Wettbewerber im Maps-Vergleich", "Local-Pack-Dominanz", "wie stark sind die lokalen Wettbewerber". Setzt 01-01-mta-projekt-init voraus, idealerweise auch 02-02-wettbewerber-identifikation und 03-16-local-gmb-und-seo - läuft sonst auf reduzierter Basis.
---

# Local-GMB-Wettbewerbsvergleich

Local-SEO-Wettbewerbs-Skill in Stufe 3. **Schema-vor-Lauf-Pattern** (siehe `contracts.md` Abschnitt 8).

`03-16-local-gmb-und-seo` auditiert primär das GMB-Profil **des Kunden** (Vollständigkeit, NAP-Konsistenz, Review-Sentiment). Dieser Skill liefert den **systematischen Wettbewerber-Vergleich**: er stellt Kunde und regionale Wettbewerber auf einer gemeinsamen Mess-Skala gegenüber und verdichtet das Ergebnis zu einem **Local-Visibility-Score (LVS)** 0-100 pro Akteur. Der LVS ist der Daten-Lieferant für die Local-SEO-Bewertung in `04-02-kanal-chancen-analyse`.

Drei Mess-Achsen pro Akteur:

1. **Review-Velocity** — neue Reviews pro Zeitfenster (letzte 1 / 3 / 6 / 12 Monate). Zeigt, wer aktiv aufbaut und wer Substanz verliert — etwas, das eine reine Gesamt-Review-Zahl verbirgt. Ein Akteur mit 400 Reviews, aber 0 in den letzten 6 Monaten, ist schwächer als einer mit 120 Reviews und 30 im letzten Quartal.
2. **GMB-Profil-Reife** — Kategorien-Anzahl, Attribute, Foto-Anzahl, Posts-Frequenz, Antwort-Quote auf Reviews, Profil-Vollständigkeit. Die kontrollierbaren Stellschrauben, die ein Akteur selbst in der Hand hat.
3. **Local-Pack-Präsenz** — Anteil Top-3- und Top-10-Platzierungen über alle Standort × Service-Keyword-Kombinationen.

Daraus der **LVS**: ein gewichteter 0-100-Score aus drei Blöcken (A Local-Pack-Präsenz, B Review-Substanz, C GMB-Profil-Reife) — robuster als der Sistrix-Sichtbarkeitsindex, der bei kleinen lokalen Akteuren mit `SI < 0,05` zu volatil ist (siehe `contracts.md` Abschnitt 13). Für lokale Akteure ist der LVS das Leitsignal, der Sistrix-VI nur sekundär.

## Abgrenzung zu `03-16-local-gmb-und-seo`

| Aspekt | `03-16-local-gmb-und-seo` | `03-20-local-gmb-wettbewerb` (dieser Skill) |
|---|---|---|
| Fokus | GMB-Profil des **Kunden** (Tiefe) | **Wettbewerber-Vergleich** (Breite) auf einer Skala |
| Review-Sicht | Sentiment entlang branchen-typischer Themen | **Velocity** in Zeit-Buckets (1/3/6/12 Monate) |
| Kern-Output | Profil-Status, NAP-Konsistenz, Review-Sentiment | **LVS-Ranking** 0-100 pro Akteur |
| Empfänger | Stratege für Kunden-Maßnahmen | `04-02-kanal-chancen-analyse` als Local-SEO-Datenpunkt |

Die beiden Skills sind komplementär. `03-20` ist **kein Ersatz** für `03-16` — wenn `03-16` schon lief, nutzt `03-20` dessen bestätigtes Schema als Basis (siehe Schritt 1) und ergänzt die Velocity- und LVS-Sicht.

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf Apify, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z.B. Wettbewerber-Liste, ggf. Override-Argument)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="03-20-local-gmb-wettbewerb"
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

- "Local-Wettbewerbsvergleich" / "GMB-Wettbewerb"
- "Review-Velocity" / "wer baut Reviews auf"
- "Local-Visibility-Score" / "LVS"
- "GMB-Profil-Reife vergleichen"
- "lokale Wettbewerber im Maps-Vergleich"
- "Local-Pack-Dominanz"
- "wie stark sind die lokalen Wettbewerber"
- Nutzer fragt im MTA-Kontext nach dem systematischen Local-Vergleich Kunde gegen Wettbewerber

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json` vorhanden (`region`, `branche` Pflichtfelder)
- **Stark empfohlen**: `02-02-wettbewerber-identifikation` mit `status: bestaetigt` → `wettbewerber/liste.md` enthält Kategorie `regional`
- **Stark empfohlen**: `03-16-local-gmb-und-seo` mit bestätigtem Schema (`audits/local-gmb-schema.md`, `status: bestaetigt`) → wird als Schema-Basis übernommen, dann entfällt eine zweite Schema-Bestätigung
- **Empfohlen**: `02-01-kunden-marken-profil` → `data/kunde.md` mit `touchpoints_gefunden` (GMB-Link, Filialen)
- **Optional**: `data/briefing.md` für vom Kunden genannte Standorte
- **Pflicht-MCP**: Apify (Google-Maps-Scraper + Review-Scraper). Ohne Apify ist der Skill nicht sinnvoll lauffähig → sauberer Abbruch.

### Pflicht-MCP — Health-Check vor dem Lauf

Nach `contracts.md` Abschnitt 11. Vor dem ersten echten Scrape (nicht nur am Skill-Start) ein billiger Apify-Test-Call (`search-actors` mit Limit 1). Schlägt er fehl:

```text
✗ Pflicht-MCP 'apify' nicht erreichbar.
Bitte in /mcp verbinden (ggf. neu authentifizieren) und Skill erneut aufrufen.
```

Apify-Sessions überleben PC-Standby / lange Pausen nicht (`Session ID not found`) und werden von parallelen Clients auf demselben Token invalidiert. Bei Session-Bruch **abbrechen mit Reconnect-Hinweis** statt jeden weiteren Akteur einzeln scheitern zu lassen — bereits geschriebene Teil-Outputs im Schluss-Format erwähnen.

### Credential-Disziplin

Apify-Token wird ausschließlich über `APIFY_TOKEN` erkannt — keine breite Credential-Suche (siehe `contracts.md` Abschnitt 11):

```bash
[ -n "$APIFY_TOKEN" ] || { echo "✗ APIFY_TOKEN nicht gesetzt."; exit 1; }
```

## Ablauf

Schema-vor-Lauf-Pattern. Bei jedem Aufruf entscheidet der Skill in Schritt 1, in welcher Phase er ist.

### Schritt 1: Drive-Bootstrap und Phasen-Entscheidung

Drive-Bootstrap (siehe `contracts.md` Abschnitt 1):

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

Wenn `meta.json` fehlt: Abbruch nach `contracts.md` Abschnitt 1 ("01-01-mta-projekt-init zuerst aufrufen").

Schema-Datei dieses Skills: `audits/local-gmb-wettbewerb-schema.md` im `audits/`-Sub-Folder.

**Phasen-Entscheidung:**

```text
1. Existiert audits/local-gmb-wettbewerb-schema.md auf Drive?
   (drive.py find_by_name "$AUDITS_ID" "local-gmb-wettbewerb-schema.md")
   - Nein → Phase A (Schema generieren — siehe Schritt 2 zur Basis-Wahl)
   - Ja, status: vorgeschlagen → freundlicher Abbruch mit Hinweis auf Strategen-Review
   - Ja, status: bestaetigt → Phase B (eigentliches Audit)
   - Ja, status: skip_national_online → Skill bewusst geskippt, kein Lauf, Hinweis "Override mit trotzdem laufen möglich"
   - Ja, anderer Status → Abbruch mit Hinweis auf erlaubte Werte

2. Existiert audits/local-gmb-wettbewerb.md auf Drive bereits?
   - Nein → weiter mit Phase B
   - Ja → fragen: überschreiben / Backup-und-neu / abbrechen
```

### Schritt 2: Schema-Basis-Wahl — `03-16`-Schema wiederverwenden statt zweites Schema verlangen

Bevor der Skill in Phase A ein eigenes Schema generiert, prüft er, ob `03-16-local-gmb-und-seo` bereits ein bestätigtes Schema hinterlassen hat:

```text
Lies audits/local-gmb-schema.md (drive.py find_by_name "$AUDITS_ID" "local-gmb-schema.md").
```

Drei Fälle:

- **`local-gmb-schema.md` existiert mit `status: bestaetigt`** → der Skill **erbt** die bereits bestätigten Felder `standorte_kunde`, `suchradius_km`, `local_pack_keywords`, `lokale_wettbewerber` daraus. Phase A ist dann **schlank**: der Skill generiert `local-gmb-wettbewerb-schema.md` und muss vom Strategen **nur noch die LVS-Block-Gewichtung und das Akteur-Set bestätigen lassen** (alles Local-spezifische ist schon geprüft). Im Schema-Frontmatter `basis_schema: local-gmb-schema.md` vermerken, im Body klar schreiben: "Standorte und Local-Pack-Keywords aus dem bereits bestätigten 03-16-Schema übernommen — bitte nur LVS-Gewichtung und Akteur-Set prüfen."
- **`local-gmb-schema.md` existiert mit `status: skip_national_online`** → `03-16` hat den Kunden als national/online eingestuft. Dieser Skill ist dann ebenfalls Skip-Kandidat (siehe Skip-Logik), es sei denn der Stratege gibt `trotzdem laufen`.
- **`local-gmb-schema.md` fehlt oder ist nur `vorgeschlagen`** → der Skill generiert ein **eigenständiges, vollständiges** Schema (Standorte, Suchradius, Local-Pack-Keywords plus LVS-Gewichtung) und lässt es komplett reviewen. Empfehlung im Body: idealerweise zuerst `03-16` laufen lassen, das spart die Doppel-Bestätigung.

Pragmatik: Es gibt **nie zwei konkurrierende Local-Schemata**, die der Stratege getrennt pflegen muss. Das `03-20`-Schema ist entweder ein schlanker Aufsatz auf dem `03-16`-Schema (häufiger Fall) oder eigenständig vollständig (wenn `03-16` noch nicht lief).

### Skip-Logik (vor Phase A)

Identisch zum Prinzip in `03-16` (`contracts.md` Abschnitt 13 — Volatilitäts- und Aggregat-Disziplin). Der Skill ist gestaffelt-optional: er läuft nur sinnvoll für Kunden mit Local-Bezug.

**Skip-Kandidat**, wenn:

- `local-gmb-schema.md` existiert mit `status: skip_national_online`, ODER
- (kein `03-16`-Schema vorhanden) UND Region-Definition aus `wettbewerber/identifikation-schema.md.region_definition.ausdehnung` in {national, dach, international} UND keine GMB-Touchpoints in `data/kunde.md.touchpoints_gefunden` UND `wettbewerber/liste.md` enthält keine Kategorie `regional`

**Override**: Nutzer-Argument `trotzdem laufen` (oder `force`) → Skip-Logik wird übersprungen.

Bei Skip-Kandidat ohne Override: schreibe `audits/local-gmb-wettbewerb-schema.md` mit `status: skip_national_online` und Begründung, setze den Skill in `status.md` auf `schritte_done` mit Vermerk "geskippt — kein Local-Bezug", aktualisiere `status.md` und Dashboard, gib im Chat aus:

```text
✗ 03-20-local-gmb-wettbewerb geskippt — kein Local-Bezug erkannt.

Begründung:
- Region-Definition: national/online (oder: 03-16 hat bereits skip_national_online gesetzt)
- Keine GMB-Touchpoints in data/kunde.md
- Keine regionalen Wettbewerber in wettbewerber/liste.md

Wenn das falsch ist (Kunde hat doch lokale Filialen oder lokales Service-Gebiet), Skill mit Argument "trotzdem laufen" erneut aufrufen.

Nächste Schritte:
1. <nächster relevanter Audit-Skill>

Sag mir, welcher als nächster.
```

---

## Phase A — Schema generieren

### Schritt A.1: Voraussetzungs-Check und Basis-Wahl

Drive-Bootstrap wie oben. Lies aus Drive (`find_by_name` + `read_text`):

- `meta.json` (Pflicht — `region`, `branche`) — bereits in `/tmp/meta.json`
- `audits/local-gmb-schema.md` (das `03-16`-Schema — Basis-Wahl nach Schritt 2)
- `wettbewerber/liste.md` via `find_by_name(WB_ID, "liste.md")` (empfohlen — `status: bestaetigt`, Kategorie `regional`)
- `data/kunde.md` via `find_by_name(DATA_ID, "kunde.md")` (empfohlen — `touchpoints_gefunden`)
- `data/briefing.md` via `find_by_name(DATA_ID, "briefing.md")` (optional — vom Kunden genannte Standorte)
- `wettbewerber/identifikation-schema.md` (optional — `region_definition` für die Skip-Logik)

Wenn `wettbewerber/liste.md` fehlt oder nicht bestätigt: Hinweis im Schema-Body, dass der Skill auf reduzierter Wettbewerbs-Basis läuft (im Extrem nur Kunde). Empfehlung: erst `02-02-wettbewerber-identifikation` bestätigen.

### Schritt A.2: Skip-Bedingung prüfen

Wende die oben beschriebene Skip-Logik an. Bei Skip-Kandidat ohne Override: Schema mit `status: skip_national_online` schreiben, Skip-Schluss-Format ausgeben, kein Phase-A-Vollformat.

### Schritt A.3: Akteur-Set festlegen

- **Kunde** — immer dabei, **alle Standorte** aus `standorte_kunde` (geerbt aus dem `03-16`-Schema oder neu bestimmt nach derselben Quellen-Reihenfolge wie `03-16` Schritt A.3: `data/kunde.md.touchpoints_gefunden` → `data/briefing.md.standorte` → Branchen-Default).
- **Regionale Wettbewerber** aus `wettbewerber/liste.md` (Kategorie `regional`, `empfehlung_profilieren: ja`).
- **Auto-Ergänzung in Phase B**: lokale Wettbewerber, die im Local-Pack häufig auftauchen, aber nicht in `liste.md` stehen → in Phase B als `auto_ergaenzt` markiert, Auffälligkeit `local_wb_nicht_in_liste`.

Hard-Cap: max 10 Wettbewerber im Lauf (Apify-Credit-Disziplin).

### Schritt A.4: Standorte und Local-Pack-Keywords

- Wenn aus `03-16`-Schema geerbt: `standorte_kunde`, `suchradius_km`, `local_pack_keywords` 1:1 übernehmen, im Body nur referenzieren ("aus bestätigtem 03-16-Schema").
- Wenn eigenständig: nach derselben Methodik wie `03-16` (Schritte A.3–A.6) — Standorte, Suchradius nach Branchen-Default, 5–10 Basis-Keywords × 2–3 Modifier-Typen, Hard-Cap 30 Local-Pack-Queries pro Standort. Branchen-Defaults für den Suchradius siehe `reference/lvs-methodik.md`.

### Schritt A.5: LVS-Block-Gewichtung vorschlagen

Der LVS aggregiert drei Blöcke. Default-Gewichtung (siehe `reference/lvs-methodik.md`):

```yaml
lvs_gewichtung:
  block_a_local_pack: 40      # Local-Pack-Präsenz
  block_b_review_substanz: 35 # Volumen + Velocity + Durchschnitts-Rating
  block_c_profil_reife: 25    # GMB-Profil-Reife
# Summe muss 100 ergeben.
```

Branchen-Anpassung im Vorschlag begründen:

- **Stark such-getriebene Branchen** (Arzt, Anwalt, Handwerk-Notdienst): Block A höher (45–50), weil die Local-Pack-Position fast direkt Anfragen bedeutet.
- **Stark reputations-getriebene Branchen** (Restaurant, Hotel, Friseur, Beauty): Block B höher (40–45), weil Reviews die Entscheidung dominieren.
- **Frühe / junge Akteure** im Markt: Default belassen — Profil-Reife (Block C) zeigt schnelle Hebel auf.

Der Stratege bestätigt oder verschiebt die Gewichtung im Review. Die Summe muss exakt 100 ergeben — Phase B validiert das.

### Schritt A.6: Review-Velocity-Buckets

Die Velocity-Buckets sind fix und nicht zu konfigurieren (für Vergleichbarkeit über MTAs hinweg):

```yaml
review_velocity_buckets:
  - letzte_1_monat
  - letzte_3_monate
  - letzte_6_monate
  - letzte_12_monate
```

Im Schema-Body kurz erklären: jeder Bucket ist **kumulativ ab heute rückwärts** (z.B. `letzte_3_monate` zählt alle Reviews der letzten 90 Tage, schließt `letzte_1_monat` ein). In Phase B wird zusätzlich ein abgeleiteter **Velocity-Trend** berechnet (siehe `reference/lvs-methodik.md`).

### Schritt A.7: `audits/local-gmb-wettbewerb-schema.md` nach Drive schreiben

Erzeuge das Schema lokal nach `reference/wettbewerb-schema-template.md`, setze `status: vorgeschlagen`, lade hoch:

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "local-gmb-wettbewerb-schema.md" \
  /tmp/local-gmb-wettbewerb-schema.md "text/markdown"
```

Sektionen siehe `reference/wettbewerb-schema-template.md`. Kern: Frontmatter mit Akteur-Set, Standorten, LVS-Gewichtung, Velocity-Buckets, Basis-Schema-Referenz; Body mit Begründungen und einer Pflicht-Review-Sektion.

### Schritt A.8: Schluss-Format Phase A

Variante 1 — **Basis aus `03-16` geerbt** (schlanker Review):

```text
✓ 03-20-local-gmb-wettbewerb Phase A abgeschlossen.

Outputs (auf Drive):
- audits/local-gmb-wettbewerb-schema.md — Wettbewerbs-Schema (status: vorgeschlagen)

Basis: Standorte, Suchradius und Local-Pack-Keywords aus dem bereits bestätigten
03-16-Schema übernommen — nur LVS-Gewichtung und Akteur-Set sind neu zu prüfen.

Konfigurations-Vorschlag:
- Akteur-Set:          Kunde (S Standorte) + W regionale Wettbewerber
- LVS-Gewichtung:      A Local-Pack 40 · B Review-Substanz 35 · C Profil-Reife 25
- Velocity-Buckets:    1 / 3 / 6 / 12 Monate (fix)
- Local-Pack-Keywords: K (aus 03-16-Schema übernommen)

⏸ Pflicht-Review durch den Strategen
Bitte prüfen: Akteur-Set vollständig? LVS-Gewichtung branchen-passend (Summe = 100)?
Nach Review: status: bestaetigt im Frontmatter setzen, dann läuft Phase B.

Sag mir, wenn du fertig bist mit dem Review.
```

Variante 2 — **eigenständiges Schema** (voller Review): zusätzlich Standorte, Suchradius und Local-Pack-Keywords als Prüfpunkte ausweisen (analog `03-16` Phase A).

`status.md` patchen (aus Drive lesen, ändern, via `drive.py upsert-text "$FOLDER_ID" "status.md"` zurück):

```yaml
blockiert:
  - skill: 03-20-local-gmb-wettbewerb (Phase B)
    wartet_auf: "Strategen-Review von audits/local-gmb-wettbewerb-schema.md (auf Drive)"
```

---

## Phase B — Eigentlicher Wettbewerbsvergleich

### Schritt B.1: Schema-Validierung

Lies `audits/local-gmb-wettbewerb-schema.md` aus Drive. Prüfe:

1. `status: bestaetigt`? Sonst Abbruch mit Hinweis auf Phase A.
2. Akteur-Set: mindestens der Kunde mit mindestens 1 Standort.
3. `lvs_gewichtung`: drei Blöcke vorhanden, **Summe exakt 100**. Sonst Abbruch mit konkretem Hinweis.
4. `local_pack_keywords`: mindestens 3 Basis-Keywords pro Standort.
5. Velocity-Buckets vorhanden (1/3/6/12).

### Schritt B.2: Apify-Health-Check

Nach `contracts.md` Abschnitt 11 — billiger Test-Call direkt vor dem ersten Scrape. Bei Fehler: Abbruch mit Reconnect-Hinweis.

### Schritt B.3: GMB-Profil- und Review-Scrape pro Akteur

Per Apify Google-Maps-Scraper plus Review-Scraper (Actor-Auswahl und datierte IDs siehe `reference/apify-actors.md`).

Pro Akteur und Standort extrahieren:

- **Profil-Reife-Felder**: Anzahl Kategorien (Haupt + Sub), Anzahl Attribute, Anzahl Fotos, Datum letztes Foto, Beschreibung (Länge), Öffnungszeiten vorhanden, Telefon/Website vorhanden, Service-Bereich definiert (falls Service-Area-Business).
- **Posts (Updates)**: Anzahl Posts in 12 Monaten, Datum letzter Post → Posting-Frequenz pro Monat.
- **Reviews**: Gesamt-Rating, Gesamt-Anzahl Reviews, Reviews-Sample mit **Datum** und **Antwort-Status** — entscheidend für Velocity und Antwort-Quote. Sample nach Datum absteigend, Hard-Cap **150 Reviews pro Akteur** (mehr als bei `03-16`, weil die Velocity-Buckets ausreichend zeitliche Tiefe brauchen; bei Akteuren mit sehr vielen Reviews deckt 150 die letzten 12 Monate i.d.R. ab).
- **Antwort-Quote**: Anteil Reviews im Sample mit Inhaber-Antwort.

Roh-JSONs lokal cachen in `~/.cache/reachx-mta/<slug>/`, am Ende nach Drive `assets/raw/gmb-wettbewerb-<slug>.json` hochladen (bei Filialen `-<standort>` suffigiert).

**Hinweis Aggregat-Disziplin** (`contracts.md` Abschnitt 13): Alle Review-Zahlen sind **GMB-only**, keine Multi-Plattform-Summe. Im Frontmatter und CSV `plattform: gmb` ausweisen.

### Schritt B.4: Review-Velocity berechnen

Pro Akteur und Standort aus dem Reviews-Sample (jedes Review hat ein Datum):

- Zähle neue Reviews je Bucket — **kumulativ** ab heute rückwärts: `velocity_1m`, `velocity_3m`, `velocity_6m`, `velocity_12m`.
- Leite daraus den **Velocity-Trend** ab (Beschleunigung / stabil / Verlangsamung) — Formel und Schwellen in `reference/lvs-methodik.md`.
- **Auffälligkeit `review_substanzverlust`**: ein Akteur mit ≥ 100 Gesamt-Reviews, aber `velocity_6m == 0` → die Gesamt-Zahl täuscht Stärke vor.
- **Auffälligkeit `wettbewerber_review_momentum`**: ein Wettbewerber mit `velocity_3m` ≥ 3× dem Kunden-Wert → er baut aktiv auf, latente Bedrohung.

Edge Case Reviews-Sample-Tiefe: deckt das Sample (150) nicht volle 12 Monate ab (sehr aktiver Akteur), wird `velocity_12m` als **untere Schranke** markiert (`velocity_12m_mind: true`) und im Output ausgewiesen — keine stille Unterschätzung.

### Schritt B.5: GMB-Profil-Reife-Score (Block C)

Pro Akteur ein 0–100-Reife-Score aus gewichteten Teil-Kriterien (Detail-Formel in `reference/lvs-methodik.md`):

- Kategorien-Anzahl (Haupt vorhanden + Sub-Kategorien)
- Attribute-Anzahl
- Foto-Anzahl (Schwellen-Buckets)
- Posts-Frequenz (Posts/Monat in 12 Monaten)
- Antwort-Quote auf Reviews
- Profil-Vollständigkeit (Telefon, Website, Öffnungszeiten, Beschreibung ≥ 100 Zeichen)

### Schritt B.6: Local-Pack-Rankings (Block A)

Pro Standort × Local-Pack-Keyword die Top-10-Maps-Ergebnisse ziehen (Tool-Optionen und Actor-IDs siehe `reference/apify-actors.md`). Pro Result-Zeile: `standort`, `keyword`, `position`, `akteur_slug`, `name`, `rating`, `rezensions_anzahl`.

Aggregation pro Akteur:

- **Top-3-Quote**: Anteil Local-Pack-Queries, in denen der Akteur in Position 1–3 ist.
- **Top-10-Quote**: Anteil in Position 1–10.
- **Auffälligkeit `wettbewerber_dominiert_local_pack`**: ein WB in ≥ 60 % der Queries in Top-3 und Kunde nicht.
- **Auffälligkeit `local_wb_nicht_in_liste`**: ein nicht in `liste.md` geführter Akteur taucht häufig in Top-10 auf → als `auto_ergaenzt` ins Akteur-Set, dann ebenfalls voll auditieren (falls Hard-Cap noch Platz lässt).

Schreibe die Roh-Rankings nach Drive `audits/local-gmb-wettbewerb-rankings.csv` und cache lokal.

### Schritt B.7: LVS berechnen

Pro Akteur den **Local-Visibility-Score (LVS)** 0–100 aus den drei Blöcken — Formel verbindlich aus `reference/lvs-methodik.md`:

```text
LVS = (Block_A_score × gA + Block_B_score × gB + Block_C_score × gC) / 100
```

mit `gA + gB + gC = 100` aus `lvs_gewichtung`, und jeder Block-Score selbst auf 0–100 normiert:

- **Block A — Local-Pack-Präsenz**: aus Top-3- und Top-10-Quote (Top-3 stärker gewichtet).
- **Block B — Review-Substanz**: aus Review-Volumen (log-skaliert gegen das Pool-Maximum, damit ein Akteur mit 2000 Reviews nicht alles erschlägt), Review-Velocity (Bucket-gewichtet, jüngere Buckets stärker) und Durchschnitts-Rating.
- **Block C — GMB-Profil-Reife**: der Reife-Score aus Schritt B.5.

Die genaue Normierung jedes Blocks, die Log-Skala für das Volumen und die Velocity-Bucket-Gewichte stehen **vollständig in `reference/lvs-methodik.md`** — dieser Skill rechnet sie nicht aus dem Gedächtnis nach.

Pro Akteur zusätzlich ausweisen: die drei Block-Scores einzeln (damit der Stratege sieht, *wo* ein Akteur stark/schwach ist) und das LVS-Ranking (Platz von N).

**Daten-Disziplin** (`contracts.md` Abschnitt 13): Der LVS ist eine **vom Skill abgeleitete Heuristik** — im Output als `schaetzung_skill` gekennzeichnet, nicht als erhobener Wert. Die Eingangsgrößen (Reviews, Rankings, Profil-Felder) sind `erhoben`. Da der LVS load-bearing für `04-02` ist, wird die Gewichtungs-Quelle (bestätigtes Schema) explizit im Frontmatter genannt.

### Schritt B.8: Auffälligkeiten konsolidieren

Mindestens diese Typen:

| Typ | Auslöser |
|---|---|
| `kunde_lvs_unter_median` | LVS des Kunden unter dem Pool-Median |
| `kunde_lvs_schlusslicht` | Kunde auf dem letzten LVS-Platz |
| `review_substanzverlust` | Akteur ≥ 100 Reviews, aber `velocity_6m == 0` |
| `wettbewerber_review_momentum` | WB-`velocity_3m` ≥ 3× Kunden-Wert |
| `wettbewerber_dominiert_local_pack` | WB in ≥ 60 % der Local-Pack-Queries in Top-3, Kunde nicht |
| `kunde_profil_reife_schwach` | Block-C-Score des Kunden < 50 |
| `kunde_antwort_quote_schwach` | Antwort-Quote des Kunden < 30 % |
| `local_wb_nicht_in_liste` | Akteur häufig im Local-Pack, fehlt in `wettbewerber/liste.md` |
| `latente_bedrohung_local` | WB mit schwachem LVS gesamt, aber stark steigender Velocity (würde stark, sobald er aufdreht) |

Die `latente_bedrohung_local`-Auffälligkeit setzt explizit die Latente-Bedrohung-Frage aus `contracts.md` Abschnitt 13 um.

### Schritt B.9: Aggregat-Markdown `audits/local-gmb-wettbewerb.md` schreiben

Lokal generieren, dann `drive.py upsert-text "$AUDITS_ID" "local-gmb-wettbewerb.md" /tmp/local-gmb-wettbewerb.md "text/markdown"`. Body-Struktur und Frontmatter siehe `reference/wettbewerb-output-schema.md`. Kern:

- **Übersicht**: Akteur-Anzahl, Standorte, Local-Pack-Queries, aktive Reduced-Modi.
- **LVS-Ranking**: Tabelle aller Akteure nach LVS absteigend, mit den drei Block-Scores einzeln und der Kunden-Position.
- **Review-Velocity-Tabelle**: pro Akteur die vier Bucket-Werte plus Velocity-Trend.
- **GMB-Profil-Reife-Tabelle**: pro Akteur die Reife-Teil-Kriterien.
- **Pro Akteur ein Detail-Block**: LVS-Aufschlüsselung, Velocity-Verlauf, Profil-Reife-Detail, Local-Pack-Quoten.
- **Pool-weite Auffälligkeiten**: nach Severity sortiert, mit Handlungs-Empfehlung.
- **Vorbereitung für `04-02-kanal-chancen-analyse`**: Local-SEO als Kanal [stark/mittel/schwach] mit Begründung aus dem LVS-Abstand Kunde-zu-Pool.

### Schritt B.10: CSV `audits/local-gmb-wettbewerb.csv` schreiben

Eine Zeile pro Akteur (bei Filialen eine Zeile pro Akteur × Standort plus eine Akteur-Aggregat-Zeile). Spalten-Definition vollständig in `reference/wettbewerb-output-schema.md`. Schreiben via `drive.py upsert-text "$AUDITS_ID" "local-gmb-wettbewerb.csv" ... "text/csv"`.

### Schritt B.11: HTML-Report `reports/14b-local-gmb-wettbewerb.html`

**Report-Slot bestimmen:** `14b` ist der Standardvorschlag — direkt hinter `14-gmb-local-seo.html` (dem `03-16`-Report). **Pflicht vor dem Render:** `reports/index.html` aus Drive lesen und prüfen, ob `14b` bereits belegt ist. Falls ja, nächste freie Nummer im 14er-Block wählen (`14c`, …). Den aufgelösten Slot in einer Shell-Variable festhalten:

```bash
REPORT_SLOT="14b"   # ggf. auf 14c o.ä. anpassen nach Kollisionsprüfung
```

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschließlich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- `_shell.html` aus Drive laden (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`), die acht Platzhalter füllen.
- Vor dem Drive-Upload validieren:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" \
    ~/.cache/reachx-mta/"$SLUG"/"$REPORT_SLOT"-local-gmb-wettbewerb.html --shell
  ```
  Exit-Code 0 → hochladen via `drive.py upsert-text "$REPORTS_ID" "$REPORT_SLOT-local-gmb-wettbewerb.html" ~/.cache/reachx-mta/"$SLUG"/"$REPORT_SLOT"-local-gmb-wettbewerb.html "text/html"`. Exit-Code 1 → nicht hochladen, Markup gegen `report-bausteine.md` korrigieren, erneut validieren.

Report-Aufbau (Baustein-Zuordnung siehe `reference/wettbewerb-output-schema.md`):

- **Stat-Strip**: Akteur-Anzahl, LVS Kunde, Kunden-Rang von N, Top-3-Quote Kunde, Anzahl Auffälligkeiten.
- **Summary-Card**: Kernbefund — LVS-Position des Kunden und der stärkste Wettbewerber.
- **Sticky-TOC**: LVS-Ranking · Review-Velocity · Profil-Reife · Pro Akteur · Auffälligkeiten.
- **LVS-Ranking** als `table.data` mit Summen-/Median-Zeile (`tr.total`).
- **Review-Velocity** als `table.data`, der Velocity-Verlauf je Akteur als Inline-SVG-Sparkline (gleicher min/max über alle Sparklines).
- **Pro Akteur ein `details.dim`-Block** mit `data-rating` aus dem LVS (stark ≥ 66, mittel 33–65, schwach < 33) — **expandierbare Akteur-Zeilen** mit LVS-Aufschlüsselung, Velocity-Buckets, Profil-Reife-Detail, Local-Pack-Quoten. Kunde und Top-2-Wettbewerber `open`, Rest zugeklappt.
- **Auffälligkeiten** als `.suggestion`-Blöcke mit Handlungs-Empfehlung.
- `{{TOKEN_FOOTER}}` mit dem Skill-Counter befüllen.

### Schritt B.12: Dashboard und status.md

Nach `contracts.md` Abschnitte 3 und 7 — zuerst alle inhaltlichen Outputs nach Drive, **dann** `status.md`, **dann** Dashboard:

- `03-20-local-gmb-wettbewerb` in `schritte_done`, aus `schritte_offen` und `blockiert` entfernen.
- Eigene Sektion unter "✓ Erledigt" mit Datum, Outputs, Top-Auffälligkeit.
- `naechster_empfohlen`: bei genug abgeschlossenen Audits `04-02-kanal-chancen-analyse`, sonst nächster offener Audit-Skill.
- Dashboard (`reports/index.html`): Reports-Eintrag mit Link auf den neuen Report (tatsächliche Nummer), Stat-Strip um LVS Kunde ergänzen, `<body class="is-dashboard">` sicherstellen.

### Schritt B.13: Standard-Schlussformat im Chat

```text
✓ 03-20-local-gmb-wettbewerb Phase B abgeschlossen.

Outputs (auf Drive):
- audits/local-gmb-wettbewerb.md — Aggregat mit LVS-Ranking, Velocity, Profil-Reife, Auffälligkeiten
- audits/local-gmb-wettbewerb.csv — eine Zeile pro Akteur mit allen Metriken
- audits/local-gmb-wettbewerb-rankings.csv — Roh-Rankings pro Standort × Keyword × Akteur
- assets/raw/gmb-wettbewerb-*.json — Roh-Caches
- reports/14b-local-gmb-wettbewerb.html — visueller Report mit LVS-Ranking und expandierbaren Akteur-Zeilen
Status aktualisiert in: status.md

Local-Wettbewerbs-Statistik:
- Akteure auditiert:       N (1 Kunde, M Wettbewerber)
- LVS Kunde:               X / 100 — Rang R von N
- Stärkster Akteur:        <name> (LVS Y)
- Review-Velocity Kunde:   V neue Reviews letzte 3 Monate
- Top-3-Quote Kunde:       Z % der Local-Pack-Queries
- Auffälligkeiten:         A

⚠ Local-Wettbewerbs-Insights:
1. <Auffälligkeit 1>
2. <Auffälligkeit 2>
3. <Auffälligkeit 3>

Nächste Schritte:
1. 04-02-kanal-chancen-analyse — nimmt den LVS als Local-SEO-Datenpunkt auf (sobald genug Audits da sind)
2. (parallel möglich, falls noch nicht durch) weitere Audit-Skills

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/wettbewerb-schema-template.md` — Phase-A-Schema-Format inklusive Basis-Wahl-Logik und LVS-Gewichtungs-Defaults
- `reference/lvs-methodik.md` — verbindliche LVS-Formel: Block-Normierung, Review-Velocity-Berechnung, Profil-Reife-Score, Branchen-Gewichtungen
- `reference/apify-actors.md` — datierte Actor-IDs für Google-Maps- und Review-Scrape, Tool-Kaskade, Reduced-Modi
- `reference/wettbewerb-output-schema.md` — Phase-B-Markdown-, CSV- und HTML-Report-Schema mit Baustein-Zuordnung

## Edge Cases

- **`03-16` lief noch nicht** → eigenständiges, vollständiges Schema, voller Strategen-Review. Empfehlung im Body: `03-16` zuerst spart die Doppel-Bestätigung. Kein Hard-Abbruch — `03-20` ist auch standalone lauffähig.
- **`03-16`-Schema ist `skip_national_online`** → dieser Skill ist ebenfalls Skip-Kandidat. Override `trotzdem laufen` möglich.
- **Kunde hat kein GMB-Profil** → harter Befund: LVS Kunde ≈ 0, Auffälligkeit `kunde_lvs_schlusslicht` mit maximaler Severity. Phase B läuft trotzdem für die Wettbewerber, damit der Stratege den Markt-Benchmark sieht.
- **Apify-Maps-Scraper liefert keine Reviews** (Rate-Limit, Bot-Erkennung) → Reduced-Modus: nur Profil-Reife (Block C) und Local-Pack (Block A), Block B aus dem aggregierten Gesamt-Rating allein (ohne Velocity, ohne Volumen-Substanz). Auffälligkeit `velocity_nicht_erhebbar`, Hinweis im Body, LVS-Konfidenz `niedrig`.
- **Reviews-Sample deckt keine 12 Monate ab** (sehr aktiver Akteur, 150-Cap erschöpft vor 12 Monaten) → `velocity_12m` als untere Schranke markieren (`velocity_12m_mind: true`), im Output ausweisen.
- **Akteur ist Service-Area-Business** (Handwerker ohne Ladengeschäft) → Adresse versteckt; Block A nutzt Service-Area-Polygone soweit der Scraper sie liefert, sonst Standort-Mittelpunkt. Im Output `service_area: true` markieren.
- **Local-Pack zeigt für ein Keyword keinen Local Pack** → Result-Zeile mit `position: null`, `pack_eingeblendet: false`; im Block-A-Aggregat als eigener Bucket "ohne Local Pack" ausgewiesen, nicht als Position 11+ gewertet.
- **Nur Kunde, keine bestätigten Wettbewerber** → Skill läuft als Kunden-only-Lauf: LVS des Kunden wird berechnet, aber ohne Pool-Vergleich. Im Body und Schluss-Format klar markiert ("LVS ohne Wettbewerbs-Benchmark — `02-02-wettbewerber-identifikation` bestätigen für Ranking"). Auffälligkeiten mit Pool-Bezug entfallen.
- **Mehr als 10 Wettbewerber im Local-Pack auto-erkannt** → Hard-Cap greift; die nicht auditierten Akteure werden namentlich im Body gelistet ("weitere lokale Akteure erkannt, nicht im Detail erhoben").
- **Re-Run nach Schema-Änderung** → Stratege ändert Schema, setzt `status: bestaetigt` erneut. Skill erkennt bestehende `local-gmb-wettbewerb.md`, fragt überschreiben/Backup/abbrechen. Bei Backup → bestehende Outputs nach `assets/_archive/<datum>/` kopieren.
- **`03-16` wurde nach diesem Skill re-gerunnt** → wenn das geerbte `03-16`-Schema neuer ist als dieser Output, Staleness-Hinweis im Schluss-Format (sinngemäß `contracts.md` Abschnitt 12): "03-16-Schema wurde aktualisiert — `03-20` Re-Run prüfen."

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Schema-vor-Lauf-Pattern strikt — Phase B läuft niemals ohne `status: bestaetigt`.
- Wenn ein bestätigtes `03-16`-Schema existiert, wird es als Basis übernommen — niemals zwei konkurrierende Local-Schemata.
- Skip-Logik in Phase A ist ein eigener Pfad (`status: skip_national_online`), kein Fehler.
- Apify-Disziplin: Pflicht-MCP-Health-Check vor dem ersten echten Scrape, Credential nur über `APIFY_TOKEN`, datierte Actor-IDs in `reference/apify-actors.md`, bei Session-Bruch Abbruch mit Reconnect-Hinweis.
- Der LVS ist `schaetzung_skill`, die Eingangsgrößen sind `erhoben` — Quellen-Kennzeichnung pro Zahl (`contracts.md` Abschnitt 13).
- Review-Zahlen sind GMB-only, keine Multi-Plattform-Summe — `plattform: gmb` im Output.
- Outputs leben auf Google Drive in `audits/`, `reports/`, `assets/raw/` (über `drive.py upsert-text`).
- HTML-Report aus `reports/_shell.html`, Bausteine 1:1 aus `report-bausteine.md`, vor Upload mit `validate-report.py` prüfen.
- Report-Nummer `14b` vor dem Render gegen `reports/index.html` auf Kollision prüfen.
- `status.md` und Dashboard werden in jedem Lauf aktualisiert (auch beim Skip).
- Standard-Schlussformat im Chat.
