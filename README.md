# REACHX Claude-Skills

Internes Marketplace-Repository für REACHX-eigene Claude-Skills. Verteilt Skills an interne Strategen und Kollegen über das Claude-Code-Plugin-System mit sauberer Versionierung und Update-Mechanik.

## Was hier drin ist

Aktuell ein Plugin:

- **`marke-und-ting-analyse-reachx`** — 33 Skills, die die REACHX MARKE&TING-Analyse (MTA) automatisieren. Vom Kickoff-Transkript über Marken-Profile, Wettbewerbs-Recherche, Multi-Channel-Audits (SEO, SEA, Social, Web-Tech, Local) bis zur Synthese (Positionierung, Kanal-Chancen, Forecast, 90-Tage-Plan, Retainer). Inklusive drei Subagents (`mta-rechercheur` auf Sonnet, `mta-stratege` auf Opus, `mta-techniker` auf Haiku), die das Token-Budget des Hauptthreads schlank halten.

Weitere Plugins können hier in Zukunft hinzukommen (z.B. Outreach-Tools, Reporting-Workflows).

## Installation für Kollegen

**Voraussetzung:** Claude Code CLI installiert (`claude --version` funktioniert). Falls nicht: https://docs.claude.com/claude-code/setup

**Marketplace einmalig hinzufügen:**

```bash
/plugin marketplace add behmueller/reachx-claude-skills
```

(Wenn das Repo später in eine REACHX-Org wandert, ändert sich der Pfad entsprechend.)

**Plugin installieren:**

```bash
/plugin install marke-und-ting-analyse-reachx@reachx-skills
```

**Updates ziehen (wenn Hinweis beim Session-Start auftaucht):**

```bash
/plugin marketplace update reachx-skills
/plugin update marke-und-ting-analyse-reachx@reachx-skills
```

Der erste Befehl refresht den Marketplace-Index (sagt Claude "es gibt eine neue Version"); der zweite zieht die neue Version tatsächlich in den lokalen Plugin-Cache.

## MCP-Voraussetzungen

Die meisten MTA-Skills brauchen externe Datenquellen. Bevor die Skills genutzt werden können, müssen folgende MCPs in Claude Code verbunden sein:

| MCP | Wofür | Pflicht? |
|---|---|---|
| Ahrefs | Keyword-Recherche, Difficulty, GSC-Proxy | **Ja** für SEO-Skills |
| Sistrix | Sichtbarkeit, DACH-Volumen | Ja für `seo-sichtbarkeit-und-rankings` |
| Apify | Scraping (Maps, Instagram, TikTok, Pinterest, LinkedIn) | Ja für Social-Audits |
| BuiltWith / Wappalyzer | Tech-Stack-Erhebung | Ja für `website-tech-und-tracking-audit` |
| Google Workspace (gws-CLI) | Slides-Reviews | Ja für `action-titles-check`, `pyramid-structure-check`, `mta-inhaltscheck` |

Setup-Anleitung pro MCP siehe `SETUP-KOLLEGEN.md` (folgt in Phase 3).

## Modell-Strategie

Die MTA verbraucht potenziell viele Tokens. Um eine ganze MTA in einer Session machbar zu halten, routet das Plugin Arbeit über drei Subagents:

- **`mta-rechercheur` (Sonnet 4.6)** — alle Audit- und Recherche-Skills. Sonnet reicht für strukturierte Tool-Call-Outputs vollständig aus.
- **`mta-stratege` (Opus 4.7)** — die sieben strategischen Synthese-Skills: `positionierungs-analyse`, `seo-keyword-kategorisierung`, `kanal-chancen-analyse`, `ziele-aus-potenzialen-ableiten`, `forecast-modell`, `90-tage-plan-generator`, `retainer-kalkulator`. Hier rechtfertigt die kognitive Schwere den Opus-Einsatz.
- **`mta-techniker` (Haiku 4.5)** — Templating, HTML-Reports, Slide-Bausteine, Drive-Export. Reine Mechanik.

Der Hauptthread orchestriert, ruft die Skills via `Agent`-Tool mit dem passenden `subagent_type`. Die Rohdaten der Audits landen nie im Hauptthread — nur die kompakten Subagent-Schlussberichte. Effekt: Hauptthread-Kontext bleibt schlank, ganze MTA in einer Session machbar.

## Repo-Struktur

```
reachx-claude-skills/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── marke-und-ting-analyse-reachx/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── skills/             # 32 SKILL.md-Ordner
│       ├── agents/             # 3 Subagent-Definitionen
│       ├── hooks/
│       │   └── hooks.json      # SessionStart-Update-Check
│       └── scripts/
│           └── check-version.sh
├── CHANGELOG.md
└── README.md
```

## Update-Mechanik

Das Plugin enthält einen `SessionStart`-Hook (`scripts/check-version.sh`), der bei jedem Session-Start prüft, ob es eine neuere Version im GitHub-Repo gibt. Vergleich erfolgt zwischen `plugin.json` (lokale Version) und dem neuesten Release-Tag im Repo.

Caching: Max 1x pro 6 Stunden gegen GitHub geprüft. Bei Netzwerkproblemen lautlos. Bei verfügbarem Update: kurzer Hinweis als `additionalContext` an Claude, der den User beim Session-Start informieren kann.

**Wichtig:** Der Hook informiert über Updates, holt sie aber **nicht automatisch**. Der Kollege muss aktiv `/plugin update` tippen — das ist Absicht, damit niemand mitten in einer Kundenarbeit eine veränderte Logik untergeschoben bekommt.

## Release-Workflow (für REACHX-internen Maintainer)

Bei jeder Skill-Änderung, die ausgerollt werden soll:

1. Änderungen committen und pushen
2. `plugins/marke-und-ting-analyse-reachx/.claude-plugin/plugin.json` → `version` hochzählen (semver: PATCH für Bugfixes, MINOR für neue Skills, MAJOR für Breaking Changes in der Skill-Reihenfolge oder den Subagent-Verträgen)
3. `CHANGELOG.md` Eintrag hinzufügen
4. Git-Tag setzen: `git tag v1.0.1 && git push --tags`
5. GitHub Release erstellen (optional, aber empfohlen): `gh release create v1.0.1 --notes-from-tag`

Kollegen sehen beim nächsten Session-Start den Update-Hinweis.

## Kontakt

Maintainer: Sascha Behmüller (sascha.behmueller@reachx.de)
