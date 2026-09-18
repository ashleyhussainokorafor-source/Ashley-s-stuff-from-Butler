#!/usr/bin/env python3
"""What image capability do we ACTUALLY have? Check keys + OpenRouter image models."""
import json, os, urllib.request

ENV = "/data/.env"
keys = []
for line in open(ENV):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        keys.append(line.split("=", 1)[0])
print("=== ALL KEYS IN /data/.env ===")
for k in sorted(keys):
    print("  ", k)

img_keys = [k for k in keys if any(t in k.upper() for t in
            ("OPENAI", "REPLICATE", "STABILITY", "FAL", "GEMINI", "GOOGLE", "IMAGE"))]
print("\n=== dedicated image-gen keys ===")
print("  ", img_keys or "NONE — image_gen tool has no provider credential")

# OpenRouter may expose image-OUTPUT models; that would be our path.
ork = ""
for line in open(ENV):
    if line.strip().startswith("OPENROUTER_API_KEY="):
        ork = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
print("\n=== openrouter key present:", bool(ork), "===")

if ork:
    req = urllib.request.Request("https://openrouter.ai/api/v1/models",
                                 headers={"Authorization": f"Bearer {ork}"})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.load(r)["data"]

    def outmods(m):
        arch = m.get("architecture") or {}
        om = arch.get("output_modalities") or []
        return "image" in om

    img_models = [m for m in data if outmods(m)]
    print(f"\n=== OpenRouter models that OUTPUT IMAGES: {len(img_models)} ===")
    for m in sorted(img_models, key=lambda x: x["id"])[:25]:
        pr = m.get("pricing") or {}
        print(f"  {m['id']}")
        print(f"      in={pr.get('prompt')} out={pr.get('completion')} "
              f"img={pr.get('image') or pr.get('image_output')}")