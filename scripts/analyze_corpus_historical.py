#!/usr/bin/env python3
"""
Analyze poetry corpus with period-appropriate historical word embeddings.
Automatically selects the correct embedding model based on poem publication year.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import pickle
import gzip
from gensim.models import Word2Vec, KeyedVectors
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Paths
METADATA_FILE = "corpus_poem_metadata.csv"
POEMS_DIR = Path("corpus_texts")
OUTPUT_FILE = "Results/corpus_trajectory_results_historical.csv"

# Historical embedding paths
EEBO_MODEL = "Historical_Embeddings/EEBO_1595-1700/eebo_word2vec.model"
ECCO_DIR = "Historical_Embeddings/ECCO_1700s"
HISTWORDS_DIR = "Historical_Embeddings/HistWords_1800s/sgns"

# Cache for loaded models (to avoid reloading)
_model_cache: Dict[str, any] = {}


class HistWordsWrapper:
    """Wrapper to make HistWords .pkl/.npy format compatible with gensim API."""

    def __init__(self, vocab_file: str, vectors_file: str):
        with open(vocab_file, 'rb') as f:
            self.vocab_dict = pickle.load(f, encoding='latin1')
        self.vectors = np.load(vectors_file)

        # Create reverse lookup: word -> index
        self.word2idx = {word: idx for word, idx in self.vocab_dict.items()}

    def __contains__(self, word: str) -> bool:
        """Check if word is in vocabulary."""
        return word in self.word2idx

    def __getitem__(self, word: str) -> np.ndarray:
        """Get vector for word."""
        if word not in self.word2idx:
            raise KeyError(f"Word '{word}' not in vocabulary")
        idx = self.word2idx[word]
        return self.vectors[idx]

    def get_vector(self, word: str) -> np.ndarray:
        """Get vector for word (alternative interface)."""
        return self[word]


def get_model_for_year(year: int) -> Tuple[any, str]:
    """
    Load the appropriate historical embedding model for a given year.

    Returns:
        (model, model_name) tuple
    """
    cache_key = f"year_{year}"

    # Check cache first
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    # 1595-1700: EEBO
    if 1595 <= year <= 1700:
        if not Path(EEBO_MODEL).exists():
            raise FileNotFoundError(
                f"EEBO model not found at {EEBO_MODEL}. "
                "Training may still be in progress."
            )
        logging.info(f"Loading EEBO model (1595-1700) for year {year}...")
        model = Word2Vec.load(EEBO_MODEL)
        model_name = "EEBO_1595-1700"
        result = (model.wv, model_name)
        _model_cache[cache_key] = result
        return result

    # 1700-1799: ECCO (20-year periods)
    elif 1700 <= year <= 1799:
        # Determine which 20-year period
        if year < 1720:
            period = "1700-1719"
        elif year < 1740:
            period = "1720-1739"
        elif year < 1760:
            period = "1740-1759"
        elif year < 1780:
            period = "1760-1779"
        else:
            period = "1780-1799"

        model_file = f"{ECCO_DIR}/word2vec.ECCO.{period}.skipgram_n=10.model.txt.gz"
        vocab_file = f"{ECCO_DIR}/word2vec.ECCO.{period}.skipgram_n=10.model.vocab.txt"

        logging.info(f"Loading ECCO model ({period}) for year {year}...")
        model = KeyedVectors.load_word2vec_format(model_file, vocab_file)
        model_name = f"ECCO_{period}"
        result = (model, model_name)
        _model_cache[cache_key] = result
        return result

    # 1800-1999: HistWords (decade resolution)
    elif 1800 <= year <= 1999:
        # Round down to nearest decade
        decade = (year // 10) * 10

        vocab_file = f"{HISTWORDS_DIR}/{decade}-vocab.pkl"
        vectors_file = f"{HISTWORDS_DIR}/{decade}-w.npy"

        logging.info(f"Loading HistWords model ({decade}s) for year {year}...")
        model = HistWordsWrapper(vocab_file, vectors_file)
        model_name = f"HistWords_{decade}s"
        result = (model, model_name)
        _model_cache[cache_key] = result
        return result

    else:
        raise ValueError(f"No historical embedding model available for year {year}")


def cosine_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine distance between two vectors."""
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_product == 0:
        return 2.0
    return float(1.0 - (dot_product / norm_product))


def semantic_path_length(embeddings: np.ndarray) -> float:
    """Total semantic distance traversed."""
    distances = [cosine_distance(embeddings[i], embeddings[i+1])
                for i in range(len(embeddings)-1)]
    return float(sum(distances))


def net_semantic_displacement(embeddings: np.ndarray) -> float:
    """Direct semantic distance from first to last word."""
    return cosine_distance(embeddings[0], embeddings[-1])


def tortuosity(spl: float, nsd: float) -> float:
    """Ratio of path length to displacement."""
    return float(spl / nsd) if nsd > 0 else float('inf')


