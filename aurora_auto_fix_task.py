"""
Aurora Auto-Fix Task
Have Aurora fix the issues she detected
"""

import json
from pathlib import Path

# Import Aurora's auto-fix system
try:
    from aurora_nexus_v3.core.advanced_auto_fix import AdvancedAutoFix
    from aurora_nexus_v3.core.advanced_issue_analyzer import AnalysisDepth
    from aurora_nexus_v3.workers.issue_detector import DetectedIssue, IssueDetector, IssueSeverity

    AURORA_AVAILABLE = True
except ImportError as e:
    print(f"[ERROR] Aurora systems not available: {e}")
    AURORA_AVAILABLE = False


class AuroraAutoFixer:
    """Have Aurora fix the issues she detected"""

    def __init__(self):
        self.fixes_applied = []
        self.errors_encountered = []

    def fix_creative_solver(self):
        """Fix the combined_score issue in creative_problem_solver.py"""
        try:
            file_path = Path("aurora_nexus_v3/core/creative_problem_solver.py")
            content = file_path.read_text()

            # Find Solution creation without combined_score
            if "combined_score=" not in content or "solution = Solution(" in content:
                # Calculate combined_score from novelty and feasibility
                old_pattern = """            solution = Solution(
                solution_id="",
                description=variation,
                technique=CreativityTechnique.DIVERGENT_THINKING,
                novelty_score=0.7 + random.uniform(0, 0.2),
                feasibility_score=0.6 + random.uniform(0, 0.2),
            )"""

                new_pattern = """            novelty = 0.7 + random.uniform(0, 0.2)
            feasibility = 0.6 + random.uniform(0, 0.2)
            solution = Solution(
                solution_id="",
                description=variation,
                technique=CreativityTechnique.DIVERGENT_THINKING,
                novelty_score=novelty,
                feasibility_score=feasibility,
                combined_score=(novelty + feasibility) / 2.0,
            )"""

                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    file_path.write_text(content)
                    self.fixes_applied.append(
                        {
                            "file": str(file_path),
                            "issue": "Missing combined_score in Solution creation",
                            "fix": "Added combined_score calculation",
                        }
                    )
                    print(f"[FIX] Fixed combined_score in {file_path}")
                    return True

            # Check all Solution creations
            lines = content.split("\n")
            fixed = False
            for i, line in enumerate(lines):
                if "solution = Solution(" in line and i + 5 < len(lines):
                    # Check next 5 lines for combined_score
                    next_lines = "\n".join(lines[i : i + 6])
                    if "combined_score" not in next_lines:
                        # Find where this Solution block ends
                        for j in range(i, min(i + 10, len(lines))):
                            if lines[j].strip() == ")" and j > i:
                                # Insert combined_score before closing paren
                                novelty_line = None
                                feasibility_line = None
                                for k in range(i, j):
                                    if "novelty_score=" in lines[k]:
                                        novelty_line = k
                                    if "feasibility_score=" in lines[k]:
                                        feasibility_line = k

                                if novelty_line and feasibility_line:
                                    # Extract values and add combined_score
                                    novelty_val = (
                                        lines[novelty_line].split("=")[1].strip().rstrip(",")
                                    )
                                    feasibility_val = (
                                        lines[feasibility_line].split("=")[1].strip().rstrip(",")
                                    )

                                    # Insert combined_score line before closing paren
                                    indent = len(lines[j]) - len(lines[j].lstrip())
                                    combined_line = (
                                        " " * indent
                                        + f"combined_score=({novelty_val} + {feasibility_val}) / 2.0,\n"
                                    )
                                    lines.insert(j, combined_line)
                                    fixed = True
                                    break
                        if fixed:
                            break

            if fixed:
                file_path.write_text("\n".join(lines))
                self.fixes_applied.append(
                    {
                        "file": str(file_path),
                        "issue": "Missing combined_score in Solution creation",
                        "fix": "Added combined_score calculation to all Solution instances",
                    }
                )
                print(f"[FIX] Fixed combined_score in {file_path}")
                return True

        except Exception as e:
            self.errors_encountered.append({"file": "creative_problem_solver.py", "error": str(e)})
            print(f"[ERROR] Failed to fix creative_solver: {e}")
            return False

        return False

    def fix_analysis_depth_imports(self):
        """Fix AnalysisDepth import issues"""
        files_to_fix = [
            "aurora_nexus_v3/autofix.py",
            "aurora_nexus_v3/core/advanced_integration.py",
            "aurora_nexus_v3/core/self_improvement_engine.py",
            "aurora_nexus_v3/autonomy/prod_autonomy.py",
            "aurora_nexus_v3/autonomy/prod_autonomy_nontemplated.py",
            "aurora_nexus_v3/autonomy/sandbox_runner.py",
            "aurora_nexus_v3/core/aurora_brain_bridge.py",
            "aurora_nexus_v3/core/config.py",
            "aurora_nexus_v3/core/nexus_bridge.py",
        ]

        fixed_count = 0

        for file_path_str in files_to_fix:
            try:
                file_path = Path(file_path_str)
                if not file_path.exists():
                    continue

                content = file_path.read_text()

                # Check if file uses AnalysisDepth but doesn't import it
                if (
                    "AnalysisDepth" in content
                    and "from .advanced_issue_analyzer import" not in content
                    and "from ..core.advanced_issue_analyzer import" not in content
                    and "from aurora_nexus_v3.core.advanced_issue_analyzer import" not in content
                ):
                    # Determine import path based on file location
                    if "core/" in file_path_str:
                        import_line = "from .advanced_issue_analyzer import AnalysisDepth"
                    elif "workers/" in file_path_str or "autonomy/" in file_path_str:
                        import_line = "from ..core.advanced_issue_analyzer import AnalysisDepth"
                    else:
                        import_line = (
                            "from aurora_nexus_v3.core.advanced_issue_analyzer import AnalysisDepth"
                        )

                    # Find a good place to insert the import (after other imports)
                    lines = content.split("\n")
                    insert_pos = None

                    # Look for existing imports from advanced_issue_analyzer or similar
                    for i, line in enumerate(lines):
                        if (
                            "from .advanced_issue_analyzer" in line
                            or "from ..core.advanced_issue_analyzer" in line
                        ):
                            # Already has import, skip
                            insert_pos = None
                            break
                        if "from ." in line or "from .." in line or "import " in line:
                            # Found import section, insert after this
                            insert_pos = i + 1

                    if insert_pos is not None:
                        # Check if import_line already exists
                        if import_line not in content:
                            lines.insert(insert_pos, import_line)
                            content = "\n".join(lines)
                            file_path.write_text(content)
                            fixed_count += 1
                            self.fixes_applied.append(
                                {
                                    "file": file_path_str,
                                    "issue": "Missing AnalysisDepth import",
                                    "fix": f"Added {import_line}",
                                }
                            )
                            print(f"[FIX] Added AnalysisDepth import to {file_path_str}")

            except Exception as e:
                self.errors_encountered.append({"file": file_path_str, "error": str(e)})
                print(f"[ERROR] Failed to fix {file_path_str}: {e}")

        return fixed_count

    def verify_fixes(self):
        """Verify all fixes work without breaking"""
        print("\n[VERIFY] Verifying fixes...")

        # Try importing fixed modules
        test_imports = [
            "aurora_nexus_v3.core.creative_problem_solver",
            "aurora_nexus_v3.core.advanced_issue_analyzer",
            "aurora_nexus_v3.workers.issue_detector",
        ]

        success_count = 0
        for module_name in test_imports:
            try:
                __import__(module_name)
                print(f"[VERIFY] [OK] {module_name} imports successfully")
                success_count += 1
            except Exception as e:
                print(f"[VERIFY] [FAIL] {module_name} failed: {e}")
                self.errors_encountered.append(
                    {"file": module_name, "error": f"Import failed: {e}"}
                )

        # Test creative solver
        try:
            from aurora_nexus_v3.core.creative_problem_solver import CreativeProblemSolver

            solver = CreativeProblemSolver()
            solutions = solver.solve_creatively("test problem", constraints=[])
            if solutions:
                print(f"[VERIFY] [OK] Creative solver works - generated {len(solutions)} solutions")
                success_count += 1
            else:
                print("[VERIFY] [WARN] Creative solver works but returned no solutions")
        except Exception as e:
            print(f"[VERIFY] [FAIL] Creative solver failed: {e}")
            self.errors_encountered.append(
                {"file": "creative_problem_solver", "error": f"Test failed: {e}"}
            )

        return success_count

    def generate_report(self):
        """Generate fix report"""
        return {
            "fixes_applied": self.fixes_applied,
            "errors_encountered": self.errors_encountered,
            "total_fixes": len(self.fixes_applied),
            "total_errors": len(self.errors_encountered),
            "success": len(self.errors_encountered) == 0,
        }


