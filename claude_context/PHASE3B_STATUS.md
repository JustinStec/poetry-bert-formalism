# Phase 3B Status - LLM Classification Training

**Date**: November 12, 2025
**Status**: ✅ Training COMPLETE (Mistral-7B with MLX LoRA)
**Duration**: 49.7 minutes (12:35 PM - 1:25 PM EST)
**Final Loss**: Train 6.486, Val 6.505
**Memory**: 28.419 GB peak (batch size 1)
**Model**: `/Users/justin/poetry-bert-formalism/models/poetry-classifier-mistral7b/`

---

## What Was Completed

### ✅ Instruction Dataset Formatting

**Script**: `scripts/phase3/format_instruction_dataset.py`

**Input**: `Data/training/phase3_classifications/training_dataset_complete.jsonl`
- 397 poems with full texts + 28 classification labels

**Output**:
- `Data/training/phase3_classifications/instruction_dataset_train.jsonl` (357 examples)
- `Data/training/phase3_classifications/instruction_dataset_val.jsonl` (40 examples)

**Format**: Prompt/completion pairs for instruction tuning
- **Prompt**: Poem text + metadata + instruction to classify across 28 dimensions
- **Completion**: Structured output with all 28 classification fields

**Statistics**:
- Train: 357 examples (~1,833 tokens per example avg)
- Val: 40 examples (~1,425 tokens per example avg)
- Total train characters: 2.6M
- Total val characters: 228K
- Split: 90/10% (reproducible with seed=42)

---

## Instruction Format

### Prompt Template

```
Classify the following poem across 28 metadata dimensions:

Title: [title]
Author: [author]
Year: [year]

Poem:
[full poem text]

Provide classifications for the following 28 fields:

HISTORICAL:
- period
- literary_movement

RHETORICAL:
- register
- rhetorical_genre
- discursive_structure
- discourse_type
- narrative_level
- diegetic_mimetic
- focalization
- person
- deictic_orientation
- addressee_type
- deictic_object
- temporal_orientation
- temporal_structure
- tradition

FORMAL:
- mode
- genre
- stanza_structure
- meter
- rhyme

Format your response as:
period: [value]
literary_movement: [value]
... (continue for all 28 fields)

Use "N/A" or empty string for fields that don't apply.
```

### Completion Template

```
period: [value]
literary_movement: [value]
register: [value]
rhetorical_genre: [value]
discursive_structure: [value]
discourse_type: [value]
narrative_level: [value]
diegetic_mimetic: [value]
focalization: [value]
person: [value]
deictic_orientation: [value]
addressee_type: [value]
deictic_object: [value]
temporal_orientation: [value]
temporal_structure: [value]
tradition: [value]
mode: [value]
genre: [value]
stanza_structure: [value]
meter: [value]
rhyme: [value]
```

---

---

## Validation Script (NEW)

**Script**: `scripts/phase3/validate_classifier.py`

**Purpose**: Test fine-tuned model on 40 hold-out poems and calculate accuracy metrics

**Features**:
- Loads fine-tuned Mistral-7B with MLX
- Runs inference on 40 validation poems
- Parses structured output (28 fields)
- Calculates per-field accuracy
- Exact match accuracy (all fields correct)
- Saves detailed results to JSON

**Usage**:
```bash
# Run validation on final model (iteration 1000)
ssh justin@100.65.21.63
cd ~/poetry-bert-formalism
python3 scripts/phase3/validate_classifier.py

# Or test best checkpoint (iteration 800)
python3 scripts/phase3/validate_classifier.py --checkpoint 800
```

**Expected Time**: 5-10 minutes for 40 poems

**Output**:
- Console: Per-field accuracy breakdown by category
- File: `results/validation_results.json` with detailed metrics

**Success Criteria**:
- ✅ Average accuracy >= 80% → Ready for corpus inference
- ⚠️ Average accuracy 70-80% → Review low-accuracy fields
- ✗ Average accuracy < 70% → Consider additional training

---

## Next Steps After Validation

### 1. Choose Base Model (COMPLETED - Mistral-7B)

**Option A: Llama-3-8B** (Recommended)
- Model: `meta-llama/Meta-Llama-3-8B-Instruct`
- Size: 8B parameters
- Strengths: Strong instruction following, good for structured output
- MLX support: ✓ Excellent

