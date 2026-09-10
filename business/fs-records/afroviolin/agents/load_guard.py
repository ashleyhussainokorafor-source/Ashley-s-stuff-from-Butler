#!/usr/bin/env python3
"""
Afroviolin Load Guard
Prevents heavy workloads from starting when the system is already overloaded.
Used to protect the Hermes VPS from thrashing / OOM / apparent shutdowns.

Usage:
    from agents.load_guard import check_load_or_exit

    check_load_or_exit(max_load=45, check_mem=True, min_free_gb=8)

Environment variables:
    AFROVIOLIN_SKIP_LOAD_GUARD=1   -> bypass entirely
    AFROVIOLIN_MAX_LOAD=50         -> override default threshold
"""
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
GUARD_LOG = LOG_DIR / "load_guard.log"


def _log(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(GUARD_LOG, "a") as f:
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
        mem_total = 0
        mem_available = 0
        for line in meminfo.splitlines():
            if line.startswith("MemTotal:"):
                mem_total = int(line.split()[1]) // 1024  # MB
            if line.startswith("MemAvailable:"):
                mem_available = int(line.split()[1]) // 1024
        if mem_total > 0:
            return mem_available / 1024.0
        return 999.0
    except Exception:
        return 999.0


def check_load_or_exit(
    max_load: int = 45,
    check_mem: bool = True,
    min_free_gb: float = 8.0,
    wait: bool = False,
    max_wait_minutes: int = 30,
):
    """
    Check system load and memory. Exit (or wait) if overloaded.

    max_load: 5-minute load average threshold (default 45 on 64-core box)
    """
    if os.environ.get("AFROVIOLIN_SKIP_LOAD_GUARD") == "1":
        _log("Load guard bypassed via env var")
        return

    override = os.environ.get("AFROVIOLIN_MAX_LOAD")
    if override:
        try:
            max_load = int(override)
        except ValueError:
            pass

    start_time = time.time()
    waited = 0

    while True:
        load1, load5, load15 = get_load_averages()
        free_gb = get_available_memory_gb()

        overloaded = load5 > max_load
        low_mem = check_mem and free_gb < min_free_gb

        if not overloaded and not low_mem:
            if waited > 0:
                _log(f"System recovered after {waited:.1f} min. Proceeding.")
            return

        reason = []
        if overloaded:
            reason.append(f"load5={load5:.1f} > {max_load}")
        if low_mem:
            reason.append(f"free_mem={free_gb:.1f}GB < {min_free_gb}GB")

        msg = f"System overloaded: {', '.join(reason)}"
        _log(msg)

        if not wait:
            _log("Exiting to protect system stability.")
            sys.exit(75)  # EX_TEMPFAIL style exit code

        waited = (time.time() - start_time) / 60
        if waited > max_wait_minutes:
            _log(f"Waited {waited:.1f} min without relief. Giving up.")
            sys.exit(75)

        sleep_minutes = min(5, max(1, int((load5 - max_load) / 10) + 1))
        _log(f"Waiting {sleep_minutes} min before retry...")
        time.sleep(sleep_minutes * 60)


if __name__ == "__main__":
    # Allow direct testing: python agents/load_guard.py
    check_load_or_exit(max_load=45, check_mem=True, wait=False)
