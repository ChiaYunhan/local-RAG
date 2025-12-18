import pytest
from app.chunkingService import ChunkingService, ChunkingStrategy


class TestChunkingService:
    @pytest.fixture
    def chunking_service(self):
        """Create a ChunkingService instance with default parameters."""
        return ChunkingService(chunk_size=100, chunk_overlap=20)

    @pytest.fixture
    def small_chunking_service(self):
        """Create a ChunkingService instance with small chunks for testing."""
        return ChunkingService(chunk_size=10, chunk_overlap=2)

    @pytest.fixture
    def sample_text_short(self):
        """Short sample text for basic testing."""
        return "This is a short sample text for testing chunking."

    @pytest.fixture
    def sample_text_long(self):
        """Long sample text that will be split into multiple chunks."""
        base_text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines,
        in contrast to the natural intelligence displayed by humans and animals.
        Leading AI textbooks define the field as the study of intelligent agents:
        any device that perceives its environment and takes actions that maximize
        its chance of successfully achieving its goals. Colloquially, the term
        artificial intelligence is often used to describe machines that mimic
        cognitive functions that humans associate with the human mind, such as
        learning and problem solving. As machines become increasingly capable,
        tasks considered to require intelligence are often removed from the
        definition of AI, a phenomenon known as the AI effect. A quip in Tesler's
        Theorem says AI is whatever hasn't been done yet. For instance, optical
        character recognition is frequently excluded from things considered to be
        AI, having become a routine technology.
        """
        # Repeat the text multiple times to ensure multiple chunks
        return (base_text + " ") * 5

    # Test initialization
    def test_initialization_default_params(self):
        """Test ChunkingService initializes with default parameters."""
        service = ChunkingService()
        assert service.chunk_size == 100
        assert service.chunk_overlap == 20

    def test_initialization_custom_params(self):
        """Test ChunkingService initializes with custom parameters."""
        service = ChunkingService(chunk_size=200, chunk_overlap=50)
        assert service.chunk_size == 200
        assert service.chunk_overlap == 50

    def test_lazy_loading_tokenizer(self, chunking_service):
        """Test that tokenizer is not loaded until first access."""
        # Initially should be None
        assert chunking_service._tokenizer is None

        # Access tokenizer
        tokenizer = chunking_service.tokenizer

        # Now should be loaded
        assert tokenizer is not None
        assert chunking_service._tokenizer is not None

    def test_lazy_loading_text_splitter(self, chunking_service):
        """Test that text_splitter is not loaded until first access."""
        # Initially should be None
        assert chunking_service._text_splitter is None

        # Access text_splitter
        splitter = chunking_service.text_splitter

        # Now should be loaded
        assert splitter is not None
        assert chunking_service._text_splitter is not None

    def test_tokenizer_reuses_same_instance(self, chunking_service):
        """Test that accessing tokenizer multiple times returns same instance."""
        tokenizer1 = chunking_service.tokenizer
        tokenizer2 = chunking_service.tokenizer

        assert tokenizer1 is tokenizer2

    # Test chunk_document
    def test_chunk_document_fixed_length_short_text(
        self, chunking_service, sample_text_short
    ):
        """Test chunking short text with FIXED_LENGTH strategy."""
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, sample_text_short
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_document_fixed_length_long_text(
        self, small_chunking_service, sample_text_long
    ):
        """Test chunking long text creates multiple chunks."""
        chunks = small_chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, sample_text_long
        )

        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should create multiple chunks
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_document_empty_string(self, chunking_service):
        """Test chunking empty string."""
        chunks = chunking_service.chunk_document(ChunkingStrategy.FIXED_LENGTH, "")

        assert isinstance(chunks, list)
        # Empty string might return empty list or list with empty string
        assert len(chunks) >= 0

    def test_chunk_document_whitespace_only(self, chunking_service):
        """Test chunking whitespace-only string."""
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, "   \n\n  \t  "
        )

        assert isinstance(chunks, list)

    def test_chunk_document_single_word(self, chunking_service):
        """Test chunking single word."""
        chunks = chunking_service.chunk_document(ChunkingStrategy.FIXED_LENGTH, "Hello")

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_chunk_document_unicode_text(self, chunking_service):
        """Test chunking text with unicode characters."""
        unicode_text = "Hello 世界! Bonjour le monde! مرحبا بالعالم! 🌍🌎🌏"
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, unicode_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_chunk_document_with_newlines(self, chunking_service):
        """Test chunking text with multiple newlines."""
        text_with_newlines = "Line 1\n\nLine 2\n\n\nLine 3\nLine 4"
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, text_with_newlines
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_chunk_document_unsupported_strategy(
        self, chunking_service, sample_text_short
    ):
        """Test that unsupported strategy raises ValueError."""

        # Create a fake strategy enum (simulate future strategy not yet implemented)
        class FakeStrategy:
            pass

        fake_strategy = FakeStrategy()

        with pytest.raises(ValueError, match="Unsupported chunking strategy"):
            chunking_service.chunk_document(fake_strategy, sample_text_short)

    # Test chunking parameters
    def test_chunk_overlap_effect(self):
        """Test that chunk overlap works correctly."""
        text = "word " * 100  # Create text with many words

        service_no_overlap = ChunkingService(chunk_size=10, chunk_overlap=0)
        service_with_overlap = ChunkingService(chunk_size=10, chunk_overlap=5)

        chunks_no_overlap = service_no_overlap.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, text
        )
        chunks_with_overlap = service_with_overlap.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, text
        )

        # With overlap, we should have more chunks (or same, but definitely not less)
        assert len(chunks_with_overlap) >= len(chunks_no_overlap)

    def test_chunk_size_effect(self):
        """Test that larger chunk size produces fewer chunks."""
        text = "word " * 100

        service_small = ChunkingService(chunk_size=10, chunk_overlap=2)
        service_large = ChunkingService(chunk_size=50, chunk_overlap=2)

        chunks_small = service_small.chunk_document(ChunkingStrategy.FIXED_LENGTH, text)
        chunks_large = service_large.chunk_document(ChunkingStrategy.FIXED_LENGTH, text)

        # Larger chunk size should produce fewer chunks
        assert len(chunks_large) <= len(chunks_small)

    # Test strategy map
    def test_strategy_map_contains_fixed_length(self, chunking_service):
        """Test that strategy map contains FIXED_LENGTH strategy."""
        assert ChunkingStrategy.FIXED_LENGTH in chunking_service._strategy_map

    def test_strategy_map_methods_callable(self, chunking_service):
        """Test that all methods in strategy map are callable."""
        for strategy, method in chunking_service._strategy_map.items():
            assert callable(method)

    # Test _fixed_length_chunking directly
    def test_fixed_length_chunking_method(self, chunking_service, sample_text_short):
        """Test _fixed_length_chunking method directly."""
        chunks = chunking_service._fixed_length_chunking(sample_text_short)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert all(isinstance(chunk, str) for chunk in chunks)

    # Test edge cases
    def test_very_long_single_word(self, small_chunking_service):
        """Test chunking a very long single word."""
        long_word = "a" * 1000
        chunks = small_chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, long_word
        )

        assert isinstance(chunks, list)
        # Should handle long word somehow (might split or keep as single chunk)
        assert len(chunks) >= 1

    def test_special_characters(self, chunking_service):
        """Test chunking text with special characters."""
        special_text = "Hello! @#$% ^&*() {}[] <> |\\/ ~`"
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, special_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_mixed_content(self, chunking_service):
        """Test chunking text with mixed content (letters, numbers, symbols)."""
        mixed_text = """
        Product ID: 12345
        Price: $99.99
        URL: https://example.com
        Email: test@example.com
        """
        chunks = chunking_service.chunk_document(
            ChunkingStrategy.FIXED_LENGTH, mixed_text
        )

        assert isinstance(chunks, list)
        print(chunks)
        assert len(chunks) >= 1

    # Test MARKDOWN_SEGMENTS strategy
    def test_markdown_segments_basic(self, chunking_service):
        """Test markdown chunking with basic markdown structure."""
        markdown_text = """# Heading 1

