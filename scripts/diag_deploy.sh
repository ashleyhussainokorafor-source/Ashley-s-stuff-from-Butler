#!/bin/bash
# Diagnose why the deploy did not reach the live site.
echo "=== A. single-request check (status + size together) ==="
for f in img/hero-wide.webp img/grads-mantles-park-800.webp index.html; do
  for base in https://thehcadaily.com https://hca-daily.empathycollection.workers.dev; do
    out=$(curl -s -L --max-time 20 -o /tmp/_b -w "%{http_code} %{size_download} %{content_type}" "$base/$f")
    printf "  %-46s %s\n" "${base#https://}/$f" "$out"
  done
done
echo

echo "=== B. what is the deployed worker actually serving at / ? ==="
curl -s -L --max-time 20 https://thehcadaily.com/ | grep -oE "Walk in already speaking|hiring execs actually use|background:var\(--coral\)|/img/" | sort | uniq -c
echo "  ^ 'hiring execs' = OLD copy; 'Walk in already' = NEW copy"

echo
echo "=== C. edge cache headers on / ==="
curl -s -I -L --max-time 20 https://thehcadaily.com/ | grep -iE "^(cf-cache-status|age|cache-control|last-modified|etag|server)" | head

echo
echo "=== D. does the deployed version's asset manifest include the images? ==="
cd /data/business/hca-daily/worker
ls assets/img/*.webp 2>/dev/null | wc -l | sed 's/^/  local webp files: /'
grep -oE '"directory"[^,]*' wrangler.jsonc

echo
echo "=== E. did the last deploy include img/ ? (re-run dry)")
set -a; source /data/.cloudflare.env 2>/dev/null; set +a
export CLOUDFLARE_ACCOUNT_ID=7331f696a15eee3fe7bf94f41376f7b8
npx --yes wrangler@4 deploy --dry-run 2>&1 | grep -iE "Read [0-9]+ files|Total Upload|assets directory" | head -4