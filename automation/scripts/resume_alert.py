#!/usr/bin/env python3
"""Email Ashley when a $147 résumé-translation buyer submits their intake form.

Without this, a paid customer's résumé sits in KV and nobody knows. That is the
worst possible failure for a done-for-you service: the customer has paid and is
waiting.

Reads KV directly (Cloudflare API), tracks what has already been notified in a
state file, and emails each NEW submission once. Silent on a clean no-op.

Usage: /opt/venv/bin/python3 resume_alert.py [--test]
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.path.insert(0, "/data/business/hca-daily/email")
import mailer  # noqa: E402  (shared SMTP-first sender; see mailer.py)

CF_ENV = "/data/.cloudflare.env"
ACCT = "7331f696a15eee3fe7bf94f41376f7b8"
NS = "048d56b2542343939b4822283e77888b"
STATE = "/data/business/hca-daily/ops/resume_alert_state.json"
# Same token + credential pattern the working lead drip uses. youtube_token.json
# is a different grant and will fail here.
TOKEN = "/data/google_token.json"
FROM = "ashleyhussainokorafor@gmail.com"
TO = "ashleyhussainokorafor@gmail.com"


def cf_creds():
    env = open(CF_ENV).read()
    return (re.search(r"CLOUDFLARE_API_KEY=([^\s]+)", env).group(1).strip("\"'"),
            re.search(r"CLOUDFLARE_EMAIL=([^\s]+)", env).group(1).strip("\"'"))


def kv_keys(prefix):
    key, email = cf_creds()
    r = subprocess.run(
        ["curl", "-s", "-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {key}",
         f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{NS}"
         f"/keys?prefix={prefix}"], capture_output=True, text=True)
    try:
        return [x["name"] for x in json.loads(r.stdout).get("result", [])]
    except Exception:  # noqa: BLE001
        return []


def kv_get(name):
    key, email = cf_creds()
    r = subprocess.run(
        ["curl", "-s", "-H", f"X-Auth-Email: {email}", "-H", f"X-Auth-Key: {key}",
         f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{NS}"
         f"/values/{name}"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:  # noqa: BLE001
        return None


def send(subject, body):
    """Send via the shared mailer (SMTP if configured, Gmail API otherwise).

    Uses mailer.py rather than a local Gmail-API call because the API path dies
    every 7 days while the OAuth app is in Testing mode — and this is the alert
    that tells Ashley a $147 order arrived. It must not be the fragile one.
    """
    ok, detail = mailer.send(TO, subject, body, from_name=None)
    if not ok:
        raise RuntimeError(f"send failed: {detail}")
    return detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true", help="send a sample email and exit")
    args = ap.parse_args()

    if args.test:
        send("[TEST] Résumé intake alert is wired up",
             "This is a test. A real alert will contain the buyer's résumé.")
        print("test email sent")
        return 0

    state = json.load(open(STATE)) if os.path.exists(STATE) else {"notified": []}
    notified = set(state["notified"])

    keys = kv_keys("resume:")
    new = [k for k in keys if k not in notified]
    if not new:
        return 0   # silent no-op

    for name in new:
        rec = kv_get(name)
        if not rec:
            continue
        body = "\n".join([
            "A $147 Résumé Translation order just came in.",
            "",
            f"Name        : {rec.get('name') or '(not given)'}",
            f"Reply to    : {rec.get('email')}",
            f"Target role : {rec.get('targetRole') or '(not given)'}",
            f"Submitted   : {rec.get('receivedAt')}",
            "",
            f"Notes from them:\n  {rec.get('notes') or '(none)'}",
            "",
            "--- THEIR RÉSUMÉ " + "-" * 40,
            rec.get("resumeText", ""),
            "-" * 58,
            "",
            "Due back within 3 business days. One revision included.",
        ])
        send(f"RÉSUMÉ ORDER — {rec.get('name') or rec.get('email')}", body)
        notified.add(name)
        state["notified"] = sorted(notified)
        json.dump(state, open(STATE, "w"), indent=1)
        print(f"alerted: {rec.get('email')}")

    print(f"new orders alerted: {len(new)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())