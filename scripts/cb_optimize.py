#!/usr/bin/env python3
"""Contact sheet for the Campus Brief set + web optimisation in one pass."""
import os
from PIL import Image, ImageDraw

SRC = "/tmp/campusbrief"
DEST = "/data/business/hca-daily/worker/assets/img"
os.makedirs(DEST, exist_ok=True)

names = [f for f in sorted(os.listdir(SRC)) if f.endswith(".png")]

# --- contact sheet for verification ---
COLS, CW, CH, PAD, LBL = 3, 420, 300, 10, 24
rows = (len(names) + COLS - 1) // COLS
W = COLS * (CW + PAD) + PAD
H = rows * (CH + LBL + PAD) + PAD
sheet = Image.new("RGB", (W, H), (12, 26, 40))
d = ImageDraw.Draw(sheet)
for i, n in enumerate(names):
    r, c = divmod(i, COLS)
    x = PAD + c * (CW + PAD); y = PAD + r * (CH + LBL + PAD)
    im = Image.open(os.path.join(SRC, n)).convert("RGB")
    im.thumbnail((CW, CH), Image.LANCZOS)
    sheet.paste(im, (x + (CW - im.width)//2, y))
    d.text((x + 2, y + CH + 5), f"{i+1}. {n[:-4]}", fill=(235, 240, 246))
sheet.save("/tmp/cb_sheet.jpg", "JPEG", quality=82)
print(f"contact sheet: /tmp/cb_sheet.jpg ({os.path.getsize('/tmp/cb_sheet.jpg'):,} bytes)")

# --- web-optimise: landscape 4:3 and portrait variants ---
PLAN = {
    "cb-campus-walk":      (1200, 800),
    "cb-lounge-laptop":    (1200, 800),
    "cb-mock-interview":   (1200, 800),
    "cb-whiteboard-ar":    (1200, 800),
    "cb-quiet-library":    (1600, 800),
    "cb-group-review":     (1200, 800),
}

def cover(im, tw, th):
    w, h = im.size
    tar = tw / th
    if w / h > tar:
        nw = int(h * tar); im = im.crop(((w - nw)//2, 0, (w - nw)//2 + nw, h))
    else:
        nh = int(w / tar); im = im.crop((0, (h - nh)//2, w, (h - nh)//2 + nh))
    return im.resize((tw, th), Image.LANCZOS)

print("\n=== optimised web assets ===")
tot = 0
for slug, (tw, th) in PLAN.items():
    src = os.path.join(SRC, f"{slug}.png")
    if not os.path.exists(src):
        continue
    im = cover(Image.open(src).convert("RGB"), tw, th)
    for ext in ("webp", "jpg"):
        p = os.path.join(DEST, f"{slug}.{ext}")
        if ext == "webp":
            im.save(p, "WEBP", quality=84, method=5)
        else:
            im.save(p, "JPEG", quality=84, optimize=True, progressive=True)
        tot += os.path.getsize(p)
    # small variant for cards / mobile
    sm = im.resize((tw // 2, th // 2), Image.LANCZOS)
    p = os.path.join(DEST, f"{slug}-sm.webp")
    sm.save(p, "WEBP", quality=82, method=5)
    tot += os.path.getsize(p)
    print(f"  {slug:22} {tw}x{th}  webp={os.path.getsize(DEST+'/'+slug+'.webp'):>7,}")
print(f"\ntotal added: {tot/1024/1024:.2f} MB")