# Poetry Corpus Metadata Schema

Complete reference for all metadata fields across the four enhancement tiers.

---

## Tier 1: Automated Basic Metadata (100% Coverage)

| Field | Type | Description | Source | Example |
|-------|------|-------------|--------|---------|
| `poem_id` | INTEGER | Unique sequential ID (1-116,675) | Sequential numbering | 42 |
| `title` | TEXT | Poem title | Filename parsing | "Daddy" |
| `author` | TEXT | Full author name | Filename parsing | "Plath, Sylvia" |
| `author_last` | TEXT | Author's last name | Parsed from author | "Plath" |
| `date` | TEXT | Date string | Filename parsing | "1962" |
| `year_approx` | INTEGER | Approximate year | Parsed from date | 1962 |
| `source` | TEXT | Corpus source | Existing metadata | "poetry_platform" |
| `source_url` | TEXT | URL to source | Generated or existing | "https://www.poetryfoundation.org/..." |
| `filepath` | TEXT | Relative path to file | File system | "Plath, Sylvia/000042_Daddy_Plath_Sylvia_1962.txt" |
| `filename` | TEXT | Standardized filename | File system | "000042_Daddy_Plath_Sylvia_1962.txt" |
| `content` | TEXT | Full poem text | File content | "You do not do, you do not do..." |
| `length_lines` | INTEGER | Number of lines | Count from content | 80 |
| `length_words` | INTEGER | Number of words | Count from content | 512 |
| `content_hash` | TEXT | MD5 hash of content | MD5 hash function | "a3f5c8..." |
| `search_vector` | TSVECTOR | Full-text search index | Auto-generated (PostgreSQL) | - |
| `created_at` | TIMESTAMP | Record creation time | Auto-generated | 2025-01-10 14:23:00 |
| `updated_at` | TIMESTAMP | Last update time | Auto-generated | 2025-01-10 14:23:00 |

---

## Tier 2: Historical Context (70-80% Coverage, AI-Assisted)

| Field | Type | Description | Vocabulary | Example |
|-------|------|-------------|------------|---------|
| `period` | TEXT | Historical period | 12 categories | "Postwar" |
| `literary_movement` | TEXT | Literary movement | 13+ categories | "Confessional" |
| `mode` | TEXT | Poetic mode | 4 categories | "Lyric" |
| `confidence_period` | FLOAT | AI confidence (0-1) | - | 0.94 |
| `confidence_movement` | FLOAT | AI confidence (0-1) | - | 0.89 |
| `confidence_mode` | FLOAT | AI confidence (0-1) | - | 0.96 |
| `classification_method` | TEXT | How classified | - | "ai_local_llm" |
| `reviewed_by` | TEXT | Manual reviewer (if any) | - | "human" |
| `reviewed_at` | TIMESTAMP | When manually reviewed | - | 2025-01-15 10:00:00 |
| `notes` | TEXT | Classification notes | - | "Borderline Beat/Confessional" |

### Controlled Vocabularies:

#### Period (12 categories)
```
Tudor         (1485-1558)
Elizabethan   (1558-1603)
Jacobean      (1603-1625)
Caroline      (1625-1649)
Interregnum   (1649-1660)
Restoration   (1660-1700)
Neoclassical  (1700-1785)
Romantic      (1785-1837)
Victorian     (1837-1901)
Modernist     (1901-1945)
Postwar       (1945-1980)
Contemporary  (1980-present)
```

#### Literary Movement (13+ categories, extensible)
```
Renaissance
Metaphysical
Augustan
Graveyard School
Romanticism
Pre-Raphaelite
Imagism
Modernism
Harlem Renaissance
Beat
Confessional
Black Arts
Language Poetry

Future additions:
- Symbolism
- Objectivism
- New Formalism
- L=A=N=G=U=A=G=E
- Flarf
- Conceptual Poetry
```

#### Mode (4 categories)
```
Lyric      - Personal, emotional, first-person
Narrative  - Story-driven, plot-based
Dramatic   - Dialogue, characters, staged
Mixed      - Combination of modes
```

---

