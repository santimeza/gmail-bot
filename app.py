from flask import Flask, redirect, url_for, request, session, render_template, jsonify
import os
import json
import webbrowser
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from werkzeug.serving import is_running_from_reloader
from bot_logic import run_gmail_cleaner, get_or_create_valid_sender_label, get_labels

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

def get_credentials():
    """Get user credentials from token.json."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    if not creds or not creds.valid:
        # If no valid credentials, initiate OAuth flow
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:5000/callback"
        )
        auth_url, state = flow.authorization_url(prompt="consent")
        session["state"] = state
        
        return redirect(auth_url)
    return creds


@app.route("/")
def home():
    """Landing page for manual bot control."""
    return render_template("index.html")

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

    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    """Post-authentication page with bot functionality."""
    if not os.path.exists("token.json"):
        return redirect(url_for("home"))  # Redirect to pre-auth page if not authenticated
    
    return render_template("dashboard.html")

@app.route("/fetch-labels")
def fetch_labels():
    """Get list of user labels."""
    labels = get_labels()   #sends only the label names
    return jsonify(labels)

@app.route("/run-bot", methods=["POST"])
def run_bot():
    try:
        data = request.json  # Extract JSON data from request
        selected_labels = data.get("labels", [])  # Get selected labels

        # Call the Gmail cleaner function with selected labels
        result = run_gmail_cleaner(selected_labels)

        return jsonify({"message": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gmail-set-up")
def gmail_set_up():
    """Create the 'Valid Sender' label in Gmail."""
    result = get_or_create_valid_sender_label()
    return result

    


if __name__ == "__main__":
    if not is_running_from_reloader():
        webbrowser.open("http://localhost:5000")  # Open UI automatically
    app.run(port=5000, debug=True)
