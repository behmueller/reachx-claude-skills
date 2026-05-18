---
name: 04-02-kanal-chancen-analyse
description: Zentraler MTA-Synthese-Skill. Aggregiert alle vorhandenen Audit-Outputs (SEO, SEA, Meta-Ads, LinkedIn-Ads, Website-Tech, Content, Local/GMB, Social) zu einem priorisierten Kanal-Chancen-Ranking. Pro Kanal werden fünf Achsen bewertet (Potenzial, Aufwand, Briefing-Fit, Kunden-Reife, Branchen-Fit) und zu einem chancen_score von 0-100 verdichtet. Output ist synthese/kanal-chancen.md mit Top-3-Empfehlungen, synthese/kanal-chancen.csv und ein HTML-Report mit Score-Heatmap. Nutze diesen Skill IMMER, wenn der Nutzer im MTA-Kontext Kanal-Chancen priorisieren oder Audit-Ergebnisse zu einer Channel-Strategie verdichten will - auch bei Phrasen wie "Kanal-Chancen-Analyse", "welche Kanäle priorisieren", "Kanal-Ranking", "Channel-Mix-Empfehlung", "Audit-Synthese", "Top-Hebel ableiten", "wo soll der Kunde Budget einsetzen", "Channel-Priorisierung". Setzt voraus, dass 01-01-mta-projekt-init gelaufen ist und mindestens 3-4 Audit-Skills durch sind - sonst Warnung "dünne Datenbasis".
---

# Kanal-Chancen-Analyse

Zentraler Synthese-Skill in Stufe 4 — der **Trichter vor dem Forecast**. Liest alle vorhandenen Audit-Outputs aus Stufe 3 plus Briefing/Marken-Profile und verdichtet sie zu einem priorisierten Kanal-Chancen-Ranking. Output ist die strategische Grundlage für `04-03-ziele-aus-potenzialen`, `04-04-forecast-modell` und `04-05-90-tage-plan`.

Drei Output-Ebenen:

1. **Aggregat-Markdown** `synthese/kanal-chancen.md` — Pro Kanal alle fünf Achsen-Scores + `chancen_score`, dazu Top-3-Empfehlungen mit Begründungen und eine strategische Story (1-2 größte Hebel)
2. **Score-CSV** `synthese/kanal-chancen.csv` — eine Zeile pro Kanal mit allen fünf Achsen-Scores für schnelle Sortierung/Filter
3. **HTML-Report** `reports/10-kanal-chancen.html` — Score-Heatmap (Kanal × Achse), Top-3-Karten, Auffälligkeiten

## Ausführungs-Modus

Dieser Skill läuft auf dem **`mta-stratege`**-Subagent (Opus 4.7). Synthese-/Bewertungs-Skills brauchen Opus für die mehrdimensionale Abwägung. Der Hauptthread orchestriert (Schema-Vorschläge bestätigen, finale Empfehlungen reviewen), der Subagent verdichtet die vorhandenen Audit-Outputs zu strategischen Empfehlungen.

Bei Schema-vor-Lauf-Pattern: Phase A schreibt das Schema nach Drive und bricht ab. User bestätigt im Hauptthread. Phase B läuft im Subagent erneut und führt die finale Logik aus.

Aufrufmuster aus dem Hauptthread:
- Tool: `Agent` mit `subagent_type: "mta-stratege"`
- Übergabe: MTA-Slug + Phase-Flag (A/B) falls Schema-vor-Lauf
- Erwarteter Rückgabe-Status: siehe Standard-Schlussformat in `contracts.md` Abschnitt 6.

## Token-Tracking

Vor und nach dem Skill-Lauf den Token-Tracker markieren, damit der Verbrauch dem Skill zugeordnet werden kann (siehe `contracts.md` Sektion 10):

```bash
TRACKER="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/token-tracker.py"
SLUG="<mta-slug-aus-schritt-0>"
SKILL_NAME="<name-dieses-skills>"
python3 "$TRACKER" mark-skill-start "$SLUG" "$SKILL_NAME"
# ... Skill-Logik ...
python3 "$TRACKER" mark-skill-end "$SLUG" "$SKILL_NAME"
```

Beim HTML-Report-Render zusätzlich den `{{TOKEN_FOOTER}}`-Platzhalter mit dem Skill-spezifischen Counter befüllen:

```bash
TOKEN_FOOTER=$(python3 "$TRACKER" render-skill-counter "$SLUG" "$SKILL_NAME")
# In den HTML-Render-Schritt einbauen: {{TOKEN_FOOTER}} → $TOKEN_FOOTER ersetzen
```

