"""
External Knowledge Integration System
Self-contained external knowledge integration without external APIs
Uses internal knowledge base, pattern matching, and knowledge synthesis
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..utils.local_embeddings import LocalEmbeddingStore


@dataclass
class KnowledgeEntry:
    """Knowledge entry"""

    id: str
    content: str
    source: str
    category: str
    metadata: dict[str, Any]
    created_at: datetime


class ExternalKnowledgeIntegration:
    """
    Self-contained external knowledge integration
    Integrates knowledge from various sources (all internal)
    """

    def __init__(self, knowledge_store: LocalEmbeddingStore | None = None):
        self.knowledge_store = knowledge_store or LocalEmbeddingStore("data/external_knowledge.db")
        self.knowledge_sources: dict[str, dict[str, Any]] = {}
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Initialize internal knowledge base"""
        # Store common programming knowledge
        common_knowledge = [
            {
                "id": "python_best_practices",
                "content": "Python best practices include PEP 8 style guide, type hints, docstrings, and proper error handling",
                "source": "internal",
                "category": "programming",
            },
            {
                "id": "security_basics",
                "content": "Security best practices include input validation, parameterized queries, encryption, and secure authentication",
                "source": "internal",
                "category": "security",
            },
            {
                "id": "performance_optimization",
                "content": "Performance optimization techniques include caching, algorithm optimization, resource pooling, and async processing",
                "source": "internal",
                "category": "performance",
            },
        ]

        for entry in common_knowledge:
            self.knowledge_store.store(
                doc_id=entry["id"],
                text=entry["content"],
                source=entry["source"],
                category=entry["category"],
            )

    def search_knowledge(
        self, query: str, category: str | None = None, top_k: int = 5
    ) -> list[dict[str, Any]]:
        """Search knowledge base"""
        results = self.knowledge_store.search(query, top_k=top_k, category=category)

        return [
            {
                "content": result.text,
                "source": result.source,
                "category": result.category,
                "score": result.score,
                "metadata": result.metadata,
            }
            for result in results
        ]

    def add_knowledge(
        self, content: str, source: str, category: str, metadata: dict[str, Any] | None = None
    ):
        """Add knowledge to base"""
        doc_id = f"knowledge_{datetime.now().timestamp()}"
        self.knowledge_store.store(
            doc_id=doc_id,
            text=content,
            source=source,
            category=category,
            metadata=metadata or {},
        )

    def get_knowledge_context(self, query: str, max_chunks: int = 3) -> str:
        """Get knowledge context for query"""
        results = self.search_knowledge(query, top_k=max_chunks)

        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{result['source']}] {result['content']}")

        return "\n".join(context_parts)

    def synthesize_knowledge(self, queries: list[str]) -> dict[str, Any]:
        """Synthesize knowledge from multiple queries"""
        all_results: list[dict[str, Any]] = []

        for query in queries:
            results = self.search_knowledge(query)
            all_results.extend(results)

        # Deduplicate and rank
        seen_content: set[str] = set()
        unique_results: list[dict[str, Any]] = []

        for result in sorted(all_results, key=lambda x: x["score"], reverse=True):
            if result["content"] not in seen_content:
                seen_content.add(result["content"])
                unique_results.append(result)

        return {
            "synthesized_knowledge": unique_results[:10],
            "total_sources": len(set(r["source"] for r in unique_results)),
            "categories": list(set(r["category"] for r in unique_results)),
        }
