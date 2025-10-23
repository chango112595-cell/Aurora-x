#!/usr/bin/env python3
"""
Export progress.json to CSV format.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any


def flatten_progress_data(data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Flatten the hierarchical progress data into a list of records.

    Args:
        data: Full progress.json data

    Returns:
        List of flattened records for CSV export
    """
    records = []

    for phase in data.get("phases", []):
        # Add phase record
        phase_record = {
            "id": phase.get("id", ""),
            "level": "phase",
            "name": phase.get("name", ""),
            "percent": calculate_phase_progress(phase),
            "owner": "-",
            "priority": "-",
            "tags": "-",
            "status": phase.get("status", "unknown"),
            "due": "-",
        }
        records.append(phase_record)

        # Add task records
        for task in phase.get("tasks", []):
            task_tags = ", ".join(task.get("tags", [])) if task.get("tags") else "-"

            task_record = {
                "id": task.get("id", ""),
                "level": "task",
                "name": task.get("name", ""),
                "percent": calculate_task_progress(task),
                "owner": task.get("owner", "-"),
                "priority": task.get("priority", "-"),
                "tags": task_tags,
                "status": task.get("status", "unknown"),
                "due": task.get("due", "-"),
            }
            records.append(task_record)

            # Add subtask records
            if "subtasks" in task and task["subtasks"]:
                for subtask in task["subtasks"]:
                    subtask_tags = ", ".join(subtask.get("tags", [])) if subtask.get("tags") else "-"

                    subtask_record = {
                        "id": subtask.get("id", ""),
                        "level": "subtask",
                        "name": subtask.get("name", ""),
                        "percent": subtask.get("progress", 0),
                        "owner": subtask.get("owner", "-"),
                        "priority": subtask.get("priority", "-"),
                        "tags": subtask_tags,
                        "status": subtask.get("status", "unknown"),
                        "due": subtask.get("due", "-"),
                    }
                    records.append(subtask_record)

    return records


def calculate_task_progress(task: dict[str, Any]) -> float:
    """
    Calculate task completion percentage.

    Args:
        task: Task dictionary

    Returns:
        Completion percentage (0-100)
    """
    if "subtasks" in task and task["subtasks"]:
        # Calculate average of subtasks
        if not task["subtasks"]:
            return 0
        total = sum(st.get("progress", 0) for st in task["subtasks"])
        return total / len(task["subtasks"])

    return task.get("progress", 0)


def calculate_phase_progress(phase: dict[str, Any]) -> float:
    """
    Calculate phase completion percentage.

    Args:
        phase: Phase dictionary

    Returns:
        Completion percentage (0-100)
    """
    if "tasks" not in phase or not phase["tasks"]:
        return 0

    total = sum(calculate_task_progress(task) for task in phase["tasks"])
    return total / len(phase["tasks"])


def export_to_csv(data: dict[str, Any], output_file=None):
    """
    Export progress data to CSV.

    Args:
        data: Full progress.json data
        output_file: Optional output file path (defaults to stdout)
    """
    records = flatten_progress_data(data)

    # Define CSV columns
    fieldnames = ["id", "level", "name", "percent", "status", "owner", "priority", "tags", "due"]

    # Write CSV
    if output_file:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        print(f"Exported {len(records)} records to {output_file}", file=sys.stderr)
    else:
        # Write to stdout
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
        print(f"Exported {len(records)} records", file=sys.stderr)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Export progress.json to CSV format")
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")
    parser.add_argument("-i", "--input", default="progress.json", help="Input JSON file (default: progress.json)")

    args = parser.parse_args()

    # Check if input file exists
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    # Load progress data
    try:
        with open(input_file) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # Export to CSV
    export_to_csv(data, args.output)


if __name__ == "__main__":
    main()
