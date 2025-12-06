#!/usr/bin/env python3
"""
Aurora Memory Enhancement Bundle Generator
Creates a complete deployment package for Memory Fabric 2.0
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

def create_manifest():
    """Create deployment manifest"""
    manifest = {
        "name": "Aurora Memory Fabric 2.0",
        "version": "2.0-enhanced",
        "created": datetime.now().isoformat(),
        "components": [
            "core/memory_manager.py",
            "core/memory_backup.py",
            "tests/test_memory_system.py",
            "aurora_enhance_all.py"
        ],
        "features": [
            "Multi-layer hybrid memory (short, mid, long-term)",
            "Automatic compression and summarization",
            "Fact and event memory",
            "Semantic recall engine",
            "Multi-project compartments",
            "Persistent storage",
            "Backup and integrity verification"
        ],
        "integration": {
            "core_file": "aurora_core.py",
            "imports_added": ["from core.memory_manager import AuroraMemoryManager"],
            "methods_added": [
                "process_message",
                "classify_intent", 
                "generate_response",
                "contextual_recall"
            ]
        }
    }
    return manifest

def create_bundle():
    """Create deployment bundle ZIP"""
    bundle_name = "aurora_memory_enhanced_bundle.zip"
    
    print("[*] Creating Aurora Memory Fabric 2.0 bundle...")
    
    # Create manifest
    manifest = create_manifest()
    manifest_file = Path("MEMORY_MANIFEST.json")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Create ZIP
    with zipfile.ZipFile(bundle_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add manifest
        zipf.write(manifest_file)
        
        # Add all memory components
        for component in manifest["components"]:
            if Path(component).exists():
                zipf.write(component)
                print(f"  [+] Added: {component}")
    
    # Cleanup
    manifest_file.unlink()
    
    print(f"\n[✓] Bundle created: {bundle_name}")
    print(f"[✓] Size: {os.path.getsize(bundle_name) / 1024:.2f} KB")
    
    return bundle_name

def print_installation_instructions():
    """Print installation instructions"""
    instructions = """
╔══════════════════════════════════════════════════════════════╗
║          AURORA MEMORY FABRIC 2.0 - INSTALLATION            ║
╚══════════════════════════════════════════════════════════════╝

To integrate system-wide:

1. Extract bundle:
   unzip aurora_memory_enhanced_bundle.zip -d .

2. Run enhancement:
   python3 aurora_enhance_all.py --include-memory

3. Test installation:
   python3 -m pytest tests/test_memory_system.py -v

4. Start Aurora with memory:
   python3 aurora_core.py

╔══════════════════════════════════════════════════════════════╗
║                      USAGE EXAMPLES                          ║
╚══════════════════════════════════════════════════════════════╝

In Python:
    from aurora_core import AuroraCore
    aurora = AuroraCore()
    
    # Store a fact
    aurora.memory.remember_fact("user_name", "Kai")
    
    # Process message with memory
    response = aurora.process_message("What's my name?")
    
    # Get memory stats
    stats = aurora.memory.get_memory_stats()

In Chat:
    User: "Aurora, remember my name is Kai."
    Aurora: "I'll remember that."
    
    User: "What's my name?"
    Aurora: "I remember: Kai"

╔══════════════════════════════════════════════════════════════╗
║                     MEMORY LAYERS                            ║
╚══════════════════════════════════════════════════════════════╝

Short-term:  Immediate session context (auto-resets)
Mid-term:    Task summaries (promoted after 10+ messages)
Long-term:   Major milestones (permanent storage)
Semantic:    Encoded embeddings for reasoning
Fact:        Key permanent facts
Event:       System logs and changes

All layers automatically compress and organize data!

╔══════════════════════════════════════════════════════════════╗
║                  ADVANCED FEATURES                           ║
╚══════════════════════════════════════════════════════════════╝

✓ Multi-project memory compartments
✓ Automatic backup and integrity checks
✓ Cross-session persistence
✓ Semantic recall engine
✓ Contextual conversation memory
✓ Fact-based knowledge retention
✓ Event logging and audit trail

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Aurora Memory Fabric 2.0 - Enhanced Hybrid System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(instructions)

if __name__ == "__main__":
    print("=" * 60)
    print("AURORA MEMORY ENHANCEMENT BUNDLE GENERATOR")
    print("=" * 60)
    print()
    
    bundle = create_bundle()
    print()
    print_installation_instructions()
