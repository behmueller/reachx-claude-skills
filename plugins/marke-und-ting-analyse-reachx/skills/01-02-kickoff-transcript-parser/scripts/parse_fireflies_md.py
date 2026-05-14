#!/usr/bin/env python3
"""
Parser für Fireflies-Markdown-Transkripte.

Fireflies und Gemini-via-Google-Meet exportieren in einem konsistenten Format:

    # Meeting-Titel

    **Meeting Date:** 18th Mar, 2026 - 4:15 PM

    ---

    **Speaker Name** *[MM:SS]*: Text
    **Speaker Name** *[HH:MM:SS]*: Text mit
    Zeilenumbruch im Text
    ...

Der Parser zerlegt das in:
- Meta (titel, datum, sprecher-liste, dauer, wortanzahl)
- Turns (liste von Speaker-Turns mit timestamp und text)

Nutzung:
    python parse_fireflies_md.py <pfad-zur-transkript-md>           # Pretty-Print
    python parse_fireflies_md.py <pfad-zur-transkript-md> --json    # JSON-Output
    python parse_fireflies_md.py <pfad-zur-transkript-md> --stats   # Nur Meta-Statistik

Aufruf aus Python:
    from parse_fireflies_md import parse_transcript
    meta, turns = parse_transcript(text)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# Regex für eine Turn-Zeile:
# **Name** *[MM:SS]*: Text  ODER  **Name** *[HH:MM:SS]*: Text
TURN_PATTERN = re.compile(
    r"^\*\*(?P<speaker>[^*]+)\*\*\s+\*\[(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\]\*:\s*(?P<text>.*)$"
)

# Header-Felder
TITLE_PATTERN = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)
DATE_PATTERN = re.compile(
    r"\*\*Meeting Date:\*\*\s*(?P<date>[^\n]+?)\s*$", re.MULTILINE
)


@dataclass
class Turn:
    """Einzelne Sprecher-Äußerung im Transkript."""
    speaker: str
    timestamp: str
    timestamp_seconds: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TranscriptMeta:
    """Meta-Daten des gesamten Transkripts."""
    titel: Optional[str] = None
    datum_raw: Optional[str] = None
    datum_iso: Optional[str] = None
    sprecher: list[str] = field(default_factory=list)
    sprecher_turn_counts: dict[str, int] = field(default_factory=dict)
    sprecher_wortcounts: dict[str, int] = field(default_factory=dict)
    anzahl_turns: int = 0
    anzahl_woerter: int = 0
    dauer_geschaetzt: Optional[str] = None
    quelle_datei: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_timestamp_to_seconds(ts: str) -> int:
    """Wandelt MM:SS oder HH:MM:SS in Sekunden um."""
    parts = ts.split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        raise ValueError(f"Ungültiger Timestamp: {ts}")


def _parse_fireflies_date(date_str: str) -> Optional[str]:
    """
    Versucht das Fireflies-Datum (z.B. '18th Mar, 2026 - 4:15 PM') in ISO-Format zu wandeln.
    Gibt None zurück, wenn das Parsing scheitert.
    """
    # Entferne ordinale Suffixe: '18th' -> '18', '1st' -> '1', '22nd' -> '22'
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)
    # Versuche verschiedene Formate
    for fmt in (
        "%d %b, %Y - %I:%M %p",
        "%d %b %Y - %I:%M %p",
        "%d %b, %Y",
        "%d %B, %Y - %I:%M %p",
        "%d %B %Y - %I:%M %p",
    ):
        try:
            dt = datetime.strptime(cleaned.strip(), fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:00")
        except ValueError:
            continue
    return None


def parse_transcript(text: str, source_path: str | None = None) -> tuple[TranscriptMeta, list[Turn]]:
    """
    Parst einen Fireflies-Markdown-Text.

    Returns (TranscriptMeta, list[Turn]).
    Tolerant: gibt zurück, was er findet, auch wenn Header fehlt oder Turns
    unterbrochene Zeilen haben.
    """
    meta = TranscriptMeta()
    if source_path:
        meta.quelle_datei = source_path

    # Header parsen
    title_match = TITLE_PATTERN.search(text)
    if title_match:
        meta.titel = title_match.group("title").strip()

    date_match = DATE_PATTERN.search(text)
    if date_match:
        meta.datum_raw = date_match.group("date").strip()
        iso = _parse_fireflies_date(meta.datum_raw)
        if iso:
            meta.datum_iso = iso

    # Turns parsen — Multi-Line: Text kann sich über mehrere Zeilen erstrecken,
    # bis der nächste Turn-Header kommt oder das Dokument endet.
    lines = text.splitlines()
    turns: list[Turn] = []
    current_turn: Optional[Turn] = None
    current_text_parts: list[str] = []

    def _flush_current() -> None:
        nonlocal current_turn, current_text_parts
        if current_turn is not None:
            current_turn.text = " ".join(part.strip() for part in current_text_parts if part.strip())
            turns.append(current_turn)
            current_turn = None
            current_text_parts = []

    for line in lines:
        match = TURN_PATTERN.match(line)
        if match:
            # Vorherigen Turn abschließen
            _flush_current()
            ts = match.group("timestamp")
            try:
                ts_seconds = _parse_timestamp_to_seconds(ts)
            except ValueError:
                ts_seconds = -1
            current_turn = Turn(
                speaker=match.group("speaker").strip(),
                timestamp=ts,
                timestamp_seconds=ts_seconds,
                text="",
            )
            initial_text = match.group("text").rstrip()
            if initial_text:
                current_text_parts.append(initial_text)
        elif current_turn is not None:
            # Fortsetzungs-Zeile des aktuellen Turns
            # Ignoriere reine Trennlinien und leere Header-Zeilen
            if line.strip() in {"---", ""}:
                # Leere Zeile innerhalb eines Turns: Trennzeichen, kein Inhalt
                continue
            current_text_parts.append(line)

    _flush_current()

    # Meta-Statistik anreichern
    if turns:
        meta.anzahl_turns = len(turns)
        meta.sprecher = sorted({t.speaker for t in turns})
        meta.sprecher_turn_counts = dict(Counter(t.speaker for t in turns))
        meta.sprecher_wortcounts = {
            speaker: sum(len(t.text.split()) for t in turns if t.speaker == speaker)
            for speaker in meta.sprecher
        }
        meta.anzahl_woerter = sum(meta.sprecher_wortcounts.values())

        # Dauer = letzter Timestamp
        last_seconds = max((t.timestamp_seconds for t in turns if t.timestamp_seconds >= 0), default=0)
        if last_seconds > 0:
            h, rem = divmod(last_seconds, 3600)
            m, s = divmod(rem, 60)
            meta.dauer_geschaetzt = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    return meta, turns


def turns_to_dict_list(turns: list[Turn]) -> list[dict]:
    return [t.to_dict() for t in turns]


def main() -> int:
    parser = argparse.ArgumentParser(description="Fireflies-Markdown-Parser für MTA-Transkripte.")
    parser.add_argument("pfad", help="Pfad zur Transkript-Markdown-Datei")
    parser.add_argument("--json", action="store_true", help="Ausgabe als JSON (Meta + Turns)")
    parser.add_argument("--stats", action="store_true", help="Nur Meta-Statistik ausgeben")
    args = parser.parse_args()

    path = Path(args.pfad)
    if not path.exists():
        print(f"Fehler: Datei nicht gefunden: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    meta, turns = parse_transcript(text, source_path=str(path))

    if args.json:
        payload = {"meta": meta.to_dict(), "turns": turns_to_dict_list(turns)}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    # Pretty-Print
    print(f"📄 {meta.titel or '(kein Titel gefunden)'}")
    print(f"   Datum: {meta.datum_raw or '(unbekannt)'}")
    if meta.datum_iso:
        print(f"   ISO:   {meta.datum_iso}")
    print(f"   Dauer: {meta.dauer_geschaetzt or '(unbekannt)'}")
    print(f"   Quelle: {meta.quelle_datei}")
    print()
    print(f"📊 {meta.anzahl_turns} Turns · {meta.anzahl_woerter} Wörter · {len(meta.sprecher)} Sprecher")
    print()
    print("Sprecher-Verteilung:")
    for speaker in sorted(meta.sprecher,
                          key=lambda s: meta.sprecher_wortcounts.get(s, 0),
                          reverse=True):
        n_turns = meta.sprecher_turn_counts.get(speaker, 0)
        n_words = meta.sprecher_wortcounts.get(speaker, 0)
        share = (n_words / meta.anzahl_woerter * 100) if meta.anzahl_woerter else 0
        print(f"  - {speaker:30s}  {n_turns:4d} Turns  {n_words:6d} Wörter  ({share:5.1f}%)")

    if not args.stats:
        print()
        print("Erste 5 Turns (Vorschau):")
        for t in turns[:5]:
            preview = t.text[:120] + ("…" if len(t.text) > 120 else "")
            print(f"  [{t.timestamp}] {t.speaker}: {preview}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
