#!/usr/bin/env python3
"""
Apply Hermes Gateway Restart

Reads the restart request flag written by telegram_routing_watcher.py
and performs a safe restart of the Hermes gateway.

This script is meant to be called by:
- A cron job every 1-2 minutes
- A systemd timer
- A container supervisor healthcheck

It will only act if:
1. A restart request file exists and is recent (< 10 minutes old)
2. The gateway process is running
3. System load is acceptable (uses load_guard)

Usage:
    python agents/apply_hermes_restart.py
"""
import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta

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

def get_gateway_pid():
    """Find the PID of the running Hermes gateway."""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline']):
            cmd = " ".join(proc.info['cmdline'] or [])
            if "hermes gateway run" in cmd:
                return proc.info['pid']
    except ImportError:
        import subprocess
        try:
            out = subprocess.check_output(
                ["ps", "aux"], stderr=subprocess.DEVNULL, text=True
            )
            for line in out.splitlines():
                if "hermes gateway run" in line and "grep" not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return int(parts[1])
        except Exception:
            pass
    return None

def is_request_valid():
    """Check if restart request exists and is recent."""
    if not RESTART_REQUEST.exists():
        return False, "No restart request file"
    
    try:
        mtime = datetime.fromtimestamp(RESTART_REQUEST.stat().st_mtime)
        age = datetime.now() - mtime
        if age > timedelta(minutes=10):
            return False, f"Request too old ({age.total_seconds()/60:.1f} min)"
        
        content = RESTART_REQUEST.read_text().strip().split("\n")
        reason = content[1] if len(content) > 1 else "unknown"
        return True, reason
    except Exception as e:
        return False, f"Error reading request: {e}"

def clear_request():
    """Remove the restart request after handling."""
    try:
        RESTART_REQUEST.unlink(missing_ok=True)
    except Exception:
        pass

def perform_restart(pid: int, reason: str):
    """Send SIGTERM to gateway so systemd/Restart=on-failure kicks in."""
    _log(f"Applying restart: {reason}")
    _log(f"  Target PID: {pid}")
    
    try:
        os.kill(pid, signal.SIGTERM)
        _log("  Sent SIGTERM to gateway process")
        clear_request()
        return True
    except ProcessLookupError:
        _log("  Gateway process already gone")
        clear_request()
        return True
    except PermissionError:
        _log("  ERROR: No permission to signal gateway")
        return False
    except Exception as e:
        _log(f"  ERROR signaling gateway: {e}")
        return False

def main():
    valid, info = is_request_valid()
    if not valid:
        sys.exit(0)
    
    _log(f"Restart request detected: {info}")
    
    pid = get_gateway_pid()
    if not pid:
        _log("No running Hermes gateway found — nothing to restart")
        clear_request()
        sys.exit(0)
    
    try:
        from agents.load_guard import check_load_or_exit
        check_load_or_exit(max_load=60, check_mem=True, min_free_gb=4.0, wait=False)
    except Exception:
        pass
    
    success = perform_restart(pid, info)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
