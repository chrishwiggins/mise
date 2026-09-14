# Plan: paths that survive the round trip through the terminal

## Goal

A path Claude prints can be handed back to Claude without Chris ever
copying it from a wrapped terminal line, and a path that does arrive with
whitespace inside it is repaired before any tool acts on it. Success is
measurable: the three failures of 2026-09-13 ("TSC-l ocal",
"hello_group_del ivery_test", and a wrapped `m send -H ... -a ...` that
silently dropped the attachment) each become either impossible or
self-corrected, with a regression test per case.

## Context

The Claude Code TUI wraps long lines at terminal width and its renderer pads
the wrap point, so a copied path comes back with two to four spaces inserted
mid-token. Long absolute paths are the norm here (the TSC project root alone
is 87 characters), so nearly every path Claude prints wraps. Today the
repair is manual: Claude notices the gap, guesses the join, and says so.
That costs a turn each time and has already produced one real failure (the
`-a` on the second line of a wrapped send command never reached `m`).

Existing pieces this plan builds on rather than duplicates:

- `/pbcopy` and `/path` skills exist; they put content or a path on the
  clipboard so nothing is copied from the terminal. They are unused in
  practice because Claude prints the path and Chris copies it before either
  is invoked.
- `~/.claude/hooks/rtk-rewrite.sh` is a wired PreToolUse hook on Bash, so
  the harness already runs a rewrite-style hook before a tool executes; its
  mechanism is the template for the repair hook.
- `~/.claude/hooks/strip-whitespace.sh` exists; read it first, it may be a
  half of this already.
- Global CLAUDE.md already carries the narrow rule for send commands (`cd`
  to the project root, relative paths, `-a` before `-H`). That rule treats
  one symptom; this plan treats the cause.

## Approach

Two halves, because the failure has two ends.

