"""Aurora Nexus V3 Utilities"""

from .atomic_io import atomic_json_write, load_snapshot
from .local_embeddings import (
    Document,
    JSONEmbeddingStore,
    LocalEmbeddingStore,
    SearchResult,
    cosine_similarity,
    generate_embedding,
    get_rag_context,
    is_embeddings_available,
    semantic_search,
    store_document,
)

__all__ = [
    "atomic_json_write",
    "load_snapshot",
    "generate_embedding",
    "cosine_similarity",
    "LocalEmbeddingStore",
    "JSONEmbeddingStore",
    "get_rag_context",
    "store_document",
    "semantic_search",
    "is_embeddings_available",
    "Document",
    "SearchResult",
]