Der Stop-Hook aggregiert den Verbrauch automatisch nach jedem Prompt — diese Marker sind nur für die saubere Pro-Skill-Aufschlüsselung nötig.

## Wann triggern

- "Kanal-Chancen-Analyse"
- "Welche Kanäle priorisieren"
- "Kanal-Ranking"
- "Channel-Mix-Empfehlung"
- "Audit-Synthese"
- "Top-Hebel ableiten"
- "Wo soll der Kunde Marketing-Budget einsetzen"
- "Channel-Priorisierung"
- "Welche Kanäle sind die besten Hebel"

## Voraussetzungen

- `01-01-mta-projekt-init` gelaufen → `meta.json`, `status.md`
- **Mindestens 3-4 Audit-Skills aus Stufe 3 durchgelaufen** (in `status.md` als `schritte_done` markiert) — sonst Warnung "Synthese auf dünner Datenbasis"
- Empfohlen: `data/briefing.md` (für Briefing-Fit-Achse) — sonst Briefing-Fit-Score wird neutral gesetzt
- Empfohlen: `data/kunde.md` (für Kunden-Reife-Achse)
- Empfohlen: `synthese/positionierung.md` falls bereits vorhanden — fließt in die strategische Story ein

**Synthese-Sequenz (`contracts.md` Abschnitt 12):** `04-02-kanal-chancen-analyse` ist der erste Schritt der Stufe-4-Synthese-Kette und wird sequenziell vor `04-03-ziele-aus-potenzialen` ausgeführt. Verbindliche Reihenfolge: `04-01 → 04-02 → 04-03 → 04-04 → 04-05 → 04-06` — kein Parallel-Start, der Hauptthread orchestriert sequenziell.

## Ablauf

### Schritt 1: Projekt-Auffindung und Voraussetzungs-Check

Folge `contracts.md` Abschnitt 1. Drive-Bootstrap:

```bash
DRIVE_PY="${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/scripts/drive.py"
[ -f "$DRIVE_PY" ] || DRIVE_PY="$HOME/.claude/skills/01-01-mta-projekt-init/scripts/drive.py"

MTA_JSON=$(python3 "$DRIVE_PY" get-mta "<slug>")
FOLDER_ID=$(echo "$MTA_JSON" | jq -r '.folder_id')
META_ID=$(python3 "$DRIVE_PY" list-children "$FOLDER_ID" | jq -r '.[] | select(.name == "meta.json") | .id')
python3 "$DRIVE_PY" read "$META_ID" > /tmp/meta.json
DATA_ID=$(jq -r '.drive.subfolders.data' /tmp/meta.json)
WB_ID=$(jq -r '.drive.subfolders.wettbewerber' /tmp/meta.json)
AUDITS_ID=$(jq -r '.drive.subfolders.audits' /tmp/meta.json)
SYNTHESE_ID=$(jq -r '.drive.subfolders.synthese' /tmp/meta.json)
REPORTS_ID=$(jq -r '.drive.subfolders.reports' /tmp/meta.json)
```

Lies `status.md` aus Drive (`find_by_name(FOLDER_ID, "status.md")` → `read_text`) und parse `schritte_done` aus dem Frontmatter.

**Audit-Coverage-Check:**

Zähle die Anzahl der durchgelaufenen Audit-Skills aus `schritte_done`. Audit-Skills sind:

- `03-04-seo-first-party-gsc`, `03-01-seo-sichtbarkeit-und-rankings`, `03-02-seo-keyword-recherche`, `03-03-seo-keyword-kategorisierung` (SEO-Familie zählt als 1, wenn mindestens einer gelaufen ist; voll wenn alle vier gelaufen — `03-04-seo-first-party-gsc` ist häufig geskippt, das ist kein Coverage-Mangel)
- `03-05-sea-google-ads-check`, `03-06-sea-meta-ads-library-check`, `03-07-sea-linkedin-ads-library-check` (jeder zählt einzeln)
- `03-14-web-tech-und-tracking` (zählt 1)
- `03-15-web-content-inventur` (zählt 1)
- `03-16-local-gmb-und-seo` (zählt 1)
- `03-11-social-linkedin`, `03-08-social-instagram`, `03-09-social-tiktok`, `03-10-social-pinterest` (jeder zählt einzeln)

Wenn weniger als 3 Audit-Skills durchgelaufen: **Warnung** im Schluss-Format, aber Skill läuft trotzdem (Stratege kann frühe Synthese gewollt haben).

### Schritt 2: Input-Inventur — Cross-Audit-Read aus Drive

