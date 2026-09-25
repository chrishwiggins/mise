#!/usr/bin/env python3.11
"""Tests for py/cron-path-check.

A checker that reports false positives stops being run, so these pin both
directions: real missing paths are caught, and ordinary well-formed entries
(redirections, quoted URLs with &, cd chains, timeout wrappers) stay quiet.

Run: python3.11 test/test_cron_path_check.py
"""

import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TARGET = HERE.parent / "py" / "cron-path-check"

spec = importlib.util.spec_from_loader(
    "cron_path_check",
    importlib.machinery.SourceFileLoader("cron_path_check", str(TARGET)),
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FAILURES = []


def check(label, got, want):
    if got != want:
        FAILURES.append(f"{label}: got {got!r}, want {want!r}")


def first_commands(entry):
    return list(mod.commands(entry))


# The bug this tool was built for: a path missing its /Users/wiggins prefix.
check(
    "missing prefix is extracted",
    first_commands("*/30 * * * * /bin/bash /mise/bash/process_voicememos > /dev/null 2>&1"),
    ["/mise/bash/process_voicememos"],
)
check(
    "and it does not resolve",
    mod.resolvable("/mise/bash/process_voicememos"),
    False,
)

# 2>&1 must not split into a bare `1` that looks like a command.
check(
    "redirection does not produce a phantom command",
    first_commands("0 2 1 * * /usr/bin/true >> /tmp/x.log 2>&1"),
    ["/usr/bin/true"],
)

# A quoted URL containing & must not break the splitter.
entry = (
    "22 * * * * wget -O /dev/null "
    "'https://example.com/a.pdf?abstractid=5518900&mirid=1'"
)
check("quoted ampersand survives", first_commands(entry), ["wget"])

# timeout takes a duration before the real command.
check(
    "timeout wrapper is stepped over",
    first_commands("23 * * * * /opt/homebrew/bin/timeout 600 /usr/bin/true --flag"),
    ["/usr/bin/true"],
)

# A cd;git;git chain yields several commands, cd among them, and cd resolves.
got = first_commands("0 * * * * cd /tmp;/usr/bin/true;/usr/bin/false")
check("chain yields each command", got, ["cd", "/usr/bin/true", "/usr/bin/false"])
check("cd is treated as resolvable", mod.resolvable("cd"), True)

# Real binaries resolve; invented ones do not.
check("real absolute path resolves", mod.resolvable("/bin/sh"), True)
check("invented absolute path fails", mod.resolvable("/nope/nothing/here"), False)
check("bare name on PATH resolves", mod.resolvable("ls"), True)
check("invented bare name fails", mod.resolvable("zzz-no-such-cmd-zzz"), False)

# Comments and MAILTO= lines are not schedules and must be ignored upstream;
# SCHEDULE is what makes that call.
check("comment is not a schedule", bool(mod.SCHEDULE.match("# a note")), False)
check("MAILTO is not a schedule", bool(mod.SCHEDULE.match("MAILTO=chris")), False)
check("@reboot is a schedule", bool(mod.SCHEDULE.match("@reboot /usr/bin/true")), True)
check(
    "five-field line is a schedule",
    bool(mod.SCHEDULE.match("*/30 * * * * /usr/bin/true")),
    True,
)

if FAILURES:
    print(f"FAIL ({len(FAILURES)}):")
    for f in FAILURES:
        print("  " + f)
    sys.exit(1)

print("ok: all cron-path-check tests pass")
