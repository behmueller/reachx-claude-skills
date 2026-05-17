# Wettbewerber-Listen-Schema (`wettbewerber/liste.md`)

Das Output-Format der Phase B des `02-02-wettbewerber-identifikation`-Skills. Die finale, vom Strategen bestätigte Wettbewerber-Liste, die alle Folge-Skills nutzen.

## Vollständiges Schema

```markdown
---
# === Skill-Metadaten ===
skill: 02-02-wettbewerber-identifikation
phase: B
generiert_am: <ISO-8601>
schema_version: "1.0"
status: vorgeschlagen   # Stratege bestätigt nach Review → bestaetigt

# === Recherche-Provenienz ===
basiert_auf_schema: wettbewerber/identifikation-schema.md
basiert_auf_schema_bestaetigt_am: <ISO-8601 aus identifikation-schema.md>
recherche_durchgefuehrt:
  sistrix_toplist: <true | false>
  google_maps_apify: <true | false>
  vom_briefing_uebernommen: <true | false>
gefilterte_domains_count: <int>   # wie viele Aggregatoren aus den Roh-Ergebnissen rausgefiltert wurden

# === Kategorien ===
# Drei strikte Kategorien — jeder Wettbewerber gehört in genau eine
# (im seltenen Edge-Case "Mehrfach-Zuordnung" wird der primäre Charakter gewählt)

wettbewerber:
  kunde_genannt:
    - name: <Wettbewerber-Name>
      website: <URL>
      kategorie: kunde_genannt
      bedrohungsgrad: <direkt | indirekt | inspiration>
      kontext_aus_briefing: <kurze Notiz aus briefing.md>
      quelle_briefing_turn: <timestamp>
      online_marketing_signale: [<liste, z.B. "Sistrix Visibility 0.12", "aktive LinkedIn-Page">]
      empfehlung_profilieren: <ja | nein | optional>   # ob 02-03-wettbewerber-marken-profil für diesen läuft
      
  regional:
    - name: <Wettbewerber-Name>
      website: <URL>
      kategorie: regional
      quelle_zusatz: <optional: first_party_signal — gesetzt, wenn der Akteur über ein GA4-Referral-Signal gefunden wurde>
      standort:
        adresse: <Adresse aus Google Maps>
        plz: <PLZ>
        stadt: <Stadt>
        koordinaten:
          lat: <float>
          lng: <float>
      google_maps_rating: <float, 1-5>
      google_maps_reviews_count: <int>
      online_marketing_signale: [<liste>]
      empfehlung_profilieren: <ja | nein | optional>

  best_practice_ueberregional:
    - name: <Wettbewerber-Name>
      website: <URL>
      kategorie: best_practice_ueberregional
      quelle_zusatz: <optional: first_party_signal — gesetzt, wenn der Akteur über ein GA4-Referral-Signal gefunden wurde>
      sistrix_visibility_index: <float>
      sistrix_top_keywords: [<liste der Top-5-Keywords, für die der WB rankt>]
      online_marketing_signale: [<liste>]
      warum_best_practice: <kurze Begründung, was diesen WB lehrreich macht>
      empfehlung_profilieren: <ja | nein | optional>

# === Statistik ===
anzahl_gesamt: <int>
anzahl_kunde_genannt: <int>
anzahl_regional: <int>
anzahl_best_practice: <int>
anzahl_empfohlen_zu_profilieren: <int>
---

# Wettbewerber-Liste: <Kundenname>

## Übersicht

Kompakte Zusammenfassung: wie viele Wettbewerber gefunden, in welchen Kategorien, was die wichtigsten Erkenntnisse sind.

## Kategorie 1: Vom Kunden genannt

Diese Wettbewerber hat der Kunde im Kickoff direkt erwähnt — sie gehören immer rein, auch wenn ihr Online-Marketing-Profil schwach ist.

### <Wettbewerber-Name>
- **Website**: <URL>
- **Bedrohungsgrad**: <direkt | indirekt | inspiration>
- **Kontext aus Briefing**: <Zitat oder Paraphrase>
- **Online-Marketing-Signale**: <Liste>
- **Empfehlung für `02-03-wettbewerber-marken-profil`**: <ja | nein | optional>

(weitere Wettbewerber dieser Kategorie …)

## Kategorie 2: Regional direkt

Lokale / regionale Wettbewerber aus Google-Maps-Recherche. Stratege wählt aus, welche für die MTA wichtig sind.

### <Wettbewerber-Name>
- **Standort**: <Adresse, PLZ, Stadt>
- **Google Maps**: <Rating> Sterne · <Reviews-Count> Bewertungen
- **Website**: <URL>
- **Online-Marketing-Signale**: <Liste>

(weitere …)

## Kategorie 3: Best-Practice überregional

Wettbewerber außerhalb der primären Region, die wegen ihres starken Online-Marketings als Inspiration / Benchmark dienen. Max 3-5 — der Stratege wählt aus, welche für die MTA tatsächlich relevant sind.

### <Wettbewerber-Name>
- **Website**: <URL>
- **Sistrix Visibility**: <Wert>
- **Top-Keywords**: <Liste>
- **Online-Marketing-Signale**: <Liste>
- **Warum Best-Practice**: <Begründung>

(weitere …)

## Pflicht-Review durch den Strategen

Diese Liste ist ein **Vorschlag** — der wichtigste Eingriffspunkt im MTA-Prozess. Bevor die Folge-Skills laufen:

1. **Sind alle vom Kunden genannten Wettbewerber relevant?** Manchmal hat der Kunde im Briefing einen WB genannt, der eigentlich nicht relevant ist (z. B. aus Versehen, oder Marktveränderung) — dann streichen.
2. **Bei regionalen WBs: welche werden profiliert?** Maximal 3-5 für `02-03-wettbewerber-marken-profil` empfohlen — sonst wird die MTA zu breit. Setze `empfehlung_profilieren: ja` nur bei denen, die wirklich profiliert werden sollen.
3. **Best-Practice-WBs: sind die ausgewählten lehrreich?** Stratege prüft, ob ein WB tatsächlich Lernpotenzial bringt, oder ob er nur durch Größe/Marketing-Budget oben rankt.
4. **Fehlt ein wichtiger Wettbewerber?** Manchmal weiß der Stratege aus eigener Recherche von einem WB, den die automatische Suche übersehen hat — manuell ergänzen.

**Nach dem Review**: Setze `status: bestaetigt` im Frontmatter, dann können `02-03-wettbewerber-marken-profil` und `02-04-branchenportal-recherche` laufen.
```

