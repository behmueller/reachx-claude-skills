# Reddit-Marketing-Fit-Score-Formel

Definiert die vier Achsen, Gewichte, Einzel-Formeln und Score-Bands fuer den Reddit-Marketing-Fit-Score. Aus dem SKILL.md Schritt 8 verwiesen.

**Designprinzip:** Der Score ist **reproduzierbar** — gleiche Eingangsdaten ergeben gleichen Score. Keine LLM-Bauchgefuehl-Komponente in der Formel selbst. LLM-Anteile sind ausschliesslich in der Sentiment-Klassifikation (Eingangsgroesse) und werden mit Konfidenz-Tracking versehen.

## Score-Bands und Strategie-Empfehlung

| Score-Band | Empfehlung | Bedeutung |
|---|---|---|
| 0-30 | `nicht_empfohlen` | Reddit ist fuer diese Branche/Marke nicht der richtige Hebel. Andere Kanaele priorisieren. Skill liefert Begruendung, keine Kanal-Investition empfohlen. |
| 31-55 | `beobachtung_empfohlen` | Kanal mit Potenzial, aber Friction-Punkte. Nicht aktiv investieren, aber Quartals-Monitoring der Subreddits + Marken-Erwaehnungen. Reputations-Watchlist statt Marketing-Aktivierung. |
| 56-100 | `aktiv_empfohlen` | Kanal lohnt aktive Bespielung. Strategie-Block im Output zeigt konkrete Pfade (AMA, organische Content-Beitraege in passenden Subreddits, ggf. eigene Subreddit-Pflege). |

Die Grenzen sind bewusst nicht 33/66 — wir sind konservativ, weil Reddit-Marketing-Fehlinvestitionen teuer sein koennen (Community-Backlash).

## Achse 1 — Community-Aktivitaet (Gewicht 30%)

**Idee:** Sind ueberhaupt aktive Communities zur Branche da, wo sich Marken-Aktivierung lohnen koennte?

**Eingangsgroessen:**

- `median_mitglieder_top10` — Median der Mitglieder-Anzahl der Top-10-Subreddits nach Relevanz
- `median_posts_pro_tag` — Median der Posts/Tag in den Top-10-Subreddits
- `subreddit_anzahl` — Anzahl Subreddits, die das Filter aus Schritt 3 passieren

**Formel:**

```
achse_1_score = min(100,
    log10(max(median_mitglieder_top10, 1)) * 12
  + min(median_posts_pro_tag, 20) * 2
  + min(subreddit_anzahl, 15) * 1
)
```

**Interpretations-Anker:**

| Wert | Beispiel-Konstellation |
|---|---|
| 0-25 | <3 Subreddits gefunden, Median <2.000 Mitglieder, <1 Post/Tag |
| 25-50 | 3-5 Subreddits, Median 5.000-20.000 Mitglieder, 2-5 Posts/Tag |
| 50-75 | 6-10 Subreddits, Median 20.000-100.000 Mitglieder, 5-15 Posts/Tag |
| 75-100 | >10 Subreddits oder Median >100.000 Mitglieder mit hoher Post-Frequenz |

## Achse 2 — Brand-Reception (Gewicht 30%)

**Idee:** Wie wird der Kunde aktuell auf Reddit wahrgenommen? Werden positive Stories erzaehlt, oder ist die Marke ein PR-Fall?

**Eingangsgroessen (alle nur fuer Kunden-Erwaehnungen):**

- `erwaehnungen_anzahl` — Anzahl Kunden-Erwaehnungen in 6 Monaten
- `pos_anteil` — Anteil positiv klassifizierter Erwaehnungen
- `neg_anteil` — Anteil negativ klassifizierter Erwaehnungen
- `unklar_anteil` — Anteil unklarer Erwaehnungen

**Formel (mit Sample-Size-Korrektur):**

```
if erwaehnungen_anzahl == 0:
    achse_2_score = 30   # Neutral-Default, weil keine Signale (kein Beleg fuer pos noch neg)
elif erwaehnungen_anzahl < 5:
    # Sample zu klein fuer Aussagen, weiter Richtung Neutral
    rohwert = 50 + (pos_anteil - neg_anteil) * 30
    achse_2_score = max(20, min(80, rohwert))
else:
    rohwert = 50 + (pos_anteil * 60) - (neg_anteil * 80)
    # neg wird staerker gewichtet — eine Reputations-Krise straft mehr als Lob hebt
    achse_2_score = max(0, min(100, rohwert))
```

**Interpretations-Anker:**

| Wert | Beispiel-Konstellation |
|---|---|
| 0-25 | Mehrheit negativ (>50% neg), oder einzelner viraler Negativ-Thread mit >500 Score |
| 25-50 | Mehrheit unklar/neutral oder gemischt, leicht negativ-tendierend |
| 50-75 | Neutral bis leicht positiv, 0-Erwaehnungen-Fall liegt hier |
| 75-100 | Mehrheit positiv (>40% pos), keine virale Negativ-Story, gemischt akzeptabel |

