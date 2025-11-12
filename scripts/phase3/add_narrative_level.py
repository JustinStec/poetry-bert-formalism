#!/usr/bin/env python3
"""
Add narrative_level column to the 52 gold-standard poems.
Logic:
- Extradiegetic: Diegetic mode with 3rd person narrator outside story
- Intradiegetic: Diegetic mode with 1st person narrator inside story
- (blank): Pure mimetic discourse (direct lyrics, apostrophes)
"""

import csv
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
input_file = BASE_DIR / "data/phase3/gold_standard_52_poems.csv"
output_file = BASE_DIR / "data/phase3/gold_standard_52_poems_with_narrative_level.csv"

with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    poems = list(reader)

print(f"Loaded {len(poems)} poems")
print("\nAdding narrative_level column...\n")

for poem in poems:
    # Logic for narrative_level
    discourse_type = poem.get('discourse_type', '')
    diegetic_mimetic = poem.get('diegetic_mimetic', '')
    person = poem.get('person', '')
    mode = poem.get('mode', '')

    narrative_level = ''

    # If it's primarily Diegetic (telling), assign narrative level
    if 'Diegetic' in diegetic_mimetic and 'Narrative' in discourse_type:
        # Check if narrator is inside (1st person) or outside (3rd person) the story
        if person.startswith('3rd'):
            narrative_level = 'Extradiegetic'
        elif person.startswith('1st'):
            # Could be either - check context
            # If mode is Narrative, likely extradiegetic (narrator telling about events)
            # If Lyric, might be intradiegetic (character's own voice)
            if mode == 'Narrative':
                narrative_level = 'Extradiegetic'
            else:
                narrative_level = 'Intradiegetic'
    elif diegetic_mimetic == 'Diegetic':
        # Pure diegetic - determine level by person
        if '3rd' in person:
            narrative_level = 'Extradiegetic'
        elif '1st' in person:
            narrative_level = 'Intradiegetic'
    # Mixed could have narrative level if there's a narrative component
    elif diegetic_mimetic == 'Mixed':
        if 'Narrative' in discourse_type:
            if '3rd' in person:
                narrative_level = 'Extradiegetic'
            elif '1st' in person:
                narrative_level = 'Intradiegetic'
    # Mimetic = no narrative level (pure showing)

    poem['narrative_level'] = narrative_level

    # Debug output for a few examples
    if int(poem['poem_id']) <= 5:
        print(f"Poem {poem['poem_id']}: {poem['title']}")
        print(f"  Discourse: {discourse_type} | Diegetic/Mimetic: {diegetic_mimetic}")
        print(f"  Person: {person} | Mode: {mode}")
        print(f"  >>> Narrative Level: {narrative_level or '(blank - mimetic)'}")
        print()

# Write updated CSV with new column order
fieldnames = [
    'poem_id', 'title', 'author', 'source_url', 'length_lines', 'length_words',
    'year_approx', 'period', 'literary_movement',
    'register', 'rhetorical_genre', 'discursive_structure', 'discourse_type',
    'narrative_level',  # NEW COLUMN
    'diegetic_mimetic', 'focalization', 'person', 'deictic_orientation',
    'addressee_type', 'deictic_object', 'temporal_orientation', 'temporal_structure', 'tradition',
    'mode', 'genre', 'stanza_structure', 'meter', 'rhyme'
]

with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(poems)

print(f"✓ Updated {len(poems)} poems")
print(f"✓ Saved to: {output_file}")

# Show distribution
from collections import Counter
levels = Counter(p['narrative_level'] for p in poems)
print("\nNarrative Level Distribution:")
print(f"  Extradiegetic: {levels['Extradiegetic']}")
print(f"  Intradiegetic: {levels['Intradiegetic']}")
print(f"  (blank/mimetic): {levels['']}")
