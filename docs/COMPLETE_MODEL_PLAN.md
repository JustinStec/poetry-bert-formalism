# Complete Model Development Plan
## Poetry BERT Formalism Project

**Last Updated**: November 12, 2025
**Status**: Phase 3B in progress

---

## Overview: Two Parallel Model Systems

This project develops **two distinct model systems** for poetry analysis:

### System A: Layered BERT for Historical Poetry (EEBO-BERT Research)
**Purpose**: Analyze Shakespeare & Early Modern poetry with historical semantics
**Status**: EEBO-BERT (Layer 1) complete, Layers 2-3 need retraining
**Goal**: Academic publications on semantic complexity & formalism

### System B: LLM Classification for Contemporary Corpus
**Purpose**: Classify 116K contemporary poems across 28 metadata dimensions
**Status**: Phase 3B in progress - preparing training data
**Goal**: Build comprehensive poetry corpus database with rich metadata

These systems are **independent** but complementary.

---

# SYSTEM A: Layered BERT Architecture

## Research Goal

**Question**: How do historical semantics and poetic conventions interact in Early Modern poetry?

**Method**: Three-layer specialized BERT + trajectory tortuosity analysis

**Target**: Publication in Digital Scholarship in the Humanities (primary) + Poetics Today (secondary)

---

## Architecture

```
bert-base-uncased (110M params)
    ↓ MLM fine-tune on 61K EEBO texts (1595-1700)
LAYER 1: EEBO-BERT
    Historical semantics for Early Modern English
    ✅ STATUS: Complete (418MB, in Google Drive)
    📍 LOCATION: Google Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/
    🎯 USE: Base for Shakespeare analysis

    ↓ MLM fine-tune on 17.7M poetry lines
LAYER 2: Poetry-EEBO-BERT
    Historical + poetic specialization
    ❌ STATUS: Need to retrain (previous corrupted)
    📦 TRAINING DATA: Shakespeare + Gutenberg + Core Poets + PoetryDB
    🎯 USE: Historical poetry analysis

    ↓ Concatenate prosodic features
LAYER 3: +Prosody Conditioning
    Meter + rhyme + line position features
    ⏸️ STATUS: Awaiting Layer 2
    🎯 USE: Test "form as semantic constraint" hypothesis
```

---

## Layer 1: EEBO-BERT (✅ COMPLETE)

### Training Details
- **Base**: `bert-base-uncased`
- **Corpus**: EEBO-TCP 1595-1700 (61,315 texts, ~8GB)
- **Method**: Masked Language Modeling (15% mask rate)
- **Epochs**: 3
- **Hardware**: Google Colab A100
- **Time**: ~8 hours
- **Output**: 418MB model (config.json, model.safetensors, vocab.txt)

### Current Status
- ✅ Training complete (October 27, 2025)
- ✅ Model saved in Google Drive
- ✅ Tested on Shakespeare sonnets
- ❓ Unknown if uploaded to HuggingFace (need to check)

### Results
- **Trajectory tortuosity**: 3.45 (vs. 3.17 base BERT)
- **Improvement**: +8.8% semantic complexity detection
- **Interpretation**: Captures historical nuances lost in base BERT

### Next Steps for Layer 1
1. **Verify HuggingFace upload** (check `justinstec/eebo-bert`)
2. **If not uploaded**: Use `upload_to_huggingface.py`
3. **Copy to M4 Max**: For continued training
4. **Continue training on 18th/19th/20th century corpora** (expand beyond 1595-1700)

---

## Layer 2: Poetry-EEBO-BERT (❌ NEEDS RETRAINING)

### Why Retrain?
- Previous version corrupted (training archive had errors)
- Need clean poetry corpus

### Training Plan
1. **Prepare corpus**:
   - Shakespeare Complete Works (✓ have: 31MB JSONL)
   - Project Gutenberg Poetry (need to collect)
   - Core 27 Poets (need to collect)
   - PoetryDB (need to collect)
   - **Target**: 17.7M lines

