#!/bin/bash
# Finish swapping remaining YouTube descriptions to thehcadaily.com (quota-aware; skips already-done).
cd /data/automation/scripts
python3 yt_update_descriptions.py --apply 270 2>&1 | grep -vE "WARNING|UserWarning|warnings.warn" | tail -2