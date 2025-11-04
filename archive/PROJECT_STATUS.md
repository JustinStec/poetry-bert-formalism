# Project Status - October 30, 2025

## Current Project: Computational Historical Formalism

**Three-Layer BERT for Diachronic Poetry Analysis**

**Researcher:** Postdoc, IU Center for Possible Minds
**Timeline:** 18-month research program (Oct 2024 - March 2026)
**Current Focus:** CMU job application due November 1, 2025
**Core Goal:** Merge historical language models + poetry-specialized BERT + prosody conditioning to track formal features across 500 years of English poetry

---

## Research Question

**How can we computationally track the historicity of formal features across literary periods?**

Scaling up close reading methodology (like the citational parataxis article) to analyze:
- Metrical variants across periods (e.g., trochaic substitutions in iambic pentameter)
- Syntactic structures (parataxis, hypotaxis, caesura)
- Line-level features (enjambment, end-stopping)
- Phonological patterns (alliteration, assonance, rhyme)

**Key dimensions:**
- Cross-period (Renaissance → Romantic → Victorian)
- Cross-author (contemporaries)
- Within-author career development (early → middle → late works)
- Cross-genre (sonnet vs. dramatic monologue vs. epic)

---

## Current Status (October 30, 2025)

> **See `docs/ARCHITECTURE_OVERVIEW.md` for complete technical overview**

### ✅ Layer 1: Historical Language Models

#### EEBO-BERT (1595-1700) - COMPLETE ✓
- **Corpus:** 7.6GB Early English Books Online
- **Model:** `eebo_bert_finetuned/` (Google Drive)
- **Status:** Training complete, ready for use

#### ECCO, NCCO, Modern - ACQUISITION IN PROGRESS
- **ECCO (1700-1800):** HathiTrust workset creation in progress
- **NCCO (1800-1900):** HathiTrust workset creation in progress
- **Modern (1900-2000):** HathiTrust workset creation in progress
- **Scripts:** `scripts/download_hathitrust_corpus.py`, `scripts/preprocess_hathitrust_downloads.py` ✓ Created
- **Strategy:** General English corpora (all genres, not just poetry)

---

### 🔄 Layer 2: Poetry BERT (~50% Trained)

#### Unified Poetry Corpus (6.2M lines)

| Source | Works | Lines | Status |
|--------|-------|-------|--------|
| **Gutenberg** | 1,191 | 5.5M | ✓ Reconstructed |
| **Shakespeare** | 40 | 181K | ✓ Ready |
| **Core 27 Poets** | 51 | 470K | ✓ Ready |
| **PoetryDB** | 3,162 | ~50K | ✓ Ready |

**Database:**
- **Location:** `Data/poetry_unified.db` (SQLite)
- **Status:** Partially imported
  - ✓ Gutenberg: 1,191 works, 10.9M lines in DB
  - ⏳ Shakespeare/Core Poets/PoetryDB: Import pending fix

**BERT Training:**
- **Status:** ~50% complete (checkpoint-395000)
- **Location:** `gutenberg_bert_checkpoints/` (Google Drive)
- **Training notebook:** `train_gutenberg_bert.ipynb` (Google Colab)
- **Timeline:** Completes in ~24 hours (Oct 31 evening)
- **Note:** Currently trained on Gutenberg only; will need to retrain on complete unified corpus after database fix

---

### ⏳ Layer 3: Prosody Conditioning

**Status:** Architecture designed, awaiting Layer 1+2 merge

**Prosodic Features:**
- Stress embeddings (stressed/unstressed syllables)
- Meter position embeddings (foot position within line)
- Line position embeddings (position within stanza/poem)
- Phonological features (rhyme, alliteration, assonance)

**Technical Spec:** See `docs/PROSODY_BERT_ARCHITECTURE.md`

**Blockers:**
- Need to complete Layer 1 historical corpus acquisition
- Need to determine model merging strategy (sequential, averaging, task arithmetic, or adapters)

---

### 📋 Applications Framework

#### Semantic Trajectory Analysis
**Status:** Methodology complete, ready for implementation

**Documentation:**
- `Methodology/methods_log.md` - Research methodology
- `Methodology/technical_notes.md` - Implementation notes
- `Methodology/metrics_definitions.md` - 7 metrics (SPL, NSD, Tortuosity, RTO, ER, VPV, DC)

