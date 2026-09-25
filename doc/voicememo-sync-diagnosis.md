# Voice memo sync and transcription: state as of 2026-09-17

Scope: one session's diagnosis of why no voice memos from 2026-09-17 appeared on
disk. Not a full audit of the transcription tooling.

## The question

Chris said he recorded voicemail reminders today and asked to find them in
`~/Documents/VoiceMemos`.

## What is true

No audio or transcript file dated 2026-09-17 exists anywhere searched.

- `~/Documents/VoiceMemos`: 592 files, newest `Sep 5 16:12`. Zero newer than
  2026-09-17 00:00.
- Apple's own library, `~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings`:
  262 `.m4a` files, newest `20260905 145544.m4a` at `Sep 5 15:03`. Zero from today.
- `~/Documents`, `~/Downloads`, `~/Desktop`, `~/Library/Group Containers` swept for
  `.m4a`/`.wav`/`.mp3`/`.caf`: 735 audio files found as positive control, zero dated today.

Conclusion: the recordings are not on this Mac. They are presumed still on the
phone, unsynced. UNVERIFIED: nobody has looked at the phone; this is inference
from absence on the Mac, not observation of presence on the device.

## Two defects found

### 1. The cron job has never worked at its current path

`crontab -l` line:

    */30 * * * * /bin/bash /mise/bash/process_voicememos > /dev/null 2>&1

`/mise/bash/process_voicememos` does not exist. The real path is
`/Users/wiggins/mise/bash/process_voicememos`. The leading `/Users/wiggins` is
missing, so every run for however long has been bash failing to open the file,
with the error discarded by `> /dev/null 2>&1` and the exit code unexamined.

This is the `cmd && success || failure` family of bug: silent failure that looks
like a working automation.

### 2. Two scripts do this job, and the log is written by the other one

- `~/mise/bash/process_voicememos`: older, single-threaded, uses Gemini for topic
  naming. This is what cron names.
- `~/mise/bash/xcribe`: newer, ~500 lines, parallel jobs, model selection
  (`-l`/`-small`/`-tiny`), lockfile, dry-run, single-file and alternate-directory
  modes. Uses Claude for topic naming.

Both write the same `$LOG_FILE` (`~/.voicememo_processing.log`, 2.3M) and the same
`$PROCESSED_LIST` (`~/.voicememo_processed`), so the log interleaves the two.

Today's log lines, 1066 of them from 17:30:16 to 18:57:05, are `xcribe`: the string
`-> Skipping: already processed with base model` is generated at `xcribe:265` and
appears in no other script in mise or seiton. So `xcribe` was run by hand today. It
correctly found nothing new, because the source directory holds nothing newer than
Sep 5.

## How to get today's memos

Sync first, then transcribe. The transcriber cannot invent files that are not there.

1. Open Voice Memos on the Mac (`voice` alias) and leave it frontmost. Sync often
   fires only while the app is open.
2. If nothing appears, confirm iCloud has Voice Memos enabled on both the Mac
   (System Settings, Apple Account, iCloud, see All) and the phone (Settings,
   name, iCloud, see All).
3. On the phone, open Voice Memos and pull down to refresh; stay on Wi-Fi.
4. Alternative that skips iCloud entirely: AirDrop the memos to the Mac, then
   `xcribe -d <dir>` on wherever they land.

Once the files are in the Recordings directory, run `xcribe` (not
`process_voicememos`).

## Not done

- The broken cron path was not edited. Editing a crontab is Chris's call.
- Which of the two scripts should survive was not decided. Running both against one
  shared processed-list is a hazard: they key on `hash:model`, so behavior when one
  script's entries meet the other's expectations is unverified.
