# Schema-Template für `synthese/ziel-annahmen-schema.md`

Format des Phase-A-Outputs. Der Skill schreibt diese Datei mit `status: vorgeschlagen`, der Stratege reviewt und setzt `status: bestaetigt`, dann läuft Phase B.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 04-03-ziele-aus-potenzialen
phase: A
generiert_am: ISO_8601_TIMESTAMP
schema_version: "1.0"
status: vorgeschlagen   # Stratege bestätigt nach Review → bestaetigt

# === Basis (was wurde gelesen) ===
basiert_auf:
  meta_json: meta.json
  kanal_chancen_md: synthese/kanal-chancen.md
  kanal_chancen_csv: synthese/kanal-chancen.csv
  briefing: data/briefing.md       # null wenn nicht vorhanden
  kunde: data/kunde.md             # null wenn nicht vorhanden
  ga4_first_party: audits/ga4-first-party.md   # null wenn 03-18 nicht lief
  sea_first_party: audits/sea-first-party.md   # null wenn 03-17 nicht lief
  audits_genutzt:
    - audits/seo-cluster-zusammenfassung.md
    - audits/google-ads.md
    # ... alle relevanten

# === First-Party-CR-Quellen (GA4 / SEA) ===
first_party_cr:
  ga4_verfuegbar: false            # true wenn audits/ga4-first-party.md vorhanden
  ga4_belastbarkeit: null          # gruen | gelb | rot — aus ga4-first-party.md Frontmatter
  ga4_gesamt_cr: null              # conversion_baseline.gesamt_cr (nachrichtlich)
  ga4_consent_korrektur_hinweis: null   # Text — Volumen-Basis um diesen Faktor hochrechnen
  sea_verfuegbar: false            # true wenn audits/sea-first-party.md vorhanden
  sea_conversion_setup_urteil: null     # sauber | mit_einschraenkung | kein_tracking
  sea_account_cr: null             # statistiken_12_monate.cr (nachrichtlich)

# === Branchen-Typ und Lauf-Modus ===
branchen_typ: BRANCHEN_SLUG   # b2b_saas | b2c_ecommerce | lokal_dienstleister | b2b_industrie | b2b_mittelstand_dienstleister | content_publisher | marktplatz_plattform | sonstige
branchen_typ_konfidenz: hoch
lauf_modus: abgeleitet_pur   # abgeleitet_pur | plausibilitaets_check | hybrid
lauf_modus_begruendung: "Briefing nennt keine bezifferten KPIs (Felder als unklar_aus_transkript markiert)"

# === Briefing-KPI-Inventur (was hat der Kunde gesagt) ===
briefing_kpi_inventur:
  bezifferte_ziele_vorhanden: false
  genannte_ziele: []         # Liste mit kpi, wert, quelle_briefing_zeile
  timeline_vorhanden: null   # in Monaten, oder null
  aov_vom_kunden_genannt: null

# === AOV / LTV-Annahme ===
aov:
  bandbreite_min: 0
  bandbreite_realistisch: 0
  bandbreite_max: 0
  einheit: EUR
  typ: order   # order | mrr | arr | auftragswert
  konfidenz: hoch | mittel | niedrig
  quelle: kunde_md_portfolio | briefing_aussage | branchen_benchmark | schaetzung_skill
  begruendung: "Portfolio-Range 80-300 EUR Mid-Tier-Werkzeuge, realistisch 150 EUR"

# === Lead-Funnel (nur bei B2B-Branchen-Typen) ===
lead_funnel:
  aktiv: true | false
  stufen:
    - name: anfrage_qualifiziert
      cr_min: 0.50
      cr_realistisch: 0.65
      cr_max: 0.80
      konfidenz: mittel
      quelle: branchen_benchmark
    - name: qualifiziert_zu_angebot
      cr_min: 0.40
      cr_realistisch: 0.55
      cr_max: 0.70
      konfidenz: mittel
      quelle: branchen_benchmark
    - name: angebot_zu_auftrag
      cr_min: 0.20
      cr_realistisch: 0.30
      cr_max: 0.40
      konfidenz: mittel
      quelle: branchen_benchmark