**Wichtig:** Die `unklar`-Klassifikation wird nicht gewichtet — der Skill rechnet konservativ, dass unklare Erwaehnungen kein Wert sind. Das wird im Output als Hinweis dokumentiert, wenn `unklar_anteil > 30%` ("Sentiment-Sample mit hoher Unschaerfe — Reception-Score mit Vorsicht").

## Achse 3 — Kommerz-Toleranz (Gewicht 20%)

**Idee:** Wie offen sind die relevanten Subreddits fuer Marken-Beitraege? Sehr strenge anti-Werbung-Communities sind eher Risiko als Chance.

**Eingangsgroessen:**

- `anteil_kommerz_allergisch_top10` — Anteil der Top-10-Subreddits mit Tonalitaet `kommerz_allergisch`
- `anteil_streng_moderiert_top10` — Anteil mit Moderations-Strenge `streng`
- `anteil_locker_moderiert_top10` — Anteil mit Moderations-Strenge `locker`

**Formel:**

```
achse_3_score = 100 * (
    (1 - anteil_kommerz_allergisch_top10) * 0.6
  + (1 - anteil_streng_moderiert_top10 * 0.5) * 0.3
  + anteil_locker_moderiert_top10 * 0.1
)
```

**Interpretations-Anker:**

| Wert | Beispiel-Konstellation |
|---|---|
| 0-25 | >70% der Top-10-Subreddits sind kommerz_allergisch und streng moderiert |
| 25-50 | 30-70% kommerz_allergisch oder ueberwiegend streng moderiert |
| 50-75 | Gemischtes Bild, einige locker moderierte Communities vorhanden |
| 75-100 | <30% kommerz_allergisch, mehrheitlich locker bis mittel moderiert |

**Anmerkung:** Selbst bei niedrigem Score 3 ist Reddit nicht automatisch tot — AMA-Formate funktionieren auch in stark moderierten Subreddits, wenn sie authentisch sind. Aber direkte Werbung ist dort raus.

## Achse 4 — Format-Tauglichkeit (Gewicht 20%)

**Idee:** Passt die Marke ueberhaupt auf Reddit? Sprache, Tonalitaet, Format-Anforderungen.

**Eingangsgroessen:**

- `sprache_kollision_faktor` — 1.0 wenn Kunde deutsch und >70% der Top-10-Subreddits englisch (oder umgekehrt), sonst 0.0, dazwischen linear
- `anteil_hilfsbereit_top10` — Anteil Top-10-Subreddits mit Tonalitaet `hilfsbereit`
- `anteil_ernsthaft_top10` — Anteil mit Tonalitaet `ernsthaft`

**Formel:**

```
sprache_faktor = 1 - sprache_kollision_faktor   # 0.0 = volle Kollision, 1.0 = passt
tonalitaet_faktor = (anteil_hilfsbereit_top10 * 1.0
                   + anteil_ernsthaft_top10 * 0.7)

achse_4_score = 100 * sprache_faktor * (0.4 + 0.6 * tonalitaet_faktor)
```

**Interpretations-Anker:**

| Wert | Beispiel-Konstellation |
|---|---|
| 0-25 | Sprache passt nicht UND wenig hilfsbereit/ernsthaft (z. B. ueberwiegend snarky) |
| 25-50 | Sprache passt teilweise oder Tonalitaet mittel |
| 50-75 | Sprache passt, Tonalitaet ueberwiegend ernsthaft, wenig hilfsbereit |
| 75-100 | Sprache passt voll, hoher Anteil hilfsbereit (Frage-Antwort-Communities) |

## Gesamt-Score

```
gesamt_score = (
    achse_1_score * 0.30
  + achse_2_score * 0.30
  + achse_3_score * 0.20
  + achse_4_score * 0.20
)
```

Runden auf ganze Zahl. Score 0-100.

## Branchen-Default-Anpassungen

Die Achsen-Gewichte koennen branchenabhaengig leicht angepasst werden. Default-Set funktioniert fuer die meisten Branchen, aber dokumentierte Sonderfaelle:

### Tech / B2B-SaaS / Developer-Tools

```
gewichte = {achse_1: 0.25, achse_2: 0.25, achse_3: 0.20, achse_4: 0.30}
```