Liste alle Files im `AUDITS_ID`-Folder via `drive.py list-children "$AUDITS_ID"` und lade jedes relevante Markdown/CSV in den lokalen Cache (`~/.cache/reachx-mta/<slug>/audits/`) per `drive.py read <file-id>`. Pattern:

```bash
python3 "$DRIVE_PY" list-children "$AUDITS_ID" > /tmp/audits-list.json
# Für jeden Eintrag mit name in {*.md, *.csv}: drive.py read <id> > local-cache
```

Analog für `synthese/positionierung.md` (falls vorhanden) via `find_by_name(SYNTHESE_ID, "positionierung.md")` und `data/briefing.md`, `data/kunde.md` aus `DATA_ID`.

Erwartete Pfade (alle optional, jeder als File auf Drive zu prüfen):

- `audits/gsc-first-party.md`, `audits/gsc-performance.csv`, `audits/gsc-pages.csv` (First-Party-Quelle, kann fehlen wenn GSC nicht angebunden)
- `audits/ga4-first-party.md`, `audits/ga4-channels.csv`, `audits/ga4-pages.csv` (First-Party-Web-Analytics aus `03-18-web-analytics-ga4`, kann fehlen wenn GA4 nicht angebunden — liefert echte Ist-Sessions/CR/Umsatz pro Kanal plus das `belastbarkeit`-Gate)
- `audits/sea-first-party.md`, `audits/sea-kampagnen.csv`, `audits/sea-suchbegriffe.csv` (First-Party-Google-Ads-Konto aus `03-17-sea-first-party-google-ads`, kann fehlen wenn kein Ads-Konto angebunden — liefert echte Kampagnen-Performance des Kunden)
- `audits/seo-sichtbarkeit.md`, `audits/seo-keyword-pool.md`, `audits/seo-cluster-zusammenfassung.md`, `audits/seo-keywords.csv`, `audits/seo-keyword-pool.csv`, `audits/seo-keyword-cluster.csv`, `audits/seo-rankings-ahrefs.csv` (optional, nur im Hybrid- oder Ahrefs-only-Modus)
- `audits/google-ads.md`, `audits/google-ads-anzeigen.csv`
- `audits/meta-ads.md`, `audits/meta-ads-anzeigen.csv`
- `audits/linkedin-ads.md`, `audits/linkedin-ads-anzeigen.csv`
- `audits/web-tech-tracking.md`, `audits/pagespeed.csv`
- `audits/content-inventur.md`
- `audits/local-gmb.md`, `audits/local-rankings.csv`
- `audits/instagram-wettbewerb.md`, `audits/tiktok-wettbewerb.md`, `audits/pinterest-wettbewerb.md`, `audits/linkedin-wettbewerb.md` (oder `03-11-social-linkedin`-Output)
- `audits/reddit-fit.md` (Reddit-/Community-Kanal, optional — fehlt häufig, dann Reddit-Kanal mit Konfidenz `niedrig`)
- `audits/geo-sichtbarkeit.md` (KI-/Discovery-Sichtbarkeits-Audit, **optional** — kann fehlen; fehlt er, wird der GEO-Kanal mit Branchen-Default und Konfidenz `niedrig` bewertet, nicht ausgelassen)
- `data/briefing.md`, `data/kunde.md`
- `synthese/positionierung.md`

Halte die Inventur als interne Datenstruktur — für jeden Kanal wird notiert, welche Inputs zur Verfügung standen.

**Apify-Konfidenz-Flag für Paid-Kanäle:** Die Scores der Paid-Kanäle (SEA / Google-Ads, Meta-Ads) hängen an den Daten aus dem Google-Ads-Transparency-Center und der Meta-Ad-Library — beide werden via Apify gescrapt. Prüfe bei der Input-Inventur, ob `audits/google-ads.md` bzw. `audits/meta-ads.md` einen Hinweis tragen, dass der Apify-Scrape unvollständig oder gar nicht gelaufen ist (Session-Abbruch, leere Anzeigen-CSV trotz aktiver Domain, expliziter `apify_unvollstaendig`-Vermerk). Trifft das zu:

- Den `potenzial_score` und `kunden_reife_score` des betroffenen Paid-Kanals mit `konfidenz: niedrig` markieren und im Frontmatter pro Kanal das Feld `apify_konfidenz_flag: niedrig_ohne_apify` setzen.
- Im Output (Auffälligkeiten und strategische Story) explizit darauf hinweisen: **Paid-Kanal-Scores ohne vollständige Display-/Video-Daten aus dem Transparency-Center können 5–10 Punkte zu niedrig liegen** — das Transparency-Center listet ohne sauberen Scrape oft nur Search-Anzeigen, nicht Display und Video. Der Stratege soll den Score in dem Wissen lesen.
- Den Paid-Kanal **nicht** aus dem Ranking entfernen — nur die Konfidenz und der Hinweis ändern sich.

