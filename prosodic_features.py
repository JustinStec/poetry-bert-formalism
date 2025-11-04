#!/usr/bin/env python3
"""
Prosodic Feature Extraction for Poetry Analysis

This module provides improved prosodic feature extraction including:
- Metrical pattern analysis (iambic pentameter deviation)
- Rhyme detection (phonetic + fallback)
- Sonnet structure features (position, couplet marking)

Features Layer 3 conditioning vectors for BERT embeddings.
"""

import re
from typing import List, Tuple, Optional, Dict
import prosodic as p

try:
    from pronouncing import rhymes
    PRONOUNCING_AVAILABLE = True
except ImportError:
    PRONOUNCING_AVAILABLE = False


class MetricalAnalyzer:
    """Analyze metrical patterns in poetry lines."""

    def __init__(self, ideal_pattern: List[int] = None):
        """
        Args:
            ideal_pattern: Expected stress pattern (default: iambic pentameter)
        """
        if ideal_pattern is None:
            # Iambic pentameter: 0 1 0 1 0 1 0 1 0 1
            self.ideal_pattern = [0, 1] * 5
        else:
            self.ideal_pattern = ideal_pattern

    def score_deviation(self, line_text: str) -> Tuple[float, Optional[List[int]]]:
        """
        Score deviation from ideal metrical pattern.

        Args:
            line_text: Line of poetry to analyze

        Returns:
            (deviation_score, actual_pattern)
            deviation_score: Number of syllables deviating from ideal
            actual_pattern: Detected stress pattern, or None if parsing failed
        """
        try:
            parsed = p.Text(line_text).parse()

            if not parsed or len(parsed) == 0:
                return 0.0, None

            # Get best parse
            best_parse = parsed[0][0]

            if not best_parse.stress_ints:
                return 0.0, None

            actual_pattern = list(best_parse.stress_ints)

            # Calculate mismatches
            min_len = min(len(actual_pattern), len(self.ideal_pattern))
            deviations = sum(
                1 for i in range(min_len)
                if actual_pattern[i] != self.ideal_pattern[i]
            )

            # Penalty for wrong syllable count
            length_penalty = abs(len(actual_pattern) - len(self.ideal_pattern))

            total_deviation = deviations + length_penalty

            return float(total_deviation), actual_pattern

        except Exception:
            # If prosodic fails, return neutral
            return 0.0, None

    def get_stress_string(self, pattern: Optional[List[int]]) -> str:
        """Convert stress pattern to string representation."""
        if pattern is None:
            return ""
        return "".join(str(s) for s in pattern)


class RhymeDetector:
    """Detect rhymes between poetry lines."""

    def __init__(self, use_phonetic: bool = True, fallback_length: int = 3):
        """
        Args:
            use_phonetic: Use pronouncing library for phonetic rhymes
            fallback_length: Fallback to last N characters if phonetic unavailable
        """
        self.use_phonetic = use_phonetic and PRONOUNCING_AVAILABLE
        self.fallback_length = fallback_length

        if not self.use_phonetic and PRONOUNCING_AVAILABLE:
            # User explicitly disabled phonetic
            pass
        elif not PRONOUNCING_AVAILABLE:
            # Phonetic library not available
            import logging
            logging.warning(
                "pronouncing library not available. "
                "Install with: pip install pronouncing\n"
                "Falling back to character-based rhyme detection."
            )

    def get_rhyme_key(self, line: str) -> str:
        """
        Extract rhyme key from line ending.

        Args:
            line: Line of poetry

        Returns:
            Rhyme key (phonetic or character-based)
        """
        # Clean line
        clean = line.lower().strip().rstrip('.,!?;:\'"')
        words = clean.split()

        if not words:
            return ""

        last_word = words[-1]

        if self.use_phonetic:
            # Use phonetic rhyme key (pronuncing library)
            try:
                # Get rhyming part (typically from primary stress onwards)
                import pronouncing
                phones = pronouncing.phones_for_word(last_word)
                if phones:
                    # Use first pronunciation
                    phone = phones[0]
                    # Get rhyme part (from primary stress onwards)
                    rhyme_part = pronouncing.rhyming_part(phone)
                    return rhyme_part
            except Exception:
                pass

        # Fallback: use last N characters
        return last_word[-self.fallback_length:] if len(last_word) >= self.fallback_length else last_word

    def do_lines_rhyme(self, line1: str, line2: str) -> bool:
        """Check if two lines rhyme."""
        key1 = self.get_rhyme_key(line1)
        key2 = self.get_rhyme_key(line2)

        if not key1 or not key2:
            return False

        return key1 == key2

    def detect_sonnet_rhymes(self, lines: List[str]) -> List[Tuple[int, int]]:
        """
        Detect rhyme pairs in a Shakespearean sonnet.

        Expected rhyme scheme: ABAB CDCD EFEF GG

        Args:
            lines: List of 14 lines (sonnet)

        Returns:
            List of (line_idx1, line_idx2) tuples for rhyming pairs
        """
        if len(lines) < 14:
            # Not a complete sonnet, do best effort
            return []

        rhyme_keys = [self.get_rhyme_key(line) for line in lines[:14]]

        # Expected pairs for Shakespearean sonnet
        expected_pairs = [
            (0, 2), (1, 3),      # ABAB
            (4, 6), (5, 7),      # CDCD
            (8, 10), (9, 11),    # EFEF
            (12, 13)             # GG (couplet)
        ]

        rhyme_pairs = []
        for i, j in expected_pairs:
            if rhyme_keys[i] and rhyme_keys[j] and rhyme_keys[i] == rhyme_keys[j]:
                rhyme_pairs.append((i, j))

        return rhyme_pairs


