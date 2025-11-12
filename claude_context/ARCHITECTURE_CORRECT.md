# Correct Architecture - ONE Integrated Layered System

**Date**: November 12, 2025
**Status**: Authoritative - Use This, Not COMPLETE_MODEL_PLAN.md

---

## ⚠️ Important Note

**DO NOT use `docs/COMPLETE_MODEL_PLAN.md`** - that document incorrectly describes this as two separate systems (System A and System B).

**This is ONE integrated architecture** where everything builds on historical BERTs.

---

## The Complete Architecture

### LAYER 1: Historical Language Models (4 Period-Specific BERTs)

Each BERT is trained on general texts from its period (NOT poetry-specific).

```
EEBO-BERT (1595-1700)
├── Status: ✅ COMPLETE
├── Training: 61K EEBO texts, 7.6GB
├── Location: Google Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/
├── Size: 418MB (config.json, model.safetensors, vocab.txt)
├── Result: +8.8% trajectory tortuosity vs base BERT (3.45 vs 3.17)
└── Purpose: Capture Early Modern English semantics (Shakespeare era)

ECCO-BERT (1700-1800)
├── Status: ❌ NOT STARTED - Need HathiTrust corpus
├── Planned: 18th century general texts (novels, essays, science, legal, etc.)
└── Purpose: Capture 18th century semantics (Augustan/Neoclassical era)

NCCO-BERT (1800-1900)
├── Status: ❌ NOT STARTED - Need HathiTrust corpus
├── Planned: 19th century general texts
└── Purpose: Capture 19th century semantics (Romantic/Victorian era)

Modern-BERT (1900-2000)
├── Status: ❌ NOT STARTED - Need HathiTrust corpus
├── Planned: 20th century general texts
└── Purpose: Capture modern English semantics (Modernist/Postwar era)
```

**Key Point**: These are NOT poetry models - they learn general historical language.

**Merge Strategy** (TBD - test all four):
- Option A: Sequential fine-tuning
- Option B: Model averaging
- Option C: Task arithmetic (Ilharco et al., 2023)
- Option D: Adapter layers

---

### LAYER 2: Poetry-Historical-BERT (Hierarchical Multi-Objective)

Takes merged Layer 1 and specializes for poetry using novel hierarchical approach.

```
Base Model: Merged historical BERTs (all 4 periods)

Training Corpus: 17.7M poetry lines
├── Shakespeare Complete Works
│   ├── Status: ✅ Have (31MB JSONL)
│   └── Size: 181K lines
├── Project Gutenberg Poetry
│   ├── Status: ❌ Need to collect
│   └── Size: 5.5M lines
├── Core 27 Poets (Donne, Milton, Pope, Wordsworth, Dickinson, etc.)
│   ├── Status: ❌ Need to collect
│   └── Size: 470K lines
└── PoetryDB
    ├── Status: ❌ Need to collect
    └── Size: ~50K lines

Training Method: Hierarchical Multi-Objective
├── Innovation: First BERT to train on hierarchical poetic structure
├── Loss Function: 0.5×MLM + 0.2×Line + 0.2×Quatrain + 0.1×Sonnet
├── MLM Loss: Standard masked language modeling
├── Line Contrastive: Adjacent/rhyming lines attract, random repel
├── Quatrain Contrastive: Same-quatrain lines attract
└── Sonnet Contrastive: Sonnet-level coherence

Implementation Status: ✅ COMPLETE
├── training/hierarchical_dataset.py
├── training/hierarchical_losses.py
├── training/hierarchical_trainer.py
└── notebooks/hierarchical_bert_training_colab.ipynb

Model Status: ❌ NEEDS TRAINING
└── Previous version corrupted and deleted
```

**Why Hierarchical?**
- Explicitly learns that adjacent lines are related
- Learns rhyme creates semantic connections
- Learns quatrains have thematic unity
- Learns sonnets are coherent wholes

**Expected Result**: Higher trajectory tortuosity than standard poetry fine-tuning.

---

### LAYER 3: Prosody Conditioning

Adds explicit formal feature awareness via feature concatenation (NOT a neural layer).

```
Method: Feature Concatenation at Analysis Time

Prosodic Features Extracted:
├── Stress patterns
│   └── Binary: stressed vs unstressed syllables (via prosodic library)
├── Meter position
│   └── Position within metrical foot (iambic vs trochaic detection)
├── Line position
│   └── Position within line/stanza (end-line effects: rhyme, enjambment)
└── Phonological features (future)
    ├── Rhyme schemes
    ├── Alliteration/assonance
    └── Sound symbolism

Analysis Pipeline:
1. Get embeddings from Poetry-Historical-BERT
2. Extract prosodic features from text
3. Concatenate: [embeddings | prosody_features]
4. Measure trajectory tortuosity on combined vector

Status: ⏸️ AWAITING LAYER 2
```

