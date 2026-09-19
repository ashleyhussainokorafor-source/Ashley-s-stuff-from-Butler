#!/usr/bin/env python3
"""Inspect the five pages still carrying no imagery: CSS vars, colours, structure."""
import os, re

D = "/data/business/hca-daily/worker/assets"
PAGES = ["vault.html", "accelerator.html", "pricing.html", "resume.html", "learn.html"]

for p in PAGES:
    fp = os.path.join(D, p)
    if not os.path.exists(fp):
        print(f"\n### {p}  -- MISSING")
        continue
    html = open(fp, encoding="utf-8", errors="ignore").read()
    print(f"\n### {p}   ({len(html):,} chars)")
    print(f"  <img> tags        : {len(re.findall(r'<img', html))}")
    print(f"  background-image  : {len(re.findall(r'background-image', html))}")
    # colour system
    root = re.search(r":root\s*\{([^}]*)\}", html)
    if root:
        vars_ = re.findall(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", root.group(1))
        print("  :root vars        :", ", ".join(f"--{k}:{v}" for k, v in vars_))
    else:
        print("  :root vars        : (none)")
    for name, hexv in [("gold #c9a227", "c9a227"), ("coral #ff5749", "ff5749"),
                       ("amber #f59e0b", "f59e0b"), ("navy #0b2545", "0b2545"),
                       ("teal #0d9488", "0d9488")]:
        n = len(re.findall(hexv, html, re.I))
        if n:
            print(f"  uses {name:16}: {n}")
    # tailwind or bespoke?
    print("  tailwind          :", "yes" if "tailwind" in html.lower() else "no (bespoke CSS)")
    # headings
    hs = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", html, re.S)
    hs = [re.sub(r"<[^>]+>", "", h).strip()[:70] for h in hs[:5]]
    for h in hs:
        print(f"    H: {h}")
    # CTA colour
    if "background:var(--coral)" in html or "bg-coral" in html:
        print("  >>> CTA uses CORAL (off-brand)")
    if "background:var(--gold)" in html or "bg-gold" in html or "c9a227" in html:
        print("  >>> CTA uses GOLD (brand-correct)")