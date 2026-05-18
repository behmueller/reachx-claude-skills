---
name: 03-19-geo-ki-sichtbarkeit
description: GEO-Audit (Generative Engine Optimization) - erhebt für Kunde und Wettbewerber die Marken-Sichtbarkeit in KI-Suchsystemen (ChatGPT, Google Gemini / AI Overviews, Perplexity; Claude analog Perplexity behandelbar). Misst über ein bestätigtes Prompt-Inventar pro Engine × Prompt × Akteur, ob und wie oft ein Akteur in der KI-Antwort genannt oder als Quelle zitiert wird, und dokumentiert das Quellen-Ökosystem - welche Domains (Branchenportale, Reddit, Fachmedien, eigene Site) die Engines zitieren. Schema-vor-Lauf - Phase A schlägt ein Prompt-Inventar (~10 Prompts, gemischt informational/kommerziell, national plus lokale Ort-Varianten) und ein Akteur-Set vor, Stratege bestätigt, Phase B führt die Prompt-Probes durch. Primär qualitative Prompt-Probes via WebSearch/WebFetch; optional - falls Ahrefs ein Brand-Radar-Abo hat - die brand-radar-Tools für ein quantitatives Share-of-Voice-Maß, sonst sauberer Fallback mit konfidenz niedrig. Output ist audits/geo-sichtbarkeit.md mit Aggregat, audits/geo-sichtbarkeit-prompts.csv (Prompt × Engine × Akteur × sichtbar), audits/geo-sichtbarkeit-quellen.csv (zitierte Domains), plus HTML-Report. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext die Sichtbarkeit in KI-Suche, generative Engines oder LLM-Antworten prüfen will - auch bei Phrasen wie "GEO-Audit", "Generative Engine Optimization", "KI-Sichtbarkeit", "taucht der Kunde in ChatGPT auf", "AI-Overviews-Check", "Perplexity-Sichtbarkeit", "wird die Marke von KI zitiert", "Brand Radar", "Share of Voice in KI-Suche", "GEO-Check", "LLM-Sichtbarkeit", "AI-Search-Audit", "Quellen-Ökosystem KI". Setzt 01-01-mta-projekt-init voraus; ohne wettbewerber/liste.md läuft der Skill im Kunden-only-Modus.
---

# GEO-KI-Sichtbarkeit (Generative Engine Optimization)

Stufe-3-Kanal-Audit. **GEO = Generative Engine Optimization** — die Sichtbarkeit einer Marke in KI-Suchsystemen statt in der klassischen blauen-Links-Suche. Dieser Skill misst, **ob und wie oft Kunde und Wettbewerber in den Antworten generativer Such-Engines auftauchen** — genannt im Antwort-Text oder zitiert als Quelle — und welches **Quellen-Ökosystem** die Engines heranziehen, wenn sie zur Branche des Kunden antworten.

Geprüfte Engines (Default-Set):

- **ChatGPT** (OpenAI, mit Web-Suche / Search-Modus)
- **Google Gemini / AI Overviews** (Googles generative Antworten oberhalb der klassischen SERP)
- **Perplexity** (Answer-Engine mit expliziter Quellen-Zitation)
- **Claude** wird, wenn der Stratege es im Schema aktiviert, **analog Perplexity** behandelt (Answer-Engine mit Quellen) — kein Pflicht-Bestandteil des Default-Sets.

**Wichtige Einordnung — GEO ist ein Cross-Channel-Multiplikator, kein eigener Budgetposten.** KI-Sichtbarkeit entsteht nicht durch ein eigenes "GEO-Budget", sondern als Folge starker SEO-/Content-Arbeit und Quell-Präsenz auf den Plattformen, die die Engines zitieren. Der Skill framt das im Output durchgängig so: die Befunde wirken auf SEO, Content und Branchenportal-Präsenz ein — sie begründen **keine** eigene Kanal-Investitionszeile. Die typischen Hebel sind FAQ-/Entity-Schema, Long-Form-Content mit Preistransparenz und Quell-Präsenz auf zitierten Plattformen (siehe `reference/geo-analyse-methodik.md`).

Vier Output-Ebenen:

1. **Aggregat-Markdown** `audits/geo-sichtbarkeit.md` — Sichtbarkeits-Befund pro Akteur, Engine-Vergleich, Quellen-Ökosystem, Auffälligkeiten, Hebel-Empfehlung
2. **Prompt-CSV** `audits/geo-sichtbarkeit-prompts.csv` — eine Zeile pro Prompt × Engine × Akteur mit `sichtbar`-Flag und Nennungs-Art
3. **Quellen-CSV** `audits/geo-sichtbarkeit-quellen.csv` — eine Zeile pro zitierter Domain × Engine, mit Häufigkeit und Quellen-Typ
4. **HTML-Report** `reports/<nummer>-geo-sichtbarkeit.html` — Sichtbarkeits-Heatmap, Engine-Vergleich, Quellen-Ökosystem, Hebel

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-rechercheur`**-Subagent (Sonnet 4.6). Der Hauptthread orchestriert (User-Interaktion, Stammdaten-Erfassung, Schema-Bestätigungs-Stopps), der Subagent führt die eigentliche Skill-Logik aus (Tool-Calls auf WebSearch/WebFetch und ggf. Ahrefs-MCP, Drive-Operationen via `drive.py`, Output-Generierung) und gibt am Ende einen kompakten Status zurück. Das hält den Hauptthread-Kontext und das Token-Budget schlank.

Der **Schema-Phase-A-Vorschlag darf vom Rechercheur erstellt werden** — der Hauptthread reicht den Schema-Vorschlag nur an den Strategen zur Bestätigung durch.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-rechercheur"`
- Übergabe: MTA-Slug + aktuell relevante Eingaben (z. B. Wettbewerber-Liste, Phase-Hinweis)
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="03-19-geo-ki-sichtbarkeit"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Die Marker werden in **beiden Phasen** gesetzt — Phase A (Schema-Vorschlag) zählt genauso wie Phase B (Vollauf). Beim HTML-Report-Render (nur Phase B) zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Wann triggern

