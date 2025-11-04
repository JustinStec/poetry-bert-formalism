# HTRC Access - Quick Start Guide

## You Now Have Access To:

### 1. HTRC Confluence Wiki
**URL:** https://htrc.atlassian.net/wiki/
**What to look for:**
- "Getting Started" guide
- "Data Access" or "Download Tools"
- "Python API" documentation
- "Authentication" setup
- API tokens/credentials

### 2. HTRC Analytics Portal
**URL:** https://analytics.hathitrust.org
**Log in with:** IU credentials

**Features:**
- **Workset Builder:** Create collections of books
- **Algorithms:** Pre-built text analysis tools
- **Data Capsule:** Secure environment for in-copyright texts
- **Downloads:** Export full text (public domain only)

### 3. HathiTrust Digital Library
**URL:** https://www.hathitrust.org
**Use for:** Searching and browsing individual books

---

## Your Path to Bulk Downloads

### Option 1: Via Analytics Portal (Easiest)
1. Log into https://analytics.hathitrust.org (IU credentials)
2. Go to "Worksets" or "Collections"
3. Search for poetry (e.g., "English poetry 1500-1900")
4. Build a workset
5. Export as dataset
6. Download full text

### Option 2: Via Python API
1. Check Confluence wiki for API documentation
2. Get API token/credentials
3. Use the script: `download_hathitrust_corpus.py`
4. Provide volume IDs from worksets

### Option 3: Request Bulk Access
**Email:** htrc-help@hathitrust.org

**Subject:** Bulk Download Access for IU Computational Humanities Research

**Body:**
```
I'm a postdoctoral researcher at Indiana University's Center for
Possible Minds conducting computational analysis of historical poetry.

I need bulk download access to public domain poetry texts for prosody
analysis (meter, rhyme scheme, lineation). My research requires full
text with preserved line breaks.

Can you provide:
1. rsync credentials for bulk downloads
2. API access for programmatic text retrieval
3. Guidance on accessing large poetry collections

I have access to the HTRC Confluence wiki and Analytics portal.

Thank you,
Justin Stec
Center for Possible Minds
Indiana University - Bloomington
stecj2700@gmail.com
```

---

## Immediate Next Steps

### Today (30 minutes):
- [ ] Log into Analytics portal: https://analytics.hathitrust.org
- [ ] Browse Confluence wiki for "Data Access" guide
- [ ] Try downloading ONE book as test:
  - Search "Shakespeare sonnets"
  - Click on a book
  - Look for download button
  - Choose "Plain text"
  - Verify it has proper lineation

### Tomorrow morning:
- [ ] Send email to IU library: digschol@iu.edu
- [ ] Send email to HTRC support: htrc-help@hathitrust.org

### This week:
- [ ] Build test workset (10-20 poetry books)
- [ ] Export and download via Analytics portal
- [ ] Scale up to full corpus (hundreds of books)

---

## What You're Looking For

**In Confluence wiki:**
- API documentation
- Authentication guide
- Python libraries
- Download scripts
- Workset export instructions

**In Analytics portal:**
- Workset/Collection builder
- Export options
- Download buttons
- Dataset formats

**Success = Getting:**
- Full text files (.txt)
- With preserved lineation
- For multiple poetry books
- Programmatically (not manual clicking)

---

## Resources

- **Analytics:** https://analytics.hathitrust.org
- **Wiki:** https://htrc.atlassian.net/wiki/
- **Digital Library:** https://www.hathitrust.org
- **Support:** htrc-help@hathitrust.org
- **Python Script:** `/Users/justin/Repos/AI Project/download_hathitrust_corpus.py`

---

**Questions? Check:**
1. Confluence wiki first
2. Analytics portal help section
3. Email htrc-help@hathitrust.org
