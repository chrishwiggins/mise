#!/bin/bash
# chrome-shadow: fails exactly when AppleScript's "Google Chrome" is a different instance
# than the real one, whatever the launch order. Hermetic: the process listing and both
# window counts come from the helper's CHROME_SHADOW_* overrides, so no Chrome is touched.
#
# Background, 2026-10-06: a calendar launcher said its Outlook tab never appeared (and
# blamed a signed-out profile) while the real Chrome was signed in. A Playwright Chrome was answering AppleScript. The
# first helper assumed the earliest-launched instance answers; once Playwright exited, a
# hung headless Chrome launched AFTER the real one answered instead and that helper
# exited 0. Case "headless launched later" is the regression for that.
set -u
H=/Users/wiggins/mise/bash/chrome-shadow
fail=0
ok()  { echo "ok   $1"; }
bad() { echo "FAIL $1"; fail=1; }
APP='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
REAL="28073 $APP --profile-directory=Profile 9"
PW="97548 $APP --disable-field-trial-config --user-data-dir=/x/ms-playwright-mcp/c --remote-debugging-pipe"
HL="38814 $APP --headless=new --user-data-dir=/tmp/h/profile --dump-dom http://127.0.0.1/x.html"
HELPER="20001 $APP Helper --type=renderer"

run() {   # name expect_exit ps byname real
  local out rc
  out=$(CHROME_SHADOW_PS="$3" CHROME_SHADOW_BYNAME="$4" CHROME_SHADOW_REAL="$5" "$H" 2>&1); rc=$?
  if [ "$rc" = "$2" ]; then ok "$1"; else bad "$1 (exit $rc, want $2): $out"; fi
  LAST="$out"
}

run "no Chrome running"                      0 "1 /bin/zsh"              ""  ""
run "only the real Chrome"                   0 "$REAL"$'\n'"$HELPER"     2   2
run "Playwright running, AppleScript fine"   0 "$PW"$'\n'"$REAL"         2   2
run "Playwright answering (launched first)"  1 "$PW"$'\n'"$REAL"         0   2
case "$LAST" in *"kill 97548"*) ok "  names the Playwright pid";; *) bad "  names the Playwright pid: $LAST";; esac
run "headless launched later, answering"     1 "$REAL"$'\n'"$HL"         0   2
case "$LAST" in *"kill 38814"*) ok "  names the headless pid";; *) bad "  names the headless pid: $LAST";; esac
run "only automation Chromes"                1 "$PW"                     0   ""
run "helper processes are not instances"     0 "$REAL"$'\n'"$HELPER"     0   0

[ "$fail" = 0 ] && echo "all passed" || echo "FAILURES"
exit $fail
