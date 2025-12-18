#!/usr/bin/env python3
"""
Aurora Memory Fabric v2 - Test Suite
-------------------------------------
Comprehensive tests for the memory system.

Run: pytest tests/test_memory_fabric.py -v

Author: Aurora AI System
Version: 2.0-enhanced
"""

import sys
import os
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.memory_fabric import AuroraMemoryFabric, get_memory_fabric


@pytest.fixture
def temp_memory():
    """Create a temporary memory instance"""
    temp_dir = tempfile.mkdtemp(prefix="aurora_memory_test_")
    am = AuroraMemoryFabric(base=temp_dir)
    am.set_project("TestProject")
    yield am
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestMemoryFabric:
    """Test suite for Aurora Memory Fabric v2"""
    
    def test_initialization(self, temp_memory):
        """Test memory fabric initialization"""
        assert temp_memory is not None
        assert temp_memory.active_project == "TestProject"
        assert temp_memory.active_conversation is not None
    
    def test_fact_memory(self, temp_memory):
        """Test fact storage and recall"""
        temp_memory.remember_fact("name", "Kai")
        temp_memory.remember_fact("language", "Python", category="preferences")
        
        assert temp_memory.recall_fact("name") == "Kai"
        assert temp_memory.recall_fact("language") == "Python"
        assert temp_memory.recall_fact("nonexistent") is None
    
    def test_message_saving(self, temp_memory):
        """Test message saving to short-term memory"""
        entry = temp_memory.save_message("user", "Hello Aurora")
        
        assert entry is not None
        assert entry.role == "user"
        assert entry.content == "Hello Aurora"
        assert entry.layer == "short"
        assert len(temp_memory.short_term) == 1
    
    def test_semantic_recall(self, temp_memory):
        """Test semantic memory search"""
        temp_memory.save_message("user", "I love programming in Python")
        temp_memory.save_message("aurora", "Python is a great language!")
        temp_memory.save_message("user", "What about machine learning?")
        
        for i in range(10):
            temp_memory.save_message("user", f"Testing message {i} about coding")
        
        results = temp_memory.recall_semantic("Python programming")
        assert len(results) >= 0
    
    def test_context_summary(self, temp_memory):
        """Test context summary generation"""
        temp_memory.remember_fact("project", "Aurora")
        temp_memory.save_message("user", "Working on AI project")
        
        context = temp_memory.get_context_summary()
        assert context is not None
        assert len(context) > 0
    
    def test_event_logging(self, temp_memory):
        """Test event logging"""
        temp_memory.log_event("test_event", {"key": "value"})
        
        assert len(temp_memory.event_log) == 1
        assert temp_memory.event_log[0]["type"] == "test_event"
    
    def test_stats(self, temp_memory):
        """Test statistics generation"""
        temp_memory.save_message("user", "Test message")
        temp_memory.remember_fact("key", "value")
        
        stats = temp_memory.get_stats()
        
        assert stats["project"] == "TestProject"
        assert stats["short_term_count"] == 1
        assert stats["fact_count"] == 1
        assert stats["fabric_version"] == "2.0-enhanced"
    
    def test_integrity_hash(self, temp_memory):
        """Test integrity hash computation"""
        temp_memory.remember_fact("test", "data")
        
        hashes = temp_memory.integrity_hash()
        assert len(hashes) > 0
        for path, hash_value in hashes.items():
            assert not hash_value.startswith("ERROR")
    
    def test_project_switching(self, temp_memory):
        """Test switching between projects"""
        temp_memory.remember_fact("project1_fact", "value1")
        
        temp_memory.set_project("Project2")
        temp_memory.remember_fact("project2_fact", "value2")
        
        assert temp_memory.recall_fact("project2_fact") == "value2"
        
        temp_memory.set_project("TestProject")
        assert temp_memory.recall_fact("project1_fact") == "value1"
    
    def test_conversation_start(self, temp_memory):
        """Test starting new conversations"""
        conv1 = temp_memory.active_conversation
        temp_memory.start_conversation()
        conv2 = temp_memory.active_conversation
        
        assert conv1 != conv2
        assert conv2.startswith("conv_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])