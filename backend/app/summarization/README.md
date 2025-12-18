# Summarization Package

Modular summarization system with extractive and abstractive strategies.

## Structure

```
app/summarization/
├── __init__.py          # Package exports
├── enums.py            # Enumerations (SummaryType, SummaryStrategy, ModelType)
├── base.py             # Abstract base class (BaseSummarizer)
├── extractive.py       # Extractive summarization (ExtractiveSummarizer)
├── abstractive.py      # Abstractive summarization (AbstractiveSummarizer)
├── service.py          # High-level orchestration (SummaryService)
└── README.md           # This file
```

## Modules

### `enums.py`
Defines strategy and model enumerations:
- **SummaryType**: EXTRACTIVE, ABSTRACTIVE
- **SummaryStrategy**: Workflow strategies (e.g., EXTRACTIVE_TO_ABSTRACTIVE)
- **ModelType**: Preset transformer models (T5, FLAN-T5, BART, etc.)

### `base.py`
Abstract base class defining the summarizer interface:
- `BaseSummarizer.summarize(chunks, max_length)` - Must be implemented by all summarizers

### `extractive.py`
Extractive summarization implementation with three strategies:
- **simple**: Takes first N sentences (fast baseline)
- **tfidf**: TF-IDF scoring with scikit-learn (keyword-based)
- **embedding_cluster**: Semantic clustering with ModernBERT embeddings

Features:
- Configurable number of sentences to extract
- Optional context window for better embeddings
- Maintains original sentence order

### `abstractive.py`
Abstractive summarization using transformer models:
- Supports T5, FLAN-T5, BART, DistilBART, Pegasus
- Automatic device detection (CUDA/MPS/CPU)
- Optional 8-bit quantization for memory efficiency
- Model-specific prompt handling

### `service.py`
High-level service orchestrating multi-level summarization:
- Topic-level summaries (per section/topic)
- Final summary (combining all topics)
- Four workflow strategies:
  1. Abstractive → Abstractive
  2. Extractive → Abstractive
  3. Extractive → Extractive
  4. Direct Extractive (no topic-level summaries)

## Usage

### Basic Extractive Summarization

```python
from app.summarization import ExtractiveSummarizer

# TF-IDF based (default)
summarizer = ExtractiveSummarizer(num_sentences=5, strategy="tfidf")
summary = summarizer.summarize(sentences)

# Embedding-based clustering
summarizer = ExtractiveSummarizer(
    num_sentences=5,
    strategy="embedding_cluster",
    embedding_model="answerdotai/ModernBERT-base",
    context_window=1
)
summary = summarizer.summarize(sentences)
```

### Basic Abstractive Summarization

```python
from app.summarization import AbstractiveSummarizer, ModelType

# FLAN-T5 (recommended for Mac)
summarizer = AbstractiveSummarizer(
    model_name=ModelType.LITE_FLAN_T5_SMALL.value
)
summary = summarizer.summarize(chunks, max_length=150)

# BART with quantization (best quality)
summarizer = AbstractiveSummarizer(
    model_name=ModelType.FINAL_BART.value,
    load_in_8bit=True
)
summary = summarizer.summarize(chunks, max_length=150)
```

### Full Pipeline with SummaryService

```python
from app.summarization import SummaryService, SummaryStrategy, ModelType

# Strategy 1: Extractive → Abstractive (recommended)
service = SummaryService(
    strategy=SummaryStrategy.EXTRACTIVE_TO_ABSTRACTIVE,
    lite_model=ModelType.LITE_FLAN_T5_SMALL,
    final_model=ModelType.FINAL_FLAN_T5_BASE,
    topic_summary_length=3,
    final_summary_length=5,
)

# Strategy 2: Extractive → Extractive (fastest, no models needed)
service = SummaryService(
    strategy=SummaryStrategy.EXTRACTIVE_TO_EXTRACTIVE,
    topic_summary_length=3,
    final_summary_length=5,
)

# Strategy 3: Abstractive → Abstractive (best quality, slowest)
service = SummaryService(
    strategy=SummaryStrategy.ABSTRACTIVE_TO_ABSTRACTIVE,
    lite_model=ModelType.LITE_FLAN_T5_SMALL,
    final_model=ModelType.FINAL_BART,
    topic_summary_length=100,  # max tokens
    final_summary_length=150,  # max tokens
)

# Strategy 4: Direct Extractive (single pass, no topic summaries)
service = SummaryService(
    strategy=SummaryStrategy.EXTRACTIVE_ONLY,
    final_summary_length=5,
)

# Generate summaries
topic_chunks = {
    "Introduction": ["sentence 1", "sentence 2", ...],
    "Methods": ["sentence 1", "sentence 2", ...],
    "Results": ["sentence 1", "sentence 2", ...],
}

result = service.summarize(topic_chunks)
print(result["final_summary"])
print(result["topic_summaries"])  # Empty dict for EXTRACTIVE_ONLY
```

### Direct Summarization

```python
# Summarize without topics (alternative to EXTRACTIVE_ONLY)
summary = service.summarize_direct(all_sentences)
```

## Backward Compatibility

The old `app/summaryService.py` module still works for backward compatibility:

```python
# Old import (still works)
from app.summaryService import SummaryService

# New import (preferred)
from app.summarization import SummaryService
```

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Lazy Loading**: Models loaded only when first accessed
3. **Strategy Pattern**: Easy to add new summarization strategies
4. **Factory Pattern**: Service creates appropriate summarizers based on strategy
5. **Dependency Injection**: Models and parameters configurable at initialization

## Adding New Strategies

To add a new extractive strategy:

1. Add method to `ExtractiveSummarizer`: `def _extract_new_strategy(self, sentences, num_sentences)`
2. Update `summarize()` method to handle the new strategy
3. Update docstrings and error messages

To add a new model:

1. Add to `ModelType` enum in `enums.py`
2. No code changes needed in `abstractive.py` (automatic support)

## Testing

Run tests for each module:

```bash
# Test extractive strategies
python test_extractive_embedding.py

# Test abstractive models
python test_abstractive.py
```

## Dependencies

- **Extractive**:
  - scikit-learn (TF-IDF)
  - sentence-transformers (embeddings)
  - numpy (matrix operations)

- **Abstractive**:
  - transformers (Hugging Face models)
  - torch (PyTorch)
  - optimum (quantization)
  - accelerate (distributed loading)
  - bitsandbytes (8-bit quantization)

## Performance

| Strategy | Speed | Quality | Memory |
|----------|-------|---------|--------|
| simple | ⚡⚡⚡ | ⭐ | Minimal |
| tfidf | ⚡⚡ | ⭐⭐⭐ | Minimal |
| embedding_cluster | ⚡ | ⭐⭐⭐⭐⭐ | ~500MB |
| abstractive (FLAN-T5) | ⚡⚡ | ⭐⭐⭐⭐ | ~1-2GB |
| abstractive (BART) | ⚡ | ⭐⭐⭐⭐⭐ | ~4-8GB |
