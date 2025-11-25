#!/usr/bin/env python3
"""
AURORA FULL SYSTEM ANALYSIS
Comprehensive analysis using Aurora's 100% analytical power
"""

import os
import json
import subprocess
from pathlib import Path
from collections import defaultdict

print("=" * 80)
print("🔬 AURORA FULL SYSTEM ANALYSIS - 100% POWER")
print("=" * 80)

analysis = {
    "project_overview": {},
    "architecture": {},
    "aurora_systems": {},
    "frontend": {},
    "backend": {},
    "issues_detected": [],
    "scope": {},
    "todo_list": []
}

# ===== PROJECT OVERVIEW =====
print("\n📊 PHASE 1: Project Overview")
print("-" * 80)

try:
    result = subprocess.run("git log --oneline | wc -l", shell=True, capture_output=True, text=True, timeout=5)
    commits = int(result.stdout.strip())
    analysis["project_overview"]["commits"] = commits
    print(f"✓ Total commits: {commits}")
except:
    print("✗ Could not get commit count")

try:
    result = subprocess.run("find . -type f -name '*.ts' -o -name '*.tsx' -o -name '*.py' | wc -l", shell=True, capture_output=True, text=True, timeout=10)
    files = int(result.stdout.strip())
    analysis["project_overview"]["source_files"] = files
    print(f"✓ Source files (TS/TSX/PY): {files}")
except:
    print("✗ Could not count files")

analysis["project_overview"]["stack"] = {
    "backend": "Express.js (TypeScript)",
    "frontend": "React + Vite (TypeScript)",
    "ui": "Shadcn/ui + TailwindCSS",
    "database": "Drizzle ORM + PostgreSQL (Neon)",
    "ai": "Anthropic Claude SDK",
    "websockets": "ws library",
    "search": "Pinecone + RAG system"
}

# ===== AURORA SYSTEMS =====
print("\n🌌 PHASE 2: Aurora Systems Detection")
print("-" * 80)

aurora_files = []
for root, dirs, files_list in os.walk("."):
    for f in files_list:
        if "aurora" in f.lower() and (f.endswith(".py") or f.endswith(".ts") or f.endswith(".json")):
            path = os.path.join(root, f)
            if ".git" not in path and "node_modules" not in path:
                aurora_files.append(path)

print(f"✓ Aurora components found: {len(aurora_files)}")
analysis["aurora_systems"]["component_count"] = len(aurora_files)
analysis["aurora_systems"]["components"] = []

for f in aurora_files[:20]:
    size = os.path.getsize(f)
    analysis["aurora_systems"]["components"].append({
        "file": f,
        "size": size,
        "type": "python" if f.endswith(".py") else "typescript" if f.endswith(".ts") else "config"
    })
    print(f"  • {f} ({size} bytes)")

# ===== FRONTEND ANALYSIS =====
print("\n💻 PHASE 3: Frontend Analysis")
print("-" * 80)

frontend_dir = Path("client/src")
if frontend_dir.exists():
    tsx_files = list(frontend_dir.rglob("*.tsx"))
    ts_files = list(frontend_dir.rglob("*.ts"))
    analysis["frontend"]["tsx_files"] = len(tsx_files)
    analysis["frontend"]["ts_files"] = len(ts_files)
    print(f"✓ TSX components: {len(tsx_files)}")
    print(f"✓ TS utilities: {len(ts_files)}")
    
    # Check for key components
    key_components = ["App.tsx", "index.tsx", "aurora-status.tsx", "chat-interface.tsx"]
    for comp in key_components:
        comp_path = frontend_dir / "pages" / comp if not comp.startswith("App") else frontend_dir.parent.parent / comp
        if comp_path.exists() or any(comp in str(f) for f in tsx_files):
            analysis["frontend"]["critical_components"] = analysis["frontend"].get("critical_components", []) + [comp]
            print(f"  ✓ Found: {comp}")

