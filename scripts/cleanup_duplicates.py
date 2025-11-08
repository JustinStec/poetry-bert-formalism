#!/usr/bin/env python3
"""
Phase 1.1: Remove duplicate files and merge author name variants.

This script:
1. Identifies and removes 1,860 duplicate files (same content_hash)
2. Merges author name variants into canonical forms
3. Deletes empty files
4. Logs all deletions for review

Result: 116,675 unique poem files
"""

import csv
import hashlib
from pathlib import Path
from collections import defaultdict
import shutil
import json
from datetime import datetime

# Configuration
BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
LOG_DIR = BASE_DIR / "data/metadata/cleanup_logs"

# Author name normalization map
AUTHOR_VARIANTS = {
    # Format: "incorrect_name" -> "correct_name"
    "OReilly, John Boyle": "Reilly, John Boyle O",
    "Maeterlin, Maurice": "Maeterlinck, Maurice",
    "Shirazi, Hafez": "Hafiz, Shams al-Din",
    "Fletcher, Phineas": "Sr, Giles Fletcher",
    # Add more as discovered
}


def calculate_file_hash(filepath):
    """Calculate MD5 hash of file content."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None


def load_csv_hashes():
    """Load content hashes from CSV to identify which files to keep."""
    csv_hashes = {}  # hash -> poem_id
    csv_poems = {}   # poem_id -> metadata

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_hashes[row['content_hash']] = row['poem_id']
            csv_poems[row['poem_id']] = row

    return csv_hashes, csv_poems


def scan_corpus_files():
    """Scan all files in corpus and group by content hash."""
    hash_to_files = defaultdict(list)
    empty_files = []

    print("Scanning corpus files...")
    file_count = 0

    for author_dir in sorted(CORPUS_DIR.iterdir()):
        if not author_dir.is_dir():
            continue

        for filepath in author_dir.glob('*.txt'):
            file_count += 1
            if file_count % 10000 == 0:
                print(f"  Scanned {file_count} files...")

            # Check if empty
            if filepath.stat().st_size == 0:
                empty_files.append(filepath)
                continue

            # Calculate hash
            file_hash = calculate_file_hash(filepath)
            if file_hash:
                hash_to_files[file_hash].append(filepath)

    print(f"✓ Scanned {file_count} total files")
    print(f"  Found {len(empty_files)} empty files")
    print(f"  Found {len(hash_to_files)} unique content hashes")

    return hash_to_files, empty_files


def identify_duplicates(hash_to_files, csv_hashes):
    """Identify which files are duplicates (not in CSV)."""
    files_to_keep = []
    files_to_delete = []

    for file_hash, file_list in hash_to_files.items():
        if len(file_list) == 1:
            # Unique file
            if file_hash in csv_hashes:
                files_to_keep.append(file_list[0])
            else:
                # Not in CSV but unique - should investigate
                print(f"Warning: Unique file not in CSV: {file_list[0]}")
                files_to_delete.append(file_list[0])
        else:
            # Multiple files with same hash
            if file_hash in csv_hashes:
                # One file should be in CSV, rest are duplicates
                kept = False
                for filepath in file_list:
                    if not kept:
                        files_to_keep.append(filepath)
                        kept = True
                    else:
                        files_to_delete.append(filepath)
            else:
                # All are duplicates not in CSV
                for filepath in file_list:
                    files_to_delete.append(filepath)

    return files_to_keep, files_to_delete


def merge_author_directories(dry_run=True):
    """Merge author name variant directories."""
    merges_performed = []

    for variant_name, canonical_name in AUTHOR_VARIANTS.items():
        variant_dir = CORPUS_DIR / variant_name
        canonical_dir = CORPUS_DIR / canonical_name

        if not variant_dir.exists():
            print(f"  Variant directory not found: {variant_name}")
            continue

        if not canonical_dir.exists():
            print(f"  Creating canonical directory: {canonical_name}")
            if not dry_run:
                canonical_dir.mkdir(parents=True, exist_ok=True)

        # Move all files from variant to canonical
        file_count = 0
        for filepath in variant_dir.glob('*.txt'):
            target = canonical_dir / filepath.name

            if target.exists():
                # File with same name exists, check if duplicate
                source_hash = calculate_file_hash(filepath)
                target_hash = calculate_file_hash(target)

                if source_hash == target_hash:
                    # Duplicate, delete source
                    if dry_run:
                        print(f"    [DRY RUN] Would delete duplicate: {filepath.name}")
                    else:
                        filepath.unlink()
                else:
                    # Different content, rename to avoid collision
                    new_name = f"{filepath.stem}_variant{filepath.suffix}"
                    target = canonical_dir / new_name
                    if dry_run:
                        print(f"    [DRY RUN] Would rename {filepath.name} → {new_name}")
                    else:
                        shutil.move(str(filepath), str(target))
            else:
                # Move file
                if dry_run:
                    print(f"    [DRY RUN] Would move: {filepath.name}")
                else:
                    shutil.move(str(filepath), str(target))

            file_count += 1

        merges_performed.append({
            'variant': variant_name,
            'canonical': canonical_name,
            'files_moved': file_count
        })

        # Remove empty variant directory
        if not dry_run and variant_dir.exists():
            try:
                variant_dir.rmdir()
                print(f"  ✓ Removed empty directory: {variant_name}")
            except OSError:
                print(f"  ! Directory not empty, skipping: {variant_name}")

    return merges_performed


def delete_files(files_to_delete, empty_files, dry_run=True):
    """Delete duplicate and empty files."""
    deletion_log = {
        'timestamp': datetime.now().isoformat(),
        'duplicates_deleted': [],
        'empty_deleted': [],
        'total_deleted': 0
    }

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting duplicate files...")
    for filepath in files_to_delete:
        if dry_run:
            print(f"  [DRY RUN] Would delete: {filepath}")
        else:
            try:
                filepath.unlink()
                deletion_log['duplicates_deleted'].append(str(filepath))
            except Exception as e:
                print(f"  Error deleting {filepath}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting empty files...")
    for filepath in empty_files:
        if dry_run:
            print(f"  [DRY RUN] Would delete: {filepath}")
        else:
            try:
                filepath.unlink()
                deletion_log['empty_deleted'].append(str(filepath))
            except Exception as e:
                print(f"  Error deleting {filepath}: {e}")

    deletion_log['total_deleted'] = (
        len(deletion_log['duplicates_deleted']) +
        len(deletion_log['empty_deleted'])
    )

    return deletion_log


def save_log(deletion_log, merge_log, dry_run=True):
    """Save cleanup logs."""
    if dry_run:
        print("\n[DRY RUN] Would save logs to:", LOG_DIR)
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Save deletion log
    deletion_log_path = LOG_DIR / f"deletions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(deletion_log_path, 'w') as f:
        json.dump(deletion_log, f, indent=2)
    print(f"\n✓ Saved deletion log: {deletion_log_path}")

    # Save merge log
    merge_log_path = LOG_DIR / f"merges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(merge_log_path, 'w') as f:
        json.dump(merge_log, f, indent=2)
    print(f"✓ Saved merge log: {merge_log_path}")


def main():
    import sys
    dry_run = '--execute' not in sys.argv

    print("=" * 80)
    if dry_run:
        print("PHASE 1.1: CLEANUP DUPLICATES (DRY RUN)")
        print("Add --execute to actually delete files")
    else:
        print("PHASE 1.1: CLEANUP DUPLICATES")
        print("\n⚠️  EXECUTING ACTUAL DELETIONS ⚠️")
    print("=" * 80)
    print()

    # Step 1: Load CSV hashes
    print("Step 1: Loading CSV metadata...")
    csv_hashes, csv_poems = load_csv_hashes()
    print(f"✓ Loaded {len(csv_hashes)} unique hashes from CSV")
    print(f"✓ Loaded {len(csv_poems)} poem records")

    # Step 2: Scan corpus files
    print("\nStep 2: Scanning corpus files...")
    hash_to_files, empty_files = scan_corpus_files()

    # Step 3: Identify duplicates
    print("\nStep 3: Identifying duplicates...")
    files_to_keep, files_to_delete = identify_duplicates(hash_to_files, csv_hashes)
    print(f"✓ Files to keep: {len(files_to_keep)}")
    print(f"✓ Duplicate files to delete: {len(files_to_delete)}")
    print(f"✓ Empty files to delete: {len(empty_files)}")
    print(f"✓ Total files to delete: {len(files_to_delete) + len(empty_files)}")

    # Step 4: Merge author directories
    print("\nStep 4: Merging author name variants...")
    merge_log = merge_author_directories(dry_run=dry_run)
    for merge in merge_log:
        print(f"  {merge['variant']} → {merge['canonical']}: {merge['files_moved']} files")

    # Step 5: Delete files
    print("\nStep 5: Deleting duplicate and empty files...")
    deletion_log = delete_files(files_to_delete, empty_files, dry_run=dry_run)

    # Step 6: Save logs
    print("\nStep 6: Saving cleanup logs...")
    save_log(deletion_log, merge_log, dry_run=dry_run)

    # Summary
    print("\n" + "=" * 80)
    print("CLEANUP SUMMARY")
    print("=" * 80)
    action = "Would delete" if dry_run else "Deleted"
    print(f"\n{action}:")
    print(f"  Duplicate files: {len(files_to_delete)}")
    print(f"  Empty files: {len(empty_files)}")
    print(f"  Total: {len(files_to_delete) + len(empty_files)}")
    print(f"\nAuthor merges: {len(merge_log)}")
    print(f"\nExpected remaining files: {len(files_to_keep)}")

    if dry_run:
        print("\n" + "-" * 80)
        print("This was a DRY RUN. Review output carefully.")
        print("When ready, run with --execute to perform cleanup.")
    else:
        print("\n✓ Cleanup complete!")
        print("\nNext step: Run scripts/renumber_corpus.py")


if __name__ == '__main__':
    main()
