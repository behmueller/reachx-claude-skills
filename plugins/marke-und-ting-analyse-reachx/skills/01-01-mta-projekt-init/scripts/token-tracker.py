#!/usr/bin/env python3
"""
REACHX MTA-Skills — Token-Tracker

Aggregiert Claude-Code-Session-Tokens pro MTA (auf Basis der Working-Directory-bezogenen
Session-JSONL-Files unter `~/.claude/projects/`), summiert pro Modell und pro Skill,
rechnet Cost in EUR und schreibt das Aggregat lokal in den MTA-Cache plus auf Drive
in `meta/token-usage.json`.

Designprinzipien:
  - **Inkrementell**: Jeder Aggregate-Lauf merkt sich den zuletzt verarbeiteten Message-Cursor
    pro Session-JSONL und verarbeitet beim nächsten Mal nur Neues.
  - **Robust**: Bei jedem Fehler (kein active MTA, kein JSONL, Schema-Mismatch) lautlos
    `exit 0` — der Hook soll Session-Start nicht blockieren.
  - **Modell-Fuzzy**: `claude-opus-4-7-20260101` wird genauso als Opus erkannt wie
    `claude-opus-4-7`. Pricing wird nach Modell-Stem nachgeschlagen.

CLI:
    python3 token-tracker.py tick
        Findet die aktuell aktive MTA aus active-mtas.json (jüngster zuletzt_aktiv-Eintrag)
        und aggregiert deren Tokens. Default-Modus für den Stop-Hook.

    python3 token-tracker.py aggregate <mta-slug>
        Aggregiert explizit für einen MTA-Slug. Schreibt nach Drive (über drive.py).

    python3 token-tracker.py render-counter <mta-slug> --style {stat-strip|breakdown|md}
        Rendert das HTML- oder Markdown-Snippet für Dashboard/Reports.
        - `stat-strip`: Kompakter HTML-Block für den Dashboard-Stat-Strip
        - `breakdown`: Vollständige HTML-Sektion mit Tabellen
        - `md`: Markdown-Version (für status.md o.ä.)

    python3 token-tracker.py render-skill-counter <mta-slug> <skill-name>
        Rendert nur den Delta-Counter des angegebenen Skills (HTML-Snippet für
        den Footer eines Skill-Reports).

    python3 token-tracker.py mark-skill-start <mta-slug> <skill-name>
    python3 token-tracker.py mark-skill-end <mta-slug> <skill-name>
        Markiert Start/Ende eines Skill-Laufs, sodass die Aggregation die zwischen
        diesen Events liegenden Messages dem Skill zuordnen kann.
"""
from __future__ import annotations

import json
import os
import sys
import re
import datetime as dt
from pathlib import Path
from typing import Optional, Any

# ---------- Pfade und Konfiguration ----------

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
CACHE_DIR = Path.home() / ".cache" / "reachx-mta"
ACTIVE_MTAS_FILE = CACHE_DIR / "active-mtas.json"

# USD → EUR FX. Konfigurierbar via Env, Default eine konservative Schätzung.
USD_TO_EUR = float(os.environ.get("REACHX_USD_TO_EUR", "0.92"))

# Anthropic Pricing pro 1M Tokens (USD, Stand Mai 2026). Fuzzy-Match auf model-stem.
# Wenn Anthropic die Preise ändert: hier anpassen.
PRICING_USD_PER_MTOK = {
    "claude-opus-4-7": {
        "input": 15.0,
        "output": 75.0,
        "cache_read": 1.50,
        "cache_write_5m": 18.75,
        "cache_write_1h": 30.0,
    },
    "claude-opus-4-6": {
        "input": 15.0, "output": 75.0,
        "cache_read": 1.50, "cache_write_5m": 18.75, "cache_write_1h": 30.0,
    },
    "claude-sonnet-4-6": {
        "input": 3.0,
        "output": 15.0,
        "cache_read": 0.30,
        "cache_write_5m": 3.75,
        "cache_write_1h": 6.0,
    },
    "claude-sonnet-4-5": {
        "input": 3.0, "output": 15.0,
        "cache_read": 0.30, "cache_write_5m": 3.75, "cache_write_1h": 6.0,
    },
    "claude-haiku-4-5": {
        "input": 0.80,
        "output": 4.0,
        "cache_read": 0.08,
        "cache_write_5m": 1.00,
        "cache_write_1h": 1.60,
    },
    # Unbekanntes Modell: Fallback auf Sonnet-Pricing (konservativ-mittlere Schätzung)
    "_default": {
        "input": 3.0, "output": 15.0,
        "cache_read": 0.30, "cache_write_5m": 3.75, "cache_write_1h": 6.0,
    },
}


