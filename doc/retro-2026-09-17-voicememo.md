# Retro: voice-memo sync session, 2026-09-17

Scope note: this covers one short session about finding today's voice memos. The
repo-wide retro from the alias-migration session is /Users/wiggins/mise/retro.md
and was not touched.

## What this session actually was

You asked where today's voicemails were. They were nowhere on this Mac, and the
useful part of the session was proving that rather than guessing it, then finding
two defects in the tooling that the question exposed.

## Where it went wrong

I gave you a command before I knew which script was live. The first answer ended
with "run `process_voicememos`", and that was wrong: the log lines from today
carry a string generated at xcribe:265, so xcribe is what runs. I caught it in
the same message only because I happened to notice the log wording did not match
the script I had read. That is luck, not method. The sequence was: read one
script, form an answer, then check. The check belonged first, and it was one
grep.

The deeper version of the same error is that I read `process_voicememos` in full
before establishing it was the relevant file. Two scripts matched the path grep
and I opened the first one. Opening the newest, or grepping both for the log
string, would have cost the same and pointed at the right one.

## Agentic concepts left on the table

This was a small session and mostly did not need agents, so I will not invent
problems. Two honest ones:

The absence proof ran as four sequential inline Bash calls in the main window:
list the directory, find by mtime, check the Apple library, sweep four home
directories for four extensions. That is a fan-out over a filesystem whose entire
useful output is two numbers (735 audio files found, zero from today). One Explore
agent with the whole question list would have returned those two numbers and kept
the directory listings out of this context. Your CLAUDE.md already says a tooling
inventory across mise and seiton is Explore work; a filesystem sweep for one date
is the same shape.

The second is smaller. When I found two scripts with the same job, I read one in
full and skimmed the other with head. Reading both properly is what settled it
twenty minutes later. A single "read both, tell me which one writes this log
string" would have been faster than the path I took.

## Deterministic over generative

The broken cron path is the real finding, and it is exactly the category your
rules call out: a command that fails every run while reporting nothing, because
stderr goes to /dev/null and nobody reads an exit code. It has presumably been
dead for a long time.

Diagnosing it by eye does not scale and does not repeat. So I wrote the checker
instead: /Users/wiggins/mise/py/cron-path-check reads your crontab, resolves every
command path, and exits 1 with the offending entries. On your live crontab it
reports one broken path out of ten, which is the voice-memo entry.

Getting it right took two rounds, both worth recording. The first version
crashed on the wget entry, whose quoted URL contains an ampersand. The second
reported five failures, four of which were `2>&1` splitting into a phantom `1`.
A checker with a 4-in-5 false positive rate is worse than none, because you stop
reading its output. It now strips redirections before splitting and is pinned by
/Users/wiggins/mise/test/test_cron_path_check.py, sixteen assertions covering
both directions: real missing paths caught, ordinary entries quiet.

## Context discipline

Fine. No screenshots, no large file dumps. The one avoidable cost was reading a
500-line script's help output when `grep -n` for one string was the question.

## Next-time playbook

1. Claude (encoded at /Users/wiggins/mise/py/cron-path-check, tested at
   /Users/wiggins/mise/test/test_cron_path_check.py): verify scheduled-job paths
   with the checker rather than by reading a crontab. It exists because reading
   by eye is how this bug survived.

2. Claude (encoded at /Users/wiggins/mise/doc/voicememo-sync-diagnosis.md and the
   project memory file): when a transcript is missing, list the Apple Recordings
   directory and compare its newest mtime to the date in question BEFORE touching
   the transcriber. The tool is usually fine; the file never arrived.

3. Claude (judgment, not encodable): when two scripts match a grep for the same
   path, identify which one is live before reading either in full. The cheapest
   discriminator here was a distinctive string from the log. I read first and
   discriminated second, and handed over a wrong command in between.

4. Chris: run /Users/wiggins/mise/py/cron-path-check, then fix the one entry it
   names. `crontab -e`, change /mise/bash/process_voicememos to
   /Users/wiggins/mise/bash/xcribe. That restores the every-30-minutes
   transcription that has been silently dead, and points it at the newer script.

5. Chris: get today's recordings onto the Mac, by opening Voice Memos and letting
   iCloud sync or by AirDrop from the phone, then run `xcribe`. Nothing else in
   this session can proceed until the files exist; that they exist at all rests on
   your word, since no file was observed on any device.
