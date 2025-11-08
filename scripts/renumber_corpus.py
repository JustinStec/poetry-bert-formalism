#!/usr/bin/env python3
"""
Phase 1.2: Sequential renumbering of corpus (1 → 116,675).

This script:
1. Reads the cleaned CSV (after duplicate removal)
2. Assigns new sequential poem_ids (1 → 116,675)
3. Renames all files with new IDs in 6-digit format
4. Updates CSV with new poem_ids and filenames
5. Preserves all other metadata (content_hash, etc.)

Result: Sequentially numbered corpus with no gaps
"""

import csv
import shutil
from pathlib import Path
import json
from datetime import datetime
from collections import OrderedDict

# Configuration
BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
NEW_CSV_PATH = BASE_DIR / "data/metadata/corpus_renumbered.csv"
LOG_DIR = BASE_DIR / "data/metadata/renumbering_logs"


def sanitize_filename_part(text, max_length=50):
    """Sanitize text for use in filename."""
    # Remove/replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '',
        '<': '',
        '>': '',
        '|': '_',
        '\n': '_',
        '\r': '_',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Trim excessive whitespace
    text = ' '.join(text.split())

    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rstrip()

    return text


def generate_new_filename(poem_id, title, author, date):
    """
    Generate new filename in format:
    {poem_id:06d}_{title}_{author}_{date}.txt

    Example: 000042_Daddy_Plath_Sylvia_1962.txt
    """
    # Format poem_id as 6-digit number
    id_str = f"{poem_id:06d}"

    # Sanitize components
    title_clean = sanitize_filename_part(title, max_length=60)
    author_clean = sanitize_filename_part(author, max_length=40)
    date_clean = sanitize_filename_part(date, max_length=10)

    # Build filename
    filename = f"{id_str}_{title_clean}_{author_clean}_{date_clean}.txt"

    return filename


def load_and_renumber_csv():
    """
    Load CSV, assign sequential IDs, generate new filenames.
    Returns: list of renumbered poems with old and new metadata
    """
    print("Loading CSV and assigning new sequential IDs...")

    poems = []

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            poems.append(row)

    print(f"✓ Loaded {len(poems)} poems from CSV")

    # Sort poems (by author, then title for consistent ordering)
    print("Sorting poems by author and title...")
    poems_sorted = sorted(poems, key=lambda x: (x['author'], x['title']))

    # Assign new sequential IDs
    print("Assigning new sequential poem IDs (1 → {})...".format(len(poems_sorted)))
    renumbered = []

    for new_id, poem in enumerate(poems_sorted, start=1):
        # Generate new filename
        new_filename = generate_new_filename(
            new_id,
            poem['title'],
            poem['author'],
            poem['date']
        )

        # Build new row
        new_poem = OrderedDict()
        new_poem['old_poem_id'] = poem['poem_id']
        new_poem['new_poem_id'] = new_id
        new_poem['title'] = poem['title']
        new_poem['author'] = poem['author']
        new_poem['date'] = poem['date']
        new_poem['source'] = poem['source']
        new_poem['old_filepath'] = poem['filepath']
        new_poem['new_filename'] = new_filename
        new_poem['lines'] = poem['lines']
        new_poem['words'] = poem['words']
        new_poem['file_size'] = poem['file_size']
        new_poem['content_hash'] = poem['content_hash']

        renumbered.append(new_poem)

        if new_id % 10000 == 0:
            print(f"  Processed {new_id} poems...")

    print(f"✓ Assigned sequential IDs to {len(renumbered)} poems")

    return renumbered