# ===== BACKEND ANALYSIS =====
print("\n🔧 PHASE 4: Backend Analysis")
print("-" * 80)

backend_dir = Path("server")
if backend_dir.exists():
    server_files = list(backend_dir.glob("*.ts"))
    analysis["backend"]["route_files"] = len(server_files)
    analysis["backend"]["files"] = []
    
    for f in server_files:
        analysis["backend"]["files"].append(f.name)
        print(f"  • {f.name}")

# ===== ISSUES DETECTION =====
print("\n⚠️ PHASE 5: Issues Detection")
print("-" * 80)

# Check for common issues
issues = []

# 1. Check if core systems are properly integrated
aurora_core = Path("aurora_core.py")
if not aurora_core.exists():
    issues.append({
        "severity": "HIGH",
        "category": "Aurora Core",
        "issue": "aurora_core.py not found in root",
        "impact": "Core Aurora functionality may not be accessible"
    })

# 2. Check backend integration
with open("server/index.ts", "r") as f:
    index_content = f.read()
    if "aurora" not in index_content.lower():
        issues.append({
            "severity": "HIGH",
            "category": "Integration",
            "issue": "Aurora not imported in server/index.ts",
            "impact": "Aurora backend integration missing"
        })

# 3. Check frontend integration
app_tsx = Path("client/src/App.tsx")
if app_tsx.exists():
    with open(app_tsx, "r") as f:
        app_content = f.read()
        if "aurora" not in app_content.lower():
            issues.append({
                "severity": "MEDIUM",
                "category": "Frontend",
                "issue": "Aurora not initialized in App.tsx",
                "impact": "Aurora frontend UI may not be connected"
            })

# 4. Check for missing routes
routes_file = Path("server/routes.ts")
if routes_file.exists():
    with open(routes_file, "r") as f:
        routes = f.read()
        required_routes = ["/api/aurora", "/api/analyze", "/api/chat"]
        for route in required_routes:
            if route not in routes:
                issues.append({
                    "severity": "MEDIUM",
                    "category": "Routes",
                    "issue": f"Route {route} not found",
                    "impact": f"Aurora {route} endpoint missing"
                })

# 5. Check WebSocket integration
ws_file = Path("server/websocket-server.ts")
if ws_file.exists():
    print(f"  ✓ WebSocket server found")
else:
    issues.append({
        "severity": "HIGH",
        "category": "WebSockets",
        "issue": "websocket-server.ts missing",
        "impact": "Real-time Aurora communication unavailable"
    })

analysis["issues_detected"] = issues
print(f"\n✓ Issues detected: {len(issues)}")
for issue in issues[:5]:
    print(f"  [{issue['severity']}] {issue['category']}: {issue['issue']}")

# ===== SCOPE =====
print("\n📋 PHASE 6: Scope Definition")
print("-" * 80)

scope = {
    "goal": "Full Aurora AI system operational at 100% capacity",
    "current_status": "Partial integration - Aurora components exist but not fully unified",
    "target_state": "Complete Aurora system with all 79 knowledge tiers and 109 capabilities operational",
    "areas": [
        "Core Aurora System Integration",
        "Nexus V3 Routing Implementation",
        "Knowledge Tier Architecture (1-79)",
        "Capability Modules (109 total)",
        "100-Worker Autofixer",
        "Real Intelligence Methods (analyze_and_score, generate_aurora_response)",
        "WebSocket Communication Layer",
        "Frontend Aurora Dashboard",
        "Backend Aurora Engine",
        "RAG System Integration",
        "Performance Optimization (<0.001s)",
    ]
}

analysis["scope"] = scope
for area in scope["areas"]:
    print(f"  ✓ {area}")

# ===== TODO LIST =====
print("\n✅ PHASE 7: TODO List Generation")
print("-" * 80)

