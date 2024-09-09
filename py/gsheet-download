#!/usr/bin/python3

import pickle  # For saving and loading credentials
import os  # For checking file existence
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
)  # For handling OAuth 2.0 authorization
from googleapiclient.discovery import build  # To interact with Google APIs
from google.auth.transport.requests import Request  # For refreshing credentials
import sys  # For handling system exit
import argparse  # For parsing command-line arguments
import platform  # For detecting the OS
import webbrowser  # For opening URLs in the browser

# Step 1: Setup argument parser for command-line flags
parser = argparse.ArgumentParser(
    description="Download Google Sheet data and save as TSV."
)
parser.add_argument("-i", "--id", required=True, help="Google Spreadsheet ID")
parser.add_argument("-f", "--file", required=True, help="Path to credentials.json file")

# Parse the arguments
args = parser.parse_args()

spreadsheet_id = args.id  # Spreadsheet ID provided by the user
credentials_file = args.file  # Path to credentials.json file

# Step 2: Define the URL for downloading credentials.json if not found
google_credentials_url = "https://console.cloud.google.com/apis/credentials"

# Step 3: Check if the provided credentials file exists, open the URL if not
if not os.path.exists(credentials_file):
    print(
        f"Error: '{credentials_file}' not found. Please download it from {google_credentials_url} and place it in the specified location."
    )

    # Echo the URL for manual access
    print(
        f"Visit the following URL to download the credentials.json file: {google_credentials_url}"
    )

    # Automatically open the URL if running on macOS
    if platform.system() == "Darwin":
        print("Opening the URL on macOS...")
        webbrowser.open(google_credentials_url)  # Automatically open the URL
    else:
        print("Please manually open the URL in your browser.")

    sys.exit(1)  # Exit the script if credentials.json is not found

# Step 4: Load credentials or initiate a new login if credentials don't exist or are invalid
creds = None  # Initialize credentials variable

# Check if the token.pickle file exists, which stores the user's credentials after the initial login
if os.path.exists("token.pickle"):
    # If the token file exists, load the credentials from it
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)  # Load credentials from the token file

# If no valid credentials are available (either missing or expired), handle authentication
if not creds or not creds.valid:
    # If the credentials are expired but a refresh token is available, refresh them
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())  # Refresh the credentials using the refresh token
    else:
        # Initiate a new login flow using the OAuth 2.0 client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file,  # File with OAuth 2.0 client information (downloadable from Google Cloud Console)
            [
                "https://www.googleapis.com/auth/spreadsheets.readonly"
            ],  # Specify the scope: read-only access to Google Sheets
        )
        creds = flow.run_local_server(
            port=0
        )  # Launch a local server to handle the OAuth redirect and login

        # After the login, save the credentials for future use by pickling them into token.pickle
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)  # Store credentials for reuse

# Step 5: Create a service object to interact with the Google Sheets API
service = build(
    "sheets", "v4", credentials=creds
)  # Build a service for Google Sheets API, version 4

# Step 6: Define the range of data to pull from the Google Sheet
range_name = "Form Responses 1"  # The name of the sheet and the range to retrieve data from (update if different)

# Step 7: Make an API request to get the data from the specified range of the Google Sheet
result = (
    service.spreadsheets()
    .values()
    .get(spreadsheetId=spreadsheet_id, range=range_name)
    .execute()
)

# Step 8: Extract the values from the result
values = result.get("values", [])

# Step 9: Save the retrieved data to a TSV (tab-separated values) file
with open("output.tsv", "w") as f:
    for row in values:
        f.write("\t".join(row) + "\n")

print("Sheet downloaded as output.tsv")
