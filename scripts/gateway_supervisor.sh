#!/bin/bash
# gateway_supervisor.sh — keep every project bot's gateway alive.
# Discovers all profiles that have a TELEGRAM_BOT_TOKEN, restarts any whose
# gateway process is missing. Silent when everything is healthy (watchdog style);
# prints only when it actually restarts something.

HERMES=/opt/venv/bin/hermes
found_any=0

for d in /data/profiles/*/; do
  [ -d "$d" ] || continue
  p=$(basename "$d")
  [ -f "$d/profile.yaml" ] || continue
  grep -q "^TELEGRAM_BOT_TOKEN=" "$d/.env" 2>/dev/null || continue

  if ! pgrep -f "profile $p gateway run" > /dev/null 2>&1; then
    mkdir -p "$d/logs"
    cd /data || exit 1
    setsid "$HERMES" --profile "$p" gateway run >> "$d/logs/gateway.log" 2>&1 < /dev/null &
    echo "🔄 restarted gateway: $p"
    found_any=1
  fi
done

exit 0