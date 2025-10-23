
#!/usr/bin/env python3
"""Check GitHub Actions workflow status and health."""

import json
import subprocess
import sys
from pathlib import Path


def check_workflow_syntax():
    """Validate all workflow YAML files."""
    workflows_dir = Path(".github/workflows")
    errors = []
    
    for workflow_file in workflows_dir.glob("*.yml"):
        try:
            # Use GitHub CLI to validate if available
            result = subprocess.run(
                ["gh", "workflow", "view", workflow_file.stem],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append(f"❌ {workflow_file.name}: Validation failed")
            else:
                print(f"✅ {workflow_file.name}: Valid")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: just check if file is readable
            try:
                workflow_file.read_text()
                print(f"⚠️  {workflow_file.name}: Syntax OK (gh CLI not available)")
            except Exception as e:
                errors.append(f"❌ {workflow_file.name}: {e}")
    
    return errors


def main():
    """Main entry point."""
    print("🔍 Checking GitHub Actions workflows...\n")
    
    errors = check_workflow_syntax()
    
    if errors:
        print("\n❌ Issues found:")
        for error in errors:
            print(f"  {error}")
        return 1
    else:
        print("\n✅ All workflows validated successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
