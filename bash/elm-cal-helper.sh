#!/bin/bash
# Helper: called by elm to run Claude CLI in a clean environment
# Usage: elm-cal-helper.sh <prompt-file> <output-file>
# Debug: writes to /tmp/elm-cal-debug.log

exec 2>/tmp/elm-cal-debug.log

echo "=== elm-cal-helper ===" >&2
echo "Date: $(date)" >&2
echo "Prompt size: $(wc -c < "$1")" >&2

for var in $(env | grep -oE '^(CLAUDE|VSCODE)[A-Z_]*'); do unset "$var"; done
unset ELECTRON_RUN_AS_NODE GIT_EDITOR
for var in $(env | grep -oE '^OTEL_[A-Z_]*'); do unset "$var"; done

prompt="$(cat "$1")"
echo "Prompt length: ${#prompt}" >&2

# Find Claude binary path dynamically
CLAUDE_BIN=$(command -v claude || echo "/Users/wiggins/.local/bin/claude")

# Python one-liner for full session isolation and FD cleanup on macOS
python3 -c "import os, sys; os.closerange(3, 1024); os.setsid(); os.execv(sys.argv[1], sys.argv[1:])" \
    "$CLAUDE_BIN" \
    --print "$prompt" --model haiku \
    --no-session-persistence \
    --disable-slash-commands \
    --allowedTools '' < /dev/null > "$2" 2>&1

rc=$?
echo "RC: $rc" >&2
echo "Output size: $(wc -c < "$2")" >&2
echo "Output:" >&2
cat "$2" >&2
echo "=== done ===" >&2
