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
    ("label wrapped across lines, colon on the next", "Your confirmation code",
     "Sign-in from unrecognized device.\n To verify, please use the following code to"
     " enable your new device, it will expire in 30\n minutes:\n 3b7c19\n"
     "That wasn't me!\n Contact us:\n 4800 West\n Example Street, Suite 2, Phoenix, AZ 85001",
     False, "3b7c19", "label-line"),
    ("html label, code after many blank lines", "Your confirmation code",
     "<p>please use the following code to enable your new device, it will expire in 30"
     "<br>minutes:</p>" + "<div>   </div>\n" * 10 + "<p>  9f2e41 </p><p>That wasn't me!</p>"
     "<p>4800 West Example Street</p>",
     True, "9f2e41", "label-line"),
    ("street number is not a lone code", "Sign in to Example",
     "We could not verify your sign-in.\nExample Inc, 4800 East Example Street, Suite 2",
     False, None, None),
    ("code alone on a line, sentence between it and the label, phone footer",
     "Example Journey: Your verification code",
     "Dear Guest,\n\nPlease use the verification code below to sign in and verify your"
     " account: user@example.com ( # )\n\nPlease do not share your code or forward this"
     " email to anyone.\n\n618204\n\nThis code will expire in 15 minutes.\n\n"
     "United Kingdom:\xa0 0800 555 0142 | Outside the UK:\xa0 +44 208 555 0177\n\n"
     "5700 Example Avenue, Suite 200, Exampleton, California 90001\n",
     False, "618204", "lone-number"),
    ("promo code at checkout is not a passcode", "55% off Black Friday",
     "Use code  BF55  at checkout. Offer ends Friday.", False, None, None),
    ("promo code on its own line in a sale", "Black Friday",
     "Enjoy up to 55% off with the promotional code.\nCode: 26BF15\nBook now.",
     False, None, None),
    ("mail code in a signature", "Reminder: seminar",
     "Please sign in at the front desk.\n500 Example Street, Mail Code: 4701",
     False, None, None),
    ("footer account number far from the sign-in word", "Alerts: Daily Balance",
     "Log in to see your balance.\n\nBalance: $1\n\nImportant information:\n"
     "Example Brokerage LLC, 900 Example Street, Exampleton, RI 02999.\n  537048\n"
     "(c) 2026 Example LLC.", False, None, None),
    ("member id after a login link", "Election: login information below",
     "Use the link below:\nhttps://example.com/login.aspx?o=1&u=60025276&p=XYZ\n"
     "Member ID: 60025276\nPassword: XYZ\n\nThis message was sent by the vendor.\n\n"
     "To vote, log in.\n\nThanks.", False, None, None),
    ("zip after a comma-state footer", "Sign in to Example",
     "Sign in with 731905. Example Media, Santa Rosa, CA, 95401", False,
     "731905", "lone-number"),
    ("promo line in a mail that also says sign in", "Black Friday savings",
     "Use code BF55 at checkout.\nSign in to your account to see more.", False,
     None, None),
    ("two numbers alone on lines stay ambiguous", "Sign in to Example",
     "Verify your sign-in.\n\n618204\n\n775310\n\nCall 0800 555 0142.", False,
     None, "lone-number"),
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
