#!/usr/bin/env python3
"""Regression test for the alias migration gate.

Run: python3 /Users/wiggins/mise/test/test_alias_golden.py

No credentials, no network, no side effects; alias-golden.py parses rather
than executes, so running this cannot touch the alias file or launch anything.

Why this exists. doc/plan-tcsh2bash.md makes the golden captures a hard gate:
no alias may be edited until its current expansion is recorded, because
afterwards the original is unrecoverable except from git. The gate was only
ever enforced by remembering to run `alias-golden.py --check` by hand, which
is exactly the kind of step that gets skipped in the middle of a batch. This
turns it into a test that fails loudly instead.

A failure here means one of three things:

  1. An alias changed and the capture was not refreshed. If the change was
     intended, rerun `./test/alias-golden.py` and commit the new captures in
     the SAME commit as the alias edit, so the diff shows both.
  2. An alias was added or retired without refreshing captures. Same fix.
  3. A translation changed behavior. This is the case the gate exists for.
     Do not refresh the captures; fix the translation.

The named-alias tests below pin the specific behaviors the migration must
preserve, so a future rewrite of alias-golden.py cannot quietly lose them.
"""

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import unittest

MISE = os.path.expanduser('~/mise')
HARNESS = os.path.join(MISE, 'test/alias-golden.py')
ALIASES = os.path.join(MISE, 'sh/aliases-public.sh')

# The captures are fixtures describing one person's aliases, so they are kept
# outside this repo and located by $ALIAS_GOLDEN_DIR. This repo must still
# test green without them: the two gate tests skip when they are absent, while
# every expansion test below runs regardless, since those assert csh semantics
# and need no fixture at all.
GOLDEN_DIR = (os.environ.get('ALIAS_GOLDEN_DIR')
              or os.path.join(MISE, 'dat/alias-golden'))
HAVE_CAPTURES = os.path.isdir(GOLDEN_DIR)
NO_CAPTURES = f'no captures at {GOLDEN_DIR}; set $ALIAS_GOLDEN_DIR'

# alias-golden.py has no .py-importable name on disk, so load it by path.
_loader = importlib.machinery.SourceFileLoader('alias_golden', HARNESS)
_spec = importlib.util.spec_from_loader('alias_golden', _loader)
ag = importlib.util.module_from_spec(_spec)
_loader.exec_module(ag)


class TestGate(unittest.TestCase):
    """The gate itself: stored captures must still match the alias file."""

    @unittest.skipUnless(HAVE_CAPTURES, NO_CAPTURES)
    def test_check_reports_no_differences(self):
        r = subprocess.run([sys.executable, HARNESS, '--check'],
                           capture_output=True, text=True)
        self.assertEqual(
            r.returncode, 0,
            'alias captures are stale or an alias changed:\n' + r.stdout)

    @unittest.skipUnless(HAVE_CAPTURES, NO_CAPTURES)
    def test_every_live_alias_has_a_capture(self):
        names = {n for n, _ in ag.read_aliases(ALIASES)}
        stored = {f[:-7] for f in os.listdir(GOLDEN_DIR)
                  if f.endswith('.golden')}
        missing = {ag.safe_filename(n) for n in names} - stored
        self.assertFalse(missing, f'aliases with no capture: {sorted(missing)}')


class TestExpansion(unittest.TestCase):
    """Substitution rules, checked against what real tcsh does.

    These values were produced by running the equivalent aliases in tcsh, not
    derived from reading its manual.
    """

    def test_whole_arglist_forms(self):
        self.assertEqual(ag.expand(r'echo \!*', ['AA', 'BB']), 'echo AA BB')
        self.assertEqual(ag.expand(r'echo \!:*', ['AA', 'BB']), 'echo AA BB')

    def test_positional(self):
        self.assertEqual(ag.expand(r'echo \!:1', ['AA', 'BB']), 'echo AA')
        self.assertEqual(ag.expand(r'echo \!:2', ['AA', 'BB']), 'echo BB')

    def test_word_modifiers(self):
        self.assertEqual(ag.expand(r'echo \!:1:r', ['dir/f.txt']),
                         'echo dir/f')
        self.assertEqual(ag.expand(r'echo \!:1:t', ['dir/f.txt']),
                         'echo f.txt')

    def test_empty_arglist_is_not_an_error(self):
        """`\\!*` with no arguments expands to nothing and the command runs."""
        self.assertEqual(ag.expand(r'echo \!*', []).rstrip(), 'echo')

    def test_missing_positional_IS_an_error(self):
        """`\\!:1` with no argument fails, and that asymmetry is the point.

        This is the silent-failure class the whole migration exists to avoid:
        a bash translation of a `\\!:1` alias must reject a missing argument
        rather than pass an empty string, which is how `gcal solo ...` came to
        create nothing and report success.
        """
        self.assertEqual(ag.expand(r'echo \!:1', []), ag.BAD_SELECTOR)


class TestPinnedBehaviors(unittest.TestCase):
    """Specific captures whose shape the migration must not lose."""

    def capture(self, name):
        # Two different reasons to skip, and conflating them hides a real
        # failure: an absent fixture dir is not evidence an alias was retired.
        if not HAVE_CAPTURES:
            self.skipTest(NO_CAPTURES)
        p = os.path.join(GOLDEN_DIR, ag.safe_filename(name) + '.golden')
        if not os.path.exists(p):
            self.skipTest(f'{name} is no longer defined')
        with open(p) as f:
            return f.read()

    def test_redirection_alias_is_recorded_not_run(self):
        """`palias` appends to the alias file itself; it must never execute.

        An executing harness ran this and appended six lines to
        sh/aliases-public.sh. The capture records the text instead.
        """
        self.assertIn('>>', self.capture('palias'))

    def test_absolute_path_alias_is_recorded_not_run(self):
        """`htm2png` invokes Chrome by absolute path, which no stub PATH can
        intercept. An executing harness launched real headless Chrome."""
        self.assertIn('Chrome', self.capture('htm2png'))

    def test_alias_body_is_not_shadowed_by_its_own_name(self):
        """`spotify` must record what it runs, not its own name.

        With an executing harness, 46 alias names collided with generated
        stubs and captured `CMD <name>` instead of the real command.
        """
        cap = self.capture('spotify')
        self.assertIn('open', cap)
        self.assertNotIn('CMD spotify', cap)

    def test_chains_are_left_unresolved(self):
        """`pbdate` records `datestr| pbcopy`, naming what still needs
        translating rather than what it bottoms out in."""
        self.assertIn('datestr', self.capture('pbdate'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
