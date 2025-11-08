#!/usr/bin/env python3
"""
Final cleanup:
1. Delete extra duplicate files on disk
2. Remove poem 1591 (empty file) from CSV
"""

import csv
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_final_metadata_clean.csv"

def find_extra_files():
    """Find files on disk not in CSV."""
    # Load CSV filepaths
    print("Loading CSV...")
    csv_files = set()
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_files.add(row['filepath'])

    # Scan disk
    print(f"Scanning disk...")
    disk_files = {}
    for author_dir in CORPUS_DIR.iterdir():
        if author_dir.is_dir():
            for filepath in author_dir.glob('*.txt'):
                rel_path = str(filepath.relative_to(CORPUS_DIR))
                disk_files[rel_path] = filepath

    # Find extras
    extras = set(disk_files.keys()) - csv_files
    return [disk_files[f] for f in extras]

def delete_extra_files(extras, dry_run=True):
    """Delete extra files."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting {len(extras)} extra files...")

    for i, filepath in enumerate(sorted(extras), 1):
        if i <= 10:  # Show first 10
            print(f"  {filepath.relative_to(CORPUS_DIR)}")

        if not dry_run:
            try:
                filepath.unlink()
            except Exception as e:
                print(f"  Error deleting {filepath}: {e}")

    print(f"✓ {'Would delete' if dry_run else 'Deleted'} {len(extras)} files")

def remove_empty_poem(dry_run=True):
    """Remove poem 1591 (empty file) from CSV."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Removing poem 1591 from CSV...")

    rows = []
    removed = False

    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            if row['poem_id'] == '1591':
                print(f"  Removing: Poem 1591 (empty file)")
                removed = True
            else:
                rows.append(row)

    print(f"✓ CSV now has {len(rows)} rows (removed 1)")

    # Write updated CSV
    print(f"\nWriting cleaned CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Wrote {len(rows)} rows")

def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 70)
    if dry_run:
        print("FINAL CLEANUP (DRY RUN)")
        print("Add --execute to perform cleanup")
    else:
        print("FINAL CLEANUP")
        print("⚠️  EXECUTING DELETIONS ⚠️")
    print("=" * 70)
    print()

    # Find and delete extra files
    extras = find_extra_files()
    delete_extra_files(extras, dry_run=dry_run)

    # Remove empty poem from CSV
    remove_empty_poem(dry_run=dry_run)

    if dry_run:
        print("\nThis was a DRY RUN. Review and run with --execute.")
    else:
        print("\n✓ Cleanup complete!")
        print("\nNext steps:")
        print("1. mv data/metadata/corpus_final_metadata.csv data/metadata/corpus_final_metadata_with_empty.csv")
        print("2. mv data/metadata/corpus_final_metadata_clean.csv data/metadata/corpus_final_metadata.csv")
        print("3. python3 scripts/validate_corpus.py")

if __name__ == '__main__':
    main()
