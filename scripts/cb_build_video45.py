#!/usr/bin/env python3
"""Render the Campus Brief hero loop to spec: 1080x1350 (4:5), 30fps, 10.0s,
H.264 yuv420p, NO audio track, seamless loop, plus a poster of the 6-9s moment.

Discrete frames assembled with ffmpeg — never a real-time screen recording
(that OOMs this box). Frames are JPEG to keep the working set small.
"""
import glob
import os
import shutil
import subprocess

STAGE = "/tmp/cbvideo/stage45.html"
WORK = "/tmp/cb45"
FPS, DUR = 30, 10.0
N = int(FPS * DUR)                      # 300 frames
OUTDIR = "/data/business/hca-daily/worker/assets/img"
MP4 = os.path.join(OUTDIR, "cb-drill-loop.mp4")
POSTER = os.path.join(OUTDIR, "cb-drill-poster.jpg")

shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK, exist_ok=True)

os.environ["LD_LIBRARY_PATH"] = (
    "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu:"
    + os.environ.get("LD_LIBRARY_PATH", ""))
from playwright.sync_api import sync_playwright

print(f"rendering {N} frames at {FPS}fps ({DUR}s)...")
with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.goto("file://" + STAGE)
    pg.wait_for_timeout(1000)
    for i in range(N):
        t = i / FPS
        pg.evaluate(f"renderAt({t})")
        pg.screenshot(path=os.path.join(WORK, f"f{i:03d}.jpg"),
                      type="jpeg", quality=92)
        if i % 60 == 0:
            print(f"  frame {i}/{N}  (t={t:.2f}s)")
    # poster = the 6-9s "insight" moment
    pg.evaluate("renderAt(7.0)")
    pg.wait_for_timeout(120)
    pg.screenshot(path=POSTER, type="jpeg", quality=88)
    b.close()

print("poster written:", POSTER, f"{os.path.getsize(POSTER):,} bytes")

# assemble
print("assembling...")
r = subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
    "-framerate", str(FPS), "-i", os.path.join(WORK, "f%03d.jpg"),
    "-c:v", "libx264", "-preset", "slow", "-crf", "21",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
    "-an",                                   # NO audio track, per spec
    MP4,
], capture_output=True, text=True)
if r.returncode != 0:
    print("ffmpeg FAILED:", r.stderr[:800])
else:
    print(f"  ok {MP4}  {os.path.getsize(MP4):,} bytes")

# verify against spec
v = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration,size", "-show_entries",
                    "stream=codec_name,width,height,r_frame_rate,nb_frames",
                    "-of", "default=noprint_wrappers=1", MP4],
                   capture_output=True, text=True)
print("\n=== ffprobe ===")
print(v.stdout.strip())

# loop-seam check: mean luma of first vs last frame should be close
def luma(path):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", "scale=64:64",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True)
    d = out.stdout
    return sum(d)/len(d) if d else -1

print("\n=== loop-seam check ===")
print(f"  frame 000 luma: {luma(os.path.join(WORK,'f000.jpg')):.1f}")
print(f"  frame 299 luma: {luma(os.path.join(WORK,'f299.jpg')):.1f}  (close = seamless)")
print(f"  peak  (f210)  luma: {luma(os.path.join(WORK,'f210.jpg')):.1f}")