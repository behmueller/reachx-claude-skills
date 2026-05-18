# Ahrefs-Brand-Radar-Nutzung

Wie der `03-19-geo-ki-sichtbarkeit`-Skill die Ahrefs-Brand-Radar-Tools für ein **quantitatives** KI-Sichtbarkeits-Maß nutzt — und warum Brand Radar **optional** ist. Aus dem SKILL.md Schritt 1 und Schritt 6 verwiesen.

**Stand:** Mai 2026

## Brand Radar ist OPTIONAL — kein Pflicht-MCP

Ahrefs Brand Radar ist ein eigenes Produkt-Modul, das **nicht in jedem Ahrefs-Abo enthalten ist** — es muss separat gebucht sein. Der Skill behandelt Brand Radar deshalb nach der **Optional-MCP-Logik** aus `contracts.md` Abschnitt 11:

- **Vorhanden und im Abo** → der Skill läuft im **Voll-Quantitativ-Modus**: qualitative Prompt-Probes **plus** Brand-Radar-Aggregate.
- **Nicht vorhanden / nicht im Abo** → der Skill läuft im **Qualitativ-Modus**: nur die Prompt-Probes, sauber mit `konfidenz: niedrig` und `methode: qualitative_probe` gekennzeichnet. **Kein Abbruch.**

Brand Radar ist nie der Grund für einen Skill-Abbruch. Pflicht-Tools sind ausschließlich `WebSearch` / `WebFetch` (für die qualitativen Probes).

## Verfügbarkeits-Check (Schritt 1)

Zwei-stufiger Check, bevor der Voll-Quantitativ-Modus angenommen wird:

### Stufe 1 — MCP erreichbar?

Billiger, kostenloser Test-Call:

```
mcp__claude_ai_Ahrefs__subscription-info-limits-and-usage
```

Dieser Call verbraucht keine API-Units. Schlägt er fehl (MCP nicht verbunden) → Brand Radar gilt als `nicht_verfuegbar`, Qualitativ-Modus.

### Stufe 2 — Brand Radar im Abo?

Auch wenn die Ahrefs-MCP erreichbar ist, kann das Brand-Radar-Modul fehlen. Prüfen:

1. Ist mindestens ein `brand-radar-*`-Tool in der Tool-Liste aufgeführt? (Tool-Namen siehe unten.)
2. Ein minimaler Test-Call auf `brand-radar-mentions-overview-entities` mit Minimal-Parametern. Bricht er mit einer Meldung wie „not in subscription", „plan does not include", „feature not available" o. ä. ab → Brand Radar gilt als `nicht_verfuegbar`.

Nur wenn **beide** Stufen positiv sind → `brand_radar: verfuegbar`, Voll-Quantitativ-Modus. Andernfalls `brand_radar: nicht_verfuegbar`, Qualitativ-Modus.

Das Ergebnis wird im Schema (Phase A) und im Aggregat-Frontmatter (Phase B) als `brand_radar: verfuegbar | nicht_verfuegbar` festgehalten.

## Doc-Tool zuerst

Vor dem ersten echten Aufruf eines Brand-Radar-Tools **immer** das Ahrefs-`doc`-Tool nutzen, um das aktuelle Input-Schema zu holen:

```
mcp__claude_ai_Ahrefs__doc  →  tool: "brand-radar-mentions-overview"
```

Die Ahrefs-MCP weist explizit darauf hin: `doc` zuerst aufrufen, sonst sind die Parameter geraten. Das gilt für jedes hier genannte Tool.

## Tool-Mapping pro Auswertungs-Schritt

Brand Radar arbeitet mit einem KI-Datensatz (`data_source` benennt die KI-Engine) und mit `brand` / `competitors` als Entitäten. Die `*-entities`-Varianten der Tools haben die beschreibenderen Inputs — laut MCP-Hinweis bevorzugt nutzen.

### Mentions — wie oft die Marke in KI-Antworten erwähnt wird

| Tool | Zweck |
|---|---|
| `brand-radar-mentions-overview-entities` | Mentions-Aggregat pro Akteur — die Kernzahl: wie oft taucht die Marke in KI-Antworten auf. Bevorzugt vor `brand-radar-mentions-overview`. |
| `brand-radar-mentions-history-entities` | Mentions-Verlauf über die Zeit — für eine Trend-Sparkline im Report. |

### Share of Voice — Anteil des Kunden gegenüber Wettbewerbern

| Tool | Zweck |
|---|---|
| `brand-radar-sov-overview-entities` | Share-of-Voice-Aggregat — Anteil des Kunden an allen Marken-Mentions im Wettbewerbsumfeld. |
| `brand-radar-sov-history-entities` | SoV-Verlauf über die Zeit. |

### Cited Domains — welche Domains die Engines zitieren

