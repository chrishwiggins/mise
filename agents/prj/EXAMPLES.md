# prj: Usage Examples

## Basic Workflow

### Register a New Project

```bash
prj -new research ~/projects/research sage
prj -new writing ~/Documents/book crimson
prj -new startup ~/work/startup coral
```

The slug (research, writing, startup) is the project identifier.
Directory paths are expanded relative to the current directory.
Colors use the tc color palette (run `tc` to see available colors).

### Launch a Project

```bash
prj research
```

This:

- Finds the most recent session for the research project

- Launches Claude Code with that session in an iTerm2 window

- Applies the project's color (sage) to the window tabs

- If the session is running but hidden, automatically raises that window

### List All Projects

```bash
prj
```

Output: human-readable table showing:

- Project slug

- Color specification

- Last-used timestamp

- Directory path

- Number of sessions

### View Sessions for a Project

```bash
prj -ls research
```

Output: table of sessions with:

- Session UUID

- Last modified time

- Message count

- Marker (*) for the auto-resume target

## Scripting Workflows

### From a Script: Get Project Directory

```bash
#!/bin/bash
dir=$(prj --cd-path myproject)
if [ $? -ne 0 ]; then
  echo "Project not found" >&2
  exit 1
fi
cd "$dir"
echo "Working in: $(pwd)"
```

The `--cd-path` flag outputs only the absolute path, safe for scripts.

### Check If a Project Exists

```bash
if prj -ls myproject > /dev/null 2>&1; then
  echo "Project exists"
else
  echo "Project not registered"
fi
```

prj exits 0 on success, 1 on failure.

### Register Projects from a List

```bash
while IFS=',' read slug dir color; do
  if ! prj -ls "$slug" > /dev/null 2>&1; then
    prj -new "$slug" "$dir" "$color"
  fi
done < projects.csv
```

Where projects.csv contains:

```
research,~/projects/research,sage
writing,~/Documents/book,crimson
startup,~/work/startup,coral
```

## Advanced: Alias for cd'ing to a Project

Create an alias in your shell config:

```bash
alias prj-cd='eval cd \`prj --cd-path \!*\`'
```

(tcsh syntax; Bash uses `${!}` instead of `\!*`)

Usage:

```bash
prj-cd research
```

Now you are in the research project directory.

## Color Specifications

Colors apply when prj launches a NEW window. Use single colors or
hyphen-delimited specs for multiple tabs:

- `sage`: all tabs colored sage

- `blue-gold`: tab 1 (Claude) blue, tab 2 (shell) gold

- `crimson-sage-blue`: three tabs with respective colors

List available colors:

```bash
tc
```

## Editing a Project

Change a project's color or directory:

```bash
prj -edit research color=blue
prj -edit research dir=~/projects/research-new
```

Changes take effect at the next launch.

## Removing a Project

```bash
prj -rm research
```

This removes the project from the registry but does not delete files
or session transcripts.

## Session Management

### Fresh Session for a Project

By default, prj resumes the most recent session. Force a fresh session:

```bash
prj -0 research
```

This launches a new Claude Code instance for the project, leaving the
old session intact.

### Find a Hidden Session

If prj reports a session is running but you cannot find the window:

```bash
pgrep -f "claude --resume"
```

Lists running sessions. To bring one to focus:

```bash
tc which <session-uuid>
```

Shows the window and tab coordinates. Then:

```bash
tc focus win.tab
```

Raises that window to the foreground.

## Integrating with Agents

Agents can use prj to manage projects programmatically:

```bash
# 1. Check if a project exists
if prj -ls myproject > /dev/null 2>&1; then
  echo "Project exists"
else
  echo "Registering new project..."
  prj -new myproject ~/my/project sage
fi

# 2. Get the directory
dir=$(prj --cd-path myproject)
cd "$dir"

# 3. Count sessions
count=$(prj -ls myproject | tail -n +2 | wc -l)
echo "Found $count session(s)"
```

## See Also

- mise/agents/prj/AGENTS.md: entry points and command reference

- mise/agents/prj/INSTALL.md: setup and prerequisites

- mise/bash/tc: window colors and control
