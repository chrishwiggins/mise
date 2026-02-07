"""
Shared Google API authentication for ~/mise/py/ scripts.

Consolidates credential resolution, token caching, and scope management
into one module. See ~/.config/gdrive/GOTCHA.md for credential history.

Usage:
    from google_auth import get_credentials, extract_google_id, extract_gid

    creds = get_credentials(scopes="sheets-readonly")
    creds = get_credentials(service="calendar")
    creds = get_credentials(scopes=["https://www.googleapis.com/auth/drive"])
"""

import json
import os
import pickle
import re
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow


# ---------------------------------------------------------------------------
# Scope presets
# ---------------------------------------------------------------------------

SCOPE_PRESETS = {
    "sheets-readonly": ["https://www.googleapis.com/auth/spreadsheets.readonly"],
    "sheets-readwrite": ["https://www.googleapis.com/auth/spreadsheets"],
    "drive-file": ["https://www.googleapis.com/auth/drive.file"],
    "drive-full": ["https://www.googleapis.com/auth/drive"],
    "drive-readonly": ["https://www.googleapis.com/auth/drive.readonly"],
    "drive-and-sheets": [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
    ],
    "calendar": ["https://www.googleapis.com/auth/calendar"],
    "forms": ["https://www.googleapis.com/auth/forms.body"],
    "docs-readonly": ["https://www.googleapis.com/auth/documents.readonly"],
}

# ---------------------------------------------------------------------------
# Credential file locations by service
# ---------------------------------------------------------------------------

SERVICE_CREDENTIALS = {
    "drive": ["~/.config/gdrive/credentials.json"],
    "sheets": ["~/.config/gdrive/credentials.json"],
    "forms": ["~/.config/gdrive/credentials.json"],
    "calendar": ["~/.config/gcal/credentials.json"],
    "thoughtgun": ["~/.config/thoughtgun/credentials.json"],
}

# Default for services not explicitly listed
DEFAULT_CREDENTIALS = ["~/.config/gdrive/credentials.json"]

# ---------------------------------------------------------------------------
# Token storage
# ---------------------------------------------------------------------------

TOKEN_DIR = Path("~/.config/google-tokens").expanduser()


def _resolve_scopes(scopes):
    """Resolve scope preset name or list to actual scope URLs."""
    if scopes is None:
        return SCOPE_PRESETS["drive-and-sheets"]
    if isinstance(scopes, str):
        if scopes in SCOPE_PRESETS:
            return SCOPE_PRESETS[scopes]
        # Assume it's a raw scope URL
        return [scopes]
    return list(scopes)


def _scope_key(scopes):
    """Generate a short, stable key from scope URLs for token filename."""
    # Check if scopes match a preset (use the preset name)
    scope_set = set(scopes)
    for name, preset_scopes in SCOPE_PRESETS.items():
        if set(preset_scopes) == scope_set:
            return name
    # Fallback: hash of sorted scope URLs
    import hashlib
    h = hashlib.sha256("|".join(sorted(scopes)).encode()).hexdigest()[:12]
    return f"custom-{h}"


def _find_credentials(service=None, creds_path=None):
    """Find the credentials.json file to use."""
    if creds_path:
        p = Path(creds_path).expanduser()
        if p.exists():
            return p
        raise FileNotFoundError(f"Specified credentials not found: {creds_path}")

    # Check env vars for calendar
    if service == "calendar":
        env_path = os.environ.get("GCAL_CREDENTIALS_PATH")
        if env_path:
            p = Path(env_path).expanduser()
            if p.exists():
                return p

    # Search service-specific paths
    search_paths = SERVICE_CREDENTIALS.get(service, DEFAULT_CREDENTIALS)
    for path_str in search_paths:
        p = Path(path_str).expanduser()
        if p.exists():
            return p

    # Last resort: check default paths
    if service and service in SERVICE_CREDENTIALS:
        for path_str in DEFAULT_CREDENTIALS:
            p = Path(path_str).expanduser()
            if p.exists():
                return p

    checked = search_paths if service not in SERVICE_CREDENTIALS else search_paths + DEFAULT_CREDENTIALS
    raise FileNotFoundError(
        "No credentials.json found. Checked:\n"
        + "\n".join(f"  {p}" for p in checked)
    )


def get_credentials(service=None, scopes=None, creds_path=None, token_name=None):
    """
    Get Google API credentials with automatic token caching.

    Args:
        service: Service name for credential lookup ("drive", "sheets",
                 "calendar", "forms", "thoughtgun"). Defaults to drive/sheets.
        scopes: Scope preset name (e.g. "sheets-readonly"), a single scope URL,
                or a list of scope URLs. Defaults to drive+sheets.
        creds_path: Override credential file path (skips service lookup).
        token_name: Override token filename (default: derived from scopes).

    Returns:
        google.oauth2.credentials.Credentials (or service account credentials)
    """
    import sys

    scopes_list = _resolve_scopes(scopes)
    creds_file = _find_credentials(service=service, creds_path=creds_path)

    # Service account detection
    try:
        with open(creds_file) as f:
            data = json.load(f)
            if data.get("type") == "service_account":
                return service_account.Credentials.from_service_account_file(
                    str(creds_file), scopes=scopes_list
                )
    except (json.JSONDecodeError, KeyError):
        pass

    # Token path: check env var for calendar, otherwise use standard dir
    if service == "calendar":
        env_token = os.environ.get("GCAL_TOKEN_PATH")
        if env_token:
            token_path = Path(env_token).expanduser()
        else:
            token_path = TOKEN_DIR / f"{token_name or _scope_key(scopes_list)}.pickle"
    else:
        token_path = TOKEN_DIR / f"{token_name or _scope_key(scopes_list)}.pickle"

    TOKEN_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Load cached token
    creds = None
    if token_path.exists():
        try:
            with open(token_path, "rb") as f:
                creds = pickle.load(f)
        except Exception:
            pass

    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed ({e}), re-authenticating...", file=sys.stderr)
                token_path.unlink(missing_ok=True)
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), scopes_list)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as f:
            pickle.dump(creds, f)
        token_path.chmod(0o600)

    return creds


# ---------------------------------------------------------------------------
# URL/ID helpers
# ---------------------------------------------------------------------------

def extract_google_id(input_string):
    """Extract Google doc/sheet/form/slide ID from URL, or return as-is if already an ID."""
    if not input_string:
        raise ValueError("Empty input")
    # Already a bare ID
    if re.match(r"^[a-zA-Z0-9-_]+$", input_string):
        return input_string
    # Extract from URL
    patterns = [
        r"/spreadsheets/d/([a-zA-Z0-9-_]+)",
        r"/document/d/([a-zA-Z0-9-_]+)",
        r"/forms/d/([a-zA-Z0-9-_]+)",
        r"/presentation/d/([a-zA-Z0-9-_]+)",
        r"/file/d/([a-zA-Z0-9-_]+)",
        r"/d/([a-zA-Z0-9-_]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, input_string)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract Google ID from: {input_string}")


def extract_gid(url):
    """Extract worksheet GID from a Google Sheets URL. Returns None if not found."""
    if not url:
        return None
    match = re.search(r"gid=(\d+)", url)
    return int(match.group(1)) if match else None
