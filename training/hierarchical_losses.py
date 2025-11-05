"""
Hierarchical Loss Functions for Multi-Objective BERT Training

Implements:
1. MLM Loss (token level) - 0.5 weight
2. Line Contrastive Loss - 0.2 weight
3. Quatrain Contrastive Loss - 0.2 weight
4. Sonnet Contrastive Loss - 0.1 weight

Uses InfoNCE (NT-Xent) loss for contrastive components.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List


class HierarchicalLoss(nn.Module):
    """
    Combined multi-objective loss for hierarchical BERT training.

    Loss = 0.5 * MLM + 0.2 * Line + 0.2 * Quatrain + 0.1 * Sonnet
    """

    def __init__(
        self,
        temperature: float = 0.07,
        mlm_weight: float = 0.5,
        line_weight: float = 0.2,
        quatrain_weight: float = 0.2,
        sonnet_weight: float = 0.1
    ):
        """
        Args:
            temperature: Temperature for InfoNCE loss (default: 0.07)
            mlm_weight: Weight for MLM loss (default: 0.5)
            line_weight: Weight for line contrastive loss (default: 0.2)
            quatrain_weight: Weight for quatrain contrastive loss (default: 0.2)
            sonnet_weight: Weight for sonnet contrastive loss (default: 0.1)
        """
        super().__init__()

        self.temperature = temperature
        self.mlm_weight = mlm_weight
        self.line_weight = line_weight
        self.quatrain_weight = quatrain_weight
        self.sonnet_weight = sonnet_weight

        # Verify weights sum to 1.0
        total_weight = mlm_weight + line_weight + quatrain_weight + sonnet_weight
        assert abs(total_weight - 1.0) < 1e-6, f"Weights must sum to 1.0, got {total_weight}"

        # MLM loss (CrossEntropy with ignore_index=-100)
        self.mlm_loss_fn = nn.CrossEntropyLoss(ignore_index=-100)

    def forward(
        self,
        mlm_logits: torch.Tensor,
        mlm_labels: torch.Tensor,
        line_embeddings: Dict,
        quatrain_embeddings: Dict,
        sonnet_embeddings: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        """
        Compute combined hierarchical loss.

        Args:
            mlm_logits: Logits from MLM head (batch_size, seq_len, vocab_size)
            mlm_labels: MLM labels (batch_size, seq_len)
            line_embeddings: Dict with 'positive_pairs' and 'negative_pairs'
            quatrain_embeddings: Dict with 'positive_pairs' and 'negative_pairs'
            sonnet_embeddings: Sonnet-level embeddings (batch_size, hidden_dim)

        Returns:
            Dictionary with:
            - 'total_loss': Combined weighted loss
            - 'mlm_loss': MLM component
            - 'line_loss': Line contrastive component
            - 'quatrain_loss': Quatrain contrastive component
            - 'sonnet_loss': Sonnet contrastive component
        """
        # 1. MLM Loss
        mlm_loss = self._compute_mlm_loss(mlm_logits, mlm_labels)

        # 2. Line Contrastive Loss
        line_loss = self._compute_contrastive_loss(
            line_embeddings['positive_pairs'],
            line_embeddings['negative_pairs']
        )

        # 3. Quatrain Contrastive Loss
        quatrain_loss = self._compute_contrastive_loss(
            quatrain_embeddings['positive_pairs'],
            quatrain_embeddings['negative_pairs']
        )

        # 4. Sonnet Contrastive Loss
        sonnet_loss = self._compute_sonnet_contrastive_loss(sonnet_embeddings)

        # Combined loss
        total_loss = (
            self.mlm_weight * mlm_loss +
            self.line_weight * line_loss +
            self.quatrain_weight * quatrain_loss +
            self.sonnet_weight * sonnet_loss
        )

        return {
            'total_loss': total_loss,
            'mlm_loss': mlm_loss.detach(),
            'line_loss': line_loss.detach(),
            'quatrain_loss': quatrain_loss.detach(),
            'sonnet_loss': sonnet_loss.detach()
        }

    def _compute_mlm_loss(
        self,
        logits: torch.Tensor,
        labels: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute masked language modeling loss.

        Args:
            logits: (batch_size, seq_len, vocab_size)
            labels: (batch_size, seq_len) with -100 for unmasked tokens

        Returns:
            scalar loss
        """
        # Reshape for CrossEntropyLoss
        loss = self.mlm_loss_fn(
            logits.view(-1, logits.size(-1)),
            labels.view(-1)
        )
        return loss

    def _compute_contrastive_loss(
        self,
        positive_pairs: List[torch.Tensor],
        negative_pairs: List[torch.Tensor]
    ) -> torch.Tensor:
        """
        Compute InfoNCE contrastive loss.

        For each anchor:
        - Positive: similar embedding (adjacent/rhyming line, same quatrain)
        - Negatives: dissimilar embeddings (random lines, different quatrains)

        Args:
            positive_pairs: List of (anchor, positive) embedding pairs
            negative_pairs: List of (anchor, negative) embedding pairs

        Returns:
            scalar loss
        """
        if len(positive_pairs) == 0:
            # Return 0 loss on same device as model parameters
            return torch.tensor(0.0, requires_grad=True)

        if len(negative_pairs) == 0:
            # Can't compute contrastive loss without negatives
            return torch.tensor(0.0, requires_grad=True)

        losses = []

        # Use all negative samples for each positive pair
        # (standard InfoNCE: one anchor+positive vs many negatives)
        all_negatives = [neg for _, neg in negative_pairs]

        for anchor, positive in positive_pairs:
            # Normalize embeddings
            anchor_norm = F.normalize(anchor, dim=-1)
            positive_norm = F.normalize(positive, dim=-1)

            # Positive similarity
            pos_sim = torch.sum(anchor_norm * positive_norm, dim=-1) / self.temperature

            # Negative similarities (use ALL negatives, not just matched anchors)
            neg_sims = []
            for negative in all_negatives:
                negative_norm = F.normalize(negative, dim=-1)
                neg_sim = torch.sum(anchor_norm * negative_norm, dim=-1) / self.temperature
                neg_sims.append(neg_sim)

            # InfoNCE loss: -log(exp(pos) / (exp(pos) + sum(exp(neg))))
            neg_sims_tensor = torch.stack(neg_sims)
            logits = torch.cat([pos_sim.unsqueeze(0), neg_sims_tensor], dim=0)
            loss = -F.log_softmax(logits, dim=0)[0]
            losses.append(loss)

        if len(losses) == 0:
            return torch.tensor(0.0, requires_grad=True)

        return torch.mean(torch.stack(losses))

    def _compute_sonnet_contrastive_loss(
        self,
        sonnet_embeddings: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute sonnet-level contrastive loss.

        Within a batch, treat each sonnet as positive to itself
        and negative to all other sonnets.

        Args:
            sonnet_embeddings: (batch_size, hidden_dim)

        Returns:
            scalar loss
        """
        batch_size = sonnet_embeddings.size(0)

        if batch_size < 2:
            return torch.tensor(0.0, device=sonnet_embeddings.device)

        # Normalize embeddings
        sonnet_norm = F.normalize(sonnet_embeddings, dim=-1)

        # Compute similarity matrix (batch_size x batch_size)
        sim_matrix = torch.matmul(sonnet_norm, sonnet_norm.T) / self.temperature

        # Create labels: diagonal elements are positive
        labels = torch.arange(batch_size, device=sonnet_embeddings.device)

        # InfoNCE loss (treat each row as a classification problem)
        loss = F.cross_entropy(sim_matrix, labels)

        return loss


class InfoNCELoss(nn.Module):
    """
    InfoNCE (Normalized Temperature-scaled Cross Entropy) Loss.

    Used for contrastive learning at line and quatrain levels.
    """

    def __init__(self, temperature: float = 0.07):
        """
        Args:
            temperature: Temperature for scaling (default: 0.07)
        """
        super().__init__()
        self.temperature = temperature

    def forward(
        self,
        anchor: torch.Tensor,
        positive: torch.Tensor,
        negatives: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute InfoNCE loss.

        Args:
            anchor: Anchor embedding (hidden_dim,)
            positive: Positive embedding (hidden_dim,)
            negatives: Negative embeddings (num_negatives, hidden_dim)

        Returns:
            scalar loss
        """
        # Normalize
        anchor = F.normalize(anchor, dim=-1)
        positive = F.normalize(positive, dim=-1)
        negatives = F.normalize(negatives, dim=-1)

        # Compute similarities
        pos_sim = torch.sum(anchor * positive, dim=-1) / self.temperature
        neg_sims = torch.matmul(negatives, anchor) / self.temperature

        # Combine into logits: [positive, negative1, negative2, ...]
        logits = torch.cat([pos_sim.unsqueeze(0), neg_sims], dim=0)

        # Loss: -log(softmax(logits)[0])
        loss = -F.log_softmax(logits, dim=0)[0]

        return loss


def compute_batch_contrastive_loss(
    embeddings_anchor: torch.Tensor,
    embeddings_positive: torch.Tensor,
    embeddings_negative: torch.Tensor,
    temperature: float = 0.07
) -> torch.Tensor:
    """
    Compute contrastive loss for a batch of embeddings.

    Args:
        embeddings_anchor: (batch_size, hidden_dim)
        embeddings_positive: (batch_size, hidden_dim)
        embeddings_negative: (batch_size, num_negatives, hidden_dim)
        temperature: Temperature scaling

    Returns:
        mean loss across batch
    """
    batch_size = embeddings_anchor.size(0)

    # Normalize all embeddings
    anchor_norm = F.normalize(embeddings_anchor, dim=-1)
    positive_norm = F.normalize(embeddings_positive, dim=-1)
    negative_norm = F.normalize(embeddings_negative, dim=-1)

    # Positive similarities (batch_size,)
    pos_sims = torch.sum(anchor_norm * positive_norm, dim=-1) / temperature

    # Negative similarities (batch_size, num_negatives)
    neg_sims = torch.bmm(
        negative_norm,
        anchor_norm.unsqueeze(-1)
    ).squeeze(-1) / temperature

    # Combine: (batch_size, 1 + num_negatives)
    logits = torch.cat([pos_sims.unsqueeze(1), neg_sims], dim=1)

    # Labels: first position (index 0) is positive
    labels = torch.zeros(batch_size, dtype=torch.long, device=logits.device)

    # Cross-entropy loss
    loss = F.cross_entropy(logits, labels)

    return loss
