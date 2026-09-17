#!/usr/bin/env python3
"""Restructure @professorashley video descriptions so the FREE offer is visible.

Why: YouTube collapses descriptions behind "...more" after roughly two lines.
The previous pass put a PAID Stripe subscription link on line 1 and buried the
free scorecard link at the bottom, so 272 videos / 644k lifetime views produced
almost no traffic or leads.

New layout:
  line 1-2 : free scorecard CTA (visible without expanding) + UTM-tagged link
  below    : free lead magnet, then the two paid one-time offers
  footer   : what the channel is

Modes:
  --dry-run        show what would change
  --apply N        update up to N videos, highest-viewed first (quota aware)
  --comments N     add a pinned first comment to the top N videos (by views)

Quota note: videos.update = 50 units, commentThreads.insert = 50 units.
Default daily quota is 10,000 units.
"""
import argparse
import json
import os
import sys
import time

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "/data/youtube_token.json"
STATE = "/data/automation/scripts/yt_cta_upgrade_state.json"

UTM = "utm_source=youtube&utm_medium=description&utm_campaign=scorecard"
UTM_PB = "utm_source=youtube&utm_medium=description&utm_campaign=playbook"

SCORECARD = f"https://thehcadaily.com/scorecard?{UTM}"
PLAYBOOK = f"https://thehcadaily.com/playbook?{UTM_PB}"
VAULT = "https://buy.stripe.com/fZufZi70H1eAaaFgrIgMw04"
ACCEL = "https://buy.stripe.com/9B63cwdp53mIdmR8ZggMw06"

MARKER = "Free 90-second scorecard"

NEW_TOP = (
    "Free 90-second scorecard — how far is your résumé from the director role?\n"
    f"👉 {SCORECARD}\n"
    "\n"
    "📥 Free download — The HCA Metric-Driven Résumé Playbook:\n"
    f"👉 {PLAYBOOK}\n"
    "\n"
    "If you want the depth:\n"
    f"• Interview Answer Vault — 156 real interview answers · $27 → {VAULT}\n"
    f"• Career Accelerator — adaptive plan + 24/7 AI advisory · $297 → {ACCEL}\n"
    "\n"
    "—\n"
    "The HCA Daily · 5 minutes a day of wRVUs, days in A/R, denial rates and the "
    "rest of the language hiring execs actually use.\n"
    "Dr. Ashley Hussain-Okorafor, DBA · https://www.youtube.com/@professorashley"
)

PINNED_COMMENT = (
    "Free 90-second scorecard — it scores the gap between your résumé and the "
    "director-level roles you're applying for, and gives you your top 3 fixes:\n"
    f"👉 {SCORECARD}\n"
    "\n"
    "(Free puzzle download too: the Metric-Driven Résumé Playbook → "
    f"{PLAYBOOK} )"
)


def make_svc():
    tok = json.load(open(TOKEN))
    creds = Credentials(
        token=tok.get("token"), refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"), scopes=tok.get("scopes"))
    return build("youtube", "v3", credentials=creds)


def retry(req, attempts=4):
    for a in range(attempts):
        try:
            return req.execute()
        except HttpError as e:
            if e.resp.status in (500, 502, 503) and a < attempts - 1:
                time.sleep(2 * (a + 1))
                continue
            raise


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"done": [], "commented": []}


def save_state(s):
    json.dump(s, open(STATE, "w"))


def get_videos(svc):
    ch = retry(svc.channels().list(part="contentDetails", mine=True))
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, pt = [], None
    while True:
        r = retry(svc.playlistItems().list(
            part="contentDetails", playlistId=uploads, maxResults=50, pageToken=pt))
        ids += [i["contentDetails"]["videoId"] for i in r.get("items", [])]
        pt = r.get("nextPageToken")
        if not pt:
            break
    out = []
    for i in range(0, len(ids), 50):
        r = retry(svc.videos().list(part="snippet,statistics", id=",".join(ids[i:i + 50])))
        for v in r.get("items", []):
            out.append({
                "id": v["id"],
                "title": v["snippet"].get("title", ""),
                "desc": v["snippet"].get("description", ""),
                "categoryId": v["snippet"].get("categoryId", "27"),
                "views": int(v["statistics"].get("viewCount", 0)),
            })
    out.sort(key=lambda v: -v["views"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", type=int, default=0)
    ap.add_argument("--comments", type=int, default=0)
    a = ap.parse_args()

    svc = make_svc()
    state = load_state()
    videos = get_videos(svc)
    todo = [v for v in videos if MARKER not in v["desc"] and v["id"] not in state["done"]]
    print(f"total videos: {len(videos)} | already upgraded: {len(videos) - len(todo)} | to do: {len(todo)}")

    if a.dry_run:
        print("\nExample — new description that will be written:\n" + "-" * 60)
        print(NEW_TOP)
        print("-" * 60)
        print("\nNext 10 videos to update (highest views first):")
        for v in todo[:10]:
            print(f"  {v['views']:>7} views  {v['id']}  {v['title'][:55]}")
        return 0

    if a.apply:
        limit = min(a.apply, len(todo))
        ok = fail = 0
        for v in todo[:limit]:
            body = {
                "id": v["id"],
                "snippet": {
                    "title": v["title"],
                    "categoryId": v.get("categoryId", "27"),
                    "description": NEW_TOP,
                },
            }
            try:
                retry(svc.videos().update(part="snippet", body=body))
                state["done"].append(v["id"])
                ok += 1
                print(f"  ok  {v['views']:>7}v  {v['title'][:50]}")
            except HttpError as e:
                fail += 1
                print(f"  FAIL {v['id']} {e.resp.status} {str(e)[:120]}")
                if e.resp.status in (403,) and "quota" in str(e).lower():
                    print("quota exhausted — stopping; rerun tomorrow")
                    break
            save_state(state)
        print(f"\nupdated {ok}, failed {fail}, remaining {len(todo) - ok}")
        return 0

    if a.comments:
        n = 0
        for v in videos[:a.comments]:
            if v["id"] in state["commented"]:
                continue
            try:
                r = retry(svc.commentThreads().insert(
                    part="snippet",
                    body={"snippet": {
                        "videoId": v["id"],
                        "topLevelComment": {"snippet": {"textOriginal": PINNED_COMMENT}},
                    }}))
                cid = r["snippet"]["topLevelComment"]["id"]
                state["commented"].append(v["id"])
                save_state(state)
                n += 1
                print(f"  commented  {v['views']:>7}v  {v['title'][:50]}")
            except HttpError as e:
                print(f"  FAIL comment {v['id']} {e.resp.status} {str(e)[:120]}")
                if e.resp.status == 403 and "quota" in str(e).lower():
                    break
        print(f"\ncommented on {n}")
        return 0

    print("nothing to do — pass --dry-run, --apply N or --comments N")
    return 0


if __name__ == "__main__":
    sys.exit(main())