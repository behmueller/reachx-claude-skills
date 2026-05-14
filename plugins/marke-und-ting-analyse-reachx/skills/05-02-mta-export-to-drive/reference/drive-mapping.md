# Drive-Mapping: Lokale Pfade → Drive-Ordner-Struktur

Definiert die **vollständige Ziel-Struktur** im Google-Drive für eine exportierte MTA, plus die exakte Mapping-Tabelle zwischen lokalen Projekt-Pfaden und Drive-Pfaden. Inkludiert Dateiformat-Konvertierungs-Regeln und Unicode-Normalisierung.

## Drive-Root-Konvention

```
/MTA-PROJEKTE/<KUNDE> - MTA - <YYYY-MM>/
```

- `<KUNDE>` = Anzeige-Name aus `meta.json.kunde` (mit korrektem Casing, NICHT der Slug)
- `<YYYY-MM>` = Monat des Drive-Exports (nicht zwingend Kickoff-Datum)
- Beispiele:
  - `/MTA-PROJEKTE/Mueller Bauunternehmen - MTA - 2026-05/`
  - `/MTA-PROJEKTE/Aufmaster - MTA - 2026-04/`
  - `/MTA-PROJEKTE/Avadent GmbH - MTA - 2026-05/`

Der übergeordnete `/MTA-PROJEKTE/`-Ordner muss im Drive vorhanden sein oder wird vom Skill mit angelegt.

### Mac/Windows-Kompatibilität

Drive Desktop Sync läuft auf beiden Plattformen. Damit der Ordner überall identisch synct, gelten:

- **Unicode-Normalisierung (NFC)** auf Ordnernamen anwenden (`unicodedata.normalize("NFC", name)`)
- **Verbotene Zeichen** in Ordner- und Dateinamen ersetzen:
  - `/` → `-` (auf macOS/Drive ungültig im Filename, nur als Pfadtrenner)
  - `\` → `-` (Windows-Pfadtrenner)
  - `:`, `*`, `?`, `"`, `<`, `>`, `|` → `-` (Windows-illegal)
  - Führende/abschließende Leerzeichen und Punkte trimmen (Windows-Quirk)
- **Maximale Pfadlänge**: 260 Zeichen (Windows-Limit) — bei Überlauf Sektion-Slug kürzen
- **Case-Sensitivity**: Drive behandelt Filenames als case-preserving aber case-insensitive für Konflikte → keine zwei Files mit nur unterschiedlichem Casing im selben Ordner

## Vollständige Ziel-Struktur

