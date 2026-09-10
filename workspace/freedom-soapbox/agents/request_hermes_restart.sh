#!/bin/bash
# request_hermes_restart.sh
# Safe way to request Hermes gateway restart from cron or external supervisor.
# Writes a flag file; does NOT attempt to kill the gateway itself.

RESTART_FLAG="/data/workspace/logs/hermes_restart_request.txt"
REASON="${1:-Manual restart requested}"

mkdir -p "$(dirname "$RESTART_FLAG")"
echo "$(date -Iseconds)" > "$RESTART_FLAG"
echo "$REASON" >> "$RESTART_FLAG"

echo "Restart requested: $REASON"
echo "Flag: $RESTART_FLAG"
echo ""
echo "The next cron run of apply_hermes_restart.py (or container supervisor) will handle it."
