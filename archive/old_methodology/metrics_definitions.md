# Trajectory Metrics - Formal Definitions

**Project**: Semantic Trajectory Analysis of Poetry
**Last Updated**: 2025-01-23

---

## Overview

This document provides formal mathematical definitions of all trajectory metrics used in the analysis. All metrics operate on sequences of word embeddings extracted from texts.

---

## Notation

- Let **w₁, w₂, ..., wₙ** be the sequence of words in a text (poem, generated text, or prose)
- Let **v₁, v₂, ..., vₙ** be their corresponding embedding vectors in ℝᵈ (d=300 for Word2Vec)
- Let **cos(vᵢ, vⱼ)** denote cosine similarity between vectors vᵢ and vⱼ
- Let **d(vᵢ, vⱼ) = 1 - cos(vᵢ, vⱼ)** denote cosine distance

### Why Cosine Distance?
- Captures angular separation in high-dimensional space
- Invariant to vector magnitude (focuses on direction/meaning)
- Standard in distributional semantics (Mikolov et al., 2013)
- Range: [0, 2] where 0 = identical, 2 = opposite

---

## Core Trajectory Metrics

### 1. Semantic Path Length (SPL)

**Definition**: Total semantic distance traversed through the text

**Formula**:
```
SPL = Σᵢ₌₁ⁿ⁻¹ d(vᵢ, vᵢ₊₁)
    = Σᵢ₌₁ⁿ⁻¹ (1 - cos(vᵢ, vᵢ₊₁))
```

**Interpretation**:
- Measures cumulative semantic change
- Higher values = more semantic movement
- Independent of direction (always positive)

**Theoretical motivation**:
- Captures the "exploratory" dimension of poetic meaning-making
- High SPL suggests traversing distant semantic domains

**Prediction**:
- **Poetry**: Moderate to high (explores semantic space)
- **LLM poetry**: Low (stays safe) OR very high (random jumping)
- **Prose**: Low to moderate (conventional progression)

---

### 2. Net Semantic Displacement (NSD)

**Definition**: Direct semantic distance from beginning to end

**Formula**:
```
NSD = d(v₁, vₙ)
    = 1 - cos(v₁, vₙ)
```

**Interpretation**:
- Measures how far meaning has moved from start to finish
- Ignores the path taken, only endpoints matter
- Range: [0, 2]

**Theoretical motivation**:
- Captures overall semantic change/development
- Low NSD = circular/returning structure
- High NSD = linear progression to distant meaning

**Prediction**:
- **Poetry**: Variable (some circular, some progressive)
- **Prose**: Moderate (topical development)

---

### 3. Tortuosity (T)

**Definition**: Ratio of path length to net displacement

**Formula**:
```
T = SPL / NSD

(Note: Undefined if NSD = 0; in practice use T = SPL / max(NSD, ε) for small ε)
```

**Interpretation**:
- T ≈ 1: Straight semantic path (direct progression)
- T >> 1: Winding, exploratory path
- Measures how much "wandering" occurs relative to overall displacement

**Theoretical motivation**:
- **Core metric for integration hypothesis**
- High tortuosity = exploring disparate domains while maintaining coherence
- Operationalizes "creating wholes from disparate fragments"

**Prediction**:
- **Poetry**: High (explores but integrates)
- **LLM poetry**: Low (too direct) OR undefined (random, no coherence)
- **Prose**: Low to moderate (efficient progression)

---

### 4. Return-to-Origin (RTO)

**Definition**: Semantic distance from end back to beginning

**Formula**:
```
RTO = d(vₙ, v₁)
    = 1 - cos(vₙ, v₁)
```

**Note**: RTO = NSD (same calculation), but conceptually frames the ending's relationship to the beginning

**Interpretation**:
- Low RTO: Circular structure, ending echoes beginning
- High RTO: Linear structure, ending distant from beginning

