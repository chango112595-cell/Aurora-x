#!/usr/bin/env python3
"""
Update README.md with generated badges
"""

import re
import subprocess
import sys
from pathlib import Path


def update_readme_badges():
    """Update README.md with new badges"""
    readme_path = Path('README.md')

    # Generate new badges
    try:
        result = subprocess.run(
            ['python', 'tools/generate_readme_badges.py'],
            capture_output=True,
            text=True,
            check=True
        )
        badge_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error generating badges: {e}", file=sys.stderr)
        return False

    # Extract badge line from output
    badge_lines = []
    in_badge_section = False
    for line in badge_output.split('\n'):
        if '<!-- BADGES-START -->' in line:
            in_badge_section = True
            badge_lines.append(line)
        elif '<!-- BADGES-END -->' in line:
            badge_lines.append(line)
            break
        elif in_badge_section:
            badge_lines.append(line)

    if not badge_lines:
        print("No badges found in generator output", file=sys.stderr)
        return False

    # Check if README exists
    if not readme_path.exists():
        # Create a basic README with badge section
        print("Creating new README.md with badge section")
        readme_content = f"""# Aurora-X Ultra

{''.join(badge_lines)}

_Offline Autonomous Code Synthesis Engine_
"""
        readme_path.write_text(readme_content)
        return True

    # Read current README
    readme_content = readme_path.read_text()

    # Replace badge section
    pattern = r'<!-- BADGES-START -->.*?<!-- BADGES-END -->'
    replacement = '\n'.join(badge_lines)

    updated_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)

    if updated_content == readme_content:
        print("No changes to badges", file=sys.stderr)
        return True

    # Write updated README
    readme_path.write_text(updated_content)
    print("✅ README.md updated with new badges")
    return True


if __name__ == "__main__":
    success = update_readme_badges()
    sys.exit(0 if success else 1)
