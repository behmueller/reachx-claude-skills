# Analyse-Methodik

Konkrete Schwellwerte, Heuristiken und Berechnungs-Formeln für die Kern-Analysen des Skills:

1. Conversion-Plausibilitäts-Check
2. Performance-Kennzahlen (ROAS / CPA / CR)
3. Kampagnentyp-Mix und Budget-Konzentration
4. Streuverlust-Heuristik für Suchbegriffe
5. Brand-Detection
6. Quality-Score-Schwellwerte
7. Auffälligkeiten-Schwellwerte

Alle Schwellwerte sind als **Default** zu verstehen — bei wiederkehrenden False-Positives in echten MTAs nachjustieren und hier dokumentieren.

## 1. Conversion-Plausibilitäts-Check

Ein **leichter Inline-Check**, kein zweiphasiges Schema-vor-Lauf-Gate. Das volle Datenqualitäts-Gate führt der Schwester-Skill `03-18-web-analytics-ga4`. Hier: eine Inline-Bewertung der `conversion-actions`-Daten, deren Ergebnis als kurzer Abschnitt im Output und als Auffälligkeit landet.

**Eingangs-Daten:** Antwort von `python3 google-ads.py conversion-actions <cid>` — pro Action `id`, `name`, `status`, `type`, `category`, `counting_type`, `primary_for_goal`.

### Prüf-Regeln

**Regel A — Gibt es eine ENABLED-Conversion?**

```
enabled_actions = [a for a in rows if a.status == "ENABLED"]
```

Wenn `len(enabled_actions) == 0` → das Konto misst keine Conversions. Alle `conversions`/`conversions_value`-Werte aus `account-overview` und `campaign-performance` sind 0 oder nicht belastbar.
→ Auffälligkeit `conversion_tracking_fehlt`, Urteil-Beitrag `kein_tracking`.

**Regel B — GA4-importierte Conversions**

```
ga4_actions  = [a for a in enabled_actions if a.type.startswith("GOOGLE_ANALYTICS_4")]
nativ_actions = [a for a in enabled_actions if a.type in ("WEBPAGE", "WEBSITE_CALL", "AD_CALL")]
```

Wenn `ga4_actions` UND `nativ_actions` beide nicht leer sind → das Konto zählt sowohl aus GA4 importierte als auch native Conversions. Wenn beide Gruppen thematisch dieselbe Aktion abdecken (z. B. beide `category` in `{LEAD, SUBMIT_LEAD_FORM}`), droht **Doppelzählung** — Conversion-Zahlen und damit ROAS sind potenziell überzeichnet.
→ Auffälligkeit `conversion_aus_ga4_importiert`, Urteil-Beitrag mindestens `mit_einschraenkung`. Cross-Check-Hinweis für `03-18-web-analytics-ga4`.

**Regel C — Macro-/Micro-Mix in der Zielmessung**

```
primary_actions = [a for a in enabled_actions if a.primary_for_goal]
macro_categories = {"PURCHASE", "LEAD", "SUBMIT_LEAD_FORM", "REQUEST_QUOTE", "BOOK_APPOINTMENT", "SIGNUP"}
micro_categories = {"PAGE_VIEW", "DOWNLOAD", "CONTACT", "DEFAULT"}
```

Wenn unter `primary_actions` sowohl eine Macro- als auch eine Micro-Category vorkommt → die Haupt-Zielmessung (auf die die Gebotsstrategie optimiert) mischt harte und weiche Conversions. Das verzerrt ROAS und CR nach oben.
→ Auffälligkeit `conversion_macro_micro_gemischt`, Urteil-Beitrag mindestens `mit_einschraenkung`.

**Regel D — Verwaiste REMOVED-Actions**

Viele `status: REMOVED`-Actions sind unkritisch (normaler Lifecycle). Nur wenn die *einzige je definierte* Action REMOVED ist und keine ENABLED existiert, deckt sich das mit Regel A.

