#!/bin/bash
# cfg-history must snapshot ~/.claude/settings.json, not only the markdown.
#
# That file wires every hook, and until 2026-10-11 the tracked_files glob was
# top-level '*.md' only, so it was never captured: the snapshot repo held 376
# files including CLAUDE.md and 55 hook scripts while `git status` there
# reported `?? settings.json`. CLAUDE.md names cfg-history as the recovery
# route for clobbered shared config, so the one file with no history was the
# one most worth having. A future edit to that glob must not silently drop it
# again, which is what this test is for.
#
# Hermetic: builds its own tree and snapshot repo under a temp dir and points
# cfg-history at them with CFG_HISTORY_TREE / CFG_HISTORY_GIT, so the real
# ~/.claude and ~/.claude-history.git are never touched.

set -uo pipefail

CFG="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/bash/cfg-history"
PASS=0; FAIL=0
check() {  # check <name> <expected> <actual>
    if [[ "$2" == "$3" ]]; then echo "  ok    $1"; PASS=$((PASS+1))
    else echo "  FAIL  $1"; echo "        expected: $2"; echo "        actual:   $3"; FAIL=$((FAIL+1)); fi
}

[[ -x "$CFG" ]] || { echo "cfg-history not executable at $CFG"; exit 1; }

SBOX="$(/usr/bin/mktemp -d)"
trap '/bin/rm -rf "$SBOX"' EXIT
TREE="$SBOX/claude"; GITD="$SBOX/hist.git"
/bin/mkdir -p "$TREE/hooks" "$TREE/commands"

# A tree shaped like the real one: markdown, a hook, and the settings files.
echo "# claude md" > "$TREE/CLAUDE.md"
echo "#!/bin/bash" > "$TREE/hooks/some-hook.sh"
printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"/x/y.sh"}]}]}}\n' \
    > "$TREE/settings.json"
printf '{"permissions":{"allow":["Bash(ls:*)"]}}\n' > "$TREE/settings.local.json"

echo "cfg-history captures the settings files"
CFG_HISTORY_TREE="$TREE" CFG_HISTORY_GIT="$GITD" "$CFG" snapshot >/dev/null 2>&1

g() { /usr/bin/git --git-dir="$GITD" --work-tree="$TREE" "$@"; }

check "settings.json is tracked" "1" "$(g ls-files | /usr/bin/grep -cx 'settings.json')"
check "settings.local.json is tracked" "1" "$(g ls-files | /usr/bin/grep -cx 'settings.local.json')"
check "markdown is still tracked" "1" "$(g ls-files | /usr/bin/grep -cx 'CLAUDE.md')"
check "hooks are still tracked" "1" "$(g ls-files | /usr/bin/grep -cx 'hooks/some-hook.sh')"

# The point of a snapshot is reading the file back out of it.
check "settings.json round-trips as valid JSON with its hook" "/x/y.sh" \
      "$(g show HEAD:settings.json | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d["hooks"]["PreToolUse"][0]["hooks"][0]["command"])' 2>/dev/null)"

# A later edit must be captured too, since one snapshot proves little.
printf '{"hooks":{"PreToolUse":[]},"fileCheckpointingEnabled":false}\n' > "$TREE/settings.json"
CFG_HISTORY_TREE="$TREE" CFG_HISTORY_GIT="$GITD" "$CFG" snapshot >/dev/null 2>&1
check "a later change to settings.json is snapshotted" "False" \
      "$(g show HEAD:settings.json | python3 -c 'import json,sys; print(json.load(sys.stdin).get("fileCheckpointingEnabled"))' 2>/dev/null)"

echo
if [[ $FAIL -eq 0 ]]; then echo "all $PASS checks passed"; else echo "$FAIL of $((PASS+FAIL)) checks FAILED"; fi
exit "$FAIL"
