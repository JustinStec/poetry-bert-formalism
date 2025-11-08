#!/usr/bin/env python3
"""
Conservative non-English detection - much stricter criteria to avoid false positives.
Requires multiple strong signals, not just isolated word matches.
"""

import re
import csv
from pathlib import Path
from collections import Counter

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
OUTPUT_DIR = Path("/Users/justin/Repos/AI Project/scripts")

# Much more conservative patterns - focus on distinctive multi-word phrases
# and words that don't commonly appear in English
PATTERNS = {
    'spanish': [
        r'\bel que\b', r'\bla que\b', r'\blos que\b', r'\blas que\b',
        r'\bpor el\b', r'\bpor la\b', r'\bpara el\b', r'\bpara la\b',
        r'\bdel que\b', r'\bdel cual\b', r'\bcuando el\b', r'\bcuando la\b',
        r'\btambién\b', r'\bdespués\b', r'\bporque\b', r'\bseñor\b', r'\bseñora\b',
        r'\bdonde\b.*\bque\b', r'\bcómo\b', r'\bquién\b', r'\bcuál\b',
        r'¿.*\?', r'¡.*!',  # Spanish punctuation
    ],
    'portuguese': [
        r'\bvocê\b', r'\btem que\b', r'\bpara o\b', r'\bpara a\b',
        r'\bdo que\b', r'\bda que\b', r'\bdos que\b', r'\bdas que\b',
        r'\bnão\b', r'\btambém\b', r'\bdepois\b', r'\bporque\b',
        r'\bmais\b.*\bque\b', r'\bonde\b.*\bque\b', r'\bquando\b.*\bque\b',
        r'[ãõ]', r'\bmuito\b', r'\bsenhor\b', r'\bsenhora\b',
    ],
    'french': [
        r'\ble que\b', r'\bla que\b', r'\bles que\b',
        r'\bde la\b', r'\bdu que\b', r'\bdes que\b',
        r'\bparce que\b', r'\baprès\b', r'\bavec\b.*\bque\b',
        r'\bmonsieur\b', r'\bmadame\b', r'\btrès\b', r'\bcomment\b',
        r'\bpourquoi\b', r'\bqu\'il\b', r'\bqu\'elle\b', r'\bc\'est\b',
        r'[àâäèéêëîïôùûü].*[àâäèéêëîïôùûü]',  # Multiple accents
    ],
    'german': [
        r'\bder der\b', r'\bdie die\b', r'\bdas das\b',
        r'\bund der\b', r'\bund die\b', r'\bund das\b',
        r'\bin der\b', r'\ban der\b', r'\bzur\b', r'\bzum\b',
        r'\bwarum\b', r'\bwelche\b', r'\bwelcher\b', r'\bwelches\b',
        r'\bdessen\b', r'\bderer\b', r'\bherr\b', r'\bfrau\b',
        r'[äöüß].*[äöüß]',  # Multiple umlauts
    ],
    'italian': [
        r'\bche il\b', r'\bche la\b', r'\bche lo\b',
        r'\bdel che\b', r'\bdella che\b', r'\bdello che\b',
        r'\bperché\b', r'\bdopo\b.*\bche\b', r'\bquando\b.*\bche\b',
        r'\bsignore\b', r'\bsignora\b', r'\bmolto\b.*\bche\b',
        r'\bchi\b.*\bche\b', r'\bquale\b.*\bche\b',
        r'[àèéìòù].*[àèéìòù]',  # Multiple accents
    ],
    'latin': [
        r'\bquod\b', r'\bqui\b.*\best\b', r'\bquae\b.*\best\b',
        r'\besse\b', r'\bsed\b.*\best\b', r'\betiam\b',
        r'\bdominus\b', r'\bdomina\b', r'\bmultum\b',
        r'\bquis\b.*\bquid\b', r'\bcur\b.*\best\b',
    ]
}

# Title patterns - strong indicator if title itself is in foreign language
TITLE_PATTERNS = {
    'spanish': [r'\b(el|la|los|las|del|al|con|por|para|desde|hasta)\b'],
    'portuguese': [r'\b(o|a|os|as|do|da|dos|das|ao|com|para|até)\b'],
    'french': [r'\b(le|la|les|des|du|avec|pour|dans|sur|sous)\b'],
    'german': [r'\b(der|die|das|den|dem|und|mit|für|von|zu)\b'],
    'italian': [r'\b(il|la|lo|i|gli|le|del|della|con|per|da)\b'],
    'latin': [r'\b(de|et|in|ad|cum|per|ex|ab)\b'],
}

def extract_title_from_filename(filename):
    """Extract title from filename format: ID_Title_Author_Date.txt"""
    parts = filename.rsplit('_', 2)
    if len(parts) >= 3:
        title_part = parts[0].split('_', 1)
        if len(title_part) > 1:
            return title_part[1].lower()
    return ""

