#!/usr/bin/env python3
"""
Download complete works of major English poets for career-arc analysis.
Extends Shakespeare pattern to build comprehensive historical poetry corpus.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Core poets with Gutenberg IDs for their major works
# Organized by period for period-specific analysis
CORE_POETS = [
    # EARLY MODERN (1500-1660)
    {
        'author': 'Edmund Spenser',
        'birth': 1552,
        'death': 1599,
        'period': 'early_modern',
        'works': [
            {'title': 'The Faerie Queene', 'date': 1590, 'genre': 'epic', 'gutenberg_id': 2759},
        ]
    },
    {
        'author': 'John Donne',
        'birth': 1572,
        'death': 1631,
        'period': 'early_modern',
        'works': [
            {'title': 'Poems', 'date': 1633, 'genre': 'lyric', 'gutenberg_id': 58820},
        ]
    },
    {
        'author': 'Ben Jonson',
        'birth': 1572,
        'death': 1637,
        'period': 'early_modern',
        'works': [
            {'title': 'Poems', 'date': 1616, 'genre': 'lyric', 'gutenberg_id': 52328},
        ]
    },
    {
        'author': 'George Herbert',
        'birth': 1593,
        'death': 1633,
        'period': 'early_modern',
        'works': [
            {'title': 'The Temple', 'date': 1633, 'genre': 'devotional', 'gutenberg_id': 18727},
        ]
    },
    {
        'author': 'John Milton',
        'birth': 1608,
        'death': 1674,
        'period': 'early_modern',
        'works': [
            {'title': 'Paradise Lost', 'date': 1667, 'genre': 'epic', 'gutenberg_id': 20},
            {'title': 'Paradise Regained', 'date': 1671, 'genre': 'epic', 'gutenberg_id': 58},
            {'title': 'Samson Agonistes', 'date': 1671, 'genre': 'drama', 'gutenberg_id': 58},
            {'title': 'Minor Poems', 'date': 1645, 'genre': 'lyric', 'gutenberg_id': 1745},
        ]
    },
    {
        'author': 'Andrew Marvell',
        'birth': 1621,
        'death': 1678,
        'period': 'early_modern',
        'works': [
            {'title': 'Poems', 'date': 1681, 'genre': 'lyric', 'gutenberg_id': 52188},
        ]
    },

    # RESTORATION/AUGUSTAN (1660-1780)
    {
        'author': 'John Dryden',
        'birth': 1631,
        'death': 1700,
        'period': 'restoration',
        'works': [
            {'title': 'Absalom and Achitophel', 'date': 1681, 'genre': 'satire', 'gutenberg_id': 18095},
            {'title': 'Poems', 'date': 1700, 'genre': 'various', 'gutenberg_id': 16396},
        ]
    },
    {
        'author': 'Alexander Pope',
        'birth': 1688,
        'death': 1744,
        'period': 'augustan',
        'works': [
            {'title': 'The Rape of the Lock', 'date': 1712, 'genre': 'mock_epic', 'gutenberg_id': 9800},
            {'title': 'An Essay on Man', 'date': 1733, 'genre': 'philosophical', 'gutenberg_id': 2428},
            {'title': 'The Dunciad', 'date': 1728, 'genre': 'satire', 'gutenberg_id': 11024},
        ]
    },
    {
        'author': 'Jonathan Swift',
        'birth': 1667,
        'death': 1745,
        'period': 'augustan',
        'works': [
            {'title': 'Poems', 'date': 1745, 'genre': 'satire', 'gutenberg_id': 15171},
        ]
    },
    {
        'author': 'Thomas Gray',
        'birth': 1716,
        'death': 1771,
        'period': 'augustan',
        'works': [
            {'title': 'Poems', 'date': 1768, 'genre': 'lyric', 'gutenberg_id': 2611},
        ]
    },

    # ROMANTIC (1780-1830)
    {
        'author': 'William Blake',
        'birth': 1757,
        'death': 1827,
        'period': 'romantic',
        'works': [
            {'title': 'Songs of Innocence and Experience', 'date': 1794, 'genre': 'lyric', 'gutenberg_id': 1934},
            {'title': 'The Marriage of Heaven and Hell', 'date': 1793, 'genre': 'prophetic', 'gutenberg_id': 45315},
        ]
    },
    {
        'author': 'William Wordsworth',
        'birth': 1770,
        'death': 1850,
        'period': 'romantic',
        'works': [
            {'title': 'Lyrical Ballads', 'date': 1798, 'genre': 'lyric', 'gutenberg_id': 8905},
            {'title': 'Poems, in Two Volumes', 'date': 1807, 'genre': 'lyric', 'gutenberg_id': 12145},
            {'title': 'The Prelude', 'date': 1850, 'genre': 'autobiography', 'gutenberg_id': 36881},
        ]
    },
    {
        'author': 'Samuel Taylor Coleridge',
        'birth': 1772,
        'death': 1834,
        'period': 'romantic',
        'works': [
            {'title': 'Lyrical Ballads (with Wordsworth)', 'date': 1798, 'genre': 'lyric', 'gutenberg_id': 8905},
            {'title': 'Christabel; Kubla Khan', 'date': 1816, 'genre': 'lyric', 'gutenberg_id': 8098},
        ]
    },
    {
        'author': 'Lord Byron',
        'birth': 1788,
        'death': 1824,
        'period': 'romantic',
        'works': [
            {'title': 'Don Juan', 'date': 1819, 'genre': 'epic_satire', 'gutenberg_id': 18762},
            {'title': 'Childe Harold\'s Pilgrimage', 'date': 1812, 'genre': 'narrative', 'gutenberg_id': 5131},
        ]
    },
    {
        'author': 'Percy Bysshe Shelley',
        'birth': 1792,
        'death': 1822,
        'period': 'romantic',
        'works': [
            {'title': 'Prometheus Unbound', 'date': 1820, 'genre': 'drama', 'gutenberg_id': 4667},
            {'title': 'The Revolt of Islam', 'date': 1818, 'genre': 'narrative', 'gutenberg_id': 13618},
            {'title': 'Poems', 'date': 1820, 'genre': 'lyric', 'gutenberg_id': 4800},
        ]
    },
    {
        'author': 'John Keats',
        'birth': 1795,
        'death': 1821,
        'period': 'romantic',
        'works': [
            {'title': 'Poems (1817)', 'date': 1817, 'genre': 'lyric', 'gutenberg_id': 2490},
            {'title': 'Endymion', 'date': 1818, 'genre': 'narrative', 'gutenberg_id': 24280},
            {'title': 'Lamia, Isabella, and Other Poems', 'date': 1820, 'genre': 'narrative', 'gutenberg_id': 23684},
        ]
    },

    # VICTORIAN (1830-1900)
    {
        'author': 'Alfred Tennyson',
        'birth': 1809,
        'death': 1892,
        'period': 'victorian',
        'works': [
            {'title': 'Poems (1842)', 'date': 1842, 'genre': 'lyric', 'gutenberg_id': 8601},
            {'title': 'In Memoriam', 'date': 1850, 'genre': 'elegy', 'gutenberg_id': 1799},
            {'title': 'Idylls of the King', 'date': 1859, 'genre': 'narrative', 'gutenberg_id': 610},
        ]
    },
    {
        'author': 'Robert Browning',
        'birth': 1812,
        'death': 1889,
        'period': 'victorian',
        'works': [
            {'title': 'Dramatic Lyrics', 'date': 1842, 'genre': 'dramatic_monologue', 'gutenberg_id': 574},
            {'title': 'Men and Women', 'date': 1855, 'genre': 'dramatic_monologue', 'gutenberg_id': 1287},
            {'title': 'The Ring and the Book', 'date': 1868, 'genre': 'narrative', 'gutenberg_id': 6915},
        ]
    },
    {
        'author': 'Elizabeth Barrett Browning',
        'birth': 1806,
        'death': 1861,
        'period': 'victorian',
        'works': [
            {'title': 'Sonnets from the Portuguese', 'date': 1850, 'genre': 'sonnet', 'gutenberg_id': 2002},
            {'title': 'Aurora Leigh', 'date': 1856, 'genre': 'verse_novel', 'gutenberg_id': 3844},
        ]
    },
    {
        'author': 'Matthew Arnold',
        'birth': 1822,
        'death': 1888,
        'period': 'victorian',
        'works': [
            {'title': 'Poems', 'date': 1869, 'genre': 'lyric', 'gutenberg_id': 2207},
        ]
    },
    {
        'author': 'Christina Rossetti',
        'birth': 1830,
        'death': 1894,
        'period': 'victorian',
        'works': [
            {'title': 'Goblin Market', 'date': 1862, 'genre': 'narrative', 'gutenberg_id': 2782},
        ]
    },
    {
        'author': 'Dante Gabriel Rossetti',
        'birth': 1828,
        'death': 1882,
        'period': 'victorian',
        'works': [
            {'title': 'Poems', 'date': 1870, 'genre': 'lyric', 'gutenberg_id': 17074},
        ]
    },
    {
        'author': 'Gerard Manley Hopkins',
        'birth': 1844,
        'death': 1889,
        'period': 'victorian',
        'works': [
            {'title': 'Poems', 'date': 1918, 'genre': 'lyric', 'gutenberg_id': 36996},
        ]
    },
    {
        'author': 'Algernon Charles Swinburne',
        'birth': 1837,
        'death': 1909,
        'period': 'victorian',
        'works': [
            {'title': 'Poems and Ballads', 'date': 1866, 'genre': 'lyric', 'gutenberg_id': 1718},
        ]
    },

    # AMERICAN (1800-1900)
    {
        'author': 'Walt Whitman',
        'birth': 1819,
        'death': 1892,
        'period': 'american',
        'works': [
            {'title': 'Leaves of Grass', 'date': 1855, 'genre': 'free_verse', 'gutenberg_id': 1322},
        ]
    },
    {
        'author': 'Emily Dickinson',
        'birth': 1830,
        'death': 1886,
        'period': 'american',
        'works': [
            {'title': 'Poems (1890)', 'date': 1890, 'genre': 'lyric', 'gutenberg_id': 12242},
            {'title': 'Poems: Second Series', 'date': 1891, 'genre': 'lyric', 'gutenberg_id': 12243},
            {'title': 'Poems: Third Series', 'date': 1896, 'genre': 'lyric', 'gutenberg_id': 12244},
        ]
    },
    {
        'author': 'Henry Wadsworth Longfellow',
        'birth': 1807,
        'death': 1882,
        'period': 'american',
        'works': [
            {'title': 'Evangeline', 'date': 1847, 'genre': 'narrative', 'gutenberg_id': 2039},
            {'title': 'The Song of Hiawatha', 'date': 1855, 'genre': 'narrative', 'gutenberg_id': 19},
            {'title': 'Tales of a Wayside Inn', 'date': 1863, 'genre': 'narrative', 'gutenberg_id': 2337},
        ]
    },
    {
        'author': 'Edgar Allan Poe',
        'birth': 1809,
        'death': 1849,
        'period': 'american',
        'works': [
            {'title': 'The Raven and Other Poems', 'date': 1845, 'genre': 'lyric', 'gutenberg_id': 17192},
        ]
    },
]


class CorePoetsCorpusBuilder:
    """Build comprehensive multi-poet corpus with career metadata."""

    def __init__(self, output_dir: str = "Data/poetry_corpus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://www.gutenberg.org/cache/epub"

    def download_work(self, author: Dict, work: Dict) -> Optional[Dict]:
        """Download a single work from Project Gutenberg."""
        try:
            url = f"{self.base_url}/{work['gutenberg_id']}/pg{work['gutenberg_id']}.txt"
            logging.info(f"  Downloading: {work['title']} ({work['date']})")

            with urlopen(url, timeout=30) as response:
                text = response.read().decode('utf-8', errors='replace')

            text = self.clean_gutenberg_text(text)
            lines = text.split('\n')

            # Calculate author career period
            author_age_at_composition = work['date'] - author['birth']
            author_lifespan = author['death'] - author['birth']
            career_position = author_age_at_composition / author_lifespan

            if career_position < 0.33:
                career_period = 'early'
            elif career_position < 0.66:
                career_period = 'middle'
            else:
                career_period = 'late'

            title_slug = work['title'].lower().replace(' ', '_').replace(',', '').replace("'", '').replace('(', '').replace(')', '')
            author_slug = author['author'].lower().replace(' ', '_').replace('.', '').replace(',', '')

            return {
                'work_id': f"{author_slug}_{work['date']}_{title_slug}",
                'title': work['title'],
                'author': author['author'],
                'author_birth': author['birth'],
                'author_death': author['death'],
                'composition_date': work['date'],
                'period': author['period'],
                'author_career_period': career_period,
                'genre': work['genre'],
                'gutenberg_id': work['gutenberg_id'],
                'text': text,
                'lines': lines,
                'line_count': len(lines),
            }

        except Exception as e:
            logging.warning(f"  Failed: {e}")
            return None

    def clean_gutenberg_text(self, text: str) -> str:
        """Remove Project Gutenberg header and footer."""
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG",
            "*** START OF THIS PROJECT GUTENBERG",
        ]
        for marker in start_markers:
            if marker in text:
                text = text.split(marker)[1]
                text = '\n'.join(text.split('\n')[1:])
                break

        end_markers = [
            "*** END OF THE PROJECT GUTENBERG",
            "*** END OF THIS PROJECT GUTENBERG",
            "End of the Project Gutenberg",
        ]
        for marker in end_markers:
            if marker in text:
                text = text.split(marker)[0]
                break

        return text.strip()

    def build_corpus(self) -> List[Dict]:
        """Download all works from all poets."""
        corpus = []

        logging.info("="*60)
        logging.info("BUILDING CORE POETS CORPUS")
        logging.info("="*60)
        logging.info(f"Total poets: {len(CORE_POETS)}")
        total_works = sum(len(poet['works']) for poet in CORE_POETS)
        logging.info(f"Total works: {total_works}\n")

        work_num = 0
        for poet_idx, poet in enumerate(CORE_POETS):
            logging.info(f"[{poet_idx+1}/{len(CORE_POETS)}] {poet['author']} ({poet['birth']}-{poet['death']}, {poet['period']})")

            for work in poet['works']:
                work_num += 1
                work_data = self.download_work(poet, work)
                if work_data:
                    corpus.append(work_data)

        return corpus

    def save_corpus(self, corpus: List[Dict]):
        """Save corpus in multiple formats."""
        # Complete corpus
        output_file = self.output_dir / 'core_poets_complete.jsonl'
        with open(output_file, 'w', encoding='utf-8') as f:
            for work in corpus:
                f.write(json.dumps(work, ensure_ascii=False) + '\n')
        logging.info(f"\n✓ Saved complete corpus to: {output_file}")

        # By period
        for period in ['early_modern', 'restoration', 'augustan', 'romantic', 'victorian', 'american']:
            period_works = [w for w in corpus if w['period'] == period]
            if period_works:
                output_file = self.output_dir / f'core_poets_{period}.jsonl'
                with open(output_file, 'w', encoding='utf-8') as f:
                    for work in period_works:
                        f.write(json.dumps(work, ensure_ascii=False) + '\n')
                logging.info(f"✓ Saved {len(period_works)} {period} works to: {output_file}")

    def generate_summary(self, corpus: List[Dict]):
        """Generate corpus statistics."""
        logging.info("\n" + "="*60)
        logging.info("CORPUS SUMMARY")
        logging.info("="*60)
        logging.info(f"Total works: {len(corpus)}")

        # By period
        logging.info("\nBy historical period:")
        for period in ['early_modern', 'restoration', 'augustan', 'romantic', 'victorian', 'american']:
            works = [w for w in corpus if w['period'] == period]
            if works:
                dates = [w['composition_date'] for w in works]
                logging.info(f"  {period}: {len(works)} works ({min(dates)}-{max(dates)})")

        # By genre
        logging.info("\nBy genre:")
        genres = {}
        for work in corpus:
            genre = work['genre']
            genres[genre] = genres.get(genre, 0) + 1
        for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
            logging.info(f"  {genre}: {count} works")

        # Total lines
        total_lines = sum(w['line_count'] for w in corpus)
        logging.info(f"\nTotal lines: {total_lines:,}")

        # Poets
        authors = set(w['author'] for w in corpus)
        logging.info(f"Unique authors: {len(authors)}")


def main():
    builder = CorePoetsCorpusBuilder()
    corpus = builder.build_corpus()
    builder.save_corpus(corpus)
    builder.generate_summary(corpus)

    logging.info("\n" + "="*60)
    logging.info("USAGE")
    logging.info("="*60)
    logging.info("""
This corpus enables:

1. Career-arc analysis (early/middle/late for each author)
2. Period comparisons (romantic vs. victorian blank verse)
3. Genre tracking (emergence of dramatic monologue)
4. Formal feature evolution (enjambment, feminine endings, caesura)

Load and analyze:
    import json
    with open('Data/poetry_corpus/core_poets_complete.jsonl') as f:
        corpus = [json.loads(line) for line in f]

Track feature across Romantic period:
    romantic_works = [w for w in corpus if w['period'] == 'romantic']
    # Run prosodic analysis on each work
    """)


if __name__ == '__main__':
    main()
