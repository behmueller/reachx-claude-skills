---
name: personio-personalkosten-report
description: Erzeugt aus den echten Personio-Mitarbeiterstammdaten einen Personalkosten- und Headcount-Report. Greift First-Party über das lokale Wrapper-Skript personio.py read-only auf die Personio REST API zu, lädt alle Mitarbeiter, leitet daraus Headcount, Vollzeitäquivalente (FTE), Bruttogehälter, geschätzte Arbeitgeberkosten (Brutto × konfigurierbarer AG-Faktor), eine Abteilungs-Kostenverteilung sowie Fluktuation (Ein-/Austritte, Betriebszugehörigkeit) ab und schreibt eine formatierte Excel-Arbeitsmappe plus einen REACHX-gebrandeten HTML-Report. Der Skill schreibt NIEMALS nach Personio zurück und lädt die sensiblen Gehaltsdaten nirgendwo hoch — alle Ausgaben bleiben lokal. Nutze diesen Skill, wenn der Nutzer Personio-Daten auswerten, einen Personalkosten-Report, Headcount-Report, Arbeitgeberkosten-Übersicht oder eine HR-Auswertung bauen will — auch bei Phrasen wie "Personio-Report bauen", "Personalkosten auswerten", "Arbeitgeberkosten berechnen", "Headcount-Übersicht", "wie viele Mitarbeiter haben wir", "Personalkosten pro Abteilung", "FTE-Auswertung", "Fluktuation auswerten", "Daten aus Personio ziehen", "HR-Report erstellen", "Personio-Mitarbeiterliste exportieren". Setzt voraus, dass in ~/.config/reachx-mta/personio.yaml gültige Personio-API-Zugangsdaten hinterlegt sind.
---

# Personio-Personalkosten-Report

Dieser Skill zieht die **echten Mitarbeiterstammdaten** aus der Personio REST API
und verdichtet sie zu einem belastbaren Personalkosten- und Headcount-Report:
Wie viele Menschen arbeiten im Unternehmen, wie viele Vollzeitäquivalente, was
kosten sie als Arbeitgeber, wie verteilen sich die Kosten auf die Abteilungen,
und wie steht es um Ein-/Austritte und Betriebszugehörigkeit?

Das Ergebnis sind zwei Outputs: eine **formatierte Excel-Arbeitsmappe** für HR-
Kollegen, die in Excel weiterrechnen, und ein **REACHX-gebrandeter HTML-Report**
als vorzeigbare Management-Sicht.

## Read-only — die zentrale Regel

**Dieser Skill verändert NIEMALS etwas in Personio.** Das Wrapper-Skript
`personio.py` hat bewusst keinen schreibenden Befehl — es kann ausschließlich
lesen (`auth-check`, `employees`, `attributes`). Bittet der Nutzer um eine
Datenänderung in Personio, wird das freundlich abgelehnt: Stammdatenpflege ist
ein bewusst getrennter Vorgang in der Personio-Oberfläche.

## Datenschutz — Gehaltsdaten sind hochsensibel

Gehalts- und Personalkostendaten sind die sensibelste Datenklasse im Unternehmen.
Deshalb gilt:

- **Alle Ausgaben bleiben lokal.** Der Report wird ausschließlich ins lokale
  Dateisystem geschrieben (`~/personio-reports/…`). Kein Upload nach Google Drive,
  in keinen Cloud-Speicher, an keinen externen Dienst.
- **Keine MCP-Weiterleitung.** Es wird kein Personio-MCP und kein
  Drittanbieter-Konnektor genutzt — der API-Zugriff läuft direkt über das lokale
  Wrapper-Skript, die Credentials liegen nur in `~/.config/reachx-mta/`.
- **Anonymisierung anbieten.** Vor dem Lauf wird gefragt, ob die Klarnamen durch
  Codes (`MA-001`, `MA-002`, …) ersetzt werden sollen — sinnvoll, wenn der Report
  über den engsten Kreis hinaus geteilt wird.
- Im Chat werden **keine Einzelgehälter** ausgeschüttet — nur Summen und
  Durchschnitte. Einzelwerte stehen in den lokalen Dateien.

## Ausführungs-Modus

Der Skill läuft **im Hauptthread**, ohne Subagent — er ist interaktiv (Annahmen
werden bestätigt) und überschaubar im Token-Verbrauch. Keine Abhängigkeit zu
anderen REACHX-Plugins.

