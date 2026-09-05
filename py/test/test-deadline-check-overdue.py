#!/usr/bin/env python3
"""Regression tests for deadline-check's date detection.

Written 2026-08-21 after the tool printed "Nothing in doc/NEXT.md is
dated within 48h" while three items in that file were already past due:
a held email (3 days over), a bank check nobody had looked at (1 day
over), and a state-filing chase (14 days over). Chris found the last one
himself, from memory, which is exactly the job this tool exists to do.

Three separate defects combined to produce that clean all-clear:

1. The window was forward-only (`today <= d <= horizon`), so anything
   already overdue was discarded. Overdue is more urgent, not less.
2. `dates_in` used `.search()`, taking only the FIRST date on a line, so
   "asked 2026-08-07, due 2026-08-19" hid the deadline behind the
   earlier date.
3. `item_lines` returned only the first PHYSICAL line of each item.
   These files are hard-wrapped, so most deadlines sit on continuation
   lines and were invisible.

Run: python3 /Users/wiggins/mise/py/test/test-deadline-check-overdue.py
"""

import os
import subprocess
import sys
import tempfile

TOOL = "/Users/wiggins/mise/py/deadline-check"
TODAY = "2026-08-21"


def run(body, *args):
    """Run deadline-check against a temp NEXT.md; return (exit_code, stdout)."""
    d = tempfile.mkdtemp()
    path = os.path.join(d, "NEXT.md")
    with open(path, "w") as fh:
        fh.write(body)
    r = subprocess.run(
        [TOOL, "--file", path, "--today", TODAY, *args],
        capture_output=True,
        text=True,
    )
    return r.returncode, r.stdout


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f"  {detail}" if detail and not cond else ""))
    return bool(cond)


def main():
    ok = True

    # 1. The original failure: a deadline on a wrapped continuation line.
    body = (
        "# NEXT\n\nUpdated 2026-08-21.\n\n"
        "1. Send the held Eric sanity-check on the DBL cancellation,\n"
        "   due 2026-08-18 and still unsent: eml/drafts/eric-dbl.eml\n"
    )
    code, out = run(body)
    ok &= check("wrapped continuation date is seen", code == 2 and "OVERDUE" in out, out)

    # 2. Overdue items must not be silently dropped.
    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Thing due 2026-08-18.\n")
    ok &= check("past-due item exits 2", code == 2 and "OVERDUE by 3 days" in out, out)

    # 3. Upcoming detection must still work (no regression).
    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Call on 2026-08-22.\n")
    ok &= check("tomorrow still detected", code == 2 and "TOMORROW" in out, out)

    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Call on 2026-08-21.\n")
    ok &= check("today still detected", code == 2 and "TODAY" in out, out)

    # 4. Multiple dates on one line: the later deadline must not be hidden.
    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Asked 2026-08-07, due 2026-08-19.\n")
    ok &= check("second date on a line is seen", code == 2 and "OVERDUE" in out, out)

    # 5. A long-dead date quoted in passing must stay quiet, or every old
    #    reference in prose would re-alarm forever.
    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Mentioning 2025-01-01 in passing.\n")
    ok &= check("ancient date stays quiet", code == 0 and "Nothing" in out, out)

    # 6. The lookback window is tunable and actually bounds the search.
    code, out = run(
        "# NEXT\n\nUpdated 2026-08-21.\n\n1. Thing due 2026-08-01.\n",
        "--overdue-days",
        "5",
    )
    ok &= check("--overdue-days bounds the lookback", code == 0, out)

    code, out = run(
        "# NEXT\n\nUpdated 2026-08-21.\n\n1. Thing due 2026-08-01.\n",
        "--overdue-days",
        "60",
    )
    ok &= check("--overdue-days widens the lookback", code == 2 and "OVERDUE" in out, out)

    # 7. A genuinely empty list stays silent and exits 0.
    code, out = run("# NEXT\n\nUpdated 2026-08-21.\n\n1. Something with no date at all.\n")
    ok &= check("undated item is not a deadline", code == 0, out)

    print("\nOK" if ok else "\nFAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
