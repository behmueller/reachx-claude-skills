# Klassifikations-Schema — Wettbewerber-Realitäts-Check

**Verbindliche Quelle** für die Klassifikation in `02-05-wettbewerber-realitaets-check`. Der Skill wendet diese Schwellen an, statt sie pro Lauf neu zu erfinden — so bleibt die Bedrohungs-Einstufung über alle MTAs konsistent und nachvollziehbar.

Die Klassifikation ist **regelbasiert**: aus den vier erhobenen Signal-Achsen ergibt sich pro Akteur ein Punktwert; aus dem Punktwert und ein paar Override-Regeln folgt genau eine der drei Klassen. Kein Bauchgefühl — jede Klasse ist aus den Signalen herleitbar.

---

## 1. Die vier Signal-Achsen

Jeder Akteur wird auf vier Achsen bewertet. Pro Achse vergibt der Skill einen von drei Stufen-Werten — `stark` / `mittel` / `schwach` — plus den optionalen Wert `unbekannt`, wenn das Signal nicht erhebbar war.

### Achse 1 — Organische Sichtbarkeit (`sichtbarkeit`)

Leitsignal: **Ahrefs-DR**, wenn verfügbar; sonst **Sistrix-VI**. DR ist robuster, weil er auf Backlink-Stärke beruht und nicht von einzelnen kurz rankenden Keywords abhängt.

| Stufe | Ahrefs-DR | Sistrix-VI (Fallback) |
|---|---|---|
| `stark` | DR ≥ 40 | VI ≥ 0,30 |
| `mittel` | DR 15–39 | VI 0,05–0,29 |
| `schwach` | DR < 15 | VI < 0,05 |

**Volatilitäts-Disziplin (Pflicht, `contracts.md` Abschnitt 13):** Bei `Sistrix-VI < 0,05` ist der VI **kein belastbares Primär-Signal** — ein einzelnes kurz rankendes Keyword verdoppelt den Wert. In diesem Fall:

- Wenn ein DR-Wert vorliegt → DR ist allein maßgeblich, der VI wird ignoriert.
- Wenn kein DR vorliegt → die Achse `sichtbarkeit` wird auf `unbekannt` gesetzt (nicht auf `schwach`, weil der VI keine verlässliche Aussage erlaubt), und `sichtbarkeit_vi_konfidenz: niedrig` wird im Output gesetzt. Die Klassifikation stützt sich dann auf die übrigen drei Achsen.

### Achse 2 — Lokale Relevanz / GMB-Proximity (`lokale_relevanz`)

Nur aktiv, wenn der Kunde lokal/regional agiert. Bei nationalem/Online-Kunden ist diese Achse für **alle** Akteure `neutral` (zählt nicht in die Punktwertung) — im Output `lokale_achse_aktiv: false`.

Die Bewertung kombiniert **Distanz** (Akteur ↔ Kunden-Standort, Haversine in km) mit der **GMB-Stärke** (`google_maps_rating` × `google_maps_reviews_count` aus `liste.md`).

| Stufe | Bedingung |
|---|---|
| `stark` | Akteur liegt **im Einzugsradius** des Kunden (siehe Tabelle Abschnitt 3) **und** hat ≥ 50 GMB-Reviews bei Rating ≥ 4,0 |
| `mittel` | Akteur liegt im Einzugsradius, aber GMB-Präsenz dünn (< 50 Reviews) — **oder** Akteur knapp außerhalb des Radius (bis 2× Radius) mit starker GMB-Präsenz |
| `schwach` | Akteur deutlich außerhalb des Einzugsradius (> 2× Radius) — lokal kein direkter Wettbewerber |

Ein Akteur, der lokal `schwach` ist, aber auf Achse 1 oder 4 stark — das ist der typische `latente_bedrohung`-Fall (überregional stark, lokal noch nicht aktiv).

### Achse 3 — Paid-Aktivität (`paid_aktivitaet`)

Aus den `online_marketing_signale` in `liste.md` und einem optionalen Frische-Check (Google Ads Transparency Center, Meta Ad Library).

| Stufe | Bedingung |
|---|---|
| `stark` | Aktive Kampagnen auf **≥ 2** bezahlten Kanälen (Google Ads / Meta Ads / LinkedIn Ads) erkannt |
| `mittel` | Aktive Kampagnen auf **genau 1** bezahlten Kanal |
| `schwach` | Keine bezahlte Aktivität erkennbar |

### Achse 4 — Website-/Marken-Stärke (`website_marken_staerke`)

Grober Check der Akteurs-Startseite — ist das ein ausgebauter, professioneller Online-Auftritt mit erkennbarem Marketing-Setup?

