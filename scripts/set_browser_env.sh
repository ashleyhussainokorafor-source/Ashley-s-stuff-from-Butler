#!/bin/bash
# Point Hermes's browser tool at the LD_LIBRARY_PATH-scoped Chrome wrapper.
ENV=/data/.env
WRAPPER=/data/scripts/chrome-wrapper
KEY=AGENT_BROWSER_EXECUTABLE_PATH

if grep -qE "^${KEY}=" "$ENV" 2>/dev/null; then
  cp "$ENV" "$ENV.bak.$(date +%s)"
  sed -i "s|^${KEY}=.*|${KEY}=${WRAPPER}|" "$ENV"
  echo "updated existing ${KEY}"
else
  cp "$ENV" "$ENV.bak.$(date +%s)"
  printf '\n# Browser: Chromium needs fixlibs on LD_LIBRARY_PATH (see /data/scripts/chrome-wrapper)\n%s=%s\n' "$KEY" "$WRAPPER" >> "$ENV"
  echo "appended ${KEY}"
fi

echo "--- current value ---"
grep -E "^${KEY}=" "$ENV"
echo "--- .env key names ---"
grep -oE "^[A-Za-z_][A-Za-z0-9_]*=" "$ENV" | sed 's/=$//' | sort | tr '\n' ' '
echo
echo "--- backups made ---"
ls -1 "$ENV".bak.* 2>/dev/null | tail -3