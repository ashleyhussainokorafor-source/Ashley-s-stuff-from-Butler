#!/usr/bin/env python3
"""Storage guard - ensures local usage never exceeds 50%."""
import shutil
import sys

def check_storage(path="/data", threshold=50):
    usage = shutil.disk_usage(path)
    percent_used = (usage.used / usage.total) * 100
    free_gb = usage.free / (1024**3)
    total_gb = usage.total / (1024**3)
    
    if percent_used > threshold:
        print(f"CRITICAL: Storage at {percent_used:.1f}% (threshold: {threshold}%)")
        print(f"Free: {free_gb:.1f} GB / {total_gb:.1f} GB")
        return False
    print(f"OK: Storage at {percent_used:.1f}% (under {threshold}% threshold)")
    print(f"Free: {free_gb:.1f} GB / {total_gb:.1f} GB")
    return True

if __name__ == "__main__":
    if not check_storage():
        sys.exit(1)
