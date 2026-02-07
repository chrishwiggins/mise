#!/usr/bin/env python3
"""
Google Sheets Permission Management Library
Provides methods to programmatically grant access to Google Sheets.

Uses google_auth.py for credential management.
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Shared auth module
sys.path.insert(0, str(Path(__file__).parent))
from google_auth import get_credentials as _get_credentials, extract_google_id

# Keep backward-compatible names
DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials(creds_path=None, scopes=DRIVE_SCOPES):
    """Backward-compatible wrapper around google_auth.get_credentials."""
    return _get_credentials(scopes="drive-and-sheets", creds_path=creds_path)


def extract_sheet_id(input_string):
    """Extract Google Sheet ID from URL or return as-is. Delegates to google_auth."""
    return extract_google_id(input_string)


# ============================================================================
# METHOD 1: GOOGLE DRIVE API (PRIMARY METHOD)
# ============================================================================


def grant_access_via_drive_api(
    sheet_input: str, email: str, role: str = "writer"
) -> Dict[str, Any]:
    """Use Google Drive API to directly add permissions."""
    sheet_id = extract_sheet_id(sheet_input)

    try:
        creds = get_credentials()
        drive_service = build("drive", "v3", credentials=creds)

        permission = {
            "type": "user",
            "role": role,
            "emailAddress": email,
        }

        result = (
            drive_service.permissions()
            .create(
                fileId=sheet_id,
                body=permission,
                sendNotificationEmail=True,
                emailMessage=f"You have been granted {role} access to this Google Sheet",
            )
            .execute()
        )

        return {
            "success": True,
            "method": "drive_api",
            "permission_id": result.get("id"),
            "message": f"Successfully granted {role} access to {email}",
        }

    except HttpError as e:
        error_details = json.loads(e.content.decode())
        return {
            "success": False,
            "method": "drive_api",
            "error": error_details.get("error", {}).get("message", str(e)),
            "code": e.resp.status,
            "message": f'Drive API failed: {error_details.get("error", {}).get("message", str(e))}',
        }
    except Exception as e:
        return {
            "success": False,
            "method": "drive_api",
            "error": str(e),
            "message": f"Drive API failed with unexpected error: {str(e)}",
        }


# ============================================================================
# METHOD 2: SHEETS API + DRIVE API COMBO (VERIFICATION FIRST)
# ============================================================================


def grant_access_via_sheets_drive_combo(
    sheet_input: str, email: str, role: str = "writer"
) -> Dict[str, Any]:
    """Verify sheet access via Sheets API, then use Drive API for permissions."""
    sheet_id = extract_sheet_id(sheet_input)

    try:
        creds = get_credentials()

        sheets_service = build("sheets", "v4", credentials=creds)
        sheet_metadata = (
            sheets_service.spreadsheets()
            .get(spreadsheetId=sheet_id, fields="properties.title")
            .execute()
        )

        sheet_title = sheet_metadata.get("properties", {}).get("title", "Unknown")

        drive_service = build("drive", "v3", credentials=creds)
        permission = {"type": "user", "role": role, "emailAddress": email}

        result = (
            drive_service.permissions()
            .create(
                fileId=sheet_id,
                body=permission,
                sendNotificationEmail=True,
                emailMessage=f'You have been granted {role} access to "{sheet_title}"',
            )
            .execute()
        )

        return {
            "success": True,
            "method": "sheets_drive_combo",
            "permission_id": result.get("id"),
            "sheet_title": sheet_title,
            "message": f'Successfully granted {role} access to {email} for sheet "{sheet_title}"',
        }

    except HttpError as e:
        error_details = json.loads(e.content.decode())
        return {
            "success": False,
            "method": "sheets_drive_combo",
            "error": error_details.get("error", {}).get("message", str(e)),
            "code": e.resp.status,
            "message": f'Sheets+Drive API failed: {error_details.get("error", {}).get("message", str(e))}',
        }
    except Exception as e:
        return {
            "success": False,
            "method": "sheets_drive_combo",
            "error": str(e),
            "message": f"Sheets+Drive API failed with unexpected error: {str(e)}",
        }


# ============================================================================
# MAIN PERMISSION GRANTING FUNCTION
# ============================================================================


def grant_sheet_access(
    sheet_input: str, email: str, role: str = "writer", creds_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Try methods in order until one succeeds.

    Args:
        sheet_input: Google Sheet URL or ID
        email: Email address to grant access to
        role: Permission role ('writer', 'reader', 'owner')
        creds_path: Optional path to credentials file

    Returns:
        Dict with success status, method used, and details
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        return {
            "success": False,
            "error": "Invalid email format",
            "message": f'Email "{email}" is not valid',
        }

    valid_roles = ["reader", "writer", "owner"]
    if role not in valid_roles:
        return {
            "success": False,
            "error": "Invalid role",
            "message": f'Role must be one of: {", ".join(valid_roles)}',
        }

    methods = [
        ("Drive API", grant_access_via_drive_api),
        ("Sheets+Drive API combo", grant_access_via_sheets_drive_combo),
    ]

    results = []

    for method_name, method_func in methods:
        print(f"Trying {method_name}...", file=sys.stderr)

        result = method_func(sheet_input, email, role)
        results.append(result)

        if result["success"]:
            return result

    return {
        "success": False,
        "error": "All methods failed",
        "message": "Could not grant access using any available method",
        "attempts": results,
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gsheet_permissions.py SHEET_ID EMAIL [ROLE]")
        sys.exit(1)

    sheet = sys.argv[1]
    email = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "writer"

    result = grant_sheet_access(sheet, email, role)

    if not result["success"]:
        print(f"\nFailed to grant access: {result['message']}")
        sys.exit(1)
    else:
        print(f"\nSuccess!")
