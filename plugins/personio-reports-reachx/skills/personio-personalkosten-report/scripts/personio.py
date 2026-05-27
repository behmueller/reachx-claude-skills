#!/usr/bin/env python3
"""
REACHX Personio-Report — Personio-API-Helper (First-Party, read-only)

Wrappt die Personio REST API v1 (Mitarbeiter-Endpunkt) in eine CLI mit
JSON-Output. Analog zu den Google-Wrappern des MTA-Plugins.

Auth: client_id / client_secret aus ~/.config/reachx-mta/personio.yaml
(chmod 600), erzeugt in Personio unter Einstellungen > Integrationen >
API-Zugaenge. Pfad ueberschreibbar via REACHX_PERSONIO_CREDENTIALS.

Der Helper liest ausschliesslich — es gibt KEINEN schreibenden Befehl.
Der API-Zugriff nutzt nur die Python-Standardbibliothek (urllib); fuer das
Lesen der Credential-YAML wird PyYAML benoetigt.

CLI:
    python3 personio.py auth-check
        Prueft Credentials und Erreichbarkeit, gibt Token-Status zurueck.

    python3 personio.py employees [--include-inactive] [--out DATEI]
        Laedt alle Mitarbeiter (paginiert), flacht die Attribute ab und
        schreibt ein normalisiertes JSON nach stdout oder --out.

    python3 personio.py attributes [--include-inactive]
        Listet alle in den Mitarbeiterdaten vorkommenden Attribut-Schluessel
        mit Label, Befuellungs-Quote und Beispielwert — hilft, das richtige
        Gehalts-Attribut zu finden (z.B. ein Custom-Attribut dynamic_NNNN).

Exit-Code 0 bei Erfolg, 1 bei jedem Konfig-, Auth- oder API-Fehler.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://api.personio.de/v1"
PAGE_LIMIT = 200            # Personio-Maximum pro Seite
HTTP_TIMEOUT = 60           # Sekunden pro Request


def _ssl_context() -> ssl.SSLContext:
    """TLS-Kontext mit verlaesslichem CA-Bundle. Die Python.framework-
    Installation auf macOS bringt oft keine System-CAs mit — dann das
    certifi-Bundle nutzen, falls vorhanden."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()


class PersonioHelperError(RuntimeError):
    """Wird bei jedem Konfig-, Auth- oder API-Fehler geworfen."""


# ---------- Credentials ----------

def _config_path() -> Path:
    env = os.environ.get("REACHX_PERSONIO_CREDENTIALS")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config" / "reachx-mta" / "personio.yaml"


def _load_credentials() -> dict:
    path = _config_path()
    if not path.exists():
        raise PersonioHelperError(
            f"Credential-Datei fehlt: {path}\n"
            f"  Vorlage: reference/credentials-vorlage.yaml nach {path} kopieren,\n"
            f"  client_id/client_secret eintragen, dann  chmod 600  setzen.\n"
            f"  Pfad ueberschreibbar via REACHX_PERSONIO_CREDENTIALS."
        )
    try:
        import yaml
    except ImportError:
        raise PersonioHelperError(
            "PyYAML fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-personio.txt"
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    missing = [k for k in ("client_id", "client_secret") if not data.get(k)]
    if missing:
        raise PersonioHelperError(
            f"Felder fehlen in {path}: {', '.join(missing)}."
        )
    placeholder = ("PUT-YOUR-CLIENT-ID-HERE", "PUT-YOUR-CLIENT-SECRET-HERE")
    if data["client_id"] in placeholder or data["client_secret"] in placeholder:
        raise PersonioHelperError(
            f"{path} enthaelt noch die Platzhalter aus der Vorlage. "
            f"Echte Personio-Zugangsdaten eintragen."
        )
    base_url = (data.get("base_url") or DEFAULT_BASE_URL).rstrip("/")
    return {
        "client_id": str(data["client_id"]),
        "client_secret": str(data["client_secret"]),
        "base_url": base_url,
    }


# ---------- HTTP / API ----------

def _request(method: str, url: str, *, token: str | None = None,
             body: dict | None = None) -> tuple[dict, dict]:
    """Fuehrt einen HTTP-Request aus. Gibt (json_body, response_headers) zurueck."""
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT,
                                    context=SSL_CONTEXT) as resp:
            raw = resp.read().decode("utf-8")
            resp_headers = dict(resp.headers.items())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
            msg = parsed.get("error", {}).get("message") or raw
        except json.JSONDecodeError:
            msg = raw[:500]
        if exc.code == 401:
            raise PersonioHelperError(
                f"Personio lehnt die Authentifizierung ab (HTTP 401): {msg}\n"
                f"  client_id/client_secret pruefen — und ob der API-Zugang "
                f"in Personio noch aktiv ist."
            )
        if exc.code == 403:
            raise PersonioHelperError(
                f"Zugriff verweigert (HTTP 403): {msg}\n"
                f"  Dem API-Zugang fehlt eine Leseberechtigung fuer diesen "
                f"Endpunkt oder fuer einzelne Attribute."
            )
        if exc.code == 429:
            raise PersonioHelperError(
                "Personio-Rate-Limit erreicht (HTTP 429). Kurz warten und "
                "den Skill erneut aufrufen."
            )
        raise PersonioHelperError(f"Personio-API-Fehler (HTTP {exc.code}): {msg}")
    except urllib.error.URLError as exc:
        raise PersonioHelperError(
            f"Personio nicht erreichbar: {exc.reason}\n"
            f"  Netzwerkverbindung und base_url pruefen."
        )
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise PersonioHelperError(
            f"Antwort von Personio ist kein gueltiges JSON: {raw[:300]}"
        )
    if isinstance(parsed, dict) and parsed.get("success") is False:
        err = parsed.get("error", {})
        raise PersonioHelperError(
            f"Personio meldet einen Fehler "
            f"(code {err.get('code', '?')}): {err.get('message', 'unbekannt')}"
        )
    return parsed, resp_headers


