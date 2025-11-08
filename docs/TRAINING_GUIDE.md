# Google Colab Training Setup Guide

**Hierarchical Multi-Objective Poetry-EEBO-BERT**

This guide will walk you through training your hierarchical BERT model on Google Colab with GPU acceleration.

---

## Prerequisites

- Google account with Colab access
- Google Drive API enabled (you have this)
- HuggingFace account with token: `YOUR_HF_TOKEN_HERE`

---

## Step 1: Prepare Files on Your Local Machine

You need to upload 5 files to Colab. They're all in `/Users/justin/Repos/AI Project/`:

**Training modules (3 files):**
- `training/hierarchical_dataset.py`
- `training/hierarchical_losses.py`
- `training/hierarchical_trainer.py`

**Training data (2 files):**
- `Data/eebo_sonnets_hierarchical_train.jsonl`
- `Data/eebo_sonnets_hierarchical_val.jsonl`

**Notebook:**
- `notebooks/hierarchical_bert_training_colab.ipynb` (already updated for you)

---

## Step 2: Open Google Colab

1. Go to: https://colab.research.google.com/
2. Sign in with your Google account
3. Click **File → Upload notebook**
4. Select: `notebooks/hierarchical_bert_training_colab.ipynb`

---

## Step 3: Configure GPU Runtime

1. Click **Runtime → Change runtime type**
2. Set **Hardware accelerator** to: **GPU**
3. Choose **GPU type**:
   - **A100** (fastest, best option if available)
   - **T4** (good alternative, free tier)
4. Click **Save**
5. Click **Connect** button in top-right corner

**Verify GPU:**
After connecting, run the first cell (GPU check). You should see:
```
GPU 0: Tesla A100-SXM4-40GB
```
or
```
GPU 0: Tesla T4
```

---

## Step 4: Upload Files to Colab

In the left sidebar, click the **📁 Files** icon, then:

1. Click **Upload** button (📤 icon)
2. Upload all 5 files from Step 1

**After upload, organize them:**
Run this code in a new cell:
```python
!mkdir -p training Data
!mv hierarchical_dataset.py training/
!mv hierarchical_losses.py training/
!mv hierarchical_trainer.py training/
!mv eebo_sonnets_hierarchical_train.jsonl Data/
!mv eebo_sonnets_hierarchical_val.jsonl Data/
!ls -lh training/
!ls -lh Data/
```

You should see:
```
training/:
  hierarchical_dataset.py
  hierarchical_losses.py
  hierarchical_trainer.py

Data/:
  eebo_sonnets_hierarchical_train.jsonl
  eebo_sonnets_hierarchical_val.jsonl
```

---

## Step 5: Run Training Cells

Now execute each cell in order (Shift+Enter or click ▶️):

### Cell 1: Check GPU
```python
!nvidia-smi
```
✅ Verify you see a GPU listed

### Cell 2: Install Dependencies
```python
!pip install -q transformers datasets tensorboard --upgrade
```
⏱️ Takes ~1 minute
✅ Uses Colab's existing PyTorch 2.8.0 and NumPy 2.x (avoids binary incompatibility)

### Cell 3: HuggingFace Authentication
```python
!pip install -q huggingface_hub
from huggingface_hub import login
login(token='YOUR_HF_TOKEN_HERE')
```
✅ Should see: "✓ Authenticated with HuggingFace"

### Cell 4: Mount Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```
📁 Click the link, authenticate, paste code

### Cell 5-7: Upload Files
Already done in Step 4!

### Cell 8: Configuration
Just run it - all settings are pre-configured:
- Base model: `jts3et/eebo-bert`
- Batch size: 16 (optimized for A100)
- Epochs: 10
- Learning rate: 2e-5

### Cell 9: Import Modules
Loads the training code you uploaded

### Cell 10-11: Load Data and Model
Downloads EEBO-BERT from HuggingFace (418MB)

### Cell 12-13: Setup Training
Configures the hierarchical loss function

### Cell 14: **START TRAINING** 🚀
```python
trainer.train()
```

This is the main training loop!

**Expected duration:** 4-6 hours on A100 (batch_size=16), 8-10 hours on T4 (reduce to batch_size=8)

