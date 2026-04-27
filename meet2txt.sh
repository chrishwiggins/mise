#!/bin/bash

# meet2txt.sh - Convert Google Meet HTML caption files to clean text transcripts
#
# Usage:
#   ./meet2txt.sh input.html [output.txt]
#   cat input.html | ./meet2txt.sh
#
# This script extracts clean transcript text from Google Meet caption HTML files.

set -euo pipefail

# Function to extract transcript from HTML
extract_transcript() {
    local html_content="$1"

    # Extract speaker names and captions using grep and sed
    echo "$html_content" | \
    grep -oP '(?<=<span class="NWpY1d">)[^<]+(?=</span>)|(?<=<div class="ygicle VbkSUe">)[^<]+(?=</div>)' | \
    awk '
    BEGIN {
        speaker = "Unknown"
        line_count = 0
    }
    {
        line_count++
        # Check if this looks like a speaker name (shorter, capitalized)
        if (length($0) < 50 && /^[A-Z]/) {
            speaker = $0
        } else if (length($0) > 2) {
            # This is caption text
            print speaker ": " $0
        }
    }'
}

# Main script
main() {
    local input_file="${1:-}"
    local output_file="${2:-}"
    local html_content=""

    # Read input
    if [[ -z "$input_file" || "$input_file" == "-" ]]; then
        # Read from stdin
        html_content=$(cat)
    else
        # Read from file
        if [[ ! -f "$input_file" ]]; then
            echo "Error: File '$input_file' not found" >&2
            exit 1
        fi
        html_content=$(cat "$input_file")
    fi

    # Check if we have content
    if [[ -z "$html_content" ]]; then
        echo "Error: No input provided" >&2
        exit 1
    fi

    # Extract transcript
    local transcript
    transcript=$(extract_transcript "$html_content")

    if [[ -z "$transcript" ]]; then
        echo "Error: No transcript content found in HTML" >&2
        exit 1
    fi

    # Add header
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local header="Google Meet Transcript - $timestamp"
    if [[ -n "$input_file" && "$input_file" != "-" ]]; then
        header="$header"$'\n'"Source: $(basename "$input_file")"
    fi

    local output="$header"$'\n\n'"$transcript"

    # Write output
    if [[ -n "$output_file" ]]; then
        echo "$output" > "$output_file"
        echo "Transcript saved to $output_file"
    else
        echo "$output"
    fi
}

# Show help if requested
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "meet2txt.sh - Convert Google Meet HTML caption files to clean text transcripts"
    echo ""
    echo "Usage:"
    echo "  ./meet2txt.sh input.html [output.txt]"
    echo "  cat input.html | ./meet2txt.sh"
    echo "  ./meet2txt.sh - output.txt < input.html"
    echo ""
    echo "Examples:"
    echo "  ./meet2txt.sh meeting.html transcript.txt"
    echo "  cat meeting.html | ./meet2txt.sh > transcript.txt"
    exit 0
fi

main "$@"