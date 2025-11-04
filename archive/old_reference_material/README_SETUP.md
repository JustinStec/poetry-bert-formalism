# Setup Guide: Poetry Trajectory Analysis

This guide will walk you through setting up Jupyter Notebook locally to run the trajectory analysis.

## Prerequisites

You need Python 3 installed on your Mac. Let's check:

```bash
python3 --version
```

If you see something like `Python 3.x.x`, you're good to go! If not, install Python from [python.org](https://www.python.org/downloads/).

---

## Step-by-Step Setup

### Step 1: Open Terminal

1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal" and press Enter

### Step 2: Navigate to Project Directory

Copy and paste this command into Terminal:

```bash
cd "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development"
```

Press Enter. This takes you to your project folder.

### Step 3: Install Required Packages

Copy and paste this command:

```bash
pip3 install -r requirements.txt
```

Press Enter. This will install:
- **Jupyter Notebook** (the environment to run analyses)
- **NumPy** (numerical computing)
- **Gensim** (Word2Vec embeddings)
- **Matplotlib** (plotting)
- **Scikit-learn** (PCA dimensionality reduction)
- And a few other helpful packages

**Note**: This may take 2-5 minutes. You'll see progress bars and installation messages.

### Step 4: Verify Installation

Check that Jupyter is installed:

```bash
jupyter notebook --version
```

You should see a version number like `7.0.0` or similar.

### Step 5: Launch Jupyter Notebook

Start Jupyter:

```bash
jupyter notebook
```

**What happens next:**
1. Your web browser will automatically open
2. You'll see a file browser showing your project directory
3. Look for `Oread_Trajectory_Analysis.ipynb` and click it

**Important**: Keep the Terminal window open while you work! Closing it will stop Jupyter.

---

## Running the Analysis

Once the notebook opens in your browser:

1. **Run cells sequentially**: Click inside the first cell and press `Shift + Enter`
2. **Cell 1**: Installs gensim (may take a minute)
3. **Cell 2**: Imports packages
4. **Cell 3**: Downloads Word2Vec model (THIS WILL TAKE 5-10 MINUTES the first time - it's a 1.5GB file!)
5. **Continue**: Keep pressing `Shift + Enter` to run each cell

**Pro tip**: You can also click `Cell → Run All` in the menu to run everything at once.

---

## Understanding What You're Seeing

### Cell Types

- **Code cells**: Have `In [ ]:` next to them, contain Python code
- **Markdown cells**: Plain text explanations (like this README)
- **Output**: Results appear below code cells (numbers, plots, tables)

### Expected Outputs

- **Metrics report**: A table showing SPL, NSD, Tortuosity, etc.
- **2D plot**: A trajectory visualization with arrows showing semantic path
- **3D plot**: A rotatable 3D view of the trajectory
- **Velocity profile**: A bar chart showing step-by-step semantic changes
- **Exported files**: `oread_trajectory_results.json` and `oread_embeddings.npz`

---

## Common Issues and Solutions

### Issue 1: "Command not found: pip3"

Try using `pip` instead of `pip3`:

```bash
pip install -r requirements.txt
```

### Issue 2: "Permission denied" when installing

Use `--user` flag:

```bash
pip3 install --user -r requirements.txt
```

### Issue 3: Word2Vec download is slow

This is normal! The model is 1.5GB. It only downloads once, then it's cached.

You can check progress in the notebook output. Be patient.

### Issue 4: Browser doesn't open automatically

If Jupyter starts but your browser doesn't open, look at the Terminal output. You'll see something like:

```
http://localhost:8888/?token=abc123...
```

Copy that URL and paste it into your web browser.

### Issue 5: Kernel keeps dying or restarting

Your computer might be running low on memory. Try:
1. Close other applications
2. Restart Jupyter: Press `Ctrl + C` in Terminal, then run `jupyter notebook` again

---

## Stopping Jupyter

When you're done:

1. Save your notebook: `File → Save and Checkpoint`
2. Close the browser tab
3. Go back to Terminal
4. Press `Ctrl + C` (this stops the Jupyter server)
5. Type `y` and press Enter to confirm

---

## Next Steps After Oread Analysis

Once you've successfully analyzed Oread:

1. **Scale to full corpus**: Modify notebook to loop through all 52 poems in `corpus_texts/`
2. **Generate LLM poems**: Create comparison poems using GPT or Claude
3. **Statistical comparison**: Compare real vs. LLM vs. prose trajectories
4. **Write paper**: Export results and create visualizations for publication

---

## File Locations

After running the notebook, you'll find:

```
Project Development/
├── Oread_Trajectory_Analysis.ipynb  (the notebook you run)
├── requirements.txt                  (package list)
├── oread_trajectory_results.json     (exported metrics)
├── oread_embeddings.npz              (saved embeddings)
├── code/
│   └── trajectory_metrics.py         (metric functions)
├── corpus_texts/                     (your 52 poems)
└── Metadata/
    └── corpus_metadata/              (poem metadata tables)
```

---

## Getting Help

If you run into issues:

1. Check the error message in the notebook output
2. Google the error message (often helpful!)
3. Check that all packages installed correctly: `pip3 list | grep jupyter`
4. Try restarting Jupyter: `Ctrl + C` in Terminal, then `jupyter notebook` again

---

## Additional Resources

- **Jupyter Basics**: https://jupyter-notebook.readthedocs.io/en/stable/
- **Keyboard Shortcuts**: Press `H` in Jupyter to see all shortcuts
- **Markdown Guide**: Double-click any markdown cell to see the raw text

---

## Ready to Start?

You're all set! Here's the quick version:

```bash
# 1. Navigate to project
cd "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development"

# 2. Install packages (only need to do this once)
pip3 install -r requirements.txt

# 3. Start Jupyter
jupyter notebook

# 4. Click Oread_Trajectory_Analysis.ipynb in the browser
# 5. Press Shift + Enter to run each cell
```

Good luck! 🚀