**Research Hypothesis**: Adding prosodic features will REDUCE complexity by -2% to -2.5%.
- **Why?**: Form acts as semantic constraint
- **Test**: Compare tortuosity with/without prosodic conditioning

---

### CLASSIFICATION HEAD: 28 Metadata Dimensions

Fine-tune complete layered model (1+2+3) for metadata classification.

```
Training Data: 397 Canonical Poems
├── Source: Matched from HEPC corpus
├── Labels: All 28 classification fields
├── Location: Data/training/phase3_classifications/training_dataset_complete.jsonl
├── Size: 2.7MB
├── Coverage: Medieval through 20th century
└── Status: ✅ COMPLETE (extracted Nov 12, 2025)

Classification Dimensions (28 fields):
├── Historical (2)
│   ├── period (Tudor, Elizabethan, Romantic, Victorian, Modernist, etc.)
│   └── literary_movement (Renaissance, Metaphysical, Romanticism, etc.)
├── Rhetorical (16)
│   ├── register (Meditative, Celebratory, Elegiac, etc.)
│   ├── rhetorical_genre (Epideictic, Deliberative, Forensic)
│   ├── discursive_structure (Monologic, Dialogic, Polyvocal)
│   ├── discourse_type (Description, Direct discourse, Commentary)
│   ├── narrative_level (Extradiegetic, Intradiegetic - Genette)
│   ├── diegetic_mimetic (Diegetic/telling, Mimetic/showing, Mixed)
│   ├── focalization (Zero, Internal, External, Multiple)
│   ├── person (1st, 2nd, 3rd, Mixed)
│   ├── deictic_orientation (Spatial, Personal, Temporal)
│   ├── addressee_type (Self, Direct, Apostrophic, Unaddressed)
│   ├── deictic_object (what is addressed)
│   ├── temporal_orientation (Present, Past, Future, Atemporal)
│   ├── temporal_structure (Static, Linear, Recursive, Fragmentary)
│   ├── tradition (Original, Translation, Imitation, Adaptation)
│   └── [2 more]
└── Formal (5)
    ├── mode (Lyric, Narrative, Dramatic, Mixed)
    ├── genre (Sonnet, Ode, Elegy, Epic, Ballad, etc.)
    ├── stanza_structure (description)
    ├── meter (Iambic pentameter, Free verse, etc.)
    └── rhyme (ABAB, AABB, unrhymed, etc.)

Method:
├── Add classification head to Poetry-Historical-BERT+Prosody
├── Fine-tune on 397 labeled poems
├── Train/val split: 357/40 (90/10%)
└── Target: >80% accuracy per field

Status: ⏸️ AWAITING LAYERS 2-3
```

---

### APPLICATION: HEPC Corpus Classification

Apply the complete trained model to all 116,674 historical poems.

```
HEPC: Historical English Poetry Corpus
├── Period Coverage: Medieval through 20th century
├── Total Poems: 116,674
├── Total Size: 551MB text files
├── Organization: By author directories
├── Metadata: Data/corpus/metadata.csv (41MB)
├── Location: M4 Max - Data/corpus/texts/
└── Periods Represented:
    ├── Medieval
    ├── Tudor
    ├── Elizabethan
    ├── Jacobean
    ├── Caroline
    ├── Interregnum
    ├── Restoration
    ├── Neoclassical
    ├── Romantic
    ├── Victorian
    ├── Modernist
    └── Postwar

Classification Pipeline:
1. Load trained classification model (Layers 1+2+3+head)
2. Batch process poems (32 at a time)
3. Generate 28 classification values per poem
4. Save with confidence scores
5. Output: corpus_metadata_v2.csv (9 existing + 28 new = 37 columns)

Estimated Runtime: 12-24 hours on M4 Max

Status: ⏸️ AWAITING COMPLETE MODEL
```

---

## Research Applications

### 1. Trajectory Tortuosity Analysis (Primary)

**Question**: How does semantic complexity vary by period, form, and author?

**Method**:
- Track word sequences through embedding space
- Measure tortuosity (path complexity)
- Compare across historical periods
- Test prosodic conditioning effect

**Metrics**:
- SPL (Summed Path Length)
- NSD (Net Semantic Displacement)
- Tortuosity = SPL / NSD
- RTO, ER, VPV, DC

