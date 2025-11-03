#!/usr/bin/env python3
"""
Quick tortuosity test on Shakespeare Sonnet 18
"""
import numpy as np
import json
from gensim.models import KeyedVectors
from pathlib import Path

# Load EEBO embeddings
print("Loading EEBO embeddings...")
kv_path = Path("/Users/justin/Repos/AI Project/Data/Historical_Embeddings/Aligned/eebo_1595-1700_aligned.kv")
kv = KeyedVectors.load(str(kv_path), mmap='r')
print(f"✓ Loaded {len(kv)} words\n")

# Sonnet 18
sonnet = {
    "number": 18,
    "lines": [
        "Shall I compare thee to a summer's day?",
        "Thou art more lovely and more temperate:",
        "Rough winds do shake the darling buds of May,",
        "And summer's lease hath all too short a date:",
        "Sometime too hot the eye of heaven shines,",
        "And often is his gold complexion dimm'd,",
        "And every fair from fair sometime declines,",
        "By chance, or nature's changing course untrimm'd:",
        "But thy eternal summer shall not fade,",
        "Nor lose possession of that fair thou ow'st,",
        "Nor shall death brag thou wander'st in his shade,",
        "When in eternal lines to time thou grow'st,",
        "So long as men can breathe, or eyes can see,",
        "So long lives this, and this gives life to thee."
    ]
}

# Extract words and get embeddings
words = []
embeddings = []
line_boundaries = [0]  # Track line breaks

for line in sonnet["lines"]:
    # Simple tokenization
    line_words = line.lower().replace("'", "").replace(",", "").replace(".", "").replace("?", "").replace(":", "").replace(";", "").split()

    for word in line_words:
        if word in kv:
            words.append(word)
            embeddings.append(kv[word])
        else:
            print(f"  [missing: {word}]")

    line_boundaries.append(len(words))

embeddings = np.array(embeddings)
print(f"Got embeddings for {len(embeddings)} words\n")

# Calculate tortuosity
angles = []
for i in range(1, len(embeddings) - 1):
    v1 = embeddings[i] - embeddings[i-1]
    v2 = embeddings[i+1] - embeddings[i]

    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
    angles.append(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

cumulative_angle = np.sum(angles)
euclidean = np.linalg.norm(embeddings[-1] - embeddings[0])
tortuosity = cumulative_angle / euclidean if euclidean > 0 else 0.0

print("="*60)
print(f"SONNET 18 TORTUOSITY ANALYSIS")
print("="*60)
print(f"Total words with embeddings: {len(embeddings)}")
print(f"Cumulative angle: {cumulative_angle:.2f} radians")
print(f"Euclidean distance: {euclidean:.4f}")
print(f"Tortuosity coefficient: {tortuosity:.4f}")
print("="*60)

# Line-by-line
print("\nLine-by-line tortuosity:")
for i in range(len(line_boundaries) - 1):
    start = line_boundaries[i]
    end = line_boundaries[i+1]

    if end - start < 3:
        continue

    line_embeds = embeddings[start:end]
    line_angles = []

    for j in range(1, len(line_embeds) - 1):
        v1 = line_embeds[j] - line_embeds[j-1]
        v2 = line_embeds[j+1] - line_embeds[j]
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
        line_angles.append(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    if line_angles:
        line_tort = np.sum(line_angles) / np.linalg.norm(line_embeds[-1] - line_embeds[0])
        print(f"  Line {i+1}: {line_tort:.2f}")

print("\n✓ Done!")
