#!/usr/bin/env python3
"""
Aurora Emergency Syntax Fixer
Fixes syntax errors created by over-aggressive perfecter
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

def check_syntax(filepath: str) -> Tuple[bool, str]:
    """Check if file has syntax errors"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return True, ""  # Not a syntax error

def fix_duplicate_imports(content: str) -> str:
    """Fix duplicate 'from' keywords in import statements"""
    # Fix "from datetime from typing" -> "from typing"
    content = re.sub(r'from \w+ from (typing|datetime|concurrent\.futures|asyncio)', r'from \1', content)
    return content

def fix_file_syntax(filepath: str) -> dict:
    """Fix syntax errors in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original = f.read()
        
        is_valid, error = check_syntax(filepath)
        
        if is_valid:
            return {"file": filepath, "status": "ok", "error": None}
        
        # Try fixes
        fixed = fix_duplicate_imports(original)
        
        # Verify fix
        try:
            ast.parse(fixed)
            # Save fixed version
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return {"file": filepath, "status": "fixed", "error": error}
        except:
            return {"file": filepath, "status": "failed", "error": error}
    
    except Exception as e:
        return {"file": filepath, "status": "error", "error": str(e)}

def main():
    """Fix all syntax errors in Python files"""
    
    print("\n" + "="*80)
    print("[AURORA] EMERGENCY SYNTAX FIXER")
    print("="*80)
    print("Scanning for syntax errors created by over-aggressive perfecter...")
    print()
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', '.venv']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Checking {len(python_files)} Python files...\n")
    
    # Check all files
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fix_file_syntax, python_files))
    
    # Summary
    ok_count = sum(1 for r in results if r['status'] == 'ok')
    fixed_count = sum(1 for r in results if r['status'] == 'fixed')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    
    if fixed_count > 0:
        print("[FIXED FILES]")
        for r in results:
            if r['status'] == 'fixed':
                print(f"  ✅ {r['file']}")
        print()
    
    if failed_count > 0:
        print("[FAILED TO FIX]")
        for r in results:
            if r['status'] == 'failed':
                print(f"  ❌ {r['file']}")
                print(f"     Error: {r['error']}")
        print()
    
    print("="*80)
    print(f"Results: {ok_count} OK | {fixed_count} FIXED | {failed_count} FAILED")
    print("="*80)

if __name__ == "__main__":
    main()
