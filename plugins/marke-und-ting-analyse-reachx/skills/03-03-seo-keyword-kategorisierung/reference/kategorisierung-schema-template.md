# Schema-Template für `audits/keyword-kategorisierung-schema.md`

Format des Phase-A-Outputs. Der Skill schreibt diese Datei mit `status: vorgeschlagen`, der Stratege reviewt und setzt `status: bestaetigt`, dann läuft Phase B.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 03-03-seo-keyword-kategorisierung
phase: A
generiert_am: <ISO-8601>
schema_version: "1.0"
status: vorgeschlagen   # Stratege bestätigt nach Review → bestaetigt

# === Basis (was wurde gelesen) ===
basiert_auf:
  pool_csv: audits/seo-keyword-pool.csv
  pool_md: audits/seo-keyword-pool.md
  pool_groesse: <int>
  kunde_md: data/kunde.md          # null wenn nicht vorhanden
  identifikation_schema: wettbewerber/identifikation-schema.md   # null wenn nicht vorhanden
  briefing: data/briefing.md       # null wenn nicht vorhanden
nutzung_ahrefs_parent_topics: <ja | nein | optional>   # Default optional

# === Branchen-Typ (Stratege kann editieren) ===
branchen_typ: <lokal_dienstleister | b2b_mittelstand | b2c_ecommerce | b2b_saas | content_publisher | sonstige>
branchen_kontext_kurz: <1-2 Sätze: was macht der Kunde, welche Sucher kommen?>

# === Cluster-Vorschläge ===
cluster:
  - name: branded_kunde
    typ: branded
    beschreibung: Kunden-Markensynonyme und nahe Variationen
    anker_token:
      - <synonym 1>
      - <synonym 2>
    geschaetzte_groesse: <int>
    intent_default: branded
    funnel_default: BOFU   # Brand-Searches sind meist Kauf-nah
    quelle: marke_synonyme_aus_kunde_md
    notiz: <z.B. "Aufgepasst: Markenname auch generisches Wort, prüfen">
    
  - name: branded_wettbewerber_<wb_slug>
    typ: branded
    beschreibung: Markensynonyme von <Wettbewerber-Name>
    anker_token: [<wb name token>]
    geschaetzte_groesse: <int>
    intent_default: branded
    funnel_default: BOFU
    quelle: wb_marken_aus_liste_md
    notiz: <optional>
    
  # ... weitere branded_wettbewerber_X Cluster ...
  
  - name: <produkt_oder_thema_slug>
    typ: produkt | anwendung | gap_cluster | longtail | generic
    beschreibung: <1 Satz>
    anker_token: [<liste>]
    geschaetzte_groesse: <int>
    intent_default: <enum>
    funnel_default: <TOFU | MOFU | BOFU>
    quelle: <token_frequenz | portfolio_kategorie | gap_cluster_auffaelligkeit | ahrefs_parent_topic | manuell>
    notiz: <optional, z.B. "Stark Gap-belastet, sehr strategie-relevant">

  # ... weitere Cluster ...

  - name: generic
    typ: fallback
    beschreibung: Keywords ohne klare Cluster-Zuordnung — Sammelbecken
    anker_token: []
    geschaetzte_groesse: <int — Schätzung aus Pool>
    intent_default: unklar
    funnel_default: TOFU
    quelle: fallback

