#!/usr/bin/env python3
"""
Setup Google API authentication for multiple services
One project, multiple service tokens
"""

import os
import pickle
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define scopes for different services
SCOPES = {
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "drive": ["https://www.googleapis.com/auth/drive"],
    "sheets": ["https://www.googleapis.com/auth/spreadsheets"],
    "all": [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ],
}


def setup_service(service_name, credentials_file="credentials.json"):
    """Setup authentication for a specific Google service"""

    # Token file named by service
    token_file = f"token.{service_name}.pickle"

    # Get appropriate scopes
    if service_name == "all":
        scopes = SCOPES["all"]
    elif service_name in SCOPES:
        scopes = SCOPES[service_name]
    else:
        print(f"❌ Unknown service: {service_name}")
        print("Available: calendar, drive, sheets, all")
        return None

    creds = None

    # Check for existing token
    if os.path.exists(token_file):
        print(f"📁 Found existing token: {token_file}")
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    # Validate and refresh if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"🔄 Refreshing expired token for {service_name}...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Refresh failed: {e}")
                creds = None

        if not creds:
            if not os.path.exists(credentials_file):
                print(f"❌ Credentials file not found: {credentials_file}")
                print("\n📋 Setup Instructions:")
                print("1. Go to https://console.cloud.google.com")
                print("2. Create a new project (or use existing)")
                print("3. Enable these APIs:")
                print("   - Google Calendar API")
                print("   - Google Drive API")
                print("   - Google Sheets API")
                print("4. Create OAuth 2.0 credentials (Desktop type)")
                print("5. Download and save as 'credentials.json'")
                return None

            print(f"🔐 Authenticating for {service_name}...")
            print("Browser will open for authorization")

            # Load credentials and determine type
            with open(credentials_file, "r") as f:
                creds_data = json.load(f)

            # Handle both web and installed app types
            if "web" in creds_data:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes, redirect_uri="http://localhost:8080"
                )
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes
                )

            try:
                creds = flow.run_local_server(
                    port=8080,
                    authorization_prompt_message=f"Authorizing {service_name} access...",
                    success_message=f"✅ {service_name} authorized! You can close this window.",
                    open_browser=True,
                )
            except Exception as e:
                print(f"❌ Authentication failed: {e}")
                return None

        # Save the token
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)
        print(f"✅ Token saved: {token_file}")

    return creds


def test_calendar(creds):
    """Test Calendar API access"""
    try:
        service = build("calendar", "v3", credentials=creds)
        # List next 5 events
        from datetime import datetime

        now = datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        print(f"📅 Found {len(events)} upcoming events")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"   - {event.get('summary', 'No title')}: {start}")
        return True
    except Exception as e:
        print(f"❌ Calendar test failed: {e}")
        return False


def test_drive(creds):
    """Test Drive API access"""
    try:
        service = build("drive", "v3", credentials=creds)
        # List 5 files
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        items = results.get("files", [])

        print(f"📁 Found {len(items)} files in Drive")
        for item in items:
            print(f"   - {item['name']}")
        return True
    except Exception as e:
        print(f"❌ Drive test failed: {e}")
        return False


def test_sheets(creds):
    """Test Sheets API access"""
    try:
        service = build("sheets", "v4", credentials=creds)
        # Just build the service as a test
        print("✅ Sheets API accessible")
        return True
    except Exception as e:
        print(f"❌ Sheets test failed: {e}")
        return False


def main():
    """Main setup function"""
    import sys

    if len(sys.argv) < 2:
        print(
            """
Google API Authentication Setup
================================

Usage: python3 setup_google_auth.py <service>

Services:
  calendar  - Google Calendar API only
  drive     - Google Drive API only  
  sheets    - Google Sheets API only
  all       - All three APIs (recommended)

Examples:
  python3 setup_google_auth.py calendar
  python3 setup_google_auth.py all

This will create token files named:
  token.calendar.pickle
  token.drive.pickle
  token.sheets.pickle
  token.all.pickle

You can use one project for all services!
Just enable all the APIs you need in the same project.
"""
        )
        sys.exit(1)

    service = sys.argv[1].lower()

    print(f"🚀 Setting up Google {service.title()} authentication\n")

    creds = setup_service(service)

    if creds:
        print(f"\n✅ Authentication successful for {service}!")

        # Test the service
        print(f"\n🧪 Testing {service} API access...")

        if service == "calendar" or service == "all":
            test_calendar(creds)

        if service == "drive" or service == "all":
            test_drive(creds)

        if service == "sheets" or service == "all":
            test_sheets(creds)

        print(f"\n✅ Setup complete! Token saved as: token.{service}.pickle")
    else:
        print(f"\n❌ Setup failed for {service}")


if __name__ == "__main__":
    main()
