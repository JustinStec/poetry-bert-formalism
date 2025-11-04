#!/usr/bin/env python3
"""
Upload Poetry-BERT models to Hugging Face Hub

This script uploads trained models to Hugging Face for:
1. Reproducibility in publications
2. Community access
3. Easy loading with transformers library
4. DOI-like citation

Usage:
    # Install huggingface_hub first:
    pip install huggingface_hub

    # Login to Hugging Face (one-time):
    huggingface-cli login

    # Upload all models:
    python upload_to_huggingface.py

    # Upload specific model:
    python upload_to_huggingface.py --model eebo
    python upload_to_huggingface.py --model poetry
    python upload_to_huggingface.py --model poetry_eebo
"""

import argparse
from pathlib import Path
from huggingface_hub import HfApi, create_repo
import os

# Paths to models in Google Drive
GOOGLE_DRIVE_BASE = "/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry"

MODELS = {
    "eebo": {
        "local_path": f"{GOOGLE_DRIVE_BASE}/EEBO_1595-1700/eebo_bert_finetuned",
        "repo_name": "eebo-bert",
        "display_name": "EEBO-BERT",
        "description": "BERT fine-tuned on Early English Books Online (1595-1700) for historical semantics"
    },
    "poetry": {
        "local_path": f"{GOOGLE_DRIVE_BASE}/poetry_bert_trained",
        "repo_name": "poetry-bert",
        "display_name": "Poetry-BERT",
        "description": "BERT fine-tuned on 17.7M lines of poetry (independent path)"
    },
    "poetry_eebo": {
        "local_path": f"{GOOGLE_DRIVE_BASE}/poetry_eebo_bert_trained",
        "repo_name": "poetry-eebo-bert",
        "display_name": "Poetry-EEBO-BERT",
        "description": "EEBO-BERT fine-tuned on poetry (proper Layer 1 → Layer 2 architecture)"
    }
}

# Model card templates
def create_eebo_model_card():
    """Create README.md for EEBO-BERT"""
    return """---
license: apache-2.0
language:
- en
tags:
- historical-nlp
- early-modern-english
- eebo
- bert
- shakespeare
datasets:
- early-english-books-online
base_model: bert-base-uncased
---

# EEBO-BERT: BERT for Early Modern English (1595-1700)

**Layer 1** of three-layer BERT architecture for analyzing Early Modern poetry.

## Model Description

EEBO-BERT is `bert-base-uncased` fine-tuned on the Early English Books Online (EEBO) corpus from 1595-1700. This model captures **historical semantics** of Early Modern English, making it ideal for analyzing Shakespeare and contemporary literature.

## Training Data

- **Corpus**: Early English Books Online (EEBO) 1595-1700
- **Size**: ~8GB of historical English text
- **Period**: Late Elizabethan through Restoration
- **Base**: `bert-base-uncased` (110M parameters)

## Intended Uses

### Primary Use Cases
- Analyzing Early Modern English literature (Shakespeare, Marlowe, Donne, etc.)
- Historical semantic analysis
- Layer 1 base model for poetry specialization (Poetry-EEBO-BERT)
- Diachronic language studies

### Out-of-Scope Uses
- Modern English NLP tasks (use `bert-base-uncased` instead)
- Generation tasks (this is an encoder-only model)
- Non-English languages

## How to Use

```python
from transformers import BertModel, BertTokenizer

# Load model
tokenizer = BertTokenizer.from_pretrained("justinstec/eebo-bert")
model = BertModel.from_pretrained("justinstec/eebo-bert")

# Get embeddings for Shakespeare
text = "Shall I compare thee to a summer's day?"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
embeddings = outputs.last_hidden_state.mean(dim=1)
```

## Training Details

### Training Procedure
- **Base model**: `bert-base-uncased`
- **Tokenizer**: WordPiece (same as base BERT)
- **Training**: Masked Language Modeling (MLM) with 15% mask rate
- **Epochs**: 3
- **Hardware**: Google Colab A100 GPU
- **Training time**: ~8 hours

### Evaluation

Evaluated on Shakespeare's sonnets using trajectory tortuosity metric:
- **Mean tortuosity**: 3.45 (vs. 3.17 for base BERT)
- **Change**: +8.8% increase in semantic complexity detection
- **Interpretation**: Captures historical semantic nuances lost in base BERT

## Architecture

Part of three-layer architecture:
```
bert-base-uncased (modern English)
    ↓ Fine-tune on EEBO 1595-1700
EEBO-BERT (Layer 1: Historical Semantics) ← THIS MODEL
    ↓ Fine-tune on 17.7M poetry lines
Poetry-EEBO-BERT (Layer 2: Poetry + Historical)
    ↓ Add prosodic features
Layer 3: +Prosody (meter, rhyme, position)
```

## Limitations

- Limited to Early Modern English (1595-1700)
- May not generalize to other historical periods
- Inherits biases from EEBO corpus (primarily male authors)
- Small vocabulary differences from modern English

## Citation

```bibtex
@unpublished{stecher2025eebo_bert,
  title={{EEBO-BERT: A Historical Language Model for Early Modern English}},
  author={Stecher, Justin},
  year={2025},
  note={Layer 1 of three-layer BERT architecture for poetry analysis}
}
```

## Related Models

- **Poetry-EEBO-BERT** (`justinstec/poetry-eebo-bert`): This model fine-tuned on poetry
- **Poetry-BERT** (`justinstec/poetry-bert`): Independent poetry path from base BERT

## Contact

- **Developed by**: Justin Stecher
- **Affiliation**: IU Center for Possible Minds
- **License**: Apache 2.0
- **Issues**: [GitHub](https://github.com/JustinStec/poetry-bert-formalism)

---

**Last Updated**: November 2025
"""

