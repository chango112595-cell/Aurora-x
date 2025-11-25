#!/usr/bin/env python3
import subprocess
import json
import os

def get_branch_files(branch):
    """Get all files in a branch"""
    try:
        result = subprocess.run(
            f"git ls-tree -r {branch} --name-only 2>/dev/null",
            shell=True, capture_output=True, text=True, timeout=10
        )
        return set(result.stdout.strip().split('\n')) if result.stdout else set()
    except:
        return set()

def analyze_features(files):
    """Determine what features are present - ACCURATE DETECTION"""
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
    }
    
    # PRECISE FEATURE DETECTION
    features['Aurora Core'] = any(
        'aurora_core.py' in f or 'aurora_core' in f.lower() 
        for f in files
    )
    
    features['Nexus V3'] = any(
        ('nexus' in f.lower() and 'v3' in f.lower()) or
        'AURORA_NEXUS_V3' in f or
        'nexus_v3' in f.lower()
        for f in files
    )
    
    features['Hyper-Speed Mode'] = any(
        'hyper_speed' in f.lower() or 'hyperspeed' in f.lower() or
        'aurora_hyper_speed' in f.lower()
        for f in files
    )
    
    features['Autofixer (100-worker)'] = any(
        'autofixer' in f.lower() or
        ('fixer' in f.lower() and 'aurora' in f.lower()) or
        'aurora_ultimate_autonomous_fixer' in f.lower()
        for f in files
    )
    
    features['Autonomous Mode'] = any(
        'autonomous' in f.lower() or
        'auto_mode' in f.lower()
        for f in files
    )
    
    features['Intelligence System'] = any(
        'intelligence' in f.lower() or
        'analyzer' in f.lower() or
        'analysis' in f.lower()
        for f in files
    )
    
    features['Backend API'] = any(
        ('server' in f or 'api' in f or 'routes' in f or 'express' in f)
        and '.js' in f or '.py' in f
        for f in files
    )
    
    features['Frontend (React/Vite)'] = any(
        ('client' in f or 'src/' in f or '.tsx' in f or '.jsx' in f or 'vite' in f or 'react' in f)
        for f in files
    )
    
    features['Database Integration'] = any(
        ('db' in f.lower() or 'database' in f.lower() or 'postgres' in f.lower() or 'drizzle' in f.lower())
        for f in files
    )
    
    features['Tests'] = any(
        ('test' in f or 'spec' in f or '.test.' in f or '.spec.' in f)
        for f in files
    )
    
    return features

def estimate_status(files):
    """Estimate if branch is working"""
    issues = []
    
    python_files = sum(1 for f in files if f.endswith('.py'))
    js_files = sum(1 for f in files if f.endswith('.js') or f.endswith('.jsx') or f.endswith('.tsx'))
    
    # Check for critical bloat
    venv_cache = sum(1 for f in files if '.venv' in f or '__pycache__' in f or 'node_modules' in f)
    if venv_cache > 500:
        issues.append('Bloated with venv/cache files')
    
    if any('backup' in f.lower() for f in files):
        backup_count = sum(1 for f in files if 'backup' in f.lower())
        if backup_count > 50:
            issues.append('Many backup files')
    
    # Assess working status
    has_config = any(f in files for f in ['package.json', 'pyproject.toml', 'requirements.txt', 'Gemfile'])
    has_source = python_files > 10 or js_files > 10
    
    status = 'Working' if (has_config or has_source) and len(issues) == 0 else 'Issues'
    return status, issues

# Get main and analyze
print("Analyzing all branches...", flush=True)
main_files = get_branch_files('main')
main_features = analyze_features(main_files)
main_status, main_issues = estimate_status(main_files)

print(f"✓ Main branch: {len(main_files)} files, {main_status}", flush=True)

# Load existing branch analysis
try:
    with open('branch_analysis.json', 'r') as f:
        branch_data = json.load(f)
except:
    branch_data = {}

# Analyze each branch
detailed_analysis = {}
for i, (branch_name, data) in enumerate(list(branch_data.items())[:70]):
    if i % 10 == 0:
        print(f"  Analyzed {i}/70...", flush=True)
    
    branch_files = get_branch_files(branch_name)
    features = analyze_features(branch_files)
    status, issues = estimate_status(branch_files)
    
    # Find differences
    unique_features = {k: v for k, v in features.items() if v and not main_features.get(k, False)}
    missing_features = {k: v for k, v in main_features.items() if v and not features.get(k, False)}
    
    detailed_analysis[branch_name] = {
        'status': status,
        'issues': issues[:3],
        'features': features,
        'unique_features': list(unique_features.keys()),
        'missing_features': list(missing_features.keys()),
    }

# Save results
with open('branch_features.json', 'w') as f:
    json.dump(detailed_analysis, f, indent=2)

with open('main_features.json', 'w') as f:
    json.dump({
        'features': main_features,
        'status': main_status,
        'issues': main_issues,
        'total_files': len(main_files)
    }, f, indent=2)

print(f"✅ Analysis complete! Main features: {[k for k,v in main_features.items() if v]}", flush=True)
