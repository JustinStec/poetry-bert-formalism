#!/usr/bin/env python3
"""
Configuration Management for Poetry BERT Formalism Project

This module centralizes all configuration, including:
- File paths (models, data, results)
- Training hyperparameters
- Device settings (CPU, CUDA, MPS)

Supports environment variables via .env file for user-specific paths.

Usage:
    from config import config
    model_path = config.paths.eebo_bert
    batch_size = config.training.batch_size
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import torch

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, that's okay


@dataclass
class Paths:
    """File and directory paths."""

    # Project root
    project_root: Path = Path(__file__).parent

    # Data directories
    data_dir: Path = project_root / "data"
    corpus_samples_dir: Path = project_root / "corpus_samples"
    results_dir: Path = project_root / "results"
    models_dir: Path = project_root / "models"

    # Model paths (can be overridden by environment variables)
    eebo_bert: Optional[Path] = None
    poetry_bert: Optional[Path] = None
    poetry_eebo_bert: Optional[Path] = None
    base_bert: str = "bert-base-uncased"

    # Data files
    shakespeare_sonnets: Path = corpus_samples_dir / "shakespeare_sonnets_parsed.jsonl"
    poetry_database: Path = data_dir / "poetry_unified.db"
    eebo_corpus: Path = data_dir / "eebo_cleaned_corpus.txt"

    # Google Drive paths (if available)
    google_drive_root: Optional[Path] = None

    def __post_init__(self):
        """Initialize paths from environment variables or defaults."""

        # Try to load from environment variables first
        if os.getenv("EEBO_BERT_PATH"):
            self.eebo_bert = Path(os.getenv("EEBO_BERT_PATH"))
        elif self.models_dir.exists():
            # Check local models directory
            local_eebo = self.models_dir / "eebo_bert"
            if local_eebo.exists():
                self.eebo_bert = local_eebo

        if os.getenv("POETRY_BERT_PATH"):
            self.poetry_bert = Path(os.getenv("POETRY_BERT_PATH"))
        elif self.models_dir.exists():
            local_poetry = self.models_dir / "poetry_bert"
            if local_poetry.exists():
                self.poetry_bert = local_poetry

        if os.getenv("POETRY_EEBO_BERT_PATH"):
            self.poetry_eebo_bert = Path(os.getenv("POETRY_EEBO_BERT_PATH"))
        elif self.models_dir.exists():
            local_poetry_eebo = self.models_dir / "poetry_eebo_bert"
            if local_poetry_eebo.exists():
                self.poetry_eebo_bert = local_poetry_eebo

        # Google Drive root (if mounted or CloudStorage)
        if os.getenv("GOOGLE_DRIVE_ROOT"):
            self.google_drive_root = Path(os.getenv("GOOGLE_DRIVE_ROOT"))
        else:
            # Try common locations
            common_locations = [
                Path.home() / "Library" / "CloudStorage" / "GoogleDrive-stecj2700@gmail.com" / "My Drive",
                Path.home() / "Google Drive",
                Path("/content/drive/MyDrive"),  # Colab
            ]
            for location in common_locations:
                if location.exists():
                    self.google_drive_root = location
                    break

        # If Google Drive is available and models aren't set, try Drive paths
        if self.google_drive_root:
            ai_poetry_dir = self.google_drive_root / "AI and Poetry"

            if not self.eebo_bert and (ai_poetry_dir / "EEBO_1595-1700" / "eebo_bert_finetuned").exists():
                self.eebo_bert = ai_poetry_dir / "EEBO_1595-1700" / "eebo_bert_finetuned"

            if not self.poetry_bert and (ai_poetry_dir / "poetry_bert_trained").exists():
                self.poetry_bert = ai_poetry_dir / "poetry_bert_trained"

            if not self.poetry_eebo_bert and (ai_poetry_dir / "poetry_eebo_bert_trained").exists():
                self.poetry_eebo_bert = ai_poetry_dir / "poetry_eebo_bert_trained"

            # Check for data files in Drive
            if not self.poetry_database.exists():
                drive_db = ai_poetry_dir / "poetry_unified.db"
                if drive_db.exists():
                    self.poetry_database = drive_db

        # Create local directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str) -> Path:
        """
        Get path for a model by name.

        Args:
            model_name: 'base', 'eebo', 'poetry', or 'poetry_eebo'

        Returns:
            Path to model or model identifier string

        Raises:
            ValueError: If model path not configured
        """
        if model_name == "base":
            return self.base_bert
        elif model_name == "eebo":
            if not self.eebo_bert:
                raise ValueError(
                    "EEBO-BERT path not configured. "
                    "Set EEBO_BERT_PATH environment variable or place model in models/eebo_bert/"
                )
            return self.eebo_bert
        elif model_name == "poetry":
            if not self.poetry_bert:
                raise ValueError(
                    "Poetry-BERT path not configured. "
                    "Set POETRY_BERT_PATH environment variable or place model in models/poetry_bert/"
                )
            return self.poetry_bert
        elif model_name == "poetry_eebo":
            if not self.poetry_eebo_bert:
                raise ValueError(
                    "Poetry-EEBO-BERT path not configured. "
                    "Set POETRY_EEBO_BERT_PATH environment variable or place model in models/poetry_eebo_bert/"
                )
            return self.poetry_eebo_bert
        else:
            raise ValueError(f"Unknown model name: {model_name}")


@dataclass
class TrainingConfig:
    """Training hyperparameters."""

    # BERT training
    max_length: int = 512
    mlm_probability: float = 0.15

    # Optimizer
    learning_rate: float = 5e-5
    weight_decay: float = 0.01
    warmup_steps: int = 500

    # Training loop
    num_epochs: int = 3
    batch_size: int = 8
    gradient_accumulation_steps: int = 1

    # Checkpointing
    save_steps: int = 1000
    save_total_limit: int = 2
    logging_steps: int = 100

    # Validation
    eval_steps: int = 500
    eval_strategy: str = "steps"  # "no", "steps", or "epoch"
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"

    # Early stopping
    early_stopping_patience: int = 3
    early_stopping_threshold: float = 0.0

    # Mixed precision
    fp16: bool = False  # Set to True for CUDA
    bf16: bool = False  # Set to True for newer CUDA or TPU

    def adjust_for_device(self, device: str):
        """Adjust settings based on available device."""
        if device == "cuda":
            self.fp16 = True
            self.batch_size = 16  # Larger batch for GPU
        elif device == "mps":
            self.fp16 = False  # MPS doesn't support fp16 yet
            self.batch_size = 8
        else:  # CPU
            self.batch_size = 2  # Much smaller for CPU
            self.fp16 = False


@dataclass
class ProsodicConfig:
    """Prosodic analysis configuration."""

    # Rhyme detection
    use_phonetic_rhyme: bool = False  # Use phonetic dictionary (if available)
    rhyme_suffix_length: int = 3  # Fallback: last N characters

    # Meter analysis
    ideal_meter: str = "iambic_pentameter"
    ideal_pattern: list = None

    # Feature dimensions
    prosodic_feature_dims: int = 4  # meter_deviation, rhyme, position, couplet

    def __post_init__(self):
        if self.ideal_pattern is None:
            # Iambic pentameter: unstressed-stressed × 5
            self.ideal_pattern = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]


@dataclass
class DeviceConfig:
    """Device and hardware configuration."""

    device: str = "auto"
    num_workers: int = 4

    def __post_init__(self):
        """Detect best available device."""
        if self.device == "auto":
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"

        # Adjust workers based on CPU count
        import multiprocessing
        available_cpus = multiprocessing.cpu_count()
        self.num_workers = min(self.num_workers, available_cpus)

    def get_torch_device(self) -> torch.device:
        """Get PyTorch device object."""
        return torch.device(self.device)


@dataclass
class Config:
    """Main configuration object."""

    paths: Paths
    training: TrainingConfig
    prosodic: ProsodicConfig
    device: DeviceConfig

    def __init__(self):
        self.paths = Paths()
        self.device = DeviceConfig()
        self.training = TrainingConfig()
        self.prosodic = ProsodicConfig()

        # Adjust training config for device
        self.training.adjust_for_device(self.device.device)

    def summary(self) -> str:
        """Return a summary of the configuration."""
        lines = ["Configuration Summary", "=" * 60]

        lines.append("\nDevice:")
        lines.append(f"  Device: {self.device.device}")
        lines.append(f"  Workers: {self.device.num_workers}")

        lines.append("\nModel Paths:")
        lines.append(f"  EEBO-BERT: {self.paths.eebo_bert or 'NOT CONFIGURED'}")
        lines.append(f"  Poetry-BERT: {self.paths.poetry_bert or 'NOT CONFIGURED'}")
        lines.append(f"  Poetry-EEBO-BERT: {self.paths.poetry_eebo_bert or 'NOT CONFIGURED'}")

        lines.append("\nData Paths:")
        lines.append(f"  Poetry DB: {self.paths.poetry_database}")
        lines.append(f"  Sonnets: {self.paths.shakespeare_sonnets}")

        lines.append("\nTraining:")
        lines.append(f"  Batch size: {self.training.batch_size}")
        lines.append(f"  Learning rate: {self.training.learning_rate}")
        lines.append(f"  Epochs: {self.training.num_epochs}")
        lines.append(f"  FP16: {self.training.fp16}")

        lines.append("=" * 60)
        return "\n".join(lines)


# Global configuration instance
config = Config()


if __name__ == "__main__":
    # Print configuration when run directly
    print(config.summary())
