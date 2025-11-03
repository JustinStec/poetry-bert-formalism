#!/usr/bin/env python3
"""
Align historical word embedding spaces using Orthogonal Procrustes transformation.

This script aligns EEBO (1595-1700), ECCO (1700-1799), and HistWords (1800-1999)
embeddings to modern Google News embeddings as the reference space.

Methodology:
- Uses Orthogonal Procrustes: Q* = argmin ||T1 - T2 * Q||_F
- Aligns on anchor words (intersection vocabulary)
- Preserves distances within each space (orthogonal transformation)

Based on: Hamilton et al. (2016) "Diachronic Word Embeddings Reveal Statistical
Laws of Semantic Change"
"""

import os
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Set, Dict
from gensim.models import Word2Vec, KeyedVectors
import gensim.downloader as api
import logging
from scipy.linalg import orthogonal_procrustes

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Paths
EEBO_MODEL = "Historical_Embeddings/EEBO_1595-1700/eebo_word2vec.model"
ECCO_DIR = "Historical_Embeddings/ECCO_1700s"
HISTWORDS_DIR = "Historical_Embeddings/HistWords_1800s/sgns"
OUTPUT_DIR = "Historical_Embeddings/Aligned"

# ECCO periods
ECCO_PERIODS = [
    "1700-1719",
    "1720-1739",
    "1740-1759",
    "1760-1779",
    "1780-1799"
]

# HistWords decades
HISTWORDS_DECADES = list(range(1800, 2000, 10))


class HistWordsWrapper:
    """Wrapper for HistWords .pkl/.npy format."""

    def __init__(self, vocab_file: str, vectors_file: str):
        with open(vocab_file, 'rb') as f:
            self.vocab_dict = pickle.load(f, encoding='latin1')
        self.vectors = np.load(vectors_file)
        self.word2idx = {word: idx for word, idx in self.vocab_dict.items()}

    def __contains__(self, word: str) -> bool:
        return word in self.word2idx

    def __getitem__(self, word: str) -> np.ndarray:
        if word not in self.word2idx:
            raise KeyError(f"Word '{word}' not in vocabulary")
        idx = self.word2idx[word]
        return self.vectors[idx]

    @property
    def index_to_key(self) -> List[str]:
        """Return list of words in vocabulary."""
        return list(self.word2idx.keys())


def find_anchor_vocabulary(*models) -> Set[str]:
    """
    Find intersection vocabulary across all embedding models.

    Args:
        *models: Variable number of embedding models

    Returns:
        Set of words present in ALL models
    """
    logging.info(f"Finding anchor vocabulary across {len(models)} models...")

    # Get vocabulary sets
    vocab_sets = []
    for i, model in enumerate(models):
        if isinstance(model, HistWordsWrapper):
            vocab = set(model.index_to_key)
        elif hasattr(model, 'key_to_index'):
            vocab = set(model.key_to_index.keys())
        elif hasattr(model, 'vocab'):
            vocab = set(model.vocab.keys())
        else:
            vocab = set(model.index_to_key)

        logging.info(f"  Model {i+1}: {len(vocab):,} words")
        vocab_sets.append(vocab)

    # Find intersection
    anchor_vocab = vocab_sets[0]
    for vocab in vocab_sets[1:]:
        anchor_vocab = anchor_vocab.intersection(vocab)

    logging.info(f"Anchor vocabulary: {len(anchor_vocab):,} words")
    return anchor_vocab


def get_anchor_matrix(model, anchor_words: List[str]) -> np.ndarray:
    """
    Extract embedding matrix for anchor words.

    Args:
        model: Embedding model
        anchor_words: List of anchor words

    Returns:
        Matrix of shape (n_words, embedding_dim)
    """
    vectors = []
    for word in anchor_words:
        if isinstance(model, HistWordsWrapper):
            vectors.append(model[word])
        else:
            vectors.append(model[word])
    return np.array(vectors)


def align_to_reference(
    target_model,
    reference_model,
    anchor_words: List[str]
) -> Tuple[np.ndarray, float]:
    """
    Align target embedding space to reference space using Orthogonal Procrustes.

    Args:
        target_model: Model to be aligned
        reference_model: Reference model (modern embeddings)
        anchor_words: List of words to use for alignment

    Returns:
        (Q, error) - Orthogonal transformation matrix and alignment error
    """
    logging.info(f"Aligning using {len(anchor_words):,} anchor words...")

    # Extract anchor word matrices
    T1 = get_anchor_matrix(reference_model, anchor_words)  # Reference
    T2 = get_anchor_matrix(target_model, anchor_words)     # Target

    # Compute Orthogonal Procrustes transformation
    # Q minimizes ||T1 - T2 @ Q||_F
    Q, scale = orthogonal_procrustes(T2, T1)

    # Calculate alignment error
    aligned = T2 @ Q
    error = np.linalg.norm(T1 - aligned, 'fro')

    logging.info(f"Alignment error (Frobenius norm): {error:.2f}")

    return Q, error


