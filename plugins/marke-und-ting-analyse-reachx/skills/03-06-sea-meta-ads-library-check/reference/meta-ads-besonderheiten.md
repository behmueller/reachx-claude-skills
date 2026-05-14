# Meta-Ads-Besonderheiten gegenüber Google Ads

Konzeptuelle Eigenheiten der Meta Ad Library, die im Output sichtbar gemacht und im Strategen-Gespräch berücksichtigt werden müssen. Diese Datei beschreibt das **Was bedeutet das eigentlich**-Wissen für den Skill — die operativen URL-/Actor-Details liegen in `ad-library-mapping.md`.

## 1. Page-zentrisch statt Domain-zentrisch

Google's Transparency Center indiziert Werbetreibende über die **Domain** (`mustermann.de`). Die Meta Ad Library indiziert über die **Facebook-Page-ID** (`view_all_page_id=NUMMER`).

**Konsequenzen für den Skill:**

- Pro Akteur muss eine Page-ID aufgelöst werden, bevor irgendetwas gescraped werden kann (siehe `ad-library-mapping.md` Abschnitt "Page-Resolution")
- Ein Akteur kann mehrere Pages haben (Marke, Shop, Service, Karriere) — der Skill arbeitet per Default mit **einer Standard-Page** (aus Marken-Profil), unterstützt aber Multi-Page-Override
- Ein Akteur kann **gar keine Page** haben (Edge Case, besonders B2B-Industrie, Handwerk) — das ist eine eigenständige strategische Aussage

**Page-Match-Problem (häufiger als gedacht):**

Bei einem typischen MTA-Lauf mit 5-7 Wettbewerbern kommen folgende Konstellationen vor:

| Konstellation | Häufigkeit | Behandlung |
|---|---|---|
| Eindeutige Page mit FB-URL im Marken-Profil | typisch 50-70% | Stufe-1-Resolution, Konfidenz hoch |
| Mehrere Pages, eine klar dominant | typisch 10-20% | Stufe-3-Resolution mit Heuristik, Konfidenz mittel |
| Page existiert, aber nur Stamm-Seite ohne Werbung | typisch 10-20% | Page-ID resolved, `aktiv_in_ad_library: false` |
| Keine Page identifizierbar | typisch 5-15% | `facebook_page_id: null`, Hinweis und ggf. Auffälligkeit |

**Wichtig:** Wenn der **Kunde** keine Page hat, ist das ein zentrales MTA-Insight — gehört prominent ins Schluss-Format und als Auffälligkeit (`keine_meta_praesenz`).

## 2. Multi-Plattform-Anzeigen

Eine einzige Meta-Anzeige läuft **gleichzeitig auf mehreren Surfaces**:

- Facebook Feed
- Facebook Stories und Reels
- Instagram Feed
- Instagram Stories und Reels
- Messenger
- Audience Network (externe Apps)

Das ist anders als bei Google, wo Anzeigentypen disjunkt sind (Search-Ad ≠ Display-Ad ≠ Video-Ad).

**Konsequenzen für den Skill:**

- `plattformen` ist eine **Liste**, nicht ein Single-Value
- Im CSV als kommagetrennte Liste (`facebook,instagram`)
- Im Markdown-Frontmatter als YAML-Liste
- Für die Plattform-Verteilungs-Statistik werden Anzeigen pro Plattform separat gezählt (eine Anzeige mit `facebook,instagram` zählt für beide Spalten)

**Strategisch relevant:**

- Akteure mit reiner Instagram-Schaltung signalisieren visuell-getriebenen Markenauftritt und jüngere Zielgruppe
- Akteure mit reiner Facebook-Schaltung signalisieren klassischen oder älteren Markenauftritt
- Audience-Network-Nutzung deutet auf Performance-Marketing-Fokus (Effizienz vor Markenkontrolle)
- "Balanced" (FB+IG zu etwa gleichen Teilen) ist der häufigste und meist defensivste Mix

## 3. EU-DSA-Pflicht für politische und gesellschaftliche Anzeigen

Seit dem Digital Services Act (DSA, EU, in Kraft 2024) müssen alle politischen und gesellschaftlichen Anzeigen in der Meta Ad Library mit erweiterten Transparenz-Daten ausgewiesen werden:

