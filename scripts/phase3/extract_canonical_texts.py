#!/usr/bin/env python3
"""
Extract full poem texts for 457 training poems from M4 Max corpus.
The canonical poems ARE in the poetry_platform_renamed directory!
"""

import pandas as pd
from pathlib import Path
import subprocess
import re

BASE_DIR = Path("/Users/justin/Repos/AI Project")
M4_MAX_USER = "justin@100.65.21.63"
M4_MAX_CORPUS_DIR = "~/poetry-bert-formalism/Data/processed/poetry_platform_renamed"

TRAINING_FILE = BASE_DIR / "Data/phase3/training_set_456_poems.csv"
OUTPUT_FILE = BASE_DIR / "Data/phase3/training_poems_with_texts.jsonl"
MISSING_LOG = BASE_DIR / "Data/phase3/missing_texts.log"

def normalize_for_filename(text):
    """Normalize text for fuzzy filename matching."""
    if pd.isna(text):
        return ""
    # Remove common punctuation and extra whitespace
    text = re.sub(r'[,:\.\!\?]', '', text)
    text = ' '.join(text.split())
    return text.lower().strip()

def search_author_directory(author, title_keywords):
    """Search for poem in author's directory on M4 Max."""
    # Try different author name formats
    author_variants = []

    # If already in "Last, First" format, use it
    if ',' in author:
        author_variants.append(author)
    # Convert "First Last" to "Last, First"
    elif ' ' in author:
        parts = author.split()
        # Handle "Lord Byron" style names
        if parts[0] in ['Lord', 'Sir', 'Dame', 'Earl']:
            author_variants.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
            author_variants.append(f"{parts[0]}, {' '.join(parts[1:])}")  # "Lord, Byron"
        else:
            author_variants.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
    else:
        author_variants.append(author)

    for author_name in author_variants:
        # Escape special characters for shell
        author_escaped = author_name.replace("'", "'\\''")

        # List files in author directory
        cmd = f"ssh {M4_MAX_USER} 'ls \"{M4_MAX_CORPUS_DIR}/{author_escaped}/\" 2>/dev/null'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            files = result.stdout.strip().split('\n')

            # Search for matching filename
            for filename in files:
                filename_lower = filename.lower()
                # Check if title keywords are in filename
                if all(kw in filename_lower for kw in title_keywords):
                    return f"{author_name}/{filename}"

    return None

def fetch_poem_text(filepath):
    """Fetch poem text from M4 Max."""
    cmd = f'ssh {M4_MAX_USER} "cat {M4_MAX_CORPUS_DIR}/{filepath}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    return None

def main():
    print("="*80)
    print("PHASE 3B: EXTRACT CANONICAL POEM TEXTS FROM M4 MAX")
    print("="*80)

    # Load training dataset
    print("\n1. Loading training dataset...")
    df = pd.read_csv(TRAINING_FILE)
    print(f"   ✓ Loaded {len(df)} training poems")

    # Extract texts
    print("\n2. Matching and extracting texts from M4 Max...")

    texts_collected = []
    missing = []

    for idx, row in df.iterrows():
        title = row['title']
        author = row['author']

        # Extract key words from title for matching
        title_norm = normalize_for_filename(title)
        # Take first few significant words
        title_keywords = [w for w in title_norm.split()[:5] if len(w) > 3]

        # Handle NaN values
        title_display = str(title)[:40] if pd.notna(title) else "Unknown"
        author_display = str(author)[:20] if pd.notna(author) else "Unknown"
        print(f"   [{idx+1}/{len(df)}] {title_display:40s} by {author_display:20s}", end=' ... ')

        # Search for poem
        filepath = search_author_directory(author, title_keywords)

        if filepath:
            # Fetch text
            text = fetch_poem_text(filepath)

            if text:
                texts_collected.append({
                    'training_idx': idx,
                    'title': title,
                    'author': author,
                    'year_approx': row['year_approx'],
                    'period': row['period'],
                    'text': text,
                    'filepath': filepath,
                    'text_length': len(text)
                })
                print(f"✓ ({len(text)} chars)")
            else:
                missing.append((idx, title, author, 'fetch_failed'))
                print("✗ fetch failed")
        else:
            missing.append((idx, title, author, 'not_found'))
            print("✗ not found")

    # Save collected texts
    print(f"\n3. Saving {len(texts_collected)} collected texts...")

    import json
    with open(OUTPUT_FILE, 'w') as f:
        for item in texts_collected:
            f.write(json.dumps(item) + '\n')

    print(f"   ✓ Saved to {OUTPUT_FILE}")

    # Save missing log
    if missing:
        print(f"\n4. Logging {len(missing)} missing poems...")
        with open(MISSING_LOG, 'w') as f:
            for idx, title, author, reason in missing:
                f.write(f"{idx}\t{title}\t{author}\t{reason}\n")
        print(f"   ✓ Saved to {MISSING_LOG}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal training poems: {len(df)}")
    print(f"Texts collected: {len(texts_collected)} ({len(texts_collected)/len(df)*100:.1f}%)")
    print(f"Missing: {len(missing)} ({len(missing)/len(df)*100:.1f}%)")

    if texts_collected:
        lengths = [t['text_length'] for t in texts_collected]
        print(f"\nText statistics:")
        print(f"  Average length: {sum(lengths)/len(lengths):.0f} characters")
        print(f"  Shortest: {min(lengths)} characters")
        print(f"  Longest: {max(lengths)} characters")

    print("\n" + "="*80)
    if len(texts_collected) >= 400:
        print("✓ READY FOR NEXT STEP: Format instruction-tuning dataset")
    else:
        print(f"⚠ Only collected {len(texts_collected)}/457 texts")
        print("  Review missing_texts.log and adjust matching strategy")
    print("="*80)

if __name__ == "__main__":
    main()
