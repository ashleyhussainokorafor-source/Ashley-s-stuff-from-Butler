#!/usr/bin/env python3
"""
Desktop OAuth Script for Afroviolin V2 Token
Run this on your local Windows/Mac machine (where you have a web browser).

Usage:
1. Ensure you have dependencies: pip install google-auth-oauthlib google-api-python-client
2. Copy 'client_secret.json' from the project 'artifacts/' folder to the same directory as this script.
3. Run: python get_v2_token.py
4. A browser will open. Log in with the SECOND Google account.
5. The script will save 'youtube_token_v2.json' in the current directory.
6. Upload/Copy 'youtube_token_v2.json' back to the server: /data/workspace/afroviolin/artifacts/
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

CLIENT_SECRET_FILE = 'client_secret.json'
OUTPUT_TOKEN_FILE = 'youtube_token_v2.json'

def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"ERROR: '{CLIENT_SECRET_FILE}' not found in the current directory.")
        print("Please copy it from the server: /data/workspace/afroviolin/artifacts/client_secret.json")
        return

    print("Starting OAuth flow for V2 Channel...")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    
    # This opens a browser window on your local machine
    creds = flow.run_local_server(port=0)

    # Save the credentials
    with open(OUTPUT_TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print(f"\nSUCCESS!")
    print(f"Token saved to: {os.path.abspath(OUTPUT_TOKEN_FILE)}")
    print("Copy this file back to the server to enable the second channel profile.")

if __name__ == "__main__":
    main()