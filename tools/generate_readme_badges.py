#!/usr/bin/env python3
"""
Generate dynamic badges for Aurora-X README from progress.json
"""

import json
import sys
from datetime import datetime


def load_progress_data(filepath="progress.json"):
    """Load progress data from JSON file"""
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def calculate_overall_progress(tasks):
    """Calculate overall progress percentage from tasks"""
    if not tasks:
        return 0

    total_progress = 0
    for task in tasks:
        # Extract percentage from percent field (e.g., "100%" -> 100)
        percent_str = task.get('percent', '0%').rstrip('%')
        try:
            percent = float(percent_str)
            total_progress += percent
        except ValueError:
            # If can't parse, assume 0
            pass

    return round(total_progress / len(tasks))


def get_active_task_ids(progress_data):
    """Get list of active task IDs"""
    # Use the 'active' field if available
    if 'active' in progress_data:
        return progress_data['active']

    # Otherwise, find tasks with in-progress or in-development status
    active_ids = []
    for task in progress_data.get('tasks', []):
        status = task.get('status', '').lower()
        if 'in-progress' in status or 'in-development' in status:
            active_ids.append(task['id'])

    return active_ids


def get_badge_color(percentage):
    """Determine badge color based on percentage"""
    if percentage >= 90:
        return 'brightgreen'
    elif percentage >= 70:
        return 'green'
    elif percentage >= 50:
        return 'yellowgreen'
    elif percentage >= 30:
        return 'yellow'
    elif percentage >= 10:
        return 'orange'
    else:
        return 'red'


def format_date_for_badge(date_str):
    """Format date string for badge display"""
    try:
        # Parse UTC date from progress.json
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Format as YYYY--MM--DD (double dash for shields.io)
        return dt.strftime('%Y--%m--%d')
    except (ValueError, AttributeError):
        # Fallback to current date if parsing fails
        return datetime.now().strftime('%Y--%m--%d')


def generate_badges(progress_data):
    """Generate shields.io badge markdown"""
    badges = []

    # Calculate overall progress
    tasks = progress_data.get('tasks', [])
    overall_progress = calculate_overall_progress(tasks)
    progress_color = get_badge_color(overall_progress)

    # Overall Progress Badge
    progress_badge = f"![Progress](https://img.shields.io/badge/Progress-{overall_progress}%25-{progress_color})"
    badges.append(progress_badge)

    # Active Tasks Badge
    active_tasks = get_active_task_ids(progress_data)
    if active_tasks:
        # Join task IDs with commas, escape for URL
        active_str = ','.join(active_tasks)
        active_badge = f"![Active Tasks](https://img.shields.io/badge/Active-{active_str}-blue)"
    else:
        active_badge = "![Active Tasks](https://img.shields.io/badge/Active-None-lightgrey)"
    badges.append(active_badge)

    # Last Updated Badge
    updated_date = progress_data.get('updated_utc', '')
    if updated_date:
        formatted_date = format_date_for_badge(updated_date)
        updated_badge = f"![Last Updated](https://img.shields.io/badge/Updated-{formatted_date}-lightgrey)"
    else:
        # Use current date as fallback
        formatted_date = datetime.now().strftime('%Y--%m--%d')
        updated_badge = f"![Last Updated](https://img.shields.io/badge/Updated-{formatted_date}-lightgrey)"
    badges.append(updated_badge)

    # Task Status Counts
    complete_count = sum(1 for t in tasks if 'complete' in t.get('status', '').lower())
    in_progress_count = sum(1 for t in tasks if 'in-progress' in t.get('status', '').lower())
    in_dev_count = sum(1 for t in tasks if 'in-development' in t.get('status', '').lower())

    # Tasks Status Badge
    status_badge = f"![Tasks](https://img.shields.io/badge/Tasks-✅{complete_count}_🚀{in_progress_count}_🔧{in_dev_count}-informational)"
    badges.append(status_badge)

    return badges


def main():
    """Main function"""
    # Load progress data
    progress_data = load_progress_data()

    # Generate badges
    badges = generate_badges(progress_data)

    # Output badge markdown
    print("<!-- BADGES-START -->")
    print(" ".join(badges))
    print("<!-- BADGES-END -->")

    # Also output individual badges for potential separate use
    print("\n<!-- Individual badges for reference:")
    for badge in badges:
        print(f"  {badge}")
    print("-->")


if __name__ == "__main__":
    main()
