# prj: Agent Integration Guide

For agents: how to integrate prj into workflows.

## What is prj?

prj is a project launcher for iTerm2 and Claude Code. It manages:

- Project directory registry (projects.json in ~/.config/prj/)

- Claude session resumption for projects

- iTerm window/tab lifecycle with colored titlebar indicators

- Auto-focus of hidden sessions via process detection

## Entry Points for Agents

### Get a Project Directory

```bash
dir=$(prj --cd-path <slug>)
cd "$dir"
```

Returns the absolute path for a registered project. Safe for scripts.
Exits 1 if the slug is not found.

### List All Registered Projects

```bash
prj
```

Output: human-readable table with:

- slug

- color

- last-used time

- directory path

Not machine-parseable; use `prj -ls <slug>` for structured session data.

### List Sessions for a Project

```bash
prj -ls <slug>
```

Output: table with:

- session IDs (UUIDs)

- modification time

- message count

- marker for auto-resume target

The session marked with `*` is the one that `prj <slug>` will resume.

### Register a New Project

```bash
prj -new <slug> <directory> <color>
```

Requires:

- slug: matches [A-Za-z0-9._@-]+

- directory: absolute or relative path (expanded to absolute)

- color: a color name recognized by tc (companion tool)

### Remove a Project

```bash
prj -rm <slug>
```

Removes from registry but does not delete any files or sessions.

## Assumptions

- prj assumes iTerm2 is running (macOS only)

- Project slugs are unique in ~/.config/prj/projects.json

- Sessions are stored in ~/.claude/projects/<mangled-path>/ where
  <mangled-path> replaces all non-alphanumeric chars with hyphen

- prj always resumes the most-recent session by file mtime

- Colors use tc, a companion tool in mise/bash/tc

- Process detection via `pgrep -f "claude --resume <uuid>"` to find
  hidden sessions

## Companion Tools

- tc: iTerm2 color and window control (mise/bash/tc)

- tc which: map session UUID to window.tab coordinates

## Key Files (Not in Repo)

These files live in the user's home directory, never committed:

- ~/.config/prj/projects.json: registry of projects (slug, dir, color)

- ~/.claude/projects/<mangled-path>/*.jsonl: session transcripts

## Common Workflow from an Agent

```bash
# 1. Check if a project exists
if prj -ls myproject > /dev/null 2>&1; then
  dir=$(prj --cd-path myproject)
  cd "$dir"
else
  echo "Project not registered" >&2
  exit 1
fi

# 2. Find the session count
session_count=$(prj -ls myproject | grep -c '.')
echo "Found $session_count session(s)"

# 3. Register a new project if needed
if ! prj -ls newproject > /dev/null 2>&1; then
  prj -new newproject ~/my/project sage
fi
```

## Error Handling

- Error messages go to stderr

- Registry creation is automatic (~/.config/prj/projects.json)

- Invalid slugs are rejected before writing to registry

## See Also

- mise/doc/AGENTS.md: index of all agent-readable tools

- mise/agents/prj/INSTALL.md: setup and prerequisites

- mise/agents/prj/EXAMPLES.md: more detailed usage examples
