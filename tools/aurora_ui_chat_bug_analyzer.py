#!/usr/bin/env python3
"""
Aurora UI/Chat Bug Analyzer
Analyzes the UI and chat system for bugs and issues
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def analyze_ui_chat():
    """Analyze UI and chat for bugs"""
    print("\n" + "="*70)
    print("🔍 AURORA UI/CHAT BUG ANALYZER")
    print("="*70 + "\n")

    issues = []

    # Check 1: Corpus database
    print("[SCAN] Checking corpus database...")
    try:
        from aurora_x.corpus.store import CorpusStore
        corpus = CorpusStore()
        entries = corpus.get_all_entries()
        print(f"  ✅ Corpus accessible: {len(entries)} entries")
    except Exception as e:
        issues.append({
            "severity": "ERROR",
            "component": "Corpus Database",
            "issue": f"Cannot access corpus: {str(e)}"
        })
        print(f"  ❌ Corpus error: {str(e)}")

    # Check 2: Chat API routes
    print("\n[SCAN] Checking chat API routes...")
    chat_route = Path("app/api/chat/route.ts")
    if chat_route.exists():
        content = chat_route.read_text()
        if "export async function POST" in content:
            print("  ✅ Chat POST route exists")
        else:
            issues.append({
                "severity": "ERROR",
                "component": "Chat API",
                "issue": "Chat POST route not found"
            })
            print("  ❌ Chat POST route missing")
    else:
        issues.append({
            "severity": "ERROR",
            "component": "Chat API",
            "issue": "Chat route file missing"
        })
        print("  ❌ Chat route file missing")

    # Check 3: Chat page component
    print("\n[SCAN] Checking chat page component...")
    chat_page = Path("app/chat/page.tsx")
    if chat_page.exists():
        content = chat_page.read_text()
        if "useState" in content and "useEffect" in content:
            print("  ✅ Chat component has state management")
        else:
            issues.append({
                "severity": "WARNING",
                "component": "Chat UI",
                "issue": "Chat component may lack proper state management"
            })
            print("  ⚠️  State management may be incomplete")
    else:
        issues.append({
            "severity": "ERROR",
            "component": "Chat UI",
            "issue": "Chat page component missing"
        })
        print("  ❌ Chat page missing")

    # Check 4: Backend chat endpoint
    print("\n[SCAN] Checking backend chat endpoint...")
    serve_file = Path("aurora_x/serve.py")
    if serve_file.exists():
        content = serve_file.read_text()
        if "/api/chat" in content:
            print("  ✅ Backend chat endpoint exists")
        else:
            issues.append({
                "severity": "WARNING",
                "component": "Backend",
                "issue": "Chat endpoint may not be registered"
            })
            print("  ⚠️  Chat endpoint registration unclear")

    # Generate report
    print("\n" + "="*70)
    print("📊 ANALYSIS RESULTS")
    print("="*70)

    if not issues:
        print("\n✅ No issues found! UI/Chat system looks healthy.")
    else:
        print(f"\n❌ Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. [{issue['severity']}] {issue['component']}")
            print(f"   {issue['issue']}\n")

    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "issues_found": len(issues),
        "issues": issues
    }

    report_file = Path("aurora/knowledge/aurora_ui_bug_analysis.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2))

    print(f"📝 Report saved to: {report_file}")
    print()

    return len(issues) == 0

if __name__ == "__main__":
    success = analyze_ui_chat()
    sys.exit(0 if success else 1)