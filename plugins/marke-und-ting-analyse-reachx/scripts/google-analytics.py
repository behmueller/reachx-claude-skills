#!/usr/bin/env python3
"""
REACHX MTA-Skills — Google-Analytics-Helper (GA4, First-Party)

Wrappt die GA4 Data API (Reporting) und die GA4 Admin API (Property-Liste)
in eine CLI mit JSON-Output, analog zu google-ads.py / drive.py.

Auth: OAuth-User-Credentials aus ~/.config/reachx-mta/google-analytics.yaml
(chmod 600), erzeugt via `google-oauth.py --service analytics`. Enthaelt
client_id, client_secret, refresh_token. Faellt auf das fruehere gemeinsame
google-credentials.yaml zurueck, falls vorhanden. Pfad ueberschreibbar via
REACHX_GOOGLE_ANALYTICS_CREDENTIALS.

CLI:
    python3 google-analytics.py list-properties
    python3 google-analytics.py overview    <property_id> [--range R]
    python3 google-analytics.py channels    <property_id> [--range R]
    python3 google-analytics.py top-pages   <property_id> [--range R] [--limit N]
    python3 google-analytics.py conversions <property_id> [--range R]
    python3 google-analytics.py run-report  <property_id> --metrics m1,m2 \\
                                            [--dimensions d1,d2] [--range R] [--limit N]

--range:  "<N>daysAgo" (Default 30daysAgo, Ende = today) ODER ein expliziter
          Bereich "YYYY-MM-DD:YYYY-MM-DD".
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# gRPC nutzt per Default den c-ares-DNS-Resolver, der in manchen Umgebungen
# (Sandboxes, restriktive Netzwerke) die DNS-Server nicht erreicht, obwohl der
# System-Resolver funktioniert. Den nativen OS-Resolver erzwingen — muss vor
# dem Import der grpc-/google-Libraries gesetzt sein. Via Env-Var überschreibbar.
os.environ.setdefault("GRPC_DNS_RESOLVER", "native")

def _config_path() -> Path:
    """Credential-Datei: Env-Override, sonst die dedizierte google-analytics.yaml,
    sonst (Fallback) das fruehere gemeinsame google-credentials.yaml."""
    env = os.environ.get("REACHX_GOOGLE_ANALYTICS_CREDENTIALS")
    if env:
        return Path(env)
    base = Path.home() / ".config" / "reachx-mta"
    dedicated = base / "google-analytics.yaml"
    return dedicated if dedicated.exists() else base / "google-credentials.yaml"


CONFIG_PATH = _config_path()

ANALYTICS_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
DEFAULT_RANGE = "30daysAgo"


class AnalyticsHelperError(RuntimeError):
    """Wird bei jedem Konfig-, Auth- oder API-Fehler geworfen."""


# ---------- Auth / Low-Level ----------

def _credentials():
    """Baut OAuth-User-Credentials aus der google-analytics.yaml."""
    if not CONFIG_PATH.exists():
        raise AnalyticsHelperError(
            f"Credential-Datei fehlt: {CONFIG_PATH}\n"
            f"  Einmalig erzeugen mit:  google-oauth.py --service analytics ...\n"
            f"  Pfad ueberschreibbar via REACHX_GOOGLE_ANALYTICS_CREDENTIALS."
        )
    try:
        import yaml
        from google.oauth2.credentials import Credentials
    except ImportError:
        raise AnalyticsHelperError(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-google.txt"
        )
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    missing = [k for k in ("client_id", "client_secret", "refresh_token")
               if not data.get(k)]
    if missing:
        raise AnalyticsHelperError(
            f"Felder fehlen in {CONFIG_PATH}: {', '.join(missing)}. "
            f"google-oauth.py erneut ausfuehren."
        )
    return Credentials(
        token=None,
        refresh_token=data["refresh_token"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=[ANALYTICS_SCOPE],
    )


def _data_client(creds):
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError:
        raise AnalyticsHelperError(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-google.txt"
        )
    return BetaAnalyticsDataClient(credentials=creds)


def _prop(property_id: str) -> str:
    """Normalisiert die Property-ID zu 'properties/<ziffern>'."""
    digits = "".join(ch for ch in str(property_id) if ch.isdigit())
    if not digits:
        raise AnalyticsHelperError(f"Ungueltige property_id: {property_id!r}")
    return f"properties/{digits}"


def _date_range(range_arg: str | None) -> tuple[str, str]:
    """Loest --range zu (start_date, end_date) im GA4-Format auf."""
    r = (range_arg or DEFAULT_RANGE).strip()
    if ":" in r:
        start, end = (p.strip() for p in r.split(":", 1))
        return start, end
    if re.fullmatch(r"\d+daysAgo", r) or r in ("today", "yesterday"):
        return r, "today"
    raise AnalyticsHelperError(
        f"Ungueltiger --range Wert: {r!r}. Erlaubt: '<N>daysAgo' "
        f"(z.B. 30daysAgo) oder 'YYYY-MM-DD:YYYY-MM-DD'."
    )


def _num(value: str):
    """GA4 liefert Metrik-Werte als String — zu int/float casten wo moeglich."""
    try:
        f = float(value)
        return int(f) if f.is_integer() else round(f, 4)
    except (ValueError, TypeError):
        return value


def _run_report(client, property_id: str, dimensions: list[str],
                metrics: list[str], range_arg: str | None,
                limit: int | None = None, order_by_metric: str | None = None) -> dict:
    """Fuehrt einen GA4-Report aus, gibt ein Wrapper-Objekt mit Zeilen zurueck."""
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric, OrderBy,
    )
    start, end = _date_range(range_arg)
    kwargs = dict(
        property=_prop(property_id),
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start, end_date=end)],
    )
    if limit:
        kwargs["limit"] = int(limit)
    if order_by_metric:
        kwargs["order_bys"] = [
            OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order_by_metric), desc=True)
        ]
    try:
        resp = client.run_report(RunReportRequest(**kwargs))
    except Exception as e:  # noqa: BLE001
        raise AnalyticsHelperError(f"{type(e).__name__}: {e}")

    dim_names = [h.name for h in resp.dimension_headers]
    met_names = [h.name for h in resp.metric_headers]
    rows = []
    for row in resp.rows:
        rec = {}
        for i, name in enumerate(dim_names):
            rec[name] = row.dimension_values[i].value
        for i, name in enumerate(met_names):
            rec[name] = _num(row.metric_values[i].value)
        rows.append(rec)
    return {
        "property": _prop(property_id),
        "range": {"start": start, "end": end},
        "row_count": getattr(resp, "row_count", len(rows)),
        "rows": rows,
    }


# ---------- Befehle ----------

def cmd_list_properties(creds) -> dict:
    """Alle GA4-Properties, auf die der OAuth-Account Zugriff hat (Admin API)."""
    try:
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
    except ImportError:
        raise AnalyticsHelperError(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-google.txt"
        )
    admin = AnalyticsAdminServiceClient(credentials=creds)
    out = []
    try:
        for summary in admin.list_account_summaries():
            for p in summary.property_summaries:
                out.append({
                    "property_id": p.property.split("/")[-1],
                    "display_name": p.display_name,
                    "account": summary.display_name,
                })
    except Exception as e:  # noqa: BLE001
        raise AnalyticsHelperError(f"{type(e).__name__}: {e}")
    return {"count": len(out), "rows": out}


def cmd_overview(client, property_id: str, range_arg: str | None) -> dict:
    """Account-Aggregat ohne Dimension — die Kern-Kennzahlen des Zeitraums."""
    metrics = ["sessions", "totalUsers", "newUsers", "screenPageViews",
               "engagementRate", "averageSessionDuration", "keyEvents"]
    rep = _run_report(client, property_id, [], metrics, range_arg)
    return {
        "property": rep["property"],
        "range": rep["range"],
        "metrics": rep["rows"][0] if rep["rows"] else {},
    }


def cmd_channels(client, property_id: str, range_arg: str | None) -> dict:
    """Traffic nach Default Channel Group — Organic / Paid / Direct / Social ..."""
    return _run_report(
        client, property_id,
        ["sessionDefaultChannelGroup"],
        ["sessions", "totalUsers", "newUsers", "keyEvents", "engagementRate"],
        range_arg, order_by_metric="sessions",
    )


def cmd_top_pages(client, property_id: str, range_arg: str | None, limit: int) -> dict:
    """Meistbesuchte Seiten nach Aufrufen."""
    return _run_report(
        client, property_id,
        ["pagePath"],
        ["screenPageViews", "sessions", "totalUsers", "averageSessionDuration"],
        range_arg, limit=limit, order_by_metric="screenPageViews",
    )


def cmd_conversions(client, property_id: str, range_arg: str | None) -> dict:
    """Events nach Key-Event-Zahl — Key Events (Conversions) stehen oben."""
    return _run_report(
        client, property_id,
        ["eventName"],
        ["keyEvents", "eventCount", "eventValue"],
        range_arg, order_by_metric="keyEvents",
    )


# ---------- CLI ----------

def _pop_opt(args: list[str], name: str, default: str | None = None):
    """Zieht `--name <wert>` aus der Argumentliste; gibt (wert, rest) zurueck."""
    if name in args:
        i = args.index(name)
        val = args[i + 1] if i + 1 < len(args) else None
        return val, args[:i] + args[i + 2:]
    return default, args


def _cli() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    cmd, args = argv[0], argv[1:]

    range_arg, args = _pop_opt(args, "--range")
    limit_arg, args = _pop_opt(args, "--limit", "100")
    dims_arg, args = _pop_opt(args, "--dimensions")
    mets_arg, args = _pop_opt(args, "--metrics")
    try:
        limit = int(limit_arg) if limit_arg else 100
    except ValueError:
        print(f"--limit muss eine Zahl sein, war: {limit_arg!r}", file=sys.stderr)
        sys.exit(1)

    try:
        creds = _credentials()

        if cmd == "list-properties":
            result = cmd_list_properties(creds)
        elif cmd == "overview":
            result = cmd_overview(_data_client(creds), args[0], range_arg)
        elif cmd == "channels":
            result = cmd_channels(_data_client(creds), args[0], range_arg)
        elif cmd == "top-pages":
            result = cmd_top_pages(_data_client(creds), args[0], range_arg, limit)
        elif cmd == "conversions":
            result = cmd_conversions(_data_client(creds), args[0], range_arg)
        elif cmd == "run-report":
            if not mets_arg:
                raise AnalyticsHelperError("run-report braucht --metrics (CSV-Liste).")
            dims = [d.strip() for d in (dims_arg or "").split(",") if d.strip()]
            mets = [m.strip() for m in mets_arg.split(",") if m.strip()]
            result = _run_report(_data_client(creds), args[0], dims, mets,
                                 range_arg, limit=limit)
        else:
            print(f"Unbekanntes Kommando: {cmd}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except IndexError:
        print(f"Fehlende Argumente fuer '{cmd}'.", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    except AnalyticsHelperError as e:
        print(f"Analytics-Fehler: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    _cli()
