#!/usr/bin/env python3
"""
Syntax Validation Script for Aurora-X
Prevents f-string and syntax errors from being committed.

This script:
1. Validates Python syntax for all .py files
2. Checks for common f-string issues
3. Validates TypeScript/JavaScript syntax
4. Can be run as a pre-commit hook
"""

import ast
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).parent.parent


def validate_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Try to parse the AST
        ast.parse(source, filename=str(file_path))
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}: {e.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_fstring_issues(file_path: Path) -> List[str]:
    """Check for common f-string issues"""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines(True)

        # Track f-string depth (can be nested)
        fstring_stack = []  # List of (start_line, quote_type)
        quote_types = ['f"""', "f'''", 'f"', "f'"]

        for i, line in enumerate(lines, 1):
            # Check for f-string start
            for quote_type in quote_types:
                if quote_type in line:
                    # Count occurrences to handle multiple f-strings on one line
                    count = line.count(quote_type)
                    for _ in range(count):
                        fstring_stack.append((i, quote_type))

            # Check for empty {} in f-strings (should be {{}})
            if fstring_stack and '= {}' in line and '{{}}' not in line:
                # Make sure it's not already escaped or in a comment
                if not line.strip().startswith('#') and '{{}}' not in line:
                    # Check if this is actually inside the f-string content
                    # (not in a nested regular string)
                    start_line, quote_type = fstring_stack[-1]
                    issues.append(
                        f"Line {i}: Empty dict literal `{{}}` in f-string should be `{{{{}}}}` "
                        f"(f-string started at line {start_line})"
                    )

            # Check for f-string end
            if fstring_stack:
                quote_type = fstring_stack[-1][1]
                if quote_type == 'f"""' and '"""' in line:
                    # Count closing quotes
                    close_count = line.count('"""')
                    for _ in range(min(close_count, len(fstring_stack))):
                        if fstring_stack and fstring_stack[-1][1] == 'f"""':
                            fstring_stack.pop()
                elif quote_type == "f'''" and "'''" in line:
                    close_count = line.count("'''")
                    for _ in range(min(close_count, len(fstring_stack))):
                        if fstring_stack and fstring_stack[-1][1] == "f'''":
                            fstring_stack.pop()
                elif quote_type == 'f"' and line.rstrip().endswith('"') and not line.rstrip().endswith('\\"'):
                    fstring_stack.pop()
                elif quote_type == "f'" and line.rstrip().endswith("'") and not line.rstrip().endswith("\\'"):
                    fstring_stack.pop()

    except Exception as e:
        issues.append(f"Error checking f-strings: {str(e)}")

    return issues


def validate_typescript_syntax(file_path: Path) -> Tuple[bool, str]:
    """Validate TypeScript/JavaScript file syntax using tsc"""
    try:
        # Try to use tsc if available
        result = subprocess.run(
            ['npx', 'tsc', '--noEmit', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=ROOT
        )

        if result.returncode == 0:
            return True, ""
        else:
            return False, result.stderr
    except FileNotFoundError:
        # tsc not available, skip TypeScript validation
        return True, "TypeScript compiler not available, skipping"
    except subprocess.TimeoutExpired:
        return False, "TypeScript validation timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_file(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    """Validate a single file - returns (is_valid, errors, warnings)"""
    errors = []
    warnings = []

    if file_path.suffix == '.py':
        # Python syntax check (CRITICAL - must pass)
        valid, error = validate_python_syntax(file_path)
        if not valid:
            errors.append(f"Python syntax error: {error}")
            # Don't check f-strings if syntax is invalid
            return False, errors, warnings

        # F-string checks (WARNING - may have false positives)
        fstring_issues = check_fstring_issues(file_path)
        warnings.extend(fstring_issues)

    elif file_path.suffix in ['.ts', '.tsx']:
        # TypeScript syntax check
        valid, error = validate_typescript_syntax(file_path)
        if not valid and "not available" not in error:
            errors.append(f"TypeScript syntax error: {error}")

    return len(errors) == 0, errors, warnings


def main():
    """Main validation function"""
    if len(sys.argv) > 1:
        # Validate specific files
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Validate all Python files in the project
        files = list(ROOT.rglob('*.py'))
        # Exclude virtual environments and cache
        files = [f for f in files if 'venv' not in str(f) and '__pycache__' not in str(f)]

    failed_files = []
    total_errors = 0
    total_warnings = 0

    print(f"[VALIDATION] Checking {len(files)} files...")

    for file_path in files:
        # Skip if file doesn't exist
        if not file_path.exists():
            continue

        valid, errors, warnings = validate_file(file_path)

        if not valid:
            failed_files.append(file_path)
            total_errors += len(errors)
            try:
                rel_path = file_path.relative_to(ROOT)
            except ValueError:
                rel_path = file_path
            print(f"\n[FAILED] {rel_path}")
            for error in errors:
                print(f"   {error}")

        if warnings:
            total_warnings += len(warnings)
            try:
                rel_path = file_path.relative_to(ROOT)
            except ValueError:
                rel_path = file_path
            if valid:  # Only show warnings if no errors
                print(f"\n[WARNING] {rel_path}")
                for warning in warnings[:3]:  # Show first 3 warnings
                    print(f"   {warning}")
                if len(warnings) > 3:
                    print(f"   ... and {len(warnings) - 3} more warnings")

    if failed_files:
        print(f"\n[VALIDATION] [FAILED] {len(failed_files)} files have syntax errors ({total_errors} total)")
        if total_warnings > 0:
            print(f"[WARNING] {total_warnings} potential f-string issues (may be false positives)")
        print("\nTo fix:")
        print("1. Review the syntax errors above")
        print("2. Fix syntax errors")
        print("3. Run validation again: python tools/validate_syntax.py")
        return 1
    else:
        if total_warnings > 0:
            print(f"\n[VALIDATION] [PASSED] All {len(files)} files compile successfully")
            print(f"[WARNING] {total_warnings} potential f-string issues (may be false positives - review if needed)")
            return 0  # Don't fail on warnings, only on actual syntax errors
        else:
            print(f"\n[VALIDATION] [PASSED] All {len(files)} files are valid")
            return 0


if __name__ == '__main__':
    sys.exit(main())
