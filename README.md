# Layered BERT Architecture for Poetry Analysis

**ONE Integrated Layered Model: Historical BERTs → Poetry Specialization → Prosodic Conditioning → Classification**

> 📖 **For Claude**: Read `claude_context/START_HERE.md` first - complete architecture overview
> 📐 **Full Details**: See `claude_context/ARCHITECTURE_CORRECT.md`
> ⚠️ **AVOID**: `docs/COMPLETE_MODEL_PLAN.md` is outdated and incorrect

---

## 🎯 Current Focus: Shakespeare Sonnets Trajectory Tortuosity Analysis

### What We're Doing
Analyzing semantic complexity in Shakespeare's 154 sonnets using a novel three-layer BERT architecture with trajectory tortuosity as our core metric.

**Trajectory Tortuosity** = `Σ(angular_deviations) / euclidean_distance`

Higher tortuosity = more semantic "turns" = greater complexity/density through embedding space

### Current Results (November 2025)

| Model | Mean Tortuosity | SD | Change from Base |
|-------|----------------|----|--------------------|
| **Base BERT** | 3.17 | 0.42 | baseline |
| **EEBO-BERT** (Layer 1) | 3.45 | 0.36 | **+8.8%** |
| **Poetry-BERT** (Layer 2*) | 3.59 | 0.35 | **+13.2%** |

*Poetry-BERT currently trained from base, not EEBO (needs retraining)

#### Layer 3: Prosodic Conditioning Effects

| Model | Semantic Only | +Prosody | Effect |
|-------|--------------|----------|---------|
| Base BERT | 3.17 | 3.10 | **-2.00%** |
| EEBO-BERT | 3.45 | 3.37 | **-2.35%** |
| Poetry-BERT | 3.59 | 3.50 | **-2.53%** |

**Key Finding**: Prosodic constraints (meter, rhyme) consistently reduce semantic complexity, suggesting **form acts as a semantic constraint**.

### Current Task 🚀
**NEW ARCHITECTURE: Hierarchical Multi-Objective BERT**

We're now implementing a novel hierarchical approach that trains on multiple objectives simultaneously:

```
Combined Loss = 0.5 × MLM + 0.2 × Line + 0.2 × Quatrain + 0.1 × Sonnet

where:
- MLM: Masked Language Modeling (token level)
- Line: Contrastive learning on line pairs (adjacent/rhyming vs random)
- Quatrain: Contrastive learning on quatrain structure
- Sonnet: Contrastive learning on whole-sonnet representations
```

**Status**: ✅ Implementation complete (CLI)
**Training Platform**: Claude Code on web (GPU compute) or Google Colab Pro
**Dataset**: Shakespeare's 154 sonnets (139 train, 15 val)
**Duration**: ~6-8 hours
**Innovation**: First poetry model with explicit hierarchical structure learning

**Why This Matters**: Standard fine-tuning only learns at the token level. This hierarchical approach explicitly trains the model to understand poetic structure at multiple scales, potentially capturing more nuanced semantic relationships than previous approaches.

---

## Hierarchical Multi-Objective Architecture (NEW)

```
EEBO-BERT (Layer 1 - historical semantics)
    ↓ Fine-tune with hierarchical multi-objective losses
Poetry-EEBO-Hierarchical-BERT (Layer 2 - NEW APPROACH)
    |
    |── Token Level (0.5 weight): Masked Language Modeling
    |── Line Level (0.2 weight): Contrastive learning on line pairs
    |     • Positive pairs: adjacent lines, rhyming lines
    |     • Negative pairs: random non-related lines
    |── Quatrain Level (0.2 weight): Contrastive learning on quatrain structure
    |     • Positive pairs: lines from same quatrain
    |     • Negative pairs: lines from different quatrains
    └── Sonnet Level (0.1 weight): Contrastive learning on whole-sonnet representations
          • Positive: sonnet vs itself
          • Negative: sonnet vs other sonnets in batch

    ↓ Optional: Concatenate prosodic features (Layer 3)
+Prosody: meter deviation, rhyme pairs, position, couplet marking
```

### Implementation Status

✅ **Data Preparation**: 139 train sonnets + 15 val sonnets with hierarchical annotations
✅ **Dataset Class**: `HierarchicalPoetryDataset` with multi-level sampling
✅ **Loss Functions**: `HierarchicalLoss` with InfoNCE contrastive learning
✅ **Custom Trainer**: `HierarchicalTrainer` extending HuggingFace Trainer
✅ **Training Scripts**: CLI script + Colab notebook
⏳ **Training**: Ready to start (6-8 hours on GPU)
⏳ **Validation**: Scripts to compare with baseline models

## Previous Three-Layer Architecture (Baseline)

```
Base BERT (general modern English)
    ↓ Fine-tune on EEBO 1595-1700
Layer 1: EEBO-BERT (historical semantics) ✓
    ↓ Fine-tune on 17.7M poetry lines
Layer 2: Poetry-BERT (poetry specialization) ✓
    ↓ Concatenate prosodic features
Layer 3: +Prosody (meter, rhyme, position, couplet) ✓
```

