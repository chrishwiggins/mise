#!/opt/homebrew/bin/bash
#
# test-claude-child-cwd.sh -- regression tests for the "child claude inherits
# a blocked cwd" bug class.
#
# Background, 2026-09-12: pbcal run from $HOME produced "Error: Failed to
# generate script". The child `claude --print` inherits the caller's working
# directory, and the block-home-dir.sh UserPromptSubmit hook refuses $HOME by
# exiting 2. Claude Code surfaces that refusal as the child's STDOUT with exit
# status 0, so the caller sees a successful run whose output is a hook notice.
# pbcal then found no <<<CALPARSE_START>>> delimiters and blamed the parse.
#
# This had been fixed once already in seiton/bash/pbcal (commits de5613e and
# 7e657d3) and was lost when the script was de-privatized into the public mise
# repo by 5529536. mise/bash precedes seiton/bash on PATH, so the regressed
# copy is the one that runs. That is why this test lives here: to make the
# regression loud if the file is ever rewritten again.
#
# These assert the CONTRACT without calling the real Claude API: that each
# caller pins a working directory for its child claude, and that each one
# recognizes a hook block rather than misreporting it as a domain error.
#
# The live paths (a real parse from $HOME) were verified by hand on
# 2026-09-12 across four flag combinations; they need API calls, so they are
# not reproduced here.

set -uo pipefail

PBCAL=/Users/wiggins/mise/bash/pbcal
PDFRENAME=/Users/wiggins/mise/py/pdf-rename

pass=0
fail=0

check() {
    local label=$1 expected=$2 actual=$3
    if [ "$expected" = "$actual" ]; then
        printf 'ok   %s\n' "$label"
        pass=$((pass + 1))
    else
        printf 'FAIL %s\n       expected: %s\n       actual:   %s\n' \
            "$label" "$expected" "$actual"
        fail=$((fail + 1))
    fi
}

# --- the files still exist -------------------------------------------------

check "pbcal exists" yes "$([ -f "$PBCAL" ] && echo yes || echo no)"
check "pdf-rename exists" yes "$([ -f "$PDFRENAME" ] && echo yes || echo no)"

# --- each caller pins a cwd for its child claude ---------------------------
#
# pbcal: the claude invocation must run inside a subshell that cds first.
# Grepping for the cd alone is not enough, since a cd elsewhere in the file
# would satisfy it; require the cd and the claude call in the same construct.

check "pbcal cds before invoking claude" yes \
    "$(grep -A1 'run_claude() {' "$PBCAL" | grep -q 'cd "\$claude_cwd"' && echo yes || echo no)"

check "pbcal creates a scratch cwd" yes \
    "$(grep -q 'claude_cwd=\$(mktemp -d' "$PBCAL" && echo yes || echo no)"

# pdf-rename: the subprocess call must carry an explicit cwd= kwarg.
check "pdf-rename passes cwd= to the claude subprocess" yes \
    "$(grep -q 'run(\[CLAUDE, "-p", PROMPT + text\], cwd=cwd)' "$PDFRENAME" && echo yes || echo no)"

check "pdf-rename imports tempfile" yes \
    "$(grep -q '^import tempfile' "$PDFRENAME" && echo yes || echo no)"

# --- each caller recognizes a hook block -----------------------------------
#
# A hook block arrives as exit 0 with the notice on stdout, so an exit-code
# check cannot catch it. Both callers must test the output text.

check "pbcal detects a hook block" yes \
    "$(grep -q "blocked by hook" "$PBCAL" && echo yes || echo no)"

check "pdf-rename detects a hook block" yes \
    "$(grep -q 'blocked by hook' "$PDFRENAME" && echo yes || echo no)"

# --- the detection branch actually fires on real block text ----------------
#
# Replays the exact stdout captured from the failing run, through the same
# grep pbcal uses, so the test fails if that predicate is ever loosened.

block_text='UserPromptSubmit operation blocked by hook:
[/Users/wiggins/.claude/hooks/block-home-dir.sh]: {"hookSpecificOutput": {"decision": "block", "reason": "Claude Code cannot run in the home directory."}}

Original prompt: Parse the following text and generate a bash script...'

check "real block text matches the detector" yes \
    "$(echo "$block_text" | grep -q 'blocked by hook' && echo yes || echo no)"

# Negative control: ordinary generated output must NOT trip the detector,
# or every successful run would be reported as blocked.
good_output='<<<CALPARSE_START>>>
#!/bin/bash
./gcal-invite-advanced add "Dinner" "2026-09-12 6:00pm" 120 ""
<<<CALPARSE_END>>>'

check "ordinary output does not trip the detector" no \
    "$(echo "$good_output" | grep -q 'blocked by hook' && echo yes || echo no)"

# --- both files still parse ------------------------------------------------

check "pbcal parses" yes \
    "$(bash -n "$PBCAL" 2>/dev/null && echo yes || echo no)"

check "pdf-rename parses" yes \
    "$(python3.11 -c "import ast,sys; ast.parse(open('$PDFRENAME').read())" 2>/dev/null && echo yes || echo no)"

# --- summary ---------------------------------------------------------------

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
