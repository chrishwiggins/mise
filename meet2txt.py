#!/usr/bin/env python3
"""
meet2txt - Convert Google Meet HTML caption files to clean text transcripts

Usage:
    python3 meet2txt.py input.html [output.txt]
    cat input.html | python3 meet2txt.py

This script extracts clean transcript text from Google Meet caption HTML files.
If no output file is specified, prints to stdout.
Supports both file input and stdin.
"""

import sys
import re
from datetime import datetime
import argparse
from pathlib import Path

def extract_transcript_from_html(html_content):
    """Extract clean transcript text from Google Meet HTML"""

    # Find all speaker name spans
    speaker_pattern = r'<span class="NWpY1d">([^<]+)</span>'
    speakers = re.findall(speaker_pattern, html_content)

    # Find all caption text divs
    caption_pattern = r'<div class="ygicle VbkSUe">([^<]+)</div>'
    captions = re.findall(caption_pattern, html_content)

    # Build transcript
    transcript_lines = []
    current_speaker = "Unknown"

    # Handle case where HTML has speaker/caption pairs
    if len(speakers) > 0 and len(captions) > 0:
        # Try to match speakers with captions
        speaker_idx = 0
        for caption in captions:
            caption = caption.strip()
            if not caption or len(caption) < 3:
                continue

            # Use next speaker if available
            if speaker_idx < len(speakers):
                current_speaker = speakers[speaker_idx]
                speaker_idx += 1

            transcript_lines.append(f"{current_speaker}: {caption}")

    # Fallback: just extract all text content
    if not transcript_lines:
        # Remove HTML tags and extract text
        text_only = re.sub(r'<[^>]+>', ' ', html_content)
        # Clean up whitespace
        text_only = re.sub(r'\s+', ' ', text_only).strip()
        if text_only:
            transcript_lines.append(text_only)

    return transcript_lines

def main():
    parser = argparse.ArgumentParser(description='Convert Google Meet HTML caption files to clean text transcripts')
    parser.add_argument('input_file', nargs='?', help='Input HTML file (use - or omit for stdin)')
    parser.add_argument('output_file', nargs='?', help='Output text file (default: stdout)')
    parser.add_argument('--timestamp', action='store_true', help='Add timestamp to output')

    args = parser.parse_args()

    # Read input
    if args.input_file and args.input_file != '-':
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            input_name = Path(args.input_file).name
        except FileNotFoundError:
            print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        html_content = sys.stdin.read()
        input_name = "stdin"

    if not html_content.strip():
        print("Error: No input provided", file=sys.stderr)
        sys.exit(1)

    # Extract transcript
    transcript_lines = extract_transcript_from_html(html_content)

    if not transcript_lines:
        print("Error: No transcript content found in HTML", file=sys.stderr)
        sys.exit(1)

    # Prepare output
    output_lines = []

    # Add header with timestamp if requested
    if args.timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output_lines.append(f"Google Meet Transcript - {timestamp}")
        if input_name != "stdin":
            output_lines.append(f"Source: {input_name}")
        output_lines.append("")

    # Add transcript content
    output_lines.extend(transcript_lines)

    output_text = "\n".join(output_lines)

    # Write output
    if args.output_file:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f"Transcript saved to {args.output_file}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_text)

if __name__ == "__main__":
    main()