- "GEO-Audit"
- "Generative Engine Optimization"
- "KI-Sichtbarkeit"
- "Taucht der Kunde in ChatGPT auf"
- "AI-Overviews-Check"
- "Perplexity-Sichtbarkeit"
- "Wird die Marke von KI zitiert"
- "Brand Radar"
- "Share of Voice in KI-Suche"
- "GEO-Check"
- "LLM-Sichtbarkeit"
- "AI-Search-Audit"
- "Quellen-Ökosystem KI"
- "Sichtbarkeit in generativer Suche"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → MTA registriert, `meta.json` im Drive-MTA-Root
- **`WebSearch` / `WebFetch` verfügbar (Pflicht)** — die Prompt-Probes gegen die KI-Systeme bzw. deren öffentliche Antworten laufen darüber. Ohne diese Tools ist der Skill nicht sinnvoll lauffähig → sauberer Abbruch.
- **Ahrefs-MCP mit Brand-Radar-Abo (optional)** — wenn die `brand-radar-*`-Tools verfügbar UND im Abo freigeschaltet sind, liefern sie ein **quantitatives** Share-of-Voice-/Mentions-Maß. Brand Radar ist häufig **nicht** im Abo → dann sauberer Fallback auf rein qualitative Prompt-Probes, klar mit `konfidenz: niedrig` und `methode: qualitative_probe` gekennzeichnet. Brand Radar ist **OPTIONAL, kein Pflicht-MCP** (Pflicht-MCP-Logik aus `contracts.md` Abschnitt 11 anwenden).
- Empfohlen: `wettbewerber/liste.md` (Drive) mit `status: bestaetigt` — sonst Kunden-only-Modus
- Empfohlen: `data/kunde.md` und `data/briefing.md` (Drive) — daraus zieht der Skill die branchenrelevanten Prompts für das Inventar
- Empfohlen vorher gelaufen: `03-01-seo-sichtbarkeit-und-rankings` (Keyword-Basis liefert gute Prompt-Kandidaten) und `02-04-branchenportal-recherche` (Portal-Liste hilft beim Quellen-Ökosystem-Abgleich) — keine harte Abhängigkeit.

### Modi-Übersicht

| WebSearch/WebFetch | Brand-Radar-Abo | Wettbewerber-Liste | Skill-Modus |
|---|---|---|---|
| ✓ | ✓ | bestätigt | **Voll-Quantitativ** (Probes + Brand-Radar, Kunde + WBs) |
| ✓ | ✗ | bestätigt | **Voll-Qualitativ** (nur Probes, Kunde + WBs, `konfidenz: niedrig`) |
| ✓ | ✓ / ✗ | fehlt / nicht bestätigt | **Kunden-only** (nur Kunden-Sichtbarkeit) |
| ✗ | — | — | **Abbruch** |

### MCP-/Tool-Health-Check (Pflicht, vor Schritt 3 / Phase B)

Vor dem ersten echten Datenabruf prüfen (siehe `contracts.md` Abschnitt 11):

- **WebSearch / WebFetch (Pflicht):** sind die Tools verfügbar? Wenn nein → Abbruch mit Hinweis "WebSearch/WebFetch nicht verfügbar — GEO-Probes nicht durchführbar."
- **Ahrefs Brand Radar (optional):** ein billiger Test-Call `mcp__claude_ai_Ahrefs__subscription-info-limits-and-usage` zeigt, ob die Ahrefs-MCP erreichbar ist. Zusätzlich prüfen, ob mindestens ein `brand-radar-*`-Tool aufgelistet ist UND ein erster Test-Call (z. B. `brand-radar-mentions-overview-entities` mit Minimal-Parametern) **nicht** mit "not in subscription / plan" o. ä. abbricht. Schlägt das fehl → **Brand Radar gilt als nicht verfügbar**, Skill läuft im Qualitativ-Modus weiter, kein Abbruch.

Brand-Radar-Tool-Details siehe `reference/brand-radar-nutzung.md`.

## Ablauf

Dieser Skill nutzt das **Schema-vor-Lauf-Pattern** (`contracts.md` Abschnitt 8): Phase A schlägt das Prompt-Inventar und das Akteur-Set vor, Phase B führt nach Bestätigung die Probes durch.

### Schritt 0: MTA-Kontext und Drive-Helper ermitteln

Alle Inputs werden aus Google Drive gelesen, alle Outputs nach Drive geschrieben — siehe `contracts.md` Abschnitt 4. Helper-Modul: `01-01-mta-projekt-init/scripts/drive.py`.

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
if [ -z "$MTA_JSON" ] || [ "$MTA_JSON" = "null" ]; then
  echo "✗ Kein MTA-Projekt gefunden. Bitte zuerst 01-01-mta-projekt-init aufrufen."
  exit 1
fi
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')

META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json

AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
ASSETS_ID=$(jq -r '.drive.subfolders.assets' /tmp/meta.json)
```

Lokaler Arbeits-Cache für Zwischenergebnisse (Probe-Roh-JSONs, CSV-Generierung, HTML-Templating): `~/.cache/reachx-mta/<slug>/`. Wird **nicht** mit Drive synchronisiert — am Ende des Laufs werden nur die finalen Outputs hochgeladen.

### Schritt 1: Voraussetzungs-Check und Modus-Bestimmung

Lies `wettbewerber/liste.md` aus Drive:

```bash
LISTE_ID=$(python3 "$DRIVE_PY" list-children "$WB_ID" | jq -r '.[] | select(.name == "liste.md") | .id')
if [ -n "$LISTE_ID" ] && [ "$LISTE_ID" != "null" ]; then
  python3 "$DRIVE_PY" read "$LISTE_ID" > /tmp/wb-liste.md
fi
```

- `liste.md` vorhanden mit `status: bestaetigt` → Modus **Voll** (Kunde + WBs)
- `liste.md` vorhanden mit `status: vorgeschlagen` → Warnung, fragen ob trotzdem im Kunden-only-Modus laufen
- `liste.md` fehlt → Modus **Kunden-only**, Hinweis im Schluss-Format

Tool-Health-Check wie oben beschrieben durchführen. Brand-Radar-Verfügbarkeit als `brand_radar: verfuegbar | nicht_verfuegbar` festhalten.

### Schritt 2 (Phase A): Schema-Vorschlag generieren

Prüfe, ob `audits/geo-sichtbarkeit-schema.md` bereits auf Drive existiert:

- **Existiert nicht** → Phase A: Schema generieren (dieser Schritt), danach Abbruch mit Review-Hinweis.
- **Existiert mit `status: vorgeschlagen`** → Hinweis, dass der Stratege das Schema noch bestätigen muss. Kein Lauf.
- **Existiert mit `status: bestaetigt`** → weiter zu Phase B (Schritt 3).

**Phase-A-Logik** — Schema-Datei `audits/geo-sichtbarkeit-schema.md` zusammenstellen (Format siehe `reference/geo-output-schema.md` Abschnitt "Schema-Datei"):

1. **Engine-Set** vorschlagen — Default: `chatgpt`, `gemini`, `perplexity`. `claude` optional, nur wenn der Stratege Claude-as-Perplexity wünscht.
2. **Prompt-Inventar** vorschlagen — **~10 Prompts**, gemischt:
   - **Informationale Branchen-Prompts** (TOFU/MOFU) — typische Fragen, die ein Interessent stellt, z. B. "Wie funktioniert X?", "Was kostet eine Y?"
   - **Kommerzielle Branchen-Prompts** (BOFU) — Anbieter-Vergleichs- und Auswahl-Fragen, z. B. "Bester Anbieter für Z", "Empfehlung für A in [Branche]"
   - **Lokale Varianten mit Ort** — dieselbe Frage mit Ortsbezug, z. B. "Bester Z-Anbieter in [Stadt]" — nur wenn der Kunde lokalen Bezug hat (`region` aus `meta.json` / `briefing.md`). Bei rein nationalen/Online-Kunden lokale Varianten weglassen.
   - Prompt-Quellen: Portfolio-Begriffe aus `data/kunde.md`, Branche aus `meta.json`, echte Keywords aus `audits/seo-keywords.csv` (falls `03-01` gelaufen), Briefing-Pain-Points.
   - Pro Prompt: `prompt_id`, Text, `typ` (`informational | kommerziell | lokal`), `funnel_stufe` (`TOFU | MOFU | BOFU`), Begründung.
3. **Akteur-Set** vorschlagen — Kunde plus relevante Wettbewerber/Best-Practice aus `wettbewerber/liste.md`. Nicht zwingend alle WBs — der Skill schlägt die strategisch relevanten vor (Top-WBs nach Bedrohungsgrad / Best-Practice), der Stratege ergänzt/streicht. Pro Akteur: `akteurs_slug`, `akteurs_name`, `akteurs_typ`, Marken-Synonyme/Schreibvarianten (wichtig für die Treffer-Erkennung) und Domain (für die Quellen-Zitations-Erkennung).
4. **Methodik-Hinweise** ins Schema schreiben: `brand_radar: verfuegbar | nicht_verfuegbar` (aus Schritt 1), und bei `nicht_verfuegbar` den Vermerk, dass der Lauf rein qualitativ wird (`konfidenz: niedrig`).

Schema-Datei nach Drive `audits/` schreiben (`upsert-text`), dann **abbrechen** mit:

```
Schema für 03-19-geo-ki-sichtbarkeit vorgeschlagen.
Datei: audits/geo-sichtbarkeit-schema.md (auf Drive)
Bitte Prompt-Inventar und Akteur-Set reviewen, anpassen, dann status auf `bestaetigt` setzen und Skill erneut aufrufen.
```

Auch bei Phase-A-Abbruch: `status.md` und Dashboard aktualisieren (Skill als "blockiert — Schema-Review offen" eintragen).

### Schritt 3 (Phase B): Schema lesen und validieren

Beim zweiten Aufruf — Schema aus Drive lesen, `status: bestaetigt` im Frontmatter prüfen. Wenn nicht bestätigt → Hinweis auf Phase A, kein Lauf.

Validieren (siehe `reference/geo-output-schema.md` Abschnitt "Schema-Validierung"):

- `engines` enthält mindestens 1 Engine
- `prompt_inventar` enthält mindestens 5 Prompts (Default-Vorschlag ~10)
- `akteur_set` enthält den Kunden plus mindestens 0 WBs (Kunden-only erlaubt)
- jeder Akteur hat mindestens den Marken-Namen als Synonym

Bei Validierungsfehler **konkret benennen, welches Feld** fehlt.

### Schritt 4: Existenz-Check Output

Via `list-children` auf `AUDITS_ID` prüfen, ob `geo-sichtbarkeit.md`, `geo-sichtbarkeit-prompts.csv` oder `geo-sichtbarkeit-quellen.csv` bereits im Drive `audits/`-Folder existieren — bei Re-Run fragen (überschreiben / Backup-und-neu / abbrechen).

### Schritt 5: Prompt-Probes durchführen (qualitativ — immer)

Für **jede Engine × jeden Prompt** eine Probe durchführen. Methodik im Detail in `reference/geo-analyse-methodik.md` Abschnitt "Prompt-Probe-Durchführung".

Vorgehen pro Probe:

1. Den Prompt-Text gegen die Engine bzw. ihre öffentlich erreichbare Antwort stellen — via `WebSearch` (liefert KI-Overview-/Answer-Snippets, die viele Engines öffentlich ausgeben) und `WebFetch` (für Answer-Engine-Ergebnisseiten mit Quellen-Liste). Engine-spezifische Aufruf-Hinweise in `reference/geo-analyse-methodik.md`.
2. Aus der Antwort extrahieren:
   - **Antwort-Text** (gekürzt auf max. 1.000 Zeichen Auszug für den Cache)
   - **Zitierte Quellen** — Liste der Domains/URLs, die die Engine als Beleg nennt (Answer-Engines wie Perplexity geben das explizit aus; bei ChatGPT/Gemini aus den verlinkten Quellen)
3. **Pro Akteur** prüfen, ob er in dieser Antwort sichtbar ist:
   - `genannt` — Marken-Name (oder ein Synonym) erscheint im Antwort-Text
   - `zitiert` — die Domain des Akteurs erscheint in der Quellen-Liste
   - `genannt_und_zitiert` — beides
   - `nicht_sichtbar` — weder noch
   - Treffer-Erkennung: Wort-Grenzen-Match auf Marken-Name + Synonyme (case-insensitive), Domain-Match auf normalisierte Host-Namen. Defensiv gegen Marken-Namen, die Common-Words sind (siehe Edge Cases).
4. **Roh-Antwort** pro Probe lokal cachen unter `~/.cache/reachx-mta/<slug>/raw/geo-probe-<engine>-<prompt_id>.json` — Upload nach Drive `assets/raw/` am Skill-Ende.

Pro Probe entsteht so ein Set von Befunden (ein `sichtbar`-Wert pro Akteur) plus die Quellen-Liste der Engine.

**Konfidenz:** Qualitative Probes sind eine **Stichprobe** — KI-Antworten sind nicht-deterministisch und personalisiert. Jede Zeile trägt `methode: qualitative_probe` und `konfidenz: niedrig`. Das ist im gesamten Output (Frontmatter, CSV-Spalte, Report-Hinweis) sichtbar zu machen. Quellen-Kennzeichnung nach `contracts.md` Abschnitt 13: die Sichtbarkeits-Werte sind `erhoben`, aber explizit als Stichprobe mit niedriger Konfidenz markiert — niemals als belastbare Quote dargestellt.

### Schritt 6: Brand-Radar-Abruf (nur Voll-Quantitativ-Modus)

**Nur ausführen, wenn Brand Radar in Schritt 1 als `verfuegbar` erkannt wurde.** Im Qualitativ-Modus überspringen.

Über die Ahrefs-`brand-radar-*`-Tools ein quantitatives Maß ziehen (Tool-Mapping und Parameter siehe `reference/brand-radar-nutzung.md`):

- **Mentions-Overview** pro Akteur — wie oft die Marke in KI-Antworten erwähnt wird
- **Share-of-Voice-Overview** — Anteil des Kunden gegenüber den Wettbewerbern
- **Cited-Domains** — welche Domains die Engines zur Branche zitieren (ergänzt die qualitativ erhobene Quellen-Liste)

Brand-Radar-Werte sind `erhoben` mit `konfidenz: mittel` bis `hoch` (echte Mess-Datenbasis statt Stichprobe) — sie werden im Output **getrennt** von den qualitativen Probe-Werten ausgewiesen, nicht mit ihnen verrechnet. Sie sind die belastbarere Lesart, ersetzen die Probes aber nicht (Probes zeigen konkrete Prompt-Antworten, Brand Radar zeigt Aggregat-Volumen).

Bei Brand-Radar-Fehler mitten im Lauf (Abo abgelaufen, Rate-Limit) → Brand-Radar-Teil sauber abbrechen, mit Qualitativ-Modus weiterlaufen, Hinweis im Schluss-Format.

### Schritt 7: Quellen-Ökosystem aggregieren

Aus den über alle Probes (und ggf. Brand-Radar-Cited-Domains) gesammelten zitierten Domains das **Quellen-Ökosystem** der Branche bilden:

1. Domains deduplizieren und über alle Engines/Prompts zählen (`zitations_anzahl`, `engines_die_zitieren`)
2. Pro Domain einen **Quellen-Typ** klassifizieren (Heuristik in `reference/geo-analyse-methodik.md` Abschnitt "Quellen-Typ-Klassifikation"):
   - `branchenportal` — Bewertungs-/Verzeichnis-Plattform (Abgleich mit `wettbewerber/portale.md`, falls `02-04` gelaufen)
   - `community` — Reddit, Foren, Q&A-Plattformen
   - `fachmedium` — Branchen-Magazine, Redaktions-Medien
   - `eigene_site` — Domain des Kunden oder eines WBs (Akteurs-Domain-Abgleich)
   - `wissensplattform` — Wikipedia, Wikis, Hersteller-Doku
   - `sonstige`
3. Markieren, ob die Domain einem Akteur gehört (`gehoert_akteur: <slug> | null`)

Das Quellen-Ökosystem zeigt dem Strategen, **wo** der Kunde präsent sein muss, damit die Engines ihn zitieren — der zentrale GEO-Hebel.

### Schritt 8: Sichtbarkeits-Befund pro Akteur ableiten

Pro Akteur aus den Probe-Befunden aggregieren:

- `prompts_sichtbar` / `prompts_gesamt` — in wie vielen Prompts überhaupt sichtbar (über alle Engines aggregiert)
- `engine_abdeckung` — in wie vielen der geprüften Engines mindestens einmal sichtbar
- Verteilung `genannt` / `zitiert` / `genannt_und_zitiert` / `nicht_sichtbar`
- `sichtbarkeits_quote` — `prompts_sichtbar / prompts_gesamt`, als Stichproben-Indikator (mit `konfidenz: niedrig` gekennzeichnet, **keine** belastbare Quote)
- Bei Voll-Quantitativ-Modus zusätzlich die Brand-Radar-Mentions und der Share-of-Voice-Wert

Akteure nach Sichtbarkeit sortieren — der Kunde wird gegen die WBs eingeordnet (Position X von N).

### Schritt 9: Auffälligkeiten

Mindestens diese Typen prüfen, nur zutreffende in den Output:

| Typ | Auslöser | Beispiel |
|---|---|---|
| `kunde_unsichtbar` | Kunde in 0 von N Prompts sichtbar | "Kunde taucht in keiner der 30 Probe-Antworten auf — in KI-Suche derzeit nicht präsent" |
| `wettbewerber_dominant_geo` | Ein WB ist in >60% der Prompts sichtbar, Kunde unter 20% | "Wettbewerber X ist KI-Sichtbarkeits-Leader, der Kunde praktisch unsichtbar" |
| `kunde_geo_stark` | Kunde in >50% der Prompts sichtbar | "Kunde wird in der Mehrheit der KI-Antworten genannt — solide GEO-Basis" |
| `engine_divergenz` | Akteur ist in einer Engine stark, in einer anderen unsichtbar | "Kunde wird in Perplexity zitiert, in Google AI Overviews nicht — Quellen-Mix passt nicht zu Googles Auswahl" |
| `quellen_oekosystem_portallastig` | >50% der zitierten Domains sind Branchenportale/Communities | "Engines zitieren überwiegend Portale und Reddit — Portal-Präsenz ist der wirksamste GEO-Hebel" |
| `eigene_site_nie_zitiert` | Kunden-Domain in 0 Quellen-Listen | "Die Kunden-Website wird von keiner Engine als Quelle herangezogen — Entity-/FAQ-Schema und Long-Form-Content fehlen" |
| `community_quelle_stark` | Reddit/Foren machen einen großen Anteil der zitierten Quellen aus | "KI-Antworten stützen sich stark auf Community-Quellen — Reddit-Präsenz wirkt indirekt auf KI-Sichtbarkeit" |
| `brand_radar_probe_divergenz` | Brand-Radar-Befund weicht stark vom Probe-Befund ab (nur Voll-Quantitativ) | "Brand Radar zeigt nennenswerte Mentions, die Stichproben-Probes nicht — Probe-Set vergrößern" |
| `lokale_unsichtbarkeit` | Kunde in lokalen Prompt-Varianten unsichtbar, obwohl lokal tätig | "Bei ortsbezogenen Prompts wird der Kunde nicht genannt — lokale GEO-Lücke" |

Pro Auffälligkeit: Typ, Titel, Beschreibung, Relevanz (`hoch`/`mittel`/`niedrig`), Handlungs-Empfehlung, betroffene Akteure/Engines.

### Schritt 10: CSVs schreiben

**`audits/geo-sichtbarkeit-prompts.csv`** — eine Zeile pro Prompt × Engine × Akteur.

Spalten (Details in `reference/geo-output-schema.md`):

```
prompt_id, prompt_text, prompt_typ, funnel_stufe, engine,
akteurs_slug, akteurs_typ, akteurs_name,
sichtbar, nennungs_art, position_in_antwort, antwort_auszug,
methode, konfidenz, datenstand_iso
```

`nennungs_art`: `genannt | zitiert | genannt_und_zitiert | nicht_sichtbar`. `antwort_auszug`: max. 200 Zeichen. `methode`: immer `qualitative_probe`.

**`audits/geo-sichtbarkeit-quellen.csv`** — eine Zeile pro zitierter Domain × Engine.

Spalten:

```
domain, quellen_typ, engine, zitations_anzahl,
prompts_die_zitieren, gehoert_akteur, datenstand_iso
```

Detaillierte Spalten-Definition in `reference/geo-output-schema.md`.

### Schritt 11: Aggregat-Markdown `audits/geo-sichtbarkeit.md`

Markdown mit YAML-Frontmatter. Vollständiges Format in `reference/geo-output-schema.md`.

Frontmatter enthält:

- Skill-Metadaten, Recherche-Provenienz, Basis-Inputs
- `modus: voll_quantitativ | voll_qualitativ | kunden_only`
- `brand_radar: verfuegbar | nicht_verfuegbar`
- `methode: qualitative_probe` (plus `brand_radar` als zweite Methode bei Voll-Quantitativ)
- `konfidenz: niedrig` für die Probe-Werte (Pflicht-Kennzeichnung)
- geprüfte Engines, Prompt-Inventar-Snapshot, Akteurs-Sichtbarkeits-Aggregate
- Quellen-Ökosystem-Snapshot (Top-Domains nach Zitations-Anzahl mit Typ)
- Auffälligkeiten

Body-Struktur:

1. **Übersicht & Kernbefund** — Kunden-Sichtbarkeit, Position gegen WBs, in 3-4 Sätzen
2. **Einordnungs-Block** — prominent: "GEO ist ein Cross-Channel-Multiplikator auf SEO/Content, kein eigener Budgetposten." Der Block erklärt, dass die folgenden Befunde in SEO-/Content-/Portal-Maßnahmen einfließen, nicht in eine eigene Investitionszeile.
3. **Sichtbarkeit pro Akteur** — pro Akteur: Prompts-sichtbar-Quote, Engine-Abdeckung, Nennungs-Art-Verteilung; bei Voll-Quantitativ zusätzlich Brand-Radar-Mentions und Share of Voice
4. **Engine-Vergleich** — welche Engine zeigt welchen Akteur wie oft; Divergenzen
5. **Quellen-Ökosystem** — Top-zitierte Domains mit Typ, was das für die Quell-Strategie bedeutet
6. **Auffälligkeiten** als Liste
7. **GEO-Hebel-Empfehlung** — konkrete, SEO-/Content-verankerte Hebel (FAQ-/Entity-Schema, Long-Form-Content mit Preistransparenz, Quell-Präsenz auf den zitierten Plattformen). Explizit als Multiplikator auf bestehende Kanäle formuliert, nicht als neuer Kanal.
8. **Methodik & Konfidenz** — kurzer Absatz: qualitative Stichprobe, nicht-deterministische KI-Antworten, `konfidenz: niedrig`; bei Voll-Quantitativ der Hinweis, dass Brand Radar die belastbarere Lesart ist.

### Schritt 12: HTML-Report `reports/<nummer>-geo-sichtbarkeit.html`

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschließlich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

**Report-Nummer:** Default ist `20` → `reports/20-geo-sichtbarkeit.html`. Die bestehenden Audit-Reports gehen aktuell bis `19` (`19-post-quality.html`). **Pflicht beim Lauf:** die nächste freie Nummer gegen `reports/index.html` (aus Drive) prüfen — ist `20` schon belegt, die nächste freie Nummer wählen. Numerisches Präfix wie in `contracts.md` Abschnitt 5.

Aus `reports/_shell.html` (aus Drive, `REPORTS_ID` via `find_by_name` + `read_text`) einen Audit-Report bauen:

- `{{TITLE}}` → `GEO-KI-Sichtbarkeit · KUNDE`
- `{{EYEBROW}}` → `MTA-Audit · GEO`
- `{{DISPLAY_NAME}}` → `GEO-KI-Sichtbarkeit: KUNDE`
- `{{META_LINE}}` → `Engines: ENGINES · N Prompts · M Akteure · Methode METHODE · Datenstand DATUM`
- `{{MAIN_CONTENT}}` →
  - **Stat-Strip oben**: Kunden-Sichtbarkeits-Quote (mit Konfidenz-Hinweis), Position von N Akteuren, Engine-Abdeckung, Anzahl zitierter Domains
  - **Einordnungs-Hinweis** als `.suggestion`-Block: "GEO ist ein Cross-Channel-Multiplikator, kein eigener Budgetposten."
  - **Sticky-TOC** zu allen Sektionen
  - **Sichtbarkeits-Heatmap** als `table.data` — Akteure (Zeilen) × Engines (Spalten), Zellen mit Badge `stark`/`mittel`/`schwach` je nach Sichtbarkeits-Quote
  - **Pro Akteur ein `details.dim`-Block** (default aufgeklappt: Kunde + Top-2): Prompts-sichtbar-Quote, Nennungs-Art-Verteilung, Beispiel-Prompts mit Treffer; bei Voll-Quantitativ zusätzlich Brand-Radar-Mentions
  - **Quellen-Ökosystem** als `table.data` — Top-Domains mit Quellen-Typ-Badge, Zitations-Anzahl, `gehoert_akteur`-Markierung
  - **Auffälligkeiten** als `.suggestion`-Blöcke, eine Karte pro Auffälligkeit
  - **GEO-Hebel** als `ol.top3` — Top-3-Hebel, SEO-/Content-verankert
  - **Methodik-Hinweis** als `.summary-card` mit `.note`: Stichproben-Charakter, `konfidenz: niedrig`
- `{{TOKEN_FOOTER}}` → `render-skill-counter`-Output
- `{{FOOTER_TEXT}}` → `MTA · KUNDE · GEO-KI-Sichtbarkeit-Audit`

### Schritt 13: Outputs nach Drive hochladen, Dashboard-Update, status.md

**Output-Uploads nach Drive** (inhaltliche Outputs zuerst, HTML zuletzt — siehe `contracts.md` Abschnitt 3):

```bash
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "geo-sichtbarkeit.md" /tmp/geo-sichtbarkeit.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "geo-sichtbarkeit-prompts.csv" /tmp/geo-sichtbarkeit-prompts.csv "text/csv"
python3 "$DRIVE_PY" upsert-text "$AUDITS_ID" "geo-sichtbarkeit-quellen.csv" /tmp/geo-sichtbarkeit-quellen.csv "text/csv"
```

Roh-JSONs gzip-komprimiert nach Drive `assets/raw/`:

```bash
RAW_ID=$(python3 "$DRIVE_PY" find-or-create-folder "$ASSETS_ID" "raw")
for f in ~/.cache/reachx-mta/<slug>/raw/geo-*.json; do
  gzip -k "$f"
  python3 "$DRIVE_PY" upsert-text "$RAW_ID" "$(basename "$f").gz" "$f.gz" "application/gzip"
