#!/usr/bin/env python3
"""
Aurora Memory Fabric 2.0 - Enhanced Hybrid Memory System
Multi-layer intelligence memory with automatic compression and semantic recall
"""

import os
import json
import datetime
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional


class AuroraMemoryManager:
    """
    Enhanced Hybrid Memory System
    Supports: short-term, mid-term, long-term, semantic, fact, and event memory
    """

    def __init__(self, base: str = "data/memory"):
        self.base_path = Path(base)
        self.base_path.mkdir(parents=True, exist_ok=True)

        self.current_project = "Aurora-Main"
        self.short_term = []
        self.mid_term = []
        self.long_term = []
        self.facts = {}
        self.events = []
        self.semantic_index = {}

        # Thresholds
        self.short_to_mid_threshold = 10
        self.mid_to_long_threshold = 10

        self._load_memory()

    def set_project(self, project_name: str):
        """Switch to a different project memory compartment"""
        self.current_project = project_name
        self._load_memory()

    def _get_project_path(self) -> Path:
        """Get the current project's memory path"""
        project_path = self.base_path / "projects" / self.current_project
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    def _load_memory(self):
        """Load memory from disk for current project"""
        project_path = self._get_project_path()
        memory_file = project_path / "project_memory.json"

        if memory_file.exists():
            with open(memory_file, 'r') as f:
                data = json.load(f)
                self.short_term = data.get('short_term', [])
                self.mid_term = data.get('mid_term', [])
                self.long_term = data.get('long_term', [])
                self.facts = data.get('facts', {})
                self.events = data.get('events', [])
                self.semantic_index = data.get('semantic_index', {})

    def _save_memory(self):
        """Save memory to disk for current project"""
        project_path = self._get_project_path()
        memory_file = project_path / "project_memory.json"

        data = {
            'short_term': self.short_term,
            'mid_term': self.mid_term,
            'long_term': self.long_term,
            'facts': self.facts,
            'events': self.events,
            'semantic_index': self.semantic_index,
            'last_updated': datetime.datetime.now().isoformat()
        }

        with open(memory_file, 'w') as f:
            json.dump(data, f, indent=2)

    def save_message(self, role: str, content: str):
        """Save a message to short-term memory"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.short_term.append(message)

        # Save conversation to separate file
        self._save_conversation(message)

        # Auto-compress if threshold reached
        if len(self.short_term) >= self.short_to_mid_threshold:
            self.compress_short_term()

        self._save_memory()

    def _save_conversation(self, message: Dict):
        """Save individual conversation message"""
        project_path = self._get_project_path()
        conv_path = project_path / "conversations"
        conv_path.mkdir(exist_ok=True)

        today = datetime.datetime.now().strftime("%Y_%m_%d")
        conv_file = conv_path / \
            f"conv_{today}_{len(list(conv_path.glob('*.json'))) + 1:03d}.json"

        with open(conv_file, 'w') as f:
            json.dump(message, f, indent=2)

    def compress_short_term(self):
        """Compress short-term memory into mid-term summary"""
        if len(self.short_term) < self.short_to_mid_threshold:
            return

        summary = {
            'summary': f"Compressed {len(self.short_term)} messages",
            'message_count': len(self.short_term),
            'first_message': self.short_term[0]['timestamp'],
            'last_message': self.short_term[-1]['timestamp'],
            'compressed_at': datetime.datetime.now().isoformat()
        }

        self.mid_term.append(summary)
        self.short_term = []

        # Check if mid-term needs compression
        if len(self.mid_term) >= self.mid_to_long_threshold:
            self.compress_mid_term()

        self._save_memory()

    def compress_mid_term(self):
        """Compress mid-term memory into long-term summary"""
        if len(self.mid_term) < self.mid_to_long_threshold:
            return

        summary = {
            'summary': f"Compressed {len(self.mid_term)} mid-term summaries",
            'summary_count': len(self.mid_term),
            'first_summary': self.mid_term[0]['first_message'],
            'last_summary': self.mid_term[-1]['last_message'],
            'compressed_at': datetime.datetime.now().isoformat()
        }

        self.long_term.append(summary)
        self.mid_term = []

        # Add to semantic index
        self._index_semantic(summary)

        self._save_memory()

    def remember_fact(self, key: str, value: Any):
        """Store a permanent fact"""
        self.facts[key] = {
            'value': value,
            'stored_at': datetime.datetime.now().isoformat()
        }
        self._save_memory()

    def recall_fact(self, key: str) -> Optional[Any]:
        """Recall a stored fact"""
        if key in self.facts:
            return self.facts[key]['value']
        return None

    def log_event(self, event_type: str, details: Dict):
        """Log a system event"""
        event = {
            'type': event_type,
            'details': details,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.events.append(event)
        self._save_memory()

    def _index_semantic(self, content: Dict):
        """Add content to semantic index"""
        # Simple hash-based indexing (can be enhanced with embeddings)
        content_str = json.dumps(content)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        self.semantic_index[content_hash] = content

    def recall_semantic(self, query: str) -> Optional[str]:
        """Semantic recall based on query"""
        # Simple keyword matching (can be enhanced with vector search)
        query_lower = query.lower()

        for hash_key, content in self.semantic_index.items():
            content_str = json.dumps(content).lower()
            if query_lower in content_str:
                return json.dumps(content, indent=2)

        return None

    def get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        return {
            'project': self.current_project,
            'short_term_count': len(self.short_term),
            'mid_term_count': len(self.mid_term),
            'long_term_count': len(self.long_term),
            'facts_count': len(self.facts),
            'events_count': len(self.events),
            'semantic_index_size': len(self.semantic_index)
        }
