#!/usr/bin/env python3
"""
Remove verse drama files from corpus.
"""

import csv
import json
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
VERSE_DRAMA_LIST = Path("/Users/justin/Repos/AI Project/scripts/verse_drama_list.txt")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/verse_drama_removal_report.md")

def get_file_path(row):
    """Get full file path from metadata row."""
    filename = row['filename']

    if 'gutenberg' in filename.lower():
        for author_dir in GUTENBERG_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path
    else:
        author = row['author']
        filepath = POETRY_PLATFORM_DIR / author / filename
        if filepath.exists():
            return filepath

    return None

def parse_verse_drama_list():
    """Parse the verse drama list to get filenames."""
    print("Loading verse drama list...")

    with open(VERSE_DRAMA_LIST, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse filenames from the list
    filenames = set()
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if line and line[0].isdigit() and '. ' in line:
            # Extract filename from lines like "1. filename.txt"
            parts = line.split('. ', 1)
            if len(parts) == 2:
                filename = parts[1].strip()
                filenames.add(filename)

    print(f"✓ Found {len(filenames)} verse drama files to remove")
    return filenames

def remove_files(verse_drama_filenames):
    """Remove verse drama files and update metadata CSV."""
    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nRemoving verse drama files...")
    removed = []
    confidence_counts = Counter()

    # Track rows to keep
    kept_rows = []

    for row in rows:
        filename = row['filename']

        if filename in verse_drama_filenames:
            # Get file path and remove
            filepath = get_file_path(row)
            if filepath and filepath.exists():
                try:
                    filepath.unlink()
                    removed.append({
                        'filename': filename,
                        'title': row['title'],
                        'author': row['author'],
                        'filepath': str(filepath)
                    })
                    print(f"  Removed: {filename}")
                except Exception as e:
                    print(f"  ERROR removing {filename}: {e}")
                    kept_rows.append(row)  # Keep in CSV if deletion failed
            else:
                print(f"  File not found: {filename}")
                # Don't add to kept_rows - remove from CSV even if file doesn't exist
        else:
            kept_rows.append(row)

    print(f"\n✓ Removed {len(removed):,} files")
    print(f"✓ Remaining: {len(kept_rows):,} entries")

    # Write updated CSV
    print("\nUpdating metadata CSV...")
    with open(UNIFIED_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

    print(f"✓ Updated {UNIFIED_CSV}")

    return removed, len(kept_rows)

def clean_empty_folders():
    """Remove empty author folders."""
    print("\nCleaning empty folders...")

    empty_folders = []

    for author_dir in POETRY_PLATFORM_DIR.iterdir():
        if author_dir.is_dir():
            # Check if empty
            contents = list(author_dir.iterdir())
            if not contents:
                try:
                    author_dir.rmdir()
                    empty_folders.append(author_dir.name)
                except:
                    pass

    if empty_folders:
        print(f"✓ Removed {len(empty_folders)} empty author folders")
    else:
        print("✓ No empty folders found")

    return empty_folders

def generate_report(removed, final_count, empty_folders):
    """Generate removal report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Verse Drama Removal Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files removed:** {len(removed):,}\n")
        f.write(f"- **Remaining corpus:** {final_count:,}\n")
        f.write(f"- **Empty folders removed:** {len(empty_folders)}\n\n")

        f.write("## Removed Files\n\n")

        # Group by author
        by_author = {}
        for item in removed:
            author = item['author']
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(item)

        for author in sorted(by_author.keys()):
            files = by_author[author]
            f.write(f"### {author} ({len(files)} files)\n\n")

            for item in files:
                f.write(f"- **{item['filename']}**\n")
                f.write(f"  - Title: {item['title']}\n")
                f.write(f"  - Path: {item['filepath']}\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

def main():
    print("Verse Drama Removal")
    print("Removing plays from poetry corpus\n")
    print("=" * 80)

    # Parse verse drama list
    verse_drama_filenames = parse_verse_drama_list()

    # Remove files and update metadata
    removed, final_count = remove_files(verse_drama_filenames)

    # Clean empty folders
    empty_folders = clean_empty_folders()

    # Generate report
    generate_report(removed, final_count, empty_folders)

    print("\n" + "=" * 80)
    print("REMOVAL COMPLETE")
    print("=" * 80)
    print(f"✓ Files removed: {len(removed):,}")
    print(f"✓ Final corpus size: {final_count:,}")
    print(f"✓ Empty folders removed: {len(empty_folders)}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