done
```

HTML-Report (nach Validierung) → `REPORTS_ID`.

**Dashboard-Update** (`reports/index.html` aus Drive lesen, anpassen, zurückschreiben — siehe `contracts.md` Abschnitt 7): Stat-Strip um Kunden-GEO-Sichtbarkeit ergänzen, "Erledigt"-Sektion um `03-19-geo-ki-sichtbarkeit` erweitern, Reports-Liste um den neuen Report.

**status.md-Update** (aus Drive lesen, aktualisieren, via `upsert-text` zurückschreiben):

- `03-19-geo-ki-sichtbarkeit` in `schritte_done`, aus `schritte_offen` entfernen
- Eigene Sektion in "✓ Erledigt" mit Datum, Outputs, Modus, Kunden-Sichtbarkeits-Quote, wichtigste Auffälligkeit
- `naechster_empfohlen`: passender nächster Skill (z. B. `04-02-kanal-chancen-analyse` wenn genug Audits durch, sonst ein offener Audit-Skill)

### Schritt 14: Standard-Schlussformat im Chat

**Phase A (Schema-Vorschlag):**

```
⏸ 03-19-geo-ki-sichtbarkeit — Phase A abgeschlossen.

Schema-Vorschlag erstellt: audits/geo-sichtbarkeit-schema.md (auf Drive)
- Prompt-Inventar: N Prompts (informational / kommerziell / lokal)
- Akteur-Set: M Akteure
- Engines: ENGINES
- Brand Radar: verfuegbar | nicht verfuegbar (→ Lauf wird quantitativ | rein qualitativ)

