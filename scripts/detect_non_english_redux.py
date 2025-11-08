#!/usr/bin/env python3
"""
Second pass at detecting non-English poems that slipped through.
More aggressive detection this time.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
REPORT_FILE = Path("/Users/justin/Repos/AI Project/scripts/non_english_redux_report.md")

# More aggressive non-English patterns
PATTERNS = {
    'spanish': [
        r'\b(está|están|había|ser|hacer|pero|porque|también|después|más|año|día)\b',
        r'\b(señor|señora|muy|donde|cuando|cómo|qué|quién|cuál)\b',
        r'[áéíóúñ¿¡]',
    ],
    'portuguese': [
        r'\b(está|são|não|também|porque|depois|mais|onde|quando|como)\b',
        r'\b(senhor|senhora|muito|qual|quem|você|ele|ela)\b',
        r'[ãõâêôçáéíóú]',
    ],
    'french': [
        r'\b(est|sont|était|être|faire|mais|parce|aussi|après|plus|où|quand)\b',
        r'\b(monsieur|madame|très|comment|pourquoi|qui|que|quel)\b',
        r'[àâäçèéêëîïôùûü]',
    ],
    'german': [
        r'\b(ist|sind|war|waren|sein|machen|aber|weil|auch|nach|mehr|wo|wann|wie)\b',
        r'\b(herr|frau|sehr|warum|wer|was|welch)\b',
        r'[äöüß]',
    ],
    'italian': [
        r'\b(è|sono|era|essere|fare|ma|perché|anche|dopo|più|dove|quando|come)\b',
        r'\b(signore|signora|molto|chi|che|quale)\b',
        r'[àèéìòù]',
    ],
    'latin': [
        r'\b(est|sunt|erat|esse|sed|quia|etiam|post|ubi|quando|quomodo)\b',
        r'\b(dominus|domina|multum|cur|quis|quid|qui|quae|quod)\b',
    ]
}

def get_file_path(row):
    """Get full file path from metadata row."""
    filename = row['filename']

    if 'gutenberg' in filename.lower():
        for author_dir in GUTENBERG_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path
    else:
        author = row['author']
        filepath = POETRY_PLATFORM_DIR / author / filename
        if filepath.exists():
            return filepath

    return None

def detect_non_english(filepath):
    """Detect if file contains non-English content."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
    except:
        return None

    if len(content) < 50:
        return None

    detections = []
    language_scores = Counter()

    # Check each language
    for language, patterns in PATTERNS.items():
        matches = 0
        for pattern in patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            matches += len(found)

        if matches > 0:
            language_scores[language] = matches
            detections.append({
                'language': language,
                'matches': matches
            })

    # Flag if we have significant matches
    if language_scores:
        top_language = language_scores.most_common(1)[0]
        if top_language[1] >= 3:  # At least 3 matches
            return {
                'primary_language': top_language[0],
                'match_count': top_language[1],
                'all_languages': dict(language_scores)
            }

    return None

def scan_corpus():
    """Scan corpus for non-English content."""
    print("=" * 80)
    print("NON-ENGLISH DETECTION (SECOND PASS)")
    print("=" * 80)
    print("Detecting poems that slipped through first pass...")
    print("=" * 80)

    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    print("\nScanning for non-English content...")
    flagged = []
    language_counts = Counter()

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Scanned {i:,}/{len(rows):,}...")

        filepath = get_file_path(row)
        if not filepath:
            continue

        result = detect_non_english(filepath)
        if result:
            flagged.append({
                'filename': row['filename'],
                'title': row['title'],
                'author': row['author'],
                'filepath': filepath,
                **result
            })
            language_counts[result['primary_language']] += 1

    print(f"\n✓ Found {len(flagged):,} non-English files")

    # Statistics
    if language_counts:
        print(f"\nBy language:")
        for language, count in sorted(language_counts.items(), key=lambda x: -x[1]):
            print(f"  {language.capitalize()}: {count:,} files")

    return flagged, language_counts

def generate_report(flagged, language_counts):
    """Generate report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    # Sort by match count
    flagged_sorted = sorted(flagged, key=lambda x: -x['match_count'])

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Non-English Detection Report (Second Pass)\n\n")

        f.write("## Overview\n\n")
        f.write(f"- **Non-English files found:** {len(flagged):,}\n")
        f.write(f"- **Total corpus:** 167,215 files\n\n")

        f.write("## By Language\n\n")
        for language, count in sorted(language_counts.items(), key=lambda x: -x[1]):
            f.write(f"- **{language.capitalize()}:** {count:,} files\n")
        f.write("\n")

        # Group by language
        for language in sorted(language_counts.keys(), key=lambda x: -language_counts[x]):
            language_files = [item for item in flagged_sorted if item['primary_language'] == language]

            f.write(f"## {language.capitalize()} ({len(language_files):,} files)\n\n")

            for i, item in enumerate(language_files[:50], 1):
                f.write(f"### {i}. `{item['filename']}`\n\n")
                f.write(f"- **Title:** {item['title']}\n")
                f.write(f"- **Author:** {item['author']}\n")
                f.write(f"- **Matches:** {item['match_count']}\n\n")

            if len(language_files) > 50:
                f.write(f"\n... and {len(language_files) - 50} more files\n\n")

    print(f"✓ Report saved to: {REPORT_FILE}")

    # Save complete list
    list_file = Path("/Users/justin/Repos/AI Project/scripts/non_english_redux_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Non-English Files ({len(flagged):,} files)\n")
        f.write("=" * 100 + "\n\n")

        for i, item in enumerate(flagged_sorted, 1):
            f.write(f"{i}. {item['filename']}\n")
            f.write(f"   Title: {item['title']}\n")
            f.write(f"   Author: {item['author']}\n")
            f.write(f"   Language: {item['primary_language']}\n")
            f.write(f"   Matches: {item['match_count']}\n\n")

    print(f"✓ Complete list saved to: {list_file}")

def main():
    print("Non-English Detection (Second Pass)")
    print("Finding poems that slipped through\n")

    # Scan corpus
    flagged, language_counts = scan_corpus()

    if not flagged:
        print("\n✓ No non-English files found - corpus is clean!")
        return

    # Generate report
    generate_report(flagged, language_counts)

    print("\n" + "=" * 80)
    print("DETECTION COMPLETE")
    print("=" * 80)
    print(f"✓ Non-English files found: {len(flagged):,}")
    print(f"✓ Review report at: {REPORT_FILE}")

if __name__ == '__main__':
    main()
