# Report-Methodik — Kennzahlen, Formeln, Datenlücken

Wie `build-report.py` aus den Mitarbeiterdaten die Report-Kennzahlen ableitet.
Alle Formeln sind hier dokumentiert, damit der Report nachvollziehbar bleibt.

## 1. Mitarbeiter-Grundgesamtheit

- Standardmäßig zählen alle vom `employees`-Befehl gelieferten Mitarbeiter —
  das sind die **aktiven** (Status ≠ `inactive`).
- Mit `--include-inactive` sind auch ausgeschiedene enthalten; dann wird im
  Report eine entsprechende Warnung gesetzt.
- `headcount` = Anzahl Mitarbeiter in der Grundgesamtheit (Köpfe, nicht FTE).

## 2. Vollzeitäquivalente (FTE)

```
FTE(Mitarbeiter) = weekly_working_hours / vollzeit_stunden
fte_summe        = Σ FTE über alle Mitarbeiter
```

`vollzeit_stunden` ist die bestätigte Vollzeit-Basis (Standard 40). Mitarbeiter
ohne `weekly_working_hours` tragen 0 zur FTE-Summe bei.

## 3. Monatsbrutto je Mitarbeiter

Das Gehalts-Attribut wird über `--gehalt-attribut` gesteuert.

**Modus `auto` (Standard):** Festgehalt vor Stundenlohn.
- `fix_salary` vorhanden und > 0 → Festgehalt, Intervall aus `fix_salary_interval`.
- sonst `hourly_salary` vorhanden und > 0 → Stundenlohn.
- sonst → kein Gehalt (Mitarbeiter zählt als „ohne Gehaltsangabe").

**Fester Schlüssel** (z. B. ein Custom-Attribut): der angegebene Wert mit dem
über `--gehalt-intervall` gesetzten Intervall.

Umrechnung auf Monatsbrutto:

| Intervall | Formel |
|---|---|
| `monatlich` | Wert unverändert |
| `jaehrlich` | Wert ÷ 12 |
| `stunde` | Wert × `weekly_working_hours` × 4,33 |

`4,33` = durchschnittliche Wochen pro Monat (52 ÷ 12).

`gehalt_basis_verteilung` im Output zeigt, wie viele Mitarbeiter über
`fix_salary`, `hourly_salary` bzw. ein Custom-Attribut erfasst wurden.

## 4. Jahresbrutto und Bonus

```
jahresbrutto        = monatsbrutto × 12
bonus_jahr          = bonus-Wert  (×12, falls --bonus-intervall monatlich)
jahresbrutto_gesamt = jahresbrutto + bonus_jahr
```

Ist `--bonus-attribut` leer, wird kein Bonus berücksichtigt.

## 5. Arbeitgeberkosten — eine Schätzung

Die Personio-API liefert **kein** Arbeitgeberkosten-Feld. Der Report rechnet:

```
ag_kosten_jahr  = jahresbrutto_gesamt × ag_faktor
ag_kosten_monat = ag_kosten_jahr / 12
```

Der **AG-Faktor** bildet die Arbeitgeber-Zusatzkosten auf das Bruttogehalt ab —
in Deutschland v. a. der Arbeitgeberanteil zur Sozialversicherung (Renten-,
Kranken-, Pflege-, Arbeitslosenversicherung, Umlagen), grob ~20 %. Standard
`1.20`.

Der Faktor ist eine **bewusste Vereinfachung** und unternehmensspezifisch:
- Betriebliche Altersvorsorge, Zuschüsse, Sachbezüge, Versicherungen treiben ihn
  höher (Werte bis ~1,30 sind realistisch).
- Er ist über alle Mitarbeiter konstant — individuelle Beitragsbemessungsgrenzen
  oder Gleitzonen werden nicht abgebildet.

Deshalb gilt durchgängig: **Arbeitgeberkosten = Schätzung, keine Ist-Werte.**
Diese Lesart steht im XLSX-Blatt „Annahmen", im HTML-Report und im Chat-Abschluss.

## 6. Aggregate

| Kennzahl | Formel |
|---|---|
| `brutto_jahr_summe` | Σ `jahresbrutto_gesamt` über Mitarbeiter mit Gehalt |
| `ag_kosten_jahr_summe` | Σ `ag_kosten_jahr` über Mitarbeiter mit Gehalt |
| `ag_kosten_monat_summe` | `ag_kosten_jahr_summe` ÷ 12 |
| `brutto_jahr_schnitt` | `brutto_jahr_summe` ÷ Anzahl mit Gehalt |
| `ag_kosten_jahr_schnitt_kopf` | `ag_kosten_jahr_summe` ÷ Anzahl mit Gehalt |
| `ag_kosten_jahr_je_fte` | `ag_kosten_jahr_summe` ÷ FTE-Summe (nur MA mit Gehalt) |

Alle Summen und Schnitte beziehen sich **nur auf Mitarbeiter mit Gehaltsangabe**.
Headcount und FTE dagegen auf die gesamte Grundgesamtheit. Diese Trennung im
Report explizit machen, wenn nicht alle Mitarbeiter ein Gehalt haben.

## 7. Abteilungs-Auswertung

Pro Abteilung: `headcount`, `fte`, Anzahl `mit_gehalt`, `brutto_jahr`, `ag_jahr`.
Mitarbeiter ohne `department` laufen unter „Ohne Abteilung". Sortierung im Output
nach `ag_jahr` absteigend (teuerste Abteilung zuerst).

## 8. Fluktuation

Bezugszeitraum: die letzten 365 Tage bis zum Stichtag (`--stichtag`, Standard
heute).

| Kennzahl | Definition |
|---|---|
| `eintritte_12m` | Mitarbeiter mit `hire_date` im Zeitfenster |
| `austritte_12m` | Mitarbeiter mit `termination_date` (oder `contract_end_date`) im Zeitfenster |
| `fluktuationsrate` | `austritte_12m` ÷ `headcount` |
| `betriebszugehoerigkeit_schnitt_jahre` | Ø (Stichtag − `hire_date`) über alle Mitarbeiter |

Die Fluktuationsrate ist eine einfache Näherung (Austritte gegen aktuellen
Headcount). Wer den Personio-Datensatz nur mit aktiven Mitarbeitern lädt, sieht
Austritte nur, solange der Mitarbeiter noch nicht auf `inactive` gesetzt ist —
für eine rückblickende Fluktuationsanalyse `--include-inactive` nutzen.

## 9. Datenlücken

`build-report.py` sammelt Warnungen in `report-daten.json` → `warnungen`. Jede
Warnung gehört sichtbar in den Report (HTML-Disclaimer + Sektion „Datenlücken").

| Situation | Auswirkung |
|---|---|
| Kein Mitarbeiter mit Gehalt | Kostensektion entfällt, Report = Headcount-Modus |
| Einzelne ohne Gehalt | fehlen in den Kostensummen; Headcount/FTE unberührt |
| `--include-inactive` gesetzt | Kennzahlen mischen aktive + ausgeschiedene MA |
| Gehalt in Custom-Attribut | korrekt nur mit passendem `--gehalt-attribut` |

Grundregel: Eine abgeleitete Kennzahl bleibt **leer** (nicht `0`), wenn ihr
Nenner 0 ist — `0 €` würde eine Aussage suggerieren, die die Daten nicht hergeben.
