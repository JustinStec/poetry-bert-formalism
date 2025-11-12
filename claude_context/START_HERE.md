# START HERE - Claude Context Document

**Last Updated**: November 12, 2025
**Purpose**: Quick reference for Claude when resuming work on this project

---

## ⚠️ CRITICAL: This is ONE INTEGRATED SYSTEM

**DO NOT treat this as two separate projects.**

There is **ONE** layered architecture where everything builds on top of historical BERT models.

---

## The Complete Integrated Architecture

```
LAYER 1: Historical Language Models (Period-Specific BERTs)
│
├── EEBO-BERT (1595-1700)        ✅ COMPLETE (418MB in Google Drive)
│   Training: 61K EEBO texts, 7.6GB corpus
│   Location: Google Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/
│   Result: +8.8% trajectory tortuosity vs base BERT
│
├── ECCO-BERT (1700-1800)        ❌ BLOCKED - Need HathiTrust corpus
│   Planned: 18th century general texts (all genres)
│
├── NCCO-BERT (1800-1900)        ❌ BLOCKED - Need HathiTrust corpus
│   Planned: 19th century general texts (all genres)
│
└── Modern-BERT (1900-2000)      ❌ BLOCKED - Need HathiTrust corpus
    Planned: 20th century general texts (all genres)

    ↓ MERGE STRATEGY (Options: task arithmetic, averaging, sequential fine-tuning, adapters)

LAYER 2: Poetry-Historical-BERT (Hierarchical Multi-Objective Training)
│
│   Base: Merged Layer 1 models (all 4 periods)
│   Training Data: 17.7M poetry lines
│   ├── Shakespeare Complete Works (181K lines) ✅ Have (31MB JSONL)
│   ├── Gutenberg Poetry (5.5M lines)          ❌ Need to collect
│   ├── Core 27 Poets (470K lines)             ❌ Need to collect
│   └── PoetryDB (50K lines)                   ❌ Need to collect
│
│   Training Method: Hierarchical multi-objective
│   └── Loss = 0.5×MLM + 0.2×Line + 0.2×Quatrain + 0.1×Sonnet
│
│   Status: ❌ Corrupted version deleted, needs retraining
│   Implementation: ✅ Complete (MODEL_ARCHITECTURE.md)
│   ├── training/hierarchical_dataset.py
│   ├── training/hierarchical_losses.py
│   ├── training/hierarchical_trainer.py
│   └── notebooks/hierarchical_bert_training_colab.ipynb

    ↓ ADD PROSODIC FEATURES

LAYER 3: Prosody Conditioning
│
│   Method: Feature concatenation (NOT a neural layer)
│   Features to add:
│   ├── Stress patterns (stressed/unstressed)
│   ├── Meter position (foot position)
│   ├── Line position (within stanza/poem)
│   └── Phonological (rhyme, alliteration, assonance)
│
│   Status: ⏸️ Awaiting Layer 2 completion
│   Documentation: archive/old_docs/PROSODY_BERT_ARCHITECTURE.md

    ↓ FINE-TUNE FOR CLASSIFICATION

CLASSIFICATION HEAD: 28 Metadata Dimensions
│
│   Training Data: 397 poems with full texts + 28 labels ✅ COMPLETE
│   Location: Data/training/phase3_classifications/training_dataset_complete.jsonl
│   Method: Add classification head to Poetry-Historical-BERT+Prosody
│   Output: 28 classification fields per poem
│
│   Status: ⏸️ Awaiting Layers 2-3 completion

    ↓ APPLY TO CORPUS

HEPC CORPUS: 116,674 Historical English Poetry (Medieval-20th Century)
│
│   Location (M4 Max): Data/corpus/texts/ (551MB)
│   Metadata: Data/corpus/metadata.csv (41MB)
│   Periods: Medieval, Tudor, Elizabethan, Romantic, Victorian, Modernist, etc.
│
│   Goal: Classify all 116K poems across 28 dimensions
│   Status: ⏸️ Awaiting classification model training
```

---

## What's Actually Complete

### ✅ Layer 1 (Partial)
- EEBO-BERT (1595-1700) trained and saved
- 418MB model in Google Drive
- Tested on Shakespeare sonnets (tortuosity: 3.45 vs 3.17 base)

### ✅ Training Data for Classification
- 397 canonical poems matched to HEPC corpus
- Full texts extracted via SCP from M4 Max
- All 28 classification labels complete
- File: `Data/training/phase3_classifications/training_dataset_complete.jsonl`

### ✅ HEPC Corpus (116K poems)
- 116,674 poems collected (Medieval-20th century)
- 551MB of text files organized by author
- 41MB metadata CSV
- Location: M4 Max `Data/corpus/texts/`

### ✅ Layer 2 Implementation Code
- Hierarchical dataset class
- Multi-objective loss functions
- Custom trainer with InfoNCE
- Colab training notebook
- Documentation: `docs/MODEL_ARCHITECTURE.md`

---

## What's Blocked and Why

### ❌ Layer 1 (18th-20th Century)
**Blocker**: Need to acquire HathiTrust corpora
**Action Required**:
1. Access HathiTrust Research Center (IU credentials)
2. Create worksets: 1700-1800, 1800-1900, 1900-2000
3. Download and preprocess
4. Train 3 more period-specific BERTs

