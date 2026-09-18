#!/usr/bin/env python3
"""Full brand image set for the HCA Daily site refresh.

Shared STYLE string keeps every photo in one visual world so the site reads as
a single brand rather than a stock-photo grab bag.
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

STYLE = (
    "Photorealistic editorial photograph, natural light, slightly warm tone, shallow depth "
    "of field, 35mm documentary candid feel — NOT a stiff corporate stock pose. Genuine "
    "unposed emotion. Modern university campus or contemporary outpatient clinic. Palette "
    "leans navy blue, teal and warm gold. Racially diverse: Black, South Asian, East Asian, "
    "Latina/o and white young adults aged 19-25. No text, no logos, no watermarks. "
)

PROMPTS = [
    ("hero-wide", STYLE +
     "WIDE 16:9 COMPOSITION. Five diverse college students walking toward camera together "
     "across a bright modern campus walkway, mid-laughter, one holding a laptop, backpacks on. "
     "They fill the frame. Golden-hour rim light. Energetic, aspirational."),
    ("clinical-team", STYLE +
     "Three young diverse healthcare administration professionals in smart casual clothes "
     "talking in a bright modern hospital corridor, one holding a tablet, confident and "
     "collaborative. Mid-shot, motion and warmth."),
    ("collab-laptop", STYLE +
     "Four diverse students crowded around a laptop at a sunny table, pointing at the screen, "
     "laughing at something together. Seen slightly from above. Warm, communal, candid."),
    ("phone-student", STYLE +
     "A young Latina student sitting on campus steps looking at her phone and smiling, "
     "earbuds in, backpack beside her, campus blurred behind. Vertical-friendly mid-shot."),
    ("offer-moment", STYLE +
     "A young Black woman in smart business casual shaking hands with a friendly older "
     "healthcare director across a desk in a bright modern office, both smiling genuinely. "
     "The moment of being hired. Mid-shot, hopeful."),
    ("portrait-confident", STYLE +
     "Close-up portrait of a confident young South Asian woman in her early twenties, "
     "natural smile, looking directly at camera, wearing a simple navy top, soft blurred "
     "campus background. Warm, approachable, real skin texture."),
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
            with urllib.request.urlopen(req, timeout=200) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  FAIL {slug}: HTTP {e.code} {e.read().decode()[:160]}")
            continue
        msg = res["choices"][0]["message"]
        imgs = msg.get("images") or []
        cost = float((res.get("usage") or {}).get("cost") or 0)
        total += cost
        if not imgs:
            print(f"  FAIL {slug}: no image returned")
            continue
        url = imgs[0].get("image_url", {}).get("url", "")
        b64 = url.split(",", 1)[1] if "," in url else ""
        if not b64:
            print(f"  ?    {slug}: non-data url")
            continue
        path = os.path.join(out, f"{slug}.png")
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  ok   {slug}.png  {os.path.getsize(path):,} bytes")
    print(f"\ntotal this run: ${total:.4f}")


if __name__ == "__main__":
    main()