#!/usr/bin/env python3
"""Fetch EVERY comment on @professorashley's channel into a local cache.

The reply engine reads this cache instead of re-hitting the API, so a reply
run costs quota only for the inserts it actually performs.

Quota: commentThreads.list = 1 unit per call. Safe to run daily.
Usage: /opt/venv/bin/python3 fetch_comments.py [--max-videos N]
"""
import argparse
import json
import os
import time

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "/data/youtube_token.json"
OUT = "/data/business/hca-daily/ops/comments_cache.json"
CHANNEL_HANDLE = "@professorashley"


def yt():
    creds = Credentials.from_authorized_user_file(TOKEN)
    return build("youtube", "v3", credentials=creds)


def all_videos(api):
    ch = api.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        pl = api.playlistItems().list(part="contentDetails", playlistId=uploads,
                                      maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in pl["items"]]
        tok = pl.get("nextPageToken")
        if not tok:
            break
    vids = []
    for i in range(0, len(ids), 50):
        vids += api.videos().list(part="snippet,statistics",
                                  id=",".join(ids[i:i + 50])).execute()["items"]
    return ch, vids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-videos", type=int, default=0)
    args = ap.parse_args()

    api = yt()
    ch, vids = all_videos(api)
    vids.sort(key=lambda v: int(v["statistics"].get("viewCount", 0)), reverse=True)
    if args.max_videos:
        vids = vids[:args.max_videos]
    print(f"channel videos: {len(vids)}")

    rows, errors, skipped = [], 0, 0
    for n, v in enumerate(vids, 1):
        vid = v["id"]
        try:
            req = api.commentThreads().list(
                part="snippet,replies", videoId=vid, maxResults=100,
                order="time", textFormat="plainText")
            while req:
                res = req.execute()
                for item in res.get("items", []):
                    top = item["snippet"]["topLevelComment"]
                    sn = top["snippet"]
                    # did the channel already reply? then don't reply again
                    replies = item.get("replies", {}).get("comments", [])
                    owner_replied = any(
                        r["snippet"].get("authorChannelId", {}).get("value")
                        == ch["id"] for r in replies)
                    rows.append({
                        "commentId": top["id"],
                        "videoId": vid,
                        "videoTitle": v["snippet"]["title"],
                        "videoViews": int(v["statistics"].get("viewCount", 0)),
                        "author": sn.get("authorDisplayName", ""),
                        "authorChannelId": sn.get("authorChannelId", {}).get("value", ""),
                        "text": sn.get("textDisplay", "").strip(),
                        "likes": int(sn.get("likeCount", 0)),
                        "publishedAt": sn.get("publishedAt", ""),
                        "totalReplyCount": item["snippet"].get("totalReplyCount", 0),
                        "ownerReplied": owner_replied,
                    })
                req = api.commentThreads().list_next(req, res)
        except HttpError as e:
            msg = str(e)
            if "disabled" in msg.lower() or "forbidden" in msg.lower():
                skipped += 1
            elif "quota" in msg.lower():
                print(f"  QUOTA HIT after {n} videos — stopping cleanly")
                break
            else:
                errors += 1
        if n % 25 == 0:
            print(f"  {n}/{len(vids)} videos, {len(rows)} comments so far")

    # drop the channel's own comments (don't reply to yourself)
    before = len(rows)
    rows = [r for r in rows if r["authorChannelId"] != ch["id"]]
    print(f"comments: {len(rows)} (dropped {before - len(rows)} of our own)")
    print(f"  videos with comments disabled: {skipped}, other errors: {errors}")
    print(f"  already replied by owner: {sum(1 for r in rows if r['ownerReplied'])}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "channelId": ch["id"], "comments": rows},
              open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()