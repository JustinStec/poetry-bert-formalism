# Archive Building Strategy: Multi-Source Poetry Corpus

## Problem Statement

PoetryDB alone provides only ~3,162 poems, with significant gaps:
- Limited period coverage (mostly 1800-1900)
- Missing metadata (49% unknown period, 89% unknown genre)
- No drama texts (critical for Shakespeare career analysis)
- Insufficient scale for robust computational historical formalism

**Goal:** Build comprehensive multi-period poetry archive with complete metadata for tracking formal features across periods, authors, and genres.

---

## Current Status

### ✓ Completed
1. **PoetryDB** (3,162 poems, 129 authors)
   - Location: `Data/poetry_corpus/poetrydb.jsonl`
   - Strengths: Structured, API access, clean formatting
   - Gaps: Metadata, period coverage

2. **Shakespeare Complete Works** (40 works, 181K lines)
   - Location: `Data/poetry_corpus/shakespeare_complete_works.jsonl`
   - Chronologically organized by career period
   - Includes plays, sonnets, narrative poems
   - Ready for career-arc analysis

3. **Gutenberg Poetry Corpus** (5.5M lines)
   - Location: `~/Library/CloudStorage/GoogleDrive-.../gutenberg_poetry_corpus_clean.jsonl`
   - Issue: Lines scattered, need to reconstruct complete poems
   - Currently training BERT (16% complete)

4. **EEBO Corpus** (7.6GB, ~60K texts, 1595-1700)
   - Location: `~/Library/CloudStorage/GoogleDrive-.../EEBO_1595-1700/eebo_cleaned_corpus.txt`
   - Word2Vec trained and aligned ✓
   - Mostly prose, some poetry

---

## Multi-Source Archive Strategy

### Tier 1: Immediate Access (No Barriers)

#### 1. Project Gutenberg Individual Author Collections
**What:** Download complete works of major poets individually
**How:** Extend `download_shakespeare_corpus.py` pattern
**Coverage:** 1500-1900
**Effort:** Low

**Priority Authors:**
- John Milton (Paradise Lost, other works)
- John Donne (metaphysical poetry)
- Alexander Pope (Augustan period)
- William Wordsworth (Romantic)
- Samuel Taylor Coleridge (Romantic)
- Percy Shelley (Romantic)
- John Keats (Romantic)
- Lord Byron (Romantic)
- Alfred Tennyson (Victorian)
- Robert Browning (Victorian)
- Walt Whitman (American)
- Emily Dickinson (American)

**Implementation:**
```python
MAJOR_POETS = [
    {'author': 'John Milton', 'works': [
        {'title': 'Paradise Lost', 'date': 1667, 'gutenberg_id': 20},
        {'title': 'Paradise Regained', 'date': 1671, 'gutenberg_id': 58},
        # ...
    ]},
    # ...
]
```

#### 2. Chadwyck-Healey English Poetry Database
**What:** Access via IU Library subscription
**Coverage:** ~4,500 volumes, 1500-1900
**How:** Check IU Library → ProQuest Literature Online
**Effort:** Medium (web scraping or API if available)

#### 3. Victorian Women Writers Project
**What:** Open-access Indiana University digital library
**URL:** https://webapp1.dlib.indiana.edu/vwwp/
**Coverage:** Victorian women poets (underrepresented in PoetryDB)
**Effort:** Low (TEI-XML format)

---

### Tier 2: HathiTrust (IU Institutional Access)

You have access to **6.5M public domain volumes** via IU. This is the key to scaling up.

#### Option A: HTRC Data Capsule (Secure Mode)
**What:** Analyze 17M volumes (including in-copyright) in secure VM
**Process:**
1. Request Data Capsule access via HTRC
2. Create workset of poetry volumes
3. Run analysis inside capsule
4. Export non-consumptive results only

**Best for:** Large-scale feature extraction where you don't need full text export

#### Option B: HathiTrust Bulk Download (Public Domain)
**What:** Download 6.5M public domain volumes via rsync
**Process:**
```bash
# IU has rsync access
rsync -av data.analytics.hathitrust.org::pd-texts/ /path/to/corpus/
```

**Filtering strategy:**
1. Use HathiTrust Bibliographic API to get metadata
2. Filter by:
   - Language: English
   - Genre: Poetry, Drama (MARC field 655)
   - Date range: 1500-1900
3. Download only poetry/drama volumes
4. Parse and structure

**Implementation:**
```python
# Query HathiTrust Bib API
def get_poetry_volumes(start_year, end_year):
    query = f"language:eng AND genre:poetry AND date:[{start_year} TO {end_year}]"
    # Returns volume IDs for rsync download
```

