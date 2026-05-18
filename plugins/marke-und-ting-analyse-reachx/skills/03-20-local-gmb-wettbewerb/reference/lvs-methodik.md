# LVS-Methodik — verbindliche Berechnungs-Vorschrift

Dieses Dokument ist die **einzige Quelle** für die Berechnung des Local-Visibility-Score (LVS) und seiner drei Blöcke. Der Skill rechnet die Formeln **nicht aus dem Gedächtnis nach** — er liest dieses Dokument und folgt ihm exakt. So ist der LVS über MTAs und Skill-Versionen hinweg vergleichbar.

## Warum der LVS und nicht der Sistrix-Sichtbarkeitsindex

`contracts.md` Abschnitt 13 schreibt vor: bei kleinen lokalen Akteuren ist der Sistrix-Sichtbarkeitsindex bei `SI < 0,05` zu volatil — ein einzelnes kurz rankendes Keyword verdoppelt den Wert. Lokale Dienstleister liegen fast immer in diesem Bereich.

Der LVS umgeht das, indem er auf **lokal-robusten Signalen** beruht:

- Local-Pack-Position ist die tatsächliche Sichtbarkeits-Größe für lokale Suche.
- Review-Volumen und -Velocity ändern sich graduell, nicht sprunghaft.
- GMB-Profil-Reife ist eine Bestands-Größe ohne Tages-Volatilität.

Der LVS ist eine **vom Skill abgeleitete Heuristik** (`schaetzung_skill`), keine erhobene Messgröße — seine Eingangswerte (Rankings, Reviews, Profil-Felder) sind `erhoben`. Da der LVS load-bearing für `04-02-kanal-chancen-analyse` ist, wird die Gewichtungs-Quelle (bestätigtes Schema) im Output explizit genannt.

## Gesamt-Formel

```
LVS = (A_score × gA + B_score × gB + C_score × gC) / 100
```

- `A_score`, `B_score`, `C_score` sind jeweils auf **0–100 normiert** (siehe unten).
- `gA`, `gB`, `gC` sind die Block-Gewichte aus `lvs_gewichtung` im bestätigten Schema, `gA + gB + gC = 100`.
- Resultat `LVS` ∈ [0, 100], auf eine Nachkommastelle gerundet.

Rating-Bänder für den HTML-Report (`data-rating`-Attribut der `details.dim`-Karten):

| LVS | `data-rating` |
|---|---|
| ≥ 66 | `stark` |
| 33 – 65 | `mittel` |
| < 33 | `schwach` |

## Block A — Local-Pack-Präsenz

Eingang pro Akteur (aggregiert über alle Standort × Keyword-Queries, in denen ein Local Pack eingeblendet war — Queries ohne Local Pack zählen nicht in den Nenner):

- `top3_quote` = Anteil Queries mit Akteur-Position 1–3
- `top10_quote` = Anteil Queries mit Akteur-Position 1–10

```
A_score = clamp_0_100( 100 × (0.70 × top3_quote + 0.30 × top10_quote) )
```

Top-3 wird stärker gewichtet, weil im Local Pack faktisch nur die ersten drei Treffer ohne Aufklappen sichtbar sind. `top10_quote` schließt `top3_quote` ein (kumulativ), darum addieren sich die Anteile nicht zu mehr als der Realität.

Sonderfälle:

- Akteur in **0** Local-Pack-Queries gefunden → `A_score = 0`.
- Kunde-only-Lauf (keine Wettbewerber): `A_score` wird trotzdem berechnet, nur ohne Ranking-Vergleich.

## Block B — Review-Substanz

Drei Teil-Größen, je auf 0–100 normiert, dann gewichtet gemittelt.

### B.1 — Review-Volumen (log-skaliert)

Eine einfache lineare Skala würde einen Akteur mit 2000 Reviews alles erschlagen lassen. Darum log-Skala gegen das **Pool-Maximum**:

```
vol_score = 100 × log(1 + reviews_gesamt) / log(1 + reviews_gesamt_pool_max)
```

- `reviews_gesamt` = GMB-Gesamt-Review-Zahl des Akteurs (GMB-only, keine Multi-Plattform-Summe).
- `reviews_gesamt_pool_max` = höchster `reviews_gesamt`-Wert im Akteur-Set.
- Bei Kunde-only-Lauf: `reviews_gesamt_pool_max` = `reviews_gesamt` des Kunden → `vol_score = 100` (kein Vergleich möglich, im Output markiert).

