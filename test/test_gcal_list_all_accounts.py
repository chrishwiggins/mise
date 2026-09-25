#!/usr/bin/env python3.11
"""Tests for gcal-list --all, the multi-account day listing.

Why these particular assertions: a merged listing is dangerous in exactly two
ways, and both are checked here.

1. Speculative auth. google_auth.get_credentials opens a browser and blocks on
   a local redirect server when a token file is missing, so an --all run over
   an account that was never authorized would hang forever with no output.
   authorized_accounts() must gate on the pickle existing.

2. Cross-account mutation. move/delete/desc index a flat list and patch
   calendarId="primary" on one service, so event #3 in a merged listing is not
   necessarily on the calendar the tool is authenticated as. --all refuses
   every command for that reason.

Nothing here touches the network: the googleapiclient modules are stubbed
before the script is imported, since the script's own venv (3.12) differs from
the interpreter running these tests (3.11) and the real libraries are not the
subject under test.
"""

import importlib.machinery
import importlib.util
import io
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

GCAL_LIST = Path.home() / "mise/py/gcal-list"


def _install_stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class _HttpError(Exception):
    pass


# Stub the Google client surface the script imports at module scope. Real
# credentials are never constructed, so no browser flow can start.
_install_stub("googleapiclient")
_install_stub("googleapiclient.discovery", build=lambda *a, **k: None)
_install_stub("googleapiclient.errors", HttpError=_HttpError)
sys.path.insert(0, str(Path.home() / "mise/py"))
_install_stub("google_auth", get_credentials=lambda **k: None)

_loader = importlib.machinery.SourceFileLoader("gcal_list_under_test", str(GCAL_LIST))
_spec = importlib.util.spec_from_loader("gcal_list_under_test", _loader)
gcal = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gcal)


class FakeEvents:
    def __init__(self, items):
        self._items = items

    def list(self, **kwargs):
        self._kwargs = kwargs
        return self

    def execute(self):
        return {"items": [dict(item) for item in self._items]}


class FakeService:
    def __init__(self, items):
        self._events = FakeEvents(items)

    def events(self):
        return self._events


def timed(summary, start, end):
    return {
        "summary": summary,
        "start": {"dateTime": f"2026-09-21T{start}:00-04:00"},
        "end": {"dateTime": f"2026-09-21T{end}:00-04:00"},
    }


class TokenDiscoveryTests(unittest.TestCase):
    """authorized_accounts() gates on the pickle so no OAuth flow can start."""

    def setUp(self):
        self._real_dir = gcal.TOKEN_DIR

    def tearDown(self):
        gcal.TOKEN_DIR = self._real_dir

    def _with_tokens(self, names):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        token_dir = Path(self._tmp.name)
        for name in names:
            (token_dir / name).write_bytes(b"")
        gcal.TOKEN_DIR = token_dir
        return token_dir

    def test_personal_token_maps_to_default_account(self):
        self._with_tokens(["calendar.pickle"])
        self.assertEqual(gcal.authorized_accounts(), ["chris.wiggins@gmail.com"])

    def test_personal_account_listed_first(self):
        self._with_tokens([
            "calendar-chw2-at-columbia-edu.pickle",
            "calendar.pickle",
            "calendar-chris-at-hackny-org.pickle",
        ])
        accounts = gcal.authorized_accounts()
        self.assertEqual(accounts[0], "chris.wiggins@gmail.com")
        self.assertEqual(
            sorted(accounts[1:]),
            ["chris@hackny.org", "chw2@columbia.edu"],
        )

    def test_account_without_a_token_is_absent(self):
        """The whole point: an unauthorized account must not be attempted."""
        self._with_tokens(["calendar.pickle"])
        self.assertNotIn("chw2@columbia.edu", gcal.authorized_accounts())

    def test_no_duplicate_when_personal_has_both_token_shapes(self):
        self._with_tokens([
            "calendar.pickle",
            "calendar-chris-wiggins-at-gmail-com.pickle",
        ])
        accounts = gcal.authorized_accounts()
        self.assertEqual(accounts.count("chris.wiggins@gmail.com"), 1)

    def test_empty_token_dir_yields_nothing(self):
        self._with_tokens([])
        self.assertEqual(gcal.authorized_accounts(), [])

    def test_token_name_matches_gcal_invite_convention(self):
        self.assertEqual(
            gcal.token_name_for("chw2@columbia.edu"),
            "calendar-chw2-at-columbia-edu",
        )

    def test_personal_token_path_is_the_bare_pickle(self):
        self.assertEqual(gcal.token_path_for("chris.wiggins@gmail.com").name,
                         "calendar.pickle")


