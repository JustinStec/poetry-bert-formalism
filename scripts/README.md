# Poetry Corpus Scripts

Active scripts for managing and training on the unified poetry corpus.

## Current Active Scripts

### Corpus Building & Management

**`scrape_poetry_platform.py`**
- Scrapes poems from poetryplatform.org
- Downloaded 124,755 poems from 9,400 poets
- Output: `poetry_platform_scraped/` directory

**`organize_scraped_poems.py`**
- Organizes scraped poems into author folders
- Prevents Finder crashes with large flat directories

**`rename_poetry_platform_to_standard.py`**
- Standardizes Poetry Platform filenames to corpus convention
- Format: `{poem_id}_{title}_{author: Last, First}_{year}.txt`
- Created standardized corpus with poem IDs 62281-185485

**`merge_and_deduplicate_corpora.py`**
- Merges Poetry Platform + Gutenberg corpora
- Deduplicates poems (removed 4,373 Gutenberg duplicates)
- Creates unified metadata CSV
- Final corpus: 170,889 unique poems

### Corpus Cleaning & Analysis

**`analyze_title_patterns.py`**
- Analyzes title formatting across entire corpus
- Detects multi-poem files needing splitting
- Identifies patterns: italic titles, dividers, numbering systems
- Output: `title_analysis_report.md`

**`split_multi_poem_files.py`**
- Identifies and splits files containing multiple poems
- Detected 1,344 files → 6,790 poems (net +5,446)
- Output: `split_plan_report.md`, `split_plan.json`

**`clean_titles_phase1.py`**
- Cleans title formatting (removes italic markup, etc.)
- Updates metadata and renames files
- DRY_RUN mode for safe preview

**`auto_detect_junk.py`**
- Automatically detects junk files (TOCs, fragments, metadata)
- Uses pattern-based rules from manual review
- Confidence scoring system

### Manual Review & Correction

**`review_web_app.py`**
- Flask web interface for manual poem review
- Features: edit, split, mark as junk, extract titles
- Runs on localhost:5001
- Saves reviews to `manual_reviews.jsonl`

**`manual_review_interface.py`**
- Alternative CLI interface for manual review

**`apply_current_corrections.py`**
- Applies corrections from GPT-4o attribution results
- Moves poems to correct authors, deletes junk
- Applied 16,780 automatic corrections

**`extract_titles_from_verified.py`**
- Extracts and removes titles from GPT-4o verified poems
- Auto-cleans poems that bypass manual review

**`review_stats.py`**
- Generates statistics from manual review sessions

### Legacy/Analysis Scripts

**`analyze_gutenberg_cleaning.py`**
- Analysis tool for Gutenberg corpus quality

**`clean_all_gutenberg_works.py`**
- Comprehensive Gutenberg cleaning script

**`build_unified_corpus.py`**
- Earlier version of corpus unification (superseded)

### Training Scripts

**`train_hierarchical_bert.py`**
- Trains hierarchical BERT model on poetry corpus
- Layer 1: Word embeddings
- Layer 2: Line embeddings
- Layer 3: Prosody features

**`prepare_hierarchical_training_data.py`**
- Prepares data for hierarchical BERT training
- Tokenizes and structures poems

**`plot_hierarchical_training_losses.py`**
- Visualizes training progress and losses

## Key Data Files

**`ai_attribution_results.jsonl`** (23MB)
- GPT-4o author attribution results for all Gutenberg poems
- 46,899 poems processed

**`manual_reviews.jsonl`** (651KB)
- Manual review decisions and corrections
- ~657 poems reviewed

**`split_plan.json`**
- Detailed plan for splitting multi-poem files
- Ready to apply

## Reports

**`title_analysis_report.md`**
- Comprehensive analysis of title patterns
- Examples of issues found

**`split_plan_report.md`**
- Splitting plan with examples
- Shows how files will be divided

**`auto_junk_report.txt`**
- Auto-detected junk files report

**`correction_report.txt`**
- Summary of applied corrections

## Archive

Old/deprecated scripts moved to `archive/` subdirectories:
- `archive/old_cleaning_scripts/` - Legacy cleaning tools
- `archive/old_download_scripts/` - Original corpus download scripts
- `archive/old_bert_scripts/` - Earlier training experiments
- `archive/test_scripts/` - Test and debug scripts
- `archive/logs/` - Execution logs

## Workflow

Current corpus building workflow:

1. **Scraping** → `scrape_poetry_platform.py`
2. **Organization** → `organize_scraped_poems.py`
3. **Standardization** → `rename_poetry_platform_to_standard.py`
4. **Merging** → `merge_and_deduplicate_corpora.py`
5. **Analysis** → `analyze_title_patterns.py`
6. **Splitting** → `split_multi_poem_files.py` (pending)
7. **Title Cleaning** → `clean_titles_phase1.py` (pending)
8. **Content Cleaning** → (to be created)
9. **Training** → `train_hierarchical_bert.py`

## Corpus Status

- **Total poems:** 170,889 unique (before splitting)
- **After splitting:** ~176,335 poems (estimated)
- **Authors:** 12,931 unique
- **Sources:** Poetry Platform (primary) + Gutenberg (unique only)
- **Format:** Standardized filenames and metadata CSV

## Next Steps

1. Apply splits from `split_plan.json`
2. Clean titles (remove italic markup, integrate numbering)
3. Clean poem content (remove dividers, decorative elements)
4. Final corpus ready for BERT training
