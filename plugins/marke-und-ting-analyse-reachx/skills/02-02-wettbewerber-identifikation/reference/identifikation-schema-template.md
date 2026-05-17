# Identifikations-Schema-Template

Format der Phase-A-Output-Datei `wettbewerber/identifikation-schema.md`. Diese Datei wird vom Skill in Phase A generiert und muss vom Strategen reviewt werden, bevor Phase B (die eigentliche Wettbewerber-Recherche) läuft.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 02-02-wettbewerber-identifikation
phase: A
generiert_am: <ISO-8601>
schema_version: "1.0"
status: vorgeschlagen   # Stratege ändert nach Review zu: bestaetigt

# === Recherche-Konfiguration ===

# Seed-Keywords für Sistrix-Toplist-Recherche
# Diese Keywords definieren, in welchem Markt-Segment der Skill nach Best-Practice-Wettbewerbern sucht
# 3-5 Keywords, möglichst spezifisch für die Branche, aber generisch genug für Sistrix
# seed_keywords_quelle: gsc        → aus echten GSC-Non-Brand-Top-Queries des Kunden abgeleitet (höhere Treffsicherheit)
#                       abgeleitet → aus Briefing/Branche abgeleitet (First-Party-Daten lagen nicht vor)
seed_keywords_quelle: <gsc | abgeleitet>
branchen_seed_keywords:
  - <keyword 1>
  - <keyword 2>
  - <keyword 3>

# Relevante Branchenportale für diese Branche
# Aus branchenportale-mapping.md ableiten + ggf. branchen-spezifisch ergänzen
# Diese Portale werden NICHT als Wettbewerber, sondern als eigenständige Touchpoints behandelt
relevante_branchenportale:
  - portal: <Portal-Name>
    url: <Haupt-URL>
    relevanz: <hoch | mittel | niedrig>
    begruendung: <warum dieses Portal in dieser Branche relevant ist>

# Region-Definition für die regionale Wettbewerbs-Recherche
region_definition:
  primaer: <z.B. "Bad Homburg, Köppern, Kronberg" für Avadent>
  radius_km: <int, z.B. 25 für lokale Dienstleister, 0 für national>
  ausdehnung: <lokal | regional | national | dach | international>
  begruendung: <warum diese Region — aus Kunden-Standort und Reichweite des Geschäftsmodells>

# Filter für "erkennbares Online-Marketing"
# Welche Schwellwerte gelten für einen Wettbewerber, damit er es in die Liste schafft?
# Ohne diesen Filter wird die Liste zu Best-Practice rauschen
filter_online_marketing:
  sistrix_visibility_min: 0.05   # Default-Schwellwert, je nach Branche anpassen
  alternative_signale_ausreichend:
    - aktive_google_ads
    - aktive_meta_ads
    - aktiver_linkedin_account_mit_posts
  begruendung: <warum dieser Schwellwert für die Branche realistisch>

# Aggregatoren-Blocklist (Zusatz zur Standard-Blocklist)
# Welche zusätzlichen Akteure sollen aus den Toplisten gefiltert werden,
# die nicht in der Standard-aggregatoren-blocklist.md stehen?
aggregatoren_blocklist_zusatz:
  - <Domain 1>
  - <Domain 2>

# === Anzahl-Targets ===
ziel_anzahl:
  best_practice_ueberregional_max: 5   # Default: max 3-5
  regional_max: 10                      # Default: max 10
  brifing_genannt_alle: true            # immer alle aus dem Briefing aufnehmen

# === Optional: vom Briefing übernommene Wettbewerber ===
# Wird automatisch aus briefing.md gefüllt — Stratege kann ergänzen oder streichen
vom_briefing_uebernommen:
  - name: <Wettbewerber-Name>
    quelle_turn: <timestamp im Briefing>
    bedrohungsgrad_aus_briefing: <direkt | indirekt | inspiration>

# === Optional: First-Party-Akteurs-Hinweise (GA4-Referral) ===
# Wird automatisch aus der GA4-source/medium-Analyse (audits/ga4-first-party.md) gefüllt, falls 03-18 gelaufen ist.
# Fremd-Domains mit relevantem Referral-Traffic, die KEINE bekannten Portale/Bewertungsplattformen/
# Social-Netze/Suchmaschinen sind — potenzielle Wettbewerber-Kandidaten.
# Stratege prüft: unzutreffende Domains streichen. Bestätigte Domains durchlaufen in Phase B
# den normalen Website-Check + Signal-Check und werden in die passende bestehende Kategorie
# (regional bzw. best_practice_ueberregional) einsortiert — mit Vermerk quelle_zusatz: first_party_signal.
# Leer lassen, wenn keine GA4-Daten vorlagen.
first_party_hinweise:
  - domain: <Referral-Domain>
    referral_sessions: <int — Sessions aus GA4, aktuelle Periode>
    begruendung: <warum als Akteurs-Kandidat aufgenommen — z.B. "Fremd-Domain mit relevantem Referral-Traffic, kein bekanntes Portal/Social/Suchmaschine">
