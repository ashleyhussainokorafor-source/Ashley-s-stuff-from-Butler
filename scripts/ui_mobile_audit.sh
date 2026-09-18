#!/bin/bash
# Mobile screenshot + brand-colour audit of the live site.
CHROME=/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome
OUT=/tmp/uianalysis
mkdir -p "$OUT"

echo "=== MOBILE (390 wide, iPhone-class) ==="
timeout 75 "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=390,1400 --virtual-time-budget=5000 \
  --screenshot="$OUT/mobile_home.png" "https://thehcadaily.com/" >/dev/null 2>&1
[ -f "$OUT/mobile_home.png" ] && echo "  ok mobile_home.png $(stat -c%s "$OUT/mobile_home.png") bytes" || echo "  FAIL"

echo
echo "=== TABLET (768 wide) ==="
timeout 75 "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=768,1200 --virtual-time-budget=5000 \
  --screenshot="$OUT/tablet_home.png" "https://thehcadaily.com/" >/dev/null 2>&1
[ -f "$OUT/tablet_home.png" ] && echo "  ok tablet_home.png $(stat -c%s "$OUT/tablet_home.png") bytes" || echo "  FAIL"

echo
echo "=== BRAND COLOURS ACTUALLY DEPLOYED (homepage) ==="
curl -s -L --max-time 15 https://thehcadaily.com/ > "$OUT/home.html" 2>/dev/null
for c in 0b2545 13315c 0d9488 0f766e c9a227 ff5749 f59e0b f97316 ef4444; do
  n=$(grep -oi "#$c" "$OUT/home.html" | wc -l)
  [ "$n" -gt 0 ] && printf "  #%s : %s occurrences\n" "$c" "$n"
done

echo
echo "=== framework / fonts ==="
grep -oiE "tailwind[^\"]*|fonts\.googleapis\.com[^\"]*|sora|inter" "$OUT/home.html" | sort -u | head -6

echo
echo "=== external image/asset references (should be 0) ==="
grep -coiE "<img|background-image:url" "$OUT/home.html"