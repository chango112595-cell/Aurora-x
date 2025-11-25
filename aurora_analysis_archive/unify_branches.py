#!/usr/bin/env python3
import json
from collections import defaultdict

# Load branch features
with open('branch_features.json', 'r') as f:
    branch_features = json.load(f)

# Create fingerprint for each branch (what makes it unique)
def get_fingerprint(branch_data):
    """Create a fingerprint to identify identical branches"""
    features = tuple(sorted([k for k, v in branch_data.get('features', {}).items() if v]))
    unique = tuple(sorted(branch_data.get('unique_features', [])))
    missing = tuple(sorted(branch_data.get('missing_features', [])))
    status = branch_data.get('status', 'Unknown')
    return (features, unique, missing, status)

# Group identical branches
groups = defaultdict(list)
for branch_name, data in branch_features.items():
    fingerprint = get_fingerprint(data)
    groups[fingerprint].append(branch_name)

# Create unified analysis
unified_analysis = {}
for fingerprint, branches in groups.items():
    # Representative branch (first one alphabetically)
    rep_branch = sorted(branches)[0]
    rep_data = branch_features[rep_branch]
    
    group_key = f"Group_{len(unified_analysis)}"
    unified_analysis[group_key] = {
        'representative': rep_branch,
        'branches': sorted(branches),
        'count': len(branches),
        'features': rep_data['features'],
        'unique_features': rep_data['unique_features'],
        'missing_features': rep_data['missing_features'],
        'status': rep_data['status'],
        'issues': rep_data.get('issues', [])
    }

# Sort by count (most common groups first)
unified_sorted = dict(sorted(unified_analysis.items(), key=lambda x: x[1]['count'], reverse=True))

# Save unified analysis
with open('unified_branches.json', 'w') as f:
    json.dump(unified_sorted, f, indent=2)

# Summary
print(f"✅ Unified {len(branch_features)} branches into {len(unified_sorted)} groups")
for group, data in list(unified_sorted.items())[:5]:
    print(f"  {group}: {data['count']} branches - {data['representative']}")
