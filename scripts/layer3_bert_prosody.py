#!/usr/bin/env python3
"""
Layer 3: Prosodic Conditioning for BERT Embeddings
Takes BERT contextual embeddings and adds prosodic features (meter, rhyme)

This layer tests whether prosodic constraints (meter, rhyme) influence
the semantic trajectory through a sonnet.

Architecture:
- Layer 1: EEBO-BERT (historical semantics)
- Layer 2: Poetry-BERT (poetry specialization)
- Layer 3: Prosodic conditioning (THIS LAYER)

Usage:
    python layer3_bert_prosody.py --model eebo    # Use EEBO-BERT
    python layer3_bert_prosody.py --model poetry  # Use Poetry-BERT
"""

import numpy as np
import json
import pandas as pd
import torch
from pathlib import Path
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
import prosodic as p
import argparse

# Paths
EEBO_BERT_PATH = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned"
POETRY_BERT_PATH = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/poetry_bert_trained"
SONNETS_PATH = "corpus_samples/shakespeare_sonnets_parsed.jsonl"
OUTPUT_DIR = "results"


def get_line_embedding(text, model, tokenizer, device):
    """
    Get contextualized embedding for a line of text.
    Returns the mean of BERT's last hidden layer.
    """
    tokens = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
    tokens = {k: v.to(device) for k, v in tokens.items()}

    with torch.no_grad():
        outputs = model(**tokens)

    # Mean of last hidden layer (excluding [CLS] and [SEP])
    embeddings = outputs.last_hidden_state[0, 1:-1, :].mean(dim=0)
    return embeddings.cpu().numpy()


def score_metrical_deviation(line_text):
    """
    Score deviation from perfect iambic pentameter.

    Returns:
        deviation_score: Number of syllables that deviate from 0-1-0-1-0-1-0-1-0-1
        actual_pattern: The actual stress pattern detected
    """
    try:
        parsed = p.Text(line_text).parse()

        if not parsed or len(parsed) == 0:
            return 0.0, None

        # Get best parse
        best_parse = parsed[0][0]

        if not best_parse.stress_ints:
            return 0.0, None

        actual_pattern = list(best_parse.stress_ints)

        # Ideal iambic pentameter: 0 1 0 1 0 1 0 1 0 1
        ideal_pattern = [0, 1] * 5

        # Calculate deviation (number of mismatches)
        min_len = min(len(actual_pattern), len(ideal_pattern))
        deviations = sum(1 for i in range(min_len) if actual_pattern[i] != ideal_pattern[i])

        # Add penalty for wrong syllable count
        length_penalty = abs(len(actual_pattern) - 10)

        total_deviation = deviations + length_penalty

        return total_deviation, actual_pattern

    except Exception as e:
        return 0.0, None


def detect_rhyme_pairs(lines):
    """
    Detect rhyme pairs in sonnet (simplified phonetic matching).

    Shakespearean sonnet rhyme scheme: ABAB CDCD EFEF GG
    Returns list of (line_idx1, line_idx2) tuples for rhyming lines
    """
    # For simplicity, use last 2-3 characters as rough rhyme detector
    # In production, would use phonetic dictionary

    def get_rhyme_key(line):
        """Extract potential rhyme from end of line"""
        # Remove punctuation and get last word
        clean = line.lower().strip().rstrip('.,!?;:')
        words = clean.split()
        if not words:
            return ""
        last_word = words[-1]
        # Use last 2-3 chars as rough rhyme
        return last_word[-3:] if len(last_word) >= 3 else last_word

    rhyme_keys = [get_rhyme_key(line) for line in lines]

    # Shakespearean sonnet rhyme scheme
    expected_pairs = [
        (0, 2), (1, 3),      # ABAB
        (4, 6), (5, 7),      # CDCD
        (8, 10), (9, 11),    # EFEF
        (12, 13)             # GG (couplet)
    ]

    rhyme_pairs = []
    for i, j in expected_pairs:
        if i < len(rhyme_keys) and j < len(rhyme_keys):
            if rhyme_keys[i] and rhyme_keys[j] and rhyme_keys[i] == rhyme_keys[j]:
                rhyme_pairs.append((i, j))

    return rhyme_pairs


