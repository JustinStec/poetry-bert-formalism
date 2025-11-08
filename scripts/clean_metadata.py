#!/usr/bin/env python3
"""
Clean remaining metadata from files.
Removes copyright, publication info, source citations, editorial notes, etc.
Avoids removing dedications (which are often legitimate poem content).
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/metadata_cleanup_report.md")

# Only clean these categories (exclude 'dedication' which are often legitimate)
CATEGORIES_TO_CLEAN = [
    'copyright',
    'publication',
    'source_citation',
    'editorial_notes',
    'collection_info',
    'brackets_metadata',
    'dates_locations'
]

# Patterns to detect and remove
PATTERNS = {
    'copyright': [
        r'©\s*\d{4}',
        r'copyright\s+\d{4}',
        r'\(c\)\s*\d{4}',
        r'all rights reserved',
    ],
    'publication': [
        r'first published in',
        r'originally published',
        r'from\s+["\']?[A-Z][^"\']{10,}["\']?\s+\(\d{4}\)',  # From "Book Title" (year)
        r'appeared in\s+[A-Z]',
        r'reprinted from',
    ],
    'source_citation': [
        r'source:',
        r'from:',
        r'taken from',
    ],
    'editorial_notes': [
        r'\[editor\'?s? note',
        r'\[translator\'?s? note',
        r'\[written\s+\d{4}',
        r'\[composed\s+\d{4}',
    ],
    'collection_info': [
        r'from the collection',
        r'from the anthology',
        r'from the volume',
    ],
    'brackets_metadata': [
        r'^\[.*\d{4}.*\]$',  # [anything with year]
        r'^\[.*published.*\]$',
    ],
    'dates_locations': [
        r'^—\s*[A-Z][a-z]+,?\s+\d{4}',  # —Location, Year
        r'^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$',  # 12 January 2000
    ]
}

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

def detect_metadata_lines(filepath):
    """Detect lines containing metadata (excluding dedications)."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except:
        return None

    if not lines:
        return None

    lines_to_remove = set()

    # Check each pattern category (only categories we want to clean)
    for category in CATEGORIES_TO_CLEAN:
        if category not in PATTERNS:
            continue

        for pattern in PATTERNS[category]:
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if re.search(pattern, line_stripped, re.IGNORECASE):
                    lines_to_remove.add(i)

    if not lines_to_remove:
        return None

    return sorted(lines_to_remove)

def clean_file(filepath, lines_to_remove):
    """Remove metadata lines from file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return 0

    if not lines:
        return 0

    # Remove lines
    cleaned_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

    # Write back
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        return len(lines_to_remove)
    except:
        return 0

def scan_and_clean():
    """Scan corpus and clean metadata."""
    print("=" * 80)
    print("METADATA CLEANUP")
    print("=" * 80)
    print("Cleaning categories:")
    for category in CATEGORIES_TO_CLEAN:
        print(f"  - {category.replace('_', ' ').title()}")
    print("\nNOT cleaning: Dedications (often legitimate poem content)")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning and cleaning files...")
    cleaned_files = []
    total_lines_removed = 0

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Processed {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        lines_to_remove = detect_metadata_lines(filepath)
        if lines_to_remove:
            lines_removed = clean_file(filepath, lines_to_remove)
            if lines_removed > 0:
                cleaned_files.append({
                    'filename': row['filename'],
                    'title': row['title'],
                    'author': row['author'],
                    'filepath': filepath,
                    'lines_removed': lines_removed
                })
                total_lines_removed += lines_removed

    print(f"\n✓ Cleaned {len(cleaned_files):,} files")
    print(f"✓ Removed {total_lines_removed:,} lines total")

    return cleaned_files, total_lines_removed

def generate_report(cleaned_files, total_lines_removed):
    """Generate cleanup report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by lines removed
    cleaned_sorted = sorted(cleaned_files, key=lambda x: -x['lines_removed'])

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Metadata Cleanup Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files cleaned:** {len(cleaned_files):,}\n")
        f.write(f"- **Lines removed:** {total_lines_removed:,}\n")
        f.write(f"- **Total corpus:** 167,442 files\n\n")

        f.write("## Categories Cleaned\n\n")
        for category in CATEGORIES_TO_CLEAN:
            f.write(f"- {category.replace('_', ' ').title()}\n")
        f.write("\n**Note:** Dedications were NOT removed (often legitimate poem content)\n\n")

        f.write("## Files Cleaned (Top 100)\n\n")
        for i, item in enumerate(cleaned_sorted[:100], 1):
            f.write(f"### {i}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Lines removed:** {item['lines_removed']}\n\n")

        if len(cleaned_sorted) > 100:
            f.write(f"\n... and {len(cleaned_sorted) - 100} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/metadata_cleanup_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Metadata Cleanup Summary ({len(cleaned_files):,} files cleaned)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(cleaned_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines removed: {item['lines_removed']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Metadata Cleanup")
    print("Removes copyright, publication info, source citations, etc.\n")

    # Scan and clean
    cleaned_files, total_lines_removed = scan_and_clean()

    if not cleaned_files:
        print("\n✓ No metadata found - corpus is clean!")
        return

    # Generate report
    generate_report(cleaned_files, total_lines_removed)

    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)
    print(f"✓ Files cleaned: {len(cleaned_files):,}")
    print(f"✓ Lines removed: {total_lines_removed:,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
