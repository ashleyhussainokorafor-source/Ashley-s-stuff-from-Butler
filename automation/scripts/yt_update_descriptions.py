#!/usr/bin/env python3
"""Add the HCA scorecard CTA to @professorashley's YouTube video descriptions.

Modes:
  --dry-run   : count videos + show which need updating (no writes)
  --apply N   : update up to N videos (append CTA where missing), quota-aware
"""
import json
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CTA = (
    "\n\n"
    "🚀 Fast-track your healthcare admin career — free.\n"
    "Take my HCA Career Readiness Scorecard: 10 questions, 90 seconds — get your "
    "0–100 score + your top 3 fixes.\n"
    "👉 https://thehcadaily.com/scorecard"
)
LINK = "thehcadaily.com/scorecard"
OLD_LINK = "hca-daily.empathycollection.workers.dev/scorecard"


def make_svc():
    tok = json.load(open("/data/youtube_token.json"))
    creds = Credentials(
        token=tok.get("token"), refresh_token=tok.get("refresh_token"),
        token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
        client_secret=tok.get("client_secret"), scopes=tok.get("scopes"))
    return build("youtube", "v3", credentials=creds)


def _execute_with_retry(req, attempts=4):
    import time
    from googleapiclient.errors import HttpError
    for a in range(attempts):
        try:
            return req.execute()
        except HttpError as e:
            if e.resp.status in (500, 502, 503) and a < attempts - 1:
                time.sleep(2 * (a + 1))
                continue
            raise


def get_all_videos(svc):
    # uploads playlist id
    ch = svc.channels().list(part="contentDetails", mine=True).execute()
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    videos = []
    page_token = None
    while True:
        resp = _execute_with_retry(svc.playlistItems().list(
            part="snippet",
            playlistId=uploads, maxResults=50, pageToken=page_token))
        for it in resp.get("items", []):
            sn = it["snippet"]
            videos.append({
                "video_id": sn["resourceId"]["videoId"],
                "title": sn.get("title", ""),
                "description": sn.get("description", ""),
                "views": 0,
            })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    # batch-fetch view counts (max 50 ids per videos.list call)
    ids = [v["video_id"] for v in videos]
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        resp = _execute_with_retry(svc.videos().list(
            part="statistics", id=",".join(batch)))
        stats = {it["id"]: it.get("statistics", {}).get("viewCount", "0")
                 for it in resp.get("items", [])}
        for v in videos:
            if v["video_id"] in stats:
                try:
                    v["views"] = int(stats[v["video_id"]])
                except (ValueError, TypeError):
                    v["views"] = 0
    return videos


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    svc = make_svc()
    videos = get_all_videos(svc)
    todo = [v for v in videos if LINK not in v["description"]]
    done = [v for v in videos if LINK in v["description"]]
    # highest views first — money-makers get the link first
    todo.sort(key=lambda v: v.get("views", 0), reverse=True)

    print(f"total videos: {len(videos)}")
    print(f"already have link: {len(done)}")
    print(f"need updating: {len(todo)}")

    if mode == "--dry-run":
        print("\ntop 12 MOST-VIEWED needing the link (will be done first):")
        for v in todo[:12]:
            print(f"  {v['views']:>9,} views  [{v['video_id']}] {v['title'][:45]!r}")
        return

    if mode == "--apply":
        n = limit if limit > 0 else len(todo)
        targets = todo[:n]
        print(f"\nupdating {len(targets)} video(s)...")
        updated = 0
        failed = 0
        for i, v in enumerate(targets, 1):
            desc = v["description"]
            if OLD_LINK in desc:
                new_desc = desc.replace(OLD_LINK, "thehcadaily.com/scorecard")
            else:
                new_desc = (desc.rstrip() + CTA).strip()
            try:
                svc.videos().update(
                    part="snippet",
                    body={"id": v["video_id"],
                          "snippet": {"title": v["title"],
                                      "description": new_desc,
                                      "categoryId": "22"}},
                ).execute()
                updated += 1
                if i % 25 == 0:
                    print(f"  ...{updated} done")
            except Exception as e:
                failed += 1
                err = str(e)
                if "quota" in err.lower() or "403" in err:
                    print(f"  ! quota/rate limit hit at video {i}; stopping. {err[:120]}")
                    break
                print(f"  ! failed [{v['video_id']}]: {err[:100]}")
        print(f"\nDONE: {updated} updated, {failed} failed")
        return

    print(f"unknown mode {mode}")


if __name__ == "__main__":
    main()