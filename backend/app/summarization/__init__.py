"""
Summarization package for local-RAG.

Provides extractive and abstractive summarization with multiple strategies.
"""

from .enums import SummaryType, SummaryStrategy, ModelType
from .base import BaseSummarizer
from .extractive import ExtractiveSummarizer
from .abstractive import AbstractiveSummarizer
from .service import SummaryService

__all__ = [
    "SummaryType",
    "SummaryStrategy",
    "ModelType",
    "BaseSummarizer",
    "ExtractiveSummarizer",
    "AbstractiveSummarizer",
    "SummaryService",
]