Bitte das Prompt-Inventar und das Akteur-Set reviewen, anpassen, dann
status auf `bestaetigt` setzen und Skill erneut aufrufen.
Status aktualisiert in: status.md
```

**Phase B (Vollauf):**

```
✓ 03-19-geo-ki-sichtbarkeit abgeschlossen.
Modus: <Voll-Quantitativ | Voll-Qualitativ | Kunden-only>

Outputs (auf Drive):
- audits/geo-sichtbarkeit.md — Aggregat mit Sichtbarkeit, Engine-Vergleich, Quellen-Ökosystem, Hebel
- audits/geo-sichtbarkeit-prompts.csv — Prompt × Engine × Akteur (N Zeilen)
- audits/geo-sichtbarkeit-quellen.csv — zitierte Domains (M Zeilen)
- assets/raw/geo-*.json.gz — komprimierter Roh-Cache
- reports/<nummer>-geo-sichtbarkeit.html — Strategen-Report mit Sichtbarkeits-Heatmap
Status aktualisiert in: status.md

GEO-Lage:
- Engines geprüft:           ENGINES
- Prompts im Inventar:       N
- Kunden-Sichtbarkeit:       K von N Prompts (Quote Q% — Stichprobe, Konfidenz niedrig)
- Engine-Abdeckung Kunde:    E von ENGINE_ANZAHL
- Position im Akteur-Set:    X von M
- Zitierte Domains gesamt:   D
[Voll-Quantitativ zusätzlich:]
- Brand-Radar-Mentions:      ... (belastbarere Lesart)
- Share of Voice Kunde:      ...%

