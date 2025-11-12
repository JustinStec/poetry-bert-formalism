# System Audit Results

**Date**: November 12, 2025
**Audited by**: Claude

---

## 1. GitHub Repository

**Status**: ✓ Connected and synced

- **URL**: `git@github.com:JustinStec/poetry-bert-formalism.git`
- **Account**: JustinStec
- **Branch**: main
- **Air status**: Up to date with origin/main
- **Max status**: Up to date with origin/main
- **GitHub CLI**: Authenticated ✓

### Untracked Files (Air)
```
Data/phase3/corpus_metadata.csv
Data/phase3/missing_texts.csv
Data/phase3/temp_texts/
Data/phase3/training_dataset_complete.jsonl
Data/phase3/training_poems_with_texts.jsonl
Data/phase3/training_texts_collected.csv
docs/SYSTEM_AUDIT.md
scripts/phase3/*.py (5 new scripts)
```

### Git Configuration
- **.gitignore**: ✓ Properly configured
  - Excludes: models/*.pt, data/raw/*, data/processed/*, .credentials/
  - Excludes: archive/old_structure/, archive/old_logs/

---

## 2. HuggingFace

**Status**: ✗ Not logged in

- **CLI command**: `hf auth whoami` → "Not logged in"
- **Action needed**: Login to HuggingFace or determine if models exist

### Questions
- Do you have a HuggingFace account?
- Have you uploaded models there before?
- If yes, what's the username/organization?

---

## 3. MacBook Air

**Location**: `/Users/justin/Repos/AI Project`
**Total size**: 8.3GB
**Git status**: Clean (all committed except today's work)

### Key Contents
- ✓ **Code**: src/, scripts/, notebooks/
- ✓ **Docs**: docs/, README.md
- ✓ **Phase 3 data**: training_dataset_complete.jsonl (397 poems)
- ✓ **Results**: EEBO-BERT analysis CSVs
- ✗ **Models**: No .pt/.pth/.bin files found
- ✗ **Corpus texts**: Not on Air (only metadata)

### EEBO-BERT Status on Air
- **Training log**: ✓ Found (61K EEBO-TCP texts processed)
- **Analysis results**: ✓ Found (Shakespeare sonnets analyzed)
- **Model weights**: ✗ NOT FOUND
- **Training notebooks**: ✓ Found (poetry_eebo_bert_training.ipynb)

---

## 4. M4 Max

**Location**: `~/poetry-bert-formalism`
**Total size**: 977MB
**Git status**: Clean

### Key Contents
- ✓ **Code**: Synced with Air
- ✓ **Corpus texts**: 116,674 poems (551MB)
- ✓ **Corpus metadata**: corpus_final_metadata.csv (41MB)
- ✓ **Shakespeare dataset**: shakespeare_complete_works.jsonl (31MB)
- ✗ **Models**: No EEBO-BERT found
- ✓ **Phase 3 folder**: Created but needs organization

### Directory Structure Issues
```
Data/
├── Datasets/              # Confusing name
├── metadata/              # OK
├── phase3/                # Why only phase3?
├── processed/
│   └── poetry_platform_renamed/  # TERRIBLE NAME - should be corpus/texts/
└── raw/                   # Empty

```

---

## 5. Critical Files Status

| File | Air | Max | GitHub | HuggingFace |
|------|-----|-----|--------|-------------|
| Code (src/) | ✓ | ✓ | ✓ | N/A |
| Scripts | ✓ | ✓ | ✓ | N/A |
| Docs | ✓ | ✓ | ✓ | N/A |
| Corpus (116K) | ✗ | ✓ | ✗ (too large) | ? |
| Training data (397) | ✓ | Partial | ✗ (not committed) | ? |
| EEBO-BERT model | ✗ | ✗ | ✗ | ? |
| Shakespeare dataset | ✗ | ✓ | ✗ (too large) | ? |

---

## 6. Problems Identified

### Critical
1. **EEBO-BERT model missing** - Trained but weights not found on either machine
2. **No HuggingFace login** - Can't check if models are uploaded
3. **Directory naming chaos** - "poetry_platform_renamed" is unintuitive
4. **Phase 3 data not committed** - Today's work not in Git

### Medium Priority
5. **No phase1/phase2 folders** - Only phase3 exists, inconsistent
6. **Corpus only on Max** - Air can't access for development
7. **Large files in Git path** - Need better data organization

### Low Priority
8. **Empty raw/ directory** - Unused, should remove or document
9. **Archive bloat** - Old files not clearly organized

---

## 7. Action Plan

### Immediate (Do First)
1. **Find EEBO-BERT**
   - Check external drives
   - Check HuggingFace (after login)
   - May need to retrain if lost

2. **HuggingFace audit**
   - Login to HuggingFace
   - Check for existing models
   - Check for existing datasets

3. **Commit Phase 3 work**
   - Add training dataset to Git (it's small enough)
   - Commit new scripts
   - Push to GitHub

### Organization (Do Second)
4. **Reorganize M4 Max Data/**
   ```
   Data/
   ├── corpus/              # Renamed from processed/poetry_platform_renamed/
   │   ├── texts/           # 116K poems
   │   └── metadata.csv
   ├── datasets/            # Other datasets
   │   └── shakespeare/
   ├── training/            # Training data
   │   └── phase3_classifications/
   └── archive/             # Old files
   ```

5. **Sync directory structure to Air** (empty folders for reference)

6. **Update .gitignore** if needed

### Documentation (Do Third)
7. **Document sync workflow** in README
8. **Create SETUP.md** for new developers
9. **Update SYSTEM_AUDIT.md** with decisions

---

## 8. Questions for User

1. **EEBO-BERT**: Do you remember where you saved the trained model?
2. **HuggingFace**: Do you have an account? What's the username?
3. **18th/19th/20th century corpora**: Do these exist anywhere?
4. **Priority**: Should we find EEBO-BERT first, or proceed with Phase 3B using a different model?

---

## 9. Recommended Workflow Going Forward

### Development (Air)
1. Make code changes
2. Test with small sample data
3. Commit and push to GitHub

### Compute (Max)
1. Pull latest code from GitHub
2. Run heavy jobs (training, inference)
3. Save results locally
4. Copy small results back to Air

### Storage
- **Code**: GitHub (source of truth)
- **Models**: HuggingFace (after training)
- **Large data**: Max only (accessed via SSH)
- **Small results**: Both machines (sync via Git or scp)

