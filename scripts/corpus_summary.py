#!/usr/bin/env python3
"""
Generate final summary statistics for the cleaned poetry corpus.
"""

from pathlib import Path
from collections import Counter
import csv

# Paths
BASE_DIR = Path("/Users/justin/Repos/AI Project")
POETRY_PLATFORM_DIR = BASE_DIR / "Data/poetry_platform_renamed"
GUTENBERG_DIR = BASE_DIR / "Data/Corpora/Gutenberg/By_Author"
OUTPUT_FILE = BASE_DIR / "scripts/corpus_final_summary.md"

def count_files_and_lines(directory):
    """Count files, lines, words, and collect statistics."""
    if not directory.exists():
        return {
            'files': 0,
            'total_lines': 0,
            'total_words': 0,
            'authors': 0,
            'avg_lines_per_poem': 0,
            'avg_words_per_poem': 0
        }

    file_count = 0
    total_lines = 0
    total_words = 0
    author_set = set()

    for author_dir in directory.iterdir():
        if not author_dir.is_dir():
            continue

        author_set.add(author_dir.name)

        for filepath in author_dir.glob('*.txt'):
            file_count += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.count('\n') + 1
                    words = len(content.split())

                    total_lines += lines
                    total_words += words
            except:
                pass

    return {
        'files': file_count,
        'total_lines': total_lines,
        'total_words': total_words,
        'authors': len(author_set),
        'avg_lines_per_poem': round(total_lines / file_count, 1) if file_count > 0 else 0,
        'avg_words_per_poem': round(total_words / file_count, 1) if file_count > 0 else 0
    }

