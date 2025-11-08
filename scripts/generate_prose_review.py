#!/usr/bin/env python3
"""
Generate detailed review file showing context around prose commentary.
"""

import csv
from pathlib import Path

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
FLAGGED_LIST = Path("/Users/justin/Repos/AI Project/scripts/prose_commentary_list.txt")
REVIEW_FILE = Path("/Users/justin/Repos/AI Project/scripts/prose_removal_review.txt")

CONTEXT_LINES = 5  # Lines of verse to show before prose

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

def parse_flagged_list():
    """Parse the flagged list to get filenames and line numbers."""
    flagged = {}

    with open(FLAGGED_LIST, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_filename = None
    for line in lines:
        line = line.strip()

        # Look for numbered entries with filenames
        if line and line[0].isdigit() and '.' in line[:10]:
            # Extract filename (after number and space)
            parts = line.split(' ', 1)
            if len(parts) > 1:
                current_filename = parts[1]
                flagged[current_filename] = {}
        elif current_filename and 'Lines to remove:' in line:
            # Extract line number
            parts = line.split(':')
            if len(parts) > 1:
                try:
                    lines_to_remove = int(parts[1].strip())
                    flagged[current_filename]['lines_to_remove'] = lines_to_remove
                except:
                    pass

    return flagged

def generate_review():
    """Generate review file with context."""
    print("Generating prose commentary review file...")

    # Load metadata
    print("\nLoading metadata...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Parse flagged list
    print("Parsing flagged list...")
    flagged = parse_flagged_list()

    print(f"Found {len(flagged)} flagged files")

    # Load detection results
    print("Re-running detection to get exact line numbers...")
    from detect_prose_commentary import analyze_file

    results = []
    for row in rows:
        if row['filename'] in flagged:
            result = analyze_file(row)
            if result:
                results.append(result)

    print(f"Loaded {len(results)} detection results")

    # Generate review file
    print(f"\nGenerating review file: {REVIEW_FILE}")

    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("PROSE COMMENTARY REMOVAL REVIEW\n")
        f.write("=" * 100 + "\n")
        f.write(f"Total files: {len(results)}\n")
        f.write(f"Total prose lines to remove: {sum(r['lines_removed'] for r in results)}\n")
        f.write("\n")
        f.write("Review each entry below. The format is:\n")
        f.write("  [VERSE CONTEXT] - Last few lines of the poem (context)\n")
        f.write("  [PROSE TO REMOVE] - The prose commentary to be removed\n")
        f.write("=" * 100 + "\n\n")

        for i, result in enumerate(results, 1):
            filepath = result['filepath']

            # Read file
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
            except:
                continue

            prose_start = result['prose_start']

            # Get context lines (verse before prose)
            context_start = max(0, prose_start - CONTEXT_LINES)
            verse_context = lines[context_start:prose_start]

            # Get prose lines to remove
            prose_lines = lines[prose_start:]

            # Write to review file
            f.write(f"{'=' * 100}\n")
            f.write(f"#{i}: {result['filename']}\n")
            f.write(f"{'=' * 100}\n")
            f.write(f"Title: {result['title']}\n")
            f.write(f"Author: {result['author']}\n")
            f.write(f"Prose starts at line: {prose_start + 1}\n")
            f.write(f"Lines to remove: {result['lines_removed']}\n")
            f.write(f"Avg verse line length: {result['avg_verse_length']}\n")
            f.write(f"Avg prose line length: {result['avg_prose_length']}\n")
            f.write("\n")

            # Show verse context
            f.write("[VERSE CONTEXT - Last few lines of poem]\n")
            f.write("-" * 100 + "\n")
            for j, line in enumerate(verse_context, start=context_start + 1):
                f.write(f"{j:4d}: {line.rstrip()}\n")
            f.write("\n")

            # Show prose to remove
            f.write("[PROSE TO REMOVE - Will be deleted]\n")
            f.write("-" * 100 + "\n")
            for j, line in enumerate(prose_lines, start=prose_start + 1):
                f.write(f"{j:4d}: {line.rstrip()}\n")

            f.write("\n\n")

    print(f"✓ Review file saved: {REVIEW_FILE}")
    print(f"\nReview this file to check for false positives.")
    print(f"Each entry shows verse context and the prose lines to be removed.")

if __name__ == '__main__':
    generate_review()
