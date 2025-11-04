# Methods Log - Semantic Trajectory Analysis of Poetry

**Project**: Poetic Meaning and the Limits of Distributional Semantics
**Last Updated**: 2025-01-23
**Status**: Initial planning and design phase

---

## Project Overview

### Research Questions
1. Do poems create distinctive semantic trajectories through embedding space?
2. Can LLMs reproduce these trajectories when generating poetry?
3. What does trajectory analysis reveal about the limits of distributional semantics?

### Core Hypotheses

**Hypothesis 1 (Semantic Integration)**:
Poetic language creates "sensuous wholes from disparate fragments of experience" - operates through integration of distant conceptual domains.

**Operationalized as:**
Real poems exhibit a distinctive pattern in distributional-semantic space:
- HIGH DISPERSION: Explore distant semantic domains (high semantic path length, exploration radius)
- + HIGH INTEGRATION: Maintain coherent structure (return-to-origin, controlled tortuosity, directional consistency)

**Contrasted with:**
- LLM-generated poems fail to reproduce this pattern, showing either:
  - Mode A: Low dispersion (safe, conventional semantic progressions)
  - Mode B: Dispersion without integration (random jumping, incoherent structure)

**Hypothesis 2 (Embodied Enactment)** [Future work]:
Poetry, when embodied through recitation, enacts physical concomitants of emotion at the level of the phoneme.

**Current Focus**: Testing Hypothesis 1 through trajectory analysis

---

### What We Mean By "Semantic" and "Meaning"

**Terminology precision:**

When we use "semantic trajectory" or "semantic structure," we refer specifically to **distributional-semantic relationships** - how words relate to each other based on co-occurrence patterns in a training corpus (Word2Vec trained on Google News).

**What this captures:**
- Lexical-semantic relations (synonymy, antonymy, hypernymy)
- Topical coherence (words about similar domains cluster together)
- Conceptual associations encoded in linguistic usage patterns
- Statistical regularities in how words appear in similar contexts

**What this does NOT capture:**
- Context-dependent interpretation (how "green" means differently in different poems)
- Figurative/metaphoric meaning that violates distributional expectations
- Embodied/phenomenological experience (the sensory "what it's like")
- Authorial intention or reader response
- Pragmatic/indexical meaning ("I," "here," "this")

**Theoretical positioning:**

We are testing whether **distributional semantics** - the claim that meaning = distribution across linguistic contexts (Firth 1957; Harris 1954) - can account for poetic meaning-making.

**Our hypothesis:** Distributional structure is NECESSARY but INSUFFICIENT for poetic meaning.

**Evidence strategy:**
1. Show poetry creates distinctive distributional patterns (trajectory analysis)
2. Show LLMs (which excel at distributional patterns) cannot reproduce these patterns
3. Conclude: Poetic meaning operates through mechanisms beyond pure distribution
4. Point toward embodied/performative dimensions (H2) as what's missing

**Methodological framing:**

"We do not claim to track 'meaning' in the full phenomenological or interpretive sense. Rather, we examine one level of semantic organization - distributional structure - and demonstrate both its distinctive properties in poetry AND its limits. The failure of LLMs to reproduce poetic trajectories, despite their mastery of distributional regularities, suggests that poetry operates through mechanisms beyond what distributional semantics can capture. This motivates our second hypothesis about embodied, articulatory dimensions of poetic performance."

---

## Session 1: 2025-01-23 - Project Scoping

### Strategic Decisions

**Narrowed scope to Approach #4 (Trajectory Analysis)**
- Initially considered four approaches:
  1. Generation quality (static dispersion+integration metrics)
  2. Perplexity/surprisal
  3. Completion/continuation tasks
  4. Embedding space trajectory analysis

- **Decision**: Focus exclusively on #4 (trajectory analysis)
- **Rationale**:
  - Most novel contribution
  - Naturally incorporates static metrics as byproducts
  - Better narrative (dynamic > static)
  - Computationally tractable extension of existing Oread notebook

**Target Venues Identified**
- Primary: *Cognitive Science*
- Alternative: *Digital Scholarship in the Humanities*
- Framing: Using poetry as test case for conceptual blending theory and limits of distributional semantics