def rename_files(renumbered_poems, dry_run=True):
    """Rename all files according to new numbering scheme."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Renaming files...")

    rename_log = {
        'timestamp': datetime.now().isoformat(),
        'renames': [],
        'errors': [],
        'total_renamed': 0
    }

    renamed_count = 0
    error_count = 0

    for poem in renumbered_poems:
        old_path = CORPUS_DIR / poem['old_filepath']
        author_dir = old_path.parent
        new_path = author_dir / poem['new_filename']

        if not old_path.exists():
            error_msg = f"Source file not found: {old_path}"
            print(f"  ERROR: {error_msg}")
            rename_log['errors'].append(error_msg)
            error_count += 1
            continue

        if dry_run:
            if renamed_count < 20:  # Show first 20 examples
                print(f"  [DRY RUN] Would rename:")
                print(f"    {old_path.name}")
                print(f"    → {new_path.name}")
        else:
            try:
                shutil.move(str(old_path), str(new_path))
                rename_log['renames'].append({
                    'old_poem_id': poem['old_poem_id'],
                    'new_poem_id': poem['new_poem_id'],
                    'old_path': str(old_path),
                    'new_path': str(new_path)
                })
                renamed_count += 1

                if renamed_count % 10000 == 0:
                    print(f"  Renamed {renamed_count} files...")

            except Exception as e:
                error_msg = f"Error renaming {old_path}: {e}"
                print(f"  ERROR: {error_msg}")
                rename_log['errors'].append(error_msg)
                error_count += 1

    rename_log['total_renamed'] = renamed_count

    print(f"\n✓ {'Would rename' if dry_run else 'Renamed'} {len(renumbered_poems)} files")
    if error_count > 0:
        print(f"  ! {error_count} errors encountered")

    return rename_log


def write_new_csv(renumbered_poems, dry_run=True):
    """Write new CSV with updated poem_ids and filenames."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Writing new CSV...")

    if dry_run:
        print(f"  [DRY RUN] Would write to: {NEW_CSV_PATH}")
        print(f"  [DRY RUN] Preview of first 5 entries:")
        for i, poem in enumerate(renumbered_poems[:5], 1):
            print(f"    {i}. ID: {poem['new_poem_id']:06d} | {poem['title']} by {poem['author']}")
        return

    # Write new CSV
    fieldnames = [
        'poem_id',      # New sequential ID
        'title',
        'author',
        'date',
        'source',
        'filepath',     # New filepath with author/filename
        'lines',
        'words',
        'file_size',
        'content_hash'
    ]

    with open(NEW_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for poem in renumbered_poems:
            # Build row for new CSV
            author_dir = Path(poem['old_filepath']).parent.name
            new_filepath = f"{author_dir}/{poem['new_filename']}"

            row = {
                'poem_id': poem['new_poem_id'],
                'title': poem['title'],
                'author': poem['author'],
                'date': poem['date'],
                'source': poem['source'],
                'filepath': new_filepath,
                'lines': poem['lines'],
                'words': poem['words'],
                'file_size': poem['file_size'],
                'content_hash': poem['content_hash']
            }

            writer.writerow(row)

    print(f"✓ Wrote new CSV: {NEW_CSV_PATH}")
    print(f"  Total entries: {len(renumbered_poems)}")


def save_renumbering_log(renumbered_poems, rename_log, dry_run=True):
    """Save renumbering logs."""
    if dry_run:
        print(f"\n[DRY RUN] Would save logs to: {LOG_DIR}")
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Save ID mapping (old_id → new_id)
    id_mapping = {
        poem['old_poem_id']: poem['new_poem_id']
        for poem in renumbered_poems
    }

    mapping_path = LOG_DIR / f"id_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(mapping_path, 'w') as f:
        json.dump(id_mapping, f, indent=2)
    print(f"\n✓ Saved ID mapping: {mapping_path}")

    # Save rename log
    rename_log_path = LOG_DIR / f"renames_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(rename_log_path, 'w') as f:
        json.dump(rename_log, f, indent=2)
    print(f"✓ Saved rename log: {rename_log_path}")


def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 80)
    if dry_run:
        print("PHASE 1.2: SEQUENTIAL RENUMBERING (DRY RUN)")
        print("Add --execute to actually rename files")
    else:
        print("PHASE 1.2: SEQUENTIAL RENUMBERING")
        print("\n⚠️  EXECUTING ACTUAL FILE RENAMING ⚠️")
    print("=" * 80)
    print()

    # Step 1: Load CSV and assign new sequential IDs
    print("Step 1: Loading CSV and assigning sequential IDs...")
    renumbered_poems = load_and_renumber_csv()

    # Step 2: Rename files
    print("\nStep 2: Renaming files on disk...")
    rename_log = rename_files(renumbered_poems, dry_run=dry_run)

    # Step 3: Write new CSV
    print("\nStep 3: Writing new CSV with updated IDs...")
    write_new_csv(renumbered_poems, dry_run=dry_run)

    # Step 4: Save logs
    print("\nStep 4: Saving renumbering logs...")
    save_renumbering_log(renumbered_poems, rename_log, dry_run=dry_run)

    # Summary
    print("\n" + "=" * 80)
    print("RENUMBERING SUMMARY")
    print("=" * 80)
    print(f"\nPoems processed: {len(renumbered_poems)}")
    print(f"New ID range: 1 → {len(renumbered_poems)}")
    print(f"\nFilename format: NNNNNN_Title_Author_Date.txt")
    print(f"Example: {renumbered_poems[0]['new_filename']}")

    if dry_run:
        print("\n" + "-" * 80)
        print("This was a DRY RUN. Review output carefully.")
        print("When ready, run with --execute to perform renumbering.")
        print("\nIMPORTANT: Run cleanup_duplicates.py first if not already done!")
    else:
        print("\n✓ Renumbering complete!")
        print(f"\nNew CSV created: {NEW_CSV_PATH}")
        print("\nNext steps:")
        print("1. Verify new CSV and files")
        print("2. Run scripts/validate_corpus.py")
        print("3. Replace old CSV with new CSV if validation passes")


if __name__ == '__main__':
    main()