Receiving side (Chris's copy): stop relying on the terminal as the transport.
Every long path Claude prints is also recorded in a numbered path box, and a
one-letter shell command puts entry N on the clipboard or prints it. Chris
types `@3` instead of pasting 90 characters. This makes wrapping irrelevant
rather than trying to defeat it, since terminal width is not ours to control.

Sending side (Claude's receipt): a deterministic resolver that takes a
whitespace-damaged path and returns the real one, wired in three places:
a PreToolUse hook that fixes `file_path` and Bash arguments before the tool
runs, a UserPromptSubmit hook that annotates the prompt with the repaired
path, and the path-taking skills (/edit, /peek, /grab, /pbcopy, /sent),
which call the resolver first.

Considered and rejected:

- Shorter paths via symlinks (`~/p/tsc -> .../TSC-src`). Helps the one
  project it is made for, breaks provenance in commit messages and docs that
  must cite real paths, and the wrap still happens at 80 columns for any
  path over about 70 characters. Partial fix with a maintenance tax.
- Asking Claude to always print paths on their own line in a code block.
  Already the norm and the wrap still happens; the copy is what inserts the
  spaces, not the rendering.
- Widening the terminal. Not a tool; Chris runs many sessions in split
  panes on purpose.
- Fuzzy matching over the whole filesystem. Too slow and too clever; the
  damage is always whitespace inserted into an otherwise exact path, so the
  repair is a search over whitespace removals, not a search over files.

## Steps

### 1. The resolver: `~/mise/py/fixpath`

- Files: create `~/mise/py/fixpath` (python3.11, no third-party deps), and
  `~/mise/test/test-fixpath.py`.
- What: `fixpath <string>` prints the repaired absolute path and exits 0,
  or prints nothing and exits 1. Algorithm, in order:
  1. If the string exists as given, print it.
  2. Collapse every run of whitespace to nothing; if that exists, print it.
     (This alone fixes all three cases from 2026-09-13.)
  3. If not, treat each whitespace run as a choice point (drop it, or keep
     one space, since real filenames can contain single spaces) and test
     each combination, at most 2^k for k runs, capped at k=8.
  4. If still nothing, split at the last `/` that yields an existing
     directory, list that directory, and return the single entry whose
     name equals the damaged tail with whitespace removed; refuse (exit 1)
     if zero or more than one match. Never guess by similarity.
  Also accept `~` and `./` prefixes and expand them. Print only the path,
  so callers can substitute it.
- Verify: the test file holds the three real cases plus a filename with a
  genuine single space, a nonexistent path (exit 1), and an ambiguous
  directory (exit 1). `python3.11 ~/mise/test/test-fixpath.py` passes.

### 2. The path box: `~/mise/bash/pp` and a Stop hook that fills it

- Files: create `~/mise/bash/pp`; create `~/.claude/hooks/pathbox-record.py`;
  wire it under `Stop` in `~/.claude/settings.json` (this wiring is the one
  step Chris does by hand, since settings.json is shared by live sessions).
- What: the Stop hook reads the transcript path from stdin JSON, scans the
  final assistant message for absolute paths and `~/` paths that exist on
  disk, and appends each new one to `~/.cache/pathbox.txt` with a running
  index, most recent last, deduplicated, capped at 50 lines. `pp` with no
  argument prints the last 10 entries numbered; `pp N` prints entry N and
  puts it on the clipboard; `pp -c` clears. Claude's side: when it prints a
  long path it may add "(pp 12)" after it, but the box works without that
  since the hook records every path regardless.
- Verify: after a Claude turn that prints a path, `pp` lists it; `pp 1 |
  pbpaste` round-trips it byte-identical. The test hook harness
  `~/.claude/hooks/test-hook-stdin.sh` runs the recorder on a synthetic
  transcript without error.

### 3. `@N` in prompts: a UserPromptSubmit hook that expands path-box refs

- Files: create `~/.claude/hooks/pathbox-expand.py`; wire under
  `UserPromptSubmit` (Chris's hand, same reason as step 2).
- What: reads the prompt from stdin JSON; for every token matching `@\d+`
  it looks up the path box and prints one line of additional context:
  `@3 = /full/path`. It also runs every path-shaped token with internal
  whitespace through `fixpath` and prints `repaired: <as typed> -> <real>`.
  UserPromptSubmit hooks add context rather than rewriting the prompt, so
  this is advisory to Claude and deterministic in content; the PreToolUse
  hook in step 4 is what makes it binding.
- Verify: `test-hook-stdin.sh` with a synthetic prompt containing `@2` and
  a damaged path prints both lines and exits 0; a prompt with neither
  prints nothing and exits 0.

### 4. The binding repair: a PreToolUse hook on Read, Edit, Write, and Bash

- Files: create `~/.claude/hooks/fixpath-pretool.py`; wire under
  `PreToolUse` with matcher `Read|Edit|Write|Bash` (Chris's hand).
- What: for Read/Edit/Write, if `tool_input.file_path` does not exist and
  `fixpath` resolves it, emit the corrected input. For Bash, apply the same
  to every argument that looks like a path with internal whitespace. The
  output shape is proven: `rtk-rewrite.sh` (wired on Bash today) returns
  `hookSpecificOutput.updatedInput` with the rewritten input, and this
  harness honors it (its line 83). Copy that shape. Keep an exit-2 fallback
  with `path repaired: <real>` on stderr for any tool where the rewrite is
  refused, which still hands Claude the fixed path in one step instead of a
  guess-and-retry.
- Verify: with the hook wired, a Read of a whitespace-damaged path either
  succeeds transparently or fails once with the correct path in the
  message; never a second guess. Regression test in
  `~/mise/test/test-fixpath-hook.sh` pipes a synthetic PreToolUse event.

### 5. Teach the path-taking skills to call the resolver

- Files: `~/.claude/commands/edit.md`, `peek.md`, `grab.md`, `pbcopy.md`,
  `sent.md`, and `~/.claude/skills/next/SKILL.md` where it names paths.
- What: one line each: "Resolve the argument with `~/mise/py/fixpath` before
  using it; if it exits 1, ask which file was meant rather than guessing a
  join." Also `/pbcopy` gains: when given no argument after Claude just
  printed a path, copy that path (from the path box) rather than asking.
- Verify: `/edit` on a damaged path opens the right file without a
  clarifying turn.

### 6. Retire the manual rule

- Files: `~/.claude/CLAUDE.md`, the send-command paragraph under Email
  Sending.
- What: keep the `-a` before `-H` ordering advice, replace "give the
  command relative to the project root" with "give the command as `m send
  -a @N -H @M`" once `m` accepts `@N` from the path box (one small change
  in `~/mise/bash/m`: expand `@\d+` arguments through `pp N` before use).
- Verify: `m send --dry-run -H @1` prints the resolved path.

## Risks

- A path with a real single space in a filename is ambiguous with a wrapped
  one. Step 1 handles it by trying both and refusing to guess when more than
  one candidate exists; the test covers it.
- Rewriting tool input from a PreToolUse hook is honored for Bash today
  (rtk-rewrite.sh); whether Read, Edit and Write accept the same
  `updatedInput` is untested until step 4 runs. The exit-2 fallback covers a
  refusal.
- The Stop hook adds a transcript scan to every turn end. It reads one
  message, not the file; keep it under 50 ms and it is invisible.
- settings.json wiring is done by hand while other sessions run; three
  hooks means three edits. Stage the exact JSON in the plan's execution
  commit so the edit is a paste.

## Out of Scope

- Changing the TUI's wrapping or column padding; not ours.
- Fuzzy or similarity-based path recovery; the damage class is whitespace
  insertion and the resolver stays exact.
- Project-specific path shortcuts; everything here lives in mise and works
  in any project.
