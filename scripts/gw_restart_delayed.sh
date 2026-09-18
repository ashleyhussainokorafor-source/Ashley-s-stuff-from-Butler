#!/bin/bash
# Detached, delayed gateway restart.
# Sleeps so the current turn's reply is delivered, then restarts the gateway in
# its own session so it survives the gateway's own death.
# Logs to /data/logs (persistent) instead of /tmp (which gets wiped on restart).
export PATH="/opt/venv/bin:$PATH"
LOG=/data/logs/gw_restart.log
mkdir -p /data/logs
{
  echo "=== gateway restart requested $(date -u +%FT%TZ) ==="
  echo "pre-restart gateway PID: $(pgrep -f 'hermes gateway' | tr '\n' ' ')"
  sleep 15
  hermes gateway restart >>"$LOG" 2>&1
  echo "restart rc=$?"
  sleep 25
  echo "post-restart gateway PID: $(pgrep -f 'hermes gateway' | tr '\n' ' ')"
  echo "browser env in new gateway:"
  for p in $(pgrep -f 'hermes gateway'); do
    tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -E '^AGENT_BROWSER_EXECUTABLE_PATH=' || echo "  (pid $p: not set)"
  done
  echo "=== done $(date -u +%FT%TZ) ==="
} >>"$LOG" 2>&1
