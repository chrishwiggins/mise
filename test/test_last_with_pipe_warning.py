#!/usr/bin/env python3.11
"""Tests for last-with's "NO MESSAGES EVER" warning when stdout is a pipe.

Why: the warning is the only guard against a wrong fragment being reported as
"they have not written". Piping the tool through grep or head deletes the
stdout copy, leaving empty output that reads as silence (caught in TSC on
2026-09-29 and again on 2026-10-04). When stdout is not a terminal, the
warning must also reach stderr, which the pipe leaves alone.

Nothing here touches the network: accounts() and listing() are replaced with
stubs, so gmails is never run.
"""

import importlib.machinery
import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "py" / "last-with"


def load():
    loader = importlib.machinery.SourceFileLoader("last_with", str(SCRIPT))
    spec = importlib.util.spec_from_loader("last_with", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class FakeOut(io.StringIO):
    def __init__(self, tty):
        super().__init__()
        self._tty = tty

    def isatty(self):
        return self._tty


def run(mod, rows, tty):
    mod.accounts = lambda: [("g", "a@example.org"), ("u", "b@example.org")]
    mod.listing = lambda alias, query, outbound: rows(query)
    out, err = FakeOut(tty), io.StringIO()
    argv = sys.argv
    sys.argv = ["last-with", "zzqx", "1"]
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = mod.main()
    finally:
        sys.argv = argv
    return code, out.getvalue(), err.getvalue()


NONE = lambda query: ["No messages found."]


class PipeWarning(unittest.TestCase):
    def test_piped_never_seen_fragment_warns_on_stderr(self):
        code, out, err = run(load(), NONE, tty=False)
        self.assertEqual(code, 0)
        self.assertIn("NO MESSAGES EVER", out)
        self.assertIn("NO MESSAGES EVER", err)

    def test_terminal_prints_warning_once(self):
        code, out, err = run(load(), NONE, tty=True)
        self.assertIn("NO MESSAGES EVER", out)
        self.assertEqual(err, "")

    def test_known_fragment_silent_window_does_not_warn(self):
        rows = lambda query: (["No messages found."] if "newer_than:1d" in query
                              else ["1. Mon 2026-09-01 10:00  Someone  Subject"])
        code, out, err = run(load(), rows, tty=False)
        self.assertIn("fragment is good", out)
        self.assertNotIn("NO MESSAGES EVER", out + err)


if __name__ == "__main__":
    unittest.main()
