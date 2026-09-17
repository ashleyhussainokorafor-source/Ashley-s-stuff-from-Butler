#!/bin/bash
# Daily continuation of the YouTube CTA upgrade.
#
# YouTube gives us 10,000 quota units/day; each description update costs 50, so
# only ~180 videos can be done per day. This finishes the job across days and
# stays SILENT (no output) once everything is upgraded, so the cron watchdog
# pattern holds.
PY=/opt/venv/bin/python3
OUT=$("$PY" /data/automation/scripts/yt_cta_upgrade.py --apply 170 2>&1)
STATUS=$?
REMAIN=$(printf '%s' "$OUT" | grep -oE 'remaining [0-9]+' | grep -oE '[0-9]+')
if [ "$STATUS" -ne 0 ]; then
  echo "YT CTA UPGRADE ERROR: $OUT"
  exit "$STATUS"
fi
if [ -z "$REMAIN" ] || [ "$REMAIN" = "0" ]; then
  exit 0   # done — stay quiet
fi
printf '%s\n' "$OUT" | tail -3
