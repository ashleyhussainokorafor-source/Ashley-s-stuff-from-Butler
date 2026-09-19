#!/bin/bash
# Deploy the 5-page imagery rollout and verify LIVE (one request per URL).
set -uo pipefail
cd /data/business/hca-daily/worker

probe() { curl -s -L --max-time 20 -o /tmp/_p -w "%{http_code} %{size_download} %{content_type}" "$1"; }

echo "=== 1. acquire deploy lock ==="
bash /data/scripts/deploy_lock.sh acquire worker butler 2>&1 | tail -2
echo

echo "=== 2. deploy ==="
set -a; source /data/.cloudflare.env 2>/dev/null; set +a
export CLOUDFLARE_ACCOUNT_ID=7331f696a15eee3fe7bf94f41376f7b8
npx --yes wrangler@4 deploy 2>&1 | grep -iE "Read [0-9]+ files|Uploaded|Version ID|error" | head -6
echo

echo "=== 3. every page still 200? (regression check) ==="
for p in "" vault accelerator pricing resume learn scorecard path practice league; do
  printf "  /%-12s %s\n" "$p" "$(probe "https://thehcadaily.com/$p")"
done
echo

echo "=== 4. imagery present on each page? (cache-busted) ==="
TS=$(date +%s)
for p in "" vault accelerator pricing resume; do
  H=$(curl -s -L --max-time 20 "https://thehcadaily.com/$p?cb=$TS")
  n=$(echo "$H" | grep -oE '<img' | wc -l)
  band=$(echo "$H" | grep -c 'hca-band')
  printf "  /%-12s <img>=%s  band=%s\n" "${p:-home}" "$n" "$band"
done
echo

echo "=== 5. brand gold on the two previously off-brand pages ==="
for p in pricing learn; do
  H=$(curl -s -L --max-time 20 "https://thehcadaily.com/$p?cb=$TS")
  printf "  /%-8s gold_vars=%s  coral_cta=%s\n" "$p" \
    "$(echo "$H" | grep -c 'c9a227')" "$(echo "$H" | grep -c 'background:var(--coral)')"
done
echo

echo "=== 6. release lock ==="
bash /data/scripts/deploy_lock.sh release worker butler 2>&1 | tail -2