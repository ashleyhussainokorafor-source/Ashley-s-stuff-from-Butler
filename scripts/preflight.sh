#!/usr/bin/env bash
# preflight.sh — refuse to let an agent start work that another agent is mid-flight on.
#
#   preflight.sh <path> <your-agent-name>
#   exit 0 = clear to proceed
#   exit 1 = STOP: someone else is on it, or it changed under you
#
# Checks, in order:
#   1. active deploy lock on this path
#   2. file modified within FRESH_SECS (someone is editing RIGHT NOW)
#   3. local branch diverged from origin, touching this path
#   4. the file is already committed upstream by someone else since you last pulled
set -u

TARGET="${1:-}"; ME="${2:-unknown}"
FRESH_SECS=900   # 15 minutes

if [ -z "$TARGET" ]; then
  echo "usage: preflight.sh <path> <your-agent-name>" >&2; exit 2
fi

REPO=/data
cd "$REPO" || exit 2
FAIL=0

echo "preflight: $ME -> $TARGET"

# 1. lock
LOCKDIR="$REPO/business/hca-daily/ops/locks"
if [ -d "$LOCKDIR" ]; then
  for lf in "$LOCKDIR"/*.lock; do
    [ -e "$lf" ] || continue
    owner=$(sed -n '1p' "$lf" 2>/dev/null); ts=$(sed -n '3p' "$lf" 2>/dev/null)
    age=$(( $(date -u +%s) - ${ts:-0} ))
    if [ "$owner" != "$ME" ] && [ "$age" -lt 3600 ]; then
      echo "  BLOCKED: lock held by '$owner' (${age}s ago) — $lf"
      FAIL=1
    fi
  done
fi

# 2. freshness — only meaningful for files git already knows about.
#    A brand-new untracked file is almost certainly the caller's own work, so
#    freshness must not block it (that produced a false STOP on first run).
TRACKED=0
if git ls-files --error-unmatch "$TARGET" >/dev/null 2>&1; then TRACKED=1; fi
if [ -e "$TARGET" ]; then
  mt=$(stat -c %Y "$TARGET" 2>/dev/null || echo 0)
  age=$(( $(date -u +%s) - mt ))
  echo "  last modified: ${age}s ago (tracked=$TRACKED)"
  if [ "$TRACKED" -eq 1 ] && [ "$age" -lt "$FRESH_SECS" ]; then
    echo "  BLOCKED: tracked file modified ${age}s ago (< ${FRESH_SECS}s)."
    echo "           Someone is editing this now."
    FAIL=1
  elif [ "$TRACKED" -eq 0 ]; then
    echo "  note: untracked — assuming this is your own new work, not a collision."
  fi
else
  echo "  note: $TARGET does not exist yet (new file — allowed)"
fi

# 3. divergence
git fetch -q origin 2>/dev/null
ahead=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
echo "  branch: ahead $ahead, behind $behind"
if [ "$behind" -gt 0 ]; then
  touched=$(git log --name-only --oneline HEAD..origin/main 2>/dev/null | grep -Fxq "$TARGET" && echo yes || echo no)
  if [ "$touched" = "yes" ]; then
    echo "  BLOCKED: origin/main already changed $TARGET since you branched."
    echo "           Pull/rebase first, or you will write stale content over theirs."
    FAIL=1
  fi
fi

# 4. uncommitted edits by others in the shared tree
dirty=$(git status --porcelain -- "$TARGET" 2>/dev/null | head -3)
if [ -n "$dirty" ]; then
  echo "  note: uncommitted changes present in the shared tree:"
  echo "$dirty" | sed 's/^/    /'
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "PASS — clear to work. Remember: acquire the lock before you deploy."
  exit 0
else
  echo "STOP — do not edit. Report this in the chat and let Ashley decide who proceeds."
  exit 1
fi