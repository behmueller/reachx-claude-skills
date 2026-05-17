#!/usr/bin/env python3
"""
REACHX MTA-Skills — Google-Ads-Helper (First-Party)

Wrappt die offizielle `google-ads`-Python-Library in eine CLI mit JSON-Output,
analog zu `drive.py`. Liefert First-Party-Account-Daten (eigene Kundenkonten
unter dem REACHX-MCC) fuer den SEA-First-Party-Skill — im Gegensatz zu
03-05-sea-google-ads-check, das via Transparency Center nur Wettbewerber sieht.

Designprinzipien (analog drive.py):
  - Eine zustandslose CLI, kein laufender Prozess. Jeder Aufruf laedt die
    Credentials, fuehrt eine GAQL-Query aus, schreibt JSON nach stdout.
  - Geld kommt aus der API in Micros (1 EUR = 1_000_000) — wird hier zu
    Waehrungs-Einheiten normalisiert. `currency` wird pro Antwort mitgeliefert.
  - Listen-Befehle geben ein Wrapper-Objekt zurueck:
        {"customer_id", "currency", "range", "count", "rows": [...]}

Auth-Credentials: ~/.config/reachx-mta/google-ads.yaml (chmod 600), erzeugt via
`google-oauth.py --service ads`. Faellt auf das fruehere gemeinsame
google-credentials.yaml zurueck, falls vorhanden. Pfad ueberschreibbar via
REACHX_GOOGLE_ADS_CREDENTIALS. NIEMALS ins Repo committen.

CLI:
    python3 google-ads.py list-accounts
    python3 google-ads.py account-overview     <customer_id> [--range R]
    python3 google-ads.py campaign-performance <customer_id> [--range R]
    python3 google-ads.py search-terms         <customer_id> [--range R] [--limit N]
    python3 google-ads.py keyword-performance  <customer_id> [--range R] [--limit N]
    python3 google-ads.py conversion-actions   <customer_id>
    python3 google-ads.py run-gaql             <customer_id> "<GAQL>"

--range:  GAQL-Datums-Literal (LAST_7_DAYS, LAST_14_DAYS, LAST_30_DAYS,
          THIS_MONTH, LAST_MONTH, LAST_BUSINESS_WEEK, ALL_TIME, ...)
          ODER ein expliziter Bereich "YYYY-MM-DD:YYYY-MM-DD".
          Default: LAST_30_DAYS.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# gRPC nutzt per Default den c-ares-DNS-Resolver, der in manchen Umgebungen
# (Sandboxes, restriktive Netzwerke) die DNS-Server nicht erreicht, obwohl der
# System-Resolver funktioniert. Den nativen OS-Resolver erzwingen — muss vor
# dem Import der grpc-/google-Libraries gesetzt sein. Via Env-Var überschreibbar.
os.environ.setdefault("GRPC_DNS_RESOLVER", "native")

# ---------- Konfiguration ----------

def _config_path() -> Path:
    """Credential-Datei: Env-Override, sonst die dedizierte google-ads.yaml,
    sonst (Fallback) das fruehere gemeinsame google-credentials.yaml."""
    env = os.environ.get("REACHX_GOOGLE_ADS_CREDENTIALS")
    if env:
        return Path(env)
    base = Path.home() / ".config" / "reachx-mta"
    dedicated = base / "google-ads.yaml"
    return dedicated if dedicated.exists() else base / "google-credentials.yaml"


CONFIG_PATH = _config_path()

# Gaengige GAQL-Datums-Literale. Fuer beliebige Zeitraeume (z.B. 12 Monate)
# stattdessen "YYYY-MM-DD:YYYY-MM-DD" an --range uebergeben.
DATE_LITERALS = {
    "TODAY", "YESTERDAY", "LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS",
    "LAST_BUSINESS_WEEK", "LAST_WEEK_MON_SUN", "LAST_WEEK_SUN_SAT",
    "THIS_MONTH", "LAST_MONTH", "ALL_TIME",
    "THIS_WEEK_MON_TODAY", "THIS_WEEK_SUN_TODAY",
}

DEFAULT_RANGE = "LAST_30_DAYS"


class GoogleAdsHelperError(RuntimeError):
    """Wird bei jedem Konfig-, Auth- oder API-Fehler geworfen."""


# ---------- Auth / Low-Level ----------

def _client():
    """Laedt den GoogleAdsClient aus der google-ads.yaml."""
    if not CONFIG_PATH.exists():
        raise GoogleAdsHelperError(
            f"Credential-Datei fehlt: {CONFIG_PATH}\n"
            f"  Einmalig erzeugen mit:  google-oauth.py --service ads ...\n"
            f"  (Felder: developer_token, client_id, client_secret, refresh_token,\n"
            f"  login_customer_id.) Pfad ueberschreibbar via REACHX_GOOGLE_ADS_CREDENTIALS."
        )
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        raise GoogleAdsHelperError(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r <plugin>/scripts/requirements-google.txt"
        )
    try:
        return GoogleAdsClient.load_from_storage(str(CONFIG_PATH))
    except Exception as e:  # noqa: BLE001 — Konfig-Fehler sollen klar rauskommen
        raise GoogleAdsHelperError(f"Konnte Credentials nicht laden: {e}")


def _clean_cid(customer_id: str) -> str:
    """Entfernt Bindestriche/Whitespace — die API will reine Ziffern."""
    return "".join(ch for ch in str(customer_id) if ch.isdigit())


def _explain(e: Exception) -> str:
    """Holt die lesbare Fehlermeldung aus einer GoogleAdsException heraus."""
    failure = getattr(e, "failure", None)
    if failure is not None:
        msgs = [err.message for err in getattr(failure, "errors", []) if err.message]
        if msgs:
            return "; ".join(msgs)
    return f"{type(e).__name__}: {e}"


def _search(client, customer_id: str, query: str) -> list:
    """Fuehrt eine GAQL-Query via SearchStream aus, gibt die Roh-Rows zurueck."""
    ga = client.get_service("GoogleAdsService")
    cid = _clean_cid(customer_id)
    if not cid:
        raise GoogleAdsHelperError(f"Ungueltige customer_id: {customer_id!r}")
    rows = []
    try:
        for batch in ga.search_stream(customer_id=cid, query=query):
            rows.extend(batch.results)
    except Exception as e:  # noqa: BLE001
        raise GoogleAdsHelperError(_explain(e))
    return rows


def _date_clause(range_arg: str | None) -> str:
    """Baut die WHERE-Datums-Bedingung aus --range."""
    r = (range_arg or DEFAULT_RANGE).strip()
    if ":" in r:
        start, end = (p.strip() for p in r.split(":", 1))
        return f"segments.date BETWEEN '{start}' AND '{end}'"
    if r.upper() in DATE_LITERALS:
        return f"segments.date DURING {r.upper()}"
    raise GoogleAdsHelperError(
        f"Ungueltiger --range Wert: {r!r}. Erlaubt: GAQL-Literal "
        f"(z.B. LAST_30_DAYS) oder 'YYYY-MM-DD:YYYY-MM-DD'."
    )


def _eur(micros: int | None) -> float:
    """Micros -> Waehrungs-Einheiten (1 EUR = 1_000_000 Micros)."""
    return round((micros or 0) / 1_000_000, 2)


def _wrap(customer_id: str, range_arg: str | None, rows: list, currency: str) -> dict:
    """Standard-Wrapper-Objekt fuer Listen-Befehle."""
    return {
        "customer_id": _clean_cid(customer_id),
        "currency": currency or "",
        "range": range_arg or DEFAULT_RANGE,
        "count": len(rows),
        "rows": rows,
    }


# ---------- Befehle ----------

def cmd_list_accounts(client) -> list:
    """Alle Kundenkonten (Level <= 1) unter dem MCC aus der config."""
    mcc = getattr(client, "login_customer_id", None)
    if not mcc:
        raise GoogleAdsHelperError("login_customer_id (MCC) fehlt in der google-ads.yaml.")
    query = """
        SELECT customer_client.id, customer_client.descriptive_name,
               customer_client.currency_code, customer_client.manager,
               customer_client.status, customer_client.level
        FROM customer_client
        WHERE customer_client.level <= 1
    """
    out = []
    for r in _search(client, str(mcc), query):
        c = r.customer_client
        out.append({
            "customer_id": str(c.id),
            "name": c.descriptive_name,
            "currency": c.currency_code,
            "is_manager": c.manager,
            "status": c.status.name,
            "level": c.level,
        })
    return out


def cmd_account_overview(client, customer_id: str, range_arg: str | None) -> dict:
    """Account-Aggregat (eine Zeile) fuer den Zeitraum."""
    query = f"""
        SELECT customer.id, customer.descriptive_name, customer.currency_code,
               metrics.cost_micros, metrics.impressions, metrics.clicks,
               metrics.conversions, metrics.conversions_value,
               metrics.ctr, metrics.average_cpc
        FROM customer
        WHERE {_date_clause(range_arg)}
    """
    rows = _search(client, customer_id, query)
    if not rows:
        return {"customer_id": _clean_cid(customer_id), "range": range_arg or DEFAULT_RANGE,
                "note": "Keine Daten fuer den Zeitraum."}
    r = rows[0]
    m = r.metrics
    return {
        "customer_id": str(r.customer.id),
        "name": r.customer.descriptive_name,
        "currency": r.customer.currency_code,
        "range": range_arg or DEFAULT_RANGE,
        "cost": _eur(m.cost_micros),
        "impressions": m.impressions,
        "clicks": m.clicks,
        "conversions": round(m.conversions, 2),
        "conversions_value": round(m.conversions_value, 2),
        "ctr": round(m.ctr, 4),
        "avg_cpc": _eur(m.average_cpc),
    }


def cmd_campaign_performance(client, customer_id: str, range_arg: str | None) -> dict:
    """Performance je Kampagne, nach Kosten absteigend."""
    query = f"""
        SELECT customer.currency_code,
               campaign.id, campaign.name, campaign.status,
               campaign.advertising_channel_type,
               metrics.cost_micros, metrics.impressions, metrics.clicks,
               metrics.conversions, metrics.conversions_value,
               metrics.ctr, metrics.average_cpc
        FROM campaign
        WHERE {_date_clause(range_arg)}
        ORDER BY metrics.cost_micros DESC
    """
    rows = _search(client, customer_id, query)
    currency = rows[0].customer.currency_code if rows else ""
    out = []
    for r in rows:
        m = r.metrics
        out.append({
            "campaign_id": str(r.campaign.id),
            "campaign": r.campaign.name,
            "status": r.campaign.status.name,
            "channel_type": r.campaign.advertising_channel_type.name,
            "cost": _eur(m.cost_micros),
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 2),
            "conversions_value": round(m.conversions_value, 2),
            "ctr": round(m.ctr, 4),
            "avg_cpc": _eur(m.average_cpc),
        })
    return _wrap(customer_id, range_arg, out, currency)


def cmd_search_terms(client, customer_id: str, range_arg: str | None, limit: int) -> dict:
    """Search-Terms-Report — welche echten Suchanfragen Ads ausgeloest haben."""
    query = f"""
        SELECT customer.currency_code,
               search_term_view.search_term, search_term_view.status,
               campaign.name,
               metrics.impressions, metrics.clicks, metrics.conversions,
               metrics.cost_micros, metrics.ctr
        FROM search_term_view
        WHERE {_date_clause(range_arg)}
        ORDER BY metrics.impressions DESC
        LIMIT {int(limit)}
    """
    rows = _search(client, customer_id, query)
    currency = rows[0].customer.currency_code if rows else ""
    out = []
    for r in rows:
        m = r.metrics
        out.append({
            "search_term": r.search_term_view.search_term,
            "status": r.search_term_view.status.name,
            "campaign": r.campaign.name,
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 2),
            "cost": _eur(m.cost_micros),
            "ctr": round(m.ctr, 4),
        })
    return _wrap(customer_id, range_arg, out, currency)


def cmd_keyword_performance(client, customer_id: str, range_arg: str | None, limit: int) -> dict:
    """Keyword-Performance inkl. Quality Score."""
    query = f"""
        SELECT customer.currency_code,
               ad_group_criterion.keyword.text,
               ad_group_criterion.keyword.match_type,
               ad_group_criterion.quality_info.quality_score,
               campaign.name,
               metrics.impressions, metrics.clicks, metrics.conversions,
               metrics.cost_micros, metrics.average_cpc
        FROM keyword_view
        WHERE {_date_clause(range_arg)}
        ORDER BY metrics.impressions DESC
        LIMIT {int(limit)}
    """
    rows = _search(client, customer_id, query)
    currency = rows[0].customer.currency_code if rows else ""
    out = []
    for r in rows:
        m = r.metrics
        crit = r.ad_group_criterion
        qs = crit.quality_info.quality_score
        out.append({
            "keyword": crit.keyword.text,
            "match_type": crit.keyword.match_type.name,
            "quality_score": qs if qs else None,
            "campaign": r.campaign.name,
            "impressions": m.impressions,
            "clicks": m.clicks,
            "conversions": round(m.conversions, 2),
            "cost": _eur(m.cost_micros),
            "avg_cpc": _eur(m.average_cpc),
        })
    return _wrap(customer_id, range_arg, out, currency)


def cmd_conversion_actions(client, customer_id: str) -> dict:
    """Conversion-Tracking-Setup — welche Conversions definiert sind und ihr Status."""
    query = """
        SELECT conversion_action.id, conversion_action.name,
               conversion_action.status, conversion_action.type,
               conversion_action.category, conversion_action.counting_type,
               conversion_action.primary_for_goal
        FROM conversion_action
    """
    rows = _search(client, customer_id, query)
    out = []
    for r in rows:
        ca = r.conversion_action
        out.append({
            "id": str(ca.id),
            "name": ca.name,
            "status": ca.status.name,
            "type": ca.type_.name,
            "category": ca.category.name,
            "counting_type": ca.counting_type.name,
            "primary_for_goal": ca.primary_for_goal,
        })
    return {
        "customer_id": _clean_cid(customer_id),
        "count": len(out),
        "rows": out,
    }


def cmd_run_gaql(client, customer_id: str, query: str) -> list:
    """Roh-GAQL fuer Sonderfaelle — Rows als verschachteltes Dict."""
    from google.protobuf.json_format import MessageToDict
    rows = _search(client, customer_id, query)
    return [MessageToDict(r._pb, preserving_proto_field_name=True) for r in rows]


# ---------- CLI ----------

def _pop_opt(args: list[str], name: str, default: str | None = None) -> tuple[str | None, list[str]]:
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
    limit_arg, args = _pop_opt(args, "--limit", "200")
    try:
        limit = int(limit_arg) if limit_arg else 200
    except ValueError:
        print(f"--limit muss eine Zahl sein, war: {limit_arg!r}", file=sys.stderr)
        sys.exit(1)

    try:
        client = _client()

        if cmd == "list-accounts":
            result = cmd_list_accounts(client)
        elif cmd == "account-overview":
            result = cmd_account_overview(client, args[0], range_arg)
        elif cmd == "campaign-performance":
            result = cmd_campaign_performance(client, args[0], range_arg)
        elif cmd == "search-terms":
            result = cmd_search_terms(client, args[0], range_arg, limit)
        elif cmd == "keyword-performance":
            result = cmd_keyword_performance(client, args[0], range_arg, limit)
        elif cmd == "conversion-actions":
            result = cmd_conversion_actions(client, args[0])
        elif cmd == "run-gaql":
            result = cmd_run_gaql(client, args[0], args[1])
        else:
            print(f"Unbekanntes Kommando: {cmd}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            sys.exit(1)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    except IndexError:
        print(f"Fehlende Argumente fuer '{cmd}'.", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    except GoogleAdsHelperError as e:
        print(f"Google-Ads-Fehler: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    _cli()
