#!/usr/bin/env python3
"""
Dry run of file splitting - shows what would happen and creates samples.
"""

import re
import csv
import json
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/split_dry_run_report.md")
SAMPLE_DIR = Path("/Users/justin/Repos/AI Project/scripts/split_samples")

# Create sample directory
SAMPLE_DIR.mkdir(exist_ok=True)

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
    """Check if a line looks like a poem title - VERY CONSERVATIVE."""
    line = line.strip()
    if not line or len(line) > 80:  # Titles shouldn't be super long
        return False
    if line.islower():
        return False

    # EXCLUDE simple numerals - these are stanza numbers
    if re.match(r'^[IVX]+\.?$', line):
        return False
    if re.match(r'^\d+\.?$', line):
        return False

    # ONLY INCLUDE numbered titles with substantial text: "1. Actual Title Here"
    # Require at least 3 words after the number
    numbered_match = re.match(r'^([IVX]+|\d+)[\.\)]\s+(.+)$', line)
    if numbered_match:
        title_text = numbered_match.group(2)
        words = title_text.split()
        # Must have at least 2 words and be title case
        if len(words) >= 2:
            cap_words = sum(1 for w in words if w and w[0].isupper())
            if cap_words >= len(words) * 0.7:  # 70% capitalized
                return True

    return False  # Don't trust anything else

def detect_section_breaks(lines):
    """Detect natural section breaks."""
    breaks = []
    blank_count = 0

    for i, line in enumerate(lines):
        if not line.strip():
            blank_count += 1
        else:
            if blank_count >= 2:
                breaks.append(i - blank_count)
            blank_count = 0

    return breaks

