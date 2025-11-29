#!/usr/bin/env python3
import subprocess
import json
from collections import defaultdict

def run_git(cmd):
    try:
        result = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

# Get all branches
all_branches = run_git("branch -a --format='%(refname:short)'").split('\n')
all_branches = [b for b in all_branches if b and not b.startswith('HEAD')]

main_files = set(run_git("ls-tree -r main --name-only").split('\n'))

branch_data = {}

for branch in all_branches[:70]:  # Limit to first 70
    # Get commit count ahead/behind
    ahead = run_git(f"rev-list --count {branch}..main 2>/dev/null || echo 0")
    behind = run_git(f"rev-list --count main..{branch} 2>/dev/null || echo 0")
    
    # Get file count difference
    try:
        branch_files = set(run_git(f"ls-tree -r {branch} --name-only 2>/dev/null").split('\n'))
        branch_files = {f for f in branch_files if f}
    except:
        branch_files = set()
    
    added = branch_files - main_files
    removed = main_files - branch_files
    
    # Get last commit info
    last_commit = run_git(f"log -1 --format=%s {branch} 2>/dev/null || echo 'N/A'")
    
    branch_data[branch] = {
        'ahead': ahead or '0',
        'behind': behind or '0',
        'added_files': len(added),
        'removed_files': len(removed),
        'total_files': len(branch_files),
        'last_commit': last_commit,
        'added_sample': list(added)[:5],
        'removed_sample': list(removed)[:5]
    }

print(json.dumps(branch_data, indent=2))