| Stufe | Bedingung |
|---|---|
| `stark` | Professionelle Marken-Website, erkennbares Marketing-Setup (Tracking, Blog/Content, Newsletter, klare CTAs) |
| `mittel` | Funktionale Website, aber dünn — wenig Content, kein erkennbarer Marketing-Ausbau |
| `schwach` | Visitenkarten-Seite, veraltet, **oder** Website offline / 404 |

---

## 2. Punkte-Logik und Klassen-Zuordnung

Pro Achse werden Punkte vergeben:

| Achsen-Stufe | Punkte |
|---|---|
| `stark` | 2 |
| `mittel` | 1 |
| `schwach` | 0 |
| `unbekannt` / `neutral` | zählt nicht — der mögliche Maximalwert sinkt entsprechend |

Der **Realitäts-Score** ist die Summe der Punkte, normiert auf den tatsächlich bewertbaren Maximalwert (Achsen mit `unbekannt`/`neutral` fallen aus Zähler und Nenner). Beispiel: 3 von 4 Achsen bewertbar, Summe 4 von max. 6 → Score 0,67.

### Schwellen für die Basis-Klasse

| Realitäts-Score | Basis-Klasse |
|---|---|
| ≥ 0,55 | `aktuell_stark` |
| 0,25 – 0,54 | Zwischenbereich → Override-Regeln in Abschnitt 2.1 entscheiden |
| < 0,25 | `nachrangig` |

### 2.1 Override-Regeln (greifen vor der reinen Score-Schwelle)

Die Override-Regeln bilden die kritische Haltung aus `contracts.md` Abschnitt 13 ab — vor allem die **Latente-Bedrohung-Frage**. Sie werden **in dieser Reihenfolge** geprüft; die erste zutreffende gewinnt:

1. **Latente Bedrohung — überregional stark, lokal (noch) nicht.** Akteur hat `sichtbarkeit: stark` **und** `lokale_relevanz: schwach` (oder `neutral`), aber der Score-Bereich wäre sonst `nachrangig`/Zwischen → Klasse `latente_bedrohung`. Begründung: er ist substanziell stark und könnte jederzeit ins Einzugsgebiet expandieren.

2. **Latente Bedrohung — starke Marke ohne Aktivierung.** Akteur hat `website_marken_staerke: stark`, aber `paid_aktivitaet: schwach` **und** (`sichtbarkeit: mittel` oder besser) → Klasse `latente_bedrohung`. Begründung: solide Basis, die durch Marketing-Aktivierung schnell gefährlich wird.

3. **Aktuell stark — lokale Dominanz schlägt schwache Sichtbarkeit.** Bei aktiver lokaler Achse: Akteur hat `lokale_relevanz: stark`, auch wenn `sichtbarkeit: schwach` → Klasse `aktuell_stark`. Begründung: im lokalen Kernmarkt ist die GMB-Dominanz das ausschlaggebende Signal, nicht der (volatil-kleine) VI.

4. **Zwischenbereich-Auflösung.** Liegt der Score im Zwischenbereich (0,25–0,54) und greift keine der Regeln 1–3:
   - Mindestens eine Achse `stark` → `latente_bedrohung` (Substanz vorhanden, aber nicht durchgängig).
   - Keine Achse `stark` → `nachrangig`.

5. **Kundengenannter Akteur ohne jedes Signal.** Ein `kunde_genannt`-Akteur, dessen Achsen durchgängig `schwach`/`unbekannt` sind (Score < 0,25, Domain ggf. offline) → `nachrangig`. Er bleibt im Output (er wird **nie** stillschweigend gestrichen), aber die Datenlage trägt keine höhere Klasse. Das erzeugt im Soll-Ist-Abgleich den „überschätzt"-Befund.

### Mindest-Konfidenz

Sind **≥ 3 von 4** Achsen `unbekannt`, ist die Klassifikation nicht belastbar — der Skill setzt die Klasse trotzdem (best effort), markiert den Akteur aber mit `konfidenz: niedrig` und nennt ihn im Schluss-Format. Bei lokalem Kunden zählt die neutrale lokale Achse hier nicht als `unbekannt`.

---

## 3. Einzugsradius-Defaults pro Branchen-Typ

Der Einzugsradius definiert, was als „im Kernmarkt des Kunden" gilt (Achse 2). Quellen-Typ: `benchmark` (Reference-Wert, im Output so zu kennzeichnen). Der Skill wählt nach dem Branchen-Typ aus `meta.json.branche`; im Zweifel den nächst-ähnlichen Typ.

