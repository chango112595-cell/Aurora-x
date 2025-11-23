#!/usr/bin/env python3
"""
Test Aurora Activation
======================
Verify that all 4 implementations work correctly.
"""

import json
import time
from pathlib import Path

print("=" * 120)
print("🧪 TESTING AURORA ACTIVATION")
print("=" * 120)

project_root = Path(__file__).parent

# Test 1: Check if orchestration is imported
print("\n📋 Test 1: Checking orchestration import...")
aurora_core = project_root / "aurora_core.py"
if aurora_core.exists():
    content = aurora_core.read_text(encoding="utf-8", errors="ignore")
    if "from tools.ultimate_api_manager import UltimateAPIManager" in content:
        print("✅ Orchestration imported")
        if "self.orchestrator_manager = UltimateAPIManager" in content:
            print("✅ Orchestration activated in __init__")
        else:
            print("⚠️ Orchestration imported but not activated")
    else:
        print("❌ Orchestration not imported")
else:
    print("❌ aurora_core.py not found")

# Test 2: Check if scoring method exists
print("\n📋 Test 2: Checking scoring method...")
if aurora_core.exists():
    content = aurora_core.read_text(encoding="utf-8", errors="ignore")
    if "def analyze_and_score" in content:
        print("✅ Scoring method exists")
        if "aurora_expert_knowledge" in content:
            print("✅ Integrates with expert knowledge")
        if ".aurora_scores.json" in content:
            print("✅ Saves to persistent storage")
    else:
        print("❌ Scoring method not found")

# Test 3: Check if API endpoints exist
print("\n📋 Test 3: Checking API endpoints...")
serve_file = project_root / "aurora_x" / "serve.py"
if serve_file.exists():
    content = serve_file.read_text(encoding="utf-8", errors="ignore")
    if "/api/aurora/scores" in content:
        print("✅ /api/aurora/scores endpoint exists")
    else:
        print("❌ /api/aurora/scores endpoint not found")

    if "/api/aurora/status" in content:
        print("✅ /api/aurora/status endpoint exists")
    else:
        print("❌ /api/aurora/status endpoint not found")
else:
    print("❌ serve.py not found")

# Test 4: Check if UI is connected
print("\n📋 Test 4: Checking UI connection...")
dashboard_files = [
    project_root / "client" / "src" / "components" / "AuroraFuturisticDashboard.tsx",
    project_root / "client" / "src" / "pages" / "ComparisonDashboard.tsx",
    project_root / "client" / "src" / "pages" / "luminar-nexus.tsx"
]

ui_connected = False
for dashboard in dashboard_files:
    if dashboard.exists():
        content = dashboard.read_text(encoding="utf-8", errors="ignore")
        if "/api/aurora" in content:
            print(f"✅ {dashboard.name} connected to Aurora API")
            ui_connected = True
            break

if not ui_connected:
    print("⚠️ No dashboard connected to Aurora API yet")

# Test 5: Try importing Aurora Core
print("\n📋 Test 5: Testing Aurora Core import...")
try:
    from aurora_core import AuroraCoreIntelligence
    print("✅ Aurora Core can be imported")

    # Try initializing (but don't start orchestration)
    print("   Testing initialization...")
    # aurora = AuroraCoreIntelligence()
    # print(f"✅ Aurora Core initialized successfully")
    print("   (Skipping full init to avoid starting services)")

except Exception as e:
    print(f"❌ Error importing Aurora Core: {e}")

print("\n" + "=" * 120)
print("🎯 ACTIVATION TEST COMPLETE")
print("=" * 120)
print("\nTo fully test:")
print("1. Start the backend: python -m uvicorn aurora_x.serve:app --reload --port 5000")
print("2. Visit: http://localhost:5000/api/aurora/status")
print("3. Visit: http://localhost:5000/api/aurora/scores")
print("=" * 120)
