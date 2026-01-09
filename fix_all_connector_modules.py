#!/usr/bin/env python3
"""
Fix ALL connector module syntax errors
Properly indents setup() and initialize() methods inside classes
"""

from pathlib import Path
import re

def fix_connector_file(file_path: Path) -> bool:
    """Fix a single connector init file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Fix pattern: def setup(self): at module level needs to be indented
        # And the try block inside needs proper indentation

        # Step 1: Move setup() inside class if it's at module level
        if '\ndef setup(self):' in content and 'class Connector' in content:
            # Replace module-level def setup with class-level
            content = re.sub(
                r'(    return True\n)\n\n(def setup\(self\):)',
                r'\1\n\n    \2',
                content
            )

        # Step 2: Fix indentation of try block inside setup
        # Pattern: "    def setup(self):\n    try:" should be "    def setup(self):\n        try:"
        content = re.sub(
            r'(    def setup\(self\):\n)    (try:)',
            r'\1        \2',
            content
        )

        # Step 3: Fix all lines inside setup() to have proper indentation (8 spaces minimum)
        lines = content.split('\n')
        fixed_lines = []
        in_setup = False
        setup_indent_level = 0

        for i, line in enumerate(lines):
            # Detect start of setup method
            if 'def setup(self):' in line and line.startswith('    '):
                in_setup = True
                setup_indent_level = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue

            # Detect end of setup method (next def or class or end of class)
            if in_setup:
                if line.strip().startswith('def ') and 'setup' not in line:
                    in_setup = False
                elif line.strip().startswith('class '):
                    in_setup = False
                elif line.strip() == '' and i < len(lines) - 1:
                    # Check if next non-empty line is a def or class
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip():
                            if lines[j].strip().startswith('def ') or lines[j].strip().startswith('class '):
                                in_setup = False
                            break

            # Fix indentation inside setup
            if in_setup and line.strip():
                current_indent = len(line) - len(line.lstrip())
                # If line is at class level (4 spaces) but should be in setup (8+ spaces)
                if current_indent == 4 and line.strip() and not line.strip().startswith('def '):
                    # This should be indented more
                    line = '        ' + line.lstrip()
                # If line starts with try/except/if/return/etc and is only 4 spaces indented
                elif current_indent == 4 and any(line.strip().startswith(kw) for kw in ['try:', 'except', 'if ', 'return', 'import', 'cfg =', 'conn =', 'raise', 'self.']):
                    line = '        ' + line.lstrip()
                # If nested inside try (should be 12 spaces)
                elif current_indent == 8 and any(line.strip().startswith(kw) for kw in ['import', 'cfg =', 'conn =', 'if ', 'raise', 'self.', 'return']):
                    # Check if previous line was try: or if:
                    if i > 0 and ('try:' in lines[i-1] or 'if ' in lines[i-1]):
                        line = '            ' + line.lstrip()

            fixed_lines.append(line)

        content = '\n'.join(fixed_lines)

        # Final cleanup: ensure proper indentation pattern
        # Fix: "    def setup(self):\n    try:" -> "    def setup(self):\n        try:"
        content = re.sub(
            r'(    def setup\(self\):\n)(    )(try:)',
            r'\1        \3',
            content
        )

        # Fix nested lines in try block
        content = re.sub(
            r'(        try:\n)(    )(import|cfg|conn|if |raise|self\.|return)',
            r'\1            \3',
            content
        )

        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all connector init files"""
    base_dir = Path("aurora_nexus_v3/generated_modules/connector")

    if not base_dir.exists():
        print(f"Directory not found: {base_dir}")
        return

    fixed_count = 0
    total_count = 0
    errors = []

    for init_file in sorted(base_dir.glob("connector_*_init.py")):
        total_count += 1
        try:
            if fix_connector_file(init_file):
                fixed_count += 1
                # Verify it compiles
                import py_compile
                py_compile.compile(str(init_file), doraise=True)
                print(f"✓ Fixed and verified: {init_file.name}")
        except Exception as e:
            errors.append((init_file.name, str(e)))
            print(f"✗ Error with {init_file.name}: {e}")

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} out of {total_count} connector init files")
    if errors:
        print(f"\nErrors encountered: {len(errors)}")
        for name, err in errors[:5]:
            print(f"  - {name}: {err}")

if __name__ == "__main__":
    main()
