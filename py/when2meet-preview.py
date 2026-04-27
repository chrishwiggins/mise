#!/usr/bin/env python3
"""
When2Meet Preview - Shows what time slots would be created

Usage: cat dates.txt | when2meet-preview.py [chunk_minutes]
"""

import sys
import re
from datetime import datetime, timedelta
from typing import List, Tuple


def parse_time_ranges(input_text: str) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """Parse input text to extract date and time ranges."""
    date_ranges = []

    for line in input_text.strip().split("\n"):
        if not line.strip():
            continue

        # Parse date part (e.g., "mon 15 sep" or "wed 17 sep")
        date_match = re.match(r"^(\w+\s+\d+\s+\w+)\s+(.+)$", line, re.IGNORECASE)
        if not date_match:
            continue

        date_str = date_match.group(1)
        time_part = date_match.group(2)

        # Parse time ranges (e.g., "09.00-10.00, 10.30-11.30")
        time_ranges = []
        for time_range in time_part.split(","):
            time_match = re.match(
                r"(\d+[.:]\d+)\s*-\s*(\d+[.:]\d+)", time_range.strip()
            )
            if time_match:
                start_time = time_match.group(1).replace(".", ":")
                end_time = time_match.group(2).replace(".", ":")
                time_ranges.append((start_time, end_time))

        if time_ranges:
            date_ranges.append((date_str, time_ranges))

    return date_ranges


def generate_time_chunks(
    date_ranges: List[Tuple[str, List[Tuple[str, str]]]], chunk_minutes: int = 30
) -> List[str]:
    """Generate time chunks based on the parsed date ranges."""
    time_slots = []

    for date_str, time_ranges in date_ranges:
        for start_str, end_str in time_ranges:
            # Parse times
            start_hour, start_min = map(int, start_str.split(":"))
            end_hour, end_min = map(int, end_str.split(":"))

            # Create datetime objects for easier manipulation
            start_time = datetime(2025, 1, 1, start_hour, start_min)
            end_time = datetime(2025, 1, 1, end_hour, end_min)

            # Generate chunks
            current = start_time
            while current < end_time:
                next_time = min(current + timedelta(minutes=chunk_minutes), end_time)
                slot_str = f"{date_str} {current.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                time_slots.append(slot_str)
                current = next_time

    return time_slots


def main():
    # Parse command line arguments
    chunk_minutes = 30  # Default
    if len(sys.argv) > 1:
        try:
            chunk_minutes = int(sys.argv[1])
        except ValueError:
            print(f"Invalid chunk size: {sys.argv[1]}")
            sys.exit(1)

    # Read input from stdin
    if sys.stdin.isatty():
        print("Error: No input provided. Pipe data to this script:")
        print("  cat dates.txt | when2meet-preview.py [chunk_minutes]")
        sys.exit(1)

    input_text = sys.stdin.read()

    # Parse date/time ranges
    date_ranges = parse_time_ranges(input_text)

    if not date_ranges:
        print("Error: No valid date/time ranges found in input")
        sys.exit(1)

    # Generate time chunks
    time_slots = generate_time_chunks(date_ranges, chunk_minutes)

    if not time_slots:
        print("Error: No time slots generated")
        sys.exit(1)

    print(
        f"PREVIEW: Would create {len(time_slots)} time slots with {chunk_minutes}-minute chunks:"
    )
    print("=" * 60)
    for i, slot in enumerate(time_slots, 1):
        print(f"{i:2}. {slot}")

    print("=" * 60)
    print("\nGoogle Form would have:")
    print("1. Name field (required)")
    print("2. Checkbox question with all these time slots")
    print("3. Public access for responses and viewing results")


if __name__ == "__main__":
    main()
