#!/usr/bin/python3
"""
Download and Clean YouTube Video Transcripts

This script downloads auto-generated English transcripts from YouTube videos using
yt-dlp, then cleans them by removing timestamps, HTML tags, and duplicate lines.
The cleaned transcript is printed to stdout.

Usage: python3 yt-clean.py <YouTube_Video_ID>

Example: python3 yt-clean.py dQw4w9WgXcQ

Requires: yt-dlp installed (pip install yt-dlp)
"""

import os
import sys
import re
import subprocess
import tempfile


def download_transcript(video_id, temp_file_path):
    """Download the auto-generated transcript of a YouTube video using yt-dlp."""
    command = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang",
        "en",
        "--skip-download",
        "-o",
        temp_file_path,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error downloading transcript:", result.stderr)
        sys.exit(1)
    print(f"Transcript downloaded to {temp_file_path}")


def clean_transcript(temp_file_path):
    """Clean the downloaded transcript."""
    seen_lines = set()
    skip_header = True

    with open(temp_file_path, "r") as file:
        for line in file:
            if skip_header:
                if line.strip() == "":
                    skip_header = False
                continue

            if re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
                continue

            cleaned_line = re.sub(r"<[^>]+>", "", line).strip()

            if not cleaned_line:
                continue

            if cleaned_line in seen_lines:
                continue

            seen_lines.add(cleaned_line)
            print(cleaned_line)


def main():
    if len(sys.argv) != 2:
        print("Usage: yt-clean.py <YouTube Video ID>")
        sys.exit(1)

    video_id = sys.argv[1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".en.vtt")
    temp_file.close()  # Close the file so yt-dlp can write to it

    try:
        download_transcript(video_id, temp_file.name)

        print(f"Checking if the file {temp_file.name} exists and its size...")
        if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
            print(f"File {temp_file.name} exists and is not empty.")
            clean_transcript(temp_file.name)
        else:
            print("Transcript download failed or the file is empty.")
            sys.exit(1)
    finally:
        os.remove(temp_file.name)
        print(f"Removed temporary file {temp_file.name}")


if __name__ == "__main__":
    main()
