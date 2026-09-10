#!/usr/bin/env python3
"""
Telegram Gateway Automation Daemon for Hermes Bolt Profile
"""
import os
import sys
import time
import signal
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

PROFILE_ENV = Path("/data/profiles/bolt/.env")
RESTART_REQUEST = Path("/data/workspace/logs/hermes_restart_request.txt")
LOG_DIR = Path("/data/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "telegram_gateway_automation.log"
STATE_FILE = LOG_DIR / ".telegram_config_hash"

CHECK_INTERVAL = 60
RESTART_COOLDOWN = 300
MAX_REQUEST_AGE_MIN = 20

def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

def get_telegram_hash():
    if not PROFILE_ENV.exists():
        return None
    try:
        lines = [l.strip() for l in PROFILE_ENV.read_text().splitlines()
                 if l.strip().startswith("TELEGRAM_")]
        lines.sort()
        return hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16]
    except Exception:
        return None

def find_gateway_pid():
    try:
        import psutil
        for p in psutil.process_iter(["pid", "cmdline"]):
            cmd = " ".join(p.info.get("cmdline") or [])
            if "hermes gateway run" in cmd:
                return p.info["pid"]
    except Exception:
        pass
    try:
        import subprocess
        out = subprocess.check_output(["ps", "aux"], text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if "hermes gateway run" in line and "grep" not in line:
                return int(line.split()[1])
    except Exception:
        pass
    return None

def apply_restart_if_needed():
    if not RESTART_REQUEST.exists():
        return False
    try:
        age = datetime.now() - datetime.fromtimestamp(RESTART_REQUEST.stat().st_mtime)
        if age > timedelta(minutes=MAX_REQUEST_AGE_MIN):
            RESTART_REQUEST.unlink(missing_ok=True)
            return False

        content = RESTART_REQUEST.read_text().strip().split("\n")
        reason = content[1] if len(content) > 1 else "unknown"

        pid = find_gateway_pid()
        if not pid:
            RESTART_REQUEST.unlink(missing_ok=True)
            return False

        log(f"Applying restart: {reason} (PID {pid})")
        os.kill(pid, signal.SIGTERM)
        time.sleep(3)
        RESTART_REQUEST.unlink(missing_ok=True)
        log("SIGTERM sent — gateway restarting via supervisor")
        return True
    except ProcessLookupError:
        RESTART_REQUEST.unlink(missing_ok=True)
        return True
    except Exception as e:
        log(f"Restart error: {e}")
        return False

def main():
    log("Telegram Gateway Automation started")
    last_hash = STATE_FILE.read_text().strip() if STATE_FILE.exists() else None
    last_restart = datetime.min

    while True:
        try:
            apply_restart_if_needed()
            current = get_telegram_hash()
            if current and current != last_hash:
                if datetime.now() - last_restart > timedelta(seconds=RESTART_COOLDOWN):
                    try:
                        RESTART_REQUEST.parent.mkdir(parents=True, exist_ok=True)
                        with open(RESTART_REQUEST, "w") as f:
                            f.write(f"{datetime.now().isoformat()}\nTELEGRAM config changed\n")
                        log(f"Config changed {last_hash} -> {current} — restart requested")
                        last_restart = datetime.now()
                    except Exception:
                        pass
                last_hash = current
                STATE_FILE.write_text(current)
            elif not last_hash and current:
                STATE_FILE.write_text(current)
                last_hash = current
        except KeyboardInterrupt:
            break
        except Exception:
            pass
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