**Corpus:** 53 canonical poems curated across periods

**Research Question:** Do real poems create distinctive semantic trajectories that LLM-generated poems cannot replicate?

**Integration:** Trajectory analysis is Phase 3 application of prosody-conditioned BERT

---

## In Progress (Next 48 Hours)

### 🔄 BERT Training Completion
- **Corpus:** Gutenberg 5.5M lines
- **Current:** ~50% (checkpoint-395000)
- **Timeline:** Completes Oct 31 evening
- **Next:** Extract embeddings for Shakespeare analysis

### 🔄 CMU Job Application
- **Deadline:** November 1, 2025 (2 days away)
- **Tomorrow (Oct 31):** Extract embeddings, analyze Shakespeare Sonnet 18
- **Thursday (Nov 1):** Draft writing sample with BERT results
- **Friday (Nov 1):** Final edits and submit application

---

## Architecture: Three-Layer Framework

> **Complete technical documentation:** `docs/ARCHITECTURE_OVERVIEW.md`

### Quick Overview

```
LAYER 1: Historical Language Models
↓
Learn period-specific English (1595-2000)
- EEBO (1595-1700) ✓ trained
- ECCO (1700-1800) ⏳ acquiring via HathiTrust
- NCCO (1800-1900) ⏳ acquiring via HathiTrust
- Modern (1900-2000) ⏳ acquiring via HathiTrust
Train on: ALL genres (novels, essays, science, legal, religious, etc.)

        ↓ MERGE (strategy TBD)

LAYER 2: Poetry Model
↓
Learn poetic conventions
- Unified 6.2M line corpus
- Shakespeare + Core Poets + Gutenberg + PoetryDB
- Train on: Poetry only
Status: ~50% trained

        ↓ ADD PROSODIC LAYERS

LAYER 3: Prosody Conditioning
↓
Add formal feature awareness
- Stress embeddings
- Meter position embeddings
- Line position embeddings
- Phonological features
Status: Architecture designed, pending merge

        ↓ APPLICATIONS

- Semantic trajectory analysis (53 canonical poems)
- Career arc tracking (Shakespeare, Romantic poets)
- Diachronic formal feature evolution (enjambment, meter, syntax)
```

### Key Design Principle

**Separate training pathways** for:
1. Historical semantics (how English changed)
2. Poetic conventions (what makes poetry distinctive)
3. Prosodic structure (formal features)

Enables **precise control** over each knowledge type during model merging.

### Open Research Question: Model Merging Strategy

Four approaches under consideration:
1. **Sequential fine-tuning** - Simple, may overwrite historical knowledge
2. **Model averaging** - Preserves both, may dilute both
3. **Task arithmetic** - Precise control, requires tuning
4. **Adapter layers** - Maintains historical perfectly, adds complexity

Testing all four post-Layer 2 completion.

---

## Embedding Alignment Strategy

### Challenge
Need to compare across periods with different embedding spaces:
- EEBO: Word2Vec (static)
- Gutenberg: BERT (contextual)

### Solution: Dual-Mode Analysis

**Aligned embeddings** (for cross-period comparison):
- Extract static embeddings from BERT token layers
- Align using Orthogonal Procrustes transformation
- Compare "love" in 1595 vs. 1850 in unified space

**Unaligned embeddings** (for period-appropriate context):
- Use period-specific BERT for contextual understanding
- Analyze enjambment in Renaissance vs. Romantic with period-appropriate semantics

**Implementation:**
- `scripts/extract_bert_static_embeddings.py` - Extract from BERT
- `scripts/align_historical_embeddings.py` - Procrustes alignment
- `scripts/tortuosity_analysis_ui.py` - Switch between embedding spaces

---

## Data Organization

