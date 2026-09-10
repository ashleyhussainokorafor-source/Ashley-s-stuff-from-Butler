#!/usr/bin/env python3
"""Assemble the HCA Interview Answer Vault into a single sellable document.

Reads the numbered parts from assets/vault/ and writes one combined markdown
file. Run again after editing any part.
"""
import re
from pathlib import Path

VAULT = Path("/data/business/hca-daily/assets/vault")
OUT = VAULT / "HCA-Interview-Answer-Vault-COMPLETE.md"

PARTS = [
    ("00-COVER.md",                  None),
    ("01-behavioral-leadership.md",  "Part 1 — Behavioral & Leadership"),
    ("02-operational-metrics.md",    "Part 2 — Operational & Metrics-Driven"),
    ("03-revenue-cycle-patient-access.md", "Part 3 — Revenue Cycle & Patient Access"),
    ("04-clinical-ops-quality-him.md",     "Part 4 — Clinical Operations, Quality, HIM & Long-Term Care"),
    ("05-salary-negotiation.md",     "Part 5 — Salary Negotiation, Offers & Follow-Up"),
]

chunks = []
stats = []

for filename, part_title in PARTS:
    path = VAULT / filename
    if not path.exists():
        raise SystemExit(f"missing part: {path}")
    body = path.read_text(encoding="utf-8").rstrip()

    if part_title:
        # Drop the part file's own H1 — the section header replaces it.
        body = re.sub(r"\A#\s+.*?\n", "", body).strip()
        chunks.append(f"\n\n---\n\n# {part_title}\n\n{body}")
    else:
        chunks.append(body)

    # count items for the report
    items = len(re.findall(r"^###\s+(?:Q|Script)\s*\d+", body, flags=re.M))
    if not items:
        items = len(re.findall(r"^###\s+\d+[\.\)]", body, flags=re.M))
    stats.append((filename, items, len(body)))

OUT.write_text("".join(chunks) + "\n", encoding="utf-8")

total_items = sum(s[1] for s in stats[1:])
print("Assembled vault parts:")
for name, items, size in stats:
    print(f"  {name:<42} items={items:<4} chars={size}")
print(f"\nTOTAL content items: {total_items}")
print(f"Output: {OUT}")
print(f"Output size: {OUT.stat().st_size:,} bytes")
print(f"Words (approx): {len(OUT.read_text(encoding='utf-8').split()):,}")
