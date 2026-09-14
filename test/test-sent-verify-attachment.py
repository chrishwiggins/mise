#!/usr/bin/env python3.11
"""Regression test for sent-verify's attachment-promise detector.

A promise to attach is first person. Warning on "the detail you attached"
trains the reader to ignore the warning, which is worse than not having it:
the check exists to catch a lost -a flag on a message that really should
carry a file.

Caught 2026-09-13: a reply acknowledging someone else's attachment warned
that the -a flag had probably been lost, on a message never meant to have one.

Runs with no credentials and no side effects: python3.11 test-sent-verify-attachment.py
"""
import importlib.machinery
import importlib.util
import pathlib
import sys

TARGET = pathlib.Path(__file__).resolve().parent.parent / "py" / "sent-verify"

# The filename has a hyphen, so the usual import machinery will not take it.
loader = importlib.machinery.SourceFileLoader("sent_verify", str(TARGET))
spec = importlib.util.spec_from_loader("sent_verify", loader)
sv = importlib.util.module_from_spec(spec)
loader.exec_module(sv)

CASES = [
    # (text, promises_attachment)
    ("I have reviewed the salary and expense detail you attached for GG021038.", False),
    ("Please see the form she attached last week.", False),
    ("Per the attached that you sent, the numbers agree.", False),
    ("Thanks for the attachment you sent yesterday.", False),
    ("I have attached the achievements report.", True),
    ("Attaching the budget spreadsheet now.", True),
    ("The signed form is enclosed.", True),
    ("My report is attached.", True),
]


def main():
    failures = []
    for text, want in CASES:
        got = sv.promises_attachment(text)
        mark = "ok  " if got == want else "FAIL"
        print(f"  {mark} want={want!s:<5} got={got!s:<5} {text[:60]}")
        if got != want:
            failures.append(text)

    print()
    if failures:
        print(f"{len(failures)} failure(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"All {len(CASES)} attachment-promise cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