```
<KUNDE> - MTA - <YYYY-MM>/
├── README.md                                        ← (generiert, Pflicht-Lese-Reihenfolge)
├── 01-Briefing/
│   ├── briefing.md                                  ← data/briefing.md
│   └── 01-briefing.html                             ← reports/01-briefing.html
├── 02-Marken-Profile/
│   ├── kunde.md                                     ← data/kunde.md
│   ├── abweichungen.md                              ← data/abweichungen.md (falls vorh.)
│   ├── 02-kunde.html                                ← reports/02-kunde.html
│   ├── 02b-abweichungen.html                        ← reports/02b-abweichungen.html (falls vorh.)
│   └── wettbewerber/
│       ├── liste.md                                 ← wettbewerber/liste.md
│       ├── 03-wettbewerber-liste.html               ← reports/03-wettbewerber-liste.html
│       ├── 04-wettbewerber-profile.html             ← reports/04-wettbewerber-profile.html (Bundle)
│       ├── <slug-1>.md                              ← wettbewerber/<slug-1>.md
│       ├── <slug-2>.md                              ← wettbewerber/<slug-2>.md
│       └── ...
├── 03-Audits/
│   ├── SEO/
│   │   ├── gsc-first-party.md                       ← audits/gsc-first-party.md (optional, nur wenn GSC angebunden)
│   │   ├── gsc-performance.csv                      ← audits/gsc-performance.csv
│   │   ├── gsc-pages.csv                            ← audits/gsc-pages.csv
│   │   ├── seo-sichtbarkeit.md                      ← audits/seo-sichtbarkeit.md
│   │   ├── seo-keywords.csv                         ← audits/seo-keywords.csv
│   │   ├── seo-rankings-ahrefs.csv                  ← audits/seo-rankings-ahrefs.csv (optional, nur im Hybrid- oder Ahrefs-only-Modus)
│   │   ├── seo-keyword-pool.csv                     ← audits/seo-keyword-pool.csv
│   │   ├── seo-keyword-pool.md                      ← audits/seo-keyword-pool.md
│   │   ├── seo-keyword-cluster.csv                  ← audits/seo-keyword-cluster.csv
│   │   ├── seo-cluster-zusammenfassung.md           ← audits/seo-cluster-zusammenfassung.md
│   │   ├── 05a-gsc-first-party.html                 ← reports/05a-gsc-first-party.html
│   │   ├── 06-seo-sichtbarkeit.html                 ← reports/06-seo-sichtbarkeit.html
│   │   ├── 07-03-02-seo-keyword-recherche.html            ← reports/07-03-02-seo-keyword-recherche.html
│   │   └── 08-03-03-seo-keyword-kategorisierung.html      ← reports/08-03-03-seo-keyword-kategorisierung.html
│   ├── Ads/
│   │   ├── 03-05-sea-google-ads-check.md                      ← audits/03-05-sea-google-ads-check.md
│   │   ├── meta-ads-library.md                      ← audits/meta-ads-library.md
│   │   ├── linkedin-ads-library.md                  ← audits/linkedin-ads-library.md
│   │   └── 09-ads-*.html                            ← reports/09-ads-*.html
│   ├── Website/
│   │   ├── web-tech-tracking.md                          ← audits/web-tech-tracking.md
│   │   ├── content-inventur.md                      ← audits/content-inventur.md
│   │   └── 10-website-*.html                        ← reports/10-website-*.html
│   ├── Local/
│   │   ├── gmb-local-seo.md                         ← audits/gmb-local-seo.md
│   │   ├── branchenportale.md                       ← wettbewerber/portale.md
│   │   └── 11-local-*.html                          ← reports/11-local-*.html
│   └── Social/
│       ├── linkedin-competitor.md                   ← audits/linkedin-competitor.md
│       ├── instagram-competitor.md                  ← audits/instagram-competitor.md
│       ├── tiktok-competitor.md                     ← audits/tiktok-competitor.md
│       ├── pinterest-competitor.md                  ← audits/pinterest-competitor.md
│       └── 12-social-*.html                         ← reports/12-social-*.html
├── 04-Synthese/
│   ├── positionierung.md                            ← synthese/positionierung.md
│   ├── positionierung-mapping.svg                   ← synthese/positionierung-mapping.svg (falls vorh.)
│   ├── kanal-chancen.md                             ← synthese/kanal-chancen.md
│   ├── kanal-chancen.csv                            ← synthese/kanal-chancen.csv
│   ├── ziele.md                         ← synthese/ziele.md
│   ├── forecast.md                                  ← synthese/forecast.md
│   ├── forecast.xlsx                                ← synthese/forecast.xlsx
│   ├── 90-tage-plan.md                              ← synthese/90-tage-plan.md
│   ├── retainer.md                                  ← synthese/retainer.md
│   ├── retainer.xlsx                                ← synthese/retainer.xlsx
│   ├── 13a-positionierung.html                      ← reports/13a-positionierung.html
│   ├── 13b-kanal-chancen.html                       ← reports/13b-kanal-chancen.html
│   ├── 13c-forecast.html                            ← reports/13c-forecast.html
│   ├── 13d-90-tage-plan.html                        ← reports/13d-90-tage-plan.html
│   └── 13e-retainer.html                            ← reports/13e-retainer.html
├── 05-Slide-Bausteine/
│   └── (rekursiv aus synthese/slide-bausteine/)     ← synthese/slide-bausteine/
├── 06-Roh-Daten/
│   ├── audits-raw.zip                               ← audits/raw/ als ZIP gepackt (falls < 2 GB)
│   └── assets/                                      ← assets/ (rekursiv)
└── 07-Reports-Index/
    ├── index.html                                   ← reports/index.html (Dashboard)
    └── _shell.html                                  ← reports/_shell.html (technische Vorlage)
```

## Mapping-Regeln

1. **Numerisches Präfix bleibt erhalten** in den HTML-Reports — der Stratege findet sie in derselben Reihenfolge wie lokal.
2. **HTML-Reports wandern in die inhaltlich passende Sektion** (z. B. `06-seo-sichtbarkeit.html` landet unter `03-Audits/SEO/`, nicht in einem flachen `reports/`-Ordner).
3. **Markdown-Outputs landen inhaltlich gruppiert** — direkt neben dem zugehörigen HTML-Report.
4. **Wettbewerber-Einzelprofile** kommen in `02-Marken-Profile/wettbewerber/` — sie gehören thematisch zur Marken-Analyse, nicht zu den Audits.
5. **Roh-Daten unter `06-Roh-Daten/`** als ZIP gepackt — Stratege hat sie zur Hand, aber sie clutter nicht die Inhalts-Sektionen. ZIP wird vom Skill on-the-fly gebaut, niemals lokal persistent.
6. **`reports/_shell.html` wird trotzdem in `07-Reports-Index/` hochgeladen** — falls Stratege das Dashboard re-rendern oder nachbearbeiten will.
7. **`reports/index.html` wird zu `07-Reports-Index/index.html` im Drive** — Stratege erreicht es über die README.md-Verlinkung.
8. **README.md im Drive-Root** wird vom Skill **generiert**, nicht aus dem lokalen Projekt kopiert — Inhalt siehe `export-output-schema.md`.

