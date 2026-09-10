#!/bin/bash
# setup_telegram_routing_automation.sh
# One-time setup to wire the Telegram routing automation into cron.

set -e

WORKSPACE="/data/workspace"
AGENTS="$WORKSPACE/agents"
LOGS="$WORKSPACE/logs"

echo "=== Hermes Telegram Routing Automation Setup ==="
echo ""

# 1. Ensure log dir exists
mkdir -p "$LOGS"

# 2. Add cron entry for the apply script (runs every 2 minutes)
CRON_ENTRY="*/2 * * * * cd $AGENTS && python3 apply_hermes_restart.py >> $LOGS/apply_hermes_restart.log 2>&1"

# Check if already present
if crontab -l 2>/dev/null | grep -q "apply_hermes_restart.py"; then
    echo "Cron entry already exists — skipping."
else
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Added cron entry:"
    echo "  $CRON_ENTRY"
fi

echo ""
echo "Automation installed."
echo ""
echo "What happens now:"
echo "  1. telegram_routing_watcher.py detects changes to TELEGRAM_ALLOWED_USERS or TELEGRAM_BOT_TOKEN"
echo "  2. It writes a restart request flag to $LOGS/hermes_restart_request.txt"
echo "  3. Every 2 minutes, apply_hermes_restart.py checks the flag and safely restarts the gateway"
echo ""
echo "To test manually:"
echo "  $AGENTS/request_hermes_restart.sh 'Testing restart automation'"
echo "  python3 $AGENTS/apply_hermes_restart.py"
