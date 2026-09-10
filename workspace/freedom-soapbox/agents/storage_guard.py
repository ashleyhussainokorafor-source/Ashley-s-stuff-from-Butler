#!/usr/bin/env python3
"""
Storage Guard — keeps disk usage under 50% by triggering cloud backups.

Monitors the workspace mount and:
- Logs current usage every check
- Triggers backup script when usage >= 50%
- Respects shared overload state from hermes_watchdog
- Writes alerts to logs/storage_guard.log

Intended to run alongside hermes_watchdog.py (or via cron).
"""

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/data/workspace")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

STORAGE_LOG = LOG_DIR / "storage_guard.log"
HEALTH_FILE = LOG_DIR / "system_health.json"
STATE_FILE = PROJECT_ROOT / "system_state.json"
BACKUP_SCRIPT = PROJECT_ROOT / "agents" / "backup_to_cloud.py"

THRESHOLD_PCT = float(os.environ.get("STORAGE_GUARD_THRESHOLD", "50.0"))
CHECK_INTERVAL = int(os.environ.get("STORAGE_GUARD_INTERVAL", "300"))  # 5 min default


def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(STORAGE_LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_disk_usage(path: str = "/data") -> float:
    try:
        total, used, free = shutil.disk_usage(path)
        pct = (used / total) * 100.0
        return round(pct, 1)
    except Exception:
        return 0.0


def is_system_overloaded() -> bool:
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
            return state.get("overloaded", False)
    except Exception:
        pass
    return False


def trigger_backup(dry_run: bool = True):
    if not BACKUP_SCRIPT.exists():
        _log("ERROR: backup_to_cloud.py not found — cannot trigger backup")
        return False

    cmd = ["python", str(BACKUP_SCRIPT)]
    if dry_run:
        cmd.append("--dry-run")

    _log(f"Triggering backup: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            _log("Backup script completed successfully")
            return True
        else:
            _log(f"Backup script failed: {result.stderr[:500]}")
            return False
    except Exception as e:
        _log(f"Backup trigger error: {e}")
        return False


def main():
    _log(f"Storage Guard started — threshold={THRESHOLD_PCT}%")
    while True:
        usage = get_disk_usage("/data")
        overloaded = is_system_overloaded()

        if usage >= THRESHOLD_PCT:
            _log(f"⚠️  STORAGE ALERT: {usage}% used (>= {THRESHOLD_PCT}%)")
            if overloaded:
                _log("System is overloaded — skipping backup this cycle")
            else:
                _log("Triggering cloud backup (respecting overload state)")
                trigger_backup(dry_run=False)
        else:
            if usage > THRESHOLD_PCT * 0.8:
                _log(f"Storage elevated: {usage}% (approaching {THRESHOLD_PCT}%)")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _log("Storage Guard stopped by user")
    except Exception as e:
        _log(f"Storage Guard crashed: {e}")
        raise
