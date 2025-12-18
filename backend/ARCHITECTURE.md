# Architecture Overview

## Summarization Package Structure

```
app/
├── summarization/              # New modular package
│   ├── __init__.py            # Package exports
│   ├── README.md              # Package documentation
│   ├── enums.py               # Enums (290 lines)
│   │   ├── SummaryType
│   │   ├── SummaryStrategy
│   │   └── ModelType
│   ├── base.py                # Abstract base (24 lines)
│   │   └── BaseSummarizer
│   ├── extractive.py          # Extractive impl (252 lines)
│   │   └── ExtractiveSummarizer
│   │       ├── _extract_simple()
│   │       ├── _extract_tfidf()
│   │       └── _extract_embedding_cluster()
│   ├── abstractive.py         # Abstractive impl (174 lines)
│   │   └── AbstractiveSummarizer
│   └── service.py             # Orchestration (180 lines)
│       └── SummaryService
└── summaryService.py          # Backward compatibility (35 lines)
```

## Class Hierarchy

```
BaseSummarizer (ABC)
    │
    ├── ExtractiveSummarizer
    │   ├── Strategy: simple
    │   ├── Strategy: tfidf
    │   └── Strategy: embedding_cluster
    │
    └── AbstractiveSummarizer
        ├── T5 models
        ├── FLAN-T5 models
        ├── BART models
        └── Pegasus models

SummaryService
    ├── lite_summarizer: BaseSummarizer (lazy-loaded)
    └── final_summarizer: BaseSummarizer (lazy-loaded)
```

## Data Flow

### Full Pipeline

```
Document
    │
    ├─> ChunkingService (SENTENCE_CHUNKING)
    │       │
    │       └─> sentences: List[str]
    │
    ├─> Topic Assignment
    │       │
    │       └─> topic_chunks: Dict[str, List[str]]
    │
    ├─> SummaryService.generate_topic_summaries()
    │       │
    │       ├─> lite_summarizer (ExtractiveSummarizer or AbstractiveSummarizer)
    │       │
    │       └─> topic_summaries: Dict[str, str]
    │
    └─> SummaryService.generate_final_summary()
            │
            ├─> final_summarizer (ExtractiveSummarizer or AbstractiveSummarizer)
            │
            └─> final_summary: str
```

### Direct Summarization

```
Document
    │
    ├─> ChunkingService
    │       │
    │       └─> chunks: List[str]
    │
    └─> SummaryService.summarize_direct()
            │
            ├─> final_summarizer
            │
            └─> summary: str
```

## Strategy Selection

```python
SummaryStrategy:
    EXTRACTIVE_TO_EXTRACTIVE
        ├─> lite_summarizer: ExtractiveSummarizer
        └─> final_summarizer: ExtractiveSummarizer

    EXTRACTIVE_TO_ABSTRACTIVE  # Most common
        ├─> lite_summarizer: ExtractiveSummarizer
        └─> final_summarizer: AbstractiveSummarizer

    ABSTRACTIVE_TO_ABSTRACTIVE
        ├─> lite_summarizer: AbstractiveSummarizer
        └─> final_summarizer: AbstractiveSummarizer
```

## Module Responsibilities

| Module           | Responsibility                  |
| ---------------- | ------------------------------- |
| `enums.py`       | Define constants and presets    |
| `base.py`        | Define interface                |
| `extractive.py`  | Implement extractive strategies |
| `abstractive.py` | Implement transformer models    |
| `service.py`     | Orchestrate pipeline            |

## Extending the System

### Adding a New Extractive Strategy

1. **Edit `extractive.py`**:

```python
def _extract_new_strategy(self, sentences: List[str], num_sentences: int) -> List[str]:
    # Your implementation
    return selected_sentences
```

2. **Update `summarize()` method**:

```python
elif self.strategy == "new_strategy":
    selected = self._extract_new_strategy(chunks, num_sentences)
```

### Adding a New Model Preset

1. **Edit `enums.py`**:

```python
class ModelType(enum.Enum):
    # ... existing models ...
    NEW_MODEL = "model-id-from-huggingface"
```

2. **Use immediately** - no other changes needed:

```python
summarizer = AbstractiveSummarizer(model_name=ModelType.NEW_MODEL.value)
```

### Adding a New Workflow Strategy

1. **Edit `enums.py`**:

```python
class SummaryStrategy(enum.Enum):
    # ... existing strategies ...
    NEW_WORKFLOW = "description_of_workflow"
```

2. **Update `service.py`**:

```python
def _uses_extractive_topic_summaries(self) -> bool:
    return self.strategy in {
        SummaryStrategy.EXTRACTIVE_TO_ABSTRACTIVE,
        SummaryStrategy.NEW_WORKFLOW,  # If applicable
    }
```

## Testing Strategy

```
Unit Tests (Per Module)
    ├── test_extractive_simple.py
    ├── test_extractive_tfidf.py
    ├── test_extractive_embedding.py
    ├── test_abstractive_t5.py
    ├── test_abstractive_bart.py
    └── test_service_pipeline.py

Integration Tests
    └── test_end_to_end_summarization.py
```

## Future Enhancements

### Potential Additions

1. **New Extractive Strategies**:

   - TextRank (graph-based)
   - LexRank (graph-based)
   - MMR (Maximal Marginal Relevance)

2. **New Abstractive Models**:

   - LED (Longformer Encoder-Decoder)
   - BigBird-Pegasus
   - GPT-based summarization

3. **Hybrid Approaches**:

   - Extractive + Rewriting
   - Hierarchical summarization
   - Query-focused summarization

4. **Optimization**:
   - Batch processing
   - Caching embeddings
   - Model quantization (4-bit)
   - ONNX runtime support
