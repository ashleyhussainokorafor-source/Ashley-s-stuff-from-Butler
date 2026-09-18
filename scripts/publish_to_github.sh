#!/bin/bash
# Publish work to GitHub — one command, safe by construction.
#
# WHY THIS EXISTS
# The local /data git history CANNOT be pushed. Commit 7de1bbd contains a live
# OpenRouter API key at profiles/bolt/state.db:11698, and GitHub push protection
# correctly refuses the entire ref. Any agent that just runs `git push` will be
# blocked and may wrongly conclude "the remote is broken".
#
# WHAT IT DOES
# Rebuilds the CURRENT WORKING TREE as a single clean commit on top of
# origin/main, in a throwaway worktree, then pushes. No poisoned history, no
# rejected pushes, no force.
#
# USAGE
#   scripts/publish_to_github.sh "feat(hca-daily): what changed"
#   scripts/publish_to_github.sh "msg" path/one path/two   # limit what is published
#
# HOUSE RULE: push as you go. Unpushed work is invisible to every other agent,
# and it is what makes two agents duplicate each other's work.
set -euo pipefail

MSG="${1:?usage: publish_to_github.sh \"<commit message>\" [path ...]}"
shift || true

REPO=/data
WT=/tmp/publish-wt
PATHS=("$@")
if [ ${#PATHS[@]} -eq 0 ]; then
  PATHS=(.gitignore agents.md automation business scripts)
fi

cd "$REPO"
git config credential.helper "store --file=/data/.git-credentials" 2>/dev/null || true

echo "→ fetching origin"
git fetch -q origin

echo "→ building a clean worktree on origin/main"
rm -rf "$WT"
git worktree add -q --detach "$WT" origin/main

echo "→ copying current work (${PATHS[*]})"
for p in "${PATHS[@]}"; do
  [ -e "$REPO/$p" ] || { echo "   skip (missing): $p"; continue; }
  mkdir -p "$WT/$(dirname "$p")"
  cp -a "$REPO/$p" "$WT/$(dirname "$p")/"
done

cd "$WT"
git add -A

if git diff --cached --quiet; then
  echo "→ nothing to publish (remote already matches)"
  cd "$REPO" && git worktree remove --force "$WT" >/dev/null 2>&1 || true
  exit 0
fi

echo "→ secret scan before committing"
if git diff --cached -U0 | grep -E '^\+' | grep -qE \
   'sk-[a-zA-Z0-9]{20}|rk_live_[a-zA-Z0-9]{12}|rk_test_[a-zA-Z0-9]{12}|AIza[0-9A-Za-z_-]{25}'; then
  echo "!! ABORT: a live-looking API key is staged. Not publishing."
  cd "$REPO" && git worktree remove --force "$WT" >/dev/null 2>&1 || true
  exit 1
fi

git commit -q -m "$MSG"
echo "→ commit $(git rev-parse --short HEAD)"

echo "→ pushing to origin/main"
git push -q origin HEAD:main
echo "✓ published: $(git rev-parse --short HEAD) -> origin/main"

cd "$REPO"
git worktree remove --force "$WT" >/dev/null 2>&1 || true
echo "✓ done"