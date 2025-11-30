# Neural Memory Engine

Modes:
- pure (default): no deps; simple vectorizer (not semantic)
- enable real embeddings: pip install sentence-transformers, modify MemoryStore to use real model
- accelerate search: install hnswlib and create HNSW index for vectors

Example:

```python
from memory.vecstore import MemoryStore
m = MemoryStore()
m.write("Alice is a dev", {"tag":"person"})
m.write("Bob likes boats", {"tag":"person"})
print(m.search("developer"))
```

Production notes:
- Use persistent ANN (hnswlib or FAISS) backed by disk
- Encrypt memory store at rest for privacy
- Rotate and age-out memory entries
