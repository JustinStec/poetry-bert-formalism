# Current Archive Status

## Overview

**Two-Corpus Structure:**
1. **Poetry Corpus (Layer 2):** ~6.2M lines for training poetry-specialized BERT
2. **Historical Corpora (Layer 1):** Period-specific general English for historical language models

---

## LAYER 1: Historical Language Corpora

> **Purpose:** Train period-specific BERTs on general English (ALL genres) to learn historical semantics and syntax

### EEBO (1595-1700) ✓ COMPLETE
**Location:** `~/Library/CloudStorage/GoogleDrive-.../EEBO_1595-1700/`

**Stats:**
- 7.6GB corpus
- ~60,000 texts
- All genres: drama, poetry, sermons, science, legal, religious, etc.

**Model:**
- BERT trained ✓
- Location: `eebo_bert_finetuned/` (Google Drive)

**Status:** ✓ Complete and ready for use

---

### ECCO (1700-1800) ⏳ ACQUISITION IN PROGRESS
**Source:** HathiTrust Research Center

**Target:**
- 18th century general English
- ALL genres (novels, philosophy, essays, science, legal, poetry)
- Target size: ~1,000-5,000 books minimum

**Search Query:**
```
language:eng AND publishDate:[1700 TO 1800]
```

**Acquisition Strategy:**
1. Create workset in HathiTrust Analytics Portal
2. Download via workset export (plain text OCR)
3. Process with `scripts/preprocess_hathitrust_downloads.py`
4. OCR quality threshold: 90% minimum

**Status:** ⏳ Workset creation in progress

---

### NCCO (1800-1900) ⏳ ACQUISITION IN PROGRESS
**Source:** HathiTrust Research Center

**Target:**
- 19th century general English
- ALL genres
- Target size: ~1,000-5,000 books minimum

**Search Query:**
```
language:eng AND publishDate:[1800 TO 1900]
```

**Status:** ⏳ Workset creation in progress

---

### Modern (1900-2000) ⏳ ACQUISITION IN PROGRESS
**Source:** HathiTrust Research Center

**Target:**
- 20th century general English
- ALL genres
- Target size: ~1,000-5,000 books minimum (sample first, then expand)

**Search Query:**
```
language:eng AND publishDate:[1900 TO 2000]
```

**Note:** Extremely large corpus - recommend sampling by decade initially

**Status:** ⏳ Workset creation in progress

---

## LAYER 2: Poetry Corpus

> **Purpose:** Train poetry-specialized BERT on unified 6.2M line corpus to learn poetic conventions

### Unified Database Status
**Location:** `Data/poetry_unified.db` (SQLite)

**Import Status:**
- ✓ Gutenberg: 1,191 works, 10.9M lines in DB
- ⏳ Shakespeare: 40 works, 181K lines (pending import fix)
- ⏳ Core Poets: 51 works, 470K lines (pending import fix)
- ⏳ PoetryDB: 3,162 poems (pending import fix)

**Total Target:** ~6.2M lines across ~4,400 works

---

### 1. Gutenberg Poetry Corpus ✓ RECONSTRUCTED
**Locations:**
- **Line-level:** `~/Library/CloudStorage/GoogleDrive-.../gutenberg_poetry_corpus_clean.jsonl` (5.5M lines)
- **Reconstructed:** `Data/gutenberg_reconstructed.jsonl` (1,191 works, 395MB)
- **Database:** `Data/poetry_unified.db` (Gutenberg portion imported)

**Stats:**
- **1,191 complete works**
- **5.5 million lines**
- Properly formatted with lineation preserved
- Metadata: title, author, publication date, period, subjects

**BERT Training:**
- Status: ~50% complete (checkpoint-395000)
- Location: `gutenberg_bert_checkpoints/` (Google Drive)
- Timeline: Completes Oct 31 evening

**Status:** ✓ Reconstructed and training
**Use case:** Poetry BERT training (Layer 2)

---

