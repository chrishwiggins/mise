#!/opt/homebrew/bin/bash
#
# test-bounce-watch.sh -- regression tests for bash/bounce-watch.
#
# The paths verified by hand on 2026-09-07, when the tool was written after a
# message to a mistyped address bounced silently. These assert the CONTRACT
# without needing a mailbox: argument handling, the interrupt path, and that
# the tool refuses to run when its dependency is missing.
#
# The live-mailbox paths (a real bounce detected, the -r filter matching and
# not matching) are NOT covered here: they need a delivery failure sitting in
# a real account, which a test may not manufacture. Those were verified by
# hand against the 2026-09-07 notice.

set -uo pipefail

BW="$(dirname "$(realpath "$0")")/../bash/bounce-watch"
pass=0
fail=0

ok()   { printf '  ok   %s\n' "$1"; pass=$((pass + 1)); }
bad()  { printf '  FAIL %s\n' "$1"; fail=$((fail + 1)); }

echo "testing $BW"

# 1. It exists and is executable.
[[ -x "$BW" ]] && ok "executable" || { bad "not executable"; exit 1; }

# 2. Help exits 0 and describes the flags.
out=$("$BW" --help 2>&1)
[[ $? -eq 0 ]] && grep -q '\-r RECIPIENT' <<<"$out" \
    && ok "--help documents -r" || bad "--help missing or incomplete"

# 3. An unknown flag is rejected with EX_USAGE, not a silent pass. A bounce
#    checker that ignores a typo'd flag would watch the wrong account.
"$BW" --nonsense >/dev/null 2>&1
[[ $? -eq 64 ]] && ok "unknown flag exits 64" || bad "unknown flag did not exit 64"

# 4. It announces itself before blocking. Chris needs to see what Ctrl-C kills.
out=$(timeout 6 "$BW" -s 3 2>&1 </dev/null)
grep -q 'checking bounce' <<<"$out" \
    && ok "prints 'checking bounce'" || bad "no 'checking bounce' banner"

# 5. A clean window exits 0 and says nothing was found.
#    Budget is generous: each poll shells out to gmails, which costs several
#    seconds, so a nominal 3-second window takes ~20s of wall clock. Measured
#    2026-09-07. Do not tighten this without re-measuring.
out=$(timeout 60 "$BW" -s 3 2>&1 </dev/null); rc=$?
[[ $rc -eq 0 ]] && grep -q 'none in' <<<"$out" \
    && ok "clean window exits 0" || bad "clean window rc=$rc"

# 6. It does NOT claim delivery success. The window only catches hard
#    failures, and saying otherwise would be worse than saying nothing.
grep -qi 'soft one can still come later' <<<"$out" \
    && ok "hedges about soft failures" || bad "missing the soft-failure hedge"

# 7. SIGINT exits 130 and reassures that the message was still sent.
#    Driven through a pty: bash IGNORES SIGINT in a job started with &, so
#    backgrounding would test a path that does not exist interactively.
if command -v expect >/dev/null 2>&1; then
    out=$(/usr/bin/expect -c "
        set timeout 15
        spawn $BW -s 30
        expect \"checking bounce\"
        sleep 2
        send \x03
        expect eof
        catch wait result
        puts \"RC=[lindex \$result 3]\"" 2>&1)
    grep -q 'RC=130' <<<"$out" && ok "Ctrl-C exits 130" || bad "Ctrl-C rc wrong"
    grep -q 'was still sent' <<<"$out" \
        && ok "Ctrl-C reassures the message went" || bad "no reassurance on interrupt"
else
    echo "  skip expect-driven interrupt test (expect not installed)"
fi

# 8. Missing dependency is a hard error, not a silent all-clear. Reporting
#    "no bounce" because the checker could not look is the worst outcome.
out=$(PATH=/usr/bin:/bin HOME=/nonexistent "$BW" -s 2 2>&1 </dev/null); rc=$?
[[ $rc -ne 0 ]] && ok "missing gmails is fatal" \
    || bad "missing gmails exited 0 (would imply all-clear)"

echo
echo "$pass passed, $fail failed"
exit $(( fail > 0 ))
