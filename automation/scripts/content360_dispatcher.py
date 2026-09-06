#!/usr/bin/env python3
"""
Autonomous Content 360 Social Media Dispatcher
Integrates with Content 360 API to schedule LinkedIn posts and multi-platform content.
"""

import os
import json
import urllib.request
import urllib.error

API_KEY = os.environ.get("CONTENT360_API_KEY", "")
TEAM_ID = os.environ.get("CONTENT360_TEAM_ID", "c5f7d2a6-829c-4d4c-938a-01e8d09c53f5")

def get_social_accounts():
    endpoints = [
        f"https://api.content360.io/v1/teams/{TEAM_ID}/integrations",
        f"https://api.content360.io/v1/integrations",
        f"https://app.content360.io/api/v1/integrations"
    ]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    for url in endpoints:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            continue
    return None

if __name__ == "__main__":
    print(f"Content 360 Dispatcher initialized for Team: {TEAM_ID}")
    print("Ready to receive scheduled queue.")
