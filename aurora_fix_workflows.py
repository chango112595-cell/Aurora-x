#!/usr/bin/env python3
"""Have REAL Aurora fix GitHub workflow validation errors"""
import sys
import time
from pathlib import Path

from aurora_core import AuroraCore

sys.path.insert(0, str(Path(__file__).parent / "tools"))

print("🌟 Activating REAL Aurora to fix workflow errors...\n")
aurora = AuroraCore()

task_message = """
Fix GitHub Actions workflow validation errors:

Files with errors:
1. .github/workflows/aurora-e2e.yml - Missing required input 'cmd' (line 185)
2. .github/workflows/release.yml - Context access might be invalid: PYPI_TOKEN (line 70)

Required fixes:
1. aurora-e2e.yml: Remove or fix the yq action that's missing 'cmd' parameter
2. release.yml: Fix or comment out the PYPI_TOKEN reference to avoid validation error

Execute these fixes autonomously.
"""

print("📋 Task for Aurora:")
print(task_message)

# Create task file for Aurora's autonomous system
task_file = Path(".aurora_tasks") / "fix_workflows.task"
task_file.parent.mkdir(exist_ok=True)

task_file.write_text(
    f"""
Task Type: fix_github_workflows
Priority: high
Created: automated
Details: {task_message}
Status: pending
Files:
- .github/workflows/aurora-e2e.yml
- .github/workflows/release.yml
"""
)

print(f"\n✅ Task created for Aurora at: {task_file}")
print("🚀 Aurora's autonomous monitoring will execute the fix...")
print("\nWaiting for Aurora to process...")

# Give Aurora a moment to detect and process
time.sleep(2)

print("\n✨ The REAL Aurora should now fix the workflow files!")
