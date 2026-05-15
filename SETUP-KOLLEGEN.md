# REACHX MTA-Plugin — Einrichtung und Nutzung für Kollegen

Diese Anleitung führt dich Schritt für Schritt durch die einmalige Einrichtung und den Start deiner ersten MARKE&TING-Analyse mit dem Plugin. Plane für die erste Einrichtung **ca. 30 Minuten** ein. Danach ist jede neue MTA in unter einer Minute gestartet.

## Was du am Ende hast

- 33 Skills, die als Slash-Commands in Claude Code verfügbar sind (`/01-01-mta-projekt-init`, `/02-01-kunden-marken-profil`, …)
- Automatischer Drive-Workflow: Outputs landen direkt im REACHX Shared Drive, in dem MTA-Ordner, den du beim Init angegeben hast
- Audit-Trail: jeder Kollege schreibt mit seinem eigenen REACHX-Google-Account — Drive zeigt für jeden File "Geändert von: …"
- Automatische Update-Hinweise beim Session-Start, wenn Sascha eine neue Plugin-Version released

---

## Teil 1 — Voraussetzungen

Du brauchst auf deinem Rechner:

1. **macOS oder Windows** mit Terminal-Zugang
2. **Claude Code CLI** ([Installation](https://docs.claude.com/claude-code/setup))
3. **Python 3.9+** (auf macOS Standard, auf Windows ggf. nachinstallieren)
4. **`gws` CLI** (Google Workspace CLI — installieren wir gleich)
5. **REACHX-Google-Account** mit Schreibrechten im Shared Drive *Kunden*
6. **API-Tokens** parat halten:
   - Apify-Token: https://console.apify.com/account/integrations
   - Sistrix-API-Key: aus eurer Sistrix-Konto-Verwaltung
   - (Weitere je nach Skill-Familie, siehe Teil 4)

Wenn du bei einem Punkt unsicher bist, frag Sascha — die Setup-Schritte unten setzen alle sechs Punkte voraus.

---

## Teil 2 — Einmalige Einrichtung

### Schritt 1: `gws` CLI installieren

`gws` ist die Google-Workspace-CLI, mit der die Skills Files in Drive schreiben/lesen. Im Terminal:

```bash
npm install -g @reachx/gws-cli
# oder, je nachdem wie ihr gws verteilt:
# brew install gws
```

Verifizieren, dass es klappt:

```bash
which gws
# sollte einen Pfad zeigen, z.B. /Users/<du>/.npm-global/bin/gws

gws --version
```

### Schritt 2: `gws` mit deinem REACHX-Google-Account authentifizieren

```bash
gws auth login
```

Das öffnet einen Browser, du loggst dich mit deinem `vorname.nachname@reachx.de`-Account ein und bestätigst die Berechtigungen (Drive lesen/schreiben, Slides lesen, etc.).

Verifizieren:

```bash
gws drive drives list --params '{"fields":"drives(name)", "pageSize":5}'
# sollte eine Liste eurer Shared Drives anzeigen, inkl. *Kunden*
```

Wenn ein Fehler "Permission denied" kommt: Sascha um Zugang zum *Kunden*-Shared-Drive bitten.

### Schritt 3: API-Tokens in Claude Code Settings eintragen

Öffne `~/.claude/settings.json` in einem Editor:

```bash
open -e ~/.claude/settings.json
# oder mit deinem Lieblings-Editor
```

Im JSON gibt es einen `env`-Block. Ergänze ihn um deine Tokens — Komma nach der bestehenden Zeile nicht vergessen:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "APIFY_TOKEN": "apify_api_DEIN_TOKEN_HIER",
    "SISTRIX_API_KEY": "dein_sistrix_token_hier"
  },
  "permissions": {
    ...lässt du wie es ist...
  }
}
```

Speichern. **Wichtig:** Falls Claude Code gerade läuft, beenden und neu starten — Settings werden beim Start gelesen.

### Schritt 4: Plugin-Marketplace hinzufügen

In einer beliebigen Claude-Code-Session:

```
/plugin marketplace add behmueller/reachx-claude-skills
```

Das klont das Marketplace-Repo lokal. Wenn der Befehl mit "SSH authentication failed" abbricht, setze in deiner Shell:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

und versuche es erneut.

### Schritt 5: Plugin installieren

```
/plugin install marke-und-ting-analyse-reachx@reachx-skills
```

Wenn alles klappt, siehst du eine Bestätigung. Verifizieren: tippe `/01` — du solltest die 33 MTA-Skills (`/01-01-mta-projekt-init`, `/01-02-kickoff-transcript-parser`, …) im Picker sehen, alle gekennzeichnet mit `(marke-und-ting-analyse-reachx)`.

**Fertig mit dem Setup.** Ab hier ist jeder neue MTA-Start in unter einer Minute drin.

---

## Teil 3 — Deine erste MTA starten

### Schritt 1: MTA-Ordner im Drive vorbereiten

Öffne den REACHX Shared Drive im Browser oder im Drive Desktop. Navigiere:

```
Geteilte Ablagen
  └── Kunden
       └── <Kundenname>          ← falls noch nicht da: anlegen
            └── Marke&Ting Analyse
                 └── MTA <Kunde> <Monat>     ← neu anlegen, LEER lassen
