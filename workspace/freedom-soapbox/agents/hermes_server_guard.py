#!/usr/bin/env python3
"""
Hermes Server Guard (Option 1)
Wraps Hermes server startup with load/memory protection.

Usage (in container or startup script):
    python agents/hermes_server_guard.py -- python -m server ...

It will:
- Check load before starting
- Wait (or exit) if the system is overloaded
- Then exec the real server command
"""
import os
import sys
import subprocess
from agents.load_guard import check_load_or_exit

def main():
    # Default thresholds for the Hermes server itself
    max_load = int(os.environ.get("HERMES_SERVER_MAX_LOAD", "55"))
    min_free_gb = float(os.environ.get("HERMES_SERVER_MIN_FREE_GB", "5.0"))

    print("[hermes_server_guard] Checking system health before starting Hermes...")
    check_load_or_exit(
        max_load=max_load,
        check_mem=True,
        min_free_gb=min_free_gb,
        wait=True,                 # Wait for relief instead of dying immediately
        max_wait_minutes=45,
    )

    print("[hermes_server_guard] System OK. Starting Hermes server...")

    # Everything after "--" is the real command
    if "--" in sys.argv:
        idx = sys.argv.index("--")
        cmd = sys.argv[idx + 1:]
    else:
        # Fallback: just run the normal server
        cmd = ["python", "server.py"]

    if not cmd:
        print("ERROR: No command specified after --")
        sys.exit(1)

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
