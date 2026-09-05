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

import glob
import os
import shutil
import sys
import re
import subprocess
import tempfile


def download_transcript(video_id, out_template):
    """Download a video's auto-generated transcript; return the file yt-dlp wrote.

    yt-dlp always appends its own ".<lang>.<ext>" to the -o template, so the
    caller cannot know the final name in advance: ask for a directory template
    and glob for the result, which also covers not knowing which of the
    requested language tags the video actually turned out to have.
    """
    # YouTube 403 workaround (2026-08-20), matching seiton/bash/yt-dlp-w: the
    # default android_vr player client now yields URLs YouTube rejects, and the
    # clients that replace it require a GVS PO Token we do not have.
    command = [
        "yt-dlp",
        "--extractor-args",
        "youtube:player_client=web_embedded",
        "--write-auto-sub",
        # An explicit list, deliberately not the regex "en.*": that pattern also
        # matches machine translations ("en-fr", "en-es") and downloads all of
        # them. Which native track exists varies by video -- some expose plain
        # "en", others only the auto-generated "en-en" -- so name the real
        # candidates and let yt-dlp take whichever is present.
        # (Do NOT add extractor-arg skip=translated_subs to prune the "en-xx"
        # noise instead: it drops the native track too, leaving nothing at all.
        # Both behaviors verified against real videos 2026-08-20.)
        "--sub-langs",
        "en-en,en-US,en-GB,en",
        "--skip-download",
        "-o",
        out_template,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error downloading transcript:", result.stderr)
        sys.exit(1)

    written = sorted(glob.glob(os.path.join(os.path.dirname(out_template), "*.vtt")))
    if not written:
        print("Transcript download produced no subtitle file.")
        sys.exit(1)
    print(f"Transcript downloaded to {written[0]}")
    return written[0]


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
    temp_dir = tempfile.mkdtemp(prefix="yt-clean.")

    try:
        vtt = download_transcript(video_id, os.path.join(temp_dir, "%(id)s"))

        if os.path.getsize(vtt) > 0:
            clean_transcript(vtt)
        else:
            print("Transcript download failed or the file is empty.")
            sys.exit(1)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
