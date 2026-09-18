#!/usr/bin/env python3
"""Quality gate (no vision provider available): compute the bright-text bounding
box of every rendered frame via ffmpeg-decoded pixels and assert it sits inside
the Shorts safe zones (y 380..1450) with margins, and that the frame isn't blank."""
import subprocess, glob, os, json

OUT = "/data/business/hca-daily/redesign/short/short001"
W, H = 1080, 1920
SAFE_TOP, SAFE_BOT = 380, 1450   # critical text must sit between these
LUM_TH = 95                      # catches white/gold/teal-light text, excludes navy bg

def bright_bbox(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True).stdout
    assert len(raw) == W * H * 3, f"bad decode {path}: {len(raw)}"
    minx, miny, maxx, maxy = W, H, -1, -1
    px = raw  # rgb24
    for y in range(0, H, 2):
        row = y * W * 3
        for x in range(0, W, 2):
            i = row + x * 3
            r, g, b = px[i], px[i+1], px[i+2]
            lum = 0.2126*r + 0.7152*g + 0.0722*b
            if lum > LUM_TH:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    return (minx, miny, maxx, maxy)

report = []
for p in sorted(glob.glob(os.path.join(OUT, "frame*.png"))):
    name = os.path.basename(p)
    minx, miny, maxx, maxy = bright_bbox(p)
    if maxx < 0:
        report.append((name, "BLANK"))
        continue
    inside_vert = miny >= SAFE_TOP - 6 and maxy <= SAFE_BOT + 6
    not_top_overlay = miny >= 320      # nothing in top ~17% overlay band
    not_bot_overlay = maxy <= 1560     # nothing in bottom ~19% overlay band
    margins_x = minx >= 30 and maxx <= W - 30
    ok = inside_vert and not_top_overlay and not_bot_overlay and margins_x
    report.append((name, f"box x[{minx}..{maxx}] y[{miny}..{maxy}] vert_safe={inside_vert} "
                         f"top_ok={not_top_overlay} bot_ok={not_bot_overlay} x_ok={margins_x} -> {'PASS' if ok else 'FAIL'}"))

for name, r in report:
    print(name, r)
fails = [r for r in report if r[1].startswith("BLANK") or "FAIL" in r[1]]
print("\nRESULT:", "ALL PASS" if not fails else f"{len(fails)} PROBLEM(S)")