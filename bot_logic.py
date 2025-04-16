import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import redirect, url_for
from datetime import datetime, timedelta, timezone
import re


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
creds = Credentials.from_authorized_user_file("token.json", SCOPES)
LOG_FILE_PATH = "gmail_cleaner_log.txt"

CLIENT_SECRETS_FILE = "credentials.json"

def run_gmail_cleaner(labels, before_date):
    """Runs the Gmail cleaner bot after authentication."""
    if not os.path.exists("token.json"):
        return redirect(url_for("auth"))
    
    if not labels:
        return "<h1>❌ Please select labels and/or categories for the cleaner.</h1>"

    service = build('gmail', 'v1', credentials=creds)
    ia_list = get_important_addresses(service=service, user_id='me', label_name="Important address")
    deleted_emails = {}
    skipped_emails = {}

    for label in labels:
        query = f'label:{label} before:{before_date} -is:important'
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        deleted_emails[label] = []
        skipped_emails[label] = []

        if not messages:
            continue

        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")

            if sender:
                match = re.search(r'<(.+?)>', sender)
                sender_email = match.group(1) if match else sender

                if sender_email in ia_list:
                    skipped_emails[label].append(f"From: {sender_email}, Subject: {subject}")
                    continue

            deleted_emails[label].append(f"From: {sender_email}, Subject: {subject}")
            # Uncomment the next line to actually delete the email
            # service.users().messages().trash(userId='me', id=msg['id']).execute()

    append_to_log_file(labels, before_date, deleted_emails, skipped_emails)
    return "<h1>✅ Emails processed!</h1><br/><h1>--------------------------------------------------</h1><br/>"

def create_important_address_label(service=build('gmail', 'v1', credentials=creds), user_id='me', label_name="Important address"):
    labels = service.users().labels().list(userId=user_id).execute()
    for label in labels['labels']:
        if label['name'].lower() == label_name.lower():
            return f"Important address label already exists. Label ID: {label['id']}"

    # Create label if it doesn’t exist
    label_body = {'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    label = service.users().labels().create(userId=user_id, body=label_body).execute()
    return "Important address label created successfully!"

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
    

# load list of Important addresses from corresponding label in Gmail
def get_important_addresses(service=build('gmail', 'v1', credentials=creds), user_id='me', label_name="Important address"):
    try:
        # Get the label ID for the "Important address" label
        labels = service.users().labels().list(userId=user_id).execute()
        label_id = None
        for label in labels['labels']:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break

        if not label_id:
            print(f"Label '{label_name}' not found.")
            return []

        # Fetch messages from the "Important address" label
        results = service.users().messages().list(userId=user_id, labelIds=[label_id]).execute()
        messages = results.get('messages', [])

        if not messages:
            print(f"No emails found in label: {label_name}")
            return []

        addresses = []
        for msg in messages:
            msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'] == 'From':
                    # Extract the email address using a regular expression
                    match = re.search(r'<(.+?)>', header['value'])
                    if match:
                        addresses.append(match.group(1))  # Extract the email address inside <>
                    else:
                        addresses.append(header['value'])  # Fallback to the full "From" value if no match
        return addresses

    except Exception as e:
        print(f"Error fetching important addresses: {e}")
        return []
    
def append_to_log_file(labels, before_date, deleted_emails, skipped_emails):
    """Appends log details to the log file."""
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    with open(LOG_FILE_PATH, "a", encoding='utf-8') as log_file:
        log_file.write(f"Date run: {current_date}\n")  # Add current date
        log_file.write("--------------------------------------------------\n")
        log_file.write(f"Labels selected:    {labels}\n")
        log_file.write(f"Before Date:         {before_date}\n\n")

        for label, details in deleted_emails.items():
            log_file.write(f"--- {label} emails deleted\n")
            for email in details:
                log_file.write(f"{email}\n")
            log_file.write("\n")

        for label, details in skipped_emails.items():
            log_file.write(f"--- {label} emails skipped\n")
            for email in details:
                log_file.write(f"{email}\n")
            log_file.write("\n")

        log_file.write("--------------------------------------------------\n\n")