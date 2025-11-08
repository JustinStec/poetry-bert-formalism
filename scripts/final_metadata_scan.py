#!/usr/bin/env python3
"""
Final comprehensive metadata scan.
Catches any remaining editorial content, copyright notices, publication info, etc.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/final_metadata_report.md")

# Metadata patterns to detect
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
    'dedication': [
        r'^for\s+[A-Z][a-z]+\b',  # "For John" at start of line
        r'^to\s+[A-Z][a-z]+\b',   # "To Mary" at start of line
        r'^in memory of',
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

def detect_metadata(filepath):
    """Detect any remaining metadata in file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except:
        return None

    if not lines:
        return None

    detections = []

    # Check each pattern category
    for category, patterns in PATTERNS.items():
        for pattern in patterns:
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                if re.search(pattern, line_stripped, re.IGNORECASE):
                    detections.append({
                        'line_num': i,
                        'category': category,
                        'pattern': pattern,
                        'text': line_stripped[:200]  # First 200 chars
                    })

    if not detections:
        return None

    return {
        'detections': detections,
        'count': len(detections),
        'categories': list(set(d['category'] for d in detections))
    }

def scan_corpus():
    """Scan entire corpus for metadata."""
    print("=" * 80)
    print("FINAL METADATA SCAN")
    print("=" * 80)
    print("Scanning for:")
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

    print("\nScanning for metadata...")
    flagged = []
    category_counts = Counter()

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = detect_metadata(filepath)
        if result:
            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'filepath': filepath,
                **result
            })

            for category in result['categories']:
                category_counts[category] += 1

    print(f"\n✓ Found {len(flagged):,} files with metadata")

    # Statistics
    print(f"\nMetadata by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {category.replace('_', ' ').title()}: {count:,} files")

    return flagged, category_counts

def generate_report(flagged, category_counts):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Final Metadata Scan Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files with metadata:** {len(flagged):,}\n")
        f.write(f"- **Total corpus:** 167,442 files\n")
        f.write(f"- **Clean files:** {167442 - len(flagged):,}\n\n")

        f.write("## Metadata by Category\n\n")
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            f.write(f"- **{category.replace('_', ' ').title()}:** {count:,} files\n")
        f.write("\n")

        # Group by category
        for category in sorted(category_counts.keys()):
            category_files = [item for item in flagged if category in item['categories']]

            f.write(f"## {category.replace('_', ' ').title()} ({len(category_files):,} files)\n\n")

            for i, item in enumerate(category_files[:50], 1):  # First 50
                f.write(f"### {i}. `{item['filename']}`\n\n")
                f.write(f"- **Title:** {item['title']}\n")
                f.write(f"- **Author:** {item['author']}\n")
                f.write(f"- **Detections:** {item['count']}\n\n")

                # Show detected lines
                category_detections = [d for d in item['detections'] if d['category'] == category]
                for detection in category_detections[:5]:  # First 5
                    f.write(f"**Line {detection['line_num']}:**\n")
                    f.write(f"```\n{detection['text']}\n```\n\n")

            if len(category_files) > 50:
                f.write(f"\n... and {len(category_files) - 50} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/final_metadata_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Files with Remaining Metadata ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(flagged, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Categories: {', '.join(item['categories'])}\n")
            f.write(f"   Detections: {item['count']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Final Metadata Scan")
    print("Detecting any remaining editorial content\n")

    # Scan corpus
    flagged, category_counts = scan_corpus()

    if not flagged:
        print("\n✓ No metadata found - corpus is clean!")
        return

    # Generate report
    generate_report(flagged, category_counts)

    print("\n" + "=" * 80)
    print("SCAN COMPLETE")
    print("=" * 80)
    print(f"✓ Total files flagged: {len(flagged):,}")
    print(f"✓ Review report at: {REPORT_FILE}")
    print("\nNote: Many detections may be false positives (legitimate poem content)")

if __name__ == '__main__':
    main()
