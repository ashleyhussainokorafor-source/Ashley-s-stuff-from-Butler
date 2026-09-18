#!/usr/bin/env python3
"""Optimise the generated PNGs into web-weight assets.

1.4MB PNGs would make the site crawl on mobile — which is the opposite of
"modern for a younger audience". Target: <200KB each, WebP + JPEG fallback.
"""
import os
from PIL import Image

SRC = "/tmp/genimg"
DEST = "/data/business/hca-daily/worker/assets/img"
os.makedirs(DEST, exist_ok=True)

# slug -> (target width, target height or None to keep aspect, crop mode)
PLAN = [
    ("hero-wide",          (1000, 1000), "square"),   # split-hero card
    ("hero-wide-wide",     (1600, 720),  "band"),     # full-width band
    ("study-focus",        (900, 600),   "wide"),
    ("grad-celebrate",     (900, 600),   "wide"),
    ("clinical-team",      (900, 600),   "wide"),
    ("collab-laptop",      (900, 600),   "wide"),
    ("phone-student",      (700, 900),   "portrait"),
    ("offer-moment",       (900, 600),   "wide"),
    ("portrait-confident", (700, 900),   "portrait"),
]


def crop_to(im, tw, th, mode):
    """Centre-crop to the target aspect, then resize."""
    w, h = im.size
    target_ar = tw / th
    src_ar = w / h
    if mode == "band":
        # keep the vertical middle for landscape bands
        new_h = int(w / target_ar)
        top = max(0, (h - new_h) // 2)
        im = im.crop((0, top, w, top + new_h))
    elif abs(src_ar - target_ar) > 0.01:
        if src_ar > target_ar:          # too wide -> trim sides
            new_w = int(h * target_ar)
            left = (w - new_w) // 2
            im = im.crop((left, 0, left + new_w, h))
        else:                            # too tall -> trim top/bottom
            new_h = int(w / target_ar)
            top = max(0, (h - new_h) // 2)
            im = im.crop((0, top, w, top + new_h))
    return im.resize((tw, th), Image.LANCZOS)


total = 0
for slug, (tw, th), mode in PLAN:
    src = os.path.join(SRC, f"{slug.split('-wide')[0] if slug.endswith('-wide') else slug}.png")
    if not os.path.exists(src):
        src = os.path.join(SRC, f"{slug}.png")
    if not os.path.exists(src):
        print(f"  skip {slug} (no source)")
        continue
    im = Image.open(src).convert("RGB")
    im = crop_to(im, tw, th, mode)
    webp = os.path.join(DEST, f"{slug}.webp")
    jpg = os.path.join(DEST, f"{slug}.jpg")
    im.save(webp, "WEBP", quality=82, method=5)
    im.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
    total += os.path.getsize(webp) + os.path.getsize(jpg)
    print(f"  {slug:22} {tw}x{th}  webp={os.path.getsize(webp):>7,}  jpg={os.path.getsize(jpg):>7,}")

print(f"\ntotal added weight (both formats): {total/1024/1024:.2f} MB")
print("files:")
for f in sorted(os.listdir(DEST)):
    print("   ", f, f"{os.path.getsize(os.path.join(DEST,f)):,}")