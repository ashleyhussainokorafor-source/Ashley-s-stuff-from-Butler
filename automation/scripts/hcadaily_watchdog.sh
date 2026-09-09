#!/bin/bash
# HCA Daily watchdog — keeps the platform server alive.
# Checks http://localhost:8085/ ; restarts the server if it's down.
# Silent on success (watchdog pattern); prints only when it acts.

PORT=8085
SERVER="/data/business/hca-daily/web/server.py"
LOG="/data/business/hca-daily/web/server.log"
ENV="/data/.env"

if curl -sf --max-time 5 -o /dev/null "http://localhost:${PORT}/"; then
  # Healthy — do nothing, print nothing.
  exit 0
fi

echo "HCA Daily server down on port ${PORT} — restarting at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Start the server detached so it outlives this script.
set -a
# shellcheck disable=SC1090
[ -f "$ENV" ] && . "$ENV"
set +a

cd "$(dirname "$SERVER")" || exit 1
setsid /usr/local/bin/python3 "$SERVER" >> "$LOG" 2>&1 < /dev/null &

# Give it a moment, then report whether it actually came up.
sleep 3
if curl -sf --max-time 5 -o /dev/null "http://localhost:${PORT}/"; then
  echo "Restart OK — server responding on ${PORT}."
else
  echo "Restart FAILED — still no response on ${PORT}. Check ${LOG}"
fi
