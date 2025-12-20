"""
Aurora Local Embeddings System
==============================

Production-ready local embedding and vector search system.
Uses TF-IDF inspired hashing - no external dependencies or vector DBs required.

Features:
- Generate embeddings for text chunks locally
- Store embeddings in SQLite or JSON
- Similarity search using cosine similarity
- Works completely offline
"""

import hashlib
import json
import math
import os
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


EMBEDDING_DIM = 384
STOP_WORDS = frozenset([
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that',
    'the', 'to', 'was', 'were', 'will', 'with', 'this', 'but', 'they',
    'have', 'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
])


@dataclass
class Document:
    id: str
    text: str
    embedding: List[float] = field(default_factory=list)
    source: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SearchResult:
    id: str
    text: str
    score: float
    source: Optional[str] = None
    category: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def hash_token(token: str) -> int:
    """DJB2 hash for consistent token hashing."""
    h = 5381
    for char in token:
        h = ((h << 5) + h) ^ ord(char)
    return h & 0x7FFFFFFF


def tokenize(text: str) -> List[str]:
    """Tokenize text into normalized tokens."""
    text = text.lower().strip()
    tokens = re.findall(r'\b[a-z][a-z0-9]{1,}\b', text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def generate_embedding(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """
    Generate a local embedding using TF-IDF inspired hashing.
    
    This creates a fixed-dimension vector representation of text
    without requiring any external APIs or models.
    
    Args:
        text: Input text to embed
        dim: Embedding dimension (default 384)
        
    Returns:
        List of floats representing the embedding vector
    """
    tokens = tokenize(text)
    embedding = [0.0] * dim
    
    if not tokens:
        return embedding
    
    for i, token in enumerate(tokens):
        h = hash_token(token)
        position = h % dim
        weight = 1.0 / math.sqrt(i + 1)
        
        embedding[position] += weight
        embedding[(position + 1) % dim] += weight * 0.5
        embedding[(position + 2) % dim] += weight * 0.25
        
        for j, char in enumerate(token):
            char_hash = (h * (j + 1) + ord(char)) % dim
            embedding[char_hash] += weight * 0.1
    
    magnitude = math.sqrt(sum(v * v for v in embedding)) or 1.0
    return [v / magnitude for v in embedding]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(a) != len(b):
        min_len = min(len(a), len(b))
        a, b = a[:min_len], b[:min_len]
    
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


class LocalEmbeddingStore:
    """
    Local embedding storage and search using SQLite.
    
    Provides a fully offline vector storage and similarity search
    without requiring external vector databases like Pinecone.
    """
    
    def __init__(self, db_path: Union[str, Path] = "data/embeddings.db"):
        """
        Initialize the local embedding store.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    source TEXT,
                    category TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON documents(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON documents(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON documents(created_at)")
            conn.commit()
    
    def store(
        self,
        doc_id: str,
        text: str,
        source: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Store a document with its embedding.
        
        Args:
            doc_id: Unique document identifier
            text: Document text content
            source: Optional source identifier
            category: Optional category
            metadata: Optional additional metadata
            
        Returns:
            Document object with generated embedding
        """
        embedding = generate_embedding(text)
        doc = Document(
            id=doc_id,
            text=text,
            embedding=embedding,
            source=source,
            category=category,
            metadata=metadata or {},
            created_at=datetime.now().isoformat()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO documents 
                (id, text, embedding, source, category, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.id,
                doc.text,
                json.dumps(doc.embedding),
                doc.source,
                doc.category,
                json.dumps(doc.metadata),
                doc.created_at
            ))
            conn.commit()
        
        return doc
    
    def store_batch(self, documents: List[Dict[str, Any]]) -> int:
        """
        Store multiple documents at once.
        
        Args:
            documents: List of document dicts with keys: id, text, source?, category?, metadata?
            
        Returns:
            Number of documents successfully stored
        """
        count = 0
        for doc_data in documents:
            try:
                self.store(
                    doc_id=doc_data['id'],
                    text=doc_data['text'],
                    source=doc_data.get('source'),
                    category=doc_data.get('category'),
                    metadata=doc_data.get('metadata')
                )
                count += 1
            except Exception as e:
                print(f"[LocalEmbeddings] Error storing document {doc_data.get('id')}: {e}")
        return count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        source: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Perform similarity search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            category: Filter by category
            source: Filter by source
            min_score: Minimum similarity score threshold
            
        Returns:
            List of SearchResult objects sorted by similarity
        """
        query_embedding = generate_embedding(query)
        
        with sqlite3.connect(self.db_path) as conn:
            conditions = []
            params: List[Any] = []
            
            if category:
                conditions.append("category = ?")
                params.append(category)
            if source:
                conditions.append("source = ?")
                params.append(source)
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            cursor = conn.execute(
                f"SELECT id, text, embedding, source, category, metadata FROM documents {where_clause}",
                params
            )
            
            results: List[Tuple[float, SearchResult]] = []
            
            for row in cursor:
                doc_id, text, embedding_json, doc_source, doc_category, metadata_json = row
                doc_embedding = json.loads(embedding_json)
                score = cosine_similarity(query_embedding, doc_embedding)
                
                if score >= min_score:
                    results.append((score, SearchResult(
                        id=doc_id,
                        text=text,
                        score=score,
                        source=doc_source,
                        category=doc_category,
                        metadata=json.loads(metadata_json) if metadata_json else {}
                    )))
            
            results.sort(key=lambda x: x[0], reverse=True)
            return [r[1] for r in results[:top_k]]
    
    def get(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, text, embedding, source, category, metadata, created_at FROM documents WHERE id = ?",
                (doc_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return Document(
                    id=row[0],
                    text=row[1],
                    embedding=json.loads(row[2]),
                    source=row[3],
                    category=row[4],
                    metadata=json.loads(row[5]) if row[5] else {},
                    created_at=row[6]
                )
            return None
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_batch(self, doc_ids: List[str]) -> int:
        """Delete multiple documents."""
        count = 0
        for doc_id in doc_ids:
            if self.delete(doc_id):
                count += 1
        return count
    
    def count(self, category: Optional[str] = None) -> int:
        """Get document count."""
        with sqlite3.connect(self.db_path) as conn:
            if category:
                cursor = conn.execute("SELECT COUNT(*) FROM documents WHERE category = ?", (category,))
            else:
                cursor = conn.execute("SELECT COUNT(*) FROM documents")
            return cursor.fetchone()[0]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT category FROM documents WHERE category IS NOT NULL")
            return [row[0] for row in cursor]
    
    def clear(self):
        """Clear all documents."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM documents")
            conn.commit()


class JSONEmbeddingStore:
    """
    Alternative JSON-based storage for simpler use cases.
    
    Stores embeddings in a flat JSON file for portability.
    Best for smaller collections (< 10,000 documents).
    """
    
    def __init__(self, json_path: Union[str, Path] = "data/embeddings.json"):
        """
        Initialize JSON embedding store.
        
        Args:
            json_path: Path to JSON storage file
        """
        self.json_path = Path(json_path)
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        self.documents: Dict[str, Document] = {}
        self._load()
    
    def _load(self):
        """Load documents from JSON file."""
        if self.json_path.exists():
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc_id, doc_data in data.items():
                        self.documents[doc_id] = Document(
                            id=doc_id,
                            text=doc_data['text'],
                            embedding=doc_data['embedding'],
                            source=doc_data.get('source'),
                            category=doc_data.get('category'),
                            metadata=doc_data.get('metadata', {}),
                            created_at=doc_data.get('created_at', datetime.now().isoformat())
                        )
            except Exception as e:
                print(f"[LocalEmbeddings] Error loading JSON store: {e}")
    
    def _save(self):
        """Save documents to JSON file."""
        data = {}
        for doc_id, doc in self.documents.items():
            data[doc_id] = {
                'text': doc.text,
                'embedding': doc.embedding,
                'source': doc.source,
                'category': doc.category,
                'metadata': doc.metadata,
                'created_at': doc.created_at
            }
        
        tmp_path = f"{self.json_path}.tmp"
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        os.replace(tmp_path, self.json_path)
    
    def store(
        self,
        doc_id: str,
        text: str,
        source: Optional[str] = None,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """Store a document with its embedding."""
        embedding = generate_embedding(text)
        doc = Document(
            id=doc_id,
            text=text,
            embedding=embedding,
            source=source,
            category=category,
            metadata=metadata or {},
            created_at=datetime.now().isoformat()
        )
        self.documents[doc_id] = doc
        self._save()
        return doc
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Perform similarity search."""
        query_embedding = generate_embedding(query)
        results: List[Tuple[float, SearchResult]] = []
        
        for doc in self.documents.values():
            if category and doc.category != category:
                continue
            
            score = cosine_similarity(query_embedding, doc.embedding)
            if score >= min_score:
                results.append((score, SearchResult(
                    id=doc.id,
                    text=doc.text,
                    score=score,
                    source=doc.source,
                    category=doc.category,
                    metadata=doc.metadata
                )))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k]]
    
    def get(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save()
            return True
        return False
    
    def count(self) -> int:
        """Get document count."""
        return len(self.documents)
    
    def clear(self):
        """Clear all documents."""
        self.documents.clear()
        self._save()


def get_rag_context(
    store: Union[LocalEmbeddingStore, JSONEmbeddingStore],
    query: str,
    top_k: int = 3,
    min_score: float = 0.1
) -> str:
    """
    Get RAG context for a query.
    
    Args:
        store: Embedding store instance
        query: Search query
        top_k: Number of context chunks to retrieve
        min_score: Minimum similarity score
        
    Returns:
        Formatted context string for LLM prompt
    """
    results = store.search(query, top_k=top_k, min_score=min_score)
    
    if not results:
        return ''
    
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(f"[Context {i}] {result.text}")
    
    return '\nRelevant Context:\n' + '\n\n'.join(context_parts) + '\n'


_default_store: Optional[LocalEmbeddingStore] = None


def get_default_store() -> LocalEmbeddingStore:
    """Get or create the default embedding store."""
    global _default_store
    if _default_store is None:
        _default_store = LocalEmbeddingStore()
    return _default_store


def store_document(doc_id: str, text: str, **kwargs) -> Document:
    """Store a document using the default store."""
    return get_default_store().store(doc_id, text, **kwargs)


def semantic_search(query: str, top_k: int = 5, **kwargs) -> List[SearchResult]:
    """Search using the default store."""
    return get_default_store().search(query, top_k=top_k, **kwargs)


def is_embeddings_available() -> bool:
    """Check if embeddings system is available (always True for local)."""
    return True


if __name__ == "__main__":
    print("Aurora Local Embeddings System")
    print("=" * 40)
    
    store = LocalEmbeddingStore("data/test_embeddings.db")
    
    store.store("doc1", "Python is a programming language.", category="tech")
    store.store("doc2", "Machine learning uses neural networks.", category="ai")
    store.store("doc3", "Aurora is an autonomous AI system.", category="ai")
    
    results = store.search("artificial intelligence programming")
    print(f"\nSearch results for 'artificial intelligence programming':")
    for r in results:
        print(f"  - [{r.score:.3f}] {r.text[:50]}...")
    
    context = get_rag_context(store, "How does Aurora work?")
    print(f"\nRAG Context:\n{context}")
    
    print(f"\nTotal documents: {store.count()}")
    print(f"Categories: {store.get_categories()}")
    print("\nLocal embeddings system is fully operational!")
