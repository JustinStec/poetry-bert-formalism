#!/usr/bin/env python3
"""
Prepare Hierarchical Training Data for Poetry-EEBO-BERT

Extracts EEBO-period sonnets with hierarchical structure annotations:
- Token level (for MLM)
- Line level (14 lines per sonnet)
- Quatrain level (3 quatrains + 1 couplet)
- Sonnet level (complete poem)

Hierarchical structure for contrastive learning:
- Line pairs: Adjacent lines, rhyming lines (positive), random lines (negative)
- Quatrain pairs: Same quatrain (positive), different quatrain (negative)
- Sonnet level: All lines from same sonnet (positive), different sonnet (negative)

Output format: JSONL with hierarchical annotations
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


def load_shakespeare_sonnets(sonnets_path: str) -> List[Dict]:
    """
    Load Shakespeare's 154 sonnets from parsed JSONL.

    Returns:
        List of sonnet dictionaries with structure preserved
    """
    sonnets = []

    with open(sonnets_path, 'r') as f:
        for line in f:
            sonnet = json.loads(line)
            sonnets.append(sonnet)

    # Sort by sonnet number
    sonnets.sort(key=lambda x: x.get('sonnet_number', 999))

    print(f"Loaded {len(sonnets)} sonnets")
    return sonnets


def detect_rhyme_scheme(lines: List[str]) -> List[Tuple[int, int]]:
    """
    Detect rhyme pairs in Shakespearean sonnet (ABAB CDCD EFEF GG).

    Uses simple suffix matching as proxy for phonetic rhyme.
    In production, would use phonetic dictionary.

    Returns:
        List of (line_idx1, line_idx2) tuples for rhyming lines
    """
    def get_rhyme_key(line: str) -> str:
        """Extract potential rhyme from end of line"""
        clean = line.lower().strip().rstrip('.,!?;:\'"')
        words = clean.split()
        if not words:
            return ""
        last_word = words[-1]
        # Use last 3 chars as rough rhyme proxy
        return last_word[-3:] if len(last_word) >= 3 else last_word

    rhyme_keys = [get_rhyme_key(line) for line in lines]

    # Shakespearean sonnet rhyme scheme
    expected_pairs = [
        (0, 2), (1, 3),      # ABAB (quatrain 1)
        (4, 6), (5, 7),      # CDCD (quatrain 2)
        (8, 10), (9, 11),    # EFEF (quatrain 3)
        (12, 13)             # GG (couplet)
    ]

    rhyme_pairs = []
    for i, j in expected_pairs:
        if i < len(rhyme_keys) and j < len(rhyme_keys):
            if rhyme_keys[i] and rhyme_keys[j] and rhyme_keys[i] == rhyme_keys[j]:
                rhyme_pairs.append((i, j))

    return rhyme_pairs


def create_hierarchical_structure(sonnet: Dict) -> Dict:
    """
    Create hierarchical annotations for a sonnet.

    Hierarchy:
    - Lines: 14 individual lines
    - Quatrains: [0-3], [4-7], [8-11] (quatrains 1-3)
    - Couplet: [12-13]
    - Sonnet: All lines together

    Args:
        sonnet: Dictionary with 'sonnet_number' and 'lines'

    Returns:
        Hierarchical structure dictionary
    """
    lines = sonnet['lines']

    # Ensure exactly 14 lines (pad or truncate if needed)
    if len(lines) < 14:
        print(f"Warning: Sonnet {sonnet.get('sonnet_number')} has {len(lines)} lines (< 14), padding")
        lines = lines + [''] * (14 - len(lines))
    elif len(lines) > 14:
        print(f"Warning: Sonnet {sonnet.get('sonnet_number')} has {len(lines)} lines (> 14), truncating")
        lines = lines[:14]

    # Detect rhyme pairs
    rhyme_pairs = detect_rhyme_scheme(lines)

    # Build hierarchical structure
    structure = {
        'sonnet_id': sonnet.get('sonnet_number'),
        'lines': lines,
        'num_lines': len(lines),

        # Quatrain groupings
        'quatrain_1': list(range(0, 4)),
        'quatrain_2': list(range(4, 8)),
        'quatrain_3': list(range(8, 12)),
        'couplet': list(range(12, 14)),

        # Rhyme pairs for line-level contrastive learning
        'rhyme_pairs': rhyme_pairs,

        # Adjacent line pairs (for local coherence)
        'adjacent_pairs': [(i, i+1) for i in range(13)],

        # Metadata
        'title': sonnet.get('title', f"Sonnet {sonnet.get('sonnet_number')}"),
        'author': 'William Shakespeare',
        'period': 'EEBO',
        'date_range': '1595-1609'
    }

    return structure


def create_train_val_split(sonnets: List[Dict], val_ratio: float = 0.1, seed: int = 42) -> Tuple[List[Dict], List[Dict]]:
    """
    Split sonnets into training and validation sets.

    Args:
        sonnets: List of sonnet dictionaries
        val_ratio: Proportion for validation (default 0.1 = 10%)
        seed: Random seed for reproducibility

    Returns:
        (train_sonnets, val_sonnets)
    """
    random.seed(seed)

    # Shuffle sonnets
    shuffled = sonnets.copy()
    random.shuffle(shuffled)

    # Split
    n_val = int(len(sonnets) * val_ratio)
    val_sonnets = shuffled[:n_val]
    train_sonnets = shuffled[n_val:]

    print(f"\nSplit: {len(train_sonnets)} train, {len(val_sonnets)} validation")

    return train_sonnets, val_sonnets


def save_hierarchical_data(sonnets: List[Dict], output_path: str):
    """
    Save hierarchical sonnet data to JSONL.

    Args:
        sonnets: List of hierarchical sonnet structures
        output_path: Path to output JSONL file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        for sonnet in sonnets:
            f.write(json.dumps(sonnet) + '\n')

    print(f"Saved {len(sonnets)} sonnets to {output_path}")


