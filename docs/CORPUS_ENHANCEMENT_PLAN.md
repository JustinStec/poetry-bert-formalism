# Corpus Enhancement & Database Implementation Plan

**Project**: Poetry Hierarchical BERT
**Corpus Size**: 116,675 unique poems
**Approach**: Iterative, quality-focused enhancement with local M4 Max ML

---

## Overview

Transform the cleaned poetry corpus into a research-grade dataset with rich metadata across multiple dimensions: bibliographic, historical, formal/prosodic, and rhetorical. Build production PostgreSQL database for efficient querying and future BERT training work.

### Philosophy
- Quality over speed (no artificial deadlines)
- Iterative development with M4 Max + Claude Code collaboration
- Local LLM fine-tuning for classification tasks
- Build robust, reusable tools progressively

---

## Current State

**Corpus Status**:
- Files on disk: 118,535 poems
- Unique poems in CSV: 116,675 poems
- Duplicates: 1,860 files (correctly identified by MD5 hash)
- Poem IDs: Non-sequential (62,281 → 185,485 with gaps)
- Basic metadata: poem_id, title, author, date, source, filepath, lines, words, content_hash

**Infrastructure**:
- M4 Max MacBook Pro for local training/fine-tuning
- Professional Python package structure (`src/poetry_bert/`)
- Existing prosodic analysis code (`src/poetry_bert/features/prosodic.py`)
- 52 gold-standard annotated poems (old metadata system)

---

## Six-Phase Implementation Plan

### **Phase 1: Foundation - Corpus Cleanup & Sequential Renumbering**

#### Goals:
1. Remove 1,860 duplicate files from disk
2. Renumber all poems sequentially (1 → 116,675, no gaps)
3. Perfect alignment: files ↔ CSV ↔ future database

#### Tasks:

**1.1 Remove Duplicates**
- Delete 1,860 duplicate files (same content_hash)
- Fix author name variants:
  - "OReilly, John Boyle" → "Reilly, John Boyle O" (67 poems)
  - "Maeterlin, Maurice" → "Maeterlinck, Maurice" (47 poems)
  - "Hafiz, Shams al-Din" / "Shirazi, Hafez" → standardize (39 poems)
  - "Sr, Giles Fletcher" / "Fletcher, Phineas" → resolve (49 poems)
- Delete 13 empty files
- Result: 116,675 files = 116,675 CSV entries

**1.2 Sequential Renumbering**
- Generate new sequential poem_ids (1 → 116,675)
- Rename all files: `{poem_id:06d}_{title}_{author}_{date}.txt`
  - Example: `000001_On_a_Quiet_Conscience_1_King_Charles_unknown.txt`
- Update CSV with new poem_ids
- Preserve all content_hash integrity

**1.3 Validation**
- Verify file count = CSV count = 116,675
- Confirm all content_hashes unique
- Test filename parsing
- Verify no broken file references

#### Scripts to Create:
- `scripts/cleanup_duplicates.py` - Remove duplicates, merge author variants
- `scripts/renumber_corpus.py` - Sequential ID assignment + file renaming
- `scripts/validate_corpus.py` - Comprehensive validation suite

#### Deliverable:
Clean, sequentially-numbered corpus with perfect file/CSV alignment

---

### **Phase 2: Tier 1 Metadata - Automated Basics**

#### Fields to Add (100% Automated):

| Field | Description | Source | Coverage |
|-------|-------------|--------|----------|
| `length_lines` | Number of lines in poem | Count from file | 100% |
| `length_words` | Number of words in poem | Count from file | 100% |
| `author_last` | Author's last name | Parse from author field | 100% |
| `year_approx` | Approximate year | Parse from date field | ~95% |
| `source_url` | Poetry Foundation URL | Generate where applicable | ~75% |
| `filename` | Standardized file reference | From filepath | 100% |

