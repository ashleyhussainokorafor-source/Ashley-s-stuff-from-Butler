#!/usr/bin/env python3
"""
Afroviolin Multi-Channel Dispatcher
Loads channel profiles from config/channels.json and returns authenticated service objects.
"""

import os
import json
import argparse
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "channels.json"

def load_config():
    """Loads the channel profile map."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def get_credentials(profile_name: str) -> Credentials:
    """Loads credentials for a specific profile."""
    config = load_config()
    profiles = config.get("profiles", {})
    
    if profile_name not in profiles:
        raise ValueError(f"Profile '{profile_name}' not found in config.")
    
    profile = profiles[profile_name]
    token_path = PROJECT_ROOT / profile["token_file"]
    
    if not token_path.exists():
        raise FileNotFoundError(f"Token file not found for profile {profile_name}: {token_path}")
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    return Credentials.from_authorized_user_info(token_data)

def get_youtube_service(profile_name: str):
    """
    Returns an authenticated YouTube Data API v3 service object for the specified profile.
    """
    creds = get_credentials(profile_name)
    # 'youtube' is the API name, 'v3' is the version
    service = build('youtube', 'v3', credentials=creds)
    return service

def list_profiles():
    """Prints available profiles for debugging."""
    config = load_config()
    print("Available Channel Profiles:")
    for name, details in config.get("profiles", {}).items():
        status = details.get("status", "unknown")
        print(f"  - {name} ({details.get('channel_name', 'N/A')}) | Status: {status}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Afroviolin Channel Dispatcher Utility")
    parser.add_argument("--list", action="store_true", help="List available profiles.")
    parser.add_argument("--validate", type=str, help="Validate credentials for a specific profile.")
    
    args = parser.parse_args()
    
    if args.list:
        list_profiles()
    elif args.validate:
        try:
            service = get_youtube_service(args.validate)
            # Test the connection by fetching the channel title
            res = service.channels().list(part="snippet", mine=True).execute()
            if res.get("items"):
                print(f"Validation successful for '{args.validate}': {res['items'][0]['snippet']['title']}")
            else:
                print(f"Validation successful for '{args.validate}', but no channels found.")
        except Exception as e:
            print(f"Validation failed for '{args.validate}': {e}")
    else:
        parser.print_help()