- **Reach-Range** (geschätzte Impressionen, untere und obere Grenze)
- **Spend-Range** (Werbe-Ausgaben in EUR, untere und obere Grenze)
- **Demographics** (Alter, Geschlecht, Region — aufgeschlüsselt)
- **Werbender** (rechtliche Identität, finanzierende Organisation)

**Was zählt als "politisch oder gesellschaftlich"?**

Metas eigene Klassifikation, inkludiert:

- Parteipolitik, Wahl-Kampagnen
- Gesellschaftliche Themen (Umwelt, Soziales, Gesundheit, Migration etc.)
- Werte-getriebene Markenkampagnen mit politischer Anlehnung
- NGO-/Verbands-Werbung

**Konsequenzen für den Skill:**

- Politische Anzeigen sind in der Ad Library separat zugänglich (`ad_type=political_and_issue_ads`)
- Werden im normalen Scrape mit erfasst (Standard `ad_type=all`), aber im Output **separat aggregiert**
- DSA-Daten kommen als Sub-Block `dsa_block` pro Akteur und als CSV-Spalten `dsa_*`
- Auffälligkeit `dsa_aktivitaet` triggern, wenn relevant (besonders bei Unternehmen mit gesellschaftlicher Positionierung — kann strategischer Hinweis sein)

**Für die MTA-Story:**

Politische Anzeigen sind bei B2B-Mittelstand und Handwerk fast nie relevant. Bei NGOs, Verbänden, Gewerkschaften, Bildungseinrichtungen, manchmal auch bei Marken mit aktivistischem Positionings-Anspruch (Patagonia-Style) — dann wird der DSA-Block zur eigenständigen Story-Achse.

## 4. Creative-Format-Vielfalt

Meta unterscheidet mehr Creative-Formate als Google, mit unterschiedlichen strategischen Implikationen:

| Format | Beschreibung | Strategische Bedeutung |
|---|---|---|
| Single Image | Statisches Bild plus Text | Standard, einfach zu produzieren, schwächste Engagement-Raten |
| Single Video | Video plus Text | Höhere Engagement-Raten, teurer in Produktion |
| Carousel | 2-10 swipebare Karten | Hohe Engagement-Raten, Storytelling-Format, Produkt-Showcases |
| Collection | Hero-Asset plus mehrere Tile-Items | Mobile-First Shopping-Format, Katalog-orientiert |
| Dynamic Product Ads (DPA) | Automatisch generiert aus Produkt-Feed | Performance-Marketing, Retargeting |
| Slideshow | Mehrere Bilder als Quasi-Video | Günstige Video-Alternative für Low-Bandwidth-Märkte |
| Stories und Reels Ads | Vertikale Video-Spots | Junge Zielgruppen, Brand-Awareness |

**Was der Skill daraus macht:**

- `anzeigentypen_verteilung` pro Akteur zeigt Format-Mix
- Auffälligkeit `format_einseitigkeit_branche` wenn mehr als 70% der Branchen-Anzeigen Single-Image sind (Video- oder Carousel-Differenzierung möglich)
- Im HTML-Report eine Format-Mix-Heatmap (Akteur x Format)

## 5. Werbetexte sind reicher und granularer

Eine Meta-Anzeige hat **mehrere Text-Felder**, anders als eine Google-Search-Ad mit ihren disjunkten Headlines:

- `werbetext_primary` — der Haupt-Text über dem Creative (frei strukturierbar, kann Emojis, Hashtags, Zeilenumbrüche enthalten)
- `werbetext_headline` — die Headline unter dem Creative (eng am Klick-CTA)
- `werbetext_beschreibung` — die Description unter der Headline (kurz, oft Domain oder Subline)
- `cta_button` — der definierte CTA-Button ("Mehr erfahren", "Jetzt einkaufen", "Demo buchen", "App-installieren")

**Was der Skill daraus macht:**

- Alle drei Texte separat in der CSV
- Für die Cluster-Heuristik (Schritt 6) wird primär `werbetext_primary` plus `werbetext_headline` genutzt
- Im HTML-Report Top-Anzeigen mit allen drei Texten plus CTA-Button

## 6. Anzeigen-Aktivität ist granularer dokumentiert

Anders als Google's TC liefert Meta:

- Genaues Datum der ersten Auslieferung
- Genaues Datum der letzten Auslieferung (bei gestoppten Anzeigen)
- Manchmal: Pausen-Zeiträume (rare, nur bei sehr alten Anzeigen sichtbar)
- "Aktiv seit X Tagen" als visueller Hinweis

