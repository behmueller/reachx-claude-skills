# Changelog

Alle nennenswerten Änderungen am REACHX-Skills-Marketplace und seinen Plugins.

Format orientiert an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
Versionierung nach [Semver](https://semver.org/lang/de/).

## [Unreleased]

### Geplant für 1.0.0

- Live-Test mit echtem Kundenprojekt durchlaufen, ggf. Korrekturen
- Subagent-Routing in Echtlauf verifizieren (Hauptthread → Subagent-Aufruf wirklich automatisch?)
- Setup-Doku für nicht-technische Kollegen schreiben (gws-Auth, Plugin-Install)

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
