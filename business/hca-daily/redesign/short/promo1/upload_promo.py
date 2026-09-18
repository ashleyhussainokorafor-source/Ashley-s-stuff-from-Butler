#!/usr/bin/env python3
"""Upload the HCA promo Short as UNLISTED for owner review."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests

VIDEO = "/data/business/hca-daily/redesign/short/promo1/hca-promo-short.mp4"

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
        "title": 'Nobody Gets Hired for Saying "I\'m a People Person" #Shorts',
        "description": (
            'Healthcare execs hear "I\'m a people person" 200 times a year. '
            "They hire the people who can say wRVUs, days in A/R, and no-show rate.\n\n"
            "Find the metric gap that's costing you interviews — free, 90 seconds:\n"
            "👉 https://thehcadaily.com/scorecard\n\n"
            "#HealthcareAdministration #HealthcareCareers #InterviewPrep "
            "#RevenueCycle #HealthcareLeadership #HCA"
        ),
        "tags": ["healthcare administration", "healthcare career", "interview prep",
                 "wRVU", "days in A/R", "no-show rate", "revenue cycle",
                 "healthcare management", "HCA", "career advice"],
        "categoryId": "27",
    },
    # UNLISTED until the owner approves
    "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
}

media = MediaFileUpload(VIDEO, chunksize=-1, resumable=True)
print("uploading...", flush=True)
resp = api.videos().insert(part="snippet,status", body=body, media_body=media).execute()
vid = resp["id"]
print("UPLOADED (unlisted):", vid)
print("PREVIEW: https://www.youtube.com/watch?v=" + vid)
print("SHORTS : https://www.youtube.com/shorts/" + vid)
json.dump({"videoId": vid, "privacy": "unlisted"},
          open("/data/business/hca-daily/redesign/short/promo1/last_upload.json", "w"), indent=1)