### Corpus Files
```
Data/
├── poetry_corpus/
│   ├── shakespeare_complete_works.jsonl          (40 works, 181K lines)
│   ├── shakespeare_early_period.jsonl            (12 works, 1591-1595)
│   ├── shakespeare_middle_period.jsonl           (13 works, 1595-1601)
│   ├── shakespeare_late_period.jsonl             (10 works, 1602-1609)
│   ├── shakespeare_final_period.jsonl            (5 works, 1609-1613)
│   ├── core_poets_complete.jsonl                 (51 works, 470K lines)
│   ├── core_poets_early_modern.jsonl             (9 works, 1590-1681)
│   ├── core_poets_romantic.jsonl                 (15 works, 1793-1850)
│   ├── core_poets_victorian.jsonl                (12 works, 1842-1918)
│   └── poetrydb.jsonl                            (3,162 poems)
├── gutenberg_poetry_corpus.jsonl                 (5.5M lines)
└── corpus_index.txt                               (Master index)
```

### Historical Embeddings
```
~/Library/CloudStorage/GoogleDrive-.../
├── EEBO_1595-1700/
│   ├── eebo_cleaned_corpus.txt                   (7.6GB)
│   └── eebo_word2vec.model                       (Trained ✓)
└── gutenberg_poetry_corpus_clean.jsonl           (5.5M lines, training BERT)
```

### Documentation
```
docs/
├── PROSODY_BERT_ARCHITECTURE.md                  (Technical spec)
├── hathitrust_step_by_step.md                    (HathiTrust access)
├── htrc_access_quickstart.md                     (HTRC quick reference)
├── htrc_data_capsule_guide.md                    (Data Capsule usage)
└── email_to_IU_library.md                        (ECCO access request)
```

### Project Documentation
```
/
├── PROJECT_STATUS.md                             (This file)
├── CURRENT_ARCHIVE_STATUS.md                     (Corpus inventory)
├── ARCHIVE_BUILDING_STRATEGY.md                  (Expansion strategy)
├── CMU_Research_Statement_Draft.md               (Job application)
└── README.md                                     (Project overview)
```

---

## Immediate Workflow (Next 48 Hours - CMU Deadline)

### Tomorrow (Oct 31) - Extract & Analyze
1. ✓ Gutenberg corpus reconstructed
2. 🔄 BERT training completes (evening)
3. ⏳ Extract static embeddings from Gutenberg BERT
4. ⏳ Align with EEBO BERT and Google News embeddings
5. ⏳ Run Shakespeare Sonnet 18 analysis for pilot study:
   - Semantic trajectory analysis
   - Compare to LLM-generated sonnet
   - Extract prosodic features for contextualization

### Thursday (Nov 1) - Draft & Submit
1. ⏳ Write up Sonnet 18 analysis results
2. ⏳ Connect to broader research framework (three-layer architecture)
3. ⏳ Explain computational historical formalism approach
4. ⏳ Include visualizations (trajectory plots)
5. ⏳ Final edits on research statement
6. ⏳ Submit complete CMU application

---

## Post-CMU Roadmap

### November-December 2025

**Fix & Expand Unified Database:**
1. Debug Shakespeare/Core Poets/PoetryDB import
2. Complete `poetry_unified.db` with all 6.2M lines
3. Retrain poetry BERT on complete unified corpus
4. Export CSV for analysis and quality checking

**Acquire Historical Corpora (Layer 1):**
1. Create HathiTrust worksets for ECCO (1700-1800)
2. Create HathiTrust worksets for NCCO (1800-1900)
3. Create HathiTrust worksets for Modern (1900-2000)
4. Download and preprocess (OCR quality 90%+ threshold)
5. Build period-specific training corpora

**Train Period-Specific BERTs:**
- ECCO-BERT (1700-1800)
- NCCO-BERT (1800-1900)
- Modern-BERT (1900-2000)

### January-March 2026

**Model Merging Experiments:**
1. Test sequential fine-tuning approach
2. Test model averaging approach
3. Test task arithmetic approach
4. Test adapter layers approach
5. Select optimal merging strategy based on evaluation

**Implement Prosody Conditioning (Layer 3):**
1. Annotate subset of unified corpus with prosodic features
2. Add prosodic embedding layers to merged model
3. Continue MLM training with prosodic features
4. Validate prosody-awareness with test cases

**Build Formal Annotation Pipeline:**
- Automated scansion (prosodic library)
- Syntactic parsing (spaCy/CoreNLP)
- Line-level feature detection (enjambment, caesura)
- Phonological analysis (rhyme, alliteration)

### April-June 2026

