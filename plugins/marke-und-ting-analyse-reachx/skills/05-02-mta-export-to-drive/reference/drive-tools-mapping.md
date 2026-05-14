# Drive-Tools-Mapping: MCP, gws-CLI, Drive-API, Reduced-ZIP

Definiert die **konkreten Befehle und Code-Snippets** für die vier Upload-Modi. Skill prüft in dieser Reihenfolge und nutzt den ersten verfügbaren Pfad.

## Modus-Erkennung (Routing)

### Modus 1: MCP-Google-Drive (primär, falls vorhanden)

Wenn die Session über einen Google-Drive-MCP-Server verfügt — typische Tool-Namen:

- `mcp__googledrive__*`
- `mcp__drive__*`
- `mcp__google_drive__*`
- Server-Name kann auch eine UUID sein (`mcp__<uuid>__create_file` etc.)

Erkennung im Skill:

```python
# Check available tools for drive-related MCP servers
import re
drive_mcp_pattern = re.compile(r"^mcp__.*(drive|googledrive|google_drive).*__", re.IGNORECASE)
mcp_tools = [t for t in available_tools if drive_mcp_pattern.match(t)]
mcp_available = len(mcp_tools) > 0
```

Wenn verfügbar: bevorzugte Tools (typische MCP-Naming-Konventionen):

- `mcp__<server>__create_file` (Upload)
- `mcp__<server>__copy_file` (oder upload)
- `mcp__<server>__search_files` (Existenz-Check)
- `mcp__<server>__get_file_metadata` (md5/Hash-Vergleich)
- `mcp__<server>__list_recent_files` (Ordner-Inhalt)

Falls MCP keine Folder-Create-Funktion hat (manche tun das nicht): Fallback auf gws-CLI für Folder-Anlage, MCP nur für File-Upload.

### Modus 2: gws-CLI (REACHX-Standard)

```bash
# Verfügbarkeit
command -v gws >/dev/null 2>&1 && gws auth status >/dev/null 2>&1
# Exit-Code 0 → Modus gws verwendbar
```

Falls verfügbar: aktives Konto prüfen:

```bash
gws drive about --fields="user(emailAddress,displayName),storageQuota(usage,limit)"
```

Output dient zur Anzeige im Chat: "Drive-Konto: stratege@reachx.de, Quota frei: 234 GB von 2 TB". Domain-Check: wenn die Domain im `emailAddress` ungleich `reachx.de` ist → Auffälligkeit `falscher_drive_account`.

### Modus 3: Drive-API (Python, Fallback)

```python
# Verfügbarkeit
try:
    from googleapiclient.discovery import build
    from google.auth import default
    creds, _ = default(scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds)
    about = service.about().get(fields="user,storageQuota").execute()
    # Erfolg → Modus api
except Exception:
    # Modus api nicht verwendbar
    pass
```

**OAuth-Setup-Hinweise** (in dieser Reihenfolge prüfen):

1. **Service-Account-JSON**: `GOOGLE_APPLICATION_CREDENTIALS` zeigt auf ein gültiges Service-Account-JSON
2. **Application Default Credentials**: `gcloud auth application-default login` ist gelaufen → `~/.config/gcloud/application_default_credentials.json` existiert
3. **OAuth-Token-Env**: `GOOGLE_DRIVE_OAUTH_TOKEN` ist gesetzt (für CI-Szenarien oder kurzlebige Tokens) — Skill nutzt es für eine `Credentials`-Instanz direkt
4. **API-Key**: `GOOGLE_DRIVE_API_KEY` (selten, nur für public files) — meistens nicht ausreichend für Upload

### Modus 4: Reduced / ZIP-Manifest (Last-Resort)

Immer verwendbar — keine externe Dependency. Falls die ersten drei Modi scheitern, fallback hierauf.

## MCP-Google-Drive (Beispiel-Aufrufe)

Da MCP-Server-Namen variieren, hier exemplarisch für einen `mcp__googledrive__*`-Server:

```python
# Ordner finden oder anlegen
result = call_tool("mcp__googledrive__create_folder", {
    "name": "Mueller Bauunternehmen - MTA - 2026-05",
    "parent_id": "<MTA-PROJEKTE-Folder-ID>"
})

# File hochladen
result = call_tool("mcp__googledrive__create_file", {
    "name": "briefing.md",
    "parent_id": "<01-Briefing-Folder-ID>",
    "content": file_bytes_or_base64,
    "mime_type": "text/markdown"
})
# Response enthält file_id und web_view_link
```

