#!/usr/bin/env python3
"""
REACHX MTA-Skills — Google-OAuth-Helper (Ads + Analytics)

Einmalig auszufuehren: erzeugt EINEN refresh_token, der sowohl die Google Ads
API als auch die GA4-APIs (Data + Admin) abdeckt. Schreibt das Ergebnis nach
~/.config/reachx-mta/google-credentials.yaml — die geteilte Credential-Datei
fuer google-ads.py und google-analytics.py.

Der refresh_token gehoert zum zentralen REACHX-Setup — einmal generiert, dann
ueber den Passwort-Manager verteilt. Wer das Script ausfuehrt, muss im Browser
mit einem Google-Account eingeloggt sein, der Zugriff auf das MCC und die
GA4-Properties hat.

OAuth-Client: Ein OAuth-Client vom Typ "Desktop-App" wird gebraucht. Ein
BESTEHENDER Desktop-Client kann wiederverwendet werden (z.B. der fuer die
gws CLI) — der Client selbst ist nicht scope-gebunden. Voraussetzung ist nur,
dass im selben Cloud-Projekt die Google Ads API UND die Google Analytics Data
API + Admin API aktiviert sind.

WICHTIG — Token-Ablauf: Steht der OAuth-Zustimmungsbildschirm ("Zielgruppe")
auf "Testing", laeuft der refresh_token nach 7 Tagen ab. Bei einer Google-
Workspace-Org auf "Intern" stellen — dann ist der Token dauerhaft und die
sensiblen Scopes (adwords, analytics) brauchen keine Google-Verifizierung.

CLI:
    # Variante A — client_secret.json aus der Cloud Console herunterladen:
    python3 google-oauth.py --client-secrets ~/Downloads/client_secret.json

    # Variante B — client_id/secret direkt (z.B. vom wiederverwendeten Client):
    python3 google-oauth.py --client-id <id> --client-secret <secret>

Optional fuer einen komplett ausgefuellten YAML-Block bzw. direktes Schreiben:
    --developer-token <token>   --login-customer-id <mcc-id>   (nur fuer Ads)
    --write    schreibt die fertige Datei nach ~/.config/reachx-mta/
"""
from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

# Beide Scopes — ein refresh_token deckt damit Ads UND GA4 ab.
SCOPES = [
    "https://www.googleapis.com/auth/adwords",             # Google Ads API
    "https://www.googleapis.com/auth/analytics.readonly",  # GA4 Data + Admin API
]

CONFIG_PATH = Path(
    os.environ.get(
        "REACHX_GOOGLE_CREDENTIALS",
        str(Path.home() / ".config" / "reachx-mta" / "google-credentials.yaml"),
    )
)


def _build_flow(client_id: str | None, client_secret: str | None,
                client_secrets_path: str | None):
    """Baut den InstalledAppFlow aus client_secret.json oder id/secret."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        sys.exit(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-google.txt"
        )
    if client_secrets_path:
        return InstalledAppFlow.from_client_secrets_file(
            client_secrets_path, scopes=SCOPES
        )
    config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return InstalledAppFlow.from_client_config(config, scopes=SCOPES)


def main() -> None:
    parser = argparse.ArgumentParser(description="Google refresh_token erzeugen (Ads + GA4).")
    parser.add_argument("--client-secrets", help="Pfad zur client_secret.json")
    parser.add_argument("--client-id", help="OAuth-Client-ID")
    parser.add_argument("--client-secret", help="OAuth-Client-Secret")
    parser.add_argument("--developer-token", default="DEIN_DEVELOPER_TOKEN")
    parser.add_argument("--login-customer-id", default="DEINE_MCC_ID")
    parser.add_argument("--write", action="store_true",
                        help="Datei direkt nach ~/.config/reachx-mta/ schreiben (chmod 600)")
    args = parser.parse_args()

    if not args.client_secrets and not (args.client_id and args.client_secret):
        parser.error("Entweder --client-secrets ODER --client-id + --client-secret angeben.")

    flow = _build_flow(args.client_id, args.client_secret, args.client_secrets)

    # access_type=offline + prompt=consent erzwingen die Ausgabe eines
    # refresh_token — auch bei wiederholter Autorisierung.
    print("→ Browser oeffnet sich. Mit einem Account einloggen, der Zugriff "
          "auf MCC und GA4-Properties hat.", file=sys.stderr)
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        sys.exit("✗ Kein refresh_token erhalten. Zustimmungsbildschirm pruefen "
                 "und Flow mit prompt=consent erneut ausfuehren.")

    yaml_block = (
        f'# Geteilte Credentials fuer google-ads.py und google-analytics.py.\n'
        f'# Der refresh_token deckt die Scopes adwords + analytics.readonly ab.\n'
        f'developer_token: "{args.developer_token}"   # nur fuer google-ads.py\n'
        f'client_id: "{creds.client_id}"\n'
        f'client_secret: "{creds.client_secret}"\n'
        f'refresh_token: "{creds.refresh_token}"\n'
        f'login_customer_id: "{args.login_customer_id}"   # nur fuer google-ads.py\n'
        f"use_proto_plus: True\n"
    )

    if args.write:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(yaml_block, encoding="utf-8")
        CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
        print(f"✓ Geschrieben nach {CONFIG_PATH} (chmod 600)", file=sys.stderr)
        if "DEIN" in yaml_block:
            print("  Noch ergaenzen: developer_token und/oder login_customer_id "
                  "(nur fuer Google Ads noetig).", file=sys.stderr)
    else:
        print("\n# --- google-credentials.yaml ---")
        print(yaml_block, end="")
        print("# Ablegen unter ~/.config/reachx-mta/google-credentials.yaml, "
              "dann: chmod 600", file=sys.stderr)


if __name__ == "__main__":
    main()
