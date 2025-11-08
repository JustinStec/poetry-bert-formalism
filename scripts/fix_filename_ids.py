#!/usr/bin/env python3
"""
Fix filenames to match their poem_id in CSV.
For each poem, rename file to start with 6-digit poem_id.
"""

import csv
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_final_metadata_fixed_ids.csv"

def fix_filenames(dry_run=True):
    """Rename files to match their poem_id."""

    print("Loading CSV...")
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"✓ Loaded {len(rows)} rows\n")

    renamed_count = 0
    errors = []

    for row in rows:
        poem_id = int(row['poem_id'])
        filepath = row['filepath']

        # Get current filename and directory
        full_path = CORPUS_DIR / filepath
        author_dir = full_path.parent
        old_filename = full_path.name

        # Extract the current ID prefix
        current_id = old_filename.split('_')[0]

        # Check if it needs fixing
        expected_id = f"{poem_id:06d}"

        if current_id != expected_id:
            # Build new filename with correct 6-digit ID
            # Keep everything after the first underscore
            rest_of_filename = '_'.join(old_filename.split('_')[1:])
            new_filename = f"{expected_id}_{rest_of_filename}"
            new_path = author_dir / new_filename

            if renamed_count < 10:  # Show first 10
                print(f"Poem {poem_id}:")
                print(f"  {old_filename}")
                print(f"  → {new_filename}")

            if not dry_run:
                try:
                    full_path.rename(new_path)
                    # Update CSV row
                    row['filepath'] = str(new_path.relative_to(CORPUS_DIR))
                except Exception as e:
                    errors.append(f"Error renaming poem {poem_id}: {e}")
            else:
                # Update CSV row for dry run preview
                row['filepath'] = str(new_path.relative_to(CORPUS_DIR))

            renamed_count += 1

    print(f"\n✓ {'Would rename' if dry_run else 'Renamed'} {renamed_count} files")

    if errors:
        print(f"⚠ {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  {err}")

    # Write updated CSV
    print(f"\nWriting updated CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Wrote {len(rows)} rows")

    return renamed_count

def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 70)
    if dry_run:
        print("FIX FILENAME IDs (DRY RUN)")
        print("Add --execute to actually rename files")
    else:
        print("FIX FILENAME IDs")
        print("⚠️  EXECUTING ACTUAL FILE RENAMING ⚠️")
    print("=" * 70)
    print()

    count = fix_filenames(dry_run=dry_run)

    if dry_run:
        print("\nThis was a DRY RUN. Review output and run with --execute.")
    else:
        print("\n✓ Complete! Files renamed and CSV updated.")
        print("\nNext steps:")
        print("1. mv data/metadata/corpus_final_metadata.csv data/metadata/corpus_final_metadata_old_ids.csv")
        print("2. mv data/metadata/corpus_final_metadata_fixed_ids.csv data/metadata/corpus_final_metadata.csv")
        print("3. python3 scripts/validate_corpus.py")

if __name__ == '__main__':
    main()