### Conversion-Setup-Urteil

Ein zusammenfassender Wert, geht ins Frontmatter (`conversion_setup_urteil`):

| Urteil | Bedingung |
|---|---|
| `kein_tracking` | Regel A trifft zu (keine ENABLED-Conversion) |
| `mit_einschraenkung` | Regel B oder Regel C trifft zu, aber Regel A nicht |
| `sauber` | mindestens eine ENABLED-Conversion, kein GA4-Import-Doppelzählungs-Risiko, kein Macro-/Micro-Mix |

### Offene Strategen-Frage

Wenn nach dem Check eine **inhaltliche Unklarheit** bleibt (typischer Fall: GA4-importierte und native Conversion derselben Kategorie — unklar, ob additiv oder ersetzend gezählt), formuliert der Skill **genau eine** beschreibende Frage. Sie muss erklären, *warum* sie wichtig ist. Beispiel:

> Das Konto zählt sowohl eine native Webseiten-Conversion ("Kontaktformular") als auch eine GA4-importierte Conversion ("Lead GA4"). Werden beide additiv in der Zielmessung gezählt? Wichtig, weil sonst die Conversion-Zahl und damit der ROAS doppelt so hoch erscheinen wie real — das würde die ganze SEA-Wirtschaftlichkeits-Aussage verzerren.

Die Frage geht über den Subagent-Rückgabe-Status an den Hauptthread und wird zusätzlich im Frontmatter (`conversion_offene_frage`) und im Body festgehalten. Der Skill schreibt die Outputs trotzdem — mit einer Default-Annahme (im Zweifel: additiv, also ROAS potenziell überzeichnet) — und markiert die Annahme als offenen Punkt.

## 2. Performance-Kennzahlen (ROAS / CPA / CR)

Aus `account-overview` (Account-Ebene) und `campaign-performance` (Kampagnen-Ebene). Alle Geld-Werte kommen vom Wrapper bereits in Konto-Währung — **keine Umrechnung**.

```
roas = conversions_value / cost          # leer (nicht 0) wenn cost = 0
cpa  = cost / conversions                # leer (nicht 0) wenn conversions = 0
cr   = conversions / clicks              # leer (nicht 0) wenn clicks = 0
```

**Wichtig:** Division-durch-0-Fälle als **leer** ausweisen, niemals als 0 — ein ROAS von "leer" (keine Kosten) ist etwas anderes als ein ROAS von 0 (Kosten, kein Umsatz).

**ROAS-Lesart:**

| ROAS | Lesart |
|---|---|
| ≥ 3,0 | wirtschaftlich stark — HTML-Badge `stark` |
| 1,0 - 3,0 | tragfähig, aber Optimierungs-Spielraum — Badge `mittel` |
| < 1,0 | Account/Kampagne macht weniger Umsatz als Kosten — Badge `schwach` |

ROAS ist nur belastbar, wenn der Conversion-Plausibilitäts-Check `sauber` oder `mit_einschraenkung` ergab. Bei `kein_tracking` ROAS/CPA/CR im Output explizit als "nicht belastbar" markieren.

**Trend 30 Tage vs. 12-Monats-Schnitt:**

```
schnitt_30t_aus_12m = cost_12m / 12
spend_30t_vs_schnitt_prozent = (cost_30t - schnitt_30t_aus_12m) / max(schnitt_30t_aus_12m, 1) * 100
```

Positiver Wert = das Konto läuft aktuell stärker als der 12-Monats-Schnitt.

## 3. Kampagnentyp-Mix und Budget-Konzentration

**Kampagnentyp-Mix:** Spend je `channel_type` über 12 Monate gruppieren, Anteil am Gesamt-Spend berechnen.

```
mix[channel_type] = sum(cost je Kampagne dieses channel_type) / sum(cost aller Kampagnen)
```

Anteile summieren sich (mit Rundungs-Toleranz) auf 1,0.

