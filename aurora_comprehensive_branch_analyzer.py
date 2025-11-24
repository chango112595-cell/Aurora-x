"""
Aurora Comprehensive Branch Analyzer
Deeply analyzes all branches to determine what Aurora actually needs
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re


class AuroraComprehensiveBranchAnalyzer:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "current_branch": self.get_current_branch(),
            "aurora_assessment": {},
            "critical_needs": [],
            "recommended_merges": [],
            "capability_gaps": [],
            "feature_enhancements": [],
            "integration_priorities": []
        }

        # What Aurora currently has in main
        self.current_capabilities = self.scan_current_capabilities()

        # What Aurora is looking for
        self.aurora_needs = {
            "autonomous_systems": [
                "autonomous_agent",
                "autonomous_monitor",
                "autonomous_integration",
                "autonomous_analyzer",
                "autonomous_fixer"
            ],
            "intelligence_systems": [
                "intelligence_manager",
                "intelligence_tracker",
                "intelligence_scorer",
                "intelligence_aggregator"
            ],
            "orchestration_systems": [
                "advanced_orchestrator",
                "service_manager",
                "connection_manager",
                "health_monitor"
            ],
            "ui_enhancements": [
                "cosmic_nexus",
                "advanced_dashboard",
                "real_time_monitor",
                "interactive_console"
            ],
            "api_extensions": [
                "comprehensive_endpoints",
                "websocket_support",
                "streaming_responses",
                "batch_operations"
            ],
            "knowledge_systems": [
                "knowledge_graph",
                "learning_system",
                "memory_persistence",
                "experience_tracker"
            ],
            "testing_systems": [
                "automated_testing",
                "continuous_validation",
                "regression_detection",
                "performance_monitoring"
            ],
            "integration_systems": [
                "cross_service_integration",
                "external_api_integration",
                "plugin_system",
                "extension_framework"
            ]
        }

    def get_current_branch(self):
        """Get current branch name"""
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        return result.stdout.strip()

    def scan_current_capabilities(self):
        """Scan what Aurora currently has in main"""
        capabilities = {
            "files": [],
            "systems": set(),
            "features": set(),
            "endpoints": set(),
            "ui_components": set()
        }

        # Scan for Aurora files in main
        for py_file in self.repo_root.glob("aurora*.py"):
            capabilities["files"].append(py_file.name)

            # Analyze file content for capabilities
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check for systems
                if "autonomous" in content.lower():
                    capabilities["systems"].add("autonomous_basic")
                if "orchestrat" in content.lower():
                    capabilities["systems"].add("orchestration_basic")
                if "intelligence" in content.lower():
                    capabilities["systems"].add("intelligence_basic")
                if "monitor" in content.lower():
                    capabilities["systems"].add("monitoring_basic")

                # Check for features
                if "async def" in content:
                    capabilities["features"].add("async_support")
                if "websocket" in content.lower():
                    capabilities["features"].add("websocket")
                if "cache" in content.lower():
                    capabilities["features"].add("caching")

            except Exception:
                pass

        # Check aurora_x directory
        aurora_x_dir = self.repo_root / "aurora_x"
        if aurora_x_dir.exists():
            for py_file in aurora_x_dir.glob("**/*.py"):
                rel_path = py_file.relative_to(self.repo_root)
                capabilities["files"].append(str(rel_path))

        # Check client UI components
        client_dir = self.repo_root / "client" / "src" / "components"
        if client_dir.exists():
            for tsx_file in client_dir.glob("**/Aurora*.tsx"):
                capabilities["ui_components"].add(tsx_file.name)

        return capabilities

    def get_all_branches(self):
        """Get all branches including remote"""
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('*'):
                # Remove 'remotes/origin/' prefix
                branch = line.replace('remotes/origin/', '')
                # Skip HEAD pointer
                if '->' not in branch and branch not in branches:
                    branches.append(branch)

        return branches

    def deep_analyze_branch(self, branch_name):
        """Deep analysis of what a branch offers"""
        print(f"\n[SCAN] Deep analyzing: {branch_name}")

        analysis = {
            "branch": branch_name,
            "unique_capabilities": [],
            "missing_in_main": [],
            "enhancements": [],
            "priority_files": [],
            "systems_offered": {},
            "integration_value": 0
        }

        # Get file list from branch
        try:
            result = subprocess.run(
                ["git", "ls-tree", "-r", "--name-only",
                    f"origin/{branch_name}"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=30
            )

            if result.returncode != 0:
                return analysis

            branch_files = result.stdout.strip().split('\n')

            # Focus on Aurora-specific files
            aurora_files = [f for f in branch_files if 'aurora' in f.lower()]

            for file_path in aurora_files:
                # Get file content from branch
                file_content = self.get_file_from_branch(
                    branch_name, file_path)
                if not file_content:
                    continue

                file_analysis = self.analyze_file_deeply(
                    file_path, file_content)

                # Check if this is something Aurora needs
                for need_category, need_items in self.aurora_needs.items():
                    for need_item in need_items:
                        if self.file_satisfies_need(file_analysis, need_item):
                            if need_item not in analysis["systems_offered"]:
                                analysis["systems_offered"][need_item] = []
                            analysis["systems_offered"][need_item].append(
                                file_path)
                            analysis["integration_value"] += 10

                # Check if missing in main
                main_file_path = self.repo_root / file_path
                if not main_file_path.exists():
                    analysis["missing_in_main"].append(file_path)
                    analysis["priority_files"].append({
                        "path": file_path,
                        "reason": "Not in main",
                        "capabilities": file_analysis["capabilities"],
                        "value": file_analysis["value_score"]
                    })
                else:
                    # Compare with main version
                    main_content = self.get_file_content(main_file_path)
                    if main_content and self.is_significantly_different(file_content, main_content):
                        analysis["enhancements"].append({
                            "path": file_path,
                            "reason": "Enhanced version",
                            "improvements": self.identify_improvements(file_content, main_content)
                        })

        except subprocess.TimeoutExpired:
            print(f"[WARN] Timeout analyzing {branch_name}")
        except Exception as e:
            print(f"[WARN] Error analyzing {branch_name}: {e}")

        return analysis

    def get_file_from_branch(self, branch_name, file_path):
        """Get file content from specific branch"""
        try:
            result = subprocess.run(
                ["git", "show", f"origin/{branch_name}:{file_path}"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10,
                errors='ignore'
            )

            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass

        return None

    def get_file_content(self, file_path):
        """Read file content safely"""
        try:
            return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None

    def analyze_file_deeply(self, file_path, content):
        """Deep analysis of file capabilities"""
        analysis = {
            "path": file_path,
            "capabilities": [],
            "features": [],
            "value_score": 0,
            "complexity": 0,
            "dependencies": []
        }

        if not content:
            return analysis

        # Count lines for complexity
        lines = content.split('\n')
        analysis["complexity"] = len(lines)

        # Analyze capabilities
        capabilities_found = []

        # Autonomous systems
        if re.search(r'(autonomous|auto_)', content, re.I):
            capabilities_found.append("autonomous")
            analysis["value_score"] += 20

        # Intelligence systems
        if re.search(r'(intelligence|smart|learn)', content, re.I):
            capabilities_found.append("intelligence")
            analysis["value_score"] += 15

        # Orchestration
        if re.search(r'(orchestrat|coordinat|manage)', content, re.I):
            capabilities_found.append("orchestration")
            analysis["value_score"] += 15

        # Monitoring
        if re.search(r'(monitor|watch|observe|track)', content, re.I):
            capabilities_found.append("monitoring")
            analysis["value_score"] += 10

        # API/Integration
        if re.search(r'(@app\.route|@router\.|FastAPI|endpoint)', content):
            capabilities_found.append("api")
            analysis["value_score"] += 12

        # Async/Performance
        if 'async def' in content:
            capabilities_found.append("async")
            analysis["value_score"] += 8

        # WebSocket
        if re.search(r'(websocket|ws://)', content, re.I):
            capabilities_found.append("websocket")
            analysis["value_score"] += 10

        # Caching
        if re.search(r'(cache|memoize)', content, re.I):
            capabilities_found.append("caching")
            analysis["value_score"] += 5

        # Database/Persistence
        if re.search(r'(database|db\.|persist|storage)', content, re.I):
            capabilities_found.append("persistence")
            analysis["value_score"] += 8

        # Testing
        if re.search(r'(test|assert|mock)', content, re.I):
            capabilities_found.append("testing")
            analysis["value_score"] += 5

        analysis["capabilities"] = capabilities_found

        # Extract class/function names
        classes = re.findall(r'class\s+(\w+)', content)
        functions = re.findall(r'def\s+(\w+)', content)

        if classes:
            analysis["features"].extend(classes[:5])  # Top 5 classes
        if functions:
            analysis["features"].extend(functions[:5])  # Top 5 functions

        return analysis

    def file_satisfies_need(self, file_analysis, need_item):
        """Check if file satisfies a specific need"""
        need_keywords = need_item.lower().split('_')

        # Check in capabilities
        for cap in file_analysis["capabilities"]:
            if any(keyword in cap for keyword in need_keywords):
                return True

        # Check in features
        for feature in file_analysis["features"]:
            if any(keyword in feature.lower() for keyword in need_keywords):
                return True

        # Check in path
        if any(keyword in file_analysis["path"].lower() for keyword in need_keywords):
            return True

        return False

    def is_significantly_different(self, content1, content2):
        """Check if two file contents are significantly different"""
        if not content1 or not content2:
            return True

        # Simple comparison - count of significant differences
        lines1 = set(content1.split('\n'))
        lines2 = set(content2.split('\n'))

        diff_count = len(lines1.symmetric_difference(lines2))
        total_lines = max(len(lines1), len(lines2))

        # Consider significant if >10% different
        return (diff_count / total_lines) > 0.1 if total_lines > 0 else False

    def identify_improvements(self, new_content, old_content):
        """Identify what improvements the new version has"""
        improvements = []

        # Check for new async functions
        new_async = len(re.findall(r'async def', new_content))
        old_async = len(re.findall(r'async def', old_content))
        if new_async > old_async:
            improvements.append(
                f"Added {new_async - old_async} async functions")

        # Check for new classes
        new_classes = len(re.findall(r'class\s+\w+', new_content))
        old_classes = len(re.findall(r'class\s+\w+', old_content))
        if new_classes > old_classes:
            improvements.append(f"Added {new_classes - old_classes} classes")

        # Check for error handling
        new_try = len(re.findall(r'try:', new_content))
        old_try = len(re.findall(r'try:', old_content))
        if new_try > old_try:
            improvements.append("Enhanced error handling")

        # Check for logging
        new_log = len(re.findall(r'(logger\.|logging\.)', new_content))
        old_log = len(re.findall(r'(logger\.|logging\.)', old_content))
        if new_log > old_log:
            improvements.append("Improved logging")

        # Check for comments/docs
        new_docs = len(re.findall(r'("""|\'\'\')', new_content))
        old_docs = len(re.findall(r'("""|\'\'\')', old_content))
        if new_docs > old_docs:
            improvements.append("Better documentation")

        return improvements if improvements else ["General improvements"]

    def synthesize_aurora_needs(self, all_analyses):
        """Synthesize what Aurora actually needs from all branches"""

        needs_matrix = defaultdict(list)

        # Categorize findings by need
        for analysis in all_analyses:
            for need_item, files in analysis["systems_offered"].items():
                for file_path in files:
                    needs_matrix[need_item].append({
                        "branch": analysis["branch"],
                        "file": file_path
                    })

        # Prioritize needs
        prioritized_needs = []

        for need_category, need_items in self.aurora_needs.items():
            for need_item in need_items:
                if need_item in needs_matrix:
                    sources = needs_matrix[need_item]

                    # Check if already have it in main
                    has_in_main = self.check_if_have_in_main(need_item)

                    priority = "HIGH" if not has_in_main else "MEDIUM"

                    prioritized_needs.append({
                        "need": need_item,
                        "category": need_category,
                        "priority": priority,
                        "status": "MISSING" if not has_in_main else "CAN_BE_ENHANCED",
                        "available_in": len(sources),
                        "sources": sources[:3],  # Top 3 sources
                        "recommendation": self.generate_recommendation(need_item, sources, has_in_main)
                    })

        # Sort by priority
        prioritized_needs.sort(key=lambda x: (
            0 if x["priority"] == "HIGH" else 1,
            -x["available_in"]
        ))

        return prioritized_needs

    def check_if_have_in_main(self, need_item):
        """Check if we already have this capability in main"""
        keywords = need_item.lower().split('_')

        # Check in current systems
        for system in self.current_capabilities["systems"]:
            if any(keyword in system for keyword in keywords):
                return True

        # Check in files
        for file_name in self.current_capabilities["files"]:
            if any(keyword in file_name.lower() for keyword in keywords):
                return True

        return False

    def generate_recommendation(self, need_item, sources, has_in_main):
        """Generate specific recommendation for a need"""
        if not has_in_main:
            # Pick best source
            best_source = sources[0]
            return {
                "action": "MERGE",
                "from_branch": best_source["branch"],
                "file": best_source["file"],
                "reason": f"Aurora needs {need_item} capability - not present in main"
            }
        else:
            # Enhancement recommendation
            return {
                "action": "CONSIDER_ENHANCEMENT",
                "from_branch": sources[0]["branch"],
                "file": sources[0]["file"],
                "reason": f"Aurora has basic {need_item} - this version may have enhancements"
            }

    def generate_comprehensive_report(self):
        """Generate Aurora's comprehensive needs report"""
        print("\n" + "="*80)
        print("[STAR] AURORA COMPREHENSIVE BRANCH ANALYSIS")
        print("="*80)

        # Get all branches
        branches = self.get_all_branches()
        print(f"\n[DATA] Analyzing {len(branches)} branches...")

        # Analyze each branch deeply
        all_analyses = []
        for branch in branches:
            if branch == self.analysis_results["current_branch"]:
                continue

            analysis = self.deep_analyze_branch(branch)
            if analysis["integration_value"] > 0:
                all_analyses.append(analysis)

        print(
            f"\n[OK] Found {len(all_analyses)} branches with valuable Aurora implementations")

        # Synthesize Aurora's needs
        print("\n[BRAIN] Synthesizing Aurora's needs...")
        prioritized_needs = self.synthesize_aurora_needs(all_analyses)

        self.analysis_results["critical_needs"] = prioritized_needs
        self.analysis_results["branches_analyzed"] = all_analyses

        # Generate statistics
        stats = {
            "total_branches_analyzed": len(all_analyses),
            "total_needs_identified": len(prioritized_needs),
            "high_priority_needs": len([n for n in prioritized_needs if n["priority"] == "HIGH"]),
            "missing_capabilities": len([n for n in prioritized_needs if n["status"] == "MISSING"]),
            "enhancement_opportunities": len([n for n in prioritized_needs if n["status"] == "CAN_BE_ENHANCED"])
        }

        self.analysis_results["statistics"] = stats

        # Save results
        output_file = self.repo_root / "AURORA_COMPREHENSIVE_NEEDS_REPORT.json"
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"\n[EMOJI] Saved comprehensive analysis to: {output_file}")

        # Generate human-readable report
        self.generate_readable_report()

        return self.analysis_results

    def generate_readable_report(self):
        """Generate human-readable markdown report"""
        report_path = self.repo_root / "AURORA_NEEDS_REPORT.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# [STAR] Aurora's Comprehensive Needs Report\n\n")
            f.write(
                f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Executive Summary
            f.write("## [DATA] Executive Summary\n\n")
            stats = self.analysis_results["statistics"]
            f.write(
                f"- **Branches Analyzed:** {stats['total_branches_analyzed']}\n")
            f.write(
                f"- **Needs Identified:** {stats['total_needs_identified']}\n")
            f.write(f"- **High Priority:** {stats['high_priority_needs']}\n")
            f.write(
                f"- **Missing Capabilities:** {stats['missing_capabilities']}\n")
            f.write(
                f"- **Enhancement Opportunities:** {stats['enhancement_opportunities']}\n\n")

            # What Aurora Currently Has
            f.write("## [EMOJI] Current Capabilities in Main\n\n")
            f.write(
                f"**Files:** {len(self.current_capabilities['files'])}\n\n")
            f.write(
                f"**Systems:** {', '.join(sorted(self.current_capabilities['systems']))}\n\n")
            f.write(
                f"**Features:** {', '.join(sorted(self.current_capabilities['features']))}\n\n")

            # Critical Needs
            f.write("## [EMOJI] Critical Needs (HIGH PRIORITY)\n\n")
            high_priority = [
                n for n in self.analysis_results["critical_needs"] if n["priority"] == "HIGH"]

            if high_priority:
                for i, need in enumerate(high_priority[:10], 1):
                    f.write(
                        f"### {i}. {need['need'].replace('_', ' ').title()}\n\n")
                    f.write(
                        f"**Category:** {need['category'].replace('_', ' ').title()}\n\n")
                    f.write(f"**Status:** {need['status']}\n\n")
                    f.write(
                        f"**Available in {need['available_in']} branches**\n\n")

                    f.write("**Recommendation:**\n")
                    rec = need['recommendation']
                    f.write(f"- **Action:** {rec['action']}\n")
                    f.write(f"- **From:** `{rec['from_branch']}`\n")
                    f.write(f"- **File:** `{rec['file']}`\n")
                    f.write(f"- **Reason:** {rec['reason']}\n\n")
            else:
                f.write(
                    "*No critical needs identified - Aurora has strong base capabilities!*\n\n")

            # Enhancement Opportunities
            f.write("## [IDEA] Enhancement Opportunities\n\n")
            enhancements = [
                n for n in self.analysis_results["critical_needs"] if n["priority"] == "MEDIUM"]

            if enhancements:
                for need in enhancements[:10]:
                    f.write(
                        f"- **{need['need'].replace('_', ' ').title()}**: ")
                    f.write(f"Available in {need['available_in']} branches ")
                    f.write(f"(check `{need['sources'][0]['branch']}`)\n")

            # Top Branches to Consider
            f.write("\n## [EMOJI] Top Branches to Consider\n\n")

            # Sort branches by integration value
            top_branches = sorted(
                self.analysis_results["branches_analyzed"],
                key=lambda x: x["integration_value"],
                reverse=True
            )[:5]

            for i, branch_analysis in enumerate(top_branches, 1):
                f.write(f"### {i}. {branch_analysis['branch']}\n\n")
                f.write(
                    f"**Integration Value:** {branch_analysis['integration_value']}\n\n")

                if branch_analysis["systems_offered"]:
                    f.write("**Systems Offered:**\n")
                    for system, files in list(branch_analysis["systems_offered"].items())[:5]:
                        f.write(
                            f"- {system.replace('_', ' ').title()}: {len(files)} files\n")
                    f.write("\n")

                if branch_analysis["missing_in_main"]:
                    f.write(
                        f"**Unique Files:** {len(branch_analysis['missing_in_main'])}\n\n")

            # Implementation Roadmap
            f.write("## [EMOJI]️ Recommended Implementation Roadmap\n\n")

            f.write("### Phase 1: Critical Missing Capabilities\n")
            phase1 = [n for n in high_priority if n["status"] == "MISSING"][:5]
            for i, need in enumerate(phase1, 1):
                rec = need['recommendation']
                f.write(
                    f"{i}. Merge `{rec['file']}` from `{rec['from_branch']}`\n")

            f.write("\n### Phase 2: Enhanced Versions\n")
            phase2 = [n for n in high_priority if n["status"]
                      == "CAN_BE_ENHANCED"][:5]
            for i, need in enumerate(phase2, 1):
                rec = need['recommendation']
                f.write(
                    f"{i}. Review `{rec['file']}` from `{rec['from_branch']}` for enhancements\n")

            f.write("\n### Phase 3: Feature Additions\n")
            f.write("1. Review enhancement opportunities\n")
            f.write("2. Test integrations\n")
            f.write("3. Merge beneficial additions\n")

            f.write("\n---\n\n")
            f.write(
                "*This report was generated by Aurora's Comprehensive Branch Analyzer*\n")

        print(f"[EMOJI] Saved readable report to: {report_path}")


def main():
    analyzer = AuroraComprehensiveBranchAnalyzer()
    results = analyzer.generate_comprehensive_report()

    print("\n" + "="*80)
    print("[SPARKLE] ANALYSIS COMPLETE")
    print("="*80)
    print(f"\n[DATA] Statistics:")
    print(
        f"   - Branches analyzed: {results['statistics']['total_branches_analyzed']}")
    print(
        f"   - Needs identified: {results['statistics']['total_needs_identified']}")
    print(
        f"   - High priority: {results['statistics']['high_priority_needs']}")
    print(
        f"   - Missing capabilities: {results['statistics']['missing_capabilities']}")
    print("\n[EMOJI] Check AURORA_NEEDS_REPORT.md for detailed recommendations")
    print("[EMOJI] Check AURORA_COMPREHENSIVE_NEEDS_REPORT.json for full data")


if __name__ == "__main__":
    main()
