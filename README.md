# Layered BERT Architecture for Poetry Analysis

**Three-Layer Model for Semantic Complexity in Early Modern Poetry**

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

### Tonight's Task 🚀
**Train Poetry-EEBO-BERT** (proper Layer 1 → Layer 2 architecture)
- Notebook: `notebooks/poetry_eebo_bert_training.ipynb`
- Platform: Google Colab (A100)
- Duration: ~6-8 hours
- Why: Test if poetry specialization preserves or modifies historical semantics

---

## Three-Layer Architecture

```
Base BERT (general modern English)
    ↓ Fine-tune on EEBO 1595-1700
Layer 1: EEBO-BERT (historical semantics) ✓
    ↓ Fine-tune on 17.7M poetry lines
Layer 2: Poetry-EEBO-BERT (poetry + historical) ⏳ TRAINING TONIGHT
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
├── notebooks/
│   ├── complete_layered_analysis.ipynb     # Main analysis (all visualizations)
│   ├── shakespeare_sonnets_bert_analysis.ipynb
│   └── poetry_eebo_bert_training.ipynb     # Colab training (TONIGHT)
│
├── scripts/
│   ├── layer3_bert_prosody.py              # Prosodic conditioning analysis
│   └── (other analysis scripts)
│
├── corpus_samples/
│   └── shakespeare_sonnets_parsed.jsonl    # 154 sonnets
│
├── results/
│   ├── shakespeare_sonnets_eebo_bert_contextual.csv
│   ├── shakespeare_sonnets_poetry_bert_contextual.csv
│   ├── shakespeare_sonnets_layer3_base_bert.csv
│   ├── shakespeare_sonnets_layer3_eebo_bert.csv
│   ├── shakespeare_sonnets_layer3_poetry_bert.csv
│   └── eebo_vs_poetry_bert_contextual_comparison.csv
│
└── Data/
    └── poetry_unified.db                   # 17.7M lines poetry corpus
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
