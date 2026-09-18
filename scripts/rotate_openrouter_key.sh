#!/usr/bin/env bash
# rotate_openrouter_key.sh — swap the OpenRouter API key everywhere it lives.
#
#   rotate_openrouter_key.sh <new-key>          # apply + verify
#   rotate_openrouter_key.sh --check <key>      # verify a key without changing anything
#   rotate_openrouter_key.sh --list             # show every location holding the key
#
# The key lives in 8 places. Rotating by hand misses one and things break
# silently hours later, so this updates all of them atomically and then proves
# the new key actually authenticates.
set -u

CF_ENV=/data/.cloudflare.env
ACCT=7331f696a15eee3fe7bf94f41376f7b8
WORKER=hca-daily

locations() {
  printf '%s\n' /data/.env
  for f in /data/profiles/*/.env; do [ -f "$f" ] && printf '%s\n' "$f"; done
}

cmd="${1:-}"

if [ "$cmd" = "--list" ]; then
  echo "Locations holding OPENROUTER_API_KEY:"
  locations | while read -r f; do
    k=$(grep -oE '^OPENROUTER_API_KEY=.*' "$f" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' ')
    [ -n "$k" ] && printf "  %-38s %s…%s\n" "$f" "${k:0:14}" "${k: -4}"
  done
  echo "  Cloudflare Worker secret      (via wrangler/API)"
  exit 0
fi

if [ "$cmd" = "--check" ]; then
  KEY="${2:?key required}"
  code=$(curl -s -o /tmp/keychk.json -w '%{http_code}' \
    "https://openrouter.ai/api/v1/key" -H "Authorization: Bearer $KEY")
  if [ "$code" = "200" ]; then
    python3 -c "
import json; d=json.load(open('/tmp/keychk.json')); dd=d.get('data',d)
print('  VALID — label:', dd.get('label'), '| usage:', dd.get('usage'), '| limit:', dd.get('limit'))
"
    exit 0
  fi
  echo "  INVALID or unauthorised (HTTP $code)"; exit 1
fi

NEW="${cmd:-}"
if [ -z "$NEW" ]; then
  echo "usage: rotate_openrouter_key.sh <new-key> | --check <key> | --list" >&2
  exit 2
fi

echo "=== 0. verify the NEW key works BEFORE changing anything ==="
if ! bash "$0" --check "$NEW"; then
  echo "Aborting — the new key does not authenticate. Nothing was changed."
  exit 1
fi

echo
echo "=== 1. back up current values (600, gitignored) ==="
BAK="/data/.openrouter-key-backup-$(date -u +%Y%m%dT%H%M%SZ).txt"
: > "$BAK"; chmod 600 "$BAK"
locations | while read -r f; do
  grep -oE '^OPENROUTER_API_KEY=.*' "$f" 2>/dev/null | sed "s|^|$f |" >> "$BAK"
done
echo "  wrote $BAK ($(wc -l < "$BAK") entries)"

echo
echo "=== 2. update every .env ==="
locations | while read -r f; do
  if grep -q '^OPENROUTER_API_KEY=' "$f" 2>/dev/null; then
    python3 - "$f" "$NEW" <<'PY'
import sys
path, new = sys.argv[1], sys.argv[2]
lines = open(path).read().splitlines(True)
out, done = [], False
for ln in lines:
    if ln.startswith("OPENROUTER_API_KEY="):
        out.append(f"OPENROUTER_API_KEY={new}\n"); done = True
    else:
        out.append(ln)
if not done:
    out.append(f"OPENROUTER_API_KEY={new}\n")
open(path, "w").writelines(out)
PY
    echo "  updated $f"
  fi
done

echo
echo "=== 3. update the Cloudflare Worker secret ==="
if [ -f "$CF_ENV" ]; then
  set -a; . "$CF_ENV"; set +a
  curl -s -X PUT \
    "https://api.cloudflare.com/client/v4/accounts/$ACCT/workers/scripts/$WORKER/secrets" \
    -H "X-Auth-Key: $CLOUDFLARE_API_KEY" -H "X-Auth-Email: $CLOUDFLARE_EMAIL" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"OPENROUTER_API_KEY\",\"text\":\"$NEW\",\"type\":\"secret_text\"}" \
    -o /tmp/secput.json -w "  PUT secret -> HTTP %{http_code}\n"
  python3 -c "
import json
try:
    d=json.load(open('/tmp/secput.json')); print('  success:', d.get('success'))
except Exception: print('  (could not parse response)')
"
else
  echo "  SKIPPED: $CF_ENV not found"
fi

echo
echo "=== 4. verify every location now holds the new key ==="
locations | while read -r f; do
  k=$(grep -oE '^OPENROUTER_API_KEY=.*' "$f" 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' ')
  if [ "$k" = "$NEW" ]; then echo "  OK   $f"; else echo "  MISMATCH $f"; fi
done

echo
echo "=== 5. DONE — now revoke the old key ==="
echo "  Go to https://openrouter.ai/settings/keys and DELETE the old key."
echo "  Until you do, the old key still works. Rotation is not finished until it's revoked."
echo "  Backup of previous values: $BAK"