def create_poetry_model_card():
    """Create README.md for Poetry-BERT"""
    return """---
license: apache-2.0
language:
- en
tags:
- poetry
- bert
- shakespeare
- literature
datasets:
- shakespeare
- gutenberg-poetry
- core-poets
- poetrydb
base_model: bert-base-uncased
---

# Poetry-BERT: BERT Fine-tuned on 17.7M Lines of Poetry

**Independent poetry specialization** path (Layer 2 alternative).

⚠️ **Note**: This model was trained from `bert-base-uncased`. For the proper **layered architecture** (EEBO-BERT → Poetry), see [`justinstec/poetry-eebo-bert`](https://huggingface.co/justinstec/poetry-eebo-bert).

## Model Description

Poetry-BERT is `bert-base-uncased` fine-tuned on 17.7 million lines of poetry from multiple sources. This model learns **poetic conventions** but does NOT preserve historical semantics from EEBO-BERT.

## Training Data

- **Corpus Size**: 17.7M lines of poetry (~1.1GB database)
- **Sources**:
  - Shakespeare Complete Works
  - Project Gutenberg poetry (reconstructed)
  - Core 27 Poets (complete works)
  - PoetryDB (multi-author anthology)
- **Base**: `bert-base-uncased` (110M parameters)

## Intended Uses

### Primary Use Cases
- Poetry analysis and generation
- Poetic semantic embeddings
- Comparison model for testing architectural choices
- Baseline for poetry NLP tasks

### When to Use vs. Poetry-EEBO-BERT
- **Use Poetry-BERT** if you want poetry specialization only
- **Use Poetry-EEBO-BERT** if analyzing historical poetry (Shakespeare, Donne, etc.)

## How to Use

```python
from transformers import BertModel, BertTokenizer

# Load model
tokenizer = BertTokenizer.from_pretrained("justinstec/poetry-bert")
model = BertModel.from_pretrained("justinstec/poetry-bert")

# Get embeddings for poetry
text = "And death shall be no more; Death, thou shalt die."
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
embeddings = outputs.last_hidden_state.mean(dim=1)
```

## Training Details

### Training Procedure
- **Base model**: `bert-base-uncased` (NOT EEBO-BERT)
- **Training**: Masked Language Modeling (MLM) with 15% mask rate
- **Epochs**: 3
- **Batch size**: 8
- **Learning rate**: 5e-5
- **Hardware**: Google Colab A100 GPU
- **Training time**: ~6-8 hours

### Evaluation

Evaluated on Shakespeare's sonnets using trajectory tortuosity metric:
- **Mean tortuosity**: 3.59 (vs. 3.17 for base BERT, 3.45 for EEBO-BERT)
- **Change**: +13.2% increase in semantic complexity detection
- **Interpretation**: Captures poetic semantic density better than base or historical-only models

## Architecture Comparison

### This Model (Poetry-BERT)
```
bert-base-uncased
    ↓ Fine-tune on 17.7M poetry lines
Poetry-BERT (Independent poetry path) ← THIS MODEL
```

### Proper Layered Architecture
```
bert-base-uncased
    ↓ Fine-tune on EEBO 1595-1700
EEBO-BERT (Layer 1: Historical)
    ↓ Fine-tune on 17.7M poetry lines
Poetry-EEBO-BERT (Layer 2: Poetry + Historical)
```

**Recommendation**: For historical poetry analysis, use `justinstec/poetry-eebo-bert` instead.

## Key Finding

Comparing Poetry-BERT vs. Poetry-EEBO-BERT reveals:
- **Correlation**: r=0.630 (moderate agreement)
- **Interpretation**: Poetry and historical specialization capture different aspects
- **Implication**: Both layers add unique, non-redundant information

## Limitations

- Trained only on poetry (may not generalize to prose)
- Does NOT preserve historical semantics from EEBO-BERT
- Inherits biases from modern poetry corpus
- May overfit to common poetic patterns

## Citation

```bibtex
@unpublished{stecher2025poetry_bert,
  title={{Poetry-BERT: BERT Fine-tuned on Poetry Corpus}},
  author={Stecher, Justin},
  year={2025},
  note={Independent poetry specialization path (comparison model)}
}
```

## Related Models

- **EEBO-BERT** (`justinstec/eebo-bert`): Historical semantics only
- **Poetry-EEBO-BERT** (`justinstec/poetry-eebo-bert`): Proper layered architecture (recommended)

## Contact

- **Developed by**: Justin Stecher
- **Affiliation**: IU Center for Possible Minds
- **License**: Apache 2.0
- **Issues**: [GitHub](https://github.com/JustinStec/poetry-bert-formalism)

---

**Last Updated**: November 2025
"""

