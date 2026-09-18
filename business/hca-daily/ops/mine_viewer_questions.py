#!/usr/bin/env python3
"""Mine the HCA Daily YouTube channel's comments for what viewers are asking.

Reads the uploads playlist, pulls comment threads per video, and keeps every
comment that looks like a question or an explicit request. Writes raw results
to JSON so the analysis can be re-run without re-spending quota.
"""
import json
import re
import sys
from collections import Counter

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

OUT = "/data/business/hca-daily/ops/viewer_questions.json"
MAX_VIDEOS = 60
COMMENTS_PER_VIDEO = 100

QUESTION_RE = re.compile(
    r"(\?|^(how|what|where|when|why|who|which|can|could|do|does|did|is|are|will|would|should|any)\b)",
    re.IGNORECASE,
)
REQUEST_RE = re.compile(
    r"\b(please (make|do|cover|talk)|can you (make|do|cover)|would love (a|to see)|"
    r"request|suggestion|idea for|next video|do a video|make a video|cover this)\b",
    re.IGNORECASE,
)


def main():
    creds = Credentials.from_authorized_user_file("/data/youtube_token.json")
    yt = build("youtube", "v3", credentials=creds)

    ch = yt.channels().list(part="contentDetails,snippet,statistics", mine=True).execute()
    item = ch["items"][0]
    uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"CHANNEL: {item['snippet']['title']}")
    print(f"  subs={item['statistics'].get('subscriberCount')} videos={item['statistics'].get('videoCount')}")

    # 1) collect recent video ids
    vids, page = [], None
    while len(vids) < MAX_VIDEOS:
        r = yt.playlistItems().list(
            part="contentDetails", playlistId=uploads, maxResults=50, pageToken=page
        ).execute()
        vids += [i["contentDetails"]["videoId"] for i in r["items"]]
        page = r.get("nextPageToken")
        if not page:
            break
    vids = vids[:MAX_VIDEOS]
    print(f"\nscanning {len(vids)} most recent uploads for comments...")

    # 2) video metadata
    meta = {}
    for i in range(0, len(vids), 50):
        batch = vids[i : i + 50]
        vr = yt.videos().list(part="snippet,statistics", id=",".join(batch)).execute()
        for v in vr["items"]:
            meta[v["id"]] = {
                "title": v["snippet"]["title"],
                "published": v["snippet"]["publishedAt"][:10],
                "views": int(v["statistics"].get("viewCount", 0)),
                "comments": int(v["statistics"].get("commentCount", 0)),
            }

    total_with_comments = sum(1 for m in meta.values() if m["comments"] > 0)
    print(f"  videos with comments: {total_with_comments}/{len(meta)}")

    # 3) pull comment threads
    rows = []
    disabled = 0
    for n, vid in enumerate(vids, 1):
        if meta.get(vid, {}).get("comments", 0) == 0:
            continue
        try:
            page = None
            got = 0
            while got < COMMENTS_PER_VIDEO:
                cr = yt.commentThreads().list(
                    part="snippet,replies",
                    videoId=vid,
                    maxResults=100,
                    order="relevance",
                    textFormat="plainText",
                    pageToken=page,
                ).execute()
                for t in cr["items"]:
                    top = t["snippet"]["topLevelComment"]["snippet"]
                    rows.append({
                        "video_id": vid,
                        "video_title": meta[vid]["title"],
                        "video_views": meta[vid]["views"],
                        "author": top.get("authorDisplayName"),
                        "text": top.get("textDisplay", ""),
                        "likes": top.get("likeCount", 0),
                        "published": top.get("publishedAt", "")[:10],
                        "is_reply": False,
                    })
                    got += 1
                    for rep in t.get("replies", {}).get("comments", []):
                        rs = rep["snippet"]
                        rows.append({
                            "video_id": vid,
                            "video_title": meta[vid]["title"],
                            "video_views": meta[vid]["views"],
                            "author": rs.get("authorDisplayName"),
                            "text": rs.get("textDisplay", ""),
                            "likes": rs.get("likeCount", 0),
                            "published": rs.get("publishedAt", "")[:10],
                            "is_reply": True,
                        })
                page = cr.get("nextPageToken")
                if not page:
                    break
        except HttpError as e:
            if "commentsDisabled" in str(e) or "forbidden" in str(e).lower():
                disabled += 1
                continue
            print(f"  ! {vid}: {str(e)[:110]}")
            continue

    print(f"  commentsDisabled videos: {disabled}")
    print(f"  TOTAL comments harvested: {len(rows)}")

    # 4) keep questions + explicit requests
    qs = [r for r in rows if QUESTION_RE.search(r["text"]) or REQUEST_RE.search(r["text"])]
    print(f"  of which look like QUESTIONS/REQUESTS: {len(qs)}")

    json.dump(
        {"channel": item["snippet"]["title"], "all_comments": rows, "questions": qs, "video_meta": meta},
        open(OUT, "w"),
        indent=2,
    )
    print(f"\nwrote {OUT}")

    # quick top-line signal
    print("\n=== top videos by comment volume ===")
    for vid, m in sorted(meta.items(), key=lambda kv: -kv[1]["comments"])[:10]:
        if m["comments"]:
            print(f"  {m['comments']:5} comments | {m['views']:8} views | {m['published']} | {m['title'][:62]}")


if __name__ == "__main__":
    main()
