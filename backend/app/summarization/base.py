"""
Base abstract class for all summarizers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class BaseSummarizer(ABC):
    """Abstract base class for summarizers."""

    @abstractmethod
    def summarize(self, chunks: List[str], max_length: Optional[int] = None) -> str:
        """
        Generate summary from text chunks.

        Args:
            chunks: List of text chunks (pre-chunked by ChunkingService)
            max_length: Maximum length of summary (interpretation varies by strategy)

        Returns:
            Summary text as a single string
        """
        pass
