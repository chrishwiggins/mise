#!/usr/bin/env python3
"""
Trash old Google Forms listed in a .form-history file, keeping the latest.

Usage: python3 gform-clean.py <.form-history>
"""

import sys
from pathlib import Path

from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).parent))
from google_auth import get_credentials


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gform-clean.py <.form-history>")
        sys.exit(1)

    history_path = Path(sys.argv[1])
    if not history_path.exists():
        print("No history file found, nothing to clean.")
        return

    form_ids = [line.strip() for line in history_path.read_text().splitlines() if line.strip()]

    if len(form_ids) <= 1:
        print("Only one form (or none) in history, nothing to clean.")
        return

    keep = form_ids[-1]
    trash = form_ids[:-1]

    creds = get_credentials(service="drive", scopes="drive-full")
    drive = build("drive", "v3", credentials=creds)

    for fid in trash:
        try:
            drive.files().delete(fileId=fid).execute()
            print(f"Deleted: {fid}")
        except Exception as e:
            print(f"Failed to delete {fid}: {e}", file=sys.stderr)

    # Rewrite history with only the keeper
    history_path.write_text(f"{keep}\n")
    print(f"Kept:    {keep}")


if __name__ == "__main__":
    main()
