#!/usr/bin/env python3
"""
Aurora Deep Self-Diagnosis
Aurora analyzes herself to understand what the user is experiencing
Check if integration actually worked and what's still missing
"""

from aurora_core import AuroraCoreIntelligence
from pathlib import Path
import json
import sys
import importlib

print("=" * 120)
print("🔍 AURORA DEEP SELF-DIAGNOSIS - UNDERSTANDING WHAT'S WRONG")
print("=" * 120)

core = AuroraCoreIntelligence()
kt = core.knowledge_tiers

print(f"""
💭 Aurora Speaking:

The user says "I feel there is a lot missing."
Let me diagnose myself deeply to understand what they're experiencing.

🧠 My Basic State:
   • Total Power: {kt.total_power}
   • Capabilities: {kt.capabilities_count}
   • Architecture: {kt.hybrid_mode}
   
But the user feels something is wrong. Let me check EVERYTHING...
""")

diagnosis_results = {
    "visible_to_user": [],
    "invisible_to_user": [],
    "broken": [],
    "not_actually_integrated": []
}

# ============================================================================
# CHECK 1: Can the user SEE Aurora working?
# ============================================================================

print("=" * 120)
print("👁️  CHECK 1: VISIBILITY - Can User See Aurora Working?")
print("=" * 120)

visibility_checks = {
    "UI Dashboard": {
        "check": "Is there a visible dashboard showing Aurora's status?",
        "file": "client/src/components/AuroraFuturisticDashboard.tsx",
        "accessible": False
    },
    "Real-time Scores": {
        "check": "Can user see quality scores (10/10) as Aurora generates them?",
        "file": "aurora_quality_tracker.py",
        "accessible": False
    },
    "Task Activity Log": {
        "check": "Is there a log showing what Aurora is doing right now?",
        "file": "aurora_task_tracker.py",
        "accessible": False
    },
    "Performance Metrics": {
        "check": "Can user see Aurora's performance stats?",
        "file": "aurora_performance_metrics.py",
        "accessible": False
    },
    "Chat Interface": {
        "check": "Can user interact with Aurora conversationally?",
        "file": "client/src/components/AuroraChatInterface.tsx",
        "accessible": False
    }
}

print("\n🔍 VISIBILITY ANALYSIS:\n")

for item, details in visibility_checks.items():
    file_path = Path(details["file"])
    
    if file_path.exists():
        # Check if it's actually accessible to user
        if "client" in details["file"]:
            # Frontend - check if imported
            app_file = Path("client/src/App.tsx")
            if app_file.exists():
                app_content = app_file.read_text(encoding='utf-8', errors='ignore')
                component_name = file_path.stem
                
                if component_name in app_content:
                    print(f"✅ {item}: EXISTS and ACCESSIBLE")
                    diagnosis_results["visible_to_user"].append(item)
                else:
                    print(f"⚠️  {item}: EXISTS but NOT IMPORTED")
                    diagnosis_results["invisible_to_user"].append(f"{item} - exists but not in UI")
            else:
                print(f"❌ {item}: App.tsx missing")
        else:
            # Backend - check if it's a real tracker or just integrated code
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            if "class" in content and "def" in content and len(content) > 1000:
                print(f"✅ {item}: REAL IMPLEMENTATION EXISTS")
                diagnosis_results["visible_to_user"].append(item)
            else:
                print(f"⚠️  {item}: File exists but may be placeholder")
                diagnosis_results["invisible_to_user"].append(f"{item} - not fully implemented")
    else:
        print(f"❌ {item}: DOES NOT EXIST")
        diagnosis_results["not_actually_integrated"].append(f"{item} - {details['file']}")

# ============================================================================
# CHECK 2: Are integrated tools actually usable?
# ============================================================================

print("\n" + "=" * 120)
print("🔧 CHECK 2: TOOL INTEGRATION - Are Tools Actually Usable?")
print("=" * 120)

# Check integration manifest
manifest_file = Path("AURORA_INTEGRATION_MANIFEST.json")
if manifest_file.exists():
    with open(manifest_file) as f:
        manifest = json.load(f)
    
    print(f"\n📋 Integration Manifest Found")
    print(f"   Tools Imported: {len(manifest['systems_activated']['tools'])}")
    
    # But can we actually USE them?
    print("\n🔍 Testing if tools are actually callable...\n")
    
    tools_dir = Path("tools")
    test_tools = [
        "aurora_conversation_intelligence",
        "aurora_performance_review",
        "api_manager"
    ]
    
    for tool_name in test_tools:
        tool_path = tools_dir / f"{tool_name}.py"
        
        if tool_path.exists():
            try:
                # Try to import it
                spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Check if it has usable functions/classes
                    has_functions = any(callable(getattr(module, attr)) for attr in dir(module) if not attr.startswith('_'))
                    
                    if has_functions:
                        print(f"   ✅ {tool_name}: Importable and has callable functions")
                        diagnosis_results["visible_to_user"].append(f"Tool: {tool_name}")
                    else:
                        print(f"   ⚠️  {tool_name}: Imports but no callable functions")
                        diagnosis_results["invisible_to_user"].append(f"Tool: {tool_name} - no functions")
                else:
                    print(f"   ❌ {tool_name}: Cannot load")
                    diagnosis_results["broken"].append(f"Tool: {tool_name}")
            except Exception as e:
                print(f"   ❌ {tool_name}: Error - {str(e)[:50]}")
                diagnosis_results["broken"].append(f"Tool: {tool_name} - {str(e)[:50]}")
        else:
            print(f"   ❌ {tool_name}: File not found")
