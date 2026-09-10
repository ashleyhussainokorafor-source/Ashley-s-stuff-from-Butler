#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path

# Load guard - protects against system overload
try:
    from agents.load_guard import check_load_or_exit
    check_load_or_exit(max_load=45, check_mem=True, min_free_gb=8)
except Exception as e:
    print(f"[load_guard] Warning: could not run load check: {e}")

WORKSPACE = "/data/workspace"
PROJECT = os.path.join(WORKSPACE, "afroviolin")
STATE_FILE = os.path.join(PROJECT, "artifacts", "afroviolin_state.json")

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def main():
    print("Starting Final Assembly Stage...")
    if not os.path.exists(STATE_FILE):
        print(f"Error: State file not found at {STATE_FILE}")
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    tracks = state.get("tracks", {})
    count = 0

    for tid, meta in list(tracks.items()):
        status = meta.get("status")
        # Process only tracks that are ready for approval or already approved, but don't have final video
        if status == "visuals_ready_for_approval" or status == "approved":
            visual_path_rel = meta.get("runway_output_url")
            if not visual_path_rel:
                continue

            visual_path = os.path.join(PROJECT, visual_path_rel)
            audio_path = os.path.join(PROJECT, "artifacts", "afroviolin_tracks", tid, "audio.mp3")
            out_path = os.path.join(PROJECT, "artifacts", "afroviolin_tracks", tid, "final_video.mp4")

            # Check files exist
            if not os.path.exists(visual_path):
                print(f"[WARN] Visual file not found: {visual_path}")
                continue
            if not os.path.exists(audio_path):
                print(f"[WARN] Audio file not found: {audio_path}")
                continue

            print(f"Assembling: {meta.get('original_title') or tid}")
            try:
                duration = get_audio_duration(audio_path)
                print(f"  Audio duration: {duration:.2f}s")

                # Run FFmpeg command to loop visual and combine with audio
                # Re-encoding the video cleanly to prevent packet/timestamp corruption in loops
                cmd = [
                    "ffmpeg", "-y",
                    "-i", visual_path,
                    "-i", audio_path,
                    "-c:v", "libx264", "-preset", "superfast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "320k",
                    "-shortest",
                    out_path
                ]
                
                print(f"  Running FFmpeg...")
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Check output file
                if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                    print(f"  ✓ Success → {out_path} ({os.path.getsize(out_path)/1024/1024:.2f} MB)")
                    meta["final_video_path"] = f"artifacts/afroviolin_tracks/{tid}/final_video.mp4"
                    meta["status"] = "assembled"
                    count += 1
                else:
                    print(f"  ✗ Failed to create valid output file")

            except Exception as e:
                print(f"  ✗ Exception occurred: {e}")
                meta["status"] = "error"
                if "error_log" not in meta:
                    meta["error_log"] = []
                meta["error_log"].append({
                    "time": subprocess.run(["date", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
                    "error": str(e)
                })

    if count > 0:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        print(f"\n✅ Assembly complete: {count} videos assembled successfully.")
    else:
        print("\nNo videos were assembled.")

if __name__ == "__main__":
    main()
