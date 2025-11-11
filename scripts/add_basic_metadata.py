#!/usr/bin/env python3
"""
Phase 2: Add automated basic metadata (Tier 1 fields).

This script:
1. Fixes 2 poems with missing titles
2. Recomputes line_counts and word_counts from actual files
3. Parses author names into author_last, author_first
4. Extracts/approximates years from date field
5. Generates source_url from source field
6. Adds created_at, updated_at timestamps
7. Prepares search_vector field (populated later in PostgreSQL)

Goal: 100% coverage on Tier 1 metadata (17 fields)
"""

import csv
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"
OUTPUT_CSV = BASE_DIR / "data/metadata/corpus_with_tier1_metadata.csv"

# Source URL templates
SOURCE_URL_TEMPLATES = {
    'poetry_foundation': 'https://www.poetryfoundation.org/poems/{poem_id}',
    'poetrydb': 'https://poetrydb.org/title/{title}',
    'gutenberg': 'https://www.gutenberg.org/ebooks/{id}',
    'poetry_platform': 'https://www.poetry.com/poem/{id}',
}

def fix_missing_titles(row, corpus_dir):
    """Fix poems with missing titles by reading file content."""
    if not row['title'] or row['title'].strip() == '':
        filepath = corpus_dir / row['filepath']

        if filepath.exists():
            # Try to extract title from filename
            filename = filepath.name
            # Format: NNNNNN_Title_Author_Date.txt
            parts = filename.split('_')
            if len(parts) >= 2:
                # Title is between first _ and last two _
                title_parts = parts[1:-2]  # Skip ID and last 2 (author, date)
                title = ' '.join(title_parts)

                if title and title.strip():
                    return title.strip()

            # If still no title, read first line of file
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line and len(first_line) < 100:  # Reasonable title length
                        return first_line
            except:
                pass

        # Last resort: use "Untitled"
        return "Untitled"

    return row['title']

