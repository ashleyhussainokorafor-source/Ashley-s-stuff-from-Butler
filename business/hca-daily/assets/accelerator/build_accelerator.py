#!/usr/bin/env python3
"""Assemble the HCA Career Accelerator into a single sellable document.
Mirrors build_vault.py — reads numbered parts, writes one combined markdown."""
import re
from pathlib import Path

ACC = Path("/data/business/hca-daily/assets/accelerator")
OUT = ACC / "HCA-Career-Accelerator-COMPLETE.md"

PARTS = [
    ("00-COVER.md",                    None),
    ("01-resume-cover-letter-kit.md",  "Part 1 — The Metric-Driven Resume & Cover Letter Kit"),
    ("02-linkedin-playbook.md",        "Part 2 — The LinkedIn Optimization Playbook"),
    ("03-30-day-sprint.md",            "Part 3 — The 30-Day Job Search Sprint"),
    ("04-negotiation-masterclass.md",  "Part 4 — The Salary & Offer Negotiation Masterclass"),
]

chunks = []
for filename, part_title in PARTS:
    path = ACC / filename
    if not path.exists():
        raise SystemExit(f"missing part: {path}")
    body = path.read_text(encoding="utf-8").rstrip()
    if part_title:
        body = re.sub(r"\A#\s+.*?\n", "", body).strip()
        chunks.append(f"\n\n---\n\n# {part_title}\n\n{body}")
    else:
        chunks.append(body)

OUT.write_text("".join(chunks) + "\n", encoding="utf-8")
print(f"Assembled {len(PARTS)-1} parts -> {OUT.name}")
print(f"Size: {OUT.stat().st_size:,} bytes")
print(f"Words (approx): {len(OUT.read_text(encoding='utf-8').split()):,}")