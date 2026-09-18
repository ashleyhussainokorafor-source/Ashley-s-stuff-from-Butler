#!/usr/bin/env python3
"""YouTube OAuth helper — generate auth URL or exchange code.

Scopes: youtube.force-ssl (manage own channel / update video descriptions).
Saves token to /data/youtube_token.json (separate from the Gmail token).

Usage:
  python3 yt_oauth.py --url            # print the URL, stash PKCE state
  python3 yt_oauth.py --code "<code>"  # exchange and save token
"""
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

CLIENT_SECRET = "/data/google_client_secret.json"
TOKEN_PATH = "/data/youtube_token.json"
PENDING = "/data/youtube_pending.json"
REDIRECT_URI = "http://localhost:1"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def do_url():
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET, scopes=SCOPES, redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=True,
    )
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
    with open(PENDING, "w") as f:
        json.dump({
            "state": state,
            "code_verifier": flow.code_verifier,
            "redirect_uri": REDIRECT_URI,
        }, f, indent=2)
    print(auth_url)


def do_code(code):
    from google_auth_oauthlib.flow import Flow
    if not os.path.exists(PENDING):
        sys.exit("ERROR: No pending OAuth session. Run --url first.")
    pending = json.load(open(PENDING))

    # accept raw code or full redirect URL
    if code.startswith("http"):
        params = parse_qs(urlparse(code).query)
        code = params["code"][0]

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET, scopes=SCOPES,
        redirect_uri=pending.get("redirect_uri", REDIRECT_URI),
        state=pending["state"],
        code_verifier=pending["code_verifier"],
    )
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
    flow.fetch_token(code=code)

    creds = flow.credentials
    token = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }
    with open(TOKEN_PATH, "w") as f:
        json.dump(token, f, indent=2)
    os.remove(PENDING)
    print(f"OK: YouTube token saved to {TOKEN_PATH}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--url":
        do_url()
    elif len(sys.argv) >= 3 and sys.argv[1] == "--code":
        do_code(sys.argv[2])
    else:
        sys.exit("usage: yt_oauth.py --url | --code <code>")
