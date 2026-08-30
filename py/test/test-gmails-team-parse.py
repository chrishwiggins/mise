#!/usr/bin/env python3
"""Regression: parse_team_file must NOT treat "## Inboxes" addresses as members.

2026-08-25: listing the default account under "## Inboxes" in a project TEAM.md
(as the /inbox command's own example showed) made gmails inbox search
from:<own address> OR to:<own address> and pull 100 unrelated personal messages
into the project's eml/inbox. The warning prose in the /inbox command had not
prevented a recurrence; this test pins the tool behavior instead.

Run: py/.venv/bin/python3 py/test/test-gmails-team-parse.py  (from the mise repo root;
the tool re-execs into that venv anyway, and macOS has no /usr/bin/timeout to guard it)
"""

import importlib.util
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "gmail-api-rw"

spec = importlib.util.spec_from_loader("gmails_mod", loader=None)
mod = importlib.util.module_from_spec(spec)
mod.__file__ = str(TOOL)  # the tool's venv-reexec preamble reads __file__
src = TOOL.read_text()
# Execute only up to the CLI entry so importing has no side effects.
cut = src.find('if __name__ ==')
exec(compile(src[:cut] if cut > 0 else src, str(TOOL), "exec"), mod.__dict__)

TEAM_MD = """# Team

## Alice Example

- Email: alice@example.org

## Bob Sample

- Email: bob@sample.net
- Also reachable at bob.sample@work.net

## Inboxes

- owner@example.com
- owner.second@example.com (alias)

## Notes

Stray mention of carol@notes.example in prose is still a member (fallback).

## Dave Sourced

- Email: dave@sourced.example
- Source: email 2026-07-09 to owner@example.com
- Notes: letter arrived at owner.second@example.com
"""

with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
    f.write(TEAM_MD)
    path = f.name

team = mod.parse_team_file(path)
emails = {addr for _, addr in team}

failures = []
if "owner@example.com" in emails or "owner.second@example.com" in emails:
    failures.append("Inboxes account addresses were parsed as team members "
                    "(second bite 2026-08-25: they appeared in a member's Source/Notes lines)")
for expected in ("alice@example.org", "bob@sample.net", "bob.sample@work.net", "carol@notes.example", "dave@sourced.example"):
    if expected not in emails:
        failures.append(f"expected member missing: {expected}")

if failures:
    for msg in failures:
        print("FAIL:", msg)
    print("parsed:", sorted(emails))
    sys.exit(1)
print(f"OK: {len(emails)} members parsed, Inboxes accounts excluded")
