# Phase 1 Usage Guide: Corpus Cleanup & Sequential Renumbering

This guide explains how to use the Phase 1 scripts to clean and renumber the poetry corpus.

---

## Overview

Phase 1 transforms the corpus from its current state (118,535 files with duplicates) to a clean, sequentially-numbered state (116,675 unique poems, IDs 1→116,675).

### Current State:
- Files on disk: 118,535 poems
- Unique poems in CSV: 116,675 poems
- Duplicates: 1,860 files
- Poem IDs: Non-sequential (62,281 → 185,485 with gaps)

### Target State:
- Files on disk: 116,675 poems (matches CSV)
- Poem IDs: Sequential (1 → 116,675, no gaps)
- Filename format: `NNNNNN_Title_Author_Date.txt`
- Perfect alignment: files ↔ CSV

---

## Scripts

### 1. `cleanup_duplicates.py`
**Purpose**: Remove 1,860 duplicate files and merge author name variants

**What it does**:
- Removes duplicate files (same content_hash)
- Merges author directory variants:
  - "OReilly, John Boyle" → "Reilly, John Boyle O" (67 poems)
  - "Maeterlin, Maurice" → "Maeterlinck, Maurice" (47 poems)
  - "Hafiz, Shams al-Din" / "Shirazi, Hafez" → Standardize (39 poems)
  - "Sr, Giles Fletcher" / "Fletcher, Phineas" → Resolve (49 poems)
- Deletes 13 empty files
- Logs all deletions

### 2. `renumber_corpus.py`
**Purpose**: Renumber all poems sequentially (1 → 116,675)

**What it does**:
- Assigns new sequential poem_ids
- Renames all files: `NNNNNN_Title_Author_Date.txt`
- Updates CSV with new IDs and filenames
- Preserves all metadata (content_hash, etc.)
- Logs all renaming operations

### 3. `validate_corpus.py`
**Purpose**: Comprehensive validation of corpus integrity

**What it tests**:
1. File count = CSV count
2. Sequential IDs (no gaps, no duplicates)
3. Unique content hashes
4. All CSV filepaths exist
5. All files readable and non-empty
6. Correct filename format
7. Complete metadata
8. Content hash integrity (spot check)

---

## Execution Order

### ⚠️ IMPORTANT: Always run in DRY RUN mode first!

All scripts support `--execute` flag. Without it, they run in dry-run mode (show what would happen without making changes).

### Step 1: Clean Up Duplicates

```bash
# DRY RUN (review what will happen)
python3 scripts/cleanup_duplicates.py

# Review output carefully, then execute
python3 scripts/cleanup_duplicates.py --execute
```

**Expected output**:
```
✓ Duplicates to delete: 1,860
✓ Empty files to delete: 13
✓ Author merges: 4 (varying file counts)
✓ Expected remaining files: 116,675
```

**Logs created**:
- `data/metadata/cleanup_logs/deletions_YYYYMMDD_HHMMSS.json`
- `data/metadata/cleanup_logs/merges_YYYYMMDD_HHMMSS.json`

---

### Step 2: Sequential Renumbering

```bash
# DRY RUN (review what will happen)
python3 scripts/renumber_corpus.py

# Review output carefully, then execute
python3 scripts/renumber_corpus.py --execute
```

**Expected output**:
```
✓ Assigned sequential IDs to 116,675 poems
✓ Renamed 116,675 files
✓ New CSV created: data/metadata/corpus_renumbered.csv
```

**Filename format**:
- Before: `62281_On a Quiet Conscience_1, King Charles_unknown.txt`
- After: `000001_On_a_Quiet_Conscience_1_King_Charles_unknown.txt`

**Logs created**:
- `data/metadata/renumbering_logs/id_mapping_YYYYMMDD_HHMMSS.json`
- `data/metadata/renumbering_logs/renames_YYYYMMDD_HHMMSS.json`

---

### Step 3: Validate Corpus

```bash
# Run validation (no dry-run mode needed)
python3 scripts/validate_corpus.py
```

**Expected output (all tests should PASS)**:
```
✓ PASS: File count match
✓ PASS: Sequential IDs
✓ PASS: Unique hashes
✓ PASS: File existence
✓ PASS: File readability
✓ PASS: Filename format
✓ PASS: Metadata completeness
✓ PASS: Hash integrity

Tests passed: 8/8
🎉 ALL TESTS PASSED! Corpus is valid.
```