### Layer 1: Historical Semantics (EEBO-BERT)
- **Base**: bert-base-uncased
- **Training**: Early English Books Online (1595-1700)
- **Purpose**: Capture historical semantics
- **Location**: `GoogleDrive/.../EEBO_1595-1700/eebo_bert_finetuned`
- **Status**: ✅ Complete

### Layer 2: Poetry Specialization
- **Current (Poetry-BERT)**: Trained from base ⚠️ Wrong path
- **Target (Poetry-EEBO-BERT)**: Train FROM EEBO-BERT ⏳ Tonight
- **Training Data**: 17.7M lines of poetry
- **Purpose**: Learn poetic conventions while preserving historical semantics
- **Location**: `Data/poetry_unified.db`

### Layer 3: Prosodic Conditioning
- **Method**: Post-hoc feature concatenation (768 BERT + 4 prosody = 772 dims)
- **Features**:
  1. Metrical deviation from iambic pentameter
  2. Rhyme pair detection (ABAB CDCD EFEF GG)
  3. Position in sonnet (normalized 0-1)
  4. Couplet marking (binary)
- **Implementation**: `scripts/layer3_bert_prosody.py`
- **Status**: ✅ Complete

---

## Publication Strategy 📝

### Paper 1: Digital Humanities (6 months)
**Target**: Digital Scholarship in the Humanities / Journal of Cultural Analytics
- **Contribution**: Novel methodology (trajectory tortuosity for poetry)
- **Corpus**: Shakespeare's 154 sonnets
- **Findings**: Specialization effects, form-semantics interaction
- **Status**: Ready to write after tonight's training
- **Timeline**:
  - Draft: 2-3 weeks
  - Submit: December 2025
  - Publication: Mid 2026

### Paper 2: Poetics/Literary Theory (12 months)
**Target**: Poetics Today / New Literary History / Modern Philology
- **Contribution**: Deep literary interpretation + complete architecture
- **Corpus**: Shakespeare + contemporaries (Donne, Spenser, Sidney)
- **Findings**: Historical semantics, formal evolution, authorship patterns
- **Additional Work Needed**:
  - Temporal analysis (early vs late sonnets)
  - Comparison poets
  - Engagement with critical tradition
  - Close reading of high-variance sonnets
- **Timeline**: Submit Q2 2026

### Paper 3: Computational / Cognitive Science (18 months)
**Target**: ACL / CogSci / Computational Linguistics
- **Contribution**: Theoretical framework for layered specialization
- **Corpus**: Broad corpus across periods, genres, authors
- **Findings**: How architecture choices affect semantic representations
- **Additional Work Needed**:
  - Broader corpus
  - Statistical significance testing
  - Comparison with baseline methods
  - Human evaluation
  - Ablation studies
- **Timeline**: Submit Q3-Q4 2026

---

## Project Structure

```
AI Project/
├── README.md (this file)
├── RESEARCH_PLAN.md                        # Multi-paper strategy
├── SHAKESPEARE_PROJECT.md                  # Detailed Shakespeare documentation
│
├── training/                                # NEW: Hierarchical training modules
│   ├── hierarchical_dataset.py             # PyTorch Dataset with multi-level sampling
│   ├── hierarchical_losses.py              # InfoNCE contrastive losses (4 levels)
│   └── hierarchical_trainer.py             # Custom HuggingFace Trainer
│
├── scripts/
│   ├── prepare_hierarchical_training_data.py   # Extract sonnets with hierarchical structure
│   ├── train_hierarchical_bert.py          # CLI training script
│   ├── layer3_bert_prosody.py              # Prosodic conditioning analysis
│   └── (other analysis scripts)
│
├── notebooks/
│   ├── hierarchical_bert_training_colab.ipynb  # NEW: Colab training notebook
│   ├── complete_layered_analysis.ipynb     # Main analysis (all visualizations)
│   └── shakespeare_sonnets_bert_analysis.ipynb
│
├── corpus_samples/
│   └── shakespeare_sonnets_parsed.jsonl    # 154 sonnets
│
├── Data/
│   ├── eebo_sonnets_hierarchical_train.jsonl   # NEW: 139 sonnets with annotations
│   ├── eebo_sonnets_hierarchical_val.jsonl     # NEW: 15 sonnets with annotations
│   ├── eebo_sonnets_hierarchical_stats.json    # Dataset statistics
│   └── poetry_unified.db                   # 17.7M lines poetry corpus
│
├── results/
│   ├── shakespeare_sonnets_eebo_bert_contextual.csv
│   ├── shakespeare_sonnets_poetry_bert_contextual.csv
│   ├── shakespeare_sonnets_layer3_base_bert.csv
│   ├── shakespeare_sonnets_layer3_eebo_bert.csv
│   ├── shakespeare_sonnets_layer3_poetry_bert.csv
│   └── eebo_vs_poetry_bert_contextual_comparison.csv
│
└── models/                                  # Trained model checkpoints
    └── poetry_eebo_hierarchical_bert/      # NEW: Hierarchical model (to be trained)
```

