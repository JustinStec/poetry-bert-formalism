#!/usr/bin/env python3
"""
Enhanced Layer 3: Meter and Rhyme-Conditioned Semantic Trajectory Analysis
Tests whether metrical deviation and rhyme constraints force semantic detours
"""
import numpy as np
import json
from gensim.models import KeyedVectors
from pathlib import Path
import pandas as pd
import prosodic as p

# Load EEBO embeddings
print("Loading EEBO embeddings...")
kv_path = Path("/Users/justin/Repos/AI Project/Data/Historical_Embeddings/Aligned/eebo_1595-1700_aligned.kv")
kv = KeyedVectors.load(str(kv_path), mmap='r')
print(f"✓ Loaded {len(kv)} words\n")

# Load sonnets
print("Loading sonnets...")
sonnets_path = Path("/Users/justin/Repos/AI Project/corpus_samples/shakespeare_sonnets_parsed.jsonl")
sonnets = []
with open(sonnets_path, 'r') as f:
    for line in f:
        sonnets.append(json.loads(line))
print(f"✓ Loaded {len(sonnets)} sonnets\n")

def tokenize_simple(text):
    """Simple tokenization removing punctuation"""
    return text.lower().replace("'", "").replace("'", "").replace(",", "").replace(".", "").replace("?", "").replace(":", "").replace(";", "").replace("!", "").replace("—", "").split()

def calculate_tortuosity(embeddings):
    """Calculate trajectory tortuosity"""
    if len(embeddings) < 3:
        return 0.0

    angles = []
    for i in range(1, len(embeddings) - 1):
        v1 = embeddings[i] - embeddings[i-1]
        v2 = embeddings[i+1] - embeddings[i]

        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
        angles.append(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    cumulative_angle = np.sum(angles)
    euclidean = np.linalg.norm(embeddings[-1] - embeddings[0])

    return cumulative_angle / euclidean if euclidean > 0 else 0.0

def score_metrical_deviation(line_text):
    """
    Score deviation from perfect iambic pentameter.
    Returns: (deviation_score, ideal_pattern, actual_pattern)
    """
    try:
        parsed = p.Text(line_text).parse()

        if not parsed or len(parsed) == 0:
            return 0.0, None, None

        # Get best parse (first parse from first ParseList)
        best_parse = parsed[0][0]

        # Extract stress pattern using stress_ints
        if not best_parse.stress_ints:
            return 0.0, None, None

        actual_pattern = list(best_parse.stress_ints)

        # Ideal iambic pentameter: 0 1 0 1 0 1 0 1 0 1
        ideal_pattern = [0, 1] * 5

        # Calculate deviation (number of mismatches)
        min_len = min(len(actual_pattern), len(ideal_pattern))
        deviations = sum(1 for i in range(min_len) if actual_pattern[i] != ideal_pattern[i])

        # Add penalty for wrong syllable count
        length_penalty = abs(len(actual_pattern) - 10)

        total_deviation = deviations + length_penalty

        return total_deviation, ideal_pattern, actual_pattern
    except:
        return 0.0, None, None

def get_rhyme_scheme_position(line_num):
    """
    Returns rhyme scheme letter for sonnet line (1-indexed).
    ABAB CDCD EFEF GG
    """
    rhyme_scheme = {
        1: 'A', 2: 'B', 3: 'A', 4: 'B',
        5: 'C', 6: 'D', 7: 'C', 8: 'D',
        9: 'E', 10: 'F', 11: 'E', 12: 'F',
        13: 'G', 14: 'G'
    }
    return rhyme_scheme.get(line_num, 'X')

def is_rhyme_position(word_idx, words_in_line, line_num):
    """
    Check if this word is in rhyme position (last word of line).
    Also return rhyme scheme slot.
    """
    is_last = (word_idx == len(words_in_line) - 1)
    rhyme_slot = get_rhyme_scheme_position(line_num) if is_last else None
    return is_last, rhyme_slot

def encode_enhanced_prosodic_vector(stress, position_in_line, line_num,
                                     metrical_deviation, is_rhyme_word, rhyme_slot):
    """
    Create enhanced prosodic feature vector:
    - stress: 0 (unstressed) or 1 (stressed)
    - position_in_line: normalized 0-1
    - line_num: which line in sonnet (1-14)
    - metrical_deviation: deviation score for this line
    - is_rhyme_word: 1 if word is in rhyme position, 0 otherwise
    - rhyme_slot: one-hot for ABCDEFG (7 dimensions)
    """
    # Stanza encoding: [Q1, Q2, Q3, Couplet]
    if line_num <= 4:
        stanza_vec = [1, 0, 0, 0]
    elif line_num <= 8:
        stanza_vec = [0, 1, 0, 0]
    elif line_num <= 12:
        stanza_vec = [0, 0, 1, 0]
    else:
        stanza_vec = [0, 0, 0, 1]

    # Rhyme slot encoding (one-hot for A, B, C, D, E, F, G)
    rhyme_encoding = [0] * 7
    if rhyme_slot:
        rhyme_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}
        if rhyme_slot in rhyme_map:
            rhyme_encoding[rhyme_map[rhyme_slot]] = 1

    # Combine all features
    return np.array([
        stress,                      # 1 dim
        position_in_line,            # 1 dim
        line_num / 14.0,            # 1 dim (normalized)
        metrical_deviation / 10.0,  # 1 dim (normalized)
        float(is_rhyme_word)        # 1 dim
    ] + stanza_vec + rhyme_encoding)  # 4 + 7 = 11 dims
    # Total: 16 dimensions