2. **Training setup**:
   - **Base**: EEBO-BERT (not bert-base-uncased!)
   - **Method**: Masked Language Modeling
   - **Epochs**: 3
   - **Hardware**: M4 Max (MLX) or Colab A100
   - **Time**: ~6-8 hours

3. **Validation**:
   - Test on Shakespeare sonnets
   - Compare trajectory tortuosity to:
     - base BERT (3.17)
     - EEBO-BERT (3.45)
     - Poetry-BERT independent path (3.59)
   - **Expected**: ~3.5-3.6 (historical + poetry)

### Training Data Collection
- [ ] Shakespeare ✓ (already have)
- [ ] Gutenberg Poetry (fetch from Gutenberg Project)
- [ ] Core 27 Poets (collect complete works)
- [ ] PoetryDB (API or scrape)
- [ ] Clean & deduplicate
- [ ] Format as JSONL
- [ ] Split train/val

---

## Layer 3: Prosodic Conditioning (⏸️ AWAITING LAYER 2)

### Method
Not a neural layer - **feature concatenation** at analysis time:

```python
# Get embeddings from Poetry-EEBO-BERT
embeddings = model(poem_text)

# Extract prosodic features
prosody = extract_features(poem_text)
# - meter_type (iambic, trochaic, etc.)
# - rhyme_scheme (ABAB, AABB, etc.)
# - line_position (normalized 0-1)
# - stanza_position
# - sonnet_quatrain_indicator

# Concatenate
analysis_vector = concat([embeddings, prosody])

# Measure tortuosity
complexity = trajectory_tortuosity(analysis_vector)
```

### Research Questions
1. Does adding prosodic features change semantic complexity?
2. **Hypothesis**: Form acts as constraint → reduces complexity
3. **Expected result**: -2% to -2.5% complexity with prosody

### Implementation
- Script: `src/poetry_bert/analysis/prosodic_features.py`
- Input: Poetry-EEBO-BERT embeddings
- Output: Enhanced embeddings for tortuosity analysis

---

## Publications from System A

### Paper 1: Digital Humanities (Primary)
**Title**: "Measuring Semantic Complexity in Shakespeare's Sonnets: A Layered BERT Architecture with Prosodic Conditioning"

**Target**: Digital Scholarship in the Humanities (Oxford UP)

**Status**: Need Layer 2 results first

**Outline**:
1. Introduction - Poetry & computational semantics
2. Related Work - BERT specialization, historical NLP
3. Methodology - Trajectory tortuosity + 3-layer architecture
4. Experiments - Shakespeare's 154 sonnets
5. Results - Layer effects + prosodic conditioning
6. Discussion - Form as semantic constraint
7. Conclusion

**Timeline**:
- Dec 2025: Complete Layers 2-3
- Jan 2026: Draft paper
- Feb 2026: Submit
- Mid-2026: Publication (after R&R)

### Paper 2: Literary Theory (Secondary)
**Title**: "Form as Semantic Constraint: Computational Evidence for Historical Poetics"

**Target**: Poetics Today

**Status**: Depends on Paper 1 acceptance

**Focus**:
- Theoretical implications
- Comparison with Donne, Spenser, Sidney
- Engagement with formalist tradition

---

# SYSTEM B: LLM Classification for 116K Corpus

## Goal

Classify all 116,674 contemporary poems in corpus across **28 metadata dimensions**:
- Historical (2): period, literary_movement
- Rhetorical (16): register, genre, person, deixis, etc.
- Formal (5): mode, meter, rhyme, etc.
- Admin (5): title, author, date, source, length

---

## Phases Overview

| Phase | Task | Status | Output |
|-------|------|--------|--------|
| **Phase 1** | Corpus assembly | ✅ Complete | 116,674 poems |
| **Phase 2** | Basic metadata | ✅ Complete | Author, title, year |
| **Phase 3A** | Training data prep | ✅ Complete | 397 poems + labels |
| **Phase 3B** | Fine-tune LLM | 🔄 In progress | Classification model |
| **Phase 3C** | Infer on corpus | ⏸️ Pending | 116K poems classified |
| **Phase 4** | Advanced features | 📅 Future | Prosody, themes |

---

## Phase 1: Corpus Assembly (✅ COMPLETE)

