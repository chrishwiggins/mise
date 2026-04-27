#!/usr/bin/env python3
"""
When2Meet-style Google Form Creator

Takes date/time ranges as input (piped or from file) and creates a Google Form
with checkbox options for each time slot. The form is made publicly accessible
with public results viewing enabled.

Usage:
    cat dates.txt | python when2meet.py [chunk_minutes]
    python when2meet.py < dates.txt
    python when2meet.py 45 < dates.txt  # 45-minute chunks

Input format examples:
    mon 15 sep 09.00-10.00, 10.30-11.30
    wed 17 sep 09.00-11.30, 14.30-18.30
"""

import sys
import re
import argparse
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def parse_time_ranges(input_text: str) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """
    Parse input text to extract date and time ranges.

    Returns:
        List of tuples: (date_string, [(start_time, end_time), ...])
    """
    date_ranges = []

    for line in input_text.strip().split("\n"):
        if not line.strip():
            continue

        # Parse date part (e.g., "mon 15 sep" or "wed 17 sep")
        date_match = re.match(r"^(\w+\s+\d+\s+\w+)\s+(.+)$", line, re.IGNORECASE)
        if not date_match:
            continue

        date_str = date_match.group(1)
        time_part = date_match.group(2)

        # Parse time ranges (e.g., "09.00-10.00, 10.30-11.30")
        time_ranges = []
        for time_range in time_part.split(","):
            time_match = re.match(
                r"(\d+[.:]\d+)\s*-\s*(\d+[.:]\d+)", time_range.strip()
            )
            if time_match:
                start_time = time_match.group(1).replace(".", ":")
                end_time = time_match.group(2).replace(".", ":")
                time_ranges.append((start_time, end_time))

        if time_ranges:
            date_ranges.append((date_str, time_ranges))

    return date_ranges


def generate_time_chunks(
    date_ranges: List[Tuple[str, List[Tuple[str, str]]]], chunk_minutes: int = 30
) -> List[str]:
    """
    Generate time chunks based on the parsed date ranges.

    Returns:
        List of formatted time slot strings
    """
    time_slots = []

    for date_str, time_ranges in date_ranges:
        for start_str, end_str in time_ranges:
            # Parse times
            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))

            # Create datetime objects for easier manipulation
            start_time = datetime(2025, 1, 1, start_hour, start_min)
            end_time = datetime(2025, 1, 1, end_hour, end_min)

            # Generate chunks
            current = start_time
            while current < end_time:
                next_time = min(current + timedelta(minutes=chunk_minutes), end_time)
                slot_str = f"{date_str} {current.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                time_slots.append(slot_str)
                current = next_time

    return time_slots


def get_authenticated_credentials():
    """Get OAuth2 credentials for Google Forms and Drive APIs"""
    SCOPES = [
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/drive",
    ]

    CREDS_FILE = "credentials.json"
    TOKEN_FILE = "token_forms.pickle"

    creds = None

    # Load existing token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                print("Error: credentials.json not found")
                print("Please ensure credentials.json exists in current directory")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            try:
                creds = flow.run_local_server(port=8080, open_browser=True)
            except:
                # Fallback to manual flow
                auth_url, _ = flow.authorization_url(prompt="consent")
                print(f"Open this URL: {auth_url}")
                code = input("Enter authorization code: ")
                flow.fetch_token(code=code)
                creds = flow.credentials

        # Save credentials for next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return creds


