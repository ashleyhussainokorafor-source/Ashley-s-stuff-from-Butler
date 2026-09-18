#!/bin/bash
# Full-page screenshots of live HCA Daily pages for visual/UX analysis.
# Uses the fixlibs-wrapped Chromium. Hard per-shot timeout so one bad page
# cannot hang the whole batch (3200px windows hung it before).
CHROME=/data/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome
OUT=/tmp/uianalysis
mkdir -p "$OUT"

shoot() {  # name, url, height, budget
  local name="$1" url="$2" h="${3:-1600}" b="${4:-5000}"
  rm -f "$OUT/$name.png"
  timeout 75 "$CHROME" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=1280,"$h" --virtual-time-budget="$b" \
    --screenshot="$OUT/$name.png" "$url" >/dev/null 2>&1
  local rc=$?
  if [ -f "$OUT/$name.png" ]; then
    echo "  ok    $name.png  $(stat -c%s "$OUT/$name.png") bytes"
  else
    echo "  FAIL  $name  (rc=$rc)"
  fi
}

echo "=== capturing live pages ==="
shoot home      "https://thehcadaily.com/"            1400
shoot scorecard "https://thehcadaily.com/scorecard"   1200
shoot vault     "https://thehcadaily.com/vault"       1400
shoot accel     "https://thehcadaily.com/accelerator"  1600
shoot resume    "https://thehcadaily.com/resume"      1400
echo
ls -la "$OUT"/*.png 2>/dev/null