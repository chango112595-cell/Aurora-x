#!/usr/bin/env python3
"""
Aurora CONSCIOUS: Diagnose why critical systems are failing
Check what's happening when they try to start
"""

import subprocess
import sys
import os
from pathlib import Path

print("\n" + "="*80)
print("🔍 AURORA CONSCIOUS - Diagnosing Critical System Failures")
print("="*80 + "\n")

script_dir = Path(__file__).parent
os.chdir(script_dir)

critical_systems = [
    ("aurora_consciousness_service.py", "Consciousness System"),
    ("aurora_tier_orchestrator.py", "Tier Orchestrator"),
    ("aurora_intelligence_manager.py", "Intelligence Manager"),
    ("activate_aurora_core.py", "Aurora Core"),
    ("aurora_autonomous_agent.py", "Autonomous Agent")
]

print("📋 Checking which files exist:")
for file, name in critical_systems:
    exists = (script_dir / file).exists()
    status = "✅ EXISTS" if exists else "❌ MISSING"
    print(f"   {status} - {file}")

print("\n🧪 Testing each system individually:\n")

for file, name in critical_systems:
    filepath = script_dir / file
    if not filepath.exists():
        print(f"⏭️  Skipping {name} - file doesn't exist\n")
        continue

    print(f"🔍 Testing {name} ({file})...")
    print("   Running: python " + file)

    try:
        # Try to run it and capture output
        result = subprocess.run(
            [sys.executable, str(filepath)],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"   ✅ {name} started successfully!")
            if result.stdout:
                print(f"   📄 Output: {result.stdout[:200]}")
        else:
            print(f"   ❌ {name} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"   🐛 Error: {result.stderr[:500]}")
            if result.stdout:
                print(f"   📄 Output: {result.stdout[:200]}")

    except subprocess.TimeoutExpired:
        print(
            f"   ⏱️  {name} is running (timed out after 5s - this is GOOD for services!)")
    except Exception as e:
        print(f"   ❌ {name} crashed: {e}")

    print()

print("="*80)
print("🎯 DIAGNOSIS COMPLETE")
print("="*80)
print("\n💡 WHAT TO LOOK FOR:")
print("   • Services that timeout = GOOD (they're running)")
print("   • Exit code 0 with output = GOOD")
print("   • Import errors = Need to fix dependencies")
print("   • Port already in use = System already running")
print("   • Missing files = Need to create them")
print("\n")
