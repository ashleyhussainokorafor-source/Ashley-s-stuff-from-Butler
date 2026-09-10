#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path

# Config
WORKSPACE = Path("/data/workspace")
PROJECT = WORKSPACE / "afroviolin"
STATE_FILE = PROJECT / "artifacts" / "afroviolin_state.json"
AGENT_BRAND = PROJECT / "agents" / "brand_videos.py"
AGENT_UPLOAD = PROJECT / "agents" / "upload_to_youtube.py"

def main():
    with open(STATE_FILE) as f:
        state = json.load(f)

    # Filter tracks that need branding or re-upload
    for tid, meta in state["tracks"].items():
        # Goal: Assemble -> Branded -> Uploaded
        if meta.get("status") in ["assembled", "uploaded_unlisted", "published"]:
            # Skip if we already have the branded version
            branded_path = PROJECT / "artifacts" / "afroviolin_tracks" / tid / "final_video_branded.mp4"
            if branded_path.exists():
                continue
            
            print(f"--- Processing {tid} ---")
            
            # Step 1: Brand it
            try:
                subprocess.run([sys.executable, str(AGENT_BRAND)], check=True)
            except Exception as e:
                print(f"Branding failed: {e}")
                continue

            # Step 2: Upload it
            try:
                subprocess.run([sys.executable, str(AGENT_UPLOAD)], check=True)
            except Exception as e:
                print(f"Upload failed: {e}")
                continue

    print("Sequential batch complete.")

if __name__ == "__main__":
    import sys
    main()
