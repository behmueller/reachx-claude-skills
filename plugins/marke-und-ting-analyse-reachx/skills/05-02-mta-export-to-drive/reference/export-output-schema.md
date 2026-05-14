# Export-Output-Schema: drive-export.md, drive-export.csv, README.md

Definiert die **exakten Schemata** für die drei generierten Output-Dateien des `05-02-mta-export-to-drive`-Skills.

---

## 1. `synthese/drive-export.md` — Lokales Manifest

### Frontmatter (YAML)

```yaml
---
generiert_am: 2026-05-14T17:00:00Z
skill: 05-02-mta-export-to-drive
schema_version: 1.0

# Drive-Ziel
drive_root: "/MTA-PROJEKTE/Mueller Bauunternehmen - MTA - 2026-05/"
drive_root_link: "https://drive.google.com/drive/folders/XYZ"
drive_root_folder_id: "XYZ123..."
drive_readme_link: "https://drive.google.com/file/d/.../view"

# Modus
modus: mcp                    # mcp | gws | api | reduced
modus_detail: "mcp__googledrive__*"
upload_modus: neu             # neu | ueberschreiben_mit_backup | versions_ordner

# Reduced-Modus-Felder (nur gefüllt wenn modus = reduced)
reduced_zip_pfad: null        # z. B. "mta-export-mueller-bauunternehmen-2026-05.zip"

# Stats
files_total: 47
files_erfolgreich: 45
files_uebersprungen_unchanged: 1
files_fehlgeschlagen: 1
files_mit_backup: 3
files_geskipped_symlink: 0
groesse_total_mb: 23.4

# Pipeline-Coverage
schritte_done:
  - 01-01-mta-projekt-init
  - 01-02-kickoff-transcript-parser
  - 02-01-kunden-marken-profil
  - 02-02-wettbewerber-identifikation
  - 02-03-wettbewerber-marken-profil
  - 03-01-seo-sichtbarkeit-und-rankings
  - 04-02-kanal-chancen-analyse
schritte_offen:
  - 04-04-forecast-modell
  - 04-06-retainer-kalkulator
pipeline_komplett: false

# Auffälligkeiten
auffaelligkeiten:
  - typ: pflicht_outputs_fehlen
    relevanz: hoch
    titel: "Forecast und Retainer fehlen"
    files_betroffen:
      - synthese/forecast.md
      - synthese/forecast.xlsx
      - synthese/retainer.md
      - synthese/retainer.xlsx
  - typ: drive_ordner_bereits_vorhanden
    relevanz: mittel
    titel: "Vorgänger-MTA im Ziel-Ordner"
    detail: "3 Files überschrieben mit Backup unter _versions/2026-05-14/"
---
```

### Markdown-Body

