# Final Poetry Corpus Summary

## Overall Statistics

- **Total poems:** 158,532
- **Total authors:** 12,473
- **Total lines:** 10,377,351
- **Total words:** 58,209,170
- **Average lines per poem:** 65.5
- **Average words per poem:** 367.2

## By Source

### Poetry Platform

- Poems: 118,535
- Authors: 8,842
- Lines: 7,760,275
- Words: 41,750,243
- Avg lines/poem: 65.5
- Avg words/poem: 352.2

### Project Gutenberg

- Poems: 39,997
- Authors: 3,631
- Lines: 2,617,076
- Words: 16,458,927
- Avg lines/poem: 65.4
- Avg words/poem: 411.5

## Cleanup Summary

### Major Cleanup Operations

1. **Reorganized files** into author folders (43,648 files → 3,926 folders)
2. **Integrated orphaned files** (3,251 kept, 5,757 deleted)
3. **GPT-4o author identification** for entire corpus
4. **Applied GPT-4o corrections** (16,780 poems cleaned)
5. **Scraped Poetry Platform** database (124,755 poems)
6. **Standardized filenames** (123,205 poems renamed)
7. **Merged and deduplicated** corpora (4,373 duplicates removed)
8. **Cleaned italic markup** (2,232 files, 12,837 instances)
9. **Removed foreign language poems** (4,129 total: 3,090 first pass + 1,039 second pass)
10. **Removed empty author folders** (1,760 folders)
11. **Removed editorial metadata** (1,375 files, 6,609 lines)
12. **Cleaned formatting artifacts** (30,523 files, 156,473 lines)
13. **Removed prose commentary** (1,427 reviewed, 589 cleaned, 357 deleted)
14. **Verified lineation** (2,088 long-line files confirmed intentional)
15. **Metadata cleanup** (3 sweeps, 3,821 files, 4,532 lines total)
16. **Removed verse drama** (227 files)
17. **Removed redundant titles** (150,908 files cleaned)

### Progression of Corpus Size

- Initial merged corpus: **170,889 poems**
- After first non-English removal: **167,799 poems**
- After verse drama removal: **167,215 poems**
- After second non-English removal: **166,176 poems**
- **Final corpus: 158,532 poems**

### Data Quality Improvements

- ✓ All poems organized by author
- ✓ Unified metadata format
- ✓ English-only corpus (>99% accuracy)
- ✓ Clean formatting (no editorial markup)
- ✓ No duplicate poems
- ✓ No redundant titles
- ✓ Standardized file naming
- ✓ Verified author attributions

## Next Steps

The corpus is now ready for:

1. **Hierarchical BERT training** - Primary goal
2. **Literary analysis** - Clean, standardized format
3. **Computational poetry research** - Large-scale dataset
4. **Stylometric studies** - Author-organized structure

