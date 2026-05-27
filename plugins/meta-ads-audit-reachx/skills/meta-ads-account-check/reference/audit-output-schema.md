# Output-Schema — Markdown, CSV, HTML

Der Skill erzeugt drei Output-Ebenen. Diese Datei legt ihre Struktur fest.

| Datei | Ebene | Zweck |
|---|---|---|
| `meta-ads-audit.md` | Interpretation | Aggregat mit Frontmatter, Modul-Befunde, Findings |
| `meta-ads-kampagnen.csv` | Maschine | Kampagnen-Rohdaten (12 M + 30 T) |
| `meta-ads-audit.html` | Präsentation | REACHX-gebrandeter Report fürs Kundengespräch |

Standard-Ablage lokal: `~/meta-ads-audits/<konto-slug>-<YYYY-MM-DD>/`.
`<konto-slug>` = Kontoname kleingeschrieben, nicht-alphanumerisch durch `-` ersetzt.

---

## 1. Markdown — `meta-ads-audit.md`

### YAML-Frontmatter

```yaml
---
skill: meta-ads-account-check
version: 0.1.0
erstellt_am: 2026-05-22            # Audit-Datum
konto:
  ad_account_id: "123456789"
  ad_account_name: "Musterkunde GmbH"
  business_name: "Musterkunde GmbH"
  waehrung: "EUR"
  konto_status: aktiv               # aktiv | eingeschraenkt | inaktiv
zeitraum:
  lang_von: 2025-05-22
  lang_bis: 2026-05-22
  kurz_von: 2026-04-22
  kurz_bis: 2026-05-22
  abgefragt_am: 2026-05-22
gesamt_ampel: gelb                  # gruen | gelb | rot
datenqualitaet_vorbehalt: true      # true wenn Modul 4 rot
modul_ampeln:
  m1_account_health: gruen
  m2_performance: gelb
  m3_struktur: gelb
  m4_tracking: rot
  m5_creatives: gruen
kennzahlen_12m:
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
opportunity_score: 58
auffaelligkeiten:
  - typ: kein_conversion_tracking
    titel: "Conversions-API nicht angebunden"
    relevanz: hoch
  # … weitere
datenluecken:                       # Reduced-Modus — leer lassen, wenn alles erhoben
  - "ads_get_datasets / dataset_quality / dataset_stats — für dieses Konto nicht ausgerollt"
  - "clicks / ctr / cpc / purchase_roas — vom MCP durchgängig 'Not available'"
---
```

`roas` / `cost_per_result` bleiben leer (kein Wert), wenn der Nenner 0 ist oder die
Metrik `Not available` war — niemals `0` eintragen.
`results` = das jeweils optimierte Ergebnis des Kontos (Käufe / Leads / …).
`datenluecken` listet jedes nicht ausgerollte Tool und jede `Not available`-Metrik
(Reduced-Modus, siehe `meta-ads-mcp-nutzung.md` Abschnitt 9); ist nichts betroffen,
das Feld weglassen oder leer lassen.

### Body-Struktur

1. **Zusammenfassung** — 4–6 Sätze: welches Konto, Spend-Größenordnung, Gesamt-Ampel,
   Datenqualitäts-Vorbehalt (falls zutreffend), wo die größten Hebel liegen.
2. **Modul-Ampeln** — Tabelle M1–M5 mit Urteil + Ein-Satz-Begründung.
3. **M1 — Account-Health** — Opportunity Score, Delivery-Fehler, Konto-Status.
4. **M2 — Performance-Verlauf** — 12-Monats-Kurve, 30-T-vs-12-M, Trend je KPI,
   Branchen-Benchmark.
5. **M3 — Struktur & Setup** — Kampagnen-/Ad-Set-Übersicht, Budget-Verteilung,
   Auction-Overlap, Audience-Setup, Placement-Verteilung.
6. **M4 — Tracking & Datenqualität** — Datasets, EMQ, CAPI-Status, Frische.
   **Der Vertrauens-Disclaimer.**
7. **M5 — Creatives** — Anzahl je Ad Set, Frequency-Lesart, Format-Mix.
8. **Findings & Empfehlungen** — alle Auffälligkeiten nach Relevanz, Quick-Wins vs.
   strukturell getrennt, Top-3-Hebel als nummerierte Liste.