```markdown
# Drive-Export-Manifest: Mueller Bauunternehmen

## Drive-Ordner

[Direkt zum MTA-Ordner](https://drive.google.com/drive/folders/XYZ)

**Drive-Pfad**: `/MTA-PROJEKTE/Mueller Bauunternehmen - MTA - 2026-05/`

## Pflicht-README

[README.md im Drive-Root](https://drive.google.com/file/d/.../view) — Lese-Reihenfolge für den Strategen

## Übersicht hochgeladener Files

### 01-Briefing

| Lokaler Pfad | Drive-Pfad | Status | Größe | Drive-Link |
|---|---|---|---|---|
| `data/briefing.md` | `01-Briefing/briefing.md` | uploaded | 4.5 KB | [öffnen](https://...) |
| `reports/01-briefing.html` | `01-Briefing/01-briefing.html` | uploaded | 12 KB | [öffnen](https://...) |

### 02-Marken-Profile

| Lokaler Pfad | Drive-Pfad | Status | Größe | Drive-Link |
|---|---|---|---|---|
| `data/kunde.md` | `02-Marken-Profile/kunde.md` | uploaded | 8.2 KB | [öffnen](https://...) |
| `data/abweichungen.md` | `02-Marken-Profile/abweichungen.md` | uploaded | 3.1 KB | [öffnen](https://...) |
| `wettbewerber/liste.md` | `02-Marken-Profile/wettbewerber/liste.md` | uploaded | 2.4 KB | [öffnen](https://...) |
| ... (weitere) | ... | ... | ... | ... |

### 03-Audits

(pro Sub-Ordner SEO / Ads / Website / Local / Social eine Tabelle wie oben)

### 04-Synthese

(siehe oben)

### 05-Slide-Bausteine

| Lokaler Pfad | Drive-Pfad | Status | Größe | Drive-Link |
|---|---|---|---|---|
| `synthese/slide-bausteine/` (47 Files) | `05-Slide-Bausteine/` | bulk_uploaded | 1.2 MB | [Ordner öffnen](https://...) |

### 06-Roh-Daten

| Lokaler Pfad | Drive-Pfad | Status | Größe | Drive-Link |
|---|---|---|---|---|
| `audits/raw/` (gezippt) | `06-Roh-Daten/audits-raw.zip` | uploaded | 14.3 MB | [öffnen](https://...) |
| `assets/` (rekursiv) | `06-Roh-Daten/assets/` | bulk_uploaded | 3.8 MB | [Ordner öffnen](https://...) |

### 07-Reports-Index

| Lokaler Pfad | Drive-Pfad | Status | Größe | Drive-Link |
|---|---|---|---|---|
| `reports/index.html` | `07-Reports-Index/index.html` | uploaded | 24 KB | [Dashboard öffnen](https://...) |
| `reports/_shell.html` | `07-Reports-Index/_shell.html` | uploaded | 18 KB | [öffnen](https://...) |

## Backups

Wenn Konflikte vorhanden — Liste der nach `_versions/<ISO-Datum>/` verschobenen Files:

| Original-Drive-Pfad | Backup-Pfad |
|---|---|
| `04-Synthese/forecast.xlsx` | `_versions/2026-05-14/forecast.xlsx` |
| ... | ... |

## Fehlgeschlagene Uploads

Wenn vorhanden — Liste mit Fehlermeldung pro File, manuelles Nachladen empfohlen:

| Lokaler Pfad | Drive-Ziel | Fehlermeldung |
|---|---|---|
| `assets/logo.png` | `06-Roh-Daten/assets/logo.png` | `403 forbidden: Quota exceeded` |
| ... | ... | ... |

## Auffälligkeiten

### `pflicht_outputs_fehlen` (Relevanz: hoch)

Forecast und Retainer-Files fehlen — MTA-Pipeline nicht komplett durchgelaufen.

**Betroffene Files**:
- `synthese/forecast.md`
- `synthese/forecast.xlsx`
- `synthese/retainer.md`
- `synthese/retainer.xlsx`

**Handlungs-Empfehlung**: `04-04-forecast-modell` und `04-06-retainer-kalkulator` nachträglich laufen lassen, dann erneut `05-02-mta-export-to-drive` (Re-Run-Modus erkennt nur die Diffs).

### `drive_ordner_bereits_vorhanden` (Relevanz: mittel)

Drive-Ordner war bereits vorhanden mit 23 Files. Konflikt-Strategie: **überschreiben mit Backup**.

**Backups erstellt**: 3 Files unter `_versions/2026-05-14/`.

**Handlungs-Empfehlung**: Stratege kann _versions-Ordner nach Übergabe löschen, wenn er sicher ist.

---

_Erzeugt von `05-02-mta-export-to-drive` am 2026-05-14T17:00:00Z. Lokales Projekt: `<projekt_pfad>`._
```

---

## 2. `synthese/drive-export.csv` — Flache Tabelle

CSV-Spalten (UTF-8, RFC 4180, Komma-getrennt, Header in Zeile 1):

```csv
lokaler_pfad,drive_pfad,drive_view_link,drive_file_id,sektion,status,groesse_bytes,md5_lokal,upload_datum_iso,fehlermeldung
```