| Tool | Zweck |
|---|---|
| `brand-radar-cited-domains-entities` | Domains, die die KI-Engines als Quelle zitieren — **ergänzt** das qualitativ erhobene Quellen-Ökosystem (SKILL.md Schritt 7) um eine quantitative Lesart. |
| `brand-radar-cited-pages-entities` | konkrete zitierte Seiten — optional, für die Tiefe. |

### AI Responses — die konkreten KI-Antworten

| Tool | Zweck |
|---|---|
| `brand-radar-ai-responses-entities` | Sample echter KI-Antworten, in denen Marken auftauchen — optional, als Beleg-Material neben den eigenen Probes. |

### Impressions / Reports / Prompts

| Tool | Zweck |
|---|---|
| `brand-radar-impressions-overview-entities` | geschätzte Impressionen der Marke in KI-Suche — optionale Zusatz-Lesart. |
| `management-brand-radar-reports` | listet vorhandene Brand-Radar-Reports im Ahrefs-Account — wenn der Kunde bereits einen Report angelegt hat, kann dessen `report_id` als Parameter genutzt werden. |
| `management-brand-radar-prompts` | listet die Prompts eines bestehenden Brand-Radar-Reports — kann das Phase-A-Prompt-Inventar inspirieren. |

## Parameter-Konventionen

- **`data_source`** — benennt die KI-Engine des Datensatzes. Pro relevanter Engine einen Aufruf, damit der Engine-Vergleich (SKILL.md Schritt 11, Block 4) auch quantitativ gestützt ist.
- **`brand`** — der Kunde (Marken-Name aus dem Akteur-Set).
- **`competitors`** — die Wettbewerber aus dem bestätigten Akteur-Set.
- **`country` / `market`** — Region aus `meta.json` (Default DACH/`de`).
- **`select`** — nur die benötigten Felder anfordern (Units sparen).
- **`report_id`** — falls `management-brand-radar-reports` einen passenden bestehenden Report liefert, dessen ID nutzen statt einen Ad-hoc-Lauf.

Monetäre Werte liefert die Ahrefs-API in **USD-Cent** — für GEO-Mentions/SoV in der Regel irrelevant, aber falls ein Kosten-Feld ausgewertet wird: durch 100 teilen.

## Einordnung der Brand-Radar-Werte im Output

- Brand-Radar-Werte sind `erhoben` mit `konfidenz: mittel` bis `hoch` — echte Aggregat-Messung, **keine** Stichprobe.
- Sie werden im Aggregat-Markdown und im HTML-Report **getrennt** von den qualitativen Probe-Werten ausgewiesen — eigener Block, eigene Spalten. **Nicht** mit den Probe-Quoten verrechnet oder zu einem Mischwert verdichtet (analog zur SI-vs-DR-Disziplin in `03-01`).
- Brand Radar ersetzt die Probes nicht: Die Probes zeigen **konkrete Antworten auf konkrete Prompts** (qualitativ greifbar für den Strategen), Brand Radar zeigt **Aggregat-Volumen** (belastbarer, aber abstrakt). Beide Lesarten stehen nebeneinander.
- Wenn Brand Radar im Abo ist, aber für die Branche **0 Daten** liefert (Nischen-Branchen sind oft nicht abgedeckt): `brand_radar_daten: leer` im Frontmatter, Befund stützt sich auf die Probes — kein Fehler.

## Fehler-Handling

| Fehler | Verhalten |
|---|---|
| Ahrefs-MCP nicht verbunden | `brand_radar: nicht_verfuegbar`, Qualitativ-Modus, Hinweis im Schluss-Format |
| `brand-radar-*`-Tools nicht in Tool-Liste | `brand_radar: nicht_verfuegbar`, Qualitativ-Modus |
| Test-Call meldet „not in subscription" | `brand_radar: nicht_verfuegbar`, Qualitativ-Modus |
| Brand-Radar-Fehler mitten im Lauf (Abo abgelaufen, Rate-Limit) | Brand-Radar-Teil sauber abbrechen, mit Qualitativ-Modus weiterlaufen, bereits erhobene Brand-Radar-Daten behalten, Hinweis im Schluss-Format |
| Brand Radar liefert 0 Daten für die Branche | `brand_radar_daten: leer`, kein Fehler, Befund aus Probes |
| Ahrefs-Unit-Budget niedrig | Warnung im Schluss-Format, Brand-Radar-Aufrufe auf das Nötigste begrenzen (`select` minimal halten) |

## Zu pflegende Felder

Diese Datei aktualisieren, wenn:

- Ahrefs die Brand-Radar-Tool-Namen ändert oder neue Tools hinzufügt → Tool-Mapping
- Sich der Abo-Verfügbarkeits-Check ändert (neuer Fehler-Wortlaut) → Verfügbarkeits-Check
- Neue relevante `data_source`-Werte (KI-Engines) dazukommen → Parameter-Konventionen
