from typing import Dict, List, Optional

from .enums import SummaryStrategy, ModelType
from .base import BaseSummarizer
from .extractive import ExtractiveSummarizer
from .abstractive import AbstractiveSummarizer


class SummaryService:
    """
    Service for generating multi-level summaries with configurable strategies.

    Supports four summarization workflows:
    1. Abstractive topic summaries → Final abstractive summary
    2. Extractive topic summaries → Final abstractive summary
    3. Extractive topic summaries → Final extractive summary
    4. Direct extractive summary (no topic-level summaries)
    """

    def __init__(
        self,
        strategy: SummaryStrategy = SummaryStrategy.EXTRACTIVE_TO_ABSTRACTIVE,
        lite_model: ModelType = ModelType.LITE_FLAN_T5_SMALL,
        final_model: ModelType = ModelType.FINAL_FLAN_T5_BASE,
        topic_summary_length: int = 3,
        final_summary_length: int = 5,
    ):
        """
        Initialize the summary service.

        Args:
            strategy: Overall summarization workflow strategy
            lite_model: Model for topic-level summaries
            final_model: Model for final summary
            topic_summary_length: Max sentences/length for topic summaries
            final_summary_length: Max sentences/length for final summary
        """
        self.strategy = strategy
        self.lite_model = lite_model
        self.final_model = final_model
        self.topic_summary_length = topic_summary_length
        self.final_summary_length = final_summary_length

        # Lazy-loaded summarizers
        self._lite_summarizer: Optional[BaseSummarizer] = None
        self._final_summarizer: Optional[BaseSummarizer] = None

    @property
    def lite_summarizer(self) -> BaseSummarizer:
        """Lazy-load the topic-level summarizer."""
        if self._lite_summarizer is None:
            if self._uses_extractive_topic_summaries():
                self._lite_summarizer = ExtractiveSummarizer(
                    num_sentences=self.topic_summary_length
                )
            else:
                self._lite_summarizer = AbstractiveSummarizer(
                    model_name=self.lite_model.value
                )
        return self._lite_summarizer

    @property
    def final_summarizer(self) -> BaseSummarizer:
        """Lazy-load the final summarizer."""
        if self._final_summarizer is None:
            if self._uses_extractive_final_summary():
                self._final_summarizer = ExtractiveSummarizer(
                    num_sentences=self.final_summary_length
                )
            else:
                self._final_summarizer = AbstractiveSummarizer(
                    model_name=self.final_model.value
                )
        return self._final_summarizer

    def _uses_extractive_topic_summaries(self) -> bool:
        """Check if strategy uses extractive summaries for topics."""
        return self.strategy in {
            SummaryStrategy.EXTRACTIVE_TO_ABSTRACTIVE,
            SummaryStrategy.EXTRACTIVE_TO_EXTRACTIVE,
        }

    def _uses_extractive_final_summary(self) -> bool:
        """Check if strategy uses extractive summary for final output."""
        return self.strategy in {
            SummaryStrategy.EXTRACTIVE_TO_EXTRACTIVE,
            SummaryStrategy.EXTRACTIVE_ONLY,
        }

    def generate_topic_summaries(
        self, topic_chunks: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """
        Generate summaries for each topic from its chunks.

        Args:
            topic_chunks: Dictionary mapping topic names to lists of text chunks
                         Chunks should already be pre-processed by ChunkingService

        Returns:
            Dictionary mapping topic names to their summaries
        """
        topic_summaries = {}

        for topic, chunks in topic_chunks.items():
            # Generate summary for this topic using the configured summarizer
            summary = self.lite_summarizer.summarize(
                chunks, max_length=self.topic_summary_length
            )

            topic_summaries[topic] = summary

        return topic_summaries

    def generate_final_summary(self, topic_summaries: Dict[str, str]) -> str:
        """
        Generate final summary from topic summaries.

        Args:
            topic_summaries: Dictionary mapping topic names to their summaries

        Returns:
            Final combined summary
        """
        # Convert topic summaries into list of chunks for final summarizer
        if self._uses_extractive_final_summary():
            # For extractive: Simple "Topic: summary" format is fine
            topic_chunks = [
                f"{topic}: {summary}" for topic, summary in topic_summaries.items()
            ]
        else:
            # For abstractive: Better formatting for natural language processing
            # Create a more natural text format that models can understand better
            topic_chunks = [summary for summary in topic_summaries.values()]

        # Generate final summary using the configured summarizer
        final_summary = self.final_summarizer.summarize(
            topic_chunks, max_length=self.final_summary_length
        )

        return final_summary

    def summarize(self, topic_chunks: Dict[str, List[str]]) -> Dict[str, any]:
        """
        Complete summarization pipeline: topic summaries → final summary.

        Args:
            topic_chunks: Dictionary mapping topic names to lists of text chunks

        Returns:
            Dictionary containing topic summaries and final summary
        """
        # For EXTRACTIVE_ONLY, skip topic-level summaries and go direct
        if self.strategy == SummaryStrategy.EXTRACTIVE_ONLY:
            # Flatten all chunks into single list
            all_chunks = []
            for chunks in topic_chunks.values():
                all_chunks.extend(chunks)

            final_summary = self.summarize_direct(all_chunks)
            return {
                "topic_summaries": {},
                "final_summary": final_summary,
                "strategy": self.strategy.value,
            }

        # Generate topic-level summaries
        topic_summaries = self.generate_topic_summaries(topic_chunks)

        # Generate final summary
        final_summary = self.generate_final_summary(topic_summaries)

        return {
            "topic_summaries": topic_summaries,
            "final_summary": final_summary,
            "strategy": self.strategy.value,
        }

    def summarize_direct(self, chunks: List[str]) -> str:
        """
        Direct summarization without topic-level summaries.
        Useful for single documents or when topics aren't needed.

        Args:
            chunks: List of text chunks from ChunkingService

        Returns:
            Summary text
        """
        return self.final_summarizer.summarize(
            chunks, max_length=self.final_summary_length
        )
