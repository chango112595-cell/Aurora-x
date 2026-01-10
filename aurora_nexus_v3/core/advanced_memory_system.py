"""
Advanced Memory System
Self-contained hierarchical memory with semantic, episodic, and procedural memory
No external APIs - uses graph structures, importance weighting, and consolidation
"""

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..utils.local_embeddings import cosine_similarity, generate_embedding


class MemoryType(Enum):
    """Types of memory"""

    SEMANTIC = "semantic"  # Facts, concepts, knowledge
    EPISODIC = "episodic"  # Events, experiences, episodes
    PROCEDURAL = "procedural"  # Skills, procedures, how-to
    WORKING = "working"  # Short-term, active processing


class MemoryImportance(Enum):
    """Memory importance levels"""

    CRITICAL = "critical"  # Never forget
    HIGH = "high"  # Long retention
    MEDIUM = "medium"  # Moderate retention
    LOW = "low"  # Short retention


@dataclass
class Memory:
    """A memory entry"""

    memory_id: str
    memory_type: MemoryType
    content: str
    importance: MemoryImportance
    created_at: datetime
    last_accessed: datetime
    access_count: int
    associations: list[str] = field(default_factory=list)  # Other memory IDs
    embedding: list[float] | None = None
    decay_rate: float = 0.1  # How fast memory decays
    strength: float = 1.0  # Current memory strength


class AdvancedMemorySystem:
    """
    Self-contained advanced memory system
    Manages hierarchical memory with consolidation and retrieval
    """

    def __init__(self):
        self.memories: dict[str, Memory] = {}
        self.memory_index: dict[str, list[str]] = {}  # concept -> [memory_ids]
        self.working_memory: deque = deque(maxlen=100)  # Short-term memory
        self.consolidation_queue: deque = deque(maxlen=1000)
        self._initialize_memory()

    def _initialize_memory(self):
        """Initialize memory system"""
        # Create core semantic memories
        core_memories = [
            ("Aurora is self-contained", MemoryImportance.CRITICAL),
            ("Aurora uses advanced algorithms", MemoryImportance.HIGH),
            ("Workers are autonomous", MemoryImportance.HIGH),
        ]

        for content, importance in core_memories:
            self.store_memory(content, MemoryType.SEMANTIC, importance)

    def store_memory(
        self,
        content: str,
        memory_type: MemoryType,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
    ) -> Memory:
        """Store a memory"""
        memory_id = str(uuid.uuid4())

        # Generate embedding
        embedding = generate_embedding(content)

        memory = Memory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            embedding=embedding,
            decay_rate=self._calculate_decay_rate(importance),
            strength=1.0,
        )

        self.memories[memory_id] = memory

        # Index by concepts
        concepts = self._extract_concepts(content)
        for concept in concepts:
            if concept not in self.memory_index:
                self.memory_index[concept] = []
            self.memory_index[concept].append(memory_id)

        # Add to working memory if important
        if importance in [MemoryImportance.CRITICAL, MemoryImportance.HIGH]:
            self.working_memory.append(memory_id)

        return memory

    def retrieve_memory(self, query: str, memory_type: MemoryType | None = None) -> list[Memory]:
        """Retrieve memories by query"""
        # Generate query embedding
        query_embedding = generate_embedding(query)

        # Find similar memories
        similar_memories = []
        for memory in self.memories.values():
            # Filter by type if specified
            if memory_type and memory.memory_type != memory_type:
                continue

            # Calculate similarity
            if memory.embedding:
                similarity = cosine_similarity(query_embedding, memory.embedding)

                # Apply memory strength
                adjusted_similarity = similarity * memory.strength

                if adjusted_similarity > 0.3:  # Threshold
                    similar_memories.append((memory, adjusted_similarity))

        # Sort by similarity
        similar_memories.sort(key=lambda x: x[1], reverse=True)

        # Update access
        for memory, _ in similar_memories[:10]:  # Top 10
            memory.last_accessed = datetime.now()
            memory.access_count += 1
            # Strengthen memory on access
            memory.strength = min(memory.strength + 0.1, 1.0)

        return [m for m, _ in similar_memories[:10]]

    def consolidate_memories(self):
        """Consolidate memories - strengthen important, weaken unused"""
        now = datetime.now()

        for memory in self.memories.values():
            # Calculate time since last access
            time_since_access = (now - memory.last_accessed).total_seconds()

            # Apply decay
            decay_amount = memory.decay_rate * (time_since_access / 86400)  # Per day

            # Don't decay critical memories
            if memory.importance == MemoryImportance.CRITICAL:
                memory.strength = 1.0
            else:
                memory.strength = max(0.0, memory.strength - decay_amount)

            # Remove very weak memories (except critical)
            if memory.strength < 0.1 and memory.importance != MemoryImportance.CRITICAL:
                # Mark for removal
                self.consolidation_queue.append(memory.memory_id)

        # Remove weak memories
        while self.consolidation_queue:
            memory_id = self.consolidation_queue.popleft()
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                if memory.strength < 0.1:
                    del self.memories[memory_id]
                    # Remove from index
                    for _concept, memory_ids in self.memory_index.items():
                        if memory_id in memory_ids:
                            memory_ids.remove(memory_id)

    def associate_memories(self, memory_id1: str, memory_id2: str):
        """Associate two memories"""
        if memory_id1 in self.memories and memory_id2 in self.memories:
            memory1 = self.memories[memory_id1]
            memory2 = self.memories[memory_id2]

            if memory_id2 not in memory1.associations:
                memory1.associations.append(memory_id2)
            if memory_id1 not in memory2.associations:
                memory2.associations.append(memory_id1)

    def get_related_memories(self, memory_id: str) -> list[Memory]:
        """Get memories related to a memory"""
        if memory_id not in self.memories:
            return []

        memory = self.memories[memory_id]
        related = []

        for related_id in memory.associations:
            if related_id in self.memories:
                related.append(self.memories[related_id])

        return related

    def _calculate_decay_rate(self, importance: MemoryImportance) -> float:
        """Calculate decay rate based on importance"""
        rates = {
            MemoryImportance.CRITICAL: 0.0,  # Never decay
            MemoryImportance.HIGH: 0.01,  # Very slow decay
            MemoryImportance.MEDIUM: 0.05,  # Moderate decay
            MemoryImportance.LOW: 0.1,  # Fast decay
        }
        return rates.get(importance, 0.05)

    def _extract_concepts(self, content: str) -> list[str]:
        """Extract key concepts from content"""
        # Simple concept extraction
        words = content.lower().split()

        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
        }

        concepts = [w for w in words if w not in stop_words and len(w) > 3]
        return list(set(concepts))[:10]  # Top 10 unique concepts

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_memories": len(self.memories),
            "memories_by_type": {
                mt.value: len([m for m in self.memories.values() if m.memory_type == mt])
                for mt in MemoryType
            },
            "memories_by_importance": {
                mi.value: len([m for m in self.memories.values() if m.importance == mi])
                for mi in MemoryImportance
            },
            "working_memory_size": len(self.working_memory),
            "average_strength": (
                sum(m.strength for m in self.memories.values()) / len(self.memories)
                if self.memories
                else 0.0
            ),
        }
