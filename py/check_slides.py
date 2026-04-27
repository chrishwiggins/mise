#!/usr/bin/env python3
"""
Slide Overflow Checker and Fixer for Beamer Presentations

This script analyzes markdown files for potential beamer slide overflow issues
and suggests fixes for common problems:
- Too many bullet points per slide
- Lines that are too long
- Lists that should be split
- Dense content blocks

Usage: python check_slides.py ros_beamer_2025.md
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class SlideChecker:
    def __init__(self):
        # Beamer slide limits (conservative estimates)
        self.MAX_BULLETS_PER_SLIDE = 6
        self.MAX_LINE_LENGTH = 85  # Characters that fit comfortably
        self.MAX_LINES_PER_SLIDE = 12  # Including title and bullets
        self.MAX_TABLE_ROWS = 8

        # Track issues found
        self.issues = []

    def analyze_markdown(self, file_path: str) -> Dict:
        """Analyze markdown file for potential overflow issues"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        slides = self.split_into_slides(content)
        results = {
            "total_slides": len(slides),
            "problematic_slides": [],
            "suggestions": [],
        }

        for i, slide in enumerate(slides, 1):
            issues = self.check_slide(slide, i)
            if issues:
                results["problematic_slides"].append(
                    {
                        "slide_number": i,
                        "title": self.get_slide_title(slide),
                        "issues": issues,
                    }
                )

        return results

    def split_into_slides(self, content: str) -> List[str]:
        """Split markdown content into individual slides"""
        # Split on ## headings (slide level 2)
        slides = re.split(r"\n## ", content)

        # Clean up the splits
        processed_slides = []
        for i, slide in enumerate(slides):
            if i == 0:
                # First slide might not start with ##
                processed_slides.append(slide)
            else:
                processed_slides.append("## " + slide)

        # Filter out empty slides and metadata
        return [
            s.strip() for s in processed_slides if s.strip() and not s.startswith("---")
        ]

    def get_slide_title(self, slide_content: str) -> str:
        """Extract slide title"""
        lines = slide_content.split("\n")
        for line in lines:
            if line.startswith("## "):
                return line[3:].strip()
            elif line.startswith("# "):
                return line[2:].strip()
        return "Unknown"

    def check_slide(self, slide_content: str, slide_num: int) -> List[str]:
        """Check individual slide for overflow issues"""
        issues = []
        lines = slide_content.split("\n")

        # Count bullets and content lines
        bullet_count = 0
        content_lines = 0
        long_lines = []
        table_rows = 0

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith("#"):
                continue

            content_lines += 1

            # Check for bullets
            if (
                line.startswith("-")
                or line.startswith("*")
                or re.match(r"^\d+\.", line)
            ):
                bullet_count += 1

            # Check line length
            # Remove markdown formatting for length calculation
            clean_line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)  # Bold
            clean_line = re.sub(r"\*(.*?)\*", r"\1", clean_line)  # Italic
            clean_line = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", clean_line)  # Links

            if len(clean_line) > self.MAX_LINE_LENGTH:
                long_lines.append((line_num, len(clean_line), line[:60] + "..."))

            # Check for table rows
            if "|" in line and not line.startswith("|--"):
                table_rows += 1

        # Report issues
        if bullet_count > self.MAX_BULLETS_PER_SLIDE:
            issues.append(
                f"Too many bullets: {bullet_count} (max {self.MAX_BULLETS_PER_SLIDE})"
            )

        if content_lines > self.MAX_LINES_PER_SLIDE:
            issues.append(
                f"Too much content: {content_lines} lines (max {self.MAX_LINES_PER_SLIDE})"
            )

        if long_lines:
            issues.append(
                f"Long lines detected: {len(long_lines)} lines over {self.MAX_LINE_LENGTH} chars"
            )
            for line_num, length, preview in long_lines[:3]:  # Show first 3
                issues.append(f"  Line {line_num} ({length} chars): {preview}")

        if table_rows > self.MAX_TABLE_ROWS:
            issues.append(f"Large table: {table_rows} rows (max {self.MAX_TABLE_ROWS})")

        return issues

    def suggest_fixes(self, results: Dict) -> List[str]:
        """Generate suggestions for fixing overflow issues"""
        suggestions = []

        for slide in results["problematic_slides"]:
            title = slide["title"]
            suggestions.append(f"\n## Slide {slide['slide_number']}: {title}")

            for issue in slide["issues"]:
                if "Too many bullets" in issue:
                    suggestions.append("  → Split into multiple slides")
                    suggestions.append("  → Use sub-sections (###)")
                    suggestions.append("  → Group related bullets under subheadings")

                elif "Too much content" in issue:
                    suggestions.append("  → Break into 2-3 smaller slides")
                    suggestions.append("  → Move details to appendix slides")
                    suggestions.append(
                        "  → Use 'pause' overlays for progressive disclosure"
                    )

                elif "Long lines" in issue:
                    suggestions.append("  → Break long sentences")
                    suggestions.append("  → Use bullet sub-points")
                    suggestions.append("  → Abbreviate where possible")

                elif "Large table" in issue:
                    suggestions.append("  → Split table across multiple slides")
                    suggestions.append("  → Highlight key rows only")
                    suggestions.append("  → Use landscape orientation")

        return suggestions


