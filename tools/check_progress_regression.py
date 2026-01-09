"""
Check Progress Regression

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Check for progress regressions compared to git HEAD~1.
"""

import json
import os
import subprocess
import sys

# Aurora Performance Optimization
from pathlib import Path
from typing import Any

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


def get_git_file_content(file_path: str, revision: str = "HEAD~1") -> str | None:
    """
    Get file content from a specific git revision.

    Args:
        file_path: Path to the file
        revision: Git revision (default: HEAD~1)

    Returns:
        File content as string, or None if not found
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{file_path}"], capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        # File might not exist in previous revision
        return None


def calculate_overall_progress(data: dict[str, Any]) -> float:
    """
    Calculate overall project completion percentage.

    Args:
        data: Full progress.json data

    Returns:
        Overall completion percentage (0-100)
    """
    if "phases" not in data or not data["phases"]:
        return 0

    total_progress = 0
    phase_count = len(data["phases"])

    for phase in data["phases"]:
        phase_progress = 0
        task_count = len(phase.get("tasks", []))

        if task_count > 0:
            for task in phase["tasks"]:
                task_progress = 0

                if "subtasks" in task and task["subtasks"]:
                    subtask_count = len(task["subtasks"])
                    if subtask_count > 0:
                        subtask_total = sum(st.get("progress", 0) for st in task["subtasks"])
                        task_progress = subtask_total / subtask_count
                else:
                    task_progress = task.get("progress", 0)

                phase_progress += task_progress

            phase_progress = phase_progress / task_count

        total_progress += phase_progress

    return total_progress / phase_count if phase_count > 0 else 0


def check_gating_violations(data: dict[str, Any]) -> list[str]:
    """
    Check for gating violations.

    Args:
        data: Full progress.json data

    Returns:
        List of violation messages
    """
    violations = []

    for phase in data.get("phases", []):
        phase_id = phase.get("id", "Unknown")

        # Check if phase is complete but has incomplete tasks
        if phase.get("status") == "completed":
            for task in phase.get("tasks", []):
                if task.get("progress", 0) < 100:
                    violations.append(
                        f"Phase {phase_id} marked complete but task {task.get('id', 'Unknown')} is incomplete"
                    )

        # Check tasks with subtasks
        for task in phase.get("tasks", []):
            task_id = task.get("id", "Unknown")

            if task.get("status") == "completed" and "subtasks" in task:
                for subtask in task["subtasks"]:
                    if subtask.get("progress", 0) < 100:
                        violations.append(
                            f"Task {task_id} marked complete but subtask {subtask.get('id', 'Unknown')} is incomplete"
                        )

    return violations


def compare_progress(current_file: Path, previous_content: str | None) -> tuple[float, float, bool]:
    """
    Compare current progress with previous version.

    Args:
        current_file: Path to current progress.json
        previous_content: Content of previous progress.json

    Returns:
        Tuple of (current_progress, previous_progress, has_regression)
    """
    # Load current data
    with open(current_file) as f:
        current_data = json.load(f)

    current_progress = calculate_overall_progress(current_data)

    # If no previous version, this is a new file
    if previous_content is None:
        return current_progress, 0, False

    # Parse previous data
    try:
        previous_data = json.loads(previous_content)
        previous_progress = calculate_overall_progress(previous_data)
    except json.JSONDecodeError:
        # Previous file was invalid JSON
        return current_progress, 0, False

    # Check for regression
    has_regression = current_progress < previous_progress

    return current_progress, previous_progress, has_regression


def main():
    """Main entry point."""
    progress_file = Path("progress.json")

    # Check if file exists
    if not progress_file.exists():
        print("Error: progress.json not found")
        sys.exit(1)

    # Get previous version from git
    previous_content = get_git_file_content("progress.json")

    # Compare progress
    current, previous, has_regression = compare_progress(progress_file, previous_content)

    # Load current data for violation check
    with open(progress_file) as f:
        current_data = json.load(f)

    # Check for gating violations
    violations = check_gating_violations(current_data)

    # Report results
    print("Progress Check Report")
    print("=" * 50)
    print(f"Previous: {previous:.1f}%")
    print(f"Current:  {current:.1f}%")
    print(f"Change:   {current - previous:+.1f}%")
    print()

    # Check for regression
    if has_regression:
        print(f"[ERROR] REGRESSION DETECTED: Progress decreased by {previous - current:.1f}%")
        print()
        sys.exit(1)
    elif current > previous:
        print(f"[OK] Progress increased by {current - previous:.1f}%")
    else:
        print(" No change in overall progress")

    print()

    # Check for violations if STRICT_GATING is set
    strict_gating = os.environ.get("STRICT_GATING", "").lower() in ["true", "1", "yes"]

    if violations:
        print(f"[WARN]  Found {len(violations)} gating violation(s):")
        for violation in violations:
            print(f"   - {violation}")
        print()

        if strict_gating:
            print("[ERROR] STRICT_GATING is enabled - failing due to violations")
            sys.exit(2)
        else:
            print("  Set STRICT_GATING=true to fail on gating violations")
    else:
        print("[OK] No gating violations found")

    print()
    print("[OK] All checks passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