## Voraussetzungen

1. **Personio-API-Zugangsdaten** in `~/.config/reachx-mta/personio.yaml`
   (`client_id`, `client_secret`). Vorlage: `reference/credentials-vorlage.yaml`.
   Die Zugangsdaten werden in Personio erstellt unter *Einstellungen >
   Integrationen > API-Zugänge*. Der Zugang braucht die **Leseberechtigung für
   den Mitarbeiter-Endpunkt**; für die Kostenauswertung zusätzlich die
   **Attribut-Freigabe für die Gehaltsfelder** (`fix_salary`,
   `fix_salary_interval`, `hourly_salary`, `bonus` — oder das jeweilige
   Custom-Attribut). Ohne diese Freigabe liefert Personio die Gehaltsfelder
   schlicht nicht, und der Report bleibt auf Headcount/FTE beschränkt.
2. **Python-Abhängigkeiten** — `PyYAML` und `openpyxl`:
   `pip3 install -r scripts/requirements-personio.txt`.
3. Der API-Zugang setzt je nach Personio-Tarif eine entsprechende Lizenz voraus
   (Custom-Integrationen sind nicht in allen Plänen enthalten).

Fehlt die Credential-Datei:

```
✗ Personio-Report nicht möglich — keine API-Zugangsdaten gefunden.

So beheben:
1. reference/credentials-vorlage.yaml nach ~/.config/reachx-mta/personio.yaml kopieren.
2. client_id und client_secret aus Personio eintragen
   (Einstellungen > Integrationen > API-Zugänge).
3. chmod 600 ~/.config/reachx-mta/personio.yaml
4. Diesen Skill erneut aufrufen.
```

## Skript-Pfade

Die beiden Skripte liegen relativ zu dieser `SKILL.md` unter `scripts/`. Im
Folgenden kurz `personio.py` und `build-report.py` genannt — immer mit dem
tatsächlichen absoluten Pfad aufrufen.

## Ablauf

### Schritt 0: Voraussetzungs-Check

`python3 scripts/personio.py auth-check` ausführen.

- Erfolg (`"success": true`) → weiter zu Schritt 1.
- `Credential-Datei fehlt` → den Hinweis aus *Voraussetzungen* ausgeben, stoppen.
- `PyYAML fehlt` / `openpyxl fehlt` → Installationsbefehl ausgeben, stoppen.
- HTTP 401/403 → Zugangsdaten bzw. Berechtigungen prüfen lassen, stoppen.

### Schritt 1: Mitarbeiterdaten laden

Ausgabe-Verzeichnis festlegen: `~/personio-reports/personalkosten-<YYYY-MM-DD>/`
(`<YYYY-MM-DD>` = heutiges Datum). Verzeichnis anlegen.

`python3 scripts/personio.py employees --out <dir>/employees.json` ausführen.

Standardmäßig werden **aktive** Mitarbeiter geladen (Status ≠ `inactive`). Will
der Nutzer ausdrücklich auch ausgeschiedene Mitarbeiter (z. B. für eine
rückblickende Jahresauswertung), `--include-inactive` ergänzen.

Aus der JSON-Antwort `count` und `gehaltsfelder_vorhanden` ablesen. Stehen alle
Gehaltsfelder auf `false`, ist die Attribut-Freigabe vermutlich nicht erteilt —
das in Schritt 2 ansprechen.

### Schritt 2: Gehalts-Attribut prüfen (nur wenn nötig)

Sind in `gehaltsfelder_vorhanden` weder `fix_salary` noch `hourly_salary` auf
`true`, liegt das Gehalt evtl. in einem **Custom-Attribut**. Dann:

`python3 scripts/personio.py attributes` ausführen und die Liste nach einem
Eintrag durchsehen, dessen Label nach Gehalt klingt (oft `ist_custom: true`,
Schlüssel `dynamic_NNNN`). Den gefundenen Schlüssel dem Nutzer vorschlagen — er
wird in Schritt 3 als `--gehalt-attribut` gesetzt.

Findet sich nichts, läuft der Report im **Headcount-Modus** weiter (FTE und
Fluktuation funktionieren, Kostenzahlen bleiben leer) — das ist eine Datenlücke,
keine Abbruchbedingung.

