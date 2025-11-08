#!/usr/bin/env python3
"""
Third and FINAL metadata sweep - ultra-focused high-precision patterns only.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/third_metadata_sweep_report.md")

# Ultra-focused patterns - only the most reliable
PATTERNS = {
    'explicit_publication': [
        r'^\s*first published in\s+["\']?[A-Z]',
        r'^\s*originally published in\s+["\']?[A-Z]',
        r'^\s*published by\s+[A-Z][a-z]+',
        r'^\s*reprinted from\s+["\']?[A-Z]',
        r'^\s*from\s+["\']?[A-Z][^\n"\']{20,}["\']?\s*,?\s*\d{4}',  # from "Long Title", 1850
    ],
    'explicit_source': [
        r'^\s*source:\s*["\']?[A-Z]',
        r'^\s*\(source:\s*[A-Z]',
        r'^\s*taken from\s+["\']?[A-Z][a-z]+\s+[A-Z]',  # taken from The Magazine
    ],
    'numbered_footnotes': [
        r'^\s*\[\d+\]\s+[A-Z][a-z]{3,}',  # [1] This is a footnote
        r'^\s*\d+\.\s+\[.*editor.*\]',  # 1. [editor's note]
    ],
    'explicit_editorial': [
        r'^\s*\[?editor\'?s?\s+note:',
        r'^\s*\[?translator\'?s?\s+note:',
        r'^\s*\*\*editor\'?s?\s+note\*\*',
    ],
    'dramatic_act_scene': [
        r'^\s*ACT\s+[IVX]+\s*[:\.]?\s*$',  # ACT I (standalone line)
        r'^\s*SCENE\s+[IVX]+\s*[:\.]?\s*$',  # SCENE II (standalone line)
        r'^\s*ACT\s+[IVX]+\s*,\s*SCENE\s+[IVX]+',  # ACT I, SCENE II
    ],
    'stage_directions_bracketed': [
        r'^\s*\[\s*ENTER\s+[A-Z]',
        r'^\s*\[\s*EXIT\s+[A-Z]',
        r'^\s*\[\s*EXEUNT',
        r'^\s*\[\s*stage\s+direction',
    ],
    'collection_explicit': [
        r'^\s*from the anthology\s+["\']?[A-Z]',
        r'^\s*from the collection\s+["\']?[A-Z]',
        r'^\s*included in\s+["\']?[A-Z][^\n"\']{15,}["\']?',  # included in "Long Collection Name"
    ],
    'copyright_explicit': [
        r'^\s*copyright\s+©\s*\d{4}',
        r'^\s*©\s*\d{4}\s+by\s+[A-Z]',
        r'^\s*all rights reserved\s*[.,]?\s*\d{4}',
    ],
    'publication_year_bracketed': [
        r'^\s*\[\s*published\s+\d{4}\s*\]',
        r'^\s*\[\s*written\s+\d{4}\s*\]',
        r'^\s*\[\s*composed\s+in\s+\d{4}\s*\]',
    ],
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
    """Detect lines containing metadata - ultra-focused."""
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

                # Skip very short lines
                if len(line_stripped) < 5:
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
    print("THIRD AND FINAL METADATA SWEEP")
    print("=" * 80)
    print("Ultra-focused high-precision patterns only:")
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
                    'detections': result['detections'][:10]
                })
                total_lines_removed += lines_removed

                for category in result['categories']:
                    category_counts[category] += 1

    print(f"\n✓ Cleaned {len(cleaned_files):,} files")
    print(f"✓ Removed {total_lines_removed:,} lines total")

    # Statistics
    if category_counts:
        print(f"\nMetadata by category:")
        for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
            print(f"  {category.replace('_', ' ').title()}: {count:,} files")
    else:
        print("\n✓ No metadata found!")

    return cleaned_files, total_lines_removed, category_counts

def generate_report(cleaned_files, total_lines_removed, category_counts):
    """Generate cleanup report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    if not cleaned_files:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Third Metadata Sweep Report\n\n")
            f.write("## Result\n\n")
            f.write("**No metadata found - corpus is clean!**\n\n")
            f.write(f"Total corpus: 167,215 files\n")
        print(f"✓ Report saved to: {REPORT_FILE}")
        return

    # Sort by lines removed
    cleaned_sorted = sorted(cleaned_files, key=lambda x: -x['lines_removed'])

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Third Metadata Sweep Report (FINAL)\n\n")

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

            for i, item in enumerate(category_files[:20], 1):  # First 20
                f.write(f"### {i}. `{item['filename']}`\n\n")
                f.write(f"- **Title:** {item['title']}\n")
                f.write(f"- **Author:** {item['author']}\n")
                f.write(f"- **Lines removed:** {item['lines_removed']}\n\n")

                # Show detected lines for this category
                category_detections = [d for d in item['detections'] if d['category'] == category]
                if category_detections:
                    f.write("**Examples:**\n\n")
                    for detection in category_detections[:2]:  # First 2
                        f.write(f"```\nLine {detection['line_num']}: {detection['text']}\n```\n\n")

            if len(category_files) > 20:
                f.write(f"\n... and {len(category_files) - 20} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/third_metadata_sweep_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Third Metadata Sweep - FINAL ({len(cleaned_files):,} files)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(cleaned_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines removed: {item['lines_removed']}\n")
            f.write(f"   Categories: {', '.join(item['categories'])}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Third and Final Metadata Sweep")
    print("High-precision patterns only\n")

    # Scan and clean
    cleaned_files, total_lines_removed, category_counts = scan_and_clean()

    # Generate report
    generate_report(cleaned_files, total_lines_removed, category_counts)

    print("\n" + "=" * 80)
    print("FINAL SWEEP COMPLETE")
    print("=" * 80)

    if cleaned_files:
        print(f"✓ Files cleaned: {len(cleaned_files):,}")
        print(f"✓ Lines removed: {total_lines_removed:,}")
        print(f"✓ Review report at: {REPORT_FILE}")
    else:
        print("✓ No metadata found - corpus is CLEAN!")
        print("✓ Ready for multi-poem detection")

if __name__ == '__main__':
    main()
