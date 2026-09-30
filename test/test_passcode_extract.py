#!/usr/bin/env python3.11
"""Synthetic tests for mise/py/passcode_extract.py (no real mail, no PII).

Run: python3.11 test/test_passcode_extract.py
"""

import sys
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py"))
from passcode_extract import extract, extract_text  # noqa: E402


def eml(subject, body, html=False):
    m = EmailMessage()
    m["Subject"] = subject
    m["From"] = "no-reply@example.com"
    m.set_content(body, subtype="html" if html else "plain")
    return m.as_bytes()


CASES = [
    # (label, subject, body, html, expected code or None, expected rule)
    ("label line, mixed case", "Verification code",
     "Dear user,\nYour verification code is:\n\nQ7rTz2\n\nand is valid for 20 minutes.", False,
     "Q7rTz2", "label-line"),
    ("inline passcodes", "New text message from 12345",
     "SMS passcodes: 4410923\nTo respond, open the app.", False, "4410923", "inline"),
    ("inline code is", "Sign in", "Hi,\nYour code is 482913. It expires soon.", False,
     "482913", "inline"),
    ("X is your code", "Sign in", "482913 is your Example verification code.", False,
     "482913", "inline"),
    ("2FA word is not a code", "Login", "Enter your 2FA code: 551234 to continue.", False,
     "551234", "inline"),
    ("subject only", "Your one-time code: 774201", "Use the code in the subject line.", False,
     "774201", "subject"),
    ("html only", "Verify",
     "<html><body><p>Your verification code is:</p><p><strong>583920</strong></p></body></html>",
     True, "583920", "label-line"),
    ("lone number", "Sign in to Example", "Use 90817 to sign in. Ignore if this was not you.",
     False, "90817", "lone-number"),
    ("ambiguous inline", "Codes", "Your code is 111222.\nBackup code: 333444.", False,
     None, "inline"),
    ("newsletter, no code", "The Morning",
     "Call 212-555-0100. The 2026 report is out: https://example.com/a/12345678\n"
     "Example Inc, 1600 Main St, Mountain View CA 94043\nSent 2026-09-29 at 10:15.",
     False, None, None),
]


def main():
    fails = 0
    for label, subject, body, is_html, want, rule in CASES:
        r = extract(eml(subject, body, is_html))
        ok = r.code == want and r.rule == rule
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: got {r!r}")
        fails += not ok
    # Positive control: extract_text on the same shape as a bytes case agrees.
    r = extract_text("x", "Your code is 482913.")
    ok = r.code == "482913"
    print(f"  {'ok  ' if ok else 'FAIL'} extract_text agrees with extract")
    fails += not ok
    print("\nall passed" if not fails else f"\n{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
