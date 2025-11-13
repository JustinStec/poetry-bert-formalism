# Phase 4: Formal Features + Historical BERT Content

**Created:** November 15, 2025, 10:00 AM EST
**Updated:** November 15, 2025, 10:30 AM EST
**Status:** IN PROGRESS
**Purpose:** Improve classifications using explicit formal feature extraction + period-appropriate historical BERTs

---

## Goal

Phase 3B created **heuristic-based classifications** of 28 dimensions for all 116,674 HEPC poems using pattern-matching (archaic pronouns, line counts, temporal markers).

**Phase 4 improves these classifications** using TWO complementary approaches:
1. **Explicit formal feature extraction** - Use specialized prosodic tools to extract meter, rhyme, stanza structure
2. **Historical BERT content features** - Use existing period-trained BERTs for genre, register, rhetoric

**Why This Approach:**
- Standard BERT treats poems as prose (strips line breaks, ignores stanza structure)
- Specialized tools (CMU Pronouncing Dictionary) are MORE accurate for versification features
- Historical BERTs are good for content-based features (genre, register, discourse type)
- Fast (2-3 weeks vs 6+ months for custom training)
- Publishable results

---

## The 28 Classification Dimensions

### HISTORICAL (2 fields)
- period (Early Modern, Romantic, Modern, etc.)
- literary_movement (Romanticism, Victorianism, etc.)

### RHETORICAL (14 fields)
- register (Meditative, Elevated, Colloquial, etc.)
- rhetorical_genre (Epideictic, Deliberative, Judicial)
- discursive_structure (Monologic, Dialogic, etc.)
- discourse_type (Narration, Description, Argument, etc.)
- narrative_level (First person, Third person, Variable, etc.)
- diegetic_mimetic (Diegetic, Mimetic, Mixed)
- focalization (First person internal, Third person, etc.)
- person (1st, 2nd, 3rd, Variable)
- deictic_orientation (Subjective, Objective, etc.)
- addressee_type (Direct address, Unaddressed, etc.)
- deictic_object (Nature/landscape, Abstract concepts, etc.)
- temporal_orientation (Present, Past, Future, Timeless)
- temporal_structure (Static, Progressive, etc.)
- tradition (Literary, Oral, Religious, etc.)

### FORMAL (5 fields)
- mode (Lyric, Narrative, Dramatic, etc.)
- genre (Sonnet, Elegy, Epic, Ode, etc.)
- stanza_structure (Quatrains, Couplets, Blank verse, etc.)
- meter (Iambic pentameter, Free verse, etc.)
- rhyme (ABAB, AABB, None, etc.)

---

## Resources Available

### ✅ Data
1. **116,674 heuristic classifications** (Phase 3B output)
   - Location: `data/classified_poems_complete.csv` (34 MB)
   - HuggingFace: https://huggingface.co/datasets/jts3et/hepc-classified-poems

2. **HEPC Corpus texts** (M4 Max only)
   - Location: `Data/corpus/texts/` (551 MB)
   - Metadata: `Data/corpus/metadata.csv` (41 MB)

3. **Manual training labels** (if available)
   - Expected: ~357 manually labeled poems (mentioned in docs but not found)
   - May need to create validation set from Phase 3B classifications

### ❓ Models (Need to verify/download)
1. **EEBO-BERT** (1470-1690) - ✅ Available locally (418 MB)
   - HuggingFace: jts3et/eebo-bert
   - Location: `models/eebo_bert/`

2. **ECCO-BERT** (1700-1800) - ❓ Need to find on HuggingFace

3. **BL-BERT** (1760-1900) - ❓ Need to find on HuggingFace

4. **MacBERTh** (1450-1950) - ❓ Need to find on HuggingFace

---

## Phase 4 Approach