### 2. Shakespeare Complete Works ✓
**Location:** `Data/poetry_corpus/shakespeare_complete_works.jsonl`

**Stats:**
- 40 works (plays, sonnets, narrative poems)
- 181,329 lines
- Chronologically organized (1591-1613)
- Career periods: early/middle/late/final

**Format:**
```json
{
    "work_id": "shakespeare_1600_hamlet",
    "title": "Hamlet",
    "author": "William Shakespeare",
    "date": 1600,
    "period": "middle",
    "genre": "tragedy",
    "text": "...",
    "lines": [...],
    "structured_lines": [...]  // For plays
}
```

**Status:** ✓ Complete
**Use case:** Career-arc analysis (T.S. Eliot-style tracking of developing blank verse)

---

### 3. Core 27 Canonical Poets ✓
**Location:** `Data/poetry_corpus/core_poets_complete.jsonl`

**Stats:**
- 27 major poets (Spenser to Poe)
- 51 works
- 470,039 lines
- Period coverage: 1590-1918
- Includes: Milton, Donne, Pope, Wordsworth, Keats, Shelley, Browning, Whitman, Dickinson

**Periods:**
- Early Modern: 9 works (1590-1681)
- Restoration: 2 works (1681-1700)
- Augustan: 5 works (1712-1768)
- Romantic: 15 works (1793-1850)
- Victorian: 12 works (1842-1918)
- American: 8 works (1845-1896)

**Format:**
```json
{
    "work_id": "john_keats_1820_lamia_isabella_and_other_poems",
    "author": "John Keats",
    "author_birth": 1795,
    "author_death": 1821,
    "composition_date": 1820,
    "period": "romantic",
    "author_career_period": "late",
    "genre": "narrative",
    "text": "...",
    "line_count": 1234
}
```

**Status:** ✓ Complete
**Use case:** Period comparisons, genre tracking, multi-author career arcs

---

### 4. PoetryDB Collection ✓
**Location:** `Data/poetry_corpus/poetrydb.jsonl`

**Stats:**
- 3,162 poems
- 129 authors
- Clean API-sourced data

**Period breakdown:**
- 1595-1700: 254 poems
- 1700-1800: 66 poems
- 1800-1900: 1,290 poems
- Unknown: 1,552 poems

**Genre breakdown:**
- Sonnets: 302
- Odes: 51
- Unknown: 2,809

**Format:**
```json
{
    "title": "Sonnet 18",
    "author": "William Shakespeare",
    "lines": ["Shall I compare thee...", ...],
    "linecount": 14,
    "period": "1595-1700",
    "genre": "sonnet"
}
```

**Status:** ✓ Complete
**Use case:** Supplementary poems, API access for expansion

---

### 5. EEBO Corpus (Early Modern Prose + Poetry) ✓
**Location:** `~/Library/CloudStorage/GoogleDrive-.../EEBO_1595-1700/eebo_cleaned_corpus.txt`

**Stats:**
- 7.6 GB
- ~60,000 texts
- Period: 1595-1700
- Word2Vec trained and aligned ✓

**Status:** ✓ Complete
**Use case:** Early Modern English embeddings, historical language model (Layer 1 training)

---

## Total Current Archive

### By Volume
- **Lines:** ~6,000,000+
- **Complete works:** ~100 major works with metadata
- **Poets:** 150+ unique authors
- **Period coverage:** 1590-1918 (robust), 1500-2000 (gaps)

### By Organizational Structure

**For BERT Training (Large-scale, line-level):**
- Gutenberg corpus: 5.5M lines ✓
- EEBO corpus: 7.6GB ✓

**For Career-Arc Analysis (Complete works, chronological):**
- Shakespeare: 40 works ✓
- Core 27 poets: 51 works ✓

**For Genre/Form Analysis (Tagged, structured):**
- PoetryDB: 3,162 poems ✓
- Shakespeare structured lines ✓
- Core poets by period ✓

---

## What This Enables NOW

