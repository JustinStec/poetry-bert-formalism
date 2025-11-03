#!/usr/bin/env python3
"""
Layer 3 Proof-of-Concept: Prosody-Conditioned Semantic Trajectory Analysis
Compares semantic-only tortuosity vs. prosody-augmented tortuosity
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

def extract_prosodic_features(line_text, line_num_in_sonnet):
    """
    Extract prosodic features for each word in a line.
    Returns list of prosodic feature vectors.
    """
    # Parse line with prosodic
    try:
        parsed = p.Text(line_text).parse()

        # Get stress patterns from first parse
        if not parsed or len(parsed) == 0:
            return None

        # Extract syllables and their stresses
        syllables = []
        for parse in parsed[:1]:  # Use first parse
            for word in parse.words():
                for syll in word.syllables():
                    syllables.append({
                        'text': syll.text,
                        'stress': 1 if syll.is_stressed else 0
                    })

        return syllables
    except:
        return None

def encode_prosodic_vector(stress, position_in_line, line_in_stanza):
    """
    Create prosodic feature vector:
    - stress: 0 (unstressed) or 1 (stressed)
    - position_in_line: normalized 0-1 (where in the line)
    - line_in_stanza: one-hot for quatrain/couplet position
    """
    # Stanza encoding: [Q1, Q2, Q3, Couplet]
    if line_in_stanza <= 4:
        stanza_vec = [1, 0, 0, 0]  # Quatrain 1
    elif line_in_stanza <= 8:
        stanza_vec = [0, 1, 0, 0]  # Quatrain 2
    elif line_in_stanza <= 12:
        stanza_vec = [0, 0, 1, 0]  # Quatrain 3
    else:
        stanza_vec = [0, 0, 0, 1]  # Couplet

    return np.array([stress, position_in_line] + stanza_vec)

# Analyze all sonnets with Layer 3 prosodic conditioning
print("Analyzing all 154 sonnets with Layer 3 prosodic conditioning...")
results = []

for sonnet in sonnets:
    num = sonnet['sonnet_number']

    if num % 20 == 0:
        print(f"  Processed {num} sonnets...")

    # Collect words, semantic embeddings, and prosodic features
    words = []
    semantic_embeddings = []
    prosodic_vectors = []

    for line_idx, line in enumerate(sonnet['lines']):
        line_num = line_idx + 1

        # Extract prosodic features
        prosodic_data = extract_prosodic_features(line, line_num)

        # Tokenize for semantic embeddings
        line_words = tokenize_simple(line)

        # Match words to syllables (approximate)
        word_idx = 0
        syll_idx = 0

        for word in line_words:
            if word not in kv:
                continue

            words.append(word)
            semantic_embeddings.append(kv[word])

            # Estimate prosodic features for this word
            # (simplified: use stress of first syllable, position in line)
            if prosodic_data and syll_idx < len(prosodic_data):
                stress = prosodic_data[syll_idx]['stress']
            else:
                stress = 0  # Default unstressed if parsing failed

            position_in_line = word_idx / max(len(line_words), 1)
            prosodic_vec = encode_prosodic_vector(stress, position_in_line, line_num)
            prosodic_vectors.append(prosodic_vec)

            word_idx += 1
            syll_idx += 1

    if len(semantic_embeddings) < 3:
        continue

    semantic_embeddings = np.array(semantic_embeddings)
    prosodic_vectors = np.array(prosodic_vectors)

    # Calculate semantic-only tortuosity (Layer 1)
    semantic_only_tort = calculate_tortuosity(semantic_embeddings)

    # Calculate prosody-conditioned tortuosity (Layer 3)
    # Concatenate semantic + prosodic features
    prosody_augmented = np.concatenate([semantic_embeddings, prosodic_vectors], axis=1)
    prosody_conditioned_tort = calculate_tortuosity(prosody_augmented)

    # Calculate difference
    difference = prosody_conditioned_tort - semantic_only_tort
    percent_change = (difference / semantic_only_tort * 100) if semantic_only_tort > 0 else 0

    results.append({
        'sonnet': num,
        'semantic_only_tortuosity': semantic_only_tort,
        'prosody_conditioned_tortuosity': prosody_conditioned_tort,
        'difference': difference,
        'percent_change': percent_change,
        'words_analyzed': len(words)
    })

print(f"\n✓ Analyzed {len(results)} sonnets\n")

# Create DataFrame
df = pd.DataFrame(results)

# Summary statistics
print("="*70)
print("LAYER 3 PROOF-OF-CONCEPT RESULTS")
print("="*70)
print("\nSemantic-Only (Layer 1) Statistics:")
print(f"  Mean tortuosity: {df['semantic_only_tortuosity'].mean():.2f}")
print(f"  Std dev: {df['semantic_only_tortuosity'].std():.2f}")

print("\nProsody-Conditioned (Layer 3) Statistics:")
print(f"  Mean tortuosity: {df['prosody_conditioned_tortuosity'].mean():.2f}")
print(f"  Std dev: {df['prosody_conditioned_tortuosity'].std():.2f}")

print("\nDifference (Layer 3 - Layer 1):")
print(f"  Mean difference: {df['difference'].mean():.2f}")
print(f"  Mean percent change: {df['percent_change'].mean():.2f}%")
print(f"  Std dev of difference: {df['difference'].std():.2f}")

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
    print(f"  Prosody-conditioned mean: {procreation['prosody_conditioned_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {procreation['difference'].mean():.2f} ({procreation['percent_change'].mean():.2f}%)")

if len(fair_youth) > 0:
    print(f"\nFair Youth Sonnets (n={len(fair_youth)}):")
    print(f"  Semantic-only mean: {fair_youth['semantic_only_tortuosity'].mean():.2f}")
    print(f"  Prosody-conditioned mean: {fair_youth['prosody_conditioned_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {fair_youth['difference'].mean():.2f} ({fair_youth['percent_change'].mean():.2f}%)")

if len(dark_lady) > 0:
    print(f"\nDark Lady Sonnets (n={len(dark_lady)}):")
    print(f"  Semantic-only mean: {dark_lady['semantic_only_tortuosity'].mean():.2f}")
    print(f"  Prosody-conditioned mean: {dark_lady['prosody_conditioned_tortuosity'].mean():.2f}")
    print(f"  Mean difference: {dark_lady['difference'].mean():.2f} ({dark_lady['percent_change'].mean():.2f}%)")

# Detailed results table
print("\n" + "="*70)
print("DETAILED RESULTS")
print("="*70)
print(df.to_string(index=False))

# Save results
output_path = Path("/Users/justin/Repos/AI Project/results/shakespeare_sonnets_layer3_full.csv")
df.to_csv(output_path, index=False)
print(f"\n✓ Results saved to {output_path}")
