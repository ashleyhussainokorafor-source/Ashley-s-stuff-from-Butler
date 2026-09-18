#!/usr/bin/env python3
"""HCA Daily Shorts publisher — turns the queue into uploads.

Reads shorts/queue.json and uploads any post whose status is "ready" and whose
publish_at has passed. Run by cron (or by hand for a one-off).

Two safety rules that exist because they were learned the hard way:

  1. auto_publish defaults to FALSE. With it false, a post is uploaded
     UNLISTED and the script reports a preview link so a human can look at it.
     Only auto_publish=true sends anything public. Never flip it silently.
  2. Idempotent: a post that already has a videoId is never uploaded twice.
     Everything is keyed off queue.json, so the queue IS the state.

Usage:
  hca_short_publish.py             # upload anything due
  hca_short_publish.py --dry-run   # show what would be uploaded
  hca_short_publish.py --go-live <post_id>   # publish an already-uploaded unlisted post

Description is assembled in the order that survives YouTube's "…more" fold:
free offer on line 1, paid offers below it.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

PY_LIBS = "/opt/venv/lib/python3.13/site-packages"
if os.path.isdir(PY_LIBS) and PY_LIBS not in sys.path:
    sys.path.insert(0, PY_LIBS)

QUEUE = "/data/business/hca-daily/shorts/queue.json"
LOG = "/data/business/hca-daily/ops/OPS_LOG.md"
TOKEN = "/data/youtube_token.json"
UPLOAD_DIR = "/data/business/hca-daily/shorts"

CTA_URL = "https://thehcadaily.com/scorecard"
PLAYBOOK_URL = "https://thehcadaily.com/playbook"
PRICING_URL = "https://thehcadaily.com/pricing"


def describe(post):
    utm = (f"?utm_source=youtube&utm_medium=shorts&utm_campaign={post['id']}")
    return "\n".join([
        f"Free 90-second scorecard — how far is your résumé from the director role?",
        f"👉 {CTA_URL}{utm}",
        "",
        f"📥 Free download — The HCA Resume & Executive Career Playbook: 👉 {PLAYBOOK_URL}",
        "If you want the depth:",
        f"• Interview Answer Vault · $27 → {PRICING_URL}",
        f"• Career Accelerator · $297 → {PRICING_URL}",
        "",
        "—",
        "Dr. Ashley, DBA · healthcare administration, without the fluff · "
        "https://www.youtube.com/@professorashley",
    ])


def youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import google.auth.transport.requests
    tok = json.load(open(TOKEN))
    creds = Credentials(
        token=tok["token"], refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"), scopes=tok.get("scopes"),
    )
    if not creds.valid:
        creds.refresh(google.auth.transport.requests.Request())
    json.dump({
        "token": creds.token, "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri, "client_id": creds.client_id,
        "client_secret": creds.client_secret, "scopes": list(creds.scopes or []),
    }, open(TOKEN, "w"))
    return build("youtube", "v3", credentials=creds)


def log(line):
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--go-live", metavar="POST_ID",
                    help="flip an already-uploaded unlisted post to public")
    args = ap.parse_args()

    q = json.load(open(QUEUE))
    posts = q["posts"]
    now = datetime.now(timezone.utc)
    out = []

    # --go-live: publish something a human already approved
    if args.go_live:
        p = next((x for x in posts if x["id"] == args.go_live), None)
        if not p:
            return f"No post with id {args.go_live} in the queue."
        if not p.get("videoId"):
            return f"'{args.go_live}' has no videoId yet — nothing to publish."
        yt = youtube()
        yt.videos().update(part="status", body={
            "id": p["videoId"],
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        }).execute()
        # YouTube's read-after-write is EVENTUALLY CONSISTENT: a videos().list
        # fired immediately after the update can still return the OLD privacy
        # state. Poll until the change is actually visible, and if it never
        # lands, say so instead of claiming success.
        real = "unknown"
        for _ in range(8):
            time.sleep(3)
            real = yt.videos().list(part="status", id=p["videoId"]).execute()[
                "items"][0]["status"]["privacyStatus"]
            if real == "public":
                break
        p["status"] = "published" if real == "public" else "publish_unconfirmed"
        p["publishedAt"] = now.isoformat()
        json.dump(q, open(QUEUE, "w"), indent=2)
        log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `PUBLISHED` | Short "
            f"'{p['title']}' (youtube.com/shorts/{p['videoId']}) went public; "
            f"YouTube now reports {real}")
        if real != "public":
            return (f"⚠️ STILL NOT PUBLIC — '{p['title']}'\n"
                    f"https://youtube.com/shorts/{p['videoId']}\n"
                    f"YouTube reports privacyStatus={real} after retries. "
                    f"Re-run --go-live {p['id']}.")
        return (f"✅ PUBLISHED — '{p['title']}'\n"
                f"https://youtube.com/shorts/{p['videoId']}\n"
                f"YouTube now reports privacyStatus={real}")

    due = [p for p in posts
           if p.get("status") == "ready" and p.get("publishAt", "") <= now.isoformat()]

    if not due:
        # Silent no-op: the cron watchdog pattern.
        return ""

    if args.dry_run:
        return "Would upload:\n" + "\n".join(f"  {p['id']} — {p['title']}" for p in due)

    auto = bool(q.get("auto_publish", False))
    yt = youtube()
    from googleapiclient.http import MediaFileUpload

    for p in due:
        path = p["file"] if os.path.isabs(p["file"]) else os.path.join(UPLOAD_DIR, p["file"])
        if not os.path.exists(path):
            out.append(f"⚠️ MISSING FILE for '{p['id']}': {path}")
            log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `FAIL` | Short '{p['id']}' "
                f"queued but the video file is missing: {path}")
            continue
        body = {
            "snippet": {"title": p["title"], "description": describe(p),
                        "tags": p.get("tags", ["healthcare administration", "healthcare management",
                                               "MHA", "career advice"]),
                        "categoryId": "27"},
            "status": {"privacyStatus": "public" if auto else "unlisted",
                       "selfDeclaredMadeForKids": False},
        }
        resp = yt.videos().insert(part="snippet,status", body=body,
                                  media_body=MediaFileUpload(path, chunksize=-1,
                                                             resumable=True)).execute()
        vid = resp["id"]
        got = yt.videos().list(part="status", id=vid).execute()["items"][0]
        real = got["status"]["privacyStatus"]
        p["videoId"] = vid
        p["status"] = "published" if real == "public" else "awaiting_approval"
        p["uploadedAt"] = now.isoformat()
        log(f"- **{now.strftime('%Y-%m-%d %H:%M')} UTC** | `UPLOADED` | Short '{p['title']}' "
            f"→ youtube.com/shorts/{vid} (privacyStatus={real})")
        if real == "public":
            out.append(f"🟢 Short published: '{p['title']}'\nhttps://youtube.com/shorts/{vid}")
        else:
            out.append(f"🎬 NEW SHORT READY FOR REVIEW — '{p['title']}'\n"
                       f"Preview: https://youtube.com/shorts/{vid}\n"
                       f"It is UNLISTED (nobody can see it yet). Reply 'publish {p['id']}' to go live.")

    json.dump(q, open(QUEUE, "w"), indent=2)
    return "\n\n".join(out)


if __name__ == "__main__":
    try:
        msg = main()
    except Exception as e:
        print(f"Shorts publisher error: {type(e).__name__}: {e}")
        sys.exit(1)
    if msg:
        print(msg)
