#!/usr/bin/env python3
"""
Merge all classification results from parallel sessions into final CSV.
"""

import json
import csv
from pathlib import Path

def main():
    classifications_dir = Path.home() / "poetry-bert-formalism" / "data" / "classifications"
    output_file = Path.home() / "poetry-bert-formalism" / "data" / "classified_poems_complete.csv"

    print("="*80)
    print("MERGING CLASSIFICATION RESULTS")
    print("="*80)

    # Find all classified batch files
    classified_files = sorted(classifications_dir.glob("*_classified.json"))
    print(f"\nFound {len(classified_files)} classified batch files")

    all_classifications = []

    for batch_file in classified_files:
        print(f"Reading {batch_file.name}...")
        with open(batch_file, 'r') as f:
            batch = json.load(f)
            all_classifications.extend(batch)

    print(f"\nTotal poems classified: {len(all_classifications):,}")

    # Write to CSV
    print(f"\nWriting to {output_file}...")

    fieldnames = [
        'poem_id', 'filename',
        'period', 'literary_movement',
        'register', 'rhetorical_genre', 'discursive_structure', 'discourse_type',
        'narrative_level', 'diegetic_mimetic', 'focalization', 'person',
        'deictic_orientation', 'addressee_type', 'deictic_object',
        'temporal_orientation', 'temporal_structure', 'tradition',
        'mode', 'genre', 'stanza_structure', 'meter', 'rhyme'
    ]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for classification in all_classifications:
            writer.writerow(classification)

    print(f"✓ Complete! {len(all_classifications):,} poems written to:")
    print(f"  {output_file}")

    # Statistics
    print(f"\n{'='*80}")
    print("STATISTICS")
    print("="*80)

    file_size_mb = output_file.stat().st_size / 1e6
    print(f"Output file size: {file_size_mb:.1f} MB")
    print(f"Total poems: {len(all_classifications):,}")
    print(f"Average per session: {len(all_classifications) / len(set(f.name.split('_')[0] for f in classified_files)):.0f}")

if __name__ == "__main__":
    main()