## Body-Sektion: Empfehlungen

Optional am Ende des Body, wenn der Skill spezielle Auffälligkeiten findet:

```markdown
## Empfehlungen

⚠ **Auffälligkeiten:**

- <Wettbewerber X> hat sehr hohe Sistrix-Sichtbarkeit, aber keine erkennbaren bezahlten Kanäle → reines SEO-Modell, sehr lehrreich für Inhaltsstrategie
- <Wettbewerber Y> ist regional dominant, hat aber keine eigene Website-Identität → könnte ein Übernahmekandidat oder schwächelnder Markt sein
- Drei der vom Kunden genannten Wettbewerber haben Sistrix-Sichtbarkeit unter 0.01 → könnten irrelevant geworden sein, mit Kunde abstimmen
```

## Feld-Erläuterungen

### `kategorie`

- **kunde_genannt**: aus `briefing.md.wettbewerber_genannt`
- **regional**: aus Google-Maps-Recherche im definierten Radius
- **best_practice_ueberregional**: aus Sistrix-Toplist, gefiltert auf "über Region hinaus"

Wenn ein Wettbewerber theoretisch in mehrere Kategorien fallen würde (z. B. vom Kunden genannt UND regional auch top), wird er primär nach **kunde_genannt** klassifiziert, weil Kunden-Aussagen Priorität haben.

### `online_marketing_signale`

Liste konkreter Hinweise auf Online-Marketing-Aktivität. Beispiele:

