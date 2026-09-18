#!/bin/bash
# Deploy + verify. NOTE: verification makes ONE request per URL and captures
# status, size and content-type together — an earlier version made two calls
# per file and reported false 404s.
set -uo pipefail
cd /data/business/hca-daily/worker

check() {  # url -> "code size type"
  curl -s -L --max-time 20 -o /tmp/_probe -w "%{http_code} %{size_download} %{content_type}" "$1"
}

echo "=== 1. acquire deploy lock ==="
bash /data/scripts/deploy_lock.sh acquire worker butler 2>&1 | tail -2
echo

echo "=== 2. deploy ==="
set -a; source /data/.cloudflare.env 2>/dev/null; set +a
export CLOUDFLARE_ACCOUNT_ID=7331f696a15eee3fe7bf94f41376f7b8
npx --yes wrangler@4 deploy 2>&1 | grep -iE "Read [0-9]+ files|Uploaded|Version ID|error" | head -6
echo

echo "=== 3. verify images (single request each) ==="
for f in hero-wide.webp students-walking-laughing-800.webp grads-mantles-park-800.webp \
         group-study-diverse-800.webp multiracial-highfive-library-800.webp \
         black-woman-laptop-study-800.webp; do
  printf "  %-42s %s\n" "$f" "$(check "https://thehcadaily.com/img/$f")"
done
echo
echo "=== 4. quarantined must NOT be served (expect 404) ==="
for f in happy-black-man-university-800.webp east-asian-student-brickwall-800.webp; do
  printf "  %-42s %s\n" "$f" "$(check "https://thehcadaily.com/img/$f")"
done
echo

echo "=== 5. homepage content (cache-busted) ==="
H=$(curl -s -L --max-time 20 "https://thehcadaily.com/?cb=$(date +%s)")
printf "  new hero copy        : %s\n" "$(echo "$H" | grep -c 'Walk in already speaking')"
printf "  brand gold in CSS    : %s\n" "$(echo "$H" | grep -ci 'c9a227')"
printf "  <img> tags           : %s\n" "$(echo "$H" | grep -oE '<img' | wc -l)"
printf "  photo band present   : %s\n" "$(echo "$H" | grep -c 'imgband')"
printf "  image cards present  : %s\n" "$(echo "$H" | grep -c 'imgcards')"
printf "  gold .btn rule       : %s\n" "$(echo "$H" | grep -c 'background:var(--gold)')"
echo

echo "=== 6. release lock ==="
bash /data/scripts/deploy_lock.sh release worker butler 2>&1 | tail -2