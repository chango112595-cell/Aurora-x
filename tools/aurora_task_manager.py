#!/usr/bin/env python3
"""
Aurora Task Manager - Advanced Task Queue and Completion System
Manages task lifecycle, prevents re-execution of completed tasks, and provides task history
"""

import json
from datetime import datetime
from pathlib import Path


class AuroraTaskManager:
    """
    Advanced task management system for Aurora
    - Tracks task lifecycle (pending -> in_progress -> completed -> archived)
    - Prevents re-execution of completed tasks
    - Maintains task history and statistics
    - Supports task priorities and dependencies
    """

    def __init__(self, knowledge_dir: str = "/workspaces/Aurora-x/.aurora_knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.tasks_file = self.knowledge_dir / "aurora_tasks.json"
        self.completed_tasks_file = self.knowledge_dir / "aurora_completed_tasks.json"
        self.task_history_file = self.knowledge_dir / "aurora_task_history.json"

        # Initialize task storage
        self.tasks = self._load_tasks()
        self.completed_tasks = self._load_completed_tasks()
        self.task_history = self._load_task_history()

    def _load_tasks(self) -> dict:
        """Load pending tasks from file"""
        if self.tasks_file.exists():
            try:
                return json.loads(self.tasks_file.read_text())
            except Exception:
                return {"pending": [], "in_progress": []}
        return {"pending": [], "in_progress": []}

    def _load_completed_tasks(self) -> list:
        """Load completed tasks from file"""
        if self.completed_tasks_file.exists():
            try:
                return json.loads(self.completed_tasks_file.read_text())
            except Exception:
                return []
        return []

    def _load_task_history(self) -> dict:
        """Load task execution history"""
        if self.task_history_file.exists():
            try:
                return json.loads(self.task_history_file.read_text())
            except Exception:
                return {"total_completed": 0, "history": []}
        return {"total_completed": 0, "history": []}

    def _save_tasks(self):
        """Save pending tasks to file"""
        self.tasks_file.write_text(json.dumps(self.tasks, indent=2))

    def _save_completed_tasks(self):
        """Save completed tasks to file"""
        self.completed_tasks_file.write_text(json.dumps(self.completed_tasks, indent=2))

    def _save_task_history(self):
        """Save task history to file"""
        self.task_history_file.write_text(json.dumps(self.task_history, indent=2))

    def get_next_task(self) -> dict | None:
        """
        Get the next pending task that hasn't been completed
        Returns None if no tasks available
        """
        # Check for priority tasks first
        for task in self.tasks["pending"]:
            task_id = task.get("id")

            # Skip if already completed
            if self.is_task_completed(task_id):
                # Remove from pending
                self.tasks["pending"].remove(task)
                self._save_tasks()
                continue

            # Check for flag file
            flag_file = self.knowledge_dir / task.get("flag_file", "")
            if flag_file.exists() and flag_file.suffix == ".flag":
                return task

        # If no tasks in queue, check for new flag files
        return self._scan_for_new_tasks()

    def _scan_for_new_tasks(self) -> dict | None:
        """Scan for new .flag files that aren't in the system yet"""
        for flag_file in self.knowledge_dir.glob("*.flag"):
            task_id = self._generate_task_id(flag_file)

            # Skip if already completed
            if self.is_task_completed(task_id):
                # Archive the old flag file
                self._archive_flag_file(flag_file)
                continue

            # Check if already in pending queue
            if any(t.get("id") == task_id for t in self.tasks["pending"]):
                continue

            # New task found!
            task = self._create_task_from_flag(flag_file)
            return task

        return None

    def _generate_task_id(self, flag_file: Path) -> str:
        """Generate unique task ID from flag file"""
        # Use flag file content hash as ID
        content = flag_file.read_text()
        import hashlib

        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _create_task_from_flag(self, flag_file: Path) -> dict:
        """Create task object from flag file"""
        content = flag_file.read_text()
        task_id = self._generate_task_id(flag_file)

        # Parse flag file content
        task_data = {}
        for line in content.split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                task_data[key.strip()] = value.strip()

        # Determine task type from flag filename
        task_type = "creative"  # Default type
        flag_name = flag_file.name.lower()
        if "request" in flag_name or "autonomous" in flag_name:
            task_type = "autonomous_request"

        task = {
            "id": task_id,
            "type": task_type,
            "flag_file": str(flag_file),
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "data": task_data,
            "attempts": 0,
        }

        # Add to pending queue
        self.tasks["pending"].append(task)
        self._save_tasks()

        return task

    def is_task_completed(self, task_id: str) -> bool:
        """Check if a task has been completed"""
        return any(t.get("id") == task_id for t in self.completed_tasks)

    def mark_task_in_progress(self, task_id: str):
        """Mark task as in progress"""
        # Move from pending to in_progress
        for task in self.tasks["pending"]:
            if task.get("id") == task_id:
                task["status"] = "in_progress"
                task["started_at"] = datetime.now().isoformat()
                task["attempts"] += 1
                self.tasks["in_progress"].append(task)
                self.tasks["pending"].remove(task)
                self._save_tasks()
                break

    def mark_task_completed(self, task_id: str, result: dict | None = None):
        """Mark task as completed and archive it"""
        # Find task in in_progress
        for task in self.tasks["in_progress"]:
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                if result:
                    task["result"] = result

                # Move to completed
                self.completed_tasks.append(task)
                self.tasks["in_progress"].remove(task)

                # Update history
                self.task_history["total_completed"] += 1
                self.task_history["history"].append(
                    {
                        "task_id": task_id,
                        "completed_at": task["completed_at"],
                        "task_name": task.get("data", {}).get("AURORA_CREATIVE_TASK", "unknown"),
                    }
                )

                # Keep only last 100 history entries
                if len(self.task_history["history"]) > 100:
                    self.task_history["history"] = self.task_history["history"][-100:]

                # Save all
                self._save_tasks()
                self._save_completed_tasks()
                self._save_task_history()

                # Archive flag file
                flag_file = self.knowledge_dir / task.get("flag_file", "")
                if flag_file.exists():
                    self._archive_flag_file(flag_file)

                break

    def _archive_flag_file(self, flag_file: Path):
        """Archive a completed flag file"""
        archive_dir = self.knowledge_dir / "completed_tasks"
        archive_dir.mkdir(exist_ok=True)

        # Move to archive with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{flag_file.stem}_{timestamp}.archived"
        archive_path = archive_dir / archive_name

        try:
            flag_file.rename(archive_path)
        except Exception:
            # If rename fails, just delete it
            flag_file.unlink()

    def get_task_statistics(self) -> dict:
        """Get statistics about task execution"""
        return {
            "pending_tasks": len(self.tasks["pending"]),
            "in_progress_tasks": len(self.tasks["in_progress"]),
            "completed_tasks": len(self.completed_tasks),
            "total_completed_all_time": self.task_history["total_completed"],
            "recent_completions": self.task_history["history"][-10:],
        }

    def clear_old_flag_files(self):
        """Clean up old .flag files that are already completed"""
        cleaned = 0
        for flag_file in self.knowledge_dir.glob("*.flag"):
            task_id = self._generate_task_id(flag_file)
            if self.is_task_completed(task_id):
                self._archive_flag_file(flag_file)
                cleaned += 1
        return cleaned


if __name__ == "__main__":
    # Test the task manager
    manager = AuroraTaskManager()
    print("[TARGET] Aurora Task Manager Test")
    print(f"Statistics: {manager.get_task_statistics()}")

    next_task = manager.get_next_task()
    if next_task:
        print(f"\n[EMOJI] Next Task: {next_task['id']}")
        print(f"   Status: {next_task['status']}")
        print(f"   Data: {next_task.get('data', {})}")
    else:
        print("\n[OK] No pending tasks!")
