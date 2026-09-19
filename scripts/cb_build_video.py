#!/usr/bin/env python3
"""Render the drill states, then assemble the 10-second hero loop + poster.

State durations total exactly 10.0s. No voiceover: the metric, the tap and the
one-line insight carry it. Silent + looping, so it can autoplay in the hero.
"""
import os
import subprocess

STAGE = "/tmp/cbvideo/stage.html"
OUT = "/tmp/cbvideo"
os.makedirs(OUT, exist_ok=True)

# (state, seconds)
PLAN = [
    ("question", 2.0),
    ("hover1",   0.8),
    ("tap1",     0.4),
    ("wrong",    0.8),
    ("hover2",   0.8),
    ("answer",   1.4),
    ("insight",  2.8),
    ("settle",   1.0),
]
print("total duration:", sum(d for _, d in PLAN), "s")

# ---- 1. render each state with Playwright ----
os.environ["LD_LIBRARY_PATH"] = (
    "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu:"
    + os.environ.get("LD_LIBRARY_PATH", ""))
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1200, "height": 860})
    pg.goto("file://" + STAGE)
    pg.wait_for_timeout(900)
    frames = []
    for i, (state, _) in enumerate(PLAN):
        pg.evaluate(f"setState('{state}')")
        pg.wait_for_timeout(320)
        f = os.path.join(OUT, f"f{i}.png")
        pg.screenshot(path=f)
        frames.append(f)
        print(f"  rendered {state:9} -> f{i}.png")
    b.close()

# ---- 2. concat list with per-frame duration ----
lst = os.path.join(OUT, "list.txt")
with open(lst, "w") as fh:
    for f, (_, d) in zip(frames, PLAN):
        fh.write(f"file '{f}'\nduration {d}\n")
    fh.write(f"file '{frames[-1]}'\n")   # repeat last so the tail isn't clipped

# ---- 3. assemble: silent, 30fps, gentle slow zoom for life ----
mp4 = "/data/business/hca-daily/worker/assets/img/cb-drill-loop.mp4"
cmd = [
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-f", "concat", "-safe", "0", "-i", lst,
    "-vf", "fps=30,scale=1200:860,zoompan=z='min(zoom+0.00035,1.035)':d=1:"
           "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1200x860,fade=t=in:st=0:d=0.5,format=yuv420p",
    "-t", "10", "-an",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20",
    "-movflags", "+faststart", "-pix_fmt", "yuv420p",
    mp4,
]
print("\nassembling video...")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ffmpeg FAILED:\n", r.stderr[:900])
else:
    print("  ok", mp4, f"{os.path.getsize(mp4):,} bytes")

# ---- 4. poster frame (first state) for LCP ----
poster = "/data/business/hca-daily/worker/assets/img/cb-drill-poster.jpg"
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", frames[0], "-vf", "scale=1000:-2",
                "-q:v", "4", poster], check=False)
print("  poster:", poster, f"{os.path.getsize(poster):,} bytes" if os.path.exists(poster) else "MISSING")

# ---- 5. verify with ffprobe ----
v = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration,size", "-show_entries",
                    "stream=codec_name,width,height,r_frame_rate",
                    "-of", "default=noprint_wrappers=1", mp4],
                   capture_output=True, text=True)
print("\n=== ffprobe ===")
print(v.stdout.strip())