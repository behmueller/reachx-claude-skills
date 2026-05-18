# GEO-Analyse-Methodik

Methodik für das `03-19-geo-ki-sichtbarkeit`-Audit: Engine-Set, Prompt-Probe-Durchführung, Treffer-Erkennung, Quellen-Typ-Klassifikation, GEO-Hebel-Katalog. Aus dem SKILL.md Schritt 5, 7 und 11 verwiesen.

**Stand:** Mai 2026

## Grundverständnis — was GEO ist und was nicht

**GEO = Generative Engine Optimization.** Die Disziplin, eine Marke so aufzustellen, dass generative Such-Engines (ChatGPT, Gemini / Google AI Overviews, Perplexity, Claude) sie in ihren Antworten **nennen** oder als **Quelle zitieren**.

**Was GEO im MTA-Kontext ist:**

- Ein **Cross-Channel-Multiplikator** — KI-Sichtbarkeit ist eine Folge starker SEO-/Content-/Reputations-Arbeit, nicht eine eigenständige Disziplin mit eigenem Budget.
- Eine **Mess-Linse** auf bestehende Kanäle: Wenn der Kunde organisch stark ist und auf den richtigen Plattformen präsent ist, taucht er auch in KI-Antworten auf. GEO macht sichtbar, wo diese Basis trägt und wo nicht.

**Was GEO im MTA-Kontext NICHT ist:**

- **Kein eigener Budgetposten.** Es gibt keine „GEO-Kampagne" mit Mediaspend. Der Skill darf in Output und Report niemals eine eigene Investitionszeile „GEO" suggerieren.
- **Kein eigener Kanal** im Kanal-Mix-Sinn. In `04-02-kanal-chancen-analyse` fließt der GEO-Befund als **Verstärker auf die Achsen von SEO und Content** ein — er begründet, warum SEO-/Content-Arbeit zusätzlichen Hebel über die klassische SERP hinaus hat.

Dieser Frame ist in jedem Output-Block durchzuhalten — Frontmatter-Hinweis, Einordnungs-Block im Markdown, `.suggestion`-Block im HTML.

## Engine-Set

| Engine | Slug | Typ | Quellen-Liste? |
|---|---|---|---|
| ChatGPT (OpenAI, Search-Modus) | `chatgpt` | Chat-Assistent mit Web-Suche | teilweise — im Search-Modus mit Quellen, klassisch ohne |
| Google Gemini / AI Overviews | `gemini` | generative Antwort über/in der SERP | ja — verlinkte Quellen in der Overview |
| Perplexity | `perplexity` | Answer-Engine | ja — explizite, nummerierte Quellen-Liste |
| Claude (analog Perplexity) | `claude` | Chat-Assistent / Answer-Engine | teilweise — wenn mit Web-Suche, dann mit Quellen |

**Default-Set:** `chatgpt`, `gemini`, `perplexity`. `claude` ist optional — der Stratege aktiviert es im Schema, wenn Claude-as-Answer-Engine relevant ist. Claude wird dann **analog Perplexity** behandelt: Probe-Logik, Treffer-Erkennung und Quellen-Auswertung identisch zu Perplexity.

**Warum diese drei als Default:** ChatGPT ist die reichweitenstärkste KI-Suche, Google AI Overviews erreichen die klassische-SERP-Nutzer, Perplexity ist der Maßstab für quellenbasierte Answer-Engines. Zusammen decken sie das relevante Spektrum ab.

## Prompt-Probe-Durchführung

Eine **Probe** ist: ein Prompt × eine Engine → eine generative Antwort, die auf Akteurs-Nennungen und zitierte Quellen ausgewertet wird.

### Aufruf-Strategie

Da keine offiziellen API-Zugänge zu den Engines vorausgesetzt werden, läuft die Probe über `WebSearch` und `WebFetch`:

- **`WebSearch`** — moderne Suchmaschinen geben generative Antwort-Snippets (Google AI Overviews, KI-Zusammenfassungen) direkt aus. Eine `WebSearch` auf den Prompt-Text liefert für die Engine `gemini` häufig die AI-Overview direkt. Für `chatgpt` / `perplexity` liefert `WebSearch` Annäherungen über die jeweiligen öffentlich indexierten Antwort-/Thread-Seiten.
- **`WebFetch`** — für Answer-Engines mit öffentlich erreichbaren Ergebnisseiten (Perplexity-Shared-Threads, öffentliche Antwort-URLs) den konkreten Antwort-Inhalt samt Quellen-Liste abrufen.

Engine-spezifische Hinweise:

| Engine | Probe-Weg |
|---|---|
| `gemini` | `WebSearch` auf den Prompt — die AI-Overview erscheint im Such-Ergebnis. Verlinkte Quellen aus der Overview extrahieren. |
| `perplexity` | Prompt gegen die öffentlich erreichbare Perplexity-Antwortseite stellen (`WebFetch`), nummerierte Quellen-Liste auslesen. |
| `chatgpt` | `WebSearch`/`WebFetch` auf öffentlich indexierte ChatGPT-Antwort-/Shared-Conversation-Inhalte und vergleichbare KI-Zusammenfassungen. Wenn keine Quellen-Liste erreichbar → nur `genannt` auswertbar. |
| `claude` | analog `perplexity` — wenn mit Web-Suche, Quellen-Liste auswerten. |

**Wichtig:** KI-Antworten sind **nicht-deterministisch und personalisiert**. Eine Probe ist eine **Stichprobe**, kein Messwert. Das ist der Grund für die durchgängige `konfidenz: niedrig`-Kennzeichnung. Wenn der Stratege im Schema `probe_wiederholungen: N` setzt (Default 1), probt der Skill jeden Prompt N-mal und nimmt den **Mehrheits-Befund** pro Akteur — das reduziert die Stichproben-Unschärfe, hebt die Konfidenz aber nicht auf `hoch`.

### Was pro Probe extrahiert wird

1. **Antwort-Text** — die generative Antwort, gekürzt auf max. 1.000 Zeichen für den Roh-Cache.
2. **Zitierte Quellen** — Liste von Domains/URLs, die die Engine als Beleg ausweist. Bei Answer-Engines explizit; bei ChatGPT/Gemini aus den verlinkten Quellen der Antwort.
3. **Probe-Status** — `ok` oder `probe_fehlgeschlagen` (keine generative Antwort erreichbar).

### Roh-Cache

Pro Probe ein File: `~/.cache/reachx-mta/<slug>/raw/geo-probe-<engine>-<prompt_id>.json` — unverändert das, was aus WebSearch/WebFetch kam (Antwort-Text, Quellen, Timestamp). Am Skill-Ende gzip-komprimiert nach Drive `assets/raw/`. Begründung: bei Methodik-Anpassungen kann re-ausgewertet werden, ohne erneut zu proben.

## Treffer-Erkennung

Pro Probe wird für **jeden Akteur** ein `sichtbar`-Befund abgeleitet.

### Nennung im Antwort-Text (`genannt`)

- Match des Marken-Namens **und aller Synonyme/Schreibvarianten** aus dem Schema gegen den Antwort-Text.
- **Wort-Grenzen-Match, case-insensitive** — keine Substring-Matches (sonst matcht „Strom" in „Stromversorgung").
- Schreibvarianten abdecken: mit/ohne Rechtsform-Suffix (GmbH, AG), mit/ohne Bindestrich, Domain-Stamm als zusätzlicher Term (z. B. `aufmaster` aus `aufmaster.de`).
- `position_in_antwort`: grobe Einordnung — `prominent` (in den ersten ~25 % der Antwort oder explizit empfohlen), `erwähnt` (irgendwo im Mittelteil), `randständig` (Aufzählung am Ende). Hilft dem Strategen, „genannt" von „als Top-Empfehlung genannt" zu unterscheiden.

### Zitation als Quelle (`zitiert`)

- Match der Akteurs-**Domain** (normalisiert: ohne `www.`, ohne Protokoll, lowercase) gegen die Host-Namen der zitierten Quellen-URLs.
- Subdomain-Toleranz: `blog.kunde.de` zählt als Zitation der Domain `kunde.de`.

### Aggregat-Befund pro Akteur × Probe

| Befund | Bedingung |
|---|---|
| `genannt_und_zitiert` | Name im Text **und** Domain in Quellen |
| `genannt` | nur Name im Text |
| `zitiert` | nur Domain in Quellen |
| `nicht_sichtbar` | weder noch |

`sichtbar` (boolesch in der CSV) ist `true` für die ersten drei, `false` für `nicht_sichtbar`.

### Common-Word-Kollision

Wenn der Marken-Name ein gängiges Wort ist (vom Strategen im Schema markiert oder vom Skill erkannt), wird der Match verschärft: Treffer zählt nur, wenn der Name **zusammen mit einem Branchen-Token** im selben Satz steht (z. B. „Boost" + „Marketing"). Auffälligkeit `marken_name_kollidiert` vergeben.

## Quellen-Typ-Klassifikation

Jede zitierte Domain bekommt im Quellen-Ökosystem (`audits/geo-sichtbarkeit-quellen.csv`) genau einen Typ:

| Typ | Heuristik |
|---|---|
| `eigene_site` | Domain = Domain eines Akteurs (Kunde oder WB) — Abgleich gegen das Akteur-Set. Vorrang vor allen anderen Typen. |
| `branchenportal` | Bewertungs-/Verzeichnis-Plattform. Abgleich mit `wettbewerber/portale.md` (falls `02-04` gelaufen) und mit bekannten Portal-Domains (Jameda, ProvenExpert, Trustpilot, G2, Capterra, OMR Reviews, wlw.de, ImmoScout24, MyHammer etc.). |
| `community` | Reddit, Foren, Q&A-Plattformen (`reddit.com`, `quora.com`, `gutefrage.net`, branchenspezifische Foren). |
| `fachmedium` | Redaktionelle Branchen-Medien, Fach-Magazine, Verlagsseiten. Heuristik: Nachrichten-/Redaktions-Struktur, kein Akteur, kein Portal. |
| `wissensplattform` | Wikipedia, Wikis, Hersteller-Dokumentation, Norm-/Standard-Seiten. |
| `sonstige` | nichts davon eindeutig. |

`gehoert_akteur`: gesetzt auf den Akteurs-Slug, wenn die Domain einem Akteur gehört (immer zusammen mit Typ `eigene_site`), sonst `null`.

**Warum das Quellen-Ökosystem zentral ist:** Es zeigt dem Strategen, **wo** der Kunde präsent sein muss, damit die Engines ihn als Quelle heranziehen. Wenn die Engines zur Branche überwiegend Reddit und ein bestimmtes Portal zitieren, ist Präsenz dort der wirksamste GEO-Hebel — wirksamer als reine Onpage-Optimierung der eigenen Seite.

## GEO-Hebel-Katalog

Die Hebel, die der Skill in der Empfehlung (Schritt 11, Body-Block 7) heranzieht. Alle sind **SEO-/Content-/Reputations-verankert** — keiner ist ein eigener Budgetposten.

| Hebel | Wirkungsweise | Verankert in |
|---|---|---|
| **FAQ-/Entity-Schema** | Strukturierte Daten (FAQPage, Organization, Product) machen Inhalte für Engines maschinenlesbar und entity-fähig — die Engines erkennen die Marke als Entität. | SEO / Web-Tech |
| **Long-Form-Content mit Preistransparenz** | Engines bevorzugen umfassende, konkrete Inhalte mit echten Zahlen (Preise, Maße, Prozesse). Vage Marketing-Seiten werden seltener zitiert. | Content |
| **Quell-Präsenz auf zitierten Plattformen** | Präsenz genau dort, wo die Engines für die Branche Quellen ziehen (Branchenportale, Reddit, Fachmedien) — abgeleitet aus dem Quellen-Ökosystem dieses Audits. | Branchenportal-Recherche / Reddit / PR |
| **Konsistente Entity-Signale (NAP, Wikidata, Profile)** | Einheitliche Marken-Daten über alle Plattformen stärken die Entity-Erkennung der Engines. | Local-SEO / Reputations-Management |
| **Vergleichs- und Bestenlisten-Content** | Engines zitieren bei kommerziellen Prompts gern Vergleichsinhalte — eigene neutrale Vergleichs-/Ratgeber-Seiten erhöhen die Zitations-Chance. | Content / SEO |

Die Hebel-Empfehlung priorisiert nach dem konkreten Befund: Ist die eigene Site nie zitiert → FAQ-/Entity-Schema + Long-Form zuerst. Ist das Ökosystem portallastig → Quell-Präsenz auf den Portalen zuerst.

## Konfidenz-Disziplin

Nach `contracts.md` Abschnitt 13:

- **Qualitative Probe-Werte** sind `erhoben` (echt aus dem Tool gemessen), aber tragen durchgängig `methode: qualitative_probe` und `konfidenz: niedrig` — weil sie Stichproben aus nicht-deterministischen Systemen sind. Eine `sichtbarkeits_quote` ist ein **Indikator**, keine belastbare Quote — nie ohne Konfidenz-Hinweis darstellen.
- **Brand-Radar-Werte** (Voll-Quantitativ-Modus) sind `erhoben` mit `konfidenz: mittel` bis `hoch` — echte Aggregat-Messung. Sie werden **getrennt** ausgewiesen, nicht mit den Probe-Werten verrechnet.
- Eine load-bearing Aussage (z. B. „Kunde ist in KI-Suche unsichtbar") wird im Output explizit als Stichproben-basiert markiert, damit der Stratege sie im Kundengespräch richtig einordnet.

## Zu pflegende Felder

Diese Datei aktualisieren, wenn:

- Eine neue relevante Engine dazukommt oder eine abgekündigt wird → Engine-Set
- Sich der Probe-Weg ändert (neue WebSearch-Fähigkeiten, offizielle APIs verfügbar) → Aufruf-Strategie
- Neue bekannte Portal-/Community-Domains für die Quellen-Klassifikation → Quellen-Typ-Klassifikation
- Sich der GEO-Hebel-Katalog durch neue Best Practices erweitert → GEO-Hebel-Katalog
