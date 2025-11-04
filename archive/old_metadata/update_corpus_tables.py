#!/usr/bin/env python3
"""
Script to update the 4-table corpus metadata structure
Handles: Historical, Form, Rhetoric, and Metadata tables
"""
import pandas as pd
import os
from datetime import datetime
from typing import Dict, Optional

# Paths
METADATA_DIR = "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development/Metadata/corpus_metadata"
TEXTS_DIR = "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development/corpus_texts"

# Table paths
HISTORICAL_CSV = os.path.join(METADATA_DIR, "Historical-corpus_metadata.csv")
FORM_CSV = os.path.join(METADATA_DIR, "Form-Table 1.csv")
RHETORIC_CSV = os.path.join(METADATA_DIR, "Rhetoric-Table 1.csv")
METADATA_CSV = os.path.join(METADATA_DIR, "Metadata-Table 1.csv")


def count_words_lines(text_path: str) -> tuple:
    """Count lines and words in a poem text file"""
    with open(text_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Skip header lines (TITLE:, AUTHOR:, YEAR:) and blank line after
    poem_lines = []
    in_poem = False
    for line in lines:
        if line.strip() == '' and not in_poem and len(poem_lines) == 0:
            in_poem = True
            continue
        if in_poem:
            poem_lines.append(line)

    num_lines = len([l for l in poem_lines if l.strip()])
    num_words = sum(len(line.split()) for line in poem_lines if line.strip())

    return num_lines, num_words


def update_historical_table(poem_id: int, title: str, author: str, author_last: str,
                            period: str, literary_movement: str, year_approx: int):
    """Update Historical-corpus_metadata.csv"""
    df = pd.read_csv(HISTORICAL_CSV)

    # Check if poem exists
    if poem_id in df['poem_id'].values:
        # Update existing
        idx = df[df['poem_id'] == poem_id].index[0]
        df.loc[idx] = [poem_id, title, author, author_last, period, literary_movement, year_approx]
    else:
        # Add new
        new_row = pd.DataFrame([{
            'poem_id': poem_id,
            'title': title,
            'author': author,
            'author_last': author_last,
            'period': period,
            'literary_movement': literary_movement,
            'year_approx': year_approx
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df = df.sort_values('poem_id').reset_index(drop=True)
    df.to_csv(HISTORICAL_CSV, index=False)
    print(f"✓ Updated Historical table for poem {poem_id}")


def update_form_table(poem_id: int, title: str, author: str, mode: str, genre: str,
                     stanza_structure: str, meter: str, rhyme: str):
    """Update Form-Table 1.csv"""
    df = pd.read_csv(FORM_CSV)

    if poem_id in df['poem_id'].values:
        idx = df[df['poem_id'] == poem_id].index[0]
        df.loc[idx] = [poem_id, title, author, mode, genre, stanza_structure, meter, rhyme]
    else:
        new_row = pd.DataFrame([{
            'poem_id': poem_id,
            'title': title,
            'author': author,
            'mode': mode,
            'genre': genre,
            'stanza_structure': stanza_structure,
            'meter': meter,
            'rhyme': rhyme
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df = df.sort_values('poem_id').reset_index(drop=True)
    df.to_csv(FORM_CSV, index=False)
    print(f"✓ Updated Form table for poem {poem_id}")


def update_rhetoric_table(poem_id: int, title: str, author: str,
                         register: str, rhetorical_genre: str, discursive_structure: str,
                         discourse_type: str, diegetic_mimetic: str, focalization: str,
                         person: str, deictic_orientation: str, addressee_type: str,
                         deictic_object: str, temporal_orientation: str,
                         temporal_structure: str, tradition: str):
    """Update Rhetoric-Table 1.csv"""
    df = pd.read_csv(RHETORIC_CSV)

    if poem_id in df['poem_id'].values:
        idx = df[df['poem_id'] == poem_id].index[0]
        df.loc[idx] = [poem_id, title, author, register, rhetorical_genre,
                      discursive_structure, discourse_type, diegetic_mimetic,
                      focalization, person, deictic_orientation, addressee_type,
                      deictic_object, temporal_orientation, temporal_structure, tradition]
    else:
        new_row = pd.DataFrame([{
            'poem_id': poem_id,
            'title': title,
            'author': author,
            'register': register,
            'rhetorical_genre': rhetorical_genre,
            'discursive_structure': discursive_structure,
            'discourse_type': discourse_type,
            'diegetic_mimetic': diegetic_mimetic,
            'focalization': focalization,
            'person': person,
            'deictic_orientation': deictic_orientation,
            'addressee_type': addressee_type,
            'deictic_object': deictic_object,
            'temporal_orientation': temporal_orientation,
            'temporal_structure': temporal_structure,
            'tradition': tradition
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df = df.sort_values('poem_id').reset_index(drop=True)
    df.to_csv(RHETORIC_CSV, index=False)
    print(f"✓ Updated Rhetoric table for poem {poem_id}")


def update_metadata_table(poem_id: int, title: str, author: str, source: str,
                         source_edition: str, source_page: str, length_lines: int,
                         length_words: float, collected: bool, filename: str, source_url: str):
    """Update Metadata-Table 1.csv"""
    df = pd.read_csv(METADATA_CSV)

    if poem_id in df['poem_id'].values:
        idx = df[df['poem_id'] == poem_id].index[0]
        df.loc[idx] = [poem_id, title, author, source, source_edition, source_page,
                      length_lines, length_words, collected, filename, source_url]
    else:
        new_row = pd.DataFrame([{
            'poem_id': poem_id,
            'title': title,
            'author': author,
            'source': source,
            'source_edition': source_edition,
            'source_page': source_page,
            'length_lines': length_lines,
            'length_words': length_words,
            'collected': collected,
            'filename': filename,
            'source_url': source_url
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    df = df.sort_values('poem_id').reset_index(drop=True)
    df.to_csv(METADATA_CSV, index=False)
    print(f"✓ Updated Metadata table for poem {poem_id}")


def add_poem_complete(
    # Basic info
    poem_id: int,
    title: str,
    author: str,
    author_last: str,

    # Historical
    period: str,
    literary_movement: str,
    year_approx: int,

    # Form
    mode: str,
    genre: str,
    stanza_structure: str,
    meter: str,
    rhyme: str,

    # Rhetoric
    register: str,
    rhetorical_genre: str,
    discursive_structure: str,
    discourse_type: str,
    diegetic_mimetic: str,
    focalization: str,
    person: str,
    deictic_orientation: str,
    addressee_type: str,
    deictic_object: str,
    temporal_orientation: str,
    temporal_structure: str,
    tradition: str,

    # Metadata
    source: str = "Poetry Foundation",
    source_edition: str = "",
    source_page: str = "",
    filename: str = "",
    source_url: str = "",
    text_path: Optional[str] = None
):
    """
    Add or update a complete poem entry across all 4 tables

    If text_path is provided, automatically counts lines and words
    """

    # Count words and lines if text path provided
    if text_path and os.path.exists(text_path):
        length_lines, length_words = count_words_lines(text_path)
        collected = True
    else:
        length_lines = 0
        length_words = 0.0
        collected = False

    # Update all tables
    update_historical_table(
        poem_id, title, author, author_last,
        period, literary_movement, year_approx
    )

    update_form_table(
        poem_id, title, author, mode, genre,
        stanza_structure, meter, rhyme
    )

    update_rhetoric_table(
        poem_id, title, author,
        register, rhetorical_genre, discursive_structure,
        discourse_type, diegetic_mimetic, focalization,
        person, deictic_orientation, addressee_type,
        deictic_object, temporal_orientation,
        temporal_structure, tradition
    )

    update_metadata_table(
        poem_id, title, author, source,
        source_edition, source_page, length_lines,
        length_words, collected, filename, source_url
    )

    print(f"\n{'='*70}")
    print(f"✓ Successfully updated all 4 tables for poem {poem_id}: {title}")
    print(f"  Lines: {length_lines}, Words: {length_words}, Collected: {collected}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    # Example usage
    print("Corpus metadata update script loaded.")
    print("\nExample usage:")
    print("""
    from update_corpus_tables import add_poem_complete

    add_poem_complete(
        poem_id=21,
        title="Ozymandias",
        author="Percy Bysshe Shelley",
        author_last="Shelley",
        period="Romantic",
        literary_movement="Romanticism",
        year_approx=1818,
        mode="Lyric",
        genre="",
        stanza_structure="Sonnet",
        meter="Iambic pentameter",
        rhyme="ABABACDCEDEFEF",
        register="Ironic",
        rhetorical_genre="Epideictic",
        discursive_structure="Monologic",
        discourse_type="Narrative report",
        diegetic_mimetic="Mixed",
        focalization="Internal",
        person="1st",
        deictic_orientation="First person",
        addressee_type="Direct address",
        deictic_object="Statue",
        temporal_orientation="Past",
        temporal_structure="Linear",
        tradition="Original",
        source="Poetry Foundation",
        filename="021_ozymandias.txt",
        source_url="https://www.poetryfoundation.org/poems/46565/ozymandias",
        text_path="/path/to/021_ozymandias.txt"
    )
    """)