def _model_stem(model: str) -> str:
    """Mappt z.B. 'claude-opus-4-7-20260101' auf 'claude-opus-4-7'."""
    if not model:
        return "_unknown"
    # Strip trailing date suffix (YYYYMMDD)
    m = re.match(r"^(claude-[a-z]+-\d+-\d+)(-\d{8})?$", model)
    if m:
        return m.group(1)
    return model


def _pricing_for(model: str) -> dict:
    stem = _model_stem(model)
    return PRICING_USD_PER_MTOK.get(stem, PRICING_USD_PER_MTOK["_default"])


# ---------- Active-MTA-Resolution ----------

def _load_active_mtas() -> dict:
    if not ACTIVE_MTAS_FILE.exists():
        return {}
    try:
        return json.loads(ACTIVE_MTAS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _most_recent_active_mta_slug() -> Optional[str]:
    mtas = _load_active_mtas()
    if not mtas:
        return None
    return max(mtas.keys(), key=lambda s: mtas[s].get("zuletzt_aktiv", ""))


def _project_dir_for_mta(slug: str) -> Optional[Path]:
    """
    Findet das `~/.claude/projects/<encoded-cwd>/`-Verzeichnis für die MTA.
    Voraussetzung: active-mtas.json hat 'working_dir' für den Slug gespeichert.
    Wenn nicht: fällt zurück auf 'erstes Match' via Heuristik (CWD enthält den Slug).
    """
    mtas = _load_active_mtas()
    entry = mtas.get(slug)
    if entry and entry.get("working_dir"):
        wd = entry["working_dir"]
        encoded = wd.replace("/", "-")  # Claude-Code-Konvention
        candidate = PROJECTS_DIR / encoded
        if candidate.exists():
            return candidate
        # Manche Versionen verwenden auch Punkte-Encoding
        candidate2 = PROJECTS_DIR / encoded.replace(".", "-")
        if candidate2.exists():
            return candidate2
    # Fallback-Heuristik: Aus Slug die Kunden-Komponente extrahieren
    # (Format: mta-<kunden-slug>-<YYYY>-<MM>)
    kunden_slug = slug
    if kunden_slug.startswith("mta-"):
        kunden_slug = kunden_slug[4:]
    # Strip trailing YYYY-MM
    kunden_slug = re.sub(r"-\d{4}-\d{2}$", "", kunden_slug)
    # Tokens
    tokens = [t for t in kunden_slug.split("-") if t and not t.isdigit()]
    # Vom längsten zum kürzesten Token suchen — distinktive Tokens zuerst
    tokens.sort(key=len, reverse=True)

    candidates = []
    for d in PROJECTS_DIR.glob("*"):
        name_low = d.name.lower()
        # Wenn ALLE Tokens enthalten sind, ist das ein starker Treffer
        if all(t.lower() in name_low for t in tokens):
            candidates.append((d, 2, d.stat().st_mtime))
        elif tokens and tokens[0].lower() in name_low:
            candidates.append((d, 1, d.stat().st_mtime))

    if not candidates:
        return None
    # Beste Match-Score, dann jüngste mtime
    candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return candidates[0][0]


# ---------- Aggregation ----------

def _per_model_empty() -> dict:
    return {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_5m_tokens": 0,
        "cache_creation_1h_tokens": 0,
        "cache_read_tokens": 0,
        "message_count": 0,
        "cost_usd": 0.0,
        "cost_eur": 0.0,
    }


def _cost_for_usage(usage: dict, pricing: dict) -> tuple[float, float]:
    """Returns (cost_usd, cost_eur) für eine usage-dict."""
    input_t = usage.get("input_tokens", 0) or 0
    output_t = usage.get("output_tokens", 0) or 0
    cache_read = usage.get("cache_read_input_tokens", 0) or 0
    cache_create = usage.get("cache_creation_input_tokens", 0) or 0
    # Split cache_create auf 5m vs 1h falls verfügbar
    cc = usage.get("cache_creation", {}) or {}
    cc_5m = cc.get("ephemeral_5m_input_tokens", cache_create) or 0
    cc_1h = cc.get("ephemeral_1h_input_tokens", 0) or 0
    # Wenn cache_creation-Aufschlüsselung leer aber cache_creation_input_tokens>0:
    # nimm an, alles ist 5m
    if cc_5m + cc_1h == 0 and cache_create > 0:
        cc_5m = cache_create

    usd = (
        input_t * pricing["input"] / 1_000_000
        + output_t * pricing["output"] / 1_000_000
        + cache_read * pricing["cache_read"] / 1_000_000
        + cc_5m * pricing["cache_write_5m"] / 1_000_000
        + cc_1h * pricing["cache_write_1h"] / 1_000_000
    )
    eur = usd * USD_TO_EUR
    return usd, eur


def _cursor_file(slug: str) -> Path:
    return CACHE_DIR / slug / "token-tracker-cursor.json"


def _load_cursor(slug: str) -> dict:
    f = _cursor_file(slug)
    if not f.exists():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cursor(slug: str, cursor: dict) -> None:
    f = _cursor_file(slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cursor, indent=2), encoding="utf-8")


