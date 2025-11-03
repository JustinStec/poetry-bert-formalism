#!/usr/bin/env python3
"""
Analyze all 154 Shakespeare sonnets for trajectory tortuosity
"""
import numpy as np
import json
from gensim.models import KeyedVectors
from pathlib import Path
import pandas as pd

# Load EEBO embeddings
print("Loading EEBO embeddings...")
kv_path = Path("/Users/justin/Repos/AI Project/Data/Historical_Embeddings/Aligned/eebo_1595-1700_aligned.kv")
kv = KeyedVectors.load(str(kv_path), mmap='r')
print(f"✓ Loaded {len(kv)} words\n")

# Load all sonnets
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

# Analyze all sonnets
results = []
missing_words_total = 0
words_found_total = 0

print("Analyzing sonnets...")
for sonnet in sonnets:
    num = sonnet['sonnet_number']

    # Get embeddings for all words
    words = []
    embeddings = []
    missing_count = 0

    for line in sonnet['lines']:
        line_words = tokenize_simple(line)
        for word in line_words:
            if word in kv:
                words.append(word)
                embeddings.append(kv[word])
                words_found_total += 1
            else:
                missing_count += 1
                missing_words_total += 1

    if len(embeddings) < 3:
        continue

    embeddings = np.array(embeddings)

    # Overall tortuosity
    overall_tort = calculate_tortuosity(embeddings)

    # Line-by-line analysis
    line_boundaries = [0]
    for line in sonnet['lines']:
        line_words = tokenize_simple(line)
        found_in_line = sum(1 for w in line_words if w in kv)
        line_boundaries.append(line_boundaries[-1] + found_in_line)

    line_tortuosities = []
    for i in range(len(line_boundaries) - 1):
        start = line_boundaries[i]
        end = line_boundaries[i+1]
        if end - start >= 3:
            line_embeds = embeddings[start:end]
            line_tort = calculate_tortuosity(line_embeds)
            line_tortuosities.append(line_tort)

    # Couplet tortuosity (last 2 lines)
    couplet_start = line_boundaries[-3]
    couplet_embeds = embeddings[couplet_start:]
    couplet_tort = calculate_tortuosity(couplet_embeds) if len(couplet_embeds) >= 3 else 0.0

    results.append({
        'sonnet': num,
        'overall_tortuosity': overall_tort,
        'mean_line_tortuosity': np.mean(line_tortuosities) if line_tortuosities else 0.0,
        'max_line_tortuosity': np.max(line_tortuosities) if line_tortuosities else 0.0,
        'couplet_tortuosity': couplet_tort,
        'words_found': len(embeddings),
        'words_missing': missing_count
    })

    if num % 20 == 0:
        print(f"  Processed {num} sonnets...")

print(f"\n✓ Analyzed {len(results)} sonnets")
print(f"  Total words found: {words_found_total}")
print(f"  Total words missing: {missing_words_total}")
print(f"  Coverage: {words_found_total/(words_found_total+missing_words_total)*100:.1f}%\n")

# Create DataFrame
df = pd.DataFrame(results)

# Summary statistics
print("="*70)
print("OVERALL STATISTICS")
print("="*70)
print(f"Mean tortuosity: {df['overall_tortuosity'].mean():.2f}")
print(f"Median tortuosity: {df['overall_tortuosity'].median():.2f}")
print(f"Std dev: {df['overall_tortuosity'].std():.2f}")
print(f"Min: {df['overall_tortuosity'].min():.2f} (Sonnet {df.loc[df['overall_tortuosity'].idxmin(), 'sonnet']})")
print(f"Max: {df['overall_tortuosity'].max():.2f} (Sonnet {df.loc[df['overall_tortuosity'].idxmax(), 'sonnet']})")

# Compare sequences
print("\n" + "="*70)
print("COMPARISON BY SEQUENCE")
print("="*70)

procreation = df[df['sonnet'] <= 17]
fair_youth = df[(df['sonnet'] >= 18) & (df['sonnet'] <= 126)]
dark_lady = df[df['sonnet'] >= 127]

print(f"\nProcreation Sonnets (1-17):")
print(f"  Mean tortuosity: {procreation['overall_tortuosity'].mean():.2f}")
print(f"  Median: {procreation['overall_tortuosity'].median():.2f}")

print(f"\nFair Youth Sonnets (18-126):")
print(f"  Mean tortuosity: {fair_youth['overall_tortuosity'].mean():.2f}")
print(f"  Median: {fair_youth['overall_tortuosity'].median():.2f}")

print(f"\nDark Lady Sonnets (127-154):")
print(f"  Mean tortuosity: {dark_lady['overall_tortuosity'].mean():.2f}")
print(f"  Median: {dark_lady['overall_tortuosity'].median():.2f}")

# Top 10 most tortuous
print("\n" + "="*70)
print("TOP 10 MOST SEMANTICALLY COMPLEX (Highest Tortuosity)")
print("="*70)
top10 = df.nlargest(10, 'overall_tortuosity')
for idx, row in top10.iterrows():
    print(f"  Sonnet {int(row['sonnet'])}: {row['overall_tortuosity']:.2f}")

# Save results
output_path = Path("/Users/justin/Repos/AI Project/results/shakespeare_sonnets_tortuosity.csv")
output_path.parent.mkdir(exist_ok=True)
df.to_csv(output_path, index=False)
print(f"\n✓ Results saved to {output_path}")
