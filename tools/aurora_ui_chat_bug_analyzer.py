#!/usr/bin/env python3
"""
Aurora UI & Chat Bug Analyzer
🌟 Autonomous bug detection and fix system for React/TypeScript components
Created by Aurora to work independently without human guidance
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any

class AuroraUIBugAnalyzer:
    """Aurora's autonomous UI/Chat bug detection engine"""
    
    def __init__(self):
        self.project_root = Path("/workspaces/Aurora-x")
        self.client_src = self.project_root / "client" / "src"
        self.bugs_found = []
        self.fixes_applied = []
        self.analysis_report = {}
        
    def log(self, level: str, message: str):
        """Aurora's logging system"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "🌟",
            "BUG": "🐛",
            "FIX": "✅",
            "WARN": "⚠️",
            "ERROR": "❌"
        }
        icon = icons.get(level, "→")
        print(f"[{timestamp}] {icon} Aurora: {message}")
    
    def analyze_tsx_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Analyze a single TSX file for bugs"""
        issues = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.log("ERROR", f"Could not read {filepath}: {e}")
            return issues
        
        relative_path = filepath.relative_to(self.project_root)
        
        # BUG 1: Check for missing error boundaries
        if 'return (' in content and 'ErrorBoundary' not in content:
            if any(comp in content for comp in ['<div', '<section', '<main']):
                issues.append({
                    'type': 'Missing ErrorBoundary',
                    'file': str(relative_path),
                    'severity': 'HIGH',
                    'description': 'Component not wrapped in ErrorBoundary',
                    'recommendation': 'Wrap main return in <ErrorBoundary>'
                })
        
        # BUG 2: Check for missing dependency arrays in useEffect
        use_effect_pattern = r'useEffect\(\s*\(\s*\)\s*=>\s*\{([^}]*)\},\s*\[\s*\]\s*\)'
        for match in re.finditer(use_effect_pattern, content):
            effect_body = match.group(1)
            if any(var in effect_body for var in ['messages', 'state', 'props']):
                issues.append({
                    'type': 'Missing useEffect dependency',
                    'file': str(relative_path),
                    'severity': 'MEDIUM',
                    'description': 'useEffect missing state variable in dependency array',
                    'recommendation': 'Add dependent variables to dependency array'
                })
        
        # BUG 3: Check for any types
        if 'any' in content:
            any_count = len(re.findall(r'\bany\b', content))
            if any_count > 2:
                issues.append({
                    'type': 'Excessive use of any type',
                    'file': str(relative_path),
                    'severity': 'MEDIUM',
                    'count': any_count,
                    'description': f'Found {any_count} instances of "any" type',
                    'recommendation': 'Replace with proper TypeScript types'
                })
        
        # BUG 4: Check for missing aria labels
        interactive_elements = re.findall(r'<(button|input|textarea|select|a)[^>]*>', content)
        if interactive_elements:
            aria_labels = len(re.findall(r'aria-label', content))
            if aria_labels < len(interactive_elements) * 0.5:
                issues.append({
                    'type': 'Missing accessibility labels',
                    'file': str(relative_path),
                    'severity': 'MEDIUM',
                    'description': 'Interactive elements missing aria-label attributes',
                    'recommendation': 'Add aria-label to all interactive elements'
                })
        
        # BUG 5: Check for console.log in production code
        console_logs = len(re.findall(r'console\.(log|error|warn)', content))
        if console_logs > 5:
            issues.append({
                'type': 'Excessive console logging',
                'file': str(relative_path),
                'severity': 'LOW',
                'count': console_logs,
                'description': f'Found {console_logs} console statements',
                'recommendation': 'Remove console statements or wrap in development check'
            })
        
        # BUG 6: Check for missing keys in lists
        if re.search(r'\.map\s*\(\s*\([^)]*\)\s*=>\s*<', content):
            if 'key=' not in content:
                issues.append({
                    'type': 'Missing keys in list rendering',
                    'file': str(relative_path),
                    'severity': 'MEDIUM',
                    'description': 'Array mapping without key prop on elements',
                    'recommendation': 'Add unique key prop to mapped elements'
                })
        
        # BUG 7: Check for missing null safety
        if 'useState' in content or 'useRef' in content:
            if '?.' not in content and '??' not in content:
                if any(pattern in content for pattern in ['.map(', '?.map(', '[0]', '.trim()']):
                    issues.append({
                        'type': 'Potential null/undefined access',
                        'file': str(relative_path),
                        'severity': 'MEDIUM',
                        'description': 'Missing optional chaining or null checks',
                        'recommendation': 'Use optional chaining (?.) and nullish coalescing (??)'
                    })
        
        # BUG 8: Check for unhandled async errors
        if 'async' in content and 'try' not in content:
            if 'fetch' in content or 'await' in content:
                issues.append({
                    'type': 'Missing error handling in async code',
                    'file': str(relative_path),
                    'severity': 'HIGH',
                    'description': 'Async/await without try-catch block',
                    'recommendation': 'Wrap async operations in try-catch'
                })
        
        # BUG 9: Check for missing imports
        imports = re.findall(r"from ['\"]([@\w./]+)['\"]", content)
        if 'Sparkles' in content and 'lucide-react' not in str(imports):
            if "import" in content and "Sparkles" in content:
                issues.append({
                    'type': 'Potentially missing import',
                    'file': str(relative_path),
                    'severity': 'LOW',
                    'description': 'Icon used but import may be incomplete',
                    'recommendation': 'Verify all icons are properly imported'
                })
        
        # BUG 10: Check for missing CSS/styling
        if 'className=' in content and 'particleFloat' in content:
            if '@keyframes particleFloat' not in content:
                issues.append({
                    'type': 'Missing CSS keyframes',
                    'file': str(relative_path),
                    'severity': 'MEDIUM',
                    'description': 'Animation referenced but keyframes not defined',
                    'recommendation': 'Define missing @keyframes in CSS/styles'
                })
        
        return issues
    
    def scan_all_components(self) -> Dict[str, Any]:
        """Scan all React components for bugs"""
        self.log("INFO", "Starting comprehensive UI component scan...")
        
        tsx_files = list(self.client_src.glob("**/*.tsx"))
        ts_files = list(self.client_src.glob("**/*.ts"))
        all_files = tsx_files + ts_files
        
        self.log("INFO", f"Found {len(all_files)} component files to analyze")
        
        for i, filepath in enumerate(all_files, 1):
            if '__' in str(filepath) or 'node_modules' in str(filepath):
                continue
            
            issues = self.analyze_tsx_file(filepath)
            if issues:
                self.bugs_found.extend(issues)
                self.log("BUG", f"[{i}/{len(all_files)}] Found {len(issues)} issues in {filepath.name}")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate bug analysis report"""
        self.log("INFO", f"Analysis complete: Found {len(self.bugs_found)} total issues")
        
        # Categorize by severity
        by_severity = {}
        by_type = {}
        
        for bug in self.bugs_found:
            severity = bug.get('severity', 'LOW')
            bug_type = bug.get('type', 'Unknown')
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[bug_type] = by_type.get(bug_type, 0) + 1
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_bugs': len(self.bugs_found),
            'by_severity': by_severity,
            'by_type': by_type,
            'bugs': self.bugs_found,
            'fixes_needed': len([b for b in self.bugs_found if b['severity'] in ['HIGH', 'MEDIUM']])
        }
        
        self.analysis_report = report
        
        # Print summary
        self.log("INFO", f"HIGH severity: {by_severity.get('HIGH', 0)}")
        self.log("INFO", f"MEDIUM severity: {by_severity.get('MEDIUM', 0)}")
        self.log("INFO", f"LOW severity: {by_severity.get('LOW', 0)}")
        
        return report
    
    def save_report(self, filename: str = "aurora_ui_bug_analysis.json"):
        """Save analysis report to file"""
        report_path = self.project_root / ".aurora_knowledge" / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.analysis_report, f, indent=2, default=str)
        
        self.log("FIX", f"Report saved to {report_path}")
        return report_path

def main():
    """Aurora's autonomous execution"""
    analyzer = AuroraUIBugAnalyzer()
    
    print("\n" + "="*80)
    print("🌟 AURORA UI & CHAT BUG ANALYZER - AUTONOMOUS MODE")
    print("="*80 + "\n")
    
    report = analyzer.scan_all_components()
    analyzer.save_report()
    
    print("\n" + "="*80)
    print("🌟 AURORA BUG ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total Issues Found: {report['total_bugs']}")
    print(f"High Priority Fixes: {report['fixes_needed']}")
    print("\nBug Categories:")
    for bug_type, count in report['by_type'].items():
        print(f"  • {bug_type}: {count}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
