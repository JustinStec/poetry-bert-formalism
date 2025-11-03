#!/usr/bin/env python3
"""
Download Shakespeare's complete works with chronological metadata.
Creates structured corpus for career-arc analysis of formal features.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen
from urllib.parse import quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Complete Shakespeare chronology with composition dates
# Based on scholarly consensus (primarily Bevington, Wells & Taylor)
SHAKESPEARE_WORKS = [
    # EARLY PERIOD (1590-1594)
    {"title": "Henry VI, Part 1", "date": 1591, "genre": "history", "period": "early", "gutenberg_id": 1511},
    {"title": "Henry VI, Part 2", "date": 1591, "genre": "history", "period": "early", "gutenberg_id": 1512},
    {"title": "Henry VI, Part 3", "date": 1591, "genre": "history", "period": "early", "gutenberg_id": 1513},
    {"title": "Richard III", "date": 1592, "genre": "history", "period": "early", "gutenberg_id": 1122},
    {"title": "The Comedy of Errors", "date": 1592, "genre": "comedy", "period": "early", "gutenberg_id": 1504},
    {"title": "Titus Andronicus", "date": 1593, "genre": "tragedy", "period": "early", "gutenberg_id": 1524},
    {"title": "The Taming of the Shrew", "date": 1593, "genre": "comedy", "period": "early", "gutenberg_id": 1508},
    {"title": "The Two Gentlemen of Verona", "date": 1594, "genre": "comedy", "period": "early", "gutenberg_id": 1507},
    {"title": "Love's Labour's Lost", "date": 1594, "genre": "comedy", "period": "early", "gutenberg_id": 1511},
    {"title": "Romeo and Juliet", "date": 1595, "genre": "tragedy", "period": "early", "gutenberg_id": 1513},

    # MIDDLE PERIOD (1595-1600)
    {"title": "Richard II", "date": 1595, "genre": "history", "period": "middle", "gutenberg_id": 1121},
    {"title": "A Midsummer Night's Dream", "date": 1595, "genre": "comedy", "period": "middle", "gutenberg_id": 1514},
    {"title": "King John", "date": 1596, "genre": "history", "period": "middle", "gutenberg_id": 1110},
    {"title": "The Merchant of Venice", "date": 1596, "genre": "comedy", "period": "middle", "gutenberg_id": 1515},
    {"title": "Henry IV, Part 1", "date": 1597, "genre": "history", "period": "middle", "gutenberg_id": 1118},
    {"title": "Henry IV, Part 2", "date": 1598, "genre": "history", "period": "middle", "gutenberg_id": 1119},
    {"title": "Much Ado About Nothing", "date": 1598, "genre": "comedy", "period": "middle", "gutenberg_id": 1519},
    {"title": "Henry V", "date": 1599, "genre": "history", "period": "middle", "gutenberg_id": 1120},
    {"title": "Julius Caesar", "date": 1599, "genre": "tragedy", "period": "middle", "gutenberg_id": 1120},
    {"title": "As You Like It", "date": 1599, "genre": "comedy", "period": "middle", "gutenberg_id": 1121},
    {"title": "Twelfth Night", "date": 1601, "genre": "comedy", "period": "middle", "gutenberg_id": 1526},
    {"title": "Hamlet", "date": 1600, "genre": "tragedy", "period": "middle", "gutenberg_id": 1524},
    {"title": "The Merry Wives of Windsor", "date": 1600, "genre": "comedy", "period": "middle", "gutenberg_id": 1517},

    # LATE PERIOD (1601-1608) - "Problem plays" and great tragedies
    {"title": "Troilus and Cressida", "date": 1602, "genre": "problem_play", "period": "late", "gutenberg_id": 1527},
    {"title": "All's Well That Ends Well", "date": 1602, "genre": "problem_play", "period": "late", "gutenberg_id": 1529},
    {"title": "Measure for Measure", "date": 1604, "genre": "problem_play", "period": "late", "gutenberg_id": 1530},
    {"title": "Othello", "date": 1604, "genre": "tragedy", "period": "late", "gutenberg_id": 1531},
    {"title": "King Lear", "date": 1605, "genre": "tragedy", "period": "late", "gutenberg_id": 1532},
    {"title": "Macbeth", "date": 1606, "genre": "tragedy", "period": "late", "gutenberg_id": 1533},
    {"title": "Antony and Cleopatra", "date": 1606, "genre": "tragedy", "period": "late", "gutenberg_id": 1534},
    {"title": "Coriolanus", "date": 1608, "genre": "tragedy", "period": "late", "gutenberg_id": 1535},
    {"title": "Timon of Athens", "date": 1608, "genre": "tragedy", "period": "late", "gutenberg_id": 1536},

    # FINAL PERIOD (1609-1613) - Romances
    {"title": "Pericles", "date": 1609, "genre": "romance", "period": "final", "gutenberg_id": 1537},
    {"title": "Cymbeline", "date": 1610, "genre": "romance", "period": "final", "gutenberg_id": 1538},
    {"title": "The Winter's Tale", "date": 1611, "genre": "romance", "period": "final", "gutenberg_id": 1539},
    {"title": "The Tempest", "date": 1611, "genre": "romance", "period": "final", "gutenberg_id": 1540},
    {"title": "Henry VIII", "date": 1613, "genre": "history", "period": "final", "gutenberg_id": 1541},

    # POETRY
    {"title": "Venus and Adonis", "date": 1593, "genre": "narrative_poem", "period": "early", "gutenberg_id": 1045},
    {"title": "The Rape of Lucrece", "date": 1594, "genre": "narrative_poem", "period": "early", "gutenberg_id": 1046},
    {"title": "Sonnets", "date": 1609, "genre": "sonnet", "period": "late", "gutenberg_id": 1041},
]


class ShakespeareCorpusBuilder:
    def __init__(self, output_dir: str = "Data/poetry_corpus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://www.gutenberg.org/cache/epub"

    def download_work(self, work: Dict) -> Optional[Dict]:
        """Download a single Shakespeare work from Project Gutenberg."""
        try:
            # Try plain text format first
            url = f"{self.base_url}/{work['gutenberg_id']}/pg{work['gutenberg_id']}.txt"
            logging.info(f"Downloading: {work['title']} ({work['date']})")

            with urlopen(url, timeout=30) as response:
                text = response.read().decode('utf-8')

            # Clean Gutenberg header/footer
            text = self.clean_gutenberg_text(text)

            # Parse into lines
            lines = text.split('\n')

            title_slug = work['title'].lower().replace(' ', '_').replace(',', '').replace("'", '')
            return {
                'work_id': f"shakespeare_{work['date']}_{title_slug}",
                'title': work['title'],
                'author': 'William Shakespeare',
                'date': work['date'],
                'period': work['period'],
                'genre': work['genre'],
                'gutenberg_id': work['gutenberg_id'],
                'text': text,
                'lines': lines,
                'line_count': len(lines),
            }

        except Exception as e:
            logging.warning(f"Failed to download {work['title']}: {e}")
            return None

    def clean_gutenberg_text(self, text: str) -> str:
        """Remove Project Gutenberg header and footer."""
        # Find start of actual text (after Gutenberg header)
        start_markers = [
            "*** START OF THE PROJECT GUTENBERG",
            "*** START OF THIS PROJECT GUTENBERG",
        ]
        for marker in start_markers:
            if marker in text:
                text = text.split(marker)[1]
                # Skip one more line (the ebook title line)
                text = '\n'.join(text.split('\n')[1:])
                break

        # Find end of actual text (before Gutenberg footer)
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

    def parse_verse_structure(self, text: str) -> List[Dict]:
        """
        Parse dramatic verse structure for prosodic analysis.
        Identifies speaker changes, verse/prose sections, line boundaries.
        """
        lines = text.split('\n')
        structured_lines = []
        current_speaker = None
        in_verse = True

        for i, line in enumerate(lines):
            line_data = {
                'line_num': i,
                'text': line,
                'is_blank': len(line.strip()) == 0,
            }

            # Detect speaker changes (all caps names followed by period/colon)
            speaker_match = re.match(r'^([A-Z][A-Z\s]+)[.:]', line)
            if speaker_match:
                current_speaker = speaker_match.group(1).strip()
                line_data['speaker'] = current_speaker
                line_data['is_speech_marker'] = True
            elif current_speaker:
                line_data['speaker'] = current_speaker

            # Detect verse vs prose (heuristic: indented lines are verse)
            if line.startswith('  ') and not line_data.get('is_speech_marker'):
                line_data['is_verse'] = True
            else:
                line_data['is_verse'] = False

            structured_lines.append(line_data)

        return structured_lines

    def build_corpus(self) -> List[Dict]:
        """Download and structure all Shakespeare works."""
        corpus = []

        logging.info("="*60)
        logging.info("BUILDING SHAKESPEARE CHRONOLOGICAL CORPUS")
        logging.info("="*60)

        # Sort by composition date for career-arc analysis
        sorted_works = sorted(SHAKESPEARE_WORKS, key=lambda x: x['date'])

        for i, work in enumerate(sorted_works):
            logging.info(f"[{i+1}/{len(sorted_works)}] {work['title']} ({work['date']}, {work['period']})")

            work_data = self.download_work(work)
            if work_data:
                # Add verse structure for plays
                if work['genre'] in ['tragedy', 'comedy', 'history', 'romance', 'problem_play']:
                    work_data['structured_lines'] = self.parse_verse_structure(work_data['text'])

                corpus.append(work_data)

        return corpus

    def save_corpus(self, corpus: List[Dict], format: str = 'jsonl'):
        """Save corpus in specified format."""
        if format == 'jsonl':
            output_file = self.output_dir / 'shakespeare_complete_works.jsonl'
            with open(output_file, 'w', encoding='utf-8') as f:
                for work in corpus:
                    f.write(json.dumps(work, ensure_ascii=False) + '\n')
            logging.info(f"✓ Saved to: {output_file}")

        # Also save period-separated files for easier access
        for period in ['early', 'middle', 'late', 'final']:
            period_works = [w for w in corpus if w['period'] == period]
            if period_works:
                output_file = self.output_dir / f'shakespeare_{period}_period.jsonl'
                with open(output_file, 'w', encoding='utf-8') as f:
                    for work in period_works:
                        f.write(json.dumps(work, ensure_ascii=False) + '\n')
                logging.info(f"✓ Saved {len(period_works)} {period} period works to: {output_file}")

    def generate_summary(self, corpus: List[Dict]):
        """Generate corpus statistics."""
        logging.info("\n" + "="*60)
        logging.info("CORPUS SUMMARY")
        logging.info("="*60)
        logging.info(f"Total works: {len(corpus)}")

        # By period
        logging.info("\nBy career period:")
        for period in ['early', 'middle', 'late', 'final']:
            count = len([w for w in corpus if w['period'] == period])
            dates = [w['date'] for w in corpus if w['period'] == period]
            date_range = f"{min(dates)}-{max(dates)}" if dates else "N/A"
            logging.info(f"  {period.title()}: {count} works ({date_range})")

        # By genre
        logging.info("\nBy genre:")
        genres = {}
        for work in corpus:
            genre = work['genre']
            genres[genre] = genres.get(genre, 0) + 1
        for genre, count in sorted(genres.items()):
            logging.info(f"  {genre}: {count} works")

        # Total lines (verse + prose)
        total_lines = sum(w.get('line_count', 0) for w in corpus)
        logging.info(f"\nTotal lines: {total_lines:,}")


def main():
    builder = ShakespeareCorpusBuilder()

    # Build corpus
    corpus = builder.build_corpus()

    # Save in multiple formats
    builder.save_corpus(corpus)

    # Generate summary
    builder.generate_summary(corpus)

    logging.info("\n" + "="*60)
    logging.info("USAGE FOR CAREER-ARC ANALYSIS")
    logging.info("="*60)
    logging.info("""
To track formal features across Shakespeare's career:

1. Load works sorted by date:
   works = sorted(corpus, key=lambda x: x['date'])

2. Calculate feature frequency by period:
   for period in ['early', 'middle', 'late', 'final']:
       period_works = [w for w in works if w['period'] == period]
       # Run prosodic analysis, count enjambment, etc.

3. Track individual features over time:
   # Example: feminine endings frequency
   for work in works:
       fem_endings = count_feminine_endings(work)
       print(f"{work['date']}: {work['title']} - {fem_endings}%")

4. Compare genres within periods:
   # E.g., early comedies vs. early tragedies

This enables the kind of career development analysis
T.S. Eliot performed on Shakespeare's verse style.
    """)


if __name__ == '__main__':
    main()
