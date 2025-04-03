import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import redirect, url_for
from datetime import datetime, timedelta, timezone
import re


SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
creds = Credentials.from_authorized_user_file("token.json", SCOPES)

CLIENT_SECRETS_FILE = "credentials.json"



def run_gmail_cleaner(labels):
    """Runs the Gmail cleaner bot after authentication."""
    if not os.path.exists("token.json"):
        return redirect(url_for("auth"))

    #creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    # make important address list
    ia_list = get_important_addresses(service=service, user_id='me', label_name="Important address")
    print("Important address list created.")
    for address in ia_list:
        print(address)

    # Example: Delete emails older than 7 days from Promotions tab
    days_old = 7
    date_limit = (datetime.now(timezone.utc) - timedelta(days=days_old)).strftime('%Y/%m/%d')
    no_messages = 0

    for label in labels:
        query = f'label:{label} before:{date_limit}'

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        if not messages:
            print("No emails found in: ", label)
            no_messages += 1
            continue

        print(f"{len(messages)} emails detected in {label}.")
        print(f"Date limit {date_limit}")
        for msg in messages:
            #service.users().messages().trash(userId='me', id=msg['id']).execute()
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "No Subject")
            print(f"email with Subject: {subject}")
    
    print(labels)
    if no_messages == len(labels):
        return "<h1>❌ No emails found!</h1><h1> ---------------------------------- </h1>"
    return "<h1>✅ Emails detected!</h1><h1> ---------------------------------- </h1>"
        
        
    #print("{{len(messages)}} emails deleted.")

    #return "<h1>✅ Emails deleted successfully!</h1>"

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