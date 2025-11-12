# Phase 3: Historical & Rhetorical Classification

**Status**: Ready to implement
**Location**: M4 Max (MLX-optimized)
**Data**: 116,674 contemporary poems + 52 canonical training examples

---

## Overview

Phase 3 adds **19 new metadata columns** to classify each poem by:
- Historical period (12 categories)
- Literary movement (13+ categories)
- Rhetorical features (16 detailed categories)

**Training Data**: 52 pre-classified canonical poems (Shakespeare, Dickinson, Wordsworth, etc.)
**Target Corpus**: 116,674 contemporary Poetry Platform poems

---

## New Metadata Schema (19 Columns)

### Historical Classification (2 columns)

1. **period** - Historical period
   - Tudor, Elizabethan, Jacobean, Caroline, Interregnum, Restoration
   - Neoclassical, Romantic, Victorian, Modernist, Postwar, Contemporary

2. **literary_movement** - Literary movement
   - Renaissance, Metaphysical, Augustan, Graveyard School
   - Romanticism, Pre-Raphaelite, Imagism, Modernism
   - Harlem Renaissance, Beat, Black Arts, Confessional, Language Poetry

### Rhetorical Classification (16 columns)

3. **register** - Emotional tone/stance
   - Examples: Meditative, Warning, Pleading, Celebratory, Argumentative, Elegiac

4. **rhetorical_genre** - Classical rhetoric category
   - Epideictic (praise/blame)
   - Deliberative (persuasion about future action)
   - Forensic (judgment about past action)
   - Mixed

5. **discursive_structure** - Voice structure
   - Monologic (single voice)
   - Dialogic (two voices)
   - Polyvocal (multiple voices)

6. **discourse_type** - Mode of discourse
   - Description, Direct discourse, Commentary, Narrative report, Mixed

7. **diegetic_mimetic** - Narrative mode
   - Diegetic (telling)
   - Mimetic (showing)
   - Mixed