## Tier 3: Prosodic Features (40-60% Coverage, Semi-Automated)

| Field | Type | Description | Vocabulary | Example |
|-------|------|-------------|------------|---------|
| `genre` | TEXT | Poetic genre/form | Semi-controlled | "Sonnet" |
| `meter` | TEXT | Metrical pattern | Semi-controlled | "Iambic pentameter" |
| `rhyme` | TEXT | Rhyme scheme | Notation | "ABAB CDCD EFEF GG" |
| `stanza_structure` | TEXT | Stanza organization | Descriptive | "16 five-line stanzas" |
| `confidence_genre` | FLOAT | Detection confidence (0-1) | - | 0.92 |
| `confidence_meter` | FLOAT | Detection confidence (0-1) | - | 0.87 |
| `confidence_rhyme` | FLOAT | Detection confidence (0-1) | - | 0.91 |
| `analysis_method` | TEXT | Analysis method | - | "prosodic_library" |
| `computed_at` | TIMESTAMP | When computed | - | 2025-02-01 15:30:00 |

### Common Values:

#### Genre (semi-controlled, extensible)
```
Sonnet
Elegy
Ode
Pastoral
Epithalamion
Satire
Ballad
Villanelle
Sestina
Haiku
Dramatic monologue
Ekphrasis
Aubade
Lyric poem
Epic
Narrative poem
Free verse
Prose poem
```

#### Meter (semi-controlled)
```
Iambic pentameter
Iambic tetrameter
Iambic trimeter
Anapestic tetrameter
Trochaic tetrameter
Dactylic hexameter
Ballad meter
Blank verse
Free verse
Syllabic verse
Mixed meter
Irregular meter
```

#### Rhyme Notation
```
ABAB         - Alternating rhyme
AABB         - Couplets
ABBA         - Enclosed rhyme
ABABCDCDEFEFGG - Shakespearean sonnet
ABBAABBA CDECDE - Petrarchan sonnet
Unrhymed     - Blank verse
Irregular    - Inconsistent pattern
Light rhyme  - Slant/near rhymes
```

---

## Tier 4: Rhetorical Features (1,000-poem Research Subset Only)

| Field | Type | Description | Vocabulary | Example |
|-------|------|-------------|------------|---------|
| `register` | TEXT | Emotional/stylistic tone | 35+ values | "Confessional" |
| `rhetorical_genre` | TEXT | Classical rhetorical category | 4 categories | "Epideictic" |
| `discursive_structure` | TEXT | Discourse organization | 3 categories | "Monologic" |
| `discourse_type` | TEXT | Type of discourse | Multiple | "Direct discourse" |
| `diegetic_mimetic` | TEXT | Narrative mode | 3 categories | "Mimetic" |
| `focalization` | TEXT | Narrative perspective | 4 categories | "Internal" |
| `person` | TEXT | Grammatical person | Multiple | "1st" |
| `deictic_orientation` | TEXT | Spatial/personal orientation | Multiple | "First person" |
| `addressee_type` | TEXT | Type of address | Multiple | "Direct address" |
| `deictic_object` | TEXT | What is referenced | Free text | "Father" |
| `temporal_orientation` | TEXT | Time focus | Multiple | "Past and present" |
| `temporal_structure` | TEXT | How time is structured | Multiple | "Recursive" |
| `tradition` | TEXT | Relation to tradition | 4 categories | "Original" |
| `annotated_by` | TEXT | Who annotated | - | "justin" |
| `annotated_at` | TIMESTAMP | When annotated | - | 2025-03-15 09:00:00 |
| `annotation_notes` | TEXT | Annotation notes | Free text | "Complex temporal layering" |

### Controlled Vocabularies:

#### Register (35+ values, extensible)
```
Meditative
Argumentative
Elegiac
Celebratory
Satiric
Confessional
Prophetic
Observational
Passionate
Bitter
Ambivalent
Playful
Ironic
Didactic
Reflective
Nostalgic
Melancholic
Ecstatic
Conversational
Formal
Colloquial
Surreal
Visionary
Documentary
Polemical
Intimate
Detached
Anxious
Triumphant
Mournful
Hopeful
Desperate
Serene
Defiant
Questioning
```

