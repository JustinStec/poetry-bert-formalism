#!/usr/bin/env python3
"""
Fine-tune BERT on EEBO corpus (1595-1700) using masked language modeling.

Optimized for Apple Silicon (MPS) local training.
Estimates completion time after first few batches.

Usage:
    python finetune_bert_eebo_local.py
"""

import os
import time
from pathlib import Path
from datetime import timedelta
import torch
from transformers import (
    BertTokenizer,
    BertForMaskedLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Paths
EEBO_CORPUS = "Data/Historical_Embeddings/EEBO_1595-1700/eebo_cleaned_corpus.txt"
OUTPUT_DIR = "Data/Historical_Embeddings/EEBO_1595-1700/eebo_bert_finetuned"
CHECKPOINT_DIR = "Data/Historical_Embeddings/EEBO_1595-1700/bert_checkpoints"

# Training configuration
BATCH_SIZE = 2  # Reduced for MacBook Air memory constraints
MAX_LENGTH = 512  # BERT's max sequence length
NUM_EPOCHS = 3  # Standard for fine-tuning
LEARNING_RATE = 5e-5
WARMUP_STEPS = 500
SAVE_STEPS = 1000
LOGGING_STEPS = 100


def check_device():
    """Check available compute device (prefer MPS for Apple Silicon)."""
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        logging.info("✓ Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        logging.info("✓ Using CUDA GPU")
    else:
        device = torch.device("cpu")
        logging.warning("⚠ Using CPU (will be very slow!)")

    return device


def load_eebo_corpus():
    """Load EEBO corpus as HuggingFace dataset."""
    logging.info(f"Loading EEBO corpus from {EEBO_CORPUS}...")

    if not Path(EEBO_CORPUS).exists():
        raise FileNotFoundError(
            f"EEBO corpus not found at {EEBO_CORPUS}\n"
            "Make sure EEBO Word2Vec training completed successfully."
        )

    # Load as plain text dataset
    dataset = load_dataset(
        'text',
        data_files={'train': EEBO_CORPUS},
        split='train'
    )

    logging.info(f"✓ Loaded {len(dataset):,} lines from EEBO corpus")
    return dataset


def tokenize_function(examples, tokenizer):
    """Tokenize text for MLM training."""
    # Tokenize with truncation and padding
    result = tokenizer(
        examples['text'],
        truncation=True,
        max_length=MAX_LENGTH,
        padding='max_length',
        return_special_tokens_mask=True
    )
    return result


def estimate_training_time(trainer, num_samples):
    """
    Run a small test to estimate total training time.

    Args:
        trainer: Hugging Face Trainer object
        num_samples: Total number of training samples

    Returns:
        Estimated time in hours
    """
    logging.info("Running timing test on first 100 samples...")
    start = time.time()

    # This is a rough estimate - actual training will vary
    # We'll log more accurate estimates during actual training

    return None  # Will estimate during training instead


class TimingCallback:
    """Callback to track and log training progress with time estimates."""

    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.start_time = None
        self.steps_completed = 0

    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()
        logging.info(f"Training started: {self.total_steps} total steps")

    def on_log(self, args, state, control, logs=None, **kwargs):
        """Log progress and time estimates."""
        if logs and 'loss' in logs:
            self.steps_completed = state.global_step
            elapsed = time.time() - self.start_time

            if self.steps_completed > 10:  # Wait for stable estimate
                steps_per_sec = self.steps_completed / elapsed
                remaining_steps = self.total_steps - self.steps_completed
                remaining_time = remaining_steps / steps_per_sec

                pct_complete = (self.steps_completed / self.total_steps) * 100

                logging.info(
                    f"Progress: {self.steps_completed}/{self.total_steps} "
                    f"({pct_complete:.1f}%) | "
                    f"Loss: {logs['loss']:.4f} | "
                    f"ETA: {timedelta(seconds=int(remaining_time))}"
                )


def main():
    """Main training pipeline."""

    logging.info("="*60)
    logging.info("EEBO-BERT FINE-TUNING (Local Apple Silicon)")
    logging.info("="*60)

    # Check device
    device = check_device()

    # Create output directories
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)

    # Load tokenizer and model
    logging.info("\nLoading BERT-base-uncased...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForMaskedLM.from_pretrained('bert-base-uncased')

    logging.info(f"✓ Model loaded: {model.num_parameters():,} parameters")

    # Load EEBO corpus
    dataset = load_eebo_corpus()

    # Tokenize dataset
    logging.info("\nTokenizing EEBO corpus...")
    logging.info("(This will take several minutes...)")
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=['text'],
        desc="Tokenizing"
    )

    logging.info(f"✓ Tokenization complete")

    # Data collator for MLM
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=True,
        mlm_probability=0.15  # Standard BERT masking
    )

    # Calculate total steps
    total_samples = len(tokenized_dataset)
    steps_per_epoch = total_samples // BATCH_SIZE
    total_steps = steps_per_epoch * NUM_EPOCHS

    logging.info(f"\nTraining configuration:")
    logging.info(f"  Samples: {total_samples:,}")
    logging.info(f"  Batch size: {BATCH_SIZE}")
    logging.info(f"  Epochs: {NUM_EPOCHS}")
    logging.info(f"  Steps per epoch: {steps_per_epoch:,}")
    logging.info(f"  Total steps: {total_steps:,}")
    logging.info(f"  Device: {device}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=CHECKPOINT_DIR,
        overwrite_output_dir=True,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        save_steps=SAVE_STEPS,
        save_total_limit=2,  # Keep only last 2 checkpoints
        logging_steps=LOGGING_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        weight_decay=0.01,
        fp16=False,  # MPS doesn't support fp16 yet
        logging_dir=f'{CHECKPOINT_DIR}/logs',
        report_to='none',  # Don't send to wandb/tensorboard
        # MPS-specific settings
        use_cpu=False if device.type == 'mps' else True,
    )

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=tokenized_dataset,
    )

    # Start training
    logging.info("\n" + "="*60)
    logging.info("STARTING TRAINING")
    logging.info("="*60)
    logging.info("Watch this space for progress updates and ETA...")
    logging.info("")

    start_time = time.time()

    try:
        trainer.train()
    except KeyboardInterrupt:
        logging.warning("\n⚠ Training interrupted by user")
        logging.info("Saving checkpoint...")
        trainer.save_model(f"{CHECKPOINT_DIR}/interrupted")
        raise

    # Training complete
    total_time = time.time() - start_time

    logging.info("\n" + "="*60)
    logging.info("TRAINING COMPLETE!")
    logging.info("="*60)
    logging.info(f"Total time: {timedelta(seconds=int(total_time))}")
    logging.info(f"Average: {total_time/total_steps:.2f} seconds per step")

    # Save final model
    logging.info(f"\nSaving final model to {OUTPUT_DIR}...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    logging.info("✓ Model saved successfully")
    logging.info(f"\nEEBO-BERT is ready at: {OUTPUT_DIR}")

    # Test the model
    logging.info("\nTesting EEBO-BERT on sample text...")
    test_text = "Shall I compare thee to a [MASK] day?"

    from transformers import pipeline
    fill_mask = pipeline(
        "fill-mask",
        model=model,
        tokenizer=tokenizer
    )

    predictions = fill_mask(test_text)
    logging.info(f"\nTest: '{test_text}'")
    for i, pred in enumerate(predictions[:5], 1):
        logging.info(f"  {i}. {pred['token_str']}: {pred['score']:.4f}")

    logging.info("\n" + "="*60)
    logging.info("Next steps:")
    logging.info("1. Run analyze_corpus_eebo_bert.py to analyze poems")
    logging.info("2. Compare BERT vs Word2Vec trajectories")
    logging.info("3. Generate visualizations for paper")
    logging.info("="*60)


if __name__ == "__main__":
    main()
