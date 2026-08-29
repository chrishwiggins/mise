#!/usr/bin/env python3
"""Regression tests for /Users/wiggins/mise/py/list-lint.

Run: python3 /Users/wiggins/mise/test/test_list_lint.py

No credentials, no network, no side effects.

The true positives are strings Chris actually rewrote into bullets. The false
positives matter just as much: his bulleted versions and ordinary two-item
prose must pass clean, or the linter cries wolf and stops being run.
"""

import importlib.machinery
import importlib.util
import os
import sys
import tempfile

LINT = "/Users/wiggins/mise/py/list-lint"

spec = importlib.util.spec_from_loader(
    "list_lint", importlib.machinery.SourceFileLoader("list_lint", LINT)
)
ll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ll)

FAILURES = []


def check_text(body, as_eml=True):
    prefix = "To: x@example.com\nSubject: t\n\n" if as_eml else ""
    suffix = ".eml" if as_eml else ".md"
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(prefix + body)
        return ll.check(path)
    finally:
        os.unlink(path)


def expect_flagged(label, body, rule=None, as_eml=True):
    found = check_text(body, as_eml)
    if not found:
        FAILURES.append("%s: expected a finding, got none" % label)
        return
    if rule and not any(rule == f[1] for f in found):
        FAILURES.append("%s: expected rule %r, got %r"
                        % (label, rule, [f[1] for f in found]))


def expect_clean(label, body, as_eml=True):
    found = check_text(body, as_eml)
    if found:
        FAILURES.append("%s: expected clean, got %r"
                        % (label, [(f[1], f[2]) for f in found]))


# --- true positives: the 2026-08-28 case Chris rewrote --------------------

expect_flagged(
    "the actual 2026-08-28 sentence",
    "The package has a federal 1040ES schedule: $0 for April and June, then\n"
    "$25,000 due September 15 and $25,000 due January 15, with the 2025\n"
    "overpayment covering the first two quarters.",
    "money-series")

expect_flagged(
    "three dollar amounts inline",
    "I paid $1,400 for prep, $25,000 in September and $25,000 in January.",
    "money-series")

expect_flagged(
    "three dates inline",
    "The deadlines are April 15, June 15 and September 15 this year.",
    "date-series")

expect_flagged(
    "classic X, Y, and Z noun series",
    "I need the statements, the voucher, and the signature page.",
    "comma-series")

expect_flagged(
    "series with or",
    "We can use Direct Pay, the Online Account, or a mailed check.",
    "comma-series")

# --- false positives: these must pass clean -------------------------------

expect_clean(
    "Chris's bulleted rewrite",
    "The package has a federal 1040ES schedule:\n"
    "  - $0 for April and June, then\n"
    "- $25,000 due September 15 and\n"
    "  - $25,000 due January 15,\n"
    "with the 2025 overpayment covering the first two quarters.")

expect_clean(
    "numbered list",
    "Three questions:\n"
    "1. Can the designations be corrected?\n"
    "2. Does that disturb the filed return?\n"
    "3. Should I fund it at all?")

expect_clean(
    "two dollar amounts is not a list",
    "The fee was $1,400 and the payment is $25,000.")

expect_clean(
    "two items joined by and",
    "I need the voucher and the signature page.")

expect_clean(
    "one date one amount",
    "The $25,000 payment is due September 15.")

expect_clean(
    "prose with a single comma",
    "Before I sign the authorizations, I want to resolve the designation.")

expect_clean(
    "quoted reply text is someone else's",
    "> I paid $1,400 for prep, $25,000 in September and $25,000 in January.")

expect_clean(
    "eml headers are skipped",
    "Hi Lou,\n\nOne question about the return.\n\nChris")

# A delivered .eml carries Received:/DKIM headers with many dates in folded
# continuation lines; those must not be parsed as body text.
DELIVERED = (
    "Return-Path: <x@example.com>\n"
    "Received: from mail.example.com (mail.example.com [10.0.0.1])\n"
    "        by mx.example.com with SMTPS id abc123\n"
    "        for <y@example.com>; Fri, 28 Aug 2026 21:54:17 -0400 (EDT)\n"
    "ARC-Seal: i=1; a=rsa-sha256; t=1756432457; cv=none\n"
    "Date: Fri, 28 Aug 2026 21:54:17 -0400\n"
    "Subject: t\n"
    "\n"
    "Hi Lou,\n\nOne question about the return.\n\nChris\n")
fd, path = tempfile.mkstemp(suffix=".eml")
with os.fdopen(fd, "w") as fh:
    fh.write(DELIVERED)
try:
    found = ll.check(path)
    if found:
        FAILURES.append("delivered eml headers: expected clean, got %r"
                        % [(f[1], f[2]) for f in found])
finally:
    os.unlink(path)


# --- report ---------------------------------------------------------------

if FAILURES:
    print("FAIL (%d):" % len(FAILURES))
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)
print("ok: all list-lint regression cases pass")
