#!/usr/bin/env python3
"""HCA Daily — faceless Shorts factory.

Turns content/shorts_scripts.json into a finished, on-brand 1080x1920 Short and
queues it for publishing. Run by cron; produces at most one Short per run.

Pipeline: script -> TTS voiceover -> word-clock slide timing -> HTML slides ->
playwright frame grabs -> ffmpeg -> append to shorts/queue.json

INTERPRETERS MATTER: playwright lives in the SYSTEM python3, edge_tts lives in
/opt/venv. This script runs under system python3 and shells out to the venv for
TTS. Do not "simplify" that away.

Idempotent: a script whose id already exists in the queue (or as a build dir) is
never rebuilt.

Usage:
  hca_short_factory.py                # build the next unbuilt script
  hca_short_factory.py --id short003  # build a specific one
  hca_short_factory.py --dry-run      # show what would be built
  hca_short_factory.py --all          # build every remaining script
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = "/data/business/hca-daily"
SCRIPTS_JSON = f"{ROOT}/content/shorts_scripts.json"
QUEUE = f"{ROOT}/shorts/queue.json"
BUILDS = f"{ROOT}/shorts/builds"
OPS_LOG = f"{ROOT}/ops/OPS_LOG.md"

VENV_PY = "/opt/venv/bin/python3"
CHROME = "/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"
FIXLIBS = "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu"
VOICE = "en-US-AriaNeural"
RATE = "+8%"

W, H = 1080, 1920
# Shorts UI eats the top ~15% and bottom ~20%. Keep text inside this band.
SAFE_TOP, SAFE_BOTTOM = 380, 1450

NAVY, NAVY2 = "#0b2545", "#13315c"
TEAL, GOLD = "#0d9488", "#c9a227"


def log(msg):
    print(msg, flush=True)
    try:
        os.makedirs(os.path.dirname(OPS_LOG), exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        with open(OPS_LOG, "a") as fh:
            fh.write(f"- **{stamp} UTC** | `SHORT-BUILD` | {msg}\n")
    except OSError:
        pass


def load_queue():
    if os.path.exists(QUEUE):
        return json.load(open(QUEUE))
    return {"auto_publish": True, "posts": []}


def save_queue(q):
    os.makedirs(os.path.dirname(QUEUE), exist_ok=True)
    json.dump(q, open(QUEUE, "w"), indent=2)


def duration_of(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def line_size(text):
    """Fit a line inside the slide's text width without clipping.

    Slide text box is 1080 - 2*78 = 924px wide. Bold DejaVu runs ~0.62*size
    per character, so size ~= 924 / (0.62 * len). Measured, not guessed: a
    looser divisor pushed long lines to x=1076 and off the padding.
    """
    n = max(len(text), 8)
    return int(min(76, max(34, 1490 / n)))


def build_html(script, out_dir):
    """One .slide per segment; lines revealed progressively."""
    segs = script["segments"]
    parts = []
    for i, seg in enumerate(segs):
        lines = []
        for k, text in enumerate(seg["display"]):
            cls = "line"
            if seg.get("slide") == "cta" and k >= 1:
                cls += " gold"
            lines.append(
                f'<div class="{cls}" data-reveal="{k}" '
                f'style="font-size:{line_size(text)}px">{text}</div>'
            )
        parts.append(f'<div class="slide" id="seg{i}">' + "".join(lines) + "</div>")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  html,body{{width:{W}px;height:{H}px;overflow:hidden}}
  body{{background:linear-gradient(160deg,{NAVY} 0%,{NAVY2} 100%);
       font-family:'DejaVu Sans','Liberation Sans',Helvetica,Arial,sans-serif;
       position:relative}}
  .brand{{position:absolute;top:310px;left:78px;font-size:28px;font-weight:800;
         letter-spacing:3px;color:{TEAL};text-transform:uppercase;z-index:10}}
  .brand span{{color:#fff}}
  .slide{{position:absolute;left:0;right:0;top:{SAFE_TOP}px;bottom:{H - SAFE_BOTTOM}px;
         display:none;flex-direction:column;justify-content:center;
         padding:0 78px}}
  .slide.on{{display:flex}}
  .line{{color:#fff;font-weight:800;line-height:1.22;margin-bottom:22px;
        letter-spacing:-0.5px;opacity:0;max-width:100%;overflow-wrap:break-word}}
  .line.gold{{color:{GOLD}}}
</style></head><body>
  <div class="brand">HCA<span>DAILY</span></div>
  {''.join(parts)}
</body></html>"""
    path = os.path.join(out_dir, "slides.html")
    with open(path, "w") as fh:
        fh.write(html)
    return path


REVEAL_JS = """([sid, reveal]) => {
  document.querySelectorAll('.slide').forEach(s =>
    s.classList.toggle('on', s.id === sid));
  document.querySelectorAll('#' + sid + ' .line').forEach(el => {
    el.style.opacity = (Number(el.dataset.reveal) <= reveal) ? '1' : '0';
  });
}"""


