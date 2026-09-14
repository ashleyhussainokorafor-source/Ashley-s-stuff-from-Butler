import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests

tok = json.load(open("/data/youtube_token.json"))
creds = Credentials(
    token=tok["token"], refresh_token=tok.get("refresh_token"),
    token_uri=tok.get("token_uri"), client_id=tok.get("client_id"),
    client_secret=tok.get("client_secret"), scopes=tok.get("scopes"),
)
if not creds.valid:
    creds.refresh(google.auth.transport.requests.Request())

api = build("youtube", "v3", credentials=creds)

body = {
    "snippet": {
        "title": "Stop Saying \"I'd Improve Productivity\" — Get Interview-Fluent in 90 Seconds #Shorts",
        "description": (
            "Healthcare hiring execs want the numbers — wRVUs, days in A/R, no-show rates — not empty promises.\n\n"
            "Take the free 90-second scorecard, then master the 4 metrics that get candidates hired, 5 minutes a day.\n\n"
            "👉 https://thehcadaily.com/scorecard\n\n"
            "#HealthcareAdministration #CareerTips #InterviewPrep #RevenueCycle #Healthcare"
        ),
        "tags": ["healthcare administration", "healthcare career", "interview prep", "wRVU", "days in A/R", "revenue cycle", "resume", "healthcare management", "HCA"],
        "categoryId": "27",
    },
    "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
}

media = MediaFileUpload("/data/business/hca-daily/redesign/short/hca-launch-short.mp4", chunksize=-1, resumable=True)
req = api.videos().insert(part="snippet,status", body=body, media_body=media)
print("uploading...", flush=True)
resp = req.execute()
vid = resp["id"]
print("UPLOADED:", vid)
print("URL: https://www.youtube.com/shorts/" + vid)
# save id for later
json.dump({"videoId": vid}, open("/data/business/hca-daily/redesign/short/last_upload.json", "w"))
print("channel:", resp["snippet"]["channelId"])