### Schritt 3: Annahmen festlegen und bestätigen

Die Personio-API liefert das **vertragliche Bruttogehalt**, nicht die
tatsächlichen Arbeitgeberkosten. Vier Annahmen steuern die Rechnung und werden
**vor dem Lauf mit dem Nutzer bestätigt** — sie stehen später transparent im
Report:

| Annahme | Standard | Bedeutung |
|---|---|---|
| **AG-Faktor** | `1.20` | Multiplikator Brutto → Arbeitgeberkosten. `1.20` ≈ 20 % Arbeitgeberanteil zur Sozialversicherung (DE). |
| **Vollzeit-Wochenstunden** | `40` | Basis für die FTE-Berechnung (FTE = Wochenstunden ÷ Basis). |
| **Gehalts-Attribut** | `auto` | `auto` nimmt `fix_salary`, sonst hilfsweise `hourly_salary`. Sonst der in Schritt 2 gefundene Schlüssel. |
| **Bonus** | `bonus`, jährlich | Bonus-Attribut und ob der Wert jährlich oder monatlich gilt. Leeres Attribut = Bonus ignorieren. |
| **Anonymisierung** | nachfragen | Klarnamen durch `MA-001` … ersetzen? Siehe *Datenschutz*. |

Dem Nutzer die Standardwerte nennen und fragen, ob sie passen — besonders der
**AG-Faktor** ist unternehmensspezifisch (Branche, Zusatzleistungen, betriebliche
Altersvorsorge können ihn höher treiben). Erst nach Bestätigung weiter.

### Schritt 4: Report-Daten berechnen und Excel-Mappe schreiben

`build-report.py` mit den bestätigten Annahmen aufrufen:

```
python3 scripts/build-report.py \
  --employees <dir>/employees.json \
  --out-dir <dir> \
  --ag-faktor <wert> \
  --vollzeit-stunden <wert> \
  --gehalt-attribut <auto|schlüssel> \
  --bonus-attribut <bonus|""> \
  --bonus-intervall <jaehrlich|monatlich> \
  [--anonym] [--stichtag YYYY-MM-DD]
```

Das Skript schreibt `personalkosten-report.xlsx` (vier Blätter: Übersicht,
Mitarbeiter, Abteilungen, Annahmen & Hinweise) und `report-daten.json` (die
verdichteten Kennzahlen für den HTML-Report). Die `warnungen`-Liste aus dem
JSON-Ergebnis merken — sie wird im Report zur Datenlücken-Sektion.

### Schritt 5: HTML-Report bauen

`report-daten.json` lesen, `reference/report-shell.html` lesen, die sechs
Platzhalter ersetzen, `personalkosten-report.html` ins Ausgabe-Verzeichnis
schreiben. `{{MAIN_CONTENT}}` **ausschließlich** aus den Bausteinen in
`reference/report-output-schema.md` — keine eigenen CSS-Klassen, kein
inline-`style` (Ausnahme: `bar-fill`-Breite), der `<style>`-Block bleibt
unverändert. Vor dem Speichern prüfen: keine offenen `{{…}}`, nur definierte
Klassen.

Inhaltliche Pflicht-Reihenfolge und Bausteine: `reference/report-output-schema.md`
Abschnitt 3. Der Report ist die **Interpretations-Schicht** (Kernbefund,
Kosten-Schwerpunkte, Datenqualität), die Excel-Mappe die Detail-Schicht.

### Schritt 6: Abschluss im Chat

```
✓ Personio-Personalkosten-Report erstellt — read-only, keine Änderungen in Personio.

Outputs (lokal in ~/personio-reports/personalkosten-<datum>/):
- personalkosten-report.html  — REACHX-Report (Management-Sicht)
- personalkosten-report.xlsx  — Excel-Mappe (4 Blätter, Detail-Sicht)
- report-daten.json           — verdichtete Kennzahlen
- employees.json              — Roh-Daten aus Personio

Stichtag: <datum>  ·  Stand der Annahmen: AG-Faktor <wert>, Vollzeit <wert> h

Kennzahlen:
- Headcount:                <N> Mitarbeiter
- Vollzeitäquivalente:      <FTE>
- Arbeitgeberkosten p.a.:   <summe> € (geschätzt)
- Ø Arbeitgeberkosten/Kopf: <wert> € p.a.
- Fluktuation 12 Monate:    <X> Eintritte / <Y> Austritte

[Bei Datenlücken:]
⚠ <Warnung, z.B. "12 von 80 Mitarbeitern ohne Gehaltsangabe">

Hinweis: Die Arbeitgeberkosten sind eine Schätzung (Brutto × AG-Faktor),
keine Ist-Abrechnungswerte. Die Dateien enthalten sensible Gehaltsdaten —
bitte entsprechend ablegen.
```