def save_aligned_model(
    original_model,
    Q: np.ndarray,
    output_path: str,
    model_name: str
):
    """
    Apply transformation Q to all vectors and save aligned model.

    Args:
        original_model: Original embedding model
        Q: Orthogonal transformation matrix
        output_path: Path to save aligned model
        model_name: Descriptive name for logging
    """
    logging.info(f"Transforming and saving {model_name}...")

    # Get all words and vectors
    if isinstance(original_model, HistWordsWrapper):
        words = original_model.index_to_key
        vectors = original_model.vectors
    elif hasattr(original_model, 'key_to_index'):
        words = list(original_model.key_to_index.keys())
        vectors = original_model.vectors
    else:
        words = original_model.index_to_key
        vectors = original_model.vectors

    # Apply transformation
    aligned_vectors = vectors @ Q

    # Create new KeyedVectors object
    aligned_model = KeyedVectors(vector_size=aligned_vectors.shape[1])
    aligned_model.add_vectors(words, aligned_vectors)

    # Save
    aligned_model.save(output_path)
    logging.info(f"Saved to: {output_path}")


def main():
    """Main alignment pipeline."""

    logging.info("="*60)
    logging.info("HISTORICAL EMBEDDING ALIGNMENT")
    logging.info("="*60)

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Step 1: Load reference model (modern Google News)
    logging.info("\n" + "="*60)
    logging.info("Step 1: Loading reference model (Google News 300D)")
    logging.info("="*60)
    reference_model = api.load('word2vec-google-news-300')
    logging.info(f"Reference vocabulary: {len(reference_model):,} words")

    # Step 2: Load and align EEBO (1595-1700)
    logging.info("\n" + "="*60)
    logging.info("Step 2: Aligning EEBO (1595-1700)")
    logging.info("="*60)

    eebo_model = Word2Vec.load(EEBO_MODEL)
    eebo_wv = eebo_model.wv

    # Find anchor vocabulary
    anchor_words_eebo = list(find_anchor_vocabulary(reference_model, eebo_wv))

    # Align
    Q_eebo, error_eebo = align_to_reference(
        eebo_wv,
        reference_model,
        anchor_words_eebo
    )

    # Save aligned model
    eebo_output = f"{OUTPUT_DIR}/eebo_1595-1700_aligned.kv"
    save_aligned_model(eebo_wv, Q_eebo, eebo_output, "EEBO")

    # Step 3: Load and align ECCO models (1700-1799)
    logging.info("\n" + "="*60)
    logging.info("Step 3: Aligning ECCO models (1700-1799)")
    logging.info("="*60)

    for period in ECCO_PERIODS:
        logging.info(f"\n--- ECCO {period} ---")

        model_file = f"{ECCO_DIR}/word2vec.ECCO.{period}.skipgram_n=10.model.txt.gz"
        vocab_file = f"{ECCO_DIR}/word2vec.ECCO.{period}.skipgram_n=10.model.vocab.txt"

        if not Path(model_file).exists():
            logging.warning(f"Model file not found: {model_file}")
            continue

        # Load model
        ecco_model = KeyedVectors.load_word2vec_format(model_file, vocab_file)

        # Find anchor vocabulary
        anchor_words_ecco = list(find_anchor_vocabulary(reference_model, ecco_model))

        # Align
        Q_ecco, error_ecco = align_to_reference(
            ecco_model,
            reference_model,
            anchor_words_ecco
        )

        # Save aligned model
        ecco_output = f"{OUTPUT_DIR}/ecco_{period}_aligned.kv"
        save_aligned_model(ecco_model, Q_ecco, ecco_output, f"ECCO {period}")

    # Step 4: Load and align HistWords models (1800-1999)
    logging.info("\n" + "="*60)
    logging.info("Step 4: Aligning HistWords models (1800-1999)")
    logging.info("="*60)

    for decade in HISTWORDS_DECADES:
        logging.info(f"\n--- HistWords {decade}s ---")

        vocab_file = f"{HISTWORDS_DIR}/{decade}-vocab.pkl"
        vectors_file = f"{HISTWORDS_DIR}/{decade}-w.npy"

        if not Path(vocab_file).exists() or not Path(vectors_file).exists():
            logging.warning(f"Model files not found for {decade}s")
            continue

        # Load model
        histwords_model = HistWordsWrapper(vocab_file, vectors_file)

        # Find anchor vocabulary
        anchor_words_hw = list(find_anchor_vocabulary(reference_model, histwords_model))

        # Align
        Q_hw, error_hw = align_to_reference(
            histwords_model,
            reference_model,
            anchor_words_hw
        )

        # Save aligned model
        hw_output = f"{OUTPUT_DIR}/histwords_{decade}s_aligned.kv"
        save_aligned_model(histwords_model, Q_hw, hw_output, f"HistWords {decade}s")

    # Step 5: Save reference model (no transformation)
    logging.info("\n" + "="*60)
    logging.info("Step 5: Saving reference model (Google News)")
    logging.info("="*60)

    reference_output = f"{OUTPUT_DIR}/google_news_300d_reference.kv"
    reference_model.save(reference_output)
    logging.info(f"Reference model saved to: {reference_output}")

    # Summary
    logging.info("\n" + "="*60)
    logging.info("ALIGNMENT COMPLETE!")
    logging.info("="*60)
    logging.info(f"Aligned models saved to: {OUTPUT_DIR}/")
    logging.info("\nNext steps:")
    logging.info("1. Run analyze_corpus_aligned.py to analyze poems in unified space")
    logging.info("2. Compare trajectory metrics across aligned embeddings")
    logging.info("3. Visualize semantic drift and formal patterns")


if __name__ == "__main__":
    main()