#### Implementation:
```python
def extract_basic_metadata(poem_file):
    """Extract automated metadata from poem file."""
    # Read file
    with open(poem_file) as f:
        content = f.read()

    # Count lines and words
    lines = len([l for l in content.split('\n') if l.strip()])
    words = len(content.split())

    # Parse filename: {id}_{title}_{author}_{date}.txt
    filename = poem_file.name
    parts = filename.replace('.txt', '').split('_')
    poem_id = int(parts[0])
    author = '_'.join(parts[-2:-1])
    date = parts[-1]

    # Parse author last name
    if ',' in author:
        author_last = author.split(',')[0].strip()
    else:
        author_last = author.split()[-1]

    # Parse year
    year_approx = parse_year(date)

    # Generate Poetry Foundation URL if applicable
    source_url = generate_pf_url(title, author) if source == 'poetry_platform' else None

    return {
        'length_lines': lines,
        'length_words': words,
        'author_last': author_last,
        'year_approx': year_approx,
        'source_url': source_url,
        'filename': filename
    }
```

#### Scripts to Create:
- `scripts/add_basic_metadata.py` - Scan corpus, extract/compute metadata
- Progress tracking and logging
- CSV update with new columns

#### Deliverable:
Enhanced CSV with ~16 total metadata fields for all 116,675 poems

---

### **Phase 3: Tier 2 Metadata - Historical Context (AI-Assisted)**

#### Fields to Add:

| Field | Description | Controlled Vocabulary | Target Coverage |
|-------|-------------|----------------------|----------------|
| `period` | Historical period | 12 categories | 70-80% |
| `literary_movement` | Literary movement | 13+ categories | 70-80% |
| `mode` | Poetic mode | 4 categories | 70-80% |

#### Controlled Vocabularies:

**Period (12 categories)**:
```
Tudor, Elizabethan, Jacobean, Caroline, Interregnum, Restoration,
Neoclassical, Romantic, Victorian, Modernist, Postwar, Contemporary
```

**Literary Movement (13+ categories)**:
```
Renaissance, Metaphysical, Augustan, Graveyard School, Romanticism,
Pre-Raphaelite, Imagism, Modernism, Harlem Renaissance, Beat,
Confessional, Black Arts, Language Poetry
```
*(Expandable with: Symbolism, Objectivism, New Formalism, etc.)*

**Mode (4 categories)**:
```
Lyric, Narrative, Dramatic, Mixed
```

#### Local M4 Max Approach:

**Step 1: Fine-Tune Local LLM**
- Use 52 gold-standard poems as training data
- Fine-tune Llama 3.1 8B or Mistral 7B on M4 Max
- Use MLX framework (optimized for Apple Silicon)
- No API costs, full control

**Step 2: Classification Pipeline**
```python
# src/poetry_bert/corpus/classifier.py

from mlx_lm import load, generate

class HistoricalContextClassifier:
    def __init__(self, model_path):
        """Load fine-tuned local model."""
        self.model, self.tokenizer = load(model_path)

    def classify_poem(self, poem_text, author, year):
        """Classify period, movement, mode with confidence."""
        prompt = self._build_classification_prompt(poem_text, author, year)
        result = generate(self.model, self.tokenizer, prompt)

        # Parse result
        period, movement, mode, confidence = self._parse_result(result)

        return {
            'period': period,
            'literary_movement': movement,
            'mode': mode,
            'confidence': confidence
        }

    def batch_classify(self, poems, batch_size=32):
        """Efficient batch processing."""
        # Process all 116K poems
        results = []
        for batch in tqdm(poems, desc="Classifying"):
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
        return results
```

**Step 3: High-Confidence Strategy**
- Only keep predictions with >90% confidence
- Flag low-confidence poems for manual review
- Iterative improvement: review edge cases → refine model

**Step 4: Manual Review Interface**
```python
# scripts/review_classifications.py

def create_review_interface():
    """Web interface for reviewing low-confidence predictions."""
    # Flask or Streamlit app
    # Show poem + AI prediction + confidence
    # User accepts/corrects
    # Use corrections to fine-tune model further
```

#### Scripts to Create:
- `scripts/prepare_training_data.py` - Format 52 gold poems for fine-tuning
- `scripts/fine_tune_classifier.py` - Fine-tune local LLM on M4 Max
- `scripts/classify_historical_context.py` - Batch classification pipeline
- `scripts/review_classifications.py` - Web interface for manual review
- `scripts/evaluate_classifier.py` - Model accuracy evaluation

#### Deliverable:
- Fine-tuned local classification model
- Period/movement/mode metadata for ~80,000-95,000 poems (high-confidence)
- Manual review queue for remaining poems
- Target accuracy: >95% on accepted classifications