def create_poetry_eebo_model_card():
    """Create README.md for Poetry-EEBO-BERT"""
    return """---
license: apache-2.0
language:
- en
tags:
- poetry
- historical-nlp
- shakespeare
- early-modern-english
- bert
- literature
datasets:
- early-english-books-online
- shakespeare
- gutenberg-poetry
- core-poets
- poetrydb
base_model: justinstec/eebo-bert
---

# Poetry-EEBO-BERT: Layered BERT for Historical Poetry Analysis

**Layer 2** of three-layer BERT architecture: Historical semantics + poetry specialization.

✅ **Proper layered architecture**: EEBO-BERT → Poetry-EEBO-BERT

## Model Description

Poetry-EEBO-BERT is **EEBO-BERT fine-tuned on 17.7M lines of poetry**. This model combines:
1. **Historical semantics** from EEBO (1595-1700)
2. **Poetic conventions** from multi-source poetry corpus

This is the **recommended model** for analyzing Early Modern poetry (Shakespeare, Donne, Spenser, etc.).

## Training Data

### Layer 1 (EEBO-BERT base)
- **Corpus**: Early English Books Online (EEBO) 1595-1700
- **Size**: ~8GB historical English text
- **Purpose**: Historical semantic representations

### Layer 2 (This Model)
- **Starting point**: EEBO-BERT (NOT bert-base-uncased)
- **Additional training**: 17.7M lines of poetry
- **Sources**:
  - Shakespeare Complete Works
  - Project Gutenberg poetry
  - Core 27 Poets
  - PoetryDB

## Intended Uses

### Primary Use Cases
- Analyzing Early Modern poetry (Shakespeare, Donne, Spenser, Sidney)
- Semantic complexity analysis of historical verse
- Layer 2 base for prosodic conditioning (Layer 3)
- Literary computational analysis

### Why Use This Over Poetry-BERT?
- **Poetry-EEBO-BERT**: Preserves historical semantics + learns poetry
- **Poetry-BERT**: Poetry only, loses historical context
- **For Shakespeare**: Use this model
- **For modern poetry**: Consider `justinstec/poetry-bert`

## How to Use

```python
from transformers import BertModel, BertTokenizer

# Load model
tokenizer = BertTokenizer.from_pretrained("justinstec/poetry-eebo-bert")
model = BertModel.from_pretrained("justinstec/poetry-eebo-bert")

# Analyze Shakespeare
text = "Shall I compare thee to a summer's day?"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
embeddings = outputs.last_hidden_state.mean(dim=1)
```

## Training Details

### Training Procedure
- **Base model**: `justinstec/eebo-bert` (Layer 1)
- **Training**: Masked Language Modeling (MLM) with 15% mask rate
- **Epochs**: 3
- **Batch size**: 8
- **Learning rate**: 5e-5
- **Hardware**: Google Colab A100 GPU
- **Training time**: ~6-8 hours

### Evaluation

Evaluated on Shakespeare's sonnets using trajectory tortuosity metric:
- **Expected results**: TBD after training completes
- **Hypothesis**: Similar to Poetry-BERT (+13%) but with historical precision
- **Comparison**: Should show effects of layered vs. independent architecture

## Complete Architecture

```
bert-base-uncased (110M parameters)
    ↓ Fine-tune on EEBO 1595-1700
EEBO-BERT (Layer 1: Historical Semantics)
    justinstec/eebo-bert
    ↓ Fine-tune on 17.7M poetry lines
Poetry-EEBO-BERT (Layer 2: Poetry + Historical) ← THIS MODEL
    justinstec/poetry-eebo-bert
    ↓ Concatenate prosodic features (meter, rhyme, position)
Layer 3: +Prosody
    (Post-hoc feature concatenation in analysis)
```

## Research Question

**Does poetry specialization preserve or modify historical semantics?**

This model lets us test whether:
1. Poetry training maintains EEBO's historical knowledge
2. The two specializations interact constructively
3. Layered architecture outperforms independent paths

## Key Findings

### Layer Effects (from full architecture)
- **EEBO-BERT**: +8.8% vs. base BERT
- **Poetry-BERT**: +13.2% vs. base BERT
- **Poetry-EEBO-BERT**: TBD (expected: different from independent Poetry-BERT)

### Prosodic Conditioning (Layer 3)
- Meter and rhyme consistently reduce complexity -2.0% to -2.5%
- **Implication**: Form acts as semantic constraint
- **Theoretical significance**: Computational evidence for formalist theories

## Limitations

- Specific to Early Modern English poetry (1595-1700 + later poetry)
- May not generalize to prose or modern poetry
- Inherits biases from both EEBO and poetry corpora
- Computational cost of layered fine-tuning

## Citation

```bibtex
@unpublished{stecher2025poetry_eebo_bert,
  title={{Poetry-EEBO-BERT: A Layered Architecture for Historical Poetry Analysis}},
  author={Stecher, Justin},
  year={2025},
  note={Layer 2 of three-layer BERT architecture}
}
```

## Related Models

- **EEBO-BERT** (`justinstec/eebo-bert`): Layer 1 base model
- **Poetry-BERT** (`justinstec/poetry-bert`): Independent poetry path (comparison)

## Related Research

This model is part of research on layered BERT architectures for poetry analysis. See:
- **Paper 1** (in prep): Trajectory tortuosity for Shakespeare sonnets
- **GitHub**: [poetry-bert-formalism](https://github.com/JustinStec/poetry-bert-formalism)

## Contact

- **Developed by**: Justin Stecher
- **Affiliation**: IU Center for Possible Minds
- **License**: Apache 2.0
- **Issues**: [GitHub](https://github.com/JustinStec/poetry-bert-formalism)

---

**Last Updated**: November 2025
"""

