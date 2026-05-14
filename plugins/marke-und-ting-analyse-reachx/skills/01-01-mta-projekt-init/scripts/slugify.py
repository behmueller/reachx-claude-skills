#!/usr/bin/env python3
"""
Slug-Erzeugung für MTA-Projekte.

Nutzung:
    python slugify.py "Müller Hausverwaltung GmbH"        # → mueller-hausverwaltung-gmbh
    python slugify.py "Müller Hausverwaltung GmbH" --mta  # → mta-mueller-hausverwaltung-gmbh-YYYY-MM (aktueller Monat)
    python slugify.py "Müller GmbH" --mta --month 2026-05 # → mta-mueller-gmbh-2026-05

Aufruf aus Python:
    from slugify import slugify, projekt_slug
    s = slugify("Müller Hausverwaltung GmbH")           # "mueller-hausverwaltung-gmbh"
    p = projekt_slug("Müller Hausverwaltung GmbH")      # "mta-mueller-hausverwaltung-gmbh-2026-05"
"""

import argparse
import re
import sys
from datetime import datetime, timezone


UMLAUT_MAP = {
    "ä": "ae", "ö": "oe", "ü": "ue",
    "Ä": "ae", "Ö": "oe", "Ü": "ue",
    "ß": "ss",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "á": "a", "à": "a", "â": "a", "ã": "a",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o",
    "ú": "u", "ù": "u", "û": "u",
    "ç": "c", "ñ": "n",
    "&": "und",
    "@": "at",
}


def slugify(name: str) -> str:
    """
    Erzeugt einen sauberen Slug aus einem Klartext-Namen.

    Regeln:
    - Umlaute und Akzente werden ersetzt (ä→ae, é→e, ß→ss)
    - & wird zu 'und'
    - Alles in Kleinbuchstaben
    - Alles außer [a-z0-9-] wird zu Bindestrich
    - Doppelte Bindestriche werden kollabiert
    - Führende/abschließende Bindestriche werden entfernt
    """
    if not name or not name.strip():
        raise ValueError("Slugify: Eingabe ist leer")

    s = name
    for src, dst in UMLAUT_MAP.items():
        s = s.replace(src, dst)
    s = s.lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")

    if not s:
        raise ValueError(f"Slugify: Eingabe '{name}' ergibt leeren Slug nach Bereinigung")

    return s


def projekt_slug(name: str, month: str | None = None) -> str:
    """
    Erzeugt den vollständigen MTA-Projekt-Slug: mta-<kunden-slug>-<YYYY-MM>.

    month: optionaler ISO-Monat (z. B. '2026-05'). Wenn nicht angegeben,
           wird der aktuelle Monat in UTC verwendet.
    """
    if month is None:
        month = datetime.now(timezone.utc).strftime("%Y-%m")
    elif not re.match(r"^\d{4}-\d{2}$", month):
        raise ValueError(f"Monat muss im Format YYYY-MM sein, war: '{month}'")

    return f"mta-{slugify(name)}-{month}"


def main() -> int:
    parser = argparse.ArgumentParser(description="MTA-Slug-Erzeugung aus Kundennamen.")
    parser.add_argument("name", help="Kundenname (in Anführungszeichen)")
    parser.add_argument("--mta", action="store_true",
                        help="Vollständigen MTA-Projekt-Slug erzeugen (mta-<slug>-<YYYY-MM>)")
    parser.add_argument("--month", default=None,
                        help="Monat als YYYY-MM (Default: aktueller Monat in UTC)")
    args = parser.parse_args()

    try:
        if args.mta:
            print(projekt_slug(args.name, args.month))
        else:
            print(slugify(args.name))
    except ValueError as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