---

### **Phase 4: Tier 3 Metadata - Prosodic Features**

#### Fields to Add:

| Field | Description | Target Coverage |
|-------|-------------|-----------------|
| `genre` | Poetic genre (sonnet, elegy, ode, etc.) | 40% |
| `meter` | Metrical pattern | 60% |
| `rhyme` | Rhyme scheme notation | 50% |
| `stanza_structure` | Structural description | 50% |

#### Approach:

**Leverage Existing Code**:
- Enhance `src/poetry_bert/features/prosodic.py` for batch processing
- Use `prosodic` library for meter detection
- Build rhyme pattern detection

**Detection Systems**:
```python
# src/poetry_bert/corpus/prosody_analyzer.py

import prosodic as p
from collections import Counter

class ProsodyAnalyzer:
    def __init__(self):
        self.prosodic = p.Text()

    def analyze_poem(self, poem_text):
        """Comprehensive prosodic analysis."""
        # Detect meter
        meter, meter_conf = self.detect_meter(poem_text)

        # Detect rhyme pattern
        rhyme_scheme, rhyme_conf = self.detect_rhyme(poem_text)

        # Classify genre (can use fine-tuned LLM from Phase 3)
        genre, genre_conf = self.classify_genre(
            poem_text, meter, rhyme_scheme
        )

        # Analyze stanza structure
        stanza_structure = self.analyze_structure(poem_text)

        return {
            'meter': meter,
            'rhyme': rhyme_scheme,
            'genre': genre,
            'stanza_structure': stanza_structure,
            'confidence_meter': meter_conf,
            'confidence_rhyme': rhyme_conf,
            'confidence_genre': genre_conf
        }

    def detect_meter(self, text):
        """Detect metrical pattern."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        meters = []
        for line in lines:
            parsed = self.prosodic.parse(line)
            meter_type = self._classify_meter(parsed)
            meters.append(meter_type)

        # Find dominant meter
        meter_counts = Counter(meters)
        if not meter_counts:
            return 'Free verse', 0.0

        dominant_meter, count = meter_counts.most_common(1)[0]
        confidence = count / len(meters)

        if confidence < 0.5:
            return 'Mixed', confidence
        return dominant_meter, confidence

    def detect_rhyme(self, text):
        """Detect rhyme scheme."""
        # Extract rhyme sounds from line endings
        # Build pattern (ABAB, AABB, etc.)
        # Handle variations and irregularities
        pass
```

**Scope**:
- Focus on ~40,000 formal poems (pre-1960s + structured contemporary)
- Accept nulls for free verse/experimental poetry
- High-confidence threshold (>85%)

#### Scripts to Create:
- `scripts/analyze_prosody.py` - Batch prosodic analysis
- `scripts/meter_detector.py` - Enhanced meter detection
- `scripts/rhyme_analyzer.py` - Rhyme pattern detection
- `scripts/genre_classifier.py` - Genre classification

#### Deliverable:
Prosodic metadata for ~40,000-70,000 formal poems

---

### **Phase 5: Tier 4 - Research Subset Gold Standard**

#### Goal: 1,000 Fully-Annotated Poems

**Selection Strategy**:
```python
def select_research_subset(corpus_df, n=1000):
    """Select balanced research subset."""

    # Include all 52 existing gold-standard poems
    selected = corpus_df[corpus_df['poem_id'].isin(GOLD_STANDARD_IDS)]

    # Add 948 new poems balanced by:
    stratify_by = {
        'period': [  # Proportional distribution
            ('Tudor', 20),
            ('Elizabethan', 30),
            ('Jacobean', 25),
            # ... etc
        ],
        'mode': [
            ('Lyric', 700),
            ('Narrative', 150),
            ('Dramatic', 100),
            ('Mixed', 50)
        ],
        'canonical': [
            ('High', 700),  # Well-known poems
            ('Medium', 200),
            ('Low', 100)    # Lesser-known
        ]
    }

    remaining = n - len(selected)
    new_poems = stratified_sample(corpus_df, stratify_by, remaining)

    return pd.concat([selected, new_poems])
```

**Full Annotation (35+ fields)**:

**From Old Metadata System**:
1. **Basic Bibliographic** (11 fields): source, source_edition, source_page, etc.
2. **Historical Context** (7 fields): period, movement, year_approx, etc.
3. **Formal Features** (8 fields): mode, genre, meter, rhyme, stanza_structure
4. **Rhetorical/Narratological** (16+ fields):
   - `register` - Emotional/stylistic tone (35+ values)
   - `rhetorical_genre` - Epideictic, Deliberative, Forensic, Mixed
   - `discursive_structure` - Monologic, Dialogic, Polyvocal
   - `discourse_type` - Direct discourse, Narrative, Description, etc.
   - `diegetic_mimetic` - Mimetic vs. Diegetic
   - `focalization` - Internal, External, Zero, Multiple
   - `person` - Grammatical person (1st, 2nd, 3rd, Mixed)
   - `deictic_orientation` - Spatial/personal orientation
   - `addressee_type` - Direct address, Apostrophic, Triangulated, etc.
   - `deictic_object` - What is referenced (free text)
   - `temporal_orientation` - Past, Present, Future, etc.
   - `temporal_structure` - Linear, Recursive, Static, etc.
   - `tradition` - Original, Translation, Imitation, Adaptation

**Annotation Workflow**:
```python
# scripts/annotation_interface.py

class AnnotationInterface:
    """User-friendly annotation tool."""

    def present_poem(self, poem_id):
        """Display poem + AI suggestions for all fields."""
        poem = self.load_poem(poem_id)

        # Show AI suggestions (from Phases 3-4)
        ai_suggestions = self.get_ai_suggestions(poem_id)

        # Present for review/correction
        self.display_annotation_form(poem, ai_suggestions)

    def save_annotation(self, poem_id, annotations):
        """Save fully annotated poem to research subset."""
        # Validate all required fields
        # Save to separate research_subset CSV
        # Track annotation progress
```

#### Scripts to Create:
- `scripts/select_research_subset.py` - Balanced selection algorithm
- `scripts/annotation_interface.py` - Web-based annotation tool (Streamlit)
- `scripts/annotation_guidelines.md` - Detailed annotation manual
- `scripts/quality_control.py` - Inter-rater reliability, validation

#### Deliverable:
1,000-poem gold-standard corpus with 35+ fields per poem

---

### **Phase 6: PostgreSQL Database (Incremental Implementation)**

#### Schema Design:

```sql
-- Core poems table (100% coverage)
CREATE TABLE poems (
    poem_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_last TEXT,
    date TEXT,
    year_approx INTEGER,
    source TEXT,
    source_url TEXT,
    filepath TEXT,
    filename TEXT,
    content TEXT NOT NULL,
    length_lines INTEGER NOT NULL,
    length_words INTEGER NOT NULL,
    content_hash TEXT UNIQUE NOT NULL,
    search_vector tsvector,  -- Full-text search
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Authors table (denormalized)
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    author_name TEXT UNIQUE NOT NULL,
    author_last TEXT,
    poem_count INTEGER DEFAULT 0,
    first_appearance_year INTEGER,
    last_appearance_year INTEGER,
    metadata JSONB  -- Flexible additional metadata
);

-- Historical context (70-80% coverage)
CREATE TABLE historical_context (
    poem_id INTEGER PRIMARY KEY REFERENCES poems(poem_id) ON DELETE CASCADE,
    period TEXT,
    literary_movement TEXT,
    mode TEXT,
    confidence_period FLOAT CHECK (confidence_period BETWEEN 0 AND 1),
    confidence_movement FLOAT CHECK (confidence_movement BETWEEN 0 AND 1),
    confidence_mode FLOAT CHECK (confidence_mode BETWEEN 0 AND 1),
    classification_method TEXT DEFAULT 'ai_local_llm',
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    notes TEXT
);

-- Prosodic features (40-60% coverage)
CREATE TABLE prosodic_features (
    poem_id INTEGER PRIMARY KEY REFERENCES poems(poem_id) ON DELETE CASCADE,
    genre TEXT,
    meter TEXT,
    rhyme TEXT,
    stanza_structure TEXT,
    confidence_genre FLOAT CHECK (confidence_genre BETWEEN 0 AND 1),
    confidence_meter FLOAT CHECK (confidence_meter BETWEEN 0 AND 1),
    confidence_rhyme FLOAT CHECK (confidence_rhyme BETWEEN 0 AND 1),
    analysis_method TEXT DEFAULT 'prosodic_library',
    computed_at TIMESTAMP DEFAULT NOW()
);

-- Rhetorical features (research subset only: 1,000 poems)
CREATE TABLE rhetorical_features (
    poem_id INTEGER PRIMARY KEY REFERENCES poems(poem_id) ON DELETE CASCADE,
    register TEXT,
    rhetorical_genre TEXT CHECK (rhetorical_genre IN ('Epideictic', 'Deliberative', 'Forensic', 'Mixed')),
    discursive_structure TEXT,
    discourse_type TEXT,
    diegetic_mimetic TEXT,
    focalization TEXT,
    person TEXT,
    deictic_orientation TEXT,
    addressee_type TEXT,
    deictic_object TEXT,
    temporal_orientation TEXT,
    temporal_structure TEXT,
    tradition TEXT,
    annotated_by TEXT,
    annotated_at TIMESTAMP,
    annotation_notes TEXT
);

-- Embeddings table (for future BERT work)
CREATE TABLE embeddings (
    poem_id INTEGER PRIMARY KEY REFERENCES poems(poem_id) ON DELETE CASCADE,
    model_version TEXT NOT NULL,
    line_embeddings vector(768)[],  -- pgvector extension
    stanza_embeddings vector(768)[],
    poem_embedding vector(768),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_poems_author ON poems(author);
CREATE INDEX idx_poems_author_last ON poems(author_last);
CREATE INDEX idx_poems_year ON poems(year_approx);
CREATE INDEX idx_poems_source ON poems(source);
CREATE INDEX idx_poems_hash ON poems(content_hash);
CREATE INDEX idx_poems_search ON poems USING GIN(search_vector);

CREATE INDEX idx_historical_period ON historical_context(period);
CREATE INDEX idx_historical_movement ON historical_context(literary_movement);
CREATE INDEX idx_historical_mode ON historical_context(mode);
CREATE INDEX idx_historical_confidence ON historical_context(confidence_period, confidence_movement, confidence_mode);

CREATE INDEX idx_prosodic_genre ON prosodic_features(genre);
CREATE INDEX idx_prosodic_meter ON prosodic_features(meter);
CREATE INDEX idx_prosodic_rhyme ON prosodic_features(rhyme);

CREATE INDEX idx_rhetorical_genre ON rhetorical_features(rhetorical_genre);
CREATE INDEX idx_rhetorical_register ON rhetorical_features(register);

-- Embedding similarity search (using pgvector)
CREATE INDEX idx_embeddings_poem ON embeddings USING ivfflat (poem_embedding vector_cosine_ops);

-- Full-text search function
CREATE OR REPLACE FUNCTION update_search_vector() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' ||
        coalesce(NEW.author, '') || ' ' ||
        coalesce(NEW.content, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER poems_search_vector_update
    BEFORE INSERT OR UPDATE ON poems
    FOR EACH ROW
    EXECUTE FUNCTION update_search_vector();
```

#### Incremental Implementation:

**After Phase 2**: Import basic metadata
```python
# scripts/import_phase2.py
df = pd.read_csv('data/metadata/corpus_final_metadata.csv')
df.to_sql('poems', engine, if_exists='replace', index=False)
```

**After Phase 3**: Add historical context
```python
# scripts/import_phase3.py
historical_df = pd.read_csv('data/metadata/historical_context.csv')
historical_df.to_sql('historical_context', engine, if_exists='replace', index=False)
```

**After Phase 4**: Add prosodic features
```python
# scripts/import_phase4.py
prosody_df = pd.read_csv('data/metadata/prosodic_features.csv')
prosody_df.to_sql('prosodic_features', engine, if_exists='replace', index=False)
```

**After Phase 5**: Add research subset
```python
# scripts/import_phase5.py
rhetoric_df = pd.read_csv('data/metadata/research_subset_rhetoric.csv')
rhetoric_df.to_sql('rhetorical_features', engine, if_exists='replace', index=False)
```

#### Useful Queries:

```sql
-- Find all sonnets by Shakespeare
SELECT p.poem_id, p.title, pf.rhyme
FROM poems p
JOIN prosodic_features pf ON p.poem_id = pf.poem_id
WHERE p.author LIKE '%Shakespeare%'
  AND pf.genre = 'Sonnet'
ORDER BY p.year_approx;

-- Poems by period and movement
SELECT hc.period, hc.literary_movement, COUNT(*) as poem_count
FROM historical_context hc
GROUP BY hc.period, hc.literary_movement
ORDER BY hc.period, poem_count DESC;

-- Full-text search for poems about "love" and "death"
SELECT p.poem_id, p.title, p.author,
       ts_rank(p.search_vector, query) as rank
FROM poems p,
     plainto_tsquery('english', 'love death') query
WHERE p.search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- Find poems by meter and period
SELECT p.title, p.author, hc.period, pf.meter
FROM poems p
JOIN historical_context hc ON p.poem_id = hc.poem_id
JOIN prosodic_features pf ON p.poem_id = pf.poem_id
WHERE pf.meter = 'Iambic pentameter'
  AND hc.period IN ('Romantic', 'Victorian')
ORDER BY p.year_approx;

-- Research subset with full annotations
SELECT p.title, p.author,
       hc.period, hc.literary_movement, hc.mode,
       pf.genre, pf.meter, pf.rhyme,
       rf.register, rf.rhetorical_genre, rf.focalization
FROM poems p
JOIN historical_context hc ON p.poem_id = hc.poem_id
JOIN prosodic_features pf ON p.poem_id = pf.poem_id
JOIN rhetorical_features rf ON p.poem_id = rf.poem_id
WHERE rf.poem_id IS NOT NULL;  -- Only research subset
```

#### Scripts to Create:
- `scripts/setup_database.py` - Schema creation and initial setup
- `src/poetry_bert/corpus/database.py` - SQLAlchemy ORM models
- `scripts/import_to_database.py` - CSV → PostgreSQL import
- `scripts/query_examples.py` - Useful query templates
- `scripts/database_migration.py` - Schema migration tools

#### Deliverable:
Production PostgreSQL database with:
- Full-text search capability
- Referential integrity constraints
- Optimized indexes for common queries
- pgvector for embedding similarity search (future BERT work)

---

## Tools & Infrastructure

### Python Packages:

```bash
# Core data processing
pip install pandas numpy

# Database
pip install sqlalchemy psycopg2-binary pgvector

# NLP & ML
pip install transformers torch torchvision

# Apple Silicon optimization (M4 Max)
pip install mlx mlx-lm

# Prosody analysis
pip install pronouncing poetry-tools prosodic

# Web interfaces
pip install streamlit flask

# Progress tracking
pip install tqdm
```

### Local LLM Setup (M4 Max):

```bash
# Install MLX for Apple Silicon
pip install mlx mlx-lm

# Download base model for fine-tuning
# Option 1: Llama 3.1 8B
mlx_lm.download --model meta-llama/Llama-3.1-8B

# Option 2: Mistral 7B
mlx_lm.download --model mistralai/Mistral-7B-v0.1
```

### PostgreSQL Setup:

```bash
# Install PostgreSQL (macOS)
brew install postgresql@16

# Install pgvector extension
brew install pgvector

# Start PostgreSQL
brew services start postgresql@16

# Create database
createdb poetry_corpus
```

---

## Validation & Quality Assurance

### Automated Testing:

```python
# src/poetry_bert/corpus/validation.py

class CorpusValidator:
    def validate_all(self):
        """Run comprehensive validation suite."""
        results = {
            'file_csv_alignment': self.validate_file_csv_alignment(),
            'unique_hashes': self.validate_unique_hashes(),
            'sequential_ids': self.validate_sequential_ids(),
            'metadata_completeness': self.validate_metadata_completeness(),
            'controlled_vocabularies': self.validate_controlled_vocabularies(),
            'database_integrity': self.validate_database_integrity(),
            'classification_accuracy': self.validate_classification_accuracy()
        }

        # Generate validation report
        self.generate_report(results)
        return all(results.values())

    def validate_file_csv_alignment(self):
        """Verify all CSV entries have corresponding files."""
        csv_ids = set(df['poem_id'])
        file_ids = set(self.get_file_ids())

        missing_files = csv_ids - file_ids
        extra_files = file_ids - csv_ids

        assert len(missing_files) == 0, f"Missing files: {missing_files}"
        assert len(extra_files) == 0, f"Extra files: {extra_files}"
        return True

    def validate_classification_accuracy(self):
        """Sample and manually verify AI classifications."""
        # Sample 100 random classifications
        # Manual review
        # Calculate accuracy
        pass
```

