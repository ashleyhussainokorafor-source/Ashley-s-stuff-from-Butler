#!/usr/bin/env python3
"""
RunwayVisualsAgent v4 — final clean version
Uses RUNWAY_API_KEY from environment (recommended)
"""
import os, json, time, argparse, requests, base64
from pathlib import Path

RUNWAY = "https://api.dev.runwayml.com/v1"

def get_headers():
    key = os.environ.get("RUNWAY_API_KEY")
    if not key:
        raise RuntimeError("RUNWAY_API_KEY not set in environment")
    return {
        "Authorization": f"Bearer {key}",
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json"
    }

def upload_image(image_path):
    """Compress and return a base64 data URL for the local image."""
    from PIL import Image
    img = Image.open(image_path)
    # Resize to 1280x720 (16:9) to match Runway ratio
    img = img.resize((1280, 720), Image.LANCZOS)
    # Convert to RGB if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    url = f"data:image/jpeg;base64,{data}"
    print(f"[upload] Compressed base64 data URL ({len(url)} chars)")
    return url

def generate_image(prompt, seed):
    payload = {
        "model": "gen4_image_turbo",
        "promptText": prompt,
        "aspectRatio": "16:9",
        "seed": seed,
        "watermark": False
    }
    r = requests.post(f"{RUNWAY}/text_to_image", json=payload, headers=get_headers())
    r.raise_for_status()
    job = r.json()["id"]
    for _ in range(45):
        time.sleep(3)
        s = requests.get(f"{RUNWAY}/tasks/{job}", headers=get_headers()).json()
        if s.get("status") == "SUCCEEDED":
            return s["output"][0]["url"]
    raise TimeoutError("Image generation timed out")

def generate_video(image_url, prompt, model, seed, duration):
    # Map aspect ratio to Runway pixel ratio
    ratio = "1280:720"  # 16:9
    payload = {
        "model": model,
        "promptText": prompt,
        "duration": duration,
        "promptImage": image_url,
        "ratio": ratio,
    }
    # Only add seed/watermark if model supports them (gen4_turbo does)
    if model in ("gen4_turbo", "gen4.5"):
        payload["seed"] = seed
        payload["watermark"] = False
    r = requests.post(f"{RUNWAY}/image_to_video", json=payload, headers=get_headers())
    if r.status_code != 200:
        print(f"[ERROR] image_to_video {r.status_code}: {r.text}")
    r.raise_for_status()
    return r.json()["id"]

def poll(job_id):
    for _ in range(90):
        time.sleep(4)
        s = requests.get(f"{RUNWAY}/tasks/{job_id}", headers=get_headers()).json()
        if s.get("status") == "SUCCEEDED":
            output = s.get("output", [])
            if isinstance(output, list) and len(output) > 0:
                if isinstance(output[0], dict):
                    return output[0].get("url", output[0])
                elif isinstance(output[0], str):
                    return output[0]
            elif isinstance(output, str):
                return output
            print(f"[WARN] Unexpected output format: {output}")
            return str(output)
        if s.get("status") in ("FAILED", "CANCELLED"):
            raise RuntimeError(s)
    raise TimeoutError(job_id)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--track_id", required=True)
    p.add_argument("--prompt_file", required=True)
    p.add_argument("--output_dir", required=True)
    p.add_argument("--image_file", default=None, help="Path to a seed image file (skips text_to_image)")
    args = p.parse_args()

    prompt = Path(args.prompt_file).read_text().strip()

    state_path = Path(args.output_dir).parent.parent / "afroviolin_state.json"
    state = json.loads(state_path.read_text())
    meta = state["tracks"][args.track_id]
    va = meta["visual_assignment"]
    model = "gen4_turbo" if "Portrait" in va["tier_label"] else "seedance2_fast"
    seed = va["seed"]
    duration = min(8, max(4, int(meta["audio_features"]["duration_seconds"] / 2)))

    if args.image_file:
        print(f"[{args.track_id}] Step 1: Uploading provided image {args.image_file}...")
        # Runway image_to_video accepts a public URL; we can't host locally.
        # Workaround: convert image to base64 data URL if supported, otherwise upload via Runway's image endpoint.
        img_url = upload_image(args.image_file)
    else:
        print(f"[{args.track_id}] Step 1: Generating image...")
        img_url = generate_image(prompt, seed)
    print(f"[{args.track_id}] Step 2: Generating video with {model}...")
    vid_job = generate_video(img_url, prompt, model, seed, duration)
    final_url = poll(vid_job)

    out = Path(args.output_dir) / f"{args.track_id}_{model}_{vid_job}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        f.write(requests.get(final_url, headers=get_headers()).content)

    meta["runway_output_url"] = str(out)
    meta["status"] = "visuals_ready_for_approval"
    meta["approval_tier"] = "style_locked"
    state_path.write_text(json.dumps(state, indent=2))
    print(f"[{args.track_id}] ✓ COMPLETE → {out}")

if __name__ == "__main__":
    main()
