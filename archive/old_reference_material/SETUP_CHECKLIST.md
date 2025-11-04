# Setup Checklist

Copy this checklist to track your progress:

## Pre-Setup

- [ ] Python 3 is installed (check with `python3 --version`)
- [ ] Terminal is open
- [ ] Located project directory

## Installation

- [ ] Navigated to project folder in Terminal
- [ ] Ran `pip3 install -r requirements.txt`
- [ ] Installation completed without errors
- [ ] Verified Jupyter installed (`jupyter notebook --version`)

## First Run

- [ ] Ran `jupyter notebook` command
- [ ] Browser opened automatically (or manually opened the localhost URL)
- [ ] Can see project files in the browser
- [ ] Opened `Oread_Trajectory_Analysis.ipynb`

## Running Analysis

- [ ] Cell 1: Installed gensim
- [ ] Cell 2: Imported packages successfully
- [ ] Cell 3: Word2Vec model loaded (took 5-10 min first time)
- [ ] Cell 4: Trajectory metrics module loaded
- [ ] Cell 5: Oread vocabulary loaded
- [ ] Cell 6: Embeddings extracted (should show ~24-25 valid words)
- [ ] Cell 7: Metrics calculated and displayed
- [ ] Cell 8: 2D trajectory plot appeared
- [ ] Cell 9: 3D trajectory plot appeared
- [ ] Cell 10: Velocity profile bar chart appeared
- [ ] Cell 11: Results exported (check for .json and .npz files)
- [ ] Cell 12: Read summary section

## Verification

- [ ] `oread_trajectory_results.json` file exists in project folder
- [ ] `oread_embeddings.npz` file exists in project folder
- [ ] All plots rendered correctly
- [ ] No error messages in red text

## Completion

- [ ] Saved notebook (`File → Save and Checkpoint`)
- [ ] Closed browser tab
- [ ] Stopped Jupyter (Ctrl + C in Terminal)
- [ ] Ready to scale to full corpus!

---

## Troubleshooting Notes

Use this space to jot down any issues you encountered and how you fixed them:

```
Issue:

Solution:


```

---

## Next Session Reminder

To restart Jupyter next time:

```bash
cd "/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Project Development"
jupyter notebook
```

Then open `Oread_Trajectory_Analysis.ipynb` and you're ready to go!
