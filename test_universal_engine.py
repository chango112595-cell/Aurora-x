#!/usr/bin/env python3
"""
Test script for the Universal Code Synthesis Engine
"""

import sys
from pathlib import Path

# Add aurora_x to path
sys.path.insert(0, str(Path(__file__).parent))

from aurora_x.synthesis import synthesize_universal_sync


def test_universal_engine():
    """Test the universal synthesis engine with various prompts"""

    test_prompts = [
        "Create a simple Flask API with user endpoints",
        "Build a React dashboard with charts and data visualization",
        "Create a full-stack application with Flask backend and React frontend for task management",
        "Build a CLI tool for file processing",
        "Create a machine learning model training script",
    ]

    print("=" * 60)
    print("Testing Aurora-X Universal Code Synthesis Engine")
    print("=" * 60)

    for i, prompt in enumerate(test_prompts[:2], 1):  # Test first 2 prompts
        print(f"\n[Test {i}] {prompt}")
        print("-" * 50)

        try:
            result = synthesize_universal_sync(prompt)

            print(f"✅ Status: {result.get('status', 'unknown')}")
            print(f"   Project Type: {result.get('project_type', 'N/A')}")
            print(f"   Files Generated: {len(result.get('files', []))}")

            if result.get("validation"):
                if result["validation"]["is_valid"]:
                    print("   Validation: ✅ Passed")
                else:
                    print(f"   Validation: ⚠️ {len(result['validation']['issues'])} issues")

            print(f"   Run Directory: {result.get('run_dir', 'N/A')}")

            # Check if key files were created
            if result.get("status") == "success":
                run_dir = Path(result["run_dir"])
                if run_dir.exists():
                    print("   ✅ Run directory created")
                    spec_file = run_dir / "spec.json"
                    if spec_file.exists():
                        print("   ✅ spec.json created")
                    zip_file = run_dir / "project.zip"
                    if zip_file.exists():
                        print("   ✅ project.zip created")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_universal_engine()
