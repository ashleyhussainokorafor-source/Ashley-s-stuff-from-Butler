#!/usr/bin/env python3
"""
Afroviolin Batch Process Worker (Refactored)
Uses agents/dispatcher.py for multi-channel support.
"""

import os
import subprocess
import json
import sys
from pathlib import Path

# Load guard - protects against system overload
try:
    from agents.load_guard import check_load_or_exit
    check_load_or_exit(max_load=45, check_mem=True, min_free_gb=8)
except Exception as e:
    print(f"[load_guard] Warning: could not run load check: {e}")

# Add project root to path to import dispatcher
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from agents.dispatcher import get_youtube_service
from googleapiclient.http import MediaFileUpload

def process_track(track_id: str, profile_name: str = "afroviolin_v1"):
    """
    Processes a single track: encodes video and uploads to specified channel profile.
    """
    base_dir = f"/data/workspace/afroviolin/artifacts/afroviolin_tracks/{track_id}"
    
    # Find the visual file
    try:
        visual_file = next((f for f in os.listdir(base_dir) if f.endswith(".mp4") and not f.startswith("final")), None)
    except FileNotFoundError:
        return f"SKIP: Directory not found for {track_id}"

    audio_file = os.path.join(base_dir, "audio.mp3")
    output_file = os.path.join(base_dir, "final_video_fixed.mp4")
    
    if not visual_file:
        return f"SKIP: No visual for {track_id}"
    
    # 1. Run verified FFmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", os.path.join(base_dir, visual_file),
        "-i", audio_file,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "320k",
        "-shortest",
        output_file
    ]
    subprocess.run(cmd, check=True)
    
    # 2. Upload to YT using Dispatcher
    # This replaces the hardcoded token loading
    youtube = get_youtube_service(profile_name)
    
    media = MediaFileUpload(output_file, mimetype='video/mp4', resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body={
            'snippet': {'title': f'Afroviolin Track {track_id}', 'description': 'Branded and re-encoded (Strict Sync)', 'categoryId': '10'},
            'status': {'privacyStatus': 'unlisted'}
        },
        media_body=media
    )
    response = request.execute()
    return response["id"]

if __name__ == "__main__":
    # Example usage with profile flag
    # python agents/batch_process_worker.py --profile afroviolin_v1 <track_id>
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("track_id", help="The track ID to process.")
    parser.add_argument("--profile", default="afroviolin_v1", help="Channel profile from config/channels.json")
    args = parser.parse_args()
    
    try:
        vid_id = process_track(args.track_id, args.profile)
        print(f"SUCCESS: {args.track_id} -> {vid_id}")
    except Exception as e:
        print(f"ERROR: {args.track_id} -> {str(e)}")