#!/usr/bin/env python3
"""
Clean up taxonomy inconsistencies from LLM-generated classifications.
Maps incorrect period/mode names to proper schema.
Flags uncertain classifications for manual review.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path("/Users/justin/Repos/AI Project")
INPUT_FILE = BASE_DIR / "data/phase3/404_poems_classified.csv"
OUTPUT_FILE = BASE_DIR / "data/phase3/404_poems_classified_cleaned.csv"
REVIEW_FILE = BASE_DIR / "data/phase3/poems_to_review.csv"

# Load data
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} poems\n")

# Track changes and flags
changes_log = []
review_flags = []

def flag_for_review(idx, reason):
    """Flag a poem for manual review"""
    review_flags.append({
        'index': idx,
        'title': df.loc[idx, 'title'],
        'author': df.loc[idx, 'author'],
        'year': df.loc[idx, 'year_approx'],
        'reason': reason,
        'current_period': df.loc[idx, 'period'],
        'current_mode': df.loc[idx, 'mode']
    })

# =============================================================================
# 1. FIX PERIOD TAXONOMY
# =============================================================================

print("Fixing period taxonomy...")

PERIOD_MAPPING = {
    'Medieval': 'Middle English',  # Could also be Anglo-Saxon - check year
    'Early Modern': None,  # Will determine from year
    'Eighteenth Century': None,  # Will determine from year
    'Early 20th Century': 'Modernist',
    'Nineteenth Century': None,  # Could be Romantic or Victorian
    'Seventeenth Century': None,  # Could be Caroline, Interregnum, Restoration
}

for idx, row in df.iterrows():
    period = row['period']
    year = row['year_approx']

    # Handle period based on year ranges
    if pd.isna(period) or period in PERIOD_MAPPING:
        old_period = period

        # Determine correct period from year
        if year < 1100:
            new_period = 'Anglo-Saxon'
        elif year < 1500:
            new_period = 'Middle English'
        elif year < 1558:
            new_period = 'Tudor'
        elif year < 1603:
            new_period = 'Elizabethan'
        elif year < 1625:
            new_period = 'Jacobean'
        elif year < 1649:
            new_period = 'Caroline'
        elif year < 1660:
            new_period = 'Interregnum'
        elif year < 1688:
            new_period = 'Restoration'
        elif year < 1780:
            if year < 1714:
                new_period = 'Augustan'
            else:
                new_period = 'Neoclassical'
        elif year < 1837:
            new_period = 'Romantic'
        elif year < 1901:
            new_period = 'Victorian'
        elif year < 1945:
            new_period = 'Modernist'
        elif year < 1980:
            new_period = 'Postwar'
        else:
            new_period = 'Contemporary'

        if old_period != new_period:
            df.loc[idx, 'period'] = new_period
            changes_log.append(f"Row {idx}: Period '{old_period}' → '{new_period}' (based on year {year})")

print(f"  Fixed {len([c for c in changes_log if 'Period' in c])} period entries")

# =============================================================================
# 2. FIX MODE TAXONOMY
# =============================================================================

print("\nFixing mode taxonomy...")

MODE_MAPPING = {
    'Descriptive': 'Lyric',
    'Satirical': 'Lyric',
    'Satire': 'Narrative',  # Most satire is narrative
    'Drama': 'Dramatic',
    'Experimental': 'Lyric',  # Most experimental poetry is lyric
    'Metaphysical': 'Lyric',
    'Poetic': 'Lyric',
    'lyric': 'Lyric',  # Fix capitalization
    'narrative': 'Narrative',
    'dramatic': 'Dramatic',
}

for idx, row in df.iterrows():
    mode = row['mode']

    if pd.notna(mode) and mode in MODE_MAPPING:
        old_mode = mode
        new_mode = MODE_MAPPING[mode]
        df.loc[idx, 'mode'] = new_mode
        changes_log.append(f"Row {idx}: Mode '{old_mode}' → '{new_mode}'")

print(f"  Fixed {len([c for c in changes_log if 'Mode' in c])} mode entries")

# =============================================================================
# 3. FLAG UNCERTAIN CLASSIFICATIONS
# =============================================================================

print("\nFlagging uncertain classifications...")

for idx, row in df.iterrows():
    # Flag if critical fields are missing
    if pd.isna(row['period']):
        flag_for_review(idx, "Missing period")

    if pd.isna(row['mode']):
        flag_for_review(idx, "Missing mode")

    # Flag unusual register values that might be errors
    register = row['register']
    if pd.notna(register):
        # Flag if register seems wrong (too short, all caps, etc.)
        if len(str(register)) < 3:
            flag_for_review(idx, f"Suspicious register: '{register}'")
        elif str(register).isupper() and len(str(register)) > 3:
            flag_for_review(idx, f"All-caps register: '{register}'")

print(f"  Flagged {len(review_flags)} poems for manual review")

# =============================================================================
# 4. STANDARDIZE RHETORICAL FIELDS
# =============================================================================

print("\nStandardizing rhetorical fields...")

# Fix common capitalization issues
RHETORICAL_FIXES = {
    'rhetorical_genre': {
        'epideictic': 'Epideictic',
        'deliberative': 'Deliberative',
        'forensic': 'Forensic',
        'mixed': 'Mixed',
    },
    'discursive_structure': {
        'monologic': 'Monologic',
        'dialogic': 'Dialogic',
        'polyvocal': 'Polyvocal',
    },
    'diegetic_mimetic': {
        'diegetic': 'Diegetic',
        'mimetic': 'Mimetic',
        'mixed': 'Mixed',
    },
}

fix_count = 0
for field, mapping in RHETORICAL_FIXES.items():
    for idx, row in df.iterrows():
        value = row[field]
        if pd.notna(value) and str(value).lower() in mapping:
            old_value = value
            new_value = mapping[str(value).lower()]
            if old_value != new_value:
                df.loc[idx, field] = new_value
                fix_count += 1

print(f"  Fixed {fix_count} rhetorical field capitalizations")

# =============================================================================
# 5. SAVE RESULTS
# =============================================================================

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

# Save cleaned CSV
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n✓ Cleaned data saved: {OUTPUT_FILE}")
print(f"  Total poems: {len(df)}")
print(f"  Changes made: {len(changes_log)}")

# Save review CSV
if review_flags:
    review_df = pd.DataFrame(review_flags)
    review_df.to_csv(REVIEW_FILE, index=False)
    print(f"\n✓ Review file saved: {REVIEW_FILE}")
    print(f"  Poems flagged for review: {len(review_flags)}")
    print("\n  Top reasons:")
    reasons = pd.Series([f['reason'] for f in review_flags]).value_counts()
    for reason, count in reasons.items():
        print(f"    - {reason}: {count}")

# Show distribution after cleanup
print("\n" + "="*60)
print("CLEANED DATA DISTRIBUTIONS")
print("="*60)

print("\nPeriod:")
print(df['period'].value_counts().head(15))

print("\nMode:")
print(df['mode'].value_counts())

print("\nRhetorical Genre:")
print(df['rhetorical_genre'].value_counts())

print("\n" + "="*60)
print("✓ Cleanup complete!")
print("="*60)
print(f"\nNext steps:")
print(f"1. Review flagged poems: {REVIEW_FILE}")
print(f"2. Make corrections if needed")
print(f"3. Merge with gold standard (52 poems)")
print(f"4. Final training set: 456 poems")
