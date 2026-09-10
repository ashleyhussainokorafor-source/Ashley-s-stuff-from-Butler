#!/usr/bin/env python3
import os
import json
import pickle
from google_auth_oauthlib.flow import Flow

CLIENT_SECRET_FILE = "/data/workspace/afroviolin/artifacts/client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob" # OOB is deprecated for new clients but some older projects allow it.
# As a fallback, we can use localhost redirect and have the user paste the redirected URL or code.
REDIRECT_URI_LOCALHOST = "http://localhost:8080" 

def main():
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: Client secret file not found at {CLIENT_SECRET_FILE}")
        return

    # Use localhost as redirect URI
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8080"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    
    print("\n" + "="*80)
    print("YOUTUBE AUTHENTICATION SETUP")
    print("="*80)
    print("Please visit the following URL in your browser to authorize this application:")
    print(f"\n{auth_url}\n")
    print("Instructions:")
    print("1. Sign in to your YouTube channel's Google account.")
    print("2. Approve permissions.")
    print("3. After approving, your browser will redirect you to a page that fails to load")
    print("   (e.g., http://localhost:8080/?code=4/0Ad...&scope=...)")
    print("4. Copy the ENTIRE URL from your browser's address bar and paste it below!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
