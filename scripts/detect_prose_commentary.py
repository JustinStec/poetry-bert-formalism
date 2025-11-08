#!/usr/bin/env python3
"""
Detect prose commentary/metadata that appears after poems.
These are harder to catch with simple patterns - they're biographical/
historical context added as prose paragraphs after verse ends.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/prose_commentary_report.md")

# Settings
DRY_RUN = True  # Set to False to apply changes
MIN_PROSE_LINE_LENGTH = 80  # Prose lines tend to be longer than verse

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

def analyze_line_lengths(lines):
    """Calculate average line length, excluding empty lines."""
    non_empty = [len(line.strip()) for line in lines if line.strip()]
    if non_empty:
        return sum(non_empty) / len(non_empty)
    return 0

def detect_verse_to_prose_transition(lines):
    """
    Detect transition from verse (short lines) to prose (long lines).
    Returns index where prose commentary starts, or None.
    """
    if len(lines) < 10:
        return None

    # Analyze in chunks - last 20 lines
    check_lines = lines[-20:]

    # Find where long prose lines start
    prose_start = None
    prose_count = 0
    first_prose_idx = None

    for i in range(len(check_lines) - 3):  # Need at least 3 lines to confirm
        line = check_lines[i].strip()

        # Skip empty lines (don't reset count - prose can have empty lines between paragraphs)
        if not line:
            continue

        # Check if this looks like prose (long line, full sentences)
        if len(line) >= MIN_PROSE_LINE_LENGTH:
            if first_prose_idx is None:
                first_prose_idx = i
            prose_count += 1

            # If we have 2+ prose lines (even with gaps), likely prose commentary
            if prose_count >= 2 and prose_start is None:
                # Map back to actual line index
                prose_start = len(lines) - len(check_lines) + first_prose_idx
        else:
            # Short line - reset if we haven't confirmed prose yet
            if prose_count < 2:
                prose_count = 0
                first_prose_idx = None

    return prose_start

def has_biographical_markers(text):
    """Check if text contains biographical/contextual markers."""
    markers = [
        r'\b(is|was) best (known|remembered) for\b',
        r'\ban inept\b',
        r'\bthe poet(\'s|ess)?\b',
        r'\bthe author\b',
        r'\bthis (poem|work)\b',
        r'\bpoems? like\b',
        r'\b(citizens|ladies|people) of\b',
        r'\bnicknames? bestowed\b',
        r'\bbiographical\b',
        r'\bhistorical context\b',
    ]

    for pattern in markers:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_footnote_markers(lines):
    """Check if lines contain footnote markers."""
    footnote_patterns = [
        r'^\s*\[\d+\]',  # [1], [2], etc.
        r'^\s*\d+\.',     # 1., 2., etc. at start of line
        r'^\s*\*+\s',     # *, **, *** at start
        r'^\s*(note|footnote|fn):',  # "Note:", "Footnote:", etc.
        r'^\s*\(\d+\)',   # (1), (2), etc.
    ]

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        for pattern in footnote_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
    return False

def analyze_file(row):
    """Analyze a single file for prose commentary."""
    filepath = get_file_path(row)
    if not filepath:
        return None

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    if len(lines) < 10:
        return None

    # Detect verse-to-prose transition
    prose_start = detect_verse_to_prose_transition(lines)

    if prose_start is None:
        return None

    # Get the prose section
    prose_section = ''.join(lines[prose_start:]).strip()
    prose_lines = lines[prose_start:]

    # Additional check: does it have biographical markers or footnote markers?
    has_bio = has_biographical_markers(prose_section)
    has_footnotes = has_footnote_markers(prose_lines)

    if not has_bio and not has_footnotes and len(prose_section) < 200:
        return None  # Might be legitimate verse

    # Calculate line length difference
    verse_section = lines[:prose_start]
    prose_lines = lines[prose_start:]

    avg_verse_length = analyze_line_lengths(verse_section)
    avg_prose_length = analyze_line_lengths(prose_lines)

    # Only flag if prose is significantly longer than verse
    if avg_prose_length < avg_verse_length * 1.5:
        return None

    # Clean text without prose
    clean_text = ''.join(verse_section).strip()

    return {
        'filepath': filepath,
        'filename': row['filename'],
        'title': row['title'],
        'author': row['author'],
        'prose_start': prose_start,
        'prose_preview': prose_section[:300],
        'avg_verse_length': round(avg_verse_length, 1),
        'avg_prose_length': round(avg_prose_length, 1),
        'lines_removed': len(prose_lines),
        'clean_text': clean_text,
    }

def scan_corpus():
    """Scan entire corpus for prose commentary."""
    print("=" * 80)
    print("PROSE COMMENTARY DETECTION")
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

    print("\nScanning for prose commentary...")
    flagged = []

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        result = analyze_file(row)
        if result:
            flagged.append(result)

    print(f"\n✓ Found {len(flagged):,} files with prose commentary")

    # Statistics
    total_lines = sum(f['lines_removed'] for f in flagged)

    print(f"\nStatistics:")
    print(f"  Total prose lines to remove: {total_lines:,}")
    print(f"  Average prose line length: {sum(f['avg_prose_length'] for f in flagged) / len(flagged):.1f}")
    print(f"  Average verse line length: {sum(f['avg_verse_length'] for f in flagged) / len(flagged):.1f}")

    return flagged

def generate_report(flagged):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Prose Commentary Detection Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Files with prose commentary:** {len(flagged):,}\n")
        f.write(f"- **Total prose lines:** {sum(item['lines_removed'] for item in flagged):,}\n\n")

        # Examples
        f.write("## Examples (First 50)\n\n")

        for i, item in enumerate(flagged[:50]):
            f.write(f"### {i+1}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Prose starts at line:** {item['prose_start'] + 1}\n")
            f.write(f"- **Lines to remove:** {item['lines_removed']}\n")
            f.write(f"- **Avg verse line length:** {item['avg_verse_length']}\n")
            f.write(f"- **Avg prose line length:** {item['avg_prose_length']}\n\n")

            f.write("**Prose commentary preview:**\n\n")
            f.write("```\n")
            f.write(item['prose_preview'])
            f.write("\n```\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/prose_commentary_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Complete List of Files with Prose Commentary ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")
        for i, item in enumerate(flagged, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Lines to remove: {item['lines_removed']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def apply_cleaning(flagged):
    """Apply prose commentary removal to files."""
    print("\n" + "=" * 80)
    print("APPLYING PROSE COMMENTARY REMOVAL")
    print("=" * 80)

    cleaned = 0
    errors = 0

    for i, item in enumerate(flagged):
        if i % 1000 == 0 and i > 0:
            print(f"  Cleaned {i:,}/{len(flagged):,}...")

        try:
            with open(item['filepath'], 'w', encoding='utf-8') as f:
                f.write(item['clean_text'] + '\n')
            cleaned += 1
        except Exception as e:
            print(f"\n  Error cleaning {item['filename']}: {e}")
            errors += 1

    print(f"\n✓ Cleaned {cleaned:,} files")
    if errors:
        print(f"✗ Errors: {errors}")

    return cleaned, errors

def main():
    print("Prose Commentary Detection and Removal")
    print("Detects biographical/contextual prose after verse poems\n")

    # Scan corpus
    flagged = scan_corpus()

    if not flagged:
        print("\nNo prose commentary found!")
        return

    # Generate report
    generate_report(flagged)

    if DRY_RUN:
        print("\n" + "=" * 80)
        print("DRY RUN - No files modified")
        print("=" * 80)
        print(f"Would clean {len(flagged):,} files")
        print(f"Would remove {sum(f['lines_removed'] for f in flagged):,} prose lines")
        print("\nSet DRY_RUN = False to apply cleaning")
    else:
        cleaned, errors = apply_cleaning(flagged)

        print("\n" + "=" * 80)
        print("CLEANING COMPLETE")
        print("=" * 80)
        print(f"✓ Cleaned {cleaned:,} files")
        print(f"✓ Removed {sum(f['lines_removed'] for f in flagged):,} prose lines")

if __name__ == '__main__':
    main()
