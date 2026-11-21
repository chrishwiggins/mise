# prj: Installation and Setup

## Prerequisites

prj requires:

- macOS (uses iTerm2 and AppleScript)

- iTerm2 (3.4+)

- Bash 4.0+

- Claude Code installed and in PATH

## Installation

1. Add mise/bash to your PATH

Ensure ~/mise/bash is in your shell's PATH. Add to ~/.zshrc or ~/.bashrc:

```bash
export PATH="$HOME/mise/bash:$PATH"
```

2. Verify prj is accessible

```bash
which prj
```

Should print: /Users/wiggins/mise/bash/prj (or similar mise path)

3. First run

```bash
prj
```

If no projects are registered yet, prj creates ~/.config/prj/projects.json
and shows an empty list. This is normal.

## Companion Tools

prj depends on these tools in mise/bash/:

- tc: iTerm2 color and window control

- Optionally, claude-statusline for colored statusline indicators

Verify they are accessible:

```bash
which tc
which claude-statusline
```

If not in PATH, add ~/mise/bash to PATH as above.

## Configuration

No configuration file is needed. prj uses:

- ~/.config/prj/projects.json: registry of projects (created automatically)

- ~/.claude/projects/: session transcripts (created by Claude Code)

Do not edit projects.json by hand; use prj commands instead.

## Troubleshooting

### "prj: command not found"

Ensure ~/mise/bash is in PATH:

```bash
echo $PATH | grep mise
```

If not present, add it to your shell config and source it:

```bash
source ~/.zshrc
```

### "iTerm2 not running"

prj requires iTerm2 to be open. Start it and try again.

### Process detection not working

If prj shows "session already running" but you cannot find the window:

```bash
pgrep -f "claude --resume"
```

Lists all running Claude sessions. Use `tc which <session-id>` to find
the window coordinates.

### Colors not applying

Colors apply only when prj launches a NEW window. Existing windows keep
their old colors until recolored with:

```bash
tc -t <tty> <color>
```

Replace <tty> with the pane's tty (e.g., ttys003) and <color> with a
color from `tc` bare listing.

## See Also

- mise/agents/prj/AGENTS.md: entry points and assumptions

- mise/agents/prj/EXAMPLES.md: usage examples

- mise/bash/tc: color specifications
