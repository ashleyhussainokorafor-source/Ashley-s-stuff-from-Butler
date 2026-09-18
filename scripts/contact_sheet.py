#!/usr/bin/env python3
"""Build a labelled contact sheet of the image library so it can be verified
in ONE vision pass instead of 19 separate calls."""
import os
from PIL import Image, ImageDraw

D = "/data/business/hca-daily/worker/assets/img"
OUT = "/tmp/contact_sheet.jpg"
COLS, CW, CH = 4, 340, 250
PAD, LBL = 10, 26

# prefer the -800 webp variants (already web weight)
files = []
for f in sorted(os.listdir(D)):
    if f.endswith("-800.webp"):
        files.append(f)
    elif f.endswith(".webp") and not f.endswith("-800.webp"):
        base = f[:-5]
        if f"{base}-800.webp" not in os.listdir(D):
            files.append(f)

# items to check that aren't webp1600/800 pairs: use the jpg originals
for f in sorted(os.listdir(D)):
    if f.endswith(".jpg") and f"{f[:-4]}-800.webp" not in os.listdir(D):
        files.append(f)

files = sorted(set(files))
rows = (len(files) + COLS - 1) // COLS
W = COLS * (CW + PAD) + PAD
H = rows * (CH + LBL + PAD) + PAD
sheet = Image.new("RGB", (W, H), (18, 26, 38))
draw = ImageDraw.Draw(sheet)

for i, f in enumerate(files):
    r, c = divmod(i, COLS)
    x = PAD + c * (CW + PAD)
    y = PAD + r * (CH + LBL + PAD)
    try:
        im = Image.open(os.path.join(D, f)).convert("RGB")
    except Exception as e:
        print("skip", f, e)
        continue
    im.thumbnail((CW, CH), Image.LANCZOS)
    sheet.paste(im, (x + (CW - im.width) // 2, y))
    draw.text((x + 2, y + CH + 6), f"{i+1}. {f[:38]}", fill=(230, 236, 245))

sheet.save(OUT, "JPEG", quality=80)
print(f"{len(files)} images -> {OUT}  ({os.path.getsize(OUT):,} bytes)")
for i, f in enumerate(files, 1):
    print(f"  {i:>2}. {f}")