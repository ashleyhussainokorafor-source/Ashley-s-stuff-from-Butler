#!/usr/bin/env python3
"""Render each kinetic frame of slides.html to PNG, timed to the voiceover word clock."""
import os, sys, json, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
os.environ["LD_LIBRARY_PATH"] = (
    "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu:"
    + os.environ.get("LD_LIBRARY_PATH", "")
)
CHROME = "/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
AUDIO = os.path.join(OUT, "voiceover.ogg")

# --- word clock -------------------------------------------------------------
# Full VO, 72 words (0-indexed word ids). WPS = seconds per word.
TOTAL_WORDS = 72
_dur = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", AUDIO],
    capture_output=True, text=True).stdout.strip()
AUDIO_DUR = float(_dur)
WPS = AUDIO_DUR / TOTAL_WORDS
print(f"audio duration={AUDIO_DUR:.3f}s  wps={WPS:.4f}")

# Slides: (id, start_word, end_word_exclusive, reveal_word_ids_inside)
SLIDES = [
    ("s1", 0,   8,  [3]),
    ("s2", 8,  18, [13]),
    ("s3", 18, 33, [26]),
    ("s4", 33, 49, [40]),
    ("s5", 49, 58, [54]),
    ("s6", 58, 72, [66, 69]),
]

from playwright.sync_api import sync_playwright

frames = []  # {id, file, dur}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME,
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + os.path.join(OUT, "slides.html"))
    pg.wait_for_timeout(700)

    n = 0
    for sid, start, end, reveals in SLIDES:
        bounds = [start] + reveals + [end]
        bounds = sorted(set(bounds))
        # ensure final boundary = end
        if bounds[-1] != end:
            bounds.append(end)
        for k in range(len(bounds) - 1):
            w0, w1 = bounds[k], bounds[k+1]
            dur = round(WPS * (w1 - w0), 4)
            # show only this slide; reveal elements with data-reveal <= w1
            pg.evaluate(
                f"""(() => {{
                  document.querySelectorAll('.slide').forEach(s =>
                    s.style.display = (s.id === '{sid}') ? 'block' : 'none');
                  document.querySelectorAll('[data-reveal]').forEach(el =>
                    el.style.opacity = (Number(el.dataset.reveal) <= {w1}) ? '1' : '0');
                }})()"""
            )
            pg.wait_for_timeout(120)
            n += 1
            path = os.path.join(OUT, f"frame{n:02d}.png")
            pg.query_selector(f"#{sid}").screenshot(path=path)
            frames.append({"id": f"frame{n:02d}", "file": path,
                           "dur": dur, "slide": sid, "bound": w1})
            print(f"  {sid} bound={w1:<3d} -> frame{n:02d}.png  dur={dur:.3f}s")
    b.close()

tot = sum(f["dur"] for f in frames)
print(f"TOTAL frames={len(frames)}  video_dur={tot:.3f}s  audio_dur={AUDIO_DUR:.3f}s")
manifest = os.path.join(OUT, "manifest.json")
json.dump({"audio_dur": AUDIO_DUR, "wps": WPS, "frames": frames},
          open(manifest, "w"), indent=1)
print("wrote", manifest)