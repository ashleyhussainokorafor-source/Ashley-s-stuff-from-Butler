#!/usr/bin/env bash
# Relaunch the multi-bot profile gateways detached from any parent shell.
# Why: on 2026-09-18T16:33:39Z hcadaily+fsrecords(+family/book) got SIGTERM when the
# bash that launched them died. setsid detaches them so that cannot recur.
set -u

PROFILES="hcadaily fsrecords family book"
HERMES=/opt/venv/bin/hermes

for p in $PROFILES; do
  echo "--- $p ---"
  lock="/data/profiles/$p/gateway.lock"
  if [ -f "$lock" ]; then
    lockpid=$(tr -dc '0-9' < "$lock")
    if [ -n "$lockpid" ] && kill -0 "$lockpid" 2>/dev/null; then
      echo "SKIP: lock held by live pid $lockpid"
      continue
    fi
    rm -f "$lock" && echo "removed stale lock (was pid ${lockpid:-unknown})"
  fi
  setsid bash -lc "cd /data && exec $HERMES --profile $p gateway run" \
    >> "/data/profiles/$p/logs/gateway.log" 2>&1 &
  echo "launched (detached)"
  sleep 1
done

echo
echo "=== startup settle ==="
sleep 15
echo "=== running gateways ==="
ps -eo pid,ppid,etimes,args | grep -E "hermes .*gateway run" | grep -v grep
echo
echo "done"