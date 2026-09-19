#!/usr/bin/env python3
"""HCA Daily — direct outreach to healthcare-administration programs.

Sends the program-outreach email from Dr. Ashley's own Gmail, in small daily
batches, and tracks every contact in one place.

Design choices that matter:

  - SMALL BATCHES BY DEFAULT (12/day). Cold email from a personal Gmail at
    university scale is how you end up in spam and burn the domain. Slow is the
    feature, not a limitation.
  - PLAIN TEXT, one link, no images, no attachments. Looks like a person wrote
    it, because a person did.
  - ONE FOLLOW-UP, five days later, to non-responders only. Never a third.
  - Per-contact UTM (`utm_campaign=hca-programs-<slug>`), so when somebody
    finally does land on the site we can prove which university produced it.
  - Never emails the same address twice, skips anything in suppress.txt, and
    refuses addresses that clearly don't accept mail (noreply@, no-reply@).
  - Dry-run is the default. Nothing is sent unless --send is passed.

Usage:
  hca_outreach_send.py --preview        # show the next batch, send nothing
  hca_outreach_send.py --send           # send the next batch (default 12)
  hca_outreach_send.py --send --limit 5
  hca_outreach_send.py --report         # tracker summary
"""
import argparse
import base64
import glob
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.path.insert(0, "/data/business/hca-daily/email")
import mailer  # noqa: E402  shared SMTP-first sender; see mailer.py

TOKEN_PATH = "/data/google_token.json"
OUT_DIR = "/data/business/hca-daily/outreach"
TRACKER = os.path.join(OUT_DIR, "tracker.json")
SUPPRESS = os.path.join(OUT_DIR, "suppress.txt")
OPS_LOG = "/data/business/hca-daily/ops/OPS_LOG.md"

FROM_NAME = "Dr. Ashley Hussain-Okorafor, DBA"
FROM_EMAIL = "ashleyhussainokorafor@gmail.com"
FOLLOW_UP_AFTER_DAYS = 5
SITE = "https://thehcadaily.com"

BAD_PREFIXES = ("noreply", "no-reply", "donotreply", "do-not-reply", "postmaster",
                "webmaster", "abuse", "privacy", "unsubscribe")

# ---------------------------------------------------------------- copy

SUBJECTS = [
    "Free 90-second scorecard for your {program_short} students",
    "A free tool for your health administration students",
    "For your {program_short} students — free résumé-gap scorecard",
]

BODY = """{greeting}

I lecture in healthcare administration (DBA, MHA; six years teaching in the California State University system), and I built a free 90-second scorecard that shows a student exactly how far their résumé is from a director-level role. It scores four things — résumé, healthcare vocabulary, LinkedIn, and interview readiness — and emails them the result plus a free résumé playbook.

It costs your program nothing and takes one line in a syllabus or a career-services email.

{cta_line}

Two things I'm happy to do if it's useful:

  1. Send you a printable one-pager your students can scan in class.
  2. Talk about a cohort rate for résumé rewrites — I do those done-for-you, and a whole graduating class is cheaper than one at a time.

If it's not a fit for {program_short}, say so and I won't follow up.

— Dr. Ashley Hussain-Okorafor, DBA, MHA
   Healthcare administration · {site}

You're receiving this because you're listed as {role} for {org}. Reply "stop" and I'll remove you immediately."""

FOLLOW_UP_BODY = """{greeting}

Following up once on my note last week — the free scorecard for {program_short} students:

{site}/scorecard?utm_source=outreach&utm_medium=email&utm_campaign={slug}-fu

It's 90 seconds, no cost, and it tells a student which of four areas is actually holding them back. If you'd rather I didn't write again, reply "stop" and that's the end of it.

— Dr. Ashley Hussain-Okorafor, DBA, MHA"""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "program").lower()).strip("-")[:40]


def gmail_service():
    """Deprecated — send() now uses mailer.py (SMTP-first). Kept as a stub so the
    existing call site does not break. The Gmail-API token dies every 7 days
    while the OAuth app is in Testing mode."""
    return None


def load_targets():
    targets, seen = [], set()
    for path in sorted(glob.glob(os.path.join(OUT_DIR, "targets_*.json"))):
        try:
            data = json.load(open(path))
        except Exception as e:
            print(f"⚠️ could not read {os.path.basename(path)}: {e}")
            continue
        for t in data.get("targets", []):
            email = (t.get("email") or "").strip().lower()
            if not email or "@" not in email:
                continue
            if email.split("@")[0].startswith(BAD_PREFIXES):
                continue
            if email in seen:
                continue
            seen.add(email)
            t["_email"] = email
            t["_org"] = t.get("university") or t.get("org") or t.get("institution") or ""
            t["_source"] = os.path.basename(path)
            targets.append(t)
    return targets


