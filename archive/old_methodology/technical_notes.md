# Technical Implementation Notes

**Project**: Semantic Trajectory Analysis of Poetry
**Last Updated**: 2025-01-23

---

## Development Environment

### Current Setup
- **Platform**: macOS (Darwin 25.0.0)
- **Python**: 3.x (version TBD)
- **Jupyter**: Notebook format (.ipynb)
- **Storage**: OneDrive cloud sync

### Key Libraries
- `gensim`: Word embedding models (Word2Vec, etc.)
- `scikit-learn`: Cosine similarity, PCA, statistical tools
- `numpy`: Numerical computing
- `matplotlib`: Visualization
- `transformers`: (Future) For BERT/contextual embeddings

---

## Existing Codebase

### "Oread in Vector Space" Notebook
**Location**: `/Users/justin/Library/CloudStorage/OneDrive-Personal/Academic & Research/Articles/2025/AI Project/Oread in Vector Space`

**Current Capabilities**:
- Loads Word2Vec Google News 300 model via `gensim.downloader`
- Extracts word embeddings for poem vocabulary
- Calculates pairwise cosine similarity matrix
- Performs PCA dimensionality reduction (300D → 2D)
- Thematic categorization (ocean vs. forest)
- Heatmap and scatter plot visualizations

**Size**: 437KB (47 cells total: 18 code, 29 markdown)

**Structure**:
- Task description and methodology
- Sequential implementation with explanations
- 10 presentation slides covering each step
- Summary and future directions

**Known Issues**:
- File too large to read in one pass (exceeds 256KB limit)
- Need to handle via offset/limit or grep for specific content

---

## Planned Extensions

### Phase 1: Sequential Analysis (Extend Oread Notebook)
**Goal**: Add trajectory analysis to existing single-poem workflow

**Tasks**:
1. Maintain word order (currently unordered vocabulary)
2. Extract sequential embeddings
3. Implement basic metrics (SPL, NSD, T)
4. Visualize trajectory in 2D PCA space
5. Validate on "Oread" as proof of concept

**Challenges**:
- Tokenization: Need to preserve word order from original poem
- Punctuation handling: Strip or keep?
- Line breaks: Preserve structure or treat as continuous?

### Phase 2: Multi-Poem Pipeline
**Goal**: Scale to corpus of 30-50 poems

**Tasks**:
1. Batch processing for multiple texts
2. Store results in structured format (DataFrame)
3. Statistical comparison framework
4. Automated visualization generation

**Design Decisions**:
- Modular functions vs. class-based architecture?
- In-memory vs. persistent storage for embeddings?
- Parallel processing for large corpus?

### Phase 3: LLM Generation
**Goal**: Generate comparison poems from GPT-4, Claude, etc.

**Tasks**:
1. API integration (OpenAI, Anthropic)
2. Prompt engineering for generation
3. Batch generation with error handling
4. Cost management (API calls can be expensive)

**Considerations**:
- Rate limiting
- Reproducibility (temperature, seed parameters)
- Storage of generated texts

---

## Data Structures

### Text Representation
```python
{
    'title': str,           # Poem title
    'author': str,          # Poet name
    'text': str,            # Full text
    'words': List[str],     # Ordered word sequence (tokenized)
    'embeddings': np.ndarray,  # Shape: (n_words, 300)
    'metadata': {
        'period': str,      # Literary period
        'genre': str,       # Genre/style
        'length': int,      # Number of words
        'source': str       # Real, GPT-4, Claude, etc.
    }
}
```

### Trajectory Metrics Output
```python
{
    'text_id': str,
    'spl': float,           # Semantic Path Length
    'nsd': float,           # Net Semantic Displacement
    'tortuosity': float,    # T = SPL / NSD
    'rto': float,           # Return-to-Origin
    'exploration_radius': float,  # ER
    'velocity_variance': float,   # VPV
    'directional_consistency': float,  # DC (after PCA)
    'pca_variance_explained': List[float],  # For 2D projection
    'num_words': int,
    'num_missing': int,     # Words not in embedding vocabulary
    'pct_missing': float
}
```

---

## Embedding Model Details

### Word2Vec Google News 300

**Specifications**:
- Dimensionality: 300
- Training corpus: Google News (~100B words)
- Vocabulary size: ~3M words
- Architecture: Continuous Bag of Words (CBOW)

**Loading**:
```python
import gensim.downloader as api
model = api.load('word2vec-google-news-300')
```

**Pros**:
- Pre-trained, no training needed
- Large vocabulary
- Standard baseline in NLP

**Cons**:
- Trained on news (may miss poetic/archaic vocabulary)
- Static embeddings (one vector per word type)
- Large file size (~1.6GB)

**Missing Words Strategy**:
- Track proportion of missing words per text
- Report in supplementary materials
- If >20% missing, may exclude text or try alternative model

### Future Models

**GloVe (Global Vectors)**:
- Trained on Wikipedia + Gigaword or Common Crawl
- Different training objective than Word2Vec
- Allows comparison of corpus effects

**FastText**:
- Subword embeddings (handles unknown words better)
- Useful for morphologically complex words
- May capture poetic neologisms

**BERT (Contextual)**:
- Context-dependent representations
- Each token gets unique embedding based on context
- Much more computationally expensive
- Useful for polysemy analysis (future work)

---

## Preprocessing Decisions

### Tokenization
**Options**:
1. Simple whitespace split + lowercase
2. NLTK word_tokenize
3. spaCy tokenization

**Decision**: TBD based on corpus characteristics