### Step 1: Resource Verification (Current Task)
- ✅ EEBO-BERT locally available
- ⏸️ Find/download ECCO-BERT, BL-BERT, MacBERTh
- ⏸️ Verify access to HEPC corpus on M4 Max
- ⏸️ Identify training/validation data

### Step 2: Period Assignment
For each of the 116,674 poems, assign appropriate historical BERT:
- **1100-1690** → EEBO-BERT
- **1690-1760** → EEBO-BERT or ECCO-BERT (transition)
- **1760-1800** → ECCO-BERT
- **1800-1900** → BL-BERT
- **1900-1928** → MacBERTh (fallback)

Use existing `period` field from Phase 3B classifications.

### Step 3: Embedding Extraction
Extract 768-dimensional embeddings for each poem using period-appropriate BERT:
```python
# Pseudocode
for poem in corpus:
    bert_model = select_bert_by_period(poem.period)
    embedding = bert_model.encode(poem.text)  # [768]
    save_embedding(poem.id, embedding)
```

**Output:** 116,674 × 768 embedding matrix
**Storage:** ~350 MB as compressed numpy array

### Step 4: Classification Head Training
Train multi-task classification head on embeddings:
```python
# Input: 768-dimensional BERT embedding
# Output: 28 classification fields

model = MultiTaskClassifier(
    input_dim=768,
    tasks={
        'period': num_period_classes,
        'meter': num_meter_classes,
        'rhyme': num_rhyme_classes,
        # ... all 28 fields
    }
)
```

**Training strategy:**
- If manual labels available: Use for supervised fine-tuning
- Otherwise: Train on Phase 3B heuristic labels (self-training)
- Validation: Hold out 10% for evaluation

### Step 5: Improved Classification Generation
Apply trained model to all 116K poems:
- Generate predictions for all 28 dimensions
- Compare with Phase 3B heuristics
- Analyze improvements and disagreements

### Step 6: Validation and Analysis
- Compare model predictions vs heuristics
- Manual spot-checking of disagreements
- Generate statistics on classification distribution
- Update final database

---

## Expected Improvements

### What Historical BERTs Provide:
1. **Period-appropriate language understanding**
   - EEBO-BERT understands Early Modern English morphology
   - ECCO-BERT captures 18th century linguistic patterns
   - Better than modern BERT for historical texts

2. **Formal feature detection**
   - Better meter detection through period-specific prosody
   - Improved genre classification (sonnet vs ballad vs epic)
   - More accurate stanza structure identification

3. **Rhetorical feature detection**
   - Better person/focalization detection
   - Improved temporal orientation classification
   - More accurate addressee type identification

### What They DON'T Provide:
- Not for semantic trajectory analysis
- Not for measuring "poetic complexity"
- Not for generating new poems

---

## Success Metrics

1. **Coverage:** All 116,674 poems with improved classifications
2. **Consistency:** Fewer "Unknown" or "Variable" labels than Phase 3B
3. **Validation:** Manual checking of sample shows >80% accuracy
4. **Distribution:** Reasonable distribution across categories (no mode collapse)

---

## Timeline Estimate

**On M4 Max (GPU available):**
- Step 1: Resource verification - 1 hour
- Step 2: Period assignment - 15 minutes
- Step 3: Embedding extraction - 6-8 hours (116K poems × 4 models)
- Step 4: Model training - 2-4 hours
- Step 5: Classification generation - 1 hour
- Step 6: Validation - 2 hours

**Total:** ~12-16 hours of compute time (mostly Step 3)

**On Air (no GPU):**
- Not recommended - would take days for embedding extraction

---

## Next Immediate Actions

1. ✅ Created this plan document
2. ⏸️ Search HuggingFace for ECCO-BERT, BL-BERT, MacBERTh
3. ⏸️ Verify HEPC corpus access on M4 Max
4. ⏸️ Create embedding extraction script
5. ⏸️ Download remaining historical BERTs to M4 Max

---

**Status:** PLANNING COMPLETE - Ready to begin resource verification
