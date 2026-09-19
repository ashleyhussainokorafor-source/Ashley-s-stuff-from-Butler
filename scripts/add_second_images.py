#!/usr/bin/env python3
"""Add a second image element (photo+text split) to the three money pages,
inserted immediately before their purchase section."""
import os
import re

D = "/data/business/hca-daily/worker/assets"
MARK = 'class="hca-split"'   # markup-only marker; the injected CSS also contains
                             # ".hca-split", which made the first check always match

SECTIONS = {
    "vault.html": dict(
        img="smiling-students-library-800.webp", w=800, h=533,
        alt="Students smiling while studying together in a library",
        t="You don't memorise 156 scripts.",
        p="You find the five or eight that match your next interview, read them, and walk "
          "in sounding like you have been doing this for years. That is the whole trick — "
          "and it takes an evening, not a semester.",
        anchor='id="buy"'),
    "accelerator.html": dict(
        img="south-asian-women-office-800.webp", w=800, h=533,
        alt="Young professionals working together on a laptop in an office",
        t="Done-for-you, not more homework.",
        p="Resume kit, LinkedIn playbook, a 30-day sprint and interview coaching — assembled "
          "and automated. No calls, no waiting on a coach's calendar, no figuring out what "
          "to do next.",
        anchor='id="buy"'),
    "resume.html": dict(
        img="black-woman-laptop-study-800.webp", w=800, h=600,
        alt="Student working on a laptop with notes beside her",
        t="Your experience is already there.",
        p="Most candidates don't lack accomplishments — they've buried them in "
          "job-description language. We pull the numbers onto the first line, where the "
          "six-second scan actually happens.",
        anchor='class="cta"'),
}


def insert(page, cfg):
    fp = os.path.join(D, page)
    html = open(fp, encoding="utf-8", errors="ignore").read()
    if MARK in html:
        print(f"  SKIP {page} (already has a split)")
        return False

    # locate the anchor, then the nearest <section before it
    ai = html.find(cfg["anchor"])
    if ai == -1:
        print(f"  FAIL {page}: anchor {cfg['anchor']} not found")
        return False
    si = html.rfind("<section", 0, ai)
    if si == -1:
        print(f"  FAIL {page}: no <section before anchor")
        return False

    block = (
        f'\n<!-- injected photo+text split (second image) -->\n'
        f'<section class="hca-split">\n'
        f'  <div>\n'
        f'    <div class="t">{cfg["t"]}</div>\n'
        f'    <p>{cfg["p"]}</p>\n'
        f'  </div>\n'
        f'  <img src="/img/{cfg["img"]}" width="{cfg["w"]}" height="{cfg["h"]}" '
        f'loading="lazy" alt="{cfg["alt"]}">\n'
        f'</section>\n'
    )
    html = html[:si] + block + html[si:]
    open(fp, "w", encoding="utf-8").write(html)
    print(f"  OK   {page}  (split before anchor {cfg['anchor']}, image={cfg['img']})")
    return True


print("=== adding second image to money pages ===")
n = 0
for page, cfg in SECTIONS.items():
    if insert(page, cfg):
        n += 1
print(f"\nupdated {n} page(s)")