#!/usr/bin/env python3.11
"""Regression tests for gcal-solo's account selection.

These run offline: no network, no credentials, no events created. The module is
loaded by importlib because gcal-solo has no .py extension.

Guards two behaviors that were built on 2026-09-18 (mise bc60b1d):

1. token_name_for follows gcal-invite's convention, so both tools resolve an
   account to the same token file.
2. -A chris.wiggins@gmail.com reuses the bare calendar.pickle default. There has
   never been a calendar-chris-wiggins-at-gmail-com.pickle, so without this the
   flag hangs on an interactive OAuth flow for a token that cannot be found.
"""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

GCAL_SOLO = Path.home() / "mise/py/gcal-solo"


def load_gcal_solo():
    """Import gcal-solo (extensionless) without running its __main__ block."""
    sys.path.insert(0, str(Path.home() / "mise/py"))
    spec = importlib.util.spec_from_loader(
        "gcal_solo_under_test",
        importlib.machinery.SourceFileLoader("gcal_solo_under_test", str(GCAL_SOLO)),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTokenNaming(unittest.TestCase):
    def setUp(self):
        self.m = load_gcal_solo()

    def test_columbia_token_name(self):
        self.assertEqual(
            self.m.token_name_for("chw2@columbia.edu"),
            "calendar-chw2-at-columbia-edu",
        )

    def test_hackny_token_name(self):
        self.assertEqual(
            self.m.token_name_for("chris@hackny.org"),
            "calendar-chris-at-hackny-org",
        )

    def test_matches_gcal_invite_convention(self):
        # gcal-invite builds the same stem; if these drift, the two tools
        # authorize separate tokens for one account and each re-runs OAuth.
        account = "chris@hackny.org"
        expected = f"calendar-{account.replace('@', '-at-').replace('.', '-')}"
        self.assertEqual(self.m.token_name_for(account), expected)


class TestDefaultAccountAliasing(unittest.TestCase):
    """The bug this file exists for: -A <default account> must not re-auth."""

    def setUp(self):
        self.m = load_gcal_solo()

    def _creds_kwargs_for(self, account):
        with mock.patch.object(self.m, "get_credentials") as gc, \
             mock.patch.object(self.m, "build") as build:
            build.return_value = object()
            self.m.get_authenticated_service(account)
            self.assertTrue(gc.called, "get_credentials was never called")
            return gc.call_args.kwargs

    def test_default_account_uses_bare_token(self):
        kwargs = self._creds_kwargs_for(self.m.DEFAULT_TOKEN_ACCOUNT)
        self.assertNotIn("token_name", kwargs)
        self.assertNotIn("login_hint", kwargs)

    def test_no_account_uses_bare_token(self):
        kwargs = self._creds_kwargs_for(None)
        self.assertNotIn("token_name", kwargs)

    def test_other_account_gets_its_own_token(self):
        kwargs = self._creds_kwargs_for("chw2@columbia.edu")
        self.assertEqual(kwargs["token_name"], "calendar-chw2-at-columbia-edu")
        self.assertEqual(kwargs["login_hint"], "chw2@columbia.edu")

    def test_default_account_constant_is_an_address(self):
        self.assertEqual(self.m.DEFAULT_TOKEN_ACCOUNT.count("@"), 1)


class TestListAccounts(unittest.TestCase):
    def setUp(self):
        self.m = load_gcal_solo()

    def test_lists_default_and_named_tokens(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            token_dir = Path(tmp)
            (token_dir / "calendar.pickle").touch()
            (token_dir / "calendar-chw2-at-columbia-edu.pickle").touch()
            (token_dir / "calendar-chris-at-hackny-org.pickle").touch()
            (token_dir / "gmail-chw2-at-columbia-edu.pickle").touch()  # wrong service
            with mock.patch.object(self.m, "TOKEN_DIR", token_dir):
                accounts = self.m.list_accounts()

        self.assertIn(self.m.DEFAULT_TOKEN_ACCOUNT, accounts)
        self.assertIn("chw2@columbia.edu", accounts)
        self.assertIn("chris@hackny.org", accounts)
        self.assertEqual(len(accounts), 3, f"gmail token leaked in: {accounts}")

    def test_no_default_listed_when_bare_token_absent(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            token_dir = Path(tmp)
            (token_dir / "calendar-chw2-at-columbia-edu.pickle").touch()
            with mock.patch.object(self.m, "TOKEN_DIR", token_dir):
                accounts = self.m.list_accounts()

        self.assertEqual(accounts, ["chw2@columbia.edu"])

    def test_missing_token_dir_is_not_an_error(self):
        with mock.patch.object(self.m, "TOKEN_DIR", Path("/nonexistent/xyzzy")):
            self.assertEqual(self.m.list_accounts(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