---

# Identifikations-Schema: <Kundenname>

## Begründung der Seed-Keywords

Quelle dieser Keywords: **<gsc | abgeleitet>**.

- Bei `gsc`: aus den echten GSC-Non-Brand-Top-Queries des Kunden abgeleitet (Output von `03-04-seo-first-party-gsc`). Vorteil: der Markt wird aus den realen Suchanfragen des Kunden bestimmt statt geraten — höhere Treffsicherheit der Toplist-Recherche.
- Bei `abgeleitet`: aus Briefing + kunde.md + Branche abgeleitet (First-Party-Daten lagen nicht vor). Eine vorherige First-Party-Erhebung (GSC) würde die Keyword-Qualität deutlich verbessern.

Warum genau diese 3-5 Keywords? Beleg-Logik:

1. **<keyword 1>**: <warum dieses Keyword — bezug zum Portfolio bzw. zur GSC-Query>
2. **<keyword 2>**: <…>
3. **<keyword 3>**: <…>

## First-Party-Akteurs-Hinweise (GA4-Referral)

<Wenn 03-18-web-analytics-ga4 gelaufen ist: Liste der Fremd-Domains mit relevantem Referral-Traffic, die kein bekanntes Portal/Social/Suchmaschine sind. Pro Domain Referral-Sessions und Begründung. Hinweis an den Strategen: bitte die Liste durchgehen und Domains streichen, die offensichtlich keine Wettbewerber sind — die verbleibenden werden in Phase B geprüft.>

<Wenn keine GA4-Daten vorlagen: "Keine GA4-Referral-Daten verfügbar — Sektion leer. Eine vorherige Erhebung mit 03-18-web-analytics-ga4 würde zusätzliche Akteurs-Kandidaten aus dem echten Referral-Traffic liefern.">



## Begründung der Region

<Erklärung, warum diese Region-Definition gewählt wurde — z.B. weil der Kunde primär lokal arbeitet, oder weil das Geschäftsmodell national ausgerichtet ist.>

## Begründung des Online-Marketing-Filters

<Erklärung des Schwellwerts und warum die alternativen Signale ausreichen.>

## Pflicht-Review durch den Strategen

Bitte folgende Punkte prüfen, bevor Phase B startet:

- [ ] **Seed-Keywords**: decken sie wirklich die Hauptmärkte des Kunden ab, oder fehlen Cluster? (Bei `seed_keywords_quelle: gsc` aus echten Queries — bei `abgeleitet` geraten, kritischer prüfen.)
- [ ] **Branchenportale**: ist die Liste vollständig für diese Branche? Fehlt ein wichtiges Portal?
- [ ] **Region**: deckt die Definition den geographischen Aktionsradius wirklich ab?
- [ ] **Online-Marketing-Filter**: ist der Schwellwert realistisch — nicht zu hoch (verliert echte Wettbewerber), nicht zu niedrig (zu viel Rauschen)?
- [ ] **Vom Briefing übernommene Wettbewerber**: alle aufgenommen, oder noch welche ergänzen?
- [ ] **First-Party-Hinweise**: sind die GA4-Referral-Domains plausible Wettbewerber-Kandidaten? Offensichtliche Nicht-Wettbewerber (Partner, Verzeichnisse, technische Referrer) streichen.

