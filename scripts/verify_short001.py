import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth.transport.requests

tok = json.load(open('/data/youtube_token.json'))
creds = Credentials(token=tok['token'], refresh_token=tok.get('refresh_token'),
    token_uri=tok.get('token_uri'), client_id=tok.get('client_id'),
    client_secret=tok.get('client_secret'), scopes=tok.get('scopes'))
if not creds.valid:
    creds.refresh(google.auth.transport.requests.Request())
yt = build('youtube', 'v3', credentials=creds)

VID = 'HHAiukzmPs8'
v = yt.videos().list(part='status,snippet,contentDetails,statistics', id=VID).execute()['items'][0]
print('TITLE      :', v['snippet']['title'])
print('PRIVACY    :', v['status']['privacyStatus'], '| uploadStatus:', v['status']['uploadStatus'])
print('CATEGORY   :', v['snippet']['categoryId'])
print('DURATION   :', v['contentDetails']['duration'])
print('PUBLISHED  :', v['snippet']['publishedAt'])
print('WATCH URL  : https://www.youtube.com/watch?v=' + VID)
print('--- DESCRIPTION, exactly as YouTube stores it ---')
print(v['snippet']['description'])
print('--- line 1 ---')
print(repr(v['snippet']['description'].splitlines()[0]))
