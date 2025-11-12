#!/usr/bin/env python3
"""
Match training poems to corpus metadata and extract texts from M4 Max.
Uses the corpus_final_metadata.csv which has filepaths for all 116K poems.
"""

import pandas as pd
from pathlib import Path
import subprocess
import json
from difflib import SequenceMatcher

BASE_DIR = Path("/Users/justin/Repos/AI Project")
M4_MAX_USER = "justin@100.65.21.63"
M4_MAX_CORPUS_DIR = "~/poetry-bert-formalism/Data/processed/poetry_platform_renamed"

TRAINING_FILE = BASE_DIR / "Data/phase3/training_set_456_poems.csv"
CORPUS_METADATA = BASE_DIR / "Data/phase3/corpus_metadata.csv"
OUTPUT_FILE = BASE_DIR / "Data/phase3/training_poems_with_texts.jsonl"

def similarity(a, b):
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def main():
    print("="*80)
    print("PHASE 3B: MATCH & EXTRACT TRAINING POEM TEXTS")
    print("="*80)

    # Load datasets
    print("\n1. Loading datasets...")
    training_df = pd.read_csv(TRAINING_FILE)
    corpus_df = pd.read_csv(CORPUS_METADATA)
    print(f"   ✓ Training poems: {len(training_df)}")
    print(f"   ✓ Corpus poems: {len(corpus_df)}")

    # Match training poems to corpus
    print("\n2. Matching poems...")

    matched = []
    unmatched = []

    for idx, row in training_df.iterrows():
        title = row['title']
        author = row['author']

        # Search for matches in corpus
        candidates = corpus_df[
            (corpus_df['author'].str.contains(author.split()[-1] if pd.notna(author) else '', case=False, na=False))
        ]

        if len(candidates) == 0:
            unmatched.append((idx, title, author, 'no_author_match'))
            continue

        # Find best title match
        best_match = None
        best_score = 0

        for _, candidate in candidates.iterrows():
            score = similarity(str(title), str(candidate['title']))
            if score > best_score:
                best_score = score
                best_match = candidate

        if best_score > 0.6:  # Threshold for match
            matched.append({
                'training_idx': idx,
                'title': title,
                'author': author,
                'corpus_poem_id': best_match['poem_id'],
                'corpus_title': best_match['title'],
                'corpus_author': best_match['author'],
                'filepath': best_match['filepath'],
                'match_score': best_score
            })
        else:
            unmatched.append((idx, title, author, f'low_score_{best_score:.2f}'))

    print(f"   ✓ Matched: {len(matched)} poems")
    print(f"   ✗ Unmatched: {len(unmatched)} poems")

    # Extract texts from M4 Max
    print(f"\n3. Extracting {len(matched)} texts from M4 Max...")

    texts_collected = []

    for i, match in enumerate(matched):
        if (i + 1) % 50 == 0:
            print(f"   Progress: {i+1}/{len(matched)} ({(i+1)/len(matched)*100:.1f}%)")

        # Construct SSH command to read file
        # Escape spaces and special characters in filepath
        filepath_escaped = match['filepath'].replace('\\', '\\\\').replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')
        cmd = f"ssh {M4_MAX_USER} cat {M4_MAX_CORPUS_DIR}/{filepath_escaped} 2>/dev/null"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0 and result.stdout:
            # Get classification fields from training data
            training_row = training_df.iloc[match['training_idx']]

            texts_collected.append({
                'training_idx': match['training_idx'],
                'corpus_poem_id': int(match['corpus_poem_id']),
                'title': match['title'],
                'author': match['author'],
                'year_approx': int(training_row['year_approx']) if pd.notna(training_row['year_approx']) else None,
                'text': result.stdout.strip(),
                # Classification fields
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
            })

    print(f"\n   ✓ Extracted {len(texts_collected)} texts")

    # Save to JSONL
    print(f"\n4. Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        for item in texts_collected:
            f.write(json.dumps(item) + '\n')
    print(f"   ✓ Saved {len(texts_collected)} training examples")

    # Stats
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nTotal training poems: {len(training_df)}")
    print(f"Texts collected: {len(texts_collected)} ({len(texts_collected)/len(training_df)*100:.1f}%)")
    print(f"Unmatched: {len(unmatched)} ({len(unmatched)/len(training_df)*100:.1f}%)")

    if texts_collected:
        lengths = [len(t['text']) for t in texts_collected]
        print(f"\nText length statistics:")
        print(f"  Average: {sum(lengths)/len(lengths):.0f} characters")
        print(f"  Shortest: {min(lengths)} characters")
        print(f"  Longest: {max(lengths)} characters")

    if len(texts_collected) >= 400:
        print("\n" + "="*80)
        print("✓ READY FOR NEXT STEP: Format instruction-tuning dataset")
        print("="*80)

if __name__ == "__main__":
    main()
