# Corpus Management Guide

Quick reference for adding poems and managing your corpus.

## 🚀 Quick Start: Add a Single Poem (Remote)

**From wife's computer via SSH:**
```bash
ssh justin@10.21.55.231
~/Repos/AI\ Project/scripts/utils/add_poem.sh
```

Follow the prompts to add one poem.

---

## 📚 Batch Add Many Poems

### Option 1: File Sharing (Easiest for Many Poems)

**Setup (one-time):**
1. On your Mac: System Settings → General → Sharing → File Sharing (ON)
2. Share the folder: `/Users/justin/Repos/AI Project/Data/corpus_texts`

**From wife's computer:**
1. Finder → Go → Connect to Server
2. Enter: `smb://10.21.55.231`
3. Navigate to: `Repos/AI Project/Data/corpus_texts`
4. Drag and drop poem files
   - Name format: `NNN_Author_Title.txt` (number will be auto-assigned)
   - Or just: `Author_Title.txt` (script will number them)

### Option 2: Batch Upload via SSH

**On wife's computer, create a folder with poems:**
```bash
mkdir ~/Desktop/poems_to_add
# Put all poem .txt files here
```

**Upload to your Mac:**
```bash
scp ~/Desktop/poems_to_add/*.txt justin@10.21.55.231:~/Desktop/poems_to_add/
```

**SSH in and run batch script:**
```bash
ssh justin@10.21.55.231
~/Repos/AI\ Project/scripts/utils/batch_add_poems.sh
```

---

## 🔄 Update Metadata After Adding Poems

After adding poems (any method), update the metadata:

```bash
~/Repos/AI\ Project/scripts/utils/update_corpus.sh
```

This will:
1. Scan for new poems
2. Create basic metadata entries
3. Update the Excel file

Then **edit the metadata file** to fill in details:
- Open: `~/Repos/AI Project/Metadata/corpus_metadata.xlsx`
- Or edit CSV: `~/Repos/AI Project/Metadata/corpus_metadata.csv`
- Fill in: year, period, form, etc.
- Set `collected=TRUE` for poems you want to analyze

---

## 📝 Poem File Naming Convention

**Good filenames:**
- `056_John_Donne_The_Good_Morrow.txt`
- `057_Emily_Dickinson_Because_I_Could_Not_Stop.txt`
- `Langston_Hughes_Harlem.txt` (script will add number)

**What to avoid:**
- Special characters: `! @ # $ % ^ & * ( )`
- Spaces (use underscores instead)

---

## 🛠 All Available Scripts

| Script | Purpose |
|--------|---------|
| `add_poem.sh` | Add single poem interactively |
| `batch_add_poems.sh` | Add multiple poems from Desktop folder |
| `scan_new_poems.sh` | Scan corpus and create metadata entries |
| `update_corpus.sh` | One-command: scan + update metadata |
| `training_progress.sh` | Check BERT training progress |
| `check_training_status.sh` | Quick training status |

---

## 🏠 Remote Access Setup

**Your Mac's IP:** `10.21.55.231`

**Enable Remote Login:**
System Settings → General → Sharing → Remote Login (ON)

**Connect:**
```bash
ssh justin@10.21.55.231
```

**Enable File Sharing:**
System Settings → General → Sharing → File Sharing (ON)

---

## 📊 Metadata Fields

When editing metadata, here are the fields to fill:

- **id**: Poem number (auto-assigned)
- **filename**: Poem filename (auto-detected)
- **author**: Poet's name
- **title**: Poem title
- **year**: Year written/published
- **period**: Tudor, Elizabethan, Romantic, Modernist, etc.
- **form**: Sonnet, Free verse, Blank verse, etc.
- **lines**: Line count (auto-counted)
- **words**: Word count (auto-counted)
- **collected**: TRUE/FALSE (set TRUE to include in analysis)

---

## 🎯 Typical Workflow

1. **Wife adds poems via File Sharing**
   - Drag .txt files to corpus folder

2. **You update metadata (via SSH or locally)**
   ```bash
   ~/Repos/AI\ Project/scripts/utils/update_corpus.sh
   ```

3. **Edit metadata file**
   - Open the Excel file
   - Fill in year, period, form
   - Set collected=TRUE

4. **Ready for analysis!**
   - BERT will analyze all poems with collected=TRUE

---

## 💡 Tips

- Keep original poems in a backup folder
- Use consistent author name spellings
- The metadata scan runs fast - safe to run multiple times
- You can edit CSV or Excel (Excel has formulas for statistics)
- Set collected=FALSE for poems you're still working on
