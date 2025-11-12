#!/usr/bin/env python3
"""
Fix remaining taxonomy issues:
1. Map rhetorical_genre to proper values (Epideictic, Deliberative, Forensic, Mixed)
2. Fill in 6 missing modes
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
INPUT_FILE = BASE_DIR / "data/phase3/404_poems_classified_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "data/phase3/404_poems_classified_final.csv"

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} poems\n")

# =============================================================================
# 1. FIX RHETORICAL_GENRE
# =============================================================================

print("Fixing rhetorical_genre taxonomy...")

# Map LLM inventions to proper classical rhetoric categories
RHETORICAL_MAPPING = {
    'Descriptive': 'Epideictic',  # Description is often praise/blame
    'Narrative': 'Epideictic',  # Narrative often praises or blames
    'Epistolary': 'Deliberative',  # Letters often persuade
    'Persuasive': 'Deliberative',  # Direct match
    'Invective': 'Forensic',  # Attack/accusation = forensic
    'Didactic': 'Deliberative',  # Teaching/advising = deliberative
    'Exhortatory': 'Deliberative',  # Urging action = deliberative
    'Hortatory': 'Deliberative',  # Urging action = deliberative
    'Dramatic': 'Epideictic',  # Drama often praises/blames
    'Epical': 'Epideictic',  # Epic praises heroes
    'Hymn': 'Epideictic',  # Hymns praise
    'Reflective': 'Epideictic',  # Reflection evaluates (praise/blame)
    'Incantatory': 'Epideictic',  # Incantation praises/invokes
    'Eulogy': 'Epideictic',  # Eulogy praises
    'Dialectic': 'Forensic',  # Argument/debate = forensic
    'Mimetic': 'Epideictic',  # Imitation evaluates
    'Meditative': 'Epideictic',  # Meditation evaluates
    'Exhortative': 'Deliberative',  # Urging action = deliberative
}

fixed_count = 0
for idx, row in df.iterrows():
    rhet_genre = row['rhetorical_genre']
    if pd.notna(rhet_genre) and rhet_genre in RHETORICAL_MAPPING:
        old_value = rhet_genre
        new_value = RHETORICAL_MAPPING[rhet_genre]
        df.loc[idx, 'rhetorical_genre'] = new_value
        fixed_count += 1

print(f"  Fixed {fixed_count} rhetorical_genre entries")

# =============================================================================
# 2. FIX 6 MISSING MODES
# =============================================================================

print("\nFilling missing modes...")

# These are the 6 poems flagged for review
MISSING_MODES = {
    'Deor': 'Lyric',  # Anglo-Saxon lament poem
    'Wulf and Eadwacer': 'Lyric',  # Anglo-Saxon dramatic monologue
    'The Faerie Queene (Book I, Canto I)': 'Narrative',  # Epic narrative
    'A Letter from Artemisia': 'Lyric',  # Verse epistle
    'Carrion Comfort': 'Lyric',  # Hopkins sonnet
    'Twenty-One Love Poems': 'Lyric',  # Love lyric sequence
}

filled_count = 0
for idx, row in df.iterrows():
    if pd.isna(row['mode']):
        title = row['title']
        if title in MISSING_MODES:
            df.loc[idx, 'mode'] = MISSING_MODES[title]
            filled_count += 1
            print(f"  {title}: {MISSING_MODES[title]}")

print(f"\n  Filled {filled_count} missing modes")

# =============================================================================
# 3. SAVE AND REPORT
# =============================================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\n" + "="*60)
print("FINAL CLEANED DISTRIBUTIONS")
print("="*60)

print("\nRhetorical Genre (should only be 4 values):")
print(df['rhetorical_genre'].value_counts())

print("\nMode (should only be 3-4 values):")
print(df['mode'].value_counts())

print("\nMissing values check:")
print(f"  Missing period: {df['period'].isna().sum()}")
print(f"  Missing mode: {df['mode'].isna().sum()}")
print(f"  Missing rhetorical_genre: {df['rhetorical_genre'].isna().sum()}")

print("\n" + "="*60)
print(f"✓ Final cleaned data saved: {OUTPUT_FILE}")
print("="*60)
print("\nReady to merge with 52 gold-standard poems!")
print("Total training set will be: 456 poems")
