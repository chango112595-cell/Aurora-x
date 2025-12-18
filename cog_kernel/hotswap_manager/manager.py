#!/usr/bin/env python3
"""
High-level memory manager that orchestrates short-term and long-term memory,
handles consolidation and forgetting policies.
"""

from memory.vecstore import MemoryStore

class MemoryMediator:
    def __init__(self):
        self.short = MemoryStore()
        self.long = MemoryStore()

    def write_event(self, text, meta=None, longterm=False):
        if longterm:
            return self.long.write(text, meta)
        return self.short.write(text, meta)

    def query(self, q, top_k=5):
        # search both and merge
        s1 = self.short.search(q, top_k=top_k)
        s2 = self.long.search(q, top_k=top_k)
        # dedupe by id
        seen = set()
        out = []
        for r in s1 + s2:
            if r["id"] in seen: continue
            seen.add(r["id"]); out.append(r)
        return out[:top_k]
