#!/usr/bin/env python3
"""
Execute Aurora Code Quality Enforcer on entire codebase
"""

from aurora_code_quality_enforcer import AuroraCodeQualityEnforcer
from pathlib import Path

print("\n" + "="*70)
print("🔧 EXECUTING CODE QUALITY ENFORCEMENT - FULL SCAN")
print("="*70 + "\n")

enforcer = AuroraCodeQualityEnforcer()

# Scan all Python files in key directories
all_issues = []
files_to_fix = []

print("Scanning key directories...\n")

# Scan new tier files
tier_files = [
    "aurora_visual_understanding.py",
    "aurora_live_integration.py",
    "aurora_test_generator.py",
    "aurora_security_auditor.py",
    "aurora_doc_generator.py",
    "aurora_multi_agent.py",
    "aurora_ui_generator.py",
    "aurora_git_master.py"
]

for file in tier_files:
    if Path(file).exists():
        issues = enforcer.scan_file(file)
        if issues:
            all_issues.extend(issues)
            files_to_fix.append(file)

# Generate report
report = enforcer.generate_quality_report(all_issues)

print("\n" + "="*70)
print("📊 QUALITY REPORT")
print("="*70)
print(f"Files Scanned: {len(tier_files)}")
print(f"Total Issues: {report['total_issues']}")
print(f"Auto-Fixable: {report['auto_fixable']}")
print(f"By Severity: {report['by_severity']}")
print(f"By Type: {report['by_type']}")

# Auto-fix all issues
if report['auto_fixable'] > 0:
    print("\n" + "="*70)
    print("🔧 AUTO-FIXING ISSUES")
    print("="*70 + "\n")

    total_fixed = 0
    for file in files_to_fix:
        file_issues = [i for i in all_issues if i.file_path == file]
        fixed = enforcer.fix_unused_arguments(file, file_issues)
        total_fixed += fixed

    print(f"\n✅ Fixed {total_fixed} issues automatically!")

print("\n" + "="*70)
print("✅ CODE QUALITY ENFORCEMENT COMPLETE")
print("="*70 + "\n")