#### Rhetorical Genre (4 categories)
```
Epideictic    - Praise or blame (most common)
Deliberative  - Persuasion about future action
Forensic      - Accusation or defense
Mixed         - Combination
```

#### Discursive Structure (3 categories)
```
Monologic    - Single voice
Dialogic     - Two voices in dialogue
Polyvocal    - Multiple voices
```

#### Discourse Type
```
Direct discourse
Narrative report
Description
Commentary
Mixed
```

#### Diegetic vs. Mimetic (3 categories)
```
Mimetic      - Showing (dramatic presentation)
Diegetic     - Telling (narrative report)
Mixed        - Combination
```

#### Focalization (4 categories)
```
Internal     - Through character's perspective
External     - From outside, observer
Zero         - Omniscient narrator
Multiple     - Shifts between perspectives
```

#### Person (grammatical)
```
1st          - I, we
2nd          - you
3rd          - he, she, they
1st/2nd      - Shifting between I and you
1st/3rd      - Shifting between I and he/she/they
2nd/3rd      - Shifting between you and he/she/they
Mixed        - All three
```

#### Deictic Orientation
```
First person
Second person
Third person
Impersonal
Shifting
Mixed
```

#### Addressee Type
```
Direct address
Apostrophic address
Triangulated address
Self-address
Implied addressee
Multiple addressees
No addressee
```

#### Temporal Orientation
```
Present
Past
Future
Past/Present
Present/Future
Past/Present/Future
Atemporal
```

#### Temporal Structure
```
Linear
Recursive
Static
Fragmentary
Anaphoric catalog
Circular
Episodic
Stream of consciousness
```

#### Tradition (4 categories)
```
Original
Translation
Imitation
Adaptation
```

---

## Database Schema Summary

### Table: `poems` (Main table, 116,675 rows)
**Coverage**: 100%
**Fields**: 17 (all Tier 1 fields)

### Table: `authors` (Derived)
**Coverage**: ~12,500 unique authors
**Fields**: author_id, author_name, author_last, poem_count, first_appearance_year, last_appearance_year, metadata

### Table: `historical_context`
**Coverage**: 70-80% (~80,000-95,000 rows)
**Fields**: 10 (Tier 2 fields)

### Table: `prosodic_features`
**Coverage**: 40-60% (~40,000-70,000 rows)
**Fields**: 9 (Tier 3 fields)

### Table: `rhetorical_features`
**Coverage**: 1,000 rows (research subset only)
**Fields**: 16 (Tier 4 fields)

### Table: `embeddings` (Future BERT work)
**Coverage**: As generated
**Fields**: poem_id, model_version, line_embeddings, stanza_embeddings, poem_embedding, created_at

---

## CSV File Structure

### `data/metadata/corpus_final_metadata.csv`
**Primary metadata file with all Tier 1-3 fields**

Columns (in order):
```
poem_id,
title,
author,
author_last,
date,
year_approx,
source,
source_url,
filepath,
filename,
length_lines,
length_words,
content_hash,
period,
literary_movement,
mode,
confidence_period,
confidence_movement,
confidence_mode,
genre,
meter,
rhyme,
stanza_structure,
confidence_genre,
confidence_meter,
confidence_rhyme
```

### `data/metadata/research_subset_rhetoric.csv`
**Research subset with all Tier 4 fields**

Additional columns:
```
register,
rhetorical_genre,
discursive_structure,
discourse_type,
diegetic_mimetic,
focalization,
person,
deictic_orientation,
addressee_type,
deictic_object,
temporal_orientation,
temporal_structure,
tradition,
annotated_by,
annotated_at,
annotation_notes
```

---

## Data Quality Indicators

### Confidence Scores
All AI-generated classifications include confidence scores (0.0-1.0):
- **>0.90**: High confidence (accept)
- **0.70-0.90**: Medium confidence (review sample)
- **<0.70**: Low confidence (manual review required)

