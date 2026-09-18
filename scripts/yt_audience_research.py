#!/usr/bin/env python3
"""What is @professorashley's audience actually asking?

Two independent signals:
  1. COMMENTS  — questions real viewers left on her own videos (highest intent:
                 these people already found her and still had an unanswered question)
  2. AUTOCOMPLETE — what people type into YouTube search (demand, whether or not
                 they've ever seen her channel)

Read-only. Writes a JSON dump next to the script for follow-up work.
"""
import json
import re
import urllib.parse
import urllib.request
from collections import Counter

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = "/data/youtube_token.json"
OUT = "/data/business/hca-daily/research/audience_questions.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122 Safari/537.36"

MAX_VIDEOS = 40
COMMENTS_PER_VIDEO = 100

STOP = set("""a an the is are was were do does did can could should would will
you your yours i me my we our us they them their he she it this that these those
of to in on for with at by from as or and but if not no yes so than then there
here what when where who whom which why how about into over after before
im ive dont doesnt didnt cant wont isnt arent wasnt aint get got getting go
going want need know think make makes made really just also very much many
lot lots thing things stuff way ways one two three new like""".split())


def yt():
    creds = Credentials.from_authorized_user_file(TOKEN)
    return build("youtube", "v3", credentials=creds)


def channel_videos(api):
    ch = api.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    for _ in range(5):
        pl = api.playlistItems().list(part="contentDetails", playlistId=uploads,
                                      maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in pl["items"]]
        tok = pl.get("nextPageToken")
        if not tok:
            break
    vids = []
    for i in range(0, len(ids), 50):
        vids += api.videos().list(part="statistics,snippet",
                                  id=",".join(ids[i:i + 50])).execute()["items"]
    vids.sort(key=lambda v: int(v["statistics"].get("viewCount", 0)), reverse=True)
    return ch, vids


def is_question(text):
    t = text.strip()
    if len(t) < 12 or len(t) > 400:
        return False
    if "?" in t:
        return True
    return bool(re.match(r"^(how|what|which|where|when|why|who|can|do|does|did|is|are|"
                         r"should|would|will|any|anyone|help)\b", t.lower()))


def mine_comments(api, vids):
    rows, errors = [], 0
    for v in vids[:MAX_VIDEOS]:
        vid = v["id"]
        try:
            res = api.commentThreads().list(
                part="snippet", videoId=vid, maxResults=COMMENTS_PER_VIDEO,
                order="relevance", textFormat="plainText").execute()
        except Exception as exc:  # noqa: BLE001  (comments off / disabled / 403)
            errors += 1
            if "disabled" not in str(exc).lower() and "forbidden" not in str(exc).lower():
                print(f"  ! {vid}: {type(exc).__name__}")
            continue
        for item in res.get("items", []):
            sn = item["snippet"]["topLevelComment"]["snippet"]
            body = sn.get("textDisplay", "")
            rows.append({
                "video": v["snippet"]["title"][:70],
                "views": int(v["statistics"].get("viewCount", 0)),
                "text": body.strip(),
                "likes": int(sn.get("likeCount", 0)),
                "is_question": is_question(body),
            })
    print(f"  comments pulled: {len(rows)}  (videos with comments off/unavailable: {errors})")
    return rows


def autocomplete(seed):
    url = ("https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&hl=en&q="
           + urllib.parse.quote(seed))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        raw = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        return []
    out = []
    for m in re.finditer(r'\["([^"]{4,90})"', raw):
        s = m.group(1)
        if s.lower() != seed.lower():
            out.append(s)
    return out


def keywords(texts, n=40):
    c = Counter()
    for t in texts:
        words = re.findall(r"[a-z][a-z'\-]{2,}", t.lower())
        for w in words:
            if w not in STOP and len(w) > 2:
                c[w] += 1
        for a, b in zip(words, words[1:]):
            if a not in STOP and b not in STOP:
                c[f"{a} {b}"] += 1
    return c.most_common(n)


def main():
    api = yt()
    ch, vids = channel_videos(api)
    print(f"CHANNEL: {ch['snippet']['title'] if 'snippet' in ch else ''}")
    print(f"videos: {len(vids)}\n")

    print("Mining comments from the {0} most-viewed videos...".format(MAX_VIDEOS))
    rows = mine_comments(api, vids)
    questions = [r for r in rows if r["is_question"]]
    print(f"  of which questions: {len(questions)}\n")

    print("=" * 72)
    print("TOP QUESTIONS BY AUDIENCE AGREEMENT (likes)")
    print("=" * 72)
    for r in sorted(questions, key=lambda x: x["likes"], reverse=True)[:25]:
        txt = " ".join(r["text"].split())[:150]
        print(f"  [{r['likes']:>3}👍 {r['views']:>7}v] {txt}")

    print("\n" + "=" * 72)
    print("RECURRING THEMES IN QUESTIONS")
    print("=" * 72)
    for kw, n in keywords([r["text"] for r in questions], 30):
        print(f"  {n:>4}  {kw}")

    print("\n" + "=" * 72)
    print("YOUTUBE SEARCH SUGGESTIONS (what people actually type)")
    print("=" * 72)
    seeds = ["healthcare administration", "how to become a healthcare administrator",
             "MHA degree", "hospital administration", "healthcare management",
             "healthcare administrator salary", "MHA vs MBA", "healthcare administration job",
             "bachelors in health science", "healthcare administration career change"]
    ac = {}
    for s in seeds:
        got = autocomplete(s)
        ac[s] = got
        print(f"\n  seed: {s!r}")
        for g in got[:10]:
            print(f"     - {g}")

    allac = [g for v in ac.values() for g in v]
    print("\n" + "=" * 72)
    print("TOP AUTOCOMPLETE THEMES")
    print("=" * 72)
    for kw, n in keywords(allac, 25):
        print(f"  {n:>4}  {kw}")

    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"comments": rows, "questions": questions,
               "autocomplete": ac, "keywords": keywords([r["text"] for r in questions], 60)},
              open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