#### Option C: HTRC Extracted Features
**What:** Token counts, page-level metadata (already downloaded sample)
**Location:** `/Users/justin/Downloads/sample-EF202003`
**Use case:** Period-specific language models (Layer 1 training data)
**Not useful for:** Prosody analysis (need full text)

---

### Tier 3: ECCO Corpus (IU Institutional Access)

**What:** Eighteenth Century Collections Online
**Coverage:** 1700-1800 (fills gap between EEBO and Gutenberg)
**Size:** ~180,000 titles
**Access:** IU Library subscription

**Process:**
1. Contact IU Library data services
2. Request ECCO-TCP (Text Creation Partnership) full-text access
3. Filter for poetry/drama
4. Use for period-specific BERT training (1700-1800)

---

### Tier 4: Modern Poetry (1900-2000)

#### 1. Poetry Foundation API
**What:** ~50,000 poems, contemporary + historical
**URL:** https://www.poetryfoundation.org
**Access:** Web scraping (no official API)
**Effort:** Medium

#### 2. Project MUSE
**What:** Scholarly journals, many with poetry
**Access:** IU subscription
**Effort:** High (article-by-article)

#### 3. Archive.org Poetry Collections
**What:** Digitized poetry books, public domain
**Effort:** Medium (variable OCR quality)

---

## Recommended Implementation Plan

### Phase 1: Immediate (This Week)
**Build "Core 100 Poets" corpus**

1. Extend Shakespeare script to download 50-100 major poets from Gutenberg
2. Add chronological metadata (birth year, major period, career phases)
3. Structure for career-arc analysis

**Output:**
- ~10,000-20,000 complete poems
- Full metadata (author, date, genre, period)
- Ready for formal feature tracking

**Effort:** 1-2 days of scripting

---

### Phase 2: Medium-term (Post-CMU, Next Month)
**HathiTrust Poetry Workset**

1. Create HathiTrust Collection of English poetry volumes (1500-1900)
2. Use HTRC Analytics API to filter by genre
3. Download via rsync or Data Capsule
4. Parse and structure with metadata

**Output:**
- Potentially 100,000+ poems
- Complete period coverage (1500-1900)
- Sufficient scale for robust computational analysis

**Effort:** 1-2 weeks

---

### Phase 3: Long-term (Next Semester)
**Modern Poetry + Drama Expansion**

1. Add 20th century poetry (Poetry Foundation, Archive.org)
2. Expand drama collection (Folger Shakespeare Library, other playwrights)
3. Add ECCO poetry for 18th century

**Output:**
- Complete 1500-2000 coverage
- Multi-genre (lyric, narrative, drama)
- Ready for comprehensive formal feature tracking

---

## Metadata Schema

All poems should be structured with this schema:

```json
{
    "poem_id": "unique_identifier",
    "title": "Poem Title",
    "author": "Author Name",
    "author_birth": 1564,
    "author_death": 1616,
    "composition_date": 1609,
    "publication_date": 1609,
    "period": "early_modern|restoration|augustan|romantic|victorian|modern",
    "author_career_period": "early|middle|late|final",
    "genre": "sonnet|lyric|narrative|epic|drama|etc",
    "form": "blank_verse|heroic_couplet|free_verse|etc",
    "source": "gutenberg|hathitrust|poetrydb|etc",
    "source_id": "gutenberg_1041",
    "text": "Full poem text...",
    "lines": ["line 1", "line 2", ...],
    "line_count": 154,
    "structured_lines": [
        {
            "line_num": 0,
            "text": "From fairest creatures we desire increase,",
            "is_blank": false,
            "speaker": null,  // For drama
            "is_verse": true,
            "stanza_num": 1,
            "rhyme_position": "A"
        }
    ]
}
```

---

## Next Steps

### Immediate Action Items:

1. **Create "Core 100 Poets" downloader** (extends Shakespeare script)
   - Priority: Milton, Donne, Wordsworth, Keats, Browning, Whitman
   - ~2 hours of work

2. **Reconstruct Gutenberg corpus into complete poems**
   - Parse `gutenberg_poetry_corpus_clean.jsonl` to identify poem boundaries
   - Extract metadata from original Gutenberg files
   - ~4 hours of work

3. **Query HathiTrust Bib API for poetry volumes**
   - Build filtered list of poetry/drama volumes (1500-1900)
   - Estimate: 10,000-50,000 volumes
   - ~2 hours of work

4. **Contact IU Library about ECCO-TCP access**
   - Email data services
   - Request 18th century poetry corpus
   - ~30 minutes

### Which should we prioritize?

For career-arc tracking and feature analysis, I recommend:
- **Short-term:** Core 100 Poets from Gutenberg (immediate, clean metadata)
- **Medium-term:** HathiTrust workset (massive scale, institutional access)
- **Long-term:** ECCO + modern poetry (complete periodization)

This gives you a working corpus within days, while building toward comprehensive coverage.
