# Output-Schema — 03-21-sea-first-party-meta-ads

MTA-Variante des Meta-Ads-Audit-Outputs. Die Audit-Methodik selbst steht in
`meta-ads-audit-methodik.md` (plugin-übergreifend identisch mit dem Standalone-Skill
`meta-ads-account-check`). Diese Datei legt fest, wie die Outputs in den MTA-Kontext
(Drive, `contracts.md`, Report-Bausteine) eingebettet werden.

| Datei (Drive-relativ) | Zweck |
|---|---|
| `audits/meta-ads-first-party.md` | Aggregat mit Frontmatter, Modul-Befunde, Findings |
| `audits/meta-ads-first-party-kampagnen.csv` | Kampagnen-Rohdaten (12 M + 30 T) |
| `reports/05d-meta-ads-first-party.html` | HTML-Report (Erkenntnis-Schicht) |

**Abgrenzung zu `03-06-sea-meta-ads-library-check`:** Jener Skill schreibt
`audits/meta-ads.md` (öffentliche Ad-Library-Sicht der Wettbewerber). Dieser Skill
schreibt `audits/meta-ads-first-party.md` (echtes Kundenkonto von innen). Verschiedene
Dateinamen — kein Konflikt.

---

## 1. Markdown — `audits/meta-ads-first-party.md`

### YAML-Frontmatter

```yaml
---
generiert_am: 2026-05-22T11:00:00Z
skill: 03-21-sea-first-party-meta-ads
schema_version: "2.2"
quelle:
  ad_account_id: "123456789"
  ad_account_name: "Musterkunde GmbH"
  business_name: "Musterkunde GmbH"
  waehrung: "EUR"
  konto_status: aktiv               # aktiv | eingeschraenkt | inaktiv
  abgefragt_am: 2026-05-22
zeitraum:
  lang_von: 2025-05-22
  lang_bis: 2026-05-22
  kurz_von: 2026-04-22
  kurz_bis: 2026-05-22
gesamt_ampel: gelb                  # gruen | gelb | rot
datenqualitaet_vorbehalt: true      # true wenn Modul 4 rot
conversion_setup_urteil: kein_tracking   # sauber | mit_einschraenkung | kein_tracking
modul_ampeln:
  m1_account_health: gruen
  m2_performance: gelb
  m3_struktur: gelb
  m4_tracking: rot
  m5_creatives: gruen
kennzahlen_12m:                     # alle Werte quelle: erhoben
  spend: 84200.00
  impressions: 4210000
  reach: 980000
  clicks: 63100
  ctr: 0.015
  cpc: 1.33
  cpm: 20.00
  results: 1820
  cost_per_result: 46.26
  purchase_value: 198400.00
  roas: 2.36
kennzahlen_30t:
  spend: 6100.00
  results: 95
  cost_per_result: 64.21
  roas: 1.71
opportunity_score: 58               # quelle: erhoben (Meta)
auffaelligkeiten:
  - typ: kein_conversion_tracking
    titel: "Conversions-API nicht angebunden"
    relevanz: hoch
datenluecken:                       # Reduced-Modus — leer lassen, wenn alles erhoben
  - "ads_get_datasets / dataset_quality / dataset_stats — für dieses Konto nicht ausgerollt"
  - "clicks / ctr / cpc / purchase_roas — vom MCP durchgängig 'Not available'"
---
```

- Geld-Werte unverändert aus dem MCP (Konto-Währung). `roas` / `cost_per_result`
  leer lassen, wenn der Nenner 0 ist oder die Metrik `Not available` war — nie `0`.
- `datenluecken` listet jedes für das Konto nicht ausgerollte Tool und jede
  `Not available`-Metrik (Reduced-Modus, `meta-ads-mcp-nutzung.md` Abschnitt 9);
  ist nichts betroffen, das Feld weglassen.
- **Quellen-Kennzeichnung (`contracts.md` §13):** Performance-Kennzahlen sind
  `erhoben`. Der `opportunity_score` ist `erhoben` (Meta-eigene Metrik). Branchen-
  Benchmark-Werte sind `benchmark`. Heuristische Einschätzungen (z. B. Ampel-Urteil)
  sind `schaetzung_skill` — im Body so kennzeichnen.
- `conversion_setup_urteil` ist das Pendant zum Conversion-Check in `03-17` und
  verankert den Datenqualitäts-Vorbehalt für `04-02`/`04-04`.

### Body-Struktur

1. **Übersicht** — 4–6 Sätze: welches Konto, Spend-Größenordnung, Gesamt-Ampel,
   Datenqualitäts-Vorbehalt, größte Hebel.
2. **Modul-Ampeln** — Tabelle M1–M5.
3. **M1–M5** — je ein Abschnitt mit Befunden (Account-Health, Performance-Verlauf,
   Struktur, Tracking, Creatives).
4. **Findings & Empfehlungen** — Auffälligkeiten nach Relevanz, Quick-Wins vs.
   strukturell, Top-3-Hebel.
