#!/usr/bin/env python3
"""
Aurora Memory System - Test Suite
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_memory_persistence():
    """Test memory persistence across sessions"""
    from core.memory_manager import AuroraMemoryManager
    
    print("[*] Testing memory persistence...")
    am = AuroraMemoryManager()
    am.set_project("TestProject")
    am.remember_fact("test_key", "test_value")
    
    result = am.recall_fact("test_key")
    assert result == "test_value", f"Expected 'test_value', got {result}"
    
    print("[✓] Memory persistence test passed")

def test_memory_compression():
    """Test automatic memory compression"""
    from core.memory_manager import AuroraMemoryManager
    
    print("[*] Testing memory compression...")
    am = AuroraMemoryManager()
    am.set_project("CompressionTest")
    
    # Add messages to trigger compression
    for i in range(12):
        am.save_message("user", f"Test message {i}")
    
    stats = am.get_memory_stats()
    assert stats['mid_term_count'] > 0, "Mid-term memory should have compressed summaries"
    
    print("[✓] Memory compression test passed")

def test_semantic_recall():
    """Test semantic memory recall"""
    from core.memory_manager import AuroraMemoryManager
    
    print("[*] Testing semantic recall...")
    am = AuroraMemoryManager()
    am.set_project("SemanticTest")
    
    # Store some facts
    am.remember_fact("user_name", "Kai")
    am.remember_fact("project_focus", "Aurora Memory System")
    
    # Test recall
    name = am.recall_fact("user_name")
    assert name == "Kai", f"Expected 'Kai', got {name}"
    
    print("[✓] Semantic recall test passed")

def test_multi_project():
    """Test multi-project memory isolation"""
    from core.memory_manager import AuroraMemoryManager
    
    print("[*] Testing multi-project isolation...")
    am = AuroraMemoryManager()
    
    # Project 1
    am.set_project("Project1")
    am.remember_fact("project_id", "P1")
    
    # Project 2
    am.set_project("Project2")
    am.remember_fact("project_id", "P2")
    
    # Verify isolation
    p2_id = am.recall_fact("project_id")
    assert p2_id == "P2", f"Expected 'P2', got {p2_id}"
    
    # Switch back
    am.set_project("Project1")
    p1_id = am.recall_fact("project_id")
    assert p1_id == "P1", f"Expected 'P1', got {p1_id}"
    
    print("[✓] Multi-project isolation test passed")

def run_all_tests():
    """Run all memory system tests"""
    print("=" * 60)
    print("AURORA MEMORY SYSTEM - TEST SUITE")
    print("=" * 60)
    
    try:
        test_memory_persistence()
        test_memory_compression()
        test_semantic_recall()
        test_multi_project()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n[✗] Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n[✗] Test error: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
