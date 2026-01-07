#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import subprocess
import sys
import os
import shutil
from collections import defaultdict


def get_line_count_at_commit(commit_hash):
    """Get line count of aliases-public.sh at specific commit"""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:sh/aliases-public.sh"],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line for line in result.stdout.split("\n") if line.strip()]
        return len(lines)
    except subprocess.CalledProcessError:
        return None


def main():
    original_cwd = os.getcwd()

    # Create temporary directory using /tmp/$$
    pid = os.getpid()
    temp_dir = f"/tmp/{pid}"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Working in temporary directory: {temp_dir}")

    try:
        # Clone with sparse checkout for just the file we need
        repo_dir = os.path.join(temp_dir, "mise")

        # Initialize repo
        subprocess.run(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                "https://github.com/chrishwiggins/mise.git",
                repo_dir,
            ],
            check=True,
        )

        os.chdir(repo_dir)

        # Set up sparse checkout for just our file
        subprocess.run(["git", "sparse-checkout", "init", "--cone"], check=True)
        subprocess.run(
            ["git", "sparse-checkout", "set", "sh/aliases-public.sh"], check=True
        )
        subprocess.run(["git", "checkout"], check=True)

        print("Sparse checkout complete, analyzing git history...")

        # Get all commits with years - this is fast since we have the full history
        result = subprocess.run(
            [
                "git",
                "log",
                "--format=%H %ad",
                "--date=format:%Y",
                "--follow",
                "--",
                "sh/aliases-public.sh",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        line_counts_by_year = defaultdict(list)
        commits = result.stdout.strip().split("\n")

        print(f"Found {len(commits)} commits, analyzing file sizes...")

        for i, line in enumerate(commits):
            if line:
                if i % 50 == 0:  # Progress indicator
                    print(f"Processing commit {i+1}/{len(commits)}")

                parts = line.split()
                commit_hash = parts[0]
                year = int(parts[1])

                line_count = get_line_count_at_commit(commit_hash)
                # Skip commits where file was missing/empty
                if line_count is not None and line_count > 0:
                    line_counts_by_year[year].append(line_count)

        # Calculate statistics
        years = sorted(line_counts_by_year.keys())
        avg_lines = [
            sum(line_counts_by_year[year]) / len(line_counts_by_year[year])
            for year in years
        ]
        max_lines = [max(line_counts_by_year[year]) for year in years]
        min_lines = [min(line_counts_by_year[year]) for year in years]

        print(f"Data spans {years[0]} to {years[-1]} ({len(years)} years)")

        # Create the plot
        plt.figure(figsize=(12, 8))

        # Plot average line count
        plt.plot(
            years,
            avg_lines,
            "o-",
            linewidth=2,
            markersize=8,
            label="Average Lines",
            color="blue",
        )

        # Plot max and min as error bars or separate lines
        plt.fill_between(
            years,
            min_lines,
            max_lines,
            alpha=0.3,
            color="lightblue",
            label="Min-Max Range",
        )

        # Formatting
        plt.xlabel("Year", fontsize=12)
        plt.ylabel("Number of Lines", fontsize=12)
        plt.title(
            "Evolution of aliases-public.sh File Size Over Time\n(chrishwiggins/mise repository)",
            fontsize=14,
        )
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Set y-axis to start from 0 for better perspective
        plt.ylim(0, max(max_lines) * 1.1)

        # Add some annotations for interesting points
        plt.annotate(
            f"Started: {avg_lines[0]:.0f} lines",
            xy=(years[0], avg_lines[0]),
            xytext=(years[0] + 1, avg_lines[0] + 50),
            arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
        )

        plt.annotate(
            f"Latest: {avg_lines[-1]:.0f} lines",
            xy=(years[-1], avg_lines[-1]),
            xytext=(years[-1] - 1, avg_lines[-1] + 30),
            arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
        )

        plt.tight_layout()

        # Save plot in original working directory
        plot_path = os.path.join(original_cwd, "lines_vs_year.png")
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Plot saved to {plot_path}")

        # Print some statistics
        print(
            f"Growth from {years[0]} to {years[-1]}: {avg_lines[-1] - avg_lines[0]:.1f} lines"
        )
        print(
            f"Average growth per year: {(avg_lines[-1] - avg_lines[0]) / (years[-1] - years[0]):.1f} lines/year"
        )

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Clean up temporary directory
        os.chdir(original_cwd)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