**Theoretical Positioning**
- Explicitly avoiding imitative form fallacy
- Not claiming: "sounds imitate emotions" (mimesis)
- Claiming: Cognitive mechanisms of semantic integration + embodied articulation (motivated but non-mimetic)
- Grounded in: Conceptual Blending Theory (Fauconnier & Turner), Embodied Cognition (Lakoff & Johnson)

### Corpus Planning

**Initial Parameters** (to be refined):
- N = 30-50 poems
- Canonical/high-quality poems across periods and styles
- Include prose controls (matched for length/vocabulary)
- Generate LLM poems for comparison (GPT-4, Claude, etc.)

**Selection Criteria** (TBD):
- Sufficient length for trajectory analysis
- Diverse content (avoid confound of topic with structure)
- Canonical status (ensures quality)
- Period/genre balance

### Comparison Framework

**Three-way comparison**:
1. Real canonical poems
2. LLM-generated poems (multiple models)
3. Prose controls

**Detailed Predictions**:

**Real canonical poems:**
- High Semantic Path Length (SPL) - explores distant semantic domains
- High Tortuosity (T) - winding, exploratory paths
- High Exploration Radius (ER) - words span diverse semantic regions
- Low Return-to-Origin (RTO) - circular/echo structure
- Moderate Velocity Variance (VPV) - controlled pacing, not random
- Moderate-to-high Directional Consistency (DC) - coherent trajectory despite exploration
- **KEY PATTERN**: High dispersion + high integration

**LLM-generated poems (Mode A - "Playing it safe"):**
- Low SPL - stays in conventional semantic neighborhoods
- Low T - direct, predictable progressions
- Low ER - tight clustering around conventional collocations
- Low RTO (but trivially - just boring)
- Low VPV - smooth but uninteresting
- **PATTERN**: Low dispersion, conventional

**LLM-generated poems (Mode B - "Random jumping"):**
- High SPL - jumps between distant domains
- Undefined or very high T - erratic, no coherent path
- High ER - scattered
- High RTO - no return structure
- Very high VPV - random, uncontrolled velocity
- Low DC - frequent direction changes, incoherent
- **PATTERN**: Dispersion without integration

**Prose controls:**
- Moderate SPL - topical development without poetic exploration
- Low-to-moderate T - efficient progression
- Moderate ER - some semantic range but conventional
- Variable RTO - depends on genre (narrative vs. expository)
- Low VPV - smooth, linear development
- **PATTERN**: Conventional semantic progression

**Critical discriminating metric: Tortuosity**
- Real poems should occupy a distinctive region: High T + Low RTO (exploratory but integrated)
- LLMs will fail to occupy this region (either too low T or high T without integration)

**Statistical predictions:**
- ANOVA across groups (Real, LLM-A, LLM-B, Prose): Significant main effect, p < 0.05
- Post-hoc comparisons: Real poems differ from all other groups on tortuosity and SPL×RTO interaction
- Effect sizes: Cohen's d > 0.8 (large) for key comparisons
- Multivariate analysis (PCA on all metrics): Real poems cluster distinctively

---

## Technical Infrastructure

### Existing Resources
- Proof-of-concept notebook: "Oread in Vector Space"
- Analyzes H.D.'s "Oread" using Word2Vec embeddings
- Demonstrates: vocabulary extraction, embedding retrieval, PCA visualization, thematic categorization

### Planned Extensions
- Add sequential/temporal analysis
- Implement trajectory metrics
- Scale to multiple poems
- Add LLM generation pipeline
- Statistical comparison framework

### Embedding Models
**Initial**: Word2Vec Google News 300
- Rationale: Pre-trained, widely used, 300-dim captures nuance
- Already implemented in Oread notebook

**Future additions**:
- GloVe (for robustness check, different training corpus)
- Possibly FastText (subword embeddings)
- Consider BERT for contextual comparison (later phase)

---

## Documentation Strategy

### Structure
- `methods_log.md` (this file): Chronological decision log
- `metrics_definitions.md`: Formal mathematical definitions
- `technical_notes.md`: Implementation details, code decisions
- Main notebook: Literate programming style with rich markdown

### Update Protocol
- Document decisions as they're made
- Include rationale for methodological choices
- Track what didn't work and why
- Maintain reproducibility focus