def _authenticate(creds: dict) -> str:
    """Holt einen Bearer-Token (24h gueltig) vom /auth-Endpunkt."""
    url = f"{creds['base_url']}/auth"
    parsed, _ = _request("POST", url, body={
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
    })
    token = (parsed.get("data") or {}).get("token")
    if not token:
        raise PersonioHelperError(
            "Personio hat keinen Token geliefert — Antwort unerwartet aufgebaut."
        )
    return token


def _next_token(resp_headers: dict, fallback: str) -> str:
    """Personio rotiert den Token und liefert den neuen im Authorization-
    Response-Header. Diesen fuer den naechsten Request uebernehmen."""
    auth = resp_headers.get("Authorization") or resp_headers.get("authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return fallback


def _fetch_all_employees(creds: dict, token: str) -> tuple[list, str]:
    """Laedt alle Mitarbeiter ueber Limit/Offset-Pagination. Gibt
    (rohe Employee-Liste, letzter Token) zurueck."""
    employees: list = []
    offset = 0
    while True:
        query = urllib.parse.urlencode({"limit": PAGE_LIMIT, "offset": offset})
        url = f"{creds['base_url']}/company/employees?{query}"
        parsed, resp_headers = _request("GET", url, token=token)
        token = _next_token(resp_headers, token)
        page = parsed.get("data") or []
        employees.extend(page)
        if len(page) < PAGE_LIMIT:
            break
        offset += PAGE_LIMIT
        if offset > 100000:        # Sicherheitsnetz gegen Endlosschleifen
            raise PersonioHelperError("Pagination-Abbruch — unplausibel viele Seiten.")
    return employees, token


# ---------- Attribut-Flattening ----------

def _simplify_value(value):
    """Reduziert einen Personio-Attributwert auf einen flachen Wert.
    Verschachtelte Objekte (Abteilung, Team, Vorgesetzter ...) werden auf
    ihren Namen bzw. ihre ID heruntergebrochen."""
    if isinstance(value, dict):
        attrs = value.get("attributes")
        if isinstance(attrs, dict):
            if "name" in attrs:
                return attrs["name"]
            inner = attrs.get("id")
            if isinstance(inner, dict):
                return inner.get("value")
            return inner
        return value.get("value", value)
    if isinstance(value, list):
        return [_simplify_value(v) for v in value]
    return value


def _flatten_employee(raw: dict) -> dict:
    """Macht aus einem rohen Employee-Objekt eine flache key->value-Map."""
    flat: dict = {}
    attributes = raw.get("attributes") or {}
    for key, wrapper in attributes.items():
        if isinstance(wrapper, dict) and "value" in wrapper:
            flat[key] = _simplify_value(wrapper["value"])
        else:
            flat[key] = _simplify_value(wrapper)
    return flat


def _collect_labels(raw_employees: list) -> dict:
    """Sammelt key->label fuer alle vorkommenden Attribute (inkl. Custom)."""
    labels: dict = {}
    for raw in raw_employees:
        for key, wrapper in (raw.get("attributes") or {}).items():
            if key not in labels and isinstance(wrapper, dict):
                labels[key] = wrapper.get("label") or key
    return labels


def _is_empty(value) -> bool:
    return value in (None, "", [], {})


# ---------- Befehle ----------

def cmd_auth_check(_args) -> dict:
    creds = _load_credentials()
    token = _authenticate(creds)
    return {
        "success": True,
        "befehl": "auth-check",
        "base_url": creds["base_url"],
        "token_erhalten": True,
        "token_praefix": token[:8] + "…",
        "hinweis": "Credentials gueltig, Personio erreichbar.",
    }


def cmd_employees(args) -> dict:
    creds = _load_credentials()
    token = _authenticate(creds)
    raw_employees, _ = _fetch_all_employees(creds, token)
    labels = _collect_labels(raw_employees)
    flat = [_flatten_employee(r) for r in raw_employees]

    if not args.include_inactive:
        flat = [e for e in flat
                if str(e.get("status", "")).lower() != "inactive"]

    salary_keys = ["fix_salary", "fix_salary_interval", "hourly_salary", "bonus"]
    salary_present = {k: any(not _is_empty(e.get(k)) for e in flat)
                      for k in salary_keys}

    return {
        "success": True,
        "befehl": "employees",
        "fetched_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "base_url": creds["base_url"],
        "include_inactive": args.include_inactive,
        "count": len(flat),
        "count_roh_inkl_inaktiv": len(raw_employees),
        "gehaltsfelder_vorhanden": salary_present,
        "attribute_labels": labels,
        "employees": flat,
    }


def cmd_attributes(args) -> dict:
    creds = _load_credentials()
    token = _authenticate(creds)
    raw_employees, _ = _fetch_all_employees(creds, token)
    labels = _collect_labels(raw_employees)
    flat = [_flatten_employee(r) for r in raw_employees]
    if not args.include_inactive:
        flat = [e for e in flat
                if str(e.get("status", "")).lower() != "inactive"]

    total = len(flat) or 1
    rows = []
    for key, label in sorted(labels.items()):
        befuellt = sum(1 for e in flat if not _is_empty(e.get(key)))
        beispiel = next((e.get(key) for e in flat
                         if not _is_empty(e.get(key))), None)
        rows.append({
            "key": key,
            "label": label,
            "befuellt": befuellt,
            "befuellt_quote": round(befuellt / total, 3),
            "ist_custom": key.startswith("dynamic_"),
            "beispielwert": beispiel,
        })
    return {
        "success": True,
        "befehl": "attributes",
        "mitarbeiter_betrachtet": len(flat),
        "attribute": rows,
    }


COMMANDS = {
    "auth-check": cmd_auth_check,
    "employees": cmd_employees,
    "attributes": cmd_attributes,
}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="personio.py",
        description="REACHX Personio-API-Helper (read-only).",
    )
    sub = parser.add_subparsers(dest="befehl", required=True)

    sub.add_parser("auth-check", help="Credentials und Erreichbarkeit pruefen.")

    p_emp = sub.add_parser("employees", help="Alle Mitarbeiter als JSON laden.")
    p_emp.add_argument("--include-inactive", action="store_true",
                       help="Auch ausgeschiedene (status=inactive) Mitarbeiter.")
    p_emp.add_argument("--out", metavar="DATEI",
                       help="Ziel-Datei statt stdout.")

    p_attr = sub.add_parser("attributes",
                            help="Attribut-Schluessel und Befuellung auflisten.")
    p_attr.add_argument("--include-inactive", action="store_true")

    args = parser.parse_args(argv)

    try:
        result = COMMANDS[args.befehl](args)
    except PersonioHelperError as exc:
        print(json.dumps({"success": False, "error": str(exc)},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    except Exception as exc:                       # noqa: BLE001
        print(json.dumps({"success": False,
                          "error": f"Unerwarteter Fehler: {exc}"},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    out = getattr(args, "out", None)
    if out:
        Path(out).expanduser().write_text(payload + "\n", encoding="utf-8")
        print(json.dumps({"success": True, "geschrieben": out,
                          "count": result.get("count")},
                         ensure_ascii=False, indent=2))
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