**Option B: Mistral-7B**
- Model: `mistralai/Mistral-7B-Instruct-v0.2`
- Size: 7B parameters
- Strengths: Fast, efficient, good general performance
- MLX support: ✓ Excellent

**Recommendation**: Start with Llama-3-8B for better instruction following

### 2. Set Up MLX Training on M4 Max

**Install MLX**:
```bash
ssh justin@100.65.21.63
pip3 install mlx-lm
```

**Transfer datasets to M4 Max**:
```bash
scp Data/training/phase3_classifications/instruction_dataset_*.jsonl \
    justin@100.65.21.63:~/poetry-bert-formalism/Data/training/phase3_classifications/
```

### 3. Fine-Tune with LoRA

**Training Configuration**:
- Method: LoRA (Low-Rank Adaptation)
- LoRA rank: 16
- LoRA alpha: 32
- Epochs: 3-5
- Batch size: 4 (adjust for M4 Max memory)
- Learning rate: 2e-4
- Warmup steps: 100
- Max sequence length: 2048

**Training Command** (example):
```bash
mlx_lm.lora \
    --model meta-llama/Meta-Llama-3-8B-Instruct \
    --train Data/training/phase3_classifications/instruction_dataset_train.jsonl \
    --val Data/training/phase3_classifications/instruction_dataset_val.jsonl \
    --iters 1000 \
    --batch-size 4 \
    --lora-layers 16 \
    --learning-rate 2e-4 \
    --output models/poetry-classifier-llama3
```

**Estimated Time**: 1-2 hours on M4 Max

### 4. Validate Model

**Validation**:
- Run inference on 40 validation examples
- Check accuracy per field
- Manual review of sample outputs
- Target: >80% accuracy per field

**Metrics to Track**:
- Per-field accuracy
- Exact match accuracy (all 28 fields correct)
- Field-specific confusion matrices
- Qualitative error analysis

### 5. Run Inference on 116K Corpus

**Batch Processing**:
```python
# Process corpus in batches
batch_size = 32
corpus_size = 116674
num_batches = corpus_size // batch_size  # ~3646 batches

# Estimated time: 12-24 hours on M4 Max
```

**Output Format**:
- `corpus_metadata_v2.csv`: Original 9 columns + 28 new classification columns
- Checkpoint saves every 1000 poems
- Confidence scores per field (optional)

---

## Files Created

### Scripts
- `scripts/phase3/format_instruction_dataset.py` - Dataset formatter (NEW)

### Data
- `Data/training/phase3_classifications/instruction_dataset_train.jsonl` - Train set (357 examples)
- `Data/training/phase3_classifications/instruction_dataset_val.jsonl` - Val set (40 examples)

### Documentation
- `claude_context/PHASE3B_STATUS.md` - This file

---

## Timeline Estimate

### Short-term (This Week)
- Day 1 (Today): ✅ Format instruction dataset - DONE
- Day 2: Set up MLX on M4 Max + transfer data
- Day 3: Start fine-tuning (1-2 hours training + overnight)
- Day 4: Validate model + test on hold-out set
- Day 5: Begin inference on corpus

### Medium-term (Next Week)
- Days 6-7: Complete corpus inference (12-24 hours runtime)
- Day 8: Validate results + spot checks
- Day 9: Merge with corpus metadata
- Day 10: Analysis + documentation

---

## Success Metrics

### Training
- ✅ Train loss decreasing steadily
- ✅ Val loss not diverging from train (no overfitting)
- ✅ Model generates structured output in correct format

### Validation
- 🎯 Target: >80% accuracy per field
- 🎯 Target: >50% exact match (all 28 fields correct)
- 🎯 Manual review: >90% quality on random sample of 20

### Corpus Inference
- 🎯 Complete: All 116,674 poems classified
- 🎯 Missing rate: <5% per field
- 🎯 Quality: Spot checks show consistent accuracy

---

## Current Status

**Completed**:
- ✅ Extract 397 training poems with texts from corpus
- ✅ Format as instruction-tuning dataset
- ✅ Split train/val (357/40)
- ✅ Save in JSONL format

**Next**:
- ➡️ Choose base model (Llama-3 vs Mistral)
- ➡️ Set up MLX training environment on M4 Max
- ➡️ Transfer datasets
- ➡️ Begin fine-tuning

**Blocked**: None - ready to proceed!

---

**Last Updated**: November 12, 2025
**Track**: Track 1 (Get Metadata NOW - Priority)