def recompute_counts(filepath):
    """Recompute line and word counts from actual file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = [line for line in content.split('\n') if line.strip()]
            words = content.split()

            return len(lines), len(words)
    except:
        return 0, 0

def parse_author_name(author):
    """Parse author into last name and first name."""
    # Format is usually "Last, First" or "Last, First Middle"
    if ',' in author:
        parts = author.split(',', 1)
        author_last = parts[0].strip()
        author_first = parts[1].strip() if len(parts) > 1 else ''
    else:
        # No comma, assume it's all last name (or single name)
        author_last = author.strip()
        author_first = ''

    return author_last, author_first

def extract_year(date_str):
    """Extract or approximate year from date field."""
    if not date_str or date_str == 'unknown':
        return None

    # Try to find 4-digit year
    year_match = re.search(r'\b(1[0-9]{3}|20[0-2][0-9])\b', date_str)
    if year_match:
        return int(year_match.group(1))

    # Try to find 2-digit year and approximate century
    year_match = re.search(r'\b([0-9]{2})\b', date_str)
    if year_match:
        two_digit = int(year_match.group(1))
        # Assume 19xx for years that make sense
        if two_digit >= 0 and two_digit <= 99:
            return 1900 + two_digit if two_digit > 24 else 2000 + two_digit

    return None

def generate_source_url(source, poem_id, title):
    """Generate source URL based on source field."""
    if not source or source == 'unknown':
        return ''

    source_lower = source.lower()

    # Match against templates
    for key, template in SOURCE_URL_TEMPLATES.items():
        if key in source_lower:
            try:
                if '{poem_id}' in template:
                    return template.format(poem_id=poem_id)
                elif '{title}' in template:
                    # URL-safe title
                    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-')
                    return template.format(title=safe_title)
                elif '{id}' in template:
                    return template.format(id=poem_id)
            except:
                pass

    return ''

def add_tier1_metadata(dry_run=True):
    """Add all Tier 1 metadata fields."""

    print("=" * 70)
    print("PHASE 2: ADD TIER 1 METADATA")
    if dry_run:
        print("[DRY RUN - No files will be modified]")
    print("=" * 70)
    print()

    print("Loading CSV...")
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"✓ Loaded {len(rows)} poems\n")

    # New fieldnames (Tier 1 complete)
    new_fieldnames = [
        'poem_id',
        'title',
        'author',
        'author_last',      # NEW
        'author_first',     # NEW
        'date',
        'year_approx',      # NEW
        'source',
        'source_url',       # NEW
        'filepath',
        'filename',         # NEW
        'content',          # Placeholder, will add later if needed
        'length_lines',     # Recomputed
        'length_words',     # Recomputed
        'file_size',
        'content_hash',
        'search_vector',    # NEW - placeholder for PostgreSQL
        'created_at',       # NEW
        'updated_at',       # NEW
    ]

    # Process each poem
    print("Processing poems...")
    timestamp = datetime.now().isoformat()

    fixed_titles = 0
    recomputed = 0

    for i, row in enumerate(rows):
        if (i + 1) % 10000 == 0:
            print(f"  Processed {i + 1} poems...")

        # 1. Fix missing titles
        old_title = row.get('title', '')
        new_title = fix_missing_titles(row, CORPUS_DIR)
        if old_title != new_title:
            row['title'] = new_title
            fixed_titles += 1
            if fixed_titles <= 5:
                print(f"  Fixed title for poem {row['poem_id']}: '{new_title}'")

        # 2. Recompute counts
        filepath = CORPUS_DIR / row['filepath']
        if filepath.exists():
            lines, words = recompute_counts(filepath)
            row['length_lines'] = lines
            row['length_words'] = words
            recomputed += 1

        # 3. Parse author names
        author_last, author_first = parse_author_name(row['author'])
        row['author_last'] = author_last
        row['author_first'] = author_first

        # 4. Extract year
        year_approx = extract_year(row.get('date', ''))
        row['year_approx'] = year_approx if year_approx else ''

        # 5. Generate source URL
        source_url = generate_source_url(
            row.get('source', ''),
            row['poem_id'],
            row['title']
        )
        row['source_url'] = source_url

        # 6. Add filename (extract from filepath)
        row['filename'] = Path(row['filepath']).name

        # 7. Add placeholders for content and search_vector
        row['content'] = ''  # Will be populated if needed
        row['search_vector'] = ''  # Will be populated in PostgreSQL

        # 8. Add timestamps
        row['created_at'] = timestamp
        row['updated_at'] = timestamp

    print(f"\n✓ Processed {len(rows)} poems")
    print(f"  Fixed titles: {fixed_titles}")
    print(f"  Recomputed counts: {recomputed}")

    # Write new CSV
    print(f"\nWriting enhanced CSV to: {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Wrote {len(rows)} rows with {len(new_fieldnames)} fields")

    # Summary
    print("\n" + "=" * 70)
    print("TIER 1 METADATA COMPLETE")
    print("=" * 70)
    print(f"\nTotal poems: {len(rows)}")
    print(f"Total fields: {len(new_fieldnames)}")
    print("\nNew fields added:")
    print("  - author_last, author_first")
    print("  - year_approx")
    print("  - source_url")
    print("  - filename")
    print("  - search_vector (placeholder)")
    print("  - created_at, updated_at")

    if dry_run:
        print("\n[DRY RUN] Review output above.")
        print("Run with --execute to write changes.")
    else:
        print("\n✓ Phase 2 complete!")
        print("\nNext steps:")
        print("1. Review output CSV")
        print("2. Replace old CSV: mv corpus_with_tier1_metadata.csv corpus_final_metadata.csv")
        print("3. Commit to GitHub")
        print("4. Transfer project to M4 Max for Phase 3 (LLM fine-tuning)")

def main():
    import sys
    dry_run = '--execute' not in sys.argv

    add_tier1_metadata(dry_run=dry_run)

if __name__ == '__main__':
    main()
