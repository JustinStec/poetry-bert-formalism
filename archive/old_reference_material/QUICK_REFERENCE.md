# Quick Reference Card

Keep this handy while working!

---

## Starting Jupyter

```bash
cd "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development"
jupyter notebook
```

---

## Jupyter Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Run cell and advance | `Shift + Enter` |
| Run cell in place | `Ctrl + Enter` |
| Insert cell above | `A` |
| Insert cell below | `B` |
| Delete cell | `D D` (press D twice) |
| Undo delete | `Z` |
| Change to Markdown | `M` |
| Change to Code | `Y` |
| Save notebook | `Cmd + S` |
| Show all shortcuts | `H` |

**Note**: These shortcuts work when you're NOT editing a cell (press `Esc` first)

---

## Common Commands

### Check Python version
```bash
python3 --version
```

### Check installed packages
```bash
pip3 list
```

### Check specific package
```bash
pip3 show jupyter
```

### Stop Jupyter
1. Go to Terminal
2. Press `Ctrl + C`
3. Type `y` and press Enter

---

## Project Structure

```
Project Development/
├── Oread_Trajectory_Analysis.ipynb     ← Run this!
├── README_SETUP.md                     ← Detailed setup instructions
├── SETUP_CHECKLIST.md                  ← Track your progress
├── requirements.txt                    ← Package list
├── code/
│   └── trajectory_metrics.py           ← Metric functions
├── corpus_texts/                       ← 52 poems (txt files)
├── Metadata/
│   └── corpus_metadata/                ← 4 CSV tables
└── Methodology/
    └── methods_log.md                  ← Documentation
```

---

## Output Files (After Running Notebook)

- `oread_trajectory_results.json` - All metrics and metadata
- `oread_embeddings.npz` - Saved embeddings for later use

---

## Expected Runtime

| Task | Time |
|------|------|
| Install packages | 2-5 minutes |
| Download Word2Vec (first time only) | 5-10 minutes |
| Extract embeddings | < 1 second |
| Calculate metrics | < 1 second |
| Generate plots | 1-2 seconds |
| **Total (first run)** | **~10-15 minutes** |
| **Total (subsequent runs)** | **< 1 minute** |

---

## Key Metrics (What They Mean)

| Metric | Symbol | What It Measures | Interpretation |
|--------|--------|------------------|----------------|
| Semantic Path Length | SPL | Total distance traveled | Higher = more exploration |
| Net Displacement | NSD | Start-to-end distance | Lower = circular structure |
| Tortuosity | T | SPL / NSD | **Key metric:** High = winding path (HIGH DISPERSION + HIGH INTEGRATION) |
| Exploration Radius | ER | Average distance from center | Higher = spanning diverse domains |
| Velocity Variance | VPV | Variation in step sizes | Shows pacing (fast vs. slow shifts) |
| Directional Consistency | DC | Path coherence | Higher = straighter path |

**Hypothesis**: Real poetry has HIGH tortuosity (winding path through diverse semantic regions while maintaining coherence)

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Jupyter won't start | Try `python3 -m jupyter notebook` |
| Package import error | Restart kernel: `Kernel → Restart` |
| Browser doesn't open | Copy URL from Terminal to browser |
| Cell won't run | Check if previous cells ran successfully |
| Plot doesn't appear | Run cell again, or try `%matplotlib inline` |
| Out of memory | Close other apps, restart Jupyter |

---

## Next Steps After Oread

1. **Adapt for full corpus**: Loop through all 52 poems in `corpus_texts/`
2. **Batch processing**: Save all results to a master CSV
3. **LLM generation**: Create comparison poems
4. **Statistical tests**: Compare distributions (real vs. LLM vs. prose)
5. **Visualize results**: Create publication-quality figures

---

## Getting More Help

- **Jupyter Docs**: https://jupyter.org/documentation
- **Matplotlib Gallery**: https://matplotlib.org/stable/gallery/
- **NumPy Docs**: https://numpy.org/doc/
- **Gensim Word2Vec**: https://radimrehurek.com/gensim/models/word2vec.html

---

## Contact Info (For Your Reference)

Project: Poetry Trajectory Analysis
Target Journal: Cognitive Science
Hypothesis: HIGH DISPERSION + HIGH INTEGRATION in real poetry

---

**Last Updated**: 2025-01-27
