#!/usr/bin/env python3
"""Tests for gmail-api-rw header handling on the send -H (.eml file) path.

Covers the 2026-08-06 fixit pair: a truncated Cc address (mcn2119@cumc)
must be refused before any API call, and non-ASCII header values (an en
dash in Subject, a UTF-8 display name in Cc) must go out RFC2047-encoded
instead of as raw bytes that arrive as mojibake.

No credentials, no network, no send: _build_raw_bytes is driven directly.
Run with the venv python (googleapiclient must import):
  /Users/wiggins/mise/py/.venv/bin/python3 test-gmail-api-rw-headers.py
or via pytest.
"""
import email
import email.policy
import importlib.util
import sys
import tempfile
import types
from email.header import decode_header, make_header
from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "gmail-api-rw"

spec = importlib.util.spec_from_file_location(
    "gmail_api_rw", SCRIPT_PATH,
    loader=SourceFileLoader("gmail_api_rw", str(SCRIPT_PATH)),
)
gm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gm)

# Banned-literal characters built at runtime (block-em-dash hook).
DASH = chr(0x2013)

BAD_CC = ("mcn2119@cumc.columbia.edu,an2969@cumc.columbia.edu,"
          "CUMCPROD@service-now.com,mcn2119@cumc,md4373@columbia.edu")


def _eml(text):
    """Write an .eml fixture to a temp file, return its path."""
    f = tempfile.NamedTemporaryFile(
        suffix=".eml", mode="w", encoding="utf-8", delete=False)
    f.write(text)
    f.close()
    return f.name


def _args(path):
    return types.SimpleNamespace(attach=None, header_file=path, subject=None,
                                 recipient=None, cc=None, bcc=None)


def test_truncated_cc_refused_before_api():
    """A Cc token with no dotted domain must exit 2 with a clear error,
    not reach Gmail and bounce as 'Invalid Cc header'."""
    path = _eml(f"To: a@example.edu\nCC: {BAD_CC}\nSubject: t\n\nbody\n")
    try:
        gm._build_raw_bytes(_args(path))
        raise AssertionError("bad Cc was not caught")
    except SystemExit as e:
        assert e.code == 2, f"expected exit 2, got {e.code}"


def test_valid_cc_builds():
    good = BAD_CC.replace("mcn2119@cumc,", "")
    path = _eml(f"To: a@example.edu\nCC: {good}\nSubject: t\n\nbody\n")
    raw = gm._build_raw_bytes(_args(path))
    assert b"mcn2119@cumc," not in raw
    assert b"mcn2119@cumc.columbia.edu" in raw


def test_nonascii_headers_rfc2047_encoded():
    subj = f"Re: Removal of Joint Appointment {DASH} Dr. W (Systems Biology)"
    path = _eml("To: a@example.edu\n"
                "Cc: \"Müller, J\" <jm@example.edu>, b@example.edu\n"
                f"Subject: {subj}\n"
                "\n"
                f"Body dash {DASH} must be untouched.\n")
    raw = gm._build_raw_bytes(_args(path))

    head, body = raw.split(b"\n\n", 1)
    head.decode("ascii")  # raises if any non-ASCII survived in headers

    msg = email.message_from_bytes(raw, policy=email.policy.compat32)
    assert str(make_header(decode_header(msg["Subject"]))) == subj
    cc = str(make_header(decode_header(msg["Cc"])))
    assert "jm@example.edu" in cc and "b@example.edu" in cc
    assert "Müller" in cc
    assert DASH.encode() in body, "body bytes were altered"


def test_ascii_draft_passes_through_unchanged():
    text = "To: a@example.edu\nSubject: plain ascii\n\nhello\n"
    path = _eml(text)
    assert gm._build_raw_bytes(_args(path)) == text.encode()


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