**Budget-Konzentration:** Wenn eine einzelne Kampagne ≥ **60 %** des Gesamt-Spends bindet → Auffälligkeit `budget_konzentration` (Klumpenrisiko).

**Kampagne ohne Conversions:** Eine Kampagne mit `status: ENABLED`, `cost > 0` und `conversions == 0` über 12 Monate → Auffälligkeit `kampagne_ohne_conversions`. Ausnahme: bei `conversion_setup_urteil: kein_tracking` ist 0 Conversions trivial (das Konto misst nichts) — dann keine Einzel-Auffälligkeit pro Kampagne.

## 4. Streuverlust-Heuristik für Suchbegriffe

"Streuverlust" = Spend, der in Suchanfragen fließt, die für den Kunden nichts bringen. Aus dem `search-terms`-Report.

**Ein Suchbegriff gilt als Streuverlust-Kandidat (`streuverlust_flag = true`), wenn:**

```
ist_streuverlust = (
    cost > 0
    AND conversions == 0
    AND clicks >= 3                    # genug Daten, dass 0 Conversions aussagekräftig ist
    AND NOT ist_brand                  # Brand-Suchen ohne Conversion sind anders zu lesen
    AND (
        enthaelt_negativ_signal        # Tokens wie "kostenlos", "gratis", "gebraucht",
                                       #   "job", "stellenangebot", "definition", "wikipedia",
                                       #   "selber machen", "anleitung" — branchen-abhängig erweitern
        OR ctr < 0.005                 # extrem niedrige CTR = thematisch unpassend ausgeliefert
    )
)
```

**Begründung:**

- `cost > 0 AND conversions == 0` — der Suchbegriff hat Geld gekostet, aber nichts gebracht
- `clicks >= 3` — filtert Einzelklick-Rauschen (1 Klick, 0 Conversions ist nicht aussagekräftig)
- `enthaelt_negativ_signal` — Tokens, die Kaufabsicht ausschließen. Die Liste ist branchen-abhängig: bei einem Shop sind "gebraucht"/"reparatur" Streuverlust, bei einem Reparatur-Dienst nicht. Der Skill darf die Liste an der Branche aus `meta.json.branche` ausrichten.
- `ctr < 0.005` — eine sehr niedrige CTR deutet darauf hin, dass die Anzeige für eine thematisch unpassende Suche ausgeliefert wurde

**Streuverlust-Anteil am Spend:**

```
streuverlust_anteil_spend = sum(cost der streuverlust-Suchbegriffe) / sum(cost aller Suchbegriffe)
```

Bei `streuverlust_anteil_spend >= 0.15` (≥ 15 % des Suchbegriff-Spends) → Auffälligkeit `hoher_streuverlust_suchbegriffe`. Empfehlung: Negativ-Keyword-Pflege als Quick-Win.

**Hinweis:** Die Heuristik ist bewusst konservativ — sie flaggt nur klare Fälle. Der Stratege kann im Output-Markdown manuelle Korrekturen vornehmen. Ein `status: EXCLUDED`-Suchbegriff ist bereits negativ ausgeschlossen — er kann trotzdem geflaggt werden (zeigt, dass die Pflege schon gestartet wurde), zählt aber nicht doppelt in die Empfehlung.

## 5. Brand-Detection

Gleiche Logik wie in `03-04-seo-first-party-gsc/reference/gsc-analyse-methodik.md` Abschnitt "Brand-Detection".

Ein Suchbegriff (oder Keyword) gilt als Brand-Term, wenn:

```
brand_tokens = tokenize(meta.json.kunde.lowercase())     # Rechtsform-Suffixe entfernt
# optional ergänzt um den Host aus meta.json.website (ohne www., ohne TLD)
term_tokens  = tokenize(search_term.lowercase())
ueberlap     = brand_tokens ∩ term_tokens
ist_brand    = (len(ueberlap) > 0 AND len(ueberlap) >= len(brand_tokens) - 1)
```

