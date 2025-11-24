#!/usr/bin/env python3
"""Add pylint disable comment to files with redefined-outer-name warnings"""

from pathlib import Path

files_to_fix = [
    "test_chat_router.py",
    "test_complete_router.py",
    "test_timer_app.py",
    "test_lib_factorial.py",
    "test_lib_generic.py",
    "generated_lib_func.py",
    "new_lib_factorial.py",
    "generated_timer_app.py",
    "generated_web_app.py",
    "timer_app.py",
    "diagnostic_server.py",
]

for filename in files_to_fix:
    filepath = Path(filename)
    if not filepath.exists():
        print(f"[WARN]  {filename} not found")
        continue

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Check if already has the disable comment
    if "disable=redefined-outer-name" in content:
        print(f"[+] {filename} already has disable comment")
        continue

    # Add after shebang if present, otherwise at the top
    lines = content.split("\n")
    if lines[0].startswith("#!"):
        lines.insert(1, "# pylint: disable=redefined-outer-name")
    else:
        lines.insert(0, "# pylint: disable=redefined-outer-name")

    new_content = "\n".join(lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] Added disable comment to {filename}")

print("\n[SPARKLE] Done!")
