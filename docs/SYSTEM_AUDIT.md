# System Audit & Synchronization Plan

**Date**: November 12, 2025
**Status**: IN PROGRESS

## Problem Statement

Currently have data/code scattered across 4 systems without clear synchronization:
1. **MacBook Air** (local development)
2. **M4 Max** (remote compute via SSH)
3. **GitHub** (version control)
4. **HuggingFace** (model storage?)

Need to audit everything and establish a single source of truth.

---

## System Audit

### 1. MacBook Air (Development Machine)

**Location**: `/Users/justin/Repos/AI Project`

**Contents**:
- Code: ✓
- Docs: ✓
- Corpus texts: ✗ (only on M4 Max)
- Phase 3 training data: ✓ (397 poems with texts)
- EEBO-BERT model: UNKNOWN
- Size: 8.3GB

**Git Status**:
- Repository: Local, not synced to GitHub
- Last commit: UNKNOWN
- Uncommitted changes: UNKNOWN

### 2. M4 Max (Compute Machine)

**Location**: `/Users/justin/poetry-bert-formalism`

**Contents**:
- Code: ✓ (synced from Air?)
- Docs: ✓
- Corpus texts: ✓ (116,674 poems, 551MB)
- Corpus metadata: ✓ (41MB CSV)
- Phase 3 training data: Partial
- EEBO-BERT model: ✗ (missing)
- Size: 977MB

**Git Status**: UNKNOWN

### 3. GitHub

**Repository**: UNKNOWN (need to check if exists)
- Private/Public: ?
- Last push: ?
- Branch structure: ?

### 4. HuggingFace

**Account**: UNKNOWN (credentials in `.credentials/poetry-bert-service-account.json`)
- Models uploaded: ?
- Datasets uploaded: ?
- Organization: ?

---

## Questions to Answer

### Code & Version Control
1. Is this repository on GitHub? What's the URL?
2. Are Air and Max repositories in sync?
3. What branch are we on?
4. What files are uncommitted?

### Data
5. Where is the EEBO-BERT model?
6. Do we have 18th/19th/20th century training corpora anywhere?
7. Which system has the most up-to-date Phase 3 data?

### Models
8. Are there any models on HuggingFace?
9. What's the HuggingFace username/organization?

### Synchronization
10. What files should live on Air vs Max?
11. What should be in Git vs excluded (`.gitignore`)?
12. What should be on HuggingFace vs local?

---

## Proposed Architecture

### MacBook Air (Source of Truth for Code)
```
/Users/justin/Repos/AI Project/
├── src/                    # Python code
├── scripts/                # Processing scripts
├── notebooks/              # Jupyter notebooks
├── docs/                   # Documentation
├── tests/                  # Unit tests
├── .git/                   # Git repository
└── Data/                   # SMALL files only
    ├── training/           # Training datasets (< 100MB)
    └── samples/            # Sample data for testing
```

**Never on Air**: Large corpus texts, model weights

### M4 Max (Compute & Storage)
```
~/poetry-bert-formalism/
├── src/                    # Synced from Air via git
├── scripts/                # Synced from Air via git
├── docs/                   # Synced from Air via git
├── Data/                   # LARGE data files
│   ├── corpus/             # 116K poems (551MB)
│   ├── datasets/           # Shakespeare, etc.
│   ├── training/           # Training data
│   └── archive/            # Old files
└── models/                 # Trained model weights
    ├── eebo_bert/
    └── poetry_eebo_bert/
```

**Never on Max**: Notebooks (run on Air with small samples)

### GitHub
- Code: `src/`, `scripts/`, `docs/`, `tests/`
- Config: `pyproject.toml`, `requirements.txt`, `README.md`
- Not in Git: `Data/`, `models/`, `.credentials/`, `*.csv` (large)

### HuggingFace
- Trained models (EEBO-BERT, Poetry-EEBO-BERT)
- Large datasets (if public)
- Not models in progress

---

## Synchronization Strategy

### Git Workflow
1. **Air = Development**
   - Make code changes on Air
   - Commit and push to GitHub

2. **Max = Pull Only**
   - Pull updates from GitHub
   - Never edit code directly on Max
   - Run compute jobs only

### Data Sync
1. **Small data** (< 100MB): Keep on both, sync via Git
2. **Large data** (> 100MB): Only on Max, access via SSH
3. **Training results**: Generate on Max, pull to Air for analysis

### Model Sync
1. **During training**: Save checkpoints on Max only
2. **After training**: Upload final model to HuggingFace
3. **For inference**: Download from HuggingFace to Max

---

## Action Items

### Immediate (Before Any Work)
- [ ] Check if GitHub repo exists, get URL
- [ ] Check Git status on both machines
- [ ] Search for EEBO-BERT on Air
- [ ] Check HuggingFace for existing models
- [ ] Document current .gitignore rules

### Organization
- [ ] Reorganize Data/ directory on Max
- [ ] Sync Data/ directory to Air (structure only)
- [ ] Create proper .gitignore
- [ ] Commit current state to Git

### Documentation
- [ ] Document sync workflow in README
- [ ] Create CONTRIBUTING.md with dev setup
- [ ] Document where each file type lives

---

## Next Steps

1. Run audit scripts (below)
2. Establish GitHub as source of truth for code
3. Reorganize both machines
4. Test sync workflow
5. THEN resume Phase 3B work