def exploration_radius(embeddings: np.ndarray) -> float:
    """Average distance from centroid."""
    centroid = np.mean(embeddings, axis=0)
    distances = [np.linalg.norm(emb - centroid) for emb in embeddings]
    return float(np.mean(distances))


def velocity_variance(embeddings: np.ndarray) -> float:
    """Variance in step sizes."""
    velocities = [cosine_distance(embeddings[i], embeddings[i+1])
                 for i in range(len(embeddings)-1)]
    return float(np.var(velocities))


def directional_consistency(embeddings: np.ndarray) -> float:
    """Measure of directional consistency using displacement vectors."""
    if len(embeddings) < 3:
        return 1.0

    displacements = [embeddings[i+1] - embeddings[i]
                    for i in range(len(embeddings)-1)]

    # Calculate pairwise cosine similarities between consecutive displacement vectors
    similarities = []
    for i in range(len(displacements)-1):
        d1, d2 = displacements[i], displacements[i+1]
        norm_product = np.linalg.norm(d1) * np.linalg.norm(d2)
        if norm_product > 0:
            similarity = np.dot(d1, d2) / norm_product
            similarities.append(similarity)

    return float(np.mean(similarities)) if similarities else 1.0


def analyze_poem(poem_file: Path, year: int, metadata: dict) -> Optional[dict]:
    """
    Analyze a single poem using period-appropriate embeddings.

    Args:
        poem_file: Path to poem text file
        year: Publication year
        metadata: Poem metadata dict

    Returns:
        Dictionary of results, or None if analysis fails
    """
    try:
        # Load appropriate model
        model, model_name = get_model_for_year(year)

        # Read and process poem
        with open(poem_file, 'r', encoding='utf-8') as f:
            text = f.read().lower()

        words = text.split()

        # Get embeddings for words in vocabulary
        embeddings = []
        valid_words = []

        for word in words:
            if word in model:
                if isinstance(model, HistWordsWrapper):
                    embeddings.append(model[word])
                else:
                    embeddings.append(model[word])
                valid_words.append(word)

        if len(embeddings) < 2:
            logging.warning(
                f"Skipping {metadata['title']} ({year}): "
                f"Only {len(embeddings)} words in vocabulary"
            )
            return None

        embeddings = np.array(embeddings)

        # Calculate metrics
        spl = semantic_path_length(embeddings)
        nsd = net_semantic_displacement(embeddings)
        t = tortuosity(spl, nsd)
        er = exploration_radius(embeddings)
        vv = velocity_variance(embeddings)
        dc = directional_consistency(embeddings)
        spl_norm = spl / len(embeddings) if len(embeddings) > 0 else 0

        results = {
            'filename': poem_file.name,
            'title': metadata['title'],
            'author': metadata['author'],
            'year': year,
            'mode': metadata['mode'],
            'embedding_model': model_name,
            'total_words': len(words),
            'valid_words': len(valid_words),
            'coverage': len(valid_words) / len(words),
            'spl': spl,
            'nsd': nsd,
            'tortuosity': t,
            'exploration_radius': er,
            'velocity_variance': vv,
            'directional_consistency': dc,
            'spl_normalized': spl_norm
        }

        logging.info(
            f"✓ {metadata['title']} ({year}) | "
            f"{model_name} | T={t:.2f} | "
            f"Coverage={results['coverage']:.1%}"
        )

        return results

    except FileNotFoundError as e:
        logging.error(f"Model file not found for {metadata['title']}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error analyzing {metadata['title']}: {e}")
        return None


def main():
    """Main analysis pipeline."""
    logging.info("="*60)
    logging.info("HISTORICAL EMBEDDING CORPUS ANALYSIS")
    logging.info("="*60)

    # Load metadata
    metadata_df = pd.read_csv(METADATA_FILE)
    logging.info(f"Loaded metadata for {len(metadata_df)} poems")

    # Analyze each poem
    results = []

    for idx, row in metadata_df.iterrows():
        poem_file = POEMS_DIR / row['filename']

        if not poem_file.exists():
            logging.warning(f"Poem file not found: {poem_file}")
            continue

        result = analyze_poem(
            poem_file=poem_file,
            year=row['year'],
            metadata=row.to_dict()
        )

        if result:
            results.append(result)

    # Save results
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('year')

        # Create output directory
        Path(OUTPUT_FILE).parent.mkdir(exist_ok=True)

        results_df.to_csv(OUTPUT_FILE, index=False)
        logging.info(f"\n{'='*60}")
        logging.info(f"Analysis complete!")
        logging.info(f"Successfully analyzed: {len(results)}/{len(metadata_df)} poems")
        logging.info(f"Results saved to: {OUTPUT_FILE}")
        logging.info(f"{'='*60}\n")

        # Print summary statistics by period
        logging.info("Summary by embedding model:")
        summary = results_df.groupby('embedding_model').agg({
            'tortuosity': ['mean', 'std', 'count'],
            'coverage': 'mean'
        }).round(3)
        print(summary)

    else:
        logging.error("No poems were successfully analyzed!")


if __name__ == "__main__":
    main()