**Input-Staleness erfassen (`contracts.md` Abschnitt 12):** Beim Lesen jedes Audit-/Synthese-Inputs aus Drive den `generiert_am`-Stempel aus dem Frontmatter mitnehmen. Diese Stempel werden im Output-Frontmatter als `basis_inputs`-Liste festgehalten (siehe Schritt 9). Existiert bereits ein `synthese/kanal-chancen.md` aus einem früheren Lauf: vergleiche die `generiert_am`-Stempel der Inputs mit dessen `generiert_am`. Ist ein Input **neuer** als der bestehende Output, im Schluss-Format einen Staleness-Hinweis ausgeben ("`<input>` wurde nach dem letzten kanal-chancen-Lauf aktualisiert — Re-Run empfohlen"). Pauschal gilt: Wurde ein Stufe-3-Audit re-gerunnt, ist die Stufe-4-Kette potenziell stale.

**First-Party-Daten und das `belastbarkeit`-Gate:** Wenn `audits/ga4-first-party.md` vorliegt, lies aus dem Frontmatter das Feld `belastbarkeit` (`gruen | gelb | rot`) sowie die Blöcke `conversion_baseline` und `kanal_wertigkeit`. Das `belastbarkeit`-Gate steuert verbindlich, mit welcher Konfidenz die GA4-Zahlen in die Achsen-Scores eingehen:

- `gruen` → GA4-Werte voll nutzbar, Achsen-Konfidenz `hoch`
- `gelb` → nutzbar mit Vorsicht, Achsen-Konfidenz `mittel`
- `rot` → GA4-Conversion-Zahlen nur als grobe Orientierung, Achsen-Konfidenz `niedrig`, keine harte Score-Ableitung daraus

`audits/sea-first-party.md` liefert die echte Google-Ads-Kampagnen-Performance des Kunden (Spend, ROAS, Conversions). Beide First-Party-Quellen sind optional — fehlen sie, läuft der Skill wie bisher mit den geschätzten Defaults (kein Blocker, keine harte Abhängigkeit).

### Schritt 3: Branchen-Typ ermitteln

Aus `meta.json.branche` und `data/kunde.md` (falls vorhanden) wird der Branchen-Typ klassifiziert. Mappe auf einen der Defaults in `reference/branchen-fit-defaults.md`:

- `b2b_saas`
- `b2c_ecommerce`
- `lokal_dienstleister`
- `b2b_industrie`
- `b2b_mittelstand_dienstleister`
- `content_publisher`
- `marktplatz_plattform`
- `sonstige`

Wenn unklar: nimm `sonstige` und verwende den ausgeglichenen Default-Fit-Vektor.

### Schritt 4: Pro Kanal die fünf Achsen scoren

Der Skill bewertet die folgenden **Kanäle** (in fester Reihenfolge im Output):

1. **SEO** (organische Suche)
2. **SEA / Google-Ads** (paid Search)
3. **Meta-Ads** (Facebook + Instagram bezahlt)
4. **LinkedIn-Ads** (paid)
5. **Local-SEO / GMB** (nur wenn lokal-relevant, sonst Skip)
6. **Content / Blog** (organische Content-Reichweite)
7. **Instagram-organisch**
8. **TikTok-organisch**
9. **LinkedIn-organisch**
10. **Pinterest-organisch**
11. **Facebook-organisch**
12. **YouTube-organisch** (optional, branchenabhängig)
13. **Reddit / Community** (organische Community-Präsenz, branchenabhängig)
14. **KI-/Discovery-Sichtbarkeit (GEO)** — Sichtbarkeit in KI-Antworten und Discovery-Feeds
15. **Website-CRO / Conversion-Optimierung**

**Drei zusätzliche Kanäle gegenüber der Grundliste — Sonderbehandlung beachten:**

