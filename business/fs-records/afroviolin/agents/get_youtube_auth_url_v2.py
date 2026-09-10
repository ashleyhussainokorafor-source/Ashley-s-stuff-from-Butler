#!/usr/bin/env python3
import os
import pickle
from google_auth_oauthlib.flow import Flow

CLIENT_SECRET_FILE = "/data/workspace/afroviolin/artifacts/client_secret.json"
PENDING_FLOW_FILE = "/data/workspace/afroviolin/artifacts/pending_flow.pkl"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    # Use localhost:1 as redirect URI to match the markdown link format
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:1"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    
    # Save the flow object (which contains the code_verifier) using pickle
    with open(PENDING_FLOW_FILE, "wb") as f:
        pickle.dump(flow, f)
        
    print("\n" + "="*80)
    print("NEW YOUTUBE AUTHORIZATION URL")
    print("="*80)
    print("Please visit this new URL to authorize:")
    print(f"\n{auth_url}\n")
    print("After approving, copy the redirect URL and paste it back to me!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
