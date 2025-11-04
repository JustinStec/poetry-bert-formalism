# Renaissance Texts Available in Gutenberg Corpus

## Confirmed Texts for Prosody-BERT Analysis

### ✅ Shakespeare's Sonnets
- **Gutenberg ID:** 1041
- **Lines:** 2,136
- **Content:** Complete collection of 154 sonnets
- **First lines:** "From fairest creatures we desire increase, / That thereby beauty's rose might never die..."
- **Perfect for:** Iambic pentameter analysis, semantic trajectories across early/late sonnets

### ✅ Philip Sidney
- **Gutenberg ID:** 1962
- **Lines:** 1,548
- **Content:** Selected works (likely includes Astrophil and Stella)
- **First lines:** Biography begins "Philip Sidney was born at Penshurst, in Kent..."
- **Note:** Need to extract actual sonnets from biographical content

### ✅ Edmund Spenser - The Faerie Queene
- **Gutenberg ID:** 2383
- **Lines:** 3,547
- **Content:** Mixed anthology with Canterbury Tales
- **Note:** Need to isolate Spenser verses from Chaucer

## Analysis Plan for CMU Writing Sample

### Quick Pilot Study Options:

**Option 1: Shakespeare Sonnets (Recommended)**
- Cleanest dataset (2,136 lines of pure iambic pentameter)
- Clear structure (154 sonnets, ~14 lines each)
- Well-documented semantic shifts (procreation sonnets → dark lady → young man)
- Can compare early sonnets (1-17) vs. late sonnets (127-154)

**Option 2: Cross-Renaissance Comparison**
- Extract 20 sonnets each from Shakespeare, Sidney, Spenser
- Compare how prosody-conditioning affects semantic modeling across authors
- More ambitious but riskier with mixed text quality

### Recommended Approach for Friday Deadline:

1. **Extract Shakespeare Sonnets** (tonight)
   - Clean, complete dataset
   - Run prosody extraction pipeline

2. **Pilot Analysis** (Thursday morning)
   - Apply prosody-BERT (once Gutenberg training finishes)
   - Compare standard BERT vs prosody-conditioned on semantic clustering

3. **Write 3-5 page sample** (Thursday afternoon)
   - Method: Architecture description, prosody extraction
   - Results: Embedding visualizations showing prosodic effects
   - Discussion: Implications for computational formalism

## Technical Notes

- All texts are in JSONL format (one line per entry)
- Need to reconstruct full poems from individual lines
- Prosody extraction works best on complete stanzas/sonnets
- Can use existing `extract_prosody_features.py` pipeline

## Next Steps

1. Extract Shakespeare sonnets to clean JSON format
2. Wait for Gutenberg BERT training to complete
3. Run prosody-conditioned analysis
4. Draft writing sample with results
