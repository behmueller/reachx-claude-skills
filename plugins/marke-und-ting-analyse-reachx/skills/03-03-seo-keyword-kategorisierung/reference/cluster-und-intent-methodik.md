# Cluster-Bildung, Intent-Typen und Funnel-Stufen — Methodik

Die fachliche Grundlage für die drei Kategorisierungs-Dimensionen. Diese Datei beschreibt **was** wir entlang welcher Achse erfassen und **warum** — die genauen Implementierungs-Regeln stehen im SKILL.md und im Schema-Template.

## 1. Cluster

### Was ist ein Cluster?

Ein Cluster ist eine **thematische Bündelung von Keywords**, die für die Strategie zusammen betrachtet werden sollen. Beispiel: 14 Keywords um das Thema "Aufmaß und Werkzeuge" bilden einen Cluster, weil sie zusammen einen Content- oder Landingpage-Bereich rechtfertigen würden.

Cluster sind **kuratiert**, nicht rein algorithmisch. Algorithmen können Cluster vorschlagen (Token-Frequenz, Ahrefs-Parent-Topics, Co-Occurrence), aber der Stratege gestaltet sie im Schema-Review. Begründung: was strategisch ein Cluster ist, hängt von Markenkommunikation, Portfolio-Schnitt und MTA-Story ab — Algorithmen können das nicht entscheiden.

### Cluster-Typen

Im Schema unterscheiden wir folgende Cluster-Typen (`typ`-Feld):

| Typ | Bedeutung | Beispiel |
|---|---|---|
| `branded` | Marken-Synonyme (Kunde oder WB) | `branded_kunde`, `branded_beta_solutions` |
| `produkt` | Eine Produkt-/Dienstleistungs-Kategorie aus dem Portfolio | `kabel_werkzeuge`, `messer_werkzeuge` |
| `anwendung` | Ein Anwendungsfall, der mehrere Produkte umfasst | `aufmass_workflow`, `smart_home_integration` |
| `gap_cluster` | Ein in `seo-keyword-pool.md` als Auffälligkeit identifizierter Gap-Cluster | `gap_verlegung` |
| `longtail` | Long-Tail-Bucket pro Themen-Stamm — eher als Sammelbecken für niedrigvolumige Variationen | `longtail_aufmass` |
| `generic` | Sammelbecken für Keywords ohne klare Zuordnung | `generic` (immer genau einer) |
| `fallback` | Reserve, nur eine Instanz: `generic`-Cluster | — |

### Cluster-Qualitäts-Kriterien (für den Strategen-Review)

Gute Cluster sind:

1. **Strategisch erzählbar** — würde man auf einer MTA-Slide stehen sehen
2. **Ausreichend groß** — mindestens 5 Keywords (Ausnahme: Branded-Cluster können kleiner sein)
3. **Ausreichend klein** — nicht über 50 Keywords (sonst eigentlich mehrere Cluster)
4. **Eindeutig benennbar** — der Name kommuniziert das Thema in 1-3 Wörtern
5. **Mit klaren Anker-Tokens** — mindestens 2-3 Tokens, die das Thema sicher matchen
6. **Inhaltlich kohärent** — wenn ein Stratege die Top-5 Keywords liest, erkennt er die Verbindung

Schlechte Cluster:

- Mischen mehrere Themen ("Werkzeuge und Software")
- Sind zu generisch ("Allgemein")
- Haben nur 2-3 Keywords (zu eng definiert)
- Brauchen 10+ Anker-Tokens (zu schwammig)
- Sind reine Wortform-Variation ohne thematische Bedeutung

### Mehrfach-Zugehörigkeit

Ein Keyword kann zu mehreren Clustern gehören:

- `primaer_cluster` (Pflicht) — der "Haupt-Heimathafen" des Keywords
- `sekundaer_cluster` (optional, Liste) — weitere passende Cluster

Beispiel: "aufmaß werkzeug günstig" gehört primär zu `produkt_aufmasswerkzeuge`, sekundär zu `transactional_intent_cluster` (weil "günstig" Kauf-Intent signalisiert).

Regel für die Zuweisung des Primär-Clusters:

- Wenn `branded`-Match → immer `primaer`
- Sonst: längster gematchter Anker-Token gewinnt
- Bei Gleichstand: alphabetischer Cluster-Name als Tiebreaker (für Reproduzierbarkeit)

## 2. Intent-Typen

### Definition

Intent-Typ beschreibt die **Such-Absicht** hinter dem Keyword — was will der Nutzer in dem Moment der Suche?

Wir nutzen **fünf Standard-Intent-Typen** plus `unklar`:

### branded

**Definition**: Der Nutzer sucht nach einer konkreten Marke (Kunde oder Wettbewerber).

