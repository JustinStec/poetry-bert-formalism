# Restart Instructions - All Sessions Use Correct Schema

## What Happened

Sessions were using different classification schemas:
- Session 1: Thematic tags ❌
- Session 2: Correct 28 fields ✓ (but was deleted)
- Session 3: Only 2 fields ❌
- Sessions 4, 5: Wrong schemas ❌

**All data deleted. Starting fresh with correct schema.**

## Correct Schema - 28 Fields

See `CLASSIFICATION_SCHEMA.md` for full details.

**HISTORICAL (2):** period, literary_movement
**RHETORICAL (14):** register, rhetorical_genre, discursive_structure, discourse_type, narrative_level, diegetic_mimetic, focalization, person, deictic_orientation, addressee_type, deictic_object, temporal_orientation, temporal_structure, tradition
**FORMAL (5):** mode, genre, stanza_structure, meter, rhyme

## Commands to Restart (Same as Before)

### Tab 1 (Session 1): Poems 0-23,334
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 0 23334 session1"
```

### Tab 2 (Session 2): Poems 23,334-46,668
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 23334 46668 session2"
```

### Tab 3 (Session 3): Poems 46,668-69,002
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 46668 69002 session3"
```

### Tab 4 (Session 4): Poems 69,002-93,336
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 69002 93336 session4"
```

### Tab 5 (Session 5): Poems 93,336-116,674
```bash
ssh justin@100.65.21.63 "cd ~/poetry-bert-formalism && python3 scripts/classify_range.py 93336 116674 session5"
```

## CRITICAL: Tell Each Claude

**In each web tab, paste this message BEFORE running the command:**

```
IMPORTANT: Read ~/poetry-bert-formalism/CLASSIFICATION_SCHEMA.md before classifying.

You MUST use exactly 28 fields for every poem:

HISTORICAL (2): period, literary_movement
RHETORICAL (14): register, rhetorical_genre, discursive_structure, discourse_type,
  narrative_level, diegetic_mimetic, focalization, person, deictic_orientation,
  addressee_type, deictic_object, temporal_orientation, temporal_structure, tradition
FORMAL (5): mode, genre, stanza_structure, meter, rhyme

DO NOT use: thematic tags, tone, death_theme, nature_imagery, formalism_score, etc.
Format MUST match training examples in training_set_456_poems.csv

Classify poems using ONLY these 28 fields.
```

## Verification After First Batch

After each session completes its first batch, verify:

```bash
ssh justin@100.65.21.63 "python3 << 'EOF'
import json
from pathlib import Path

for session in ['session1', 'session2', 'session3', 'session4', 'session5']:
    file = Path.home() / 'poetry-bert-formalism' / 'data' / 'classifications' / f'{session}_batch_000000_classified.json'
    if file.exists():
        with open(file) as f:
            data = json.load(f)
        if data:
            fields = set(data[0].keys()) - {'poem_id', 'filename', 'global_index', 'text'}
            print(f'{session}: {len(fields)} fields')
            if len(fields) == 21:  # 28 total - 7 metadata fields
                print(f'  ✓ CORRECT')
            else:
                print(f'  ✗ WRONG - has: {sorted(fields)[:5]}...')
EOF
"
```

Should show "✓ CORRECT" for all sessions.
