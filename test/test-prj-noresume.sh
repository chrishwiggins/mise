#!/bin/bash
# prj -ls marks the session prj would auto-resume; ids listed in
# ~/.config/prj/noresume are passed over. Hermetic: HOME is a temp dir.
# Also checks _find_latest_session, which launch uses, against the same data.
set -u
PRJ=${PRJ:-$(cd "$(dirname "$0")/.." && pwd)/bash/prj}
BASH4=/opt/homebrew/bin/bash
H=$(mktemp -d /tmp/prj-noresume-XXXXXX)
fails=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: want '$2' got '$3'"; fails=$((fails + 1)); fi; }

mkdir -p "$H/.config/prj" "$H/work" "$H/lib"
dir=$H/work
sdir=$H/.claude/projects/$(echo "$dir" | sed 's|[^a-zA-Z0-9]|-|g')
mkdir -p "$sdir"
echo "{\"t\": {\"dir\": \"$dir\", \"color\": \"sage\"}}" > "$H/.config/prj/projects.json"
echo '{"type":"user"}' > "$sdir/older.jsonl"
echo '{"type":"user"}' > "$sdir/newer.jsonl"
touch -t 202601010000 "$sdir/older.jsonl"
touch -t 202601020000 "$sdir/newer.jsonl"

{
    echo 'CLAUDE_PROJECTS="$HOME/.claude/projects"'
    echo 'PRJ_NORESUME="$HOME/.config/prj/noresume"'
    sed -n '/^_mangle_path() {/,/^}/p; /^_find_latest_session() {/,/^}/p' "$PRJ"
} > "$H/lib/fn.sh"
latest() { HOME=$H "$BASH4" -c '. "$HOME/lib/fn.sh"; _find_latest_session "$HOME/work"'; }
marked() { HOME=$H "$BASH4" "$PRJ" -ls t | awk '$1 == "*" && $2 != "=" {print $2}'; }

check "no list: launch picks newest" newer "$(latest)"
check "no list: -ls marks newest" newer "$(marked)"
echo newer > "$H/.config/prj/noresume"
check "listed: launch skips it" older "$(latest)"
check "listed: -ls marks the next" older "$(marked)"
printf 'newer\nolder\n' > "$H/.config/prj/noresume"
check "all listed: launch finds none" "" "$(latest)"
check "all listed: -ls marks none" "" "$(marked)"
echo new > "$H/.config/prj/noresume"
check "partial id does not match" newer "$(latest)"
echo newer > "$H/.config/prj/noresume"
check "skip is reported on stderr" 1 "$(latest 2>&1 >/dev/null | grep -c 'not resuming newer')"
check "-ls flags the listed id" newer "$(HOME=$H "$BASH4" "$PRJ" -ls t | awk '$1 == "-" && $2 != "=" {print $2}')"

/bin/rm -rf "$H"
echo "$fails failure(s)"
[ "$fails" -eq 0 ]
