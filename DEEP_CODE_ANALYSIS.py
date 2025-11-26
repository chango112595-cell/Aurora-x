#!/usr/bin/env python3
"""
AURORA FORENSIC ANALYSIS - PHASE 2: DEEP CODE ANALYSIS
Analyzes code quality, dependencies, and potential runtime issues
"""

import json
import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict


class DeepCodeAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.findings = defaultdict(list)

    def analyze_python_imports(self):
        """Analyze Python files for missing imports"""
        print("\n[DEEP ANALYSIS] Python Import Dependencies")
        print("━" * 60)

        py_files = list(self.project_root.glob("*.py"))
        py_files.extend(list((self.project_root / "tools").glob("*.py")))

        missing_imports = []

        for py_file in py_files[:20]:  # Sample first 20 files
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for common imports
                imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                from_imports = re.findall(
                    r'^from\s+([\w.]+)', content, re.MULTILINE)

                # Check if imported modules exist
                for imp in imports:
                    if imp not in ['os', 'sys', 'json', 're', 'pathlib', 'typing', 'datetime']:
                        try:
                            __import__(imp)
                        except ImportError:
                            missing_imports.append((py_file.name, imp))

            except Exception as e:
                pass

        if missing_imports:
            print(
                f"  ⚠ Found {len(missing_imports)} potential missing imports")
            for file, imp in missing_imports[:5]:
                print(f"    • {file}: {imp}")
                self.findings['python_imports'].append(
                    {'file': file, 'module': imp})
        else:
            print("  ✓ No obvious missing Python imports detected")

    def analyze_react_components(self):
        """Analyze React components for common issues"""
        print("\n[DEEP ANALYSIS] React Component Health")
        print("━" * 60)

        tsx_files = list((self.project_root / "client" /
                         "src" / "components").glob("*.tsx"))

        issues_found = 0

        for tsx_file in tsx_files:
            try:
                content = tsx_file.read_text(encoding='utf-8')

                # Check for useState without import
                if 'useState' in content and 'import { useState' not in content and 'import {' in content:
                    if 'useState' not in re.search(r'import \{([^}]+)\}', content).group(1):
                        print(
                            f"  ⚠ {tsx_file.name}: useState used but not imported")
                        issues_found += 1
                        self.findings['react'].append(
                            {'file': tsx_file.name, 'issue': 'useState not imported'})

                # Check for useEffect without import
                if 'useEffect' in content and 'import { useEffect' not in content and 'import {' in content:
                    imports_block = re.search(
                        r'import \{([^}]+)\} from [\'"]react[\'"]', content)
                    if imports_block and 'useEffect' not in imports_block.group(1):
                        print(
                            f"  ⚠ {tsx_file.name}: useEffect used but not imported")
                        issues_found += 1
                        self.findings['react'].append(
                            {'file': tsx_file.name, 'issue': 'useEffect not imported'})

                # Check for missing key prop in map
                map_without_key = re.search(
                    r'\.map\([^)]+\)\s*(?!.*key=)', content)
                if map_without_key:
                    print(f"  ⚠ {tsx_file.name}: .map() without key prop")
                    issues_found += 1
                    self.findings['react'].append(
                        {'file': tsx_file.name, 'issue': 'map without key'})

            except Exception as e:
                pass

        if issues_found == 0:
            print("  ✓ React components look healthy")

    def analyze_api_endpoints(self):
        """Analyze API endpoint structure"""
        print("\n[DEEP ANALYSIS] API Endpoints")
        print("━" * 60)

        # Check Next.js API routes
        api_dir = self.project_root / "app" / "api"
        if api_dir.exists():
            api_routes = list(api_dir.rglob("route.ts"))
            print(f"  Next.js API routes found: {len(api_routes)}")

            for route in api_routes:
                print(f"    • {route.relative_to(api_dir)}")
        else:
            print("  ✗ app/api directory not found")
            self.findings['api'].append({'issue': 'app/api directory missing'})

        # Check server API files
        server_dir = self.project_root / "server"
        if server_dir.exists():
            server_files = list(server_dir.glob("*.ts"))
            print(f"  Server files found: {len(server_files)}")

            for sf in server_files:
                if 'route' in sf.name or 'api' in sf.name:
                    print(f"    • {sf.name}")

    def analyze_environment_vars(self):
        """Check for environment variable usage"""
        print("\n[DEEP ANALYSIS] Environment Variables")
        print("━" * 60)

        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_file.exists() and not env_example.exists():
            print("  ⚠ No .env or .env.example file found")
            self.findings['env'].append({'issue': 'No environment file'})

        # Check for environment variable usage in code
        code_files = []
        code_files.extend(list(self.project_root.glob("*.py"))[:10])
        code_files.extend(list((self.project_root / "server").glob("*.ts")))

        env_vars_used = set()

        for file in code_files:
            try:
                content = file.read_text(encoding='utf-8')

                # Find process.env or os.getenv usage
                env_matches = re.findall(r'process\.env\.(\w+)', content)
                env_matches.extend(re.findall(
                    r'os\.getenv\(["\'](\w+)["\']\)', content))

                env_vars_used.update(env_matches)

            except Exception as e:
                pass

        if env_vars_used:
            print(
                f"  Found {len(env_vars_used)} environment variables in use:")
            for var in sorted(list(env_vars_used))[:10]:
                print(f"    • {var}")

    def analyze_database_config(self):
        """Check database configuration"""
        print("\n[DEEP ANALYSIS] Database Configuration")
        print("━" * 60)

        # Check for drizzle config
        drizzle_config = self.project_root / "drizzle.config.ts"
        if drizzle_config.exists():
            print("  ✓ drizzle.config.ts found")
        else:
            print("  ⚠ drizzle.config.ts not found")
            self.findings['database'].append(
                {'issue': 'drizzle.config.ts missing'})

        # Check for schema files
        schema_files = list(self.project_root.rglob("*schema.ts"))
        if schema_files:
            print(f"  Found {len(schema_files)} schema files:")
            for schema in schema_files[:5]:
                print(f"    • {schema.relative_to(self.project_root)}")
        else:
            print("  ⚠ No schema files found")

    def analyze_test_coverage(self):
        """Analyze test files"""
        print("\n[DEEP ANALYSIS] Test Coverage")
        print("━" * 60)

        test_dirs = ['tests', 'test', '__tests__']
        test_files = []

        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if test_path.exists():
                test_files.extend(list(test_path.rglob("test_*.py")))
                test_files.extend(list(test_path.rglob("*.test.ts")))
                test_files.extend(list(test_path.rglob("*.test.tsx")))

        if test_files:
            print(f"  Found {len(test_files)} test files")
            py_tests = len([f for f in test_files if f.suffix == '.py'])
            ts_tests = len(
                [f for f in test_files if f.suffix in ['.ts', '.tsx']])
            print(f"    • Python tests: {py_tests}")
            print(f"    • TypeScript tests: {ts_tests}")
        else:
            print("  ⚠ No test files found")
            self.findings['tests'].append({'issue': 'No tests found'})

    def analyze_security_issues(self):
        """Check for common security issues"""
        print("\n[DEEP ANALYSIS] Security Scan")
        print("━" * 60)

        # Check for hardcoded secrets
        sensitive_patterns = [
            (r'password\s*=\s*["\'](?!.*\$)([^"\']+)["\']',
             'Hardcoded password'),
            (r'api_key\s*=\s*["\'](?!.*\$)([^"\']+)["\']',
             'Hardcoded API key'),
            (r'secret\s*=\s*["\'](?!.*\$)([^"\']+)["\']', 'Hardcoded secret'),
        ]

        code_files = list(self.project_root.glob("*.py"))[:10]
        code_files.extend(list((self.project_root / "server").glob("*.ts")))

        security_issues = []

        for file in code_files:
            try:
                content = file.read_text(encoding='utf-8')

                for pattern, issue_type in sensitive_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        security_issues.append((file.name, issue_type))

            except Exception as e:
                pass

        if security_issues:
            print(
                f"  ⚠ Found {len(security_issues)} potential security issues:")
            for file, issue in security_issues[:5]:
                print(f"    • {file}: {issue}")
                self.findings['security'].append(
                    {'file': file, 'issue': issue})
        else:
            print("  ✓ No obvious security issues detected")

    def generate_deep_report(self):
        """Generate comprehensive report"""
        print("\n" + "=" * 60)
        print("DEEP CODE ANALYSIS COMPLETE")
        print("=" * 60)

        total_findings = sum(len(v) for v in self.findings.values())
        print(f"\nTotal findings across categories: {total_findings}")

        for category, issues in self.findings.items():
            if issues:
                print(f"\n{category.upper()}: {len(issues)} issues")
                for issue in issues[:3]:
                    print(f"  • {issue}")

        # Save report
        report_file = self.project_root / "AURORA_DEEP_ANALYSIS_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(dict(self.findings), f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║           AURORA DEEP CODE ANALYSIS - PHASE 2                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    analyzer = DeepCodeAnalyzer()

    analyzer.analyze_python_imports()
    analyzer.analyze_react_components()
    analyzer.analyze_api_endpoints()
    analyzer.analyze_environment_vars()
    analyzer.analyze_database_config()
    analyzer.analyze_test_coverage()
    analyzer.analyze_security_issues()

    analyzer.generate_deep_report()
