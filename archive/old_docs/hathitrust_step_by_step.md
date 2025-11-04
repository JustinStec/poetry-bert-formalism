# HathiTrust Full Text Access - Step by Step

## The Confusion

**What you DON'T want:** Extracted Features (the sample you downloaded)
**What you DO want:** Full text downloads from HathiTrust Digital Library

---

## Method 1: Individual Book Downloads (Start Here)

### Step 1: Go to HathiTrust Digital Library
**URL:** https://www.hathitrust.org

### Step 2: Search for Poetry
Example searches:
- "Shakespeare sonnets"
- "Wordsworth poems"
- "English poetry"

### Step 3: Filter Results
- Click "Full view only" (public domain)
- Set date range: 1500-1900
- Language: English

### Step 4: Open a Book
Click on any result to view the book

### Step 5: Download Full Text
Look for the download icon (⬇) or "Download" link
- Choose "Plain text" format
- This gives you the actual text with lineation preserved

### Example: Let's Get Shakespeare Sonnets

1. Go to: https://www.hathitrust.org
2. Search: "shakespeare sonnets"
3. Find result from 1609 or clean edition
4. Click "Download" → "Plain text"
5. Save the .txt file

**That's it.** You now have the full text with proper line breaks.

---

## Method 2: Bulk Downloads (For Larger Projects)

### Option A: HTRC Data API

**Install Python library:**
```bash
pip install hathitrust-api
```

**Download a volume:**
```python
from hathitrust_api import DataAPI

api = DataAPI()
volume_id = "hvd.hnwpu9"  # Example: Shakespeare

# Get full text
text = api.get_volume_text(volume_id)

# Save to file
with open('shakespeare.txt', 'w') as f:
    f.write(text)
```

### Option B: Build a Collection ("Workset")

1. Go to: https://babel.hathitrust.org/cgi/mb
2. Log in with IU credentials
3. Search for books
4. Click "Select" on each book you want
5. Create a "Collection"
6. Export collection metadata
7. Use Python API to download all texts in collection

---

## Method 3: Using rsync for Large Datasets

HathiTrust provides rsync access for partner institutions (IU is a partner).

**Contact:** htrc-help@hathitrust.org
**Ask for:** Bulk download access for computational research

They can provide:
- rsync credentials
- Access to full-text datasets
- Batch download scripts

---

## What You Should Do Right Now

### Immediate (5 minutes):
1. Go to https://www.hathitrust.org
2. Search "shakespeare sonnets"
3. Download one book as plain text
4. Verify it has proper lineation
5. Compare with your Gutenberg version

### Short-term (tomorrow):
1. Send email to IU library (digschol@iu.edu)
2. Ask about HathiTrust bulk access for IU researchers
3. Mention you're at Center for Possible Minds, need computational access

### Medium-term (next week):
1. Email htrc-help@hathitrust.org
2. Explain: "I'm a postdoc at IU's Center for Possible Minds doing computational poetry analysis"
3. Ask: "How can I get bulk download access for historical poetry texts?"
4. They will likely set you up with rsync or API credentials

---

## The Real Answer

**You have THREE paths to get bulk poetry:**

1. **Project Gutenberg** (your Colab rebuild) - ~1,200 books, running now
2. **HathiTrust** (via IU partnership) - 8M+ books, need to request access
3. **ProQuest** (via IU license) - premium, need library approval

**My recommendation:**
- Use Gutenberg rebuild for CMU application (due Friday)
- Request HathiTrust bulk access for dissertation research
- Email IU library about ProQuest TDM rights

---

## Try This Now

Open your browser and:
1. Go to: https://www.hathitrust.org
2. Search: "Milton Paradise Lost"
3. Click first full-view result
4. Click "Download" → "Plain text"

If you can download that file, you have access. Then it's just a matter of scaling up with API/rsync.

---

**Questions?**
- Can you access HathiTrust.org and search? (Test this first)
- Can you download a single book as plain text? (Test this second)
- Do you need help with Python API for bulk downloads? (We'll do this after testing)