| Spalte | Typ | Beschreibung |
|---|---|---|
| `lokaler_pfad` | string | Relativer Pfad im Projekt, z. B. `data/briefing.md` |
| `drive_pfad` | string | Relativer Pfad im Drive-Root, z. B. `01-Briefing/briefing.md` |
| `drive_view_link` | string (URL) oder leer | `webViewLink` aus Drive-Response |
| `drive_file_id` | string oder leer | Drive-File-ID |
| `sektion` | string | `01-Briefing` \| `02-Marken-Profile` \| `03-Audits` \| `04-Synthese` \| `05-Slide-Bausteine` \| `06-Roh-Daten` \| `07-Reports-Index` \| `Root` |
| `status` | enum | `uploaded` \| `unchanged` \| `skipped_symlink` \| `fehler` \| `bulk_uploaded` |
| `groesse_bytes` | int oder leer | File-Größe in Bytes |
| `md5_lokal` | string oder leer | MD5-Hash des lokalen Files (für Re-Run-Diffing) |
| `upload_datum_iso` | string (ISO-8601) | Zeitstempel des Upload-Versuchs |
| `fehlermeldung` | string oder leer | Bei `status=fehler`: kurze Fehlerbeschreibung |

### Beispiel-Zeilen

```csv
lokaler_pfad,drive_pfad,drive_view_link,drive_file_id,sektion,status,groesse_bytes,md5_lokal,upload_datum_iso,fehlermeldung
,README.md,https://drive.google.com/file/d/abc/view,abc,Root,uploaded,3245,d41d8cd98f00b204e9800998ecf8427e,2026-05-14T17:00:01Z,
data/briefing.md,01-Briefing/briefing.md,https://drive.google.com/file/d/def/view,def,01-Briefing,uploaded,4523,5d41402abc4b2a76b9719d911017c592,2026-05-14T17:00:02Z,
reports/01-briefing.html,01-Briefing/01-briefing.html,https://drive.google.com/file/d/ghi/view,ghi,01-Briefing,uploaded,12834,098f6bcd4621d373cade4e832627b4f6,2026-05-14T17:00:03Z,
synthese/forecast.xlsx,04-Synthese/forecast.xlsx,,jkl,04-Synthese,unchanged,28456,e10adc3949ba59abbe56e057f20f883e,2026-05-14T17:00:42Z,
assets/logo.png,06-Roh-Daten/assets/logo.png,,,06-Roh-Daten,fehler,15234,,2026-05-14T17:01:15Z,403 forbidden: Quota exceeded
```

### CSV-Konventionen

- Encoding: **UTF-8 mit BOM** (Excel-kompatibel)
- Felder mit `,` oder `"` oder Newline: in `"..."` quoten, interne `"` als `""` doppeln
- Empty values: leer (nicht `null` oder `NaN`)
- Datumsformat: **ISO-8601 mit `Z`** (`2026-05-14T17:00:01Z`)

---

## 3. README.md im Drive-Root — Template

Vom Skill generiert. Inhalt (Markdown):

