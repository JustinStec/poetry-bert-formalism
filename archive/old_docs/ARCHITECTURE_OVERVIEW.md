# Three-Layer Architecture for Computational Historical Formalism

**Last Updated:** October 30, 2025

This document provides a comprehensive overview of the three-layer BERT architecture for analyzing formal features of poetry across historical periods (1595-2025).

---

## Overview

The project uses a **three-layer training strategy** to create BERT models that understand:
1. **Historical language patterns** (how English changed across centuries)
2. **Poetic conventions** (how poetry differs from prose)
3. **Prosodic structure** (formal features: meter, syntax, line boundaries, phonology)

These three layers are trained separately, then merged to create a unified model for diachronic formal feature analysis.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: HISTORICAL LANGUAGE             │
│                   Period-Specific BERT Models                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  EEBO-BERT        ECCO-BERT        NCCO-BERT    Modern-BERT │
│  (1595-1700)      (1700-1800)      (1800-1900)  (1900-2000) │
│                                                              │
│  7.6GB corpus     HathiTrust       HathiTrust   HathiTrust  │
│  ✓ Trained        ⏳ Pending       ⏳ Pending   ⏳ Pending   │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ MERGE (strategy TBD)
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 2: POETRY MODEL                     │
│                  Poetry-Specialized BERT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Gutenberg BERT                                              │
│  Trained on unified 6.2M-line poetry corpus                  │
│                                                              │
│  Sources:                                                    │
│  • Gutenberg: 1,191 works, 5.5M lines                       │
│  • Shakespeare: 40 works, 181K lines                         │
│  • Core 27 Poets: 51 works, 470K lines                      │
│  • PoetryDB: 3,162 poems                                     │
│                                                              │
│  Status: ~50% trained (checkpoint-395000)                    │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ ADD PROSODIC LAYERS
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LAYER 3: PROSODY CONDITIONING                   │
│            Formal Feature-Aware Embeddings                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Additional embedding layers for:                            │
│  • Stress patterns (stressed/unstressed syllables)           │
│  • Meter position (foot position within line)                │
│  • Line position (position within stanza/poem)               │
│  • Phonological features (rhyme, alliteration, assonance)    │
│                                                              │
│  Status: Architecture designed, awaiting Layer 1+2 merge     │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  APPLICATIONS  │
              └────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌────────┐    ┌────────┐
   │Semantic│    │ Career │    │Diachronic│
   │Trajec- │    │  Arc   │    │ Formal  │
   │ tory   │    │Analysis│    │ Feature │
   │Analysis│    │        │    │Tracking │
   └────────┘    └────────┘    └────────┘
