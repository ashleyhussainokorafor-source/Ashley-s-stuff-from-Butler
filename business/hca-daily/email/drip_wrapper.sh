#!/bin/bash
# Cron wrapper for the HCA Daily drip engine.
# Silent on a clean no-op run; only emits output when emails are sent or on error.
cd /data/business/hca-daily/email || exit 1
OUT=$(python3 drip.py 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo "DRIP ERROR: $OUT"
  exit $STATUS
fi
# drip.py prints nothing on a no-op; anything printed here means it sent emails.
[ -n "$OUT" ] && echo "$OUT"
exit 0