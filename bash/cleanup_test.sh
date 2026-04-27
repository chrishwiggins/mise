#!/bin/bash
echo "=== 1. Environment Dump ==="
env | sort > /tmp/cleanup-env-user.txt
echo "Saved environment to /tmp/cleanup-env-user.txt"

echo "=== 2. Process Tree ==="
# Try to get the process tree for the current scripts
ps -g $$ -o pid,ppid,command > /tmp/cleanup-ps-user.txt
echo "Saved process tree to /tmp/cleanup-ps-user.txt"

prompt="Clean up this text: Hey howas tit gon offer there"

echo "=== 3. Testing direct execution ==="
"${HOME}/.local/bin/claude" -p "$prompt" < /dev/null > /tmp/cleanup-out-direct.log 2>/tmp/cleanup-err-direct.log
echo "Direct exit code: $?"
echo "Direct stdout length: $(wc -c < /tmp/cleanup-out-direct.log)"
echo "Direct stderr length: $(wc -c < /tmp/cleanup-err-direct.log)"

echo "=== 4. Testing with setsid ==="
setsid "${HOME}/.local/bin/claude" -p "$prompt" < /dev/null > /tmp/cleanup-out-setsid.log 2>/tmp/cleanup-err-setsid.log
echo "setsid exit code: $?"
echo "setsid stdout length: $(wc -c < /tmp/cleanup-out-setsid.log)"
echo "setsid stderr length: $(wc -c < /tmp/cleanup-err-setsid.log)"

echo "Done. Please let the AI know you have run this script!"
