#!/usr/bin/env python3
"""
Format Phase 3 training dataset for instruction tuning.

Converts 397 poems with 28 classification labels into prompt/completion pairs
suitable for fine-tuning Llama-3 or Mistral with LoRA/MLX.

Input:  Data/training/phase3_classifications/training_dataset_complete.jsonl
Output: Data/training/phase3_classifications/instruction_dataset_train.jsonl
        Data/training/phase3_classifications/instruction_dataset_val.jsonl
"""

import json
from pathlib import Path
import random

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
INPUT_FILE = BASE_DIR / "Data/training/phase3_classifications/training_dataset_complete.jsonl"
OUTPUT_TRAIN = BASE_DIR / "Data/training/phase3_classifications/instruction_dataset_train.jsonl"
OUTPUT_VAL = BASE_DIR / "Data/training/phase3_classifications/instruction_dataset_val.jsonl"

# Classification fields (28 total)
CLASSIFICATION_FIELDS = [
    # Historical (2)
    'period', 'literary_movement',
    # Rhetorical (16)
    'register', 'rhetorical_genre', 'discursive_structure', 'discourse_type',
    'narrative_level', 'diegetic_mimetic', 'focalization', 'person',
    'deictic_orientation', 'addressee_type', 'deictic_object',
    'temporal_orientation', 'temporal_structure', 'tradition',
    # Formal (5)
    'mode', 'genre', 'stanza_structure', 'meter', 'rhyme'
]

def create_instruction_prompt(poem_text, title, author, year):
    """Create instruction prompt for the model."""
    prompt = f"""Classify the following poem across 28 metadata dimensions:

Title: {title}
Author: {author}
Year: {year if year else 'Unknown'}

Poem:
{poem_text}

Provide classifications for the following 28 fields:

HISTORICAL:
- period
- literary_movement

RHETORICAL:
- register
- rhetorical_genre
- discursive_structure
- discourse_type
- narrative_level
- diegetic_mimetic
- focalization
- person
- deictic_orientation
- addressee_type
- deictic_object
- temporal_orientation
- temporal_structure
- tradition

FORMAL:
- mode
- genre
- stanza_structure
- meter
- rhyme

Format your response as:
period: [value]
literary_movement: [value]
... (continue for all 28 fields)

Use "N/A" or empty string for fields that don't apply."""

    return prompt

def create_completion(example):
    """Create completion (target output) from classification fields."""
    completion_lines = []

    for field in CLASSIFICATION_FIELDS:
        value = example.get(field, '')
        # Handle empty/null values
        if value is None or value == '':
            value = ''
        completion_lines.append(f"{field}: {value}")

    return '\n'.join(completion_lines)

def format_for_instruction_tuning(example):
    """Format a single example as instruction-tuning pair."""
    prompt = create_instruction_prompt(
        example['text'],
        example['title'],
        example['author'],
        example.get('year_approx')
    )

    completion = create_completion(example)

    return {
        'prompt': prompt,
        'completion': completion,
        'metadata': {
            'training_idx': example['training_idx'],
            'corpus_poem_id': example['corpus_poem_id'],
            'title': example['title'],
            'author': example['author']
        }
    }

def main():
    print("="*80)
    print("PHASE 3B: FORMAT INSTRUCTION-TUNING DATASET")
    print("="*80)

    # Load training data
    print(f"\n1. Loading training data from {INPUT_FILE}...")
    examples = []
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            examples.append(json.loads(line))

    print(f"   ✓ Loaded {len(examples)} training examples")

    # Format for instruction tuning
    print("\n2. Formatting as instruction-tuning pairs...")
    formatted_examples = []
    for ex in examples:
        formatted = format_for_instruction_tuning(ex)
        formatted_examples.append(formatted)

    print(f"   ✓ Formatted {len(formatted_examples)} examples")

    # Split train/val (90/10%)
    print("\n3. Splitting train/validation sets (90/10%)...")
    random.seed(42)  # Reproducible split
    random.shuffle(formatted_examples)

    split_idx = int(len(formatted_examples) * 0.9)
    train_examples = formatted_examples[:split_idx]
    val_examples = formatted_examples[split_idx:]

    print(f"   ✓ Train: {len(train_examples)} examples")
    print(f"   ✓ Val:   {len(val_examples)} examples")

    # Save datasets
    print(f"\n4. Saving datasets...")
    with open(OUTPUT_TRAIN, 'w') as f:
        for ex in train_examples:
            f.write(json.dumps(ex) + '\n')
    print(f"   ✓ Train: {OUTPUT_TRAIN}")

    with open(OUTPUT_VAL, 'w') as f:
        for ex in val_examples:
            f.write(json.dumps(ex) + '\n')
    print(f"   ✓ Val:   {OUTPUT_VAL}")

    # Statistics
    print("\n" + "="*80)
    print("DATASET STATISTICS")
    print("="*80)

    # Sample prompt/completion
    sample = train_examples[0]
    print(f"\nSample prompt (first 500 chars):")
    print(sample['prompt'][:500] + "...")
    print(f"\nSample completion (first 300 chars):")
    print(sample['completion'][:300] + "...")

    # Token counts (rough estimate)
    total_train_chars = sum(len(ex['prompt']) + len(ex['completion']) for ex in train_examples)
    total_val_chars = sum(len(ex['prompt']) + len(ex['completion']) for ex in val_examples)

    print(f"\nApproximate statistics:")
    print(f"  Train total characters: {total_train_chars:,}")
    print(f"  Val total characters:   {total_val_chars:,}")
    print(f"  Avg tokens per example (train): ~{total_train_chars / len(train_examples) / 4:.0f}")
    print(f"  Avg tokens per example (val):   ~{total_val_chars / len(val_examples) / 4:.0f}")

    print("\n" + "="*80)
    print("✓ INSTRUCTION DATASET READY FOR FINE-TUNING")
    print("="*80)
    print(f"\nNext steps:")
    print(f"  1. Choose base model: Llama-3-8B or Mistral-7B")
    print(f"  2. Set up MLX training on M4 Max")
    print(f"  3. Fine-tune with LoRA (rank=16, alpha=32, ~1-2 hours)")
    print(f"  4. Validate on {len(val_examples)} hold-out poems")
    print(f"  5. Run inference on 116K HEPC corpus")
    print("="*80)

if __name__ == "__main__":
    main()