# === Intent-Typen (Standard + Branchen-Anpassung) ===
intent_typen:
  branded:
    beschreibung: Marken-Searches (Kunde oder WB)
    trigger_token: [<keine — wird über cluster_typ: branded ausgelöst>]
    branchen_anpassung: <z.B. "Bei B2B-SaaS: Brand-Demo-Anfragen zählen trotzdem als transactional">
  
  transactional:
    beschreibung: konkrete Kauf- oder Buchungs-Absicht
    trigger_token: [kaufen, preis, bestellen, shop, angebot, rabatt, günstig, bestpreis, online kaufen, demo buchen, termin buchen]
    branchen_anpassung: <z.B. "Bei B2B: 'demo', 'termin', 'angebot anfordern' zählt als transactional">
  
  commercial:
    beschreibung: Vergleichs- und Recherche-Absicht vor Kauf
    trigger_token: [test, vergleich, vs, erfahrungen, bewertung, beste, ranking, alternativen zu]
    branchen_anpassung: <optional>
  
  informational:
    beschreibung: Wissens-/Lern-Suche
    trigger_token: [was ist, wie funktioniert, anleitung, tipps, guide, tutorial, w-frage-pattern]
    branchen_anpassung: <z.B. "Bei Lifestyle-Brands: How-to-Pattern besonders relevant">
  
  navigational:
    beschreibung: Suche nach einer konkreten Marke / URL ohne Kauf-Signal
    trigger_token: [<sehr kurz, oft nur 1-2 Wörter>]
    branchen_anpassung: <optional>
  
  unklar:
    beschreibung: keine eindeutige Zuordnung
    trigger_token: []

# === Funnel-Stufen-Mapping (Standard + Cluster-Override-Hinweise) ===
funnel_mapping:
  default_aus_intent:
    branded: BOFU
    transactional: BOFU
    commercial: MOFU
    informational: TOFU
    navigational: BOFU   # wenn der User die Marke gezielt sucht, ist er nah am Kauf
    unklar: TOFU         # konservativ
  
  cluster_overrides:
    # Pro Cluster optional einen Funnel-Override definieren
    - cluster: <cluster_slug>
      funnel: <stufe>
      grund: <warum dieser Cluster trotz seiner Intent-Verteilung einer anderen Funnel-Stufe zugeordnet wird>

# === Konfidenz-Schwellen für Phase B ===
konfidenz:
  hoch_bei: "genau ein Anker-Token gematcht ODER branded-Match"
  mittel_bei: "mehrere Anker-Tokens gematcht (mehrere Cluster passen)"
  niedrig_bei: "nur Fallback generic oder Ahrefs-Parent-Topic ohne Anker"

# === Cluster-Score-Konfiguration ===
cluster_score:
  abdeckung_kunde_faktor:
    abdeckung_hoch: 0.5    # > 50% Top-10
    abdeckung_mittel: 1.0
    abdeckung_null: 1.5    # 0% + WB stark
  difficulty_bonus:
    sweet_spot: 1.4        # Median-Difficulty <= 30
    standard: 1.0
---

# Cluster-Schema für SEO-Keyword-Kategorisierung: <Kundenname>

## Übersicht

3-5 Sätze: Pool-Größe, Anzahl Cluster-Vorschläge, Branchen-Typ, Top-1-2-Beobachtungen aus der Vor-Analyse.

## Pool-Vor-Analyse

| Kennzahl | Wert |
|---|---|
| Pool-Größe | N Keywords |
| Davon Branded (heuristisch) | M |
| Davon Gaps zum Kunden | G |
| Davon mit Difficulty angereichert | D |
| Top-Tokens nach Frequenz | aufmaß (47), kabel (32), werkzeug (28), ... |
| Top-3 Ahrefs-Parent-Topics (falls vorhanden) | "Cable Tools" (45), "DIY Tools" (32), "Industrial Tools" (18) |

## Cluster-Vorschläge

Pro Cluster: Name, Beschreibung, Anker-Tokens, geschätzte Größe, Default-Intent, Default-Funnel, Quelle, Notiz.

### 1. branded_kunde

(Details aus Frontmatter rendered)

### 2. <produkt-cluster>

(...)

(... weitere Cluster ...)

## Intent-Typ-Definitionen

(Detaillierte Begründung der Trigger-Token-Listen und Branchen-Anpassungen — Stratege kann hier inhaltlich editieren)

## Funnel-Stufen-Mapping

(Default-Tabelle Intent → Funnel plus die vorgeschlagenen Cluster-Overrides mit Begründung)

## Pflicht-Review durch den Strategen

Bevor Phase B läuft, bitte prüfen:

