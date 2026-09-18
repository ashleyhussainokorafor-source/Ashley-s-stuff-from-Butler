import json
import re
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('/data/google_token.json') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri=token_data.get('token_uri'),
    client_id=token_data.get('client_id'),
    client_secret='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'
)

service = build('gmail', 'v1', credentials=creds)

results = service.users().messages().list(userId='me', q='invitation', maxResults=5).execute()
messages = results.get('messages', [])
print(f"Found {len(messages)} messages matching 'invitation'")

for m in messages:
    msg_data = service.users().messages().get(userId='me', id=m['id'], format='full').execute()
    headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
    print("Subject:", headers.get('Subject'))
    print("From:", headers.get('From'))
    print("Snippet:", msg_data.get('snippet'))
    
    # Extract body
    html_content = ""
    if 'parts' in msg_data['payload']:
        for p in msg_data['payload']['parts']:
            if p.get('mimeType') == 'text/html' and 'data' in p.get('body', {}):
                html_content = base64.urlsafe_b64decode(p['body']['data']).decode('utf-8', errors='ignore')
    elif 'body' in msg_data['payload'] and 'data' in msg_data['payload']['body']:
        html_content = base64.urlsafe_b64decode(msg_data['payload']['body']['data']).decode('utf-8', errors='ignore')
        
    links = re.findall(r'https://studio\.youtube\.com/[^\s"\'<>]+', html_content)
    if links:
        print("Accept URL:", links[0])
    print("-" * 40)
