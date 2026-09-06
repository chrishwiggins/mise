#!/usr/bin/env python3
"""Record the command line every alias in a tcsh alias file expands to, so a
bash migration can prove it did not change anything.

Written 2026-09-05 for doc/plan-tcsh2bash.md step 1, which makes this a hard
gate: batches 4a through 4e may not start until captures exist and are
committed, because once an alias is edited its original text is unrecoverable
except from git.

THIS PARSES. IT DOES NOT EXECUTE.

The first version of this harness ran each alias in tcsh under a stubbed PATH.
That was the wrong design, and every one of these came out of it:

  - `palias` is `echo "alias \\!*" >> $paliases`, and login-public.sh sets
    $paliases to aliases-public.sh itself. Running it APPENDED SIX LINES TO
    THE ALIAS FILE BEING CAPTURED. Recovered with git checkout, and only
    because the file happened to be committed minutes earlier.
  - `pip3-tend` chains to `pip3s` in a private alias file, which writes
    $cwaux/pip3-<timestamp>.asc. A capture run left 29 junk files in that
    directory. A guard inspecting the invoked alias body cannot see a
    redirect two aliases away.
  - `htm2pdf` and `htm2png` invoke Chrome by absolute path, which no stub PATH
    can intercept. Real headless Chrome ran and left screenshot.png and
    output.pdf in the repo root.
  - Sandboxing HOME to contain those writes broke the login chain, so only
    1128 of 3109 aliases registered and 226 of 305 captures came back
    "Command not found": a baseline full of failures that still looked valid.
  - 46 alias names also appear as words inside other alias bodies, so a stub
    named after an alias SHADOWED it and `spotify` captured "CMD spotify"
    rather than "open /Applications/Spotify.app/".

None of that is possible here. Answering "what does this alias run" needs the
alias body with its history markers substituted, which is a text
transformation. So this reads the file and expands strings. No subprocess, no
stubs, no writes, no browser, and it finishes in under a second instead of
five minutes, which is what makes it cheap to iterate on.

WHAT A CAPTURE IS

For each alias, the expansion with no arguments and, when the body takes
arguments, the expansion with fixed probe arguments. Chains are deliberately
NOT resolved: `pbdate` records `datestr| pbcopy`, not whatever `datestr`
bottoms out in. For a migration baseline that is the more useful record, since
it names the thing that still has to be translated.

Substitution rules, verified against tcsh rather than assumed:

    \\!*      all arguments          `a1 AA BB` -> `star AA BB`
    \\!:*     all arguments          same as \\!*
    \\!:N     argument N             `a3 AA BB` -> `one AA`
    \\!:1:r   argument 1, no suffix  `dir/file.txt` -> `dir/file`
    \\!:1:t   argument 1, basename   `dir/file.txt` -> `file.txt`

With NO arguments the two forms differ, and the difference is the whole point
of capturing the empty case: `\\!*` expands to nothing and the command runs
anyway, while `\\!:1` fails with "Bad ! arg selector." A bash translation of a
`\\!:1` alias must reject a missing argument rather than silently passing an
empty string, which is precisely the silent-failure class that started this
migration.

Usage:
  alias-golden.py                 capture to the golden dir (see below)
  alias-golden.py --check         re-expand and diff against what is stored
  alias-golden.py --alias NAME    print one alias, write nothing
  alias-golden.py --file FILE     use a different alias file
  alias-golden.py --golden-dir D  read and write captures in D

Captures are FIXTURES: each is an expansion of one particular person's aliases,
while this file is a general csh-expansion tool, so keep them apart. Locate them
with --golden-dir, which beats $ALIAS_GOLDEN_DIR, which beats a repo-local
default.

Exit: 0 if captures were written, or if --check found no differences; 1 if
--check found a difference; 2 if --check found no capture directory at all.
"""
import os
import re
import sys

MISE = os.path.expanduser('~/mise')
DEFAULT_ALIASES = os.path.join(MISE, 'sh/aliases-public.sh')

# Captures are FIXTURES, not tool. Each is an expansion of one particular
# person's aliases, while this file is a general csh-expansion tool, so the
# two should not live together. Point $ALIAS_GOLDEN_DIR (or --golden-dir) at
# wherever the captures are kept; this repo names no location outside itself.
# The fallback is repo-local so the tool works standalone out of a fresh
# checkout. Absent captures affect only --check, which has nothing to compare.
DEFAULT_GOLDEN_DIR = os.path.join(MISE, 'dat/alias-golden')
GOLDEN_DIR = os.environ.get('ALIAS_GOLDEN_DIR') or DEFAULT_GOLDEN_DIR

ALIAS_RE = re.compile(r'^alias\s+(\S+)\s+(.*)$')

# Fixed and meaningless on purpose: a capture must not depend on a file that
# exists today and not tomorrow.
PROBE_ARGS = ['ARG1', 'ARG2']

# tcsh's error when \!:N is used and argument N was not supplied. Reproduced
# verbatim so the capture records the real failure, not a paraphrase.
BAD_SELECTOR = 'Bad ! arg selector.'

