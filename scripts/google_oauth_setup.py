"""One-time script to obtain a Google OAuth refresh token for Calendar access.

Usage:
    1. In Google Cloud Console, create OAuth 2.0 credentials (Desktop app type).
    2. Download the JSON, save as client_secret.json in repo root.
    3. Run: python scripts/google_oauth_setup.py
    4. Authorize in browser, then copy the printed refresh token into k8s secrets
       as GOOGLE_REFRESH_TOKEN (alongside GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET).
"""
import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def main() -> int:
    client_secret_path = Path("client_secret.json")
    if not client_secret_path.exists():
        print("ERROR: client_secret.json not found in current directory.", file=sys.stderr)
        print("Download it from Google Cloud Console → APIs & Services → Credentials.", file=sys.stderr)
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    with client_secret_path.open() as f:
        secret = json.load(f)
    block = secret.get("installed") or secret.get("web") or {}

    print("\n" + "=" * 60)
    print("SUCCESS — save these as k8s secrets:")
    print("=" * 60)
    print(f"GOOGLE_CLIENT_ID={block.get('client_id', '')}")
    print(f"GOOGLE_CLIENT_SECRET={block.get('client_secret', '')}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