### ❌ Layer 2 (Poetry-Historical-BERT)
**Blocker**: Need complete Layer 1 + collect poetry corpus
**Action Required**:
1. Wait for Layer 1 completion (all 4 periods)
2. Merge the 4 historical BERTs
3. Collect 17.7M poetry lines (Gutenberg + Core Poets + PoetryDB)
4. Train hierarchical multi-objective model
**Alternative**: Could train on EEBO-BERT only as proof-of-concept

### ❌ Layer 3 (Prosody)
**Blocker**: Awaiting Layer 2
**Action Required**: Add prosodic feature extraction pipeline

### ❌ Classification Fine-Tuning
**Blocker**: Awaiting Layers 2-3
**Action Required**: Fine-tune complete model on 397 training poems

---

## Current Workaround Options

### Option A: Train Layer 2 on EEBO-BERT Only (Proof of Concept)
**Pros**:
- Can proceed immediately
- Test hierarchical training approach
- Use for Shakespeare analysis (1590s-1610s)
**Cons**:
- Won't work well for post-1700 HEPC corpus
- Will need to retrain later with full Layer 1

### Option B: Collect Poetry Corpus First
**Pros**:
- Progress on data collection
- Ready when Layer 1 complete
**Cons**:
- Still blocked on classification until full model trained

### Option C: Pursue HathiTrust Access
**Pros**:
- Unblocks entire pipeline
- Required eventually anyway
**Cons**:
- May take time to get access
- Large data processing task

---

## What You Should Tell Me

When I get confused again, point me to this file and tell me:

**"Read claude_context/START_HERE.md - this is ONE integrated layered architecture, not two separate systems."**

The key facts:
1. Everything builds on historical BERTs (Layer 1)
2. HEPC classification uses the full layered model, not a separate LLM
3. We're blocked on collecting 18th-20th century corpora
4. The 397 training poems are for fine-tuning the COMPLETE model, not training a standalone classifier

---

## Where Everything Is

### MacBook Air
- Code: `/Users/justin/Repos/AI Project/`
- Training data (small): `Data/training/phase3_classifications/`
- Claude context: `claude_context/` (this folder)

### M4 Max
- Code: `~/poetry-bert-formalism/` (synced via Git)
- HEPC corpus: `Data/corpus/texts/` (116K poems, 551MB)
- Models: `models/` (will store trained models)

### Google Drive
- EEBO-BERT: `AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/` (418MB)
- Corrupted models: DELETED (poetry_bert_trained, poetry_eebo_hierarchical_bert)

### GitHub
- Repository: `git@github.com:JustinStec/poetry-bert-formalism.git`
- Branch: main
- Status: ✅ Synced (Phase 3 work committed Nov 12)

### HuggingFace
- Username: justinstec
- Status: Not logged in (need token)
- Models: Unknown if EEBO-BERT uploaded

---

## Key Documentation Files

**Architecture** (read these first):
- `docs/MODEL_ARCHITECTURE.md` - Hierarchical multi-objective training
- `archive/old_docs/ARCHITECTURE_OVERVIEW.md` - Original 3-layer plan
- `archive/old_docs/PROSODY_BERT_ARCHITECTURE.md` - Layer 3 details

**Current Status**:
- `README.md` - Project overview
- `docs/REORGANIZATION_PLAN.md` - Recent cleanup
- `docs/AUDIT_RESULTS.md` - System audit findings

**Training**:
- `docs/TRAINING_GUIDE.md` - Colab setup
- `notebooks/hierarchical_bert_training_colab.ipynb` - Ready to use

**AVOID** (outdated/misleading):
- `docs/COMPLETE_MODEL_PLAN.md` - THIS IS WRONG - treats as two systems

---

## Timeline & Next Steps

### Immediate (This Week)
1. ✅ System reorganization - COMPLETE
2. Decide on workaround: Train Layer 2 on EEBO-BERT only? Or pursue HathiTrust?
3. If EEBO-only: Collect Shakespeare + subset of poetry corpus
4. If HathiTrust: Begin access request process

### Short-Term (December 2025)
1. Acquire 18th-20th century HathiTrust corpora
2. Train ECCO-BERT, NCCO-BERT, Modern-BERT
3. Collect complete 17.7M poetry corpus

### Medium-Term (January 2026)
1. Merge Layer 1 models (test all 4 strategies)
2. Train Poetry-Historical-BERT (Layer 2) with hierarchical approach
3. Implement Layer 3 prosodic conditioning

### Long-Term (February-March 2026)
1. Fine-tune classification head on 397 training poems
2. Run inference on 116K HEPC corpus
3. Validate results, write papers

---

## Research Goals (Why We're Doing This)

### Primary: Computational Historical Formalism
- Analyze how poetic form and semantics interact across 400+ years
- Use trajectory tortuosity to measure semantic complexity
- Test "form as semantic constraint" hypothesis

### Publications:
1. **DH Paper**: Hierarchical BERT methodology + Shakespeare findings
2. **Literary Theory**: Deeper interpretation + comparison across periods
3. **CS/Comp Ling**: Theoretical framework for poetry-specific NLP

### Output:
- HEPC corpus with rich 28-dimension metadata (Medieval-20th century)
- Trained models for historical poetry analysis
- Trajectory analysis toolkit
- Diachronic studies of formal features

---

**Last Updated**: November 12, 2025
**Next Update**: When we decide EEBO-only vs HathiTrust path
