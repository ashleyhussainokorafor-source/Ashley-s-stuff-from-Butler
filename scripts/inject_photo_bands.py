#!/usr/bin/env python3
"""Inject a self-contained photo band + brand CSS into the non-homepage pages.

Self-contained on purpose: each page has bespoke CSS with DIFFERENT variable
names (--navy-2 vs --navy2, --bg vs --off), so the snippet uses literal brand
hex values and its own class namespace (hca-*) to avoid collisions.

Idempotent: re-running skips pages already injected.
"""
import os
import re

D = "/data/business/hca-daily/worker/assets"
MARK = "hca-photoband"          # idempotency marker

CSS = """<style>
/* ── HCA shared imagery (injected) ─────────────────────────────────────
   The site had zero images on every page. Self-contained: literal brand
   hexes + hca-* namespace so it works on pages with different var names. */
.hca-band{position:relative;width:100%;overflow:hidden;background:#0b2545;margin:0}
.hca-band img{display:block;width:100%;height:clamp(220px,34vw,380px);
  object-fit:cover;object-position:center 32%}
.hca-band .cap{position:absolute;left:0;right:0;bottom:0;
  background:linear-gradient(transparent,rgba(11,37,69,.94));color:#fff;
  padding:56px 22px 22px;text-align:center;font-size:15px;font-weight:600;
  font-family:'Inter',system-ui,-apple-system,sans-serif}
.hca-band .cap b{color:#c9a227}
.hca-split{display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:center;
  max-width:1080px;margin:0 auto;padding:40px 22px}
.hca-split img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;
  border-radius:20px;box-shadow:0 18px 44px rgba(11,37,69,.18)}
.hca-split .t{font-family:'Sora',sans-serif;font-weight:800;color:#0b2545;
  font-size:26px;line-height:1.2;margin-bottom:10px}
.hca-split p{color:#5b6572;font-size:16px;line-height:1.6}
@media(max-width:820px){.hca-split{grid-template-columns:1fr;gap:24px}}
</style>
"""

# page -> (image, width, height, caption html, alt)
BANDS = {
    "vault.html": (
        "offer-moment.webp", 900, 600,
        "The moment you stop <b>hoping</b> and start answering.", 
        "Young professional shaking hands with a hiring director after a successful interview"),
    "accelerator.html": (
        "clinical-team.webp", 900, 600,
        "Built for the room you're <b>actually</b> walking into.",
        "Young healthcare administration professionals talking in a modern hospital corridor"),
    "resume.html": (
        "portrait-confident.webp", 700, 900,
        "Six seconds is all the first <b>scan</b> takes.",
        "Confident young professional smiling at the camera"),
    "pricing.html": (
        "grads-diplomas-800.webp", 800, 533,
        "Pick the version that matches <b>where you are</b>.",
        "Diverse graduates celebrating with diplomas outdoors"),
}


def inject(page, spec):
    fp = os.path.join(D, page)
    if not os.path.exists(fp):
        print(f"  SKIP {page} (missing)")
        return False
    html = open(fp, encoding="utf-8", errors="ignore").read()
    if MARK in html:
        print(f"  SKIP {page} (already injected)")
        return False

    img, w, h, cap, alt = spec
    band = (
        f'\n<!-- injected photo band (site had no imagery) -->\n'
        f'<div class="hca-band">\n'
        f'  <img src="/img/{img}" width="{w}" height="{h}" loading="lazy" alt="{alt}">\n'
        f'  <div class="cap">{cap}</div>\n'
        f'</div>\n'
    )

    # 1) CSS before </head>
    if "</head>" in html:
        html = html.replace("</head>", CSS + "</head>", 1)
    else:
        html = html.replace("<body", CSS + "<body", 1)

    # 2) band after the first hero block (</header> or </section>) following <body>
    bi = html.find("<body")
    cands = []
    for tag in ("</header>", "</section>"):
        j = html.find(tag, bi)
        if j != -1:
            cands.append((j + len(tag), tag))
    if not cands:
        print(f"  FAIL {page}: no hero close tag found")
        return False
    pos, tag = min(cands)
    html = html[:pos] + "\n" + band + html[pos:]

    open(fp, "w", encoding="utf-8").write(html)
    print(f"  OK   {page}  (band after first {tag}, image={img})")
    return True


print("=== injecting photo bands ===")
n = 0
for page, spec in BANDS.items():
    if inject(page, spec):
        n += 1
print(f"\ninjected into {n} page(s)")