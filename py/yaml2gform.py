#!/usr/bin/env python3
"""
Create a Google Form from a YAML definition file.

Reads a YAML file with form title, description, settings, and questions,
then creates a Google Form via the Forms API.

Supports: text, paragraph, multiple_choice, checkbox, dropdown, date.

YAML format:
    title: "Form Title"
    description: "Form description"
    settings:
        require_login: true
        collect_email: true
        send_receipt: true
        allow_edit: true
    questions:
        - id: q1
          type: multiple_choice
          title: "Question text"
          description: "Help text shown below the question"
          required: true
          choices: ["Option A", "Option B"]

Usage: python3 yaml2gform.py <form.yaml>

Requires:
    pip install pyyaml google-api-python-client google-auth-oauthlib

Uses google_auth.py for credential management (forms scope).
"""

import sys
import yaml
from pathlib import Path

from googleapiclient.discovery import build

# Shared auth module
sys.path.insert(0, str(Path(__file__).parent))
from google_auth import get_credentials


# ---------------------------------------------------------------------------
# YAML -> Forms API request translation
# ---------------------------------------------------------------------------

QUESTION_TYPE_MAP = {
    "text": "TEXT",
    "paragraph": "PARAGRAPH",
    "multiple_choice": "RADIO",
    "checkbox": "CHECKBOX",
    "dropdown": "DROP_DOWN",
    "date": "DATE",
}


def build_question_item(q):
    """Convert a YAML question dict to a Forms API createItem request body."""
    qtype = q.get("type", "text")
    api_type = QUESTION_TYPE_MAP.get(qtype)
    if not api_type:
        print(f"Warning: unknown question type '{qtype}', defaulting to TEXT", file=sys.stderr)
        api_type = "TEXT"

    # Forms API doesn't allow newlines in displayed text
    title = " ".join(q["title"].split())
    item = {
        "title": title,
        "questionItem": {
            "question": {
                "required": q.get("required", False),
            }
        },
    }

    # Per-question help text
    desc = " ".join(q.get("description", "").split())
    if desc:
        item["description"] = desc

    if api_type == "DATE":
        item["questionItem"]["question"]["dateQuestion"] = {
            "includeTime": False,
            "includeYear": True,
        }
    elif api_type in ("RADIO", "CHECKBOX", "DROP_DOWN"):
        choices = q.get("choices", [])
        item["questionItem"]["question"]["choiceQuestion"] = {
            "type": api_type,
            "options": [{"value": c} for c in choices],
        }
    else:
        item["questionItem"]["question"]["textQuestion"] = {
            "paragraph": api_type == "PARAGRAPH",
        }

    return item


def build_requests(form_def):
    """Build the list of batchUpdate requests from parsed YAML."""
    requests = []

    # Form description
    desc = form_def.get("description", "").strip()
    if desc:
        requests.append({
            "updateFormInfo": {
                "info": {"description": desc},
                "updateMask": "description",
            }
        })

    # Form settings (API only supports emailCollectionType)
    settings = form_def.get("settings", {})

    if settings.get("require_login") or settings.get("collect_email"):
        requests.append({
            "updateSettings": {
                "settings": {"emailCollectionType": "VERIFIED"},
                "updateMask": "emailCollectionType",
            }
        })

    # These must be set manually in Forms UI (not in the API):
    ui_settings = []
    if settings.get("send_receipt"):
        ui_settings.append("send receipt email")
    if settings.get("allow_edit"):
        ui_settings.append("allow response editing")
    if ui_settings:
        print(f"NOTE: Set manually in Forms Settings: {', '.join(ui_settings)}", file=sys.stderr)

    # Questions (flat list, no page breaks)
    questions = form_def.get("questions", [])

    # Also support legacy sections format
    if not questions:
        for section in form_def.get("sections", []):
            questions.extend(section.get("questions", []))

    for idx, q in enumerate(questions):
        item = build_question_item(q)
        requests.append({
            "createItem": {
                "item": item,
                "location": {"index": idx},
            }
        })

    return requests


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 yaml2gform.py <form.yaml>")
        sys.exit(1)

    yaml_path = Path(sys.argv[1])
    if not yaml_path.exists():
        print(f"File not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    with open(yaml_path) as f:
        form_def = yaml.safe_load(f)

    # Authenticate
    creds = get_credentials(service="forms", scopes="forms")

    # Create empty form
    service = build("forms", "v1", credentials=creds)
    form_body = {
        "info": {
            "title": form_def.get("title", "Untitled Form"),
        }
    }
    form = service.forms().create(body=form_body).execute()
    form_id = form["formId"]
    print(f"Created form: {form['responderUri']}")

    # Set description, settings, and add all items via batchUpdate
    requests = build_requests(form_def)

    if requests:
        service.forms().batchUpdate(
            formId=form_id,
            body={"requests": requests},
        ).execute()

    # Write URLs to companion file next to the YAML
    url_file = yaml_path.with_suffix(".url")
    url_file.write_text(
        f"fill: {form['responderUri']}\n"
        f"edit: https://docs.google.com/forms/d/{form_id}/edit\n"
    )

    # Append to history for cleanup
    history_file = yaml_path.parent / ".form-history"
    with open(history_file, "a") as f:
        f.write(f"{form_id}\n")

    print(f"Form ID: {form_id}")
    print(f"Edit:    https://docs.google.com/forms/d/{form_id}/edit")
    print(f"Fill:    {form['responderUri']}")
    print(f"URLs:    {url_file}")


if __name__ == "__main__":
    main()
