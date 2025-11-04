# HTRC Data Capsule - Full Text Access Guide

Based on HTRC documentation, here's how to access full text from HathiTrust.

---

## Your Access Level

**As IU postdoc:**
- **Immediate access:** 6.5M public domain volumes
- **With approval:** 17M volumes (including in-copyright)
  - IU is a HathiTrust member institution
  - Request approval for in-copyright access

---

## Method 1: HTRC Data Capsule (Recommended)

### What is it?
A secure computational environment where you can:
- Access full text of HathiTrust volumes
- Run your own code (Python, etc.)
- Download/export results (but not raw text of in-copyright works)

### Step 1: Create HTRC Analytics Account
1. Go to: https://analytics.hathitrust.org
2. Sign in with IU credentials
3. Accept terms of service

### Step 2: Build a Workset (Poetry Collection)

**Option A: Via HathiTrust Search**
1. Go to: https://www.hathitrust.org
2. Search: "English poetry" with filters:
   - Date: 1500-1900
   - Rights: Full view only (public domain)
   - Language: English
3. Click "Select" on books you want
4. Create collection
5. Export to HTRC as "Workset"

**Option B: Via HathiFiles or Bib API**
- Query HathiTrust Bibliographic API
- Or use HathiFiles dataset
- Or contact htrc-help@hathitrust.org for help building volume ID list

### Step 3: Launch Data Capsule
1. Log into: https://analytics.hathitrust.org
2. Go to "Data Capsules"
3. Click "Create New Capsule"
4. Select your poetry workset
5. Launch secure environment

### Step 4: Access Full Text in Capsule

**Use HTRC Workset Toolkit:**
```python
from htrc.workset import Workset
from htrc.data_api import DataAPI

# Load your poetry workset
ws = Workset('YOUR_WORKSET_ID')

# Initialize Data API
data_api = DataAPI()

# Download volumes from your workset
for volume_id in ws.volume_ids:
    # Get full text
    text = data_api.get_volume_text(volume_id)

    # Process text
    lines = text.split('\n')

    # Save or analyze
    with open(f'{volume_id}.txt', 'w') as f:
        f.write(text)
```

### Step 5: Process Text and Export

**Inside the Data Capsule:**
- Run your prosody analysis
- Extract features (stress, meter, etc.)
- Create structured JSONL corpus
- Export results (NOT raw in-copyright text)

**Public domain texts:**
- Can be exported directly
- Download to your local machine

---

## Method 2: HathiTrust Dataset Request (rsync)

For very large downloads without Data Capsule.

### Step 1: Apply for Dataset Request
1. Go to: https://www.hathitrust.org/help_digital_library
2. Find "Research Center Dataset Request"
3. Fill out application:
   - Researcher: Justin Stec, IU Center for Possible Minds
   - Project: Computational prosody analysis of historical poetry
   - Volumes needed: Public domain English poetry 1500-1900
   - Format: Full text

### Step 2: Receive rsync Credentials
HTRC will provide:
- rsync server address
- Authentication credentials
- Volume IDs or paths

### Step 3: Download via rsync
```bash
# Example rsync command (HTRC will provide exact syntax)
rsync -av --include='*.txt.zip' \
    username@htrc-server.org:/path/to/volumes/ \
    ./hathitrust_poetry_corpus/
```

---

## Method 3: HTRC Analytics Algorithms

Use pre-built algorithms without direct text access.

**Available algorithms:**
- Word frequency
- Topic modeling
- Named entity recognition
- Token count

**Limitations:**
- Can't do line-level prosody analysis
- Can't preserve lineation
- Only results exposed (not raw text)

**Not recommended for your research.**

---

## Recommended Path for You

### Immediate (Today):
1. ✓ Log into https://analytics.hathitrust.org (IU credentials)
2. ✓ Explore "Data Capsules" section
3. ✓ Build test workset (10-20 poetry volumes)
4. ✓ Launch a Data Capsule
5. ✓ Install HTRC Workset Toolkit
6. ✓ Download 1-2 test volumes
7. ✓ Verify lineation preservation

### Short-term (This week):
1. Request approval for in-copyright access (17M volumes)
   - Email: htrc-help@hathitrust.org
   - Mention: IU affiliation, computational research
2. Build larger poetry workset (500-1000 volumes)
3. Process in Data Capsule
4. Export structured corpus

### Alternative (If Capsule is complex):
1. Apply for HathiTrust dataset request
2. Use rsync for bulk download
3. Process locally

---

## Key Contacts

- **HTRC Help:** htrc-help@hathitrust.org
- **IU Library:** digschol@iu.edu
- **Dataset requests:** Via HathiTrust website

---

## Data Format

**What you'll get:**
- Zipped text files
- PairTree directory structure
- Uncorrected OCR text
- METS metadata

**Example structure:**
```
volume_id_1/
  ├── 00000001.txt  (page 1)
  ├── 00000002.txt  (page 2)
  └── ...

volume_id_2/
  └── ...
```

**You'll need to:**
1. Unzip files
2. Parse PairTree structure
3. Combine pages
4. Extract line-level structure
5. Process with prosody pipeline

---

## Python Script Update Needed

I'll update `download_hathitrust_corpus.py` to use:
- HTRC Workset Toolkit
- HTRC Data API
- Proper authentication (JWT)
- PairTree structure parsing

---

## Questions?

Contact me or:
- HTRC documentation: https://htrc.atlassian.net/wiki/
- HTRC support: htrc-help@hathitrust.org
- HathiTrust help: feedback@issues.hathitrust.org
