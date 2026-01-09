#!/usr/bin/env python3
"""
Fix syntax errors in generated modules
Fixes indentation issues where setup() and initialize() are outside classes
"""

from pathlib import Path

def fix_connector_init_file(file_path: Path) -> bool:
    """Fix indentation issues in connector init files"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content

        # Check if file has the issue: setup() defined at module level (not indented)
        if 'def setup(self):' in content and 'class Connector' in content:
            lines = content.split('\n')
            fixed_lines = []
            in_class = False
            setup_found = False

            for i, line in enumerate(lines):
                # Track when we're inside the class
                if line.strip().startswith('class Connector') and ':' in line:
                    in_class = True
                    fixed_lines.append(line)
                    continue

                # If we see def setup(self) at module level (no indentation)
                if line == 'def setup(self):' and not line.startswith('    '):
                    # This should be inside the class
                    fixed_lines.append('    def setup(self):')
                    setup_found = True
                    continue

                # If we see def initialize inside setup (wrong nesting)
                if setup_found and line.strip() == 'def initialize(self):' and not line.startswith('    '):
                    # This should be at class level, not inside setup
                    # Find where setup ends
                    fixed_lines.append('    def initialize(self):')
                    continue

                # If we're inside setup() and see initialize, fix indentation
                if setup_found and 'def initialize' in line and line.startswith('    ') and not line.startswith('        '):
                    # This is incorrectly nested - should be at class level
                    # But we need to close setup first
                    pass

                # Normal line handling
                if line == 'def setup(self):':
                    # Already handled above
                    continue

                fixed_lines.append(line)

            # Simple approach: find the pattern and replace it
            # Pattern: class ends with return True, then blank line, then def setup(self) at module level
            import re

            # Fix: move setup and initialize inside class
            pattern1 = r'(    return True\n)\n\n(def setup\(self\):)'
            if re.search(pattern1, content):
                # Replace with indented version
                content = re.sub(
                    pattern1,
                    r'\1\n\n    \2',
                    content
                )

            # Fix: move initialize out of setup and into class
            pattern2 = r'(raise RuntimeError\(f"connector setup failed: \{exc\}"\) from exc\n)\n\n(    def initialize\(self\):)'
            if re.search(pattern2, content):
                content = re.sub(
                    pattern2,
                    r'\1\n\2',
                    content
                )

            # Also need to fix the indentation of initialize's body
            # If initialize is at wrong indentation level, fix it
            lines = content.split('\n')
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                # If we see def initialize with wrong indentation after setup
                if 'def initialize(self):' in line and i > 0:
                    prev_line = lines[i-1] if i > 0 else ''
                    # If previous line ends setup's except block
                    if 'from exc' in prev_line or 'raise RuntimeError' in prev_line:
                        # This initialize should be at class level (4 spaces)
                        if not line.startswith('    def initialize'):
                            line = '    ' + line.lstrip()
                new_lines.append(line)
                i += 1

            content = '\n'.join(new_lines)

            if content != original:
                file_path.write_text(content, encoding='utf-8')
                return True
        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fix all connector init files"""
    base_dir = Path("aurora_nexus_v3/generated_modules/connector")

    if not base_dir.exists():
        print(f"Directory not found: {base_dir}")
        return

    # Fix files one by one with proper pattern matching
    fixed_count = 0
    total_count = 0

    for init_file in sorted(base_dir.glob("connector_*_init.py"))[:10]:  # Test first 10
        total_count += 1
        content = init_file.read_text(encoding='utf-8')

        # Check if it has the bug: def setup(self) at module level
        if 'def setup(self):' in content and '\ndef setup(self):' in content:
            # Fix it
            import re
            # Move setup inside class
            fixed = re.sub(
                r'(    return True\n)\n\n(def setup\(self\):)',
                r'\1\n\n    \2',
                content
            )
            # Fix initialize indentation if needed
            fixed = re.sub(
                r'(    raise RuntimeError\(f"connector setup failed: \{exc\}"\) from exc\n)\n\n(    def initialize\(self\):)',
                r'\1\n\2',
                fixed
            )

            if fixed != content:
                init_file.write_text(fixed, encoding='utf-8')
                fixed_count += 1
                print(f"Fixed: {init_file.name}")

    print(f"\nFixed {fixed_count} out of {total_count} connector init files (tested first 10)")
    print("Run again without limit to fix all files")

if __name__ == "__main__":
    main()