# \!:N with optional :r (strip suffix) or :t (basename) modifiers, and \!:*
# or \!* for the whole argument list.
MARKER_RE = re.compile(r'\\!(?::(\d+)((?::[rte])*)|:\*|\*)')


def apply_modifiers(value, mods):
    """Apply csh word modifiers. `:r` strips the last suffix, `:t` takes the
    basename, `:e` keeps only the suffix. They chain left to right."""
    for mod in re.findall(r':([rte])', mods or ''):
        if mod == 'r':
            value = value.rsplit('.', 1)[0] if '.' in value else value
        elif mod == 't':
            value = value.rsplit('/', 1)[-1]
        elif mod == 'e':
            value = value.rsplit('.', 1)[1] if '.' in value else ''
    return value


def expand(body, args):
    """Substitute history markers in an alias body.

    Returns the expanded string, or BAD_SELECTOR if the body asks for a
    positional argument that was not supplied, matching what tcsh prints.
    """
    failed = []

    def sub(m):
        n, mods = m.group(1), m.group(2)
        if n is None:                      # \!* or \!:*, the whole list
            return ' '.join(args)
        i = int(n)
        if i < 1 or i > len(args):
            failed.append(i)
            return ''
        return apply_modifiers(args[i - 1], mods)

    out = MARKER_RE.sub(sub, body)
    return BAD_SELECTOR if failed else out


def strip_quotes(body):
    """Remove one matched layer of surrounding quotes, and any trailing
    comment outside them, so the recorded line is the command itself."""
    b = body.strip()
    if len(b) >= 2 and b[0] in '"\'' and b[-1] == b[0]:
        return b[1:-1]
    # An unmatched trailing quote means a comment followed it on the line.
    if len(b) >= 2 and b[0] in '"\'':
        end = b.rfind(b[0])
        if end > 0:
            return b[1:end]
    return b


def takes_args(body):
    return bool(MARKER_RE.search(body))


def read_aliases(path):
    """[(name, body)] for the LAST definition of each name, which is the one
    tcsh registers. An earlier definition never runs, so recording it would
    capture something nobody can invoke."""
    last, order = {}, []
    with open(path, errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('#') or not line.strip():
                continue
            m = ALIAS_RE.match(line)
            if m:
                name, body = m.group(1), m.group(2)
                if name not in last:
                    order.append(name)
                last[name] = body
    return [(n, last[n]) for n in order]


def capture_all(alias_file, only=None):
    results = {}
    for name, body in read_aliases(alias_file):
        if only and name != only:
            continue
        clean = strip_quotes(body)
        parts = [f'$ {name}', expand(clean, [])]
        if takes_args(clean):
            parts.append(f'$ {name} {" ".join(PROBE_ARGS)}')
            parts.append(expand(clean, PROBE_ARGS))
        results[name] = '\n'.join(parts)
    return results


def safe_filename(name):
    """An alias name may contain characters that are unsafe in a path."""
    return re.sub(r'[^A-Za-z0-9_.-]', lambda m: f'%{ord(m.group()):02x}', name)


def main():
    global GOLDEN_DIR
    argv = sys.argv[1:]
    alias_file = DEFAULT_ALIASES
    if '--file' in argv:
        alias_file = os.path.abspath(argv[argv.index('--file') + 1])
    if '--golden-dir' in argv:
        GOLDEN_DIR = os.path.abspath(argv[argv.index('--golden-dir') + 1])
    only = argv[argv.index('--alias') + 1] if '--alias' in argv else None

    results = capture_all(alias_file, only)

    if only:
        for text in results.values():
            print(text)
        return 0

    if '--check' in argv:
        # Distinguish "captures are missing" from "captures disagree". Without
        # this, a checkout that lacks the private fixture dir reports all 303
        # aliases as NEW, which reads like catastrophic drift.
        if not os.path.isdir(GOLDEN_DIR):
            print(f'no captures at '
                  f'{GOLDEN_DIR.replace(os.path.expanduser("~"), "~")}')
            print('nothing to check against; set $ALIAS_GOLDEN_DIR or pass '
                  '--golden-dir')
            return 2
        bad = 0
        for name, text in sorted(results.items()):
            p = os.path.join(GOLDEN_DIR, safe_filename(name) + '.golden')
            if not os.path.exists(p):
                print(f'  NEW      {name}')
                bad += 1
                continue
            if open(p).read().strip() != text.strip():
                print(f'  CHANGED  {name}')
                bad += 1
        stored = ({f[:-7] for f in os.listdir(GOLDEN_DIR)
                   if f.endswith('.golden')}
                  if os.path.isdir(GOLDEN_DIR) else set())
        for gone in sorted(stored - {safe_filename(n) for n in results}):
            print(f'  REMOVED  {gone}')
            bad += 1
        print(f'{len(results)} aliases checked, {bad} differing.')
        return 1 if bad else 0

    os.makedirs(GOLDEN_DIR, exist_ok=True)
    for name, text in results.items():
        p = os.path.join(GOLDEN_DIR, safe_filename(name) + '.golden')
        with open(p, 'w') as f:
            f.write(text.strip() + '\n')
    print(f'wrote {len(results)} captures to '
          f'{GOLDEN_DIR.replace(os.path.expanduser("~"), "~")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