Wenn der konkrete MCP-Server andere Parameter-Namen verwendet, in der MCP-Tool-Schema-Beschreibung nachsehen (ToolSearch query: `select:mcp__<server>__create_file`).

## gws-CLI-Befehle

### Ordner anlegen

```bash
# Parent-Ordner-ID auflösen
gws drive files list --params '{
  "q": "name = '"'"'MTA-PROJEKTE'"'"' and mimeType = '"'"'application/vnd.google-apps.folder'"'"' and trashed = false",
  "fields": "files(id,name)"
}'

# Neuen Ordner anlegen (parent_id von oben)
gws drive files create --params '{
  "name": "Mueller Bauunternehmen - MTA - 2026-05",
  "mimeType": "application/vnd.google-apps.folder",
  "parents": ["PARENT_ID"]
}'
# Response enthält "id" — die ist die neue Folder-ID
```

**Wichtig**: Die `gws`-CLI druckt vor der JSON-Antwort die Zeile `Using keyring backend: keyring` auf stdout. Bevor du parsst, erste Zeile entfernen, falls sie nicht mit `{` beginnt.

### File-Upload (einfach, < 5 MB)

```bash
gws drive files create \
  --upload-file "/lokaler/pfad/briefing.md" \
  --params '{
    "name": "briefing.md",
    "parents": ["FOLDER_ID"],
    "mimeType": "text/markdown"
  }' \
  --fields "id,name,webViewLink,size,md5Checksum"
```

Response:

```json
{
  "id": "1AbC...",
  "name": "briefing.md",
  "webViewLink": "https://drive.google.com/file/d/1AbC.../view",
  "size": "4523",
  "md5Checksum": "d41d8cd..."
}
```

`webViewLink` ist der Link, den der Stratege im Browser klicken kann — sammle ihn ins Manifest.

### File-Upload (Resumable, > 5 MB)

Für Forecast/Retainer-XLSX und große raw-JSONs:

```bash
gws drive files create \
  --upload-file "/lokaler/pfad/forecast.xlsx" \
  --resumable \
  --params '{
    "name": "forecast.xlsx",
    "parents": ["FOLDER_ID"],
    "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }' \
  --fields "id,name,webViewLink,size"
```

Resumable-Upload macht automatisch Chunks von 5 MB. Bei Abbruch retry-fähig.

### File-Existenz prüfen (für Konflikt-Strategie)

```bash
gws drive files list --params '{
  "q": "name = '"'"'briefing.md'"'"' and '"'"'FOLDER_ID'"'"' in parents and trashed = false",
  "fields": "files(id,name,md5Checksum,size,modifiedTime)"
}'
```

Wenn `files[]` leer → File existiert nicht, normaler Upload.
Wenn `files[0].md5Checksum` identisch zum lokalen `md5sum` → File ist unverändert, Skip.
Sonst → Backup nach `_versions/<ISO-Datum>/<original-name>` und neuer Upload.

### File nach `_versions/` verschieben (Backup)

```bash
# _versions/-Ordner anlegen, falls nicht da
gws drive files create --params '{
  "name": "_versions",
  "mimeType": "application/vnd.google-apps.folder",
  "parents": ["FOLDER_ID"]
}'
# Datums-Sub-Ordner: "2026-05-14"
gws drive files create --params '{
  "name": "2026-05-14",
  "mimeType": "application/vnd.google-apps.folder",
  "parents": ["VERSIONS_FOLDER_ID"]
}'
# Altes File reinmoven (parent ändern)
gws drive files update --params '{
  "fileId": "OLD_FILE_ID",
  "addParents": "DATE_FOLDER_ID",
  "removeParents": "FOLDER_ID"
}'
```

### Permissions setzen (optional, nur via Override)

```bash
# Lesbar für gesamte REACHX-Domain
gws drive permissions create --params '{
  "fileId": "FOLDER_ID",
  "type": "domain",
  "role": "reader",
  "domain": "reachx.de"
}'
```

Default: **nicht** ausführen. Nur wenn Override `sharing: intern_lesbar`.

## Drive-API-Snippets (Python)

### Setup

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth import default
import hashlib, os

creds, _ = default(scopes=["https://www.googleapis.com/auth/drive"])
service = build("drive", "v3", credentials=creds)
```

Alternativ mit `GOOGLE_DRIVE_OAUTH_TOKEN`:

```python
from google.oauth2.credentials import Credentials
import os