---

## Session 2: 2025-01-23 - Corpus Finalized

### Corpus Selection Complete

**Final corpus: 53 canonical poems** (documented in `corpus_list.md`)

**Coverage achieved**:
- **Historical range**: Renaissance (16th C) through Contemporary (21st C)
  - Renaissance/Early Modern: 7 poems
  - 17th Century: 5 poems
  - Restoration/18th C: 5 poems
  - Romantic: 7 poems
  - Victorian: 6 poems
  - Modernist: 5 poems
  - Mid-20th C: 7 poems
  - Contemporary: 11 poems

- **Demographic diversity**:
  - Gender: ~21 female, ~32 male poets
  - Race: 10+ Black/African American poets, South Asian representation
  - Includes historically marginalized voices (Wheatley, Lanyer, Cavendish)

- **Form variety**:
  - Fixed forms: Sonnets, odes, elegies, dramatic monologues, ballads
  - Free verse and experimental modernist work
  - Very short (2 lines - Pound) to very long (Coleridge, Ginsberg, Milton)

- **Stylistic movements**:
  - Imagist (H.D., Pound)
  - Romantic (Wordsworth, Keats, Shelley, Byron)
  - Victorian (Tennyson, Browning)
  - Modernist (Eliot, Yeats, Moore)
  - Beat (Ginsberg)
  - Confessional (Plath, Sexton, Lowell)
  - Black Arts Movement (Baraka, Brooks)
  - Contemporary experimental (Howe)

**Rationale for size (53 vs. 30-50)**:
- Slightly larger than initial target to ensure robust statistical power
- Includes representation across all major periods
- Allows for potential exclusions (e.g., if extremely long poems like "Howl" or "Ancient Mariner" prove problematic for analysis)
- Sufficient diversity to test generalizability

**Key corpus characteristics**:
- All poems are canonical (widely anthologized, critically recognized)
- Broad thematic coverage: nature, love, death, identity, politics, art, spirituality
- Length variation will require normalization strategies
- Expect varying rates of missing words (archaic vocabulary in older texts)

### Documentation Created
- `corpus_list.md`: Complete listing with metadata, period breakdown, thematic coverage
- Identified need for structured data collection (clean texts + metadata CSV)

## Open Questions / Decisions Needed

### Corpus
- [x] Finalize N poems (30? 50?) → **RESOLVED: 53 poems**
- [x] Define specific inclusion criteria → **RESOLVED: See corpus_list.md**
- [x] Select specific poems vs. sampling strategy → **RESOLVED: Curated canonical selection**
- [ ] How to select/generate prose controls?
- [ ] Obtain clean text files for all 53 poems
- [ ] Create metadata CSV with all fields (author, date, period, form, length, etc.)

### LLM Generation
- [ ] Which models? (GPT-4, Claude 3.5, Gemini?)
- [ ] How many samples per poem? (5-10?)
- [ ] Prompt strategy: style imitation vs. topic matching?
- [ ] Temperature/sampling parameters?

### Metrics
- [ ] Finalize trajectory metric definitions
- [ ] Which metrics are most theoretically motivated?
- [ ] How to handle poems of different lengths?

### Analysis
- [ ] Statistical tests for comparison?
- [ ] Multiple comparison corrections needed?
- [ ] Effect size measures?

---

## Next Steps

1. Define formal trajectory metrics
2. Extend Oread notebook with sequential analysis
3. Begin corpus curation
4. Prototype trajectory visualization
5. Design LLM generation protocol

---

## References to Integrate

- Fauconnier & Turner - Conceptual Blending Theory
- Lakoff & Johnson - Conceptual Metaphor Theory, Embodied Cognition
- Motor theory of speech perception (for H2)
- Previous work on computational poetry analysis
- LLM capabilities/limitations literature

---

## Notes for Methods Section

When writing up, emphasize:
1. Poetry as **extreme test case** for semantic composition theories
2. Trajectory analysis captures **dynamic process**, not just static properties
3. Computational operationalization of conceptual blending
4. Clear predictions distinguishing real vs. generated vs. prose
5. This tests **mechanisms** (how poetry works), not just **patterns** (what it looks like)
