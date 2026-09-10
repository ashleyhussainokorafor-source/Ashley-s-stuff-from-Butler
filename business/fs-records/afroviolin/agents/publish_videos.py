import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

PROJECT = "/data/workspace/afroviolin"
TOKEN_FILE = os.path.join(PROJECT, "artifacts", "youtube_token.json")
STATE_FILE = os.path.join(PROJECT, "artifacts", "afroviolin_state.json")

def load_credentials():
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
    creds = Credentials(**token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def publish():
    creds = load_credentials()
    youtube = build("youtube", "v3", credentials=creds)
    
    with open(STATE_FILE) as f:
        state = json.load(f)
        
    for tid, meta in state["tracks"].items():
        if meta.get("status") == "uploaded_unlisted" and meta.get("youtube_video_id"):
            video_id = meta["youtube_video_id"]
            print(f"Publishing video {video_id} ({meta.get('original_title')})...")
            
            try:
                # Update status to public
                response = youtube.videos().update(
                    part="status",
                    body={
                        "id": video_id,
                        "status": {"privacyStatus": "public"}
                    }
                ).execute()
                
                meta["status"] = "published"
                meta["published_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                print(f"  ✓ Success: https://youtu.be/{video_id}")
            except Exception as e:
                print(f"  ✗ Failed to publish {video_id}: {e}")
                
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    publish()
