#!/usr/bin/env python3
"""
Classify poems in a specific range.
Usage: python3 classify_range.py <start_idx> <end_idx> <session_id>
Example: python3 classify_range.py 0 20000 session1
"""

import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 classify_range.py <start_idx> <end_idx> <session_id>")
        sys.exit(1)

    start_idx = int(sys.argv[1])
    end_idx = int(sys.argv[2])
    session_id = sys.argv[3]

    texts_dir = Path.home() / "poetry-bert-formalism" / "data" / "corpus" / "texts"
    output_dir = Path.home() / "poetry-bert-formalism" / "data" / "classifications"
    output_dir.mkdir(exist_ok=True)

    # Get all poem files
    all_files = sorted(list(texts_dir.rglob("*.txt")))

    # Get assigned range
    range_files = all_files[start_idx:end_idx]

    print(f"="*80)
    print(f"SESSION: {session_id}")
    print(f"="*80)
    print(f"Total poems in corpus: {len(all_files):,}")
    print(f"Assigned range: {start_idx:,} to {end_idx:,}")
    print(f"Poems to classify: {len(range_files):,}")

    # Check for existing progress
    progress_file = output_dir / f"{session_id}_progress.txt"
    completed = 0
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            completed = int(f.read().strip())
        print(f"Progress: {completed:,} / {len(range_files):,} completed")

    if completed >= len(range_files):
        print("\n✓ This session is complete!")
        sys.exit(0)

    # Load next batch (100 poems at a time)
    batch_size = 100
    batch_start = completed
    batch_end = min(completed + batch_size, len(range_files))
    batch_files = range_files[batch_start:batch_end]

    print(f"\n{'='*80}")
    print(f"LOADING BATCH: {batch_start} to {batch_end}")
    print(f"{'='*80}\n")

    batch = []
    for poem_file in batch_files:
        try:
            with open(poem_file, 'r', encoding='utf-8') as f:
                text = f.read().strip()

            filename = poem_file.name
            parts = filename.replace('.txt', '').split('_', 1)
            poem_id = parts[0] if parts else "unknown"

            batch.append({
                'poem_id': poem_id,
                'filename': str(poem_file.relative_to(texts_dir)),
                'text': text,
                'global_index': start_idx + batch_start + len(batch) - 1
            })
        except Exception as e:
            print(f"Error reading {poem_file}: {e}")

    # Save batch info
    batch_file = output_dir / f"{session_id}_batch_{batch_start:06d}.json"
    with open(batch_file, 'w') as f:
        json.dump(batch, f, indent=2)

    print(f"Batch saved to: {batch_file}")
    print(f"\nReady for Claude to classify {len(batch)} poems!")
    print(f"\nAfter classification:")
    print(f"1. Save results to: {output_dir}/{session_id}_batch_{batch_start:06d}_classified.json")
    print(f"2. Update progress: echo '{batch_end}' > {progress_file}")
    print(f"3. Run script again to continue")

if __name__ == "__main__":
    main()