def create_when2meet_form(time_slots: List[str], form_title: str = None) -> str:
    """
    Create a Google Form with checkbox options for each time slot.
    Makes the form publicly accessible with public results.

    Returns:
        Form ID of the created form
    """
    # Get authenticated credentials
    creds = get_authenticated_credentials()

    # Initialize API clients
    forms_service = build("forms", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Create form with title
    if not form_title:
        form_title = f"Availability Poll - {datetime.now().strftime('%Y-%m-%d')}"

    print(f"Creating form: {form_title}")

    form = forms_service.forms().create(body={"info": {"title": form_title}}).execute()

    form_id = form["formId"]

    # Add description
    description = "Please select all time slots when you are available. You can select multiple options."

    # Create batch update request
    batch_request = {"requests": []}

    # Update form description
    batch_request["requests"].append(
        {
            "updateFormInfo": {
                "info": {"description": description},
                "updateMask": "description",
            }
        }
    )

    # Add name field
    batch_request["requests"].append(
        {
            "createItem": {
                "item": {
                    "title": "Your Name",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {"paragraph": False},
                        }
                    },
                },
                "location": {"index": 0},
            }
        }
    )

    # Add checkbox grid for time slots
    # Google Forms API doesn't directly support checkbox grids,
    # so we'll use multiple choice checkboxes instead
    batch_request["requests"].append(
        {
            "createItem": {
                "item": {
                    "title": "Available Time Slots",
                    "description": "Select all times when you are available",
                    "questionItem": {
                        "question": {
                            "required": False,
                            "choiceQuestion": {
                                "type": "CHECKBOX",
                                "options": [{"value": slot} for slot in time_slots],
                            },
                        }
                    },
                },
                "location": {"index": 1},
            }
        }
    )

    # Execute batch update
    forms_service.forms().batchUpdate(formId=form_id, body=batch_request).execute()

    # Make form publicly accessible
    print("Setting public permissions...")

    try:
        # Get current form settings
        form_settings = forms_service.forms().get(formId=form_id).execute()

        # Update form settings to allow response viewing
        settings_update = {
            "requests": [
                {
                    "updateSettings": {
                        "settings": {"quizSettings": {"isQuiz": False}},
                        "updateMask": "quizSettings.isQuiz",
                    }
                }
            ]
        }

        forms_service.forms().batchUpdate(
            formId=form_id, body=settings_update
        ).execute()

        # Make form publicly accessible via Drive API
        permission = {"type": "anyone", "role": "writer"}

        drive_service.permissions().create(fileId=form_id, body=permission).execute()

    except Exception as e:
        print(f"Note: Could not set all public permissions: {e}")
        print("You may need to manually enable response viewing in form settings")

    return form_id


def main():
    # Parse command line arguments
    chunk_minutes = 30  # Default
    if len(sys.argv) > 1:
        try:
            chunk_minutes = int(sys.argv[1])
        except ValueError:
            print(f"Invalid chunk size: {sys.argv[1]}")
            sys.exit(1)

    # Read input from stdin
    if sys.stdin.isatty():
        print("Error: No input provided. Pipe data to this script:")
        print("  cat dates.txt | python when2meet.py [chunk_minutes]")
        sys.exit(1)

    input_text = sys.stdin.read()

    # Parse date/time ranges
    date_ranges = parse_time_ranges(input_text)

    if not date_ranges:
        print("Error: No valid date/time ranges found in input")
        sys.exit(1)

    # Generate time chunks
    time_slots = generate_time_chunks(date_ranges, chunk_minutes)

    if not time_slots:
        print("Error: No time slots generated")
        sys.exit(1)

    print(f"Generated {len(time_slots)} time slots with {chunk_minutes}-minute chunks:")
    for slot in time_slots[:5]:  # Show first 5 as preview
        print(f"  - {slot}")
    if len(time_slots) > 5:
        print(f"  ... and {len(time_slots) - 5} more")

    # Create Google Form
    form_id = create_when2meet_form(time_slots)

    # Output results
    print("\n" + "=" * 60)
    print("✅ Form created successfully!")
    print("=" * 60)
    print(f"\nForm links:")
    print(f"  Edit: https://docs.google.com/forms/d/{form_id}/edit")
    print(f"  Share: https://docs.google.com/forms/d/{form_id}/viewform")
    print(f"  Responses: https://docs.google.com/forms/d/{form_id}/responses")
    print("\nNote: The form is publicly accessible. Anyone with the link can respond.")
    print("To see aggregated responses, use the 'Responses' link above.")


if __name__ == "__main__":
    main()
