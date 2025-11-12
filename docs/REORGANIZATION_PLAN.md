# System Reorganization Plan

**Date**: November 12, 2025
**Status**: Ready to execute
**Priority**: CRITICAL - Do before resuming any work

---

## Summary of Findings

### ✅ Good News
1. **EEBO-BERT found** in Google Drive (418MB, complete)
2. **Both machines synced** to GitHub
3. **397 training poems extracted** successfully today
4. **GitHub username**: JustinStec
5. **HuggingFace username**: justinstec

### ❌ Problems
1. **poetry-bert** and **poetry-eebo-bert** corrupted (archives were bad)
2. **Directory chaos** on M4 Max ("poetry_platform_renamed", inconsistent naming)
3. **Not logged into HuggingFace** - can't check if EEBO-BERT was uploaded
4. **Today's Phase 3 work** not committed to Git

### 📊 Model Status
| Model | Status | Location |
|-------|--------|----------|
| EEBO-BERT | ✅ Found | Google Drive (418MB) |
| Poetry-BERT | ❌ Corrupted | Delete |
| Poetry-EEBO-BERT | ❌ Corrupted | Delete |

---

## Step-by-Step Reorganization Plan

### Phase 1: Clean Up (30 minutes)

#### 1.1: Delete Corrupted Models
```bash
# On Air
cd "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry"

# Move to trash (safe)
mv poetry_bert_trained ~/.Trash/
mv poetry_eebo_hierarchical_bert ~/.Trash/

# Verify EEBO-BERT is safe
ls -lh EEBO_1595-1700/eebo_bert_finetuned/
# Should show: config.json, model.safetensors (418MB), vocab.txt
```

#### 1.2: Copy EEBO-BERT to M4 Max
```bash
# Create models directory on Max
ssh justin@100.65.21.63 "mkdir -p ~/poetry-bert-formalism/models"

# Copy EEBO-BERT
scp -r "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned" \
    justin@100.65.21.63:~/poetry-bert-formalism/models/eebo_bert

# Verify (should be 418MB)
ssh justin@100.65.21.63 "du -sh ~/poetry-bert-formalism/models/eebo_bert"
```

---

### Phase 2: Reorganize M4 Max Data/ Directory (45 minutes)

#### Current Structure (BAD)
```
Data/
├── Datasets/              # Confusing
├── metadata/              # OK
├── phase3/                # Inconsistent
├── processed/
│   └── poetry_platform_renamed/  # TERRIBLE NAME
└── raw/                   # Empty
```

#### New Structure (GOOD)
```
Data/
├── corpus/                # 116,674 contemporary poems
│   ├── texts/             # Renamed from poetry_platform_renamed
│   │   ├── Author1/
│   │   ├── Author2/
│   │   └── ...
│   ├── metadata.csv       # Moved from metadata/corpus_final_metadata.csv
│   └── statistics.txt
│
├── datasets/              # Additional text collections
│   └── shakespeare/
│       └── shakespeare_complete_works.jsonl
│
├── training/              # All training data
│   └── phase3_classifications/  # 397 poems with 28 fields
│       ├── training_set_457_poems.csv
│       ├── training_dataset_complete.jsonl
│       ├── gold_standard_52_poems.csv
│       └── README.md
│
└── archive/               # Deprecated files (keep for reference)
    ├── metadata/          # Old metadata folder
    └── old_structure/
```

#### Reorganization Script
```bash
#!/bin/bash
# Run on M4 Max
cd ~/poetry-bert-formalism/Data

# 1. Rename main corpus directory
mv processed/poetry_platform_renamed corpus/texts

# 2. Reorganize datasets
mkdir -p datasets/shakespeare
mv Datasets/shakespeare_complete_works.jsonl datasets/shakespeare/

# 3. Organize training data
mkdir -p training/phase3_classifications
mv phase3/* training/phase3_classifications/

# 4. Move corpus metadata
mv metadata/corpus_final_metadata.csv corpus/metadata.csv
mv metadata/corpus_statistics.txt corpus/statistics.txt

# 5. Archive old structure
mkdir -p archive
mv metadata archive/
mv Datasets archive/old_Datasets
rmdir processed  # Should be empty now
rmdir phase3     # Should be empty now
rmdir raw        # Empty anyway

# 6. Verify new structure
echo "New structure:"
tree -L 2 Data/
```

---

### Phase 3: Sync to Air (15 minutes)

#### 3.1: Update Air with New Structure
```bash
# On Air
cd "/Users/justin/Repos/AI Project"

# Create matching directory structure (empty, for reference)
mkdir -p Data/{corpus,datasets/shakespeare,training/phase3_classifications,archive}

# Copy small training data from Max
scp -r justin@100.65.21.63:~/poetry-bert-formalism/Data/training/phase3_classifications/*.csv \
    Data/training/phase3_classifications/

scp justin@100.65.21.63:~/poetry-bert-formalism/Data/training/phase3_classifications/training_dataset_complete.jsonl \
    Data/training/phase3_classifications/
```

