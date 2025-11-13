# START HERE - Claude Context Document

**Last Updated**: November 12, 2025
**Purpose**: Quick reference for Claude when resuming work on this project

---

## Project Status: Phase 4 - Improving Classifications

**Current Approach:** Pragmatic hybrid method using existing historical BERTs + explicit formal feature extraction

---

## Two Parallel Tracks

### Track 1: IMMEDIATE - Phase 4 (Current Work)
**Goal:** Improve 116K poem classifications using existing tools
**Timeline:** 2-3 weeks
**Approach:** Formal features + Historical BERT content

```
STEP 1: Formal Feature Extraction (Versification)
│   Tools: CMU Pronouncing Dictionary, pronouncing library
│   Extract:
│   ├── Meter & stress patterns (iambic, trochaic, etc.)
│   ├── Rhyme schemes (ABAB, AABB, phonetic matching)
│   ├── Stanza structure (quatrains, couplets, etc.)
│   └── Line lengths, syllable counts
│
│   Status: ⏸️ Tools installed, ready to extract
│
│          ↓
│
STEP 2: Historical BERT Content Features
│   Use EXISTING models (no custom training):
│   ├── EEBO-BERT (1470-1690) - jts3et/eebo-bert ✅ Have locally
│   ├── ECCO-BERT (1700-1800) - TurkuNLP/eccobert-base-cased-v1 ✅ Found
│   └── BL-Books BERT (18th-19th c.) - bigscience-historical-texts/bert-base-blbooks-cased ✅ Found
│
│   Extract 768-dim embeddings per poem using period-appropriate BERT
│   Status: ⏸️ Need to download models
│
│          ↓
│
STEP 3: Combined Classification
│   Input: Formal features (50-100 dim) + BERT embeddings (768 dim)
│   Model: Multi-task classifier with 28 output heads
│   Training: On Phase 3B heuristic labels (116K poems)
│
│   Status: ⏸️ Awaiting Steps 1-2
│
│          ↓
│
OUTPUT: Improved 28-field classifications for all 116,674 HEPC poems
```

**Why This Approach:**
- ✅ Uses specialized tools for formal features (more accurate than teaching BERT to "see" meter)
- ✅ Leverages period-appropriate historical language understanding
- ✅ Fast (2-3 weeks vs 6+ months)
- ✅ Publishable (DH papers + literary analysis)
- ✅ Can proceed immediately with available resources

---

### Track 2: LONG-TERM - Custom Poetry-Specific Models (Future)
**Goal:** Novel NLP architecture for poetry understanding
**Timeline:** 6-9 months
**Status:** Deferred until after Phase 4 + initial papers

```
LAYER 1: Custom Historical BERTs (Optional - may use existing)
LAYER 2: Hierarchical Poetry-BERT (Line→Stanza→Poem training)
LAYER 3: Prosodic Conditioning (Deep integration of formal features)
LAYER 4: Classification Fine-tuning

Status: ⏸️ Deferred - implementation code exists in archive/
Documentation: docs/MODEL_ARCHITECTURE.md, archive/old_docs/
```

**Why Deferred:**
- Requires 6-9 months of training time
- Needs large poetry corpus collection
- More valuable after publishing initial results from Track 1
- Can be pursued for NLP-focused publications later

---

## Current Phase: Phase 4 Implementation

**What's Complete:**
- ✅ Phase 3B: 116,674 poems classified with heuristic-based labels
- ✅ Prosodic tools installed (pronouncing, CMU dict)
- ✅ Historical BERTs identified on HuggingFace
- ✅ Phase 4 plan documented

**Next Steps:**
1. Test prosodic tools on sample poems
2. Download historical BERTs to M4 Max
3. Extract formal features for all poems
4. Extract BERT embeddings
5. Train classifier and generate improved classifications

---

## HEPC CORPUS: 116,674 Historical English Poetry (1100-1928)

**Location (M4 Max):** `Data/corpus/texts/` (551MB)
**Metadata:** `Data/corpus/metadata.csv` (41MB)
**Periods:** Medieval, Tudor, Elizabethan, Romantic, Victorian, Modernist

