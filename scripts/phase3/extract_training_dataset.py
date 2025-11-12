#!/usr/bin/env python3
"""
Extract complete training dataset: 397 matched poems with texts + classifications.
Uses SCP to copy files from M4 Max.
"""

import pandas as pd
import subprocess
from pathlib import Path
from difflib import SequenceMatcher
import json

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

BASE_DIR = Path("/Users/justin/Repos/AI Project")
M4_MAX_USER = "justin@100.65.21.63"
M4_MAX_CORPUS_DIR = "/Users/justin/poetry-bert-formalism/Data/processed/poetry_platform_renamed"

TRAINING_FILE = BASE_DIR / "Data/phase3/training_set_456_poems.csv"
CORPUS_METADATA = BASE_DIR / "Data/phase3/corpus_metadata.csv"
OUTPUT_FILE = BASE_DIR / "Data/phase3/training_dataset_complete.jsonl"

def main():
    print("="*80)
    print("PHASE 3B: EXTRACT COMPLETE TRAINING DATASET")
    print("="*80)

    # Load datasets
    print("\n1. Loading datasets...")
    training_df = pd.read_csv(TRAINING_FILE)
    corpus_df = pd.read_csv(CORPUS_METADATA)
    print(f"   ✓ Training poems: {len(training_df)}")
    print(f"   ✓ Corpus poems: {len(corpus_df)}")

    # Match poems
    print("\n2. Matching poems...")
    matched = []
    for idx, row in training_df.iterrows():
        title, author = row['title'], row['author']
        candidates = corpus_df[corpus_df['author'].str.contains(
            author.split()[-1] if pd.notna(author) else '',
            case=False, na=False
        )]

        best_match, best_score = None, 0
        for _, cand in candidates.iterrows():
            score = similarity(str(title), str(cand['title']))
            if score > best_score:
                best_match, best_score = cand, score

        if best_score > 0.6:
            matched.append((idx, best_match, row))

    print(f"   ✓ Matched: {len(matched)} poems")

    # Extract texts
    print(f"\n3. Extracting {len(matched)} texts from M4 Max...")

    texts_collected = []
    temp_dir = Path("/tmp/phase3_texts")
    temp_dir.mkdir(exist_ok=True)

    for i, (training_idx, corpus_match, training_row) in enumerate(matched):
        if (i + 1) % 50 == 0:
            print(f"   Progress: {i+1}/{len(matched)} ({(i+1)/len(matched)*100:.1f}%)")

        remote_path = f"{M4_MAX_USER}:{M4_MAX_CORPUS_DIR}/{corpus_match['filepath']}"
        local_path = temp_dir / f"poem_{i}.txt"

        cmd = ["scp", "-q", remote_path, str(local_path)]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode == 0 and local_path.exists():
            text = local_path.read_text()

            # Build complete training example
            example = {
                'training_idx': int(training_idx),
                'corpus_poem_id': int(corpus_match['poem_id']),
                'title': training_row['title'],
                'author': training_row['author'],
                'year_approx': int(training_row['year_approx']) if pd.notna(training_row['year_approx']) else None,
                'text': text,
                # All 28 classification fields
                'period': training_row['period'],
                'literary_movement': training_row['literary_movement'] if pd.notna(training_row['literary_movement']) else '',
                'register': training_row['register'],
                'rhetorical_genre': training_row['rhetorical_genre'],
                'discursive_structure': training_row['discursive_structure'],
                'discourse_type': training_row['discourse_type'],
                'narrative_level': training_row['narrative_level'] if pd.notna(training_row['narrative_level']) else '',
                'diegetic_mimetic': training_row['diegetic_mimetic'],
                'focalization': training_row['focalization'],
                'person': training_row['person'],
                'deictic_orientation': training_row['deictic_orientation'],
                'addressee_type': training_row['addressee_type'],
                'deictic_object': training_row['deictic_object'],
                'temporal_orientation': training_row['temporal_orientation'],
                'temporal_structure': training_row['temporal_structure'],
                'tradition': training_row['tradition'],
                'mode': training_row['mode'],
                'genre': training_row['genre'] if pd.notna(training_row['genre']) else '',
                'stanza_structure': training_row['stanza_structure'] if pd.notna(training_row['stanza_structure']) else '',
                'meter': training_row['meter'] if pd.notna(training_row['meter']) else '',
                'rhyme': training_row['rhyme'] if pd.notna(training_row['rhyme']) else '',
            }

            texts_collected.append(example)
            local_path.unlink()  # Clean up

    print(f"\n   ✓ Extracted {len(texts_collected)} complete training examples")

    # Save to JSONL
    print(f"\n4. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for example in texts_collected:
            f.write(json.dumps(example) + '\n')
    print(f"   ✓ Saved")

    # Stats
    print("\n" + "="*80)
    print("TRAINING DATASET COMPLETE")
    print("="*80)
    print(f"\nTotal examples: {len(texts_collected)}")

    lengths = [len(ex['text']) for ex in texts_collected]
    print(f"\nText statistics:")
    print(f"  Average length: {sum(lengths)/len(lengths):.0f} characters")
    print(f"  Shortest: {min(lengths)} characters")
    print(f"  Longest: {max(lengths)} characters")

    # Period distribution
    periods = {}
    for ex in texts_collected:
        p = ex['period']
        periods[p] = periods.get(p, 0) + 1

    print(f"\nPeriod distribution:")
    for period, count in sorted(periods.items(), key=lambda x: -x[1])[:10]:
        print(f"  {period}: {count}")

    print("\n" + "="*80)
    print("✓ READY FOR NEXT STEP: Format as instruction-tuning dataset")
    print("="*80)

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
