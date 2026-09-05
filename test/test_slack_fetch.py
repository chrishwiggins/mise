#!/usr/bin/python3
"""Regression tests for ~/mise/py/slack-fetch permalink parsing.

Runs without credentials and touches no network: it imports the script by path
and exercises parse_permalink only.

    python3 test/test_slack_fetch.py
"""

import importlib.util
import os
import sys
import unittest

SCRIPT = os.path.expanduser("~/mise/py/slack-fetch")


def load():
    """Import an extensionless script by path."""
    spec = importlib.util.spec_from_loader(
        "slack_fetch", importlib.machinery.SourceFileLoader("slack_fetch", SCRIPT)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestParsePermalink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_clean_permalink(self):
        got = self.m.parse_permalink(
            "https://hackny.slack.com/archives/C0AKK6PDG0P/p1786912252317009"
        )
        self.assertEqual(got, ("C0AKK6PDG0P", "1786912252.317009"))

    def test_redir_wrapper(self):
        """The login-bounce form Slack hands you when not signed in.

        The path is percent-encoded inside a ?redir= parameter. This is the
        case that regressed once: the regex matched only after the URL was
        unquoted, so the wrapper form silently returned None.
        """
        got = self.m.parse_permalink(
            "https://hackny.slack.com/?redir=%2Farchives%2FC0AKK6PDG0P"
            "%2Fp1786912252317009%3Fname%3DC0AKK6PDG0P%26perma%3D1786912252317009"
        )
        self.assertEqual(got, ("C0AKK6PDG0P", "1786912252.317009"))

    def test_thread_permalink_with_query(self):
        got = self.m.parse_permalink(
            "https://hackny.slack.com/archives/C0AKK6PDG0P/p1786912252317009"
            "?thread_ts=1786912000.000100&cid=C0AKK6PDG0P"
        )
        self.assertEqual(got, ("C0AKK6PDG0P", "1786912252.317009"))

    def test_non_permalink_returns_none(self):
        self.assertIsNone(self.m.parse_permalink("https://example.com/nope"))
        self.assertIsNone(self.m.parse_permalink("C0AKK6PDG0P"))

    def test_microsecond_split_is_exact(self):
        """ts is the 10-digit epoch, a dot, then exactly 6 more digits.

        Getting this wrong yields a ts Slack rejects, which surfaces as a
        confusing message_not_found rather than a parse error.
        """
        chan, ts = self.m.parse_permalink(
            "https://x.slack.com/archives/C123ABC/p1700000000123456"
        )
        self.assertEqual(chan, "C123ABC")
        self.assertEqual(ts, "1700000000.123456")


if __name__ == "__main__":
    unittest.main(verbosity=2)
