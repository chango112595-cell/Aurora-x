#!/usr/bin/env python3
"""
Update progress.json and generate MASTER_TASK_LIST.md with validation and history.
"""

import json
import os
import sys
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Import our schema validator
from progress_schema import validate


def clamp(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(value, max_val))


def pct_fmt(value: float) -> str:
    """Format percentage with consistent precision."""
    return f"{clamp(value):.1f}%"


def status(progress: float, status_str: str = None) -> str:
    """
    Return emoji status indicator based on progress or status string.
    
    Args:
        progress: Progress percentage (0-100)
        status_str: Optional status string (pending, in_progress, completed, blocked)
    
    Returns:
        Emoji status indicator
    """
    if status_str:
        status_map = {
            'pending': '⏳',
            'in_progress': '🚀',
            'completed': '✅',
            'blocked': '🚫'
        }
        return status_map.get(status_str, '❓')
    
    # Progress-based status
    if progress >= 100:
        return '✅'
    elif progress >= 75:
        return '🔵'
    elif progress >= 50:
        return '🟡'
    elif progress > 0:
        return '🔴'
    else:
        return '⏳'


def task_pct(task: Dict[str, Any]) -> float:
    """
    Calculate task completion percentage.
    
    If task has subtasks, calculates weighted average.
    Otherwise returns task's progress field.
    
    Args:
        task: Task dictionary
    
    Returns:
        Completion percentage (0-100)
    """
    if 'subtasks' in task and task['subtasks']:
        # Calculate weighted average of subtasks
        total_progress = 0
        count = len(task['subtasks'])
        
        for subtask in task['subtasks']:
            subtask_progress = subtask.get('progress', 0)
            total_progress += clamp(subtask_progress)
        
        return total_progress / count if count > 0 else 0
    
    # Return task's own progress
    return clamp(task.get('progress', 0))


def phase_pct(phase: Dict[str, Any]) -> float:
    """
    Calculate phase completion percentage.
    
    Calculates weighted average of all tasks in phase.
    
    Args:
        phase: Phase dictionary
    
    Returns:
        Completion percentage (0-100)
    """
    if 'tasks' not in phase or not phase['tasks']:
        return 0
    
    total_progress = 0
    count = len(phase['tasks'])
    
    for task in phase['tasks']:
        total_progress += task_pct(task)
    
    return total_progress / count if count > 0 else 0


def overall_pct(data: Dict[str, Any]) -> float:
    """
    Calculate overall project completion percentage.
    
    Calculates weighted average of all phases.
    
    Args:
        data: Full progress.json data
    
    Returns:
        Overall completion percentage (0-100)
    """
    if 'phases' not in data or not data['phases']:
        return 0
    
    total_progress = 0
    count = len(data['phases'])
    
    for phase in data['phases']:
        total_progress += phase_pct(phase)
    
    return total_progress / count if count > 0 else 0


def gating_violations(data: Dict[str, Any]) -> List[str]:
    """
    Check for gating violations (e.g., completed tasks with incomplete dependencies).
    
    Args:
        data: Full progress.json data
    
    Returns:
        List of violation messages
    """
    violations = []
    
    for phase in data.get('phases', []):
        phase_id = phase.get('id', 'Unknown')
        
        # Check if phase is complete but has incomplete tasks
        if phase.get('status') == 'completed':
            for task in phase.get('tasks', []):
                if task.get('progress', 0) < 100:
                    violations.append(
                        f"Phase {phase_id} marked complete but task {task.get('id', 'Unknown')} is at {task.get('progress', 0)}%"
                    )
        
        # Check tasks with subtasks
        for task in phase.get('tasks', []):
            task_id = task.get('id', 'Unknown')
            
            if task.get('status') == 'completed' and 'subtasks' in task:
                for subtask in task['subtasks']:
                    if subtask.get('progress', 0) < 100:
                        violations.append(
                            f"Task {task_id} marked complete but subtask {subtask.get('id', 'Unknown')} is at {subtask.get('progress', 0)}%"
                        )
    
    return violations


