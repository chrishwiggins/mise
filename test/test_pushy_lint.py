#!/usr/bin/env python3
"""Regression tests for /Users/wiggins/mise/py/pushy-lint.

Run: python3 /Users/wiggins/mise/test/test_pushy_lint.py

No credentials, no network, no side effects. Loads pushy-lint by path because
it has no .py extension.

The true positives here are the literal strings Chris edited out of a CPA
draft on 2026-08-27, paired with the replacements he wrote. The false
negatives matter just as much: his corrected phrasings must pass clean, or
the linter would flag the very sentences it is supposed to produce.
"""

import importlib.machinery
import importlib.util
import os
import sys
import tempfile

LINT = "/Users/wiggins/mise/py/pushy-lint"

spec = importlib.util.spec_from_loader(
    "pushy_lint", importlib.machinery.SourceFileLoader("pushy_lint", LINT)
)
pushy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pushy)

FAILURES = []


def check_text(body, as_eml=True):
    prefix = "To: x@example.com\nSubject: t\n\n" if as_eml else ""
    suffix = ".eml" if as_eml else ".md"
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(prefix + body)
        return pushy.check(path)
    finally:
        os.unlink(path)


def expect_flagged(label, body, kind=None):
    found = check_text(body)
    if not found:
        FAILURES.append("%s: expected a finding, got none" % label)
        return
    if kind and not any(kind in f[2] for f in found):
        FAILURES.append("%s: expected %r, got %r" % (label, kind, found))


def expect_clean(label, body):
    found = check_text(body)
    if found:
        FAILURES.append("%s: expected clean, got %r" % (label, found))


# --- true positives: the exact strings Chris cut on 2026-08-27 -------------

expect_flagged(
    "attribution as fact",
    "Matt told me on the 20th that it has to be in before 2026-10-15.",
    "attribution-as-fact")

expect_flagged(
    "demand heading",
    "What I need from you:",
    "demand-framing")

expect_flagged(
    "unanswered as their failure",
    "a year-designation issue I raised with Matt on Friday the 21st that has\n"
    "not been answered yet",
    "blame-framing")

expect_flagged(
    "as instructed points a finger",
    "If it belongs to 2023 as instructed, it was fine.",
    "finger-pointing")

expect_flagged(
    "preemptive phone offer",
    "I am glad to get on the phone if that is faster than email.",
    "preemptive-logistics")

# --- true positives: the same family, not from that draft -----------------

expect_flagged("counting silence", "Two days of silence now.", "counting-silence")
expect_flagged("heard back", "I still haven't heard back on this.", "counting-silence")
expect_flagged("as we discussed", "As we discussed on Friday, the form is due.",
               "finger-pointing")
expect_flagged("were you able to", "Were you able to file the extension?",
               "finger-pointing")
expect_flagged("manufactured urgency", "This is critical: I need the form today.",
               "manufactured-urgency")
expect_flagged("bare imperative ask", "Please send the signed form by Friday.",
               "demand-framing")
expect_flagged("i need you to", "I need you to confirm the designation.",
               "demand-framing")
expect_flagged("according to", "According to Louis, the contribution was for 2023.",
               "attribution-as-fact")

# --- false positives: Chris's own corrected phrasings must pass -----------

expect_clean(
    "hedged attribution",
    "My understanding from Matt's email on the 20th is that it has to be in\n"
    "before 2026-10-15.")

expect_clean(
    "hope framing",
    "What I'm hoping you can help me with:")

expect_clean(
    "shared open item",
    "a year-designation issue I raised with Matt on Friday the 21st that I\n"
    "don't think we've resolved")

expect_clean(
    "as intended",
    "If it belongs to 2023 as intended, it was fine.")

expect_clean(
    "softened ask",
    "Please can you confirm which tax year the contribution was credited to?")

expect_clean(
    "plain deadline statement",
    "The contribution has to be made before 2026-10-15.")

expect_clean(
    "owning the problem",
    "My SEP was misattributed when I asked Fidelity's team to make these.")

expect_clean(
    "ordinary prose",
    "Schedule C shows gross receipts of $40,700 and net profit of $33,766.")

# Quoted reply text is someone else's words; the rule does not apply.
expect_clean("quoted reply", "> What I need from you is the signed form.")

# Headers must be skipped in .eml files.
expect_clean("eml headers skipped", "Matt,\n\nThe form is attached.\n\nChris")


# --- report ---------------------------------------------------------------

if FAILURES:
    print("FAIL (%d):" % len(FAILURES))
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)
print("ok: all pushy-lint regression cases pass")
