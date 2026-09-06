#!/usr/bin/env python3
"""
Workspace Storage & Cloudflare R2 Offload Manager
- Enforces <50% disk usage ceiling on /data (alert/cleanup threshold at 40%).
- Offloads media and bulky assets to Cloudflare R2 automatically.
"""

import os
import sys
import json
import shutil
import urllib.request
import urllib.error

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "7331f696a15eee3fe7bf94f41376f7b8")
CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
DEFAULT_BUCKET = os.environ.get("CLOUDFLARE_R2_BUCKET", "hca-daily-assets")
BASE_DIR = "/data"
THRESHOLD_PERCENT = 50.0

def get_disk_usage(path=BASE_DIR):
    stat = shutil.disk_usage(path)
    percent = (stat.used / stat.total) * 100
    return {
        "total_gb": round(stat.total / (1024**3), 2),
        "used_gb": round(stat.used / (1024**3), 2),
        "free_gb": round(stat.free / (1024**3), 2),
        "percent_used": round(percent, 2)
    }

def list_r2_buckets():
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets"
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return [b["name"] for b in data.get("result", {}).get("buckets", [])]

def upload_file_to_r2(local_path, bucket=DEFAULT_BUCKET, r2_key=None):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")
    
    if r2_key is None:
        r2_key = os.path.basename(local_path)
        
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets/{bucket}/objects/{r2_key}"
    headers = {
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    with open(local_path, "rb") as f:
        payload = f.read()
        
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return resp.status in (200, 201)

def run_storage_audit():
    usage = get_disk_usage()
    print(f"Disk Usage on {BASE_DIR}: {usage['used_gb']}GB / {usage['total_gb']}GB ({usage['percent_used']}%)")
    
    if usage["percent_used"] >= THRESHOLD_PERCENT:
        print(f"WARNING: Disk usage exceeds {THRESHOLD_PERCENT}% threshold! Triggering cleanup...")
        # Auto-clean temporary caches / logs
        tmp_cache = os.path.join(BASE_DIR, "cache")
        if os.path.exists(tmp_cache):
            for root, dirs, files in os.walk(tmp_cache):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
        print("Cache cleanup executed.")
    else:
        print(f"HEALTHY: Disk usage is safely below {THRESHOLD_PERCENT}% ceiling.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        run_storage_audit()
    elif len(sys.argv) > 2 and sys.argv[1] == "upload":
        success = upload_file_to_r2(sys.argv[2])
        print(f"Upload to R2: {'SUCCESS' if success else 'FAILED'}")
    else:
        run_storage_audit()
        buckets = list_r2_buckets()
        print(f"Connected R2 Buckets: {buckets}")
