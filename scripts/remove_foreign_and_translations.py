#!/usr/bin/env python3
"""
Remove foreign language works and translations from corpus.
Does NOT remove verse drama - that will be refined separately.
"""

import json
import csv
from pathlib import Path
import shutil

# Paths
POETRY_PLATFORM_DIR = Path("/Users/justin/Repos/AI Project/Data/poetry_platform_renamed")
GUTENBERG_DIR = Path("/Users/justin/Repos/AI Project/Data/Corpora/Gutenberg/By_Author")
UNIFIED_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_italic_cleaned.csv")
NEW_CSV = Path("/Users/justin/Repos/AI Project/Data/unified_corpus_metadata_english_only.csv")
FLAGGED_JSON = Path("/Users/justin/Repos/AI Project/scripts/flagged_for_removal.json")
REMOVED_DIR = Path("/Users/justin/Repos/AI Project/Data/removed_files")
REMOVAL_REPORT = Path("/Users/justin/Repos/AI Project/scripts/removal_report.txt")

# Settings
DRY_RUN = False  # Set to False to actually delete files

def get_file_path(filename):
    """Get full file path from filename."""
    if 'gutenberg' in filename.lower():
        for author_dir in GUTENBERG_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path
    else:
        # Poetry Platform file - need to search by author folder
        # Extract author from filename: {id}_{title}_{author}_{year}.txt
        parts = filename.rsplit('_', 2)
        if len(parts) >= 2:
            author = parts[-2].replace('_', ' ')
            filepath = POETRY_PLATFORM_DIR / author / filename
            if filepath.exists():
                return filepath

        # If that fails, search all author folders
        for author_dir in POETRY_PLATFORM_DIR.iterdir():
            if author_dir.is_dir():
                test_path = author_dir / filename
                if test_path.exists():
                    return test_path

    return None

def load_flagged_files():
    """Load flagged files and filter for foreign language + translations only."""
    print("=" * 80)
    print("REMOVE FOREIGN LANGUAGE & TRANSLATIONS")
    print("=" * 80)
    print(f"DRY RUN: {DRY_RUN}")
    print("=" * 80)

    print("\nLoading flagged files...")
    with open(FLAGGED_JSON, 'r', encoding='utf-8') as f:
        flagged = json.load(f)

    print(f"✓ Loaded {len(flagged):,} flagged works")

    # Filter for foreign language and translations only (exclude verse drama)
    to_remove = []
    for item in flagged:
        categories = item['categories']
        # Keep if it's foreign_language OR translation (but not ONLY verse_drama)
        if 'foreign_language' in categories or 'translation' in categories:
            to_remove.append(item)

    print(f"✓ Filtered to {len(to_remove):,} works (foreign language + translations)")

    # Statistics
    foreign_only = sum(1 for item in to_remove if 'foreign_language' in item['categories'])
    translation_only = sum(1 for item in to_remove if 'translation' in item['categories'])
    both = sum(1 for item in to_remove if 'foreign_language' in item['categories'] and 'translation' in item['categories'])

    print("\nBreakdown:")
    print(f"  Foreign language: {foreign_only:,}")
    print(f"  Translations: {translation_only:,}")
    print(f"  Both: {both:,}")

    return to_remove