def main():
    """Main function"""
    print("=" * 80)
    print("AURORA AUTO-FIX TASK")
    print("=" * 80)
    print()

    if not AURORA_AVAILABLE:
        print("[ERROR] Aurora systems not available")
        return

    fixer = AuroraAutoFixer()

    # Fix 1: Creative solver combined_score
    print("[FIX] Fixing creative solver combined_score issue...")
    fixer.fix_creative_solver()

    # Fix 2: AnalysisDepth imports
    print("\n[FIX] Fixing AnalysisDepth import issues...")
    fixed_count = fixer.fix_analysis_depth_imports()
    print(f"[FIX] Fixed {fixed_count} files with AnalysisDepth import issues")

    # Verify fixes
    print("\n[VERIFY] Verifying all fixes...")
    success_count = fixer.verify_fixes()

    # Generate report
    report = fixer.generate_report()

    print("\n" + "=" * 80)
    print("AURORA AUTO-FIX REPORT")
    print("=" * 80)
    print(f"Fixes Applied: {report['total_fixes']}")
    print(f"Errors: {report['total_errors']}")
    print(f"Verification Success: {success_count} modules verified")
    print(f"Overall Status: {'[SUCCESS]' if report['success'] else '[PARTIAL]'}")

    if report["fixes_applied"]:
        print("\nFixes Applied:")
        for fix in report["fixes_applied"]:
            print(f"  - {fix['file']}: {fix['issue']}")

    if report["errors_encountered"]:
        print("\nErrors Encountered:")
        for error in report["errors_encountered"]:
            print(f"  - {error['file']}: {error['error']}")

    # Save report
    report_file = Path("aurora_auto_fix_report.json")
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\nFull report saved to: {report_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
