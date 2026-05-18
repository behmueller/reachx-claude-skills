# Output-Schema — Wettbewerber-Realitäts-Check

Format der beiden inhaltlichen Outputs von `02-05-wettbewerber-realitaets-check`:

- `wettbewerber/realitaets-check.md` — das Aggregat (Markdown + YAML-Frontmatter)
- `wettbewerber/realitaets-check.csv` — die Signal-Tabelle (eine Zeile pro Akteur)

Beide sind **ab diesem Skill die maßgebliche Wettbewerbs-Datenbasis** — `02-03-wettbewerber-marken-profil`, `02-04-branchenportal-recherche` und die Synthese-Stufe lesen die Klassifikation, um Profilier-Tiefe und Bedrohungs-Gewichtung zu steuern.

---

## 1. `wettbewerber/realitaets-check.csv`

Eine Kopfzeile, danach eine Zeile pro Akteur. Komma-getrennt, UTF-8, Werte mit Komma in doppelten Anführungszeichen.

### Spalten

| Spalte | Inhalt |
|---|---|
| `name` | Akteurs-Name aus `liste.md` |
| `website` | URL (leer, wenn keine bekannt) |
| `kategorie` | `kunde_genannt` / `regional` / `best_practice_ueberregional` (aus `liste.md`) |
| `quelle_zusatz` | `first_party_signal` oder leer (aus `liste.md`) |
| `soll_bedrohungsgrad` | Kunden-Einschätzung: `direkt` / `indirekt` / `inspiration` / `nicht_genannt` |
| `sig_sichtbarkeit` | `stark` / `mittel` / `schwach` / `unbekannt` |
| `sichtbarkeit_dr` | Ahrefs-Domain-Rating, numerisch — leer, wenn nicht erhoben |
| `sichtbarkeit_vi` | Sistrix-Sichtbarkeitsindex, numerisch — leer, wenn nicht erhoben |
| `sichtbarkeit_vi_konfidenz` | `ok` / `niedrig` — `niedrig` bei VI < 0,05 (Volatilitäts-Disziplin) |
| `sig_lokale_relevanz` | `stark` / `mittel` / `schwach` / `neutral` (`neutral` bei nationalem Kunden) |
| `distanz_km` | Distanz Akteur ↔ Kunden-Standort in km — leer bei neutraler Achse |
| `gmb_rating` | Google-Maps-Rating (aus `liste.md`) — leer, wenn unbekannt |
| `gmb_reviews` | Anzahl Google-Maps-Reviews (aus `liste.md`) — leer, wenn unbekannt |
| `sig_paid_aktivitaet` | `stark` / `mittel` / `schwach` / `unbekannt` |
| `sig_website_marken_staerke` | `stark` / `mittel` / `schwach` / `unbekannt` |
| `realitaets_score` | normierter Score 0,00–1,00 (siehe `klassifikations-schema.md` Abschnitt 2) |
| `klasse` | **Ist** — `aktuell_stark` / `latente_bedrohung` / `nachrangig` |
| `soll_ist_befund` | `bestaetigt` / `teilweise_bestaetigt` / `ueberschaetzt` / `unterschaetzt` / `blinder_fleck` / `latente_bedrohung_uebersehen` |
| `konfidenz` | `ok` / `niedrig` (≥ 3 Achsen `unbekannt` → `niedrig`) |
| `begruendung` | Ein-Satz-Begründung der Klasse (datengestützt) |

### Beispiel

```csv
name,website,kategorie,quelle_zusatz,soll_bedrohungsgrad,sig_sichtbarkeit,sichtbarkeit_dr,sichtbarkeit_vi,sichtbarkeit_vi_konfidenz,sig_lokale_relevanz,distanz_km,gmb_rating,gmb_reviews,sig_paid_aktivitaet,sig_website_marken_staerke,realitaets_score,klasse,soll_ist_befund,konfidenz,begruendung
Verwaltung Müller,https://verwaltung-mueller.de,kunde_genannt,,direkt,mittel,22,0.08,ok,stark,4.2,4.5,90,mittel,mittel,0.67,aktuell_stark,bestaetigt,ok,"Im Einzugsgebiet mit starker GMB-Präsenz; solide Sichtbarkeit — realer Wettbewerber."
Hausservice Klein,https://hausservice-klein.de,kunde_genannt,,direkt,unbekannt,,0.01,niedrig,schwach,40.0,4.1,12,schwach,schwach,0.11,nachrangig,ueberschaetzt,niedrig,"Außerhalb des Einzugsgebiets, keine Paid-Aktivität, dünne Marke — datenseitig nachrangig."
ImmoProfi,https://immoprofi.de,best_practice_ueberregional,,nicht_genannt,stark,51,0.62,ok,schwach,120.0,,,stark,stark,,latente_bedrohung,latente_bedrohung_uebersehen,ok,"Überregional stark in Sichtbarkeit und Paid; lokal noch nicht aktiv — könnte ins Einzugsgebiet expandieren."
```

