#!/usr/bin/env python3
"""
Detect and analyze lineation issues in poetry corpus.
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
import re

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/lineation_analysis_report.md")

# Thresholds
LONG_LINE_THRESHOLD = 200  # Lines longer than this are suspicious
VERY_LONG_LINE_THRESHOLD = 400  # Lines this long are almost certainly broken

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

def analyze_lineation(filepath):
    """Analyze a file for lineation issues."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    if not lines:
        return None

    # Calculate line length statistics
    line_lengths = [len(line.rstrip('\n\r')) for line in lines if line.strip()]

    if not line_lengths:
        return None

    max_length = max(line_lengths)
    avg_length = sum(line_lengths) / len(line_lengths)

    # Count problematic lines
    long_lines = sum(1 for l in line_lengths if l > LONG_LINE_THRESHOLD)
    very_long_lines = sum(1 for l in line_lengths if l > VERY_LONG_LINE_THRESHOLD)

    # Only flag if there are problematic lines
    if long_lines == 0:
        return None

    # Get the longest line for preview
    longest_line_idx = line_lengths.index(max_length)
    non_empty_lines = [line for line in lines if line.strip()]
    longest_line = non_empty_lines[longest_line_idx].strip()[:300] if longest_line_idx < len(non_empty_lines) else ""

    # Check if this looks like a prose poem vs broken lineation
    # Prose poems tend to have consistently long lines
    # Broken lineation tends to have a mix
    std_dev = (sum((l - avg_length) ** 2 for l in line_lengths) / len(line_lengths)) ** 0.5
    coefficient_of_variation = std_dev / avg_length if avg_length > 0 else 0

    # High CV suggests mixed line lengths (more likely broken lineation)
    # Low CV suggests consistent length (could be prose poem)
    likely_prose_poem = coefficient_of_variation < 0.5 and avg_length > 150

    return {
        'max_length': max_length,
        'avg_length': round(avg_length, 1),
        'total_lines': len(line_lengths),
        'long_lines': long_lines,
        'very_long_lines': very_long_lines,
        'longest_line': longest_line,
        'likely_prose_poem': likely_prose_poem,
        'cv': round(coefficient_of_variation, 2),
    }

def scan_corpus():
    """Scan entire corpus for lineation issues."""
    print("=" * 80)
    print("LINEATION ISSUE DETECTION")
    print("=" * 80)
    print(f"Long line threshold: {LONG_LINE_THRESHOLD} characters")
    print(f"Very long line threshold: {VERY_LONG_LINE_THRESHOLD} characters")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning for lineation issues...")
    flagged = []

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = analyze_lineation(filepath)
        if result:
            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'filepath': filepath,
                **result
            })

    print(f"\n✓ Found {len(flagged):,} files with lineation issues")

    # Statistics
    prose_poems = sum(1 for f in flagged if f['likely_prose_poem'])
    broken_lineation = len(flagged) - prose_poems
    very_long = sum(1 for f in flagged if f['very_long_lines'] > 0)

    print(f"\nStatistics:")
    print(f"  Files with long lines (>{LONG_LINE_THRESHOLD} chars): {len(flagged):,}")
    print(f"  Files with very long lines (>{VERY_LONG_LINE_THRESHOLD} chars): {very_long:,}")
    print(f"  Likely prose poems (consistent long lines): {prose_poems:,}")
    print(f"  Likely broken lineation (mixed line lengths): {broken_lineation:,}")

    return flagged

def generate_report(flagged):
    """Generate markdown report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by severity
    flagged_sorted = sorted(flagged, key=lambda x: (-x['max_length'], -x['long_lines']))

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Lineation Issue Analysis Report\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Total files with lineation issues:** {len(flagged):,}\n")
        f.write(f"- **Long line threshold:** {LONG_LINE_THRESHOLD} characters\n")
        f.write(f"- **Very long line threshold:** {VERY_LONG_LINE_THRESHOLD} characters\n\n")

        prose_poems = [f for f in flagged if f['likely_prose_poem']]
        broken = [f for f in flagged if not f['likely_prose_poem']]

        f.write(f"- **Likely prose poems:** {len(prose_poems):,}\n")
        f.write(f"- **Likely broken lineation:** {len(broken):,}\n\n")

        # Most severe cases (very long lines, likely broken)
        f.write("## Most Severe Cases (Likely Broken Lineation)\n\n")
        severe = [item for item in flagged_sorted if not item['likely_prose_poem'] and item['very_long_lines'] > 0]

        for i, item in enumerate(severe[:100], 1):
            f.write(f"### {i}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Max line length:** {item['max_length']} chars\n")
            f.write(f"- **Average line length:** {item['avg_length']} chars\n")
            f.write(f"- **Total lines:** {item['total_lines']}\n")
            f.write(f"- **Long lines:** {item['long_lines']}\n")
            f.write(f"- **Very long lines:** {item['very_long_lines']}\n")
            f.write(f"- **Coefficient of variation:** {item['cv']} (high = mixed lengths)\n\n")
            f.write("**Longest line preview:**\n\n")
            f.write(f"```\n{item['longest_line']}\n```\n\n")

        if len(severe) > 100:
            f.write(f"\n... and {len(severe) - 100} more severe cases\n\n")

        # Possible prose poems
        f.write("## Possible Prose Poems (Consistent Long Lines)\n\n")
        f.write("These files have consistently long lines and may be legitimate prose poems.\n\n")

        for i, item in enumerate(prose_poems[:50], 1):
            f.write(f"### {i}. `{item['filename']}`\n\n")
            f.write(f"- **Title:** {item['title']}\n")
            f.write(f"- **Author:** {item['author']}\n")
            f.write(f"- **Max line length:** {item['max_length']} chars\n")
            f.write(f"- **Average line length:** {item['avg_length']} chars\n")
            f.write(f"- **Coefficient of variation:** {item['cv']} (low = consistent lengths)\n\n")

        if len(prose_poems) > 50:
            f.write(f"\n... and {len(prose_poems) - 50} more possible prose poems\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/lineation_issues_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Files with Lineation Issues ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")

        f.write("BROKEN LINEATION (likely needs fixing):\n")
        f.write("-" * 100 + "\n\n")
        broken = [item for item in flagged if not item['likely_prose_poem']]
        for i, item in enumerate(broken, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Max line: {item['max_length']} chars, Avg: {item['avg_length']}\n\n")

        f.write("\n\nPROSE POEMS (likely legitimate):\n")
        f.write("-" * 100 + "\n\n")
        prose = [item for item in flagged if item['likely_prose_poem']]
        for i, item in enumerate(prose, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Avg line: {item['avg_length']} chars (CV: {item['cv']})\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Lineation Issue Detection")
    print("Identifies files with abnormally long lines\n")

    # Scan corpus
    flagged = scan_corpus()

    if not flagged:
        print("\nNo lineation issues found!")
        return

    # Generate report
    generate_report(flagged)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"✓ Total files flagged: {len(flagged):,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
