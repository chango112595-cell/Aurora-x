"""
Aurora System Integration Analysis
Analyze where each dormant capability should be integrated
Then automatically integrate them into aurora_core.py
"""

from aurora_core import AuroraCoreIntelligence
import sys
import os
from pathlib import Path
import json
import importlib.util

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class AuroraIntegrationAnalyzer:
    def __init__(self, aurora_core: AuroraCoreIntelligence):
        self.aurora = aurora_core
        self.project_root = aurora_core.project_root
        self.tools_dir = self.project_root / "tools"
        self.integration_plan = {}

    def analyze_module(self, module_path: Path) -> dict:
        """Analyze a single module to understand its purpose and integration point"""
        try:
            content = module_path.read_text(encoding='utf-8', errors='ignore')

            analysis = {
                "name": module_path.stem,
                "path": str(module_path.relative_to(self.project_root)),
                "size": len(content),
                "lines": len(content.split('\n')),
                "has_class": "class " in content,
                "has_main": "if __name__" in content,
                "classes": [],
                "functions": [],
                "integration_point": "unknown",
                "purpose": "unknown",
                "priority": "low"
            }

            # Extract classes
            for line in content.split('\n'):
                if line.strip().startswith('class '):
                    class_name = line.split('class ')[1].split(
                        '(')[0].split(':')[0].strip()
                    analysis["classes"].append(class_name)

            # Extract top-level functions
            for line in content.split('\n'):
                if line.startswith('def ') and not line.startswith('    '):
                    func_name = line.split('def ')[1].split('(')[0].strip()
                    analysis["functions"].append(func_name)

            # Determine integration point based on content analysis
            content_lower = content.lower()

            # Proactive/Daemon modules
            if any(word in content_lower for word in ['proactive', 'daemon', 'monitor', 'continuous']):
                analysis["integration_point"] = "autonomous_system"
                analysis["purpose"] = "proactive_monitoring"
                analysis["priority"] = "critical"

            # Autonomous execution modules
            elif any(word in content_lower for word in ['autonomous', 'execute', 'task']):
                analysis["integration_point"] = "autonomous_agent"
                analysis["purpose"] = "task_execution"
                analysis["priority"] = "high"

            # Intelligence/Learning modules
            elif any(word in content_lower for word in ['intelligence', 'learning', 'knowledge']):
                analysis["integration_point"] = "intelligence_manager"
                analysis["purpose"] = "intelligence_enhancement"
                analysis["priority"] = "high"

            # Testing modules
            elif any(word in content_lower for word in ['test', 'pytest', 'validation']):
                analysis["integration_point"] = "testing_system"
                analysis["purpose"] = "automated_testing"
                analysis["priority"] = "critical"

            # Git/Safety modules
            elif any(word in content_lower for word in ['git', 'commit', 'branch', 'rollback']):
                analysis["integration_point"] = "safety_system"
                analysis["purpose"] = "version_control"
                analysis["priority"] = "critical"

            # Refactoring modules
            elif any(word in content_lower for word in ['refactor', 'rename', 'extract']):
                analysis["integration_point"] = "refactoring_engine"
                analysis["purpose"] = "code_refactoring"
                analysis["priority"] = "medium"

            # Performance modules
            elif any(word in content_lower for word in ['performance', 'optimize', 'profile']):
                analysis["integration_point"] = "performance_optimizer"
                analysis["purpose"] = "performance_optimization"
                analysis["priority"] = "medium"

            # UI/Dashboard modules
            elif any(word in content_lower for word in ['dashboard', 'ui', 'interface']):
                analysis["integration_point"] = "ui_system"
                analysis["purpose"] = "user_interface"
                analysis["priority"] = "low"

            # Core enhancement modules
            elif any(word in content_lower for word in ['core', 'enhance', 'improve']):
                analysis["integration_point"] = "core_enhancement"
                analysis["purpose"] = "core_improvement"
                analysis["priority"] = "high"

            return analysis

        except Exception as e:
            return {
                "name": module_path.stem,
                "error": str(e),
                "integration_point": "error",
                "priority": "skip"
            }

    def scan_all_dormant_modules(self):
        """Scan all modules in tools/ directory"""
        print("🔍 Analyzing dormant modules in tools/...\n")

        if not self.tools_dir.exists():
            print("❌ tools/ directory not found")
            return

        tool_files = list(self.tools_dir.glob("aurora_*.py"))
        print(f"Found {len(tool_files)} tool files\n")

        # Analyze each module
        integration_categories = {}

        for tool_file in tool_files:
            analysis = self.analyze_module(tool_file)

            if analysis.get("priority") != "skip":
                integration_point = analysis["integration_point"]

                if integration_point not in integration_categories:
                    integration_categories[integration_point] = []

                integration_categories[integration_point].append(analysis)

        self.integration_plan = integration_categories
        return integration_categories

    def generate_integration_report(self) -> str:
        """Generate detailed integration plan"""
        report = []
        report.append("=" * 80)
        report.append("AURORA INTEGRATION ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        # Summary by integration point
        report.append("INTEGRATION CATEGORIES:")
        report.append("-" * 80)

        for category, modules in sorted(self.integration_plan.items()):
            count = len(modules)
            critical = len(
                [m for m in modules if m.get("priority") == "critical"])
            high = len([m for m in modules if m.get("priority") == "high"])

            report.append(f"\n{category.upper()}: {count} modules")
            report.append(f"  Critical: {critical}, High: {high}")
            report.append("")

        # Detailed breakdown
        for category, modules in sorted(self.integration_plan.items()):
            report.append("\n" + "=" * 80)
            report.append(f"CATEGORY: {category.upper()}")
            report.append("=" * 80)

            # Sort by priority
            critical_modules = [
                m for m in modules if m.get("priority") == "critical"]
            high_modules = [m for m in modules if m.get("priority") == "high"]
            medium_modules = [
                m for m in modules if m.get("priority") == "medium"]
            low_modules = [m for m in modules if m.get("priority") == "low"]

            for priority_name, priority_modules in [
                ("CRITICAL", critical_modules),
                ("HIGH", high_modules),
                ("MEDIUM", medium_modules),
                ("LOW", low_modules)
            ]:
                if priority_modules:
                    report.append(f"\n{priority_name} PRIORITY:")
                    report.append("-" * 80)

                    for module in priority_modules:
                        report.append(f"\n  • {module['name']}")
                        report.append(f"    Purpose: {module['purpose']}")
                        report.append(f"    Path: {module['path']}")
                        report.append(
                            f"    Classes: {', '.join(module.get('classes', []))[:60] or 'None'}")
                        report.append(
                            f"    Functions: {len(module.get('functions', []))} detected")
                        report.append(f"    Size: {module['lines']} lines")

        report.append("\n\n" + "=" * 80)
        report.append("INTEGRATION STRATEGY:")
        report.append("=" * 80)
        report.append("")

        strategy = {
            "autonomous_system": "Add to AuroraCoreIntelligence.__init__ as self.autonomous_system enhancement",
            "autonomous_agent": "Extend AuroraAutonomousAgent with additional capabilities",
            "intelligence_manager": "Enhance AuroraIntelligenceManager with new learning systems",
            "testing_system": "Create new self.testing_system component in AuroraCoreIntelligence",
            "safety_system": "Create new self.safety_system with git integration",
            "refactoring_engine": "Create new self.refactoring_engine component",
            "performance_optimizer": "Create new self.performance_optimizer component",
            "core_enhancement": "Integrate directly into AuroraCoreIntelligence methods",
            "ui_system": "Keep as standalone (UI is external to core)",
            "unknown": "Needs manual review"
        }

        for category, description in strategy.items():
            if category in self.integration_plan:
                count = len(self.integration_plan[category])
                report.append(f"\n{category.upper()} ({count} modules):")
                report.append(f"  Strategy: {description}")

        report.append("\n\n" + "=" * 80)
        report.append("CRITICAL INTEGRATIONS TO DO IMMEDIATELY:")
        report.append("=" * 80)

        all_critical = []
        for modules in self.integration_plan.values():
            all_critical.extend(
                [m for m in modules if m.get("priority") == "critical"])

        if all_critical:
            for i, module in enumerate(all_critical, 1):
                report.append(f"\n{i}. {module['name']}")
                report.append(
                    f"   → Integrate into: {module['integration_point']}")
                report.append(f"   → Purpose: {module['purpose']}")
        else:
            report.append("\nNo critical modules found.")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def generate_integration_code(self) -> str:
        """Generate actual Python code to integrate modules"""
        code = []
        code.append("# AUTO-GENERATED INTEGRATION CODE")
        code.append("# Add this to aurora_core.py")
        code.append("")
        code.append("# === IMPORTS ===")
        code.append("")

        # Generate imports for critical modules
        for category, modules in self.integration_plan.items():
            critical_modules = [
                m for m in modules if m.get("priority") == "critical"]

            for module in critical_modules:
                if module.get("classes"):
                    for class_name in module["classes"][:1]:  # Import first class
                        code.append(f"try:")
                        code.append(
                            f"    from tools.{module['name']} import {class_name}")
                        code.append(
                            f"    {module['name'].upper()}_AVAILABLE = True")
                        code.append(f"except ImportError:")
                        code.append(
                            f"    {module['name'].upper()}_AVAILABLE = False")
                        code.append("")

        code.append("")
        code.append("# === INTEGRATION IN __init__ ===")
        code.append("# Add these lines to AuroraCoreIntelligence.__init__")
        code.append("")

        for category, modules in self.integration_plan.items():
            critical_modules = [
                m for m in modules if m.get("priority") == "critical"]

            if critical_modules:
                code.append(f"# {category.upper()}")
                for module in critical_modules:
                    if module.get("classes"):
                        class_name = module["classes"][0]
                        var_name = f"{category}_enhanced"
                        code.append(f"if {module['name'].upper()}_AVAILABLE:")
                        code.append(f"    try:")
                        code.append(
                            f"        self.{var_name} = {class_name}()")
                        code.append(
                            f"        print(f'✅ {category}: {class_name} loaded')")
                        code.append(f"    except Exception as e:")
                        code.append(
                            f"        print(f'⚠️ {category} initialization failed: {{e}}')")
                        code.append("")

        return "\n".join(code)


def main():
    print("=" * 80)
    print("AURORA INTEGRATION ANALYSIS")
    print("Analyzing where dormant capabilities should be integrated")
    print("=" * 80)
    print()

    # Initialize Aurora
    print("Initializing Aurora...")
    aurora = AuroraCoreIntelligence()
    print("✅ Aurora initialized\n")

    # Create analyzer
    analyzer = AuroraIntegrationAnalyzer(aurora)

    # Scan modules
    integration_plan = analyzer.scan_all_dormant_modules()

    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING INTEGRATION REPORT")
    print("=" * 80)
    print()

    report = analyzer.generate_integration_report()
    print(report)

    # Save report
    report_file = Path(__file__).parent / "AURORA_INTEGRATION_PLAN.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Report saved to: {report_file}")

    # Generate integration code
    integration_code = analyzer.generate_integration_code()
    code_file = Path(__file__).parent / "aurora_integration_code.py"
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    print(f"💾 Integration code saved to: {code_file}")

    # Save JSON plan
    json_file = Path(__file__).parent / "aurora_integration_plan.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(integration_plan, f, indent=2)
    print(f"💾 JSON plan saved to: {json_file}")

    print("\n" + "=" * 80)
    print("READY TO INTEGRATE")
    print("=" * 80)
    print("\nNext step: Run integration to wire in all critical modules")


if __name__ == "__main__":
    main()
