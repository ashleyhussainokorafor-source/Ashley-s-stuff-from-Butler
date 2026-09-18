#!/bin/bash
# HCA Daily lead drip engine — silent on no-op, delivers only real sends.
# stderr (transient fetch warnings) goes to a log, NOT delivered — so a
# blip doesn't spam an error alert every tick.
cd /data/business/hca-daily/email || exit 1
LOG=/tmp/hca_daily_drip.log
OUT=$(python3 drip.py 2>>"$LOG")
STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo "DRIP ERROR: $(tail -5 "$LOG" 2>/dev/null)"
  exit $STATUS
fi
[ -n "$OUT" ] && echo "$OUT"
exit 0