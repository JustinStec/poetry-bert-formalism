#!/usr/bin/env python3
"""
Extract Static Embeddings from BERT for Alignment

Takes a trained BERT model and extracts its token embedding layer,
converting it to KeyedVectors format for alignment with Word2Vec models.

Usage:
    python extract_bert_static_embeddings.py \
        --bert_path /path/to/gutenberg_bert_finetuned \
        --output_path gutenberg_bert_static.kv
"""

import argparse
import torch
from transformers import AutoModel, AutoTokenizer
from gensim.models import KeyedVectors
import numpy as np
from pathlib import Path


def extract_static_embeddings(bert_model_path: str, output_path: str):
    """
    Extract token embeddings from BERT and save as KeyedVectors.

    Args:
        bert_model_path: Path to fine-tuned BERT model
        output_path: Where to save KeyedVectors format
    """
    print(f"Loading BERT model from: {bert_model_path}")

    # Load model and tokenizer
    model = AutoModel.from_pretrained(bert_model_path)
    tokenizer = AutoTokenizer.from_pretrained(bert_model_path)

    print(f"Model loaded: {sum(p.numel() for p in model.parameters()):,} parameters")

    # Extract token embedding layer
    token_embeddings = model.embeddings.word_embeddings.weight.detach().cpu().numpy()
    print(f"Extracted embeddings: {token_embeddings.shape}")

    # Get vocabulary
    vocab = tokenizer.vocab
    print(f"Vocabulary size: {len(vocab):,} tokens")

    # Create mapping from token to embedding
    # Filter out special tokens if desired
    valid_tokens = []
    valid_embeddings = []

    for token, idx in vocab.items():
        # Skip special tokens like [PAD], [CLS], [SEP], [MASK]
        if token.startswith('[') and token.endswith(']'):
            continue

        # Skip subword tokens (##) if you only want full words
        # if token.startswith('##'):
        #     continue

        valid_tokens.append(token)
        valid_embeddings.append(token_embeddings[idx])

    valid_embeddings = np.array(valid_embeddings)
    print(f"Valid tokens (after filtering): {len(valid_tokens):,}")

    # Create KeyedVectors object
    print("Creating KeyedVectors...")
    kv = KeyedVectors(vector_size=valid_embeddings.shape[1])
    kv.add_vectors(valid_tokens, valid_embeddings)

    # Save
    print(f"Saving to: {output_path}")
    kv.save(output_path)

    print("✓ Done!")
    print(f"\nYou can now use this in alignment:")
    print(f"  from gensim.models import KeyedVectors")
    print(f"  model = KeyedVectors.load('{output_path}')")

    # Basic tests
    print("\nTesting embeddings:")
    test_words = ['love', 'death', 'nature', 'beauty', 'time']
    found = [w for w in test_words if w in kv]
    print(f"  Found {len(found)}/{len(test_words)} test words: {found}")

    if len(found) >= 2:
        w1, w2 = found[0], found[1]
        sim = kv.similarity(w1, w2)
        print(f"  Similarity('{w1}', '{w2}'): {sim:.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract static embeddings from BERT for alignment"
    )
    parser.add_argument(
        '--bert_path',
        required=True,
        help='Path to fine-tuned BERT model directory'
    )
    parser.add_argument(
        '--output_path',
        required=True,
        help='Output path for KeyedVectors (.kv extension recommended)'
    )
    parser.add_argument(
        '--include_subwords',
        action='store_true',
        help='Include BERT subword tokens (##token)'
    )

    args = parser.parse_args()

    extract_static_embeddings(args.bert_path, args.output_path)


if __name__ == '__main__':
    main()
