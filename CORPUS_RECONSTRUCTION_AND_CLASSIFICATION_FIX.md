# HEPC Corpus Reconstruction & Classification Correction

**Date**: November 13, 2025
**Status**: Emergency reconstruction in progress
**Impact**: Blocking Track 1 Mistral-7B inference on 116K poems

---

## Table of Contents

1. [Project Context](#project-context)
2. [The Crisis: Deleted Corpus](#the-crisis-deleted-corpus)
3. [Immediate Solution: Corpus Reconstruction](#immediate-solution-corpus-reconstruction)
4. [Secondary Problem: Claude's Systematic Mislabeling](#secondary-problem-claudes-systematic-mislabeling)
5. [Long-term Solution: Theory-Aware Classification](#long-term-solution-theory-aware-classification)
6. [Current Status](#current-status)
7. [Next Steps](#next-steps)

---

## Project Context

### Overall Research Goal
**Layered BERT Architecture for Poetry Analysis** - analyzing semantic complexity in historical English poetry through trajectory tortuosity metrics.

### Three-Layer Architecture

```
Layer 1: Historical BERTs
├── EEBO-BERT (1595-1700) ✅ Complete
├── ECCO-BERT (1700-1800)
└── BLBooks-BERT (1800-1900)

Layer 2: Poetry Specialization
└── Hierarchical Multi-Objective BERT
    ├── Token Level: MLM (0.5 weight)
    ├── Line Level: Contrastive learning (0.2 weight)
    ├── Quatrain Level: Contrastive learning (0.2 weight)
    └── Sonnet Level: Contrastive learning (0.1 weight)

Layer 3: Prosodic Conditioning
└── Meter, rhyme, position features
```

### Two-Track Approach

**Track 1: Get Metadata NOW** (Urgent)
- Trained Mistral-7B classifier (49.7 min, losses 6.486/6.505)
- Model: `/Users/justin/poetry-bert-formalism/models/poetry-classifier-mistral7b/`
- Dataset: 357 train / 40 validation poems
- **Goal**: Run inference on 116,674 HEPC corpus poems
- **Status**: ⚠️ BLOCKED - corpus deleted November 12

**Track 2: Build Full Layered Model** (Long-term)
- EEBO-BERT (Layer 1) complete
- Blocked on HathiTrust corpus acquisition
- Timeline: Months

---

## The Crisis: Deleted Corpus

### What Happened (November 12, 2025)

The **Historical English Poetry Corpus (HEPC)** was accidentally deleted during repository cleanup.

**Corpus Details:**
- **Size**: 116,674 poems
- **Storage**: ~551 MB
- **Structure**: Organized by author folders with exact filenames from CSV
- **Location**: `/Users/justin/Repos/AI Project/Data/corpus/` (deleted)
- **Mirrored**: `~/poetry-bert-formalism/data/corpus/` on M4 Max (also affected)

**What Survived:**
- ✅ `corpus_metadata.csv` (22 MB, 116,676 rows)
  - Contains: poem_id, title, author, filepath, date, source, lines, words, file_size, content_hash
- ✅ `classified_poems_complete.csv` (36 MB)
  - Contains: Claude's 28-dimension classifications (with systematic errors)
- ❌ Actual poem texts - GONE
- ❌ No Time Machine backups
- ❌ Git ignored corpus files
- ❌ No iCloud/Drive backups

### Impact

**Immediate**:
- Cannot run Mistral-7B inference (needs poem texts)
- Cannot validate classifications
- Cannot proceed with Track 1

**Research**:
- Months of corpus curation lost
- 116K+ poems need text recovery
- Workflow completely blocked

---

## Immediate Solution: Corpus Reconstruction

### Strategy

Reconstruct the corpus by fetching poems from poetryplatform.org API and matching them to CSV metadata using fuzzy matching on author+title.

### Four-Phase Reconstruction Plan

#### Phase 1: Fetch All Poems from API ⏳ IN PROGRESS

**Source**: `https://www.poetryplatform.org/api/poets_full` (paginated)

**Status**: Running on M4 Max
- Currently: Page 609+
- Collected: 79,924+ poems
- Expected total: ~86,000 poems available

**Output**: In-memory list of poem dictionaries:
```python
{
    'title': str,
    'author': str,
    'text': str  # CLEAN text only
}
```

#### Phase 2: Fuzzy Match to CSV Metadata ⏸️ PENDING

**Method**: Author + title similarity matching

**Thresholds**:
- Title similarity: 85%
- Author similarity: 80%
- Combined score: (title × 0.55) + (author × 0.45)

**Matching Algorithm**:
```python
for csv_row in metadata:
    best_match = None
    best_score = 0

    for api_poem in api_poems:
        title_sim = SequenceMatcher(
            normalize(csv_row['title']),
            normalize(api_poem['title'])
        ).ratio()

        author_sim = SequenceMatcher(
            normalize(csv_row['author']),
            normalize(api_poem['author'])
        ).ratio()

        score = (title_sim * 0.55) + (author_sim * 0.45)

        if score > best_score:
            best_score = score
            best_match = api_poem

    if title_sim >= 0.85 and author_sim >= 0.80:
        matched.append(csv_row + api_poem)
    else:
        unmatched.append(csv_row)
```

**Expected Results**:
- Matched: ~70,000-80,000 poems (60-70%)
- Unmatched: ~30,000-40,000 poems
- Unmatched reasons:
  - Not available on poetryplatform.org
  - Title/author variations too different
  - Poems from other sources (Gutenberg, etc.)

#### Phase 3: Save with Exact Filenames ⏸️ PENDING

**Critical Requirements**:
1. ✅ Use exact filepath from CSV (e.g., "Author Name/000123_Poem Title_Author Name_1850.txt")
2. ✅ Clean text only - NO metadata, NO titles, NO bylines, NO artifacts
3. ✅ Preserve lineation (line breaks maintained)
4. ✅ Organize by author folders (from CSV filepath)
5. ✅ Save to: `~/poetry-bert-formalism/data/corpus/` on M4 Max

**Text Cleaning Function**:
```python
def clean_text(text):
    """
    Clean poem text - remove ALL metadata, preserve lineation.
    User requirement: NO metadata, NO titles, NO typographic renderings.
    """
    if not text:
        return ""

    # Remove metadata patterns
    text = re.sub(r'^.*?(?:by|BY)\s+[A-Z].*?\n', '', text, count=1, flags=re.MULTILINE)

    # Remove title at start (all caps or Title Case, short line)
    lines = text.split('\n')
    if len(lines) > 1:
        first_line = lines[0].strip()
        if len(first_line) < 100 and (first_line.isupper() or first_line.istitle()):
            text = '\n'.join(lines[1:])

    # Strip leading/trailing whitespace but preserve internal line breaks
    text = text.strip()

    return text
```

**Example Output Structure**:
```
~/poetry-bert-formalism/data/corpus/
├── 1, King Charles/
│   └── 000001_On a Quiet Conscience_1, King Charles_unknown.txt
├── Browning, Elizabeth Barrett/
│   ├── 000234_Sonnet 43_Browning, Elizabeth Barrett_1850.txt
│   └── 000235_The Cry of the Children_Browning, Elizabeth Barrett_1843.txt
└── Shakespeare, William/
    ├── 005021_Sonnet 1_Shakespeare, William_1609.txt
    └── 005022_Sonnet 2_Shakespeare, William_1609.txt
```

#### Phase 4: Validation & Reporting ⏸️ PENDING

**Reports Generated**:
1. `reconstruction_stats.txt` - Coverage statistics
2. `reconstruction_log.txt` - Detailed matching log
3. `unmatched_poems.csv` - List of poems not found

**Validation Checks**:
- File count matches saved count
- Filepaths match CSV exactly
- Text is clean (no metadata detected)
- All author directories created
- No duplicate files

---

## Secondary Problem: Claude's Systematic Mislabeling

### The Issue

The `classified_poems_complete.csv` contains 116,674 poems with 28 metadata dimensions labeled by Claude. However, **Claude doesn't understand literary theory**, leading to systematic category errors.

### Systematic Classification Errors

| Field | Claude's Error | Should Be | Example |
|-------|---------------|-----------|---------|
| **person** | "Linear", "Literary" | First/Second/Third | "I wandered" → First (not "Linear") |
| **focalization** | "Future" | Zero/Internal/External (Genette) | All labeled "Future" (nonsense) |
| **narrative_level** | "Omniscient", "Multiple stanzas" | Extradiegetic/Intradiegetic/Metadiegetic | Confusing narratology with structure |
| **temporal_orientation** | 100% "Present" | Past/Present/Future/Atemporal | Everything labeled "Present" |
| **addressee_type** | "Personal experience" | Self/Other/Apostrophic/Reader | Confusing content with addressee |
| **meter** | "ABAB" (rhyme scheme!) | Iambic pentameter/Trochaic/etc. | Confusing meter with rhyme |

### Why This Matters

These errors make the metadata **unusable for literary analysis**. You cannot:
- Study narrative perspective shifts (focalization all wrong)
- Analyze temporal structures (all "Present")
- Examine metrical patterns (confused with rhyme)
- Understand address modes (categories invalid)

### Root Cause

**LLMs pattern-match without understanding theory**. Claude has never read:
- Genette's *Narrative Discourse* (focalization theory)
- Puttenham's *Arte of English Poesie* (prosody definitions)
- Saintsbury's *History of English Prosody* (metrical analysis)

So it guesses based on surface patterns, not theoretical grounding.

---

## Long-term Solution: Theory-Aware Classification

### The Approach

**Train a model on actual prosody and narratology texts** so it understands what these terms *mean*, not just correlates patterns.

### Prosody Text Collection

#### Tool: Smart Prosody Scraper ⏳ IN PROGRESS

**Location**: `/Users/justin/Repos/AI Project/prosody_tools/smart_prosody_scraper.py`

**What It Does**:
1. Downloads T.V.F. Brogan bibliography from Princeton Prosody Archive (Zenodo)
2. Extracts ~2,000 public domain prosody works (pre-1923)
3. Prioritizes 50 essential prosody texts
4. Searches for specific titles on:
   - Project Gutenberg
   - Internet Archive
5. Downloads actual prosody manuals (not nursery rhymes!)

**Status**: Running on M4 Max
- Currently: Searching 16/50 essential works
- Downloaded so far:
  - Saintsbury's "History of English Prose Rhythm"
  - Shelley's "Defence of Poetry"
  - Gummere's "Beginnings of Poetry"
  - Johnson's "Lives of English Poets"
  - Moore's "Historical Outlines of English Phonology"
  - And more...

**Output**: `~/poetry-bert-formalism/prosody_texts/`

#### Essential Authors Being Collected

- George Puttenham (*Arte of English Poesie*)
- George Gascoigne (*Certayne Notes of Instruction*)
- Philip Sidney (*Defence of Poesie*)
- Thomas Campion (*Observations in the Art of English Poesie*)
- Samuel Daniel (*Defence of Ryme*)
- George Saintsbury (*History of English Prosody* - 3 volumes)
- Edwin Guest (*History of English Rhythms*)
- Robert Bridges (*Milton's Prosody*)
- And 17+ more authoritative sources

### Theory-Aware Training Pipeline

#### Step 1: Extract Definitions from Prosody Texts

Parse prosody manuals to extract:
- Definitions of metrical terms (iambic, trochaic, etc.)
- Explanations of rhyme schemes vs. meter
- Narratological concepts (if present in texts)
- Historical terminology and usage

#### Step 2: Create Instruction Dataset

Combine:
1. **Prosody definitions** (from extracted texts)
2. **Correct examples** (397 manually-labeled poems)
3. **Error corrections** (Claude's mistakes → correct labels)

Format:
```json
{
  "instruction": "Classify the grammatical person of this poem",
  "poem": "I wandered lonely as a cloud\nThat floats on high o'er vales and hills",
  "correct_label": "First",
  "explanation": "Uses 'I' pronoun, indicating first-person perspective",
  "common_error": "Linear (incorrect - this confuses temporal with grammatical structure)"
}
```

#### Step 3: Fine-tune Classification Model

**Architecture**:
```python
class ProsodyAwareClassifier:
    def __init__(self):
        self.base_model = AutoModel.from_pretrained('roberta-base')
        # OR: Use EEBO-BERT for historical language understanding

        self.classifiers = {
            'person': nn.Linear(768, 3),              # First/Second/Third
            'focalization': nn.Linear(768, 3),        # Zero/Internal/External
            'narrative_level': nn.Linear(768, 3),     # Extra/Intra/Meta-diegetic
            'temporal_orientation': nn.Linear(768, 4), # Past/Present/Future/Atemporal
            'meter': nn.Linear(768, 10),              # Iambic/Trochaic/etc.
            'rhyme_scheme': nn.Linear(768, 15),       # ABAB/AABB/etc. (separate!)
            # ... 22 more classification heads
        }
```

**Training Data**:
- Prosody text chunks with extracted concepts
- 397 manually-labeled poems (correct labels)
- Error correction examples (Claude's mistakes)
- Theory definitions as instruction-following examples

**Expected Improvements**:

| Field | Before (Claude) | After (Theory Model) |
|-------|----------------|---------------------|
| person | "Linear" | "First" ✓ |
| focalization | "Future" | "Internal" ✓ |
| narrative_level | "Omniscient" | "Intradiegetic" ✓ |
| temporal_orientation | "Present" (100%) | "Past" / "Present" / varied ✓ |
| meter | "ABAB" | "Iambic pentameter" ✓ |
| rhyme_scheme | (missing) | "ABAB" ✓ |

#### Step 4: Re-classify 116K Corpus

Once corpus is reconstructed AND theory-aware model is trained:
1. Load fine-tuned prosody classifier
2. Process poems in batches (1,000 at a time)
3. Generate all 28 classification fields
4. Save with confidence scores
5. Flag low-confidence predictions for human review

**Output**: `classified_poems_theory_aware.csv`

---

## Current Status

### Running Processes (November 13, 2025)

#### On M4 Max (100.65.21.63)

**1. Corpus Reconstruction Script**
- **Status**: ⏳ Phase 1 in progress (API fetching)
- **Location**: `~/poetry-bert-formalism/scripts/reconstruct_hepc_corpus.py`
- **Output**: `~/poetry-bert-formalism/reconstruction_output.log`
- **Progress**: Page 609+, 79,924 poems collected
- **Next**: Phase 2 (fuzzy matching), Phase 3 (saving), Phase 4 (validation)

**2. Smart Prosody Scraper**
- **Status**: ⏳ Running (searching 16/50 essential works)
- **Location**: `~/poetry-bert-formalism/scripts/smart_prosody_scraper.py`
- **Output**: `~/poetry-bert-formalism/prosody_scraper_output.log`
- **Downloaded**: 6+ prosody texts so far
- **Target**: ~50 essential prosody manuals

#### On MacBook Air (Local)

**3. Background Classification Sessions** (appears to be older work)
- Multiple session monitors running (session1-session5)
- Likely related to earlier Mistral-7B classification attempts
- May be outdated/superseded by reconstruction needs

### Data Status

**Air (Local Machine)**:
```
/Users/justin/Repos/AI Project/Data/
├── HEPC/
│   ├── Metadata/
│   │   └── corpus_metadata.csv (22 MB) ✅ SURVIVED
│   └── corpus/ ❌ DELETED (was ~551 MB)
├── Datasets/
└── [other data]
```

**M4 Max**:
```
~/poetry-bert-formalism/data/
├── corpus_metadata.csv (22 MB) ✅
├── classified_poems_complete.csv (36 MB) ✅ (Claude's errors)
├── corpus/ (173 subdirs) ⏳ BEING RECONSTRUCTED
├── classifications/ (old session data)
└── prosody_texts/ ⏳ BEING POPULATED
```

### Timeline Estimates

**Immediate (24-48 hours)**:
- ✅ Phase 1: API fetching (~1-2 hours) - NEARLY COMPLETE
- ⏸️ Phase 2: Fuzzy matching (~30 mins)
- ⏸️ Phase 3: Saving files (~1 hour)
- ⏸️ Phase 4: Validation (~15 mins)
- **Result**: ~70,000-80,000 poems recovered

**Short-term (1 week)**:
- Prosody scraper completes (~2-3 days)
- Extract definitions from prosody texts (2-3 days)
- Create theory-aware instruction dataset (1 day)

**Medium-term (2-3 weeks)**:
- Fine-tune theory-aware classifier (3-5 days with GPU)
- Validate on subset (1 day)
- Run inference on reconstructed corpus (1-2 days)
- Review and iterate (ongoing)

**Additional 30K Poems** (TBD):
- User mentioned: "those additional 30K poems are available, we will just have to get them once we are done with the scraper"
- Source unknown (possibly Gutenberg, JSONL archives, or other sources)
- To be addressed after initial reconstruction

---

## Next Steps

### Immediate Actions (Once Phase 1 Completes)

1. **Monitor reconstruction completion**
   ```bash
   ssh justin@100.65.21.63 "tail -f ~/poetry-bert-formalism/reconstruction_output.log"
   ```

2. **Review Phase 1 results**
   - Total API poems fetched
   - Quality of texts
   - Completeness

3. **Phase 2: Run fuzzy matching**
   - Automatic when Phase 1 completes
   - Monitor matching statistics
   - Review unmatched list

4. **Phase 3: Save files**
   - Verify clean text requirement
   - Check exact filepath matching
   - Validate author folder structure

5. **Phase 4: Validation**
   - Review reconstruction statistics
   - Spot-check random samples
   - Verify file counts

### Post-Reconstruction

1. **Unblock Mistral-7B inference**
   - Run validation on 40 poems
   - Run inference on ~70K reconstructed poems
   - Generate classifications with confidence scores

2. **Complete prosody text collection**
   - Let smart scraper finish (~50 texts)
   - Review downloaded manuals
   - Assess coverage of key concepts

3. **Build theory-aware classifier**
   - Extract definitions from prosody texts
   - Create instruction dataset
   - Fine-tune model
   - Validate against known examples

4. **Re-classify corpus**
   - Run theory-aware model on reconstructed corpus
   - Compare with Claude's labels
   - Identify systematic corrections
   - Generate final metadata

### Additional 30K Poems

Once initial reconstruction is complete:
- User to provide source/method for additional poems
- Integrate into corpus with same cleaning standards
- Re-run matching and classification

---

## Key Files & Locations

### Scripts

**Reconstruction**:
- `/tmp/reconstruct_hepc_corpus.py` (Air - original)
- `~/poetry-bert-formalism/scripts/reconstruct_hepc_corpus.py` (M4 Max - running)

**Prosody Tools**:
- `/Users/justin/Repos/AI Project/prosody_tools/smart_prosody_scraper.py`
- `/Users/justin/Repos/AI Project/prosody_tools/prosody_theory_trainer.py`
- `~/poetry-bert-formalism/scripts/smart_prosody_scraper.py` (M4 Max - running)

### Data Files

**Metadata**:
- `/Users/justin/Repos/AI Project/Data/HEPC/Metadata/corpus_metadata.csv` (Air)
- `~/poetry-bert-formalism/data/corpus_metadata.csv` (M4 Max)
- Columns: poem_id, title, author, date, source, filepath, lines, words, file_size, content_hash

**Classifications**:
- `~/poetry-bert-formalism/data/classified_poems_complete.csv` (M4 Max)
- Contains Claude's 28-dimension labels (with systematic errors)

**Corpus** (being reconstructed):
- `~/poetry-bert-formalism/data/corpus/` (M4 Max)
- Target: 116,674 poems in author subdirectories
- Current: ~173 subdirectories being populated

**Prosody Texts** (being collected):
- `~/poetry-bert-formalism/prosody_texts/` (M4 Max)
- Target: ~50 essential prosody manuals
- Current: 6+ texts downloaded

### Models

**Mistral Classifier** (blocked):
- `~/poetry-bert-formalism/models/poetry-classifier-mistral7b/` (M4 Max)
- Trained on 357 examples
- Ready for inference once corpus reconstructed

**Historical BERTs** (for layered architecture):
- `~/poetry-bert-formalism/models/eebo-bert/` (Layer 1, 1595-1700)
- `~/poetry-bert-formalism/models/ecco-bert/` (Layer 1, 1700-1800)
- `~/poetry-bert-formalism/models/blbooks-bert/` (Layer 1, 1800-1900)

### Logs

**Reconstruction**:
- `~/poetry-bert-formalism/reconstruction_output.log` (M4 Max)
- `~/poetry-bert-formalism/Data/corpus/reconstruction_log.txt` (when complete)
- `~/poetry-bert-formalism/Data/corpus/reconstruction_stats.txt` (when complete)

**Prosody Scraper**:
- `~/poetry-bert-formalism/prosody_scraper_output.log` (M4 Max)
- `~/poetry-bert-formalism/prosody_texts/found_prosody_texts.json` (when complete)

---

## Documentation References

### Project Documentation

**Main README**:
- `/Users/justin/Repos/AI Project/README.md`
- Overview of layered BERT architecture
- Current status and trajectory tortuosity results

**Claude Context** (for AI assistants):
- `/Users/justin/Repos/AI Project/claude_context/START_HERE.md` - Architecture overview
- `/Users/justin/Repos/AI Project/claude_context/PRAGMATIC_WORKFLOW.md` - Two-track approach
- `/Users/justin/Repos/AI Project/claude_context/ARCHITECTURE_CORRECT.md` - Full technical details

### Prosody Tools Documentation

- `/Users/justin/Repos/AI Project/prosody_tools/README_FOR_CLAUDE_CODE.md` - AI assistant guide
- `/Users/justin/Repos/AI Project/prosody_tools/README_PROSODY_TOOLS.md` - Full tool documentation
- `/Users/justin/Repos/AI Project/prosody_tools/USE_SMART_SCRAPER.md` - Why smart scraper is better
- `/Users/justin/Repos/AI Project/prosody_tools/SOLUTION_SUMMARY.md` - Quick overview

---

## Critical Requirements (DO NOT FORGET)

### Text Cleaning

**Absolute Requirements**:
1. ✅ **NO metadata** in saved files
2. ✅ **NO titles** at start of poems
3. ✅ **NO bylines** ("by Author Name")
4. ✅ **NO artifacts** or typographic renderings
5. ✅ **Preserve lineation** (line breaks are content)
6. ✅ Only strip leading/trailing whitespace

**Examples**:

❌ **BAD** (has metadata):
```
THE CLOUD
by Percy Bysshe Shelley

I bring fresh showers for the thirsting flowers,
From the seas and the streams
```

✅ **GOOD** (clean):
```
I bring fresh showers for the thirsting flowers,
From the seas and the streams
```

### Filepath Matching

**Critical**:
- Use EXACT filepath from CSV `filepath` column
- Example: `"Shelley, Percy Bysshe/012345_The Cloud_Shelley, Percy Bysshe_1820.txt"`
- Create author directory: `"Shelley, Percy Bysshe/"`
- Use exact filename: `"012345_The Cloud_Shelley, Percy Bysshe_1820.txt"`

### Rejected Approaches

❌ **JSONL files** - Explicitly rejected by user as "worthless"
❌ **Numeric ID fetching** - poetryplatform.org doesn't support poem ID lookup
❌ **Keyword scraping** - Too many false positives (nursery rhymes, etc.)
✅ **API + fuzzy matching** - Current approach

---

## Contact & Notes

**Project**: Historical English Poetry Formalism Research
**Primary Machine**: M4 Max (100.65.21.63) - main computation
**Development Machine**: MacBook Air - scripts and context

**Git Repository**: `/Users/justin/Repos/AI Project/`
**Mirrored on M4**: `~/poetry-bert-formalism/`

---

*This document tracks the emergency corpus reconstruction effort and the parallel development of theory-aware classification to fix Claude's systematic labeling errors. Both are critical for completing Track 1 (Mistral-7B inference) and enabling the larger layered BERT architecture research.*

**Last Updated**: November 13, 2025, 17:30
**Next Review**: When Phase 1 (API fetching) completes