### Coverage Targets
- **Tier 1**: 100% (automated)
- **Tier 2**: 70-80% (high-confidence AI only)
- **Tier 3**: 40-60% (formal poetry only)
- **Tier 4**: 1,000 poems (gold standard)

### Null Values
Null values acceptable for:
- Free verse poems (meter, rhyme)
- Experimental poetry (stanza_structure, genre)
- Low-confidence AI predictions (period, movement, mode)
- Non-research subset (all Tier 4 fields)

---

## Example: Complete Metadata for a Poem

**Sylvia Plath - "Daddy" (Poem #42)**

```json
{
  // Tier 1: Automated Basic Metadata
  "poem_id": 42,
  "title": "Daddy",
  "author": "Plath, Sylvia",
  "author_last": "Plath",
  "date": "1962",
  "year_approx": 1962,
  "source": "poetry_platform",
  "source_url": "https://www.poetryfoundation.org/poems/48999/daddy",
  "filepath": "Plath, Sylvia/000042_Daddy_Plath_Sylvia_1962.txt",
  "filename": "000042_Daddy_Plath_Sylvia_1962.txt",
  "length_lines": 80,
  "length_words": 512,
  "content_hash": "a3f5c8...",

  // Tier 2: Historical Context (AI-assisted)
  "period": "Postwar",
  "literary_movement": "Confessional",
  "mode": "Lyric",
  "confidence_period": 0.94,
  "confidence_movement": 0.89,
  "confidence_mode": 0.96,
  "classification_method": "ai_local_llm",
  "reviewed_by": null,
  "reviewed_at": null,

  // Tier 3: Prosodic Features (semi-automated)
  "genre": null,  // Not a fixed form
  "meter": "Modified villanelle",
  "rhyme": "Loose rhyme scheme",
  "stanza_structure": "16 five-line stanzas",
  "confidence_meter": 0.72,
  "confidence_rhyme": 0.68,

  // Tier 4: Rhetorical Features (manual, research subset only)
  "register": "Confessional",
  "rhetorical_genre": "Epideictic",
  "discursive_structure": "Monologic",
  "discourse_type": "Direct discourse",
  "diegetic_mimetic": "Mimetic",
  "focalization": "Internal",
  "person": "1st",
  "deictic_orientation": "First person",
  "addressee_type": "Direct address",
  "deictic_object": "Father",
  "temporal_orientation": "Past and present",
  "temporal_structure": "Recursive",
  "tradition": "Original",
  "annotated_by": "justin",
  "annotated_at": "2025-03-15T09:30:00",
  "annotation_notes": "Complex father-daughter relationship, Holocaust imagery"
}
```

---

## Usage Notes

### Querying by Confidence
```sql
-- Only high-confidence historical classifications
SELECT * FROM historical_context
WHERE confidence_period > 0.90
  AND confidence_movement > 0.90
  AND confidence_mode > 0.90;
```

### Handling Nulls
```sql
-- Find poems with complete prosodic metadata
SELECT * FROM prosodic_features
WHERE genre IS NOT NULL
  AND meter IS NOT NULL
  AND rhyme IS NOT NULL
  AND stanza_structure IS NOT NULL;
```

### Research Subset
```sql
-- Get fully annotated poems only
SELECT p.*, hc.*, pf.*, rf.*
FROM poems p
JOIN historical_context hc ON p.poem_id = hc.poem_id
JOIN prosodic_features pf ON p.poem_id = pf.poem_id
JOIN rhetorical_features rf ON p.poem_id = rf.poem_id;
```

---

## Extending the Schema

### Adding New Fields
1. Add column to appropriate CSV
2. Update database schema
3. Run migration script
4. Update this documentation

### Adding New Controlled Vocabulary Values
1. Update this documentation
2. Ensure database constraints allow new values
3. Retrain classification models if needed

---

## References

- **Period/Movement definitions**: Based on Norton Anthology of English Literature
- **Rhetorical categories**: Aristotle's Rhetoric (epideictic, deliberative, forensic)
- **Narratological terms**: Gérard Genette, Mieke Bal
- **Prosodic terminology**: Princeton Encyclopedia of Poetry and Poetics