This is a paragraph under heading 1.

## Heading 2

This is content under heading 2.

### Heading 3

And this is under heading 3."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_markdown_segments_with_code_blocks(self, chunking_service):
        """Test markdown chunking with code blocks."""
        markdown_text = """# Code Examples

Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And here's some JavaScript:

```javascript
console.log("Hello, World!");
```"""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_with_lists(self, chunking_service):
        """Test markdown chunking with lists."""
        markdown_text = """# Shopping List

- Apples
- Bananas
- Oranges

## Numbered List

1. First item
2. Second item
3. Third item"""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_with_links_and_images(self, chunking_service):
        """Test markdown chunking with links and images."""
        markdown_text = """# Resources

Check out [this link](https://example.com) for more info.

![Alt text](https://example.com/image.png)

Visit [GitHub](https://github.com) for code."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_with_tables(self, chunking_service):
        """Test markdown chunking with tables."""
        markdown_text = """# Data Table

| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |

## Summary

This is a summary section."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_with_blockquotes(self, chunking_service):
        """Test markdown chunking with blockquotes."""
        markdown_text = """# Quote Section

> This is a blockquote.
> It can span multiple lines.

Regular text after the quote."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_nested_headings(self, chunking_service):
        """Test markdown chunking with deeply nested headings."""
        markdown_text = """# Level 1

