#!/usr/bin/env python3
"""
Merge the 4 gold-standard CSVs into one complete reference file.
"""

import csv
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
ARCHIVE = BASE_DIR / "archive/old_metadata/corpus_metadata"

# Read all 4 CSVs
historical = {}
rhetoric = {}
form = {}
metadata = {}

print("Loading gold-standard classifications...")

with open(ARCHIVE / "Historical-corpus_metadata.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('poem_id'):
            historical[row['poem_id']] = row

with open(ARCHIVE / "Rhetoric-Table 1.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('poem_id'):
            rhetoric[row['poem_id']] = row

with open(ARCHIVE / "Form-Table 1.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('poem_id'):
            form[row['poem_id']] = row

with open(ARCHIVE / "Metadata-Table 1.csv", 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get('poem_id'):
            metadata[row['poem_id']] = row

print(f"  Historical: {len(historical)} poems")
print(f"  Rhetoric: {len(rhetoric)} poems")
print(f"  Form: {len(form)} poems")
print(f"  Metadata: {len(metadata)} poems")

# Merge all data
merged = []
all_ids = sorted(set(historical.keys()) | set(rhetoric.keys()) | set(form.keys()) | set(metadata.keys()))

for poem_id in all_ids:
    row = {'poem_id': poem_id}

    # Basic metadata
    if poem_id in metadata:
        row['title'] = metadata[poem_id].get('title', '')
        row['author'] = metadata[poem_id].get('author', '')
        row['source_url'] = metadata[poem_id].get('source_url', '')
        row['length_lines'] = metadata[poem_id].get('length_lines', '')
        row['length_words'] = metadata[poem_id].get('length_words', '')

    # Historical
    if poem_id in historical:
        row['period'] = historical[poem_id].get('period', '')
        row['literary_movement'] = historical[poem_id].get('literary_movement', '')
        row['year_approx'] = historical[poem_id].get('year_approx', '')

    # Rhetoric (16 columns)
    if poem_id in rhetoric:
        row['register'] = rhetoric[poem_id].get('register', '')
        row['rhetorical_genre'] = rhetoric[poem_id].get('rhetorical_genre', '')
        row['discursive_structure'] = rhetoric[poem_id].get('discursive_structure', '')
        row['discourse_type'] = rhetoric[poem_id].get('discourse_type', '')
        row['diegetic_mimetic'] = rhetoric[poem_id].get('diegetic_mimetic', '')
        row['focalization'] = rhetoric[poem_id].get('focalization', '')
        row['person'] = rhetoric[poem_id].get('person', '')
        row['deictic_orientation'] = rhetoric[poem_id].get('deictic_orientation', '')
        row['addressee_type'] = rhetoric[poem_id].get('addressee_type', '')
        row['deictic_object'] = rhetoric[poem_id].get('deictic_object', '')
        row['temporal_orientation'] = rhetoric[poem_id].get('temporal_orientation', '')
        row['temporal_structure'] = rhetoric[poem_id].get('temporal_structure', '')
        row['tradition'] = rhetoric[poem_id].get('tradition', '')

    # Form (5 columns)
    if poem_id in form:
        row['mode'] = form[poem_id].get('mode', '')
        row['genre'] = form[poem_id].get('genre', '')
        row['stanza_structure'] = form[poem_id].get('stanza_structure', '')
        row['meter'] = form[poem_id].get('meter', '')
        row['rhyme'] = form[poem_id].get('rhyme', '')

    merged.append(row)

# Write merged file
output_file = BASE_DIR / "data/phase3/gold_standard_52_poems.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    'poem_id', 'title', 'author', 'source_url', 'length_lines', 'length_words',
    'year_approx', 'period', 'literary_movement',
    'register', 'rhetorical_genre', 'discursive_structure', 'discourse_type',
    'diegetic_mimetic', 'focalization', 'person', 'deictic_orientation',
    'addressee_type', 'deictic_object', 'temporal_orientation', 'temporal_structure', 'tradition',
    'mode', 'genre', 'stanza_structure', 'meter', 'rhyme'
]

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(merged)

print(f"\n✓ Merged {len(merged)} poems")
print(f"✓ Saved to: {output_file}")
print(f"\nColumns: {len(fieldnames)}")
print("  - Basic metadata: 6")
print("  - Historical: 3")
print("  - Rhetoric: 13")
print("  - Form: 5")
print("  - Total: 27")
