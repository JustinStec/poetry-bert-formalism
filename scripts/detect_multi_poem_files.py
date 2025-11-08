#!/usr/bin/env python3
"""
Detect files containing multiple poems that should be split.
Now that the corpus is clean, we can get accurate results.
"""

import re
import csv
from pathlib import Path
from collections import Counter, defaultdict

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/multi_poem_detection_report.md")

# Detection thresholds
MIN_LINES_FOR_MULTI = 50  # Files must be at least this long to check
MIN_POEMS_TO_FLAG = 2  # Must detect at least this many poems

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

def is_likely_title(line):
    """Check if a line looks like a poem title."""
    line = line.strip()

    # Skip empty lines
    if not line:
        return False

    # Skip very long lines (likely part of poem)
    if len(line) > 100:
        return False

    # Skip lines that are all lowercase (likely part of poem)
    if line.islower():
        return False

    # Title-like patterns:
    # 1. Title Case With Each Word Capitalized
    # 2. ALL CAPS TITLES
    # 3. Roman numerals: I, II, III, IV, etc.
    # 4. Numbers: 1, 2, 3, etc.
    # 5. Common title formats

    # EXCLUDE simple numerals - these are stanza numbers, not poem titles
    # Roman numerals alone: I, II, III, IV, etc.
    if re.match(r'^[IVX]+\.?$', line):
        return False
    # Arabic numerals alone: 1, 2, 3, 4, etc.
    if re.match(r'^\d+\.?$', line):
        return False

    # INCLUDE numbered titles with actual text: "1. Title" or "I. Title"
    if re.match(r'^([IVX]+|\d+)[\.\)]\s+[A-Z]', line):
        return True

    # Title case (multiple capitalized words)
    words = line.split()
    if len(words) >= 2:
        # At least 2 words, and most words are capitalized
        cap_words = sum(1 for w in words if w and w[0].isupper())
        if cap_words >= len(words) * 0.6:  # 60% of words capitalized
            return True

    # ALL CAPS
    if line.isupper() and len(line) >= 3:
        return True

    return False

def detect_section_breaks(lines):
    """Detect natural section breaks (multiple blank lines)."""
    breaks = []
    blank_count = 0

    for i, line in enumerate(lines):
        if not line.strip():
            blank_count += 1
        else:
            if blank_count >= 2:  # 2+ blank lines = section break
                breaks.append(i - blank_count)
            blank_count = 0

    return breaks

