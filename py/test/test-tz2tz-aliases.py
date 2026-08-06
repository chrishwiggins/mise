#!/usr/bin/env python3
"""Tests for tz2tz: CODE_ALIASES integrity and am/pm conversion.

Run directly (python3 test-tz2tz-aliases.py) or via pytest.
"""
import importlib.util
import sys
from datetime import datetime
from importlib.machinery import SourceFileLoader
from pathlib import Path

TZ2TZ_PATH = Path(__file__).resolve().parent.parent / "tz2tz"

# The script has no .py extension, so name a loader explicitly
spec = importlib.util.spec_from_file_location(
    "tz2tz", TZ2TZ_PATH, loader=SourceFileLoader("tz2tz", str(TZ2TZ_PATH))
)
tz2tz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tz2tz)


def test_alias_targets_exist():
    """Every CODE_ALIASES target must be a real airport in airportsdata."""
    missing = {
        alias: target
        for alias, target in tz2tz.CODE_ALIASES.items()
        if target not in tz2tz.AIRPORTS
    }
    assert not missing, f"alias targets not in airportsdata: {missing}"


def test_aliases_do_not_shadow_real_codes():
    """No alias key may collide with a real airport code; resolve_code
    checks AIRPORTS first, so a collision would make the alias dead and
    misleading (the SAO/BER lesson)."""
    shadowed = sorted(
        alias for alias in tz2tz.CODE_ALIASES if alias in tz2tz.AIRPORTS
    )
    assert not shadowed, f"aliases shadowed by real airport codes: {shadowed}"


def test_resolve_code():
    assert tz2tz.resolve_code("NYC") == "JFK"
    assert tz2tz.resolve_code("nyc") == "JFK"
    assert tz2tz.resolve_code("JFK") == "JFK"
    assert tz2tz.resolve_code("XXQZ") == "XXQZ"  # unknown passes through


def test_ampm_meridiem_converts():
    """9:00am Tokyo is 8:00pm the previous day in New York; the suffix
    must flip to pm, keeping the input's lowercase style."""
    date = datetime(2026, 8, 6)  # fixed date: JST +9, EDT -4
    assert tz2tz.convert_time("9:00am", "HND", "JFK", date=date) == "08:00pm (-1d)"
    assert tz2tz.convert_time("9:00AM", "HND", "JFK", date=date) == "08:00PM (-1d)"


def test_ampm_same_meridiem_preserved():
    date = datetime(2026, 8, 6)  # JFK -4, LHR +1
    assert tz2tz.convert_time("9:00am", "JFK", "LHR", date=date) == "02:00pm"


def test_24h_stays_24h():
    date = datetime(2026, 8, 6)
    assert tz2tz.convert_time("14:30", "JFK", "LHR", date=date) == "19:30"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