# Analyze all sonnets with enhanced Layer 3
print("Analyzing all 154 sonnets with enhanced Layer 3 (meter + rhyme)...")
results = []

for sonnet in sonnets:
    num = sonnet['sonnet_number']

    if num % 20 == 0:
        print(f"  Processed {num} sonnets...")

    # First pass: calculate metrical deviations for all lines
    line_deviations = []
    for line in sonnet['lines']:
        deviation, _, _ = score_metrical_deviation(line)
        line_deviations.append(deviation)

    # Second pass: collect words, semantic embeddings, and enhanced prosodic features
    words = []
    semantic_embeddings = []
    enhanced_prosodic_vectors = []
    word_is_rhyme = []  # Track which words are in rhyme positions

    for line_idx, line in enumerate(sonnet['lines']):
        line_num = line_idx + 1
        line_words = tokenize_simple(line)
        metrical_deviation = line_deviations[line_idx]

        word_idx_in_line = 0
        for word in line_words:
            if word not in kv:
                continue

            words.append(word)
            semantic_embeddings.append(kv[word])

            # Check if this is a rhyme word
            is_last_word, rhyme_slot = is_rhyme_position(word_idx_in_line, line_words, line_num)
            word_is_rhyme.append(is_last_word)

            # Get stress (simplified: assume first syllable stress)
            try:
                parsed = p.Text(word).parse()
                if parsed and len(parsed) > 0 and parsed[0] and len(parsed[0]) > 0:
                    best = parsed[0][0]
                    if best.stress_ints and len(best.stress_ints) > 0:
                        stress = best.stress_ints[0]  # First syllable
                    else:
                        stress = 0
                else:
                    stress = 0
            except:
                stress = 0

            position_in_line = word_idx_in_line / max(len(line_words), 1)

            prosodic_vec = encode_enhanced_prosodic_vector(
                stress, position_in_line, line_num,
                metrical_deviation, is_last_word, rhyme_slot
            )
            enhanced_prosodic_vectors.append(prosodic_vec)

            word_idx_in_line += 1

    if len(semantic_embeddings) < 3:
        continue

    semantic_embeddings = np.array(semantic_embeddings)
    enhanced_prosodic_vectors = np.array(enhanced_prosodic_vectors)

    # Calculate semantic-only tortuosity (Layer 1)
    semantic_only_tort = calculate_tortuosity(semantic_embeddings)

    # Calculate enhanced prosody-conditioned tortuosity (Layer 3)
    enhanced_prosody_augmented = np.concatenate([semantic_embeddings, enhanced_prosodic_vectors], axis=1)
    enhanced_prosody_tort = calculate_tortuosity(enhanced_prosody_augmented)

    # Analyze tortuosity approaching rhyme words vs. non-rhyme words
    rhyme_word_indices = [i for i, is_rhyme in enumerate(word_is_rhyme) if is_rhyme]

    # Calculate average tortuosity in 2-word windows before rhyme words
    rhyme_approach_angles = []
    for rhyme_idx in rhyme_word_indices:
        if rhyme_idx >= 2:  # Need at least 2 words before
            # Get angle at position just before rhyme word
            i = rhyme_idx - 1
            if i > 0:
                v1 = semantic_embeddings[i] - semantic_embeddings[i-1]
                v2 = semantic_embeddings[i+1] - semantic_embeddings[i]
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
                angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
                rhyme_approach_angles.append(angle)

    # Calculate average metrical deviation
    avg_metrical_deviation = np.mean(line_deviations)

    # Calculate difference
    difference = enhanced_prosody_tort - semantic_only_tort
    percent_change = (difference / semantic_only_tort * 100) if semantic_only_tort > 0 else 0

    results.append({
        'sonnet': num,
        'semantic_only_tortuosity': semantic_only_tort,
        'enhanced_prosody_tortuosity': enhanced_prosody_tort,
        'difference': difference,
        'percent_change': percent_change,
        'avg_metrical_deviation': avg_metrical_deviation,
        'rhyme_approach_mean_angle': np.mean(rhyme_approach_angles) if rhyme_approach_angles else 0,
        'num_rhyme_words': len(rhyme_word_indices),
        'words_analyzed': len(words)
    })

