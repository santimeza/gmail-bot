import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import redirect, url_for

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
creds = Credentials.from_authorized_user_file("token.json", SCOPES)

CLIENT_SECRETS_FILE = "credentials.json"


def run_gmail_cleaner():
    """Runs the Gmail cleaner bot after authentication."""
    if not os.path.exists("token.json"):
        return redirect(url_for("auth"))

    #creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # Example: Delete emails older than 7 days from Promotions tab
    days_old = 7

    from datetime import datetime, timedelta, timezone
    date_limit = (datetime.now(timezone.utc) - timedelta(days=days_old)).strftime('%Y/%m/%d')
    query = f'label:personal before:{date_limit}'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No emails found.")
        return "<h1>No emails found.</h1>"

    print(f"{len(messages)} emails detected.")
    print(f"Date limit {date_limit}")
    for msg in messages:
        #service.users().messages().trash(userId='me', id=msg['id']).execute()
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
        print(f"email with Subject: {subject}")
        
    return "<h1>✅ Emails detected!</h1>"
        
        
    #print("{{len(messages)}} emails deleted.")

    #return "<h1>✅ Emails deleted successfully!</h1>"

def get_or_create_valid_sender_label(service=build('gmail', 'v1', credentials=creds), user_id='me', label_name="Valid Sender"):
    labels = service.users().labels().list(userId=user_id).execute()
    for label in labels['labels']:
        if label['name'].lower() == label_name.lower():
            return f"Valid Sender label already exists. Label ID: {label['id']}"

    # Create label if it doesn’t exist
    label_body = {'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    label = service.users().labels().create(userId=user_id, body=label_body).execute()
    return "Valid Sender label created successfully!"

# Gets list of user labels. For use in the dashboard-- bot setup
def get_labels(service=build('gmail', 'v1', credentials=creds), user_id='me'):
    try:
        results = service.users().labels().list(userId=user_id).execute()
        labels = results.get("labels", [])

        # Extract only the names and clean up CATEGORY_ prefixes
        label_names = [
            label["name"].replace("CATEGORY_", "")  # Remove "CATEGORY_" prefix
            for label in labels
            if label["name"].lower() != "trash"  # Skip "Trash" label
        ]

        print('Processed labels:', label_names)  # Debugging
        return label_names  # Return only the cleaned label names

    except Exception as e:
        print(f"Error fetching labels: {e}")
        return []
