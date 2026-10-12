#!/bin/bash
# cfg-history must not lose a snapshot to git's index lock, and must not grow
# its cron log without bound.
#
# A snapshot takes the index lock once per tracked file, so a cron run that
# overlaps a manual one used to lose the race and drop the ENTIRE snapshot:
# ~/.claude-history.log held 3221 "Another git process seems to be running"
# lines with real gaps in the series on a five-minute cron. Since cfg-history
# is the only history for ~/.claude/settings.json, a dropped snapshot is a lost
# version of the file that wires every hook.
#
# Hermetic: its own tree, snapshot repo and log under a temp dir, pointed at by
# CFG_HISTORY_TREE / CFG_HISTORY_GIT / CFG_HISTORY_LOG, so the live config,
# the real history repo and the real log are never touched.

set -uo pipefail

CFG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bash/cfg-history"
PASS=0; FAIL=0
check() {
    if [[ "$2" == "$3" ]]; then echo "  ok    $1"; PASS=$((PASS+1))
    else echo "  FAIL  $1"; echo "        expected: $2"; echo "        actual:   $3"; FAIL=$((FAIL+1)); fi
}

[[ -x "$CFG" ]] || { echo "cfg-history not executable at $CFG"; exit 1; }

SBOX="$(/usr/bin/mktemp -d)"
trap '/bin/rm -rf "$SBOX"' EXIT
TREE="$SBOX/claude"; GITD="$SBOX/hist.git"; LOG="$SBOX/hist.log"
/bin/mkdir -p "$TREE"
echo "# md" > "$TREE/CLAUDE.md"
printf '{"hooks":{}}\n' > "$TREE/settings.json"

run() { CFG_HISTORY_TREE="$TREE" CFG_HISTORY_GIT="$GITD" CFG_HISTORY_LOG="$LOG" "$CFG" "$@"; }
g() { /usr/bin/git --git-dir="$GITD" --work-tree="$TREE" "$@"; }

echo "cfg-history survives a held lock"
run snapshot >/dev/null 2>&1
base=$(g rev-list --count HEAD 2>/dev/null || echo 0)
check "a first snapshot commits" "1" "$base"

# Hold the lock the way a concurrent run would, then snapshot a real change.
/bin/mkdir -p "$GITD.snapshot.lock"
printf '{"hooks":{"Stop":[]}}\n' > "$TREE/settings.json"
CFG_HISTORY_TREE="$TREE" CFG_HISTORY_GIT="$GITD" CFG_HISTORY_LOG="$LOG" \
  CFG_HISTORY_STALE_LOCK=9999 "$CFG" snapshot >/dev/null 2>&1
rc=$?
check "a blocked run exits 0 rather than erroring" "0" "$rc"
check "a blocked run commits nothing" "$base" "$(g rev-list --count HEAD)"
/bin/rm -rf "$GITD.snapshot.lock"

# With the lock free, the same change must be captured, so nothing is lost.
run snapshot >/dev/null 2>&1
check "the change is captured once the lock clears" "$((base + 1))" "$(g rev-list --count HEAD)"
check "and its content is the new one" "Stop" \
      "$(g show HEAD:settings.json | python3 -c 'import json,sys; print(",".join(json.load(sys.stdin)["hooks"]))' 2>/dev/null)"

# A lock left by a crashed run must not block forever.
/bin/mkdir -p "$GITD.snapshot.lock"
/usr/bin/touch -t 202001010000 "$GITD.snapshot.lock"
printf '{"hooks":{"Notification":[]}}\n' > "$TREE/settings.json"
before=$(g rev-list --count HEAD)
run snapshot >/dev/null 2>&1
check "a stale lock is broken and the snapshot proceeds" "$((before + 1))" "$(g rev-list --count HEAD)"

echo
echo "cfg-history caps its cron log"
/usr/bin/head -c 400000 /dev/zero | /usr/bin/tr '\0' 'x' > "$LOG"
CFG_HISTORY_TREE="$TREE" CFG_HISTORY_GIT="$GITD" CFG_HISTORY_LOG="$LOG" \
  CFG_HISTORY_LOG_MAX=1024 "$CFG" snapshot >/dev/null 2>&1
sz=$(/usr/bin/stat -f %z "$LOG")
check "an oversized log is trimmed" "yes" "$([ "$sz" -le 2048 ] && echo yes || echo no)"

echo
if [[ $FAIL -eq 0 ]]; then echo "all $PASS checks passed"; else echo "$FAIL of $((PASS+FAIL)) checks FAILED"; fi
exit "$FAIL"