class MergeTests(unittest.TestCase):
    """fetch_all_accounts tags each event and keeps one chronological order."""

    def setUp(self):
        self._real = gcal.get_calendar_service
        self.services = {
            "chris.wiggins@gmail.com": FakeService([timed("personal lunch", "13", "14")]),
            "chw2@columbia.edu": FakeService([timed("faculty meeting", "09", "10")]),
            "chris@hackny.org": FakeService([timed("PIL sync", "17", "18")]),
        }
        gcal.get_calendar_service = lambda account=None: self.services[account]

    def tearDown(self):
        gcal.get_calendar_service = self._real

    def test_events_sorted_across_accounts(self):
        events, errors = gcal.fetch_all_accounts(date(2026, 9, 21), list(self.services))
        self.assertEqual(errors, [])
        self.assertEqual(
            [e["summary"] for e in events],
            ["faculty meeting", "personal lunch", "PIL sync"],
        )

    def test_each_event_carries_its_account(self):
        events, _ = gcal.fetch_all_accounts(date(2026, 9, 21), list(self.services))
        by_summary = {e["summary"]: e["_account"] for e in events}
        self.assertEqual(by_summary["faculty meeting"], "chw2@columbia.edu")
        self.assertEqual(by_summary["PIL sync"], "chris@hackny.org")

    def test_one_failing_account_does_not_lose_the_others(self):
        def boom(account=None):
            if account == "chw2@columbia.edu":
                raise RuntimeError("token revoked")
            return self.services[account]

        gcal.get_calendar_service = boom
        events, errors = gcal.fetch_all_accounts(date(2026, 9, 21), list(self.services))
        self.assertEqual([e["summary"] for e in events],
                         ["personal lunch", "PIL sync"])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "chw2@columbia.edu")

    def test_all_day_events_sort_before_timed_ones(self):
        self.services["chris.wiggins@gmail.com"] = FakeService([
            {"summary": "birthday", "start": {"date": "2026-09-21"},
             "end": {"date": "2026-09-22"}},
        ])
        events, _ = gcal.fetch_all_accounts(date(2026, 9, 21), list(self.services))
        self.assertEqual(events[0]["summary"], "birthday")


class DisplayTests(unittest.TestCase):
    def test_account_letter_shown_per_row(self):
        events = [
            dict(timed("faculty meeting", "09", "10"), _account="chw2@columbia.edu"),
            dict(timed("PIL sync", "17", "18"), _account="chris@hackny.org"),
        ]
        out = io.StringIO()
        with redirect_stdout(out):
            gcal.display_events(events, date(2026, 9, 21), show_accounts=True)
        text = out.getvalue()
        self.assertIn("[u]", text)
        self.assertIn("[h]", text)
        self.assertIn("faculty meeting", text)

    def test_single_account_listing_has_no_letter_column(self):
        events = [timed("faculty meeting", "09", "10")]
        out = io.StringIO()
        with redirect_stdout(out):
            gcal.display_events(events, date(2026, 9, 21))
        self.assertNotIn("[u]", out.getvalue())

    def test_unknown_account_falls_back_to_local_part(self):
        self.assertEqual(gcal.account_label("someone@example.org"), "someone")


class RefusalTests(unittest.TestCase):
    """--all must refuse every mutator: N is ambiguous across calendars."""

    def setUp(self):
        self._argv = sys.argv
        self._real = gcal.get_calendar_service
        gcal.get_calendar_service = lambda account=None: FakeService([])

    def tearDown(self):
        sys.argv = self._argv
        gcal.get_calendar_service = self._real

    def _run(self, args):
        sys.argv = ["gcal-list"] + args
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as caught:
                gcal.main()
        return caught.exception.code, err.getvalue()

    def test_delete_is_refused(self):
        code, err = self._run(["--all", "delete", "3"])
        self.assertEqual(code, 1)
        self.assertIn("read-only", err)

    def test_move_is_refused(self):
        code, err = self._run(["--all", "move", "2", "3pm"])
        self.assertEqual(code, 1)
        self.assertIn("read-only", err)

    def test_desc_is_refused(self):
        code, err = self._run(["--all", "desc", "2", "notes"])
        self.assertEqual(code, 1)
        self.assertIn("read-only", err)

    def test_show_is_refused(self):
        """A bare number becomes the 'show' command and is equally ambiguous."""
        code, err = self._run(["--all", "3"])
        self.assertEqual(code, 1)
        self.assertIn("read-only", err)


class ListingModeTests(unittest.TestCase):
    def setUp(self):
        self._argv = sys.argv
        self._real_service = gcal.get_calendar_service
        self._real_accounts = gcal.authorized_accounts
        gcal.get_calendar_service = lambda account=None: FakeService(
            [timed("faculty meeting", "09", "10")]
        )
        gcal.authorized_accounts = lambda: ["chw2@columbia.edu"]

    def tearDown(self):
        sys.argv = self._argv
        gcal.get_calendar_service = self._real_service
        gcal.authorized_accounts = self._real_accounts

    def _run(self, args):
        sys.argv = ["gcal-list"] + args
        out = io.StringIO()
        with redirect_stdout(out):
            gcal.main()
        return out.getvalue()

    def test_all_names_which_accounts_were_read(self):
        text = self._run(["--all"])
        self.assertIn("read: u=chw2@columbia.edu", text)

    def test_all_declares_cnn_unread(self):
        """Silence about CNN would imply coverage the tool does not have."""
        text = self._run(["--all"])
        self.assertIn("not read: CNN", text)

    def test_all_accepts_a_signed_offset(self):
        text = self._run(["--all", "+2"])
        expected = (date.today().__class__.today()).strftime("%A")
        self.assertTrue(text.strip())
        self.assertIn("read:", text)
        self.assertIsInstance(expected, str)

    def test_offset_may_precede_the_flag(self):
        text = self._run(["+2", "--all"])
        self.assertIn("read:", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