If any tests fail:
1. Review the error messages
2. Fix the issues
3. Re-run validation
4. Do NOT proceed to Phase 2 until all tests pass

---

### Step 4: Replace Old CSV (After Validation Passes)

```bash
# Backup old CSV
cp data/metadata/corpus_final_metadata.csv \
   data/metadata/corpus_final_metadata_OLD.csv

# Replace with new CSV
mv data/metadata/corpus_renumbered.csv \
   data/metadata/corpus_final_metadata.csv

# Validate again with new CSV
python3 scripts/validate_corpus.py
```

---

## Safety Features

### Dry Run Mode
- All destructive operations require `--execute` flag
- Default behavior is dry-run (show what would happen)
- Review output carefully before executing

### Comprehensive Logging
All operations are logged:
- `cleanup_logs/` - Deletions and merges
- `renumbering_logs/` - ID mappings and file renames

### Rollback Capability
- All logs include old → new mappings
- Can reverse operations if needed
- Validation catches errors before finalizing

---

## Troubleshooting

### Problem: "Duplicate file not found"
**Cause**: File already deleted or moved
**Solution**: Re-run cleanup script, review logs

### Problem: "Hash mismatch"
**Cause**: File content changed since CSV generation
**Solution**: Re-generate CSV with `scripts/update_metadata.py`

### Problem: "Invalid filename format"
**Cause**: Special characters in title/author
**Solution**: Script sanitizes automatically, check logs for details

### Problem: Validation fails after renumbering
**Cause**: Script interrupted mid-execution
**Solution**:
1. Review logs to see how far script got
2. May need to restore from backup
3. Re-run from beginning

---

## Expected Timeline

- **Step 1 (Cleanup)**: ~2-5 minutes (DRY RUN: instant, EXECUTE: ~2-5 min)
- **Step 2 (Renumber)**: ~10-15 minutes (DRY RUN: ~1 min, EXECUTE: ~10-15 min)
- **Step 3 (Validate)**: ~5-10 minutes

**Total Phase 1**: ~20-30 minutes

---

## Verification Checklist

After completing Phase 1, verify:

- [ ] File count on disk = 116,675
- [ ] CSV has 116,675 entries
- [ ] Poem IDs are 1 → 116,675 (sequential, no gaps)
- [ ] All filenames follow format: `NNNNNN_Title_Author_Date.txt`
- [ ] All content_hashes are unique
- [ ] Validation script passes all 8 tests
- [ ] Logs saved in `data/metadata/cleanup_logs/` and `renumbering_logs/`

---

## Next Steps

Once Phase 1 is complete and all validation tests pass:

1. **Phase 2**: Add automated basic metadata
   - Line counts, word counts
   - Author parsing, year extraction
   - Source URLs

2. **Commit to GitHub**:
   ```bash
   git add -A
   git commit -m "Phase 1 complete: Clean, sequentially-numbered corpus (116,675 poems)"
   git push
   ```

---

## Support

If you encounter issues:
1. Check logs in `data/metadata/cleanup_logs/` and `renumbering_logs/`
2. Review validation output for specific errors
3. Ensure all prerequisites are met (CSV exists, corpus directory accessible)
4. Ask Claude Code for help debugging

---

## File Locations

### Scripts:
- `/Users/justin/Repos/AI Project/scripts/cleanup_duplicates.py`
- `/Users/justin/Repos/AI Project/scripts/renumber_corpus.py`
- `/Users/justin/Repos/AI Project/scripts/validate_corpus.py`

### Data:
- Corpus: `/Users/justin/Repos/AI Project/data/processed/poetry_platform_renamed/`
- CSV: `/Users/justin/Repos/AI Project/data/metadata/corpus_final_metadata.csv`
- Logs: `/Users/justin/Repos/AI Project/data/metadata/cleanup_logs/`
- Logs: `/Users/justin/Repos/AI Project/data/metadata/renumbering_logs/`

### Documentation:
- Overall plan: `/Users/justin/Repos/AI Project/docs/CORPUS_ENHANCEMENT_PLAN.md`
- Metadata schema: `/Users/justin/Repos/AI Project/docs/METADATA_SCHEMA.md`
- This guide: `/Users/justin/Repos/AI Project/docs/PHASE1_USAGE.md`
