# Phase 3 Progress Summary

**Date**: November 11, 2025
**Status**: Training data preparation COMPLETE ✓

---

## Objective

Create a comprehensive training dataset for fine-tuning an LLM to classify 116,674 corpus poems across 28 metadata dimensions including historical period, literary movement, rhetorical features, and formal characteristics.

---

## Accomplishments

### 1. Schema Development ✓

**Expanded from 19 to 28 classification columns:**

**Historical (2 columns):**
- `period` - 15 periods from Anglo-Saxon to Contemporary
- `literary_movement` - 13+ movements (Renaissance, Romanticism, Modernism, etc.)

**Rhetorical (16 columns):**
- `register` - Emotional tone/stance
- `rhetorical_genre` - Epideictic/Deliberative/Forensic/Mixed
- `discursive_structure` - Monologic/Dialogic/Polyvocal
- `discourse_type` - Description/Direct discourse/Commentary/Narrative report
- **`narrative_level`** - Extradiegetic/Intradiegetic (NEW - added to distinguish narrative layers)
- `diegetic_mimetic` - Diegetic/Mimetic/Mixed
- `focalization` - Zero/Internal/External/Multiple
- `person` - 1st/2nd/3rd/Mixed
- `deictic_orientation` - Spatial/personal deixis
- `addressee_type` - Who is addressed
- `deictic_object` - Subject/addressee description
- `temporal_orientation` - Present/Past/Future/Atemporal
- `temporal_structure` - Static/Linear/Recursive/Fragmentary
- `tradition` - Original/Translation/Imitation/Adaptation

**Form (5 columns):**
- `mode` - Lyric/Narrative/Dramatic/Mixed
- `genre` - Specific genre (Ode, Elegy, Sonnet, Epic, etc.)
- `stanza_structure` - Form description
- `meter` - Metrical pattern
- `rhyme` - Rhyme scheme

**Metadata (5 columns):**
- `title`, `author`, `year_approx`, `source_url`, `length_lines`, `length_words`

---

### 2. Gold-Standard Dataset ✓

**Source**: Existing expert classifications
- **Files**: 4 CSV tables (Historical, Rhetoric, Form, Metadata)
- **Poems**: 53 canonical works (Shakespeare to contemporary)
- **Quality**: Expert-curated classifications
- **Updated**: Added `narrative_level` column for narrative theory distinction

---

### 3. Canonical Poem Selection ✓

**Curated list of 404 poems** spanning English literary history:
- **Anglo-Saxon**: 15 poems (Beowulf, The Wanderer, etc.)
- **Middle English**: 25 poems (Chaucer, Pearl Poet, etc.)
- **Renaissance**: 66 poems (Tudor, Elizabethan, Jacobean)
- **17th Century**: 59 poems (Caroline, Interregnum, Restoration)
- **18th Century**: 28 poems (Augustan, Neoclassical)
- **Romantic**: 47 poems (Blake, Wordsworth, Keats, Shelley, Byron)
- **Victorian**: 56 poems (Tennyson, Browning, Hopkins, Dickinson, Whitman)
- **Modernist**: 52 poems (Eliot, Yeats, Pound, Stevens, Hughes)
- **Postwar**: 32 poems (Lowell, Bishop, Plath, Ginsberg, Brooks)
- **Contemporary**: 24 poems (Rich, Oliver, Dove, Angelou)

**Selection criteria**:
- Canonical status in English literature
- Representative of period/movement
- Diverse authors, styles, and forms
- No foreign language works (Anglo-Saxon/Middle English count as English)

---

### 4. Automated Classification ✓

**Method**: Few-shot LLM classification using Mistral-7B-Instruct

**Infrastructure**:
- **Platform**: Google Colab (GPU runtime)
- **Model**: Mistral-7B-Instruct-v0.2 (ungated, instruction-tuned)
- **Approach**: 5 gold-standard examples as few-shot prompts
- **Runtime**: ~60 minutes for 404 poems (~9.5 sec/poem)
- **Checkpointing**: Saved to Google Drive every 50 poems
- **Location**: Ran on M4 Max at office, monitored remotely

**Results**:
- **404/404 poems classified**
- All 28 fields populated
- Only 3 missing periods, 6 missing modes initially

---

### 5. Data Cleaning & Quality Control ✓

**Issues Found & Fixed**:

1. **Period taxonomy** (134 fixes)
   - LLM invented: "Medieval", "Early Modern", "Eighteenth Century"
   - Fixed by mapping to proper periods based on year ranges

2. **Mode taxonomy** (158 fixes)
   - LLM invented: "Descriptive", "Satirical", "Drama", "Experimental"
   - Mapped to canonical: Lyric, Narrative, Dramatic, Mixed

3. **Rhetorical genre** (168 fixes)
   - LLM invented: "Descriptive", "Narrative", "Epistolary", "Invective"
   - Mapped to classical rhetoric: Epideictic, Deliberative, Forensic, Mixed

