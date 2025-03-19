from google.oauth2 import service_account
from googleapiclient.discovery import build
import os  # Added to handle token deletion
import base64
import email
from datetime import datetime, timedelta, timezone

# Load credentials.json (OAuth 2.0)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
creds = None

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
except Exception as e:
    print("Error authenticating:", e)

# Connect to Gmail API
service = build('gmail', 'v1', credentials=creds)

# Define criteria (delete emails older than 30 days in Promotions tab)
days_old = 7
date_limit = (datetime.now(timezone.utc) - timedelta(days=days_old)).strftime('%Y/%m/%d')
query = f'category:promotions before:{date_limit}'

# Fetch emails matching criteria
results = service.users().messages().list(userId='me', q=query).execute()
messages = results.get('messages', [])

#Delete emails
if not messages:
    print("No emails found.")
else:
    print(f"Found {len(messages)} emails. Deleting...")
    for msg in messages:
        service.users().messages().trash(userId='me', id=msg['id']).execute()
    print("Deletion complete.")