**Run Semantic Trajectory Analysis:**
- Analyze 53-poem canonical corpus
- Compare real vs. LLM-generated poems
- Test hypothesis: Real poems create distinctive trajectories
- Write empirical paper on findings

**Career Arc Analysis:**
- Shakespeare early/middle/late/final periods
- Track formal features across Romantic poets
- Correlate prosodic patterns with career development

**Scale Formal Feature Tracking:**
- Index full 6.2M line corpus by formal features
- Enable searchable database queries
- Visualization interface for feature distributions
- Diachronic studies (enjambment, meter, syntax evolution 1595-2025)

**Publications:**
1. Methodology paper: "Three-Layer BERT for Diachronic Poetry Analysis"
2. Empirical paper: "Semantic Trajectories in Real vs. LLM-Generated Poetry"
3. Historical paper: "Formal Feature Evolution in English Poetry, 1595-2025"

**Grant Applications:**
- NEH Digital Humanities Advancement Grant
- NSF-NEH "Digging Into Data"
- ACLS Digital Extension Grant
- Mellon Foundation Digital Humanities Grant

---

## Technical Stack

### Core Tools
- **Python 3.x** - Primary language
- **Prosodic** - Scansion and prosodic analysis
- **Transformers (HuggingFace)** - BERT training and inference
- **Gensim** - Word2Vec and embedding alignment
- **scipy** - Orthogonal Procrustes alignment

### Data Sources
- **Project Gutenberg** - Public domain poetry
- **PoetryDB API** - Structured poetry collection
- **EEBO** - Early Modern English corpus (1595-1700)
- **ECCO** - 18th century texts (via IU)
- **HathiTrust** - 6.5M public domain volumes (via IU)

### Computing
- **Local:** M2 Mac for development
- **Training:** Google Colab Pro (temporary), M4 Max ordered
- **Storage:** Google Drive for large corpora

---

## Key Insights from This Week

### 1. Archive Is Sufficient for Immediate Research
- 6M lines of poetry with metadata
- Complete author career arcs (Shakespeare + 27 poets)
- Period coverage 1590-1918 (robust)
- No immediate need for massive expansion

### 2. Three-Layer Architecture Clarified
- Layer 1: Period-specific language (prose + poetry)
- Layer 2: Prosody conditioning (poetry only)
- Layer 3: Genre filtering for analysis (not separate models)

### 3. Dual Embedding Strategy Required
- Aligned for cross-period comparison
- Unaligned for period-appropriate context
- Different research questions need different spaces

### 4. Career-Arc Analysis Is Feasible
- Shakespeare: 40 works chronologically ordered
- Core poets: 51 works with author career periods
- Can track features within individual authors' development
- Example: T.S. Eliot's analysis of Shakespeare's blank verse

### 5. Metadata Schema Standardized
All poems structured with:
- Author, title, composition date
- Period (early_modern, romantic, victorian, etc.)
- Author career period (early/middle/late)
- Genre (sonnet, epic, dramatic_monologue, etc.)
- Complete text + line-by-line structure

---

## Files Reorganized (Oct 30, 2024)

**Cleaned up root directory:**
- Moved obsolete scripts to `scripts/archive/`
- Moved sample texts to `corpus_samples/`
- Moved notebooks to `notebooks/`
- Consolidated documentation in `docs/`
- Archived old HTML/web scraping to `archive/obsolete/`

**Current root structure:**
```
/
├── Data/                      (Corpus files)
├── scripts/                   (Active scripts)
├── docs/                      (Documentation)
├── paper/                     (Research papers)
├── Methodology/              (Methods documentation)
├── Metadata/                  (Corpus metadata)
├── notebooks/                 (Jupyter notebooks)
├── logs/                      (Training logs)
├── PROJECT_STATUS.md          (This file)
├── CURRENT_ARCHIVE_STATUS.md  (Corpus inventory)
├── ARCHIVE_BUILDING_STRATEGY.md
└── CMU_Research_Statement_Draft.md
```

---

## Contact & Collaboration

**Affiliation:** IU Center for Possible Minds
**Project Type:** Computational literary analysis, digital humanities
**Open to collaboration on:** Formal feature tracking, historical embeddings, prosody-conditioned models

---

**Last Updated:** October 30, 2025
**Next Update:** After CMU application submitted (Nov 1, 2025)
