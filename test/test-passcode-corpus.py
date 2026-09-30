#!/usr/bin/env python3.11
"""Run passcode_extract over a private labeled corpus.

The corpus is $PASSCODE_CORPUS: dat/eml/*.eml plus dat/labels.tsv with columns
filename, code, account. A code of "x" or empty means the message holds no
passcode and the extractor must return none. Exits 2 with a warning when
$PASSCODE_CORPUS is unset, since a silent 0 would read as a passing corpus.

Run: PASSCODE_CORPUS=/path/to/corpus python3.11 test/test-passcode-corpus.py
"""

import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "py"))
from passcode_extract import extract  # noqa: E402


def main():
    root = os.environ.get("PASSCODE_CORPUS")
    if not root:
        print("⚠️  PASSCODE_CORPUS is unset; no corpus tested.", file=sys.stderr)
        return 2
    root = Path(root)
    labels = root / "dat" / "labels.tsv"
    rows = list(csv.DictReader(labels.open(newline=""), delimiter="\t"))
    if not rows:
        print(f"⚠️  {labels} has no rows; nothing tested.", file=sys.stderr)
        return 2
    fails = 0
    for row in rows:
        want = (row.get("code") or "").strip()
        want = None if want in ("", "x") else want
        path = root / "dat" / "eml" / row["filename"]
        try:
            r = extract(path.read_bytes())
        except OSError as e:
            print(f"  FAIL {row['filename']}: {e}")
            fails += 1
            continue
        ok = r.code == want
        print(f"  {'ok  ' if ok else 'FAIL'} {row['filename']}: want {want!r}, "
              f"got {r.code!r} ({r.rule}; candidates {r.candidates})")
        fails += not ok
    print(f"\n{len(rows) - fails}/{len(rows)} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
