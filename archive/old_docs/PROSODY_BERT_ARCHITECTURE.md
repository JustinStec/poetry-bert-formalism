# Prosody-Conditioned BERT: Two-Phase Architecture

## Overview

**Goal:** Create a BERT model that generates prosody-aware contextual embeddings for semantic trajectory analysis of poetry across historical periods.

**Strategy:** Two-phase training
- Phase 1: Learn Early Modern English from large prose corpus
- Phase 2: Add prosodic awareness from actual poetry

---

## Phase 1: EEBO-BERT (Historical Language Model)

### Corpus
- **Source:** EEBO 1595-1700 (7.6GB, 61,315 texts)
- **Content:** Early Modern English prose and poetry
- **Purpose:** Learn vocabulary, syntax, and semantic patterns of the period

### Architecture
```
Standard BERT-base-uncased:
- 12 transformer layers
- 768 hidden dimensions
- 12 attention heads
- 110M parameters
- Pre-trained on modern English (Wikipedia + BookCorpus)
```

### Training Task
**Masked Language Modeling (MLM):**
- Randomly mask 15% of tokens
- Train BERT to predict masked tokens from context
- Example: "Shall I compare thee to a [MASK] day?" → predict "summer"

### Training Configuration
```python
BATCH_SIZE = 8          # Colab GPU has memory
MAX_LENGTH = 512        # BERT's max sequence length
NUM_EPOCHS = 3          # Standard for fine-tuning
LEARNING_RATE = 5e-5
WARMUP_STEPS = 500
```

### Expected Output
`eebo_bert_finetuned/` - A BERT model that understands:
- Archaic vocabulary: "thee", "thou", "doth"
- Early Modern syntax and grammar
- Historical word usage patterns
- Contextual relationships in 1595-1700 English

### Timeline
- Setup: 30 minutes (upload to Colab, configure)
- Training: 6-8 hours on Colab Pro GPU (T4 or V100)
- Cost: $10/month Colab Pro subscription

---

## Phase 2: Prosody-Conditioned EEBO-BERT

### Corpus
- **Source:** Your 52 canonical poems
- **Content:** Poetry from 1500s-2000s (Shakespeare, Donne, Milton, Wordsworth, Ginsberg, etc.)
- **Purpose:** Learn how prosody conditions semantic meaning

### Modified Architecture

**Add prosodic embedding layers:**

```
Standard BERT embeddings:
  input_ids → token_embedding (768 dim)
  position_ids → position_embedding (768 dim)

  Combined: token_emb + position_emb → BERT encoder

Prosody-Conditioned BERT embeddings:
  input_ids → token_embedding (768 dim)
  position_ids → position_embedding (768 dim)

  PROSODIC FEATURES (new):
  stress_ids → stress_embedding (64 dim)
    - 0 = unstressed/weak syllable
    - 1 = stressed/strong syllable

  meter_pos_ids → meter_position_embedding (64 dim)
    - Position in metrical foot (1-5 for pentameter)

  line_pos_ids → line_position_embedding (64 dim)
    - Normalized position in line (0.0 - 1.0)

  Combined: token_emb + position_emb +
            stress_emb + meter_pos_emb + line_pos_emb → BERT encoder
```

### Implementation

```python
class ProsodyConditionedBert(BertForMaskedLM):
    def __init__(self, config):
        super().__init__(config)

        # Add prosodic embedding layers
        self.stress_embeddings = nn.Embedding(2, 64)  # Binary: 0/1
        self.meter_position_embeddings = nn.Embedding(10, 64)  # Up to 10 positions
        self.line_position_embeddings = nn.Embedding(100, 64)  # Discretized 0-100

        # Projection layer to combine prosodic features
        self.prosody_projection = nn.Linear(64 * 3, 768)

    def forward(self, input_ids, attention_mask=None,
                stress_ids=None, meter_pos_ids=None, line_pos_ids=None):

        # Standard BERT embeddings
        token_emb = self.embeddings.word_embeddings(input_ids)
        position_emb = self.embeddings.position_embeddings(position_ids)

        # Prosodic embeddings (if provided)
        if stress_ids is not None:
            stress_emb = self.stress_embeddings(stress_ids)
            meter_emb = self.meter_position_embeddings(meter_pos_ids)
            line_emb = self.line_position_embeddings(line_pos_ids)

            # Combine prosodic features
            prosody_emb = torch.cat([stress_emb, meter_emb, line_emb], dim=-1)
            prosody_emb = self.prosody_projection(prosody_emb)

            # Add to standard embeddings
            embeddings = token_emb + position_emb + prosody_emb
        else:
            # Fall back to standard BERT (for non-poetry text)
            embeddings = token_emb + position_emb

        # Pass through BERT encoder
        return self.bert(inputs_embeds=embeddings, attention_mask=attention_mask)
```

