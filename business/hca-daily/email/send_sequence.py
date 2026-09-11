#!/usr/bin/env python3
"""Send one email from the HCA Daily scorecard->vault sequence via Gmail API.

Usage:
    python3 send_sequence.py --email lead@example.com \\
        --first-name Sarah --score 72 --top "Resume Metrics" \\
        --weakest "Interview Readiness" --day 4

    --day maps to the sequence: 0,1,3,5,7,9  (see sequence.md)

Sends a single email. To drip the whole series, call repeatedly with
increasing --day on your own scheduler. Sending is one-shot by design so a
failed send never re-fires a later one accidentally.
"""
import argparse
import base64
import json
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/data/google_token.json"
VAULT_LINK = "https://buy.stripe.com/fZufZi70H1eAaaFgrIgMw04"
FROM_NAME = "Dr. Ashley Hussain - The HCA Daily"
FROM_EMAIL = "ashleyhussainokorafor@gmail.com"

# Each key is the --day value. Body templates use .format() placeholders.
TEMPLATES = {
    0: {
        "subject": "Your HCA Career Readiness Score is in",
        "body": (
            "Hi {first},\n\n"
            "Here's what you came for — your HCA Career Readiness Score:\n\n"
            "**{score} / 100**\n\n"
            "You scored strongest in **{top}**, and your biggest gap is "
            "**{weak}**.\n\n"
            "Here's the honest version of what that means: most "
            "healthcare-administration candidates walk into interviews with a "
            "great resume and no idea which dimension the interviewer is "
            "actually screening them on. The people who win offers know their "
            "weak spot going in. Now you know yours.\n\n"
            "Tomorrow I'll send you the single fastest way to close that gap.\n\n"
            "— Ashley\n\n"
            "P.S. Reply if your result surprised you. I read every one.\n\n---\n"
            "Reply STOP to opt out."
        ),
    },
    1: {
        "subject": "The #1 reason qualified candidates lose the offer",
        "body": (
            "Hi {first},\n\n"
            "I've sat on the hiring side, and here's the uncomfortable truth "
            "I'd tell you in person: it's almost never your experience. It's "
            "your **answer format.**\n\n"
            "Ask a candidate \"tell me about a time you improved productivity\" "
            "and 9 out of 10 say something like \"I worked hard and we got "
            "better.\"\n\n"
            "Ask the one who got the offer, and you hear: \"That provider's "
            "production rose from 3,800 to 4,750 wRVUs — just under the 50th "
            "percentile — while our wRVU per FTE moved from 4,950 to 5,180 "
            "across twelve months.\"\n\n"
            "Same candidate. Same experience. One gets hired, one gets a \"we "
            "went another direction\" email. The difference is speaking the "
            "language healthcare executives actually interview in: numbers, "
            "benchmarks, results.\n\n"
            "The good news? It's completely learnable. It's not talent — it's "
            "a script. More on that in a couple days.\n\n"
            "— Ashley\n\n---\nReply STOP to opt out."
        ),
    },
    3: {
        "subject": "The 3-number formula interviewers secretly check",
        "body": (
            "Hi {first},\n\n"
            "Give me 90 seconds and I'll give you a framework that works in "
            "any healthcare-interview room.\n\n"
            "Every strong behavioral answer has **three parts**:\n\n"
            "1. **A baseline** — the number you started with. (\"We were "
            "running a 40% no-show rate.\")\n"
            "2. **The action** — what *you* specifically did. (\"I rebuilt "
            "the reminder protocol and moved to same-day open scheduling.\")\n"
            "3. **The result** — the number you ended with, plus a benchmark. "
            "(\"No-shows dropped to 19% — the MGMA 50th percentile.\")\n\n"
            "That's it. Baseline → action → result. Most candidates give you "
            "#2 and skip the numbers on either side. That's the whole game.\n\n"
            "Try it on your last interview question and watch how differently "
            "it lands. I've got something specific for this — next email.\n\n"
            "— Ashley\n\n---\nReply STOP to opt out."
        ),
    },
    5: {
        "subject": "I built you a cheat code (156 of them, actually)",
        "body": (
            "Hi {first},\n\n"
            "When my students asked me to stop repeating myself, I wrote it "
            "all down. The result is a 157-page playbook:\n\n"
            "**The HCA Interview Answer Vault — 156 real questions with "
            "complete answer scripts.**\n\n"
            "- 30 Behavioral & Leadership\n"
            "- 30 Operational & Metrics-Driven\n"
            "- 30 Revenue Cycle & Patient Access\n"
            "- 30 Clinical Ops, Quality, HIM & Long-Term Care\n"
            "- 36 Salary negotiation scripts and follow-up emails\n\n"
            "Every single one uses the baseline → action → result formula, "
            "and every one is anchored to the real metrics hiring executives "
            "ask about — wRVUs, days in A/R, denial rates, HCAHPS composites, "
            "third-next-available.\n\n"
            "You don't memorize all 156. You read the 5–8 relevant to your "
            "next interview and you walk in speaking the language.\n\n"
            "Normally $97. For readers on this list, it's **$27.**\n\n"
            "Get the Vault: {vault}\n\n"
            "30-day, no-questions money-back guarantee.\n\n"
            "— Ashley\n\n---\nReply STOP to opt out."
        ),
    },
    7: {
        "subject": '"But I\'m not a metrics person"',
        "body": (
            "Hi {first},\n\n"
            "If the thought running through your head right now is \"this all "
            "sounds great, but I don't have impressive numbers to talk about"
            "\" — I want to stop you right there. You do. You just haven't "
            "framed them yet.\n\n"
            "Every role touches numbers. Front desk? No-show rate and "
            "point-of-service collections. Billing? Clean claim rate and days "
            "in A/R. Clinical? HCAHPS and length of stay.\n\n"
            "The Vault doesn't invent numbers for you. It shows you **which** "
            "number your role should already be tracking, and exactly how to "
            "say it so it lands.\n\n"
            "And if it doesn't move the needle in 30 days, email me and I "
            "refund you. You keep the Vault either way.\n\n"
            "Get the Vault: {vault}\n\n"
            "— Ashley\n\n---\nReply STOP to opt out."
        ),
    },
    9: {
        "subject": "Last one from me on this (closing this list price)",
        "body": (
            "Hi {first},\n\n"
            "I said I wouldn't email you forever, so this is the last one.\n\n"
            "In the last week you learned the #1 reason qualified candidates "
            "lose offers, got the 3-number formula, and now know exactly what "
            "the Vault is.\n\n"
            "Here's the honest bottom line: the $27 price is an early-list "
            "price. When the Vault moves to the public site next month, it "
            "goes to $97.\n\n"
            "The difference between the candidate who walks in prepared and "
            "the one who wings it is typically the job itself — an offer that "
            "can be worth $10k–$30k more in year one.\n\n"
            "One $27 decision. A year of higher income. You can do the math "
            "faster than I can type it.\n\n"
            "Get the Vault: {vault}\n\n"
            "Either way — good luck in that next room. You've already shown "
            "more initiative than most by scoring yourself today.\n\n"
            "— Ashley\n\n---\nReply STOP to opt out."
        ),
    },
}


def build_service():
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
    return build("gmail", "v1", credentials=creds)


def send(service, to, subject, body):
    msg = MIMEText(body)
    msg["from"] = f'{FROM_NAME} <{FROM_EMAIL}>'
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--first-name", default="there")
    ap.add_argument("--score", default="")
    ap.add_argument("--top", default="")
    ap.add_argument("--weakest", default="")
    ap.add_argument("--day", type=int, required=True,
                    choices=sorted(TEMPLATES.keys()))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tpl = TEMPLATES[args.day]
    body = tpl["body"].format(
        first=args.first_name,
        score=args.score,
        top=args.top,
        weak=args.weakest,
        vault=VAULT_LINK,
    )

    if args.dry_run:
        print(f"[DRY RUN] day={args.day}  to={args.email}")
        print(f"Subject: {tpl['subject']}")
        print("---")
        print(body)
        return

    service = build_service()
    sent = send(service, args.email, tpl["subject"], body)
    print(f"Sent day={args.day} to {args.email} -> message id {sent['id']}")


if __name__ == "__main__":
    main()