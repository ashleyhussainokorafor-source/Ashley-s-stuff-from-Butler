#!/bin/bash
# Cron wrapper for the HCA Daily drip engine.
#
# IMPORTANT: must run under /opt/venv/bin/python3 — the system python3 has no
# google-api-python-client, so this silently dies with ModuleNotFoundError.
# Silent on a clean no-op run; only emits output when emails are sent or on error.
cd /data/business/hca-daily/email || exit 1
PY=/opt/venv/bin/python3
[ -x "$PY" ] || PY=python3
OUT=$("$PY" drip.py 2>&1)
STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo "DRIP ERROR: $OUT"
  exit $STATUS
fi
# drip.py prints nothing on a no-op; anything printed here means it sent emails.
[ -n "$OUT" ] && echo "$OUT"
exit 0