def detect_multi_poem(filepath):
    """Detect if file contains multiple poems."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    # Filter out completely empty lines for analysis
    non_empty_lines = [l for l in lines if l.strip()]

    # Skip short files
    if len(non_empty_lines) < MIN_LINES_FOR_MULTI:
        return None

    # Detect potential titles
    title_positions = []
    for i, line in enumerate(lines):
        if is_likely_title(line.strip()):
            # Make sure it's followed by content (not another title immediately)
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # Skip if next line is also a title (likely not real titles)
                if next_line and not is_likely_title(next_line):
                    title_positions.append({
                        'line_num': i + 1,  # 1-indexed
                        'text': line.strip(),
                        'type': 'title'
                    })

    # Detect section breaks
    section_breaks = detect_section_breaks(lines)

    # Combine evidence
    split_points = []

    # Add titles as split points
    for title in title_positions:
        split_points.append(title)

    # Add section breaks that aren't already near titles
    for break_line in section_breaks:
        # Check if there's already a title near this break
        near_title = any(abs(break_line - (t['line_num'] - 1)) < 5 for t in title_positions)
        if not near_title:
            split_points.append({
                'line_num': break_line + 1,
                'text': '(section break)',
                'type': 'break'
            })

    # Sort by line number
    split_points.sort(key=lambda x: x['line_num'])

    # Estimate number of poems
    # If we have multiple split points that divide the file into reasonable chunks
    if len(split_points) >= MIN_POEMS_TO_FLAG:
        # Filter out split points that are too close together
        filtered_splits = []
        last_split = 0

        for split in split_points:
            if split['line_num'] - last_split >= 10:  # At least 10 lines between splits
                filtered_splits.append(split)
                last_split = split['line_num']

        if len(filtered_splits) >= MIN_POEMS_TO_FLAG:
            return {
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'estimated_poems': len(filtered_splits),
                'split_points': filtered_splits[:20],  # First 20 for report
                'confidence': 'high' if len(title_positions) >= 3 else 'medium'
            }

    return None

def scan_corpus():
    """Scan entire corpus for multi-poem files."""
    print("=" * 80)
    print("MULTI-POEM FILE DETECTION")
    print("=" * 80)
    print(f"Minimum file length: {MIN_LINES_FOR_MULTI} lines")
    print(f"Minimum poems to flag: {MIN_POEMS_TO_FLAG}")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning for multi-poem files...")
    flagged = []
    confidence_counts = Counter()

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = detect_multi_poem(filepath)
        if result:
            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'filepath': filepath,
                **result
            })
            confidence_counts[result['confidence']] += 1

    print(f"\n✓ Found {len(flagged):,} multi-poem files")

    # Statistics
    print(f"\nConfidence levels:")
    for conf in ['high', 'medium', 'low']:
        if conf in confidence_counts:
            print(f"  {conf.capitalize()}: {confidence_counts[conf]:,} files")

    # Poem count distribution
    poem_counts = Counter(f['estimated_poems'] for f in flagged)
    print(f"\nPoem count distribution:")
    for count in sorted(poem_counts.keys()):
        print(f"  {count} poems: {poem_counts[count]:,} files")

    return flagged, confidence_counts

def generate_report(flagged, confidence_counts):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by estimated poems (most first)
    flagged_sorted = sorted(flagged, key=lambda x: (-x['estimated_poems'], -x['total_lines']))

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Multi-Poem File Detection Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Multi-poem files detected:** {len(flagged):,}\n")
        f.write(f"- **Total corpus:** 167,215 files\n")
        f.write(f"- **Single-poem files:** {167215 - len(flagged):,}\n\n")

        f.write("## Confidence Levels\n\n")
        for conf in ['high', 'medium', 'low']:
            if conf in confidence_counts:
                f.write(f"- **{conf.capitalize()}:** {confidence_counts[conf]:,} files\n")
        f.write("\n")

        # Poem count distribution
        poem_counts = Counter(item['estimated_poems'] for item in flagged)
        f.write("## Poem Count Distribution\n\n")
        for count in sorted(poem_counts.keys()):
            f.write(f"- **{count} poems:** {poem_counts[count]:,} files\n")
        f.write("\n")

        # Top files by poem count
        f.write("## Files with Most Poems (Top 100)\n\n")
        for i, item in enumerate(flagged_sorted[:100], 1):
            f.write(f"### {i}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Estimated poems:** {item['estimated_poems']}\n")
            f.write(f"- **Total lines:** {item['total_lines']}\n")
            f.write(f"- **Confidence:** {item['confidence']}\n\n")

            f.write("**Detected split points:**\n\n")
            for split in item['split_points'][:10]:  # First 10
                f.write(f"- Line {split['line_num']}: `{split['text'][:80]}`\n")
            f.write("\n")

        if len(flagged_sorted) > 100:
            f.write(f"\n... and {len(flagged_sorted) - 100} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/multi_poem_files_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Multi-Poem Files ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(flagged_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Estimated poems: {item['estimated_poems']}\n")
            f.write(f"   Confidence: {item['confidence']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Multi-Poem File Detection")
    print("Identifies files containing multiple poems\n")

    # Scan corpus
    flagged, confidence_counts = scan_corpus()

    if not flagged:
        print("\n✓ No multi-poem files found!")
        return

    # Generate report
    generate_report(flagged, confidence_counts)

    print("\n" + "=" * 80)
    print("DETECTION COMPLETE")
    print("=" * 80)
    print(f"✓ Multi-poem files detected: {len(flagged):,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