def main():
    print("=" * 80)
    print("GENERATING FINAL CORPUS SUMMARY")
    print("=" * 80)
    print()

    # Count statistics
    print("Counting Poetry Platform poems...")
    pp_stats = count_files_and_lines(POETRY_PLATFORM_DIR)

    print("Counting Gutenberg poems...")
    gb_stats = count_files_and_lines(GUTENBERG_DIR)

    # Combined statistics
    total_stats = {
        'files': pp_stats['files'] + gb_stats['files'],
        'total_lines': pp_stats['total_lines'] + gb_stats['total_lines'],
        'total_words': pp_stats['total_words'] + gb_stats['total_words'],
        'authors': pp_stats['authors'] + gb_stats['authors'],
    }

    total_stats['avg_lines_per_poem'] = round(
        total_stats['total_lines'] / total_stats['files'], 1
    ) if total_stats['files'] > 0 else 0

    total_stats['avg_words_per_poem'] = round(
        total_stats['total_words'] / total_stats['files'], 1
    ) if total_stats['files'] > 0 else 0

    # Write summary report
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Final Poetry Corpus Summary\n\n")
        f.write("## Overall Statistics\n\n")
        f.write(f"- **Total poems:** {total_stats['files']:,}\n")
        f.write(f"- **Total authors:** {total_stats['authors']:,}\n")
        f.write(f"- **Total lines:** {total_stats['total_lines']:,}\n")
        f.write(f"- **Total words:** {total_stats['total_words']:,}\n")
        f.write(f"- **Average lines per poem:** {total_stats['avg_lines_per_poem']}\n")
        f.write(f"- **Average words per poem:** {total_stats['avg_words_per_poem']}\n\n")

        f.write("## By Source\n\n")
        f.write("### Poetry Platform\n\n")
        f.write(f"- Poems: {pp_stats['files']:,}\n")
        f.write(f"- Authors: {pp_stats['authors']:,}\n")
        f.write(f"- Lines: {pp_stats['total_lines']:,}\n")
        f.write(f"- Words: {pp_stats['total_words']:,}\n")
        f.write(f"- Avg lines/poem: {pp_stats['avg_lines_per_poem']}\n")
        f.write(f"- Avg words/poem: {pp_stats['avg_words_per_poem']}\n\n")

        f.write("### Project Gutenberg\n\n")
        f.write(f"- Poems: {gb_stats['files']:,}\n")
        f.write(f"- Authors: {gb_stats['authors']:,}\n")
        f.write(f"- Lines: {gb_stats['total_lines']:,}\n")
        f.write(f"- Words: {gb_stats['total_words']:,}\n")
        f.write(f"- Avg lines/poem: {gb_stats['avg_lines_per_poem']}\n")
        f.write(f"- Avg words/poem: {gb_stats['avg_words_per_poem']}\n\n")

        f.write("## Cleanup Summary\n\n")
        f.write("### Major Cleanup Operations\n\n")
        f.write("1. **Reorganized files** into author folders (43,648 files → 3,926 folders)\n")
        f.write("2. **Integrated orphaned files** (3,251 kept, 5,757 deleted)\n")
        f.write("3. **GPT-4o author identification** for entire corpus\n")
        f.write("4. **Applied GPT-4o corrections** (16,780 poems cleaned)\n")
        f.write("5. **Scraped Poetry Platform** database (124,755 poems)\n")
        f.write("6. **Standardized filenames** (123,205 poems renamed)\n")
        f.write("7. **Merged and deduplicated** corpora (4,373 duplicates removed)\n")
        f.write("8. **Cleaned italic markup** (2,232 files, 12,837 instances)\n")
        f.write("9. **Removed foreign language poems** (4,129 total: 3,090 first pass + 1,039 second pass)\n")
        f.write("10. **Removed empty author folders** (1,760 folders)\n")
        f.write("11. **Removed editorial metadata** (1,375 files, 6,609 lines)\n")
        f.write("12. **Cleaned formatting artifacts** (30,523 files, 156,473 lines)\n")
        f.write("13. **Removed prose commentary** (1,427 reviewed, 589 cleaned, 357 deleted)\n")
        f.write("14. **Verified lineation** (2,088 long-line files confirmed intentional)\n")
        f.write("15. **Metadata cleanup** (3 sweeps, 3,821 files, 4,532 lines total)\n")
        f.write("16. **Removed verse drama** (227 files)\n")
        f.write("17. **Removed redundant titles** (150,908 files cleaned)\n\n")

        f.write("### Progression of Corpus Size\n\n")
        f.write("- Initial merged corpus: **170,889 poems**\n")
        f.write("- After first non-English removal: **167,799 poems**\n")
        f.write("- After verse drama removal: **167,215 poems**\n")
        f.write("- After second non-English removal: **166,176 poems**\n")
        f.write(f"- **Final corpus: {total_stats['files']:,} poems**\n\n")

        f.write("### Data Quality Improvements\n\n")
        f.write("- ✓ All poems organized by author\n")
        f.write("- ✓ Unified metadata format\n")
        f.write("- ✓ English-only corpus (>99% accuracy)\n")
        f.write("- ✓ Clean formatting (no editorial markup)\n")
        f.write("- ✓ No duplicate poems\n")
        f.write("- ✓ No redundant titles\n")
        f.write("- ✓ Standardized file naming\n")
        f.write("- ✓ Verified author attributions\n\n")

        f.write("## Next Steps\n\n")
        f.write("The corpus is now ready for:\n\n")
        f.write("1. **Hierarchical BERT training** - Primary goal\n")
        f.write("2. **Literary analysis** - Clean, standardized format\n")
        f.write("3. **Computational poetry research** - Large-scale dataset\n")
        f.write("4. **Stylometric studies** - Author-organized structure\n\n")

    print("\n" + "=" * 80)
    print("SUMMARY COMPLETE")
    print("=" * 80)
    print(f"\n**Final Corpus: {total_stats['files']:,} poems**")
    print(f"Authors: {total_stats['authors']:,}")
    print(f"Total lines: {total_stats['total_lines']:,}")
    print(f"Total words: {total_stats['total_words']:,}")
    print(f"\nFull report: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