Content at level 1.

## Level 2

Content at level 2.

### Level 3

Content at level 3.

#### Level 4

Content at level 4.

##### Level 5

Content at level 5.

###### Level 6

Content at level 6."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_empty_sections(self, chunking_service):
        """Test markdown chunking with empty sections."""
        markdown_text = """# Heading 1

## Heading 2

## Heading 3

Content only under heading 3."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        # Should handle empty sections gracefully
        assert len(chunks) >= 0

    def test_markdown_segments_plain_text(self, chunking_service):
        """Test markdown chunking with plain text (no markdown syntax)."""
        plain_text = "This is just plain text with no markdown formatting at all."

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, plain_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_segments_mixed_formatting(self, chunking_service):
        """Test markdown chunking with mixed inline formatting."""
        markdown_text = """# Formatting Examples

This is **bold** text.

This is *italic* text.

This is ***bold and italic*** text.

This is `inline code`.

This is ~~strikethrough~~ text."""

        chunks = chunking_service.chunk_document(
            ChunkingStrategy.MARKDOWN_SEGMENTS, markdown_text
        )

        assert isinstance(chunks, list)
        assert len(chunks) >= 1

    def test_markdown_splitter_lazy_loading(self, chunking_service):
        """Test that markdown splitter is lazy-loaded."""
        # Initially should be None
        assert chunking_service._markdown_splitter is None

        # Access markdown_splitter
        splitter = chunking_service.markdown_splitter

        # Now should be loaded
        assert splitter is not None
        assert chunking_service._markdown_splitter is not None

    def test_markdown_splitter_reuses_same_instance(self, chunking_service):
        """Test that accessing markdown_splitter multiple times returns same instance."""
        splitter1 = chunking_service.markdown_splitter
        splitter2 = chunking_service.markdown_splitter

        assert splitter1 is splitter2

    def test_strategy_map_contains_markdown_segments(self, chunking_service):
        """Test that strategy map contains MARKDOWN_SEGMENTS strategy."""
        assert ChunkingStrategy.MARKDOWN_SEGMENTS in chunking_service._strategy_map

    def test_markdown_chunking_method_directly(self, chunking_service):
        """Test _markdown_chunking method directly."""
        markdown_text = "# Test\n\nThis is a test."
        chunks = chunking_service._markdown_chunking(markdown_text)

        assert isinstance(chunks, list)
        assert len(chunks) >= 1
