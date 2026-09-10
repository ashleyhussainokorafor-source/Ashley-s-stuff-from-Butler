#!/usr/bin/env python3
"""
Cloudflare R2 Storage Manager
Automates bucket + token + rclone remote setup for new projects.

Usage:
    python storage_manager.py new-project-name
    python storage_manager.py --list
    python storage_manager.py --check
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RCLONE_CONFIG = Path.home() / ".config" / "rclone" / "rclone.conf"
STORAGE_GUARD = Path(__file__).parent / "storage_guard.py"

def check_local_storage(threshold=50):
    """Ensure local storage usage is under threshold."""
    usage = shutil.disk_usage("/")
    percent = (usage.used / usage.total) * 100
    if percent > threshold:
        print(f"❌ CRITICAL: Local storage at {percent:.1f}% (limit: {threshold}%)")
        return False
    print(f"✅ Local storage at {percent:.1f}% (under {threshold}%)")
    return True

def create_rclone_remote(project_name: str, access_key: str, secret_key: str, 
                         endpoint: str, bucket: str):
    """Add a new rclone remote for the project."""
    remote_name = f"cloudflare-{project_name}"
    
    config_lines = [
        f"\n[{remote_name}]",
        "type = s3",
        "provider = Cloudflare",
        f"access_key_id = {access_key}",
        f"secret_access_key = {secret_key}",
        f"endpoint = {endpoint}",
        "acl = private",
        f"bucket = {bucket}",
    ]
    
    with open(RCLONE_CONFIG, "a") as f:
        f.write("\n".join(config_lines) + "\n")
    
    print(f"✅ Added rclone remote: {remote_name}")
    return remote_name

def update_project_env(project_root: Path, remote_name: str, bucket: str, base_path: str):
    """Update project .env with storage settings."""
    env_file = project_root / ".env"
    if not env_file.exists():
        print(f"⚠️  No .env found in {project_root}")
        return
    
    lines = [
        "",
        "# Storage Configuration (auto-generated)",
        f"STORAGE_MODE=cloudflare-r2",
        f"STORAGE_REMOTE={remote_name}",
        f"STORAGE_BUCKET={bucket}",
        f"STORAGE_BASE_PATH={base_path}",
        f"STORAGE_MAX_LOCAL_USAGE=50",
    ]
    
    with open(env_file, "a") as f:
        f.write("\n".join(lines) + "\n")
    
    print(f"✅ Updated {env_file} with storage settings")

def main():
    if len(sys.argv) < 2:
        print("Usage: storage_manager.py <project-name> | --list | --check")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "--check":
        check_local_storage()
        return
    
    if cmd == "--list":
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        print(result.stdout)
        return
    
    # New project flow
    project_name = cmd
    print(f"\n🚀 Setting up Cloudflare R2 storage for: {project_name}")
    
    if not check_local_storage():
        sys.exit(1)
    
    print("\nPlease create the following in Cloudflare Dashboard:")
    print(f"1. Bucket name: fs-records-{project_name}-assets")
    print(f"2. API Token with Object Read & Write on that bucket")
    print("\nThen paste the values below:")
    
    access_key = input("Access Key ID: ").strip()
    secret_key = input("Secret Access Key: ").strip()
    endpoint = input("Endpoint (https://...r2.cloudflarestorage.com): ").strip() or \
               "https://7331f696a15eee3fe7bf94f41376f7b8.r2.cloudflarestorage.com"
    bucket = input("Bucket name: ").strip()
    
    remote_name = create_rclone_remote(project_name, access_key, secret_key, endpoint, bucket)
    
    # Optional: update current project .env
    current_project = Path.cwd()
    if (current_project / ".env").exists():
        update_project_env(current_project, remote_name, bucket, f"{project_name}-assets")
    
    print(f"\n✅ Storage setup complete for {project_name}")
    print(f"   Remote: {remote_name}")
    print(f"   Bucket: {bucket}")
    print(f"   Usage: rclone ls {remote_name}:")

if __name__ == "__main__":
    main()