# === Kanäle mit CR-Bandbreiten und Ramp-up ===
kanaele:
  - kanal_slug: seo
    kanal_anzeigename: SEO
    rang_aus_kanal_chancen: 1
    volumen_basis:
      wert_min: 0
      wert_realistisch: 0
      wert_max: 0
      einheit: monatliche_suchanfragen
      quelle: audits/seo-cluster-zusammenfassung.md
      konfidenz: hoch
      begruendung: ""   # bei GA4-Sessions als Basis: Consent-Hochrechnungs-Faktor hier dokumentieren
    cr_bandbreite:
      konservativ: 0.008
      realistisch: 0.015
      ambitioniert: 0.030
      konfidenz: hoch
      # quelle: einer der 10 kanonischen CR-Quellen-Tags —
      #   ga4_first_party | ga4_first_party_eingeschraenkt | sea_first_party | sistrix_daten |
      #   ahrefs_daten | gmb_daten | ads_audit | briefing_aussage | branchen_benchmark | schaetzung_skill
      # ga4_first_party (belastbarkeit gruen): realistisch = GA4-Channel-CR, Spread ×0,80 / ×1,30
      # ga4_first_party_eingeschraenkt (belastbarkeit gelb): realistisch = GA4-CR, Spread ×0,65 / ×1,55
      # branchen_benchmark (kein GA4 / belastbarkeit rot): Werte aus diesem Template
      quelle: branchen_benchmark
      first_party_cr_roh: null   # die echte GA4-Channel-CR, auch wenn quelle=branchen_benchmark (nachrichtlich)
    klick_anteil:
      konservativ: 0.20
      realistisch: 0.30
      ambitioniert: 0.40
      begruendung: "Position-1-Erwartung, Klick-Verteilung nach Google-CTR-Studien"
    ramp_up_monate_min: 6
    ramp_up_monate_max: 12
    ramp_up_quelle: branchen_benchmark
    
  - kanal_slug: sea
    kanal_anzeigename: SEA / Google-Ads
    rang_aus_kanal_chancen: 2
    volumen_basis:
      wert_min: 0
      wert_realistisch: 0
      wert_max: 0
      einheit: monatliche_klicks_aus_spend
      quelle: audits/google-ads.md
      konfidenz: mittel
    cr_bandbreite:
      konservativ: 0.025
      realistisch: 0.045
      ambitioniert: 0.070
      konfidenz: hoch
      # quelle: einer der 10 kanonischen CR-Quellen-Tags —
      #   ga4_first_party | ga4_first_party_eingeschraenkt | sea_first_party | sistrix_daten |
      #   ahrefs_daten | gmb_daten | ads_audit | briefing_aussage | branchen_benchmark | schaetzung_skill
      # sea_first_party (conversion_setup_urteil sauber): realistisch = SEA-Account-/Kampagnen-CR, Spread ×0,80 / ×1,30
      # sea_first_party (conversion_setup_urteil mit_einschraenkung): realistisch = SEA-CR, Spread ×0,65 / ×1,55, konfidenz mittel
      # branchen_benchmark (kein SEA / kein_tracking): Werte aus diesem Template
      quelle: branchen_benchmark
      first_party_cr_roh: null   # die echte SEA-CR, auch wenn quelle=branchen_benchmark (nachrichtlich)
    spend_annahme_eur_monat:
      konservativ: 0
      realistisch: 0
      ambitioniert: 0
      quelle: schaetzung_skill | briefing_aussage
    ramp_up_monate_min: 1
    ramp_up_monate_max: 2

  # ... weitere Kanäle analog: local-seo, linkedin-ads, meta-ads, content, social-organisch, newsletter, website-cro

