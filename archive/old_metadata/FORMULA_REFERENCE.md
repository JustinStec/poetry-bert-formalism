# Excel/Google Sheets Formulas for Corpus Metadata

Add these formulas below your data (starting around row 57) in the Excel/Google Sheets version of corpus_metadata.csv

## Setup
1. Open corpus_metadata.csv in Excel or Google Sheets
2. Save as .xlsx file
3. Add these formulas in the cells indicated below

## Summary Statistics Section

### Row 57: Header
**A57:** `SUMMARY STATISTICS (COLLECTED POEMS ONLY)`

### Starting Row 59: Period Counts

| Cell | Label | Formula |
|------|-------|---------|
| A59 | PERIOD | (header) |
| B59 | Count | (header) |
| A60 | Tudor | (label) |
| B60 | | `=COUNTIFS(E:E,A60,AI:AI,TRUE)` |
| A61 | Elizabethan | (label) |
| B61 | | `=COUNTIFS(E:E,A61,AI:AI,TRUE)` |
| A62 | Jacobean | (label) |
| B62 | | `=COUNTIFS(E:E,A62,AI:AI,TRUE)` |
| A63 | Caroline | (label) |
| B63 | | `=COUNTIFS(E:E,A63,AI:AI,TRUE)` |
| A64 | Interregnum | (label) |
| B64 | | `=COUNTIFS(E:E,A64,AI:AI,TRUE)` |
| A65 | Restoration | (label) |
| B65 | | `=COUNTIFS(E:E,A65,AI:AI,TRUE)` |
| A66 | Neoclassical | (label) |
| B66 | | `=COUNTIFS(E:E,A66,AI:AI,TRUE)` |
| A67 | Romantic | (label) |
| B67 | | `=COUNTIFS(E:E,A67,AI:AI,TRUE)` |
| A68 | Victorian | (label) |
| B68 | | `=COUNTIFS(E:E,A68,AI:AI,TRUE)` |
| A69 | Modernist | (label) |
| B69 | | `=COUNTIFS(E:E,A69,AI:AI,TRUE)` |
| A70 | Postwar | (label) |
| B70 | | `=COUNTIFS(E:E,A70,AI:AI,TRUE)` |
| A71 | Contemporary | (label) |
| B71 | | `=COUNTIFS(E:E,A71,AI:AI,TRUE)` |

### Column D: Literary Movement Counts

| Cell | Label | Formula |
|------|-------|---------|
| D59 | LITERARY_MOVEMENT | (header) |
| E59 | Count | (header) |
| D60 | Renaissance | (label) |
| E60 | | `=COUNTIFS(F:F,D60,AI:AI,TRUE)` |
| D61 | Metaphysical | (label) |
| E61 | | `=COUNTIFS(F:F,D61,AI:AI,TRUE)` |
| D62 | Augustan | (label) |
| E62 | | `=COUNTIFS(F:F,D62,AI:AI,TRUE)` |
| D63 | Graveyard School | (label) |
| E63 | | `=COUNTIFS(F:F,D63,AI:AI,TRUE)` |
| D64 | Romanticism | (label) |
| E64 | | `=COUNTIFS(F:F,D64,AI:AI,TRUE)` |
| D65 | Pre-Raphaelite | (label) |
| E65 | | `=COUNTIFS(F:F,D65,AI:AI,TRUE)` |
| D66 | Imagism | (label) |
| E66 | | `=COUNTIFS(F:F,D66,AI:AI,TRUE)` |
| D67 | Modernism | (label) |
| E67 | | `=COUNTIFS(F:F,D67,AI:AI,TRUE)` |
| D68 | Harlem Renaissance | (label) |
| E68 | | `=COUNTIFS(F:F,D68,AI:AI,TRUE)` |
| D69 | Beat | (label) |
| E69 | | `=COUNTIFS(F:F,D69,AI:AI,TRUE)` |
| D70 | Confessional | (label) |
| E70 | | `=COUNTIFS(F:F,D70,AI:AI,TRUE)` |
| D71 | Black Arts | (label) |
| E71 | | `=COUNTIFS(F:F,D71,AI:AI,TRUE)` |
| D72 | Language Poetry | (label) |
| E72 | | `=COUNTIFS(F:F,D72,AI:AI,TRUE)` |

### Column G: Mode Counts

| Cell | Label | Formula |
|------|-------|---------|
| G59 | MODE | (header) |
| H59 | Count | (header) |
| G60 | Lyric | (label) |
| H60 | | `=COUNTIFS(H:H,G60,AI:AI,TRUE)` |
| G61 | Narrative | (label) |
| H61 | | `=COUNTIFS(H:H,G61,AI:AI,TRUE)` |
| G62 | Dramatic | (label) |
| H62 | | `=COUNTIFS(H:H,G62,AI:AI,TRUE)` |
| G63 | Mixed | (label) |
| H63 | | `=COUNTIFS(H:H,G63,AI:AI,TRUE)` |

