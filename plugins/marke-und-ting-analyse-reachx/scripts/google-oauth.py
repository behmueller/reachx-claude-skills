#!/usr/bin/env python3
"""
REACHX MTA-Skills — Google-OAuth-Helper

Erzeugt den refresh_token fuer den Zugriff auf die Google-APIs. Ads und Analytics
werden GETRENNT eingerichtet — so kann jeder Service mit dem Google-Account laufen,
der dort tatsaechlich Zugriff hat (z.B. MCC-Account fuer Ads, GA4-Vollzugriffs-
Account fuer Analytics). Pro Service einmal ausfuehren.

  --service ads        Scope adwords            -> ~/.config/reachx-mta/google-ads.yaml
  --service analytics  Scope analytics.readonly -> ~/.config/reachx-mta/google-analytics.yaml

Wer das Script ausfuehrt, muss im Browser mit dem Account eingeloggt sein, der fuer
den gewaehlten Service Zugriff hat. Der refresh_token gehoert zu diesem Account —
einmal generiert, dann ueber den Passwort-Manager verteilt.

OAuth-Client: Ein Desktop-OAuth-Client wird gebraucht — derselbe fuer beide Services
(der Client ist weder account- noch scope-gebunden). Der bestehende gws-CLI-Client
kann wiederverwendet werden.

WICHTIG — Token-Ablauf: Steht der OAuth-Zustimmungsbildschirm auf "Testing", laeuft
der refresh_token nach 7 Tagen ab. Bei einer Google-Workspace-Org auf "Intern"
stellen — dann ist der Token dauerhaft.

CLI:
    # Analytics — im Browser mit dem GA4-Vollzugriffs-Account einloggen:
    python3 google-oauth.py --service analytics \\
        --client-secrets ~/.config/gws/client_secret.json --write

    # Ads — im Browser mit dem MCC-Account einloggen:
    python3 google-oauth.py --service ads \\
        --client-secrets ~/.config/gws/client_secret.json \\
        --developer-token <token> --login-customer-id <mcc-id> --write

    # client_id/secret direkt statt client_secret.json:
    python3 google-oauth.py --service ads --client-id <id> --client-secret <secret> ...

    --write   schreibt die fertige Datei nach ~/.config/reachx-mta/ (chmod 600)
"""
from __future__ import annotations

import argparse
import os
import stat
import sys
from pathlib import Path

CONFIG_DIR = Path(
    os.environ.get(
        "REACHX_GOOGLE_CONFIG_DIR",
        str(Path.home() / ".config" / "reachx-mta"),
    )
)

# Pro Service: eigener OAuth-Scope und eigene Ziel-Datei.
SCOPES = {
    "ads": ["https://www.googleapis.com/auth/adwords"],
    "analytics": ["https://www.googleapis.com/auth/analytics.readonly"],
}
CONFIG_FILE = {
    "ads": "google-ads.yaml",
    "analytics": "google-analytics.yaml",
}


def _build_flow(client_id, client_secret, client_secrets_path, scopes):
    """Baut den InstalledAppFlow aus client_secret.json oder client_id/secret."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        sys.exit(
            "Library fehlt. Installieren mit:\n"
            "  pip3 install -r requirements-google.txt"
        )
    if client_secrets_path:
        return InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=scopes)
    config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return InstalledAppFlow.from_client_config(config, scopes=scopes)


def _yaml_block(service: str, creds, developer_token: str, login_customer_id: str) -> str:
    """Baut den YAML-Inhalt der Credential-Datei je nach Service."""
    if service == "ads":
        return (
            "# Google-Ads-Credentials fuer google-ads.py — erzeugt mit\n"
            "# google-oauth.py --service ads. Account mit MCC-Zugriff.\n"
            f'developer_token: "{developer_token}"\n'
            f'client_id: "{creds.client_id}"\n'
            f'client_secret: "{creds.client_secret}"\n'
            f'refresh_token: "{creds.refresh_token}"\n'
            f'login_customer_id: "{login_customer_id}"\n'
            "use_proto_plus: True\n"
        )
    return (
        "# GA4-Credentials fuer google-analytics.py — erzeugt mit\n"
        "# google-oauth.py --service analytics. Account mit GA4-Zugriff.\n"
        f'client_id: "{creds.client_id}"\n'
        f'client_secret: "{creds.client_secret}"\n'
        f'refresh_token: "{creds.refresh_token}"\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Google refresh_token pro Service erzeugen.")
    parser.add_argument("--service", required=True, choices=["ads", "analytics"],
                        help="ads -> google-ads.yaml | analytics -> google-analytics.yaml")
    parser.add_argument("--client-secrets", help="Pfad zur client_secret.json")
    parser.add_argument("--client-id", help="OAuth-Client-ID")
    parser.add_argument("--client-secret", help="OAuth-Client-Secret")
    parser.add_argument("--developer-token", default="DEIN_DEVELOPER_TOKEN",
                        help="nur fuer --service ads")
    parser.add_argument("--login-customer-id", default="DEINE_MCC_ID",
                        help="nur fuer --service ads")
    parser.add_argument("--write", action="store_true",
                        help="Datei direkt nach ~/.config/reachx-mta/ schreiben (chmod 600)")
    args = parser.parse_args()

    if not args.client_secrets and not (args.client_id and args.client_secret):
        parser.error("Entweder --client-secrets ODER --client-id + --client-secret angeben.")

    scopes = SCOPES[args.service]
    flow = _build_flow(args.client_id, args.client_secret, args.client_secrets, scopes)

    print(f"→ Browser oeffnet sich. Mit einem Account einloggen, der "
          f"{args.service.upper()}-Zugriff hat.", file=sys.stderr)
    # access_type=offline + prompt=consent erzwingen die Ausgabe eines refresh_token.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    if not creds.refresh_token:
        sys.exit("✗ Kein refresh_token erhalten. Zustimmungsbildschirm pruefen "
                 "und Flow mit prompt=consent erneut ausfuehren.")

    block = _yaml_block(args.service, creds, args.developer_token, args.login_customer_id)
    target = CONFIG_DIR / CONFIG_FILE[args.service]

    if args.write:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        target.write_text(block, encoding="utf-8")
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
        print(f"✓ Geschrieben nach {target} (chmod 600)", file=sys.stderr)
        if args.service == "ads" and "DEIN" in block:
            print("  Noch ergaenzen: developer_token und/oder login_customer_id.",
                  file=sys.stderr)
    else:
        print(f"\n# --- {CONFIG_FILE[args.service]} ---")
        print(block, end="")
        print(f"# Ablegen unter {target}, dann: chmod 600", file=sys.stderr)


if __name__ == "__main__":
    main()
