#!/usr/bin/env python3
"""Campus Brief image brief — 6 shots, generated to the new design system.

Brief constraints honoured:
  - diverse, mid-20s, authentic campus/study/mock-interview settings
  - NO pointing-at-laptop stock, NO handshake-on-white
  - candid walk, laptop in lounge, whiteboard metrics, quiet interview room
Palette mood: off-white #F7F6F2, ink #0B1B2B, navy #132337, teal #2A9D8F.
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

BASE = (
    "Photorealistic candid documentary photograph, natural available light, mid-20s American "
    "university students, genuinely diverse (Black, South Asian, East Asian, Latina/o, white). "
    "Warm neutral tones with soft off-white and muted teal in the scene. Shot on 35mm, "
    "shallow depth of field, unstaged and unposed — nobody looking at the camera, nobody "
    "smiling for a lens. Quiet, calm, credible mood. No text overlay, no logos, no watermarks, "
    "no stock-photo gloss. "
)

PROMPTS = [
    ("cb-campus-walk",
     BASE + "Two students walking side by side along an outdoor campus path between "
     "buildings in late afternoon, mid-conversation, one holding a notebook against their "
     "side, backpacks on. Seen from behind and slightly to the side. Wide, calm, cinematic."),
    ("cb-lounge-laptop",
     BASE + "A student sitting alone on a worn lounge sofa in a university student center, "
     "laptop open on their knees, focused, one hand near their chin, coffee cup on the floor "
     "beside them. Natural window light from the left. NOT pointing at the screen."),
    ("cb-mock-interview",
     BASE + "A quiet small interview room with a plain table: a student seated on one side "
     "listening intently, hands folded, and an interviewer partly out of frame across from "
     "them with a notepad. Neutral wall, soft daylight. Tense-but-calm, respectful mood."),
    ("cb-whiteboard-ar",
     BASE + "Two students standing at a whiteboard in a study room, one mid-gesture "
     "explaining a simple hand-drawn line chart while the other watches and thinks. The "
     "marker strokes are abstract numbers and a downward- trending line — generic, no "
     "readable marketing text. Teal marker, off-white board."),
    ("cb-quiet-library",
     BASE + "A tall university library reading room, long wooden tables, warm lamps, a few "
     "students studying quietly far apart. Wide architectural shot, soft depth, calm and "
     "still, almost empty. Late afternoon light through tall windows."),
    ("cb-group-review",
     BASE + "Four students clustered around a single table in a bright study room, one "
     "laptop between them and notes spread out, mid-discussion and pointing at a page — "
     "collaborative, absorbed, not performing for a camera."),
]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/campusbrief"
    os.makedirs(out, exist_ok=True)
    total = 0.0
    for slug, prompt in PROMPTS:
        body = json.dumps({"model": MODEL,
                           "messages": [{"role": "user", "content": prompt}],
                           "modalities": ["image", "text"]}).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions", data=body,
            headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=200) as r:
                res = json.load(r)
        except urllib.error.HTTPError as e:
            print(f"  FAIL {slug}: HTTP {e.code} {e.read().decode()[:140]}")
            continue
        msg = res["choices"][0]["message"]
        imgs = msg.get("images") or []
        total += float((res.get("usage") or {}).get("cost") or 0)
        if not imgs:
            print(f"  FAIL {slug}: no image")
            continue
        url = imgs[0].get("image_url", {}).get("url", "")
        b64 = url.split(",", 1)[1] if "," in url else ""
        if not b64:
            print(f"  ?    {slug}: non-data url")
            continue
        p = os.path.join(out, f"{slug}.png")
        with open(p, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  ok   {slug}.png  {os.path.getsize(p):,} bytes")
    print(f"\ncost this run: ${total:.4f}")


if __name__ == "__main__":
    main()