### Continuous Improvement:

```python
# Track all manual corrections
corrections_log = []

def log_correction(poem_id, field, ai_value, correct_value, confidence):
    """Log all manual corrections for model improvement."""
    corrections_log.append({
        'poem_id': poem_id,
        'field': field,
        'ai_prediction': ai_value,
        'correct_value': correct_value,
        'original_confidence': confidence,
        'timestamp': datetime.now()
    })

def analyze_corrections():
    """Find patterns in AI errors for model improvement."""
    df = pd.DataFrame(corrections_log)

    # Which periods/movements are most often wrong?
    # What confidence threshold should we use?
    # Which poems need manual review?

    return improvement_suggestions
```

---

## Expected Deliverables (Final State)

### 1. Clean Corpus
- 116,675 unique, sequentially-numbered poems (IDs: 1-116,675)
- No duplicates, no gaps
- Perfect file/CSV/database alignment

### 2. Rich Metadata CSV
- **Basic**: 16 fields (100% coverage)
- **Historical**: period, movement, mode (70-80% coverage)
- **Prosodic**: genre, meter, rhyme, structure (40-60% coverage)
- **Rhetorical**: 16+ fields (1,000-poem research subset)
- **Total**: 40-45 metadata fields

### 3. PostgreSQL Database
- Production-ready with integrity constraints
- Optimized indexes for common queries
- Full-text search capability
- pgvector for embedding similarity (future BERT work)
- 116,675 poems in main table
- ~80,000-95,000 with historical context
- ~40,000-70,000 with prosodic features
- 1,000 with full rhetorical annotation

### 4. Research Subset
- 1,000 gold-standard poems
- 35+ fields per poem
- Balanced selection (period, mode, canonical status)
- Inter-rater reliability validation
- Suitable for publication and advanced research

### 5. Classification Models
- Fine-tuned local LLM for period/movement/mode
- Trained on M4 Max, runs locally
- >95% accuracy on high-confidence predictions
- Iteratively improved with manual corrections

### 6. Analysis Tools
- Prosodic analysis pipeline
- Batch processing scripts
- Annotation interfaces
- Validation suite
- Query templates and examples

### 7. Documentation
- Complete annotation guidelines
- Schema documentation
- API documentation for database queries
- Maintenance and extension guides

---

## Success Criteria

1. ✅ **Corpus Integrity**: 116,675 unique poems, perfect alignment
2. ✅ **Metadata Coverage**: >70% for historical, >40% for prosodic
3. ✅ **Classification Accuracy**: >95% on accepted AI classifications
4. ✅ **Database Performance**: Optimized queries, full-text search
5. ✅ **Research Subset**: 1,000 fully-annotated gold-standard poems
6. ✅ **Reproducibility**: All scripts documented and reusable
7. ✅ **Validation**: Automated test suite passing
8. ✅ **Local Models**: Fine-tuned LLMs running on M4 Max

---

## Collaborative Workflow

### Division of Responsibilities:

**You (Human)**:
- Guide research priorities
- Make final annotation decisions
- Review classification results
- Validate and test outputs
- Provide domain expertise

**Claude Code (Me)**:
- Write all scripts and tools
- Process data at scale
- Suggest classifications
- Debug and optimize code
- Help with complex annotations
- Generate documentation

**M4 Max**:
- Fine-tune local LLM models
- Run batch processing efficiently
- Host local PostgreSQL
- Generate embeddings (future BERT work)

### Iteration Pattern:

1. Build a tool together
2. Run on sample (100-1,000 poems)
3. Review results together
4. Refine approach based on findings
5. Scale to full corpus
6. Validate and document

---

## Next Steps

**Phase 1 Ready to Begin**:
1. Create `scripts/cleanup_duplicates.py`
2. Create `scripts/renumber_corpus.py`
3. Create `scripts/validate_corpus.py`
4. Execute cleanup and renumbering
5. Validate results

**Ready to start coding when you are!**