**Konsequenz:**

`erst_schalt_datum` und `letzte_anzeige_datum` sind verlässlicher als bei Google. Im Aggregat `aelteste_schalt_datum` und `juengste_schalt_datum` pro Akteur ausweisen.

## 7. Kein Spend-Drittanbieter nötig (bei DSA-Anzeigen)

Für politische Anzeigen liefert Meta die Spend-Range direkt — kein SpyFu-Lookup nötig.

Für normale Anzeigen gibt es keine zuverlässige Spend-Schätzung von Drittanbietern (anders als bei Google, wo SpyFu/SEMrush Domain-Lookups bieten). Meta-Spend-Schätzungen einzelner Werbetreibender sind im Markt notorisch unzuverlässig.

**Konsequenz für den Skill:**

- Kein SpyFu-Block bei Meta (im Gegensatz zu `03-05-sea-google-ads-check`)
- Spend-Aggregat nur für DSA-Bereich
- Im Strategen-Schluss-Format kein "Spend-Schätzung" für normale Werbetreibende
- Im Output-Frontmatter explizit dokumentieren: `spend_quelle: nur_dsa`

## 8. Hard-Cap und Anzahl-Anzeigen-Interpretation

Manche Akteure (besonders E-Commerce mit DPA-Setup) haben Hunderte aktive Anzeigen. Der Hard-Cap (Top-100 nach Erst-Schalt-Datum) ist nötig, um Output handhabbar zu halten.

**Anzahl-Anzeigen ist nicht gleich Werbe-Intensität.** Ein E-Commerce-Akteur mit 200 DPA-Anzeigen schaltet möglicherweise weniger Spend als ein B2B-Akteur mit 8 sorgfältig produzierten Video-Carousels.

**Konsequenz:**

- Im Strategen-Schluss-Format darauf hinweisen, wenn ein Akteur das Cap erreicht hat
- Im Body-Hinweis "DPA-/Catalog-Setup erkannt" wenn mehr als 70% der Anzeigen `anzeige_typ: dpa`
- In der Branchen-Statistik nicht nur Anzeigen-Anzahl, sondern auch Anteil von DPA aufschlüsseln

## 9. Internationale Aktivität ist sichtbar

Anders als bei Google's Region-Filter, der das Anzeigen nur in einem Land erlaubt, kann Meta Multi-Country-Kampagnen führen. Eine Anzeige läuft ggf. simultan in DE, AT, CH und FR.

**Konsequenz:**

- `aktive_in_regionen` ist eine Liste
- `in_zielregion` als Boolean: true wenn mindestens eine Region im Akteur-Zielraum liegt
- Internationale Anzeigen werden in der CSV gehalten, aber im Aggregat separat als `internationale_aktivitaet`-Sektion ausgewiesen (strategischer Hinweis: WB expandiert in Märkte, die der Kunde noch nicht bedient)

## 10. Snapshot-Charakter und Zeit-Cliffs

Meta Ad Library zeigt:

- Aktuelle aktive Anzeigen
- Anzeigen, die in den letzten ~7 Jahren in der EU geschaltet wurden (Archiv)
- Politische Anzeigen unbefristet rückwirkend

Für die MTA: **wir konzentrieren uns auf aktive plus kürzlich gestoppte** (Standard-Filter `active_status=active`). Historische Archiv-Analyse ist Sonder-Fall (z.B. bei Strategie-Recherche zu Marken-Reposi­tio­nie­rung der WB).

**Konsequenz:**

- Standard-Lauf: `active_status=active` (Default-URL-Parameter)
- Override `include_inactive: true` möglich, dann zusätzliche Sektion `historische_anzeigen` im Output

## Zusammenfassung: Was machen wir mit der Meta-Spezifik?

1. Page-Resolution als eigenständigen Schritt vor dem Scrape
2. Plattform-Mix als zweite Auswertungs-Dimension (neben Anzeigentyp)
3. EU-DSA-Block als optionale Sektion bei Bedarf
4. Format-Mix als strategisches Insight (Single-Image vs. Video vs. Carousel)
5. Spend nur aus DSA-Block, nicht aus Drittanbieter
6. Klare Sichtbarmachung von "keine Page" als Edge Case mit strategischer Bedeutung
7. Internationale Anzeigen separat ausweisen
8. Hard-Cap mit Hinweis kombinieren, wenn DPA-Setup erkannt
