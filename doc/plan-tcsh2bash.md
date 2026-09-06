# Plan: migrate `~/mise` tcsh/csh aliases and scripts to bash

Status: partly executed, 2026-09-05. Steps 1 and 2 are done and shipped, as
is batch 4f and the retirement the census made possible. Steps 3, 4a through
4e, 4g through 4j, and 5 remain. Each completed step carries a DONE marker
with its commit.

  step 1  golden harness              DONE  dcb76da
  step 2  dead-alias census           DONE  783ff1e
  retire  DEAD and SHADOWED aliases   DONE  d2d0918
  4f      shebangs, 10 of 12 files    DONE  d2d0918
  step 3  per-alias decisions         open, and 7 shell-only rows block batch 4
  4a-4e   the alias translation tiers  open, unblocked by step 1
  4g-4i   the remaining script tiers   open
  step 5  regression test              open

## Goal

Move the shell surface in `~/mise` from tcsh/csh to bash, without ever
breaking a working command and without deleting anything.

Success looks like: every alias in `sh/aliases-public.sh` and every script in
`sh/`, `csh/`, and `tcsh/` has been classified and then either translated to a
bash script in `bash/`, kept deliberately as a shell alias or function with a
written reason, or retired as already-dead. At the end, `sh/aliases-public.sh`
is a short file of things that genuinely must be shell-level, and everything
else is a real executable that bash, zsh, and tcsh can all call.

Note that `sh/` is in scope and is not what its name suggests: it holds tcsh
scripts, a csh script, and files with no shebang at all. Directory names are
not evidence of interpreter here; the first line of each file is.