def check_title_language(filename):
    """Check if title indicates a foreign language."""
    title = extract_title_from_filename(filename)
    if not title:
        return None

    # Count matches in title for each language
    language_scores = Counter()
    for language, patterns in TITLE_PATTERNS.items():
        for pattern in patterns:
            matches = len(re.findall(pattern, title, re.IGNORECASE))
            if matches >= 2:  # At least 2 foreign words in title
                language_scores[language] += matches

    if language_scores:
        top = language_scores.most_common(1)[0]
        if top[1] >= 2:
            return top[0]
    return None

def detect_non_english(filepath):
    """
    Conservative detection - requires multiple strong signals.

    Returns None if likely English, otherwise returns detected language info.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return None

    # Limit content to speed up processing
    content = content[:5000].lower()

    # Count matches for each language
    language_scores = Counter()

    for language, patterns in PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            language_scores[language] += len(matches)

    # Check title for additional evidence
    title_lang = check_title_language(filepath.name)
    if title_lang:
        language_scores[title_lang] += 5  # Boost if title is foreign

    # CONSERVATIVE THRESHOLD: Require at least 8 strong matches
    # (vs. 3 in the previous script)
    if language_scores:
        top_language = language_scores.most_common(1)[0]
        if top_language[1] >= 8:
            return {
                'primary_language': top_language[0],
                'match_count': top_language[1],
                'all_languages': dict(language_scores)
            }

    return None

def scan_directory(directory):
    """Scan a directory for non-English poems."""
    non_english_files = []

    print(f"Scanning {directory.name}...")

    # Walk through all author subdirectories
    for author_dir in sorted(directory.iterdir()):
        if not author_dir.is_dir():
            continue

        for filepath in author_dir.glob('*.txt'):
            result = detect_non_english(filepath)
            if result:
                non_english_files.append({
                    'filepath': filepath,
                    'relative_path': f"{author_dir.name}/{filepath.name}",
                    'language': result['primary_language'],
                    'matches': result['match_count']
                })

    return non_english_files

def main():
    print("=" * 80)
    print("CONSERVATIVE NON-ENGLISH DETECTION")
    print("=" * 80)
    print("\nThis uses much stricter criteria to avoid false positives:")
    print("- Multi-word phrases instead of single words")
    print("- Higher match threshold (8+ vs 3+)")
    print("- Distinctive patterns that don't match English")
    print()

    # Scan both directories
    all_non_english = []

    if POETRY_PLATFORM_DIR.exists():
        all_non_english.extend(scan_directory(POETRY_PLATFORM_DIR))

    if GUTENBERG_DIR.exists():
        all_non_english.extend(scan_directory(GUTENBERG_DIR))

    # Sort by language and matches
    all_non_english.sort(key=lambda x: (x['language'], -x['matches']))

    # Count by language
    language_counts = Counter(f['language'] for f in all_non_english)

    print(f"\n{'=' * 80}")
    print(f"RESULTS: Found {len(all_non_english)} non-English files")
    print(f"{'=' * 80}\n")

    for language, count in language_counts.most_common():
        print(f"{language}: {count} files")

    # Write detailed report
    report_file = OUTPUT_DIR / 'non_english_conservative_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Conservative Non-English Detection Results\n\n")
        f.write(f"Total files detected: **{len(all_non_english)}**\n\n")
        f.write(f"## By Language\n\n")

        for language, count in language_counts.most_common():
            f.write(f"- {language}: {count} files\n")

        f.write(f"\n## Comparison with Previous Detection\n\n")
        f.write(f"Previous aggressive detection: 25,999 files\n")
        f.write(f"Conservative detection: {len(all_non_english)} files\n")
        f.write(f"Reduction: {25999 - len(all_non_english)} files ({100 * (25999 - len(all_non_english)) / 25999:.1f}%)\n\n")

        f.write(f"\n## Top Matches by Language\n\n")

        for language in sorted(language_counts.keys()):
            f.write(f"\n### {language.upper()}\n\n")
            lang_files = [f for f in all_non_english if f['language'] == language]

            # Show top 20 strongest matches
            for i, file_info in enumerate(lang_files[:20], 1):
                f.write(f"{i}. {file_info['relative_path']}\n")
                f.write(f"   Matches: {file_info['matches']}\n\n")

    print(f"\nDetailed report written to: {report_file}")

    # Write list of files to remove
    list_file = OUTPUT_DIR / 'non_english_conservative_list.txt'
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write(f"Non-English Files (Conservative Detection) - {len(all_non_english)} files\n")
        f.write("=" * 100 + "\n\n")

        for i, file_info in enumerate(all_non_english, 1):
            f.write(f"{i}. {file_info['relative_path']}\n")
            f.write(f"   Language: {file_info['language']}\n")
            f.write(f"   Matches: {file_info['matches']}\n\n")

    print(f"File list written to: {list_file}")

    print(f"\n{'=' * 80}")
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. Review samples from the conservative list")
    print("2. If accuracy is good (>80% true positives), proceed with removal")
    print("3. If still too many false positives, increase threshold further")

if __name__ == '__main__':
    main()
