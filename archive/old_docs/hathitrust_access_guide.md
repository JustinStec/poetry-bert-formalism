# HathiTrust Research Center - Access Guide

## Why HathiTrust for Poetry Research

**Advantages over Gutenberg/ProQuest:**
- ✅ Designed specifically for computational text analysis
- ✅ 17+ million volumes, 8+ million public domain
- ✅ Clean OCR with metadata (dates, authors, genres)
- ✅ Bulk download tools built-in
- ✅ IU is a partner institution - enhanced access
- ✅ Completely legitimate for research use

## Getting Access

### 1. Register for HTRC Account
**URL:** https://analytics.hathitrust.org

**Steps:**
1. Click "Sign In" (top right)
2. Select "Indiana University" from institution list
3. Log in with IU credentials
4. Accept terms of service

**Access Level:** As IU researcher, you get:
- Full text access to public domain works
- Non-consumptive research tools
- Bulk download capabilities
- API access

### 2. Access Methods

**Option A: HathiTrust Digital Library (Browse/Search)**
- URL: https://www.hathitrust.org
- Search by author, title, subject
- Preview and verify texts before bulk download
- Export metadata catalogs

**Option B: HTRC Analytics (Computational Access)**
- URL: https://analytics.hathitrust.org
- Bulk text downloads
- Pre-built algorithms (word frequency, topic modeling, etc.)
- Workset builder for custom collections

**Option C: HTRC Data API (Programmatic)**
- Direct API access for large-scale downloads
- Python libraries available
- Rate limits but very generous

## Building a Poetry Corpus

### Search Strategy

**1. Find Poetry Collections:**
```
Subject: English poetry
Date Range: 1500-1900
Language: English
Rights: Public Domain
```

**2. Specific Authors:**
- Shakespeare, William
- Spenser, Edmund
- Sidney, Philip
- Donne, John
- Milton, John
- Wordsworth, William
- Keats, John
- Shelley, Percy Bysshe
- Byron, Lord
- Tennyson, Alfred
- Browning, Robert & Elizabeth Barrett
- Arnold, Matthew

**3. Build Worksets:**
- Create collections of related texts
- Export as dataset
- Download in bulk

### Download Format Options

**Available formats:**
- Plain text (best for BERT)
- METS/ALTO XML (with structure)
- Page images (if needed)
- Metadata (JSON, CSV)

## Python Tools for HTRC

### HTRC Feature Reader
```python
# Install
pip install htrc-feature-reader

# Usage
from htrc_features import FeatureReader
fr = FeatureReader(['volume_id_1', 'volume_id_2'])

for vol in fr.volumes():
    tokens = vol.tokens_per_page()
    # Process text
```

### Direct API Access
```python
import requests

# Get volume text
vol_id = "hvd.1234567890"
url = f"https://data.analytics.hathitrust.org/download/{vol_id}"

response = requests.get(url, headers={'Authorization': 'Bearer YOUR_TOKEN'})
text = response.text
```

## Recommended Workflow

### For Your CMU Project:

1. **Create Renaissance Poetry Workset:**
   - Search: "English poetry 1500-1650"
   - Include: Shakespeare, Spenser, Sidney, Donne, etc.
   - ~500-1000 volumes

2. **Create Modern Poetry Workset:**
   - Search: "English poetry 1800-1900"
   - Include: Romantics, Victorians
   - ~500-1000 volumes

3. **Download & Process:**
   - Use HTRC tools to download plain text
   - Parse into line-by-line format
   - Extract prosodic features
   - Train period-specific BERT models

4. **Cite Properly:**
   ```
   Text data from HathiTrust Digital Library
   (https://www.hathitrust.org), accessed [date].
   ```

## Next Steps

1. ☐ Register at https://analytics.hathitrust.org
2. ☐ Search for Shakespeare sonnets to verify access
3. ☐ Build test workset (10-20 volumes)
4. ☐ Download and test parsing pipeline
5. ☐ Scale up to full corpus

## Resources

- **Documentation:** https://wiki.htrc.illinois.edu/
- **Support:** htrc-help@hathitrust.org
- **Python tools:** https://github.com/htrc
- **IU Library contact:** digschol@iu.edu

## Comparison: HathiTrust vs Current Corpus

| Feature | Gutenberg (biglam) | HathiTrust |
|---------|-------------------|------------|
| Size | 1,191 books | 8M+ books (PD) |
| Quality | Poor lineation | Clean OCR |
| Metadata | Minimal | Rich (dates, authors) |
| Structure | Lost | Preserved |
| Legal | Public domain | Authorized TDM |
| IU Access | Anyone | Enhanced for IU |

**Recommendation:** Use HathiTrust for serious research corpus.