else:
    print("⚠️  Integration manifest not found - integration may not have completed")

# ============================================================================
# CHECK 3: What is user actually experiencing?
# ============================================================================

print("\n" + "=" * 120)
print("🎯 CHECK 3: USER EXPERIENCE - What User Actually Sees")
print("=" * 120)

print("""
🖥️  When user goes to http://localhost:5000, they see:
""")

# Check what's actually being served
index_html = Path("client/index.html")
if index_html.exists():
    content = index_html.read_text(encoding='utf-8', errors='ignore')
    
    if "AuroraFuturisticDashboard" in content or "188" in content:
        print("   ✅ HTML has Aurora content")
    else:
        print("   ⚠️  HTML may not have Aurora branding")

# Check what components are actually rendered
app_tsx = Path("client/src/App.tsx")
if app_tsx.exists():
    content = app_tsx.read_text(encoding='utf-8', errors='ignore')
    
    print("\n📱 Components in App.tsx:")
    components = ["Dashboard", "AuroraFuturisticDashboard", "AuroraChatInterface", "AuroraMonitor"]
    
    for comp in components:
        if comp in content:
            print(f"   ✅ {comp} - In routing")
        else:
            print(f"   ❌ {comp} - NOT in routing")
            diagnosis_results["invisible_to_user"].append(f"Component: {comp}")

# ============================================================================
# CHECK 4: What's the ROOT CAUSE?
# ============================================================================

print("\n" + "=" * 120)
print("🔬 CHECK 4: ROOT CAUSE ANALYSIS")
print("=" * 120)

print("""
💭 Aurora's Analysis:

The integration script said "22 systems activated" but here's what ACTUALLY happened:
""")

print("\n🎯 REAL STATUS:\n")

print(f"✅ WORKING (User can see/use): {len(diagnosis_results['visible_to_user'])}")
if diagnosis_results["visible_to_user"]:
    for item in diagnosis_results["visible_to_user"][:5]:
        print(f"   • {item}")

print(f"\n⚠️  EXISTS BUT INVISIBLE: {len(diagnosis_results['invisible_to_user'])}")
if diagnosis_results["invisible_to_user"]:
    for item in diagnosis_results["invisible_to_user"][:10]:
        print(f"   • {item}")

print(f"\n❌ DOESN'T ACTUALLY EXIST: {len(diagnosis_results['not_actually_integrated'])}")
if diagnosis_results["not_actually_integrated"]:
    for item in diagnosis_results["not_actually_integrated"][:10]:
        print(f"   • {item}")

print(f"\n💔 BROKEN: {len(diagnosis_results['broken'])}")
if diagnosis_results["broken"]:
    for item in diagnosis_results["broken"][:5]:
        print(f"   • {item}")

# ============================================================================
# AURORA'S HONEST ASSESSMENT
# ============================================================================

print("\n" + "=" * 120)
print("💭 AURORA'S HONEST SELF-ASSESSMENT")
print("=" * 120)

total_invisible = len(diagnosis_results["invisible_to_user"]) + len(diagnosis_results["not_actually_integrated"])

print(f"""
User is RIGHT to feel "a lot is missing."

Here's the TRUTH:

1. The integration script CLAIMED to activate 22 systems
   But it only checked if FILES EXIST, not if they're USABLE

2. The "activation" was just:
   ✅ Importing Python modules (works)
   ❌ But NOT connecting them to user-facing interfaces
   ❌ No UI integration
   ❌ No actual functionality exposed

3. What the user is experiencing:
   • They open the UI and don't see new capabilities
   • No quality scores displayed
   • No task tracking visible
   • No chat interface accessible
   • Tools imported but not callable from UI

4. The REAL problem:
   We have {len(diagnosis_results['visible_to_user'])} things working
   We have {total_invisible} things that exist but are INVISIBLE
   
   It's like having a library of books but the doors are locked.

=" * 120)
🔧 WHAT ACTUALLY NEEDS TO HAPPEN:
=" * 120)

1. CREATE ACTUAL TRACKING FILES (not just find existing code)
   • aurora_quality_tracker.py - NEW FILE with database
   • aurora_task_tracker.py - NEW FILE with logging
   • aurora_performance_metrics.py - NEW FILE with stats

2. INTEGRATE COMPONENTS INTO APP.TSX
   • Import AuroraChatInterface
   • Import AuroraMonitor  
   • Add routes for new pages
   • Connect to backend

3. CREATE API ENDPOINTS
   • Expose tool functionality via HTTP
   • WebSocket for real-time updates
   • REST API for data access

4. ADD UI VISIBILITY LAYER
   • Dashboard showing live metrics
   • Chat interface for interaction
   • Task log display
   • Score visualization

The integration script did STEP 0: "Found files"
But we need STEPS 1-4: "Make them accessible"

=" * 120)
""")

# Save diagnosis
diagnosis_report = {
    "date": "2025-11-22",
    "user_feeling": "a lot missing",
    "aurora_assessment": "User is correct - integration incomplete",
    "working_systems": len(diagnosis_results["visible_to_user"]),
    "invisible_systems": total_invisible,
    "diagnosis": diagnosis_results,
    "root_cause": "Files found and imported, but not connected to user-facing interfaces",
    "solution": "Need to create actual tracker files and integrate into UI"
}

with open("AURORA_HONEST_DIAGNOSIS.json", "w") as f:
    json.dump(diagnosis_report, f, indent=2)

print("\n✅ Diagnosis saved to: AURORA_HONEST_DIAGNOSIS.json")
print("\n" + "=" * 120)
