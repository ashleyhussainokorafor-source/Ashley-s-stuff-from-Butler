#!/bin/bash
# Diagnose Chromium shared-library status: bare vs fixlibs-augmented.
CHROME=$(ls -d /data/.cache/ms-playwright/chromium-*/chrome-linux64/chrome 2>/dev/null | tail -1)
FIX=/data/.cache/ms-playwright/fixlibs/extracted/usr/lib/x86_64-linux-gnu
echo "CHROME=$CHROME"
ls -la "$CHROME" 2>&1 | head -2
echo
echo "=== MISSING LIBS (bare) ==="
ldd "$CHROME" 2>/dev/null | grep -i "not found" | sort
echo "bare missing count: $(ldd "$CHROME" 2>/dev/null | grep -ci 'not found')"
echo
echo "=== fixlibs contents (count) ==="
ls "$FIX" 2>/dev/null | wc -l
echo "sample:"
ls "$FIX" 2>/dev/null | head -12
echo
echo "=== MISSING LIBS (with fixlibs on LD_LIBRARY_PATH) ==="
LD_LIBRARY_PATH="$FIX" ldd "$CHROME" 2>/dev/null | grep -i "not found" | sort
echo "with-fixlibs missing count: $(LD_LIBRARY_PATH="$FIX" ldd "$CHROME" 2>/dev/null | grep -ci 'not found')"
echo
echo "=== SMOKE TEST: does chrome actually launch with fixlibs? ==="
LD_LIBRARY_PATH="$FIX" "$CHROME" --headless=new --disable-gpu --no-sandbox \
  --virtual-time-budget=6000 --dump-dom "https://example.com" 2>/tmp/chrome_err.txt | head -5
echo "exit=$?"
echo "--- stderr (tail) ---"
tail -5 /tmp/chrome_err.txt