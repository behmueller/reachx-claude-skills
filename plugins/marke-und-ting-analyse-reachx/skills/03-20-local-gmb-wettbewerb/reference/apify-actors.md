# Apify-Actors für den Local-GMB-Wettbewerbsvergleich

Datierte Actor-IDs und Tool-Kaskade für Phase B. Apify ist **Pflicht-MCP** — ohne Apify bricht der Skill ab (siehe `contracts.md` Abschnitt 11).

## Credential und Health-Check

```bash
[ -n "$APIFY_TOKEN" ] || { echo "✗ APIFY_TOKEN nicht gesetzt."; exit 1; }
```

Keine breite Credential-Suche — ausschließlich `APIFY_TOKEN` testen (`contracts.md` Abschnitt 11).

**Health-Check** vor dem ersten echten Scrape (nicht nur am Skill-Start): billiger Test-Call `search-actors` mit Limit 1. Schlägt er fehl → Abbruch mit Reconnect-Hinweis. Apify-Sessions überleben PC-Standby nicht (`Session ID not found`) und werden von parallelen Clients (Codex, zweite Claude-Session) auf demselben Token invalidiert. Bei Session-Bruch im Lauf: **abbrechen mit Reconnect-Hinweis**, bereits geschriebene Teil-Outputs erwähnen — nicht jeden weiteren Akteur einzeln scheitern lassen.

## 1. GMB-Profil- und Review-Scrape

### Bevorzugt: `compass/google-maps-scraper`

| Feld | Wert |
|---|---|
| `actor` | `compass/google-maps-scraper` |
| `zuletzt_getestet` | 2026-05-17 |
| `status` | aktiv — liefert Profil-Daten, Medien-Count, Reviews mit Datum |

- Input: Google-Maps-URL (`startUrls` / `placeIds`) wenn die GMB-URL aus `data/kunde.md` oder `standorte_kunde[].gmb_url` extrahierbar ist; sonst Suchbegriff (`searchStringsArray: ["<name> <stadt>"]`).
- Reviews: `maxReviews: 150`, `reviewsSort: "newest"`, `reviewsStartDate` ggf. auf heute − 13 Monate setzen, um die Velocity-Buckets sicher abzudecken.
- Liefert pro Place: Name, Adresse, Telefon, Website, Kategorien (Haupt + Sub), Attribute, Öffnungszeiten, Beschreibung, Foto-Count, `reviewsCount`, `totalScore`, Reviews-Array (jedes mit `publishedAtDate`, `stars`, `text`, `responseFromOwnerText`/`responseFromOwnerDate`).
- **Velocity-kritisch**: das `publishedAtDate`-Feld pro Review ist Pflicht für die Bucket-Berechnung. Liefert der Actor nur relative Datumsangaben ("vor 2 Monaten"), in absolute Daten umrechnen (Lauf-Datum minus Offset) und im Output mit `datum_approx: true` markieren.

### Alternative: `apify/google-maps-extractor`

| Feld | Wert |
|---|---|
| `actor` | `apify/google-maps-extractor` |
| `zuletzt_getestet` | 2026-05-17 |
| `status` | aktiv — Fallback, andere Default-Felder |

Einsatz, wenn `compass/google-maps-scraper` Probleme macht (Rate-Limit, leere Reviews). Funktional ähnlich.

### Letzter Fallback: manuelle Profil-Erfassung

Web-Search nach `<name> google maps` → zentrale Profil-Felder und Gesamt-Rating/-Anzahl. **Keine** Reviews mit Datum → keine Velocity. Reduced-Modus: Block B ohne `vel_score` (siehe `lvs-methodik.md`), LVS-Konfidenz `niedrig`, Auffälligkeit `velocity_nicht_erhebbar`.

## 2. Local-Pack-Rankings

### Bevorzugt: `compass/google-maps-scraper` mit Geo-Suche

Pro Standort × Local-Pack-Keyword ein Call: `searchStringsArray: ["<keyword>"]`, `customGeolocation` mit Lat/Lng des Standorts und `radiusKm` aus `suchradius_km`. Output: Maps-Ergebnis-Liste in Reihenfolge → Position 1–10 ableiten.

| Feld | Wert |
|---|---|
| `actor` | `compass/google-maps-scraper` |
| `zuletzt_getestet` | 2026-05-17 |
| `status` | aktiv — liefert geo-lokalisierte Ergebnis-Reihenfolge |

Bei 12 Keywords × 1 Standort = 12 Calls (typischer Lauf).

