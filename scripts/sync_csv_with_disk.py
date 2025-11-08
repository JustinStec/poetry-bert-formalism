#!/usr/bin/env python3
"""
Sync CSV with actual files on disk.
Scans all files, matches by content hash, updates CSV with actual paths.
"""

import csv
import hashlib
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_synced.csv"

def calculate_file_hash(filepath):
    """Calculate MD5 hash of file content."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def scan_all_files():
    """Scan all files on disk and build hash -> filepath mapping."""
    print("Scanning all files on disk...")
    hash_to_path = {}
    file_count = 0

    for author_dir in sorted(CORPUS_DIR.iterdir()):
        if not author_dir.is_dir():
            continue

        for filepath in author_dir.glob('*.txt'):
            file_count += 1
            if file_count % 10000 == 0:
                print(f"  Scanned {file_count} files...")

            file_hash = calculate_file_hash(filepath)
            if file_hash:
                # Store relative path from corpus dir
                rel_path = filepath.relative_to(CORPUS_DIR)
                hash_to_path[file_hash] = str(rel_path)

    print(f"✓ Scanned {file_count} files on disk")
    return hash_to_path

def sync_csv(hash_to_path):
    """Update CSV filepaths to match actual files on disk."""
    print("\nLoading CSV...")

    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows)} CSV entries")

    # Update filepaths
    print("\nMatching CSV entries to actual files...")
    matched = 0
    mismatched = 0
    not_found = 0

    for row in rows:
        content_hash = row['content_hash']
        old_filepath = row['filepath']

        if content_hash in hash_to_path:
            actual_filepath = hash_to_path[content_hash]

            if actual_filepath != old_filepath:
                if mismatched < 10:  # Show first 10
                    print(f"  Updating: {old_filepath}")
                    print(f"         → {actual_filepath}")
                mismatched += 1
                row['filepath'] = actual_filepath
            else:
                matched += 1
        else:
            not_found += 1
            if not_found <= 5:
                print(f"  WARNING: No file found for hash {content_hash} (poem {row['poem_id']})")

    print(f"\n✓ Matched: {matched}")
    print(f"✓ Updated: {mismatched}")
    if not_found > 0:
        print(f"⚠ Not found on disk: {not_found}")

    # Write synced CSV
    print(f"\nWriting synced CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Wrote {len(rows)} rows")
    print("\nNext steps:")
    print("1. Review output above")
    print("2. mv data/metadata/corpus_final_metadata.csv data/metadata/corpus_final_metadata_pre_sync.csv")
    print("3. mv data/metadata/corpus_synced.csv data/metadata/corpus_final_metadata.csv")
    print("4. python3 scripts/validate_corpus.py")

if __name__ == '__main__':
    hash_to_path = scan_all_files()
    sync_csv(hash_to_path)
