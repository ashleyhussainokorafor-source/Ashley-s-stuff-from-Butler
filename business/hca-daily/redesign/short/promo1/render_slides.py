#!/usr/bin/env python3
"""Render each .slide element of slides.html to a 1080x1920 PNG."""
import os
OUT = os.path.dirname(os.path.abspath(__file__))
os.environ["LD_LIBRARY_PATH"] = (
    "/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu:"
    + os.environ.get("LD_LIBRARY_PATH", "")
)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + os.path.join(OUT, "slides.html"))
    pg.wait_for_timeout(1200)
    slides = pg.query_selector_all(".slide")
    print("slides found:", len(slides))
    for i, s in enumerate(slides, 1):
        path = os.path.join(OUT, f"slide{i}.png")
        s.screenshot(path=path)
        print(f"  wrote slide{i}.png  ({os.path.getsize(path):,} bytes)")
    b.close()
print("render complete")
