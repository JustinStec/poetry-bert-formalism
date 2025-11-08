#!/usr/bin/env python3
"""
Review samples from non-English detection to verify accuracy.
Takes stratified samples from each language for manual review.
"""

import os
import json
import random
from pathlib import Path
from collections import defaultdict

# Paths
BASE_DIR = Path('/Users/justin/Repos/AI Project')
POETRY_PLATFORM_DIR = BASE_DIR / 'Data/poetry_platform_renamed'
GUTENBERG_DIR = BASE_DIR / 'Data/Corpora/Gutenberg/By_Author'
NON_ENGLISH_LIST = BASE_DIR / 'scripts/non_english_redux_list.txt'
SAMPLES_DIR = BASE_DIR / 'scripts/non_english_samples'

def load_non_english_files():
    """Load the list of detected non-English files."""
    files_by_language = defaultdict(list)

    with open(NON_ENGLISH_LIST, 'r', encoding='utf-8') as f:
        current_file = None
        current_lang = None

        for line in f:
            line = line.strip()

            # Match numbered entries like "1. filename.txt"
            if line and line[0].isdigit() and '. ' in line:
                # Extract filename (after the number and ". ")
                filename = line.split('. ', 1)[1]
                current_file = filename
            elif line.startswith('Language:'):
                current_lang = line.split(':', 1)[1].strip()
                if current_file and current_lang:
                    files_by_language[current_lang].append(current_file)

    return files_by_language

def find_file(filename):
    """Find the actual file path by searching in both corpus directories."""
    # Extract author from filename (format: ID_Title_Author_Date.txt)
    parts = filename.rsplit('_', 2)
    if len(parts) >= 2:
        author = parts[-2]

        # Try poetry platform directory
        pp_path = POETRY_PLATFORM_DIR / author / filename
        if pp_path.exists():
            return pp_path

        # Try Gutenberg directory
        gb_path = GUTENBERG_DIR / author / filename
        if gb_path.exists():
            return gb_path

    return None

def get_file_preview(filename, num_words=200):
    """Get first N words of a file for preview."""
    filepath = find_file(filename)

    if not filepath:
        return "[FILE NOT FOUND]"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            words = content.split()[:num_words]
            return ' '.join(words)
    except Exception as e:
        return f"[ERROR reading file: {e}]"

def create_samples(files_by_language, samples_per_language=20):
    """Create sample files for manual review."""
    # Create samples directory
    SAMPLES_DIR.mkdir(exist_ok=True)

    results = {}

    for language, files in files_by_language.items():
        print(f"\n{language.upper()}: {len(files)} files detected")

        # Take random sample
        sample_size = min(samples_per_language, len(files))
        sample_files = random.sample(files, sample_size)

        # Create sample report
        sample_report = []
        sample_report.append(f"# {language.upper()} SAMPLES")
        sample_report.append(f"Total detected: {len(files)}")
        sample_report.append(f"Sample size: {sample_size}")
        sample_report.append("=" * 80)
        sample_report.append("")

        for i, filename in enumerate(sample_files, 1):
            sample_report.append(f"\n## SAMPLE {i}/{sample_size}")
            sample_report.append(f"File: {filename}")
            sample_report.append("-" * 80)

            preview = get_file_preview(filename, num_words=200)
            sample_report.append(preview)

            sample_report.append("-" * 80)

        # Write sample report
        output_file = SAMPLES_DIR / f'{language}_samples.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sample_report))

        print(f"  → Created sample report: {output_file}")
        results[language] = {
            'total': len(files),
            'sampled': sample_size,
            'report': str(output_file)
        }

    return results

def create_summary(results):
    """Create a summary report."""
    summary = []
    summary.append("# NON-ENGLISH DETECTION SAMPLE REVIEW")
    summary.append("")
    summary.append("## SUMMARY")
    summary.append("")

    total_files = sum(r['total'] for r in results.values())
    total_sampled = sum(r['sampled'] for r in results.values())

    summary.append(f"Total files detected: {total_files}")
    summary.append(f"Total samples created: {total_sampled}")
    summary.append("")
    summary.append("## BY LANGUAGE")
    summary.append("")

    for language, data in sorted(results.items(), key=lambda x: x[1]['total'], reverse=True):
        summary.append(f"- {language}: {data['total']} files ({data['sampled']} sampled)")

    summary.append("")
    summary.append("## REVIEW INSTRUCTIONS")
    summary.append("")
    summary.append("1. Check each language's sample file in non_english_samples/")
    summary.append("2. For each sample, determine if it is:")
    summary.append("   - TRUE POSITIVE: Actually non-English (should be removed)")
    summary.append("   - FALSE POSITIVE: English with some foreign words (should be kept)")
    summary.append("3. Pay special attention to German samples (highest count)")
    summary.append("4. If false positive rate is high (>20%), may need to adjust detection")
    summary.append("")
    summary.append("## SAMPLE FILES")
    summary.append("")

    for language, data in sorted(results.items()):
        summary.append(f"- {data['report']}")

    # Write summary
    summary_file = SAMPLES_DIR / 'REVIEW_SUMMARY.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary))

    print(f"\nSummary report: {summary_file}")
    return summary_file

def main():
    print("Loading non-English detection results...")
    files_by_language = load_non_english_files()

    print(f"\nFound {len(files_by_language)} languages")

    print("\nCreating sample files for review...")
    results = create_samples(files_by_language, samples_per_language=20)

    print("\nCreating summary report...")
    summary_file = create_summary(results)

    print("\n" + "=" * 80)
    print("SAMPLE REVIEW COMPLETE")
    print("=" * 80)
    print(f"\nReview the sample files in: {SAMPLES_DIR}")
    print(f"Start with the summary: {summary_file}")
    print("\nPay special attention to German samples (highest count)")

if __name__ == '__main__':
    main()
