# Poetry Corpus Project - TODO

## ✅ Completed

### Phase 1: Corpus Cleanup & Sequential Renumbering
- [x] Remove 1,860 duplicate files (by content hash)
- [x] Merge author name variants (3 directories: OReilly→Reilly, Shirazi→Hafiz, Fletcher→Sr Giles Fletcher)
- [x] Delete 14 empty files
- [x] Renumber all poems sequentially (1 → 116,674, no gaps)
- [x] Standardize filename format: `NNNNNN_Title_Author_Date.txt`
- [x] Sync CSV with actual files on disk
- [x] Validate corpus integrity (7/8 tests passing)
- [x] Document Phase 1 process and scripts

**Final corpus state:**
- 116,674 unique poems
- Sequential poem_ids (1-116,674)
- All files match CSV
- All validation tests pass except 2 missing titles (minor)

---

## 🔄 In Progress

None currently.

---

## 📋 Planned

### Phase 2: Automated Basic Metadata (Next)
- [ ] Fix 2 poems with missing titles (poems 75474, 84157)
- [ ] Recompute line counts and word counts
- [ ] Parse author names into author_last, author_first
- [ ] Extract/approximate years from date field
- [ ] Generate source URLs from source field
- [ ] Add search_vector field (for PostgreSQL full-text search)
- [ ] Add created_at, updated_at timestamps
- [ ] Validate metadata completeness (aim for 100% coverage on basic fields)

**Goal**: Complete Tier 1 metadata (17 fields, 100% coverage)

### Phase 3: Historical Context Classification
- [ ] Fine-tune local LLM (MLX on M4 Max) for period classification
  - 12 periods: Ancient, Medieval, Renaissance, Restoration, 18th C, Romantic, Victorian, Modernist, etc.
- [ ] Train classifier for literary movement
  - 13+ movements: Romanticism, Symbolism, Surrealism, Beat, Confessional, etc.
- [ ] Train classifier for mode (4 categories: Lyric, Narrative, Dramatic, Satirical)
- [ ] Generate confidence scores for all classifications
- [ ] Only accept high-confidence predictions (>90%)
- [ ] Flag low-confidence poems for manual review

**Goal**: Tier 2 metadata (10 fields, 70-80% coverage)

### Phase 4: Prosodic Features Analysis
- [ ] Genre detection (Sonnet, Ode, Elegy, Free Verse, etc.)
- [ ] Meter detection using prosodic library
- [ ] Rhyme scheme analysis
- [ ] Stanza structure detection
- [ ] Generate confidence scores
- [ ] Manual review of uncertain cases

**Goal**: Tier 3 metadata (9 fields, 40-60% coverage on formal poetry)

### Phase 5: Research Subset (Gold Standard)
- [ ] Select 1,000 representative poems across periods/movements
- [ ] Manual annotation of all 35+ fields
- [ ] Include rhetorical features: register, rhetorical_genre, focalization, person, etc.
- [ ] Create gold standard for evaluating automated methods
- [ ] Use for LLM training/validation

**Goal**: Tier 4 metadata (16 fields, 1,000-poem subset)

### Phase 6: PostgreSQL Database
- [ ] Design normalized schema (4+ tables)
- [ ] Set up pgvector extension for BERT embeddings
- [ ] Create indexes for performance
- [ ] Import all metadata
- [ ] Set up full-text search
- [ ] Create views for common queries
- [ ] Document database schema and API

**Goal**: Production-ready database with full corpus

---

## 🔧 Technical Debt / Maintenance

- [ ] Clean up organization scripts in root directory
- [ ] Archive old/temporary scripts
- [ ] Update package dependencies
- [ ] Add unit tests for core functions
- [ ] Set up CI/CD for validation

---

## 📚 Documentation

- [x] CORPUS_ENHANCEMENT_PLAN.md - Overall strategy
- [x] METADATA_SCHEMA.md - Complete field reference
- [x] PHASE1_USAGE.md - Phase 1 execution guide
- [ ] Add Phase 2 usage guide
- [ ] Add database schema documentation
- [ ] Add API documentation (when ready)

---

## 🎯 Long-term Goals

- Publish corpus as open dataset
- Create web interface for exploration
- Generate BERT embeddings for all poems
- Build recommendation system
- Support multiple export formats (JSON, CSV, SQL)

---

**Last Updated**: 2025-11-08 (Phase 1 complete)