# === Doppelzählungs-Korrektur (Aggregat über Kanäle) ===
doppelzaehlung_faktor:
  zwei_kanal: 0.85
  drei_plus_kanal: 0.75
  begruendung: "Default-Werte für Multi-Touch-Overlap; im Schema-Review anpassbar"

# === Quellen-Inventur ===
quellen_inventur:
  hoch_konfidenz: 0   # int — Anzahl Annahmen mit Konfidenz hoch
  mittel_konfidenz: 0
  niedrig_konfidenz: 0
  branchen_benchmark_anteil_prozent: 0.0   # wie viel Prozent aus Branchen-Benchmarks
---

# Annahmen-Schema für 04-03-ziele-aus-potenzialen: KUNDENNAME

## Übersicht

3-5 Sätze: Branchen-Typ, Lauf-Modus, Anzahl Kanäle, Konfidenz-Verteilung, Hinweis auf den Strategen-Review.

## AOV / LTV-Annahme

Bandbreite mit Begründung und Quelle.

## Lead-Funnel (B2B)

Tabelle mit Stufen, CR-Bandbreiten, Quellen.

## Kanal-Annahmen

Pro Kanal: Volumen-Basis, CR-Bandbreite, Ramp-up, Quellen.

## Pflicht-Review

Bitte prüfen:

1. **AOV-Bandbreite** — passt zum Portfolio? (Wenn nein: Wert direkt im Frontmatter editieren)
2. **CR-Bandbreiten pro Kanal** — branchen-realistisch? (Branchen-Benchmark vs. Kunden-Reife)
3. **Lead-Funnel-Stufen** (B2B) — sind die Quoten realistisch oder zu optimistisch?
4. **Ramp-up-Phasen** — passt zur Kunden-Timeline aus dem Briefing? Wenn Kunde "3 Monate Ergebnisse" sagt, aber SEO 6-12 braucht → im Output als Diskrepanz markieren
5. **Doppelzählungs-Faktor** — falls Kunde Multi-Touch trackt, anpassen

