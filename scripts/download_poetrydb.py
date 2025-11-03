#!/usr/bin/env python3
"""
Download Complete PoetryDB Dataset

Downloads all ~3,000 poems from PoetryDB API and saves as structured JSON.

Usage:
    python download_poetrydb.py --output Data/poetry_corpus/poetrydb.jsonl
"""

import requests
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class PoetryDBDownloader:
    """Download and structure PoetryDB corpus."""

    def __init__(self):
        self.base_url = "https://poetrydb.org"
        self.downloaded_poems = []
        self.failed = []

    def get_all_authors(self) -> List[str]:
        """Get list of all authors in PoetryDB."""
        logger.info("Fetching author list...")
        response = requests.get(f"{self.base_url}/author")
        data = response.json()
        authors = data['authors']
        logger.info(f"Found {len(authors)} authors")
        return authors

    def get_poems_by_author(self, author: str) -> List[Dict]:
        """Get all poems by a specific author."""
        try:
            # URL encode author name
            author_encoded = requests.utils.quote(author)
            url = f"{self.base_url}/author/{author_encoded}"

            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                poems = response.json()

                # Handle both list and dict responses
                if isinstance(poems, dict):
                    poems = [poems]

                logger.info(f"  {author}: {len(poems)} poems")
                return poems
            else:
                logger.warning(f"  {author}: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"  {author}: Error - {e}")
            self.failed.append(author)
            return []

    def add_metadata(self, poems: List[Dict]) -> List[Dict]:
        """Add period and genre metadata based on author."""

        # Period mapping (approximate)
        period_map = {
            'William Shakespeare': '1595-1700',
            'John Donne': '1595-1700',
            'Ben Jonson': '1595-1700',
            'Andrew Marvell': '1595-1700',
            'John Milton': '1595-1700',
            'Edmund Spenser': '1595-1700',

            'Alexander Pope': '1700-1800',
            'Jonathan Swift': '1700-1800',

            'William Wordsworth': '1800-1900',
            'Samuel Taylor Coleridge': '1800-1900',
            'John Keats': '1800-1900',
            'Percy Bysshe Shelley': '1800-1900',
            'George Gordon, Lord Byron': '1800-1900',
            'Alfred, Lord Tennyson': '1800-1900',
            'Robert Browning': '1800-1900',
            'Elizabeth Barrett Browning': '1800-1900',
            'Emily Dickinson': '1800-1900',
            'Walt Whitman': '1800-1900',
            'Christina Rossetti': '1800-1900',
            'Gerard Manley Hopkins': '1800-1900',
            'Matthew Arnold': '1800-1900',
            'Edgar Allan Poe': '1800-1900',

            'W. B. Yeats': '1900-2000',
            'T. S. Eliot': '1900-2000',
            'Robert Frost': '1900-2000',
            'Ezra Pound': '1900-2000',
        }

        for poem in poems:
            author = poem.get('author', 'Unknown')

            # Add period
            poem['period'] = period_map.get(author, 'unknown')

            # Infer genre from title (rough heuristic)
            title = poem.get('title', '').lower()
            if 'sonnet' in title:
                poem['genre'] = 'sonnet'
            elif 'ode' in title:
                poem['genre'] = 'ode'
            else:
                poem['genre'] = 'unknown'

            # Add ID
            poem['poem_id'] = f"{author.replace(' ', '_').lower()}_{poem.get('title', 'untitled').replace(' ', '_').lower()}"

        return poems

    def download_all(self, output_file: str, rate_limit: float = 0.5):
        """Download all poems from PoetryDB."""

        logger.info("="*60)
        logger.info("DOWNLOADING POETRYDB CORPUS")
        logger.info("="*60)

        # Get all authors
        authors = self.get_all_authors()

        # Download poems for each author
        logger.info(f"\nDownloading poems from {len(authors)} authors...")

        for i, author in enumerate(authors, 1):
            logger.info(f"[{i}/{len(authors)}] {author}")

            poems = self.get_poems_by_author(author)

            if poems:
                # Add metadata
                poems = self.add_metadata(poems)
                self.downloaded_poems.extend(poems)

            # Rate limiting
            time.sleep(rate_limit)

        # Save
        logger.info(f"\nSaving to {output_file}...")
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            for poem in self.downloaded_poems:
                f.write(json.dumps(poem) + '\n')

        # Summary
        logger.info("\n" + "="*60)
        logger.info("DOWNLOAD COMPLETE")
        logger.info("="*60)
        logger.info(f"Total poems: {len(self.downloaded_poems):,}")
        logger.info(f"Failed authors: {len(self.failed)}")
        if self.failed:
            logger.info(f"Failed: {', '.join(self.failed)}")

        # Period breakdown
        from collections import Counter
        periods = Counter(p['period'] for p in self.downloaded_poems)
        logger.info("\nPeriod breakdown:")
        for period, count in sorted(periods.items()):
            logger.info(f"  {period}: {count} poems")

        # Genre breakdown
        genres = Counter(p['genre'] for p in self.downloaded_poems)
        logger.info("\nGenre breakdown:")
        for genre, count in sorted(genres.items()):
            logger.info(f"  {genre}: {count} poems")

        logger.info(f"\n✓ Saved to: {output_file}")

        return len(self.downloaded_poems)


def main():
    parser = argparse.ArgumentParser(
        description="Download complete PoetryDB corpus"
    )
    parser.add_argument(
        '--output',
        default='Data/poetry_corpus/poetrydb.jsonl',
        help='Output JSONL file path'
    )
    parser.add_argument(
        '--rate_limit',
        type=float,
        default=0.5,
        help='Seconds to wait between requests (default: 0.5)'
    )

    args = parser.parse_args()

    downloader = PoetryDBDownloader()
    downloader.download_all(args.output, args.rate_limit)


if __name__ == '__main__':
    main()
