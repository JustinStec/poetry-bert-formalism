#!/usr/bin/env python3
"""
Detect and remove redundant titles from poem content.
Many poems have the title as the first line, which is redundant.
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

# Paths
BASE_DIR = Path("/Users/justin/Repos/AI Project")
POETRY_PLATFORM_DIR = BASE_DIR / "Data/poetry_platform_renamed"
GUTENBERG_DIR = BASE_DIR / "Data/Corpora/Gutenberg/By_Author"
REPORT_FILE = BASE_DIR / "scripts/redundant_titles_report.txt"

def extract_title_from_filename(filename):
    """Extract title from filename format: ID_Title_Author_Date.txt"""
    parts = filename.rsplit('_', 2)
    if len(parts) >= 3:
        title_part = parts[0].split('_', 1)
        if len(title_part) > 1:
            return title_part[1]
    return None

def similarity(a, b):
    """Calculate similarity between two strings (0-1)."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()

def check_redundant_title(filepath):
    """
    Check if first line of poem matches the title.
    Returns (has_redundant_title, first_line, similarity_score)
    """
    title = extract_title_from_filename(filepath.name)
    if not title:
        return False, None, 0

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return False, None, 0

    if not lines:
        return False, None, 0

    first_line = lines[0].strip()
    if not first_line:
        return False, None, 0

    # Calculate similarity
    sim = similarity(title, first_line)

    # Consider it redundant if similarity > 0.85
    return sim > 0.85, first_line, sim

def remove_first_line(filepath):
    """Remove the first line from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Remove first line and any immediately following blank lines
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        return True
    except Exception as e:
        return False

def scan_directory(directory, dry_run=True):
    """Scan a directory for redundant titles."""
    redundant_files = []

    print(f"Scanning {directory.name}...")

    file_count = 0
    for author_dir in sorted(directory.iterdir()):
        if not author_dir.is_dir():
            continue

        for filepath in author_dir.glob('*.txt'):
            file_count += 1
            if file_count % 10000 == 0:
                print(f"  Scanned {file_count} files...")

            has_redundant, first_line, sim = check_redundant_title(filepath)
            if has_redundant:
                redundant_files.append({
                    'filepath': filepath,
                    'relative_path': f"{author_dir.name}/{filepath.name}",
                    'title': extract_title_from_filename(filepath.name),
                    'first_line': first_line,
                    'similarity': sim
                })

    return redundant_files

def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 80)
    if dry_run:
        print("REDUNDANT TITLE DETECTION (DRY RUN)")
        print("Add --execute flag to actually remove titles")
    else:
        print("REMOVING REDUNDANT TITLES")
    print("=" * 80)
    print()

    # Scan both directories
    all_redundant = []

    if POETRY_PLATFORM_DIR.exists():
        all_redundant.extend(scan_directory(POETRY_PLATFORM_DIR, dry_run))

    if GUTENBERG_DIR.exists():
        all_redundant.extend(scan_directory(GUTENBERG_DIR, dry_run))

    print(f"\n{'=' * 80}")
    print(f"RESULTS: Found {len(all_redundant)} files with redundant titles")
    print(f"{'=' * 80}\n")

    # Sort by similarity (highest first)
    all_redundant.sort(key=lambda x: x['similarity'], reverse=True)

    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Redundant Title Detection Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total files with redundant titles: {len(all_redundant)}\n\n")
        f.write("\nTop 50 Examples:\n")
        f.write("-" * 80 + "\n\n")

        for i, file_info in enumerate(all_redundant[:50], 1):
            f.write(f"{i}. {file_info['relative_path']}\n")
            f.write(f"   Title: {file_info['title']}\n")
            f.write(f"   First Line: {file_info['first_line']}\n")
            f.write(f"   Similarity: {file_info['similarity']:.2%}\n\n")

    print(f"Report written to: {REPORT_FILE}")

    if not dry_run:
        print(f"\nRemoving redundant titles...")
        removed_count = 0
        failed_count = 0

        for i, file_info in enumerate(all_redundant, 1):
            if i % 1000 == 0:
                print(f"  Progress: {i}/{len(all_redundant)}")

            if remove_first_line(file_info['filepath']):
                removed_count += 1
            else:
                failed_count += 1

        print(f"\n{'=' * 80}")
        print("REMOVAL COMPLETE")
        print(f"{'=' * 80}")
        print(f"\nTitles removed: {removed_count}")
        print(f"Failed: {failed_count}")
    else:
        print(f"\nThis was a DRY RUN. Run with --execute to actually remove titles.")
        print(f"Review the report first: {REPORT_FILE}")

if __name__ == '__main__':
    main()