4. **Missing values** (6 fixes)
   - Filled 6 missing modes based on poem knowledge

5. **Capitalization** (1 fix)
   - Standardized field value capitalization

**Total changes**: 467 corrections

**Final quality**:
- 0 missing periods ✓
- 0 missing modes ✓
- 11 missing rhetorical_genre (2.6% - acceptable for edge cases)
- Clean taxonomy matching gold-standard schema ✓

---

### 6. Training Dataset Assembly ✓

**Merged Components**:
- 53 gold-standard poems (expert-curated)
- 404 Colab-classified poems (LLM + manual cleanup)
- **Total: 457 poems**

**Coverage**:
- **Periods**: All 15 periods represented
- **Modes**: Lyric (74%), Narrative (23%), Dramatic (2%), Mixed (<1%)
- **Rhetorical genres**: Epideictic (84%), Deliberative (11%), Forensic (3%), Mixed (1%)

**File**: `data/phase3/training_set_456_poems.csv`

---

## Technical Setup

### M4 Max Configuration

**Purpose**: Remote compute workstation for ML tasks

**Setup**:
- **Connection**: SSH via Tailscale VPN (100.65.21.63)
- **Storage**: 116,674 corpus poems (10GB) on M4 Max only
- **Environment**: Python 3.11, MLX, PyTorch, Transformers
- **Power management**: Sleep disabled for overnight tasks
- **Remote monitoring**: SSH + rclone for Google Drive

**Workflow**:
1. Develop on MacBook Air (lightweight, portable)
2. Transfer code/data to M4 Max via rsync
3. Run compute-intensive tasks on M4 Max
4. Monitor progress remotely from home
5. Retrieve results back to Air

### Colab Integration

**Benefits**:
- Free GPU access (T4/V100)
- Google Drive persistence for checkpoints
- No local compute resources used
- Can monitor from any device

**Configuration**:
- Checkpoints every 50 poems
- Google Drive auto-save
- Browser keep-alive script
- Auto-download results

---

## Key Decisions

### 1. Narrative Level Addition

**Issue**: `diegetic_mimetic` column conflated narrative mode (telling vs. showing) with narrative level (inside vs. outside story).

**Solution**: Added `narrative_level` column
- **Extradiegetic**: Narrator outside story world (Chaucer, Pope)
- **Intradiegetic**: Narrator inside story world (The Wanderer)
- **(Blank)**: Pure mimetic discourse (direct lyrics, apostrophes)

**Rationale**: Crucial distinction in narrative theory for studying narrative poetry.

### 2. Taxonomy Approach

**Chose**: Expanded fixed taxonomy (Option B)
- Strict fixed values for core fields (rhetorical_genre, person, mode)
- Semi-controlled vocabulary for descriptive fields (register, genre)
- Track new categories as they emerge

**Rationale**: Balances ML training requirements (consistent categories) with scholarly flexibility (domain-specific nuance).

### 3. Classification Method

**Chose**: Few-shot LLM with manual cleanup (Option A + Colab)
- LLM provides fast initial classification
- Manual review catches systematic errors
- Hybrid approach balances speed and accuracy

**Rejected**: Fully manual (too slow), Paid API (ongoing cost), Pure LLM (less accurate)

---

## Challenges & Solutions

### Challenge 1: Llama-3 Access

**Problem**: Llama-3-8B is gated, requires Meta approval

**Solution**: Switched to Mistral-7B-Instruct (ungated, equivalent performance)

**Outcome**: No delays, classification proceeded smoothly

### Challenge 2: LLM Inventing Categories

**Problem**: LLM created non-canonical values (e.g., "Early Modern" for period)

**Solution**: Post-processing scripts with year-based mapping

**Outcome**: 467 corrections, clean taxonomy

### Challenge 3: Remote Monitoring

**Problem**: Need to check progress without SSH access to Colab runtime

**Solution**:
1. Checkpoints to Google Drive (accessible from anywhere)
2. rclone CLI for terminal-based Drive access
3. SSH to M4 Max for local file checks

**Outcome**: Successfully monitored from home, retrieved results next day

### Challenge 4: Checkpoint Persistence

**Problem**: Initial Colab notebook saved checkpoints to `/content/` (temporary)

**Solution**: Modified to save to both `/content/` and Google Drive

**Outcome**: Checkpoints survived potential runtime disconnects

---

## Scripts Created

1. **`generate_comprehensive_list.py`** - Generated 404 canonical poem list
2. **`merge_gold_standard.py`** - Merged 4 gold-standard CSVs
3. **`add_narrative_level.py`** - Added narrative_level to gold poems
4. **`colab_classifier.ipynb`** - Colab notebook for LLM classification
5. **`clean_classifications.py`** - Fixed period/mode taxonomy
6. **`fix_remaining_issues.py`** - Fixed rhetorical_genre, filled missing modes
7. **`merge_training_set.py`** - Combined 53 + 404 into final dataset

---

## Files Created

