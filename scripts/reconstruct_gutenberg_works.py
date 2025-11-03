#!/usr/bin/env python3
"""
Reconstruct Gutenberg Poetry Corpus into Complete Works with Metadata

Input: gutenberg_poetry_corpus_clean.jsonl (line-by-line)
Output: gutenberg_reconstructed.jsonl (complete works with metadata)

Fetches metadata from Gutenberg catalog for each work.
"""

import json
import logging
import re
import requests
import time
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class GutenbergReconstructor:
    """Reconstruct complete works from line-level Gutenberg corpus."""

    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.metadata_cache = {}
        self.failed_ids = []

    def fetch_gutenberg_metadata(self, gutenberg_id: int) -> Optional[Dict]:
        """Fetch metadata from Gutenberg RDF catalog."""

        # Check cache
        if gutenberg_id in self.metadata_cache:
            return self.metadata_cache[gutenberg_id]

        try:
            # Try Gutenberg RDF API
            url = f"https://www.gutenberg.org/ebooks/{gutenberg_id}.rdf"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                rdf_data = response.text

                # Extract metadata from RDF (simple regex parsing)
                metadata = {
                    'gutenberg_id': gutenberg_id,
                    'title': self._extract_rdf_field(rdf_data, 'dcterms:title'),
                    'author': self._extract_rdf_field(rdf_data, 'pgterms:name'),
                    'publication_date': self._extract_rdf_field(rdf_data, 'dcterms:issued'),
                    'language': self._extract_rdf_field(rdf_data, 'dcterms:language'),
                    'subjects': self._extract_rdf_subjects(rdf_data),
                }

                self.metadata_cache[gutenberg_id] = metadata
                return metadata
            else:
                logging.warning(f"Failed to fetch metadata for ID {gutenberg_id}: HTTP {response.status_code}")

        except Exception as e:
            logging.warning(f"Error fetching metadata for ID {gutenberg_id}: {e}")

        self.failed_ids.append(gutenberg_id)
        return None

    def _extract_rdf_field(self, rdf_data: str, field_name: str) -> Optional[str]:
        """Extract field from RDF using regex."""
        # Try different RDF patterns
        patterns = [
            f'<{field_name}>([^<]+)</{field_name}>',
            f'<{field_name} rdf:resource="[^"]*">([^<]+)',
            f'{field_name}="([^"]+)"',
        ]

        for pattern in patterns:
            match = re.search(pattern, rdf_data)
            if match:
                return match.group(1).strip()
        return None

    def _extract_rdf_subjects(self, rdf_data: str) -> List[str]:
        """Extract subject headings from RDF."""
        subjects = []
        # Look for subject tags
        subject_pattern = r'<dcterms:subject>.*?<rdf:value>([^<]+)</rdf:value>'
        matches = re.findall(subject_pattern, rdf_data, re.DOTALL)
        return [m.strip() for m in matches]

    def guess_period_from_date(self, date: Optional[str]) -> str:
        """Guess historical period from publication date."""
        if not date:
            return 'unknown'

        # Extract year from various date formats
        year_match = re.search(r'\b(1[4-9]\d{2}|20\d{2})\b', str(date))
        if not year_match:
            return 'unknown'

        year = int(year_match.group(1))

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

    def reconstruct_works(self) -> List[Dict]:
        """Group lines by gutenberg_id and reconstruct complete works."""

        logging.info(f"Reading lines from {self.input_path}...")

        # Group lines by gutenberg_id
        works_lines = defaultdict(list)

        with open(self.input_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Grouping lines"):
                data = json.loads(line)
                works_lines[data['gutenberg_id']].append(data)

        logging.info(f"Found {len(works_lines)} unique Gutenberg IDs")

        # Reconstruct complete works
        reconstructed_works = []

        for gutenberg_id, lines in tqdm(works_lines.items(), desc="Reconstructing works"):
            # Sort lines by line_num
            lines.sort(key=lambda x: x['line_num'])

            # Fetch metadata
            metadata = self.fetch_gutenberg_metadata(gutenberg_id)

            # Combine lines into text
            text_lines = [line['line'] for line in lines]
            full_text = '\n'.join(text_lines)

            # Extract publication year
            pub_date = None
            if metadata and metadata.get('publication_date'):
                year_match = re.search(r'\b(1[4-9]\d{2}|20\d{2})\b', metadata['publication_date'])
                if year_match:
                    pub_date = int(year_match.group(1))

            # Create work entry
            work = {
                'work_id': f"gutenberg_{gutenberg_id}",
                'title': metadata['title'] if metadata else f"Gutenberg Text {gutenberg_id}",
                'author': metadata['author'] if metadata else None,
                'gutenberg_id': gutenberg_id,
                'publication_date': pub_date,
                'composition_date': None,  # Usually same as publication for Gutenberg
                'period': self.guess_period_from_date(pub_date),
                'source': 'gutenberg',
                'text': full_text,
                'lines': text_lines,
                'line_count': len([l for l in lines if not l['is_blank']]),
                'metadata_complete': metadata is not None,
                'subjects': metadata.get('subjects', []) if metadata else [],
            }

            reconstructed_works.append(work)

            # Rate limiting
            time.sleep(0.1)

        return reconstructed_works

    def save_works(self, works: List[Dict]):
        """Save reconstructed works to JSONL."""
        logging.info(f"Saving {len(works)} works to {self.output_path}...")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            for work in works:
                f.write(json.dumps(work, ensure_ascii=False) + '\n')

        logging.info(f"✓ Saved to {self.output_path}")

        # Summary
        with_metadata = sum(1 for w in works if w['metadata_complete'])
        logging.info(f"\nSummary:")
        logging.info(f"  Total works: {len(works)}")
        logging.info(f"  With metadata: {with_metadata} ({with_metadata/len(works)*100:.1f}%)")
        logging.info(f"  Failed metadata fetches: {len(self.failed_ids)}")

        # Period breakdown
        periods = defaultdict(int)
        for work in works:
            periods[work['period']] += 1

        logging.info(f"\nBy period:")
        for period, count in sorted(periods.items()):
            logging.info(f"  {period}: {count} works")


def main():
    input_file = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/Historical Embeddings/gutenberg_poetry_corpus_clean.jsonl"
    output_file = "/Users/justin/Repos/AI Project/Data/gutenberg_reconstructed.jsonl"

    reconstructor = GutenbergReconstructor(input_file, output_file)

    logging.info("="*60)
    logging.info("GUTENBERG CORPUS RECONSTRUCTION")
    logging.info("="*60)

    # Reconstruct works
    works = reconstructor.reconstruct_works()

    # Save
    reconstructor.save_works(works)

    logging.info("\n" + "="*60)
    logging.info("RECONSTRUCTION COMPLETE")
    logging.info("="*60)


if __name__ == '__main__':
    main()
