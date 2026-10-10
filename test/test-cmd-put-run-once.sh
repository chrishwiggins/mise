#!/bin/bash
# cmd-put: a staged script runs once; a second run is refused (exit 3) unless FORCE=1.
set -u
T=$(mktemp -d)
export CMD_DIR=$T/cmd CMD_DOC_DIR=$T/doc CMD_OUT_DIR=$T/out
fail=0
printf 'echo hello-from-body\n' > "$T/body.sh"
script=$(/Users/wiggins/mise/bash/cmd-put once-test "$T/body.sh" | /usr/bin/awk '/^run it:/{print $NF}')

out1=$(bash "$script" 2>&1); rc1=$?
[ $rc1 = 0 ] && echo "$out1" | /usr/bin/grep -q hello-from-body || { echo "FAIL first run rc=$rc1: $out1"; fail=1; }

out2=$(bash "$script" 2>&1); rc2=$?
[ $rc2 = 3 ] && echo "$out2" | /usr/bin/grep -q REFUSED || { echo "FAIL second run not refused rc=$rc2: $out2"; fail=1; }
echo "$out2" | /usr/bin/grep -q hello-from-body && { echo "FAIL second run executed the body"; fail=1; }

out3=$(FORCE=1 bash "$script" 2>&1); rc3=$?
[ $rc3 = 0 ] && echo "$out3" | /usr/bin/grep -q hello-from-body || { echo "FAIL FORCE=1 run rc=$rc3: $out3"; fail=1; }

n=$(/usr/bin/grep -c '^=== start' "$CMD_OUT_DIR"/1-once-test.out)
[ "$n" = 2 ] || { echo "FAIL expected 2 start lines in receipt, got $n"; fail=1; }

/bin/rm -rf "$T"
[ $fail = 0 ] && echo "PASS test-cmd-put-run-once" || exit 1
