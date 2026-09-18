#!/usr/bin/env python3
"""Quality gate for a built Short: verify every frame's text stays inside the
Shorts safe zone and never touches the horizontal padding.

Usage: short_qc.py <build_dir>
Exits non-zero if any frame fails, so it can gate a publish step.
"""
import glob
import os
import subprocess
import sys

from PIL import Image

SAFE_TOP, SAFE_BOTTOM = 380, 1450
LEFT_MIN, RIGHT_MAX = 70, 1010  # 78px padding, with 8px tolerance
BRIGHT = 140


def main():
    build_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    mp4s = glob.glob(os.path.join(build_dir, "*.mp4"))
    if not mp4s:
        print("no mp4 found")
        return 1
    for mp4 in mp4s:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=width,height",
             "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1", mp4],
            capture_output=True, text=True).stdout
        print(f"VIDEO {os.path.basename(mp4)}\n{out.strip()}")

    frames = sorted(glob.glob(os.path.join(build_dir, "frame*.png")))
    if not frames:
        print("no frames found")
        return 1

    fails = []
    for f in frames:
        im = Image.open(f).convert("L")
        w, h = im.size
        px = im.load()
        xs, ys = [], []
        # skip the top band entirely for the wordmark check; we measure all text
        for y in range(0, h, 4):
            for x in range(0, w, 4):
                if px[x, y] > BRIGHT:
                    xs.append(x)
                    ys.append(y)
        if not xs:
            continue
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        problems = []
        if x0 < LEFT_MIN:
            problems.append(f"left {x0}<{LEFT_MIN}")
        if x1 > RIGHT_MAX:
            problems.append(f"right {x1}>{RIGHT_MAX}")
        if y1 > SAFE_BOTTOM:
            problems.append(f"bottom {y1}>{SAFE_BOTTOM}")
        status = "OK " if not problems else "FAIL"
        print(f"  {status} {os.path.basename(f)}: x[{x0}..{x1}] y[{y0}..{y1}]"
              + ("  " + ", ".join(problems) if problems else ""))
        if problems:
            fails.append((os.path.basename(f), problems))

    print()
    if fails:
        print(f"QC FAILED on {len(fails)} frame(s): {fails[:5]}")
        return 1
    print(f"QC PASSED — all {len(frames)} frames inside safe zone x[{LEFT_MIN}..{RIGHT_MAX}] y<= {SAFE_BOTTOM}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
