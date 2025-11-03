"""
Trajectory Metrics for Semantic Analysis of Poetry

This module implements metrics for analyzing semantic trajectories through
embedding space. See metrics_definitions.md for formal mathematical definitions.

Author: Claude Code
Date: 2025-01-23
"""

import numpy as np
from sklearn.decomposition import PCA
from typing import List, Dict, Tuple

def get_sequential_embeddings(words: List[str], model, verbose: bool = True) -> Tuple[np.ndarray, List[str]]:
    """
    Extract sequential word embeddings, preserving order and handling missing words.

    Parameters
    ----------
    words : List[str]
        Ordered list of words from the text
    model : gensim.models.KeyedVectors
        Pre-trained word embedding model
    verbose : bool
        Whether to print warnings for missing words

    Returns
    -------
    embeddings : np.ndarray, shape (n_valid_words, embedding_dim)
        Sequential embeddings for words found in vocabulary
    valid_words : List[str]
        Words that were found in the model vocabulary

    Notes
    -----
    Words not in the model vocabulary are skipped. The proportion of missing
    words should be reported in analysis.
    """
    embeddings = []
    valid_words = []

    for word in words:
        try:
            # Try lowercase first (Word2Vec is case-sensitive)
            if word in model:
                embeddings.append(model[word])
                valid_words.append(word)
            elif word.lower() in model:
                embeddings.append(model[word.lower()])
                valid_words.append(word.lower())
            elif word.capitalize() in model:
                embeddings.append(model[word.capitalize()])
                valid_words.append(word.capitalize())
            else:
                if verbose:
                    print(f"Word '{word}' not found in vocabulary. Skipping...")
        except KeyError:
            if verbose:
                print(f"Word '{word}' not found in vocabulary. Skipping...")

    if len(embeddings) == 0:
        raise ValueError("No words found in model vocabulary!")

    return np.array(embeddings), valid_words


