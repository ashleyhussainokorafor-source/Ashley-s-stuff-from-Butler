#!/usr/bin/env python3
"""Generate site imagery via OpenRouter image models.

No dedicated image-gen key exists on this host; OpenRouter's image-output models
(gemini-*-image) are the available path.

Usage:  python3 gen_images.py out_dir  (edit PROMPTS below)
Writes <slug>.png per prompt and prints the real cost from the response.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

ENV = "/data/.env"
KEY = ""
for line in open(ENV):
    if line.strip().startswith("OPENROUTER_API_KEY="):
        KEY = line.strip().split("=", 1)[1].strip().strip('"').strip("'")

MODEL = "google/gemini-2.5-flash-image"

# Shared style so every image belongs to the same brand world.
STYLE = (
    "Photorealistic editorial photograph, natural window light, slightly warm tone, "
    "shallow depth of field, shot on 35mm, documentary candid feel — NOT a stiff corporate "
    "stock pose. Genuine smiles, real emotion. Modern university campus or modern outpaient "
    "clinic setting. Colour palette leans navy blue and teal with warm golden highlights. "
    "Diverse group: Black, South Asian, East Asian, Latina/o and white young adults, "
    "ages 19-25. No text, no logos, no watermarks in the image. "
)

PROMPTS = [
    ("hero-students",
     STYLE + "A joyful group of five diverse college students walking together across a sunny "
     "campus quad, laughing mid-conversation, one carrying a laptop, backpacks on. "
     "Wide shot, they fill the frame, energy and motion."),
    ("study-focus",
     STYLE + "A young Black woman in her early twenties studying at a library table with a "
     "laptop and notebook, focused and quietly confident, warm light across her face. "
     "Medium close-up, shallow depth of field."),
    ("grad-celebrate",
     STYLE + "A young South Asian woman in a graduation gown throwing her cap, laughing with "
     "pure joy, campus building blurred behind her. Mid-shot, golden hour."),
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/genimg"
    os.makedirs(out, exist_ok=True)
    total = 0.0
    for slug, prompt in PROMPTS:
        body = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image", "text"],
        }).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=body,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  FAIL {slug}: HTTP {e.code} {e.read().decode()[:200]}")
            continue

        msg = res["choices"][0]["message"]
        imgs = msg.get("images") or []
        cost = (res.get("usage") or {}).get("cost")
        if cost:
            total += float(cost)
        if not imgs:
            print(f"  FAIL {slug}: no image in response. keys={list(msg.keys())}")
            continue
        url = imgs[0].get("image_url", {}).get("url", "")
        if "," in url:
            b64 = url.split(",", 1)[1]
            path = os.path.join(out, f"{slug}.png")
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64))
            print(f"  ok   {slug}.png  {os.path.getsize(path):,} bytes   cost=${cost}")
        else:
            print(f"  ?    {slug}: non-data url {url[:80]}")
    print(f"\ntotal cost: ${total:.4f}")


if __name__ == "__main__":
    main()