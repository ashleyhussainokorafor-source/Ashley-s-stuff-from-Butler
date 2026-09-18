#!/usr/bin/env bash
# deploy_lock.sh — serialize production changes across agents.
#
#   deploy_lock.sh acquire <scope> <owner>   # exits 1 if someone else holds it
#   deploy_lock.sh release <scope> <owner>
#   deploy_lock.sh status
#
# A lock older than STALE_SECS is treated as abandoned (owner died) and can be
# taken over with a warning. This is deliberately simple: no daemon, no DB.
set -u

BUSY_DIR="/data/business/hca-daily/ops/locks"
STALE_SECS=3600
CMD="${1:-status}"

mkdir -p "$BUSY_DIR"

now() { date -u +%s; }
iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

case "$CMD" in
  acquire)
    scope="${2:?scope required}"; owner="${3:?owner required}"
    f="$BUSY_DIR/${scope//\//_}.lock"
    if [ -f "$f" ]; then
      prev_owner=$(sed -n '1p' "$f" 2>/dev/null)
      prev_time=$(sed -n '2p' "$f" 2>/dev/null)
      prev_epoch=$(sed -n '3p' "$f" 2>/dev/null)
      age=$(( $(now) - ${prev_epoch:-0} ))
      if [ "${prev_owner:-}" != "$owner" ] && [ "$age" -lt "$STALE_SECS" ]; then
        echo "HELD by '$prev_owner' since $prev_time (${age}s ago) — scope: $scope"
        echo "Stop. Ask Ashley who should proceed. Do not overwrite."
        exit 1
      fi
      [ "$age" -ge "$STALE_SECS" ] && echo "WARN: taking over stale lock from '$prev_owner' (${age}s old)"
    fi
    printf '%s\n%s\n%s\n' "$owner" "$(iso)" "$(now)" > "$f"
    echo "ACQUIRED $scope by $owner at $(iso)"
    ;;

  release)
    scope="${2:?scope required}"; owner="${3:?owner required}"
    f="$BUSY_DIR/${scope//\//_}.lock"
    if [ ! -f "$f" ]; then echo "no lock for $scope"; exit 0; fi
    if [ "$(sed -n '1p' "$f")" != "$owner" ]; then
      echo "REFUSED: lock for $scope is held by '$(sed -n '1p' "$f")', not $owner"
      exit 1
    fi
    rm -f "$f"
    echo "RELEASED $scope by $owner"
    ;;

  status)
    shopt -s nullglob
    files=("$BUSY_DIR"/*.lock)
    if [ ${#files[@]} -eq 0 ]; then echo "no active locks"; exit 0; fi
    for f in "${files[@]}"; do
      scope=$(basename "$f" .lock)
      owner=$(sed -n '1p' "$f"); t=$(sed -n '2p' "$f"); e=$(sed -n '3p' "$f")
      age=$(( $(now) - ${e:-0} ))
      flag=""; [ "$age" -ge "$STALE_SECS" ] && flag=" (STALE — safe to take over)"
      echo "  $scope | $owner | since $t | ${age}s${flag}"
    done
    ;;
  *)
    echo "usage: deploy_lock.sh {acquire|release|status} [scope] [owner]" >&2
    exit 2
    ;;
esac