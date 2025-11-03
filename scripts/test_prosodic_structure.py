#!/usr/bin/env python3
"""
Inspect prosodic Parse structure
"""
import prosodic as p

line = "Shall I compare thee to a summer's day?"
parsed = p.Text(line).parse()

print(f"Line: {line}\n")
print(f"Type of parsed: {type(parsed)}")
print(f"Parsed: {parsed}\n")

best_parse = parsed[0][0]
print(f"Type of best_parse: {type(best_parse)}")
print(f"Best parse: {best_parse}\n")

print(f"Dir of best_parse:")
print([attr for attr in dir(best_parse) if not attr.startswith('_')])
print()

print(f"best_parse.words type: {type(best_parse.words)}")
print(f"best_parse.words: {best_parse.words}")
print(f"Length: {len(best_parse.words) if hasattr(best_parse.words, '__len__') else 'N/A'}")
print()

if best_parse.words:
    print("Iterating through words:")
    for i, word in enumerate(best_parse.words):
        print(f"  Word {i}: type={type(word)}, value={word}")
        print(f"    text: {word.text if hasattr(word, 'text') else 'N/A'}")
        print(f"    syllables type: {type(word.syllables) if hasattr(word, 'syllables') else 'N/A'}")

        if hasattr(word, 'syllables'):
            print(f"    syllables: {word.syllables}")
            for j, syll in enumerate(word.syllables):
                print(f"      Syll {j}: type={type(syll)}, value={syll}")
                print(f"        text: {syll.text if hasattr(syll, 'text') else 'N/A'}")
                print(f"        is_stressed: {syll.is_stressed if hasattr(syll, 'is_stressed') else 'N/A'}")
                print(f"        stress: {syll.stress if hasattr(syll, 'stress') else 'N/A'}")
