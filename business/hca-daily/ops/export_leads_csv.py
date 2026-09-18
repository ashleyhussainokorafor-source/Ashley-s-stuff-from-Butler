#!/usr/bin/env python3
"""Export every HCA Daily lead and user from Cloudflare KV to CSV.

Why this exists: the funnel writes leads to KV, not to Wix (or any other
platform). Nothing forwards them anywhere — LEAD_WEBHOOK is unset on the
Worker. Without this, the email list exists only inside a KV namespace that
nobody can read as a spreadsheet.

Grows a master file: re-running merges new rows in, never duplicates, so the
list accumulates over time. First run backfills.

Usage:
    export_leads_csv.py                 # merge into the master CSV
    export_leads_csv.py --stdout        # print CSV, write nothing
    export_leads_csv.py --out /tmp/x.csv
"""
import argparse
import csv
import json
import os
import urllib.parse
import urllib.request

ACCT = "7331f696a15eee3fe7bf94f41376f7b8"
NS = "048d56b2542343939b4822283e77888b"   # hca-daily-leads
CF_ENV = "/data/.cloudflare.env"
MASTER = "/data/business/hca-daily/ops/exports/leads.csv"

# Column order for the master file. Stable so the CSV stays diffable.
FIELDS = [
    "email", "record_type", "name", "captured_at", "source", "campaign",
    "country", "overall_score", "streak", "xp", "freezes", "user_id", "raw_key",
]


def cf_headers():
    env = {}
    with open(CF_ENV) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return {
        "X-Auth-Key": env["CLOUDFLARE_API_KEY"],
        "X-Auth-Email": env["CLOUDFLARE_EMAIL"],
    }


def api(path):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}{path}"
    req = urllib.request.Request(url, headers={**cf_headers(), "User-Agent": "HCA-Export/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def list_keys(prefix):
    keys, cursor = [], None
    while True:
        p = f"/storage/kv/namespaces/{NS}/keys?limit=1000"
        if prefix:
            p += f"&prefix={urllib.parse.quote(prefix, safe='')}"
        if cursor:
            p += f"&cursor={cursor}"
        d = api(p)
        keys += [k["name"] for k in d.get("result", [])]
        info = d.get("result_info", {})
        cursor = info.get("cursor")
        if not cursor or not d.get("result"):
            break
    return keys


def get_value(key):
    enc = urllib.parse.quote(key, safe="")
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCT}/storage/kv/namespaces/{NS}/values/{enc}"
    req = urllib.request.Request(url, headers={**cf_headers(), "User-Agent": "HCA-Export/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def row_from(key, raw):
    try:
        d = json.loads(raw) if raw else {}
    except Exception:
        d = {}
    if not isinstance(d, dict):
        d = {}
    is_lead = key.startswith("lead:")
    email = (d.get("email") or "").strip().lower()
    return {
        "email": email,
        "record_type": "lead" if is_lead else "user",
        "name": (d.get("name") or "").strip(),
        "captured_at": d.get("receivedAt") or d.get("createdAt") or "",
        "source": d.get("source") or d.get("utm_source") or "",
        "campaign": d.get("campaign") or d.get("utm_campaign") or "",
        "country": d.get("country") or "",
        "overall_score": d.get("overall", ""),
        "streak": d.get("streak", ""),
        "xp": d.get("xp", ""),
        "freezes": d.get("freezes", ""),
        "user_id": d.get("userId", ""),
        "raw_key": key,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args()

    keys = list_keys("lead:") + list_keys("user:")
    print(f"  KV keys found: {len(keys)}")

    rows = []
    for k in keys:
        r = row_from(k, get_value(k))
        if r["email"]:
            rows.append(r)
    print(f"  rows with a usable email: {len(rows)}")

    out = args.out or MASTER
    if not args.stdout:
        os.makedirs(os.path.dirname(out), exist_ok=True)

    # Merge with an existing master so the file accumulates over time.
    merged = {}
    if not args.stdout and os.path.exists(out):
        with open(out, newline="") as fh:
            for old in csv.DictReader(fh):
                merged[old.get("raw_key") or old.get("email", "")] = old
        print(f"  existing master rows: {len(merged)}")

    new_count = 0
    for r in rows:
        k = r["raw_key"] or r["email"]
        if k not in merged:
            new_count += 1
        merged[k] = r

    ordered = sorted(merged.values(), key=lambda r: r.get("captured_at") or "")
    print(f"  new since last export: {new_count}")
    print(f"  total rows: {len(ordered)}")

    buf = []
    import io
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    for r in ordered:
        w.writerow(r)
    text = sio.getvalue()

    if args.stdout:
        print(text)
        return

    with open(out, "w", newline="") as fh:
        fh.write(text)
    print(f"  wrote {out}")

    # A simple date-stamped snapshot too, so growth is visible over time.
    snap_dir = os.path.join(os.path.dirname(out), "snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    import datetime
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    with open(os.path.join(snap_dir, f"leads-{stamp}.csv"), "w", newline="") as fh:
        fh.write(text)
    print(f"  wrote snapshot for {stamp}")


if __name__ == "__main__":
    main()