def load_json(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path))
        except Exception:
            pass
    return default


def suppressions():
    s = set()
    if os.path.exists(SUPPRESS):
        for line in open(SUPPRESS):
            line = line.strip().lower()
            if line and not line.startswith("#"):
                s.add(line)
    return s


def render(target, template="first"):
    org = target.get("_org") or "your program"
    program = target.get("program") or "health administration"
    role = target.get("contact_role") or "a member of staff"
    name = (target.get("contact_name") or "").strip()
    first = name.split()[0] if name else ""
    greeting = f"Dr. {name}," if name else "Hello,"
    if name and not name.lower().startswith(("dr", "prof")):
        greeting = f"Hi {first}," if target.get("email_type") == "named" else "Hello,"
    slug = slugify(org)
    # Program strings arrive as "MHSA (Master of Health Services Administration)",
    # "M.S. in Health Administration", "Coding Specialist - Postsecondary certificate".
    # Take the short form before any parenthesis and normalise the common long names,
    # or the subject line ends up reading "your MHSA (MHSA) students".
    program_short = (program or "health administration").split("(")[0].strip(" -,–—")
    for long, short in (("Master of Health Administration", "MHA"),
                        ("Master of Health Services Administration", "MHSA"),
                        ("Master of Science in Health Administration", "MSHA"),
                        ("Bachelor of Science in Health Administration", "health administration"),
                        ("Bachelor of Health Services Administration", "health administration"),
                        ("Health Services Administration", "health administration"),
                        ("Health Care Administration", "healthcare administration"),
                        ("Health Administration", "health administration")):
        program_short = program_short.replace(long, short)
    program_short = " ".join(program_short.split())[:42].strip(" -,–—") or "health administration"

    if template == "followup":
        return ("Re: your students — free scorecard", FOLLOW_UP_BODY.format(
            greeting=greeting, program_short=program_short, site=SITE, slug=slug))

    subject = SUBJECTS[abs(hash(target["_email"])) % len(SUBJECTS)].format(
        program_short=program_short)
    body = BODY.format(
        greeting=greeting, program_short=program_short, org=org, role=role, site=SITE,
        cta_line=(f"{SITE}/scorecard?utm_source=outreach&utm_medium=email"
                  f"&utm_campaign={slug}"),
    )
    return subject, body


def send(svc, to, subject, body):
    """Route through the shared mailer (SMTP-first).

    The Gmail-API path here is what killed the first outreach batch: 10 sent,
    then 12 failed with invalid_grant when the OAuth refresh token hit its
    7-day expiry. SMTP with an app password has no such expiry.
    """
    ok, detail = mailer.send(to, subject, body, from_name=FROM_NAME)
    if not ok:
        raise RuntimeError(detail)


