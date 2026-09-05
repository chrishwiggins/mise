"""Regression tests for bash/subcommand-dispatch and its wrappers.

The bug: `gcal` was a tcsh alias for `chrome-profile-open 0 <calendar url>`.
tcsh appends unmatched arguments to an alias expansion, and
chrome-profile-open reads only $1 and $2, so

    gcal solo "tomorrow 4:30 pm bar6"

opened a bare calendar page and threw the rest away -- no event, no error.
subcommand-dispatch replaces that alias shape: a known subcommand dispatches
to <name>-<sub>, and an unknown one FAILS instead of discarding arguments.
"""

import os
import stat
import subprocess
import unittest
from pathlib import Path

BASH_DIR = Path(__file__).resolve().parent.parent / "bash"
DISPATCH = BASH_DIR / "subcommand-dispatch"

WRAPPERS = ["gcal", "gdrive", "gsheet", "quote"]


def make_stub(directory, name, marker):
    """Create an executable stub that echoes a marker plus its arguments."""
    path = directory / name
    path.write_text('#!/bin/bash\necho "%s $@"\n' % marker)
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


class TestSubcommandDispatch(unittest.TestCase):
    def setUp(self):
        import tempfile

        self.tmp = tempfile.TemporaryDirectory()
        self.bin = Path(self.tmp.name)
        # A fake subcommand and a fake fallback, so nothing real is invoked.
        make_stub(self.bin, "demo-solo", "SOLO:")
        make_stub(self.bin, "demo-list", "LIST:")
        make_stub(self.bin, "fake-browser", "BROWSER:")
        self.env = dict(os.environ, PATH=f"{self.bin}:{BASH_DIR}:{os.environ['PATH']}")

    def tearDown(self):
        self.tmp.cleanup()

    def run_dispatch(self, *args):
        cmd = [
            str(DISPATCH),
            "demo",
            "fake-browser",
            "http://example.invalid/",
            "--",
            *args,
        ]
        return subprocess.run(cmd, capture_output=True, text=True, env=self.env)

    def test_subcommand_receives_all_arguments(self):
        """The exact bug: multi-word text must reach the subcommand intact."""
        r = self.run_dispatch("solo", "tomorrow 4:30 pm bar6")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "SOLO: tomorrow 4:30 pm bar6")

    def test_arguments_are_not_silently_swallowed(self):
        """An unknown subcommand must fail loudly, never open the fallback."""
        r = self.run_dispatch("bogus", "tomorrow 4:30 pm bar6")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no such subcommand: bogus", r.stderr)
        self.assertNotIn("BROWSER:", r.stdout)

    def test_bare_name_runs_fallback(self):
        r = self.run_dispatch()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("BROWSER: http://example.invalid/", r.stdout)

    def test_leading_flag_runs_fallback(self):
        r = self.run_dispatch("--profile")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("BROWSER:", r.stdout)

    def test_url_argument_runs_fallback(self):
        r = self.run_dispatch("https://calendar.google.com/")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("BROWSER:", r.stdout)

    def test_help_lists_discovered_subcommands(self):
        r = self.run_dispatch("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("solo", r.stdout)
        self.assertIn("list", r.stdout)

    def test_wrappers_exist_and_are_executable(self):
        for name in WRAPPERS:
            p = BASH_DIR / name
            self.assertTrue(p.exists(), f"missing wrapper: {name}")
            self.assertTrue(os.access(p, os.X_OK), f"not executable: {name}")

    def test_wrappers_reject_unknown_subcommands(self):
        """Every wrapper must inherit the fail-loudly behavior."""
        for name in WRAPPERS:
            r = subprocess.run(
                [str(BASH_DIR / name), "definitelynotasubcommand"],
                capture_output=True,
                text=True,
                env=self.env,
            )
            self.assertEqual(r.returncode, 1, f"{name} did not fail")
            self.assertIn("no such subcommand", r.stderr, name)


class TestAliasesRemoved(unittest.TestCase):
    """The shadowing tcsh aliases must stay gone, or the bug comes back."""

    FILES = [
        Path("/Users/wiggins/mise/sh/aliases-public.sh"),
        Path("/Users/wiggins/gd/local/seiton/sh/aliases-private.sh"),
    ]

    def test_no_alias_shadows_a_dispatcher(self):
        for f in self.FILES:
            if not f.exists():
                continue
            for i, line in enumerate(f.read_text().splitlines(), 1):
                if line.lstrip().startswith("#"):
                    continue
                for name in WRAPPERS:
                    self.assertFalse(
                        line.startswith(f"alias {name} ")
                        or line.startswith(f'alias {name}\t'),
                        f"{f}:{i} redefines '{name}' as an alias: {line}",
                    )


if __name__ == "__main__":
    unittest.main()
