"""
Aurora investigates expert knowledge import issue
"""
import sys
import os

print("[AURORA] Investigating Expert Knowledge import issue...")
print()

print("[AURORA] Testing import from current location...")
try:
    from tools.aurora_expert_knowledge import AuroraExpertKnowledge
    print("[AURORA] ✅ Import successful from root directory")
    expert = AuroraExpertKnowledge()
    print(
        f"[AURORA] ✅ Expert Knowledge loaded: {len(expert.languages)} languages")
except Exception as e:
    print(f"[AURORA] ❌ Import failed: {e}")
    print(f"[AURORA] Error type: {type(e).__name__}")

print()
print("[AURORA] Environment check:")
print(f"  Current directory: {os.getcwd()}")
print(f"  tools/ exists: {os.path.exists('tools')}")
print(
    f"  expert file exists: {os.path.exists('tools/aurora_expert_knowledge.py')}")
print()

print("[AURORA] Python path (first 5):")
for i, p in enumerate(sys.path[:5]):
    print(f"  {i}: {p}")
print()

print("[AURORA] Testing what aurora_core.py sees...")
# Simulate what happens when aurora_core.py runs
try:
    # This is exactly what aurora_core.py does
    from tools.aurora_expert_knowledge import AuroraExpertKnowledge
    print("[AURORA] ✅ aurora_core.py CAN import expert knowledge")
    print("[AURORA] The import works fine!")
except ImportError as e:
    print(f"[AURORA] ❌ aurora_core.py CANNOT import: {e}")
    print("[AURORA] This is the actual problem")
