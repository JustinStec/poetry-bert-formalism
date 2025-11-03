#!/usr/bin/env python3
"""
Extract prosodic features from poetry for BERT integration.
This shows what features Prosodic can provide for our custom BERT model.
"""

import prosodic as pr
import json

def extract_prosodic_features(line_text):
    """
    Extract all prosodic features from a line of poetry.

    Returns dict with:
    - meter_pattern: string like '-+-+-+-+-+' (w=weak/unstressed, s=strong/stressed)
    - stress_pattern: actual linguistic stress '---+---+-+'
    - syllables: list of syllable texts
    - syllable_stresses: list of 0/1 for each syllable
    - meter_values: list of 'w'/'s' for each position
    - score: how well line fits meter
    - num_viols: number of metrical violations
    """
    text = pr.Text(line_text)
    line = list(text.lines)[0]

    if not line.parses:
        return None

    # Get best parse
    parse = line.parses[0]
    attrs = parse.attrs

    # Extract position-level features
    syllables = []
    stress_values = []
    meter_values = []

    for position in parse.children:
        syllables.append(position.txt)
        # meter_val is 'w' (weak) or 's' (strong)
        meter_values.append(position.meter_val)

        # Convert to binary: s=1, w=0
        stress = 1 if position.meter_val == 's' else 0
        stress_values.append(stress)

    return {
        'text': line_text,
        'scansion': attrs['txt'],  # Text with stressed syllables capitalized
        'meter_pattern': attrs['meter'],  # '-+-+-+-+-+' format
        'stress_pattern': attrs['stress'],  # Actual linguistic stress
        'syllables': syllables,
        'syllable_count': len(syllables),
        'stress_values': stress_values,  # Binary 0/1
        'meter_values': meter_values,  # 'w'/'s'
        'score': attrs['score'],
        'num_violations': attrs['num_viols'],
        'num_parses': len(line.parses)
    }


print("="*80)
print("PROSODIC FEATURES FOR BERT INTEGRATION")
print("="*80)

# Test on various poetic lines
test_lines = [
    "Shall I compare thee to a summer's day?",  # Shakespeare sonnet
    "Death be not proud, though some have called thee",  # Donne
    "I wandered lonely as a cloud",  # Wordsworth
    "The woods are lovely, dark and deep",  # Frost
]

all_features = []

for line in test_lines:
    print(f"\n{'='*80}")
    print(f"LINE: {line}")
    print(f"{'='*80}")

    features = extract_prosodic_features(line)

    if features:
        all_features.append(features)

        print(f"\nScansion: {features['scansion']}")
        print(f"Meter pattern:  {features['meter_pattern']}")
        print(f"Stress pattern: {features['stress_pattern']}")
        print(f"\nSyllable breakdown:")
        for i, (syll, stress, meter) in enumerate(zip(
            features['syllables'],
            features['stress_values'],
            features['meter_values']
        )):
            stress_str = "STRONG" if stress == 1 else "weak"
            print(f"  {i+1}. '{syll}' - {stress_str} ({meter})")

        print(f"\nMetrics:")
        print(f"  Syllable count: {features['syllable_count']}")
        print(f"  Metrical score: {features['score']}")
        print(f"  Violations: {features['num_violations']}")
        print(f"  Alternative parses: {features['num_parses']}")

print(f"\n{'='*80}")
print("FEATURES FOR BERT EMBEDDING LAYERS")
print(f"{'='*80}")

print("""
For each syllable/token, we can add these embedding dimensions:

1. STRESS EMBEDDING (binary)
   - 0 = unstressed (weak)
   - 1 = stressed (strong)

2. METER POSITION EMBEDDING (categorical)
   - Position in metrical foot (1-2 for iambic, etc.)
   - Could encode as: foot_number, position_in_foot

3. LINE POSITION EMBEDDING (numerical)
   - Position in line (normalized 0-1)

4. METRICAL CONTEXT EMBEDDING
   - Meter type of line (iambic, trochaic, etc.)
   - Detected from pattern

These would be added to BERT's standard embeddings:
   token_emb + position_emb + STRESS_EMB + METER_POS_EMB + LINE_POS_EMB

Example for "Shall I compare thee to a summer's day?":
""")

if all_features:
    example = all_features[0]
    print(f"\nToken-level prosodic embeddings:")
    print(f"{'Token':<12} {'Stress':<8} {'Meter':<8} {'Line Pos':<10}")
    print("-" * 40)
    for i, (syll, stress, meter) in enumerate(zip(
        example['syllables'],
        example['stress_values'],
        example['meter_values']
    )):
        line_pos = i / len(example['syllables'])
        print(f"{syll:<12} {stress:<8} {meter:<8} {line_pos:<10.2f}")

print(f"\n{'='*80}")
print("NEXT STEPS FOR PROSODY-CONDITIONED BERT")
print(f"{'='*80}")
print("""
1. Annotate EEBO corpus (7.6GB) with prosodic features
   - Run Prosodic on each line
   - Save: stress_values, meter_values, line_positions

2. Modify BERT architecture
   - Add embedding layers for prosodic features
   - Concatenate with standard BERT embeddings

3. Custom tokenizer alignment
   - BERT tokenizes differently than Prosodic syllabifies
   - Need to align BERT WordPiece tokens with syllables
   - Strategy: assign each token the prosodic features of its syllable

4. Training objectives
   - Standard MLM (masked language modeling)
   - Prosody prediction task (predict stress pattern)
   - Multi-task learning improves both

Ready to implement!
""")