9. **Datenlücken & Vorbehalte** — was nicht erhoben werden konnte, Konto zu neu, etc.

---

## 2. CSV — `meta-ads-kampagnen.csv`

Eine Zeile je Kampagne × Zeitraum. UTF-8, Komma-getrennt, Header-Zeile.

```
ad_account_id,campaign_id,campaign_name,status,objective,zeitraum,datum_von,datum_bis,spend,waehrung,impressions,reach,frequency,clicks,ctr,cpc,cpm,results,cost_per_result,purchase_value,roas
```

- `zeitraum` ∈ {`12m`, `30t`}.
- Leere Zelle (nicht `0`), wenn eine abgeleitete Kennzahl wegen Nenner 0 nicht
  bestimmbar ist.
- Header und Semantik nicht ohne Versions-Bump ändern.

---

## 3. HTML — `meta-ads-audit.html`

Aus `reference/report-shell.html` bauen: Shell lesen, die fünf Platzhalter ersetzen,
Ergebnis schreiben. `{{MAIN_CONTENT}}` **ausschließlich** aus den Bausteinen unten —
keine eigenen CSS-Klassen, kein inline-`style`, der `<style>`-Block bleibt unverändert.

### Platzhalter

| Platzhalter | Inhalt |
|---|---|
| `{{TITLE}}` | `Meta-Ads-Audit · <Kontoname>` |
| `{{EYEBROW}}` | `REACHX · Werbekonto-Audit` |
| `{{DISPLAY_NAME}}` | `Meta-Ads-Audit: <Kontoname>` |
| `{{META_LINE}}` | `Quelle: Meta-Ads-MCP (First-Party) · Konto: <name> (<id>) · Zeitraum: 12 Monate · Erstellt: <datum>` |
| `{{MAIN_CONTENT}}` | Report-Körper aus den Bausteinen |
| `{{FOOTER_TEXT}}` | `REACHX · <Kontoname> · Meta-Ads-Werbekonto-Audit · read-only` |

### Pflicht-Reihenfolge in `{{MAIN_CONTENT}}`

1. Sticky-TOC
2. Stat-Strip (Spend 12 M, ROAS, Cost-per-Result, Opportunity Score, 30-T-Trend)
3. Datenqualitäts-Disclaimer (**nur** wenn `datenqualitaet_vorbehalt: true`)
4. Summary-Card „Kernbefund"
5. Ampel-Grid (M1–M5)
6. Je Modul eine `<section>` mit Befunden
7. Findings-Sektion: Top-3-Hebel (`ol.top3`) + Auffälligkeiten als `.suggestion`-Blöcke

### Bausteine (Copy-Paste-Markup)

**Sticky-TOC**
```html
<nav class="toc" aria-label="Schnellzugriff">
  <strong>Schnellzugriff</strong>
  <a href="#health">Account-Health</a>
  <a href="#performance">Performance</a>
  <a href="#struktur">Struktur</a>
  <a href="#tracking">Tracking</a>
  <a href="#creatives">Creatives</a>
  <a href="#findings">Findings</a>
</nav>
```

**Stat-Strip** (im Hero ist kein Platz — als erste Sektion oder in eine Summary-Card)
```html
<div class="stat-strip">
  <div class="stat"><span class="num">84.200 €</span><span class="lbl">Spend / 12 Monate</span></div>
  <div class="stat"><span class="num">2,4</span><span class="lbl">ROAS / 12 Monate</span></div>
  <div class="stat"><span class="num">46 €</span><span class="lbl">Cost per Result</span></div>
  <div class="stat"><span class="num">58</span><span class="lbl">Opportunity Score</span></div>
  <div class="stat"><span class="num">−27 %</span><span class="lbl">Spend-Trend 30 T</span><span class="sub">ggü. 12-M-Schnitt</span></div>
</div>
```

**Datenqualitäts-Disclaimer**
```html
<div class="disclaimer">
  <strong>Datenqualitäts-Vorbehalt:</strong> Das Conversion-Tracking dieses Kontos
  ist unvollständig (Modul 4 = rot). Alle ROAS- und Cost-per-Result-Zahlen in diesem
  Report stehen damit unter Vorbehalt und sind als Größenordnung, nicht als exakte
  Werte zu lesen.
</div>
```

