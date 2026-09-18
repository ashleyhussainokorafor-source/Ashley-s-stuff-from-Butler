#!/bin/bash
# Clean gateway restart trigger (run by Hermes cron).
#
# Detaches the restart so the cron tick records cleanly, then bounces the
# gateway a few seconds later. On respawn the gateway reloads config.yaml,
# which activates the new model routing (flash delegation + free fallback).
#
# Detached via a subshell so the no_agent cron tick exits 0 immediately and
# its stdout stays empty (no delivery spam).
( sleep 8; /opt/venv/bin/hermes gateway restart ) >> /tmp/gateway_restart.log 2>&1 &
exit 0