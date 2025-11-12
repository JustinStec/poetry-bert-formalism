#!/usr/bin/env python3
"""
Merge cleaned 404 poems with 52 gold-standard poems into final training dataset.
Total: 456 poems for Phase 3 LLM fine-tuning.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
GOLD_FILE = BASE_DIR / "data/phase3/gold_standard_52_poems_with_narrative_level.csv"
CLASSIFIED_FILE = BASE_DIR / "data/phase3/404_poems_classified_final.csv"
OUTPUT_FILE = BASE_DIR / "data/phase3/training_set_456_poems.csv"

print("="*60)
print("MERGING TRAINING DATASET")
print("="*60)

# Load both datasets
print("\nLoading data...")
gold_df = pd.read_csv(GOLD_FILE)
classified_df = pd.read_csv(CLASSIFIED_FILE)

print(f"  Gold standard: {len(gold_df)} poems")
print(f"  Classified: {len(classified_df)} poems")

# Check column alignment
gold_cols = set(gold_df.columns)
classified_cols = set(classified_df.columns)

print("\n" + "="*60)
print("COLUMN COMPARISON")
print("="*60)

print(f"\nGold standard columns: {len(gold_cols)}")
print(f"Classified columns: {len(classified_cols)}")

# Columns only in gold
only_gold = gold_cols - classified_cols
if only_gold:
    print(f"\nOnly in gold standard: {only_gold}")

# Columns only in classified
only_classified = classified_cols - gold_cols
if only_classified:
    print(f"\nOnly in classified: {only_classified}")

# Add source column to track origin
gold_df['source'] = 'gold_standard'
classified_df['source'] = 'colab_classified'

# Standardize column order (use gold standard as template)
target_columns = [
    'source',
    'title', 'author', 'year_approx',
    'period', 'literary_movement',
    'register', 'rhetorical_genre', 'discursive_structure', 'discourse_type',
    'narrative_level', 'diegetic_mimetic', 'focalization', 'person',
    'deictic_orientation', 'addressee_type', 'deictic_object',
    'temporal_orientation', 'temporal_structure', 'tradition',
    'mode', 'genre', 'stanza_structure', 'meter', 'rhyme'
]

# Add any columns that exist in either dataset but not in target list
all_cols = gold_cols | classified_cols
for col in all_cols:
    if col not in target_columns:
        target_columns.append(col)

# Ensure both dataframes have all columns (fill missing with NaN)
for col in target_columns:
    if col not in gold_df.columns:
        gold_df[col] = None
    if col not in classified_df.columns:
        classified_df[col] = None

# Reorder columns
gold_df = gold_df[target_columns]
classified_df = classified_df[target_columns]

# Merge
merged_df = pd.concat([gold_df, classified_df], ignore_index=True)

print("\n" + "="*60)
print("MERGED DATASET")
print("="*60)

print(f"\nTotal poems: {len(merged_df)}")
print(f"  From gold standard: {(merged_df['source'] == 'gold_standard').sum()}")
print(f"  From Colab classification: {(merged_df['source'] == 'colab_classified').sum()}")

print(f"\nColumns: {len(merged_df.columns)}")

# Quality checks
print("\n" + "="*60)
print("QUALITY CHECKS")
print("="*60)

print("\nMissing values by column:")
missing = merged_df.isnull().sum()
missing = missing[missing > 0].sort_values(ascending=False)
for col, count in missing.items():
    pct = (count / len(merged_df)) * 100
    print(f"  {col}: {count} ({pct:.1f}%)")

print("\nPeriod distribution:")
print(merged_df['period'].value_counts().head(15))

print("\nMode distribution:")
print(merged_df['mode'].value_counts())

print("\nRhetorical Genre distribution:")
print(merged_df['rhetorical_genre'].value_counts())

print("\nSource distribution:")
print(merged_df['source'].value_counts())

# Save
merged_df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "="*60)
print("✓ MERGE COMPLETE")
print("="*60)

print(f"\n✓ Training dataset saved: {OUTPUT_FILE}")
print(f"✓ Total poems: {len(merged_df)}")
print(f"✓ Total columns: {len(merged_df.columns)}")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("\n1. Review sample poems to verify quality")
print("2. Fetch full texts for all 456 poems")
print("3. Format as instruction-tuning dataset")
print("4. Fine-tune LLM on M4 Max with MLX")
print("5. Apply to 116,674 corpus poems")
print("\nReady for Phase 3 fine-tuning!")