- `"Sistrix Visibility 0.12"` — organische Sichtbarkeit
- `"aktive Google Ads (Transparency Center: 3 Anzeigen)"`
- `"aktive Meta-Ads (Ad Library: 5 Anzeigen)"`
- `"LinkedIn Company Page mit 12 Posts in den letzten 90 Tagen"`
- `"Aktiver Newsletter (Sign-up-Form auf Startseite)"`
- `"GMB-Profil mit 47 Reviews"`

Bei der Validierung in Phase B: ein Wettbewerber kommt nur in die Liste, wenn mindestens ein Signal aus der Schema-Konfiguration erfüllt ist (Default: Sistrix-Visibility ≥ Schwellwert ODER mindestens ein alternatives Signal).

### `empfehlung_profilieren`

Steuert, ob `02-03-wettbewerber-marken-profil` für diesen Wettbewerber laufen sollte:

- `ja` → standardmäßig profilieren
- `nein` → Standort/Bewertungen-Daten reichen, kein vollständiges Profil
- `optional` → der Stratege entscheidet beim Lauf von `02-03-wettbewerber-marken-profil` per Filter

Default-Logik des Skills:

- Alle `kunde_genannt` mit Bedrohungsgrad `direkt` → `ja`
- Alle `kunde_genannt` mit Bedrohungsgrad `inspiration` → `optional`
- Regional: top 3 nach Google-Maps-Reviews → `ja`, Rest → `optional`
- Best-Practice: alle → `ja` (sind ja absichtlich kuratiert)

### `quelle_zusatz`

Optionales Feld auf Einträgen der Kategorien `regional` und `best_practice_ueberregional`. Wert `first_party_signal`, wenn der Akteur ursprünglich über einen First-Party-Hinweis (GA4-Referral-Domain aus `identifikation-schema.md.first_party_hinweise`) gefunden und in Phase B als echter Wettbewerber bestätigt wurde. Macht nachvollziehbar, dass der Akteur nicht aus Google Maps / Sistrix, sondern aus dem echten Referral-Traffic des Kunden stammt. Fehlt das Feld, kam der Akteur über den normalen Weg (Maps / Sistrix-Toplist) in die Liste. Es entsteht **keine eigene Kategorie** — `quelle_zusatz` ist nur ein Vermerk.

### `sistrix_visibility_index`

Sistrix-Sichtbarkeitsindex zum Zeitpunkt der Recherche. Wichtig: dieser Wert ist eine Momentaufnahme — bei einer späteren MTA für denselben Kunden kann sich das geändert haben.

### `warum_best_practice`

**Pflichtfeld** für die Best-Practice-Kategorie. Wenn der Skill keinen klaren Grund formulieren kann, gehört der WB nicht in diese Kategorie. Typische Begründungen:

- "Sehr starker Content-Hub mit über 200 indexierten Ratgeber-Seiten — Modell für Content-Strategie"
- "Klare D2C-Positionierung mit innovativem Branding — direkter Vergleichspunkt für Kundenwunsch D2C-Ausbau"
- "Newsletter-getrieben mit über 50k Abonnenten — Inspiration für E-Mail-Marketing-Aufbau"

## Wie Folge-Skills diese Datei lesen

Alle Wettbewerber-Operationen in Stufe 2 und 3 prüfen zuerst:

1. **`status: bestaetigt`** vorhanden? Sonst Abbruch mit Hinweis "Liste noch nicht reviewt"
2. **`empfehlung_profilieren: ja`** oder explizite Filter-Übergabe? Für `02-03-wettbewerber-marken-profil`
3. **`website`-URL** vorhanden für jeden zu profilierenden WB? Sonst Skip mit Hinweis

Konvention: Folge-Skills schreiben **nicht** in `liste.md` zurück. Wenn ein Folge-Skill (z. B. `03-01-seo-sichtbarkeit-und-rankings`) zusätzliche Daten zu einem WB erhebt, gehört das in den eigenen Output (`audits/seo-sichtbarkeit.md`).
