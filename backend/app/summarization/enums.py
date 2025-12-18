"""
Enumerations for summarization strategies and model types.
"""

import enum


class SummaryType(enum.Enum):
    """Types of summary generation strategies."""

    EXTRACTIVE = "extractive"
    ABSTRACTIVE = "abstractive"


class SummaryStrategy(enum.Enum):
    """Overall summarization workflow strategies."""

    ABSTRACTIVE_TO_ABSTRACTIVE = "abstractive_topic_to_abstractive_final"
    EXTRACTIVE_TO_ABSTRACTIVE = "extractive_topic_to_abstractive_final"
    EXTRACTIVE_TO_EXTRACTIVE = "extractive_topic_to_extractive_final"
    EXTRACTIVE_ONLY = "extractive_direct"


class ModelType(enum.Enum):
    """
    Preset models for summarization.

    Model sizes (full precision):
    - t5-small: ~240MB (fastest, good for quick summaries)
    - distilbart-cnn: ~1.2GB (good balance of speed and quality)
    - flan-t5-small: ~310MB (better than t5-small, instruction-tuned)
    - t5-base: ~850MB (better quality than t5-small)
    - bart-large-cnn: ~1.6GB (best quality, slower)

    Quantized models (8-bit, ~50% memory reduction):
    - Use any model with load_in_8bit=True for quantization
    - Recommended for MacBook with 16GB RAM

    For Mac M4 (Apple Silicon):
    - MPS acceleration automatically enabled
    - Smaller models (t5-small, flan-t5-small, distilbart) run well
    - Larger models benefit from quantization
    """

    # Lightweight models for topic summaries (faster, smaller, Mac-friendly)
    LITE_FLAN_T5_SMALL = "google/flan-t5-small"
    LITE_T5_BASE = "google/flan-t5-base"
    LITE_DISTILBART = "sshleifer/distilbart-cnn-12-6"

    # Powerful models for final summaries (better quality)
    FINAL_BART = "facebook/bart-large-cnn"
    FINAL_FLAN_T5_BASE = "google/flan-t5-base"
    FINAL_FLAN_T5_LARGE = "google/flan-t5-large"
    FINAL_PEGASUS = "google/pegasus-xsum"