def _skill_log_file(slug: str) -> Path:
    return CACHE_DIR / slug / "skill-log.jsonl"


def _aggregate_path(slug: str) -> Path:
    return CACHE_DIR / slug / "token-usage.json"


def _read_skill_log(slug: str) -> list[dict]:
    f = _skill_log_file(slug)
    if not f.exists():
        return []
    entries = []
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entries.append(json.loads(line))
    except Exception:
        return []
    return entries


def _append_skill_log(slug: str, event: dict) -> None:
    f = _skill_log_file(slug)
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(event, ensure_ascii=False) + "\n")


def _resolve_skill_for_timestamp(skill_log: list[dict], ts: str) -> Optional[str]:
    """
    Findet den Skill-Namen, der zum Zeitpunkt `ts` aktiv war (zwischen start und end).
    Wenn mehrere overlap haben: nimmt das jüngste start. Wenn keiner: None (heisst:
    Tokens wurden zwischen Skill-Läufen verbraucht, z.B. User-Interaktion).
    """
    if not skill_log:
        return None
    active = None
    for e in skill_log:
        if e.get("ts", "") > ts:
            break
        if e["event"] == "start":
            active = e["skill"]
        elif e["event"] == "end" and e["skill"] == active:
            active = None
    return active


def aggregate(slug: str) -> dict:
    """Aggregiert Token-Daten für den MTA-Slug, schreibt token-usage.json lokal."""
    pdir = _project_dir_for_mta(slug)
    if pdir is None or not pdir.exists():
        return _empty_aggregate(slug, reason="no_project_dir")

    cursor = _load_cursor(slug)
    skill_log = _read_skill_log(slug)

    # Bestehendes Aggregat laden, oder leeres anlegen
    agg_path = _aggregate_path(slug)
    if agg_path.exists():
        try:
            agg = json.loads(agg_path.read_text(encoding="utf-8"))
        except Exception:
            agg = _empty_aggregate(slug)
    else:
        agg = _empty_aggregate(slug)

    new_messages = 0
    for jsonl in sorted(pdir.glob("*.jsonl")):
        last_seen_uuid = cursor.get(jsonl.name, "")
        try:
            with jsonl.open("r", encoding="utf-8") as fp:
                lines = fp.readlines()
        except Exception:
            continue

        # Finde Index des zuletzt gesehenen Messages (UUID-Match) und nimm alles danach
        start_idx = 0
        if last_seen_uuid:
            for i, line in enumerate(lines):
                try:
                    d = json.loads(line)
                    if d.get("uuid") == last_seen_uuid:
                        start_idx = i + 1
                        break
                except Exception:
                    continue

        last_uuid_in_file = last_seen_uuid
        for line in lines[start_idx:]:
            try:
                d = json.loads(line)
            except Exception:
                continue
            uuid = d.get("uuid")
            if uuid:
                last_uuid_in_file = uuid

            msg = d.get("message", {})
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue

            model = msg.get("model") or "_unknown"
            stem = _model_stem(model)
            pricing = _pricing_for(model)
            usd, eur = _cost_for_usage(usage, pricing)

            # In Gesamt + per-model + per-skill summieren
            ts = d.get("timestamp", "")
            skill = _resolve_skill_for_timestamp(skill_log, ts) or "_kein_skill_aktiv"

            for bucket_key in ("gesamt",):
                _add_to_bucket(agg[bucket_key], usage, usd, eur)
            agg["pro_modell"].setdefault(stem, _per_model_empty())
            _add_to_bucket(agg["pro_modell"][stem], usage, usd, eur)
            agg["pro_skill"].setdefault(skill, _per_model_empty())
            _add_to_bucket(agg["pro_skill"][skill], usage, usd, eur)

            new_messages += 1

        cursor[jsonl.name] = last_uuid_in_file

    agg["letzte_aktualisierung"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    agg["new_messages_seit_letztem_lauf"] = new_messages

    # Persistieren
    agg_path.parent.mkdir(parents=True, exist_ok=True)
    agg_path.write_text(json.dumps(agg, indent=2, ensure_ascii=False), encoding="utf-8")
    _save_cursor(slug, cursor)

    return agg


def _add_to_bucket(bucket: dict, usage: dict, usd: float, eur: float) -> None:
    bucket["input_tokens"] += usage.get("input_tokens", 0) or 0
    bucket["output_tokens"] += usage.get("output_tokens", 0) or 0
    bucket["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0) or 0
    cc = usage.get("cache_creation", {}) or {}
    cc_5m = cc.get("ephemeral_5m_input_tokens", 0) or 0
    cc_1h = cc.get("ephemeral_1h_input_tokens", 0) or 0
    if cc_5m + cc_1h == 0:
        cc_5m = usage.get("cache_creation_input_tokens", 0) or 0
    bucket["cache_creation_5m_tokens"] += cc_5m
    bucket["cache_creation_1h_tokens"] += cc_1h
    bucket["message_count"] += 1
    bucket["cost_usd"] += usd
    bucket["cost_eur"] += eur


def _empty_aggregate(slug: str, reason: str = "") -> dict:
    return {
        "schema_version": "1.0",
        "slug": slug,
        "letzte_aktualisierung": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "fx_usd_to_eur": USD_TO_EUR,
        "gesamt": _per_model_empty(),
        "pro_modell": {},
        "pro_skill": {},
        "reason": reason,
    }


# ---------- Rendering ----------

def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def _fmt_eur(amount: float) -> str:
    return f"{amount:.2f} €"


def _all_tokens(bucket: dict) -> int:
    return (
        bucket["input_tokens"]
        + bucket["output_tokens"]
        + bucket["cache_creation_5m_tokens"]
        + bucket["cache_creation_1h_tokens"]
        + bucket["cache_read_tokens"]
    )


def render_stat_strip(agg: dict) -> str:
    """Kompakter HTML-Block für den Dashboard-Stat-Strip."""
    g = agg["gesamt"]
    total = _all_tokens(g)
    # Synthetic / Pseudo-Modelle aus der Mix-Anzeige rausfiltern
    relevant = {k: v for k, v in agg["pro_modell"].items() if k.startswith("claude-")}
    modelle = sorted(relevant.items(), key=lambda kv: _all_tokens(kv[1]), reverse=True)
    modell_share_strs = []
    # Bezug zum echten Modell-Total (ohne synthetic)
    relevant_total = sum(_all_tokens(b) for b in relevant.values())
    for stem, bucket in modelle[:3]:
        share = _all_tokens(bucket) / relevant_total * 100 if relevant_total else 0
        if share < 1:
            continue
        short = stem.replace("claude-", "").replace("-4-7", "").replace("-4-6", "").replace("-4-5", "").title()
        modell_share_strs.append(f"{share:.0f}% {short}")
    mix = " · ".join(modell_share_strs) if modell_share_strs else "—"
    return (
        f'<div class="stat-item stat-tokens">'
        f'<span class="stat-label">Token-Verbrauch</span>'
        f'<span class="stat-value">{_fmt_tokens(total)}</span>'
        f'<span class="stat-sub">{_fmt_eur(g["cost_eur"])} · {mix}</span>'
        f'</div>'
    )


def render_breakdown(agg: dict) -> str:
    """Vollständige HTML-Sektion mit Tabellen für die Detail-Seite."""
    g = agg["gesamt"]
    total = _all_tokens(g)
    if total == 0:
        return '<section class="token-breakdown"><h2>Token-Verbrauch</h2><p>Noch keine Daten erfasst.</p></section>'

    rows_modell = []
    for stem, bucket in sorted(agg["pro_modell"].items(), key=lambda kv: _all_tokens(kv[1]), reverse=True):
        share = _all_tokens(bucket) / total * 100 if total else 0
        rows_modell.append(
            f'<tr>'
            f'<td>{stem}</td>'
            f'<td class="num">{_fmt_tokens(_all_tokens(bucket))}</td>'
            f'<td class="num">{_fmt_tokens(bucket["input_tokens"])}</td>'
            f'<td class="num">{_fmt_tokens(bucket["output_tokens"])}</td>'
            f'<td class="num">{_fmt_tokens(bucket["cache_creation_5m_tokens"] + bucket["cache_creation_1h_tokens"])}</td>'
            f'<td class="num">{_fmt_tokens(bucket["cache_read_tokens"])}</td>'
            f'<td class="num">{_fmt_eur(bucket["cost_eur"])}</td>'
            f'<td class="num">{share:.1f}%</td>'
            f'</tr>'
        )

    rows_skill = []
    for skill, bucket in sorted(agg["pro_skill"].items(), key=lambda kv: kv[1]["cost_eur"], reverse=True):
        if bucket["message_count"] == 0:
            continue
        rows_skill.append(
            f'<tr>'
            f'<td>{skill}</td>'
            f'<td class="num">{_fmt_tokens(_all_tokens(bucket))}</td>'
            f'<td class="num">{bucket["message_count"]}</td>'
            f'<td class="num">{_fmt_eur(bucket["cost_eur"])}</td>'
            f'</tr>'
        )

    return f'''<section class="token-breakdown">
  <div class="section-heading">
    <span class="label">Kosten-Tracking</span>
    <h2>Token-Verbrauch dieser MTA</h2>
  </div>
  <p class="summary-card"><strong>Gesamt:</strong> {_fmt_tokens(total)} Tokens · {_fmt_eur(g["cost_eur"])} · letzte Aktualisierung: {agg["letzte_aktualisierung"]}<br>
  <em>Schätzung auf Basis Anthropic-Pricing (Stand Mai 2026), Wechselkurs USD→EUR: {USD_TO_EUR:.3f}</em></p>

  <h3>Aufschlüsselung nach Modell</h3>
  <table class="data">
    <thead><tr><th>Modell</th><th>Tokens</th><th>Input</th><th>Output</th><th>Cache-Write</th><th>Cache-Read</th><th>Kosten</th><th>Anteil</th></tr></thead>
    <tbody>{"".join(rows_modell)}</tbody>
  </table>

  <h3>Aufschlüsselung nach Skill</h3>
  <table class="data">
    <thead><tr><th>Skill</th><th>Tokens</th><th>Messages</th><th>Kosten</th></tr></thead>
    <tbody>{"".join(rows_skill)}</tbody>
  </table>
</section>'''


def render_skill_counter(agg: dict, skill: str) -> str:
    """Footer-Block für einen Skill-spezifischen HTML-Report."""
    bucket = agg["pro_skill"].get(skill)
    if not bucket or bucket["message_count"] == 0:
        return ''
    total = _all_tokens(bucket)
    return (
        f'<aside class="token-footer">'
        f'<strong>Dieser Skill:</strong> '
        f'{_fmt_tokens(total)} Tokens · '
        f'{bucket["message_count"]} Messages · '
        f'~{_fmt_eur(bucket["cost_eur"])}'
        f'</aside>'
    )


def render_markdown(agg: dict) -> str:
    """Markdown-Version für status.md o.ä."""
    g = agg["gesamt"]
    total = _all_tokens(g)
    lines = [
        f"## Token-Verbrauch",
        f"",
        f"- **Gesamt:** {_fmt_tokens(total)} Tokens · {_fmt_eur(g['cost_eur'])}",
        f"- **Letzte Aktualisierung:** {agg['letzte_aktualisierung']}",
        f"",
        f"### Pro Modell",
        f"",
        f"| Modell | Tokens | Kosten |",
        f"|---|---:|---:|",
    ]
    for stem, b in sorted(agg["pro_modell"].items(), key=lambda kv: _all_tokens(kv[1]), reverse=True):
        lines.append(f"| {stem} | {_fmt_tokens(_all_tokens(b))} | {_fmt_eur(b['cost_eur'])} |")
    return "\n".join(lines)


# ---------- Skill-Log ----------

def mark_skill_start(slug: str, skill: str) -> None:
    _append_skill_log(slug, {
        "event": "start",
        "skill": skill,
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    })


def mark_skill_end(slug: str, skill: str) -> None:
    _append_skill_log(slug, {
        "event": "end",
        "skill": skill,
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    })


# ---------- CLI ----------

def _load_aggregate(slug: str) -> dict:
    f = _aggregate_path(slug)
    if not f.exists():
        return _empty_aggregate(slug, reason="not_yet_aggregated")
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return _empty_aggregate(slug, reason="parse_error")


def _cli() -> None:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(0)
    cmd = sys.argv[1]
    args = sys.argv[2:]

    try:
        if cmd == "tick":
            # Default-Modus für Stop-Hook: silent ermitteln, was aktiv ist
            slug = _most_recent_active_mta_slug()
            if not slug:
                sys.exit(0)
            aggregate(slug)
            sys.exit(0)
        elif cmd == "tick-and-print-slug":
            # Wie tick, aber gibt den Slug auf stdout aus (für Hook-Skript)
            slug = _most_recent_active_mta_slug()
            if not slug:
                sys.exit(0)
            aggregate(slug)
            print(slug)
            sys.exit(0)
        elif cmd == "aggregate":
            slug = args[0]
            agg = aggregate(slug)
            print(json.dumps(agg, indent=2, ensure_ascii=False))
        elif cmd == "render-counter":
            slug = args[0]
            style = "stat-strip"
            if "--style" in args:
                i = args.index("--style")
                style = args[i + 1] if i + 1 < len(args) else "stat-strip"
            agg = _load_aggregate(slug)
            if style == "stat-strip":
                print(render_stat_strip(agg))
            elif style == "breakdown":
                print(render_breakdown(agg))
            elif style == "md":
                print(render_markdown(agg))
            else:
                print(f"Unbekannter Style: {style}", file=sys.stderr)
                sys.exit(1)
        elif cmd == "render-skill-counter":
            slug, skill = args[0], args[1]
            agg = _load_aggregate(slug)
            print(render_skill_counter(agg, skill))
        elif cmd == "mark-skill-start":
            slug, skill = args[0], args[1]
            mark_skill_start(slug, skill)
            print("marked")
        elif cmd == "mark-skill-end":
            slug, skill = args[0], args[1]
            mark_skill_end(slug, skill)
            print("marked")
        else:
            print(f"Unbekanntes Kommando: {cmd}", file=sys.stderr)
            sys.exit(1)
    except IndexError:
        print(f"Fehlende Argumente für '{cmd}'.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Stop-Hook soll NIEMALS Session blockieren
        print(f"Token-Tracker-Fehler: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    _cli()
