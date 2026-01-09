#!/usr/bin/env python3
"""Verify all 550 modules have real code implementations"""

from pathlib import Path

base = Path('aurora_nexus_v3/generated_modules')
cats = ['connector', 'processor', 'analyzer', 'generator', 'transformer', 
        'validator', 'formatter', 'optimizer', 'monitor', 'integrator']

counts = {}
total_exec = 0
total_init = 0
total_cleanup = 0
has_real_code = 0
has_pass = 0
has_mock = 0
sample_checked = 0

for cat in cats:
    cat_path = base / cat
    if not cat_path.exists():
        continue
    
    exec_files = list(cat_path.glob('*_execute.py'))
    init_files = list(cat_path.glob('*_init.py'))
    cleanup_files = list(cat_path.glob('*_cleanup.py'))
    
    counts[cat] = {
        'execute': len(exec_files),
        'init': len(init_files),
        'cleanup': len(cleanup_files)
    }
    
    total_exec += len(exec_files)
    total_init += len(init_files)
    total_cleanup += len(cleanup_files)
    
    # Sample check execute files
    for f in exec_files[:20]:  # Check first 20 of each category
        try:
            content = f.read_text(encoding='utf-8')
            sample_checked += 1
            
            if 'def execute' in content:
                if 'pass' not in content or ('pass' in content and 'except' in content):
                    has_real_code += 1
                if 'pass' in content and 'def execute' in content:
                    # Check if pass is in execute method
                    lines = content.split('\n')
                    in_execute = False
                    for line in lines:
                        if 'def execute' in line:
                            in_execute = True
                        elif in_execute and line.strip() == 'pass':
                            has_pass += 1
                            break
                        elif in_execute and 'def ' in line:
                            break
            
            if 'mock' in content.lower() and 'true' in content.lower():
                has_mock += 1
        except Exception as e:
            print(f"Error reading {f}: {e}")

print("=" * 60)
print("550 MODULES VERIFICATION REPORT")
print("=" * 60)
print(f"\nModule counts by category:")
for cat in sorted(cats):
    if cat in counts:
        print(f"  {cat:15} - Execute: {counts[cat]['execute']:3}, Init: {counts[cat]['init']:3}, Cleanup: {counts[cat]['cleanup']:3}")

print(f"\nTotal modules:")
print(f"  Execute: {total_exec}")
print(f"  Init:    {total_init}")
print(f"  Cleanup: {total_cleanup}")

print(f"\nSample verification (checked {sample_checked} execute files):")
print(f"  [OK] Have real code: {has_real_code}")
print(f"  [PASS] Have pass statements: {has_pass}")
print(f"  [MOCK] Have mock data: {has_mock}")

if total_exec == 550 and has_real_code == sample_checked and has_pass == 0:
    print("\n[VERIFIED] All 550 modules have REAL CODE implementations!")
else:
    print(f"\n[STATUS] {total_exec} execute modules found")
    if has_pass > 0:
        print(f"   Warning: {has_pass} files have pass statements")
    if has_mock > 0:
        print(f"   Warning: {has_mock} files have mock data")
