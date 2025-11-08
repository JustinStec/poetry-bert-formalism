#!/usr/bin/env python3
"""
Train Hierarchical Multi-Objective Poetry-EEBO-BERT

Trains BERT with hierarchical losses:
- 0.5 * MLM (token level)
- 0.2 * Line contrastive
- 0.2 * Quatrain contrastive
- 0.1 * Sonnet contrastive

Starting from EEBO-BERT checkpoint, fine-tuning on Shakespeare's sonnets.
"""

import os
import sys
import argparse
import torch
from pathlib import Path
from transformers import BertTokenizer, TrainingArguments
from torch.utils.data import DataLoader

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from training.hierarchical_dataset import HierarchicalPoetryDataset, collate_hierarchical
from training.hierarchical_losses import HierarchicalLoss
from training.hierarchical_trainer import HierarchicalBertModel, HierarchicalTrainer


def parse_args():
    parser = argparse.ArgumentParser(description='Train hierarchical Poetry-EEBO-BERT')

    # Model paths
    parser.add_argument('--base-model', type=str,
                       default='/Users/justin/Library/CloudStorage/GoogleDrive-stecj2700@gmail.com/My Drive/AI and Poetry/EEBO_1595-1700/eebo_bert_finetuned',
                       help='Path to base EEBO-BERT model')
    parser.add_argument('--output-dir', type=str,
                       default='models/poetry_eebo_hierarchical_bert',
                       help='Output directory for trained model')

    # Data paths
    parser.add_argument('--train-data', type=str,
                       default='Data/eebo_sonnets_hierarchical_train.jsonl',
                       help='Path to training data')
    parser.add_argument('--val-data', type=str,
                       default='Data/eebo_sonnets_hierarchical_val.jsonl',
                       help='Path to validation data')

    # Training hyperparameters
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Training batch size')
    parser.add_argument('--num-epochs', type=int, default=10,
                       help='Number of training epochs')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate')
    parser.add_argument('--warmup-steps', type=int, default=100,
                       help='Number of warmup steps')
    parser.add_argument('--max-length', type=int, default=128,
                       help='Maximum sequence length')

    # Loss weights
    parser.add_argument('--mlm-weight', type=float, default=0.5,
                       help='Weight for MLM loss')
    parser.add_argument('--line-weight', type=float, default=0.2,
                       help='Weight for line contrastive loss')
    parser.add_argument('--quatrain-weight', type=float, default=0.2,
                       help='Weight for quatrain contrastive loss')
    parser.add_argument('--sonnet-weight', type=float, default=0.1,
                       help='Weight for sonnet contrastive loss')
    parser.add_argument('--temperature', type=float, default=0.07,
                       help='Temperature for contrastive losses')

    # Other settings
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    parser.add_argument('--device', type=str, default='auto',
                       help='Device (auto, cpu, cuda, mps)')

    return parser.parse_args()


def setup_device(device_arg: str) -> str:
    """
    Determine and setup the training device.

    Args:
        device_arg: 'auto', 'cpu', 'cuda', or 'mps'

    Returns:
        device string
    """
    if device_arg == 'auto':
        if torch.cuda.is_available():
            device = 'cuda'
        elif torch.backends.mps.is_available():
            device = 'mps'
        else:
            device = 'cpu'
    else:
        device = device_arg

    print(f"Using device: {device}")
    return device


def main():
    args = parse_args()

    print("="*70)
    print("HIERARCHICAL MULTI-OBJECTIVE POETRY-EEBO-BERT TRAINING")
    print("="*70)

    # Set random seed
    torch.manual_seed(args.seed)

    # Setup device
    device = setup_device(args.device)

    # Load tokenizer
    print(f"\nLoading tokenizer from {args.base_model}...")
    tokenizer = BertTokenizer.from_pretrained(args.base_model)
    print("✓ Tokenizer loaded")

    # Load datasets
    print(f"\nLoading training data from {args.train_data}...")
    train_dataset = HierarchicalPoetryDataset(
        data_path=args.train_data,
        tokenizer=tokenizer,
        max_length=args.max_length,
        mlm_probability=0.15
    )

    print(f"Loading validation data from {args.val_data}...")
    val_dataset = HierarchicalPoetryDataset(
        data_path=args.val_data,
        tokenizer=tokenizer,
        max_length=args.max_length,
        mlm_probability=0.15
    )
    print("✓ Datasets loaded")

    # Initialize model
    print(f"\nInitializing model from {args.base_model}...")
    model = HierarchicalBertModel(base_model_path=args.base_model)
    print("✓ Model initialized")

    # Initialize loss function
    loss_fn = HierarchicalLoss(
        temperature=args.temperature,
        mlm_weight=args.mlm_weight,
        line_weight=args.line_weight,
        quatrain_weight=args.quatrain_weight,
        sonnet_weight=args.sonnet_weight
    )

    print("\nLoss configuration:")
    print(f"  MLM weight: {args.mlm_weight}")
    print(f"  Line weight: {args.line_weight}")
    print(f"  Quatrain weight: {args.quatrain_weight}")
    print(f"  Sonnet weight: {args.sonnet_weight}")
    print(f"  Temperature: {args.temperature}")

    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        warmup_steps=args.warmup_steps,
        weight_decay=0.01,
        logging_dir=f"{args.output_dir}/logs",
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=3,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=(device == 'cuda'),  # Use mixed precision on CUDA
        dataloader_num_workers=0,  # Simplified for hierarchical data
        remove_unused_columns=False,  # Keep all columns for hierarchical processing
        report_to=["tensorboard"],
        seed=args.seed
    )

    # Initialize trainer
    trainer = HierarchicalTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=collate_hierarchical,
        loss_fn=loss_fn
    )

    print("\n" + "="*70)
    print("STARTING TRAINING")
    print("="*70)
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Batch size: {args.batch_size}")
    print(f"Epochs: {args.num_epochs}")
    print(f"Learning rate: {args.learning_rate}")
    print(f"Output: {args.output_dir}")
    print("="*70 + "\n")

    # Train
    try:
        trainer.train()

        print("\n" + "="*70)
        print("TRAINING COMPLETE")
        print("="*70)

        # Save final model
        final_model_path = f"{args.output_dir}/final"
        trainer.save_model(final_model_path)
        tokenizer.save_pretrained(final_model_path)

        print(f"✓ Final model saved to {final_model_path}")

        # Print loss history summary
        print("\nLoss history (last 10 steps):")
        if trainer.loss_history['total']:
            for i, (total, mlm, line, quatrain, sonnet) in enumerate(zip(
                trainer.loss_history['total'][-10:],
                trainer.loss_history['mlm'][-10:],
                trainer.loss_history['line'][-10:],
                trainer.loss_history['quatrain'][-10:],
                trainer.loss_history['sonnet'][-10:]
            )):
                print(f"  Step {i+1}: total={total:.4f} | mlm={mlm:.4f} | "
                      f"line={line:.4f} | quatrain={quatrain:.4f} | sonnet={sonnet:.4f}")

    except Exception as e:
        print(f"\n❌ Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