**Theoretical motivation**:
- Many poems exhibit circular/return structure
- Imagist poetry especially (e.g., H.D.'s "Oread" - ocean/forest integration)
- Tests whether LLMs can create coherent closure

**Prediction**:
- **Poetry**: Often low (return/echo structure)
- **LLM poetry**: Random (no structural awareness)
- **Prose**: Higher (narrative progression)

---

### 5. Exploration Radius (ER)

**Definition**: Average distance of all words from the semantic centroid

**Formula**:
```
Let c = (1/n) Σᵢ₌₁ⁿ vᵢ  (centroid of all embeddings)

ER = (1/n) Σᵢ₌₁ⁿ d(vᵢ, c)
```

**Interpretation**:
- Measures how "spread out" the semantic space is
- High ER = words span diverse semantic regions
- Low ER = words cluster tightly

**Theoretical motivation**:
- Operationalizes "disparate fragments"
- Should correlate with semantic dispersion
- Complements path-based metrics

**Prediction**:
- **Poetry**: High (diverse vocabulary, distant domains)
- **LLM poetry**: Low (safe, conventional collocations)
- **Prose**: Moderate

---

### 6. Velocity Profile Variance (VPV)

**Definition**: Variance in step-by-step semantic velocity

**Formula**:
```
Let δᵢ = d(vᵢ, vᵢ₊₁) for i = 1, ..., n-1  (step distances)

Let μ_δ = (1/(n-1)) Σᵢ δᵢ  (mean step distance)

VPV = (1/(n-1)) Σᵢ (δᵢ - μ_δ)²
```

**Interpretation**:
- Low VPV: Smooth, regular semantic progression
- High VPV: Alternating fast/slow movement, jumpy

**Theoretical motivation**:
- Real poetry should have controlled variation (deliberate pacing)
- Random text has high variance (no control)
- Conventional text has low variance (predictable)

**Prediction**:
- **Poetry**: Moderate (varied but controlled)
- **LLM poetry**: Low (too smooth) OR very high (random)
- **Prose**: Low (smooth progression)

---

### 7. Directional Consistency (DC)

**Definition**: Measures how often the trajectory changes direction in semantic space

**Formula** (after PCA projection to 2D or 3D):
```
For sequential points p₁, p₂, ..., pₙ in ℝᵏ (k=2 or 3):

Let θᵢ = angle between vectors (pᵢ₊₁ - pᵢ) and (pᵢ₊₂ - pᵢ₊₁)

DC = (1/(n-2)) Σᵢ₌₁ⁿ⁻² cos(θᵢ)
```

**Interpretation**:
- DC ≈ 1: Consistent direction (straight path)
- DC ≈ 0: Frequent perpendicular turns
- DC ≈ -1: Frequent reversals

**Theoretical motivation**:
- Captures structural coherence of semantic journey
- Poems might have deliberate directional patterns

**Note**: Requires dimensionality reduction (PCA) first, so is representation-dependent

---

## Derived Metrics

### Integration Index (II)

**Definition**: Ratio of exploration to displacement (related to tortuosity)

**Formula**:
```
II = ER / NSD
```

**Interpretation**:
- High II: Explores widely but returns/integrates
- Operationalizes "integration of disparate elements"

---

## Length Normalization

**Issue**: Longer texts naturally have higher SPL

**Solutions**:
1. **Normalize by length**: SPL_norm = SPL / (n-1)
   - Yields average step distance

2. **Control for length**: Include text length as covariate in statistical models

3. **Match lengths**: Compare poems of similar length

**Decision**: TBD based on corpus characteristics

---

## Implementation Notes

### Handling Missing Words
- Some words may not exist in embedding model vocabulary
- Options:
  1. Skip missing words (reduces n)
  2. Use average of surrounding words
  3. Use subword embeddings (FastText)

**Current approach**: Skip missing words, document proportion missing per text

### Dimensionality Reduction
- Some metrics (e.g., DC) require lower-dimensional representation
- Use PCA to project 300D → 2D or 3D
- Document variance explained by components

### Statistical Considerations
- SPL, ER are extensive (scale with length) → normalize
- T, RTO, DC are intensive (length-independent) → use directly
- Check distributions for normality before parametric tests

---

## Validation

### Sanity Checks
- Random word sequences should show high SPL, high VPV, low DC
- Repeated words should show SPL ≈ 0, T undefined
- Prose should show lower T than poetry

### Correlation Structure
- Expect SPL and ER to correlate (both measure dispersion)
- T should be relatively independent of length (ratio metric)

---

## Future Extensions

### Potential Additional Metrics
- **Fractal dimension**: Measure self-similarity at different scales
- **Entropy**: Information-theoretic measure of trajectory complexity
- **Alignment with topic models**: How much does trajectory follow topic structure?
- **Return frequency**: How often does trajectory revisit semantic neighborhoods?

### Multi-scale Analysis
- Calculate metrics at different granularities (word, line, stanza)
- Compare local vs. global trajectory properties

---

## References

- Mikolov et al. (2013) - Word2Vec and cosine distance
- Turbulence/fluid dynamics literature - tortuosity metric
- Network science - path-based metrics
- (To be expanded with relevant computational linguistics papers)