def split_file(filepath):
    """Split file into individual poems."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return None

    if len(lines) < 50:
        return None

    # Detect split points
    title_positions = []
    for i, line in enumerate(lines):
        if is_likely_title(line.strip()):
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not is_likely_title(next_line):
                    title_positions.append({
                        'line_num': i,
                        'text': line.strip(),
                        'type': 'title'
                    })

    section_breaks = detect_section_breaks(lines)

    # Combine split points
    split_points = []
    for title in title_positions:
        split_points.append(title)

    for break_line in section_breaks:
        near_title = any(abs(break_line - t['line_num']) < 5 for t in title_positions)
        if not near_title:
            split_points.append({
                'line_num': break_line,
                'text': '(section break)',
                'type': 'break'
            })

    split_points.sort(key=lambda x: x['line_num'])

    # Filter close splits
    filtered_splits = []
    last_split = 0
    for split in split_points:
        if split['line_num'] - last_split >= 10:
            filtered_splits.append(split)
            last_split = split['line_num']

    if len(filtered_splits) < 2:
        return None

    # Create poem chunks
    poems = []
    split_lines = [0] + [s['line_num'] for s in filtered_splits] + [len(lines)]

    for i in range(len(split_lines) - 1):
        start = split_lines[i]
        end = split_lines[i + 1]

        poem_lines = lines[start:end]

        # Clean up: remove leading/trailing blank lines
        while poem_lines and not poem_lines[0].strip():
            poem_lines.pop(0)
        while poem_lines and not poem_lines[-1].strip():
            poem_lines.pop()

        if poem_lines:
            # Try to extract title
            first_line = poem_lines[0].strip()
            if is_likely_title(first_line):
                title = first_line
                content = ''.join(poem_lines[1:])
            else:
                title = f"Untitled {i+1}"
                content = ''.join(poem_lines)

            poems.append({
                'title': title,
                'content': content,
                'start_line': start + 1,
                'end_line': end,
                'line_count': len(poem_lines)
            })

    return poems

def dry_run_analysis():
    """Analyze what would happen if we split files."""
    print("=" * 80)
    print("FILE SPLITTING DRY RUN")
    print("=" * 80)
    print("Analyzing splits without modifying files...")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nAnalyzing potential splits...")

    stats = {
        'total_files_checked': 0,
        'files_to_split': 0,
        'total_current_poems': len(rows),
        'total_new_poems': 0,
        'split_distribution': Counter(),
        'samples': []
    }

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Analyzed {i:,}/{len(rows):,}...")

        stats['total_files_checked'] += 1

        filepath = get_file_path(row)
        if not filepath:
            stats['total_new_poems'] += 1  # Keep as 1 poem
            continue

        poems = split_file(filepath)

        if poems and len(poems) >= 2:
            stats['files_to_split'] += 1
            stats['total_new_poems'] += len(poems)
            stats['split_distribution'][len(poems)] += 1

            # Save first 20 as samples
            if len(stats['samples']) < 20:
                stats['samples'].append({
                    'filename': row['filename'],
                    'title': row['title'],
                    'author': row['author'],
                    'filepath': str(filepath),
                    'poems': poems
                })
        else:
            stats['total_new_poems'] += 1  # Keep as 1 poem

    print(f"\n✓ Analysis complete")
    return stats

def create_sample_splits(stats):
    """Create actual sample splits for review."""
    print("\n" + "=" * 80)
    print("CREATING SAMPLE SPLITS")
    print("=" * 80)

    for i, sample in enumerate(stats['samples'], 1):
        sample_subdir = SAMPLE_DIR / f"sample_{i:02d}"
        sample_subdir.mkdir(exist_ok=True)

        # Write original file
        original_path = Path(sample['filepath'])
        with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()

        with open(sample_subdir / "ORIGINAL.txt", 'w', encoding='utf-8') as f:
            f.write(f"Original file: {sample['filename']}\n")
            f.write(f"Title: {sample['title']}\n")
            f.write(f"Author: {sample['author']}\n")
            f.write("=" * 80 + "\n\n")
            f.write(original_content)

        # Write split poems
        for j, poem in enumerate(sample['poems'], 1):
            poem_filename = f"poem_{j:02d}_{poem['title'][:50]}.txt"
            # Clean filename
            poem_filename = re.sub(r'[^\w\s\-\.]', '_', poem_filename)

            with open(sample_subdir / poem_filename, 'w', encoding='utf-8') as f:
                f.write(poem['content'])

        # Write manifest
        with open(sample_subdir / "MANIFEST.txt", 'w', encoding='utf-8') as f:
            f.write(f"Sample {i}: {sample['filename']}\n")
            f.write(f"Author: {sample['author']}\n")
            f.write(f"Original Title: {sample['title']}\n")
            f.write(f"\nSplit into {len(sample['poems'])} poems:\n\n")
            for j, poem in enumerate(sample['poems'], 1):
                f.write(f"{j}. {poem['title']}\n")
                f.write(f"   Lines {poem['start_line']}-{poem['end_line']} ({poem['line_count']} lines)\n\n")

        print(f"  Created sample {i}: {len(sample['poems'])} poems from {sample['filename']}")

    print(f"\n✓ Samples saved to: {SAMPLE_DIR}")

def generate_report(stats):
    """Generate dry run report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# File Splitting Dry Run Report\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Files checked:** {stats['total_files_checked']:,}\n")
        f.write(f"- **Files to split:** {stats['files_to_split']:,}\n")
        f.write(f"- **Current total poems:** {stats['total_current_poems']:,}\n")
        f.write(f"- **After splitting:** {stats['total_new_poems']:,} poems\n")
        f.write(f"- **Net increase:** +{stats['total_new_poems'] - stats['total_current_poems']:,} poems\n\n")

        f.write("## Split Distribution\n\n")
        f.write("Files split into N poems:\n\n")
        for count in sorted(stats['split_distribution'].keys()):
            num_files = stats['split_distribution'][count]
            f.write(f"- **{count} poems:** {num_files:,} files\n")
        f.write("\n")

        f.write("## Impact Analysis\n\n")
        percent_increase = ((stats['total_new_poems'] - stats['total_current_poems']) /
                           stats['total_current_poems'] * 100)
        f.write(f"- Corpus will increase by **{percent_increase:.1f}%**\n")
        f.write(f"- {(stats['files_to_split'] / stats['total_files_checked'] * 100):.1f}% of files will be split\n\n")

        f.write("## Sample Splits\n\n")
        f.write(f"Created {len(stats['samples'])} sample splits for manual review.\n\n")
        f.write(f"Location: `{SAMPLE_DIR}`\n\n")

        for i, sample in enumerate(stats['samples'], 1):
            f.write(f"### Sample {i}: `{sample['filename']}`\n\n")
            f.write(f"- **Author:** {sample['author']}\n")
            f.write(f"- **Original Title:** {sample['title']}\n")
            f.write(f"- **Splits into:** {len(sample['poems'])} poems\n\n")

            f.write("**Detected poems:**\n\n")
            for j, poem in enumerate(sample['poems'], 1):
                f.write(f"{j}. **{poem['title']}** (lines {poem['start_line']}-{poem['end_line']}, {poem['line_count']} lines)\n")
            f.write("\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

def main():
    print("File Splitting Dry Run")
    print("Shows what would happen without modifying files\n")

    # Run analysis
    stats = dry_run_analysis()

    # Create sample splits
    create_sample_splits(stats)

    # Generate report
    generate_report(stats)

    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE")
    print("=" * 80)
    print(f"✓ Files to split: {stats['files_to_split']:,}")
    print(f"✓ Current poems: {stats['total_current_poems']:,}")
    print(f"✓ After splitting: {stats['total_new_poems']:,}")
    print(f"✓ Net increase: +{stats['total_new_poems'] - stats['total_current_poems']:,}")
    print(f"\n✓ Review samples in: {SAMPLE_DIR}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
