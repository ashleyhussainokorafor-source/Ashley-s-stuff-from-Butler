#!/usr/bin/env python3
"""Upload hca-short001.mp4 as UNLISTED (never public), then verify privacyStatus."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests

VIDEO = "/data/business/hca-daily/redesign/short/short001/hca-short001.mp4"

TITLE = "MHA or MBA? You're Asking the Wrong Question #Shorts"

DESCRIPTION = (
    "Free 90-second scorecard — which one are you missing? \u2192\n"
    "https://thehcadaily.com/scorecard?utm_source=youtube&utm_medium=shorts&utm_campaign=short001\n"
    "\n"
    "Want the deeper prep?\n"
    "Interview Answer Vault \u00b7 $27 \u2192 https://thehcadaily.com/pricing\n"
    "Career Accelerator \u00b7 $297 \u2192 https://thehcadaily.com/pricing\n"
    "\n"
    "#HealthcareAdministration #MHA #MBA #HealthcareCareer #CareerAdvice #HealthCareAdmin"
)

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
        "title": TITLE,
        "description": DESCRIPTION,
        "categoryId": "27",
    },
    "status": {"privacyStatus": "unlisted", "selfDeclaredMadeForKids": False},
}

media = MediaFileUpload(VIDEO, chunksize=-1, resumable=True)
print("uploading...", flush=True)
resp = api.videos().insert(part="snippet,status", body=body, media_body=media).execute()
vid = resp["id"]
print("INSERT videoId:", vid, flush=True)

# ---- verify the on-platform state before claiming success ----
check = api.videos().list(part="status,snippet", id=vid).execute()
item = check["items"][0]
print("VERIFIED videoId :", item.get("id"))
print("VERIFIED privacy :", item.get("status", {}).get("privacyStatus"))
print("VERIFIED title   :", item.get("snippet", {}).get("title"))
print("VERIFIED category:", item.get("snippet", {}).get("categoryId"))
print("SHORTS URL:", "https://www.youtube.com/shorts/" + vid)

json.dump({"videoId": vid, "privacy": item.get("status", {}).get("privacyStatus")},
          open("/data/business/hca-daily/redesign/short/short001/last_upload.json", "w"), indent=1)
print("wrote last_upload.json")