### B.2 — Review-Velocity

Aus den vier kumulativen Buckets (`velocity_1m`, `velocity_3m`, `velocity_6m`, `velocity_12m` — siehe Abschnitt "Review-Velocity-Berechnung"). Jüngere Aktivität zählt stärker. Es wird eine **gewichtete Monats-Rate** gebildet:

```
# Inkrementelle (nicht-kumulative) Bucket-Werte:
inc_1m  = velocity_1m
inc_2_3 = velocity_3m  - velocity_1m      # Reviews aus Monat 2–3
inc_4_6 = velocity_6m  - velocity_3m      # Monat 4–6
inc_7_12= velocity_12m - velocity_6m      # Monat 7–12

# Gewichtete Monats-Rate (Gewichte: jüngste Periode 4×, dann 2×, 1×, 0.5×):
vel_rate = (4.0 × inc_1m
          + 2.0 × (inc_2_3 / 2)
          + 1.0 × (inc_4_6 / 3)
          + 0.5 × (inc_7_12 / 6))

# Normierung gegen das Pool-Maximum der vel_rate:
vel_score = clamp_0_100( 100 × vel_rate / vel_rate_pool_max )
```

- Die Division `inc_2_3 / 2` etc. macht aus der Bucket-Summe eine Monats-Durchschnittsrate.
- `vel_rate_pool_max` = höchste `vel_rate` im Akteur-Set. Ist sie 0 (niemand hat Reviews bekommen), `vel_score = 0` für alle.
- Kunde-only-Lauf: `vel_rate_pool_max` = Kunden-`vel_rate` → `vel_score = 100`, im Output markiert.

### B.3 — Durchschnitts-Rating

```
rating_score = clamp_0_100( (avg_rating - 3.0) / (5.0 - 3.0) × 100 )
```

Unter 3,0 Sterne → 0. Die Skala startet bei 3,0, weil Ratings im DACH-GMB-Raum praktisch nie unter 3,0 fallen — eine 3,8 soll sich deutlich von einer 4,8 absetzen. Bei `reviews_gesamt < 5` ist das Rating statistisch dünn: `rating_score` wird trotzdem berechnet, aber im Output mit `rating_duenn: true` markiert.

### B.4 — Block-B-Aggregat

```
B_score = 0.35 × vol_score + 0.40 × vel_score + 0.25 × rating_score
```

Velocity wird innerhalb von Block B am höchsten gewichtet — sie ist das vorausschauende Signal (wer baut auf), Volumen ist die Vergangenheit.

Reduced-Modus (keine Reviews scrapebar, nur Gesamt-Rating und -Anzahl aus dem Profil): `vel_score` entfällt, `B_score = 0.55 × vol_score + 0.45 × rating_score`, LVS-Konfidenz `niedrig`, Auffälligkeit `velocity_nicht_erhebbar`.

## Block C — GMB-Profil-Reife

Sechs Teil-Kriterien, je 0–100, dann gewichtet gemittelt. Alle Schwellen sind branchen-übergreifend.

| Kriterium | Berechnung 0–100 |
|---|---|
| `kat_score` | Hauptkategorie vorhanden = 40 Punkte. Pro Sub-Kategorie +20, Cap 100. |
| `attr_score` | `min(100, attribute_anzahl / 8 × 100)` — ab 8 Attributen voll. |
| `foto_score` | Buckets: 0 Fotos = 0 · 1–4 = 25 · 5–14 = 50 · 15–29 = 75 · ≥ 30 = 100. |
| `post_score` | `posts_pro_monat` (Posts der letzten 12 Monate / 12): 0 = 0 · < 0,5 = 30 · 0,5–1 = 60 · 1–2 = 85 · > 2 = 100. |
| `antwort_score` | `antwort_quote_prozent` direkt als 0–100 (Anteil Reviews mit Inhaber-Antwort × 100). |
| `vollst_score` | Vier Checks à 25 Punkte: Telefon vorhanden · Website vorhanden · Öffnungszeiten vorhanden · Beschreibung ≥ 100 Zeichen. |

```
C_score = (0.15 × kat_score
         + 0.10 × attr_score
         + 0.20 × foto_score
         + 0.20 × post_score
         + 0.20 × antwort_score
         + 0.15 × vollst_score)
```