### Alternative: dedizierter Local-Pack-Scanner

Wenn ein dedizierter Local-Pack-Actor verfügbar und getestet ist, hier mit datierter ID eintragen. Stand 2026-05-17 wird der `compass/google-maps-scraper` mit Geo-Suche als robust genug bewertet — kein separater Pack-Scanner nötig.

### Web-Search-Fallback (Reduced-Modus)

Bei erschöpften Apify-Credits: Local-Pack-Snippets per Web-Search. Nur Top-3 zuverlässig erfassbar. Im Output `quelle: web_search`, `tiefe: top_3_nur`. Block A wird dann nur aus `top3_quote` gebildet (`top10_quote` = `top3_quote` gesetzt), LVS-Konfidenz `niedrig`.

### Tool-Wahl-Kaskade Local-Pack

```
1. compass/google-maps-scraper mit Geo-Suche
2. apify/google-maps-extractor mit Geo-Suche
3. Web-Search (Reduced-Modus, nur Top-3)
```

## 3. Apify-Credit-Strategie

Typischer Lauf (Kunde + 5 WB, 1 Standort, 12 Local-Pack-Keywords):

| Tätigkeit | Calls | Compute-Units (CU, grob) |
|---|---|---|
| GMB-Profil + Reviews × 6 Akteure (Sample 150) | 6 | ~18 CU |
| Local-Pack-Queries 12 × 1 Standort | 12 | ~6 CU |
| **Summe pro Lauf** | ~18 | **~24 CU** |

Bei großen Läufen (10 WB, 3 Standorte, 30 Keywords): linear hochrechnen. Übersteigt der erwartete Verbrauch ~100 CU, im Schema-Body Vorab-Warnung und Vorschlag, Standorte oder Keywords zu priorisieren.

## 4. Cache-Strategie

Pro Akteur und Standort ein Roh-Cache, lokal in `~/.cache/reachx-mta/<slug>/`, am Ende nach Drive `assets/raw/gmb-wettbewerb-<slug>.json` (Filialen `-<standort>` suffigiert):

```json
{
  "akteur_slug": "alpha-zahnarzt",
  "standort_id": "hauptsitz",
  "scrape_datum": "2026-05-17T11:00:00Z",
  "apify_actor": "compass/google-maps-scraper",
  "raw": { "...": "vollständiges Apify-Result" }
}
```

Bei Re-Run: ist der Cache jünger als 14 Tage, kein erneuter Apify-Call — die Velocity-Buckets ändern sich in 14 Tagen nur marginal.

## 5. Reduced-Modi (Übersicht)

| Bedingung | Reduced-Modus | LVS-Folge |
|---|---|---|
| Reviews nicht scrapebar (Bot/Rate-Limit) | nur Profil-Reife + Local-Pack | Block B ohne `vel_score`, Konfidenz `niedrig`, `velocity_nicht_erhebbar` |
| Reviews ohne absolutes Datum | relative Daten umrechnen | `datum_approx: true` pro betroffenem Review |
| Sample deckt keine 12 Monate ab | `velocity_12m` als untere Schranke | `velocity_12m_mind: true` |
| Local-Pack nur per Web-Search | nur Top-3 | Block A nur aus `top3_quote`, Konfidenz `niedrig` |
| Apify-Credits fast erschöpft | Review-Sample auf 50 reduzieren | Velocity der älteren Buckets evtl. unvollständig |

Jeder aktive Reduced-Modus wird im Markdown- und HTML-Output explizit dokumentiert (`reduced_modi`-Liste im Frontmatter).

## 6. Bekannte Limits

- **GMB-Insights nicht scrapebar**: Profil-Aufrufe, Wegbeschreibungs-Klicks, Anrufe sind Inhaber-only. Wenn der Kunde diese teilt: manueller Block, nicht Teil des LVS.
- **Reviews-Filterung durch Google**: Spam-/Fake-Reviews werden von Google ausgeblendet — das Sample ist nicht zwingend vollständig. Hinweis im Body.
- **Local-Pack-Personalisierung**: Google personalisiert nach Such-Historie. Der Scraper liefert den "unsearched" Local-Pack — derselbe Ausgangspunkt für alle Akteure, kann aber von realen Nutzern abweichen.
- **Login-Wall**: GMB-Profile und Maps-Ergebnisse sind öffentlich — keine Login-Wall-Problematik wie bei Facebook-Posts oder der LinkedIn Ad Library.