Beispiel: Kunde "Mustermann GmbH" → Brand-Terms sind "mustermann", "mustermann gmbh", "mustermann shop". Nicht "muster gmbh".

**Brand-Anteil:**

```
brand_anteil_spend       = sum(cost der Brand-Suchbegriffe)        / sum(cost aller Suchbegriffe)
brand_anteil_conversions = sum(conversions der Brand-Suchbegriffe) / sum(conversions aller Suchbegriffe)
```

Bei `brand_anteil_spend >= 0.40` (≥ 40 % des Suchbegriff-Spends auf Brand) → Auffälligkeit `brand_anteil_hoch`. Lesart: Das Konto erntet vor allem bestehende Nachfrage (Brand-Suchen), erschließt aber wenig neue. Brand-Klicks sind günstig und konvertieren stark — ein hoher Brand-Anteil schönt den Account-ROAS. Für die MTA-Story: Non-Brand-Performance gesondert betrachten, denn dort liegt das echte Wachstums-Potenzial.

## 6. Quality-Score-Schwellwerte

Aus `keyword-performance`. Quality Score 1-10 oder `null` (Google vergibt keinen QS bei zu wenig Impressionen).

**Bins:**

| Bin | QS-Bereich | Lesart |
|---|---|---|
| schwach | 1-4 | Anzeigen-Relevanz / Erwartete CTR / Landingpage schwach — treibt CPC hoch |
| mittel | 5-7 | solide, Feintuning möglich |
| stark | 8-10 | gut optimiert |

**Spend-gewichtete Verteilung** (nicht keyword-gezählt — ein QS-4-Keyword mit hohem Spend wiegt schwerer als zehn QS-4-Keywords mit Mini-Spend):

```
anteil_schwach = sum(cost der Keywords mit QS 1-4)  / sum(cost der Keywords mit QS != null)
anteil_mittel  = sum(cost der Keywords mit QS 5-7)  / sum(cost der Keywords mit QS != null)
anteil_stark   = sum(cost der Keywords mit QS 8-10) / sum(cost der Keywords mit QS != null)
keywords_ohne_qs = count(Keywords mit QS == null)
```

`null`-QS-Keywords aus der Verteilungs-Berechnung ausnehmen — nicht als 0 werten.

**Auffälligkeit `quality_score_schwach`:** wenn `anteil_schwach >= 0.25` (≥ 25 % des QS-bewerteten Spends auf QS-1-4-Keywords). Empfehlung: Anzeigen-Relevanz (Anzeigentexte, Keyword-zu-Anzeigengruppen-Zuordnung) und Landingpage-Qualität als Optimierungs-Hebel — ein besserer QS senkt den CPC bei gleicher Position.

**Edge-Case:** Wenn die Mehrheit der Keywords `quality_score == null` hat (kleines Konto, zu wenig Impressionen pro Keyword), wird die QS-Verteilung ausgelassen. Frontmatter `quality_score_verteilung.hinweis` setzen, keine `quality_score_schwach`-Auffälligkeit.

## 7. Auffälligkeiten-Schwellwerte

Zusammenfassung aller Schwellwerte, die eine Auffälligkeit auslösen:

| Typ | Auslöser-Schwelle | Relevanz-Default |
|---|---|---|
| `conversion_tracking_fehlt` | keine ENABLED-Conversion-Action | hoch |
| `conversion_aus_ga4_importiert` | GA4-importierte UND native Conversion derselben Kategorie | hoch |
| `conversion_macro_micro_gemischt` | Macro- und Micro-Category beide `primary_for_goal` | mittel |
| `hoher_streuverlust_suchbegriffe` | `streuverlust_anteil_spend >= 0.15` | mittel |
| `quality_score_schwach` | `anteil_schwach >= 0.25` (spend-gewichtet) | mittel |
| `kampagne_ohne_conversions` | ENABLED-Kampagne, `cost > 0`, `conversions == 0` / 12M (nur bei vorhandenem Tracking) | mittel |
| `budget_konzentration` | eine Kampagne bindet ≥ 60 % des Gesamt-Spends | mittel |
| `brand_anteil_hoch` | `brand_anteil_spend >= 0.40` | mittel |
| `roas_unter_eins` | Account-ROAS 12M < 1,0 (nur bei `conversion_setup_urteil != kein_tracking`) | hoch |
| `konto_inaktiv` | Spend letzte 30 Tage = 0, aber 12M-Spend > 0 | mittel |