`C_score` ist gleichzeitig der GMB-Profil-Reife-Score, der im Output separat ausgewiesen wird (Schritt B.5 im SKILL).

Service-Area-Business: `foto_score` und `vollst_score` werden unverändert berechnet (Service-Area-Profile haben dieselben Felder). Fehlt die Adresse strukturell, fällt sie nicht in `vollst_score` — die vier Checks sind Telefon/Website/Öffnungszeiten/Beschreibung, nicht Adresse.

## Review-Velocity-Berechnung

Aus dem Reviews-Sample (jedes Review trägt ein Datum). Stichtag ist das Lauf-Datum.

```
velocity_1m  = Anzahl Reviews mit Datum ≥ heute − 30 Tage
velocity_3m  = Anzahl Reviews mit Datum ≥ heute − 90 Tage
velocity_6m  = Anzahl Reviews mit Datum ≥ heute − 180 Tage
velocity_12m = Anzahl Reviews mit Datum ≥ heute − 365 Tage
```

Die Buckets sind **kumulativ** — `velocity_3m` schließt `velocity_1m` ein. Per Definition gilt `velocity_1m ≤ velocity_3m ≤ velocity_6m ≤ velocity_12m`.

### Velocity-Trend

Vergleicht die jüngste Quartals-Rate mit der davorliegenden:

```
rate_jung = velocity_3m / 3                       # Reviews/Monat, Monat 1–3
rate_alt  = (velocity_6m − velocity_3m) / 3        # Reviews/Monat, Monat 4–6

trend_faktor = rate_jung / rate_alt   (rate_alt > 0)
```

| Bedingung | `velocity_trend` |
|---|---|
| `rate_alt == 0` und `rate_jung > 0` | `beschleunigung` (aus dem Stand) |
| `rate_alt == 0` und `rate_jung == 0` | `inaktiv` |
| `trend_faktor ≥ 1.3` | `beschleunigung` |
| `0.7 ≤ trend_faktor < 1.3` | `stabil` |
| `trend_faktor < 0.7` | `verlangsamung` |

### Sample-Tiefe

Deckt das 150-Review-Sample keine vollen 12 Monate ab (das älteste Review im Sample ist jünger als heute − 365 Tage), ist `velocity_12m` eine **untere Schranke**: `velocity_12m_mind: true` setzen, im Output ausweisen. `velocity_1m/3m/6m` sind davon nicht betroffen, solange das Sample mindestens 6 Monate zurückreicht.

## Branchen-Gewichtungen (LVS-Block-Gewichte)

Default und branchen-typische Anpassungen — Phase A schlägt vor, Stratege bestätigt. Summe immer 100.

| Branchen-Typ | `gA` Local-Pack | `gB` Review-Substanz | `gC` Profil-Reife | Begründung |
|---|---:|---:|---:|---|
| Default | 40 | 35 | 25 | ausgewogen |
| Such-getrieben (Arzt, Anwalt, Steuerberater) | 45 | 30 | 25 | Local-Pack-Position bedeutet fast direkt Anfragen |
| Notdienst-Handwerk (Klempner, Elektriker, Schlüsseldienst) | 50 | 30 | 20 | Suche im Akut-Moment, Position entscheidet |
| Reputations-getrieben (Restaurant, Café, Hotel) | 30 | 45 | 25 | Reviews dominieren die Entscheidung |
| Beauty / Friseur / Studio | 30 | 40 | 30 | Reviews wichtig, Profil-Reife (Fotos) ebenfalls |
| Hausverwaltung / Immobilien | 40 | 35 | 25 | Default |
| KFZ-Werkstatt | 40 | 40 | 20 | Suche und Reputation gleich stark |
| Filialist (regional) | 40 | 35 | 25 | Default — pro Filiale gerechnet |
| B2B-Mittelstand mit Standort-Bezug | 45 | 30 | 25 | Local-Pack relevanter als Reviews |

Fallback (Branche nicht gelistet): Default 40 / 35 / 25 — Hinweis im Schema-Body, dass der Stratege branchen-passend justieren sollte.

## Rundung und Hilfsfunktion

```
clamp_0_100(x) = max(0, min(100, x))
```

Alle Block-Scores und der LVS auf **eine Nachkommastelle** runden. Velocity-Buckets und Review-Zahlen sind ganzzahlig.
