# Changelog

Alle nennenswerten Änderungen am REACHX-Skills-Marketplace und seinen Plugins.

Format orientiert an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semver](https://semver.org/lang/de/).

## [Unreleased]

### Geplant für 1.0.0

- Live-Test mit echtem Kundenprojekt durchlaufen, ggf. Korrekturen
- First-Party-Google-Ads-Skill (siehe MTA-SKILLS-PLAN: bekannte Lücken)

## [0.3.0] — 2026-05-15 — Token-Tracking pro MTA

### Hinzugefügt — Live-Token-Tracking mit EUR-Cost-Aufschlüsselung

Du siehst jetzt pro MTA live, wieviele Tokens verbraucht wurden — total, pro Modell (Opus/Sonnet/Haiku) und pro Skill — und was das in Euro kostet. Sichtbar im Dashboard (`reports/index.html`) und im Footer jedes Skill-Reports.

- **`token-tracker.py`** (neu, in `01-01-mta-projekt-init/scripts/`) — Aggregiert Claude-Code-Session-JSONLs (`~/.claude/projects/<cwd>/*.jsonl`) inkrementell mit Cursor-State. CLI: `tick`, `aggregate <slug>`, `render-counter <slug> --style {stat-strip|breakdown|md}`, `render-skill-counter <slug> <skill-name>`, `mark-skill-start`, `mark-skill-end`. Pricing-Tabelle Opus 4.7/Sonnet 4.6/Haiku 4.5 hardcoded (USD), EUR-Konversion via Env `REACHX_USD_TO_EUR` (Default 0.92).
- **Stop-Hook** (`hooks/hooks.json` + `scripts/post-stop-token-sync.sh`) — Läuft nach jedem Prompt non-blocking. Lokale Aggregation immer, Drive-Push gedrosselt alle 5 Minuten (`token-usage.json` im neuen `meta/`-Sub-Folder).
- **`01-01-mta-projekt-init`** — Schritt 9b initialisiert `meta/token-usage.json` auf Drive. `register-mta` speichert jetzt automatisch `working_dir` (aus `os.getcwd()`) für robuste Project-Resolution ohne Heuristik. Dashboard-Render bindet Stat-Strip- und Breakdown-Counter ein.
- **`report-shell.html`** — Zwei neue Platzhalter: `{{TOKEN_BREAKDOWN}}` (für Dashboard-Detail-Sektion) und `{{TOKEN_FOOTER}}` (für Skill-Report-Footer). Wenn nicht befüllt: leerer String.
- **32 Folge-SKILL.md** — Token-Tracking-Block nach `## Ausführungs-Modus` eingefügt, mit `mark-skill-start`/`mark-skill-end`-Pattern und Hinweis zum `{{TOKEN_FOOTER}}`-Render.
- **`contracts.md` Sektion 10** — Volle Doku der Token-Tracking-Konvention inklusive Pricing-Tabelle und Pflicht-Pattern.

### Bekanntes

- Tokens aus Drittanbieter-APIs (Apify, Sistrix, Ahrefs, gws) werden NICHT getrackt — nur Claude-Code-Tokens.
- Bestands-MTAs vor diesem Release: Token-Cursor startet leer, Re-Aggregate für Vollständigkeit via `rm ~/.cache/reachx-mta/<slug>/token-tracker-cursor.json && python3 token-tracker.py aggregate <slug>`.
- Drive-Push frequenz fest auf 300s gedrosselt — falls Drive-Volumen zu hoch wird, lieber Pushen auf nur "am Skill-Ende" umstellen.

## [0.2.1] — 2026-05-15

### Geändert — Bot-Protector-Handling für Branchenportale

- **`02-04-branchenportal-recherche` nutzt jetzt `apify/website-content-crawler` für Jameda.** Live-Test ist bei Jameda auf einen Bot-Protector gestoßen (vermutlich Datadome/Cloudflare-Variante), direkte HTTP-Crawls bekommen 403/429. Neue Methode A2 im Mapping eingeführt: `apify/website-content-crawler` mit `crawlerType: playwright:chrome` + Residential-Proxy + `removeCookieWarnings: true`. Wickelt JavaScript ab, rotiert IPs, umgeht damit die meisten Bot-Schutze (Cloudflare-Challenge, Datadome, PerimeterX, JS-Cookie-Walls). Profil-URL wird vorab über Web-Search ermittelt und dem Crawler als `startUrls` übergeben.
- **`portal-scraper-mapping.md`** Methoden-Glossar um Methode A2 erweitert. Standard-Config dokumentiert (10-Felder JSON-Snippet). Jameda-Eintrag explizit auf A2 umgestellt mit Hinweis "Bot-Protector erkannt 2026-05-15, A2 ist hier Pflicht, kein Fallback auf B".
- **`02-04` SKILL.md** Schritt 4 erweitert: Mapping-Reihenfolge wird strikt befolgt (kein B-Fallback, wenn Mapping A2 vorschreibt). Wenn ein Lauf trotz B in einen Bot-Protector läuft (403/429/Cloudflare-Challenge), wird das Portal automatisch ins Mapping als A2 dokumentiert und erneut versucht. Output-Datei trackt `methode: A2_after_bot_protector_fallback`.

### Setup-Doku

- **`SETUP-KOLLEGEN.md`** in v0.2.0 ergänzt (war im Tag noch nicht drin). Vollständige Schritt-für-Schritt-Anleitung für Onboarding nicht-technischer Kollegen — Voraussetzungen, gws-Setup, Plugin-Install, erste MTA, Resume, Troubleshooting.

## [0.2.0] — 2026-05-15

### Geändert — Schema-Erweiterung 2.0 → 2.1

- **Neuer Drive-Sub-Folder `input/` mit `input/transkripte/`.** Quell-Files (z.B. Meeting-Transkripte), die der Stratege selbst bereitstellt, leben jetzt nicht mehr lokal beim Strategen, sondern direkt auf Drive im MTA-Folder. Skills lesen daraus, schreiben aber niemals dort hinein. Begründung: Reproduzierbarkeit für alle Kollegen (kein "liegt nur auf einer Maschine"), Audit-Trail, einheitliche Datenheimat. Aktuell genutzt von `01-02-kickoff-transcript-parser`; weitere Sub-Sub-Folder unter `input/` (z.B. `screenshots/`, `dokumente/`) können in späteren Versionen ergänzt werden.
- **`01-01-mta-projekt-init`** legt den `input/`-Sub-Folder und `input/transkripte/` beim Init und beim Resume idempotent an. `meta.json` Schema-Version auf `2.1` mit neuem `drive.subfolders.input` plus `drive.input_subfolders.transkripte`-Block. Resume-Pfad ergänzt fehlende Sub-Folder bei bestehenden Schema-2.0-Projekten automatisch und hebt das Schema.
- **`01-02-kickoff-transcript-parser`** liest das Transkript jetzt aus Drive `input/transkripte/` statt vom lokalen Filesystem. Schritt 2 lädt das gewählte File in den lokalen Cache, parst dort und schreibt Briefing nach `data/`. Bei mehreren Files in `input/transkripte/` fragt der Skill nach (oder akzeptiert einen `Transkript-Dateiname`-Parameter). Schema-Version-Check: bricht bei 2.0 mit klarem Hinweis auf 01-01-Resume ab.
- **`briefing-schema.md`** (`schema_version: 1.1`): `transkript_quelle.pfad` ersetzt durch `drive_file_id` + `drive_url` + `dateiname`. Append-Modus (mehrere Meetings pro Kunde) klar dokumentiert.
- **`contracts.md`** (Schema 2.1): neue Sektion "Input-Sub-Folder" mit Tabelle (Sub-Sub-Folder × Befüller × Leser), Dateinamen-Empfehlung `<typ>-<YYYY-MM-DD>.<ext>`, Migrations-Hinweis 2.0 → 2.1 via 01-01-Resume.

### Hinweis für laufende Projekte

Bestehende Schema-2.0-MTAs (falls bereits live angelegt) werden automatisch migriert: `01-01-mta-projekt-init` mit derselben Drive-URL erneut aufrufen — der Resume-Pfad ergänzt `input/transkripte/` idempotent und hebt das Schema in der `meta.json`.

## [0.1.1] — 2026-05-15

### Geändert

- **`mta-stratege`-Subagent: Denk-Modus-Block ergänzt.** Pflicht-Reflexions-Loop vor jeder strategischen Empfehlung (Daten-Sichtung → 3+ Hypothesen → Gegen-Argumente → Entscheidung mit Begründung → Bandbreiten). Begründung: Subagent-Frontmatter unterstützt kein `effort`-Feld; der Effort wird vom Hauptthread vererbt. Der Denk-Modus zwingt Opus zu mehrdimensionaler Reflexion unabhängig vom Hauptthread-Effort und verhindert "erste plausible Antwort"-Pattern. Im Hauptthread auf `high effort` läuft der Loop als strukturierte Leitplanke, damit Opus seine Tokens auf die richtigen Fragen lenkt.

### Verifiziert beim Live-Test 01-01

- Subagent-Routing funktioniert: Hauptthread erkennt `## Ausführungs-Modus`-Block und startet automatisch `mta-rechercheur` für 01-01-mta-projekt-init.
- Plugin-Pfad-Auflösung sauber: `${CLAUDE_PLUGIN_ROOT}` wird in der Plugin-Cache-Lokation `~/.claude/plugins/cache/reachx-skills/marke-und-ting-analyse-reachx/<version>/skills/...` aufgelöst.
- Drive-Schreibvorgänge via `gws` über `drive.py` laufen aus dem Plugin-Kontext heraus.

## [0.1.0] — 2026-05-14 — Alpha-Release

Initialer Marketplace-Build. **Alpha**, weil Drive-Migration noch live getestet werden muss und Subagent-Routing nicht im echten MTA-Lauf verifiziert ist.

### Hinzugefügt

- **Marketplace-Skelett** `reachx-skills` als interner REACHX-Marketplace.
- **Plugin `marke-und-ting-analyse-reachx` 0.1.0** mit 33 MTA-Skills.
- **Stufen-Nomenklatur `NN-NN-name`** für alle Skill-Namen — Filesystem-Sortierung entspricht der MTA-Reihenfolge.
- **Drei Subagents**:
  - `mta-rechercheur` auf Sonnet 4.6 — 21 Audit-/Recherche-Skills (Stufen 01–03)
  - `mta-stratege` auf Opus 4.7 — 10 Synthese-/Bewertungs-Skills (Stufe 04 + Deck-QA)
  - `mta-techniker` auf Haiku 4.5 — 2 Templating-Skills (Stufe 05)
- **Subagent-Routing in allen 33 SKILL.md** verdrahtet (`## Ausführungs-Modus`-Block).
- **SessionStart-Update-Check-Hook** — informiert beim Session-Start, wenn eine neue Plugin-Version im GitHub-Repo verfügbar ist. Caching 6 Stunden, lautlos bei Offline-Betrieb.
- **Drive-basierter Workflow (Schema 2.0)** — MTA-Outputs leben in Google Drive über `gws` CLI:
  - `01-01-mta-projekt-init` voll umgestellt (Pilot, getestet)
  - `scripts/drive.py` Helper mit Python-API und CLI
  - `contracts.md` auf Schema 2.0 (`drive`-Block in `meta.json`)
  - Active-MTA-Cache unter `~/.cache/reachx-mta/active-mtas.json`
  - Resume-Logik direkt in `01-01-mta-projekt-init`
  - Schritt-für-Schritt-Migrationspattern für die anderen 32 Skills via `MIGRATION-DRIVE.md`

### Migrierte Skills (Stufen-Nomenklatur)

- **Stufe 01 (Setup):** `01-01-mta-projekt-init`, `01-02-kickoff-transcript-parser`
- **Stufe 02 (Marken/Wettbewerber):** `02-01-kunden-marken-profil`, `02-02-wettbewerber-identifikation`, `02-03-wettbewerber-marken-profil`, `02-04-branchenportal-recherche`
- **Stufe 03 SEO:** `03-01-seo-sichtbarkeit-und-rankings`, `03-02-seo-keyword-recherche`, `03-03-seo-keyword-kategorisierung`, `03-04-seo-first-party-gsc`
- **Stufe 03 SEA:** `03-05-sea-google-ads-check`, `03-06-sea-meta-ads-library-check`, `03-07-sea-linkedin-ads-library-check`
- **Stufe 03 Social:** `03-08-social-instagram`, `03-09-social-tiktok`, `03-10-social-pinterest`, `03-11-social-linkedin`, `03-12-social-linkedin-post-quality`, `03-13-social-reddit-fit-check`
- **Stufe 03 Web/Local:** `03-14-web-tech-und-tracking`, `03-15-web-content-inventur`, `03-16-local-gmb-und-seo`
- **Stufe 04 (Synthese):** `04-01-positionierungs-analyse`, `04-02-kanal-chancen-analyse`, `04-03-ziele-aus-potenzialen`, `04-04-forecast-modell`, `04-05-90-tage-plan`, `04-06-retainer-kalkulator`
- **Stufe 05 (Output):** `05-01-mta-slide-bausteine`, `05-02-mta-export-to-drive`
- **Stufe 06 (Deck-QA):** `06-01-action-titles-check`, `06-02-pyramid-structure-check`, `06-03-mta-inhaltscheck`

### Voraussetzungen für Kollegen

- `gws` CLI installiert + mit persönlichem REACHX-Google-Account authentifiziert
- Schreibrechte im REACHX Shared Drive
- Pro MTA: Projektleiter legt im Shared Drive einen MTA-Folder im Kunden-Ordner an, gibt URL beim Init mit