### Accomplishments
- **Source**: Poetry.com platform scrape
- **Poems collected**: 116,674
- **Authors**: 8,765
- **Total lines**: 6M
- **Total words**: 41M
- **Storage**: 551MB (text files)
- **Organization**: By author directories

### Quality Control
- Removed non-English poems
- Removed AI-generated poems
- Removed prose
- Deduplicated
- Validated metadata

### Files
- **Texts**: `Data/corpus/texts/` (by author)
- **Metadata**: `Data/corpus/metadata.csv` (41MB)
- **Statistics**: `Data/corpus/statistics.txt`

---

## Phase 2: Basic Metadata (✅ COMPLETE)

### Fields Added
1. `poem_id` - Unique ID (1-116674)
2. `title` - Poem title
3. `author` - Author name (Last, First)
4. `year_approx` - Estimated year (if known)
5. `source` - poetry_platform
6. `source_url` - Original URL
7. `length_lines` - Line count
8. `length_words` - Word count
9. `filepath` - Local path to text file

### Files
- `Data/corpus/metadata.csv` (41MB, 116,675 rows)

---

## Phase 3A: Training Data Preparation (✅ COMPLETE Nov 12)

### Goal
Create labeled dataset for fine-tuning LLM to classify poems

### Approach
1. **Gold standard** (53 poems): Expert-curated classifications
2. **Canonical poems** (404 poems): LLM few-shot classification → manual cleanup
3. **Text extraction**: Match to corpus, extract full texts
4. **Final dataset**: 397 poems with texts + 28 labels

