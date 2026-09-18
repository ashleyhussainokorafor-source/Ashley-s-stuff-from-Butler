#!/usr/bin/env python3
"""Quarantine images whose subject does NOT match their filename.

Verified visually 2026-09-18 (vision available this session). The library was
built without visual verification and its CREDITS.md says so explicitly.
"""
import os
import shutil

D = "/data/business/hca-daily/worker/assets/img"
Q = os.path.join(D, "_quarantine")
os.makedirs(Q, exist_ok=True)

# slug -> reason (subject does not match the filename / off-message)
BAD = {
    "happy-black-man-university":
        "Filename says Black man; photo is a white man with glasses. "
        "Pexels description itself reads 'cheerful young man with blonde hair'. "
        "Cannot be used where the filename implies representation.",
    "east-asian-student-brickwall":
        "Filename says East Asian; photo shows a white woman against a brick wall.",
}

moved = []
for slug, reason in BAD.items():
    for f in list(os.listdir(D)):
        if f.startswith(slug):
            shutil.move(os.path.join(D, f), os.path.join(Q, f))
            moved.append(f)
    print(f"  quarantined {slug}\n      reason: {reason}")

print(f"\nmoved {len(moved)} file(s) to _quarantine/")
for m in moved:
    print("   ", m)

# record it
note = os.path.join(D, "_QUARANTINE.md")
with open(note, "w") as fh:
    fh.write("# Quarantined images\n\n")
    fh.write("Visually verified 2026-09-18 (Butler). Build step had no vision model "
             "available and flagged this risk in `CREDITS.md`.\n\n")
    for slug, reason in BAD.items():
        fh.write(f"- **{slug}** — {reason}\n")
    fh.write("\nThese files are moved out of the served directory so they cannot be "
             "referenced by accident. Delete or re-source deliberately.\n")
print("wrote", note)