def cosine_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate cosine distance between two vectors.

    Parameters
    ----------
    v1, v2 : np.ndarray
        Embedding vectors

    Returns
    -------
    distance : float
        Cosine distance = 1 - cosine_similarity
        Range: [0, 2] where 0 = identical, 2 = opposite
    """
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)

    if norm_product == 0:
        return 2.0  # Maximum distance for zero vectors

    cosine_sim = dot_product / norm_product
    return 1.0 - cosine_sim


def semantic_path_length(embeddings: np.ndarray) -> float:
    """
    Calculate total semantic distance traversed through sequential embeddings.

    SPL = Σ(i=1 to n-1) d(v_i, v_{i+1})

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings

    Returns
    -------
    spl : float
        Total semantic path length

    Notes
    -----
    Higher values indicate more semantic movement/exploration.
    For length-normalized version, divide by (n-1).
    """
    if len(embeddings) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(len(embeddings) - 1):
        total_distance += cosine_distance(embeddings[i], embeddings[i+1])

    return total_distance


def net_semantic_displacement(embeddings: np.ndarray) -> float:
    """
    Calculate direct semantic distance from beginning to end.

    NSD = d(v_1, v_n)

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings

    Returns
    -------
    nsd : float
        Net displacement from start to end
    """
    if len(embeddings) < 2:
        return 0.0

    return cosine_distance(embeddings[0], embeddings[-1])


def tortuosity(embeddings: np.ndarray, epsilon: float = 1e-6) -> float:
    """
    Calculate tortuosity: ratio of path length to net displacement.

    T = SPL / NSD

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings
    epsilon : float
        Small value to avoid division by zero

    Returns
    -------
    t : float
        Tortuosity measure
        T ≈ 1: Straight path
        T >> 1: Winding, exploratory path

    Notes
    -----
    This is a key metric for the dispersion+integration hypothesis.
    High tortuosity = exploring distant domains while maintaining coherence.
    """
    spl = semantic_path_length(embeddings)
    nsd = net_semantic_displacement(embeddings)

    # Avoid division by zero
    if nsd < epsilon:
        return np.inf if spl > epsilon else 1.0

    return spl / max(nsd, epsilon)


def return_to_origin(embeddings: np.ndarray) -> float:
    """
    Calculate semantic distance from end back to beginning.

    RTO = d(v_n, v_1)

    Note: RTO = NSD (same calculation), but conceptually frames
    the ending's relationship to the beginning.

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings

    Returns
    -------
    rto : float
        Distance from end back to start
        Low RTO: Circular structure (ending echoes beginning)
        High RTO: Linear structure (ending distant from beginning)
    """
    return net_semantic_displacement(embeddings)


def exploration_radius(embeddings: np.ndarray) -> float:
    """
    Calculate average distance of all words from semantic centroid.

    ER = (1/n) Σ d(v_i, c) where c = (1/n) Σ v_i

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings

    Returns
    -------
    er : float
        Average distance from centroid
        High ER: Words span diverse semantic regions
        Low ER: Words cluster tightly
    """
    if len(embeddings) < 2:
        return 0.0

    # Calculate centroid
    centroid = np.mean(embeddings, axis=0)

    # Calculate average distance to centroid
    distances = [cosine_distance(emb, centroid) for emb in embeddings]
    return np.mean(distances)


def velocity_profile_variance(embeddings: np.ndarray) -> float:
    """
    Calculate variance in step-by-step semantic velocity.

    Let δ_i = d(v_i, v_{i+1}) be step distances
    VPV = Var(δ)

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings

    Returns
    -------
    vpv : float
        Variance of step distances
        Low VPV: Smooth, regular progression
        High VPV: Alternating fast/slow, jumpy movement

    Notes
    -----
    Real poetry should have controlled variation (deliberate pacing).
    Random text has high variance. Conventional text has low variance.
    """
    if len(embeddings) < 3:
        return 0.0

    # Calculate step distances
    step_distances = []
    for i in range(len(embeddings) - 1):
        step_distances.append(cosine_distance(embeddings[i], embeddings[i+1]))

    return np.var(step_distances)


def directional_consistency(embeddings: np.ndarray, n_components: int = 2) -> float:
    """
    Measure how often trajectory changes direction in semantic space.

    Requires PCA projection to lower dimensions first.
    DC = (1/(n-2)) Σ cos(θ_i) where θ_i is angle between consecutive vectors

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings
    n_components : int
        Number of PCA components to project to (2 or 3)

    Returns
    -------
    dc : float
        Directional consistency measure
        DC ≈ 1: Consistent direction (straight path)
        DC ≈ 0: Frequent perpendicular turns
        DC ≈ -1: Frequent reversals

    Notes
    -----
    This metric is representation-dependent (requires PCA).
    """
    if len(embeddings) < 3:
        return 1.0

    # Project to lower dimensions
    pca = PCA(n_components=n_components)
    points = pca.fit_transform(embeddings)

    # Calculate direction vectors
    angles_cos = []
    for i in range(len(points) - 2):
        # Vector from point i to i+1
        v1 = points[i+1] - points[i]
        # Vector from point i+1 to i+2
        v2 = points[i+2] - points[i+1]

        # Calculate cosine of angle between vectors
        norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm_product > 0:
            cos_angle = np.dot(v1, v2) / norm_product
            angles_cos.append(cos_angle)

    if len(angles_cos) == 0:
        return 1.0

    return np.mean(angles_cos)


def calculate_all_metrics(embeddings: np.ndarray, words: List[str] = None) -> Dict[str, float]:
    """
    Calculate all trajectory metrics for a sequence of embeddings.

    Parameters
    ----------
    embeddings : np.ndarray, shape (n_words, embedding_dim)
        Sequential word embeddings
    words : List[str], optional
        Corresponding words (for reference)

    Returns
    -------
    metrics : Dict[str, float]
        Dictionary containing all trajectory metrics:
        - spl: Semantic Path Length
        - nsd: Net Semantic Displacement
        - tortuosity: SPL / NSD
        - rto: Return-to-Origin
        - exploration_radius: Average distance from centroid
        - velocity_variance: Variance in step distances
        - directional_consistency: Measure of path coherence
        - num_words: Number of words in sequence
        - spl_normalized: SPL / (n-1)

    Examples
    --------
    >>> metrics = calculate_all_metrics(oread_embeddings, oread_words)
    >>> print(f"Tortuosity: {metrics['tortuosity']:.3f}")
    """
    n = len(embeddings)

    metrics = {
        'spl': semantic_path_length(embeddings),
        'nsd': net_semantic_displacement(embeddings),
        'tortuosity': tortuosity(embeddings),
        'rto': return_to_origin(embeddings),
        'exploration_radius': exploration_radius(embeddings),
        'velocity_variance': velocity_profile_variance(embeddings),
        'directional_consistency': directional_consistency(embeddings),
        'num_words': n,
    }

    # Add normalized version of SPL
    if n > 1:
        metrics['spl_normalized'] = metrics['spl'] / (n - 1)
    else:
        metrics['spl_normalized'] = 0.0

    return metrics


def print_metrics_report(metrics: Dict[str, float], title: str = "Trajectory Metrics"):
    """
    Print a formatted report of trajectory metrics.

    Parameters
    ----------
    metrics : Dict[str, float]
        Metrics dictionary from calculate_all_metrics()
    title : str
        Title for the report
    """
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}\n")

    print(f"Number of words: {metrics['num_words']}")
    print(f"\n--- Dispersion Metrics ---")
    print(f"Semantic Path Length (SPL):      {metrics['spl']:.4f}")
    print(f"  Normalized (avg step):          {metrics['spl_normalized']:.4f}")
    print(f"Exploration Radius (ER):          {metrics['exploration_radius']:.4f}")

    print(f"\n--- Integration Metrics ---")
    print(f"Net Displacement (NSD):           {metrics['nsd']:.4f}")
    print(f"Return-to-Origin (RTO):           {metrics['rto']:.4f}")
    print(f"Tortuosity (T = SPL/NSD):         {metrics['tortuosity']:.4f}")

    print(f"\n--- Trajectory Dynamics ---")
    print(f"Velocity Variance (VPV):          {metrics['velocity_variance']:.4f}")
    print(f"Directional Consistency (DC):     {metrics['directional_consistency']:.4f}")

    print(f"\n{'=' * 60}\n")


# Example usage block (can be run as script or imported)
if __name__ == "__main__":
    print("Trajectory Metrics Module")
    print("See metrics_definitions.md for formal definitions")
    print("\nImport this module to use trajectory analysis functions:")
    print("  from trajectory_metrics import calculate_all_metrics")
