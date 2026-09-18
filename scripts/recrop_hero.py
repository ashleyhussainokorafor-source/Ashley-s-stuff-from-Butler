#!/usr/bin/env python3
"""Re-crop the hero image: remove dead sky/building from the top so the
students fill the frame, and emit the sizes the hero card actually uses."""
import os
from PIL import Image

SRC = "/tmp/genimg/hero-wide.png"
DEST = "/data/business/hca-daily/worker/assets/img"

im = Image.open(SRC).convert("RGB")
w, h = im.size
print("source:", im.size)

# Students sit in the lower ~78%; drop the empty upper band.
crop_top = int(h * 0.20)
im2 = im.crop((0, crop_top, w, h))
print("after crop:", im2.size, "aspect", round(im2.width / im2.height, 3))

# Emit at 1000 wide, 5:4 (matches the new CSS aspect-ratio)
target_w, target_h = 1000, 800
im2 = im2.resize((target_w, target_h), Image.LANCZOS)
for ext, kw in (("webp", dict(quality=84, method=5)),
                ("jpg", dict(quality=84, optimize=True, progressive=True))):
    p = os.path.join(DEST, f"hero-wide.{ext}")
    im2.save(p, ext.upper() if ext == "jpg" else "WEBP", **kw)
    print(f"  {p}  {os.path.getsize(p):,} bytes")