## Bundled Resources

- `scripts/personio.py` — read-only CLI gegen die Personio REST API v1
  (`auth-check`, `employees`, `attributes`). Nur Standardbibliothek + PyYAML.
- `scripts/build-report.py` — Aggregation und Excel-Mappe (openpyxl).
- `scripts/requirements-personio.txt` — Python-Abhängigkeiten.
- `reference/credentials-vorlage.yaml` — Vorlage für `personio.yaml`.
- `reference/personio-api-nutzung.md` — API-Endpunkte, Auth-Flow, Berechtigungen,
  Datenmodell der Mitarbeiter-Attribute, Fehlerverhalten.
- `reference/report-methodik.md` — Kennzahlen-Formeln, AG-Faktor-Logik,
  FTE-Berechnung, Fluktuation, Umgang mit Datenlücken.
- `reference/report-output-schema.md` — XLSX-Blätter, `report-daten.json`-Schema,
  HTML-Platzhalter und Report-Bausteine.
- `reference/report-shell.html` — REACHX-gebrandete HTML-Shell.

## Edge Cases

- **Credential-Datei fehlt / Platzhalter noch drin** → Hinweis aus
  *Voraussetzungen*, sauberer Stopp.
- **HTTP 401** (Auth abgelehnt) → `client_id`/`client_secret` prüfen, ob der
  API-Zugang in Personio noch aktiv ist. Stopp.
- **HTTP 403** (Zugriff verweigert) → dem API-Zugang fehlt eine Lese- oder
  Attribut-Berechtigung. Mit reduziertem Datensatz weiterarbeiten, Lücke
  vermerken.
- **HTTP 429** (Rate-Limit) → kurz warten, Skill erneut aufrufen.
- **Keine Gehaltsfelder** (`gehaltsfelder_vorhanden` alle `false`) → Schritt 2,
  Custom-Attribut suchen; sonst Headcount-Modus, Kostensektion als Datenlücke.
- **Einzelne Mitarbeiter ohne Gehalt** → sie zählen in Headcount/FTE, fehlen aber
  in den Kostensummen. `build-report.py` meldet das als Warnung — im Report als
  Datenlücke ausweisen, Kostenzahlen entsprechend als „für N von M MA" lesen.
- **Gemischte Gehaltsbasis** (Festangestellte + Stundenkräfte) → `auto` löst das
  automatisch (fix_salary bzuerst, sonst hourly_salary); `gehalt_basis_verteilung`
  in `report-daten.json` zeigt die Aufteilung.
- **Mitarbeiter ohne Abteilung** → laufen unter „Ohne Abteilung".
- **Sehr kleines Unternehmen** (wenige Mitarbeiter) → Report läuft normal; bei
  Anonymisierung darauf hinweisen, dass Codes bei kleiner Belegschaft trotzdem
  rückführbar sein können.
- **Nutzer wünscht eine Änderung in Personio** → freundlich ablehnen (read-only),
  auf die Personio-Oberfläche verweisen.
- **Netzwerk nicht erreichbar** → Verbindung prüfen, Skill erneut aufrufen.

## Wichtige Konventionen

- **Read-only ist nicht verhandelbar** — `personio.py` hat keinen Schreibbefehl.
- **Gehaltsdaten bleiben lokal** — kein Upload, keine MCP-Weiterleitung, keine
  Einzelgehälter im Chat.
- **Arbeitgeberkosten sind eine Schätzung** — Brutto × AG-Faktor. Diese Lesart
  steht in jedem Output (XLSX-Blatt „Annahmen", HTML-Report, Chat-Abschluss).
- Abgeleitete Kennzahlen bleiben leer (nicht `0`), wenn ihr Nenner 0 ist.
- Der HTML-Report ist die Interpretations-Schicht, die XLSX-Mappe die Detail-
  Schicht, `report-daten.json` die Maschinen-Schicht.
