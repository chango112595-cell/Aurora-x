#!/usr/bin/env python3
'''
Aurora Branch Merge Helper
===========================
Selectively merge useful features from other branches
'''

import subprocess
from pathlib import Path

def cherry_pick_file(branch, filepath):
    '''Cherry-pick a specific file from a branch'''
    try:
        # Show the file from that branch
        result = subprocess.run(
            ['git', 'show', f'origin/{branch}:{filepath}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Write to current branch
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            Path(filepath).write_text(result.stdout, encoding='utf-8')
            print(f'[OK] Merged {filepath} from {branch}')
            return True
        else:
            print(f'[ERROR] Could not get {filepath} from {branch}')
            return False
    except Exception as e:
        print(f'[ERROR] Error: {e}')
        return False

# Usage example:
# cherry_pick_file('aurora-nexus-v2-integration', 'tools/some_feature.py')