def create_prosodic_features(lines):
    """
    Extract prosodic features for all lines.

    Returns:
        meter_deviations: List of metrical deviation scores per line
        rhyme_pairs: List of (idx1, idx2) tuples for rhyming lines
    """
    meter_deviations = []

    for line in lines:
        deviation, _ = score_metrical_deviation(line)
        meter_deviations.append(deviation)

    rhyme_pairs = detect_rhyme_pairs(lines)

    return meter_deviations, rhyme_pairs


def calculate_tortuosity(embeddings):
    """
    Calculate trajectory tortuosity from sequence of embeddings.

    Tortuosity = cumulative angular deviation / euclidean distance
    """
    if len(embeddings) < 2:
        return 0.0

    total_angle = 0.0

    for i in range(len(embeddings) - 2):
        v1 = embeddings[i+1] - embeddings[i]
        v2 = embeddings[i+2] - embeddings[i+1]

        # Normalize
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)

        # Calculate angle
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle = np.arccos(cos_angle)
        total_angle += angle

    euclidean = np.linalg.norm(embeddings[-1] - embeddings[0])

    if euclidean < 1e-8:
        return 0.0

    return total_angle / euclidean


def add_prosodic_conditioning(embeddings, meter_deviations, rhyme_pairs):
    """
    Add prosodic features to semantic embeddings.

    Method: Concatenate prosodic features to each embedding vector

    Args:
        embeddings: (n_lines, 768) BERT embeddings
        meter_deviations: (n_lines,) metrical deviation scores
        rhyme_pairs: List of (idx1, idx2) rhyme pairs

    Returns:
        conditioned_embeddings: (n_lines, 768 + prosodic_dims) augmented embeddings
    """
    n_lines = len(embeddings)

    # Create prosodic feature vectors
    prosodic_features = []

    for i in range(n_lines):
        features = []

        # Feature 1: Metrical deviation (normalized)
        meter_norm = meter_deviations[i] / 10.0  # Scale to ~[0, 1]
        features.append(meter_norm)

        # Feature 2: Is this line part of a rhyme pair?
        is_rhyme = any(i in pair for pair in rhyme_pairs)
        features.append(1.0 if is_rhyme else 0.0)

        # Feature 3: Position in sonnet (normalized)
        position = i / (n_lines - 1) if n_lines > 1 else 0.0
        features.append(position)

        # Feature 4: Is couplet (last 2 lines)
        is_couplet = 1.0 if i >= n_lines - 2 else 0.0
        features.append(is_couplet)

        prosodic_features.append(features)

    prosodic_features = np.array(prosodic_features)

    # Concatenate to embeddings
    conditioned = np.concatenate([embeddings, prosodic_features], axis=1)

    return conditioned


def analyze_sonnet(sonnet, model, tokenizer, device, add_prosody=False):
    """
    Analyze a single sonnet with optional prosodic conditioning.

    Args:
        sonnet: Dictionary with 'sonnet_number' and 'lines'
        model: BERT model
        tokenizer: BERT tokenizer
        device: torch device
        add_prosody: Whether to add prosodic features

    Returns:
        Dictionary with tortuosity metrics
    """
    lines = sonnet['lines']

    # Get BERT embeddings for each line
    line_embeddings = []
    for line in lines:
        if line.strip():
            emb = get_line_embedding(line, model, tokenizer, device)
            line_embeddings.append(emb)

    if len(line_embeddings) < 2:
        return None

    line_embeddings = np.array(line_embeddings)

    # Extract prosodic features
    meter_deviations, rhyme_pairs = create_prosodic_features(lines)

    # Calculate base (semantic-only) tortuosity
    semantic_tort = calculate_tortuosity(line_embeddings)

    # Calculate prosody-conditioned tortuosity if requested
    if add_prosody:
        conditioned_embeddings = add_prosodic_conditioning(
            line_embeddings,
            meter_deviations,
            rhyme_pairs
        )
        prosody_tort = calculate_tortuosity(conditioned_embeddings)
    else:
        prosody_tort = semantic_tort

    # Calculate per-line tortuosity (distance between consecutive lines)
    line_torts = []
    for i in range(len(line_embeddings) - 1):
        dist = np.linalg.norm(line_embeddings[i+1] - line_embeddings[i])
        line_torts.append(dist)

    mean_line_tort = np.mean(line_torts) if line_torts else 0.0

    # Calculate couplet tortuosity (distance between last 2 lines)
    if len(line_embeddings) >= 2:
        couplet_tort = np.linalg.norm(line_embeddings[-1] - line_embeddings[-2])
    else:
        couplet_tort = 0.0

    # Calculate metrics
    avg_meter_dev = np.mean(meter_deviations)
    num_rhymes = len(rhyme_pairs)

    return {
        'sonnet': sonnet['sonnet_number'],
        'semantic_tortuosity': semantic_tort,
        'prosody_conditioned_tortuosity': prosody_tort,
        'difference': prosody_tort - semantic_tort,
        'percent_change': ((prosody_tort - semantic_tort) / semantic_tort * 100) if semantic_tort > 0 else 0.0,
        'mean_line_tortuosity': mean_line_tort,
        'couplet_tortuosity': couplet_tort,
        'avg_metrical_deviation': avg_meter_dev,
        'num_rhyme_pairs': num_rhymes,
        'num_lines': len(line_embeddings)
    }