**What you'll see:**
```
======================================================================
STARTING TRAINING
======================================================================
Training samples: 139
Validation samples: 15
Batch size: 8
Epochs: 10
...

Epoch 1/10: [=========>          ] 45/139 batches
Total loss: 4.2156 | MLM: 3.8945 | Line: 0.1523 | Quatrain: 0.1204 | Sonnet: 0.0484
```

**All 4 loss components should decrease over time!**

---

## Step 6: Monitor Training

### Option A: Watch the Output
The cell will show progress bars and loss updates

### Option B: Use TensorBoard
Open a new cell and run:
```python
%load_ext tensorboard
%tensorboard --logdir models/poetry_eebo_hierarchical_bert/logs
```

This shows interactive loss curves in real-time!

---

## Step 7: Save Model

After training completes, run the final cells:

### Cell 15: Save to Google Drive
```python
trainer.save_model("models/poetry_eebo_hierarchical_bert/final")
# Copies to Google Drive
```

### Cell 16: View Loss Curves
Matplotlib plots of all 4 loss components

### Cell 17: Test Model
Quick sanity check that the model works

---

## Step 8: Download Trained Model

1. In Colab Files panel, navigate to:
   ```
   /content/drive/MyDrive/AI and Poetry/poetry_eebo_hierarchical_bert/
   ```

2. Or download directly from Colab:
   ```python
   !zip -r poetry_eebo_hierarchical_bert.zip models/poetry_eebo_hierarchical_bert/final
   from google.colab import files
   files.download('poetry_eebo_hierarchical_bert.zip')
   ```

3. Extract on your local machine to:
   ```
   /Users/justin/Repos/AI Project/models/poetry_eebo_hierarchical_bert/
   ```

---

## Troubleshooting

### ❌ "No GPU available"
- **Fix**: Runtime → Change runtime type → GPU → Save → Reconnect

### ❌ "401 Unauthorized" loading model
- **Fix**: Re-run Cell 3 (HuggingFace authentication)

### ❌ "numpy.dtype size changed, may indicate binary incompatibility"
- **Fix**: Runtime → Restart runtime → Factory reset runtime
- Then re-run all cells from the beginning
- The updated Cell 3 uses Colab's existing NumPy 2.x instead of downgrading

### ❌ "CUDA out of memory"
- **Fix**: Edit Cell 8, change `'batch_size': 16` to `'batch_size': 8` or `'batch_size': 4`

### ❌ "Files not found"
- **Fix**: Re-run Step 4 to organize uploaded files

### ❌ Training disconnects overnight
- **Fix**: Colab may disconnect after ~12 hours idle
  - Solution: Keep the tab open and check periodically
  - Or: Use Colab Pro ($10/month) for longer runtimes

---

## Expected Results

After training, you should have:

✅ **Trained model**: `poetry_eebo_hierarchical_bert/`
✅ **Loss curves**: Showing all 4 components decreasing
✅ **Checkpoints**: Saved every epoch
✅ **TensorBoard logs**: For detailed analysis

**Final loss values (approximate):**
- Total: ~2.5-3.0
- MLM: ~2.0-2.5
- Line: ~0.3-0.5
- Quatrain: ~0.3-0.5
- Sonnet: ~0.1-0.2

---

## Next Steps After Training

Once you have the trained model:

1. **Run validation scripts** (to be created):
   ```bash
   python scripts/validate_hierarchical_bert.py
   ```

2. **Compare trajectory tortuosity** with baseline models:
   - Base BERT: 3.17
   - EEBO-BERT: 3.45
   - Poetry-BERT: 3.59
   - **Hierarchical**: ???

3. **Write Paper 1** for Digital Humanities venue

---

## Questions?

- Check TensorBoard for training progress
- Loss curves should be smooth and decreasing
- If any component flatlines or increases, stop and investigate

**Training should be completely automated once you start Cell 14!**

---

**Last Updated:** November 4, 2025
**Estimated Cost:** Free (Google Colab) or $10/month (Colab Pro for A100)
**Duration:** 4-6 hours (A100) or 8-10 hours (T4)
