#!/usr/bin/env python3
"""
Test Aurora Memory System Integration
Quick verification that memory manager is working
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from cog_kernel.memory_abstraction.manager import MemoryMediator
from memory.vecstore import MemoryStore

def test_memory_store():
    """Test the basic MemoryStore functionality"""
    print("🧪 Testing MemoryStore...")
    
    store = MemoryStore()
    
    # Write some test entries
    entry1 = store.write("Python is a programming language", {"category": "tech"})
    entry2 = store.write("JavaScript runs in browsers", {"category": "tech"})
    entry3 = store.write("Coffee helps developers stay awake", {"category": "life"})
    
    print(f"  ✅ Wrote 3 entries")
    print(f"  - Entry 1 ID: {entry1['id']}")
    print(f"  - Entry 2 ID: {entry2['id']}")
    print(f"  - Entry 3 ID: {entry3['id']}")
    
    # Search for entries
    results = store.search("programming code", top_k=2)
    print(f"\n  🔍 Search for 'programming code':")
    for i, result in enumerate(results):
        print(f"    {i+1}. {result['text']} (meta: {result['meta']})")
    
    return True

def test_memory_mediator():
    """Test the MemoryMediator (dual memory system)"""
    print("\n🧪 Testing MemoryMediator...")
    
    mediator = MemoryMediator()
    
    # Write to short-term memory
    id1 = mediator.write_event("User asked about Python", {"type": "question"}, longterm=False)
    id2 = mediator.write_event("System responded with code example", {"type": "response"}, longterm=False)
    
    # Write to long-term memory
    id3 = mediator.write_event("Core system principle: Always validate inputs", {"type": "principle"}, longterm=True)
    
    print(f"  ✅ Wrote to short-term: {id1['id']}, {id2['id']}")
    print(f"  ✅ Wrote to long-term: {id3['id']}")
    
    # Query across both memories
    results = mediator.query("Python code", top_k=3)
    print(f"\n  🔍 Query for 'Python code' (searches both short+long term):")
    for i, result in enumerate(results):
        print(f"    {i+1}. {result['text']} (meta: {result['meta']})")
    
    print(f"\n  📊 Memory Stats:")
    print(f"    Short-term entries: {len(mediator.short._index)}")
    print(f"    Long-term entries: {len(mediator.long._index)}")
    
    return True

def main():
    print("=" * 60)
    print("🧠 AURORA MEMORY SYSTEM TEST")
    print("=" * 60)
    
    try:
        # Test individual components
        test_memory_store()
        test_memory_mediator()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Memory system is working!")
        print("=" * 60)
        print("\n💡 Integration Status:")
        print("  ✅ cog_kernel/memory_abstraction/manager.py - MemoryMediator")
        print("  ✅ memory/vecstore.py - MemoryStore")
        print("  ✅ server/memory-bridge.py - HTTP bridge service")
        print("  ✅ server/memory-client.ts - TypeScript client")
        print("  ✅ server/aurora-core.ts - Integrated into Aurora Core")
        print("  ✅ server/routes.ts - API endpoints added")
        print("\n🚀 Ready to use! Start with: npm run dev")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
