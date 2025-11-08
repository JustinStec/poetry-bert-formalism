#!/usr/bin/env python3
"""
Detect and remove editorial metadata from poem files.
Common patterns: publication info, source citations, editor notes, etc.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/metadata_detection_report.md")

# Settings
DRY_RUN = False  # Set to False to apply changes
MIN_LINES_TO_CHECK = 5  # Check last N lines for metadata

# Metadata patterns (case-insensitive)
METADATA_PATTERNS = [
    re.compile(r'\bthis poem (is taken|was taken|appears|is from|comes from)\b', re.IGNORECASE),
    re.compile(r'\bpublished (by|in)\b', re.IGNORECASE),
    re.compile(r'\bsource:\s', re.IGNORECASE),
    re.compile(r'\bfrom (the )?(collection|anthology|book|volume)\b', re.IGNORECASE),
    re.compile(r'\bedited by\b', re.IGNORECASE),
    re.compile(r'\bcopyright\s+©?\s*\d{4}', re.IGNORECASE),
    re.compile(r'\b\d{4}\s+(edition|printing|publication)', re.IGNORECASE),
    re.compile(r'\bpage\s+\d+', re.IGNORECASE),
    re.compile(r'\bpp\.\s*\d+', re.IGNORECASE),
    re.compile(r'\b(originally|first) (published|appeared) (in|on)\b', re.IGNORECASE),
    re.compile(r'\bISBN[:\s]+[-\d]+', re.IGNORECASE),
    re.compile(r'\btranslator\'?s? note', re.IGNORECASE),
    re.compile(r'\beditor\'?s? note', re.IGNORECASE),
    re.compile(r'\bHoughton Mifflin\b', re.IGNORECASE),  # Publisher name
    re.compile(r'\bOxford University Press\b', re.IGNORECASE),
    re.compile(r'\bPenguin Books?\b', re.IGNORECASE),
    re.compile(r'\bPoetry Foundation\b', re.IGNORECASE),
]

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

def detect_metadata_in_text(lines):
    """Detect metadata lines at the end of a poem."""
    if len(lines) < 5:
        return [], []

    # Check last 10 lines for metadata
    check_lines = lines[-10:]
    metadata_lines = []
    patterns_found = []

    for i, line in enumerate(check_lines):
        line_stripped = line.strip()

        if not line_stripped:
            continue

        # Check against patterns
        for pattern in METADATA_PATTERNS:
            if pattern.search(line_stripped):
                # Store the actual line index from end of file
                actual_index = len(lines) - len(check_lines) + i
                metadata_lines.append(actual_index)
                patterns_found.append((actual_index, pattern.pattern[:50], line_stripped[:100]))
                break

    return metadata_lines, patterns_found

def find_metadata_start(lines, metadata_lines):
    """Find where metadata section starts (first empty line before metadata)."""
    if not metadata_lines:
        return None

    first_metadata_line = min(metadata_lines)

    # Search backwards from first metadata line to find empty line or poem end
    for i in range(first_metadata_line - 1, max(0, first_metadata_line - 10), -1):
        if not lines[i].strip():
            # Found empty line, metadata starts after this
            return i + 1

    # No empty line found, metadata starts at first detected line
    return first_metadata_line

def analyze_file(row):
    """Analyze a single file for metadata."""
    filepath = get_file_path(row)
    if not filepath:
        return None

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    if len(lines) < 5:
        return None

    # Detect metadata
    metadata_lines, patterns_found = detect_metadata_in_text(lines)

    if not metadata_lines:
        return None

    # Find where to cut
    metadata_start = find_metadata_start(lines, metadata_lines)

    if metadata_start is None:
        return None

    # Create cleaned version
    clean_lines = lines[:metadata_start]
    clean_text = ''.join(clean_lines).strip()

    # Skip if we'd remove more than 30% of the file
    original_length = sum(len(line.strip()) for line in lines)
    clean_length = sum(len(line.strip()) for line in clean_lines)

    if original_length > 0 and clean_length / original_length < 0.7:
        return None  # Would remove too much

    return {
        'filepath': filepath,
        'filename': row['filename'],
        'title': row['title'],
        'author': row['author'],
        'metadata_start': metadata_start,
        'metadata_lines': metadata_lines,
        'patterns_found': patterns_found,
        'lines_removed': len(lines) - len(clean_lines),
        'clean_text': clean_text,
        'original_lines': lines
    }

def scan_corpus():
    """Scan entire corpus for metadata."""
    print("=" * 80)
    print("METADATA DETECTION")
    print("=" * 80)
    print(f"DRY RUN: {DRY_RUN}")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning for editorial metadata...")
    flagged = []

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        result = analyze_file(row)
        if result:
            flagged.append(result)

    print(f"\n✓ Found {len(flagged):,} files with metadata")

    # Statistics
    total_lines_to_remove = sum(f['lines_removed'] for f in flagged)
    pattern_counts = Counter()
    for item in flagged:
        for _, pattern, _ in item['patterns_found']:
            pattern_counts[pattern] += 1

    print(f"\nStatistics:")
    print(f"  Total metadata lines to remove: {total_lines_to_remove:,}")
    print(f"\nMost common patterns:")
    for pattern, count in pattern_counts.most_common(10):
        print(f"  {pattern[:60]}: {count:,}")

    return flagged

def generate_report(flagged):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Metadata Detection Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files with metadata:** {len(flagged):,}\n")
        f.write(f"- **Total metadata lines:** {sum(item['lines_removed'] for item in flagged):,}\n\n")

        # Pattern frequency
        pattern_counts = Counter()
        for item in flagged:
            for _, pattern, _ in item['patterns_found']:
                pattern_counts[pattern] += 1

        f.write("## Pattern Frequencies\n\n")
        f.write("| Pattern | Count |\n")
        f.write("|---------|-------|\n")
        for pattern, count in pattern_counts.most_common():
            f.write(f"| `{pattern[:60]}` | {count:,} |\n")

        # Examples
        f.write("\n## Examples (First 30)\n\n")

        for i, item in enumerate(flagged[:30]):
            f.write(f"### {i+1}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Metadata starts at line:** {item['metadata_start'] + 1}\n")
            f.write(f"- **Lines to remove:** {item['lines_removed']}\n\n")

            f.write("**Detected patterns:**\n\n")
            for line_num, pattern, text in item['patterns_found']:
                f.write(f"- Line {line_num + 1}: `{pattern[:50]}`\n")
                f.write(f"  ```\n  {text}\n  ```\n\n")

            f.write("**Metadata to remove:**\n\n")
            f.write("```\n")
            metadata_lines = item['original_lines'][item['metadata_start']:]
            for line in metadata_lines[:10]:  # Show first 10 lines of metadata
                f.write(line.rstrip()[:100] + '\n')
            f.write("```\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Also save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/complete_metadata_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Complete List of Files with Metadata ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")
        for i, item in enumerate(flagged, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines to remove: {item['lines_removed']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def apply_cleaning(flagged):
    """Apply metadata removal to files."""
    print("\n" + "=" * 80)
    print("APPLYING METADATA REMOVAL")
    print("=" * 80)

    cleaned = 0
    errors = 0

    for i, item in enumerate(flagged):
        if i % 1000 == 0 and i > 0:
            print(f"  Cleaned {i:,}/{len(flagged):,}...")

        try:
            with open(item['filepath'], 'w', encoding='utf-8') as f:
                f.write(item['clean_text'])
            cleaned += 1
        except Exception as e:
            print(f"\n  Error cleaning {item['filename']}: {e}")
            errors += 1

    print(f"\n✓ Cleaned {cleaned:,} files")
    if errors:
        print(f"✗ Errors: {errors}")

    return cleaned, errors

def main():
    print("Metadata Detection and Removal")
    print("Removes editorial metadata from poem files\n")

    # Scan corpus
    flagged = scan_corpus()

    if not flagged:
        print("\nNo metadata found!")
        return

    # Generate report
    generate_report(flagged)

    if DRY_RUN:
        print("\n" + "=" * 80)
        print("DRY RUN - No files modified")
        print("=" * 80)
        print(f"Would clean {len(flagged):,} files")
        print(f"Would remove {sum(f['lines_removed'] for f in flagged):,} lines")
        print("\nSet DRY_RUN = False to apply cleaning")
    else:
        cleaned, errors = apply_cleaning(flagged)

        print("\n" + "=" * 80)
        print("CLEANING COMPLETE")
        print("=" * 80)
        print(f"✓ Cleaned {cleaned:,} files")
        print(f"✓ Removed {sum(f['lines_removed'] for f in flagged):,} metadata lines")

if __name__ == '__main__':
    main()