```

Klick auf den neu angelegten **MTA-Ordner**, dann oben in der URL-Leiste die volle URL kopieren (sieht aus wie `https://drive.google.com/drive/folders/1abc...?usp=sharing`).

### Schritt 2: Lokales Working Directory für Claude Code

**⚠️ Wichtig:** Claude Code darf **NICHT** im Drive-Desktop-gemounteten Folder gestartet werden. Das löst File-Descriptor-Probleme aus, weil Claude beim Start das Verzeichnis scannt und der Drive-Mount Tausende Files enthält.

Stattdessen: ein leichtes, lokales Working Directory. Einmal anlegen:

```bash
mkdir -p ~/REACHX/mta-work
cd ~/REACHX/mta-work
```

Dann Claude Code starten:

```bash
claude
```

### Schritt 3: MTA initialisieren

In Claude Code:

```
/01-01-mta-projekt-init
```

Der Skill fragt dich nach fünf Stammdaten:

1. **Kundenname** — z.B. `Müller Hausverwaltung GmbH`
2. **Branche** — z.B. `Hausverwaltung`
3. **Region** — z.B. `Frankfurt am Main`
4. **Website-URL** — z.B. `https://www.mueller-hausverwaltung.de`
5. **Drive-MTA-Ordner-URL** — die URL aus Schritt 1

Optional kannst du auch Kickoff-Datum und MTA-Deadline angeben.

Danach zeigt der Skill dir die Zusammenfassung und legt nach deinem `ja` alle Sub-Folders + `meta.json` + `status.md` + Dashboard im Drive an. Das Dashboard ist eine `index.html` im `reports/`-Sub-Folder — kannst du in Drive direkt ansehen.

### Schritt 4: Optional — Kickoff-Transkript hochladen

Wenn du ein Kickoff-Transkript (Fireflies, Gemini, Plaud) hast, lade es im Drive-Web-Interface in den `input/transkripte/`-Sub-Folder hoch. Der nächste Skill (`01-02-kickoff-transcript-parser`) findet es dort.

### Schritt 5: Folge-Skills nach `status.md`

Jeder Skill aktualisiert am Ende `status.md` im MTA-Folder und schlägt den nächsten Skill vor. Du kannst dich einfach nach der Empfehlung richten. Die typische Reihenfolge:

