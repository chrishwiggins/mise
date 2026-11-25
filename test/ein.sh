#!/opt/homebrew/bin/bash
# Hermetic test for mise/bash/ein: fake HOME registry, stub pbpaste.
EIN=${EIN:-$HOME/mise/bash/ein}
T=$(mktemp -d); pass=0; fail=0
mkdir -p "$T/home/.config/prj" "$T/proj/a/b" "$T/proj/sub/inner/x" "$T/bin" \
  "$T/git/d" "$T/nowhere"
git -C "$T/git" init -q
printf '{"foo":{"dir":"%s","color":"sage"},"gone":{"dir":"%s/nope"},"inner":{"dir":"%s"}}' \
  "$T/proj" "$T" "$T/proj/sub/inner" > "$T/home/.config/prj/projects.json"
printf '#!/bin/sh\nprintf "%%s" "$CLIP"\n' > "$T/bin/pbpaste"; chmod +x "$T/bin/pbpaste"
run() { HOME="$T/home" PATH="$T/bin:$PATH" CLIP="$1" "$EIN" "${@:2}"; }
check() { if [ "$1" = "$2" ]; then pass=$((pass+1)); echo "ok   $3"; else fail=$((fail+1)); echo "FAIL $3 (got $1 want $2)"; fi; }

run "https://example.org/a" foo >/dev/null; check $? 0 "known slug exits 0"
f=$(ls "$T/proj/ein" | head -1)
[[ "$f" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}h[0-9]{2}m[0-9]{2}s$ ]]; check $? 0 "datestr name ($f)"
check "$(cat "$T/proj/ein/$f")" "https://example.org/a" "content is clipboard"
run "second" foo >/dev/null; run "third" foo >/dev/null
check "$(ls "$T/proj/ein" | wc -l | tr -d ' ')" 3 "same-second writes do not overwrite"
run "x" bogus 2>/dev/null; check $? 1 "unknown slug exits 1"
run "x" gone 2>/dev/null; check $? 1 "missing project dir exits 1"
run "  " foo 2>/dev/null; check $? 1 "empty clipboard exits 1"
check "$(ls "$T/proj/ein" | wc -l | tr -d ' ')" 3 "failures wrote nothing"
(cd "$T/proj/a/b" && run "cwd" >/dev/null); check $? 0 "no slug in project subdir exits 0"
check "$(ls "$T/proj/ein" | wc -l | tr -d ' ')" 4 "no slug writes to containing project"
(cd "$T/proj/sub/inner/x" && run "nested" >/dev/null)
check "$(cat "$T/proj/sub/inner/ein/"* 2>/dev/null)" "nested" "deepest project wins"
check "$(ls "$T/proj/ein" | wc -l | tr -d ' ')" 4 "outer project untouched by nested"
(cd "$T/git/d" && run "repo" >/dev/null); check $? 0 "no slug in unregistered git repo exits 0"
check "$(cat "$T/git/ein/"* 2>/dev/null)" "repo" "falls back to git root"
(cd "$T/nowhere" && run "x" 2>/dev/null); check $? 1 "no slug outside project and repo exits 1"
check "$(ls "$T/nowhere" | wc -l | tr -d ' ')" 0 "outside: nothing written"
run "x" -h >/dev/null; check $? 0 "-h exits 0"

# Text after the slug replaces the clipboard.
mkdir -p "$T/t"
printf '{"t":{"dir":"%s"}}' "$T/t" > "$T/home/.config/prj/projects.json"
run "CLIPBOARD" t "summarize this thread" >/dev/null; check $? 0 "quoted prompt exits 0"
check "$(cat "$T/t/ein/"*)" "summarize this thread" "prompt text written, not clipboard"
rm -rf "$T/t/ein"
run "CLIPBOARD" t "https://example.org/x?a=1&b=2" >/dev/null
check "$(cat "$T/t/ein/"*)" "https://example.org/x?a=1&b=2" "URL written verbatim"
rm -rf "$T/t/ein"
run "CLIPBOARD" t look at this >/dev/null
check "$(cat "$T/t/ein/"*)" "look at this" "unquoted words joined with spaces"
rm -rf "$T/t/ein"
run "CLIPBOARD" t "   " 2>/dev/null; check $? 1 "whitespace text exits 1"
check "$(ls "$T/t/ein" 2>/dev/null | wc -l | tr -d ' ')" 0 "whitespace text wrote nothing"
run "CLIPBOARD" bogus "hello" 2>/dev/null; check $? 1 "text with unknown slug exits 1"

# prj -alias entries (_aliases) resolve; a real slug beats a same-named alias.
mkdir -p "$T/al" "$T/real"
printf '{"al":{"dir":"%s"},"real":{"dir":"%s"},"_aliases":{"AL":"al","real":"al","dead":"nope"}}' \
  "$T/al" "$T/real" > "$T/home/.config/prj/projects.json"
run "x" AL "via alias" >/dev/null; check $? 0 "alias exits 0"
check "$(cat "$T/al/ein/"* 2>/dev/null)" "via alias" "alias writes to target project"
run "x" real "direct" >/dev/null
check "$(cat "$T/real/ein/"* 2>/dev/null)" "direct" "real slug beats same-named alias"
run "x" dead "y" 2>/dev/null; check $? 1 "alias to unknown slug exits 1"
echo "$pass passed, $fail failed"; rm -rf "$T"; [ $fail -eq 0 ]