**Corpus**: HEPC with 28-dimension classifications

**Publications**:
- Paper 1 (DH): Methodology + Shakespeare findings
- Paper 2 (Literary Theory): Deep interpretation + diachronic patterns
- Paper 3 (CS/Comp Ling): Framework for poetry-specific NLP

---

### 2. Career Arc Analysis

**Question**: How do poets evolve across their career?

**Examples**:
- Shakespeare: Early/Middle/Late/Final periods
- Romantics: Wordsworth, Coleridge across decades
- Modernists: Yeats, Eliot transformations

**Enabled By**: Period-aware embeddings + prosodic conditioning

---

### 3. Diachronic Formal Feature Tracking

**Question**: How do formal features change 1595-2000?

**Examples**:
- Enjambment rates across centuries
- Metrical regularity evolution
- Syntactic inversion patterns
- Figurative language density

**Enabled By**: Aligned embeddings + HEPC classifications

---

## Current Blockers & Next Steps

### Critical Blocker: Need HathiTrust Corpora

**What we need**:
- 18th century general texts (ECCO equivalent)
- 19th century general texts (NCCO equivalent)
- 20th century general texts

**Action**:
1. Access HathiTrust Research Center (IU credentials)
2. Create worksets by date range: 1700-1800, 1800-1900, 1900-2000
3. Filter: `language:eng AND publishDate:[YYYY TO YYYY]`
4. No genre restrictions (need all text types)
5. Download and preprocess
6. Train 3 additional historical BERTs

**Alternative Path**: Train Layer 2 on EEBO-BERT only as proof-of-concept for Shakespeare analysis, then retrain later with complete Layer 1.

---

### Secondary Blocker: Need Complete Poetry Corpus

**What we need**:
- Gutenberg Poetry (5.5M lines)
- Core 27 Poets (470K lines)
- PoetryDB (50K lines)

**We have**:
- ✅ Shakespeare (181K lines, 31MB JSONL)

**Action**:
1. Collect Gutenberg poetry works
2. Collect Core 27 Poets complete works
3. Collect PoetryDB
4. Merge into unified training corpus
5. Ready for Layer 2 training

---

## Timeline (Assuming HathiTrust Access)

### December 2025
- Acquire HathiTrust 18th-20th century corpora
- Preprocess and format
- Train ECCO-BERT, NCCO-BERT, Modern-BERT

### January 2026
- Test all 4 merge strategies
- Select best approach
- Merge Layer 1 models
- Collect complete poetry corpus (17.7M lines)

### February 2026
- Train Poetry-Historical-BERT (Layer 2) with hierarchical approach
- Implement prosodic conditioning (Layer 3)
- Validate on Shakespeare sonnets

### March 2026
- Fine-tune classification head on 397 training poems
- Run inference on 116K HEPC corpus
- Validate results

### April-June 2026
- Trajectory analysis across HEPC
- Career arc studies
- Diachronic formal feature analysis
- Write papers

---

## Files & Locations

### Code (Both Machines via Git)
- Repository: `git@github.com:JustinStec/poetry-bert-formalism.git`
- Air: `/Users/justin/Repos/AI Project/`
- Max: `~/poetry-bert-formalism/`

### Data
- **Air**: Small training data only
  - `Data/training/phase3_classifications/` (397 poems, 2.7MB)
- **Max**: Large corpus
  - `Data/corpus/texts/` (116K poems, 551MB)
  - `Data/corpus/metadata.csv` (41MB)

### Models
- **Google Drive**:
  - EEBO-BERT: `AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/` (418MB)
- **HuggingFace** (username: justinstec):
  - Status unknown - need to login and check
- **M4 Max**:
  - `models/` directory created for future trained models

---

## Key Documentation

**Read These** (Correct):
- `claude_context/START_HERE.md` - Quick reference for Claude
- `claude_context/ARCHITECTURE_CORRECT.md` - This file
- `docs/MODEL_ARCHITECTURE.md` - Hierarchical training implementation
- `archive/old_docs/ARCHITECTURE_OVERVIEW.md` - Original 3-layer plan
- `archive/old_docs/PROSODY_BERT_ARCHITECTURE.md` - Layer 3 technical details

**Avoid These** (Outdated/Incorrect):
- `docs/COMPLETE_MODEL_PLAN.md` - WRONG - describes two separate systems

---

**Last Updated**: November 12, 2025
**Authoritative**: YES - Use this over COMPLETE_MODEL_PLAN.md
