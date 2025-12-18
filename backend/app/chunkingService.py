import enum
from typing import List
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    SpacyTextSplitter,
)
from transformers import GPT2TokenizerFast


class ChunkingStrategy(enum.Enum):
    FIXED_LENGTH = "fixed_length"
    MARKDOWN_SEGMENTS = "markdown_segments"
    SENTENCE_CHUNKING = "sentence_chunking"


class ChunkingService:
    def __init__(self, chunk_size: int = 100, chunk_overlap: int = 20):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Lazy-loaded resources (only initialized when needed)
        self._tokenizer = None
        self._text_splitter = None
        self._markdown_splitter = None
        self._sentence_splitter = None

        # Map strategies to their methods
        self._strategy_map = {
            ChunkingStrategy.FIXED_LENGTH: self._fixed_length_chunking,
            ChunkingStrategy.MARKDOWN_SEGMENTS: self._markdown_chunking,
            ChunkingStrategy.SENTENCE_CHUNKING: self._sentence_chunking,
        }

    @property
    def tokenizer(self):
        """Lazy-load tokenizer only when needed."""
        if self._tokenizer is None:
            self._tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        return self._tokenizer

    @property
    def text_splitter(self):
        """Lazy-load text splitter only when needed."""
        if self._text_splitter is None:
            self._text_splitter = (
                RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
                    self.tokenizer,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
            )
        return self._text_splitter

    @property
    def markdown_splitter(self):
        """Lazy-load markdown splitter only when needed."""
        if self._markdown_splitter is None:
            self._markdown_splitter = MarkdownTextSplitter()
        return self._markdown_splitter

    @property
    def sentence_splitter(self):
        if self._sentence_splitter is None:
            self._sentence_splitter = SpacyTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )

        return self._sentence_splitter

    # main function
    def chunk_document(
        self, strategy_type: ChunkingStrategy, document_content: str
    ) -> List[str]:
        """
        Chunks document content based on the specified strategy.

        Args:
            strategy_type: The chunking strategy to use
            document_content: The text content to chunk

        Returns:
            List of text chunks

        Raises:
            ValueError: If the strategy is not supported
        """
        strategy_method = self._strategy_map.get(strategy_type)

        if strategy_method is None:
            raise ValueError(f"Unsupported chunking strategy: {strategy_type}")

        return strategy_method(document_content)

    def _fixed_length_chunking(self, document_content: str) -> List[str]:
        """
        Chunks document using fixed-length strategy with token-based splitting.

        Args:
            document_content: The text content to chunk

        Returns:
            List of text chunks
        """
        return self.text_splitter.split_text(document_content)

    def _markdown_chunking(self, document_content: str) -> List[str]:
        return self.markdown_splitter.split_text(document_content)

    def _sentence_chunking(self, document_content: str) -> List[str]:
        return self.sentence_splitter.split_text(document_content)

    # Add more strategy methods here as needed
    # def _semantic_chunking(self, document_content: str) -> List[str]:
    #     pass

    # def _sliding_window_chunking(self, document_content: str) -> List[str]:
    #     pass