Hinweis: Bei einem Akteur, der über eine Override-Regel klassifiziert wurde (z. B. `latente_bedrohung`), kann das `realitaets_score`-Feld leer bleiben — dann trägt die Override-Regel die Klasse, nicht der Score. Die `begruendung` nennt in dem Fall die Regel sinngemäß.

---

## 2. `wettbewerber/realitaets-check.md`

### YAML-Frontmatter

```yaml
---
skill: 02-05-wettbewerber-realitaets-check
generiert_am: <ISO-8601>
schema_version: "1.0"

# Provenienz
basiert_auf:
  - datei: wettbewerber/liste.md
    generiert_am: <ISO-8601 aus liste.md>
    status: bestaetigt

# Erhebungs-Kontext
lokale_achse_aktiv: <true | false>   # false bei nationalem/Online-Kunden
einzugsradius_km: <int | null>       # null bei neutraler lokaler Achse — Quellen-Typ: benchmark
mcp_status:
  sistrix: <erreichbar | reduced | aus>
  ahrefs: <erreichbar | reduced | aus>
  apify: <erreichbar | reduced | aus>

# Verteilung
akteure_gesamt: <int>
anzahl_aktuell_stark: <int>
anzahl_latente_bedrohung: <int>
anzahl_nachrangig: <int>
anzahl_soll_ist_abweichungen: <int>
anzahl_konfidenz_niedrig: <int>

# Klassifikation pro Akteur
akteure:
  - name: <Akteurs-Name>
    kategorie: <kunde_genannt | regional | best_practice_ueberregional>
    soll_bedrohungsgrad: <direkt | indirekt | inspiration | nicht_genannt>  # quelle_typ: briefing
    signale:
      sichtbarkeit: <stark | mittel | schwach | unbekannt>          # quelle_typ: erhoben
      lokale_relevanz: <stark | mittel | schwach | neutral>          # quelle_typ: erhoben
      paid_aktivitaet: <stark | mittel | schwach | unbekannt>        # quelle_typ: erhoben
      website_marken_staerke: <stark | mittel | schwach | unbekannt> # quelle_typ: erhoben
    realitaets_score: <float | null>
    klasse: <aktuell_stark | latente_bedrohung | nachrangig>         # Ist
    soll_ist_befund: <bestaetigt | teilweise_bestaetigt | ueberschaetzt | unterschaetzt | blinder_fleck | latente_bedrohung_uebersehen>
    konfidenz: <ok | niedrig>
---
```

**Quellen-Kennzeichnung (Pflicht, `contracts.md` Abschnitt 13):** Der `soll_bedrohungsgrad` ist immer `briefing` (unverifizierte Kundenaussage). Die vier `signale` sind `erhoben` (aus MCP gemessen oder aus `liste.md` übernommen, die ihrerseits erhoben hat). Der `einzugsradius_km` ist `benchmark` (Reference-Wert aus `klassifikations-schema.md`). Der `realitaets_score` und die `klasse` sind `schaetzung_skill` — regelbasiert abgeleitet; das ist im Body transparent zu machen.

### Markdown-Body