```

---

## Layer 1: Historical Language Models

### Purpose
Learn period-specific semantic and syntactic patterns to enable diachronic analysis. Each BERT model is trained on general English texts from its century.

### Corpora

| Period | Corpus | Size | Source | Status |
|--------|--------|------|--------|--------|
| 1595-1700 | EEBO (Early English Books Online) | 7.6GB | Pre-existing | ✓ Trained |
| 1700-1800 | ECCO (18th Century Collections) | TBD | HathiTrust | ⏳ Acquiring |
| 1800-1900 | NCCO (19th Century Collections) | TBD | HathiTrust | ⏳ Acquiring |
| 1900-2000 | Modern English | TBD | HathiTrust | ⏳ Acquiring |

### Training Approach
- Standard BERT MLM (Masked Language Modeling) training
- Goal: Capture historical semantics and syntax
- Not poetry-specific (train on all genres: novels, essays, science, legal, religious, etc.)

### HathiTrust Acquisition Strategy
See: `scripts/download_hathitrust_corpus.py`, `scripts/preprocess_hathitrust_downloads.py`

1. Create worksets in HathiTrust Analytics Portal by date range
2. Filter: `language:eng AND publishDate:[YYYY TO YYYY]`
3. No genre restriction (want all text types)
4. Export and download via workset interface
5. OCR quality threshold: 90% minimum, 95% preferred

---

## Layer 2: Poetry Model

### Purpose
Learn poetic conventions: lineation, stanza structure, meter patterns, figurative language, poetic diction.

### Unified Poetry Corpus

**Total:** 6.2M lines across ~4,400 works

| Source | Works | Lines | Coverage |
|--------|-------|-------|----------|
| Gutenberg | 1,191 | 5.5M | 15th-20th c. poetry (broad) |
| Shakespeare | 40 | 181K | 1590-1613 (drama + sonnets) |
| Core 27 Poets | 51 | 470K | Canonical poets (Donne, Milton, Pope, Wordsworth, Dickinson, etc.) |
| PoetryDB | 3,162 | ~50K | Mixed periods |

**Status:** Unified SQLite database at `Data/poetry_unified.db`
- ✓ Gutenberg imported (1,191 works, 10.9M lines in database)
- ⏳ Shakespeare/Core Poets/PoetryDB import pending fix

### Training Approach
- Train BERT on complete unified corpus
- Current: ~50% trained (checkpoint-395000 on Gutenberg subset)
- Need to restart training on FULL unified corpus once Shakespeare/Core Poets/PoetryDB import completes

---

## Layer 3: Prosody Conditioning

### Purpose
Add explicit formal feature awareness to the merged historical+poetry model.

### Prosodic Features

**Four embedding layers** (see `PROSODY_BERT_ARCHITECTURE.md` for technical details):

1. **Stress Embeddings**
   - Binary: stressed vs. unstressed syllables
   - Extracted via `prosodic` library scansion

2. **Meter Position Embeddings**
   - Position within metrical foot (foot 1, 2, 3, etc.)
   - Enables iambic pentameter vs. trochaic tetrameter distinction

3. **Line Position Embeddings**
   - Position within line/stanza
   - Captures end-line effects (rhyme, enjambment)

4. **Phonological Embeddings** (future)
   - Rhyme schemes
   - Alliteration/assonance patterns
   - Sound symbolism features

### Training Approach
- Add prosodic embedding layers to merged Layer 1+2 model
- Continue MLM training with prosodic features as additional input
- Dataset: Annotated poetry from unified corpus (prosodic scansion pre-computed)

---

## Model Merging Strategy

**Open Research Question:** How to merge Layer 1 (period-specific historical BERTs) with Layer 2 (poetry BERT)?

### Options Under Consideration

**Option A: Sequential Fine-Tuning**
- Start with historical BERT for appropriate period
- Fine-tune on poetry corpus
- Advantage: Simple, preserves period-specific knowledge
- Disadvantage: May overwrite historical semantics

**Option B: Model Averaging**
- Average weights of historical BERT + poetry BERT
- Advantage: Preserves both knowledge types
- Disadvantage: May dilute both

**Option C: Task Arithmetic**
- Use task vectors (Ilharco et al., 2023)
- Compute: BERT_merged = BERT_base + α(BERT_history - BERT_base) + β(BERT_poetry - BERT_base)
- Advantage: Precise control over contribution weights
- Disadvantage: Requires careful hyperparameter tuning

**Option D: Adapter Layers**
- Keep historical BERT frozen
- Add adapter modules trained on poetry
- Advantage: Maintains historical knowledge perfectly
- Disadvantage: Additional parameters, complexity

**Current Status:** Testing all four approaches post-Layer 2 completion

---

## Applications

### 1. Semantic Trajectory Analysis

**Method:** Track word sequences through embedding space

**Metrics (see `Methodology/metrics_definitions.md`):**
- SPL (Summed Path Length)
- NSD (Net Semantic Displacement)
- Tortuosity (path complexity)
- RTO (Return-to-Origin tendency)
- ER (Exploration Radius)
- VPV (Velocity Per Verse)
- DC (Directional Coherence)

**Research Question:** Do real poems create distinctive semantic trajectories that LLM-generated poems cannot replicate?

**Corpus:** 53 canonical poems across periods
- Renaissance/Medieval: 12 poems
- Romantic: 12 poems
- Modernist: 12 poems
- Contemporary: 12 poems
- AI-generated (GPT-4): 5 poems for comparison

**Status:** Methodology documented in `Methodology/methods_log.md`, `Methodology/technical_notes.md`

### 2. Career Arc Analysis

**Research Question:** How do poets' formal features evolve across their career?

**Approach:**
- Shakespeare early/middle/late/final periods
- Romantic poets (Wordsworth, Coleridge across decades)
- Track metrical variation, syntactic complexity, semantic patterns

**Enabled by:** Prosody-conditioned embeddings with period-aware historical context

### 3. Diachronic Formal Feature Tracking

**Research Question:** How do formal features change across literary periods?

**Examples:**
- Enjambment rates 1600-2000
- Metrical regularity across centuries
- Syntactic inversion patterns
- Figurative language density

**Enabled by:** Aligned embeddings (via Procrustes) for cross-period comparison

---

## Data Organization

### Poetry Corpus Structure
```
Data/
├── poetry_unified.db              # SQLite database (all sources)
├── gutenberg_reconstructed.jsonl  # Gutenberg works (complete)
└── poetry_corpus/
    ├── shakespeare_complete_works.jsonl
    ├── core_poets_complete.jsonl
    └── poetrydb.jsonl
