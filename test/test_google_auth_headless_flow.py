#!/usr/bin/env python3
"""google_auth's browser OAuth flow must give up when nobody can answer it.

Why: gmails children launched by sent-verify and last-with (stdin not a tty)
fell into InstalledAppFlow.run_local_server() and listened on 127.0.0.1
forever; two from 2026-09-26 were still alive on 2026-10-04. Headless callers
now get a bounded wait (GOOGLE_AUTH_FLOW_TIMEOUT, default 120s) and a clear
RuntimeError.

Run with the mise venv (it has google_auth_oauthlib):
    ~/mise/py/.venv/bin/python3 ~/mise/test/test_google_auth_headless_flow.py

Uses a throwaway client file and token dir, and BROWSER=/usr/bin/true so no
browser opens. Nothing reaches Google.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

PY = Path(__file__).resolve().parent.parent / "py"

PROBE = r"""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import google_auth
d = Path(tempfile.mkdtemp())
client = d / "client.json"
client.write_text(json.dumps({"installed": {
    "client_id": "x.apps.googleusercontent.com", "client_secret": "y",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost"]}}))
google_auth.TOKEN_DIR = d / "tokens"
try:
    google_auth.get_credentials(service="gmail", scopes="gmail-readonly",
                                creds_path=str(client), token_name="probe-no-such-token")
    print("RETURNED")
except RuntimeError as e:
    print("RAISED", e)
"""


class HeadlessFlow(unittest.TestCase):
    def test_headless_flow_times_out(self):
        env = dict(os.environ, GOOGLE_AUTH_FLOW_TIMEOUT="3", BROWSER="/usr/bin/true")
        try:
            r = subprocess.run([sys.executable, "-c", PROBE, str(PY)], env=env,
                               stdin=subprocess.DEVNULL, capture_output=True,
                               text=True, timeout=30)
        except subprocess.TimeoutExpired:
            self.fail("browser OAuth flow still waiting after 30s with no terminal")
        self.assertIn("RAISED google_auth: no browser consent", r.stdout)
        self.assertIn("browser consent needed for probe-no-such-token", r.stderr)


if __name__ == "__main__":
    unittest.main()
