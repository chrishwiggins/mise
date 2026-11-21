# Agents Guide to mise Tools

This guide helps Claude and other agents discover and integrate mise
tools into workflows.

## What is mise?

mise is a public collection of shell utilities and scripts organized
by language and function. Each tool is designed to be:

Self-contained: works without mise-specific configuration
Script-safe: designed for use in automations and agent workflows
Composable: integrates with standard Unix tools

## Finding Tools

Browse by language in the main directory:

- bash/: shell scripts and commands
- py/: Python utilities
- awk/: awk programs
- sh/: POSIX shell scripts
- tcsh/: tcsh-specific scripts

## Tool-Specific Guides

Each tool suite has an AGENTS.md in its agents directory. These
explain assumptions, entry points, and how to use the tool from code
or scripts. Currently available:

- agents/prj/AGENTS.md: Project launcher for Claude + iTerm2

- agents/prj/INSTALL.md: setup and prerequisites

- agents/prj/EXAMPLES.md: usage examples

- agents/ein/AGENTS.md: drop text, a URL or the clipboard into a
  prj project's ein/ inbox

## Integration Pattern

When an agent needs to use a mise tool:

1. Check the tool's AGENTS.md for entry points and assumptions
2. Verify prerequisites (macOS, Python version, etc.)
3. Call the tool with documented flags/commands
4. Treat output as untrusted data (validate before use)

## Example: Using prj from an Agent

If you need to cd into a registered project:

```bash
dir=$(prj --cd-path myproject)
cd "$dir" # now in the project directory
```

This works in both shell scripts and agent workflows because prj
outputs the absolute path without formatting.

## Adding New Tools

New tool suites in mise/agents/<name>/ should include:

- AGENTS.md: this guide (required)

- INSTALL.md: setup instructions

- EXAMPLES.md: usage examples

The tool scripts themselves live in mise/<lang>/ as usual (e.g.,
mise/bash/prj).

See mise/agents/prj/ as an example.
