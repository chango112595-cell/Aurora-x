#!/usr/bin/env python3
"""
Aurora Memory Fabric v2
-----------------------
Hybrid multi-tier memory engine with:
- Short/Mid/Long/Semantic tiers
- Project & conversation compartments
- Fact/Event stores
- Summarization & auto-compression
- Encryption-ready data layer

Author: Aurora AI System
Version: 2.0-enhanced
"""

import datetime
import hashlib
import json
import math
import os
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MemoryEntry:
    """Single memory entry with full metadata"""

    id: str
    content: str
    role: str
    timestamp: str
    layer: str
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None


class SimpleEmbedder:
    """Lightweight embedding generator for semantic search"""

    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """Generate a simple bag-of-words hash embedding"""
        vec = [0.0] * self.dimensions
        words = text.lower().split()
        for i, word in enumerate(words):
            idx = hash(word) % self.dimensions
            vec[idx] += 1.0 * (1.0 / (i + 1))
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class AuroraMemoryFabric:
    """
    Aurora Memory Fabric v2
    -----------------------
    Hybrid multi-tier memory engine with:
    - Short/Mid/Long/Semantic tiers
    - Project & conversation compartments
    - Fact/Event stores
    - Summarization & auto-compression
    - Encryption-ready data layer
    - Integrity verification
    - Automatic backups
    """

    SHORT_TERM_THRESHOLD = 10
    MID_TERM_THRESHOLD = 10
    LONG_TERM_MAX = 100
    SEMANTIC_MAX = 500

    def __init__(self, base: str = "data/memory"):
        self.base = base
        os.makedirs(self.base, exist_ok=True)

        self.active_project: str | None = None
        self.active_conversation: str | None = None

        self.short_term: list[MemoryEntry] = []
        self.mid_term: list[MemoryEntry] = []
        self.long_term: list[MemoryEntry] = []
        self.semantic_memory: list[MemoryEntry] = []
        self.embedding_index: dict[int, list[float]] = {}
        self.fact_cache: dict[str, Any] = {}
        self.event_log: list[dict[str, Any]] = []

        self.embedder = SimpleEmbedder()
        self.session_id = (
            f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        )
        self.message_count = 0

        self._ensure_global_structure()
        print(f"[Memory Fabric 2.0] Initialized | Session: {self.session_id}")

    def _ensure_global_structure(self) -> None:
        """Create global directory structure"""
        global_path = Path(self.base) / "global"
        global_path.mkdir(parents=True, exist_ok=True)

        manifest_path = global_path / "manifest.json"
        if not manifest_path.exists():
            self._save_json(
                manifest_path,
                {
                    "fabric_version": "2.0-enhanced",
                    "created": str(datetime.datetime.now()),
                    "features": [
                        "short/mid/long/semantic memory",
                        "project/conversation compartments",
                        "auto summarization",
                        "fact/event stores",
                        "semantic vector recall",
                        "backup + integrity",
                        "encryption-ready",
                    ],
                },
            )

    def set_project(self, name: str) -> None:
        """Switch to a project context"""
        if self.active_project:
            self._save_project_memory()

        self.active_project = name
        pdir = Path(self.base) / "projects" / name
        (pdir / "conversations").mkdir(parents=True, exist_ok=True)
        (pdir / "semantic").mkdir(parents=True, exist_ok=True)
        (pdir / "events").mkdir(parents=True, exist_ok=True)

        self._ensure_project_file(self.project_file(), {"facts": {}, "summary": ""})
        self._load_project_memory()
        self.start_conversation()

        print(f"[Memory Fabric 2.0] Project set: {name}")

    def start_conversation(self) -> str:
        """Start a new conversation session"""
        cid = (
            "conv_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
        )
        self.active_conversation = cid

        conv_file = self.conversation_file()
        self._save_json(
            conv_file,
            {
                "conversation_id": cid,
                "project": self.active_project,
                "created": str(datetime.datetime.now()),
                "messages": [],
            },
        )

        self.short_term = []
        self.message_count = 0

        print(f"[Memory Fabric 2.0] Conversation started: {cid}")
        return cid

    def save_message(
        self, role: str, content: str, importance: float = 0.5, tags: list[str] | None = None
    ) -> MemoryEntry:
        """Save a message to short-term memory"""
        entry = MemoryEntry(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            content=content,
            role=role,
            timestamp=datetime.datetime.now().isoformat(),
            layer="short",
            importance=importance,
            tags=tags or [],
            metadata={
                "session_id": self.session_id,
                "conversation_id": self.active_conversation,
                "message_number": self.message_count,
            },
            embedding=self.embedder.embed(content),
        )

        self.short_term.append(entry)
        self.message_count += 1

        convo = self._load_json(self.conversation_file())
        convo.setdefault("messages", []).append(self._entry_to_dict(entry))
        self._save_json(self.conversation_file(), convo)

        if len(self.short_term) >= self.SHORT_TERM_THRESHOLD:
            self._compress_short_term()

        return entry

    def remember_fact(self, key: str, value: Any, category: str = "general") -> None:
        """Store a persistent fact"""
        proj = self._load_json(self.project_file())
        proj.setdefault("facts", {})[key] = {
            "value": value,
            "category": category,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self.fact_cache[key] = value
        self._save_json(self.project_file(), proj)

        self.log_event("fact_stored", {"key": key, "category": category})
        print(f"[Memory Fabric 2.0] Fact stored: {key} = {value}")

    def recall_fact(self, key: str) -> Any | None:
        """Recall a stored fact"""
        if key in self.fact_cache:
            return self.fact_cache[key]
        proj = self._load_json(self.project_file())
        fact_data = proj.get("facts", {}).get(key)
        if fact_data:
            self.fact_cache[key] = fact_data["value"]
            return fact_data["value"]
        return None

    def get_all_facts(self) -> dict[str, Any]:
        """Get all stored facts for current project"""
        proj = self._load_json(self.project_file())
        facts = proj.get("facts", {})
        return {k: v["value"] for k, v in facts.items()}

    def _compress_short_term(self) -> None:
        """Compress short-term memory into mid-term summary"""
        if len(self.short_term) < 3:
            return

        messages = [e.content for e in self.short_term]
        summary = self._generate_summary(messages)
        avg_importance = sum(e.importance for e in self.short_term) / len(self.short_term)

        mid_entry = MemoryEntry(
            id=f"mid_{uuid.uuid4().hex[:12]}",
            content=summary,
            role="summary",
            timestamp=datetime.datetime.now().isoformat(),
            layer="mid",
            importance=avg_importance,
            tags=["compressed", "conversation_summary"],
            metadata={
                "source_count": len(self.short_term),
                "session_id": self.session_id,
                "conversation_id": self.active_conversation,
            },
            embedding=self.embedder.embed(summary),
        )

        self.mid_term.append(mid_entry)
        self.short_term = self.short_term[-5:]

        if len(self.mid_term) >= self.MID_TERM_THRESHOLD:
            self._compress_mid_term()

        self._save_project_memory()
        print(f"[Memory Fabric 2.0] Compressed {len(messages)} messages to mid-term")

    def _compress_mid_term(self) -> None:
        """Compress mid-term memory into long-term"""
        if len(self.mid_term) < 3:
            return

        summaries = [e.content for e in self.mid_term]
        long_summary = self._generate_summary(summaries, is_meta=True)
        max_importance = max(e.importance for e in self.mid_term)

        long_entry = MemoryEntry(
            id=f"long_{uuid.uuid4().hex[:12]}",
            content=long_summary,
            role="milestone",
            timestamp=datetime.datetime.now().isoformat(),
            layer="long",
            importance=max_importance,
            tags=["milestone", "project_memory"],
            metadata={"source_count": len(self.mid_term), "project": self.active_project},
            embedding=self.embedder.embed(long_summary),
        )

        self.long_term.append(long_entry)
        self.semantic_memory.append(long_entry)
        self.mid_term = self.mid_term[-5:]

        if len(self.long_term) > self.LONG_TERM_MAX:
            self.long_term = self.long_term[-self.LONG_TERM_MAX :]
        if len(self.semantic_memory) > self.SEMANTIC_MAX:
            self.semantic_memory = self.semantic_memory[-self.SEMANTIC_MAX :]

        self._save_project_memory()
        print("[Memory Fabric 2.0] Promoted to long-term memory")

    def _generate_summary(self, texts: list[str], is_meta: bool = False) -> str:
        """Generate a summary of multiple texts"""
        if not texts:
            return ""

        prefix = "Project milestone: " if is_meta else "Conversation summary: "
        all_text = " ".join(texts)
        words = all_text.split()
        summary_words = words[:100] if len(words) > 100 else words

        return prefix + " ".join(summary_words)

    def build_embeddings(self) -> None:
        """Rebuild embedding index for semantic search"""
        self.embedding_index.clear()
        for idx, entry in enumerate(self.long_term + self.semantic_memory):
            if entry.embedding:
                self.embedding_index[idx] = entry.embedding
        print(f"[Memory Fabric 2.0] Built {len(self.embedding_index)} embeddings")

    def recall_semantic(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """Search semantic memory for relevant entries"""
        query_embedding = self.embedder.embed(query)
        all_entries = self.semantic_memory + self.long_term + self.mid_term

        candidates = []
        for entry in all_entries:
            if entry.embedding:
                score = self.embedder.similarity(query_embedding, entry.embedding)
                candidates.append((score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in candidates[:top_k] if score > 0.1]

    def contextual_recall(self, query: str) -> str:
        """Intelligent recall for conversational use"""
        for key in self.fact_cache:
            if key.lower() in query.lower():
                return f"I remember: {key} = {self.fact_cache[key]}"

        semantic_results = self.recall_semantic(query, top_k=3)
        if semantic_results:
            best = semantic_results[0]
            return f"Based on memory: {best.content[:200]}"

        return ""

    def get_context_summary(self, max_tokens: int = 500) -> str:
        """Get a summary of current context for AI use"""
        parts = []

        if self.fact_cache:
            facts_str = ", ".join([f"{k}={v}" for k, v in list(self.fact_cache.items())[:10]])
            parts.append(f"Facts: {facts_str}")

        recent = self.short_term[-5:] + self.mid_term[-3:]
        if recent:
            conv_parts = [f"{e.role}: {e.content[:80]}" for e in recent]
            parts.append("Recent: " + " | ".join(conv_parts))

        if self.long_term:
            latest = self.long_term[-1]
            parts.append(f"Milestone: {latest.content[:150]}")

        context = "\n".join(parts)
        words = context.split()
        if len(words) > max_tokens:
            context = " ".join(words[:max_tokens]) + "..."

        return context

    def log_event(self, event_type: str, detail: Any = None) -> None:
        """Log a system event"""
        event = {
            "type": event_type,
            "detail": detail,
            "timestamp": datetime.datetime.now().isoformat(),
            "project": self.active_project,
        }
        self.event_log.append(event)

        event_path = Path(self.base) / "global" / "event_log.json"
        events = self._load_json(event_path).get("events", [])
        events.append(event)
        if len(events) > 1000:
            events = events[-1000:]
        self._save_json(event_path, {"events": events})

    def backup(self, backup_dir: str = "backups") -> str:
        """Create a backup of all memory"""
        self._save_project_memory()

        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(backup_dir, f"memory_{timestamp}")

        shutil.make_archive(dst, "zip", self.base)
        backup_path = dst + ".zip"

        self.log_event("backup_created", {"path": backup_path})
        print(f"[Memory Fabric 2.0] Backup created: {backup_path}")
        return backup_path

    def integrity_hash(self) -> dict[str, str]:
        """Compute integrity hashes for all memory files"""
        hmap = {}
        for root, _, files in os.walk(self.base):
            for f in files:
                if f.endswith(".json"):
                    p = os.path.join(root, f)
                    try:
                        with open(p, "rb") as fh:
                            hmap[p] = hashlib.sha256(fh.read()).hexdigest()
                    except Exception as e:
                        hmap[p] = f"ERROR: {e}"
        return hmap

    def get_stats(self) -> dict[str, Any]:
        """Get memory system statistics"""
        return {
            "project": self.active_project,
            "conversation": self.active_conversation,
            "session_id": self.session_id,
            "message_count": self.message_count,
            "short_term_count": len(self.short_term),
            "mid_term_count": len(self.mid_term),
            "long_term_count": len(self.long_term),
            "semantic_count": len(self.semantic_memory),
            "fact_count": len(self.fact_cache),
            "event_count": len(self.event_log),
            "fabric_version": "2.0-enhanced",
        }

    def project_file(self) -> str:
        """Get path to project memory file"""
        return os.path.join(
            self.base, "projects", self.active_project or "default", "project_memory.json"
        )

    def conversation_file(self) -> str:
        """Get path to current conversation file"""
        return os.path.join(
            self.base,
            "projects",
            self.active_project or "default",
            "conversations",
            f"{self.active_conversation or 'default'}.json",
        )

    def _save_project_memory(self) -> None:
        """Save all project memory to disk"""
        if not self.active_project:
            return

        project_path = Path(self.base) / "projects" / self.active_project

        self._save_json(
            project_path / "mid_term_memory.json", [self._entry_to_dict(e) for e in self.mid_term]
        )
        self._save_json(
            project_path / "long_term_memory.json", [self._entry_to_dict(e) for e in self.long_term]
        )
        self._save_json(
            project_path / "semantic" / "embeddings.json",
            [self._entry_to_dict(e) for e in self.semantic_memory],
        )

    def _load_project_memory(self) -> None:
        """Load project memory from disk"""
        if not self.active_project:
            return

        project_path = Path(self.base) / "projects" / self.active_project

        proj = self._load_json(self.project_file())
        facts = proj.get("facts", {})
        self.fact_cache = {k: v["value"] for k, v in facts.items()}

        mid_file = project_path / "mid_term_memory.json"
        if mid_file.exists():
            data = self._load_json(mid_file)
            self.mid_term = [self._dict_to_entry(d) for d in data] if isinstance(data, list) else []

        long_file = project_path / "long_term_memory.json"
        if long_file.exists():
            data = self._load_json(long_file)
            self.long_term = (
                [self._dict_to_entry(d) for d in data] if isinstance(data, list) else []
            )

        semantic_file = project_path / "semantic" / "embeddings.json"
        if semantic_file.exists():
            data = self._load_json(semantic_file)
            self.semantic_memory = (
                [self._dict_to_entry(d) for d in data] if isinstance(data, list) else []
            )

        print(
            f"[Memory Fabric 2.0] Loaded: {len(self.fact_cache)} facts, {len(self.mid_term)} mid, {len(self.long_term)} long"
        )

    def _entry_to_dict(self, entry: MemoryEntry) -> dict[str, Any]:
        """Convert MemoryEntry to dictionary"""
        return asdict(entry)

    def _dict_to_entry(self, d: dict[str, Any]) -> MemoryEntry:
        """Convert dictionary to MemoryEntry"""
        return MemoryEntry(**d)

    def _save_json(self, path, data) -> None:
        """Save JSON data to file"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_json(self, path) -> dict:
        """Load JSON data from file"""
        path = Path(path)
        if not path.exists():
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _ensure_project_file(self, path_str: str, default: dict) -> None:
        """Ensure project file exists with default content"""
        path = Path(path_str)
        if not path.exists():
            self._save_json(path, default)


_memory_instance: AuroraMemoryFabric | None = None


def get_memory_fabric(base: str = "data/memory") -> AuroraMemoryFabric:
    """Get or create the global memory fabric instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = AuroraMemoryFabric(base=base)
    return _memory_instance


if __name__ == "__main__":
    print("=" * 60)
    print("Aurora Memory Fabric v2 - Test Run")
    print("=" * 60)

    am = AuroraMemoryFabric()
    am.set_project("Test")

    am.remember_fact("name", "Kai")
    am.remember_fact("language", "Python")

    am.save_message("user", "Hello Aurora!")
    am.save_message("aurora", "Hello! How can I help?")

    print("\nRecall name:", am.recall_fact("name"))
    print("All facts:", am.get_all_facts())
    print("\nContext:", am.get_context_summary())
    print("\nStats:", am.get_stats())

    print("\n" + "=" * 60)
    print("Memory Fabric v2 test complete!")
