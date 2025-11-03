#!/usr/bin/env python3
"""
Test extracting stress pattern directly
"""
import prosodic as p

lines = [
    "Shall I compare thee to a summer's day?",
    "Thou art more lovely and more temperate:",
    "Rough winds do shake the darling buds of May,",
    "Tired with all these, for restful death I cry",
]

for line in lines:
    parsed = p.Text(line).parse()
    best_parse = parsed[0][0]

    print(f"\nLine: {line}")
    print(f"  txt: {best_parse.txt}")
    print(f"  stress_str: {best_parse.stress_str}")
    print(f"  stress_ints: {best_parse.stress_ints}")
    print(f"  meter_str: {best_parse.meter_str}")
    print(f"  meter_ints: {best_parse.meter_ints}")

    # Convert stress_ints to pattern
    if best_parse.stress_ints:
        stress_pattern = list(best_parse.stress_ints)
        print(f"  Stress pattern: {stress_pattern}")

        # Ideal iambic pentameter
        ideal = [0, 1] * 5
        print(f"  Ideal pattern:  {ideal}")

        # Calculate deviation
        min_len = min(len(stress_pattern), 10)
        deviations = sum(1 for i in range(min_len) if stress_pattern[i] != ideal[i])
        length_penalty = abs(len(stress_pattern) - 10)
        total = deviations + length_penalty

        print(f"  Deviations: {deviations}, Length penalty: {length_penalty}, Total: {total}")
