#!/bin/bash
# Finish adding the scorecard link to remaining @professorashley videos.
# Runs after YouTube's daily quota reset; the dedup in the python script
# skips the 199 already updated, so --apply 100 cleanly catches the rest.
cd /data || exit 1
python3 automation/scripts/yt_update_descriptions.py --apply 100 2>&1 | tail -6