def main():
    parser = argparse.ArgumentParser(description='Layer 3: Prosodic conditioning for BERT embeddings')
    parser.add_argument('--model', choices=['base', 'eebo', 'poetry'], default='eebo',
                       help='Which BERT model to use (base, eebo, or poetry)')
    args = parser.parse_args()

    print("="*70)
    print("LAYER 3: PROSODIC CONDITIONING FOR BERT EMBEDDINGS")
    print("="*70)

    # Load BERT model
    if args.model == 'base':
        model_path = 'bert-base-uncased'
        model_name = "bert-base-uncased"
    elif args.model == 'eebo':
        model_path = EEBO_BERT_PATH
        model_name = "EEBO-BERT"
    else:
        model_path = POETRY_BERT_PATH
        model_name = "Poetry-BERT"

    print(f"\nLoading {model_name}...")
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertModel.from_pretrained(model_path)
    model.eval()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)
    print(f"✓ {model_name} loaded on {device}")

    # Load sonnets
    print(f"\nLoading sonnets from {SONNETS_PATH}...")
    sonnets = []
    with open(SONNETS_PATH, 'r') as f:
        for line in f:
            sonnets.append(json.loads(line))
    print(f"✓ Loaded {len(sonnets)} sonnets")

    # Analyze all sonnets
    print(f"\nAnalyzing sonnets with prosodic conditioning...")
    results = []

    for sonnet in tqdm(sonnets, desc="Processing"):
        result = analyze_sonnet(sonnet, model, tokenizer, device, add_prosody=True)
        if result:
            results.append(result)

    df = pd.DataFrame(results)

    # Summary statistics
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)

    print(f"\nModel: {model_name}")
    print(f"Sonnets analyzed: {len(df)}")

    print(f"\nSemantic-only tortuosity:")
    print(f"  Mean: {df['semantic_tortuosity'].mean():.2f}")
    print(f"  SD:   {df['semantic_tortuosity'].std():.2f}")

    print(f"\nProsody-conditioned tortuosity:")
    print(f"  Mean: {df['prosody_conditioned_tortuosity'].mean():.2f}")
    print(f"  SD:   {df['prosody_conditioned_tortuosity'].std():.2f}")

    print(f"\nEffect of prosodic conditioning:")
    print(f"  Mean difference: {df['difference'].mean():+.2f}")
    print(f"  Mean percent change: {df['percent_change'].mean():+.2f}%")

    print(f"\nProsodic metrics:")
    print(f"  Avg metrical deviation: {df['avg_metrical_deviation'].mean():.2f} syllables")
    print(f"  Avg rhyme pairs detected: {df['num_rhyme_pairs'].mean():.1f} per sonnet")

    # Top 10 with biggest prosodic effect
    print(f"\n\nTop 10 sonnets where prosody has biggest effect:")
    print("="*70)
    top_effect = df.nlargest(10, 'difference')[['sonnet', 'semantic_tortuosity', 'prosody_conditioned_tortuosity', 'difference', 'percent_change']]
    print(top_effect.to_string(index=False))

    # Save results
    output_path = Path(OUTPUT_DIR) / f"shakespeare_sonnets_layer3_{args.model}_bert.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to {output_path}")


if __name__ == "__main__":
    main()