def upload_model(model_key, username, private=False):
    """
    Upload a model to Hugging Face Hub

    Args:
        model_key: Key from MODELS dict ('eebo', 'poetry', or 'poetry_eebo')
        username: Hugging Face username
        private: Whether to make the model private
    """
    model_info = MODELS[model_key]
    local_path = Path(model_info["local_path"])
    repo_id = f"{username}/{model_info['repo_name']}"

    print(f"\n{'='*70}")
    print(f"Uploading {model_info['display_name']}")
    print(f"{'='*70}")
    print(f"Local path: {local_path}")
    print(f"Repository: {repo_id}")
    print(f"Private: {private}")

    # Check if model exists
    if not local_path.exists():
        print(f"❌ Model not found at {local_path}")
        print(f"   Please ensure the model is in your Google Drive")
        return False

    # Check for required files
    required_files = ["config.json", "vocab.txt"]
    model_files = ["pytorch_model.bin", "model.safetensors"]

    has_model = any((local_path / f).exists() for f in model_files)
    has_required = all((local_path / f).exists() for f in required_files)

    if not has_required or not has_model:
        print(f"❌ Missing required model files:")
        print(f"   Required: {required_files + ['pytorch_model.bin OR model.safetensors']}")
        return False

    print(f"✓ Model files found")

    # Create repository
    api = HfApi()
    try:
        create_repo(repo_id, private=private, exist_ok=True)
        print(f"✓ Repository created: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"⚠ Repository might already exist: {e}")

    # Create and save model card
    if model_key == "eebo":
        model_card = create_eebo_model_card()
    elif model_key == "poetry":
        model_card = create_poetry_model_card()
    else:  # poetry_eebo
        model_card = create_poetry_eebo_model_card()

    readme_path = local_path / "README.md"
    with open(readme_path, 'w') as f:
        f.write(model_card)
    print(f"✓ Model card created: {readme_path}")

    # Upload model
    print(f"\nUploading files to Hugging Face...")
    print(f"This may take 10-20 minutes depending on your internet speed...")

    try:
        api.upload_folder(
            folder_path=str(local_path),
            repo_id=repo_id,
            repo_type="model",
        )
        print(f"\n✓ Upload complete!")
        print(f"  View at: https://huggingface.co/{repo_id}")
        return True
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Upload Poetry-BERT models to Hugging Face")
    parser.add_argument("--model", choices=["eebo", "poetry", "poetry_eebo", "all"],
                       default="all", help="Which model to upload")
    parser.add_argument("--username", type=str, required=True,
                       help="Your Hugging Face username")
    parser.add_argument("--private", action="store_true",
                       help="Make repositories private")

    args = parser.parse_args()

    print("="*70)
    print("Hugging Face Model Upload Script")
    print("="*70)
    print(f"Username: {args.username}")
    print(f"Private: {args.private}")
    print()
    print("Before uploading, please ensure:")
    print("  1. You've logged in: huggingface-cli login")
    print("  2. You've installed: pip install huggingface_hub")
    print("  3. Models are in Google Drive at expected paths")
    print("="*70)

    input("\nPress Enter to continue...")

    # Upload models
    if args.model == "all":
        models_to_upload = ["eebo", "poetry", "poetry_eebo"]
    else:
        models_to_upload = [args.model]

    results = {}
    for model_key in models_to_upload:
        success = upload_model(model_key, args.username, args.private)
        results[model_key] = success

    # Summary
    print("\n" + "="*70)
    print("UPLOAD SUMMARY")
    print("="*70)
    for model_key, success in results.items():
        status = "✓ Success" if success else "❌ Failed"
        print(f"{MODELS[model_key]['display_name']}: {status}")

    print("\n" + "="*70)
    print("Next Steps:")
    print("="*70)
    print("1. Visit your models at: https://huggingface.co/" + args.username)
    print("2. Verify model cards look correct")
    print("3. Test loading with: transformers.AutoModel.from_pretrained()")
    print("4. Add model links to your paper!")
    print("="*70)

if __name__ == "__main__":
    main()