## Dateiformat-Konvertierungs-Regeln

| Lokale Endung | Drive-Endung | Konvertierung | Begründung |
|---|---|---|---|
| `.md` | `.md` | keine | Drive rendert Markdown nativ als Preview |
| `.html` | `.html` | keine | Drive-HTML-Viewer reicht; KEINE Google-Doc-Konvertierung |
| `.xlsx` | `.xlsx` | keine (Native) | Forecast/Retainer haben komplexe Formeln, die Google Sheets bricht |
| `.csv` | `.csv` | keine | Drive zeigt CSV nativ; KEINE Sheets-Konvertierung (verändert Encoding) |
| `.json` | `.json` | keine | Roh-Daten bleiben Roh |
| `.svg` | `.svg` | keine | Drive rendert SVG als Bild-Preview |
| `.png`, `.jpg`, `.gif` | identisch | keine | Bild-Viewer |
| `.zip` | `.zip` | keine | Bei Roh-Daten und Reduced-Modus: bleibt Archiv |

**Override** (selten genutzt): Wenn der Stratege explizit will, dass XLSX zu Google Sheets konvertiert wird, per Override-Flag `convert_xlsx_to_sheets: true`. Standard ist **nicht konvertieren**.

## Mime-Types für Upload

Pro Endung das richtige MIME beim Upload setzen:

| Endung | MIME |
|---|---|
| `.md` | `text/markdown` |
| `.html` | `text/html` |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| `.csv` | `text/csv` |
| `.json` | `application/json` |
| `.svg` | `image/svg+xml` |
| `.png` | `image/png` |
| `.jpg` | `image/jpeg` |
| `.zip` | `application/zip` |

Wichtig: Wenn das MIME fehlt, raten manche Drive-API-Implementierungen falsch (z. B. `application/octet-stream` für `.md`), und der Stratege bekommt keinen schönen Preview.

## Sonderfälle

### Sehr großer `slide-bausteine/`-Ordner

Wenn `synthese/slide-bausteine/` mehr als 100 HTML-Dateien enthält:

- Upload bleibt rekursiv, aber als **Bulk-Operation** (gws-CLI: `gws drive files create --recursive`, API: parallele Uploads mit Pool-Size 5)
- Im Manifest als Sammel-Eintrag listen, nicht jeder einzelne Slide-Baustein
- Drive-Link pro Slide-Baustein-Datei kann optional im Manifest sein (Override-Flag) — Default: nur Sammel-Link auf den Ordner

### `audits/raw/` als ZIP

Sistrix-JSONs, Apify-Caches etc. sind oft sehr viele kleine Files. Als ZIP gepackt:

- Komprimiert deutlich (JSON komprimiert oft auf 10-20% der Original-Größe)
- Drive-Upload ist eine einzige Operation (statt 100+)
- Stratege entpackt lokal, falls er an die Roh-Daten will

Wenn ZIP > 2 GB → Auffälligkeit `rohdaten_zu_gross_fuer_drive`, NICHT hochladen, im README.md auf lokalen Pfad verweisen.

### `assets/`

Logos, Screenshots, ggf. abgelegte Hero-Screenshots. Vollständig hochladen, **nicht zippen** — Drive zeigt Bilder direkt im Browser, ZIP würde Preview verhindern.

### Sub-Ordner-Tiefe

Drive unterstützt beliebige Ordnertiefe, aber: **maximal 4 Ebenen** zur Lesbarkeit anstreben. Wenn ein lokaler Ordner > 4 Ebenen tief ist (z. B. `assets/wb/<slug>/screenshots/hero/`), die letzten zwei Ebenen mit Bindestrich kombinieren (`hero-screenshot.png`).

## Reihenfolge des Uploads

Schreibreihenfolge sollte sein:

1. Drive-Root-Ordner anlegen (`<KUNDE> - MTA - <YYYY-MM>/`)
2. **README.md hochladen** (zuerst, damit der Stratege sie sofort sieht, auch bei laufendem Upload)
3. Alle Sub-Ordner (`01-Briefing/` bis `07-Reports-Index/`) anlegen
4. Files pro Sub-Ordner hochladen
5. `07-Reports-Index/index.html` **zuletzt** — damit der Stratege beim Öffnen des Dashboards alle verlinkten Reports schon sieht
6. Permissions setzen (falls Override)
7. Manifest-Files schreiben (lokal)

Die Schreibreihenfolge ist wichtig, weil das Dashboard auf andere Reports verlinkt — wenn diese noch nicht im Drive sind, sind die Drive-Links im Dashboard nicht klickbar.