token = os.environ["GOOGLE_DRIVE_OAUTH_TOKEN"]
creds = Credentials(token=token, scopes=["https://www.googleapis.com/auth/drive"])
service = build("drive", "v3", credentials=creds)
```

### Ordner anlegen oder finden

```python
def find_or_create_folder(name: str, parent_id: str) -> str:
    # Drive-Filename-escaping: Apostrophes in q-string escapen
    safe_name = name.replace("'", "\\'")
    q = (
        f"name = '{safe_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed = false"
    )
    res = service.files().list(q=q, fields="files(id,name)").execute()
    if res.get("files"):
        return res["files"][0]["id"]
    folder = service.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        },
        fields="id",
    ).execute()
    return folder["id"]
```

### File-Upload mit Konflikt-Check

```python
def upload_with_backup(local_path: str, drive_name: str, parent_id: str,
                       mime: str, versions_folder_id: str | None = None) -> dict:
    safe_name = drive_name.replace("'", "\\'")
    q = f"name = '{safe_name}' and '{parent_id}' in parents and trashed = false"
    existing = service.files().list(q=q, fields="files(id,md5Checksum)").execute()
    local_md5 = hashlib.md5(open(local_path, "rb").read()).hexdigest()
    if existing.get("files"):
        old = existing["files"][0]
        if old.get("md5Checksum") == local_md5:
            return {"status": "unchanged", "id": old["id"]}
        # Backup: altes File nach versions_folder verschieben
        if versions_folder_id:
            service.files().update(
                fileId=old["id"],
                addParents=versions_folder_id,
                removeParents=parent_id,
            ).execute()
    # Upload (resumable bei > 5 MB)
    size = os.path.getsize(local_path)
    media = MediaFileUpload(local_path, mimetype=mime, resumable=(size > 5 * 1024 * 1024))
    new = service.files().create(
        body={"name": drive_name, "parents": [parent_id]},
        media_body=media,
        fields="id,webViewLink,size",
    ).execute()
    return {"status": "uploaded", **new}
```

### Retry-Logik

```python
import time
from googleapiclient.errors import HttpError

