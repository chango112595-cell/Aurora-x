#!/usr/bin/env python3
import subprocess
import json
import re
from collections import defaultdict

def get_branch_files(branch):
    """Get all files in a branch"""
    try:
        result = subprocess.run(
            f"git ls-tree -r {branch} --name-only 2>/dev/null",
            shell=True, capture_output=True, text=True, timeout=5
        )
        return set(result.stdout.strip().split('\n')) if result.stdout else set()
    except:
        return set()

def analyze_features(files):
    """Determine what features/systems are present based on files"""
    features = {
        'Aurora Core': False,
        'Nexus V3': False,
        'Hyper-Speed Mode': False,
        'Autofixer (100-worker)': False,
        'Autonomous Mode': False,
        'Intelligence System': False,
        'Backend API': False,
        'Frontend (React/Vite)': False,
        'Database Integration': False,
        'Tests': False,
        'Documentation': False,
    }
    
    features['Aurora Core'] = any('aurora_core' in f for f in files)
    features['Nexus V3'] = any('nexus' in f.lower() and 'v3' in f.lower() for f in files)
    features['Hyper-Speed Mode'] = any('hyper_speed' in f.lower() or 'hyperspeed' in f.lower() for f in files)
    features['Autofixer (100-worker)'] = any('autofixer' in f.lower() or 'fixer' in f.lower() for f in files)
    features['Autonomous Mode'] = any('autonomous' in f.lower() or 'auto' in f.lower() for f in files)
    features['Intelligence System'] = any('intelligence' in f.lower() or 'analyzer' in f.lower() for f in files)
    features['Backend API'] = any('server' in f or 'api' in f or 'routes' in f for f in files)
    features['Frontend (React/Vite)'] = any(('client' in f or 'src/' in f or '.tsx' in f or 'vite' in f) for f in files)
    features['Database Integration'] = any(('db' in f.lower() or 'database' in f.lower() or 'postgres' in f.lower()) for f in files)
    features['Tests'] = any(('test' in f or 'spec' in f) for f in files)
    features['Documentation'] = any(('.md' in f or 'docs' in f) for f in files)
    
    return features

def estimate_status(files):
    """Estimate if branch is working or broken based on file structure"""
    issues = []
    
    # Check for common issues
    if any('.venv' in f or '__pycache__' in f or 'node_modules' in f for f in files):
        if sum(1 for f in files if '.venv' in f or '__pycache__' in f or 'node_modules' in f) > 100:
            issues.append('Virtual env/cache bloat')
    
    if any('backup' in f.lower() or 'old' in f.lower() for f in files):
        issues.append('Contains backups/old files')
    
    has_python = any(f.endswith('.py') for f in files)
    has_config = any(f in files for f in ['package.json', 'pyproject.toml', 'requirements.txt'])
    
    if has_python and not has_config:
        issues.append('Python files but no config')
    
    status = 'Working' if len(issues) == 0 else 'Issues'
    return status, issues

# Get main branch files
main_files = get_branch_files('main')
main_features = analyze_features(main_files)
main_status, main_issues = estimate_status(main_files)

# Load existing branch analysis
try:
    with open('branch_analysis.json', 'r') as f:
        branch_data = json.load(f)
except:
    branch_data = {}

# Analyze each branch
detailed_analysis = {}

for branch_name, data in list(branch_data.items())[:70]:
    branch_files = get_branch_files(branch_name)
    features = analyze_features(branch_files)
    status, issues = estimate_status(branch_files)
    
    # Find feature differences
    unique_features = {k: v for k, v in features.items() if v and not main_features.get(k, False)}
    missing_features = {k: v for k, v in main_features.items() if v and not features.get(k, False)}
    
    detailed_analysis[branch_name] = {
        'status': status,
        'issues': issues[:3],  # Top 3 issues
        'features': features,
        'unique_features': list(unique_features.keys()),
        'missing_features': list(missing_features.keys()),
    }

# Save analysis
with open('branch_features.json', 'w') as f:
    json.dump(detailed_analysis, f, indent=2)

# Save main analysis
with open('main_features.json', 'w') as f:
    json.dump({
        'features': main_features,
        'status': main_status,
        'issues': main_issues,
        'total_files': len(main_files)
    }, f, indent=2)

print(f"✅ Analyzed {len(detailed_analysis)} branches")
print(f"Main branch: {main_status} ({len(main_files)} files)")