- **Facebook-organisch** — wird wie die anderen Social-organisch-Kanäle bewertet. Datenquelle ist das Facebook-Audit, falls vorhanden; fehlt es, gilt der Branchen-Fit-Default und Konfidenz `niedrig`. Facebook-Posts sind häufig login-wall-blockiert — eine dünne Datenlage ist erwartbar und kein Fehler.
- **Reddit / Community** — Datenquelle ist `audits/reddit-fit.md` (aus dem Reddit-Fit-Check), falls vorhanden. Fehlt die Datei, wird der Kanal mit Branchen-Fit-Default und Konfidenz `niedrig` bewertet — **nicht ausgelassen**.
- **KI-/Discovery-Sichtbarkeit (GEO)** — bewusst als **Multiplikator-Strang auf SEO und Content** zu kennzeichnen, **kein eigener Budgetposten**. GEO-Sichtbarkeit entsteht aus starkem SEO-/Content-Fundament, nicht aus separatem Spend. Im Output, in der strategischen Story und in der Top-3-Begründung explizit so benennen ("GEO ist ein Hebel auf SEO/Content, kein eigenständiger Kanal mit eigenem Budget"). Datenquelle ist der **optionale** Audit `audits/geo-sichtbarkeit.md` — der Audit kann fehlen. Fehlt er, wird GEO trotzdem bewertet, mit Branchen-Fit-Default und **Konfidenz `niedrig`** — nicht ausgelassen. Der Kanal landet im CSV mit `score`, nicht `skip`.

Keiner der drei Kanäle wird wegen fehlendem Audit übersprungen — sie werden mit niedriger Konfidenz bewertet, weil die bloße Bewertung (auch konservativ) für den Strategen Information ist.

Pro Kanal werden **fünf Achsen** auf einer 0-100-Skala bewertet. Die genauen Scoring-Regeln stehen in `reference/chancen-score-formel.md`. Kurz zusammengefasst:

- **`potenzial_score`** — wie groß ist der Markt für diesen Kanal? Quellen: SEO-Volumen, Ads-Spend-Range der Branche, Social-Reichweiten der WBs, GMB-Such-Volumen. Bei fehlenden Daten: branchen-typischer Default aus `branchen-fit-defaults.md` mit Konfidenz `niedrig`. **First-Party-Schärfung:** Liegt `ga4-first-party.md` mit dem Block `kanal_wertigkeit` vor, wird das Potenzial messbar statt geschätzt — ein Kanal, der laut GA4 schon echte Sessions plus eine ordentliche Conversion-Rate/Umsatz bringt, belegt ein reales Hebel-Potenzial; ein Kanal mit 0 oder kaum GA4-Beitrag, der branchen-typisch aber stark ist, zeigt echtes ungehobenes Aufholpotenzial (Default bleibt gültig, GA4 liefert nur den Ist-Beweis). Für SEA liest `sea-first-party.md` die echte Kampagnen-Performance (Spend-Größenordnung, ROAS) als Markt-Signal statt der geschätzten Branchen-Dichte. Die Achsen-Konfidenz folgt dem `belastbarkeit`-Gate (siehe Schritt 2): GA4 `gruen` → `hoch`, `gelb` → `mittel`, `rot` → `niedrig`/keine harte Ableitung.
- **`aufwand_score`** — wie hoch ist die Reibung im Kanal? **Invertiert**: 100 = niedriger Aufwand. Berücksichtigt Difficulty (SEO), Spend-Anforderung (Ads), Content-Frequenz (Social), Tech-Voraussetzungen (Tracking, CRO).
- **`briefing_fit_score`** — passt der Kanal zu den Zielen aus `data/briefing.md`? Mappe Briefing-Ziele auf Kanal-Eignung. Bei fehlendem Briefing: 50 (neutral).
- **`kunden_reife_score`** — wie weit ist der Kunde bereits aktiv im Kanal? Niedrig = großes Aufholpotenzial; sehr niedrig kann auch heißen "Tech-Lücke / Team-Lücke / nicht ready". Wird invertiert je nach Kontext — siehe Formel-Datei. **First-Party-Schärfung:** Liegt `ga4-first-party.md` vor, wird die Kunden-Reife datenbasiert statt geschätzt bestimmt — ein Kanal, der laut GA4 `kanal_wertigkeit` schon echte Sessions plus Conversions liefert, hat eine belegte, hohe Kunden-Reife (`reife_roh` aus dem GA4-Session-/Conversion-Beitrag statt aus Annahmen); ein potenzialstarker Kanal mit 0 GA4-Beitrag belegt echtes Aufholpotenzial statt einer bloßen Vermutung. Für SEA liefert `sea-first-party.md` die echte Konto-Aktivität (aktive Kampagnen, Spend) als `reife_roh`. Die Achsen-Konfidenz folgt dem `belastbarkeit`-Gate.
- **`branchen_fit_score`** — passt der Kanal zur Branche? Aus `branchen-fit-defaults.md` plus Override aus konkreten Audit-Daten (z. B. wenn 6 von 7 WBs auf TikTok aktiv sind, ist TikTok branchen-fit hoch, auch wenn Branche eher nicht TikTok-affin).