```markdown
# MTA-Übergabe: <KUNDE>

**Datum**: <YYYY-MM-DD>
**Stratege**: <stratege_name oder "—" wenn nicht in meta.json>
**Pipeline-Lauf**: Stufe 1-4 (Briefing, Marken-Profile, Audits, Synthese)

---

## MTA-Stammdaten

| Feld | Wert |
|---|---|
| Kunde | <kunde> |
| Branche | <branche> |
| Region | <region> |
| Website | <website> |
| Kickoff-Datum | <kickoff_datum oder "—"> |
| MTA-Deadline | <mta_deadline oder "—"> |
| Projekt-Slug | <projekt_slug> |

---

## Empfohlene Lese-Reihenfolge für den Strategen

1. **Start hier**: `04-Synthese/kanal-chancen.md` — Top-3-Kanal-Empfehlungen mit `chancen_score` und Begründung. Strategisches Herz der MTA.
2. **Differenzierung**: `04-Synthese/positionierung.md` — Wo steht der Kunde im Wettbewerbsumfeld, welche White-Spaces sind offen.
3. **Quantitative Ableitung**: `04-Synthese/forecast.md` + `forecast.xlsx` — 12-Monats-Modell, Best/Real/Worst-Szenarien pro Kanal.
4. **Roadmap**: `04-Synthese/90-tage-plan.md` und `retainer.md` + `retainer.xlsx` — konkrete Maßnahmen und Retainer-Empfehlung.
5. **Kontext**: `01-Briefing/` (was der Kunde gesagt hat) und `02-Marken-Profile/` (Kunde + Wettbewerber-Profile).
6. **Tiefe**: `03-Audits/` (Daten-Belege pro Kanal: SEO, Ads, Website, Local, Social) — bei Detail-Fragen.
7. **Präsentation**: `05-Slide-Bausteine/` — fertige HTML-Bausteine, Copy-Paste in Google Slides (Slide-Layouts via `05-01-mta-slide-bausteine`).
8. **Reproduzierbarkeit**: `06-Roh-Daten/audits-raw.zip` — Sistrix-/Apify-Caches für Re-Runs (nur bei Bedarf).

**Dashboard**: `07-Reports-Index/index.html` — Vollständige interaktive Übersicht aller Skill-Reports im Browser.

---

## Was wurde geliefert (Skill-Übersicht)

| Skill | Stufe | Output | Drive-Pfad |
|---|---|---|---|
| `01-01-mta-projekt-init` | 0 | meta.json, status.md | `06-Roh-Daten/` (in audits-raw.zip enthalten) |
| `01-02-kickoff-transcript-parser` | 1 | briefing.md | `01-Briefing/briefing.md` |
| `02-01-kunden-marken-profil` | 1 | kunde.md, abweichungen.md | `02-Marken-Profile/` |
| `02-02-wettbewerber-identifikation` | 2 | liste.md | `02-Marken-Profile/wettbewerber/liste.md` |
| `02-03-wettbewerber-marken-profil` | 2 | pro WB ein Profil | `02-Marken-Profile/wettbewerber/` |
| `03-04-seo-first-party-gsc` | 3 | gsc-first-party.md + CSVs | `03-Audits/SEO/` |
| `03-01-seo-sichtbarkeit-und-rankings` | 3 | seo-sichtbarkeit.md + CSVs (inkl. seo-rankings-ahrefs.csv im Hybrid) | `03-Audits/SEO/` |
| `04-02-kanal-chancen-analyse` | 4 | kanal-chancen.md | `04-Synthese/kanal-chancen.md` |
| ... (alle erledigten Skills aus status.md) | ... | ... | ... |

---

## Offene Punkte aus status.md

<aus status.md "Offene Punkte" und "Blockiert" extrahieren — wenn leer, ganzen Block weglassen>

---

## Pipeline-Lücken

<wenn pflicht_outputs_fehlen-Auffälligkeit vorliegt:>

⚠ **Diese MTA ist inhaltlich nicht vollständig.** Folgende Outputs fehlen:

- `<liste fehlender Files>`

Empfehlung: Fehlende Skills nachlaufen lassen und `05-02-mta-export-to-drive` erneut ausführen (Re-Run lädt nur Diffs hoch).

<sonst:>

✓ **Pipeline vollständig** — alle Skills von Stufe 1 bis 4 sind durchgelaufen.

---

## Technische Hinweise

- **HTML-Reports**: Direkt im Drive-Browser ansehen (Drive-HTML-Viewer)
- **XLSX-Files** (Forecast, Retainer): Native-XLSX, NICHT zu Google Sheets konvertieren — Formeln gehen sonst verloren. Lokal in Excel/Numbers öffnen oder in Drive als Native-Vorschau ansehen.
- **CSV-Files**: Direkt in Drive ansehen oder zu Google Sheets konvertieren (Encoding ist UTF-8 mit BOM, sollte sauber funktionieren).
- **Roh-Daten (`06-Roh-Daten/audits-raw.zip`)**: Lokal entpacken bei Bedarf an Re-Analyse.

---

## Bei Fragen

- **Original-Projekt liegt lokal unter**: `<projekt_pfad>` (auf der Maschine des MTA-Erstellers)
- **Skill-Manifest** (lokal): `synthese/drive-export.md` und `synthese/drive-export.csv`
- **MTA-Pipeline-Doku**: `MTA-SKILLS-PLAN.md` im REACHX-Skill-Repository

---

_Diese README wurde automatisch erzeugt von `05-02-mta-export-to-drive` am <ISO-Datum>. Bei inhaltlichen Fragen zur MTA-Auswertung: <stratege_kontakt oder "Rückfrage an MTA-Ersteller">._
```

---

## Versionierung dieses Schemas

Bei Schema-Änderung (z. B. neue Spalten in CSV, neue Frontmatter-Felder):

- `schema_version` in `drive-export.md`-Frontmatter hochzählen
- Alte Manifest-Files bleiben auf ihrer Version — Re-Run-Modus muss Version-Check machen, bevor er Diffs vergleicht

Aktuelle Version: **1.0**
