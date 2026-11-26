#!/bin/bash
# Hermetic test for py/weekday-lint: one mismatch, one correct, one quoted (ignored).
set -u
here="$(cd "$(dirname "$0")/.." && pwd)"
tmp="$(mktemp -d)"
cat > "$tmp/bad.eml" <<'EOF'
To: someone@example.edu
Subject: test

Please can we plan for September 12 for your talk? That's a Monday and works.
EOF
cat > "$tmp/good.eml" <<'EOF'
To: someone@example.edu
Subject: test

Would Wednesday, September 16, 11:40-12:55, work for your talk?
Also fine: this coming monday, Sep 14?

> On Mon, 07 Sep 2026, someone wrote: September 12 is a Monday (quoted, ignored)
EOF
fail=0
"$here/py/weekday-lint" --year 2026 "$tmp/bad.eml" >/dev/null && { echo "FAIL: bad.eml not flagged"; fail=1; }
"$here/py/weekday-lint" --year 2026 "$tmp/good.eml" >/dev/null || { echo "FAIL: good.eml flagged"; fail=1; }
# Yearless date across New Year: in late November, "Sat Jan 2" means the
# coming January (2027-01-02 is a Saturday; 2026-01-02 was a Friday).
cat > "$tmp/newyear.eml" <<'EOF'
To: someone@example.edu
Subject: test

- Sat Jan 2: they leave San Antonio at 12:52 PM to JFK.
EOF
cat > "$tmp/newyear-bad.eml" <<'EOF'
To: someone@example.edu
Subject: test

- Fri Jan 2: they leave San Antonio at 12:52 PM to JFK.
EOF
"$here/py/weekday-lint" --today 2026-11-21 "$tmp/newyear.eml" >/dev/null || { echo "FAIL: Jan 2 2027 flagged from November"; fail=1; }
"$here/py/weekday-lint" --today 2026-11-21 "$tmp/newyear-bad.eml" >/dev/null && { echo "FAIL: wrong weekday for Jan 2 2027 not flagged"; fail=1; }
rm -rf "$tmp"
(( fail )) && exit 1
echo PASS