ℹ Einordnung
- GEO ist ein Cross-Channel-Multiplikator auf SEO/Content — kein eigener Budgetposten.
  Die Hebel sind FAQ-/Entity-Schema, Long-Form-Content, Quell-Präsenz auf zitierten Plattformen.

[Wenn Auffälligkeiten:]
⚠ Top-Auffälligkeiten:
- (1-3 Punkte, sortiert nach Relevanz)

[Wenn Voll-Qualitativ — Brand Radar fehlte:]
ℹ Rein qualitativer Lauf
- Kein Brand-Radar-Abo erkannt — Befunde basieren auf Prompt-Stichproben (Konfidenz niedrig).
  Für ein belastbares Share-of-Voice-Maß Brand Radar im Ahrefs-Abo freischalten und Skill erneut laufen lassen.

[Wenn Kunden-only-Modus:]
ℹ Kein Wettbewerber-Vergleich
- wettbewerber/liste.md nicht bestätigt — GEO-Sichtbarkeit nur für den Kunden erhoben.

Nächste Schritte:
1. 04-02-kanal-chancen-analyse — der GEO-Befund fließt als Multiplikator auf SEO/Content ein
2. (parallel möglich) [offener Audit-Skill] — wenn weitere Kanäle zu prüfen sind

Sag mir, welcher als nächster.
```

## Bundled Resources

- `reference/geo-analyse-methodik.md` — Engine-Set und Engine-spezifische Probe-Hinweise, Prompt-Probe-Durchführung via WebSearch/WebFetch, Treffer-Erkennung (Marken-Synonym-Match, Domain-Match), Quellen-Typ-Klassifikations-Heuristik, GEO-Hebel-Katalog, Einordnung als Cross-Channel-Multiplikator
- `reference/brand-radar-nutzung.md` — Ahrefs-Brand-Radar-Tool-Mapping (Mentions/SoV/Cited-Domains), Verfügbarkeits-/Abo-Check, Parameter, Fallback-Logik bei fehlendem Abo
- `reference/geo-output-schema.md` — Schema-Datei-Format (Phase A), Markdown-Frontmatter-Schema, beide CSV-Schemas mit Spalten-Definition, Schema-Validierungs-Regeln

## Edge Cases

- **Marken-Name kollidiert mit Common-Word** (Kunde heißt z. B. "Boost" oder "Strom"): die Treffer-Erkennung würde falsch-positiv anschlagen. Das Schema fordert in Phase A präzise Synonyme; bei Kollision wird ein Branchen-Disambiguator gefordert (Marke + Branchen-Token im Match) und in den Auffälligkeiten `marken_name_kollidiert` vermerkt.

- **KI-Antwort nicht-deterministisch / personalisiert**: dieselbe Frage liefert unterschiedliche Antworten. Der Skill behandelt jede Probe als **Stichprobe** — `konfidenz: niedrig` durchgängig. Optional kann der Stratege im Schema `probe_wiederholungen: 2-3` setzen, dann probt der Skill jeden Prompt mehrfach und aggregiert (Mehrheits-Befund); Default ist 1.

- **Engine liefert keine Quellen-Liste** (klassisches ChatGPT ohne Search-Modus): `zitiert` ist dann nicht erkennbar, nur `genannt`. Im Output für diese Engine `quellen_erhebbar: false` markieren, Quellen-Ökosystem stützt sich auf die Answer-Engines (Perplexity / Gemini).

- **WebSearch liefert keine KI-Overview-Snippets**: Wenn für einen Prompt keine generative Antwort erreichbar ist, Probe als `probe_fehlgeschlagen` markieren, nicht in die Sichtbarkeits-Quote einrechnen (Nenner reduzieren), im Body dokumentieren.

- **Brand Radar im Abo, aber 0 Daten für die Branche**: kleine/Nischen-Branchen sind in Brand Radar oft nicht abgedeckt. Kein Fehler — `brand_radar_daten: leer` markieren, Befund stützt sich auf die qualitativen Probes.

- **Lokaler Kunde ohne nationale Relevanz**: das Prompt-Inventar gewichtet dann die lokalen Varianten stärker. Bei rein lokalem Kunden sind nationale Prompts ggf. wenig aussagekräftig — im Schema-Body als Hinweis dokumentieren.

- **Reiner Online-/National-Kunde**: keine lokalen Prompt-Varianten — das Inventar besteht nur aus informationalen und kommerziellen nationalen Prompts.

- **Schema existiert, aber Akteur-Set veraltet** (WBs nach Schema-Bestätigung in `liste.md` geändert): der Skill nutzt das bestätigte Schema unverändert (Schema-vor-Lauf-Prinzip) und weist im Schluss-Format darauf hin, dass ein Schema-Refresh möglich ist.

- **Sehr großes Prompt-Inventar** (Stratege erweitert auf >20 Prompts): Hinweis im Schluss-Format, dass der Lauf länger dauert und mehr WebSearch/WebFetch-Calls verbraucht; kein Hard-Cap, aber Empfehlung ~10-15.

- **Alle Engines zeigen den Kunden unsichtbar**: das ist ein valides, häufiges Ergebnis (GEO ist ein junges Feld). Kein Fehler — Auffälligkeit `kunde_unsichtbar`, Output framt das als Ausgangslage mit klaren Hebeln, nicht als Mess-Problem.

## Wichtige Konventionen

Alle in `contracts.md` definierten Konventionen sind verbindlich:

- Outputs leben in Google Drive im MTA-Folder (Sub-Folder-IDs aus `meta.json`)
- Markdown + YAML-Frontmatter für das Aggregat, CSV für die Roh-Daten-Listen
- Standard-Schlussformat im Chat (zwei Varianten: Phase A / Phase B)
- `status.md` und Dashboard werden in jedem Lauf aktualisiert, auch bei Phase A
- HTML-Report basiert auf `reports/_shell.html` (aus Drive), vor Upload mit `validate-report.py` validiert
- **Roh-Daten** gzip-komprimiert in Drive `assets/raw/geo-*.json.gz` (lokaler Arbeits-Cache: `~/.cache/reachx-mta/<slug>/raw/`)
- **Schema-vor-Lauf** ist Pflicht — Phase A schlägt Prompt-Inventar und Akteur-Set vor, Phase B läuft erst nach `status: bestaetigt`
- **Konfidenz-Kennzeichnung Pflicht** — qualitative Probe-Werte tragen durchgängig `methode: qualitative_probe` und `konfidenz: niedrig`; Brand-Radar-Werte werden getrennt mit höherer Konfidenz ausgewiesen, nicht verrechnet
- **Einordnung Pflicht** — GEO wird im gesamten Output als Cross-Channel-Multiplikator auf SEO/Content geframt, niemals als eigener Budgetposten
- **Brand Radar ist OPTIONAL** — kein Pflicht-MCP; fehlendes Abo führt zum sauberen Qualitativ-Modus, nicht zum Abbruch
