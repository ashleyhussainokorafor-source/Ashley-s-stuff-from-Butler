#!/usr/bin/env python3
"""Show the hero region of each sales page so image insertions land correctly."""
import os, re

D = "/data/business/hca-daily/worker/assets"
for p in ["vault.html", "accelerator.html", "resume.html", "pricing.html"]:
    html = open(os.path.join(D, p), encoding="utf-8", errors="ignore").read()
    print(f"\n{'='*72}\n### {p}\n{'='*72}")
    # find where the body starts and print the first hero-ish block
    i = html.lower().find("<body")
    seg = html[i:i + 1400] if i >= 0 else html[:1400]
    # strip long css if it leaked in
    seg = re.sub(r"<style.*?</style>", "[STYLE]", seg, flags=re.S)
    print(seg[:1300])