```markdown
# Wettbewerber-Realitäts-Check: <Kundenname>

## Kernbefund

<Verdichteter Absatz: Wie viele Akteure verifiziert, wie verteilt sich die
Bedrohungslage, was ist die wichtigste Soll-Ist-Abweichung. Dies ist die
Kernaussage für den Strategen — die MTA übernimmt ab hier diese Klassifikation
statt der ungeprüften Kunden-Einschätzung.>

## Klassifikations-Übersicht

| Akteur | Kategorie | Klasse (Daten) | Soll (Kunde) | Soll-Ist-Befund |
|---|---|---|---|---|
| <Name> | <Kategorie> | <Klasse> | <Bedrohungsgrad> | <Befund> |
| … | | | | |

Verteilung: <X> aktuell_stark · <Y> latente_bedrohung · <Z> nachrangig.

## Akteure im Detail

### <Akteurs-Name> — <Klasse>

- **Kategorie:** <kunde_genannt | regional | best_practice_ueberregional>
- **Kunden-Einschätzung (Soll):** <Bedrohungsgrad> — <kurzer Kontext aus dem Briefing, falls vorhanden>
- **Signale (Ist):**
  - Sichtbarkeit: <Stufe> — <DR / VI mit Wert; bei VI < 0,05: Volatilitäts-Hinweis>
  - Lokale Relevanz: <Stufe> — <Distanz in km, GMB-Stärke; oder "neutral — nationaler Kunde">
  - Paid-Aktivität: <Stufe> — <welche Kanäle erkannt>
  - Website-/Marken-Stärke: <Stufe> — <kurze Beobachtung>
- **Realitäts-Score:** <Wert> → **Klasse: <Klasse>**
- **Begründung:** <datengestützter Satz — welche Signale die Klasse tragen, ggf. welche Override-Regel griff>
- **Soll-Ist-Abgleich:** <Befund + ein Satz: deckt sich die Kunden-Einschätzung mit den Daten, oder weicht sie ab — und in welche Richtung>

(weitere Akteure …)

## Auffälligkeiten

⚠ **Soll-Ist-Abweichungen und strategische Befunde:**

- <Akteur X> — vom Kunden als `direkt`-Konkurrent genannt, datenseitig `nachrangig`: <ein Satz Konsequenz>
- <Akteur Y> — `latente_bedrohung`, vom Kunden nicht erwähnt: <warum er beobachtet werden sollte>
- <Akteur Z> — `aktuell_stark`, aber nur als `inspiration` genannt: blinder Fleck
- <weitere strategie-relevante Beobachtungen über die Akteurs-Gruppe>

## Konsequenz für die Folge-Skills

<Kurzer Absatz: Welche Akteure sollte 02-03-wettbewerber-marken-profil
priorisiert profilieren (aktuell_stark + latente_bedrohung), welche kann es
nachrangig behandeln. Hinweis, dass diese Klassifikation ab hier die
maßgebliche Wettbewerbs-Datenbasis ist.>
```

---

## 3. Befund-Werte (Soll-Ist)

Die `soll_ist_befund`-Werte und ihre Bedeutung — vollständige Mapping-Tabelle in `klassifikations-schema.md` Abschnitt 4:

| Wert | Bedeutung | Abweichung? |
|---|---|---|
| `bestaetigt` | Kunden-Einschätzung deckt sich mit der Datenlage | nein |
| `teilweise_bestaetigt` | Kunde sieht `direkt`-Bedrohung, Daten sagen `latente_bedrohung` — relevant, aber heute nicht akut | ja |
| `ueberschaetzt` | Kunde nennt `direkt`, Daten sagen `nachrangig` | ja |
| `unterschaetzt` | Kunde sieht den Akteur als zweitrangig/`inspiration`, Daten sagen `aktuell_stark` | ja |
| `blinder_fleck` | Akteur `aktuell_stark`, vom Kunden gar nicht oder nur als `inspiration` genannt | ja |
| `latente_bedrohung_uebersehen` | Akteur `latente_bedrohung`, vom Kunden nicht erwähnt | ja |

Alle Werte mit „ja" in der Abweichungs-Spalte zählen in `anzahl_soll_ist_abweichungen`, erscheinen im Auffälligkeiten-Block und im Schluss-Format.

---

## 4. Wie Folge-Skills diese Dateien lesen

- **`02-03-wettbewerber-marken-profil`:** liest die `klasse` pro Akteur. Empfehlung: `aktuell_stark` und `latente_bedrohung` voll profilieren, `nachrangig` nur, wenn der Stratege es ausdrücklich will. Der Realitäts-Check ergänzt damit die `empfehlung_profilieren`-Logik aus `liste.md` um eine datengestützte Priorisierung.
- **`02-04-branchenportal-recherche`:** kann die Klassifikation nutzen, um die Portal-Recherche auf die real relevanten Akteure zu fokussieren.
- **Synthese-Stufe (04-*):** nutzt die Bedrohungs-Klassifikation für die Wettbewerbs-Gewichtung in der Positionierungs- und Kanal-Chancen-Analyse.

Konvention: Folge-Skills schreiben **nicht** in `realitaets-check.md`/`.csv` zurück. Erheben sie neue Daten zu einem Akteur, gehört das in ihren eigenen Output. Wird `liste.md` nach diesem Lauf geändert, ist `02-05` erneut auszuführen — der Realitäts-Check verifiziert dann das vollständige neue Akteur-Set.
