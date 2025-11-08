#!/usr/bin/env python3
"""
Second metadata sweep - focused on critical patterns.
Excludes dedications (too many false positives).
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/second_metadata_sweep_report.md")

# Focused patterns - excluding dedications
PATTERNS = {
    'dramatic_markers': [
        r'^\s*\[?\s*(ACT|SCENE)\s+[IVX0-9]+',
        r'^\s*\[?\s*(ENTER|EXIT|EXEUNT)\s+[A-Z]',
        r'\[.*stage direction.*\]',
        r'DRAMATIS\s+PERSONAE',
    ],
    'editorial_notes': [
        r'\[editor\'?s?\s+note',
        r'\[translator\'?s?\s+note',
        r'\[footnote',
        r'\[\d+\]\s*[A-Z]',  # [1] Footnote text
        r'^\s*\*+\s*note:',
    ],
    'publication_info': [
        r'first published in\s+["\']?[A-Z]',
        r'originally published',
        r'published by\s+[A-Z]',
        r'reprinted from',
        r'appeared in\s+["\']?[A-Z]',
        r'from\s+["\']?[A-Z][^\n]{15,}["\']?\s*\(?\d{4}\)?',  # from "Book Title" (year)
    ],
    'copyright': [
        r'©\s*\d{4}',
        r'copyright\s*[©(c)]\s*\d{4}',
        r'\(c\)\s*\d{4}',
        r'all rights reserved',
    ],
    'source_attribution': [
        r'^source:\s*[A-Z]',
        r'^from:\s*[A-Z]',
        r'taken from\s+[A-Z]',
        r'collected from',
    ],
    'collection_metadata': [
        r'from the collection\s+["\']?[A-Z]',
        r'from the anthology',
        r'from the volume\s+["\']?[A-Z]',
        r'included in\s+["\']?[A-Z]',
    ],
    'bracketed_years': [
        r'^\s*\[\s*\d{4}\s*\]',  # [1850]
        r'^\s*\[\s*written\s+\d{4}',
        r'^\s*\[\s*composed\s+\d{4}',
        r'^\s*\[\s*published\s+\d{4}',
    ],
    'date_location_stamps': [
        r'^—\s*[A-Z][a-z]+,?\s+\d{4}$',  # —London, 1850
        r'^\d{1,2}\s+[A-Z][a-z]+\s+\d{4}$',  # 15 March 1850
        r'^[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}$',  # March 15, 1850
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
    """Detect lines containing metadata."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except:
        return None

    if not lines:
        return None

    detections = []
    lines_to_remove = set()

    # Check each pattern category
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # Skip very short lines (likely not metadata)
                if len(line_stripped) < 3:
                    continue

                if re.search(pattern, line_stripped, re.IGNORECASE):
                    lines_to_remove.add(i)
                    detections.append({
                        'line_num': i + 1,
                        'category': category,
                        'text': line_stripped[:200]
                    })

    if not detections:
        return None

    return {
        'detections': detections,
        'lines_to_remove': sorted(lines_to_remove),
        'categories': list(set(d['category'] for d in detections))
    }

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
    print("SECOND METADATA SWEEP")
    print("=" * 80)
    print("Focused patterns (excluding dedications):")
    for category in PATTERNS.keys():
        print(f"  - {category.replace('_', ' ').title()}")
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
    category_counts = Counter()
    total_lines_removed = 0

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Processed {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = detect_metadata_lines(filepath)
        if result:
            # Clean the file
            lines_removed = clean_file(filepath, result['lines_to_remove'])

            if lines_removed > 0:
                cleaned_files.append({
                    'filename': row['filename'],
                    'title': row['title'],
                    'author': row['author'],
                    'filepath': filepath,
                    'lines_removed': lines_removed,
                    'categories': result['categories'],
                    'detections': result['detections'][:10]  # First 10 for report
                })
                total_lines_removed += lines_removed

                for category in result['categories']:
                    category_counts[category] += 1

    print(f"\n✓ Cleaned {len(cleaned_files):,} files")
    print(f"✓ Removed {total_lines_removed:,} lines total")

    # Statistics
    print(f"\nMetadata by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {category.replace('_', ' ').title()}: {count:,} files")

    return cleaned_files, total_lines_removed, category_counts

def generate_report(cleaned_files, total_lines_removed, category_counts):
    """Generate cleanup report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by lines removed
    cleaned_sorted = sorted(cleaned_files, key=lambda x: -x['lines_removed'])

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Second Metadata Sweep Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files cleaned:** {len(cleaned_files):,}\n")
        f.write(f"- **Lines removed:** {total_lines_removed:,}\n")
        f.write(f"- **Total corpus:** 167,215 files\n\n")

        f.write("## Categories Cleaned\n\n")
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            f.write(f"- **{category.replace('_', ' ').title()}:** {count:,} files\n")
        f.write("\n")

        # Group by category
        for category in sorted(category_counts.keys(), key=lambda x: -category_counts[x]):
            category_files = [item for item in cleaned_sorted if category in item['categories']]

            f.write(f"## {category.replace('_', ' ').title()} ({len(category_files):,} files)\n\n")

            for i, item in enumerate(category_files[:30], 1):  # First 30
                f.write(f"### {i}. `{item['filename']}`\n\n")
                f.write(f"- **Title:** {item['title']}\n")
                f.write(f"- **Author:** {item['author']}\n")
                f.write(f"- **Lines removed:** {item['lines_removed']}\n\n")

                # Show detected lines for this category
                category_detections = [d for d in item['detections'] if d['category'] == category]
                if category_detections:
                    f.write("**Examples:**\n\n")
                    for detection in category_detections[:3]:  # First 3
                        f.write(f"```\nLine {detection['line_num']}: {detection['text']}\n```\n\n")

            if len(category_files) > 30:
                f.write(f"\n... and {len(category_files) - 30} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/second_metadata_sweep_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Second Metadata Sweep ({len(cleaned_files):,} files cleaned)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(cleaned_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines removed: {item['lines_removed']}\n")
            f.write(f"   Categories: {', '.join(item['categories'])}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Second Metadata Sweep")
    print("Focused cleanup excluding dedications\n")

    # Scan and clean
    cleaned_files, total_lines_removed, category_counts = scan_and_clean()

    if not cleaned_files:
        print("\n✓ No metadata found - corpus is clean!")
        return

    # Generate report
    generate_report(cleaned_files, total_lines_removed, category_counts)

    print("\n" + "=" * 80)
    print("SWEEP COMPLETE")
    print("=" * 80)
    print(f"✓ Files cleaned: {len(cleaned_files):,}")
    print(f"✓ Lines removed: {total_lines_removed:,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
