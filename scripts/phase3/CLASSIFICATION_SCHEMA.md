# Poetry Classification Schema - 28 Fields

## CRITICAL: Use EXACTLY these 28 fields for every poem

Based on training data format from `training_set_456_poems.csv`

### HISTORICAL (2 fields)
1. **period** - e.g., "Tudor", "Romantic", "Modern", "Contemporary"
2. **literary_movement** - e.g., "Romanticism", "Modernism", "Postmodernism"

### RHETORICAL (14 fields)
3. **register** - e.g., "Meditative", "Confessional", "Descriptive", "Epic"
4. **rhetorical_genre** - e.g., "Epideictic", "Deliberative", "Judicial"
5. **discursive_structure** - e.g., "Monologic", "Dialogic", "Fragmented"
6. **discourse_type** - e.g., "Description", "Narration", "Argument", "Exposition"
7. **narrative_level** - e.g., "First person", "Third person", "Second person"
8. **diegetic_mimetic** - e.g., "Diegetic", "Mimetic", "Non-diegetic", "Mixed"
9. **focalization** - e.g., "First person internal", "Omniscient", "External", "Zero"
10. **person** - e.g., "1st", "2nd", "3rd", "Speaker"
11. **deictic_orientation** - e.g., "Subjective", "Impersonal", "Direct address", "Anaphoric"
12. **addressee_type** - e.g., "Addressed", "Unaddressed", "Implied", "Self"
13. **deictic_object** - What is being pointed to/referenced
14. **temporal_orientation** - e.g., "Present", "Past", "Future", "Atemporal", "Gnomic present"
15. **temporal_structure** - e.g., "Linear", "Static", "Cyclical", "Sequential", "Fragmented"
16. **tradition** - e.g., "Petrarchan", "Oral", "Folk", "Contemporary American"

### FORMAL (5 fields)
17. **mode** - e.g., "Lyric", "Narrative", "Dramatic", "Didactic", "Descriptive"
18. **genre** - e.g., "Sonnet", "Epic", "Ballad", "Elegy", "Free verse lyric"
19. **stanza_structure** - e.g., "Quatrains", "Couplets", "Tercets", "Irregular", "Octaves"
20. **meter** - e.g., "Iambic pentameter", "Free verse", "Alliterative", "Folk meter"
21. **rhyme** - e.g., "ABAB", "AABB", "None", "Sonnet rhyme", "Irregular"

## Additional Metadata (NOT classification fields)
- poem_id
- filename (optional)
- global_index (optional)

## OUTPUT FORMAT

```json
{
  "poem_id": "000001",
  "period": "Tudor",
  "literary_movement": "Renaissance",
  "register": "Meditative",
  "rhetorical_genre": "Epideictic",
  "discursive_structure": "Monologic",
  "discourse_type": "Description",
  "narrative_level": "Third person",
  "diegetic_mimetic": "Mimetic",
  "focalization": "Zero",
  "person": "3rd",
  "deictic_orientation": "Impersonal",
  "addressee_type": "Unaddressed",
  "deictic_object": "The things/quiet life",
  "temporal_orientation": "Atemporal",
  "temporal_structure": "Static",
  "tradition": "Translation (Martial)",
  "mode": "Lyric",
  "genre": "Lyric",
  "stanza_structure": "Couplets",
  "meter": "Iambic pentameter",
  "rhyme": "AABB"
}
```

## CRITICAL RULES

1. **NEVER** use thematic tags (death_theme, nature_imagery, etc.)
2. **NEVER** use only 2 fields (narrative_level, formalism_score)
3. **ALWAYS** include all 28 fields
4. Use "N/A" or appropriate descriptor if field doesn't apply
5. Be consistent with existing training data vocabulary

## Verification

Before saving, check:
- [ ] Exactly 28 classification fields present
- [ ] No extra fields (length, tone, death_theme, etc.)
- [ ] All values are descriptive strings, not scores
- [ ] Format matches training data examples
