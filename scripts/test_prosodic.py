#!/usr/bin/env python3
"""
Test Prosodic library on sample poems to see what features it extracts.
"""

import prosodic as pr

# Test on Shakespeare sonnet (from your corpus)
shakespeare_line = "Shall I compare thee to a summer's day?"

print("="*60)
print("TESTING PROSODIC ON SHAKESPEARE")
print("="*60)
print(f"Line: {shakespeare_line}\n")

# Parse the line
text = pr.Text(shakespeare_line)

# Get all parses
for line in text.lines:  # Changed from lines() to lines (property)
    print(f"Line text: {line.txt}")
    print(f"\nNumber of possible metrical parses: {len(line.parses)}")

    # Show best parse
    if line.parses:
        best_parse = line.parses[0]  # Get first (best) parse
        print(f"\nBest parse:")
        print(f"Meter: {best_parse.meter}")
        print(f"Stress pattern: {best_parse.str_stress()}")
        print(f"Scansion: {best_parse}")

        # Get syllables with stress
        print(f"\nSyllable breakdown:")
        for word in best_parse.words():
            print(f"  Word: '{word.txt}'")
            for syll in word.syllables():
                stress = "STRESSED" if syll.stress == 1 else "UNSTRESSED"
                print(f"    Syllable: '{syll.txt}' - {stress}")

print("\n" + "="*60)
print("TESTING ON DONNE")
print("="*60)

# Test on Donne (metaphysical poetry, more complex meter)
donne_line = "Death be not proud, though some have called thee"
text2 = pr.Text(donne_line)

for line in text2.lines:  # Fixed
    print(f"Line: {line.txt}\n")
    if line.parses:
        best = line.parses[0]  # Fixed
        print(f"Meter: {best.meter}")
        print(f"Stress: {best.str_stress()}")  # Fixed
        print(f"Scansion: {best}")

print("\n" + "="*60)
print("EXTRACTING FEATURES FOR BERT")
print("="*60)

# Show what features we can extract for BERT embedding
test_line = pr.Text("Shall I compare thee to a summer's day?")
for line in test_line.lines:  # Fixed
    if line.parses:
        parse = line.parses[0]  # Fixed

        # Extract features we could add to BERT
        print("Features for BERT integration:")
        print(f"1. Meter type: {parse.meter}")
        print(f"2. Stress pattern: {parse.str_stress()}")  # Fixed

        # Syllable-level features
        syllables = []
        stresses = []
        for word in parse.words():
            for syll in word.syllables():
                syllables.append(syll.txt)
                stresses.append(syll.stress)

        print(f"3. Syllables: {syllables}")
        print(f"4. Stress values (0=unstressed, 1=stressed): {stresses}")
        print(f"5. Line position markers: {list(range(len(syllables)))}")

        # Phonetic features
        print(f"\n6. Phonetic transcription:")
        for word in parse.words():
            for syll in word.syllables():
                print(f"   '{syll.txt}' -> {syll.phonemes()}")

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
print("Prosodic can extract:")
print("  - Stress patterns (binary: stressed/unstressed)")
print("  - Meter type (iambic, trochaic, etc.)")
print("  - Syllable boundaries")
print("  - Phonetic transcriptions")
print("  - Line position information")
print("\nThese can be added as embeddings to BERT!")