def generate_statistics(sonnets: List[Dict]) -> Dict:
    """
    Generate statistics about the hierarchical dataset.

    Returns:
        Dictionary with dataset statistics
    """
    total_lines = sum(s['num_lines'] for s in sonnets)
    total_rhymes = sum(len(s['rhyme_pairs']) for s in sonnets)

    stats = {
        'num_sonnets': len(sonnets),
        'total_lines': total_lines,
        'avg_lines_per_sonnet': total_lines / len(sonnets) if sonnets else 0,
        'total_rhyme_pairs': total_rhymes,
        'avg_rhyme_pairs_per_sonnet': total_rhymes / len(sonnets) if sonnets else 0,
        'num_quatrains': len(sonnets) * 3,  # 3 quatrains per sonnet
        'num_couplets': len(sonnets),
    }

    return stats


def main():
    parser = argparse.ArgumentParser(description='Prepare hierarchical training data for Poetry-EEBO-BERT')
    parser.add_argument('--input', type=str,
                       default='corpus_samples/shakespeare_sonnets_parsed.jsonl',
                       help='Input JSONL file with parsed sonnets')
    parser.add_argument('--output-dir', type=str,
                       default='Data',
                       help='Output directory for hierarchical data')
    parser.add_argument('--val-ratio', type=float, default=0.1,
                       help='Validation set ratio (default: 0.1)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for train/val split')

    args = parser.parse_args()

    print("="*70)
    print("PREPARING HIERARCHICAL TRAINING DATA")
    print("="*70)

    # Load Shakespeare sonnets
    print(f"\nLoading sonnets from {args.input}...")
    sonnets_raw = load_shakespeare_sonnets(args.input)

    # Create hierarchical structures
    print("\nCreating hierarchical annotations...")
    sonnets_hierarchical = []
    for sonnet in sonnets_raw:
        structure = create_hierarchical_structure(sonnet)
        sonnets_hierarchical.append(structure)

    print(f"Created hierarchical structures for {len(sonnets_hierarchical)} sonnets")

    # Train/val split
    print("\nSplitting into train/val sets...")
    train_sonnets, val_sonnets = create_train_val_split(
        sonnets_hierarchical,
        val_ratio=args.val_ratio,
        seed=args.seed
    )

    # Save datasets
    print("\nSaving datasets...")
    train_path = f"{args.output_dir}/eebo_sonnets_hierarchical_train.jsonl"
    val_path = f"{args.output_dir}/eebo_sonnets_hierarchical_val.jsonl"

    save_hierarchical_data(train_sonnets, train_path)
    save_hierarchical_data(val_sonnets, val_path)

    # Generate and save statistics
    print("\nGenerating statistics...")
    train_stats = generate_statistics(train_sonnets)
    val_stats = generate_statistics(val_sonnets)

    stats = {
        'train': train_stats,
        'val': val_stats,
        'total': {
            'num_sonnets': train_stats['num_sonnets'] + val_stats['num_sonnets'],
            'total_lines': train_stats['total_lines'] + val_stats['total_lines'],
        }
    }

    stats_path = f"{args.output_dir}/eebo_sonnets_hierarchical_stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print("\n" + "="*70)
    print("DATASET STATISTICS")
    print("="*70)
    print(f"\nTrain set:")
    for key, value in train_stats.items():
        print(f"  {key}: {value}")

    print(f"\nValidation set:")
    for key, value in val_stats.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("DATA PREPARATION COMPLETE")
    print("="*70)
    print(f"\nOutput files:")
    print(f"  Train: {train_path}")
    print(f"  Val: {val_path}")
    print(f"  Stats: {stats_path}")


if __name__ == "__main__":
    main()
