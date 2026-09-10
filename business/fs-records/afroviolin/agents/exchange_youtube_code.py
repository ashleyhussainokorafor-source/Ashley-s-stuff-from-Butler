#!/usr/bin/env python3
import os
import json
from google_auth_oauthlib.flow import Flow

CLIENT_SECRET_FILE = "/data/workspace/afroviolin/artifacts/client_secret.json"
TOKEN_FILE = "/data/workspace/afroviolin/artifacts/youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]

def main():
    # The authorization code from the user
    auth_code = "4/0AdkVLPwXtdN1l71861L8mIwZMZb3_vGki7QcPB3KvnAWHrLhjEadvmUkc61QqC5djI7b9Q"
    
    # We must use http://localhost:1 because that's what was used in the markdown link
    redirect_uri = "http://localhost:1"
    
    print(f"Exchanging code using redirect_uri: {redirect_uri}")
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    
    try:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Save credentials as JSON
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
