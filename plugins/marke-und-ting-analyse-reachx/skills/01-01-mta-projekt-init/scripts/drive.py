#!/usr/bin/env python3
"""
REACHX MTA-Skills — Google-Drive-Helper

Wrappt die `gws` CLI (Google Workspace CLI) in eine pythonische Schnittstelle, die
alle anderen MTA-Skills nutzen, um Outputs auf Drive zu schreiben statt lokal.

Designprinzipien:
  - Alle Drive-Operationen laufen über `gws drive files <verb>` als Subprocess-Call.
    Das hält die MCP-Token-Kosten bei null und nutzt die volle Drive-API
    (inklusive update_file und delete_file, die der MCP nicht bietet).
  - `gws --upload` verlangt einen cwd-relativen Pfad. Wir lösen das über
    `subprocess.run(..., cwd=<tmpdir>)`.
  - Aktive MTAs werden lokal pro Kollege in `~/.cache/reachx-mta/active-mtas.json`
    gecached, damit Folge-Skills den Drive-Folder schnell wiederfinden.

Kann als Modul importiert oder als CLI aufgerufen werden:

    python3 drive.py extract-folder-id <url-or-id>
    python3 drive.py validate-folder <folder-id>
    python3 drive.py find-or-create-folder <parent-id> <name>
    python3 drive.py upsert-text <parent-id> <name> <content-file> [mime]
    python3 drive.py read <file-id>
    python3 drive.py register-mta <slug> <folder-id> <kunde>
    python3 drive.py get-mta <slug>
    python3 drive.py list-mtas
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# ---------- Konfiguration ----------

CACHE_DIR = Path.home() / ".cache" / "reachx-mta"
ACTIVE_MTAS_FILE = CACHE_DIR / "active-mtas.json"
GWS_BIN = os.environ.get("REACHX_GWS_BIN", "gws")
FOLDER_MIME = "application/vnd.google-apps.folder"
DEFAULT_TEXT_MIME = "text/markdown"


class DriveError(RuntimeError):
    """Wird bei jedem gws-API-Fehler geworfen."""


# ---------- Low-Level gws Wrapper ----------

def _run_gws(args: list[str], *, cwd: Optional[Path] = None, expect_json: bool = True) -> dict | str:
    """
    Führt `gws <args>` aus. Gibt geparstes JSON zurück oder rohen stdout-Text.

    `gws` schreibt vor jeder JSON-Antwort eine Zeile "Using keyring backend: keyring".
    Wir filtern die raus, bevor wir parsen.
    """
    cmd = [GWS_BIN] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=60
        )
    except subprocess.TimeoutExpired:
        raise DriveError(f"gws-Aufruf hat Timeout (60s) überschritten: {' '.join(cmd[:3])}...")

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    # Keyring-Logzeile aus stdout filtern
    cleaned = "\n".join(
        line for line in stdout.splitlines()
        if not line.startswith("Using keyring backend")
    ).strip()

    if result.returncode != 0:
        # gws schreibt JSON-Fehler oft auf stdout, manchmal auf stderr
        error_text = cleaned or stderr
        raise DriveError(f"gws-Aufruf fehlgeschlagen (rc={result.returncode}): {error_text[:500]}")

    if not expect_json:
        return cleaned

    if not cleaned:
        return {}

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise DriveError(f"Konnte gws-Output nicht als JSON parsen: {e}\nOutput: {cleaned[:500]}")


# ---------- URL-Parsing ----------

_FOLDER_URL_RES = [
    re.compile(r"/folders/([a-zA-Z0-9_-]+)"),
    re.compile(r"[?&]id=([a-zA-Z0-9_-]+)"),
    re.compile(r"^([a-zA-Z0-9_-]{20,})$"),  # nackte File/Folder-ID
]


def extract_folder_id(url_or_id: str) -> str:
    """
    Extrahiert eine Drive-Folder-ID aus einer Drive-URL oder einer rohen ID.

    Akzeptiert:
      - https://drive.google.com/drive/folders/<ID>
      - https://drive.google.com/drive/u/0/folders/<ID>?usp=sharing
      - https://drive.google.com/open?id=<ID>
      - <ID> (nackt, 20+ Zeichen)
    """
    if not url_or_id:
        raise DriveError("Leere Drive-URL/ID übergeben")
    url_or_id = url_or_id.strip()
    for regex in _FOLDER_URL_RES:
        m = regex.search(url_or_id)
        if m:
            return m.group(1)
    raise DriveError(
        f"Konnte keine Drive-Folder-ID aus '{url_or_id[:80]}...' extrahieren. "
        "Erwartet: Drive-URL mit /folders/<ID> oder direkt die ID."
    )


# ---------- Drive-Operationen ----------

def validate_folder(folder_id: str) -> dict:
    """
    Prüft, dass die ID einen erreichbaren Drive-Folder bezeichnet. Gibt Metadaten zurück.
    """
    params = json.dumps({
        "fileId": folder_id,
        "fields": "id,name,mimeType,driveId,parents,capabilities/canAddChildren",
        "supportsAllDrives": True,
    })
    data = _run_gws(["drive", "files", "get", "--params", params])
    if data.get("mimeType") != FOLDER_MIME:
        raise DriveError(
            f"Drive-Objekt {folder_id} ist kein Folder, sondern '{data.get('mimeType')}'"
        )
    can_write = (data.get("capabilities") or {}).get("canAddChildren", False)
    if not can_write:
        raise DriveError(
            f"Kein Schreibrecht auf Folder '{data.get('name')}' ({folder_id}). "
            "Bitte vom Drive-Admin Schreibrechte anfordern."
        )
    return data


def find_by_name(parent_id: str, name: str, mime_type: Optional[str] = None) -> Optional[dict]:
    """
    Sucht eine Datei oder einen Folder mit exaktem Namen unter `parent_id`.
    Gibt None zurück, wenn nicht gefunden. Bei Duplikaten: gibt das jüngste zurück.
    """
    q_parts = [f"'{parent_id}' in parents", "trashed = false", f"name = '{_escape(name)}'"]
    if mime_type:
        q_parts.append(f"mimeType = '{mime_type}'")
    params = json.dumps({
        "q": " and ".join(q_parts),
        "fields": "files(id,name,mimeType,modifiedTime)",
        "orderBy": "modifiedTime desc",
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
        "pageSize": 5,
    })
    data = _run_gws(["drive", "files", "list", "--params", params])
    files = data.get("files") or []
    return files[0] if files else None


def list_children(parent_id: str) -> list[dict]:
    """Listet alle nicht-getrashten Kinder eines Folders."""
    params = json.dumps({
        "q": f"'{parent_id}' in parents and trashed = false",
        "fields": "files(id,name,mimeType,modifiedTime,size)",
        "orderBy": "name",
        "supportsAllDrives": True,
        "includeItemsFromAllDrives": True,
        "pageSize": 200,
    })
    data = _run_gws(["drive", "files", "list", "--params", params])
    return data.get("files") or []


def create_subfolder(parent_id: str, name: str) -> str:
    """Erstellt einen neuen Subfolder unter parent_id. Gibt die neue Folder-ID zurück."""
    existing = find_by_name(parent_id, name, mime_type=FOLDER_MIME)
    if existing:
        return existing["id"]
    body = json.dumps({
        "name": name,
        "parents": [parent_id],
        "mimeType": FOLDER_MIME,
    })
    params = json.dumps({"supportsAllDrives": True, "fields": "id,name"})
    data = _run_gws(["drive", "files", "create", "--json", body, "--params", params])
    return data["id"]


def upload_text(parent_id: str, name: str, content: str, mime_type: str = DEFAULT_TEXT_MIME) -> str:
    """
    Lädt eine neue Text-Datei in den Folder hoch. Returns File-ID.

    WICHTIG: Erstellt immer eine NEUE Datei, auch wenn der Name schon existiert
    (Drive lässt Duplikate zu). Für Update-Semantik siehe `upsert_text`.
    """
    with tempfile.TemporaryDirectory(prefix="reachx-mta-") as tmp:
        tmp_path = Path(tmp)
        local_file = tmp_path / name
        local_file.write_text(content, encoding="utf-8")
        body = json.dumps({"name": name, "parents": [parent_id]})
        params = json.dumps({"supportsAllDrives": True, "fields": "id,name"})
        data = _run_gws(
            [
                "drive", "files", "create",
                "--json", body,
                "--params", params,
                "--upload", name,
                "--upload-content-type", mime_type,
            ],
            cwd=tmp_path,
        )
        return data["id"]


def update_text(file_id: str, content: str, mime_type: str = DEFAULT_TEXT_MIME) -> None:
    """Überschreibt den Inhalt einer existierenden Datei."""
    # Wir brauchen den ursprünglichen Dateinamen für den temporären Upload
    meta = _run_gws([
        "drive", "files", "get",
        "--params", json.dumps({"fileId": file_id, "fields": "name", "supportsAllDrives": True}),
    ])
    name = meta.get("name") or "content"
    with tempfile.TemporaryDirectory(prefix="reachx-mta-") as tmp:
        tmp_path = Path(tmp)
        local_file = tmp_path / name
        local_file.write_text(content, encoding="utf-8")
        params = json.dumps({"fileId": file_id, "supportsAllDrives": True})
        _run_gws(
            [
                "drive", "files", "update",
                "--params", params,
                "--upload", name,
                "--upload-content-type", mime_type,
            ],
            cwd=tmp_path,
        )


def upsert_text(
    parent_id: str, name: str, content: str, mime_type: str = DEFAULT_TEXT_MIME
) -> str:
    """
    Idempotent: Wenn eine Datei mit diesem Namen im Folder existiert, update; sonst create.

    Gibt die Drive-File-ID zurück. Der häufigste Schreib-Pfad für MTA-Skills.
    """
    existing = find_by_name(parent_id, name)
    if existing:
        update_text(existing["id"], content, mime_type=mime_type)
        return existing["id"]
    return upload_text(parent_id, name, content, mime_type=mime_type)


def read_text(file_id: str) -> str:
    """Liest den Text-Inhalt einer Drive-Datei via files.get?alt=media."""
    with tempfile.TemporaryDirectory(prefix="reachx-mta-") as tmp:
        tmp_path = Path(tmp)
        out_file = tmp_path / "content"
        params = json.dumps({"fileId": file_id, "alt": "media", "supportsAllDrives": True})
        _run_gws(
            ["drive", "files", "get", "--params", params, "-o", "content"],
            cwd=tmp_path,
            expect_json=False,
        )
        return out_file.read_text(encoding="utf-8")


def delete(file_id: str) -> None:
    """Löscht eine Drive-Datei oder einen leeren Folder (permanent, nicht Trash)."""
    params = json.dumps({"fileId": file_id, "supportsAllDrives": True})
    _run_gws(
        ["drive", "files", "delete", "--params", params],
        expect_json=False,
    )


# ---------- Active-MTA-Cache ----------

def _load_active_mtas() -> dict:
    if not ACTIVE_MTAS_FILE.exists():
        return {}
    try:
        return json.loads(ACTIVE_MTAS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_active_mtas(data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_MTAS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def register_active_mta(slug: str, folder_id: str, kunde: str, working_dir: Optional[str] = None) -> None:
    """Registriert eine aktive MTA im lokalen Cache (pro Kollege).

    `working_dir` ist optional, aber für robustes Token-Tracking empfohlen: damit
    kann der Token-Tracker das passende `~/.claude/projects/`-Verzeichnis eindeutig
    auflösen, ohne auf Heuristik zurückzufallen. Wenn nicht gesetzt, nimmt der
    Skill den aktuellen `os.getcwd()`.
    """
    import os as _os
    from datetime import datetime, timezone
    data = _load_active_mtas()
    if working_dir is None:
        working_dir = _os.getcwd()
    data[slug] = {
        "folder_id": folder_id,
        "kunde": kunde,
        "working_dir": working_dir,
        "zuletzt_aktiv": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _save_active_mtas(data)


def get_active_mta(slug: str) -> Optional[dict]:
    """Holt die aktive MTA aus dem Cache. None wenn nicht registriert."""
    return _load_active_mtas().get(slug)


def list_active_mtas() -> dict:
    """Gibt alle gecachten aktiven MTAs zurück."""
    return _load_active_mtas()


# ---------- Hilfsfunktionen ----------

def _escape(s: str) -> str:
    """Escaped einfache Anführungszeichen für Drive-Query-Syntax."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


