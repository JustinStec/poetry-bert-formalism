# Pragmatic Workflow - What We're Actually Doing

**Date**: November 12, 2025
**Status**: Active workflow

---

## The Two-Track Approach

We have TWO parallel tracks that eventually converge:

### Track 1: Get Rich Metadata NOW (Phase 3B) - CURRENT PRIORITY

**Goal**: Classify all 116K HEPC poems with 28-dimension metadata using a simple fine-tuned LLM

**Why**:
- The full layered BERT will take months (need HathiTrust corpora)
- We need the rich metadata to make the corpus useful NOW
- When the full model is ready, we'll have richly-annotated data

**Workflow**:
```
397 Training Poems (✅ Complete)
    ↓
Format as instruction-tuning dataset
    ↓
Fine-tune Llama-3-8B or Mistral-7B (LoRA on M4 Max)
    ↓
Run inference on 116K HEPC corpus
    ↓
OUTPUT: corpus_metadata_v2.csv (37 columns: 9 existing + 28 new)
```

**Timeline**: ~1 week
- Day 1: Format dataset
- Day 2-3: Fine-tune LLM (1-2 hours training)
- Day 4-5: Run inference (12-24 hours)
- Day 6: Validate results

**Status**: Ready to start - all training data prepared

---

### Track 2: Build Complete Layered BERT (Long-term)

**Goal**: Build the full integrated architecture for deep historical poetry analysis

**Workflow**:
```
Layer 1: Train 4 Historical BERTs
├── EEBO-BERT (1595-1700) ✅ Complete
├── ECCO-BERT (1700-1800) ❌ Need HathiTrust
├── NCCO-BERT (1800-1900) ❌ Need HathiTrust
└── Modern-BERT (1900-2000) ❌ Need HathiTrust
    ↓ Merge
Layer 2: Poetry-Historical-BERT (hierarchical multi-objective)
    ↓ Add prosodic features
Layer 3: Prosody Conditioning
    ↓ Fine-tune
Classification Head (or just use for analysis)
```

**Timeline**: Months (blocked on HathiTrust access)

**Status**:
- EEBO-BERT ready (418MB in Google Drive)
- Implementation code complete
- Blocked on acquiring corpora

---

## How They Connect

1. **Now**: Use simple LLM to get metadata → classify 116K corpus
2. **Later**: Train complete layered BERT → use richly-annotated corpus for analysis
3. **Result**: Full model + rich corpus = powerful diachronic formal analysis

**The metadata from Track 1 makes Track 2's output more valuable.**

---

## Current Status

### What's Complete
- ✅ 397 training poems with 28 labels
- ✅ HEPC corpus (116K poems)
- ✅ EEBO-BERT (Layer 1, period 1)
- ✅ Layer 2 implementation code
- ✅ HuggingFace login (username: jts3et, not justinstec)
- ✅ Token stored: ~/.cache/claude_hf/token

### What's Next (Track 1 - Priority)
1. Format 397 poems as instruction-tuning dataset
2. Fine-tune Llama-3-8B or Mistral-7B with LoRA on M4 Max
3. Run inference on 116K corpus
4. Validate and save enriched metadata

### What's Blocked (Track 2 - Long-term)
1. Need HathiTrust access for 18th-20th century corpora
2. Need to collect 17.7M poetry lines
3. Need to train Layers 2-3

---

## Key Insight

**Phase 3B is NOT a replacement for the layered architecture** - it's a pragmatic intermediate step to get useful metadata while we build the full model.

Think of it as:
- **Track 1**: Quick & practical (weeks) - Get metadata with simple LLM
- **Track 2**: Deep & rigorous (months) - Build specialized historical poetry model

Both are valuable, both are needed.

---

## HuggingFace Status

- **Username**: `jts3et` (NOT justinstec - that was wrong in docs)
- **Token**: Stored in `~/.cache/claude_hf/token` (Claude-specific)
- **Models uploaded**: None yet (0 models found)
- **Action needed**: Upload EEBO-BERT from Google Drive

---

## Next Steps

**Immediate (Today/Tomorrow)**:
1. ✅ HuggingFace login - DONE
2. Create instruction-tuning dataset formatter
3. Set up MLX training on M4 Max
4. Choose base model (Llama-3-8B vs Mistral-7B)

**This Week**:
5. Train classification LLM
6. Validate on hold-out set
7. Run inference on full corpus

**Later**:
8. Pursue HathiTrust access
9. Continue Track 2 (layered BERT)
10. Integrate when ready

---

**Last Updated**: November 12, 2025
**Current Track**: Track 1 (Phase 3B classification)
