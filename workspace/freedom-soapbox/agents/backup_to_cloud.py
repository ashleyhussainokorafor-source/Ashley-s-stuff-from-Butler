#!/usr/bin/env python3
"""
backup_to_cloud.py — Afroviolin artifact backup to cloud storage.

Uses rclone (preferred) or falls back to AWS CLI / gsutil.
- Never uploads secrets (.env, *.env, tokens)
- Supports --dry-run for safe testing
- Respects system overload state (skips if overloaded)
- Creates dated backup manifests

Usage:
    python agents/backup_to_cloud.py --dry-run
    python agents/backup_to_cloud.py --remote gdrive:afroviolin-backups

Environment:
    AFROVIOLIN_CLOUD_REMOTE   default remote name (e.g. gdrive, s3, onedrive)
    AFROVIOLIN_SKIP_BACKUP=1  bypass entirely
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/data/workspace")
ARTIFACTS = PROJECT_ROOT / "afroviolin" / "artifacts"
BACKUP_ROOT = PROJECT_ROOT / "artifacts" / "backups"
LOG_DIR = PROJECT_ROOT / "logs"
STATE_FILE = PROJECT_ROOT / "system_state.json"

DEFAULT_REMOTE = os.environ.get("AFROVIOLIN_CLOUD_REMOTE", "gdrive:afroviolin-backups")
EXCLUDES = [
    ".env", "*.env", "client_secret.json", "youtube_token*.json",
    "__pycache__/", "*.pyc", "pending_*.pkl", "*.log"
]


def _log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def is_overloaded() -> bool:
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return json.load(f).get("overloaded", False)
    except Exception:
        pass
    return False


def run_rclone(src: Path, dest: str, dry_run: bool = True) -> bool:
    cmd = ["rclone", "sync", str(src), dest, "--exclude", "*.log"]
    for ex in EXCLUDES:
        cmd.extend(["--exclude", ex])
    if dry_run:
        cmd.append("--dry-run")
    _log(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            _log("rclone completed successfully")
            return True
        _log(f"rclone error: {result.stderr[:300]}")
        return False
    except FileNotFoundError:
        _log("rclone not found — install rclone or use AWS/gsutil fallback")
        return False
    except Exception as e:
        _log(f"rclone exception: {e}")
        return False


def create_manifest(backup_name: str):
    manifest = {
        "backup_name": backup_name,
        "timestamp": datetime.now().isoformat(),
        "source": str(ARTIFACTS),
        "remote": DEFAULT_REMOTE,
        "excludes": EXCLUDES,
    }
    manifest_path = BACKUP_ROOT / f"{backup_name}_manifest.json"
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    _log(f"Manifest written: {manifest_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without uploading")
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="rclone remote destination")
    args = parser.parse_args()

    if os.environ.get("AFROVIOLIN_SKIP_BACKUP") == "1":
        _log("Backup skipped via AFROVIOLIN_SKIP_BACKUP=1")
        return

    if is_overloaded():
        _log("System overloaded — skipping backup this cycle")
        return

    if not ARTIFACTS.exists():
        _log(f"No artifacts dir at {ARTIFACTS}")
        return

    backup_name = datetime.now().strftime("backup_%Y%m%d_%H%M%S")
    _log(f"Starting backup: {backup_name} (dry_run={args.dry_run})")

    success = run_rclone(ARTIFACTS, args.remote, dry_run=args.dry_run)
    if success and not args.dry_run:
        create_manifest(backup_name)
        _log("Backup complete")
    elif args.dry_run:
        _log("Dry-run complete — no files uploaded")


if __name__ == "__main__":
    main()