**Fallback ohne First-Party-Daten:** Fehlen `ga4-first-party.md` und `sea-first-party.md`, bleibt das bisherige Verhalten von `potenzial_score` und `kunden_reife_score` unverändert — geschätzt aus Branchen-Defaults und Wettbewerber-/Audit-Daten mit der bisherigen Konfidenz-Logik. Die First-Party-Schärfung ist ein Bonus, kein Blocker.

### Schritt 5: `chancen_score` berechnen

Aus den fünf Achsen wird der Gesamt-Score berechnet. Default-Formel (siehe `reference/chancen-score-formel.md` für Details und Branchen-Overrides):

```
chancen_score = (
    0.30 * potenzial_score
  + 0.20 * aufwand_score
  + 0.20 * briefing_fit_score
  + 0.10 * kunden_reife_inverse(score, kontext)
  + 0.20 * branchen_fit_score
)
```

Wobei `kunden_reife_inverse`:

- Bei `niedrig` Reife + hohem Potenzial → großes Hebel-Potenzial → hoher Achsen-Beitrag
- Bei `niedrig` Reife + niedrigem Branchen-Fit → wahrscheinlich Engpass → niedriger Achsen-Beitrag
- Bei `hoch` Reife → Kanal ist eher Status-Quo, nicht "Chance" → mittlerer Achsen-Beitrag

Konfidenz pro Achsen-Score (`hoch | mittel | niedrig`) wird mitgespeichert. Wenn mehr als 2 von 5 Achsen Konfidenz `niedrig`, wird auch der `chancen_score_konfidenz` als `niedrig` markiert.

### Schritt 6: Ranking und Top-3 ableiten

Sortiere alle Kanäle nach `chancen_score` absteigend. Wende Tiebreaker an (siehe Formel-Datei): bei gleichem Score gewinnt der mit höherem `briefing_fit_score`, dann `potenzial_score`.

Top-3 als prominente Empfehlungen herausziehen — pro Top-3 wird eine 3-4-Satz-Begründung formuliert:

- **Warum dieser Kanal jetzt?** (Hebel, Datenlage)
- **Was sind die konkreten Argumente?** (Belege aus den Audits)
- **Was ist die nächste konkrete Aktion?** (z. B. "Content-Hub für Cluster X aufbauen", "Conquest-Kampagne aktivieren")

### Schritt 7: Auffälligkeiten identifizieren

Mindestens **7 Auffälligkeiten** (siehe Reference-Datei für Details):

- `kanal_unterbespielt_kunde` — Kanal mit hohem Potenzial, Kunde inaktiv
- `kanal_branchen_chance` — Branchen-Lücke (kein WB spielt)
- `kanal_branchen_uebersaturiert` — alle WBs aktiv, hoher Aufwand
- `kanal_briefing_widerspruch` — Briefing zielt auf Kanal X, aber Daten zeigen Kanal Y stärker
- `kunden_reife_engpass` — Kanal hat Potenzial, aber Kunden-Reife (Tech, Team) ist niedrig
- `quick_win_kanal` — niedrige Difficulty + hohes Potenzial + niedriger Aufwand
- `kanal_zu_klein` — Branchen-Fit zu schwach für relevanten Hebel

**First-Party-Schärfung der Auffälligkeiten:** Wenn `ga4-first-party.md` vorliegt (und `belastbarkeit` nicht `rot`), werden die folgenden Auffälligkeiten aus echten Ist-Daten belegt statt geschätzt — im `beschreibung`-Feld dann konkret die GA4-Zahl nennen:

- `kanal_unterbespielt_kunde` — wird durch GA4 gehärtet: Kanal hat laut Branchen-Default/WB-Daten hohes Potenzial, aber `kanal_wertigkeit` zeigt für ihn 0 oder einen sehr geringen Session-Anteil → der Beleg ist nicht mehr eine Annahme, sondern die echte GA4-Zahl ("Kanal X liefert laut GA4 nur N% der Sessions trotz Branchen-Potenzial").
- `kunden_reife_engpass` — wird durch GA4/SEA gehärtet: ein potenzialstarker Kanal mit faktisch fehlendem GA4-Beitrag bzw. inaktivem Ads-Konto belegt die Reife-Lücke mit Ist-Daten statt mit einer Tech-Vermutung.
- `quick_win_kanal` — wird durch GA4 gehärtet: zeigt `kanal_wertigkeit` für einen Kanal eine bereits gute Conversion-Rate bei noch kleinem Session-Volumen, ist der Skalierungs-Quick-Win datenbelegt ("Kanal X konvertiert laut GA4 mit X,X%, hat aber erst N Sessions/Monat — Hebel ist Volumen, nicht CR").

