#!/usr/bin/env python3
import os
import json
from google_auth_oauthlib.flow import Flow

CLIENT_SECRET_FILE = "/data/workspace/afroviolin/artifacts/client_secret.json"
PENDING_VERIFIER_FILE = "/data/workspace/afroviolin/artifacts/pending_verifier.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:1"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    
    # Save code verifier and state
    verifier = getattr(flow, "code_verifier", None)
    state_data = {
        "code_verifier": verifier,
        "redirect_uri": "http://localhost:1"
    }
    
    with open(PENDING_VERIFIER_FILE, "w") as f:
        json.dump(state_data, f, indent=2)
        
    print("\n" + "="*80)
    print("NEW YOUTUBE AUTHORIZATION URL")
    print("="*80)
    print("Please visit this new URL to authorize:")
    print(f"\n{auth_url}\n")
    print("After approving, copy the redirect URL and paste it back to me!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
