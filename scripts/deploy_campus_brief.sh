#!/bin/bash
# Deploy the merged Campus Brief homepage (spec by hcadaily bot, media by Butler).
set -uo pipefail
cd /data/business/hca-daily/worker
probe(){ curl -s -L --max-time 20 -o /tmp/_p -w "%{http_code} %{size_download}" "$1"; }

echo "=== 1. lock ==="
bash /data/scripts/deploy_lock.sh acquire worker butler 2>&1 | tail -2
echo
echo "=== 2. deploy ==="
set -a; source /data/.cloudflare.env 2>/dev/null; set +a
export CLOUDFLARE_ACCOUNT_ID=7331f696a15eee3fe7bf94f41376f7b8
npx --yes wrangler@4 deploy 2>&1 | grep -iE "Read [0-9]+ files|Uploaded [0-9]+ of|Version ID|error" | head -5
echo
echo "=== 3. routes (regression) ==="
for p in "" scorecard vault accelerator pricing resume learn path practice league legal; do
  printf "  /%-12s %s\n" "$p" "$(probe "https://thehcadaily.com/$p")"
done
echo
echo "=== 4. Campus Brief media ==="
for f in cb-drill-loop.mp4 cb-drill-poster.jpg cb-campus-walk.webp cb-lounge-laptop.webp \
         cb-mock-interview.webp cb-whiteboard-ar.webp cb-quiet-library.webp cb-group-review.webp; do
  printf "  %-26s %s\n" "$f" "$(probe "https://thehcadaily.com/img/$f")"
done
printf "  %-26s %s\n" "ashley.jpg (founder)" "$(probe "https://thehcadaily.com/ashley.jpg")"
echo
echo "=== 5. design + contract checks (live homepage) ==="
H=$(curl -s -L --max-time 25 "https://thehcadaily.com/")
chk(){ printf "  %-40s %s\n" "$1" "$(echo "$H" | grep -c "$2")"; }
chk "paper #F7F6F2"            "F7F6F2"
chk "ink #0B1B2B"              "0B1B2B"
chk "navy #132337"             "132337"
chk "teal accent #2A9D8F"      "2A9D8F"
chk "teal-dk button #1F7A6F"   "1F7A6F"
chk "gold (chips only)"        "C9A227"
chk "poster <img> for LCP"     'class="poster"'
chk "hero video src"           "cb-drill-loop.mp4"
chk "UTM carry-through script" "utm_"
chk "founder headshot"         "ashley.jpg"
chk "mobile bottom bar"        "mbar"
chk "hero H1 verbatim"         "Walk in speaking their language"
echo
echo "  --- must be ZERO (banned/removed) ---"
for pat in "heroForm" "you@email.com" "Get instant access" "game-changer" "don't miss out" "unlock your potential" "background:var(--gold)" "background:var(--coral)"; do
  printf "  %-40s %s\n" "$pat" "$(echo "$H" | grep -ci "$pat")"
done
echo
echo "  --- inventory ---"
printf "  %-40s %s\n" "<img> tags"    "$(echo "$H" | grep -oE '<img' | wc -l)"
printf "  %-40s %s\n" "<video> tags"  "$(echo "$H" | grep -oE '<video' | wc -l)"
printf "  %-40s %s\n" "FAQ items"     "$(echo "$H" | grep -oE '<details' | wc -l)"
printf "  %-40s %s\n" "primary CTAs"  "$(echo "$H" | grep -oE 'btn-primary' | wc -l)"
echo
echo "=== 6. release ==="
bash /data/scripts/deploy_lock.sh release worker butler 2>&1 | tail -2