Bei `belastbarkeit: rot` werden die GA4-Zahlen nur als grobe Orientierung erwähnt, nicht als harter Beleg. Fehlen die First-Party-Daten ganz, bleiben die Auffälligkeiten wie bisher geschätzt aus Branchen-Defaults und Wettbewerber-Daten.

Wenn weniger als 7 echte Auffälligkeiten aus den Daten ableitbar sind: ergänze um methodische Hinweise (z. B. "Datenbasis für Kanal X dünn — Folge-Audit empfohlen").

### Schritt 8: Strategische Story formulieren

Im Body der `kanal-chancen.md` ein narrativer Abschnitt (3-5 Sätze): Was sind die **1-2 größten Hebel** für diesen Kunden? Wie verhalten sich die Top-3 zueinander? Gibt es einen klaren Primär-Kanal, oder einen sinnvollen Mix?

Diese Story ist die Vorbereitung für die MTA-Slides (Briefing-Story-Slide vor dem Forecast).

### Schritt 9: Output schreiben — Markdown + CSV nach Drive

Erzeuge `synthese/kanal-chancen.md` und `synthese/kanal-chancen.csv` lokal nach dem Schema in `reference/kanal-chancen-output-schema.md` und lade nach Drive:

```bash
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "kanal-chancen.md" /tmp/kanal-chancen.md "text/markdown"
python3 "$DRIVE_PY" upsert-text "$SYNTHESE_ID" "kanal-chancen.csv" /tmp/kanal-chancen.csv "text/csv"
```

**Output-Reihenfolge (`contracts.md` Abschnitt 3):** zuerst `kanal-chancen.md` und `kanal-chancen.csv`, dann der HTML-Report (Schritt 10), **zuletzt** `status.md` (Schritt 11) — ein vorzeitig beendeter Lauf hinterlässt so vollständige, nutzbare Outputs.

**`basis_inputs` im Frontmatter (Pflicht, `contracts.md` Abschnitt 12):** Das Frontmatter von `kanal-chancen.md` trägt die Liste aller gelesenen Audit-/Synthese-Inputs mit ihrem `generiert_am`-Stempel — die Datenbasis, auf der die Synthese beruht:

```yaml
basis_inputs:
  - datei: audits/seo-cluster-zusammenfassung.md
    generiert_am: 2026-05-16T14:00:00Z
  - datei: audits/google-ads.md
    generiert_am: 2026-05-15T09:30:00Z
  - datei: audits/ga4-first-party.md
    generiert_am: 2026-05-16T11:00:00Z
```

Damit kann jeder nachgelagerte Synthese-Skill (`04-03` ff.) prüfen, ob `kanal-chancen.md` auf veralteten Audits steht.

### Schritt 10: HTML-Report

**Report-Bausteine + Validierung — Pflicht (siehe `contracts.md` Abschnitt 7):**

- `{{MAIN_CONTENT}}` wird ausschliesslich aus den fertigen Bausteinen in `${CLAUDE_PLUGIN_ROOT}/skills/01-01-mta-projekt-init/reference/report-bausteine.md` zusammengesetzt — Markup 1:1 kopieren, keine eigenen CSS-Klassen erfinden, kein inline-`style`, den `<style>`-Block der Shell nicht verändern.
- Vor dem Drive-Upload validieren: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-report.py" <lokaler-html-pfad> --shell`. Exit-Code 0 → hochladen. Exit-Code 1 → nicht hochladen, gemeldete Klassen/Platzhalter gegen `report-bausteine.md` korrigieren, erneut validieren.

Lies `_shell.html` aus Drive (`find_by_name(REPORTS_ID, "_shell.html")` → `read_text`). Ersetze Platzhalter (siehe `contracts.md` Abschnitt 7). Inhalt für `{{MAIN_CONTENT}}`:

- **Stat-Strip**: Anzahl bewerteter Kanäle, durchschnittlicher `chancen_score`, Top-Kanal, Audit-Coverage-Quote
- **Score-Heatmap**: Tabelle Kanal × Achse, Zellen farbcodiert (rot < 30, gelb 30-60, grün > 60). CSS-Klassen aus `_shell.html`.
- **Top-3-Karten**: pro Top-Kanal eine `.summary-card` mit Score, Begründung, nächster Aktion
- **Vollständige Kanal-Tabelle**: alle Kanäle nach Score sortiert, mit allen fünf Achsen
- **Auffälligkeiten**: als aufklappbare `<details>`-Blöcke
- **Strategische Story**: prominente `.summary-card` am Ende
- **Datenbasis-Hinweis**: welche Audits zur Verfügung standen, welche fehlten

