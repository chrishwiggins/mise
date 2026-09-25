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
rm -rf "$tmp"
(( fail )) && exit 1
echo PASS
