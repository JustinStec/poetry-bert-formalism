#!/usr/bin/env python3
"""
Simplified Prosodic test - extract features for BERT integration.
"""

import prosodic as pr

print("="*60)
print("PROSODIC FEATURE EXTRACTION FOR BERT")
print("="*60)

# Test line
line_text = "Shall I compare thee to a summer's day?"
print(f"\nTest line: {line_text}\n")

# Parse
text = pr.Text(line_text)
line = list(text.lines)[0]

print(f"Number of possible parses: {len(line.parses)}")

if line.parses:
    parse = line.parses[0]  # Best parse

    print(f"\n{'='*60}")
    print("PARSE OBJECT STRUCTURE:")
    print(f"{'='*60}")
    print(f"Parse type: {type(parse)}")
    print(f"Parse repr: {parse}")

    # Try to get words
    print(f"\n{'='*60}")
    print("WORD-LEVEL FEATURES:")
    print(f"{'='*60}")
    try:
        words = list(parse.words())
        for word in words:
            print(f"\nWord: '{word.txt}'")
            print(f"  Type: {type(word)}")

            # Try to get syllables
            try:
                syllables = list(word.syllables())
                for syll in syllables:
                    print(f"  Syllable: '{syll.txt}'")

                    # Check what attributes syllable has
                    print(f"    Attributes: {dir(syll)}")

                    # Try to get stress
                    if hasattr(syll, 'stress'):
                        print(f"    Stress: {syll.stress}")
                    if hasattr(syll, 'is_stressed'):
                        print(f"    Is stressed: {syll.is_stressed}")

            except Exception as e:
                print(f"  Error getting syllables: {e}")

    except Exception as e:
        print(f"Error getting words: {e}")

    # Try to get meter features
    print(f"\n{'='*60}")
    print("METER FEATURES:")
    print(f"{'='*60}")

    if hasattr(parse, 'meter'):
        print(f"Meter object: {parse.meter}")

    # Check all parse attributes
    print(f"\nAll parse attributes:")
    attrs = [attr for attr in dir(parse) if not attr.startswith('_')]
    for attr in attrs[:20]:  # First 20
        try:
            val = getattr(parse, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except:
            pass