Verify: a golden-output differential harness (step 1) that captures each
alias's and each script's observable behavior before the change and asserts it
unchanged after. Plus two negative checks: `grep -c '^alias '
sh/aliases-public.sh` falls from 335 toward the shell-only remainder (305 live aliases as of the 2026-09-05 retirement, of which 23 are shell-only and stay), and

    head -1 sh/* csh/* tcsh/* | grep -c tcsh

falls to zero. No invocation Chris actually types starts failing.

## Context

Measured this session, against the real files, not estimated:

`sh/aliases-public.sh` has 582 lines, 335 `alias` lines, 119 commented-out.

The 335 is a line count and is NOT the translation surface. 15 alias names are
defined more than once in the file (`gpy3` three times, at lines 460, 461,
462), and tcsh keeps only the last definition of a name. That makes 16 alias
lines unreachable dead code, and leaves 319 distinct live aliases:

    335 alias lines - 16 shadowed lines = 319 live aliases

Confirmed two ways: `awk '{print $2}' | sort -u` over the alias lines returns
319, and `py/alias-health` reports 328 registered in a real tcsh (the gap to
319 being `unalias` lines and tcsh builtins). Verified that last-wins is the
actual behavior: sourcing the file and asking `alias gpy3` returns the line
462 definition, not 460.

Every count below is computed over the 319 LIVE aliases (last definition of
each name), not over the 335 lines. The first draft of this plan used
line-based counts and every one of them was slightly wrong.

| property | count | why it matters |
|---|---|---|
| take arguments (`\!` markers) | 41 | `\!:*` 12, `\!*` 11, `\!:1` 18; these must become `"$@"` scripts |
| contain backticks | 17 | command substitution; evaluation timing differs |
| contain `$` variables | 45 | depend on env set at login; a script gets its own env |
| contain a pipe | 57 | fine in a script, but quoting must be re-checked |
| multi-command (`;`) | 69 | become multi-line scripts |
| plain 3-token, one-word target | 50 | the trivial tier, near-mechanical |
| must mutate the parent shell | 11 | 4 `cd`, 3 `setenv`, 2 `source`, 2 `history`; cannot be scripts at all |

The "11 shell-only" figure above is a grep result and it UNDERCOUNTS. The
census (step 2, now run) puts the real figure at 23. See the census results
below.

### Census results, 2026-09-05

Step 2 has been executed. `py/alias-census` classifies all 335 alias lines;
full table in `doc/alias-census.md`.

| class | n | meaning |
|---|---|---|
| LIVE | 256 | target resolves; the translation surface |
| CHAIN | 36 | target is another alias in this file; translate the target first |
| SHELL-ONLY | 16 | calls cd/setenv/set/source/history/alias directly |
| SHADOWED | 16 | never reachable; retire, never translate |
| DEAD | 11 | target verified gone; retire |

256 + 36 + 16 + 16 + 11 = 335, so every alias line is classified exactly once.

RETIREMENT DONE 2026-09-05. The DEAD and SHADOWED rows have been retired in
place as `# DEAD 2026-09-05: <original>` / `# SHADOWED 2026-09-05: <original>`
comments plus `unalias`. The census now reads LIVE 254, CHAIN 35, SHELL-ONLY
16, over 305 alias lines, with DEAD and SHADOWED both empty. 14 alias names
stopped registering, verified by diffing the full registered set before and
after; nothing was added. Two retirements were judgment calls where the
SHADOWED line worked and the LIVE line was broken (`drive`, `omail`); Chris
chose to retire both halves and leave those names undefined. `profile`
cascaded, having chained to the retired `py3`. Details in
`doc/alias-census.md`.

Three findings change the plan:

1. TRUE SHELL-ONLY IS 23, NOT 11. The earlier grep counted only aliases whose
   body starts with `cd`/`setenv`/`source`/`history`. It missed `set` and
   `alias` bodies, and it missed seven CHAIN rows that point at an alias whose
   own body is shell-only, inheriting the property transitively: `dusort` (58),
   `miseup` (113), `remise` (115), `d` (134), `pu` (223), `uppu` (478), `cd-f`
   (541). Translating any of those to a script produces a command that silently
   fails to change the caller's directory, the same silent-failure class that
   started this project.

2. ONLY 11 ALIASES ARE DEAD, not "maybe half" as the approach section guessed.
   All 11 were hand-verified independently of the tool, against both alias
   files: `jsc` (57), `gv` (136, smail), `json-grep` (158, jgrep), `conda-tend`
   (191, conda), `pwstore` (197), `st2` (231, Sublime Text 2), `att` (412, gg),
   `to` (414, gg), `py3` (459, anaconda3), `g0` (468, googler), `wifis` (517,
   airport). The optimistic case where the census shrinks the project did not
   happen: 292 of 335 lines are live work.

3. CHAIN IS A NEW CLASS THE PLAN DID NOT ANTICIPATE. 36 aliases invoke another
   alias in the same file. These constrain ORDER, not difficulty: a chain's
   target must be translated before the chain itself, or the chain breaks the
   moment its target is unaliased. Batches must be ordered by dependency, not
   only by risk.

Standalone scripts: 57 total across all three directories, not the 39 counted
in the first draft of this plan. `sh/` was initially overlooked, and it is not
a POSIX-sh directory at all: it is a grab-bag holding tcsh scripts, one csh
script, two real `/bin/sh` scripts, two that are already bash, and four with
no shebang.

Classified by actual interpreter (the first line of the file), not by which
directory it happens to sit in:

| interpreter | count | work required |
|---|---|---|
| `#!/bin/tcsh` | 38 | real translation |
| no shebang, portable body | 12 | add `#!/bin/bash`, no translation |
| `#!/bin/sh` | 2 | near-free, sh is close to bash |
| no shebang, csh syntax in body | 2 | real translation |
| `#!/bin/csh` | 1 | real translation |
| already `#!/bin/bash` | 2 | none |

The 12 no-shebang portable files are the happy surprise: `sh/ffix`, `sh/fix`,
`sh/npr`, `sh/update`, `sh/werds`, `sh/words`, `tcsh/lgit`, `tcsh/ogit`,
`tcsh/reply`, `tcsh/unspace`, `tcsh/unspace-mvs`, `tcsh/unzoom` contain no
csh-only syntax. They are pipelines and one-liners that already run under
bash; they only ever worked by inheriting the caller's shell. Adding a shebang
line is the entire fix. Two of them (`tcsh/unspace`, `tcsh/unspace-mvs`) have
a commented-out `#/bin/tcsh` shebang, which is the worst case: it looks
intentional and does nothing.

Line budget across all 57 files: 1828 lines total, of which
`sh/aliases-public.sh` is 582 and `tcsh/ocr` is 281. Everything else together
is 965 lines, so two files are half the project.

`sh/login-public.sh` (72 lines, 12 `set`/`setenv`/`alias` lines) is a special
case: it is sourced at login, not executed, so it cannot become a script at
all. It belongs with the shell-only tier.

Environment: Chris has 26 live tcsh processes right now. The account's
`UserShell` says `/bin/zsh` and `$SHELL` agrees, but tcsh is the actual
working shell, driven by `~/.tcshrc` pointing at
`gd/local/seiton/dotfiles/.tcshrc`. `~/mise/bash` already holds 117 bash
scripts and is early on `$PATH` (position 4), so the target convention and
precedence already exist.

Precedent from earlier today: we converted the arg-swallowing
`gcal`/`gdrive`/`gsheet`/`quote` aliases into `bash/subcommand-dispatch` plus
four wrappers, replaced each alias with `unalias <name>` in place (comment
explaining why, alias text preserved in git history), and backed it with a
9-test hermetic harness in `test/`. That commit (`d9b6008`) is the template
this plan generalizes: script in `bash/`, `unalias` in the alias file, test
in `test/`.

## Approach

Four ideas carry the whole plan.

1. Classify before translating. The expensive mistake is translating 305
aliases when maybe half are dead. So the first deliverable is not a
translation, it is a census: a deterministic checker that resolves each
alias's target and reports live / dead / shell-only. Translation effort then
goes only where it pays.

2. Golden-output differential testing, captured BEFORE any edit. For each
alias we record what it actually does today in a real tcsh, then assert the
bash script produces the same thing. This is the only way to make 305
translations trustworthy, and it must run first: once an alias is edited its
original behavior is unrecoverable except from git.

3. `unalias`, never delete. Chris's hard requirement. Every retired alias
stays in the file as a comment plus an `unalias` line, so the original text is
readable in place and in `git log`. Rollback for any single alias is
un-commenting one line. Rollback for a whole batch is `git revert` of one
commit. Nothing is ever `rm`'d, and the csh/tcsh script directories are kept
on disk even after their bash replacements land.

4. Risk tiers, smallest blast radius first. Batch by difficulty so early
batches build confidence in the harness before it is trusted on hard cases.

### Considered and rejected

- Automated tcsh-to-bash transpiler. Rejected: csh grammar is genuinely
  irregular (`\!:1` history substitution, `:r`/`:t` modifiers, its own
  quoting), and a transpiler that is 90% right on 305 aliases leaves about 30
  silent breakages, exactly the failure mode that started today's session.
  Machine assistance for the trivial tier, human judgment for the rest.
- Big-bang rewrite of `aliases-public.sh`. Rejected: unreviewable, and one bad
  line breaks every new shell Chris opens.
- Converting everything to zsh instead. Rejected: Chris asked for bash, and
  bash scripts are callable from tcsh, zsh, and bash alike. The point of
  moving to `bash/` is that the caller's shell stops mattering.
- Deleting dead aliases as we find them. Rejected by the stated requirement.
  They get `unalias` plus a `# DEAD:` comment instead.
- Touching seiton's private aliases in the same pass. Out of scope; see below.
  `seiton/sh/aliases-private.sh` is about 5000 lines and deserves its own run
  of this same plan once the machinery is proven on the smaller file.

## Steps

### 1. The golden-output harness (DONE 2026-09-05, commit dcb76da)

- Files: `test/alias-golden.py` (runner), `dat/alias-golden/` (305 captures,
  21524 bytes).
- What it records: the command line each alias EXPANDS TO, with no arguments
  and, when the body takes arguments, with the fixed probe arguments ARG1 and
  ARG2. One capture per alias, all 305, no skips and no refusals.
- IT PARSES. IT DOES NOT EXECUTE. This is the load-bearing design decision and
  the reason the section below exists.
- Verify: `./test/alias-golden.py --check` re-expands and diffs against what is
  stored. Three consecutive runs reported 0 differing. Ten captures were
  hand-checked against the source (spotify, gcals, palias, htm2png, pbdate,
  txt2m4a, dusort, code, vs, l), chosen to include the redirection and
  absolute-path cases.
- Gate: SATISFIED. Batches 4a through 4e may proceed.

Substitution rules were verified against tcsh rather than assumed. `\!*` and
`\!:*` take the whole argument list, `\!:N` takes one, and the `:r`, `:t` and
`:e` word modifiers chain left to right. With NO arguments the two forms
differ, and that difference is why the empty case is captured at all: `\!*`
expands to nothing and the command still runs, while `\!:1` fails with
`Bad ! arg selector.` 18 captures record that error, and each one marks an
alias whose bash translation must REJECT a missing argument rather than
silently pass an empty string. That is the silent-failure class that started
this project.

Chains are deliberately not resolved. `pbdate` records `datestr| pbcopy`
rather than whatever `datestr` bottoms out in, because the unresolved form
names the thing that still has to be translated.

#### Do not rebuild the executing version

The first version of this harness did what the original draft of this step
prescribed: run each alias in a real tcsh under a stubbed `PATH`. That design
is recorded here because it looks reasonable on paper and is not.

- `palias` is `echo "alias \!*" >> $paliases`, and `login-public.sh` sets
  `$paliases` to `aliases-public.sh` itself. Running it APPENDED SIX LINES TO
  THE ALIAS FILE BEING CAPTURED. Recovered with `git checkout`, and only
  because the file happened to be committed minutes earlier.
- `pip3-tend` chains to `pip3s` in the PRIVATE alias file, which writes
  `$cwaux/pip3-<timestamp>.asc`. One run left 29 junk files in
  `~/gd/local/seiton/aux`. A guard that inspects the invoked alias body cannot
  see a redirect two aliases away.
- `htm2pdf` and `htm2png` invoke Chrome by ABSOLUTE PATH, which no stub `PATH`
  can intercept. Real headless Chrome ran and left `screenshot.png` and
  `output.pdf` in the repo root.
- Sandboxing `HOME` to contain those writes broke the login chain: only 1128
  of 3109 aliases registered, and 226 of 305 captures came back "Command not
  found". A baseline full of failures that still looked valid.
- 46 alias names also appear as words inside other alias bodies, so a stub
  named after an alias SHADOWED it, and `spotify` captured `CMD spotify`
  instead of `open /Applications/Spotify.app/`.

The measured difference between the two designs:

| | executing | parsing |
|---|---|---|
| runtime | 4m47s | 0.076s |
| determinism | 3 aliases unstable | 0 differing over 3 runs |
| "Command not found" | 226 of 305 | 0 |
| refused to capture | 36 | 0 |
| files written | the alias file, 29 in aux, 2 in repo | none |

Answering "what does this alias run" needs the alias body with its history
markers substituted, which is a text transformation. Nothing needs to run, and
when nothing runs, none of the five failures above is possible.

### 2. Deterministic dead-alias census (DONE 2026-09-05)

Built as `py/alias-census`, output in `doc/alias-census.md`. Results are
summarized in the Context section above. What follows is the original spec,
kept because it records why the tool works the way it does.

Four bugs were found and fixed while validating it, each of which had reported
live aliases as dead. They are worth knowing because the next person to touch
shell-resolution code will hit them:

- `which "name"` with QUOTES suppresses tcsh's alias lookup and reports
  "Command not found" for a name that bare `which name` resolves. Quoting
  every probe reported 30 live alias-to-alias chains as dead.
- The probe must source the ALIAS FILE ITSELF, not only the login chain, or no
  alias-to-alias chain resolves at all.
- Splitting a resolved path on whitespace to test existence breaks app bundles:
  `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` is one
  filename containing spaces, and splitting reported a live Chrome as dead.
- An alias body's trailing `# comment` must be stripped before parsing the
  command word, or a stray quote glues itself to the word.

- Files: `py/alias-census` (new), output `doc/alias-census.md`
- What: for each alias, resolve its first token through the same chain a real
  shell would (alias, then function, then `$PATH`, then absolute path, with
  `$var` expansion) and classify:
  - `LIVE`: target resolves and exists
  - `DEAD`: target is an absolute path or app that no longer exists
  - `SHADOWED`: an earlier definition of a name redefined later in the file;
    tcsh never registers it. 16 such lines are already known (15 names, with
    `gpy3` defined three times). These are retired, never translated: nothing
    can be calling them today because they have never been reachable.
    The full list, already enumerated so step 2 need not rediscover it, as
    `name: lines (live one last)`: aaias 405 406; deck 253 254; drive 67 380;
    dstr 50 52; gpy3 460 461 462; kdir 476 485; omail 295 301; oopen 475 484;
    plan 204 538; ppf-server 366 367; remkae 399 400; spotify 477 486;
    toc 426 427; vs 458 546; weahter 401 402.
    Two of those names (`remkae`, `weahter`) are misspellings, which suggests
    the duplicate is a typo-fix pair rather than an intentional override, and
    the census should flag both members for Chris rather than silently keeping
    the later one.
  - `SHELL-ONLY`: needs the parent shell (`cd`/`setenv`/`source`/`history`)
  - `UNKNOWN`: needs human eyes
- Note: a naive probe I ran this session resolved only 7 of 121 distinct
  targets and could not follow alias-to-alias chains, so the census must
  expand `$mise`, `$gdrive` and friends from a sourced login env, and iterate
  to a fixed point. The "how many are dead" number is deliberately not
  asserted in this plan; step 2 produces it.
- Verify: hand-check 15 sampled rows across all four classes; LIVE plus DEAD
  plus SHADOWED plus SHELL-ONLY plus UNKNOWN equals 335 exactly (every alias LINE gets a class; the 16 SHADOWED ones are the difference between 335 lines and 319 live aliases).
- The census also covers the 57 scripts, on the same LIVE/DEAD axis. A script
  that shells out to a vanished binary is as dead as an alias that does, and
  `gg-deprecated` announces its own status in its filename. Scripts have a
  second signal aliases lack: `git log -1 --format=%ar <file>` gives a last
  touched date, so anything untouched for years and pointing at a dead target
  is a strong retire candidate.

### 3. Decide per alias: translate / keep / retire

- Files: `doc/alias-census.md` gains a `decision` column, reviewed by Chris
- Rules, in order:
  1. `SHELL-ONLY` becomes keep, but moved to a bash function file
     (`sh/functions-public.bash`) for bash and zsh, with the tcsh alias kept
     for tcsh. A script cannot `cd` its parent; this is physics, not
     preference. `sh/login-public.sh` lands here too: it is sourced at login
     rather than executed, so it stays a sourced file and gets a bash sibling
     only if Chris ever wants a bash login path.
  2. `DEAD` becomes retire: `# DEAD <date>: <original text>` plus `unalias`.
  3. Takes args, or multi-command, or has backticks: translate to
     `bash/<name>`.
  4. Trivial one-word target with no args: translate only if it earns a file.
     A pure abbreviation like `alias up "cd .."` is shell-only anyway.
- Verify: every one of the 335 rows (one per alias line) carries exactly one decision; Chris signs
  off on the census file before step 4 starts.

### 4. Translate in risk-ordered batches

Each batch is one commit, and therefore one `git revert` unit.

| batch | contents | approx n | risk |
|---|---|---|---|
| 4a | trivial one-word targets, no args | 2 | low |
| 4b | multi-command (`;`), no args | 69 | low-med |
| 4c | arg-taking `\!*` and `\!:*` (whole arglist to `"$@"`) | 23 | medium |
| 4d | arg-taking `\!:1` (positional to `"$1"`, arity checks) | 18 | high |
| 4e | backtick and `$var` dependent | 45 | high |
| 4f | no-shebang portable scripts: add `#!/bin/bash` only | 12 | very low |
| 4g | `#!/bin/sh` scripts retargeted to bash | 2 | very low |
| 4h | tcsh/csh scripts, real translation, excluding `tcsh/ocr` | 40 | medium |
| 4i | `tcsh/ocr` (281 lines, by itself) | 1 | high |

BATCH 4F IS DONE (2026-09-05), but on 10 files, not 12. Two of the twelve
turned out NOT to be portable, and `bash -n` did not catch either, because
both parse fine under bash and simply mean something else:

  tcsh/unspace-mvs  uses csh `>!`. Bash parses that as a redirect into a file
                    literally named `!`, then treats the intended filename as
                    an argument. Verified: `echo second >! /tmp/gt3.txt` under
                    bash creates `/tmp/!` and never writes gt3.txt. Adding a
                    bash shebang would make this script rename files off a
                    stale list. It needs `>!` rewritten to `>`, which is a
                    translation, so it belongs in batch 4h.
  tcsh/unzoom       calls `mi`, which is an ALIAS (mv -i), not a command. A
                    script cannot see the caller's aliases at all. Needs `mi`
                    replaced with `mv -i`, also a translation.

The lesson generalizes to every later batch: `bash -n` proves a file PARSES,
never that it MEANS the same thing. Batches 4g through 4i need behavioral
checks, not syntax checks.

The other ten got `#!/bin/bash` and were verified behaviorally, not just
syntactically: the four stdin filters (fix, reply, words, werds) produce
byte-identical output under bash and under tcsh, `ffix` still dedupes through
its sibling `fix`, and `lgit` still prints the right GitHub URL.

BATCH 4A IS ESSENTIALLY EMPTY, and the reason generalizes. Recomputed against
the current 305-line file it holds 37 candidates rather than the 50 estimated
from the pre-retirement count. Of those:

  29  TYPO CATCHERS. opne, oepn, poen and oopen for `open`; mdkdir, mdkir,
      mkddir and kdir for `mkdir`; fidn, duff, moer, mroe, mor, gttp, pcbopy,
      pbpate, remkae and the rest. THESE MUST STAY ALIASES. A typo alias works
      precisely because the shell resolves it before anything else; as a
      script in bash/ a mistyped command would fork a subprocess instead of
      correcting to the intended one, which is slower and changes what the
      typo means. They are a KEEP tier, not a translate tier.
   2  ALREADY MARKED SHELL-ONLY. pu and cd-f, plus uppu which the typo
      heuristic also flagged; all three are recorded KEEP in the census
      because they leave the caller in a different directory.
   2  sudo WRAPPERS. `please` and `porfa` are both bare `sudo`. Wrapping sudo
      in a script interposes a process between the terminal and the password
      prompt, so these stay aliases too.
   2  CHAIN TO ANOTHER ALIAS. `deck` calls `onion`, `spot` calls `spotify`.
      They cannot become scripts before their targets do, which is the
      dependency ordering the CHAIN class exists to enforce.
   2  GENUINELY TRANSLATABLE. `g` calls `gsearch` and `oct` calls `ocr`, both
      of which are real scripts already on PATH.

The rule this establishes, which applies to every later batch: an alias whose
NAME is a misspelling of its own TARGET is a keyboard correction, not an
abbreviation, and translating it is a category error. The same goes for
anything wrapping sudo or a program that reads from the terminal.

Batch 4f was the cheapest win in the whole project and went first, ahead
of even 4a: 12 files, no translation, one line added to each, and the result
is strictly more correct than today because those scripts currently depend on
the caller's shell. Batch 4g is nearly as cheap.

Batch 4i gets its own commit because `tcsh/ocr` is 281 lines, roughly a third
of all non-alias script content, and is the one file where a translation bug
is most likely to hide. If it turns out to be dead or superseded (Chris has
`tcsh/ocr` and CLAUDE.md references `mise/tcsh/ocr` for PDF OCR, so it is
probably live), it still gets translated rather than retired.

- Per alias: write `bash/<name>` (with `set -u` and a "why this exists" header
  in the house style of `bash/subcommand-dispatch`), replace the alias with
  `unalias <name>` plus the original text as a comment, re-run the harness,
  confirm the golden capture still matches.
- 4d is flagged high because `\!:1` silently expands to empty when the user
  supplies no argument, and a bash `"$1"` does the same. This is the
  silent-failure class that caused today's `gcal` bug. Every 4d script gets an
  explicit arity check that fails loudly.
- Verify per batch: full harness green, plus `for n in <batch>; do tcsh -c
  "source aliases; which $n"; done` shows each resolving to `bash/<name>`.
- Verify for script batches (4f through 4i): `head -1` shows `#!/bin/bash`,
  the file is executable, and `bash -n <file>` parses clean.

### 4j. Directory naming, last and optional

Once no tcsh or csh remains, the `csh/` and `tcsh/` directory names are lies.
Leaving them is harmless (they are on `$PATH` and the contents are bash by
then). Renaming them is a `$PATH` change in the dotfiles, which is seiton
work and outside this plan's scope. Deliberately deferred, not forgotten.

### 5. Regression test and repo hygiene

- Files: `test/test_alias_migration.py`
- What: assert (a) no alias in `sh/aliases-public.sh` shadows a script of the
  same name in `bash/`, (b) every `bash/` script added by this plan is
  executable and has a shebang, (c) the golden harness passes.
- Red/green it the way `test_subcommand_dispatch.py` was: confirm it FAILS
  against the pre-migration tree before trusting it.
- Verify: `python3 test/test_alias_migration.py` green; run from a clean
  checkout too.

## Rollback

Three independent levels, cheapest first:

1. One alias misbehaves: un-comment its original line in
   `sh/aliases-public.sh`. The alias text was never deleted, so this is a
   one-line edit. The new `bash/<name>` script can stay; the alias wins by
   shell precedence.
2. One batch is bad: `git revert <batch commit>`. Batches are sized so this is
   always a clean revert.
3. Abandon the migration: `git revert` the batch commits in reverse order.
   `csh/` and `tcsh/` were never deleted, so the original scripts are still on
   disk and still on `$PATH`.

The 26 live tcsh sessions do not pick up alias-file changes until they are
restarted, so a bad batch cannot break a shell Chris already has open. New
shells get the new behavior. That is a safety property worth preserving: do
not add anything that re-sources aliases into running shells.

## Risks

- Silent-empty-argument bugs (highest). See 4d above. Mitigation: arity checks
  in every 4d script, and the harness captures a no-argument invocation for
  each arg-taking alias.
- Golden captures encode current bugs as correct. If an alias is already
  broken, the harness will faithfully preserve the breakage. Mitigation: the
  census (step 2) runs first and marks dead targets, so known-broken aliases
  are retired rather than lovingly reproduced.
- Env-dependent aliases. 47 reference `$` vars set at login. A script gets a
  fresh env and may not see them. Mitigation: those scripts source a small
  shared env preamble, or hardcode the resolved path; decided per alias in
  step 3.
- Startup cost. Replacing 300 aliases with 300 `$PATH` lookups is slightly
  slower per command but faster at shell startup. Not expected to matter;
  worth one measurement in step 4a.
- Concurrent sessions. Today's push hit exactly this: another session had
  uncommitted work in the same file, and `git commit -- <pathspec>` swept it
  in because a pathspec commit ignores the index. For every batch commit here:
  check `git diff` for foreign hunks, stage with `git apply --cached`, and
  commit with no pathspec so the index is what lands.
- Scope. 305 live aliases plus 57 scripts (1828 lines of script) is genuinely
  large. If the census shows most are dead, this shrinks a lot. If it shows
  most are live, this is a multi-session project and should be run batch by
  batch, not in one sitting. Note that 14 of the 57 scripts (the 12 portable
  no-shebang files plus the 2 posix-sh ones) need a shebang line rather than a
  translation, so the real translation surface is 41 scripts, and 2 of those
  are already bash.
- Directory names mislead. `sh/` is not POSIX sh, and after this migration
  `csh/` and `tcsh/` will hold bash. Any future work in this repo should read
  the shebang, never trust the directory. Worth a line in the repo README at
  the end.

## Out of Scope

- `~/gd/local/seiton/sh/aliases-private.sh` (about 5000 lines). Same treatment
  later, once this machinery is proven on the smaller public file.
- The dotfiles themselves (`.tcshrc`, `.login`) and switching Chris's
  interactive shell away from tcsh. This plan makes commands shell-agnostic;
  it does not change which shell he types into.
- `sh/login-public.sh` beyond whatever a translated alias strictly requires.
- Deleting anything. Explicitly forbidden by the requirement.
- Rewriting the 117 existing `bash/` scripts.