1. **Cluster-Namen und -Beschreibungen** — sind sie für die MTA-Story strategisch verständlich? Würdest du sie so auf einer Slide stehen sehen?
2. **Anker-Tokens** — decken sie die intendierten Keywords ab? Fehlen wichtige Synonyme?
3. **Cluster-Anzahl** — zu viele (>20 wird unübersichtlich) oder zu wenige (<5 ist meist zu grob)?
4. **Cluster zusammenlegen / splitten** — manchmal sind zwei Cluster eigentlich einer (z. B. "Aufmaß" und "Aufmaß-Werkzeuge" sollten zusammen), manchmal versteckt ein Cluster zwei Themen
5. **Intent-Trigger-Token** — passen die Default-Heuristiken zur Branche? Manche Branchen haben Eigen-Sprache (z. B. B2B-SaaS: "demo" ist eher commercial als transactional)
6. **Funnel-Mapping** — sollte ein Cluster vom Intent-Default abweichen? Im `cluster_overrides` ergänzen
7. **Branded-Cluster** — sind alle Marken-Synonyme korrekt? Fehlt ein wichtiger WB?

**Nach dem Review**: Setze `status: bestaetigt` im Frontmatter, dann läuft Phase B.

## Notizen für Phase B

Frei-Text-Feld, in dem der Stratege im Review Hinweise hinterlassen kann, z. B.:

- "Cluster X erstmal nur grob — wir verfeinern nach MTA-Präsentation"
- "Achtung: Keyword Y ist mehrdeutig, prüfe in der Output-CSV manuell"
- "Wenn `unklar`-Cluster groß wird, ist das OK — wir filtern später"
```

## Default-Cluster-Templates pro Branchen-Typ

Pro Branchen-Typ ein Vorschlag für Standard-Cluster, die der Skill vorschlagen kann (zusätzlich zu den dynamisch aus dem Pool generierten Clustern):

### lokal_dienstleister (z. B. Hausverwaltung, Arzt, Handwerk)

- `branded_kunde`
- `dienstleistung_kern` (z. B. "hausverwaltung berlin", "zahnarzt münchen")
- `notfall_keywords` (z. B. "rohrbruch sofort", "zahnschmerz notfall")
- `service_variationen` (z. B. "wohnung verwalten lassen", "wohnung mieten verwalten")
- `local_modifier_cluster` (Keywords mit Ortsnamen)
- `informations_keywords` (z. B. "was kostet hausverwaltung")

### b2b_mittelstand

- `branded_kunde`
- `produkt_kategorie_1`, `produkt_kategorie_2`, ... (aus Portfolio)
- `branchen_loesungen` (z. B. "lösung für maschinenbau")
- `vergleich_und_test` (Mid-Funnel)
- `informations_keywords` (Top-Funnel, "wie funktioniert X")

### b2c_ecommerce

- `branded_kunde`
- `produkt_kategorie_X`
- `transactional_keywords` ("kaufen", "shop", "online bestellen")
- `vergleich_und_test`
- `informations_keywords`
- `saisonal_oder_trend` (wenn Trend-Keywords im Pool)

### b2b_saas

- `branded_kunde`
- `funktions_keywords` ("X verwalten", "X tool")
- `vergleich_und_alternativen` ("alternative zu X", "X vs Y")
- `integration_und_workflow` ("X mit Y verbinden")
- `pricing_und_demo` ("X preis", "X demo")
- `informations_keywords` ("was ist X")

### content_publisher / Medien

- `branded_kunde`
- `themen_cluster_1`, `themen_cluster_2` (aus Content-Schwerpunkten)
- `aktuelle_ereignisse` (Trend-Keywords)
- `evergreen_themen`

### sonstige

- Skill versucht die dynamische Cluster-Bildung allein und schreibt im Body Hinweis "Branchen-Typ nicht vordefiniert — Cluster sind rein heuristisch, Strategen-Review besonders wichtig"

## Hinweise zur Schema-Pflege

- Bei Skill-Versionierung (Schema-Änderungen) wird `schema_version` hochgesetzt
- Bei MTA-Projekt-Re-Run mit Schema-Änderung: alte Phase-B-Outputs nach `_backup/` schieben, Schema-Status zurück auf `vorgeschlagen`, Stratege bestätigt erneut
