#!/usr/bin/env python3
"""
Apply prose commentary review decisions.
Removes prose from files marked 'discard', deletes files marked 'delete_file'.
"""

import json
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
DECISIONS_FILE = Path("/Users/justin/Repos/AI Project/scripts/prose_review_decisions.json")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/prose_application_report.md")

# Detection file for getting prose boundaries
from detect_prose_commentary import detect_verse_to_prose_transition

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

def main():
    print("=" * 80)
    print("APPLYING PROSE COMMENTARY DECISIONS")
    print("=" * 80)

    # Load decisions
    print("\nLoading decisions...")
    with open(DECISIONS_FILE, 'r') as f:
        decisions = json.load(f)

    # Count decisions (handle mixed string and dict formats)
    decision_values = []
    custom_boundaries = 0
    for v in decisions.values():
        if isinstance(v, dict):
            decision_values.append(v['decision'])
            if v.get('custom_boundary') is not None:
                custom_boundaries += 1
        else:
            decision_values.append(v)

    decision_counts = Counter(decision_values)

    print(f"\n✓ Loaded {len(decisions):,} decisions")
    print(f"  Keep (no action): {decision_counts['keep']:,}")
    print(f"  Discard (remove prose): {decision_counts['discard']:,}")
    print(f"  Delete file: {decision_counts['delete_file']:,}")

    if custom_boundaries > 0:
        print(f"  Files with custom boundaries: {custom_boundaries:,}")

    # Load metadata
    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
    print(f"✓ Loaded {len(rows):,} entries")

    # Track changes
    files_deleted = []
    prose_removed = []
    errors = []

    # Process each decision
    print("\n" + "=" * 80)
    print("PROCESSING FILES")
    print("=" * 80)

    for filename, decision_data in decisions.items():
        # Handle both string and dict formats
        if isinstance(decision_data, dict):
            decision = decision_data['decision']
            custom_boundary = decision_data.get('custom_boundary')
        else:
            decision = decision_data
            custom_boundary = None

        # Find the file
        file_row = None
        for row in rows:
            if row['filename'] == filename:
                file_row = row
                break

        if not file_row:
            errors.append(f"Could not find metadata for: {filename}")
            continue

        filepath = get_file_path(file_row)
        if not filepath:
            errors.append(f"Could not find file: {filename}")
            continue

        try:
            if decision == 'delete_file':
                # Delete the file
                filepath.unlink()
                files_deleted.append(filename)

            elif decision == 'discard':
                # Remove prose from file
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                # Determine prose boundary
                if custom_boundary is not None:
                    prose_start = custom_boundary
                else:
                    # Use automatic detection
                    prose_start = detect_verse_to_prose_transition(lines)

                if prose_start is None:
                    errors.append(f"Could not detect prose boundary: {filename}")
                    continue

                # Write cleaned text (everything before prose)
                clean_text = ''.join(lines[:prose_start]).strip()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(clean_text + '\n')

                lines_removed = len(lines) - prose_start
                prose_removed.append({
                    'filename': filename,
                    'lines_removed': lines_removed,
                    'prose_start': prose_start,
                    'custom': custom_boundary is not None
                })

            # 'keep' decision: do nothing

        except Exception as e:
            errors.append(f"Error processing {filename}: {e}")

    # Update metadata CSV to remove deleted files
    print("\n" + "=" * 80)
    print("UPDATING METADATA CSV")
    print("=" * 80)

    deleted_set = set(files_deleted)
    rows_to_keep = [row for row in rows if row['filename'] not in deleted_set]

    print(f"Removing {len(deleted_set):,} deleted files from metadata...")

    with open(UNIFIED_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_keep)

    print(f"✓ Updated metadata CSV ({len(rows_to_keep):,} entries remain)")

    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Prose Commentary Application Report\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total decisions processed:** {len(decisions):,}\n")
        f.write(f"- **Files kept (no action):** {decision_counts['keep']:,}\n")
        f.write(f"- **Files with prose removed:** {len(prose_removed):,}\n")
        f.write(f"- **Files deleted:** {len(files_deleted):,}\n")
        f.write(f"- **Errors encountered:** {len(errors)}\n\n")

        # Prose removal stats
        if prose_removed:
            total_lines = sum(p['lines_removed'] for p in prose_removed)
            custom_count = sum(1 for p in prose_removed if p['custom'])

            f.write("## Prose Removal Statistics\n\n")
            f.write(f"- **Total prose lines removed:** {total_lines:,}\n")
            f.write(f"- **Files with custom boundaries:** {custom_count:,}\n")
            f.write(f"- **Files with auto-detected boundaries:** {len(prose_removed) - custom_count:,}\n\n")

        # Errors
        if errors:
            f.write("## Errors\n\n")
            for error in errors[:50]:  # First 50 errors
                f.write(f"- {error}\n")
            if len(errors) > 50:
                f.write(f"\n... and {len(errors) - 50} more errors\n")
            f.write("\n")

        # Sample deletions
        if files_deleted:
            f.write("## Sample Deleted Files (First 50)\n\n")
            for filename in files_deleted[:50]:
                f.write(f"- {filename}\n")
            if len(files_deleted) > 50:
                f.write(f"\n... and {len(files_deleted) - 50} more files\n")
            f.write("\n")

        # Sample prose removals
        if prose_removed:
            f.write("## Sample Prose Removals (First 50)\n\n")
            for item in prose_removed[:50]:
                boundary_type = "custom" if item['custom'] else "auto"
                f.write(f"- **{item['filename']}**\n")
                f.write(f"  - Prose started at line: {item['prose_start'] + 1}\n")
                f.write(f"  - Lines removed: {item['lines_removed']}\n")
                f.write(f"  - Boundary: {boundary_type}\n\n")
            if len(prose_removed) > 50:
                f.write(f"... and {len(prose_removed) - 50} more files\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Final summary
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"✓ Files deleted: {len(files_deleted):,}")
    print(f"✓ Files with prose removed: {len(prose_removed):,}")
    if prose_removed:
        print(f"✓ Total prose lines removed: {sum(p['lines_removed'] for p in prose_removed):,}")
    print(f"✓ Files kept unchanged: {decision_counts['keep']:,}")
    if errors:
        print(f"✗ Errors: {len(errors)}")

    # Final corpus size
    final_size = len(rows) - len(files_deleted)
    print(f"\nFinal corpus size: {final_size:,} poems")

if __name__ == '__main__':
    main()
