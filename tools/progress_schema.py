#!/usr/bin/env python3
"""
Lightweight schema validation for progress.json with no external dependencies.
"""

# Required fields for each level
REQUIRED_PHASE_FIELDS = {"id", "name", "status", "progress", "tasks"}
REQUIRED_TASK_FIELDS = {"id", "name", "progress", "status"}
OPTIONAL_TASK_FIELDS = {"owner", "due", "tags", "priority", "subtasks"}
REQUIRED_SUBTASK_FIELDS = {"id", "name", "progress", "status"}
OPTIONAL_SUBTASK_FIELDS = {"owner", "due", "tags", "priority"}


def validate(data):
    """
    Validate progress.json structure and return list of errors.

    Args:
        data: Dict from json.load(progress.json)

    Returns:
        List of error strings (empty if valid)
    """
    errors = []

    # Check top-level structure
    if not isinstance(data, dict):
        errors.append("Root must be a dictionary")
        return errors

    if "phases" not in data:
        errors.append("Missing 'phases' key at root level")
        return errors

    if not isinstance(data["phases"], list):
        errors.append("'phases' must be a list")
        return errors

    # Validate each phase
    for i, phase in enumerate(data["phases"]):
        phase_prefix = f"Phase[{i}]"

        if not isinstance(phase, dict):
            errors.append(f"{phase_prefix}: Must be a dictionary")
            continue

        # Check required phase fields
        missing_fields = REQUIRED_PHASE_FIELDS - set(phase.keys())
        if missing_fields:
            errors.append(
                f"{phase_prefix}: Missing required fields: {', '.join(sorted(missing_fields))}"
            )

        # Validate phase fields
        if "id" in phase and not isinstance(phase["id"], str):
            errors.append(f"{phase_prefix}: 'id' must be a string")

        if "name" in phase and not isinstance(phase["name"], str):
            errors.append(f"{phase_prefix}: 'name' must be a string")

        if "status" in phase:
            valid_statuses = {"pending", "in_progress", "completed", "blocked"}
            if phase["status"] not in valid_statuses:
                errors.append(
                    f"{phase_prefix}: Invalid status '{phase['status']}', must be one of: {', '.join(sorted(valid_statuses))}"
                )

        if "progress" in phase:
            if not isinstance(phase["progress"], (int, float)):
                errors.append(f"{phase_prefix}: 'progress' must be a number")
            elif not 0 <= phase["progress"] <= 100:
                errors.append(f"{phase_prefix}: 'progress' must be between 0 and 100")

        # Validate tasks
        if "tasks" not in phase:
            continue

        if not isinstance(phase["tasks"], list):
            errors.append(f"{phase_prefix}: 'tasks' must be a list")
            continue

        for j, task in enumerate(phase["tasks"]):
            task_prefix = f"{phase_prefix}.Task[{j}]"

            if not isinstance(task, dict):
                errors.append(f"{task_prefix}: Must be a dictionary")
                continue

            # Check required task fields
            missing_fields = REQUIRED_TASK_FIELDS - set(task.keys())
            if missing_fields:
                errors.append(
                    f"{task_prefix}: Missing required fields: {', '.join(sorted(missing_fields))}"
                )

            # Check for unexpected fields
            all_allowed_fields = REQUIRED_TASK_FIELDS | OPTIONAL_TASK_FIELDS
            unexpected_fields = set(task.keys()) - all_allowed_fields
            if unexpected_fields:
                errors.append(
                    f"{task_prefix}: Unexpected fields: {', '.join(sorted(unexpected_fields))}"
                )

            # Validate task fields
            if "id" in task and not isinstance(task["id"], str):
                errors.append(f"{task_prefix}: 'id' must be a string")

            if "name" in task and not isinstance(task["name"], str):
                errors.append(f"{task_prefix}: 'name' must be a string")

            if "status" in task:
                valid_statuses = {"pending", "in_progress", "completed", "blocked"}
                if task["status"] not in valid_statuses:
                    errors.append(
                        f"{task_prefix}: Invalid status '{task['status']}', must be one of: {', '.join(sorted(valid_statuses))}"
                    )

            if "progress" in task:
                if not isinstance(task["progress"], (int, float)):
                    errors.append(f"{task_prefix}: 'progress' must be a number")
                elif not 0 <= task["progress"] <= 100:
                    errors.append(f"{task_prefix}: 'progress' must be between 0 and 100")

            if "tags" in task:
                if not isinstance(task["tags"], list):
                    errors.append(f"{task_prefix}: 'tags' must be a list")
                elif not all(isinstance(tag, str) for tag in task["tags"]):
                    errors.append(f"{task_prefix}: All tags must be strings")

            if "priority" in task:
                valid_priorities = {"low", "medium", "high", "critical"}
                if task["priority"] not in valid_priorities:
                    errors.append(
                        f"{task_prefix}: Invalid priority '{task['priority']}', must be one of: {', '.join(sorted(valid_priorities))}"
                    )

            # Validate subtasks if present
            if "subtasks" not in task:
                continue

            if not isinstance(task["subtasks"], list):
                errors.append(f"{task_prefix}: 'subtasks' must be a list")
                continue

            for k, subtask in enumerate(task["subtasks"]):
                subtask_prefix = f"{task_prefix}.Subtask[{k}]"

                if not isinstance(subtask, dict):
                    errors.append(f"{subtask_prefix}: Must be a dictionary")
                    continue

                # Check required subtask fields
                missing_fields = REQUIRED_SUBTASK_FIELDS - set(subtask.keys())
                if missing_fields:
                    errors.append(
                        f"{subtask_prefix}: Missing required fields: {', '.join(sorted(missing_fields))}"
                    )

                # Check for unexpected fields
                all_allowed_fields = REQUIRED_SUBTASK_FIELDS | OPTIONAL_SUBTASK_FIELDS
                unexpected_fields = set(subtask.keys()) - all_allowed_fields
                if unexpected_fields:
                    errors.append(
                        f"{subtask_prefix}: Unexpected fields: {', '.join(sorted(unexpected_fields))}"
                    )

                # Validate subtask fields
                if "id" in subtask and not isinstance(subtask["id"], str):
                    errors.append(f"{subtask_prefix}: 'id' must be a string")

                if "name" in subtask and not isinstance(subtask["name"], str):
                    errors.append(f"{subtask_prefix}: 'name' must be a string")

                if "status" in subtask:
                    valid_statuses = {"pending", "in_progress", "completed", "blocked"}
                    if subtask["status"] not in valid_statuses:
                        errors.append(
                            f"{subtask_prefix}: Invalid status '{subtask['status']}', must be one of: {', '.join(sorted(valid_statuses))}"
                        )

                if "progress" in subtask:
                    if not isinstance(subtask["progress"], (int, float)):
                        errors.append(f"{subtask_prefix}: 'progress' must be a number")
                    elif not 0 <= subtask["progress"] <= 100:
                        errors.append(f"{subtask_prefix}: 'progress' must be between 0 and 100")

                if "tags" in subtask:
                    if not isinstance(subtask["tags"], list):
                        errors.append(f"{subtask_prefix}: 'tags' must be a list")
                    elif not all(isinstance(tag, str) for tag in subtask["tags"]):
                        errors.append(f"{subtask_prefix}: All tags must be strings")

                if "priority" in subtask:
                    valid_priorities = {"low", "medium", "high", "critical"}
                    if subtask["priority"] not in valid_priorities:
                        errors.append(
                            f"{subtask_prefix}: Invalid priority '{subtask['priority']}', must be one of: {', '.join(sorted(valid_priorities))}"
                        )

    return errors
