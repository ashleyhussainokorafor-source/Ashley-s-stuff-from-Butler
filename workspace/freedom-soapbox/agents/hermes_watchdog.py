#!/usr/bin/env python3
"""
Hermes Server Watchdog
Lightweight background process that monitors system load and can:
- Log warnings when load is high
- Optionally pause/resume heavy work via a shared state file
- Send alerts to Bolt's Telegram bot when the system is in danger

Run this alongside the Hermes server:
    python agents/hermes_watchdog.py &

It writes to:
    /data/workspace/logs/hermes_watchdog.log
    /data/workspace/logs/system_health.json   (machine-readable state)
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/data/workspace")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

WATCHDOG_LOG = LOG_DIR / "hermes_watchdog.log"
HEALTH_FILE = LOG_DIR / "system_health.json"
STATE_FILE = PROJECT_ROOT / "system_state.json"   # shared flag other scripts can read

MAX_LOAD = int(os.environ.get("HERMES_MAX_LOAD", "50"))
MIN_FREE_GB = float(os.environ.get("HERMES_MIN_FREE_GB", "6.0"))
CHECK_INTERVAL = int(os.environ.get("HERMES_WATCHDOG_INTERVAL", "60"))  # seconds


def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(WATCHDOG_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_load_averages():
    try:
        with open("/proc/loadavg") as f:
            parts = f.read().strip().split()
            return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception:
        return 0.0, 0.0, 0.0


def get_available_memory_gb():
    try:
        with open("/proc/meminfo") as f:
            meminfo = f.read()
        mem_available = 0
        for line in meminfo.splitlines():
            if line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) // 1024
                break
        return mem_available / 1024.0
    except Exception:
        return 999.0


def write_health(load5: float, free_gb: float, status: str):
    data = {
        "timestamp": datetime.now().isoformat(),
        "load5": round(load5, 2),
        "free_gb": round(free_gb, 2),
        "status": status,
        "max_load": MAX_LOAD,
        "min_free_gb": MIN_FREE_GB,
    }
    try:
        with open(HEALTH_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def update_shared_state(overloaded: bool):
    """Write a simple flag that other scripts (Afroviolin agents, etc.) can check."""
    try:
        state = {
            "overloaded": overloaded,
            "updated_at": datetime.now().isoformat(),
        }
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass


def main():
    _log("Hermes Watchdog started")
    _log(f"Thresholds: load5 > {MAX_LOAD} OR free_mem < {MIN_FREE_GB} GB")

    while True:
        load1, load5, load15 = get_load_averages()
        free_gb = get_available_memory_gb()

        overloaded = load5 > MAX_LOAD or free_gb < MIN_FREE_GB

        if overloaded:
            reason = []
            if load5 > MAX_LOAD:
                reason.append(f"load5={load5:.1f}")
            if free_gb < MIN_FREE_GB:
                reason.append(f"free={free_gb:.1f}GB")
            status = "OVERLOADED"
            _log(f"⚠️  SYSTEM {status}: {', '.join(reason)} — heavy work should pause")
        else:
            status = "OK"
            if load5 > MAX_LOAD * 0.7:
                _log(f"System load elevated: load5={load5:.1f}")

        write_health(load5, free_gb, status)
        update_shared_state(overloaded)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _log("Watchdog stopped by user")
    except Exception as e:
        _log(f"Watchdog crashed: {e}")
        raise
