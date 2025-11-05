"""
Custom HuggingFace Trainer for Hierarchical Multi-Objective BERT Training

Extends Trainer to:
1. Compute embeddings at multiple hierarchical levels
2. Apply multi-objective loss (MLM + contrastive at line/quatrain/sonnet levels)
3. Track loss components separately
4. Save best model based on validation loss
"""

import torch
import torch.nn as nn
from transformers import Trainer, BertModel, BertForMaskedLM
from typing import Dict, Optional, Tuple
from .hierarchical_losses import HierarchicalLoss


class HierarchicalBertModel(nn.Module):
    """
    BERT model with hierarchical output heads.

    Provides:
    - MLM logits (for token-level loss)
    - Line embeddings (mean pooling of line tokens)
    - Quatrain embeddings (mean pooling of quatrain lines)
    - Sonnet embeddings (mean pooling of all lines)
    """

    def __init__(self, base_model_path: str):
        """
        Args:
            base_model_path: Path to base BERT model (e.g., EEBO-BERT)
        """
        super().__init__()

        # Load BERT with MLM head
        self.bert_mlm = BertForMaskedLM.from_pretrained(base_model_path)
        self.bert = self.bert_mlm.bert

        # Projection heads for contrastive learning (optional)
        hidden_size = self.bert.config.hidden_size
        self.line_proj = nn.Linear(hidden_size, hidden_size)
        self.quatrain_proj = nn.Linear(hidden_size, hidden_size)
        self.sonnet_proj = nn.Linear(hidden_size, hidden_size)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        line_pairs_positive: list = None,
        line_pairs_negative: list = None,
        quatrain_pairs_positive: list = None,
        quatrain_pairs_negative: list = None,
        **kwargs
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass with hierarchical outputs.

        Args:
            input_ids: (batch_size, seq_len)
            attention_mask: (batch_size, seq_len)
            line_pairs_positive: List of positive line pairs
            line_pairs_negative: List of negative line pairs
            quatrain_pairs_positive: List of positive quatrain pairs
            quatrain_pairs_negative: List of negative quatrain pairs

        Returns:
            Dictionary with:
            - mlm_logits: (batch_size, seq_len, vocab_size)
            - line_embeddings: Dict with positive/negative pairs
            - quatrain_embeddings: Dict with positive/negative pairs
            - sonnet_embeddings: (batch_size, hidden_size)
        """
        # Get MLM logits
        mlm_outputs = self.bert_mlm(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        mlm_logits = mlm_outputs.logits

        # Get base BERT outputs for contrastive learning
        bert_outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        sequence_output = bert_outputs.last_hidden_state  # (batch_size, seq_len, hidden_size)

        # Sonnet-level embedding: mean pool over sequence
        sonnet_embeddings = self._mean_pool(sequence_output, attention_mask)
        sonnet_embeddings = self.sonnet_proj(sonnet_embeddings)

        # Process line pairs for contrastive learning
        line_embeddings = self._process_line_pairs(
            line_pairs_positive,
            line_pairs_negative
        )

        # Process quatrain pairs
        quatrain_embeddings = self._process_quatrain_pairs(
            quatrain_pairs_positive,
            quatrain_pairs_negative
        )

        return {
            'mlm_logits': mlm_logits,
            'line_embeddings': line_embeddings,
            'quatrain_embeddings': quatrain_embeddings,
            'sonnet_embeddings': sonnet_embeddings
        }

    def _mean_pool(
        self,
        token_embeddings: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Mean pooling over sequence, accounting for padding.

        Args:
            token_embeddings: (batch_size, seq_len, hidden_size)
            attention_mask: (batch_size, seq_len)

        Returns:
            pooled: (batch_size, hidden_size)
        """
        # Expand mask to match embeddings
        mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()

        # Sum embeddings (masked)
        sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)

        # Count non-padding tokens
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)

        # Mean
        return sum_embeddings / sum_mask

    def _process_line_pairs(
        self,
        positive_pairs: list,
        negative_pairs: list
    ) -> Dict:
        """
        Process line pairs to extract embeddings.

        Args:
            positive_pairs: List of dicts with 'anchor' and 'positive' encodings
            negative_pairs: List of dicts with 'anchor' and 'negative' encodings

        Returns:
            Dict with 'positive_pairs' and 'negative_pairs' as lists of tensors
        """
        if not positive_pairs or len(positive_pairs) == 0:
            return {'positive_pairs': [], 'negative_pairs': []}

        pos_pair_embeddings = []
        for batch_pairs in positive_pairs:
            for pair in batch_pairs:
                # Get embeddings for anchor and positive
                anchor_emb = self._encode_line(
                    pair['anchor']['input_ids'],
                    pair['anchor']['attention_mask']
                )
                positive_emb = self._encode_line(
                    pair['positive']['input_ids'],
                    pair['positive']['attention_mask']
                )

                # Project
                anchor_emb = self.line_proj(anchor_emb)
                positive_emb = self.line_proj(positive_emb)

                pos_pair_embeddings.append((anchor_emb, positive_emb))

        neg_pair_embeddings = []
        for batch_pairs in negative_pairs:
            for pair in batch_pairs:
                anchor_emb = self._encode_line(
                    pair['anchor']['input_ids'],
                    pair['anchor']['attention_mask']
                )
                negative_emb = self._encode_line(
                    pair['negative']['input_ids'],
                    pair['negative']['attention_mask']
                )

                # Project
                anchor_emb = self.line_proj(anchor_emb)
                negative_emb = self.line_proj(negative_emb)

                neg_pair_embeddings.append((anchor_emb, negative_emb))

        return {
            'positive_pairs': pos_pair_embeddings,
            'negative_pairs': neg_pair_embeddings
        }

    def _process_quatrain_pairs(
        self,
        positive_pairs: list,
        negative_pairs: list
    ) -> Dict:
        """
        Process quatrain pairs to extract embeddings.
        """
        if not positive_pairs or len(positive_pairs) == 0:
            return {'positive_pairs': [], 'negative_pairs': []}

        pos_pair_embeddings = []
        for batch_pairs in positive_pairs:
            for pair in batch_pairs:
                anchor_emb = self._encode_line(
                    pair['anchor']['input_ids'],
                    pair['anchor']['attention_mask']
                )
                positive_emb = self._encode_line(
                    pair['positive']['input_ids'],
                    pair['positive']['attention_mask']
                )

                # Project
                anchor_emb = self.quatrain_proj(anchor_emb)
                positive_emb = self.quatrain_proj(positive_emb)

                pos_pair_embeddings.append((anchor_emb, positive_emb))

        neg_pair_embeddings = []
        for batch_pairs in negative_pairs:
            for pair in batch_pairs:
                anchor_emb = self._encode_line(
                    pair['anchor']['input_ids'],
                    pair['anchor']['attention_mask']
                )
                negative_emb = self._encode_line(
                    pair['negative']['input_ids'],
                    pair['negative']['attention_mask']
                )

                # Project
                anchor_emb = self.quatrain_proj(anchor_emb)
                negative_emb = self.quatrain_proj(negative_emb)

                neg_pair_embeddings.append((anchor_emb, negative_emb))

        return {
            'positive_pairs': pos_pair_embeddings,
            'negative_pairs': neg_pair_embeddings
        }

    def _encode_line(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Encode a single line.

        Args:
            input_ids: (seq_len,) or (1, seq_len)
            attention_mask: (seq_len,) or (1, seq_len)

        Returns:
            embedding: (hidden_size,)
        """
        # Add batch dimension if needed
        if input_ids.dim() == 1:
            input_ids = input_ids.unsqueeze(0)
            attention_mask = attention_mask.unsqueeze(0)

        # Ensure on same device as model
        device = next(self.parameters()).device
        input_ids = input_ids.to(device)
        attention_mask = attention_mask.to(device)

        # Encode
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        # Mean pool
        embedding = self._mean_pool(outputs.last_hidden_state, attention_mask)

        return embedding.squeeze(0)  # Remove batch dimension


class HierarchicalTrainer(Trainer):
    """
    Custom Trainer for hierarchical multi-objective BERT training.
    """

    def __init__(self, *args, loss_fn: Optional[HierarchicalLoss] = None, **kwargs):
        """
        Args:
            loss_fn: Hierarchical loss function
            *args, **kwargs: Arguments for base Trainer
        """
        super().__init__(*args, **kwargs)

        self.loss_fn = loss_fn if loss_fn else HierarchicalLoss()

        # Track loss components
        self.loss_history = {
            'total': [],
            'mlm': [],
            'line': [],
            'quatrain': [],
            'sonnet': []
        }

    def compute_loss(
        self,
        model: HierarchicalBertModel,
        inputs: Dict,
        return_outputs: bool = False,
        num_items_in_batch: int = None
    ) -> torch.Tensor:
        """
        Compute hierarchical loss.

        Args:
            model: HierarchicalBertModel
            inputs: Batch dictionary from dataset
            return_outputs: Whether to return model outputs
            num_items_in_batch: Number of items in batch (for compatibility with newer transformers)

        Returns:
            loss (and optionally outputs)
        """
        # Forward pass
        outputs = model(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            line_pairs_positive=inputs.get('line_pairs_positive'),
            line_pairs_negative=inputs.get('line_pairs_negative'),
            quatrain_pairs_positive=inputs.get('quatrain_pairs_positive'),
            quatrain_pairs_negative=inputs.get('quatrain_pairs_negative')
        )

        # Compute hierarchical loss
        loss_dict = self.loss_fn(
            mlm_logits=outputs['mlm_logits'],
            mlm_labels=inputs['mlm_labels'],
            line_embeddings=outputs['line_embeddings'],
            quatrain_embeddings=outputs['quatrain_embeddings'],
            sonnet_embeddings=outputs['sonnet_embeddings']
        )

        # Track loss components
        if self.state.global_step % 10 == 0:  # Log every 10 steps
            self.loss_history['total'].append(loss_dict['total_loss'].item())
            self.loss_history['mlm'].append(loss_dict['mlm_loss'].item())
            self.loss_history['line'].append(loss_dict['line_loss'].item())
            self.loss_history['quatrain'].append(loss_dict['quatrain_loss'].item())
            self.loss_history['sonnet'].append(loss_dict['sonnet_loss'].item())

        loss = loss_dict['total_loss']

        return (loss, outputs) if return_outputs else loss

    def log(self, logs: Dict[str, float]) -> None:
        """
        Override log to include loss components.
        """
        # Add loss components to logs if available
        if self.loss_history['total']:
            logs['loss_mlm'] = self.loss_history['mlm'][-1]
            logs['loss_line'] = self.loss_history['line'][-1]
            logs['loss_quatrain'] = self.loss_history['quatrain'][-1]
            logs['loss_sonnet'] = self.loss_history['sonnet'][-1]

        super().log(logs)