def render(data: Dict[str, Any]) -> str:
    """
    Render progress data as markdown.
    
    Args:
        data: Full progress.json data
    
    Returns:
        Markdown string
    """
    lines = []
    
    # Header
    lines.append("# 🎯 Aurora-X Task Tracker - MASTER_TASK_LIST")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    
    # Project Summary
    overall = overall_pct(data)
    lines.append("## 📊 Project Summary")
    lines.append("")
    lines.append(f"**Overall Progress:** {status(overall)} {pct_fmt(overall)}")
    lines.append("")
    
    # Check for violations
    violations = gating_violations(data)
    if violations:
        lines.append("### ⚠️ Gating Violations")
        lines.append("")
        for violation in violations:
            lines.append(f"- {violation}")
        lines.append("")
    
    # Phase Progress Table
    lines.append("## 📈 Phase Progress")
    lines.append("")
    lines.append("| Phase | Name | Status | Progress |")
    lines.append("|-------|------|--------|----------|")
    
    for phase in data.get('phases', []):
        phase_id = phase.get('id', 'Unknown')
        phase_name = phase.get('name', 'Unknown')
        phase_status = phase.get('status', 'unknown')
        phase_progress = phase_pct(phase)
        
        lines.append(f"| {phase_id} | {phase_name} | {status(0, phase_status)} {phase_status} | {pct_fmt(phase_progress)} |")
    
    lines.append("")
    
    # Detailed Phase and Task Breakdown
    lines.append("## 📋 Detailed Breakdown")
    lines.append("")
    
    for phase in data.get('phases', []):
        phase_id = phase.get('id', 'Unknown')
        phase_name = phase.get('name', 'Unknown')
        phase_status = phase.get('status', 'unknown')
        phase_progress = phase_pct(phase)
        
        lines.append(f"### {status(0, phase_status)} {phase_id}: {phase_name} ({pct_fmt(phase_progress)})")
        lines.append("")
        
        if not phase.get('tasks'):
            lines.append("*No tasks defined*")
            lines.append("")
            continue
        
        # Task table
        lines.append("| Task | Name | Status | Progress | Owner | Priority | Tags |")
        lines.append("|------|------|--------|----------|-------|----------|------|")
        
        for task in phase['tasks']:
            task_id = task.get('id', 'Unknown')
            task_name = task.get('name', 'Unknown')
            task_status = task.get('status', 'unknown')
            task_progress = task_pct(task)
            task_owner = task.get('owner', '-')
            task_priority = task.get('priority', '-')
            task_tags = ', '.join(task.get('tags', [])) if task.get('tags') else '-'
            
            lines.append(
                f"| {task_id} | {task_name} | {status(0, task_status)} {task_status} | "
                f"{pct_fmt(task_progress)} | {task_owner} | {task_priority} | {task_tags} |"
            )
        
        lines.append("")
        
        # Subtasks if any
        for task in phase['tasks']:
            if 'subtasks' not in task or not task['subtasks']:
                continue
            
            task_id = task.get('id', 'Unknown')
            task_name = task.get('name', 'Unknown')
            
            lines.append(f"#### 📁 {task_id}: {task_name} - Subtasks")
            lines.append("")
            lines.append("| Subtask | Name | Status | Progress | Tags |")
            lines.append("|---------|------|--------|----------|------|")
            
            for subtask in task['subtasks']:
                subtask_id = subtask.get('id', 'Unknown')
                subtask_name = subtask.get('name', 'Unknown')
                subtask_status = subtask.get('status', 'unknown')
                subtask_progress = subtask.get('progress', 0)
                subtask_tags = ', '.join(subtask.get('tags', [])) if subtask.get('tags') else '-'
                
                lines.append(
                    f"| {subtask_id} | {subtask_name} | {status(0, subtask_status)} {subtask_status} | "
                    f"{pct_fmt(subtask_progress)} | {subtask_tags} |"
                )
            
            lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("")
    lines.append("## 🔄 Update Instructions")
    lines.append("")
    lines.append("1. Edit `progress.json` with your updates")
    lines.append("2. Run `python tools/update_progress.py` to validate and regenerate this file")
    lines.append("3. Check for any validation errors or gating violations")
    lines.append("4. Commit both files together")
    lines.append("")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    # Paths
    progress_file = Path('progress.json')
    output_file = Path('MASTER_TASK_LIST.md')
    lock_file = Path('.progress.lock')
    history_dir = Path('.progress_history')
    
    # Check for lock file
    if lock_file.exists():
        print("Error: Another update is in progress (.progress.lock exists)")
        print("If this is an error, remove the lock file and try again")
        sys.exit(1)
    
    try:
        # Create lock file
        lock_file.touch()
        
        # Check if progress.json exists
        if not progress_file.exists():
            print(f"Error: {progress_file} not found")
            sys.exit(1)
        
        # Load progress data
        with open(progress_file, 'r') as f:
            data = json.load(f)
        
        # Validate schema
        errors = validate(data)
        if errors:
            print("Schema validation errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        
        # Create history directory if needed
        history_dir.mkdir(exist_ok=True)
        
        # Create timestamped snapshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_file = history_dir / f"progress_{timestamp}.json"
        
        with open(snapshot_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Created snapshot: {snapshot_file}")
        
        # Clean up old snapshots (keep last 10)
        snapshots = sorted(history_dir.glob('progress_*.json'))
        if len(snapshots) > 10:
            for old_snapshot in snapshots[:-10]:
                old_snapshot.unlink()
                print(f"Removed old snapshot: {old_snapshot}")
        
        # Generate markdown
        markdown_content = render(data)
        
        # Write output file
        with open(output_file, 'w') as f:
            f.write(markdown_content)
        
        print(f"Generated: {output_file}")
        
        # Report statistics
        overall = overall_pct(data)
        violations = gating_violations(data)
        
        print(f"Overall progress: {pct_fmt(overall)}")
        
        if violations:
            print(f"Warning: {len(violations)} gating violation(s) found")
            for violation in violations:
                print(f"  - {violation}")
        else:
            print("No gating violations found")
        
    finally:
        # Always remove lock file
        if lock_file.exists():
            lock_file.unlink()


if __name__ == '__main__':
    main()