| Branchen-Typ | Einzugsradius (km) | Begründung |
|---|---:|---|
| Lokale Dienstleister (Arzt, Anwalt, Handwerk, Hausverwaltung, Restaurant, Kfz) | 15 | Kunden suchen wohnort-/standortnah; jenseits davon kaum Kannibalisierung |
| Regionale B2B-Mittelständler | 50 | Vertrieb deckt eine Region / mehrere Großstädte ab |
| Spezial-/Nischen-Dienstleister mit Anfahrt (z. B. Spezial-Handwerk) | 80 | Kunden nehmen für seltene Leistung längere Wege in Kauf |
| National / DACH / Online-Handel / B2B-SaaS | — (lokale Achse `neutral`) | Kein geografischer Kernmarkt — Achse 2 zählt nicht |

„Knapp außerhalb" (Achsen-Stufe `mittel`) reicht bis zum **2-fachen** des Radius. Alles darüber ist `schwach` auf Achse 2.

---

## 4. Soll-Ist-Mapping

Der Soll-Ist-Abgleich stellt die **Kunden-Einschätzung** (Soll) gegen die **Datenlage** (Ist = die in Abschnitt 2 vergebene Klasse).

**Soll** — der `bedrohungsgrad` aus `liste.md` / `briefing.md`:

- `direkt` — Kunde sieht den Akteur als direkten Hauptkonkurrenten.
- `indirekt` — Kunde sieht ihn als Wettbewerber, aber zweitrangig.
- `inspiration` — Kunde nennt ihn als Vorbild/Benchmark, nicht als Bedrohung.
- `nicht_genannt` — Akteur stammt aus regionaler/Best-Practice-Recherche, der Kunde hat ihn nicht erwähnt.

**Mapping-Tabelle** — der Befund pro Soll-Ist-Kombination:

| Soll (Kunde) ↓ \ Ist (Daten) → | `aktuell_stark` | `latente_bedrohung` | `nachrangig` |
|---|---|---|---|
| `direkt` | **bestätigt** | **teilweise bestätigt** — heute nicht akut, aber relevant | **überschätzt** — datenseitig nachrangig |
| `indirekt` | **unterschätzt** — stärker als gedacht | **bestätigt** | **bestätigt** |
| `inspiration` | **unterschätzt / blinder Fleck** — der „Benchmark" ist real ein Wettbewerber | **bestätigt** — Benchmark mit Bedrohungspotenzial | **bestätigt** |
| `nicht_genannt` | **blinder Fleck** — starker Wettbewerber, nicht auf dem Schirm | **latente Bedrohung übersehen** | **bestätigt** — zu Recht nicht genannt |

**Pflicht:** Alle Befunde mit fettem Markup oben außer „bestätigt" (also: überschätzt, unterschätzt, blinder Fleck, latente Bedrohung übersehen, teilweise bestätigt) sind **Abweichungen** und wandern zusätzlich in den Auffälligkeiten-Block des Outputs und ins Schluss-Format. „bestätigt" bleibt im Akteur-Block, ist aber selbst ein wertvolles Ergebnis — es belegt, dass die Kunden-Einschätzung trägt.

---

## 5. Beispiel (illustrativ)

Lokaler Kunde (Hausverwaltung, Einzugsradius 15 km). Vier Akteure aus `liste.md`:

| Akteur | Soll (Kunde) | Sichtbarkeit | Lokal | Paid | Marke | Score | Klasse (Ist) | Soll-Ist-Befund |
|---|---|---|---|---|---|---:|---|---|
| Verwaltung Müller | `direkt` | mittel (DR 22) | stark (im Radius, 90 Reviews) | mittel | mittel | 0,67 | `aktuell_stark` | bestätigt |
| Hausservice Klein | `direkt` | schwach (VI 0,01 → unbekannt) | schwach (40 km) | schwach | schwach | 0,11 | `nachrangig` | **überschätzt** |
| ImmoProfi (überregional) | `nicht_genannt` | stark (DR 51) | schwach (120 km) | stark | stark | — | `latente_bedrohung` (Override 1) | **latente Bedrohung übersehen** |
| Verwaltung Nord | `nicht_genannt` | mittel (DR 18) | stark (im Radius, 70 Reviews) | schwach | mittel | 0,50 | `aktuell_stark` (Override 3) | **blinder Fleck** |

Lesart: Der Kunde hat seine zwei „Hauptkonkurrenten" genannt — aber einer davon ist datenseitig nachrangig, und zwei real relevante Akteure standen gar nicht auf seiner Liste. Genau das soll der Realitäts-Check sichtbar machen.
