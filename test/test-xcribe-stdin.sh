#!/bin/bash
# Regression test for xcribe's stdin bug: background jobs inherited the file
# list on stdin, ffmpeg read it, and the next path lost its head, so memos
# failed with "Transcript file not found". Runs xcribe under a fake HOME with
# -parallel 2 on 3 memos from the source folder, placed in a folder whose path
# has a space. ffmpeg only eats stdin on non-trivial conversions, so memos are
# picked at 2 to 4 MB.
# Pass: 3 transcripts, 0 "not found" errors. Exit 2: too few memos to test.
# Usage: test-xcribe-stdin.sh [memo folder] [path to xcribe]
SRC="${1:-$HOME/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings}"
XCRIBE="${2:-$(dirname "$0")/../bash/xcribe}"
T=$(/usr/bin/mktemp -d /tmp/xcribe-stdin-test-XXXXXX)
REC="$T/Group Containers/rec"
/bin/mkdir -p "$T/home/Documents/VoiceMemos" "$T/home/.config/voicememos" \
    "$T/home/.local/share/whisper-cpp" "$REC"
/bin/ln -s "$HOME/.local/share/whisper-cpp/models" "$T/home/.local/share/whisper-cpp/models"
# find -size counts 512-byte blocks: 4096 is 2 MB, 8192 is 4 MB.
/usr/bin/find "$SRC" -maxdepth 1 -name '*.m4a' -size +4096 -size -8192 | /usr/bin/sort | head -3 |
    while IFS= read -r f; do /bin/cp -p "$f" "$REC/"; done
have=$(/usr/bin/find "$REC" -name '*.m4a' | wc -l | tr -d ' ')
if [ "$have" -ne 3 ]; then
    echo "need 3 memos of 2 to 4 MB in $SRC, found $have"
    /bin/rm -rf "$T"
    exit 2
fi
echo "$REC" > "$T/home/.config/voicememos/dirs"
HOME="$T/home" /bin/bash "$XCRIBE" -parallel 2 -base > "$T/run.log" 2>&1
echo "xcribe exit: $?"
n=$(/usr/bin/find "$T/home/Documents/VoiceMemos" -name '*.md' | wc -l | tr -d ' ')
bad=$(/usr/bin/grep -c 'Transcript file not found' "$T/home/.voicememo_processing.log" 2>/dev/null)
bad=${bad:-0}
echo "transcripts: $n (want 3)   not-found errors: $bad (want 0)"
/bin/rm -rf "$T"
[ "$n" -eq 3 ] && [ "$bad" -eq 0 ] && echo PASS || { echo FAIL; exit 1; }