### 1. Career-Arc Tracking
Track formal features across individual authors' development:

```python
# Load Shakespeare's works
with open('Data/poetry_corpus/shakespeare_complete_works.jsonl') as f:
    works = sorted([json.loads(line) for line in f], key=lambda x: x['date'])

# Track enjambment frequency over career
for work in works:
    enjambment_rate = analyze_enjambment(work['text'])
    print(f"{work['date']} ({work['period']}): {work['title']} - {enjambment_rate}%")

# Compare early vs. late periods
early = [w for w in works if w['period'] == 'early']
late = [w for w in works if w['period'] == 'late']
```

### 2. Cross-Period Comparison
Compare formal features across historical periods:

```python
# Load all core poets
romantic = load_period('romantic')  # 15 works, 1793-1850
victorian = load_period('victorian')  # 12 works, 1842-1918

# Compare metrical variants
romantic_trochaic = count_trochaic_substitutions(romantic)
victorian_trochaic = count_trochaic_substitutions(victorian)
```

### 3. Genre Evolution
Track emergence and development of genres:

```python
# Track dramatic monologue emergence (Browning's innovation)
early_modern_monologues = filter_genre('dramatic_monologue', period='early_modern')  # 0
victorian_monologues = filter_genre('dramatic_monologue', period='victorian')  # Browning's works
```

### 4. Large-Scale Statistical Analysis
Use 5.5M line Gutenberg corpus for robust statistics:

```python
# Calculate baseline metrical patterns across all 5.5M lines
baseline_patterns = analyze_meter(gutenberg_corpus)

# Compare individual authors against baseline
shakespeare_patterns = analyze_meter(shakespeare_corpus)
deviation = compare_to_baseline(shakespeare_patterns, baseline_patterns)
```

---

## Known Gaps & Future Expansion

### Metadata Gaps
- **PoetryDB:** 49% unknown period, 89% unknown genre
- **Gutenberg corpus:** Lines scattered, need poem boundaries
- **Missing composition dates** for some works

### Period Gaps
- **1700-1800:** Thin coverage (need ECCO via IU)
- **1900-2000:** Minimal (need modern poetry sources)

### Genre Gaps
- **Drama:** Only Shakespeare plays (need Marlowe, Jonson, etc.)
- **Modern free verse:** Need 20th century poets

---

## Recommended Next Actions

### Immediate (This Week - Pre-CMU)
Nothing required - current corpus is sufficient for:
- Shakespeare analysis for CMU writing sample
- BERT training completion
- Initial tortuosity experiments

### Post-CMU (Next Month)
1. **Reconstruct Gutenberg corpus** into complete poems
   - Parse line data to identify poem boundaries
   - Extract metadata from original Gutenberg files
   - Creates ~50,000+ complete poems with dates/authors

2. **Build HathiTrust poetry workset**
   - Query Bib API for English poetry 1500-1900
   - Download via IU rsync access
   - Filter and structure with metadata

3. **Request ECCO access via IU Library**
   - Fill 1700-1800 gap
   - Period-specific BERT training

### Long-term (Next Semester)
1. **Add modern poetry** (Poetry Foundation, Archive.org)
2. **Expand drama** (Folger, other playwrights)
3. **Build formal annotation pipeline** (prosody, syntax, line-level, phonological)

---

## Summary

**You already have a working archive of ~6 million lines** with multiple organizational structures ready for immediate use:

- ✓ Large-scale training data (Gutenberg 5.5M, EEBO 7.6GB)
- ✓ Career-arc analysis (Shakespeare + 27 poets with chronology)
- ✓ Period comparison (Early Modern → Romantic → Victorian → American)
- ✓ Genre tracking (17 genres including emerging forms)

**This is sufficient for:**
- CMU writing sample (Shakespeare career analysis)
- Pilot studies tracking formal features
- Initial computational historical formalism research

**Future expansion via HathiTrust/ECCO can scale to 100K+ poems** when needed for comprehensive coverage.
