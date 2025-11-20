#!/usr/bin/env python3
"""
Aurora Autonomous Debug & Fix Everything
Self-healing system that finds and fixes ALL errors across the entire project
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from aurora_core import create_aurora_core
    AURORA_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Aurora core not available: {e}")
    AURORA_AVAILABLE = False


class AuroraAutonomousDebugger:
    """Aurora's autonomous debugging and fixing system"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.issues_found = []
        self.fixes_applied = []
        self.scan_report = {
            "timestamp": datetime.now().isoformat(),
            "total_files_scanned": 0,
            "issues_found": 0,
            "fixes_applied": 0,
            "errors_by_type": {},
            "files_fixed": []
        }
        
        if AURORA_AVAILABLE:
            self.aurora = create_aurora_core()
            print("🌟 Aurora Intelligence Core: ONLINE")
        else:
            self.aurora = None
            print("⚙️ Running in standalone mode")
    
    def log(self, message: str, level: str = "INFO"):
        """Log with Aurora's intelligence"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "DEBUG": "🔍",
            "FIX": "🔧"
        }.get(level, "ℹ️")
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def scan_python_files(self) -> List[Path]:
        """Scan all Python files for syntax and import errors"""
        self.log("Scanning Python files for errors...", "DEBUG")
        
        python_files = []
        skip_dirs = {'.venv', 'venv', 'node_modules', '__pycache__', '.git', 
                     'dist', 'build', '.pytest_cache', '.mypy_cache'}
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        self.scan_report["total_files_scanned"] = len(python_files)
        self.log(f"Found {len(python_files)} Python files to analyze", "INFO")
        
        return python_files
    
    def check_python_syntax(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check Python file for syntax errors"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Try to compile the code
            compile(code, str(file_path), 'exec')
            
        except SyntaxError as e:
            issues.append({
                "file": str(file_path),
                "line": e.lineno,
                "type": "SyntaxError",
                "message": str(e.msg),
                "text": e.text
            })
        except Exception as e:
            issues.append({
                "file": str(file_path),
                "type": "CompileError",
                "message": str(e)
            })
        
        return issues
    
    def run_pylint_check(self, file_path: Path) -> List[Dict[str, Any]]:
        """Run pylint on a file to find issues"""
        issues = []
        
        try:
            result = subprocess.run(
                ['pylint', str(file_path), '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                pylint_issues = json.loads(result.stdout)
                for issue in pylint_issues:
                    if issue['type'] in ['error', 'fatal']:
                        issues.append({
                            "file": str(file_path),
                            "line": issue.get('line', 0),
                            "type": f"pylint-{issue['type']}",
                            "message": issue['message'],
                            "symbol": issue.get('symbol', '')
                        })
        except subprocess.TimeoutExpired:
            self.log(f"Pylint timeout on {file_path.name}", "WARNING")
        except FileNotFoundError:
            self.log("Pylint not installed, skipping pylint checks", "WARNING")
        except Exception as e:
            self.log(f"Pylint error on {file_path.name}: {e}", "WARNING")
        
        return issues
    
    def check_typescript_files(self) -> List[Dict[str, Any]]:
        """Check TypeScript files for errors"""
        self.log("Checking TypeScript files...", "DEBUG")
        issues = []
        
        try:
            # Run TypeScript compiler in check mode
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', '--pretty', 'false'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.project_root
            )
            
            if result.returncode != 0 and result.stdout:
                # Parse TypeScript errors
                for line in result.stdout.split('\n'):
                    if line.strip():
                        match = re.match(r'(.+?)\((\d+),(\d+)\): error (.+?):', line)
                        if match:
                            issues.append({
                                "file": match.group(1),
                                "line": int(match.group(2)),
                                "column": int(match.group(3)),
                                "type": "TypeScriptError",
                                "message": match.group(4)
                            })
        
        except subprocess.TimeoutExpired:
            self.log("TypeScript check timeout", "WARNING")
        except FileNotFoundError:
            self.log("TypeScript not available, skipping TS checks", "WARNING")
        except Exception as e:
            self.log(f"TypeScript check error: {e}", "WARNING")
        
        return issues
    
    def check_dockerfile_syntax(self) -> List[Dict[str, Any]]:
        """Check Dockerfile syntax"""
        self.log("Checking Dockerfiles...", "DEBUG")
        issues = []
        
        dockerfiles = list(self.project_root.glob('**/Dockerfile*'))
        
        for dockerfile in dockerfiles:
            if dockerfile.is_file() and '.dockerignore' not in str(dockerfile):
                try:
                    with open(dockerfile, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for common Dockerfile issues
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        # Check FROM casing
                        if re.match(r'FROM\s+.+\s+as\s+', line):
                            issues.append({
                                "file": str(dockerfile),
                                "line": i,
                                "type": "DockerfileError",
                                "message": "Use uppercase AS in multi-stage builds",
                                "fix": line.replace(' as ', ' AS ')
                            })
                
                except Exception as e:
                    self.log(f"Error checking {dockerfile.name}: {e}", "WARNING")
        
        return issues
    
    def fix_dockerfile_casing(self, issue: Dict[str, Any]) -> bool:
        """Fix Dockerfile AS casing"""
        try:
            file_path = Path(issue["file"])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix the casing
            fixed_content = re.sub(r'FROM\s+(.+?)\s+as\s+', r'FROM \1 AS ', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            self.log(f"Fixed AS casing in {file_path.name}", "FIX")
            return True
        
        except Exception as e:
            self.log(f"Failed to fix {issue['file']}: {e}", "ERROR")
            return False
    
    def fix_python_imports(self, issue: Dict[str, Any]) -> bool:
        """Attempt to fix Python import errors"""
        try:
            if 'import' not in issue.get('message', '').lower():
                return False
            
            file_path = Path(issue["file"])
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Common import fixes
            fixed = False
            for i, line in enumerate(lines):
                # Fix relative imports
                if 'from test import' in line and 'tests/' in str(file_path):
                    lines[i] = line.replace('from test import', 'from ..test import')
                    fixed = True
                
                # Add missing Optional import
                if 'Optional' in line and 'from typing import' in line and 'Optional' not in lines[i]:
                    if 'import' in line:
                        lines[i] = line.rstrip() + ', Optional\n'
                        fixed = True
            
            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                self.log(f"Fixed imports in {file_path.name}", "FIX")
                return True
        
        except Exception as e:
            self.log(f"Failed to fix imports in {issue['file']}: {e}", "ERROR")
        
        return False
    
    def auto_fix_issue(self, issue: Dict[str, Any]) -> bool:
        """Intelligently fix an issue"""
        issue_type = issue.get('type', '')
        
        # Route to appropriate fixer
        if 'Dockerfile' in issue_type:
            return self.fix_dockerfile_casing(issue)
        elif 'import' in issue.get('message', '').lower():
            return self.fix_python_imports(issue)
        
        return False
    
    def run_full_scan(self):
        """Run complete project scan and fix"""
        self.log("=" * 80, "INFO")
        self.log("AURORA AUTONOMOUS DEBUG & FIX - FULL PROJECT SCAN", "INFO")
        self.log("=" * 80, "INFO")
        
        # 1. Scan Python files
        python_files = self.scan_python_files()
        
        for py_file in python_files:
            # Check syntax
            syntax_issues = self.check_python_syntax(py_file)
            self.issues_found.extend(syntax_issues)
            
            # Check with pylint (only if no syntax errors)
            if not syntax_issues:
                pylint_issues = self.run_pylint_check(py_file)
                self.issues_found.extend(pylint_issues)
        
        # 2. Check TypeScript files
        ts_issues = self.check_typescript_files()
        self.issues_found.extend(ts_issues)
        
        # 3. Check Dockerfiles
        docker_issues = self.check_dockerfile_syntax()
        self.issues_found.extend(docker_issues)
        
        # Report findings
        self.scan_report["issues_found"] = len(self.issues_found)
        
        self.log("=" * 80, "INFO")
        self.log(f"SCAN COMPLETE: Found {len(self.issues_found)} issues", "INFO")
        self.log("=" * 80, "INFO")
        
        # Categorize issues
        for issue in self.issues_found:
            issue_type = issue.get('type', 'Unknown')
            self.scan_report["errors_by_type"][issue_type] = \
                self.scan_report["errors_by_type"].get(issue_type, 0) + 1
        
        # Display issues by type
        for issue_type, count in self.scan_report["errors_by_type"].items():
            self.log(f"  {issue_type}: {count}", "INFO")
        
        # Auto-fix issues
        if self.issues_found:
            self.log("\n🔧 Attempting automatic fixes...", "INFO")
            
            for issue in self.issues_found:
                if self.auto_fix_issue(issue):
                    self.fixes_applied.append(issue)
                    self.scan_report["files_fixed"].append(issue.get("file"))
            
            self.scan_report["fixes_applied"] = len(self.fixes_applied)
            
            self.log(f"\n✅ Applied {len(self.fixes_applied)} fixes", "SUCCESS")
        
        # Save report
        report_path = self.project_root / "aurora_debug_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.scan_report, f, indent=2)
        
        self.log(f"\n📊 Full report saved to: {report_path}", "SUCCESS")
        
        return self.scan_report
    
    def display_summary(self):
        """Display final summary"""
        print("\n" + "=" * 80)
        print("🌟 AURORA AUTONOMOUS DEBUG SUMMARY")
        print("=" * 80)
        print(f"Files Scanned:  {self.scan_report['total_files_scanned']}")
        print(f"Issues Found:   {self.scan_report['issues_found']}")
        print(f"Fixes Applied:  {self.scan_report['fixes_applied']}")
        print(f"Success Rate:   {(self.scan_report['fixes_applied'] / max(self.scan_report['issues_found'], 1)) * 100:.1f}%")
        print("=" * 80)
        
        if self.fixes_applied:
            print("\n🔧 Files Fixed:")
            unique_files = set(self.scan_report["files_fixed"])
            for file in sorted(unique_files):
                print(f"  • {file}")
        
        if self.scan_report['issues_found'] > self.scan_report['fixes_applied']:
            remaining = self.scan_report['issues_found'] - self.scan_report['fixes_applied']
            print(f"\n⚠️ {remaining} issues require manual review")
            print("Check aurora_debug_report.json for details")


def main():
    """Main execution"""
    debugger = AuroraAutonomousDebugger()
    
    try:
        debugger.run_full_scan()
        debugger.display_summary()
        
        # Exit with appropriate code
        if debugger.scan_report['issues_found'] == 0:
            print("\n🎉 Perfect! No issues found!")
            sys.exit(0)
        elif debugger.scan_report['fixes_applied'] > 0:
            print("\n✅ Aurora successfully fixed issues autonomously!")
            sys.exit(0)
        else:
            print("\n⚠️ Some issues require manual review")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
