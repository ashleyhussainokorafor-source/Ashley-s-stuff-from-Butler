#!/usr/bin/env python3
"""Sync HCA Daily scorecard leads (Cloudflare KV) -> Google Sheet + email alert.

Runs on a cron schedule. Idempotent: dedupes by the KV lead key, so a lead is
never double-written and nothing is lost if a run overlaps.

Google auth uses the same token as the university-batch sender
(/data/google_token.json -> ashleyhussainokorafor@gmail.com).
"""
import json
import os
import urllib.request

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

WORKER = "https://hca-daily.empathycollection.workers.dev"
TOKEN_PATH = "/data/google_token.json"
DEV_VARS = "/data/business/hca-daily/worker/.dev.vars"
SHEET_TITLE = "HCA Daily - Scorecard Leads"
SHEET_ID_FILE = "/data/business/hca-daily/email/sheet_id.txt"
NOTIFY_EMAIL = "ashleyhussainokorafor@gmail.com"

HEADERS = ["Lead ID", "Received At", "Email", "Name", "Overall",
           "Resume", "Vocabulary", "LinkedIn", "Interview"]


def google_service(api, version):
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    creds = Credentials(
        token=tok.get("token"),
        refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"),
        client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"),
        scopes=tok.get("scopes"),
    )
    return build(api, version, credentials=creds)


def get_admin_token():
    with open(DEV_VARS) as f:
        for line in f:
            if line.startswith("ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("ADMIN_TOKEN not found in .dev.vars")


def fetch_leads():
    url = f"{WORKER}/admin/leads?token={get_admin_token()}"
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.load(r).get("leads", [])


def get_or_create_sheet(sheets):
    if os.path.exists(SHEET_ID_FILE):
        sid = open(SHEET_ID_FILE).read().strip()
        if sid:
            try:
                sheets.spreadsheets().get(spreadsheetId=sid).execute()
                return sid
            except Exception:
                pass
    ss = sheets.spreadsheets().create(
        body={"properties": {"title": SHEET_TITLE}}).execute()
    sid = ss["spreadsheetId"]
    with open(SHEET_ID_FILE, "w") as f:
        f.write(sid)
    return sid


def ensure_headers(sheets, sid):
    r = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="A1:I1").execute()
    if not r.get("values"):
        sheets.spreadsheets().values().update(
            spreadsheetId=sid, range="A1:I1", valueInputOption="RAW",
            body={"values": [HEADERS]}).execute()


def existing_keys(sheets, sid):
    r = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="A:A").execute()
    return set(v[0] for v in r.get("values", [])[1:] if v)


def send_notification(gmail, new_rows):
    lines = ["New HCA Daily scorecard leads:\n"]
    for row in new_rows:
        email = row[2] or "(no email)"
        name = row[3] or ""
        overall = row[4]
        lines.append(f"- {name} <{email}> — score {overall}/100")
    lines.append("\nOpen the sheet to see the full breakdown.")
    body = "\n".join(lines)

    import base64
    from email.mime.text import MIMEText
    msg = MIMEText(body)
    msg["from"] = f'Dr. Ashley Hussain - The HCA Daily <{NOTIFY_EMAIL}>'
    msg["to"] = NOTIFY_EMAIL
    msg["subject"] = f"🎯 {len(new_rows)} new HCA Daily scorecard lead(s)"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    sheets = google_service("sheets", "v4")
    gmail = google_service("gmail", "v1")

    sid = get_or_create_sheet(sheets)
    ensure_headers(sheets, sid)

    leads = fetch_leads()
    keys = existing_keys(sheets, sid)

    new_rows = []
    for lead in leads:
        k = lead.get("_key", "")
        if not k or k in keys:
            continue
        dims = lead.get("dimensions") or {}
        new_rows.append([
            k,
            lead.get("receivedAt") or lead.get("ts") or "",
            lead.get("email", ""),
            lead.get("name", ""),
            lead.get("overall", ""),
            dims.get("resume", ""),
            dims.get("vocabulary", ""),
            dims.get("linkedin", ""),
            dims.get("interview", ""),
        ])

    if new_rows:
        sheets.spreadsheets().values().append(
            spreadsheetId=sid, range="A1", valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": new_rows}).execute()
        send_notification(gmail, new_rows)

    print(f"done: {len(new_rows)} new leads written "
          f"({len(leads)} total in KV), sheet={sid}")


if __name__ == "__main__":
    main()