#!/bin/bash

# Get the latest screenshot file
latest_screenshot=$(ls -t ~/Shots/ | grep -E '^Screenshot ' | head -n 1)

# Check if a screenshot is found
if [ -z "$latest_screenshot" ]; then
    echo "No screenshot found."
    exit 1
fi

# Run Tesseract OCR on the latest screenshot
#tesseract ~/Shots/"$latest_screenshot" /tmp/ocr.txt
tesseract ~/Shots/"$latest_screenshot" /tmp/ocr

# Inform the user
echo "OCR output written to /tmp/ocr.txt"
