#!/usr/bin/env python3
"""
Build Unified Poetry Database

Combines all poetry sources into a single SQLite database:
- Shakespeare (40 works, 181K lines)
- Core 27 Poets (51 works, 470K lines)
- PoetryDB (3,162 poems)
- Gutenberg (1,191 works, 5.5M lines)

Total: ~4,444 works, ~6.2M lines
"""

import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class UnifiedDatabaseBuilder:
    """Build unified SQLite database from all poetry sources."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None

    def create_schema(self):
        """Create unified database schema."""

        logging.info("Creating database schema...")

        # Works table (one row per complete work)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS works (
                work_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT,
                first_appearance_date INTEGER,  -- First publication/performance date
                publication_date INTEGER,
                composition_date INTEGER,
                period TEXT,
                genre TEXT,
                source TEXT NOT NULL,
                line_count INTEGER,
                metadata_complete BOOLEAN,
                full_text TEXT,

                -- Standardized taxonomies
                career_period TEXT,  -- early, middle, late, final

                -- Source-specific IDs
                gutenberg_id INTEGER,
                poetrydb_id TEXT,

                -- Searchability
                title_normalized TEXT,
                author_normalized TEXT
            )
        """)

        # Lines table (one row per line of poetry)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS lines (
                line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_id TEXT NOT NULL,
                line_num INTEGER NOT NULL,
                line_text TEXT NOT NULL,
                is_blank BOOLEAN DEFAULT FALSE,

                -- Prosodic features (to be populated later)
                meter TEXT,
                feet INTEGER,
                stresses TEXT,
                rhyme_scheme TEXT,

                FOREIGN KEY (work_id) REFERENCES works(work_id)
            )
        """)

        # Authors table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                author_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_normalized TEXT,
                birth_year INTEGER,
                death_year INTEGER,
                period TEXT,
                work_count INTEGER
            )
        """)

        # Metadata table (flexible key-value for source-specific metadata)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                work_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                PRIMARY KEY (work_id, key),
                FOREIGN KEY (work_id) REFERENCES works(work_id)
            )
        """)

        # Create indexes for fast queries
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_works_author ON works(author)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_works_period ON works(period)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_works_genre ON works(genre)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_works_source ON works(source)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_lines_work ON lines(work_id)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_lines_text ON lines(line_text)")

        self.conn.commit()
        logging.info("✓ Schema created")

    def normalize_text(self, text: str) -> str:
        """Normalize text for searching (lowercase, strip punctuation)."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def import_gutenberg(self, input_path: str):
        """Import Gutenberg reconstructed works."""

        input_path = Path(input_path)
        logging.info(f"Importing Gutenberg from {input_path}...")

        works = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="Reading Gutenberg"):
                works.append(json.loads(line))

        logging.info(f"Inserting {len(works)} Gutenberg works...")

        for work in tqdm(works, desc="Importing Gutenberg"):
            # Insert work
            pub_date = work.get('publication_date')
            self.cursor.execute("""
                INSERT OR IGNORE INTO works (
                    work_id, title, author, first_appearance_date, publication_date,
                    composition_date, period, genre, source, line_count,
                    metadata_complete, full_text, gutenberg_id,
                    title_normalized, author_normalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work['work_id'],
                work['title'],
                work.get('author'),
                pub_date,  # First appearance = publication for Gutenberg
                pub_date,
                work.get('composition_date'),
                work.get('period', 'unknown'),
                'poetry',  # All Gutenberg corpus is poetry
                work['source'],
                work['line_count'],
                work.get('metadata_complete', False),
                work.get('text'),
                work['gutenberg_id'],
                self.normalize_text(work['title']),
                self.normalize_text(work.get('author', ''))
            ))

            # Insert lines
            for i, line_text in enumerate(work['lines'], 1):
                is_blank = len(line_text.strip()) == 0
                self.cursor.execute("""
                    INSERT INTO lines (work_id, line_num, line_text, is_blank)
                    VALUES (?, ?, ?, ?)
                """, (work['work_id'], i, line_text, is_blank))

            # Insert subjects as metadata
            if 'subjects' in work:
                for subject in work['subjects']:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO metadata (work_id, key, value)
                        VALUES (?, ?, ?)
                    """, (work['work_id'], 'subject', subject))

        self.conn.commit()
        logging.info(f"✓ Imported {len(works)} Gutenberg works")

    def import_shakespeare(self, input_path: str):
        """Import Shakespeare corpus."""

        input_path = Path(input_path)
        if not input_path.exists():
            logging.warning(f"Shakespeare corpus not found at {input_path}")
            return

        logging.info(f"Importing Shakespeare from {input_path}...")

        works = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                works.append(json.loads(line))

        logging.info(f"Inserting {len(works)} Shakespeare works...")

        for work in tqdm(works, desc="Importing Shakespeare"):
            # Determine career period from date
            career_period = self.guess_shakespeare_career_period(work.get('date'))

            # Insert work
            date = work.get('date')
            self.cursor.execute("""
                INSERT OR IGNORE INTO works (
                    work_id, title, author, first_appearance_date, publication_date,
                    composition_date, period, genre, source, line_count,
                    metadata_complete, full_text, career_period,
                    title_normalized, author_normalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work['work_id'],
                work['title'],
                'William Shakespeare',
                date,  # First appearance
                date,  # Publication
                date,  # Composition
                'early_modern',
                work.get('genre', 'drama'),
                work['source'],
                work.get('line_count', 0),
                True,
                work.get('text'),
                career_period,
                self.normalize_text(work['title']),
                self.normalize_text('William Shakespeare')
            ))

            # Insert lines if available
            if 'lines' in work:
                for i, line_text in enumerate(work['lines'], 1):
                    is_blank = len(line_text.strip()) == 0
                    self.cursor.execute("""
                        INSERT INTO lines (work_id, line_num, line_text, is_blank)
                        VALUES (?, ?, ?, ?)
                    """, (work['work_id'], i, line_text, is_blank))

        self.conn.commit()
        logging.info(f"✓ Imported {len(works)} Shakespeare works")

    def guess_shakespeare_career_period(self, year: Optional[int]) -> str:
        """Map Shakespeare work to career period."""
        if not year:
            return 'unknown'

        if year < 1594:
            return 'early'
        elif year < 1601:
            return 'middle'
        elif year < 1608:
            return 'late'
        else:
            return 'final'

    def import_core_poets(self, input_path: str):
        """Import Core 27 Poets corpus."""

        input_path = Path(input_path)
        if not input_path.exists():
            logging.warning(f"Core poets corpus not found at {input_path}")
            return

        logging.info(f"Importing Core Poets from {input_path}...")

        works = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                works.append(json.loads(line))

        logging.info(f"Inserting {len(works)} Core Poets works...")

        for work in tqdm(works, desc="Importing Core Poets"):
            pub_date = work.get('publication_date')
            self.cursor.execute("""
                INSERT OR IGNORE INTO works (
                    work_id, title, author, first_appearance_date, publication_date,
                    composition_date, period, genre, source, line_count,
                    metadata_complete, full_text, title_normalized, author_normalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work['work_id'],
                work['title'],
                work['author'],
                pub_date,  # First appearance
                pub_date,
                work.get('composition_date'),
                work.get('period', 'unknown'),
                work.get('genre', 'poetry'),
                work['source'],
                work.get('line_count', 0),
                work.get('metadata_complete', True),
                work.get('text'),
                self.normalize_text(work['title']),
                self.normalize_text(work['author'])
            ))

            # Insert lines if available
            if 'lines' in work:
                for i, line_text in enumerate(work['lines'], 1):
                    is_blank = len(line_text.strip()) == 0
                    self.cursor.execute("""
                        INSERT INTO lines (work_id, line_num, line_text, is_blank)
                        VALUES (?, ?, ?, ?)
                    """, (work['work_id'], i, line_text, is_blank))

        self.conn.commit()
        logging.info(f"✓ Imported {len(works)} Core Poets works")

    def import_poetrydb(self, input_path: str):
        """Import PoetryDB corpus."""

        input_path = Path(input_path)
        if not input_path.exists():
            logging.warning(f"PoetryDB corpus not found at {input_path}")
            return

        logging.info(f"Importing PoetryDB from {input_path}...")

        works = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                works.append(json.loads(line))

        logging.info(f"Inserting {len(works)} PoetryDB works...")

        for work in tqdm(works, desc="Importing PoetryDB"):
            pub_date = work.get('publication_date')
            self.cursor.execute("""
                INSERT OR IGNORE INTO works (
                    work_id, title, author, first_appearance_date, publication_date,
                    period, genre, source, line_count, metadata_complete, full_text,
                    poetrydb_id, title_normalized, author_normalized
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                work['work_id'],
                work['title'],
                work['author'],
                pub_date,  # First appearance
                pub_date,
                work.get('period', 'unknown'),
                'poetry',
                work['source'],
                work.get('line_count', 0),
                True,
                work.get('text'),
                work.get('poetrydb_id'),
                self.normalize_text(work['title']),
                self.normalize_text(work['author'])
            ))

            # Insert lines if available
            if 'lines' in work:
                for i, line_text in enumerate(work['lines'], 1):
                    is_blank = len(line_text.strip()) == 0
                    self.cursor.execute("""
                        INSERT INTO lines (work_id, line_num, line_text, is_blank)
                        VALUES (?, ?, ?, ?)
                    """, (work['work_id'], i, line_text, is_blank))

        self.conn.commit()
        logging.info(f"✓ Imported {len(works)} PoetryDB works")

    def build_author_table(self):
        """Populate authors table from works."""

        logging.info("Building authors table...")

        self.cursor.execute("""
            INSERT OR IGNORE INTO authors (name, name_normalized, work_count)
            SELECT
                author,
                author_normalized,
                COUNT(*) as work_count
            FROM works
            WHERE author IS NOT NULL
            GROUP BY author, author_normalized
        """)

        self.conn.commit()

        author_count = self.cursor.execute("SELECT COUNT(*) FROM authors").fetchone()[0]
        logging.info(f"✓ Built authors table with {author_count} authors")

    def print_summary(self):
        """Print database summary statistics."""

        logging.info("\n" + "="*60)
        logging.info("DATABASE SUMMARY")
        logging.info("="*60)

        # Total counts
        total_works = self.cursor.execute("SELECT COUNT(*) FROM works").fetchone()[0]
        total_lines = self.cursor.execute("SELECT COUNT(*) FROM lines").fetchone()[0]
        total_authors = self.cursor.execute("SELECT COUNT(*) FROM authors").fetchone()[0]

        logging.info(f"\nTotal works: {total_works:,}")
        logging.info(f"Total lines: {total_lines:,}")
        logging.info(f"Total authors: {total_authors:,}")

        # By source
        logging.info("\nBy source:")
        sources = self.cursor.execute("""
            SELECT source, COUNT(*), SUM(line_count)
            FROM works
            GROUP BY source
            ORDER BY COUNT(*) DESC
        """).fetchall()

        for source, count, lines in sources:
            logging.info(f"  {source}: {count:,} works, {lines:,} lines")

        # By period
        logging.info("\nBy period:")
        periods = self.cursor.execute("""
            SELECT period, COUNT(*)
            FROM works
            GROUP BY period
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """).fetchall()

        for period, count in periods:
            logging.info(f"  {period}: {count:,} works")

        # Top authors
        logging.info("\nTop 10 authors by work count:")
        top_authors = self.cursor.execute("""
            SELECT name, work_count
            FROM authors
            ORDER BY work_count DESC
            LIMIT 10
        """).fetchall()

        for author, count in top_authors:
            logging.info(f"  {author}: {count:,} works")

        logging.info("\n" + "="*60)

    def build(self, sources: Dict[str, str]):
        """Build the unified database from all sources."""

        # Connect to database
        logging.info(f"Creating database at {self.db_path}...")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        try:
            # Create schema
            self.create_schema()

            # Import each source
            if 'gutenberg' in sources:
                self.import_gutenberg(sources['gutenberg'])

            if 'shakespeare' in sources:
                self.import_shakespeare(sources['shakespeare'])

            if 'core_poets' in sources:
                self.import_core_poets(sources['core_poets'])

            if 'poetrydb' in sources:
                self.import_poetrydb(sources['poetrydb'])

            # Build author table
            self.build_author_table()

            # Print summary
            self.print_summary()

            logging.info(f"\n✓ Database built successfully: {self.db_path}")

        finally:
            self.conn.close()


def main():
    """Build unified poetry database."""

    base_path = Path("/Users/justin/Repos/AI Project")

    # Define source file paths
    sources = {
        'gutenberg': base_path / "Data/gutenberg_reconstructed.jsonl",
        'shakespeare': base_path / "Data/poetry_corpus/shakespeare_complete_works.jsonl",
        'core_poets': base_path / "Data/poetry_corpus/core_poets_complete.jsonl",
        'poetrydb': base_path / "Data/poetry_corpus/poetrydb.jsonl"
    }

    # Output database
    output_db = base_path / "Data/poetry_unified.db"

    # Build database
    builder = UnifiedDatabaseBuilder(output_db)

    logging.info("="*60)
    logging.info("BUILDING UNIFIED POETRY DATABASE")
    logging.info("="*60)
    logging.info("")

    builder.build(sources)

    logging.info("\n" + "="*60)
    logging.info("BUILD COMPLETE")
    logging.info("="*60)


if __name__ == '__main__':
    main()
