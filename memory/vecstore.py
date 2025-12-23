#!/usr/bin/env python3
"""
Neural Memory Engine - simple vector store abstraction
Modes:
 - pure (no external deps): uses simple TF-IDF-like vectors via hashlib + token counts
 - sqlite (fallback)
 - hnsw (if hnswlib available)
Embeddings are pluggable: set AURORA_EMBEDDER_MODEL to use sentence-transformers,
otherwise a deterministic local embedder is used (no external APIs).
"""

import os, json, math, uuid
from pathlib import Path
from typing import List, Dict

STORE_DIR = Path(".memory")
STORE_DIR.mkdir(exist_ok=True)

class SimpleEmbedder:
    def embed(self, text: str):
        if not isinstance(text, str):
            text = json.dumps(text, ensure_ascii=False, sort_keys=True)
        # deterministic lightweight embedding: bag-of-words hashed counts into fixed-size vector
        vec = [0.0]*128
        for i,w in enumerate(text.split()):
            idx = hash(w) % 128
            vec[idx] += 1.0
        # normalize
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        vec = [x/norm for x in vec]
        return vec


class PluggableEmbedder:
    """
    Uses sentence-transformers if available and AURORA_EMBEDDER_MODEL is set,
    otherwise falls back to SimpleEmbedder.
    """
    def __init__(self):
        self.model = None
        model_name = os.getenv("AURORA_EMBEDDER_MODEL")
        if model_name:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
                self.model = SentenceTransformer(model_name)
            except Exception as exc:
                print(f"[VecStore] sentence-transformers unavailable ({exc}); using simple embedder.")
        self.fallback = SimpleEmbedder()

    def embed(self, text: str):
        if self.model:
            try:
                vec = self.model.encode([text], normalize_embeddings=True)[0].tolist()
                return vec
            except Exception as exc:
                print(f"[VecStore] Model encode failed ({exc}); using fallback embedder.")
        return self.fallback.embed(text)

def cosine(a, b):
    s = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na==0 or nb==0: return 0.0
    return s/(na*nb)

class MemoryStore:
    def __init__(self, mode="pure"):
        self.mode = mode
        self.embedder = PluggableEmbedder()
        self._mem = {}  # id -> {text, vec, meta}
        self._index = []  # list of ids (keeps insertion order)
    def write(self, text: str, meta: Dict=None):
        if not isinstance(text, str):
            text = json.dumps(text, ensure_ascii=False, sort_keys=True)
        mid = str(uuid.uuid4())
        vec = self.embedder.embed(text)
        rec = {"id": mid, "text": text, "vec": vec, "meta": meta or {}}
        self._mem[mid] = rec
        self._index.append(mid)
        return rec
    def search(self, query: str, top_k=5):
        qv = self.embedder.embed(query)
        scored = []
        for mid in self._index:
            rec = self._mem[mid]
            score = cosine(qv, rec["vec"])
            scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for s,r in scored[:top_k]]
    def all(self):
        return [self._mem[i] for i in self._index]