**Current Classifications (Phase 3B):**
- File: `data/classified_poems_complete.csv` (34 MB)
- HuggingFace: https://huggingface.co/datasets/jts3et/hepc-classified-poems
- Method: Pattern-matching heuristics (archaic pronouns, line counts, etc.)
- Quality: Reasonable for trends, needs improvement for precision

**Phase 4 Goal:** Improve classification accuracy using formal feature extraction + historical BERTs

---

## What's Complete (Phase 3B)

### ✅ HEPC Corpus + Classifications
- **116,674 poems** (Medieval-20th century, 1100-1928)
- **551MB text files** organized by author (M4 Max: `Data/corpus/texts/`)
- **28-dimension classifications** (heuristic-based, Phase 3B)
- **34MB CSV** with all classifications
- **HuggingFace dataset**: https://huggingface.co/datasets/jts3et/hepc-classified-poems

### ✅ Historical BERT Models (Ready to Use)
- **EEBO-BERT** (1470-1690): jts3et/eebo-bert - ✅ Have locally (418MB)
- **ECCO-BERT** (1700-1800): TurkuNLP/eccobert-base-cased-v1 - ✅ Identified
- **BL-Books BERT** (18th-19th c.): bigscience-historical-texts/bert-base-blbooks-cased - ✅ Identified

### ✅ Prosodic Analysis Tools (Phase 4)
- **pronouncing** library installed (CMU Pronouncing Dictionary)
- **NLTK** installed
- Ready for formal feature extraction

### ✅ Custom Training Code (Track 2 - Deferred)
- Hierarchical dataset class (`training/hierarchical_dataset.py`)
- Multi-objective loss functions (`training/hierarchical_losses.py`)
- Custom trainer with InfoNCE (`training/hierarchical_trainer.py`)
- Colab training notebook (`notebooks/hierarchical_bert_training_colab.ipynb`)
- Documentation: `docs/MODEL_ARCHITECTURE.md`
- Status: ⏸️ Archived for future use

---

## Phase 4 vs Track 2: Why This Approach

**Phase 4 (Current):** Use existing tools, get results fast
- ✅ No training required (use existing BERTs)
- ✅ Specialized formal feature tools (more accurate)
- ✅ 2-3 weeks to completion
- ✅ Publishable results (DH + literary papers)

**Track 2 (Future):** Custom poetry-specific models
- ❌ Requires 6-9 months
- ❌ Need HathiTrust corpus access
- ❌ Need to collect 17M poetry lines
- ✅ Novel NLP contribution
- ✅ Additional publications in NLP venues

**Decision:** Do Phase 4 first, then decide if Track 2 is worth the investment based on initial publication success

---

## Working With This Project (Instructions for Claude)

### When User Asks to "Document Progress" or "Update Documentation"

**ALWAYS UPDATE existing documentation, DO NOT create new files.**

Files to update:
- `claude_context/START_HERE.md` - Overall project status
- `claude_context/PHASE3B_STATUS.md` - Phase 3B specific status
- `claude_context/PHASE3B_TRAINING_LOG.md` - Training progress and details
- `README.md` - User-facing project overview

**Exception**: Only create NEW documentation when:
1. Starting a completely new phase/track
2. User explicitly asks for a new document
3. Creating initial documentation for a new component

### When I Get Confused

Point me to this file and tell me:

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
- Username: jts3et (NOT justinstec)
- Status: ✅ Logged in with Claude-specific token
- Token: ~/.cache/claude_hf/token (38 bytes, last verified Nov 12, 2025 7:21 PM)
- Models: 1 uploaded
  - ✅ EEBO-BERT: https://huggingface.co/jts3et/eebo-bert (418MB)
- Datasets: 1 uploaded
  - ✅ HEPC Classifications: https://huggingface.co/datasets/jts3et/hepc-classified-poems (36MB, uploaded Nov 12, 2025)

### Google Drive
- **Desktop Client**: `/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive`
  - Phase 3B Backup: `AI_Project_Phase3B_Backup/` (created Nov 12, 2025)
  - Contains: `classified_poems_complete.csv`, `PHASE3B_COMPLETION_SUMMARY.md`, `merge_classifications.py`
- **API Access** (alternative when Desktop has sync issues):
  - Service account: poetry-bert-service@poetry-bert-training.iam.gserviceaccount.com
  - Credentials: `.credentials/poetry-bert-service-account.json` (2.3KB, Nov 4, 2025)
  - Scopes: drive.readonly
  - Use for: Downloading models programmatically
