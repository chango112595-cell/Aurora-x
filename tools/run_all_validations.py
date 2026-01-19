#!/usr/bin/env python3
"""
Run All Validations - Comprehensive Pre-Commit Check
Runs all validation scripts to ensure code quality before commit.

This script:
1. Validates Python syntax
2. Validates API endpoints
3. Validates service startup
4. Returns non-zero exit code if any validation fails
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_validation(name: str, script: str, args: list[str] | None = None) -> tuple[bool, str]:
    """Run a validation script and return success status"""
    import os
    cmd = [sys.executable, str(ROOT / script)] + (args or [])

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT,
            env=env
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return False, f"Validation timed out after 60 seconds"
    except Exception as e:
        return False, str(e)


def main():
    """Run all validations"""
    import os

    # Set PYTHONPATH
    os.environ["PYTHONPATH"] = str(ROOT)

    print("=" * 80)
    print("AURORA-X PRE-COMMIT VALIDATION")
    print("=" * 80)
    print()

    validations = [
        ("Syntax Validation", "tools/validate_syntax.py", ["aurora_x/synthesis/universal_engine.py"]),
        ("Endpoint Validation", "tools/validate_endpoints.py", []),
        ("Service Startup Validation", "tools/validate_service_startup.py", []),
    ]

    failed = []

    for name, script, args in validations:
        print(f"[{name}] Running...")
        success, output = run_validation(name, script, args)

        if success:
            print(f"[{name}] [PASSED]")
            if output.strip():
                # Show last few lines if there's output
                lines = output.strip().split('\n')
                if len(lines) > 3:
                    print("   " + "\n   ".join(lines[-3:]))
                else:
                    print("   " + "\n   ".join(lines))
        else:
            print(f"[{name}] [FAILED]")
            print("   " + "\n   ".join(output.strip().split('\n')[-5:]))
            failed.append(name)
        print()

    print("=" * 80)
    if failed:
        print(f"[FAILED] VALIDATION FAILED: {len(failed)}/{len(validations)} checks failed")
        print(f"   Failed: {', '.join(failed)}")
        print()
        print("To fix:")
        print("1. Review the errors above")
        print("2. Fix the issues")
        print("3. Run validation again: python tools/run_all_validations.py")
        return 1
    else:
        print(f"[PASSED] ALL VALIDATIONS PASSED: {len(validations)}/{len(validations)} checks passed")
        return 0


if __name__ == '__main__':
    sys.exit(main())