def upload_with_retry(fn, *args, max_retries=2, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except HttpError as e:
            if attempt == max_retries or e.resp.status not in (429, 500, 502, 503, 504):
                raise
            time.sleep(3 * (attempt + 1))
```

## Reduced-Modus: ZIP-Manifest

Wenn weder MCP, gws-CLI noch Drive-API verfügbar:

```python
import zipfile, os
from pathlib import Path

def build_reduced_zip(project_root: Path, kunden_slug: str, yyyy_mm: str,
                      kunde_display: str, mapping: list[tuple[Path, str]]) -> Path:
    """
    mapping: Liste von (lokaler-pfad, drive-pfad-relativ) Tupeln
    Beispiel: [
      (project_root / "README-generated.md", "README.md"),
      (project_root / "data/briefing.md", "01-Briefing/briefing.md"),
      ...
    ]
    """
    zip_path = project_root / f"mta-export-{kunden_slug}-{yyyy_mm}.zip"
    root_dir = f"{kunde_display} - MTA - {yyyy_mm}"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for local, drive_rel in mapping:
            if not local.exists():
                continue
            arcname = f"{root_dir}/{drive_rel}"
            zf.write(local, arcname=arcname)
    return zip_path
```

Manifest schreibt dann `drive_root_link: null`, dafür `reduced_zip_pfad: mta-export-...zip`.

Im HTML-Report wird ein großer `.suggestion`-Block statt der Drive-Buttons gerendert:

```html
<section class="suggestion">
  <p><strong>Reduced-Modus aktiv</strong> — ZIP-Manifest wurde lokal erstellt.</p>
  <p>Bitte manuell hochladen unter <code>/MTA-PROJEKTE/KUNDE - MTA - YYYY-MM/</code></p>
  <p>ZIP-Pfad: <code>mta-export-KUNDEN_SLUG-YYYY-MM.zip</code></p>
</section>
```

## Pfad-Auflösung im Drive

Drive-API arbeitet mit Folder-IDs, nicht Pfaden. Die Funktion `resolve_drive_path` durchläuft den Pfad-String Ebene für Ebene und findet die jeweilige Folder-ID:

```python
def resolve_drive_path(path: str) -> str:
    """
    path: '/MTA-PROJEKTE/Mueller Bauunternehmen - MTA - 2026-05/'
    Returns: Drive Folder-ID des letzten Pfad-Segments
    """
    parts = [p for p in path.strip("/").split("/") if p]
    current = "root"  # Drive-Root-ID
    for part in parts:
        current = find_or_create_folder(part, current)
    return current
```

## Fehlerquellen und Recovery

| Fehler | Ursache | Recovery |
|---|---|---|
| `403 storageQuotaExceeded` | Drive voll | Abbruch, Auffälligkeit `drive_quota_kritisch` |
| `403 forbidden` | Account hat keine Schreibrechte | Abbruch, Stratege bitten Account-Berechtigung zu prüfen |
| `404` bei Folder-ID | Folder gelöscht zwischen Resolve und Upload | Re-Resolve, einmal retry |
| `429 rateLimitExceeded` | Zu viele Requests pro Sekunde | 3-Sekunden-Pause, retry |
| `500/502/503` | Drive-Server-Hiccup | Retry mit Exponential-Backoff |
| `401 unauthorized` | Token abgelaufen | gws-CLI: Nutzer auf `gws auth login` hinweisen; API: ADC neu setzen oder `GOOGLE_DRIVE_OAUTH_TOKEN` refreshen |

## Beispiel-Skelett (Pseudocode)

```python
# Schritt 4: Drive-Root-Folder auflösen oder anlegen
root_name = f"{kunde_display} - MTA - {yyyy_mm}"
projekte_id = find_or_create_folder("MTA-PROJEKTE", "root")
root_id = find_or_create_folder(root_name, projekte_id)

# Schritt 5: Sub-Ordner anlegen
sections = ["01-Briefing", "02-Marken-Profile", "03-Audits", "04-Synthese",
            "05-Slide-Bausteine", "06-Roh-Daten", "07-Reports-Index"]
section_ids = {s: find_or_create_folder(s, root_id) for s in sections}

# 03-Audits weiter unterteilen
audit_subs = ["SEO", "Ads", "Website", "Local", "Social"]
audit_sub_ids = {s: find_or_create_folder(s, section_ids["03-Audits"]) for s in audit_subs}

# 02-Marken-Profile/wettbewerber/ anlegen
wb_id = find_or_create_folder("wettbewerber", section_ids["02-Marken-Profile"])

# README.md zuerst hochladen
readme_result = upload_with_retry(upload_with_backup,
    readme_local_path, "README.md", root_id, "text/markdown")

# Schritt 7: Upload mit Plan
manifest_entries = [readme_entry]
for local, drive_rel, mime in upload_plan:
    target_folder_id = resolve_target_folder(drive_rel, section_ids, audit_sub_ids, wb_id)
    drive_name = Path(drive_rel).name
    try:
        result = upload_with_retry(upload_with_backup, local, drive_name,
                                   target_folder_id, mime, versions_folder_id)
        manifest_entries.append({
            "lokaler_pfad": str(local),
            "drive_pfad": drive_rel,
            "drive_view_link": result.get("webViewLink"),
            "status": result["status"],
            "groesse_bytes": result.get("size"),
            "upload_datum_iso": now_iso(),
        })
    except Exception as e:
        manifest_entries.append({
            "lokaler_pfad": str(local),
            "drive_pfad": drive_rel,
            "status": f"fehler: {e}",
        })
```

## Modus-Auswahl: Wann was

- **MCP-Google-Drive bevorzugt**, wenn vorhanden — modernste Integration, oft mit besseren Defaults und integrierter Auth
- **gws-CLI als Fallback**, wenn MCP nicht verbunden — REACHX-Standard, einheitliche Auth, identisch zu anderen Skills (`06-01-action-titles-check` etc.)
- **Drive-API als zweiter Fallback**, wenn weder MCP noch gws-CLI auf der Maschine ist
- **Reduced-ZIP als Last-Resort**, damit der Skill auf jeder Maschine läuft, auch ohne Drive-Zugang

## Modus-Anzeige im Chat

Vor dem Upload-Start einmalig melden, welcher Modus aktiv ist:

```
Drive-Modus erkannt: MCP-Google-Drive (mcp__googledrive__*)
Drive-Konto: stratege@reachx.de
Drive-Quota: 234 GB frei von 2 TB
Drive-Pfad-Ziel: /MTA-PROJEKTE/Mueller Bauunternehmen - MTA - 2026-05/

Upload startet ...
```

Oder bei Reduced:

```
Drive-Modus erkannt: REDUCED (kein MCP, kein gws-CLI, keine Drive-API)
Fallback: ZIP-Manifest wird lokal erstellt unter mta-export-mueller-2026-05.zip
Stratege muss ZIP manuell in Drive hochladen.
```