### Column J: Stance Counts (with wildcards for compound stances)

| Cell | Label | Formula |
|------|-------|---------|
| J59 | STANCE | (header) |
| K59 | Count | (header) |
| J60 | Apostrophic | (label) |
| K60 | | `=COUNTIFS(K:K,"*Apostrophic*",AI:AI,TRUE)` |
| J61 | Meditative | (label) |
| K61 | | `=COUNTIFS(K:K,"*Meditative*",AI:AI,TRUE)` |
| J62 | Descriptive | (label) |
| K62 | | `=COUNTIFS(K:K,"*Descriptive*",AI:AI,TRUE)` |
| J63 | Argumentative | (label) |
| K63 | | `=COUNTIFS(K:K,"*Argumentative*",AI:AI,TRUE)` |
| J64 | Narrative | (label) |
| K64 | | `=COUNTIFS(K:K,"Narrative",AI:AI,TRUE)` |
| J65 | Satiric | (label) |
| K65 | | `=COUNTIFS(K:K,"Satiric",AI:AI,TRUE)` |
| J66 | Prophetic | (label) |
| K66 | | `=COUNTIFS(K:K,"*Prophetic*",AI:AI,TRUE)` |
| J67 | Ceremonial | (label) |
| K67 | | `=COUNTIFS(K:K,"*Ceremonial*",AI:AI,TRUE)` |

### Column M: Rhetorical Mode Counts

| Cell | Label | Formula |
|------|-------|---------|
| M59 | RHETORICAL_MODE | (header) |
| N59 | Count | (header) |
| M60 | Epideictic | (label) |
| N60 | | `=COUNTIFS(L:L,"Epideictic",AI:AI,TRUE)` |
| M61 | Deliberative | (label) |
| N61 | | `=COUNTIFS(L:L,"Deliberative",AI:AI,TRUE)` |
| M62 | Forensic | (label) |
| N62 | | `=COUNTIFS(L:L,"Forensic",AI:AI,TRUE)` |
| M63 | (blank) | (label) |
| N63 | | `=COUNTIFS(L:L,"",AI:AI,TRUE)` |

### Column P: Length Statistics

| Cell | Label | Formula |
|------|-------|---------|
| P59 | LENGTH STATISTICS | (header) |
| P60 | Total collected | (label) |
| Q60 | | `=COUNTIF(AI:AI,TRUE)` |
| P61 | Mean lines | (label) |
| Q61 | | `=AVERAGEIF(AI:AI,TRUE,AG:AG)` |
| P62 | Median lines | (label) |
| Q62 | | `=MEDIAN(IF(AI2:AI54=TRUE,AG2:AG54))` * |
| P63 | Min lines | (label) |
| Q63 | | `=MINIFS(AG:AG,AI:AI,TRUE)` |
| P64 | Max lines | (label) |
| Q64 | | `=MAXIFS(AG:AG,AI:AI,TRUE)` |
| P65 | Mean words | (label) |
| Q65 | | `=AVERAGEIF(AI:AI,TRUE,AH:AH)` |
| P66 | Median words | (label) |
| Q66 | | `=MEDIAN(IF(AI2:AI54=TRUE,AH2:AH54))` * |

\* For median formulas in Excel, enter as array formula with Ctrl+Shift+Enter
\* In Google Sheets, these work as regular formulas

## Column Reference (Updated with New Narratological Metadata)
- E = period
- F = literary_movement
- H = mode
- I = genre
- J = stanza_structure
- K = meter
- L = rhyme
- M = register
- N = stance
- O = rhetorical_mode
- P = rhetorical_genre
- Q = discursive_structure
- R = discourse_type
- S = diegetic_mimetic
- T = focalization
- U = person
- V = deictic_orientation
- W = address_mode
- X = addressee_type
- Y = deictic_object
- Z = temporal_orientation
- AA = temporal_structure
- AB = tradition
- AG = length_lines
- AH = length_words
- AI = collected (TRUE/FALSE)
- AJ = filename

## Notes
- All formulas only count rows where column AI (collected) = TRUE
- Formulas will automatically update as you add new poems
- Wildcard formulas (with asterisks) catch compound categories like "Apostrophic/Meditative"
- After adding 16 new narratological metadata columns, the collected column moved from T to AI
- Length columns are now at AG (length_lines) and AH (length_words)
