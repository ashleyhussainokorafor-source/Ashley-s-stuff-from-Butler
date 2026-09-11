#!/usr/bin/env python3
"""HCA Daily lead drip engine.

Fetches leads from the Cloudflare KV (via /admin/leads), figures out which
email in the 6-email nurture sequence each lead is due for based on capture
time, and sends the next due email via Gmail.

Idempotent: tracks sent emails in a local state file so a lead is never
emailed the same message twice, and re-running is safe.

Schedule: run every ~2 hours via cron. Leads get:
  Day 0 (email 1)  - immediately
  Day 1 (email 2)  - pain
  Day 3 (email 3)  - value
  Day 5 (email 4)  - pitch
  Day 7 (email 5)  - objection
  Day 9 (email 6)  - close
"""
import base64
import json
import os
import time
import urllib.request
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

WORKER = "https://hca-daily.empathycollection.workers.dev"
TOKEN_PATH = "/data/google_token.json"
DEV_VARS = "/data/business/hca-daily/worker/.dev.vars"
STATE_FILE = "/data/business/hca-daily/email/drip_state.json"
FROM_NAME = "Dr. Ashley Hussain - The HCA Daily"
FROM_EMAIL = "ashleyhussainokorafor@gmail.com"
VAULT_LINK = "https://buy.stripe.com/fZufZi70H1eAaaFgrIgMw04"

# (day, hours_after_capture) -> email definition
SEQUENCE = [
    (0, 0.0, "Your HCA Career Readiness Score is in",
     "Hi {first},\n\nHere's what you came for — your HCA Career Readiness "
     "Score:\n\n**{score} / 100**\n\nYou scored strongest in **{top}**, and "
     "your biggest gap is **{weak}**.\n\nThe people who win offers know their "
     "weak spot going in. Now you know yours.\n\nTomorrow I'll send you the "
     "single fastest way to close that gap.\n\n— Ashley\n\nP.S. Reply if your "
     "result surprised you. I read every one.\n\n---\nReply STOP to opt out."),
    (1, 24.0, "The #1 reason qualified candidates lose the offer",
     "Hi {first},\n\nI've sat on the hiring side, and here's the uncomfortable "
     "truth: it's almost never your experience. It's your **answer format.**\n\n"
     "Ask a candidate \"tell me about a time you improved productivity\" and 9 "
     "out of 10 say \"I worked hard and we got better.\" Ask the one who got "
     "the offer, and you hear numbers, benchmarks, results.\n\nSame candidate. "
     "Same experience. One gets hired. The difference is speaking the language "
     "healthcare executives actually interview in.\n\nThe good news? It's "
     "completely learnable. It's not talent — it's a script. More in a couple "
     "days.\n\n— Ashley\n\n---\nReply STOP to opt out."),
    (3, 72.0, "The 3-number formula interviewers secretly check",
     "Hi {first},\n\nGive me 90 seconds and I'll give you a framework that "
     "works in any healthcare-interview room.\n\nEvery strong answer has three "
     "parts:\n1. **A baseline** — the number you started with.\n2. **The "
     "action** — what you specifically did.\n3. **The result** — the number you "
     "ended with, plus a benchmark.\n\nMost candidates give #2 and skip the "
     "numbers. That's the whole game.\n\nTry it on your last interview question "
     "and watch how differently it lands. I've got something specific for this "
     "— next email.\n\n— Ashley\n\n---\nReply STOP to opt out."),
    (5, 120.0, "I built you a cheat code (156 of them, actually)",
     "Hi {first},\n\nWhen my students asked me to stop repeating myself, I "
     "wrote it all down. The result is a 157-page playbook:\n\n**The HCA "
     "Interview Answer Vault — 156 real questions with complete answer "
     "scripts.**\n\n- 30 Behavioral & Leadership\n- 30 Operational & "
     "Metrics-Driven\n- 30 Revenue Cycle & Patient Access\n- 30 Clinical Ops, "
     "Quality, HIM & Long-Term Care\n- 36 Salary negotiation scripts\n\nEvery "
     "one uses the baseline → action → result formula, anchored to the real "
     "metrics hiring executives ask about.\n\nNormally $97. For readers on this "
     "list, it's **$27.**\n\nGet the Vault: {vault}\n\n30-day money-back "
     "guarantee.\n\n— Ashley\n\n---\nReply STOP to opt out."),
    (7, 168.0, '"But I\'m not a metrics person"',
     "Hi {first},\n\nIf the thought running through your head is \"this all "
     "sounds great, but I don't have impressive numbers to talk about\" — stop "
     "right there. You do. You just haven't framed them yet.\n\nEvery role "
     "touches numbers. Front desk? No-show rate and point-of-service "
     "collections. Billing? Clean claim rate and days in A/R. Clinical? HCAHPS "
     "and length of stay.\n\nThe Vault doesn't invent numbers for you. It shows "
     "you which number your role should already be tracking, and how to say it "
     "so it lands.\n\nAnd if it doesn't move the needle in 30 days, email me "
     "and I refund you. You keep it either way.\n\nGet the Vault: {vault}\n\n— "
     "Ashley\n\n---\nReply STOP to opt out."),
    (9, 216.0, "Last one from me on this (closing this list price)",
     "Hi {first},\n\nI said I wouldn't email you forever, so this is the last "
     "one.\n\nIn the last week you learned the #1 reason qualified candidates "
     "lose offers, got the 3-number formula, and now know exactly what the "
     "Vault is.\n\nHere's the honest bottom line: the $27 price is an "
     "early-list price. When the Vault moves to the public site, it goes to "
     "$97.\n\nThe difference between the candidate who walks in prepared and "
     "the one who wings it is typically the job itself — an offer worth "
     "$10k–$30k more in year one.\n\nGet the Vault: {vault}\n\nEither way — "
     "good luck in that next room.\n\n— Ashley\n\n---\nReply STOP to opt out."),
]


