#!/usr/bin/env python3
"""
Download Historical Corpus from HathiTrust Research Center

Uses HTRC Data API to download texts by period for BERT training.
Filters by date range, language, and OCR quality.

Periods:
- ECCO replacement: 1700-1800
- NCCO replacement: 1800-1900
- Modern: 1900-2000

Output: JSONL files compatible with unified database pipeline
"""

import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class HathiTrustDownloader:
    """Download texts from HathiTrust using HTRC API."""

    # HTRC Data API endpoints
    SOLR_API = "https://catalog.hathitrust.org/api/volumes/brief/json"
    HTRC_DATA_API = "https://data.analytics.hathitrust.org/features"

    def __init__(self, output_dir: str, min_ocr_quality: float = 0.90):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_ocr_quality = min_ocr_quality
        self.session = requests.Session()
        self.failed_downloads = []

    def search_by_period(self, start_year: int, end_year: int,
                         max_results: int = 10000) -> List[str]:
        """
        Search HathiTrust catalog for volumes in date range.

        Returns list of HathiTrust volume IDs.
        """
        logging.info(f"Searching HathiTrust for {start_year}-{end_year}...")

        # Build Solr query
        # Note: This uses HathiTrust's public Solr API
        # For bulk downloads, you may need HTRC worksets instead

        query_params = {
            'q': f'publishDate:[{start_year} TO {end_year}] AND language:eng',
            'fl': 'id,title,author,publishDate',
            'rows': max_results,
            'wt': 'json'
        }

        # Note: You'll need to use the Bibliographic API or Worksets
        # This is a placeholder - actual implementation depends on access method

        logging.warning("This script requires HTRC workset access or rsync credentials")
        logging.warning("See instructions below for setup")

        return []

    def download_volume(self, volume_id: str) -> Optional[Dict]:
        """
        Download full text for a HathiTrust volume.

        Note: Requires HTRC Data API access or rsync credentials.
        """
        try:
            # HTRC Data API provides extracted features, not full text
            # For full text, need:
            # 1. rsync access for bulk downloads, OR
            # 2. HTRC Data Capsule for in-copyright texts, OR
            # 3. Individual page downloads for public domain

            # Placeholder - actual implementation depends on access method
            logging.warning(f"Volume {volume_id}: Full text download requires setup")

            return None

        except Exception as e:
            logging.error(f"Failed to download {volume_id}: {e}")
            self.failed_downloads.append(volume_id)
            return None

    def assess_ocr_quality(self, text: str) -> float:
        """
        Estimate OCR quality from text characteristics.

        Returns confidence score 0.0-1.0.
        """
        if not text or len(text) < 100:
            return 0.0

        # Count suspicious patterns
        total_chars = len(text)

        # Common OCR errors
        rn_to_m = text.count('rn') / total_chars if total_chars > 0 else 0
        cl_to_d = text.count('cl') / total_chars if total_chars > 0 else 0

        # Check for gibberish (non-alphabetic ratio in "words")
        words = text.split()
        if not words:
            return 0.0

        valid_words = sum(1 for w in words if w.isalpha() and len(w) > 1)
        word_quality = valid_words / len(words) if words else 0.0

        # Combine metrics
        ocr_score = word_quality * 0.7 + (1.0 - rn_to_m * 100) * 0.15 + (1.0 - cl_to_d * 100) * 0.15

        return max(0.0, min(1.0, ocr_score))

    def save_corpus(self, volumes: List[Dict], period: str):
        """Save downloaded volumes to JSONL."""
        output_file = self.output_dir / f"hathitrust_{period}.jsonl"

        logging.info(f"Saving {len(volumes)} volumes to {output_file}...")

        with open(output_file, 'w', encoding='utf-8') as f:
            for vol in volumes:
                f.write(json.dumps(vol, ensure_ascii=False) + '\n')

        logging.info(f"✓ Saved to {output_file}")