print(f"\n✓ Analyzed {len(results)} sonnets\n")

# Create DataFrame
df = pd.DataFrame(results)

# Summary statistics
print("="*70)
print("ENHANCED LAYER 3 RESULTS (Meter + Rhyme)")
print("="*70)
print("\nSemantic-Only (Layer 1) Statistics:")
print(f"  Mean tortuosity: {df['semantic_only_tortuosity'].mean():.2f}")
print(f"  Std dev: {df['semantic_only_tortuosity'].std():.2f}")

print("\nEnhanced Prosody-Conditioned (Layer 3) Statistics:")
print(f"  Mean tortuosity: {df['enhanced_prosody_tortuosity'].mean():.2f}")
print(f"  Std dev: {df['enhanced_prosody_tortuosity'].std():.2f}")

print("\nDifference (Enhanced Layer 3 - Layer 1):")
print(f"  Mean difference: {df['difference'].mean():.2f}")
print(f"  Mean percent change: {df['percent_change'].mean():.2f}%")
print(f"  Std dev of difference: {df['difference'].std():.2f}")

print("\nMetrical Analysis:")
print(f"  Mean metrical deviation: {df['avg_metrical_deviation'].mean():.2f} syllables per line")
print(f"  Std dev: {df['avg_metrical_deviation'].std():.2f}")

print("\nRhyme Constraint Analysis:")
print(f"  Mean angle approaching rhyme words: {df['rhyme_approach_mean_angle'].mean():.4f} radians")
print(f"  Std dev: {df['rhyme_approach_mean_angle'].std():.4f}")

# Correlation between metrical deviation and tortuosity
correlation_meter = df['avg_metrical_deviation'].corr(df['semantic_only_tortuosity'])
print(f"\nCorrelation (metrical deviation ↔ semantic tortuosity): {correlation_meter:.4f}")

# By sequence
print("\n" + "="*70)
print("COMPARISON BY SEQUENCE")
print("="*70)

procreation = df[df['sonnet'] <= 17]
fair_youth = df[(df['sonnet'] >= 18) & (df['sonnet'] <= 126)]
dark_lady = df[df['sonnet'] >= 127]

if len(procreation) > 0:
    print(f"\nProcreation Sonnets (n={len(procreation)}):")
    print(f"  Semantic-only mean: {procreation['semantic_only_tortuosity'].mean():.2f}")
    print(f"  Enhanced prosody mean: {procreation['enhanced_prosody_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {procreation['difference'].mean():.2f} ({procreation['percent_change'].mean():.2f}%)")
    print(f"  Avg metrical deviation: {procreation['avg_metrical_deviation'].mean():.2f}")

if len(fair_youth) > 0:
    print(f"\nFair Youth Sonnets (n={len(fair_youth)}):")
    print(f"  Semantic-only mean: {fair_youth['semantic_only_tortuosity'].mean():.2f}")
    print(f"  Enhanced prosody mean: {fair_youth['enhanced_prosody_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {fair_youth['difference'].mean():.2f} ({fair_youth['percent_change'].mean():.2f}%)")
    print(f"  Avg metrical deviation: {fair_youth['avg_metrical_deviation'].mean():.2f}")

if len(dark_lady) > 0:
    print(f"\nDark Lady Sonnets (n={len(dark_lady)}):")
    print(f"  Semantic-only mean: {dark_lady['semantic_only_tortuosity'].mean():.2f}")
    print(f"  Enhanced prosody mean: {dark_lady['enhanced_prosody_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {dark_lady['difference'].mean():.2f} ({dark_lady['percent_change'].mean():.2f}%)")
    print(f"  Avg metrical deviation: {dark_lady['avg_metrical_deviation'].mean():.2f}")

# Save results
output_path = Path("/Users/justin/Repos/AI Project/results/shakespeare_sonnets_layer3_enhanced.csv")
df.to_csv(output_path, index=False)
print(f"\n✓ Results saved to {output_path}")