def admin_token():
    with open(DEV_VARS) as f:
        for line in f:
            if line.startswith("ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("ADMIN_TOKEN not found")


def fetch_leads():
    url = f"{WORKER}/admin/leads?token={admin_token()}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "HCA-Daily-LeadSync/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r).get("leads", [])


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except Exception:
            pass
    return {}


def save_state(state):
    json.dump(state, open(STATE_FILE, "w"), indent=2)


def gmail_service():
    tok = json.load(open(TOKEN_PATH))
    creds = Credentials(
        token=tok.get("token"), refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"), scopes=tok.get("scopes"))
    return build("gmail", "v1", credentials=creds)


def send_email(svc, to, subject, body):
    msg = MIMEText(body)
    msg["from"] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    svc.users().messages().send(userId="me", body={"raw": raw}).execute()


def lead_name(lead):
    n = (lead.get("name") or "").strip()
    return n.split()[0] if n else "there"


def main():
    leads = fetch_leads()
    state = load_state()
    now = time.time()
    svc = None  # lazy — only init if there's something to send

    sent_count = 0
    for lead in leads:
        key = lead.get("_key", "")
        if not key:
            continue
        email = (lead.get("email") or "").strip()
        if not email or "@" not in email:
            continue

        received = lead.get("receivedAt") or lead.get("ts") or ""
        try:
            # parse ISO; fall back to now if malformed
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(received.replace("Z", "+00:00"))
            age_h = (now - dt.timestamp()) / 3600.0
        except Exception:
            age_h = 0.0

        done = set(state.get(key, []))
        dims = lead.get("dimensions") or {}

        for day, hours, subject, body in SEQUENCE:
            if day in done:
                continue
            if age_h < hours:
                continue  # not due yet
            # due and not yet sent -> send
            if svc is None:
                svc = gmail_service()
            text = body.format(
                first=lead_name(lead),
                score=lead.get("overall", ""),
                top="your strongest area",
                weak="your biggest gap",
                vault=VAULT_LINK,
            )
            try:
                send_email(svc, email, subject, text)
                done.add(day)
                state[key] = sorted(done)
                sent_count += 1
            except Exception as e:
                print(f"  ! failed to send day {day} to {email}: {str(e)[:80]}")

    if sent_count:
        save_state(state)
    # Only emit output when something happened, so a no-op cron tick stays
    # silent (and errors above already print inline).
    if sent_count:
        print(f"Sent {sent_count} drip email(s) across {len(leads)} lead(s).")


if __name__ == "__main__":
    main()