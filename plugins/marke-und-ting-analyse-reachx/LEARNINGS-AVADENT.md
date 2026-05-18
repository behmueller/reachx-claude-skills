# Learnings aus der Avadent-MTA → Skill-Release 0.7.0

Dieses Dokument hält fest, **warum** das Release 0.7.0 die Skills so verändert hat, wie es
sie verändert hat. Es ist die Begründungs-Quelle hinter dem CHANGELOG-Eintrag — gedacht
als Nachschlagewerk für künftige Wartung.

## Woher die Learnings stammen

Die erste vollständige Live-MTA (Kundenprojekt „Avadent", Mai 2026) wurde nach Abschluss
ausgewertet. Quellen:

- der `status.md` des Projekts (vollständiger Lauf- und Re-Run-Verlauf),
- vier Feedback-/Projekt-Memories aus den Projekt-Sessions,
- ~19 MB Claude-Code-Session-Transkripte aus zwei Projektordnern.

Im Projektverlauf wurden Erkenntnisse erarbeitet, aber nicht in die Skills zurückgeführt.
Release 0.7.0 holt das nach. Die in 0.7.0 erstellten und geänderten Skills bleiben
generisch — „Avadent" wird dort nicht genannt, das Projekt ist nur die Erkenntnis-Quelle.
(Drei ältere Skill-Dateien aus dem First-Party-Strang nennen „Avadent" noch als
Live-Test-Beispiel — siehe Abschnitt „Bewusst nur teilweise gelöst / offen".)

## Übergreifende Änderungen

### `contracts.md` v2.2 — drei neue Querschnitts-Abschnitte

| Abschnitt | Learning dahinter |
|---|---|
| §11 MCP-Health-Checks & Credential-Disziplin | Apify-Sessions brachen nach PC-Standby ab (`Session ID not found`); Subagenten durchsuchten bei fehlendem Token Credential-Stores (`~/.zshrc`, `env\|grep`) und lösten einen Security-Block aus; Sistrix/Ahrefs waren bei Session-Start teils nicht verbunden. |
| §12 Synthese-Sequenz & Input-Staleness | `04-04-forecast` lief vor `04-03-ziele` mit stillem „hybrid"-Fallback → zwei MTA-Outputs mit ~50 % divergierenden Zahlen. Re-Runs von Audits machten die nachgelagerte Synthese unbemerkt veraltet. |
| §13 Kritische Haltung & Daten-Disziplin | Kunden-genannte Wettbewerber und -Ziele wurden ungeprüft übernommen; load-bearing Heuristiken (z.B. eine geschätzte Kapazitätsgrenze) waren nicht als Schätzung gekennzeichnet; eine Multi-Plattform-Review-Summe wurde als GMB-Zahl geführt; der Sistrix-VI wurde bei volatilen Kleinstwerten als Primär-Signal verwendet. |
| §3 ergänzt: Output-Reihenfolge | Ein Subagent wurde vor dem HTML-Report gekillt → `status.md` meldete „fertig", obwohl Outputs fehlten. Regel: inhaltliche Outputs vor `status.md`. |

### Agent-Definitionen

- **`mta-techniker`** (Haiku) hatte `status.md`-Einträge halluziniert (erfundene Follower-Zahlen, ausgedachte Befunde) und `index.html` beschädigt. Neu: erfindet keine Inhalte, schreibt `status.md`/`index.html` nur mit fertig übergebenem Text, validiert jeden Report.
- **`mta-rechercheur`** — MCP-Health-Check, Credential-Disziplin, Quellen-Kennzeichnung, keine erfundenen Daten.
- **`mta-stratege`** — Pflicht-Input-Check ohne Silent-Fallback, Staleness-/Konsistenz-Prüfung, Heuristik-Kennzeichnung, kritische Haltung gegenüber Kunden-Aussagen.

## Vier neue Skills

In der MTA ad hoc gebaut, jetzt feste generische Skills:

- **`02-05-wettbewerber-realitaets-check`** — kundengenannte Wettbewerber sind Hypothesen; dieser Skill verifiziert sie gegen Daten und klassifiziert nach realer Bedrohungslage. Läuft zwischen `02-02` und `02-03`.
- **`03-19-geo-ki-sichtbarkeit`** — GEO-Audit (Sichtbarkeit in ChatGPT/Gemini/Perplexity); in der MTA explizit gefordert, kein Skill vorhanden.
- **`03-20-local-gmb-wettbewerb`** — Wettbewerber-Vergleich mit Review-Velocity und Local-Visibility-Score; `03-16` lieferte nur den Kunden tief genug.
- **`04-07-segment-potenzial-matrix`** — segment-zentrierte Zweitsynthese; die kanal-zentrierten Skills `04-02/03/04` decken eine Segment-Sicht nicht ab.

## Härtungen bestehender Skills (Auswahl)

- **`03-02`** trennte lokale und generische Keywords nicht → Geo-vs-generisch-Klassifikation + Local-Pack-SERP-Check als Standard.
- **`03-03`** wies einen invisalign-getriebenen „generic"-Cluster als Top-Hebel aus → Artefakt-Warnung; vom Briefing ausgeschlossene Leistungen werden „geparkt".
- **`03-05`** wertete einen Akteur als „inaktiv", weil Ahrefs nur Search-Bidding sieht → Apify-Transparency-Center ist maßgeblich.
- **`03-14`** verlor alle PageSpeed-Daten an die API-Quota → `PAGESPEED_API_KEY`-Check, Begrenzung auf die Kunden-Domain ohne Key.
- **`04-02`** kannte GEO, Reddit und Facebook-organisch nicht als Kanäle → ergänzt; Apify-Konfidenz-Flag für Paid-Scores.
- **`04-01`** stallte beim Render des Mapping-SVG → SVG in eigene Datei ausgelagert.
- **`05-02`** konnte Re-Run-Duplikate auf Drive nicht aufräumen → De-Duplication-Pass.

Vollständige Liste der berührten Dateien: siehe Git-Diff von Release 0.7.0.

## Bewusst nur teilweise gelöst / offen

- **Report-Slot-Kollisionen** — Re-Runs vergaben kollidierende Report-Nummern (`08↔09`, `10` doppelt belegt). 0.7.0 hat **keine** zentrale Report-Registry eingeführt; die Skills prüfen ihre Nummer weiterhin zur Laufzeit gegen `reports/index.html`. Eine echte Registry bleibt ein offener Punkt für ein späteres Release. Verwandter Befund aus dem ersten First-Party-MTA-Lauf (`03-18-web-analytics-ga4`, Avadent): Auch das Dashboard-Update muss die Einfüge-Stelle in `reports/index.html` zur Laufzeit erraten, weil dessen HTML-Struktur nicht garantiert ist — der Skill suchte einen `</li>`-Anker, das Dashboard war aber tabellenbasiert (`<tr>`). Eine Report-Registry sollte daher nicht nur die Nummern vergeben, sondern auch die Einfüge-Struktur des Dashboards verbindlich definieren.
- **Skill-Discovery-Cache** — frisch installierte Skills erscheinen erst nach einem Session-Neustart. Das ist Harness-Verhalten und nicht per Skill behebbar; es ist nur in `01-01` dokumentiert.
- **„Avadent" als Beispiel in Alt-Bestand** — `03-04-seo-first-party-gsc` (SKILL.md + reference) sowie je eine reference-Datei von `02-02` und `05-02` nennen „Avadent" noch als Live-Test-Beispiel. Das stammt aus dem First-Party-Strang (Releases 0.5/0.6) und wurde in 0.7.0 bewusst nicht angefasst — sollte bei Gelegenheit generisch gemacht werden.
