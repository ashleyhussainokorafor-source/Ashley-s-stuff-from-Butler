#!/usr/bin/env python3
"""Read-only: report the true privacy/processing state of a video."""
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

vid = sys.argv[1] if len(sys.argv) > 1 else "HHAiukzmPs8"
creds = Credentials.from_authorized_user_file('/data/youtube_token.json')
yt = build('youtube', 'v3', credentials=creds)

r = yt.videos().list(part='status,snippet,processingDetails,statistics',
                     id=vid).execute()
if not r.get('items'):
    print(f"video {vid}: NOT FOUND")
    raise SystemExit(1)
v = r['items'][0]
print("title        :", v['snippet']['title'])
print("privacyStatus:", v['status'].get('privacyStatus'))
print("uploadStatus :", v['status'].get('uploadStatus'))
print("publishAt    :", v['status'].get('publishAt'))
print("madeForKids  :", v['status'].get('madeForKids'))
print("views        :", v['statistics'].get('viewCount'))
pd = v.get('processingDetails', {})
print("processing   :", pd.get('processingStatus'), pd.get('processingProgress'))