**Trigger**: nicht Token-basiert, sondern Cluster-Typ-basiert (`cluster.typ: branded`). Keine eigenen Trigger-Tokens, weil Marken-Namen so spezifisch sind, dass sie über die Cluster-Zuordnung geregelt werden.

**Funnel-Default**: BOFU — wer eine Marke kennt und sucht, ist in der Regel nah am Kauf.

**Edge Cases**:

- Brand-Search nach Bewertungen ("Marke X Erfahrungen") ist branded + commercial-Aspekt
- Brand-Search nach Alternativen ("alternative zu Marke X") ist branded + commercial — typischer Conquest-Suchpunkt
- Brand-Search vom Kunden für die eigene Marke ist trivial, aber dennoch wichtig (Brand-Equity)

### transactional

**Definition**: Konkrete Kauf-, Buchungs- oder Abschluss-Absicht.

**Standard-Trigger-Token**:

- "kaufen", "preis", "kosten", "bestellen", "shop", "online kaufen"
- "angebot", "rabatt", "günstig", "bestpreis", "deal"
- "buchen", "termin", "termin online"
- "demo buchen", "demo anfordern", "testphase starten"

**Branchen-Anpassungen**:

- B2B-SaaS: "demo", "trial", "termin" sind transactional, nicht commercial
- B2B-Industrie: "angebot anfordern", "katalog" sind transactional
- B2C-Lokal: "in meiner nähe", "öffnungszeiten" können transactional-Hinweise sein
- Medizin / Recht: "termin", "sprechstunde" sind transactional

**Funnel-Default**: BOFU.

### commercial

**Definition**: Vergleichende oder evaluierende Suche **vor** dem Kauf.

**Standard-Trigger-Token**:

- "test", "vergleich", "vs", "oder"
- "erfahrungen", "bewertung", "rezension", "review"
- "beste", "top", "ranking", "rangliste"
- "alternativen zu", "ersatz für", "ähnlich wie"
- "lohnt sich", "ist x gut"

**Branchen-Anpassungen**:

- Bei Lifestyle / B2C-Produkten ist `test`-Pattern stärker mit informational verwoben (Tutorial-Tests)
- Bei B2B-Software ist `vs`-Pattern sehr explizit commercial

**Funnel-Default**: MOFU.

### informational

**Definition**: Wissens-, Lern-, oder Recherche-Absicht ohne unmittelbare Kauf-Nähe.

**Standard-Trigger-Token**:

- W-Fragen: "was ist", "wie funktioniert", "wann", "wo", "warum", "wer"
- "anleitung", "tutorial", "guide", "tipps", "tricks"
- "definition", "erklärt", "erklärung"
- "vorteile", "nachteile" (außer in Kombi mit Marke → eher commercial)
- "selber machen", "selbst", "diy"

**Branchen-Anpassungen**:

- Bei Lifestyle / B2C: How-to-Pattern besonders relevant
- Bei B2B / Tech: "best practices", "use case" sind informational
- Bei Health: "symptome", "ursachen" sind informational

**Funnel-Default**: TOFU.

### navigational

**Definition**: Suche nach einer konkreten Marke / URL ohne Kauf-Signal — oft sehr kurze Keywords.

**Standard-Trigger**:

- Sehr kurze Keywords (1-2 Tokens)
- Kein Kauf-Signal, kein Vergleich-Signal, kein W-Fragen-Pattern
- Oft Marken-Synonyme oder Marken-Variationen

**Hinweis**: navigational ist häufig **mit** branded überlappend. Im Skill-Schema wird empfohlen, navigational nur dann als eigenen Intent zu vergeben, wenn der Cluster nicht branded ist (z. B. ein Nutzer sucht "haftpflicht versicherung" ohne Marke — generic navigational).

**Funnel-Default**: BOFU (wenn die Marke schon gewusst wird) oder MOFU (wenn nur die Kategorie gemeint ist).

### unklar

**Definition**: Keine eindeutige Intent-Zuordnung möglich.

**Fallback** für Keywords, die keinem der obigen Trigger-Patterns folgen und auch nicht branded sind. Sollte unter 10% des Pools bleiben — wenn größer, ist das Schema zu eng (Auffälligkeit in Phase B).

**Funnel-Default**: TOFU (konservativ).

## 3. Funnel-Stufen

### Was ist die Funnel-Stufe?

Beschreibt die **Position des Nutzers in der Kauf-Reise**:

| Stufe | Bedeutung | Typische Aktivität |
|---|---|---|
| **TOFU** (Top of Funnel) | Awareness, Problem-Erkundung | Recherchiert, lernt, entdeckt das Problem |
| **MOFU** (Middle of Funnel) | Consideration, Lösungs-Suche | Vergleicht Optionen, bewertet Lösungen |
| **BOFU** (Bottom of Funnel) | Decision, Kauf-Vorbereitung | Will jetzt kaufen / buchen / kontaktieren |

### Funnel vs. Intent

Funnel und Intent sind **ergänzende Achsen**, aber nicht identisch:

- Intent beschreibt die konkrete Such-Absicht ("was tut der Nutzer in diesem Moment")
- Funnel beschreibt die Kauf-Reise-Stufe ("wie weit ist der Nutzer auf dem Weg zur Entscheidung")

Beispiel: "was ist crm" (informational, TOFU) und "crm vs erp" (commercial, MOFU) sind unterschiedliche Funnel-Stufen mit unterschiedlichen Intents — Standard-Fall.

Aber: "preise für hausverwaltung berlin" (transactional, BOFU) und "preise für hausverwaltung im vergleich" (commercial, MOFU) — der Funnel verschiebt sich, obwohl beide um "Preise" gehen.

**Im Skill**: Default-Mapping Intent → Funnel (siehe Schema-Template), Cluster-Overrides bei Bedarf. Das Cluster-Schema überschreibt das Intent-Default — z. B. ein "Vergleichs-Cluster" pusht alle Keywords auf MOFU, auch wenn sie informational klingen.

### Funnel-Verteilung als Qualitäts-Indikator

Eine gesunde Pool-Funnel-Verteilung sieht je nach Branche unterschiedlich aus:

| Branchen-Typ | Typische Verteilung |
|---|---|
| Content-Publisher | 70% TOFU, 20% MOFU, 10% BOFU |
| B2C-E-Commerce | 30% TOFU, 30% MOFU, 40% BOFU |
| B2B-SaaS | 40% TOFU, 35% MOFU, 25% BOFU |
| Lokal-Dienstleister | 25% TOFU, 25% MOFU, 50% BOFU |
| B2B-Mittelstand | 50% TOFU, 30% MOFU, 20% BOFU |

Starke Abweichung von diesen Defaults → Hinweis-Block im Output, dass der Funnel-Mix ungewöhnlich ist (möglicher Grund: Pool ist zu informational, oder die Branche hat eine besondere Such-Charakteristik).

## 4. Konfidenz

Pro Keyword wird ein `kategorisierungs_konfidenz`-Wert mitgespeichert:

| Konfidenz | Bedingung |
|---|---|
| `hoch` | Genau ein Cluster-Anker-Token gematcht (eindeutig), oder branded-Match |
| `mittel` | Mehrere Cluster-Anker-Tokens gematcht (Tiebreaker entschied), oder Match über Ahrefs-Parent-Topic |
| `niedrig` | Reiner Fallback zu `generic`, oder weniger als 50% Token-Übereinstimmung mit dem zugewiesenen Cluster |

Konfidenz-Verteilung wird im Skill-Output ausgewertet:

- > 80% hoch + mittel → sehr gute Schema-Qualität
- 60-80% → ausreichend
- < 60% → Schema sollte überarbeitet werden (Auffälligkeit `kategorisierung_unsicher`)

## 5. Verbindung zu Folge-Skills

Die kategorisierten Daten fließen in:

### `04-02-kanal-chancen-analyse`

Liest pro Cluster:

- Cluster-Score (Priorisierungs-Basis)
- Funnel-Verteilung (für Channel-Mix-Empfehlung — TOFU-lastig = Content + SEO, BOFU-lastig = Ads + Conversion-Optimierung)
- Intent-Verteilung (für Channel-Empfehlung — viel transactional = Ads-Kandidaten)
- Kunden-Abdeckung pro Cluster (für Priorisierung — Gaps haben höheren Cluster-Score)

### `04-04-forecast-modell`

Liest:

- Cluster-Score-Top-10 — Annahme: Top-Cluster sind die Forecast-Treiber
- Suchvolumen pro Cluster — Multiplikation mit Konversions-Annahme ergibt Traffic-Forecast
- Difficulty-Verteilung — Annahme: hohe Difficulty = längere Ramp-up-Zeit im Forecast

### `04-05-90-tage-plan`

Liest:

- Sweet-Spot-Cluster (niedrige Difficulty + relevantes Volumen) — werden zu konkreten 90-Tage-Maßnahmen
- Gap-Cluster mit hohem Score — werden zu prioritären Content-Briefings

### `05-01-mta-slide-bausteine`

Liest:

- Aggregat-Markdown (für Slide-Text)
- Top-3-Cluster-Tabelle (für Slide-Tabelle)
- Auffälligkeiten (für die "Erkenntnis"-Slides)
