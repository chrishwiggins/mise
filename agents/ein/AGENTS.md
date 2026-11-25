# ein: Agent Integration Guide

For agents: how to drop a note into a project's ein/ inbox.

## What is ein?

ein writes one new file into `<project dir>/ein/`, the inbox a
later session triages. The content is either text given on the
command line (a prompt, a URL) or the macOS clipboard. The project
is named by a prj slug, so any slug `prj` lists works. A prj alias
also works (for example `hackNY` for `hny`); a real slug wins over an
alias of the same name, as in prj.

## Entry Points

### Write text to a project's inbox

```bash
ein <slug> "summarize the thread with the vendor"
ein <slug> "https://example.org/page?a=1&b=2"
ein <slug> look at this # unquoted words joined with spaces
```

Quote URLs that contain `?`, `&` or `*`, or the shell will glob them
or background part of the line.

### Write the clipboard

```bash
ein <slug> # pbpaste into that project's inbox
ein # pbpaste into the project containing cwd
```

With no arguments, ein picks the deepest registered prj directory
that is cwd or one of its parents, and falls back to the git root.

### Help

```bash
ein -h
```

## Output

On success, one line on stdout:

```
<path> (<N> lines): <first 70 characters of line 1>
```

Files are named `YYYY-MM-DDTHHhMMmSSs` (for example
`2026-11-21T11h17m49s`); a second write in the same second gets
`-2`, `-3` and so on, so nothing is overwritten.

## Exit Codes

- 0: file written

- 1: unknown slug, registered dir missing, no prj project or git
  repo around cwd (no-argument form), or empty or whitespace-only
  content; nothing is written in any of these cases

## Assumptions

- macOS (`pbpaste`) and Bash 4+

- The first argument is always a slug, never a path: `ein .` fails
  as an unknown slug. Use bare `ein` for "the project I am in".

- The registry is `~/.config/prj/projects.json`, read directly;
  prj itself is not called.

## Test

```bash
bash ~/mise/test/ein.sh
```

Hermetic: a fake HOME registry and a stub pbpaste.

## See Also

- mise/agents/prj/AGENTS.md: the registry ein resolves slugs through
