#!/usr/bin/env python3
"""
Close gap in sequential IDs after removing poem 1591.
Renumber poems 1592-116675 → 1591-116674
"""

import csv
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_final_metadata_no_gaps.csv"

def close_gap(dry_run=True):
    """Renumber to close gap."""
    print("Loading CSV...")
    rows = []
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"✓ Loaded {len(rows)} rows\n")

    renamed_count = 0

    for row in rows:
        old_id = int(row['poem_id'])

        # If poem_id > 1591, reduce by 1
        if old_id > 1591:
            new_id = old_id - 1

            # Update poem_id in CSV
            row['poem_id'] = str(new_id)

            # Update filename on disk and in CSV
            filepath = row['filepath']
            full_path = CORPUS_DIR / filepath
            author_dir = full_path.parent
            old_filename = full_path.name

            # Build new filename with new ID
            rest_of_filename = '_'.join(old_filename.split('_')[1:])
            new_filename = f"{new_id:06d}_{rest_of_filename}"
            new_path = author_dir / new_filename

            if renamed_count < 10:  # Show first 10
                print(f"Poem {old_id} → {new_id}:")
                print(f"  {old_filename}")
                print(f"  → {new_filename}")

            if not dry_run:
                try:
                    full_path.rename(new_path)
                    row['filepath'] = str(new_path.relative_to(CORPUS_DIR))
                except Exception as e:
                    print(f"  Error: {e}")
            else:
                row['filepath'] = str(new_path.relative_to(CORPUS_DIR))

            renamed_count += 1

    print(f"\n✓ {'Would renumber' if dry_run else 'Renumbered'} {renamed_count} poems")

    # Write CSV
    print(f"\nWriting CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Wrote {len(rows)} rows (IDs now 1-{len(rows)})")

def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 70)
    if dry_run:
        print("CLOSE ID GAP (DRY RUN)")
        print("Add --execute to renumber")
    else:
        print("CLOSE ID GAP")
        print("⚠️  EXECUTING RENUMBERING ⚠️")
    print("=" * 70)
    print()

    close_gap(dry_run=dry_run)

    if dry_run:
        print("\nThis was a DRY RUN. Review and run with --execute.")
    else:
        print("\n✓ Complete!")
        print("\nNext steps:")
        print("1. mv data/metadata/corpus_final_metadata.csv data/metadata/corpus_final_metadata_with_gap.csv")
        print("2. mv data/metadata/corpus_final_metadata_no_gaps.csv data/metadata/corpus_final_metadata.csv")
        print("3. python3 scripts/validate_corpus.py")

if __name__ == '__main__':
    main()
