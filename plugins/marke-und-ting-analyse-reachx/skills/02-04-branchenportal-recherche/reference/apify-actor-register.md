# Apify-Actor-Register für Branchenportal-Recherche

Datiert getestete Apify-Actor-IDs für `02-04-branchenportal-recherche`. Bei jedem Skill-Lauf prüfen, ob ein Actor noch verfügbar ist. Bei Änderungen (Actor gelöscht, umbenannt, neue Version) diesen Eintrag aktualisieren.

**Pflege-Regel:** Wird ein Actor bei einem Skill-Lauf erfolgreich genutzt, Datum in `zuletzt_getestet` aktualisieren. Schlägt er fehl (Actor nicht gefunden, 402 Paid, oder Parsing-Fehler im Output), `status` auf `fehlgeschlagen` setzen und Kommentar ergänzen. So spart der nächste Lauf die Fehlersuche.

| Actor-Name | Actor-ID | Portal / Zweck | Zuletzt getestet | Status | Anmerkung |
|---|---|---|---|---|---|
| `apify/website-content-crawler` | `aYG0l9s7dbB7j3gbS` | Generisch (Methode A2, Bot-Protector-Portale) | 2026-05-15 | ok | Playwright+Residential-Proxy; Pflicht für Jameda |
| `compass/google-maps-scraper` | — | Google Business Profile / Google Maps | — | ungetestet | Alternative: `apify/google-maps-extractor` |
| `apify/trustpilot-scraper` | — | Trustpilot | — | ungetestet | — |
| `maxcopell/tripadvisor` | — | TripAdvisor | — | ungetestet | Alternative: `apify/tripadvisor-scraper` |
| `apify/puppeteer-scraper` | — | Generisch (Methode C, Portal-interne Suche) | — | ungetestet | Basis-Actor für Custom-Scripts |

## Login-Wall / Bot-Protection — manueller Fallback (Methode D)

Folgende Portale konnten in Tests nicht automatisch gescraped werden und erfordern manuellen Datenabruf durch den Strategen. **Kein endloses Actor-Durchprobieren** — sobald ein Portal als Methode D klassifiziert ist, direkt als `recherche_fehlgeschlagen` markieren und im Schluss-Format auf den manuellen Fallback hinweisen.

| Portal | Grund | Manueller Fallback |
|---|---|---|
| Jameda (Login-Bereiche) | Bot-Protector aktiv (getestet 2026-05-15); öffentliche Profil-Seiten über A2 erreichbar, Login-geschützte Review-Details nicht | Öffentliche Profil-URL manuell aufrufen; sichtbare Note + Anzahl Bewertungen notieren |
| G2 (Detail-Ansicht) | Login-Wall für tiefere Review-Daten | Basis-Daten (Score, Reviews-Count) oft über Google-Snippet extrahierbar (Methode B); tiefere Daten: manuell |
| Facebook-Unternehmensseiten | Login-Wall für vollständige Post-Daten | Öffentlich sichtbare Kennzahlen (Follower-Count, Rating) über `rag-web-browser` auf `facebook.com/<page>` |

**Hinweis für neue Portale:** Vor dem ersten Scrape-Versuch prüfen, ob das Portal auf dieser Liste steht. Wenn ja, direkt Methode D einsetzen — keine Zeit mit Methode B/C verschwenden, wenn ein Login erforderlich ist.