**Nach dem Review:** Setze `status: bestaetigt` im Frontmatter, dann läuft Phase B.
```

## Wann welche Werte gesetzt werden

### Seed-Keywords

**Primärquelle, wenn `audits/gsc-performance.csv` vorliegt** (Output von `03-04-seo-first-party-gsc`): die echten Non-Brand-Top-Queries des Kunden nach Klicks/Impressionen — Brand-Queries (Marken-Name + Synonyme) ausgeschlossen. Dann `seed_keywords_quelle: gsc`.

**Fallback, wenn keine GSC-Daten vorliegen** — Quellen für die Generierung in Phase A:

1. Aus `data/briefing.md`: `produkte_dienstleistungen` (Kategorie + Name)
2. Aus `data/kunde.md`: `portfolio_wie_kommuniziert.kategorie`
3. Aus `meta.json`: `branche` (für branchen-generische Keywords)

Pragmatisch: 1-2 Keywords sind sehr spezifisch (Produktkategorie), 1-2 sind branchen-generisch (für Sistrix-Toplist). Dann `seed_keywords_quelle: abgeleitet`.

### First-Party-Hinweise

Quelle: die GA4-source/medium-Analyse aus `audits/ga4-first-party.md` (Output von `03-18-web-analytics-ga4`). Der Skill scannt die Top-Referral-Domains und nimmt alle auf, die KEINE bekannten Portale/Bewertungsplattformen/Social-Netze/Suchmaschinen sind (Abgleich u. a. mit `aggregatoren-blocklist.md`). Pro Kandidat `domain`, `referral_sessions`, `begruendung`. Leer lassen, wenn `03-18` nicht gelaufen ist. Der Stratege kuratiert die Liste; bestätigte Domains werden in Phase B geprüft und ggf. mit `quelle_zusatz: first_party_signal` in `regional` oder `best_practice_ueberregional` einsortiert — es entsteht keine neue Kategorie.

**Beispiel Aufmaster:**

```yaml
branchen_seed_keywords:
  - kabel messen tool         # spezifisch zum Produkt
  - aufmaß handwerker          # spezifisch zum Anwendungsfall
  - kabel handwerksbedarf      # branchen-generisch
  - elektrotechnik werkzeug    # branchen-generisch
```

### Region-Definition

Quellen:

1. Aus `meta.json`: `region`
2. Aus `data/briefing.md`: `regionen`
3. Aus `data/kunde.md`: Indikatoren in den Touchpoints (GMB-Standorte, lokale Verweise)

Faustregel:

- Lokale Dienstleister (Arzt, Anwalt, Restaurant, Hausverwaltung): `radius_km: 15-30`, `ausdehnung: lokal`
- Regionale B2B-Mittelständler: `ausdehnung: regional`, evtl. mehrere Großstädte/Regionen
- Nationale / DACH-Produkt-Anbieter: `radius_km: 0`, `ausdehnung: national` oder `dach`
- Globale B2B-SaaS / E-Commerce: `ausdehnung: international` (dann ggf. mehrere Sprachen)

### Online-Marketing-Filter

Default-Schwellwerte (vom Skill in Phase A als Vorschlag gesetzt):

| Branchen-Typ | Sistrix Visibility min | Alternative-Signale-Mindestens |
|---|---|---|
| B2C Mainstream (Hotels, E-Commerce, Retail) | 0.10 | 2 von 3 |
| B2B Mittelstand | 0.05 | 1 von 3 |
| B2B Nische / Spezialprodukte | 0.02 | 1 von 3 |
| Lokale Dienstleister | 0.01 | GMB-Profil zählt als Signal |

Strateg kann anpassen, wenn er die Branche besser kennt.

### Anzahl-Targets

Standard-Werte halten, außer es gibt einen guten Grund:

- **best_practice_ueberregional_max: 5** — mehr wird zu viel zum Profilieren; Stratege kuratiert
- **regional_max: 10** — typische Größenordnung für eine regionale Recherche; Stratege wählt aus
- **brifing_genannt_alle: true** — was der Kunde nennt, gehört immer rein, unabhängig vom Filter

## Validierungs-Regeln

Vor dem Lauf von Phase B prüft der Skill:

1. `status: bestaetigt` im Frontmatter? Sonst Abbruch mit Hinweis "Schema noch nicht reviewt"
2. `branchen_seed_keywords` enthält mindestens 2 Einträge? Sonst Abbruch
3. `region_definition.ausdehnung` gesetzt? Sonst Abbruch
4. `filter_online_marketing.sistrix_visibility_min` gesetzt und numerisch? Sonst Default 0.05

Wenn eine Validierung fehlschlägt, gibt der Skill **konkret an, welches Feld** korrigiert werden muss, statt eine generische Fehlermeldung.

## Edge Case: keine `kunde.md`

Wenn `02-01-kunden-marken-profil` noch nicht gelaufen ist:

- Schema kann trotzdem generiert werden, basiert dann nur auf `briefing.md` und `meta.json`
- Hinweis im Schema-Body: *"`kunde.md` fehlt — Seed-Keywords nur aus Briefing abgeleitet. Empfohlen: `02-01-kunden-marken-profil` zuerst, dann Schema neu generieren."*
- Der Stratege kann das Schema bestätigen und Phase B laufen lassen — auf eigene Verantwortung, weil die Keyword-Auswahl weniger fundiert ist