Format-Tauglichkeit zaehlt staerker (Reddit ist fuer Dev-Tools ein etablierter Kanal — wenn Sprache/Tonalitaet nicht passt, wird's schwierig).

### Lokale Dienstleister (Handwerk, Praxen, regionale B2C)

```
gewichte = {achse_1: 0.40, achse_2: 0.25, achse_3: 0.15, achse_4: 0.20}
```

Community-Aktivitaet entscheidet — wenn die Branche auf Reddit strukturell nicht praesent ist, ist alles andere egal. Kommerz-Toleranz weniger relevant (Skip-Variante greift meist eh).

### Krise / PR-Hot-Topic (Kunde hat gerade Reputations-Issue)

```
gewichte = {achse_1: 0.20, achse_2: 0.50, achse_3: 0.15, achse_4: 0.15}
```

Brand-Reception wird zur dominanten Achse. Wird vom Skill **nicht automatisch** angewandt — nur wenn der Stratege es explizit anfordert oder die Auffaelligkeit `negativer_sentiment_haeufung` getriggert ist.

Default-Set ueberschreiben:

- Im Frontmatter von `audits/reddit-fit.md`: `gewichte_override: {...}` setzen
- Skill nutzt dann diese statt der Defaults
- Im Output Sektion "Fit-Score-Aufschluesselung" wird der Override-Zustand ausgewiesen

## Sanity-Check-Regeln

Bevor der Score finalisiert wird, der Skill prueft:

1. **Wenn `subreddit_anzahl == 0` → Score automatisch 0**, Empfehlung `nicht_empfohlen`, keine weiteren Berechnungen (Skip-Variante).
2. **Wenn `unklar_anteil > 50%` der Erwaehnungen UND `erwaehnungen_anzahl >= 10` → Sentiment-Qualitaet-Warnung** im Output, Achse 2 mit `daten_verlaesslichkeit: niedrig` markieren.
3. **Wenn Achse 1 < 20 und Gesamt-Score >= 56 → Inkonsistenz, Skill loggt Warnung**, Score bleibt aber numerisch. Kann passieren, wenn andere Achsen sehr hoch sind, aber Community-Basis schwach ist — selten, aber moeglich.
4. **Wenn `gewichte` nicht zu 1.0 aufsummieren (Override-Fehler) → Skill normalisiert auf 1.0** und gibt Hinweis im Output.

## Beispiel-Rechnungen

### Beispiel A — B2B-SaaS, etablierte Marke

- `median_mitglieder_top10 = 80.000`, `median_posts_pro_tag = 8`, `subreddit_anzahl = 12`
  → Achse 1 = `min(100, log10(80000) * 12 + 8 * 2 + 12 * 1)` = `min(100, 58.6 + 16 + 12)` = `86.6` → **87**
- `erwaehnungen_anzahl = 35`, `pos_anteil = 0.45`, `neg_anteil = 0.10`
  → Achse 2 = `50 + (0.45 * 60) - (0.10 * 80)` = `50 + 27 - 8` = **69**
- `anteil_kommerz_allergisch_top10 = 0.20`, `anteil_streng = 0.30`, `anteil_locker = 0.40`
  → Achse 3 = `100 * (0.80 * 0.6 + 0.85 * 0.3 + 0.40 * 0.1)` = `100 * (0.48 + 0.255 + 0.04)` = **77**
- `sprache_kollision_faktor = 0.3`, `anteil_hilfsbereit = 0.40`, `anteil_ernsthaft = 0.40`
  → Achse 4 = `100 * 0.7 * (0.4 + 0.6 * (0.40 + 0.40 * 0.7))` = `100 * 0.7 * (0.4 + 0.408)` = **57**
- Gesamt: `87 * 0.30 + 69 * 0.30 + 77 * 0.20 + 57 * 0.20` = `26.1 + 20.7 + 15.4 + 11.4` = **74** → `aktiv_empfohlen`

### Beispiel B — Lokaler Maler-Betrieb

- `subreddit_anzahl = 2`, `median_mitglieder = 8.000`, `median_posts_pro_tag = 1`
  → Achse 1 = `log10(8000) * 12 + 1 * 2 + 2 * 1` = `46.9 + 2 + 2` = **51**
- `erwaehnungen_anzahl = 0` → Achse 2 = **30** (Neutral-Default)
- `anteil_kommerz_allergisch = 0.0`, `anteil_streng = 0.5`, `anteil_locker = 0.5`
  → Achse 3 = `100 * (1.0 * 0.6 + 0.75 * 0.3 + 0.5 * 0.1)` = `100 * 0.875` = **87**
- `sprache_kollision = 0`, `anteil_hilfsbereit = 0.50`, `anteil_ernsthaft = 0.50`
  → Achse 4 = `100 * 1.0 * (0.4 + 0.6 * (0.5 + 0.35))` = `100 * 0.91` = **91**
- Branchen-Default fuer lokale Dienstleister:
  → `51 * 0.40 + 30 * 0.25 + 87 * 0.15 + 91 * 0.20` = `20.4 + 7.5 + 13.05 + 18.2` = **59** → `aktiv_empfohlen` (knapp)

Aber Sanity-Check: Achse 1 = 51 ist okay, aber `subreddit_anzahl = 2` triggert kompakter Lauf. Empfehlung wird dann im Strategie-Block: "Beobachtung in den 2 identifizierten Subreddits sinnvoll, keine grosse Aktivierungs-Kampagne".

### Beispiel C — Hausverwaltung, B2B

- `subreddit_anzahl = 0` → Skip-Variante, Score = 0, `nicht_empfohlen`. Keine weiteren Berechnungen.

## Versionierung

Wenn sich die Formel aendert: in `audits/reddit-fit.md` Frontmatter `formel_version: "1.0"` setzen, in diesem File die neue Version dokumentieren, alte Beispiel-Rechnungen behalten als Vergleichs-Anker.

Aktuelle Version: **1.0**