# ---------- CLI ----------

def _cli() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]

    try:
        if cmd == "extract-folder-id":
            print(extract_folder_id(args[0]))
        elif cmd == "validate-folder":
            print(json.dumps(validate_folder(args[0]), indent=2, ensure_ascii=False))
        elif cmd == "find-or-create-folder":
            print(create_subfolder(args[0], args[1]))
        elif cmd == "upsert-text":
            parent_id, name, content_file = args[0], args[1], args[2]
            mime = args[3] if len(args) > 3 else DEFAULT_TEXT_MIME
            content = Path(content_file).read_text(encoding="utf-8")
            print(upsert_text(parent_id, name, content, mime_type=mime))
        elif cmd == "read":
            print(read_text(args[0]))
        elif cmd == "delete":
            delete(args[0])
            print("deleted")
        elif cmd == "register-mta":
            # CLI: register-mta <slug> <folder_id> [--working-dir <pfad>] <kunde-name...>
            slug, folder_id = args[0], args[1]
            rest = args[2:]
            working_dir = None
            if "--working-dir" in rest:
                i = rest.index("--working-dir")
                working_dir = rest[i + 1] if i + 1 < len(rest) else None
                rest = rest[:i] + rest[i + 2:]
            kunde = " ".join(rest)
            register_active_mta(slug, folder_id, kunde, working_dir=working_dir)
            print("registered")
        elif cmd == "get-mta":
            mta = get_active_mta(args[0])
            print(json.dumps(mta, indent=2, ensure_ascii=False) if mta else "")
        elif cmd == "list-mtas":
            print(json.dumps(list_active_mtas(), indent=2, ensure_ascii=False))
        elif cmd == "list-children":
            print(json.dumps(list_children(args[0]), indent=2, ensure_ascii=False))
        else:
            print(f"Unbekanntes Kommando: {cmd}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            sys.exit(1)
    except IndexError:
        print(f"Fehlende Argumente für '{cmd}'.", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    except DriveError as e:
        print(f"Drive-Fehler: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    _cli()
