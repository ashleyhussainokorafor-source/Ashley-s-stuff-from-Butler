#!/bin/bash
# HCA Daily lead drip engine — silent on no-op, emits only on sends/errors.
cd /data/business/hca-daily/email || exit 1
OUT=$(python3 drip.py 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo "DRIP ERROR: $OUT"
  exit $STATUS
fi
[ -n "$OUT" ] && echo "$OUT"
exit 0