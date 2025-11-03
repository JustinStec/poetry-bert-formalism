#!/usr/bin/env python3
"""
Debug metrical deviation scoring
"""
import prosodic as p

def score_metrical_deviation(line_text):
    """
    Score deviation from perfect iambic pentameter.
    Returns: (deviation_score, ideal_pattern, actual_pattern)
    """
    try:
        parsed = p.Text(line_text).parse()

        print(f"\nLine: {line_text}")
        print(f"  Parsed: {parsed}")
        print(f"  Number of parses: {len(parsed) if parsed else 0}")

        if not parsed or len(parsed) == 0:
            print("  → No parse returned")
            return 0.0, None, None

        # Get best parse (first parse from first ParseList)
        best_parse = parsed[0][0]  # ParseList -> Parse
        print(f"  Best parse: {best_parse}")

        # Extract stress pattern
        actual_pattern = []
        for word in best_parse.words:  # words is a property, not a method
            print(f"    Word: {word.text}")
            for syll in word.syllables:  # syllables is also a property
                stress_val = 1 if syll.is_stressed else 0
                actual_pattern.append(stress_val)
                print(f"      Syllable: {syll.text}, stressed: {syll.is_stressed}, value: {stress_val}")

        print(f"  Actual pattern: {actual_pattern}")

        # Ideal iambic pentameter: 0 1 0 1 0 1 0 1 0 1
        ideal_pattern = [0, 1] * 5
        print(f"  Ideal pattern:  {ideal_pattern}")

        # Calculate deviation (number of mismatches)
        min_len = min(len(actual_pattern), len(ideal_pattern))
        deviations = sum(1 for i in range(min_len) if actual_pattern[i] != ideal_pattern[i])
        print(f"  Mismatches in first {min_len} syllables: {deviations}")

        # Add penalty for wrong syllable count
        length_penalty = abs(len(actual_pattern) - 10)
        print(f"  Length penalty (|{len(actual_pattern)} - 10|): {length_penalty}")

        total_deviation = deviations + length_penalty
        print(f"  Total deviation: {total_deviation}")

        return total_deviation, ideal_pattern, actual_pattern
    except Exception as e:
        print(f"  → Exception: {e}")
        import traceback
        traceback.print_exc()
        return 0.0, None, None

# Test on Shakespeare sonnet lines
test_lines = [
    "Shall I compare thee to a summer's day?",  # Perfect iambic pentameter
    "Thou art more lovely and more temperate:",  # Perfect
    "Rough winds do shake the darling buds of May,",  # Trochaic start (violation)
    "Tired with all these, for restful death I cry",  # (Sonnet 66)
    "When in disgrace with fortune and men's eyes",  # Perfect
]

print("="*70)
print("TESTING METRICAL DEVIATION SCORING")
print("="*70)

for line in test_lines:
    deviation, ideal, actual = score_metrical_deviation(line)
    print(f"\n→ Final score: {deviation}")
    print("-"*70)