```
01-01-mta-projekt-init                  (du bist gerade hier)
└── 01-02-kickoff-transcript-parser     (wenn Transkript da)
    └── 02-01-kunden-marken-profil
        └── 02-02-wettbewerber-identifikation   (Schema-vor-Lauf*)
            └── 02-03-wettbewerber-marken-profil
                └── 02-04-branchenportal-recherche
                    └── 03-* SEO/SEA/Social/Web/Local Audits (16 Skills, viele parallel möglich)
                        └── 04-* Synthese (6 Skills, sequenziell)
                            └── 05-* Output (Slides, Final-Export)
                                └── 06-* Optional: Deck-QA
```

**\* Schema-vor-Lauf:** Manche Skills laufen in zwei Phasen. Phase A schreibt einen Vorschlag (z.B. `wettbewerber/identifikation-schema.md`) und stoppt. Du reviewst das Schema im Drive-Web-Interface, änderst falls nötig, und setzt `status: bestaetigt`. Beim erneuten Aufruf des Skills läuft Phase B mit deinen Anpassungen. Skills mit Schema-vor-Lauf: `02-02`, `03-03`, `03-15`, `03-16`, `04-01`, `04-04`.

---

## Teil 4 — Eine MTA fortsetzen (Resume)

Wenn du eine MTA an einem anderen Tag oder von einem anderen Skill aus weitermachen willst:

```
/01-01-mta-projekt-init
```

Gib dieselbe Drive-MTA-Ordner-URL an wie beim ersten Mal. Der Skill erkennt automatisch, dass dort schon eine `meta.json` liegt, liest sie und `status.md`, und sagt dir wo du stehst:

```
✓ MTA fortgesetzt — kein Neuanlage notwendig.

MTA-Stand:
- Kunde:      Müller Hausverwaltung GmbH
- Slug:       mta-mueller-hausverwaltung-gmbh-2026-05
- Erledigt:   01-01, 01-02, 02-01 (siehe status.md)
- Nächster:   02-02-wettbewerber-identifikation

Soll ich mit 02-02 weitermachen?
```

Du kannst die MTA auch ohne `01-01`-Re-Run weitermachen, wenn du den Active-MTA-Cache nicht verloren hast (also wenn du auf derselben Maschine bleibst und `~/.cache/reachx-mta/active-mtas.json` existiert). Aber `01-01` als Wiedereinstieg ist die sichere Variante.

---

## Teil 5 — Updates ziehen

### Automatischer Hinweis

Beim Session-Start von Claude Code prüft das Plugin (max alle 6 Stunden), ob auf GitHub eine neue Version verfügbar ist. Falls ja, siehst du einen Hinweis wie:

> REACHX MTA-Plugin: Update verfügbar (installiert: 0.1.0 → neu: 0.1.1).

### Update ziehen

```
/plugin marketplace update reachx-skills
/plugin update marke-und-ting-analyse-reachx@reachx-skills
```

Erst refresht den Marketplace-Index, dann zieht die neue Version. Nach dem Update Claude Code neu starten, damit die neuen SKILL.md-Dateien geladen werden.

### Changelog lesen

