#!/usr/bin/env python3
"""
Download HathiTrust volumes from CSV of volume IDs

Takes a CSV with HathiTrust volume IDs and downloads full text.
Requires HTRC access or uses HathiTrust Data API.

Input: CSV with columns: id, title, year, language, authors
Output: Downloaded texts in Data/hathitrust/raw/
"""

import csv
import json
import logging
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


class HathiTrustCSVDownloader:
    """Download HathiTrust volumes from CSV of IDs."""

    # HathiTrust Bibliographic API
    BIB_API = "https://catalog.hathitrust.org/api/volumes/brief/htid/{htid}.json"

    # HathiTrust Data API (requires authentication)
    DATA_API = "https://data.analytics.hathitrust.org/features"

    def __init__(self, csv_path: str, output_dir: str):
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.downloaded = 0
        self.failed = []
        self.metadata = []

    def read_csv(self) -> List[Dict]:
        """Read CSV of HathiTrust volume IDs."""
        volumes = []

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                volumes.append(row)

        logging.info(f"Read {len(volumes)} volumes from {self.csv_path}")
        return volumes

    def get_volume_metadata(self, htid: str) -> Optional[Dict]:
        """
        Get volume metadata from HathiTrust Bibliographic API.

        This returns metadata only, not full text.
        """
        try:
            url = self.BIB_API.format(htid=htid)
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data
            else:
                logging.warning(f"Failed to get metadata for {htid}: {response.status_code}")
                return None

        except Exception as e:
            logging.error(f"Error getting metadata for {htid}: {e}")
            return None

    def download_volume_text(self, htid: str, title: str, year: str) -> bool:
        """
        Download full text for a volume.

        NOTE: This is where we hit the main challenge:
        HathiTrust does NOT provide a simple public API for full text download.

        Options:
        1. HTRC Data Capsule (requires setup)
        2. HTRC Extracted Features API (features only, not full text)
        3. Manual download from HathiTrust website (1 by 1)
        4. Institution-specific bulk access (need credentials)
        """

        # Option 1: Try HTRC Extracted Features (NOT full text, but useful)
        # This gives you word counts, POS tags, etc. but not the actual text

        logging.warning(f"Full text download not available via public API for {htid}")
        logging.info(f"Title: {title} ({year})")

        # Save metadata for manual download list
        self.metadata.append({
            'htid': htid,
            'title': title,
            'year': year,
            'download_url': f"https://babel.hathitrust.org/cgi/pt?id={htid}"
        })

        return False

    def process_csv(self):
        """Process all volumes in CSV."""

        volumes = self.read_csv()

        logging.info("="*60)
        logging.info("IMPORTANT: HathiTrust Full Text Download")
        logging.info("="*60)
        logging.info("")
        logging.info("This CSV contains volume IDs, but HathiTrust does NOT provide")
        logging.info("a public API for bulk full-text download.")
        logging.info("")
        logging.info("You have THREE options:")
        logging.info("")
        logging.info("OPTION 1: Use HathiTrust Analytics Portal (RECOMMENDED)")
        logging.info("  1. Go to https://analytics.hathitrust.org")
        logging.info("  2. Create a workset from this CSV")
        logging.info("  3. Export workset as plain text")
        logging.info("  4. Download the exported files")
        logging.info("")
        logging.info("OPTION 2: Request HTRC Data Capsule Access")
        logging.info("  Email: htrc-help@hathitrust.org")
        logging.info("  Request: Bulk download access for research")
        logging.info("  They may provide rsync credentials")
        logging.info("")
        logging.info("OPTION 3: Manual Download (NOT RECOMMENDED)")
        logging.info("  Visit each URL individually and download")
        logging.info("  Time-consuming for large collections")
        logging.info("")
        logging.info("="*60)

        # Generate a manifest file for Analytics Portal upload
        manifest_path = self.output_dir / "volume_manifest.txt"

        with open(manifest_path, 'w') as f:
            for vol in volumes:
                # HathiTrust Analytics Portal expects volume IDs in specific format
                f.write(vol['id'] + '\n')

        logging.info(f"\n✓ Created volume manifest: {manifest_path}")
        logging.info(f"  Total volumes: {len(volumes)}")
        logging.info("")
        logging.info("NEXT STEPS:")
        logging.info("1. Go to https://analytics.hathitrust.org")
        logging.info("2. Log in with IU credentials")
        logging.info("3. Click 'Worksets' → 'Create New Workset'")
        logging.info(f"4. Upload this file: {manifest_path}")
        logging.info("5. Export workset as plain text")
        logging.info("6. Download to Data/hathitrust/raw/")
        logging.info("7. Run: python scripts/preprocess_hathitrust_downloads.py")

        # Also create a summary JSON
        summary_path = self.output_dir / "csv_summary.json"

        summary = {
            'total_volumes': len(volumes),
            'date_range': {
                'earliest': min(int(v['year']) for v in volumes if v['year'].isdigit()),
                'latest': max(int(v['year']) for v in volumes if v['year'].isdigit())
            },
            'languages': list(set(v['language'] for v in volumes)),
            'sample_titles': [v['title'][:80] for v in volumes[:10]]
        }

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        logging.info(f"\n✓ Created summary: {summary_path}")

        # Create a URLs file for reference
        urls_path = self.output_dir / "volume_urls.txt"

        with open(urls_path, 'w') as f:
            f.write("# HathiTrust Volume URLs\n")
            f.write("# You can visit these individually if needed\n\n")
            for vol in volumes[:20]:  # First 20 for manual check
                url = f"https://babel.hathitrust.org/cgi/pt?id={vol['id']}"
                f.write(f"{vol['title'][:60]}\n")
                f.write(f"{url}\n\n")

        logging.info(f"✓ Created URL list: {urls_path}")
        logging.info("\n" + "="*60)


def main():
    """Main entry point."""

    import sys

    if len(sys.argv) < 2:
        print("Usage: python download_from_hathitrust_csv.py <csv_file>")
        print("\nExample:")
        print("  python download_from_hathitrust_csv.py '/Users/justin/Desktop/valid_volumes (2).csv'")
        sys.exit(1)

    csv_path = sys.argv[1]
    output_dir = "/Users/justin/Repos/AI Project/Data/hathitrust/raw"

    downloader = HathiTrustCSVDownloader(csv_path, output_dir)
    downloader.process_csv()


if __name__ == '__main__':
    main()
