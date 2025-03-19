from flask import Flask, redirect, url_for, request, session
import os
import json
import webbrowser
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# ✅ Allow HTTP for OAuth during local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure random key

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CLIENT_SECRETS_FILE = "credentials.json"

# Ensure fresh authentication each run
# if os.path.exists('token.json'):
#     os.remove('token.json')

# OAuth flow setup
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri="http://localhost:5000/callback"
)

@app.route("/")
def home():
    """Landing page for manual bot control."""
    return "<h1>📬 Gmail Cleaner</h1><p>Click <a href='/auth'>here</a> to authenticate.</p>"

@app.route("/auth")
def auth():
    """Redirects users to Google's OAuth page."""
    auth_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Handles Google's OAuth callback and saves credentials."""
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Save credentials for future use
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

    return "<h1>✅ Authentication Successful!</h1><p>You can now close this window.</p><br><a href='/run-bot'>Run Bot</a>"

@app.route("/run-bot")
def run_bot():
    """Runs the Gmail cleaner bot after authentication."""
    if not os.path.exists("token.json"):
        return redirect(url_for("auth"))

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # Example: Delete emails older than 7 days from Promotions tab
    days_old = 7
    from datetime import datetime, timedelta, timezone
    date_limit = (datetime.now(timezone.utc) - timedelta(days=days_old)).strftime('%Y/%m/%d')
    query = f'category:promotions before:{date_limit}'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        return "<h1>No emails found.</h1>"

    for msg in messages:
        service.users().messages().trash(userId='me', id=msg['id']).execute()

    return "<h1>✅ Emails deleted successfully!</h1>"

if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")  # Open UI automatically
    app.run(port=5000, debug=True)