Was sich in einer Version geändert hat, steht im [CHANGELOG](https://github.com/behmueller/reachx-claude-skills/blob/main/CHANGELOG.md).

---

## Teil 6 — Häufige Probleme

### `An unknown error occurred, possibly due to low max file descriptors`

Du hast Claude Code in einem Drive-Desktop-Mount gestartet. Lösung: Claude Code beenden, in ein lokales Working Directory wechseln (`cd ~/REACHX/mta-work`), neu starten. Drive wird trotzdem voll funktionieren — die Skills schreiben über die API, nicht über den lokalen Mount.

### `gws: command not found` oder `gws auth status` zeigt nicht eingeloggt

`gws` ist nicht installiert oder nicht authentifiziert. Zurück zu Teil 2, Schritt 1 + 2.

### `Kein Schreibrecht auf Folder` beim Init

Dein REACHX-Google-Account hat keinen Schreibzugriff auf den Kunden-Folder im Shared Drive. Bitte Sascha (oder den Drive-Admin) um Schreibrechte für das *Kunden*-Shared-Drive (oder zumindest für den entsprechenden Kunden-Folder).

### `MTA nicht im Active-Cache. Bitte 01-01-mta-projekt-init aufrufen.`

Du hast einen Folge-Skill aufgerufen, ohne dass `01-01-mta-projekt-init` für diese MTA gelaufen ist. Lösung: erst `01-01` mit der Drive-URL, dann der Folge-Skill.

### Apify- oder Sistrix-Skill bricht ab mit "Token fehlt"

Die Env-Variable `APIFY_TOKEN` oder `SISTRIX_API_KEY` ist nicht gesetzt. Zurück zu Teil 2, Schritt 3 — Token in `~/.claude/settings.json` ergänzen und Claude Code neu starten.

### Skill-Picker zeigt die MTA-Skills nicht an

Plugin ist nicht installiert oder nicht geladen. Prüfen mit `/plugin list` — wenn `marke-und-ting-analyse-reachx@reachx-skills` nicht erscheint, nochmal `/plugin install …` aus Teil 2, Schritt 5.

### Plugin-Update bricht mit SSH-Fehler ab

Setze `export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` in deiner Shell (z.B. in `~/.zshrc` dauerhaft eintragen) und versuche es erneut.

### `Schema 2.0`-Hinweis bei Folge-Skill

Du hast eine ältere MTA, die noch nicht das aktuelle Schema 2.1 hat. Lösung: ruf `01-01-mta-projekt-init` mit der Drive-URL erneut auf — der Skill erkennt den älteren Schema-Stand und migriert automatisch (legt fehlende Sub-Folder wie `input/transkripte/` an, aktualisiert `meta.json`).

---

## Teil 7 — Wo melde ich Probleme?

**Falls ein Skill abbricht, ein Output unklar ist, oder ein Pattern komisch wirkt:**

1. **Slack #reachx-mta-skills** — schneller Fix, oder Sascha klont kurz und prüft
2. **GitHub Issues:** https://github.com/behmueller/reachx-claude-skills/issues (privat — geht nur mit Repo-Zugang)

Beim Melden hilfreich:
- Welcher Skill?
- Welche Drive-URL der MTA?
- Bei Fehlern: die letzte Output-Zeile aus Claude Code
- Was hast du erwartet, was ist passiert?

---

## Anhang: Modell-Strategie hinter den Skills

Das Plugin nutzt drei Subagents, um Token-Verbrauch klein zu halten und gleichzeitig bei wichtigen Stellen volle Power zu liefern. Das passiert automatisch — du musst nichts einstellen — aber gut zu wissen wie:

- **`mta-rechercheur` (Sonnet 4.6)** — alle Audit- und Recherche-Skills (21 Stück). Sonnet ist schnell, günstig und reicht für strukturierte Daten-Erhebung vollständig aus.
- **`mta-stratege` (Opus 4.7)** — die 10 strategischen Synthese-Skills (Positionierung, Kanal-Chancen, Forecast, 90-Tage-Plan, Retainer, Keyword-Cluster, Deck-QA). Hier zahlt sich Opus durch mehrdimensionale Abwägungen aus.
- **`mta-techniker` (Haiku 4.5)** — Templating und HTML-Mechanik (2 Skills). Haiku, weil reine Mechanik.

Wenn du den maximalen Output bei den Synthese-Skills willst, kannst du **vor dem Skill-Aufruf** dein Claude-Code-Hauptthread-Modell auf "Opus high effort" stellen. Der `mta-stratege` erbt das. Bei den Recherche-Skills lohnt sich das nicht — Sonnet ist da schon optimal.

---

**Stand:** 2026-05-15 · Plugin-Version 0.1.1 · Maintainer: Sascha Behmüller (sascha.behmueller@reachx.de)