#### 3.2: Update .gitignore
```bash
# Add to .gitignore
echo "
# Large corpus data (only on M4 Max)
Data/corpus/texts/
Data/corpus/metadata.csv
Data/datasets/shakespeare/

# Models (in Google Drive + HuggingFace)
models/eebo_bert/
models/poetry_bert/

# Archive
Data/archive/
" >> .gitignore
```

---

### Phase 4: Git Commit & Push (10 minutes)

```bash
# On Air
cd "/Users/justin/Repos/AI Project"

# Stage new files
git add docs/SYSTEM_AUDIT.md
git add docs/AUDIT_RESULTS.md
git add docs/REORGANIZATION_PLAN.md
git add scripts/phase3/extract_training_dataset.py
git add Data/training/phase3_classifications/

# Commit
git commit -m "Phase 3B: Extract 397 training poems + system audit

- Extracted 397 canonical poems with texts from M4 Max corpus
- Created training_dataset_complete.jsonl with all 28 classification fields
- Completed system audit (Air, Max, GitHub, HuggingFace)
- Found EEBO-BERT in Google Drive (418MB, intact)
- Identified corrupted poetry models (need retraining)
- Created reorganization plan for Data/ directory

Next: Execute reorganization, then format instruction-tuning dataset"

# Push to GitHub
git push origin main
```

---

### Phase 5: HuggingFace Setup (15 minutes)

#### 5.1: Login to HuggingFace
```bash
# Get token from https://huggingface.co/settings/tokens
hf auth login
# Enter token when prompted
# Username should be: justinstec
```

#### 5.2: Check if EEBO-BERT was uploaded
```bash
# Check your models
python3 << 'EOF'
from huggingface_hub import HfApi
api = HfApi()
models = api.list_models(author="justinstec")
print("Your HuggingFace models:")
for model in models:
    print(f"  - {model.modelId}")
EOF
```

#### 5.3: Upload EEBO-BERT if not there
```bash
# If EEBO-BERT not on HuggingFace, upload it
cd "/Users/justin/Repos/AI Project"
python scripts/archive/old_bert_scripts/upload_to_huggingface.py \
    --model eebo \
    --username justinstec
```

---

### Phase 6: Documentation (10 minutes)

#### 6.1: Create README for Training Data
```bash
# On Air
cat > Data/training/phase3_classifications/README.md << 'EOF'
# Phase 3 Classification Training Data

**397 canonical poems** with expert classifications across 28 metadata dimensions.

## Files

- `training_dataset_complete.jsonl`: Full dataset (397 poems with texts + classifications)
- `training_set_457_poems.csv`: Metadata only (457 poems, 397 matched to texts)
- `gold_standard_52_poems.csv`: Expert-classified gold standard
- `404_poems_classified.csv`: LLM-classified using few-shot prompts

## Schema

28 classification fields:
- Historical: period, literary_movement
- Rhetorical: 16 fields (register, genre, person, etc.)
- Formal: 5 fields (mode, meter, rhyme, etc.)

## Usage

For fine-tuning LLM to classify 116K corpus poems.

See: `/docs/PHASE_3_PROGRESS.md` for methodology.
EOF
```

#### 6.2: Update Main README
Add to main README:
```markdown
## Data Organization

- **Code**: `src/`, `scripts/`, `notebooks/` → Synced via GitHub
- **Corpus** (116K poems): Only on M4 Max (`Data/corpus/`)
- **Models**: Google Drive + HuggingFace
- **Training data**: Small files synced via GitHub

See `docs/SYSTEM_AUDIT.md` for details.
```

---

## Verification Checklist

After completing all phases:

### On M4 Max
- [ ] Data/ directory reorganized
- [ ] `Data/corpus/texts/` contains 116K poems
- [ ] `Data/training/phase3_classifications/` has 397-poem dataset
- [ ] `models/eebo_bert/` contains EEBO-BERT (418MB)
- [ ] Old directories moved to `archive/`

### On MacBook Air
- [ ] Directory structure matches Max (empty folders)
- [ ] Training data (small files) synced
- [ ] All today's work committed to Git
- [ ] Pushed to GitHub
- [ ] .gitignore excludes large files

### GitHub
- [ ] Latest commit shows Phase 3B work
- [ ] Repository clean (no large files tracked)
- [ ] Both machines can pull successfully

### HuggingFace
- [ ] Logged in as justinstec
- [ ] EEBO-BERT uploaded (or verified if already there)
- [ ] Can download model with transformers library

### Google Drive
- [ ] Corrupted models deleted
- [ ] EEBO-BERT safe at: `AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned/`

---

## After Reorganization: Resume Work

Once everything is reorganized, you can safely:

1. **Format instruction-tuning dataset** (Phase 3B continues)
2. **Fine-tune LLM** on 397 poems
3. **Classify 116K corpus**
4. **Retrain poetry-specific BERTs** (when ready, using clean data)

---

## Estimated Total Time

- Phase 1 (Cleanup): 30 min
- Phase 2 (Reorganize Max): 45 min
- Phase 3 (Sync Air): 15 min
- Phase 4 (Git commit): 10 min
- Phase 5 (HuggingFace): 15 min
- Phase 6 (Documentation): 10 min

**Total: ~2 hours**

Worth it to avoid future chaos!

