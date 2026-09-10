#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

# Load guard - protects against system overload
try:
    from agents.load_guard import check_load_or_exit
    check_load_or_exit(max_load=45, check_mem=True, min_free_gb=8)
except Exception as e:
    print(f"[load_guard] Warning: could not run load check: {e}")

# Assembly script for visuals with dynamic text overlays
# We use FFmpeg drawtext to overlay:
# 1. Rotating Thank You Note
# 2. Call to Action (CTA)

WORKSPACE = Path("/data/workspace")
PROJECT = WORKSPACE / "afroviolin"

def add_overlays(visual_path, audio_path, output_path, duration):
    # Overlay logic:
    # 1. Thank You Note: "Thank you for listening to Afroviolin!" (Fades in/out)
    # 2. CTA: "Subscribe for new instrumentals every week!" (Persistent or rotates)
    
    # FFmpeg drawtext complex filter string:
    # drawtext=text='Thank you for listening!':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=48:fontcolor=white:alpha='if(lt(t,3),t/3,if(lt(t,6),1,1-(t-6)/3))'
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(visual_path),
        "-i", str(audio_path),
        "-vf", (
            "drawtext=text='Thank you for listening to Afroviolin!':"
            "x=(w-text_w)/2:y=(h-text_h)/2:fontsize=64:fontcolor=white:"
            "alpha='if(lt(t,2),t/2,if(lt(t,5),1,1-(t-5)/2))',"
            "drawtext=text='Subscribe for new instrumentals every week!':"
            "x=(w-text_w)/2:y=h-100:fontsize=40:fontcolor=yellow"
        ),
        "-c:v", "libx264", "-preset", "superfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "320k",
        "-shortest",
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True)

def main():
    # Loop through tracks and re-assemble with overlay
    state_file = PROJECT / "artifacts" / "afroviolin_state.json"
    with open(state_file) as f:
        state = json.load(f)
        
    for tid, meta in state["tracks"].items():
        if meta.get("status") in ["assembled", "uploaded_unlisted", "published"]:
            visual_rel = meta.get("runway_output_url")
            if not visual_rel: continue
            
            visual_path = PROJECT / visual_rel
            audio_path = PROJECT / "artifacts" / "afroviolin_tracks" / tid / "audio.mp3"
            out_path = PROJECT / "artifacts" / "afroviolin_tracks" / tid / "final_video_branded.mp4"
            
            duration = meta["audio_features"]["duration_seconds"]
            
            print(f"Branding {tid}...")
            add_overlays(visual_path, audio_path, out_path, duration)
            meta["final_video_path"] = str(out_path.relative_to(PROJECT))
            
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
        
    print("✅ Branding complete.")

if __name__ == "__main__":
    main()
