#!/usr/bin/env python3
"""validate-report.py — Qualitätskontrolle für MTA-HTML-Reports.

Prüft einen fertig gerenderten HTML-Report gegen drei Regeln:

  1. KLASSEN-VERTRAG  — jede im Report verwendete CSS-Klasse ist im
     <style>-Block desselben Dokuments definiert. Schlägt eine Klasse fehl,
     rendert sie ungestylt (der häufigste Report-Bug).
  2. PLATZHALTER      — keine offenen {{PLATZHALTER}} mehr im Dokument.
  3. SHELL-INTEGRITÄT — (optional, --shell) der <style>-Block ist
     byte-identisch mit dem kanonischen report-shell.html. Fängt den Fall,
     dass das CSS umgebaut oder aus dem Gedächtnis rekonstruiert wurde.

Exit-Code 0 = sauber, 1 = mindestens ein Fehler, 2 = Aufruf-/Datei-Fehler.

Aufruf:
  validate-report.py <report.html>              # Regeln 1 + 2
  validate-report.py <report.html> --shell       # zusätzlich Regel 3 (Default-Shell)
  validate-report.py <report.html> --shell <pfad-zu-shell.html>

Reine Standard-Bibliothek, keine Abhängigkeiten.
"""

import argparse
import re
import sys
from pathlib import Path

# Kanonisches Shell-Template, relativ zu diesem Skript.
DEFAULT_SHELL = (
    Path(__file__).resolve().parent.parent
    / "skills" / "01-01-mta-projekt-init" / "reference" / "report-shell.html"
)

STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# CSS-Klassen-Selektor: Punkt + Name, der mit Buchstabe/Unterstrich beginnt.
# Numerische Werte (0.5rem, 1.5rem) starten mit Ziffer und matchen nicht.
CSS_CLASS_RE = re.compile(r"\.([A-Za-z_][\w-]*)")
# class="a b c" / class='a b c'
CLASS_ATTR_RE = re.compile(r"""class\s*=\s*["']([^"']*)["']""", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\{\{\s*[A-Za-z0-9_]+\s*\}\}")


def extract_style_block(html: str):
    """Gibt (roh, normalisiert) des ersten <style>-Blocks zurück, sonst (None, None)."""
    m = STYLE_RE.search(html)
    if not m:
        return None, None
    return m.group(0), m.group(1)


def defined_classes(style_body: str) -> set:
    """Alle im CSS definierten Klassen-Namen."""
    no_comments = COMMENT_RE.sub("", style_body)
    return set(CSS_CLASS_RE.findall(no_comments))


def used_classes(html: str) -> set:
    """Alle in class="…"-Attributen verwendeten Klassen-Namen.

    HTML-Kommentare werden ignoriert — sie rendern nicht, ihre Klassen
    (z. B. die Klassen-Doku im Shell) sind keine echte Verwendung.
    """
    visible = HTML_COMMENT_RE.sub("", html)
    used = set()
    for group in CLASS_ATTR_RE.findall(visible):
        used.update(tok for tok in group.split() if tok)
    return used


def main() -> int:
    parser = argparse.ArgumentParser(description="MTA-HTML-Report validieren.")
    parser.add_argument("report", help="Pfad zum gerenderten HTML-Report")
    parser.add_argument(
        "--shell",
        nargs="?",
        const=str(DEFAULT_SHELL),
        default=None,
        metavar="PFAD",
        help="zusätzlich CSS-Block byte-genau gegen report-shell.html prüfen "
        "(ohne Pfad: kanonische Shell)",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.is_file():
        print(f"FEHLER: Datei nicht gefunden: {report_path}", file=sys.stderr)
        return 2

    html = report_path.read_text(encoding="utf-8", errors="replace")
    errors = []
    warnings = []

    # --- Regel 1: Klassen-Vertrag ------------------------------------------
    style_raw, style_body = extract_style_block(html)
    if style_body is None:
        errors.append("Kein <style>-Block gefunden — der Report hat kein CSS.")
        defined = set()
    else:
        defined = defined_classes(style_body)

    used = used_classes(html)
    undefined = sorted(used - defined)
    if undefined:
        errors.append(
            "Verwendete CSS-Klassen ohne Definition im <style>-Block "
            f"(rendern ungestylt): {', '.join(undefined)}"
        )

    # --- Regel 2: Platzhalter ----------------------------------------------
    placeholders = sorted(set(PLACEHOLDER_RE.findall(html)))
    if placeholders:
        errors.append(
            f"Nicht ersetzte Platzhalter: {', '.join(placeholders)}"
        )

    # --- Regel 3: Shell-Integrität (optional) ------------------------------
    if args.shell is not None:
        shell_path = Path(args.shell)
        if not shell_path.is_file():
            errors.append(f"Shell-Referenz nicht gefunden: {shell_path}")
        elif style_raw is None:
            pass  # bereits als Fehler erfasst
        else:
            shell_html = shell_path.read_text(encoding="utf-8", errors="replace")
            shell_style_raw, _ = extract_style_block(shell_html)
            if shell_style_raw is None:
                errors.append(f"Shell-Referenz hat keinen <style>-Block: {shell_path}")
            elif style_raw != shell_style_raw:
                errors.append(
                    "CSS-Block weicht vom kanonischen report-shell.html ab — "
                    "die Shell darf nicht umgebaut werden. "
                    f"Referenz: {shell_path}"
                )

    # --- Hinweise (kein harter Fehler) -------------------------------------
    if re.search(r"""\sstyle\s*=\s*["']""", html, re.IGNORECASE):
        warnings.append(
            "inline style=\"…\"-Attribute gefunden — Styling gehört ins "
            "Shell-CSS, nicht in den Report-Inhalt."
        )

    # --- Ausgabe -----------------------------------------------------------
    name = report_path.name
    if errors:
        print(f"✗ {name} — {len(errors)} Fehler:")
        for e in errors:
            print(f"  • {e}")
        for w in warnings:
            print(f"  ⚠ {w}")
        print()
        print("Report nicht ausliefern. Markup gegen report-bausteine.md prüfen, "
              "korrigieren, erneut validieren.")
        return 1

    print(f"✓ {name} — sauber ({len(used)} Klassen verwendet, alle definiert).")
    for w in warnings:
        print(f"  ⚠ {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
