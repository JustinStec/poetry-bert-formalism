#!/usr/bin/env python3
"""
Phase 1.3: Comprehensive corpus validation suite.

This script validates:
1. File count = CSV count
2. All poem_ids are sequential (1 → N, no gaps)
3. All content_hashes are unique
4. All CSV filepaths match actual files
5. All files are readable and non-empty
6. Filename format is correct
7. CSV metadata is complete

Result: Validation report with pass/fail for each check
"""

import csv
import hashlib
from pathlib import Path
from collections import Counter
import json
from datetime import datetime

# Configuration
BASE_DIR = Path("/Users/justin/Repos/AI Project")
CORPUS_DIR = BASE_DIR / "data/processed/poetry_platform_renamed"
CSV_PATH = BASE_DIR / "data/metadata/corpus_final_metadata.csv"


class CorpusValidator:
    def __init__(self, csv_path, corpus_dir):
        self.csv_path = csv_path
        self.corpus_dir = corpus_dir
        self.csv_data = []
        self.results = {}

    def load_csv(self):
        """Load CSV data."""
        print("Loading CSV...")
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.csv_data = list(reader)
        print(f"✓ Loaded {len(self.csv_data)} entries from CSV\n")

    def validate_file_count(self):
        """Validate that file count matches CSV count."""
        print("Test 1: File count = CSV count")
        print("-" * 60)

        # Count files
        file_count = 0
        for author_dir in self.corpus_dir.iterdir():
            if author_dir.is_dir():
                file_count += len(list(author_dir.glob('*.txt')))

        csv_count = len(self.csv_data)

        print(f"  Files on disk: {file_count}")
        print(f"  Entries in CSV: {csv_count}")

        if file_count == csv_count:
            print("  ✓ PASS: Counts match\n")
            return True
        else:
            print(f"  ✗ FAIL: Mismatch of {abs(file_count - csv_count)} files\n")
            return False

    def validate_sequential_ids(self):
        """Validate that poem_ids are sequential with no gaps."""
        print("Test 2: Sequential poem IDs (no gaps)")
        print("-" * 60)

        poem_ids = [int(row['poem_id']) for row in self.csv_data]
        poem_ids_sorted = sorted(poem_ids)

        # Check for duplicates
        duplicates = [id for id, count in Counter(poem_ids).items() if count > 1]
        if duplicates:
            print(f"  ✗ FAIL: Found {len(duplicates)} duplicate poem_ids")
            print(f"  First few duplicates: {duplicates[:10]}\n")
            return False

        # Check sequentiality
        expected_ids = list(range(1, len(poem_ids) + 1))

        if poem_ids_sorted == expected_ids:
            print(f"  ✓ PASS: IDs are sequential (1 → {len(poem_ids)})\n")
            return True
        else:
            # Find gaps
            gaps = []
            for i, expected_id in enumerate(expected_ids):
                if expected_id != poem_ids_sorted[i]:
                    gaps.append(expected_id)

            print(f"  ✗ FAIL: Found {len(gaps)} gaps in ID sequence")
            print(f"  First few gaps: {gaps[:20]}\n")
            return False

    def validate_unique_hashes(self):
        """Validate that all content_hashes are unique."""
        print("Test 3: Unique content hashes (no duplicates)")
        print("-" * 60)

        hashes = [row['content_hash'] for row in self.csv_data]
        hash_counts = Counter(hashes)
        duplicates = {h: count for h, count in hash_counts.items() if count > 1}

        if duplicates:
            print(f"  ✗ FAIL: Found {len(duplicates)} duplicate hashes")
            print(f"  Total duplicate entries: {sum(duplicates.values()) - len(duplicates)}")
            print(f"  Example: {list(duplicates.items())[0]}\n")
            return False
        else:
            print(f"  ✓ PASS: All {len(hashes)} content hashes are unique\n")
            return True

    def validate_file_existence(self):
        """Validate that all CSV filepaths point to existing files."""
        print("Test 4: All CSV filepaths exist on disk")
        print("-" * 60)

        missing_files = []
        checked = 0

        for row in self.csv_data:
            filepath = self.corpus_dir / row['filepath']
            if not filepath.exists():
                missing_files.append(row['filepath'])

            checked += 1
            if checked % 10000 == 0:
                print(f"  Checked {checked} files...")

        if missing_files:
            print(f"  ✗ FAIL: {len(missing_files)} files not found on disk")
            print(f"  First few missing: {missing_files[:10]}\n")
            return False
        else:
            print(f"  ✓ PASS: All {len(self.csv_data)} files exist\n")
            return True

    def validate_file_readability(self):
        """Validate that all files are readable and non-empty."""
        print("Test 5: All files are readable and non-empty")
        print("-" * 60)

        unreadable = []
        empty = []
        checked = 0

        for row in self.csv_data:
            filepath = self.corpus_dir / row['filepath']

            if not filepath.exists():
                continue

            # Check if empty
            if filepath.stat().st_size == 0:
                empty.append(row['filepath'])
                continue

            # Check if readable
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content.strip():
                        empty.append(row['filepath'])
            except Exception as e:
                unreadable.append((row['filepath'], str(e)))

            checked += 1
            if checked % 10000 == 0:
                print(f"  Checked {checked} files...")

        issues = []
        if unreadable:
            print(f"  ✗ Unreadable files: {len(unreadable)}")
            issues.append(False)
        if empty:
            print(f"  ✗ Empty files: {len(empty)}")
            issues.append(False)

        if not issues:
            print(f"  ✓ PASS: All {checked} files are readable and non-empty\n")
            return True
        else:
            print(f"  ✗ FAIL: Found {len(unreadable) + len(empty)} problematic files\n")
            return False

    def validate_filename_format(self):
        """Validate that filenames follow the correct format."""
        print("Test 6: Filename format validation")
        print("-" * 60)

        # Expected format: NNNNNN_Title_Author_Date.txt
        # where NNNNNN is a 6-digit number

        invalid_formats = []
        checked = 0

        for row in self.csv_data:
            filename = Path(row['filepath']).name

            # Check if starts with 6 digits
            if not filename[:6].isdigit():
                invalid_formats.append((filename, "Missing 6-digit ID prefix"))
                continue

            # Check if ends with .txt
            if not filename.endswith('.txt'):
                invalid_formats.append((filename, "Missing .txt extension"))
                continue

            # Check for underscores (should have at least 3)
            if filename.count('_') < 3:
                invalid_formats.append((filename, "Missing underscores (need 3+)"))
                continue

            checked += 1
            if checked % 10000 == 0:
                print(f"  Checked {checked} filenames...")

        if invalid_formats:
            print(f"  ✗ FAIL: {len(invalid_formats)} filenames with invalid format")
            print(f"  Examples:")
            for filename, reason in invalid_formats[:5]:
                print(f"    {filename}: {reason}")
            print()
            return False
        else:
            print(f"  ✓ PASS: All {checked} filenames follow correct format\n")
            return True

    def validate_metadata_completeness(self):
        """Validate that all required CSV fields are complete."""
        print("Test 7: Metadata completeness")
        print("-" * 60)

        required_fields = [
            'poem_id', 'title', 'author', 'date', 'source',
            'filepath', 'lines', 'words', 'content_hash'
        ]

        incomplete_records = []

        for row in self.csv_data:
            missing_fields = []
            for field in required_fields:
                if not row.get(field) or row[field].strip() == '':
                    missing_fields.append(field)

            if missing_fields:
                incomplete_records.append({
                    'poem_id': row.get('poem_id'),
                    'title': row.get('title'),
                    'missing_fields': missing_fields
                })

        if incomplete_records:
            print(f"  ✗ FAIL: {len(incomplete_records)} records with missing fields")
            print(f"  Examples:")
            for record in incomplete_records[:5]:
                print(f"    Poem {record['poem_id']}: Missing {record['missing_fields']}")
            print()
            return False
        else:
            print(f"  ✓ PASS: All {len(self.csv_data)} records have complete metadata\n")
            return True

    def validate_hash_integrity(self):
        """Spot-check content hashes against actual file content."""
        print("Test 8: Content hash integrity (spot check)")
        print("-" * 60)

        # Sample 100 random poems
        import random
        sample_size = min(100, len(self.csv_data))
        sample = random.sample(self.csv_data, sample_size)

        mismatches = []

        for i, row in enumerate(sample, 1):
            if i % 20 == 0:
                print(f"  Checked {i}/{sample_size} hashes...")

            filepath = self.corpus_dir / row['filepath']

            if not filepath.exists():
                continue

            # Calculate hash
            try:
                with open(filepath, 'rb') as f:
                    actual_hash = hashlib.md5(f.read()).hexdigest()

                if actual_hash != row['content_hash']:
                    mismatches.append({
                        'poem_id': row['poem_id'],
                        'filepath': row['filepath'],
                        'csv_hash': row['content_hash'],
                        'actual_hash': actual_hash
                    })
            except Exception as e:
                mismatches.append({
                    'poem_id': row['poem_id'],
                    'filepath': row['filepath'],
                    'error': str(e)
                })

        if mismatches:
            print(f"  ✗ FAIL: {len(mismatches)} hash mismatches in sample")
            print(f"  Examples:")
            for m in mismatches[:3]:
                print(f"    Poem {m['poem_id']}: {m.get('error', 'Hash mismatch')}")
            print()
            return False
        else:
            print(f"  ✓ PASS: All {sample_size} sampled hashes match\n")
            return True

    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 80)
        print("CORPUS VALIDATION SUITE")
        print("=" * 80)
        print()

        self.load_csv()

        # Run all tests
        tests = [
            ('File count match', self.validate_file_count),
            ('Sequential IDs', self.validate_sequential_ids),
            ('Unique hashes', self.validate_unique_hashes),
            ('File existence', self.validate_file_existence),
            ('File readability', self.validate_file_readability),
            ('Filename format', self.validate_filename_format),
            ('Metadata completeness', self.validate_metadata_completeness),
            ('Hash integrity', self.validate_hash_integrity),
        ]

        results = {}
        for test_name, test_func in tests:
            results[test_name] = test_func()

        # Summary
        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()

        passed = sum(results.values())
        total = len(results)

        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {test_name}")

        print()
        print(f"Tests passed: {passed}/{total}")

        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Corpus is valid.\n")
            return True
        else:
            print(f"\n⚠️  {total - passed} TEST(S) FAILED. Review issues above.\n")
            return False


def main():
    validator = CorpusValidator(CSV_PATH, CORPUS_DIR)
    success = validator.run_all_tests()

    # Exit code
    import sys
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
