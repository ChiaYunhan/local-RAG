"""
Abstractive summarization implementation using transformer models.

Supports various models:
- T5 (small, base)
- FLAN-T5 (small, base) - instruction-tuned
- BART (large-cnn)
- DistilBART
- Pegasus

Includes support for 8-bit quantization for memory efficiency.
"""

import logging
from typing import List, Optional

from .base import BaseSummarizer
from .enums import ModelType

logger = logging.getLogger(__name__)


class AbstractiveSummarizer(BaseSummarizer):
    """
    Abstractive summarization - generates new summary text using transformer models.

    Supports various models from Hugging Face:
    - BART: facebook/bart-large-cnn (good quality, larger model ~1.6GB)
    - T5: t5-small (lightweight, ~240MB), t5-base (~850MB)
    - FLAN-T5: google/flan-t5-small/base (instruction-tuned, better quality)
    - DistilBART: sshleifer/distilbart-cnn-12-6 (faster, smaller ~1.2GB)

    Quantization support:
    - Set load_in_8bit=True to enable 8-bit quantization
    - Reduces memory usage by ~50%
    - Recommended for larger models on Mac with 16GB RAM
    """

    def __init__(
        self,
        model_name: str = ModelType.LITE_FLAN_T5_SMALL.value,
        load_in_8bit: bool = False,
    ):
        self.model_name = model_name
        self.load_in_8bit = load_in_8bit
        self._model = None
        self._tokenizer = None
        self._device = None

    @property
    def device(self):
        """Determine device (CPU/GPU/MPS) for model inference."""
        if self._device is None:
            import torch

            if torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available():
                # Apple Silicon MPS (Metal Performance Shaders)
                self._device = "mps"
            else:
                self._device = "cpu"
        return self._device

    @property
    def model(self):
        """Lazy-load the summarization model with optional quantization."""
        if self._model is None:
            from transformers import AutoModelForSeq2SeqLM, BitsAndBytesConfig
            import torch

            logger.info(f"Loading summarization model: {self.model_name}")

            # Load model with optional quantization
            if self.load_in_8bit:
                logger.info("Loading with 8-bit quantization for memory efficiency...")

                # Configure 8-bit quantization
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_threshold=6.0,  # Threshold for outlier detection
                )

                self._model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    quantization_config=quantization_config,
                    device_map="auto",  # Automatically distribute across devices
                )
                logger.info(f"Model loaded with 8-bit quantization")
            else:
                self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self._model.to(self.device)
                logger.info(f"Model loaded on {self.device}")

            self._model.eval()  # Set to evaluation mode
        return self._model

    @property
    def tokenizer(self):
        """Lazy-load the tokenizer."""
        if self._tokenizer is None:
            from transformers import AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        return self._tokenizer

    def summarize(
        self,
        chunks: List[str],
        max_length: Optional[int] = None,
        prompt: Optional[str] = None,
    ) -> str:
        """
        Generate abstractive summary using transformer model.

        Args:
            chunks: List of text chunks from ChunkingService
            max_length: Maximum length of generated summary in tokens
            prompt: Optional instruction prompt (useful for FLAN-T5/instruction-tuned models)
                   Examples: "Summarize the following:", "Write a brief summary:",
                   If None, uses model-specific defaults

        Returns:
            Generated summary text as a single string
        """
        max_length = max_length or 150

        # Combine chunks into single text for abstractive summarization
        combined_text = " ".join(chunks)

        # Add prompt if provided, or use model-specific defaults
        if prompt:
            # User-provided prompt
            input_text = f"{prompt} {combined_text}"
        elif "flan" in self.model_name.lower():
            # FLAN-T5 models benefit from instruction prompts
            input_text = f"Summarize the following text: {combined_text}"
        elif "t5" in self.model_name.lower():
            # Regular T5 models need "summarize:" prefix
            input_text = f"summarize: {combined_text}"
        else:
            # BART, Pegasus, etc. - no prefix needed
            input_text = combined_text

        # Tokenize input with truncation (models have max input length)
        inputs = self.tokenizer(
            input_text, max_length=1024, truncation=True, return_tensors="pt"
        ).to(self.device)

        # Generate summary
        summary_ids = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=int(max_length * 0.2),  # Min length is 20% of max
            length_penalty=2.0,  # Encourages longer summaries
            num_beams=4,  # Beam search for better quality
            early_stopping=True,
        )

        # Decode and return summary
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
