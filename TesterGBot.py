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
    creds = flow.run_local_server(
        host="localhost",
        port=8080  # Change this if needed
    )
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




















# from flask import Flask, redirect, url_for
# import os
# import webbrowser
# import threading
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials

# app = Flask(__name__)

# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# # Ensure fresh authentication each run
# if os.path.exists('token.json'):
#     os.remove('token.json')

# def get_gmail_service():
#     """Handles authentication and returns an authenticated Gmail service object."""
#     creds = None

#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0, open_browser=False)  # Prevent Google's redirect

#         # Save credentials for future use
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     return build('gmail', 'v1', credentials=creds)

# @app.route("/")
# def index():
#     """Handles authentication and redirects user upon success."""
#     try:
#         get_gmail_service()
#         return redirect(url_for('auth_complete'))  # Redirect to custom success page
#     except Exception as e:
#         return f"<h1>❌ Error:</h1><p>{str(e)}</p>", 500

# @app.route("/auth-complete")
# def auth_complete():
#     """Post-authentication success message."""
#     return "<h1>✅ Authentication Successful!</h1><p>You can now close this window.</p>"

# if __name__ == "__main__":
#     # Open Google OAuth page manually
#     def start_auth():
#         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0, open_browser=True)  # Open Google Auth
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#         webbrowser.open("http://localhost:8080")  # Redirect to our Flask app

#     #threading.Thread(target=start_auth).start()  # Run authentication in separate thread
#     app.run(port=8080, debug=True)