**Summary-Card**
```html
<div class="summary-card">
  <h3>Kernbefund</h3>
  <p>Verdichteter Fließtext: Gesamt-Ampel, größte Hebel, Datenstand.</p>
  <p class="note">Datenstand: 2026-05-22 · Quelle: Meta-Ads-MCP · read-only Audit</p>
</div>
```

**Ampel-Grid**
```html
<div class="ampel-grid">
  <div class="ampel-card" data-ampel="gruen">
    <p class="modul">M1 — Account-Health</p>
    <p class="urteil">Solide</p>
    <p class="detail">Opportunity Score 72, keine Delivery-Fehler.</p>
  </div>
  <div class="ampel-card" data-ampel="rot">
    <p class="modul">M4 — Tracking</p>
    <p class="urteil">Handlungsbedarf</p>
    <p class="detail">Keine Conversions-API, EMQ schwach.</p>
  </div>
  <!-- … M2, M3, M5 -->
</div>
```
`data-ampel` ∈ {`gruen`, `gelb`, `rot`}.

**Modul-Sektion**
```html
<section id="performance">
  <div class="section-heading">
    <p class="label">Modul 2</p>
    <h2>Performance-Verlauf — 12 Monate</h2>
  </div>
  <p class="section-intro">Optionaler Einleitungssatz.</p>
  <!-- table.data, bar-row, details.dim … -->
</section>
```

**Daten-Tabelle**
```html
<table class="data">
  <thead><tr><th>Kampagne</th><th>Spend</th><th>ROAS</th><th>Cost / Result</th></tr></thead>
  <tbody>
    <tr><td>Prospecting DE</td><td>32.100 €</td><td>2,8</td><td>41 €</td></tr>
    <tr class="total"><td>Gesamt</td><td>84.200 €</td><td>2,4</td><td>46 €</td></tr>
  </tbody>
</table>
```

**Mini-Balken** (Spend-Mix, Placement-Verteilung)
```html
<div class="bar-row">
  <span class="bar-label">Prospecting DE</span>
  <span class="bar-track"><span class="bar-fill" style="width:62%"></span></span>
  <span class="bar-val">62 %</span>
</div>
```
> Ausnahme: Beim `bar-fill` ist `style="width:NN%"` erlaubt — das ist der einzige
> zulässige inline-`style` im ganzen Report, weil die Balkenbreite datengetrieben ist.

**Aufklappbare Modul-Detailkarte** (optional, für lange Modul-Inhalte)
```html
<details class="dim" data-rating="schwach">
  <summary><h3>Tracking-Setup</h3><span class="badge schwach">Handlungsbedarf</span></summary>
  <div class="body"><p>Detailtext …</p></div>
</details>
```
`data-rating` ∈ {`stark`, `mittel`, `schwach`} — `summary` enthält `<h3>` + ein `.badge`.

**Top-3-Hebel**
```html
<ol class="top3">
  <li><h3>Conversions-API anbinden</h3><p>Begründung + erwarteter Effekt.</p></li>
  <li><h3>Zombie-Kampagne pausieren</h3><p>…</p></li>
  <li><h3>Audience-Overlap auflösen</h3><p>…</p></li>
</ol>
```

**Finding-Block**
```html
<div class="suggestion hoch">
  <p class="label">Finding · hohe Relevanz · Quick-Win</p>
  <p><strong>Zombie-Kampagne „Retargeting alt".</strong> 90 Tage Spend ohne ein
  einziges Result. Empfehlung: pausieren und Budget umschichten.</p>
</div>
```
Klasse ∈ {`suggestion hoch`, `suggestion mittel`, `suggestion niedrig`}.

### Validierung vor dem Speichern

Keine offenen `{{…}}`-Platzhalter, nur Klassen aus `report-shell.html`, kein
inline-`style` außer `bar-fill`-Breite. Optional gegen den MTA-Validator prüfbar,
wenn das `marke-und-ting-analyse-reachx`-Plugin installiert ist:
`python3 <mta-plugin>/scripts/validate-report.py <html>` — der Standalone-Skill
hat aber keine harte Abhängigkeit dazu.
