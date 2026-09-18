#!/usr/bin/env python3
"""Read-only: show the live description of the channel's top-viewed videos."""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('/data/youtube_token.json')
yt = build('youtube', 'v3', credentials=creds)

ch = yt.channels().list(part='contentDetails', mine=True).execute()['items'][0]
uploads = ch['contentDetails']['relatedPlaylists']['uploads']

ids, tok = [], None
for _ in range(4):
    pl = yt.playlistItems().list(part='contentDetails', playlistId=uploads,
                                 maxResults=50, pageToken=tok).execute()
    ids += [i['contentDetails']['videoId'] for i in pl['items']]
    tok = pl.get('nextPageToken')
    if not tok:
        break

vids = []
for i in range(0, len(ids), 50):
    vids += yt.videos().list(part='statistics,snippet', id=','.join(ids[i:i + 50])).execute()['items']

top = sorted(vids, key=lambda v: int(v['statistics'].get('viewCount', 0)), reverse=True)[:4]
for v in top:
    d = v['snippet']['description']
    first = d.splitlines()[0] if d.strip() else '(EMPTY DESCRIPTION)'
    has_cta = 'thehcadaily.com' in d
    print(f"{int(v['statistics']['viewCount']):>7} views | {v['snippet']['title'][:52]}")
    print(f"        CTA present: {has_cta}")
    print(f"        line 1: {first[:90]}")
    print()