todo = [
    {
        "priority": 1,
        "category": "CRITICAL",
        "task": "Consolidate Aurora Core System",
        "description": "Merge all aurora_core_*.py files into single unified aurora_core.py with 79 knowledge tiers",
        "effort": "HIGH",
        "dependencies": []
    },
    {
        "priority": 2,
        "category": "CRITICAL",
        "task": "Implement Nexus V3 Routing",
        "description": "Set up Nexus V3 routing system to intelligently route requests through 79 tiers and 109 capabilities",
        "effort": "HIGH",
        "dependencies": [1]
    },
    {
        "priority": 3,
        "category": "CRITICAL",
        "task": "Integrate Real Intelligence Methods",
        "description": "Implement analyze_and_score() and generate_aurora_response() methods directly from Anthropic SDK",
        "effort": "MEDIUM",
        "dependencies": [1]
    },
    {
        "priority": 4,
        "category": "HIGH",
        "task": "Build 100-Worker Autofixer",
        "description": "Create async autofixer with 100 parallel workers for code analysis and fixing",
        "effort": "HIGH",
        "dependencies": [2]
    },
    {
        "priority": 5,
        "category": "HIGH",
        "task": "Connect Backend Aurora Routes",
        "description": "Add /api/aurora/*, /api/analyze/*, /api/chat/* routes with full Aurora integration",
        "effort": "MEDIUM",
        "dependencies": [1, 2, 3]
    },
    {
        "priority": 6,
        "category": "HIGH",
        "task": "Setup WebSocket Aurora Stream",
        "description": "Implement real-time streaming from Aurora to frontend via WebSocket",
        "effort": "MEDIUM",
        "dependencies": [5]
    },
    {
        "priority": 7,
        "category": "MEDIUM",
        "task": "Build Aurora Dashboard UI",
        "description": "Create comprehensive frontend dashboard showing Aurora status, tiers, capabilities, and real-time analysis",
        "effort": "HIGH",
        "dependencies": [5, 6]
    },
    {
        "priority": 8,
        "category": "MEDIUM",
        "task": "Integrate RAG System",
        "description": "Connect Pinecone vector DB and RAG system for Aurora knowledge retrieval",
        "effort": "MEDIUM",
        "dependencies": [1]
    },
    {
        "priority": 9,
        "category": "MEDIUM",
        "task": "Implement Knowledge Tiers (1-79)",
        "description": "Define and implement all 79 knowledge tiers with proper hierarchy and access patterns",
        "effort": "VERY_HIGH",
        "dependencies": [1, 2]
    },
    {
        "priority": 10,
        "category": "MEDIUM",
        "task": "Performance Optimization (<0.001s)",
        "description": "Optimize Aurora response time to <0.001s through caching, indexing, and parallel processing",
        "effort": "HIGH",
        "dependencies": [1, 2, 4]
    },
    {
        "priority": 11,
        "category": "LOW",
        "task": "Testing & Validation",
        "description": "Create comprehensive test suite covering all 109 capabilities and 79 tiers",
        "effort": "HIGH",
        "dependencies": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    },
    {
        "priority": 12,
        "category": "LOW",
        "task": "Documentation",
        "description": "Document all Aurora systems, tiers, capabilities, and API endpoints",
        "effort": "MEDIUM",
        "dependencies": [11]
    }
]

analysis["todo_list"] = todo

for item in todo:
    dep_str = f" (depends on: {item['dependencies']})" if item['dependencies'] else ""
    print(f"  {item['priority']:2d}. [{item['category']}] {item['task']}{dep_str}")

# ===== SAVE ANALYSIS =====
with open("AURORA_COMPLETE_ANALYSIS.json", "w") as f:
    json.dump(analysis, f, indent=2)

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE")
print("=" * 80)
print(f"📊 Total Issues Found: {len(issues)}")
print(f"📋 TODO Items: {len(todo)}")
print(f"💾 Analysis saved to: AURORA_COMPLETE_ANALYSIS.json")