def create_fixed_version(input_file: str, output_file: str, results: Dict):
    """Create a fixed version of the markdown file"""

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply common fixes
    fixed_content = content

    # Fix 1: Break long bullet lists
    fixed_content = re.sub(
        r"(\n- .*?\n- .*?\n- .*?\n- .*?\n- .*?\n- .*?\n- .*?\n)",
        lambda m: m.group(1).replace(
            "\n- ", "\n\n### \n\n- ", 2
        ),  # Insert subheading every 6 bullets
        fixed_content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Fix 2: Break long lines at sentence boundaries
    lines = fixed_content.split("\n")
    fixed_lines = []

    for line in lines:
        if len(line) > 85 and not line.startswith("#"):
            # Try to break at sentence boundaries
            sentences = re.split(r"(\. )", line)
            if len(sentences) > 2:
                # Rejoin sentences, breaking every 2 sentences
                current_line = ""
                for i, part in enumerate(sentences):
                    current_line += part
                    if ". " in part and len(current_line) > 60:
                        fixed_lines.append(current_line.strip())
                        current_line = ""
                if current_line.strip():
                    fixed_lines.append(current_line.strip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    fixed_content = "\n".join(fixed_lines)

    # Write fixed version
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(fixed_content)


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_slides.py <markdown_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"Error: File {input_file} not found")
        sys.exit(1)

    checker = SlideChecker()
    results = checker.analyze_markdown(input_file)

    print(f"\n🎯 Slide Analysis Results for {input_file}")
    print("=" * 60)
    print(f"Total slides: {results['total_slides']}")
    print(f"Problematic slides: {len(results['problematic_slides'])}")

    if results["problematic_slides"]:
        print(f"\n⚠️  Issues Found:")
        for slide in results["problematic_slides"]:
            print(f"\nSlide {slide['slide_number']}: {slide['title']}")
            for issue in slide["issues"]:
                print(f"  • {issue}")

        print(f"\n💡 Suggested Fixes:")
        suggestions = checker.suggest_fixes(results)
        for suggestion in suggestions:
            print(suggestion)

        # Offer to create fixed version
        response = input(f"\nCreate automatically fixed version? (y/n): ")
        if response.lower() == "y":
            output_file = input_file.replace(".md", "_fixed.md")
            create_fixed_version(input_file, output_file, results)
            print(f"✅ Created fixed version: {output_file}")
            print("Review the changes and rebuild with: make beamer")
    else:
        print("\n✅ No overflow issues detected!")


if __name__ == "__main__":
    main()
