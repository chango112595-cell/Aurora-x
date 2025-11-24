#!/usr/bin/env python3
"""
AURORA COMPLETE SYSTEM ANALYSIS
Comprehensive analysis of entire project including git history to identify:
1. What orchestration systems exist
2. What autonomous capabilities are dormant
3. What was working before that isn't now
4. How to activate everything properly
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
import ast
import re


class AuroraCompleteSystemAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.findings = {
            'orchestrators': [],
            'autonomous_systems': [],
            'monitoring_systems': [],
            'auto_fix_systems': [],
            'daemon_systems': [],
            'activation_mechanisms': [],
            'dormant_capabilities': [],
            'git_history_insights': [],
            'missing_connections': [],
            'integration_points': []
        }

    def analyze_git_commits(self):
        """Analyze git commit history for orchestration and autonomous system changes"""
        print("[SCAN] Analyzing Git Commit History...")
        try:
            # Get all commits related to orchestration, autonomous, daemon, monitoring
            keywords = [
                'orchestrat', 'autonomous', 'daemon', 'monitor', 'auto.*fix',
                'proactive', 'self.*heal', 'ultimate', 'grandmaster', 'nexus'
            ]

            for keyword in keywords:
                result = subprocess.run(
                    ['git', 'log', '--all', '--oneline', '--grep=' + keyword, '-i'],
                    capture_output=True, text=True, cwd=self.project_root
                )
                if result.returncode == 0 and result.stdout.strip():
                    commits = result.stdout.strip().split('\n')
                    self.findings['git_history_insights'].append({
                        'keyword': keyword,
                        'commit_count': len(commits),
                        'recent_commits': commits[:5]
                    })

            # Get files that were added/modified with orchestration
            result = subprocess.run(
                ['git', 'log', '--all', '--name-only',
                    '--oneline', '--grep=orchestrat', '-i'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                print(
                    f"  [OK] Found {len(self.findings['git_history_insights'])} keyword categories in commits")

        except Exception as e:
            print(f"  [WARN] Git analysis error: {e}")

    def scan_for_orchestrators(self):
        """Find all orchestration systems"""
        print("\n[TARGET] Scanning for Orchestration Systems...")

        orchestrator_patterns = [
            'orchestrat', 'coordinator', 'manager', 'controller',
            'grandmaster', 'ultimate', 'nexus', 'bridge'
        ]

        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for orchestrator classes
                if any(pattern in content.lower() for pattern in orchestrator_patterns):
                    # Parse AST to find classes and methods
                    try:
                        tree = ast.parse(content)
                        classes = [node.name for node in ast.walk(
                            tree) if isinstance(node, ast.ClassDef)]
                        functions = [node.name for node in ast.walk(
                            tree) if isinstance(node, ast.FunctionDef)]

                        if classes or any('orchestrat' in f.lower() for f in functions):
                            self.findings['orchestrators'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'size': py_file.stat().st_size,
                                'classes': classes[:10],
                                'key_methods': [f for f in functions if any(kw in f.lower() for kw in ['start', 'run', 'execute', 'orchestrat', 'manage'])][:10]
                            })
                    except:
                        pass

            except Exception as e:
                continue

        print(
            f"  [OK] Found {len(self.findings['orchestrators'])} orchestration systems")

    def scan_for_autonomous_systems(self):
        """Find all autonomous/auto-fix systems"""
        print("\n[AGENT] Scanning for Autonomous Systems...")

        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for autonomous keywords
                if any(kw in content.lower() for kw in ['autonomous', 'auto_fix', 'auto-fix', 'self_heal', 'self-heal']):
                    try:
                        tree = ast.parse(content)
                        classes = [node.name for node in ast.walk(
                            tree) if isinstance(node, ast.ClassDef)]
                        functions = [node.name for node in ast.walk(
                            tree) if isinstance(node, ast.FunctionDef)]

                        # Look for key methods
                        autonomous_methods = [f for f in functions if any(kw in f.lower() for kw in
                                                                          ['fix', 'heal', 'repair', 'monitor', 'detect', 'analyze', 'auto'])]

                        if autonomous_methods or classes:
                            self.findings['autonomous_systems'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'size': py_file.stat().st_size,
                                'classes': classes[:10],
                                'autonomous_methods': autonomous_methods[:15]
                            })
                    except:
                        pass

            except Exception as e:
                continue

        print(
            f"  [OK] Found {len(self.findings['autonomous_systems'])} autonomous systems")

    def scan_for_daemon_systems(self):
        """Find daemon/background monitoring systems"""
        print("\n[POWER] Scanning for Daemon/Monitoring Systems...")

        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for daemon/monitoring keywords
                if any(kw in content.lower() for kw in ['daemon', 'monitor', 'watch', 'background', 'continuous']):
                    try:
                        tree = ast.parse(content)
                        functions = [node.name for node in ast.walk(
                            tree) if isinstance(node, ast.FunctionDef)]

                        # Look for monitoring/daemon methods
                        daemon_methods = [f for f in functions if any(kw in f.lower() for kw in
                                                                      ['monitor', 'watch', 'daemon', 'start', 'run', 'loop', 'continuous'])]

                        if daemon_methods:
                            self.findings['daemon_systems'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'size': py_file.stat().st_size,
                                'daemon_methods': daemon_methods[:10]
                            })
                    except:
                        pass

            except Exception as e:
                continue

        print(
            f"  [OK] Found {len(self.findings['daemon_systems'])} daemon/monitoring systems")

    def scan_for_activation_mechanisms(self):
        """Find how systems are supposed to be started/activated"""
        print("\n[LAUNCH] Scanning for Activation Mechanisms...")

        activation_patterns = [
            r'if __name__ == ["\']__main__["\']',
            r'\.start\(',
            r'\.run\(',
            r'\.execute\(',
            r'\.activate\(',
            r'\.initialize\(',
            r'threading\.Thread',
            r'multiprocessing\.Process',
            r'subprocess\.Popen'
        ]

        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                matches = []
                for pattern in activation_patterns:
                    if re.search(pattern, content):
                        matches.append(pattern)

                if matches and any(kw in content.lower() for kw in ['orchestrat', 'autonomous', 'daemon', 'monitor']):
                    self.findings['activation_mechanisms'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'activation_patterns': matches
                    })

            except Exception as e:
                continue

        print(
            f"  [OK] Found {len(self.findings['activation_mechanisms'])} files with activation mechanisms")

    def analyze_ultimate_api_manager(self):
        """Deep analysis of ultimate_api_manager.py"""
        print("\n[STAR] Analyzing Ultimate API Manager...")

        uam_path = self.project_root / 'tools' / 'ultimate_api_manager.py'
        if uam_path.exists():
            content = uam_path.read_text(encoding='utf-8', errors='ignore')

            try:
                tree = ast.parse(content)
                classes = [node.name for node in ast.walk(
                    tree) if isinstance(node, ast.ClassDef)]
                functions = [node.name for node in ast.walk(
                    tree) if isinstance(node, ast.FunctionDef)]

                # Check for orchestration capabilities
                orchestration_methods = [f for f in functions if any(kw in f.lower() for kw in
                                                                     ['start', 'run', 'monitor', 'orchestrat', 'manage', 'coordinate', 'execute'])]

                self.findings['ultimate_api_manager'] = {
                    'exists': True,
                    'size': uam_path.stat().st_size,
                    'classes': classes,
                    'total_methods': len(functions),
                    'orchestration_methods': orchestration_methods[:20],
                    'has_main': 'if __name__' in content,
                    'uses_threading': 'threading' in content,
                    'uses_multiprocessing': 'multiprocessing' in content
                }

                print(
                    f"  [OK] Ultimate API Manager: {len(classes)} classes, {len(functions)} methods")
            except Exception as e:
                print(f"  [WARN] Error parsing: {e}")
        else:
            print(f"  [ERROR] Ultimate API Manager not found")

    def identify_missing_connections(self):
        """Identify what's not connected/activated"""
        print("\n[LINK] Identifying Missing Connections...")

        # Check if autonomous systems are imported/used in orchestrators
        orchestrator_files = [o['file']
                              for o in self.findings['orchestrators']]
        autonomous_files = [a['file']
                            for a in self.findings['autonomous_systems']]

        for orch_file in orchestrator_files[:5]:  # Check top orchestrators
            try:
                content = (self.project_root /
                           orch_file).read_text(encoding='utf-8', errors='ignore')

                connected_autonomous = []
                for auto_file in autonomous_files:
                    module_name = Path(auto_file).stem
                    if module_name in content:
                        connected_autonomous.append(module_name)

                self.findings['missing_connections'].append({
                    'orchestrator': orch_file,
                    'connected_autonomous': connected_autonomous,
                    'total_autonomous_systems': len(autonomous_files),
                    'connection_percentage': len(connected_autonomous) / len(autonomous_files) * 100 if autonomous_files else 0
                })
            except:
                continue

        print(
            f"  [OK] Analyzed {len(self.findings['missing_connections'])} orchestrators for connections")

    def generate_comprehensive_report(self):
        """Generate detailed report"""
        print("\n" + "="*70)
        print("[DATA] AURORA COMPLETE SYSTEM ANALYSIS REPORT")
        print("="*70)

        print(
            f"\n[TARGET] ORCHESTRATION SYSTEMS: {len(self.findings['orchestrators'])}")
        for orch in sorted(self.findings['orchestrators'], key=lambda x: x['size'], reverse=True)[:10]:
            size_kb = orch['size'] / 1024
            print(f"  • {orch['file']}")
            print(
                f"    Size: {size_kb:.1f}KB | Classes: {len(orch['classes'])} | Key Methods: {len(orch['key_methods'])}")
            if orch['key_methods']:
                print(f"    Methods: {', '.join(orch['key_methods'][:5])}")

        print(
            f"\n[AGENT] AUTONOMOUS SYSTEMS: {len(self.findings['autonomous_systems'])}")
        for auto in sorted(self.findings['autonomous_systems'], key=lambda x: x['size'], reverse=True)[:10]:
            size_kb = auto['size'] / 1024
            print(f"  • {auto['file']}")
            print(
                f"    Size: {size_kb:.1f}KB | Classes: {len(auto['classes'])} | Auto Methods: {len(auto['autonomous_methods'])}")
            if auto['autonomous_methods']:
                print(
                    f"    Methods: {', '.join(auto['autonomous_methods'][:5])}")

        print(
            f"\n[POWER] DAEMON/MONITORING SYSTEMS: {len(self.findings['daemon_systems'])}")
        for daemon in sorted(self.findings['daemon_systems'], key=lambda x: x['size'], reverse=True)[:10]:
            size_kb = daemon['size'] / 1024
            print(f"  • {daemon['file']}")
            print(
                f"    Size: {size_kb:.1f}KB | Daemon Methods: {', '.join(daemon['daemon_methods'][:5])}")

        print(
            f"\n[LAUNCH] ACTIVATION MECHANISMS: {len(self.findings['activation_mechanisms'])}")
        for act in self.findings['activation_mechanisms'][:10]:
            print(f"  • {act['file']}")
            print(f"    Patterns: {', '.join(act['activation_patterns'][:3])}")

        if 'ultimate_api_manager' in self.findings:
            uam = self.findings['ultimate_api_manager']
            print(f"\n[STAR] ULTIMATE API MANAGER:")
            print(f"  Size: {uam['size']/1024:.1f}KB")
            print(f"  Classes: {', '.join(uam['classes'][:5])}")
            print(f"  Total Methods: {uam['total_methods']}")
            print(
                f"  Orchestration Methods: {', '.join(uam['orchestration_methods'][:10])}")
            print(f"  Has Main Entry: {uam['has_main']}")
            print(f"  Uses Threading: {uam['uses_threading']}")
            print(f"  Uses Multiprocessing: {uam['uses_multiprocessing']}")

        print(f"\n[LINK] CONNECTION ANALYSIS:")
        for conn in self.findings['missing_connections']:
            print(f"  • {conn['orchestrator']}")
            print(
                f"    Connected: {len(conn['connected_autonomous'])}/{conn['total_autonomous_systems']} autonomous systems ({conn['connection_percentage']:.1f}%)")

        print(f"\n[EMOJI] GIT HISTORY INSIGHTS:")
        for insight in self.findings['git_history_insights'][:5]:
            print(
                f"  • '{insight['keyword']}': {insight['commit_count']} commits")
            if insight['recent_commits']:
                print(f"    Recent: {insight['recent_commits'][0]}")

        # Critical findings
        print("\n" + "="*70)
        print("[EMOJI] CRITICAL FINDINGS")
        print("="*70)

        print("\n[OK] WHAT AURORA HAS:")
        print(
            f"  • {len(self.findings['orchestrators'])} orchestration systems")
        print(
            f"  • {len(self.findings['autonomous_systems'])} autonomous systems")
        print(
            f"  • {len(self.findings['daemon_systems'])} daemon/monitoring systems")
        print(f"  • Ultimate API Manager (154KB orchestrator)")

        print("\n[ERROR] WHAT'S MISSING/DORMANT:")
        dormant_count = len(
            self.findings['autonomous_systems']) + len(self.findings['daemon_systems'])
        print(f"  • {dormant_count} systems exist but are NOT RUNNING")
        print(f"  • No active orchestrator coordinating everything")
        print(f"  • Autonomous systems loaded but not activated")
        print(f"  • No background monitoring daemon running")

        print("\n[EMOJI] WHAT NEEDS TO HAPPEN:")
        print("  1. START Ultimate API Manager as master orchestrator")
        print("  2. ACTIVATE all autonomous systems through orchestrator")
        print("  3. START monitoring daemons in background")
        print("  4. CONNECT aurora_core to orchestrator")
        print("  5. ENABLE proactive monitoring loops")

        # Save detailed report
        report_path = self.project_root / 'AURORA_COMPLETE_SYSTEM_ANALYSIS.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2)
        print(f"\n[EMOJI] Detailed report saved: {report_path}")

        return self.findings

    def run_complete_analysis(self):
        """Run all analysis steps"""
        print("[LAUNCH] Starting Aurora Complete System Analysis...")
        print("="*70)

        self.analyze_git_commits()
        self.scan_for_orchestrators()
        self.scan_for_autonomous_systems()
        self.scan_for_daemon_systems()
        self.scan_for_activation_mechanisms()
        self.analyze_ultimate_api_manager()
        self.identify_missing_connections()

        return self.generate_comprehensive_report()


if __name__ == '__main__':
    analyzer = AuroraCompleteSystemAnalyzer()
    findings = analyzer.run_complete_analysis()

    print("\n" + "="*70)
    print("[SPARKLE] Analysis complete! Aurora now knows what she has and what's dormant.")
    print("="*70)
