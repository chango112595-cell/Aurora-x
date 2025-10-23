
#!/usr/bin/env python3
"""Real-time workflow monitoring dashboard."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_workflow_runs():
    """Get recent workflow runs via GitHub CLI."""
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "10", "--json", "name,status,conclusion,createdAt"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception:
        return []


def print_dashboard():
    """Print workflow status dashboard."""
    workflows_dir = Path(".github/workflows")
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Aurora-X GitHub Actions Workflow Dashboard          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Count workflows
    all_workflows = list(workflows_dir.glob("*.yml"))
    enabled = [w for w in all_workflows if "DISABLED" not in w.read_text()]
    disabled = [w for w in all_workflows if "DISABLED" in w.read_text()]
    
    print(f"📊 Status: {len(enabled)}/{len(all_workflows)} workflows enabled")
    print()
    
    # Recent runs
    runs = get_workflow_runs()
    if runs:
        print("🏃 Recent Runs:")
        for run in runs[:5]:
            status_icon = {
                "completed": "✅" if run.get("conclusion") == "success" else "❌",
                "in_progress": "🔄",
                "queued": "⏳"
            }.get(run.get("status"), "❓")
            
            print(f"  {status_icon} {run['name'][:40]:40s} - {run.get('conclusion', run.get('status'))}")
    else:
        print("ℹ️  No recent runs found (gh CLI may not be configured)")
    
    print()
    print("📋 Available Workflows:")
    for workflow in sorted(enabled, key=lambda w: w.name):
        print(f"  ✅ {workflow.name}")
    
    if disabled:
        print()
        print("💤 Disabled Workflows:")
        for workflow in sorted(disabled, key=lambda w: w.name):
            print(f"  ❌ {workflow.name}")


if __name__ == "__main__":
    try:
        print_dashboard()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard closed")
        sys.exit(0)
