#!/bin/bash
# bus-put: credential-word refusal happens BEFORE anything is written or copied,
# and a literal {N} in the body becomes the real bus number.
# Runs against a temp BUS_DIR; saves and restores the clipboard, which bus-put loads.
set -u
PUT=/Users/wiggins/mise/bash/bus-put
T=$(/usr/bin/mktemp -d)
export BUS_DIR="$T/bus"
/bin/mkdir -p "$BUS_DIR"
saved="$T/clip.saved"
/usr/bin/pbpaste > "$saved"
fail=0
ok()  { echo "ok   $1"; }
bad() { echo "FAIL $1"; fail=1; }

# 1. a body naming a credential word is refused with exit 3 and writes nothing
printf 'Log in.\nThe pwd is in a file.\n' > "$T/dirty.md"
"$PUT" dirty "$T/dirty.md" >/dev/null 2>"$T/err"
rc=$?
[[ $rc -eq 3 ]] && ok "dirty body exits 3" || bad "dirty body exit was $rc"
[[ -z "$(/bin/ls -A "$BUS_DIR")" ]] && ok "dirty body wrote no bus file" || bad "bus file written for dirty body"
/usr/bin/grep -q '^2:' "$T/err" && ok "offending line number reported" || bad "no line number on stderr"
/usr/bin/cmp -s "$saved" <(/usr/bin/pbpaste) && ok "clipboard untouched by refusal" || bad "refusal changed the clipboard"

# 2. a clean body posts, and {N} is filled with the number bus-put chose
printf 'Do the task.\nBegin your report with <bus {N} report>.\n' > "$T/clean.md"
out=$("$PUT" clean "$T/clean.md" 2>&1)
rc=$?
[[ $rc -eq 0 ]] && ok "clean body exits 0" || bad "clean body exit was $rc: $out"
f=$(/bin/ls "$BUS_DIR"/*-clean.md 2>/dev/null | /usr/bin/head -1)
if [[ -n "$f" ]]; then
    n=$(/usr/bin/basename "$f" | /usr/bin/cut -d- -f1)
    /usr/bin/grep -q "<bus $n report>" "$f" && ok "{N} became $n" || bad "{N} not substituted in $f"
    /usr/bin/grep -q '{N}' "$f" && bad "literal {N} survived" || ok "no literal {N} left"
else
    bad "no bus file written for clean body"
fi

/usr/bin/pbcopy < "$saved"
/bin/rm -rf "$T"
[[ $fail -eq 0 ]] && echo "PASS" || echo "FAILED"
exit $fail