```

### Historical Corpora Structure (Future)
```
Data/
└── hathitrust/
    ├── raw/                       # Downloaded texts
    ├── hathitrust_1700_1800.jsonl # 18th century processed
    ├── hathitrust_1800_1900.jsonl # 19th century processed
    └── hathitrust_1900_2000.jsonl # 20th century processed
```

### Trained Models Structure
```
Google Drive: /My Drive/AI and Poetry/Historical Embeddings/
├── eebo_bert_finetuned/           # Layer 1 (1595-1700) ✓
├── gutenberg_bert_finetuned/      # Layer 2 (poetry) ~50%
├── gutenberg_bert_checkpoints/    # Training checkpoints
└── [future: ecco_bert, ncco_bert, modern_bert, prosody_bert]
```

---

## Timeline

### Immediate (Next 48 hours - CMU deadline: Nov 1)
1. ✓ Gutenberg corpus reconstructed
2. ⏳ BERT training completion (checkpoint-395000 → 100%)
3. ⏳ Extract embeddings for Shakespeare analysis
4. ⏳ Draft CMU writing sample (Sonnet 18 pilot study)

### Post-CMU (November-December 2025)
1. Fix unified database import (Shakespeare/Core Poets/PoetryDB)
2. Retrain poetry BERT on complete 6.2M line corpus
3. Acquire HathiTrust historical corpora (ECCO, NCCO, Modern)
4. Train period-specific BERTs (18th, 19th, 20th century)
5. Experiment with model merging strategies

### January-March 2026
1. Implement prosody conditioning (Layer 3)
2. Build formal annotation pipeline (automated scansion, syntax parsing)
3. Run semantic trajectory analysis on 53-poem corpus
4. Career arc analysis (Shakespeare periods, Romantic poets)

### April-June 2026
1. Scale formal feature tracking across full 6.2M line corpus
2. Diachronic studies (enjambment, meter, syntax evolution)
3. Write methodology paper
4. Write empirical paper (trajectory analysis results)

---

## Key Design Decisions

### Why Three Layers?

**Problem:** A single BERT trained on mixed historical + poetry corpus would conflate:
- Period-specific language change (historical semantics)
- Genre-specific conventions (poetic vs. prose)
- Formal structural features (meter, rhyme, lineation)

**Solution:** Separate training pathways that can be merged with control over contribution weights.

### Why Separate Historical and Poetry Corpora?

**Historical corpora** (Layer 1):
- Need to be large (millions of words per century)
- Must include all genres (not just poetry)
- Goal: Learn how English semantics/syntax changed

**Poetry corpus** (Layer 2):
- Can be smaller but must be high-quality
- Poetry-only (captures genre-specific patterns)
- Goal: Learn what makes poetry distinctive

**Analogy:** Historical BERTs learn "English in 1800"; Poetry BERT learns "how poetry works"; merged model knows "how poetry works in historical context."

### Why HathiTrust instead of ECCO/NCCO Direct Access?

**Practical reasons:**
- IU institutional access via HathiTrust Research Center
- No TDM (Text and Data Mining) restrictions
- Programmatic bulk download via worksets
- Better OCR quality on average
- Covers all needed periods (1700-2000)

**ECCO/NCCO via Gale Digital Scholar Lab** remains backup option if HathiTrust insufficient.

---

## Technical References

- **BERT Architecture:** `docs/PROSODY_BERT_ARCHITECTURE.md`
- **Trajectory Metrics:** `Methodology/metrics_definitions.md`
- **Methodology:** `Methodology/methods_log.md`, `Methodology/technical_notes.md`
- **Corpus Status:** `CURRENT_ARCHIVE_STATUS.md`
- **Expansion Strategy:** `ARCHIVE_BUILDING_STRATEGY.md`

---

## Open Questions

1. **Model merging:** Which approach (sequential, averaging, task arithmetic, adapters) best preserves both historical and poetic knowledge?

2. **Embedding alignment:** Should we use Procrustes alignment for cross-period comparison, or accept that period-specific semantic spaces are inherently incomparable?

3. **Prosodic features:** Are 4 prosodic embedding layers sufficient, or do we need more granular features (syllable stress strength, caesura, foot type)?

4. **Trajectory analysis:** Can semantic trajectory metrics (SPL, NSD, etc.) distinguish real from LLM-generated poetry? If so, which metrics are most diagnostic?

5. **Temporal resolution:** Are century-level periods appropriate, or should we use finer-grained periods (decades) or coarser ones (literary movements)?

---

**For questions or clarifications, see:** `PROJECT_STATUS.md`, `README.md`, or contact documentation.