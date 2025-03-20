from flask import Flask, redirect, url_for, request, session
import os
import json
import webbrowser
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from bot_logic import run_gmail_cleaner

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
    result = run_gmail_cleaner()
    return f"<h1>Bot Execution:</h1><p>{result}</p>"


if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")  # Open UI automatically
    app.run(port=5000, debug=True)