8. **focalization** - Perspective/point of view
   - Zero (objective/omniscient)
   - Internal (character's perspective)
   - External (outside observer)
   - Multiple

9. **person** - Grammatical person
   - 1st, 2nd, 3rd, Mixed

10. **deictic_orientation** - Spatial/personal deixis
    - Impersonal, Second person, Apostrophic, First person, etc.

11. **addressee_type** - Who is addressed
    - Unaddressed, Direct address, Apostrophic address, Self-address, etc.

12. **deictic_object** - What/who is the focus
    - Free text describing the poem's subject/addressee

13. **temporal_orientation** - Time reference
    - Present, Past, Future, Atemporal, Mixed

14. **temporal_structure** - Time organization
    - Static (timeless/frozen moment)
    - Linear (chronological progression)
    - Recursive (circular/returning)
    - Fragmentary (discontinuous)

15. **tradition** - Literary lineage
    - Original, Translation, Imitation, Adaptation

16. **year_approx** - Already exists in corpus ✓

---

## Training Data

### Source Files
- `/Users/justin/Repos/AI Project/archive/old_metadata/corpus_metadata/Historical-corpus_metadata.csv` (53 poems)
- `/Users/justin/Repos/AI Project/archive/old_metadata/corpus_metadata/Rhetoric-Table 1.csv` (52 poems)

### Distribution

**By Period** (53 poems):
- Modernist: 9
- Postwar: 9
- Victorian: 7
- Romantic: 6
- Contemporary: 6
- Elizabethan: 3
- Neoclassical: 3
- Tudor, Jacobean, Caroline, Interregnum, Restoration: 2 each

**By Literary Movement** (32 labeled):
- Renaissance: 8
- Romanticism: 6
- Modernism: 4
- Metaphysical, Harlem Renaissance, Confessional: 3 each
- Augustan, Imagism: 2 each
- 7 movements with 1 example each

### Sample Poems
1. "Shall I Compare Thee to a Summer's Day" - Shakespeare (Jacobean, Renaissance, Argumentative/Epideictic)
2. "I'm Nobody! Who are you?" - Dickinson (Victorian, Playful/Deliberative)
3. "Howl" - Ginsberg (Postwar, Beat, Prophetic/Epideictic)
4. "Daddy" - Plath (Postwar, Confessional)
5. "In a Station of the Metro" - Pound (Modernist, Imagism)

---

## Implementation Strategy

### Approach: Few-Shot Fine-Tuning with MLX

**Model**: Llama-3-8B or Mistral-7B (Apple Silicon optimized)
**Framework**: MLX (Apple's ML framework for M4 Max)
**Training**: LoRA fine-tuning on 52 examples
**Inference**: Batch classification of 116,674 poems

### Why This Works

1. **Small training set is OK**: LLMs already understand literary concepts from pre-training
2. **Few-shot learning**: 52 examples teach the model our specific taxonomy
3. **Transfer learning**: Model learns from canonical poets, applies to contemporary work
4. **Multi-label classification**: One forward pass predicts all 16+ fields

---

## Pipeline Steps

### 1. Data Preparation (Air)

**Script**: `scripts/phase3/prepare_training_data.py`

```bash
# On MacBook Air (light work)
cd ~/Repos/AI\ Project
python3 scripts/phase3/prepare_training_data.py
```

**Tasks**:
- Merge Historical + Rhetoric CSVs (match by poem_id)
- Fetch full text for 52 canonical poems (from Gutenberg/Poetry Foundation)
- Format as instruction-tuning dataset:
  ```json
  {
    "instruction": "Classify this poem across historical, literary, and rhetorical dimensions.",
    "input": "<full poem text>",
    "output": "period: Romantic\nliterary_movement: Romanticism\nregister: Meditative\n..."
  }
  ```
- Split: 42 training, 10 validation

**Output**: `data/phase3/training_data.jsonl`

### 2. Transfer to M4 Max

```bash
# From Air
rsync -avz --progress \
  ~/Repos/AI\ Project/data/phase3/ \
  justin@100.65.21.63:~/poetry-bert-formalism/data/phase3/
```

### 3. Fine-Tune Model (M4 Max)

**Script**: `scripts/phase3/finetune_classifier.py`

```bash
# On M4 Max via SSH
ssh m4max
poetry-env
cd ~/poetry-bert-formalism
python scripts/phase3/finetune_classifier.py
```

**Method**: LoRA (Low-Rank Adaptation)
- Only train 0.1% of parameters
- Fast on M4 Max (~30-60 minutes)
- Low memory footprint

**Framework**: MLX + mlx-lm

**Output**:
- `models/phase3/poetry-classifier-lora/` (fine-tuned weights)
- `logs/phase3/training_metrics.json`

### 4. Validate Model (M4 Max)

**Script**: `scripts/phase3/validate_classifier.py`

```bash
python scripts/phase3/validate_classifier.py
```

**Tasks**:
- Test on 10 held-out poems
- Check accuracy per field
- Generate sample outputs for manual review

**Success Criteria**: >70% accuracy on validation set

### 5. Run Inference on Full Corpus (M4 Max)

**Script**: `scripts/phase3/classify_corpus.py`

```bash
# Batch processing with progress bar
python scripts/phase3/classify_corpus.py \
  --batch-size 32 \
  --checkpoint-every 10000
```

**Process**:
- Load 116,674 poem texts from CSV
- Batch inference (32 poems at a time)
- Save checkpoints every 10k poems
- Estimated time: 6-12 hours on M4 Max

**Output**: `data/phase3/classifications.csv`
```csv
poem_id,period,literary_movement,register,rhetorical_genre,...
1,Contemporary,,Meditative,Epideictic,...
2,Contemporary,,Celebratory,Epideictic,...
```

### 6. Merge into Main Metadata (Air)

**Script**: `scripts/phase3/merge_classifications.py`

```bash
# Transfer classifications back to Air
rsync -avz --progress \
  justin@100.65.21.63:~/poetry-bert-formalism/data/phase3/classifications.csv \
  ~/Repos/AI\ Project/data/phase3/

# Merge into main CSV
python3 scripts/phase3/merge_classifications.py
```

**Tasks**:
- Validate poem_id alignment
- Add 19 new columns to `corpus_final_metadata.csv`
- Create backup before merge
- Verify no data loss

**Output**: `data/metadata/corpus_final_metadata.csv` (now with 38 total fields)

---

## Quality Control

### Manual Spot Checks

Review 100 random classifications:
```bash
python3 scripts/phase3/sample_checker.py --n 100
```

Check for:
- Obvious misclassifications (e.g., contemporary poem labeled "Elizabethan")
- Consistency across related fields
- Reasonable distributions

### Distribution Analysis

```python
import pandas as pd

df = pd.read_csv('data/metadata/corpus_final_metadata.csv')

# Check period distribution
print(df['period'].value_counts())

# Check movement distribution
print(df['literary_movement'].value_counts(dropna=False))

# Check register distribution
print(df['register'].value_counts().head(20))
```

Expected results:
- Most poems: "Contemporary" period (our corpus is modern)
- Many null `literary_movement` (contemporary work may not fit historical movements)
- Diverse `register` values

---

## Schema Extensions (Future Phases)

### Phase 4: Formal/Prosodic Features
- Meter (iambic pentameter, free verse, etc.)
- Rhyme scheme (ABAB, blank verse, etc.)
- Stanza form (sonnet, villanelle, haiku, etc.)
- Line length patterns

### Phase 5: Thematic Classification
- Subject matter (love, nature, death, politics, etc.)
- Imagery types (visual, auditory, tactile, etc.)
- Symbolic content

---

## File Structure

```
AI Project/
├── data/
│   ├── metadata/
│   │   └── corpus_final_metadata.csv (38 fields after Phase 3)
│   ├── phase3/
│   │   ├── training_data.jsonl (52 canonical poems + full text)
│   │   ├── classifications.csv (116,674 classifications)
│   │   └── validation_results.json
│   └── processed/
│       └── poetry_platform_renamed/ (116,674 .txt files on M4 Max only)
├── archive/
│   └── old_metadata/
│       └── corpus_metadata/
│           ├── Historical-corpus_metadata.csv (53 poems)
│           └── Rhetoric-Table 1.csv (52 poems)
├── scripts/
│   └── phase3/
│       ├── prepare_training_data.py
│       ├── finetune_classifier.py
│       ├── validate_classifier.py
│       ├── classify_corpus.py
│       ├── merge_classifications.py
│       └── sample_checker.py
└── models/
    └── phase3/
        └── poetry-classifier-lora/ (M4 Max only)
```

---

## Timeline Estimate

| Task | Time | Machine |
|------|------|---------|
| Prepare training data | 2-4 hours | Air |
| Transfer to M4 Max | 10 mins | Both |
| Fine-tune model | 30-60 mins | M4 Max |
| Validate model | 15 mins | M4 Max |
| Classify corpus | 6-12 hours | M4 Max |
| Merge results | 30 mins | Air |
| Quality checks | 1-2 hours | Air |

**Total**: ~2-3 days (mostly automated, can run overnight)

---

## Success Metrics

- [x] Training data prepared (52 canonical poems with full text)
- [ ] Model fine-tuned (validation accuracy >70%)
- [ ] Full corpus classified (116,674 poems)
- [ ] New columns added to metadata CSV
- [ ] Spot check quality >80% reasonable
- [ ] No null/missing values for critical fields

---

## Next Steps

1. **Create Phase 3 scripts directory**
   ```bash
   mkdir -p scripts/phase3
   ```

2. **Write data preparation script** (`prepare_training_data.py`)
   - Merge Historical + Rhetoric CSVs
   - Fetch canonical poem texts
   - Format for instruction tuning

3. **Set up MLX fine-tuning** (`finetune_classifier.py`)
   - Load Llama-3-8B or Mistral-7B
   - LoRA configuration
   - Training loop with checkpointing

4. **Implement inference pipeline** (`classify_corpus.py`)
   - Batch processing
   - Progress tracking
   - Checkpoint saving

Ready to start implementation?
