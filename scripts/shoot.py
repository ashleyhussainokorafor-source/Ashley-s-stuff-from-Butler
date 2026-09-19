#!/usr/bin/env python3
"""Screenshot a live page to a PNG so it can be shared.

Full-page capture at a phone-ish width, which is how most of Ashley's traffic
arrives. Run: python3 /data/scripts/shoot.py /about /tmp/about.png
"""
import os
import sys

os.environ["LD_LIBRARY_PATH"] = (
    "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu:"
    + os.environ.get("LD_LIBRARY_PATH", "")
)
CHROME = "/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome"

path = sys.argv[1] if len(sys.argv) > 1 else "/"
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/shot.png"
width = int(sys.argv[3]) if len(sys.argv) > 3 else 430

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME,
                          args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": width, "height": 900}, device_scale_factor=2)
    pg.goto("https://thehcadaily.com" + path, wait_until="networkidle")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=out, full_page=True)
    print("h:", pg.evaluate("document.body.scrollHeight"))
    b.close()
print("wrote", out, os.path.getsize(out) // 1024, "KB")