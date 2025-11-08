#!/usr/bin/env python3
"""
Clean formatting artifacts from poem content:
- Standalone quotation marks on their own lines
- Decorative dividers (asterisks, dashes, underscores)
- Lines with only punctuation/whitespace
- Redundant title lines at start of poems
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/content_cleanup_report.md")

# Settings
DRY_RUN = False  # Set to False to apply changes

# Patterns for lines to remove
REMOVE_PATTERNS = [
    # Standalone quotation marks
    re.compile(r'^\s*["\'""'']+\s*$'),

    # Decorative dividers (5+ repeated characters)
    re.compile(r'^\s*[\*\-_=~]{5,}\s*$'),

    # Lines with only punctuation and spaces
    re.compile(r'^\s*[^\w\s]+\s*$'),
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

def normalize_whitespace(text):
    """Normalize whitespace but preserve line breaks."""
    # Remove trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)

def should_remove_line(line):
    """Check if line should be removed."""
    line_stripped = line.strip()

    if not line_stripped:
        return False  # Keep empty lines for stanza breaks

    # Check against removal patterns
    for pattern in REMOVE_PATTERNS:
        if pattern.match(line_stripped):
            return True

    return False

def remove_redundant_title(lines, title):
    """Remove redundant title line at start of poem if present."""
    if not lines or not title:
        return lines, False

    # Check first 3 non-empty lines
    for i in range(min(3, len(lines))):
        line = lines[i].strip()
        if line:
            # Normalize for comparison
            line_norm = line.lower().strip('.,!?;:')
            title_norm = title.lower().strip('.,!?;:')

            # Check if line matches title (with some flexibility)
            if line_norm == title_norm or title_norm in line_norm or line_norm in title_norm:
                # Check if it's similar enough
                if len(line_norm) > 3 and abs(len(line_norm) - len(title_norm)) < 20:
                    # Remove this line
                    return lines[:i] + lines[i+1:], True
            break  # Only check first non-empty line

    return lines, False

def clean_file_content(filepath, title):
    """Clean formatting artifacts from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    if not lines:
        return None

    # Skip redundant title removal - we need titles for multi-poem detection
    title_removed = False
    # lines, title_removed = remove_redundant_title(lines, title)

    # Remove formatting artifact lines
    clean_lines = []
    removed_lines = []

    for i, line in enumerate(lines):
        if should_remove_line(line):
            removed_lines.append((i, line.strip()))
        else:
            clean_lines.append(line)

    # Check if anything changed
    if not removed_lines and not title_removed:
        return None

    # Join and normalize whitespace
    clean_text = ''.join(clean_lines)
    clean_text = normalize_whitespace(clean_text)

    # Remove excessive empty lines (more than 2 consecutive)
    while '\n\n\n\n' in clean_text:
        clean_text = clean_text.replace('\n\n\n\n', '\n\n\n')

    # Ensure file ends with single newline
    clean_text = clean_text.rstrip() + '\n'

    return {
        'filepath': filepath,
        'filename': filepath.name,
        'lines_removed': len(removed_lines),
        'removed_lines': removed_lines[:10],  # Sample
        'title_removed': title_removed,
        'clean_text': clean_text,
        'original_line_count': len(lines),
        'clean_line_count': len(clean_text.split('\n'))
    }

def scan_corpus():
    """Scan entire corpus for formatting artifacts."""
    print("=" * 80)
    print("CONTENT FORMATTING CLEANUP")
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

    print("\nScanning for formatting artifacts...")
    flagged = []

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = clean_file_content(filepath, row['title'])
        if result:
            result['title'] = row['title']
            result['author'] = row['author']
            flagged.append(result)

    print(f"\n✓ Found {len(flagged):,} files with formatting artifacts")

    # Statistics
    total_lines_removed = sum(f['lines_removed'] for f in flagged)
    titles_removed = sum(1 for f in flagged if f['title_removed'])

    # Categorize removed lines
    pattern_types = Counter()
    for item in flagged:
        for _, line in item['removed_lines']:
            if re.match(r'^\s*["\'""'']+\s*$', line):
                pattern_types['standalone_quotes'] += 1
            elif re.match(r'^\s*[\*\-_=~]{5,}\s*$', line):
                pattern_types['dividers'] += 1
            else:
                pattern_types['other_punctuation'] += 1

    print(f"\nStatistics:")
    print(f"  Total lines to remove: {total_lines_removed:,}")
    print(f"  Redundant titles removed: {titles_removed:,}")
    print(f"\nBy type:")
    for pattern_type, count in pattern_types.most_common():
        print(f"  {pattern_type}: {count:,}")

    return flagged

def generate_report(flagged):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Content Formatting Cleanup Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files with formatting artifacts:** {len(flagged):,}\n")
        f.write(f"- **Total lines to remove:** {sum(item['lines_removed'] for item in flagged):,}\n")
        f.write(f"- **Redundant titles removed:** {sum(1 for item in flagged if item['title_removed']):,}\n\n")

        # Examples
        f.write("## Examples (First 30)\n\n")

        for i, item in enumerate(flagged[:30]):
            f.write(f"### {i+1}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Lines to remove:** {item['lines_removed']}\n")
            f.write(f"- **Redundant title removed:** {'Yes' if item['title_removed'] else 'No'}\n\n")

            if item['removed_lines']:
                f.write("**Sample removed lines:**\n\n")
                for line_num, line_text in item['removed_lines']:
                    f.write(f"- Line {line_num + 1}: `{line_text[:80]}`\n")
                f.write("\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/content_cleanup_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Complete List of Files to Clean ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")
        for i, item in enumerate(flagged, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines to remove: {item['lines_removed']}\n")
            if item['title_removed']:
                f.write(f"   Redundant title: removed\n")
            f.write("\n")

    print(f"✓ Complete list saved to: {list_file}")

def apply_cleaning(flagged):
    """Apply content cleanup to files."""
    print("\n" + "=" * 80)
    print("APPLYING CONTENT CLEANUP")
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
    print("Content Formatting Cleanup")
    print("Removes formatting artifacts from poem files\n")

    # Scan corpus
    flagged = scan_corpus()

    if not flagged:
        print("\nNo formatting artifacts found!")
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
        print(f"✓ Removed {sum(f['lines_removed'] for f in flagged):,} formatting lines")

if __name__ == '__main__':
    main()
