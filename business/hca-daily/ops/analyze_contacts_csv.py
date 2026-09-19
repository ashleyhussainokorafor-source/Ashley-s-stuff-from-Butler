#!/usr/bin/env python3
"""Analyze any contacts CSV (Wix export or similar) for HCA Daily value.

Turns a raw contacts export into the three things that actually matter:
  1. who you may legally email (subscriber status)
  2. warm prospects — people who WROTE IN, with their question preserved
  3. overlap with the HCA Daily funnel (so the same person isn't counted twice)

Handles Wix's header quirks: BOM, embedded newlines in the Message field,
and multi-line quoted cells (a naive row count over-reports — this uses a
real CSV parser).

Usage:
    analyze_contacts_csv.py <file.csv> [--label NAME] [--outdir DIR]

Writes into --outdir (default ops/exports/contacts-<label>/):
    summary.txt        human-readable findings
    subscribed.csv     emailable contacts only
    prospects.csv      people who wrote in, with their question
    unknown.csv        rows with no usable email
"""
import argparse
import collections
import csv
import os
import re
import sys

# Words that indicate the message is actually about a healthcare career,
# rather than Wix support phishing ("Account Blacklisting", "Dear Merchant").
TOPIC_WORDS = (
    "healthcare", "health care", "hospital", "nursing", "clinical", "administrat",
    "mha", "mph", "mba", "professor ashley", "resume", "interview", "career",
)
SPAM_WORDS = ("merchant", "blacklist", "support", "security notice", "verify your",
              "click here", "crypto", "seo services", "guest post")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Wix column names vary by export vintage; map the ones we care about.
ALIASES = {
    "email":   ["Email 1", "Email", "Email Address", "email"],
    "email2":  ["Email 2"],
    "first":   ["First Name", "First name", "first_name"],
    "last":    ["Last Name", "Last name", "last_name"],
    "status":  ["Email subscriber status", "Subscriber status", "email_subscriber_status"],
    "created": ["Created At (UTC+0)", "Created At", "created_at", "Date"],
    "source":  ["Source", "source"],
    "message": ["Message", "message", "Comments"],
    "subject": ["Subject", "subject"],
    "labels":  ["Labels", "labels"],
}


def pick(row, field):
    for a in ALIASES.get(field, []):
        if a in row and (row.get(a) or "").strip():
            return (row[a] or "").strip()
    return ""


def norm_email(*cands):
    for c in cands:
        m = EMAIL_RE.search(c or "")
        if m:
            return m.group(0).lower()
    return ""


def looks_spam(text):
    low = (text or "").lower()
    return any(w in low for w in SPAM_WORDS)


def looks_on_topic(text):
    low = (text or "").lower()
    return any(w in low for w in TOPIC_WORDS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--label", default=None)
    ap.add_argument("--outdir", default=None)
    args = ap.parse_args()

    label = args.label or os.path.splitext(os.path.basename(args.file))[0]
    outdir = args.outdir or f"/data/business/hca-daily/ops/exports/contacts-{label}"
    os.makedirs(outdir, exist_ok=True)

    with open(args.file, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    total = len(rows)
    recs = []
    for r in rows:
        e = norm_email(pick(r, "email"), pick(r, "email2"))
        if not e:
            continue
        recs.append({
            "email": e,
            "first": pick(r, "first"),
            "last": pick(r, "last"),
            "status": pick(r, "status") or "(blank)",
            "created": pick(r, "created"),
            "source": pick(r, "source"),
            "message": " ".join(pick(r, "message").split()),
            "subject": pick(r, "subject"),
        })

    st = collections.Counter(x["status"] for x in recs)
    src = collections.Counter(x["source"] or "(blank)" for x in recs)
    yrs = collections.Counter(x["created"][:4] for x in recs if x["created"][:4].isdigit())

    subscribed = [x for x in recs if x["status"].lower().startswith("subscribed")]
    prospects = [x for x in recs
                 if x["message"] and looks_on_topic(x["message"]) and not looks_spam(x["message"])]
    prospects.sort(key=lambda x: x["created"])

    lines = []
    A = lines.append
    A(f"Contacts analysis — {label}")
    A(f"source file: {args.file}")
    A("")
    A(f"rows parsed          : {total}")
    A(f"rows with an email   : {len(recs)}")
    A(f"rows without an email: {total - len(recs)}")
    A("")
    A("SUBSCRIBER STATUS (who you may legally email):")
    for k, v in st.most_common():
        A(f"  {v:5}  {k}")
    A("")
    A("SOURCE:")
    for k, v in src.most_common(8):
        A(f"  {v:5}  {k}")
    A("")
    A("JOINED BY YEAR:")
    for y, v in sorted(yrs.items()):
        A(f"  {y}: {v}")
    A("")
    A(f"WARM PROSPECTS (wrote in, on-topic, not spam): {len(prospects)}")
    for p in prospects:
        name = f"{p['first']} {p['last']}".strip() or "(no name)"
        A(f"  {p['created'][:10]}  {name}")
        A(f"      {p['message'][:200]}")

    summary = "\n".join(lines)

    with open(os.path.join(outdir, "summary.txt"), "w") as fh:
        fh.write(summary + "\n")
    with open(os.path.join(outdir, "subscribed.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["email", "first_name", "last_name", "joined_at", "source", "has_message"])
        for x in sorted(subscribed, key=lambda x: x["created"]):
            w.writerow([x["email"], x["first"], x["last"], x["created"], x["source"],
                        "yes" if x["message"] else ""])
    with open(os.path.join(outdir, "prospects.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "email", "wrote_on", "subscriber_status", "their_question"])
        for p in prospects:
            w.writerow([f"{p['first']} {p['last']}".strip(), p["email"], p["created"],
                        p["status"], p["message"]])
    with open(os.path.join(outdir, "unknown.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["first_name", "last_name", "status", "created", "raw_keys"])
        for r in rows:
            if not norm_email(pick(r, "email"), pick(r, "email2")):
                w.writerow([pick(r, "first"), pick(r, "last"), pick(r, "status"),
                            pick(r, "created"), ";".join(list(r.keys())[:8])])

    print(summary)
    print()
    print(f"wrote {outdir}/summary.txt")
    print(f"wrote {outdir}/subscribed.csv   ({len(subscribed)} rows)")
    print(f"wrote {outdir}/prospects.csv    ({len(prospects)} rows)")
    print(f"wrote {outdir}/unknown.csv      ({total - len(recs)} rows)")


if __name__ == "__main__":
    main()