- Example:
  ```python
  from google.oauth2 import service_account
  from googleapiclient.discovery import build

  credentials = service_account.Credentials.from_service_account_file(
      '.credentials/poetry-bert-service-account.json',
      scopes=['https://www.googleapis.com/auth/drive.readonly'])
  service = build('drive', 'v3', credentials=credentials)
  ```

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

### TWO-TRACK APPROACH (See claude_context/PRAGMATIC_WORKFLOW.md)

**Track 1: Get Metadata NOW (Priority)**
1. ✅ System reorganization - COMPLETE
2. ✅ 397 training poems prepared - COMPLETE
3. ✅ HuggingFace login - COMPLETE
4. ✅ Format instruction-tuning dataset - COMPLETE (357 train, 40 val)
5. ✅ Fine-tune Mistral-7B - COMPLETE but FAILED (model didn't learn)
   - Only generated "structure" repeatedly - insufficient training
6. ✅ **Phase 3B: Direct Claude Code Classification** - COMPLETE (Nov 12, 2025)
   - Method: Pattern-based heuristics instead of LLM fine-tuning
   - Classified all 116,674 HEPC poems across 28 dimensions
   - Parallel processing: 5 sessions, ~200-400 poems/min
   - Output: `data/classified_poems_complete.csv` (34 MB)
   - Uploaded to: https://huggingface.co/datasets/jts3et/hepc-classified-poems
   - Backed up to: Google Drive, GitHub, M4 Max
   - Documentation: `scripts/phase3/PHASE3B_COMPLETION_SUMMARY.md`
   - Note: Interim solution using heuristics, not model-based classification

**Track 2: Build Full Model (Long-term)**
1. Pursue HathiTrust access (18th-20th century corpora)
2. Collect 17.7M poetry lines
3. Train complete Layers 1+2+3
4. Use richly-annotated corpus for deep analysis

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

### Primary: Database for History of English Versification
**"Create a database of English poems (1100-1928) that will allow computational formalism at scale with the idea of allowing scholars to write the history of English versification"**

This is NOT primarily about semantic analysis. The focus is:
- **Computational formalism at scale**: Analyzing formal features (meter, rhyme, stanza structure)
- **Versification history**: How poetic form evolved across 800+ years
- **Rich metadata**: 28 dimensions capturing formal, rhetorical, and historical features
- **Scholarly resource**: Enable researchers to conduct diachronic studies of English poetry

### Publications:
1. **DH Paper**: Historical BERT ensemble methodology + HEPC database
2. **Literary History**: Versification patterns across periods
3. **CS/Comp Ling**: Framework for historical poetry NLP

### Output:
- HEPC corpus with 28-dimension metadata (Medieval-20th century, 116K poems)
- Historical BERT ensemble for period-appropriate analysis
- Improved classification models for formal features
- Tools for computational formalism research

---

**Last Updated**: November 15, 2025, 10:30 AM EST
**Current Status**: Phase 4 STARTED - Improving Classifications with Formal Features + Historical BERTs
**Current Approach**: Pragmatic hybrid (existing BERTs + explicit formal feature extraction)

**Phase 3B Complete:**
  - ✅ 116,674 HEPC poems classified (heuristic-based)
  - ✅ CSV: `data/classified_poems_complete.csv` (34 MB)
  - ✅ HuggingFace: https://huggingface.co/datasets/jts3et/hepc-classified-poems
  - ✅ System cleaned and synced (Git commit 06e7966)

**Phase 4 Progress:**
  - ✅ Prosodic tools installed (pronouncing, NLTK, CMU dict)
  - ✅ Historical BERTs identified (EEBO, ECCO, BL-Books)
  - ✅ Documentation updated (two-track approach clarified)
  - ⏸️ Ready to test prosodic extraction on sample poems
  - ⏸️ Ready to download historical BERTs to M4 Max

**Next Actions:**
  1. Test prosodic feature extraction on sample poems
  2. Download ECCO-BERT and BL-Books BERT to M4 Max
  3. Extract formal features for all 116K poems
  4. Extract BERT embeddings for all poems
  5. Train multi-task classifier
  6. Generate improved classifications