### Steps Completed
1. ✅ Expanded schema from 19 → 28 fields
2. ✅ Added `narrative_level` column (Genette's framework)
3. ✅ Generated list of 404 canonical poems
4. ✅ Few-shot classification with Mistral-7B-Instruct
5. ✅ Cleaned taxonomy (467 corrections)
6. ✅ Merged with 53 gold-standard poems
7. ✅ **Matched 397/457 poems to corpus** (matched by title/author)
8. ✅ **Extracted full texts via SCP from M4 Max**

### Results
- **Training examples**: 397 poems
- **With full text**: 397 (100%)
- **Average text length**: ~6K characters
- **All 28 fields**: Complete
- **Coverage**: All periods (Middle English → Contemporary)

### Files
- **Primary dataset**: `Data/training/phase3_classifications/training_dataset_complete.jsonl`
  - 397 poems
  - Full text + 28 classification labels
  - Ready for instruction tuning

- **Supporting files**:
  - `training_set_457_poems.csv` - Metadata for all 457
  - `gold_standard_52_poems.csv` - Expert labels
  - `404_poems_classified.csv` - LLM classifications

### Schema (28 Fields)

#### Historical (2)
- `period`: Tudor, Elizabethan, Jacobean, Caroline, Interregnum, Restoration, Neoclassical, Romantic, Victorian, Modernist, Postwar, Contemporary
- `literary_movement`: Renaissance, Metaphysical, Augustan, Romanticism, Imagism, Modernism, Beat, Confessional, etc.

#### Rhetorical (16)
- `register`: Emotional tone (Meditative, Celebratory, Elegiac, etc.)
- `rhetorical_genre`: Epideictic, Deliberative, Forensic, Mixed
- `discursive_structure`: Monologic, Dialogic, Polyvocal
- `discourse_type`: Description, Direct discourse, Commentary, Narrative report
- `narrative_level`: Extradiegetic, Intradiegetic (blank for pure lyric)
- `diegetic_mimetic`: Diegetic (telling), Mimetic (showing), Mixed
- `focalization`: Zero, Internal, External, Multiple
- `person`: 1st, 2nd, 3rd, Mixed
- `deictic_orientation`: Spatial, Personal, Temporal, etc.
- `addressee_type`: Self, Direct, Apostrophic, Unaddressed
- `deictic_object`: Subject description
- `temporal_orientation`: Present, Past, Future, Atemporal
- `temporal_structure`: Static, Linear, Recursive, Fragmentary
- `tradition`: Original, Translation, Imitation, Adaptation
- *(2 more rhetorical fields)*

#### Formal (5)
- `mode`: Lyric, Narrative, Dramatic, Mixed
- `genre`: Sonnet, Ode, Elegy, Epic, Ballad, etc.
- `stanza_structure`: Description of stanza form
- `meter`: Iambic pentameter, Trochaic tetrameter, Free verse, etc.
- `rhyme`: ABAB, AABB, unrhymed, etc.

#### Administrative (5)
- `title`, `author`, `year_approx`, `poem_id`, `text`

---

## Phase 3B: Fine-Tune LLM (🔄 IN PROGRESS)

### Goal
Train LLM to predict all 28 classification fields from poem text

### Current Status
- ✅ Training data complete (397 poems)
- ⏸️ **PAUSED for system reorganization**
- Next: Format instruction-tuning dataset

### Plan

#### Step 1: Format Instruction Dataset
```jsonl
{
  "prompt": "Classify this poem across 28 metadata dimensions:\n\n{poem_text}\n\nProvide classifications for: period, literary_movement, register, ...",
  "completion": "period: Romantic\nliterary_movement: Romanticism\nregister: Meditative\n..."
}
```

**Script**: `scripts/phase3/format_instruction_dataset.py`

#### Step 2: Choose Fine-Tuning Approach

**Option A: MLX on M4 Max** (Preferred - local, free)
- Model: Llama-3-8B or Mistral-7B
- Method: LoRA (Low-Rank Adaptation)
- Framework: MLX (Apple Silicon optimized)
- Hardware: M4 Max (40 GPU cores)
- Time: 1-2 hours
- Cost: $0

**Option B: Google Colab** (Backup - if M4 Max insufficient)
- Model: Same as Option A
- Hardware: T4/A100 GPU
- Time: 2-4 hours
- Cost: Free tier or $10/month

#### Step 3: Training Configuration
```python
# Training params
base_model = "meta-llama/Llama-3-8B"  # or "mistralai/Mistral-7B-Instruct-v0.2"
method = "LoRA"  # Low-rank adaptation
rank = 16
alpha = 32
epochs = 3
batch_size = 4
learning_rate = 2e-4
warmup_steps = 100

# Data split
train_size = 357  # 90%
val_size = 40     # 10%
```

#### Step 4: Validation
- Hold out 40 poems
- Check accuracy per field
- Manual review of 10 sample outputs
- Acceptable accuracy: >80% for core fields

#### Step 5: Save Model
- Format: HuggingFace Transformers
- Upload to: `justinstec/poetry-classifier-llama3` (or Mistral variant)
- Include: Model card with metrics

### Timeline
- Day 1: Format dataset + setup MLX
- Day 2: Train model
- Day 3: Validate + save
- **Total**: 3 days active work

---

## Phase 3C: Infer on Full Corpus (⏸️ PENDING)

### Goal
Apply trained model to all 116,674 poems

### Plan

#### Batch Processing
```python
# Process in batches
batch_size = 32
total_batches = 116674 // 32 = 3646 batches

# Runtime estimate
time_per_poem = 2 seconds  # inference
total_time = 116674 * 2 / 3600 = ~65 hours

# With batching optimization
actual_time = ~12-24 hours on M4 Max
```

#### Implementation
1. Load fine-tuned model
2. Read poems from `Data/corpus/texts/`
3. Batch inference (32 poems at a time)
4. Save results progressively (checkpoint every 1000)
5. Merge classifications with `corpus_metadata.csv`

#### Error Handling
- Log poems that fail classification
- Retry with different prompt
- Manual review of flagged cases
- Missing values: mark as "Unknown" + confidence score

#### Output
- **Updated metadata**: `corpus_final_metadata_v2.csv`
  - Original 9 columns
  - +28 classification columns
  - = 37 total columns
- **Confidence scores**: Per-field confidence
- **Error log**: Poems needing manual review

### Timeline
- Setup: 1 day
- Inference: 1-2 days (12-24 hours runtime)
- Validation: 1 day (spot checks)
- **Total**: 3-4 days

---

## Phase 4: Advanced Features (📅 FUTURE)

### Prosodic Analysis
- Meter detection (iambic, trochaic, etc.)
- Rhyme scheme extraction
- Scansion (stress patterns)
- Caesura detection
- Enjambment detection

**Method**: Rule-based + ML hybrid
**Tools**: `prosodic` library + custom

### Thematic Analysis
- Topic modeling (LDA or neural)
- Emotion classification
- Imagery detection (sight, sound, touch, etc.)
- Figurative language (metaphor, simile, etc.)

**Method**: Fine-tuned transformers
**Base models**: RoBERTa or DeBERTa

### Network Analysis
- Intertextuality detection
- Influence networks
- Stylistic similarity

**Method**: Embedding-based similarity

---

## Timeline Summary

### Completed (✅)
- **Oct-Nov 2025**: Phase 1 (Corpus assembly)
- **Nov 2025**: Phase 2 (Basic metadata)
- **Nov 11-12, 2025**: Phase 3A (Training data)

### In Progress (🔄)
- **Nov 12, 2025**: System reorganization (2 hours)
- **Nov 13-15, 2025**: Phase 3B (Format + train + validate, 3 days)

### Upcoming (📅)
- **Nov 16-19, 2025**: Phase 3C (Infer on corpus, 3-4 days)
- **Nov 20+**: Validation & cleanup
- **Dec 2025+**: Phase 4 (Advanced features)

### EEBO-BERT Continuation (📅)
- **Dec 2025**: Collect poetry corpora (17.7M lines)
- **Jan 2026**: Train Poetry-EEBO-BERT (Layer 2)
- **Jan 2026**: Implement prosodic conditioning (Layer 3)
- **Feb 2026**: Shakespeare analysis + paper draft
- **Spring 2026**: Submit to journals

---

## Critical Path

### To Resume Phase 3B (TODAY):
1. ✅ Complete system audit
2. 🔄 Execute reorganization plan (~2 hours)
3. ➡️ Format instruction-tuning dataset
4. ➡️ Train LLM on M4 Max
5. ➡️ Validate model
6. ➡️ Run inference on 116K corpus

### To Restart EEBO-BERT Research (DEC):
1. Verify EEBO-BERT on HuggingFace
2. Copy to M4 Max
3. Collect clean poetry corpora
4. Train Poetry-EEBO-BERT
5. Implement Layer 3 prosodic features
6. Analyze Shakespeare sonnets
7. Write papers

---

## Resource Requirements

### Storage
- **Air**: 10GB (code + small data)
- **M4 Max**: 1.5GB (corpus + models + results)
- **Google Drive**: 10GB (EEBO-BERT + backups)
- **HuggingFace**: 2GB (models)

### Compute
- **Phase 3B training**: M4 Max (1-2 hours)
- **Phase 3C inference**: M4 Max (12-24 hours)
- **EEBO Layer 2 training**: Colab A100 (6-8 hours) or M4 Max
- **Layer 3 analysis**: M4 Max (light compute)

### Budget
- **HuggingFace**: Free tier sufficient
- **Colab**: Free tier + Pro ($10/month if needed)
- **Total cost**: $0-10/month

---

## Success Metrics

### System A (EEBO-BERT)
- ✅ Layer 1 complete (+8.8% vs base BERT)
- 🎯 Layer 2 target: +10-15% vs EEBO-BERT
- 🎯 Layer 3 effect: -2% to -2.5% with prosody
- 🎯 Publication: 2 papers accepted by mid-2026

### System B (Corpus Classification)
- ✅ 397 training examples complete
- 🎯 Fine-tuning accuracy: >80% per field
- 🎯 Corpus coverage: 116,674 poems classified
- 🎯 Missing rate: <5% per field
- 🎯 Manual validation: >90% accuracy on sample

---

## Questions?

See detailed documentation:
- `docs/PHASE_3_PROGRESS.md` - Phase 3A methodology
- `docs/RESEARCH_PLAN.md` - EEBO-BERT papers
- `docs/REORGANIZATION_PLAN.md` - System cleanup
- `docs/TRAINING_GUIDE.md` - Technical setup