def render_frames(script, out_dir, wps):
    """Grab one PNG per reveal step, timed by the voiceover word clock.

    Screenshots MUST be taken from Python — page.evaluate runs inside the
    browser and has no access to locators or the screenshot API.
    """
    segs = script["segments"]
    steps = []
    word_cursor = 0
    for i, seg in enumerate(segs):
        lines = seg["display"]
        seg_words = max(len(seg["vo"].split()), 1)
        # split this segment's word span evenly across its revealed lines
        bounds = [word_cursor + round(seg_words * k / len(lines))
                  for k in range(len(lines) + 1)]
        for k in range(len(lines)):
            dur = round(wps * (bounds[k + 1] - bounds[k]), 4)
            if dur <= 0:
                dur = 0.4
            steps.append({"slideId": f"seg{i}", "reveal": k, "dur": dur})
        word_cursor = bounds[-1]

    os.environ["LD_LIBRARY_PATH"] = FIXLIBS + ":" + os.environ.get("LD_LIBRARY_PATH", "")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME,
                              args=["--no-sandbox", "--disable-dev-shm-usage"])
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.join(out_dir, "slides.html"))
        pg.wait_for_timeout(800)
        for n, step in enumerate(steps, start=1):
            pg.evaluate(REVEAL_JS, [step["slideId"], step["reveal"]])
            pg.wait_for_timeout(120)
            name = f"frame{n:02d}.png"
            # full-viewport grab so every frame is exactly 1080x1920
            pg.screenshot(path=os.path.join(out_dir, name))
            step["file"] = name
        b.close()
    return steps


def assemble(out_dir, steps, audio, mp4):
    """Concat the stills with their durations, then mux the voiceover."""
    concat = os.path.join(out_dir, "concat.txt")
    with open(concat, "w") as fh:
        fh.write("ffconcat version 1.0\n")
        for s in steps:
            fh.write(f"file '{s['file']}'\nduration {s['dur']}\n")
        fh.write(f"file '{steps[-1]['file']}'\n")  # concat demuxer needs a final repeat
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", concat,
         "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
         "-s", f"{W}x{H}", "-c:a", "aac", "-b:a", "128k", "-shortest",
         "-movflags", "+faststart", mp4], check=True)
    return mp4


def build(script):
    sid = script["id"]
    out_dir = os.path.join(BUILDS, sid)
    if os.path.exists(os.path.join(out_dir, f"hca-{sid}.mp4")):
        log(f"{sid}: already built, skipping")
        return None
    os.makedirs(out_dir, exist_ok=True)

    vo_text = " ".join(seg["vo"] for seg in script["segments"])
    words = len(vo_text.split())
    audio = os.path.join(out_dir, "voiceover.mp3")

    log(f"{sid}: synthesizing voiceover ({words} words)")
    subprocess.run([VENV_PY, "-m", "edge_tts", "--voice", VOICE, f"--rate={RATE}",
                    "--text", vo_text, "--write-media", audio], check=True)

    audio_dur = duration_of(audio)
    wps = audio_dur / words
    log(f"{sid}: audio={audio_dur:.2f}s  wps={wps:.4f}")

    build_html(script, out_dir)
    steps = render_frames(script, out_dir, wps)
    total = sum(s["dur"] for s in steps)

    mp4 = os.path.join(out_dir, f"hca-{sid}.mp4")
    assemble(out_dir, steps, audio, mp4)
    real = duration_of(mp4)
    log(f"{sid}: built {len(steps)} frames -> {real:.2f}s  {os.path.getsize(mp4)//1024}KB")

    return {"id": sid, "mp4": mp4, "title": script["title"],
            "tags": script.get("tags", []), "frames": len(steps),
            "duration": real}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="build a specific script id")
    ap.add_argument("--all", action="store_true", help="build every remaining script")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = json.load(open(SCRIPTS_JSON))
    scripts = data["scripts"]
    q = load_queue()
    queued = {p["id"] for p in q["posts"]}

    todo = [s for s in scripts
            if s["id"] not in queued
            and not os.path.exists(os.path.join(BUILDS, s["id"], f"hca-{s['id']}.mp4"))]
    if args.id:
        todo = [s for s in todo if s["id"] == args.id]
        if not todo:
            print(f"{args.id}: nothing to do (already queued or built)")
            return 0
    if not args.all:
        todo = todo[:1]

    if args.dry_run:
        for s in todo:
            print(f"would build {s['id']}: {s['title']}")
        if not todo:
            print("nothing to build — every script is already built and queued")
        return 0

    if not todo:
        if args.all:
            print("nothing to build — every script is already built and queued")
        return 0

    made = []
    for s in todo:
        res = build(s)
        if not res:
            continue
        made.append(res)
        q = load_queue()
        q["posts"].append({
            "id": res["id"],
            "title": res["title"],
            "file": res["mp4"],
            "videoId": None,
            "status": "ready",
            "publishAt": datetime.now(timezone.utc).isoformat(),
            "tags": res["tags"],
            "built": {"frames": res["frames"], "duration": round(res["duration"], 2)},
        })
        save_queue(q)
        log(f"{res['id']}: queued as ready (auto_publish={q.get('auto_publish')}) "
            f"-> https://youtube.com/shorts/... after publish")

    for m in made:
        print(f"BUILT {m['id']}: {m['title']} ({m['duration']:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
