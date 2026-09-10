#!/usr/bin/env python3
import os
import sys
import json
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow

CLIENT_SECRET_FILE = "/data/workspace/afroviolin/artifacts/client_secret.json"
PENDING_VERIFIER_FILE = "/data/workspace/afroviolin/artifacts/pending_verifier.json"
TOKEN_FILE = "/data/workspace/afroviolin/artifacts/youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    if len(sys.argv) < 2:
        print("Usage: exchange_youtube_code_v3.py <auth_code_or_redirect_url>")
        return

    input_val = sys.argv[1]
    
    # Extract code from URL if a URL is provided
    if "code=" in input_val:
        parsed = urlparse(input_val)
        queries = parse_qs(parsed.query)
        if "code" in queries:
            auth_code = queries["code"][0]
        else:
            print("Error: Could not parse 'code' from URL")
            return
    else:
        auth_code = input_val

    if not os.path.exists(PENDING_VERIFIER_FILE):
        print(f"Error: Pending verifier state not found at {PENDING_VERIFIER_FILE}")
        return

    with open(PENDING_VERIFIER_FILE) as f:
        state_data = json.load(f)

    code_verifier = state_data.get("code_verifier")
    redirect_uri = state_data.get("redirect_uri", "http://localhost:1")

    print(f"Exchanging code: {auth_code[:10]}...")
    print(f"Using redirect_uri: {redirect_uri}")
    print(f"Using code_verifier: {code_verifier[:10]}...")

    # Initialize Flow
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    # Set the verifier that matches the challenge used to generate the auth_url
    flow.code_verifier = code_verifier

    try:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Save credentials
        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
            
        print(f"\n✅ SUCCESS! Credentials saved to {TOKEN_FILE}")
        
    except Exception as e:
        print(f"\n❌ Error during exchange: {e}")

if __name__ == "__main__":
    main()
