#!/usr/bin/env python3
"""Re-mint the DEFAULT-account gmail send token for a specific identity.

The default account (no -e/-F in `m`) uses two separate token files:
  ~/.config/google-tokens/gmail-readonly.pickle   (reading)
  ~/.config/google-tokens/gmail-send.pickle       (composing/replying)

These can drift to DIFFERENT Gmail identities if the browser was logged into
the wrong account when a token was minted. That makes `m ... reply` read from
one mailbox and compose from another (or, as observed, search the wrong mailbox
and report "No messages found").

This tool deletes the stale default send token and mints a fresh one with a
login_hint so the OAuth browser preselects the intended account, then verifies
the resulting token really belongs to that account before trusting it.

Usage:
    python3 ~/mise/py/gmail-remint-default-send.py chris.wiggins@gmail.com

It opens a browser; log in as the address you passed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import google_auth  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

TOKEN_DIR = Path("~/.config/google-tokens").expanduser()
SEND_TOKEN = TOKEN_DIR / "gmail-send.pickle"
VERIFIED_CACHE = Path("/tmp/spool/.gmail-api-rw-verified-accounts.json")


def main():
    if len(sys.argv) != 2 or "@" not in sys.argv[1]:
        print(f"Usage: {Path(sys.argv[0]).name} <email-address>", file=sys.stderr)
        print("  e.g. gmail-remint-default-send.py chris.wiggins@gmail.com", file=sys.stderr)
        sys.exit(2)
    target = sys.argv[1].strip()

    if SEND_TOKEN.exists():
        print(f"Removing stale default send token: {SEND_TOKEN}", file=sys.stderr)
        SEND_TOKEN.unlink()

    print(f"A browser will open. Log in as {target}.", file=sys.stderr)
    # token_name=None -> writes the default scope-keyed file (gmail-send.pickle).
    creds = google_auth.get_credentials(
        service="gmail", scopes="gmail-send", token_name=None, login_hint=target
    )

    # Verify the minted token actually belongs to the requested identity.
    svc = build("gmail", "v1", credentials=creds)
    actual = svc.users().getProfile(userId="me").execute().get("emailAddress", "")
    if actual.lower() != target.lower():
        print(f"Minted token is for {actual}, not {target}.", file=sys.stderr)
        print("You logged into the wrong Google account. Re-run and pick the right one.",
              file=sys.stderr)
        SEND_TOKEN.unlink(missing_ok=True)
        sys.exit(1)

    # Refresh the verified-account cache so `m` trusts the new pairing without a
    # round-trip. The default send identity is keyed __default__:gmail-send.
    import json
    try:
        data = json.loads(VERIFIED_CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        data = {}
    data["__default__:gmail-send"] = actual
    VERIFIED_CACHE.parent.mkdir(parents=True, exist_ok=True)
    VERIFIED_CACHE.write_text(json.dumps(data))

    print(f"Default send token re-minted for {actual}.", file=sys.stderr)
    print("`m ... reply` on the default account now composes from this identity.",
          file=sys.stderr)


if __name__ == "__main__":
    main()