**Considerations**:
- Preserve contractions? ("don't" vs. "do not")
- Handle hyphenated words? ("sea-green")
- Poetic line breaks as tokens?

### Stopwords
**Question**: Remove stopwords (the, a, of, etc.)?

**Arguments for removal**:
- Reduce noise from function words
- Focus on content words

**Arguments against**:
- Stopwords carry grammatical/structural information
- Removal may distort trajectory
- Distributional models handle stopwords naturally

**Current decision**: Keep all words, analyze with/without as robustness check

### Punctuation
**Decision**: Strip punctuation

**Rationale**:
- Punctuation not in embedding vocabulary
- Preserves word boundaries

---

## Visualization Strategy

### Trajectory Plots
**2D PCA projection**:
- Plot word embeddings as points in 2D
- Connect with arrows showing sequence
- Color-code by source (real/generated/prose)
- Annotate first/last words

**Example code structure**:
```python
# Reduce to 2D
pca = PCA(n_components=2)
coords_2d = pca.fit_transform(embeddings)

# Plot trajectory
plt.figure(figsize=(10, 8))
plt.plot(coords_2d[:, 0], coords_2d[:, 1], 'o-', alpha=0.6)
plt.scatter(coords_2d[0, 0], coords_2d[0, 1], c='green', s=100, label='Start')
plt.scatter(coords_2d[-1, 0], coords_2d[-1, 1], c='red', s=100, label='End')
# Add word labels...
```

### Metric Distributions
**Violin plots or box plots**:
- Compare metric distributions across text types
- Show median, quartiles, outliers
- Statistical significance markers

### Heatmaps
**Similarity matrices**:
- Already implemented in Oread notebook
- Useful for showing semantic clustering

---

## Statistical Analysis Plan

### Comparisons
1. **Real vs. Generated**: Primary comparison (t-test or Mann-Whitney)
2. **Real vs. Prose**: Shows poetry is distinctive
3. **Generated (GPT-4) vs. Generated (Claude)**: Do models fail similarly?

### Multiple Comparisons
- Bonferroni or FDR correction if testing many metrics
- Or frame as exploratory with effect sizes

### Effect Sizes
- Cohen's d for all comparisons
- Interpret: small (0.2), medium (0.5), large (0.8)

### Regression
- Predict text type from trajectory metrics
- Logistic regression: Real vs. Generated
- Shows which metrics best discriminate

---

## Computational Efficiency

### Current Bottlenecks (Anticipated)
1. **Embedding extraction**: O(n) per text, but model loading is one-time
2. **Pairwise distances**: O(n²) for similarity matrices (not needed for trajectory)
3. **PCA**: O(n * d²) where d=300, but fast for typical n

### Optimization Strategies
- **Vectorization**: Use numpy operations, avoid Python loops
- **Caching**: Save computed embeddings to disk
- **Batch processing**: Process multiple texts in parallel

### Storage
- Embeddings: 300 * 8 bytes = 2.4KB per word
- 50 poems * 100 words avg = 12MB total (manageable)

---

## Reproducibility

### Version Control
- **Code**: Jupyter notebooks (currently manual versioning via OneDrive)
- **Future**: Consider git repository for version tracking

### Random Seeds
- Set seeds for:
  - PCA (if randomized solver)
  - LLM generation (for reproducibility)
  - Train/test splits (if applicable)

### Documentation
- Maintain this file + methods_log.md
- Inline comments in code
- Markdown explanations in notebook cells

---

## Error Handling

### Missing Words
```python
def get_embeddings_safe(words, model):
    embeddings = []
    valid_words = []
    for word in words:
        try:
            embeddings.append(model[word])
            valid_words.append(word)
        except KeyError:
            # Word not in vocabulary
            pass
    return np.array(embeddings), valid_words
```

### Edge Cases
- Poems with <10 words: Exclude or flag
- All words missing: Skip text, log error
- NSD = 0: Handle division by zero in tortuosity

---

## API Integration (Future)

### OpenAI
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    n=10  # Generate 10 samples
)
```

### Anthropic (Claude)
```python
import anthropic

client = anthropic.Client(api_key=API_KEY)
response = client.messages.create(
    model="claude-3-5-sonnet-20250129",
    max_tokens=500,
    messages=[{"role": "user", "content": prompt}]
)
```

### Cost Estimation
- GPT-4: ~$0.03 per 1K tokens
- 50 poems * 10 samples * 200 tokens = 100K tokens = ~$3
- Manageable budget

---

## Testing Strategy

### Unit Tests (Future)
- Test metric calculations on toy examples
- Verify known properties (e.g., T=1 for straight line)

### Validation
- Compare to hand-calculated examples
- Sanity checks (random text should have high variance)

---

## Next Implementation Steps

1. **Read and parse Oread notebook** to understand current structure
2. **Implement sequential word extraction** from poem text
3. **Code trajectory metrics** (start with SPL, NSD, T)
4. **Visualize trajectory** for Oread as proof of concept
5. **Prototype on 5-10 poems** before scaling to full corpus

---

## Open Technical Questions

- [ ] How to handle line breaks in poems? (Structure vs. continuous text)
- [ ] Best way to structure modular code? (Functions vs. classes)
- [ ] Where to store generated LLM poems? (Database, flat files, notebook)
- [ ] Parallel processing worth the complexity for corpus this size?
- [ ] Should we implement caching for embeddings?

---

## Performance Benchmarks (TBD)

Will track:
- Time to extract embeddings per text
- Time to calculate all metrics per text
- Total runtime for corpus
- Memory usage

Target: <1 minute per poem for full analysis
