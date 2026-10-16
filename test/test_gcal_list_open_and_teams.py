#!/usr/bin/env python3.11
"""Regression tests for gcal-list's event-number arguments and calzoom's Teams links.

Each case pins a bug that was live on 2026-10-16:

1. `gcal-list 2 open` and `gcal-list 2 U` silently ignored the trailing word and
   printed event #2's details again, so the meeting link never opened.
2. `gcal-list delete 3 4` deleted #3 and dropped the 4 without a word, and
   `delete 3 y` (no dash) was not treated as -y but was not refused either.
3. `zooms` (calzoom) did not recognize Teams links at all, so a Teams call in
   the location field never appeared in its menu.

Nothing here touches the network or opens anything: the Google client modules
are stubbed, events are fed in directly, and the opener is replaced by a
recorder.
"""

import importlib.machinery
import importlib.util
import io
import sys
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

PY = Path.home() / "mise/py"


def _install_stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class _HttpError(Exception):
    pass


_install_stub("googleapiclient")
_install_stub("googleapiclient.discovery", build=lambda *a, **k: None)
_install_stub("googleapiclient.errors", HttpError=_HttpError)
sys.path.insert(0, str(PY))
_install_stub("google_auth", get_credentials=lambda **k: None)


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


gcal = _load("gcal_list_under_test", PY / "gcal-list")
calzoom = _load("calzoom_under_test", PY / "calzoom")

TEAMS = "https://teams.live.com/meet/9316799086680?p=b04TLQtoQ2nPsfbUyQ"
EVENTS = [
    {"id": "a", "summary": "No link",
     "start": {"dateTime": "2026-10-16T08:00:00-04:00"},
     "end": {"dateTime": "2026-10-16T08:30:00-04:00"}},
    {"id": "b", "summary": "Meeting FS CW", "location": TEAMS,
     "start": {"dateTime": "2026-10-16T09:00:00-04:00"},
     "end": {"dateTime": "2026-10-16T10:00:00-04:00"}},
]


def run_gcal(*argv):
    """Run gcal-list main() on EVENTS; return (exit code, stdout, stderr, opened urls, service)."""
    opened = []
    service = mock.MagicMock()
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with mock.patch.object(gcal, "get_calendar_service", return_value=service), \
         mock.patch.object(gcal, "fetch_events", return_value=[dict(e) for e in EVENTS]), \
         mock.patch("subprocess.call", side_effect=lambda cmd: opened.append(cmd[-1]) or 0), \
         mock.patch.object(sys, "argv", ["gcal-list", *argv]), \
         redirect_stdout(out), redirect_stderr(err):
        try:
            gcal.main()
        except SystemExit as e:
            code = e.code or 0
    return code, out.getvalue(), err.getvalue(), opened, service


class OpenEventUrl(unittest.TestCase):
    def test_trailing_open_words_open_the_url(self):
        for argv in (["2", "open"], ["2", "U"], ["open", "2"], ["+0", "2", "open"]):
            with self.subTest(argv=argv):
                code, _, _, opened, _ = run_gcal(*argv)
                self.assertEqual(code, 0)
                self.assertEqual(opened, [TEAMS])

    def test_unknown_trailing_word_is_refused_not_ignored(self):
        code, out, err, opened, _ = run_gcal("2", "foo")
        self.assertEqual(code, 1)
        self.assertIn("unexpected", err)
        self.assertEqual(opened, [])
        self.assertNotIn("Meeting FS CW", out)

    def test_event_without_url_errors(self):
        code, _, err, opened, _ = run_gcal("1", "open")
        self.assertEqual(code, 1)
        self.assertIn("has no url", err)
        self.assertEqual(opened, [])

    def test_bare_number_still_shows_details(self):
        code, out, _, opened, _ = run_gcal("2")
        self.assertEqual(code, 0)
        self.assertIn(TEAMS, out)
        self.assertEqual(opened, [])


class DeleteArguments(unittest.TestCase):
    def test_extra_event_number_is_refused(self):
        code, _, err, _, service = run_gcal("delete", "1", "2")
        self.assertEqual(code, 1)
        self.assertIn("unexpected: 2", err)
        service.events.return_value.delete.assert_not_called()

    def test_undashed_y_is_refused(self):
        code, _, err, _, service = run_gcal("delete", "1", "y")
        self.assertEqual(code, 1)
        service.events.return_value.delete.assert_not_called()

    def test_dash_y_still_deletes_without_prompt(self):
        code, out, _, _, service = run_gcal("delete", "1", "-y")
        self.assertEqual(code, 0)
        self.assertIn("Deleted: No link", out)
        service.events.return_value.delete.assert_called_once_with(
            calendarId="primary", eventId="a")


class CalzoomTeams(unittest.TestCase):
    def test_teams_urls_are_extracted_and_labelled(self):
        cases = {
            TEAMS: "teams",
            "Join: https://teams.microsoft.com/l/meetup-join/19%3ameeting_abc%40thread.v2/0?context=x.":
                "teams",
            "https://teams.microsoft.com/meet/123456?p=abc": "teams",
            "https://us02web.zoom.us/j/123": "zoom",
            "https://meet.google.com/abc-defg-hij": "meet",
        }
        for text, kind in cases.items():
            with self.subTest(text=text):
                urls = calzoom.extract_zoom_urls(text)
                self.assertEqual(len(urls), 1)
                self.assertFalse(urls[0].endswith("."))
                self.assertEqual(calzoom.meeting_kind(urls[0]), kind)

    def test_teams_call_in_location_appears_in_menu(self):
        svc = mock.MagicMock()
        svc.events.return_value.list.return_value.execute.return_value = {
            "items": [dict(e) for e in EVENTS]}
        with mock.patch.object(calzoom, "get_calendar_service", return_value=svc):
            meetings = calzoom.fetch_zoom_meetings(["chris.wiggins@gmail.com"])
        self.assertEqual([m["summary"] for m in meetings], ["Meeting FS CW"])
        self.assertIn(" teams ", calzoom.format_meeting(meetings[0], 1))

    def test_teams_opens_in_browser_not_zoom_app(self):
        meeting = {"summary": "x", "zoom_urls": [TEAMS], "account": "chris.wiggins@gmail.com",
                   "start": calzoom.datetime(2026, 10, 16, 9, tzinfo=calzoom.LOCAL_TZ),
                   "end": calzoom.datetime(2026, 10, 16, 10, tzinfo=calzoom.LOCAL_TZ)}
        with mock.patch.object(calzoom, "open_in_browser") as browser, \
             mock.patch.object(calzoom.subprocess, "run") as run, \
             redirect_stdout(io.StringIO()):
            calzoom.open_zoom_meeting(meeting)
        browser.assert_called_once_with(TEAMS, "chris.wiggins@gmail.com")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