---

## Key Findings So Far

### 1. **Specialization Matters**
- Historical training (EEBO): +8.8% complexity
- Poetry training: +13.2% complexity
- Both significantly increase semantic density vs. base BERT
- **Implication**: Modern language models "smooth over" historical/poetic nuances

### 2. **Form Constrains Semantics**
- Prosodic conditioning reduces complexity -2.0% to -2.5%
- Effect consistent across ALL models
- **Implication**: Meter and rhyme guide semantic choices, creating smoother trajectories
- **Supports**: Theories of form as semantic constraint (not just decoration)

### 3. **Complementary Information**
- EEBO-BERT vs Poetry-BERT correlation: r=0.630 (moderate)
- They agree on some sonnets, disagree on others
- **Implication**: Historical semantics and poetic conventions capture different aspects
- **Key**: They're not redundant - both layers add unique information

### 4. **Non-Linear Effects**
- Effects don't add linearly
- Interactions between layers are complex
- **Need**: Proper Layer 1 → Layer 2 architecture to test true interactions
- **Tonight's training will reveal**: Does poetry specialization preserve or modify historical semantics?

---

## Analysis Capabilities

`notebooks/complete_layered_analysis.ipynb` provides:

1. **Model Comparison**: All 3 models (base, EEBO, poetry) with/without prosody
2. **Statistical Summary**: Means, SDs, correlations, significance tests
3. **Visualizations**:
   - Distribution comparisons
   - Scatter plots (model agreement)
   - Temporal patterns across sonnet sequence
4. **Couplet Analysis**: Interactive Plotly visualization (which couplets are more complex?)
5. **Scansion Explorer** (in progress):
   - All metrical variants for lines
   - Hand-scansion notation (bold stress, | foot boundaries)
   - Corpus-wide metrical statistics
6. **Key Findings**: Complete results summary

---

## Running the Analysis

### Quick Start
```bash
cd "/Users/justin/Repos/AI Project"
jupyter notebook notebooks/complete_layered_analysis.ipynb
```

### Re-run Layer 3 Analysis
```bash
python scripts/layer3_bert_prosody.py --model base
python scripts/layer3_bert_prosody.py --model eebo
python scripts/layer3_bert_prosody.py --model poetry
```

### Train Poetry-EEBO-BERT (Tonight)
1. Upload `notebooks/poetry_eebo_bert_training.ipynb` to Google Colab
2. Request A100 GPU runtime
3. Mount Google Drive
4. Run all cells (~6-8 hours)
5. Model saves to: `GoogleDrive/.../poetry_eebo_bert_trained`

---

## Next Steps

### Immediate (This Week)
- [ ] **Tonight**: Train Poetry-EEBO-BERT on Colab
- [ ] Run Layer 3 on Poetry-EEBO-BERT
- [ ] Compare layered vs independent architecture paths
- [ ] Fix scansion display functions
- [ ] Statistical significance tests (paired t-tests)

### Short-term (This Month)
- [ ] Write DH paper draft (Paper 1)
- [ ] Analyze high-variance sonnets (46, 75, 151, 144) - why do models disagree?
- [ ] Temporal analysis (early vs late sonnets in sequence)
- [ ] Literary interpretation of findings

### Medium-term (Next 3 Months)
- [ ] Expand corpus: Donne, Spenser, Sidney
- [ ] Form variation analysis (different meters)
- [ ] Correlation with literary criticism
- [ ] Prepare Paper 2 (literary venue)

### Long-term (6+ Months)
- [ ] Broad corpus across periods/genres
- [ ] Theoretical framework paper
- [ ] Ablation studies
- [ ] Human evaluation
- [ ] Prepare Paper 3 (ACL/CogSci)

---

## Requirements

### Python Environment
```bash
pip install torch transformers pandas numpy matplotlib seaborn tqdm prosodic plotly jupyter
```

### Hardware
- **Local inference**: Apple Silicon MPS (M1/M2/M3) or CUDA GPU
- **Training**: Google Colab with A100 GPU (free tier sufficient)

### Data Locations
- **EEBO-BERT**: `/Users/justin/Library/CloudStorage/GoogleDrive-.../EEBO_1595-1700/eebo_bert_finetuned`
- **Poetry-BERT**: `/Users/justin/Library/CloudStorage/GoogleDrive-.../poetry_bert_trained`
- **Sonnets**: `corpus_samples/shakespeare_sonnets_parsed.jsonl`
- **Poetry Corpus**: `Data/poetry_unified.db` (17.7M lines)

---

## Citation (Provisional)

```bibtex
@unpublished{stecher2025layered,
  title={Layered BERT Architecture for Semantic Complexity Analysis in Early Modern Poetry},
  author={Stecher, Justin},
  year={2025},
  note={In preparation}
}
```

---

## Contact

Justin Stecher
Postdoc, IU Center for Possible Minds
[Your email]

---

**Last Updated**: November 3, 2025
**Current Status**: Training Poetry-EEBO-BERT tonight, preparing DH paper draft
