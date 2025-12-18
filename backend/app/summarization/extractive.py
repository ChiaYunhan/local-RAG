"""
Extractive summarization implementation.

Supports multiple extraction strategies:
- simple: Takes first N sentences
- tfidf: TF-IDF based scoring with scikit-learn
- embedding_cluster: Semantic clustering with embeddings
"""

import logging
from typing import List, Optional

from .base import BaseSummarizer

logger = logging.getLogger(__name__)


class ExtractiveSummarizer(BaseSummarizer):
    """
    Extractive summarization - selects important sentences from text.

    Supports multiple extraction strategies:
    - simple: Takes first N sentences (fast)
    - tfidf: Scores sentences by TF-IDF (no embeddings needed)
    - embedding_cluster: Uses embeddings + clustering for semantic extraction
      - Generates embeddings with ModernBERT or similar models
      - Clusters sentences using K-means
      - Extracts sentences closest to cluster centers

    Expects input to be pre-chunked by ChunkingService with SENTENCE_CHUNKING strategy.
    """

    def __init__(
        self,
        num_sentences: int = 3,
        strategy: str = "tfidf",  # "simple", "tfidf", or "embedding_cluster"
        embedding_model: str = "answerdotai/ModernBERT-base",
        context_window: int = 0,  # Number of sentences before/after to include in context
    ):
        self.num_sentences = num_sentences
        self.strategy = strategy
        self.embedding_model = embedding_model
        self.context_window = context_window
        self._embedder = None  # Lazy-loaded embedding model

    @property
    def embedder(self):
        """Lazy-load the sentence embedding model."""
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.embedding_model}")
            self._embedder = SentenceTransformer(self.embedding_model)
            logger.info("Embedding model loaded successfully")
        return self._embedder

    def _add_context_to_sentences(self, sentences: List[str]) -> List[str]:
        """
        Add context from surrounding sentences for better embeddings.

        Args:
            sentences: List of sentences

        Returns:
            List of sentences with added context (original position preserved)
        """
        if self.context_window == 0:
            return sentences

        contextualized = []
        for i, sent in enumerate(sentences):
            # Get surrounding sentences
            start_idx = max(0, i - self.context_window)
            end_idx = min(len(sentences), i + self.context_window + 1)

            # Combine with context
            context_sents = sentences[start_idx:end_idx]
            contextualized.append(" ".join(context_sents))

        return contextualized

    def _extract_simple(self, sentences: List[str], num_sentences: int) -> List[str]:
        """Simple extraction: take first N sentences."""
        return sentences[:num_sentences]

    def _extract_tfidf(self, sentences: List[str], num_sentences: int) -> List[str]:
        """
        TF-IDF based extraction using scikit-learn.

        Uses TfidfVectorizer to compute TF-IDF scores for each sentence,
        then ranks sentences by the sum of their TF-IDF scores.

        Args:
            sentences: List of sentences to extract from
            num_sentences: Number of sentences to extract

        Returns:
            List of extracted sentences in original order
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np

        logger.info(f"Starting TF-IDF extraction for {len(sentences)} sentences")

        # Create TF-IDF vectorizer
        # - lowercase=True: Convert all text to lowercase
        # - stop_words='english': Remove common English words
        # - min_df=1: Keep words that appear in at least 1 document
        # - max_df=0.8: Remove words that appear in >80% of documents (too common)
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            min_df=1,
            max_df=0.8,
            token_pattern=r'\b[a-zA-Z]{3,}\b'  # Only words with 3+ letters
        )

        # Compute TF-IDF matrix: (num_sentences, num_terms)
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # Calculate sentence scores by summing TF-IDF values across all terms
        sentence_scores = np.asarray(tfidf_matrix.sum(axis=1)).flatten()

        # Get indices of top N sentences by score
        top_indices = np.argsort(sentence_scores)[-num_sentences:]

        # Sort by original position to maintain document order
        top_indices_sorted = sorted(top_indices)

        # Extract sentences
        selected_sentences = [sentences[idx] for idx in top_indices_sorted]

        logger.info(f"Extracted {len(selected_sentences)} sentences using TF-IDF")
        return selected_sentences

    def _extract_embedding_cluster(
        self, sentences: List[str], num_sentences: int
    ) -> List[str]:
        """
        Embedding-based clustering extraction using ModernBERT.

        Process:
        1. Generate embeddings for each sentence (optionally with context)
        2. Cluster embeddings using K-means
        3. Extract sentences closest to each cluster center
        4. Return sentences in original order

        Args:
            sentences: List of sentences to extract from
            num_sentences: Number of sentences to extract

        Returns:
            List of extracted sentences in original order
        """
        from sklearn.cluster import KMeans
        import numpy as np

        if len(sentences) <= num_sentences:
            return sentences

        logger.info(
            f"Starting embedding-based extraction for {len(sentences)} sentences"
        )

        # Step 1: Add context to sentences if configured
        contextualized_sentences = self._add_context_to_sentences(sentences)

        # Step 2: Generate embeddings
        logger.info("Generating sentence embeddings...")
        embeddings = self.embedder.encode(
            contextualized_sentences, show_progress_bar=False, convert_to_numpy=True
        )

        # Step 3: Cluster embeddings
        # Use min(num_sentences, len(sentences)) clusters
        n_clusters = min(num_sentences, len(sentences))
        logger.info(f"Clustering {len(sentences)} sentences into {n_clusters} clusters")

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)

        # Step 4: Find sentence closest to each cluster center
        selected_indices = []
        for cluster_id in range(n_clusters):
            # Get cluster center
            center = kmeans.cluster_centers_[cluster_id]

            # Find sentences in this cluster
            cluster_mask = kmeans.labels_ == cluster_id
            cluster_indices = np.where(cluster_mask)[0]

            if len(cluster_indices) == 0:
                continue

            # Calculate distances from center for sentences in this cluster
            cluster_embeddings = embeddings[cluster_indices]
            distances = np.linalg.norm(cluster_embeddings - center, axis=1)

            # Get index of sentence closest to center
            closest_idx_in_cluster = np.argmin(distances)
            closest_sentence_idx = cluster_indices[closest_idx_in_cluster]

            selected_indices.append(closest_sentence_idx)

        # Step 5: Sort by original position and extract sentences
        selected_indices.sort()
        selected_sentences = [sentences[idx] for idx in selected_indices]

        logger.info(f"Extracted {len(selected_sentences)} sentences using clustering")
        return selected_sentences

    def summarize(self, chunks: List[str], max_length: Optional[int] = None) -> str:
        """
        Extract key sentences from pre-chunked text.

        Args:
            chunks: List of text chunks (sentences) from ChunkingService
            max_length: Maximum number of sentences (overrides num_sentences if provided)

        Returns:
            Summary containing extracted sentences joined as a single string
        """
        num_sentences = max_length if max_length else self.num_sentences

        if len(chunks) <= num_sentences:
            # If already short enough, return as-is
            return " ".join(chunks)

        # Extract based on strategy
        if self.strategy == "simple":
            selected = self._extract_simple(chunks, num_sentences)
        elif self.strategy == "tfidf":
            selected = self._extract_tfidf(chunks, num_sentences)
        elif self.strategy == "embedding_cluster":
            selected = self._extract_embedding_cluster(chunks, num_sentences)
        else:
            raise ValueError(
                f"Unknown extraction strategy: {self.strategy}. Supported strategies: 'simple', 'tfidf', 'embedding_cluster'"
            )

        return " ".join(selected)