Schreibe nach Drive via `drive.py upsert-text "$REPORTS_ID" "10-kanal-chancen.html" /tmp/report.html "text/html"`. Aktualisiere `reports/index.html` analog (lesen, patchen, upsert).

### Schritt 11: Status-Update

Folge `contracts.md` Abschnitt 3. `status.md` aus Drive lesen, patchen, via `drive.py upsert-text "$FOLDER_ID" "status.md" ... "text/markdown"` zurückschreiben:

- `04-02-kanal-chancen-analyse` in `schritte_done` aufnehmen, aus `schritte_offen` entfernen
- Body-Eintrag unter "✓ Erledigt"
- `naechster_empfohlen`: in der Regel `04-03-ziele-aus-potenzialen` (oder `04-04-forecast-modell` falls KPIs im Briefing genannt)

### Schritt 12: Schluss-Format im Chat

Standard-Schluss nach `contracts.md` Abschnitt 6. Bei dünner Datenbasis (weniger als 3 Audits) explizit warnen:

```
HINWEIS: Synthese auf dünner Datenbasis (N Audit-Skills gelaufen).
Empfohlen: weitere Audits laufen lassen und Skill neu aufrufen für robustere Empfehlung.
```

## Modi

- **Voll**: 5+ Audit-Skills durchgelaufen, Briefing vorhanden, kunde.md vorhanden — Default-Modus, alle Achsen mit hoher/mittlerer Konfidenz
- **Reduced**: 3-4 Audits — Skill läuft, aber fehlende Audits dokumentiert, einige Achsen mit niedriger Konfidenz
- **Dünn**: 0-2 Audits — Warnung, aber Skill läuft trotzdem (für sehr frühe Plausibilitäts-Checks)

## Edge Cases

- **Kunde ist nicht lokal-relevant**: Local-SEO/GMB-Kanal wird ausgeschlossen (Score nicht berechnet, im CSV `score: skip`)
- **Kein Briefing vorhanden**: `briefing_fit_score` = 50 (neutral), Konfidenz `niedrig`, Hinweis im Output
- **Sehr starker Wettbewerber-Cluster auf einem Kanal**: bei 6+ WBs aktiv und Spend-Range hoch → `branchen_uebersaturiert` setzen, `aufwand_score` reduzieren
- **Konflikt zwischen Briefing-Ziel und Daten**: explizit als `kanal_briefing_widerspruch` herausstellen — Stratege muss im Kunden-Gespräch klären
- **YouTube/Pinterest nicht relevant für Branche**: Branchen-Fit-Score sehr niedrig, Kanal landet automatisch im Ranking unten — nicht ausschließen, weil die Bewertung selbst Information ist
- **`audits/geo-sichtbarkeit.md` fehlt**: GEO-Kanal wird trotzdem bewertet — Branchen-Fit-Default, alle Achsen `konfidenz: niedrig`, im CSV `score` (nicht `skip`). GEO bleibt als Multiplikator-Strang auf SEO/Content gekennzeichnet, kein eigener Budgetposten
- **`audits/reddit-fit.md` fehlt**: Reddit/Community-Kanal wird mit Branchen-Fit-Default und Konfidenz `niedrig` bewertet — nicht ausgelassen
- **Facebook-Audit fehlt / login-wall-blockiert**: Facebook-organisch wird mit Branchen-Fit-Default und Konfidenz `niedrig` bewertet — dünne Datenlage ist erwartbar, kein Fehler
- **Apify-Scrape für Paid-Kanäle unvollständig**: `apify_konfidenz_flag: niedrig_ohne_apify` für SEA/Meta-Ads setzen, Achsen-Konfidenz `niedrig`, Hinweis im Output — Paid-Scores können ohne Display-/Video-Daten 5–10 Punkte zu niedrig liegen. Kanal bleibt im Ranking
- **`reports/_shell.html` fehlt auf Drive**: Hinweis im Schluss-Format, HTML-Report wird trotzdem als minimaler Plain-HTML-Stub geschrieben und hochgeladen

## Reference-Dateien

- `reference/chancen-score-formel.md` — die fünf Achsen, ihre Score-Berechnung pro Kanal mit konkreten Quellen aus den Audits, die Aggregations-Formel, Tiebreaker, Konfidenz-Regeln
- `reference/branchen-fit-defaults.md` — Branchen × Kanal-Matrix mit Default-Branchen-Fit-Scores, Begründungen, Override-Regeln aus konkreten Audit-Daten
- `reference/kanal-chancen-output-schema.md` — exakte Definition der Markdown-Frontmatter-Struktur, des CSV-Schemas und der HTML-Sektionen
