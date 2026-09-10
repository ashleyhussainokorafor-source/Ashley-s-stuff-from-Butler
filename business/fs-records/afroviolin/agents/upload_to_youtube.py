#!/usr/bin/env python3
import os
import json
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

WORKSPACE = "/data/workspace"
PROJECT = os.path.join(WORKSPACE, "afroviolin")
TOKEN_FILE = os.path.join(PROJECT, "artifacts", "youtube_token.json")
STATE_FILE = os.path.join(PROJECT, "artifacts", "afroviolin_state.json")

def load_credentials():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"Credentials token not found at {TOKEN_FILE}")
        
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
        
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes")
    )
    
    if creds.expired and creds.refresh_token:
        print("OAuth token expired, refreshing...")
        creds.refresh(Request())
        # Update token file with refreshed token
        token_data["token"] = creds.token
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
            
    return creds

def upload_video(youtube, file_path, title, description, tags):
    print(f"Uploading file: {file_path}")
    print(f"Title: {title}")
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10"  # Category 10 is Music
        },
        "status": {
            "privacyStatus": "unlisted"  # Standard pipeline is unlisted first
        }
    }
    
    media = MediaFileUpload(
        file_path,
        mimetype="video/mp4",
        chunksize=1024*1024*5,  # 5MB chunks
        resumable=True
    )
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")
            
    video_id = response.get("id")
    print(f"  ✓ Upload Successful! Video ID: {video_id}")
    return video_id

def main():
    try:
        creds = load_credentials()
        youtube = build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"Authentication failed: {e}")
        return
        
    if not os.path.exists(STATE_FILE):
        print(f"Error: State file not found at {STATE_FILE}")
        return
        
    with open(STATE_FILE) as f:
        state = json.load(f)
        
    tracks = state.get("tracks", {})
    uploaded_count = 0
    
    for tid, meta in list(tracks.items()):
        status = meta.get("status")
        if status == "assembled":
            title = meta.get("generated_metadata", {}).get("youtube_title") or meta.get("original_title") or f"Afroviolin Track {tid}"
            description = meta.get("generated_metadata", {}).get("description", "")
            tags = meta.get("generated_metadata", {}).get("tags", [])
            
            video_path_rel = meta.get("final_video_path")
            if not video_path_rel:
                print(f"[WARN] Assembled track {tid} has no final_video_path set.")
                continue
                
            video_path = os.path.join(PROJECT, video_path_rel)
            if not os.path.exists(video_path):
                print(f"[WARN] Assembled video file not found at: {video_path}")
                continue
                
            print(f"\n{'='*60}")
            print(f"Starting Upload for: {title}")
            print(f"{'='*60}")
            
            try:
                video_id = upload_video(youtube, video_path, title, description, tags)
                
                # Update state
                meta["youtube_video_id"] = video_id
                meta["uploaded_at"] = datetime.datetime.utcnow().isoformat() + "Z"
                meta["status"] = "uploaded_unlisted"
                uploaded_count += 1
                
                # Save state after each successful upload to avoid re-uploading on failures
                with open(STATE_FILE, "w") as f:
                    json.dump(state, f, indent=2)
                    
            except HttpError as e:
                print(f"  ✗ Google API HTTP Error uploading track {tid}: {e}")
                # Check for quota errors
                try:
                    err_reason = json.loads(e.content.decode("utf-8")).get("error", {}).get("errors", [{}])[0].get("reason", "")
                    if err_reason == "quotaExceeded":
                        print("  🔴 CRITICAL: YouTube API Daily Quota Exceeded. Stopping batch uploads.")
                        break
                except Exception:
                    pass
            except Exception as e:
                print(f"  ✗ General Error uploading track {tid}: {e}")
                
    print(f"\n✅ Upload process complete. {uploaded_count} tracks uploaded to YouTube.")

if __name__ == "__main__":
    main()
