#!/usr/bin/env python3
"""Read-only snapshot of the @professorashley channel: size + recent performance."""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

try:
    creds = Credentials.from_authorized_user_file('/data/youtube_token.json')
    yt = build('youtube', 'v3', credentials=creds)
    ch = yt.channels().list(part='snippet,statistics,contentDetails', mine=True).execute()
    if not ch.get('items'):
        print("NO CHANNEL RETURNED (token may lack the right scope)")
        raise SystemExit
    c = ch['items'][0]
    st = c['statistics']
    print("CHANNEL:", c['snippet']['title'])
    print("  subs:", st.get('subscriberCount'),
          "| videos:", st.get('videoCount'),
          "| lifetime views:", st.get('viewCount'))

    uploads = c['contentDetails']['relatedPlaylists']['uploads']
    items, tok = [], None
    for _ in range(4):
        pl = yt.playlistItems().list(part='contentDetails', playlistId=uploads,
                                     maxResults=50, pageToken=tok).execute()
        items += pl['items']
        tok = pl.get('nextPageToken')
        if not tok:
            break
    ids = [i['contentDetails']['videoId'] for i in items]
    print("  uploads fetched:", len(ids))

    vids = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part='statistics,snippet', id=','.join(ids[i:i + 50])).execute()
        vids += r['items']
    vids.sort(key=lambda v: v['snippet']['publishedAt'], reverse=True)

    print("\n  LAST 12 UPLOADS:")
    for v in vids[:12]:
        print(f"    {v['snippet']['publishedAt'][:10]}  "
              f"{int(v['statistics'].get('viewCount', 0)):>7} views  "
              f"{v['snippet']['title'][:60]}")

    recent = [v for v in vids if v['snippet']['publishedAt'] > '2026-08-01']
    print(f"\n  uploaded since Aug 1 2026: {len(recent)}")
    print(f"  views on those: {sum(int(v['statistics'].get('viewCount', 0)) for v in recent)}")

    top = sorted(vids, key=lambda v: int(v['statistics'].get('viewCount', 0)), reverse=True)[:8]
    print("\n  TOP 8 BY VIEWS:")
    for v in top:
        print(f"    {int(v['statistics'].get('viewCount', 0)):>7} views  "
              f"{v['snippet']['publishedAt'][:10]}  {v['snippet']['title'][:56]}")
except Exception as e:  # noqa: BLE001
    print("YT ERROR:", type(e).__name__, str(e)[:400])