def print_setup_instructions():
    """Print instructions for HathiTrust access setup."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                  HATHITRUST SETUP INSTRUCTIONS                       ║
╚══════════════════════════════════════════════════════════════════════╝

This script requires HathiTrust Research Center (HTRC) access.

OPTION 1: HTRC Analytics Portal (Recommended for IU users)
────────────────────────────────────────────────────────────────────────

1. Go to: https://analytics.hathitrust.org
2. Log in with IU credentials
3. Create a Workset:
   - Click "Worksets" or "Collections"
   - Search for texts by date range and subject
   - Example query: "language:eng AND publishDate:[1700 TO 1800]"
   - Save as workset

4. Export Workset:
   - Select your workset
   - Click "Export" or "Download"
   - Choose format: "Plain text" or "Page-level OCR"
   - Download to: /Users/justin/Repos/AI Project/Data/hathitrust/

5. Update this script with workset ID or volume IDs

OPTION 2: HTRC Data API
────────────────────────────────────────────────────────────────────────

1. Get HTRC credentials:
   - Email: htrc-help@hathitrust.org
   - Request: Data API access for computational research

2. Install HTRC Python library:
   pip install htrc-feature-reader

3. Update this script with your API credentials

OPTION 3: Rsync Bulk Downloads (For large-scale access)
────────────────────────────────────────────────────────────────────────

1. Email: htrc-help@hathitrust.org
   Subject: Rsync Access for Computational Research

2. Provide:
   - Research description (BERT training on historical texts)
   - Institutional affiliation (IU Center for Possible Minds)
   - Expected corpus size

3. Receive rsync credentials and server address

4. Download with rsync:
   rsync -av htrc@server:/path/to/texts ./Data/hathitrust/

MANUAL ALTERNATIVE (Small-scale testing)
────────────────────────────────────────────────────────────────────────

For testing with 10-20 books:

1. Go to: https://www.hathitrust.org
2. Search for books (e.g., "poetry 1700-1800")
3. For each public domain book:
   - Click book title
   - Click "Download" → "Plain text OCR"
   - Save to Data/hathitrust/raw/

4. Run preprocessing script (we'll create this next)

RECOMMENDED APPROACH FOR YOUR PROJECT
────────────────────────────────────────────────────────────────────────

Start with Analytics Portal:
1. Create 3 worksets (1700-1800, 1800-1900, 1900-2000)
2. Export small test set (100 books each)
3. Verify OCR quality
4. Scale up to full corpus (thousands of books)

Then use rsync for bulk downloads if needed.

═══════════════════════════════════════════════════════════════════════

Next steps:
1. Visit https://analytics.hathitrust.org
2. Create a test workset
3. Export and download 10-20 books
4. Run: python scripts/preprocess_hathitrust_downloads.py

Questions? Email: htrc-help@hathitrust.org
""")


def main():
    """Main entry point - setup wizard."""

    print_setup_instructions()

    print("\n" + "="*70)
    print("SETUP STATUS CHECK")
    print("="*70)

    # Check if user has downloaded anything yet
    data_dir = Path("/Users/justin/Repos/AI Project/Data/hathitrust")

    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✓ Created directory: {data_dir}")

    # Check for workset files
    raw_dir = data_dir / "raw"
    worksets_dir = data_dir / "worksets"

    for d in [raw_dir, worksets_dir]:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Data directories ready:")
    print(f"   Raw downloads: {raw_dir}")
    print(f"   Worksets: {worksets_dir}")

    # Check for existing downloads
    existing_files = list(raw_dir.glob("*.txt")) + list(raw_dir.glob("*.zip"))

    if existing_files:
        print(f"\n✓ Found {len(existing_files)} downloaded files")
        print("\nReady to run preprocessing:")
        print("  python scripts/preprocess_hathitrust_downloads.py")
    else:
        print("\n⚠ No downloads found yet")
        print("\nNext steps:")
        print("1. Visit https://analytics.hathitrust.org")
        print("2. Create a workset for your period (1700-1800, etc.)")
        print("3. Download to:", raw_dir)
        print("4. Re-run this script")

    print("\n" + "="*70)


if __name__ == '__main__':
    main()
