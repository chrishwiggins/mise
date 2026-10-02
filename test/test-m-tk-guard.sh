#!/bin/bash
# Test the TK-placeholder filter that m applies to a draft before dispatch.
# Runs the same awk/grep pipeline m uses on fixture drafts; no mail is sent.
# Positive case: the 2026-10-01 incident line. Negative cases: quoted TK,
# TK only in headers, and ordinary words containing "tk".
set -u
filter() {
  /usr/bin/awk 'NR>1 && /^$/ && !body {body=1; next} body && !/^>/' "$1" \
    | /usr/bin/grep -n -E '(^|[^A-Za-z])TK([^A-Za-z]|$)|\[[tT][kK]\]' | /usr/bin/head -5
}
d=$(/usr/bin/mktemp -d)
fail=0
printf 'To: a\nSubject: x\n\nHi,\n\nTK: RULING. Pick one block below and delete the rest of this block.\n\nBest\n' > "$d/hit.eml"
printf 'To: a\nSubject: x\n\nHi [tk] here\n' > "$d/hit2.eml"
printf 'To: a\nSubject: TK note\n\nHi,\n\n> TK in a quote\n\nBest\n' > "$d/miss.eml"
printf 'To: a\nSubject: x\n\nThe Atkins diet and an outkick, and Tkachenko.\n' > "$d/miss2.eml"
for f in hit hit2; do [ -n "$(filter "$d/$f.eml")" ] || { echo "FAIL: $f not caught"; fail=1; }; done
for f in miss miss2; do [ -z "$(filter "$d/$f.eml")" ] || { echo "FAIL: $f falsely caught: $(filter "$d/$f.eml")"; fail=1; }; done
# The incident draft itself, as sent, must be caught.
inc=/Users/wiggins/gd/local/Science/Advising/Groups/eml/sent/2026-10-01-kk3876-stats-and-ml-sequence.eml
[ -f "$inc" ] && { [ -n "$(filter "$inc")" ] || { echo "FAIL: incident draft not caught"; fail=1; }; }
/bin/rm -rf "$d"
[ $fail -eq 0 ] && echo "PASS: TK guard catches 3 positives, passes 2 negatives"
exit $fail
