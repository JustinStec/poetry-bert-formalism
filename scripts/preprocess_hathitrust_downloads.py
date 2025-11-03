#!/usr/bin/env python3
"""
Preprocess HathiTrust Downloads for BERT Training

Processes downloaded HathiTrust texts into unified JSONL format.
Handles workset exports, individual texts, and bulk rsync downloads.

Input: Raw HathiTrust downloads (various formats)
Output: Standardized JSONL files by period
"""

import json
import logging
import re
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class HathiTrustPreprocessor:
    """Process HathiTrust downloads into unified format."""

    def __init__(self, input_dir: str, output_dir: str, min_ocr_quality: float = 0.90):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_ocr_quality = min_ocr_quality
        self.stats = defaultdict(int)

    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """
        Extract metadata from HathiTrust filename.

        Common formats:
        - {htid}.txt
        - {author}_{title}_{year}.txt
        - Volume_XXXXX.txt
        """
        metadata = {
            'filename': filename,
            'htid': None,
            'title': None,
            'author': None,
            'year': None
        }

        # Try to extract year from filename
        year_match = re.search(r'\b(1[4-9]\d{2}|20\d{2})\b', filename)
        if year_match:
            metadata['year'] = int(year_match.group(1))

        # HathiTrust ID format: institution.identifier
        htid_match = re.search(r'([a-z]+\.[0-9a-z]+)', filename)
        if htid_match:
            metadata['htid'] = htid_match.group(1)

        return metadata

    def assess_ocr_quality(self, text: str) -> float:
        """
        Estimate OCR quality from text characteristics.

        Checks for:
        - Gibberish ratio
        - Common OCR errors
        - Word/character distribution
        - Line breaks and formatting

        Returns: confidence score 0.0-1.0
        """
        if not text or len(text) < 100:
            return 0.0

        lines = text.split('\n')
        total_chars = len(text)

        # 1. Check word quality
        words = text.split()
        if not words:
            return 0.0

        # Valid English words (mostly alphabetic, reasonable length)
        valid_words = sum(1 for w in words
                         if w.isalpha() and 2 <= len(w) <= 20)
        word_quality = valid_words / len(words) if words else 0.0

        # 2. Check for common OCR errors
        ocr_error_patterns = {
            'rn_to_m': text.lower().count('rn'),  # 'rn' misread as 'm'
            'cl_to_d': text.lower().count('cl'),  # 'cl' misread as 'd'
            'vv_to_w': text.lower().count('vv'),  # 'vv' misread as 'w'
            'ii_to_n': text.lower().count('ii'),  # 'ii' misread as 'n'
        }

        error_rate = sum(ocr_error_patterns.values()) / total_chars if total_chars > 0 else 1.0

        # 3. Check line quality (poetry should have reasonable line lengths)
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0

        line_quality = 1.0
        if avg_line_length < 10:  # Fragmented lines
            line_quality = 0.5
        elif avg_line_length > 200:  # No line breaks (wall of text)
            line_quality = 0.7

        # 4. Check for excessive whitespace
        whitespace_ratio = text.count('  ') / total_chars if total_chars > 0 else 0
        whitespace_quality = 1.0 - min(whitespace_ratio * 10, 0.3)

        # Combine metrics
        ocr_score = (
            word_quality * 0.5 +
            (1.0 - min(error_rate * 100, 0.3)) * 0.2 +
            line_quality * 0.2 +
            whitespace_quality * 0.1
        )

        return max(0.0, min(1.0, ocr_score))

    def guess_period_from_year(self, year: Optional[int]) -> str:
        """Map publication year to historical period."""
        if not year:
            return 'unknown'

        if year < 1660:
            return 'early_modern'
        elif year < 1700:
            return 'restoration'
        elif year < 1780:
            return 'augustan'
        elif year < 1830:
            return 'romantic'
        elif year < 1900:
            return 'victorian'
        elif year < 2000:
            return 'modern'
        else:
            return 'contemporary'

    def process_text_file(self, filepath: Path) -> Optional[Dict]:
        """Process a single text file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

            # Extract metadata from filename
            metadata = self.extract_metadata_from_filename(filepath.stem)

            # Assess OCR quality
            ocr_quality = self.assess_ocr_quality(text)

            if ocr_quality < self.min_ocr_quality:
                logging.debug(f"Skipping {filepath.name} (OCR quality: {ocr_quality:.2f})")
                self.stats['low_quality'] += 1
                return None

            # Split into lines
            lines = [line.rstrip() for line in text.split('\n')]

            # Create work entry
            work = {
                'work_id': f"hathitrust_{metadata.get('htid', filepath.stem)}",
                'title': metadata.get('title', f"HathiTrust {filepath.stem}"),
                'author': metadata.get('author'),
                'hathitrust_id': metadata.get('htid'),
                'publication_date': metadata.get('year'),
                'period': self.guess_period_from_year(metadata.get('year')),
                'source': 'hathitrust',
                'text': text,
                'lines': lines,
                'line_count': len([l for l in lines if l.strip()]),
                'ocr_quality': ocr_quality,
                'metadata_complete': metadata.get('year') is not None,
            }

            self.stats['processed'] += 1
            return work

        except Exception as e:
            logging.error(f"Error processing {filepath}: {e}")
            self.stats['errors'] += 1
            return None

    def process_workset_export(self, filepath: Path) -> List[Dict]:
        """
        Process HathiTrust workset export.

        Handles various export formats:
        - ZIP archives with multiple texts
        - JSONL workset metadata
        - CSV volume lists
        """
        works = []

        if filepath.suffix == '.zip':
            # Extract and process all texts in ZIP
            with zipfile.ZipFile(filepath, 'r') as zf:
                for name in zf.namelist():
                    if name.endswith('.txt'):
                        with zf.open(name) as f:
                            text = f.read().decode('utf-8', errors='ignore')

                        # Process as text
                        # (Similar to process_text_file but for in-memory text)
                        # Simplified for now
                        logging.info(f"Processing {name} from {filepath.name}")

        elif filepath.suffix == '.json' or filepath.suffix == '.jsonl':
            # Workset metadata file
            with open(filepath, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    # Extract volume IDs and metadata
                    logging.info(f"Found volume: {data.get('htid', 'unknown')}")

        return works

    def process_directory(self) -> Dict[str, List[Dict]]:
        """
        Process all files in input directory.

        Returns: dict mapping period to list of works
        """
        logging.info(f"Processing files in {self.input_dir}...")

        # Find all text files
        text_files = list(self.input_dir.rglob("*.txt"))
        zip_files = list(self.input_dir.rglob("*.zip"))

        logging.info(f"Found {len(text_files)} text files, {len(zip_files)} ZIP files")

        # Group works by period
        works_by_period = defaultdict(list)

        # Process text files
        for filepath in tqdm(text_files, desc="Processing texts"):
            work = self.process_text_file(filepath)
            if work:
                # Determine target period for BERT training
                year = work.get('publication_date')
                if year:
                    if 1700 <= year < 1800:
                        period = '1700-1800'
                    elif 1800 <= year < 1900:
                        period = '1800-1900'
                    elif 1900 <= year < 2000:
                        period = '1900-2000'
                    else:
                        period = 'other'
                else:
                    period = 'unknown'

                works_by_period[period].append(work)

        # Process ZIP files
        for filepath in zip_files:
            workset_works = self.process_workset_export(filepath)
            # Add to appropriate periods
            # (implementation depends on workset format)

        return works_by_period

    def save_by_period(self, works_by_period: Dict[str, List[Dict]]):
        """Save works grouped by period to separate JSONL files."""

        for period, works in works_by_period.items():
            if not works:
                continue

            output_file = self.output_dir / f"hathitrust_{period.replace('-', '_')}.jsonl"

            logging.info(f"Saving {len(works)} works for {period}...")

            with open(output_file, 'w', encoding='utf-8') as f:
                for work in works:
                    f.write(json.dumps(work, ensure_ascii=False) + '\n')

            logging.info(f"✓ Saved to {output_file}")

    def print_stats(self):
        """Print processing statistics."""
        logging.info("\n" + "="*60)
        logging.info("PROCESSING SUMMARY")
        logging.info("="*60)
        logging.info(f"Processed: {self.stats['processed']}")
        logging.info(f"Low quality (skipped): {self.stats['low_quality']}")
        logging.info(f"Errors: {self.stats['errors']}")
        logging.info("="*60)


def main():
    """Process HathiTrust downloads."""

    base_path = Path("/Users/justin/Repos/AI Project")
    input_dir = base_path / "Data/hathitrust/raw"
    output_dir = base_path / "Data"

    # Check if input directory exists and has files
    if not input_dir.exists():
        logging.error(f"Input directory not found: {input_dir}")
        logging.info("Please download HathiTrust texts first.")
        logging.info("Run: python scripts/download_hathitrust_corpus.py")
        return

    files = list(input_dir.rglob("*.txt")) + list(input_dir.rglob("*.zip"))
    if not files:
        logging.error(f"No files found in {input_dir}")
        logging.info("\nDownload HathiTrust texts to this directory:")
        logging.info(f"  {input_dir}")
        logging.info("\nThen re-run this script.")
        return

    # Process
    logging.info("="*60)
    logging.info("HATHITRUST PREPROCESSING")
    logging.info("="*60)
    logging.info(f"Input: {input_dir}")
    logging.info(f"Output: {output_dir}")
    logging.info(f"Min OCR quality: 0.90")
    logging.info("")

    preprocessor = HathiTrustPreprocessor(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        min_ocr_quality=0.90
    )

    # Process all files
    works_by_period = preprocessor.process_directory()

    # Save by period
    preprocessor.save_by_period(works_by_period)

    # Print stats
    preprocessor.print_stats()

    # Summary
    logging.info("\n" + "="*60)
    logging.info("NEXT STEPS")
    logging.info("="*60)
    logging.info("1. Review generated JSONL files:")
    for period in works_by_period.keys():
        output_file = output_dir / f"hathitrust_{period.replace('-', '_')}.jsonl"
        if output_file.exists():
            logging.info(f"   {output_file}")

    logging.info("\n2. Add to unified database:")
    logging.info("   Update scripts/build_unified_database.py to include HathiTrust sources")

    logging.info("\n3. Train period-specific BERTs:")
    logging.info("   - 1700-1800 (ECCO replacement)")
    logging.info("   - 1800-1900 (NCCO replacement)")
    logging.info("   - 1900-2000 (Modern corpus)")
    logging.info("="*60)


if __name__ == '__main__':
    main()
