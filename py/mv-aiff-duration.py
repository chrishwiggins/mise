#!/usr/bin/python3
"""
Rename AIFF Audio Files to Include Duration in Filename

This script scans the current directory for AIFF audio files named "chapter_N.aiff",
extracts their duration using exiftool, and renames them to "ch_N_HHMMSS.aiff"
where HHMMSS is the duration in hours, minutes, and seconds.

Useful for organizing audiobook chapters or podcast segments by length.

Requires: exiftool installed (brew install exiftool)
"""

import os
import re
import subprocess

for filename in os.listdir("."):
    if filename.startswith("chapter_") and filename.endswith(".aiff"):
        # Extract chapter number from filename
        chapter_number = re.search(r"chapter_(\d+)", filename).group(1)

        # Get duration using exiftool
        output = subprocess.check_output(["exiftool", filename])
        duration_match = re.search(
            r"Duration\s*:\s*(\d+:\d+:\d+|\d+:\d+|\d+\.\d+)", output.decode()
        )
        if duration_match:
            duration = duration_match.group(1)
            if "." in duration:
                seconds = float(duration)
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds = int(seconds % 60)
                duration = f"{hours:02d}{minutes:02d}{seconds:02d}"
            else:
                duration_parts = duration.split(":")
                if len(duration_parts) == 3:
                    hours, minutes, seconds = map(int, duration_parts)
                    duration = f"{hours:02d}{minutes:02d}{seconds:02d}"
                elif len(duration_parts) == 2:
                    minutes, seconds = map(int, duration_parts)
                    duration = f"00{minutes:02d}{seconds:02d}"
                else:
                    seconds = int(duration_parts[0])
                    minutes = seconds // 60
                    seconds = seconds % 60
                    duration = f"00{minutes:02d}{seconds:02d}"
        else:
            print(f"Failed to extract duration from {filename}")
            continue

        # Rename file
        new_filename = f"ch_{chapter_number}_{duration}.aiff"
        os.rename(filename, new_filename)
        print(f"Renamed {filename} to {new_filename}")
