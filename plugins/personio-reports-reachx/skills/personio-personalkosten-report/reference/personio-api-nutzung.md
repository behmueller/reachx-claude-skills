# Personio-API — Nutzung, Auth, Datenmodell

Referenz für das Wrapper-Skript `personio.py`. Der Skill ruft die API nie direkt
auf — er nutzt ausschließlich die drei CLI-Befehle des Skripts.

## 0. Read-only — kein Schreibbefehl

`personio.py` kann **nur lesen**. Es gibt bewusst keinen Befehl, der Daten in
Personio anlegt oder ändert. Die genutzten Endpunkte sind `POST /auth` (nur
Token-Erzeugung) und `GET /company/employees`. Mehr nicht.

## 1. Auth-Flow

Personio v1 nutzt einen proprietären Bearer-Token-Flow — **kein** Standard-OAuth.

1. `POST {base_url}/auth` mit JSON-Body `{"client_id": …, "client_secret": …}`.
2. Antwort: `{"success": true, "data": {"token": "…"}}`.
3. Der Token gilt rund 24 Stunden und wird als `Authorization: Bearer <token>`
   an alle weiteren Requests gehängt.
4. Personio rotiert den Token: Jede API-Antwort kann im `Authorization`-
   Response-Header einen frischen Token mitliefern. `personio.py` übernimmt
   diesen automatisch für den jeweils nächsten Request (`_next_token`).

Jeder CLI-Aufruf authentifiziert sich einmal frisch — es wird kein Token
zwischengespeichert.

`base_url` ist standardmäßig `https://api.personio.de/v1` und kann in
`personio.yaml` überschrieben werden (falls eine andere Personio-Instanz).

## 2. Credentials

- Datei: `~/.config/reachx-mta/personio.yaml`, Pfad überschreibbar via
  `REACHX_PERSONIO_CREDENTIALS`.
- Felder: `client_id`, `client_secret`, optional `base_url`.
- Erzeugt in Personio unter *Einstellungen > Integrationen > API-Zugänge >
  Neue API-Zugangsdaten generieren*.
- Rechte einschränken: `chmod 600`. Die Datei ist über `.gitignore` des Repos
  abgedeckt und gehört niemals in Versionskontrolle.

### Erforderliche Berechtigungen des API-Zugangs

Beim Anlegen der API-Zugangsdaten in Personio wird festgelegt, welche Endpunkte
und **welche einzelnen Mitarbeiter-Attribute** der Zugang lesen darf.

- **Pflicht:** Leserecht für den Mitarbeiter-Endpunkt (`Employees`).
- **Für die Kostenauswertung:** zusätzlich die Attribut-Freigabe für
  `fix_salary`, `fix_salary_interval`, `hourly_salary`, `bonus` — bzw. das
  Custom-Attribut, in dem das Gehalt geführt wird.

Nicht freigegebene Attribute erscheinen **gar nicht** in der API-Antwort (kein
Fehler, sie fehlen einfach). Genau deshalb prüft der `employees`-Befehl
`gehaltsfelder_vorhanden` und der `attributes`-Befehl hilft, ein abweichendes
Custom-Attribut zu finden.

## 3. Endpunkt `GET /company/employees`

- Liefert alle Mitarbeiter, paginiert über `limit` (max. 200) und `offset`.
- `personio.py` lädt alle Seiten in einer Schleife, bis eine Seite weniger als
  `limit` Einträge zurückgibt.
- Antwortstruktur:

```json
{
  "success": true,
  "metadata": {"total_elements": 142, "current_page": 1, "total_pages": 1},
  "data": [
    {"type": "Employee", "attributes": { … }}
  ]
}
```

## 4. Datenmodell — Mitarbeiter-Attribute

Jedes Attribut ist in ein Objekt verpackt:

```json
"fix_salary": {
  "label": "Fixgehalt",
  "value": 4500,
  "type": "standard",
  "universal_id": "fix_salary"
}
```