def remove_files(to_remove):
    """Remove flagged files and update metadata."""
    print("\n" + "=" * 80)
    print("REMOVING FILES")
    print("=" * 80)

    # Create removal directory if it doesn't exist
    if not DRY_RUN:
        REMOVED_DIR.mkdir(exist_ok=True)
        (REMOVED_DIR / "foreign_language").mkdir(exist_ok=True)
        (REMOVED_DIR / "translations").mkdir(exist_ok=True)

    # Load metadata
    print("\nLoading metadata CSV...")
    rows = []
    with open(UNIFIED_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"✓ Loaded {len(rows):,} entries")

    # Create set of filenames to remove
    filenames_to_remove = {item['filename'] for item in to_remove}

    # Process files
    print("\nRemoving files...")
    removed_count = 0
    not_found_count = 0
    kept_rows = []

    for i, row in enumerate(rows):
        if i % 10000 == 0 and i > 0:
            print(f"  Processed {i:,}/{len(rows):,}...")

        filename = row['filename']

        if filename in filenames_to_remove:
            # File should be removed
            filepath = get_file_path(filename)

            if filepath and filepath.exists():
                if not DRY_RUN:
                    # Determine which category
                    item = next(item for item in to_remove if item['filename'] == filename)
                    if 'foreign_language' in item['categories']:
                        dest_dir = REMOVED_DIR / "foreign_language"
                    else:
                        dest_dir = REMOVED_DIR / "translations"

                    # Move file to removed directory
                    dest_path = dest_dir / filename
                    try:
                        shutil.move(str(filepath), str(dest_path))
                        removed_count += 1
                    except Exception as e:
                        print(f"\n  Error moving {filename}: {e}")
                else:
                    removed_count += 1
            else:
                not_found_count += 1
        else:
            # Keep this file
            kept_rows.append(row)

    print(f"\n✓ Removed {removed_count:,} files")
    if not_found_count:
        print(f"✗ Could not find {not_found_count:,} files")

    # Write new CSV
    print(f"\nWriting updated metadata to {NEW_CSV}...")
    if not DRY_RUN:
        with open(NEW_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(kept_rows)

    print(f"✓ New corpus has {len(kept_rows):,} entries")
    print(f"✓ Removed {len(rows) - len(kept_rows):,} entries from metadata")

    return removed_count, kept_rows

def generate_report(to_remove, removed_count, kept_count):
    """Generate removal report."""
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)

    with open(REMOVAL_REPORT, 'w', encoding='utf-8') as f:
        f.write("Foreign Language & Translation Removal Report\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total files removed: {removed_count:,}\n")
        f.write(f"Remaining corpus size: {kept_count:,}\n\n")

        # By category
        foreign = [item for item in to_remove if 'foreign_language' in item['categories']]
        translations = [item for item in to_remove if 'translation' in item['categories']]

        f.write(f"Foreign language works removed: {len(foreign):,}\n")
        f.write(f"Translations removed: {len(translations):,}\n\n")

        # Sample removed files
        f.write("Sample Foreign Language Works Removed (First 20):\n")
        f.write("-" * 80 + "\n")
        for i, item in enumerate(foreign[:20]):
            f.write(f"{i+1}. {item['title']} - {item['author']}\n")
            f.write(f"   File: {item['filename']}\n\n")

        f.write("\nSample Translations Removed (First 20):\n")
        f.write("-" * 80 + "\n")
        for i, item in enumerate(translations[:20]):
            f.write(f"{i+1}. {item['title']} - {item['author']}\n")
            f.write(f"   File: {item['filename']}\n\n")

    print(f"✓ Report saved to: {REMOVAL_REPORT}")

def main():
    print("Remove Foreign Language & Translations")
    print("Verse drama will be handled separately\n")

    # Load flagged files
    to_remove = load_flagged_files()

    if not to_remove:
        print("\nNo files to remove!")
        return

    # Remove files
    removed_count, kept_rows = remove_files(to_remove)

    # Generate report
    generate_report(to_remove, removed_count, len(kept_rows))

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files removed: {removed_count:,}")
    print(f"Remaining corpus: {len(kept_rows):,}")

    if DRY_RUN:
        print("\n" + "=" * 80)
        print("DRY RUN - No files were actually deleted")
        print("=" * 80)
        print("Review the numbers above, then set DRY_RUN = False to apply removal")
    else:
        print("\n" + "=" * 80)
        print("REMOVAL COMPLETE")
        print("=" * 80)
        print(f"✓ Updated metadata: {NEW_CSV}")
        print(f"✓ Removed files moved to: {REMOVED_DIR}")

if __name__ == '__main__':
    main()
