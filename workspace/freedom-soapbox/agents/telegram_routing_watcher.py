#!/usr/bin/env python3
"""
Telegram Routing Watcher for Hermes Bolt Profile

Watches the bolt profile's .env for changes to TELEGRAM_ALLOWED_USERS or TELEGRAM_BOT_TOKEN.
When a change is detected that would affect routing (new users added), it triggers a safe gateway restart
by writing a restart request file that the host/container supervisor can act on.

This script is designed to run OUTSIDE the Hermes gateway process (e.g., as a cron job or separate daemon)
so it can safely request restarts without being killed by the gateway's anti-suicide guard.

Usage:
    python agents/telegram_routing_watcher.py --watch
    python agents/telegram_routing_watcher.py --check-once
"""
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime

PROFILE_ENV = Path("/data/profiles/bolt/.env")
RESTART_REQUEST = Path("/data/workspace/logs/hermes_restart_request.txt")
WATCHER_LOG = Path("/data/workspace/logs/telegram_routing_watcher.log")

def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(WATCHER_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_telegram_config_hash():
    """Extract and hash just the Telegram-related config lines."""
    if not PROFILE_ENV.exists():
        return None
    try:
        content = PROFILE_ENV.read_text()
        telegram_lines = [line.strip() for line in content.splitlines() 
                          if line.strip().startswith("TELEGRAM_")]
        telegram_lines.sort()
        joined = "\n".join(telegram_lines)
        return hashlib.sha256(joined.encode()).hexdigest()[:16]
    except Exception as e:
        _log(f"ERROR reading config: {e}")
        return None

def request_gateway_restart(reason: str):
    """Write a restart request that an external supervisor can act on."""
    try:
        RESTART_REQUEST.parent.mkdir(parents=True, exist_ok=True)
        with open(RESTART_REQUEST, "w") as f:
            f.write(f"{datetime.now().isoformat()}\n{reason}\n")
        _log(f"RESTART REQUESTED: {reason}")
        _log(f"  Flag written to: {RESTART_REQUEST}")
        return True
    except Exception as e:
        _log(f"ERROR writing restart request: {e}")
        return False

def check_and_act():
    """Check current config and request restart if needed."""
    current_hash = get_telegram_config_hash()
    if not current_hash:
        _log("No Telegram config found in bolt profile")
        return False

    # Compare with last known state
    state_file = Path("/data/workspace/logs/.telegram_config_state")
    last_hash = None
    if state_file.exists():
        try:
            last_hash = state_file.read_text().strip()
        except Exception:
            pass

    if last_hash and last_hash != current_hash:
        _log(f"Telegram config changed (hash {last_hash} -> {current_hash})")
        # Extract the actual new allowed users for logging
        try:
            content = PROFILE_ENV.read_text()
            for line in content.splitlines():
                if "TELEGRAM_ALLOWED_USERS" in line:
                    _log(f"  New allowed users: {line.split('=', 1)[1]}")
        except Exception:
            pass
        
        success = request_gateway_restart("TELEGRAM_ALLOWED_USERS or TELEGRAM_BOT_TOKEN changed")
        if success:
            state_file.write_text(current_hash)
        return success
    else:
        if not last_hash:
            state_file.write_text(current_hash)
            _log(f"Initial state recorded (hash {current_hash})")
        return False

def watch_loop(interval: int = 30):
    """Continuously watch for config changes."""
    _log("Telegram routing watcher started")
    _log(f"Watching: {PROFILE_ENV}")
    _log(f"Restart flag: {RESTART_REQUEST}")
    
    while True:
        try:
            check_and_act()
        except Exception as e:
            _log(f"Watch loop error: {e}")
        time.sleep(interval)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check-once":
        changed = check_and_act()
        sys.exit(0 if not changed else 10)  # Exit 10 = restart needed
    else:
        watch_loop()
