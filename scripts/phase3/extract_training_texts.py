#!/usr/bin/env python3
"""
Extract full poem texts for the 457 training poems from the M4 Max corpus.
Match by title and author, then read the text files.
"""

import pandas as pd
import csv
from pathlib import Path
import re
import subprocess

# Paths
BASE_DIR = Path("/Users/justin/Repos/AI Project")
M4_MAX_USER = "justin@100.65.21.63"
M4_MAX_CORPUS_DIR = "~/poetry-bert-formalism/Data/processed/poetry_platform_renamed"
M4_MAX_METADATA = "~/poetry-bert-formalism/Data/metadata/corpus_final_metadata.csv"

TRAINING_FILE = BASE_DIR / "Data/phase3/training_set_456_poems.csv"
OUTPUT_FILE = BASE_DIR / "Data/phase3/training_texts_collected.csv"
MISSING_LOG = BASE_DIR / "Data/phase3/missing_texts.csv"

def normalize_name(name):
    """Normalize names for matching (remove extra spaces, standardize)."""
    if pd.isna(name):
        return ""
    # Remove extra whitespace
    name = " ".join(name.split())
    return name.strip()

def normalize_title(title):
    """Normalize titles for matching."""
    if pd.isna(title):
        return ""
    # Remove extra whitespace
    title = " ".join(title.split())
    # Remove common variations
    title = title.strip()
    return title

def main():
    print("="*80)
    print("PHASE 3B: EXTRACT TRAINING POEM TEXTS")
    print("="*80)

    # Load training dataset
    print("\n1. Loading training dataset...")
    training_df = pd.read_csv(TRAINING_FILE)
    print(f"   ✓ Loaded {len(training_df)} training poems")

    # Download corpus metadata from M4 Max
    print("\n2. Downloading corpus metadata from M4 Max...")
    local_metadata = BASE_DIR / "Data/phase3/corpus_metadata_temp.csv"

    cmd = f'scp {M4_MAX_USER}:{M4_MAX_METADATA} "{local_metadata}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"   ✗ Failed to download metadata: {result.stderr}")
        return

    print(f"   ✓ Downloaded corpus metadata")

    # Load corpus metadata
    print("\n3. Loading corpus metadata...")
    corpus_df = pd.read_csv(local_metadata)
    print(f"   ✓ Loaded {len(corpus_df)} corpus poems")

    # Create lookup dictionaries
    print("\n4. Creating lookup tables...")

    # Normalize corpus metadata for matching
    corpus_df['title_norm'] = corpus_df['title'].apply(normalize_title)
    corpus_df['author_norm'] = corpus_df['author'].apply(normalize_name)

    # Create lookup by (title, author)
    corpus_lookup = {}
    for _, row in corpus_df.iterrows():
        key = (row['title_norm'].lower(), row['author_norm'].lower())
        if key not in corpus_lookup:
            corpus_lookup[key] = []
        corpus_lookup[key].append({
            'poem_id': row['poem_id'],
            'filepath': row['filepath'],
            'filename': row['filename']
        })

    print(f"   ✓ Created lookup table with {len(corpus_lookup)} unique (title, author) pairs")

    # Match training poems to corpus
    print("\n5. Matching training poems to corpus...")

    matches = []
    missing = []

    for idx, row in training_df.iterrows():
        title_norm = normalize_title(row['title'])
        author_norm = normalize_name(row['author'])

        key = (title_norm.lower(), author_norm.lower())

        if key in corpus_lookup:
            corpus_entries = corpus_lookup[key]
            if len(corpus_entries) == 1:
                match = corpus_entries[0]
                matches.append({
                    'training_idx': idx,
                    'title': row['title'],
                    'author': row['author'],
                    'year_approx': row['year_approx'],
                    'period': row['period'],
                    'corpus_poem_id': match['poem_id'],
                    'filepath': match['filepath'],
                    'filename': match['filename'],
                    'match_type': 'exact'
                })
            else:
                # Multiple matches - take first one, log warning
                match = corpus_entries[0]
                matches.append({
                    'training_idx': idx,
                    'title': row['title'],
                    'author': row['author'],
                    'year_approx': row['year_approx'],
                    'period': row['period'],
                    'corpus_poem_id': match['poem_id'],
                    'filepath': match['filepath'],
                    'filename': match['filename'],
                    'match_type': f'multiple ({len(corpus_entries)})'
                })
                print(f"   ⚠ Multiple matches for '{title_norm}' by {author_norm}: {len(corpus_entries)}")
        else:
            missing.append({
                'training_idx': idx,
                'title': row['title'],
                'author': row['author'],
                'year_approx': row['year_approx'],
                'period': row['period']
            })

    print(f"\n   ✓ Matched: {len(matches)} poems")
    print(f"   ✗ Missing: {len(missing)} poems")

    if missing:
        print("\n6. Saving missing poems log...")
        missing_df = pd.DataFrame(missing)
        missing_df.to_csv(MISSING_LOG, index=False)
        print(f"   ✓ Saved to {MISSING_LOG}")

        print("\n   Missing poems:")
        for m in missing[:10]:
            print(f"     - '{m['title']}' by {m['author']} ({m['year_approx']})")
        if len(missing) > 10:
            print(f"     ... and {len(missing) - 10} more")

    if not matches:
        print("\n✗ No matches found. Cannot proceed.")
        return

    # Download matched texts from M4 Max
    print(f"\n7. Downloading {len(matches)} poem texts from M4 Max...")

    texts_collected = []
    download_failures = []

    for i, match in enumerate(matches):
        if (i + 1) % 50 == 0:
            print(f"   Progress: {i+1}/{len(matches)} ({(i+1)/len(matches)*100:.1f}%)")

        # Construct remote path
        remote_path = f"{M4_MAX_CORPUS_DIR}/{match['filepath']}"

        # Read file via SSH
        cmd = f"ssh {M4_MAX_USER} 'cat {remote_path}' 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            texts_collected.append({
                'training_idx': match['training_idx'],
                'corpus_poem_id': match['corpus_poem_id'],
                'title': match['title'],
                'author': match['author'],
                'year_approx': match['year_approx'],
                'period': match['period'],
                'text': result.stdout.strip(),
                'text_length': len(result.stdout.strip()),
                'filepath': match['filepath']
            })
        else:
            download_failures.append(match)
            print(f"   ✗ Failed to download: {match['filepath']}")

    print(f"\n   ✓ Downloaded: {len(texts_collected)} texts")
    if download_failures:
        print(f"   ✗ Failed: {len(download_failures)} downloads")

    # Save collected texts
    print(f"\n8. Saving collected texts...")
    texts_df = pd.DataFrame(texts_collected)
    texts_df.to_csv(OUTPUT_FILE, index=False)
    print(f"   ✓ Saved to {OUTPUT_FILE}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal training poems: {len(training_df)}")
    print(f"Matched to corpus: {len(matches)}")
    print(f"Texts downloaded: {len(texts_collected)}")
    print(f"Missing from corpus: {len(missing)}")
    print(f"Download failures: {len(download_failures)}")

    if texts_collected:
        avg_length = sum(t['text_length'] for t in texts_collected) / len(texts_collected)
        print(f"\nAverage text length: {avg_length:.0f} characters")
        print(f"Shortest text: {min(t['text_length'] for t in texts_collected)} characters")
        print(f"Longest text: {max(t['text_length'] for t in texts_collected)} characters")

    print("\n" + "="*80)
    print("NEXT STEP: Format as instruction-tuning dataset")
    print("="*80)

    # Clean up temp file
    local_metadata.unlink()

if __name__ == "__main__":
    main()
