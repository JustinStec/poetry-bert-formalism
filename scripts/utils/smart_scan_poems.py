#!/usr/bin/env python3
"""
Smart poem scanner - works with existing Excel metadata
Only adds NEW poems that don't have metadata entries yet
"""

import pandas as pd
from pathlib import Path
import re

# Paths
CORPUS_DIR = Path.home() / "Repos/AI Project/Data/corpus_texts"
METADATA_FILE = Path.home() / "Repos/AI Project/Metadata/corpus_metadata.xlsx"

def count_text_stats(filepath):
    """Count lines and words in a text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        lines = len(text.strip().split('\n'))
        words = len(text.split())
    return lines, words

def parse_filename(filename):
    """Extract info from filename: NNN_Author_Title.txt"""
    # Remove .txt
    name = filename.replace('.txt', '')

    # Split by first underscore (number)
    parts = name.split('_', 1)

    if len(parts) < 2:
        return None, filename, "UNKNOWN"

    poem_id = parts[0]
    rest = parts[1]

    # Try to split author and title
    # Assume first 1-2 words are author, rest is title
    words = rest.split('_')

    if len(words) >= 2:
        # Simple heuristic: author is first 2 words or until we hit lowercase
        author_parts = []
        title_parts = []
        in_title = False

        for i, word in enumerate(words):
            if i < 2 and not in_title:
                author_parts.append(word)
            else:
                title_parts.append(word)

        author = ' '.join(author_parts)
        title = ' '.join(title_parts)
    else:
        author = words[0] if words else "UNKNOWN"
        title = "UNKNOWN"

    return poem_id, author, title

def main():
    print("=" * 50)
    print("   SMART POEM SCANNER")
    print("=" * 50)
    print()

    # Load existing metadata if it exists
    try:
        df = pd.read_excel(METADATA_FILE)
        print(f"✓ Loaded existing metadata: {len(df)} entries")
        existing_files = set(df['filename'].values) if 'filename' in df.columns else set()
    except FileNotFoundError:
        print("! No existing metadata found - will create new file")
        df = pd.DataFrame(columns=['id', 'filename', 'author', 'title', 'year',
                                   'period', 'form', 'lines', 'words', 'collected'])
        existing_files = set()

    print()

    # Scan corpus directory
    poem_files = list(CORPUS_DIR.glob('*.txt'))
    print(f"Total poems in corpus: {len(poem_files)}")
    print()

    # Find new poems
    new_poems = []
    for poem_path in sorted(poem_files):
        filename = poem_path.name

        if filename in existing_files:
            continue  # Already have metadata

        # Parse filename
        poem_id, author, title = parse_filename(filename)

        # Count stats
        lines, words = count_text_stats(poem_path)

        # Create entry
        new_poems.append({
            'id': poem_id,
            'filename': filename,
            'author': author,
            'title': title,
            'year': 'UNKNOWN',
            'period': 'UNKNOWN',
            'form': 'UNKNOWN',
            'lines': lines,
            'words': words,
            'collected': False
        })

        print(f"✓ New poem: {filename}")
        print(f"  Author: {author}, Title: {title}")
        print(f"  Stats: {lines} lines, {words} words")
        print()

    if not new_poems:
        print("=" * 50)
        print("No new poems found!")
        print("All poems already have metadata entries.")
        print("=" * 50)
        return

    # Add new poems to dataframe
    new_df = pd.DataFrame(new_poems)
    df = pd.concat([df, new_df], ignore_index=True)

    # Save updated metadata
    df.to_excel(METADATA_FILE, index=False)

    print("=" * 50)
    print(f"✓ Added {len(new_poems)} new poems to metadata!")
    print("=" * 50)
    print()
    print("Next steps:")
    print(f"1. Open: {METADATA_FILE}")
    print("2. Fill in: year, period, form for new poems")
    print("3. Set collected=TRUE for poems to analyze")
    print()
    print(f"Total poems with metadata: {len(df)}")

if __name__ == '__main__':
    main()
