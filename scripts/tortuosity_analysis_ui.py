#!/usr/bin/env python3
"""
Tortuosity Analysis UI - Flexible Pipeline for Semantic Trajectory Research

Allows researchers to:
- Switch between embedding spaces (period-specific vs. aligned)
- Compare within-author, cross-author, cross-period
- Filter by prosodic form (meter, genre)
- Visualize semantic trajectories

Usage:
    python tortuosity_analysis_ui.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from gensim.models import KeyedVectors
from transformers import AutoModel, AutoTokenizer
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


@dataclass
class EmbeddingSpace:
    """Configuration for an embedding space."""
    name: str
    model_type: str  # 'word2vec', 'bert', 'prosody_bert'
    path: str
    period: Optional[str] = None
    is_aligned: bool = False


# Available embedding spaces
EMBEDDING_SPACES = {
    'eebo': EmbeddingSpace(
        name='EEBO (1595-1700)',
        model_type='word2vec',
        path='Data/Historical_Embeddings/Aligned/eebo_1595-1700_aligned.kv',
        period='1595-1700',
        is_aligned=True
    ),
    'eebo_raw': EmbeddingSpace(
        name='EEBO (Unaligned)',
        model_type='word2vec',
        path='Data/Historical_Embeddings/EEBO_1595-1700/eebo_word2vec.model',
        period='1595-1700',
        is_aligned=False
    ),
    'gutenberg': EmbeddingSpace(
        name='Gutenberg Poetry (Mixed Periods)',
        model_type='bert',
        path='gutenberg_bert_finetuned',  # From Google Drive
        period='1500-1900',
        is_aligned=False
    ),
    'gutenberg_aligned': EmbeddingSpace(
        name='Gutenberg (Aligned)',
        model_type='word2vec',  # Static embeddings extracted from BERT
        path='Data/Historical_Embeddings/Aligned/gutenberg_poetry_aligned.kv',
        period='1500-1900',
        is_aligned=True
    ),
    'google_news': EmbeddingSpace(
        name='Google News (Reference)',
        model_type='word2vec',
        path='Data/Historical_Embeddings/Aligned/google_news_300d_reference.kv',
        period='modern',
        is_aligned=True
    ),
}


class TortuosityAnalyzer:
    """Main analysis engine for semantic trajectories."""

    def __init__(self, embedding_space: str = 'eebo'):
        """Initialize with specified embedding space."""
        self.space_config = EMBEDDING_SPACES[embedding_space]
        self.model = self._load_model()
        print(f"✓ Loaded: {self.space_config.name}")

    def _load_model(self):
        """Load embedding model based on type."""
        if self.space_config.model_type == 'word2vec':
            return KeyedVectors.load(self.space_config.path)
        elif self.space_config.model_type == 'bert':
            # Load BERT and extract static embeddings
            model = AutoModel.from_pretrained(self.space_config.path)
            return model.embeddings.word_embeddings.weight.detach().numpy()
        else:
            raise ValueError(f"Unknown model type: {self.space_config.model_type}")

    def get_embeddings(self, words: List[str]) -> np.ndarray:
        """Extract embeddings for word sequence."""
        embeddings = []
        valid_words = []

        for word in words:
            try:
                if self.space_config.model_type == 'word2vec':
                    embeddings.append(self.model[word.lower()])
                else:  # BERT
                    # TODO: Implement BERT tokenization + embedding extraction
                    pass
                valid_words.append(word)
            except KeyError:
                pass  # Word not in vocabulary

        if len(embeddings) == 0:
            raise ValueError("No words found in vocabulary")

        return np.array(embeddings), valid_words

    def calculate_tortuosity(self, words: List[str]) -> Dict:
        """Calculate semantic trajectory metrics."""
        embeddings, valid_words = self.get_embeddings(words)

        # Calculate step-wise distances
        distances = []
        for i in range(len(embeddings) - 1):
            dist = np.linalg.norm(embeddings[i+1] - embeddings[i])
            distances.append(dist)

        # Semantic Path Length (SPL)
        spl = sum(distances)

        # Net Semantic Displacement (NSD)
        nsd = np.linalg.norm(embeddings[-1] - embeddings[0])

        # Tortuosity (T)
        tortuosity = spl / nsd if nsd > 0 else float('inf')

        # Return-to-Origin (RTO)
        rto = np.linalg.norm(embeddings[-1] - embeddings[0])

        # Exploration Radius (ER)
        centroid = np.mean(embeddings, axis=0)
        distances_from_center = [np.linalg.norm(emb - centroid) for emb in embeddings]
        er = np.mean(distances_from_center)

        return {
            'spl': spl,
            'nsd': nsd,
            'tortuosity': tortuosity,
            'rto': rto,
            'exploration_radius': er,
            'num_words': len(valid_words),
            'num_total': len(words),
            'coverage': len(valid_words) / len(words)
        }

    def visualize_trajectory(self, words: List[str], title: str = "Semantic Trajectory"):
        """Plot 2D trajectory using PCA."""
        embeddings, valid_words = self.get_embeddings(words)

        # Reduce to 2D
        pca = PCA(n_components=2)
        coords_2d = pca.fit_transform(embeddings)

        # Plot
        fig, ax = plt.subplots(figsize=(12, 8))

        # Trajectory line
        ax.plot(coords_2d[:, 0], coords_2d[:, 1], 'o-',
                alpha=0.6, linewidth=2, markersize=8)

        # Start/end markers
        ax.scatter(coords_2d[0, 0], coords_2d[0, 1],
                  c='green', s=200, marker='o', label='Start', zorder=5)
        ax.scatter(coords_2d[-1, 0], coords_2d[-1, 1],
                  c='red', s=200, marker='s', label='End', zorder=5)

        # Annotate words
        for i, word in enumerate(valid_words):
            ax.annotate(word, (coords_2d[i, 0], coords_2d[i, 1]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, alpha=0.7)

        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        ax.set_title(f'{title}\n{self.space_config.name}')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        return fig

    def compare_poems(self, poems: Dict[str, List[str]]) -> pd.DataFrame:
        """Compare tortuosity across multiple poems."""
        results = []

        for title, words in poems.items():
            metrics = self.calculate_tortuosity(words)
            metrics['title'] = title
            results.append(metrics)

        return pd.DataFrame(results)


class AnalysisPipeline:
    """High-level interface for common analysis patterns."""

    @staticmethod
    def within_author(author: str, poems: List[str],
                     embedding_space: str = 'eebo') -> pd.DataFrame:
        """Compare poems within single author."""
        analyzer = TortuosityAnalyzer(embedding_space)

        # TODO: Load poems from corpus
        # For now, placeholder
        poems_dict = {}
        for poem_title in poems:
            words = []  # Load from corpus
            poems_dict[poem_title] = words

        return analyzer.compare_poems(poems_dict)

    @staticmethod
    def cross_period(poem_period_pairs: List[tuple],
                    use_aligned: bool = True) -> pd.DataFrame:
        """Compare poems across historical periods.

        Args:
            poem_period_pairs: [(poem1, period1), (poem2, period2), ...]
            use_aligned: If True, use aligned embeddings for fair comparison
        """
        if use_aligned:
            # Use aligned space for cross-period comparison
            analyzer = TortuosityAnalyzer('gutenberg_aligned')
        else:
            raise ValueError("Cross-period comparison requires aligned embeddings")

        # TODO: Implement
        pass

    @staticmethod
    def by_meter(meter_type: str, poems: List[str]) -> pd.DataFrame:
        """Compare poems by prosodic form.

        Args:
            meter_type: 'iambic_pentameter', 'free_verse', etc.
        """
        # TODO: Implement prosodic filtering
        pass


# Interactive CLI
def interactive_mode():
    """Interactive command-line interface."""
    print("="*60)
    print("SEMANTIC TRAJECTORY ANALYSIS")
    print("="*60)
    print("\nAvailable embedding spaces:")
    for key, space in EMBEDDING_SPACES.items():
        aligned_str = " [ALIGNED]" if space.is_aligned else ""
        print(f"  {key}: {space.name}{aligned_str}")

    print("\nAnalysis types:")
    print("  1. Within-author comparison")
    print("  2. Cross-period comparison")
    print("  3. By prosodic form (meter)")
    print("  4. Custom analysis")
    print("  5. Exit")

    choice = input("\nSelect analysis type (1-5): ").strip()

    if choice == '1':
        print("\n--- Within-Author Analysis ---")
        author = input("Author name: ").strip()
        space = input("Embedding space (default: eebo): ").strip() or 'eebo'

        # TODO: List available poems by author
        print(f"\nAnalyzing {author} using {EMBEDDING_SPACES[space].name}")

    elif choice == '2':
        print("\n--- Cross-Period Comparison ---")
        print("Using aligned embeddings for fair comparison")

    elif choice == '3':
        print("\n--- By Prosodic Form ---")
        meter = input("Meter type (e.g., iambic_pentameter): ").strip()

    elif choice == '4':
        print("\n--- Custom Analysis ---")
        space = input("Embedding space: ").strip()
        analyzer = TortuosityAnalyzer(space)

        # Example analysis
        test_words = input("Enter words (space-separated): ").strip().split()
        metrics = analyzer.calculate_tortuosity(test_words)

        print("\nMetrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}" if isinstance(value, float) else f"  {key}: {value}")

        # Visualize
        if input("\nVisualize? (y/n): ").lower() == 'y':
            fig = analyzer.visualize_trajectory(test_words, "Custom Analysis")
            plt.show()

    else:
        print("Exiting.")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        print("Usage:")
        print("  python tortuosity_analysis_ui.py --interactive")
        print("\nOr import as module:")
        print("  from tortuosity_analysis_ui import TortuosityAnalyzer")
        print("  analyzer = TortuosityAnalyzer('eebo')")
        print("  metrics = analyzer.calculate_tortuosity(['shall', 'I', 'compare', 'thee'])")
