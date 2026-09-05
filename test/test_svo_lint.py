#!/usr/bin/env python3
"""Regression tests for /Users/wiggins/mise/py/svo-lint.

Run: python3 /Users/wiggins/mise/test/test_svo_lint.py

No credentials, no network, no side effects. Loads svo-lint by path because
it has no .py extension.

The false-positive cases matter more than the true positives here. A linter
that flags correct prose stops being run, and then it protects nothing. The
"Advanced LAN Techs" case is real: it fired on a genuine CPA draft the first
time the linter ran, because an email body wraps at ~72 columns and the
company name happened to land at the start of a continuation line.
"""

import importlib.machinery
import importlib.util
import os
import sys
import tempfile

SVO = "/Users/wiggins/mise/py/svo-lint"

spec = importlib.util.spec_from_loader(
    "svo_lint", importlib.machinery.SourceFileLoader("svo_lint", SVO)
)
svo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(svo)

FAILURES = []


def check_text(body, as_eml=True):
    """Write body to a temp file and return svo-lint's findings."""
    prefix = "To: x@example.com\nSubject: t\n\n" if as_eml else ""
    suffix = ".eml" if as_eml else ".md"
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(prefix + body)
        return svo.check(path)
    finally:
        os.unlink(path)


def expect_flagged(label, body, kind=None):
    found = check_text(body)
    if not found:
        FAILURES.append("%s: expected a finding, got none" % label)
        return
    if kind and kind not in found[0][2]:
        FAILURES.append("%s: expected %r, got %r" % (label, kind, found[0][2]))


def expect_clean(label, body):
    found = check_text(body)
    if found:
        FAILURES.append("%s: expected clean, got %r" % (label, found))


# --- true positives: the three subjectless shapes -------------------------

expect_flagged("participial", "Sending it now rather than waiting.", "participial")
expect_flagged("participial/attaching", "Attaching the second copy.", "participial")
expect_flagged("irregular past", "Sent the invite yesterday.", "past-tense")
expect_flagged("regular past", "Queued your payment this morning.", "past-tense")
expect_flagged("predicative", "Happy to send it along.", "predicative")

# The exact sentence that shipped in a CPA draft on 2026-08-23 and that Chris
# caught by hand. This is the case the linter exists for.
expect_flagged(
    "the 2026-08-23 regression",
    "Sending it now rather than waiting, since it is an input to the 2025\n"
    "Schedule C and I would rather you not have to redo the SEP arithmetic.",
    "participial",
)

# --- false positives: prose that is correct and must not be flagged -------

expect_clean("explicit subject", "I am sending it now rather than waiting.")
expect_clean("explicit subject past", "I sent the invite yesterday.")
expect_clean("existential there", "There are three items left.")
expect_clean("subordinate opener", "Before I send this, one caveat.")
expect_clean("attached-is", "Attached is the form you asked for.")
expect_clean("determiner", "The statement balance is $128.54.")
expect_clean("demonstrative", "This is one payer, not the whole picture.")

# Proper nouns. A capitalized word followed by another capitalized word is a
# name, not a dropped-subject verb.
expect_clean("proper noun company", "Advanced LAN Techs paid $20,700.")
expect_clean(
    "proper noun wrapped",
    "One more document turned up today: a Form 1099-NEC from\n"
    "Advanced LAN Techs (EIN 27-0178436), issued through Gusto.",
)

# Hard-wrapped sentences must be joined before splitting, or every
# continuation line looks like a fresh sentence.
expect_clean(
    "line wrap mid-sentence",
    "I am sending it now rather than waiting, since it is an input to the\n"
    "2025 Schedule C and I would rather you not redo the arithmetic.",
)

# Structural lines are not sentences and the rule does not apply.
expect_clean("bullet", "- Sending the form tomorrow")
expect_clean("numbered item", "1. Sent the invite")
expect_clean("quoted reply", "> Sending it now rather than waiting.")
expect_clean("heading", "# Sending money abroad")

# Headers must be skipped in .eml files.
expect_clean("eml headers skipped", "Matt,\n\nI am sending the form.\n\nChris")


# --- report ---------------------------------------------------------------

if FAILURES:
    print("FAIL (%d):" % len(FAILURES))
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)
print("ok: all svo-lint regression cases pass")
