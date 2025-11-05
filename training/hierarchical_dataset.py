"""
Hierarchical Poetry Dataset for Multi-Objective BERT Training

PyTorch Dataset that provides hierarchical structure for:
- Token level (MLM)
- Line level (contrastive)
- Quatrain level (contrastive)
- Sonnet level (contrastive)
"""

import json
import random
import torch
from torch.utils.data import Dataset
from typing import Dict, List, Tuple
from transformers import BertTokenizer


class HierarchicalPoetryDataset(Dataset):
    """
    Dataset for hierarchical multi-objective BERT training.

    Loads sonnets with hierarchical annotations and provides:
    1. Tokenized text with MLM masking
    2. Line pairs (positive: adjacent/rhyming, negative: random)
    3. Quatrain pairs (positive: same quatrain, negative: different)
    4. Sonnet-level embeddings
    """

    def __init__(
        self,
        data_path: str,
        tokenizer: BertTokenizer,
        max_length: int = 128,
        mlm_probability: float = 0.15,
        line_negative_samples: int = 2,
        quatrain_negative_samples: int = 1,
    ):
        """
        Args:
            data_path: Path to hierarchical JSONL file
            tokenizer: BERT tokenizer
            max_length: Max sequence length for tokenization
            mlm_probability: Probability of masking tokens for MLM
            line_negative_samples: Number of negative line pairs per positive
            quatrain_negative_samples: Number of negative quatrain pairs per positive
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.mlm_probability = mlm_probability
        self.line_negative_samples = line_negative_samples
        self.quatrain_negative_samples = quatrain_negative_samples

        # Load data
        self.sonnets = []
        with open(data_path, 'r') as f:
            for line in f:
                self.sonnets.append(json.loads(line))

        print(f"Loaded {len(self.sonnets)} sonnets from {data_path}")

    def __len__(self):
        return len(self.sonnets)

    def __getitem__(self, idx: int) -> Dict:
        """
        Get a single sonnet with all hierarchical annotations.

        Returns dictionary with:
        - input_ids: Tokenized sonnet (for MLM)
        - attention_mask: Attention mask
        - mlm_labels: Labels for MLM (-100 for unmasked tokens)
        - line_pairs_positive: List of (line_i, line_j) positive pairs
        - line_pairs_negative: List of (line_i, line_j) negative pairs
        - quatrain_pairs_positive: List of quatrain pairs
        - quatrain_pairs_negative: List of quatrain pairs
        - sonnet_id: Sonnet identifier
        """
        sonnet = self.sonnets[idx]

        # Get full sonnet text
        full_text = " [SEP] ".join(sonnet['lines'])

        # Tokenize
        encoding = self.tokenizer(
            full_text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)

        # Create MLM labels
        mlm_labels = self._create_mlm_labels(input_ids)

        # Tokenize individual lines for contrastive learning
        line_encodings = []
        for line in sonnet['lines']:
            line_enc = self.tokenizer(
                line,
                max_length=64,  # Lines are shorter
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            line_encodings.append({
                'input_ids': line_enc['input_ids'].squeeze(0),
                'attention_mask': line_enc['attention_mask'].squeeze(0)
            })

        # Create line pairs for contrastive learning
        line_pairs_pos, line_pairs_neg = self._create_line_pairs(sonnet, line_encodings)

        # Create quatrain pairs for contrastive learning
        quatrain_pairs_pos, quatrain_pairs_neg = self._create_quatrain_pairs(sonnet, line_encodings)

        return {
            # Token level (MLM)
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'mlm_labels': mlm_labels,

            # Line level (contrastive)
            'line_pairs_positive': line_pairs_pos,
            'line_pairs_negative': line_pairs_neg,

            # Quatrain level (contrastive)
            'quatrain_pairs_positive': quatrain_pairs_pos,
            'quatrain_pairs_negative': quatrain_pairs_neg,

            # Metadata
            'sonnet_id': sonnet.get('sonnet_id', idx),
            'num_lines': sonnet['num_lines']
        }

    def _create_mlm_labels(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Create MLM labels by masking tokens.

        Args:
            input_ids: Token IDs (shape: [seq_len])

        Returns:
            mlm_labels: Labels for MLM (shape: [seq_len])
                        -100 for unmasked tokens (ignored by loss)
        """
        labels = input_ids.clone()

        # Create probability mask
        probability_matrix = torch.full(labels.shape, self.mlm_probability)

        # Don't mask special tokens
        special_tokens_mask = self.tokenizer.get_special_tokens_mask(
            labels.tolist(), already_has_special_tokens=True
        )
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)

        # Create masked indices
        masked_indices = torch.bernoulli(probability_matrix).bool()

        # Set unmasked tokens to -100 (ignored by loss)
        labels[~masked_indices] = -100

        # 80% of time: replace with [MASK]
        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        input_ids[indices_replaced] = self.tokenizer.mask_token_id

        # 10% of time: replace with random token
        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        input_ids[indices_random] = random_words[indices_random]

        # 10% of time: keep original token (for contrastive learning)
        # (remaining masked_indices that aren't replaced or randomized)

        return labels

    def _create_line_pairs(
        self,
        sonnet: Dict,
        line_encodings: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Create positive and negative line pairs for contrastive learning.

        Positive pairs:
        - Adjacent lines (semantic continuity)
        - Rhyming lines (formal connection)

        Negative pairs:
        - Random lines from same sonnet (within-sonnet negatives)
        """
        positive_pairs = []
        negative_pairs = []

        # Positive pairs: adjacent lines
        for i, j in sonnet['adjacent_pairs']:
            if i < len(line_encodings) and j < len(line_encodings):
                positive_pairs.append({
                    'anchor': line_encodings[i],
                    'positive': line_encodings[j],
                    'type': 'adjacent'
                })

        # Positive pairs: rhyming lines
        for i, j in sonnet['rhyme_pairs']:
            if i < len(line_encodings) and j < len(line_encodings):
                positive_pairs.append({
                    'anchor': line_encodings[i],
                    'positive': line_encodings[j],
                    'type': 'rhyme'
                })

        # Negative pairs: random non-adjacent, non-rhyming lines
        num_lines = len(line_encodings)
        positive_indices = set()
        for i, j in sonnet['adjacent_pairs'] + sonnet['rhyme_pairs']:
            positive_indices.add((i, j))
            positive_indices.add((j, i))

        # Sample negative pairs
        for _ in range(len(positive_pairs) * self.line_negative_samples):
            # Random pair that's not positive
            attempts = 0
            while attempts < 10:
                i = random.randint(0, num_lines - 1)
                j = random.randint(0, num_lines - 1)
                if i != j and (i, j) not in positive_indices:
                    negative_pairs.append({
                        'anchor': line_encodings[i],
                        'negative': line_encodings[j],
                        'type': 'random'
                    })
                    break
                attempts += 1

        return positive_pairs, negative_pairs

    def _create_quatrain_pairs(
        self,
        sonnet: Dict,
        line_encodings: List[Dict]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Create positive and negative quatrain pairs.

        Positive pairs:
        - Lines from same quatrain (thematic unity)

        Negative pairs:
        - Lines from different quatrains
        """
        positive_pairs = []
        negative_pairs = []

        # Define quatrains
        quatrains = [
            sonnet['quatrain_1'],
            sonnet['quatrain_2'],
            sonnet['quatrain_3'],
            sonnet['couplet']
        ]

        # Positive pairs: lines within same quatrain
        for q_idx, quatrain in enumerate(quatrains):
            if len(quatrain) < 2:
                continue

            # Sample pairs within this quatrain
            for i in range(len(quatrain)):
                for j in range(i + 1, len(quatrain)):
                    line_i = quatrain[i]
                    line_j = quatrain[j]

                    if line_i < len(line_encodings) and line_j < len(line_encodings):
                        positive_pairs.append({
                            'anchor': line_encodings[line_i],
                            'positive': line_encodings[line_j],
                            'quatrain': q_idx
                        })

        # Negative pairs: lines from different quatrains
        for _ in range(len(positive_pairs) * self.quatrain_negative_samples):
            # Sample two different quatrains
            if len(quatrains) < 2:
                break

            q1, q2 = random.sample(range(len(quatrains)), 2)

            if len(quatrains[q1]) == 0 or len(quatrains[q2]) == 0:
                continue

            line_i = random.choice(quatrains[q1])
            line_j = random.choice(quatrains[q2])

            if line_i < len(line_encodings) and line_j < len(line_encodings):
                negative_pairs.append({
                    'anchor': line_encodings[line_i],
                    'negative': line_encodings[line_j],
                    'quatrains': (q1, q2)
                })

        return positive_pairs, negative_pairs


def collate_hierarchical(batch: List[Dict]) -> Dict:
    """
    Custom collate function for hierarchical batches.

    Handles variable-length line and quatrain pairs.
    """
    # Stack token-level data
    input_ids = torch.stack([item['input_ids'] for item in batch])
    attention_mask = torch.stack([item['attention_mask'] for item in batch])
    mlm_labels = torch.stack([item['mlm_labels'] for item in batch])

    # Collect line pairs (keep as list of lists for now)
    line_pairs_pos = [item['line_pairs_positive'] for item in batch]
    line_pairs_neg = [item['line_pairs_negative'] for item in batch]

    # Collect quatrain pairs
    quatrain_pairs_pos = [item['quatrain_pairs_positive'] for item in batch]
    quatrain_pairs_neg = [item['quatrain_pairs_negative'] for item in batch]

    # Metadata
    sonnet_ids = [item['sonnet_id'] for item in batch]

    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'mlm_labels': mlm_labels,
        'line_pairs_positive': line_pairs_pos,
        'line_pairs_negative': line_pairs_neg,
        'quatrain_pairs_positive': quatrain_pairs_pos,
        'quatrain_pairs_negative': quatrain_pairs_neg,
        'sonnet_ids': sonnet_ids
    }
