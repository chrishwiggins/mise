#!/usr/bin/env python3.11
"""sent-verify and last-with must abandon a stuck gmails call and say so.

Why: on 2026-10-04 sent-verify sat for 72 minutes inside a gmails child, and
last-with timed out twice under a 90-second outer limit. The children were
blocked in google_auth's browser OAuth flow (a 127.0.0.1 LISTEN socket waiting
for a consent nobody would give; two such processes from 2026-09-26 were still
alive eight days later). Neither tool printed anything, and a caller that
killed them could only guess. Worse, a timeout must never come out as "no hit",
"NOT FOUND" or "nothing to or from", because callers read those as facts.

Each tool is run as a real subprocess with GMAILS pointed at a stub that
answers -E with two accounts and sleeps forever on every query. With
GMAILS_TIMEOUT=2 each tool must finish well inside the outer limit, print
"TIMED OUT ... result unknown", exit 3, and print no negative verdict.
The stub never touches the network.
"""

import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

PY = Path(__file__).resolve().parent.parent / "py"
OUTER = 30  # seconds; the old code hangs past this

STUB = """#!/bin/sh
if [ "$1" = "-E" ]; then
  echo "  g: a@example.org"
  echo "  u: b@example.org"
  exit 0
fi
exec /bin/sleep 100000
"""

LAUNCH = """
import importlib.machinery, importlib.util, sys
from pathlib import Path
script, stub = sys.argv[1], sys.argv[2]
loader = importlib.machinery.SourceFileLoader("tool", script)
spec = importlib.util.spec_from_loader("tool", loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
mod.GMAILS = stub if isinstance(mod.GMAILS, str) else Path(stub)
sys.argv = [script] + sys.argv[3:]
raise SystemExit(mod.main())
"""


def run_tool(script, *args, stub=STUB):
    d = tempfile.mkdtemp()
    stub_text, stub = stub, Path(d) / "gmails"
    stub.write_text(stub_text)
    stub.chmod(stub.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, GMAILS_TIMEOUT="2")
    t0 = time.monotonic()
    # start_new_session so a hung run can be killed with its sleeping children
    p = subprocess.Popen([sys.executable, "-c", LAUNCH, str(PY / script), str(stub), *args],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                         env=env, cwd=d, start_new_session=True)
    try:
        out, err = p.communicate(timeout=OUTER)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9)
        p.communicate()
        raise AssertionError(f"{script} still running after {OUTER}s: it hangs on a stuck gmails")
    return p.returncode, out, err, time.monotonic() - t0, d


class SentVerifyTimeout(unittest.TestCase):
    def test_stuck_gmails_is_unknown_not_not_found(self):
        d = tempfile.mkdtemp()
        draft = Path(d) / "draft.eml"
        draft.write_text("To: X <x@example.org>\nSubject: hello there\n\nbody\n")
        code, out, err, secs, _ = run_tool("sent-verify", str(draft))
        self.assertIn("g: TIMED OUT after 2s, result unknown", out)
        self.assertIn("u: TIMED OUT after 2s, result unknown", out)
        self.assertNotIn("NOT FOUND", out + err)
        self.assertNotIn("no hit", out.replace("no hit in the accounts that answered", ""))
        self.assertEqual(code, 3)
        self.assertLess(secs, 15)


class LastWithTimeout(unittest.TestCase):
    def test_stuck_gmails_is_unknown_not_silence(self):
        code, out, err, secs, _ = run_tool("last-with", "zzqx", "1")
        self.assertIn("## g (a@example.org): TIMED OUT after 2s, result unknown", out)
        self.assertIn("## u (b@example.org): TIMED OUT after 2s, result unknown", out)
        for negative in ("nothing to or from", "NO MESSAGES EVER", "silence is real"):
            self.assertNotIn(negative, out + err)
        self.assertEqual(code, 3)
        # one timeout per account, not one per query: 2 accounts x 2s plus slack
        self.assertLess(secs, 15)

    def test_window_empty_but_year_check_stuck_is_unknown(self):
        # The window answers "No messages found."; the 365d widening hangs.
        # That must not become "NO MESSAGES EVER" or "silence is real".
        stub = STUB.replace('exec /bin/sleep 100000',
                            'case "$*" in *newer_than:365d*) exec /bin/sleep 100000;; esac\n'
                            'echo "No messages found."')
        code, out, err, secs, _ = run_tool("last-with", "zzqx", "1", stub=stub)
        self.assertIn("365d fragment check TIMED OUT after 2s", out)
        for negative in ("nothing to or from", "NO MESSAGES EVER", "silence is real"):
            self.assertNotIn(negative, out + err)
        self.assertEqual(code, 3)
        self.assertLess(secs, 15)


if __name__ == "__main__":
    unittest.main()