5. **Lücken und Hinweise** — Datenbasis dünn? Konto inaktiv? `is_queryable=false`?

---

## 2. CSV — `audits/meta-ads-first-party-kampagnen.csv`

Eine Zeile je Kampagne × Zeitraum. UTF-8, Komma-getrennt, Header.

```
ad_account_id,campaign_id,campaign_name,status,objective,zeitraum,datum_von,datum_bis,spend,waehrung,impressions,reach,frequency,clicks,ctr,cpc,cpm,results,cost_per_result,purchase_value,roas
```

`zeitraum` ∈ {`12m`, `30t`}. Leere Zelle (nicht `0`) bei Nenner 0. Header und
Semantik nicht ohne Versions-Bump ändern — die CSV ist Datenbasis für
`04-02-kanal-chancen-analyse` (Paid-Social-Hebel) und `04-04-forecast-modell`
(echte CR-/CPA-Werte statt Branchen-Annahmen).

---

## 3. HTML-Report — `reports/05d-meta-ads-first-party.html`

Folgt `contracts.md` Abschnitt 7 vollständig:

- Aus `reports/_shell.html` (Drive) bauen, `<style>`-Block unverändert.
- `{{MAIN_CONTENT}}` **ausschließlich** aus den Bausteinen in
  `01-01-mta-projekt-init/reference/report-bausteine.md` — Markup 1:1, keine eigenen
  CSS-Klassen, kein inline-`style`.
- Vor dem Upload validieren:
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <html> --shell` —
  Exit 0 → hochladen, Exit 1 → korrigieren.

### Report-Nummer

`05d` — der First-Party-Block ist: `05a` GSC (`03-04`), `05b` GA4 (`03-18`),
`05c` SEA-Google (`03-17`), **`05d` SEA-Meta (dieser Skill)**. Damit stehen die
vier First-Party-Audits im Dashboard zusammen vor den Third-Party-Audits.

### Platzhalter

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | `Meta-Ads First-Party · KUNDE` |
| `{{EYEBROW}}` | `MTA-Audit · SEA First-Party` |
| `{{DISPLAY_NAME}}` | `Meta-Ads First-Party-Audit: KUNDE` |
| `{{META_LINE}}` | `Quelle: Meta-Ads-MCP (First-Party) · Konto: <name> (<id>) · Zeitraum: 12 Monate · Generiert: <heute>` |
| `{{MAIN_CONTENT}}` | siehe unten |
| `{{TOKEN_BREAKDOWN}}` | leer lassen (nur Dashboard) |
| `{{TOKEN_FOOTER}}` | Skill-Counter (siehe SKILL.md, Token-Tracking) |
| `{{FOOTER_TEXT}}` | `MTA · KUNDE · Meta-Ads First-Party-Audit` |

### `{{MAIN_CONTENT}}` — Aufbau aus kanonischen Bausteinen

- **Stat-Strip** oben: Spend/12M, ROAS, Cost-per-Result, Opportunity Score,
  30-Tage-Spend-Trend.
- **Conversion-Setup-Urteil** prominent als `.summary-card` direkt darunter — Badge
  (`stark` = sauber, `mittel` = mit Einschränkung, `schwach` = kein Tracking) plus
  ein bis zwei Sätze. Das ist der Vertrauens-Disclaimer für alle ROAS-Zahlen.
- **Sticky-TOC**: Account-Health, Performance, Struktur, Tracking, Creatives, Findings.
- **Modul-Ampeln**: als `details.dim`-Karten mit `data-rating` (`stark`/`mittel`/
  `schwach`) — eine je Modul M1–M5, jeweils mit `.badge`.
- **Performance**: `table.data` (12 Monate vs. 30 Tage), Top-Kampagnen mit ROAS-Badge.
- **Struktur**: Kampagnen-`table.data`, Budget-Verteilung als kleine Balken (aus dem
  `report-bausteine.md`-Inventar — keine eigene Balken-Klasse erfinden).
- **Findings**: `.suggestion`-Blöcke nach Relevanz, Top-3-Hebel als `ol.top3`.

`<body>` ohne Klasse → Back-Link zum Dashboard sichtbar (`contracts.md` §7).

> Hinweis: Die Mini-Balken/`ampel-grid`-Bausteine des Standalone-Skills existieren
> im MTA-Shell-CSS **nicht**. Im MTA-Kontext ausschließlich die in
> `report-bausteine.md` dokumentierten Klassen verwenden — der Validator schlägt
> sonst an.

---

## 4. Dashboard- und status.md-Update

- `reports/index.html`: Stat-Strip um Meta-Spend/12M und ROAS ergänzen,
  `03-21-sea-first-party-meta-ads` in die Erledigt-Liste, `05d`-Report verlinken.
- `status.md` nach `contracts.md` §3. Bei `conversion_tracking_fehlt` oder
  `roas_unter_eins`: Hinweis „in MTA-Story als Schwerpunkt einplanen".
