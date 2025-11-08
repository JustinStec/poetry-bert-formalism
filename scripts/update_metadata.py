#!/usr/bin/env python3
"""
Create final metadata CSV reflecting the cleaned corpus.
Scans the actual cleaned corpus directories and generates fresh metadata.
"""

import csv
from pathlib import Path
from collections import Counter
import hashlib

BASE_DIR = Path("/Users/justin/Repos/AI Project")
POETRY_PLATFORM_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
GUTENBERG_DIR = BASE_DIR / "data/processed/gutenberg"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_final_metadata.csv"

def extract_metadata_from_filename(filename):
    """Extract metadata from filename format: ID_Title_Author_Date.txt"""
    parts = filename.rsplit('_', 2)
    if len(parts) >= 3:
        title_part = parts[0].split('_', 1)
        if len(title_part) > 1:
            poem_id = title_part[0]
            title = title_part[1]
            author = parts[1]
            date = parts[2].replace('.txt', '')
            return poem_id, title, author, date
    return None, filename.replace('.txt', ''), 'Unknown', 'unknown'

def calculate_file_hash(filepath):
    """Calculate MD5 hash of file content for uniqueness verification."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def count_lines_and_words(filepath):
    """Count lines and words in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = len([line for line in content.split('\n') if line.strip()])
            words = len(content.split())
            return lines, words
    except:
        return 0, 0

def scan_corpus():
    """Scan corpus directories and extract metadata."""
    all_poems = []
    hashes_seen = set()
    duplicates_found = 0

    directories = [
        ('poetry_platform', POETRY_PLATFORM_DIR),
    ]

    # Check if Gutenberg directory exists separately
    if GUTENBERG_DIR.exists():
        directories.append(('gutenberg', GUTENBERG_DIR))

    for source, directory in directories:
        if not directory.exists():
            continue

        print(f"Scanning {source}...")
        file_count = 0

        for author_dir in sorted(directory.iterdir()):
            if not author_dir.is_dir():
                continue

            for filepath in author_dir.glob('*.txt'):
                file_count += 1
                if file_count % 10000 == 0:
                    print(f"  Processed {file_count} files...")

                poem_id, title, author, date = extract_metadata_from_filename(filepath.name)
                lines, words = count_lines_and_words(filepath)
                file_hash = calculate_file_hash(filepath)

                # Check for duplicates
                if file_hash in hashes_seen:
                    duplicates_found += 1
                    continue
                hashes_seen.add(file_hash)

                # Get file stats
                stat = filepath.stat()

                all_poems.append({
                    'poem_id': poem_id,
                    'title': title,
                    'author': author,
                    'date': date,
                    'source': source,
                    'filepath': f"{author_dir.name}/{filepath.name}",
                    'lines': lines,
                    'words': words,
                    'file_size': stat.st_size,
                    'content_hash': file_hash,
                    'last_modified': stat.st_mtime
                })

        print(f"  Found {file_count} poems in {source}")

    print(f"\nTotal poems: {len(all_poems)}")
    print(f"Duplicates skipped: {duplicates_found}")

    return all_poems

def generate_statistics(poems):
    """Generate summary statistics."""
    stats = {
        'total_poems': len(poems),
        'total_lines': sum(p['lines'] for p in poems),
        'total_words': sum(p['words'] for p in poems),
        'total_authors': len(set(p['author'] for p in poems)),
        'by_source': Counter(p['source'] for p in poems),
        'by_date': Counter(p['date'] for p in poems),
        'avg_lines': round(sum(p['lines'] for p in poems) / len(poems), 1) if poems else 0,
        'avg_words': round(sum(p['words'] for p in poems) / len(poems), 1) if poems else 0,
    }

    return stats

def write_csv(poems, output_path):
    """Write metadata to CSV."""
    fieldnames = [
        'poem_id', 'title', 'author', 'date', 'source', 'filepath',
        'lines', 'words', 'file_size', 'content_hash'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for poem in sorted(poems, key=lambda x: (x['author'], x['title'])):
            row = {k: poem[k] for k in fieldnames}
            writer.writerow(row)

def main():
    print("=" * 80)
    print("GENERATING FINAL CORPUS METADATA")
    print("=" * 80)
    print()

    # Scan corpus
    poems = scan_corpus()

    # Generate statistics
    print("\nGenerating statistics...")
    stats = generate_statistics(poems)

    # Write CSV
    print(f"\nWriting metadata to {OUTPUT_CSV}...")
    write_csv(poems, OUTPUT_CSV)

    # Write statistics file
    stats_file = BASE_DIR / "data/metadata/corpus_statistics.txt"
    with open(stats_file, 'w') as f:
        f.write("Final Corpus Statistics\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Poems: {stats['total_poems']:,}\n")
        f.write(f"Total Authors: {stats['total_authors']:,}\n")
        f.write(f"Total Lines: {stats['total_lines']:,}\n")
        f.write(f"Total Words: {stats['total_words']:,}\n")
        f.write(f"Average Lines/Poem: {stats['avg_lines']}\n")
        f.write(f"Average Words/Poem: {stats['avg_words']}\n\n")
        f.write("By Source:\n")
        for source, count in stats['by_source'].items():
            f.write(f"  {source}: {count:,} poems\n")

    print("\n" + "=" * 80)
    print("METADATA GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n✓ Metadata CSV: {OUTPUT_CSV}")
    print(f"✓ Statistics: {stats_file}")
    print(f"\nTotal poems: {stats['total_poems']:,}")
    print(f"Total authors: {stats['total_authors']:,}")
    print(f"Total words: {stats['total_words']:,}")

if __name__ == '__main__':
    main()