**Relevanz-Hochstufung:** Eine Auffälligkeit kann von ihrem Default abweichen, wenn die Größenordnung extrem ist — z. B. `budget_konzentration` von Default `mittel` auf `hoch`, wenn eine Kampagne ≥ 85 % bindet. Der Skill entscheidet kontextabhängig, dokumentiert die Hochstufung aber im `beschreibung`-Feld.

Jede Auffälligkeit braucht: `typ`, `titel`, `beschreibung` (1-2 Sätze), `relevanz` (`hoch`/`mittel`/`niedrig`), `handlungs_empfehlung` (konkrete Aktion für die MTA-Slide), optional `betroffene_kampagnen` / `betroffene_suchbegriffe`.

## Daten-Qualitäts-Bewertung

Setze `daten_qualitaet` im Frontmatter basierend auf der Datenbasis:

| Klasse | Bedingung |
|---|---|
| `hoch` | Spend 12M ≥ 5.000 (Konto-Währung) UND ENABLED-Conversion vorhanden |
| `mittel` | Spend 12M ≥ 1.000 UND mindestens eine Kampagne mit Daten |
| `niedrig` | Spend 12M ≥ 100 |
| `keine` | Spend 12M = 0 (Konto angelegt, aber inaktiv) |

Bei `niedrig` und `keine`: Hinweis im Body und im Schluss-Format, dass die Hebel-Aussagen mit Vorsicht zu lesen sind. Bei `keine`: minimale Outputs schreiben, kein erzwungener Analyse-Teil.

**Wichtig:** `daten_qualitaet` bewertet die *Menge* der Daten. `conversion_setup_urteil` bewertet die *Belastbarkeit der Conversion-Zahlen* — beide sind unabhängig. Ein Konto kann viel Spend haben (`daten_qualitaet: hoch`), aber kein Conversion-Tracking (`conversion_setup_urteil: kein_tracking`).

## Re-Run-Konsistenz

Bei Re-Run mit `audits/_backup/`-Optionen:

- Backup-Dateinamen enthalten `sea-<typ>-<ISO>.csv` und `sea-first-party-<ISO>.md`
- Roh-Daten unter `audits/raw/sea-*.json` werden bei Re-Run komplett überschrieben (kein Backup, Roh-Daten sind via neue API-Calls reproduzierbar)
- Die `customer_id` wird beim Re-Run aus dem Frontmatter des vorhandenen `sea-first-party.md` gelesen — keine erneute Konto-Bestätigung

## Offene Methodik-Fragen für spätere Iteration

(In zukünftigen MTAs prüfen und hier dokumentieren:)

- Sind die Streuverlust-Negativ-Signal-Tokens für B2B-Konten sinnvoll? B2B hat andere Streuverlust-Muster (Wettbewerber-Recherche, Job-Suchen) als B2C.
- Soll die Quality-Score-Schwelle (25 % Spend auf QS 1-4) nach channel_type differenzieren? PMax-Kampagnen haben oft keine keyword-Ebene.
- Lohnt ein eigener `pmax_intransparenz`-Hinweis? Performance-Max-Kampagnen liefern weder Search-Terms noch Quality Score auf Keyword-Ebene — ihr Spend ist analytisch eine Blackbox.
- Conversion-Window: Die letzten Tage des 12-Monats-Range haben noch nicht final attribuierte Conversions. Soll der Range standardmäßig 7 Tage vor heute enden, analog zum GSC-3-Tage-Puffer?