**Data files** (`data/phase3/`):
- `canonical_poems_to_classify.csv` - 226 poems (initial list)
- `448_poems_to_classify.csv` - 404 poems (expanded list)
- `gold_standard_52_poems.csv` - 53 expert-classified poems
- `gold_standard_52_poems_with_narrative_level.csv` - Updated with new column
- `404_poems_classified.csv` - Raw Colab output
- `404_poems_classified_cleaned.csv` - After period/mode fixes
- `404_poems_classified_final.csv` - After all fixes
- `poems_to_review.csv` - 6 flagged poems (now resolved)
- **`training_set_456_poems.csv`** - **FINAL: 457 poems, 29 columns** ✓

**Documentation** (`docs/`):
- `PHASE_3_PLAN.md` - Initial implementation plan
- `PHASE_3_PROGRESS.md` - This summary

**Code** (`scripts/phase3/`):
- 7 Python scripts + 1 Jupyter notebook

---

## Statistics

### Processing Time

- Gold standard prep: ~30 minutes
- Canonical poem list: ~30 minutes
- Colab classification: ~60 minutes (automated)
- Data cleaning: ~45 minutes (3 scripts)
- Total: **~3 hours** (mostly automated)

### Classification Quality

**Before cleanup**:
- 404 poems classified
- 3 missing periods (0.7%)
- 6 missing modes (1.5%)
- Taxonomy issues in 467 entries (29%)

**After cleanup**:
- 457 poems total
- 0 missing periods ✓
- 0 missing modes ✓
- 11 missing rhetorical_genre (2.6%)
- All taxonomy values match schema ✓

### Data Distribution

**By Period**:
1. Modernist: 84 poems (18%)
2. Romantic: 63 poems (14%)
3. Victorian: 49 poems (11%)
4. Caroline: 48 poems (11%)
5. Elizabethan: 43 poems (9%)
6. Contemporary: 32 poems (7%)
7. Others: 138 poems (30%)

**By Mode**:
- Lyric: 339 poems (74%)
- Narrative: 106 poems (23%)
- Dramatic: 11 poems (2%)
- Mixed: 1 poem (<1%)

**By Rhetorical Genre**:
- Epideictic: 376 poems (84%)
- Deliberative: 50 poems (11%)
- Forensic: 13 poems (3%)
- Mixed: 6 poems (1%)

---

## Next Steps

### Phase 3B: Fine-Tuning (On Deck)

1. **Fetch full poem texts** for all 457 training poems
   - Poetry Foundation API
   - Gutenberg Project
   - Manual collection for difficult cases

2. **Format instruction-tuning dataset**
   - Prompt: "Classify this poem..."
   - Input: Full poem text
   - Output: All 28 classification fields

3. **Fine-tune LLM on M4 Max**
   - Model: Llama-3-8B or Mistral-7B
   - Method: LoRA (Low-Rank Adaptation)
   - Framework: MLX (Apple Silicon optimized)
   - Time: 1-2 hours on M4 Max

4. **Validate model**
   - Test on held-out poems
   - Check accuracy per field
   - Manual review of sample outputs

5. **Run inference on full corpus**
   - Apply to 116,674 poems
   - Batch process (32 poems at a time)
   - Time: 6-12 hours on M4 Max

6. **Update corpus metadata**
   - Add 28 new columns to `corpus_final_metadata.csv`
   - Merge by poem_id
   - Create backup before merge

---

## Repository Status

**Phase 1**: ✓ Complete (Corpus assembly - 116,674 poems)
**Phase 2**: ✓ Complete (Basic metadata - 19 fields)
**Phase 3A**: ✓ Complete (Training data - 457 poems, 28 fields)
**Phase 3B**: Next (Fine-tuning & inference)
**Phase 4**: Future (Prosodic/thematic features)

---

## Lessons Learned

1. **Few-shot LLM + manual cleanup works well**
   - Fast initial classification
   - Systematic errors easy to catch
   - Total 3 hours including cleanup

2. **Remote compute workflow is effective**
   - Develop on Air, execute on M4 Max
   - Colab bridges gap for GPU tasks
   - Tailscale VPN essential for eduroam

3. **Checkpointing is critical**
   - Google Drive persistence saved progress
   - Every 50 poems = manageable restart point

4. **Taxonomy standardization requires domain knowledge**
   - LLMs invent plausible-sounding categories
   - Year-based heuristics work well for periods
   - Classical rhetoric maps well to modern categories

5. **Narrative theory matters**
   - Adding `narrative_level` improves analytical precision
   - Genette's framework still relevant for poetry

---

## Acknowledgments

- **Existing classifications**: Built on previous manual expert work (52 poems)
- **LLM**: Mistral-7B-Instruct (HuggingFace)
- **Infrastructure**: Google Colab (GPU), Tailscale (VPN)
- **Compute**: M4 Max (home), MacBook Air (office)

---

**End of Phase 3A Summary**

*Next: Fetch poem texts & fine-tune LLM for corpus-wide classification*