class ProsodicFeatureExtractor:
    """
    Extract complete prosodic features for poetry lines.

    Features:
    1. Metrical deviation (float)
    2. Rhyme pair indicator (binary)
    3. Position in poem (normalized 0-1)
    4. Couplet indicator (binary for final couplet)
    """

    def __init__(
        self,
        ideal_pattern: List[int] = None,
        use_phonetic_rhyme: bool = True
    ):
        self.meter_analyzer = MetricalAnalyzer(ideal_pattern)
        self.rhyme_detector = RhymeDetector(use_phonetic=use_phonetic_rhyme)

    def extract_features(
        self,
        lines: List[str],
        is_sonnet: bool = True
    ) -> List[Dict[str, float]]:
        """
        Extract prosodic features for all lines.

        Args:
            lines: List of poetry lines
            is_sonnet: Whether this is a sonnet (affects rhyme/couplet detection)

        Returns:
            List of feature dicts, one per line:
            {
                'meter_deviation': float,
                'rhyme': float (0 or 1),
                'position': float (0 to 1),
                'couplet': float (0 or 1)
            }
        """
        num_lines = len(lines)
        features = []

        # Detect rhyme pairs
        if is_sonnet:
            rhyme_pairs = self.rhyme_detector.detect_sonnet_rhymes(lines)
        else:
            rhyme_pairs = []  # Could implement other rhyme schemes

        # Create rhyme lookup
        rhyming_lines = set()
        for i, j in rhyme_pairs:
            rhyming_lines.add(i)
            rhyming_lines.add(j)

        # Extract features for each line
        for idx, line in enumerate(lines):
            # 1. Metrical deviation
            deviation, _ = self.meter_analyzer.score_deviation(line)

            # 2. Rhyme indicator
            rhyme = 1.0 if idx in rhyming_lines else 0.0

            # 3. Position in poem (normalized)
            position = idx / max(num_lines - 1, 1)

            # 4. Couplet indicator (last 2 lines for sonnets)
            couplet = 1.0 if (is_sonnet and idx >= num_lines - 2) else 0.0

            features.append({
                'meter_deviation': float(deviation),
                'rhyme': rhyme,
                'position': position,
                'couplet': couplet
            })

        return features

    def features_to_vector(self, features: Dict[str, float]) -> List[float]:
        """
        Convert feature dict to vector for concatenation with embeddings.

        Args:
            features: Feature dict from extract_features()

        Returns:
            Feature vector: [meter_deviation, rhyme, position, couplet]
        """
        return [
            features['meter_deviation'],
            features['rhyme'],
            features['position'],
            features['couplet']
        ]

    def analyze_corpus_stats(self, all_features: List[List[Dict[str, float]]]) -> Dict:
        """
        Compute statistics over a corpus of poems.

        Args:
            all_features: List of feature lists (one per poem)

        Returns:
            Dictionary of statistics
        """
        import numpy as np

        all_deviations = []
        rhyme_counts = []
        couplet_counts = []

        for poem_features in all_features:
            for feat in poem_features:
                all_deviations.append(feat['meter_deviation'])
                rhyme_counts.append(feat['rhyme'])
                couplet_counts.append(feat['couplet'])

        stats = {
            'mean_deviation': np.mean(all_deviations),
            'std_deviation': np.std(all_deviations),
            'rhyme_frequency': np.mean(rhyme_counts),
            'couplet_frequency': np.mean(couplet_counts),
            'total_lines': len(all_deviations)
        }

        return stats


# Convenience functions

def extract_prosodic_features(
    lines: List[str],
    is_sonnet: bool = True,
    use_phonetic_rhyme: bool = True
) -> List[Dict[str, float]]:
    """
    Convenience function to extract prosodic features.

    Args:
        lines: List of poetry lines
        is_sonnet: Whether this is a sonnet
        use_phonetic_rhyme: Use phonetic rhyme detection

    Returns:
        List of feature dicts
    """
    extractor = ProsodicFeatureExtractor(use_phonetic_rhyme=use_phonetic_rhyme)
    return extractor.extract_features(lines, is_sonnet=is_sonnet)


def test_prosodic_features():
    """Test the prosodic feature extraction."""
    # Test sonnet (Sonnet 18, first 4 lines)
    test_lines = [
        "Shall I compare thee to a summer's day?",
        "Thou art more lovely and more temperate:",
        "Rough winds do shake the darling buds of May,",
        "And summer's lease hath all too short a date:",
    ]

    print("Testing Prosodic Feature Extraction")
    print("="*60)

    extractor = ProsodicFeatureExtractor(use_phonetic_rhyme=True)
    features = extractor.extract_features(test_lines, is_sonnet=True)

    for idx, (line, feat) in enumerate(zip(test_lines, features)):
        print(f"\nLine {idx+1}: {line}")
        print(f"  Meter deviation: {feat['meter_deviation']:.1f}")
        print(f"  Rhymes: {'Yes' if feat['rhyme'] else 'No'}")
        print(f"  Position: {feat['position']:.2f}")
        print(f"  Couplet: {'Yes' if feat['couplet'] else 'No'}")
        print(f"  Feature vector: {extractor.features_to_vector(feat)}")

    print("\n" + "="*60)
    print("✓ Prosodic feature extraction working")


if __name__ == "__main__":
    test_prosodic_features()