def log(line):
    try:
        with open(OPS_LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--replies", action="store_true",
                    help="scan the inbox for replies from tracked contacts and alert")
    ap.add_argument("--limit", type=int, default=12)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    tr = load_json(TRACKER, {"contacts": {}, "sent_total": 0})
    contacts = tr["contacts"]
    now = datetime.now(timezone.utc)

    if args.report:
        sent = sum(1 for c in contacts.values() if c.get("status") == "sent")
        fu = sum(1 for c in contacts.values() if c.get("status") == "followed_up")
        replies = sum(1 for c in contacts.values() if c.get("status") == "replied")
        stop = sum(1 for c in contacts.values() if c.get("status") == "unsubscribed")
        print(f"Outreach tracker: {len(contacts)} contacts known")
        print(f"  first email sent : {sent + fu + replies}")
        print(f"  follow-up sent   : {fu}")
        print(f"  replied          : {replies}")
        print(f"  opted out        : {stop}")
        due_fu = [e for e, c in contacts.items()
                  if c.get("status") == "sent"
                  and (now - datetime.fromisoformat(c["sent_at"])).days >= FOLLOW_UP_AFTER_DAYS]
        print(f"  follow-ups due   : {len(due_fu)}")
        return ""

    skip = suppressions()

    if args.replies:
        # One cheap inbox scan, matched against tracked contacts. A reply from a
        # program director is a hot lead — it must surface the same day, not sit
        # in Ashley's inbox unnoticed.
        svc = gmail_service()
        if svc is None:
            # SMTP is send-only. Reading replies still needs OAuth (or IMAP with
            # the same app password). Say so plainly rather than throwing a
            # TypeError on None.
            return ("⚠️ Reply tracking needs Gmail API access, which is currently "
                    "revoked. Sending works via SMTP; reading replies does not. "
                    "Re-authorise OAuth or add IMAP (see email/mailer.py).")
        res = svc.users().messages().list(userId="me", q="in:inbox newer_than:14d",
                                          maxResults=120).execute()
        new_replies = []
        for m in res.get("messages", []):
            d = svc.users().messages().get(userId="me", id=m["id"], format="metadata",
                                           metadataHeaders=["From", "Subject", "Date"]).execute()
            h = {x["name"].lower(): x["value"] for x in d["payload"]["headers"]}
            sender = h.get("from", "")
            addr = sender.split("<")[-1].strip(">").strip().lower()
            subj = h.get("subject", "")
            # An out-of-office auto-response is not a lead. It must not be counted
            # as a reply or it will make the campaign look like it's working.
            auto = (h.get("auto-submitted", "").startswith("auto")
                    or re.match(r"^(automatic reply|auto(matic)?[:\s]|out of (the )?office|"
                                r"autoreply|away from|thank you for your email)",
                                subj.strip(), re.I))
            if addr in contacts and contacts[addr].get("status") in ("sent", "followed_up"):
                if auto:
                    contacts[addr]["auto_reply_seen"] = subj[:120]
                    continue
                contacts[addr]["status"] = "replied"
                contacts[addr]["replied_at"] = now.isoformat()
                contacts[addr]["reply_subject"] = subj
                new_replies.append(f"{addr} — {subj[:70]}")
        json.dump(tr, open(TRACKER, "w"), indent=2)
        if new_replies:
            log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `OUTREACH-REPLY` | "
                f"{len(new_replies)} program contact(s) replied")
            return ("📬 REPLIED — program outreach:\n  " + "\n  ".join(new_replies) +
                    "\n\nA reply from a program director is a live lead. Answer it today.")
        return ""
    targets = [t for t in load_targets()
               if t["_email"] not in skip and t["_email"] not in contacts]

    if not targets and not args.preview:
        # nothing new — check for follow-ups that are due
        due = [(e, c) for e, c in contacts.items()
               if c.get("status") == "sent"
               and (now - datetime.fromisoformat(c["sent_at"])).days >= FOLLOW_UP_AFTER_DAYS]
        if not due:
            return ""
        batch = due[:args.limit]
        if not args.send:
            return "Follow-ups due:\n" + "\n".join(f"  {e}" for e, _ in batch)
        svc = gmail_service()
        done = []
        for email, c in batch:
            t = {"_email": email, "_org": c.get("org", ""), "program": c.get("program", ""),
                 "contact_name": c.get("contact_name", ""),
                 "contact_role": c.get("contact_role", ""),
                 "email_type": c.get("email_type", "named")}
            subject, body = render(t, "followup")
            send(svc, email, subject, body)
            c["status"] = "followed_up"
            c["followed_up_at"] = now.isoformat()
            done.append(email)
            time.sleep(3)
        json.dump(tr, open(TRACKER, "w"), indent=2)
        log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `OUTREACH` | sent {len(done)} "
            f"follow-up email(s) to program contacts")
        return f"📧 Sent {len(done)} outreach follow-ups."

    batch = targets[:args.limit]
    if args.preview or not args.send:
        out = [f"Next batch ({len(batch)} of {len(targets)} verified contacts):"]
        for t in batch:
            subject, _ = render(t)
            out.append(f"  {t['_email']:<42} {t['_org'][:34]:<34} [{t.get('email_type')}]")
        out.append("\nNothing sent — this was a preview. Re-run with --send.")
        return "\n".join(out)

    svc = gmail_service()
    sent = []
    for t in batch:
        subject, body = render(t)
        try:
            send(svc, t["_email"], subject, body)
        except Exception as e:
            contacts[t["_email"]] = {"status": "error", "detail": str(e)[:200],
                                     "org": t["_org"]}
            continue
        contacts[t["_email"]] = {
            "status": "sent", "sent_at": now.isoformat(), "org": t["_org"],
            "program": t.get("program", ""), "contact_name": t.get("contact_name", ""),
            "contact_role": t.get("contact_role", ""),
            "email_type": t.get("email_type", ""), "source_url": t.get("source_url", ""),
            "subject": subject,
        }
        sent.append(t["_email"])
        time.sleep(4)  # human pace; also keeps us far from any rate limit

    tr["sent_total"] = tr.get("sent_total", 0) + len(sent)
    json.dump(tr, open(TRACKER, "w"), indent=2)
    log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `OUTREACH` | sent {len(sent)} "
        f"program-outreach email(s); {len(targets) - len(batch)} still queued")
    return (f"📧 Sent {len(sent)} program-outreach email(s). "
            f"{len(targets) - len(batch)} contacts still queued.")


if __name__ == "__main__":
    try:
        msg = main()
    except Exception as e:
        print(f"Outreach sender error: {type(e).__name__}: {e}")
        sys.exit(1)
    if msg:
        print(msg)