Nach Review: `status: bestaetigt` im Frontmatter setzen.
```

---

## Branchen-Defaults

Pro Branchen-Typ kuratierte CR-Bandbreiten und AOV-Hinweise.

### 1. `b2b_saas`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 0,5% | 1,2% | 2,5% | 6-12 |
| SEA | 2,0% | 4,0% | 6,5% | 1-2 |
| LinkedIn-Ads | 0,8% | 1,8% | 3,5% | 2-4 |
| Meta-Ads | 0,6% | 1,4% | 2,8% | 1-3 |
| Content / Blog | 0,4% | 1,0% | 2,2% | 6-12 |
| Newsletter | 1,5% | 4,0% | 8,0% | 2-4 |
| Social-organisch | 0,3% | 0,8% | 1,5% | 3-6 |

AOV-Default: 80-300 EUR MRR, 1.000-3.500 EUR ARR. LTV typisch 24-36 Monate.
Lead-Funnel: Anfrage→qualifiziert 60-80%, qualifiziert→Angebot 50-70%, Angebot→Auftrag 25-40%.

### 2. `b2c_ecommerce`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 1,0% | 2,0% | 3,5% | 6-12 |
| SEA | 2,5% | 4,5% | 7,5% | 1-2 |
| Meta-Ads | 1,2% | 2,8% | 5,5% | 1-3 |
| Newsletter | 2,0% | 5,0% | 10,0% | 2-4 |
| Content / Blog | 0,6% | 1,4% | 2,8% | 6-12 |
| Social-organisch | 0,4% | 1,0% | 2,0% | 3-6 |
| Website-CRO | +10% | +15% | +30% | 1-3 |

AOV-Default: 40-200 EUR Order (kategorien-abhängig). Wiederkaufs-Rate typisch 20-40% pro Jahr.
Lead-Funnel: deaktiviert (Direct-Conversion).

### 3. `lokal_dienstleister`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| Local-Pack / GMB | 4,0% | 8,0% | 12,0% | 1-3 |
| SEO | 1,2% | 2,5% | 4,0% | 4-10 |
| SEA (Local) | 3,0% | 5,5% | 8,5% | 1-2 |
| Meta-Ads | 0,8% | 2,0% | 4,0% | 1-3 |
| Newsletter | 1,5% | 4,0% | 8,0% | 2-4 |

AOV-Default: 250-2.000 EUR pro Auftrag (Branchen-spezifisch — Friseur 50 EUR, Handwerker 800 EUR, Anwalt 1.500 EUR).
Lead-Funnel: optional aktiv, Anfrage→Auftrag 30-60% (kürzerer Funnel als B2B-SaaS).

### 4. `b2b_industrie`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 0,6% | 1,3% | 2,8% | 6-12 |
| SEA | 1,8% | 3,5% | 6,0% | 1-2 |
| LinkedIn-Ads | 0,5% | 1,2% | 2,5% | 2-4 |
| Content / Blog | 0,4% | 1,0% | 2,2% | 6-12 |
| Newsletter | 1,0% | 3,0% | 6,0% | 2-4 |

AOV-Default: 5.000-50.000+ EUR Auftragswert. LTV oft mehrjährig.
Lead-Funnel: lang — Anfrage→qualifiziert 50-70%, qualifiziert→Angebot 40-60%, Angebot→Auftrag 15-30%.

### 5. `b2b_mittelstand_dienstleister`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 0,8% | 1,5% | 3,0% | 6-12 |
| SEA | 2,5% | 4,5% | 7,0% | 1-2 |
| LinkedIn-Ads | 0,5% | 1,2% | 2,4% | 2-4 |
| Content / Blog | 0,5% | 1,2% | 2,5% | 6-12 |
| Newsletter | 1,5% | 4,0% | 8,0% | 2-4 |

AOV-Default: 1.500-15.000 EUR pro Projekt / Retainer.
Lead-Funnel: Anfrage→qualifiziert 55-75%, qualifiziert→Angebot 45-65%, Angebot→Auftrag 20-35%.

### 6. `content_publisher`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 1,5% | 3,0% | 5,0% | 6-12 |
| Newsletter | 3,0% | 6,0% | 12,0% | 2-4 |
| Social-organisch | 0,5% | 1,2% | 2,5% | 3-6 |
| Meta-Ads | 0,8% | 2,0% | 4,0% | 1-3 |

AOV: Abo-Modell — typisch 5-30 EUR / Monat. LTV stark Retention-getrieben.

### 7. `marktplatz_plattform`

| Kanal | CR konservativ | CR realistisch | CR ambitioniert | Ramp-up |
|---|---|---|---|---|
| SEO | 1,2% | 2,5% | 4,5% | 6-12 |
| SEA | 2,0% | 4,0% | 6,5% | 1-2 |
| Meta-Ads | 1,0% | 2,5% | 5,0% | 1-3 |

AOV: hängt stark vom Take-Rate-Modell ab; im Schema branchen-spezifisch.

### 8. `sonstige`

Mittelwert über die anderen Typen, Konfidenz `niedrig`, Hinweis im Schema-Body, dass der Stratege die Werte branchen-spezifisch nachziehen sollte.

---

## Konventionen für Defaults

- Bandbreiten sind als **Faktor 2-4 zwischen konservativ und ambitioniert** designt — wenn der Skill weniger Spread erzeugt, ist das ein Hinweis auf zu optimistische Annahmen
- Default-Konfidenz für reine Branchen-Benchmark-Werte ist `mittel` — wird auf `hoch` nur erhöht, wenn audit-belegte Kunden-Daten die Bandbreite stützen
- Bei `audit_coverage.modus: duenn` (aus `kanal-chancen.md`) werden alle Default-Konfidenzen automatisch auf `niedrig` herabgestuft

---

## First-Party-CR überschreibt die Branchen-Defaults

Die obigen Branchen-Tabellen sind der **Fallback**. Liegen First-Party-Daten des Kunden vor, ist die echte Kunden-CR die bevorzugte Quelle (Quellen-Hierarchie, siehe `herleitungs-methodik.md` Abschnitt 2). Das `belastbarkeit`-Feld aus `audits/ga4-first-party.md` bzw. das `conversion_setup_urteil` aus `audits/sea-first-party.md` steuern, wie stark die echten Zahlen genutzt werden.

**Kanonische CR-Quellen-Tag-Liste (`cr_bandbreite.quelle`):** Das Feld trägt genau einen Wert aus dieser 10er-Liste — identisch deklariert in `SKILL.md` Schritt A.7 und der CSV-Spalte `annahme_cr_quelle` in `ziel-output-schema.md`:

```
ga4_first_party | ga4_first_party_eingeschraenkt | sea_first_party | sistrix_daten |
ahrefs_daten | gmb_daten | ads_audit | briefing_aussage | branchen_benchmark | schaetzung_skill
```

`abgeleitete_ziele` ist kein Herkunfts-Tag und darf hier nicht vorkommen. Die untenstehende Tabelle zeigt nur die GA4-/SEA-First-Party-Fälle im Detail; `sistrix_daten`, `ahrefs_daten`, `gmb_daten` und `ads_audit` kommen zum Tragen, wenn die CR aus dem jeweiligen Audit (statt First-Party oder reinem Branchen-Benchmark) abgeleitet wurde.

| Quelle | Gate-Wert | CR-Bandbreite | `cr_bandbreite.quelle` | Konfidenz |
|---|---|---|---|---|
| GA4 (`ga4-first-party.md`) | `belastbarkeit: gruen` | `realistisch` = GA4-Channel-CR (oder Gesamt-CR-Fallback); Spread `×0,80` / `×1,30` | `ga4_first_party` | hoch (Channel-CR) / mittel (Gesamt-CR-Fallback) |
| GA4 | `belastbarkeit: gelb` | `realistisch` = GA4-CR; breiterer Spread `×0,65` / `×1,55` | `ga4_first_party_eingeschraenkt` | mittel |
| GA4 | `belastbarkeit: rot` | Branchen-Default aus diesem Template; GA4-Wert nur in `first_party_cr_roh` + Body-Hinweis | `branchen_benchmark` | wie Default |
| SEA (`sea-first-party.md`) | `conversion_setup_urteil: sauber` | `realistisch` = SEA-Account-/Kampagnen-CR; Spread `×0,80` / `×1,30` | `sea_first_party` | hoch |
| SEA | `conversion_setup_urteil: mit_einschraenkung` | `realistisch` = SEA-CR; breiterer Spread `×0,65` / `×1,55` | `sea_first_party` | mittel |
| SEA | `conversion_setup_urteil: kein_tracking` | Branchen-Default aus diesem Template; SEA-Wert nur in `first_party_cr_roh` + Body-Hinweis | `branchen_benchmark` | wie Default |

**Consent-Nuance bei der Volumen-Basis:** Eine Consent-/Cookie-Lücke verzerrt die **Sessions** (Volumen) nach unten, die **Conversion-Rate** bleibt robust. Folge:

- GA4-**CR** wird unverändert als `realistisch`-Wert genutzt — Consent ändert daran nichts.
- GA4-**Sessions** als `volumen_basis` werden, wenn `conversion_baseline.consent_korrektur_hinweis` im GA4-Frontmatter gesetzt ist, um den dort genannten Faktor **nach oben hochgerechnet**. Der Faktor und die Begründung gehören in `volumen_basis.begruendung`.

Eine Mischung der Quellen-Tags im selben Schema ist erwartet und korrekt: GA4-belegbare Kanäle (Organic Search, Direct, Referral) tragen `ga4_first_party`, der Paid-Search-Kanal `sea_first_party`, noch nicht bespielte Kanäle weiterhin `branchen_benchmark`. Der Tag wird von `04-04-forecast-modell` unverändert durchgereicht.
