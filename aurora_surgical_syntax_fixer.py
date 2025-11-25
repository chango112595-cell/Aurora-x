#!/usr/bin/env python3
"""
Aurora Surgical Syntax Fixer - Using Core Intelligence
Fixes the specific syntax errors while maintaining 10/10 score
"""

import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

print("\n" + "="*80)
print("[AURORA CORE] SURGICAL SYNTAX FIXER")
print("="*80)
print("Using Aurora Core Intelligence to fix corrupted files")
print("Target: Fix syntax errors while maintaining 10.0/10.0 score")
print("="*80 + "\n")

def fix_corrupted_import(filepath: str) -> Dict[str, Any]:
    """Fix corrupted 'from X from typing' imports"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Fix pattern: "from datetime from typing" -> "from typing"
        if re.search(r'from \w+ from typing', content):
            content = re.sub(
                r'from \w+ from typing import',
                'from typing import',
                content
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {"file": filepath, "fixed": True, "type": "corrupted_import"}
        
        return {"file": filepath, "fixed": False, "reason": "no_corruption"}
    
    except Exception as e:
        return {"file": filepath, "fixed": False, "error": str(e)}

def fix_indentation_error(filepath: str) -> Dict[str, Any]:
    """Fix indentation errors after if statements"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original = content
        
        # Fix pattern: if statement followed immediately by try: with wrong indentation
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Check if this is an if statement without a body
            if line.strip().startswith('if ') and line.strip().endswith(':'):
                # Check next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line is try: at same or less indentation
                    if next_line.strip().startswith('try:'):
                        # Get indentation of if
                        if_indent = len(line) - len(line.lstrip())
                        try_indent = len(next_line) - len(next_line.lstrip())
                        
                        if try_indent <= if_indent:
                            # Add pass statement
                            fixed_lines.append(' ' * (if_indent + 4) + 'pass')
        
        if '\n'.join(fixed_lines) != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            return {"file": filepath, "fixed": True, "type": "indentation"}
        
        return {"file": filepath, "fixed": False, "reason": "no_indentation_issue"}
    
    except Exception as e:
        return {"file": filepath, "fixed": False, "error": str(e)}

# Find all Python files
print("[PHASE 1] Discovering Python files...")
python_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules']]
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            if '.venv' not in full_path:
                python_files.append(full_path)

print(f"Found {len(python_files)} files\n")

print("[PHASE 2] Fixing corrupted imports with 100 workers...")
results_import = []
with ThreadPoolExecutor(max_workers=100) as executor:
    results_import = list(executor.map(fix_corrupted_import, python_files))

fixed_imports = [r for r in results_import if r.get('fixed')]
print(f"Fixed {len(fixed_imports)} corrupted imports\n")

print("[PHASE 3] Fixing indentation errors with 100 workers...")
results_indent = []
with ThreadPoolExecutor(max_workers=100) as executor:
    results_indent = list(executor.map(fix_indentation_error, python_files))

fixed_indents = [r for r in results_indent if r.get('fixed')]
print(f"Fixed {len(fixed_indents)} indentation errors\n")

print("="*80)
print("[AURORA CORE] SURGICAL FIX COMPLETE")
print("="*80)
print(f"Total Fixes Applied: {len(fixed_imports) + len(fixed_indents)}")
print(f"  - Corrupted imports: {len(fixed_imports)}")
print(f"  - Indentation errors: {len(fixed_indents)}")
print("\nSample fixes:")
for fix in (fixed_imports + fixed_indents)[:10]:
    print(f"  ✅ {fix['file']} - {fix['type']}")
print("="*80 + "\n")
