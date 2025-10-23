#!/usr/bin/env python3
"""
Generate MASTER_TASK_LIST.md from progress.json with the new format.
"""

import json
from datetime import datetime


def status_emoji(status):
    """Convert status to emoji."""
    if status == "complete":
        return "✅"
    elif status == "in-progress":
        return "🚧"
    else:
        return "⬜"


def generate_tasklist():
    """Generate MASTER_TASK_LIST.md from progress.json."""
    # Load progress.json
    with open("progress.json") as f:
        data = json.load(f)

    # Start building the markdown
    lines = []
    lines.append("# Aurora-X Master Task List")
    lines.append(f"\n> Auto-generated from progress.json v{data.get('version', '1.0')}")
    lines.append(f"> Last updated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"> {data.get('automation', '')}\n")

    # Summary statistics
    total_phases = len(data["phases"])
    complete = sum(1 for p in data["phases"] if p.get("overall") == "complete")
    in_progress = sum(1 for p in data["phases"] if p.get("overall") == "in-progress")
    not_started = total_phases - complete - in_progress

    lines.append("## 📊 Overall Progress")
    lines.append(f"- **Completed:** {complete}/{total_phases} phases")
    lines.append(f"- **In Progress:** {in_progress} phases")
    lines.append(f"- **Not Started:** {not_started} phases")
    lines.append("")

    # Phase details
    lines.append("## 📋 Phase Breakdown\n")

    for phase in data["phases"]:
        phase_id = phase.get("id", "Unknown")
        phase_name = phase.get("name", "Unknown")
        overall = phase.get("overall", "not started")
        percent = phase.get("percent", 0)

        # Phase header
        lines.append(f"### {status_emoji(overall)} {phase_id}: {phase_name}")
        lines.append(f"**Status:** {overall.replace('-', ' ').title()} | **Progress:** {percent}%")

        # Notes if present
        if "notes" in phase:
            lines.append("\n**Notes:**")
            for note in phase["notes"]:
                lines.append(f"- {note}")

        # Rule if present
        if "rule" in phase:
            lines.append(f"\n**Rule:** {phase['rule']}")

        # Acceptance criteria if present
        if "acceptance" in phase:
            lines.append("\n**Acceptance Criteria:**")
            for criterion in phase["acceptance"]:
                lines.append(f"- {criterion}")

        # Subtasks if present
        if "subtasks" in phase:
            lines.append("\n**Subtasks:**")
            for subtask in phase["subtasks"]:
                task_id = subtask.get("id", "Unknown")
                task_name = subtask.get("name", "Unknown")
                task_percent = subtask.get("percent", 0)

                # Progress bar
                filled = int(task_percent / 10)
                empty = 10 - filled
                progress_bar = "█" * filled + "░" * empty

                lines.append(f"- `{task_id}` {task_name}: [{progress_bar}] {task_percent}%")

        lines.append("")

    # Key milestones
    lines.append("## 🎯 Key Milestones\n")
    lines.append("1. **T01-T07:** Core Engine & Infrastructure ✅")
    lines.append("2. **T08:** Natural Language → Code Pipeline 🚧")
    lines.append("3. **T09/T09x:** Template Systems & Multi-Language ⬜")
    lines.append("4. **T10-T13:** Automation & Polish ⬜")
    lines.append("5. **T14:** Telemetry (Last) ⬜")
    lines.append("6. **T15:** STEM Mastery ⬜")
    lines.append("7. **T00:** Omni-Code Knowledge ⬜")
    lines.append("")

    # Active work
    lines.append("## 🔥 Currently Active\n")
    for phase in data["phases"]:
        if phase.get("overall") == "in-progress":
            lines.append(f"- **{phase['id']}:** {phase['name']}")
            if "subtasks" in phase:
                for subtask in phase["subtasks"]:
                    if subtask.get("percent", 0) > 0 and subtask.get("percent", 0) < 100:
                        lines.append(f"  - {subtask['name']}: {subtask['percent']}%")
    lines.append("")

    # Write to file
    with open("MASTER_TASK_LIST.md", "w") as f:
        f.write("\n".join(lines))

    print("✅ MASTER_TASK_LIST.md generated successfully!")
    print(f"   - {total_phases} phases tracked")
    print(f"   - {complete} completed, {in_progress} in progress")
    return True


if __name__ == "__main__":
    generate_tasklist()