### Training Tasks

**Multi-task learning:**

1. **Masked Language Modeling (MLM)** - primary task
   - Predict masked words from context
   - Same as Phase 1

2. **Prosody Prediction** - auxiliary task
   - Predict stress pattern from words
   - Forces model to learn prosodic structure
   - Example: Given "summer", predict stress=1

```python
loss = mlm_loss + 0.3 * prosody_prediction_loss
```

### Data Preparation

For each poem, extract prosodic features using Prosodic library:

```python
# Input line
"Shall I compare thee to a summer's day?"

# BERT tokenization (WordPiece)
tokens = ['shall', 'I', 'compare', 'thee', 'to', 'a', 'summer', "'", 's', 'day', '?']

# Prosodic analysis (syllables)
syllables = ['shall', 'I', 'com', 'PARE', 'thee', 'TO', 'a', 'SUM', "mer's", 'DAY']
stress = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]

# Alignment: map BERT tokens to prosodic features
# 'summer' → 'SUM' + "mer's"
# Strategy: assign each token the prosodic features of its primary syllable
token_stress = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # '?' gets neutral 0
token_meter_pos = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 0]
token_line_pos = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # Discretized
```

### Training Configuration

```python
BATCH_SIZE = 4          # Smaller due to extra embeddings
MAX_LENGTH = 512
NUM_EPOCHS = 10         # More epochs for small dataset
LEARNING_RATE = 2e-5    # Lower LR to preserve Phase 1 knowledge
WARMUP_STEPS = 100
```

### Expected Output

`eebo_bert_prosody_finetuned/` - A BERT model that:
- Understands Early Modern English (from Phase 1)
- Generates different embeddings for same word based on prosodic context
- Example: "day" at end of line (stressed, rhyme position) vs. middle (unstressed)

### Timeline
- Annotation: 1-2 hours (run Prosodic on 52 poems)
- Implementation: 2-3 days (custom BERT class, training script)
- Training: 1-2 hours on GPU

---

## Usage for Semantic Trajectory Analysis

Once both phases are complete:

```python
from transformers import AutoTokenizer, AutoModel
import prosodic as pr

# Load prosody-conditioned model
tokenizer = AutoTokenizer.from_pretrained('./eebo_bert_prosody_finetuned')
model = ProsodyConditionedBert.from_pretrained('./eebo_bert_prosody_finetuned')

# Analyze a poem
poem_line = "Shall I compare thee to a summer's day?"

# Get prosodic features
prosodic_features = extract_prosodic_features(poem_line)

# Tokenize with prosodic context
encoding = tokenizer(
    poem_line,
    return_tensors='pt',
    prosodic_features=prosodic_features  # Custom addition
)

# Get prosody-conditioned embeddings
outputs = model(**encoding, output_hidden_states=True)
embeddings = outputs.hidden_states[-1]  # Last layer

# Now analyze semantic trajectories using these embeddings
# Words in stressed vs unstressed positions will have different embeddings
```

---

## Comparison to Alternatives

### vs. Standard BERT Fine-tuning (Option A)
- ❌ No prosodic awareness
- ❌ Same embedding regardless of metrical position
- ✓ Simpler to implement

### vs. Annotate All EEBO with Prosody (Option B)
- ❌ Prosodic features don't make sense for prose
- ❌ Would annotate 7.6GB of legal documents with "meter"
- ❌ Slow and theoretically unsound

### Our Two-Phase Approach (Option C)
- ✓ Learns language from large corpus
- ✓ Learns prosody from actual poetry
- ✓ Theoretically sound (prosody only matters for poetry)
- ✓ Computationally efficient
- ✓ Novel approach (potentially publishable)

---

## Next Steps

1. **Phase 1 Training** (can start immediately)
   - Use existing `colab_bert_training.ipynb`
   - Upload EEBO corpus to Google Drive
   - Train standard BERT (6-8 hours)

2. **Phase 2 Implementation** (while Phase 1 trains)
   - Annotate 52 poems with Prosodic
   - Implement `ProsodyConditionedBert` class
   - Write training script with multi-task learning

3. **Validation**
   - Test on held-out poems
   - Compare embeddings with/without prosodic conditioning
   - Analyze semantic trajectories

Ready to start Phase 1?