`personio.py` flacht das ab — pro Mitarbeiter entsteht eine `key → value`-Map.
Verschachtelte Objekte (z. B. `department`) werden auf ihren `name` reduziert.

### Für den Report relevante Standard-Attribute

| Schlüssel | Bedeutung | Hinweis |
|---|---|---|
| `id` | Personio-Mitarbeiter-ID | stabil |
| `first_name`, `last_name` | Name | bei `--anonym` durch Code ersetzt |
| `email` | E-Mail | nicht im Report verwendet |
| `status` | `active` / `inactive` / `onboarding` / `leave` | Filter-Basis |
| `position` | Stellenbezeichnung | |
| `department` | Abteilung | verschachteltes Objekt → Name |
| `employment_type` | `internal` / `external` | |
| `weekly_working_hours` | Wochenstunden | Basis der FTE-Rechnung; oft String |
| `hire_date` | Eintrittsdatum | ISO-Datum |
| `contract_end_date` | Vertragsende | ISO-Datum oder leer |
| `termination_date` | Austrittsdatum | ISO-Datum oder leer |
| `fix_salary` | Festgehalt | Betrag |
| `fix_salary_interval` | `monthly` / `yearly` | Intervall zu `fix_salary` |
| `hourly_salary` | Stundenlohn | für Stundenkräfte |
| `bonus` | Bonus | i. d. R. Jahresbetrag |

### Custom-Attribute

Unternehmensspezifische Felder haben Schlüssel der Form `dynamic_<zahl>`. Wird
das Gehalt in einem Custom-Attribut geführt, liefert `personio.py attributes`
Schlüssel, Label und Befüllungsquote — daraus den richtigen Schlüssel wählen und
`build-report.py --gehalt-attribut dynamic_<zahl>` setzen.

## 5. CLI-Befehle

| Befehl | Zweck |
|---|---|
| `personio.py auth-check` | Credentials + Erreichbarkeit prüfen |
| `personio.py employees [--include-inactive] [--out DATEI]` | alle Mitarbeiter als normalisiertes JSON |
| `personio.py attributes [--include-inactive]` | Attribut-Inventar (Schlüssel, Label, Befüllung) |

Ausgabe ist immer JSON. Bei Erfolg Exit-Code 0; bei jedem Konfig-, Auth- oder
API-Fehler Exit-Code 1 und `{"success": false, "error": "…"}` auf stderr.

## 6. Fehlerverhalten

| Situation | Verhalten |
|---|---|
| Credential-Datei fehlt / Platzhalter | sauberer Stopp mit Anleitung |
| PyYAML fehlt | Hinweis auf `pip3 install -r requirements-personio.txt` |
| HTTP 401 | Auth abgelehnt — Zugangsdaten / Zugang-Status prüfen |
| HTTP 403 | Berechtigung fehlt — mit reduziertem Datensatz weiter |
| HTTP 429 | Rate-Limit — kurz warten, erneut |
| HTTP 5xx / Netzwerk | Verbindung prüfen, erneut aufrufen |
| `success: false` im Body | Personio-Fehlercode + Meldung werden durchgereicht |

## 7. Grenzen der API

- Die API liefert das **vertragliche Bruttogehalt**, nicht die tatsächlichen
  Arbeitgeberkosten und keine Lohnabrechnungswerte. Die Arbeitgeberkosten im
  Report sind eine Hochrechnung (siehe `report-methodik.md`).
- Boni werden als einzelner Betrag geführt; ob jährlich oder monatlich, ist eine
  Annahme des Skills (`--bonus-intervall`).
- Variable Vergütung, Sachbezüge, betriebliche Altersvorsorge etc. sind über die
  Standard-Attribute nicht abgebildet — falls vorhanden, liegen sie in
  Custom-Attributen und müssten gezielt einbezogen werden.
