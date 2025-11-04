# Remote Access Quick Reference

## 🔑 Connection Info

**Mac IP Address:** `10.21.55.231`
**Username:** `justin`
**Password:** (your Mac login password)

---

## 📁 Method 1: File Sharing (Easiest for Adding Many Poems)

### From Wife's Mac:

1. **Connect to your Mac:**
   - Finder → Go → Connect to Server (⌘K)
   - Enter: `smb://10.21.55.231`
   - Click Connect
   - Login as: `justin` with your Mac password

2. **Navigate to corpus folder:**
   - Open: `Repos` → `AI Project` → `Data` → `corpus_texts`

3. **Add poems:**
   - Drag and drop `.txt` files into this folder
   - Name them: `AuthorName_PoemTitle.txt`
   - Examples:
     - `Emily_Dickinson_Hope.txt`
     - `Robert_Frost_The_Road_Not_Taken.txt`

4. **Done!**
   - Disconnect when finished

---

## 💻 Method 2: SSH Terminal Access

### Connect via Terminal:

```bash
ssh justin@10.21.55.231
```

Enter your Mac password when prompted.

### Once Connected - Common Commands:

**Navigate to project:**
```bash
cd ~/Repos/AI\ Project
```

**Add a single poem (interactive):**
```bash
~/Repos/AI\ Project/scripts/utils/add_poem.sh
```

**Check BERT training progress:**
```bash
~/Repos/AI\ Project/scripts/utils/training_progress.sh
```

**Quick training status:**
```bash
~/Repos/AI\ Project/scripts/utils/check_training_status.sh
```

**List poems in corpus:**
```bash
ls ~/Repos/AI\ Project/Data/corpus_texts/
```

**Disconnect:**
```bash
exit
```

---

## 📤 Method 3: Upload Files via SCP

### From Wife's Computer (if she has poem files locally):

**Upload one file:**
```bash
scp ~/Desktop/my_poem.txt justin@10.21.55.231:~/Desktop/poems_to_add/
```

**Upload all poems from a folder:**
```bash
scp ~/Desktop/poems_to_add/*.txt justin@10.21.55.231:~/Desktop/poems_to_add/
```

**Then SSH in and run batch script:**
```bash
ssh justin@10.21.55.231
~/Repos/AI\ Project/scripts/utils/batch_add_poems.sh
```

---

## 🔧 For You: Update Metadata After She Adds Poems

**SSH in or run locally:**
```bash
ssh justin@10.21.55.231
cd ~/Repos/AI\ Project
python3 scripts/utils/smart_scan_poems.py
```

**Then edit metadata:**
```bash
open ~/Repos/AI\ Project/Metadata/corpus_metadata.xlsx
```

Fill in: author, title, year, period, form
Set: `collected=TRUE` for poems to analyze

---

## ✅ Setup Checklist (One-Time)

On your Mac before leaving:

- [ ] Enable Remote Login
  - System Settings → General → Sharing → Remote Login (ON)

- [ ] Enable File Sharing
  - System Settings → General → Sharing → File Sharing (ON)

- [ ] Keep Mac awake for training
  ```bash
  caffeinate -i
  ```

- [ ] Verify connection works
  ```bash
  # From wife's computer:
  ssh justin@10.21.55.231
  ```

---

## 📱 From iPhone/iPad

**Using Terminus or Prompt App:**

1. Download: Terminus (free) or Prompt (paid)
2. Add connection:
   - Host: `10.21.55.231`
   - User: `justin`
   - Port: `22`
3. Connect and run commands above

---

## 🆘 Troubleshooting

**"Connection refused"**
- Mac Remote Login might be off
- Check: System Settings → Sharing → Remote Login

**"Network unreachable"**
- Wife's computer must be on same network as your Mac
- Or use VPN if accessing from outside

**"Permission denied"**
- Wrong password
- Make sure using your Mac login password

**Can't find folders**
- Make sure File Sharing is enabled
- Check path: `/Users/justin/Repos/AI Project/Data/corpus_texts`

---

## 📍 Key File Paths

**Corpus (where poems go):**
```
~/Repos/AI Project/Data/corpus_texts/
```

**Metadata file:**
```
~/Repos/AI Project/Metadata/corpus_metadata.xlsx
```

**All scripts:**
```
~/Repos/AI Project/scripts/utils/
  ├── add_poem.sh              # Add one poem interactively
  ├── batch_add_poems.sh       # Batch add from Desktop
  ├── smart_scan_poems.py      # Scan & update metadata
  ├── training_progress.sh     # Check BERT progress
  └── check_training_status.sh # Quick status check
```

---

## 🎯 Most Common Workflow

**Wife adds poems via File Sharing:**
1. Connect: `smb://10.21.55.231`
2. Navigate to: `Repos/AI Project/Data/corpus_texts`
3. Drop poem files

**You update metadata later:**
```bash
ssh justin@10.21.55.231
cd ~/Repos/AI\ Project
python3 scripts/utils/smart_scan_poems.py
open Metadata/corpus_metadata.xlsx
# Fill in details, set collected=TRUE
```

**Done!**
