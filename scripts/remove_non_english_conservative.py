#!/usr/bin/env python3
"""
Remove non-English files identified by conservative detection.
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/justin/Repos/AI Project")
POETRY_PLATFORM_DIR = BASE_DIR / "Data/poetry_platform_renamed"
GUTENBERG_DIR = BASE_DIR / "Data/Corpora/Gutenberg/By_Author"
NON_ENGLISH_LIST = BASE_DIR / "scripts/non_english_conservative_list.txt"
REPORT_FILE = BASE_DIR / "scripts/remove_non_english_report.txt"

def parse_file_list():
    """Parse the non-English file list."""
    files_to_remove = []

    with open(NON_ENGLISH_LIST, 'r', encoding='utf-8') as f:
        current_file = None

        for line in f:
            line = line.strip()

            # Skip header lines
            if not line or line.startswith('=') or line.startswith('Non-English'):
                continue

            # Match numbered entries like "1. filename.txt"
            if line and line[0].isdigit() and '. ' in line:
                # Extract filename (after the number and ". ")
                filename = line.split('. ', 1)[1]
                current_file = filename
                files_to_remove.append(current_file)

    return files_to_remove

def find_and_remove_file(filename):
    """Find and remove a file from either directory."""
    # Extract author from filename (format: Author/ID_Title_Author_Date.txt)
    parts = filename.split('/', 1)
    if len(parts) != 2:
        return False, f"Invalid filename format: {filename}"

    author, file_only = parts

    # Try poetry platform directory
    pp_path = POETRY_PLATFORM_DIR / author / file_only
    if pp_path.exists():
        pp_path.unlink()
        return True, f"Removed from poetry_platform_renamed: {filename}"

    # Try Gutenberg directory
    gb_path = GUTENBERG_DIR / author / file_only
    if gb_path.exists():
        gb_path.unlink()
        return True, f"Removed from Gutenberg: {filename}"

    return False, f"File not found: {filename}"

def main():
    print("=" * 80)
    print("REMOVING NON-ENGLISH FILES (CONSERVATIVE DETECTION)")
    print("=" * 80)
    print()

    # Parse file list
    print("Loading file list...")
    files_to_remove = parse_file_list()
    print(f"Found {len(files_to_remove)} files to remove")
    print()

    # Remove files
    removed_count = 0
    not_found_count = 0
    results = []

    print("Removing files...")
    for i, filename in enumerate(files_to_remove, 1):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(files_to_remove)}")

        success, message = find_and_remove_file(filename)
        results.append(message)

        if success:
            removed_count += 1
        else:
            not_found_count += 1

    print()
    print("=" * 80)
    print("REMOVAL COMPLETE")
    print("=" * 80)
    print(f"\nFiles removed: {removed_count}")
    print(f"Files not found: {not_found_count}")
    print(f"Total processed: {len(files_to_remove)}")

    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("Non-English File Removal Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Files removed: {removed_count}\n")
        f.write(f"Files not found: {not_found_count}\n")
        f.write(f"Total processed: {len(files_to_remove)}\n\n")
        f.write("\nDetailed Results:\n")
        f.write("-" * 80 + "\n\n")

        for result in results:
            f.write(result + "\n")

    print(f"\nDetailed report written to: {REPORT_FILE}")

    # Remove empty author folders
    print("\nRemoving empty author folders...")
    empty_folders_removed = 0

    for directory in [POETRY_PLATFORM_DIR, GUTENBERG_DIR]:
        if not directory.exists():
            continue

        for author_dir in directory.iterdir():
            if author_dir.is_dir() and not any(author_dir.iterdir()):
                author_dir.rmdir()
                empty_folders_removed += 1

    print(f"Empty folders removed: {empty_folders_removed}")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Non-English files removed: {removed_count}")
    print(f"Empty author folders removed: {empty_folders_removed}")
    print(f"Corpus after removal: {167215 - removed_count} poems")

if __name__ == '__main__':
    main()
