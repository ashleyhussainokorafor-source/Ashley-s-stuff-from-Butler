#!/usr/bin/env python3
"""Shared email sender for HCA Daily — SMTP first, Gmail API as fallback.

WHY THIS EXISTS
The Gmail-API path authenticates with an OAuth refresh token. The Google Cloud
project's consent screen is in "Testing" mode, and Google expires refresh tokens
after exactly 7 days in that mode. That is not a theory: every Gmail token on this
box died on a 7-day boundary, and it silently killed the lead drip, the $147
résumé-order alerts and the university outreach sender at the same moment.

SMTP with a Google App Password has no such expiry. This module prefers SMTP and
only falls back to the API if no app password is configured.

CONFIG — /data/.gmail.env  (chmod 600, never committed; .gitignore covers *.env)

    SMTP_USER=ashleyhussainokorafor@gmail.com
    SMTP_APP_PASSWORD=xxxxxxxxxxxxxxxx        # 16 chars, spaces optional

Create one at https://myaccount.google.com/apppasswords (needs 2-Step Verification
on the account). Revoke it any time from the same page.

USAGE

    from mailer import send
    ok, detail = send("someone@example.edu", "Subject", "Body text")
"""
import json
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid

CONFIG = "/data/.gmail.env"
API_TOKEN = "/data/google_token.json"
DEFAULT_FROM = "ashleyhussainokorafor@gmail.com"
FROM_NAME = "Dr. Ashley Hussain-Okorafor, DBA"


def _config():
    """Read SMTP settings. Tolerates spaces in the app password (Google shows it
    grouped in fours) and ignores commented lines."""
    if not os.path.exists(CONFIG):
        return None
    user = pw = None
    for line in open(CONFIG):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k == "SMTP_USER":
            user = v
        elif k == "SMTP_APP_PASSWORD":
            pw = v.replace(" ", "")
    if user and pw:
        return user, pw
    return None


def smtp_available():
    return _config() is not None


def _send_smtp(user, pw, to, subject, body, from_name, port=465):
    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to
    msg["From"] = formataddr((from_name, user)) if from_name else user
    msg["Subject"] = subject
    msg["Message-ID"] = make_msgid(domain="thehcadaily.com")

    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=30) as s:
            s.login(user, pw)
            s.send_message(msg)
    else:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(user, pw)
            s.send_message(msg)


def _send_api(to, subject, body, from_name):
    """Fallback: the original Gmail-API path. Will fail with invalid_grant once
    the OAuth refresh token is beyond its 7-day life — that is expected."""
    import base64
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    tok = json.load(open(API_TOKEN))
    creds = Credentials(
        token=tok.get("token"), refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"), scopes=tok.get("scopes"))
    svc = build("gmail", "v1", credentials=creds)
    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to
    msg["From"] = formataddr((from_name, DEFAULT_FROM)) if from_name else DEFAULT_FROM
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()


def send(to, subject, body, from_name=FROM_NAME, prefer_smtp=True):
    """Send one plain-text email.

    Returns (ok: bool, detail: str). Never raises — callers are cron scripts and
    a crash there is worse than a returned failure. NEVER logs the password.
    """
    cfg = _config() if prefer_smtp else None
    if cfg:
        user, pw = cfg
        last = ""
        for port in (465, 587):          # 465 first; 587 if that's filtered
            try:
                _send_smtp(user, pw, to, subject, body, from_name, port=port)
                return True, f"smtp:{port}"
            except smtplib.SMTPAuthenticationError as e:
                return False, f"smtp auth failed ({port}): {str(e)[:120]}"
            except Exception as e:  # noqa: BLE001
                last = f"{type(e).__name__}: {str(e)[:120]}"
        return False, f"smtp failed: {last}"

    try:
        _send_api(to, subject, body, from_name)
        return True, "gmail-api"
    except Exception as e:  # noqa: BLE001
        return False, f"api failed: {str(e)[:140]}"


if __name__ == "__main__":
    import sys
    if smtp_available():
        u, _ = _config()
        print(f"SMTP configured for {u}")
        if "--test" in sys.argv:
            ok, detail = send(DEFAULT_FROM, "[TEST] HCA mailer via SMTP",
                              "If you are reading this, SMTP sending works.")
            print("send:", ok, detail)
    else:
        print(f"No SMTP config at {CONFIG} — falling back to the Gmail API.")
        print("Add SMTP_USER and SMTP_APP_PASSWORD to switch.")
